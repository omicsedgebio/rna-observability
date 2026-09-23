#!/usr/bin/env python3
"""Inventory GSE149767 K562 processed profiles without sequencing outcomes."""
import csv
import hashlib
import json
import tarfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIVO = ROOT / '.cache/phase3b/structure/GSE149767_k562_vivo_icshape.tar.gz'
MAPS = ROOT / '.cache/phase3b/structure/GSE149767_k562maps.tar.gz'
OUT = ROOT / 'results/tables/gse149767_compatibility.tsv'
SUMMARY = ROOT / 'results/tables/gse149767_compatibility_summary.json'


def prefix(name):
    return Path(name).name.split('.NM_')[0] + '.NM_' + Path(name).name.split('.NM_')[1].split('.')[0] if '.NM_' in name else (
        Path(name).name.split('.NR_')[0] + '.NR_' + Path(name).name.split('.NR_')[1].split('.')[0] if '.NR_' in name else None)


def main():
    vivo = {}
    with tarfile.open(VIVO, 'r|gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.rx'):
                continue
            key = prefix(member.name)
            if not key or key in vivo:
                raise ValueError('Duplicate or unparsable vivo profile: ' + member.name)
            n = callable1 = callable2 = 0
            for line in archive.extractfile(member):
                values = line.split()
                if len(values) != 2:
                    raise ValueError('Unexpected vivo rx columns')
                n += 1
                callable1 += values[0] != b'-999.0'
                callable2 += values[1] != b'-999.0'
            vivo[key] = (n, callable1, callable2)
    targets = defaultdict(list)
    with (ROOT / 'results/tables/reference_transcript_validation.tsv').open() as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            if row['fasta_reconstruction_equal'] == 'True':
                targets[row['sequence_sha256']].append(row)
    maps = defaultdict(list)
    with tarfile.open(MAPS, 'r|gz') as archive:
        for member in archive:
            if not member.isfile() or not member.name.endswith('.map'):
                continue
            key = prefix(member.name)
            if key not in vivo:
                continue
            seq = []
            for line in archive.extractfile(member):
                fields = line.split()
                if len(fields) != 4 or int(fields[0]) != len(seq) + 1:
                    raise ValueError('Malformed map: ' + member.name)
                seq.append(fields[3].decode().upper().replace('U', 'T'))
            digest = hashlib.sha256(''.join(seq).encode()).hexdigest()
            maps[key].append((len(seq), digest, member.name))
    fields = ['profile_id', 'refseq_id', 'vivo_length', 'vivo_callable_rep1',
              'vivo_callable_rep2', 'map_count', 'map_length', 'map_sequence_sha256',
              'ensembl91_match_count', 'ensembl91_transcript_id', 'compatibility']
    counts = Counter()
    with OUT.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for key, (length, call1, call2) in sorted(vivo.items()):
            possible = maps[key]
            single = possible[0] if len(possible) == 1 else None
            hits = targets.get(single[1], []) if single and single[0] == length else []
            if len(possible) != 1:
                classification = 'NO_UNIQUE_SEQUENCE_MAP'
            elif single[0] != length:
                classification = 'MAP_VIVO_LENGTH_MISMATCH'
            elif len(hits) == 1:
                classification = 'UNIQUE_EXACT_ENSEMBL91_SEQUENCE'
            elif hits:
                classification = 'MULTIPLE_ENSEMBL91_SEQUENCE_MATCHES'
            else:
                classification = 'NO_EXACT_ENSEMBL91_SEQUENCE'
            counts[classification] += 1
            writer.writerow(dict(profile_id=key, refseq_id=key.split('.')[-1],
                vivo_length=length, vivo_callable_rep1=call1,
                vivo_callable_rep2=call2, map_count=len(possible),
                map_length=single[0] if single else 'NA',
                map_sequence_sha256=single[1] if single else 'NA',
                ensembl91_match_count=len(hits),
                ensembl91_transcript_id=hits[0]['transcript_id'] if len(hits) == 1 else 'NA',
                compatibility=classification))
    summary = dict(vivo_profiles=len(vivo), matched_fshape_maps=sum(bool(maps[x]) for x in vivo),
                   categories=dict(counts), sequencing_outcomes_read=False,
                   structure_vs_sequencing_tested=False)
    SUMMARY.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
