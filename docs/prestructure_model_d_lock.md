# Project 001 RNA Observability: prestructure Model D lock candidate

Status: **CANDIDATE_FOR_HUMAN_REVIEW; BLOCK_STRUCTURE_TEST remains in force.**

Classification: **PRESTRUCTURE_BASELINE_REESTABLISHMENT** — specifically, **PRE-STRUCTURE BASELINE RE-ESTABLISHMENT AFTER PRIOR BASELINE INSPECTION**. This is a pre-structure analysis lock candidate established after inspection of structure-blind baseline performance. It is not a prospective preregistration, original-prediction recovery, or exact historical reconstruction.

Parent commit: `d077a7bc9c7cd0bf1209a72265ea84e800e570c0`.

No RNA-structure value was read in preparing this candidate. No structure feature was computed, no structure-outcome test was run, no Model D was fit, and no LongBench input was read. This candidate does not authorize any of those actions. Structure access remains prohibited after the scientific lock is reviewed, approved, committed, and pushed: a separate `PRESTRUCTURE_IMPLEMENTATION_LOCK` must then be created while structure remains blinded, committed, pushed, reviewed, and explicitly approved by a human before structure access may be authorized.

## Scientific question and estimand

The single central question is whether the pooled, independently measured GSE132099 K562 in-vivo icSHAPE median enrichment score provides incremental held-out information about the five-state `workflow_detection_v1` phenotype beyond independent abundance, transcript sequence composition, transcript architecture, annotation/read-model identifiability controls, and icSHAPE assay callability.

The target population is exactly the frozen 15,999-transcript cohort. It is conditional on exact Ensembl 88-to-91 transcript identity, SG-NEx row availability, and the already fixed structure-callability rule. It does not target all human transcripts, all K562 transcripts, matched aliquots, other cell types, biological truth, or technology-intrinsic error. SG-NEx sequencing and GSE132099 structure measurements come from different studies and preparations.

## Evidence reviewed

The following files were read for this specification. No structure-value file or LongBench outcome file was opened.

- `docs/model_c_execution_verification.md`
- `docs/model_c_reestablishment_reviewer2.md`
- `docs/model_c_reconstruction_audit.md`
- `docs/prestructure_decision_chronology.md`
- `docs/phase3c_report.md`
- `docs/phase3c_reviewer2.md`
- `docs/phase3d_report.md`
- `docs/phase3d_integrity_verification.md`
- `docs/claims_register.md`
- `docs/identifiability_baseline.md`
- `docs/identifiability_implementation.md`
- `docs/structure_feature_specification.md`
- `docs/structure_estimand.md`
- `docs/structure_missingness.md`
- `docs/transcript_mapping_validation.md`
- `docs/ensembl88_to_91_bridge.md`
- `docs/gse132099_feasibility.md`
- `docs/phase3b_report.md`
- `docs/frozen_analysis_plan.md`
- `docs/external_validation_lock.md`
- `docs/phase3d_reviewer2.md`
- `configs/model_c_outcome.json`
- `configs/model_c_reestablishment.json`
- `metadata/feature_definitions.tsv`
- `metadata/model_c_reestablishment_manifest.json`
- `metadata/model_c_saved_artifact_verification.json`
- `results/tables/model_c_reestablishment_metrics.json`
- `analysis/baseline_models/fit_structure_blind.py`
- `scripts/model_c_reestablish.py`
- `scripts/model_c_artifact.py`
- `scripts/phase3a_feature_audit.py`
- `scripts/run_miniquant_kvalue.py`
- `scripts/phase3b_acquire.py`
- `scripts/phase3b_structure_inventory.py`
- `src/rnaobs/core.py`

Path/name searches were also used to locate relevant non-structure source and metadata definitions. Those searches did not open scientific structure values or LongBench inputs.

## Established record versus choices fixed here

Already established and unchanged are the phenotype, 15,999 transcript IDs and their order, five folds, sequence groups, class order, historical Model C implementation, historical Model C saved OOF predictions, sample weight of one, macro-F1 as the historical primary metric, and the workflow-specific/cross-study claim limits. The authoritative hashes are recorded in the companion JSON and manifest.

This candidate newly fixes the enhanced annotation comparator, the role of callable fraction, the one-dimensional biological structure vector, structure parsing and failure rules, paired uncertainty, negative-control calibration, one sensitivity, multiplicity, practical magnitude thresholds, four-way conclusion rule, deviation policy, stop rule, and the mandatory implementation-lock gate. None of these choices may be changed after structure access without a declared protocol deviation.

## Locked model hierarchy

The hierarchy is deliberately small.

