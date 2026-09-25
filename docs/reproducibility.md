# Reproducibility

## Current frozen state, 2026-09-25

The historical Phase 1 notes below are retained for chronology but no longer
describe the current project state. The Model D development comparison has been
executed once and frozen at commit
`294f59ddab5dc4262d23ebbd976f2cec6469bc71` with conclusion
`NOT_SUPPORTED / NEGLIGIBLE`. Model D must not be rerun. The post-development
Model C deployment estimator is a separate transparent artifact verified by
`scripts/materialize_model_c_deployment.py --verify`; its fit mode is consumed
and cannot be rerun automatically.

The locked scientific environment is Python 3.11.12, NumPy 2.4.2, SciPy 1.17.1,
pandas 3.0.6, DuckDB 1.5.5, scikit-learn 1.9.1, and threadpoolctl 3.7.0. Safe
offline checks are listed in the repository README. LongBench remains locked and
is not part of reproduction.

## Historical Phase 1 record

Phase 1 contains literature/metadata reconnaissance and offline repository validation only. No models, science package environment, random draws, scientific inputs or results yet.

Local observed environment: macOS Darwin 25.6.0 arm64; Python 3.9.6; Git 2.50.1 (Apple Git-155). Checks use only the Python standard library. Linux CI targets Python 3.11 on ubuntu-24.04. Linux execution has not been observed locally; workflow configuration is not a CI pass.

The default Python 3.9.6 ran the validator but failed importing standard-library tempfile due to a pre-existing SyntaxError in /Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/tempfile.py. No system file was edited. The installed Homebrew Python 3.12.14 at /opt/homebrew/opt/python@3.12/bin/python3.12 successfully ran the validator and all six tests. Use that explicit interpreter on this machine until its default environment is repaired separately.

Commands:
```sh
python3 scripts/validate_repository.py
python3 -m unittest discover -s tests -v
git diff --check
```

Sources and retrieval dates are recorded in docs/search_log.tsv, docs/prior_art_matrix.tsv and metadata/datasets.tsv. Reference lookup date is 2026-09-22 (America/New_York). Browser/search excerpts can be stale; do not mistake crawl dates for publication dates. SG-NEx manifest pinned to fea2aa80b149778d7fce507867dd6754fc4f84ca; no outcome payload downloaded or hash invented.

Future data manifests require acquisition time (UTC), URL, accession, source release, exact bytes, SHA-256, license/permission, command, parameters, genome/annotation hashes, input/output paths and producing code commit. ETag is not a general-purpose content checksum. Catalog-only entries use NA_NOT_DOWNLOADED.

Before scientific execution: pin R/Python and dependencies, create lockfiles and a Linux environment recipe, fix seeds/fold membership/configuration, record sample exclusion reasons, and define memory limits. Avoid installing large ML stacks. Every scientific output must carry generating command/config/code/input hashes; regenerate manuscripts programmatically.

CI validates schema/policies/local links and data exclusions; it does not certify novelty, source correctness, actual license permissions, biological compatibility, or the procedural validation firewall.

Release remains deferred: finalize authors/title/license/URL; audit rights; add CITATION.cff and contribution guidance; approve a publication-grade tagged GitHub release, then archive the exact version on Zenodo and cite its DOI. No development deposits, no final metadata or website in this phase.

## Phase 3A reproducibility record

The phase was resumed after interruption without rerunning completed 1.955 GB reference downloads, genomic reconstruction, 31-mer calculation or original miniQuant K-value calculation. `metadata/reference_resources.tsv` and `metadata/phase3a_source_provenance.tsv` record exact URLs, timestamps, sizes and SHA256 checksums. `metadata/phase3a_integrity_audit.json` verifies all 7 reference and 73 small source files still match; no raw sequencing files were acquired. R extraction uses R 4.3.1 with the package session in `metadata/phase3a_R_session.txt`. Python runs from the project-local Python 3.12.14 environment; exact packages are in `metadata/phase3a_python_packages.txt`. C++ features use a C++23 compiler. The original miniQuant commit is c1b5a89f3c31c83b271a477475a1e289ee9806d7. Ensembl reference is release 91, GRCh38. No stochastic feature or reference step was used; proposed future grouped CV seeds 230923-230925 are not yet executed.

In a prepared environment with the checksummed source objects in their documented ignored cache paths, the completed local commands are:

```sh
Rscript scripts/phase3a_extract.R
.venv/bin/python scripts/phase3a_references.py
c++ -std=c++23 -O3 src/exact_kmers.cpp -o .cache/phase3a/exact_kmers
.cache/phase3a/exact_kmers .cache/phase3a/references/validated_transcripts.fa 31 .cache/phase3a/qc/kmer_scratch results/tables/unique_kmers31.tsv
.venv/bin/python scripts/run_miniquant_kvalue.py
.venv/bin/python scripts/phase3a_feature_audit.py
.venv/bin/python scripts/phase3a_outcome_qc.py
.venv/bin/python scripts/phase3a_missingness.py
.venv/bin/python scripts/validate_repository.py
.venv/bin/python -m unittest discover -s tests -v
```

The full Ensembl 91 references and local derived transcript matrices remain ignored. Selected small status summaries and SVG availability QC figures are tracked. Scripts must be run from the repository root. The missingness script enforces an availability-only input schema; the outcome script does not import reactivity. `scripts/phase3a_acquire.py` rejects LongBench URLs. No baseline model or structure hypothesis test was run.
