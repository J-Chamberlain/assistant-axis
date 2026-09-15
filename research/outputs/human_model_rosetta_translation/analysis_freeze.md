# Human ↔ Model Rosetta Stone Profile Translation — analysis freeze

Status: frozen before inspecting matched-profile residuals or fitting translation models.
Date frozen: 2026-09-15
Study branch: `codex/human-model-rosetta-translation-v1`
Base: V1 verification commit `49f6994127cdffc19dc7d8ffe34ea981c04c6438`

## Scope

This is an aggregate profile-shape study. It does not modify, retune, overwrite, or reclassify the V1 individual bridge, and it does not optimize against V1 outcomes or errors. It cannot establish human/model psychological equivalence or individual-level generalization.

## Frozen inputs and primary scope

- Primary model: Qwen family profiles from the prior frozen aggregate correspondence study.
- Llama and Gemma: fixed-pair descriptive replications only; no model chosen by translation performance.
- Human source: exact prior frozen aggregate SAPA profile solution; no reclustering or relabeling.
- Model source: exact prior frozen consensus family solution; no reclustering.
- Primary family pairs: prior injective A–D assignments at each eligible K=`4,5,6,7,8,10`; K=9 remains diagnostic/ineligible.
- Matching replication: prior full-profile injective maximum-total-Pearson assignment is recovered descriptively, but it is circular for translation assessment and is not treated as held-out evidence.

## Anchor/target separation

Before examining residuals, the stricter translation test is frozen to match human and model profiles using only the 12 prior SAPA traits with moderate-or-better human measurement support:

`adventurous, altruistic, forgiving, grandiose, impulsive, manipulative, optimistic, pessimistic, traditional, innovative, introspective, judgmental`

The target set is the remaining 33 `ACCEPT_DIRECT` traits in the prior 45-trait vocabulary, selected by exact complement. No `ACCEPT_CLOSE` traits enter. Anchor matching uses the same frozen profile normalization as the prior study, Pearson correlation, and the same injective A–D assignment rule. Translation quality is evaluated only on target traits not used for matching. The partition is immutable.

## Translation candidates and validation

The candidate family is fixed before fitting: identity/direct bridge; global intercept/scale; strongly regularized trait-wise affine calibration; orthogonal Procrustes; and constrained Ridge linear mapping. Primary validation is leave-one-matched-pair-out over the four anchor-matched A–D pairs at each eligible K, with hyperparameters selected inside training folds. Metrics are target-profile Pearson, cosine, RMSE, standardized RMSE, and change versus identity. A descriptive full-profile recovery is reported separately from the anchor-only held-out target test.

## Nulls and seeds

The primary cluster-pairing null permutes model-family labels across matched pairs while preserving marginal human/model profiles. The trait-label null permutes target trait identities within the frozen target set while preserving anchors. The translation-structure null independently permutes target coordinates across model profiles, preserving each target trait's marginal distribution. The search-adjusted match null repeats anchor-only matching after a deterministic target-preserving model-profile permutation. Each null uses seed `2026091501` and 2,000 draws, with the exact matching/fit procedure repeated within each draw. If a null cannot be completed, it is recorded as not run rather than replaced.

## Classification rule

SUPPORTED requires a low-complexity candidate to improve held-out target prediction over identity, with the improvement recurring across held-out pairs, and the relevant structural nulls controlled. MIXED means reproducible but localized or sensitive evidence. WEAK / ABSENT means no stable out-of-sample improvement beyond identity. In-sample fit alone is never sufficient.

## Privacy and stopping

Only aggregate/statistical artifacts may be committed. Raw SAPA respondent data, respondent IDs, masks, posteriors, scores, and V1 private predictions remain untracked. No HRS/LISS/HILDA/MIDUS/SOEP data, new inference, activation extraction, GPU, RunPod, or external model API is permitted.
