# Identifiability baseline feasibility

The following annotation and sequence-derived variables are feasible in principle: transcript number per gene, exon sharing, unique junction count, transcript length, unique sequence length, pairwise transcript similarity, and effective unique regions. The annotation object supplies Ensembl 91 transcript, gene, exon count, length, and gene relationships. Exact GC and unique sequence calculations still require the matching Ensembl 91 transcript FASTA and exon definitions.

The miniQuant family motivates a compatibility or rank-deficiency baseline based on a transcript-to-observation compatibility matrix. A K-value or related singular-value summary may be implemented only after the published matrix construction, read model, and annotation assumptions are reproduced and tested against the original software where licensing permits. We will not label an independent reimplementation miniQuant-compatible without that verification.

The structure model must add information beyond this baseline. Isoform count, shared exons, unique junctions, effective unique length, and transcript similarity are mandatory covariates or comparators, not optional post hoc controls.
