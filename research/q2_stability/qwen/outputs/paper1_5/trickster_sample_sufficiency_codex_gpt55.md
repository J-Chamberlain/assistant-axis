# Trickster Sample Sufficiency Analysis

Date: 2026-05-26
Model used for analysis: GPT-5.5

## Scope

This is a local CPU-only analysis of available Phase 1 activations. It does not validate role expression and does not claim Lu replication success. Score-conditioned analysis is added automatically if the Phase 2 score JSONL exists.

## Validation

- Records: 1200 / 1200
- Unique `(sp_idx, q_idx)` pairs: 1200 / 1200
- Activations loaded: 1200 with dimension 5120
- Activation load errors: 0
- Lu reference tensor: `downloads/hf_vectors/qwen-3-32b/role_vectors/trickster.pt` with shape `[64, 5120]`
- Phase 2 scores present: `True`

## Lu Reference Dispersion

Lu row-to-mean cosine p05/p50/p95: `0.695369` / `0.899715` / `0.975110`.
Lu dispersion, defined as std cosine(row_i, Lu_mean), is `0.083971`.

## Candidate Subsets

| Subset | n | cos(mean, Lu mean) | cos(mean, full 1200 mean) | internal std | Criterion A n | Criterion B n | Criterion C n | Criterion D n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all_1200 | 1200 | 0.958211 | 1.000000 | 0.009222 | 4 | 4 | 4 | 4 |
| non_truncated | 467 | 0.953492 | 0.997753 | 0.008858 | 4 | 4 | 4 | 4 |
| truncated | 733 | 0.958973 | 0.999119 | 0.009031 | 4 | 4 | 4 | 4 |
| sp_idx_0 | 240 | 0.957463 | 0.999027 | 0.010528 | 4 | 4 | 4 | 4 |
| sp_idx_1 | 240 | 0.954445 | 0.998359 | 0.008490 | 4 | 4 | 4 | 4 |
| sp_idx_2 | 240 | 0.946804 | 0.990149 | 0.007826 | 4 | 4 | 4 | 4 |
| sp_idx_3 | 240 | 0.951703 | 0.990919 | 0.009517 | 4 | 4 | 4 | 4 |
| sp_idx_4 | 240 | 0.955978 | 0.995866 | 0.007018 | 4 | 4 | 4 | 4 |

## Operational Answers

### 1. What is the best current estimate of the minimum n needed for a stable trickster vector?

Based on all available Phase 1 activations, the raw bootstrap Criterion A minimum is `4`, but the provisional operational minimum is `16` after applying the n>=16 floor used by the adaptive stopping rule. The stricter target is `16`.

### 2. Under which criterion is that estimate made?

The raw estimate uses Criterion A: p05 cosine(sample_mean, subset_full_mean) >= 0.95. The operational estimate applies a floor of 16 activations because pre-scoring subsets below that size are too brittle to treat as a workflow rule. The stricter target uses Criterion B, p05 cosine(sample_mean, subset_full_mean) >= 0.98.

### 3. How does the estimate compare to Lu et al.'s fixed 64-row cap?

Lu's fixed 64-row cap is `appropriate` for trickster under this pre-scoring analysis.

### 4. Does truncation change the answer?

Truncation materially changes the Criterion A minimum: `False`. Non-truncated Criterion A n is `4`, while truncated Criterion A n is `4`.

### 5. Are system prompts equally efficient, or does one prompt produce more stable geometry?

System prompts are not identical. Criterion A minima across `sp_idx` are `[4, 4, 4, 4, 4]`, so prompt-level efficiency should remain visible in future extraction decisions.

### 6. Can future persona extractions use an adaptive stopping rule?

Yes, but use it alongside a fixed target. The adaptive SE rule is useful as an early warning and stopping diagnostic, but fixed n keeps personas comparable.

### 7. What fixed target n should be used until Phase 2 scoring is available?

Use `n=64` available activations as the provisional default target, while preserving all metadata needed to rerun the score-conditioned analysis.

### 8. What should change after score-conditioned analysis is possible?

Rerun this same script after score output exists and set the target from `score>=2` and `score==3` subsets rather than from all available activations.

### 9. What should be written into the project workflow as the provisional sample-size rule?

Until Phase 2 scoring exists, use a fixed target of 64 available activations per persona as the provisional default and require at least the Criterion A minimum from this analysis; once scores exist, rerun this script and set the target from score>=2 and score==3 subsets, not from all available activations.

## Interpretation Guardrails

This analysis uses all available Phase 1 activations and truncation-defined subsets. It does not claim that all 1200 activations are qualifying role-expression samples, and score-conditioned analysis remains pending.
