# Extraction Equivalence Audit Report

- Generated UTC: 2026-05-31T14:10:40.063900+00:00
- Model used: GPT-5.5
- Scope: source/artifact audit only; no new activations, pods, or GPU work.

## Direct Answer

D01 should remain in_progress, not closed. The audit verifies model identity, the intended layer target, response-token mean pooling, PCA centering/sign/projection, and the prior hook-based trickster replication result. It also finds a material unresolved implementation question: the prior adaptive extraction and local source pipeline use forward hooks on transformer layer outputs, while the H100 validation reads `output_hidden_states[48]`.

## What The Prior Trickster Success Constrains

The prior adaptive trickster run is strong evidence that the project can reproduce a downloaded Qwen role vector when it uses the hook-based Phase 1 extraction path. The score>=2 vector reached cosine 0.957557 to `downloads/hf_vectors/qwen-3-32b/role_vectors/trickster.pt`, and adaptive stopping passed at n=16 for both score>=2 and score==3 subsets.

That success materially reduces concern that the local role prompts, response-token pooling, layer-48 target, and score-conditioned averaging procedure are broadly broken. It does **not** by itself close the H100 measurement question, because the H100 runner used `output_hidden_states[48]` rather than the hook path that produced the trickster replication.

## Comparison Summary

| component | equivalent_status | evidence | remaining_uncertainty |
| --- | --- | --- | --- |
| model_id | matched | trickster_phase1_manifest.json; h100_run_config.json | None for model identifier. |
| tokenizer_chat_template | partially matched | phase1_inference_only_v4.py; run_h100_percentile_edge_validation.py; assistant_axis/internals/conversation.py | Role-vector source used system+user role prompts; H100 novel prompts are user-only by design, so template roles differ even though Qwen chat-template mechanics match. |
| thinking_mode | mostly matched | trickster manifest; final_phase1_integrity.md; h100_run_config.json | H100 did not apply the same discard rule for literal think artifacts, but deterministic Qwen chat template used thinking-disabled mode. |
| prompt_construction | intentionally different | data/roles/instructions; data/extraction_questions.jsonl; percentile_edge_h100_manifest.csv | Different prompt construction is experimental design, not extraction mismatch. |
| generation_settings | partially matched | trickster_phase1_manifest.json; h100_run_config.json | Token cap differs; this affects response text distribution, not the activation object for a fixed sequence. |
| layer_index | ambiguous | pipeline/2_activations.py; phase1_inference_only_v4.py; run_h100_percentile_edge_validation.py | Need direct proof whether hidden_states[48] equals hook output of model.model.layers[48] or an adjacent boundary for Qwen. |
| indexing_convention | ambiguous | assistant_axis/internals/model.py; phase1_inference_only_v4.py; H100 runner | Transformers hidden_states usually includes embedding output at index 0, making hidden_states[48] potentially correspond to post-layer-47 rather than post-layer-48; must test or prove for Qwen implementation. |
| activation_site | not closed | assistant_axis/internals/activations.py says hooks are used; methodology note says post-MLP residual; H100 runner uses output_hidden_states | This is the main D01 uncertainty. |
| hidden_state_vs_hook | different implementation, equivalence unproven | assistant_axis/internals/activations.py; phase1_inference_only_v4.py; H100 runner | Direct hook-vs-hidden-state comparison needed. |
| pre_or_post_layernorm | ambiguous | forward-hook code captures layer module output; hidden_states boundary not locally tested | If hidden_states[48] is pre-layer-48 or post-layer-47, pre/post-block boundary differs. |
| response_token_mask | matched for generated single-turn responses | conversation.py; phase1_inference_only_v4.py; H100 runner | Original pipeline span parser trims assistant spans and may remove leading/trailing whitespace in some cases; H100 prompt_len slicing is simpler. |
| response_token_pooling | matched | assistant_axis/internals/spans.py; phase1_inference_only_v4.py; H100 runner | Only minor boundary/whitespace differences remain possible. |
| rollout_pooling | intentionally different | trickster_vector_validation; H100 final results | None; H100 validates prompt-level forecasts, not role-vector extraction. |
| role_expression_filtering | intentionally different | replication_differences_vs_lu.md; trickster/editor scoring summaries | Filtering differences matter for adaptive extraction claims, not H100 prompt validation. |
| vector_normalization | matched | extract_validate_trickster_vector.py; H100 project_activation | None found. |
| PCA_basis_loading | strongly verified | h100_activation_projection_debug.json | Projection basis correctness is closed for the committed coordinates. |
| PCA_centering_projection | strongly verified | max abs coordinate reproduction error 1.207e-06 | Does not prove extraction equivalence. |
| sign_orientation | strongly verified | h100_activation_projection_debug.json | None for projection sign. |

## PCA Reproduction Boundary

The 1.207e-06 PCA reproduction error proves that the H100 projection basis, centering, and sign orientation reproduce committed canonical role coordinates. It does not prove that newly measured H100 activations were captured at the same hook site or layer boundary as the released vectors.

## Can The H100 PC2/PC3 Anomalies Still Be Measurement Artifacts?

Yes, but only as a bounded methodological caveat. Projection mismatch is very unlikely, because the PCA basis and sign convention reproduce canonical role coordinates to near numerical precision. Response-token pooling is also aligned in broad form. The remaining plausible measurement artifact is activation-site or layer-boundary mismatch between hook-captured `model.model.layers[48]` output and `output_hidden_states[48]`.

## D01 Decision

Status: `in_progress`.

Closure reason not met: source-level evidence does not yet show that `output_hidden_states[48]` is exactly the same activation object as the hook output used by the original pipeline and the successful trickster replication.

## Recommended Next Step

Run the minimal hook-vs-hidden-state equivalence test described in `proposed_minimal_empirical_test.md`, or locate upstream Qwen/Transformers source documentation proving the mapping for this exact model class and Transformers version.
