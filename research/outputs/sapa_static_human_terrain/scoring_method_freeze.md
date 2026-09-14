# SAPA Static Human Terrain — Scoring Method Freeze

Status: frozen before any terrain/density/topology results are computed or inspected.

## Purpose

Choose a respondent-level five-dimensional Big Five scoring method using only measurement-recovery diagnostics under SAPA's planned missingness. Model-side geometry is not used. Terrain density, modes, holes, ridges, bottlenecks, and cross-model correspondence are not inspected during this selection.

## Source

Canonical human release: Harvard Dataverse V5, doi:10.7910/DVN/SD7SVE. Expected respondent table SHA256: `fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6`.

Primary psychological representation: SAPA IPIP100 Big Five domains. Source item membership is taken from `ItemInfo696.csv`; score direction is taken mechanically from `superKey696.csv`.

Observed source anomaly: `ItemInfo696.csv` assigns 20 items to IPIP100 Extraversion, but `superKey696.csv` gives a nonzero `IPIP100extra` coefficient for only 19. The zero-coefficient item is `q_55` ("Am a very private person."). Primary scoring therefore follows the official nonzero scoring key exactly and uses 19 Extraversion items. A prespecified sensitivity analysis may add `q_55` as reverse-keyed, but this cannot replace the primary result.

## Candidate scoring rules

All responses are first keyed so higher values indicate more of the named domain. For reverse-keyed items on the 1–6 scale, keyed response is `7 - response`.

A. Raw keyed mean: mean of available keyed responses within domain.

B. Item-centered mean: subtract each item's training-sample keyed mean, average available residuals, and add the equal-item domain mean.

C. Item-standardized residual mean: subtract each item's training-sample keyed mean, divide by its training-sample keyed SD, and average available standardized residuals. Final domain coordinates are standardized only after respondent scoring.

No deterministic filling of unanswered items is permitted. No Gaussian latent prior, multivariate-normal imputation, factor-score prior, or model-side information is permitted in the primary scoring method, because these could impose or smooth the terrain topology being tested.

## Selection test

Use deterministic five-fold respondent splits based on RID hash. For each domain and held-out fold, fit item means and SDs using training respondents only. Among held-out respondents with at least two observed keyed items in that domain, leave each observed item out in turn and predict its keyed response using the remaining observed items.

Compare A/B/C on pooled held-out RMSE, MAE, and Pearson correlation separately by domain. Selection is based on mean standardized rank across the five domains, prioritizing RMSE, then MAE, then correlation. A method must not be rejected because it produces less visually interesting geometry; terrain output is unavailable during selection.

## Recovery characterization

After choosing the scoring rule, characterize item-sampling uncertainty without inspecting terrain. Among respondents with at least six observed items in a domain, repeatedly subsample k=1,2,3,4,5 items and compare the resulting score with the same respondent's all-observed score. Record correlation, RMSE, normalized RMSE, and MAE by domain and k.

This recovery exercise calibrates measurement uncertainty. It does not prove that the all-observed score is error-free.

## Cohort rule for Stage 1 terrain

Primary cohort: respondents with at least 2 scored IPIP100 items in every one of the five domains.

Sensitivity cohorts:

- broad: at least 1 item in every domain;
- cleaner: at least 3 items in every domain.

The primary threshold is fixed before terrain inspection. It is chosen as a compromise between five-dimensional sample size and the recovery diagnostics, not to maximize or minimize apparent topology.

## Terrain interpretation boundary

All Stage 1 results are static occupancy structure. Density corridors, holes, bottlenecks, modes, and ridges are not transition probabilities, attractors, energy barriers, or paths of least resistance. Dynamic interpretation requires longitudinal evidence.
