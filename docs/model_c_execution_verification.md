# Model C unattended execution verification

Disposition: **READY_FOR_PRESTRUCTURE_LOCK_SPEC**. Classification: **PRESTRUCTURE_BASELINE_REESTABLISHMENT**. This is a pre-structure baseline re-establishment after prior baseline inspection, not exact historical reconstruction or prospective preregistration. Readiness is for a separate lock-specification review only; **BLOCK_STRUCTURE_TEST** remains in force.

Exactly one fitting attempt was launched through `.automation/run_model_c_once.sh` at 2026-09-24T07:00:08Z. The first fold started; all five folds completed. Wrapper exit status: 0. The immutable launch guard and internal attempt marker remain retained. No rerun, model repair, parameter/seed/predictor/fold/preprocessing change or performance-guided selection occurred.

## Resource and extraction verification

All four resources match their registered size and SHA256. SGNEX_TX was already complete and was not downloaded again. Only the two authorized Ensembl resources were restored.

| Resource | Bytes | SHA256 |
|---|---:|---|
| SGNEX_TX | 669521420 | `51d41a85766e536fc995965d820facc3e2e02bb99391330b9df4a46ff9a3a7d2` |
| SGNEX_META | 27131354 | `d37b4e2bf289ea46b59c2cd47c23c036f0708b1c31a5c235687dbfd1048b24b5` |
| ensembl91_cdna | 65088589 | `a7f0022e884826d70e0a151f6c38547aea8d443eaa9653aaf56e698e23109201` |
| ensembl91_ncrna | 9365901 | `0ab3565714f88fb98eb7df7814fe3fed770e2b098d37cd7b83601258f87e75dd` |

Only the unchanged `scripts/model_c_extract.R` was used for extraction. Exit 0; the data.table build-version warning and R session information are preserved.

| Extraction | Rows | Bytes | SHA256 |
|---|---:|---:|---|
| sgnex_annotation_full.tsv | 200310 | 40031956 | `5ac1122d0e751b235d416ee7457e2711108935a55f417accf23e33fe7c7661fa` |
| k562_quantification.tsv | 7900002 | 859220112 | `f00b1002e1b5c5e3109df112fbeb6c9799fafb795ee2d1cd546a42c90878289a` |
| model_c_R_session.txt | n/a | 1476 | `75ce2d04e4d59795db6f660710413759e129795bfafc89e4191725f69dda0d63` |

## Frozen inputs and saved artifacts

All four specified frozen hashes match. Every protected script/configuration matches pre-fit commit `162ee8f4195bf2141cd8c086c131acf2c65dda9b`. Preflight passed 15,999 ordered transcripts, exactly nine frozen finite predictors, unchanged historical label counts, zero duplicate measurement keys, 4,314 indivisible sequence groups and zero genes spanning folds. All five outputs and both guards were absent immediately before the sole launch.

The saved OOF was reopened: exactly 15,999 rows, exact ordered transcript membership, folds and sequence groups, weight 1, valid classes, five finite probabilities in [0,1], sums within 1e-12 of one and predictions matching maximum probability with lexicographic tie handling. The saved input matrix was independently rebuilt and all nine feature values and support-derived labels matched exactly. All manifest hashes were rechecked.

| Artifact | Bytes | SHA256 |
|---|---:|---|
| results/tables/model_c_oof.tsv.gz | 996601 | `aa3798858f17194b2acebdcb7e9411e1cb724fa7beff3441b585116c0fef5225` |
| results/tables/model_c_inputs.tsv.gz | 885816 | `c7597fcf57d955a84dcd512d4e4689be6127a408b76aed992d176af8e3a41a31` |
| results/tables/model_c_reestablishment_metrics.json | 12185 | `ee3e23119338cd411f44c4b4e7d22a252fdee35fdb3ae2d445b2a76b83c6921c` |
| metadata/model_c_reestablishment_manifest.json | 6019 | `5d11686ed71166d1351c03473166fcbc55d2974b9a98e0e568231f6ec6951647` |

## Recomputed saved-OOF metrics

All metrics below were computed from saved OOF rows, then checked independently with sklearn/numpy. Overall and per-fold differences between scoring implementations are below 1e-12.

| Metric | Value |
|---|---:|
| macro_f1 | 0.5218300679510073 |
| log_loss | 0.9454521553596428 |
| accuracy | 0.6152259516219764 |
| balanced_accuracy | 0.5274919726380182 |
| brier_multiclass | 0.5157598074560121 |

