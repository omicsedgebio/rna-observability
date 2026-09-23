#!/usr/bin/env python3
"""Auditable public reference/source acquisition, never raw reads or LongBench."""
import argparse
import csv
import datetime as dt
import hashlib
from pathlib import Path
import subprocess


def acquire(resource_id, url, destination, release, assembly, license_note, kind):
    if any(x in url.lower() for x in ('longbench', 'gse303762')):
        raise ValueError('LongBench remains locked')
    destination = Path(destination)
    if not str(destination).startswith('.cache/phase3a/'):
        raise ValueError('Source acquisition must remain in ignored phase cache')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        partial = destination.with_suffix(destination.suffix + '.partial')
        subprocess.run(['curl', '-L', '--fail', '--retry', '2', '--connect-timeout', '30',
                        '--max-time', '1800', '-sS', url, '-o', str(partial)], check=True)
        partial.rename(destination)
    digest = hashlib.sha256()
    with destination.open('rb') as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    row = dict(resource_id=resource_id, kind=kind, authoritative_url=url, release=release,
               assembly=assembly, bytes=destination.stat().st_size, sha256=digest.hexdigest(),
               retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
               license_reuse=license_note, cache_path=str(destination))
    manifest = Path('metadata/reference_resources.tsv' if kind == 'reference'
                    else 'metadata/phase3a_source_provenance.tsv')
    rows = []
    if manifest.exists():
        with manifest.open() as handle:
            rows = list(csv.DictReader(handle, delimiter='\t'))
    previous = [r for r in rows if r['resource_id'] == resource_id]
    if previous:
        if previous[0]['sha256'] != row['sha256'] or previous[0]['authoritative_url'] != url:
            raise ValueError('Resource identity changed; do not silently overwrite provenance')
        return previous[0]
    rows.append(row)
    with manifest.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(resource_id, row['bytes'], row['sha256'], flush=True)
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ('resource_id', 'url', 'destination', 'release', 'assembly', 'license_note', 'kind'):
        p.add_argument(name)
    acquire(**vars(p.parse_args()))
