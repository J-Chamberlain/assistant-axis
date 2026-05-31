#!/usr/bin/env python3
"""Write the public-source extraction-equivalence audit artifacts.

This script does not run model inference. It records the public/local source
evidence inspected for D01: whether Assistant Axis Qwen layer-48 hook vectors
are equivalent to H100 `outputs.hidden_states[48]` measurements.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research/outputs/public_source_extraction_equivalence"
MODEL_USED = "GPT-5.5"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_lines(path: str, start: int, end: int) -> str:
    full = REPO / path
    if not full.exists():
        return "LOCAL FILE NOT FOUND"
    lines = full.read_text(errors="replace").splitlines()
    selected = []
    for i in range(start, min(end, len(lines)) + 1):
        selected.append(f"{i}: {lines[i-1]}")
    return "\n".join(selected)


EVIDENCE_ROWS = [
    {
        "question": "official vector extraction representation",
        "public_source": "official Assistant Axis GitHub",
        "file_or_url": "https://raw.githubusercontent.com/safety-research/assistant-axis/master/pipeline/README.md",
        "line_or_snippet": "pipeline/README.md:47-62",
        "evidence_summary": "The extraction step is documented as mean response activations; `--layers` are zero-indexed post-MLP residual stream layers.",
        "implication_for_D01": "Official role/trait vectors target zero-indexed post-MLP residual stream layer outputs.",
        "confidence": "high",
    },
    {
        "question": "official hook point or hidden-state usage",
        "public_source": "official Assistant Axis GitHub",
        "file_or_url": "https://raw.githubusercontent.com/safety-research/assistant-axis/master/assistant_axis/internals/activations.py",
        "line_or_snippet": "assistant_axis/internals/activations.py:318-334",
        "evidence_summary": "The batch extractor registers forward hooks on `model_layers[layer_idx]` and captures `output[0]` or `output` from the target layer; the source comment says hooks are used because they are more reliable than `output_hidden_states`.",
        "implication_for_D01": "Official extraction uses module-output hooks, not `outputs.hidden_states[layer]` indexing.",
        "confidence": "high",
    },
    {
        "question": "layer indexing",
        "public_source": "official Assistant Axis GitHub",
        "file_or_url": "https://raw.githubusercontent.com/safety-research/assistant-axis/master/pipeline/README.md",
        "line_or_snippet": "pipeline/README.md:59-62; pipeline/4_vectors.py:38-61",
        "evidence_summary": "Layers are documented as zero-indexed; vectors are stacked as `(n_samples, n_layers, hidden_dim)` and averaged to `(n_layers, hidden_dim)`.",
        "implication_for_D01": "Layer 48 means module index 48 in the official vector tensor convention.",
        "confidence": "high",
    },
    {
        "question": "hidden_states semantics for Qwen3",
        "public_source": "Hugging Face Transformers docs and Qwen3 source",
        "file_or_url": "https://huggingface.co/docs/transformers/v4.38.0/en/main_classes/output ; https://raw.githubusercontent.com/huggingface/transformers/v4.51.0/src/transformers/models/qwen3/modeling_qwen3.py",
        "line_or_snippet": "HF docs: hidden_states are embedding output plus one per layer; Qwen3 v4.51.0 source appends `hidden_states` before each decoder layer and appends the final normalized state after the loop.",
        "evidence_summary": "For intermediate Qwen3 layers in Transformers 4.51.0, `hidden_states[k]` is the state before decoder layer k, equivalently the output after layer k-1. The official docs also state the tuple includes embedding output plus layer outputs.",
        "implication_for_D01": "`outputs.hidden_states[48]` is not the output of decoder module `layers[48]`; it is the input to layer 48 / output after layer 47.",
        "confidence": "high",
    },
    {
        "question": "hook output semantics for model.model.layers[48]",
        "public_source": "Hugging Face Qwen3 source and prior local replication script",
        "file_or_url": "https://raw.githubusercontent.com/huggingface/transformers/v4.51.0/src/transformers/models/qwen3/modeling_qwen3.py ; research/q2_stability/qwen/scripts/phase1_inference_only_v4.py",
        "line_or_snippet": "Qwen3DecoderLayer returns post-MLP residual `hidden_states`; phase1_inference_only_v4.py:126-139",
        "evidence_summary": "Qwen3 decoder layer returns `hidden_states` after attention residual plus MLP residual. Prior trickster replication hooks `model.model.layers[48]`, then mean-pools response positions.",
        "implication_for_D01": "A forward hook on `layers[48]` captures post-layer-48, post-MLP residual output, which corresponds to the next hidden-state boundary, not `hidden_states[48]`.",
        "confidence": "high",
    },
    {
        "question": "response-token masking",
        "public_source": "official Assistant Axis GitHub and current H100 runner",
        "file_or_url": "https://raw.githubusercontent.com/safety-research/assistant-axis/master/assistant_axis/internals/conversation.py ; research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py",
        "line_or_snippet": "conversation.py:135-205; run_h100_percentile_edge_validation.py:330-375",
        "evidence_summary": "Official Qwen span code detects assistant spans between Qwen chat sentinels and filters think tokens when disabled. H100 slices generated response tokens with `prompt_len:` after using Qwen chat template.",
        "implication_for_D01": "Token selection is broadly response-token-only in both paths, with minor wrapper/span differences less central than layer-boundary mismatch.",
        "confidence": "medium",
    },
    {
        "question": "pooling",
        "public_source": "official Assistant Axis GitHub, prior replication, and H100 runner",
        "file_or_url": "https://raw.githubusercontent.com/safety-research/assistant-axis/master/assistant_axis/internals/spans.py ; research/q2_stability/qwen/scripts/phase1_inference_only_v4.py ; research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py",
        "line_or_snippet": "spans.py:95-108; phase1_inference_only_v4.py:134-139; H100 runner:375-379",
        "evidence_summary": "All paths mean-pool response-token activations after selecting the response span.",
        "implication_for_D01": "Pooling convention is likely equivalent enough; it does not explain the hook-vs-hidden-state mismatch.",
        "confidence": "high",
    },
    {
        "question": "chat template",
        "public_source": "official Assistant Axis GitHub, prior replication, H100 runner",
        "file_or_url": "https://raw.githubusercontent.com/safety-research/assistant-axis/master/pipeline/2_activations.py ; research/q2_stability/qwen/scripts/phase1_inference_only_v4.py ; research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py",
        "line_or_snippet": "pipeline/2_activations.py:67-87; phase1_inference_only_v4.py:88-103; H100 runner:330-340",
        "evidence_summary": "All use tokenizer chat templates and pass `enable_thinking=False` for Qwen when supported; prior role extraction uses system+user messages, while H100 novel prompts are intentionally user-only.",
        "implication_for_D01": "Template mechanics are similar, but content/message-role structure differs by experimental design and does not resolve activation-site equivalence.",
        "confidence": "medium",
    },
    {
        "question": "thinking mode",
        "public_source": "official Assistant Axis GitHub, prior replication, H100 runner",
        "file_or_url": "https://raw.githubusercontent.com/safety-research/assistant-axis/master/pipeline/2_activations.py ; research/q2_stability/qwen/scripts/phase1_inference_only_v4.py ; research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py",
        "line_or_snippet": "pipeline/2_activations.py:67-70; phase1_inference_only_v4.py:92-110; H100 runner:333-338",
        "evidence_summary": "`enable_thinking=False` is consistently used where Qwen chat-template/generation calls accept it.",
        "implication_for_D01": "Thinking-mode convention appears matched and is not the blocking discrepancy.",
        "confidence": "high",
    },
    {
        "question": "comparison to current H100 runner",
        "public_source": "local committed H100 runner",
        "file_or_url": "research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py",
        "line_or_snippet": "run_h100_percentile_edge_validation.py:367-379",
        "evidence_summary": "The H100 runner calls the full generated sequence with `output_hidden_states=True` and uses `out.hidden_states[LAYER]` with `LAYER = 48`, then mean-pools generated response positions.",
        "implication_for_D01": "Current H100 extraction uses `hidden_states[48]`, which public Transformers semantics map to a different boundary than the official layer-48 hook.",
        "confidence": "high",
    },
    {
        "question": "comparison to prior trickster replication",
        "public_source": "local prior adaptive extraction artifact",
        "file_or_url": "research/q2_stability/qwen/scripts/phase1_inference_only_v4.py ; research/outputs/extraction_equivalence_audit/trickster_replication_method_summary.md",
        "line_or_snippet": "phase1_inference_only_v4.py:126-139",
        "evidence_summary": "The prior successful trickster replication used a layer-48 module-output hook and matched the downloaded trickster vector at cosine 0.957557.",
        "implication_for_D01": "Prior success supports the hook path, not the H100 hidden-states path; it increases concern that H100 used the wrong boundary.",
        "confidence": "high",
    },
]


SOURCE_INVENTORY = [
    ["official_github", "pipeline/README.md", "https://raw.githubusercontent.com/safety-research/assistant-axis/master/pipeline/README.md", "documents zero-indexed post-MLP residual-stream layers"],
    ["official_github", "pipeline/2_activations.py", "https://raw.githubusercontent.com/safety-research/assistant-axis/master/pipeline/2_activations.py", "calls ActivationExtractor and maps assistant spans"],
    ["official_github", "assistant_axis/internals/activations.py", "https://raw.githubusercontent.com/safety-research/assistant-axis/master/assistant_axis/internals/activations.py", "registers forward hooks; avoids output_hidden_states"],
    ["official_github", "assistant_axis/internals/conversation.py", "https://raw.githubusercontent.com/safety-research/assistant-axis/master/assistant_axis/internals/conversation.py", "Qwen chat-template span detection and thinking-token filtering"],
    ["official_github", "assistant_axis/internals/spans.py", "https://raw.githubusercontent.com/safety-research/assistant-axis/master/assistant_axis/internals/spans.py", "response-span mean pooling"],
    ["official_github", "pipeline/4_vectors.py", "https://raw.githubusercontent.com/safety-research/assistant-axis/master/pipeline/4_vectors.py", "averages score=3 activations into per-layer vectors"],
    ["official_huggingface", "assistant-axis-vectors dataset", "https://huggingface.co/datasets/lu-christina/assistant-axis-vectors", "precomputed axes/vectors; no extra hook-vs-hidden-state detail found"],
    ["prompt_artifacts", "assistant-axis-vector-prompts dataset", "https://huggingface.co/datasets/belmore/assistant-axis-vector-prompts", "documents prompt artifacts but not activation-site convention"],
    ["model_source", "Qwen/Qwen3-32B config", "https://huggingface.co/Qwen/Qwen3-32B/raw/main/config.json", "Qwen3ForCausalLM, num_hidden_layers=64, hidden_size=5120, transformers_version=4.51.0"],
    ["model_source", "Transformers Qwen3 source v4.51.0", "https://raw.githubusercontent.com/huggingface/transformers/v4.51.0/src/transformers/models/qwen3/modeling_qwen3.py", "decoder-layer output and hidden-state collection semantics"],
    ["model_docs", "Transformers ModelOutput docs", "https://huggingface.co/docs/transformers/v4.38.0/en/main_classes/output", "hidden_states include embedding output plus layer outputs"],
    ["local_project", "research/q2_stability/qwen/scripts/phase1_inference_only_v4.py", "local", "prior trickster hook extraction"],
    ["local_project", "research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py", "local", "current H100 output_hidden_states[48] extraction"],
    ["local_project", "research/outputs/extraction_equivalence_audit/", "local", "previous D01 audit and minimal empirical test"],
]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generated = utc_now()

    write_csv(
        OUT / "public_source_evidence_table.csv",
        EVIDENCE_ROWS,
        [
            "question",
            "public_source",
            "file_or_url",
            "line_or_snippet",
            "evidence_summary",
            "implication_for_D01",
            "confidence",
        ],
    )

    with (OUT / "source_file_inventory.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source_category", "file_or_artifact", "url_or_path", "relevance"])
        writer.writerows(SOURCE_INVENTORY)

    snippets = [
        ("pipeline/README.md", 47, 62),
        ("assistant_axis/internals/activations.py", 318, 334),
        ("assistant_axis/internals/spans.py", 95, 108),
        ("assistant_axis/internals/conversation.py", 135, 205),
        ("pipeline/2_activations.py", 67, 87),
        ("pipeline/4_vectors.py", 38, 61),
        ("research/q2_stability/qwen/scripts/phase1_inference_only_v4.py", 126, 139),
        ("research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py", 367, 379),
    ]
    snippet_md = [
        "# Assistant Axis Source Snippets",
        "",
        f"- Generated UTC: {generated}",
        f"- model_used: {MODEL_USED}",
        "",
        "Short local line excerpts used for the public-source audit. Public raw URLs are recorded in `source_file_inventory.csv`.",
    ]
    for path, start, end in snippets:
        snippet_md += ["", f"## {path}:{start}-{end}", "", "```text", read_lines(path, start, end), "```"]
    (OUT / "assistant_axis_source_snippets.md").write_text("\n".join(snippet_md) + "\n")

    qwen_notes = f"""# Qwen Hidden-States Semantics Notes

