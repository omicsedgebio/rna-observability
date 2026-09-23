# Outcome selection without structure

Candidate endpoints were evaluated from measurement semantics and replicate behavior only. Cross-platform disagreement is not ground truth error. A defensible candidate is a protocol-specific signed log abundance contrast, for example the median across biological observations of `log2(a_t,dRNA + c) - log2(a_t,Illumina + c)`, where the abundance scale, offset, and aggregation are fixed in advance. Absolute contrast, detection disagreement, rank concordance, isoform fraction disagreement, dropout, splice-chain agreement, full-length recovery, end completeness, and replicate variance are secondary candidates.

The current SG-NEx object does not establish that `normEst` is a common molar scale across methods. Therefore no final primary endpoint is frozen in Phase 2. Before freezing, we must establish a common quantification scale or restrict comparisons to outputs with documented compatible semantics. Sensitivity to offset, zeros, normalization, quantifier, annotation, and aggregation must be reported. Spike in recovery will be analyzed separately as true measurement error only after known input concentrations and calibration metadata are linked.

Structure information was not used to choose the candidate endpoints, and no structure versus outcome association was computed.
