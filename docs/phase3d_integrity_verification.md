# Phase 3D closeout integrity verification

This is an integrity audit of already completed work, not another design phase. No model was fitted, no endpoint/cohort/fold/model definition was changed, and no structure-versus-sequencing or LongBench outcome analysis was performed during verification.

## Recovered commits and checkout

The substantive pushed commit is `5b98bfd49195585bc866ad8894f86adfc14a80c7`. The recovered closeout commit is `99ddb849c1e9b4d32d5aa30be423a120088c3201`, verified against `origin/main` with `git ls-remote`. The GitHub repository was verified private through `gh repo view`.

The active checkout remains at Phase 3C commit `09d12633f4587aa60e8cd34e7e58b9657a437a9a` because its Git index is protected. Its scientific/source files matched every tracked file in the pushed closeout commit byte-for-byte before this audit addendum. The existing temporary clone at `/private/tmp/phase3d-final.gwUEwX` was clean at the recovered closeout commit. Do not describe the active checkout as clean or synchronized at the Git-reference level.

## Checks that passed

- The full lightweight suite passed 34 tests using the project Python 3.11 environment. ResourceWarnings about unclosed test readers are nonfatal.
- Repository validation and `git diff --check` passed. These checks do not establish scientific validity or pre-result freeze chronology.
- No tracked file exceeded 1,000,000 bytes, and no raw FASTQ/FQ/BAM/CRAM, RDS, DuckDB, cache, or dependency-environment file was tracked. Pattern scanning found no GitHub-token, AWS-access-key, or private-key matches. This is a bounded scan, not a guarantee against all secret formats.
- The cohort has 15,999 unique transcript IDs. The cohort SHA256 is `3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5`; the fold SHA256 is `66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52`. Both match the plan and baseline summary.
- The five fold counts are 3,199, 3,199, 3,202, 3,199 and 3,200. Joining cached gene membership to the frozen manifest found zero split genes and zero split sequence clusters. All 9,595 accepted cached 95% identity / 90% coverage similarity edges remain within folds. This verifies the accepted graph, not exhaustive homology detection beyond the clustering method.
- G9 PASS is supported for that documented grouping. G3 PASS is explicitly workflow-specific; the evidence does not support technology-intrinsic detection or a common molar scale. The named endpoint remains unchanged.
- The A/B/C predictor lists and actual input-reading paths contain only SG-NEx sequencing quantities, reference sequence, annotation and cohort/fold metadata. No structure reactivity, structure residual, Model D or LongBench outcome input was found. Existing records and the observed commands show no central-hypothesis or LongBench exposure; this is a procedural audit, not an operating-system access trace.

## Material integrity exceptions

### Freeze chronology

The earlier execution record shows baseline fitting, saved predictions and inspection of A/B/C metrics before `docs/frozen_analysis_plan.md` was written with timestamp `2026-09-23T15:30:16Z`. A later rerun used that plan, but rerunning cannot restore prospective status. The substantive commit also contains both the plan and baseline results; there is no separate committed pre-result freeze. Therefore statements that all baseline fitting occurred only after the freeze are incorrect. The plan is a recorded specification with matching artifact hashes, but it is not a valid prospective pre-baseline freeze. The existing baseline results must be treated as exploratory with respect to that chronology. The central structure hypothesis remains unseen.

The plan also leaves future structure-feature selection, permutation details and multiplicity choices unresolved. This audit does not fill them in or authorize Model D. The recorded GO_TO_BASELINES verdict is retained as the prior decision, not recertified as completion of all original freeze requirements.

### Probability metric ordering

The baseline `metrics()` function supplies probability columns in the order BOTH, ILLUMINA_ONLY, DIRECT_RNA_ONLY, NEITHER, INDETERMINATE to sklearn `log_loss`, which interprets classes lexicographically. The emitted warning was consequential. Reported log losses 3.645, 3.625 and 3.643 are invalid.

Without refitting, the saved out-of-fold predictions give mean negative log probability of the actual class of 0.9719333478197004 (A), 0.9476654174737653 (B), and 0.9454521553596371 (C). These checks use the explicit probability-column mapping. Existing result tables are retained as historical artifacts; their log-loss fields are superseded by this correction. Accuracy is independently reproduced, including Model C 0.6152259516219764. Its recorded macro-F1 is 0.5218300679510073, with recorded cluster-bootstrap interval 0.512376260340985 to 0.5328101838801408. This audit does not rerun that bootstrap.

### Other reporting and reproduction limits

- The reviewer table contains eight MAJOR_BUT_MANAGEABLE entries, not the stated seven.
- The quantifier audit labels `sequencing_outcomes_read=false` despite reading sequencing quantities and computing detection labels. The valid blinding claim is that no structure-versus-sequencing association was inspected. That flag alone is not evidence of blinding.
- The baseline script does not generate the committed MAJORITY row itself; that row was added by a separate calculation. It therefore does not reproduce the complete metrics file unaided.
- The baseline implementation removes non-ACGT characters before window/run calculations, while the feature registry defines valid windows in the original sequence. The definitions differ for sequences containing ambiguous bases. No feature values or models were changed during this audit.
- The code uses only exon count, isoform count and sequence-cluster size beyond Model A for its frozen minimal Model B. Richer previously documented identifiability controls were omitted. No claim that this is the strongest earlier proposed identifiability baseline is warranted.

## Disposition

No additional rescue phase or scientific redesign is initiated. The historical verdict remains GO_TO_BASELINES with the above integrity exceptions explicitly attached. Baselines exist and the central hypothesis is still blinded, but prospective-freeze compliance cannot be certified. Stop before Model D and LongBench evaluation. Any later review must see this addendum alongside the report rather than relying on the original clean-freeze wording.
