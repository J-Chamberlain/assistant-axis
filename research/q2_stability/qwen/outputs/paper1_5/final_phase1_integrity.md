# Final Phase 1 integrity check — 2026-05-26

Scope: best local snapshot available at `research/q2_stability/qwen/outputs/paper1_5`. The live pod was still running at 1180/1200 during the required one-time status check, so this is not a final 1200-record integrity pass.

## Counts

- JSONL line count: 1126 / 1200 expected
- Unique `(sp_idx, q_idx)` pairs: 1126
- Duplicate pairs: 0
- Missing expected pairs: 74
- `activation_saved=True`: 1126
- `activation_saved=False`: 0
- Local activation `.pt` files: 1126

## Response and artifact checks

- `think_artifact=True`: 0
- `truncated=True`: 670
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

The available local snapshot passes internal integrity for the 1126 records present: records are unique, activation counts match, sampled tensors load as `[5120]`, response text is present, and no think tags are visible in saved responses. It is incomplete relative to the full 1200-record design because the live pod had not finished at the required one-time status check.
