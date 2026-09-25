"""Fail-closed, outcome-blind LongBench external-validation lock helpers.

This module deliberately has no download, network, bucket-listing, or LongBench
data-reading function.  It validates the planning artifacts and provides small
pure functions that can be tested with synthetic values before any data-access
authorization exists.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = ROOT / "configs/longbench_external_validation_lock.json"
MANIFEST_PATH = ROOT / "metadata/longbench_external_validation_manifest.json"
AUDIT_PATH = ROOT / "metadata/longbench_compatibility_audit.tsv"

DEVELOPMENT_FREEZE_COMMIT = "294f59ddab5dc4262d23ebbd976f2cec6469bc71"
SCIENTIFIC_LOCK_COMMIT = "ea1dd05a992b92becc66e1cb825a821e48798923"
IMPLEMENTATION_LOCK_COMMIT = "ba9516ecea7dcfea5d216c2560f591638c874e13"
DEPLOYMENT_ESTIMATOR_COMMIT = "936ba5b33cc22b0eeae18bbfb7d93e63bce6358a"

CLASSES = (
    "BOTH",
    "ILLUMINA_ONLY",
    "DIRECT_RNA_ONLY",
    "NEITHER",
    "INDETERMINATE",
)
FEATURES = (
    "independent_abundance_log1p",
    "sequence_length",
    "gc_fraction",
    "exon_count",
    "isoforms_per_gene",
    "sequence_cluster_size",
    "homopolymer_fraction",
    "low_complexity_fraction",
    "sequence_entropy",
)
AUDIT_CLASSES = {"PASS", "CONDITIONAL_PASS", "BLOCKER", "UNKNOWN"}
REQUIRED_RELEASE_CONDITIONS = {
    "development_conclusion_frozen_and_committed",
    "external_validation_objective_human_approved_and_committed",
    "exact_validation_code_config_environment_hashed_and_committed",
    "independent_study_inclusion_manifest_complete_and_committed",
    "outcomes_blind_compatibility_audit_all_required_items_resolved",
    "compatibility_audit_human_approved",
    "annotation_and_transcript_mapping_policy_implemented_and_frozen",
    "exact_reference_frozen",
    "feature_order_and_preprocessing_frozen_and_committed",
    "inclusion_rules_frozen_and_committed",
    "prediction_before_scoring_workflow_implemented_and_frozen",
    "full_development_model_and_preprocessing_state_serialized_hashed_and_committed",
    "acquisition_size_purpose_alternatives_and_necessity_recorded",
    "human_review_complete",
    "reviewer2_review_complete",
    "explicit_human_feature_access_authorization_present",
    "explicit_human_scoring_authorization_present",
}
AUDIT_COLUMNS = (
    "item",
    "classification",
    "program_scope",
    "permitted_evidence",
    "release_effect",
)


class ExternalValidationLockError(RuntimeError):
    """A planning invariant or release condition failed."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def workflow_detection_v1(
    illumina_tpm: Sequence[float], direct_rna_tpm: Sequence[float]
) -> str:
    """Construct the frozen five-class phenotype from synthetic/permitted data.

    Exact transport requires two Illumina outcome preparations and four ONT
    direct-RNA outcome preparations.  Missing, negative, non-finite, or extra
    values fail closed rather than changing the endpoint.
    """
    import math

    if len(illumina_tpm) != 2 or len(direct_rna_tpm) != 4:
        raise ExternalValidationLockError(
            "workflow_detection_v1 requires exactly 2 Illumina and 4 direct-RNA values"
        )
    values = tuple(illumina_tpm) + tuple(direct_rna_tpm)
    if any(not math.isfinite(float(value)) or float(value) < 0 for value in values):
        raise ExternalValidationLockError("TPM values must be finite and non-negative")
    illumina_support = sum(float(value) >= 1.0 for value in illumina_tpm)
    direct_rna_support = sum(float(value) >= 1.0 for value in direct_rna_tpm)
    illumina_positive = illumina_support == 2
    direct_rna_positive = direct_rna_support >= 3
    illumina_intermediate = illumina_support == 1
    direct_rna_intermediate = direct_rna_support in (1, 2)
    if illumina_intermediate or direct_rna_intermediate:
        return "INDETERMINATE"
    if illumina_positive and direct_rna_positive:
        return "BOTH"
    if illumina_positive:
        return "ILLUMINA_ONLY"
    if direct_rna_positive:
        return "DIRECT_RNA_ONLY"
    return "NEITHER"


