#!/usr/bin/env Rscript
# Phase 2 bounded QC. Writes only small summaries, never source objects.
suppressPackageStartupMessages({library(data.table)})
dir.create("results/tables", recursive=TRUE, showWarnings=FALSE)
dir.create("metadata", recursive=TRUE, showWarnings=FALSE)
dir.create(".cache/phase2/qc", recursive=TRUE, showWarnings=FALSE)

meta <- readRDS(".cache/phase2/sgnex/metadata.rds")
tx <- readRDS(".cache/phase2/sgnex/transcript.rds")
sp <- readRDS(".cache/phase2/sgnex/spikein.rds")

write_meta <- function(x, path) fwrite(as.data.table(x), path, sep="\t", na="NA", quote=FALSE)

tx_summary <- tx[, .(
  rows=.N, transcripts=uniqueN(tx_name), genes=uniqueN(gene_name), runs=uniqueN(runname),
  methods=uniqueN(method), protocols=uniqueN(protocol), cell_lines=uniqueN(cellLine),
  estimate_min=min(estimates, na.rm=TRUE), estimate_max=max(estimates, na.rm=TRUE),
  estimate_zero_fraction=mean(estimates==0, na.rm=TRUE),
  norm_min=min(normEst, na.rm=TRUE), norm_max=max(normEst, na.rm=TRUE),
  norm_zero_fraction=mean(normEst==0, na.rm=TRUE),
  ntotal_min=min(ntotal, na.rm=TRUE), ntotal_max=max(ntotal, na.rm=TRUE),
  short_read_min=min(short_read, na.rm=TRUE), short_read_max=max(short_read, na.rm=TRUE)
)]
tx_summary[, source_file := "combinedExpressionDataTranscript_19June2023.rds"]
write_meta(tx_summary, "results/tables/sgnex_transcript_object_summary.tsv")

by_group <- tx[, .(
  rows=.N, transcripts=uniqueN(tx_name), runs=uniqueN(runname), methods=uniqueN(method),
  estimate_zero_fraction=mean(estimates==0, na.rm=TRUE),
  estimate_median=median(estimates, na.rm=TRUE), norm_median=median(normEst, na.rm=TRUE),
  ntotal_median=median(ntotal, na.rm=TRUE), short_read_median=median(short_read, na.rm=TRUE)
), by=.(cellLine, protocol_general, protocol_method, protocol, method, short_read)]
write_meta(by_group[order(cellLine, protocol_general, protocol_method, method)], "results/tables/sgnex_measurement_groups.tsv")

k562 <- tx[cellLine == "K562"]
k562_group <- k562[, .(
  rows=.N, transcripts=uniqueN(tx_name), runs=uniqueN(runname),
  estimate_zero_fraction=mean(estimates==0, na.rm=TRUE), estimate_median=median(estimates, na.rm=TRUE),
  norm_median=median(normEst, na.rm=TRUE), ntotal_median=median(ntotal, na.rm=TRUE)
), by=.(protocol_general, protocol_method, protocol, method, short_read, runname_method)]
write_meta(k562_group[order(protocol_general, protocol_method, method, runname_method)], "results/tables/k562_measurement_groups.tsv")

ann <- as.data.table(meta$ensemblAnnotations.transcripts)
ann[, stable_transcript_id := sub("\\.[0-9]+$", "", ensembl_transcript_id.version)]
ann[, annotation_version := "Ensembl 91"]
write_meta(ann[, .(sgnex_transcript_id=tx_name, sgnex_versioned_transcript_id=ensembl_transcript_id.version,
                  stable_transcript_id, gene_id=ensembl_gene_id, tx_len, nexon, hgnc_symbol,
                  gene_biotype, annotation_version)], "results/tables/sgnex_transcript_annotation.tsv")

hier_long <- as.data.table(meta$samples)
hier_long[, source_table := "samples"]
hier_long[, biological_source := paste(cellLine, cancer_type, sep="|")]
hier_long[, rna_preparation := replicate_id]
hier_long[, library_id := old_runname]
hier_long[, sequencing_run := runname]
hier_long[, technical_replicate := techRep]
hier_long[, biological_replicate := bioRep]
hier_long[, technology := Platform]
hier_long[, library_protocol := protocol]
hier_long <- hier_long[, .(source_table, biological_source, cell_line=cellLine, biological_replicate,
                           rna_preparation, library_id, sequencing_run, technical_replicate,
                           technology, library_protocol, replicate_id)]
hier_long <- hier_long[cell_line == "K562"]

sr <- as.data.table(meta$sampleData_sr)
hier_sr <- sr[cellLine == "K562", .(
  source_table="sampleData_sr", biological_source=paste(cellLine, "Leukocyte", sep="|"), cell_line=cellLine,
  biological_replicate=`replicate-id`, rna_preparation=`replicate-id`, library_id=`ELM library ID`,
  sequencing_run=runName, technical_replicate="run1", technology="Illumina", library_protocol="Illumina",
  replicate_id=`replicate-id`)]

pb <- as.data.table(meta$pacbio_data)
hier_pb <- pb[grepl("K562", `Sample (cell line + condition)`), .(
  source_table="pacbio_data", biological_source=paste(`Sample (cell line + condition)`, "Leukocyte", sep="|"),
  cell_line=`Sample (cell line + condition)`, biological_replicate=paste0("replicate", Replicate),
  rna_preparation=paste0("replicate", Replicate), library_id=name, sequencing_run=runName,
  technical_replicate=paste0("run", Run), technology="PacBio", library_protocol=Protocol,
  replicate_id=paste0("replicate", Replicate))]

hier <- rbindlist(list(hier_long, hier_sr, hier_pb), fill=TRUE)
hier[, independent_biological_observation := paste(cell_line, biological_replicate, library_protocol, sep="|")]
write_meta(hier, "metadata/replicate_hierarchy.tsv")

rep_summary <- hier[, .(rows=.N, runs=uniqueN(sequencing_run), preparations=uniqueN(rna_preparation),
                       technical_replicates=uniqueN(technical_replicate)),
                   by=.(cell_line, technology, library_protocol, biological_replicate, rna_preparation)]
write_meta(rep_summary[order(cell_line, technology, library_protocol, biological_replicate)], "results/tables/replicate_hierarchy_summary.tsv")

sp_summary <- rbindlist(lapply(seq_along(sp), function(i) {
  z <- as.data.table(sp[[i]])
  z[, spikein_object := i]
  z[, .(rows=.N, transcripts=uniqueN(gene_name), runs=uniqueN(runname), methods=uniqueN(method),
        protocols=uniqueN(protocol), zero_fraction=mean(estimates==0, na.rm=TRUE),
        estimate_median=median(estimates, na.rm=TRUE), norm_median=median(normEst, na.rm=TRUE)),
      by=.(spikein_object)]
}), fill=TRUE)
write_meta(sp_summary, "results/tables/spikein_object_summary.tsv")

cat("QC_COMPLETE\n")
cat("transcript_rows", nrow(tx), "\n")
cat("k562_rows", nrow(k562), "\n")
cat("hierarchy_rows", nrow(hier), "\n")
