# PC2 Trait-Profile Inventory

- Startup status: verified by raw GitHub startup files with cache-busted `curl`.
- Geometry source: `research/visualizations/geometry_viz_data.json`
- Trait-profile source: `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`
- Prior trait stats source: `research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json`
- Optional prior PC2 sources: `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_top_bottom.csv`, `research/outputs/pc2_cluster_conditioned_extremes/pc2_diagnostic_roles_table.csv`
- Source model: `Qwen/Qwen3-32B`
- Geometry metadata `model_used`: `GPT-5.5`. This is project metadata, not the source model for the public role vectors.
- Trait/profile model: `Qwen/Qwen3-32B`
- Trait/profile layer: `48`
- Trait score meaning: `raw activation-space cosine between mean role and mean trait vectors`
- Stored-vector pooling note: `mean over 64 stored vectors per persona/trait, then L2 normalize`
- Joined role count: 275
- Trait count: 240
- Cluster count: 7

The joined matrix stores Qwen role PCA coordinates plus the 240-dimensional persona-by-trait cosine profile. These trait scores are activation-space similarity features, not direct human ratings or causal psychological labels.
