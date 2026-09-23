# Outcome selection without structure

Candidate endpoints were evaluated from measurement semantics and replicate behavior only. Cross-platform disagreement is not ground truth error. A defensible candidate is a protocol-specific signed log abundance contrast, for example the median across biological observations of `log2(a_t,dRNA + c) - log2(a_t,Illumina + c)`, where the abundance scale, offset, and aggregation are fixed in advance. Absolute contrast, detection disagreement, rank concordance, isoform fraction disagreement, dropout, splice-chain agreement, full-length recovery, end completeness, and replicate variance are secondary candidates.

The current SG-NEx object does not establish that `normEst` is a common molar scale across methods. Therefore no final primary endpoint is frozen in Phase 2. Before freezing, we must establish a common quantification scale or restrict comparisons to outputs with documented compatible semantics. Sensitivity to offset, zeros, normalization, quantifier, annotation, and aggregation must be reported. Spike in recovery will be analyzed separately as true measurement error only after known input concentrations and calibration metadata are linked.

Structure information was not used to choose the candidate endpoints, and no structure versus outcome association was computed.

## Phase 3A candidate-by-candidate decision, structure blind

| Candidate | Measurement-only evidence | Decision |
|---|---|---|
| Signed log abundance disagreement | Same Salmon family and fixed transcript index feasible, but 56.8% direct-RNA all-zero among independently expression-eligible transcripts; median shifts by >5 log2 units across prespecified offsets and by 0.432 after reclosure | Retain as a candidate for an explicitly detection-conditioned estimand; reject current form as frozen primary |
| Absolute log disagreement | Inherits offset, zero and quantifier sensitivity; erases direction | Secondary candidate only, not primary |
| Transcript detection disagreement / platform-specific dropout | Interpretable at stated per-library threshold; depth and effective-length handling differ | Secondary candidate, threshold and depth calibration unresolved |
| Percentile-rank disagreement | Avoids cross-platform scale but strongly abundance dependent and compositional | Secondary candidate; not accuracy |
| Isoform-fraction disagreement | Controls some gene-level composition; undefined at zero gene total and annotation sensitive | Secondary candidate with explicit denominator eligibility |
| Replicate-normalized disagreement | 2 Illumina outcome libraries and 4 direct-RNA preparations; within-protocol dispersion itself unstable at zero floor | Defer; denominator/variance estimation not reliable |
| Splice-chain agreement | Requires read alignments and assignment denominators absent from processed matrix | Exploratory only; not computed |
| Transcript, 5-prime and 3-prime completeness | Requires full-length aligned read evidence and end definitions absent from processed matrix | Exploratory only; not computed |
| Spike-in true relative error | Known synthetic within-mixture concentration ratios, but per-library mixture linkage and numeric truth are incomplete for some molecules | Defined separately; not evaluated |

Illumina RSEM and ONT NanoCount/Bambu sensitivity changes provisional contrasts substantially; NanoCount output is sparse and Bambu is a different abundance scale. No candidate was promoted because of any structural feature behavior. The decision is to leave the primary/secondary endpoint family **unfrozen** until transcript mapping, zero behavior and an independent covariate strategy are resolved.
