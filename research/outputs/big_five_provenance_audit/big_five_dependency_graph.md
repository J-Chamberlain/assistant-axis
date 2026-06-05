# Big Five Dependency Graph

## Observed Graph

```text
Qwen/Gemma role vectors -> activation cluster assignment -> visualizations/deep_analysis.py cluster_bases -> visualizations/bigfive_profiles.json
role names -> visualizations/deep_analysis.py role-specific adjustments -> visualizations/bigfive_profiles.json
visualizations/bigfive_profiles.json -> Claude branch claude_feature_matrix.csv -> shared_latent_feature_benchmark.py -> claude_bigfive_features.csv / claude_full_feature_matrix.csv
geometry_viz_data.json + claude_full_feature_matrix.csv + shared_persona_residual_rankings.csv -> bigfive_geometry_overlay_data.{csv,json} -> persona_geometry_explorer.html
Qwen role vectors -> geometry_viz_data.json -> role PCA geometry -> persona_geometry_explorer.html
Qwen role vectors + Qwen trait vectors -> trait profile matrix / trait-region overlays -> persona_geometry_explorer.html
```

## Actual Dependencies

| From | To | Dependency type | Evidence |
|---|---|---|---|
| Role geometry / role vectors | Activation cluster labels | Actual | `visualizations/deep_analysis.py` calls `assign_cluster_labels(roles, role_tensor[:, DEFAULT_LAYER, :])`. |
| Activation cluster labels | Big Five scores | Actual | `build_bigfive_profile(role, cluster_label)` sets cluster-specific Big Five base values. |
| Role names | Big Five scores | Actual | `build_bigfive_profile` applies role-name-specific additive adjustments. |
| Trait vectors | Big Five scores | Not found | No Big Five scoring script reads trait vectors or trait profiles. |
| Trait profiles | Big Five scores | Not found | Big Five source predates/currently does not load trait-profile matrix. |
| Big Five scores | Big Five overlay | Actual | Overlay data copies five score columns from `claude_full_feature_matrix.csv`. |
| Role PCA geometry | Big Five overlay | Actual for visualization join, not score generation | Overlay joins scores to PC coordinates and residuals for display. |
| Big Five scores | Role PCA geometry | No | PCA coordinates are from activation vectors, not Big Five scores. |

## Classification

Big Five is **partially dependent on activation geometry** through activation-derived cluster labels, and semantically dependent through role names. It is **not derived from the 240-trait vector/profile system** and is **not an activation-space Big Five vector construction**.
