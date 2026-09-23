#!/usr/bin/env python3
"""Freeze deterministic gene and high-similarity grouped folds."""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLUSTERS = ROOT / 'metadata/transcript_sequence_clusters.tsv'
MEMBERS = ROOT / '.cache/phase3d/cluster_members.tsv'
QTABLE = ROOT / 'results/tables/phase3d_quantifier_agreement.tsv'
FOLDS = ROOT / 'metadata/cv_folds.tsv'
COHORT = ROOT / 'metadata/final_transcript_cohort.tsv'
BALANCE = ROOT / 'results/tables/phase3d_fold_balance.tsv'
SEED = 20260923


def category(row):
    i, d = int(row.illumina_salmon_threshold_runs), int(row.directrna_salmon_threshold_runs)
    istate = 'detected' if i == 2 else 'absent' if i == 0 else 'indeterminate'
    dstate = 'detected' if d >= 3 else 'absent' if d == 0 else 'indeterminate'
    if 'indeterminate' in (istate, dstate): return 'INDETERMINATE'
    return {('detected', 'detected'): 'BOTH', ('detected', 'absent'): 'ILLUMINA_ONLY',
            ('absent', 'detected'): 'DIRECT_RNA_ONLY', ('absent', 'absent'): 'NEITHER'}[(istate, dstate)]


def main():
    c = pd.read_csv(CLUSTERS, sep='\t')
    m = pd.read_csv(MEMBERS, sep='\t')
    c = c.merge(m[['stable_id', 'gene_id']], on='stable_id', validate='one_to_one')
    groups = c.groupby('sequence_cluster_id').size().sort_values(ascending=False)
    rng = np.random.default_rng(SEED)
    ids = list(groups.index); rng.shuffle(ids)
    fold_sizes = [0] * 5; assignment = {}
    for group in ids:
        fold = min(range(5), key=lambda i: (fold_sizes[i], i))
        assignment[group] = fold; fold_sizes[fold] += int(groups[group])
    c['fold'] = c.sequence_cluster_id.map(assignment).astype(int)
    q = pd.read_csv(QTABLE, sep='\t', usecols=['stable_id', 'illumina_salmon_threshold_runs', 'directrna_salmon_threshold_runs'])
    c = c.merge(q, on='stable_id', validate='one_to_one')
    c['phenotype_category'] = c.apply(category, axis=1)
    with FOLDS.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['status', 'stable_id', 'sequence_cluster_id', 'fold'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for row in c.sort_values('stable_id').itertuples(index=False):
            writer.writerow({'status': 'FROZEN_PHASE3D', 'stable_id': row.stable_id,
                             'sequence_cluster_id': row.sequence_cluster_id, 'fold': row.fold})
    with COHORT.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['cohort_status', 'stable_id', 'fold'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for row in c.sort_values('stable_id').itertuples(index=False):
            writer.writerow({'cohort_status': 'FINAL_WORKFLOW_SPECIFIC', 'stable_id': row.stable_id, 'fold': row.fold})
    balance = []
    for fold, z in c.groupby('fold'):
        counts = z.phenotype_category.value_counts()
        balance.append({'fold': int(fold), 'n_transcripts': len(z),
                        'n_sequence_clusters': z.sequence_cluster_id.nunique(),
                        'n_genes': z.gene_id.nunique(),
                        'n_both': int(counts.get('BOTH', 0)),
                        'n_illumina_only': int(counts.get('ILLUMINA_ONLY', 0)),
                        'n_directrna_only': int(counts.get('DIRECT_RNA_ONLY', 0)),
                        'n_neither': int(counts.get('NEITHER', 0)),
                        'n_indeterminate': int(counts.get('INDETERMINATE', 0)),
                        'seed': SEED, 'structure_inputs_read': False, 'longbench_inputs_read': False})
    pd.DataFrame(balance).sort_values('fold').to_csv(BALANCE, sep='\t', index=False)
    cohort_hash = hashlib.sha256(COHORT.read_bytes()).hexdigest()
    fold_hash = hashlib.sha256(FOLDS.read_bytes()).hexdigest()
    print(json.dumps({'n_transcripts': len(c), 'n_groups': len(groups), 'fold_sizes': fold_sizes,
                      'seed': SEED, 'cohort_sha256': cohort_hash, 'fold_sha256': fold_hash,
                      'structure_inputs_read': False, 'longbench_inputs_read': False}, indent=2))


if __name__ == '__main__': main()
