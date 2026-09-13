# AA-12 follow-up 7 — Aggregate human-profile geometry projection method freeze

Status: **FROZEN BEFORE ANY HUMAN PC COORDINATE OR HUMAN/TERRAIN RESULT WAS COMPUTED OR INSPECTED**  
Date: 2026-09-13  
Analysis model: GPT-5.5  
Branch: `codex/aa12-human-terrain-overlay`  
Required base: `103c13ea692ed7e1c9cb8309bfc8b150171e7b40`

## Scope

This study predicts model-native PC1–PC3 locations for already-frozen **aggregate** SAPA latent profiles. It does not project respondents, refit human profiles, change the semantic bridge, or modify the frozen model-role occupancy terrain. Every projection is a model prediction from relative trait-profile shape, not an observed human activation coordinate.

Primary analysis uses the frozen 12 moderate-or-better `ACCEPT_DIRECT` mappings (9 high, 3 moderate). The complete 45 `ACCEPT_DIRECT` mappings are a secondary measurement-sensitivity analysis. `ACCEPT_CLOSE` mappings and the other 195 model traits are excluded.

## Frozen sources

- Human aggregate profiles: `research/outputs/human_model_profile_correspondence/human_trait_profiles_12.csv` and `human_trait_profiles_45.csv`.
- Human K status and size: K=4,5,6,7,8,10 eligible; K=9 diagnostic/ineligible. Profile sizes and stability tiers are copied from frozen AA-12 outputs.
- Model role/trait matrices: Qwen `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`; LLaMA and Gemma `research/outputs/multimodel_trait_profile_pc_predictor/{llama,gemma}/persona_trait_similarity_matrix.csv`.
- Native role targets and terrain: `research/outputs/model_coverage_terrain_viewer/`, frozen at numerical commit `9335ffaeac215cfdbb709b041c1fa1db0d8f754e` and final commit `103c13ea692ed7e1c9cb8309bfc8b150171e7b40`.
- Frozen A–E family memberships and native centroids: Follow-up-6 tables, inherited from `research/outputs/crossmodel_cluster_reconciliation/` without modification.
- Display alignment: the exact Follow-up-6 model-only variance-standardized PC1–PC3 Procrustes transform from `research/outputs/human_supported_trait_convergence/procrustes_alignment_matrices.json`. No transform is refit.

The existing `human_split_refit_stability.csv` contains distances and proportions, not aligned aggregate trait vectors. Therefore human-fit parameter spread is preregistered as **NOT AVAILABLE**; no new human bootstrap/refit will be created.

## Shared-trait representation

For each trait set independently:

1. Extract the exact ordered trait list from the corresponding frozen human profile file.
2. For each model role, use the canonical raw activation-space role/trait cosine values for those traits.
3. For each human aggregate profile, use its frozen `human_trait_value` values.
4. Within each row, subtract that row's across-trait mean.
5. Divide by the centered row's L2 norm.

No across-domain level or scale equivalence is assumed. Euclidean distance between these unit vectors is a monotonic transform of centered cosine/Pearson profile-shape similarity. Zero or non-finite norms are fatal verification failures. The exact transformed role and human vectors will be saved.

## Primary Ridge projection

Fit Qwen, LLaMA, and Gemma independently. Each model has 275 training rows and three unstandardized native targets: canonical PC1, PC2, PC3. Features are the centered/L2-normalized 12- or 45-trait rows. A multivariate `sklearn.linear_model.Ridge(fit_intercept=True)` uses one shared alpha across the three outputs and no additional feature scaling.

Alpha grid: `10**p` for integer `p=-6,-5,...,6`.

Model-only nested validation:

- outer CV: 10-fold shuffled K-fold, seed `120927`;
- inner CV within each outer training set: 5-fold shuffled K-fold, seed `121000 + outer_fold`;
- inner objective: root mean squared error after dividing each coordinate residual by that inner-training coordinate SD, averaged over all held-out rows and three coordinates;
- alpha selection: smallest objective; numerical ties within `1e-12` choose the larger alpha;
- final alpha: the same grid and objective under 10-fold CV over all 275 roles, seed `120928`.

Report pooled outer-fold PC-specific R²/RMSE, mean-coordinate-baseline R²/RMSE, normalized 3D RMSE, selected alphas, and covariance of pooled outer-fold residuals. Normalized 3D RMSE is `sqrt(mean((residual_j / full-sample target_SD_j)^2))`; the mean-coordinate baseline is approximately 1 by construction.

### Frozen usability gate

A model/trait-set projection is `USABLE` only if all are true under nested model-only OOF predictions:

1. normalized 3D RMSE `<= 0.90`;
2. mean of the three coordinate R² values `>= 0.20`;
3. at least two of three coordinate R² values are positive;
4. normalized 3D RMSE is lower than the corresponding mean-coordinate baseline.

If the primary 12-trait model fails for a model, its human location is saved for diagnostics but must be labeled `INSUFFICIENT MODEL-SIDE LOCALIZATION`, hidden by default in the viewer, excluded from coverage-extension candidacy, and never described as precise. The 45-trait sensitivity never supersedes the primary solely because its validation is stronger.

