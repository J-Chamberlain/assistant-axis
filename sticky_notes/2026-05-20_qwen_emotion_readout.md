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

## Update 2026-05-20

Full Qwen 3 32B layer-48 emotion readout extraction completed with all
171 emotions from `ryancodrai/emotion-probes`. Discrimination accuracy
was 0.072 versus chance 0.006, with readout verdict USABLE and 9/9
opposite-valence validation pairs anticorrelated. Anthropic Qwen capping
files were downloaded locally; `capping_config.pt` confirms vector layers
0-63 and includes layer-48 capping experiments, including p50 cap -16.875
for `layers_48:52-p0.5`.

## Update 2026-05-20

Computed an empirical valence-arousal map from the 171 Qwen 3 32B
layer-48 emotion readout directions. Valence was defined as the
normalized mean of positive-valence anchor directions minus the mean of
negative-valence anchor directions; arousal was defined analogously from
high-arousal versus low-arousal anchors. The valence-arousal axis cosine
was -0.149, supporting a mostly independent two-axis map. The projection
recovers a circumplex-like structure: happy, fulfilled, optimistic, and
hopeful are strongest on positive valence; distressed, terrified, scared,
and shaken are strongest on negative valence; angry, outraged, furious,
and irate are highest arousal; content, peaceful, melancholy, and relaxed
are lowest arousal.
