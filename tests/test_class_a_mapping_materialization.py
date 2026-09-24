"""Synthetic-only tests for structure-blind class-A mapping materialization."""
from __future__ import annotations

import csv
import importlib.util
import inspect
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rnaobs.model_d_locked import (
    AnalysisBlocker,
    CLASS_A_MAPPING_COLUMNS,
    StructureMapping,
    parse_mapping_tsv,
    parse_structure_stream,
)

SCRIPT_SPEC = importlib.util.spec_from_file_location(
    "class_a_materializer", ROOT / "scripts/materialize_class_a_mapping.py"
)
materializer = importlib.util.module_from_spec(SCRIPT_SPEC)
assert SCRIPT_SPEC.loader is not None
sys.modules[SCRIPT_SPEC.name] = materializer
SCRIPT_SPEC.loader.exec_module(materializer)


def transcript(
    identifier="ENST000001.1",
    *,
    gene="ENSG000001.1",
    chrom="1",
    strand="+",
    exons=((0, 4),),
    sequence="ACGT",
):
    return {
        "identifier": identifier,
        "gene": gene,
        "chrom": chrom,
        "strand": strand,
        "exons": exons,
        "sequence": sequence,
    }


def write_gtf(path: Path, transcripts) -> None:
    lines = []
    for item in transcripts:
        for start, end in item["exons"]:
            attributes = (
                f'gene_id "{item["gene"]}"; transcript_id "{item["identifier"]}"; '
                'transcript_biotype "protein_coding";'
            )
            lines.append(
                "\t".join([
                    item["chrom"], "synthetic", "exon", str(start + 1), str(end),
                    ".", item["strand"], ".", attributes,
                ])
            )
    path.write_text("\n".join(lines) + ("\n" if lines else ""))


def write_fasta(path: Path, transcripts) -> None:
    path.write_text("".join(
        f'>{item["identifier"]}\n{item["sequence"]}\n' for item in transcripts
    ))


def valid_row(stable: str, *, structure_id: str | None = None, length: int = 4):
    return {
        "stable_id": stable,
        "structure_transcript_id": structure_id or stable,
        "mapping_class": "A",
        "reported_length": length,
        "unique_source_stable_id": "true",
        "gene_equal_88_91": "true",
        "chromosome_equal_88_91": "true",
        "strand_equal_88_91": "true",
        "exon_intervals_equal_88_91": "true",
        "transcript_length_equal_88_91": "true",
        "transcript_sequence_equal_88_91": "true",
    }


class SyntheticReferences:
    def __init__(self, testcase: unittest.TestCase, source=None, target=None):
        self.temporary = tempfile.TemporaryDirectory()
        testcase.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.cohort = self.root / "cohort.tsv"
        self.folds = self.root / "folds.tsv"
        self.gtf88 = self.root / "ensembl88.gtf"
        self.cdna88 = self.root / "ensembl88.cdna.fa"
        self.ncrna88 = self.root / "ensembl88.ncrna.fa"
        self.gtf91 = self.root / "ensembl91.gtf"
        self.cdna91 = self.root / "ensembl91.cdna.fa"
        self.ncrna91 = self.root / "ensembl91.ncrna.fa"
        self.output = self.root / "mapping.tsv"
        self.cohort.write_text("stable_id\nENST000001\n")
        self.folds.write_text("stable_id\tfold\nENST000001\t0\n")
        self.set_references(source or [transcript()], target or [transcript()])

    def set_references(self, source, target):
        write_gtf(self.gtf88, source)
        write_fasta(self.cdna88, source)
        self.ncrna88.write_text("")
        write_gtf(self.gtf91, target)
        write_fasta(self.cdna91, target)
        self.ncrna91.write_text("")

    @property
    def inputs(self):
        return materializer.MappingInputs(
            cohort=self.cohort,
            folds=self.folds,
            ensembl88_gtf=self.gtf88,
            ensembl88_fastas=(self.cdna88, self.ncrna88),
            ensembl91_gtf=self.gtf91,
            ensembl91_fastas=(self.cdna91, self.ncrna91),
        )

    def run(self):
        return materializer.materialize(self.inputs, self.output, expected_rows=1)


