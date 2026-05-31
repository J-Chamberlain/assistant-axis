# Instance-Level Forecaster Dataset Recommendation

- Generated UTC: 2026-05-31T15:02:53.318157+00:00
- model_used: GPT-5.5

## Direct Recommendation

Use a reconstructed intended-input dataset now, on the Mac Mini, without GPU work:

- One row per role instruction-question pair.
- Input text fields: role name for metadata only, positive instruction text, extraction question text, optional rendered chat-template prompt if tokenizer is available locally.
- Target: released role centroid / role PCA coordinates for that role.
- Weighting: each of the 1,200 rows per role receives the same role-level target, because public data do not identify which individual rollouts succeeded.

This supports an improved instance-level prompt-to-centroid forecaster over intended elicitation inputs. It does not support successful-rollout-only or judge-filter-aware training.

## Why Successful-Rollout-Only Training Is Not Publicly Possible

Public artifacts do not include generated responses, response-level judge scores, or retained response IDs/masks for the original role vectors. The released Qwen role vector tensors shaped `[64, 5120]` are layer-by-hidden vectors, not 64 retained examples. Successful-rollout-aware training would require regenerating responses and judge scores or obtaining private original outputs.

## GPU Requirement

No GPU is needed for reconstructed intended-input forecasting. GPU work is needed only if the project chooses to regenerate rollout responses/activations or to build a successful-rollout-aware dataset from fresh runs.
