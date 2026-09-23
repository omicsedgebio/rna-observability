#!/usr/bin/env Rscript
# Cache-only extraction of the exact historical tables, without other audits.
suppressPackageStartupMessages(library(data.table))
setDTthreads(1)
dir.create('.cache/phase3a/qc', recursive=TRUE, showWarnings=FALSE)
m <- readRDS('.cache/phase2/sgnex/metadata.rds')
cat('Extracted annotation rows:', nrow(m$ensemblAnnotations.transcripts), '\n')
fwrite(as.data.table(m$ensemblAnnotations.transcripts),
       '.cache/phase3a/qc/sgnex_annotation_full.tsv', sep='\t', quote=FALSE, na='NA')
rm(m); gc()
tx <- readRDS('.cache/phase2/sgnex/transcript.rds')
setDT(tx)
k <- tx[cellLine=='K562', .(tx_name, gene_name, estimates, normEst, ntotal,
                           runname, method, protocol_general)]
fwrite(k, '.cache/phase3a/qc/k562_quantification.tsv', sep='\t', quote=FALSE, na='NA')
cat('Extracted K562 rows:', nrow(k), '\n')
writeLines(capture.output(sessionInfo()), '.cache/phase3a/qc/model_c_R_session.txt')
