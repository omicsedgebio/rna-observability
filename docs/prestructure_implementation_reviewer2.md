# PRESTRUCTURE_IMPLEMENTATION_LOCK candidate: adversarial Reviewer 2

Scope: skeptical computational-reproducibility review of the uncommitted implementation candidate while real GSE132099 structure and LongBench remain unread. This review does not authorize execution.

| # | Challenge | Classification | Finding |
|---:|---|---|---|
| 1 | Does code exactly implement the scientific lock? | `MINOR` | Static comparison found the hierarchy, transforms, estimator, resampling, sensitivity, and decisions encoded exactly. The pinned Mac environment is present; canonical Linux reproduction remains deliberately unperformed and must remain a visible limitation. |
| 2 | Is every future predictor fixed? | `NOT_SUPPORTED` | The only vectors are the nine historical fields, eleven named annotation controls, callable fraction, and median reactivity in the locked nesting. |
| 3 | Does feature ordering match the lock? | `NOT_SUPPORTED` | Tuple constants and tests preserve exact C_ANNOTATION, C_QUALITY, and D_STRUCTURE order; fitting rejects any other vector. |
| 4 | Is the annotation matrix deterministic and frozen? | `NOT_SUPPORTED` | It was regenerated from hash-matching sources, deterministically gzipped, validated, Git-visible, receipted, and protected by SHA256. |
| 5 | Is there outcome leakage into annotation controls? | `NOT_SUPPORTED` | The build consumes only Ensembl annotation/sequence and miniQuant source/output. Schema validation excludes labels, outcomes, predictions, and structure fields. |
| 6 | Is fold-local imputation leak-free? | `NOT_SUPPORTED` | Only the two locked variables are imputed from finite training-fold values; tests show held-out extremes cannot affect medians and empty bases block. |
| 7 | Is StandardScaler training-fold only? | `NOT_SUPPORTED` | It is fit on the imputed training array and only transformed on held-out rows; the synthetic leakage test verifies training moments. |
| 8 | Can the parser silently alter the cohort? | `NOT_SUPPORTED` | It requires the complete one-to-one frozen mapping, exactly one mapped row per frozen ID, and returns frozen mapping order; joins also recheck all 15,999 IDs. |
| 9 | Can NULL become zero? | `NOT_SUPPORTED` | Only exact `NULL` is excluded. Lowercase or other nonnumeric tokens block, and no zero substitution exists. |
| 10 | Can assay_rpkm enter D_STRUCTURE? | `NOT_SUPPORTED` | It is parsed only for finite schema validation and is absent from parser output and every feature tuple. |
| 11 | Can unsupported structure summaries enter? | `NOT_SUPPORTED` | The parser emits only callable count, callable fraction, and median reactivity; feature-vector rejection prevents mean/fractions or other summaries. |
| 12 | Is callable_fraction technical-only? | `NOT_SUPPORTED` | It is appended equally to C_QUALITY and D_STRUCTURE and receives no biological-feature role. |
| 13 | Are mapping failures blockers? | `NOT_SUPPORTED` | The future mapping projection must provide class A plus all eight required evidence flags; missing, false, duplicate, extra, or ambiguous records block. |
| 14 | Is model fitting exactly frozen? | `NOT_SUPPORTED` | Constructor values, folds, training-only transforms, unit weights, one thread, no refit, and convergence/non-finite checks are fixed. |
| 15 | Are class and probability orders fixed? | `NOT_SUPPORTED` | All five labels and named probability columns are constants; predicted ties use lexicographically smallest exact maximum. |
| 16 | Is bootstrap paired and cluster-level? | `NOT_SUPPORTED` | Each PCG64 draw samples lexicographically ordered cluster IDs with replacement and applies identical concatenated rows to both predictions. |
| 17 | Does permutation preserve the specified strata/vector behavior? | `NOT_SUPPORTED` | It changes only median reactivity, assigns whole stable-ID-ordered vectors among equal-size clusters within fold/size strata, leaves singleton strata fixed, and checks 15,217/782 row counts. |
| 18 | Is sensitivity exactly the locked one? | `NOT_SUPPORTED` | Only the frozen-cohort ≥50 and ≥0.75 subset is available; folds are retained, only C_QUALITY/D_STRUCTURE refit, and the paired bootstrap seed is fixed. |
| 19 | Are all decision boundaries exact? | `NOT_SUPPORTED` | Tests cover zero, negligible, 0.005, 0.020, CI equality, permutation equality, sensitivity zero, fold counts, class instability, and all four conclusions. |
| 20 | Can secondary metrics rescue the conclusion? | `NOT_SUPPORTED` | The decision function accepts only locked primary/robustness/class-stability gates; secondary metrics are reported separately. |
| 21 | Can the real model run twice? | `NOT_SUPPORTED` | An exclusive durable metadata marker is fsynced immediately before the first real structure-file byte read; its existence blocks another attempt before structure access, and deletion/retry requires explicit human adjudication outside the entry point. |
| 22 | Can LongBench be accessed? | `NOT_SUPPORTED` | The entry point has no LongBench input and rejects known LongBench path/resource tokens. The repository's procedural lock remains necessary outside this script. |
| 23 | Can real structure be opened before authorization? | `NOT_SUPPORTED` | The fixed execute path requires a separate authorization naming the approved committed/pushed lock before mapping validation, attempt consumption, structure hash, or parsing. |
| 24 | Are hashes checked before execution? | `NOT_SUPPORTED` | Frozen cohort/folds/Model C/config/comparator/code/guard hashes, the authorization-pinned mapping hash, and all frozen non-structure input validations run before attempt consumption. Structure existence and byte size are metadata-only preflight checks; the structure SHA remains after consumption because it necessarily reads real structure bytes. |
| 25 | Are repairs distinguishable from deviations? | `NOT_SUPPORTED` | Disjoint enum/classifier support and documented requirements separate code defects, scientific changes, and blockers. |
| 26 | Does any test read real structure? | `NOT_SUPPORTED` | Parser inputs, model inputs, bootstrap, and permutations are entirely synthetic. Suites known to read structure-derived summaries were not run. |
| 27 | Did this phase generate a new real predictive result? | `NOT_SUPPORTED` | No real model fit occurred. The only estimator test is a 50-row synthetic toy check with no scientific interpretation. |
| 28 | Is implementation discretion left after approval? | `NOT_SUPPORTED` | Resource identities, schemas, paths, transforms, vectors, seeds, counts, metrics, and decisions are fixed. The class-A projection cannot be read in this phase; the approval record must pin its exact SHA256, and the code requires all locked evidence flags before any raw structure parsing. This is data authorization, not a new mapping choice. |
| 29 | Can a structure-blind failure unnecessarily consume the attempt? | `NOT_SUPPORTED` | Synthetic ordering tests show that missing/wrong mapping, missing/wrong-size structure, invalid frozen non-structure inputs, absent/invalid authorization, and an existing marker all block before consumption. Consumption is the final structure-blind operation and is immediately followed by the structure SHA read. A SHA mismatch after that byte access legitimately leaves the attempt consumed, and no automatic retry exists. |

