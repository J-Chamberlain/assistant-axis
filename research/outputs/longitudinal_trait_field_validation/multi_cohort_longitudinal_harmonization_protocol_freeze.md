# Multi-Cohort Longitudinal Trait-Field Harmonization Protocol — Frozen Design

Status: FROZEN before inspecting participant-level longitudinal outcomes in the long-horizon candidate cohorts.

Freeze date: 2026-09-14.

Branch: `gpt/longitudinal-trait-field-validation`.

## Purpose

This protocol defines one harmonization and analysis procedure for testing whether within-person changes in broad Big Five coordinates are accompanied by lower-level trait-profile changes predicted by the independently constructed SAPA human trait field. It is designed to be applied consistently across heterogeneous longitudinal datasets rather than creating a bespoke bridge after seeing each dataset's results.

The central prospective prediction is:

`observed broad-trait change -> frozen predicted lower-level change -> observed lower-level change`

The protocol is human-only. Model activations, persona coordinates, model trait scores, model clusters, and model-side geometry must not be used to construct, tune, adjudicate, or rescue any dataset bridge.

## Prior-outcome boundary

The project has already inspected published aggregate PEACH facet-change patterns as a preliminary sanity check. PEACH therefore cannot serve as a pristine outcome-blind confirmation cohort for the multi-cohort protocol, although participant-level analyses can still be reported as a secondary intervention test using the frozen field and frozen rules.

At the time of this freeze, participant-level longitudinal lower-level trait outcomes from HILDA, HRS, MIDUS, SOEP, and LISS have not been inspected for this project. Any of those cohorts that later meet the measurement and access criteria can serve as prospective long-horizon validation cohorts.

## Canonical broad coordinate system

Every eligible dataset is translated into the same five signed broad coordinates:

1. Agreeableness
2. Conscientiousness
3. Extraversion
4. Emotional Stability
5. Openness

If a source instrument uses Neuroticism or Negative Emotionality, it is sign-reversed so that higher values mean Emotional Stability.

Published/released scoring keys are primary. Item wording, reverse scoring, response scale, wave availability, and instrument version must be recorded before longitudinal outcomes are examined.

Do not standardize each wave independently. For each analysis interval, scoring transformations are estimated from the baseline wave and applied unchanged to the follow-up wave so that real longitudinal mean shifts are not erased. If a study publishes latent scores on a common longitudinal metric, those may be used instead, with provenance recorded.

## Canonical lower-level vocabulary

The common lower-level vocabulary is the 15 BFI-2 facet system, three facets per broad domain:

Extraversion: Sociability, Assertiveness, Energy Level.

Agreeableness: Compassion, Respectfulness, Trust.

Conscientiousness: Organization, Productiveness, Responsibility.

Negative Emotionality / Emotional Stability side: Anxiety, Depression, Emotional Volatility. Source scores remain in their natural facet direction for the lower-level outcome vector, while the broad coordinate is oriented as Emotional Stability.

Openness: Intellectual Curiosity, Aesthetic Sensitivity, Creative Imagination.

Datasets do not need to contain literal BFI-2 facet scales. Their lower-level items, adjectives, facets, or subscales may be mapped to this vocabulary only under the frozen bridge rules below.

## Frozen predictive field

The canonical human prediction field is the already-frozen SAPA-derived 15 x 5 BFI-2 facet Jacobian:

`research/outputs/longitudinal_trait_field_validation/frozen_bfi2_facet_jacobian.csv`

This field was estimated entirely from SAPA before participant-level longitudinal outcome analysis and is not refit on any validation cohort.

For an observed broad-trait change vector `ΔB` in the five canonical coordinates, the predicted lower-level change is:

`ΔF_pred = J_SAPA × ΔB`

Only rows of the frozen Jacobian corresponding to eligible mapped facets in a given dataset are used. Missing facets do not cause the field to be refit.

## Dataset bridge construction

Each dataset receives a separate bridge packet created before its longitudinal change outcomes are inspected. Bridge construction follows the same ordered evidence hierarchy:

1. Official published facet/subscale membership in the source instrument.
2. Exact source item wording and keyed direction.
3. External instrument documentation or published crosswalks to BFI-2/IPIP-like lower-level constructs.
4. Coordinate-blind semantic adjudication from wording and definitions only.
5. Baseline-wave psychometric coherence may downgrade a proposed bridge but cannot promote a semantically weak mapping merely because it predicts longitudinal outcomes.

No longitudinal change statistic, intervention effect, follow-up correlation, model geometry, or downstream prediction score may be visible during mapping adjudication.

### Mapping tiers

`DIRECT`: official facet membership, exact construct identity, or very close documented equivalent.

`CLOSE`: wording and external construct definitions support a narrow semantic match, but the source measure is not the canonical facet itself.

`PROXY`: broader, narrower, or neighboring construct that may be informative but is not sufficiently equivalent for the primary cross-cohort test.

