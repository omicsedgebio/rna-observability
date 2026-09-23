#!/usr/bin/env python3
"""One fixed Model C rerun only. No RNA structure or external outcomes are read."""
import gzip
import importlib.util
import importlib.metadata
import io
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits, threadpool_info
from model_c_artifact import ROOT, CONFIG, PREDICTIONS, sha, evaluate

OUTPUTS = [PREDICTIONS, ROOT/'results/tables/model_c_inputs.tsv.gz',
           ROOT/'results/tables/model_c_reestablishment_metrics.json',
           ROOT/'metadata/model_c_reestablishment_manifest.json',
           ROOT/'docs/model_c_reestablishment_results.md']
ATTEMPT = ROOT/'metadata/model_c_fit_attempt.json'


def require_absent():
    for path in OUTPUTS + [ATTEMPT]:
        if path.exists():
            raise RuntimeError('Existing output/attempt; adjudication required, no refit: ' + str(path))


def write_gzip(frame, path):
    raw = frame.to_csv(sep='\t', index=False, float_format='%.17g').encode()
    path.write_bytes(gzip.compress(raw, mtime=0))


def main():
    if sys.argv[1:] not in ([], ['--preflight']):
        raise ValueError('Only --preflight or the fixed fitting invocation is allowed')
    preflight = sys.argv[1:] == ['--preflight']
    require_absent()
    if sys.version_info[:2] != (3, 11):
        raise ValueError('Python 3.11 required')
    cfg = json.loads(CONFIG.read_text())
    paths = {'historical_code_sha256':'analysis/baseline_models/fit_structure_blind.py',
             'cohort_sha256':'metadata/final_transcript_cohort.tsv','fold_sha256':'metadata/cv_folds.tsv',
             'feature_registry_sha256':'metadata/feature_definitions.tsv'}
    for key, rel in paths.items():
        if sha(ROOT / rel) != cfg[key]:
            raise ValueError('Immutable input changed: ' + rel)
    for package in ['numpy','scipy','pandas','duckdb','scikit-learn']:
        if importlib.metadata.version(package) != cfg[package]:
            raise ValueError('Package version differs from pre-run specification: ' + package)
    start = datetime.now(timezone.utc).isoformat()
    source = ROOT / paths['historical_code_sha256']
    spec = importlib.util.spec_from_file_location('historical_model_c', source)
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    outcome = json.loads((ROOT/'configs/model_c_outcome.json').read_text())
    if (outcome['illumina_runs'] != old.ILL_RUNS or outcome['directrna_runs'] != old.DR_RUNS
            or outcome['independent_covariate_run'] != old.COV_RUN or outcome['threshold'] != 1.0):
        raise ValueError('Frozen outcome configuration disagrees with historical implementation')
    # Isolated derived database: never trust or overwrite a previous phase cache.
    old.DB = ROOT/'.cache/model_c/quantifiers.duckdb'
    old.DB.parent.mkdir(parents=True, exist_ok=True)
    extracted = {p:sha(ROOT/p) for p in ['.cache/phase3a/qc/sgnex_annotation_full.tsv', '.cache/phase3a/qc/k562_quantification.tsv']}
    receipt = old.DB.with_suffix('.sources.json')
    if old.DB.exists() and (not receipt.exists() or json.loads(receipt.read_text()) != extracted):
        raise ValueError('Derived database provenance mismatch; no automatic replacement')
    with duckdb.connect(str(old.DB)) as con:
        con.execute('PRAGMA threads=1')
        con.execute("PRAGMA memory_limit='4GB'")
        if not con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='ann'").fetchone()[0]:
            con.execute("CREATE TABLE ann AS SELECT tx_name AS stable, ensembl_gene_id AS gene, CAST(tx_len AS INTEGER) AS length_nt, CAST(nexon AS INTEGER) AS exon_count FROM read_csv(?, delim='\t', header=true)", [str(ROOT/'.cache/phase3a/qc/sgnex_annotation_full.tsv')])
            con.execute("CREATE TABLE q AS SELECT regexp_replace(tx_name, '\\.[0-9]+', '') AS stable, tx_name, runname, method, protocol_general, CAST(normEst AS DOUBLE) AS value, CAST(estimates AS DOUBLE) AS estimates FROM read_csv(?, delim='\t', header=true)", [str(ROOT/'.cache/phase3a/qc/k562_quantification.tsv')])
        if con.execute("SELECT count(*) FROM (SELECT stable,runname,method FROM q WHERE starts_with(stable,'ENST') GROUP BY ALL HAVING count(*)>1)").fetchone()[0]:
            raise ValueError('Duplicate source measurement keys')
        ann = con.execute('SELECT stable FROM ann').df()
        if ann.stable.duplicated().any():
            raise ValueError('Duplicate source annotation')
        cohort_ids = pd.read_csv(old.COHORT, sep='\t')[['stable_id']]
        for method, runs in [('salmon_sr', old.ILL_RUNS+[old.COV_RUN]), ('salmon_lr',old.DR_RUNS)]:
            for run in runs:
                q = con.execute('SELECT stable,value FROM q WHERE method=? AND runname=?',[method,run]).df().set_index('stable').reindex(cohort_ids.stable_id)
                if len(q)!=15999 or not np.isfinite(q.value.to_numpy()).all() or (q.value<0).any():
                    raise ValueError('Missing/nonfinite/negative measurement: ' + run)
    receipt.write_text(json.dumps(extracted, indent=2)+'\n')
    cohort, folds, ann, dat = old.load_data()
    seqs = old.read_sequences(set(cohort.stable_id)); sf = old.seq_features(seqs)
    df = cohort.merge(folds,on='stable_id',validate='one_to_one').merge(ann,on='stable_id',validate='one_to_one').merge(dat.reset_index(),on='stable_id',validate='one_to_one').merge(sf,on='stable_id',validate='one_to_one')
    df['sequence_cluster_size'] = df.sequence_cluster_id.map(df.sequence_cluster_id.value_counts())
    cols = cfg['features']; labels = cfg['classes']; y = df.label.to_numpy()
    if len(df)!=15999 or not np.isfinite(df[cols].to_numpy()).all():
        raise ValueError('Cohort or feature completeness failed')
    historical = json.loads((ROOT/'results/tables/baseline_model_summary.json').read_text())
    if df.label.value_counts().to_dict()!=historical['labels'] or cols!=historical['feature_sets']['C']:
        raise ValueError('Historical outcome counts or feature list do not match')
    if df.stable_id.tolist() != cohort.stable_id.tolist() or df.stable_id.duplicated().any():
        raise ValueError('Ordered cohort changed')
    if set(df.fold) != set(range(5)) or df.groupby('sequence_cluster_id').fold.nunique().max() != 1:
        raise ValueError('Fold or group integrity failed')
    frozen_cohort = pd.read_csv(old.COHORT, sep='\t')
    if df.fold.tolist() != frozen_cohort.fold.tolist():
        raise ValueError('Cohort fold mismatch')
    df['sample_weight']=1.0
    verification = dict(utc=datetime.now(timezone.utc).isoformat(), n=len(df),
                        labels=df.label.value_counts().to_dict(), features=cols,
                        sequence_groups=int(df.sequence_cluster_id.nunique()),
                        complete_finite_predictors=True, duplicate_measurement_keys=0,
                        exact_order_and_folds=True, outputs_absent=True,
                        structure_inputs_read=False, longbench_inputs_read=False,
                        python=sys.version, packages={p:importlib.metadata.version(p) for p in ['numpy','scipy','pandas','duckdb','scikit-learn']},
                        frozen_sha256={rel:sha(ROOT/rel) for rel in paths.values()}, extracted_sha256=extracted)
    if preflight:
        print(json.dumps(verification, indent=2), flush=True)
        return
    lock = json.loads((ROOT/'metadata/model_c_prefit_lock.json').read_text())
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    remote = subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],cwd=ROOT,text=True).split()[0]
    if head != lock['commit'] or remote != head:
        raise ValueError('Pre-fit lock is not current local and remote HEAD')
    protected = list(paths.values()) + ['configs/model_c_outcome.json','configs/model_c_reestablishment.json','scripts/model_c_reestablish.py','scripts/model_c_artifact.py','scripts/model_c_extract.R']
    for rel in protected:
        committed = subprocess.check_output(['git','show',head+':'+rel],cwd=ROOT)
        if committed != (ROOT/rel).read_bytes():
            raise ValueError('Uncommitted protocol change: '+rel)
    require_absent()
    with (ROOT/'docs/model_c_reconstruction_audit.md').open('a') as stream:
        stream.write('\n## Immediate pre-fit verification\n\n```json\n'+json.dumps(verification,indent=2)+'\n```\n')
    inputs=ROOT/'results/tables/model_c_inputs.tsv.gz'
    write_gzip(df[['stable_id','fold','sequence_cluster_id','label','illumina_support','directrna_support','sample_weight']+cols], inputs)
    pred=np.empty(len(df),dtype=object); prob=np.zeros((len(df),len(labels)))
    fits=[]
    with threadpool_limits(limits=cfg['threads']):
        native=threadpool_info()
        with ATTEMPT.open('x') as stream:
            json.dump(dict(status='FITTING_STARTED_NO_AUTOMATIC_RETRY', utc=datetime.now(timezone.utc).isoformat(), lock_commit=head, invocation='.venv/bin/python3.11 scripts/model_c_reestablish.py'),stream,indent=2)
            stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        for fold in sorted(df.fold.unique()):
            tr=df.fold.ne(fold); te=df.fold.eq(fold)
            estimator=LogisticRegression(C=cfg['C'],solver=cfg['solver'],tol=cfg['tol'],max_iter=cfg['max_iter'],random_state=cfg['seed'],class_weight=cfg['class_weight'],fit_intercept=cfg['fit_intercept'])
            clf=make_pipeline(StandardScaler(),estimator)
            print('Starting sole authorized C attempt, fold',fold,flush=True)
            clf.fit(df.loc[tr,cols],y[tr])
            pred[te]=clf.predict(df.loc[te,cols])
            prob[te]=clf.predict_proba(df.loc[te,cols])[:,[list(clf.classes_).index(x) for x in labels]]
            fits.append(dict(fold=int(fold),iterations=estimator.n_iter_.tolist(),parameters=estimator.get_params()))
            print('Completed fixed C fold',fold,flush=True)
    oof=df[['stable_id','fold','sequence_cluster_id','sample_weight']].copy()
    oof['y']=y; oof['pred']=pred
    for j,col in enumerate(cfg['probability_columns']):
        oof[col]=prob[:,j]
    write_gzip(oof,PREDICTIONS)
    result=evaluate()
    references=['.cache/phase2/sgnex/metadata.rds','.cache/phase2/sgnex/transcript.rds','.cache/phase3a/references/ensembl91.cdna.fa.gz','.cache/phase3a/references/ensembl91.ncrna.fa.gz']
    frozen=list(paths.values())+['configs/model_c_reestablishment.json','configs/model_c_outcome.json','scripts/model_c_reestablish.py','scripts/model_c_artifact.py','scripts/model_c_extract.R',str(inputs.relative_to(ROOT)),str(PREDICTIONS.relative_to(ROOT)),'results/tables/model_c_reestablishment_metrics.json']
    manifest=dict(provenance=cfg['provenance'],started_utc=start,completed_utc=datetime.now(timezone.utc).isoformat(),
                  source_git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  invocation='.venv/bin/python3.11 scripts/model_c_reestablish.py',python=sys.version,platform=platform.platform(),
                  packages={d.metadata['Name']:d.version for d in importlib.metadata.distributions()},native_libraries=native,fold_fits=fits,
                  artifact_sha256={p:sha(ROOT/p) for p in frozen},source_inputs={p:dict(bytes=(ROOT/p).stat().st_size,sha256=sha(ROOT/p)) for p in references},
                  structure_inputs_read=False,longbench_inputs_read=False,training_attempts=1,selection_or_tuning=False)
    manifest['prefit_lock_commit'] = head
    manifest['extracted_sha256'] = extracted
    (ROOT/'metadata/model_c_reestablishment_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    main()
