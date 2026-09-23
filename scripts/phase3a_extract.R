#!/usr/bin/env Rscript
# Semantics and replicate QC only. Never loads RNA reactivity or external outcomes.
suppressPackageStartupMessages(library(data.table))
setDTthreads(2)
dir.create('.cache/phase3a/qc', recursive=TRUE, showWarnings=FALSE)
write_tab <- function(x, file) fwrite(x, file, sep='\t', quote=FALSE, na='NA')
m <- readRDS('.cache/phase2/sgnex/metadata.rds')
write_tab(as.data.table(m$samples_wSpikein), '.cache/phase3a/qc/spikein_library_metadata.tsv')
write_tab(as.data.table(m$sampleData_sr), '.cache/phase3a/qc/illumina_metadata.tsv')
write_tab(as.data.table(m$ensemblAnnotations.transcripts), '.cache/phase3a/qc/sgnex_annotation_full.tsv')
tx <- readRDS('.cache/phase2/sgnex/transcript.rds')
setDT(tx)
audit <- tx[, .(rows=.N, sum_estimates=sum(estimates), sum_normEst=sum(normEst),
                 ntotal_values=uniqueN(ntotal), ntotal=ntotal[1],
                 formula_max_abs_error=max(abs(normEst-estimates/ntotal*1e6)),
                 duplicate_transcript_rows=.N-uniqueN(tx_name),
                 zero_fraction=mean(normEst==0)),
             by=.(runname, method, protocol_general, cellLine)]
write_tab(audit, 'results/tables/abundance_semantics_audit.tsv')
k <- tx[cellLine=='K562', .(tx_name, gene_name, estimates, normEst, ntotal,
                            runname, method, protocol_general)]
write_tab(k, '.cache/phase3a/qc/k562_quantification.tsv')
cat('K562 rows:',nrow(k),'\n')
rm(tx, k); gc()
s <- readRDS('.cache/phase2/sgnex/spikein.rds')
for(i in seq_along(s)) {
 z <- as.data.table(s[[i]])
 audit <- z[, .(rows=.N, unique_entities=uniqueN(if(i==1) tx_name else gene_name),
                sum_normEst=sum(normEst), zero_fraction=mean(normEst==0)),
            by=.(runname, protocol, method)]
 write_tab(audit, paste0('results/tables/spikein_workflow_audit_',i,'.tsv'))
 write_tab(z[!grepl('^ENST|^ENSG',if(i==1) tx_name else gene_name)],
           paste0('.cache/phase3a/qc/spikein_synthetic_',i,'.tsv'))
}
writeLines(capture.output(sessionInfo()), 'metadata/phase3a_R_session.txt')
