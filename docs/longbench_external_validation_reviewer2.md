# Fresh Reviewer 2: containment and repository-preparation review

Status: **REVIEW COMPLETE - LONGBENCH REMAINS LOCKED**

Date: 2026-09-25

This review used only repository-local pre-exposure evidence. It did not use web
search, open LongBench, recover or infer the quarantined content, or inspect any
validation outcome. "Reviewer 2" denotes a separate adversarial pass by the
executing agent, not an independent human reviewer.

## Finding counts

| Classification | Count |
|---|---:|
| FATAL | 0 |
| MAJOR_BUT_MANAGEABLE | 1 |
| MINOR | 2 |
| NOT_SUPPORTED | 12 |

## Findings

| # | Question | Classification | Finding and disposition |
|---:|---|---|---|
| 1 | Did the accidental exposure contaminate a committed or candidate artifact? | NOT_SUPPORTED | The prior session stopped without repository modification. All eight candidate bytes matched their independently supplied pre-exposure SHA256 values before new work began. |
| 2 | Do the eight hashes establish pre-exposure identity? | NOT_SUPPORTED | Yes. The exact paths and hashes are preserved in `metadata/longbench_exposure_incident_20260925.json`; every value matched at the containment gate. |
| 3 | Is the incident transparently documented without reproducing content? | NOT_SUPPORTED | Yes. The incident JSON, external lock, and README record only process facts and do not state the exposed scientific result. |
| 4 | Is LongBench still locked? | NOT_SUPPORTED | Yes. No access or scoring authorization exists, required compatibility fields remain unresolved, and the checker returns `LOCKED_RELEASE_CONDITIONS_UNMET`. |
| 5 | Was any attempt made to recover or infer the exposed content? | NOT_SUPPORTED | No. This review used only local pre-exposure governance and frozen development artifacts. |
| 6 | Is Model D still frozen? | NOT_SUPPORTED | Yes. The attempt remains consumed; no Model D fit, tuning, threshold, cohort, fold, metric, or decision-rule change occurred. |
| 7 | Is the deployment estimator distinct from OOF development evidence? | NOT_SUPPORTED | Yes. It is labeled post-development, fit once on the frozen full matrix, reports no performance metric, saves transparent state, and cannot alter the development conclusion. |
| 8 | Does the README accurately present the near-null increment? | NOT_SUPPORTED | Yes. Exact point, interval, permutation threshold, sensitivity, and `NOT_SUPPORTED / NEGLIGIBLE` conclusion are shown with the biological-irrelevance boundary. |
| 9 | Are the diagrams scientifically accurate? | NOT_SUPPORTED | Yes. They describe the fixed analysis and governance sequence and do not imply a mechanism, causal effect, or successful structure validation. |
| 10 | Are LongBench compatibility unknowns still honest? | NOT_SUPPORTED | Yes. No classification was upgraded using external information; nine required items remain `UNKNOWN`, and absent matched structure blocks aims A/B only. |
| 11 | Can prediction-before-scoring currently be bypassed? | MAJOR_BUT_MANAGEABLE | No execution path is authorized or implemented, so no current scoring bypass exists. A future implementation, exact mapping, validation environment, inclusion manifest, feature/label separation, and two human authorizations remain mandatory release blockers. |
| 12 | Did repository polish introduce an overclaim? | NOT_SUPPORTED | No. The project contribution is framed as a measurement framework and falsifiable test, not novelty, truth, clinical utility, or a validated score. |
| 13 | Can the prepared work be committed without weakening Git controls? | NOT_SUPPORTED | Yes. The primary checkout denies `.git/index.lock` creation, so a fresh isolated clone was used for byte-identical staged review and commits. No Git guard was bypassed. |
| 14 | Is final citation/license metadata complete? | MINOR | No. Authorship and project license remain intentionally pending, so creating `CITATION.cff` would invent release metadata. The blockers are visible. |
| 15 | Is historical provenance fully free of personal absolute paths? | MINOR | Four frozen receipt/audit lines retain an execution username/path. Editing them would break locked hashes and not erase Git history; they are flagged for final privacy review. |

## Deployment-estimator review

The deployment fit used the exact historical Python/package environment and the
frozen 15,999-row Model C matrix. Feature order, class order, scaler parameters,
coefficients, intercepts, iterations, hashes, and environment are recorded. A
manual NumPy reconstruction reproduces the canonical prediction fingerprint.
The attempt marker prevents a second fit. No performance metric, Model D result,
structure input, or LongBench input entered construction.

## Disposition

There is no unresolved scientific or containment FATAL issue. The external
validation program remains unreleased because compatibility, mapping,
environment, prediction-before-scoring implementation, inclusion, human review,
and authorization conditions are unmet. Repository changes were reviewed and
committed through an isolated writable clone because the primary checkout's Git
metadata is read-only in this environment.
