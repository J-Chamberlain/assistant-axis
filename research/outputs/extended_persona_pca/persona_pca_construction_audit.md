# Persona PCA construction audit

Generated UTC: 2026-09-11T23:18:54Z
Analysis model: GPT-5.5

## Why the project previously used three PCs

The original geometry builder explicitly instantiated `PCA(n_components=3)` for the role-vector 3D visualization and a separate two-component fit for the 2D view. No saved scree, parallel-analysis, bootstrap-stability, or cumulative-variance decision selected three as the scientific dimensionality. PC4 and later components were outside the original display target, not rejected.

## Variables and observations

Rows are the 275 lexically ordered persona/role artifacts. Columns are hidden-state activation coordinates after each saved role tensor is mean-pooled across its stored layer rows. PCA is ordinary centered role-vector PCA. The named 240 traits do not enter any persona PCA fit; they are used only later for descriptive same-space associations.

| Model | Input rows | Activation-coordinate columns | Stored source tensor shape | Construction |
|---|---:|---:|---|---|
| Qwen/Qwen3-32B | 275 | 5120 | (64, 5120) × 275 | mean-pool stored rows, stack roles, center columns, full SVD |
| Llama-3.3-70B | 275 | 8192 | (80, 8192) × 275 | mean-pool stored rows, stack roles, center columns, full SVD |
| Gemma-2-27B | 275 | 4608 | (46, 4608) × 275 | mean-pool stored rows, stack roles, center columns, full SVD |

The centered matrix rank cannot exceed 274 because there are 275 observations. The audit retains all 274 mathematically available nonzero directions and verifies full reconstruction.

## Orientation and compatibility

Qwen PC1-PC3 are sign-oriented to the canonical `geometry_viz_data.json` coordinates. Llama and Gemma PC1-PC3 follow the established project rule: recompute PCA in each model's own activation space, then orient each same-index sign by its correlation with the Qwen reference score. Later-component signs use a deterministic largest-absolute-loading convention; signs do not affect variance, stability, or subspace conclusions.

- Qwen/Qwen3-32B: orientation signs for the saved full PCA begin `[1, 1, 1, 1, 1, -1, -1, 1, -1, -1]`; PC1-PC3 reproduction maximum absolute error `1.207e-06`; full reconstruction relative Frobenius error `3.874e-15`.
- Llama-3.3-70B: orientation signs for the saved full PCA begin `[1, -1, -1, 1, -1, -1, -1, -1, 1, -1]`; PC1-PC3 reproduction maximum absolute error `2.748e-14`; full reconstruction relative Frobenius error `4.065e-15`.
- Gemma-2-27B: orientation signs for the saved full PCA begin `[1, 1, 1, 1, -1, 1, 1, 1, -1, -1]`; PC1-PC3 reproduction maximum absolute error `1.376e-11`; full reconstruction relative Frobenius error `3.605e-15`.

## Variance language

**Explained variance is the fraction of total squared variation among the 275 centered role activation vectors captured by a PCA direction. It is not a percent of personality, behavior, psychological variation in humans, or causal importance.**

## Sources

Saved role-vector root: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors`. Canonical coordinate and cluster sources are `research/visualizations/geometry_viz_data.json`, `research/geometry_tables/`, and the established multimodel PCA reconstruction in `research/outputs/multimodel_ordered_trait_region_viewer/`.

No GPU, RunPod, model inference, activation extraction, or external model API was used.
