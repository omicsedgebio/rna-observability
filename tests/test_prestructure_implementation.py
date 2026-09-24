"""Synthetic-only tests for the blinded PRESTRUCTURE_IMPLEMENTATION_LOCK."""
from __future__ import annotations

import importlib.util
from contextlib import contextmanager, ExitStack
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rnaobs.model_d_locked import (
    AnalysisBlocker,
    ANNOTATION_CONTROLS,
    ANNOTATION_MATRIX_COLUMNS,
    C_ANNOTATION_FEATURES,
    C_QUALITY_FEATURES,
    CLASSES,
    D_STRUCTURE_FEATURES,
    HISTORICAL_FEATURES,
    StructureMapping,
    accuracy,
    balanced_accuracy,
    bootstrap_interval,
    central_decision,
    classify_protocol_issue,
    confusion_matrix_fixed,
    corrected_log_loss,
    fold_local_impute,
    fit_oof,
    macro_f1,
    multiclass_brier,
    paired_cluster_bootstrap,
    parse_mapping_tsv,
    parse_structure_stream,
    per_class_f1,
    permute_median_reactivity_vectors,
    permutation_row_counts,
    practical_effect_category,
    prediction_from_probabilities,
    scale_training_only,
    ProtocolClassification,
    validate_annotation_matrix,
    validate_class_a_mappings,
)

SCRIPT_SPEC = importlib.util.spec_from_file_location(
    "locked_runner", ROOT / "scripts/run_locked_model_d.py")
locked_runner = importlib.util.module_from_spec(SCRIPT_SPEC)
assert SCRIPT_SPEC.loader is not None
SCRIPT_SPEC.loader.exec_module(locked_runner)


def annotation_frame(ids=("T1", "T2")) -> pd.DataFrame:
    rows = []
    for index, stable in enumerate(ids):
        row = {column: float(index + 1) for column in ANNOTATION_CONTROLS}
        row["stable_id"] = stable
        row["unique_kmer_fraction_missing"] = 0
        row["miniquant_kvalue_missing"] = 0
        rows.append(row)
    return pd.DataFrame(rows, columns=ANNOTATION_MATRIX_COLUMNS)


def one_mapping(length=50) -> dict[str, StructureMapping]:
    return {"T1": StructureMapping("T1", "ENST1.1", "A", length)}


def structure_line(values, *, transcript="ENST1.1", assay="2.5") -> str:
    return "\t".join([transcript, str(len(values)), assay, *values]) + "\n"


class AnnotationMatrixTests(unittest.TestCase):
    def test_valid_matrix_and_exact_missingness(self):
        frame = annotation_frame()
        frame.loc[1, "unique_kmer_fraction"] = np.nan
        frame.loc[1, "unique_kmer_fraction_missing"] = 1
        self.assertEqual(validate_annotation_matrix(frame, ["T1", "T2"], expected_rows=2),
                         {"unique_kmer_fraction_missing": 1,
                          "miniquant_kvalue_missing": 0})

    def test_row_count_duplicate_and_order_rejected(self):
        frame = annotation_frame()
        with self.assertRaises(AnalysisBlocker):
            validate_annotation_matrix(frame.iloc[:1], ["T1"], expected_rows=2)
        duplicate = frame.copy(); duplicate.loc[1, "stable_id"] = "T1"
        with self.assertRaises(AnalysisBlocker):
            validate_annotation_matrix(duplicate, ["T1", "T2"], expected_rows=2)
        with self.assertRaises(AnalysisBlocker):
            validate_annotation_matrix(frame, ["T2", "T1"], expected_rows=2)

    def test_missing_unexpected_outcome_and_structure_columns_rejected(self):
        frame = annotation_frame()
        with self.assertRaises(AnalysisBlocker):
            validate_annotation_matrix(frame.drop(columns="mean_exon_length"), ["T1", "T2"], expected_rows=2)
        for column in ("extra", "label", "median_reactivity"):
            altered = frame.copy(); altered[column] = 0
            with self.assertRaises(AnalysisBlocker, msg=column):
                validate_annotation_matrix(altered, ["T1", "T2"], expected_rows=2)

    def test_indicator_mismatch_and_non_imputable_missing_rejected(self):
        frame = annotation_frame(); frame.loc[0, "miniquant_kvalue"] = np.nan
        with self.assertRaises(AnalysisBlocker):
            validate_annotation_matrix(frame, ["T1", "T2"], expected_rows=2)
        frame = annotation_frame(); frame.loc[0, "max_exon_jaccard"] = np.nan
        with self.assertRaises(AnalysisBlocker):
            validate_annotation_matrix(frame, ["T1", "T2"], expected_rows=2)


