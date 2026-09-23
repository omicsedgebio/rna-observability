#!/usr/bin/env python3
"""Calibrate candidate measurement summaries against SG-NEx synthetic truth.

This is a descriptive, spike-in-only analysis. It does not claim that spike-in
behavior is endogenous RNA error and does not read icSHAPE or LongBench data.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / '.cache/phase3a/qc/spike_truth.tsv'
INPUT = ROOT / '.cache/phase3a/qc/spikein_synthetic_1.tsv'
OUT = ROOT / 'results/tables/spikein_endpoint_calibration.tsv'


def mix(name):
    return re.sub(r'^allSpikinReadsCombined_', '', name).rsplit('_', 1)[0]


def main():
    truth = pd.read_csv(TRUTH, sep='\t').drop_duplicates('tx_name')
    truth = truth.loc[truth.conc.gt(0), ['tx_name', 'conc', 'spike_in']]
    q = pd.read_csv(INPUT, sep='\t')
    q['mix'] = q.runname.map(mix)
    rows = []
    for (run, method, protocol, mx), z in q.groupby(['runname', 'method', 'protocol', 'mix']):
        x = truth.merge(z[['tx_name', 'estimates', 'normEst']], on='tx_name', how='left')
        # A missing sparse-output row is missing, not a zero observation.
        observed = x.estimates.notna()
        positive = observed & x.estimates.gt(0)
        true = x.conc / x.conc.sum()
        for value_name in ['estimates', 'normEst']:
            value = x[value_name]
            ok = value.notna() & value.gt(0)
            pred = value / value[ok].sum() if ok.any() else value
            log_error = np.log10(pred[ok] / true[ok]) if ok.any() else pd.Series(dtype=float)
            rho = spearmanr(true[ok], pred[ok]).statistic if ok.sum() > 2 and true[ok].nunique() > 1 and pred[ok].nunique() > 1 else np.nan
            rows.append(dict(runname=run, mix=mx, protocol=protocol, method=method,
                quantity=value_name, n_truth=len(x), n_rows_observed=int(observed.sum()),
                n_positive=int(positive.sum()), observed_fraction=float(observed.mean()),
                positive_fraction=float(positive.mean()),
                rank_spearman=float(rho) if np.isfinite(rho) else np.nan,
                median_abs_log10_relative_error=float(np.median(np.abs(log_error))) if len(log_error) else np.nan,
                median_signed_log10_relative_error=float(np.median(log_error)) if len(log_error) else np.nan,
                truth_source='SG-NEx spikein.rds via phase3a spike_truth.tsv',
                missing_sparse_rows_are_not_zero=True))
    pd.DataFrame(rows).to_csv(OUT, sep='\t', index=False)
    print(f'rows={len(rows)} output={OUT}')


if __name__ == '__main__':
    main()