1. **C_HISTORICAL** is the existing re-established Model C, unchanged. Its saved OOF artifact is a secondary historical benchmark and is never refit or relabeled.
2. **C_ANNOTATION** uses the same outcome, cohort, folds, estimator, and nine Model C inputs, then adds the exact pre-outcome identifiability controls below. This comparator is mandatory because historical Model C did not adequately represent the repository's registered annotation-only controls.
3. **C_QUALITY** adds only `callable_fraction` to C_ANNOTATION. Callable fraction is an icSHAPE assay-quality/coverage variable, not biological RNA structure.
4. **D_STRUCTURE** adds only `median_reactivity` to C_QUALITY. This is the primary Model D.

No alternative enhanced annotation model, quality model, biological feature combination, interaction, spline, feature selection, or stepwise comparison is permitted.

### Exact feature order

`C_HISTORICAL`:

1. `independent_abundance_log1p`
2. `sequence_length`
3. `gc_fraction`
4. `exon_count`
5. `isoforms_per_gene`
6. `sequence_cluster_size`
7. `homopolymer_fraction`
8. `low_complexity_fraction`
9. `sequence_entropy`

`C_ANNOTATION` uses the preceding nine in that order, followed by:

10. `unique_kmer_fraction`
11. `unique_kmer_fraction_missing`
12. `unique_exonic_bases`
13. `shared_exon_fraction`
14. `unique_junction_count`
15. `max_exon_jaccard`
16. `identical_splice_chain_isoforms`
17. `incidence_rank_deficiency`
18. `mean_exon_length`
19. `miniquant_kvalue`
20. `miniquant_kvalue_missing`

`C_QUALITY` appends:

21. `callable_fraction`

`D_STRUCTURE` appends:

22. `median_reactivity`

### Added annotation and identifiability controls

All controls were defined before any structure-outcome comparison. Their inclusion is rationale-driven and not selected by Model C or future Model D performance.

The prior full joined file `results/tables/identifiability_sequence_features.tsv` is not present in this checkout. The definitions, pinned sources, implementations, and provenance records exist, so the values are reproducible without structure or outcomes. The companion JSON pins the Ensembl 91 GTF/cDNA/ncRNA and implementation hashes. Versioned transcript IDs are converted with the existing stable-ID rule that removes only the terminal numeric version while preserving `_PAR_Y`, and the join must be one-to-one. During the separately committed `PRESTRUCTURE_IMPLEMENTATION_LOCK` and before any structure file is opened, the enhanced annotation matrix must be regenerated, restricted to the frozen ordered cohort, verified for one row per transcript in exact frozen order, and hashed. It may retain raw missing values for `unique_kmer_fraction` and `miniquant_kvalue`; their locked fold-local imputation must not be performed globally during materialization. Failure to regenerate the matrix exactly is an `ANALYSIS_BLOCKER`; it does not permit dropping a control or using a reduced comparator.

| Variable | Source and exact definition | Rationale | Transformation, missingness, scaling | Available before unblinding |
|---|---|---|---|---|
| `unique_kmer_fraction` | Ensembl 91 validated transcript FASTA; `src/exact_kmers.cpp`; canonical ACGT-only distinct 31-mers unique to one transcript identity divided by all distinct valid canonical 31-mers | Exact transcript-specific sequence evidence | Raw fraction; non-finite/missing values receive the training-fold median and set the fixed indicator below; standardized using training-fold mean and population SD | Source, definition, and implementation available; cohort matrix must be regenerated and hashed before structure access |
| `unique_kmer_fraction_missing` | Derived from the raw field before imputation; 1 for missing/non-finite, otherwise 0 | Preserves information about inability to define exact 31-mer uniqueness without deleting transcripts | No imputation; standardized with all other columns; a constant column is retained | Yes |
| `unique_exonic_bases` | Ensembl 91 GTF; bases in exon-union segments belonging to no other same-gene transcript | Absolute isoform-specific exonic evidence | Raw count; missing/non-finite is an analysis blocker; training-fold standardization | Yes |
| `shared_exon_fraction` | Ensembl 91 GTF; `1 - unique_exonic_bases / transcript_length` | Fractional exon sharing complements the absolute unique-evidence count | Raw fraction; missing/non-finite is an analysis blocker; training-fold standardization | Yes |
| `unique_junction_count` | Ensembl 91 GTF; adjacent donor-acceptor coordinate pairs found in exactly one same-gene transcript | Splice-specific assignment opportunity | Raw count; missing/non-finite is an analysis blocker; training-fold standardization | Yes |
| `max_exon_jaccard` | Ensembl 91 GTF; maximum exonic-base intersection/union with another same-gene transcript | Closest annotated isoform similarity | Raw fraction; missing/non-finite is an analysis blocker; training-fold standardization | Yes |
| `identical_splice_chain_isoforms` | Ensembl 91 GTF; number of same-gene isoforms, including self, with the identical ordered intron chain | Ambiguity among transcripts with the same splice chain | Raw count; missing/non-finite is an analysis blocker; training-fold standardization | Yes |
| `incidence_rank_deficiency` | Ensembl 91 binary exon-segment plus junction incidence matrix; transcript columns minus numerical SVD rank using the existing implementation tolerance | Annotation-derived nonidentifiable transcript combinations | Raw count; missing/non-finite is an analysis blocker; training-fold standardization | Yes |
| `mean_exon_length` | Ensembl 91 GTF; transcript exonic length divided by exon count | Read-support geometry beyond total length and exon count | Raw value; missing/non-finite is an analysis blocker; training-fold standardization | Yes |
| `miniquant_kvalue` | Original miniQuant commit `c1b5a89f3c31c83b271a477475a1e289ee9806d7`; gene K-value; fragment length 235, effective-length entry, two threads, Ensembl 91 GTF | Published annotation/read-model conditioning control distinct from exact k-mers and exon incidence | Raw value; non-finite/missing receives the training-fold median and sets the indicator below; training-fold standardization | Source, definition, and implementation available; cohort matrix must be regenerated and hashed before structure access |
| `miniquant_kvalue_missing` | Derived from the raw K-value before imputation; 1 for missing/non-finite, otherwise 0 | Prevents K-value availability from being silently converted to an ordinary numeric value | No imputation; standardized with all other columns; a constant column is retained | Yes |

