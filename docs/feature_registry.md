# Candidate feature registry

No features calculated. P = candidate primary core; S = secondary; E = exploratory. Model memberships are additive, except endpoint-derived features are excluded from primary prediction. Unspecified direction means two-sided; absence is not zero.

Definitions: L transcript length; O callable positions; r_i icSHAPE reactivity; B annotation read-compatibility matrix at declared read length/distribution. Source annotations must be versioned and sequence-verified.

| Feature / model | Definition/formula | Source | Rationale | Confounding/leakage | Missingness | Direction | Class |
|---|---|---|---|---|---|---|---|
| Abundance A | median log2(a+0.1) from independent covariate libraries | Processed estimates; manifest | Sampling sensitivity | Mechanical leakage if reused endpoint | No independent source -> cannot primary-fit | Unspecified | P |
| Replicate variability | var(log2(a+0.1)) independent covariate libraries | Same | Background precision | Direct outcome reuse forbidden | Requires >=3 replicates | Unspecified | E |
| Dynamic range | max_c log2(a+0.1)-min_c log2(a+0.1) in training contexts | Training-only expression | Context dependence | External context use forbidden | Multiple contexts required | Unspecified | E |
| Length A | log(L), mature transcript excluding added poly(A) | FASTA + GTF | Capture/processivity | Annotation and RNA degradation | Exclude unresolved sequence | Unspecified | P |
| GC A | (G+C)/(A+C+G+T) | FASTA | Known sequence bias | Structure correlation | Ambiguous bases audited | Unspecified | P |
| Isoform number B | log(1+n_transcripts_gene) | Fixed GTF | Complexity | Annotation completeness, expression | Fixed annotation required | More difficulty expected | P |
| Exon count B | n_exons(t) | GTF | Architecture | Length correlated | Exclude invalid exon chains | Unspecified | P |
| Exon sharing B | shared exonic bases/L within gene | GTF | Read ambiguity | Identical exons and alternative boundaries | Mapping required | More difficulty expected | P |
| Unique junctions B | junctions exclusive to t / max(1,n_junctions) | Fixed GTF | Assignability | Read length and coverage | Single exon flag separate | Less difficulty expected | P |
| Unique sequence B | number of uniquely attributable k-mer starts / (L-k+1), k=31 candidate | Full transcriptome FASTA | Sequence-level ambiguity | Read length, errors, paralogs | L<k -> NA | Less difficulty expected | P |
| Effective unique length B | count of uniquely assignable fragment start positions under fixed length distribution | Annotation + simulation of compatibility, not fitted outcomes | Assay-aware uniqueness | Fragment model assumptions | Unresolved geometry -> NA | Less difficulty expected | P |
| Transcript similarity B | maximum sibling/paralog sequence identity under fixed alignment definition | FASTA | Near indistinguishability | Families span genes | Definition must be frozen | More difficulty expected | P |
| Alternative first/last exon B | indicators of nonshared terminal exon structures | GTF | End ambiguity | Degradation/end annotation | Missing ends explicit | Unspecified | S |
| K-value B | sigma_max(B)/sigma_min_positive(B), plus rank deficiency flag | miniQuant-compatible implementation | Deconvolution conditioning | Gene-level; read-length dependent | Singular design cannot silently use K alone | More difficulty expected | P |
| Inferential uncertainty B sensitivity | SD(abundance draws)/(mean+epsilon), independent data only | Quantifier bootstraps/posteriors | Assignment uncertainty | Not biological variance; may reuse endpoint | Not assumed in RDS | More difficulty expected | S |
| k-mer composition C | normalized counts, k=2/3 candidate; remove redundant column | FASTA | Residual sequence effects | Collinearity, GC | Ambiguous windows excluded | Unspecified | P |
| Homopolymers C | max run and bases in runs>=6 / L | FASTA | Sequencing/processivity | GC and repeat effects | Sequence required | Unspecified | P |
| Repetitive content C | RepeatMasker-overlap bases/L | Matched build repeat annotation | Mapping difficulty | Annotation overlap | Missing repeat map -> NA | More difficulty expected | P |
| Low complexity C | fixed-window Shannon entropy; fraction below predefined threshold | FASTA | Sequence bias | Repeats/GC | Window/threshold not frozen | Unspecified | S |
| Mean reactivity D | mean_(i in O) r_i | Experimental icSHAPE | Accessibility proxy | Coverage, RBP binding, assay/RT biases | Never fill NULL with 0 | Unspecified | P |
| Reactivity distribution D | median, IQR, fixed quantiles | Experimental icSHAPE | Heterogeneous accessibility | Correlated summaries | Minimum callable bases required | Unspecified | S |
| Low-reactivity burden D | sum_(i in O) I(r_i<tau)/|O|; tau chosen before outcomes | Experimental icSHAPE | Proxy for protected/structured regions | Not direct pairing; cutoff dependent | Coverage restriction | Unspecified | S |
| Local variability D | mean |r_(i+1)-r_i| over adjacent callable pairs | Experimental icSHAPE | Spatial heterogeneity | Missing gaps, local GC | No bridging missing bases | Unspecified | S |
| End accessibility D | mean r in first/last 100 mature-transcript bases | Experimental icSHAPE + mapped ends | End-related effects | Annotation and 5/3 coverage | Window coverage required | Unspecified | S |
| Junction accessibility D | mean r within +/-25 nt of mapped junctions | Experimental icSHAPE + GTF | Local assay sensitivity | Shared exons; isoform assignment | Single exon -> not applicable | Unspecified | E |
| Disagreement-region structure | summaries in independently defined fixed regions | Structure + coverage | Localization | Outcome-defined windows create circularity | Region data unavailable | Unspecified | E |
| Structure availability nuisance C and D | |O|/L, position coverage, probe-depth if available | Structure assay metadata | Control selection effects | Coverage can proxy abundance and assay bias | Observed mask retained | Unspecified | P nuisance |
| m6A E | fraction of adequately covered eligible motifs with independently supported modification; coverage reported | Matched orthogonal m6ACE where verified | Modification-dependent behavior | Same nanopore signal creates circularity | Unknown is not unmodified | Unspecified | E |
| Predicted structure comparator | MFE/L or pairing summaries from versioned predictor | FASTA; fixed method | Separate predicted vs measured increment | Predicted fold depends on GC/length | Method/window limitations | Unspecified | S |

Structure coverage nuisances are included in both C and D for the conditional comparison; report a sequence-only C without assay metadata separately. Do not call coverage gain structural signal. No region selection using outcome residuals in the confirmatory path.

Batch, chemistry, library prep, depth, gene abundance, platform coverage, RIN/degradation, transcript ends, context and quantifier are nuisance/design variables, not intrinsic features. Include only if recorded and identifiable; a covariate cannot resolve perfectly confounded design. Parameters, transforms, thresholds, annotation and tool versions remain to freeze.
