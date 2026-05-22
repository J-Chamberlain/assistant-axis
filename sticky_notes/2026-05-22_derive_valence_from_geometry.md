# Derive Emotion Valence Positions from Model Geometry

**Date:** 2026-05-22
**Status:** Pending — flagged for follow-up
**Priority:** Medium — affects validity of waveform visualizations

## The Issue

The signed emotion waveform visualizations
(waveform_adversarial.html, waveform_emotional.html,
waveform_neutral.html) position each of the 171 emotions
on the x-axis according to a hand-assigned valence map.
These values were estimated from the psychological
literature (Russell's circumplex model of affect) and
assigned by hand. They are approximate and may not
reflect how the model itself organizes these concepts
in its internal geometry.

## The Better Approach

Derive the x-axis valence positions empirically from
the model's own emotion vectors. The 171 emotion probe
directions are available as pre-computed vectors in the
lu-christina/assistant-axis-vectors HuggingFace dataset
for Qwen 3 32B. The valence position of each emotion can
be estimated by:

1. Downloading the 171 emotion probe direction vectors
   at layer 48
2. Computing PCA on the 171 vectors
3. Identifying which principal component corresponds to
   valence (the component that separates positive from
   negative affect — this should be PC1 or PC2 based on
   Anthropic's Emotion Concepts paper finding that the
   geometry mirrors the human circumplex)
4. Projecting each emotion vector onto that component
   to get its model-derived valence position
5. Replacing the hand-assigned VALENCE dict in
   extract_waveform_data.py with these empirical values
6. Re-running extraction and regenerating the three
   waveform HTML files

## Why This Matters

Anthropic's Emotion Concepts paper (Sofroniew et al.,
2026) found that the geometry of emotion vectors in
Claude Sonnet 4.5 mirrors the human circumplex model,
with valence and arousal as the dominant axes. If Qwen 3
32B shows a similar structure, the empirically derived
positions would validate the hand-assigned values and
strengthen the paper's claims. If they diverge, the
divergence is itself a finding — the model organizes
emotional concepts differently from the human framework.

## Dependencies

- Emotion probe vectors must be available in
  lu-christina/assistant-axis-vectors for Qwen 3 32B
- Requires a GPU pod (A100, ~1-2 hours, ~$3-5) to
  download and compute
- Should be done before paper submission but not
  blocking for current visualization iteration

## Related Files

- visualizations/data/waveform_data_turn3.json
- /tmp/extract_waveform_data.py (last run version)
- visualizations/waveform_adversarial.html
- visualizations/waveform_emotional.html
- visualizations/waveform_neutral.html
