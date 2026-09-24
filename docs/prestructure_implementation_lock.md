# Project 001 RNA Observability: PRESTRUCTURE_IMPLEMENTATION_LOCK candidate

Status: **CANDIDATE_FOR_HUMAN_REVIEW; BLOCK_STRUCTURE_TEST remains in force.**

Parent and scientific-lock commit: `ea1dd05a992b92becc66e1cb825a821e48798923`. Starting `HEAD` and `origin/main` both matched that commit and the starting worktree was clean. This candidate is uncommitted and unpushed. It implements the committed scientific specification without authorizing or performing structure access.

## Phase boundary and exposure state

No real GSE132099 structure resource, structure-derived per-transcript value table, or LongBench input was opened. No real structure feature, C_ANNOTATION fit, C_QUALITY fit, D_STRUCTURE fit, permutation, or strict-callability sensitivity was run. The only estimator execution was a synthetic toy-unit-test fit. The attempt state remains `MODEL_D_ATTEMPT_NOT_CONSUMED`; `structure_test_authorized` remains false.

## Frozen input verification

All required hashes passed before implementation work:

| Artifact | SHA256 |
|---|---|
| `configs/prestructure_model_d_lock.json` | `d280b0e0505a7eaa24f6df7fcba2d9a6e53fe81fa2610a349b9e370ec7fe3d17` |
| `docs/prestructure_model_d_lock.md` | `488475f6543b56c64f19e9377c13a10bc4b8a9fb1bfec84e94cd572705ec7dcf` |
| `docs/prestructure_model_d_reviewer2.md` | `19d4007b24d5bed969212c732fb6ec0ee3957a013a936895ee8fab6066cb3777` |
| `metadata/prestructure_model_d_lock_candidate_manifest.json` | `5941fb66d6f95deccb04db66b7bc3902a1685010f589a79c162bc55efecf4170` |
| frozen cohort | `3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5` |
| frozen folds | `66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52` |
| Model C OOF | `aa3798858f17194b2acebdcb7e9411e1cb724fa7beff3441b585116c0fef5225` |
| Model C inputs | `c7597fcf57d955a84dcd512d4e4689be6127a408b76aed992d176af8e3a41a31` |
| historical Model C source | `175239e847e7d4cc6a3b812913541d518c942403af43b870af18fff5bdf8259c` |
| feature registry | `30b96cad1df8d9f9cad4e4829702e739a05013a013fb5b4f0b3d770859ab8d4d` |

## Annotation-only comparator

The intended commands were recorded in `metadata/prestructure_annotation_build_plan.json` before expensive computation. Hash-matching cached copies of the pinned Ensembl 91 GTF, cDNA, ncRNA, and original miniQuant source snapshot were used. The exact GTF/combined-FASTA transcript intersection was 199,216 IDs, matching the prior validated universe without consulting structure inventory metadata.

Original miniQuant commit `c1b5a89f3c31c83b271a477475a1e289ee9806d7` was rebuilt and rerun with fragment length 235, effective-length entry, and two threads. Its output was byte-identical to the prior deterministic K-value table (`9bce0d5c…`). Pinned `src/exact_kmers.cpp` was rebuilt with C++23 and run at k=31 over the full sorted 199,216-transcript universe. Annotation controls were recomputed with pinned `src/rnaobs/core.py` over the complete GTF.

The canonical artifact is `results/tables/prestructure_annotation_comparator.tsv.gz`: 15,999 rows, 522,602 bytes, SHA256 `6530a0280112483a5d43790d2518dc11b996c8bee7a24ddbc6891f67ac863fe2`. Its columns, in order, are:

1. `stable_id`
2. `unique_kmer_fraction`
3. `unique_kmer_fraction_missing`
4. `unique_exonic_bases`
5. `shared_exon_fraction`
6. `unique_junction_count`
7. `max_exon_jaccard`
8. `identical_splice_chain_isoforms`
9. `incidence_rank_deficiency`
10. `mean_exon_length`
11. `miniquant_kvalue`
12. `miniquant_kvalue_missing`

There are zero missing `unique_kmer_fraction` values and 212 missing `miniquant_kvalue` values. Indicators match raw non-finiteness exactly. No global imputation was applied. All other controls are finite. IDs are unique, complete, and in exact frozen order. There is no outcome, class, structure, assay-RPKM, future prediction, or outcome-selected field. Full provenance is in `metadata/prestructure_annotation_comparator_receipt.json`.

## Locked future implementation

`src/rnaobs/model_d_locked.py` implements the exact ordered hierarchy, two-variable training-fold median imputation, training-only `StandardScaler`, fixed one-thread logistic regression, fixed probability order and lexicographic tie rule, metrics, paired cluster bootstrap, negative-control vector permutation, strict-callability subset, decision boundaries, protocol classifications, class-A evidence checks, and strict parser.

