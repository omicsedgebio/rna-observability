#!/usr/bin/env python3
"""Fit or verify the one post-development Model C deployment estimator.

The fixed input is the frozen SG-NEx development matrix. This script has no
LongBench, structure, network, download, or arbitrary-path interface. The saved
JSON is transparent estimator state, not a pickle and not a reconstruction of
the historical out-of-fold predictions.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs/model_c_deployment.json"
SCRIPT_PATH = ROOT / "scripts/materialize_model_c_deployment.py"
DEVELOPMENT_FREEZE_COMMIT = "294f59ddab5dc4262d23ebbd976f2cec6469bc71"


class DeploymentError(RuntimeError):
    """A deterministic deployment-estimator invariant failed."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_prediction_hash(
    stable_ids: Sequence[str], classes: Sequence[str], probabilities: np.ndarray
) -> str:
    """Hash deployment outputs in a platform-readable canonical text form."""
    if probabilities.shape != (len(stable_ids), len(classes)):
        raise DeploymentError("prediction matrix shape mismatch")
    labels = np.asarray(classes, dtype=object)[np.argmax(probabilities, axis=1)]
    digest = hashlib.sha256()
    for stable_id, label, row in zip(stable_ids, labels, probabilities):
        fields = [str(stable_id), str(label)] + [format(float(value), ".15g") for value in row]
        digest.update(("\t".join(fields) + "\n").encode("utf-8"))
    return digest.hexdigest()


