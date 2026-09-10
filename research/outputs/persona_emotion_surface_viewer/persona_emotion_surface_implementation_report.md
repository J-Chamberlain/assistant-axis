# Qwen Emotion Surface Viewer: Implementation Report

Date: 2026-09-09
Status: prototype implemented; startup guard patched after user-reported loading failure; user-browser confirmation pending.
Branch: `master`. Implementation base commit: `e7513f60697ee52d5ef3b6f1c3962756e54c22d5`.
Author: Codex; exact runtime model identifier unavailable. Source activation model: Qwen/Qwen3-32B.

### UI Control Update (2026-09-09)

The existing emotion viewer was updated in place from its saved data bundle. The surface now uses a more saturated fixed symmetric z-score palette, the `Persona nodes` control provides a true fabric-only view by hiding nodes, pins, connectors, and the zero reference, and synchronized yaw/pitch/roll/zoom controls provide numeric entry plus Isometric, Top, Front, and Side presets. These are presentation controls only: the six emotion scores, 275 persona coordinates, meshes, and emotion semantics were not regenerated or changed.

The new `camera_controls.js`, `verify_emotion_surface_controls.cjs`, and `emotion_surface_control_checks.json` are indexed with the viewer. The control test covers 225 camera round trips, pole handling, all six emotions and ordered PC views, node visibility, camera persistence, rapid updates, presets, and numeric input using Plotly/DOM doubles. It is not a live WebGL browser test.

## Open and Explore

### Startup Follow-Up (2026-09-09)

Observed: the user's local Chrome tab remained on the initial loading message. The numerical outputs were already generated; this was a display/startup failure, not ongoing model inference. The preceding browser checks used a clean Chromium 151 profile, while installed Chrome is 152.0.7977.83. These facts do not identify the root cause. Inferred: the main initialization did not reach its status update. Unknown: whether the user's page encountered blocked JavaScript, a script exception, or a renderer issue. The browser tool blocked inspection of the local-file tab; no alternate browser-access route was used to bypass that restriction.

The patch adds a small independent startup guard before the chart library, captures early runtime errors and rejected promises, reports the startup stage, and times out after 15 seconds instead of silently waiting. A bundled static Joy preview is shown until successful startup; a `noscript` message explains disabled JavaScript. The chart library now follows the visible page markup. Failure does not launch any new computation. The initial static status no longer claims that generation is loading.

`viewer_bootstrap.js` implements this guard. `verify_viewer_bootstrap.cjs` and `viewer_bootstrap_checks.json` record passing Node/DOM-double tests for progress, errors, timeouts, recovery, preview visibility, and HTML ordering. These are not browser tests. The earlier `persona_emotion_surface_browser_checks.json` is explicitly marked historical and retains the original tested HTML hash. Actual user-profile interactive rendering remains unconfirmed; the next diagnostic is the warning/error displayed after the user refreshes the file. Do not report the underlying startup failure as resolved until that confirmation.

The patch uses `run_persona_emotion_surface_viewer.py --ui-only`, preserving the saved 1,650 scores and mesh data byte-for-byte. No rescoring, model generation, API calls, GPU work, security-setting changes, or external hosting was performed.

Open `persona_emotion_surface_viewer.html` in a local WebGL-capable browser. The 6.70 MB HTML embeds Plotly, data, styles, and scripts, so it works without a server or internet connection. Choose two different PCs, then use the six-stop slider or emotion buttons. Drag to rotate, scroll to zoom, hover a node for its name, and click or use the persona selector to pin details. Reset view restores the starting camera; small screens use a farther starting camera so the axes fit.

Joy, Calm, Sadness, Fear, Anger, and Disgust select existing `joyful`, `calm`, `sad`, `afraid`, `angry`, and `disgusted` directions. The slider is categorical, not an ordered scale of valence. Brief morph frames are visual transitions only. Reduced-motion preferences disable those transitions.

## Implemented Scope

