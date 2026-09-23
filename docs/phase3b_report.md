# OmicsEdgeBio Project 001 - Phase 3B report

Date: 2026-09-23. Scientific implementation commit: `a797439`. Status: pre-hypothesis design rescue. The analysis plan remains `DRAFT_NOT_FROZEN`.

## PHASE 3B VERDICT

**MODIFY.** The Ensembl 88 resource resolves a real transcript-definition bridge to SG-NEx, but the candidate ONT detection phenotype remains quantifier sensitive and independent transcript-level structure-summary reproducibility is not established. The selected structure set is highly nonrepresentative of all transcripts. The phase does not meet a defensible GO_TO_FREEZE standard. No baseline or structure-versus-sequencing model was fitted.

## WHY PHASE 3A FAILED

For the original GSE145805 K562 file, 65,956 SG-NEx transcript records had exact versioned ID and reported length agreement but no pinned source exon/FASTA definition. They properly remained D. Fifty-nine stable-ID candidates had reported length mismatch and 134,295 had no stable-ID overlap. Confirmed version-only, exon, sequence, build or identifier-semantics mismatch counts cannot be estimated from that source, and are recorded as zero **confirmed**, not zero occurring. The Phase 3A offset-based signed log-abundance candidate was dominated by ONT zeros: 56.8% all-zero ONT among independently expressed transcripts and a >5 log2-unit median shift across tested offsets. `docs/mapping_failure_root_cause.md` and `results/tables/mapping_failure_categories.tsv` give the audit.

## GSE132099

[GEO GSE132099](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132099) has K562 in-vivo icSHAPE with three treated biological replicates and controls; [processing metadata](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM3842467) pins Bowtie2 mapping to Ensembl 88 GRCh38. The pooled processed file has 16,295 unversioned transcript IDs, reported length, assay RPKM and per-position enrichment scores, with `NULL` uncalled. It has 20,354,101 reported positions and 19,188,788 numeric positions. Scores include values outside 0-1 and must not be called probabilities. The 22,840,529-byte file has SHA256 `d2d168e235faf9cdc3169c96ffc046635695bf1bec5e1e63a4066cd283cd198d`. Only processed in-vivo structure was acquired. See `docs/gse132099_feasibility.md`.

## ENSEMBL 88 TO 91 BRIDGE

The Ensembl 88 GRCh38.p10 GTF (46,157,774 bytes; SHA256 `ba9cb13686c3a4429724dfd6f6e52df92d1cc59675a4590d4a854f64ce633f46`), cDNA FASTA (64,661,761; `462823cdad614a2a77763004735fb9d4fabf3bb691b57737697208679c26cb86`) and ncRNA FASTA (9,318,335; `298925becc19859d420f5fbd70994c72ab82df1aedc94515faf86b000b2157b4`) were retrieved from exact Ensembl archive URLs in `metadata/reference_resources.tsv`. All 16,288 source FASTA candidates reconstructed from the genome. GSE132099-to-SG-NEx classes are **A 16,268; B 0; C 17; D 5; E 5**. Of A, 16,055 pass the prespecified 50 callable bases and 0.5 callable fraction. This is a genuine rescue, not a reinterpretation of GSE145805. Per-transcript bridge evidence is generated locally at `results/tables/ensembl88_to_91_transcript_bridge.tsv`; the large generated table is ignored by Git but reproducible from code and checksummed references. See `docs/ensembl88_to_91_bridge.md`.

## GSE149767

[GEO GSE149767](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE149767) supplies independent K562 in-vivo icSHAPE `.rx` profiles with two reactivity columns and `-999.0` uncalled values. The hg38 processed profiles use RefSeq NM/NR filenames with no pinned annotation release. A same-RefSeq fSHAPE map supplied base sequence only as an identity proxy, not as a substitute reactivity assay. Of 10,896 in-vivo profiles, 724 have a unique exact Ensembl 91 sequence proxy; 10,149 have no exact Ensembl 91 match, 18 no unique map, 4 map/profile length mismatches and 1 a nonunique Ensembl sequence. There are 353 sequence-proxy overlaps with the covered GSE132099 A set and 75 pass coverage in both in-vivo GSE149767 replicate columns. Classification: **WEAK** for independent structure-feature reproducibility and **UNSUITABLE** for validation of the structure-versus-sequencing increment. See `docs/gse149767_feasibility.md`.

## STRUCTURE REPRODUCIBILITY

Cross-study callable-fraction Spearman was -0.008 among the 75 shared eligible profiles.

