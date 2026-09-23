# Phase 3D skeptical final design review

This review was performed after the quantifier strategy audit and sequence-cluster construction, before any structure-outcome analysis. It does not inspect LongBench outcomes.

| Objection | Classification | Resolution or remaining limitation |
|---|---|---|
| The endpoint is a software artifact rather than a technology-intrinsic property | MAJOR_BUT_MANAGEABLE | The endpoint is explicitly narrowed to measurement behavior under named Salmon 1.9.0 / Ensembl 91 workflows. RSEM, NanoCount and Bambu are sensitivity workflows. The manuscript must not claim platform accuracy or technology-intrinsic reliability. |
| Another reasonable quantifier can change transcript labels | MAJOR_BUT_MANAGEABLE | Yes. The primary label is frozen as a workflow-specific Salmon label and quantifier disagreement is a required sensitivity report. This limitation remains material. |
| Technical runs could be mistaken for independent biological replication | MINOR | Outcome labels aggregate library support; runs are not independent observations. Biological preparations remain the inferential unit. |
| Selecting complete measured rows trivializes the task | MAJOR_BUT_MANAGEABLE | The estimand is conditional on class-A, structure-callable, complete-row transcripts. Attrition is published, no value threshold is used, and claims are not generalized to all transcripts. |
| Structure availability sharply narrows the target population | MAJOR_BUT_MANAGEABLE | Positivity is poor outside the callable measured population. Complete-case conditional inference and strata are frozen; unstable weighting is prohibited. |
| Sequence clustering does not prevent all biological relatedness leakage | MAJOR_BUT_MANAGEABLE | Same genes and BLASTN >=95% identity / >=90% coverage components are held together. Lower-identity homology and unannotated relationships remain limitations, not hidden exclusions. |
| The model may mostly learn prior-run abundance | MAJOR_BUT_MANAGEABLE | Abundance is an explicit baseline covariate, Model A is reported, and strata plus trivial baseline are required. Future structure increment must beat Model C on held-out clusters. |
| Structure summaries have weak independent reproducibility | MAJOR_BUT_MANAGEABLE | Mean, median and categorical summaries remain conditional future candidates. Unsupported local, end and junction features are excluded. A future Model D result cannot be called general if structure reproducibility remains weak. |
| Cross-platform samples are not matched aliquots | MAJOR_BUT_MANAGEABLE | The study describes cross-preparation workflow behavior, not per-molecule error or causal platform effects. |
| Synthetic spike-ins validate endogenous transcript truth | NOT_SUPPORTED | Spike-ins are reported as separate calibration only; no endogenous truth claim is made. |

## Falsification conclusion

No unresolved FATAL objection remains after the claim scope is narrowed to the named workflow. The design is scientifically usable for structure-blind baseline modeling, with several major limitations that must remain visible in the manuscript. A strong structure claim would still require a future held-out incremental result, reproducible structure features, and uncertainty that survives the conditional estimand and quantifier sensitivity analyses. A null or unstable Model D result would reject the central incremental claim without invalidating the workflow baseline.

Issue count: 0 FATAL, 7 MAJOR_BUT_MANAGEABLE, 1 MINOR, 1 NOT_SUPPORTED.
