#!/usr/bin/env python3
"""Offline Phase 1 governance/schema checks; not scientific validation."""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    "research_question hypotheses novelty_gate claims_register outcome_definition "
    "feature_registry k562_feasibility sgnex_feasibility external_validation_lock "
    "frozen_analysis_plan manuscript_plan assumptions limitations decision_log "
    "reproducibility phase1_report command_log sgnex_processed_data_qc replicate_structure icshape_qc structure_missingness outcome_selection quantifier_sensitivity identifiability_baseline structure_feature_specification k562_compatibility_audit data_reuse_and_licensing structure_external_validation_search phase2_report"
).split()
REQUIRED = [
    "README.md", "AGENTS.md", "LICENSE_PENDING.md", "CITATION_PENDING.md",
    "data/README.md", "results/README.md", "metadata/datasets.tsv",
    "docs/prior_art_matrix.tsv", "docs/search_log.tsv", "configs/phase1.json",
    ".github/workflows/validate.yml",
] + ["docs/" + name + ".md" for name in DOCS]
DIRS = (
    "configs data/external data/processed scripts src analysis/pilot_k562 "
    "results/tables results/figures manuscript/figures manuscript/tables manuscript/notes tests"
).split()
SCHEMAS = {
    "metadata/datasets.tsv": (
        "dataset_id role accession identity_url technologies contexts processed_resource "
        "download_url size_bytes size_status genome_build annotation replicates license "
        "compatibility_status retrieval_date download_status sha256 locked"
    ).split(),
    "docs/prior_art_matrix.tsv": (
        "work_id citation year permanent_url research_question technologies biological_system "
        "ground_truth analysis_level rna_structure_included structure_type measurement_error_modeled "
        "cross_platform technology_specific predictive_or_descriptive independent_external_validation "
        "software_tool closest_overlap remaining_difference evidence_depth accessed"
    ).split(),
    "docs/search_log.tsv": (
        "search_id date channel query_or_resource screening_result limitation"
    ).split(),
}


def read_table(path, expected):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    errors = []
    if not rows or rows[0] != expected:
        return [], [str(path) + ": wrong or missing header"]
    if len(rows) < 2:
        errors.append(str(path) + ": no data rows")
    ids = set()
    result = []
    for line, row in enumerate(rows[1:], 2):
        if len(row) != len(expected) or any(not cell.strip() for cell in row):
            errors.append(f"{path}:{line}: ragged/empty fields")
            continue
        if row[0] in ids:
            errors.append(f"{path}:{line}: duplicate identifier {row[0]}")
        ids.add(row[0])
        result.append(dict(zip(expected, row)))
    return result, errors


def forbidden_file(path, size, limit=1000000):
    name = path.lower()
    raw = re.search(r"\.(fastq|fq|bam|bai|cram|crai|fast5|pod5|blow5)(\.gz)?$", name)
    private_dir = name.startswith(("data/external/", "data/processed/", ".cache/", "tmp/"))
    return bool(raw or size > limit or (private_dir and not name.endswith("/.gitkeep")))


def phase_errors(policy, plan, lock, datasets):
    errors = []
    expected = {
        "phase": "reconnaissance", "novelty_verdict": "MODIFY",
        "modeling_authorized": False, "external_validation_locked": True,
        "analysis_plan_status": "DRAFT_NOT_FROZEN", "external_outcomes_viewed": False,
        "public_release_authorized": False, "push_authorized": False,
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            errors.append("Phase 1 policy mismatch: " + key)
    if "Status: DRAFT_NOT_FROZEN" not in plan:
        errors.append("Plan incorrectly marked frozen or missing status")
    if "Status: LOCKED" not in lock or "2026-09-22" not in lock:
        errors.append("Missing external lock/status/date")
    external = [r for r in datasets if r["dataset_id"] == "LONGBENCH"]
    if len(external) != 1:
        errors.append("Exactly one LongBench registry row required")
    elif external[0]["locked"] != "true" or external[0]["download_status"] != "NOT_DOWNLOADED":
        errors.append("LongBench must remain locked and not downloaded in Phase 1")
    for row in datasets:
        if row["locked"] not in {"true", "false"}:
            errors.append("Invalid locked boolean: " + row["dataset_id"])
        if row["download_status"] == "NOT_DOWNLOADED" and row["sha256"] != "NA_NOT_DOWNLOADED":
            errors.append("Unacquired data cannot have an invented checksum: " + row["dataset_id"])
        if row["size_bytes"] != "UNKNOWN" and not row["size_bytes"].isdigit():
            errors.append("Invalid byte count: " + row["dataset_id"])
    return errors


def validate(root=ROOT):
    errors = []
    for rel in REQUIRED:
        if not (root / rel).is_file() or not (root / rel).stat().st_size:
            errors.append("Missing/empty required file: " + rel)
    for rel in DIRS:
        if not (root / rel).is_dir():
            errors.append("Missing directory: " + rel)
    if errors:
        return errors
    tables = {}
    for rel, schema in SCHEMAS.items():
        tables[rel], found = read_table(root / rel, schema)
        errors.extend(found)
    if len(tables["docs/prior_art_matrix.tsv"]) < 10:
        errors.append("Insufficient populated prior-art records")
    policy = json.loads((root / "configs/phase1.json").read_text())
    errors.extend(phase_errors(
        policy, (root / "docs/frozen_analysis_plan.md").read_text(),
        (root / "docs/external_validation_lock.md").read_text(),
        tables["metadata/datasets.tsv"],
    ))
    files = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
    ).decode().split("\0")
    for rel in sorted(set(filter(None, files))):
        path = root / rel
        if not path.is_file():
            errors.append("Listed file absent: " + rel)
            continue
        if forbidden_file(rel, path.stat().st_size, policy["max_committed_file_bytes"]):
            errors.append("Source/large/cache file would be committed: " + rel)
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                if "://" in target or target.startswith(("#", "mailto:")):
                    continue
                local = target.split("#", 1)[0]
                if local and not (path.parent / local).exists():
                    errors.append(f"{rel}: broken local link {local}")
    return errors


if __name__ == "__main__":
    issues = validate()
    for issue in issues:
        print("FAIL:", issue)
    if issues:
        sys.exit(1)
    print("PASS: Phase 1 scaffold, registry schemas, links, policy flags, and Git-visible file hygiene")
    print("Not a biological, novelty, license, or external-access certification.")
