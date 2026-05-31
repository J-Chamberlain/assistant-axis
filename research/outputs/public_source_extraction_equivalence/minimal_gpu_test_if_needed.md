# Minimal GPU Test If Needed

- Generated UTC: 2026-05-31T14:32:47.986206+00:00
- model_used: GPT-5.5

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
