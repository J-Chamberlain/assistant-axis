# SAPA × HiFWB reproducibility, robustness, and wellbeing-surface test

## Status and scope

**Observed.** This is a human-only, cross-sectional analysis of the public SAPA V5 release (23,679 respondents, 696 items). The historical analysis is exploratory/post hoc and was not preregistered. New score/model definitions were frozen before new outcomes were run. Raw respondent data remain local and gitignored.

Historical source: `gpt/sapa-hifwb-outcome-surface` at `2d93b794065d25d99261de1a5769dbe1eb116706`. Frozen human terrain source: `gpt/sapa-static-human-terrain` at `e385a4664ec46bb53a9d966000728deac06e212b`.

## Historical reconstruction

The 13 direct items reproduce the preserved pairwise diagnostics exactly: mean pairwise Pearson **0.478443**, first eigenvalue **6.793177**, and first-component fraction **0.522552** (all first-component loadings positive). Terrain eligibility is **8,585**; direct-score terrain cohort is **3,972**; non-affect cohort is **2,548**. The original fold assignment is unavailable, so deterministic five-fold seed `20260915` is explicitly marked UNKNOWN.

The reconstructed Big Five→direct score gives OOF Pearson **0.627627**, Spearman **0.620246**, R² **0.393916**, RMSE **0.631316**, MAE **0.500560**. The preservation targets were 0.6276/0.620/0.3939. Non-affect gives Pearson **0.635560**, Spearman **0.635584**, R² **0.403928** (preserved targets 0.6356/0.4039). Differences are attributable to the unrecoverable historical fold assignment and are not tuned.

## Frozen robustness scores

| score | N | OOF Pearson | OOF Spearman | OOF R² | RMSE | MAE |
|---|---:|---:|---:|---:|---:|---:|
| historical 13-item | 3,972 | 0.6276 | 0.6202 | 0.3939 | 0.6313 | 0.5006 |
| non-affect | 2,548 | 0.6356 | 0.6356 | 0.4039 | 0.6422 | 0.5100 |
| content-balanced ≥2 | 3,257 | 0.6406 | 0.6342 | 0.4104 | 0.6223 | 0.4937 |
| content-balanced ≥3 | 1,698 | 0.6979 | 0.6952 | 0.4870 | 0.5707 | 0.4487 |
| six-group vitality auxiliary | 3,257 | 0.6469 | 0.6380 | 0.4185 | 0.6141 | 0.4877 |
| fold-safe PC1-loading-weighted | 8,585 | 0.8855 | 0.8729 | 0.7842 | 0.1848 | 0.1441 |

The loading-weighted score is a sensitivity estimator, not a validated HiFWB scale; its larger N and higher predictability reflect its different missingness handling and should not be compared as if it were the historical score.

Leave-one-content-out results are in `leave_one_content_out.csv`. OOF R² ranges from **0.3779** (drop Self-concept) to **0.4050** (drop Appraisal), with all five content omissions retaining a substantial Big Five association.

## Full terrain versus one-dimensional backbone

All predictions are out-of-fold on the 3,972 historical-score respondents.

| model | Pearson | Spearman | R² | RMSE | MAE |
|---|---:|---:|---:|---:|---:|
| M0 intercept | -0.0487 | -0.0448 | -0.0013 | 0.8115 | 0.6659 |
| M1 frozen backbone cubic | 0.5406 | 0.5363 | 0.2922 | 0.6822 | 0.5429 |
| M2 five-coordinate Ridge | 0.6276 | 0.6202 | 0.3939 | 0.6313 | 0.5006 |
| M3 RBF Nyström/Ridge sensitivity | 0.6193 | 0.6142 | 0.3832 | 0.6368 | 0.5062 |

Compared with M1, M2 improves R² by **0.1017** (bootstrap 95% CI **[0.0867, 0.1176]**); M3 improves by **0.0910** ([0.0772, 0.1060]). M2 exceeds M3 by **0.0107** ([-0.0174, -0.0039]). M3 uses a frozen 120-feature Nyström approximation with at most 1,200 training points per fold for a reproducible CPU-only RBF sensitivity.

**Interpretation.** Under this reconstruction, full five-dimensional position contains predictive wellbeing information beyond the one-dimensional frozen backbone. This is a predictive, cross-sectional result, not a causal terrain or transition claim. It does not establish that the backbone is psychologically fundamental or that the score is a validated HiFWB instrument.

## Epistemic labels

- **Observed:** exact historical common-factor diagnostics; near-exact historical OOF reproduction; robust positive M1–M2/M3 out-of-fold contrasts; content-omission stability.
- **Interpretation:** lateral Big Five position carries information beyond the reconstructed backbone coordinate.
- **Hypothesis:** wellbeing may vary over a genuinely multivariate human personality surface rather than only along a density gradient.
- **Unknown:** effects under the unavailable historical fold assignment, alternative official scoring representations, longitudinal change, causal direction, and generalization beyond SAPA V5.

No human-to-model projection, model persona geometry, inference, activation extraction, or respondent-level data publication was performed.
