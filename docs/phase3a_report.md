# OmicsEdgeBio Project 001 - Phase 3A report

Date: 2026-09-23. Scientific implementation commit: `59e6cce`. This report documents a failed pretest progression gate, not a structure hypothesis result.

## PHASE 3A VERDICT

**MODIFY**. Exact references, SG-NEx abundance semantics, source-independent sequence/identifiability features and substantial measurement/availability QC are complete. The required mapping and missingness conditions for a valid primary structure comparison are not met. The analysis plan remains unfrozen and no baseline model was fit.

## EXECUTIVE SCIENTIFIC SUMMARY

The Ensembl 91 GRCh38 reference identity is resolved and internally consistent. SG-NEx `normEst` has quantifier-specific meanings; Salmon short- and long-read values recover TPM but use different mapping and effective-length models, so only a specified relative-abundance contrast is defensible. The 200,310 SG-NEx GTF transcripts yield 199,216 sequence-validated records and a broad annotation/sequence baseline. However, icSHAPE's source transcript GTF/FASTA is not pinned. Exact ID plus length is not enough to verify exons or sequence, leaving **zero** A/B matched transcripts. Moreover, provisional structure availability is strongly selected by abundance and GC and lacks overlap for unrestricted weighting; the candidate continuous endpoint is strongly zero/pseudocount dependent. Those blockers prevent a freeze or A/B/C modeling without weakening the manuscript standard. The central structure hypothesis remains unseen.

## INTERRUPTION RECOVERY

At resume, branch `main`, HEAD and `origin/main` were `e83efc6`, with only untracked Phase 3A work. Every untracked Phase 3A script/source/metadata file, ignored cache/output inventory, command log and existing report/lock document was inspected. The completed reference downloads, Ensembl/SG-NEx sequence reconstruction, canonical 31-mer counts, original miniQuant K-values, RDS extraction, abundance semantics audit, endpoint-only QC and spike-in metadata were reused. No expensive reference or k-mer operation was restarted. The adjusted missingness GLM alone was partial: it had failed rank/convergence checks and had generated no usable adjusted result. A standardized ridge logistic availability-only diagnostic replaced it and completed. Integrity checks found no truncated/corrupt acquired file. Code and output audits found no reactivity-versus-outcome result and no LongBench outcome access. The acquisition guard rejected one generic literature URL query containing the word LongBench before network transfer.

## REFERENCE RESOLUTION

All reference URLs, UTC retrieval dates and reuse notes are in `metadata/reference_resources.tsv`. Assembly is GRCh38, Ensembl release 91; the SG-NEx mirror GTF adds synthetic references and `chr` prefixes. The Ensembl GTF supplies transcript-to-gene mapping, biotype, chromosome, strand and exact exons. The genomic FASTA, transcript cDNA/ncRNA FASTA and SG-NEx transcript mirror agree for 199,216 sequence-available GTF transcripts.

| Resource | Bytes | SHA256 |
|---|---:|---|
| Ensembl 91 GTF | 41,862,461 | `1abe442ea2ba90c022545be71c4e7b95b66d45c8c9e4e4ec3788b6be440b598d` |
| Ensembl 91 cDNA | 65,088,589 | `a7f0022e884826d70e0a151f6c38547aea8d443eaa9653aaf56e698e23109201` |
| Ensembl 91 ncRNA | 9,365,901 | `0ab3565714f88fb98eb7df7814fe3fed770e2b098d37cd7b83601258f87e75dd` |
| Ensembl 91 primary genome | 881,214,396 | `745f93e65defa8a4c5e9e99be9d87cce4c767ab6ff8f8683f8fb1c4ecbd3e836` |
| SG-NEx transcriptome mirror | 383,778,406 | `ceeaaeb8fe0fe3a3472e736c7283903d6fc34166c9fc89ed832b2584c344ec2c` |
| SG-NEx augmented GTF | 264,174,466 | `c6fd87310bd3b1dcb271bb535b1ce872cb41bea1638493f65918653455c2162a` |
| SG-NEx augmented transcriptome | 309,643,020 | `6acae821e99faefb9b8654da7694e3174f32fb82a9a3affd41ea2c45bc4842ba` |

