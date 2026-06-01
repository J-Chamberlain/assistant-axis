# Visualization Tool Inventory

## Canonical Include

Latest/main visualization tool: `research/visualizations/persona_geometry_explorer.html`.

Why this version is canonical:

- It is the active Persona Geometry Explorer under `research/visualizations/`, not the older top-level `visualizations/` exploratory pages.
- It uses embedded `VIZ_DATA` and no `fetch(` dependency.
- It supports PCA/UMAP, 2D/3D, axis swapping, fixed ranges, persistent selection, lasso/box selection, cluster colors, and Big Five-style overlays.
- Required rebuild/source data live beside it: `geometry_viz_data.json`, `cluster_assignments_full.json`, and `bigfive_geometry_overlay_data.json/.csv`.

## Explicit Exclusion

Do not include the H100 forecast-vs-observed arrow tools in the first clean repo pass:

- `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_3d_arrows.html`
- `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_2d_arrows_pc1_pc2.html`
- `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_2d_arrows_pc1_pc3.html`
- `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_2d_arrows_pc2_pc3.html`

Those are useful later for the validation/calibration repo, but they would pull the first clean Paper 1.5 core repo toward H100 diagnostics rather than the report spine.
