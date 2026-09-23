#!/usr/bin/env python3
"""GSE132099 structure-only schema/coverage inventory; never opens sequencing."""
import csv
import gzip
import json
import math
from pathlib import Path
from collections import Counter

INPUT = Path('.cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz')
OUTPUT = Path('results/tables/gse132099_structure_inventory.tsv')
SUMMARY = Path('results/tables/gse132099_inventory_summary.json')


def inspect_row(fields):
    if len(fields) < 4:
        raise ValueError('Processed row has fewer than four fields')
    tid, length_text, rpkm_text = fields[:3]
    length = int(length_text)
    if length < 1 or len(fields)-3 != length:
        raise ValueError(f'Reported length disagrees with score positions: {tid}')
    callable_count = 0
    score_min, score_max = math.inf, -math.inf
    for value in fields[3:]:
        if value == 'NULL':
            continue
        score = float(value)
        if not math.isfinite(score):
            raise ValueError('Non-finite non-NULL score: '+tid)
        callable_count += 1
        score_min = min(score_min,score)
        score_max = max(score_max,score)
    return dict(structure_transcript_id=tid, reported_length=length,
                assay_rpkm=float(rpkm_text), callable_bases=callable_count,
                callable_fraction=callable_count/length,
                min_score=score_min if callable_count else 'NA',
                max_score=score_max if callable_count else 'NA')


def main():
    seen = set()
    stats = Counter()
    min_score, max_score = math.inf, -math.inf
    with gzip.open(INPUT,'rt') as source, OUTPUT.open('w',newline='') as stream:
        writer = None
        for line in source:
            fields = line.rstrip('\n').split('\t')
            row = inspect_row(fields)
            tid = row['structure_transcript_id']
            if tid in seen:
                raise ValueError('Duplicate processed transcript: '+tid)
            seen.add(tid)
            if writer is None:
                writer=csv.DictWriter(stream,fieldnames=list(row),delimiter='\t',lineterminator='\n')
                writer.writeheader()
            writer.writerow(row)
            stats['transcripts'] += 1
            stats['reported_bases'] += row['reported_length']
            stats['callable_bases'] += row['callable_bases']
            if '.' in tid: stats['ids_containing_period'] += 1
            if row['callable_bases'] >= 50 and row['callable_fraction'] >= .5:
                stats['profiles_callable_50_fraction_0_5'] += 1
            if row['callable_bases']:
                min_score = min(min_score,row['min_score'])
                max_score = max(max_score,row['max_score'])
    if not stats['transcripts']:
        raise ValueError('Empty structure file')
    result = dict(stats)
    result.update(min_score=min_score,max_score=max_score,
                  score_semantics='GEO: per-position icSHAPE enrichment score; NULL is uncalled',
                  source='GSE132099 processed in-vivo icSHAPE only',
                  sequencing_outcomes_read=False)
    SUMMARY.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
