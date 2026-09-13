# Aggregate human-profile projection into model persona terrain

Status: aggregate projection complete; all primary Ridge locations require strong extrapolation warnings

## Observed inputs

The analysis uses the frozen aggregate SAPA latent profiles at K=4–10, with K=9 retained only as diagnostic/ineligible. It uses the exact 12 moderate-or-better bridge traits as primary and all 45 `ACCEPT_DIRECT` traits as sensitivity. Each human and model role vector is centered across its selected traits and L2-normalized. The unchanged model terrain contains 275 curated roles per Qwen, LLaMA, and Gemma; human predictions never enter its KDE or coverage thresholds.

No respondent row, ID, response mask, posterior membership, individual score, or imputation is present.

## Model-only validation

All six model/trait-set fits pass the frozen usability gate. Primary 12-trait normalized 3D RMSE is 0.1811 Qwen, 0.4040 LLaMA, and 0.3873 Gemma; mean coordinate R2 is 0.9671, 0.8362, and 0.8494. The 45-trait sensitivity improves normalized 3D RMSE to 0.0812, 0.1610, and 0.1388. Full coordinate results, selected Ridge alphas, residual covariance, and kNN validation appear in `model_projection_validation_report.md` and the model-validation tables.

## Aggregate projected locations

All 40 eligible profiles were projected independently into each model, producing 120 primary 12-trait Ridge locations. Every one lies outside the frozen 95% sampled-role KDE envelope. Every profile also has 0th-percentile trait-shape support relative to the leave-one-out support distribution of the 275 model roles. Consequently, the nominally accurate model-side Ridge map is being applied well outside the role-profile support on which it was validated.

The frozen candidate rule therefore flags all 120 model/profile rows as projected coverage-extension candidates, and every eligible human profile recurs as a candidate in all three models. This is a broad out-of-support warning, not evidence of 40 novel human regions.

## K=6 presentation view

At K=6, median 12-trait Ridge-to-kNN displacement is 10.77 native-PC SD units for Qwen, 20.86 for LLaMA, and 36.41 for Gemma. Median nearest-role distance is 9.42, 14.68, and 34.83 SD units. Median 12-to-45 displacement is 24.44, 20.73, and 166.48 SD units. Median bootstrap fraction inside the model 95% sampled-role envelope is 0.000, 0.001, and 0.000.

## K=10 anchor view

At K=10, median 12-trait Ridge-to-kNN displacement is 8.89 native-PC SD units for Qwen, 20.86 for LLaMA, and 41.82 for Gemma. Median nearest-role distance is 5.81, 15.65, and 39.30 SD units. Median 12-to-45 displacement is 19.40, 20.17, and 149.03 SD units. Median bootstrap fraction inside the model 95% envelope is zero in all three models.

K=10 remains the frozen predictive-likelihood and aggregate-correspondence anchor but has low human split-refit stability. K=6 remains the reader default because it is in the moderate-stability range. Neither is treated as a true human resolution.

## Ridge versus support-constrained interpolation

The model-only kNN diagnostic is much more conservative by construction. Among the 40 eligible 12-trait profiles, its predictions fall inside the frozen 95% role envelope for 39 Qwen, 29 LLaMA, and 30 Gemma profiles. The very large Ridge-to-kNN displacements exceed the model-role warning threshold throughout, so exact geometric placement is method-sensitive. The viewer exposes both predictions and labels Ridge as extrapolative.

## Projection uncertainty

Five hundred fixed-seed bootstrap refits quantify variation in the fitted Ridge map. These model-fit bootstrap envelopes usually remain outside sampled-role coverage and do not resolve the support failure. Cross-validated residual covariance is saved separately and is not combined opaquely with bootstrap spread. Frozen upstream artifacts contain split-refit profile distances but no aligned aggregate profile vectors, so human latent-profile fit sensitivity is recorded as unavailable rather than newly estimated.

## 12-versus-45 sensitivity

The 45-trait models localize held-out model roles more accurately, but aggregate human predictions move substantially relative to the 12-trait primary result—especially for Gemma. No model/profile switches into the 95% Ridge coverage envelope. The richer 45-trait representation therefore does not rescue support and remains sensitivity only.

## Cross-model comparison

The frozen model-only display alignment was reused without human refitting. Human Ridge projections differ greatly across aligned model displays (median mean pairwise distance 23.28 at K=6 and 23.39 at K=10 for the primary representation). This is descriptive evidence of poor localization consistency, not a formal model-comparison test.

## Interpretation and limits

The bounded result is negative for precise aggregate geometric localization: excellent role-held-out prediction within each model does not guarantee supported transfer from human aggregate trait shapes. The frozen mapping mechanically places every profile beyond current sampled-role coverage, but support, estimator, trait-set, and cross-model diagnostics all warn against reading those locations literally.

The viewer is therefore an inspection tool for extrapolation behavior. It does not establish observed human occupancy, actual human activation coordinates, psychometric equivalence, probability, population prevalence, a new basin, stability, accessibility, or shared causal mechanisms. No individual projection, bridge expansion, model-family-informed training, new inference, activation extraction, external model API, GPU, or RunPod work occurred.
