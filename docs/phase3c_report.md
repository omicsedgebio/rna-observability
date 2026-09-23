# Phase 3C final scientific review

## PHASE 3C VERDICT

**MODIFY**

The validated transcript bridge and metadata-only cohort are adequate for continued design work, but the primary measurement phenotype is not yet defensible as a quantifier-robust technology phenotype. The decision is based only on measurement properties and structure-quality diagnostics. No RNA-structure versus sequencing association was examined.

## REPOSITORY AND INTERRUPTION AUDIT

The checkout was verified at branch `main`, HEAD `56bd8ae8f95f66beaf4cec13274a6be6d63dde02`, matching `origin/main`. The working tree was clean at review start. The interim handoff was checked against underlying tables, scripts and summaries rather than accepted without verification.

The cohort bridge reproduces 16,268 class-A mappings, 17 class-C, 5 class-D and 5 class-E records, with 16,055 class-A profiles passing the callable-base rule. The row-availability audit reproduces 16,205 class-A profiles with complete Illumina and direct-RNA Salmon rows and a 15,999 intersection with structure coverage eligibility. No reactivity value entered cohort selection.

Quantifier outputs contain three Illumina Salmon runs, three Illumina RSEM runs, four direct-RNA Salmon runs, four direct-RNA NanoCount runs and four direct-RNA Bambu runs. Direct-RNA NanoCount is sparse, and its absent rows were treated as missing. Bambu `normEst` was treated as CPM-like and was not assigned TPM cutoffs. The quantifier table contains explicit `NA` fields for unavailable comparisons.

Replicate handling uses biological preparation or biological replicate as the inferential unit and retains run-level variation for technical diagnostics. The three Illumina libraries and four direct-RNA libraries are distinct SG-NEx K562 preparations, not matched aliquots. Technical runs were not counted as independent biological replicates. The available endpoint is therefore protocol-specific and cross-preparation, not per-molecule error.

The spike-in calculation uses known synthetic mixture concentrations and preserves missing sparse-output rows. It is separate from endogenous disagreement. Detection-threshold calculations use only replicate support and quantifier behavior. The signed log-offset endpoint was rejected because zero fractions and reclosure cause large changes.

The structure reproducibility calculation reads only structure profiles and reference identity. It retained 72 profiles from 68 genes after exact-sequence and joint-callability filtering. The central structure hypothesis remains unseen. LongBench was not accessed beyond the lock metadata.

## QUANTIFIER STRATEGY REVIEW

The full evidence table is `results/tables/quantifier_strategy_evidence.tsv`.

| Strategy | Evidence | Verdict |
|---|---|---|
| A. Single technically preferred quantifier | Salmon has complete rows, but direct-RNA Salmon replicate rho is 0.677 and no workflow is documented as a common cross-platform molar scale | REJECT_PRIMARY |
| B. Quantifier consensus | Direct-RNA cross-method rank rho is 0.476 to 0.668; NanoCount is sparse and Bambu is CPM-like | REJECT_PRIMARY |
| C. Replicate-supported consensus | At 1 TPM, Illumina pair agreement is 0.869, direct-RNA mean agreement is 0.880, and disjoint direct-RNA agreement is 0.920 | CONDITIONAL_CANDIDATE |
| D. Named primary workflow plus sensitivity analyses | Reproducible and transparent, but the estimand would be Salmon-defined rather than quantifier-robust | CONDITIONAL_CANDIDATE |
| E. Endpoint not stabilized | Most faithful to the unresolved measurement semantics and avoids false platform claims | SUPPORTED_DECISION |

Within-method median rank correlations were 0.811 for Illumina Salmon, 0.801 for Illumina RSEM, 0.677 for direct-RNA Salmon, 0.837 for NanoCount on its represented rows, and 0.712 for Bambu. Same-run direct-RNA cross-method median rank correlations were 0.497 for Salmon versus NanoCount, 0.668 for Salmon versus Bambu and 0.476 for NanoCount versus Bambu. These results do not support promoting one ONT quantifier as a technology-independent reference. The primary phenotype is therefore not frozen.

## PHENOTYPE REVIEW

