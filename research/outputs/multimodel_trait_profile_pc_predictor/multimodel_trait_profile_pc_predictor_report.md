# Multimodel trait-profile to persona-PC predictor

Generated UTC: 2026-09-11T20:59:40Z

## Result

Observed: complete same-model activation-derived trait profiles predict held-out persona PCA location in both Llama and Gemma under the canonical Qwen pipeline. Ridge remains the selected family under the predeclared 10% material-improvement rule unless the table below states otherwise. This is same-space representation analysis, not evidence that any model has more sophisticated or more human-like psychology.

## Cross-model comparison

| Model | Raw Ridge LOPO R2 PC1/PC2/PC3 | Raw norm. 3D RMSE | Quantile norm. 3D RMSE | Family norm. 3D RMSE | Family/LOPO mean-error ratio | Permutation p95 mean R2 | Synthetic R2 PC1/PC2/PC3 | Synthetic norm. 3D RMSE | Selected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Qwen/Qwen3-32B | 0.999522/0.998811/0.999611 | 0.045378 | 0.159028 | 0.067997 | 1.679x | -0.007548 | 0.995266/0.984377/0.997144 | 0.149728 | ridge |
| Llama-3.3-70B | 0.997833/0.997161/0.989900 | 0.124494 | 0.328303 | 0.204224 | 1.810x | -0.009359 | 0.983420/0.982280/0.946688 | 0.331184 | ridge |
| Gemma-2-27B | 0.999788/0.996179/0.987835 | 0.127824 | 0.304909 | 0.176110 | 1.535x | -0.011572 | 0.999557/0.980280/0.969824 | 0.214870 | ridge |

Qwen numbers above are read directly from the canonical saved validation summary, not recomputed.

## Important divergences

Llama and Gemma raw LOPO normalized RMSE are 2.74x and 2.82x Qwen's, and their role-family RMSE values are 3.00x and 2.59x Qwen's. The largest relative losses are concentrated in PC3 and distant synthetic mixtures, although all raw LOPO PC R2 values remain above 0.9878.

The hardest fixed role family by normalized RMSE is other for both Llama and Gemma, unlike editorial in Qwen. Training-only OOD/error association is also much stronger for Llama than for Qwen or Gemma. These are measured pipeline differences, not rankings of psychological sophistication or human-likeness.

RBF Kernel Ridge partly reduces the precision loss of quantile profiles in repeated nested validation for Llama and Gemma, but neither quantile pipeline beats raw Ridge and no raw nonlinear challenger clears the model-replacement rule.

## Methods held constant

The canonical Qwen runner is imported for the estimator definitions, grids, repeated 5-fold x 10-seed outer validation, 4-fold inner tuning, LOPO, 100 target permutations, training-only OOD PCA, and deterministic synthetic-pair selection. Raw profiles are same-model role-to-trait cosines after layer mean-pooling and L2 normalization. QuantileTransformer and all scaling remain inside each training fold.

A complete second fixed-seed run reproduced all 20 deterministic model CSV artifacts byte-for-byte; exact before/after hashes are saved in deterministic_full_rerun_comparison.json.

Role-family transfer uses the fixed label: Qwen-canonical role-family partition applied cross-model. It is not described as Llama-native or Gemma-native clustering.

## Model-specific results

### Llama-3.3-70B

Sources: /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/llama-3.3-70b/role_vectors and /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/llama-3.3-70b/trait_vectors.

PCA reproduction max absolute error: 2.748e-14 (strict tolerance 1.0e-08); orientation signs [1, -1, -1].

Raw Ridge LOPO: R2 0.997833/0.997161/0.989900; Pearson 0.998916/0.998583/0.994981; Spearman 0.997667/0.996618/0.995319; RMSE 0.053225/0.055224/0.070457; MAE 0.032626/0.039427/0.043352; normalized 3D RMSE 0.124494.

Fold-safe quantile Ridge LOPO: R2 0.982646/0.986466/0.925175; normalized 3D RMSE 0.328303. Quantiles are less precise than raw cosines for this model.

Role-family holdout Ridge: R2 0.993894/0.993627/0.977094; normalized 3D RMSE 0.204224; mean-error degradation 1.810x; aggregate bias [0.0271, 0.0280, 0.0223].

