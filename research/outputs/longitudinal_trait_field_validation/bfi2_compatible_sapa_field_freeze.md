# BFI-2-Compatible SAPA Facet Field — Pre-Outcome Freeze

Status: frozen before fitting any facet-field result and before opening participant-level PEACH longitudinal outcome data.

## Purpose

Construct a human-only lower-level trait field over Big Five space that is directly compatible with the 15 BFI-2 facets measured longitudinally in the PEACH intervention. This field is a separate validation instrument from the previously completed 12-trait human/model bridge field. It does not replace or retune that bridge.

## Predictor coordinates

Use the same five human Big Five coordinates already established from the official SAPA IPIP100 scoring keys: Agreeableness, Conscientiousness, Extraversion, Emotional Stability, and Openness/Intellect. Use the already selected observed-only item-standardized scoring family and require at least two observed scored IPIP100 items per domain.

To prevent direct item leakage, every BFI-2-compatible facet target is built only from SAPA items that are not used by any of the five IPIP100 predictor keys. The common predictor coordinates therefore remain unchanged across facet targets.

## Facet targets and frozen source-scale families

The facet labels come from the published BFI-2 hierarchy. SAPA proxy construction uses established public-domain source scales already present in the canonical SAPA scoring dictionary. No PEACH outcome value or model-side evidence enters the mapping.

Sociability uses `SPI_15sociability`, `HXSociable`, and `NEOe2`.

Assertiveness uses `BFASassert`, `HXSocBold`, and `NEOe3`.

Energy Level uses `BFASenthus`, `HXLiveliness`, and `NEOe4`.

Compassion uses `BFAScomp`, `SPI_15compassion`, `NEOa3`, and `HAGentle`.

Respectfulness uses `BFASpolite`, `NEOa4`, and `HHFairness`.

Trust uses `SPI_15trust` and `NEOa1`.

Organization uses `BFASorder`, `HCOrgan`, and `NEOc2`.

Productiveness uses `BFASindustry`, `SPI_15industry`, `NEOc4`, and `NEOc5`.

Responsibility uses `NEOc3`, `HCDiligence`, and `MPQco`.

Anxiety uses `HEAnxiety`, `NEOn1`, and `BFASwithdraw`.

Depression uses `NEOn3`, `MPQwb`, and `BFASwithdraw`. The MPQ well-being contribution is reverse-oriented by its released scoring direction when combined with depression-oriented sources.

Emotional Volatility uses `BFASvolatile`, `SPI_15volatility`, and `NEOn2`.

Intellectual Curiosity uses `BFASintel`, `SPI_15intellect`, `NEOo5`, and `HOInquisite`.

Aesthetic Sensitivity uses `HOAesthetic`, `NEOo2`, and `BFASopen`.

Creative Imagination uses `HOCreative`, `NEOo1`, and `SPI_15openness`.

## Item construction rule

For each facet, take the union of nonzero-scored SAPA items from the frozen source-scale family, then remove every item that appears in any official IPIP100 Big Five predictor key. For each remaining item, orient its sign toward the named BFI-2 facet using the released source-scale directions. When an item appears in multiple frozen source scales with the same orientation, include it once. If source scales imply conflicting orientation for the same item, exclude that item rather than adjudicating after outcome inspection.

Standardize each retained item using its observed SAPA mean and SD, apply the frozen orientation, and compute an observed-only respondent facet score as the mean of available oriented standardized items. No unanswered item is imputed.

A facet is eligible for the primary field only if at least six non-overlapping target items survive and at least 1,000 respondents have at least one observed target item. A cleaner sensitivity cohort for that facet requires at least two observed target items.

## Field model

For each eligible facet, compare linear Ridge on the five Big Five coordinates with the same frozen nonlinear RBF-Nystroem plus Ridge family used in the prior 12-trait field. Use deterministic five-fold respondent cross-validation. The nonlinear field replaces the linear field only if held-out RMSE improves by at least 1 percent.

A facet passes the field-quality gate if held-out Pearson correlation is at least 0.20 and held-out R2 is positive. The fitted Jacobian row is taken from the selected full-sample model only after cross-validated model-family selection.

## Robustness

Repeat the selected model independently in the deterministic split halves. A facet direction is recurring if the split-half gradient cosine is at least 0.75. Repeat on the cleaner target-item cohort and report gradient cosine relative to the primary fit.

Add raw response mean and within-person response SD as nuisance covariates in a sensitivity fit. The five-dimensional facet-gradient component is considered response-style robust if its cosine with the primary gradient is at least 0.85.

## Longitudinal handoff rule

Freeze the final retained facet set, Jacobian matrix, scoring metadata, and validation metrics before participant-level PEACH outcomes are opened. The longitudinal preregistration may not drop a facet because it performs poorly in PEACH or add a facet because it performs well.

The later PEACH analysis will standardize BFI-2 domain and facet scores using the PEACH baseline distribution, compute observed within-person change, and test directional alignment against this frozen SAPA-derived field. Cross-instrument magnitude agreement is secondary; direction, rank, and sign are primary.

## Interpretation boundary

This construction tests whether an independently estimated human cross-sectional relation between broad and narrow personality dimensions predicts actual longitudinal change in a different sample and instrument family. It does not establish that the SAPA proxies are identical to BFI-2 facets, that the intervention moves people along a causal field, or that model geometry predicts human change.
