# Source Extraction Code Notes

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