- Generated UTC: {generated}
- model_used: {MODEL_USED}
- Scope: public-source reasoning only; no model execution.

## Observed

The official Qwen/Qwen3-32B config reports `architectures: ["Qwen3ForCausalLM"]`, `num_hidden_layers: 64`, `hidden_size: 5120`, and `transformers_version: 4.51.0`.

Hugging Face ModelOutput documentation says hidden states are returned as the embedding output plus one tensor per layer. The Transformers 4.51.0 Qwen3 source stores the current `hidden_states` before each decoder layer in `all_hidden_states`, applies the decoder layer, assigns `hidden_states = layer_outputs[0]`, then after all layers applies final norm and appends that final state.

The Qwen3 decoder layer itself is pre-norm internally, but its module return value is after attention residual and after MLP residual. That is the post-MLP residual stream / decoder-block output for the layer.

## Inferred Layer-Boundary Mapping

For intermediate layers:

```text
outputs.hidden_states[0]  = token embeddings before decoder layer 0
outputs.hidden_states[1]  = output after decoder layer 0 / input to layer 1
...
outputs.hidden_states[48] = output after decoder layer 47 / input to layer 48
outputs.hidden_states[49] = output after decoder layer 48 / input to layer 49
```

A forward hook on `model.model.layers[48]` captures the output of decoder layer 48. Under the documented and source-inspected mapping, that corresponds to `outputs.hidden_states[49]`, not `outputs.hidden_states[48]`.

