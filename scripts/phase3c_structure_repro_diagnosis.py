#!/usr/bin/env python3
"""Diagnose K562 structure-to-structure reproducibility only.

The script reads only the two processed structure resources and reference
identity masks. It never opens SG-NEx abundance or any sequencing outcome.
"""
import csv, gzip, hashlib, json, tarfile
from collections import Counter
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / 'results/tables/phase3c_reference_bridge.tsv'
VIVO = ROOT / '.cache/phase3b/structure/GSE149767_k562_vivo_icshape.tar.gz'
MAPS = ROOT / '.cache/phase3b/structure/GSE149767_k562maps.tar.gz'
GSE132 = ROOT / '.cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz'
OUT = ROOT / 'results/tables/structure_reproducibility.tsv'
SUMMARY = ROOT / 'results/tables/structure_reproducibility_diagnosis.json'


def profile_key(name):
    base = Path(name).name
    for token in ('.NM_', '.NR_'):
        if token in base:
            return base.split(token, 1)[0] + token + base.split(token, 1)[1].split('.', 1)[0]
    return None


def numeric(values, missing):
    return np.array([np.nan if x in missing else float(x) for x in values], dtype=float)


def rho(x, y):
    keep = np.isfinite(x) & np.isfinite(y)
    if keep.sum() < 3 or len(np.unique(x[keep])) < 2 or len(np.unique(y[keep])) < 2:
        return np.nan, int(keep.sum())
    return float(spearmanr(x[keep], y[keep]).statistic), int(keep.sum())


def summarize(x, y, prefix):
    r, n = rho(x, y)
    keep = np.isfinite(x) & np.isfinite(y)
    result = {f'{prefix}_spearman': r, f'{prefix}_joint_callable': n}
    if keep.sum():
        qx = np.nanquantile(x[keep], .75); qy = np.nanquantile(y[keep], .75)
        result[f'{prefix}_upper_quartile_overlap'] = float(((x[keep] >= qx) & (y[keep] >= qy)).sum() / keep.sum())
        result[f'{prefix}_low_quartile_overlap'] = float(((x[keep] <= np.nanquantile(x[keep], .25)) & (y[keep] <= np.nanquantile(y[keep], .25))).sum() / keep.sum())
    else:
        result[f'{prefix}_upper_quartile_overlap'] = np.nan
        result[f'{prefix}_low_quartile_overlap'] = np.nan
    return result


def main():
    bridge_rows = list(csv.DictReader(BRIDGE.open(), delimiter='\t'))
    # Class A and coverage are identity/assay-callability rules, not outcome rules.
    target_by_digest = {}
    for row in bridge_rows:
        if row['mapping_class'] == 'A' and row['coverage_eligible'] == 'True':
            target_by_digest.setdefault(row['sequence_sha256'], []).append(row)

    profiles = {}
    with tarfile.open(VIVO, 'r|gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.rx'):
                continue
            key = profile_key(member.name)
            vals = [line.decode().split() for line in archive.extractfile(member)]
            if key in profiles:
                raise ValueError('duplicate GSE149767 profile: ' + key)
            profiles[key] = vals

    maps = {}
    with tarfile.open(MAPS, 'r|gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.map'):
                continue
            key = profile_key(member.name)
            seq = []
            for line in archive.extractfile(member):
                fields = line.split()
                # GSE149767 maps are distributed in both four- and five-field
                # variants; the nucleotide identity is field 4 in either case.
                if len(fields) < 4 or int(fields[0]) != len(seq) + 1:
                    raise ValueError('malformed map: ' + member.name)
                seq.append(fields[3].decode().upper().replace('U', 'T'))
            digest = hashlib.sha256(''.join(seq).encode()).hexdigest()
            maps.setdefault(key, []).append((len(seq), digest))

    gse132 = {}
    with gzip.open(GSE132, 'rt') as stream:
        for line in stream:
            fields = line.rstrip('\n').split('\t')
            gse132[fields[0]] = numeric(fields[3:], {'NULL', '-999.0'})

    rows, attrition = [], Counter()
    attrition['gse149767_vivo_profiles'] = len(profiles)
    attrition['profiles_with_map'] = sum(k in maps for k in profiles)
    attrition['profiles_with_unique_map'] = sum(len(maps.get(k, [])) == 1 for k in profiles)
    for key, values in profiles.items():
        candidates = maps.get(key, [])
        if len(candidates) != 1:
            continue
        mlen, digest = candidates[0]
        hits = target_by_digest.get(digest, [])
        if len(hits) != 1:
            continue
        target = hits[0]
        sid = target['structure_transcript_id']
        if mlen != len(values) or sid not in gse132:
            continue
        attrition['unique_exact_classA_bridge'] += 1
        a = gse132[sid]
        b1 = numeric([x[0] for x in values], {'-999.0'})
        b2 = numeric([x[1] for x in values], {'-999.0'})
        if len(a) != len(b1):
            attrition['length_mismatch'] += 1
            continue
        callable_a = np.isfinite(a).sum(); callable_b = np.isfinite(b1) & np.isfinite(b2)
        if callable_a < 50 or callable_a / len(a) < .5 or callable_b.sum() < 50 or callable_b.sum() / len(a) < .5:
            attrition['joint_coverage_below_rule'] += 1
            continue
        attrition['joint_coverage_eligible'] += 1
        row = {'gse132099_id': sid, 'gse149767_profile': key, 'gene_id': target['gene_id'], 'length': len(a),
               'gse132099_callable': int(callable_a), 'gse149767_rep1_callable': int(np.isfinite(b1).sum()),
               'gse149767_rep2_callable': int(np.isfinite(b2).sum())}
        row.update(summarize(a, b1, 'cross_rep1'))
        row.update(summarize(a, b2, 'cross_rep2'))
        row.update(summarize(a, (b1 + b2) / 2, 'cross_mean'))
        row.update(summarize(b1, b2, 'within_gse149767'))
        for label, sl in [('five_prime_100', slice(0, 100)), ('three_prime_100', slice(-100, None))]:
            if len(a[sl][np.isfinite(a[sl]) & np.isfinite(b1[sl]) & np.isfinite(b2[sl])]) >= 30:
                row.update(summarize(a[sl], b1[sl], label + '_rep1'))
                row.update(summarize(a[sl], b2[sl], label + '_rep2'))
            else:
                row[label + '_eligible'] = False
        rows.append(row)
    if rows:
        with OUT.open('w', newline='') as stream:
            fields = sorted({key for row in rows for key in row})
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter='\t', lineterminator='\n')
            writer.writeheader(); writer.writerows(rows)
    cross = np.array([r['cross_mean_spearman'] for r in rows], dtype=float)
    within = np.array([r['within_gse149767_spearman'] for r in rows], dtype=float)
    summary = {'attrition': dict(attrition), 'n_profiles': len(rows), 'n_genes': len({r['gene_id'] for r in rows}),
               'cross_study_median_spearman': float(np.nanmedian(cross)) if len(cross) else None,
               'within_gse149767_median_spearman': float(np.nanmedian(within)) if len(within) else None,
               'cross_study_median_upper_quartile_overlap': float(np.nanmedian([r['cross_mean_upper_quartile_overlap'] for r in rows])) if rows else None,
               'cross_study_median_low_quartile_overlap': float(np.nanmedian([r['cross_mean_low_quartile_overlap'] for r in rows])) if rows else None,
               'structure_values_only': True, 'sequencing_outcomes_read': False, 'longbench_inputs_read': False}
    SUMMARY.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
