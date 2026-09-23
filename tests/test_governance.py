"""Negative tests for mistakes that could compromise repository governance."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "validator", Path(__file__).resolve().parents[1] / "scripts/validate_repository.py"
)
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class GovernanceTests(unittest.TestCase):
    def test_raw_and_cache_rejected(self):
        for path in ["sample.fastq.gz", "sample.bam", "sample.cram", "tmp/cache.json", "data/external/x.rds"]:
            self.assertTrue(V.forbidden_file(path, 10), path)

    def test_small_metadata_and_placeholders_allowed(self):
        for path in ["metadata/datasets.tsv", "data/external/.gitkeep", "README.md"]:
            self.assertFalse(V.forbidden_file(path, 100), path)
        self.assertTrue(V.forbidden_file("matrix.tsv", 1000001))

    def test_ragged_and_duplicate_rows_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.tsv"
            path.write_text("id\tvalue\na\tx\na\ty\nb\n", encoding="utf-8")
            _, errors = V.read_table(path, ["id", "value"])
            self.assertTrue(any("duplicate" in e for e in errors))
            self.assertTrue(any("ragged" in e for e in errors))

    def test_actual_repository(self):
        self.assertEqual(V.validate(), [])

    def test_unlock_or_false_freeze_rejected(self):
        import json
        policy = json.loads((V.ROOT / "configs/phase1.json").read_text())
        rows, _ = V.read_table(V.ROOT / "metadata/datasets.tsv", V.SCHEMAS["metadata/datasets.tsv"])
        policy["external_validation_locked"] = False
        errors = V.phase_errors(policy, "Status: FROZEN", "Status: LOCKED 2026-09-22", rows)
        self.assertTrue(any("external_validation_locked" in e for e in errors))
        self.assertTrue(any("incorrectly marked frozen" in e for e in errors))

    def test_invented_checksum_rejected(self):
        import json
        policy = json.loads((V.ROOT / "configs/phase1.json").read_text())
        rows, _ = V.read_table(V.ROOT / "metadata/datasets.tsv", V.SCHEMAS["metadata/datasets.tsv"])
        next(row for row in rows if row["dataset_id"] == "LONGBENCH")["sha256"] = "0" * 64
        errors = V.phase_errors(policy, "Status: DRAFT_NOT_FROZEN", "Status: LOCKED 2026-09-22", rows)
        self.assertTrue(any("invented checksum" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
