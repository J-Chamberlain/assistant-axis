# LISS 2020 HiFWB analysis specification (human-only pre-data freeze)

## Boundary and eligibility
No respondent data have been accessed. Join Study 965 and 1105 locally on `nomem_encr` after authorization. Preserve `ss20a001`, form, and timeframe. Missingness, valid-range, minimum-item, and complete-case rules are frozen in `liss_2020_scoring_freeze.json`; no outcome-driven feature or model selection is permitted.

## A. Measurement program
Compare rather than assume: (M0) general factor; (M1) correlated lower-order contents; (M2) proposed HiFWB higher-order structure; (M3) bifactor where identified; (M4) ESEM or approximate cross-loadings where software/sample support it. Report fit, convergence, inadmissible solutions, reliability, factor correlations, and sensitivity to form/timeframe. Do not score unsupported latent levels.

## B. Personality relations
Estimate preregistered associations at characteristic, content, lens, and h levels supported by measurement. Report ordinary standardized Big Five coefficients with multiplicity control and uncertainty. Label established replications, HiFWB regroupings, and new tests using `liss_hifwb_novelty_matrix.csv`.

## C. Affect-overlap sensitivity
Primary reports include all outcomes. Prespecified sensitivities remove Affect outcomes and separately examine Extraversion–positive-affect and Emotional-Stability–negative-affect relations. This tests whether broader results survive conceptual overlap.

## D. Multivariate personality comparison
P0: ordinary five simultaneous linear Big Five coefficients. P1: a one-dimensional personality gradient derived from predictor covariance only, within training folds. P2: standardized five-dimensional Ridge. P3: a validated nonlinear model (RBF kernel Ridge) only as a sensitivity. Nested cross-validation must keep preprocessing and P1 derivation inside training folds. Primary question: does full multivariate personality position add held-out information beyond ordinary coefficients or a dominant one-dimensional gradient? Wellbeing outcomes never define personality geometry.

## Outputs and interpretation
Tracked outputs contain aggregate fit indices, coefficients, fold metrics, uncertainty, sample counts, hashes, software versions, and seeds only. Prediction is descriptive and does not establish causality, modifiability, or individualized benefit.
