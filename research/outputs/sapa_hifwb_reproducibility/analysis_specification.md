# SAPA × HiFWB reproducibility and wellbeing-surface specification

Status: PRE-RESULT FREEZE (2026-09-15)

This human-only analysis reconstructs the preserved exploratory SAPA V5 × HiFWB result and prospectively freezes robustness and surface-vs-backbone tests. The historical result remains exploratory/post hoc; this freeze does not retroactively make it confirmatory.

## Reconstructed historical procedure

- Source: SAPA V5, DOI 10.7910/DVN/SD7SVE; raw respondent data remain local and gitignored.
- Big Five: frozen IPIP100 domains A, C, E, ES, O, 20 source items per domain; score directions are read from `superKey696.csv`. The official nonzero key is used, so Extraversion has 19 nonzero-keyed items (q_55 is recorded as a sensitivity anomaly).
- Direct wellbeing inventory: the exact 13 item IDs in `wellbeing_item_freeze.csv`; each item is oriented so larger values indicate wellbeing. Historical score is the respondent's mean of available item-standardized values, requiring at least two observed direct items.
- Historical non-affect score removes q_1043, q_208, q_206, q_1578, and q_832 from the direct set and retains the same two-item rule.
- Five-fold prediction uses deterministic `random_state=20260915`; the original chat fold assignment is UNKNOWN.

## Newly frozen robustness procedure

- Content-balanced core: within-content mean of observed positively oriented standardized items, then equal-weight observed content means; primary eligibility requires ≥2 observed core contents, secondary ≥3. Vitality is excluded from the primary score and included only in the labeled six-group sensitivity.
- Leave-one-content-out: repeat the primary content-balanced score after dropping each core content.
- Fold-safe loading sensitivity: training-fold item moments and one-component PCA loadings, oriented positive, score held-out rows from observed items only. This is called a fold-safe PC1-loading-weighted score, not a validated latent HiFWB scale.
- Surface models use out-of-fold predictions only: M0 intercept, M1 frozen-backbone cubic polynomial, M2 Ridge with alpha selected within training folds over {0.1,1,10,100}, and M3 RBF Kernel Ridge over frozen alpha/gamma grids. Primary contrasts are M1–M2, M1–M3, M2–M3. Bootstrap uncertainty uses deterministic respondent-level resampling of paired OOF errors.

No respondent-level data, IDs, coordinates, scores, or OOF predictions are committed. No model geometry, projection, inference, or external model API is used.
