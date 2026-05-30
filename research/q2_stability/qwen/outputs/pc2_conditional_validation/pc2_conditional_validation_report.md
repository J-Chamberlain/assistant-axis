# Does PC2 Survive Control for PC1?

model_used: GPT-5.5 High Reasoning

## Method

Observed: canonical activation PCA coordinates were loaded from `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv` and blinded candidate ratings were loaded from `research/q2_stability/qwen/outputs/blinded_axis_rater_study/axis_rater_scores.csv`. The candidate ratings were produced from anonymized no-label prompt dossiers before PCA coordinates, clusters, and persona names were joined for analysis. This study therefore uses the richest complete 275-persona text source currently available locally: the blinded no-label dossier corpus. Full rollout-response text is not available for all personas, so this remains a prompt-dossier validation rather than a full behavior-corpus validation.

Observed: 273 personas were common between the canonical PCA table and the blinded rater score table. PC1 was divided into 10 percentile bands of roughly 27-28 personas each. Within each band, PC2 was tested against maturity, abstraction, expertise/intellectual sophistication, uncertainty exposure, residence time under uncertainty, and coherent action under unresolved uncertainty.

## PC1 Band Construction

Observed: 10 decile bands were used for coverage across the full PC1 range. This is narrow enough to reduce gross PC1 variation while preserving enough within-band n for correlations and matched-pair search. See `pc2_band_inventory.csv` for boundaries and persona membership.

## Candidate Comparison

| Rank | Candidate | Pooled band-demeaned Pearson | Pooled Spearman | Mean abs within-band Pearson | Pooled R2 |
|---:|---|---:|---:|---:|---:|
| 1 | abstraction | -0.618 | -0.597 | 0.621 | 0.382 |
| 2 | maturity | -0.440 | -0.319 | 0.379 | 0.193 |
| 3 | expertise | -0.430 | -0.381 | 0.477 | 0.185 |
| 4 | coherent_action_under_unresolved_uncertainty | 0.427 | 0.334 | 0.404 | 0.182 |
| 5 | residence_time_under_uncertainty | -0.417 | -0.362 | 0.371 | 0.174 |
| 6 | uncertainty_exposure | -0.026 | -0.040 | 0.230 | 0.001 |

## Required Interpretation

1. Which candidate explanation performed best?

Observed: `abstraction` performed best by absolute pooled band-demeaned Pearson correlation with PC2 after removing band means: r=-0.618, R2=0.382. `maturity` was second by the same criterion.

2. Which explanations failed?

Observed: the weakest pooled predictors were uncertainty_exposure. In practical terms, simple uncertainty exposure did not carry the residual PC2 structure well after PC1 banding.

3. Does coherent action under unresolved uncertainty remain viable?

Inferred: coherent action remains viable only as part of a compound interpretation. Its pooled band-demeaned correlation was r=0.427, weaker than abstraction's r=-0.618. This means the original formulation captures something real but is not the dominant residual predictor in this conditional test.

4. Is abstraction actually the stronger explanation?

Observed: abstraction is stronger than coherent action in this test if one judges by within-band residual prediction. Its sign is negative, meaning lower PC2 personas are more abstract after PC1 is approximately controlled. That matches the low-PC2 mythic/theoretical/world-model pole and the physicist/scientist contrast better than the coherent-action-only framing.

5. Are multiple variables required?

Inferred: yes. Abstraction performs best, but maturity, expertise, residence time, and coherent action are correlated explanatory neighbors rather than cleanly independent constructs. The strongest current reading is that PC2 is an abstraction/integration/developmental axis, not a single-variable uncertainty-capacity axis.

6. Current confidence level for PC2 interpretation.

Inferred: confidence should move from low toward moderate-low for a revised PC2 interpretation. The viable formulation is: low PC2 reflects abstract, world-model-like, integrated, long-residence cognition; high PC2 reflects developmental, reactive, socially volatile, or less integrated action. Speculative: coherent action under unresolved uncertainty may be a downstream behavioral expression of that deeper abstraction/integration structure rather than the primary axis itself.

## Matched-Pair Analysis

Observed: 75 matched pairs were selected with |PC1 difference| <= 5.0 and maximal PC2 separation. See `pc2_matched_pairs.csv` for all pairs and candidate-score differences.

