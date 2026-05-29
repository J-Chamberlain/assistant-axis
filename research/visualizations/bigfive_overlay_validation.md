# Big Five Overlay Validation

Date: 2026-05-29
model_used: GPT-5.5

## Source Data

Selected source: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_full_feature_matrix.csv`.

Reason: this is the shared latent feature benchmark feature matrix containing the five `big5_*` columns. The corresponding benchmark summary reports `claude_bigfive` against `canonical_activation_pca3d` with mean held-out PCA3D R2 = 0.612979, compared with semantic baseline mean R2 = 0.389397.

Residual source: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_persona_residual_rankings.csv`.

Geometry source: `research/visualizations/geometry_viz_data.json`.

## Dataset Checks

- Geometry personas: 275.
- Personas with Big Five scores: 273.
- Missing Big Five scores: `coral_reef`, `devils_advocate`.
- Overlay outputs written to:
  - `research/visualizations/bigfive_geometry_overlay_data.json`
  - `research/visualizations/bigfive_geometry_overlay_data.csv`

## Viewer Checks

Implemented modes:

- Cluster color.
- Axis projection color.
- Openness color.
- Conscientiousness color.
- Extraversion color.
- Agreeableness color.
- Neuroticism color.
- Dominant Big Five trait categorical color.
- Big Five residual magnitude color.

Static validation completed:

- HTML remains self-contained: no `fetch(` usage.
- Embedded `VIZ_DATA` remains present.
- Embedded `BIGFIVE_OVERLAY` is present.
- Extracted inline JavaScript passes `node --check`.

Interactive headless browser validation was attempted, but Playwright is not installed in the local Node environment available to Codex. No browser runtime errors were observed because a browser run could not be completed in this environment.

## Caveats

Big Five fields are LLM-assigned feature scores from the shared benchmark, not true psychological measurements. Per-persona Big Five predicted PC coordinates were not found in the persisted local benchmark artifacts, so `predicted_pc1_from_bigfive`, `predicted_pc2_from_bigfive`, and `predicted_pc3_from_bigfive` are null in the overlay dataset.