`genomic_span` is not added because intronic span is not a direct transcriptome-identifiability control after transcript construction. `repeat_content` is not added because the repository records it as unimplemented with no pinned repeat-mask source. `incidence_condition_number` is not added because singular matrices create non-finite values and rank deficiency already encodes that failure mode. No control is included merely because it might improve prediction.

## Mandatory PRESTRUCTURE_IMPLEMENTATION_LOCK

Committing and pushing this scientific lock does not authorize structure access. The next phase after scientific-lock approval is `PRESTRUCTURE_IMPLEMENTATION_LOCK`, not Model D execution. The exact authorization sequence is:

1. Human review of this scientific lock candidate.
2. Authorized commit and push of the approved scientific prestructure lock.
3. While all real structure values remain blinded, create and statically validate the exact execution implementation.
4. Materialize and hash the complete annotation-only comparator matrix.
5. Commit and push the implementation lock.
6. Only after separate human review and explicit approval of that committed implementation lock may structure access be authorized.

The implementation lock must satisfy every requirement below before **any** structure file is opened.

### Annotation-only matrix gate

Materialize the exact annotation-only matrix using only the frozen/pinned Ensembl 91 and miniQuant resources and implementations. It must contain exactly the frozen 15,999 transcripts, one row per transcript, in exact frozen transcript order, with all locked added annotation controls and no outcome-derived or structure-derived feature. No outcome-guided feature selection is permitted. Validate every deterministic definition and record the matrix file SHA256, all source/reference hashes, and all implementation hashes.

The materialized matrix may contain raw missing values for `unique_kmer_fraction` and `miniquant_kvalue`, the two variables whose imputation is fold-local. Do not globally impute them during matrix materialization. Their missingness indicators must reflect the raw fields, and the execution implementation must perform the locked training-fold-only median imputation.

### Exact execution implementation gate

While structure remains blinded, create the exact future execution code for C_ANNOTATION, C_QUALITY, and D_STRUCTURE. It must encode frozen feature ordering; fold-local imputation; scaling; estimator; seeds; one-thread fitting; OOF generation; paired bootstrap; negative-control permutations; stricter-callability sensitivity; deterministic decision rules; protocol-deviation handling; and the stop rule.

The implementation must fail closed on a changed cohort hash, changed fold hash, changed Model C artifacts, changed annotation-matrix hash, unexpected structure-resource hash, any LongBench access, or any attempt to rerun a consumed locked model attempt without adjudication.

### Blinded static-validation gate

Validate the implementation without reading real GSE132099 RNA-structure values. Permitted checks are syntax checks, config validation, unit tests, synthetic/mock structure arrays, synthetic missingness cases, deterministic decision-rule tests, bootstrap/permutation logic tests on synthetic data, hash-guard tests, and attempt-guard tests. Real structure values must remain unread, and no C_ANNOTATION, C_QUALITY, or D_STRUCTURE fit on the real cohort is permitted during this phase.

### Required implementation-lock record

The implementation-lock commit must contain or hash, at minimum: the final scientific lock config; the materialized annotation matrix or a deterministic artifact/receipt allowed by repository policy; the annotation-matrix SHA256; exact execution script or scripts and their SHA256 values; implementation unit tests; an implementation-validation receipt; environment/version requirements; and the model-attempt guard policy.

### Authorization states

The current scientific candidate has `structure_test_authorized = false`. After the scientific-lock commit alone, `structure_test_authorized = false` and `implementation_lock_required = true`. Only after the `PRESTRUCTURE_IMPLEMENTATION_LOCK` is separately committed, pushed, reviewed, and explicitly approved by a human may `structure_test_authorized` become true. This candidate does not grant that approval or authorization.

## Structure source, mapping, and feature classification

