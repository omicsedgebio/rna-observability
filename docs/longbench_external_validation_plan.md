# LongBench external-validation lock candidate

Status: **LOCK CANDIDATE — NOT AUTHORIZED**

Date: 2026-09-25

Development freeze: `294f59ddab5dc4262d23ebbd976f2cec6469bc71`

This document is a post-development, outcomes-blind plan. It does not amend or
replace `docs/frozen_analysis_plan.md`, the Model D scientific lock, or the
frozen `NOT_SUPPORTED / NEGLIGIBLE` Model D conclusion. It authorizes no
LongBench access, bucket listing, acquisition, value inspection, prediction, or
scoring.

## Decision

LongBench is conditionally appropriate for two scientifically separate aims:

1. transport of the fixed `workflow_detection_v1` measurement phenotype; and
2. transport of one structure-blind Model C classifier after its deployable
   full-development estimator and scaler are serialized, hashed, reviewed, and
   committed before any LongBench access.

LongBench is excluded from validation of the incremental structure hypothesis
and from structure-feature reproducibility. No verified cell-matched
experimental structure assay is present in permitted metadata. No LongBench
finding can revise, rescue, qualify, rerun, or motivate post-hoc expansion of
Model D.

The program is scientifically justified but not release-ready. The unresolved
compatibility facts are methods/sample-metadata questions; they do not require
and must not be answered by viewing expression values or performance results.
They are release blockers rather than reasons to weaken the endpoint.

## Exact objective and scope

The primary objective is to estimate, without validation refitting, how one
fixed structure-blind transcript classifier trained in K562 transports to
eligible independent human lung-cancer cell lines when labels are constructed
with the unchanged `workflow_detection_v1` rules. The secondary objective is to
report the five-class phenotype by cell line using those same rules.

The target observations are frozen development-cohort transcripts within each
eligible human lung-cancer cell line. Eligibility requires matched bulk
Illumina and bulk ONT direct-RNA biological preparations. Single-cell,
single-nucleus, ONT PCR-cDNA, and PacBio Kinnex data are outside the primary
objective. At least four cell lines must independently satisfy every condition.
The primary analysis does not pool cell lines.

This is transport across a large biological-context shift from K562 to lung
cancer cell lines. The result therefore concerns workflow-specific measurement
behavior in the eligible contexts, not biological truth, platform accuracy,
clinical utility, causation, or a generally validated score.

## Transcript and reference lock

The transcript universe is exactly the frozen 15,999-transcript development
cohort in its frozen order. The biological unit is the pinned Ensembl 91
transcript accession with version identity retained; the unversioned stable ID
is only the frozen join key. Validation expression values cannot select the
transcript universe.

Release requires either the exact pinned Ensembl 91 transcriptome used in
development or a pre-access mapping that proves unique equality of gene,
chromosome, strand, exon intervals, transcript length, and sequence. Missing,
duplicated, ambiguous, non-finite, or incomplete transcript rows are blockers.
Missing rows are not zeros, are not imputed, and cannot be removed after outcome
exposure.

Exact transport requires Salmon 1.9 with the frozen development settings and
reference. Processed outputs are usable only if methods and file metadata prove
the exact transcript index, quantifier, settings, and complete-row behavior
before values are opened. Otherwise a fixed raw-data re-quantification route
must be reviewed. Before any transfer over approximately 5 GB, the purpose,
size, processed alternatives, and necessity must be reported and authorized.

## Biological preparations and phenotype

Biological preparations, not technical runs or lanes, supply replicate support.
Technical runs must remain nested under their biological preparation. For each
included cell line, an outcomes-blind manifest must freeze exact accessions and
roles for:

- two bulk Illumina outcome preparations;
- four bulk ONT direct-RNA outcome preparations; and
- one additional, non-overlapping bulk Illumina preparation for the independent
  abundance covariate.

If more eligible preparations exist, the deterministic selection rule and exact
sample list must be approved before any expression value is opened. Outcome
values cannot choose samples.

For each transcript, Illumina support means TPM at least 1 in both of two
Illumina outcome preparations. Direct-RNA support means TPM at least 1 in at
least three of four direct-RNA preparations. Illumina support of one or
direct-RNA support of one or two gives `INDETERMINATE`. Otherwise the fixed
class is `BOTH`, `ILLUMINA_ONLY`, `DIRECT_RNA_ONLY`, or `NEITHER`. The class
order is:

1. `BOTH`
2. `ILLUMINA_ONLY`
3. `DIRECT_RNA_ONLY`
4. `NEITHER`
5. `INDETERMINATE`

If the required preparations do not exist, exact phenotype transport fails. A
modified support rule is a different endpoint and requires a new outcomes-blind
lock; it cannot be substituted under this candidate.

## Model policy

The selected design is pure frozen-model transport after pre-access
materialization. Validation refitting, recalibration, feature selection,
imputation, threshold tuning, and model selection are prohibited.

