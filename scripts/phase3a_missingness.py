#!/usr/bin/env python3
"""Availability-only QC. Never reads a reactivity value or a disagreement endpoint."""
import json
import os
from pathlib import Path
import sys
os.environ.setdefault('MPLCONFIGDIR',str(Path('.cache/phase3a/matplotlib').resolve()))
os.environ.setdefault('XDG_CACHE_HOME',str(Path('.cache/phase3a/fontcache').resolve()))
import numpy as np
import pandas as pd
from patsy import dmatrix
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from rnaobs.core import stable_id, provisional_availability


def main():
    feature=pd.read_csv('results/tables/sequence_annotation_features.tsv',sep='\t')
    mapping=pd.read_csv('results/tables/transcript_mapping_validated.tsv',sep='\t',low_memory=False)
    shape=pd.read_csv('results/tables/icshape_transcript_inventory.tsv',sep='\t')
    # Inventory columns contain only masks/counts/lengths, never numerical reactivity.
    allowed={'structure_transcript_id','stable_transcript_id','reported_length','callable_bases','callable_fraction'}
    if set(shape.columns)!=allowed:
        raise ValueError('Unexpected structure input: fail closed')
    if shape.structure_transcript_id.duplicated().any():
        raise ValueError('Duplicate structure identifiers')
    availability=shape.set_index('structure_transcript_id')
    feature=feature.merge(mapping[['sgnex_transcript_id','structure_transcript_id','exact_version_id','reason']],
                          left_on='transcript_id',right_on='sgnex_transcript_id',how='left',validate='1:1')
    feature['callable_fraction']=feature.structure_transcript_id.map(availability.callable_fraction)
    feature['callable_bases']=feature.structure_transcript_id.map(availability.callable_bases)
    # Provisional QC only: equivalent length and exact ID are insufficient for A/B.
    compatible=feature.exact_version_id & (feature.reason=='icshape_source_exons_and_sequence_unavailable')
    feature['usable']=np.fromiter((
        provisional_availability(exact, reason, fraction, bases)
        for exact,reason,fraction,bases in zip(
            feature.exact_version_id,feature.reason,feature.callable_fraction,feature.callable_bases)),
        dtype=bool,count=len(feature))
    x=pd.read_csv('.cache/phase3a/qc/k562_quantification.tsv',sep='\t',
                  usecols=['tx_name','normEst','runname','method','protocol_general'])
    x=x[x.tx_name.notna()].copy(); x['stable_transcript_id']=x.tx_name.map(stable_id)
    sr=x[x.method=='salmon_sr'].pivot(index='stable_transcript_id',columns='runname',values='normEst')
    dr=x[(x.method=='salmon_lr') & (x.protocol_general=='directRNA')].pivot(index='stable_transcript_id',columns='runname',values='normEst')
    med=sr.median(axis=1); med[sr.isna().any(axis=1)]=np.nan
    feature['illumina_TPM']=feature.stable_transcript_id.map(med)
    feature['illumina_detection_fraction']=feature.stable_transcript_id.map((sr>=1).mean(axis=1).where(sr.notna().all(axis=1)))
    feature['directRNA_detection_fraction']=feature.stable_transcript_id.map((dr>=1).mean(axis=1).where(dr.notna().all(axis=1)))
    data=feature.dropna(subset=['illumina_TPM','gc_fraction','directRNA_detection_fraction','illumina_detection_fraction']).copy()
    for source,target in [('illumina_TPM','log_abundance'),('sequence_length','log_length'),
                          ('isoforms_per_gene','log_isoforms'),('exon_count','log_exons')]:
        data[target]=np.log1p(data[source])
    formula='bs(log_abundance,df=4) + bs(log_length,df=4) + bs(gc_fraction,df=4) + log_isoforms + log_exons + shared_exon_fraction + illumina_detection_fraction + directRNA_detection_fraction'
    design=dmatrix(formula,data,return_type='dataframe')
    # The unpenalized clustered GLM is singular for these correlated detection
    # covariates. Ridge is a descriptive overlap diagnostic, not an effect test.
    design=design.drop(columns='Intercept')
    scaler=StandardScaler()
    scaled=scaler.fit_transform(design)
    fit=LogisticRegression(penalty='l2',C=1.0,max_iter=500,solver='lbfgs',tol=1e-6)
    fit.fit(scaled,data.usable.astype(int))
    data['availability_probability']=fit.predict_proba(scaled)[:,1]
    coeff=pd.DataFrame({'term':design.columns,'standardized_coefficient':fit.coef_[0],
                        'standardized_odds_ratio':np.exp(fit.coef_[0]),
                        'model':'ridge_logistic_C1_descriptive_no_inferential_CI'})
    coeff.to_csv('results/tables/structure_missingness_adjusted.tsv',sep='\t',index=False)
    data[['transcript_id','gene_id','usable','availability_probability']].to_csv(
        '.cache/phase3a/qc/missingness_probabilities.tsv',sep='\t',index=False)
    # Fixed bins permit descriptive inspection without response-based threshold tuning.
    data['abundance_bin']=pd.cut(data.illumina_TPM,[-1e-10,0,.1,1,10,100,np.inf],
                                labels=['0','(0,0.1]','(0.1,1]','(1,10]','(10,100]','>100'])
    data['length_bin']=pd.cut(data.sequence_length,[0,500,1000,2000,5000,10000,np.inf],
                            labels=['<=500','501-1000','1001-2000','2001-5000','5001-10000','>10000'])
    data['gc_bin']=pd.cut(data.gc_fraction,[-.01,.3,.4,.5,.6,.7,1.01])
    data['isoform_bin']=pd.cut(data.isoforms_per_gene,[0,1,2,5,10,20,np.inf])
    summaries=[]
    for dim in ['abundance_bin','length_bin','gc_bin','isoform_bin','exon_count',
                'illumina_detection_fraction','directRNA_detection_fraction']:
        grouped=data.groupby(dim,observed=True)
        for level,group in grouped:
            summaries.append(dict(dimension=dim,level=str(level),transcripts=len(group),
                                  usable=int(group.usable.sum()),usable_fraction=float(group.usable.mean()),
                                  mean_fitted_probability=float(group.availability_probability.mean())))
    table=pd.DataFrame(summaries)
    table.to_csv('results/tables/structure_missingness_strata.tsv',sep='\t',index=False)
    genes=data.groupby('gene_id').usable.agg(['size','sum','mean'])
    genes.to_csv('results/tables/structure_missingness_by_gene.tsv',sep='\t')
    probs=data.availability_probability
    observed=data.loc[data.usable,'availability_probability']
    weights=1/observed
    stats=dict(status='PROVISIONAL_ID_LENGTH_AVAILABILITY_ONLY_NOT_VALIDATED_MAPPING',
        feature_universe=len(feature),usable_provisional=int(feature.usable.sum()),
        usable_fraction=float(feature.usable.mean()),adjusted_analysis_n=len(data),
        excluded_missing_covariates=len(feature)-len(data),gene_clusters=len(genes),
        genes_no_usable=int((genes['sum']==0).sum()),genes_all_usable=int((genes['mean']==1).sum()),
        probability_below_0_05_fraction=float((probs<.05).mean()),
        probability_above_0_95_fraction=float((probs>.95).mean()),
        inverse_probability_weight_max=float(weights.max()),
        inverse_probability_weight_q99=float(weights.quantile(.99)),
        weight_effective_sample_size=float(weights.sum()**2/(weights**2).sum()),
        model_converged=bool(fit.n_iter_[0]<500),model='ridge_logistic_C1_standardized',
        formula=formula,seed='NONE_DETERMINISTIC_SOLVER',
        coverage_threshold_counts={str(t):int((compatible & (feature.callable_fraction>=t) & (feature.callable_bases>=50)).sum()) for t in [.25,.5,.75]},
        reactivity_values_read=False,disagreement_values_read=False)
    Path('results/tables/missingness_adjusted_summary.json').write_text(json.dumps(stats,indent=2)+'\n')
    figdir=Path('results/figures/qc'); figdir.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,
                         'svg.fonttype':'none','svg.hashsalt':'phase3a_availability',
                         'savefig.dpi':300})
    fig,axes=plt.subplots(2,2,figsize=(8,6),constrained_layout=True)
    for ax,dim,title in zip(axes.flat,['abundance_bin','length_bin','gc_bin','isoform_bin'],
                            ['Illumina abundance (TPM)','Transcript length (nt)','GC fraction','Isoforms per gene']):
        z=table[table.dimension==dim]
        ax.bar(range(len(z)),z.usable_fraction,color='#346A8A')
        ax.set_xticks(range(len(z)),z.level,rotation=40,ha='right',fontsize=7)
        ax.set_ylim(0,1); ax.set_xlabel(title); ax.set_ylabel('Provisional usable fraction')
    fig.suptitle('K562 icSHAPE availability: exact ID and length QC only\nTranscript definition validation remains incomplete',fontsize=11)
    fig.savefig(figdir/'structure_missingness_strata.svg'); fig.savefig(figdir/'structure_missingness_strata.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(5.8,3.7),constrained_layout=True)
    for values,color,label in [(probs,'#346A8A','All QC transcripts'),
                               (observed,'#B44A3A','Provisional usable profiles')]:
        ordered=np.sort(values.to_numpy())
        ax.plot(ordered,np.arange(1,len(ordered)+1)/len(ordered),color=color,
                linewidth=1.8,label=label)
    ax.axvline(.05,color='black',linestyle=':',linewidth=1)
    ax.set(xlabel='Fitted profile-availability probability',ylabel='Cumulative fraction',
           xlim=(0,1),ylim=(0,1),title='Availability overlap diagnostic (in-sample QC)')
    ax.legend(frameon=False,fontsize=8)
    fig.savefig(figdir/'structure_missingness_overlap.svg');fig.savefig(figdir/'structure_missingness_overlap.png');plt.close(fig)
    for path in figdir.glob('structure_missingness_*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    print(json.dumps(stats,indent=2))


if __name__=='__main__': main()