The sole primary structure source is GEO **GSE132099**, processed pooled K562 in-vivo icSHAPE file `GSE132099_icSHAPE_invivo.out.txt.gz`, associated with GSM3842467 processing metadata. The required file size is 22,840,529 bytes and SHA256 is `d2d168e235faf9cdc3169c96ffc046635695bf1bec5e1e63a4066cd283cd198d`. The expected cache path for later authorized execution is `.cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz`.

GEO reports Bowtie2 alignment to the Ensembl release 88 GRCh38 transcriptome; the release 88 GTF identifies GRCh38.p10. The frozen sequencing cohort uses Ensembl release 91 GRCh38. Mapping is permitted only through the existing class-A bridge: unique GSE132099 stable ID to one Ensembl 88 transcript, processed length agreement, then identical release 88 and release 91 gene, chromosome, strand, exon intervals, transcript length, and transcript sequence. Class B, C, D, E, gene-symbol mapping, many-to-one mapping, one-to-many mapping, length-only mapping, and coordinate interpolation are disallowed. Any disagreement with the frozen class-A mapping is an analysis blocker.

The processed score is interpreted only as an assay-derived, context-specific icSHAPE enrichment/accessibility proxy. It is not a probability, base-pairing truth, causal exposure, or immutable transcript property. No clipping, winsorization, sign change, rank transform, log transform, or thresholding is allowed.

| Variable or candidate | Classification | Locked treatment |
|---|---|---|
| `median_reactivity` | `BIOLOGICAL_STRUCTURE` | Sole biological feature; NumPy float64 median of all finite non-`NULL` per-position enrichment scores for the mapped transcript, using the arithmetic mean of the two middle sorted values for an even count |
| `callable_fraction` | `ASSAY_QUALITY` | Numeric non-`NULL` position count divided by reported transcript length; included in both C_QUALITY and D_STRUCTURE |
| `unique_kmer_fraction_missing`, `miniquant_kvalue_missing` | `MISSINGNESS_CONTROL` | Non-structure indicators fixed above |
| Mean reactivity | `UNSUPPORTED` for this lock | Omitted to avoid a redundant second global location summary and sensitivity to the documented extreme score scale |
| High-reactivity fraction | `UNSUPPORTED` for this lock | Omitted because no pre-existing absolute assay-scale threshold is fixed |
| Low-reactivity fraction | `UNSUPPORTED` for this lock | Omitted because no pre-existing absolute assay-scale threshold is fixed |
| Local variability, variance, local heterogeneity | `UNSUPPORTED` | Omitted; repository evidence did not establish independent reproducibility |
| Transcript-end summaries | `UNSUPPORTED` | Omitted |
| Splice-junction summaries | `UNSUPPORTED` | Omitted |
| Assay RPKM | `UNSUPPORTED` as predictor | Omitted; it is assay metadata and could act as a technical abundance surrogate |

## Structure parsing, callability, and missingness

For each source row, fields are transcript ID, reported length, assay RPKM, then exactly `reported_length` position fields. A position is callable only when its field is not the case-sensitive exact token `NULL` and parses as a finite float64 number. Any other non-numeric or non-finite token is an analysis blocker. The median uses NumPy float64 median semantics, including the arithmetic mean of the two middle sorted values when the callable count is even. Assay RPKM is parsed only for source-schema validation and is never a predictor.

Every frozen transcript must have exactly one class-A mapped row, reported length equal to the validated transcript length, at least 50 callable positions, callable fraction at least 0.5, and a finite median across callable scores. Partial callability is expected: `NULL` positions are excluded from the median numerator and denominator, and callable fraction records the remaining assay coverage. No zero is substituted for an uncalled position.

The 15,999-row cohort is never filtered, enlarged, or reordered for the primary analysis. There is no structure imputation and no structure-missingness indicator because the cohort was fixed using the stated mapping/callability rule. The following all stop the analysis before fitting rather than trigger filtering or imputation: no mapped structure row, duplicate row, mapping ambiguity, reported-length mismatch, fewer than 50 callable positions, callable fraction below 0.5, zero callable positions, missing/non-finite median, or a non-finite `callable_fraction`. A failure affecting even one primary-cohort transcript is an `ANALYSIS_BLOCKER` pending human adjudication.

## Locked fitting procedure

All new hierarchy models use the 15,999 rows in saved Model C input order, the frozen fold assignments, frozen sequence-cluster IDs, frozen five-state labels, and sample weight 1.0. Model C's nine fields come from the authoritative saved input matrix. Added annotation controls are regenerated only from the pinned Ensembl 91 references and locked implementations. No outcome enters feature generation.

The nine saved Model C columns are consumed without re-derivation: `independent_abundance_log1p` is the already stored natural `log1p` abundance; the other eight stored columns use identity transformation. This preserves the documented historical ambiguity-handling discrepancy. Every added annotation field, `callable_fraction`, and `median_reactivity` also uses identity transformation before the fold-local scaler. Training medians for the two imputable annotation fields use NumPy float64 median semantics.

