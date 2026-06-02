# Cross-Model Cluster Visualization Feasibility Update

- Date: 2026-06-02T10:37:33Z
- Reference viewer inspected only: `research/visualizations/persona_geometry_explorer.html`
- No visualization files were modified.

## Feasibility

Model switching is feasible but should be implemented as a separate, reviewed visualization task. The current viewer embeds a single Qwen data object; a multi-model viewer needs a new data artifact containing per-model PCA/UMAP coordinates, cluster labels, nearest-neighbor summaries, and metadata.

## Arrows

Cross-model arrows are not recommended as a first visualization. Independent PCA spaces rotate, especially beyond PC1, and the previous diagnostic found weak same-index PC3 comparability. If arrows are built later, limit them to PC1/PC2 or use an alignment-corrected basis.

## Best Next Visualization

The best next visualization is a model-switching cluster/topology viewer or a cluster-overlap Sankey/alluvial table. This would show broad region preservation without implying that PC3 coordinates are directly interchangeable.
