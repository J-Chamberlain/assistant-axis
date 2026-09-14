# Longitudinal Trait-Field Validation — Analysis Preregistration

Status: frozen before participant-level PEACH outcome data are downloaded or inspected.

## Primary question

For a participant with a measured Big Five change vector from baseline to a later wave, does an independently estimated human lower-level trait field predict the observed direction of narrower personality change better than target-permuted, direction-permuted, and covariance-matched null predictions?

The analysis is predictive and within-person. It does not assume that the intervention changes people along the cross-sectional density backbone, and it does not interpret the human trait field as a causal transition law.

## Representation

The primary predictor coordinates are the five BFI-2 domains, standardized using the baseline distribution of the longitudinal sample. A participant's displacement is `ΔB = B_later - B_baseline` in baseline-SD units.

The primary lower-level outcome representation is a BFI-2-compatible facet field frozen on SAPA before PEACH outcomes are inspected. The intended target set is the 15 BFI-2 facets, subject only to pre-outcome human-side measurement feasibility. Any facet excluded for inadequate SAPA measurement must be excluded before the PEACH participant-level file is opened.

The human field is represented by a frozen Jacobian `J`, with rows equal to retained lower-level traits/facets and columns equal to the five Big Five dimensions. The predicted within-person lower-level change is `ΔT_pred = J × ΔB`.

Observed lower-level change is computed from the repeated BFI-2 facet scores in the longitudinal dataset, standardized by baseline facet SD. No parameter in `J` is fit or recalibrated on longitudinal outcomes.

## Primary wave contrast

The primary contrast is baseline to immediate posttest because it maximizes alignment with the active intervention window and retains the largest post-baseline sample. Baseline to three-month follow-up is the prespecified persistence replication. If the one-year file can be linked to the same participant identifiers without ambiguity, baseline to one-year follow-up is secondary because of severe attrition.

The weekly BFI-2-S process dataset is a separate secondary analysis and will not replace a failed primary endpoint.

## Primary participant-level metrics

For each participant with sufficient repeated data, compute cosine similarity between predicted and observed lower-level change vectors. The primary aggregate statistic is the mean participant-level cosine, evaluated against a participant-preserving null distribution.

Secondary participant-level metrics are Pearson correlation across retained lower-level traits, sign agreement across traits with absolute observed change above a frozen noise floor, and normalized Euclidean prediction error after both predicted and observed vectors are scaled to unit norm. Magnitude calibration is secondary because the human field and BFI-2 longitudinal instrument come from different samples and measurement systems.

## Aggregate directional tests

In addition to person-level tests, compute the observed mean lower-level change vector within each major intervention goal group and compare it with the field prediction derived from that group's mean Big Five displacement. Report cosine similarity, trait-rank correlation, and sign agreement. Group-level analyses are descriptive complements to the individual-level primary test.

## Nulls and controls

The primary null independently permutes lower-level trait labels within the frozen Jacobian while preserving each participant's observed Big Five displacement and observed lower-level outcome vector. Repeat the complete scoring procedure for at least 10,000 deterministic permutations.

A second null applies random orthogonal rotations to the five-dimensional Big Five displacement vectors while preserving their norms and the empirical distribution of displacement magnitudes. This tests whether performance depends on the actual direction of change rather than change magnitude alone.

A covariance-matched control generates random lower-level Jacobians with row covariance matched to the frozen human field but without semantic row identity. This evaluates whether any smooth correlated field would achieve similar directional performance.

A baseline-change regression control predicts each lower-level outcome from its own baseline value and the five-dimensional Big Five change vector using only the longitudinal sample. This model is descriptive and cannot replace the independent-field primary test. It quantifies how much predictive information is available when longitudinal outcomes are allowed to tune coefficients directly.

## Measurement invariance and reliability

Because lower-level personality measures can change nonuniformly under intervention, the primary facet scoring uses the published BFI-2 scoring key but reports measurement-invariance diagnostics before substantive interpretation. Facets with clear scalar noninvariance remain valid descriptive change outcomes but are flagged because mean change may partly reflect item-specific response change.

The analysis will reproduce published domain/facet change patterns sufficiently to verify file interpretation before testing the new trait-field hypothesis. Reproduction checks are validation only and must not be used to tune the frozen human field.

## Attrition and missingness

Primary participant-level analyses require baseline and posttest Big Five domain scores plus at least a prespecified minimum number of retained lower-level facets at both waves. The exact minimum is frozen at 80% of retained facets unless the source file structure makes facet-level missingness structurally impossible, in which case complete BFI-2 wave completion is used.

Report baseline differences between included and excluded participants on available demographics and baseline Big Five scores. Repeat the primary analysis with inverse-probability-of-retention weights estimated only from baseline variables. Weighted results are sensitivity analyses, not replacements for the unweighted primary result.

## Observer-report sensitivity

Where observer BFI-2-S data are available at matched waves, construct the closest facet-level observer outcome vector and test whether self-report Big Five displacement predicts observer-reported lower-level change in the same direction. This analysis is lower powered and uses a shorter instrument, so it is secondary. It is nevertheless important because it weakens a pure same-rater response-style explanation if directional correspondence replicates.

## Goal-group sensitivity

Repeat the primary test separately for the three largest goal groups documented in the trial: lower Negative Emotionality, higher Conscientiousness, and higher Extraversion. Openness and Agreeableness goal groups are reported if sample sizes support stable estimation but are not required for the primary conclusion.

A positive result is not defined as every group passing separately. The preregistered primary evidence is the participant-level full-sample test. Group heterogeneity is expected and reported.

## Frozen interpretation thresholds

Evidence is classified as strong if the primary mean participant-level cosine exceeds the 99th percentile of all three null families and has the same sign and above-null direction at the three-month follow-up. Evidence is moderate if it exceeds the 99th percentile of the label-permutation null and at least one additional null, with direction preserved at follow-up. Evidence is weak if the observed statistic is positive but fails these gates. Evidence is absent if the primary statistic is near or below the null center.

No threshold will be changed after outcomes are inspected.

## Bridge-specific secondary analysis

The existing SAPA 12-trait human/model bridge remains frozen. Before PEACH outcomes are opened, semantic compatibility between those 12 traits and BFI-2 facets/items may be reviewed using only canonical trait definitions and published BFI-2 measurement definitions. Only direct or clearly close proxies are retained. If fewer than four bridge traits survive, no bridge-specific longitudinal test is run. This prevents outcome-driven crosswalk construction.

## Longitudinal hypothesis

If the static human field contains information about real directions of personality change, participants whose Big Five coordinates move by `ΔB` should exhibit lower-level changes more aligned with `J × ΔB` than expected under semantic-label, direction, or covariance-matched controls.

A positive result would establish prospective directional validity of the static human field under this intervention context. It would not establish that people choose the easiest path, that density determines transition probability, that changing one trait causes another to change, or that the model geometry predicts human change.

A later model comparison must remain separate: freeze a model-side predicted lower-level change field independently, then compare whether human longitudinal changes align more strongly with the human field, model field, both, or neither.
