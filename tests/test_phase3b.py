"""Small synthetic Phase 3B scientific and provenance checks; no source downloads."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rnaobs.core import Transcript
from rnaobs.phase3b import detection_status, platform_category, positive_log_ratio


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BridgeTests(unittest.TestCase):
    def test_full_reference_equivalence_and_changes(self):
        bridge = script('phase3b_bridge')
        old = Transcript('ENST1.1', 'ENSG1', '1', '+', ((0, 4), (8, 12)))
        same = Transcript('ENST1.1', 'ENSG1', '1', '+', old.exons)
        benign = Transcript('ENST1.2', 'ENSG1', '1', '+', old.exons)
        changed = Transcript('ENST1.1', 'ENSG1', '1', '+', ((0, 4), (9, 13)))
        digest = hashlib.sha256(b'ACGTTGCA').hexdigest()
        self.assertEqual(bridge.classify(old, same, 'ACGTTGCA', digest, 8)[0], 'A')
        self.assertEqual(bridge.classify(old, benign, 'ACGTTGCA', digest, 8)[0], 'B')
        self.assertEqual(bridge.classify(old, changed, 'ACGTTGCA', digest, 8)[0], 'C')
        self.assertEqual(bridge.classify(old, same, 'ACGTTGCA', hashlib.sha256(b'ACGTTGCT').hexdigest(), 8)[0], 'C')
        self.assertEqual(bridge.classify(old, same, 'ACGTTGCA', digest, 7)[0], 'D')
        self.assertEqual(bridge.classify(None, same, None, digest, 8)[0], 'E')

    def test_refseq_key_not_gene_symbol(self):
        resolver = script('phase3b_gse149767')
        self.assertEqual(resolver.prefix('chr12+.NM_003805.GENEX.map'), 'chr12+.NM_003805')
        self.assertEqual(resolver.prefix('chr12+.NM_003805.rx'), 'chr12+.NM_003805')
        self.assertIsNone(resolver.prefix('chr12+.GENEX.map'))


class EndpointTests(unittest.TestCase):
    def test_three_state_detection_and_four_categories(self):
        self.assertEqual(detection_status([1.1, 1.3], 1, 2), 'detected')
        self.assertEqual(detection_status([0, 0], 1, 2), 'absent')
        self.assertEqual(detection_status([0, 1.3], 1, 2), 'indeterminate')
        self.assertEqual(detection_status([1, 1, 0, 1], 1, 3), 'detected')
        self.assertEqual(platform_category('detected', 'absent'), 'illumina_only')
        self.assertEqual(platform_category('absent', 'detected'), 'direct_rna_only')
        self.assertEqual(platform_category('detected', 'detected'), 'both')
        self.assertEqual(platform_category('absent', 'absent'), 'neither')
        self.assertEqual(platform_category('indeterminate', 'detected'), 'indeterminate')
        with self.assertRaises(ValueError):
            detection_status([1, float('nan')], 1, 2)

    def test_positive_only_ratio_has_no_pseudocount(self):
        self.assertAlmostEqual(positive_log_ratio([1, 2], [2, 4]), 1)
        self.assertTrue(np.isnan(positive_log_ratio([0, 2], [2, 4])))


class ProvenanceTests(unittest.TestCase):
    def test_phase3b_resources_complete_and_reference_release_exact(self):
        with (ROOT / 'metadata/phase3b_resources.tsv').open() as stream:
            rows = list(csv.DictReader(stream, delimiter='\t'))
        self.assertEqual(len(rows), 7)
        self.assertEqual(len({r['resource_id'] for r in rows}), 7)
        for row in rows:
            self.assertTrue(row['authoritative_url'].startswith('https://'))
            self.assertEqual(len(row['sha256']), 64)
            self.assertGreater(int(row['bytes']), 0)
            self.assertTrue(row['retrieved_utc'])
        release88 = [r for r in rows if r['resource_id'].startswith('ensembl88')]
        self.assertEqual(len(release88), 3)
        self.assertTrue(all(r['release'] == 'Ensembl 88' for r in release88))

    def test_structure_sequencing_blinding_assertions(self):
        for path in ['ensembl88_to_91_bridge_summary.json', 'gse132099_missingness_summary.json',
                     'gse149767_compatibility_summary.json', 'structure_reproducibility_summary.json']:
            summary = json.loads((ROOT / 'results/tables' / path).read_text())
            self.assertFalse(summary.get('sequencing_outcomes_read', False))
            self.assertFalse(summary.get('structure_vs_sequencing_tested', False))
        endpoint = json.loads((ROOT / 'results/tables/zero_aware_endpoint_summary.json').read_text())
        self.assertFalse(endpoint['structure_input_used'])


if __name__ == '__main__':
    unittest.main()
