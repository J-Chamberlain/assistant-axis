# PEACH longitudinal validation — data-access resolution

Status: active planning artifact on `gpt/longitudinal-trait-field-validation`.

## Preferred path

The original PNAS OSF archive at `https://osf.io/g3yfz/` contains analysis-specific `.sav` files with broad Big Five domain scores but not the 60 BFI-2 item responses or 15 facet scores required by the frozen individual-level facet-change validation.

A separate PEACH reanalysis by Olaru et al., *Personality change through a digital-coaching intervention: Using measurement invariance testing to distinguish between trait domain, facet, and nuance change*, explicitly analyzed the same trial at BFI-2 facet and item level and states that data, code, and materials are available at `https://osf.io/q7vgf/`. This is the preferred source for the individual-level longitudinal test because the published analysis necessarily uses facet/item-level repeated measures.

Primary next acquisition target: download the complete OSF storage archive from `q7vgf` and inspect whether it contains participant-level repeated BFI-2 items/facets at pretest, posttest, and follow-up. If present, preserve the previously frozen test unchanged: use the SAPA-derived 15-facet Jacobian to predict each participant's facet-change vector from their observed five-domain change vector, then test individual-level directional similarity with the preregistered controls.

## Weaker path using currently available public outputs

Before obtaining participant-level facet data, published aggregate facet-change effects can be compared descriptively with the frozen SAPA-derived facet gradients. This is not a substitute for the individual-level validation because intervention targeting, baseline selection, and group-level aggregation all affect the observed mean changes.

The Olaru et al. paper reports the following self-reported standardized changes from pretest to posttest/follow-up for the three focal goal groups:

- Increase Extraversion: Sociability +0.89/+1.00, Assertiveness +0.12/+0.15, Energy Level +0.20/+0.17.
- Increase Conscientiousness: Organization +0.42/+0.49, Productiveness +0.64/+0.93, Responsibility -0.09/+0.19.
- Decrease Negative Emotionality: Anxiety -0.57/-0.89, Depression -0.22/-0.36, Emotional Volatility -0.36/-0.39.

The frozen SAPA BFI-2 facet Jacobian predicts, for a pure +1 SD domain displacement:

- +Extraversion: Sociability +0.492, Assertiveness +0.482, Energy Level +0.333.
- +Conscientiousness: Organization +0.467, Productiveness +0.487, Responsibility +0.463.
- +Emotional Stability, corresponding to lower Negative Emotionality: Anxiety -0.130, Depression -0.353, Emotional Volatility -0.458.

Within-domain rank agreement is therefore mixed. Conscientiousness matches exactly (Productiveness > Organization > Responsibility). Extraversion partially matches because Sociability is correctly strongest but Assertiveness and Energy Level swap order. Negative Emotionality does not match the predicted differential ordering: the intervention shows Anxiety changing most, whereas the cross-sectional SAPA field predicts Emotional Volatility changing most strongly.

A pooled within-domain standardized comparison across these nine facet effects is weakly positive only: Pearson approximately 0.19 and Spearman approximately 0.27 at posttest; Pearson approximately 0.19 and Spearman approximately 0.22 at follow-up. These descriptive values are post hoc and must not be treated as the primary validation statistic.

## Interpretation

Observed: published PEACH facet changes are heterogeneous within broad domains. The cross-sectional human trait field correctly anticipates some of that structure, especially Conscientiousness and the dominance of Sociability within Extraversion, but not the strong Anxiety-focused change within Negative Emotionality.

Interpretation: this mixed aggregate result increases the value of the frozen individual-level test rather than resolving it. It suggests the longitudinal process may not simply follow the cross-sectional conditional field, which is exactly the empirical question the participant-level validation is intended to answer.

Unknown: whether the `q7vgf` public archive exposes the necessary participant-level repeated item/facet data in a directly usable file; this must be verified from the archive itself before execution.
