#!/usr/bin/env python3
"""Register Phase 3B references and processed structure acquisitions."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        return reader.fieldnames, list(reader)


def write(path, fields, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def main():
    _, resources = read(ROOT / 'metadata/phase3b_resources.tsv')
    fields, refs = read(ROOT / 'metadata/reference_resources.tsv')
    seen = {r['resource_id'] for r in refs}
    for row in resources:
        if row['kind'] == 'reference' and row['resource_id'] not in seen:
            refs.append({k: row[k] for k in fields})
    write(ROOT / 'metadata/reference_resources.tsv', fields, refs)
    fields, provenance = read(ROOT / 'metadata/download_provenance.tsv')
    seen = {r['dataset_id'] for r in provenance}
    for row in resources:
        if row['resource_id'] not in seen:
            provenance.append(dict(dataset_id=row['resource_id'], local_cache_path=row['cache_path'],
                source_url=row['authoritative_url'], retrieval_date=row['retrieved_utc'][:10],
                bytes=row['bytes'], sha256=row['sha256'],
                command='scripts/phase3b_acquire.py or verified ranged Ensembl transfer'))
    write(ROOT / 'metadata/download_provenance.tsv', fields, provenance)
    fields, datasets = read(ROOT / 'metadata/datasets.tsv')
    seen = {r['dataset_id'] for r in datasets}
    definitions = [
        ('GSE132099', 'structure_development_candidate', 'GSE132099',
         'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132099',
         'in_vivo_icSHAPE', 'K562', 'GSE132099_icSHAPE_invivo.out.txt.gz',
         'GRCh38.p10', 'Ensembl_88_unversioned_processed_IDs',
         '3_treated_biological_replicates;pooled_processed_scores',
         'A_16268_B_0_C_17_D_5_E_5;16055_coverage_eligible',
         'GEO_public;dataset_specific_redistribution_commercial_terms_unclear'),
        ('GSE149767', 'independent_structure_reproducibility_candidate', 'GSE149767',
         'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE149767',
         'in_vivo_icSHAPE;fSHAPE_sequence_maps', 'K562',
         'GSE149767_k562_vivo_icshape.tar.gz;GSE149767_k562maps.tar.gz',
         'hg38', 'RefSeq_NM_NR;release_unverified',
         '2_reactivity_columns;sample_lineage_requires_confirmation',
         '724_unique_sequence_matches;75_cross_study_coverage_eligible',
         'GEO_public;dataset_specific_redistribution_commercial_terms_unclear')]
    key_to_resource = {'GSE132099': 'gse132099_icshape_invivo',
                       'GSE149767': 'gse149767_k562_icshape_invivo'}
    by_id = {r['resource_id']: r for r in resources}
    for dataset_id, role, accession, identity_url, tech, context, processed, assembly, annotation, reps, compatible, license_ in definitions:
        if dataset_id in seen:
            continue
        r = by_id[key_to_resource[dataset_id]]
        datasets.append(dict(dataset_id=dataset_id, role=role, accession=accession,
            identity_url=identity_url, technologies=tech, contexts=context,
            processed_resource=processed, download_url=r['authoritative_url'],
            size_bytes=r['bytes'], size_status='exact_SHA256_verified', genome_build=assembly,
            annotation=annotation, replicates=reps, license=license_,
            compatibility_status=compatible, retrieval_date=r['retrieved_utc'][:10],
            download_status='DOWNLOADED_CACHE', sha256=r['sha256'], locked='false'))
    write(ROOT / 'metadata/datasets.tsv', fields, datasets)


if __name__ == '__main__':
    main()
