# Final grouped cross-validation design

## Purpose and blinding

The folds are defined before baseline model fitting using only the fixed cohort, Ensembl 91 transcript sequences, Ensembl 91 gene identity, and the pre-specified workflow detection labels used for balance checks. No RNA structure value, structure feature, LongBench outcome, model residual, or performance result was read.

## Sequence grouping

Eligible transcript sequences were extracted from the pinned Ensembl 91 cDNA and ncRNA FASTA resources. BLASTN 2.15.0 `megablast` self-search used `-perc_identity 95`, `-qcov_hsp_perc 90`, `-evalue 1e-20`, and an alignment-length requirement of at least 90 percent of the shorter transcript. Same-gene transcripts were unioned regardless of sequence similarity. Connected components form the sequence groups.

The primary leakage-prevention threshold is 95 percent nucleotide identity with 90 percent coverage. It is deliberately conservative for transcript prediction: paralogous and near-identical isoforms remain in one dependency group even when they are from different genes. A 99 percent identity and 90 percent coverage sensitivity grouping was also computed without using model performance. The threshold decision was made for leakage prevention and biological relatedness, not to improve a result.

| identity | coverage | transcripts | clusters | singleton clusters | largest cluster | multi-gene clusters | maximum genes in a cluster |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 99% | 90% | 15,999 | 4,881 | 2,430 | 38 | 131 | 11 |
| 95% | 90% | 15,999 | 4,314 | 1,858 | 43 | 314 | 34 |

The primary assignments are in `metadata/transcript_sequence_clusters.tsv`. The clustering code is `scripts/phase3d_sequence_clusters.py` and records method/version in this document and the Phase 3D report.

## Fold construction

All transcripts sharing a sequence cluster, and therefore all transcripts in a gene, are assigned to one fold. A deterministic greedy assignment balances transcript counts over five folds after shuffling cluster IDs with NumPy seed `20260923`. The assignments are in `metadata/cv_folds.tsv`, with status `FROZEN_PHASE3D`.

Fold sizes are 3,199, 3,199, 3,202, 3,199, and 3,200. The primary workflow detection categories remain represented in every fold; the largest category difference is small relative to the fold size. Technical runs are columns used to form one transcript label, never independent rows. No sequence cluster or gene appears in more than one fold.

The exact cohort SHA256 is `3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5`. The exact fold SHA256 is `66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52` at construction time; the freeze document records the final pre-baseline hashes if the manifest is regenerated.

## G9 decision

G9 is **PASS**. Deterministic assignments exist, gene and sequence-cluster leakage checks pass, fold sizes are adequate, and the five workflow-specific outcome states are represented in each fold. This design supports held-out structure-blind baseline evaluation. It does not imply that the endpoint is technology-intrinsic or that an unseen transcript is independent of all biological relatedness.
