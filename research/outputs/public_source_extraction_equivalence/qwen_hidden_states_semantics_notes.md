# Qwen Hidden-States Semantics Notes

- Generated UTC: 2026-05-31T14:32:47.986206+00:00
- model_used: GPT-5.5
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
