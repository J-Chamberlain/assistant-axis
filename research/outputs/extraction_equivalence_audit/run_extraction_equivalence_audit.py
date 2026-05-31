#!/usr/bin/env python3
"""Document extraction-equivalence evidence for the H100 validation audit.

This is a source/artifact audit only. It does not run model inference or
generate activations.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


MODEL_USED = "GPT-5.5"
REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research/outputs/extraction_equivalence_audit"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def md_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    lines = [
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join(["---"] * len(fields)) + " |",
    ]
    for row in rows:
        vals = [str(row.get(field, "")).replace("\n", "<br>") for field in fields]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    trickster_manifest = read_json(REPO / "research/q2_stability/qwen/outputs/paper1_5/trickster_phase1_manifest.json")
    trickster_validation = read_json(REPO / "research/q2_stability/qwen/outputs/paper1_5/trickster_vector_validation_codex_gpt55.json")
    editor_manifest = read_json(REPO / "research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase1_128_manifest.json")
    editor_summary = read_json(REPO / "research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase2_scores_codex_gpt55_summary.json")
    editor_1024 = read_json(REPO / "research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/editor_token_cap_comparison_codex_gpt55.json")
    h100_config = read_json(REPO / "research/outputs/h100_percentile_edge_validation/h100_run_config.json")
    h100_debug = read_json(REPO / "research/outputs/h100_percentile_edge_validation/h100_activation_projection_debug.json")

    inventory_rows = [
        {
            "persona_name": "trickster",
            "model": trickster_manifest["generation_model"],
            "layer": trickster_manifest["layer"],
            "extraction_method": "forward hook on model.model.layers[48] during full generated sequence forward pass",
            "vector_type": "mean response-token layer output vector saved as one 5120-d .pt shard per rollout; score-conditioned mean candidate vector",
            "pooling_method": "mean over generated response tokens only, excluding prompt tokens",
            "number_of_rollouts": trickster_validation["phase1_records"],
            "filtering_threshold": "Codex/GPT-5.5 role-expression score >=2; score==3 also evaluated",
            "cosine_to_reference_vector": trickster_validation["candidate_sets"]["score_ge_2"]["cosine_to_lu_mean"],
            "projected_pc_coordinates": "not found in prior adaptive validation report",
            "integrity_checks": "1200/1200 records, 1200 activation shards, all sampled tensors shape [5120], no think artifacts, no missing activations",
            "evidence_path": "research/q2_stability/qwen/outputs/paper1_5/trickster_vector_validation_codex_gpt55.md",
        },
        {
            "persona_name": "editor",
            "model": editor_manifest["generation_model"],
            "layer": editor_manifest["layer"],
            "extraction_method": "forward hook on model.model.layers[48] during full generated sequence forward pass",
            "vector_type": "mean response-token layer output vector saved as one 5120-d .pt shard per rollout; no validated role vector constructed",
            "pooling_method": "mean over generated response tokens only, excluding prompt tokens",
            "number_of_rollouts": editor_summary["total_records"],
            "filtering_threshold": "Codex/GPT-5.5 score >=2 target not met; vector validation not run",
            "cosine_to_reference_vector": "",
            "projected_pc_coordinates": "not available; validation gate failed",
            "integrity_checks": "128/128 records, 128 activation shards, sampled tensors shape [5120], no think artifacts, no missing activations",
            "evidence_path": "research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase1_128_integrity.md",
        },
        {
            "persona_name": "editor_1024_matched64",
            "model": editor_manifest["generation_model"],
            "layer": editor_manifest["layer"],
            "extraction_method": "forward hook on model.model.layers[48] during full generated sequence forward pass",
            "vector_type": "token-cap sensitivity activation shards; no validated role vector constructed",
            "pooling_method": "mean over generated response tokens only, excluding prompt tokens",
            "number_of_rollouts": editor_1024["matched_pairs"],
            "filtering_threshold": "score >=2 unchanged at 5/64; score==3 unchanged at 1/64",
            "cosine_to_reference_vector": "",
            "projected_pc_coordinates": "not available; validation gate failed",
            "integrity_checks": f"truncation reduced {editor_1024['truncation_reduction']} cases, but role-expression counts unchanged",
            "evidence_path": "research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/editor_token_cap_comparison_codex_gpt55.md",
        },
    ]
    inventory_fields = list(inventory_rows[0].keys())
    write_csv(OUT / "prior_adaptive_extraction_inventory.csv", inventory_rows, inventory_fields)

    equivalence_rows = [
        {
            "component": "model_id",
            "original_assistant_axis_method": "Model passed to pipeline; local Qwen artifacts use Qwen/Qwen3-32B",
            "prior_trickster_replication_method": trickster_manifest["generation_model"],
            "current_h100_method": h100_config["model"],
            "equivalent_status": "matched",
            "evidence": "trickster_phase1_manifest.json; h100_run_config.json",
            "remaining_uncertainty": "None for model identifier.",
        },
        {
            "component": "tokenizer_chat_template",
            "original_assistant_axis_method": "ConversationEncoder/tokenizer.apply_chat_template over conversation records; Qwen spans parsed by <|im_start|>assistant and <|im_end|>",
            "prior_trickster_replication_method": "system+user messages with add_generation_prompt=True and enable_thinking=False",
            "current_h100_method": "user-only prompt with add_generation_prompt=True and enable_thinking=False",
            "equivalent_status": "partially matched",
            "evidence": "phase1_inference_only_v4.py; run_h100_percentile_edge_validation.py; assistant_axis/internals/conversation.py",
            "remaining_uncertainty": "Role-vector source used system+user role prompts; H100 novel prompts are user-only by design, so template roles differ even though Qwen chat-template mechanics match.",
        },
        {
            "component": "thinking_mode",
            "original_assistant_axis_method": "Qwen pipeline supports enable_thinking=False; thinking tokens filtered when disabled",
            "prior_trickster_replication_method": "enable_thinking=False and think artifacts discarded",
            "current_h100_method": "enable_thinking=False in chat template; generated responses measured without thinking artifacts check as role extraction did",
            "equivalent_status": "mostly matched",
            "evidence": "trickster manifest; final_phase1_integrity.md; h100_run_config.json",
            "remaining_uncertainty": "H100 did not apply the same discard rule for literal think artifacts, but deterministic Qwen chat template used thinking-disabled mode.",
        },
        {
            "component": "prompt_construction",
            "original_assistant_axis_method": "role instruction/system prompt plus extraction question, stored as conversation turns",
            "prior_trickster_replication_method": "five role system prompts x 240 extraction questions",
            "current_h100_method": "single novel user prompt from percentile-edge manifest",
            "equivalent_status": "intentionally different",
            "evidence": "data/roles/instructions; data/extraction_questions.jsonl; percentile_edge_h100_manifest.csv",
            "remaining_uncertainty": "Different prompt construction is experimental design, not extraction mismatch.",
        },
        {
            "component": "generation_settings",
            "original_assistant_axis_method": "not fully recovered from released metadata; pipeline responses preexist before activation extraction",
            "prior_trickster_replication_method": "max_new_tokens=512, do_sample=False",
            "current_h100_method": "max_new_tokens=256, do_sample=False, temperature=0.0, top_p=1.0",
            "equivalent_status": "partially matched",
            "evidence": "trickster_phase1_manifest.json; h100_run_config.json",
            "remaining_uncertainty": "Token cap differs; this affects response text distribution, not the activation object for a fixed sequence.",
        },
        {
            "component": "layer_index",
            "original_assistant_axis_method": "pipeline accepts integer layer list; pca.py selects activation_list[:, layer, :]",
            "prior_trickster_replication_method": "LAYER=48 hooked at model.model.layers[48]",
            "current_h100_method": "LAYER=48 read from out.hidden_states[48]",
            "equivalent_status": "ambiguous",
            "evidence": "pipeline/2_activations.py; phase1_inference_only_v4.py; run_h100_percentile_edge_validation.py",
            "remaining_uncertainty": "Need direct proof whether hidden_states[48] equals hook output of model.model.layers[48] or an adjacent boundary for Qwen.",
        },
        {
            "component": "indexing_convention",
            "original_assistant_axis_method": "zero-indexed ModuleList layer indices",
            "prior_trickster_replication_method": "zero-indexed model.model.layers[48]",
            "current_h100_method": "Transformers hidden_states tuple index 48",
            "equivalent_status": "ambiguous",
            "evidence": "assistant_axis/internals/model.py; phase1_inference_only_v4.py; H100 runner",
            "remaining_uncertainty": "Transformers hidden_states usually includes embedding output at index 0, making hidden_states[48] potentially correspond to post-layer-47 rather than post-layer-48; must test or prove for Qwen implementation.",
        },
        {
            "component": "activation_site",
            "original_assistant_axis_method": "hooked transformer layer output described locally as mean post-MLP residual over response tokens",
            "prior_trickster_replication_method": "forward hook on model.model.layers[48] output tensor",
            "current_h100_method": "output_hidden_states[48]",
            "equivalent_status": "not closed",
            "evidence": "assistant_axis/internals/activations.py says hooks are used; methodology note says post-MLP residual; H100 runner uses output_hidden_states",
            "remaining_uncertainty": "This is the main D01 uncertainty.",
        },
        {
            "component": "hidden_state_vs_hook",
            "original_assistant_axis_method": "hook-based extraction; local comment says hooks are more reliable than output_hidden_states",
            "prior_trickster_replication_method": "hook-based extraction",
            "current_h100_method": "output_hidden_states extraction",
            "equivalent_status": "different implementation, equivalence unproven",
            "evidence": "assistant_axis/internals/activations.py; phase1_inference_only_v4.py; H100 runner",
            "remaining_uncertainty": "Direct hook-vs-hidden-state comparison needed.",
        },
        {
            "component": "pre_or_post_layernorm",
            "original_assistant_axis_method": "module output after full decoder layer, likely post-block residual after post-MLP update",
            "prior_trickster_replication_method": "module output after full decoder layer",
            "current_h100_method": "Transformers hidden state boundary selected by tuple index",
            "equivalent_status": "ambiguous",
            "evidence": "forward-hook code captures layer module output; hidden_states boundary not locally tested",
            "remaining_uncertainty": "If hidden_states[48] is pre-layer-48 or post-layer-47, pre/post-block boundary differs.",
        },
        {
            "component": "response_token_mask",
            "original_assistant_axis_method": "assistant response spans identified by Qwen chat-template special tokens",
            "prior_trickster_replication_method": "generated response tokens are out[0][prompt_len:]",
            "current_h100_method": "generated response tokens are gen_out[0, prompt_len:]",
            "equivalent_status": "matched for generated single-turn responses",
            "evidence": "conversation.py; phase1_inference_only_v4.py; H100 runner",
            "remaining_uncertainty": "Original pipeline span parser trims assistant spans and may remove leading/trailing whitespace in some cases; H100 prompt_len slicing is simpler.",
        },
        {
            "component": "response_token_pooling",
            "original_assistant_axis_method": "mean over response span tokens",
            "prior_trickster_replication_method": "response_h.mean(0)",
            "current_h100_method": "hidden.mean(axis=0) over prompt_len: end",
            "equivalent_status": "matched",
            "evidence": "assistant_axis/internals/spans.py; phase1_inference_only_v4.py; H100 runner",
            "remaining_uncertainty": "Only minor boundary/whitespace differences remain possible.",
        },
        {
            "component": "rollout_pooling",
            "original_assistant_axis_method": "mean over qualified role-expression vectors",
            "prior_trickster_replication_method": "mean over Codex-scored score>=2 or score==3 activation shards",
            "current_h100_method": "no rollout pooling; one measured response vector per novel prompt",
            "equivalent_status": "intentionally different",
            "evidence": "trickster_vector_validation; H100 final results",
            "remaining_uncertainty": "None; H100 validates prompt-level forecasts, not role-vector extraction.",
        },
        {
            "component": "role_expression_filtering",
            "original_assistant_axis_method": "gpt-4.1-mini separates fully/somewhat role-playing",
            "prior_trickster_replication_method": "Codex/GPT-5.5 score>=2 and score==3 filters",
            "current_h100_method": "none; all novel prompts measured",
            "equivalent_status": "intentionally different",
            "evidence": "replication_differences_vs_lu.md; trickster/editor scoring summaries",
            "remaining_uncertainty": "Filtering differences matter for adaptive extraction claims, not H100 prompt validation.",
        },
        {
            "component": "vector_normalization",
            "original_assistant_axis_method": "released role vectors are raw mean activation vectors; cosine comparisons normalize only for cosine",
            "prior_trickster_replication_method": "mean vector saved raw; cosine normalization used only in comparison",
            "current_h100_method": "raw mean activation projected after PCA centering",
            "equivalent_status": "matched",
            "evidence": "extract_validate_trickster_vector.py; H100 project_activation",
            "remaining_uncertainty": "None found.",
        },
        {
            "component": "PCA_basis_loading",
            "original_assistant_axis_method": "PCA fit over role activation vectors",
            "prior_trickster_replication_method": "not used in vector-validation report",
            "current_h100_method": "basis reconstructed from all 275 Qwen role vectors and verified against committed canonical coordinates",
            "equivalent_status": "strongly verified",
            "evidence": "h100_activation_projection_debug.json",
            "remaining_uncertainty": "Projection basis correctness is closed for the committed coordinates.",
        },
        {
            "component": "PCA_centering_projection",
            "original_assistant_axis_method": "pca.py centers through sklearn PCA; no standardization by default",
            "prior_trickster_replication_method": "not used",
            "current_h100_method": "subtract role-vector mean then dot PCA components",
            "equivalent_status": "strongly verified",
            "evidence": f"max abs coordinate reproduction error {h100_debug['max_abs_coordinate_reproduction_error']:.3e}",
            "remaining_uncertainty": "Does not prove extraction equivalence.",
        },
        {
            "component": "sign_orientation",
            "original_assistant_axis_method": "canonical committed PCA coordinate orientation",
            "prior_trickster_replication_method": "not used",
            "current_h100_method": f"sign alignment {h100_debug['sign_alignment']}",
            "equivalent_status": "strongly verified",
            "evidence": "h100_activation_projection_debug.json",
            "remaining_uncertainty": "None for projection sign.",
        },
    ]
    equivalence_fields = list(equivalence_rows[0].keys())
    write_csv(OUT / "extraction_equivalence_table.csv", equivalence_rows, equivalence_fields)

    direct_answer = (
        "D01 should remain in_progress, not closed. The audit verifies model identity, "
        "the intended layer target, response-token mean pooling, PCA centering/sign/projection, "
        "and the prior hook-based trickster replication result. It also finds a material unresolved "
        "implementation question: the prior adaptive extraction and local source pipeline use forward "
        "hooks on transformer layer outputs, while the H100 validation reads `output_hidden_states[48]`."
    )
    pca_proves = (
        "The 1.207e-06 PCA reproduction error proves that the H100 projection basis, centering, and sign "
        "orientation reproduce committed canonical role coordinates. It does not prove that newly measured "
        "H100 activations were captured at the same hook site or layer boundary as the released vectors."
    )
    report = f"""# Extraction Equivalence Audit Report

