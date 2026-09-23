# Phase 1 command and access log

Date: 2026-09-22. Read-only remote calls did not alter external applications. No push, model training, raw-data transfer or LongBench outcome access.

## Local inspection

Commands executed included `pwd`, `ls -la`, `git status --short`, `rg --files -g AGENTS.md -g '!data/**'`, `git status --branch --short`, `git log -1 --oneline`, `git remote -v`, `python3 --version`, `git --version`, and `uname -srm`.

Initial repository contained only .git, no commits and no user files. The initial rg returned exit 1 because no files matched; git log returned 128 because main was unborn. Origin was already configured to the OmicsEdgeBio repository. Neither remote visibility nor remote branch content was changed or independently checked.

## Public retrieval

Web searches and primary-page reads are cataloged in search_log.tsv; prior_art_matrix.tsv holds permanent source links and evidence depth. Some Nature/PMC readers failed with redirects/CAPTCHA; PubMed returned a 429 on one update page. The initial unquoted GitHub API URL caused zsh glob failure and was corrected. A sandbox curl failed DNS (exit 6); the same operation was retried with approved network escalation. One guessed AWS registry filename failed; the canonical registry page /sgnex/ was subsequently found. One Europe PMC metadata query returned only a version object and provided no usable evidence. No failed response was counted as verification.

Representative exact successful retrieval commands (output was inspected in memory, not saved as source data):

```sh
curl -L --fail --max-time 30 -s 'https://api.github.com/repos/GoekeLab/sg-nex-data/git/trees/master?recursive=1'
curl -L --fail --max-time 30 -s 'https://raw.githubusercontent.com/GoekeLab/sg-nex-data/fea2aa80b149778d7fce507867dd6754fc4f84ca/docs/samples.tsv'
curl -L --fail --max-time 30 -s 'https://raw.githubusercontent.com/GoekeLab/sg-nex-data/fea2aa80b149778d7fce507867dd6754fc4f84ca/docs/illumina_samples.tsv'
curl -L --fail --max-time 30 -s 'https://sg-nex-data.s3.ap-southeast-1.amazonaws.com/?list-type=2&prefix=data/processed_data/&delimiter=/'
curl -L --fail --max-time 30 -s 'https://sg-nex-data.s3.ap-southeast-1.amazonaws.com/?list-type=2&prefix=data/processed_data/manuscript/&delimiter=/'
curl -L --fail --max-time 30 -s 'https://sg-nex-data.s3.ap-southeast-1.amazonaws.com/data/processed_data/manuscript/README.txt'
curl -L --fail --max-time 30 -s 'https://sg-nex-data.s3.ap-southeast-1.amazonaws.com/?list-type=2&prefix=data/processed_data/manuscript/processed/&max-keys=1000'
curl -L --fail --max-time 30 -s 'https://www.nature.com/articles/s41592-025-02623-4'
curl -L --fail --max-time 30 -s 'https://www.nature.com/articles/s41422-021-00476-y'
```

Metadata TSV streams were filtered to K562 with Python csv.DictReader; publisher HTML was reduced to relevant method passages with regex. This was metadata inspection, not quantitative analysis. Exact raw URLs and the source tree commit permit repetition. No page snapshots/checksums were archived, so source evidence is link-traceable rather than a bitwise archived literature corpus.

Local file creation/edits used apply_patch. A spreadsheet skill was inspected but no workbook workflow was used; requested deliverables are plain repository TSV/Markdown. Supplementary workbook content could not be verified through the web reader; unresolved details are recorded, not inferred.

## Verification and local commit

Run `python3 scripts/validate_repository.py`, `python3 -m unittest discover -s tests -v`, `git diff --check`, stage the scoped scaffold, inspect `git diff --cached --stat` and `git diff --cached --check`, then local `git commit -m "Initialize private RNA measurement research scaffold and reconnaissance"`.

Actual check outcomes and any commit limitation are reported in phase1_report.md and the final handoff. The final commit identifier is read from git after committing; no self-referential hash is embedded in the committed report.

Observed: default Python validator passed, but unittest failed importing a damaged standard-library tempfile.py. Interpreter discovery used `which -a python3`, `ls -l /usr/bin/python3 /opt/homebrew/opt/python@3.12/bin/python3.12`, and the latter's `--version`. A prior `command -v -a` attempt was invalid in this shell and yielded no evidence. Successful checks:

