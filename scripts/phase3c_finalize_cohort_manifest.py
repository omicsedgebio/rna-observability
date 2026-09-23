#!/usr/bin/env python3
"""Materialize the pre-endpoint eligible transcript manifest from fixed folds."""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'metadata/cv_folds.tsv'
OUT = ROOT / 'metadata/final_transcript_cohort.tsv'


def main():
    with SOURCE.open() as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    if not rows or len({row['stable_id'] for row in rows}) != len(rows):
        raise ValueError('fold manifest is empty or contains duplicate stable IDs')
    if {int(row['fold']) for row in rows} != set(range(5)):
        raise ValueError('fold manifest does not contain exactly five folds')
    with OUT.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['cohort_status', 'stable_id', 'fold'],
                                delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({'cohort_status': 'PRE_ENDPOINT_ELIGIBILITY',
                             'stable_id': row['stable_id'], 'fold': row['fold']})
    print({'n_transcripts': len(rows), 'status': 'PRE_ENDPOINT_ELIGIBILITY',
           'rule': 'class-A mapping, structure coverage eligible, complete Illumina/direct-RNA Salmon row availability'})


if __name__ == '__main__':
    main()
