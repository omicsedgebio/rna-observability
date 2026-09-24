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

## Permanent execution clone resumption and transport repair (2026-09-24 UTC)

The execution workspace is `/Users/priyanshpathak/Projects/omicsedgebio/rna-observability-execution`. Initial HEAD, origin/main and independently queried remote main all matched the authoritative pre-fit protocol lock `162ee8f4195bf2141cd8c086c131acf2c65dda9b`; initial `git status --short` was empty. Neither the original checkout nor the previous temporary clone was modified. All four frozen cohort/fold/source/registry hashes matched, the five named output artifacts and attempt marker were absent, and the supplied prior fitting-attempt count was zero.

SGNEX_META was reverified without downloading: 27,131,354 bytes, SHA256 `d37b4e2bf289ea46b59c2cd47c23c036f0708b1c31a5c235687dbfd1048b24b5`. The copied SGNEX_TX partial initially matched 15,818,752 bytes and transport-only SHA256 `0efacebca6b15358aee1478bb8c5bf30b5bd87e283f7a9b7463ccf09253421ed`. The original restore session was retained across the user-directed resumption; no concurrent second restore was started.

The configured SGNEX_TX transfer produced this actual error: `curl: (28) Operation timed out after 3600010 milliseconds with 313381768 out of 653702668 bytes received`. Curl's automatic retry then truncated the partial back toward its original resume offset. Only after observing that error and truncation was the failed retry cycle stopped (terminal exit 130). The failed retry partial was preserved. A previously saved, noninterrupting transport snapshot was restored: 316,735,488 bytes, SHA256 `92e3ccf1af9cc50fb1b7417789ac3c4aa2c4673a0f39bb5a096b531b65bca37c`. The overlapping retry prefix matched that snapshot exactly. These are transport-state hashes, not the final SGNEX_TX hash.

A one-byte probe of the same pinned URL returned HTTP 206 and `Content-Range: bytes 316735488-316735488/669521420`. The repair resumes that same URL and prefix with a 14,400-second timeout and zero automatic retries to retain progress on error. No restart from byte zero, source substitution or scientific-provenance change occurred. Full logs, response headers, partials and the repair record are retained in the ignored `.cache/model_c_execution/` directory. Final resource verification remains a mandatory gate; this entry does not assert download completion.

The execution clone's Git index remains read-only to this session (`git update-index --refresh` failed creating `.git/index.lock`). The user explicitly adjudicated this as a tooling restriction, accepted the already-pushed protocol lock as sufficient chronology, waived a second pre-fit commit, and authorized a fresh writable commit clone with exact source/destination hash verification after successful scientific validation. No frozen scientific configuration or fitting script was changed. No fit has been invoked at this stage; structure remains blinded and LongBench remains locked.

## Unattended filesystem resumption (2026-09-24 06:50 UTC)

The filesystem was reconstructed before action. Process enumeration (`ps`) was denied by the sandbox; this limitation was not bypassed. SGNEX_TX was already complete, with the preserved transport log reporting completion at 03:24:39 UTC. Its final pinned size and SHA256 were reverified immediately; no second SGNEX_TX transfer was started. SGNEX_META was also reverified without download. Both launch guard and internal fit marker, and all five scientific output artifacts, were absent. Initial fitting-attempt count remains zero on the supplied record and durable filesystem evidence.

Eight incomplete Ensembl 91 cDNA range segments last modified approximately three hours earlier were preserved with hashes in `.cache/model_c_execution/preserved_ensembl91_cdna_segments_20260924/` before restoring only the pinned Ensembl 91 cDNA and ncRNA resources. The existing registered URLs and resource identities were unchanged. Both reference restores exited successfully and passed exact size/SHA256 checks.

Resource verification:

```json
{
  "SGNEX_TX": {
    "bytes": 669521420,
    "sha256": "51d41a85766e536fc995965d820facc3e2e02bb99391330b9df4a46ff9a3a7d2",
    "verified": true
  },
  "SGNEX_META": {
    "bytes": 27131354,
    "sha256": "d37b4e2bf289ea46b59c2cd47c23c036f0708b1c31a5c235687dbfd1048b24b5",
    "verified": true
  },
  "ensembl91_cdna": {
    "bytes": 65088589,
    "sha256": "a7f0022e884826d70e0a151f6c38547aea8d443eaa9653aaf56e698e23109201",
    "verified": true
  },
  "ensembl91_ncrna": {
    "bytes": 9365901,
    "sha256": "0ab3565714f88fb98eb7df7814fe3fed770e2b098d37cd7b83601258f87e75dd",
    "verified": true
  }
}
```

All four frozen hashes and every protected script/config byte match lock `162ee8f4195bf2141cd8c086c131acf2c65dda9b`. Local HEAD, local origin/main and a read-only `git ls-remote` check agree with this lock. The missing `metadata/model_c_prefit_lock.json` receipt was reconstructed from these existing facts before fitting; no scientific code/configuration changed and no new lock was invented. Three applicable static integrity checks passed.

The user’s latest unattended override supersedes the older clean-clone plan above: no push, pull, fetch, gh, clean clone, commit or remote modification is permitted in this invocation. Commit/push are intentionally deferred for human review and are not a scientific completion gate. No Git write was attempted. No RNA-structure values/resources or LongBench data were accessed; no Model D work was performed.

Only the unchanged `scripts/model_c_extract.R` was launched for extraction, after all four resources were verified. Completion and data-dependent pre-fit gates remain pending at this entry.

## Extraction and final gate before sole launch

