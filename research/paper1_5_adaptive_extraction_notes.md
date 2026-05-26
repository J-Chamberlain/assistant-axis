# Paper 1.5 Adaptive Extraction Notes

Date: 2026-05-26
Model used for synthesis: GPT-5.5 Standard

## Purpose

This note records the operational extraction workflow validated by the Qwen/Qwen3-32B trickster Phase 1 run and follow-on Codex-scored validation. It is a workflow continuity note, not paper prose.

## Overnight run architecture

The trickster replication uses the Lu-style extraction design: five trickster system prompts crossed with 240 extraction questions, producing 1200 rollouts. The run uses Qwen/Qwen3-32B with deterministic inference, thinking disabled, and layer 48 hidden-state extraction. Each rollout writes a JSONL record and a separate activation shard under `research/q2_stability/qwen/outputs/paper1_5/activations_trickster/`.

Final integrity passed with 1200 records, 1200 unique `(sp_idx, q_idx)` pairs, 1200 `activation_saved=True` records, and 1200 matching activation tensors of shape `[5120]`.

## Inference and scoring separation

Inference and scoring are deliberately separate. Phase 1 generates text and saves activations. Phase 2 scores role expression from response text without touching activation shards. This allows scoring to be rerun with different judges or rubrics while preserving the same generation and activation corpus.

The original Phase 2 plan used `gpt-4.1-mini` for closer alignment with the Lu et al. scoring path. That run is blocked by OpenAI API quota before producing scores. The current usable path is Codex GPT-5.5 Standard scoring, explicitly labeled as a pragmatic substitute rather than strict Lu-method replication.

## Truncation findings

The Phase 1 run produces 733 truncated responses out of 1200 at a 512-token generation limit. Truncation varies by system prompt and question subset, so it should be retained as a covariate in scoring and validation. The pre-scoring sample sufficiency analysis shows that truncated, non-truncated, and full-corpus subsets all converge geometrically, so truncation does not by itself invalidate the trickster extraction corpus.

## Adaptive scoring and stopping

Codex scoring resumed from an existing 16-record partial file and stopped adaptively at 64 scored records. The scored subset contains 64 score>=2 responses and 33 score==3 responses, meeting the preferred operational threshold of at least 64 qualifying responses and at least 16 strong responses.

Vector validation against the Lu et al. Qwen trickster reference finds the best candidate is the score>=2 mean vector, with cosine 0.957557 to the Lu mean. The score==3 candidate is also close, with cosine 0.955388 in the score-conditioned sufficiency analysis. Adaptive stopping passes at n=16 for both score>=2 and score==3 subsets.

## Operational recommendation

For future persona extractions, use 64 qualifying responses as the conservative default target until multi-persona validation broadens the evidence base. Adaptive stopping may be used once convergence criteria are satisfied, but fixed target counts should remain available for cross-persona comparability. The workflow should continue to preserve all Phase 1 activation shards, keep scoring files judge-specific, and never overwrite the missing `gpt-4.1-mini` score path with substitute scores.

The current trickster result supports Paper 1.5 proceeding with a clearly labeled operationally validated adaptive extraction protocol. Strict Lu-method replication remains pending unless the intended `gpt-4.1-mini` scoring path is restored.
