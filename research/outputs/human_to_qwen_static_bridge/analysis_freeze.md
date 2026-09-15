# Human-to-Qwen Static Bridge V1 — Analysis Freeze

Freeze status: **FROZEN BEFORE OUTCOME ANALYSIS**

This is a separate study. It does not continue AA-7's failed respondent-projection gate and cannot be cited as though AA-7 justified human-to-model projection.

## Frozen primary design

- Primary traits: exactly the 12 traits in `primary_trait_set.json`.
- Human scoring: reviewed SAPA evidence items only; frozen orientation signs; observed-only item means; no deterministic filling of missing target items.
- Human/model scale: within-trait empirical CDF followed by midrank inverse-normal transform, with human CDF fit within training folds for validation. Percentile scale is the fixed sensitivity analysis.
- Model geometry: Qwen canonical PC1-PC3. PC1-PC6 is secondary/provisional only.
- Sparse location: model-only Ridge from observed anchor-trait normal scores to PC1-PC3, deterministic model-persona CV and fixed alpha grid; cache by exact anchor subset.
- Trait decoder: model-only Ridge from PC1-PC3 to each target-trait normal score, with deterministic model-persona CV.
- Validation: respondent-level deterministic five-fold outer cross-fitting; all target predictions from one respondent remain in one fold; target trait is excluded from its own anchors.
- Primary anchor rule: six remaining observed anchors, because coverage-only screening yields 1,935 respondents and 17,209 respondent-target pairs. Five and four anchors are fixed fallbacks only if the preceding floor fails.
- Primary endpoint: equal-weight Fisher-z macro-average of within-trait Pearson correlations, requiring at least 100 cases per trait; report per-trait and pooled Pearson/Spearman, RMSE, calibration slope, sample sizes, respondents, and anchor counts.
- Uncertainty: respondent-cluster bootstrap, seed fixed in the analysis script, 2,000 draws when computationally reasonable.
- Nulls: 1) bridge-label permutation; 2) independent within-trait persona-row permutations with Qwen PCs fixed; 3) within-fold human target shuffles. Each uses 1,000 fixed-seed draws.
- Gate: SUPPORTED only if macro correlation is positive, respondent-bootstrap 95% CI excludes zero, and empirical p <= .05 against all three null families. Otherwise classify as MIXED or WEAK / ABSENT according to the locked result rule; any projection is then DESCRIPTIVE / UNVALIDATED.

## Explicit boundaries

No Llama or Gemma, longitudinal outcome analysis, causal interpretation, behavioral equivalence, theory-of-change claim, new model inference, activation extraction, GPU, RunPod, or external model API. Human respondent rows and all row-level derivatives remain local under `data_external/` and are never committed.

The freeze commit must precede any held-out human prediction, result inspection, null outcome, or projected human distribution.
