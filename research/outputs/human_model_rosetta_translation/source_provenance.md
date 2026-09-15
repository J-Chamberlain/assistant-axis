# Human ↔ Model Rosetta Stone — source provenance

Status: source record prepared before Rosetta residual inspection.
Date: 2026-09-15

## Prior correspondence recovered from canonical local Git history

The prior aggregate correspondence study is the AA-12 line in local Git history. Its frozen method is commit `c71bcf9` (`research/outputs/human_model_profile_correspondence/analysis_preregistration.md`), its common-space representations are frozen at `ba095f6`, its primary correspondence result at `96c3e0d`, and its robustness results at `e1d10da`. The prior verification artifact is `1bca429`.

The prior study used aggregate SAPA latent profiles and reconciled model-family profiles, not respondent-level projection. Human profiles were a frozen observed-cell product-multinomial mixture bank at K=4,5,6,7,8,10 (K=9 diagnostic only). Model profiles were four primary three-model consensus families A–D, with E secondary. Profiles were expressed in the frozen 45-trait direct SAPA bridge; human profile values used observed-only item expectations, frozen orientation, observed item mean/SD, and equal item weights. Model values were frozen within-model role-level trait z-scores aggregated to families.

The prior matching rule was maximum-total-Pearson injective assignment of A–D to distinct human profiles at each eligible K, with unmatched human profiles allowed. The global statistic was the maximum over eligible K of the mean Fisher-z of the four assigned correlations. The primary null consistently permuted the 45 human trait labels across all human profiles/K values, recomputed correlations and assignments, and retained the maximum over K for 20,000 draws (seed `2026091304`). The focal prior result was K=10, back-transformed mean r `0.5201688077382118`, search-adjusted p `0.0000499975`; the prior robustness artifact classified the aggregate correspondence `STRONG AGGREGATE CORRESPONDENCE`. This is a descriptive recovery input here, not an independent translation-validation result.

## Inputs for this Rosetta follow-up

This follow-up reuses the prior frozen numerical banks and exact profile identities. The Qwen family representation is primary; Llama and Gemma are fixed-pair descriptive replications only. No new human clustering, model clustering, respondent scoring, inference, activation extraction, or V1 outcome inspection is performed.

Source hashes are recorded in the prior `common_space_manifest.json`; the SAPA respondent release hash is `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`. Respondent-level data remain local and are not copied into tracked outputs.