`scripts/run_locked_model_d.py` is the single future entry point. `--preflight` only verifies frozen hashes, environment, matrix/fold/order integrity, and guard state; it cannot accept a structure path or fit. `--execute` has fixed structure and mapping paths. It requires a separate human authorization artifact naming the approved committed/pushed implementation lock and pinning the class-A mapping SHA256. Before consuming the attempt, it verifies all frozen implementation hashes and environment versions; rejects LongBench paths; validates the authorization and approved commit against both `HEAD` and `origin/main`; verifies the fixed structure and mapping identities; reads and hashes the non-biological mapping; confirms structure existence and byte size using filesystem metadata only; validates every frozen non-structure input; and rejects an existing marker. It then durably consumes the attempt as the final structure-blind operation and immediately reads structure bytes for the locked SHA256 check. Mapping parsing and real structure parsing follow only after the structure SHA matches. A preflight failure does not consume the attempt. Any failure after structure byte access preserves the consumed attempt and records `ANALYSIS_BLOCKER` with central conclusion `INCONCLUSIVE`; there is no automatic retry.

The parser accepts only tab-delimited rows containing transcript ID, integer reported length, finite assay RPKM, and exactly one token per position. Only exact case-sensitive `NULL` is uncalled. Numeric positions must be finite float64. It computes only callable count, callable fraction, and NumPy float64 median; assay RPKM is excluded. It rejects all missing, duplicate, ambiguous, non-class-A, length, callability, and non-finite cases.

Historical Model C OOF is loaded only as a descriptive benchmark and never refit. Future real execution fits exactly C_ANNOTATION, C_QUALITY, and D_STRUCTURE over folds 0–4. It pools OOF rows for primary macro-F1, uses 5,000 PCG64 cluster bootstrap draws, enforces the locked 15,217/782 negative-control stratum counts before 1,000 PCG64 permutations, and runs only the locked 0.75-callability sensitivity. Secondary metrics cannot change the decision result.

## Guards

Hard guards cover the cohort, folds, Model C OOF, Model C inputs, scientific config, comparator matrix, execution module, entry script, attempt policy, structure filename/size/SHA256, authorization-pinned class-A mapping, prohibited LongBench path tokens, and consumed attempt. The current attempt policy is `metadata/model_d_attempt_guard.json`; `metadata/model_d_attempt_consumed.json` is absent.

LongBench remains a procedural and entry-point deny. The implementation names no LongBench data path and rejects `longbench`, `GSE303762`, or `longbench-data` in any guarded path. No filesystem search for LongBench values and no LongBench dataset access occurred.

## Validation scope

Validation uses Python 3.11.12, NumPy 2.4.2, SciPy 1.17.1, pandas 3.0.6, DuckDB 1.5.5, scikit-learn 1.9.1, and threadpoolctl 3.7.0 on macOS arm64. Canonical Linux reproduction remains required later and was not performed in this blinded candidate phase.

The new synthetic suite covers annotation schema/order/missingness/leakage, imputation and scaler leakage, feature vectors, a five-fold toy fit, parser rules, class-A evidence, metrics/class order/ties, cluster bootstrap, vector permutation, every decision boundary, issue classification, hash guards, attempt consumption, and LongBench denial. Twelve temporary-resource tests specifically verify that missing/wrong mapping, missing/wrong-size structure, invalid frozen non-structure input, absent/invalid authorization, and an existing marker all block at the correct boundary; that successful structure-blind preflight reaches consumption; that consumption occurs immediately before the mocked structure hash/read; and that a post-byte-access structure-hash failure leaves the attempt consumed with no retry. Every execution-ordering resource is synthetic and isolated under a temporary directory. Existing `tests/test_phase3a.py`, `tests/test_phase3b.py`, and `tests/test_phase3c.py`, plus full automatic discovery, are deliberately skipped because those suites include reads of structure-derived summaries or diagnostics. No skipped test is needed to validate the new implementation logic.

Final allowed validation ran 41 tests: 41 passed, zero failed, and zero framework-skipped. Twenty-three tests in the three excluded files were intentionally not run. The four-test `test_prestructure_integrity.py` suite passed. JSON parsing, Python syntax compilation, locked entry-point preflight, repository validation, and `git diff --check` all passed. The repository validator result was `PASS: Phase 1 scaffold, registry schemas, links, policy flags, and Git-visible file hygiene`; this remains a hygiene/governance check, not biological certification.

## Protocol integrity

`IMPLEMENTATION_REPAIR` is restricted to a demonstrable code defect against an unambiguous lock and requires preserved failed artifacts/logs, exact patch documentation, rerun of all affected outputs, and human adjudication if performance was visible. Any source, mapping, cohort, feature/order, threshold, transformation, missingness, comparator, model, hyperparameter, fold, seed, thread, metric, resampling, sensitivity, decision, or claim change is a `PROTOCOL_DEVIATION` and cannot silently replace the locked primary. Hash, resource, mapping, callability, imputation-basis, class, convergence, non-finite, negative-control, sensitivity, or lock-ambiguity failure is an `ANALYSIS_BLOCKER`.

This candidate creates no scientific result and no authorization. It must be committed, pushed, separately reviewed, and explicitly approved by a human before a distinct authorization record can permit one structure access attempt.
