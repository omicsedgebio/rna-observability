# Reproducibility

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
