# Phase 3D final scientific review

Subsequent adjudication: the historical GO_TO_BASELINES remains recorded, but a pre-structure analysis lock has not been approved. [Decision chronology](prestructure_decision_chronology.md) records BLOCK_STRUCTURE_TEST because the original per-transcript baseline predictions are unavailable and the exact D comparison remains incompletely specified. Prior baseline inspection alone is not a disqualification.

Integrity closeout: [verification addendum](phase3d_integrity_verification.md) supersedes the pre-baseline freeze chronology and log-loss claims below. Baseline results were inspected before the recorded freeze; the later rerun does not restore prospective status. The historical verdict is retained, but full freeze compliance is not certified. No central structure or LongBench outcome exposure was found.

## PHASE 3D VERDICT

**GO_TO_BASELINES**

G3 and G9 are resolved, but G3 passes only as `PASS_WORKFLOW_SPECIFIC`. The endpoint and all claims are narrowed to measurement behavior under named Salmon 1.9.0 / Ensembl 91 workflows. No technology-intrinsic accuracy or endogenous true-error claim is permitted.

## G3 QUANTIFIER RESOLUTION

| Strategy | Result | Evidence |
|---|---|---|
| A. Common quantifier | `PASS_WORKFLOW_SPECIFIC`; `FAIL` for technology-oriented use | Salmon 1.9.0 is available for both protocols with Ensembl 91, but direct-RNA `--ont` suppresses length correction and input evidence differs. Same software does not create a common molar scale. |
| B. Consensus detection | `FAIL` | NanoCount is sparse and its 3-of-4 common-row agreement with Salmon is 0.475 with kappa 0.000. Bambu is CPM-like on an augmented annotation. |
| C. Direct sequencing evidence | `FAIL` | Current processed matrices lack validated alignment-derived full-length, splice-chain, 5-prime or 3-prime measures. No raw alignment data were downloaded. |

The complete transcript audit is `results/tables/phase3d_quantifier_agreement.tsv`, with compact summary in `results/tables/phase3d_quantifier_agreement_summary.tsv` and interpretation in `docs/phase3d_quantifier_problem.md`.

## FINAL PRIMARY PHENOTYPE

`workflow_detection_v1` is a five-state supported-detection label. Illumina support is Salmon TPM >=1 in both `GIS_K562_Illumina_Rep4-Run1` and `GIS_k562_Illumina_Rep5-Run1`. Direct-RNA support is Salmon TPM >=1 in at least three of four SG-NEx direct-RNA outcome libraries. The label is `BOTH`, `ILLUMINA_ONLY`, `DIRECT_RNA_ONLY`, or `NEITHER` when both platform states are determinate; intermediate support is `INDETERMINATE`. No pseudocount is used and fitted zeros are not biological absence.

Secondary phenotypes are common-positive within-workflow percentile-rank difference, replicate reproducibility, quantifier sensitivity, and synthetic spike-in calibration. Transcript-end and splice-chain measures remain exploratory and unavailable from the current processed matrices. Phenotypes are not combined into one score.

## CLAIM SCOPE

**Workflow-specific.** The scientific wording is measurement behavior under a defined sequencing and quantification workflow. It is not technology-intrinsic reliability, platform accuracy, endogenous measurement error, or a universal RNA observability score. This scope is propagated to `docs/research_question.md`, `docs/claims_register.md`, `docs/manuscript_plan.md`, and the frozen plan.

## FINAL COHORT

N = **15,999** stable Ensembl transcript IDs. Eligibility is outcomes-blind: validated class-A Ensembl 88 to 91 sequence/exon bridge, Ensembl 91 annotation and gene grouping, complete rows in three Illumina and four direct-RNA Salmon runs, and GSE132099 structure-callability of at least 50 positions and 0.5 fraction for the future conditional estimand. The attrition table is `results/tables/phase3d_cohort_attrition.tsv`.

