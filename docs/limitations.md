# Limitations and risks

No original data analysis exists. Reconnaissance is incomplete at supplemental-method and full citation-census level.

- Novelty: experimental structure/sequence bias and transcript difficulty already studied. The complete test, not terminology or a new dashboard, must carry contribution.
- Biology: in-vivo probing measures accessibility with protein/modification effects; assay preparation can refold extracted RNA. Cross-study stocks/culture/passages may differ.
- Confounding: expression, length, GC, isoform number/similarity, read depth, batch, degradation, library selection, chemistry, quantifier, end effects and annotation. Perfectly confounded factors are not statistically separable.
- Selection: structure calls preferentially cover abundant/assignable regions; complete-case analysis targets a selected population. Report coverage-conditioned estimand and exclusions.
- Identifiability: a bounded K-value does not remove rank-deficient null directions; record rank and unique evidence. Sibling transcripts are dependent.
- Statistics: few biological libraries; uncertain endpoints; pseudocount sensitivity; compositional abundance; nested CV cannot fix leakage before splitting.
- Leakage: endpoint-derived abundance/variance, outcome-selected windows, whole-dataset imputation/feature selection, shared-exon/sequence leakage and nanopore-derived m6A.
- External validity: LongBench new kits and cancer contexts differ; no verified matched structure. Catalog gene data may be insufficient for transcript-level validation.
- Reproducibility: processed RDS objects may need legacy packages; reference release/object processing dates may differ; checksum/version audit needed. Offline checks do not validate biology or reproduce findings.
- Reuse: public accessibility is not unrestricted permission; do not relicense source data with project code.