`REJECT`: ambiguous, contradictory, multi-construct, or not defensibly mapped.

Primary analyses use DIRECT and CLOSE mappings only. PROXY mappings are sensitivity analyses only and can never rescue a failed primary result.

If multiple source variables map to one canonical facet, aggregation rules are frozen from source scoring/documentation or, when unavailable, use an equal-weight standardized mean after direction alignment. The aggregation rule cannot be chosen from longitudinal performance.

## Predictor-target leakage protection

A source item or variable cannot contribute simultaneously to a broad Big Five predictor coordinate and its lower-level target in the same primary test.

If an overlap exists, construct a leave-target-out broad score by removing the overlapping item(s) from the broad-domain predictor. If fewer than two nonoverlapping broad-domain indicators remain after removal, that facet-domain prediction is ineligible for the primary analysis.

If a dataset is too short to create a meaningful disjoint broad predictor and lower-level target, it may support only a domain-level or exploratory analysis and must not be represented as a facet-level validation.

## Measurement comparability across waves

Every source variable must have unchanged or documented-equivalent wording, keying, and response scale across the analyzed interval.

Measurement comparability is labeled before outcome analysis:

`M1`: same measurement across waves plus published or project-verified scalar/partial-scalar longitudinal invariance or an equivalent common latent metric.

`M2`: same items/wording/keying/response scale across waves with no known instrument change, but full scalar-invariance evidence is unavailable. Eligible for directional change tests, with mean-magnitude interpretations explicitly qualified.

`M3`: changed wording, changed response format, changing item set, or unresolved linking problem. Exploratory only; excluded from pooled primary confirmation.

Failure of measurement comparability causes downgrade or exclusion, not post-hoc remapping.

## Coverage and evidence tiers

A dataset is `HIGH-COVERAGE` if it provides at least 10 eligible canonical facets spanning at least 4 broad domains.

A dataset is `MULTI-DOMAIN ELIGIBLE` if it provides at least 6 eligible canonical facets spanning at least 3 broad domains, with no single broad domain supplying more than half of the included facets.

A dataset with 3-5 eligible facets or coverage concentrated in one/two domains is `DOMAIN-LOCAL / EXPLORATORY`.

A person-level observation enters the primary directional analysis only if the person has valid broad-coordinate change and valid observed lower-level change for at least 6 eligible facets across at least 3 broad domains. Dataset-specific domain-local analyses may use fewer facets but are reported separately.

These coverage thresholds may not be relaxed after seeing results.

## Time intervals

All measurement-compatible intervals are enumerated before outcomes are inspected. No interval is selected because it gives the strongest result.

For datasets with more than two waves, report:

1. all eligible adjacent-wave intervals;
2. the longest eligible interval;
3. prespecified common-duration intervals when the survey design naturally provides them.

The longest interval is the dataset-level long-horizon focal analysis when measurement compatibility is M1/M2 and analyzable sample size is adequate. Adjacent intervals assess local reproducibility and timescale dependence.

PEACH retains its pre/post and follow-up intervention intervals as secondary short-horizon tests.

## Change scoring

For each eligible participant and interval:

`ΔB = B_followup - B_baseline`

`ΔF_obs = F_followup - F_baseline`

`ΔF_pred = J_SAPA × ΔB`

All signs are defined before outcome analysis. Broad coordinates use the canonical direction above. Lower-level facets use the canonical BFI-2 facet direction named in the Jacobian.

The same baseline-derived scaling is applied at follow-up. Do not residualize away population-level longitudinal change unless a separately labeled sensitivity analysis explicitly requires it.

## Primary person-level endpoint

The primary person-level endpoint is cosine similarity between `ΔF_pred` and `ΔF_obs` over the eligible canonical facets available for that participant:

`cos(ΔF_pred, ΔF_obs)`

Participants with numerically zero predicted or observed change vectors are excluded from cosine computation and counted explicitly.

Report mean cosine, median cosine, participant-cluster/bootstrap confidence intervals, and the full distribution. Do not summarize only positive movers or intervention responders.

### Change-magnitude sensitivity

Direction becomes noisy when broad change is near zero. The primary result includes all eligible nonzero change vectors. A prespecified sensitivity repeats the analysis in the upper 50% of broad-change magnitude within each dataset/interval. This sensitivity cannot replace the all-eligible result.

## Cohort-level secondary endpoints

For each dataset/interval also report:

1. cosine similarity between the mean predicted and mean observed lower-level change vectors;
2. Pearson and Spearman association across canonical facets between mean predicted and observed changes;
3. calibration slope from observed lower-level change on predicted lower-level change, with uncertainty;
4. facet-specific predicted-versus-observed change associations where measurement supports them.

These are secondary to the person-level directional endpoint.

## Frozen null controls

Every primary dataset/interval uses the same null families.

### Null 1: participant pairing

