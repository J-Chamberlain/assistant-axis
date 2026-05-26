# Trickster Phase 1 Truncation Diagnostic

Date: 2026-05-26
Model used for analysis: GPT-5.5
Input: `research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl`

## Validation

- Records: 1200 / 1200
- Unique `(sp_idx, q_idx)` pairs: 1200 / 1200
- System prompts: 5 / 5
- Questions: 240 / 240
- Tokenization: Local tokenizer unavailable; character and word-count proxies were used. Tokenizer error: No module named 'transformers'

## Length Statistics

| Group | Character median | Character p90 | Word median | Word p90 |
|---|---:|---:|---:|---:|
| all | 2078 | 2241 | 375 | 405 |
| truncated | 2142 | 2275 | 387 | 409 |
| non_truncated | 1701 | 2074 | 315 | 380 |

## Truncation Summary

Overall truncation: 733/1200 (61.1%).

### By System Prompt

| sp_idx | records | truncated | fraction |
|---:|---:|---:|---:|
| 0 | 240 | 153 | 63.7% |
| 1 | 240 | 118 | 49.2% |
| 2 | 240 | 155 | 64.6% |
| 3 | 240 | 114 | 47.5% |
| 4 | 240 | 193 | 80.4% |

### By Question Decile

| q_idx range | records | truncated | fraction |
|---|---:|---:|---:|
| 000-023 | 120 | 77 | 64.2% |
| 024-047 | 120 | 77 | 64.2% |
| 048-071 | 120 | 79 | 65.8% |
| 072-095 | 120 | 68 | 56.7% |
| 096-119 | 120 | 86 | 71.7% |
| 120-143 | 120 | 54 | 45.0% |
| 144-167 | 120 | 64 | 53.3% |
| 168-191 | 120 | 80 | 66.7% |
| 192-215 | 120 | 77 | 64.2% |
| 216-239 | 120 | 71 | 59.2% |

### Most Truncated Questions

| q_idx | records | truncated | fraction |
|---:|---:|---:|---:|
| 2 | 5 | 5 | 100.0% |
| 5 | 5 | 5 | 100.0% |
| 6 | 5 | 5 | 100.0% |
| 8 | 5 | 5 | 100.0% |
| 13 | 5 | 5 | 100.0% |
| 14 | 5 | 5 | 100.0% |
| 17 | 5 | 5 | 100.0% |
| 19 | 5 | 5 | 100.0% |
| 23 | 5 | 5 | 100.0% |
| 29 | 5 | 5 | 100.0% |
| 32 | 5 | 5 | 100.0% |
| 35 | 5 | 5 | 100.0% |
| 38 | 5 | 5 | 100.0% |
| 39 | 5 | 5 | 100.0% |
| 42 | 5 | 5 | 100.0% |

## Completion Heuristics

- Truncated responses ending with sentence punctuation: 62/733 (8.5%)
- Truncated responses meeting abrupt-ending heuristic: 536/733 (73.1%)
- Non-truncated responses meeting abrupt-ending heuristic: 10/467 (2.1%)
- Truncated responses with at least two trickster lexical markers: 690/733 (94.1%)

## Answers

### How severe is truncation overall?

Truncation is high: 733/1200 records (61.1%) are flagged truncated.

### Is truncation concentrated by system prompt?

Truncation varies by system prompt, but every prompt has substantial truncation; the sp_idx fraction range is 47.5% to 80.4%.

### Is truncation concentrated by question subset?

Truncation varies more by question subset than by system prompt; q_idx decile fractions range from 45.0% to 71.7%.

### Do truncated responses appear to usually contain enough role expression before the cutoff?

690/733 truncated records (94.1%) contain at least two simple trickster lexical markers, so many truncated records likely contain usable role expression before cutoff, but this is only a proxy.

### Are endings often abrupt or mostly complete before continuation?

62/733 truncated records (8.5%) end with sentence punctuation; 536/733 (73.1%) meet the abrupt-ending heuristic.

### Does truncation look likely to bias score-3 selection?

Truncation could bias score-3 selection downward for records whose strongest role expression would have appeared late, and upward only if early role expression is strong while later generic continuation is cut away. The diagnostic supports keeping the truncation flag visible during scoring and downstream selection.

### Should Phase 2 scoring proceed on all 1200 records?

Phase 2 scoring should proceed on all 1200 records, with truncation included as a covariate/filter and with manual review of high-scoring truncated candidates.

### Is a small follow-up run with higher max_new_tokens recommended?

A small follow-up run with higher max_new_tokens is recommended for a stratified subset of high-scoring truncated records and the most abrupt truncated questions, not as a prerequisite for Phase 2.
