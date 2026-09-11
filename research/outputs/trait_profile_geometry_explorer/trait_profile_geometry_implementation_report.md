# Interactive trait-profile geometry equalizer — implementation report

## Result

An active companion explorer now displays the 275 canonical Qwen personas in 2D or 3D PC space while a separately styled point shows the selected persona's genuinely held-out Ridge prediction. All 240 activation-derived trait affinities are editable in percentile units. Edits update one predicted counterfactual point through the same Ridge model that excluded the selected persona.

The companion was used instead of editing `research/visualizations/persona_geometry_explorer.html`. The canonical builder owns only its embedded geometry block, while the larger interface is monolithic and has a second string-patch integration step. On this parallel branch, a source-built companion is safer and reproducible. The canonical explorer hash remained `82d8e7f3d659ca441551c5db06ec5bba508f669fb3bf54abe184f38ef3277dce` throughout generation and verification.

## Predictor artifacts consumed

- `research/outputs/trait_profile_pc_predictor/trait_profile_pc_predictor_report.md`
- `research/outputs/trait_profile_pc_predictor/ridge_predictor.json`
- `research/outputs/trait_profile_pc_predictor/leave_one_persona_out_predictions.csv`
- `research/outputs/trait_profile_pc_predictor/ood_reference.json`
- `research/outputs/trait_profile_pc_predictor/predict_trait_profile.py`
- `research/outputs/trait_profile_pc_predictor/run_trait_profile_pc_predictor.py`
- `research/outputs/trait_profile_pc_predictor/source_manifest.json`
- `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`
- `research/visualizations/geometry_viz_data.json`
- `data/traits/trait_list.json`

The source matrix has 275 personas × 240 traits. Persona order exactly matches canonical geometry; trait order exactly matches the predictor and OOD bundles; all names are unique; all values and coordinates are finite; all 240 traits have an existing canonical definition.

## Interface behavior

- Selecting a point or a name loads the complete 240-trait profile.
- A connected equalizer shows baseline and edited percentile profiles.
- Every trait has a native slider, current value, definition access, and individual reset.
- Search, changed-only, and reset-all controls remain usable across 240 dimensions.
- Both 2D and 3D keep the full persona distribution, selected actual point, held-out predicted point, connector, PC values, delta vector, and 3D displacement.
- Axis changes project the unchanged predicted 3D coordinate onto the selected pair.
- Camera, dimensional mode, and PC-axis choices survive trait edits.
- The optional q95 whiskers are labeled `Empirical held-out error reference`.
- The OOD panel shows the saved heuristic label, five-neighbor distance, corpus-relative distance percentile, range count, and nearest profiles.

## Held-out and browser agreement

The generator fitted 275 per-persona transparent raw-cosine Ridge bundles with the validated LOPO split, scaling, inner-CV seed, and alpha grid. Every model has 274 training personas and names the one excluded persona.

**Observed implementation checks:**

- Maximum generator reproduction error versus saved raw-cosine LOPO predictions: `2.3163693185779266e-12`.
- Maximum independent Python reproduction error across all 275 personas: `2.0818902157770935e-12`.
- Maximum JavaScript-core reproduction error across all 275 personas: `2.2666313270747196e-12`.
- Maximum live-Chrome browser reproduction error across all 275 personas: `2.2666313270747196e-12`.
- Thirty deterministic three-trait edit cases were compared with Python.
- Maximum JavaScript-core modified prediction disagreement: `5.684341886080801e-13`.
- Maximum live-Chrome modified prediction disagreement: `2.7000623958883807e-13`.
- Maximum JavaScript-core OOD scalar disagreement: `1.4210854715202004e-14`.
- Maximum live-Chrome OOD scalar disagreement: `1.3322676295501878e-15`.
- Percentile inverse-mapping disagreement: `0` in deterministic reference cases.
- 2D projection, reset profile, multi-trait determinism, and camera-preservation errors: `0`.

These are software-reproduction results, not new evidence about behavioral generalization.

## Regression and live-browser status

The pre-existing trait-ridge Python verification, trait-surface Python verification, and trait-surface Node/DOM verification all passed. The new explorer also passed a live headless Google Chrome 152 interaction test over a local HTTP server, with 275 personas, 240 sliders, plot selection, list selection, native slider input, changed-only filtering, reset-all, 2D/3D switching, and camera persistence exercised. Chrome was forced to the CPU-based ANGLE SwiftShader WebGL backend; no hardware GPU was used.

## Scientific interpretation boundary

**Observed:** The browser implements the saved transformation and per-persona held-out Ridge mappings to strict numerical tolerance.

**Interpretation:** Users can inspect ordinary held-out prediction error and explore model-predicted counterfactual motion while seeing whether an edited profile remains near the canonical profile manifold.

**Hypothesis:** A behaviorally elicited novel persona will occupy the displayed counterfactual coordinate. This viewer does not test that hypothesis. Trait edits are not causal interventions, and the interface is not a human personality measure.

## Compute and external services

No GPU, RunPod, new model inference, new activation extraction, or external model API was used. LOPO Ridge bundle generation and verification ran locally on CPU over saved artifacts. Plotly is loaded in the viewer from the same pinned CDN version used by the canonical explorer; the saved predictor, profile, and geometry data are embedded for local use.
