# Structure coverage and missingness

Structure availability was assessed before any structure versus measurement association. The inventory has 69,416 transcript rows. A transcript is provisionally usable for transcript-level summaries when at least 50 percent of its reported nucleotide positions have non-NULL scores. This is a coverage rule, not a biological interpretation.

The current QC summary reports 36,433 usable rows, 52.49 percent of the inventory, with 66,052 rows linked to the cached SG-NEx QC inventory. A comparable expression value was not retained because the attempted Salmon extraction was interrupted and `normEst` is workflow-specific. GC is not available from the processed objects. Protocol detectability summaries are screening diagnostics, not covariate-adjusted analyses. Abundance-stratified missingness remains a required pre-modeling task.

Outputs are `results/tables/structure_missingness.tsv` and `results/tables/structure_missingness_summary.json`. No endpoint, disagreement, or predictive association was tested against structure. If usable structure is strongly selected by abundance, length, or protocol detectability, inverse probability weighting, stratification, or a prespecified missingness sensitivity analysis will be required.