Counts are: SG-NEx annotation 200,310 -> class A 16,268 -> complete primary Salmon rows 16,205 -> structure eligible 16,055 -> final cohort 15,999. No structure value, disagreement magnitude or model performance entered selection.

## SEQUENCE CLUSTERING

Ensembl 91 cDNA and ncRNA sequences were clustered with BLASTN 2.15.0 megablast, at least 95% identity and 90% coverage of the shorter sequence. Same-gene transcripts were always grouped. The primary 95% threshold produced 4,314 clusters, 1,858 singleton clusters, largest cluster 43, and 314 multi-gene clusters with a maximum of 34 genes. The 99% / 90% sensitivity grouping produced 4,881 clusters and largest cluster 38. Assignments are in `metadata/transcript_sequence_clusters.tsv`; details are in `docs/final_cv_design.md`.

## FINAL CV FOLDS

Five deterministic folds were generated with NumPy seed `20260923` by greedy balancing of sequence-cluster sizes. Fold sizes are 3,199, 3,199, 3,202, 3,199 and 3,200. All same-gene and same-primary-sequence-cluster transcripts remain together. No sequence cluster or gene crosses folds. Every fold contains all five workflow states. Technical runs are columns used for one transcript label, not independent observations. `metadata/cv_folds.tsv` is frozen.

## G9 VERDICT

**PASS.** Gene leakage, primary sequence-cluster leakage, nondeterminism and inadequate fold size were not detected. Lower-identity homology and unannotated relationships remain limitations and are disclosed.

## FINAL GATE TABLE

| Gate | Verdict | Basis |
|---|---|---|
| G1 validated cohort | PASS | 15,999 outcomes-blind class-A, annotation-complete rows |
| G2 replicate unit | PASS | biological preparations define inference; runs are not pseudoreplicates |
| G3 measurement phenotype | PASS_WORKFLOW_SPECIFIC | named Salmon workflow endpoint; technology-oriented interpretation rejected |
| G4 zero handling | PASS | no pseudocount; indeterminate support retained |
| G5 spike-in validation | CONDITIONAL_PASS | synthetic calibration supports sensitivity checks only |
| G6 structure estimand | PASS | conditional measured and callable transcript target |
| G7 structure missingness | CONDITIONAL_PASS | complete-case conditional inference; poor broad positivity disclosed |
| G8 future structure feature | CONDITIONAL_PASS | mean/median and categorical summaries defined but weakly reproducible |
| G9 leakage-resistant folds | PASS | gene and >=95% identity / >=90% coverage sequence groups fixed |
| G10 structure hypothesis unseen | PASS | no structure-outcome or residual analysis |
| G11 LongBench locked | PASS | no transcript outcomes or performance viewed |

## REVIEWER 2

The final skeptical review is `docs/phase3d_reviewer2.md`: 0 FATAL, 7 MAJOR_BUT_MANAGEABLE, 1 MINOR and 1 NOT_SUPPORTED issue. The major issues are workflow-specific quantifier dependence, selected measured-transcript estimand, limited structure reproducibility, cross-preparation design, and abundance-dominated prediction. The narrowed claim scope and mandatory sensitivity reporting make them manageable for baseline progression.

## ANALYSIS FREEZE

**YES.** `docs/frozen_analysis_plan.md` records the timestamp, endpoint version, reference versions, cohort and fold hashes, outcome rules, features, reserved structure features, estimand, missingness strategy, models, metrics, uncertainty and success/failure criteria. The plan explicitly states: “RNA structure versus sequencing measurement behavior has not been inspected.”

## BASELINE MODELS

Models A, B and C were fitted after the freeze using exactly the frozen cohort and folds. No structure variable was included.