## Implication

The H100 runner's use of `out.hidden_states[48]` is likely one layer boundary earlier than the official Assistant Axis layer-48 hook convention. This is not proven by PCA reproduction, because PCA reproduction verifies only the projection basis, centering, and sign orientation for existing role vectors.
"""
    (OUT / "qwen_hidden_states_semantics_notes.md").write_text(qwen_notes)

    minimal_test = f"""# Minimal GPU Test If Needed

- Generated UTC: {generated}
- model_used: {MODEL_USED}

## Purpose

Public evidence is strong enough to identify a likely layer-boundary mismatch: official/prior extraction uses a forward hook on `model.model.layers[48]`, while H100 used `outputs.hidden_states[48]`. Before rerunning the full H100 validation, run one tiny confirmation test to verify the exact mapping in the deployed Qwen/Transformers stack.

## Test

Use one short prompt and Qwen/Qwen3-32B with the same tokenizer/model loading path as the H100 run.

1. Format the prompt with the same Qwen chat template and `enable_thinking=False`.
2. Generate one deterministic response, or use a short fixed full sequence if generation cost should be minimized.
3. Run a second full forward pass with `use_cache=False`, `output_hidden_states=True`.
4. In the same forward pass, register a forward hook on `model.model.layers[48]` and capture the module output.
5. Compare response-token tensors:
   - hook layer 48 output vs `outputs.hidden_states[48]`
   - hook layer 48 output vs `outputs.hidden_states[49]`
