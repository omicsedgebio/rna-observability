# Research question

Can transcript-intrinsic sequence and annotation features predict protocol-specific transcript measurement behavior, and do independent experimental in-vivo RNA accessibility measurements add reproducible information beyond abundance, sequence, architecture and identifiability?

The originally proposed “intrinsic molecular property” framing needs qualification: in-vivo reactivity also reflects proteins, modifications, environment and assay chemistry. This is an observational prediction study; neither a causal mechanism nor a universal biological property is its default estimand.

Scope: human bulk RNA, initially K562 for data feasibility, then compatible SG-NEx contexts. Technology means the combination of platform, library protocol, chemistry and quantifier. Separate protocol effects from platform effects wherever design permits; do not claim they can always be separated.

Candidate contribution: an independently evaluated incremental test of measured structure for reproducible transcript-level protocol disagreement, against strong sequence and identifiability baselines. Prior art already establishes many constituent ideas (see prior_art_matrix.tsv). Localized effects remain exploratory until region-level evidence is available.

Initial decision MODIFY (2026-09-22): K562 may support a cross-study feasibility analysis, not a matched causal experiment. LongBench alone does not yet supply a verified external test of cell-matched structure.

## Phase 3D scope decision (2026-09-23)

The development endpoint, if advanced, is workflow-specific: supported transcript detection under named SG-NEx Salmon 1.9.0 / Ensembl 91 Illumina and direct-RNA workflows. The same quantifier executable does not make the endpoint technology-intrinsic because the protocols, input evidence and Salmon options differ. The future structure question is therefore scoped as whether experimentally measured in-vivo RNA accessibility adds incremental information about this defined workflow phenotype after sequence, architecture, abundance and identifiability controls. RNA structure versus measurement behavior remains untested.
