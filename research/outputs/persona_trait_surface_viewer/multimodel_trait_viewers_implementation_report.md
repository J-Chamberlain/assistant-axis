# Multimodel Trait Viewer Implementation Report

Date: 2026-09-11 (America/Los_Angeles)  
Branch: `codex/multimodel-trait-viewers`  
Worktree: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis-multimodel-trait-viewers`

## Startup and Base

Startup status: **PASS**. The four canonical raw files were fetched in the required order. Visible titles, canonical/state-role fields, update dates, the RESEARCH_STATE last-commit field, byte counts, and SHA256 hashes matched `STARTUP_MANIFEST.md`.

The local checkout's remote aliases differ from the task wording. Literal local `origin/master` is `safety-research/assistant-axis` at `a98961956072224eaf244eb289d6c01700b63795` and does not contain the research artifacts. The canonical repository referenced by the startup URLs is configured as `myfork`; its fetched `master` was `d68921b898ed179194223f449149d715298cdabe`. The new task branch was created in the requested separate worktree, then fast-forwarded from the upstream ancestor to this canonical J-Chamberlain master before edits. No parallel task branch was merged or cherry-picked.

## Delivered Viewers

- `research/outputs/persona_trait_ridge_plots/persona_trait_ridges.html`
- `research/outputs/persona_trait_surface_viewer/persona_trait_surface_viewer.html`

Both are self-contained/offline to the same degree as their prior versions and default to Qwen. Both add Qwen, Llama, and Gemma selection without page reload.

The ridge viewer pre-renders three PC rankings for each model and preserves linked role-name selection. The surface viewer preserves ordered axes, smoothing, fabric/plane/node/connector visibility, camera orientation, zoom, group selection, hover/pin behavior, and flat diagnostics. Switching model replaces actual selected-model coordinates and scores. Reset restores Qwen; the surface reset preserves the pinned persona by role name.

## Data and Coordinate Construction

Each model has 275 released/local role tensors and 240 released/local trait tensors. The verified role and trait name sets are identical across models. The exact logical sources are:

- `downloads/hf_vectors/qwen-3-32b/role_vectors`
- `downloads/hf_vectors/qwen-3-32b/trait_vectors`
- `downloads/hf_vectors/llama-3.3-70b/role_vectors`
- `downloads/hf_vectors/llama-3.3-70b/trait_vectors`
- `downloads/hf_vectors/gemma-2-27b/role_vectors`
- `downloads/hf_vectors/gemma-2-27b/trait_vectors`

The shared loader imports PCA, vector-loading, normalization, and orientation functions from `run_multimodel_ordered_trait_region_viewer.py`. Qwen uses canonical `geometry_viz_data.json` coordinates. Llama and Gemma fit PCA on their own layer-mean role vectors and use the established corresponding-PC sign orientation to Qwen; signs are Llama `[+1, -1, -1]` and Gemma `[+1, +1, +1]`. Strict maximum coordinate difference against the established multimodel viewer is `0.0` for all three models.

Qwen scores are retained exactly from the accepted primary matrix because the established newer float32 recomputation differs by up to `4.389272697635782e-06`. Llama and Gemma scores use that established float32 activation-cosine path over their own released vectors. Within-trait percentiles are recomputed independently in each model's 275-role population.

## Qwen Compatibility

Reference commit: `d68921b898ed179194223f449149d715298cdabe`.

- ridge raw cosine maximum difference: `0.0`;
- ridge z-score maximum difference: `0.0`;
- ridge percentile maximum difference: `0.0`;
- ridge PC-coordinate maximum difference: `0.0`;
- surface/group/mesh/mask/flat-diagnostic recursive maximum difference: `0.0`;
- roles: 275;
- source traits: 240;
- displayed traits: 15;
- Qwen ridge rows: 4,125;
- groups: 5;
- Qwen group rows: 1,375.

## Verification Results

All deterministic numerical/static checks pass:

- 275 unique roles and 240 unique traits per model;
- identical role-name and trait-name sets;
- finite coordinates and trait scores;
- independently reconstructed within-model midrank percentiles and z-scores;
- exact Qwen reproduction;
- Llama/Gemma strict coordinate agreement;
- model-specific PC1/PC2/PC3 ridge ordering;
- 12,375 unique multimodel ridge rows;
- exact equal-weight surface group means;
- 4,125 unique multimodel group rows;
- support masks reconstructed from each selected model's coordinates;
- flat planes and adherence diagnostics reconstructed per model;
- source hashes and self-contained HTML checks.

The Plotly/DOM-double suite passes 225 camera round trips plus repeated and queued switches, stale-trace checks, visibility modes, all ordered PC pairs, camera persistence, and persona-name selection persistence.

Actual browser verification is separately **PASS**, not inferred from DOM doubles. Chrome 152 loaded both local artifacts. The ridge viewer rendered 825 active rows and 12,375 active trait nodes for each model. The surface viewer rendered real embedded Plotly WebGL, switched all models repeatedly and rapidly, matched selected-model coordinates/heights/fabric/flat diagnostics, exercised camera controls after switches, preserved `playwright`, reset to Qwen, and emitted zero page errors. Browser evidence is stored in `trait_viewers_browser_checks.json`, `multimodel_ridge_browser.png`, and `multimodel_surface_browser.png`.

## Scientific Labeling

These are same-space activation-cosine trait profiles. Percentiles are within-model ranks. The five three-trait groups are editorial reading groups, not fitted latent factors. Surface heights are equal-weight means of member percentiles. Cross-model PC orientation follows the existing project procedure. Model selection does not establish identical psychological semantics across models.

This task adds a comparative interface over saved data; it does not change a claim status. It therefore does not add a new claim or Paper 1.5 result.

## Deployment Status

**DEPLOYMENT BLOCKED / REQUIRES DISPATCH OR USER ACTION.** Repository and navigation searches found no `.openai/hosting.json`, public-site project ID, source credential, upload command, or documented workflow for replacing the two existing `chatgpt.site` routes. Creating a new Site would not update those canonical URLs and would invent a deployment mechanism, which the task forbids. The exact dependency is access to the existing two Site projects (or their hosting manifests/project IDs and authorized publish workflow), followed by dispatch/upload of the two preserved HTML filenames to their existing routes.

## Compute Declaration

No new model inference, response generation, activation extraction, GPU, RunPod, or external model API was used. All computation was CPU-only over saved local released vectors and saved repository artifacts.
