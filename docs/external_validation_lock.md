# External validation lock

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