## Additional falsification findings

- The materializer recomputed rather than copied the matrix. Its full-universe FASTA and k-mer intermediate hashes match the prior deterministic artifacts, and regenerated miniQuant output is byte-identical.
- The attempt policy remains unconsumed and false-authorized. `--preflight` does not create a marker.
- The execution script imports no structure at module load and uses no path discovery. Real execution paths are constants.
- All deterministic structure-blind checks, including mapping hash, structure metadata size, and frozen non-structure input validation, precede consumption. The marker write is immediately before the first structure-file byte read.
- A structure SHA mismatch occurs only after real structure byte access and therefore legitimately remains a failed, consumed scientific attempt; the code records `ANALYSIS_BLOCKER`/`INCONCLUSIVE` and supplies no automatic retry branch.
- External deletion of a durable marker, bypass execution, or direct filesystem access cannot be prevented by scientific Python code; those remain governance violations, not hidden supported paths in this implementation.

## Issue counts and disposition

- `FATAL`: 0
- `MAJOR_BUT_MANAGEABLE`: 0
- `MINOR`: 1
- `NOT_SUPPORTED`: 28

No fatal implementation defect was identified. The only minor finding is the already declared absence of canonical Linux reproduction at this phase boundary. Disposition: **ELIGIBLE_FOR_IMPLEMENTATION_LOCK_HUMAN_REVIEW**, with `BLOCK_STRUCTURE_TEST` and `structure_test_authorized = false` unchanged.
