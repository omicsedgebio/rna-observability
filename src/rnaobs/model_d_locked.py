"""Locked Model D implementation primitives.

This module contains no path discovery and performs no I/O at import time.  Real
structure access is reserved for the separately authorized execution entry point.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping, Sequence, TextIO
import csv
import hashlib
import math
import warnings

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


CLASSES = (
    "BOTH",
    "ILLUMINA_ONLY",
    "DIRECT_RNA_ONLY",
    "NEITHER",
    "INDETERMINATE",
)
PROBABILITY_COLUMNS = (
    "p_both",
    "p_illumina_only",
    "p_directrna_only",
    "p_neither",
    "p_indeterminate",
)
HISTORICAL_FEATURES = (
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
ANNOTATION_CONTROLS = (
    "unique_kmer_fraction",
    "unique_kmer_fraction_missing",
    "unique_exonic_bases",
    "shared_exon_fraction",
    "unique_junction_count",
    "max_exon_jaccard",
    "identical_splice_chain_isoforms",
    "incidence_rank_deficiency",
    "mean_exon_length",
    "miniquant_kvalue",
    "miniquant_kvalue_missing",
)
C_ANNOTATION_FEATURES = HISTORICAL_FEATURES + ANNOTATION_CONTROLS
C_QUALITY_FEATURES = C_ANNOTATION_FEATURES + ("callable_fraction",)
D_STRUCTURE_FEATURES = C_QUALITY_FEATURES + ("median_reactivity",)
IMPUTED_FEATURES = ("unique_kmer_fraction", "miniquant_kvalue")
ANNOTATION_MATRIX_COLUMNS = ("stable_id",) + ANNOTATION_CONTROLS


class ProtocolClassification(str, Enum):
    IMPLEMENTATION_REPAIR = "IMPLEMENTATION_REPAIR"
    PROTOCOL_DEVIATION = "PROTOCOL_DEVIATION"
    ANALYSIS_BLOCKER = "ANALYSIS_BLOCKER"


class AnalysisBlocker(RuntimeError):
    """A locked condition requires stopping without scientific substitution."""


PROTOCOL_DEVIATION_DOMAINS = frozenset({
    "source", "mapping", "cohort", "feature_list", "feature_order", "threshold",
    "transformation", "missingness", "comparator", "model", "hyperparameter",
    "fold", "seed", "thread_rule", "metric", "resampling", "sensitivity",
    "decision_rule", "claim_boundary",
})


def classify_protocol_issue(*, demonstrable_code_defect: bool = False,
                            scientific_change_domain: str | None = None,
                            blocker: bool = False) -> ProtocolClassification:
    selections = sum((demonstrable_code_defect, scientific_change_domain is not None, blocker))
    if selections != 1:
        raise ValueError("classify exactly one implementation repair, protocol deviation, or blocker")
    if blocker:
        return ProtocolClassification.ANALYSIS_BLOCKER
    if scientific_change_domain is not None:
        if scientific_change_domain not in PROTOCOL_DEVIATION_DOMAINS:
            raise ValueError("unknown scientific/statistical change domain")
        return ProtocolClassification.PROTOCOL_DEVIATION
    return ProtocolClassification.IMPLEMENTATION_REPAIR


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_annotation_matrix(
    frame: pd.DataFrame,
    frozen_ids: Sequence[str],
    *,
    expected_rows: int = 15_999,
) -> dict[str, int]:
    if list(frame.columns) != list(ANNOTATION_MATRIX_COLUMNS):
        raise AnalysisBlocker("annotation comparator columns or order differ from lock")
    if len(frame) != expected_rows or len(frozen_ids) != expected_rows:
        raise AnalysisBlocker("annotation comparator row count differs from lock")
    if frame["stable_id"].isna().any() or (frame["stable_id"].astype(str) == "").any():
        raise AnalysisBlocker("annotation comparator contains a missing transcript ID")
    if frame["stable_id"].duplicated().any():
        raise AnalysisBlocker("annotation comparator contains duplicate transcript IDs")
    if frame["stable_id"].astype(str).tolist() != list(frozen_ids):
        raise AnalysisBlocker("annotation comparator does not preserve frozen order")

    prohibited = {
        "label", "y", "outcome", "pred", "assay_rpkm", "callable_fraction",
        "median_reactivity", "mean_reactivity", "high_reactivity_fraction",
        "low_reactivity_fraction",
    }
    if prohibited.intersection(frame.columns):
        raise AnalysisBlocker("annotation comparator contains prohibited fields")

    numeric = frame.drop(columns="stable_id").apply(pd.to_numeric, errors="coerce")
    for raw, indicator in (
        ("unique_kmer_fraction", "unique_kmer_fraction_missing"),
        ("miniquant_kvalue", "miniquant_kvalue_missing"),
    ):
        raw_values = numeric[raw].to_numpy(dtype=np.float64)
        expected = (~np.isfinite(raw_values)).astype(np.int64)
        found = numeric[indicator].to_numpy(dtype=np.float64)
        if not np.isfinite(found).all() or not np.isin(found, [0.0, 1.0]).all():
            raise AnalysisBlocker(f"{indicator} is not a complete binary indicator")
        if not np.array_equal(found.astype(np.int64), expected):
            raise AnalysisBlocker(f"{indicator} does not match raw missingness")

    required_finite = [c for c in ANNOTATION_CONTROLS if c not in IMPUTED_FEATURES]
    if not np.isfinite(numeric[required_finite].to_numpy(dtype=np.float64)).all():
        raise AnalysisBlocker("non-imputable annotation control is missing or non-finite")
    return {
        "unique_kmer_fraction_missing": int(numeric["unique_kmer_fraction_missing"].sum()),
        "miniquant_kvalue_missing": int(numeric["miniquant_kvalue_missing"].sum()),
    }


def fold_local_impute(
    train: pd.DataFrame,
    test: pd.DataFrame,
    feature_names: Sequence[str],
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    if list(train.columns) != list(feature_names) or list(test.columns) != list(feature_names):
        raise AnalysisBlocker("model matrix feature order differs from lock")
    train_values = train.to_numpy(dtype=np.float64, copy=True)
    test_values = test.to_numpy(dtype=np.float64, copy=True)
    medians: dict[str, float] = {}
    for feature in IMPUTED_FEATURES:
        if feature not in feature_names:
            continue
        index = list(feature_names).index(feature)
        finite = np.isfinite(train_values[:, index])
        if not finite.any():
            raise AnalysisBlocker(f"empty training-fold imputation basis for {feature}")
        median = float(np.median(train_values[finite, index], overwrite_input=False))
        if not math.isfinite(median):
            raise AnalysisBlocker(f"non-finite training-fold median for {feature}")
        medians[feature] = median
        train_values[~finite, index] = median
        test_values[~np.isfinite(test_values[:, index]), index] = median
    if not np.isfinite(train_values).all() or not np.isfinite(test_values).all():
        raise AnalysisBlocker("predictor other than a locked imputable field is non-finite")
    return train_values, test_values, medians


def scale_training_only(
    train_values: np.ndarray,
    test_values: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    scaler = StandardScaler(with_mean=True, with_std=True)
    scaled_train = scaler.fit_transform(train_values)
    scaled_test = scaler.transform(test_values)
    if not np.isfinite(scaled_train).all() or not np.isfinite(scaled_test).all():
        raise AnalysisBlocker("non-finite output from locked StandardScaler")
    return scaled_train, scaled_test, scaler


def prediction_from_probabilities(probabilities: np.ndarray) -> np.ndarray:
    array = np.asarray(probabilities, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != len(CLASSES):
        raise AnalysisBlocker("probability matrix has wrong class dimension")
    result = []
    for row in array:
        maximum = np.max(row)
        tied = [CLASSES[i] for i, value in enumerate(row) if value == maximum]
        result.append(min(tied))
    return np.asarray(result, dtype=object)


@dataclass(frozen=True)
class FoldFit:
    fold: int
    imputation_medians: Mapping[str, float]
    n_iter: tuple[int, ...]


def fit_oof(
    frame: pd.DataFrame,
    feature_names: Sequence[str],
    *,
    label_column: str = "label",
    fold_column: str = "fold",
) -> tuple[np.ndarray, np.ndarray, list[FoldFit]]:
    expected = {
        tuple(C_ANNOTATION_FEATURES), tuple(C_QUALITY_FEATURES), tuple(D_STRUCTURE_FEATURES)
    }
    if tuple(feature_names) not in expected:
        raise AnalysisBlocker("feature vector is not one of the three locked model vectors")
    if not bool(frame[label_column].isin(CLASSES).all()):
        raise AnalysisBlocker("unexpected outcome class")
    if sorted(pd.unique(frame[fold_column]).tolist()) != [0, 1, 2, 3, 4]:
        raise AnalysisBlocker("outer folds differ from locked 0..4 values")
    y = frame[label_column].astype(str).to_numpy()
    probabilities = np.full((len(frame), len(CLASSES)), np.nan, dtype=np.float64)
    fits: list[FoldFit] = []
    with threadpool_limits(limits=1):
        for fold in range(5):
            train_mask = frame[fold_column].ne(fold).to_numpy()
            test_mask = ~train_mask
            if set(y[train_mask]) != set(CLASSES):
                raise AnalysisBlocker(f"training fold {fold} lacks a required outcome class")
            train, test, medians = fold_local_impute(
                frame.loc[train_mask, feature_names],
                frame.loc[test_mask, feature_names],
                feature_names,
            )
            train, test, _ = scale_training_only(train, test)
            estimator = LogisticRegression(
                C=1.0,
                solver="lbfgs",
                tol=1e-4,
                max_iter=2000,
                random_state=20260923,
                class_weight=None,
                fit_intercept=True,
            )
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ConvergenceWarning)
                estimator.fit(train, y[train_mask])
            if any(issubclass(item.category, ConvergenceWarning) for item in caught):
                raise AnalysisBlocker(f"convergence warning in fold {fold}")
            if np.any(estimator.n_iter_ >= 2000):
                raise AnalysisBlocker(f"n_iter reached locked maximum in fold {fold}")
            raw = estimator.predict_proba(test)
            order = [list(estimator.classes_).index(name) for name in CLASSES]
            probabilities[test_mask, :] = raw[:, order]
            if not np.isfinite(estimator.coef_).all() or not np.isfinite(estimator.intercept_).all():
                raise AnalysisBlocker(f"non-finite fitted parameter in fold {fold}")
            fits.append(FoldFit(fold, medians, tuple(int(x) for x in estimator.n_iter_)))
    if not np.isfinite(probabilities).all():
        raise AnalysisBlocker("non-finite OOF probability")
    if ((probabilities < 0) | (probabilities > 1)).any():
        raise AnalysisBlocker("OOF probability outside [0,1]")
    if not np.allclose(probabilities.sum(axis=1), 1.0, rtol=0.0, atol=1e-12):
        raise AnalysisBlocker("OOF probability row sum exceeds locked tolerance")
    return prediction_from_probabilities(probabilities), probabilities, fits


def _class_counts(y_true: Sequence[str], y_pred: Sequence[str], label: str) -> tuple[int, int, int]:
    truth = np.asarray(y_true, dtype=object)
    pred = np.asarray(y_pred, dtype=object)
    tp = int(np.sum((truth == label) & (pred == label)))
    observed = int(np.sum(truth == label))
    predicted = int(np.sum(pred == label))
    return tp, observed, predicted


def per_class_f1(y_true: Sequence[str], y_pred: Sequence[str]) -> dict[str, float]:
    values: dict[str, float] = {}
    for label in CLASSES:
        tp, observed, predicted = _class_counts(y_true, y_pred, label)
        denominator = observed + predicted
        values[label] = 0.0 if denominator == 0 else float(2 * tp / denominator)
    return values


def macro_f1(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    return float(np.mean(list(per_class_f1(y_true, y_pred).values())))


def corrected_log_loss(y_true: Sequence[str], probabilities: np.ndarray) -> float:
    array = np.asarray(probabilities, dtype=np.float64)
    if array.shape != (len(y_true), len(CLASSES)):
        raise AnalysisBlocker("log-loss probability matrix has wrong shape")
    indices = {label: i for i, label in enumerate(CLASSES)}
    try:
        named = np.asarray([array[row, indices[label]] for row, label in enumerate(y_true)])
    except KeyError as error:
        raise AnalysisBlocker("log loss encountered an unexpected class") from error
    return float(-np.mean(np.log(np.maximum(named, 2.220446049250313e-16))))


def accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    return float(np.mean(np.asarray(y_true, dtype=object) == np.asarray(y_pred, dtype=object)))


def balanced_accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    truth = np.asarray(y_true, dtype=object)
    pred = np.asarray(y_pred, dtype=object)
    recalls = []
    for label in CLASSES:
        observed = int(np.sum(truth == label))
        recalls.append(0.0 if observed == 0 else float(np.sum((truth == label) & (pred == label)) / observed))
    return float(np.mean(recalls))


def multiclass_brier(y_true: Sequence[str], probabilities: np.ndarray) -> float:
    array = np.asarray(probabilities, dtype=np.float64)
    if array.shape != (len(y_true), len(CLASSES)):
        raise AnalysisBlocker("Brier probability matrix has wrong shape")
    indices = {label: i for i, label in enumerate(CLASSES)}
    one_hot = np.zeros_like(array)
    try:
        one_hot[np.arange(len(y_true)), [indices[label] for label in y_true]] = 1.0
    except KeyError as error:
        raise AnalysisBlocker("Brier score encountered an unexpected class") from error
    return float(np.mean(np.sum((array - one_hot) ** 2, axis=1)))


def confusion_matrix_fixed(y_true: Sequence[str], y_pred: Sequence[str]) -> np.ndarray:
    indices = {label: i for i, label in enumerate(CLASSES)}
    matrix = np.zeros((len(CLASSES), len(CLASSES)), dtype=np.int64)
    try:
        for truth, pred in zip(y_true, y_pred, strict=True):
            matrix[indices[truth], indices[pred]] += 1
    except KeyError as error:
        raise AnalysisBlocker("confusion matrix encountered an unexpected class") from error
    return matrix


def all_metrics(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    probabilities: np.ndarray,
) -> dict[str, object]:
    return {
        "macro_f1": macro_f1(y_true, y_pred),
        "corrected_log_loss": corrected_log_loss(y_true, probabilities),
        "accuracy": accuracy(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy(y_true, y_pred),
        "brier_multiclass": multiclass_brier(y_true, probabilities),
        "per_class_f1": per_class_f1(y_true, y_pred),
        "confusion_matrix": confusion_matrix_fixed(y_true, y_pred).tolist(),
    }


def fold_macro_f1_deltas(
    y_true: Sequence[str],
    c_pred: Sequence[str],
    d_pred: Sequence[str],
    folds: Sequence[int],
) -> list[dict[str, float | int]]:
    y = np.asarray(y_true, dtype=object)
    c = np.asarray(c_pred, dtype=object)
    d = np.asarray(d_pred, dtype=object)
    f = np.asarray(folds)
    result = []
    for fold in range(5):
        mask = f == fold
        c_score = macro_f1(y[mask], c[mask])
        d_score = macro_f1(y[mask], d[mask])
        result.append({"fold": fold, "c_quality_macro_f1": c_score,
                       "d_structure_macro_f1": d_score, "delta": d_score - c_score})
    return result


def paired_cluster_bootstrap(
    y_true: Sequence[str],
    c_pred: Sequence[str],
    d_pred: Sequence[str],
    cluster_ids: Sequence[str],
    *,
    replicates: int = 5000,
    seed: int = 20260924,
) -> np.ndarray:
    y = np.asarray(y_true, dtype=object)
    c = np.asarray(c_pred, dtype=object)
    d = np.asarray(d_pred, dtype=object)
    cluster_array = np.asarray(cluster_ids, dtype=object)
    clusters = sorted(set(cluster_array.tolist()))
    rows = {cluster: np.flatnonzero(cluster_array == cluster) for cluster in clusters}
    rng = np.random.Generator(np.random.PCG64(seed))
    deltas = np.empty(replicates, dtype=np.float64)
    for replicate in range(replicates):
        sampled = rng.choice(clusters, size=len(clusters), replace=True)
        indices = np.concatenate([rows[cluster] for cluster in sampled])
        deltas[replicate] = macro_f1(y[indices], d[indices]) - macro_f1(y[indices], c[indices])
    return deltas


def bootstrap_interval(deltas: Sequence[float]) -> tuple[float, float]:
    values = np.asarray(deltas, dtype=np.float64)
    return tuple(float(x) for x in np.quantile(values, [0.025, 0.975], method="linear"))


def permute_median_reactivity_vectors(frame: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    required = {"stable_id", "sequence_cluster_id", "fold", "median_reactivity"}
    if not required.issubset(frame.columns):
        raise AnalysisBlocker("permutation input lacks a locked column")
    if frame["stable_id"].duplicated().any() or not np.isfinite(frame["median_reactivity"]).all():
        raise AnalysisBlocker("permutation input IDs or biological feature are invalid")
    output = frame.copy(deep=True)
    cluster_meta = frame.groupby("sequence_cluster_id", sort=False).agg(
        fold=("fold", "nunique"),
        fold_value=("fold", "first"),
        cluster_size=("stable_id", "size"),
    )
    if (cluster_meta["fold"] != 1).any():
        raise AnalysisBlocker("sequence cluster crosses outer folds")
    strata: dict[tuple[int, int], list[str]] = {}
    for cluster, row in cluster_meta.iterrows():
        strata.setdefault((int(row["fold_value"]), int(row["cluster_size"])), []).append(str(cluster))
    for key in sorted(strata):
        targets = sorted(strata[key])
        sources = list(rng.permutation(targets)) if len(targets) > 1 else targets
        for target, source in zip(targets, sources, strict=True):
            target_rows = frame.index[frame["sequence_cluster_id"].eq(target)].tolist()
            source_rows = frame.index[frame["sequence_cluster_id"].eq(source)].tolist()
            target_rows.sort(key=lambda index: str(frame.at[index, "stable_id"]))
            source_rows.sort(key=lambda index: str(frame.at[index, "stable_id"]))
            if len(target_rows) != len(source_rows):
                raise AnalysisBlocker("permutation stratum contains unequal cluster vectors")
            output.loc[target_rows, "median_reactivity"] = frame.loc[source_rows, "median_reactivity"].to_numpy()
    return output


def permutation_row_counts(frame: pd.DataFrame) -> tuple[int, int]:
    cluster_meta = frame.groupby("sequence_cluster_id", sort=False).agg(
        fold_count=("fold", "nunique"),
        fold=("fold", "first"),
        size=("stable_id", "size"),
    )
    if (cluster_meta["fold_count"] != 1).any():
        raise AnalysisBlocker("sequence cluster crosses outer folds")
    counts = cluster_meta.groupby(["fold", "size"]).size()
    singleton_clusters = set(counts[counts == 1].index)
    fixed = 0
    for _, row in cluster_meta.iterrows():
        if (int(row["fold"]), int(row["size"])) in singleton_clusters:
            fixed += int(row["size"])
    return len(frame) - fixed, fixed


def run_negative_control(
    frame: pd.DataFrame,
    observed_c_quality_pred: Sequence[str],
    *,
    permutations: int = 1000,
    seed: int = 20260925,
) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(seed))
    c_score = macro_f1(frame["label"], observed_c_quality_pred)
    deltas = np.empty(permutations, dtype=np.float64)
    for index in range(permutations):
        permuted = permute_median_reactivity_vectors(frame, rng)
        d_pred, _, _ = fit_oof(permuted, D_STRUCTURE_FEATURES)
        deltas[index] = macro_f1(frame["label"], d_pred) - c_score
    return deltas


def practical_effect_category(delta: float) -> str:
    if delta <= 0:
        return "NO_INCREMENT"
    if delta < 0.005:
        return "NEGLIGIBLE"
    if delta < 0.020:
        return "SMALL"
    return "MEANINGFUL"


@dataclass(frozen=True)
class Decision:
    conclusion: str
    practical_category: str
    gates: Mapping[str, bool]
    class_instability: bool


def central_decision(
    *,
    validity: bool,
    delta_macro_f1: float,
    paired_bootstrap_ci_lower: float,
    permutation_95th_percentile: float,
    fold_deltas: Sequence[float],
    strict_callability_delta: float,
    direct_rna_only_delta_f1: float,
    indeterminate_delta_f1: float,
) -> Decision:
    category = practical_effect_category(delta_macro_f1)
    positive_folds = sum(value > 0 for value in fold_deltas)
    gates = {
        "validity": bool(validity),
        "positive": delta_macro_f1 > 0,
        "statistical": paired_bootstrap_ci_lower > 0,
        "practical": category == "MEANINGFUL",
        "null_calibrated": delta_macro_f1 > permutation_95th_percentile,
        "fold_robust": positive_folds >= 4,
        "partial_magnitude": delta_macro_f1 >= 0.005,
        "partial_fold_robust": positive_folds >= 3,
        "callability_robust": strict_callability_delta > 0,
        "class_stable": (
            direct_rna_only_delta_f1 >= -0.020
            and indeterminate_delta_f1 >= -0.020
        ),
    }
    supported = all(gates[name] for name in (
        "validity", "positive", "statistical", "practical", "null_calibrated",
        "fold_robust", "callability_robust", "class_stable",
    ))
    partial = (
        gates["validity"]
        and gates["partial_magnitude"]
        and gates["null_calibrated"]
        and gates["callability_robust"]
        and gates["partial_fold_robust"]
        and (gates["statistical"] or gates["practical"])
        and not supported
    )
    if not gates["validity"]:
        conclusion = "INCONCLUSIVE"
    elif supported:
        conclusion = "SUPPORTED"
    elif partial:
        conclusion = "PARTIALLY_SUPPORTED"
    else:
        conclusion = "NOT_SUPPORTED"
    return Decision(conclusion, category, gates, not gates["class_stable"])


@dataclass(frozen=True)
class StructureMapping:
    stable_id: str
    structure_transcript_id: str
    mapping_class: str
    reported_length: int


def validate_class_a_mappings(
    mappings: Iterable[StructureMapping],
    frozen_ids: Sequence[str],
) -> dict[str, StructureMapping]:
    result: dict[str, StructureMapping] = {}
    source_ids: set[str] = set()
    for record in mappings:
        if record.mapping_class != "A":
            raise AnalysisBlocker("mapping-policy violation: only class A is allowed")
        if record.stable_id in result or record.structure_transcript_id in source_ids:
            raise AnalysisBlocker("duplicate or ambiguous structure mapping")
        if record.reported_length <= 0:
            raise AnalysisBlocker("mapping contains invalid reported length")
        result[record.stable_id] = record
        source_ids.add(record.structure_transcript_id)
    if set(result) != set(frozen_ids) or len(result) != len(frozen_ids):
        raise AnalysisBlocker("missing or extra mapped record for frozen cohort")
    return result


def parse_mapping_tsv(path: Path, frozen_ids: Sequence[str]) -> dict[str, StructureMapping]:
    required = [
        "stable_id", "structure_transcript_id", "mapping_class", "reported_length",
        "unique_source_stable_id", "processed_length_matches_ensembl88",
        "gene_equal_88_91", "chromosome_equal_88_91", "strand_equal_88_91",
        "exon_intervals_equal_88_91", "transcript_length_equal_88_91",
        "transcript_sequence_equal_88_91",
    ]
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != required:
            raise AnalysisBlocker("mapping TSV schema or column order differs from implementation lock")
        records = []
        for row in reader:
            if any(row[field] != "true" for field in required[4:]):
                raise AnalysisBlocker("mapping-policy evidence does not establish locked class A")
            try:
                length = int(row["reported_length"])
            except (TypeError, ValueError) as error:
                raise AnalysisBlocker("mapping reported_length is invalid") from error
            records.append(StructureMapping(row["stable_id"], row["structure_transcript_id"],
                                            row["mapping_class"], length))
    return validate_class_a_mappings(records, frozen_ids)


def parse_structure_stream(
    handle: TextIO,
    mappings: Mapping[str, StructureMapping],
) -> pd.DataFrame:
    by_source = {record.structure_transcript_id: record for record in mappings.values()}
    if len(by_source) != len(mappings):
        raise AnalysisBlocker("ambiguous mapping source IDs")
    found: dict[str, tuple[float, float, int]] = {}
    for line_number, line in enumerate(handle, 1):
        fields = line.rstrip("\n").rstrip("\r").split("\t")
        if len(fields) < 3:
            raise AnalysisBlocker(f"structure row {line_number} has fewer than three fields")
        transcript_id = fields[0]
        if transcript_id in found:
            raise AnalysisBlocker("duplicate structure transcript record")
        record = by_source.get(transcript_id)
        if record is None:
            continue
        try:
            reported_length = int(fields[1])
            assay_rpkm = np.float64(fields[2])
        except (TypeError, ValueError) as error:
            raise AnalysisBlocker("invalid structure length or assay_rpkm") from error
        if not np.isfinite(assay_rpkm):
            raise AnalysisBlocker("non-finite assay_rpkm")
        if reported_length != record.reported_length:
            raise AnalysisBlocker("reported structure length differs from class-A mapping")
        positions = fields[3:]
        if len(positions) != reported_length:
            raise AnalysisBlocker("position field count differs from reported length")
        scores: list[np.float64] = []
        for token in positions:
            if token == "NULL":
                continue
            try:
                value = np.float64(token)
            except (TypeError, ValueError) as error:
                raise AnalysisBlocker("non-numeric non-NULL structure score") from error
            if not np.isfinite(value):
                raise AnalysisBlocker("non-finite structure score")
            scores.append(value)
        callable_count = len(scores)
        callable_fraction = np.float64(callable_count) / np.float64(reported_length)
        if callable_count < 50:
            raise AnalysisBlocker("fewer than 50 callable structure positions")
        if callable_fraction < np.float64(0.5):
            raise AnalysisBlocker("structure callable fraction below 0.5")
        median = np.median(np.asarray(scores, dtype=np.float64))
        if not np.isfinite(callable_fraction) or not np.isfinite(median):
            raise AnalysisBlocker("non-finite locked structure feature")
        found[transcript_id] = (float(callable_fraction), float(median), callable_count)
    if set(found) != set(by_source):
        raise AnalysisBlocker("missing mapped structure record")
    rows = []
    for stable_id in mappings:
        record = mappings[stable_id]
        callable_fraction, median, callable_count = found[record.structure_transcript_id]
        rows.append({
            "stable_id": stable_id,
            "callable_fraction": callable_fraction,
            "median_reactivity": median,
            "callable_positions": callable_count,
        })
    return pd.DataFrame(rows, columns=["stable_id", "callable_fraction",
                                      "median_reactivity", "callable_positions"])


def strict_callability_subset(frame: pd.DataFrame) -> pd.DataFrame:
    subset = frame.loc[
        frame["callable_positions"].ge(50) & frame["callable_fraction"].ge(0.75)
    ].copy()
    if subset.empty:
        raise AnalysisBlocker("mandatory strict-callability sensitivity is unavailable")
    for fold in range(5):
        training = subset.loc[subset["fold"].ne(fold), "label"]
        if set(training) != set(CLASSES):
            raise AnalysisBlocker("strict-callability training fold lacks a required class")
    return subset
