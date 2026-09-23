# Model C prediction artifact reconstruction audit

Parent: `557d2714d1c176dec0587065aca14ea8e7336890`. The active checkout and private remote matched this commit and were clean at start.

## Pre-run provenance decision

Selected path before any new fit: **PRESTRUCTURE_BASELINE_REESTABLISHMENT**.

This is **PRE-STRUCTURE BASELINE RE-ESTABLISHMENT AFTER PRIOR BASELINE INSPECTION**. The original OOF predictions cannot be found. Historical numerical-library/BLAS and thread state are not fully recoverable, so no exact reconstruction is attempted. Matching aggregate metrics would not prove identical predictions. The one authorized run will preserve the executable historical Model C, phenotype, cohort, folds, feature registry, model family, fixed hyperparameters and seed. There is no search over configurations or seeds. Its predictions, once persisted and checked, become the sole comparator; historical performance remains provenance only.

## Search before training

Inspected current files, all reachable Git objects and path history, deleted tracked paths, relevant retained temporary directories, serialized-model/prediction filenames, committed baseline source and summaries, tests, command log and prior integrity audit. `git fsck --no-reflogs --unreachable` reported no recoverable dangling artifact. Relevant temporary directories were the Phase 3D final/commit and Phase 3C final/clone directories identified in the prior audit. Only aggregate metrics, summary and cross-tabulation were found. No historical OOF file, serialized fitted model, or historical prediction digest was recovered. No unrelated scientific cache was inspected.

## Historical specification recovery

| Component | Classification | Recovered specification or limit |
|---|---|---|
| Cohort | EXACTLY_RECOVERED | 15,999 rows in final_transcript_cohort.tsv; SHA256 3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5 |
| Outcome rule | EXACTLY_RECOVERED | historical category() and run constants; TPM >=1; 2/2 Illumina and >=3/4 directRNA; intermediates indeterminate; unchanged normEst, no reclosure/pseudocount |
| Original transcript-level labels file | UNKNOWN | Labels are reproducible from pinned source and exact rule; no original per-transcript prediction/label artifact retained |
| Source values and annotation | EXACTLY_RECOVERED | Pinned SG-NEx transcript and metadata RDS; original source SHA256 in download_provenance.tsv; original R extraction and DuckDB SQL available |
| Folds | EXACTLY_RECOVERED | Existing five-fold manifest; SHA256 66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52; no regeneration |
| Model C feature list | EXACTLY_RECOVERED | independent_abundance_log1p, sequence_length, gc_fraction, exon_count, isoforms_per_gene, sequence_cluster_size, homopolymer_fraction, low_complexity_fraction, sequence_entropy |
| Feature implementation | EXACTLY_RECOVERED | Existing fit_structure_blind.py functions; source SHA256 175239e847e7d4cc6a3b812913541d518c942403af43b870af18fff5bdf8259c |
| Registry vs implementation | EXACTLY_RECOVERED | Historical sequence code removes non-ACGT characters before runs/windows. Preserve implementation without repairing this known registry discrepancy or adding omitted identifiability predictors. Registry unchanged. |
| Missing-value handling | EXACTLY_RECOVERED | Historical covariate NA filled with zero; unsupported/missing measurement comparisons behave as false. Eligibility should make those paths unused. Validate complete input rows and finite predictors before fitting; fail rather than change membership/impute new values. |
| Categorical encoding | EXACTLY_RECOVERED | Target string labels; sklearn fitted class order mapped to explicit named probability columns; no categorical predictor |
| Scaling | EXACTLY_RECOVERED | StandardScaler inside each training fold; default centering and variance scaling; applied to all nine numeric columns |
| Estimator | EXACTLY_RECOVERED | LogisticRegression, multinomial behavior under lbfgs for five classes |
| Hyperparameters | INFERRED_WITH_STRONG_EVIDENCE | Original explicit max_iter=2000, random_state=20260923; C=1, tol=1e-4, lbfgs, L2, intercept, no class weights were defaults; no tuning |
| Seeds and folds loop | EXACTLY_RECOVERED | 20260923; sorted folds 0-4; final manifest row order drives train/test row order |
| Invocation | EXACTLY_RECOVERED | .venv/bin/python3.11 analysis/baseline_models/fit_structure_blind.py; this task calls recovered helper functions but fits only C, leaving A/B untouched |
| Historical Python family | INFERRED_WITH_STRONG_EVIDENCE | Python 3.11 from execution record; full old environment not archived |
| Historical sklearn version | INFERRED_WITH_STRONG_EVIDENCE | 1.9.1 printed in earlier execution; original constructor signatures/warnings agree |
| Historical pandas/DuckDB/SciPy | INFERRED_WITH_STRONG_EVIDENCE | 3.0.6 / 1.5.5 / 1.17.1 from execution and regenerated audit; prior committed QC also contains 1.18.1 from a different environment |
| Historical NumPy/BLAS/thread/compiler state | UNKNOWN | No complete fit-time environment or native-library/thread record; exact floating-point reproduction cannot be asserted |
| Macro-F1 | EXACTLY_RECOVERED | sklearn f1_score, average=macro over all five named classes, zero_division=0, unweighted transcripts |
| Log loss | EXACTLY_RECOVERED | Original column-order bug documented; correct scorer must explicitly index each row's actual-class probability or reorder for sklearn; no model change |
| Confidence interval | EXACTLY_RECOVERED | 100 cluster bootstrap draws, seed 20260923, groupby(sort=False), resample 4,314 cluster IDs with replacement, retain all rows, 2.5/97.5 percentiles, conditional on fitted OOF predictions |
| Original individual probabilities | UNKNOWN | No file/hash; aggregate numbers cannot recover them |
| Historical fold/class-specific scores | UNKNOWN | No such historical saved score tables located; new outputs will be reported without invented historical comparators |

