# Phase 2 report

## Verdict

**MODIFY.** The processed data are accessible and the core QC can proceed, but a primary endpoint is not yet defensible across quantifiers, structure coverage is selected, K562 structure is a cell-context reference rather than a matched measurement, and no strong independent structure validation dataset has been established.

## Data downloaded

| File | Source | Size | SHA256 |
|---|---|---:|---|
| transcript.rds | SG-NEx S3 processed transcript estimates | 669,521,420 bytes | 51d41a85766e536fc995965d820facc3e2e02bb99391330b9df4a46ff9a3a7d2 |
| metadata.rds | SG-NEx S3 metadata and annotation | 26 MB on disk | d37b4e2bf289ea46b59c2cd47c23c036f0708b1c31a5c235687dbfd1048b24b |
| spikein.rds | SG-NEx S3 spike in estimates | 62 MB on disk | d2d085c5c7108cb2c5e015eed192cf54e464effe639ed5b80b2a4f315bef9084 |
| GSM4333260_K562.out.txt.gz | GEO GSE145805 processed icSHAPE | 87 MB on disk | e7131005627f39b0054074ac59c4d12d67ac2e3e87058926a56e691c7891c758 |

The total is approximately 815 MB. All files are ignored cache files. No raw sequencing files were downloaded.

## SG-NEx schema

The transcript object has 61,576,601 rows, 212,379 unique transcript IDs, 139 runs, five quantification methods, six protocols, and 15 cell lines. `estimates` and `normEst` are workflow-specific values with large zero fractions and are not established as a common abundance scale. The metadata includes explicit protocol, run, replicate, library, RNA extraction, cell line, and Ensembl 91 fields.

## Replicates

Runs are nested within libraries and RNA preparations. Biological source or RNA preparation, not run, is the independent unit. K562 has 14 ONT rows, three Illumina rows, and one PacBio row, with repeated technical and protocol runs. The hierarchy is in `metadata/replicate_hierarchy.tsv`.

## Transcript mapping

The SG-NEx annotation has 200,310 versioned transcript records. The icSHAPE inventory has 69,416 versioned records. Exact versioned matches are 65,913, version-only stable-ID matches are 87, ambiguous structure stable IDs are 26, unmatched SG-NEx records are 134,284, and unmatched structure records are 3,364. Stable-ID matches remain QC candidates until sequence and exon-definition checks are completed.

## Structure coverage

There are 69,416 structure rows and 53,728,868 callable nucleotide values. Using a provisional callable fraction threshold of 0.5, 36,433 transcripts are usable. `NULL` is missing, not zero. Coverage is likely abundance and length dependent, and GC is not yet available from the processed objects. No structure versus outcome association was calculated.

## K562 compatibility

Classification B: cell-context reference structure. The shared cell line is not a matched culture, RNA preparation, or replicate. Independent laboratory and assay batch are high concerns. Integration is conditionally defensible only with explicit batch and missingness limitations.

## Outcome recommendation

Primary candidate: a quantifier-compatible, replicate-aggregated signed log abundance contrast, with fixed offset and a documented common abundance scale. Secondary candidates are absolute contrast, detection disagreement, rank concordance, isoform fraction disagreement, dropout, splice-chain agreement, full-length recovery, end completeness, and replicate variance. No outcome is frozen until quantifier semantics and zero handling are resolved.

## Identifiability baseline

Transcript count per gene, exon sharing, unique junctions, effective unique length, and transcript similarity are feasible from Ensembl 91 plus a matching transcript sequence resource. A miniQuant-style compatibility or rank-deficiency baseline is feasible only after reproducing the published matrix construction and checking licensing. GC and sequence uniqueness remain pending the exact reference FASTA.

## Quantifier sensitivity

Illumina RSEM and Salmon, and long-read NanoCount, Bambu, and Salmon outputs have different transcript coverage and zero fractions. Quantifier and annotation can therefore mimic platform disagreement. Workflow-stratified sensitivity is mandatory.

## Licensing

SG-NEx is identified as CC BY-NC 4.0. GEO access does not establish blanket redistribution rights for GSE145805. LongBench metadata indicates CC BY 4.0. Academic analysis is feasible with attribution and source-specific review. Commercial website reuse is unresolved and requires legal review.

## Structural external validation

No strong independent human dataset combining experimental structure and matched multi-platform transcript measurements was established. HEK293 structure resources are weak for the full incremental test. LongBench remains a locked platform validation resource without structure outcomes.

## LongBench lock

Confirmed. Only metadata needed for compatibility and licensing was viewed. No transcript-level outcomes or performance were inspected.

## Major risks

The main risks are workflow-specific abundance semantics, cross-study biological mismatch, structure coverage selection, transcript-version ambiguity, insufficient independent biological replication, quantifier and annotation confounding, and lack of strong independent structure validation.

## Next phase

Review this report. If approved, freeze a data and endpoint plan, obtain the exact Ensembl 91 sequence and exon resources, complete mapping validation and replicate-aware outcome QC, and only then begin prespecified baseline modeling. Do not inspect LongBench outcomes before model freeze.