Detection is the leading candidate: 1 TPM, 2/2 Illumina support and 3/4 direct-RNA support, with intermediate support indeterminate. It has clear operational meaning and no pseudocount, but remains quantifier-aware rather than quantifier-robust. Its counts are BOTH 11,731, ILLUMINA_ONLY 20,201, DIRECT_RNA_ONLY 315, NEITHER 3,687 and INDETERMINATE 13,375 in the independently expressed universe.

Quantitative abundance agreement is restricted to positive, supported measurements and is represented by within-library percentile difference. It avoids pseudocounts but remains abundance-dependent and compositional. It is a candidate secondary, not a frozen endpoint. Replicate reliability is a separate secondary quality phenotype. Transcript-end completeness is exploratory and unavailable from the current transcript-total matrices. Isoform ambiguity remains a separate annotation and identifiability phenotype.

No composite observability score is defined. No primary phenotype is frozen because the detection state changes materially with quantifier and the quantitative scale is not common across workflows.

## SPIKE-IN REVIEW

Spike-in support for the proposed primary detection phenotype is **WEAK**. Illumina RSEM and Salmon show median mixture rank correlations of 0.745 and 0.736. Direct-RNA median rank correlations are 0.574 for NanoCount, 0.548 for Bambu and 0.503 for Salmon, with NanoCount observed fractions near 0.19 and the other explicit-output methods near 0.98. The truth is synthetic mixture truth, not endogenous transcript truth. It supports separate calibration and detection sensitivity checks but cannot establish endogenous platform accuracy or a common molar scale.

## STRUCTURE FEATURE FEASIBILITY

| Future structure feature | Classification | Reason |
|---|---|---|
| Callable fraction | SUPPORTED as assay-quality control | Directly defined from the processed masks and required for the conditional estimand; it is not a biological structure effect |
| Mean reactivity | CONDITIONAL | Defined in GSE132099, but cross-study structure-only reproducibility is limited and pooled scores lack independent per-transcript replicates |
| Median reactivity | CONDITIONAL | Same limitation; earlier cross-study transcript-median rho was 0.196 and the stricter local diagnostic retained only 72 profiles |
| High-reactivity fraction | CONDITIONAL | Defined categorical summary, but cross-study upper-quartile overlap is only 0.126 median |
| Low-reactivity fraction | CONDITIONAL | Defined categorical summary, but cross-study lower-quartile overlap is only 0.100 median |
| Local variability | UNSUPPORTED | No independent reproducibility evidence was established |
| Transcript-end structure | UNSUPPORTED | No defensible cross-study end-feature reproducibility was established |
| Splice-junction structure | UNSUPPORTED | No validated joint nucleotide and junction representation was established |

No structure feature is supported as a sequencing predictor. Conditional features may be considered only after a final prespecification and a structure-quality sensitivity analysis. This review did not compare any structure feature with a sequencing outcome.

## FINAL PRE-ENDPOINT TRANSCRIPT COHORT

`metadata/final_transcript_cohort.tsv` contains exactly **15,999** stable transcript IDs. Its status is `PRE_ENDPOINT_ELIGIBILITY`, because the endpoint itself is unresolved. Eligibility uses class-A Ensembl 88 to 91 identity, at least 50 callable GSE132099 positions, callable fraction at least 0.5, and complete row availability in the three Illumina and four direct-RNA Salmon runs. It does not use reactivity magnitude, platform disagreement or model performance. Attrition is in `results/tables/cohort_attrition.tsv`.

This is not a claim about all human or all K562 transcripts. It is a conditional, measured-transcript population. Structure availability is selective: the existing availability audit reports low positivity across abundance and other covariate strata, and unstable inverse-probability weights. Complete-case conditional inference is the only defensible current strategy; population-wide weighting is rejected.

## CV FOLDS

The provisional manifest covers 15,999 transcripts in five balanced folds and groups transcripts by gene, with exact cross-gene duplicate sequence grouping in the construction script. The current final checkout does not carry the ignored reference cache needed to reconstruct gene and sequence group labels independently from the compact manifest. Near-sequence similarity beyond exact duplicates was not assessed. Therefore the folds remain **PROVISIONAL_NOT_FROZEN** and cannot support GO_TO_BASELINES. A later freeze must rerun the grouping from pinned reference sequences and assess paralog or high-similarity leakage.

