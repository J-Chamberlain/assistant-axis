# Proposed Clean Repo Tree

Recommended repo name: `assistant-axis-paper15-core`

```text
assistant-axis-paper15-core/
  README.md
  PROVENANCE.md
  REPORT_SPINE.md
  archive_index.md
  data/
    public/
      extraction_questions.jsonl
      roles/instructions/
      traits/instructions/                  # optional first pass
      prompts_and_questions_cards/
    processed/
      geometry_viz_data.json
      cluster_assignments_full.json
      bigfive_geometry_overlay_data.json
      bigfive_geometry_overlay_data.csv
  scripts/
    build_geometry_viz.py
    assign_clusters_by_centroid.py
    shared_latent_feature_benchmark.py
    hierarchical_trait_procedural_model.py
    residual_manifold_analysis.py
    residual_svd_interpretation.py
    pc3_perturbation_validation.py
  notebooks/
    01_public_data_and_geometry.ipynb
    02_stress_tests_and_stability.ipynb
    03_axis_interpretation.ipynb
    04_prediction_improvement_sequence.ipynb
  outputs/
    tables/
      prompt_artifact_inventory/
      role_rollout_artifact_audit/
      no_label_prompt_ablation/
      semantic_vs_activation_geometry/
      stress_tests/
      shared_latent_feature_benchmark/
      hierarchical_trait_procedural_model/
      residual_manifold_analysis/
      residual_svd_interpretation/
      pc3_validation/
      pc2_conditional_validation/
      cluster_conditioned_axis_tests/
      trait_persona_prediction/
      trait_space_interpretation/           # optional first pass
      prompt_to_geometry_forecasting/       # optional first pass
    figures/
  visualizations/
    persona_geometry_explorer.html
    bigfive_overlay_validation.md
  report/
    methodology/
    notes/
    drafts/
    references/
```

No files should be copied until the user reviews and approves the plan.
