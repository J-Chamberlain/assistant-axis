# Human-Only SAPA Psychometric Structure Audit of the Provisional Trait Bridge

## Result in one sentence

**Twelve of the 45 `ACCEPT_DIRECT` links survive the frozen human-data structural audit at moderate-or-better support: 9 high and 3 moderate.** Thirty are structurally weak/redundant under the preregistered reuse and discriminant rules, and 3 single-item proxies have insufficient internal/part-whole evidence. This is provisional human-data structural support, not psychometric validation and not evidence of human/model correspondence.

## Scope and provenance

- Human data: SAPA Project release V5, DOI `10.7910/DVN/SD7SVE`, 23,679 respondents and 696 psychological items.
- Bridge: 45 coordinate-blind `ACCEPT_DIRECT` links (primary) and 29 `ACCEPT_CLOSE` links (secondary sensitivity) from the frozen Phase 1b semantic review.
- Scoring evidence: exact SAPA wording, the item dictionary, source-scale inventory, and `superKey696.csv` scoring signs.
- Primary statistic: pairwise-complete Pearson correlation on oriented 1–6 responses. Spearman is a sensitivity analysis.
- Missingness: treated as SAPA's randomized planned item administration. There was no complete-case analysis and no respondent/item mean imputation.
- Model information: none. The script loads no persona, activation, trait-cosine, predictor, occupation, or model-coordinate artifact.

The decision rules were frozen in [`psychometric_support_rubric.md`](psychometric_support_rubric.md) at commit `6bf36c0` before inspecting response covariance. A later cleanup removed four Markdown hard-break trailing spaces but changed no criterion or threshold; the verifier checks line content after trailing-space normalization against the frozen commit. The complete source chain and hashes are in [`source_manifest.json`](source_manifest.json).

## Observed

### 1. Primary 45-link result

| Human-measurement tier | Count | Direct traits |
|---|---:|---|
| High human-measurement support | 9 | adventurous, altruistic, forgiving, grandiose, impulsive, manipulative, optimistic, pessimistic, traditional |
| Moderate support | 3 | innovative, introspective, judgmental |
| Redundant / broad | 30 | agreeable, anxious, artistic, assertive, bitter, callous, calm, conscientious, creative, cynical, dominant, emotional, empathetic, extroverted, gregarious, melancholic, meticulous, neurotic, paranoid, perfectionist, playful, rebellious, reserved, resilient, secular, serene, stoic, temperamental, theatrical, vindictive |
| Insufficient | 3 | curious, dramatic, patient |

At the component-diagnostic level, 11 direct traits met `STRONG STRUCTURAL SUPPORT`, 1 met `MODERATE STRUCTURAL SUPPORT`, 30 were `WEAK / REDUNDANT`, and 3 had `INSUFFICIENT EVIDENCE`. The final human-measurement tier additionally applies the frozen semantic-tier, item-count, reliability, reuse, and effective-N rules.

### 2. Internal coherence and source convergence

Among the 45 direct mappings, 38 multi-item proxies had strong internal coherence, 3 moderate coherence, and 1 weak coherence. Three were single-item only. The 42 multi-item standardized alphas had median `0.723` (range `0.215–0.923`); these are descriptive pairwise-correlation alphas because contributing respondents differ by item pair. Omega was not estimated: two- and three-item proxy models are underidentified or saturated and would add false precision.

Source-scale convergence was strong for 41 direct proxies, weak for theatrical, and not internally estimable for the three single-item proxies after the required part-whole correction. Theatrical had mean inter-item `r = 0.120` and intended-source-scale `|r| = 0.118` (rank 91/131), versus a strongest alternative association of `0.500`.

The single-item cases—curious, dramatic, and patient—are not empirically rejected. They cannot supply internal reliability, and their one-item intended source scales have no remaining item after part-whole exclusion, so the frozen rubric assigns insufficient evidence.

