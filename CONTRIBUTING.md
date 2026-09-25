# Contributing

RNA Observability is a research repository with frozen scientific and governance
artifacts. Contributions are welcome when they preserve those boundaries.

## Before opening a change

Please distinguish between:

- corrections to documentation, tests, packaging, or reproducibility tooling;
- new exploratory analyses;
- changes that would alter a frozen scientific result, model specification,
  provenance record, validation lock, or authorization boundary.

Do not rewrite historical provenance or frozen scientific artifacts to make them
look cleaner retrospectively.

## Scientific changes

Changes affecting scientific conclusions should be proposed separately from
maintenance changes and should state:

- the scientific question being changed or extended;
- whether the change is exploratory, confirmatory, or post-development;
- which frozen artifacts are affected;
- whether any new data access or outcome inspection is required;
- how leakage, model-selection, and external-validation boundaries are preserved.

LongBench remains locked unless the repository's explicit authorization and
release conditions are satisfied.

## Data and licensing

Do not commit raw sequencing data, large external resources, credentials, or
third-party materials that the repository is not permitted to redistribute.

Project-authored software and non-manuscript repository documentation are
licensed as described in `LICENSE` and `LICENSE_SCOPE.md`. Third-party resources
retain their own terms; see `THIRD_PARTY_NOTICES.md`.

## Validation

Run the repository validator and relevant tests before submitting changes.
