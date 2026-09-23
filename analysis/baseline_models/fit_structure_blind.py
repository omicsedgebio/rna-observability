#!/usr/bin/env python3
"""Fit frozen structure-blind Models A, B and C for Phase 3D.

Only SG-NEx Salmon quantification, Ensembl 91 annotation/reference sequence,
cluster/fold manifests are read. No structure or LongBench files are read.
"""
from pathlib import Path
import hashlib, json, math, re, subprocess, shutil
import numpy as np
import pandas as pd
import duckdb
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, log_loss, brier_score_loss

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT/'.cache/phase3c/quantifiers.duckdb'
COHORT = ROOT/'metadata/final_transcript_cohort.tsv'
FOLDS = ROOT/'metadata/cv_folds.tsv'
FASTA_SOURCES = [ROOT/'.cache/phase3a/references/ensembl91.cdna.fa.gz', ROOT/'.cache/phase3a/references/ensembl91.ncrna.fa.gz']
CACHE = ROOT/'.cache/phase3d'
ELIGIBLE_FA = CACHE/'baseline_eligible.fa'
KMER_OUT = CACHE/'baseline_kmers.tsv'
OUT = ROOT/'results/tables/baseline_model_metrics.tsv'
OOF_OUT = ROOT/'results/tables/baseline_oof_predictions.tsv'
STRATA_OUT = ROOT/'results/tables/baseline_strata_metrics.tsv'
FIG = ROOT/'results/figures/qc/phase3d_baseline_performance.svg'
SEED = 20260923
ILL_RUNS = ['GIS_K562_Illumina_Rep4-Run1','GIS_k562_Illumina_Rep5-Run1']
DR_RUNS = ['SGNex_K562_directRNA_replicate1_run1','SGNex_K562_directRNA_replicate4_run1','SGNex_K562_directRNA_replicate5_run1','SGNex_K562_directRNA_replicate6_run1']
COV_RUN = 'GIS_K562_Illumina_Rep3-Run1'


def stable(x):
    return re.sub(r'\.[0-9]+(?=(?:_PAR_Y)?$)', '', x)


def read_sequences(wanted):
    import gzip
    found = {}
    for path in FASTA_SOURCES:
        with gzip.open(path, 'rt') as fh:
            name, parts = None, []
            for line in fh:
                if line.startswith('>'):
                    if name is not None and stable(name) in wanted and stable(name) not in found:
                        found[stable(name)] = ''.join(parts).upper()
                    name, parts = line[1:].split()[0], []
                else: parts.append(line.strip())
            if name is not None and stable(name) in wanted and stable(name) not in found:
                found[stable(name)] = ''.join(parts).upper()
    missing = wanted-set(found)
    if missing: raise RuntimeError(f'missing reference sequences: {len(missing)}')
    return found


def seq_features(seqs):
    out=[]
    for tid, seq in seqs.items():
        s=''.join(c for c in seq if c in 'ACGT')
        n=len(s)
        counts=np.array([s.count(c) for c in 'ACGT'], dtype=float)
        probs=counts/n if n else np.zeros(4)
        entropy=float(-(probs[probs>0]*np.log2(probs[probs>0])).sum()) if n else np.nan
        homopolymer=0
        for m in re.finditer(r'([ACGT])\1{5,}', s): homopolymer += len(m.group(0))
        low=0; windows=0
        if n >= 32:
            codes=np.frombuffer(s.encode('ascii'),dtype=np.uint8)
            windows=n-31; win_counts=[]
            for code in (65,67,71,84):
                hit=(codes==code).astype(np.int32); cs=np.concatenate(([0],np.cumsum(hit)))
                win_counts.append(cs[32:]-cs[:-32])
            wc=np.stack(win_counts,axis=1).astype(float)/32.0
            nz=wc>0; terms=np.where(nz, wc*np.log2(np.where(nz,wc,1.0)), 0.0); ent=-terms.sum(axis=1)
            low=int(np.sum(ent < 1.5))
        out.append(dict(stable_id=tid, sequence_length=n, gc_fraction=float((counts[1]+counts[2])/n) if n else np.nan,
                        homopolymer_fraction=homopolymer/n if n else np.nan,
                        low_complexity_fraction=low/windows if windows else 0.0,
                        sequence_entropy=entropy))
    return pd.DataFrame(out)


