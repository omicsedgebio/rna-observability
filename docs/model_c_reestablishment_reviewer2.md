# Model C re-establishment Reviewer 2 integrity review

## Completed unattended review — 2026-09-24 UTC

Disposition: **READY_FOR_PRESTRUCTURE_LOCK_SPEC**. Classification remains **PRESTRUCTURE_BASELINE_REESTABLISHMENT**, after prior baseline inspection. This is not exact historical reconstruction, original-prediction recovery or prospective preregistration. The completed review supersedes the earlier incomplete execution disposition preserved below; it does not approve a structure test. **BLOCK_STRUCTURE_TEST** remains in force pending a separately reviewed exact lock specification. No Model D work was performed.

Reviewer 2 integrity review was performed by the executing agent using a separate saved-artifact verification implementation; no independent human reviewer or second agent is implied. Evidence: [execution report](model_c_execution_verification.md), [verification receipt](../metadata/model_c_saved_artifact_verification.json), [fit manifest](../metadata/model_c_reestablishment_manifest.json), and the durable run log.

| Item | Evidence and disposition |
|---|---|
| Pre-fit chronology | Existing authoritative lock 162ee8f4195bf2141cd8c086c131acf2c65dda9b matched HEAD, origin/main, read-only remote check and every protected script/config byte before the sole launch. The missing lock receipt was reconstructed from that existing evidence. PASS; no newly invented scientific lock. |
| Resource identity | SGNEX_META, SGNEX_TX, Ensembl 91 cDNA and ncRNA matched pinned sizes/SHA256. Completed SGNEX_TX was not downloaded again. Transport logs/partials were preserved; no source substitution. PASS. |
| Extraction | Unchanged R script, exit 0: 200,310 annotation rows and 7,900,002 K562 rows; sizes/hashes recorded. R data.table build-version warning retained. PASS with disclosed environment warning. |
| Frozen inputs | All four stated SHA256 values match; 15,999 ordered transcripts; unchanged five folds, nine finite predictors and historical label counts. PASS. |
| Nesting and leakage | Independent Rep3 abundance remains distinct from outcome runs; training-fold StandardScaler remains inside each pipeline; zero duplicate measurement keys; 4,314 sequence groups intact; zero genes spanning folds. PASS for these checks; this is not proof against all possible leakage or cross-study confounding. |
| Attempts and selection | Exactly one wrapper launch and one fitting attempt; first fold started, all five completed, exit 0. Guard and internal marker retained. No retry, tuning or scientific code change. PASS. |
| Numerical fitting | Fold iterations 33, 32, 31, 32, 34; no warning/error in fit log. Frozen one-thread limit applied; available native-library report archived. PASS in declared Mac environment. |
| OOF artifact | Reopened 15,999 rows; exact membership/order/folds/groups; weight 1; valid observed/predicted classes; finite bounded probabilities summing to one; documented lexicographic argmax handling verified. PASS. |
| Input artifact | All nine predictors rebuilt from verified resources using unchanged historical helpers and exactly matched saved values; labels and support counts matched. PASS. |
| Scoring | Named-class corrected log loss independently checked against sklearn with explicit class ordering; macro-F1, accuracy, balanced accuracy, multiclass Brier, class F1, confusion matrices and every fold checked to <1e-12. PASS. |
| Bootstrap | Fixed 100-draw sequence-cluster interval independently recomputed with historical group ordering/seed: [0.512376260340985, 0.5328101838801408]. PASS; conditional OOF uncertainty only. |
| Historical comparison | Macro-F1 difference 0, corrected log-loss difference +5.662137425588298e-15, accuracy difference 0; all within 1e-6. Descriptive agreement only; no historical prediction identity claim. |
| Weak/negative performance | DIRECT_RNA_ONLY F1 0.1733102253032929, recall 0.111358574610245, 50 true positives among 449 observed; INDETERMINATE F1 0.33989765855171344. Retained without relabeling, tuning or exclusion. |
| Structure and external lock | No RNA-structure resources restored/read; LongBench not accessed; Model D not fitted. Procedural evidence from reviewed code and authorized input paths, not an OS-wide access audit. Sandbox denied ps. |
| Git and retention | Scientific artifacts and hashes preserved. No Git write, push, pull, fetch, gh, clean clone or remote modification. Commit/push intentionally deferred by unattended override; not a scientific blocker. OOF/input files remain ignored and need explicit retention in the later human-reviewed workflow. |

No fatal scientific inconsistency was identified in the executed re-establishment and saved-artifact checks. No new empirical claim about structure, novelty, causation, clinical utility, endogenous true error, validated scores or platform accuracy is supported.

