# Qwen Persona Emotion Surface Viewer: Implementation Plan

Date: 2026-09-09
Status: active design brief; implementation has not started.
Author: Codex, GPT-6.
Generation/activation model represented by the source artifacts: Qwen/Qwen3-32B.
Repository base commit: `9a5068275bcf39b2e5040a59f29f4552658a639c` on `master`.
Startup status: canonical raw startup files and local copies verified against `research/STARTUP_MANIFEST.md` before documenting this plan.
Scope of this change: document the user's requested visualization and the proposed implementation. No viewer, new emotion scores, model generations, GPU work, or model API calls were produced.

## 1. Purpose and Agreed Experience

Create one interactive 3D tool for exploring relative emotion-associated activation strength across the 275 Qwen personas. The user chooses two of the three existing persona principal components for the horizontal plane and an emotion for the vertical dimension.

Each persona node has these coordinates:

- X: the selected persona PC coordinate.
- Y: a different selected persona PC coordinate.
- Z: that persona's normalized affinity for the selected emotion.

The third displayed coordinate replaces the omitted persona PC; it is not another PCA component. The viewer should look like a loose, softly folded fabric or terrycloth sheet, with a continuous surface and visible persona nodes. Hover identifies a persona; dragging rotates the scene; scrolling zooms. Sliding between emotions updates the landscape immediately while preserving the user's viewing angle.

Version 1 is an exploratory map of role-centroid emotion affinity. It does not estimate the frequency with which a persona experiences an emotion, a probability distribution over emotions, or a distribution across generated responses. Functional valence and response-level distributions remain later validation questions.

## 2. Available Inputs and Measurement Constraints

Observed source availability from the preceding read-only repository inspection:

| Input | Coverage and intended use |
|---|---|
| `research/visualizations/geometry_viz_data.json` | Existing Qwen PC coordinates and persona names; preserve these coordinates exactly. |
| `research/visualizations/scripts/build_geometry_viz.py` | Documents the current geometry construction, which averages each released role tensor across layers before PCA. |
| `downloads/hf_vectors/qwen-3-32b/role_vectors/*.pt` | 275 released role tensors with shape `[64, 5120]`; the 64 rows are layers, not repeated response samples. |
| `downloads/hf_vectors/qwen-3-32b/trait_vectors/*.pt` | 240 released trait tensors; optional sensitivity comparisons, not a substitute for the emotion directions. |
| `research/emotions/outputs/emotion_readout_directions_qwen3_32b_full_layer48.pt` | 171 locally extracted, 5120-dimensional emotion directions. |
| `research/emotions/scripts/extract_qwen_full.py` | Source procedure: last-token story activations at `hidden_states[48]`; training-mean subtraction, removal of the leading story-activation PC, and normalization to construct directions. |
| `research/emotions/outputs/readout_verdict_qwen3_32b_full_layer48.txt` | Existing held-out emotion classification diagnostics; not validation of response-level functional valence. |
| `research/emotions/scripts/compute_qwen_valence_arousal.py` | Existing anchor-defined valence/arousal construction; separate from the six individual-emotion measurements proposed here. |
| `research/assistant_axis_methodology/role_vector_structure_audit.md` | Released tensor layout and decoder-block indexing provenance. |
| `research/outputs/a100_two_role_activation_cloud_pilot/boundary_test_report.md` | Empirical finding that `model.model.layers[48]` hook output matches `hidden_states[49]`, not `hidden_states[48]`. |
| `research/visualizations/persona_geometry_explorer.html` | Existing Plotly interaction patterns, camera persistence, point selection, and visual language to reuse. |

The emotion directions were generated locally using stories from `ryancodrai/emotion-probes`; they are distinct from the released Assistant Axis role/trait vectors in the Hugging Face directory.

Before scoring, verify the exact layer correspondence rather than matching filenames containing "48". The candidate matching released role row is index 47 for the emotion extractor's `hidden_states[48]`, subject to confirming the source row convention. Do not silently compare that readout to the corrected response-cloud hook at block 48.

Even after layer alignment, story-last-token directions and response-mean role centroids have different pooling and input distributions. Their use together remains an exploratory transfer assumption. A layer-matched score displayed over the existing layer-averaged PCA is a role-level overlay, not a claim that both were extracted at one identical boundary.

## 3. Initial Emotion Selector

Use individual saved directions for the first version:

