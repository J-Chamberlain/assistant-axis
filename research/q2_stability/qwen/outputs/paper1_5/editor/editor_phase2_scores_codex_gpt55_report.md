# Editor Phase 2 Codex GPT-5.5 Role-Expression Scores

Date: 2026-05-26
Judge model: Codex GPT-5.5 Standard
Judge context: local Codex rubric scoring, no OpenAI API
Input: `research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase1_128.jsonl`

## Status

Scored: 128 / 128
Complete: `True`

## Score Distribution

| Score | Count | Fraction |
|---:|---:|---:|
| 0 | 51 | 39.8% |
| 1 | 67 | 52.3% |
| 2 | 7 | 5.5% |
| 3 | 3 | 2.3% |

Score >= 2: 10 (7.8%)
Score == 3: 3 (2.3%)

## Split By Truncation

| Truncated | n | score>=2 | score==3 |
|---|---:|---:|---:|
| false | 29 | 3 (10.3%) | 2 (6.9%) |
| true | 99 | 7 (7.1%) | 1 (1.0%) |

## Split By sp_idx

| sp_idx | n | score>=2 | score==3 |
|---:|---:|---:|---:|
| 0 | 128 | 10 (7.8%) | 3 (2.3%) |

## Thresholds

- n >= 16 score-3 responses achieved: `False`
- n >= 64 score-3 responses achieved: `False`
- n >= 16 score>=2 responses achieved: `False`
- n >= 64 score>=2 responses achieved: `False`

## Interpretation

No strong suppression signal from truncation in the scored subset.

Do not proceed to vector validation; qualifying counts are below target.

Judge model differs from Lu et al.; Codex GPT-5.5 Standard is used as a pragmatic local scoring substitute, not a strict Lu-method replication.
