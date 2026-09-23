# Phase 3C interim handoff

Status: deterministic work complete; final endpoint review pending. This handoff deliberately does not freeze the analysis plan, declare GO_TO_BASELINES, fit Models A/B/C, inspect structure versus sequencing behavior, or access LongBench outcomes.

The final scientific review is recorded in `docs/phase3c_report.md`; the resulting verdict is MODIFY.

## Work completed

- Rebuilt the Ensembl 88 to 91 bridge from the pinned GSE132099 structure inventory, Ensembl 88/91 GTFs and transcript FASTA files. The exact class counts are A=16,268, B=0, C=17, D=5 and E=5; 16,055 class-A profiles meet the 50-callable-base and 0.5-callable-fraction rule.
- Defined the metadata-only cohort attrition audit. The current complete-row Salmon intersection is 15,999 transcripts. The row-availability rule does not treat sparse NanoCount rows as zeros.
- Completed the SG-NEx K562 quantifier audit. Illumina Salmon/RSEM and direct-RNA Salmon/NanoCount/Bambu run inventories, rank concordance, threshold behavior and stratified diagnostics are recorded in `results/tables/quantifier_concordance.tsv` and `docs/quantifier_endpoint_audit.md`.
- Calibrated candidate measurement summaries against SG-NEx synthetic spike-in truth without extrapolating that truth to endogenous RNA.
- Documented transcript-end endpoint infeasibility from transcript-total processed matrices and identified the required alignment/coverage resources.
- Audited alternative K562 sequencing resources from public metadata only.
- Completed a structure-to-structure reproducibility diagnosis using GSE132099 and GSE149767 only. No sequencing abundance, disagreement, residual or LongBench outcome was read.
- Constructed reproducible but explicitly provisional five-fold assignments over the 15,999 candidate rows. Groups combine genes and exact cross-gene reference sequence duplicates; near-sequence grouping is not yet assessed.

## Data and resources acquired or reused

Existing ignored caches were reused: SG-NEx transcript, metadata and spike-in RDS objects; Ensembl 91 GTF/cDNA/ncRNA; Ensembl 88 GTF/cDNA/ncRNA; GSE132099 processed in-vivo structure; and GSE149767 processed in-vivo profiles and sequence maps. No FASTQ, BAM or CRAM was downloaded. Checksums and URLs remain in the existing metadata manifests; the corrected SGNEX metadata SHA256 ends in `...1048b24b5`.

## Quantifier findings

Within-method median replicate Spearman correlations were 0.811 (Illumina Salmon), 0.801 (Illumina RSEM), 0.677 (direct-RNA Salmon), 0.837 (direct-RNA NanoCount on represented rows) and 0.712 (direct-RNA Bambu). Same-run cross-method median rank correlations were 0.797 for Illumina Salmon/RSEM, 0.497 for direct-RNA Salmon/NanoCount, 0.668 for Salmon/Bambu and 0.476 for NanoCount/Bambu. Bambu `normEst` is CPM-like and was not given TPM cutoffs. NanoCount is sparse; absent rows are missing rather than zero.

## Endpoint candidates and remaining ambiguity

The leading detection candidate is a four-category supported state using 1 TPM, 2/2 Illumina support and 3/4 direct-RNA support, with intermediate support indeterminate. The measurement-only counts are BOTH=11,731, ILLUMINA_ONLY=20,201, DIRECT_RNA_ONLY=315, NEITHER=3,687 and INDETERMINATE=13,375 in the independently expressed universe. A percentile-rank difference among positive, supported transcripts is the leading quantitative secondary. The offset-based signed log endpoint remains rejected as a primary because of zero sensitivity. Final selection is **PENDING_FINAL_REVIEW** because Salmon/RSEM status agreement is 0.861 while direct-RNA Salmon/NanoCount agreement is 0.519 on a sparse common subset, and no quantifier-independent ONT zero semantics have been established.

## Proposed cohort and folds

The proposed maximum is the 15,999-transcript intersection of class-A mapping, structure coverage eligibility and complete SG-NEx Salmon rows across three Illumina and four direct-RNA K562 runs. This is a conditional candidate, not a frozen analytic population. `metadata/cv_folds.tsv` contains five balanced, deterministic, gene-grouped assignments and is marked `PROVISIONAL_NOT_FROZEN`. Exact duplicate sequence groups across genes are collapsed; near-sequence leakage remains a required final-review item.

## Structure reproducibility findings

Among 10,896 GSE149767 in-vivo profiles, 10,878 had a unique map, 353 matched a class-A Ensembl 91 sequence, and 72 profiles from 68 genes passed the joint callable-position rule. Median cross-study nucleotide Spearman correlation was 0.321 versus 0.679 for the two GSE149767 replicate columns. Median cross-study upper- and lower-quartile overlap was 0.126 and 0.100. This is a negative or weak reproducibility diagnostic, not a structure-sequencing test, and no structure summary has been selected for a future model from this result.

## Tests completed

`python -m unittest discover -s tests -p 'test_*.py'` passed all 27 tests. New tests cover bridge counts, cohort attrition, provisional fold manifest, spike-in missing-row semantics and structure/LongBench blinding flags.

## Files modified or created

New deterministic scripts: `scripts/phase3c_restore.py`, `phase3c_cohort_reference.py`, `phase3c_cohort_attrition.py`, `phase3c_quantifier_audit.py`, `phase3c_spikein_calibration.py`, `phase3c_structure_repro_diagnosis.py`, and `phase3c_candidate_folds.py`. New tests, cohort/fold metadata, QC tables and the Phase 3C endpoint, cohort, K562-resource, transcript-end, spike-in and structure-diagnosis documentation were added. Claims, novelty, manuscript, missingness and structure-estimand records were updated with the interim status. No large scientific cache is tracked.

## Decisions requiring final review

1. Select or reject the supported-detection primary phenotype after reviewing common-output and quantifier sensitivity, without using structure.
2. Decide whether a quantitative secondary remains interpretable as a rank phenotype and define its missingness rules.
3. Assess whether near-sequence grouping is required before folds can be frozen.
4. Decide whether the weak cross-study structure reproducibility permits any prespecified structure summary to advance.
5. Only after those decisions, freeze `docs/frozen_analysis_plan.md`, assess GO_TO_BASELINES, and fit structure-blind Models A/B/C if permitted.

The interim commit SHA is reported in the terminal handoff. The source checkout cannot update its Git index in this environment because `.git/index.lock` creation is denied; the commit was pushed from a clean temporary clone of the same private remote.

The central RNA-structure hypothesis remains blinded. LongBench remains locked.
