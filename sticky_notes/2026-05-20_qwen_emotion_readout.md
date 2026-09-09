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

## Update 2026-09-09

Documented a proposed Qwen persona emotion surface viewer at
`research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_viewer_plan.md`.
It would show two selected persona PCs and a normalized emotion-affinity height,
with six emotion-slider states and a smooth fabric surface. Implementation and
new scoring have not started. The source inspection identifies a necessary
alignment check: the emotion extractor uses story-last-token
`hidden_states[48]`, while the corrected response-cloud block-48 hook matches
`hidden_states[49]` and pools response tokens. The existing persona explorer
also averages released role vectors across layers before PCA. The plan preserves
these distinctions; it does not extend the historical readout verdict to
response prevalence or validated functional valence.

## Update 2026-09-09 (Implementation)

The authorized six-emotion persona surface prototype is now implemented in
`research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_viewer.html`.
It scores all 275 released centroids at row 47 against the saved story
`hidden_states[48]` directions, keeps the original PC coordinates, and displays
per-emotion normalized affinity rather than prevalence. Source mapping,
preprocessing sensitivity, support-masked fabric fits, and browser/data checks
are documented alongside the viewer. The historical readout verdict has not
been extended to role-response functional valence; story/response pooling and
domain transfer remain open. No new GPU or model API work was performed.

## Update 2026-09-09 (Viewer Startup)

The user reported an indefinitely loading viewer in their local profile.
A UI-only patch adds early-error/timeout diagnostics and a bundled static
preview; scores and surfaces were not recomputed. Startup guard unit tests
pass, but user-profile interactive rendering is not yet confirmed. The prior
clean-profile browser tests should not be treated as proof it works in that
profile. No emotion-readout finding or claim changed.
