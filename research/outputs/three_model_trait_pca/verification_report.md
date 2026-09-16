# AA-14 verification · 2026-09-16

Public viewer: https://persona-trait-landscapes.josiah-chamberlain.chatgpt.site/three_model_trait_pca/trait_pc_persona_viewer

The existing public Sites project deployed version 7 from its source commit `6f3eb744047eed965c9e98eac5363c60dec87de9` with a terminal `succeeded` status. A fresh Chrome tab loaded the HTTPS sibling route directly, rendered the 3D Plotly scene and 275/240 counts, switched Qwen→Llama with the correct 53.5% displayed trait variance, and showed no browser-console errors. A hard refresh returned the same working page. The page does not use localhost or local files. After deployment, the original `/persona_trait_surface_viewer/persona_trait_surface_viewer` route was refreshed and still displayed its fabric and Qwen trait-group controls. The previously deployed original public file was not overwritten in the Sites source update.

Numerical verification: Qwen PC1–3 variance ratios match the saved reference within 2.8e-16 and first-three trait scores within 2.8e-9. All 240 trait names and 275 persona names match in identical order across models. Full rank is 239 per trait PCA. Eigenvalue ratios sum to one and cumulative arithmetic has zero discrepancy within CSV precision. A second seeded full run produced byte-identical SHA1 hashes for `full_spectra.csv`, `trait_pc_scores_all.csv`, `projected_personas_all_pcs.csv`, `cross_model_alignment.csv`, `viewer_data.json`, and `analysis_summary.json`. Seed and draw counts are in `verification.json`.

`verify_outputs.py` independently recomputed all 825 persona projections from the saved source tensors using each model's frozen trait mean and directions. Exported float32 directions/mean reconstruct the first 20 CSV coordinates with maximum absolute error 3.8e-6 Qwen, 5.9e-8 Llama, and 1.6e-4 Gemma; this is below the 0.004 export tolerance and small relative to coordinate scale. For all models, each viewer point matches the source CSV within 5.1e-6 after five-decimal compact rounding; all 3×20³ selector triples address finite coordinates for 515 points per model. The projected-energy plus residual-energy identity passes for every persona. `verification_artifact_checks.json` records the independent checks. No model's activation coordinates were concatenated with another's.

Browser interaction evidence: the local sibling was checked against the deployed original side-by-side. Model switching, PC selection to PC5, trait-only layer, trait search, persona picker and its coordinate/capture/residual/nearest-landmark/OOD details, camera presets/dials, mobile 390×844 viewport, and error logs were inspected. The public route was also tested in a fresh tab, after a hard refresh, and with model switching. Screenshots of the original, local sibling (desktop/mobile), and public sibling were captured during browser QA; they are inspection evidence, not a substitute for the live viewer. No console errors were observed. Plotly is embedded and the compact visualization data is embedded; no local runtime service or raw activation tensor is needed in production.

## Visual fidelity acceptance

| Element | Reuse/adaptation |
|---|---|
| Page shell and header | Reused original `viewer_template.html` HTML/CSS silhouette, eyebrow, title, count placement; copy changed to trait-derived coordinates. |
| Control panel placement/components | Reused top toolbar, sticky second control band, native selects/inputs, right inspection panel. Surface-specific controls were replaced by PC/layer/search/marker controls. |
| Chart container and plotting library | Reused `.canvas-wrap`, `#plot`, original embedded Plotly engine, 3D orbit behavior, dark axes and chart-title position. Default traces are exact scatter3d markers, not a surface. |
| Fonts, colors, spacing | Original Menlo/Consolas monospace stack, dark variables, accent/warm palette, borders, panel spacing, and responsive breakpoints retained. |
| Tooltips, legends | Original Plotly hoverlabel palette and bottom legend layout retained; text now distinguishes projected personas from trait landmarks. |
| Camera | Original `camera_controls.js` reused unchanged with yaw/pitch/roll/zoom dials and Isometric/Top/Front/Side presets. |
| Responsive behavior | Original 850px and 520px rules retained; mobile viewport inspected. |
| Loading/error states | Original startup status/error shell retained; ready status is shown after Plotly renders. |
| Explanation | Original footer `<details>` methodology treatment and small-note styling reused with trait-PCA-specific cautions. |

Limitations: search/filter interactions and representative selectors were exercised in the browser; the combinatorial 24,000 axis triples were checked from the exported coordinate arrays, not clicked individually. OOD flags are descriptive and nearly universal; the viewer does not infer psychometric trait membership. The public route currently uses a long canonical Sites path; the platform rewrites `.html` away in its visible URL, which was verified after reload.
