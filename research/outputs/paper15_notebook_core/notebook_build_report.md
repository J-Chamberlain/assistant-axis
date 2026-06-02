# Paper 1.5 Notebook Build Report

Generated UTC: 2026-06-02T12:26:34+00:00
Notebook path: `research/notebooks/paper15_core_analysis_walkthrough.ipynb`

## Sections Created

- N00. Setup and Provenance
- N01. Public Geometry and Artifact Reconstruction
- N02. Cross-Model Scope and Caveats
- N03. PC1 Interpretation
- N04. PC2 Interpretation
- N05. PC3 Interpretation
- N06. Trait/Persona Relationship
- N07. Prediction-Improvement Sequence
- N08. Prompt-to-Geometry Forecasting Baseline
- N09. Main Visualization Tool
- N10. Summary of Claims, Confidence, and Next Tests

## Data Files Referenced

- `research/outputs/paper15_clean_repo_copy_plan/clean_repo_copy_plan.csv` — exists=True — Copy-plan artifact inventory and canonical status counts.
- `research/outputs/paper15_clean_repo_copy_plan/canonical_claims_traceability_table.csv` — exists=True — Traceability table for report-spine claims.
- `research/visualizations/geometry_viz_data.json` — exists=True — Public persona/trait geometry, Qwen role coordinates, clusters, and available model geometry.
- `research/outputs/prompt_artifact_inventory/role_prompt_artifact_index.csv` — exists=True — Role prompt artifact inventory.
- `research/outputs/prompt_artifact_inventory/trait_prompt_artifact_index.csv` — exists=True — Trait prompt artifact inventory.
- `research/outputs/role_rollout_artifact_audit/role_prompt_reconstruction_inventory.csv` — exists=True — Role 5x240 input reconstruction inventory.
- `research/outputs/cross_model_pc2_pc3_diagnostic/cross_model_pc_correlation_matrix.csv` — exists=True — Cross-model PC correlation matrix.
- `research/outputs/cross_model_pc2_pc3_diagnostic/cross_model_pc_best_matches.csv` — exists=True — Best matching PCs across models.
- `research/outputs/cross_model_cluster_topology/cross_model_cluster_similarity_metrics.json` — exists=True — Cross-model cluster topology metrics.
- `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_top_bottom.csv` — exists=True — Muted-PC1 PC2 extreme roles.
- `research/outputs/pc2_cluster_conditioned_extremes/pc2_diagnostic_roles_table.csv` — exists=True — PC2 diagnostic role table.
- `research/outputs/pc2_cluster_conditioned_extremes/pc2_expected_direction_checks.csv` — exists=True — PC2 expected-direction checks.
- `research/outputs/pc3_validation/pc3_validation_stats.json` — exists=True — PC3 perturbation/stabilization validation stats.
- `research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json` — exists=True — Trait-profile prediction of persona PCs.
- `research/outputs/trait_space_interpretation/trait_space_validation_stats.json` — exists=True — Trait-only PCA and trait/persona PC comparison.
- `research/outputs/prompt_to_geometry_forecasting/forecasting_results.json` — exists=True — Prompt-to-geometry forecasting result summary.
- `research/outputs/prompt_to_geometry_forecasting/forecasting_model_comparison.csv` — exists=True — Prompt-to-geometry model comparison.
- `research/visualizations/persona_geometry_explorer.html` — exists=True — Main Persona Geometry Explorer.

## Missing Files or Unresolved Dependencies

- None among required notebook input files.

## Placeholders

- Plot cells are guarded: figures are skipped when `matplotlib` is unavailable.
- The notebook uses standard-library tables instead of pandas DataFrames so it can run in a minimal Python kernel.
- H100 validation, prompt-battery generation, extraction-boundary diagnostics, and RunPod materials are intentionally deferred.

## Execution Status

- Execution method: `plain_python_exec_over_code_cells`
- Executed code cells: 12
- Error count: 0
- Jupyter execution: not attempted because `jupyter`, `nbformat`, and `nbclient` are not installed in this local Python environment.
