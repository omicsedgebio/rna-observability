#!/usr/bin/env python3
"""Structure-blind SG-NEx quantifier audit on a fixed Ensembl 91 annotation."""
import json
from pathlib import Path
import sys

import duckdb
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.cache/phase3a/qc/k562_quantification.tsv'
ANNOTATION = ROOT / '.cache/phase3a/qc/sgnex_annotation_full.tsv'
DB = ROOT / '.cache/phase3c/quantifiers.duckdb'
OUT = ROOT / 'results/tables/quantifier_concordance.tsv'
SUMMARY = ROOT / 'results/tables/quantifier_audit_summary.json'


def correlation(a, b):
    keep = np.isfinite(a) & np.isfinite(b)
    if keep.sum() < 3 or len(np.unique(a[keep])) < 2 or len(np.unique(b[keep])) < 2:
        return None
    return float(spearmanr(a[keep], b[keep]).statistic)


def compare(left, right, threshold, row_type, platform, method1, method2,
            run1, run2, stratum='all', level='all'):
    z = pd.concat([left.rename('a'), right.rename('b')], axis=1)
    both = z.dropna()
    a, b = both.a.to_numpy(), both.b.to_numpy()
    result = dict(row_type=row_type, platform=platform, method1=method1,
        method2=method2, run1=run1, run2=run2, stratum=stratum, level=str(level),
        n_union=len(z), n_common=len(both), n_positive_both=int(((a>0)&(b>0)).sum()),
        spearman_rank=correlation(a,b),
        positive_call_agreement=float(((a>0)==(b>0)).mean()) if len(both) else None,
        threshold_TPM=threshold)
    if threshold is not None and len(both):
        ca, cb = a>=threshold, b>=threshold
        result.update(threshold_call_agreement=float((ca==cb).mean()),
                      both_detected=int((ca&cb).sum()), first_only=int((ca&~cb).sum()),
                      second_only=int((~ca&cb).sum()), neither=int((~ca&~cb).sum()))
    else:
        result.update(threshold_call_agreement=None, both_detected=None,
                      first_only=None, second_only=None, neither=None)
    return result