6. Report max absolute error, cosine similarity, and mean L2 difference before pooling and after response-token mean pooling.

## Expected Result

If public-source reasoning is correct, the layer-48 hook output should match `outputs.hidden_states[49]` and not `outputs.hidden_states[48]`.

## GPU Requirement

A Qwen/Qwen3-32B GPU is required only for this final implementation-level confirmation. A full H100 rerun should wait until this tiny test confirms the corrected boundary.
"""
    (OUT / "minimal_gpu_test_if_needed.md").write_text(minimal_test)

    d01_update = f"""# D01 Public-Source Update

- Generated UTC: {generated}
- model_used: {MODEL_USED}
- D01 status recommendation: open, with likely mismatch found.

## Direct Answer

Public-source evidence does not support closing D01 as equivalent. It instead supports marking D01 as an activation-boundary mismatch: the current H100 runner used `outputs.hidden_states[48]`, while the official Assistant Axis extraction path and the prior successful trickster replication use a forward hook on `model.model.layers[48]`.

## Key Evidence

- Official Assistant Axis pipeline documents `--layers` as zero-indexed post-MLP residual stream layers.
- Official `ActivationExtractor` registers forward hooks on target layer modules and captures module outputs.
- Prior trickster replication used the same layer-48 hook path and matched the downloaded trickster vector at cosine 0.957557.
- Transformers/Qwen3 hidden-state semantics imply `hidden_states[48]` is the input to decoder layer 48 / output after layer 47, while the layer-48 hook output corresponds to `hidden_states[49]`.

