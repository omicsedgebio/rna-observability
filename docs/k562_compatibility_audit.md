# K562 compatibility audit

SG-NEx K562 is a multi-protocol sequencing resource with explicitly labeled RNA preparations, libraries, runs, and technical replicates. The icSHAPE source is an independent in vivo chemical probing experiment. The shared cell-line name is not a matched biological sample.

| Dimension | Assessment | Concern |
|---|---|---|
| Cell line identity and source | UNKNOWN to MODERATE | A shared K562 label does not prove identical provenance or passage history. |
| Treatment and culture | UNKNOWN | Exact media, density, treatment, timing, and harvest must be reconciled from source methods. |
| RNA extraction and state | HIGH | icSHAPE chemical probing and SG-NEx sequencing use different preparation and enrichment workflows. |
| Replicate generation | HIGH | Replicates are from separate studies and are not paired molecules or cultures. |
| Laboratory and batch | HIGH | Independent laboratories and library workflows are confounded with dataset. |
| Genome and annotation | LOW after mapping | Both resources are associated with human reference assemblies, but transcript versions still differ. |

Classification: **B, cell-context reference structure**, not A matched biological measurement. It can support a conditional feasibility analysis with explicit batch and missingness limitations. It is not sufficient to claim that structure was measured in the same culture used for SG-NEx sequencing.