def ensure_kmers(seqs):
    CACHE.mkdir(parents=True, exist_ok=True)
    with ELIGIBLE_FA.open('w') as fh:
        for tid in sorted(seqs): fh.write(f'>{tid}\n{seqs[tid]}\n')
    if not KMER_OUT.exists():
        exe=CACHE/'exact_kmers'
        if not exe.exists():
            compiler=shutil.which('clang++') or shutil.which('g++')
            if not compiler: raise RuntimeError('no C++ compiler for prespecified k-mer feature')
            subprocess.run([compiler,'-O3','-std=c++17',str(ROOT/'src/exact_kmers.cpp'),'-o',str(exe)],check=True)
        scratch=CACHE/'kmer_scratch'
        subprocess.run([str(exe),str(ELIGIBLE_FA),'31',str(scratch),str(KMER_OUT)],check=True)
    k=pd.read_csv(KMER_OUT,sep='\t')
    k=k.rename(columns={'transcript_id':'stable_id'})
    return k[['stable_id','unique_kmer_fraction']]


def category(i, d):
    istate='detected' if i==2 else 'absent' if i==0 else 'indeterminate'
    dstate='detected' if d>=3 else 'absent' if d==0 else 'indeterminate'
    if istate=='indeterminate' or dstate=='indeterminate': return 'INDETERMINATE'
    return {('detected','detected'):'BOTH',('detected','absent'):'ILLUMINA_ONLY',('absent','detected'):'DIRECT_RNA_ONLY',('absent','absent'):'NEITHER'}[(istate,dstate)]


def load_data():
    cohort=pd.read_csv(COHORT,sep='\t',usecols=['stable_id'])
    folds=pd.read_csv(FOLDS,sep='\t',usecols=['stable_id','sequence_cluster_id','fold'])
    con=duckdb.connect(str(DB),read_only=True)
    ann=con.execute("select stable,gene,length_nt,exon_count,count(*) over(partition by gene) isoforms_per_gene from ann").df().rename(columns={'stable':'stable_id'})
    wanted=set(cohort.stable_id)
    ann=ann[ann.stable_id.isin(wanted)].drop_duplicates('stable_id')
    q=con.execute("select stable as stable_id,runname,method,protocol_general,value from q where method in ('salmon_sr','salmon_lr','rsem_sr','bambu_lr') and stable like 'ENST%'").df()
    q=q[q.stable_id.isin(wanted)]
    # Primary workflow outcome states
    il=q[(q.method=='salmon_sr') & q.runname.isin(ILL_RUNS)].pivot_table(index='stable_id',columns='runname',values='value',aggfunc='first').reindex(columns=ILL_RUNS)
    dr=q[(q.method=='salmon_lr') & q.runname.isin(DR_RUNS)].pivot_table(index='stable_id',columns='runname',values='value',aggfunc='first').reindex(columns=DR_RUNS)
    primary=pd.DataFrame(index=sorted(wanted)); primary.index.name='stable_id'
    primary['illumina_support']=(il>=1).sum(axis=1).reindex(primary.index).fillna(0).astype(int)
    primary['directrna_support']=(dr>=1).sum(axis=1).reindex(primary.index).fillna(0).astype(int)
    primary['label']=[category(i,d) for i,d in zip(primary.illumina_support,primary.directrna_support)]
    # Independent prior-run abundance covariate, not an outcome library.
    cov=q[(q.method=='salmon_sr') & (q.runname==COV_RUN)].set_index('stable_id')['value'].reindex(primary.index)
    primary['independent_abundance_log1p']=np.log1p(cov.fillna(0).astype(float))
    # Alternative quantifier sensitivity labels are reported, never used to choose primary.
    ilr=q[(q.method=='rsem_sr') & q.runname.isin(ILL_RUNS)].pivot_table(index='stable_id',columns='runname',values='value',aggfunc='first').reindex(columns=ILL_RUNS)
    db=q[(q.method=='bambu_lr') & q.runname.isin(DR_RUNS)].pivot_table(index='stable_id',columns='runname',values='value',aggfunc='first').reindex(columns=DR_RUNS)
    alt_i=(ilr>=1).sum(axis=1).reindex(primary.index).fillna(0).astype(int)
    alt_d=(db>0).sum(axis=1).reindex(primary.index).fillna(0).astype(int)
    primary['alt_label']=[category(i,d) for i,d in zip(alt_i,alt_d)]
    return cohort, folds, ann, primary