def prediction_before_scoring_transition(state: str, event: str) -> str:
    """Pure state machine enforcing prediction hashing before label exposure."""
    transitions = {
        ("PLANNING_LOCKED", "AUTHORIZE_FEATURE_ONLY_ACCESS"): "FEATURE_ONLY_ACCESS_AUTHORIZED",
        ("FEATURE_ONLY_ACCESS_AUTHORIZED", "HASH_PREDICTIONS"): "PREDICTIONS_HASHED",
        ("PREDICTIONS_HASHED", "AUTHORIZE_LABEL_ACCESS"): "LABEL_ACCESS_AUTHORIZED",
        ("LABEL_ACCESS_AUTHORIZED", "SCORE_ONCE"): "SCORED_ONCE",
    }
    try:
        return transitions[(state, event)]
    except KeyError as exc:
        raise ExternalValidationLockError(
            f"forbidden validation transition: {state} + {event}"
        ) from exc


def validate_audit_rows(rows: Iterable[Mapping[str, str]]) -> list[dict[str, str]]:
    materialized = [dict(row) for row in rows]
    if not materialized:
        raise ExternalValidationLockError("compatibility audit is empty")
    seen: set[str] = set()
    for row in materialized:
        if tuple(row) != AUDIT_COLUMNS:
            raise ExternalValidationLockError("compatibility audit column order changed")
        item = row["item"]
        if not item or item in seen:
            raise ExternalValidationLockError("compatibility audit item is empty or duplicated")
        seen.add(item)
        if row["classification"] not in AUDIT_CLASSES:
            raise ExternalValidationLockError("invalid compatibility classification")
        if row["program_scope"] not in {"C_D_REQUIRED", "A_B_ONLY", "SEPARATE_OBJECTIVE"}:
            raise ExternalValidationLockError("invalid compatibility program scope")
        if not row["permitted_evidence"] or not row["release_effect"]:
            raise ExternalValidationLockError("compatibility evidence/effect cannot be empty")
    return materialized


def read_audit(path: Path = AUDIT_PATH) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != AUDIT_COLUMNS:
            raise ExternalValidationLockError("compatibility audit has wrong header")
        return validate_audit_rows(reader)


def validate_lock_document(lock: Mapping[str, object]) -> None:
    if lock.get("status") != "LOCK_CANDIDATE_NOT_AUTHORIZED":
        raise ExternalValidationLockError("candidate must remain not authorized")
    if lock.get("development_freeze_commit") != DEVELOPMENT_FREEZE_COMMIT:
        raise ExternalValidationLockError("development freeze commit changed")
    if lock.get("scientific_lock_commit") != SCIENTIFIC_LOCK_COMMIT:
        raise ExternalValidationLockError("scientific lock commit changed")
    if lock.get("repaired_implementation_lock_commit") != IMPLEMENTATION_LOCK_COMMIT:
        raise ExternalValidationLockError("implementation lock commit changed")
    frozen = lock.get("frozen_development_conclusion", {})
    expected_frozen = {
        "model_d": "NOT_SUPPORTED",
        "practical_magnitude": "NEGLIGIBLE",
        "primary_delta_macro_f1": 0.0009736264857591603,
        "paired_bootstrap_interval": [
            -0.0023443180806064804,
            0.004123505221307526,
        ],
        "negative_control_95th_percentile": 0.0015090734133574142,
        "strict_callability_delta": 0.0007399110130869024,
        "strict_callability_bootstrap_interval": [
            -0.0034377341044534047,
            0.004809181103569267,
        ],
        "immutable_under_external_validation": True,
    }
    if frozen != expected_frozen:
        raise ExternalValidationLockError("frozen Model D conclusion changed")
    decision = lock.get("scientific_decision", {})
    if not isinstance(decision, Mapping):
        raise ExternalValidationLockError("scientific decision is missing")
    if decision.get("incremental_structure_hypothesis") != "EXCLUDED":
        raise ExternalValidationLockError("LongBench must not validate Model D")
    if decision.get("structure_feature_reproducibility") != "EXCLUDED":
        raise ExternalValidationLockError("unmatched structure cannot be called reproducibility")
    phenotype = lock.get("phenotype", {})
    if not isinstance(phenotype, Mapping):
        raise ExternalValidationLockError("phenotype lock is missing")
    if tuple(phenotype.get("classes", ())) != CLASSES:
        raise ExternalValidationLockError("class order changed")
    if phenotype.get("threshold_tpm") != 1.0:
        raise ExternalValidationLockError("phenotype threshold changed")
    if phenotype.get("illumina_outcome_preparations") != 2:
        raise ExternalValidationLockError("Illumina support rule changed")
    if phenotype.get("direct_rna_outcome_preparations") != 4:
        raise ExternalValidationLockError("direct-RNA support rule changed")
    model = lock.get("model_policy", {})
    if not isinstance(model, Mapping):
        raise ExternalValidationLockError("model policy is missing")
    if tuple(model.get("features", ())) != FEATURES:
        raise ExternalValidationLockError("Model C feature order changed")
    if model.get("validation_refit_allowed") is not False:
        raise ExternalValidationLockError("validation refitting must be prohibited")
    if model.get("current_serialized_estimator_present") is not True:
        raise ExternalValidationLockError("deployment estimator is not pinned")
    if model.get("deployment_estimator_commit") != DEPLOYMENT_ESTIMATOR_COMMIT:
        raise ExternalValidationLockError("deployment estimator commit changed")
    conditions = lock.get("release_conditions", {})
    if not isinstance(conditions, Mapping) or set(conditions) != REQUIRED_RELEASE_CONDITIONS:
        raise ExternalValidationLockError("release-condition schema changed")
    if conditions.get("development_conclusion_frozen_and_committed") is not True:
        raise ExternalValidationLockError("development freeze must remain satisfied")
    if conditions.get("reviewer2_review_complete") is not True:
        raise ExternalValidationLockError("candidate Reviewer 2 review must be complete")
    if any(
        conditions.get(key) is not False
        for key in (
            "human_review_complete",
            "explicit_human_feature_access_authorization_present",
            "explicit_human_scoring_authorization_present",
        )
    ):
        raise ExternalValidationLockError("candidate cannot claim review or authorization")
    prohibitions = lock.get("prohibitions", {})
    required_false = (
        "longbench_access_authorized",
        "longbench_outcomes_viewed",
        "longbench_bucket_listed",
        "model_d_rerun_allowed",
        "validation_tuning_allowed",
    )
    if not isinstance(prohibitions, Mapping) or any(
        prohibitions.get(key) is not False for key in required_false
    ):
        raise ExternalValidationLockError("a required prohibition is not false")


