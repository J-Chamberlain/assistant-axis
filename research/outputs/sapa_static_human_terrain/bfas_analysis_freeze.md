# SAPA Static Human Terrain — BFAS Aspect Analysis Freeze

Status: frozen before inspecting BFAS terrain, peak, saddle, or corridor results.

## Purpose

Increase psychological resolution from the five broad IPIP100 Big Five domains to the ten established Big Five Aspect Scales (BFAS): Compassion, Politeness, Industriousness, Orderliness, Assertiveness, Enthusiasm, Intellect, Openness, Volatility, and Withdrawal. The objective is to test whether the single broad Big Five occupancy mound resolves into reproducible substructure at aspect level without changing the terrain logic after seeing the result.

## Source and item definitions

Use the same canonical SAPA V5 respondent table and the official BFAS scoring keys in `superKey696.csv`. Each aspect contains 10 nonzero-key items. Reverse scoring is determined mechanically by key sign on the 1–6 response scale.

## Scoring method

Compare the same three missingness-compatible scoring rules used in Stage 1: raw keyed mean, item-centered residual mean, and item-standardized residual mean. Use deterministic five-fold respondent cross-validation and leave-one-observed-item-out prediction within each aspect. Select the method by average performance rank across RMSE, MAE, and Pearson correlation over all ten aspects, with RMSE first, then MAE, then correlation. Terrain output is unavailable during scoring selection.

Characterize recovery by subsampling k=1..5 answered items among respondents with at least six observed items in an aspect and comparing with that respondent's all-observed aspect score.

## Cohorts

Because planned missingness becomes much more severe in ten dimensions, cohort definitions are frozen before terrain inspection:

- primary exploratory cohort: at least 1 scored item in every BFAS aspect;
- cleaner sensitivity cohort: at least 2 scored items in every BFAS aspect.

The primary cohort is allowed only if N>=2,500; the cleaner sensitivity is allowed if N>=500. If these gates fail, no BFAS topology claim is made. One-item aspect scores are acknowledged as noisy and primary findings must survive directionally in the cleaner cohort to be called robust.

## Coordinate preparation

After respondent scoring, standardize each of the ten aspect coordinates within the relevant cohort. No Gaussian latent prior, multivariate-normal imputation, factor-score prior, or model-side information is permitted.

## Terrain analysis

Primary exploratory density estimator: 30-nearest-neighbor relative log density in standardized 10D aspect space. Primary graph: symmetric 20-nearest-neighbor graph. These smaller neighborhood sizes are fixed in advance because the BFAS cohort is materially smaller and the dimension is doubled relative to the 5D analysis.

Run superlevel-set connectivity over retained-density fractions 10%, 20%, ..., 90%. Then apply the same descending-density component-tree peak/saddle procedure used in the frozen Big Five corridor follow-up.

A finite BFAS peak is material if its pre-merge basin support is at least 1% of the analyzed cohort. Retain all material finite peaks, capped at eight by density prominence, plus the root/global peak. Do not label them personality types.

For every retained peak pair, compute the maximum-support corridor using the maximin graph path. Report saddle density percentile, lower-peak-to-saddle barrier, endpoint and saddle aspect profiles, graph path length, and Euclidean arc length.

## Robustness

Repeat the complete peak/saddle analysis in the cleaner >=2-items-per-aspect cohort. Primary peaks are considered coverage-robust only when a cleaner-cohort peak occurs within Euclidean distance 1.0 in standardized ten-aspect profile space after nearest-profile matching and has the same qualitative sign pattern on at least 8 of 10 aspects.

Also repeat primary-cohort terrain with density k=20 and 60 and graph k=15 and 30. Do not retune peak thresholds.

## Interpretation boundary

This is static cross-sectional occupancy. Peaks, saddles and corridors are not dynamical attractors, transition probabilities, causal sequences, or paths of least resistance. Demographic representativeness robustness remains deferred until after the structural terrain analyses, per user instruction.