No newer annotation was substituted. `metadata/phase3a_integrity_audit.json` records successful byte/SHA256 verification of all seven references.

## TRANSCRIPT VALIDATION

The target-side check compared versioned/stable ID, gene ID, chromosome, strand, exon count and every exon coordinate, reported and reconstructed lengths, and genomic/FASTA/mirror sequences. All 200,310 Ensembl GTF transcript exons agree with the SG-NEx augmented GTF. There are 1,094 GTF transcripts lacking a matching Ensembl transcript FASTA; 199,216 are exactly reconstructed, with zero sequence mismatches. The 1,094 SG-NEx processed IDs lacking a version were recovered unambiguously from the Ensembl 91 GTF and marked.

| Mapping class | Count | Interpretation |
|---|---:|---|
| A | 0 | Exact ID and equivalent full transcript definition |
| B | 0 | Stable ID and defensibly equivalent full definition |
| C | 59 | Reported transcript length changed |
| D | 65,956 | Source icSHAPE exon/sequence definition unavailable or ambiguous |
| E | 134,295 | No stable-ID match |

Total: 200,310. Another 3,401 icSHAPE records have no SG-NEx GTF match. The 65,956 D records include exact-ID/equal-length provisional candidates, never primary eligible. Final eligible A/B universe: **0**. Full local derived rows: `results/tables/transcript_mapping_validated.tsv` (ignored because large); reproducible summary: `results/tables/reference_mapping_summary.json`. A source icSHAPE annotation and transcript FASTA are required for promotion.

## ABUNDANCE SEMANTICS

Pinned SG-NEx code computes `normEst = estimates / ntotal * 1e6`. Salmon, RSEM and NanoCount processing first rescale source TPM into `estimates = TPM * ntotal / 1e6`, so `normEst` recovers quantifier TPM. Bambu uses assay counts as `estimates`; its `normEst` is CPM-like. Salmon ONT mode and short-read mode differ in mapping, bias and effective-length handling. `metadata/quantification_workflows.tsv` classifies every workflow, input, annotation, multimapping and zero semantics. No selected cross-technology value is directly comparable as molecule count or truth. The Salmon pair is **COMPARABLE_AFTER_SPECIFIED_TRANSFORMATION** for relative composition; RSEM/NanoCount sensitivity is rank/detection oriented; Bambu CPM versus Salmon TPM is not a defensible continuous abundance contrast.

## PRIMARY PLATFORM COMPARISON

Candidate pair: K562 Illumina short reads versus ONT direct RNA, both SG-NEx Salmon Ensembl 91 outputs, with TPM reclosed to a fixed common transcript index per library. This minimizes quantifier-family differences but not protocol-specific Salmon settings, cross-study preparation differences, or nonidentical effective-length treatment. Original TPM and fixed-universe closure, alternative quantifiers, and ONT cDNA would be explicit sensitivities. The selected platform comparison is **not frozen** because no A/B mapped structure cohort or stable primary endpoint exists.

## REPLICATE UNIT

Independent biological RNA preparation/library is the observation unit; multiple sequencing runs within a verified preparation are technical replicates and would be depth-aggregated before protocol medians. Provisional endpoint QC used Illumina Rep4/5 and four ONT direct-RNA preparations (replicates 1, 4, 5, 6). Illumina Rep3 was held apart as an abundance covariate source. Similar replicate numbers across laboratories do not prove paired aliquots. One independent abundance-source Illumina library does not meet the previous two-library eligibility goal. Transcript-level rows are not biological replicates.

## SPIKE-IN GROUND TRUTH

The checksummed 3,494-byte SG-NEx truth RDS supplies IDs and concentrations for Sequin, SIRV, long SIRV and ERCC mixes; 161/164 Sequin A v1.0 molecules have numeric concentrations. Sample metadata identifies Sequin A v1.0 in K562 Illumina Rep3-5 and ONT direct-RNA Rep4-5. Processed spike-in outputs combine reads by mix/protocol rather than preserving every K562 biological preparation. A within-mixture true **relative** error endpoint is defined in `docs/spikein_ground_truth.md` but not evaluated; mixture/unit and processed-run linkage need final verification. No endogenous disagreement is called measurement error.