- All 275 Qwen personas and all six ordered pairs of the existing PC1/PC2/PC3 coordinates, with no PCA refit or point movement.
- Exactly 1,650 scored persona/emotion rows; per-emotion population z-scores and empirical midrank percentiles over the fixed full persona set.
- Smooth thin-plate-spline fabric, a subtle mesh, and three predeclared smoothing settings. Neutral nodes remain at their actual scored heights; connectors expose differences from the fitted fabric.
- Convex-hull and local-density support masks; no filling of unsupported regions with zeros. Reversed axes transpose the same fit.
- Fixed vertical/color limits across emotions and planes. Color and height both mean normalized affinity, not assistant-axis projection or cluster.
- Persistent persona selection and camera; click-versus-drag handling and a live-camera snapshot address observed Plotly 3D picking/wheel-update inconsistencies.
- An accessible persona selector, keyboard range control, sticky emotion slider, mobile layout, and downloadable scores.
- Separate companion artifact: the main geometry explorer and unrelated pre-existing worktree changes were not modified.

## Measurement and Provenance

The implementation follows the approved plan, using released role row 47 with the emotion bank extracted at `hidden_states[48]`. This is supported by inspected decoder-block ordering and the prior empirical finding that block 48 equals `hidden_states[49]`. The historical emotion readout uses story last tokens; the role tensors summarize role responses. The displayed PCA averages role tensors across layers. These differences are documented, not concealed by the shared word "48."

Primary affinity is an uncentered normalized dot product with a saved emotion direction. No direction was retrained, no role was rated by a model, and no observed response emotion distribution was estimated. Sensitivity checks compare the displayed method with adjacent-row, layer-mean, and story-centered/nuisance-removed variants; they do not select whichever variant makes the prettiest landscape. Across six emotions, layer-mean rank correlations are 0.927-0.968 but top-20 overlap is only 0.60-0.90. Story-centering/nuisance removal yields correlations 0.943-0.997 and overlap 0.55-0.95, so fine-grained rankings remain method-sensitive.

Observed: the saved activation artifacts support this relative-affinity visualization. Inferred: it can guide inspection of emotion-associated representational structure. Unknown: whether these transferred story probes measure functional emotional tendencies in role-conditioned responses, how often such states occur, and how stable those tendencies are across prompts. Neither the smooth surface nor normalization resolves those unknowns. A negative z-score means below the across-persona average, not the opposite emotion.

## Startup and Verification

Before implementation, the canonical raw manifest and its three startup files were fetched in order and verified against hashes and local copies at base commit `e7513f6`. The generator additionally checks local canonical startup hashes before scoring. Repository continuity changes regenerate `STARTUP_MANIFEST.md` in the implementation commit.

Data checks passed: exact geometry fidelity, unique 1,650-row coverage, CSV/bundle equality, per-emotion normalization and tied-rank convention, 66 independently recomputed source cosines, all 54 mesh support masks, no clipping, and source/generated-artifact hashes. The manifest records hashes for all 275 role tensors and supporting sources. `persona_emotion_surface_data_checks.json` records the tests.

Browser checks passed in local headless Chromium with network access blocked: all six emotions, all six ordered PC pairs, fixed height ranges, unchanged node scores under smoothing, persistent camera and pinned persona, native range keyboard/pointer inputs, rapid input coalescing, real node hover/click, real rotation/scroll, and 390-pixel mobile touch emulation with reduced motion and no horizontal overflow. The exact browser version, timings, HTML hash, and zero page-error/network-attempt counts are in `persona_emotion_surface_browser_checks.json`. Timings describe renderer updates in this test environment, not a guarantee for every device. Physical iPhone/Safari testing was not performed.

Desktop Joy and Fear screenshots and a mobile Anger screenshot were captured and visually inspected. Mobile interaction remains most convenient via the persona selector because dense 3D nodes are small touch targets. Sparse support cutouts and node/fabric gaps are deliberate, not data-loss errors. No GPU inference, pods, model API calls, or new activations were used.

## Reproduce

From the repository root, with the source tensors present and NumPy, SciPy, Torch, Plotly, and Node/Playwright installed:

```bash
python3 -B research/outputs/persona_emotion_surface_viewer/run_persona_emotion_surface_viewer.py
python3 -B research/outputs/persona_emotion_surface_viewer/verify_persona_emotion_surface_data.py
node research/outputs/persona_emotion_surface_viewer/verify_viewer_bootstrap.cjs
node research/outputs/persona_emotion_surface_viewer/verify_persona_emotion_surface_browser.cjs
node research/outputs/persona_emotion_surface_viewer/verify_emotion_surface_controls.cjs
```

