#!/usr/bin/env python3
"""Offline saved-prediction validation and metrics; never fits or reads structure."""
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'configs/model_c_reestablishment.json'
PREDICTIONS = ROOT / 'results/tables/model_c_oof.tsv.gz'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def validate(rows, root=ROOT):
    cfg = json.loads((root / 'configs/model_c_reestablishment.json').read_text())
    cohort = read_rows(root / 'metadata/final_transcript_cohort.tsv')
    folds = {r['stable_id']: r for r in read_rows(root / 'metadata/cv_folds.tsv')}
    ids = [r['stable_id'] for r in rows]
    if len(rows) != 15999:
        raise ValueError('OOF must contain exactly 15,999 rows')
    if ids != [r['stable_id'] for r in cohort] or len(set(ids)) != len(ids):
        raise ValueError('OOF rows must equal ordered cohort, once each')
    for row in rows:
        fold = folds[row['stable_id']]
        if any(row[k] != fold[k] for k in ('fold', 'sequence_cluster_id')):
            raise ValueError('Frozen fold or sequence group mismatch')
        if row['y'] not in cfg['classes'] or row['pred'] not in cfg['classes']:
            raise ValueError('Unknown class')
        p = [float(row[k]) for k in cfg['probability_columns']]
        if any(not math.isfinite(x) or not 0 <= x <= 1 for x in p):
            raise ValueError('Invalid probability')
        if abs(sum(p) - 1) > 1e-12:
            raise ValueError('Probability sum differs from one')
        # sklearn uses lexicographic class order for an exact tie.
        best = sorted(cfg['classes'], key=lambda c: (-p[cfg['classes'].index(c)], c))[0]
        if row['pred'] != best or float(row['sample_weight']) != 1:
            raise ValueError('Prediction or sample weight mismatch')
    return cfg


def metrics(rows, classes):
    matrix = [[0 for _ in classes] for _ in classes]
    loss = brier = 0.0
    cols = ['p_both', 'p_illumina_only', 'p_directrna_only', 'p_neither', 'p_indeterminate']
    for row in rows:
        a, b = classes.index(row['y']), classes.index(row['pred'])
        matrix[a][b] += 1
        p = [float(row[c]) for c in cols]
        # Explicit actual-class indexing avoids sklearn's lexicographic-order trap.
        loss -= math.log(max(p[a], 2.220446049250313e-16))
        brier += sum((x - (j == a)) ** 2 for j, x in enumerate(p))
    f1, recalls, per_class = [], [], []
    for i, name in enumerate(classes):
        tp = matrix[i][i]; support = sum(matrix[i]); predicted = sum(r[i] for r in matrix)
        score = 2 * tp / (support + predicted) if support + predicted else 0.0
        recall = tp / support if support else 0.0
        f1.append(score)
        if support:
            recalls.append(recall)
        per_class.append(dict(label=name, n=support, predicted_n=predicted, f1=score, recall=recall,
                              precision=tp / predicted if predicted else 0.0))
    return dict(n=len(rows), macro_f1=sum(f1)/len(classes), log_loss=loss/len(rows),
                accuracy=sum(matrix[i][i] for i in range(len(classes)))/len(rows),
                balanced_accuracy=sum(recalls)/len(recalls), brier_multiclass=brier/len(rows),
                class_metrics=per_class, confusion_matrix=matrix, class_order=classes)


