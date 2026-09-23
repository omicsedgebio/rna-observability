"""Small synthetic scientific checks. No scientific cache or network required."""
import gzip
import hashlib
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest
import sys
import subprocess
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rnaobs.core import (Transcript, aggregate_technical, annotation_features,
                         connected_groups, grouped_folds, mapping_class,
                         predictor_guard, read_gtf, reconstruct, sequence_features,
                         signed_endpoint, stable_id, unique_index,
                         provisional_availability)


class ReferenceMappingTests(unittest.TestCase):
    def test_version_strip_preserves_pseudoautosomal_copy(self):
        self.assertEqual(stable_id('ENST0001.12'), 'ENST0001')
        self.assertEqual(stable_id('ENST0001.12_PAR_Y'), 'ENST0001_PAR_Y')
        self.assertNotEqual(stable_id('ENST0001.12_PAR_Y'), stable_id('ENST0001.12'))

    def test_duplicate_stable_ids_are_ambiguous(self):
        a = Transcript('ENST1.1', 'G1', '1', '+', ((0, 4),))
        b = Transcript('ENST1.2', 'G1', '1', '+', ((0, 4),))
        index = unique_index([a, b], lambda x: stable_id(x.identifier))
        self.assertEqual(mapping_class(a, index['ENST1'])[0], 'D')
        self.assertEqual(mapping_class(a, [a], 'ACGT', {a.identifier:'ACGT'}, duplicate_target=True)[0], 'D')

    def test_exact_stable_sequence_and_exon_mismatch(self):
        a = Transcript('ENST1.1', 'G1', '1', '+', ((0, 4),))
        v = Transcript('ENST1.2', 'G1', '1', '+', ((0, 4),))
        e = Transcript('ENST1.1', 'G1', '1', '+', ((1, 5),))
        self.assertEqual(mapping_class(a, [a], 'ACGT', {a.identifier:'ACGT'})[0], 'A')
        self.assertEqual(mapping_class(a, [v], 'ACGT', {v.identifier:'ACGT'})[0], 'B')
        self.assertEqual(mapping_class(a, [e], 'ACGT', {e.identifier:'ACGT'})[0], 'C')
        self.assertEqual(mapping_class(a, [a], 'ACGT', {a.identifier:'TGCA'})[0], 'C')
        self.assertEqual(mapping_class(a, [a], 'ACGT', {})[0], 'D')
        self.assertEqual(mapping_class(a, [])[0], 'E')

    def test_gtf_version_coordinate_and_minus_strand_reconstruction(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'small.gtf.gz'
            with gzip.open(path, 'wt') as out:
                out.write('1\tsrc\texon\t1\t4\t.\t-\t.\tgene_id "G1"; transcript_id "ENST1"; transcript_version "2";\n')
                out.write('1\tsrc\texon\t7\t8\t.\t-\t.\tgene_id "G1"; transcript_id "ENST1"; transcript_version "2";\n')
            tx = read_gtf(path)['ENST1.2']
            self.assertEqual(tx.exons, ((0, 4), (6, 8)))
            self.assertEqual(reconstruct(tx, {'1':'ACGTCCAA'}), 'TTACGT')

    def test_reference_manifest_release_and_hash_format(self):
        import csv
        with (ROOT/'metadata/reference_resources.tsv').open() as handle:
            rows=list(csv.DictReader(handle,delimiter='\t'))
        release91 = [r for r in rows if 'Ensembl 91' in r['release']]
        self.assertEqual(len(release91), 7)
        self.assertEqual(len({r['resource_id'] for r in rows}), len(rows))
        for row in release91:
            self.assertIn('Ensembl 91', row['release'])
            self.assertEqual(row['assembly'], 'GRCh38')
            self.assertEqual(len(row['sha256']), 64)
            int(row['sha256'], 16)
            self.assertGreater(int(row['bytes']), 0)
            self.assertTrue(row['authoritative_url'].startswith('https://'))


class FeatureAndMeasurementTests(unittest.TestCase):
    def test_sequence_features(self):
        x=sequence_features('AAAAAAGCGC')
        self.assertEqual(x['sequence_length'],10)
        self.assertAlmostEqual(x['gc_fraction'],0.4)
        self.assertAlmostEqual(x['homopolymer_fraction'],0.6)
        self.assertTrue(math.isnan(x['low_complexity_fraction']))
        self.assertEqual(x['sequence_sha256'],hashlib.sha256(b'AAAAAAGCGC').hexdigest())

    def test_annotation_identifiability(self):
        a=Transcript('T1.1','G1','1','+',((0,4),(8,12)))
        b=Transcript('T2.1','G1','1','+',((0,4),(10,14)))
        f=annotation_features([a,b])
        self.assertEqual(f['T1.1']['isoforms_per_gene'],2)
        self.assertEqual(f['T1.1']['unique_exonic_bases'],2)
        self.assertEqual(f['T1.1']['unique_junction_count'],1)
        self.assertAlmostEqual(f['T1.1']['shared_exon_fraction'],.75)

    def test_aggregation_and_endpoint(self):
        self.assertAlmostEqual(aggregate_technical([2.,4.],[1.,3.]),3.5)
        with self.assertRaises(ValueError):
            aggregate_technical([2.,float('nan')],[1.,1.])
        self.assertAlmostEqual(signed_endpoint([4.,4.],[1.,1.],offset=1.),math.log2(5/2))
        with self.assertRaises(ValueError):
            signed_endpoint([0.],[-1.])

    def test_grouped_cv_and_guard(self):
        group=connected_groups(['G1','G2','G3'],[('G1','G2')])
        self.assertEqual(group['G1'],group['G2'])
        fold=grouped_folds(group,2,230923)
        self.assertEqual(fold['G1'],fold['G2'])
        self.assertNotEqual(fold['G1'],fold['G3'])
        with self.assertRaises(ValueError):
            predictor_guard(['outcome'],{'outcome':'OUTCOME_DERIVED'})
        with self.assertRaises(ValueError):
            predictor_guard(['gc'],{'gc':'PRE_MEASUREMENT_MOLECULAR'},['lib1'],['lib1'])
        with self.assertRaises(ValueError):
            predictor_guard(['icshape'],{'icshape':'PRE_MEASUREMENT_MOLECULAR'})

    def test_missingness_and_provenance_summary(self):
        import json
        m=json.loads((ROOT/'results/tables/missingness_adjusted_summary.json').read_text())
        self.assertFalse(m['reactivity_values_read'])
        self.assertFalse(m['disagreement_values_read'])
        self.assertLessEqual(m['usable_provisional'],m['feature_universe'])
        self.assertLess(m['weight_effective_sample_size'],m['usable_provisional'])
        f=json.loads((ROOT/'results/tables/feature_audit_summary.json').read_text())
        self.assertFalse(f['structure_inputs_read'])
        self.assertFalse(f['outcome_inputs_read'])
        self.assertTrue(provisional_availability(True,'icshape_source_exons_and_sequence_unavailable',.5,50))
        self.assertFalse(provisional_availability(True,'icshape_source_exons_and_sequence_unavailable',.49,50))
        self.assertFalse(provisional_availability(True,'icshape_source_exons_and_sequence_unavailable',.5,49))
        self.assertFalse(provisional_availability(True,'icshape_source_exons_and_sequence_unavailable',float('nan'),50))
        self.assertFalse(provisional_availability(False,'icshape_source_exons_and_sequence_unavailable',.9,100))
        import csv
        with (ROOT/'metadata/phase3a_source_provenance.tsv').open() as handle:
            rows=list(csv.DictReader(handle,delimiter='\t'))
        self.assertGreater(len(rows),30)
        for row in rows:
            self.assertTrue(row['authoritative_url'].startswith('https://'))
            self.assertEqual(len(row['sha256']),64)
            self.assertGreater(int(row['bytes']),0)
            self.assertTrue(row['retrieved_utc'])

    @unittest.skipUnless(shutil.which('c++'), 'C++ compiler absent')
    def test_canonical_unique_kmers(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory)
            fasta=d/'tiny.fa'
            fasta.write_text('>T1\nACGTA\n>T2\nTACGT\n>T3\nTTTTT\n')
            binary=d/'kmers'
            subprocess.run(['c++','-std=c++23','-O0',str(ROOT/'src/exact_kmers.cpp'),'-o',str(binary)],check=True,capture_output=True)
            subprocess.run([str(binary),str(fasta),'4',str(d/'scratch'),str(d/'out.tsv')],check=True,capture_output=True)
            import csv
            with (d/'out.tsv').open() as handle:
                rows=list(csv.DictReader(handle,delimiter='\t'))
            self.assertEqual(len(rows),3)
            self.assertEqual(rows[0]['unique_kmer_fraction'],'0')
            self.assertEqual(rows[1]['unique_kmer_fraction'],'0')
            self.assertEqual(rows[2]['unique_kmer_fraction'],'1')


if __name__=='__main__':
    unittest.main()