For each outer fold 0 through 4:

1. Training rows are all other folds; test rows are the held-out fold. Row order follows the saved input matrix.
2. For `unique_kmer_fraction` and `miniquant_kvalue`, define missing as absent or non-finite. Compute each replacement median on training rows only, fail if no finite training value exists, and apply that median to missing training and test values. Their indicators are computed before imputation.
3. Every other predictor must already be finite.
4. Fit `StandardScaler(with_mean=true, with_std=true)` on the training rows across the exact ordered feature vector, using population variance (`ddof=0`), and apply it unchanged to the test rows. Constant columns map to zero under sklearn behavior and remain in place.
5. Fit sklearn 1.9.1 `LogisticRegression` with constructor arguments `C=1.0`, `solver="lbfgs"`, `tol=0.0001`, `max_iter=2000`, `random_state=20260923`, `class_weight=None`, and `fit_intercept=True`; omit `penalty`, `multi_class`, and `n_jobs` to retain the re-establishment behavior. The effective penalty is the sklearn 1.9.1 default L2 behavior. Use no sample weights beyond the fixed unit weights.
6. Limit native numerical libraries to one thread. No warm start, calibration, refit on all rows, hyperparameter tuning, seed search, feature selection, interaction, or threshold search is allowed.
7. A convergence warning, non-finite coefficient/probability, probability outside `[0,1]`, row probability sum differing from one by more than `1e-12`, or `n_iter >= 2000` is an analysis blocker.
8. Reorder `predict_proba` explicitly to `BOTH`, `ILLUMINA_ONLY`, `DIRECT_RNA_ONLY`, `NEITHER`, `INDETERMINATE`, with output columns `p_both`, `p_illumina_only`, `p_directrna_only`, `p_neither`, `p_indeterminate`. Predicted class is the maximum probability with lexicographic class-name tie breaking, matching the saved Model C validator.

The canonical development execution environment remains Python 3.11.12, NumPy 2.4.2, SciPy 1.17.1, pandas 3.0.6, DuckDB 1.5.5, scikit-learn 1.9.1, and threadpoolctl 3.7.0 on the current Mac re-establishment environment. A canonical Linux reproduction remains required for reproducibility reporting but cannot replace or tune the locked development result.

## Primary comparison and uncertainty

The single primary hypothesis is a joint model-increment hypothesis: **D_STRUCTURE improves pooled out-of-fold macro-F1 over C_QUALITY**. Historical C is not the primary comparator because it lacks the mandatory enhanced identifiability controls and callable fraction. Callable fraction cannot be credited as biological structure.

The point statistic is

`delta_macro_f1 = macro_f1(D_STRUCTURE pooled OOF) - macro_f1(C_QUALITY pooled OOF)`.

Macro-F1 uses all five named classes, unweighted transcript rows, and `zero_division=0`. All five held-out folds are pooled once; fold scores are descriptive robustness outputs and are not averaged to form the primary statistic. Improvement is positive. A zero difference is a tie and is not improvement.

The paired 95% interval uses 5,000 sequence-cluster bootstrap draws. Sort the 4,314 frozen `sequence_cluster_id` values lexicographically. Initialize NumPy `Generator(PCG64(20260924))`. On every draw, sample 4,314 cluster IDs with replacement, concatenate every transcript row from each sampled cluster, and compute D and C_QUALITY macro-F1 on the identical resampled rows. Store D minus C_QUALITY. The interval is the 2.5th and 97.5th percentiles using NumPy quantile `method="linear"`. A resample missing a class still uses all five labels and class F1 zero for the absent class. This interval is conditional on the fitted OOF predictions, frozen transcript groups, and observed preparations; it is not biological-replicate uncertainty.

## Locked negative-control calibration

The null procedure is a dependence-aware negative-control calibration, not a formal conditional-independence test.

Run exactly 1,000 permutations with NumPy `Generator(PCG64(20260925))`. Start each permutation from the original feature table. Stratify sequence clusters by `(outer_fold, cluster_size)`. Within every stratum containing at least two clusters, sort cluster IDs lexicographically, independently permute the source cluster IDs, order transcripts within every cluster by `stable_id`, and assign the complete ordered `median_reactivity` vector from the source cluster to the target cluster. Equal cluster size makes the vector assignment exact. Strata containing one cluster remain unchanged. Callable fraction and every non-structure field remain attached to the original transcript. The current frozen grouping makes 15,217 of 15,999 rows (95.1122%) permutable under this rule; 782 rows in singleton strata remain fixed.