def validate_manifest(manifest: Mapping[str, object]) -> None:
    expected = {
        "development_freeze_commit": DEVELOPMENT_FREEZE_COMMIT,
        "scientific_lock_commit": SCIENTIFIC_LOCK_COMMIT,
        "repaired_implementation_lock_commit": IMPLEMENTATION_LOCK_COMMIT,
        "model_d_conclusion": "NOT_SUPPORTED",
        "model_d_practical_magnitude": "NEGLIGIBLE",
        "model_d_attempt_consumed": True,
        "longbench_inputs_read": False,
        "longbench_bucket_listed": False,
        "longbench_outcomes_viewed": False,
        "longbench_access_authorized": False,
        "scoring_authorized": False,
        "serialized_transport_estimator_present": True,
        "serialized_transport_preprocessing_present": True,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ExternalValidationLockError(f"manifest invariant failed: {key}")
    if manifest.get("included_cell_lines") != []:
        raise ExternalValidationLockError("no cell line may be included before audit completion")
    if manifest.get("included_transcripts") != 0:
        raise ExternalValidationLockError("no transcript may be included before authorization")


def current_release_status(root: Path = ROOT) -> dict[str, object]:
    """Validate fixed planning artifacts and report why access remains locked."""
    lock = json.loads((root / LOCK_PATH.relative_to(ROOT)).read_text())
    manifest = json.loads((root / MANIFEST_PATH.relative_to(ROOT)).read_text())
    validate_lock_document(lock)
    validate_manifest(manifest)
    audit = read_audit(root / AUDIT_PATH.relative_to(ROOT))

    hash_errors: list[str] = []
    for group in (
        "artifact_sha256",
        "containment_artifact_sha256",
        "deployment_artifact_sha256",
        "frozen_development_artifact_sha256",
        "governance_source_sha256",
        "public_preparation_artifact_sha256",
    ):
        values = manifest.get(group, {})
        if not isinstance(values, Mapping) or not values:
            raise ExternalValidationLockError(f"manifest hash group missing: {group}")
        for rel, expected in values.items():
            path = root / str(rel)
            if not path.is_file() or sha256(path) != expected:
                hash_errors.append(str(rel))

    conditions = lock.get("release_conditions", {})
    if not isinstance(conditions, Mapping):
        raise ExternalValidationLockError("release conditions missing")
    unmet = [str(name) for name, met in conditions.items() if met is not True]
    blockers = sorted(
        row["item"]
        for row in audit
        if row["program_scope"] == "C_D_REQUIRED"
        and row["classification"] in {"BLOCKER", "UNKNOWN"}
    )
    authorization_paths = (
        root / "metadata/longbench_data_access_authorization.json",
        root / "metadata/longbench_scoring_authorization.json",
    )
    present_authorizations = [str(path.relative_to(root)) for path in authorization_paths if path.exists()]
    authorized = not (unmet or blockers or hash_errors or present_authorizations == [])
    # The candidate itself can never authorize access. A future committed checker
    # must additionally validate signed human authorization artifacts.
    if authorized:
        raise ExternalValidationLockError(
            "candidate checker cannot authorize access; a reviewed implementation lock is required"
        )
    return {
        "status": "LOCKED_RELEASE_CONDITIONS_UNMET",
        "unmet_release_conditions": unmet,
        "compatibility_blockers_or_unknowns": blockers,
        "hash_errors": hash_errors,
        "authorization_artifacts_present": present_authorizations,
        "longbench_access_authorized": False,
    }
