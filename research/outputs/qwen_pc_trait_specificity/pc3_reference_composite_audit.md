# Canonical Three-Trait PC3 Composite Audit

Status: **EXACT CANONICAL REFERENCE LOCATED**.

## Navigation route

The artifact was located through `research/REPO_NAVIGATION.md`, then confirmed
in `research/REPO_FILE_INDEX.csv` and `research/RAW_URL_INDEX.md`. The indexed
source chain is:

- `research/outputs/persona_trait_surface_viewer/persona_trait_group_scores.csv`
- `research/outputs/persona_trait_surface_viewer/trait_surface_methodology.md`
- `research/outputs/persona_trait_surface_viewer/run_persona_trait_surface.py`
- `research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json`

## Exact constituents and formula

The canonical Qwen Editorial `Affiliation` surface uses, in saved order:

1. `empathetic`
2. `agreeable`
3. `altruistic`

For each of the 275 Qwen roles, the viewer computes the within-Qwen midrank
percentile of each saved raw trait-affinity profile, then takes their exact
equal-weight mean. Each weight is `1/3`. The mean is not reranked or
restandardized. The current viewer generator also verifies byte-for-byte Qwen
scientific-data compatibility against commit
`d68921b898ed179194223f449149d715298cdabe`.

## PC1-PC6 benchmark

| Metric | Value |
|---|---:|
| PC1 r | -0.110061 |
| PC2 r | -0.011574 |
| PC3 r | -0.944857 |
| PC4 r | 0.049736 |
| PC5 r | 0.061208 |
| PC6 r | -0.038998 |
| Target PC3 absolute r | 0.944857 |
| Largest off-target | PC1 (-0.110061) |
| Specificity margin | 0.834796 |
| Specificity ratio | 8.584854 |
| PC1-PC6 concentration | 0.978101 |

The reference is secondary and descriptive. No threshold was chosen or changed
to make it pass, and the reference did not affect any single-trait selection.
