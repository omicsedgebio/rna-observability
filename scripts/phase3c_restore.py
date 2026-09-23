#!/usr/bin/env python3
"""Restore only checksummed, previously pinned scientific inputs to ignored caches."""
import csv
import hashlib
from pathlib import Path
import subprocess
import sys

from phase3b_acquire import RESOURCES
from phase3b_parallel_reference import download

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with (ROOT / path).open() as stream:
        return {r.get('resource_id', r.get('dataset_id')): r for r in csv.DictReader(stream, delimiter='\t')}


REFERENCE = rows('metadata/reference_resources.tsv')
PROVENANCE = rows('metadata/download_provenance.tsv')
ALLOWED = {'ensembl91_gtf', 'ensembl91_cdna', 'ensembl91_ncrna',
           'SGNEX_TX', 'SGNEX_META', 'SGNEX_SPIKE'}


def restore(name):
    if name not in ALLOWED:
        raise ValueError('Unregistered or out-of-scope scientific resource')
    record = REFERENCE.get(name) or PROVENANCE[name]
    target = ROOT / record.get('cache_path', record.get('local_cache_path'))
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() and name.startswith('ensembl91'):
        RESOURCES[name] = ('reference', record['authoritative_url'], 'Ensembl 91',
                           'GRCh38', str(target.relative_to(ROOT)), 'previously pinned')
        download(name)
    elif not target.exists():
        partial = target.with_name(target.name + '.partial')
        subprocess.run(['curl', '-sSL', '--fail', '--retry', '4', '--connect-timeout',
                        '30', '--max-time', '3600', '-C', '-', '-o', str(partial),
                        record['source_url']], check=True)
        partial.rename(target)
    digest = hashlib.sha256()
    with target.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    if target.stat().st_size != int(record['bytes']) or digest.hexdigest() != record['sha256']:
        raise ValueError('Pinned resource checksum/size mismatch: ' + name)
    print(name, target.stat().st_size, 'SHA256_OK', flush=True)


if __name__ == '__main__':
    for item in sys.argv[1:]:
        restore(item)