The structure-only plan was written before comparing scores. On 75 profiles from 71 genes, GSE149767 replicate median-reactivity Spearman is 0.799. Cross-study median-reactivity Spearman is 0.196 with 500-draw gene-bootstrap 95% interval -0.063 to 0.408. Independent cross-study reproducibility is therefore **not established**; assay scales and small overlap limit interpretation. This result is kept even though unfavorable. The script never reads sequencing outcomes. See `docs/structure_reproducibility_plan.md` and `results/tables/structure_reproducibility_summary.json`.

## ALTERNATIVE SEQUENCING DATASETS

Metadata-only audit covered K562 [PacBio GSE143129/ENCSR589FUJ](https://www.encodeproject.org/experiments/ENCSR589FUJ/) (two replicates), [PacBio GSE174877/ENCSR526TQU](https://www.encodeproject.org/experiments/ENCSR526TQU/) (one replicate), [ONT direct-RNA GSE220019/ENCSR917JIA](https://www.encodeproject.org/experiments/ENCSR917JIA/) (two replicates), [ONT TALON GSE132766](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132766), untreated Illumina ENCSR000AEP/AEM and treated Illumina ENCSR534TGM. The last is JQ1-treated and unsuitable as an untreated partner. ENCODE alternatives have processed data but their transcript annotation, quantifier and biological-preparation matching remain unverified. No alternative transcript outcomes were opened. `docs/alternative_sequencing_resources.md` records the full compatibility matrix.

## RECOMMENDED DEVELOPMENT DATASET

Retain SG-NEx provisionally because its K562 preparation hierarchy, multi-platform workflows and Ensembl 91 Salmon outputs are audited, and the GSE132099 bridge is exact. This is a design choice based on metadata and QC, not a claim that SG-NEx is unbiased. ENCODE ONT plus untreated Illumina should be audited as an independent sequencing-behavior validation candidate or a replacement if annotation and preparation matching prove cleaner.

## ZERO-AWARE PRIMARY OUTCOME

The **candidate, unfrozen** primary endpoint is four-category supported detection after fixed Ensembl 91 reclosure: a library is detected at reclosed Salmon TPM at least 1; Illumina is detected with 2/2 Rep4/5 support, ONT direct RNA with at least 3/4 preparations; a platform is absent only with zero supporting libraries; intermediate support is indeterminate. Determined pairs are BOTH, ILLUMINA_ONLY, DIRECT_RNA_ONLY and NEITHER. Independent Illumina Rep3 TPM at least 1 is the expression eligibility source. In the 49,309 independently eligible measurement transcripts, counts are 11,731 BOTH, 20,201 ILLUMINA_ONLY, 315 DIRECT_RNA_ONLY, 3,687 NEITHER and 13,375 INDETERMINATE. Illumina pair detection agreement is 0.869 and mean ONT pair agreement is 0.880. RSEM versus Salmon Illumina status agreement is 0.861; NanoCount versus Salmon ONT agreement is only 0.519 on 30,445 complete NanoCount rows. No cross-platform disagreement is called measurement error. See `docs/zero_aware_endpoint_design.md`.

## SECONDARY OUTCOMES

Among BOTH, median within-ONT-library transcript percentile rank minus median within-Illumina-library percentile rank is the candidate quantitative secondary. Positive-only log2 TPM ratio is exploratory and undefined when any required estimate is zero, with no pseudocount. Isoform-fraction difference is exploratory when gene totals are positive. Spike-in relative true error remains separate and contingent on exact mixture/sample truth linkage.

## STRUCTURE ESTIMAND

The future question is conditional on uniquely A/B-bridged, coverage-adequate GSE132099 K562 transcripts with complete baseline features and independent Illumina abundance at least 1 TPM. It cannot generalize to all transcripts, other cells or matched aliquots. There are 16,055 A/coverage profiles before covariate/endpoint restrictions, 15,999 among the covariate-complete universe and 11,687 with independent abundance at least 1 in that audit. The final cohort is not frozen. See `docs/structure_estimand.md`.

## MISSINGNESS STRATEGY

The usable structure fraction is 15,999/198,539 (8.06%) in the adjusted availability universe. A descriptive expression/length/GC overlap stratum has 10,281/41,165 (25.0%) usable. Ridge availability probability is below 0.05 for 71.1% of all covariate-complete transcripts. Naive full-population IPW has maximum weight 246.6 and effective sample size about 6,302, so unrestricted weighting is rejected. An explicitly conditional complete-case estimand, attrition tables, coverage-threshold sensitivity and gene/sequence-group uncertainty are required; no population-wide extrapolation. See `docs/missingness_strategy.md`.

## CENTRAL HYPOTHESIS BLINDING

RNA structure versus sequencing measurement behavior has NOT been tested: **YES**. No icSHAPE score was correlated with a platform endpoint or baseline residual; no structure-containing model, feature importance or D versus C comparison was run. The structure-to-structure correlation above is a distinct assay-reproducibility diagnostic.

## LONGBENCH LOCK

Preserved: **YES**. Only the prior lock and catalog-level compatibility notes were read. No LongBench outcome file, distribution, benchmark figure, transcript result or model performance was accessed. No LongBench resource was downloaded. `docs/external_validation_lock.md` has the exposure audit.

## PUBLICATION OUTLOOK

**WEAK at present.** The annotation bridge creates a real conditional test opportunity, but the primary measurement phenotype has substantial ONT quantifier dependence and many indeterminate calls; independent structure-summary reproducibility is not established; structure availability selects a narrow cohort; sequencing and structure were measured in different preparations. A well-controlled negative result could still be informative if these limitations are resolved and its precision is adequate. No novelty, causation, accuracy or platform-recommender claim is supported now.

## FILES CREATED OR MODIFIED

New Phase 3B scripts under `scripts/` implement processed/reference acquisition, release bridging, GSE149767 sequence compatibility, mapping-failure audit, endpoint QC, missingness and structure-only reproducibility. `src/rnaobs/phase3b.py` and `tests/test_phase3b.py` add pure endpoint logic and synthetic checks. New metadata include `metadata/phase3b_resources.tsv`; datasets, downloads and reference manifests were updated. New docs cover each scientific decision and this report. Lightweight summary tables and the mapping-failure/threshold tables are tracked; large source archives and full derived tables remain ignored and reproducible from scripts.

## TEST RESULTS

The final local unit/governance suite passed 23/23 tests. `scripts/validate_repository.py` passed in both the original working directory and the repository-local commit clone. All seven Phase 3B downloads matched manifest bytes and SHA256 on reread. `git diff --check` passed. A staged-file audit found 47 implementation files, zero raw/cache/FASTQ/BAM/CRAM paths, zero common credential patterns and maximum staged file size 8,958 bytes. An initial governance test rejected the 8 MB bridge TSV as a large Git-visible generated file; it remains generated locally but ignored. The script and small class-count summary are tracked. The case-sensitive Illumina run-name and reference-universe closure issues found during QC were fixed and rerun, with superseded outputs overwritten; `docs/command_log.md` records them.

## FINAL COMMIT SHA

The scientific implementation commit is `a797439`. The final report commit is identified by `git rev-parse HEAD` in the terminal handoff; a commit cannot embed its own SHA.

## PRIVATE PUSH STATUS

The two Phase 3B commits were pushed from a repository-local clone to the existing `omicsedgebio/rna-observability` private remote on `main`. GitHub visibility was verified as PRIVATE before the push. The original checkout's `.git` directory is read-only in this execution environment, so its local HEAD/tracking ref cannot be advanced here; the terminal handoff verifies the actual remote SHA separately. No visibility change or public release was made.

## WORKING TREE STATUS

The repository-local commit clone is clean after push. The original checkout still reports Phase 3B source, metadata and documentation as modified/untracked against its old `52cb042` HEAD because this execution environment denied Git index writes with `Operation not permitted`. The work is preserved in place and pushed privately, but the original checkout's Git status is **not clean**. Do not misreport it as clean. Cached source files and generated large tables remain ignored.

## EXACT NEXT PHASE

Run a narrowly scoped **pre-freeze endpoint rescue** while keeping structure scores blinded to sequencing outcomes. Harmonize ONT quantifier output and zero semantics against the same fixed Ensembl 91 universe; verify the candidate four-category state survives a defensible alternative method and the biological-preparation hierarchy. Audit whether ENCODE untreated K562 Illumina plus direct RNA offers a cleaner independent phenotype without opening LongBench. Complete the exact eligible-cohort attrition and grouped fold graph, and decide whether the weak independent structure-summary reproducibility is acceptable for a conditional manuscript. Only then, if the measurement phenotype and selection estimand pass, write and commit a final frozen plan, fit structure-blind Models A/B/C, and seek review before the first Model D test. Do not run that structure-versus-sequencing test in this phase.
