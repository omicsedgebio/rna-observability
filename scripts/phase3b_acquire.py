#!/usr/bin/env python3
"""Acquire only prespecified processed structure and Ensembl 88 references."""
import csv
import datetime as dt
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'metadata/phase3b_resources.tsv'
RESOURCES = {
    'gse132099_icshape_invivo': ('processed_structure',
        'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE132nnn/GSE132099/suppl/GSE132099_icSHAPE_invivo.out.txt.gz',
        'GSE132099', 'GRCh38; Ensembl 88',
        '.cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz',
        'GEO public access; redistribution and commercial terms not explicitly established'),
    'gse149767_k562_icshape_invivo': ('processed_structure',
        'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE149nnn/GSE149767/suppl/GSE149767_k562_vivo_icshape.tar.gz',
        'GSE149767', 'GRCh38; annotation release unverified',
        '.cache/phase3b/structure/GSE149767_k562_vivo_icshape.tar.gz',
        'GEO public access; redistribution and commercial terms not explicitly established'),
    'gse149767_readme': ('processed_metadata',
        'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE149nnn/GSE149767/suppl/GSE149767_readme.txt',
        'GSE149767', 'GRCh38 for icSHAPE',
        '.cache/phase3b/structure/GSE149767_readme.txt',
        'GEO public access; redistribution and commercial terms not explicitly established'),
    'gse149767_k562_maps': ('processed_structure_metadata',
        'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE149nnn/GSE149767/suppl/GSE149767_k562maps.tar.gz',
        'GSE149767', 'GRCh38 for icSHAPE',
        '.cache/phase3b/structure/GSE149767_k562maps.tar.gz',
        'GEO public access; redistribution and commercial terms not explicitly established'),
    'ensembl88_gtf': ('reference',
        'https://ftp.ensembl.org/pub/release-88/gtf/homo_sapiens/Homo_sapiens.GRCh38.88.gtf.gz',
        'Ensembl 88', 'GRCh38',
        '.cache/phase3b/references/ensembl88.gtf.gz',
        'Ensembl-produced data available without restriction; third-party caveats'),
    'ensembl88_cdna': ('reference',
        'https://ftp.ensembl.org/pub/release-88/fasta/homo_sapiens/cdna/Homo_sapiens.GRCh38.cdna.all.fa.gz',
        'Ensembl 88', 'GRCh38',
        '.cache/phase3b/references/ensembl88.cdna.fa.gz',
        'Ensembl-produced data available without restriction; third-party caveats'),
    'ensembl88_ncrna': ('reference',
        'https://ftp.ensembl.org/pub/release-88/fasta/homo_sapiens/ncrna/Homo_sapiens.GRCh38.ncrna.fa.gz',
        'Ensembl 88', 'GRCh38',
        '.cache/phase3b/references/ensembl88.ncrna.fa.gz',
        'Ensembl-produced data available without restriction; third-party caveats'),
}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def acquire(name):
    if name not in RESOURCES:
        raise ValueError('Unregistered resource: ' + name)
    kind, url, release, assembly, relpath, rights = RESOURCES[name]
    if 'longbench' in url.lower() or 'gse303762' in url.lower():
        raise ValueError('LongBench remains locked')
    path = ROOT / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if MANIFEST.exists():
        with MANIFEST.open() as stream:
            existing = list(csv.DictReader(stream, delimiter='\t'))
    registered = next((r for r in existing if r['resource_id'] == name), None)
    if not path.exists():
        partial = path.with_name(path.name + '.partial')
        subprocess.run(['curl', '-L', '--fail', '--retry', '4', '--connect-timeout', '30',
                        '--max-time', '3600', '-C', '-', '-o', str(partial), url], check=True)
        partial.rename(path)
    row = dict(resource_id=name, kind=kind, authoritative_url=url, release=release,
               assembly=assembly, bytes=str(path.stat().st_size), sha256=digest(path),
               retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
               license_reuse=rights, cache_path=relpath)
    if registered:
        if any(row[k] != registered[k] for k in ['authoritative_url', 'bytes', 'sha256']):
            raise ValueError('Downloaded file differs from registered resource: ' + name)
        return registered
    existing.append(row)
    with MANIFEST.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(existing)
    return row


if __name__ == '__main__':
    for name in sys.argv[1:]:
        print(acquire(name), flush=True)
