#!/usr/bin/env python3
"""Create an explicit SG-NEx to icSHAPE transcript mapping audit."""
from collections import Counter, defaultdict
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
ann_path = ROOT / "results/tables/sgnex_transcript_annotation.tsv"
shape_path = ROOT / "results/tables/icshape_transcript_inventory.tsv"
cache = ROOT / ".cache/phase2/qc"
cache.mkdir(parents=True, exist_ok=True)
full_path = cache / "transcript_mapping_summary.tsv"
counts_path = ROOT / "results/tables/transcript_mapping_category_counts.tsv"

def stable(identifier: str) -> str:
    return identifier.split(".", 1)[0] if identifier else ""

shape_ids = []
with shape_path.open() as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    for row in reader:
        shape_ids.append(row["structure_transcript_id"])

shape_by_stable = defaultdict(list)
for sid in shape_ids:
    shape_by_stable[stable(sid)].append(sid)

ann_rows = []
ann_by_stable = defaultdict(list)
with ann_path.open() as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    for row in reader:
        tid = row["sgnex_versioned_transcript_id"]
        record = {
            "sgnex_transcript_id": tid,
            "gene_id": row.get("gene_id", ""),
            "annotation_version": row.get("annotation_version", "Ensembl 91"),
        }
        ann_rows.append(record)
        ann_by_stable[stable(tid)].append(record)

fields = [
    "sgnex_transcript_id", "structure_data_transcript_id", "stable_transcript_id",
    "gene_id", "annotation_version", "mapping_category", "mapping_confidence",
    "ambiguity_reason", "retained_excluded",
]
counts = Counter()
with full_path.open("w", newline="") as out:
    writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    seen_shape = set()
    for row in ann_rows:
        tid = row["sgnex_transcript_id"]
        sid_stable = stable(tid)
        exact = [sid for sid in shape_by_stable.get(sid_stable, []) if sid == tid]
        candidates = shape_by_stable.get(sid_stable, [])
        if len(candidates) == 0:
            category, confidence, reason, retained, sid = "unmatched_sgnex", "none", "no stable ID in icSHAPE inventory", "excluded", ""
        elif len(ann_by_stable[sid_stable]) > 1:
            category, confidence, reason, retained, sid = "ambiguous_sgnex_stable_id", "low", "duplicate SG-NEx annotation rows for stable ID", "excluded", ";".join(candidates)
        elif len(candidates) > 1:
            category, confidence, reason, retained, sid = "ambiguous_structure_stable_id", "low", "multiple structure rows for stable ID", "excluded", ";".join(candidates)
        elif exact:
            category, confidence, reason, retained, sid = "exact_versioned_match", "high", "", "qc_candidate", exact[0]
        else:
            category, confidence, reason, retained, sid = "version_only_match", "moderate", "version suffix differs or is absent in one resource", "qc_candidate", candidates[0]
        seen_shape.update(candidates)
        counts[category] += 1
        writer.writerow({
            "sgnex_transcript_id": tid,
            "structure_data_transcript_id": sid,
            "stable_transcript_id": sid_stable,
            "gene_id": row["gene_id"],
            "annotation_version": row["annotation_version"],
            "mapping_category": category,
            "mapping_confidence": confidence,
            "ambiguity_reason": reason,
            "retained_excluded": retained,
        })

for sid in sorted(set(shape_ids) - seen_shape):
    counts["unmatched_structure"] += 1

with counts_path.open("w", newline="") as out:
    writer = csv.writer(out, delimiter="\t")
    writer.writerow(["mapping_category", "count"])
    for category, count in sorted(counts.items()):
        writer.writerow([category, count])

print(f"wrote {full_path} and {counts_path}")
