# OmicsEdgeBio Project 001 --- RNA measurement behavior

RNA-sequencing technologies do not observe every transcript equally. This project investigates whether intrinsic molecular properties of RNA can help explain and predict technology-specific measurement behavior.

Research in progress. The hypothesis is not yet validated. --�RNA Observability--� is provisional terminology, not an established property or validated score. No validated predictive model is currently available. No clinical use, diagnostic use, or sequencing-platform recommendation.

Phase 1 verdict: **MODIFY**. See [novelty gate](docs/novelty_gate.md), [K562 feasibility](docs/k562_feasibility.md), and [phase report](docs/phase1_report.md). There are no project results, fitted models, or generated scientific figures.

## Research boundaries

- Keep the project private. No push, public release, DOI deposit, or website deployment without explicit approval.
- LongBench is locked external validation: [firewall](docs/external_validation_lock.md).
- The [analysis plan](docs/frozen_analysis_plan.md) is deliberately **DRAFT_NOT_FROZEN**. A filename or initial commit is not a scientific freeze.
- Cross-platform disagreement is not measurement error without defensible truth.
- Experimental in-vivo structure is context dependent and assay dependent; it is not purely transcript intrinsic.
- Null and negative findings are valid. Do not optimize for a positive result.

## Navigation and checks

[Question](docs/research_question.md) · [Hypotheses](docs/hypotheses.md) · [Prior art](docs/prior_art_matrix.tsv) · [Datasets](metadata/datasets.tsv) · [Outcomes](docs/outcome_definition.md) · [Features](docs/feature_registry.md) · [Claims](docs/claims_register.md) · [Reproduction](docs/reproducibility.md).

Run `python3 scripts/validate_repository.py` and `python3 -m unittest discover -s tests -v` (Python 3.9+, standard library only). CI performs lightweight offline checks on Linux; it does not fetch data or fit models.

On the audited development machine, the default Python 3.9 standard library is damaged; both checks passed using `/opt/homebrew/opt/python@3.12/bin/python3.12` (3.12.14). See the reproduction notes before running locally.

Large/source data belong in ignored directories. Code licensing and citation metadata remain pending. Source data have their own reuse terms; SG-NEx's noncommercial restriction must be assessed before company-hosted reuse.