## Remaining Uncertainty

The remaining uncertainty is not whether public sources can explain the likely mismatch; they can. The remaining uncertainty is implementation-level confirmation in the exact H100 environment. A one-prompt hook-vs-hidden-states test should compare layer-48 hook output to `hidden_states[48]` and `hidden_states[49]`.
"""
    (OUT / "d01_public_source_update.md").write_text(d01_update)

    report = f"""# Public-Source Extraction Equivalence Audit

- Generated UTC: {generated}
- model_used: {MODEL_USED}
- Scope: public-source and local-source audit only; no pods, no new activations, no model APIs.

## Direct Answer

The public-source audit finds a likely extraction-boundary mismatch, not equivalence. The official Assistant Axis pipeline and prior successful trickster replication use forward hooks on `model.model.layers[48]`, capturing the decoder layer 48 module output. The H100 percentile-edge runner used `outputs.hidden_states[48]`.

Under Hugging Face ModelOutput documentation and the Transformers 4.51.0 Qwen3 source behavior, `outputs.hidden_states[48]` is the state before decoder layer 48, equivalently the output after decoder layer 47. The layer-48 module-output hook corresponds to the output after decoder layer 48, which maps to `outputs.hidden_states[49]` for intermediate layers. Therefore D01 should not be closed as resolved-equivalent; it should be marked open with mismatch details and rerun implications.

## Sources Inspected

The audit inspected the official Assistant Axis GitHub repository, including pipeline files, internals helpers, vector construction, PCA utilities, generation helpers, steering/capping code, and notebooks. It inspected the Hugging Face Assistant Axis vector dataset and prompt-artifact dataset metadata. It inspected the Qwen/Qwen3-32B config and the Transformers Qwen3 model source behavior relevant to decoder-layer outputs and hidden-state indexing. It also compared current H100 code against prior project trickster/editor adaptive extraction artifacts and the previous D01 audit.

