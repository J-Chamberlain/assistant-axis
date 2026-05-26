# Editor Matched64 1024-Token Integrity Check

Date: 2026-05-26T19:50:22.908440+00:00

## Result

Valid: `True`

## Counts

- JSONL records: 64 / 64
- Same pairs as first 64 editor 512-cap records: `True`
- Unique `(sp_idx, q_idx)` pairs: 64
- Duplicate pairs: 0
- `activation_saved=True`: 64
- Activation shards: 64
- Missing activation targets: 0
- `think_artifact=True`: 0
- Literal think tags: 0
- Truncated responses at 1024: 5
- Truncated responses for matched first 64 at 512: 50
- Truncation reduction: 45
- Empty `response_text`: 0

## Sampled Activation Loads

| index | sp_idx | q_idx | shape | dtype |
|---:|---:|---:|---|---|
| 0 | 0 | 0 | `[5120]` | `torch.float32` |
| 15 | 0 | 15 | `[5120]` | `torch.float32` |
| 31 | 0 | 31 | `[5120]` | `torch.float32` |
| 47 | 0 | 47 | `[5120]` | `torch.float32` |
| 63 | 0 | 63 | `[5120]` | `torch.float32` |