100-draw sequence-cluster bootstrap macro-F1 95% interval: **[0.512376260340985, 0.5328101838801408]**. Seed 20260923; 4,314 groups; historical group ordering. Independently recomputed with the historical bootstrap function. This is conditional on the fitted OOF predictions/libraries, not biological-replicate uncertainty.

| Class | N | F1 |
|---|---:|---:|
| BOTH | 4240 | 0.7383007171508448 |
| ILLUMINA_ONLY | 4680 | 0.665011421193763 |
| DIRECT_RNA_ONLY | 449 | 0.1733102253032929 |
| NEITHER | 2883 | 0.6926303175554224 |
| INDETERMINATE | 3747 | 0.33989765855171344 |

Confusion matrix: rows observed, columns predicted.

| Observed | BOTH | ILLUMINA_ONLY | DIRECT_RNA_ONLY | NEITHER | INDETERMINATE |
|---|---:|---:|---:|---:|---:|
| BOTH | 3037 | 769 | 3 | 20 | 411 |
| ILLUMINA_ONLY | 456 | 3348 | 2 | 179 | 695 |
| DIRECT_RNA_ONLY | 19 | 8 | 50 | 250 | 122 |
| NEITHER | 4 | 159 | 30 | 2312 | 378 |
| INDETERMINATE | 471 | 1105 | 43 | 1032 | 1096 |

| Fold | N | Macro-F1 | Corrected log loss | Accuracy | Balanced accuracy | Multiclass Brier |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 3199 | 0.513375425702682 | 0.9476304638790369 | 0.6080025007814942 | 0.5200714943752951 | 0.5198934543763728 |
| 1 | 3199 | 0.5433929837885888 | 0.9533133737973875 | 0.6223819943732416 | 0.5456857820685185 | 0.5161679829352861 |
| 2 | 3202 | 0.5135659228446484 | 0.955280599130669 | 0.6043098063710182 | 0.5229746236284739 | 0.5247809176684192 |
| 3 | 3199 | 0.5200122983825872 | 0.9225478368406762 | 0.6245701781806815 | 0.5271854722041363 | 0.5021681118772681 |
| 4 | 3200 | 0.5190189505917806 | 0.9484783401256959 | 0.616875 | 0.5232282568085723 | 0.5157801041434642 |

Full per-fold class F1 and confusion matrices are retained in [the metrics JSON](../results/tables/model_c_reestablishment_metrics.json).

## Historical descriptive comparison

| Metric | Re-established minus historical | Absolute tolerance | Pass |
|---|---:|---:|---|
| macro_f1 | 0.0 | 1e-6 | True |
| log_loss | 5.662137425588298e-15 | 1e-6 | True |
| accuracy | 0.0 | 1e-6 | True |

All three comparisons pass. Historical comparisons are descriptive only; agreement does not establish original prediction identity. No retry was performed or permitted for metric disagreement.

## Reviewer 2 disposition and limits

The [completed Reviewer 2 integrity review](model_c_reestablishment_reviewer2.md) found no fatal inconsistency in the saved-artifact verification. The review was performed by the executing agent with separate metric calculations, not an independent human reviewer or second agent.

Weak performance is retained: DIRECT_RNA_ONLY F1 is 0.1733102253032929 (449 observed rows; 50 true positives); INDETERMINATE F1 is 0.33989765855171344. These are workflow-specific supported-detection labels, not endogenous measurement truth or platform accuracy. Historical environment uncertainty, limited annotation-only identifiability controls, the preserved sequence ambiguity-handling discrepancy, and conditional bootstrap/generalization limits remain unresolved. Mac execution completed; Linux canonical reproduction has not been performed.

RNA structure remains blinded; no structure resource was restored or accessed. LongBench remains locked and was not accessed. No Model D work was performed. Blinding evidence is the reviewed execution/input allowlist, not an OS-wide access audit; sandbox restrictions prevented process enumeration.

Git commit and push were intentionally deferred until human review. No push, pull, fetch, gh, clean clone, Git write or remote modification was performed. Read-only local Git and remote-ref checks were used. This deferral is not a scientific blocker.

OOF and input files are ignored by the existing Git policy and remain on disk with hashes in the manifest and verification receipt. No ignore rules or scientific outputs were changed for Git handling. Durably retained execution logs, guards and ignored caches must remain available for the later human-reviewed commit/retention workflow.

Primary receipts: [saved-artifact verification](../metadata/model_c_saved_artifact_verification.json), [fit manifest](../metadata/model_c_reestablishment_manifest.json), [reconstruction audit](model_c_reconstruction_audit.md), and [durable run log](../results/logs/model_c_reestablishment_run.log).
