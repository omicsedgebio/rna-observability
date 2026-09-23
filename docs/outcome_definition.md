# Candidate measurement outcomes

Status: proposed, not frozen or computed. No composite score.

Let U be a fixed annotation universe; t a transcript, c context, p a protocol+chemistry+quantifier, r an independent biological RNA preparation. Technical runs are aggregated within library/preparation before summarizing. Let a_tcpr be a harmonized relative molar abundance on a per-million scale over U (not uncorrected short-read counts). Absent quantification rows are missing until proven to mean zero.

## Primary candidate: signed protocol-pair disagreement

Primary pair proposed: ONT direct RNA p versus Illumina q in K562.

y_tc,pq = median_r[log2(a_tcpr + 0.1)] - median_s[log2(a_tcqs + 0.1)].

Units: log2 relative-abundance difference; positive means higher on p relative to q, not greater truth or reliability. The 0.1 per-million offset is a proposed convention, not an optimized or validated value. Assess fixed 0.01 and 1 sensitivity later. Separate positive and negative behavior; use |y| as secondary magnitude. Do not pool different pairs into a universal score.

Candidate inclusion: fixed reference transcripts with confirmed mapping and independent abundance evidence >=1 per million in >=2 covariate-source replicates; at least 2 independent outcome libraries per protocol. Never require detection on both outcome platforms: retain genuine zeros to avoid deleting disagreement. Low-expression and unsupported outcomes are reported separately. Structure comparison further requires predeclared callable-base coverage; threshold awaits metadata-only feasibility.

Paired aliquots are preferable. If true pairs exist, use a predeclared paired sensitivity; do not infer pairs from matching replicate numbers. Bootstrap independent preparations within protocols and genes for cohort uncertainty. The number of libraries, not transcript count, limits protocol-effect inference. Avoid treating every cross-product of replicate pairs as independent evidence.

This endpoint combines biology, preparation, sequencing, quantification and composition. It cannot identify which platform is inaccurate. It is abundance-conditioned prediction, not necessarily pre-sequencing assay selection.

## Secondary endpoints

| Endpoint | Operational definition | Limitation |
|---|---|---|
| Absolute disagreement | d=|y| | Loss of direction; greater sampling variance inflates d |
| Replicate dispersion | v_tcp=sample variance_r(log2(a_tcpr+0.1)) | At least 3 independent replicates preferred; few replicates unstable |
| Detection consistency | pi_tcp=mean_r I(n_tcpr>=k); propose k=5 assigned molecules/fragments | Count units and depth differ; k not frozen |
| Platform-specific detection | pi_tcp-pi_tcq; dropout=1-pi on independent eligibility universe | Depth/algorithm dependent, not proof of absence |
| Isoform-fraction disagreement | f_tcpr=a_tcpr/sum_(u in gene(t)) a_ucpr; median(f_p)-median(f_q) | Undefined if gene total zero; compositional and annotation dependent |
| Rank concordance | Spearman correlation across eligible transcripts between independent libraries | Global/context endpoint, not an individual-transcript target |
| Spike-in recovery error | e_spr=log2(hat_pi_spr/pi_s), where pi_s=molar input_s/sum_inputs and hat_pi is estimated molar fraction within spike-ins | Non-detected spike-ins handled separately; no arbitrary truth pseudocount; mixture/length correction mandatory |

## Exploratory endpoints

Splice-chain support = reads supporting exact annotated intron chain / assignable reads for a transcript; full-length recovery = reads matching chain AND both ends within predeclared tolerance / assignable reads. Candidate end tolerance 50 nt, sensitivity 25/100; not frozen. 5-prime and 3-prime completeness analyzed separately using strand-aware distances from aligned ends to annotated ends, conditioned on read assignment. Chain agreement alone is not end completeness. Regional coverage depletion is a within-transcript normalized regional depth contrast, requiring actual coverage tracks and window definition.

Cannot derive these regional endpoints from transcript-total matrices. Multimapping, alternative ends, degradation and poly(A) selection complicate them. No raw read retrieval for them in this phase.

## Leakage guard

Expression or replicate variability calculated from the same measurements that define y can mechanically predict it. Primary covariates must come from independent libraries/orthogonal expression source or a prespecified cross-fitting construction; endpoint libraries cannot supply their own covariates. If replication cannot support this separation, downgrade to descriptive association or remove those features, and revise the estimand before freeze. All nested models must be evaluated on identical rows.

## Phase 3A measurement-only QC and freeze status

The original primary formula remains a **candidate**, not a frozen endpoint. For a fixed common Ensembl 91 transcript index U, proposed per-library abundance is `a_tr = 1e6 * normEst_tr / sum_{u in U} normEst_ur`; if a transcript has no represented row, do not silently set it to zero. For independent biological preparations, the proposed signed contrast is `y_t(c) = median_{r in dRNA} log2(a_tr+c) - median_{s in Illumina} log2(a_ts+c)`, with candidate `c=0.1 TPM`. It is protocol-specific log relative-abundance disagreement, never true measurement error. Absolute disagreement is `|y_t(c)|`. Detection difference at threshold q is `mean_{dRNA} I(a_tr>=q) - mean_{Illumina} I(a_ts>=q)`. Isoform-fraction difference is the difference of protocol medians of `a_tr / sum_{u in gene(t)} a_ur`, undefined when the gene denominator is zero. Rank difference is the difference of transcript percentile ranks within each library before protocol medians.

Measurement-only QC examined `c=0.01, 0.1, 1` TPM. On 49,309 transcripts with Illumina Rep3 TPM >=1, the median signed contrast moved from -6.90 to -3.83 to -1.40 log2 units. At `c=0.1`, 56.8% were all-zero in the four direct-RNA libraries. The fixed-universe closure changed the contrast by median absolute 0.432 log2 units. These changes are too large to call the continuous zero-heavy contrast robust. Replicate disjoint-contrast Spearman values of 0.734-0.757 are partly driven by shared abundance/detection behavior and do not establish a stable residual measurement phenotype. No structure data were used for these checks. There is only one disjoint Illumina covariate preparation if Rep4/5 define the outcome; the earlier >=2 independent covariate-library eligibility condition is not met.

Candidate secondary outcomes are absolute log disagreement, thresholded detection difference at 0 and 1 TPM, rank difference, isoform-fraction difference, and within-protocol replicate dispersion. Candidate spike-in true relative error is defined separately in `docs/spikein_ground_truth.md`, but is not evaluated. Splice-chain, whole-transcript and 5-prime/3-prime completeness require read alignments and remain exploratory with no values derived. No PRIMARY ENDPOINT or SECONDARY ENDPOINTS are frozen in Phase 3A.
