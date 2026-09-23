#!/usr/bin/env Rscript
suppressPackageStartupMessages({library(data.table)})
root <- getwd()
obj <- readRDS(file.path(root, ".cache/phase2/sgnex/transcript.rds"))
dt <- as.data.table(obj)
k <- dt[cellLine == "K562"]
ann <- fread(file.path(root, "results/tables/sgnex_transcript_annotation.tsv"))
ann <- unique(ann[, .(sgnex_transcript_id, stable_transcript_id, gene_id, tx_len, nexon)])
k[, stable_transcript_id := sub("\\..*$", "", tx_name)]
expr <- k[method == "salmon_sr",
          .(salmon_sr_median_normEst=median(normEst, na.rm=TRUE),
            salmon_sr_detect_fraction=mean(normEst > 0, na.rm=TRUE),
            salmon_sr_runs=.N), by=.(stable_transcript_id)]
det <- k[, .(protocols_detected=sum(any(normEst > 0)), n_rows=.N), by=.(stable_transcript_id, protocol_general)]
det <- dcast(det, stable_transcript_id ~ protocol_general, value.var="protocols_detected", fill=0)
setnames(det, old=setdiff(names(det), "stable_transcript_id"), new=paste0("detected_", setdiff(names(det), "stable_transcript_id")))
out <- merge(ann, expr, by="stable_transcript_id", all.x=TRUE)
out <- merge(out, det, by="stable_transcript_id", all.x=TRUE)
fwrite(out, file.path(root, ".cache/phase2/qc/k562_expression_qc.tsv"), sep="\t", na="NA")
