#!/usr/bin/env python3
"""Bridge GSE132099 Ensembl 88 to SG-NEx Ensembl 91 without reactivity."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

from pyfaidx import Fasta

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from rnaobs.core import fasta_records, read_gtf, reconstruct, stable_id, unique_index

ROOT = Path('.')
OUT = ROOT/'results/tables/ensembl88_to_91_transcript_bridge.tsv'
SUMMARY = ROOT/'results/tables/ensembl88_to_91_bridge_summary.json'


def classify(source, target, source_sequence, target_digest, reported_length):
    """Classify only after the study-pinned release 88 source is internally valid."""
    if source is None or target is None:
        return 'E','absent_from_one_reference'
    if source_sequence is None:
        return 'D','source_fasta_unavailable'
    if source.length != reported_length or len(source_sequence) != source.length:
        return 'D','study_length_or_source_fasta_inconsistent'
    if target_digest is None:
        return 'D','target_fasta_unavailable'
    equal_sequence = hashlib.sha256(source_sequence.encode()).hexdigest()==target_digest
    equal_definition = (source.gene,source.chrom,source.strand,source.exons)==(
        target.gene,target.chrom,target.strand,target.exons)
    if not equal_sequence or not equal_definition or source.length != target.length:
        return 'C','sequence_or_exon_definition_changed'
    return ('A','exact_id_sequence_exons') if source.identifier==target.identifier else (
        'B','benign_version_or_metadata_difference')


def main():
    inventory=list(csv.DictReader(open('results/tables/gse132099_structure_inventory.tsv'),delimiter='\t'))
    study_ids=Counter(row['structure_transcript_id'] for row in inventory)
    a88=read_gtf('.cache/phase3b/references/ensembl88.gtf.gz')
    a91=read_gtf('.cache/phase3a/references/ensembl91.gtf.gz')
    idx88=unique_index(a88.values(),lambda tx: stable_id(tx.identifier))
    idx91=unique_index(a91.values(),lambda tx: stable_id(tx.identifier))
    ref91={}
    with open('results/tables/reference_transcript_validation.tsv') as stream:
        for row in csv.DictReader(stream,delimiter='\t'):
            ref91[row['transcript_id']]=row
    needed88={tx.identifier for row in inventory
              for tx in idx88.get(stable_id(row['structure_transcript_id']),[])}
    seq88={}
    for path in ['.cache/phase3b/references/ensembl88.cdna.fa.gz',
                 '.cache/phase3b/references/ensembl88.ncrna.fa.gz']:
        for tid,seq in fasta_records(path):
            if tid in needed88:
                if tid in seq88: raise ValueError('Duplicate Ensembl 88 FASTA ID')
                seq88[tid]=seq.upper()
    genome=Fasta('.cache/phase3a/references/ensembl91.genome.fa',
                 as_raw=True,sequence_always_upper=True)
    fields=['structure_transcript_id','stable_transcript_id','reported_length',
            'ensembl88_transcript_id','ensembl91_sgnex_transcript_id','gene_id',
            'chromosome','strand','ensembl88_exon_count','ensembl91_exon_count',
            'ensembl88_exons_0based','ensembl91_exons_0based','ensembl88_length',
            'ensembl91_length','ensembl88_sequence_sha256','ensembl91_sequence_sha256',
            'source_fasta_genome_equal','sequence_equal','exons_equal',
            'mapping_class','reason','callable_bases','callable_fraction','primary_eligible']
    counts=Counter(); reasons=Counter(); eligible=0; source_reconstructed=0
    with OUT.open('w',newline='') as output:
        writer=csv.DictWriter(output,fieldnames=fields,delimiter='\t',lineterminator='\n')
        writer.writeheader()
        for row in inventory:
            sid=row['structure_transcript_id']; stable=stable_id(sid)
            source_candidates=idx88.get(stable,[])
            target_candidates=idx91.get(stable,[])
            source=source_candidates[0] if len(source_candidates)==1 else None
            target=target_candidates[0] if len(target_candidates)==1 else None
            sequence=seq88.get(source.identifier) if source else None
            source_valid=False
            if source and sequence and source.chrom in genome:
                source_valid=(reconstruct(source,genome)==sequence)
                source_reconstructed += int(source_valid)
            target_row=ref91.get(target.identifier,{}) if target else {}
            target_digest=target_row.get('sequence_sha256')
            if target_row.get('fasta_reconstruction_equal')!='True':
                target_digest=None
            if study_ids[sid]>1 or len(source_candidates)>1 or len(target_candidates)>1:
                cl,reason='D','duplicate_or_ambiguous_stable_id'
            elif source is None or target is None:
                cl,reason='E','absent_from_ensembl88_or_91'
            elif sequence and not source_valid:
                cl,reason='D','source_sequence_not_reconstructed_on_grch38_p10'
            else:
                cl,reason=classify(source,target,sequence,target_digest,int(row['reported_length']))
            equal_seq=(hashlib.sha256(sequence.encode()).hexdigest()==target_digest
                       if sequence and target_digest else False)
            equal_exons=(source.exons==target.exons if source and target else False)
            ok=cl in ('A','B') and int(row['callable_bases'])>=50 and float(row['callable_fraction'])>=.5
            counts[cl]+=1;reasons[reason]+=1;eligible+=int(ok)
            writer.writerow(dict(structure_transcript_id=sid,stable_transcript_id=stable,
                reported_length=row['reported_length'],
                ensembl88_transcript_id=source.identifier if source else 'NA',
                ensembl91_sgnex_transcript_id=target.identifier if target else 'NA',
                gene_id=target.gene if target else 'NA',
                chromosome=target.chrom if target else 'NA',strand=target.strand if target else 'NA',
                ensembl88_exon_count=len(source.exons) if source else 'NA',
                ensembl91_exon_count=len(target.exons) if target else 'NA',
                ensembl88_exons_0based=';'.join(f'{a}-{b}' for a,b in source.exons) if source else 'NA',
                ensembl91_exons_0based=';'.join(f'{a}-{b}' for a,b in target.exons) if target else 'NA',
                ensembl88_length=source.length if source else 'NA',
                ensembl91_length=target.length if target else 'NA',
                ensembl88_sequence_sha256=hashlib.sha256(sequence.encode()).hexdigest() if sequence else 'NA',
                ensembl91_sequence_sha256=target_digest or 'NA',
                source_fasta_genome_equal=source_valid,sequence_equal=equal_seq,
                exons_equal=equal_exons,mapping_class=cl,reason=reason,
                callable_bases=row['callable_bases'],
                callable_fraction=row['callable_fraction'],primary_eligible=ok))
    summary=dict(study_transcripts=len(inventory),ensembl88_gtf_transcripts=len(a88),
        ensembl91_gtf_transcripts=len(a91),ensembl88_fasta_study_candidates=len(seq88),
        ensembl88_fasta_genome_reconstructed=source_reconstructed,
        mapping_classes={k:counts[k] for k in 'ABCDE'},reasons=dict(reasons),
        a_or_b_coverage_eligible=eligible,reactivity_values_read=False,
        sequencing_outcomes_read=False)
    SUMMARY.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