Permute predicted change vectors across participants within the same dataset and interval, preserving the marginal distributions of predicted and observed change while breaking person-specific correspondence.

### Null 2: within-domain facet identity

Permute the canonical facet rows of the frozen Jacobian within each broad domain. This preserves broad domain membership while testing whether the specific lower-level facet pattern matters beyond generic domain movement.

### Null 3: broad-change direction

Apply random orthogonal rotations to the five-dimensional `ΔB` vectors using fixed seeds while preserving each participant's broad-change magnitude. This tests whether the specific observed direction through broad-trait space is informative.

Use at least 1,000 deterministic permutations/rotations per null family when computationally feasible. If a dataset is too small or computation is limited, use the maximum feasible count above 500 and report the exact finite-null resolution.

Empirical p-values use `(exceedances + 1) / (draws + 1)`.

## Split and robustness analyses

When sample size permits, repeat the full primary analysis in deterministic split halves or survey-design-appropriate independent subsamples. Report whether the sign and approximate magnitude of alignment recur.

Prespecified robustness checks include:

1. stricter DIRECT-only bridges;
2. M1-only measurement intervals when available;
3. high-coverage participants only;
4. alternate published scoring of the same source instrument when fixed in advance;
5. demographic or survey-weight sensitivity where weights are available and appropriate.

No robustness result may redefine the primary bridge after outcomes are seen.

## Sample-size status

`CONFIRMATORY-CAPABLE`: at least 300 eligible person-interval observations for the primary multi-domain test.

`EXPLORATORY`: 100-299 eligible observations.

`DESCRIPTIVE`: fewer than 100 eligible observations.

This label concerns precision only. A large convenience sample is not automatically population-representative.

## Cross-study synthesis

Do not pool raw questionnaires or force all studies onto one original score scale. Each study yields the same harmonized directional effect.

Primary synthesis reports:

1. dataset/interval mean cosine with bootstrap standard error;
2. empirical null percentile and p-value;
3. sign concordance across independent datasets;
4. random-effects meta-analysis of dataset-level mean cosine when at least three independent eligible datasets are available;
5. heterogeneity statistics and leave-one-dataset-out sensitivity.

Datasets, not person-interval rows, are the unit of evidence for cross-study replication. A very large single cohort must not dominate interpretation solely because of N.

## Prespecified exploratory moderators

The following are exploratory and cannot define success/failure of the primary test:

- interval duration / log years;
- intervention versus naturalistic change;
- age band;
- country;
- self-report versus observer report;
- measurement tier M1 versus M2;
- baseline trait location;
- broad-change magnitude.

These analyses test whether the geometry is more locally predictive, more intervention-sensitive, or population-dependent.

## Interpretation rules

### Finding supported by a dataset

Observed person-level alignment exceeds the frozen null controls with the same sign in the primary and key sensitivity analyses.

### Cross-study support

Multiple independent eligible datasets show positive above-null alignment under the same harmonization rules, with heterogeneity reported rather than hidden.

### Allowed interpretation

Cross-sectional human trait-field directionality predicts some structure in observed within-person lower-level personality change across independently measured longitudinal cohorts.

### Not established

Causal sequencing, which trait should change first, intervention leverage, attractors, energy barriers, transition probabilities, or deterministic personality trajectories.

A failure in one or more datasets is informative and must be retained. It may indicate timescale dependence, instrument dependence, population dependence, intervention-specific change, or failure of the cross-sectional field to predict longitudinal dynamics.

## Candidate cohort audit order

The following candidate datasets should be audited against this protocol before any participant-level outcome analysis:

1. HILDA
2. HRS
3. LISS
4. SOEP
5. MIDUS
6. PEACH as a secondary short-horizon intervention cohort

This ordering is operational, not a scientific ranking. A dataset that fails access, leakage, coverage, or measurement-comparability gates is downgraded or excluded without changing the protocol.

## Required per-dataset frozen artifacts

Before outcome analysis, each dataset must have:

1. source/provenance manifest;
2. wave and instrument inventory;
3. source-item/scale to canonical-domain/facet bridge with mapping tiers;
4. leakage audit and leave-target-out scoring decisions;
5. measurement-comparability tier per interval;
6. eligible interval list;
7. sample-size/coverage forecast based only on availability and missingness, not change outcomes;
8. signed analysis manifest containing the exact bridge file hashes and this protocol's commit.

Only after those artifacts are frozen may participant-level change outcomes be computed.

## Provenance and boundary

Primary predictive source artifact: `research/outputs/longitudinal_trait_field_validation/frozen_bfi2_facet_jacobian.csv`, derived from human SAPA responses.

Dependent future analyses: HILDA/HRS/LISS/SOEP/MIDUS/PEACH cohort-specific longitudinal validation packets and any later cross-study synthesis.

No model geometry is an input to this protocol. Any later comparison to model-side trait geometry must be a separate analysis that cannot alter the human longitudinal results.
