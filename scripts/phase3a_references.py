#!/usr/bin/env python3
"""Validate SG-NEx references, classify mappings, build annotation/sequence QC.

Uses only icSHAPE inventory identifiers, lengths and callable counts, never scores.
"""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from rnaobs.core import (read_gtf, fasta_records, reconstruct, stable_id,
                         unique_index, sequence_features, annotation_features)
from pyfaidx import Fasta


def table(path, rows):
    rows = iter(rows)
    first = next(rows)
    with Path(path).open('w', newline='') as out:
        w = csv.DictWriter(out, fieldnames=list(first), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerow(first); w.writerows(rows)


def main():
    ref = Path('.cache/phase3a/references')
    genome_path = ref/'ensembl91.genome.fa'
    if not genome_path.exists():
        with gzip.open(ref/'ensembl91.genome.fa.gz', 'rb') as inp, genome_path.open('wb') as out:
            shutil.copyfileobj(inp, out)
    genome = Fasta(str(genome_path), as_raw=True, sequence_always_upper=True)
    annotation = read_gtf(ref/'ensembl91.gtf.gz')
    print('GTF transcripts',len(annotation),flush=True)
    sequences = {}
    for name in ['ensembl91.cdna.fa.gz','ensembl91.ncrna.fa.gz']:
        for tid, sequence in fasta_records(ref/name):
            if tid in sequences:
                raise ValueError('Duplicate exact transcript ID in combined Ensembl FASTA')
            sequences[tid] = sequence.upper()
    sgnex_sequences = dict(fasta_records(ref/'sgnex.cdna.ncrna.fa'))
    sgnex_by_stable = unique_index(sgnex_sequences.items(), lambda x: stable_id(x[0]))
    ann_by_stable = unique_index(annotation.values(), lambda x: stable_id(x.identifier))
    augmented = read_gtf(ref/'sgnex.augmented.gtf')
    augmented_by_stable = unique_index(augmented.values(), lambda x: stable_id(x.identifier))
    refrows, reconstructed = [], {}
    for tid, tx in sorted(annotation.items()):
        seq = sequences.get(tid)
        rec = reconstruct(tx, genome) if tx.chrom in genome else None
        reconstructed[tid] = rec
        mirror = sgnex_by_stable.get(stable_id(tid), [])
        aug = augmented_by_stable.get(stable_id(tid), [])
        refrows.append(dict(transcript_id=tid, stable_transcript_id=stable_id(tid), gene_id=tx.gene,
                            chromosome=tx.chrom, strand=tx.strand, exon_count=len(tx.exons),
                            transcript_length=tx.length, transcript_biotype=tx.biotype,
                            exon_coordinates_0based=';'.join(f'{s}-{e}' for s,e in tx.exons),
                            fasta_available=seq is not None, genome_available=rec is not None,
                            fasta_reconstruction_equal=seq is not None and seq==rec,
                            sgnex_mirror_equal=len(mirror)==1 and mirror[0][1].upper()==seq,
                            augmented_exons_equal=len(aug)==1 and aug[0].exons==tx.exons and
                            aug[0].chrom.removeprefix('chr')==tx.chrom and aug[0].strand==tx.strand,
                            sequence_sha256=hashlib.sha256(seq.encode()).hexdigest() if seq else 'NA'))
    table('results/tables/reference_transcript_validation.tsv', refrows)
    with open('results/tables/sgnex_transcript_annotation.tsv') as handle:
        sgnex = list(csv.DictReader(handle, delimiter='\t'))
    for row in sgnex:
        row['version_recovered_from_gtf'] = False
        if row['sgnex_versioned_transcript_id'] in ('NA',''):
            candidates=ann_by_stable.get(row['sgnex_transcript_id'],[])
            if len(candidates)!=1:
                raise ValueError('Cannot recover a unique version from exact Ensembl 91 GTF')
            row['sgnex_versioned_transcript_id']=candidates[0].identifier
            row['version_recovered_from_gtf']=True
    with open('results/tables/icshape_transcript_inventory.tsv') as handle:
        structure = list(csv.DictReader(handle, delimiter='\t'))
    structure_index = unique_index(structure, lambda r: stable_id(r['structure_transcript_id']))
    target_index = unique_index(sgnex, lambda r: stable_id(r['sgnex_versioned_transcript_id']))
    ref_index = {r['transcript_id']:r for r in refrows}
    mappings, seen, counts = [], set(), Counter()
    for r in sgnex:
        tid = r['sgnex_versioned_transcript_id']; stable = stable_id(tid)
        candidates = structure_index.get(stable, [])
        definition = annotation.get(tid)
        sid = ';'.join(x['structure_transcript_id'] for x in candidates) or 'NA'
        seen.update(x['structure_transcript_id'] for x in candidates)
        category, reason = 'E', 'no_structure_stable_id'
        if candidates:
            category, reason = 'D', 'icshape_source_exons_and_sequence_unavailable'
            if len(candidates)>1 or len(target_index[stable])>1:
                reason = 'duplicate_stable_id'
            elif definition and int(candidates[0]['reported_length']) != definition.length:
                category, reason = 'C', 'reported_transcript_length_changed'
        counts[category] += 1
        check = ref_index.get(tid,{})
        mappings.append(dict(sgnex_transcript_id=tid, structure_transcript_id=sid,
            stable_transcript_id=stable, gene_id=r['gene_id'], mapping_class=category,
            reason=reason, primary_eligible=False, exact_version_id=(sid==tid),
            version_recovered_from_gtf=r['version_recovered_from_gtf'],
            chromosome=definition.chrom if definition else 'NA', strand=definition.strand if definition else 'NA',
            exon_count=len(definition.exons) if definition else 'NA',
            exon_coordinates_0based=';'.join(f'{s}-{e}' for s,e in definition.exons) if definition else 'NA',
            sgnex_reported_length=r['tx_len'], ensembl_length=definition.length if definition else 'NA',
            icshape_reported_length=candidates[0]['reported_length'] if len(candidates)==1 else 'NA',
            sgnex_gene_agrees=definition is not None and stable_id(r['gene_id'])==definition.gene,
            sgnex_length_agrees=definition is not None and int(r['tx_len'])==definition.length,
            sgnex_exon_count_agrees=definition is not None and int(r['nexon'])==len(definition.exons),
            target_sequence_verified=check.get('fasta_reconstruction_equal',False),
            target_sequence_sha256=check.get('sequence_sha256','NA'),
            structure_gene_id='UNAVAILABLE',structure_chromosome='UNAVAILABLE',structure_strand='UNAVAILABLE',
            structure_exon_count='UNAVAILABLE',structure_exon_coordinates='UNAVAILABLE',
            structure_sequence_sha256='UNAVAILABLE'))
    table('results/tables/transcript_mapping_validated.tsv', mappings)
    unmatched = [r for r in structure if r['structure_transcript_id'] not in seen]
    table('results/tables/transcript_mapping_unmatched_structure.tsv', unmatched)
    summary = dict(annotation_transcripts=len(annotation), ensembl_fasta_sequences=len(sequences),
        sgnex_mirror_sequences=len(sgnex_sequences),
        genome_reconstruction_equal=sum(r['fasta_reconstruction_equal'] for r in refrows),
        genome_unavailable=sum(not r['genome_available'] for r in refrows),
        fasta_unavailable=sum(not r['fasta_available'] for r in refrows),
        sequence_discordant=sum(r['fasta_available'] and r['genome_available'] and not r['fasta_reconstruction_equal'] for r in refrows),
        sgnex_mirror_equal=sum(r['sgnex_mirror_equal'] for r in refrows),
        augmented_exons_equal=sum(r['augmented_exons_equal'] for r in refrows),
        sgnex_records=len(sgnex), mapping_classes={c:counts[c] for c in 'ABCDE'},
        sgnex_missing_versions_recovered=sum(r['version_recovered_from_gtf'] for r in sgnex),
        reasons=dict(Counter(r['reason'] for r in mappings)),
        unmatched_structure=len(unmatched), primary_eligible=0,
        exact_id_equal_length_provisional=sum(r['exact_version_id'] and r['reason']=='icshape_source_exons_and_sequence_unavailable' for r in mappings))
    print(json.dumps(summary,indent=2),flush=True)
    Path('results/tables/reference_mapping_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Feature universe is all authoritative GTF transcripts with reconstructed equal sequence.
    valid = {r['transcript_id'] for r in refrows if r['fasta_reconstruction_equal']}
    architecture = annotation_features(annotation.values())
    features = []
    with (ref/'validated_transcripts.fa').open('w') as fasta:
        for tid in sorted(valid):
            tx = annotation[tid]; seq = sequences[tid]
            fasta.write('>'+tid+'\n'+seq+'\n')
            features.append(dict(transcript_id=tid, stable_transcript_id=stable_id(tid), gene_id=tx.gene,
                                 transcript_biotype=tx.biotype, **sequence_features(seq), **architecture[tid]))
    table('results/tables/sequence_annotation_features.tsv', features)
    print('FEATURES_COMPLETE',len(features),flush=True)


if __name__ == '__main__':
    main()