def metrics(y_true, pred, prob, model, n):
    labels=['BOTH','ILLUMINA_ONLY','DIRECT_RNA_ONLY','NEITHER','INDETERMINATE']
    return {'model':model,'n':n,'accuracy':accuracy_score(y_true,pred),'balanced_accuracy':balanced_accuracy_score(y_true,pred),
            'macro_f1':f1_score(y_true,pred,labels=labels,average='macro',zero_division=0),'log_loss':log_loss(y_true,prob,labels=labels),
            'brier_multiclass':float(np.mean(np.sum((prob-np.eye(len(labels))[pd.Categorical(y_true,categories=labels).codes])**2,axis=1))),
            'structure_inputs_read':False,'longbench_inputs_read':False}


def bootstrap_ci(oof, metric_name, nboot=100):
    rng=np.random.default_rng(SEED)
    groups=oof.groupby('sequence_cluster_id',sort=False).indices
    keys=np.array(list(groups),dtype=object); vals=[]
    y=oof.y.to_numpy(); pred=oof.pred.to_numpy()
    for _ in range(nboot):
        sampled=rng.choice(keys,size=len(keys),replace=True)
        idx=np.concatenate([groups[k] for k in sampled])
        if metric_name=='accuracy': vals.append(accuracy_score(y[idx],pred[idx]))
        elif metric_name=='balanced_accuracy': vals.append(balanced_accuracy_score(y[idx],pred[idx]))
        else: vals.append(f1_score(y[idx],pred[idx],labels=['BOTH','ILLUMINA_ONLY','DIRECT_RNA_ONLY','NEITHER','INDETERMINATE'],average='macro',zero_division=0))
    return float(np.quantile(vals,.025)),float(np.quantile(vals,.975))


