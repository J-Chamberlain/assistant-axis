# Cross-Model Feature Transfer Summary

Date: 2026-05-28
Model used: GPT-5.5 Standard

## Question

Do Claude Big Five features transfer to canonical activation PCA geometry, and do Codex-derived behavioral/procedural features transfer to a Claude/Big-Five-derived pseudo-PCA geometry?

## Matrix

| feature_family | target | mean_r2 | semantic_baseline_r2 | delta_vs_semantic_baseline | axis1_r2 | axis2_r2 | axis3_r2 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| codex_derived_outer_loop_features | canonical_activation_pca3 | 0.49009 | 0.389397 | 0.100693 | 0.631205 | 0.257221 | 0.422097 |
| claude_big_five_features | canonical_activation_pca3 | 0.612861 | 0.389397 | 0.223464 | 0.733919 | 0.480416 | 0.414677 |
| codex_derived_outer_loop_features | claude_big_five_pseudo_pca3 | 0.280223 | 0.268704 | 0.01152 | 0.401787 | -0.190897 | 0.073905 |
| claude_big_five_features | claude_big_five_pseudo_pca3 | 1.0 | 0.268704 | 0.731296 | 1.0 | 1.0 | 1.0 |

## Direct Answers

- Big Five improves canonical activation PCA prediction: yes (delta vs semantic baseline +0.223; residual reduction +5.483).
- Codex features improve Claude pseudo-PCA prediction: no (delta vs semantic baseline +0.012; residual reduction -0.041).
- Overall interpretation: big five transfers to activation but codex does not transfer to pseudo pca.

## Caveat

No separately committed Claude pseudo-PCA coordinate artifact was found. This run reconstructs the pseudo-PCA target from `visualizations/bigfive_profiles.json`, so the Big-Five-on-pseudo-PCA condition is a positive-control style condition rather than an independent target.
