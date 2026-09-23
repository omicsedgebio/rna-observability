# SG-NEx processed-data feasibility

Study identity: Chen et al., Nature Methods 2025, DOI [10.1038/s41592-025-02623-4](https://doi.org/10.1038/s41592-025-02623-4), ENA PRJEB44348. Seven core lines in the publication: A549, HCT116, HepG2, K562, MCF7, H9, HEYA8. Public manifests include extensions; core is not a rectangular sample-by-platform design. Five methods include Illumina, three ONT protocols and PacBio IsoSeq. Spike-in families include Sequins, SIRV and ERCC; sample-level presence and mixtures must be audited.

Official [S3 manuscript README](https://sg-nex-data.s3.ap-southeast-1.amazonaws.com/data/processed_data/manuscript/README.txt) and [processed listing](https://sg-nex-data.s3.ap-southeast-1.amazonaws.com/?list-type=2&prefix=data/processed_data/manuscript/processed/&max-keys=1000) inspected 2026-09-22:

| Object | Bytes from listing | Purpose |
|---|---:|---|
| combinedExpressionDataTranscript_19June2023.rds | 669521420 | Transcript estimates across samples/methods |
| general_list2023-08-29.rds | 27131354 | Sample/annotation object |
| combinedExpressionDataList_spikein_25May.rds | 65329913 | Spike-in-only estimates |
| combinedExpressionDataCountsList_5May2023.rds | 314273081 | Differential-isoform subset, not automatically complete counts |
| combinedExpressionDataGene_19June2023.rds | 109338919 | Gene estimates |
| combinedExpressionDataTranscript_trimreads_20May2024.rds | 1069296886 | Trimmed-read analysis; not the primary input |
| dominant_typeData_25May2023.rds | 41011537 | Derived classification, not independent truth |

Minimal candidate payload: ~697 MB for transcript plus annotation; ~762 MB with spike-ins; ~0.85 GB with K562 structure (approximate decimal total; GEO display units differ). Uncompressed memory footprint and object schemas UNKNOWN. No payload downloaded. Processed availability is verified at catalog level, not yet validated for this endpoint.

Check RDS schema, packages, units, quantifier version and reference universe before choosing an outcome. Long-read read fractions and short-read length-corrected abundances must not be blindly interchanged. Processed object dates precede the present metadata release; verify which basecalling/annotation release produced each object. Current repository notes Guppy 6.4.2 / minimap2 2.22; ENA manifest basecaller labels may describe older deposits.

GRCh38 / Ensembl 91 documented in [data-access tutorial](https://github.com/GoekeLab/sg-nex-data/blob/master/docs/AWS_data_access_tutorial.md). Matched m6A is partial; K562 directRNA labels 4/5/6 marked yes in manifest. Modification calls from the same nanopore signal can leak technology behavior. Orthogonal m6ACE-seq needs sample-specific provenance.

Reuse: [AWS registry](https://registry.opendata.aws/sgnex/) specifies CC BY-NC 4.0. Do not infer an unrestricted dataset license from a code repository or open-access article. Later company use/redistribution needs clarification. The repository records a correction to H9/HEYA8 spike-in information; use corrected manifest with provenance.

Next step after review: license/provenance clarification and bounded processed-only schema/coordinate QC. FASTQ/BAM are not currently necessary.
