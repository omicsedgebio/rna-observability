# Structure-blind baseline model results

Integrity qualification: these fits are exploratory relative to the recorded freeze chronology. The log-loss column below is invalid because of probability-column ordering; corrected values from saved predictions are A=0.971933, B=0.947665, C=0.945452. See [verification addendum](phase3d_integrity_verification.md). The endpoint, models, cohort, folds and predictions were not changed during verification.

These are the frozen Phase 3D Models A, B and C. They use the 15,999-transcript workflow-specific cohort, fixed five-fold gene and sequence-cluster folds, and no RNA structure value or LongBench outcome. The primary label has five classes: `BOTH`, `ILLUMINA_ONLY`, `DIRECT_RNA_ONLY`, `NEITHER`, and `INDETERMINATE`.

## Held-out performance

| Model | Features added | Accuracy | Balanced accuracy | Macro-F1 (95% cluster bootstrap interval) | Log loss | Multiclass Brier |
|---|---|---:|---:|---:|---:|---:|
| Majority | most common class | 0.293 | 0.200 | 0.091 | NA | NA |
| A | independent prior-run abundance, length, GC | 0.603 | 0.516 | 0.509 (0.499-0.519) | 3.645 | 0.531 |
| B | A plus exon count, isoform count, sequence-cluster size | 0.614 | 0.523 | 0.516 (0.506-0.525) | 3.625 | 0.517 |
| C | B plus homopolymer fraction, low-complexity fraction, sequence entropy | 0.615 | 0.527 | 0.522 (0.512-0.533) | 3.643 | 0.516 |

The small C over B improvement is structure-blind and is not evidence for an RNA-structure contribution. The large difference between the majority classifier and Models A-C shows that the workflow phenotype is not a trivial constant label, but performance is strongly abundance- and class-dependent.

## Prespecified strata

Model C accuracy and macro-F1 are reported in `results/tables/baseline_model_metrics.tsv` for abundance, transcript length and isoform-count strata. Accuracy is highest in the high-abundance stratum (0.721) and lowest in the middle abundance stratum (0.572). Macro-F1 ranges from 0.305 to 0.331 across abundance strata, showing that accuracy alone is misleading under class imbalance. Length and isoform strata show similar heterogeneity.

## Quantifier sensitivity

The alternative RSEM/Bambu descriptive label cross-tabulation is in `results/tables/baseline_strata_metrics.tsv`. It is not used to redefine the frozen primary endpoint. The quantifier audit remains a material limitation: the endpoint is a Salmon-defined workflow phenotype, not a technology-intrinsic property.

## Reproducibility

The implementation is `analysis/baseline_models/fit_structure_blind.py`. It uses fixed `C=1` multinomial logistic regression, training-fold standardization, seed `20260923`, and 100 sequence-cluster bootstrap replicates for macro-F1 intervals. The exact cohort and fold hashes are stored in `results/tables/baseline_model_summary.json` and the frozen plan. The publication-quality structure-blind figure is `results/figures/qc/phase3d_baseline_performance.svg`.

No Model D, structure residual analysis, structure feature importance, or LongBench outcome analysis was performed. The baseline results do not change the frozen primary phenotype or its workflow-specific claim scope.
