# SAPA Static Human Terrain — Density Backbone Analysis Freeze

Status: frozen before inspecting any density-backbone result.

## Purpose

The completed Big Five and BFAS analyses found a single connected occupancy body and no material secondary density peaks. This follow-up therefore does not search again for discrete basins. It asks whether the dense population body contains a reproducible lower-dimensional high-support backbone, how curved that backbone is, which trait combinations characterize movement along it, and how quickly occupancy support falls away from it.

This is a static cross-sectional occupancy analysis. A backbone is a descriptive centerline through high-density trait space, not a transition path, causal trajectory, attractor, energy valley, or path of least resistance.

## Representations

Run the same procedure separately in:

1. five-dimensional IPIP100 Big Five space using the already-frozen primary cohort and scoring;
2. ten-dimensional BFAS aspect space using the already-frozen primary exploratory cohort and scoring.

No model-side geometry enters the analysis.

## Primary density core

Reuse the established kNN density estimator for each representation. Define the primary dense core as the top 50% of respondents by local density. Sensitivity cores are the top 30% and top 70%.

## Local dimensionality diagnostic

Before interpreting a one-dimensional backbone, estimate local effective dimensionality in the dense core. For each core respondent, compute the covariance matrix of its 60 nearest core neighbors for Big Five and 30 nearest core neighbors for BFAS. Record the participation-ratio dimension `(sum eigenvalues)^2 / sum(eigenvalues^2)` and the number of local principal components needed to explain 80% of neighborhood variance.

A one-dimensional backbone may still be fit as a centerline if local dimension exceeds one, but must then be described as a centerline through a thicker manifold rather than as the manifold itself.

## Backbone estimator

Fit a deterministic principal-curve approximation to the dense core only.

1. Standardize coordinates using the full primary cohort means and SDs already used for terrain analysis.
2. Initialize curve order with the first principal-component score of the dense core.
3. Divide respondents into 21 equal-count bins along the current curve parameter.
4. For each bin, compute a density-weighted centroid, with weight proportional to `exp(relative_log_density - max_relative_log_density)` within the dense core.
5. Fit a cubic smoothing spline independently for each trait coordinate through the 21 centroids as a function of normalized arc parameter. Use smoothing factor equal to `0.5 * number_of_bins` for every coordinate; no smoothing factor is tuned from outcomes.
6. Sample the curve at 201 equally spaced parameter values, project each dense-core respondent to the nearest sampled curve point, replace the curve parameter by normalized cumulative arc length at that projection, and repeat steps 3–6 for five iterations.
7. The final 201-point curve is the primary density backbone.

If the algorithm collapses, self-intersects severely, or fails deterministic convergence, report failure rather than retuning.

## Primary backbone summaries

Report:

- arc length;
- straight endpoint distance;
- curvature ratio = arc length / endpoint distance;
- mean and median respondent distance to the backbone within the dense core;
- variance captured by nearest-point reconstruction relative to total dense-core variance;
- PCA1 variance captured as a linear baseline;
- PCA2 cumulative variance as a thickness/context baseline.

At 11 equally spaced arc-length positions, report the trait coordinates of the backbone and the local median density of respondents projecting near that position.

## Support falloff

For every primary-cohort respondent, compute distance to the nearest backbone point. Within ten equal-count bins of backbone arc position, fit a robust linear regression of relative log density on squared perpendicular distance. Report slope and R2 per bin and pooled. This characterizes how rapidly occupancy support falls away from the backbone locally.

Do not interpret this falloff as an energy or causal potential.

## Split-half reproducibility

Refit the full procedure independently in the deterministic split halves already used in prior terrain analyses. Align curve orientation by minimizing endpoint matching distance. Compare curves at 101 equal arc-length fractions and report median and 90th-percentile Euclidean curve separation plus coordinate-wise correlations of the 101-point trait trajectories.

## Density-core sensitivity

Repeat the backbone fit for top-30% and top-70% density cores. Align orientation to the primary curve and report median curve separation and curvature ratio.

## Interpretation rules

Observed findings may describe a reproducible high-density centerline, its trait trajectory, local dimensionality, and cross-sectional density falloff.

Do not call the backbone a transition corridor unless longitudinal data later show movement preferentially follows it. Do not call it a personality type. If local effective dimension is substantially above one, explicitly describe it as a centerline embedded in a thicker continuous manifold.

## Deferred demographic robustness

After the structural backbone analysis, run the already-promised representativeness robustness pass using age, sex, student status, and country/region where support permits. Demographic reweighting or stratification must not be used to tune the present structural method.
