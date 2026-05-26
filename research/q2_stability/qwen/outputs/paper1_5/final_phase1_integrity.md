# Final Phase 1 integrity check — 2026-05-26

Scope: final local snapshot copied from `213.173.102.6:22707` after the pod reached 1200/1200.

## Counts

- JSONL line count: 1200 / 1200 expected
- Parse errors: 0
- Unique `(sp_idx, q_idx)` pairs: 1200
- Duplicate pairs: 0
- Missing expected pairs: 0
- `activation_saved=True`: 1200
- `activation_saved=False`: 0
- Local activation `.pt` files: 1200

## Response and artifact checks

- `think_artifact=True`: 0
- `truncated=True`: 733
- Empty `response_text`: 0
- Literal `<think>` or `</think>` in `response_text`: 0
- `activation_saved=True` but missing `activation_relpath`: 0
- `activation_saved=True` but local activation file missing: 0

## Tensor checks

Loaded 10 activation tensors spread across the local snapshot. All checked tensors shape `[5120]`: True.

## Provenance checks

- `generation_model`: ['Qwen/Qwen3-32B']
- `script_author_model`: ['GPT-5.5']
- Local script checked: `research/q2_stability/qwen/scripts/phase1_inference_only_v4.py`
- No OpenAI/API references in script: True
- Measurement uses `use_cache=False`: True
- Activation shards staged for Git: 0
- Activation ignore rule: `.gitignore:42:outputs/	research/q2_stability/qwen/outputs/paper1_5/activations_trickster/sp0_q0.pt`

## Result

A. FINAL OUTPUTS PRESERVED AND INTEGRITY PASSED. The final 1200-record Phase 1 snapshot is preserved locally, activation shards match the JSONL records, sampled tensors load as `[5120]`, and the copied script/provenance checks pass. The pod has not been terminated.