For every permutation, refit D_STRUCTURE across the five frozen folds using the full locked pipeline. Reuse the observed C_QUALITY OOF predictions. The statistic is permuted D minus observed C_QUALITY pooled macro-F1. Preserve the complete cohort and the absence of biological-feature missingness. Report the 95th percentile with quantile `method="linear"` and the descriptive upper-tail fraction `(1 + number of permuted deltas >= observed delta) / 1001`. Do not call that fraction an exact p-value. The negative control passes only when the observed delta is strictly greater than the permutation 95th percentile.

## Secondary analyses

All secondary outputs are descriptive and cannot rescue a failed primary comparison.

| Output | Classification | Exact direction/comparison |
|---|---|---|
| Pooled macro-F1 increment D_STRUCTURE minus C_QUALITY | `PRIMARY` | Positive is improvement |
| Corrected named-class log loss | `SECONDARY_DESCRIPTIVE` | C_QUALITY minus D_STRUCTURE; positive favors D |
| Accuracy | `SECONDARY_DESCRIPTIVE` | D minus C_QUALITY |
| Balanced accuracy | `SECONDARY_DESCRIPTIVE` | D minus C_QUALITY |
| Multiclass Brier score | `SECONDARY_DESCRIPTIVE` | C_QUALITY minus D_STRUCTURE; positive favors D |
| Per-class F1 for all five classes | `SECONDARY_DESCRIPTIVE` | D minus C_QUALITY; DIRECT_RNA_ONLY and INDETERMINATE must be displayed prominently |
| Confusion matrices | `SECONDARY_DESCRIPTIVE` | Rows observed, columns predicted, fixed class order, for both models |
| Fold-specific macro-F1 and paired delta | `SECONDARY_DESCRIPTIVE` | D minus C_QUALITY in each frozen fold |
| C_HISTORICAL performance and D minus C_HISTORICAL | `SECONDARY_DESCRIPTIVE` | Provenance benchmark only; cannot support a biological increment claim |
| Any unlisted metric, coefficient analysis, feature importance, subgroup, or alternative feature representation | `EXPLORATORY_NOT_LOCKED` | Requires post-hoc label and separate reporting |

Metric definitions are fixed. Corrected log loss is `-mean(log(max(p_actual_class, 2.220446049250313e-16)))` with named-class lookup. Multiclass Brier is the mean across transcripts of the sum across the five ordered classes of `(p_k - 1[y=k])^2`. Accuracy is the correct-prediction fraction. Balanced accuracy is the unweighted mean of the five class recalls. Per-class F1 uses `zero_division=0`.

No class-specific inferential test is authorized. Class-specific results cannot rescue a failed primary result. A decrease greater than 0.02 in either DIRECT_RNA_ONLY or INDETERMINATE F1 is a prespecified class-instability flag that prevents the conclusion `SUPPORTED` but does not by itself establish harm or causation.

## One locked sensitivity analysis

The only primary-claim sensitivity is a stricter callability subset: retain frozen-cohort rows with the same class-A mapping, at least 50 callable positions, and `callable_fraction >= 0.75`. No transcript outside the frozen cohort may enter. Refit C_QUALITY and D_STRUCTURE from scratch using their exact locked feature sets, preprocessing, original fold labels, estimator, class order, seed, and one-thread rule. Compute pooled D-minus-C_QUALITY macro-F1 and the same 5,000-draw paired sequence-cluster bootstrap interval using seed 20260924 and the subset's lexicographically sorted surviving clusters.

The sensitivity changes only the sensitivity-analysis row set; it never changes the primary cohort or primary estimate. It is interpretable as robustness in a more completely observed assay subset, not as a better target population. It cannot upgrade `NOT_SUPPORTED` or `INCONCLUSIVE`, and it cannot rescue a failed primary result. A nonpositive sensitivity point estimate prevents `SUPPORTED`. If any sensitivity training fold lacks one of the five outcome classes or the locked model cannot be fit, the required robustness check is unavailable and the central conclusion is `INCONCLUSIVE` pending human adjudication.

No alternative structure resource is authorized: GSE149767 is unsuitable for validating the sequencing increment and has unresolved annotation/overlap limitations. No 0.25 callability analysis, alternative biological summary, outcome restriction, quantifier substitution, threshold grid, feature ablation, or best-performing sensitivity is permitted. Anything else is post-hoc exploratory work.

## Multiplicity policy

There is exactly one primary hypothesis: the joint D_STRUCTURE model increment over C_QUALITY in pooled OOF macro-F1. The single `median_reactivity` coefficient is not a separate primary hypothesis. The bootstrap interval and the one negative-control calibration quantify the same primary comparison and do not create additional claims.

There are no secondary inferential hypotheses, so no multiplicity correction is applied. All other metrics, five per-class F1 values, confusion matrices, fold results, and the historical-C benchmark are descriptive. The stricter-callability analysis is a one-way robustness gate that can only downgrade support. If any unlisted inferential analysis is later performed, it is post-hoc and cannot alter the locked conclusion.

## Practical-effect categories

Let `delta` be the pooled primary macro-F1 difference D_STRUCTURE minus C_QUALITY. Boundaries are exact:

- `NO_INCREMENT`: `delta <= 0`.
- `NEGLIGIBLE`: `0 < delta < 0.005`.
- `SMALL`: `0.005 <= delta < 0.020`.
- `MEANINGFUL`: `delta >= 0.020`.

Macro-F1 averages five class F1 values. A 0.020 increase therefore requires a total 0.10 increase across the five class F1 values, while a sub-0.005 gain is too small to carry a biological increment claim in this imbalanced, workflow-specific setting. These magnitude thresholds are judgment-based. They are fixed after structure-blind baseline inspection but before any structure outcome; they are not empirically validated minimal important differences, estimated from Model D, or chosen to match a future result.

## Deterministic development conclusion

Define these gates:

- `validity`: every locked artifact, mapping, feature, fold, fit, probability, negative control, and mandatory sensitivity completes without an unresolved blocker or protocol deviation.
- `positive`: primary `delta > 0`.
- `statistical`: paired bootstrap lower bound is strictly greater than 0.
- `practical`: practical category is `MEANINGFUL`.
- `null_calibrated`: observed delta is strictly greater than the negative-control 95th percentile.
- `fold_robust`: at least four of five fold-specific deltas are strictly greater than 0.
- `partial_magnitude`: primary `delta >= 0.005`, so the category is at least `SMALL`.
- `partial_fold_robust`: at least three of five fold-specific deltas are strictly greater than 0.
- `callability_robust`: stricter-callability sensitivity delta is strictly greater than 0.
- `class_stable`: D-minus-C_QUALITY F1 is at least -0.020 for both DIRECT_RNA_ONLY and INDETERMINATE.

Apply the following rules in order:

1. **INCONCLUSIVE** if `validity` is false.
2. **SUPPORTED** if all eight `SUPPORTED` gates (`validity`, `positive`, `statistical`, `practical`, `null_calibrated`, `fold_robust`, `callability_robust`, and `class_stable`) are true.
3. **PARTIALLY_SUPPORTED** only if all of the following hold: `validity`; `partial_magnitude`; `null_calibrated`; `callability_robust`; `partial_fold_robust`; at least one of `statistical` or `practical`; and the result does not satisfy every `SUPPORTED` gate.
4. **NOT_SUPPORTED** in every other valid case.

An interval touching zero fails `statistical`. A delta exactly 0 is `NO_INCREMENT` and `NOT_SUPPORTED`. A positive but `NEGLIGIBLE` delta is `NOT_SUPPORTED` even if its bootstrap interval excludes zero. Failure of permutation calibration is `NOT_SUPPORTED`; equality to the permutation 95th percentile fails `null_calibrated`. A nonpositive stricter-callability sensitivity delta is `NOT_SUPPORTED`. Fewer than three strictly positive fold deltas is `NOT_SUPPORTED`. A `SMALL` result can be `PARTIALLY_SUPPORTED` only when it passes permutation calibration, stricter-callability robustness, at least three of five positive folds, and has a bootstrap lower bound above zero. A `MEANINGFUL` result whose bootstrap interval touches zero can be `PARTIALLY_SUPPORTED` only when it passes permutation calibration, stricter-callability robustness, and at least three of five positive folds. Equality to 0.020 is `MEANINGFUL`.

Weak-class deterioration does not invalidate an otherwise completed analysis. Failure of `class_stable` prevents `SUPPORTED` but can yield `PARTIALLY_SUPPORTED` if every partial-support requirement is met; that class-instability deficiency must be named prominently in the conclusion language and results. No secondary metric or class-specific result can upgrade `NOT_SUPPORTED`. Statistical evidence, practical magnitude, and robustness are reported separately even when the categorical conclusion is determined.

## Protocol deviations and failures

Every event is assigned exactly one class.

### IMPLEMENTATION_REPAIR

A repair corrects code that demonstrably fails to implement an unambiguous locked rule without changing the rule, input identity, cohort, feature definitions, transformations, model, seed, metric, or interpretation. Examples are a column-name typo, deterministic parser defect, or probability-column ordering bug. Preserve the failed artifacts and logs, document the defect and exact patch, and rerun every affected hierarchy model and downstream statistic from a clean derived-output state. If any performance was visible before discovery, human adjudication is mandatory before the rerun; the repair may not be chosen using performance.

### PROTOCOL_DEVIATION

Any change to source identity, mapping class, cohort, feature list/order, threshold, transformation, missingness rule, comparator, model, solver, hyperparameter, fold, seed, thread rule, metric, bootstrap/permutation procedure, sensitivity, decision rule, or claim boundary is a protocol deviation. Software substitution is also a deviation unless exact semantic and numerical equivalence is established without structure-outcome inspection. Record the deviation before re-analysis, preserve the original attempt, and require human and Reviewer 2 adjudication. A deviated analysis is not the locked primary analysis and cannot silently replace it.

