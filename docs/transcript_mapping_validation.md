# Transcript mapping validation and attrition

The Ensembl 91 side was validated using full versioned ID, stable ID including `_PAR_Y` identity, gene ID, chromosome, strand, exon count, every exon interval, transcript length and reconstructed strand-aware sequence. The 199,216 sequence-available Ensembl 91 transcripts exactly match the SG-NEx transcriptome mirror and the genomic reconstruction. The augmented SG-NEx GTF agrees with all 200,310 reference exon definitions. We recovered 1,094 version suffixes omitted in the processed SG-NEx annotation from the unique exact Ensembl 91 GTF ID; these are flagged individually.

The icSHAPE processed supplement provides versioned transcript ID, reported length and per-base values, but the source transcript FASTA and source exon annotation were not pinned or recoverable in this phase. A generic `hg38.gtf` mention is insufficient to establish release or exon/sequence equivalence. We therefore failed closed, including for exact versioned ID and length agreement. No gene symbol was used to resolve a transcript. The per-transcript table `results/tables/transcript_mapping_validated.tsv` contains explicit `UNAVAILABLE` values for icSHAPE gene, chromosome, strand, exon and sequence evidence.

| Class | Meaning | Transcripts |
|---|---|---:|
| A | Exact versioned ID and equivalent source definition | 0 |
| B | Stable ID with defensibly equivalent source definition | 0 |
| C | Stable ID but reported transcript length changed | 59 |
| D | Stable match, source exon/sequence definition unavailable or ambiguous | 65,956 |
| E | No structure stable-ID match | 134,295 |

Total SG-NEx GTF transcripts: 200,310. Of class D, 65,956 are provisional exact-ID/equal-length candidates, not validated matched molecules. A further 3,401 icSHAPE inventory records have no SG-NEx GTF match. The primary matched universe is **zero** because only A and validated B are eligible. These counts supersede Phase 2's provisional overlap after preserving pseudoautosomal suffixes and recovering omitted SG-NEx versions. The remaining blocker is independent evidence for the GSE145805 transcript model: exact annotation release or source GTF and transcript FASTA, followed by coordinate and sequence checks. A length match alone cannot promote D to A.