def evaluate():
    rows = read_rows(PREDICTIONS); cfg = validate(rows)
    result = metrics(rows, cfg['classes'])
    result['prediction_sha256'] = sha(PREDICTIONS)
    result['provenance'] = cfg['provenance']
    result['fold_metrics'] = [dict(fold=f, **metrics([r for r in rows if int(r['fold']) == f], cfg['classes'])) for f in range(5)]
    # Exact historical group ordering and 100-draw bootstrap; conditional OOF interval.
    import numpy as np
    groups = {}
    for i, row in enumerate(rows):
        groups.setdefault(row['sequence_cluster_id'], []).append(i)
    keys = np.array(list(groups), dtype=object); rng = np.random.default_rng(cfg['seed'])
    # Compute F1 from resampled per-cluster confusion matrices without reparsing rows.
    mats = {k: np.array(metrics([rows[i] for i in ix], cfg['classes'])['confusion_matrix']) for k, ix in groups.items()}
    scores = []
    for _ in range(cfg['bootstrap_replicates']):
        mat = sum((mats[k] for k in rng.choice(keys, len(keys), replace=True)), np.zeros((5, 5), dtype=int))
        denom = mat.sum(axis=0) + mat.sum(axis=1)
        scores.append(float(np.divide(2*np.diag(mat), denom, out=np.zeros(5), where=denom>0).mean()))
    result['macro_f1_ci'] = np.quantile(scores, [.025, .975]).tolist()
    result['bootstrap_replicates'] = cfg['bootstrap_replicates']
    result['historical_differences'] = {k: result[k] - cfg['historical_comparison'][old] for k, old in [('macro_f1','macro_f1'),('log_loss','log_loss_corrected'),('accuracy','accuracy')]}
    result['historical_metrics_within_tolerance'] = all(abs(v) <= cfg['comparison_tolerance_absolute'] for v in result['historical_differences'].values())
    out = ROOT / 'results/tables/model_c_reestablishment_metrics.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    lines = ['# Model C saved-prediction metrics', '', 'Generated by scripts/model_c_artifact.py from the saved artifact, without fitting.', '',
             'Provenance: PRESTRUCTURE_BASELINE_REESTABLISHMENT. PRE-STRUCTURE BASELINE RE-ESTABLISHMENT AFTER PRIOR BASELINE INSPECTION. This is not a prospective preregistration or prospective freeze. Historical performance remains historical provenance only.', '',
             f"Prediction SHA256: `{result['prediction_sha256']}`", '', '| Metric | Value |', '|---|---|']
    for key in ['n','macro_f1','log_loss','accuracy','balanced_accuracy','brier_multiclass','macro_f1_ci']:
        lines.append(f'| {key} | {result[key]} |')
    lines += ['', 'The interval uses 100 fixed-seed sequence-cluster bootstrap draws of saved OOF predictions. It is conditional on these libraries and fitted folds, not a biological-replicate confidence interval.', '',
              'Log loss indexes named class probabilities directly. The original 3.64349 value is invalid; no probability permutation is inferred from the numeric class positions.', '',
              '| Class | N | F1 |', '|---|---|---|']
    for r in result['class_metrics']:
        lines.append(f"| {r['label']} | {r['n']} | {r['f1']:.12f} |")
    lines += ['', '| Fold | N | Macro-F1 | Log loss |', '|---|---|---|---|']
    for r in result['fold_metrics']:
        lines.append(f"| {r['fold']} | {r['n']} | {r['macro_f1']:.12f} | {r['log_loss']:.12f} |")
    lines += ['', 'Confusion matrix (rows observed, columns predicted; fixed order):', '', '| Observed | ' + ' | '.join(cfg['classes']) + ' |', '|---|' + '---|'*5]
    for label, row in zip(cfg['classes'], result['confusion_matrix']):
        lines.append('| ' + label + ' | ' + ' | '.join(map(str,row)) + ' |')
    lines += ['', 'Historical differences (re-established minus historical): `' + json.dumps(result['historical_differences']) + '`.', '',
              f"All three aggregate metrics within predeclared absolute tolerance 1e-6: {result['historical_metrics_within_tolerance']}. This cannot prove original prediction identity. Historical fold/class-specific metrics were not retained.", '']
    (ROOT / 'docs/model_c_reestablishment_results.md').write_text('\n'.join(lines))
    print(json.dumps({k:result[k] for k in ['n','macro_f1','log_loss','macro_f1_ci','historical_differences']}, indent=2))
    return result


if __name__ == '__main__':
    evaluate()
