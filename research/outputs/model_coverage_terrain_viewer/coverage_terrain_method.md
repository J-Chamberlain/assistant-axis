# AA-12 follow-up 6 — Model-only coverage-terrain method freeze

**Status:** frozen before terrain calculation or visual inspection  
**Date:** 2026-09-13  
**Analysis model:** GPT-5.5  
**Scope:** deterministic CPU-only descriptive analysis of the saved 275-role inventories for Qwen 3 32B, LLaMA 3.3 70B, and Gemma 2 27B.

## Evidentiary boundary

The analysis estimates **sample occupancy**, **role coverage**, and **local sample density** for a curated role inventory. It does not estimate population probability, prevalence, likelihood of a persona or mind, dynamical stability, accessibility, attraction, or repulsion. Human data, human profiles, human/model correspondence outputs, and semantic bridges are prohibited inputs.

Only roles/personas enter occupancy and sparsity estimators. Optional trait points are landmarks and never enter any density, boundary, neighborhood, or gap calculation.

## Frozen inputs

1. Native PCA coordinates: `research/outputs/extended_persona_pca/viewer_data.json` (SHA256 `672c617758ace9654708d5f248e094d3005f19ee5237d3918a159bc0e3d813d3`). It contains the already-established, canonically oriented model-local PC scores. No role vectors will be recomputed.
2. Coordinate provenance: `research/outputs/extended_persona_pca/source_manifest.json` (SHA256 `24aa559170ede3a222cb13793426c5ec90272e610c5328b3f0700e202d0cae7b`).
3. Frozen family membership: `research/outputs/crossmodel_cluster_reconciliation/consensus_family_roles.csv` (SHA256 `212a32b3edc187fa837a6dc31b66b1bf4c05ab3e39bfb837ef1b07068c0ab24c`) and `candidate_consensus_families.csv` (SHA256 `ed109cda337fd9a7e4672ef6c7ed6750139216326ced9ce3a7ab246bc42e3b6c`). Families A–D are broad candidate consensus families; E remains the small, resolution-sensitive secondary family.
4. Optional Qwen-only trait landmarks: `research/geometry_tables/qwen_trait_pc_rankings.csv` (SHA256 `3063da7db511bb31602e070f9f131f4ad5c768887b86fa384010de6bec9ee56c`). These landmarks are visually distinct and excluded from occupancy calculations.
5. Optional display alignment: the already-frozen model-only transform in `research/outputs/human_supported_trait_convergence/procrustes_alignment_matrices.json` (Git object content SHA256 `045f723df1340fb1eccff01eb4c562c8597cde74f449bc64ee7258417be21b96`). Only the two `pc1_pc3__variance_standardized` full-fit transforms to Qwen are used. No human observation, human profile, or human trait result from that analysis is loaded.

All three coordinate sets must contain exactly 275 unique, identical role labels. Any mismatch stops generation.

## Native occupancy estimator

- Primary space: each model's own native PC1–PC3 coordinates, preserving the frozen axis orientation.
- Estimator: `scipy.stats.gaussian_kde` with its deterministic Scott bandwidth factor and full covariance matrix.
- Bandwidth: one Scott factor per model; no visual retuning. Sensitivity multipliers are fixed at `0.75`, `1.00`, and `1.25` times Scott.
- Three-dimensional grid: `36 × 36 × 36` points.
- Grid extent: per axis, observed minimum to maximum plus one primary kernel marginal standard deviation on both sides. Kernel marginal SD is the square root of the corresponding diagonal of the KDE kernel covariance.
- Two-dimensional companions: separate covariance-aware bivariate Scott KDEs on native PC1×PC2, PC1×PC3, and PC2×PC3, each on an `80 × 80` grid with the same one-kernel-SD margin rule.
- Color semantics: raw density is retained in tables; displays use within-model density percentile or log-density so raw unit-dependent densities are not compared as absolute quantities across native model spaces.

## Sample-coverage regions

The inner, middle, and outer boundaries target approximately 50%, 80%, and 95% of the 275 sampled role points. For target fraction `c`, the KDE threshold is the empirical role-location-density quantile `1-c` using NumPy's deterministic linear quantile. The achieved fraction is the proportion of role-location densities at or above that threshold and is reported explicitly. These are sample-coverage regions, not confidence or probability regions.

