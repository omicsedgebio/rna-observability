# Phase 3C fixed cohort definition

The cohort audit starts with the 200,310 unique Ensembl 91 transcript identifiers in the SG-NEx processed K562 annotation. The structure bridge is limited to the 16,295 GSE132099 identifiers present in the Ensembl 88 inventory. Class A requires the same transcript definition in the release 88 and release 91 GTFs and identical reconstructed cDNA sequence. No gene symbol matching is used. The audit reproduces 16,268 class-A transcripts and 17 class-C, 5 class-D and 5 class-E profiles.

Structure eligibility is an assay rule, not a favorable-outcome rule: at least 50 callable GSE132099 positions and callable fraction at least 0.5. This gives 16,055 class-A profiles. The provisional platform-availability check requires a represented row for every K562 Illumina Salmon and direct-RNA Salmon run; it uses row presence only and does not convert missing rows to zero. It leaves 16,205 class-A transcripts. The intersection of this availability rule and structure eligibility is a 15,999-transcript maximum for later review.

NanoCount is not an inclusion requirement. Its processed direct-RNA output is sparse, and treating absent rows as zero would select an algorithmic representation rather than a molecular cohort. RSEM and Bambu are retained for sensitivity audits. The exact stage counts are in `results/tables/cohort_attrition.tsv` and the reproducible implementation is `scripts/phase3c_cohort_attrition.py`.

No stage uses icSHAPE reactivity, platform disagreement, residuals, or LongBench outcomes. The cohort and endpoint remain provisional pending final review of quantifier-robust detection.
