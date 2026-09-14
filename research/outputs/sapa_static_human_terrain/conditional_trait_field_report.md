# SAPA Conditional Trait Field Over Big Five Space

## Bottom line

The frozen human-only analysis supports a coherent conditional trait field over five-dimensional Big Five space. All 12 primary narrower trait proxies pass the preregistered held-out quality gate. In every case, linear Ridge is retained over the nonlinear RBF-Nystroem alternative because the nonlinear model fails to improve held-out RMSE by the frozen 1% replacement threshold. At the resolution supported by these data, the expected narrower-trait profile therefore varies approximately directionally across Big Five space rather than requiring strongly curved trait surfaces.

The field is reproducible. In deterministic split halves, all 12 traits again select the linear family. Eleven of 12 pass the frozen combined recurrence gate for gradient direction and profile trajectory. `introspective` has a highly similar gradient direction across halves but fails the backbone-trajectory correlation criterion, so its pathwise interpretation remains weaker.

The field also reveals a second kind of sparsity beyond Big Five occupancy. Among 3,806 respondents with at least four observed primary narrow-trait scores, larger cross-validated partial trait-profile surprise is associated with lower Big Five occupancy density (Spearman rho = -0.2523). Broad-space sparsity and narrower-trait unusualness are related but not the same object.

## Source and independence

Human source: Harvard Dataverse SAPA V5, DOI `10.7910/DVN/SD7SVE`, respondent table SHA256 `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`.

Primary narrower-trait set: the 12 `ACCEPT_DIRECT` traits previously classified as moderate-or-better human measurement support in `research/outputs/sapa_bridge_psychometric_audit/sapa_trait_bridge_psychometric_support_v1.csv`: adventurous, altruistic, forgiving, grandiose, impulsive, manipulative, optimistic, pessimistic, traditional, innovative, introspective, and judgmental.

No model coordinate, activation vector, persona label, model trait score, or model-side geometry is used in fitting this field. The result is an independently constructed human-side object suitable for later comparison with model trait geometry.

## Leakage protection and cohort

The primary Big Five coordinates use the already-selected observed-only item-standardized scoring family. To prevent direct questionnaire-item overlap between predictors and the 12 target traits, `q_1385` is removed from Agreeableness and `q_1392` from Openness before scoring the common five-dimensional coordinate system. No other primary trait item overlaps a nonzero official IPIP100 Big Five key.

The resulting primary cohort contains 8,165 respondents with at least two observed scored items in every leakage-reduced Big Five domain. Old versus leakage-reduced coordinate correlations are 0.992 for Agreeableness, 0.989 for Openness, and 1.000 for Conscientiousness, Extraversion, and Emotional Stability.

## Conditional field model selection

Each narrower trait is standardized from its available oriented items without filling unanswered items. Respondents contribute to a trait field when at least one target-trait item is observed.

Deterministic five-fold respondent cross-validation compares linear Ridge on the five Big Five coordinates with RBF-Nystroem plus Ridge under the frozen nonlinear hyperparameter grid. A nonlinear field must improve held-out RMSE by at least 1% to replace the linear field.

All 12 traits retain the linear model. The only raw RMSE improvements from RBF are approximately 0.1% for grandiose and 0.4% for introspective, both below the frozen threshold. All 12 pass the field-quality gate of held-out Pearson r >= 0.20 and positive held-out R2. Held-out correlations range from 0.274 for adventurous to 0.523 for optimistic. The strongest fields are optimistic (r=0.523, R2=0.274), innovative (r=0.504, R2=0.254), pessimistic (r=0.497, R2=0.247), altruistic (r=0.459, R2=0.211), and impulsive (r=0.431, R2=0.186).

## Human trait-direction field

Because all selected primary fields are linear, the local Jacobian is constant in the primary fitted model. The strongest directional relationships are:

Agreeableness: altruistic +0.440, forgiving +0.345, manipulative -0.339, judgmental -0.278, optimistic +0.242, grandiose -0.191.

Conscientiousness: impulsive -0.317 and traditional +0.249 are the largest effects.

Extraversion: grandiose +0.212, adventurous +0.204, pessimistic -0.199, impulsive +0.177, optimistic +0.165, innovative +0.154, manipulative +0.152, introspective -0.142.

Emotional Stability: pessimistic -0.364, optimistic +0.322, impulsive -0.243, judgmental -0.240, forgiving +0.218.

Openness: innovative +0.444, introspective +0.293, traditional -0.246, grandiose +0.179, adventurous +0.128.

These coefficients are conditional associations, not causal effects.

## Trait-profile trajectory along the dense Big Five orientation

