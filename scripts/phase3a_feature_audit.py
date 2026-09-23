#!/usr/bin/env python3
"""Join annotation-only controls and audit sequence grouping without outcomes."""
import json
from pathlib import Path
import pandas as pd


def main():
    feature = pd.read_csv('results/tables/sequence_annotation_features.tsv', sep='\t')
    kmers = pd.read_csv('results/tables/unique_kmers31.tsv', sep='\t')
    kval = pd.read_csv('.cache/phase3a/qc/miniquant/kvalues.tsv', sep='\t')
    if feature.transcript_id.duplicated().any() or kmers.transcript_id.duplicated().any() or kval.Gene_id.duplicated().any():
        raise ValueError('Duplicate identifiers in feature inputs')
    if set(feature.transcript_id) != set(kmers.transcript_id):
        raise ValueError('Sequence and unique-kmer transcript universes differ')
    joined = feature.merge(kmers, on='transcript_id', how='left', validate='1:1')
    joined = joined.merge(kval.rename(columns={'Gene_id':'gene_id','K-value':'miniquant_kvalue'}),
                          on='gene_id', how='left', validate='m:1')
    joined.to_csv('results/tables/identifiability_sequence_features.tsv', sep='\t', index=False)
    duplicate = feature.groupby('sequence_sha256').agg(transcripts=('transcript_id','size'),
                                                        genes=('gene_id','nunique'))
    crossgene = duplicate[duplicate.genes > 1]
    duplicated_hashes = set(crossgene.index)
    summary = {
        'feature_transcripts':len(feature),
        'kmer_transcripts':len(kmers),
        'miniquant_genes_reported':len(kval),
        'miniquant_kvalue_available_transcripts':int(joined.miniquant_kvalue.notna().sum()),
        'unique_kmer_fraction_available':int(joined.unique_kmer_fraction.notna().sum()),
        'cross_gene_exact_sequence_hashes':len(crossgene),
        'cross_gene_exact_sequence_transcripts':int(feature.sequence_sha256.isin(duplicated_hashes).sum()),
        'cross_gene_exact_sequence_max_genes':int(crossgene.genes.max()) if len(crossgene) else 0,
        'feature_missingness':{c:int(joined[c].isna().sum()) for c in [
            'sequence_length','gc_fraction','homopolymer_fraction','low_complexity_fraction',
            'sequence_entropy','unique_kmer_fraction','unique_exonic_bases','unique_junction_count',
            'max_exon_jaccard','incidence_rank_deficiency','miniquant_kvalue']},
        'outcome_inputs_read':False,'structure_inputs_read':False}
    Path('results/tables/feature_audit_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
