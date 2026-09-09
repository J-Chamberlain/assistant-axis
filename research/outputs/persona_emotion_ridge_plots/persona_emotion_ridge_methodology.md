# Qwen Persona Emotion Ridges

Date: 2026-09-09. Startup: canonical raw manifest/state/thread/claims hashes and local bytes verified before work. Base commit: `5568ea4d89e39230df175f74864c73bd444777bc`, branch `master`.

## What To Open

Open [the completed three-plot viewer](persona_emotion_ridges.html). The plots are fully embedded as HTML/SVG before JavaScript runs: there is no loading phase, external chart library, network request, or build template to open. Each panel contains all 275 personas, sorted descending on its respective original Qwen PC, with alphabetical tie-breaking. Panels are side by side on wide screens and stacked on narrow screens. Each has its own scroll area, fixed category header, and full SVG/PNG export. Choosing or clicking a persona locates that same persona in all three rankings without reordering any rows.

The static full plots are `persona_emotion_ridges_pc1.svg/.png`, `persona_emotion_ridges_pc2.svg/.png`, and `persona_emotion_ridges_pc3.svg/.png`. Each includes every persona and is 1,000 x 12,340 pixels. `persona_emotion_ridges_overview.svg/.png` is explicitly a top-20-per-PC preview, not the complete dataset. The full PNGs are readable at native size or zoom, rather than scaled to fit their entire height on one screen.

## Available Directions And Selection

Observed: the saved Qwen bank contains 171 named directions of length 5,120. We retained all six channels of the working surface viewer and added four from this same bank, not a different model or layer:

| Left-to-right position | Category | Bank key | Saved valence projection | Selection |
|---:|---|---|---:|---|
| 1 | Fear | afraid | -0.56850386 | Original six |
| 2 | Sadness | sad | -0.52887309 | Original six |
| 3 | Disgust | disgusted | -0.45944560 | Original six |
| 4 | Anger | angry | -0.25724834 | Original six |
| 5 | Loneliness | lonely | -0.08661529 | Added: affiliation-related negative category |
| 6 | Calm | calm | +0.34195125 | Original six |
| 7 | Excitement | excited | +0.49129093 | Added: activated positive category |
| 8 | Joy | joyful | +0.50005740 | Original six |
| 9 | Gratitude | grateful | +0.60586154 | Added: social positive category |
| 10 | Hope | hopeful | +0.62998569 | Added: anticipatory positive category |

The four additions were selected for qualitative coverage and continuity with the original six, not based on attractive persona results, PC correlations, or superior validation. Availability does not establish equal reliability for each channel. The existing full-bank story readout diagnostic reported 171-way accuracy approximately 0.0721 versus chance 0.00585; this does not validate applying those probes to role centroids.

## X Position And Ridge Height

X is an ordered categorical axis. We sort the ten selected categories by the existing `valence_raw` column in `research/emotions/outputs/qwen_valence_arousal.csv`, then space them equally for readable labels. The first five projections are negative and the last five positive. The divider between them is not a measured neutral category. Within-group ordering is an artifact-derived ordering, not a universal psychological ranking. Unequal numeric valence distances are deliberately not encoded as X spacing.

That valence table came from `compute_qwen_valence_arousal.py`: the direction is the normalized difference between the mean of 20 positive-anchor directions and the mean of 20 negative-anchor directions. Anchor lists are saved in `qwen_valence_arousal_axes.json`. It is same-space activation evidence with semantic anchor selection, not an independent psychometric scale. We load the saved ordering; no new valence axis is fitted.

Raw affinity is cosine similarity between each released role tensor's row 47 and each saved emotion direction, with both unit normalized in float64 after conversion from float32. No new story-mean subtraction or nuisance-PC removal is applied to the role vectors, matching the existing surface viewer's primary scoring convention. The saved emotion directions already include their original training preprocessing.

Ridge height is `100 * (average_rank(raw_affinity) - 0.5) / 275`, ranked separately within each emotion over all personas. The common displayed baseline is 0 and common maximum is 100. A height near 90 means that persona ranks near the 90th percentile for that emotion relative to the other personas. No per-persona maximum/area normalization, clipping, rectification, softmax, or probability calculation is used. Negative raw cosine or negative z-score does not mean negative valence: valence determines X category placement, while percentile height describes relative affinity.

Percentiles were chosen so below-average affinities can still be represented as nonnegative ridges without pretending that the magnitude of a negative z-score is strong emotion. They preserve within-emotion ranking, not linear cosine distances. A percentile profile compares relative standings across ten separately normalized channels; it does not identify which emotion is absolutely strongest within a persona. Raw cosine and population z-scores remain in the CSV/JSON and exact-point tooltips.