class ClassAMaterializationTests(unittest.TestCase):
    def test_unique_88_and_91_mapping_succeeds(self):
        fixture = SyntheticReferences(self)
        rows, counts = fixture.run()
        self.assertEqual(counts["n_mapped"], 1)
        self.assertEqual(rows[0]["mapping_class"], "A")
        self.assertEqual(rows[0]["structure_transcript_id"], "ENST000001")
        parsed = parse_mapping_tsv(fixture.output, ["ENST000001"])
        self.assertEqual(set(parsed), {"ENST000001"})

    def test_ambiguous_ensembl88_stable_id_blocks(self):
        source = [transcript(), transcript("ENST000001.2")]
        fixture = SyntheticReferences(self, source=source)
        with self.assertRaisesRegex(AnalysisBlocker, "ambiguous Ensembl 88"):
            fixture.run()

    def test_ambiguous_ensembl91_stable_id_blocks(self):
        target = [transcript(), transcript("ENST000001.2")]
        fixture = SyntheticReferences(self, target=target)
        with self.assertRaisesRegex(AnalysisBlocker, "ambiguous Ensembl 91"):
            fixture.run()

    def test_missing_ensembl88_transcript_blocks(self):
        fixture = SyntheticReferences(self)
        fixture.set_references([], [transcript()])
        with self.assertRaisesRegex(AnalysisBlocker, "missing Ensembl 88"):
            fixture.run()

    def test_missing_ensembl91_transcript_blocks(self):
        fixture = SyntheticReferences(self)
        fixture.set_references([transcript()], [])
        with self.assertRaisesRegex(AnalysisBlocker, "missing Ensembl 91"):
            fixture.run()

    def test_gene_inequality_blocks(self):
        fixture = SyntheticReferences(self, target=[transcript(gene="ENSG000002.1")])
        with self.assertRaisesRegex(AnalysisBlocker, "gene inequality"):
            fixture.run()

    def test_chromosome_inequality_blocks(self):
        fixture = SyntheticReferences(self, target=[transcript(chrom="2")])
        with self.assertRaisesRegex(AnalysisBlocker, "chromosome inequality"):
            fixture.run()

    def test_strand_inequality_blocks(self):
        fixture = SyntheticReferences(self, target=[transcript(strand="-")])
        with self.assertRaisesRegex(AnalysisBlocker, "strand inequality"):
            fixture.run()

    def test_exon_interval_inequality_blocks(self):
        fixture = SyntheticReferences(self, target=[transcript(exons=((1, 5),))])
        with self.assertRaisesRegex(AnalysisBlocker, "exon interval inequality"):
            fixture.run()

    def test_transcript_length_inequality_blocks(self):
        target = transcript(exons=((0, 5),), sequence="ACGTA")
        fixture = SyntheticReferences(self, target=[target])
        with self.assertRaisesRegex(AnalysisBlocker, "transcript length inequality"):
            fixture.run()

    def test_transcript_sequence_inequality_blocks(self):
        fixture = SyntheticReferences(self, target=[transcript(sequence="TGCA")])
        with self.assertRaisesRegex(AnalysisBlocker, "transcript sequence inequality"):
            fixture.run()

    def test_full_versioned_id_difference_is_not_class_a(self):
        fixture = SyntheticReferences(self, target=[transcript("ENST000001.2")])
        with self.assertRaisesRegex(AnalysisBlocker, "identical versioned transcript IDs"):
            fixture.run()

    def test_exact_15999_row_coverage_validation(self):
        frozen = [f"ENST{index:011d}" for index in range(15_999)]
        rows = [valid_row(stable) for stable in frozen]
        counts = materializer.validate_mapping_rows(
            rows, frozen, expected_rows=15_999
        )
        self.assertEqual(counts, {
            "n_frozen_transcripts": 15_999,
            "n_mapped": 15_999,
            "n_missing": 0,
            "n_extra": 0,
            "n_duplicate_stable_id": 0,
            "n_duplicate_structure_transcript_id": 0,
        })
        with self.assertRaises(AnalysisBlocker):
            materializer.validate_mapping_rows(rows[:-1], frozen, expected_rows=15_999)

    def test_duplicate_stable_id_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cohort.tsv"
            path.write_text("stable_id\nENST000001\nENST000001\n")
            with self.assertRaisesRegex(AnalysisBlocker, "duplicate stable_id"):
                materializer.read_ordered_ids(path, expected_rows=2)

    def test_duplicate_structure_transcript_id_blocks(self):
        frozen = ["ENST000001", "ENST000002"]
        rows = [valid_row(frozen[0], structure_id="ENST_SHARED"),
                valid_row(frozen[1], structure_id="ENST_SHARED")]
        with self.assertRaisesRegex(AnalysisBlocker, "duplicate structure_transcript_id"):
            materializer.validate_mapping_rows(rows, frozen, expected_rows=2)

    def test_exact_column_order_and_removed_processed_length_field(self):
        expected = (
            "stable_id", "structure_transcript_id", "mapping_class", "reported_length",
            "unique_source_stable_id", "gene_equal_88_91",
            "chromosome_equal_88_91", "strand_equal_88_91",
            "exon_intervals_equal_88_91", "transcript_length_equal_88_91",
            "transcript_sequence_equal_88_91",
        )
        self.assertEqual(CLASS_A_MAPPING_COLUMNS, expected)
        self.assertNotIn("processed_length_matches_ensembl88", CLASS_A_MAPPING_COLUMNS)
        fixture = SyntheticReferences(self)
        fixture.run()
        with fixture.output.open(newline="") as handle:
            self.assertEqual(tuple(csv.DictReader(handle, delimiter="\t").fieldnames), expected)

    def test_mapping_reported_length_is_ensembl88_expected_length(self):
        source = transcript(exons=((10, 12), (20, 23)), sequence="ACGTA")
        target = transcript(exons=((10, 12), (20, 23)), sequence="ACGTA")
        fixture = SyntheticReferences(self, source=[source], target=[target])
        rows, _ = fixture.run()
        self.assertEqual(rows[0]["reported_length"], 5)

    def test_old_preauthorization_schema_is_rejected(self):
        fixture = SyntheticReferences(self)
        fixture.run()
        content = fixture.output.read_text().replace(
            "unique_source_stable_id",
            "unique_source_stable_id\tprocessed_length_matches_ensembl88",
            1,
        ).replace("true\ttrue", "true\ttrue\ttrue", 1)
        fixture.output.write_text(content)
        with self.assertRaisesRegex(AnalysisBlocker, "schema or column order"):
            parse_mapping_tsv(fixture.output, ["ENST000001"])


