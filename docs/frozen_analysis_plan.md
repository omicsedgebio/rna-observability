# Analysis plan

Status: DRAFT_NOT_FROZEN
Created: 2026-09-22
Phase 3A review: 2026-09-23
Freeze timestamp: NOT_APPLICABLE
Freeze commit: NOT_APPLICABLE
External outcomes viewed: NO
Central structure versus measurement association examined: NO

This file is an explicit pre-freeze draft. Its initial local commit does NOT unlock LongBench. Do not mark FROZEN while any required choice is unresolved. Phase 3A did not freeze or run Models A/B/C because no mapping class A/B transcript exists and other endpoint/missingness blockers remain.

## Proposed analysis and fields to freeze

| Required field | Current proposal | Unresolved before freeze |
|---|---|---|
| Primary outcome | Signed ONT directRNA minus Illumina median log2 relative abundance, +0.1 offset | Comparable abundance units and independent preparations |
| Secondary outcomes | Absolute disagreement, replicate variance, detection, isoform fractions, spike-in error | Exact family and multiplicity |
| Inclusion | Fixed annotation, independent expression eligibility, adequate independent libraries | Numeric coverage and expression rules after outcomes-blind QC |
| Exclusion | Ambiguous coordinate map, invalid sequences, incompatible treatment, missing essential covariates | Exact audited sample IDs and reasons |
| Transcript universe | Ensembl 91-compatible mature transcripts | Hash of FASTA/GTF and exact map/list |
| Feature set | A abundance/length/GC; B architecture/identifiability; C sequence; D measured structure | Exact columns and structure summaries |
| Preprocessing | Training-only centering/scaling; nonlinear terms prespecified; no external fitting | Transform definitions |
| Missing data | Structure missingness audited; common C/D cohort; other imputation fitted only on training | Callable threshold, imputation method, missing indicators |
| Primary statistical model | Interpretable regularized linear model with prespecified smooth abundance/length/GC terms; protocol-specific fit | Penalty/spline degrees and model formula |
| Predictive baselines | Mean-only; A/B/C; annotation K-value; measured-coverage-only increment; predicted-structure comparator | Implementations and computational scope |
| Hyperparameters | Inner grouped CV for fixed small grid; identical budget for C/D | Exact grid |
| CV procedure | Nested 5 outer / 4 inner folds grouped by gene AND cross-gene sequence similarity components | Feasible group counts, similarity threshold, seeds, repetitions |
| Performance | Primary paired held-out MAE reduction; RMSE/R2/rank and calibration slope/intercept secondary | Cluster weighting and uncertainty prescription |
| Null/permutation tests | Matched-bin whole-profile permutations with fixed masks; outcome permutation; random features | Matching bins, exchangeability justification, number of null fits |
| Primary comparison | D vs C on identical rows/folds, conditional on coverage | Exact paired loss estimand and primary contrast |
| Success criteria | Positive practically meaningful delta with cluster CI excluding zero, control robustness, independent context replication | Minimum meaningful delta and precision/power target fixed before outcome analysis |
| Failure criteria | No stable phenotype; no meaningful D>C; gain explained by missingness/sequence; failure to transport | Quantitative equivalence and transport margins |
| External test | Frozen pipeline, no retraining; one compatible LongBench bulk contrast | Transcript outputs/annotation/replication and matched-structure availability |
| Model/prediction artifacts | Hash all code/config/environment/model files; save predictions before scoring | Exact storage paths and freeze commit |
| Reporting | All prespecified tests including nulls; post-hoc separately labeled | Final table/figure manifest |

## Statistical safeguards to preserve at freeze

- Define per-gene contribution to loss (equal gene weights proposed) so many isoforms do not dominate. Cluster bootstrap paired C/D errors by gene/similarity group; do not t-test correlated fold means.
- Transcript resampling is not a substitute for biological-preparation uncertainty. Resample preparations separately; report limited library degrees of freedom.
- Pooling all cells of a transcript across train/test is prohibited for unseen-transcript claims. For cross-study same-transcript transfer, label it explicitly and report separately.
- Separate expression covariate libraries from endpoint libraries. Freeze cross-fitting only if replication supports it.
- Choose every inclusion/coverage threshold without LongBench outcomes and without maximizing a structural association. Nested CV does not repair whole-dataset feature selection.
- A secondary GAM/mixed model can assess adjusted effects with simultaneous controls and clustered uncertainty. Avoid claiming causation from coefficients.
- Calibration for continuous y: out-of-fold calibration intercept/slope and residual scale; probability calibration only for binary detection outcomes.
- Primary delta = MAE_C - MAE_D; positive favors D. Report absolute/relative delta, uncertainty, distribution across contexts/protocols, and permutation tail area (1 + exceedances)/(1 + permutations).
- No “success” based solely on P<0.05, a feature importance rank, or a single favorable protocol.

## Negative-control design

| Control | Preserved / disrupted | Leakage or validity risk |
|---|---|---|
| Whole-profile permutation within expression/length/GC/coverage/ambiguity bins | Retains broad nuisance structure, disrupts transcript link | Conditional exchangeability approximate; bins built in training only |
| Transcript-label permutation in grouped folds | Tests full pipeline against no target association | Must permute gene/similarity units, not split sibling rows |
| Circular profile shifts within transcript | Retains value distribution, changes local positioning | Invalid for global mean tests; handle mask and boundary effects |
| Context-mismatched structure | Tests cell-context specificity | Same RNA sequence remains; not a pure null; no external outcomes used |
| Predicted structure vs experimental | Tests whether experiment adds beyond computable sequence summary | Prediction not equivalent to in-vivo truth |
| Random features with matched dimension | Tests overfitting from added capacity | Draw only with fixed training seeds |
| Coverage-only added features | Tests missingness/measurement availability explanation | Required comparator, not biological structure |

A stable null is publishable only within its identifiable scope and precision. An external failure remains failure even if an exploratory refit subsequently works.

## Phase 3A freeze gate failure

No plan is frozen. The 200,310 SG-NEx/Ensembl 91 transcripts map to zero validated A/B icSHAPE transcript definitions, so an exact primary transcript inclusion list cannot be written. The proposed 0.5 callable fraction and 50 callable-base threshold produces 35,309 **provisional** ID/length/availability matches, but 47.37% of the 198,569-transcript adjusted universe has fitted availability below 0.05 and naive inverse-probability weights have effective sample size about 193. The abundance representation is identified as Salmon TPM after common-universe closure, yet the median signed contrast moves from -6.90 to -1.40 log2 units between fixed 0.01 and 1 TPM offsets. Only one Illumina library remains for independent abundance conditioning when two outcome libraries are reserved. A cross-gene similarity graph beyond exact duplicates and exact outer fold assignments are also pending. These are scientific stop conditions, not optional analysis choices.

Before a real freeze, resolve the icSHAPE source transcript FASTA/GTF or reconstruct a documented equivalent transcript model, set an explicit high-overlap conditional estimand and missing-data rule, decide whether a hurdle/detection endpoint replaces the unstable continuous primary, obtain an independent abundance covariate strategy, build the complete gene/sequence-similarity group graph and lock fold assignments. Then finalize exact model classes, inner penalty grids, null/permutation units, number of permutations, multiplicity family, numerical success/partial-success/failure margins and uncertainty procedure with a freeze timestamp and commit SHA **before** A/B/C fitting or any reactivity association. RNA structure versus transcript measurement behavior has not yet been tested.
