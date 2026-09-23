# K562 icSHAPE QC

The downloaded processed GEO supplement is `GSM4333260_K562.out.txt.gz` from GSE145805. It contains 69,416 unique versioned Ensembl transcript rows and 53,728,868 callable nucleotide scores. All identifiers are versioned. Scores range from 0 to 1, with mean 0.32065 and standard deviation 0.29155. The third field is `*` and remaining fields are nucleotide positions. `NULL` denotes no confident measurement and is missing, not a structural zero.

The source experiment is in vivo icSHAPE, based on NAI-N3 treatment and reverse transcriptase stop profiling. The processed file is associated with GRCh38/hg38 in the GEO record and is not itself a run-level SG-NEx measurement. The file does not provide per-position depth, so callable fraction is a coverage proxy rather than a calibrated confidence probability. A threshold of callable fraction at least 0.5 is a provisional QC flag only.

Inventory and score summaries are in `results/tables/icshape_transcript_inventory.tsv` and `results/tables/icshape_summary.json`. Replicate-level information must be taken from the source publication and GEO metadata before any structure feature is treated as replicated.
