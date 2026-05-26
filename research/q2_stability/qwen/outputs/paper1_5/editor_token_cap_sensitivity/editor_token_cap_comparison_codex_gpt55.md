# Editor Token-Cap Comparison, Codex GPT-5.5

Date: 2026-05-26
Judge model: Codex GPT-5.5 Standard

## Matched Design

The comparison uses the same first 64 `(sp_idx, q_idx)` pairs from the 512-cap editor run and the matched 1024-cap follow-up. Scoring is Codex-local rubric scoring and does not use gpt-4.1-mini.

## Results

| Metric | 512 cap | 1024 cap |
|---|---:|---:|
| Truncated responses | 50/64 | 5/64 |
| Score >= 2 | 5/64 | 5/64 |
| Score == 3 | 1/64 | 1/64 |

| Agreement metric | Count | Fraction |
|---|---:|---:|
| Exact score agreement | 62/64 | 96.9% |
| Score >= 2 classification agreement | 64/64 | 100.0% |
| Score == 3 classification agreement | 64/64 | 100.0% |

## Interpretation

The 1024 cap reduces truncation sharply, from 50/64 to 5/64. It does not increase the matched score>=2 yield in this conservative scoring pass: both caps produce 5/64 score>=2 responses, and both produce 1/64 score==3 response. Longer completions add weak editor-like structure in 2 cases and dilute scores in 0 cases, with no cases changing the score>=2 classification.

The 512 cap is not defensible as a primary editor extraction cap from this chunk because truncation is high and the editor-role yield remains far below extraction thresholds. The matched comparison suggests that token cap alone is not the main source of low role expression, since 1024 substantially reduces truncation without increasing score>=2 yield. Future editor runs should use conditional escalation or a 1024 cap while also testing whether later system prompts yield stronger editor expression.

## Validation Gate

Vector validation was not run. The full 512-cap scored set has 10 score>=2 responses and 3 score==3 responses, below the required 64 and 16 thresholds.
