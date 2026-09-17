# AA-17 analysis freeze

Frozen before fitting factors, 2026-09-17. Input is the three saved 275 × 240 signed role–trait cosine matrices. Rows are matched persona observations; columns are the identical ordered trait vocabulary. No HiFWB value, PCA score, human response, or SAPA variable enters fitting, rotation, retention, or labels.

## Phase gate and exclusions

Require 275 unique identical persona names and 240 unique identical trait names in identical order, finite numeric scores, and documented mean-pooled role/trait cosine construction. A column with sample SD below `1e-6` is degenerate and excluded. Exact duplicates are identified by equality at `1e-12`; near duplicates by absolute Pearson correlation at least `0.995`. The full analysis retains all nondegenerate columns. In the redundancy sensitivity, connected components under that near-duplicate threshold are represented by their first column in canonical order. Every omitted member remains in the inventory and is mapped back by association with frozen factor scores. Sign is never flipped during preprocessing.

## Estimation and retention

Within each model, center and standardize each trait across personas. The primary correlation is Ledoit–Wolf shrinkage of the standardized matrix, then rescaled to unit diagonal. The estimator shrinks toward a spherical covariance target and assumes personas are exchangeable for covariance estimation. The ordinary Pearson correlation is a sensitivity input. Fit iterative principal-axis common factors (squared-multiple-correlation initialization, 20 communality updates or tolerance `1e-7`) with oblimin rotation; varimax is an orthogonal sensitivity. Report unrotated and rotated pattern/structure loadings, factor correlations, communalities, uniquenesses, regression factor-score coefficients, and off-diagonal residual RMS. The model correlation is `L Phi L.T + diag(uniqueness)`.

Retention diagnostics are fixed before factor interpretation: 100 columnwise independent marginal permutations for Horn's 95th-percentile parallel analysis; Velicer MAP on the ordinary correlation up to 15 components; raw and shrinkage scree; Gaussian heldout log likelihood under 3 deterministic persona folds; and stability. Parallel analysis is the provisional count, with candidates from max(2, count−2) through min(10, count+3). Disagreement is reported, and no count is chosen by Big Five correspondence or label appeal. Eigenvalue > 1 is descriptive only.

## Stability and matching

Use seed 17017, 20 persona bootstraps and 10 repeated random split halves per model at the frozen count. Match axes by maximum absolute Tucker congruence (Hungarian permutation), correct sign, and compare factor-space canonical correlations. Also report aligned loading congruence, per-trait bootstrap loading SD and 5th/95th percentile interval, primary assignment and cross-loading stability. Individual factor stability requires bootstrap median congruence at least 0.90 and tenth percentile at least 0.75, plus split-half median congruence at least 0.80. Otherwise report a stable subspace only if the lowest retained-subspace canonical correlation median is at least 0.80.

Across models, match columns by absolute loading congruence, report signed congruence after orientation, loading-vector correlations, principal angles, subspace canonical correlations, and 100 trait-label permutation references. Factor order and sign are arbitrary. Clean loading means absolute primary pattern loading ≥0.40 and every secondary <0.30; cross-loading means primary and secondary both ≥0.30. Weak explanation means communality <0.20. These are descriptive cutoffs, not selection rules. Human bridge coverage is a post-fit label overlap audit only, using the pre-existing 45 direct and 74 direct-plus-close mappings. The five prior editorial groups are also post-fit comparisons only.

No causal trait, human personality, wellbeing, or diagnosis claim follows from this analysis.
