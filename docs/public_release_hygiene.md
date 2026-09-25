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
| License and citation metadata | PASS_WITH_RELEASE_METADATA_LIMITS | Apache-2.0 is selected for project-authored software and non-manuscript repository documentation under `LICENSE_SCOPE.md`; Priyansh Pathak is the sole author recorded in `CITATION.cff`. No DOI, ORCID, affiliation, archival deposit, or tagged release version is claimed yet. |
| Personal absolute paths in immutable provenance | RETAINED_WITH_LIMITATION | Five historical provenance occurrences contain a local username/path. They document the actual execution environment and are already part of frozen provenance. Editing them would invalidate locked hashes and would not remove them from Git history. They are retained. The author explicitly accepted their public visibility during the final privacy review on 2026-09-25. |

## Publication boundary

This audit prepares the working repository for public release. Project-authored
software and non-manuscript repository documentation are licensed under Apache-2.0 as scoped
by `LICENSE_SCOPE.md`. This does not license or relicense source datasets,
third-party software, external validation resources, or large reference files,
which retain their original terms.

The repository has not yet been declared a tagged release, archived deposit, or
DOI-bearing research object.

No history rewrite, provenance deletion, repository-visibility change, release,
DOI, or public site deployment was performed.

## Public-preparation hash maintenance, 2026-09-25

After finalizing the repository-level Apache-2.0 license scope and citation
metadata, the `public_preparation_artifact_sha256` entries in
`metadata/longbench_external_validation_manifest.json` were refreshed to match
the resulting public-facing repository files.

This is non-scientific release maintenance. It does not change the external
validation objective, compatibility audit, development result, deployment
estimator, LongBench access state, release conditions, scientific configuration,
or any frozen scientific/governance hash group. LongBench remains locked.

## Final rights and privacy review, 2026-09-25

The final repository-level rights and privacy review was completed before any
repository-visibility change.

Five tracked historical provenance occurrences contain the local path component
`/Users/priyanshpathak/`. They contain no credential, token, private key, patient
identifier, or raw sequencing payload. They are retained because they document
the actual execution environment, are already part of repository history, and
editing frozen provenance would invalidate integrity records without removing
the historical copies.

The author explicitly accepted public visibility of those five occurrences.

Contribution guidance is provided in `CONTRIBUTING.md`. This review does not
authorize LongBench access, change any scientific result, or create a tagged,
archived, or DOI-bearing release.
