# K562 integration feasibility

Verdict: CONDITIONAL for exploratory cross-study feasibility; NOT established as matched biological integration or a causal experiment. There are no joined data or estimated overlap rates yet.

## Provenance and compatibility audit

| Item | SG-NEx | GSE145805 | Assessment |
|---|---|---|---|
| Identity | K562 samples explicitly listed | GSM4333259 K562D; GSM4333260 K562N | Same label, not same donor stock/aliquot |
| Source / passage / authentication | Not established from inspected manifest | Not established from inspected GEO record | Must recover source/STR/passage/mycoplasma if available |
| Culture | Main paper delegates to Supplementary Table 1; exact K562 recipe not verified here | RPMI 1640, 10% FBS, 37 C, 5% CO2 | Do not assume equivalence |
| Treatment | Sequencing extraction, not structure probing | In-vivo NAI-N3 treatment, 5 min at 37 C; DMSO control | Structure assay perturbs RNA chemically |
| Extraction / fractions | Exact per-sample extraction in Supplementary Table 1 unresolved | GEO text mixes fractionation/in-vitro/irCLIP descriptions | Need sample-specific clarification; do not infer fractionation from boilerplate |
| Sequencing | Illumina paired-end 150 bp; ONT RNA/cDNA/PCR-cDNA; PacBio | HiSeq X Ten icSHAPE libraries | Different selection and library chemistry |
| Genome | GRCh38 | hg38 | Assembly family agrees; exact FASTA not yet compared |
| Annotation | Ensembl 91 | Ensembl-like IDs, exact annotation release unverified | Joining IDs without exon/sequence checks prohibited |
| Structure object | No matched icSHAPE located | Per-base score vector with NULL entries | Scores are RT/probing accessibility proxies |
| Replicates | See manifest counts below | Series has treated/control accessions, not distinct biological replicate GSMs | D/N are NOT replicates; independent replicate score availability unresolved |

Sources: [SG-NEx methods](https://doi.org/10.1038/s41592-025-02623-4), [K562 GEO record](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM4333260), [PrismNet](https://doi.org/10.1038/s41422-021-00476-y).

## Manifest audit (metadata only)

Pinned SG-NEx repository tree: fea2aa80b149778d7fce507867dd6754fc4f84ca. [ONT manifest](https://github.com/GoekeLab/sg-nex-data/blob/fea2aa80b149778d7fce507867dd6754fc4f84ca/docs/samples.tsv) has 14 K562 runs: five PCR-cDNA runs across replicate labels 1/2/3 (cDNA and cDNAStranded), five direct-cDNA runs across 1/2/3/4, four direct-RNA runs across 1/4/5/6. Repeated run labels must not be treated as biological replication. RNA001/RNA002, PCS108/109 and DCS108/109 are mixed; sequencing dates span years. Labels alone do not establish paired extractions.

[Illumina manifest](https://github.com/GoekeLab/sg-nex-data/blob/fea2aa80b149778d7fce507867dd6754fc4f84ca/docs/illumina_samples.tsv): three K562 runs, replicate labels 3/4/5, Sequin Mix A recorded. [PacBio manifest](https://github.com/GoekeLab/sg-nex-data/blob/fea2aa80b149778d7fce507867dd6754fc4f84ca/docs/samples_pacbio.tsv): one K562 run, replicate7, dated 2023-01-27. No replicated PacBio endpoint should be promised.

## Structure audit

[GEO series](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE145805) lists K562, HepG2 and H9, all candidate SG-NEx overlaps. HEK293 is not HEK293T. GEO lists 12 sample records despite a summary saying seven cell lines: retain this discrepancy.

K562 processed file is GSM4333260_K562.out.txt.gz, listed 87.3 MB; full processed archive 424.4 MB. No file acquired. Row schema: identifier, reported length, placeholder, per-base scores; NULL is no confident score, never zero. Exact ID namespace/version, coordinate origin and mature-transcript orientation require inspection. The GEO record's NAI-N5 characteristic conflicts with NAI-N3 methods; log, do not silently correct source metadata.

The primary PrismNet paper reports two biological replicates and retains nucleotide scores at read depth greater than 100. Its processing collapses PCR duplicates, trims adapters, maps using STAR and computes icSHAPE-pipe scores. [AStruct](https://pmc.ncbi.nlm.nih.gov/articles/PMC11264973/) also describes two treated/two control replicates when reusing these data. Confirm the run-to-replicate mapping and whether downloadable score vectors retain replicate identity. Exact pipeline version, background handling and normalization parameters remain unresolved. Bounded reactivity is not base-pairing probability.

## Conditions for proceeding

Require an explicit versioned transcript map: exact reference sequence/exon chain/length where possible; mark one-to-many and ambiguous shared-exon assignments. No silent version stripping, no wholesale genomic liftover as substitute for transcript validation. Report callable bases, score coverage and exclusion counts by abundance/length/GC/ambiguity before structure-outcome associations.

Structure coverage depends on abundance, RT and mappability; selection can manufacture associations. Library protocols act on extracted RNA after heating/selection, so living-cell accessibility need not represent the molecule entering the instrument. Unmeasured cell-stock/culture differences cannot be removed by adding a study indicator when structure and study are confounded.

Alternatives: replicate feasibility in HepG2/H9 under the same safeguards; seek independently acquired matched structure without looking at LongBench outcomes; or eventually generate matched-aliquot probing/sequencing with explicit new authorization. If coordinate/provenance mismatch is severe, stop cross-study structural inference. A sequence-only study changes the central contribution and requires review.
