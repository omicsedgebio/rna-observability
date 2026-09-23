import csv
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Phase3DTests(unittest.TestCase):
    def read(self, rel):
        with (ROOT/rel).open() as h: return list(csv.DictReader(h,delimiter='\t'))
    def test_sequence_clusters_complete(self):
        rows=self.read('metadata/transcript_sequence_clusters.tsv'); self.assertEqual(len(rows),15999); self.assertEqual(len({r['stable_id'] for r in rows}),15999); self.assertEqual(len({r['sequence_cluster_id'] for r in rows}),4314)
    def test_folds_cluster_complete(self):
        rows=self.read('metadata/cv_folds.tsv'); self.assertEqual(len(rows),15999); by={}
        for r in rows: by.setdefault(r['sequence_cluster_id'],set()).add(r['fold'])
        self.assertTrue(all(len(v)==1 for v in by.values())); self.assertEqual({int(r['fold']) for r in rows},set(range(5)))
    def test_primary_blinding(self):
        rows=self.read('results/tables/phase3d_quantifier_agreement_summary.tsv'); self.assertTrue(rows); self.assertTrue(all(r['structure_inputs_read']=='False' and r['sequencing_outcomes_read']=='False' for r in rows))
    def test_baseline_outputs_blinded(self):
        d=json.loads((ROOT/'results/tables/baseline_model_summary.json').read_text()); self.assertEqual(d['models'],['A','B','C']); self.assertFalse(d['structure_inputs_read']); self.assertFalse(d['longbench_inputs_read'])
    def test_plan_frozen_scope(self):
        p=(ROOT/'docs/frozen_analysis_plan.md').read_text(); self.assertIn('Status: FROZEN_PHASE3D',p); self.assertIn('RNA structure versus sequencing measurement behavior has not been inspected.',p); self.assertIn('workflow-specific',p)
if __name__=='__main__': unittest.main()