class AuthorizedParserLengthTests(unittest.TestCase):
    @staticmethod
    def mapping(length=4):
        return {
            "ENST000001": StructureMapping(
                "ENST000001", "ENST000001", "A", length
            )
        }

    @staticmethod
    def line(reported_length=4, positions=None):
        positions = positions or ["1"] * reported_length
        return "\t".join([
            "ENST000001", str(reported_length), "2.5", *positions,
        ]) + "\n"

    def test_parser_accepts_equal_processed_length(self):
        positions = ["1"] * 50
        parsed = parse_structure_stream(
            StringIO(self.line(50, positions)), self.mapping(50)
        )
        self.assertEqual(parsed.loc[0, "callable_positions"], 50)

    def test_parser_blocks_processed_length_not_equal_to_ensembl88_expected(self):
        with self.assertRaisesRegex(
            AnalysisBlocker, "locked Ensembl 88 expected length"
        ):
            parse_structure_stream(StringIO(self.line(51)), self.mapping(50))

    def test_parser_still_blocks_position_count_mismatch(self):
        with self.assertRaisesRegex(AnalysisBlocker, "position field count"):
            parse_structure_stream(
                StringIO(self.line(50, ["1"] * 49)), self.mapping(50)
            )


class ProhibitedInputTests(unittest.TestCase):
    def test_materializer_refuses_real_structure_and_derived_tables(self):
        prohibited = (
            ROOT / "results/tables/gse132099_structure_inventory.tsv",
            ROOT / "results/tables/ensembl88_to_91_transcript_bridge.tsv",
            ROOT / "results/tables/phase3c_reference_bridge.tsv",
            ROOT / ".cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz",
        )
        for path in prohibited:
            with self.subTest(path=path), self.assertRaises(AnalysisBlocker):
                materializer.reject_prohibited_path(path)

    def test_materializer_refuses_longbench(self):
        for path in (Path("LongBench/input.tsv"), Path("GSE303762/data.tsv")):
            with self.subTest(path=path), self.assertRaises(AnalysisBlocker):
                materializer.reject_prohibited_path(path)

    def test_fixed_generator_inputs_are_structure_blind_and_cli_has_no_paths(self):
        materializer.verify_structure_blind_paths(materializer.FIXED_INPUTS)
        self.assertEqual(list(inspect.signature(materializer.main).parameters), [])
        fixed = {path.as_posix() for path in materializer.FIXED_INPUTS.readable_paths()}
        self.assertFalse(any("structure" in path.lower() for path in fixed))
        self.assertFalse(any("bridge" in path.lower() for path in fixed))
        self.assertFalse(any("longbench" in path.lower() for path in fixed))


if __name__ == "__main__":
    unittest.main()
