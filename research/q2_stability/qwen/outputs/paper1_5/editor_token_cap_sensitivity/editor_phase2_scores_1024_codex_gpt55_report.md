# Editor Phase 2 Codex GPT-5.5 Role-Expression Scores

Date: 2026-05-26
Judge model: Codex GPT-5.5 Standard
Judge context: local Codex rubric scoring, no OpenAI API
Input: `research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/editor_phase1_matched64_1024.jsonl`

## Status

Scored: 64 / 64
Complete: `True`

## Score Distribution

| Score | Count | Fraction |
|---:|---:|---:|
| 0 | 22 | 34.4% |
| 1 | 37 | 57.8% |
| 2 | 4 | 6.2% |
| 3 | 1 | 1.6% |

Score >= 2: 5 (7.8%)
Score == 3: 1 (1.6%)

## Split By Truncation

| Truncated | n | score>=2 | score==3 |
|---|---:|---:|---:|
| false | 59 | 5 (8.5%) | 1 (1.7%) |
| true | 5 | 0 (0.0%) | 0 (0.0%) |

## Split By sp_idx

| sp_idx | n | score>=2 | score==3 |
|---:|---:|---:|---:|
| 0 | 64 | 5 (7.8%) | 1 (1.6%) |

## Thresholds

- n >= 16 score-3 responses achieved: `False`
- n >= 64 score-3 responses achieved: `False`
- n >= 16 score>=2 responses achieved: `False`
- n >= 64 score>=2 responses achieved: `False`

## Interpretation

No strong suppression signal from truncation in the scored subset.

Do not proceed to vector validation; qualifying counts are below target.

Judge model differs from Lu et al.; Codex GPT-5.5 Standard is used as a pragmatic local scoring substitute, not a strict Lu-method replication.
