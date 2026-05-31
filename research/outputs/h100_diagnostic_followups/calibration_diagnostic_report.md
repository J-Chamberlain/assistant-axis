# Calibration Diagnostic Report

Axis-wise observed = a + b * predicted calibration was fit as a first-pass diagnostic. LOOCV values are preliminary because this is still the same 100-prompt validation set.

| axis | uncalibrated R2 | in-sample calibrated R2 | LOOCV calibrated R2 | slope | intercept | uncalibrated RMSE | LOOCV RMSE |
|---|---:|---:|---:|---:|---:|---:|---:|
| pc1 | 0.321 | 0.478 | 0.463 | 0.831 | -9.134 | 20.323 | 18.087 |
| pc2 | -2.721 | 0.413 | 0.390 | 0.846 | 27.064 | 30.948 | 12.527 |
| pc3 | -0.243 | 0.241 | 0.211 | 0.710 | -7.282 | 13.637 | 10.862 |

Conclusion: calibration looks promising enough to be the next task, but it is not a resolved fix until tested on held-out prompts.
