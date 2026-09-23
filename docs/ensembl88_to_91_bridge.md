# Ensembl 88 to 91 transcript bridge

GSE132099's [GEO processing record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM3842467) pins Ensembl 88 GRCh38. The authoritative [Ensembl archive](https://ftp.ensembl.org/pub/release-88/) supplied the release 88 GTF, cDNA and ncRNA FASTA. The release 88 GTF header specifies GRCh38.p10, matching the existing release 91 genomic reconstruction used for SG-NEx. Exact resource URLs, sizes, SHA256, UTC dates and reuse notes are in `metadata/reference_resources.tsv` and `metadata/phase3b_resources.tsv`.

| Release 88 resource | Compressed bytes | SHA256 |
|---|---:|---|
| GTF | 46,157,774 | `ba9cb13686c3a4429724dfd6f6e52df92d1cc59675a4590d4a854f64ce633f46` |
| cDNA FASTA | 64,661,761 | `462823cdad614a2a77763004735fb9d4fabf3bb691b57737697208679c26cb86` |
| ncRNA FASTA | 9,318,335 | `298925becc19859d420f5fbd70994c72ab82df1aedc94515faf86b000b2157b4` |

`scripts/phase3b_bridge.py` preserves the unversioned GSE132099 ID, finds a unique Ensembl 88 stable ID, checks the reported length against release 88 exons and FASTA, reconstructs release 88 sequence from the GRCh38.p10 genome, and compares release 88 with the previously sequence-validated SG-NEx/Ensembl 91 transcript. It compares full versioned ID, stable ID, gene, chromosome, strand, exon intervals, length and SHA256 of transcript sequence. An A requires exact full release-to-release ID, exon definition and sequence. A B permits only a benign version or metadata difference with equal sequence and exons. C is a material definition change; D is ambiguous or internally unvalidated; E is absent. Processed GSE132099 IDs are unversioned, so the A designation is exact **release 88 versus release 91 reference identity**, anchored to the study-pinned release and processed length; it does not falsely claim the processed file itself contains a full versioned ID.

| Class | GSE132099 transcripts |
|---|---:|
| A | 16,268 |
| B | 0 |
| C | 17 |
| D | 5 |
| E | 5 |
| Total | 16,295 |

All 16,288 source FASTA candidates reconstructed exactly from the genome. The five D records lacked source FASTA; the five E records were absent from one reference. The 17 C records had changed sequence, exon definition or length. The A set contains 16,055 transcripts meeting the prespecified 50-base/0.5 callable rule; 213 A records fail coverage. This is the primary rescue count. Full per-transcript evidence is `results/tables/ensembl88_to_91_transcript_bridge.tsv`, generated programmatically. No reactivity values, SG-NEx outcomes or LongBench outputs enter the bridge.
