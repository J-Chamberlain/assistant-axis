# SAPA Static Human Terrain — Initial Big Five Occupancy Analysis

## Bottom line

Using the frozen IPIP100 Big Five representation and a scoring procedure selected before terrain inspection, the human sample forms one connected high-density occupancy region across the preregistered superlevel thresholds. The first-pass five-dimensional analysis therefore does **not** show evidence for multiple disconnected material lobes or a literal coarse-grained “Swiss-cheese” topology at this resolution.

At the same time, local density is more heterogeneous than expected under a Gaussian-copula null that preserves each empirical marginal distribution and the five-dimensional rank-correlation structure. This excess density heterogeneity is stable across kNN density scales and remains present in both noisier and cleaner item-coverage cohorts. The result is therefore compatible with nontrivial higher-order occupancy structure inside a single connected region, but it does not yet establish holes, corridors, bottlenecks, attractors, or transition paths.

## Provenance and source verification

The uploaded Dataverse archive contains the expected SAPA V5 files. The primary respondent table `sapaTempData696items08dec2013thru26jul2014.tab` is 23,975,309 bytes and has SHA256 `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`, exactly matching the previously recorded canonical project manifest. The loaded table contains 23,679 respondents and 719 columns.

Raw respondent-level data are not committed to GitHub. Only aggregate diagnostics and methods are saved here.

## Scoring selection

The scoring choice was frozen before terrain results were computed. Three missingness-compatible rules were compared by deterministic five-fold respondent cross-validation. Within each held-out fold, each observed Big Five item was left out in turn and predicted from the respondent's remaining observed items in that domain. Item means and SDs were estimated only from the training respondents.

The item-standardized residual mean (`zscaled`) won the frozen selection rule. Across the five domains it had mean method rank 1.067, versus 1.933 for item-centered scoring and 3.000 for raw keyed means. It had the best MAE and held-out correlation in all five domains and the best RMSE in four of five; Agreeableness RMSE was essentially tied with the centered method (1.24744 versus 1.24714).

The method does not fill unanswered items. It averages standardized residual evidence from the items actually answered. No Gaussian latent prior or model-side information is used.

## Missingness recovery

Masked-recovery diagnostics support the preregistered choice of at least two scored items per domain for the primary terrain cohort, while also showing substantial remaining measurement noise.

With two observed items, correlation with the same respondent's fuller observed-domain score ranges from 0.783 for Openness to 0.856 for Extraversion. With three items the range is 0.865 to 0.913. With five items it is 0.951 to 0.971. One-item recovery is materially weaker, ranging from 0.646 to 0.735.

These are item-sampling recovery diagnostics, not proof that the fuller observed score is error-free.

## Cohorts

The frozen primary cohort requires at least two scored IPIP100 items in every Big Five domain and contains 8,585 respondents.

The broad sensitivity cohort, requiring at least one item per domain, contains 19,046 respondents. The cleaner sensitivity cohort, requiring at least three items per domain, contains 2,361 respondents.

## Primary terrain result

The primary density estimator is 60-nearest-neighbor relative log density in standardized five-dimensional Big Five space. Connectivity is evaluated on a symmetric 30-nearest-neighbor graph.

At every preregistered retained-density fraction from 10% through 90%, the induced high-density graph contains exactly one connected component and one material component. The largest-component fraction is 1.000 at every threshold. The frozen fragmentation score is therefore 0 and the largest-component deficit is 0.

This remains true under the principal graph/density sensitivities. Across k-density values 30, 60, and 120 and graph k values 20, 30, and 60, no material secondary component appears. The only non-primary irregularity is a single tiny nonmaterial split under k-density 30 / graph-k 20, yielding a largest-component deficit of only 0.000277 and still one material component.

The same one-component result appears in both deterministic split halves and in the broad and cleaner item-coverage cohorts.

The preregistered multiscale branch criterion is therefore not met. No distinct material occupancy branch is declared.

## Density heterogeneity versus structured nulls

Although the terrain is connected, its local density distribution is not fully captured by simple null structure.

