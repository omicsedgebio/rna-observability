# Formal novelty gate --- reconnaissance decision

Phase 3B design update, 2026-09-23: a new K562 in-vivo structure resource now maps exactly across Ensembl 88/91 for 16,055 coverage-eligible transcripts, and a zero-aware supported-detection phenotype replaces the pseudocount-dependent candidate. This changes feasibility, not novelty. The prior-art risk and MODIFY novelty gate remain. Independent structure-summary reproducibility is weak in a small cross-study overlap, and the primary sequencing phenotype remains quantifier sensitive. No new originality claim is made.

Decision: **MODIFY**. Date: 2026-09-22. This is a documented reconnaissance gate, not proof of novelty or an exhaustive systematic review. No modeling is authorized by this verdict.

Phase 3C interim decision, 2026-09-23: **MODIFY remains in force**. The Ensembl bridge is now defensible, but direct-RNA endpoint behavior remains quantifier sensitive and the cross-study structure diagnostic does not establish a reproducible structure summary. Endpoint selection, analysis freeze and baseline modeling are deferred for final review. This does not alter the narrow testable question or add an originality claim.

## Why modify

The broad proposition --�molecular RNA properties affect measurement--� is established. [miniQuant](https://doi.org/10.1038/s41587-025-02633-9) explicitly characterizes quantification difficulty and supports read-technology choice. [Price et al.](https://doi.org/10.1371/journal.pone.0173023) already link experimental PARS structure to Illumina read-start bias. [Su et al.](https://doi.org/10.1101/gr.280713.125) connect local sequence-derived structural representations to sequencing efficiency. [Brooks et al.'s preprint](https://doi.org/10.1101/2025.01.30.634337) reports no improvement from inferred structure in an alpine coverage model; its [2026 journal version](https://doi.org/10.1261/rna.080852.125) must be reconciled in a full review.

No inspected work was verified to jointly establish all six proposed components: reproducible transcript-level protocol phenotype, prediction, strong identifiability adjustment, measured in-vivo structure increment, independent study validation and local effects. That absence in this search does not establish that no such work exists.

The defensible narrower question is whether independent measured in-vivo accessibility adds transportable information after these existing explanations. A complete solution found on deeper review would trigger NO-GO for the current framing. Localized prediction is not independently novel just because it is added to this project.

## Complete-contribution audit

| Component | Existing contribution | Remaining question |
|---|---|---|
| Protocol-specific transcript behavior | SG-NEx and other benchmarks | Stable predictable phenotype with honest uncertainty |
| Molecular/sequence prediction | Bias correction; Su structural clustering | Independent protocol-pair transportability |
| Identifiability | miniQuant K-value; nonidentifiability ranges | Residual increment after sufficiently strong baseline |
| Experimental structure | Price PARS; PrismNet in-vivo features for a different target | Cell-context-aware incremental measurement prediction |
| Independent validation | Many tools use multiple datasets | Untouched independent study for this precise nested test |
| Localization | Read-start and coverage studies | Adds value only with controls and genuine region outcomes |

## Search coverage and limits

Queries and evidence links are in search_log.tsv and prior_art_matrix.tsv. Searched PubMed-indexed records; OpenAlex as the Google Scholar-equivalent discovery index; bioRxiv; medRxiv; journal sites; GitHub; public web tools; Google Patents; SG-NEx's curated citing/using works and targeted forward-use searches. No Google Scholar access is claimed. Search-engine indexing is incomplete. Patent discovery is a scientific overlap screen, not a legal freedom-to-operate determination.

Bibliographic convention: miniQuant was published online in June 2025 and appears in the March 2026 issue (Nature Biotechnology 44:477---489); the matrix uses online publication year. Do not count these as separate studies.

Included both supportive and contradictory evidence. Duplicate preprint/journal versions are a single contribution; matrix notes distinguish versions. LongBench's paper/results/citation graph were intentionally not examined to protect the validation lock. Its GEO and AWS catalog metadata were viewed only. SG-NEx forward-use searches found exitron artifacts, TranSigner, lr-kallisto, DeepChopper, and fusion benchmarking; this is not a complete forward-citation census.

Several publisher/PMC pages returned CAPTCHA/429 errors; public indexed excerpts and publisher HTML were used with evidence depth recorded. The Brooks journal update is bibliographically verified via PubMed's update link; journal methods not independently reconciled. Unknown matrix entries mean unknown, not absent.

## Reopening criteria

Before GO for modeling: audit closest full texts/supplements, resolve coordinate provenance and sample nesting, verify a reproducible phenotype is estimable, and specify an external structural-validation route. A non-structural LongBench test cannot silently substitute for external D>C validation. A generic sequence predictor or another benchmark alone is insufficient manuscript novelty.
