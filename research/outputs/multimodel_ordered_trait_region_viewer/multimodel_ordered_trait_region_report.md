# Multi-Model Ordered Trait-Region Viewer

Generated UTC: 2026-06-05T17:00:31Z
model_used: GPT-5.5

## Startup and Source Status

Startup verification was run before generation using the raw `STARTUP_MANIFEST.md`, `RESEARCH_STATE.md`, `THREAD_START.md`, and `CLAIMS_REGISTER.md` files from GitHub. The canonical file hashes matched the manifest.

## What Was Built

Created a single integrated HTML viewer for ordered trait-region overlays across available Qwen, Llama, and Gemma released-vector artifacts. The viewer supports model selection, ordered x/y PC-axis selection, quantile or fixed-grid region basis, label count selection, point coloring by cluster/region/assistant-axis, role-point click details, and region click details.

The important methodological rule is enforced in the generated data: the selected x-axis defines the conditioning bands. `PC1 x PC2` asks how PC2 varies within PC1 bands; `PC2 x PC1` asks how PC1 varies within PC2 bands. These are not treated as equivalent.

## Available Models

- qwen: available, 275 roles, 240 traits, coordinate source `canonical_geometry_viz_data`.
- llama: available, 275 roles, 240 traits, coordinate source `recomputed_layer_mean_role_vector_pca_oriented_to_qwen_reference`.
- gemma: available, 275 roles, 240 traits, coordinate source `recomputed_layer_mean_role_vector_pca_oriented_to_qwen_reference`.

## Ordered Axis Views Generated

Generated 18 ordered model/axis views for each basis, covering all six ordered PC pairs per available model. Combined cell table rows: 531.

## Dependencies Used

- qwen: role vectors `downloads/hf_vectors/qwen-3-32b/role_vectors`, trait vectors `downloads/hf_vectors/qwen-3-32b/trait_vectors`, reference geometry `research/visualizations/geometry_viz_data.json`.
- llama: role vectors `downloads/hf_vectors/llama-3.3-70b/role_vectors`, trait vectors `downloads/hf_vectors/llama-3.3-70b/trait_vectors`, reference geometry `research/visualizations/geometry_viz_data.json`.
- gemma: role vectors `downloads/hf_vectors/gemma-2-27b/role_vectors`, trait vectors `downloads/hf_vectors/gemma-2-27b/trait_vectors`, reference geometry `research/visualizations/geometry_viz_data.json`.

## Local-vs-Global Label Difference

- Quantile views mean top-3 local/global overlap across views: 0.199.
- Fixed-grid views mean top-3 local/global overlap across views: 0.214.
- Low overlap means local x-axis-band-relative labels differ materially from global cell labels, so the selected conditioning axis matters.

## Axis Reversal

Observed: reversing axes changes the conditioning baseline and changes local enrichment labels. Largest quantile-view reversal differences by mean local/global overlap:

- qwen PC2xPC3 overlap 0.133 vs PC3xPC2 overlap 0.267; absolute difference 0.133.
- qwen PC1xPC3 overlap 0.089 vs PC3xPC1 overlap 0.222; absolute difference 0.133.
- gemma PC1xPC2 overlap 0.133 vs PC2xPC1 overlap 0.200; absolute difference 0.067.
- gemma PC2xPC3 overlap 0.133 vs PC3xPC2 overlap 0.178; absolute difference 0.045.
- llama PC1xPC3 overlap 0.289 vs PC3xPC1 overlap 0.244; absolute difference 0.044.
- llama PC2xPC3 overlap 0.222 vs PC3xPC2 overlap 0.267; absolute difference 0.044.

Inferred: reverse views should be inspected as distinct hypotheses rather than as cosmetic axis swaps.

## Cross-Model Interpretation Notes

Observed: Qwen, Llama, and Gemma all have complete local released role/trait vector dependencies, so no model was excluded. Qwen uses canonical `geometry_viz_data.json` coordinates; Llama and Gemma coordinates are recomputed from layer-mean role vectors and sign-oriented to the Qwen reference geometry.

Inferred: Qwen and Llama remain the most comparable pair for PC1/PC2 based on prior cross-model diagnostics. Gemma should be treated as secondary/contextual because prior diagnostics already found divergence from Qwen/Llama in effective psychological taxonomy.

Speculative: publication-worthy views are likely the ordered PC1/PC2 and PC2/PC1 panels for Qwen and Llama, because they directly test whether local PC2 and PC1 interpretations survive conditioning-axis reversal. PC3 views are useful for exploration but should stay lower-confidence.

Unknown: whether these same-space trait-cosine labels would survive independent human/LLM trait ratings or response-derived trait scoring.

## Sparse Cells

- Quantile basis sparse cells: 0.
- Fixed-grid basis sparse/empty cells: 105.
- Quantile views are the stable default because they control sample size. Fixed-grid views are descriptive and should not be overinterpreted in sparse regions.

## Browser Verification

- Local HTTP preview was opened through the Browser plugin at `http://127.0.0.1:8766/research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_viewer.html`.
- Default Qwen PC1 x PC2 quantile view rendered as dependency-free SVG with 275 role points, 15 region cells, and 15 cell labels.
- Control switching was tested by changing to Llama PC2 x PC1; the reversed ordered-axis view rendered with 275 role points, 15 region cells, and 15 cell labels.
- Verified preview image saved as `research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_viewer_preview_full.png`.

## Manual Inspection Recommendations

1. Compare Qwen PC1xPC2 against Qwen PC2xPC1 to see how PC2-local labels change when PC2 becomes the conditioning axis.
2. Compare Qwen and Llama PC1xPC2 for broad PC1 organization, then inspect Gemma as a divergence case.
3. Treat PC3 ordered views as exploratory until cross-model PC3 alignment is stronger.
4. Inspect sparse fixed-grid cells only as visual prompts, not as stable enrichment estimates.

## Interpretation Constraints

- Treat labels as activation-space trait-vector enrichments, not independent psychological ratings.
- Do not claim Big Five/Dark Triad validation from this viewer.
- Do not claim PC2 or PC3 is solved from visualization alone.
- The selected x-axis defines the conditioning baseline and must be reported with any screenshot or interpretation.