def predict_from_state(matrix: np.ndarray, state: Mapping[str, object]) -> np.ndarray:
    """Reconstruct ordered class probabilities without scikit-learn objects."""
    scaler = state["standard_scaler"]
    estimator = state["logistic_regression"]
    if not isinstance(scaler, Mapping) or not isinstance(estimator, Mapping):
        raise DeploymentError("invalid estimator state")
    mean = np.asarray(scaler["mean"], dtype=np.float64)
    scale = np.asarray(scaler["scale"], dtype=np.float64)
    coefficients = np.asarray(estimator["coefficients"], dtype=np.float64)
    intercepts = np.asarray(estimator["intercepts"], dtype=np.float64)
    native_classes = list(estimator["coefficient_class_order"])
    output_classes = list(state["output_class_order"])
    values = np.asarray(matrix, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != len(mean):
        raise DeploymentError("feature matrix shape mismatch")
    if not np.isfinite(values).all() or np.any(scale <= 0):
        raise DeploymentError("non-finite feature or invalid scale")
    standardized = (values - mean) / scale
    logits = standardized @ coefficients.T + intercepts
    logits -= logits.max(axis=1, keepdims=True)
    native_probabilities = np.exp(logits)
    native_probabilities /= native_probabilities.sum(axis=1, keepdims=True)
    try:
        order = [native_classes.index(name) for name in output_classes]
    except ValueError as exc:
        raise DeploymentError("saved class orders disagree") from exc
    probabilities = native_probabilities[:, order]
    if not np.isfinite(probabilities).all():
        raise DeploymentError("non-finite reconstructed probability")
    return probabilities


def load_config() -> dict[str, object]:
    config = json.loads(CONFIG_PATH.read_text())
    if config["development_freeze_commit"] != DEVELOPMENT_FREEZE_COMMIT:
        raise DeploymentError("development freeze commit changed")
    if config["artifact_label"] != "POST-DEVELOPMENT DEPLOYMENT ESTIMATOR":
        raise DeploymentError("deployment artifact label changed")
    if config["historical_oof_reconstruction"] is not False:
        raise DeploymentError("artifact cannot claim historical OOF reconstruction")
    if config["new_development_evidence"] is not False:
        raise DeploymentError("artifact cannot claim new development evidence")
    for key in ("training_matrix", "cohort", "feature_registry", "model_c_config"):
        path = ROOT / str(config[key])
        if sha256(path) != config[key + "_sha256"]:
            raise DeploymentError(f"frozen input changed: {config[key]}")
    model_c = json.loads((ROOT / str(config["model_c_config"])).read_text())
    if config["features"] != model_c["features"] or config["output_class_order"] != model_c["classes"]:
        raise DeploymentError("feature or class order differs from frozen Model C")
    for key in ("C", "solver", "tol", "max_iter", "class_weight", "fit_intercept", "random_state"):
        source_key = "seed" if key == "random_state" else key
        if config["estimator"][key] != model_c[source_key]:
            raise DeploymentError(f"estimator parameter differs from frozen Model C: {key}")
    expected_environment = config["environment"]
    if platform.python_version() != expected_environment["python"]:
        raise DeploymentError("Python version differs from deployment lock")
    for package in ("numpy", "scipy", "pandas", "scikit-learn", "threadpoolctl"):
        if importlib.metadata.version(package) != expected_environment[package]:
            raise DeploymentError(f"package version differs from deployment lock: {package}")
    return config


def load_training(config: Mapping[str, object]) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    frame = pd.read_csv(ROOT / str(config["training_matrix"]), sep="\t")
    features = list(config["features"])
    required = ["stable_id", "label"] + features
    if any(column not in frame.columns for column in required):
        raise DeploymentError("training matrix is missing a required column")
    if len(frame) != config["training_rows"] or frame.stable_id.duplicated().any():
        raise DeploymentError("training cohort row count or uniqueness changed")
    cohort = pd.read_csv(ROOT / str(config["cohort"]), sep="\t")
    if frame.stable_id.tolist() != cohort.stable_id.tolist():
        raise DeploymentError("training matrix order differs from frozen cohort")
    matrix = frame[features].to_numpy(dtype=np.float64)
    labels = frame.label.to_numpy(dtype=str)
    if not np.isfinite(matrix).all():
        raise DeploymentError("training features are not complete and finite")
    if set(labels) != set(config["output_class_order"]):
        raise DeploymentError("training classes differ from frozen Model C")
    if "sample_weight" in frame and not np.all(frame.sample_weight.to_numpy() == 1.0):
        raise DeploymentError("unexpected non-unit sample weight")
    return frame, matrix, labels


def verify_saved() -> dict[str, object]:
    config = load_config()
    outputs = config["outputs"]
    state_path = ROOT / str(outputs["state"])
    receipt_path = ROOT / str(outputs["receipt"])
    attempt_path = ROOT / str(outputs["attempt"])
    for path in (state_path, receipt_path, attempt_path):
        if not path.is_file():
            raise DeploymentError(f"missing deployment artifact: {path.relative_to(ROOT)}")
    state = json.loads(state_path.read_text())
    receipt = json.loads(receipt_path.read_text())
    frame, matrix, _ = load_training(config)
    probabilities = predict_from_state(matrix, state)
    prediction_hash = canonical_prediction_hash(
        frame.stable_id.astype(str).tolist(), state["output_class_order"], probabilities
    )
    checks = {
        "state_sha256": sha256(state_path),
        "attempt_sha256": sha256(attempt_path),
        "prediction_sha256": prediction_hash,
    }
    for key, actual in checks.items():
        if receipt[key] != actual:
            raise DeploymentError(f"saved deployment verification failed: {key}")
    if state["training_rows"] != 15999 or state["longbench_inputs_read"] is not False:
        raise DeploymentError("saved deployment scope changed")
    return {
        "status": "VERIFIED_POST_DEVELOPMENT_DEPLOYMENT_ESTIMATOR",
        "training_rows": len(frame),
        "features": list(config["features"]),
        "output_class_order": list(state["output_class_order"]),
        "state_sha256": checks["state_sha256"],
        "prediction_sha256": prediction_hash,
        "longbench_inputs_read": False,
        "model_d_rerun": False,
    }


def fit_once() -> None:
    config = load_config()
    outputs = config["outputs"]
    state_path = ROOT / str(outputs["state"])
    receipt_path = ROOT / str(outputs["receipt"])
    attempt_path = ROOT / str(outputs["attempt"])
    for path in (state_path, receipt_path, attempt_path):
        if path.exists():
            raise DeploymentError(f"deployment attempt/output already exists: {path.relative_to(ROOT)}")
    frame, matrix, labels = load_training(config)
    attempt = {
        "status": "DEPLOYMENT_FIT_STARTED_NO_AUTOMATIC_RETRY",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "development_freeze_commit": DEVELOPMENT_FREEZE_COMMIT,
        "artifact_label": config["artifact_label"],
        "historical_oof_reconstruction": False,
        "new_development_evidence": False,
        "longbench_inputs_read": False,
        "model_d_rerun": False,
    }
    with attempt_path.open("x") as handle:
        json.dump(attempt, handle, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    estimator_config = config["estimator"]
    with threadpool_limits(limits=1):
        scaler = StandardScaler(with_mean=True, with_std=True)
        standardized = scaler.fit_transform(matrix)
        estimator = LogisticRegression(
            C=estimator_config["C"],
            solver=estimator_config["solver"],
            tol=estimator_config["tol"],
            max_iter=estimator_config["max_iter"],
            class_weight=estimator_config["class_weight"],
            fit_intercept=estimator_config["fit_intercept"],
            random_state=estimator_config["random_state"],
        )
        estimator.fit(standardized, labels)
        native_probabilities = estimator.predict_proba(standardized)
    if np.any(estimator.n_iter_ >= estimator_config["max_iter"]):
        raise DeploymentError("deployment estimator reached iteration limit")
    output_classes = list(config["output_class_order"])
    native_classes = estimator.classes_.astype(str).tolist()
    order = [native_classes.index(name) for name in output_classes]
    ordered_probabilities = native_probabilities[:, order]
    state = {
        "schema_version": 1,
        "artifact_label": config["artifact_label"],
        "historical_oof_reconstruction": False,
        "new_development_evidence": False,
        "development_freeze_commit": DEVELOPMENT_FREEZE_COMMIT,
        "training_matrix_sha256": config["training_matrix_sha256"],
        "training_rows": len(frame),
        "feature_order": list(config["features"]),
        "output_class_order": output_classes,
        "standard_scaler": {
            "with_mean": True,
            "with_std": True,
            "n_samples_seen": int(scaler.n_samples_seen_),
            "mean": scaler.mean_.tolist(),
            "variance": scaler.var_.tolist(),
            "scale": scaler.scale_.tolist(),
        },
        "logistic_regression": {
            "coefficient_class_order": native_classes,
            "coefficients": estimator.coef_.tolist(),
            "intercepts": estimator.intercept_.tolist(),
            "n_iter": estimator.n_iter_.astype(int).tolist(),
            "parameters": {
                "C": estimator_config["C"],
                "solver": estimator_config["solver"],
                "tol": estimator_config["tol"],
                "max_iter": estimator_config["max_iter"],
                "class_weight": estimator_config["class_weight"],
                "fit_intercept": estimator_config["fit_intercept"],
                "random_state": estimator_config["random_state"],
            },
        },
        "longbench_inputs_read": False,
        "model_d_rerun": False,
    }
    reconstructed = predict_from_state(matrix, state)
    if not np.allclose(reconstructed, ordered_probabilities, rtol=1e-13, atol=1e-15):
        raise DeploymentError("transparent state does not reconstruct fitted probabilities")
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    prediction_hash = canonical_prediction_hash(
        frame.stable_id.astype(str).tolist(), output_classes, reconstructed
    )
    receipt = {
        "schema_version": 1,
        "status": "FROZEN_POST_DEVELOPMENT_DEPLOYMENT_ESTIMATOR",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_label": config["artifact_label"],
        "historical_oof_reconstruction": False,
        "new_development_evidence": False,
        "development_freeze_commit": DEVELOPMENT_FREEZE_COMMIT,
        "training_rows": len(frame),
        "training_input_sha256": config["training_matrix_sha256"],
        "config_sha256": sha256(CONFIG_PATH),
        "script_sha256": sha256(SCRIPT_PATH),
        "state_sha256": sha256(state_path),
        "attempt_sha256": sha256(attempt_path),
        "prediction_sha256": prediction_hash,
        "features": list(config["features"]),
        "output_class_order": output_classes,
        "coefficient_class_order": native_classes,
        "environment": {
            "python": platform.python_version(),
            **{
                package: importlib.metadata.version(package)
                for package in ("numpy", "scipy", "pandas", "scikit-learn", "threadpoolctl")
            },
        },
        "fit_attempts": 1,
        "selection_or_tuning": False,
        "development_metrics_computed": False,
        "longbench_inputs_read": False,
        "longbench_predictions_computed": False,
        "longbench_metrics_computed": False,
        "model_d_rerun": False,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(verify_saved(), indent=2))


def main() -> None:
    if sys.argv[1:] == ["--verify"]:
        print(json.dumps(verify_saved(), indent=2))
        return
    if sys.argv[1:]:
        raise DeploymentError("only the fixed fit invocation or --verify is allowed")
    fit_once()


if __name__ == "__main__":
    main()
