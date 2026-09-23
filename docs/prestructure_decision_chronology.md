# Pre-structure integrity adjudication

Decision: **BLOCK_STRUCTURE_TEST**

Review timestamp UTC: 2026-09-23T17:33:34Z (review time, not a lock timestamp).
Reviewed parent: `d6c55d345fc44630977aa81f921cf1cf1d581d80`, initially equal to private `origin/main` on clean branch `main`.

This decision does not overturn the historical Phase 3D GO_TO_BASELINES, G3 workflow-specific PASS, or G9 PASS. It addresses whether an executable, auditable pre-structure analysis lock can be established with the available artifacts. Prior inspection of structure-blind baseline results is not itself a reason to reject a future D-vs-C development analysis.

## Evidence and limits

Sources are Git history and diffs, the Phase 3C/3D reports, the committed integrity correction, the baseline script and aggregate tables, existing cohort/fold manifests, and the earlier execution transcript available in this conversation. Commit times establish when content was committed, not when an uncommitted decision was first made. File modification times after checkout do not establish decision order. The exact wall-clock time of every uncommitted edit is not recoverable; unknown times are explicitly retained as unknown.

No scientific source dataset was downloaded or opened for this review. No A/B/C refit, D fit, structure-score calculation, structure-versus-outcome or residual comparison, or LongBench outcome access occurred. The procedural evidence supports continued central-hypothesis blinding; this is not an operating-system access audit.

## Reconstructed event order

All times below are UTC on 2026-09-23 unless stated otherwise.

| Time or interval | Evidence | Event |
|---|---|---|
| 04:21:01 | `e83efc6` | Phase 2 includes broad candidate structure summaries; they are not an exact final D specification. |
| 12:34:39 | `59e6cce` | Phase 3A sequence/identifiability feature registry committed; no A/B/C performance yet. |
| 13:13:40 | `a797439` | Phase 3B replaces pseudocount outcome with zero-aware candidates and conditional missingness design. |
| 13:59:38 | `56bd8ae` | Phase 3C recommends TPM 1, Illumina 2/2 and direct-RNA 3/4 support; endpoint is pending review. |
| 14:31:29 | `09d1263` | Phase 3C final report: 15,999 pre-endpoint IDs, no models, G3/G9 unresolved, conditional structure feature evidence. |
| After Phase 3C, before first completed fit | Earlier execution transcript; bundled later in `5b98bfd` | Workflow-specific scope selected; BLAST grouping and final folds constructed; baseline code written. No separate commit captures these intermediate states. |
| Before first completed baseline metrics | Earlier execution transcript | Initial baseline attempts fail on index naming and sequence-feature implementation; k-mer predictor removed before the first successful fit; obsolete sklearn argument removed before fitting. Bootstrap resampling reduced from 200 to 100 during an interrupted run, before the first metric table was inspected. No observed performance-based comparison accompanies these changes. |
| Before 15:30:16; approximately 15:27-15:28 from execution output | Earlier execution transcript; confirmed in `d6c55d3` integrity report | A/B/C predictions and metric table produced and inspected. Plotting aborts after predictions/metrics were written. Saved metrics are explicitly read. |
| 15:30:16 | Timestamp in plan; execution transcript | Plan written after baseline performance inspection. It is not a prospective pre-baseline freeze. |
| After 15:30:16, before 15:46:28 | Earlier execution transcript | A/B/C rerun under recorded plan; it cannot erase prior exposure. |
| 15:46:28 | `5b98bfd49195585bc866ad8894f86adfc14a80c7` | Design, code and aggregate baseline results first committed together. Per-transcript OOF predictions are ignored and not included. |
| 15:46:56 | `99ddb849c1e9b4d32d5aa30be423a120088c3201` | Closeout provenance committed. |
| 17:27:43 | `d6c55d345fc44630977aa81f921cf1cf1d581d80` | Freeze chronology and probability-ordering errors documented. Corrected log losses computed from then-available saved predictions, without refitting. |
| This adjudication | File/history search | The ignored OOF predictions are no longer available in the active checkout or retained relevant temporary directories. No Git version or recorded OOF hash exists. Aggregate metrics and code remain available. |

