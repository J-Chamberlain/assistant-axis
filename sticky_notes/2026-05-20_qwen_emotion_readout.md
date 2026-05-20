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

## 2026-05-20 Update

Cross-model summary added to findings log: Gemma 2 27B, Qwen 3 32B,
and Llama 3.3 70B all show distributed emotion geometry with PC1
variance around 7-9% and opposite-valence anticorrelation preserved.
The Anthropic PCA gate should be treated as a causal-steering benchmark,
not a binary validity criterion for readout.
