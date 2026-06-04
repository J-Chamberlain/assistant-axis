# Recovered Role Cloud Analysis

Startup status: **STARTUP VERIFIED**.

This local analysis rejudged recovered adaptive-extraction responses with the same GPT-4.1 temperature-0 role-expression rubric used for the amateur/playwright activation-cloud posthoc analysis, then processed recovered trickster/editor corrected PCA coordinates through the same cloud-summary logic.

Judge run: GPT-4.1, temperature 0, 1392 recovered responses scored, actual token usage {'completion_tokens': 187913, 'prompt_tokens': 1084673, 'total_tokens': 1272586}, estimated actual cost $3.6726.

## Response Counts and Retention

| run | n | score0 | score1 | score2 | score3 | retain>=2 | retain==3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| amateur_a100_cloud_60 | 60 | 0 | 1 | 25 | 34 | 59 (0.983) | 34 (0.567) |
| editor_matched64_1024 | 64 | 3 | 25 | 34 | 2 | 36 (0.562) | 2 (0.031) |
| editor_phase1_128 | 128 | 8 | 63 | 54 | 3 | 57 (0.445) | 3 (0.023) |
| playwright_a100_cloud_60 | 60 | 3 | 3 | 5 | 49 | 54 (0.900) | 49 (0.817) |
| trickster_phase1_1200 | 1200 | 0 | 0 | 2 | 1198 | 1200 (1.000) | 1198 (0.998) |

## Cloud Comparison Summary

| run | all centroid distance | ge2 centroid distance | all mean response distance | all volume proxy | all anisotropy |
|---|---:|---:|---:|---:|---:|
| amateur_a100_cloud_60 | 8.394 | 8.542 | 24.912 | 3073.713 | 3.416 |
| editor_matched64_1024 | 14.076 | 8.293 | 28.291 | 4592.419 | 5.419 |
| editor_phase1_128 | 13.627 | 9.658 | 30.309 | 5696.568 | 5.370 |
| playwright_a100_cloud_60 | 7.460 | 8.452 | 27.916 | 3187.526 | 6.371 |
| trickster_phase1_1200 | 13.637 | 13.637 | 23.866 | 1818.891 | 4.581 |

## Interpretation

Trickster behaves like a broad but high-yield recovered adaptive cloud: GPT-4.1 retains most responses and the score>=2/score==3 subsets remain well populated. Editor behaves unlike both trickster and the amateur/playwright A100 roles: retained counts are low in both the 512-token and 1024-token recovered runs, and token-cap relief does not solve the expression problem.

The editor/procedural-professional result is therefore best treated as an elicitation failure or assistant-adjacent collapse problem, not a recoverability problem. The saved hook vectors are usable for local analysis, but low retained counts make editor a weak candidate for downstream validated role-vector construction.

## Recommendation on Additional GPU Work

No additional GPU work is needed to recover these prior adaptive runs. If the goal is procedural-professional extraction, redesign the elicitation target before spending GPU: use a less generic assistant-adjacent procedural role, add stronger expression prompts, or run a small multi-role pilot comparing auditor/examiner/validator/editor before committing to a full extraction.
