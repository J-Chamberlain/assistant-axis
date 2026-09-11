# Future SAPA Scoring Options for the Provisional Trait Bridge

Status: methodological feasibility note; no respondent-to-model scoring was performed.

## Empirical constraint

The 45 `ACCEPT_DIRECT` proxies use 96 distinct SAPA items. A respondent observed a median of 10 of those items, and the median respondent had zero fully observed direct proxies under exact evidence-item scoring. Across all 74 retained links, a respondent observed a median of 13 of 129 items and one fully observed proxy. No respondent observed a complete retained profile. Any later respondent-level analysis must therefore treat the randomized SAPA administration design as planned missingness rather than manufacture complete profiles.

## Options

| Option | Required assumptions | Fit to SAPA planned missingness | Likely coverage | Complexity | Main risk |
|---|---|---|---|---|---|
| Official source-scale scoring from administered subsets | Missing-by-design items are ignorable; a preregistered minimum item rule preserves score meaning; partial scores are comparable across forms | Moderate | Potentially broad for established source scales, but weak for the narrow 1–3 item bridge proxies | Low–moderate | Heterogeneous item subsets can create nonequivalent scores and attenuated reliability |
| Pairwise covariance/correlation modeling | Random administration is effectively MCAR for the item pairs; pairwise covariance estimates are sufficiently compatible | Strong for group-level structure | All retained items and proxies at the covariance level | Low | Produces no respondent-level trait scores; pairwise matrices can be slightly non-positive-semidefinite |
| Confirmatory/exploratory factor scoring | A defensible latent structure is specified and invariant across administration patterns; scoring handles missing likelihoods | Moderate | Best for multi-item source domains and carefully pooled narrow constructs | Moderate–high | With only 1–3 bridge items per construct, a 45-factor model is underidentified or unstable |
| Ordinal IRT | Item response functions are invariant; local independence is reasonable; enough items anchor each latent construct | Potentially strong | Stronger for official item pools than for single-item or two-item proxies | High | Narrow bridge constructs lack enough items for separately identified latent traits; multidimensional IRT may become fragile |
| Full-information latent-variable modeling | Missingness is ignorable under the randomized design; the covariance/threshold model is correctly specified | Strong in principle | Multi-item latent domains; possibly a reduced bridge | High | A high-dimensional 45- or 74-trait model may be weakly identified and sensitive to structural assumptions |
| Multiple imputation | The imputation model contains the joint structure needed to predict mostly unadministered items and properly reflects uncertainty | Weak–moderate | Nominally broad | High | Extreme planned sparsity makes a saturated joint imputation model unrealistic; mean-style or generic chained imputation could invent structure |
| Bayesian latent trait estimation | Priors and measurement model are defensible; missingness is ignorable; posterior uncertainty is propagated | Strong in principle | Reduced multi-item bridge or source-scale latent traits | Very high | Results can be prior-sensitive, and single-item constructs remain weakly identified |

## Practical next-method comparison

A later methods study should compare a reduced, independently reviewed bridge under three candidates: (1) official source-scale partial scoring with explicit minimum-item rules, (2) full-information latent scoring for multi-item constructs, and (3) Bayesian or ordinal-IRT scoring only where an adequate item pool exists. Pairwise covariance remains the appropriate reference for group-level structural checks. Generic mean imputation and complete-case scoring should not be contenders.

The comparison should evaluate score availability, test-retest or split-item stability where possible, recovery in masked-item experiments, and sensitivity to administration-pattern assumptions. It should not select a method using any model-geometry outcome.
