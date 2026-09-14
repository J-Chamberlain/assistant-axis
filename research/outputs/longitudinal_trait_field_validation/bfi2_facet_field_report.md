# BFI-2-Compatible SAPA Facet Field

## Bottom line

The preregistered human-only BFI-2-compatible facet field is now frozen before any participant-level PEACH longitudinal outcome data have been opened. All 15 intended BFI-2 facets pass the held-out quality gate. In every case the linear Ridge field is retained over the nonlinear RBF-Nystroem alternative because the nonlinear model fails to improve held-out RMSE by the frozen 1 percent replacement threshold.

The resulting 15 by 5 Jacobian is highly stable. Split-half gradient cosines range from 0.945 to 0.999, and the cleaner cohort requiring more Big Five and target-facet item coverage yields gradient cosines of 0.986 to 0.999 relative to the primary fit. This is therefore a strong independent human-side object for longitudinal validation.

## Source and construction

Human source is the same verified Harvard Dataverse SAPA V5 release used in the preceding human-terrain work, DOI `10.7910/DVN/SD7SVE`, 23,679 respondents. Big Five predictors use the already frozen observed-only item-standardized IPIP100 scoring family. Primary Big Five eligibility requires at least two observed scored items in every domain, yielding N = 8,585.

The 15 target facets are the published BFI-2 facet hierarchy: Sociability, Assertiveness, Energy Level, Compassion, Respectfulness, Trust, Organization, Productiveness, Responsibility, Anxiety, Depression, Emotional Volatility, Intellectual Curiosity, Aesthetic Sensitivity, and Creative Imagination.

Each target is constructed from the pre-outcome SAPA source-scale families frozen in `bfi2_compatible_sapa_field_freeze.md`. Every SAPA item appearing in any official IPIP100 predictor key is excluded from every target proxy before fitting, so target items are disjoint from the five predictor keys. Surviving target item counts range from 8 to 26 per facet. No unanswered target item is imputed.

## Held-out field quality

All 15 facets pass the frozen requirement of held-out Pearson r at least 0.20 and positive held-out R2.

The strongest held-out fields are Productiveness with r = 0.589 and R2 = 0.347, Sociability r = 0.579 and R2 = 0.335, Depression r = 0.567 and R2 = 0.322, Assertiveness r = 0.567 and R2 = 0.322, Compassion r = 0.530 and R2 = 0.280, and Responsibility r = 0.519 and R2 = 0.269.

The weakest retained field is Anxiety, r = 0.247 and R2 = 0.061. Aesthetic Sensitivity and Creative Imagination are also comparatively weak, with R2 approximately 0.099 and 0.111. These remain above the frozen quality gate and are retained rather than post-hoc removed.

No facet selects the nonlinear candidate. The largest positive RBF improvement is approximately 0.17 percent for Trust and 0.15 percent for Creative Imagination, well below the preregistered 1 percent replacement threshold. For most facets the RBF candidate performs slightly worse than the linear field.

## Frozen Jacobian

The final linear Jacobian maps standardized Big Five displacement to expected standardized facet displacement.

Extraversion most strongly predicts Sociability +0.492, Assertiveness +0.482, and Energy Level +0.333.

Agreeableness most strongly predicts Compassion +0.491, Respectfulness +0.376, and Trust +0.279.

Conscientiousness most strongly predicts Productiveness +0.487, Organization +0.467, and Responsibility +0.463.

Emotional Stability most strongly predicts lower Emotional Volatility -0.458 and lower Depression -0.353. The Anxiety relation is weaker, with Emotional Stability -0.130 and Extraversion -0.165.

Openness most strongly predicts Intellectual Curiosity +0.435, Creative Imagination +0.324, and Aesthetic Sensitivity +0.247.

Cross-domain terms are retained and sometimes meaningful. For example, Extraversion also predicts lower Depression, Agreeableness contributes to Aesthetic Sensitivity, and Openness contributes to Assertiveness. The longitudinal test will use the complete frozen Jacobian rather than only the nominal within-domain entries.

## Robustness

Independent deterministic split halves produce nearly identical gradient directions. The smallest half-to-half gradient cosine is 0.945 for Anxiety; the next smallest is 0.974 for Trust. All other facets are at least 0.983, with most above 0.99.

A cleaner sensitivity cohort requires at least three observed IPIP100 items in every Big Five domain and at least two observed items for the specific target facet. Gradient cosine relative to the primary fit ranges from 0.986 to 0.999 across all 15 facets.

These robustness results exceed the prespecified recurrence thresholds by a wide margin.

## Observed

A reproducible 15-facet conditional personality field can be estimated from SAPA using target items fully disjoint from the Big Five predictor items.

At the supported resolution, the field is approximately linear. Broad-domain displacement corresponds to coordinated lower-level facet displacement, with expected strongest loadings closely aligned to the BFI-2 domain hierarchy but with nonzero cross-domain structure.

## Interpretation

This field provides a clean independent bridge into the PEACH intervention. The prospective prediction is now fixed before longitudinal participant outcomes are seen: for any observed Big Five change vector `ΔB`, the expected lower-level change is `J × ΔB`, where `J` is the saved 15 by 5 human Jacobian.

A successful longitudinal test would show that an independently estimated cross-sectional human broad-to-narrow trait geometry predicts actual within-person change in another sample and measurement system.

## Unknown

The field does not establish causal pathways, temporal ordering among facets, intervention leverage, or that people preferentially travel along high-density routes. Cross-instrument equivalence between SAPA facet proxies and the BFI-2 facets is approximate rather than identity. The longitudinal analysis must therefore prioritize directional alignment, sign agreement, and rank structure over exact magnitude matching.

No model coordinate, activation vector, persona label, or model-side outcome was used in this construction.
