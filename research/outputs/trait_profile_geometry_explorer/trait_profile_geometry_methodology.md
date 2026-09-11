# Trait-profile geometry equalizer methodology

## Scope

This companion viewer is a deterministic interface over the validated Qwen/Qwen3-32B trait-profile-to-PC mapping. It performs no model inference and extracts no new activations. It does not test whether a newly elicited persona occupies a predicted coordinate.

The inputs and target share activation-space provenance:

- Input profile: 240 cosine similarities between a mean-pooled, normalized Qwen role vector and the canonical mean-pooled, normalized Qwen trait vectors.
- Human-facing control: an empirical percentile relative to the 275 canonical Qwen persona profiles.
- Target: canonical Qwen role PC1/PC2/PC3 coordinates from `research/visualizations/geometry_viz_data.json`.
- Mapping: raw-cosine Ridge regression.

The interface therefore visualizes a same-space learned geometric relationship. It is not a human personality instrument, and a trait edit is not a causal intervention.

## Companion-viewer decision

The canonical explorer is a monolithic generated HTML file. Its canonical builder, `research/visualizations/scripts/build_geometry_viz.py`, regenerates geometry data and replaces only the embedded `VIZ_DATA` block; it does not own the larger interface source. A second integration script applies brittle string-level edits. Extending that chain on a parallel branch would make regeneration and later conflict resolution unsafe.

The active companion at `research/outputs/trait_profile_geometry_explorer/trait_profile_geometry_explorer.html` therefore preserves the required canonical 275-point 2D/3D distribution behavior while leaving `research/visualizations/persona_geometry_explorer.html` byte-identical. The companion is built from `viewer_template.html`, `trait_profile_geometry_core.js`, `viewer.js`, and generated data/model bundles by `run_trait_profile_geometry_explorer.py`.

## Persona-held-out models

There is one transparent Ridge bundle for each of the 275 personas. For persona index `i`, the generator exactly repeats the validated raw-cosine LOPO procedure:

1. Remove persona `i` completely.
2. Use the other 274 profiles and targets only.
3. Tune alpha over `0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000` with shuffled four-fold inner CV and seed `10000 + i`.
4. Fit fold-local feature and target `StandardScaler` transforms with Ridge.
5. Export direct coefficients and intercepts from raw 240-trait cosine input to unstandardized PC1/PC2/PC3 output.

On selecting persona `P`, the UI always uses `P`'s excluded-persona bundle. The unedited profile reproduces the saved raw-cosine LOPO prediction; edits continue through the same bundle, so selecting or editing never reintroduces `P` into predictor fitting.

## Percentile conversion

Browser-side conversion mirrors `predict_trait_profile.py`:

- Raw to percentile uses the average index between left and right binary-search insertion positions, divided by `n - 1`, then clamped to 0–100.
- Percentile to raw uses linear interpolation at `percentile / 100 * (n - 1)` in the saved sorted per-trait reference values.
- Controls clamp values to 0–100.
- Reset uses the original raw profile value, not a percentile round-trip, so it exactly restores the held-out baseline.

All predictions remain raw-cosine Ridge predictions. Percentiles are only the editing interface and inverse-mapping mechanism.

## Geometry display and equalizer

The viewer renders all canonical personas by the existing seven cluster labels in either 3D PC1/PC2/PC3 or any 2D PC pair. The selected actual point is a white diamond; the predicted point is a yellow circle with a direct label; a connector shows their displacement. Optional axiswise whiskers show the saved q95 absolute LOPO errors and are explicitly labeled as an empirical held-out error reference.

All 240 traits have native sliders, exact names, current percentile values, per-trait reset, canonical definitions where available, search, changed-only filtering, and reset-all. A horizontally scrollable connected profile shows the muted selected-persona baseline behind the edited profile. Plot `uirevision` and the last 3D camera state preserve the view during edits.

## OOD context

The viewer reuses `ood_reference.json` and the deployed CLI calculation:

- standardize the raw 240-trait profile with the saved all-corpus standardizer;
- project into the five retained profile-PCA components (at least 95% training variance);
- calculate nearest and mean five-nearest distances in score space, excluding the selected persona from the neighbor list;
- percentile the five-neighbor distance against canonical leave-one-out distances;
- calculate the discarded-space reconstruction error and its reference percentile;
- count raw trait values outside the saved corpus ranges;
- apply the saved in-distribution / edge / out-of-distribution heuristic thresholds.

This OOD reference is an all-corpus deployed-profile context, not a persona-held-out uncertainty model and not a calibrated probability. The selected-persona prediction itself is still generated by the persona-held-out Ridge bundle.

## Reproduction and verification

Run from the repository root with the project environment:

```bash
python research/outputs/trait_profile_geometry_explorer/run_trait_profile_geometry_explorer.py --n-jobs 4
python research/outputs/trait_profile_geometry_explorer/verify_trait_profile_geometry_explorer.py --write-report
node research/outputs/trait_profile_geometry_explorer/verify_trait_profile_geometry_core.cjs
python research/outputs/trait_profile_geometry_explorer/verify_trait_profile_geometry_browser.py --write-report
```

`--reuse-lopo` rebuilds browser data, reference cases, manifests, and HTML without refitting already verified held-out bundles. `--inventory-only` refreshes hashes and URLs after report or registry edits.

The test layers are intentionally distinguished:

- `verification_report.json`: independent Python artifact and reference-implementation checks.
- `node_verification_report.json`: browser-core JavaScript numerical checks for all held-out baselines and 30 modified cases.
- `browser_verification_report.json`: real headless Google Chrome rendering and interaction checks, including list selection, plot selection, sliders, changed-only, reset, 2D projection, and camera persistence. This test forces ANGLE SwiftShader software WebGL and records the renderer, so it does not use a hardware GPU.

## Epistemic labels

**Observed:** Saved inputs contain 275 unique personas and 240 unique traits; every held-out bundle excludes its selected persona; unedited and deterministic edited predictions reproduce saved Python references within the recorded numerical tolerances.

**Interpretation:** The interface faithfully exposes the already validated same-space mapping and makes its known held-out error and profile-manifold context visible during edits.

**Hypothesis / unresolved:** A newly elicited persona may or may not occupy the predicted coordinate. Testing that requires a separate behavioral-validation experiment and is outside this viewer.
