# q2_stability

Dyad stability experiments for Paper 2.

## Directory structure

gemma/   — Gemma 2 27B artifacts (layer 45, Gemma cluster taxonomy, Gemma-derived persona centroids)
qwen/    — Qwen 3 32B artifacts (layer 48, Gemma-derived persona labels applied to Qwen — see qwen/outputs/calibration/CENTROID_NOTE.md)

## Important provenance note

The seven persona centroids used in Qwen dyad experiments v5 and v6 were selected from Gemma layer-45 role vectors by find_centroid_reps.py, then applied to Qwen without Qwen-native centroid validation. Weak or negative baseline cosines for synthesizer, contrarian, and editor in Qwen calibration confirm these are not Qwen-native centroids. Qwen-native centroid selection is documented in qwen/outputs/calibration/qwen_centroid_selection.json (generated in the session that created this README).
