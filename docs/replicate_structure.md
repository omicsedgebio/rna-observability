# Replicate structure

The unit of observation is not a sequencing run by default. The working hierarchy is:

biological source, RNA preparation, library, sequencing run, technical replicate.

`metadata/replicate_hierarchy.tsv` preserves the SG-NEx identifiers and assigns a conservative observation level. Runs sharing a biological replicate or RNA preparation are not independent biological observations. K562 includes multiple ONT runs and protocol variants, including two differently loaded preparations under a replicate 2 label. Those rows must not be collapsed solely by a text replicate label.

The three K562 Illumina rows are separately labeled replicates, while K562 PacBio has one processed run in the inspected object. Several ONT groups have repeated runs within a biological replicate. Primary inference must use biological source or RNA preparation as the clustering unit, with run level retained for technical reproducibility. If a contrast has only one independent biological source, it is descriptive and cannot support a biological generalization.
