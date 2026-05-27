# Semantic vs Activation Geometry Comparison

## Research Question

This study compares three prompt-space semantic geometries with the available activation-space references: role names, original label-exposed prompts, and no-label rewritten prompts. The goal is to test how much activation-space clustering is recoverable from semantic structure alone and whether label removal preserves prompt-space topology.

## Data Sources

- `role_list`: `data/roles/role_list.json`
- `role_instruction_dir`: `data/roles/instructions`
- `no_label_prompts`: `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`
- `no_label_validation`: `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_prompt_ablation_validation.json`
- `prior_no_label_comparison`: `research/assistant_axis_methodology/no_label_prompt_ablation/original_vs_no_label_semantic_comparison.json`
- `activation_cluster_labels`: `visualizations/full_ranking.csv`
- `gemma_directionality`: `research/cluster_analysis/gemma_cluster_directionality.csv`
- `qwen_directionality`: `research/cluster_analysis/qwen_cluster_directionality.csv`

Available activation references include `visualizations/full_ranking.csv` cluster labels and the prior Gemma/Qwen cluster-directionality CSVs. No full pairwise activation distance matrix was reconstructed or fabricated.

## Method

No local sentence-transformers, scikit-learn, or matplotlib installation was available. The analysis therefore uses offline TF-IDF with unigrams and bigrams plus NumPy SVD, deterministic k-means, nearest-neighbor preservation, ARI/NMI cluster agreement, and distance-matrix correlations. UMAP and t-SNE were not run.

## Headline Metrics

- Role-name k=7 ARI vs activation labels: 0.010
- Role-name+description k=7 ARI vs activation labels: 0.023
- Original-prompt k=7 ARI vs activation labels: 0.111
- No-label-prompt k=7 ARI vs activation labels: 0.130
- Original vs no-label distance correlation: 0.956
- Original vs no-label nearest-neighbor preservation: 0.858

## Analysis Questions

### 1_role_names_alone

Role names alone recover weak but nonzero topology relative to activation labels; k=7 ARI is 0.010. Name-only geometry is much thinner than prompt geometry.

### 2_original_prompts_vs_role_names

Original prompts recover more structure than role names alone when compared to activation centroid-profile distances and richer nearest-neighbor neighborhoods; adding role descriptions also improves over names alone.

### 3_no_label_close_to_original

No-label prompt geometry remains close to original prompt geometry: distance correlation 0.956 and nearest-neighbor preservation 0.858.

### 4_best_predictor_of_activation

Best semantic predictor of available Gemma activation centroid-profile distances is no_label_prompt with correlation 0.230.

### 5_seven_clusters_recoverable

Seven-cluster structures are only partially recoverable from semantic space. Prompt-space k=7 clusters have low-to-modest ARI against activation labels, so semantic topology and activation clustering overlap but are not identical.

### 6_most_unstable_roles

See `role_displacement_metrics.csv` and `most_unstable_roles` in the summary JSON; instability is concentrated where label removal or name-to-prompt expansion changes nearest neighbors.

### 7_semantically_intrinsic_clusters

Clusters with higher within-cluster prompt cosine are more semantically intrinsic; see `cluster_semantic_intrinsic` for per-cluster values. Low values suggest activation-specific or heterogeneous organization.

### 8_assistant_vs_theatrical

Assistant-adjacent roles are semantically explicit in prompts but can be behaviorally low-yield in activation extraction; theatrical roles tend to remain semantically vivid after label removal. This supports an interaction between semantic priors and model-specific assistant-basin organization.

### 9_activation_geometry_interpretation

Available evidence supports partial preservation plus reorganization: activation geometry preserves some semantic topology, but it sharpens, compresses, or reorganizes it into model-specific cluster structure rather than simply copying prompt semantics.

## Cluster-Level Semantic Intrinsicness

| Activation cluster | n | Original within cosine | No-label within cosine | Original-to-no-label role cosine |
|---|---:|---:|---:|---:|
| `editorial` | 5 | 0.338 | 0.393 | 0.993 |
| `trickster_chaos` | 7 | 0.180 | 0.205 | 0.994 |
| `combative_iconoclast` | 8 | 0.164 | 0.190 | 0.997 |
| `grounded_social` | 45 | 0.114 | 0.158 | 0.991 |
| `other` | 22 | 0.105 | 0.149 | 0.991 |
| `mythic_spiritual` | 61 | 0.100 | 0.152 | 0.985 |
| `procedural_professional` | 127 | 0.082 | 0.144 | 0.983 |

## Interpretation

The comparison supports partial preservation plus reorganization. Semantic topology is not irrelevant: role descriptions and prompts recover weak-to-modest agreement with activation labels, and no-label prompt geometry remains very close to original prompt geometry in continuous distance structure. At the same time, agreement with activation clusters is limited and hard semantic cluster assignments are unstable, so activation-space geometry should not be described as just semantics.

The most defensible interpretation is that the activation geometry reflects an interaction between semantic priors in the elicitation corpus and model-specific representational organization. Label-exposed prompts contribute to prompt-space organization, but no-label rewrites preserve enough continuous topology to justify a small activation-space stress test.

## Limitations

This is a prompt-space semantic analysis, not a new activation experiment. TF-IDF/SVD is lexical and cannot fully capture paraphrastic equivalence. Activation comparison uses available cluster labels and centroid-proximity profiles, not a full published pairwise activation matrix. The role inventory is a constructed semantic corpus and should not be treated as a representative sample of humanity.

## Recommended Next Experiment

Run a small no-label activation-space stress test on a mixed role set. Include trickster as a high-yield theatrical positive control, editor as an assistant-adjacent failure case, and one or two intermediate roles. Compare no-label extracted vectors to Lu reference vectors and original-prompt extraction behavior before scaling.