The unchanged R extraction exited 0. Its data.table build-version warning is retained in the extraction log; no extraction error occurred. Exact output counts, sizes and SHA256 values:

```json
{
  ".cache/phase3a/qc/sgnex_annotation_full.tsv": {
    "bytes": 40031956,
    "sha256": "5ac1122d0e751b235d416ee7457e2711108935a55f417accf23e33fe7c7661fa",
    "rows_excluding_header": 200310
  },
  ".cache/phase3a/qc/k562_quantification.tsv": {
    "bytes": 859220112,
    "sha256": "f00b1002e1b5c5e3109df112fbeb6c9799fafb795ee2d1cd546a42c90878289a",
    "rows_excluding_header": 7900002
  },
  ".cache/phase3a/qc/model_c_R_session.txt": {
    "bytes": 1476,
    "sha256": "75ce2d04e4d59795db6f660710413759e129795bfafc89e4191725f69dda0d63"
  }
}
```

The non-fitting preflight exited 0. All required gates passed: 15,999 ordered transcripts, exactly nine frozen finite predictors, unchanged historical counts and folds, 4,314 intact sequence groups, zero duplicate measurement keys, and zero genes spanning folds. Every protected script/configuration matches the existing lock. All five outputs and both fit guards were absent immediately before launch authorization. Structure remains blinded; LongBench remains locked. The durable detailed gate is `.cache/model_c_execution/final_prefit_gate.json`. Only `.automation/run_model_c_once.sh` may consume the single launch authorization.

## Immediate pre-fit verification

```json
{
  "utc": "2026-09-24T07:00:29.314300+00:00",
  "n": 15999,
  "labels": {
    "ILLUMINA_ONLY": 4680,
    "BOTH": 4240,
    "INDETERMINATE": 3747,
    "NEITHER": 2883,
    "DIRECT_RNA_ONLY": 449
  },
  "features": [
    "independent_abundance_log1p",
    "sequence_length",
    "gc_fraction",
    "exon_count",
    "isoforms_per_gene",
    "sequence_cluster_size",
    "homopolymer_fraction",
    "low_complexity_fraction",
    "sequence_entropy"
  ],
  "sequence_groups": 4314,
  "complete_finite_predictors": true,
  "duplicate_measurement_keys": 0,
  "exact_order_and_folds": true,
  "outputs_absent": true,
  "structure_inputs_read": false,
  "longbench_inputs_read": false,
  "python": "3.11.12 (main, Apr  8 2025, 14:15:29) [Clang 16.0.0 (clang-1600.0.26.6)]",
  "packages": {
    "numpy": "2.4.2",
    "scipy": "1.17.1",
    "pandas": "3.0.6",
    "duckdb": "1.5.5",
    "scikit-learn": "1.9.1"
  },
  "frozen_sha256": {
    "analysis/baseline_models/fit_structure_blind.py": "175239e847e7d4cc6a3b812913541d518c942403af43b870af18fff5bdf8259c",
    "metadata/final_transcript_cohort.tsv": "3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5",
    "metadata/cv_folds.tsv": "66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52",
    "metadata/feature_definitions.tsv": "30b96cad1df8d9f9cad4e4829702e739a05013a013fb5b4f0b3d770859ab8d4d"
  },
  "extracted_sha256": {
    ".cache/phase3a/qc/sgnex_annotation_full.tsv": "5ac1122d0e751b235d416ee7457e2711108935a55f417accf23e33fe7c7661fa",
    ".cache/phase3a/qc/k562_quantification.tsv": "f00b1002e1b5c5e3109df112fbeb6c9799fafb795ee2d1cd546a42c90878289a"
  }
}
```

## Successful sole fitting attempt and saved-artifact verification

The single permitted wrapper launch consumed `.automation/MODEL_C_FIT_LAUNCH_CONSUMED` at 2026-09-24T07:00:08Z. The internal fitting marker was fsynced at 07:00:31.496327Z, first fold started, and all five folds completed. Wrapper completion was 07:00:34Z, exit 0. Both guards, stdout/stderr and outputs are retained. No retry or model modification occurred.

The independent saved-artifact verifier exited 0: exact OOF constraints, exact rebuilt nine-column input matrix/support-derived labels, all overall and fold metrics, class F1/confusion matrices, 100-draw sequence-cluster interval and every manifest hash passed. The durable receipt is `metadata/model_c_saved_artifact_verification.json`; the full programmatically generated report is `docs/model_c_execution_verification.md`.

OOF SHA256: `aa3798858f17194b2acebdcb7e9411e1cb724fa7beff3441b585116c0fef5225`. Input SHA256: `c7597fcf57d955a84dcd512d4e4689be6127a408b76aed992d176af8e3a41a31`. Historical differences: {"macro_f1": 0.0, "log_loss": 5.662137425588298e-15, "accuracy": 0.0}; all satisfy absolute tolerance 1e-6. No identity of original historical predictions is inferred. Classification remains PRESTRUCTURE_BASELINE_REESTABLISHMENT.

Reviewer 2 integrity review is complete, with weak DIRECT_RNA_ONLY and INDETERMINATE performance and existing limitations preserved. Disposition READY_FOR_PRESTRUCTURE_LOCK_SPEC means only readiness for a separate exact lock-specification review. BLOCK_STRUCTURE_TEST remains in force. Structure remains blinded, LongBench locked and unaccessed, and no Model D work was performed. Git commit/push are intentionally deferred for human review under the latest unattended override; no Git write or remote modification occurred.
