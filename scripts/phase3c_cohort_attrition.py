#!/usr/bin/env python3
"""Create the prespecified Phase 3C cohort attrition table.

This uses identifiers, annotation availability, and processed-object row
availability only. It never uses reactivity values or agreement to select a
transcript.
"""
from pathlib import Path
import json
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / 'results/tables/phase3c_reference_bridge.tsv'
ANN = ROOT / '.cache/phase3a/qc/sgnex_annotation_full.tsv'
DB = ROOT / '.cache/phase3c/quantifiers.duckdb'
OUT = ROOT / 'results/tables/cohort_attrition.tsv'
SUMMARY = ROOT / 'results/tables/cohort_attrition_summary.json'


def main():
    bridge = pd.read_csv(BRIDGE, sep='\t')
    ann = pd.read_csv(ANN, sep='\t', usecols=['tx_name'])
    ann_ids = set(ann.tx_name.str.replace(r'\.[0-9]+$', '', regex=True))
    b = bridge.copy()
    b['stable'] = b.ensembl91_transcript_id.replace('NA', pd.NA).str.replace(r'\.[0-9]+$', '', regex=True)
    b['mapping_compatible'] = b.mapping_class.isin(['A', 'B'])
    b['class_a'] = b.mapping_class.eq('A')
    b['annotation_available'] = b.stable.isin(ann_ids)
    b['coverage_eligible'] = b.coverage_eligible.astype(bool)

    con = duckdb.connect(str(DB), read_only=True)
    q = con.execute("""SELECT regexp_replace(tx_name, '\\.[0-9]+', '') AS stable,
        protocol_general AS platform, method, runname
        FROM q WHERE starts_with(stable, 'ENST') GROUP BY ALL""").df()
    # Row presence is a data-availability check. It is not a detection call.
    availability = {}
    for (platform, method), z in q.groupby(['platform', 'method']):
        runs = sorted(z.runname.unique())
        sets = [set(z.loc[z.runname.eq(run), 'stable']) for run in runs]
        availability[(platform, method)] = {
            'runs': runs,
            'all_runs': set.intersection(*sets) if sets else set(),
        }
    b['illumina_salmon_all_runs'] = b.stable.isin(availability[('Illumina', 'salmon_sr')]['all_runs'])
    b['illumina_rsem_all_runs'] = b.stable.isin(availability[('Illumina', 'rsem_sr')]['all_runs'])
    b['directrna_salmon_all_runs'] = b.stable.isin(availability[('directRNA', 'salmon_lr')]['all_runs'])
    b['directrna_bambu_all_runs'] = b.stable.isin(availability[('directRNA', 'bambu_lr')]['all_runs'])
    b['directrna_nanocount_any_run'] = b.stable.isin(availability[('directRNA', 'NanoCount_lr')]['all_runs'])
    b['platform_measurable'] = b.class_a & b.annotation_available & b.directrna_salmon_all_runs & b.illumina_salmon_all_runs
    # Salmon is the provisional complete-row reference workflow. No positive
    # value is used here, and NanoCount is not required because its sparse
    # output semantics are themselves under audit.
    b['quantifier_supported_reference'] = b.platform_measurable
    b['structure_eligible'] = b.class_a & b.coverage_eligible
    b['future_maximum_cohort'] = b.platform_measurable & b.structure_eligible

    stages = [
        ('all_sgnex_annotation_transcripts', pd.Series(True, index=b.index), len(ann_ids)),
        ('mapping_compatible_A_or_B', b.mapping_compatible, None),
        ('class_A', b.class_a, None),
        ('annotation_available', b.class_a & b.annotation_available, None),
        ('platform_measurable_complete_salmon', b.platform_measurable, None),
        ('quantifier_supported_reference', b.quantifier_supported_reference, None),
        ('structure_eligible_A_coverage', b.structure_eligible, None),
        ('future_maximum_intersection', b.future_maximum_cohort, None),
    ]
    rows = []
    for label, mask, override in stages:
        rows.append({'stage': label, 'n_transcripts': int(override if override is not None else mask.sum()),
                     'source': 'SG-NEx Ensembl91 annotation' if label.startswith('all_') else
                              'phase3c_reference_bridge and processed row availability',
                     'selection_uses_structure_values': False, 'selection_uses_outcome': False})
    pd.DataFrame(rows).to_csv(OUT, sep='\t', index=False)
    summary = {'stages': rows, 'rows_in_bridge': len(b),
               'reference_workflows': {f'{p}:{m}': len(v['all_runs']) for (p, m), v in availability.items()},
               'reference_workflow_runs': {f'{p}:{m}': v['runs'] for (p, m), v in availability.items()},
               'structure_values_read': False, 'sequencing_outcomes_read': False,
               'future_maximum_definition': 'class-A, >=50 callable bases, >=0.5 callable fraction, complete SG-NEx Salmon rows in all Illumina and directRNA K562 runs'}
    SUMMARY.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
