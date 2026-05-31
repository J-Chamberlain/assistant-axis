# Training Forecast Error Geometry

model_used: GPT-5.5

## Forecasting Model

- Exact model: role-trained leakage-control elastic-net TF-IDF
- Model hash: `7863f7626ead1e7ee7a4404f1e7e10171517f29a083d39f1cd1a38c7adcbdc1f`
- Predictions were recomputed from the frozen serialized forecaster because no saved per-example role prediction table existed.
- Important split caveat: the frozen design forecaster was retrained on all 275 role artifacts, so `heldout_role_prior` marks the prior validation split membership but is not out-of-sample for this frozen-model visualization.
- Input text fields: role description + positive instructions + behavioral questions.
- Role labels excluded: yes, explicit role names replaced by `[TARGET]`.
- Eval prompts excluded: yes.

## Counts

- Examples visualized: 275
- Split counts: `{'train_prior': 220, 'heldout_role_prior': 55}`

## Target-to-Forecast Metrics

| axis | R2 | Pearson | Spearman | RMSE | MAE | signed bias mean |
|---|---:|---:|---:|---:|---:|---:|
| PC1 | 1.000 | 1.000 | 1.000 | 0.559 | 0.449 | 0.000 |
| PC2 | 0.999 | 1.000 | 1.000 | 0.582 | 0.432 | -0.000 |
| PC3 | 0.999 | 1.000 | 1.000 | 0.497 | 0.394 | -0.000 |

## Native Error Geometry

- Mean 3D error: 0.843
- Median 3D error: 0.784
- Forecast closer to origin fraction: 0.898
- Mean radial movement toward origin: 0.615
- Forecast |PC3| <= 5 fraction: 0.291
- Forecast |PC3| <= 2 fraction: 0.102

## Comparison To H100 Forecast-Observed Error

- H100 mean 3D error: 37.291 vs native training-artifact mean 3D error 0.843.
- H100 signed deltas observed-minus-forecast: PC1 -9.114, PC2 28.342, PC3 -8.151.
- Native signed deltas forecast-minus-target: PC1 0.000, PC2 -0.000, PC3 -0.000.
- H100 forecast |PC3| <= 5 fraction: 0.530; native artifact forecast |PC3| <= 5 fraction: 0.291.

## Conclusions

- The forecaster has native origin/centroid bias.
- The suspicious PC3 near-zero forecast clustering is not dominant in the original role-artifact predictions.
- The H100 PC2 upward shift is not present in the original target-to-forecast comparison; it appears during response generation/activation measurement rather than in the native forecaster.
- Recommended next diagnostic step: run the same target-to-forecast visualization for held-out-role-only models and compare against the frozen all-role design forecaster to separate in-sample shrinkage from generalization error.
