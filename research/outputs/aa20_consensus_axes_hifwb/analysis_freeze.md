# AA-20 analysis freeze

Frozen 2026-09-17 after verifying the AA-19 artifact hashes/classes, AA-16 frozen 13-item HiFWB definition, AA-19 future-safe bridge and item orientations, external SAPA raw/key fingerprints, and zero predictor--outcome item overlap. This document precedes every C1--C3/HiFWB association estimate.

## Scope and fixed predictors

Primary predictors are C1--C3 only. C4/C5 are excluded because AA-19 classed them D (presently untestable). All predictor trait proxies use the 41 AA-19 future-safe, unique-source direct representatives; repeated human-source aliases are not repeated. Each trait proxy is a mean of its frozen oriented SAPA items. Item directions follow AA-19/AA-1; source responses on the released 1--6 scale are transformed to `7-x` where orientation is negative.

Let `L` be AA-19's frozen 41-by-5 oblimin pattern-loading matrix and `Q` its orthonormal column span. Let `v_c` be the AA-18 signed consensus loading restricted to these 41 traits. The fixed human representations are the normalized score weights `Q Q' v_c` for C1 and C2. C3 primary uses the sign-aligned AA-19 H2 pattern loading, because its primary five-factor single-axis Tucker congruence was 0.744; the fixed C3 subspace weight `Q Q' v_3` is a sensitivity. These weights are constructed from frozen AA-18/AA-19 artifacts only and will never be fit, rotated, signed, selected, or tuned using HiFWB.

## Eligibility and scoring

For the common primary sample a respondent must: (1) have at least two of 13 frozen, oriented HiFWB items; (2) have at least eight observed AA-19 proxy traits; (3) have at least two observed traits on each signed pole and at least 15% absolute loading coverage for each of C1--C3; and (4) have at least two observed nonoverlapping IPIP100 items for each of Agreeableness, Conscientiousness, Extraversion, Intellect/Openness, and Emotional Stability. The outcome is the frozen AA-16 mean of globally standardized oriented items; its 8,664-person eligibility count must reproduce before applying the common predictor rule.

Because the required model comparison includes the five broader AA-19 human-factor scores on the same respondents, the common sample additionally requires all five fixed pattern-weighted factor scores to meet their 15% absolute-weight coverage rule. This criterion is outcome-blind and prevents factor-score imputation.

Predictor item means/scales and predictor-score standardization are fit on the training respondents only. Missing trait components use the observed absolute-weight renormalized mean after the fixed coverage rule; no response, trait, factor, or outcome value is imputed. Big Five domain means use their official frozen keys, with reverse items oriented before standardization. Every outcome model uses the same eligible respondents within its split.

## Validation and model decisions

The AA-13 deterministic raw-respondent split is reused: seed 20260915, 60% train, 20% validation, 20% test before eligibility filtering. Ridge penalty is selected only on validation from {0, 0.01, 0.1, 1, 10, 100}; the final model refits on train+validation, with preprocessing refit there, and is evaluated once on the untouched test subset. The primary incremental comparison is Big Five + C1--C3 versus Big Five. Report held-out R2, RMSE, MAE, calibration intercept/slope, paired 1,000-test-resample intervals, and 1,000 outcome-label test permutations. A low-complexity quadratic ridge model is a predeclared nonlinear sensitivity only.

Compare intercept, Big Five, C1--C3, Big Five+C1--C3, five AA-19 factors, and Big Five+five factors. The factor comparison uses the frozen five-factor loadings; it is descriptive of broader human structure, not a selection device.

## Association and robustness procedures

Composite associations are standardized OLS coefficients and zero-order Pearson correlations on the common eligible sample, with 1,000 respondent bootstraps, VIFs, and five repeated deterministic split sets. Indicator analyses use the same fixed scores and each indicator's observed respondents; Benjamini--Hochberg FDR at q=.05 corrects the 39 axis-by-indicator zero-order tests. Predeclared sensitivities are: direct-plus-close mappings; source-group duplicate handling; C3 primary factor versus frozen subspace; five versus six human factors; a leave-one-trait-out dominant-weight check; separate removal of optimistic and pessimistic predictor traits; and the quadratic model. The outcome has no role in choosing a primary representation.

## Decision rules

Headline A requires an incremental test-R2 bootstrap 95% interval strictly above zero and a one-sided permutation p<=.05, without sign reversal under core scoring sensitivities. B requires a stable held-out association but no reliable Big Five increment. C applies when the association materially depends on outcome indicator, factor count, bridge, or scoring specification. D applies when no stable held-out association is found. E applies if reconstruction, overlap, or eligibility gates fail. Later model-persona projection passes only for an AA-19 supported representation with stable held-out association, robust sign, zero item leakage, and no sensitivity reversal. AA-20 will not perform that projection.

No model inference, RunPod, paid compute, activation work, persona scoring, or viewer modification is in scope.