- Generated UTC: {now}
- Model used: {MODEL_USED}
- Scope: source/artifact audit only; no new activations, pods, or GPU work.

## Direct Answer

{direct_answer}

## What The Prior Trickster Success Constrains

The prior adaptive trickster run is strong evidence that the project can reproduce a downloaded Qwen role vector when it uses the hook-based Phase 1 extraction path. The score>=2 vector reached cosine {trickster_validation['candidate_sets']['score_ge_2']['cosine_to_lu_mean']:.6f} to `downloads/hf_vectors/qwen-3-32b/role_vectors/trickster.pt`, and adaptive stopping passed at n=16 for both score>=2 and score==3 subsets.

That success materially reduces concern that the local role prompts, response-token pooling, layer-48 target, and score-conditioned averaging procedure are broadly broken. It does **not** by itself close the H100 measurement question, because the H100 runner used `output_hidden_states[48]` rather than the hook path that produced the trickster replication.

## Comparison Summary

{md_table(equivalence_rows, ['component', 'equivalent_status', 'evidence', 'remaining_uncertainty'])}

## PCA Reproduction Boundary

{pca_proves}

## Can The H100 PC2/PC3 Anomalies Still Be Measurement Artifacts?

Yes, but only as a bounded methodological caveat. Projection mismatch is very unlikely, because the PCA basis and sign convention reproduce canonical role coordinates to near numerical precision. Response-token pooling is also aligned in broad form. The remaining plausible measurement artifact is activation-site or layer-boundary mismatch between hook-captured `model.model.layers[48]` output and `output_hidden_states[48]`.

