#!/usr/bin/env python3
"""Transcript-level, structure-blind quantifier agreement audit for Phase 3D."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / '.cache/phase3c/quantifiers.duckdb'
COHORT = ROOT / 'metadata/final_transcript_cohort.tsv'
OUT = ROOT / 'results/tables/phase3d_quantifier_agreement.tsv'
SUMMARY = ROOT / 'results/tables/phase3d_quantifier_agreement_summary.tsv'

ILL_OUTCOME = ['GIS_K562_Illumina_Rep4-Run1', 'GIS_k562_Illumina_Rep5-Run1']
DR_RUNS = [
    'SGNex_K562_directRNA_replicate1_run1',
    'SGNex_K562_directRNA_replicate4_run1',
    'SGNex_K562_directRNA_replicate5_run1',
    'SGNex_K562_directRNA_replicate6_run1',
]


def kappa(a, b):
    a = np.asarray(a, dtype=bool); b = np.asarray(b, dtype=bool)
    if len(a) == 0:
        return np.nan
    po = np.mean(a == b)
    pa = np.mean(a); pb = np.mean(b)
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float((po - pe) / (1 - pe)) if pe < 1 else np.nan


def summary_pair(frame, left, right, label, strata='all'):
    z = frame[[left, right]].dropna()
    if not len(z):
        return None
    a = z[left].astype(bool).to_numpy(); b = z[right].astype(bool).to_numpy()
    return dict(pair=label, stratum=strata, n_transcripts=len(z),
                percent_concordance=float(np.mean(a == b)), cohen_kappa=kappa(a, b),
                left_positive_fraction=float(a.mean()), right_positive_fraction=float(b.mean()),
                structure_inputs_read=False, sequencing_outcomes_read=False)


def main():
    con = duckdb.connect(str(DB), read_only=True)
    ann = con.execute("""SELECT stable, gene, length_nt, exon_count,
        count(*) OVER (PARTITION BY gene) AS isoforms_per_gene FROM ann""").df()
    q = con.execute("""SELECT stable, tx_name, runname, method, protocol_general,
        value FROM q WHERE starts_with(stable, 'ENST')""").df()
    cohort = pd.read_csv(COHORT, sep='\t', usecols=['stable_id'])
    cohort = set(cohort.stable_id)
    ann = ann.loc[ann.stable.isin(cohort)].drop_duplicates('stable').set_index('stable')
    rows = pd.DataFrame(index=sorted(cohort))
    for platform, method, prefix, runs in [
        ('Illumina', 'salmon_sr', 'illumina_salmon', ILL_OUTCOME),
        ('Illumina', 'rsem_sr', 'illumina_rsem', ILL_OUTCOME),
        ('directRNA', 'salmon_lr', 'directrna_salmon', DR_RUNS),
        ('directRNA', 'NanoCount_lr', 'directrna_nanocount', DR_RUNS),
        ('directRNA', 'bambu_lr', 'directrna_bambu', DR_RUNS),
    ]:
        z = q.loc[q.protocol_general.eq(platform) & q.method.eq(method) & q.runname.isin(runs)]
        if z.empty:
            continue
        p = z.pivot_table(index='stable', columns='runname', values='value', aggfunc='first').reindex(rows.index)
        p = p.reindex(columns=runs)
        rows[prefix + '_present_runs'] = p.notna().sum(axis=1).astype(int)
        rows[prefix + '_positive_runs'] = (p > 0).sum(axis=1).astype(int)
        rows[prefix + '_median_value'] = p.median(axis=1)
        # TPM-like thresholds are used only for Salmon/RSEM. Bambu and
        # NanoCount are reported on positive assignment/presence semantics.
        if method in ('salmon_sr', 'rsem_sr', 'salmon_lr'):
            rows[prefix + '_threshold_runs'] = (p >= 1).sum(axis=1).astype(int)
        else:
            rows[prefix + '_threshold_runs'] = np.nan
    rows = rows.join(ann[['gene', 'length_nt', 'exon_count', 'isoforms_per_gene']])
    rows['length_stratum'] = pd.cut(rows.length_nt, [0, 500, 1000, 2000, 5000, 10000, np.inf], right=True).astype(str)
    rows['isoform_stratum'] = pd.cut(rows.isoforms_per_gene, [0, 1, 2, 5, 10, 20, np.inf], right=True).astype(str)
    rows['illumina_salmon_detected'] = rows.illumina_salmon_threshold_runs >= 2
    rows['illumina_rsem_detected'] = rows.illumina_rsem_threshold_runs >= 2
    rows['directrna_salmon_detected'] = rows.directrna_salmon_threshold_runs >= 3
    rows['directrna_bambu_positive_supported'] = rows.directrna_bambu_positive_runs >= 3
    rows['directrna_nanocount_positive_supported'] = rows.directrna_nanocount_positive_runs >= 3
    rows.index.name = 'stable_id'
    rows.to_csv(OUT, sep='\t', na_rep='NA')

    metrics = []
    for left, right, label in [
        ('illumina_salmon_detected', 'illumina_rsem_detected', 'Illumina_Salmon_vs_RSEM_2of2_TPM1'),
        ('directrna_salmon_detected', 'directrna_bambu_positive_supported', 'directRNA_Salmon_vs_Bambu_3of4_positive'),
        ('directrna_salmon_detected', 'directrna_nanocount_positive_supported', 'directRNA_Salmon_vs_NanoCount_3of4_common'),
    ]:
        if label.endswith('common'):
            avail = rows.directrna_nanocount_present_runs.eq(4)
            x = rows.loc[avail]
        else:
            x = rows
        all_metric = summary_pair(x, left, right, label)
        if all_metric: metrics.append(all_metric)
        for column, name in [('length_stratum', 'length'), ('isoform_stratum', 'isoforms')]:
            for level, y in x.groupby(column, observed=True):
                item = summary_pair(y, left, right, label, f'{name}:{level}')
                if item: metrics.append(item)
    pd.DataFrame(metrics).to_csv(SUMMARY, sep='\t', index=False, na_rep='NA')
    print(json.dumps({'cohort_transcripts': len(rows), 'agreement_rows': len(metrics),
                      'output': str(OUT), 'summary': str(SUMMARY),
                      'structure_inputs_read': False, 'longbench_inputs_read': False}, indent=2))


if __name__ == '__main__':
    main()