The line is shape-preserving PCHIP through all ten percentile values. Dots are the exact category scores; interpolation does not overshoot their range. Filled ridges have a common height scale and row spacing, with no overlap or per-persona rescaling. Curves between categories are visual connectors, not measured intermediate states, probability densities, temporal distributions, or prevalence estimates.

## Source Geometry And Boundary

All 275 role names and PC1/PC2/PC3 coordinates come unchanged from `research/visualizations/geometry_viz_data.json`, `roles.names` and `roles.pca3d`. Ranking does not refit PCA. This geometry uses the existing layer-averaged role vectors.

The emotion extractor `research/emotions/scripts/extract_qwen_full.py` used story-last-token `hidden_states[48]`. Released decoder-block row 47 corresponds to that boundary under the source hook ordering. The existing A100 boundary test established that block 48 matches `hidden_states[49]`, not `[48]`; we do not silently use block 48 for these probes. The working surface viewer already audited this convention, and the identical original six scores provide a regression check, not new physiological/behavioral validation.

Story-last-token emotion probes and role-response-mean centroids come from different pooling and input distributions. Their transfer remains unvalidated. The extra directions do not remove this limitation. These plots concern activation affinity, not feelings experienced by a model, behavioral emotion frequency, or evidence that a PC has a uniquely determined meaning.

## Checks And Reproduction

Run from the repository root:

```sh
python3 -B research/outputs/persona_emotion_ridge_plots/run_persona_emotion_ridges.py
python3 -B research/outputs/persona_emotion_ridge_plots/verify_persona_emotion_ridges.py
NODE_PATH=/Users/alfred/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules node research/outputs/persona_emotion_ridge_plots/render_ridge_images.cjs
python3 -B research/outputs/persona_emotion_ridge_plots/run_persona_emotion_ridges.py --inventory-only
```

The first two commands require NumPy, SciPy and CPU PyTorch. The third requires Node and Sharp; `NODE_PATH` is the bundled dependency path on this Mac, not a portable install requirement. The generator records source hashes in `persona_emotion_ridge_manifest.json`, including the 275 local released vector files. The scores CSV has 2,750 unique persona-emotion pairs; each plot has all 275 personas exactly once; the HTML has 825 ridges and 8,250 exact category markers. The full geometry and all original six scores are unchanged; the maximum absolute raw-affinity difference across 1,650 existing rows is exactly 0.0. Per-emotion z-score and percentile normalization, descending PC ranks, finite coordinates, and non-overshooting interpolation pass checks.

Static SVG-to-PNG rendering and Node DOM-double tests pass, including linked persona selection and clearing selection. The overview was visually inspected. These are not browser screenshots or independent live-browser validation. Initial plots do not depend on JavaScript; only linked highlighting does. The user separately reported that the original completed 3D viewer now works after distinguishing it from `viewer_template.html`; that is user confirmation, not a new automated browser test.

## Status And Next Step

Observed: ten-channel centroid affinities, three PC orderings, and static chart exports are available. Inferred: these may help visually compare relative emotion-associated profiles along the existing PC ranking. Unknown: response-level functional emotion transfer and absolute cross-emotion intensity. No new scientific interpretation or paper claim is advanced; `CLAIMS_REGISTER.md` and `FINDINGS_LEDGER.md` are unchanged.

Next step: inspect the three full rankings and identify specific profiles for validation against saved responses before claiming emotional prevalence or experience. No GPU, activation extraction, model generation, or model API call was performed for this task.

## Canonical Links

Raw base: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/`.

- [Completed viewer](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_ridge_plots/persona_emotion_ridges.html)
- [Methodology](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_ridge_plots/persona_emotion_ridge_methodology.md)
- [All scores](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_ridge_plots/persona_emotion_ridge_scores.csv)
- [Source manifest](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_ridge_plots/persona_emotion_ridge_manifest.json)
- [Geometry source](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/visualizations/geometry_viz_data.json)
- [Saved direction bank](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/emotions/outputs/emotion_readout_directions_qwen3_32b_full_layer48.pt)
- [Valence-order source](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/emotions/outputs/qwen_valence_arousal.csv)
- [Valence anchors](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/emotions/outputs/qwen_valence_arousal_axes.json)
- [Original six-score source](https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/outputs/persona_emotion_surface_viewer/persona_emotion_scores.csv)

The accompanying `artifact_inventory.csv` lists every new companion artifact with its raw URL, byte count and SHA256.