Full source inventory is saved in `source_file_inventory.csv`.

## Evidence Summary

| Evidence question | Finding | D01 implication |
| --- | --- | --- |
| Official representation | `pipeline/README.md` documents zero-indexed post-MLP residual-stream layers. | Released vectors target decoder-block outputs, not arbitrary hidden-state tuple indices. |
| Official extraction path | `ActivationExtractor` registers forward hooks on target layers and captures module outputs. | Official extraction is hook-based. |
| Prior successful replication | Trickster replication hooks `model.model.layers[48]` and reached cosine 0.957557 to the downloaded trickster vector. | The hook path is empirically aligned with released vectors. |
| H100 extraction path | H100 runner uses `out.hidden_states[48]` after a second full forward pass. | H100 used hidden-state tuple indexing, not hook capture. |
| Qwen3 hidden-state mapping | HF docs and Qwen3 source imply hidden states include embeddings and then layer-boundary outputs. | `hidden_states[48]` is one decoder block earlier than layer-48 hook output. |

## Does `outputs.hidden_states[48]` Equal The Layer-48 Hook Tensor?

Observed: the Qwen3 decoder layer returns the post-attention-residual and post-MLP-residual hidden state. A forward hook on `model.model.layers[48]` captures that returned tensor.

Observed: Transformers hidden states include an initial embedding state plus per-layer states. In the Qwen3 4.51.0 source, the current hidden state is appended before each decoder layer, then the decoder layer updates it.

Inferred: for intermediate layers, `hidden_states[48]` is the output of layer 47 / input to layer 48. The output of `model.model.layers[48]` corresponds to `hidden_states[49]`.

Conclusion: no, public evidence indicates `outputs.hidden_states[48]` does not equal the Assistant Axis layer-48 hook tensor.

## What PCA Reproduction Proves

The H100 PCA reproduction error of 1.207e-06 proves that the committed projection basis, centering, and sign orientation reproduce canonical role coordinates. It does not prove that new H100 activations were measured at the same activation site or layer boundary as the released role vectors.

## Does Prior Trickster/Jester Replication Resolve This?

No. It helps in the opposite direction: it validates the hook-based extraction path as compatible with released Qwen vectors. It does not validate H100 `hidden_states[48]`; rather, it makes the H100 hidden-state path more suspect because it differs from the path that already matched a released role vector.

## D01 Decision

D01 should be marked `open` with likely mismatch found. The mismatch is source-backed enough to block further interpretation of H100 PC2/PC3 anomalies as model-behavior results until the extraction boundary is corrected or empirically checked.

## Remaining Test

Run the minimal one-prompt hook-vs-hidden-states comparison in `minimal_gpu_test_if_needed.md`. If the hook output matches `hidden_states[49]`, rerun or reinterpret the H100 validation with the corrected extraction boundary. A full H100 rerun is not the next step; a tiny verification is.

## Bottom Line

Public-source evidence strongly suggests the H100 runner measured one layer boundary earlier than the official Assistant Axis Qwen layer-48 vector convention. This could plausibly contribute to the observed PC2 shift, cone outliers, and PC3 collapse, so those anomalies should remain methodologically caveated until corrected.
"""
    (OUT / "public_source_extraction_equivalence_report.md").write_text(report)

    metadata = {
        "generated_utc": generated,
        "model_used": MODEL_USED,
        "d01_status": "open_likely_mismatch",
        "primary_conclusion": "outputs.hidden_states[48] likely does not equal model.model.layers[48] hook output; hook output maps to hidden_states[49].",
        "gpu_required_next": "tiny one-prompt confirmation only; no full rerun before confirmation",
    }
    (OUT / "audit_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    print(f"Wrote public-source extraction audit artifacts to {OUT}")


if __name__ == "__main__":
    main()