## D01 Decision

Status: `in_progress`.

Closure reason not met: source-level evidence does not yet show that `output_hidden_states[48]` is exactly the same activation object as the hook output used by the original pipeline and the successful trickster replication.

## Recommended Next Step

Run the minimal hook-vs-hidden-state equivalence test described in `proposed_minimal_empirical_test.md`, or locate upstream Qwen/Transformers source documentation proving the mapping for this exact model class and Transformers version.
"""
    write(OUT / "extraction_equivalence_audit_report.md", report)

    trickster_summary = f"""# Trickster Replication Method Summary

- Persona: trickster
- Model: {trickster_manifest['generation_model']}
- Layer: {trickster_manifest['layer']}
- Script: `research/q2_stability/qwen/scripts/phase1_inference_only_v4.py`
- Extraction path: forward hook on `model.model.layers[LAYER]` during a full forward pass over the generated sequence with `use_cache=False`.
- Prompt format: system role instruction plus user extraction question, with `add_generation_prompt=True` and `enable_thinking=False`.
- Response-token selection: generated sequence positions after `prompt_len`.
- Pooling: mean over response-token hook outputs.
- Rollouts: {trickster_validation['phase1_records']} generated, {trickster_validation['phase2_scored_records']} scored by Codex/GPT-5.5.
- Best vector: score>=2, n={trickster_validation['candidate_sets']['score_ge_2']['n_qualifying']}, cosine to Lu/reference vector {trickster_validation['candidate_sets']['score_ge_2']['cosine_to_lu_mean']:.6f}.
- Adaptive stopping: score>=2 passed at n={trickster_validation['adaptive_stopping']['score_ge_2']['n_stop']} with cosine {trickster_validation['adaptive_stopping']['score_ge_2']['cosine_to_lu_at_stop']:.6f}.