Strongest supporting pair: `teenager` vs `crystalline` has PC1 difference 3.057 and PC2 difference 122.122. High-PC2 `teenager` has abstraction 35.000, maturity 28.000, coherent action 78.000; low-PC2 `crystalline` has abstraction 96.000, maturity 62.000, coherent action 24.000.

Strongest counterexample found by abstraction sign: `adolescent` vs `parasite` has PC2 difference 91.238, but the high-PC2 member has higher abstraction by 21.000. This is a warning against treating abstraction as a complete explanation.

## Physicist Test

- physicist: PC1 29.160, PC2 -17.278, abstraction 88.000, expertise 94.000, coherent action 18.000, residence time 86.000
- scientist: PC1 41.455, PC2 -11.640, abstraction 76.000, expertise 94.000, coherent action 12.000, residence time 88.000

Inferred: the physicist/scientist contrast favors abstraction over coherent-action capacity. Physicist is lower on PC2 than scientist and is rated more abstract, while coherent action is not clearly higher for physicist. Nearby professional roles show the same broad low-PC2 tendency for philosopher/theorist/scholar-like world-model roles compared with more institutional/practical scientific roles.

## Mythic / Developmental Test

### Mythic group

| Persona | PC1 | PC2 | Maturity | Abstraction | Expertise | Uncertainty exposure | Residence time | Coherent action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mystic | -42.169 | -36.161 | 66.000 | 88.000 | 63.000 | 86.000 | 74.000 | 28.000 |
| prophet | -53.777 | -32.708 | 70.000 | 90.000 | 55.000 | 85.000 | 70.000 | 30.000 |
| sage | -30.696 | -30.205 | 94.000 | 88.000 | 72.000 | 68.000 | 94.000 | 8.000 |

### Developmental group

| Persona | PC1 | PC2 | Maturity | Abstraction | Expertise | Uncertainty exposure | Residence time | Coherent action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| infant | -42.890 | 44.700 | 2.000 | 0.000 | 0.000 | 55.000 | 3.000 | 96.000 |
| fool | -37.407 | 47.921 | 42.000 | 58.000 | 45.000 | 65.000 | 48.000 | 50.000 |
| procrastinator | -16.544 | 69.468 | 20.000 | 15.000 | 20.000 | 60.000 | 10.000 | 85.000 |
| toddler | -36.268 | 71.156 | 8.000 | 12.000 | 8.000 | 70.000 | 18.000 | 85.000 |

Observed: mythic/deep-world-model roles are much lower on PC2 than the developmental/reactive group. The largest group separations are abstraction, maturity, expertise, residence time, and coherent action; uncertainty exposure alone is less discriminative.

Inferred: this is the critical result. PC2 is not simply uncertainty exposure. The axis separates roles that can inhabit abstract or unresolved world-model space from roles whose uncertainty is developmentally unresolved, impulsive, stalled, or socially volatile.

## What Changed Relative to Prior PC2 Interpretations

Inferred: prior language centered too much on coherent action under unresolved uncertainty. This study shifts the preferred interpretation toward abstraction/integration as the primary residual predictor after PC1 control, with coherent action retained as an important but secondary behavioral manifestation.

## Key Judgment Calls

- Used 10 PC1 percentile bands rather than fixed-width PC1 units because the persona distribution is uneven and deciles preserve within-band sample size.
- Used existing blinded no-label dossier ratings rather than creating new coordinate-aware labels, preserving the no-PCA-while-rating constraint.
- Treated expertise as the existing `intelligence_expertise_score` from the rater study, because it is the closest available blinded score.
- Interpreted signs substantively: lower PC2 corresponds to higher abstraction/integration; higher PC2 corresponds to developmental/reactive or less integrated roles.

## Recommended Next Test

Run a second-model or human blinded rating study over the same PC1-matched pairs only, forcing raters to choose which member is higher on abstraction, maturity/integration, and coherent action while still hiding PCA coordinates. If abstraction again beats coherent action inside matched PC1 pairs, revise the working interpretation note to demote coherent-action-under-uncertainty from primary PC2 label to secondary mechanism.
