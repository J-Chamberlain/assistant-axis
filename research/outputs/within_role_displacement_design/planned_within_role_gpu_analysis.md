# Planned Within-Role GPU Analysis

- Generated UTC: 2026-05-31T16:16:54.255289+00:00
- model_used: GPT-5.5
- No GPU was used to prepare this plan.

## Purpose

Test whether variation among five positive role instructions and 240 extraction questions predicts response-activation displacement around a fixed released role centroid.

## Later Execution Plan

1. Wait until D01/extraction-boundary uncertainty is resolved.
2. Select `target_role`.
3. Reconstruct 1,200 inputs: five positive role instructions x 240 shared extraction questions.
4. Generate deterministic Qwen/Qwen3-32B responses with the corrected hook-based extraction path.
5. Extract response-token activations with the same activation object, token mask, pooling, centering, and PCA basis used for the inherited geometry.
6. Compute observed coordinate and displacement:

```text
observed_delta_pcj = observed_pcj - released_target_role_centroid_pcj
```

7. Optionally judge role expression for every response and compare all responses vs retained role-expressive responses.

## Planned Statistical Tests

- Instruction main effects on PC1/PC2/PC3 displacement.
- Question main effects on PC1/PC2/PC3 displacement.
- Additive instruction + question prediction of observed displacement.
- Interaction diagnostics if signal and sample size justify it.
- Sign accuracy: predicted displacement direction vs observed displacement sign.
- Pearson/Spearman correlation between predicted displacement scores and observed displacement.
- Compare all-response analysis to retained-response-only analysis after fresh role-expression scoring.

## Interpretation Caveat

This study tests within-role displacement, not role-centroid recovery. A successful result would show that prompts move activations in predictable directions around a fixed role address.
