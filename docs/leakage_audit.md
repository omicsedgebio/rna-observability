# Predictor and endpoint leakage audit

No model was fit in Phase 3A. This registry classifies candidate predictors before any structure hypothesis test. A value measured from the same endpoint libraries is not a valid predictor simply because it is available in the same table.

| Class | Examples | Baseline policy |
|---|---|---|
| PRE_MEASUREMENT_MOLECULAR | Independently measured expression from disjoint biological preparation, if its collection and protocol are fixed | Eligible only with documented independent library and no endpoint overlap |
| ANNOTATION | Ensembl 91 transcript length, gene/biotype, exon count, genomic span | Eligible after exact mapping |
| IDENTIFIABILITY | Isoform count, exon sharing, unique exon/junction sequence, incidence rank, original miniQuant K-value | Mandatory controls; computed only from fixed annotation/sequence |
| MEASUREMENT_DERIVED | Endpoint-library read depth, coverage, Salmon uncertainty, direct-RNA detection, same-library abundance | Excluded from A/B/C primary predictor set; may be outcome QC or explicitly separate sensitivity |
| OUTCOME_DERIVED | Signed/absolute disagreement, endpoint detection difference, outcome ranks, Model residuals | Always excluded |

Structure availability and callable coverage are missingness/QC variables, not substitutes for structure values. Future experimental reactivity features are reserved for Model D and prohibited from A/B/C. `predictor_guard` in `src/rnaobs/core.py` rejects unregistered, measurement/outcome-derived and structure/residual predictor names and rejects endpoint/covariate library overlap. A feature's provenance is additionally checked in the registry because renaming a leaked column cannot make it valid. Independent abundance uses only Illumina Rep3 if Rep4/5 define the outcome, leaving one covariate-source preparation; a robust abundance-conditioned primary analysis is not yet supportable.
