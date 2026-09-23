# Frozen analysis plan - Phase 3D workflow-specific baselines

Current adjudication: **BLOCK_STRUCTURE_TEST**. This file is a historical baseline specification, not an approved pre-structure analysis lock. See [decision chronology](prestructure_decision_chronology.md). No new lock timestamp or prospective-registration claim is created. The recorded status below is retained for historical traceability.

Status: FROZEN_PHASE3D
Integrity qualification: this is the recorded status, not a certified prospective pre-baseline freeze. Baseline results were inspected before this document was written. See [closeout integrity audit](phase3d_integrity_verification.md); do not interpret this status as permission for Model D or LongBench evaluation.
Freeze timestamp UTC: 2026-09-23T15:30:16Z
Freeze parent git SHA before design commit: 09d12633f4587aa60e8cd34e7e58b9657a437a9a
Design freeze and baseline commit: 5b98bfd
Endpoint version: `workflow_detection_v1`
Cohort SHA256: `3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5`
CV fold SHA256: `66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52`
External outcomes viewed: NO

**RNA structure versus sequencing measurement behavior has not been inspected.** This freeze precedes the final structure hypothesis test. LongBench remains locked and no LongBench outcome is used.

## Scientific scope

The estimand is measurement behavior under a defined sequencing and quantification workflow. It is not technology-intrinsic reliability, platform accuracy, endogenous true error, or a universal observability score. The development context is SG-NEx K562 bulk RNA with Ensembl GRCh38 transcript definitions and Salmon 1.9.0 outputs.

## Data and reference versions

- SG-NEx processed K562 quantification object, restricted to the documented Illumina and direct-RNA runs in `metadata/quantification_workflows.tsv`.
- Ensembl release 91 GRCh38 transcriptome, GTF, cDNA and ncRNA FASTA with recorded checksums.
- GSE132099 in-vivo icSHAPE is used only to define the future conditional structure-callability population; no reactivity value enters baseline outcomes, features or folds.
- GSE149767 is not an outcome or baseline predictor.
- LongBench is not downloaded or read beyond `docs/external_validation_lock.md`.

## Transcript universe and eligibility

The final universe contains 15,999 stable Ensembl transcript IDs. Eligibility is fixed and outcome-blind: class-A Ensembl 88 to 91 sequence and exon equivalence; valid Ensembl 91 annotation; complete rows in three Illumina Salmon and four direct-RNA Salmon SG-NEx runs; at least 50 callable GSE132099 positions and callable fraction at least 0.5 for the conditional future structure estimand. No structure magnitude, platform disagreement, or model performance was used. The full attrition is `results/tables/phase3d_cohort_attrition.tsv`.

## Replicate unit and quantification

A transcript is the prediction row. SG-NEx biological preparations are the inferential unit; run-level columns are aggregated into support states and are not pseudoreplicates. The primary workflow is Salmon 1.9.0 with Ensembl 91. Illumina uses the two outcome libraries `GIS_K562_Illumina_Rep4-Run1` and `GIS_k562_Illumina_Rep5-Run1`. Direct RNA uses four outcome libraries `SGNex_K562_directRNA_replicate1_run1`, `replicate4_run1`, `replicate5_run1`, and `replicate6_run1`. `GIS_K562_Illumina_Rep3-Run1` is an independent prior-run abundance covariate only.

## Primary phenotype

`workflow_detection_v1` is a five-state categorical endpoint:

1. Illumina supported detection: Salmon TPM >= 1 in both two outcome libraries.
2. Direct-RNA supported detection: Salmon TPM >= 1 in at least three of four outcome libraries.
3. `BOTH` if both supported, `ILLUMINA_ONLY` if only Illumina supported, `DIRECT_RNA_ONLY` if only direct RNA supported, and `NEITHER` if neither supported.
4. Any intermediate replicate support (one of two Illumina or one/two of four direct-RNA libraries) is `INDETERMINATE`.

Zeros are retained as fitted zeros and are not treated as biological absence. No pseudocount is used. This endpoint is workflow-specific and is not called measurement error or truth.

## Secondary and exploratory phenotypes

Secondary: within-common-positive percentile-rank difference using the same named Salmon workflows; within-workflow replicate reproducibility; quantifier sensitivity using Illumina RSEM and direct-RNA Bambu/NanoCount as descriptive alternatives; synthetic spike-in calibration separated from endogenous inference. Exploratory: transcript completeness or transcript-end measures only if a future processed alignment resource supplies validated evidence; isoform ambiguity and architecture remain separate annotation-derived phenotypes. No composite score is defined.

