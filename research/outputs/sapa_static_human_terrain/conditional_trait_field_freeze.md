# SAPA Static Human Terrain — Conditional Trait Field Analysis Freeze

Status: frozen before inspecting any conditional trait-field result.

## Purpose

Estimate how independently defined narrower human trait proxies vary across five-dimensional Big Five space. This analysis asks: at a given Big Five location, what narrower trait profile is expected, how does that profile change under movement through Big Five space, and where are narrower-trait configurations conditionally unusual? It is a human-only structural analysis and uses no model coordinates, model trait scores, persona labels, or model-side geometry.

This is cross-sectional occupancy structure. Trait-field gradients are not behavioral transition probabilities, causal effects, intervention effects, or paths people actually traverse.

## Human source and fixed Big Five coordinates

Source: SAPA V5 respondent table, DOI 10.7910/DVN/SD7SVE, SHA256 `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`.

Reuse the already-frozen item-standardized observed-only Big Five scoring family. The primary five-dimensional coordinate system uses Agreeableness, Conscientiousness, Extraversion, Emotional Stability, and Openness.

To prevent direct item leakage into the primary 12-trait field, remove from the Big Five scoring keys any item that is also used by any of the 12 primary trait proxies. For the current 12-trait set this removes `q_1385` from Agreeableness and `q_1392` from Openness. All respondents are then rescored in one common leakage-reduced Big Five coordinate system. Eligibility remains at least two observed scored items in every Big Five domain after these exclusions. Coordinates are standardized over the eligible cohort.

## Primary narrower-trait set

Primary analysis uses the 12 `ACCEPT_DIRECT` traits previously classified as moderate-or-better human measurement support in the human-only SAPA psychometric audit:

adventurous, altruistic, forgiving, grandiose, impulsive, manipulative, optimistic, pessimistic, traditional, innovative, introspective, judgmental.

The exact item sets are inherited unchanged from `sapa_trait_bridge_psychometric_support_v1.csv` and the frozen provisional bridge. Trait item direction is semantic and fixed from item wording/released scale direction before field fitting. The only reverse-keyed primary items are handled mechanically where wording runs opposite the named trait, including `q_915` for forgiving and `q_905` for manipulative.

Each primary trait score is an observed-only item-standardized residual mean using that trait's available oriented items. No unanswered trait item is deterministically filled. A respondent may contribute to a trait model with at least one observed item for that trait.

## Conditional mean field

For each trait separately, fit a smooth predictor of standardized trait score from the five standardized leakage-reduced Big Five coordinates.

Two prespecified candidate model families are compared under deterministic five-fold respondent cross-validation:

1. linear Ridge on the five coordinates;
2. RBF-Nystroem features plus Ridge, allowing smooth nonlinear interactions.

For the nonlinear candidate, use 300 Nystroem components with fixed random seed 20260914. Select RBF gamma from `{0.1, 0.25, 0.5, 1.0}` and Ridge alpha from `{0.1, 1, 10, 100}` using training-fold inner cross-validation. Linear Ridge selects alpha from the same alpha grid. All preprocessing is fit inside training folds.

Primary selection per trait is lower held-out RMSE; correlation is secondary. A nonlinear model must improve held-out RMSE by at least 1% relative to linear Ridge to replace the linear model. Otherwise retain linear Ridge for parsimony. This rule is frozen before inspecting trait surfaces.

After model selection, refit the selected family on all respondents available for that trait.

## Field quality gate

For every trait report cross-validated N, RMSE, normalized RMSE, Pearson correlation, and R2. Traits with held-out Pearson correlation below 0.20 or nonpositive held-out R2 are retained in the audit table but not used for substantive gradient/corridor interpretation. No threshold is retuned after results.

## Local gradients and Jacobian

For each fitted trait field, compute numerical derivatives with respect to each Big Five coordinate by centered finite differences of 0.05 SD. Stack the 12 trait gradients into a 12 x 5 local Jacobian.

Evaluate the Jacobian at:

- the cohort Big Five centroid;
- the 11 already-saved Big Five density-backbone knots;
- fixed ±1 SD coordinate probes around the centroid, when those probes remain within the empirical 95% support envelope.

Report which narrower traits are predicted to rise or fall most strongly for movement in each Big Five direction. These are conditional associations, not causal trait changes.

## Trait-profile trajectories

Along the 11 frozen Big Five density-backbone knots, predict the 12-trait conditional mean profile. Standardize each predicted trait relative to its observed trait-score distribution. Save the complete 11 x 12 trajectory.

Quantify profile change between adjacent knots by Euclidean distance in standardized 12-trait profile space and identify the three traits contributing the largest absolute change at each step.

## Conditional unusualness

For each trait, compute out-of-fold residuals among observed trait scores. Standardize residuals by that trait's cross-validated residual SD.

Because complete 12-trait respondent profiles are unavailable under SAPA planned missingness, do not fabricate full residual vectors. Instead define respondent-level partial profile surprise only for respondents with at least four observed primary trait scores as the root-mean-square standardized residual across their observed traits. This score measures departure from the conditional trait field using available evidence only.

Assess whether high partial profile surprise concentrates in low Big Five occupancy density using Spearman correlation and decile summaries. Do not call high-surprise observations impossible or pathological.

## Split-half robustness

Repeat the complete model-selection and field-fitting procedure separately in the same deterministic split halves used by the prior terrain analyses. For each trait compare:

- selected model family;
- centroid gradient cosine similarity;
- correlation of predicted trait values across the 11 backbone knots.

A trait gradient is called split-recurring only if centroid gradient cosine >= 0.75 and backbone-trajectory correlation >= 0.70 with consistent overall sign/orientation.

## Sensitivities

1. Refit the primary field using the cleaner Big Five cohort requiring at least three observed items per Big Five domain after overlap exclusions.
2. Repeat using only respondents with at least two observed items for each specific trait where sample size remains >=500.
3. Report response-style sensitivity by adding respondent raw response mean and within-person response SD as nuisance covariates for traits whose field passes the primary quality gate. This is a sensitivity only and cannot replace the primary human trait field.

## Secondary 45-trait field

The 45 `ACCEPT_DIRECT` traits may be evaluated only after the primary 12-trait analysis is complete. It is secondary because 30/45 were previously classified as redundant/broad and three as single-item insufficient. No secondary result may be used to redefine the primary method.

## Interpretation boundary

Observed: conditional trait associations and profile structure in this SAPA convenience sample.

Interpretation allowed: some narrower trait combinations are more or less typical conditional on Big Five location, and movement through Big Five space is associated with coordinated changes in narrower trait profiles.

Not established: individual behavioral transitions, causal sequencing, intervention leverage, dynamical attractors, energy barriers, or representative-population prevalence.

A later longitudinal before/after study may test whether observed human change vectors align with the frozen cross-sectional trait-field predictions. That future test must be designed after this field is frozen and cannot retroactively alter this analysis.
