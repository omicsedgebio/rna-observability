# Phase 3C skeptical second pass

Role: Reviewer 2 for a manuscript submitted to a genomics methods journal. This review was performed after the structure-blind endpoint audit and before any structure hypothesis test. No LongBench outcomes were viewed.

## Criticisms

| Criticism | Classification | Evidence and consequence |
|---|---|---|
| The proposed primary detection phenotype is conditional on a quantifier whose ONT semantics are not independent of the target behavior | FATAL | Salmon versus NanoCount status agreement is 0.519 on a sparse complete subset; Salmon versus Bambu rank correlation is 0.668 and Bambu is CPM-like. A primary model could therefore learn Salmon-versus-annotation behavior rather than a platform property. Baseline modeling is prohibited until this is resolved or explicitly reframed as a Salmon-defined phenotype. |
| The supported-detection threshold is defensible as a candidate but not uniquely identified | MAJOR_BUT_MANAGEABLE | Thresholds 0.1, 1 and 5 TPM and 2/4, 3/4 and 4/4 support all produce materially different class counts. The selected 1 TPM rule was chosen from replicate behavior, but the ONT quantifier issue means it cannot yet be called algorithm independent. |
| Structure availability is strongly selected by abundance and other transcript features | MAJOR_BUT_MANAGEABLE | Only 15,999 of the covariate-complete universe are structure eligible; 71.1% of the availability model universe has fitted probability below 0.05 and naive inverse-probability weighting is unstable. The estimand must remain conditional on callable, measured transcripts. |
| Independent structure-summary reproducibility is weak | MAJOR_BUT_MANAGEABLE | The stricter structure-only comparison has 72 profiles from 68 genes, cross-study median nucleotide rho 0.321 versus within-study rho 0.679. Mean/median and categorical summaries are at most conditional future features. |
| Near-sequence leakage has not been evaluated | MAJOR_BUT_MANAGEABLE | Current folds group genes and exact cross-gene duplicate sequences, but no similarity grouping beyond exact sequence was completed. A model can otherwise place paralogous transcripts in separate folds. |
| Cross-platform comparisons use different biological preparations and laboratories | MAJOR_BUT_MANAGEABLE | SG-NEx Illumina and direct-RNA observations are not matched aliquots, and the structure experiments are from different preparations and laboratories. Results would describe protocol-specific behavior, not synchronized per-molecule error. |
| Spike-in truth does not validate endogenous transcript behavior | MAJOR_BUT_MANAGEABLE | Direct-RNA spike-in rank correlations are only moderate and NanoCount observes a small sparse subset. Mixture-level truth has no complete biological-replicate linkage for the endpoint. It is weak calibration, not proof of endogenous accuracy. |
| Transcript-end phenotypes cannot be computed from the available processed matrices | MINOR | This limits mechanism-specific interpretation but does not invalidate a future detection phenotype if the quantifier issue is resolved. |
| No evidence supports an accidental structure-outcome analysis or LongBench exposure | NOT_SUPPORTED | Blinding flags, scripts and the external lock document show structure-only and outcome-only analyses were kept separate; no prohibited result was inspected. |

## Falsification conclusion

The proposed primary endpoint is still capable of being an algorithm-defined Salmon phenotype, but it is not yet a defensible quantifier-robust platform phenotype. A reviewer could reasonably reject a manuscript that presents it as technology-specific measurement behavior without an explicit quantifier-aware scope. The issue is potentially manageable by obtaining a common-output representation with documented zero semantics, or by reframing the estimand and validation around a named workflow while treating all other workflows as sensitivity analyses. The current evidence does not justify freezing the plan or fitting Models A/B/C.

Reviewer 2 count: 1 FATAL issue for progression, 6 MAJOR_BUT_MANAGEABLE issues, 1 MINOR issue, and 1 NOT_SUPPORTED criticism.
