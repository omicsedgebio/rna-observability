# Phase 3D quantifier problem and resolution

## Scope and blinding

This audit uses the SG-NEx K562 processed quantification object, the fixed 15,999-transcript cohort, and Ensembl 91 annotation. It does not read icSHAPE values, structure summaries, LongBench outcomes, or any structure-derived feature. Technical runs remain nested within the biological preparation records; they are not treated as independent observations.

The candidate primary state is computed from Salmon TPM-like `normEst` values. Illumina outcome libraries are `GIS_K562_Illumina_Rep4-Run1` and `GIS_k562_Illumina_Rep5-Run1`. Direct-RNA outcome libraries are `SGNex_K562_directRNA_replicate1_run1`, `replicate4_run1`, `replicate5_run1`, and `replicate6_run1`. The independent Illumina `Rep3-Run1` library is reserved as a covariate for future baseline models.

## Workflow comparison

| Workflow | Annotation/input | Zero and scale semantics | Measurement-only evidence | Interpretation |
|---|---|---|---|---|
| Illumina Salmon 1.9.0 | Ensembl 91 transcriptome, paired short-read FASTQ | TPM over the fixed transcript index; fitted zero is not biological absence | Complete three-run matrix; within-workflow median replicate Spearman rho 0.811 | Candidate Illumina component |
| Illumina RSEM | Ensembl 91 transcriptome, short-read alignment | TPM with RSEM length and assignment model | Within-workflow median rho 0.801; Salmon/RSEM 2-of-2 TPM-1 status kappa 0.608, concordance 0.808 | Sensitivity workflow, not a common scale |
| Direct-RNA Salmon 1.9.0 | Ensembl 91 transcriptome, transcriptome-aligned BAM, `--ont` | TPM-like output; ONT mode suppresses Salmon length correction; fitted zero is not biological absence | Four-run matrix; within-workflow median rho 0.677 | Candidate direct-RNA component under a named workflow |
| Direct-RNA NanoCount | Ensembl 91 transcriptome, aligned BAM | Sparse emitted rows; absent row is missing, not zero | Common four-run rows n=8,846; Salmon/NanoCount 3-of-4 status concordance 0.475, kappa 0.000; represented-row bias | Cannot define a cohort-wide consensus |
| Direct-RNA Bambu | Augmented Ensembl 91 GTF, genome-aligned BAM | CPM-like counts; no TPM effective-length semantics | Salmon/Bambu 3-of-4 positive-support concordance 0.861, kappa 0.687, but shared zeros and distinct annotation make this non-equivalence | Detection sensitivity only |

The transcript-level agreement table is `results/tables/phase3d_quantifier_agreement.tsv`; the compact evidence is `results/tables/phase3d_quantifier_agreement_summary.tsv`. NanoCount is not treated as a zero-filled matrix. Bambu is not assigned TPM thresholds. Agreement changes with transcript length and isoform complexity, so a quantifier-independent ONT state is not supported.

## Strategy A: common quantifier

**Result: PASS_WORKFLOW_SPECIFIC; FAIL as a technology-oriented endpoint.**

Salmon 1.9.0 is available for both Illumina and direct RNA with Ensembl 91 reference identities. The outputs are comparable only after a specified transformation to fixed-index TPM-like values and after preserving protocol-specific options. Illumina uses short-read bias and effective-length correction. Direct RNA uses transcriptome-aligned long-read evidence with Salmon `--ont`, which suppresses length correction and uses a different assignment-error profile. The same executable therefore does not establish a common molar measurement scale. The defensible estimand is supported detection under these two named Salmon workflows, not platform-intrinsic accuracy or endogenous true error.

Frozen workflow labels are:

- `illumina_salmon_1.9.0_ensembl91_tpm`: TPM >= 1 in both outcome Illumina libraries.
- `directrna_salmon_1.9.0_ont_ensembl91_tpm`: TPM >= 1 in at least three of four outcome direct-RNA libraries.

The independent Illumina Rep3 Salmon library is used only as a pre-outcome abundance covariate. Intermediate replicate support is indeterminate, not zero.

## Strategy B: consensus detection

**Result: FAIL.**

A consensus requiring Salmon, NanoCount and Bambu is not defensible because NanoCount is sparse and Bambu uses a CPM-like quantity on an augmented annotation. Relaxing the consensus to Salmon plus Bambu retains a method-dependent shared-zero component and does not resolve the direct-RNA algorithm disagreement. The observed Salmon/NanoCount kappa of zero on the complete sparse subset is incompatible with a robust majority call. Replicate support is useful within each named workflow, but it does not turn incompatible quantifier semantics into a common endpoint.

## Strategy C: direct sequencing-evidence phenotype

**Result: FAIL for this dataset state.**

The available processed matrices contain transcript totals, not validated alignment-derived full-length, splice-chain, 5-prime, or 3-prime evidence. Constructing such a phenotype would require raw or alignment-level reprocessing beyond the bounded data policy. No raw FASTQ, BAM, or CRAM was downloaded. Strategy C therefore cannot replace the named Salmon endpoint in this phase.

## G3 decision

G3 passes only as `PASS_WORKFLOW_SPECIFIC`. All manuscript and analysis language must say **measurement behavior under a defined sequencing and quantification workflow**. The study must not call the endpoint a technology-intrinsic property, a platform accuracy measure, or endogenous measurement error. RSEM, NanoCount, and Bambu remain prespecified sensitivity or descriptive workflows and cannot redefine the primary endpoint after results are seen.

## Primary and secondary phenotype boundaries

The primary phenotype is the five-state workflow-supported detection label: `BOTH`, `ILLUMINA_ONLY`, `DIRECT_RNA_ONLY`, `NEITHER`, or `INDETERMINATE`. Quantitative rank differences among transcripts positive under both named Salmon workflows are secondary. Within-workflow replicate reproducibility, quantifier sensitivity, and synthetic spike-in calibration are reported separately. No composite observability score is used.
