#!/usr/bin/env python3
"""GSE132099 availability diagnostic; IDs/masks and independent abundance only."""
import csv
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rnaobs.core import stable_id


def main():
    columns = ['transcript_id', 'stable_transcript_id', 'gene_id', 'sequence_length',
               'gc_fraction', 'isoforms_per_gene', 'exon_count', 'unique_kmer_fraction']
    feature = pd.read_csv(ROOT / 'results/tables/identifiability_sequence_features.tsv',
                          sep='\t', usecols=columns)
    eligible = {r['ensembl91_sgnex_transcript_id'] for r in csv.DictReader(
        (ROOT / 'results/tables/ensembl88_to_91_transcript_bridge.tsv').open(), delimiter='\t')
        if r['primary_eligible'] == 'True'}
    feature['usable'] = feature.transcript_id.isin(eligible)
    run = 'GIS_K562_Illumina_Rep3-Run1'
    abundance = []
    for chunk in pd.read_csv(ROOT / '.cache/phase3a/qc/k562_quantification.tsv',
                             sep='\t', usecols=['tx_name', 'normEst', 'runname', 'method'], chunksize=500000):
        z = chunk.loc[(chunk.runname == run) & (chunk.method == 'salmon_sr') & chunk.tx_name.notna(),
                      ['tx_name', 'normEst']].copy()
        z['stable_transcript_id'] = z.tx_name.map(stable_id)
        abundance.append(z[['stable_transcript_id', 'normEst']])
    abundance = pd.concat(abundance)
    if abundance.stable_transcript_id.duplicated().any():
        raise ValueError('Duplicate independent abundance source')
    abundance = abundance.loc[abundance.stable_transcript_id.isin(set(feature.stable_transcript_id))].copy()
    abundance['tpm'] = abundance.normEst / abundance.normEst.sum() * 1e6
    data = feature.merge(abundance[['stable_transcript_id', 'tpm']],
                         on='stable_transcript_id', how='left', validate='1:1')
    data = data.dropna(subset=['tpm', 'gc_fraction', 'unique_kmer_fraction']).copy()
    data['log_abundance'] = np.log1p(data.tpm)
    data['log_length'] = np.log1p(data.sequence_length)
    data['log_isoforms'] = np.log1p(data.isoforms_per_gene)
    x = data[['log_abundance', 'log_length', 'gc_fraction', 'log_isoforms',
              'exon_count', 'unique_kmer_fraction']]
    scaled = StandardScaler().fit_transform(x)
    fit = LogisticRegression(C=1, max_iter=500, tol=1e-6)
    fit.fit(scaled, data.usable)
    data['fitted_p'] = fit.predict_proba(scaled)[:, 1]
    boundaries = {
        'independent_abundance_TPM': ('tpm', [-1e-10, 0, .1, 1, 10, 100, np.inf]),
        'length_nt': ('sequence_length', [0, 500, 1000, 2000, 5000, 10000, np.inf]),
        'gc_fraction': ('gc_fraction', [-.01, .3, .4, .5, .6, .7, 1.01]),
        'isoforms_per_gene': ('isoforms_per_gene', [0, 1, 2, 5, 10, 20, np.inf]),
        'unique_31mer_fraction': ('unique_kmer_fraction', [-.01, 0, .01, .05, .2, .5, 1.01]),
    }
    rows = []
    for name, (column, bins) in boundaries.items():
        for interval, z in data.groupby(pd.cut(data[column], bins), observed=True):
            rows.append(dict(dimension=name, level=str(interval), transcripts=len(z),
                             usable=int(z.usable.sum()), usable_fraction=float(z.usable.mean()),
                             mean_fitted_probability=float(z.fitted_p.mean())))
    pd.DataFrame(rows).to_csv(ROOT / 'results/tables/gse132099_missingness_strata.tsv', sep='\t', index=False)
    high = data[(data.tpm >= 1) & (data.sequence_length.between(500, 5000)) &
                (data.gc_fraction.between(.3, .7))]
    observed = data.loc[data.usable, 'fitted_p']
    weights = 1 / observed
    summary = dict(sequence_validated_universe=len(feature), adjusted_universe=len(data),
                   usable=int(data.usable.sum()), usable_fraction=float(data.usable.mean()),
                   independent_abundance_TPM_ge1=int((data.tpm>=1).sum()),
                   usable_with_independent_abundance_TPM_ge1=int((data.usable & (data.tpm>=1)).sum()),
                   high_overlap_descriptive_stratum_n=len(high),
                   high_overlap_descriptive_stratum_usable=int(high.usable.sum()),
                   high_overlap_descriptive_stratum_usable_fraction=float(high.usable.mean()),
                   fitted_probability_below_0_05_fraction=float((data.fitted_p<.05).mean()),
                   fitted_probability_below_0_01_fraction=float((data.fitted_p<.01).mean()),
                   naive_ipw_max=float(weights.max()),
                   naive_ipw_effective_sample_size=float(weights.sum()**2/(weights**2).sum()),
                   model='standardized_ridge_logistic_C1_descriptive',
                   model_converged=bool(fit.n_iter_[0]<500),
                   predictors=list(x.columns), reactivity_values_read=False,
                   sequencing_outcomes_read=False)
    (ROOT / 'results/tables/gse132099_missingness_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
