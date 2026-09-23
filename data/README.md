# Data policy

No scientific data have been downloaded in Phase 1. Public catalog pages, file manifests and methods were read remotely.

Use ignored external/ for authorized source data and processed/ for reproducible derived data. No FASTQ/BAM/CRAM, large matrices, restricted material or caches in Git. Public access does not imply unrestricted reuse.

Registry: ../metadata/datasets.tsv. NA_NOT_DOWNLOADED checksums are intentional; remote ETags are not SHA-256 hashes. Before acquisition record URL, date, bytes, checksum, source release, license, command, sample mapping, genome and annotation. Never download LongBench through a general development downloader. The locked flag is a governance boundary, not an operating-system access control.
