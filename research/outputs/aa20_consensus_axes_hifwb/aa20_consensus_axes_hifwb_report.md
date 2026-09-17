# AA-20 HiFWB associations of supported model–human consensus axes

**Headline decision: B. Reliable association without incremental validity.** The primary analysis uses fixed AA-19 human representations and the frozen human HiFWB outcome; no model-persona score is calculated.

## Phase gate

**Observed:** AA-19 hashes/classes, SAPA source and key hashes, the 13-item outcome, and Big Five keys pass. The frozen HiFWB reconstruction gives 8,664 eligible respondents before predictor coverage. The common primary rule yields 2,859 respondents. No future-safe C1–C3 or Big Five predictor item overlaps an outcome item.

## Composite results

| Axis | Zero-order r | Big Five-adjusted coefficient | Bootstrap 95% CI | Sign stability | VIF |
|---|---:|---:|---:|---:|---:|
| C1 | -0.318 | -0.076 | [-0.136, -0.023] | 0.993 | 3.61 |
| C2 | +0.339 | +0.051 | [+0.002, +0.095] | 0.981 | 2.24 |
| C3 | +0.305 | +0.021 | [-0.037, +0.077] | 0.768 | 3.23 |

| Axis | AA-20 classification |
|---|---|
| C1 | Big Five-redundant association |
| C2 | Big Five-redundant association |
| C3 | Big Five-redundant association |

**Observed:** The primary incremental test comparison is Big Five plus C1–C3 against Big Five alone.

| Model | Test N | R² | RMSE | MAE | Calibration slope |
|---|---:|---:|---:|---:|
| Intercept | 564 | -0.001 | 0.824 | 0.675 | 0.745 |
| BigFive | 564 | 0.493 | 0.586 | 0.460 | 1.154 |
| C1_C3 | 564 | 0.179 | 0.746 | 0.596 | 1.140 |
| BigFive_plus_C1_C3 | 564 | 0.498 | 0.583 | 0.457 | 1.147 |
| HumanFactors5 | 564 | 0.429 | 0.622 | 0.486 | 1.070 |
| BigFive_plus_HumanFactors5 | 564 | 0.518 | 0.572 | 0.444 | 1.070 |

Big Five test R²=0.493; Big Five+C1–C3 test R²=0.498; ΔR²=+0.005, paired bootstrap 95% CI [-0.006, +0.018], label-permutation p=0.033. The interval crosses zero, so the frozen incremental criterion does not pass. AA-13 used a different broad-PC predictor set and a smaller eligible test sample, so its R² is contextual only, not a direct benchmark.

## Indicator results

**Observed:** 39/39 axis-by-indicator tests survive the frozen Benjamini–Hochberg correction. The full estimates, sample sizes, and corrected values are in `indicator_axis_associations.csv` and `indicator_multiple_testing.csv`.

## Interpretation

The results describe associations among independently scored human proxy representations and HiFWB. They do not establish causal effects, model wellbeing, persona wellbeing, or human psychological traits in a model. C1 is a factor combination and C2 is partial by AA-19 design; C3 has a factor-count-sensitive single-factor interpretation. Five-versus-six-factor and C3 subspace checks preserve the small, non-reliable Big Five increment rather than creating a new basis for projection.

## Hypothesis

If an association survives the held-out and sensitivity tests, it may reflect human trait covariance shared with the frozen model-consensus bridge. Training, instruction tuning, the provisional trait mapping, and general human personality structure remain alternative explanations.

## Projection gate

**Not passed.** AA-20 does not authorize model-persona projection: the incremental outcome criterion did not pass.

No model inference, RunPod, paid compute, persona wellbeing projection, or viewer deployment occurred.