Conclusion: this is a successful hook-based adaptive extraction replication, not evidence that `output_hidden_states[48]` is equivalent to the hook site.
"""
    write(OUT / "trickster_replication_method_summary.md", trickster_summary)

    h100_diff = f"""# H100 Vs Prior Extraction Difference

## Shared Elements

- Model ID: `Qwen/Qwen3-32B`.
- Target layer number: 48.
- Thinking disabled at chat-template/generation time.
- Deterministic generation.
- Response-token mean pooling excludes prompt tokens.
- Raw mean activation vectors are used without L2 normalization before PCA projection.

## Differences

- Prior trickster/editor adaptive extraction captured activations using `model.model.layers[48].register_forward_hook(...)`.
- H100 validation captured activations from `out.hidden_states[48]` after a second forward pass with `output_hidden_states=True`.
- Prior adaptive extraction used system+user role-instruction prompts and 512 max new tokens; H100 used novel user-only prompts and 256 max new tokens.
- Prior adaptive extraction pooled multiple qualifying rollouts into role vectors; H100 used one measured response vector per prompt.
- Prior extraction filtered by role-expression score; H100 did not filter prompts/responses by role expression.

## Interpretation

The prompt, filtering, and rollout-pooling differences are expected by design. The activation-site difference is the unresolved methodological issue for D01.
"""
    write(OUT / "h100_vs_prior_extraction_diff.md", h100_diff)

    source_notes = """# Source Extraction Code Notes

