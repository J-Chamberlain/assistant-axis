# Qwen, Llama, and Gemma Grouped Trait Landscapes

Date: 2026-09-11 (America/Los_Angeles)  
Status: implemented and verified; Qwen is the default.  
Scientific label: same-space activation-cosine trait profiles.

## What the Viewer Shows

`persona_trait_surface_viewer.html` extends the accepted trait ridges into five three-dimensional grouped surfaces for Qwen, Llama, and Gemma. Model switching replaces persona coordinates, group heights, fitted fabric, support mask, flat plane, node-fit diagnostics, hover data, and pinned-node position without reloading the page.

The groups are unchanged:

| Editorial reading group | Three equal-weight members |
|---|---|
| Exploration | creative, abstract, curious |
| Response | reactive, adaptable, practical |
| Scrutiny | skeptical, analytical, conscientious |
| Challenge | rebellious, competitive, manipulative |
| Affiliation | empathetic, agreeable, altruistic |

These are editorial reading groups, not fitted latent factors. For persona `i`, group `g`, and selected model `m`:

`height(i, g, m) = mean(member_trait_within_model_percentiles(i, g, m))`

The three weights are exactly `1/3`. The composite is not re-ranked or re-standardized. Its height range is fixed to 0–100, and exact persona nodes retain the exact group mean. Surface heights are equal-weight means of member percentiles, not probabilities or absolute trait intensities.

## Model-Specific Data

All six logical released-vector directories and their bundle SHA256 digests are recorded in `persona_trait_ridge_manifest.json` and `trait_surface_manifest.json`. Each model has 275 roles and 240 traits, and all three role-name and trait-name sets are identical.

Qwen uses the exact accepted ridge scores and canonical `geometry_viz_data.json` coordinates. Llama and Gemma use their own role-by-trait activation cosines and PCA coordinates. Their PCAs are fit independently to their layer-mean role vectors and sign-oriented to corresponding Qwen PCs by the exact functions already used in `research/outputs/multimodel_ordered_trait_region_viewer/run_multimodel_ordered_trait_region_viewer.py`. Llama and Gemma are not projected through the Qwen PCA basis.

Trait percentiles are computed independently inside each model's 275-persona distribution. Therefore a percentile of 90 has the same rank interpretation across models but not the same raw cosine or necessarily the same psychological meaning. Model selection does not establish identical psychological semantics across models.

## Fabric, Support, and Diagnostics

The original methodology is applied independently to every model.

For each of the three unordered PC planes:

1. Select the model's exact 275 two-PC nodes.
2. Center the two coordinates and divide both axes by one common scale, `sqrt(mean(var(PCs)))`, preserving relative distances.
3. Combine coincident projected nodes only for fitting.
4. Prepare a 61-by-61 grid over that model's coordinate extent.
5. Fit degree-1 thin-plate RBF surfaces at smoothing `0.003` (Detail), `0.03` (Balanced), or `0.3` (Gentle).
6. Mask grid points outside that model's convex hull or beyond its 90th-percentile sixth-neighbor support radius.
7. Clip displayed fabric to 0–100 while retaining exact persona nodes.

Each selected model therefore owns its surface and mask. Relative to the Qwen masks, Llama differs in 1,013 / 1,694 / 1,378 grid cells for PC1-PC2 / PC1-PC3 / PC2-PC3; Gemma differs in 722 / 873 / 675 cells. These differences are verification that switching does not leave a Qwen support mask behind, not scientific claims about which geometry is superior.

For every model, group, and PC plane, the flat comparison is a least-squares plane over intercept plus that model's two normalized PC coordinates. `node_r2` and `node_rmse` compare exact group nodes with that model's plane. `fabric_flat_r2`, `fabric_flat_rmse`, and the clipped `100 * R2` adherence score compare that model's supported rolling fabric with its own flat plane. All are in-sample descriptive diagnostics, not held-out validation.

Across all 135 model/plane/smoothing/group meshes, the total clipped supported cells are Qwen 73, Llama 65, and Gemma 47. This count depends on the model's coordinates, group heights, support, and smoothing; it is not a cross-model quality ranking.

## Controls and Switching

The original ordered PC-axis choices, three smoothing settings, fabric toggle, flat-plane toggle, flat-plane-only mode, persona-node toggle, connector toggle, group slider/buttons, hover/pin behavior, and yaw/pitch/roll/zoom controls remain.

On a model switch, the current PC pair, smoothing, view mode, camera, zoom, visibility toggles, and group remain. If a pinned persona is present, it is looked up by role name in the new model and remains selected. Reset View restores Qwen and the initial camera while preserving the selected persona by name.

## Qwen Backward Compatibility

Against the complete saved Qwen surface data at commit `d68921b898ed179194223f449149d715298cdabe`, the maximum numerical difference is `0.0`. This full recursive comparison covers:

- all 275 role names and PC coordinates;
- all 15 raw/z/percentile member traits;
- all five group heights and mean member z values;
- all three PC-plane grids at all smoothing levels;
- all support masks;
- all fitted-node values and fit RMSEs;
- all flat-plane coefficients, node diagnostics, and fabric-adherence diagnostics.

The Qwen subset retains five groups and 1,375 group rows exactly.

## Verification

`verify_trait_surface_data.py` independently reconstructs group means, support masks, flat-plane fits, and diagnostic values for all three models. It verifies 4,125 unique model/persona/group rows, 135 surface variants, strict Qwen reproduction, bounded meshes, source hashes, and embedded-data identity.

`verify_trait_surface_controls.cjs` is a Plotly/DOM-double suite. It runs 225 camera round trips, all six ordered PC views, all five groups, visibility modes, repeated and queued model switches, selected-model surface/flat diagnostics, stale-trace rejection, camera persistence, and persona-name selection persistence.

`verify_trait_viewers_browser.cjs` is separate actual-browser verification. Headless Chrome 152 loaded real embedded Plotly WebGL, switched all three models repeatedly and rapidly, confirmed that node coordinates, group heights, fabric and flat diagnostics matched the selected model, exercised camera presets/dials after switches, preserved `playwright` by name, reset to Qwen, and produced no page errors. Captured browser images are `multimodel_surface_browser.png` and the companion ridge screenshot.

`trait_surface_preview.svg` and `.png` remain static Qwen scientific previews generated without a browser. They are not browser screenshots.

## Reproduction

```sh
python3 -B research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py \
  --vector-root /absolute/path/to/assistant-axis/downloads/hf_vectors
python3 -B research/outputs/persona_trait_surface_viewer/run_persona_trait_surface.py
python3 -B research/outputs/persona_trait_surface_viewer/verify_trait_surface_data.py
node research/outputs/persona_trait_surface_viewer/verify_trait_surface_controls.cjs
node research/outputs/persona_trait_surface_viewer/verify_trait_viewers_browser.cjs
python3 -B research/outputs/persona_trait_surface_viewer/run_persona_trait_surface.py --inventory-only
```

The completed HTML is self-contained and offline. Build-time Python needs NumPy, SciPy, Plotly, and PyTorch through the ridge loader. Browser verification needs local Chrome plus `puppeteer-core` and is not required to use the saved viewer.

No new inference, response generation, activation extraction, GPU, RunPod, or external model API was used.