## Element-by-element chronology and contamination audit

A = fixed before any baseline performance was inspected. B = changed or newly formalized after inspection without structure-outcome information. C = timing or exact specification cannot be established. A classification supported by the execution transcript is identified as such; it is weaker than an independently committed preregistration. Formalization after inspection is separated from evidence of performance-driven optimization.

| Design element | Class | Baseline dependence | Evidence and interpretation |
|---|---|---|---|
| Five-state primary phenotype | A | BASELINE_INDEPENDENT | Rule appears as candidate before modeling and is used unchanged in the first successful fit. Formal GO language came later; no alternate phenotype was fit and selected by score in the observed record. |
| TPM 1; Illumina 2/2; direct-RNA >=3/4; intermediate support indeterminate | A | BASELINE_INDEPENDENT | Phase 3C measurement-only threshold grid precedes all baselines; Phase 3D code implements those values. |
| Salmon 1.9.0 / Ensembl 91 workflow-specific strategy | A | BASELINE_INDEPENDENT | Scope narrowed before first successful fitting in the execution transcript, with quantifier evidence rather than model performance. |
| Cohort membership | A | BASELINE_INDEPENDENT | Stable-ID set is exactly equal between `09d1263` and current 15,999-row manifest; status and ordering changed, membership did not. |
| Final CV grouping and assignment | A | BASELINE_INDEPENDENT | 95% identity / 90% coverage grouping and folds existed before fitting in execution order. Hashes match baseline summary. No performance-based fold search is observed. |
| Broad baseline feature registry | A | BASELINE_INDEPENDENT | Definitions committed in Phase 3A. Not all registered controls were used. Registry/implementation ambiguity handling differs. |
| Executed Model A | A | BASELINE_INDEPENDENT | Independent Rep3 log1p abundance, sequence length and GC selected in initial baseline script before successful fitting. |
| Executed Model B | A | BASELINE_INDEPENDENT | Adds exon count, isoform count, cluster size. Initial attempted k-mer inclusion was removed before first successful fit/metric inspection, not following a successful score comparison. This reduction weakens identifiability coverage but is not evidence of score optimization. |
| Executed Model C | A | BASELINE_INDEPENDENT | Adds homopolymer burden, low-complexity fraction and entropy before successful fitting. Definition bugs/registry mismatch remain disclosed, without rewriting features here. |
| Model family and fixed hyperparameters | A | BASELINE_INDEPENDENT | StandardScaler plus logistic regression, C=1 default, lbfgs default, max_iter=2000, seed 20260923 appear before completed results. No hyperparameter search is present. Environment/version defaults are not a complete portable reproduction lock. |
| Baseline evaluation metric set | A | BASELINE_INDEPENDENT | Accuracy, balanced accuracy, macro-F1, log loss and Brier are calculated in the original successful script. Incorrect probability-ordering affects log loss only as documented. |
| Primary D-vs-C metric | C | UNCLEAR | Older draft names continuous MAE, incompatible with the categorical endpoint. Phase 3D lists several classification metrics but never identifies one exact primary D-vs-C contrast. Macro-F1 being prominently reported does not establish prior selection for H3. |
| Recorded freeze and authorization wording | B | BASELINE_INFORMED | The document was written with baseline results already known; it cannot support a prospective claim. No evidence shows the wording was chosen to maximize a later D effect. |
| Success/failure interpretation | B | UNCLEAR | Qualitative final wording was newly written after baseline inspection. No practical-effect margin, multiplicity family or exact four-way decision rule was fixed; causal influence of baseline scores on wording is not established. |
| Exact future D feature vector | C | UNCLEAR | Mean/median/high/low are reservations, not an unambiguous list with cutoffs and transformations. The older structure registry also lists unsupported regional/variance features. No structure-outcome-informed selection is found. |
| Structure feature reservation and feasibility exclusions | A | BASELINE_INDEPENDENT | Phase 3C reserves global summaries conditionally and finds local/end/junction summaries unsupported using structure-to-structure evidence only. |
| Conditional structure estimand principle | A | BASELINE_INDEPENDENT | Restriction to measured, mapped, sufficiently callable transcripts predates baselines. |
| Exact estimand abundance restriction | C | UNCLEAR | `structure_estimand.md` requires Rep3 TPM >=1, whereas final 15,999 cohort and Phase 3D plan have no such restriction. We preserve authoritative cohort membership and annotate the older text; do not silently discard low-abundance rows. |
| Complete-case missingness strategy; no population IPW | A | BASELINE_INDEPENDENT | Phase 3B/3C availability analysis motivates conditional inference before baselines. Whether callable fraction enters D or a separate nuisance comparator is not finally specified. |
| D-vs-C uncertainty, permutations and multiplicity | C | UNCLEAR | Baseline bootstrap uses 100 cluster resamples. This does not define a paired D/C procedure, exchangeability scheme for unequal clusters, permutation count or multiple-testing family. |
| Baseline result inspection | B | BASELINE_INFORMED | Direct inspection precedes the recorded freeze; later repetition did not restore prospective status. This is an exposure event, not a claim that the endpoint was optimized. |
| Log-loss correction and limitations language | B | BASELINE_INFORMED | Triggered by observed scorer warning and saved predictions. Correction is explicitly recorded and does not change fitted models, labels or predicted probabilities. |

