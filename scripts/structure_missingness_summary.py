#!/usr/bin/env python3
"""Summarize icSHAPE callable coverage without testing outcome associations."""
from pathlib import Path
import csv
import json
import statistics

root = Path(__file__).resolve().parents[1]
with (root / "results/tables/icshape_transcript_inventory.tsv").open() as h:
    shape = list(csv.DictReader(h, delimiter="\t"))
with (root / ".cache/phase2/qc/k562_expression_qc.tsv").open() as h:
    expr = {r["stable_transcript_id"].strip('"'): r for r in csv.DictReader(h, delimiter="\t") if r["stable_transcript_id"] != "NA"}
for r in shape:
    e = expr.get(r["stable_transcript_id"].strip('"'), {})
    r.update(e)
    r["callable_fraction_f"] = float(r["callable_fraction"])
    r["usable"] = r["callable_fraction_f"] >= 0.5
    r["expression"] = float(e["salmon_sr_median_normEst"]) if e.get("salmon_sr_median_normEst") not in (None, "", "NA") else None
    r["isoforms"] = int(e["isoform_count"]) if e.get("isoform_count") not in (None, "", "NA") else None

expressed = sorted(r["expression"] for r in shape if r["expression"] is not None)
def decile(x):
    if x is None or not expressed: return "NA"
    rank = sum(v <= x for v in expressed)
    return str(min(10, max(1, int((rank - 1) * 10 / len(expressed)) + 1)))
rows = []
for r in shape:
    r["expression_decile"] = decile(r["expression"])
for dimension, key in [("expression_decile", "expression_decile"), ("isoform_count", "isoforms")]:
    groups = {}
    for r in shape:
        groups.setdefault(str(r[key] if r[key] is not None else "NA"), []).append(r)
    for level, g in sorted(groups.items()):
        rows.append({"dimension": dimension, "level": level, "transcripts": len(g), "usable_callable_fraction_ge_0.5": sum(x["usable"] for x in g), "usable_fraction": sum(x["usable"] for x in g) / len(g), "median_callable_fraction": statistics.median(x["callable_fraction_f"] for x in g)})
for platform_col in ("detected_Illumina", "detected_directRNA", "detected_directcDNA", "detected_cDNA"):
    groups = {"detected": [], "not_detected": [], "unknown": []}
    for r in shape:
        value = r.get(platform_col, "NA")
        groups["unknown" if value in ("", "NA", None) else ("detected" if float(value) > 0 else "not_detected")].append(r)
    for level, g in groups.items():
        if g:
            rows.append({"dimension": platform_col, "level": level, "transcripts": len(g), "usable_callable_fraction_ge_0.5": sum(x["usable"] for x in g), "usable_fraction": sum(x["usable"] for x in g) / len(g), "median_callable_fraction": statistics.median(x["callable_fraction_f"] for x in g)})
with (root / "results/tables/structure_missingness.tsv").open("w", newline="") as h:
    w = csv.DictWriter(h, fieldnames=rows[0].keys(), delimiter="\t")
    w.writeheader(); w.writerows(rows)
summary = {"structure_transcripts": len(shape), "matched_qc_rows": sum(r["stable_transcript_id"].strip('"') in expr for r in shape), "expression_values_available": sum(r["expression"] is not None for r in shape), "callable_fraction_ge_0.5": sum(r["usable"] for r in shape), "callable_fraction_ge_0.5_fraction": sum(r["usable"] for r in shape) / len(shape), "gc_available": False, "note": "No structure outcome association was computed; summaries are availability/QC only."}
(root / "results/tables/structure_missingness_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
