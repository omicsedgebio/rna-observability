# Alternative K562 measurement-validation resources

This bounded audit used public experiment metadata only. It did not inspect transcript-level outcome distributions or any structure association.

| Resource | Technology and replication | Annotation/context | Classification | Use |
|---|---|---|---|---|
| SG-NEx K562 | Illumina, direct RNA, cDNA and other workflows with processed matrices; multiple preparations | GRCh38, Ensembl 91 object | MODERATE | Best currently accessible development matrix, but workflow-specific scales and sparse NanoCount output remain limiting |
| ENCSR917JIA | ONT direct RNA, two isogenic K562 replicates | ENCODE processed long-read resource | MODERATE | Independent direct-RNA measurement validation candidate; requires exact processed quantification and annotation audit |
| GSE132766 | ONT direct RNA, two K562 replicates, TALON output | GENCODE v29 | MODERATE | Processed transcript output; release bridge and laboratory differences require explicit handling |
| ENCSR000AEP / ENCSR000AEM | Illumina poly(A), two replicates each, different ENCODE laboratories | K562 untreated ENCODE contexts | WEAK to MODERATE | Possible short-read comparator, but laboratory and library differences complicate pairing |
| ENCSR589FUJ | PacBio K562, two replicates | ENCODE processed long-read resource | WEAK | Platform breadth, but not a direct-RNA comparator |
| ENCSR526TQU | PacBio K562, one replicate | ENCODE processed long-read resource | WEAK | Insufficient replication for primary validation |
| ENCSR534TGM | Long-read K562 after JQ1 treatment | Treated context | UNSUITABLE for untreated primary analysis | Treatment mismatch |

Sources: [ENCSR917JIA](https://www.encodeproject.org/experiments/ENCSR917JIA/), [GSE132766](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132766), [ENCSR000AEP](https://www.encodeproject.org/experiments/ENCSR000AEP/), [ENCSR000AEM](https://www.encodeproject.org/experiments/ENCSR000AEM/), [ENCSR589FUJ](https://www.encodeproject.org/experiments/ENCSR589FUJ/), [ENCSR526TQU](https://www.encodeproject.org/experiments/ENCSR526TQU/), [ENCSR534TGM](https://www.encodeproject.org/experiments/ENCSR534TGM/). These candidates remain metadata-level alternatives, not replacements selected from outcome performance.