Package versions are frozen in the output manifest. In this Mac environment, Playwright was resolved through `NODE_PATH=/Users/alfred/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules`. Rebuilding requires the local source tensors; opening the HTML does not. The generator uses one CPU thread with the local OpenMP compatibility setting recorded in source. UI sources are `viewer_template.html` and `viewer.js`; edit those and regenerate rather than editing the embedded library HTML.

## Files and Repository Continuity

The viewer directory contains all created/updated implementation artifacts; each is indexed as active. The prior plan is preserved with an implementation addendum. Canonical updates record the new exploratory tool and remaining validation limits, not a revised PC interpretation. `CLAIMS_REGISTER.md` was explicitly not changed because no behavioral or causal evidential status changed.

Registries updated: `PROVENANCE_REGISTRY.md`, `FINDINGS_LEDGER.md`, `RESEARCH_INDEX.md`, `RESEARCH_STATE.md`, and `THREAD_START.md`. Navigation updated: `REPO_NAVIGATION.md`, `REPO_FILE_INDEX.csv`, and `RAW_URL_INDEX.md`; `STARTUP_MANIFEST.md` regenerated. The Qwen emotion-readout sticky note received an appended implementation update.

Raw GitHub links for every changed file are indexed below and in the canonical raw/file indexes. Links to the HTML are source/download links; use the local file for direct viewing.

| Changed file | Raw GitHub URL |
|---|---|
| `research/outputs/persona_emotion_surface_viewer/viewer_bootstrap.js` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/viewer_bootstrap.js) |
| `research/outputs/persona_emotion_surface_viewer/verify_viewer_bootstrap.cjs` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/verify_viewer_bootstrap.cjs) |
| `research/outputs/persona_emotion_surface_viewer/viewer_bootstrap_checks.json` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/viewer_bootstrap_checks.json) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_viewer.html` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_viewer.html) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_data.json` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_data.json) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_scores.csv` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_scores.csv) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_score_sensitivity.csv` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_score_sensitivity.csv) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_fit_diagnostics.csv` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_fit_diagnostics.csv) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_manifest.json` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_manifest.json) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_methodology.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_methodology.md) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_implementation_report.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_implementation_report.md) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_data_checks.json` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_data_checks.json) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_browser_checks.json` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_browser_checks.json) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_desktop.png` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_desktop.png) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_fear.png` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_fear.png) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_mobile.png` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_mobile.png) |
| `research/outputs/persona_emotion_surface_viewer/run_persona_emotion_surface_viewer.py` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/run_persona_emotion_surface_viewer.py) |
| `research/outputs/persona_emotion_surface_viewer/verify_persona_emotion_surface_data.py` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/verify_persona_emotion_surface_data.py) |
| `research/outputs/persona_emotion_surface_viewer/verify_persona_emotion_surface_browser.cjs` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/verify_persona_emotion_surface_browser.cjs) |
| `research/outputs/persona_emotion_surface_viewer/viewer.js` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/viewer.js) |
| `research/outputs/persona_emotion_surface_viewer/viewer_template.html` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/viewer_template.html) |
| `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_viewer_plan.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_viewer_plan.md) |
| `research/FINDINGS_LEDGER.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/FINDINGS_LEDGER.md) |
| `research/PROVENANCE_REGISTRY.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/PROVENANCE_REGISTRY.md) |
| `research/RESEARCH_INDEX.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_INDEX.md) |
| `research/RESEARCH_STATE.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md) |
| `research/THREAD_START.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md) |
| `research/REPO_NAVIGATION.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/REPO_NAVIGATION.md) |
| `research/REPO_FILE_INDEX.csv` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/REPO_FILE_INDEX.csv) |
| `research/RAW_URL_INDEX.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RAW_URL_INDEX.md) |
| `research/STARTUP_MANIFEST.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/STARTUP_MANIFEST.md) |
| `sticky_notes/2026-05-20_qwen_emotion_readout.md` | [Raw file](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/sticky_notes/2026-05-20_qwen_emotion_readout.md) |

## Next Step

Inspect the six landscapes and flagged node/fabric gaps before adding more emotion directions. If the next question is response-level functional valence rather than centroid affinity, first validate the readout for the actual response extraction boundary and pooling convention. Do not infer an emotion distribution from a single centroid or recover arbitrary emotion projections from only three PC coordinates.

Project impact: the documented design is now a tested offline exploratory viewer, while functional-emotion and response-prevalence claims remain unvalidated.
