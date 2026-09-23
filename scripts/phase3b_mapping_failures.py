#!/usr/bin/env python3
"""Audit Phase 3A failures without interpreting missing source definitions as mismatches."""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results/tables/transcript_mapping_validated.tsv'
OUT = ROOT / 'results/tables/mapping_failure_categories.tsv'


def category(row):
    if row['mapping_class'] == 'E':
        return 'no_stable_identifier_overlap'
    if row['mapping_class'] == 'C':
        return 'reported_length_mismatch'
    if row['mapping_class'] == 'D':
        return 'source_annotation_sequence_unavailable'
    raise ValueError('Unexpected validated row class')


def main():
    counts = Counter()
    with SOURCE.open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            counts[category(row)] += 1
            if row['mapping_class'] == 'D' and row['exact_version_id'] == 'True':
                counts['diagnostic_exact_id_equal_length_unverified'] += 1
            if row['version_recovered_from_gtf'] == 'True':
                counts['diagnostic_sgnex_version_recovered'] += 1
    zero_categories = ['version_difference_only_confirmed', 'exon_coordinate_mismatch_confirmed',
                       'sequence_mismatch_confirmed', 'annotation_build_mismatch_confirmed',
                       'identifier_semantics_mismatch_confirmed',
                       'possible_preprocessing_artifact_confirmed',
                       'incorrect_source_annotation_assumption_confirmed']
    with OUT.open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(['failure_category', 'transcripts', 'count_type', 'interpretation'])
        for name in ['no_stable_identifier_overlap', 'reported_length_mismatch',
                     'source_annotation_sequence_unavailable']:
            writer.writerow([name, counts[name], 'mutually_exclusive', 'Phase 3A observed'])
        for name in zero_categories:
            writer.writerow([name, 0, 'not_confirmed', 'Cannot establish without source GSE145805 transcriptome'])
        for name in ['diagnostic_exact_id_equal_length_unverified',
                     'diagnostic_sgnex_version_recovered']:
            writer.writerow([name, counts[name], 'overlapping_diagnostic', 'Not a validated mapping failure'])
    print(dict(counts))


if __name__ == '__main__':
    main()
