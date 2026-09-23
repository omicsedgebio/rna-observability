#!/usr/bin/env python3
"""Structure-blind K562 detection and conditional-abundance measurement QC."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.cache/phase3a/qc/k562_quantification.tsv'
OUT = ROOT / 'results/tables/zero_aware_threshold_qc.tsv'
SUMMARY = ROOT / 'results/tables/zero_aware_endpoint_summary.json'


def statuses(matrix, threshold, support):
    hits = (matrix >= threshold).sum(axis=1)
    return np.select([hits >= support, hits == 0], ['detected', 'absent'], default='indeterminate')


def category(a, b):
    return np.select([(a == 'indeterminate') | (b == 'indeterminate'),
                      (a == 'detected') & (b == 'detected'),
                      (a == 'detected') & (b == 'absent'),
                      (a == 'absent') & (b == 'detected')],
                     ['indeterminate', 'both', 'illumina_only', 'direct_rna_only'],
                     default='neither')


def matrix_for(frame, method, columns):
    x = frame.loc[frame.method == method]
    x = x.loc[x.runname.isin(columns)]
    if x.duplicated(['tx_name', 'runname']).any():
        raise ValueError('Duplicate transcript/run measurement')
    z = x.pivot(index='tx_name', columns='runname', values='normEst')
    return z.reindex(columns=columns)


def main():
    names = pd.read_csv(ROOT / 'results/tables/sgnex_transcript_annotation.tsv',
                        sep='\t', usecols=['sgnex_transcript_id'])
    # Processed IDs sometimes omit version, so use Phase 3A's unique stable map.
    import sys
    sys.path.insert(0, str(ROOT / 'src'))
    from rnaobs.core import stable_id
    names['stable'] = names.sgnex_transcript_id.map(stable_id)
    if names.stable.duplicated().any():
        raise ValueError('Ambiguous stable IDs')
    allowed = set(names.stable)
    chunks = []
    for chunk in pd.read_csv(SOURCE, sep='\t', chunksize=500000,
                             usecols=['tx_name', 'normEst', 'runname', 'method']):
        chunk = chunk.loc[chunk.method.isin(['salmon_sr', 'salmon_lr', 'rsem_sr', 'NanoCount_lr']) & chunk.tx_name.notna()].copy()
        chunk['tx_name'] = chunk.tx_name.map(stable_id)
        chunks.append(chunk.loc[chunk.tx_name.isin(allowed)])
    frame = pd.concat(chunks, ignore_index=True)
    sr_runs = sorted(x for x in frame.loc[frame.method == 'salmon_sr', 'runname'].unique()
                     if 'k562' in x.lower() and 'Illumina' in x)
    dr_runs = sorted(x for x in frame.loc[frame.method == 'salmon_lr', 'runname'].unique()
                     if '_directRNA_' in x)
    covariate = 'GIS_K562_Illumina_Rep3-Run1'
    sr_out = [x for x in sr_runs if x != covariate]
    if len(sr_out) != 2 or len(dr_runs) != 4:
        raise ValueError(f'Unexpected K562 replicate counts: {sr_out}, {dr_runs}')
    sr = matrix_for(frame, 'salmon_sr', sr_out + [covariate])
    dr = matrix_for(frame, 'salmon_lr', dr_runs)
    common = sr.dropna().index.intersection(dr.dropna().index)
    sr = sr.loc[common]
    dr = dr.loc[common]
    # Fixed common transcript universe, separately closed per run.
    sr = sr.div(sr.sum(axis=0), axis=1) * 1e6
    dr = dr.div(dr.sum(axis=0), axis=1) * 1e6
    independent_expression = sr[covariate] >= 1
    sr2 = sr[sr_out]
    rows = []
    for threshold in [0.1, 1.0, 5.0]:
        for d_support in [2, 3, 4]:
            a = statuses(sr2, threshold, 2)
            b = statuses(dr, threshold, d_support)
            state = category(a, b)
            # Replicate disagreement is a measurement property only.
            ai = (sr2.to_numpy() >= threshold)
            di = (dr.to_numpy() >= threshold)
            sr_agree = float((ai[:, 0] == ai[:, 1])[independent_expression].mean())
            dr_pair_agree = float(np.mean([(di[:, i] == di[:, j])[independent_expression].mean()
                                          for i in range(4) for j in range(i+1, 4)]))
            all_ = pd.Series(state[independent_expression], dtype='string').value_counts()
            # Disjoint ONT pairs show whether a supported call survives a split.
            d12 = (di[:, :2].sum(axis=1) == 2)
            d34 = (di[:, 2:].sum(axis=1) == 2)
            split_agree = float((d12 == d34)[independent_expression].mean())
            rows.append(dict(threshold_TPM=threshold, illumina_min_support=2,
                             direct_rna_min_support=d_support,
                             independently_expressed=int(independent_expression.sum()),
                             illumina_pair_detection_agreement=sr_agree,
                             direct_rna_pair_detection_agreement=dr_pair_agree,
                             direct_rna_disjoint_pair_call_agreement=split_agree,
                             **{k: int(all_.get(k, 0)) for k in
                                ['both', 'illumina_only', 'direct_rna_only', 'neither', 'indeterminate']}))
    pd.DataFrame(rows).to_csv(OUT, sep='\t', index=False)
    primary_threshold = 1.0
    aa = statuses(sr2, primary_threshold, 2)
    dd = statuses(dr, primary_threshold, 3)
    state = category(aa, dd)
    both = (state == 'both') & independent_expression.to_numpy()
    # Conditional outcome is evaluated only on strictly positive replicate values.
    positive_all = both & (sr2.to_numpy() > 0).all(axis=1) & (dr.to_numpy() > 0).all(axis=1)
    rank_sr = sr2.rank(pct=True).median(axis=1)
    rank_dr = dr.rank(pct=True).median(axis=1)
    rank_delta = rank_dr - rank_sr
    # Alternative quantifiers have different zero/missing semantics. Compare
    # only rows explicitly present in their output; never fill absent rows.
    rsem = matrix_for(frame, 'rsem_sr', sr_out)
    rsem_common = common.intersection(rsem.dropna().index)
    rsem = rsem.loc[rsem_common]
    rsem = rsem.div(rsem.sum(axis=0), axis=1) * 1e6
    rsem_status = statuses(rsem, primary_threshold, 2)
    salmon_status_rsem = statuses(sr2.loc[rsem_common], primary_threshold, 2)
    nc = matrix_for(frame, 'NanoCount_lr', dr_runs)
    nc_common = common.intersection(nc.dropna().index)
    nc = nc.loc[nc_common]
    nc = nc.div(nc.sum(axis=0), axis=1) * 1e6
    nc_status = statuses(nc, primary_threshold, 3)
    salmon_status_nc = statuses(dr.loc[nc_common], primary_threshold, 3)
    summary = dict(common_quantified_transcripts=len(common), independent_expression_count=int(independent_expression.sum()),
                   selected_threshold_TPM=primary_threshold, selected_illumina_support='2_of_2',
                   selected_direct_rna_support='3_of_4', selected_category_counts={k: int((state[independent_expression] == k).sum()) for k in
                   ['both', 'illumina_only', 'direct_rna_only', 'neither', 'indeterminate']},
                   both_with_all_positive_replicates=int(positive_all.sum()),
                   conditional_rank_delta_median=float(rank_delta.iloc[np.where(both)[0]].median()),
                   conditional_rank_delta_iqr=[float(rank_delta.iloc[np.where(both)[0]].quantile(q)) for q in [.25, .75]],
                   rsem_complete_rows=len(rsem_common),
                   rsem_vs_salmon_illumina_status_agreement=float(np.mean(rsem_status == salmon_status_rsem)),
                   nanocount_complete_rows=len(nc_common),
                   nanocount_vs_salmon_direct_rna_status_agreement_on_complete_rows=float(np.mean(nc_status == salmon_status_nc)) if len(nc_common) else None,
                   independent_abundance_run=covariate, illumina_outcome_runs=sr_out,
                   direct_rna_outcome_runs=dr_runs, structure_input_used=False,
                   transcript_level_outcomes_written=False)
    SUMMARY.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