| Display label | Saved direction key |
|---|---|
| Joy | `joyful` |
| Calm | `calm` |
| Sadness | `sad` |
| Fear | `afraid` |
| Anger | `angry` |
| Disgust | `disgusted` |

All six keys were observed in the existing 171-emotion artifact. These six channels provide initial coverage; they are not asserted to be exhaustive or statistically independent.

The horizontal slider has six labeled, keyboard-accessible stops. Its order is navigation between categories, not a validated ordering along one valence continuum. A short animation may morph between adjacent landscapes, but any intermediate frame is a visual transition, not a measured mixed-emotion state. Show the active label clearly and avoid reporting intermediate morph values as measurements. Support reduced-motion preferences.

Future versions can add further existing directions without changing the interface model. Composite valence and arousal channels would require their own documented definitions and should not be conflated with individual emotion intensity.

## 4. Scoring and Normalization

Proposed primary raw score: cosine affinity between each role vector at the verified matching layer and the selected saved unit emotion direction. Reuse the saved direction preprocessing and record the exact role normalization/centering choice before computing results; do not silently replace the historical readout procedure.

For each emotion independently, standardize the 275 raw role scores:

```text
z(role, emotion) = (raw_affinity(role, emotion) - mean_across_275_roles(emotion))
                  / population_std_across_275_roles(emotion)
```

- Height 0 means average affinity for that emotion across the 275 personas.
- Height +1 means one standard deviation above that average; -1 means below average.
- A negative height does not mean that the persona expresses the opposite emotion.
- Compute tooltip percentiles with an explicit tie convention, proposed as empirical midranks.
- Preserve raw scores, z-scores, and percentiles in the exported table.
- Normalize against the full fixed set of 275 personas, not the currently visible subset or the six emotions within a persona.
- Retain a fixed vertical range covering all six score sets. Changing the PC pair or camera must not change any emotion score or its normalization.
- Do not clip outliers silently, fabricate missing scores, or render a nearly constant score channel as an informative landscape. Flag such a channel as unavailable/low variation.

The UI label should say "Relative emotion affinity (standard deviations)". Percentiles indicate relative ordering, not probabilities or prevalence. Separate normalization supports within-emotion persona comparisons; equal z-scores for different emotions do not establish equal absolute emotional strength.

## 5. Continuous Surface and Exact Nodes

Use a smooth, regularized surface fitted to the selected PC-plane locations and normalized emotion scores. A radial-basis or comparable smooth surface fit is an implementation candidate; choose and record the method, parameters, and fit diagnostics during prototype work.

Keep persona nodes at their true X, Y, and scored Z coordinates. Where smoothing moves the surface away from a node, draw a subtle vertical connector. Do not move nodes onto the fitted surface or change their PC positions for aesthetic reasons.

This is necessary because nearby or coincident positions in a two-PC projection can have different emotion scores. The omitted PC and remaining activation dimensions still matter. A single smooth height field cannot always pass through every measurement without sharp spikes or contradictions. Preserve that disagreement visibly rather than implying the selected PC pair fully predicts the emotion.

Visual treatment:

- Soft, matte shading and a faint woven mesh to suggest fabric.
- Folds determined by the fitted values; no decorative random height noise.
- Surface extent limited to the data-supported region, with no unrestricted extrapolation beyond the role-location hull.
- Fade or mask sparse areas and large unsupported gaps inside the hull using a documented local-density criterion.
- Treat density shading as support information, not a statistical confidence interval.
- Use a subtle zero-height reference and neutral, contrasting persona nodes.
- Offer surface visibility and smoothing controls; smoothing changes only the surface, never scores or node positions.
- Preserve data values when adjusting the display aspect ratio; mark any vertical exaggeration if introduced.

## 6. Interaction and Color Semantics

- X and Y selectors support all six ordered pairs of distinct PCs: PC1/PC2, PC2/PC1, PC1/PC3, PC3/PC1, PC2/PC3, and PC3/PC2.
- The initial view is PC1 on X, PC2 on Y, with Joy selected.
- The emotion slider updates node heights and the fitted fabric while keeping the camera and axis ranges stable for that PC pair.
- Drag to rotate, scroll/pinch to zoom, and provide a reset-view control.
- Hover shows persona name, selected emotion, raw affinity, z-score, percentile, and the selected PC coordinates.
- Clicking/tapping pins a persona's details; the same persona remains selected when changing emotions.
- Surface color and height encode the same normalized emotion score, using one fixed diverging scale centered on zero.
- Do not reuse Assistant Axis coloring for the fabric or imply that a fabric color means cluster membership.
- The legend distinguishes scored persona nodes from the interpolated regional surface.
- Reuse the existing explorer's layout and interaction conventions where useful. Because that explorer has pre-existing local edits, start with a companion HTML tool rather than overwriting it.

