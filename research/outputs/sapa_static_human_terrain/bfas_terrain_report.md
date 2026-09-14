# SAPA Static Human Terrain — BFAS Aspect Follow-up

## Bottom line

The ten-dimensional BFAS follow-up does not reveal multiple material occupancy basins under the frozen procedure. The primary exploratory cohort contains 3,082 respondents with at least one scored item in every BFAS aspect. Under the frozen 30-nearest-neighbor density and symmetric 20-nearest-neighbor graph, the terrain remains a single connected high-density body at every retained-density threshold from 10% through 90%.

The descending-density component tree contains one global/root peak plus only two finite local bumps. Their pre-merge basin supports are 4 respondents and 1 respondent, both far below the frozen 1% material-support floor of 31 respondents. Therefore no BFAS peak pair qualifies for saddle/corridor interpretation.

## Scoring validation

The same three missingness-compatible scoring rules used in Stage 1 were compared before terrain inspection: raw keyed means, item-centered residual means, and item-standardized residual means.

Across the ten BFAS aspects, item-standardized residual scoring ranked first on mean RMSE rank (1.0), mean MAE rank (1.2), and mean held-out correlation rank (1.0). Item-centered scoring ranked second and raw keyed means third. The BFAS terrain therefore uses the same observed-only item-standardized scoring family as the Big Five analysis; unanswered items are not deterministically filled.

Masked-recovery diagnostics show the expected resolution/noise tradeoff. With one observed item per aspect, recovery correlations against fuller observed-aspect scores range from roughly 0.60 to 0.78, with median about 0.72. With two items they range from roughly 0.75 to 0.90, median about 0.84. With three items they range from roughly 0.86 to 0.93, median about 0.91.

## Cohorts

Primary exploratory cohort: at least one scored item in all ten aspects, N=3,082.

Cleaner sensitivity cohort: at least two scored items in all ten aspects, N=725.

Both prespecified minimum-N gates are satisfied. The primary cohort remains noisy at the aspect level, so a structural feature would need directional support in the cleaner cohort to be treated as robust.

## Primary BFAS topology

At every retained-density fraction from 10% through 90%, the induced high-density respondent graph has exactly one connected component containing 100% of retained nodes.

The primary component-tree analysis finds only two finite local bumps before they merge into the root basin. Their basin supports are 4 and 1 respondents. Neither reaches the 1% material-support threshold of 31 respondents.

Accordingly, the frozen maximum-support corridor stage is not entered. There is no pair of material BFAS peaks between which a defensible saddle corridor can be defined.

## Robustness

No material finite peak appears under any frozen neighborhood sensitivity:

- density k=20, graph k=20: 3 finite peaks, 0 material, largest finite basin 6 respondents;
- density k=30, graph k=15: 4 finite peaks, 0 material, largest finite basin 4 respondents;
- density k=30, graph k=20: 2 finite peaks, 0 material, largest finite basin 4 respondents;
- density k=30, graph k=30: 2 finite peaks, 0 material, largest finite basin 4 respondents;
- density k=60, graph k=20: 2 finite peaks, 0 material, largest finite basin 1 respondent.

The cleaner >=2-items-per-aspect cohort also contains no material finite peak under the primary BFAS neighborhood settings. It produces three finite bumps, with largest basin support 4 respondents versus an 8-respondent 1% threshold.

## Interpretation

### Observed

Increasing representation from five broad Big Five domains to ten BFAS aspects does not resolve the SAPA occupancy distribution into multiple material high-density basins under the frozen graph-density procedure. The dense core remains continuously connected and essentially unimodal at this scale.

### Interpretation

The absence of material peaks in both 5D Big Five and 10D BFAS space suggests that the population structure captured by these conventional trait coordinates is better described as a continuous, anisotropic distribution than as a small set of separated hills connected by passes.

This does not mean the terrain is homogeneous. The earlier Big Five analysis already established excess local-density heterogeneity relative to a Gaussian-copula null. What the present result rules against is a specific stronger picture: several population-scale trait basins with identifiable saddle corridors between them.

### Consequence

The next structural analysis should shift from `mode-to-mode corridors` to continuous density-ridge geometry: identify directions and curved high-support manifolds within the single occupancy body, characterize how rapidly support falls away from those ridges, and test whether those ridge structures replicate under demographic stratification/reweighting. This better matches the observed terrain than forcing discrete peaks where the data do not support them.

## Deferred demographic robustness

Per user instruction, demographic robustness remains queued immediately after the structural terrain pass. It should test age, sex, student status, and country/region composition without changing the frozen scoring or structural definitions.
