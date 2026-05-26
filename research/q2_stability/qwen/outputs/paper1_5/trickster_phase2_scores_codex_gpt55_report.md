# Trickster Phase 2 Codex GPT-5.5 Role-Expression Scores

Date: 2026-05-26
Judge model: Codex GPT-5.5 Standard
Judge context: local Codex rubric scoring, no OpenAI API

## Status

Scored: 64 / 1200
Complete: `False`

## Score Distribution

| Score | Count | Fraction |
|---:|---:|---:|
| 0 | 0 | 0.0% |
| 1 | 0 | 0.0% |
| 2 | 31 | 48.4% |
| 3 | 33 | 51.6% |

Score >= 2: 64 (100.0%)
Score == 3: 33 (51.6%)

## Split By Truncation

| Truncated | n | score>=2 | score==3 |
|---|---:|---:|---:|
| false | 18 | 18 (100.0%) | 12 (66.7%) |
| true | 46 | 46 (100.0%) | 21 (45.7%) |

## Split By sp_idx

| sp_idx | n | score>=2 | score==3 |
|---:|---:|---:|---:|
| 0 | 64 | 64 (100.0%) | 33 (51.6%) |
| 1 | 0 | 0 (0.0%) | 0 (0.0%) |
| 2 | 0 | 0 (0.0%) | 0 (0.0%) |
| 3 | 0 | 0 (0.0%) | 0 (0.0%) |
| 4 | 0 | 0 (0.0%) | 0 (0.0%) |

## Thresholds

- n >= 16 score-3 responses achieved: `True`
- n >= 64 score-3 responses achieved: `False`
- n >= 16 score>=2 responses achieved: `True`
- n >= 64 score>=2 responses achieved: `True`

## Interpretation

No strong suppression signal from truncation in the scored subset.

Do not proceed to vector extraction yet; scoring is partial.

Judge model differs from Lu et al.; Codex GPT-5.5 Standard is used as a pragmatic local scoring substitute, not a strict Lu-method replication.