Pearson and Spearman proxy correlations agreed closely. Across the 990 direct proxy pairs, the two correlation vectors correlated `0.9974`; median absolute difference was `0.0093`, maximum `0.0754`, with 20 sign differences concentrated around near-zero associations. A reliable local polychoric implementation was unavailable. This did not block the preregistered Pearson primary analysis; the SAPA SPI development documentation also reports a very small average Pearson/polychoric difference and uses Pearson.

### 3. Reuse and discriminant structure

The direct tier uses 96 distinct items and 70 source scales; maximum reuse is 4 direct traits per item and 6 per source scale. Across all 74 links those totals are 129 items and 78 scales, with maxima of 4 and 7.

Across 224 retained-trait pairs sharing at least one item or named source scale:

- 4 are exact or inverse item-set aliases;
- 34 lose at least `0.20` absolute correlation when shared items are removed;
- 11 are same-source-scale high-redundancy pairs;
- 99 behave as neighboring constructs;
- 76 remain differentiated by the frozen rule.

Median absolute correlation across these shared-evidence pairs fell from `0.4185` to `0.3793` after shared items were removed where both proxies retained evidence. Exact aliases include assertive/dominant, mercurial/temperamental, zealous/passionate, and the inverse secular/spiritual pair. Other conspicuous same-scale or shared-item relationships include calm/serene, bitter/vindictive, creative/innovative, extroverted/gregarious, and cruel/callous. The pair-level values and remaining item counts are preserved in [`bridge_reuse_sensitivity.csv`](bridge_reuse_sensitivity.csv).

### 4. Human trait-proxy dimensionality

The direct 45×45 pairwise proxy matrix is positive semidefinite to numerical tolerance (minimum raw eigenvalue approximately zero; maximum PSD adjustment `< 1e-8`). It does not reduce to one unique dimensionality count:

- Horn-style parallel analysis retains 6 components;
- 10 eigenvalues exceed 1;
- participation-ratio effective rank is `12.44`;
- entropy effective rank is `20.84`;
- 5 components account for 50% of variance, 16 for 80%, and 24 for 90%.

Average-linkage clustering selected 2 clusters, but the silhouette was only `0.151`; the division is weak rather than a clean taxonomy. Together, these diagnostics show substantial common broad-factor variance plus narrower residual differentiation—not 45 independent measurements.

### 5. Human-side Big Five relationships

Each direct proxy was related only to official SAPA/IPIP100 Openness, Conscientiousness, Extraversion, Agreeableness, and inverse Emotional Stability scoring keys, with proxy items excluded from the relevant scale association. The strongest domain was Neuroticism for 14 traits, Agreeableness for 11, Extraversion for 9, Openness for 6, and Conscientiousness for 5.

Median descriptive multiple `R²` from the five correlated Big Five domains was `0.334` (IQR `0.264–0.405`); 42/45 traits were below `0.50`. Temperamental (`0.518`), creative (`0.514`), and extroverted (`0.511`) were the only direct proxies at or above `0.50`. These pairwise-matrix multiple associations are descriptive, not respondent-level regressions. The residual-matrix diagnostic requires a nontrivial PSD correction (`0.122` maximum adjustment), so its large residual effective rank is treated cautiously.

### 6. `ACCEPT_CLOSE` sensitivity

Adding the 29 close links yields 74 proxies. Five close links reach moderate support—adaptable, avoidant, disorganized, naive, and spontaneous—while 19 are redundant/broad and 5 are insufficient single-item cases. Under the semantic-tier rule no close link is labeled high.

The combined matrix has participation-ratio effective rank `15.14` and 11 parallel-analysis components, versus `12.44` and 6 for the direct tier. It uses 33 additional distinct items but adds only 2.70 participation-ratio dimensions and 5 moderate-support links. Thus the secondary tier increases content breadth and some covariance dimensionality, while most added links do not become differentiated human measurements.

### 7. Planned-missingness constraints

For the 96 direct-tier items, individual administration counts range from 2,327 to 4,381. The median item-pair overlap is 490 (range 296–961). A respondent observes a median of 10/96 items and zero fully observed direct proxies, although a median of 11 proxies has at least one administered evidence item. No respondent observes all 96 items.