class PreprocessingTests(unittest.TestCase):
    def test_training_only_even_median_and_indicator_preserved(self):
        columns = ["unique_kmer_fraction", "unique_kmer_fraction_missing",
                   "miniquant_kvalue", "miniquant_kvalue_missing"]
        train = pd.DataFrame([[1, 0, 2, 0], [3, 0, 4, 0], [np.nan, 1, np.nan, 1]], columns=columns)
        test = pd.DataFrame([[1000, 0, 1000, 0], [np.nan, 1, np.nan, 1]], columns=columns)
        tr, te, medians = fold_local_impute(train, test, columns)
        self.assertEqual(medians, {"unique_kmer_fraction": 2.0, "miniquant_kvalue": 3.0})
        self.assertEqual(tr[2].tolist(), [2.0, 1.0, 3.0, 1.0])
        self.assertEqual(te[1].tolist(), [2.0, 1.0, 3.0, 1.0])

    def test_empty_training_basis_blocks(self):
        columns = ["unique_kmer_fraction"]
        with self.assertRaises(AnalysisBlocker):
            fold_local_impute(pd.DataFrame([[np.nan]], columns=columns),
                              pd.DataFrame([[1]], columns=columns), columns)

    def test_scaler_is_training_only(self):
        train = np.asarray([[0.0], [2.0]])
        test = np.asarray([[100.0]])
        scaled_train, scaled_test, scaler = scale_training_only(train, test)
        self.assertEqual(scaler.mean_[0], 1.0)
        self.assertEqual(scaler.var_[0], 1.0)
        self.assertEqual(scaled_train[:, 0].tolist(), [-1.0, 1.0])
        self.assertEqual(scaled_test[0, 0], 99.0)

    def test_exact_feature_order(self):
        self.assertEqual(C_ANNOTATION_FEATURES, HISTORICAL_FEATURES + ANNOTATION_CONTROLS)
        self.assertEqual(C_QUALITY_FEATURES, C_ANNOTATION_FEATURES + ("callable_fraction",))
        self.assertEqual(D_STRUCTURE_FEATURES, C_QUALITY_FEATURES + ("median_reactivity",))

    def test_synthetic_oof_fit_uses_locked_vector(self):
        rows = []
        for fold in range(5):
            for class_index, label in enumerate(CLASSES):
                for replicate in range(2):
                    row = {feature: float(class_index + replicate / 10 + fold / 100)
                           for feature in C_ANNOTATION_FEATURES}
                    row.update(label=label, fold=fold)
                    row["unique_kmer_fraction_missing"] = 0.0
                    row["miniquant_kvalue_missing"] = 0.0
                    rows.append(row)
        frame = pd.DataFrame(rows)
        pred, probability, fits = fit_oof(frame, C_ANNOTATION_FEATURES)
        self.assertEqual(len(pred), len(frame))
        self.assertEqual(probability.shape, (len(frame), 5))
        np.testing.assert_allclose(probability.sum(axis=1), 1.0, rtol=0, atol=1e-12)
        self.assertEqual([fit.fold for fit in fits], [0, 1, 2, 3, 4])


