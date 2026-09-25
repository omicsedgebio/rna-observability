# External validation lock

## Contained search-response exposure, 2026-09-25

Status remains **LOCKED**. In a prior Codex session, accidental result-bearing
tutorial text appeared in a search response. The tutorial was not deliberately
opened. No LongBench file was accessed, no bucket was listed, no transcript
value was inspected, and no prediction or metric was computed. The session was
quarantined immediately, with no repository modification after recognition.
The exposed scientific content was not propagated into repository artifacts
and must not be reconstructed or repeated.

The eight external-validation candidate files predated the incident. A fresh
session independently reverified their exact pre-exposure SHA256 values, as
recorded in
`metadata/longbench_exposure_incident_20260925.json`. Future planning is limited
to clean agents and repository-local pre-exposure material. LongBench remains
**LOCKED**.

## Phase 3B exposure audit, 2026-09-23

Status remains **LOCKED**. Phase 3B read this lock and prior catalog-level compatibility notes only. No LongBench bucket, file, transcript outcome, platform-disagreement distribution, figure, model performance, tutorial result or association was accessed. No LongBench download occurred. The analysis plan is still `DRAFT_NOT_FROZEN`; its Phase 3B edit does not authorize release of the lock.

## Phase 2 lock update

LongBench remains locked. During this phase only dataset identity, public availability, technology labels, approximate scale, and licensing metadata were viewed. No transcript-level outcomes, plots, platform disagreement values, model predictions, performance metrics, or transcript-specific behavior were inspected. No LongBench feature, threshold, or hypothesis was selected using outcome information. The lock date is 2026-09-23.

Status: LOCKED
Lock date: 2026-09-22
Dataset: biological LongBench, GEO GSE303762 / AWS longbench-data; not the similarly named language-model benchmark.
Sources: [GEO identity](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE303762), [AWS catalog](https://registry.opendata.aws/longbench/).

Metadata viewed: title, summary/design, public-release date (2025-09-01), eight lung-cancer cell lines, bulk/single-cell/single-nucleus modalities, bulk ONT PCR-cDNA and direct RNA, PacBio Kinnex and Illumina; synthetic Sequins/SIRV controls; availability of raw/aligned material, references and processed gene expression; CC BY-4.0 license; bucket location and documentation link. No transcript-level outcomes, values, plots, performance summaries, tutorial outputs, or model evaluations viewed. No LongBench files downloaded and no S3 listing performed. Approximate byte size is UNKNOWN; eight cell lines is metadata scale, not a download estimate.

## Prohibited before freeze

No outcome files, distributions, cross-platform concordance, transcript detection, performance, benchmark results, figure captions containing results, or outcome-containing tutorials. No testing, feature selection, missingness thresholds, annotation filtering, platform selection or hypothesis revision using validation outcomes. Do not open its full paper as routine literature review. No training or preprocessing fitted on validation data.

## Release of lock

Requires explicit authorization for evaluation after docs/frozen_analysis_plan.md is complete, approved and committed with status FROZEN; exact code/config/environment/model hashes; independent-study inclusion manifest and outcomes-blind compatibility audit. Record the freeze commit and timestamp in a later validation record. Record predictions before scoring. Perform the predeclared evaluation once and retain failures.

There is no verified matched structure assay for these cell contexts. Decide before unlock whether D can be tested with independent cell-matched structure. Using K562 reactivity in lung cells tests transfer of a fixed K562 proxy, not matched in-vivo structure generalization. Model C transport can be evaluated separately but does not validate H3.

## Exposure log

| Date | Access | Reason | Outcome exposure |
|---|---|---|---|
| 2026-09-22 | General identity search; GEO catalog result; AWS catalog page | Existence/platform/license feasibility | None identified; catalog-level summary only |

No claimed physical access isolation: this is a documented procedural lock with offline CI guards. Future access must append its purpose and fields viewed, including accidental exposure. If outcomes are inadvertently exposed, quarantine affected decisions and reassess confirmatory validity.

## Phase 3A interruption-recovery audit, 2026-09-23

The prior Phase 1/2 lock document and previously recorded compatibility metadata were read. No LongBench bucket, file, transcript-level result, outcome distribution, benchmark/tutorial figure, model performance or association was opened or downloaded. The Phase 3A acquisition script contains a URL/accession guard; an attempted generic literature query containing the word LongBench was rejected before a network transfer. It produced no LongBench exposure. Search of local outputs and scripts found no LongBench outcome dependency. Status remains **LOCKED**. No committed frozen plan exists, so the release conditions are unmet.