## Local Assistant Axis Pipeline

- `pipeline/2_activations.py` loads response conversations, calls `ActivationExtractor.batch_conversations(...)`, maps assistant spans with `SpanMapper.map_spans(...)`, and saves mean assistant-turn activations.
- `assistant_axis/internals/activations.py` uses forward hooks on `model_layers[layer_idx]`; its batch path says hooks are used because they are more reliable than `output_hidden_states`.
- `assistant_axis/internals/spans.py` computes mean activations over response-span tokens.
- `assistant_axis/internals/conversation.py` contains Qwen-specific assistant response span parsing using `<|im_start|>assistant` and `<|im_end|>`, with optional thinking-token exclusion when thinking is disabled.
- `assistant_axis/pca.py` selects `activation_list[:, layer, :]` when given 3D activations and performs ordinary sklearn PCA over the selected layer with no scaler by default.

## Prior Adaptive Extraction

- `research/q2_stability/qwen/scripts/phase1_inference_only_v4.py` and editor variants use a forward hook on `model.model.layers[LAYER]`.
- They forward the full generated sequence with `use_cache=False`, slice response-token positions using `prompt_len:`, and mean-pool those hook outputs.

## H100 Extraction

- `research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py` forwards the full generated sequence with `output_hidden_states=True` and `use_cache=False`, reads `out.hidden_states[LAYER]`, slices `prompt_len:`, mean-pools, and projects into the reconstructed persona PCA basis.

