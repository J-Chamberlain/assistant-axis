# Trickster Replication Method Summary

- Persona: trickster
- Model: Qwen/Qwen3-32B
- Layer: 48
- Script: `research/q2_stability/qwen/scripts/phase1_inference_only_v4.py`
- Extraction path: forward hook on `model.model.layers[LAYER]` during a full forward pass over the generated sequence with `use_cache=False`.
- Prompt format: system role instruction plus user extraction question, with `add_generation_prompt=True` and `enable_thinking=False`.
- Response-token selection: generated sequence positions after `prompt_len`.
- Pooling: mean over response-token hook outputs.
- Rollouts: 1200 generated, 64 scored by Codex/GPT-5.5.
- Best vector: score>=2, n=64, cosine to Lu/reference vector 0.957557.
- Adaptive stopping: score>=2 passed at n=16 with cosine 0.957582.

Conclusion: this is a successful hook-based adaptive extraction replication, not evidence that `output_hidden_states[48]` is equivalent to the hook site.