## Baseline predictors

Model A uses independent prior-run `log1p` Illumina Salmon TPM, transcript length and GC fraction. Model B adds exon count, isoforms per gene and sequence-cluster size as architecture and identifiability controls. Model C adds prespecified sequence features: homopolymer fraction, 32-nt low-complexity fraction, and whole-transcript Shannon entropy. Features are computed from Ensembl 91 sequence and annotation only, with training-fold standardization. No endpoint-derived predictor is permitted. Exact definitions remain in `metadata/feature_definitions.tsv`.

Annotation-only identifiability controls remain mandatory. The 95% identity / 90% coverage sequence cluster is a leakage group, not a biological feature selected from results. The miniQuant K-value and unique k-mer fraction remain sensitivity resources but are not required for the frozen minimal Model C because their complete cohort rows were not available in the current checkout.

## Reserved future structure features

Callable fraction is an assay quality covariate. Mean or median reactivity and high- or low-reactivity fractions are conditional future candidates, each requiring a prespecified structure-quality analysis and reproducibility report. Local variability, transcript-end structure and splice-junction structure are unsupported in the present evidence. No structure feature enters Models A, B or C.

## Structure estimand and missingness

Future structure inference is conditional on the 15,999 measured, mapped and structure-callable transcripts described above. It does not target all human transcripts. Positivity is poor outside the measured high-callability population, so complete-case conditional inference is primary. Stratified reporting by abundance, length and isoform complexity is required. Matching may be used only as a sensitivity analysis. Inverse-probability weighting is prohibited unless positivity and weight stability are demonstrated independently before analysis.

## Cross-validation and leakage control

Five folds are fixed in `metadata/cv_folds.tsv` with NumPy seed `20260923`. Same-gene transcripts and all transcripts in the same connected Ensembl 91 sequence cluster are assigned together. Clusters use BLASTN 2.15.0 megablast, >=95% identity and >=90% coverage of the shorter sequence; a 99% threshold is a sensitivity diagnostic. No gene or primary sequence cluster occurs in more than one fold. Technical runs are columns, not rows. These exact folds must be reused for all structure-blind and future structure models.

## Models, tuning and metrics

Models A, B and C are multinomial regularized logistic models with fixed `C=1`, `lbfgs`, maximum 2,000 iterations, NumPy/sklearn seed `20260923`, and training-fold centering/scaling. No post-freeze feature selection or endpoint redesign is allowed. Metrics are held-out accuracy, balanced accuracy, macro-F1, multiclass log loss, multiclass Brier score, and calibration summaries where class probabilities are estimable. The majority-class classifier is the trivial comparator. Performance is reported overall and by prespecified abundance, length and isoform strata. Quantifier sensitivity uses the fixed alternative labels and does not redefine the primary outcome.

Uncertainty uses a sequence-cluster bootstrap of out-of-fold predictions with 100 fixed-seed replicates for primary metric intervals. Fold-level and class-level counts are reported. Replicate variation is reported descriptively because SG-NEx has limited independent biological preparations. No transcript-level t-test treats technical runs as independent.

## Future structure hypothesis tests

Model D is reserved. Only after review of the frozen structure-blind results may a future phase add prespecified structure summaries to Model C on the identical cohort and folds. That phase must use held-out incremental performance, cluster uncertainty, null permutations at the sequence-cluster unit, and multiplicity control defined before reading the structure-outcome result. This plan does not authorize Model D or any structure association.

## Sensitivity analyses

Prespecified sensitivities are: 0.1 and 5 TPM detection thresholds; alternative replicate support rules; RSEM and Bambu/NanoCount descriptive labels; 99% sequence-cluster threshold; abundance, length and isoform strata; exclusion of indeterminate rows; and secondary rank phenotype. None may replace the primary endpoint after outcome inspection. Spike-ins calibrate synthetic mixture behavior only and cannot be treated as endogenous truth.

## Success, partial success and failure

Success requires a stable workflow-specific phenotype, leakage-safe held-out baseline estimates with useful calibration, and a future Model D comparison that improves held-out performance beyond Model C with cluster-level uncertainty and null control. Partial success is a reproducible workflow-specific baseline and a precisely bounded null or conditional structure increment. Failure is unresolved quantifier dependence, unstable endpoint labels, leakage, severe loss of positivity, or no reproducible incremental structure information at the conditional estimand.
