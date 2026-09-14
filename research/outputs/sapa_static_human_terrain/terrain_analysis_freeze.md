# SAPA Static Human Terrain — Terrain Analysis Freeze

Status: frozen after scoring-method selection and before any terrain/density/topology result is computed or inspected.

## Primary respondent representation

Use the IPIP100 Big Five domains scored under the frozen missingness-recovery procedure. Primary scoring method is selected solely from held-out item-recovery diagnostics. No model-side geometry, persona labels, cluster assignments, or human/model correspondence results enter scoring or terrain construction.

Primary respondent cohort requires at least two scored IPIP100 items in each of the five domains. Sensitivity cohorts require at least one and at least three items in every domain.

After respondent scoring, each domain is standardized to zero mean and unit SD within the primary cohort. Euclidean distance in this standardized five-dimensional space is the primary metric.

## Density

Primary local occupancy estimator: k-nearest-neighbor density proxy using k=60. For respondent i in D=5 dimensions, relative log density is `-D * log(r_k)`, where `r_k` is the Euclidean distance to the kth other respondent. Additive constants are irrelevant because only relative density/ranks are interpreted.

Sensitivity k values: 30 and 120.

Density is occupancy only. It is not probability of behavioral transition, stability, utility, or causal attraction.

## Superlevel connectivity

Construct a symmetric k-nearest-neighbor graph with k=30 on the standardized five-dimensional coordinates. Sensitivity graph k values are 20 and 60.

At retained-density fractions 10%, 20%, ..., 90%, keep the respondents with the highest estimated density and induce the graph on those respondents.

For every threshold record:

- number of connected components;
- number of material components;
- largest-component fraction;
- component sizes;
- component centroids in Big Five coordinates.

A material component contains at least max(50 respondents, 1% of the full primary cohort). This threshold is fixed before inspection.

## Multiscale branch persistence

A candidate occupancy branch is considered descriptively persistent only if a material component remains distinct from the largest component across at least three consecutive retained-density thresholds and can be matched across adjacent thresholds by maximum respondent overlap.

This is a descriptive occupancy branch, not a personality type or attractor.

## Structured nulls

Primary null: Gaussian-copula null preserving each empirical univariate marginal distribution and the five-dimensional rank-correlation structure while removing higher-order/non-copula topology. Generate 50 deterministic null replicates using seed 20260914.

Secondary null: multivariate Gaussian with empirical mean and covariance, 50 deterministic replicates.

For each replicate rerun the identical density and superlevel-connectivity pipeline.

Primary test statistics:

1. Fragmentation score: sum over retained-density fractions 20% through 80% of `max(material_component_count - 1, 0)`.
2. Largest-component deficit: mean over retained-density fractions 20% through 80% of `1 - largest_component_fraction`.
3. Density heterogeneity: IQR of primary k=60 relative log density.

Empirical one-sided p-values use `(1 + null_count >= observed)/(1 + number_of_nulls)` for statistics where larger means more structure/heterogeneity.

No post-result statistic may be promoted to primary significance testing.

## Split-half replication

Deterministically split respondents by RID hash into two halves. Recompute the primary kNN density and connectivity summaries separately in each half using the same fixed rules, with material-component size threshold scaled to max(30, 1% of that half).

Replication is assessed by:

- same qualitative component-count sequence across density thresholds;
- correlation of threshold-wise largest-component fractions;
- nearest-centroid correspondence of material components after standardizing each half in the full-sample coordinate system.

No threshold is retuned to improve replication.

## Measurement-quality sensitivity

Repeat the primary descriptive terrain summary on the broad >=1-item/domain cohort and cleaner >=3-item/domain cohort, using the same scoring rule and density/graph parameters. Treat changes as measurement-resolution sensitivity, not as separate confirmatory discoveries.

The q_55 Extraversion source anomaly is handled only in a prespecified sensitivity analysis that reverse-keys q_55 and adds it as the 20th Extraversion item. The primary result follows the nonzero `IPIP100extra` coefficients in `superKey696.csv` exactly.

## Interpretation boundary

The analysis can establish static population occupancy structure: dense regions, sparse regions, superlevel branches, and bottleneck-like separations under the chosen graph/density representation.

It cannot establish transition ease, paths of least resistance, dynamical basins, attractors, energy barriers, or intervention targets. Those claims require longitudinal or perturbational evidence.
