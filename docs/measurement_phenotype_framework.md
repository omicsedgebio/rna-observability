# Measurement phenotype framework

The Phase 3C design keeps distinct failure mechanisms separate:

1. **Detection reliability:** replicate-supported detection state under a specified TPM-like workflow. Intermediate support is indeterminate.
2. **Quantitative abundance agreement:** within-transcript percentile difference between direct-RNA and Illumina among transcripts positive under prespecified support rules. A log ratio is exploratory and defined only for strictly positive values; no pseudocount is used.
3. **Replicate reproducibility:** within-platform rank and detection agreement across independent preparations.
4. **Transcript completeness:** 5-prime completeness, 3-prime completeness, and full-length recovery only if strand-aware processed coverage or alignments can be obtained.
5. **Isoform ambiguity:** gene isoform count, exon sharing, unique sequence and related annotation-only controls. These are not replaced by structure measurements.

Each phenotype is audited against quantifier, replicate, abundance, length, isoform-complexity and annotation sensitivity. They are not combined into one score. The current evidence supports a detection candidate and a percentile-rank secondary, but ONT quantifier sensitivity prevents a final primary selection during the reserve-model handoff.