```sh
/opt/homebrew/opt/python@3.12/bin/python3.12 scripts/validate_repository.py
/opt/homebrew/opt/python@3.12/bin/python3.12 -m unittest discover -s tests -v
git diff --check
git check-ignore data/external/probe.rds data/processed/probe.tsv tmp/probe.txt example.fastq.gz
```

Validator and all six tests passed; all four ignore probes matched. Probe filenames were arguments only; no probe data were created. Default Python installation was left untouched.

Staging initially failed because the sandbox disallowed .git/index.lock; the same scoped git add was retried with approval. The staged whitespace check then identified trailing empty lines in 18 text files. A bulk formatting command (`perl -0pi -e 's/\n+\z/\n/'` on the explicitly listed files) normalized final newlines before restaging and checking again.

## Phase 3A interruption recovery and resolution, 2026-09-23

At resume, `main`, `HEAD` and private `origin/main` were `e83efc6`; Phase 3A files were untracked and no Phase 3A commit existed. Inspected every untracked script/source/metadata file, ignored reference and QC cache inventory, phase logs, partial outputs, earlier reports, claims and lock docs, and git status/diff. Successful prior computations were retained: Ensembl 91 and SG-NEx reference downloads, GTF/FASTA/genome validation, exact canonical 31-mers, original miniQuant gene K-values, SG-NEx RDS extraction, abundance/outcome-only QC and spike-in inventory. The sole partial operation was adjusted missingness GLM, which failed due rank deficiency/nonconvergence; no adjusted table or figure existed. It was replaced by explicitly descriptive standardized ridge logistic QC, then rerun successfully. The source-code audit found no RNA reactivity-versus-outcome calculation, and no LongBench outcome access. A generic literature query containing the lock name was rejected by the acquisition guard before transfer.

Validation commands used `find` and `rg` for file/log inventory, `git status --short`, `git diff --check`, project Python checks, `Rscript` extraction in the prior session, and read-only web/GEO/Ensembl/source-code retrieval. `metadata/phase3a_integrity_audit.json` checks 80 downloaded files: seven large references totaling 1,955,127,239 bytes and 73 small source/metadata files totaling 5,127,992 bytes, with no size or SHA256 failures. `scripts/phase3a_feature_audit.py` joined the previously completed feature outputs without recomputing references, kmers or miniQuant. No raw read transfer was attempted. Availability figures were inspected visually and the overlap diagnostic was changed to cumulative curves for legibility. The package/environment record and exact regeneration commands are in `docs/reproducibility.md`.
# Phase 3B command and failure record, 2026-09-23

`scripts/phase3b_acquire.py` downloaded processed GSE132099 and GSE149767 files and registered exact bytes/SHA256. A single-stream Ensembl 88 transfer was interrupted after approximately 1.5 MB because the archive endpoint delivered slowly; the partial `.cache` file was not used. `scripts/phase3b_parallel_reference.py` then fetched the same authoritative URLs by verified HTTP byte ranges, checked expected lengths and gzip integrity, and registered SHA256 through `scripts/phase3b_acquire.py`. No annotation substitution occurred. An ENCODE biosample search API request returned HTTP 404; experiment pages and public JSON metadata were used instead, and no result from the failed query informed the design.

`scripts/phase3b_structure_inventory.py`, `phase3b_bridge.py`, `phase3b_gse149767.py`, `phase3b_mapping_failures.py`, `phase3b_structure_reproducibility.py`, `phase3b_endpoint_qc.py`, `phase3b_missingness.py` and `phase3b_register_metadata.py` generated all Phase 3B tables. The initial endpoint QC run rejected an unexpected Illumina replicate count because one run uses lowercase `k562`; the run-name filter was corrected to case-insensitive cell-line matching and the full QC was rerun. The initial missingness audit closed TPM over all source rows rather than the fixed Ensembl feature universe; it was corrected and rerun. Both superseded outputs were overwritten before interpretation. No structure-versus-sequencing value analysis occurred.

Validation: `.venv/bin/python -m unittest discover -s tests -v`; `.venv/bin/python scripts/validate_repository.py` if available; `git diff --check`; resource checksum verification from `metadata/phase3b_resources.tsv`; `git status`/staged-file review. Large reference/processed source archives and untracked ENCODE JSON remain in ignored `.cache/phase3b/`.
