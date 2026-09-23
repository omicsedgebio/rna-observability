import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Phase3CTest(unittest.TestCase):
    def test_bridge_and_attrition_counts(self):
        summary = json.loads((ROOT / 'results/tables/phase3c_reference_bridge_summary.json').read_text())
        self.assertEqual(summary['mapping_classes'], {'A': 16268, 'B': 0, 'C': 17, 'D': 5, 'E': 5})
        self.assertEqual(summary['coverage_eligible'], 16055)
        rows = list(csv.DictReader((ROOT / 'results/tables/cohort_attrition.tsv').open(), delimiter='\t'))
        counts = {row['stage']: int(row['n_transcripts']) for row in rows}
        self.assertEqual(counts['future_maximum_intersection'], 15999)

    def test_provisional_folds_are_grouped_and_complete(self):
        rows = list(csv.DictReader((ROOT / 'metadata/cv_folds.tsv').open(), delimiter='\t'))
        self.assertEqual(len(rows), 15999)
        self.assertTrue(all(row['status'] == 'PROVISIONAL_NOT_FROZEN' for row in rows))
        self.assertEqual(len({row['stable_id'] for row in rows}), len(rows))
        self.assertEqual({int(row['fold']) for row in rows}, set(range(5)))

    def test_spikein_missing_rows_not_zero(self):
        rows = list(csv.DictReader((ROOT / 'results/tables/spikein_endpoint_calibration.tsv').open(), delimiter='\t'))
        self.assertTrue(rows)
        self.assertTrue(all(row['missing_sparse_rows_are_not_zero'] == 'True' for row in rows))

    def test_blinding_summaries(self):
        q = json.loads((ROOT / 'results/tables/quantifier_audit_summary.json').read_text())
        s = json.loads((ROOT / 'results/tables/structure_reproducibility_diagnosis.json').read_text())
        self.assertFalse(q['structure_inputs_read'])
        self.assertFalse(q['longbench_inputs_read'])
        self.assertTrue(s['structure_values_only'])
        self.assertFalse(s['sequencing_outcomes_read'])
        self.assertFalse(s['longbench_inputs_read'])


if __name__ == '__main__':
    unittest.main()
