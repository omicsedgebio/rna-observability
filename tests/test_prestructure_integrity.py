"""Offline, standard-library integrity checks. No model or structure data read."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PrestructureIntegrityTests(unittest.TestCase):
    def test_baseline_artifacts_unchanged(self):
        expected = {
            'metadata/final_transcript_cohort.tsv': '3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5',
            'metadata/cv_folds.tsv': '66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52',
            'results/tables/baseline_model_metrics.tsv': 'c3e51b6fd307f10fe20f6593574e18678cf62f9fc6072ad7f03c8e5ac6305931',
            'results/tables/baseline_model_summary.json': 'b1e2dcbac3d5045d52ebe2b3f8266975fdde18104da29ee0df71be33507b9f8e',
            'metadata/feature_definitions.tsv': '30b96cad1df8d9f9cad4e4829702e739a05013a013fb5b4f0b3d770859ab8d4d',
            'docs/structure_feature_specification.md': '271e23c803f1bd081f2c4007b4bdb9e038d009673bfd96ddc08dd5389dd4b580',
            'analysis/baseline_models/fit_structure_blind.py': '175239e847e7d4cc6a3b812913541d518c942403af43b870af18fff5bdf8259c',
        }
        for path, digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest, path)

    def test_folds_cover_cohort_and_keep_clusters_together(self):
        with (ROOT / 'metadata/cv_folds.tsv').open() as handle:
            folds = list(csv.DictReader(handle, delimiter='\t'))
        with (ROOT / 'metadata/final_transcript_cohort.tsv').open() as handle:
            cohort = list(csv.DictReader(handle, delimiter='\t'))
        self.assertEqual(len(folds), 15999)
        self.assertEqual(len({r['stable_id'] for r in folds}), 15999)
        self.assertEqual({r['stable_id'] for r in folds}, {r['stable_id'] for r in cohort})
        self.assertEqual({r['fold'] for r in folds}, set('01234'))
        group_folds = {}
        for row in folds:
            group_folds.setdefault(row['sequence_cluster_id'], set()).add(row['fold'])
        self.assertEqual(len(group_folds), 4314)
        self.assertTrue(all(len(v) == 1 for v in group_folds.values()))

    def test_predictor_spec_matches_saved_summary(self):
        tree = ast.parse((ROOT / 'analysis/baseline_models/fit_structure_blind.py').read_text())
        specs = [ast.literal_eval(n.value) for n in ast.walk(tree)
                 if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'feature_sets' for t in n.targets)]
        self.assertEqual(len(specs), 1)
        summary = json.loads((ROOT / 'results/tables/baseline_model_summary.json').read_text())
        self.assertEqual(specs[0], summary['feature_sets'])
        allowed = {'independent_abundance_log1p', 'sequence_length', 'gc_fraction',
                   'exon_count', 'isoforms_per_gene', 'sequence_cluster_size',
                   'homopolymer_fraction', 'low_complexity_fraction', 'sequence_entropy'}
        self.assertTrue(all(set(v) <= allowed for v in specs[0].values()))

    def test_no_false_lock_created(self):
        report = (ROOT / 'docs/prestructure_decision_chronology.md').read_text()
        self.assertIn('**BLOCK_STRUCTURE_TEST**', report)
        self.assertFalse((ROOT / 'docs/prestructure_analysis_lock.md').exists())
        self.assertIn('MISSING; no recorded hash', report)


if __name__ == '__main__':
    unittest.main()