Major limitations remain unchanged: historical numerical environment and original prediction identity are unrecoverable; C contains limited annotation-only identifiability controls and preserves the documented sequence ambiguity-handling discrepancy. Mandatory annotation-only controls for a future comparison still require an explicit specification and cannot be replaced by experimental structure. Shared preparations, workflow specificity and cross-study context limit biological/generalization claims. Bootstrap draws are not independent biological replicates. Canonical Linux reproduction remains unperformed; this run is the declared Mac re-establishment. These limits are not repaired by aggregate historical agreement.

## Preserved prior incomplete review (historical record)

The text below describes the earlier pre-fit state and is superseded only as to execution completion by the completed review above. Its historical chronology and substantive limitations are retained.

# Model C re-establishment Reviewer 2 integrity review

Disposition: **BLOCKED_BEFORE_PRESTRUCTURE_LOCK_SPEC**. This is an incomplete pre-fit review; no new model results exist. Classification remains **PRESTRUCTURE_BASELINE_REESTABLISHMENT**, described as **PRE-STRUCTURE BASELINE RE-ESTABLISHMENT AFTER PRIOR BASELINE INSPECTION**. It is not prospective preregistration, exact reconstruction, numerical-equivalence reconstruction or original-prediction recovery.

## Fatal execution gate

The required pre-fit lock commit could not be created because the current session makes .git read-only. Staging failed creating .git/index.lock with Operation not permitted. No push or fitting followed. This is an execution blocker, not evidence of a fatal scientific inconsistency. Post-fit readiness cannot be adjudicated until the authorized workflow completes.

## Findings

| Item | Evidence and disposition |
|---|---|
| Pre-fit chronology | Local and remote main initially verified at 557d2714d1c176dec0587065aca14ea8e7336890. Protocol edits precede fitting, but no committed remote lock exists. FAIL gate. |
| Cohort | Frozen hash matches; existing integrity tests verify 15,999 unique IDs and unchanged fold membership. PASS static checks; feature joins remain unexecuted. |
| Phenotype | Outcome configuration agrees with historical 1 TPM, 2/2 Illumina and 3/4 directRNA support rule and independent Rep3 abundance. Recreated labels/counts remain unverified. |
| Folds and groups | Frozen hash matches; five folds and 4,314 indivisible sequence groups verified. No regeneration. |
| Predictors and preprocessing | Exact nine predictors match historical summary/source. Historical sequence functions and train-fold StandardScaler retained. Completeness/finite checks pending inputs. |
| Tuning and attempts | No tuning, seed search, changed hyperparameters or fit retry. Zero actual re-establishment fit attempts on supplied historical record plus current execution evidence. Historical A/B/C attempts remain disclosed in chronology. |
| OOF completeness and saved metrics | No OOF or baseline matrix exists. Saved-artifact validator and named-class scoring inspected; runtime and numerical validation pending. No metrics fabricated. |
| Hashes and provenance | Four frozen hashes match. Input restoration/checksums, extraction hashes, output hashes and final manifest remain pending. |
| Structure blinding | No structure values/resources read or calculated in this session. Only governance documents/source code inspected. This is procedural evidence, not an OS-wide access audit. |
| LongBench | No LongBench outcome or resource accessed; lock unchanged. |
| Historical performance | Used solely as declared descriptive provenance and to audit fixed tolerance. No new metric comparison performed. |
| Leakage | Independent abundance run differs from outcome runs; scaler fits inside training folds; sequence groups remain together. Gene-level partition integrity and source identity remain to be checked on extracted annotation before claiming broader leakage protection. No fold changes authorized. |
| Multiplicity | Macro-F1 primary; other metrics descriptive; fixed 100-draw cluster interval conditional on fitted folds/libraries. No hypothesis test or Model D specification created. |
| Post-hoc decisions | Prior baseline inspection and historical registry/implementation discrepancies remain disclosed. Current edits only add execution safeguards and provenance; no performance-guided edit occurred. |
| Reproducibility | Python 3.11.12 and all five exact declared installed package versions verified. Syntax and four static integrity tests pass; full imports, extraction, native threads and Linux reproduction remain unverified. |

## Major limitations and pending gates

Absence of the remote pre-fit commit and all saved predictions prevents completing this review. Dataset restoration, measurement-key checks, exact labels, complete predictors, one-attempt execution, saved-file metric verification and durable artifact retention remain mandatory. No claim that these gates passed is supported.

Known scientific limitations remain: historical environment uncertainty prevents original-prediction identity claims; implemented Model C offers limited annotation-only identifiability controls and preserves the documented ambiguity-handling discrepancy; shared preparations and cross-study context limit biological/generalization inference; cluster bootstrap uncertainty is conditional and does not constitute biological replication. None is repaired by changing the frozen baseline here.

No new fatal scientific inconsistency was found in the static protocol comparison. This conclusion is limited to reviewed code/configuration and frozen manifests. Successful baseline re-establishment would permit a separate exact pre-structure lock specification review, never automatic Model D authorization. Current formal **BLOCK_STRUCTURE_TEST** remains in force.