The previously frozen 11-point Big Five density backbone is used as a probe path through the leakage-reduced field. Because two items were removed from Big Five scoring for leakage control, the path is not refit here; it is treated as an approximately matched probe, justified by the very high old-versus-new coordinate correlations above.

Across the path from its low-score endpoint to its high-score endpoint, the largest total expected narrow-trait shifts, in standardized trait units, are: optimistic +1.434, pessimistic -1.355, impulsive -1.055, innovative +0.942, forgiving +0.843, altruistic +0.730, judgmental -0.630, grandiose +0.601, manipulative -0.440, and adventurous +0.423. Introspective and traditional change little over this particular path even though each has a clear gradient in other Big Five directions.

Adjacent backbone steps show coordinated rather than single-trait movement. In the lower and middle portions, optimistic rises and pessimistic falls while innovative increasingly rises. In the upper portion, the largest changes shift toward falling impulsivity and pessimism with continued rising optimism. This is the human-side analogue of a trait profile changing as location changes in a low-dimensional geometry.

## Conditional profile unusualness

For every trait, out-of-fold residuals are standardized by cross-validated residual SD. A respondent-level partial profile surprise score is computed only for respondents with at least four observed primary traits as the RMS standardized residual over the traits actually observed. No complete 12-dimensional profile is imputed.

N = 3,806 respondents meet this criterion. Partial profile surprise correlates negatively with Big Five occupancy density, Spearman rho = -0.2523, p = 2.44e-56. The lowest-surprise decile has median relative Big Five log density +0.527, whereas the highest-surprise decile has median -0.789.

This is a first-pass conditional unusualness measure. It does not estimate a full 12-dimensional residual joint probability because SAPA planned missingness prevents complete primary-trait profiles.

## Split-half robustness

The complete frozen candidate-model comparison is rerun independently in both deterministic halves. All 12 traits select linear Ridge in both halves.

Eleven of 12 pass the frozen recurrence rule requiring centroid gradient cosine >=0.75 and backbone trajectory correlation >=0.70. Gradient cosines for the 11 recurring traits range from 0.929 to 0.998, and their backbone trajectory correlations range from 0.965 to approximately 1.000.

`introspective` has gradient cosine 0.965 but backbone trajectory correlation 0.379 and therefore fails the frozen combined recurrence criterion.

## Measurement-quality and response-style sensitivities

A cleaner cohort requiring at least three observed Big Five items per domain contains 2,235 respondents. Every trait's Big Five gradient remains extremely close to primary, with cosine 0.981 to 0.997, and held-out prediction generally improves.

For the eight traits with at least 500 respondents who observed at least two of that trait's own items, gradient cosines relative to primary range from 0.986 to 0.998.

Adding respondent raw response mean and within-person response SD as nuisance covariates increases prediction somewhat, but the five-dimensional Big Five gradient remains close to primary for every trait, with cosine 0.926 to 0.998. Generic response style contributes information but does not explain away the principal field directions.

## Observed

A reproducible human-side conditional trait field exists across leakage-reduced Big Five space for all 12 primary trait proxies. Under the frozen model comparison, it is adequately described by linear directional gradients rather than requiring the tested nonlinear surfaces. Coordinated trait-profile changes occur along an independently established dense Big Five orientation. Narrower-trait profile surprise is greater, on average, in lower-occupancy Big Five regions.

## Interpretation

The human result supplies an empirical counterpart to the model-side idea that movement through a low-dimensional behavioral geometry entails coordinated changes in a higher-dimensional trait profile. The mapping is not deterministic: held-out R2 values are modest, so the same Big Five location permits substantial narrower-trait variation. The appropriate picture is a conditional distribution around a directional mean field.

The static result also separates two forms of rarity: sparse Big Five locations and unusual narrower-trait configurations conditional on Big Five location. They overlap but are distinct.

## Hypothesis for later longitudinal validation

A future longitudinal before/after dataset can freeze a baseline Big Five location, an observed Big Five change vector, and the corresponding trait-field-predicted narrow-trait change vector. It can then test whether actual within-person narrow-trait changes align with that prediction more than matched or permuted controls.

This would be a prospective test of whether cross-sectional trait-field directionality predicts real behavioral change. It must be designed after the current field is frozen, and the current static findings cannot be described as evidence that people actually move along these directions.

A later model-human comparison can separately test whether the independently constructed human Jacobian and profile trajectories correspond to the independently constructed model trait field. Longitudinal validation can then ask whether either or both static geometries forecast actual change.

## Unknown

The present analysis does not establish causal sequencing, which trait should change first, intervention leverage, transition probabilities, dynamical attractors, or population representativeness. A full joint conditional probability model over the 12 narrow traits remains limited by planned missingness and would require additional modeling assumptions.
