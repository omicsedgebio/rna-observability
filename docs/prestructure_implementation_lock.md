# Project 001 RNA Observability: PRESTRUCTURE_IMPLEMENTATION_LOCK candidate

Status: **CANDIDATE_FOR_HUMAN_REVIEW; BLOCK_STRUCTURE_TEST remains in force.**

Parent and scientific-lock commit: `ea1dd05a992b92becc66e1cb825a821e48798923`. The implementation-repair starting commit was `d15af40f99900a539dc9d730548bb408fadce893`; starting `HEAD` and `origin/main` both matched it and the starting worktree was clean. This repair candidate is uncommitted and unpushed. It preserves the committed scientific specification without authorizing or performing structure access.

## Phase boundary and exposure state

No real GSE132099 structure resource, structure-derived per-transcript value table, or LongBench input was opened. No real structure feature, C_ANNOTATION fit, C_QUALITY fit, D_STRUCTURE fit, permutation, or strict-callability sensitivity was run. The only estimator execution was a synthetic toy-unit-test fit. The attempt state remains `MODEL_D_ATTEMPT_NOT_CONSUMED`; `structure_test_authorized` remains false.

## Implementation repair: structure-blind class-A mapping

Human review found that the implementation required a preauthorization
`processed_length_matches_ensembl88` assertion even though the historical full
Phase 3B/3C bridge artifacts are unavailable. The remaining historical bridge
script obtains that assertion from
`results/tables/gse132099_structure_inventory.tsv`, which also contains
structure-derived callability. Reconstructing the assertion before
authorization would therefore violate the structure lock.

This is an `IMPLEMENTATION_REPAIR`, not a `PROTOCOL_DEVIATION`. The locked
scientific condition remains exact equality between the processed GSE132099
reported transcript length and the pinned Ensembl 88 transcript length. The
repair changes only when that equality can truthfully be evaluated:

1. `scripts/materialize_class_a_mapping.py` fixes the expected length from the
   pinned Ensembl 88 reference before unblinding.
2. The materializer uses only the frozen cohort/folds, pinned Ensembl 88/91 GTF
   and transcript FASTA resources, and the committed stable-ID rule. It has no
   CLI path options and explicitly rejects the real structure path, the
   structure-derived inventory, both historical callable bridges, and
   LongBench.
3. The authorized parser still parses the actual processed `reported_length`,
   compares it exactly with the fixed Ensembl 88 expectation, and raises
   `AnalysisBlocker` on inequality before requiring the position-field count to
   equal the processed length.

No source, cohort, mapping class, feature, threshold, transformation,
missingness rule, comparator, estimator, fold, seed, thread rule, metric,
resampling procedure, sensitivity, decision rule, or claim boundary changed.
No real structure or structure-derived table was accessed during the repair.

The revised preauthorization mapping schema is exactly:

1. `stable_id`
2. `structure_transcript_id`
3. `mapping_class`
4. `reported_length`
5. `unique_source_stable_id`
6. `gene_equal_88_91`
7. `chromosome_equal_88_91`
8. `strand_equal_88_91`
9. `exon_intervals_equal_88_91`
10. `transcript_length_equal_88_91`
11. `transcript_sequence_equal_88_91`

Here `reported_length` means **expected pinned Ensembl 88 transcript length**;
it is not an inspected processed-file value. Every remaining evidence flag must
be literal `true`. The generated ignored mapping is
`.cache/model_d/class_a_mapping.tsv`; its Git-visible provenance and digest are
in `metadata/class_a_mapping_receipt.json`. A later execution authorization
must pin that digest. This repair does not create the authorization.

The structure-blind materialization produced exactly 15,999 rows and
1,174,624 bytes with SHA256
`b78371a0b78996ab81fc3e9c617f1478ac3220f7530229a6b9479ef40870f9b4`.
There are zero missing IDs, zero extra IDs, zero duplicate `stable_id` values,
and zero duplicate `structure_transcript_id` values. The generator SHA256 is
`8ff6ab28e5b7197d97e3ea7e9083fc883bc41d44bb125e9d97c8b6ea6d2d4d16`.
The Ensembl 88 GTF/cDNA/ncRNA SHA256 values are respectively
`ba9cb13686c3a4429724dfd6f6e52df92d1cc59675a4590d4a854f64ce633f46`,
`462823cdad614a2a77763004735fb9d4fabf3bb691b57737697208679c26cb86`,
and `298925becc19859d420f5fbd70994c72ab82df1aedc94515faf86b000b2157b4`.
The Ensembl 91 GTF/cDNA/ncRNA SHA256 values are respectively
`1abe442ea2ba90c022545be71c4e7b95b66d45c8c9e4e4ec3788b6be440b598d`,
`a7f0022e884826d70e0a151f6c38547aea8d443eaa9653aaf56e698e23109201`,
and `0ab3565714f88fb98eb7df7814fe3fed770e2b098d37cd7b83601258f87e75dd`.

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

`src/rnaobs/model_d_locked.py` implements the exact ordered hierarchy, two-variable training-fold median imputation, training-only `StandardScaler`, fixed one-thread logistic regression, fixed probability order and lexicographic tie rule, metrics, paired cluster bootstrap, negative-control vector permutation, strict-callability subset, decision boundaries, protocol classifications, structure-blind class-A reference-evidence checks, and strict parser.

