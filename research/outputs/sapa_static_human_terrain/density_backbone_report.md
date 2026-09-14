# SAPA Static Human Terrain — Density Backbone Follow-up

## Bottom line

The single-mound result persists, but the dense occupancy body does have a reproducible central direction in five-dimensional Big Five space. That direction is not a thin one-dimensional ridge. The dense core is locally high-dimensional, with median participation-ratio dimension 4.54 and a median of 4 local principal components required to explain 80% of neighborhood variance. The fitted one-dimensional backbone therefore should be interpreted as a centerline through a thick continuous manifold, not as the manifold itself.

The Big Five backbone captures 41.7% of dense-core variance, versus 40.0% for a straight PCA1 axis. Its curvature ratio is 1.191, so the nonlinear centerline is modestly curved rather than strongly folded. The backbone is reasonably stable to changing the density-core definition, but only moderately reproducible across deterministic split halves.

The BFAS result is different. A one-dimensional centerline captures only 32.0% of dense-core variance, local effective dimensionality is much higher (median participation-ratio dimension 7.08; median 6 PCs for 80%), and split-half curves do not align reliably. The ten-dimensional BFAS occupancy body therefore does not support a stable one-dimensional backbone under this frozen method.

## Frozen method

This analysis follows `density_backbone_analysis_freeze.md`, committed before any backbone result was inspected.

The primary dense core is the top 50% of respondents by the already-established kNN local-density measure. Sensitivity cores retain the top 30% and 70%. A deterministic principal-curve approximation is initialized from PCA1, repeatedly forms 21 equal-count bins, computes density-weighted centroids, smooths each trait coordinate with the same fixed cubic-spline rule, reprojects respondents, and iterates five times.

The backbone is descriptive cross-sectional geometry. It is not a behavioral transition path, energy valley, attractor, or causal route.

## Big Five result

Primary cohort N = 8,585; dense-core N = 4,293.

The fitted centerline explains 41.7% of dense-core variance. The straight PCA1 baseline explains 40.0%, and the first two linear PCs together explain 57.2%. Thus nonlinearity adds only a modest amount beyond the dominant linear direction.

Arc length = 4.442; endpoint distance = 3.729; curvature ratio = 1.191. Median dense-core perpendicular distance to the centerline = 1.169 standardized units.

The local-dimensionality diagnostic strongly rejects a thin one-dimensional interpretation. Across dense-core neighborhoods, participation-ratio dimension has 10th/50th/90th percentiles 4.24/4.54/4.74. Four local PCs are required for 80% of neighborhood variance for nearly all dense-core respondents.

The trait trajectory along the fitted centerline is broad and approximately ordered. One endpoint is below the sample mean across all five domains; moving along the centerline raises Agreeableness, Conscientiousness, Extraversion, Emotional Stability, and Openness together, with Emotional Stability and Conscientiousness continuing to rise most strongly toward the far endpoint. The exact 11-point trajectory is saved in `bigfive_backbone_knots.csv`.

This should not be read as a single substantive psychological trait. The joint movement could reflect a broad evaluative/general-personality direction, correlated behavioral organization, measurement structure, or a mixture of these. A post-hoc response-style diagnostic finds almost no relation between arc position and raw response mean (r=0.010) or items answered (r=-0.029), but a moderate relation with within-person response SD (r=0.373). This sensitivity is exploratory because it was not part of the backbone freeze.

Occupancy support falls off strongly away from the centerline. Pooled robust regression of relative log density on squared perpendicular distance gives slope -0.454 and R2=0.816. The same negative falloff appears across nearly all arc-position bins. This is a geometric support gradient only, not a dynamical potential.

## Big Five robustness

Changing the dense-core definition produces similar centerlines. Relative to the primary top-50% curve, the top-30% curve has median separation 0.159 standardized units and the top-70% curve 0.130. Their curvature ratios remain in the same modest range.

Split-half reproducibility is moderate rather than exact. Median curve separation between independently fitted halves is 0.459 standardized units and the 90th percentile is 1.138. Coordinate-wise trajectory correlations are highest for Conscientiousness (0.987), Extraversion (0.974), and Emotional Stability (0.880), and weaker for Agreeableness (0.676) and Openness (0.656).

Thus the strongest defensible statement is that the Big Five mound has a reproducible broad central direction and strong density falloff around it, not that it contains a unique precisely determined curved spine.

## BFAS result

Primary exploratory cohort N = 3,082; dense-core N = 1,541.

The fitted one-dimensional centerline explains 32.0% of dense-core variance. PCA1 explains 26.3% and PCA1+PCA2 39.7%. Local neighborhoods are substantially higher-dimensional: participation-ratio dimension 10th/50th/90th percentiles 6.55/7.08/7.58, with a median of 6 PCs required for 80% of neighborhood variance.

Although the fitted full-sample BFAS curve is visibly curved (curvature ratio 2.021), it is not stable enough for substantive interpretation. Independent split halves have median curve separation 2.478 standardized units and 90th-percentile separation 2.979, with several aspect trajectories changing orientation or shape. The apparent BFAS curve should therefore be treated as unstable exploratory geometry.

Density still falls away strongly with distance from the fitted full-sample centerline (pooled slope -0.410, R2=0.849), but because the line itself is unstable and the manifold is thick, this mainly shows a compact central occupancy body rather than a reproducible one-dimensional behavioral backbone.

## Observed

Big Five and BFAS both form thick, locally multidimensional occupancy bodies rather than thin one-dimensional ridges.

The Big Five dense core contains a reproducible broad central direction that is modestly nonlinear and around which density falls off strongly.

The BFAS space does not yield a stable one-dimensional centerline under split-half validation.

## Interpretation

The human terrain currently looks less like islands joined by narrow corridors and less like a single narrow ridge than like a continuous high-dimensional volume with a broad preferred orientation. In Big Five space that orientation is roughly a joint movement from lower scores across the five broad domains toward higher scores across them, with some curvature.

The phrase `connecting tissue` is therefore better operationalized as the high-density central volume and its principal orientation, rather than as a narrow path between basins.

## Unknown

Cross-sectional occupancy alone cannot determine whether people move preferentially along this direction. It also does not establish whether the broad Big Five orientation is psychological, evaluative, demographic, response-style-related, or some mixture.

## Next required robustness

Per prior user instruction, the next pass should test whether the Big Five central orientation and density falloff remain similar across age, sex, student-status, and country/region strata. Probability-sample population prevalence cannot be recovered from these data alone, so demographic analysis should be framed as structural robustness rather than proof of representativeness.
