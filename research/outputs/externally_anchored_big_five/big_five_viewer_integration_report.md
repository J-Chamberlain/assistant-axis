# Big Five Viewer Integration Report

Date: 2026-09-11 (America/Los_Angeles)
Status: completed and verified on `codex/aa2-big-five-audit`.

## Integrated behavior

The canonical ridge viewer retains the original **Editorial traits** default and adds a no-reload **Big Five** profile set for Qwen, Llama, and Gemma. Big Five mode offers the four frozen constructions: human-anchored strict (default), human-anchored extended, external-taxonomy expanded, and historical hand-predeclared. It plots the five domain percentiles, retains raw composite projections in hover text, and lists each constituent trait, polarity, and IPIP facet.

The canonical 3D viewer retains the original **Editorial groups** default and adds the preregistered primary **Human-anchored strict Big Five** profiles. Its Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism surfaces use exact model-specific nodes. Every thin-plate fabric, support mask, least-squares flat plane, node-fit diagnostic, flat-adherence diagnostic, and hover record is recomputed from the selected model's coordinates and selected profile data. The Big Five Agreeableness plane is not the editorial Affiliation plane.

Both viewers preserve PC axes, smoothing, visibility state, camera orientation/zoom where applicable, and pinned persona selection by role name across switches. Reset restores Qwen/editorial; ridge reset also restores the strict Big Five construction.

## Backward compatibility

The ridge verifier recursively compared Qwen editorial coordinates, raw cosines, z scores, percentiles, and orders with the accepted artifact at `d68921b898ed179194223f449149d715298cdabe`; every maximum absolute difference is `0.0`. The surface verifier recursively compared Qwen editorial roles, member scores, group heights, all grids/smoothing levels, support masks, fitted nodes, flat planes, and diagnostics with the same accepted reference; its maximum absolute difference is also `0.0`.

Counts remain 275 roles and 240 source traits per model, 15 editorial traits, 4,125 Qwen editorial ridge rows, five editorial groups, and 1,375 Qwen editorial group rows. Big Five adds 4,125 strict surface-node rows across the three models and 270 total surface variants across editorial and strict Big Five modes.

## Verification

- `verify_persona_trait_ridges.py`: pass; exact Qwen reproduction, all model coordinates/orders, all four Big Five constructions, finite raw scores, and independently reconstructed within-model percentiles.
- `verify_trait_surface_data.py`: pass; exact source nodes, bounded fabrics, independently reconstructed support masks and flat planes, 4,125 editorial rows, 4,125 Big Five rows, and 270 variants.
- `verify_trait_surface_controls.cjs`: pass; Plotly/DOM-double state tests, 225 camera round trips, repeated model/profile switching, no stale traces, and persona/camera persistence.
- `verify_trait_viewers_browser.cjs`: pass in actual `Chrome/152.0.7977.84` with real embedded Plotly WebGL. Both viewers switched all models and profile sets; ridge also switched constructions. There were no page errors. Actual-browser evidence is recorded separately from unit/DOM-double tests.
- Static focal PNG/SVG validation renders cover Qwen strict Agreeableness on PC1 × PC3, PC2 × PC3, and PC1 × PC2 with identical axis/display conventions. Their node-plane R2 values are 0.894573, 0.717009, and 0.178453, respectively.

## Scientific labeling

These are same-space activation-derived trait profiles. Big Five percentiles are ranks within each model's own 275-persona distribution. The external taxonomy anchors construction but does not establish independent human psychometric validation or identical psychological semantics across models. Editorial groups remain reading aids rather than fitted latent factors; Big Five surfaces are frozen activation-direction score profiles rather than fitted factors in persona PCA geometry.

## Public-site deployment

**DEPLOYMENT BLOCKED / REQUIRES DISPATCH OR USER ACTION.** The repository still contains no `.openai/hosting.json`, existing public-site project ID, credential, upload command, or documented authorized workflow for replacing the two supplied `chatgpt.site` routes. The exact dependency is access to the existing Site projects (or their hosting manifests/project IDs and authorized publication workflow), followed by dispatch of the preserved `persona_trait_ridges.html` and `persona_trait_surface_viewer.html` bundles to their existing routes. No replacement public site was created.

## Compute boundary

All analysis and surface fitting used CPU computation over saved local released vectors. No GPU, RunPod, new model inference, response generation, activation extraction, or external model API was used.
