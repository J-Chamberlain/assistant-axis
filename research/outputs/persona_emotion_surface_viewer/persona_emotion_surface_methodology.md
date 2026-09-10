# Qwen Persona Emotion Surface Viewer: Methodology

Generated UTC: 2026-09-09T13:54:27.404590+00:00
Author: Codex; exact runtime model identifier unavailable. Activation model: Qwen/Qwen3-32B.

## What Was Built

An offline HTML viewer with 275 exact persona nodes, six emotion-slider stops, all six ordered PC pairs, three surface smoothing levels, node tooltips and pinned selection, camera persistence, rotation, zoom, surface/connector toggles, and a zero-height reference. The UI also provides a vivid fixed symmetric z-score color scale, a fabric-only mode that hides nodes and reference guides, and synchronized yaw/pitch/roll/zoom dials with Isometric, Top, Front, and Side presets. No model inference, new activations, or judge calls were used; this update changes presentation controls only.

## Sources and Layer Alignment

The displayed PC coordinates are copied exactly from `research/visualizations/geometry_viz_data.json`. Its builder averages released role tensors across all 64 layers before PCA. No PCA is fitted by this tool.

Emotion directions come from `research/emotions/outputs/emotion_readout_directions_qwen3_32b_full_layer48.pt`. The historical extractor uses the last token of supplied emotion stories at `hidden_states[48]`. The released role tensors stack decoder-block outputs in ascending layer order; row 47 is the matching intermediate boundary under the source-documented Qwen hidden-state convention. The prior A100 test independently established that block 48 matches `hidden_states[49]`. This tool therefore uses role row 47, not row 48. This mapping is based on inspected source conventions plus the existing boundary test; no new GPU equivalence test was run.

The remaining transfer assumption is story-last-token emotion directions versus response-mean role centroids. Layer correspondence does not validate functional emotion measurement or eliminate pooling/domain differences.

## Scores

Primary affinity is cosine(role row 47, saved emotion direction). Role vectors are normalized without centering, matching the historical held-out nearest-direction readout's input normalization. Saved emotion directions already incorporate training-mean subtraction and removal of the leading story-activation PC. Unit normalization is repeated only to remove floating-point norm drift. There is no new probe fitting.

For each emotion, z = (affinity - mean of all 275 affinities) / population standard deviation (ddof=0). Percentile = 100 * (average rank - 0.5) / 275. All six channels pass finite/nonzero-variation checks. Reference membership is fixed; selection and smoothing cannot change a node's score. CSV stores unrounded values. A negative z-score means below-average affinity, not an opposite emotion. Separate z-normalization does not make absolute emotion strengths comparable or convert affinity to prevalence/probability.

## Surface

Each PC plane is centered and divided by one common root-mean-axis-variance scale, preserving its relative PC metric. A degree-1 thin-plate-spline RBF fits all six z-score channels jointly with predeclared smoothing 0.003 (Detail), 0.03 (Balanced, default), or 0.3 (Gentle). Parameters were not selected to maximize a scientific result. Coincident projected locations are averaged for the surface only; original nodes stay separate and unchanged. Reversed views transpose the same grid. A 61 x 61 grid is retained only inside the convex hull AND within the 90th percentile of role sixth-neighbor distances (including each role itself when estimating that radius). This masks large unsupported gaps. Missing grid cells are null, not zero; `connectgaps` is false.

Surface heights are rounded to six decimals for the bundle; node scores and coordinates are not rounded. The faint weave follows the fitted surface without random height noise. Thin connectors link node heights to their fitted values when the gap exceeds 0.03 z. Density masking is not a confidence interval. The fixed symmetric Z/color range includes all nodes and all retained grid values across every view and smoothing. No outliers are clipped. X/Y ranges are padded by 4%; Z aspect is a labeled display choice because PC units and SD are unlike quantities. Missing third-PC information can make nearby points disagree; fitting cannot resolve that information loss.

## Sensitivity

The displayed method stays frozen. Alternatives below are diagnostics: adjacent row 48 is deliberately boundary-mismatched; layer mean follows the explorer pooling; story-centering/nuisance removal changes input preprocessing. These are not validated alternative emotion measurements.

| Emotion | Variant | Spearman vs primary | Top-20 overlap |
|---|---|---:|---:|
| joyful | adjacent_row48 | 0.995 | 0.90 |
| joyful | layer_mean | 0.936 | 0.70 |
| joyful | story_mean_centered_pc_removed | 0.997 | 0.95 |
| calm | adjacent_row48 | 0.993 | 0.95 |
| calm | layer_mean | 0.927 | 0.70 |
| calm | story_mean_centered_pc_removed | 0.965 | 0.85 |
| sad | adjacent_row48 | 0.993 | 0.95 |
| sad | layer_mean | 0.968 | 0.85 |
| sad | story_mean_centered_pc_removed | 0.951 | 0.90 |
| afraid | adjacent_row48 | 0.988 | 0.90 |
| afraid | layer_mean | 0.928 | 0.60 |
| afraid | story_mean_centered_pc_removed | 0.978 | 0.90 |
| angry | adjacent_row48 | 0.998 | 1.00 |
| angry | layer_mean | 0.950 | 0.90 |
| angry | story_mean_centered_pc_removed | 0.984 | 0.90 |
| disgusted | adjacent_row48 | 0.989 | 0.85 |
| disgusted | layer_mean | 0.960 | 0.60 |
| disgusted | story_mean_centered_pc_removed | 0.943 | 0.55 |

Surface fit errors are descriptive in-sample node/surface discrepancies, not predictive validation. See `persona_emotion_surface_fit_diagnostics.csv` for all 54 plane/emotion/smoothing combinations.

## Reproduction and Verification

From the repository root:

```bash
python3 -B research/outputs/persona_emotion_surface_viewer/run_persona_emotion_surface_viewer.py
```

The runner verifies local canonical startup hashes before scoring and uses CPU tensors only. Package versions and every input tensor hash are recorded in the manifest. Plotly is embedded with its MIT license header, as are all viewer data and styles: the HTML makes no network requests. Browser QA is recorded separately in `persona_emotion_surface_browser_checks.json` with preview images.

## Interpretation Limits

Observed: this tool calculates relative affinities of saved activation centroids to existing emotion directions. Inferred: those affinities may help locate emotion-associated representational structure across the displayed PC map. Unknown: transfer from story probes to role behavior, response-level prevalence, temporal variability, and subjective experience. A smooth landscape is a visualization of a fitted field, not evidence of an emotion manifold or a solved PC interpretation.
