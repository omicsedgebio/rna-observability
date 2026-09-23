#!/usr/bin/env python3
"""Structure-to-structure only reproducibility; sequencing files are never read."""
import csv
import gzip
import json
import tarfile
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/tables/structure_reproducibility.tsv'
SUMMARY = ROOT / 'results/tables/structure_reproducibility_summary.json'


def median_callable(values):
    x = np.array([float(y) for y in values if y not in ('NULL', '-999.0')], dtype=float)
    return (float(np.median(x)) if len(x) else float('nan'), len(x))


def bootstrap_cluster_ci(rows, x, y, seed=33149, draws=500):
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[row['gene_id']].append(i)
    keys = list(groups)
    rng = np.random.default_rng(seed)
    result = []
    for _ in range(draws):
        choice = rng.choice(len(keys), size=len(keys), replace=True)
        indices = [i for g in choice for i in groups[keys[g]]]
        result.append(float(spearmanr(np.asarray(x)[indices], np.asarray(y)[indices]).statistic))
    return [float(z) for z in np.quantile(result, [.025, .975])]


def main():
    bridge = {row['structure_transcript_id']: row for row in
              csv.DictReader((ROOT / 'results/tables/ensembl88_to_91_transcript_bridge.tsv').open(), delimiter='\t')
              if row['primary_eligible'] == 'True'}
    compat = {row['profile_id']: row for row in
              csv.DictReader((ROOT / 'results/tables/gse149767_compatibility.tsv').open(), delimiter='\t')
              if row['compatibility'] == 'UNIQUE_EXACT_ENSEMBL91_SEQUENCE'}
    by_target = {row['ensembl91_sgnex_transcript_id']: sid for sid, row in bridge.items()}
    selected = {profile: (row, by_target[row['ensembl91_transcript_id']]) for profile, row in compat.items()
                if row['ensembl91_transcript_id'] in by_target}
    study = {}
    with gzip.open(ROOT / '.cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz', 'rt') as stream:
        wanted = {sid for _, sid in selected.values()}
        for line in stream:
            fields = line.rstrip('\n').split('\t')
            if fields[0] in wanted:
                med, n = median_callable(fields[3:])
                study[fields[0]] = (med, n, len(fields) - 3)
    independent = {}
    with tarfile.open(ROOT / '.cache/phase3b/structure/GSE149767_k562_vivo_icshape.tar.gz', 'r|gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.rx'):
                continue
            profile = Path(member.name).name.removesuffix('.rx')
            if profile not in selected:
                continue
            cols = [[], []]
            for line in archive.extractfile(member):
                vals = line.decode().split()
                for j in range(2):
                    if vals[j] != '-999.0':
                        cols[j].append(float(vals[j]))
            independent[profile] = [(float(np.median(z)) if z else float('nan'), len(z)) for z in cols]
    rows = []
    for profile, (record, sid) in selected.items():
        if sid not in study or profile not in independent:
            continue
        gmed, gn, glen = study[sid]
        (r1, n1), (r2, n2) = independent[profile]
        length = int(record['vivo_length'])
        if min(n1, n2) < 50 or min(n1, n2) / length < .5 or not np.isfinite([gmed, r1, r2]).all():
            continue
        rows.append(dict(gse132099_id=sid, ensembl91_transcript_id=record['ensembl91_transcript_id'],
                         gene_id=bridge[sid]['gene_id'], gse149767_refseq=record['refseq_id'],
                         length=length, gse132099_callable=gn, gse132099_callable_fraction=gn/glen,
                         gse132099_median_reactivity=gmed, gse149767_rep1_callable=n1,
                         gse149767_rep2_callable=n2, gse149767_rep1_median=r1,
                         gse149767_rep2_median=r2, gse149767_mean_of_replicate_medians=(r1+r2)/2))
    with OUT.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else [], delimiter='\t', lineterminator='\n')
        if rows:
            writer.writeheader(); writer.writerows(rows)
    x = [r['gse132099_median_reactivity'] for r in rows]
    y = [r['gse149767_mean_of_replicate_medians'] for r in rows]
    r1 = [r['gse149767_rep1_median'] for r in rows]
    r2 = [r['gse149767_rep2_median'] for r in rows]
    fraction1 = [r['gse132099_callable_fraction'] for r in rows]
    fraction2 = [(r['gse149767_rep1_callable'] + r['gse149767_rep2_callable']) / (2*r['length']) for r in rows]
    summary = dict(n_profiles=len(rows), n_genes=len({r['gene_id'] for r in rows}),
                   cross_study_median_spearman=float(spearmanr(x, y).statistic) if len(rows)>2 else None,
                   cross_study_gene_bootstrap_95ci=bootstrap_cluster_ci(rows, x, y) if len(rows)>2 else None,
                   gse149767_replicate_median_spearman=float(spearmanr(r1, r2).statistic) if len(rows)>2 else None,
                   cross_study_callable_fraction_spearman=float(spearmanr(fraction1, fraction2).statistic) if len(rows)>2 else None,
                   sequencing_outcomes_read=False, structure_vs_sequencing_tested=False)
    SUMMARY.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
