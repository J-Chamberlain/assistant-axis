# Provenance Registry

This registry is a fast lineage lookup for Paper 1.5 artifacts. Use it before running repository archaeology. It records where major artifacts came from, which model or agent authored them, what inputs they depend on, and which conclusions currently rely on them.

## claude_full_feature_matrix.csv

Artifact: Claude full latent-feature matrix, including Big Five-style scores and TF-IDF/SVD-derived features.
Location: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_full_feature_matrix.csv`
Created by: Claude-side feature analysis, then aligned into the shared benchmark by Codex.
Model used: Claude for feature generation; Codex/GPT-5.5 Standard for benchmark integration.
Source inputs: 273 common personas, canonical activation PCA3D target, Claude feature exports, semantic baseline features.
Generating script: `research/q2_stability/qwen/scripts/shared_latent_feature_benchmark.py` for local alignment.
Dependent analyses: shared benchmark, Big Five overlay visualization, hierarchical trait-procedural model, convergence status report.
Current status: Established feature source for Big Five-style overlays and shared benchmark comparisons.
Notes/caveats: Big Five scores are LLM-assigned features, not true psychological measurements. The matrix covers 273 personas; `coral_reef` and `devils_advocate` are absent from this benchmark feature source.

## geometry_viz_data.json

Artifact: Self-contained persona geometry data for the Plotly viewer.
Location: `research/visualizations/geometry_viz_data.json`
Created by: Codex/GPT-5.5 Standard via visualization scripts.
Model used: Script-author model GPT-5.5; target vectors are Qwen/Qwen3-32B Lu-style role vectors.
Source inputs: `downloads/hf_vectors/qwen-3-32b/role_vectors/`, `research/visualizations/cluster_assignments_full.json`, assistant-axis vector metadata, nearest-neighbor computations.
Generating script: `research/visualizations/scripts/build_geometry_viz.py`
Dependent analyses: `research/visualizations/persona_geometry_explorer.html`, Big Five overlay viewer, PCA/UMAP visual inspection.
Current status: Established visualization data source.
Notes/caveats: PCA/UMAP data are visualization coordinates, not new extraction outputs. PC1 explains 0.315954 variance and aligns with the assistant-axis vector at 0.802310 cosine in the current Qwen role-vector geometry.

## bigfive_geometry_overlay_data.json / .csv

Artifact: Persona-aligned Big Five overlay table for the Plotly viewer.
Location: `research/visualizations/bigfive_geometry_overlay_data.json`; `research/visualizations/bigfive_geometry_overlay_data.csv`
Created by: Codex/GPT-5.5 Standard.
Model used: `model_used: GPT-5.5` recorded in JSON and validation note.
Source inputs: `geometry_viz_data.json`, `claude_full_feature_matrix.csv`, `shared_persona_residual_rankings.csv`, `shared_benchmark_summary.csv`.
Generating script: One-time local merge performed by Codex in the 2026-05-29 visualization session.
Dependent analyses: Big Five visualization modes in `research/visualizations/persona_geometry_explorer.html`.
Current status: Established visualization overlay.
Notes/caveats: Per-persona Big Five predicted PC coordinates were not found in persisted benchmark outputs, so `predicted_pc1_from_bigfive`, `predicted_pc2_from_bigfive`, and `predicted_pc3_from_bigfive` are null. Big Five scores are missing for `coral_reef` and `devils_advocate`.

## shared_persona_residual_rankings.csv

Artifact: Per-persona residual ranking table across semantic, Codex retained, Big Five, and combined feature families.
Location: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_persona_residual_rankings.csv`
Created by: Codex/GPT-5.5 Standard.
Model used: Script-author and analysis model GPT-5.5 Standard; Claude features included as input.
Source inputs: shared benchmark feature matrices, canonical activation PCA3D target, five deterministic split assignments.
Generating script: `research/q2_stability/qwen/scripts/shared_latent_feature_benchmark.py`
Dependent analyses: Big Five overlay residual color mode, residual case selection, hierarchical and residual-manifold interpretation.
Current status: Established diagnostic artifact.
Notes/caveats: Residual ranks diagnose prediction error under feature models. They are not causal explanations of why a persona occupies a geometry region.

## shared_latent_feature_benchmark outputs

