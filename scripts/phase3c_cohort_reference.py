#!/usr/bin/env python3
"""Reconstruct the Phase 3B bridge from pinned GTF/FASTA and coverage masks only."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rnaobs.core import fasta_records, read_gtf, stable_id, unique_index


def sequences(paths, wanted):
    found = {}
    for path in paths:
        for name, sequence in fasta_records(path):
            if name in wanted:
                if name in found:
                    raise ValueError('Duplicate reference FASTA ID: ' + name)
                found[name] = sequence.upper()
    return found


def classify(old, new, seq_old, seq_new, reported_length):
    if old is None or new is None:
        return 'E', 'absent_reference'
    if seq_old is None or seq_new is None:
        return 'D', 'reference_fasta_missing'
    if old.length != reported_length or len(seq_old) != old.length:
        return 'D', 'source_length_inconsistent'
    if len(seq_new) != new.length:
        return 'D', 'target_length_inconsistent'
    if (old.gene, old.chrom, old.strand, old.exons, seq_old) != (
            new.gene, new.chrom, new.strand, new.exons, seq_new):
        return 'C', 'material_definition_change'
    return ('A', 'exact_reference_definition') if old.identifier == new.identifier else (
        'B', 'benign_version_metadata_difference')


def main():
    inventory = pd.read_csv(ROOT / 'results/tables/gse132099_structure_inventory.tsv',
                            sep='\t', usecols=['structure_transcript_id', 'reported_length',
                                               'callable_bases', 'callable_fraction'])
    if inventory.structure_transcript_id.duplicated().any():
        raise ValueError('Duplicate processed structure ID')
    old = read_gtf(ROOT / '.cache/phase3b/references/ensembl88.gtf.gz')
    new = read_gtf(ROOT / '.cache/phase3a/references/ensembl91.gtf.gz')
    idx_old = unique_index(old.values(), lambda x: stable_id(x.identifier))
    idx_new = unique_index(new.values(), lambda x: stable_id(x.identifier))
    wanted = set(inventory.structure_transcript_id)
    ids_old = {x.identifier for sid in wanted for x in idx_old.get(stable_id(sid), [])}
    ids_new = {x.identifier for sid in wanted for x in idx_new.get(stable_id(sid), [])}
    seq_old = sequences([ROOT / '.cache/phase3b/references/ensembl88.cdna.fa.gz',
                         ROOT / '.cache/phase3b/references/ensembl88.ncrna.fa.gz'], ids_old)
    seq_new = sequences([ROOT / '.cache/phase3a/references/ensembl91.cdna.fa.gz',
                         ROOT / '.cache/phase3a/references/ensembl91.ncrna.fa.gz'], ids_new)
    output = ROOT / 'results/tables/phase3c_reference_bridge.tsv'
    fields = ['structure_transcript_id', 'ensembl88_transcript_id', 'ensembl91_transcript_id',
              'gene_id', 'mapping_class', 'reason', 'transcript_length', 'callable_bases',
              'callable_fraction', 'coverage_eligible', 'chromosome', 'strand', 'exon_count',
              'sequence_sha256']
    count = Counter()
    with output.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for row in inventory.itertuples(index=False):
            sid = stable_id(row.structure_transcript_id)
            a = idx_old.get(sid, [])
            b = idx_new.get(sid, [])
            if len(a) > 1 or len(b) > 1:
                cls, reason = 'D', 'ambiguous_stable_identifier'
            else:
                cls, reason = classify(a[0] if a else None, b[0] if b else None,
                    seq_old.get(a[0].identifier) if a else None,
                    seq_new.get(b[0].identifier) if b else None, int(row.reported_length))
            target = b[0] if len(b) == 1 else None
            coverage = cls == 'A' and row.callable_bases >= 50 and row.callable_fraction >= .5
            count[cls] += 1
            count['coverage_eligible'] += int(coverage)
            writer.writerow(dict(structure_transcript_id=row.structure_transcript_id,
                ensembl88_transcript_id=a[0].identifier if len(a) == 1 else 'NA',
                ensembl91_transcript_id=target.identifier if target else 'NA',
                gene_id=target.gene if target else 'NA', mapping_class=cls, reason=reason,
                transcript_length=target.length if target else 'NA',
                callable_bases=row.callable_bases, callable_fraction=row.callable_fraction,
                coverage_eligible=coverage, chromosome=target.chrom if target else 'NA',
                strand=target.strand if target else 'NA',
                exon_count=len(target.exons) if target else 'NA',
                sequence_sha256=hashlib.sha256(seq_new[target.identifier].encode()).hexdigest()
                if target and target.identifier in seq_new else 'NA'))
    prior = json.loads((ROOT / 'results/tables/ensembl88_to_91_bridge_summary.json').read_text())
    expected = prior['mapping_classes']
    if any(count[k] != expected[k] for k in 'ABCDE') or count['coverage_eligible'] != prior['a_or_b_coverage_eligible']:
        raise ValueError('Phase 3B class or coverage counts not reproduced')
    summary = dict(ensembl91_transcripts=len(new), structure_profiles=len(inventory),
                   mapping_classes={k:count[k] for k in 'ABCDE'},
                   coverage_eligible=count['coverage_eligible'],
                   study_ids_lengths_masks_only=True, structure_values_read=False,
                   sequencing_outcomes_read=False)
    (ROOT / 'results/tables/phase3c_reference_bridge_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
