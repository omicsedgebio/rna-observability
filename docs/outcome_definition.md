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