Permutation control: 100 permutations, p95 mean-PC R2 -0.009359, maximum 0.008320; leakage anomaly detected=False.

Synthetic endpoint-held-out interpolation: R2 0.983420/0.982280/0.946688; normalized 3D RMSE 0.331184; nearby 0.064988; distant 0.463834; pair-level endpoint-distance/error Pearson 0.8704, Spearman 0.7854.

OOD/error association: 5-NN distance Pearson 0.6505, Spearman 0.6063; reconstruction residual Pearson 0.6138, Spearman 0.5105. These are geometric associations, not calibrated probabilities.

Selected model family: ridge. Ridge remains V1 because no challenger cleared the predeclared material-improvement rule without a harder-holdout penalty.

Nested repeated model comparison:

| Representation | Model | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE |
|---|---|---:|---:|---:|---:|
| raw_cosine | ridge | 0.997179 | 0.996573 | 0.986628 | 0.143906 |
| raw_cosine | pls | 0.995933 | 0.995322 | 0.984414 | 0.159656 |
| raw_cosine | kernel_ridge | 0.993293 | 0.988599 | 0.960200 | 0.257805 |
| raw_cosine | knn | 0.929342 | 0.949262 | 0.757241 | 0.620909 |
| quantile | ridge | 0.979806 | 0.981579 | 0.904156 | 0.379073 |
| quantile | pls | 0.975197 | 0.979132 | 0.899457 | 0.392779 |
| quantile | kernel_ridge | 0.991116 | 0.986686 | 0.920014 | 0.335572 |
| quantile | knn | 0.921652 | 0.934573 | 0.735529 | 0.657347 |

Ridge role-family holdouts:

| Role family | n | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE | mean-error vs family LOPO | bias PC1/PC2/PC3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| combative_iconoclast | 15 | 0.9860 | 0.9812 | 0.9322 | 0.2136 | 1.266x | 0.030/-0.015/-0.013 |
| editorial | 13 | 0.9773 | 0.9722 | 0.9812 | 0.0695 | 0.780x | -0.000/-0.012/0.004 |
| grounded_social | 54 | 0.9923 | 0.9916 | 0.9579 | 0.1805 | 1.332x | -0.000/-0.022/-0.012 |
| mythic_spiritual | 51 | 0.9604 | 0.9681 | 0.9855 | 0.2785 | 2.765x | 0.110/0.057/0.003 |
| other | 6 | 0.8105 | 0.9647 | 0.9854 | 0.4383 | 1.284x | -0.126/0.117/-0.028 |
| procedural_professional | 126 | 0.9874 | 0.9471 | 0.9612 | 0.1378 | 2.133x | 0.017/0.046/0.053 |
| trickster_chaos | 10 | 0.9863 | 0.9851 | 0.9299 | 0.3821 | 1.377x | 0.010/-0.011/0.022 |

### Gemma-2-27B

Sources: /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/gemma-2-27b/role_vectors and /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/gemma-2-27b/trait_vectors.

PCA reproduction max absolute error: 1.376e-11 (strict tolerance 1.0e-08); orientation signs [1, 1, 1].

Raw Ridge LOPO: R2 0.999788/0.996179/0.987835; Pearson 0.999894/0.998099/0.993928; Spearman 0.999819/0.995881/0.991419; RMSE 7.544873/23.643897/28.136896; MAE 5.440359/16.131241/16.702279; normalized 3D RMSE 0.127824.

Fold-safe quantile Ridge LOPO: R2 0.994534/0.977123/0.936810; normalized 3D RMSE 0.304909. Quantiles are less precise than raw cosines for this model.

Role-family holdout Ridge: R2 0.999271/0.993851/0.975087; normalized 3D RMSE 0.176110; mean-error degradation 1.535x; aggregate bias [-0.1817, -4.6482, -6.5657].

Permutation control: 100 permutations, p95 mean-PC R2 -0.011572, maximum -0.004984; leakage anomaly detected=False.

Synthetic endpoint-held-out interpolation: R2 0.999557/0.980280/0.969824; normalized 3D RMSE 0.214870; nearby 0.066921; distant 0.296412; pair-level endpoint-distance/error Pearson 0.7738, Spearman 0.8096.

