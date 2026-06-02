# Visualization Feasibility Note

- Date: 2026-06-02T10:16:43Z
- Main viewer inspected: `research/visualizations/persona_geometry_explorer.html`
- H100 arrow viewer inspected as design reference only: `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_3d_arrows.html`
- No visualization files were modified.

## Current Viewer Structure

The current main viewer embeds a single Qwen `VIZ_DATA` object and renders one active dataset at a time. It assumes one set of PCA/UMAP coordinates, one role list, one cluster assignment list, and one nearest-neighbor map. It does not currently expose a model dimension.

## Required Changes for Model Switching

To add Qwen/Llama/Gemma switching, build a separate multi-model geometry data artifact with per-model role coordinates, explained variance, nearest neighbors, and metadata. Then add a model selector to the viewer and route all PCA/UMAP/color/selection logic through the selected model's dataset.

## Required Changes for Cross-Model Arrows

Cross-model arrows from Qwen coordinates to Llama coordinates are only meaningful if coordinates are put into a shared alignment convention. Independent PCA spaces have arbitrary signs and rotations, especially for weaker PCs. Same-index PC3 is not currently reliable enough for uncaveated arrows.

## Recommendation

Do not modify visualization tools yet. If a visualization is later warranted, start with model switching or PC1/PC2-only cross-model arrows. A PC1/PC2/PC3 arrow viewer should wait for alignment correction or carry a strong PC3 caveat.
