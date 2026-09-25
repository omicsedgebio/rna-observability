# Model C post-development deployment estimator

Status: **FROZEN DEPLOYMENT ARTIFACT**

Development conclusion affected: **NO**

The repository now contains one transparent full-development Model C estimator
for possible future external transport. It was fit once to the already frozen
15,999-row SG-NEx Model C matrix, using the exact nine-feature order,
`StandardScaler`, logistic-regression parameters, class definitions, software
versions, and single-thread rule recorded before the fit.

This artifact is deliberately labeled **POST-DEVELOPMENT DEPLOYMENT
ESTIMATOR**. It is not a reconstruction of the five historical out-of-fold
estimators, it is not new held-out development evidence, and no performance
metric was calculated from its in-sample predictions. It cannot change the
frozen `NOT_SUPPORTED / NEGLIGIBLE` Model D conclusion.

## Transparent state

The estimator is stored as JSON rather than a Python pickle. It records:

- exact feature and output-class order;
- `StandardScaler` sample count, mean, variance, and scale;
- logistic-regression coefficient class order, coefficients, intercepts,
  iteration count, and fixed parameters;
- the frozen training-matrix and development-freeze identities; and
- explicit zero-access flags for LongBench and Model D.

The coefficient rows use scikit-learn's native alphabetical class order, which
is saved separately. Deployment probabilities are deterministically reordered
to the frozen scientific class order.

Primary artifacts:

- `configs/model_c_deployment.json`
- `metadata/model_c_deployment_estimator.json`
- `metadata/model_c_deployment_estimator_receipt.json`
- `metadata/model_c_deployment_attempt.json`
- `scripts/materialize_model_c_deployment.py`

The receipt pins the training input, config, script, state, attempt, environment,
and a canonical hash of reconstructed full-cohort predictions. The prediction
hash is a reproducibility check, not a reported performance result.

## Verification

From the repository root, using the exact Model C environment:

```bash
python3.11 scripts/materialize_model_c_deployment.py --verify
python3.11 -m unittest tests.test_model_c_deployment -v
```

The fit mode is fail-closed once the durable attempt marker or either output
exists. The script has fixed repository paths and no network, LongBench,
structure, download, or arbitrary-path interface.