The interactive cloud uses one isosurface per requested level. Static cloud views use the same frozen grid and thresholds. No threshold is changed per model for aesthetic reasons.

## Density, sparsity, and neighbors

- Primary point density: the fitted 3D KDE evaluated at each sampled role.
- Primary sparsity score: inverse-density ordering expressed as a within-model percentile rank from 0 (densest) to 100 (sparsest). Raw inverse density is also retained.
- Diagnostic sparsity: mean Euclidean distance to the `k=10` nearest roles after standardizing each model-local PC1–PC3 axis by its sample SD. This prevents PC1's larger raw variance from mechanically dominating the diagnostic.
- Nearest-role table: the same standardized native PC1–PC3 Euclidean metric, `k=10`, excluding the role itself; deterministic lexical role name breaks exact distance ties.
- Cross-model neighborhood recurrence: for each role, Jaccard overlap of its `k=10` neighbor sets for Qwen–LLaMA, Qwen–Gemma, and LLaMA–Gemma, plus their unweighted mean. This is descriptive local-topology recurrence, not coordinate equivalence.

## Bandwidth sensitivity

At each frozen multiplier, calculate role-location densities, within-model density ranks, Spearman rank correlation with the primary ranks, densest-decile and sparsest-decile Jaccard overlap with the primary, and grid-density correlation with the primary over the common primary grid. Major density ordering is called smoothing-robust only when rank correlation is at least `0.90`; major dense/sparse extremes are called robust only when their Jaccard overlap is at least `0.70`. These labels are descriptive and frozen before outcomes.

## Families and overlap display

- Family membership is copied exactly from the frozen model-specific support flags.
- Core/majority/fringe metadata are preserved.
- Family colors are fixed: A `#2D7FF9`, B `#E45756`, C `#54A24B`, D `#B279A2`, E `#F2CF5B`; unassigned roles are gray.
- Family-specific geometry is a translucent **convex sample envelope**, not a density cloud and not a probability region.
- Minimum family size for any envelope is frozen at `N >= 10` roles in that model. Smaller groups, including model-specific E representations, are shown as points only and labeled small/resolution-sensitive. No smooth density is fit below the threshold.
- Family-envelope intersections may be inspected visually. This analysis will not interpret overlap volume probabilistically.

## Cross-model display

Native model panels and linked role selection are primary. Raw native coordinates are never directly overlaid.

A secondary **display-aligned shared-role view** uses the frozen variance-standardized orthogonal Procrustes transforms for LLaMA→Qwen and Gemma→Qwen in PC1–PC3. Qwen is standardized using the corresponding frozen target mean/scale; each source is standardized using its frozen source mean/scale and right-multiplied by the frozen rotation. These are aligned display coordinates, not universally shared native PC meanings. The alignment is fitted on the same 275 shared roles and is descriptive, not an independent validation.

## Viewer and static rendering

- Viewer data are embedded locally in a standalone HTML file with the Plotly JavaScript bundle embedded; core use has no network dependency.
- Default view: Qwen native PC1–PC3 persona points plus the 80% sample-coverage boundary.
- Controls: model, native/aligned compare, 3D or three 2D pairs, points, coverage boundaries, density surface, density/sparsity/family color, family visibility/envelopes, optional Qwen trait landmarks, role search/selection, and camera reset.
- Selecting a role highlights that exact shared label in all linked model panels.
- Static plots use the same source tables, grids, thresholds, family colors, and no manual point repositioning.

## Determinism and stopping rules

No stochastic procedure is required. The recorded fallback seed is `120926` and may only be used by rendering libraries that unexpectedly require a seed. The generator stops on missing/non-finite coordinates, duplicate or mismatched role labels, family-label disagreement, trait points entering any role-density array, advertised coverage-fraction mismatch beyond the discretization implied by 275 roles, or use of a non-frozen coordinate/alignment source.

No gap candidates will be declared in this first viewer. Low-density fields and distance-to-nearest sampled roles are offered for neutral exploration only.
