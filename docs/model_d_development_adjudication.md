# Model D development adjudication

Status: **DEVELOPMENT CONCLUSION FROZEN**

Approved implementation-lock commit:
`ba9516ecea7dcfea5d216c2560f591638c874e13`

Scientific-lock commit:
`ea1dd05a992b92becc66e1cb825a821e48798923`

Development-result freeze:
`metadata/model_d_development_result_freeze.json`

## Locked result

The primary comparison was `D_STRUCTURE - C_QUALITY` using pooled five-fold out-of-fold macro-F1.

- C_QUALITY macro-F1: `0.54890983706729`
- D_STRUCTURE macro-F1: `0.5498834635530492`
- Delta macro-F1: `0.0009736264857591603`
- Paired cluster-bootstrap interval: `[-0.0023443180806064804, 0.004123505221307526]`
- Negative-control 95th percentile: `0.0015090734133574142`
- Strict-callability delta macro-F1: `0.0007399110130869024`
- Strict-callability bootstrap interval: `[-0.0034377341044534047, 0.004809181103569267]`

The frozen decision is:

- Conclusion: `NOT_SUPPORTED`
- Practical category: `NEGLIGIBLE`

The observed delta was positive but did not satisfy the locked statistical, practical-magnitude, or negative-control calibration gates. Four of five fold deltas were positive and the strict-callability sensitivity remained positive, but these findings do not override the failed primary decision gates.

## Scientific interpretation

Under the locked K562 development analysis, independently measured in-vivo RNA structure did not provide supported incremental predictive information about the workflow-specific transcript measurement phenotype beyond the frozen abundance, sequence, transcript-architecture/identifiability, and callability controls.

This result does not establish that RNA structure is biologically irrelevant or that structure cannot contribute under other assays, phenotypes, cell types, or study designs. It addresses only the frozen development hypothesis and comparison defined before structure access.

## Governance

The single authorized Model D execution completed successfully with no protocol deviation.

The Model D attempt is consumed and must not be rerun automatically.

The following are prohibited after this development result:

- rerunning Model D;
- retuning the frozen estimator or thresholds;
- adding post hoc structure summaries to rescue the result;
- changing the development cohort or folds;
- changing the locked primary metric or decision thresholds;
- reinterpreting secondary metrics as a rescue of the primary conclusion.

LongBench remains locked at this stage. No LongBench result has been inspected or used in this adjudication.

Any later decision to open LongBench must be made as a separate, explicit post-development validation decision after this development conclusion is committed and frozen.
