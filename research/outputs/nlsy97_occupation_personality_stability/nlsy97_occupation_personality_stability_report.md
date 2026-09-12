# NLSY97 occupational personality centroid stability

## Can NLSY97 produce stable human occupational personality centroids suitable for later model comparison?

Qualified yes. Among the 151 reportable narrow four-digit Census cells, 27 pass the frozen empirical criteria (9 strong and 18 moderate). Among 22 reportable SOC major families, 20 pass (18 strong and 2 moderate). Aggregation makes means precise, but broad occupations explain only a small fraction of personality variance and mix substantively different jobs. The defensible conclusion is feasibility for selected aggregate human comparisons—not evidence that occupations are personality types.

## Primary cohort and measurement

The official extract contains 8,984 respondents. 7,044 have complete Round-12 TIPI data, and 6,261 reproduce the AA-1 complete-TIPI plus official-code count. Excluding Census code 9920 because it represents no recent occupation, and requiring a positive Round-12 weight plus valid VSTRAT/VPSU, leaves 6,261 respondents.

TIPI domains use the [official Gosling scoring key](https://gosling.psy.utexas.edu/scales-weve-developed/ten-item-personality-measure-tipi/): Extraversion items 1 and reversed 6; Agreeableness reversed 2 and 7; Conscientiousness 3 and reversed 8; Emotional Stability reversed 4 and 9; Openness 5 and reversed 10. Each pair is averaged, then all five domains are standardized globally using Round-12 survey weights. The instrument is deliberately short; its two-item reliabilities and item availability are reported in `analysis_cohort_summary.json`. These are low-resolution domain summaries, not high-resolution personality profiles.

Round-12 industriousness and traditionalism (four items each) and Round-16/17 grit (eight items) are inventoried but were not combined into an omnibus score. Round-6 Goldberg Agreeableness and Conscientiousness are kept as the separate replication layer. The official codebook—not the convenience labels in the original AA-1 item manifest—determines all eight bipolar directions; the corrected manifest is included in this branch.

## Between-occupation signal and within-occupation heterogeneity

- Narrow observed finite-sample ICCs: Openness to Experience 0.082, Conscientiousness 0.100, Extraversion 0.094, Agreeableness 0.120, Emotional Stability 0.098.
- Narrow sampling-error-corrected sensitivity ICCs: Openness to Experience 0.038, Conscientiousness 0.056, Extraversion 0.049, Agreeableness 0.078, Emotional Stability 0.054.
- Broad observed finite-sample ICCs: Openness to Experience 0.012, Conscientiousness 0.021, Extraversion 0.017, Agreeableness 0.036, Emotional Stability 0.020.
- Broad sampling-error-corrected sensitivity ICCs: Openness to Experience 0.008, Conscientiousness 0.017, Extraversion 0.013, Agreeableness 0.032, Emotional Stability 0.016.

The observed narrow decomposition assigns 8.2%-12.0% of variance to the 400 sampled occupation means, but this is inflated because many means are estimated from sparse cells. Subtracting the population-share-weighted Taylor variance of those means reduces the narrow signal to 3.8%-7.8%. At the broad level, the corrected signal is only 0.8%-3.2%. Thus within-occupation heterogeneity dominates (roughly 92%-99%, depending on level, domain, and estimator). The separate unweighted random-intercept ANOVA sensitivity is also saved. None of these descriptive associations identifies selection, socialization, or a causal occupational effect.

## Sample-size stability curve

- Narrow: N=20: median expected error 0.429 (median cell p95 0.699; 41 reference cells); N=50: median expected error 0.263 (median cell p95 0.425; 10 reference cells); N=100: median expected error 0.172 (median cell p95 0.268; 1 reference cells).
- Intermediate: N=20: median expected error 0.440 (median cell p95 0.710; 46 reference cells); N=50: median expected error 0.264 (median cell p95 0.415; 25 reference cells); N=100: median expected error 0.180 (median cell p95 0.307; 6 reference cells).
- Broad: N=20: median expected error 0.464 (median cell p95 0.763; 21 reference cells); N=50: median expected error 0.277 (median cell p95 0.458; 18 reference cells); N=100: median expected error 0.179 (median cell p95 0.299; 14 reference cells).

The curve compares repeated subsample centroids with each full finite-sample cell centroid. N=20 leaves expected 5D error near 0.43-0.46 SD units and is not a confirmatory threshold. N=50 is a defensible lower bound only for moderate/exploratory cells that also pass vector-stability checks. N=100 is a sensible strong-centroid screen, not a guarantee. The narrow N=100 summary has only one eligible reference cell under the frozen `full N >= max(2n,n+20)` rule, so broad/intermediate curves provide the stronger empirical calibration at that size.

## Frozen feasibility tiers

- Narrow: STRONG CENTROID = 9, MODERATE / EXPLORATORY = 18, BROAD-FAMILY ONLY = 120, UNSTABLE / TOO SPARSE = 4.
- Intermediate: STRONG CENTROID = 25, MODERATE / EXPLORATORY = 13, BROAD-FAMILY ONLY = 31, UNSTABLE / TOO SPARSE = 3.
- Broad: STRONG CENTROID = 18, MODERATE / EXPLORATORY = 2, BROAD-FAMILY ONLY = 0, UNSTABLE / TOO SPARSE = 2.

Tier thresholds were committed before the trait outcomes were inspected. They jointly require N, design-respecting bootstrap precision, split-half distance, and uncertainty relative to within-cell heterogeneity. Shrinkage is reported only as a sensitivity analysis and cannot upgrade a tier.

## Narrow versus broad occupation tradeoff

Official SOC minor and major groups sharply increase sample size and generally reduce centroid uncertainty. They also increase the number of distinct four-digit Census occupations inside a cell and therefore the semantic distance from a specific role. `occupation_granularity_tradeoff.csv` exposes N gain, child-code count, heterogeneity, bootstrap error, split-half error, and tier at all three levels. A stable parent is a possible aggregate comparison only; it does not rescue the meaning of an unstable narrow job.

| Requested comparison | Narrow code | Narrow result | Most specific stable official parent | Feasibility interpretation |
|---|---:|---|---|---|
| Secretary / administrative assistant | 5700 | N=113; STRONG CENTROID | Not needed | Direct narrow comparison is feasible at the stated tier. |
| Accountant / auditor | 0800 | N=59; MODERATE / EXPLORATORY | Not needed | Direct narrow comparison is feasible at the stated tier. |
| Caregiver | 4610 | N=59; MODERATE / EXPLORATORY | Not needed | Direct narrow comparison is feasible at the stated tier. |
| Counselor | 2000 | N=44; BROAD-FAMILY ONLY | intermediate 21-1000 (Counselors, Social Workers, and Other Community and Social Service Specialists), N=111; STRONG CENTROID | Precision improves only by changing the construct; semantic-cost flag applies. |
| Artisan proxy | 8960 | N=54; MODERATE / EXPLORATORY | Not needed | Direct narrow comparison is feasible at the stated tier. |
| Teacher / instructor | 2340 | N=24; BROAD-FAMILY ONLY | broad 25-0000 (Education, Training, and Library Occupations), N=370; STRONG CENTROID | Precision improves only by changing the construct; semantic-cost flag applies. |
| Lawyer | 2100 | N=17; UNSTABLE / TOO SPARSE | No stable reportable official parent | Not a current candidate. |
| Programmer | 1010 | N=13; BROAD-FAMILY ONLY | intermediate 15-1000 (Computer Specialists), N=114; STRONG CENTROID | Precision improves only by changing the construct; semantic-cost flag applies. |
| Engineer | 1530 | N<10 or zero; suppressed/empty | intermediate 17-2000 (Engineers), N=55; MODERATE / EXPLORATORY | Precision improves only by changing the construct; semantic-cost flag applies. |
| Therapist | 3240 | N<10 or zero; suppressed/empty | intermediate 29-1000 (Health Diagnosing and Treating Practitioners), N=115; STRONG CENTROID | Precision improves only by changing the construct; semantic-cost flag applies. |
| Psychologist | 1820 | N<10 or zero; suppressed/empty | broad 19-0000 (Life, Physical, and Social Science Occupations), N=55; MODERATE / EXPLORATORY | Precision improves only by changing the construct; semantic-cost flag applies. |
| Journalist | 2810 | N<10 or zero; suppressed/empty | intermediate 27-3000 (Media and Communication Workers), N=55; MODERATE / EXPLORATORY | Precision improves only by changing the construct; semantic-cost flag applies. |
| Actor | 2700 | N<10 or zero; suppressed/empty | broad 27-0000 (Arts, Design, Entertainment, Sports, and Media Occupations), N=159; STRONG CENTROID | Precision improves only by changing the construct; semantic-cost flag applies. |

## Round-6/Round-12 recurrence

The population-cell recurrence is mixed but more consistent for Conscientiousness:

- Narrow population cells (k=34): Agreeableness Pearson r=0.364; Conscientiousness r=0.485.
- Intermediate population cells (k=35): Agreeableness Pearson r=0.452; Conscientiousness r=0.490.
- Broad population cells (k=18): Agreeableness Pearson r=-0.176; Conscientiousness r=0.393.

Among respondents retained in the same official group at both waves:

- Narrow: not estimable (fewer than three cells with at least 20 stable respondents).
- Intermediate stable cells (k=6; 244 respondents across those cells): Agreeableness r=-0.720; Conscientiousness r=0.521.
- Broad stable cells (k=9; 614 respondents across those cells): Agreeableness r=0.449; Conscientiousness r=0.813.

The Round-6 items were administered only to respondents age 14 or younger at the end of 1996, and the canonical extract has no Round-6 survey weight. With few stable cells, especially at the intermediate level, correlations are volatile. The evidence supports modest Conscientiousness recurrence and no robust general recurrence claim for Agreeableness. These are occupational-pattern checks, not estimates of personality change.

## Occupation discriminability

- Narrow: balanced accuracy 0.049 versus 0.037 baseline across 27 classes.
- Intermediate: balanced accuracy 0.035 versus 0.026 baseline across 39 classes.
- Broad: balanced accuracy 0.084 versus 0.050 baseline across 20 classes.

Big Five profiles contain little occupation information: accuracy is only 0.009-0.034 above the balanced multiclass baseline. This is scientifically consistent with the small corrected ICCs and extensive distributional overlap, and should not be read as a useful individual occupation classifier.

## Stable future role candidates

The post-tier crosswalk produces 94 mapping rows covering 94 model-role names and 28 distinct stable human cells. Only 7 rows retain the mapped narrow occupation; 87 require an intermediate or broad parent and carry a semantic-cost flag. Secretary/administrative assistant is strong at the narrow level; accountant/auditor, caregiver, and the `production workers, all other` artisan proxy are moderate. Counselor, programmer, engineer, therapist, psychologist, journalist, teacher/instructor, and actor have only more aggregated stable options. Lawyer has no stable reportable parent in this sample. This is a candidate list for later preregistration, not a model comparison.

## Expected-question audit

1. Between-occupation variation exists, but the design-error-corrected signal is modest: 3.8%-7.8% at narrow and 0.8%-3.2% at broad levels.
2. Within-occupation variance is the overwhelming majority in every domain.
3. Five-dimensional centroids become reasonably stable around N=50 for exploratory use and around N=100 for a stronger screen, conditional on empirical stability.
4. The earlier N>=20/50/100 cutoffs were sensible as sparse/exploratory/strong screens, but N=20 is too noisy and N alone is insufficient.
5. 27 reportable narrow occupations are stable enough: 9 strong and 18 moderate.
6. 20 broad families are stable enough: 18 strong and 2 moderate.
7. `future_model_role_comparison_candidates.csv` gives every current role correspondence and flags aggregation cost.
8. Accountant, caregiver, secretary/administrative assistant, and the artisan proxy are plausible narrow future comparisons; counselor is plausible only as an explicitly broader community/social-service comparison.
9. Lawyer, programmer, engineer, therapist, psychologist, journalist, and actor are too sparse at the narrow level; only some have stable broader substitutes.
10. Broadening improves precision, often sharply, but can impose unacceptable semantic cost when the target is a specific job.
11. Round-6/Round-12 recurrence is mixed; Conscientiousness recurs more consistently than Agreeableness, with major measurement and cell-count limitations.
12. Occupation is adequate for selected preregistered aggregate comparisons, but the low ICCs and near-chance classification rule out treating it as a strong human personality grouping variable.

## Observed

Human occupational TIPI means, dispersion, design uncertainty, resampling stability, sample-size error, variance decomposition, cross-wave recurrence, and descriptive discriminability.

## Interpretation

Some official occupation groups are sufficiently reproducible to serve as human comparison distributions in a later, separately preregistered study. Stability means the group mean is estimated consistently; it does not mean the group is internally homogeneous, highly distinctive, or psychologically equivalent to a model role.

## Unknowns and future hypothesis

Whether any human occupational distribution corresponds to an LLM occupational-role prototype remains untested. A later study would need an independent construct bridge, frozen comparison metrics, multiplicity control, and explicit decisions about the semantic cost of occupation aggregation.

No model geometry was used. No human-to-model projection was performed. No respondent-level NLSY97 data were committed. No GPU, RunPod, model inference, activation extraction, or external model API was used.
