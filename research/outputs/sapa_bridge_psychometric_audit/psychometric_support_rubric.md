# SAPA Bridge Human-Data Psychometric Support Rubric

Status: frozen before inspecting human-response covariance results
Rubric version: 1.0
Frozen UTC: 2026-09-11T23:07:00Z
Analysis model: GPT-5.5

## Scope and blindness

This rubric evaluates only the empirical structure of the retained SAPA item proxies in human SAPA responses. It is a psychometric coherence diagnostic, not absolute validation and not independent expert review.

Permitted inputs are the frozen SAPA bridge tier, exact item wording, official SAPA item and scoring-key metadata, respondent item responses, planned-administration overlap, item/scale reuse, and statistics derived exclusively from those human data.

The analysis must not load persona names, model coordinates, PC values, activation vectors, trait-vector cosines, predictor outputs, occupation outcomes, or any downstream model-geometry result. No support label may be optimized against model geometry.

The 45 `ACCEPT_DIRECT` links are the primary analysis. The 29 `ACCEPT_CLOSE` links enter only a separately reported direct-plus-close sensitivity analysis.

## Item orientation

- Each trait-item pair receives an explicit orientation sign before correlation analysis: `+1` retains the released 1–6 response; `-1` applies `7 - response`.
- The sign follows the frozen bridge wording and second-pass direction note. Official `superKey696.csv` keys are retained separately as source-scale scoring evidence; a scale's key does not override the direction required for the named proxy.
- Shared items may legitimately receive opposite signs for opposite constructs, such as dominant versus submissive or spiritual versus secular.
- Any orientation that cannot be resolved from the exact wording is marked ambiguous and excluded rather than inferred.

## Correlations and planned missingness

- Primary item associations are pairwise-complete Pearson correlations on oriented 1–6 responses, matching the SAPA release's documented structural-analysis practice.
- Every item-pair estimate retains its pairwise `N` and Fisher approximation `SE(r) = (1-r^2)/sqrt(N-3)` when `N > 3`.
- Pairwise-complete Spearman correlations are the ordinal/rank sensitivity analysis.
- Polychoric correlation is optional. Its absence does not block the audit when no reliable local implementation is available; the report must disclose the omission and the release paper's own Pearson/polychoric comparison.
- No complete-case filter and no respondent- or item-mean imputation is permitted.

## Proxy construction

Trait-proxy correlations are correlations of standardized unit-weighted composites reconstructed from the pairwise item correlation matrix:

`r(X,Y) = sum(Rxy) / sqrt(sum(Rxx) * sum(Ryy))`.

This uses all pairwise administrations without fabricating complete respondent profiles. Pairwise effective `N` is the harmonic mean of the contributing item-pair counts; minimum and range remain available in the long item-pair table. Shared-item sensitivity removes shared items from both proxies and recomputes only when both retain evidence.

## Internal coherence

Internal reliability is not estimated for single-item proxies.

For multi-item proxies:

- strong coherence: mean oriented inter-item Pearson `r >= 0.30`, median `r > 0`, and no pair below `-0.10`;
- moderate coherence: mean `r >= 0.15`, median `r > 0`, and no pair below `-0.10`;
- weak coherence: mean `0.00 <= r < 0.15` or any pair below `-0.10`;
- contradictory coherence: mean or median `r < 0`.

Standardized Cronbach alpha is reported from the pairwise correlation matrix. Alpha is descriptive because pairwise sample membership varies. Omega is not used: with only two or three evidence items per proxy, a one-factor omega is underidentified or saturated and would add false precision.

## Source-scale convergence

Official source scales are reconstructed from `superKey696.csv`. Associations exclude the proxy's own evidence items from the scale composite to remove part-whole overlap. Absolute association is used for convergence rank because some named proxies are the inverse of an official scale direction; signed associations remain reported.

