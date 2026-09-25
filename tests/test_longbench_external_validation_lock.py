import copy
import csv
import io
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rnaobs.external_validation_lock import (  # noqa: E402
    AUDIT_COLUMNS,
    CLASSES,
    ExternalValidationLockError,
    current_release_status,
    prediction_before_scoring_transition,
    validate_audit_rows,
    validate_lock_document,
    validate_manifest,
    workflow_detection_v1,
)


class SyntheticPhenotypeTests(unittest.TestCase):
    def test_all_fixed_classes(self):
        examples = {
            "BOTH": ([1, 2], [1, 1, 1, 0]),
            "ILLUMINA_ONLY": ([1, 1], [0, 0, 0, 0]),
            "DIRECT_RNA_ONLY": ([0, 0], [1, 1, 1, 0]),
            "NEITHER": ([0, 0], [0, 0, 0, 0]),
            "INDETERMINATE": ([1, 0], [0, 0, 0, 0]),
        }
        for expected, values in examples.items():
            with self.subTest(expected=expected):
                self.assertEqual(workflow_detection_v1(*values), expected)
        self.assertEqual(tuple(examples), CLASSES)

    def test_wrong_replicate_count_blocks(self):
        with self.assertRaisesRegex(ExternalValidationLockError, "exactly 2 Illumina"):
            workflow_detection_v1([1], [1, 1, 1, 1])
        with self.assertRaisesRegex(ExternalValidationLockError, "exactly 2 Illumina"):
            workflow_detection_v1([1, 1], [1, 1, 1])

    def test_bad_value_blocks_without_imputation(self):
        for value in (-1, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ExternalValidationLockError):
                workflow_detection_v1([value, 1], [1, 1, 1, 1])


class PredictionBeforeScoringTests(unittest.TestCase):
    def test_only_locked_sequence_is_permitted(self):
        state = "PLANNING_LOCKED"
        for event, expected in (
            ("AUTHORIZE_FEATURE_ONLY_ACCESS", "FEATURE_ONLY_ACCESS_AUTHORIZED"),
            ("HASH_PREDICTIONS", "PREDICTIONS_HASHED"),
            ("AUTHORIZE_LABEL_ACCESS", "LABEL_ACCESS_AUTHORIZED"),
            ("SCORE_ONCE", "SCORED_ONCE"),
        ):
            state = prediction_before_scoring_transition(state, event)
            self.assertEqual(state, expected)

    def test_label_access_before_prediction_hash_blocks(self):
        with self.assertRaisesRegex(ExternalValidationLockError, "forbidden"):
            prediction_before_scoring_transition(
                "FEATURE_ONLY_ACCESS_AUTHORIZED", "AUTHORIZE_LABEL_ACCESS"
            )

    def test_scoring_twice_blocks(self):
        with self.assertRaises(ExternalValidationLockError):
            prediction_before_scoring_transition("SCORED_ONCE", "SCORE_ONCE")


class CandidateSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = json.loads(
            (ROOT / "configs/longbench_external_validation_lock.json").read_text()
        )
        cls.manifest = json.loads(
            (ROOT / "metadata/longbench_external_validation_manifest.json").read_text()
        )

    def test_lock_candidate_is_valid_and_not_authorized(self):
        validate_lock_document(self.lock)
        self.assertEqual(self.lock["status"], "LOCK_CANDIDATE_NOT_AUTHORIZED")
        self.assertFalse(self.lock["prohibitions"]["longbench_access_authorized"])

    def test_structure_objectives_cannot_be_enabled(self):
        changed = copy.deepcopy(self.lock)
        changed["scientific_decision"]["incremental_structure_hypothesis"] = "PURSUE"
        with self.assertRaisesRegex(ExternalValidationLockError, "must not validate Model D"):
            validate_lock_document(changed)

    def test_threshold_and_class_order_are_immutable(self):
        changed = copy.deepcopy(self.lock)
        changed["phenotype"]["threshold_tpm"] = 0.5
        with self.assertRaisesRegex(ExternalValidationLockError, "threshold"):
            validate_lock_document(changed)
        changed = copy.deepcopy(self.lock)
        changed["phenotype"]["classes"] = list(reversed(CLASSES))
        with self.assertRaisesRegex(ExternalValidationLockError, "class order"):
            validate_lock_document(changed)

    def test_validation_refit_cannot_be_enabled(self):
        changed = copy.deepcopy(self.lock)
        changed["model_policy"]["validation_refit_allowed"] = True
        with self.assertRaisesRegex(ExternalValidationLockError, "refitting"):
            validate_lock_document(changed)

    def test_frozen_development_result_cannot_change(self):
        changed = copy.deepcopy(self.lock)
        changed["frozen_development_conclusion"]["primary_delta_macro_f1"] = 0.1
        with self.assertRaisesRegex(ExternalValidationLockError, "conclusion changed"):
            validate_lock_document(changed)

    def test_human_authorization_cannot_be_claimed_by_candidate(self):
        changed = copy.deepcopy(self.lock)
        changed["release_conditions"]["human_review_complete"] = True
        with self.assertRaisesRegex(ExternalValidationLockError, "cannot claim"):
            validate_lock_document(changed)

    def test_deployment_estimator_commit_cannot_change(self):
        changed = copy.deepcopy(self.lock)
        changed["model_policy"]["deployment_estimator_commit"] = "invented"
        with self.assertRaisesRegex(ExternalValidationLockError, "commit changed"):
            validate_lock_document(changed)

    def test_manifest_records_zero_exposure_and_zero_inclusion(self):
        validate_manifest(self.manifest)
        self.assertEqual(self.manifest["included_cell_lines"], [])
        self.assertEqual(self.manifest["included_transcripts"], 0)
        self.assertFalse(self.manifest["longbench_inputs_read"])
        self.assertFalse(self.manifest["longbench_bucket_listed"])
        self.assertFalse(self.manifest["longbench_outcomes_viewed"])
        self.assertTrue(self.manifest["serialized_transport_estimator_present"])
        self.assertTrue(self.manifest["serialized_transport_estimator_committed"])

    def test_authorization_files_are_absent(self):
        self.assertFalse(
            (ROOT / "metadata/longbench_data_access_authorization.json").exists()
        )
        self.assertFalse(
            (ROOT / "metadata/longbench_scoring_authorization.json").exists()
        )

    def test_release_checker_fails_closed(self):
        status = current_release_status(ROOT)
        self.assertEqual(status["status"], "LOCKED_RELEASE_CONDITIONS_UNMET")
        self.assertFalse(status["longbench_access_authorized"])
        self.assertTrue(status["unmet_release_conditions"])
        self.assertTrue(status["compatibility_blockers_or_unknowns"])
        self.assertEqual(status["hash_errors"], [])


class CompatibilityAuditTests(unittest.TestCase):
    def test_exact_columns_and_allowed_classifications(self):
        raw = (ROOT / "metadata/longbench_compatibility_audit.tsv").read_text()
        rows = list(csv.DictReader(io.StringIO(raw), delimiter="\t"))
        validated = validate_audit_rows(rows)
        self.assertEqual(tuple(rows[0]), AUDIT_COLUMNS)
        self.assertGreaterEqual(len(validated), 18)

    def test_duplicate_item_blocks(self):
        row = dict(
            zip(AUDIT_COLUMNS, ("x", "PASS", "C_D_REQUIRED", "evidence", "effect"))
        )
        with self.assertRaisesRegex(ExternalValidationLockError, "duplicated"):
            validate_audit_rows([row, row])

    def test_invalid_classification_blocks(self):
        row = dict(
            zip(AUDIT_COLUMNS, ("x", "MAYBE", "C_D_REQUIRED", "evidence", "effect"))
        )
        with self.assertRaisesRegex(ExternalValidationLockError, "classification"):
            validate_audit_rows([row])


class NoAccessSurfaceTests(unittest.TestCase):
    def test_planning_module_has_no_network_or_data_reader_import(self):
        source = (ROOT / "src/rnaobs/external_validation_lock.py").read_text()
        for forbidden in (
            "import boto",
            "import requests",
            "import urllib",
            "subprocess",
            "pandas",
            "duckdb",
        ):
            self.assertNotIn(forbidden, source)

    def test_checker_accepts_no_input_path(self):
        source = (ROOT / "scripts/check_longbench_release.py").read_text()
        self.assertNotIn("argparse", source)
        self.assertNotIn("sys.argv", source)


if __name__ == "__main__":
    unittest.main()
