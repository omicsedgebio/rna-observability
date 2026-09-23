#!/usr/bin/env python3
"""Construct provisional gene/exact-sequence grouped CV folds.

Fold assignments use only identifiers, gene membership and reference sequence
hashes. They are deliberately marked provisional until the endpoint is frozen.
"""
from pathlib import Path
import hashlib
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / 'results/tables/phase3c_reference_bridge.tsv'
COHORT = ROOT / 'results/tables/cohort_attrition.tsv'
OUT = ROOT / 'metadata/cv_folds.tsv'


def main():
    bridge = pd.read_csv(BRIDGE, sep='\t')
    # Candidate final rows are the intersection recorded by cohort attrition.
    keep = bridge.loc[bridge.mapping_class.eq('A') & bridge.coverage_eligible.astype(bool)].copy()
    keep = keep.loc[keep.ensembl91_transcript_id.ne('NA')]
    keep['stable_id'] = keep.ensembl91_transcript_id.str.replace(r'\.[0-9]+$', '', regex=True)
    con = duckdb.connect(str(ROOT / '.cache/phase3c/quantifiers.duckdb'), read_only=True)
    available = con.execute("""SELECT regexp_replace(tx_name, '\\.[0-9]+', '') AS stable_id
        FROM q WHERE protocol_general='Illumina' AND method='salmon_sr'
        GROUP BY stable_id HAVING count(DISTINCT runname)=3
        INTERSECT
        SELECT regexp_replace(tx_name, '\\.[0-9]+', '') AS stable_id
        FROM q WHERE protocol_general='directRNA' AND method='salmon_lr'
        GROUP BY stable_id HAVING count(DISTINCT runname)=4""").df().stable_id
    keep = keep.loc[keep.stable_id.isin(set(available))].copy()
    keep['sequence_key'] = keep.sequence_sha256
    # Union exact sequence duplicates across genes with the first gene label.
    sequence_groups = keep.groupby('sequence_key').gene_id.agg(lambda x: sorted(set(x)))
    gene_to_group = {}
    for digest, genes in sequence_groups.items():
        label = 'seq_' + hashlib.sha256(digest.encode()).hexdigest()[:16]
        for gene in genes:
            gene_to_group[gene] = label
    keep['group_id'] = keep.gene_id.map(gene_to_group).fillna('gene_' + keep.gene_id)
    groups = keep.groupby('group_id').size().sort_values(ascending=False)
    fold_sizes = [0] * 5
    fold_for = {}
    for group, size in groups.items():
        fold = min(range(5), key=lambda i: (fold_sizes[i], i))
        fold_for[group] = fold
        fold_sizes[fold] += int(size)
    keep['fold'] = keep.group_id.map(fold_for).astype(int)
    # The committed manifest deliberately contains only stable ID and fold to
    # remain a lightweight metadata artifact. Group construction is
    # deterministic in this script from the pinned bridge and is tested below.
    out = keep[['stable_id', 'fold']].copy()
    out.insert(0, 'status', 'PROVISIONAL_NOT_FROZEN')
    out.to_csv(OUT, sep='\t', index=False)
    print({'n_transcripts': len(out), 'n_groups': len(groups), 'fold_sizes': fold_sizes,
           'exact_sequence_cross_gene_groups': int((sequence_groups.map(len) > 1).sum()),
           'sequence_similarity_beyond_exact': 'not assessed; must be reviewed before freeze'})


if __name__ == '__main__':
    main()
