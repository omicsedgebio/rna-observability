# External validation search for the structure increment

The search looked for independent human cell data combining experimental transcriptome-wide structure with Illumina transcriptomics and ONT or PacBio transcript measurements. GSE74353 provides in vivo icSHAPE in HEK293T, but uses an older GRCh37.74 coordinate context and does not provide a matched SG-NEx-style multi-platform benchmark. RNA structure maps across mammalian compartments provide experimental structure in HEK293 cells, but not a clearly matched cross-platform transcript measurement panel. Recent direct-RNA structure probing in Candida albicans is technologically relevant but not a human-cell validation set.

| Strategy | Classification | Reason |
|---|---|---|
| Independent human structure plus matched ONT and Illumina transcript quantification | UNAVAILABLE in the inspected resources | No dataset met all criteria without raw-data reconstruction or unverified compatibility. |
| HEK293T icSHAPE plus independent transcriptomics | WEAK | Structure exists, but cell state, annotation, and platform pairing are not matched. |
| Structure-only external replication of feature distributions | MODERATE | Can test feature reproducibility, not the incremental measurement hypothesis. |
| Locked LongBench platform validation without structure | MODERATE | Can validate a general measurement framework, not the structure increment. |

The honest Phase 2 position is that an independent structure-validation dataset is not currently established. A future strong validation would require a separate laboratory, experimental structure, compatible transcript definitions, and processed multi-platform measurements from the same biological context.
