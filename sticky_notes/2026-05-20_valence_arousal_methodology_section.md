# Valence-Arousal Methodology Section — Draft Notes

Date: 2026-05-20
Status: To be written — discussion section for Paper 2
Priority: High — connects empirical findings to literature

## What needs to be written

A methods review and discussion section on the valence-arousal
framework as the organizing principle for emotion geometry
in LLMs.

Key claims:
1. The valence-arousal circumplex (Russell, 1980) is the most
   cross-model-consistent structure in the literature.
   Confirmed on Claude Sonnet 4.5 (Sofroniew et al., 2026),
   Llama-3.1-8B, Qwen3-8B, Qwen3-14B (arXiv:2604.03147),
   and Gemma4-E4B (independent replication, April 2026).

2. Ekman's six basic emotions are recoverable as discrete
   regions within the valence-arousal space but are not the
   fundamental organizing unit.

3. Our k=5 Qwen clustering maps onto the circumplex with
   two meaningful divergences: serene (deactivated-positive,
   no Ekman equivalent) and proud (assertive/agentic,
   maps to dominance dimension in VAD model).

4. The empirical valence axis for Qwen can be computed
   directly from probe directions by contrasting high-valence
   and low-valence emotion means. Analysis pending.

## Key citations

- Russell (1980) — original circumplex model
- Sofroniew et al. (2026) — Anthropic emotion concepts
- arXiv:2604.03147 — valence-arousal subspace, cross-model
- arXiv:2604.07382 — latent structure of affective representations
- Hollinsworth et al. (2024) — valence linearly embedded
- Zhao et al. (2025) — hierarchical emotion organization
- Wang et al. (2025, arXiv:2510.11328) — emotion circuits
