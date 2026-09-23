# SG-NEx processed data QC

The Phase 2 download used the SG-NEx processed transcript object, metadata object, and optional spike in object. No FASTQ, BAM, CRAM, or raw signal files were downloaded.

The transcript object is an R data.table with 61,576,601 rows and 13 columns: `tx_name`, `gene_name`, `estimates`, `runname`, `method`, `ntotal`, `protocol`, `protocol_general`, `protocol_method`, `short_read`, `runname_method`, `cellLine`, and `normEst`. It contains 212,379 unique transcript identifiers, 139 runs, five methods, six protocols, and 15 cell lines. `estimates` and `normEst` are method and workflow outputs, not a demonstrated common molar scale. The object contains 74.65% zero values in both fields. They must not be called TPM or CPM without source workflow documentation.

The metadata object contains 22 named components, including `sampleData` (130 rows), `sampleData_sr` (21 rows), `samples` (139 rows), Ensembl 91 transcript and gene annotations, protocol labels, cell line provenance, RNA extraction fields, library fields, and a six row PacBio table. SG-NEx uses GRCh38 with Ensembl 91 in the processed release.

K562 has 14 ONT rows, three Illumina rows, and one PacBio row in `samples`. ONT rows include direct RNA, direct cDNA, PCR cDNA, and stranded cDNA protocols. The object explicitly records `bioRep`, `techRep`, run names, RNA preparation labels, and library identifiers. The Illumina rows have separate RSEM and Salmon outputs. This supports quantifier sensitivity analysis, but it does not make outputs from different quantifiers directly comparable.

The spike in object has two data.tables with 7,422,995 and 2,163,455 rows, respectively, covering 58,494 spike in transcript identifiers and 34 runs. Most values are zero. Known spike in concentrations and the exact calibration table must be linked before a true measurement error endpoint is claimed.

Checks and compact summaries are in `results/tables/sgnex_transcript_object_summary.tsv`, `results/tables/sgnex_measurement_groups.tsv`, `results/tables/k562_measurement_groups.tsv`, and `results/tables/spikein_object_summary.tsv`. Large source-derived tables remain ignored under `.cache` or data cache paths.
