#!/usr/bin/env python3
"""Outcome measurement QC with no structure file, feature or availability input."""
from pathlib import Path
import json
import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from rnaobs.core import stable_id


def main():
    x = pd.read_csv('.cache/phase3a/qc/k562_quantification.tsv', sep='\t')
    ann = pd.read_csv('results/tables/sgnex_transcript_annotation.tsv', sep='\t')
    ann['stable'] = ann.sgnex_transcript_id.map(stable_id)
    if ann.stable.duplicated().any():
        raise ValueError('Ambiguous SG-NEx stable IDs')
    genes=ann.set_index('stable').gene_id
    human=set(genes.index)
    missing_transcript_rows=int(x.tx_name.isna().sum())
    x=x[x.tx_name.notna()].copy()
    x['stable'] = x.tx_name.map(stable_id)
    x = x[x.stable.isin(human)].copy()
    if x.duplicated(['stable','runname','method']).any():
        raise ValueError('Duplicate measurement key')
    matrices={method:z.pivot(index='stable',columns='runname',values='normEst')
              for method,z in x.groupby('method')}
    sr=matrices['salmon_sr']; lr=matrices['salmon_lr']
    drna_cols=[c for c in lr if '_directRNA_' in c]
    covariate_run='GIS_K562_Illumina_Rep3-Run1'
    outcome_sr=[c for c in sr if c!=covariate_run]
    complete=sr.dropna().index.intersection(lr[drna_cols].dropna().index)
    # Defined by quantifier output availability only, never by detection or structure.
    sr=sr.loc[complete]; drna=lr.loc[complete,drna_cols]
    sr=sr.div(sr.sum(axis=0),axis=1)*1e6
    drna=drna.div(drna.sum(axis=0),axis=1)*1e6
    covariate=sr[covariate_run]
    eligible=covariate>=1
    # Endpoint evaluation includes all available reference rows; eligibility subset
    # is reported separately and never deletes genuine platform zero values.
    primary=np.log2(drna+0.1).median(axis=1)-np.log2(sr[outcome_sr]+0.1).median(axis=1)
    full=np.log2(drna+0.1).median(axis=1)-np.log2(sr+0.1).median(axis=1)
    summaries=[]
    def add(label, values, mask=eligible):
        z=values[mask]
        summaries.append(dict(candidate=label,n=len(z),median=float(z.median()),
                              q05=float(z.quantile(.05)),q95=float(z.quantile(.95)),
                              spearman_with_primary=float(spearmanr(primary[mask],z).statistic),
                              spearman_with_independent_abundance=float(spearmanr(covariate[mask],z).statistic)))
    add('signed_log2_offset_0.1',primary)
    add('absolute_log2_offset_0.1',primary.abs())
    add('signed_all_Illumina_libraries_descriptive',full)
    for offset in [.01,1.0]:
        add(f'signed_log2_offset_{offset}',np.log2(drna+offset).median(axis=1)-np.log2(sr[outcome_sr]+offset).median(axis=1))
    add('detection_gt0_fraction_difference',(drna>0).mean(axis=1)-(sr[outcome_sr]>0).mean(axis=1))
    add('detection_ge1_TPM_fraction_difference',(drna>=1).mean(axis=1)-(sr[outcome_sr]>=1).mean(axis=1))
    rank=drna.rank(pct=True).median(axis=1)-sr[outcome_sr].rank(pct=True).median(axis=1)
    add('percentile_rank_difference',rank)
    gene=genes.loc[complete]
    fd=drna.div(drna.groupby(gene).transform('sum').replace(0,np.nan))
    fs=sr[outcome_sr].div(sr[outcome_sr].groupby(gene).transform('sum').replace(0,np.nan))
    fraction=fd.median(axis=1)-fs.median(axis=1)
    add('isoform_fraction_difference',fraction,eligible & fraction.notna())
    for method in ['rsem_sr','NanoCount_lr','bambu_lr']:
        matrix=matrices[method]
        cols=outcome_sr if method=='rsem_sr' else [c for c in matrix if '_directRNA_' in c]
        sensitivity_ids=complete.intersection(matrix[cols].dropna().index)
        values=matrix.loc[sensitivity_ids,cols]
        values=values.div(values.sum(axis=0),axis=1)*1e6
        if method=='rsem_sr':
            comparison=np.log2(drna.loc[sensitivity_ids]+.1).median(axis=1)-np.log2(values+.1).median(axis=1)
        else:
            comparison=np.log2(values+.1).median(axis=1)-np.log2(sr.loc[sensitivity_ids,outcome_sr]+.1).median(axis=1)
        # Recompute Salmon comparator on EXACT sensitivity rows and closure.
        d=drna.loc[sensitivity_ids]; d=d.div(d.sum(axis=0),axis=1)*1e6
        s=sr.loc[sensitivity_ids,outcome_sr]; s=s.div(s.sum(axis=0),axis=1)*1e6
        ref=np.log2(d+.1).median(axis=1)-np.log2(s+.1).median(axis=1)
        if method=='rsem_sr': comparison=np.log2(d+.1).median(axis=1)-np.log2(values+.1).median(axis=1)
        else: comparison=np.log2(values+.1).median(axis=1)-np.log2(s+.1).median(axis=1)
        mask=covariate.loc[sensitivity_ids]>=1
        summaries.append(dict(candidate='quantifier_'+method,n=int(mask.sum()),
                              median=float(comparison[mask].median()),q05=float(comparison[mask].quantile(.05)),
                              q95=float(comparison[mask].quantile(.95)),
                              spearman_with_primary=float(spearmanr(ref[mask],comparison[mask]).statistic),
                              spearman_with_independent_abundance=float(spearmanr(covariate.loc[sensitivity_ids][mask],comparison[mask]).statistic)))
    pd.DataFrame(summaries).to_csv('results/tables/outcome_candidate_qc.tsv',sep='\t',index=False)
    repeat=[]
    for platform,matrix in [('Illumina',sr),('directRNA',drna)]:
        for i,c in enumerate(matrix):
            for d in list(matrix)[i+1:]:
                repeat.append(dict(platform=platform,run1=c,run2=d,n=int(eligible.sum()),
                    spearman=float(spearmanr(matrix.loc[eligible,c],matrix.loc[eligible,d]).statistic),
                    median_abs_log_difference=float((np.log2(matrix.loc[eligible,c]+.1)-np.log2(matrix.loc[eligible,d]+.1)).abs().median())))
    pd.DataFrame(repeat).to_csv('results/tables/replicate_outcome_qc.tsv',sep='\t',index=False)
    # Two disjoint sets of protocol libraries: not presumed matched aliquots.
    contrasts=[]
    for i,d in enumerate(drna_cols):
        for j,e in enumerate(drna_cols):
            if i>=j: continue
            for reverse in [False,True]:
                s1,s2=outcome_sr[::-1] if reverse else outcome_sr
                a=np.log2(drna[d]+.1)-np.log2(sr[s1]+.1)
                b=np.log2(drna[e]+.1)-np.log2(sr[s2]+.1)
                contrasts.append(dict(dRNA1=d,dRNA2=e,Illumina1=s1,Illumina2=s2,
                    spearman=float(spearmanr(a[eligible],b[eligible]).statistic),
                    sign_agreement=float((np.sign(a[eligible])==np.sign(b[eligible])).mean())))
    pd.DataFrame(contrasts).to_csv('results/tables/disjoint_contrast_reproducibility.tsv',sep='\t',index=False)
    rawsr=matrices['salmon_sr'].loc[complete,outcome_sr]
    rawdrna=matrices['salmon_lr'].loc[complete,drna_cols]
    raw=np.log2(rawdrna+.1).median(axis=1)-np.log2(rawsr+.1).median(axis=1)
    stats=dict(missing_transcript_id_rows_excluded=missing_transcript_rows,
        common_quantified_reference_transcripts=len(complete),independent_covariate_TPM_ge1=int(eligible.sum()),
        covariate_library=covariate_run,outcome_illumina_libraries=outcome_sr,outcome_directRNA_libraries=drna_cols,
        closure_vs_original_median_abs_change=float((primary[eligible]-raw[eligible]).abs().median()),
        all_zero_directRNA_fraction_eligible=float((drna.loc[eligible].sum(axis=1)==0).mean()),
        all_zero_illumina_fraction_eligible=float((sr.loc[eligible,outcome_sr].sum(axis=1)==0).mean()),
        disjoint_contrast_spearman_min=min(z['spearman'] for z in contrasts),
        disjoint_contrast_spearman_max=max(z['spearman'] for z in contrasts),
        structure_inputs_used=False, status='MEASUREMENT_QC_NOT_FROZEN')
    Path('results/tables/outcome_qc_summary.json').write_text(json.dumps(stats,indent=2)+'\n')
    # Keep transcript outcomes in a separate cache. Missingness script never reads this file.
    pd.DataFrame(dict(stable_transcript_id=complete,signed_disagreement=primary,
                      independent_covariate_TPM=covariate)).to_csv('.cache/phase3a/qc/outcome_only.tsv',sep='\t',index=False)
    print(json.dumps(stats,indent=2))


if __name__=='__main__':
    main()