No evidence in the observed record demonstrates choosing a phenotype, threshold, quantifier, cohort, folds, model family or penalty to obtain stronger A/B/C performance. The exact primary H3 metric and some specification choices remain UNCLEAR. Consequently the overall answer to whether result-driven baseline design changes were found is **UNCLEAR**, not an accusation of optimization and not a guarantee that undocumented optimization was impossible.

## Artifact availability and hashes

| Artifact | SHA256 / status |
|---|---|
| Final cohort | `3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5` |
| CV folds | `66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52` |
| Historical baseline metrics TSV | `c3e51b6fd307f10fe20f6593574e18678cf62f9fc6072ad7f03c8e5ac6305931` |
| Baseline summary JSON | `b1e2dcbac3d5045d52ebe2b3f8266975fdde18104da29ee0df71be33507b9f8e` |
| Feature registry | `30b96cad1df8d9f9cad4e4829702e739a05013a013fb5b4f0b3d770859ab8d4d` |
| Structure feature specification (candidate registry, not a D lock) | `271e23c803f1bd081f2c4007b4bdb9e038d009673bfd96ddc08dd5389dd4b580` |
| Baseline source | `175239e847e7d4cc6a3b812913541d518c942403af43b870af18fff5bdf8259c` |
| Model C per-transcript OOF probabilities | MISSING; no recorded hash; cannot freeze these predictions |
| Pre-structure lock document/hash/timestamp | NOT_CREATED / NOT_APPLICABLE |

The historical metrics TSV contains invalid original log-loss columns; its hash preserves the artifact, not correctness of those columns. The documented correction remains C=0.9454521553596371. It cannot be independently recalculated here without the missing probabilities. Aggregate macro-F1 and log loss cannot reconstruct the per-transcript probabilities needed for paired losses and uncertainty.

Search was limited to the relevant repository and retained project temporary directories: `/private/tmp/phase3d-final.gwUEwX`, `/private/tmp/phase3d-commit.ufwZOJ`, `/private/tmp/phase3c-clone.I1cDS6`, `/private/tmp/phase3c-final.lnI0U0`, and Git history for the named OOF path. No unrelated user files were searched. The historical `.gitignore` excludes `results/tables/*`; the OOF file was not force-added. Its disappearance is an artifact-retention failure, not evidence of structure exposure. No baseline was refitted to replace it.

## Lock gate adjudication

