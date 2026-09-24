#!/usr/bin/env python3
"""Materialize the locked class-A mapping without structure-derived inputs.

The mapping's ``reported_length`` is the expected Ensembl 88 reference
transcript length.  The real processed-file reported length is deliberately
unknown here and is compared with this expectation only by the separately
authorized structure parser.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
import json
from pathlib import Path
import sys
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rnaobs.core import fasta_records, read_gtf, stable_id, unique_index
from rnaobs.model_d_locked import (
    AnalysisBlocker,
    CLASS_A_MAPPING_COLUMNS,
    sha256,
)

EXPECTED_ROWS = 15_999
COHORT_SHA256 = "3df267fde7a8bafbaccd0266d55bf4f3ad11c2a18a142db70e49dd3b86a8b7f5"
FOLD_SHA256 = "66cfccce6252a39bda918cd99843cb4415b3af64f2ec4a965a9787234e948c52"
CORE_SHA256 = "42a42d2cba1a3fcf20b77360feed2ef4d84183485a3072a56023556f641b1969"
REFERENCE_SHA256 = {
    "ensembl88_gtf": "ba9cb13686c3a4429724dfd6f6e52df92d1cc59675a4590d4a854f64ce633f46",
    "ensembl88_cdna": "462823cdad614a2a77763004735fb9d4fabf3bb691b57737697208679c26cb86",
    "ensembl88_ncrna": "298925becc19859d420f5fbd70994c72ab82df1aedc94515faf86b000b2157b4",
    "ensembl91_gtf": "1abe442ea2ba90c022545be71c4e7b95b66d45c8c9e4e4ec3788b6be440b598d",
    "ensembl91_cdna": "a7f0022e884826d70e0a151f6c38547aea8d443eaa9653aaf56e698e23109201",
    "ensembl91_ncrna": "0ab3565714f88fb98eb7df7814fe3fed770e2b098d37cd7b83601258f87e75dd",
}
STABLE_ID_RULE = (
    "src/rnaobs/core.py::stable_id removes only a terminal numeric transcript "
    "version and preserves the _PAR_Y suffix"
)
FORBIDDEN_RELATIVE_PATHS = (
    "results/tables/gse132099_structure_inventory.tsv",
    "results/tables/ensembl88_to_91_transcript_bridge.tsv",
    "results/tables/phase3c_reference_bridge.tsv",
    ".cache/phase3b/structure/gse132099_icshape_invivo.out.txt.gz",
)
FORBIDDEN_PATH_TOKENS = ("longbench", "gse303762", "longbench-data")


@dataclass(frozen=True)
class MappingInputs:
    cohort: Path
    folds: Path
    ensembl88_gtf: Path
    ensembl88_fastas: tuple[Path, Path]
    ensembl91_gtf: Path
    ensembl91_fastas: tuple[Path, Path]

    def readable_paths(self) -> tuple[Path, ...]:
        return (
            self.cohort,
            self.folds,
            self.ensembl88_gtf,
            *self.ensembl88_fastas,
            self.ensembl91_gtf,
            *self.ensembl91_fastas,
        )


FIXED_INPUTS = MappingInputs(
    cohort=ROOT / "metadata/final_transcript_cohort.tsv",
    folds=ROOT / "metadata/cv_folds.tsv",
    ensembl88_gtf=ROOT / ".cache/phase3b/references/ensembl88.gtf.gz",
    ensembl88_fastas=(
        ROOT / ".cache/phase3b/references/ensembl88.cdna.fa.gz",
        ROOT / ".cache/phase3b/references/ensembl88.ncrna.fa.gz",
    ),
    ensembl91_gtf=ROOT / ".cache/phase3a/references/ensembl91.gtf.gz",
    ensembl91_fastas=(
        ROOT / ".cache/phase3a/references/ensembl91.cdna.fa.gz",
        ROOT / ".cache/phase3a/references/ensembl91.ncrna.fa.gz",
    ),
)
MAPPING_OUTPUT = ROOT / ".cache/model_d/class_a_mapping.tsv"
RECEIPT_OUTPUT = ROOT / "metadata/class_a_mapping_receipt.json"


def reject_prohibited_path(path: Path) -> None:
    """Fail closed if a caller tries to substitute prohibited evidence."""
    lowered = path.as_posix().lower()
    if any(lowered.endswith(item) for item in FORBIDDEN_RELATIVE_PATHS):
        raise AnalysisBlocker(f"structure-derived mapping input is prohibited: {path}")
    if any(token in lowered for token in FORBIDDEN_PATH_TOKENS):
        raise AnalysisBlocker(f"LongBench input is prohibited: {path}")


def verify_structure_blind_paths(inputs: MappingInputs) -> None:
    for path in inputs.readable_paths():
        reject_prohibited_path(path)


def read_ordered_ids(path: Path, *, expected_rows: int) -> list[str]:
    reject_prohibited_path(path)
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or "stable_id" not in reader.fieldnames:
            raise AnalysisBlocker(f"frozen ID table lacks stable_id: {path}")
        ids = [row["stable_id"] for row in reader]
    if len(ids) != expected_rows:
        raise AnalysisBlocker(f"frozen ID row count differs from {expected_rows}: {path}")
    if any(not transcript_id for transcript_id in ids):
        raise AnalysisBlocker(f"frozen ID table contains an empty stable_id: {path}")
    if len(set(ids)) != len(ids):
        raise AnalysisBlocker(f"frozen ID table contains duplicate stable_id values: {path}")
    if any(stable_id(transcript_id) != transcript_id for transcript_id in ids):
        raise AnalysisBlocker(f"frozen ID table contains a versioned transcript ID: {path}")
    return ids


def load_needed_sequences(paths: Iterable[Path], needed: set[str], release: str) -> dict[str, str]:
    sequences: dict[str, str] = {}
    for path in paths:
        reject_prohibited_path(path)
        for transcript_id, sequence in fasta_records(path):
            if transcript_id not in needed:
                continue
            if transcript_id in sequences:
                raise AnalysisBlocker(
                    f"duplicate {release} FASTA transcript ID: {transcript_id}"
                )
            sequences[transcript_id] = sequence.upper()
    missing = sorted(needed.difference(sequences))
    if missing:
        raise AnalysisBlocker(
            f"missing {release} transcript sequence for {missing[0]}"
        )
    return sequences


def _resolve_unique(index: dict[str, list], stable: str, release: str):
    candidates = index.get(stable, [])
    if not candidates:
        raise AnalysisBlocker(f"missing Ensembl {release} transcript for {stable}")
    if len(candidates) != 1:
        raise AnalysisBlocker(f"ambiguous Ensembl {release} stable ID for {stable}")
    return candidates[0]


def build_mapping_rows(
    frozen_ids: Sequence[str],
    *,
    ensembl88_gtf: Path,
    ensembl88_fastas: Iterable[Path],
    ensembl91_gtf: Path,
    ensembl91_fastas: Iterable[Path],
) -> list[dict[str, object]]:
    ensembl88_fastas = tuple(ensembl88_fastas)
    ensembl91_fastas = tuple(ensembl91_fastas)
    for path in (ensembl88_gtf, *ensembl88_fastas, ensembl91_gtf, *ensembl91_fastas):
        reject_prohibited_path(path)
    annotation88 = read_gtf(ensembl88_gtf)
    annotation91 = read_gtf(ensembl91_gtf)
    index88 = unique_index(annotation88.values(), lambda transcript: stable_id(transcript.identifier))
    index91 = unique_index(annotation91.values(), lambda transcript: stable_id(transcript.identifier))

    resolved = []
    for stable in frozen_ids:
        source = _resolve_unique(index88, stable, "88")
        target = _resolve_unique(index91, stable, "91")
        if source.identifier != target.identifier:
            raise AnalysisBlocker(
                f"locked class A requires identical versioned transcript IDs for {stable}"
            )
        resolved.append((stable, source, target))

    needed88 = {source.identifier for _, source, _ in resolved}
    needed91 = {target.identifier for _, _, target in resolved}
    sequences88 = load_needed_sequences(ensembl88_fastas, needed88, "88")
    sequences91 = load_needed_sequences(ensembl91_fastas, needed91, "91")

    rows: list[dict[str, object]] = []
    for stable, source, target in resolved:
        if source.gene != target.gene:
            raise AnalysisBlocker(f"Ensembl 88/91 gene inequality for {stable}")
        if source.chrom != target.chrom:
            raise AnalysisBlocker(f"Ensembl 88/91 chromosome inequality for {stable}")
        if source.strand != target.strand:
            raise AnalysisBlocker(f"Ensembl 88/91 strand inequality for {stable}")
        if source.length != target.length:
            raise AnalysisBlocker(f"Ensembl 88/91 transcript length inequality for {stable}")
        if source.exons != target.exons:
            raise AnalysisBlocker(f"Ensembl 88/91 exon interval inequality for {stable}")
        sequence88 = sequences88[source.identifier]
        sequence91 = sequences91[target.identifier]
        if len(sequence88) != source.length:
            raise AnalysisBlocker(f"Ensembl 88 annotation/sequence length mismatch for {stable}")
        if len(sequence91) != target.length:
            raise AnalysisBlocker(f"Ensembl 91 annotation/sequence length mismatch for {stable}")
        if sequence88 != sequence91:
            raise AnalysisBlocker(f"Ensembl 88/91 transcript sequence inequality for {stable}")
        rows.append({
            "stable_id": stable,
            "structure_transcript_id": stable,
            "mapping_class": "A",
            "reported_length": source.length,
            "unique_source_stable_id": "true",
            "gene_equal_88_91": "true",
            "chromosome_equal_88_91": "true",
            "strand_equal_88_91": "true",
            "exon_intervals_equal_88_91": "true",
            "transcript_length_equal_88_91": "true",
            "transcript_sequence_equal_88_91": "true",
        })
    return rows


def validate_mapping_rows(
    rows: Sequence[dict[str, object]],
    frozen_ids: Sequence[str],
    *,
    expected_rows: int,
) -> dict[str, int]:
    if len(frozen_ids) != expected_rows or len(rows) != expected_rows:
        raise AnalysisBlocker("class-A mapping does not have the exact required row count")
    if any(list(row) != list(CLASS_A_MAPPING_COLUMNS) for row in rows):
        raise AnalysisBlocker("class-A mapping columns or order differ from lock")
    mapped_ids = [str(row["stable_id"]) for row in rows]
    structure_ids = [str(row["structure_transcript_id"]) for row in rows]
    duplicate_stable = len(mapped_ids) - len(set(mapped_ids))
    duplicate_structure = len(structure_ids) - len(set(structure_ids))
    if duplicate_stable:
        raise AnalysisBlocker("duplicate stable_id in class-A mapping")
    if duplicate_structure:
        raise AnalysisBlocker("duplicate structure_transcript_id in class-A mapping")
    missing = set(frozen_ids).difference(mapped_ids)
    extra = set(mapped_ids).difference(frozen_ids)
    if missing or extra or mapped_ids != list(frozen_ids):
        raise AnalysisBlocker("class-A mapping is missing, extra, or out of frozen order")
    for row in rows:
        if row["mapping_class"] != "A":
            raise AnalysisBlocker("non-class-A row in class-A mapping")
        if any(row[column] != "true" for column in CLASS_A_MAPPING_COLUMNS[4:]):
            raise AnalysisBlocker("class-A reference evidence is not literal true")
        if not isinstance(row["reported_length"], int) or row["reported_length"] <= 0:
            raise AnalysisBlocker("invalid Ensembl 88 expected transcript length")
    return {
        "n_frozen_transcripts": len(frozen_ids),
        "n_mapped": len(rows),
        "n_missing": len(missing),
        "n_extra": len(extra),
        "n_duplicate_stable_id": duplicate_stable,
        "n_duplicate_structure_transcript_id": duplicate_structure,
    }


def write_mapping(path: Path, rows: Sequence[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(CLASS_A_MAPPING_COLUMNS),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def verify_fixed_input_hashes(inputs: MappingInputs) -> dict[str, str]:
    expected = {
        inputs.cohort: COHORT_SHA256,
        inputs.folds: FOLD_SHA256,
        inputs.ensembl88_gtf: REFERENCE_SHA256["ensembl88_gtf"],
        inputs.ensembl88_fastas[0]: REFERENCE_SHA256["ensembl88_cdna"],
        inputs.ensembl88_fastas[1]: REFERENCE_SHA256["ensembl88_ncrna"],
        inputs.ensembl91_gtf: REFERENCE_SHA256["ensembl91_gtf"],
        inputs.ensembl91_fastas[0]: REFERENCE_SHA256["ensembl91_cdna"],
        inputs.ensembl91_fastas[1]: REFERENCE_SHA256["ensembl91_ncrna"],
        ROOT / "src/rnaobs/core.py": CORE_SHA256,
    }
    observed: dict[str, str] = {}
    for path, expected_sha in expected.items():
        reject_prohibited_path(path)
        if not path.is_file():
            raise AnalysisBlocker(f"required pinned non-structure input is absent: {path}")
        digest = sha256(path)
        if digest != expected_sha:
            raise AnalysisBlocker(f"pinned non-structure input hash mismatch: {path}")
        observed[path.relative_to(ROOT).as_posix()] = digest
    return observed


def materialize(
    inputs: MappingInputs,
    output: Path,
    *,
    expected_rows: int,
) -> tuple[list[dict[str, object]], dict[str, int]]:
    verify_structure_blind_paths(inputs)
    frozen_ids = read_ordered_ids(inputs.cohort, expected_rows=expected_rows)
    fold_ids = read_ordered_ids(inputs.folds, expected_rows=expected_rows)
    if fold_ids != frozen_ids:
        raise AnalysisBlocker("frozen fold IDs/order differ from frozen cohort")
    rows = build_mapping_rows(
        frozen_ids,
        ensembl88_gtf=inputs.ensembl88_gtf,
        ensembl88_fastas=inputs.ensembl88_fastas,
        ensembl91_gtf=inputs.ensembl91_gtf,
        ensembl91_fastas=inputs.ensembl91_fastas,
    )
    counts = validate_mapping_rows(rows, frozen_ids, expected_rows=expected_rows)
    write_mapping(output, rows)
    return rows, counts


def main() -> None:
    input_hashes = verify_fixed_input_hashes(FIXED_INPUTS)
    _, counts = materialize(FIXED_INPUTS, MAPPING_OUTPUT, expected_rows=EXPECTED_ROWS)
    receipt = {
        "receipt_version": "class_a_mapping_structure_blind_v1",
        "generator_path": "scripts/materialize_class_a_mapping.py",
        "generator_sha256": sha256(Path(__file__)),
        "frozen_cohort_path": "metadata/final_transcript_cohort.tsv",
        "frozen_cohort_sha256": input_hashes["metadata/final_transcript_cohort.tsv"],
        "frozen_fold_path": "metadata/cv_folds.tsv",
        "frozen_fold_sha256": input_hashes["metadata/cv_folds.tsv"],
        "ensembl88_resource_sha256": {
            "gtf": input_hashes[".cache/phase3b/references/ensembl88.gtf.gz"],
            "cdna_fasta": input_hashes[".cache/phase3b/references/ensembl88.cdna.fa.gz"],
            "ncrna_fasta": input_hashes[".cache/phase3b/references/ensembl88.ncrna.fa.gz"],
        },
        "ensembl91_resource_sha256": {
            "gtf": input_hashes[".cache/phase3a/references/ensembl91.gtf.gz"],
            "cdna_fasta": input_hashes[".cache/phase3a/references/ensembl91.cdna.fa.gz"],
            "ncrna_fasta": input_hashes[".cache/phase3a/references/ensembl91.ncrna.fa.gz"],
        },
        "stable_id_rule": STABLE_ID_RULE,
        "stable_id_rule_implementation_sha256": input_hashes["src/rnaobs/core.py"],
        "mapping_path": ".cache/model_d/class_a_mapping.tsv",
        "mapping_row_count": counts["n_mapped"],
        "mapping_schema": list(CLASS_A_MAPPING_COLUMNS),
        "reported_length_semantics": "EXPECTED_ENSEMBL_88_TRANSCRIPT_LENGTH",
        "mapping_byte_size": MAPPING_OUTPUT.stat().st_size,
        "class_a_mapping_sha256": sha256(MAPPING_OUTPUT),
        **counts,
        "expected_ensembl88_length_fixed_before_unblinding": True,
        "actual_processed_length_checked": False,
        "actual_processed_length_check_deferred_to_authorized_parser": True,
        "structure_inputs_read": False,
        "structure_derived_tables_read": False,
        "longbench_inputs_read": False,
    }
    RECEIPT_OUTPUT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