For the primary k=60 density estimator, the observed IQR of relative log density is 1.772. Under 50 Gaussian-copula null replicates preserving the empirical univariate marginals and rank-correlation structure, the median is 1.543 and the 5th–95th percentile interval is 1.504–1.603. None of the 50 null replicates reaches the observed value, giving the finite-null empirical p-value 1/51 = 0.0196.

The result is stable across density scales:

- k=30: observed 1.810 versus Gaussian-copula null median 1.587, empirical p=0.0196;
- k=60: observed 1.772 versus null median 1.543, empirical p=0.0196;
- k=120: observed 1.722 versus null median 1.502, empirical p=0.0196.

Against a multivariate-normal null with the empirical covariance, the primary density-IQR comparison is weaker: observed 1.772 versus null median 1.720, empirical p=0.0784.

The Gaussian-copula comparison is the more informative frozen null for higher-order structure because it preserves both the empirical one-dimensional marginals and monotonic dependence structure.

## Measurement-quality sensitivity

Density heterogeneity decreases as respondent item coverage becomes stricter, which is consistent with sparse-item measurement noise contributing some local irregularity. The density IQR is 1.825 in the >=1-item/domain cohort, 1.772 in the >=2 primary cohort, and 1.677 in the >=3 cleaner cohort.

However, the excess over the Gaussian-copula null remains in both sensitivity cohorts. For the broad cohort the observed k=60 density IQR is 1.826 versus null median 1.574 (empirical p=0.0196). For the cleaner cohort it is 1.673 versus null median 1.491 (empirical p=0.0196).

Thus the higher-order density heterogeneity is not eliminated by requiring better item coverage, although its magnitude is smaller in the cleaner cohort.

## Extraversion source-key anomaly sensitivity

`ItemInfo696.csv` assigns 20 items to IPIP100 Extraversion, but `superKey696.csv` gives a nonzero `IPIP100extra` coefficient for only 19. Primary scoring follows the official nonzero key. A prespecified sensitivity adds `q_55` ("Am a very private person.") as reverse-keyed.

That sensitivity yields 8,863 primary-eligible respondents and the same connectivity result: one component at every 10–90% density threshold, fragmentation score 0, largest-component deficit 0, and density IQR 1.782. The primary qualitative conclusion is unchanged.

## Interpretation

### Observed

The frozen five-dimensional Big Five occupancy terrain is continuously connected at the tested kNN scales and density thresholds. No material discrete branch or lobe separation is detected. Local density heterogeneity is greater than the Gaussian-copula null preserving marginals and rank dependence, and that excess survives density-scale and item-coverage sensitivity checks.

### Interpretation

At Big Five resolution, the human population appears more like one connected but internally uneven terrain than a set of sharply separated personality islands. There is evidence for higher-order occupancy structure beyond a simple copula description, but the current graph analysis does not resolve that structure into distinct material basins or corridors.

This is not a negative result for the broader research program. It identifies where the interesting structure is not: it is not expressed as coarse disconnected Big Five components under these frozen definitions. The next resolution increase should therefore examine aspects/facets or narrower trait coordinates while preserving the same dimension-agnostic terrain machinery.

### Hypothesis

The model-side geometry may be representing finer-grained behavioral organization that is compressed away by the five broad Big Five domains. If so, richer human representations should increase local topological structure without requiring changes to the terrain method itself.

### Unknown

This first pass does not test persistent homology for true topological holes, nonlinear manifold curvature, facet-level terrain, or actual behavioral transitions. It also cannot determine whether the observed density heterogeneity reflects stable psychological organization, item-level interactions, demographic mixture, response-style effects, or another source.

## Next step

The strongest next human-only analysis is to rerun the same frozen occupancy framework at higher psychological resolution, preferably the ten BFAS aspects first because they remain established psychological constructs while doubling resolution from 5D to 10D. A facet-level or narrower-trait analysis can follow if sample support remains adequate.

Only after the human terrain is independently characterized at the chosen resolution should its topology be compared with the independently derived model terrain. Dynamic “paths of least resistance” remain a later longitudinal question.