Artifact: Shared benchmark package comparing semantic baseline, Codex retained features, Claude Big Five, Claude full matrix, and combined features.
Location: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`
Created by: Codex/GPT-5.5 Standard, using Codex and Claude feature inputs.
Model used: Codex/GPT-5.5 Standard for script and analysis; Claude for Claude-side feature matrices.
Source inputs: canonical activation PCA3D coordinates, Claude cluster-cosine pseudo-PCA3D coordinates, semantic baseline features, Codex retained features, Claude Big Five/full feature matrices.
Generating script: `research/q2_stability/qwen/scripts/shared_latent_feature_benchmark.py`
Dependent analyses: convergence status, Big Five performance claim, visual overlay source selection, later hierarchical model.
Current status: Established apples-to-apples benchmark.
Notes/caveats: Cleanest current comparison uses 273 common personas and five deterministic Codex outer-loop splits. Big Five reaches canonical activation PCA3D R2 0.612979 vs semantic baseline 0.389397; Codex retained reaches 0.490090. Combined features do not beat Big Five on canonical activation PCA.

## hierarchical_trait_procedural_model outputs

Artifact: Two-stage trait-plus-procedural predictor of canonical activation PCA3D.
Location: `research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/`
Created by: Codex/GPT-5.5 Standard.
Model used: Analysis and script-author model GPT-5.5 Standard.
Source inputs: shared benchmark semantic controls, Claude Big Five-style features, selected Codex procedural/behavioral features, canonical activation PCA3D target, shared splits.
Generating script: `research/q2_stability/qwen/scripts/hierarchical_trait_procedural_model.py`
Dependent analyses: layered geometry interpretation, residual-manifold analysis baseline, findings ledger.
Current status: Provisional but replicated under the shared split/evaluation path.
Notes/caveats: Hierarchical model reaches R2 0.622 vs trait stage 0.613, a modest +0.009 increment. This supports a small local residual contribution from procedural features, not a strong standalone procedural ontology.

## residual_manifold_analysis outputs

Artifact: Third-layer diagnostic over residual structure after semantic, Big Five, and procedural modeling.
Location: `research/q2_stability/qwen/outputs/residual_manifold_analysis/`
Created by: Codex/GPT-5.5 Standard.
Model used: Analysis and script-author model GPT-5.5 Standard.
Source inputs: hierarchical model baseline, full no-label prompts, no-label semantic-neighborhood metadata, bridge/displacement metadata, residual histories, canonical activation PCA context.
Generating script: `research/q2_stability/qwen/scripts/residual_manifold_analysis.py`
Dependent analyses: residual-layer interpretation, developmental/liminal/collective high-residual hypotheses.
Current status: Provisional diagnostic.
Notes/caveats: Residual-manifold model reaches R2 0.632 vs hierarchical baseline 0.622. The improvement is small and should be treated as evidence for candidate residual regions, not a solved third-layer model.

## residual_svd_interpretation outputs

Artifact: Reconstruction and interpretation of Claude's TF-IDF SVD15 residual signal.
Location: `research/q2_stability/qwen/outputs/residual_svd_interpretation/`
Created by: Codex/GPT-5.5 Standard, reconstructing Claude's committed SVD15 result.
Model used: Claude produced the original residual-SVD result; Codex/GPT-5.5 Standard reconstructed and interpreted local components.
Source inputs: full no-label prompt corpus, Claude residual report/run script, canonical activation PCA3D target, sem+BigFive baseline.
Generating script: `research/q2_stability/qwen/scripts/residual_svd_interpretation.py`
Dependent analyses: lexical/register layer claim, Paper 1.5 layered geometry framing.
Current status: Provisional but strong predictive result.
Notes/caveats: Sem+BigFive+SVD15 reaches R2 0.707 vs sem+BigFive 0.613. SVD15 is an unsupervised text basis that may exploit prompt-corpus/register artifacts; it should be interpreted as lexical/register signal until distilled into human-readable features and retested.

## semantic topology outputs

Artifact: Semantic-only and semantic-vs-activation topology analyses.
Location: `research/assistant_axis_methodology/semantic_vs_activation_geometry/`, `research/assistant_axis_methodology/deep_semantic_topology_analysis.md`, `research/assistant_axis_methodology/semantic_geometry_standalone_interpretation.md`
Created by: Codex/GPT-5.5 Standard.
Model used: Analysis and script-author model GPT-5.5 Standard; local semantic methods only.
Source inputs: canonical role list, original prompts, no-label prompts, available activation cluster assignments, local semantic embeddings or TF-IDF/SVD fallback.
Generating scripts: `research/assistant_axis_methodology/scripts/compare_semantic_vs_activation_geometry.py`, `research/assistant_axis_methodology/scripts/deep_semantic_topology_analysis.py`
Dependent analyses: semantic-prior framing, no-label activation stress-test design, cluster-overlap analysis.
Current status: Established as prompt-space due diligence; activation implications remain bounded.
Notes/caveats: Semantic topology partially predicts activation topology and survives label removal, but activation geometry is not reducible to lexical semantics.

## trait replication outputs

Artifact: Codex-only constrained trait replication loop.
Location: `research/q2_stability/qwen/outputs/codex_trait_replication/`
Created by: Codex/GPT-5.5 Standard.
Model used: Analysis and script-author model GPT-5.5 Standard.
Source inputs: canonical activation PCA3D target, semantic baseline, Claude Big Five reference, five deterministic shared splits.
Generating script: `research/q2_stability/qwen/scripts/codex_trait_replication_loop.py`
Dependent analyses: evaluator/agent convergence discussion, Big Five robustness framing.
Current status: Negative/provisional replication.
Notes/caveats: Codex trait model reaches R2 0.398 vs semantic baseline 0.389 and far below Claude Big Five R2 0.613. This is weak positive trait signal, not a successful Big Five-level replication.

## procedural replication / Codex retained outputs

Artifact: Codex retained latent-feature and procedural/behavioral feature family outputs.
Location: `research/q2_stability/qwen/outputs/iterative_outer_loop/`, `research/q2_stability/qwen/outputs/latent_feature_framing_ablation/`, `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/codex_retained_features.csv`
Created by: Codex/GPT-5.5 Standard.
Model used: Analysis and script-author model GPT-5.5 Standard.
Source inputs: canonical activation PCA3D target, semantic baseline, role metadata, prompt-derived features, five deterministic split assignments.
Generating scripts: `research/q2_stability/qwen/scripts/iterative_latent_feature_outer_loop.py`, `research/q2_stability/qwen/scripts/latent_feature_framing_ablation.py`, `research/q2_stability/qwen/scripts/shared_latent_feature_benchmark.py`
Dependent analyses: procedural/operating-mode layer claim, convergence status, hierarchical model stage B.
Current status: Established as useful but weaker than Big Five for global geometry.
Notes/caveats: Codex retained features reach R2 0.490 vs semantic baseline 0.389 in the shared benchmark. They do not transfer to Claude's direct pseudo-PCA target over semantic baseline and should be framed as local/procedural explanatory candidates rather than the best global predictor.

## no-label prompt ablation outputs

Artifact: Label-removed prompt dataset and semantic comparison.
Location: `research/assistant_axis_methodology/no_label_prompt_ablation/`
Created by: Codex/GPT-5.5 Standard.
Model used: Codex/GPT-5.5 Standard for rewrites, validation, and analysis.
Source inputs: canonical role instruction JSONs, label-exposure audit, canonical system prompts and role list.
Generating scripts: `research/assistant_axis_methodology/scripts/rewrite_role_prompts_no_label_codex_gpt55.py`, `validate_no_label_prompt_ablation.py`, `compare_original_vs_no_label_prompt_semantics.py`
Dependent analyses: semantic topology, no-label activation stress-test design, methodology caveats.
Current status: Established prompt-space stress test input.
Notes/caveats: No-label prompts remove explicit role labels but still preserve behavioral descriptors, so they do not eliminate all role-identifying content.

## cluster overlap outputs

Artifact: Overlap analysis between activation-space clusters, original semantic prompt clusters, and no-label semantic prompt clusters.
Location: `research/assistant_axis_methodology/cluster_overlap_analysis.md` and supporting CSV/JSON files in `research/assistant_axis_methodology/`
Created by: Codex/GPT-5.5 Standard.
Model used: Analysis and script-author model GPT-5.5 Standard.
Source inputs: semantic-vs-activation geometry outputs, no-label prompt geometry outputs, activation-cluster mappings.
Generating script: `research/assistant_axis_methodology/scripts/cluster_overlap_analysis.py`
Dependent analyses: stable-anchor/bridge-role selection, no-label activation stress-test role selection.
Current status: Established overlap due diligence.
Notes/caveats: Structured partial overlap is the finding. Exact equality between semantic and activation clusters is not expected and should not be claimed.

## persona_geometry_explorer.html

Artifact: Interactive Plotly persona geometry viewer.
Location: `research/visualizations/persona_geometry_explorer.html`
Created by: Codex/GPT-5.5 Standard.
Model used: Script-author model GPT-5.5 Standard.
Source inputs: `geometry_viz_data.json`, `bigfive_geometry_overlay_data.json` embedded into HTML.
Generating script: Manual HTML/JS edits plus prior `build_geometry_viz.py` data generation.
Dependent analyses: visual inspection of PCA/UMAP geometry, cluster coloring, Big Five overlays, selection/lasso review.
Current status: Established visualization tool.
Notes/caveats: Visualization is self-contained and intentionally large. It is exploratory support, not a statistical test.