### ANALYSIS_BLOCKER

Hash mismatch, unavailable required source, unexpected mapping ambiguity, any primary-cohort structure missingness/callability failure, impossible prespecified feature, empty training-fold imputation basis, missing training class, convergence failure, non-finite fit output, unavailable required negative control or sensitivity, or an ambiguity in the written lock is an analysis blocker. Stop before further structure analysis. Do not drop rows, substitute a feature, relax a threshold, change software, increase iterations, or try another model. Human adjudication is required.

An unexpectedly all-missing `median_reactivity`, any non-finite biological value, or fewer mapped/callable transcripts than the frozen cohort is an analysis blocker. A coding bug may be an implementation repair only when the intended locked behavior is already unique; otherwise it is a protocol deviation or blocker.

## Stop rule and LongBench

After this scientific lock is approved, committed, and pushed, stop. The next phase is `PRESTRUCTURE_IMPLEMENTATION_LOCK`, not Model D execution. Structure access remains prohibited while the exact implementation is created and statically validated and the annotation-only matrix is materialized and hashed. After that implementation lock is committed and pushed, stop again for separate human review and explicit approval; only that approval may authorize structure access.

Once separately authorized in a later phase, development execution is complete only after one valid locked execution has produced OOF predictions for C_ANNOTATION, C_QUALITY, and D_STRUCTURE; the primary point estimate and 5,000-draw paired interval; 1,000 negative controls; every listed descriptive output; the single stricter-callability sensitivity; the practical category; the four-way conclusion; full hashes; convergence records; and a protocol-deviation statement. Then stop.

Do not change features, endpoint, cohort, folds, transformations, thresholds, missingness, comparator, estimator, seed, metric, or conclusion rule. Do not run a rescue analysis. First freeze the development conclusion and obtain human and Reviewer 2 adjudication.

LongBench remains `LOCKED` throughout both the scientific-lock and `PRESTRUCTURE_IMPLEMENTATION_LOCK` phases. It may be considered only after the later development conclusion and execution artifacts are committed and explicitly approved, and only under the separate release conditions in `docs/external_validation_lock.md`. LongBench could evaluate transport of the fixed workflow phenotype and fixed model in its distinct sequencing context. Without a compatible independent cell-matched structure assay, it cannot validate the GSE132099 structure increment. It cannot rescue a negative, weak, invalid, or inconclusive development result and cannot be used to redesign Model D, choose features or thresholds, change the primary metric, redefine outcome categories, or select a better model.

## Maximum manuscript language

The following are ceilings, not required wording.

- **SUPPORTED:** "Within the frozen, structure-callable SG-NEx K562 transcript cohort and named Salmon 1.9.0/Ensembl 91 workflows, pooled GSE132099 K562 in-vivo icSHAPE median enrichment provided a meaningful, held-out incremental association beyond the locked abundance, sequence, annotation-identifiability, and assay-callability comparator. The result is cross-study, conditional, predictive, and non-causal."
- **PARTIALLY_SUPPORTED:** "Within the frozen workflow-specific cohort, the locked structure model showed limited evidence of incremental predictive information. The effect was at least SMALL, exceeded the negative-control 95th percentile, remained positive under stricter callability, and was positive in at least three of five folds, but it did not meet every SUPPORTED gate. The unmet statistical, meaningful-magnitude, four-of-five-fold, and/or class-stability gates are named explicitly; any DIRECT_RNA_ONLY or INDETERMINATE class-instability flag is reported prominently."
- **NOT_SUPPORTED:** "The locked development analysis did not support an incremental contribution of GSE132099 median icSHAPE enrichment beyond the strongest locked non-biological comparator for this workflow-specific conditional estimand. The null or negative result is retained as a scientific result, not described as pipeline failure."
- **INCONCLUSIVE:** "The locked development analysis could not yield a valid conclusion because a prespecified data, mapping, model, negative-control, sensitivity, convergence, or protocol-integrity requirement failed. No direction of biological structure contribution is inferred."

Under every outcome, prohibit claims of technology-intrinsic bias, biological ground truth, endogenous true measurement error, causal structure effects, universal platform behavior, clinical utility, a clinically validated score, broad cross-tissue generalization, matched biological material, or novelty. DIRECT_RNA_ONLY and INDETERMINATE weakness, historical reconstruction limits, ambiguity-handling discrepancy, conditional bootstrap, shared-preparation/workflow limits, cross-study structure context, and absent canonical Linux reproduction remain visible.

## Candidate disposition

This specification resolves the mandatory annotation-only comparator at the design level and leaves no empirical structure threshold to future discretion. It remains a candidate. `BLOCK_STRUCTURE_TEST` stays in force through scientific-lock review and commit and through the separate, blinded `PRESTRUCTURE_IMPLEMENTATION_LOCK`. A scientific-lock commit alone does not authorize structure access; only separate human approval after the implementation lock is committed and pushed may do so.