## Unresolved Source Question

For Qwen/Qwen3-32B under the relevant Transformers versions, the audit did not prove whether `out.hidden_states[48]` equals the output captured by a forward hook on `model.model.layers[48]`, or whether one of `hidden_states[48]` / `hidden_states[49]` corresponds to that hook due to the embedding-output offset.
"""
    write(OUT / "source_extraction_code_notes.md", source_notes)

    d01 = """# D01 Resolution Update

Status: `in_progress`.

The audit resolves several pieces of D01:

- Model identity matches Qwen/Qwen3-32B.
- Layer target is consistently recorded as 48.
- Prior adaptive trickster/editor extraction used response-token mean pooling and disabled thinking.
- Current H100 projection centering/sign/basis is strongly verified by canonical coordinate reproduction at max abs error 1.207e-06.
- Prior trickster adaptive extraction successfully matched the Lu/downloaded trickster vector at cosine 0.957557.

The audit does not resolve the activation-site equivalence question:

- Local source and prior adaptive extraction use forward hooks on transformer layer outputs.
- Current H100 validation uses `output_hidden_states[48]`.
- The exact hook-vs-hidden-state boundary for Qwen/Qwen3-32B was not proven in local source inspection.

Conclusion: D01 should not be closed yet. H100 results remain informative, but PC2 shift, cone outliers, and PC3 collapse should continue to carry an activation-site caveat until the minimal equivalence test is run or source-level proof is found.
"""
    write(OUT / "d01_resolution_update.md", d01)

    test = """# Proposed Minimal Empirical Test

No full H100 validation rerun is required to resolve the remaining D01 uncertainty.

## Test

On Qwen/Qwen3-32B with the same Transformers family used in the H100 run:

1. Choose one to three short prompts.
2. Apply the same Qwen chat template with `enable_thinking=False`.
3. Generate or use a fixed short assistant response.
4. Run one full forward pass over the complete prompt+response sequence with `use_cache=False`.
5. During that pass, capture:
   - a forward hook on `model.model.layers[48]` output,
   - `out.hidden_states[48]`,
   - `out.hidden_states[49]`.
6. Compare response-token slices tokenwise and mean-pooled:
   - max absolute difference,
   - L2 difference,
   - cosine similarity,
   - shape and dtype.

## Decision Rule

If the hook output matches `hidden_states[48]` or `hidden_states[49]` to numerical tolerance, update the H100 method notes accordingly and close D01. If neither matches, rerun or reinterpret the H100 validation with the hook-equivalent activation object.

## GPU Requirement

A Qwen/Qwen3-32B test likely requires a GPU instance because the model is too large for local CPU-only verification. This is a tiny diagnostic job: a one-prompt, single-forward equivalence check, not a new activation validation run. If a small Qwen-family model is used first, it can provide architectural evidence but should not be treated as final proof for the 32B checkpoint.
"""
    write(OUT / "proposed_minimal_empirical_test.md", test)

    print(f"Wrote extraction-equivalence audit to {OUT}")


if __name__ == "__main__":
    main()
