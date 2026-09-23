# Quantifier and pipeline sensitivity

The processed object contains multiple reasonable workflows, including Illumina RSEM and Salmon, and long-read NanoCount, Bambu, and Salmon outputs. Quantifier and protocol are explicit columns. K562 group summaries show materially different zero fractions and transcript coverage among workflows, even for the same broad technology. This means an apparent contrast can reflect quantifier behavior, annotation, or normalization rather than a physical platform effect.

Phase 2 therefore treats quantifier as a design factor and requires within-workflow sensitivity analyses before a cross-platform claim. The first comparison should be a common annotation and compatible abundance scale, followed by workflow-stratified contrasts. A result that changes sign or magnitude across reasonable workflows is not a stable molecular measurement phenotype. No raw re-quantification was performed.