## 7. Implementation Sequence

1. Recheck startup/source integrity and freeze the role list, source checksums, selected layer, direction keys, and scoring conventions in a manifest.
2. Validate the proposed layer pairing and document the remaining story-to-role pooling transfer limitation. If correspondence cannot be established, stop scoring and document the dependency rather than fabricate a surface.
3. Compute the six score sets locally and inspect variation, missing values, normalization, and sensitivity to explicitly documented preprocessing choices.
4. Fit and precompute surface meshes for the six emotions and six ordered PC views. Share/transposed meshes are possible when the surface method is symmetric under swapping axes.
5. Build the companion Plotly viewer with surface and 3D node traces, slider, axis selectors, tooltips, rotation, and persistent selection/camera.
6. Verify the browser behavior, geometry fidelity, surface support, score semantics, and responsiveness. Capture review screenshots.
7. Present the prototype for inspection before adding more emotions or commissioning response-level activation work.

Precomputation should make browser updates inexpensive at 275 nodes. Interactive work must not trigger model inference, GPU use, or API requests. The first prototype should open locally with its data bundled or embedded; document any plotting-library network dependency or bundle the library for offline use.

## 8. Planned Deliverables

Proposed implementation directory: `research/outputs/persona_emotion_surface_viewer/`.

- `persona_emotion_surface_viewer.html`: interactive companion tool.
- `persona_emotion_surface_data.json`: coordinates, scores, mesh data, and provenance needed by the viewer, or an equivalent embedded bundle.
- `persona_emotion_scores.csv`: 1,650 role/emotion records if all six channels pass checks.
- `run_persona_emotion_surface_viewer.py`: reproducible local score/mesh/viewer generation.
- `persona_emotion_surface_methodology.md`: exact scoring, layer, smoothing, support, and interpretation decisions.
- `persona_emotion_surface_manifest.json`: source hashes, direction labels, parameters, and verification results.
- Preview screenshots suitable for reviewing the initial interface.

These are future deliverables. This documentation change creates only this plan and associated repository continuity updates.

## 9. Acceptance Checks

- Every one of the 275 personas appears exactly once per supported emotion, with no invented data.
- X/Y coordinates equal the existing canonical coordinates for the selected PCs, including swapped views.
- Six available emotion directions are explicitly mapped to their displayed labels.
- Each valid z-score column has mean approximately 0 and population standard deviation approximately 1 across the fixed role set.
- Scores are invariant to camera, axis-pair selection, hiding points, and surface smoothing.
- Node heights equal exported scores; surface deviations remain visible and documented.
- Coincident/nearby projected points and sparse regions do not cause unexplained spikes, fabricated certainty, or silent point movement.
- Slider changes preserve rotation and scale and update without a reload; keyboard and touch interaction work.
- Hover/click identifies the correct persona after every change.
- Labels never imply response frequency, subjective experience, a probability distribution, or an independently validated psychological rating.
- Browser/data checks and screenshots are reviewed before calling the prototype complete.

## 10. Remaining Questions and Later Work

Unknown until implementation checks: how much of each emotion score is organized smoothly over each selected PC plane, how sensitive affinity is to preprocessing/pooling transfer, and how much smoothing can be applied without hiding local variation. A visually attractive surface is not evidence that a PC interpretation is correct.

Later response-distribution work can consider the locally preserved 1,200 trickster and 192 editor response vectors and 1,690 Run 2 control/directional-response vectors after validating an emotion readout for their actual extraction boundary. The 60 amateur and 60 playwright cloud rows retain text and 3D coordinates, but full-dimensional response vectors were not found locally in the preceding inspection. Three PCA coordinates alone cannot recover arbitrary emotion projections.

Current decision: the visualization is feasible as an exploratory centroid-affinity landscape. The user requested that the plan be documented before implementation; implementation remains the next task, not part of this documentation change.
