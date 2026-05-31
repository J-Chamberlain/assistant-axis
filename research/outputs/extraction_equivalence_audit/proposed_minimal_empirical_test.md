# Proposed Minimal Empirical Test

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
