# Qwen 3 32B Emotion Readout Validation
Date: 2026-05-20

Previous pilot (layers 63 and 48) failed PC1 >= 30% gate but showed
4/4 opposite-valence pairs anticorrelated. Gate was calibrated for
causal steering. Re-ran with readout objective: vectors saved
unconditionally, validated by discrimination accuracy rather than
variance concentration.

Results: layer 63 readout verdict USABLE, discrimination accuracy
0.212 versus chance 0.091, 4/4 opposite-valence pairs anticorrelated.
Layer 48 readout verdict USABLE, discrimination accuracy 0.242 versus
chance 0.091, 4/4 opposite-valence pairs anticorrelated.
Recommended readout layer: 48.