class StructureParserTests(unittest.TestCase):
    def test_valid_null_odd_and_even_medians(self):
        even = [str(x) for x in range(50)]
        parsed = parse_structure_stream(StringIO(structure_line(even)), one_mapping(50))
        self.assertEqual(parsed.loc[0, "median_reactivity"], 24.5)
        self.assertEqual(parsed.loc[0, "callable_fraction"], 1.0)
        odd = [str(x) for x in range(51)] + ["NULL"]
        parsed = parse_structure_stream(StringIO(structure_line(odd)), one_mapping(52))
        self.assertEqual(parsed.loc[0, "median_reactivity"], 25.0)
        self.assertEqual(parsed.loc[0, "callable_positions"], 51)
        self.assertNotIn("assay_rpkm", parsed.columns)

    def test_case_sensitive_null_and_nonfinite_rejected(self):
        for token in ("null", "NaN", "inf", "-inf"):
            values = ["1"] * 49 + [token]
            with self.assertRaises(AnalysisBlocker, msg=token):
                parse_structure_stream(StringIO(structure_line(values)), one_mapping(50))

    def test_position_count_length_mismatch_and_duplicate_rejected(self):
        values = ["1"] * 50
        bad_count = "\t".join(["ENST1.1", "51", "2", *values]) + "\n"
        with self.assertRaises(AnalysisBlocker):
            parse_structure_stream(StringIO(bad_count), one_mapping(51))
        with self.assertRaises(AnalysisBlocker):
            parse_structure_stream(StringIO(structure_line(values)), one_mapping(51))
        with self.assertRaises(AnalysisBlocker):
            parse_structure_stream(StringIO(structure_line(values) * 2), one_mapping(50))

    def test_callable_count_and_fraction_thresholds(self):
        with self.assertRaises(AnalysisBlocker):
            parse_structure_stream(StringIO(structure_line(["1"] * 49 + ["NULL"])), one_mapping(50))
        values = ["1"] * 50 + ["NULL"] * 51
        with self.assertRaises(AnalysisBlocker):
            parse_structure_stream(StringIO(structure_line(values)), one_mapping(101))

    def test_mapping_policy_is_class_a_one_to_one_complete(self):
        with self.assertRaises(AnalysisBlocker):
            validate_class_a_mappings([StructureMapping("T1", "S1", "B", 50)], ["T1"])
        duplicate = [StructureMapping("T1", "S1", "A", 50),
                     StructureMapping("T2", "S1", "A", 50)]
        with self.assertRaises(AnalysisBlocker):
            validate_class_a_mappings(duplicate, ["T1", "T2"])
        with self.assertRaises(AnalysisBlocker):
            validate_class_a_mappings([], ["T1"])

    def test_mapping_tsv_requires_all_class_a_evidence(self):
        columns = [
            "stable_id", "structure_transcript_id", "mapping_class", "reported_length",
            "unique_source_stable_id", "gene_equal_88_91",
            "chromosome_equal_88_91", "strand_equal_88_91",
            "exon_intervals_equal_88_91", "transcript_length_equal_88_91",
            "transcript_sequence_equal_88_91",
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapping.tsv"
            path.write_text("\t".join(columns) + "\n" +
                            "\t".join(["T1", "S1", "A", "50"] + ["true"] * 7) + "\n")
            self.assertEqual(set(parse_mapping_tsv(path, ["T1"])), {"T1"})
            path.write_text("\t".join(columns) + "\n" +
                            "\t".join(["T1", "S1", "A", "50", "false"] + ["true"] * 6) + "\n")
            with self.assertRaises(AnalysisBlocker):
                parse_mapping_tsv(path, ["T1"])


class MetricTests(unittest.TestCase):
    def test_fixed_class_metrics_and_absent_class_behavior(self):
        y = ["BOTH", "BOTH", "ILLUMINA_ONLY"]
        pred = ["BOTH", "ILLUMINA_ONLY", "ILLUMINA_ONLY"]
        scores = per_class_f1(y, pred)
        self.assertEqual(list(scores), list(CLASSES))
        self.assertAlmostEqual(scores["BOTH"], 2 / 3)
        self.assertAlmostEqual(scores["ILLUMINA_ONLY"], 2 / 3)
        self.assertEqual(scores["DIRECT_RNA_ONLY"], 0.0)
        self.assertAlmostEqual(macro_f1(y, pred), (4 / 3) / 5)
        self.assertAlmostEqual(accuracy(y, pred), 2 / 3)
        self.assertAlmostEqual(balanced_accuracy(y, pred), (0.5 + 1.0) / 5)
        matrix = confusion_matrix_fixed(y, pred)
        self.assertEqual(matrix.shape, (5, 5))
        self.assertEqual(int(matrix.sum()), 3)

    def test_named_log_loss_and_brier(self):
        probabilities = np.asarray([[0.8, 0.1, 0.05, 0.03, 0.02],
                                    [0.1, 0.7, 0.1, 0.05, 0.05]])
        y = ["BOTH", "ILLUMINA_ONLY"]
        self.assertAlmostEqual(corrected_log_loss(y, probabilities),
                               -np.mean(np.log([0.8, 0.7])))
        expected = np.mean(np.sum((probabilities - np.asarray([[1, 0, 0, 0, 0],
                                                               [0, 1, 0, 0, 0]])) ** 2, axis=1))
        self.assertAlmostEqual(multiclass_brier(y, probabilities), expected)

    def test_lexicographic_probability_tie(self):
        probabilities = np.asarray([[0.4, 0.4, 0.1, 0.05, 0.05],
                                    [0.0, 0.0, 0.5, 0.5, 0.0]])
        self.assertEqual(prediction_from_probabilities(probabilities).tolist(),
                         ["BOTH", "DIRECT_RNA_ONLY"])


class ResamplingTests(unittest.TestCase):
    def test_bootstrap_is_deterministic_paired_and_cluster_level(self):
        y = np.asarray(["BOTH", "BOTH", "ILLUMINA_ONLY", "ILLUMINA_ONLY"])
        c = np.asarray(["BOTH", "ILLUMINA_ONLY", "BOTH", "ILLUMINA_ONLY"])
        d = np.asarray(["BOTH", "BOTH", "ILLUMINA_ONLY", "ILLUMINA_ONLY"])
        clusters = np.asarray(["A", "A", "B", "B"])
        first = paired_cluster_bootstrap(y, c, d, clusters, replicates=20, seed=20260924)
        second = paired_cluster_bootstrap(y, c, d, clusters, replicates=20, seed=20260924)
        np.testing.assert_array_equal(first, second)
        zeros = paired_cluster_bootstrap(y, c, c, clusters, replicates=20, seed=20260924)
        np.testing.assert_array_equal(zeros, np.zeros(20))
        self.assertEqual(bootstrap_interval([0, 1, 2, 3]),
                         tuple(np.quantile([0, 1, 2, 3], [0.025, 0.975], method="linear")))

    def test_permutation_vector_strata_singleton_and_nonstructure_unchanged(self):
        frame = pd.DataFrame({
            "stable_id": ["A1", "A2", "B1", "B2", "C1"],
            "sequence_cluster_id": ["A", "A", "B", "B", "C"],
            "fold": [0, 0, 0, 0, 1],
            "median_reactivity": [1.0, 2.0, 10.0, 20.0, 99.0],
            "callable_fraction": [0.8, 0.9, 0.7, 0.6, 1.0],
        })
        one = permute_median_reactivity_vectors(frame, np.random.Generator(np.random.PCG64(5)))
        two = permute_median_reactivity_vectors(frame, np.random.Generator(np.random.PCG64(5)))
        pd.testing.assert_frame_equal(one, two)
        self.assertEqual(one.loc[one.sequence_cluster_id.eq("C"), "median_reactivity"].tolist(), [99.0])
        pd.testing.assert_series_equal(one["callable_fraction"], frame["callable_fraction"])
        for cluster in ("A", "B"):
            vector = one.loc[one.sequence_cluster_id.eq(cluster), "median_reactivity"].tolist()
            self.assertIn(vector, ([1.0, 2.0], [10.0, 20.0]))
        self.assertEqual(permutation_row_counts(frame), (4, 1))


class DecisionTests(unittest.TestCase):
    def decide(self, **changes):
        values = dict(validity=True, delta_macro_f1=0.02,
                      paired_bootstrap_ci_lower=0.001,
                      permutation_95th_percentile=0.0,
                      fold_deltas=[1, 1, 1, 1, -1],
                      strict_callability_delta=0.001,
                      direct_rna_only_delta_f1=0.0,
                      indeterminate_delta_f1=0.0)
        values.update(changes)
        return central_decision(**values)

    def test_practical_boundaries(self):
        self.assertEqual(practical_effect_category(-1), "NO_INCREMENT")
        self.assertEqual(practical_effect_category(0), "NO_INCREMENT")
        self.assertEqual(practical_effect_category(0.004999), "NEGLIGIBLE")
        self.assertEqual(practical_effect_category(0.005), "SMALL")
        self.assertEqual(practical_effect_category(0.020), "MEANINGFUL")

    def test_supported_partial_not_supported_and_inconclusive(self):
        self.assertEqual(self.decide().conclusion, "SUPPORTED")
        self.assertEqual(self.decide(delta_macro_f1=0.005,
                                     fold_deltas=[1, 1, 1, -1, -1]).conclusion,
                         "PARTIALLY_SUPPORTED")
        self.assertEqual(self.decide(validity=False).conclusion, "INCONCLUSIVE")
        for delta in (-0.1, 0.0, 0.004):
            self.assertEqual(self.decide(delta_macro_f1=delta,
                                         permutation_95th_percentile=-1).conclusion,
                             "NOT_SUPPORTED")

    def test_exact_failed_gate_boundaries(self):
        cases = [
            dict(paired_bootstrap_ci_lower=0.0, delta_macro_f1=0.005),
            dict(permutation_95th_percentile=0.02),
            dict(strict_callability_delta=0.0),
            dict(fold_deltas=[1, 1, -1, -1, -1]),
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                self.assertEqual(self.decide(**changes).conclusion, "NOT_SUPPORTED")

    def test_three_four_fold_and_class_instability_behavior(self):
        three = self.decide(fold_deltas=[1, 1, 1, -1, -1])
        self.assertEqual(three.conclusion, "PARTIALLY_SUPPORTED")
        four = self.decide(fold_deltas=[1, 1, 1, 1, -1])
        self.assertEqual(four.conclusion, "SUPPORTED")
        unstable = self.decide(direct_rna_only_delta_f1=-0.0200001)
        self.assertEqual(unstable.conclusion, "PARTIALLY_SUPPORTED")
        self.assertTrue(unstable.class_instability)


class GuardTests(unittest.TestCase):
    def test_attempt_guard_first_use_then_consumed_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "attempt.json"
            with mock.patch.object(locked_runner, "ATTEMPT_MARKER", marker):
                locked_runner.consume_attempt("a" * 40)
                self.assertTrue(marker.exists())
                with self.assertRaises(AnalysisBlocker):
                    locked_runner.consume_attempt("a" * 40)

    def test_current_phase_guard_not_consumed(self):
        guard = json.loads((ROOT / "metadata/model_d_attempt_guard.json").read_text())
        self.assertEqual(guard["state"], "MODEL_D_ATTEMPT_NOT_CONSUMED")
        self.assertFalse(guard["structure_test_authorized"])
        self.assertFalse((ROOT / guard["consumed_marker"]).exists())

    def test_mock_altered_frozen_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "item.txt").write_text("altered")
            manifest = {"protected_file_sha256": {"item.txt": "0" * 64}}
            with mock.patch.object(locked_runner, "ROOT", root):
                with self.assertRaises(AnalysisBlocker):
                    locked_runner.verify_frozen_files(manifest)

    def test_longbench_paths_rejected(self):
        for path in (Path("LongBench/outcome.tsv"), Path("GSE303762/data"),
                     Path("s3://longbench-data/x")):
            with self.assertRaises(AnalysisBlocker):
                locked_runner.reject_longbench_path(path)

    def test_protocol_issue_categories_are_disjoint(self):
        self.assertEqual(classify_protocol_issue(demonstrable_code_defect=True),
                         ProtocolClassification.IMPLEMENTATION_REPAIR)
        self.assertEqual(classify_protocol_issue(scientific_change_domain="feature_order"),
                         ProtocolClassification.PROTOCOL_DEVIATION)
        self.assertEqual(classify_protocol_issue(blocker=True),
                         ProtocolClassification.ANALYSIS_BLOCKER)
        with self.assertRaises(ValueError):
            classify_protocol_issue(blocker=True, demonstrable_code_defect=True)


class ExecutePreflightOrderingTests(unittest.TestCase):
    """Exercise execute() with temporary synthetic resources only."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.manifest = self.root / "metadata/implementation.json"
        self.authorization = self.root / "metadata/model_d_execution_authorization.json"
        self.marker = self.root / "metadata/model_d_attempt_consumed.json"
        self.mapping = self.root / ".cache/model_d/class_a_mapping.tsv"
        self.structure = (
            self.root / ".cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz"
        )
        self.manifest.parent.mkdir(parents=True)
        self.mapping.parent.mkdir(parents=True)
        self.structure.parent.mkdir(parents=True)
        self.manifest.write_text(json.dumps({"scientific_lock_commit": "b" * 40}))
        self.locked_inputs = tuple(pd.DataFrame() for _ in range(5))

    @contextmanager
    def execution_context(self, *, mock_authorization=True,
                          locked_input_effect=None, expected_structure_bytes=9):
        with ExitStack() as stack:
            stack.enter_context(mock.patch.multiple(
                locked_runner,
                ROOT=self.root,
                MANIFEST=self.manifest,
                AUTHORIZATION=self.authorization,
                ATTEMPT_MARKER=self.marker,
                MAPPING=self.mapping,
                STRUCTURE=self.structure,
                EXPECTED_STRUCTURE_BYTES=expected_structure_bytes,
            ))
            stack.enter_context(mock.patch.object(locked_runner, "verify_frozen_files"))
            stack.enter_context(mock.patch.object(locked_runner, "verify_environment"))
            if locked_input_effect is None:
                stack.enter_context(mock.patch.object(
                    locked_runner, "read_locked_inputs", return_value=self.locked_inputs))
            else:
                stack.enter_context(mock.patch.object(
                    locked_runner, "read_locked_inputs", side_effect=locked_input_effect))
            if mock_authorization:
                stack.enter_context(mock.patch.object(
                    locked_runner, "require_execution_authorization",
                    return_value=("a" * 40, "c" * 64)))
            yield

    def write_mapping(self):
        self.mapping.write_text("synthetic mapping metadata\n")

    def write_structure_placeholder(self, size=9):
        # Metadata-only preflight may stat this file; content is never real structure.
        self.structure.write_bytes(b"S" * size)

    def test_missing_mapping_does_not_consume_attempt(self):
        consume = mock.Mock()
        with self.execution_context(), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(AnalysisBlocker, "mapping resource is missing"):
                locked_runner.execute()
        consume.assert_not_called()

    def test_wrong_mapping_hash_does_not_consume_attempt(self):
        self.write_mapping()
        consume = mock.Mock()
        with self.execution_context(), \
                mock.patch.object(locked_runner, "sha256", return_value="d" * 64), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(AnalysisBlocker, "authorized SHA256"):
                locked_runner.execute()
        consume.assert_not_called()

    def test_missing_structure_file_does_not_consume_attempt(self):
        self.write_mapping()
        consume = mock.Mock()
        with self.execution_context(), \
                mock.patch.object(locked_runner, "sha256", return_value="c" * 64), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(AnalysisBlocker, "structure resource is missing"):
                locked_runner.execute()
        consume.assert_not_called()

    def test_wrong_structure_byte_size_does_not_consume_attempt(self):
        self.write_mapping()
        self.write_structure_placeholder(size=8)
        consume = mock.Mock()
        with self.execution_context(expected_structure_bytes=9), \
                mock.patch.object(locked_runner, "sha256", return_value="c" * 64), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(AnalysisBlocker, "byte size differs"):
                locked_runner.execute()
        consume.assert_not_called()

    def test_invalid_frozen_nonstructure_input_does_not_consume_attempt(self):
        self.write_mapping()
        self.write_structure_placeholder()
        consume = mock.Mock()
        invalid = AnalysisBlocker("synthetic frozen input invalid")
        with self.execution_context(locked_input_effect=invalid), \
                mock.patch.object(locked_runner, "sha256", return_value="c" * 64), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(AnalysisBlocker, "synthetic frozen input invalid"):
                locked_runner.execute()
        consume.assert_not_called()

    def test_absent_authorization_does_not_consume_attempt(self):
        consume = mock.Mock()
        with self.execution_context(mock_authorization=False), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(AnalysisBlocker, "authorization is absent"):
                locked_runner.execute()
        consume.assert_not_called()

    def test_invalid_authorization_does_not_consume_attempt(self):
        self.authorization.write_text(json.dumps({"structure_test_authorized": False}))
        consume = mock.Mock()
        with self.execution_context(mock_authorization=False), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(AnalysisBlocker, "not fully approved"):
                locked_runner.execute()
        consume.assert_not_called()

    def test_existing_consumed_marker_blocks_before_structure_access(self):
        self.write_mapping()
        self.write_structure_placeholder()
        self.marker.write_text("already consumed\n")
        events = []

        def synthetic_sha(path):
            events.append(("sha256", path))
            if path == self.structure:
                self.fail("structure content hash must not run with an existing marker")
            return "c" * 64

        consume = mock.Mock()
        with self.execution_context(), \
                mock.patch.object(locked_runner, "sha256", side_effect=synthetic_sha), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(AnalysisBlocker, "already consumed"):
                locked_runner.execute()
        consume.assert_not_called()
        self.assertEqual(events, [("sha256", self.mapping)])

    def test_successful_structure_blind_preflight_reaches_consumption_boundary(self):
        self.write_mapping()
        self.write_structure_placeholder()
        boundary = RuntimeError("synthetic consumption boundary")
        consume = mock.Mock(side_effect=boundary)
        with self.execution_context(), \
                mock.patch.object(locked_runner, "sha256", return_value="c" * 64), \
                mock.patch.object(locked_runner, "consume_attempt", consume):
            with self.assertRaisesRegex(RuntimeError, "synthetic consumption boundary"):
                locked_runner.execute()
        consume.assert_called_once_with("a" * 40)

    def test_attempt_consumed_immediately_before_structure_content_hash(self):
        self.write_mapping()
        self.write_structure_placeholder()
        events = []

        def synthetic_sha(path):
            events.append(("sha256", path))
            if path == self.structure:
                raise RuntimeError("synthetic first structure-byte access")
            return "c" * 64

        def synthetic_consume(commit):
            events.append(("consume", commit))

        with self.execution_context(), \
                mock.patch.object(locked_runner, "sha256", side_effect=synthetic_sha), \
                mock.patch.object(locked_runner, "consume_attempt", side_effect=synthetic_consume):
            with self.assertRaisesRegex(RuntimeError, "first structure-byte access"):
                locked_runner.execute()
        self.assertEqual(events, [
            ("sha256", self.mapping),
            ("consume", "a" * 40),
            ("sha256", self.structure),
        ])

    def test_structure_hash_failure_after_byte_access_leaves_attempt_consumed(self):
        self.write_mapping()
        self.write_structure_placeholder()
        structure_hash_calls = []

        def synthetic_sha(path):
            if path == self.mapping:
                return "c" * 64
            if path == self.structure:
                structure_hash_calls.append(path)
                return "0" * 64
            self.fail(f"unexpected synthetic SHA path: {path}")

        with self.execution_context(), \
                mock.patch.object(locked_runner, "sha256", side_effect=synthetic_sha):
            with self.assertRaisesRegex(AnalysisBlocker, "structure-resource SHA256"):
                locked_runner.execute()
        self.assertEqual(structure_hash_calls, [self.structure])
        self.assertTrue(self.marker.is_file())
        marker = json.loads(self.marker.read_text())
        self.assertEqual(marker["state"], "MODEL_D_ATTEMPT_CONSUMED_NO_AUTOMATIC_RERUN")

    def test_execute_ordering_tests_use_no_real_structure_resource(self):
        real_structure = ROOT / ".cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz"
        self.assertNotEqual(self.structure, real_structure)
        self.assertTrue(self.structure.is_relative_to(self.root))
        self.assertFalse(self.structure.exists())


if __name__ == "__main__":
    unittest.main()