## Support-constrained interpolation

The secondary estimator is k-nearest-neighbor regression in the same normalized trait-shape space. Euclidean distance is used; on unit centered vectors it is equivalent in ordering to centered cosine.

Candidate `k`: 3, 5, 7, 10, 15, 25, 40. Candidate weights: `uniform`, `distance`. Selection uses the same nested splits and normalized 3D RMSE objective. Ties choose smaller k, then `distance`. The final setting is selected by 10-fold model-only CV with seed `120928`.

For every projected aggregate profile, save the selected neighbors, their similarities, the interpolation coordinate, neighbor-coordinate spread, and PC-standardized Ridge↔kNN displacement. Ridge remains primary.

## Projection uncertainty

For every model, trait set, and aggregate human profile, make 500 deterministic bootstrap refits of the 275 role rows with replacement, retaining the already selected full-data Ridge alpha. Seeds are:

- 12 traits: Qwen `121201`, LLaMA `121202`, Gemma `121203`;
- 45 traits: Qwen `451201`, LLaMA `451202`, Gemma `451203`.

Save all aggregate-profile bootstrap predicted coordinates plus centroid, covariance, axis SDs, and covariance-eigendecomposition ellipsoid parameters. This is a **model-fit bootstrap envelope**, not a confidence region for a human's true model-space position.

Pooled nested-CV residual covariance is saved separately and is never silently combined with bootstrap covariance. A second optional residual envelope may be displayed only with an explicit label.

## Support and OOD diagnostics

For each model/trait-set/profile:

- maximum similarity to any model role;
- mean similarity of the selected kNN support roles;
- support percentile relative to the distribution of each model role's leave-one-out maximum role similarity;
- PC-standardized Ridge↔kNN displacement;
- nearest-role PC-standardized native distance;
- frozen Follow-up-6 KDE density at the Ridge location;
- sparsity percentile relative to role-location densities;
- membership inside the frozen 50%, 80%, and 95% sample-coverage density thresholds;
- nearest frozen A–E native family centroid and distances to all available family centroids.

OOD warnings are mechanical and descriptive: `LOW_SHAPE_SUPPORT` if support percentile <5; `RIDGE_KNN_DISAGREEMENT` if Ridge↔kNN displacement exceeds the 95th percentile of model-role nested-OOF Ridge↔kNN displacement; and `BEYOND_95_SAMPLE_COVERAGE` if Ridge density is below the frozen 95% threshold.

## 12-versus-45 sensitivity

For every model/profile, save both coordinates, displacement in model-native PC-SD units, signed native displacement, coverage-membership changes, density-regime changes, nearest roles before/after, and nearest family before/after. A line may connect the two locations in the viewer. No post-result trait weighting or selection is allowed.

## Coverage-extension rule

A model/profile row is a `PROJECTED COVERAGE-EXTENSION CANDIDATE` only when:

1. the primary 12-trait model passes the frozen usability gate; and
2. the primary 12-trait Ridge density lies below the frozen 95% sampled-role coverage threshold.

A profile-level candidate is called cross-model recurring only if the condition holds in at least two usable models. The table must also carry 12/45 displacement, bootstrap placement fraction, shape support, Ridge/kNN disagreement, and nearest-role distance. No outside point is automatically interpreted as meaningful territory.

## Human K and cross-model comparison

Eligible K=4,5,6,7,8,10 are primary. K=9 is computed only after eligible results freeze and remains diagnostic/ineligible. K=6 is the viewer presentation default because its human split-refit stability is moderate. K=10 remains available as the predictive-likelihood/aggregate-correspondence anchor with low split-refit stability. Neither is the true human resolution.

Each native prediction is transformed with the already frozen display transform. Pairwise Qwen↔LLaMA, Qwen↔Gemma, and LLaMA↔Gemma display-aligned distances and their mean are descriptive. No human data refit or alter the alignment.

## Viewer and publication plan

The derivative viewer will preserve the original Follow-up-6 HTML byte-for-byte and reuse its architecture in `research/outputs/human_profile_terrain_overlay/human_profile_terrain_overlay.html`. Default: Qwen, K=6, 12 traits, Ridge, bootstrap envelope on, role points on, occupancy on, sample-size scaling off.

The repository has no existing `.openai/hosting.json`, GitHub Pages workflow, CNAME, Wrangler, Vercel, or Netlify manifest. Publication will therefore use the authorized Sites static-hosting workflow. The deployable static site will expose `/model-terrain/` and `/human-terrain/`, contain no secrets or microdata, and record its exact public build in `public_deployment_manifest.json`. Public deployment is not claimed until unauthenticated desktop and mobile-width checks pass against the deployed URL.

## Frozen boundaries

No individual respondent projection or imputation; no 240-trait human completion; no bridge expansion or `ACCEPT_CLOSE`; no family/match/role-name/PC-interpretation-informed training; no K or model-family change; no human contribution to KDE, density, terrain boundaries, or alignment; no probability/prevalence, psychometric-equivalence, shared-mechanism, neural-coordinate, stability, accessibility, or basin claim; no new prompts, model inference, activation extraction, external model API, GPU, or RunPod.
