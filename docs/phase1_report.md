# Phase 1 report --- 2026-09-22

## Novelty verdict

**MODIFY.** The broad structure/bias and transcript-difficulty ideas are prior art. No inspected work establishes the full proposed combination, but this reconnaissance does not prove novelty. Restrict the question to independent experimental structure's incremental information beyond strong identifiability/sequence controls. See [gate](novelty_gate.md) and [21-work matrix](prior_art_matrix.tsv).

## Closest prior art

| Study/tool | Solves / overlaps | Remaining distinction to test |
|---|---|---|
| [miniQuant, 2025](https://doi.org/10.1038/s41587-025-02633-9) | Quantification difficulty from isoform ambiguity; hybrid read integration and design | Experimental in-vivo structure increment after its controls |
| [Price et al., 2017](https://doi.org/10.1371/journal.pone.0173023) | Experimental PARS and Illumina read-start/GC bias | Human isoforms, in-vivo probing, cross-protocol and independent predictive test |
| [Su et al., 2025](https://doi.org/10.1101/gr.280713.125) | Local structure-related sequencing efficiency using learned representations | Measured in-vivo reactivity and identifiability-adjusted increment |
| [Brooks et al., 2025/2026](https://doi.org/10.1101/2025.01.30.634337) | Protocol/coverage mechanisms; predicted-structure increment reported negative in preprint | Experimental structure, broader protocol phenotype; reconcile final journal text |
| [SG-NEx, 2025](https://doi.org/10.1038/s41592-025-02623-4) | Cross-protocol transcript benchmark | Predicting stable behavior with independent structure and external freeze |
| [alpine, 2016](https://doi.org/10.1038/nbt.3682) | Fragment GC/sequence bias correction | Residual measured structure and transportability |
| [Salmon, 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5600148/) | Bias-aware transcript quantification | A distinct prediction target; quantifier robustness required |
| [subgraphquant, 2022](https://doi.org/10.1089/cmb.2021.0444) | Nonidentifiability ranges under annotation uncertainty | Structure cannot substitute for assignment uncertainty |
| [PrismNet, 2021](https://doi.org/10.1038/s41422-021-00476-y) | Sequence plus measured structure predicts RBP binding | Measurement-behavior target differs from RBP binding |
| [Boivin et al., 2020](https://doi.org/10.1093/nar/gkaa028) | Structure-sensitive RT and missed ncRNA detection | Adjusted transcript-isoform prediction across platforms |

## Defensible candidate contribution

A reproducible observational test of whether independent, experimentally measured in-vivo RNA accessibility improves prediction of a stable transcript-level protocol-pair abundance-disagreement phenotype beyond independently measured abundance, sequence composition, transcript architecture and rigorous annotation/read-identifiability controls, with gene/similarity-group held-out evaluation, matched missingness controls, and independent study validation where both outcome and feature compatibility are demonstrable. This is a candidate contribution, not an established result, causal claim or universal RNA property.

## Publication potential

A paper requires meaningful reproducible D>C improvement with uncertainty, credible phenotype repeatability, strong controls and independent validation; alternatively, a precise well-controlled null could resolve a specific existing expectation. Small unstable improvements, selected high-coverage cohorts without sensitivity, quantifier-specific effects or same-gene-only transfer weaken the paper. Adequate-precision nulls across compatible independent contexts kill the central incremental-structure hypothesis within that scope. Failure to establish a phenotype or valid structure mapping blocks its test rather than biologically falsifying it.

## Data feasibility

SG-NEx processed transcript RDS: 669,521,420 bytes; sample/annotation RDS: 27,131,354; optional spike-in RDS: 65,329,913. These sizes are from actual S3 metadata, not estimates of raw data. K562 processed icSHAPE is listed as 87.3 MB; full processed series 424.4 MB. Candidate minimal set including spike-ins and K562 structure is approximately 0.85 GB compressed. None downloaded. Exact RDS schema, units, memory use and reference compatibility remain untested. [Detailed audit](sgnex_feasibility.md).

SG-NEx data license is CC BY-NC 4.0; GEO dataset-specific terms are unresolved. LongBench catalog is CC BY-4.0 and lists eight lung-cancer cell lines and relevant technologies, but transcript-matrix availability, annotation compatibility, matched structure and byte size are unverified. Do not promise a small external download or a matched-structure validation.

## K562 feasibility

Scientifically defensible only as a conditional cross-study feasibility investigation. Genome-family overlap exists; exact transcript mapping, cell source/culture/extraction comparability and biological sample pairing are not established. Primary PrismNet paper confirms two biological replicates and a >100 read-depth score filter; availability of separate score files remains unresolved. SG-NEx lists 14 ONT runs, three Illumina runs, and one PacBio K562 sample; runs are not independent biological replicates. [Audit and stop conditions](k562_feasibility.md).

## Primary outcome candidate

For fixed transcript universe U, harmonized molar abundance a on a per-million scale, protocol p=ONT direct RNA and q=Illumina:

`y_t = median_r log2(a_tpr + 0.1) - median_s log2(a_tqs + 0.1)`.

Aggregate technical runs first; r/s represent independent RNA preparations. This is signed disagreement, not error. Inclusion uses independent abundance evidence; retain outcome zeros. Exact sample cohort/coverage thresholds remain to freeze. [Definitions and secondary endpoints](outcome_definition.md).

## Baseline comparators and structure test

Mean-only and A (abundance, length, GC); B adds exon/isoform architecture, unique sequence/read geometry, miniQuant-compatible K-value and rank deficiency; C adds sequence composition/repeats; D adds experimental reactivity. Compare D and C on identical transcripts/folds, with structure coverage covariates in both. Quantifier sensitivity should include bias-aware short-read estimation and established long-read methods when processed outputs permit; this project is not trying to replace those quantifiers.

Use grouped nested validation, training-only preprocessing, paired held-out MAE difference, effect estimates and clustered uncertainty. Add predicted-structure, coverage-only, matched profile permutations and local-shift controls where appropriate. Abundance/replicate-variance covariates must be independent of their endpoint. [Feature registry](feature_registry.md) and [draft plan](frozen_analysis_plan.md).

## Validation firewall

LongBench outcomes remain untouched. Only GEO/AWS catalog metadata were viewed; no files downloaded, no metrics or transcript values examined, no threshold selection or model fitting. The analysis plan is explicitly DRAFT_NOT_FROZEN. Model C transport alone cannot validate incremental structure. [Exposure log](external_validation_lock.md).

## Major risks

Prior-art overlap; cross-study biology; extracted versus in-vivo RNA folding; structure-assay missingness; uncertain transcript coordinate mapping; low biological replication; composition/depth/pseudocount effects; gene/sequence leakage; quantifier and chemistry dependence; unavailable external matched structure; licensing and legacy processed-object provenance. See [limitations](limitations.md).

## Files created

Root README, AGENTS, pending license/citation and ignore policy; all requested directories; 21-work prior-art matrix; six-row dataset registry; 22-entry search log; scientific question/hypotheses/claims/outcomes/features; K562 and SG-NEx feasibility; external lock and draft freeze plan; manuscript plan; assumptions/limitations/decisions/reproduction; phase policy JSON; offline validator and governance tests; lightweight GitHub Actions workflow; this report and command log. Empty manuscript/results directories contain placeholders only.

## Commands and checks

See [command log](command_log.md). Check results: validator PASS, six governance tests PASS under installed Python 3.12.14; ignore-policy probes PASS. Default Python 3.9 failed on an existing syntax error in its own tempfile module; no system file was changed. No Linux/GitHub Actions execution is claimed. The validator verifies structure and governance consistency, not scientific findings. Whitespace checks passed before staging; the final staged check is part of the commit procedure.

## Git status / commit

Initial main had no commits; existing origin retained. This report is prepared for the initial local scaffold commit. The final handoff records the actual local commit hash and clean/dirty status; `git log -1 --oneline` retrieves it. No push or remote write is authorized or performed. Remote visibility was not independently verified or changed.

## Next recommended phase

Review this MODIFY decision. If explicitly approved, perform a bounded processed-data feasibility/QC phase: resolve rights and supplemental provenance; inspect RDS/structure schemas; validate transcript mapping and sample independence; quantify missingness without association hunting; resolve an external matched-structure route. Complete the analysis plan before modeling and commit the actual freeze before external evaluation. Stop here until review and explicit approval.