def main():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB))
    con.execute("PRAGMA threads=4")
    con.execute("PRAGMA memory_limit='6GB'")
    if not con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='ann'").fetchone()[0]:
        con.execute("CREATE TABLE ann AS SELECT tx_name AS stable, ensembl_gene_id AS gene, "
                    "CAST(tx_len AS INTEGER) AS length_nt, CAST(nexon AS INTEGER) AS exon_count "
                    "FROM read_csv(?, delim='\\t', header=true)", [str(ANNOTATION)])
        con.execute("CREATE TABLE q AS SELECT regexp_replace(tx_name, '\\.[0-9]+', '') AS stable, "
                    "tx_name, runname, method, protocol_general, CAST(normEst AS DOUBLE) AS value, "
                    "CAST(estimates AS DOUBLE) AS estimates "
                    "FROM read_csv(?, delim='\\t', header=true)", [str(SOURCE)])
    if con.execute('SELECT count(*) FROM (SELECT stable,runname,method FROM q WHERE starts_with(stable,\'ENST\') GROUP BY ALL HAVING count(*)>1)').fetchone()[0]:
        raise ValueError('Duplicate stable transcript/method/run keys')
    ann = con.execute('SELECT stable, gene, length_nt, exon_count, '
                      'count(*) OVER (PARTITION BY gene) AS isoforms_per_gene FROM ann').df()
    if ann.stable.duplicated().any():
        raise ValueError('Duplicate stable transcript annotation')
    annotation = ann.set_index('stable')
    run_stats = con.execute("SELECT protocol_general, method, runname, count(*) AS rows, "
        "count(*) FILTER (WHERE value>0) AS nonzero_rows, "
        "count(*) FILTER (WHERE starts_with(stable,'ENST')) AS enst_rows, "
        "count(*) FILTER (WHERE starts_with(stable,'BambuTx')) AS bambu_novel_rows, "
        "sum(value) AS sum_value FROM q GROUP BY ALL ORDER BY method,runname").df()
    run_stats.to_csv(ROOT / 'results/tables/quantifier_run_inventory.tsv', sep='\t', index=False)
    required = {
        'Illumina': ['salmon_sr', 'rsem_sr'],
        'directRNA': ['salmon_lr', 'NanoCount_lr', 'bambu_lr'],
    }
    matrices = {}
    for platform, methods in required.items():
        for method in methods:
            frame = con.execute("SELECT stable, runname, value FROM q WHERE method=? AND "
                "protocol_general=? AND starts_with(stable,'ENST')", [method,platform]).df()
            if not frame.empty:
                frame = frame.loc[frame.stable.isin(annotation.index)]
                matrices[(platform,method)] = frame.pivot(index='stable',columns='runname',values='value')
    records = []
    for (platform,method), matrix in matrices.items():
        columns = list(matrix)
        for i, left in enumerate(columns):
            records.append(dict(row_type='method_run_inventory', platform=platform, method1=method,
                method2='NA', run1=left, run2='NA', stratum='all', level='all',
                n_union=len(annotation), n_common=int(matrix[left].notna().sum()),
                n_positive_both=int((matrix[left]>0).sum()), spearman_rank=None,
                positive_call_agreement=None, threshold_TPM=None,
                threshold_call_agreement=None, both_detected=None, first_only=None,
                second_only=None, neither=None))
            for right in columns[i+1:]:
                # Bambu normEst is CPM-like in this processed object, whereas
                # Salmon/RSEM values are TPM-like.  Do not label CPM cutoffs
                # as TPM thresholds in the within-method audit.
                thresholds = [None] if method == 'bambu_lr' else [0.1, 1.0, 5.0]
                for threshold in thresholds:
                    records.append(compare(matrix[left],matrix[right],threshold,
                        'within_method_replicates',platform,method,method,left,right))
    for platform, methods in required.items():
        for i, method1 in enumerate(methods):
            for method2 in methods[i+1:]:
                a = matrices.get((platform,method1))
                b = matrices.get((platform,method2))
                if a is None or b is None:
                    continue
                for run in set(a).intersection(b):
                    # Bambu values are CPM-like, not TPM. Only rank and >0
                    # assignment can be compared to TPM without calibration.
                    comparable_tpm = method1!='bambu_lr' and method2!='bambu_lr'
                    for threshold in ([0.1,1.0,5.0] if comparable_tpm else [None]):
                        records.append(compare(a[run],b[run],threshold,
                            'same_run_cross_quantifier',platform,method1,method2,run,run))
                    if comparable_tpm:
                        left = a[run]; right = b[run]
                        independent = matrices.get(('Illumina','salmon_sr'))
                        source = independent['GIS_K562_Illumina_Rep3-Run1'] if independent is not None else None
                        if source is not None:
                            strata = {
                                'independent_abundance_TPM': pd.cut(source,[-1e-10,0,.1,1,10,100,float('inf')]),
                                'transcript_length_nt': pd.cut(annotation.length_nt,[0,500,1000,2000,5000,10000,float('inf')]),
                                'isoforms_per_gene': pd.cut(annotation.isoforms_per_gene,[0,1,2,5,10,20,float('inf')]),
                            }
                            for dimension, groups in strata.items():
                                for level in groups.dropna().unique():
                                    ids=groups.index[groups==level]
                                    records.append(compare(left.reindex(ids),right.reindex(ids),1.0,
                                        'cross_quantifier_stratum',platform,method1,method2,run,run,
                                        dimension,level))
    # Use explicit NA tokens so committed TSV rows are rectangular without
    # trailing tab whitespace and missing sparse-output values remain explicit.
    table = pd.DataFrame(records).fillna('NA')
    table.to_csv(OUT, sep='\t', index=False)
    summary = dict(annotation_transcripts=len(annotation), k562_rows=int(con.execute('SELECT count(*) FROM q').fetchone()[0]),
        workflows={f'{p}:{m}':dict(transcripts=len(z),runs=len(z.columns)) for (p,m),z in matrices.items()},
        bambu_novel_output_rows=int(run_stats.bambu_novel_rows.sum()),
        structure_inputs_read=False, longbench_inputs_read=False,
        source='SG-NEx K562 processed quantification only', duckdb_version=duckdb.__version__,
        pandas_version=pd.__version__, scipy_version=__import__('scipy').__version__)
    SUMMARY.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