The repository contains the frozen 15,999-row development matrix at
`results/tables/model_c_inputs.tsv.gz` (SHA256
`c7597fcf57d955a84dcd512d4e4689be6127a408b76aed992d176af8e3a41a31`)
and out-of-fold predictions. The out-of-fold predictions are not an external
estimator. A separate full-development deployment artifact has now been fit once
from that frozen matrix and saved transparently in
`metadata/model_c_deployment_estimator.json`. It is labeled
`POST-DEVELOPMENT DEPLOYMENT ESTIMATOR`, not a reconstruction of historical OOF
predictions and not new development evidence. Before LongBench access it must
also remain fixed at deployment commit
`936ba5b33cc22b0eeae18bbfb7d93e63bce6358a`.

The deployment fit used:

- the nine features in their frozen order;
- `StandardScaler` fit only on the 15,999 development rows;
- `LogisticRegression(C=1.0, solver="lbfgs", tol=0.0001,
  max_iter=2000, class_weight=None, fit_intercept=True,
  random_state=20260923)`;
- one thread and the locked Python/package environment; and
- the fixed five-class order above.

This is a deployable transport artifact specified after the negative Model D
result, not a new Model D attempt and not a re-estimation on validation data. It
cannot retroactively alter any development result. Its state and receipt hashes
are pinned in the candidate configuration and its deployment commit is fixed.
Until all remaining release conditions pass, model transport is prohibited.

Validation features are deterministic pinned-reference sequence/annotation
features plus `log1p(TPM)` from the separately reserved Illumina abundance
preparation. The outcome Illumina preparations cannot supply that covariate.
The development-fitted scaler is applied unchanged. No cross-cell-line batch
correction or validation-estimated preprocessing is allowed.

## Metrics and uncertainty

The primary metric is the unweighted mean of cell-line-specific five-class
macro-F1, with the fixed class order and `zero_division=0`. The primary 95%
interval is a 10,000-replicate percentile bootstrap that resamples eligible
cell lines with replacement using seed `20260925`. A pooled
transcript-by-cell-line metric is secondary and descriptive only.

Secondary reporting includes cell-line-specific macro-F1, multiclass log loss,
multiclass Brier score, per-class precision/recall/F1/support, fixed-order
confusion matrices, and phenotype prevalence. Calibration is reported for every
class in ten fixed equal-width probability bins with bin count, mean predicted
probability, and observed proportion. Predictions are never recalibrated.

There is no binary performance threshold and no post-hoc declaration that the
model is “validated.” The estimate and interval are reported regardless of
direction. Development comparisons are descriptive; there is no improvised
non-inferiority margin and no path from external performance back to Model D.

## Prediction before scoring

The workflow has two separately authorized exposure stages:

1. Freeze and commit the sample inclusion manifest, transcript mapping,
   implementation, environment, and full-development estimator.
2. Obtain explicit human authorization for feature-only access.
3. Materialize pinned reference features and only the reserved independent
   abundance covariate.
4. Generate predictions and probabilities, save them, and hash the prediction,
   inclusion, feature, code, model, and environment receipts.
5. Obtain a separate human scoring authorization tied to those hashes.
6. Only then open the outcome-library expression values, construct labels, and
   score once.

If LongBench packaging exposes outcome-library values while the abundance
feature is built, sample-separated extraction by a trusted custodian is
required. If that separation cannot be demonstrated, the analysis is blocked.
The planning code accepts no arbitrary LongBench path and contains no network,
download, listing, or data-reader implementation.

## Prespecified failures

Analysis stops without scoring if any eligibility, replicate, identity,
quantifier, completeness, separation, hash, authorization, or prediction-receipt
condition fails. It also stops if fewer than four cell lines qualify, if the
full-development estimator is absent, or if any label/outcome information
influences inclusion, preprocessing, missingness handling, or model choice.

Failure of exact compatibility does not permit a modified endpoint. A modified
phenotype would require a new lock written without outcome exposure. No failure
or success can trigger a Model D rerun or redesign.

## Current compatibility judgment

Catalog-level evidence supports independent-study, human-context, technology
presence, and licensing conditions. Exact bulk modality pairing, biological
replicate roles, a separate abundance preparation, annotation, transcript
outputs, quantifier compatibility, acquisition burden, and operational
feature/label separation remain unresolved. Matched experimental structure is
absent and is a permanent blocker for structure validation under this plan.

These findings are recorded in
`metadata/longbench_compatibility_audit.tsv`. They were not resolved by opening
LongBench, listing its bucket, querying outcome information, or viewing values,
figures, tutorials, performance summaries, or the full paper.

## Release conditions

No access is authorized until all machine-checkable conditions in
`configs/longbench_external_validation_lock.json` are true, all required audit
items are resolved using outcomes-blind methods/sample metadata, exact study and
sample inclusion is committed, the annotation mapping and validation
implementation are frozen, the deployable estimator and preprocessing state
are serialized and hashed, acquisition burden is reviewed, and human review is
complete.

Feature access requires a future
`metadata/longbench_data_access_authorization.json`. Outcome-label access and
scoring additionally require a future
`metadata/longbench_scoring_authorization.json` tied to a frozen prediction
hash. Neither artifact exists or is authorized by this candidate.

## Exposure statement

During preparation of this candidate: no LongBench file, bucket listing,
transcript-level value, outcome, result, figure, tutorial output, performance
summary, or full-paper result extraction was accessed; no Model D fit or rerun
was performed; and no validation prediction or metric was computed.
