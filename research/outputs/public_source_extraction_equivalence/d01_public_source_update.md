# D01 Public-Source Update

- Generated UTC: 2026-05-31T14:32:47.986206+00:00
- model_used: GPT-5.5
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