## One-run protocol fixed before fitting

Use configs/model_c_reestablishment.json and configs/model_c_outcome.json, seed 20260923 and one thread. Pin sklearn 1.9.1, pandas 3.0.6, DuckDB 1.5.5, SciPy 1.17.1 and NumPy 2.4.2 before fitting; NumPy is a declared re-establishment environment choice, not a claim about the old environment. Restoring four checksummed reference/processed inputs is required because ignored caches were not retained; no structure resource or raw reads are retrieved. Historical helper functions and annotation extraction are reused exactly, without running prior phases or their audits.

Persist full-precision probabilities, observed/predicted class, transcript ID, fold, sequence group and weight=1 in deterministic gzip (mtime=0), then reopen the saved file to calculate metrics. Also retain the actual baseline feature matrix so the future same-fold D comparison need not rebuild or silently reinterpret features. No outcome-derived covariate or structure value enters this matrix. Generated artifacts must fit the existing lightweight Git policy, splitting losslessly into fixed shards only if necessary.

Primary baseline metric remains macro-F1. Correct log loss, accuracy, balanced accuracy, Brier, class F1, confusion matrix and fold metrics are verification outputs. Absolute tolerance 1e-6 for historical aggregate agreement is fixed in config before fitting; it is about six orders below the unit metric scale and does not imply prediction identity or prove the cause of any difference. Do not label this an exact/numerically equivalent historical reconstruction merely because aggregate scores agree. No retry for score agreement is permitted.

The original feature registry and baseline source remain unchanged. Richer annotation identifiability controls were not in the executed C and are not introduced during reconstruction. Central structure hypothesis remains unseen; LongBench remains locked.

## Post-run disposition

Pending the single run and saved-artifact verification. Exact Model D feature/statistical choices were incomplete in the earlier lock audit; durable baseline predictions alone will not be treated as automatic structure-test authorization.

## Resumed Phase 0 inspection (2026-09-23)

The resumed checkout was on main at the stated parent, with exactly the six untracked reconstruction files supplied by the user, no tracked/staged diff, and origin/main independently verified by git ls-remote at that parent. Earlier search statements above are inherited records, not searches repeated in this session. The outside-repository backup was not touched. All five named re-establishment outputs were absent. No fitting occurred in the interrupted restore according to the supplied execution record; absence of outputs alone is not proof of that historical fact.

All four frozen SHA256 values match. Historical source, extraction SQL/R, baseline summary, chronology, claims register, outcome and re-establishment configurations were compared directly. The nine predictors, threshold/support phenotype, independent Rep3 covariate, train-fold StandardScaler, five frozen folds and fixed estimator match. No material scientific inconsistency was found. Existing limitations (minimal identifiability controls, ambiguity handling, historical environment uncertainty and prior baseline inspection) remain unchanged.

Pure implementation safeguards added before any fitting: require Python 3.11; refuse all pre-existing outputs and a durable exclusive attempt marker; verify ordered cohort and group/fold consistency; provide a non-fitting --preflight mode; check local/remote pre-fit lock and committed protocol bytes; append immediate pre-fit checks to this audit; build a separately named Model C derived database with extraction hashes rather than reuse an unverified historical database; and enforce one extraction thread. These do not change values, predictors, phenotype, preprocessing, model or tuning. The historical source remains byte-for-byte unchanged. An attempt marker is fsynced immediately before the fold loop; any unexpected failure after that point requires adjudication, never automatic rerun. Exact probability ties use lexicographic class order, matching sklearn.

The existing environment reports Python 3.11.12 and all five exact declared package versions. Full import/runtime checks and input completeness checks remain gates after restoration. Restoration is restricted to the four named processed/reference inputs (771,107,264 bytes total; not raw sequencing). Existing transcript partial bytes will be preserved. No RNA-structure values, structure resources, LongBench outcomes, or unrelated scientific caches were accessed. Lock commit identity will be recorded after committing and remote verification; this is a baseline re-establishment lock, not permission for a structure test.

### Phase 0 execution blocker

All four existing prestructure integrity tests, repository validation, Python syntax compilation and git diff --check passed. The attempt to stage the six protocol files failed with: `fatal: Unable to create '/Users/priyanshpathak/Projects/omicsedgebio/rna-observability/.git/index.lock': Operation not permitted`. The session filesystem policy grants read-only access to .git and does not permit approval escalation. No pre-fit commit was created, no push was attempted, and the mandatory remotely committed lock gate remains unmet. No restoration, extraction, preflight data construction or fitting was started in this resumed session. The number of actual re-establishment fitting attempts remains zero on the supplied prior record and current execution evidence. The six protocol files remain untracked, with the implementation edits described above; the separate backup remains untouched.

The five scientific output artifacts remain absent. New metrics, bootstrap intervals and historical differences are unavailable, and tolerance is not evaluated. The Reviewer 2 document records an incomplete pre-fit review, not a successful post-fit review. Resume requires a session able to commit to this repository, then remote lock verification before continuing Phase 1. Do not treat these pending checks as passed.