## GATE TABLE

| Gate | Assessment | Evidence |
|---|---|---|
| G1 - validated transcript cohort | PASS | 16,268 class-A mappings; 15,999 pre-endpoint eligible IDs |
| G2 - defensible replicate unit | PASS | Biological preparation is the unit; technical runs are not pseudoreplicates |
| G3 - quantifier-robust or explicitly quantifier-aware primary phenotype | FAIL | No quantifier-robust ONT detection or abundance semantics; strategy D remains conditional |
| G4 - no arbitrary zero/pseudocount dependence | PASS | Offset log endpoint rejected; detection candidate keeps indeterminate states without pseudocount |
| G5 - spike-in or measurement validation | CONDITIONAL_PASS | Synthetic truth is available, but transfer to endogenous detection is weak |
| G6 - explicit structure estimand | PASS | Conditional measured-transcript estimand is documented |
| G7 - manageable structure missingness | CONDITIONAL_PASS | Complete-case target is explicit, but positivity is poor and population inference is excluded |
| G8 - supported or conditional future structure feature | CONDITIONAL_PASS | Callable fraction is supported as QC; reactivity summaries are conditional only |
| G9 - leakage-resistant frozen CV folds | FAIL | Compact provisional folds exist, but near-sequence grouping and final freeze are incomplete |
| G10 - central structure hypothesis unseen | PASS | No structure versus sequencing analysis occurred |
| G11 - LongBench locked | PASS | Lock preserved and no transcript outcomes accessed |

G3 and G9 fail, so the GO_TO_BASELINES requirement is not met.

## SKEPTICAL SECOND PASS

Reviewer 2 identified 1 FATAL issue for progression, 6 MAJOR_BUT_MANAGEABLE issues, 1 MINOR issue and 1 NOT_SUPPORTED criticism. The FATAL issue is that the proposed primary phenotype could be a Salmon-defined algorithm artifact. Major issues are quantifier-dependent threshold labels, selective structure availability, weak independent structure reproducibility, unresolved near-sequence leakage, nonmatched biological preparations, and weak endogenous transfer from synthetic spike-ins. The full critique is in `docs/phase3c_reviewer2.md`.

## ANALYSIS PLAN AND BASELINES

The analysis plan is **not frozen**. `docs/frozen_analysis_plan.md` remains a draft. Models A, B and C were not fit. No structure feature, structure residual, Model D, structure feature importance or LongBench outcome was inspected.

## PUBLICATION OUTLOOK

**WEAK.** The project has a defensible mapping and missingness framework, but the current measurement phenotype is not stable enough for a strong manuscript claim. A publishable computational genomics paper would require a defensible quantifier-aware endpoint, frozen sequence-safe folds, and an explicit conditional estimand. A strong structure paper would additionally require a reproducible structure feature and an independent validation strategy. A null or failure result would be scientifically informative only if the measurement endpoint is stabilized first.

## CENTRAL HYPOTHESIS STATUS

**RNA structure versus sequencing measurement behavior has not been tested.**

## TESTS AND REPRODUCIBILITY

The previously completed lightweight suite passed 27 tests, and the Phase 3C governance validator passed. The new cohort manifest was generated from the existing compact fold manifest with duplicate and five-fold integrity checks. Large scientific caches, FASTQ, BAM and CRAM files were not staged.

## GIT AND PRIVATE REMOTE

The review began at `56bd8ae8f95f66beaf4cec13274a6be6d63dde02`, matching `origin/main`. Final review files and the cohort manifest will be committed and pushed as a new private-remote commit after validation.

## EXACT NEXT PHASE

Resolve whether a common-output or explicitly quantifier-defined endpoint can be defended independently of any structure result. Reconstruct and assess sequence-similarity groups from pinned references, then freeze the cohort, endpoint, folds and analysis plan only if G3 and G9 pass. Fit structure-blind Models A/B/C only after that freeze. Stop before the first structure hypothesis test.
