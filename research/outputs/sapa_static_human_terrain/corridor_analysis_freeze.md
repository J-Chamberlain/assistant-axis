# SAPA Static Human Terrain — Peak/Saddle/Corridor Analysis Freeze

Status: frozen before inspecting any peak, saddle, or corridor result.

## Purpose

Refine the completed Stage-1 Big Five connectivity result. The prior analysis asked whether high-density occupancy separates into disconnected material components. This follow-up asks a different question: within the single connected occupancy body, are there reproducible local density maxima joined by lower-density passes, and what Big Five profiles characterize the highest-support connecting tissue between them?

This is a static occupancy analysis. A corridor is a high-support route through cross-sectional respondent density. It is not a transition path, causal route, energy barrier, attractor, or path of least resistance.

## Fixed source and scoring

Reuse without alteration the canonical SAPA V5 respondent table whose SHA256 is `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6` and the already-frozen primary Big Five scoring/cohort decisions in this directory.

Primary coordinates are the five standardized respondent scores for Agreeableness, Conscientiousness, Extraversion, Emotional Stability, and Openness, using the selected item-standardized residual mean and the primary eligibility rule of at least two scored IPIP100 items in every domain. No model-side information enters the analysis.

## Primary density and graph

Use the already-frozen primary density estimator: 60-nearest-neighbor relative log density in standardized 5D Big Five space.

Use the already-frozen symmetric 30-nearest-neighbor respondent graph for topology and path calculations. Distances are Euclidean in the standardized five-dimensional coordinate system.

## Peak and saddle definition

Process respondent nodes from highest to lowest local log density. A new connected component is born when a node appears without an already-active neighbor. When two or more active components first join, the lower-persistence component dies at that node's density. For every component, record:

- peak node and peak density;
- merge/saddle density at death;
- density prominence = peak density minus saddle density;
- basin support = number of component members immediately before its first merge divided by the primary cohort size.

The final surviving component is the global/root basin and has no finite death/saddle; it is retained as the global density maximum but is not assigned an infinite prominence.

## Descriptive mode set

To avoid tuning the number of modes after seeing results, the descriptive table will contain every finite-persistence peak with basin support at least 0.5% of the primary cohort, ranked by density prominence, capped at the top 8. The root/global peak is added separately.

No peak is called a distinct population type solely because it appears in this table.

## Null comparison

Use 100 deterministic Gaussian-copula null replicates preserving the five empirical univariate marginals and the empirical rank-correlation structure, matching the existing Stage-1 null family.

For each null replicate, recompute coordinates, 60-NN density, 30-NN graph, and the same peak/saddle persistence procedure. Record the largest finite prominence among peaks with basin support at least 0.5%.

The primary significance diagnostic for multimodality is whether the largest observed finite prominence exceeds the null distribution. Report the finite empirical one-sided p-value `(1 + null >= observed)/(101)`. This is a test of unusually strong internal peak/saddle structure under the chosen graph-density representation, not a test of psychological types.

## Maximum-support corridors

For each pair among the retained descriptive peaks plus the root peak, define the maximum-support corridor as the graph path that maximizes the minimum node density encountered. Compute it via a maximum-spanning tree whose edge capacity is the minimum density of its two endpoints. The minimum node density along the resulting path is the corridor saddle density.

For each pair report:

- endpoint peak densities;
- maximin saddle density;
- barrier from the lower endpoint peak: `min(endpoint peak densities) - saddle density`;
- normalized saddle support: percentile rank of the saddle density among primary respondents;
- path length in graph nodes and Euclidean arc length;
- Big Five coordinates of both endpoints and the saddle node.

## Which corridors receive interpretation

Interpret the five peak-pair corridors with the largest barrier from the lower endpoint peak, restricted to endpoint peaks in the descriptive mode set. Also report the five strongest corridors by highest saddle-density percentile. These two rankings answer complementary questions: the deepest internal passes and the most heavily supported connecting tissue.

If fewer than two finite-persistence descriptive peaks survive the fixed support rule, report that the 5D terrain does not resolve multiple material local peaks under this procedure and do not manufacture corridors.

## Profile summaries

For each retained peak and saddle, summarize Big Five coordinates using a local neighborhood rather than a single respondent: the focal node plus its 30 nearest neighbors in 5D. Report local mean and median standardized coordinates. No respondent IDs or row-level data are committed.

For an interpreted corridor, report endpoint-neighborhood profiles, saddle-neighborhood profile, and the signed coordinate changes from each endpoint toward the saddle. Language must remain descriptive, e.g. `higher/lower Agreeableness`, not diagnostic labels.

## Robustness

Repeat the peak/saddle extraction for density k = 30 and 120 while keeping graph k = 30, and for graph k = 20 and 60 while keeping density k = 60. A peak is considered sensitivity-recurring if a peak in the alternate run lies within Euclidean distance 0.75 standardized units of the primary peak.

Run the primary procedure independently on the same deterministic split halves used by the Stage-1 analysis. A full-sample peak is split-recurring if each half contains a peak within 0.75 standardized units. Report recurrence but do not retune thresholds based on it.

## Deferred demographic robustness

Per user instruction, demographic reweighting/stratification is required after the structural terrain analyses. It is deliberately not used to define or tune the present peaks or corridors. The later robustness pass should test age, sex, student status, and country/region composition where sample support permits.

## Interpretation boundary

Observed peak/saddle structure may support statements about cross-sectional occupancy geometry. It cannot establish dynamical attractors, transition probabilities, causal sequencing, intervention leverage, or representative population prevalence. SAPA is a large convenience sample rather than a probability sample.
