# Public-release hygiene audit

Date: 2026-09-25

Scope: Git-visible files plus ignored-path policy; no external or LongBench access

## Findings

| Check | Result | Disposition |
|---|---|---|
| Credentials, private keys, common cloud/GitHub token forms | PASS | No match in Git-visible project files. This is pattern screening, not a credential guarantee. |
| Private Jira, Bitbucket, corporate, or internal-service URLs | PASS | No match found. |
| Raw sequencing formats | PASS | No Git-visible FASTQ, BAM, CRAM, FAST5, POD5, or BLOW5 file. |
| Cache and source-data exclusions | PASS | `.cache/`, `data/external/`, `data/processed/`, Python bytecode, and local environments remain ignored. |
| Oversized Git-visible artifacts | PASS | Largest visible file is below the repository's 1,000,000-byte policy limit. |
| LongBench scientific results | PASS_WITH_INCIDENT_RECORD | No LongBench result content was found or introduced. The contained search-response incident is described without scientific content. |
| Public scientific framing | PASS | README and current claims state the frozen near-null result and prohibit biological-irrelevance, truth, clinical, and structure-validation overclaims. |
| License and citation metadata | OPEN_RELEASE_BLOCKER | Project license and authorship are not finalized; `LICENSE_PENDING.md` and `CITATION_PENDING.md` must remain visible. No `CITATION.cff` is created yet. |
| Personal absolute paths in immutable provenance | RETAINED_WITH_LIMITATION | Four historical receipt/audit lines contain a local username/path. They document the actual execution environment and are already part of frozen provenance. Editing them would invalidate locked hashes and would not remove them from Git history. They are retained and must be considered in the final publication/privacy review. |

## Publication boundary

This audit prepares the working repository but does not declare it licensed,
released, archived, or suitable for unrestricted reuse. Source datasets and
large references remain excluded. Their original terms are not replaced by any
future project-code license.

No history rewrite, provenance deletion, repository-visibility change, release,
DOI, or public site deployment was performed.
