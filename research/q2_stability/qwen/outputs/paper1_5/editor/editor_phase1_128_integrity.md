# Editor Phase 1 128 Integrity Check

Date: 2026-05-26T17:58:52.541183+00:00

## Result

Valid: `True`

## Counts

- JSONL records: 128 / 128
- Unique `(sp_idx, q_idx)` pairs: 128
- Duplicate pairs: 0
- `activation_saved=True`: 128
- Activation shards: 128
- Missing activation targets: 0
- `think_artifact=True`: 0
- Literal think tags: 0
- Truncated responses: 99
- Empty `response_text`: 0

## Metadata

- Generation model values: `['Qwen/Qwen3-32B']`
- Script author model values: `['GPT-5.5']`

## Sampled Activation Loads

| index | sp_idx | q_idx | shape | dtype |
|---:|---:|---:|---|---|
| 0 | 0 | 0 | `[5120]` | `torch.float32` |
| 31 | 0 | 31 | `[5120]` | `torch.float32` |
| 63 | 0 | 63 | `[5120]` | `torch.float32` |
| 95 | 0 | 95 | `[5120]` | `torch.float32` |
| 127 | 0 | 127 | `[5120]` | `torch.float32` |