def main():
    cohort, folds, ann, dat=load_data()
    seqs=read_sequences(set(cohort.stable_id)); sf=seq_features(seqs); km=pd.DataFrame({'stable_id':list(seqs),'unique_kmer_fraction':np.nan})
    df=cohort.merge(folds,on='stable_id',validate='one_to_one').merge(ann,on='stable_id',validate='one_to_one').merge(dat.reset_index(),on='stable_id',validate='one_to_one').merge(sf,on='stable_id',validate='one_to_one').merge(km,on='stable_id',validate='one_to_one')
    cluster_sizes=df.sequence_cluster_id.value_counts(); df['sequence_cluster_size']=df.sequence_cluster_id.map(cluster_sizes)
    df['gene_isoform_count']=df['isoforms_per_gene']
    labels=['BOTH','ILLUMINA_ONLY','DIRECT_RNA_ONLY','NEITHER','INDETERMINATE']; y=df.label.to_numpy()
    feature_sets={'A':['independent_abundance_log1p','sequence_length','gc_fraction'],
                  'B':['independent_abundance_log1p','sequence_length','gc_fraction','exon_count','isoforms_per_gene','sequence_cluster_size'],
                  'C':['independent_abundance_log1p','sequence_length','gc_fraction','exon_count','isoforms_per_gene','sequence_cluster_size','homopolymer_fraction','low_complexity_fraction','sequence_entropy']}
    metrics_rows=[]; pred_rows=[]
    for model, cols in feature_sets.items():
        pred=np.empty(len(df),dtype=object); prob=np.zeros((len(df),len(labels)))
        for fold in sorted(df.fold.unique()):
            tr=df.fold.ne(fold); te=df.fold.eq(fold)
            clf=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,random_state=SEED))
            clf.fit(df.loc[tr,cols],y[tr]); pred[te]=clf.predict(df.loc[te,cols]); prob[te]=clf.predict_proba(df.loc[te,cols])[:,[list(clf.classes_).index(x) for x in labels]]
        m=metrics(y,pred,prob,model,len(df)); oof=pd.DataFrame({'stable_id':df.stable_id,'sequence_cluster_id':df.sequence_cluster_id,'fold':df.fold,'y':y,'pred':pred})
        lo,hi=bootstrap_ci(oof,'macro_f1'); m['macro_f1_ci_low']=lo; m['macro_f1_ci_high']=hi
        metrics_rows.append(m)
        for i,row in df.iterrows(): pred_rows.append({'model':model,'stable_id':row.stable_id,'fold':int(row.fold),'y':y[i],'pred':pred[i],'p_both':prob[i,0],'p_illumina_only':prob[i,1],'p_directrna_only':prob[i,2],'p_neither':prob[i,3],'p_indeterminate':prob[i,4],'sequence_cluster_id':row.sequence_cluster_id})
        # stratum metrics for Model C only
        if model=='C':
            for name, groups in [('abundance',pd.qcut(df.independent_abundance_log1p.rank(method='first'),3,labels=['low','mid','high'])),('length',pd.qcut(df.sequence_length.rank(method='first'),3,labels=['short','mid','long'])),('isoform',pd.cut(df.isoforms_per_gene,[0,1,5,10,np.inf],labels=['1','2-5','6-10','>10']))]:
                for level in groups.cat.categories:
                    mask=(groups==level).to_numpy(); z=oof[mask]; metrics_rows.append({'model':'C_'+name+'_'+str(level),'n':len(z),'accuracy':accuracy_score(z.y,z.pred),'balanced_accuracy':balanced_accuracy_score(z.y,z.pred),'macro_f1':f1_score(z.y,z.pred,labels=labels,average='macro',zero_division=0),'log_loss':np.nan,'brier_multiclass':np.nan,'structure_inputs_read':False,'longbench_inputs_read':False})
    pd.DataFrame(metrics_rows).to_csv(OUT,sep='\t',index=False)
    pd.DataFrame(pred_rows).to_csv(OOF_OUT,sep='\t',index=False)
    # Alternative labels are a descriptive quantifier sensitivity diagnostic.
    alt=pd.DataFrame({'primary':dat.label,'alternative':dat.alt_label}).value_counts().rename('n').reset_index()
    alt.to_csv(STRATA_OUT,sep='\t',index=False)
    # Compact SVG generated without external plotting state.
    rows=pd.DataFrame(metrics_rows).query("model in ['A','B','C']")
    W,H=560,340; ml,mb=80,40; plotw,ploth=430,230
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">','<rect width="100%" height="100%" fill="white"/>','<text x="280" y="25" text-anchor="middle" font-family="sans-serif" font-size="16">Structure-blind workflow phenotype</text>']
    for v in [0,.25,.5,.75,1]:
        yy=mb+ploth*(1-v); svg += [f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+plotw}" y2="{yy:.1f}" stroke="#ddd"/>',f'<text x="{ml-8}" y="{yy+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="10">{v:.2f}</text>']
    for j,row in rows.reset_index(drop=True).iterrows():
        xx=ml+plotw*(j+.5)/3
        for off,key,col in [(-12,'accuracy','#4472c4'),(12,'macro_f1','#ed7d31')]:
            hh=ploth*float(row[key]); yy=mb+ploth-hh; svg.append(f'<rect x="{xx+off-7:.1f}" y="{yy:.1f}" width="14" height="{hh:.1f}" fill="{col}"/>')
        svg.append(f'<text x="{xx:.1f}" y="{mb+ploth+20}" text-anchor="middle" font-family="sans-serif" font-size="11">{row.model}</text>')
    svg += [f'<line x1="{ml}" y1="{mb}" x2="{ml}" y2="{mb+ploth}" stroke="black"/><line x1="{ml}" y1="{mb+ploth}" x2="{ml+plotw}" y2="{mb+ploth}" stroke="black"/>','<rect x="390" y="285" width="12" height="12" fill="#4472c4"/><text x="408" y="295" font-family="sans-serif" font-size="10">accuracy</text>','<rect x="460" y="285" width="12" height="12" fill="#ed7d31"/><text x="478" y="295" font-family="sans-serif" font-size="10">macro-F1</text>','</svg>']
    FIG.write_text('\n'.join(svg))
    summary={'n_transcripts':len(df),'labels':df.label.value_counts().to_dict(),'models':['A','B','C'],'feature_sets':feature_sets,'cohort_sha256':hashlib.sha256(COHORT.read_bytes()).hexdigest(),'fold_sha256':hashlib.sha256(FOLDS.read_bytes()).hexdigest(),'structure_inputs_read':False,'longbench_inputs_read':False}
    (ROOT/'results/tables/baseline_model_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
