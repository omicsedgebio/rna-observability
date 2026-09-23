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