- strong convergence: best intended-scale `|r| >= 0.30` and rank is within the top 25% of evaluable official scoring keys;
- moderate convergence: best intended-scale `|r| >= 0.20` and rank is within the top 50%;
- weak convergence: an intended scale is evaluable but neither threshold is met;
- insufficient: no intended scale can be mapped to an official scoring key or corrected composite.

The strongest non-intended scale, intended rank, and signed margin over the strongest alternative remain visible. A negative margin is not an automatic rejection because nearby scales can validly correlate, but it weakens discriminant evidence.

## Discriminant-support status

The audit assigns one transparent structural status before the overall support tier:

- `STRONG STRUCTURAL SUPPORT`: strong source convergence; and, for multi-item proxies, strong or moderate internal coherence; nearest other-proxy `|r| < 0.80`; no direction ambiguity.
- `MODERATE STRUCTURAL SUPPORT`: at least moderate source convergence; and, for multi-item proxies, coherence is not contradictory; nearest other-proxy `|r| < 0.90`; no direction ambiguity.
- `WEAK / REDUNDANT`: evaluable evidence that fails the moderate rule, has contradictory coherence, has nearest other-proxy `|r| >= 0.90`, or loses at least 0.20 absolute correlation when shared items are removed.
- `INSUFFICIENT EVIDENCE`: unresolved direction, no evaluable intended scale, or contributing item-pair effective `N < 200`.

These labels summarize; raw correlations, ranks, reuse, and sample sizes control interpretation.

## Provisional human-measurement support tier

- `HIGH HUMAN-MEASUREMENT SUPPORT`: `ACCEPT_DIRECT`, at least two items, strong structural support, mean inter-item `r >= 0.25`, standardized alpha `>= 0.50`, intended `|r| >= 0.30`, pairwise effective `N >= 300`, and no unresolved reuse failure.
- `MODERATE SUPPORT`: strong or moderate structural support but not every high-tier condition; includes well-converging single-item direct proxies that cannot establish internal reliability.
- `LIMITED / SINGLE-ITEM`: single-item evidence without strong convergence, or multi-item evidence with weak internal coherence but no direct contradiction.
- `REDUNDANT / BROAD`: weak/redundant structural status driven by near-duplicate proxy structure, scale relabeling, or a shared-item effect of at least 0.20.
- `INSUFFICIENT`: insufficient structural status, direction ambiguity, or contradictory internal covariance.

`ACCEPT_CLOSE` rows cannot receive the high tier. At best they receive `MODERATE SUPPORT`, and their counts are always reported separately.

## Reuse interpretation

- exact alias: two proxies have the same oriented item set;
- shared-item sensitive: removing shared items changes `|r|` by at least 0.20;
- same-scale / high redundancy: no shared item is required and `|r| >= 0.70` among proxies sharing a source scale;
- neighboring construct: shared scale and `0.35 <= |r| < 0.70`;
- differentiated despite shared scale: shared scale and `|r| < 0.35`.

## Effective dimensionality

- Pairwise Pearson and Spearman matrices are analyzed separately for the direct tier and direct-plus-close sensitivity tier.
- Because pairwise correlation matrices can be slightly indefinite, eigenvalue clipping followed by diagonal renormalization supplies a documented positive-semidefinite analysis matrix; the minimum raw eigenvalue and maximum adjustment are reported.
- Participation-ratio effective rank and entropy effective rank are descriptive.
- A fixed-seed Horn parallel-analysis reference uses 500 independent Gaussian correlation matrices at the median proxy-pair effective `N`; it is explicitly approximate because effective `N` varies by pair.
- Average-linkage hierarchical clustering uses distance `sqrt(max(0, (1-r)/2))`. The cluster count is selected by maximum precomputed-distance silhouette over `k=2..min(12,p-1)`, with ties resolved toward smaller `k`.

## Decision boundary

Human-data structural support cannot establish model-trait equivalence or human/model correspondence. Independent external semantic review remains required even if covariance diagnostics are favorable. No human-to-model projection is authorized by this rubric.