## STRUCTURE MISSINGNESS

Only IDs, length and callable masks/counts were read, never reactivity. With provisional exact ID/equal length, at least 50 callable bases and callable fraction at least 0.5, 35,309 of 199,216 sequence-validated reference transcripts (17.72%) are usable as a QC proxy. Fixed availability thresholds 0.25/0.5/0.75 yield 48,048/35,309/20,941 profiles. In the 198,569-transcript adjusted universe, availability rises from 6.49% at zero Illumina TPM to 89.09% above 100 TPM and varies with length, GC, isoform architecture and detectability. A standardized ridge logistic model is descriptive after the unpenalized GLM failed convergence. Some 47.37% have fitted probability below 0.05. Naive inverse-probability weights reach 12,608 and effective sample size about 193, so unrestricted IPW is rejected. A future conditional complete-case/high-overlap stratum or matched availability design would change the estimand and requires a new prespecified freeze. Current missingness is too severe for population-wide structure inference. QC figures are `results/figures/qc/structure_missingness_strata.svg` and `structure_missingness_overlap.svg`.

## IDENTIFIABILITY BASELINE

`src/rnaobs/core.py` computes annotation-only isoform count, exon/junction sharing, unique exonic bases, maximum same-gene exonic Jaccard, identical splice chains and binary incidence rank deficiency. `src/exact_kmers.cpp` computes exact canonical transcript-specific 31-mer fraction. The pinned original miniQuant gene K-value code was run with 235-nt fragment length and effective-length entries. Full upstream build failed due unavailable static ggcat libraries; a minimal driver compiled original K-value source units without changing their algorithm. Gene K-values exist for 191,286 sequence-feature transcripts; no approximation is labeled miniQuant. Its PolyForm Noncommercial license is recorded. Annotation-only controls remain mandatory for a future structure increment.

## SEQUENCE FEATURES

Generated for 199,216 validated transcripts: length, GC fraction, homopolymer burden, low-complexity fraction, mononucleotide entropy, canonical 31-mer uniqueness, transcript-specific 31-mer fraction, plus architecture/identifiability controls. Only 46 low-complexity and 35 k-mer fractions are missing for insufficient valid sequence; miniQuant K-value is missing for 7,930 transcript rows. Cross-gene exact sequence duplicates include 398 hashes and 970 transcripts. `metadata/feature_definitions.tsv` records exact algorithms, versions, parameters, reference, missingness and rationale. Repeat content was not generated because an authoritative mask release was not pinned. No feature was selected based on outcome association.

## PRIMARY ENDPOINT

**NOT FROZEN.** The candidate signed contrast is `median_dRNA log2(a_t+0.1) - median_Illumina log2(a_t+0.1)` where `a_t` is Salmon TPM reclosed over a fixed common transcript universe. This is signed platform disagreement in log2 relative abundance, not error. Measurement-only QC on 49,309 transcripts independently eligible by Illumina Rep3 TPM >=1 found median -3.83 at offset 0.1. Changing the fixed offset from 0.01 to 1 moved the median from -6.90 to -1.40; 56.8% were zero in all direct-RNA libraries. The formula cannot be frozen without a zero-aware estimand and suitable independent abundance conditioning.

## SECONDARY ENDPOINTS

**NOT FROZEN.** Candidates are absolute signed contrast; detection-fraction difference at >0 and >=1 TPM; percentile rank difference; within-gene isoform-fraction difference when gene denominator is positive; and within-protocol replicate dispersion. Splice-chain, whole-transcript, 5-prime and 3-prime completeness remain exploratory because processed transcript totals lack aligned-read evidence. The spike-in true-relative-error candidate is separate. All candidates and retention/defer reasons are in `docs/outcome_selection.md`.

## LEAKAGE AUDIT

The registry classifies pre-measurement sequence, annotation, identifiability, measurement-derived and outcome-derived variables. Endpoint-library abundance, read depth, detection, uncertainty and coverage are excluded from primary predictors; disagreement, its ranks and residuals are outcome-derived. Independent abundance may only use a disjoint documented preparation. Structure availability may diagnose selection but cannot substitute for a reactivity value. The `predictor_guard` enforces provenance classes and library separation on future A/B/C code. `docs/leakage_audit.md` lists safeguards.

