#!/usr/bin/env python3
"""Build the locked annotation-only comparator without structure or outcomes."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rnaobs.core import annotation_features, fasta_records, read_gtf, stable_id
from rnaobs.model_d_locked import (
    ANNOTATION_MATRIX_COLUMNS,
    validate_annotation_matrix,
    sha256,
)

EXPECTED = {
    "ensembl91.gtf.gz": "1abe442ea2ba90c022545be71c4e7b95b66d45c8c9e4e4ec3788b6be440b598d",
    "ensembl91.cdna.fa.gz": "a7f0022e884826d70e0a151f6c38547aea8d443eaa9653aaf56e698e23109201",
    "ensembl91.ncrna.fa.gz": "0ab3565714f88fb98eb7df7814fe3fed770e2b098d37cd7b83601258f87e75dd",
    "src/rnaobs/core.py": "42a42d2cba1a3fcf20b77360feed2ef4d84183485a3072a56023556f641b1969",
    "src/exact_kmers.cpp": "2ab285bd2a052c4a0cfc9afa5051192b73a66375b25c4bb326416f061edadc7a",
    "scripts/phase3a_feature_audit.py": "4d1537108521f513f004bb528dc2f1881e827e8a71d643f496df3b1a7c6f2459",
    "scripts/run_miniquant_kvalue.py": "960487e1077b044fbe269526c3e4693223cf5993fa346180f1561f202d7194d6",
}
EXPECTED_UNIVERSE = 199_216
EXPECTED_COHORT = 15_999


def deterministic_gzip_tsv(frame: pd.DataFrame, path: Path) -> None:
    buffer = io.StringIO(newline="")
    frame.to_csv(buffer, sep="\t", index=False, lineterminator="\n",
                 float_format="%.17g", na_rep="")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(buffer.getvalue().encode("utf-8"), mtime=0))


def verify_inputs(references: Path, kvalues: Path) -> dict[str, str]:
    observed: dict[str, str] = {}
    for name in ("ensembl91.gtf.gz", "ensembl91.cdna.fa.gz", "ensembl91.ncrna.fa.gz"):
        path = references / name
        if not path.is_file():
            raise RuntimeError(f"required pinned reference unavailable: {path}")
        observed[str(path)] = sha256(path)
        if observed[str(path)] != EXPECTED[name]:
            raise RuntimeError(f"pinned reference hash mismatch: {path}")
    for relative in ("src/rnaobs/core.py", "src/exact_kmers.cpp",
                     "scripts/phase3a_feature_audit.py", "scripts/run_miniquant_kvalue.py"):
        path = ROOT / relative
        observed[relative] = sha256(path)
        if observed[relative] != EXPECTED[relative]:
            raise RuntimeError(f"pinned implementation hash mismatch: {relative}")
    if not kvalues.is_file():
        raise RuntimeError("locked miniQuant K-value output is unavailable")
    observed[str(kvalues)] = sha256(kvalues)
    return observed


def load_sequences(references: Path) -> dict[str, str]:
    sequences: dict[str, str] = {}
    for name in ("ensembl91.cdna.fa.gz", "ensembl91.ncrna.fa.gz"):
        for transcript_id, sequence in fasta_records(references / name):
            if transcript_id in sequences:
                raise RuntimeError("duplicate exact transcript ID in pinned FASTAs")
            sequences[transcript_id] = sequence.upper()
    return sequences


def write_universe_fasta(path: Path, universe: list[str], sequences: dict[str, str]) -> None:
    with path.open("w", encoding="ascii", newline="") as handle:
        for transcript_id in universe:
            handle.write(f">{transcript_id}\n{sequences[transcript_id]}\n")


def run_exact_kmers(work: Path, fasta: Path) -> Path:
    binary = work / "exact_kmers"
    output = work / "unique_kmers31.tsv"
    scratch = work / "kmer_scratch"
    subprocess.run(["c++", "-std=c++23", "-O3", str(ROOT / "src/exact_kmers.cpp"),
                    "-o", str(binary)], check=True)
    subprocess.run([str(binary), str(fasta), "31", str(scratch), str(output)], check=True)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--references", type=Path,
                        default=ROOT / ".cache/phase3a/references")
    parser.add_argument("--kvalues", type=Path,
                        default=ROOT / ".cache/phase3a/qc/miniquant/kvalues.tsv")
    parser.add_argument("--work", type=Path,
                        default=ROOT / ".cache/prestructure_annotation")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/tables/prestructure_annotation_comparator.tsv.gz")
    args = parser.parse_args()
    inputs = verify_inputs(args.references, args.kvalues)
    args.work.mkdir(parents=True, exist_ok=True)

    annotation = read_gtf(args.references / "ensembl91.gtf.gz")
    sequences = load_sequences(args.references)
    universe = sorted(set(annotation).intersection(sequences))
    if len(universe) != EXPECTED_UNIVERSE:
        raise RuntimeError("pinned GTF/FASTA intersection differs from locked feature universe")
    stable_to_version: dict[str, str] = {}
    for transcript_id in universe:
        stable = stable_id(transcript_id)
        if stable in stable_to_version:
            raise RuntimeError("validated universe has a non-unique stable transcript ID")
        stable_to_version[stable] = transcript_id

    architecture = annotation_features(annotation.values())
    fasta = args.work / "validated_transcripts.fa"
    write_universe_fasta(fasta, universe, sequences)
    kmer_path = run_exact_kmers(args.work, fasta)
    kmers = pd.read_csv(kmer_path, sep="\t", dtype={"transcript_id": str})
    if len(kmers) != EXPECTED_UNIVERSE or kmers["transcript_id"].duplicated().any():
        raise RuntimeError("exact-kmer output universe is invalid")
    if kmers["transcript_id"].tolist() != universe:
        raise RuntimeError("exact-kmer output order differs from sorted validated universe")
    kmer_values = dict(zip(kmers["transcript_id"], kmers["unique_kmer_fraction"], strict=True))

    kvalues = pd.read_csv(args.kvalues, sep="\t")
    if list(kvalues.columns) != ["Gene_id", "K-value"] or kvalues["Gene_id"].duplicated().any():
        raise RuntimeError("miniQuant K-value schema or uniqueness check failed")
    miniquant = dict(zip(kvalues["Gene_id"].astype(str), kvalues["K-value"], strict=True))

    with (ROOT / "metadata/final_transcript_cohort.tsv").open(newline="") as handle:
        cohort = list(csv.DictReader(handle, delimiter="\t"))
    frozen_ids = [row["stable_id"] for row in cohort]
    if len(frozen_ids) != EXPECTED_COHORT or len(set(frozen_ids)) != EXPECTED_COHORT:
        raise RuntimeError("frozen cohort ID count or uniqueness differs from lock")

    rows = []
    for stable in frozen_ids:
        transcript_id = stable_to_version.get(stable)
        if transcript_id is None:
            raise RuntimeError(f"frozen transcript is absent from validated universe: {stable}")
        tx = annotation[transcript_id]
        values = architecture[transcript_id]
        kmer = np.float64(kmer_values[transcript_id])
        kval = np.float64(miniquant.get(tx.gene, np.nan))
        rows.append({
            "stable_id": stable,
            "unique_kmer_fraction": kmer,
            "unique_kmer_fraction_missing": int(not np.isfinite(kmer)),
            "unique_exonic_bases": values["unique_exonic_bases"],
            "shared_exon_fraction": values["shared_exon_fraction"],
            "unique_junction_count": values["unique_junction_count"],
            "max_exon_jaccard": values["max_exon_jaccard"],
            "identical_splice_chain_isoforms": values["identical_splice_chain_isoforms"],
            "incidence_rank_deficiency": values["incidence_rank_deficiency"],
            "mean_exon_length": values["mean_exon_length"],
            "miniquant_kvalue": kval,
            "miniquant_kvalue_missing": int(not np.isfinite(kval)),
        })
    frame = pd.DataFrame(rows, columns=ANNOTATION_MATRIX_COLUMNS)
    missing = validate_annotation_matrix(frame, frozen_ids)
    deterministic_gzip_tsv(frame, args.output)
    receipt = {
        "rows": len(frame),
        "columns": list(frame.columns),
        "missing_counts": missing,
        "global_imputation_applied": False,
        "bytes": args.output.stat().st_size,
        "sha256": sha256(args.output),
        "validated_universe_transcripts": len(universe),
        "source_and_implementation_sha256": inputs,
        "derived_intermediate_sha256": {
            str(fasta): sha256(fasta),
            str(kmer_path): sha256(kmer_path),
        },
        "structure_inputs_read": False,
        "outcome_inputs_read": False,
    }
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