| Model | Accuracy | Balanced accuracy | Macro-F1 (95% cluster bootstrap) | Log loss |
|---|---:|---:|---:|---:|
| Majority | 0.293 | 0.200 | 0.091 | NA |
| A: abundance, length, GC | 0.603 | 0.516 | 0.509 (0.499-0.519) | 3.645 |
| B: A + architecture and identifiability | 0.614 | 0.523 | 0.516 (0.506-0.525) | 3.625 |
| C: B + sequence features | 0.615 | 0.527 | 0.522 (0.512-0.533) | 3.643 |

The C over B change is small. Performance varies materially by abundance and class balance: Model C accuracy is 0.721 in the high-abundance stratum, while macro-F1 remains about 0.305. The baseline is therefore informative but not evidence of a structure increment. Full metrics and the structure-blind figure are in `docs/baseline_model_results.md` and `results/figures/qc/phase3d_baseline_performance.svg`.

## BASELINE SANITY CHECK

The phenotype is not a constant-label problem because all models exceed the majority baseline. However, abundance strongly influences accuracy, macro-F1 is much lower than accuracy, and C adds little beyond B. These are prespecified limitations. They do not alter the frozen endpoint or model specification.

## CENTRAL HYPOTHESIS BLINDING

RNA structure versus sequencing behavior has NOT been tested: **YES**. No icSHAPE score was correlated with the endpoint or residuals, no structure feature entered a model, and no Model D was fit.

## LONGBENCH LOCK

**YES.** The external lock remains in force. No LongBench transcript outcome, performance result, or candidate association was viewed.

## PUBLICATION OUTLOOK

**PLAUSIBLE.** A moderate computational genomics paper is feasible if it stays workflow-specific and reports quantifier dependence, conditional structure missingness, weak independent structure reproducibility, and held-out uncertainty. A strong structure claim is not supported yet. Future Model D would need a prespecified structure feature with acceptable quality, held-out improvement beyond Model C on identical sequence-safe folds, cluster-level uncertainty, and null/permutation control. A stable null would be informative; an unstable or absent increment would reject the central incremental claim within this estimand.

## MAJOR RISKS

- Salmon is a named workflow component, so endpoint labels may include algorithm and annotation effects.
- Structure-callable transcripts are selected by abundance and sequence properties; inference is conditional, not population-wide.
- Cross-platform libraries are from different preparations and laboratories.
- Independent structure-summary reproducibility is weak and limits future feature interpretation.
- Baseline performance is abundance-dependent and class imbalance affects accuracy.

## FILES CREATED OR MODIFIED

Phase 3D added the quantifier audit and resolution documentation, BLASTN sequence-cluster and final-fold scripts/manifests, workflow-specific frozen plan, reviewer report, final report, baseline model code/results/figure, final attrition table, scope updates, governance state, and Phase 3D tests. Large source caches and raw sequencing files remain ignored.

## TEST RESULTS

`python3.11 -m unittest discover -s tests -p 'test_*.py'`: 34 tests passed. `scripts/validate_repository.py`: passed repository schema, policy, link and file-hygiene checks. The baseline script recorded `structure_inputs_read=false` and `longbench_inputs_read=false` in its summary and output tables.

## EXACT NEXT PHASE

After independent review of this frozen, structure-blind state, the next phase may define and run one prespecified Model D comparison on the identical cohort and folds. It must first recheck structure-feature quality and the conditional estimand, then add only the reserved structure features, use held-out incremental metrics and cluster-level uncertainty, and execute null/permutation controls fixed in advance. Do not unlock LongBench or broaden claims. Model D was not run in Phase 3D.

## FINAL COMMIT SHA

Substantive Phase 3D design and baseline commit: `5b98bfd`. A documentation closeout commit records the final repository state after this report was updated.

## PRIVATE PUSH STATUS

The substantive Phase 3D commit was pushed to the existing private `origin/main`; the documentation closeout is pushed with it.

## WORKING TREE STATUS

The source checkout cannot update its Git index because `.git/index.lock` creation is denied by the managed environment. The committed temporary clone is clean; the source files mirror the pushed commit and local scientific caches remain ignored.