| Required condition | Finding |
|---|---|
| Structure has never been compared with outcome/residuals | PASS on available execution and code evidence |
| D features defined without structure-outcome inspection | Candidate reservations PASS; exact D definition incomplete |
| Outcome fixed | PASS: preserve workflow_detection_v1 |
| Cohort fixed | PASS: preserve 15,999 IDs and hash |
| CV folds fixed | PASS: preserve recorded assignments and hash |
| A/B/C specifications fixed | Executed source fixed; registry discrepancy must remain visible |
| Model C predictions frozen unchanged | FAIL: required artifact absent; aggregate summaries are insufficient |
| Primary D-vs-C metric and statistical comparison fixed | NOT_MET: no single primary metric or executable paired comparison is locked |
| Missingness handling fixed | Conditional complete-case principle fixed; coverage-only comparator role unresolved |
| Success/failure interpretation fixed | NOT_MET: numerical practical-effect and four-way criteria absent |
| No unresolved result-driven optimization making comparison uninterpretable | No demonstrated score-optimized baseline choice; unresolved provenance does not alone prove invalidity |

The absent baseline prediction artifact is independently sufficient to block approval under the requirement to freeze Model C predictions without refitting. Completing missing statistical choices on paper would not cure that absence. Accordingly this review does not create a partial document labeled an approved lock or make otherwise unnecessary new analysis choices. **BLOCK_STRUCTURE_TEST** is a present readiness decision, not rejection of the biological hypothesis or a new design-rescue phase.

## Skeptical methods review

Development-set validity: a future paired, same-cohort, same-fold D-vs-C analysis can remain interpretable after baseline inspection if the structure-outcome relationship is still unseen, the actual baseline predictions are retained, and all D-specific choices are fixed before testing. Knowledge that C has macro-F1 0.522 is not itself a disqualifying exposure. The current missing artifact prevents verifying that exact comparison now. Weak annotation-only controls restrict any eventual claim to increment over the implemented minimal C; they cannot support a claim of controlling every established identifiability explanation.

Confirmatory strength: even after a valid lock, these are development-set results with already inspected outcome and baseline behavior, cross-study biology, selective structure availability and weak independent structure reproducibility. A cluster bootstrap describes transcript-group uncertainty conditional on the observed preparations; it is not independent biological replication. Permutations must have a defensible conditional null and cannot be asserted exact by merely shuffling correlated, unequal-size groups.

Publication implications: an honestly described development analysis may be publishable with a positive, negative or inconclusive increment. Independent validation is **REQUIRED for strong confirmatory/generalization claims**, not as a prerequisite to any useful development analysis. LongBench sequencing validation alone cannot validate a structure contribution without a compatible independent structure resource. Do not unlock it here.

If a lock is later actually established, manuscript wording must be exactly: "This is a pre-structure analysis lock established after inspection of structure-blind baseline performance. It is not a prospective preregistration." This sentence is a future reporting requirement, not a claim that this blocked review established a lock.

## Disposition and validation

No lock created. No scientific result, feature definition, endpoint, cohort, fold or fitted model changed. The old FROZEN_PHASE3D status is preserved as historical and explicitly not treated as a current structure-test authorization. Recovering the original OOF artifact and documenting its custody would permit reassessment; if it is irretrievable, this no-refit request cannot be completed by inventing or regenerating probabilities. Exact statistical and D-feature choices would still need completion before any approved lock.

Validation: `/opt/homebrew/bin/python3.11 -m unittest discover -s tests -p 'test_prestructure_integrity.py' -v` passed all four lightweight integrity tests. Repository validation and `git diff --check` passed. Checks verify unchanged artifact hashes, fold partition integrity, predictor lists and absence of a falsely approved lock document. A separate read-only comparison verified unchanged cohort ID membership since Phase 3C; the scoped file search established missing prediction status. No model-fitting test was run. The pushed documentation commit is reported in the terminal closeout. There is no lock commit or lock timestamp. Stop before Model D.
