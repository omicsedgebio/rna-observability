#!/usr/bin/env python3
"""Stream K562 icSHAPE rows and produce identifier/coverage QC only."""
import csv
import gzip
import json
import math
from collections import Counter
from pathlib import Path

src = Path('.cache/phase2/icshape/GSM4333260_K562.out.txt.gz')
out = Path('results/tables')
out.mkdir(parents=True, exist_ok=True)
ids = []
records = []
rows = score_count = 0
score_sum = score_sq = 0.0
score_min = math.inf
score_max = -math.inf

with gzip.open(src, 'rt', encoding='utf-8') as handle:
    for row in csv.reader(handle, delimiter='\t'):
        if not row:
            continue
        tx_id = row[0]
        try:
            length = int(row[1])
        except ValueError:
            length = None
        vals = []
        for value in row[3:]:
            if value in {'NULL', ''}:
                continue
            try:
                v = float(value)
            except ValueError:
                continue
            if math.isfinite(v):
                vals.append(v)
        n = len(vals)
        rows += 1
        score_count += n
        score_sum += sum(vals)
        score_sq += sum(v * v for v in vals)
        if vals:
            score_min = min(score_min, min(vals))
            score_max = max(score_max, max(vals))
        ids.append(tx_id)
        records.append((tx_id, length, n, n / length if length else None))

id_counts = Counter(ids)
stable = [tx_id.rsplit('.', 1)[0] if '.' in tx_id else tx_id for tx_id in ids]
stable_counts = Counter(stable)
with (out / 'icshape_transcript_inventory.tsv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
    writer.writerow(['structure_transcript_id', 'stable_transcript_id', 'reported_length', 'callable_bases', 'callable_fraction'])
    for tx_id, length, n, frac in records:
        writer.writerow([tx_id, tx_id.rsplit('.', 1)[0] if '.' in tx_id else tx_id, length, n, 'NA' if frac is None else f'{frac:.8g}'])

summary = {
    'source': str(src),
    'rows': rows,
    'unique_transcript_ids': len(id_counts),
    'duplicate_transcript_id_rows': sum(v - 1 for v in id_counts.values() if v > 1),
    'unique_stable_ids': len(stable_counts),
    'versioned_id_rows': sum(1 for tx_id in ids if '.' in tx_id),
    'score_values': score_count,
    'score_min': score_min if score_count else None,
    'score_max': score_max if score_count else None,
    'score_mean': score_sum / score_count if score_count else None,
    'score_sd': math.sqrt(max(0.0, score_sq / score_count - (score_sum / score_count) ** 2)) if score_count else None,
    'missing_score_semantics': 'NULL or empty fields are no confident score; retained as missing, never zero',
    'coordinate_semantics': 'one row per reported Ensembl transcript; remaining columns are nucleotide-resolution scores; exact start/orientation requires source pipeline verification',
    'depth_filter': 'source GEO record and PrismNet methods report retaining scores with read depth >100; this file does not carry per-position depth',
}
(out / 'icshape_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