For all 129 retained items, administration counts range from 2,327 to 5,902 and median item-pair overlap is 504 (range 289–1,212). A respondent observes a median of 13/129 items and one fully observed proxy. No respondent observes a complete 129-item profile.

These are administration-pattern facts, not ordinary item nonresponse rates. Group-level pairwise covariance is well supported, but literal respondent-level 45- or 74-trait complete profiles are unavailable without a measurement model.

## Interpretation

The semantic bridge contracts sharply when the question changes from “is the wording plausible?” to “does it form a coherent and sufficiently distinct measurement in human responses?” Twelve direct links satisfy the frozen moderate-or-better rules. Nine of those are especially clean provisional candidates. The remaining direct links are often coherent and source-convergent individually, but fail distinctness because the bridge reuses the same items/scales for neighboring labels. They should not be counted as 30 independent negative findings; rather, many are competing labels for a smaller set of human constructs.

The direct matrix contains more information than a handful of Big Five labels alone: the effective-rank and Big Five association diagnostics retain narrower structure. It nevertheless falls far short of 45 independent dimensions. Adding close links mostly adds redundancy or weakly identified single-item content, not a comparably strong expansion of the bridge.

The bridge remains suitable for designing a future human/model projection study only in restricted form: start from the 9 high and 3 moderate direct links, resolve exact aliases and reuse, obtain independent expert review, and demonstrate a defensible respondent-level scoring model under planned missingness. The current 45- or 74-trait table should not be projected as though it were a validated complete human trait profile.

The most viable later scoring candidates are official source-scale partial scoring with preregistered item minimums, full-information latent scoring for multi-item constructs, and Bayesian/ordinal IRT only where item pools are adequate. Pairwise covariance remains the group-level reference. Complete-case analysis, simple mean filling, and unconstrained high-dimensional multiple imputation are poor fits.

## Unknown

- Independent expert agreement with the semantic bridge and with item direction choices.
- Test–retest stability, measurement invariance, and criterion validity of the provisional proxy composites.
- Whether a reduced latent measurement model can recover reliable respondent-level scores under SAPA's administration design.
- Whether the human proxies and any model-derived constructs are psychometrically equivalent.
- Whether human trait distributions correspond to model representations or whether any human/model projection would be scientifically meaningful.

## Answers to the nine decision questions

1. **Moderate-or-better direct links:** 12/45 (9 high, 3 moderate).
2. **Inherently single-item direct links:** 3/45; internal reliability is not estimable.
3. **Weak/contradictory structure:** theatrical is the clearest coherence/convergence failure; 30 direct links are weak/redundant after discriminant/reuse rules, and 3 are insufficient rather than contradicted.
4. **Reuse effect:** 4 exact/inverse aliases and 34 shared-item-sensitive pairs exist across retained tiers; the median shared-evidence-pair `|r|` falls by about `0.039` after removable overlap, while certain individual drops exceed `0.20`.
5. **Effective dimensionality:** 6 components by parallel analysis and effective rank 12.44 (entropy rank 20.84) for 45 direct proxies; no single count is definitive.
6. **Big Five versus narrow structure:** broad domains explain meaningful variance (median descriptive `R² = 0.334`), but 42/45 remain below 0.50 and dimensionality diagnostics retain narrower structure.
7. **Effect of close links:** only 5/29 reach moderate support; most add redundancy or insufficient evidence, despite increasing effective rank from 12.44 to 15.14.
8. **Readiness:** a restricted bridge supports methods design after independent expert review; the full bridge is not ready for respondent-level projection.
9. **Viable scoring approaches:** pairwise covariance for structural work; compare official partial-scale, full-information latent, and carefully identified Bayesian/IRT scoring for later respondent scores.

## Boundaries

No model geometry, persona labels, activation vectors, trait-vector cosine scores, occupation outcomes, or downstream correspondence results were used. No human-to-model projection was performed. No respondent-level record was written or committed. No GPU, RunPod, model inference, activation extraction, or external model API was used.
