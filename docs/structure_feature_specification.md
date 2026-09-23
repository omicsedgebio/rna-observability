# Experimental structure feature specification

Candidate features are computed only from callable icSHAPE positions and retain a transcript-level coverage field. Proposed features are mean, median, variance, high-reactivity fraction, low-reactivity fraction, structured-region burden, local heterogeneity, junction-window summaries, and 5 prime and 3 prime end-window summaries.

For every feature, the minimum rule is 50 callable positions for global summaries and 20 callable positions in a local window, with the exact threshold frozen before modeling. `NULL` is excluded from numerators and denominators. A transcript is not assigned zero reactivity because it is missing. Junction and end windows use the SG-NEx Ensembl 91 transcript definition after explicit coordinate harmonization. Features with insufficient coverage are missing, with missingness indicators retained.

Mean and median summarize flexibility, variance and local heterogeneity summarize structural variability, and regional features test whether location could matter. All features can be confounded by abundance, transcript length, RNA preparation, and assay coverage. Structure summaries remain QC candidates until replicate concordance and cross-study compatibility are established.