OOD/error association: 5-NN distance Pearson 0.3825, Spearman 0.2743; reconstruction residual Pearson 0.3791, Spearman 0.3193. These are geometric associations, not calibrated probabilities.

Selected model family: ridge. Ridge remains V1 because no challenger cleared the predeclared material-improvement rule without a harder-holdout penalty.

Nested repeated model comparison:

| Representation | Model | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE |
|---|---|---:|---:|---:|---:|
| raw_cosine | ridge | 0.999649 | 0.995112 | 0.984375 | 0.146321 |
| raw_cosine | pls | 0.998990 | 0.993860 | 0.982674 | 0.158385 |
| raw_cosine | kernel_ridge | 0.995902 | 0.988206 | 0.965492 | 0.229603 |
| raw_cosine | knn | 0.951759 | 0.924682 | 0.762521 | 0.609861 |
| quantile | ridge | 0.993361 | 0.973719 | 0.925468 | 0.334029 |
| quantile | pls | 0.992271 | 0.970257 | 0.917227 | 0.352372 |
| quantile | kernel_ridge | 0.995886 | 0.985106 | 0.933869 | 0.299311 |
| quantile | knn | 0.955621 | 0.917856 | 0.702237 | 0.663464 |

Ridge role-family holdouts:

| Role family | n | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE | mean-error vs family LOPO | bias PC1/PC2/PC3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| combative_iconoclast | 15 | 0.9972 | 0.9940 | 0.9739 | 0.1592 | 1.306x | 2.386/-3.752/0.606 |
| editorial | 13 | 0.9603 | 0.9574 | 0.8924 | 0.1632 | 1.360x | 2.736/-1.989/-7.733 |
| grounded_social | 54 | 0.9973 | 0.9892 | 0.9788 | 0.1615 | 1.457x | -1.549/-4.320/-6.185 |
| mythic_spiritual | 51 | 0.9960 | 0.9553 | 0.9561 | 0.2509 | 1.975x | 2.073/-7.157/-31.062 |
| other | 6 | 0.9969 | 0.9829 | 0.9445 | 0.4411 | 1.512x | -8.792/-8.665/30.423 |
| procedural_professional | 126 | 0.9972 | 0.9710 | 0.9721 | 0.1006 | 1.406x | -1.468/-2.306/1.771 |
| trickster_chaos | 10 | 0.9964 | 0.9854 | 0.9859 | 0.2722 | 1.459x | 9.433/-25.526/-20.156 |

## OOD association comparison

| Model | 5-NN distance Pearson/Spearman | Reconstruction residual Pearson/Spearman |
|---|---:|---:|
| Qwen/Qwen3-32B | 0.2431/0.2627 | 0.3002/0.2477 |
| Llama-3.3-70B | 0.6505/0.6063 | 0.6138/0.5105 |
| Gemma-2-27B | 0.3825/0.2743 | 0.3791/0.3193 |

## Epistemic status

Observed:

- Held-out LOPO, whole-role-family, permutation, OOD-association, and endpoint-held-out synthetic metrics reported above.
- Exact 275-role and 240-trait label coverage in each model, finite sources and cosine matrices, and strict reproduction of the established within-model PCA coordinates.
- Raw and quantile Ridge performance plus repeated nested comparisons with PLS, RBF Kernel Ridge, and distance-weighted KNN.

Interpretation:

- Replication across the three saved open-model vector sets supports broad same-space trait-bank coverage of their respective persona geometries.
- If Ridge remains selected, the relationship is approximately linear at the resolution tested; this does not imply individual coefficients are stable semantic explanations because the 240 traits are highly correlated.
- Whole-family degradation and distance-linked synthetic error identify limits of interpolation inside the saved artifact family.

Hypotheses and unresolved questions:

- Whether frozen profile-based predictions match newly elicited behavioral persona activations remains untested.
- Whether the pattern extends to frontier models, other checkpoints, humans, or a human personality ontology remains untested.
- PC sign orientation helps display consistency; it does not establish identical PC1/PC2/PC3 semantics across models.

No GPU, RunPod, new model inference, new activation extraction, or external model API was used.
