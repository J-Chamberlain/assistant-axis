# Cluster-Conditioned Axis Tests: PC1 and PC2

model_used: GPT-5.5

## Data Sources

- Role geometry: `research/visualizations/geometry_viz_data.json`
- Proxy annotations: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/axis_rater_scores.csv`
- Text for cluster classifier: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/blinded_persona_dossiers.jsonl`
- Prior PC3 validation context: `research/outputs/pc3_validation/`

Cluster labels used: `roles.clusters` from `geometry_viz_data.json`.

Role count: 275
Cluster count: 7
Cluster counts: `{'combative_iconoclast': 15, 'editorial': 13, 'grounded_social': 54, 'mythic_spiritual': 51, 'other': 6, 'procedural_professional': 126, 'trickster_chaos': 10}`
Missing text records for cluster prediction: 0

## Proxy Scores

PC1 proxy: `pc1_objective_certainty_score`, interpreted as convergence pressure versus degrees of freedom.

PC2 proxy: `100 - abstraction_score`, interpreted as situated developmental immediacy versus integrated abstraction. This sign choice makes higher proxy scores predict higher PC2, because prior PC2 work found abstraction negatively associated with PC2.

## PC1 Results

Global Pearson r=0.558, p=5.93e-24; global Spearman r=0.565, p=1.47e-24. Cluster-controlled Pearson r=0.268, p=6.82e-06; cluster-controlled Spearman r=0.260, p=1.29e-05.

| pair scope | ordering accuracy | usable pairs |
|---|---:|---:|
| global | 0.709 | 36906 |
| within-cluster | 0.622 | 10515 |
| across-cluster | 0.743 | 26391 |

Within-minus-global bootstrap: mean diff -0.085, 95% CI [-0.125, -0.044]

### PC1 Per-Cluster Results

| cluster | n | Pearson | Spearman | pairwise accuracy |
|---|---:|---|---|---:|
| combative_iconoclast | 15 | r=0.337, p=0.219 | r=0.294, p=0.288 | 0.598 |
| editorial | 13 | r=0.802, p=0.00098 | r=0.615, p=0.0252 | 0.733 |
| grounded_social | 54 | r=0.093, p=0.502 | r=0.120, p=0.387 | 0.551 |
| mythic_spiritual | 51 | r=0.235, p=0.0974 | r=0.265, p=0.0602 | 0.600 |
| other | 6 | r=-0.548, p=0.26 | r=-0.371, p=0.468 | 0.333 |
| procedural_professional | 126 | r=0.404, p=2.63e-06 | r=0.387, p=7.6e-06 | 0.639 |
| trickster_chaos | 10 | r=-0.121, p=0.739 | r=-0.073, p=0.841 | 0.477 |

## PC2 Results

Global Pearson r=0.655, p=3.94e-35; global Spearman r=0.658, p=1.48e-35. Cluster-controlled Pearson r=0.486, p=9.82e-18; cluster-controlled Spearman r=0.484, p=1.54e-17.

| pair scope | ordering accuracy | usable pairs |
|---|---:|---:|
| global | 0.746 | 36827 |
| within-cluster | 0.687 | 10483 |
| across-cluster | 0.770 | 26344 |

Within-minus-global bootstrap: mean diff -0.058, 95% CI [-0.099, -0.020]

### PC2 Per-Cluster Results

| cluster | n | Pearson | Spearman | pairwise accuracy |
|---|---:|---|---|---:|
| combative_iconoclast | 15 | r=0.573, p=0.0255 | r=0.514, p=0.0502 | 0.701 |
| editorial | 13 | r=-0.309, p=0.305 | r=-0.403, p=0.172 | 0.387 |
| grounded_social | 54 | r=0.549, p=1.71e-05 | r=0.476, p=0.000275 | 0.681 |
| mythic_spiritual | 51 | r=0.639, p=4.48e-07 | r=0.587, p=5.89e-06 | 0.722 |
| other | 6 | r=-0.711, p=0.113 | r=-0.609, p=0.2 | 0.286 |
| procedural_professional | 126 | r=0.526, p=2.52e-10 | r=0.520, p=4.39e-10 | 0.686 |
| trickster_chaos | 10 | r=0.378, p=0.281 | r=0.523, p=0.121 | 0.705 |

## Cluster Prediction Accuracy

A TF-IDF bigram logistic classifier was trained in five stratified folds on blinded dossier text.

Mean held-out cluster accuracy: 0.687
Mean held-out macro F1: 0.404

## Direct vs Oracle-Cluster vs Predicted-Cluster Regimes

### PC1

| regime | R2 | Pearson | Spearman | RMSE | pairwise accuracy |
|---|---:|---:|---:|---:|---:|
| direct_axis | 0.296 | 0.544 | 0.550 | 25.196 | 0.700 |
| oracle_cluster | 0.811 | 0.901 | 0.866 | 13.053 | 0.832 |
| predicted_cluster | 0.647 | 0.810 | 0.799 | 17.838 | 0.797 |

### PC2

| regime | R2 | Pearson | Spearman | RMSE | pairwise accuracy |
|---|---:|---:|---:|---:|---:|
| direct_axis | 0.416 | 0.645 | 0.655 | 16.416 | 0.741 |
| oracle_cluster | 0.718 | 0.847 | 0.847 | 11.413 | 0.831 |
| predicted_cluster | 0.520 | 0.732 | 0.715 | 14.879 | 0.772 |

## Interpretation

Observed: simple within-cluster pairwise ordering is not easier for either axis. PC1 global ordering accuracy is 0.709, while within-cluster accuracy is 0.622; PC2 global ordering accuracy is 0.746, while within-cluster accuracy is 0.687. Across-cluster pairs are easier because large cluster-level offsets make many comparisons obvious.

Observed: cluster conditioning does improve prediction in the regression regime. PC1 oracle-cluster R2 improves over direct-axis R2 by 0.515; PC2 oracle-cluster R2 improves by 0.302. This means cluster identity carries substantial intercept/slope information even though within-cluster pairwise judgments are harder than global pairwise judgments.

Observed: cluster-prediction uncertainty is nontrivial. The text-to-cluster classifier reached 0.687 accuracy and 0.404 macro F1. Predicted-cluster conditioning preserves part of the oracle benefit for PC1 (0.351 R2 over direct), but only part for PC2 (0.104 R2 over direct). Hard cluster errors therefore erase much of the PC2 oracle benefit.

Inferred: cluster conditioning helps as a modeling interaction, not as evidence that axis position is easier to judge within a known cluster. PC1 remains a strong global convergence-pressure scale, but cluster context improves calibrated prediction. PC2 is more region-dependent: abstraction/developmental-immediacy has a global signal, yet its mapping onto PC2 depends substantially on coarse persona region.

## Judge-Rubric Design Recommendation

- PC1: use a direct axis judge when simplicity matters; use a hybrid direct-plus-cluster model when calibrated numeric prediction matters.
- PC2: use cluster-conditioned interpretation for analysis, but deployment-style forecasting should prefer soft-cluster or interaction features over hard predicted clusters.
- Oracle-cluster scores are appropriate for mechanistic interpretation; hard predicted-cluster deployment should report cluster accuracy because classifier errors materially reduce the benefit, especially for PC2.