## CROSS-VALIDATION

Proposed, not executable/frozen: connected components of genes plus cross-gene exact and near-identical transcript sequences, followed by outcome-blind five-fold grouped CV with three seeds and four inner grouped folds. Exact duplicates already cross gene boundaries; gene-only CV is insufficient. The cross-gene near-similarity graph and actual folds must be built and audited before freeze. Preparation uncertainty must be separate from gene-cluster bootstrap uncertainty. No CV performance was calculated.

## STRUCTURE EXTERNAL VALIDATION

No STRONG independent resource combining validated experimental structure with independent matched Illumina and ONT direct-RNA transcript abundance was found. GSE149767 K562/HepG2 profiles are MODERATE for independent structure-feature reproducibility but WEAK for the incremental structure effect. H9 PORE-cupine GSE133361 is a MODERATE candidate for deeper audit, but its ONT structure signal and ONT measurement may share reads. GSE74353, GSE155961, GSE45803, ENCODE and NAP-seq contexts are WEAK or unsuitable for the increment as presently documented. The alternative validation program separately tests sequencing behavior, structure-feature reproducibility and ultimately the incremental structure contribution; the first two cannot stand in for the third.

## LONGBENCH LOCK

Preserved. Only Phase 1/2 compatibility and license metadata plus the lock document were read. No LongBench file, S3 listing, transcript-level result, outcome distribution, disagreement value, benchmark figure, model result or association was accessed. A URL guard blocked an accidental generic search string before transfer. No plan is frozen, so the lock cannot be released.

## LICENSING

Academic manuscript analysis with attribution remains feasible under source-specific terms. SG-NEx repository terms are CC BY-NC 4.0; miniQuant source is PolyForm Noncommercial 1.0.0. GSE145805 GEO access does not establish blanket redistribution/commercial rights. Ensembl-produced reference data have broad reuse terms, subject to third-party caveats; ENCODE is a potential permissive future resource. LongBench catalog metadata indicates CC BY 4.0, still locked and component review remains. Future commercial product reuse is a separate unresolved rights track; no legal advice or clearance is given. No source dataset or licensed code was committed.

## ANALYSIS FREEZE

**Frozen: NO.** File: `docs/frozen_analysis_plan.md`, status `DRAFT_NOT_FROZEN`. Freeze timestamp and freeze commit SHA: **NOT_APPLICABLE**. Scientific implementation commit at report drafting: `59e6cce`. Missing required decisions include A/B transcript eligibility, a robust endpoint/zero rule, high-overlap missingness estimand, independent abundance source and similarity-group folds. A report or implementation commit does not imply a freeze. The future plan must be completed and committed before baseline fitting or the first structure association, and cannot be changed merely because a future Model D is unattractive.

## BASELINE MODEL RESULTS

Model A: **NOT_RUN**. Model B: **NOT_RUN**. Model C: **NOT_RUN**. The conditional Task 17 gate failed. No held-out performance, calibration or residuals exist. There is no Model D. `docs/baseline_model_results.md` and `analysis/baseline_models/README.md` document this decision; no publication figure claims baseline predictive performance. Availability-only QC figures contain no structure-value result.

## CENTRAL HYPOTHESIS STATUS

RNA structure versus transcript measurement behavior has not yet been tested.

## PUBLICATION OUTLOOK

**WEAK** for the present design, based on feasibility rather than journal target. An Ensembl-side reproducible baseline and a same-cell-line external structure reference are promising, but no validated matched transcript cohort, robust frozen endpoint, manageable population selection adjustment or strong independent increment-validation dataset currently exists. The project is salvageable only if those blockers are resolved; no positive structure result is implied.

## MAJOR SCIENTIFIC RISKS

The largest risks are source transcript model mismatch, abundance-dependent structure selection and positivity failure, zero-dominated endpoint instability, cross-study culture/preparation effects, quantifier/effective-length differences, too few independent abundance covariate libraries, cross-gene sequence leakage and lack of independent structure-increment replication. These are not removed by larger transcript counts or standard cross-validation.

## FILES CREATED OR MODIFIED