`scripts/run_locked_model_d.py` is the single future entry point. `--preflight` only verifies frozen hashes, environment, matrix/fold/order integrity, and guard state; it cannot accept a structure path or fit. `--execute` has fixed structure and mapping paths. It requires a separate human authorization artifact naming the approved committed/pushed implementation lock and pinning the class-A mapping SHA256. Before consuming the attempt, it verifies all frozen implementation hashes and environment versions; rejects LongBench paths; validates the authorization and approved commit against both `HEAD` and `origin/main`; verifies the fixed structure and mapping identities; reads and hashes the non-biological mapping; confirms structure existence and byte size using filesystem metadata only; validates every frozen non-structure input; and rejects an existing marker. It then durably consumes the attempt as the final structure-blind operation and immediately reads structure bytes for the locked SHA256 check. Mapping parsing and real structure parsing follow only after the structure SHA matches. A preflight failure does not consume the attempt. Any failure after structure byte access preserves the consumed attempt and records `ANALYSIS_BLOCKER` with central conclusion `INCONCLUSIVE`; there is no automatic retry.

The parser accepts only tab-delimited rows containing transcript ID, integer reported length, finite assay RPKM, and exactly one token per position. Only exact case-sensitive `NULL` is uncalled. Numeric positions must be finite float64. It computes only callable count, callable fraction, and NumPy float64 median; assay RPKM is excluded. It first requires the actual processed reported length to equal the mapping's fixed Ensembl 88 expected length, then independently requires exactly that many position fields. It rejects all missing, duplicate, ambiguous, non-class-A, length, callability, and non-finite cases.

Historical Model C OOF is loaded only as a descriptive benchmark and never refit. Future real execution fits exactly C_ANNOTATION, C_QUALITY, and D_STRUCTURE over folds 0–4. It pools OOF rows for primary macro-F1, uses 5,000 PCG64 cluster bootstrap draws, enforces the locked 15,217/782 negative-control stratum counts before 1,000 PCG64 permutations, and runs only the locked 0.75-callability sensitivity. Secondary metrics cannot change the decision result.

## Guards

Hard guards cover the cohort, folds, Model C OOF, Model C inputs, scientific config, comparator matrix, execution module, entry script, attempt policy, structure filename/size/SHA256, authorization-pinned class-A mapping, prohibited LongBench path tokens, and consumed attempt. The current attempt policy is `metadata/model_d_attempt_guard.json`; `metadata/model_d_attempt_consumed.json` is absent.

LongBench remains a procedural and entry-point deny. The implementation names no LongBench data path and rejects `longbench`, `GSE303762`, or `longbench-data` in any guarded path. No filesystem search for LongBench values and no LongBench dataset access occurred.

## Validation scope

Validation uses Python 3.11.12, NumPy 2.4.2, SciPy 1.17.1, pandas 3.0.6, DuckDB 1.5.5, scikit-learn 1.9.1, and threadpoolctl 3.7.0 on macOS arm64. Canonical Linux reproduction remains required later and was not performed in this blinded candidate phase.

The synthetic suites cover annotation schema/order/missingness/leakage, imputation and scaler leakage, feature vectors, a five-fold toy fit, parser rules, class-A evidence, metrics/class order/ties, cluster bootstrap, vector permutation, every decision boundary, issue classification, hash guards, attempt consumption, and LongBench denial. The repair tests additionally cover unique and ambiguous release mappings; missing transcripts; every required class-A equality; exact 15,999-row coverage; duplicate IDs; exact schema; expected-length semantics; authorized processed-length equality; position counts; and hard denial of real structure, structure-derived bridges/inventory, and LongBench. Twelve temporary-resource tests specifically verify that missing/wrong mapping, missing/wrong-size structure, invalid frozen non-structure input, absent/invalid authorization, and an existing marker all block at the correct boundary; that successful structure-blind preflight reaches consumption; that consumption occurs immediately before the mocked structure hash/read; and that a post-byte-access structure-hash failure leaves the attempt consumed with no retry. Every execution-ordering resource is synthetic and isolated under a temporary directory. Existing `tests/test_phase3a.py`, `tests/test_phase3b.py`, and `tests/test_phase3c.py`, plus full automatic discovery, are deliberately skipped because those suites include reads of structure-derived summaries or diagnostics. No skipped test is needed to validate the new implementation logic.

Final allowed implementation validation ran 65 tests: 65 passed, zero failed, and zero framework-skipped. Twenty-three tests in the three excluded files were intentionally not run. The four-test `test_prestructure_integrity.py` suite also passed. JSON parsing, Python syntax compilation, mapping generation and artifact validation, locked entry-point preflight, repository validation, and `git diff --check` all passed. The repository validator result was `PASS: Phase 1 scaffold, registry schemas, links, policy flags, and Git-visible file hygiene`; this remains a hygiene/governance check, not biological certification.

## Protocol integrity

`IMPLEMENTATION_REPAIR` is restricted to a demonstrable code defect against an unambiguous lock and requires preserved failed artifacts/logs, exact patch documentation, rerun of all affected outputs, and human adjudication if performance was visible. Any source, mapping, cohort, feature/order, threshold, transformation, missingness, comparator, model, hyperparameter, fold, seed, thread, metric, resampling, sensitivity, decision, or claim change is a `PROTOCOL_DEVIATION` and cannot silently replace the locked primary. Hash, resource, mapping, callability, imputation-basis, class, convergence, non-finite, negative-control, sensitivity, or lock-ambiguity failure is an `ANALYSIS_BLOCKER`.

This candidate creates no scientific result and no authorization. It must be committed, pushed, separately reviewed, and explicitly approved by a human before a distinct authorization record can permit one structure access attempt.
