# Baseline Return — Replication vs Original Finding

The multi-turn experiment finding that both personas return toward
the evaluative basin under neutral prompting is consistent with
Anthropic's Emotion Concepts paper (Sofroniew et al., 2026,
arXiv:2604.07729), which notes that emotional vector activation
returns to baseline relatively quickly after the triggering
stimulus is removed.

ACTION NEEDED: Retrieve the specific passage and wording from the
Emotion Concepts paper before write-up. Confirm whether their
baseline return finding applies to instruction-tuned model only
or also base model, and what number of turns or tokens they cite.

FRAMING: Position as replication and extension.
Replication: evaluative basin acts as generative attractor,
activation returns toward it after perturbation.
Extension: measured geometrically in BASE model, connected to
persona drift rather than emotional valence alone. This is the
novel contribution — the attractor is a pretraining property.

Priority: verify citation before write-up begins.

## Update 2026-05-18

The paper now incorporates the base-vs-instruct emotional responsiveness finding in Sections 1 and 9. The framing shifts from simple baseline-return replication toward a stronger dissociation: base Gemma shows 0 of 12 negative-valence turns under grief/loss prompts, while instruction-tuned Gemma shows 12 of 12, suggesting emotional responsiveness may be installed or strongly amplified by post-training.

## Update 2026-05-19

Local HuggingFace cache check found no cached 171-vector Emotion Concepts bundle in `lu-christina/assistant-axis-vectors`. The only emotion-name match is `gemma-2-27b/trait_vectors/emotional.pt`, a single Gemma trait vector with shape `(46, 4608)`, so any direct Emotion Concepts replication still requires obtaining those vectors separately or recomputing them.
