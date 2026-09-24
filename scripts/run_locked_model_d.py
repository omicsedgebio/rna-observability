#!/usr/bin/env python3
"""Single-attempt future execution for the approved locked Model D analysis.

During PRESTRUCTURE_IMPLEMENTATION_LOCK only ``--preflight`` is permitted.  It
does not accept or open a structure path and does not fit any model.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import gzip
import importlib.metadata
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rnaobs.model_d_locked import (
    AnalysisBlocker,
    ANNOTATION_MATRIX_COLUMNS,
    C_ANNOTATION_FEATURES,
    C_QUALITY_FEATURES,
    CLASSES,
    D_STRUCTURE_FEATURES,
    PROBABILITY_COLUMNS,
    all_metrics,
    bootstrap_interval,
    central_decision,
    fit_oof,
    fold_macro_f1_deltas,
    macro_f1,
    paired_cluster_bootstrap,
    parse_mapping_tsv,
    parse_structure_stream,
    per_class_f1,
    permutation_row_counts,
    run_negative_control,
    sha256,
    strict_callability_subset,
    validate_annotation_matrix,
)

MANIFEST = ROOT / "metadata/prestructure_implementation_lock_candidate_manifest.json"
ATTEMPT_POLICY = ROOT / "metadata/model_d_attempt_guard.json"
ATTEMPT_MARKER = ROOT / "metadata/model_d_attempt_consumed.json"
FAILURE_LOG = ROOT / ".cache/model_d/model_d_failure.json"
AUTHORIZATION = ROOT / "metadata/model_d_execution_authorization.json"
STRUCTURE = ROOT / ".cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz"
MAPPING = ROOT / ".cache/model_d/class_a_mapping.tsv"
OUTPUT_DIR = ROOT / "results/tables"
EXPECTED_STRUCTURE_SHA256 = "d2d168e235faf9cdc3169c96ffc046635695bf1bec5e1e63a4066cd283cd198d"
EXPECTED_STRUCTURE_BYTES = 22_840_529
LONG_BENCH_TOKENS = ("longbench", "gse303762", "longbench-data")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def reject_longbench_path(path: Path) -> None:
    lowered = str(path).lower()
    if any(token in lowered for token in LONG_BENCH_TOKENS):
        raise AnalysisBlocker("LongBench path/resource access is prohibited")


def verify_environment() -> dict[str, str]:
    if sys.version_info[:3] != (3, 11, 12):
        raise AnalysisBlocker("Python version differs from implementation lock")
    expected = {
        "numpy": "2.4.2",
        "scipy": "1.17.1",
        "pandas": "3.0.6",
        "duckdb": "1.5.5",
        "scikit-learn": "1.9.1",
        "threadpoolctl": "3.7.0",
    }
    observed = {name: importlib.metadata.version(name) for name in expected}
    if observed != expected:
        raise AnalysisBlocker("package environment differs from implementation lock")
    return observed


def verify_frozen_files(manifest: dict) -> None:
    protected = manifest["protected_file_sha256"]
    for relative, expected in protected.items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            raise AnalysisBlocker(f"frozen implementation-lock item changed: {relative}")


def read_locked_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cohort = pd.read_csv(ROOT / "metadata/final_transcript_cohort.tsv", sep="\t")
    folds = pd.read_csv(ROOT / "metadata/cv_folds.tsv", sep="\t")
    model_c = pd.read_csv(ROOT / "results/tables/model_c_inputs.tsv.gz", sep="\t")
    annotation = pd.read_csv(ROOT / "results/tables/prestructure_annotation_comparator.tsv.gz",
                             sep="\t", keep_default_na=True)
    historical_oof = pd.read_csv(ROOT / "results/tables/model_c_oof.tsv.gz", sep="\t")
    frozen_ids = cohort["stable_id"].astype(str).tolist()
    validate_annotation_matrix(annotation, frozen_ids)
    if model_c["stable_id"].astype(str).tolist() != frozen_ids:
        raise AnalysisBlocker("saved Model C input order differs from frozen cohort")
    if folds["stable_id"].astype(str).tolist() != frozen_ids:
        raise AnalysisBlocker("fold order differs from frozen cohort")
    if not np.array_equal(model_c["fold"].to_numpy(), folds["fold"].to_numpy()):
        raise AnalysisBlocker("saved input folds differ from frozen folds")
    if not np.array_equal(model_c["sequence_cluster_id"].astype(str).to_numpy(),
                          folds["sequence_cluster_id"].astype(str).to_numpy()):
        raise AnalysisBlocker("saved input clusters differ from frozen folds")
    if not bool(model_c["label"].isin(CLASSES).all()):
        raise AnalysisBlocker("saved Model C input contains an unexpected class")
    if len(model_c) != 15_999 or folds["sequence_cluster_id"].nunique() != 4_314:
        raise AnalysisBlocker("frozen row or sequence-cluster count differs from lock")
    if folds.groupby("sequence_cluster_id")["fold"].nunique().max() != 1:
        raise AnalysisBlocker("a frozen sequence cluster crosses outer folds")
    if not np.isfinite(model_c["sample_weight"]).all() or not np.equal(
            model_c["sample_weight"].to_numpy(dtype=np.float64), 1.0).all():
        raise AnalysisBlocker("saved sample weights differ from locked unit weights")
    cluster_size = model_c["sequence_cluster_id"].map(
        model_c["sequence_cluster_id"].value_counts()).to_numpy()
    if not np.array_equal(cluster_size, model_c["sequence_cluster_size"].to_numpy()):
        raise AnalysisBlocker("saved sequence_cluster_size differs from frozen groups")
    if historical_oof["stable_id"].astype(str).tolist() != frozen_ids:
        raise AnalysisBlocker("historical Model C OOF order differs from frozen cohort")
    if not np.array_equal(historical_oof["y"].astype(str).to_numpy(),
                          model_c["label"].astype(str).to_numpy()):
        raise AnalysisBlocker("historical Model C OOF outcomes differ from saved inputs")
    return cohort, folds, model_c, annotation, historical_oof


def preflight() -> dict:
    manifest = load_json(MANIFEST)
    verify_frozen_files(manifest)
    environment = verify_environment()
    cohort, folds, model_c, annotation, historical_oof = read_locked_inputs()
    guard = load_json(ATTEMPT_POLICY)
    if guard != {
        "guard_version": "model_d_single_attempt_v1",
        "state": "MODEL_D_ATTEMPT_NOT_CONSUMED",
        "structure_test_authorized": False,
        "implementation_lock_approved": False,
        "consumed_marker": "metadata/model_d_attempt_consumed.json",
        "rerun_policy": "EXPLICIT_HUMAN_ADJUDICATION_REQUIRED",
    }:
        raise AnalysisBlocker("attempt guard definition/state differs from implementation lock")
    if ATTEMPT_MARKER.exists():
        raise AnalysisBlocker("locked Model D attempt is already consumed")
    return {
        "status": "PREFLIGHT_PASS_NO_STRUCTURE_ACCESS_NO_FIT",
        "rows": len(cohort),
        "clusters": int(folds["sequence_cluster_id"].nunique()),
        "annotation_rows": len(annotation),
        "model_c_rows": len(model_c),
        "historical_model_c_oof_rows": len(historical_oof),
        "environment": environment,
        "structure_inputs_read": False,
        "structure_features_computed": False,
        "structure_outcome_tests": 0,
        "c_annotation_real_fits": 0,
        "c_quality_real_fits": 0,
        "model_d_fits": 0,
        "real_data_permutations": 0,
        "real_data_sensitivities": 0,
        "longbench_inputs_read": False,
        "model_d_attempt_consumed": False,
        "structure_test_authorized": False,
    }


def require_execution_authorization(manifest: dict) -> tuple[str, str]:
    if not AUTHORIZATION.is_file():
        raise AnalysisBlocker("separate human execution authorization is absent")
    authorization = load_json(AUTHORIZATION)
    required_true = (
        "implementation_lock_committed", "implementation_lock_pushed",
        "implementation_lock_human_reviewed", "implementation_lock_approved",
        "structure_test_authorized",
    )
    if any(authorization.get(key) is not True for key in required_true):
        raise AnalysisBlocker("implementation lock is not fully approved for structure access")
    commit = authorization.get("approved_implementation_lock_commit")
    if not isinstance(commit, str) or len(commit) != 40:
        raise AnalysisBlocker("approved implementation-lock commit is invalid")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    origin = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=ROOT,
                                     text=True).strip()
    if head != commit or origin != commit:
        raise AnalysisBlocker("approved implementation-lock commit is not local and origin/main HEAD")
    if authorization.get("scientific_lock_commit") != manifest["scientific_lock_commit"]:
        raise AnalysisBlocker("authorization names a different scientific lock")
    mapping_sha = authorization.get("class_a_mapping_sha256")
    if (not isinstance(mapping_sha, str) or len(mapping_sha) != 64
            or any(character not in "0123456789abcdef" for character in mapping_sha)):
        raise AnalysisBlocker("authorization does not pin the class-A mapping SHA256")
    return commit, mapping_sha


def consume_attempt(approved_commit: str) -> None:
    ATTEMPT_MARKER.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "state": "MODEL_D_ATTEMPT_CONSUMED_NO_AUTOMATIC_RERUN",
        "consumed_utc": datetime.now(timezone.utc).isoformat(),
        "approved_implementation_lock_commit": approved_commit,
    }
    try:
        with ATTEMPT_MARKER.open("x") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise AnalysisBlocker("locked Model D attempt is already consumed") from error


def deterministic_gzip_tsv(frame: pd.DataFrame, path: Path) -> None:
    buffer = io.StringIO(newline="")
    frame.to_csv(buffer, sep="\t", index=False, lineterminator="\n",
                 float_format="%.17g")
    path.write_bytes(gzip.compress(buffer.getvalue().encode(), mtime=0))


def oof_frame(base: pd.DataFrame, pred: np.ndarray, probability: np.ndarray) -> pd.DataFrame:
    output = base[["stable_id", "fold", "sequence_cluster_id", "label"]].copy()
    output["pred"] = pred
    for index, column in enumerate(PROBABILITY_COLUMNS):
        output[column] = probability[:, index]
    return output


def execute() -> dict:
    manifest = load_json(MANIFEST)
    verify_frozen_files(manifest)
    verify_environment()
    for path in (STRUCTURE, MAPPING, AUTHORIZATION):
        reject_longbench_path(path)
    approved_commit, approved_mapping_sha = require_execution_authorization(manifest)
    if STRUCTURE != ROOT / ".cache/phase3b/structure/GSE132099_icSHAPE_invivo.out.txt.gz":
        raise AnalysisBlocker("unexpected structure resource identity")
    if MAPPING != ROOT / ".cache/model_d/class_a_mapping.tsv":
        raise AnalysisBlocker("unexpected class-A mapping resource identity")

    # Exhaust structure-blind failures before spending the single scientific attempt.
    # The mapping is authorization metadata, not the biological structure-value file.
    if not MAPPING.is_file():
        raise AnalysisBlocker("class-A mapping resource is missing")
    if sha256(MAPPING) != approved_mapping_sha:
        raise AnalysisBlocker("class-A mapping resource differs from authorized SHA256")
    if not STRUCTURE.is_file():
        raise AnalysisBlocker("structure resource is missing")
    if STRUCTURE.stat().st_size != EXPECTED_STRUCTURE_BYTES:
        raise AnalysisBlocker("structure resource byte size differs from lock")

    cohort, folds, model_c, annotation, historical_oof = read_locked_inputs()
    if ATTEMPT_MARKER.exists():
        raise AnalysisBlocker("locked Model D attempt is already consumed")

    # This durable marker is the final structure-blind operation.  The very next
    # operation reads the first real structure-file bytes to verify its SHA256.
    consume_attempt(approved_commit)
    if sha256(STRUCTURE) != EXPECTED_STRUCTURE_SHA256:
        raise AnalysisBlocker("unexpected structure-resource SHA256")

    frozen_ids = cohort["stable_id"].astype(str).tolist()
    mappings = parse_mapping_tsv(MAPPING, frozen_ids)
    with gzip.open(STRUCTURE, "rt") as handle:
        structure = parse_structure_stream(handle, mappings)
    if structure["stable_id"].tolist() != frozen_ids:
        raise AnalysisBlocker("parsed structure rows do not preserve frozen cohort order")
    data = model_c.merge(annotation, on="stable_id", validate="one_to_one", sort=False)
    data = data.merge(structure, on="stable_id", validate="one_to_one", sort=False)
    if data["stable_id"].tolist() != frozen_ids or len(data) != 15_999:
        raise AnalysisBlocker("future execution join changed the frozen cohort")

    c_annotation_pred, c_annotation_prob, c_annotation_fits = fit_oof(
        data, C_ANNOTATION_FEATURES)
    c_quality_pred, c_quality_prob, c_quality_fits = fit_oof(data, C_QUALITY_FEATURES)
    d_structure_pred, d_structure_prob, d_structure_fits = fit_oof(data, D_STRUCTURE_FEATURES)

    y = data["label"].astype(str).to_numpy()
    historical_prob = historical_oof[list(PROBABILITY_COLUMNS)].to_numpy(dtype=np.float64)
    historical_metrics = all_metrics(y, historical_oof["pred"].astype(str), historical_prob)
    c_metrics = all_metrics(y, c_quality_pred, c_quality_prob)
    d_metrics = all_metrics(y, d_structure_pred, d_structure_prob)
    delta = float(d_metrics["macro_f1"] - c_metrics["macro_f1"])
    folds_result = fold_macro_f1_deltas(y, c_quality_pred, d_structure_pred, data["fold"])
    bootstrap = paired_cluster_bootstrap(
        y, c_quality_pred, d_structure_pred, data["sequence_cluster_id"],
        replicates=5000, seed=20260924)
    bootstrap_ci = bootstrap_interval(bootstrap)

    permutable_rows, fixed_rows = permutation_row_counts(data)
    if (permutable_rows, fixed_rows) != (15_217, 782):
        raise AnalysisBlocker("negative-control stratum counts differ from scientific lock")
    permutations = run_negative_control(
        data, c_quality_pred, permutations=1000, seed=20260925)
    permutation_95 = float(np.quantile(permutations, 0.95, method="linear"))
    permutation_tail_fraction = float((1 + np.sum(permutations >= delta)) / 1001)

    strict = strict_callability_subset(data)
    strict_c_pred, strict_c_prob, strict_c_fits = fit_oof(strict, C_QUALITY_FEATURES)
    strict_d_pred, strict_d_prob, strict_d_fits = fit_oof(strict, D_STRUCTURE_FEATURES)
    strict_delta = macro_f1(strict["label"], strict_d_pred) - macro_f1(
        strict["label"], strict_c_pred)
    strict_bootstrap = paired_cluster_bootstrap(
        strict["label"], strict_c_pred, strict_d_pred, strict["sequence_cluster_id"],
        replicates=5000, seed=20260924)
    strict_ci = bootstrap_interval(strict_bootstrap)

    c_f1 = per_class_f1(y, c_quality_pred)
    d_f1 = per_class_f1(y, d_structure_pred)
    decision = central_decision(
        validity=True,
        delta_macro_f1=delta,
        paired_bootstrap_ci_lower=bootstrap_ci[0],
        permutation_95th_percentile=permutation_95,
        fold_deltas=[row["delta"] for row in folds_result],
        strict_callability_delta=strict_delta,
        direct_rna_only_delta_f1=d_f1["DIRECT_RNA_ONLY"] - c_f1["DIRECT_RNA_ONLY"],
        indeterminate_delta_f1=d_f1["INDETERMINATE"] - c_f1["INDETERMINATE"],
    )

    outputs = {
        "model_d_c_annotation_oof.tsv.gz": oof_frame(data, c_annotation_pred, c_annotation_prob),
        "model_d_c_quality_oof.tsv.gz": oof_frame(data, c_quality_pred, c_quality_prob),
        "model_d_d_structure_oof.tsv.gz": oof_frame(data, d_structure_pred, d_structure_prob),
    }
    for name, frame in outputs.items():
        deterministic_gzip_tsv(frame, OUTPUT_DIR / name)
    result = {
        "primary_comparison": "D_STRUCTURE_minus_C_QUALITY",
        "primary_metric": "pooled_five_fold_oof_macro_f1",
        "delta_macro_f1": delta,
        "c_historical_metrics": historical_metrics,
        "d_minus_c_historical_macro_f1": float(
            d_metrics["macro_f1"] - historical_metrics["macro_f1"]),
        "c_quality_metrics": c_metrics,
        "d_structure_metrics": d_metrics,
        "fold_metrics": folds_result,
        "paired_bootstrap": {
            "replicates": 5000, "seed": 20260924, "ci": bootstrap_ci,
            "interpretation": "conditional transcript-group uncertainty, not biological-replicate uncertainty",
        },
        "negative_control": {
            "classification": "NEGATIVE_CONTROL_CALIBRATION_NOT_FORMAL_CONDITIONAL_INDEPENDENCE_TEST",
            "permutations": 1000, "seed": 20260925,
            "percentile_95": permutation_95,
            "descriptive_upper_tail_fraction": permutation_tail_fraction,
            "permutable_rows": permutable_rows,
            "fixed_rows": fixed_rows,
        },
        "strict_callability": {
            "rows": len(strict), "delta_macro_f1": strict_delta,
            "paired_bootstrap_ci": strict_ci,
        },
        "decision": {
            "conclusion": decision.conclusion,
            "practical_category": decision.practical_category,
            "gates": dict(decision.gates),
            "class_instability": decision.class_instability,
        },
        "fit_records": {
            "C_ANNOTATION": [fit.__dict__ for fit in c_annotation_fits],
            "C_QUALITY": [fit.__dict__ for fit in c_quality_fits],
            "D_STRUCTURE": [fit.__dict__ for fit in d_structure_fits],
            "strict_C_QUALITY": [fit.__dict__ for fit in strict_c_fits],
            "strict_D_STRUCTURE": [fit.__dict__ for fit in strict_d_fits],
        },
        "protocol_deviation": None,
        "model_d_attempt_consumed": True,
    }
    result_path = OUTPUT_DIR / "model_d_locked_results.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(), indent=2))
        return
    try:
        print(json.dumps(execute(), indent=2))
    except Exception as error:
        FAILURE_LOG.parent.mkdir(parents=True, exist_ok=True)
        FAILURE_LOG.write_text(json.dumps({
            "classification": "ANALYSIS_BLOCKER",
            "utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "central_conclusion": "INCONCLUSIVE",
            "automatic_rerun_prohibited": True,
        }, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
