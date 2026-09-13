# Model-only projection validation

Status: frozen model-only validation stage

Method freeze: `58529805ce25f0c1e6ab2716fad4eaa8bc4b80e0`

This stage selects and evaluates the projection machinery using only the 275 saved model roles per model. No human PC coordinate was computed or inspected during validation. The human aggregate files were used only to recover the already-frozen 12- and 45-trait identities and ordering.

## Ridge validation

| Trait set | Model | PC1 OOF R2 | PC2 OOF R2 | PC3 OOF R2 | PC1 RMSE | PC2 RMSE | PC3 RMSE | normalized 3D RMSE | mean R2 | alpha | Gate |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 12 | Qwen | 0.980600 | 0.966700 | 0.953974 | 4.181990 | 3.918850 | 3.378231 | 0.181077 | 0.967091 | 0.0001 | USABLE |
| 12 | LLaMA | 0.918312 | 0.830365 | 0.759774 | 0.326774 | 0.426848 | 0.343609 | 0.404047 | 0.836150 | 0.001 | USABLE |
| 12 | Gemma | 0.973737 | 0.827388 | 0.747147 | 83.964093 | 158.910593 | 128.279167 | 0.387335 | 0.849424 | 0.0001 | USABLE |
| 45 | Qwen | 0.995842 | 0.991577 | 0.992721 | 1.936050 | 1.970883 | 1.343477 | 0.081215 | 0.993380 | 0.00001 | USABLE |
| 45 | LLaMA | 0.965773 | 0.979890 | 0.976303 | 0.211519 | 0.146966 | 0.107920 | 0.160986 | 0.973989 | 0.0001 | USABLE |
| 45 | Gemma | 0.997663 | 0.985221 | 0.959131 | 25.045922 | 46.499224 | 51.572857 | 0.138774 | 0.980671 | 0.000001 | USABLE |

The normalized 3D RMSE is the square root of the mean squared coordinate error after dividing each native PC coordinate by its model-role target SD. The mean-coordinate baseline is approximately 1.002 under the same convention for every model and trait set.

## Interpolation diagnostic

Nested model-only validation selected distance-weighted kNN with `k=5` for Qwen and `k=3` for LLaMA and Gemma for both trait sets. Its normalized 3D RMSE under the same coordinate-averaged convention was:

| Trait set | Qwen | LLaMA | Gemma |
|---:|---:|---:|---:|
| 12 | 0.336573 | 0.478139 | 0.463251 |
| 45 | 0.259796 | 0.419292 | 0.373399 |

Ridge outperformed the interpolation diagnostic for every model and trait set. kNN is retained only as the preregistered support-constrained diagnostic.

## Gate conclusion

All six model/trait-set combinations pass the frozen usability gate: normalized 3D RMSE is at most 0.90, mean coordinate R2 is at least 0.20, all three coordinate R2 values are positive, and Ridge beats the mean-coordinate baseline. This authorizes aggregate human-profile projection under the frozen method without changing the primary/sensitivity ordering: 12 traits remain primary and 45 traits remain sensitivity.

These validation results establish model-side predictive localization only. They do not establish psychometric equivalence or actual human activation coordinates.
