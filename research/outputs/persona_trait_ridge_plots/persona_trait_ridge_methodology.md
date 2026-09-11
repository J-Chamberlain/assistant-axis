# Multimodel PC-Ranked Persona Trait Profiles

Date: 2026-09-11 (America/Los_Angeles)  
Status: completed descriptive visualization; no new inference or activation extraction.  
Default model: Qwen.

## Scope

`persona_trait_ridges.html` is the canonical offline viewer for the same 15 editorial traits in Qwen, Llama, and Gemma. The Model selector replaces all three PC-ranked panels without a page reload. The selected persona persists by role name when models change because the released bundles were verified to contain the same 275 role names.

The trait selection and order are unchanged:

| Position | Editorial reading group | Trait |
|---:|---|---|
| 1 | Exploration | creative |
| 2 | Exploration | abstract |
| 3 | Exploration | curious |
| 4 | Response | reactive |
| 5 | Response | adaptable |
| 6 | Response | practical |
| 7 | Scrutiny | skeptical |
| 8 | Scrutiny | analytical |
| 9 | Scrutiny | conscientious |
| 10 | Challenge | rebellious |
| 11 | Challenge | competitive |
| 12 | Challenge | manipulative |
| 13 | Affiliation | empathetic |
| 14 | Affiliation | agreeable |
| 15 | Affiliation | altruistic |

These five groups are editorial reading groups, not fitted latent factors, discovered clusters, valence dimensions, or validated psychological scales.

## Exact Model Sources

Only saved local released tensors were used:

- Qwen role vectors: `downloads/hf_vectors/qwen-3-32b/role_vectors` (275 files).
- Qwen trait vectors: `downloads/hf_vectors/qwen-3-32b/trait_vectors` (240 files).
- Llama role vectors: `downloads/hf_vectors/llama-3.3-70b/role_vectors` (275 files).
- Llama trait vectors: `downloads/hf_vectors/llama-3.3-70b/trait_vectors` (240 files).
- Gemma role vectors: `downloads/hf_vectors/gemma-2-27b/role_vectors` (275 files).
- Gemma trait vectors: `downloads/hf_vectors/gemma-2-27b/trait_vectors` (240 files).

The manifest records a SHA256 bundle digest over sorted filename/content pairs for each directory. The task worktree did not contain a copied `downloads/` cache; generation used the read-only local cache in `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors` through the explicit `--vector-root` argument. No missing bundle was downloaded or substituted.

## Coordinates and Orientation

Coordinate construction calls the functions in `research/outputs/multimodel_ordered_trait_region_viewer/run_multimodel_ordered_trait_region_viewer.py`; it does not define a competing PCA alignment.

- Qwen uses `research/visualizations/geometry_viz_data.json` coordinates exactly.
- Llama and Gemma independently mean-pool every released role tensor across its stored rows, fit three-component PCA to their own 275-role matrix, and orient each resulting PC sign to the corresponding Qwen reference PC with the established cross-role correlation sign rule.
- Llama orientation signs are `[+1, -1, -1]`; Gemma signs are `[+1, +1, +1]` for these saved bundles.
- Llama and Gemma are not projected into the Qwen PCA basis.

All three coordinate arrays agree with the previously validated multimodel ordered-trait viewer to maximum absolute difference `0.0`.

## Activation-Cosine Scores

These are same-space activation-cosine trait profiles.

Qwen retains `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv` as the canonical source so the viewer reproduces the accepted Qwen result exactly. As an audit, the newer multimodel float32 cosine path was also recomputed from Qwen vectors; it differs from the canonical saved matrix by at most `4.389272697635782e-06`, so it is not substituted for the accepted Qwen numbers.

Llama and Gemma use the established multimodel computation: mean each role and trait tensor across stored rows, convert to float32, L2-normalize each mean vector, and take the role-by-trait matrix product. Their displayed data are selected from their own 275-by-240 matrices, never from Qwen.

For every model and trait independently across 275 personas:

`height = 100 * (average_rank(raw_cosine) - 0.5) / 275`

Ties use average ranks. Population z-scores use `(raw - mean) / std(ddof=0)`. The saved score table retains model, raw cosine, z-score, percentile, all three PC coordinates, and all three PC ranks for every displayed model/persona/trait row.

A percentile of 90 in Qwen and 90 in Llama expresses the same within-model rank concept. It does not imply the same absolute cosine, calibrated psychological intensity, or identical psychological semantics. Model selection does not establish psychological equivalence across models.

## Display

Each selected model has three complete panels, ordered independently by that model's descending PC1, PC2, and PC3 coordinates with persona-name tie-breaking. Exact colored dots are data. PCHIP supplies non-overshooting visual connectors between equally spaced categories; the line is not a density or continuous trait factor.

The HTML pre-renders all 2,475 model/panel/persona rows and 37,125 trait nodes, keeps Qwen visible by default, and switches the three model panels in place. It remains self-contained and has no network script or data dependency. Static SVG/PNG exports are provided for all three PCs and an overview for each model; the historical unsuffixed exports remain Qwen aliases.

## Qwen Backward Compatibility

The reference is commit `d68921b898ed179194223f449149d715298cdabe`, the canonical J-Chamberlain master at task start. Maximum Qwen differences are:

- raw trait cosine: `0.0`;
- z-score: `0.0`;
- within-trait percentile: `0.0`;
- PC coordinate: `0.0`;
- PC orders: exact;
- 275 personas, 240 source traits, 15 displayed traits, and 4,125 Qwen score rows: exact.

## Verification

`verify_persona_trait_ridges.py` independently checks model counts and role sets, finite values, 240-trait source coverage, the unchanged 15-trait set, percentile/z calculations, all model-specific PC orders, strict coordinate agreement, exact Qwen reproduction, complete saved rows, pre-rendered markup, and source hashes.

`render_ridge_images.cjs` rasterizes all model-specific static exports and runs a DOM double for default/reset behavior, real coordinate-row replacement, linked selection, and persona-name persistence.

`verify_trait_viewers_browser.cjs` separately uses actual headless Chrome. It opened the self-contained viewer, switched Qwen/Llama/Gemma, verified 825 active rows and 12,375 active trait nodes per model, confirmed coordinate rows changed, preserved `playwright` by name, reset to Qwen, and observed no page errors. This actual-browser result is distinct from the DOM-double tests.

## Reproduction

```sh
python3 -B research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py \
  --vector-root /absolute/path/to/assistant-axis/downloads/hf_vectors
python3 -B research/outputs/persona_trait_ridge_plots/verify_persona_trait_ridges.py
node research/outputs/persona_trait_ridge_plots/render_ridge_images.cjs
python3 -B research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py --inventory-only
```

Static PNG reproduction needs Sharp. Actual browser verification additionally needs `puppeteer-core` and local Chrome; neither runtime package is embedded in the viewer.

No new model inference, response generation, activation extraction, GPU, RunPod, or external model API was used.