Scientific code: `scripts/phase3a_acquire.py`, `phase3a_extract.R`, `phase3a_references.py`, `phase3a_feature_audit.py`, `phase3a_outcome_qc.py`, `phase3a_missingness.py`, `run_miniquant_kvalue.py`, `src/rnaobs/core.py`, `src/exact_kmers.cpp`, `tests/test_phase3a.py`. Metadata: `reference_resources.tsv`, `phase3a_source_provenance.tsv`, `phase3a_integrity_audit.json`, software sessions, `quantification_workflows.tsv`, `feature_definitions.tsv`, `spikein_truth_summary.tsv`. Documentation: the new reference, mapping, abundance, comparison, spike-in, identifiability, leakage, cross-validation and baseline notes, and updated outcome, missingness, feature, licensing, external-search, claims, freeze, reproducibility, decision, command and LongBench lock records. Lightweight summary JSON/TSV and two SVG availability figures are tracked. Full derived matrices remain ignored. The exact tracked file list is in `git show --stat 59e6cce`; this report is a separate final commit.

## DATA DOWNLOADED

Seven Ensembl/SG-NEx references total 1,955,127,239 bytes with individual sizes and SHA256 above. A further 73 small code/methods/metadata sources total 5,127,992 bytes; exact URLs, sizes and SHA256 are in `metadata/phase3a_source_provenance.tsv`. This includes SG-NEx spike-in truth RDS, 3,494 bytes, SHA256 `5375f835de896b21345e9f8154ef67adfb8c6ab1ddf71691a205c0dbb6414fa6`, and pinned miniQuant source archive, 2,963,535 bytes, SHA256 `6b2e2de5eaeb66bf48d4a4bacb463c7ff484f3efb281cecf93f8d52639ef829b`. The Phase 2 SG-NEx processed RDS and icSHAPE supplement were reused, not downloaded again. No FASTQ, BAM or CRAM was acquired. All downloads remain in ignored caches; all 80 manifest entries passed SHA256 and size verification.

## TEST RESULTS

Project Python 3.12.14: 17 unit tests passed, covering mapping/version/sequence/exon failures, minus-strand extraction, canonical k-mer uniqueness, annotation identifiability, aggregation, endpoint math, provisional availability, grouped splitting, predictor leakage and provenance. Repository validator passed. `git diff --check` passed after normalizing generated SVG/R-session whitespace. All staged files were below 1 MB (maximum 38,218 bytes); no reference, large matrix, raw read file, credential-like string or generated binary was staged. QC SVGs were visually inspected. The attempted unpenalized missingness GLM failure and safe ridge alternative are documented.

## GIT COMMITS

Starting HEAD/origin: `e83efc6`. Scientific implementation and QC commit: `59e6cce` (`Resolve Phase 3A references, measurement semantics, and pretest gates`). This report is committed separately; its self-referential final SHA is given in the terminal handoff and repository log.

## PRIVATE REMOTE PUSH STATUS

The configured `omicsedgebio/rna-observability` remote was confirmed private with `gh repo view`. The two Phase 3A commits are pushed to that existing private remote and verified in the final terminal handoff. Repository visibility was not changed; no release, DOI, manuscript submission or public deployment occurred.

## WORKING TREE STATUS

The final terminal handoff verifies the clean `main` working tree and equality of HEAD and `origin/main` after this report commit and push. Large caches and full derived matrices remain intentionally ignored.

## EXACT NEXT PHASE

Conduct a Phase 3B **pretest blocker rescue**, not an RNA structure test. First obtain the exact GSE145805/PrismNet source transcript GTF and FASTA or a defensible transcript reconstruction; recalculate A/B mapping eligibility and attrition. If that source cannot be established, identify a different independently measured structure assay with fully verifiable transcript definitions. Next define a zero-aware detection/hurdle or restricted continuous endpoint using only measurement properties, secure an independent abundance covariate strategy, set a high-overlap conditional missingness estimand without unstable full-population IPW, and build the gene/paralog/sequence-similarity grouping graph. Re-audit independent structure validation and spike-in mixture linkage. Only after these pass should a precise plan be frozen and committed, then structure-blind A/B/C models fit on its held-out folds. The first structure-versus-outcome test remains a later phase and LongBench remains locked until its own release criteria are satisfied.
