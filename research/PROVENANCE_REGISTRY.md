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
Notes/caveats: Big Five scores are not true psychological measurements. The 2026-06-05 audit traces the current Big Five source back to `visualizations/bigfive_profiles.json`, generated from activation-derived cluster base scores plus role-name heuristic adjustments. The matrix covers 273 personas; `coral_reef` and `devils_advocate` are absent from this benchmark feature source.

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
Current status: Established visualization overlay, but evidence status is heuristic/secondary.
Notes/caveats: Per-persona Big Five predicted PC coordinates were not found in persisted benchmark outputs, so `predicted_pc1_from_bigfive`, `predicted_pc2_from_bigfive`, and `predicted_pc3_from_bigfive` are null. Big Five scores are missing for `coral_reef` and `devils_advocate`. Current overlay scores are partially activation-dependent because their underlying source uses activation-derived cluster labels as base scores.

## big_five_provenance_audit outputs

Artifact: Provenance and methodology audit of the Big Five overlays used in the persona geometry explorer.
Location: `research/outputs/big_five_provenance_audit/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, or new activations were run.
Source inputs: `research/REPO_NAVIGATION.md`, `research/REPO_FILE_INDEX.csv`, `research/RAW_URL_INDEX.md`, `research/PROVENANCE_REGISTRY.md`, `research/RESEARCH_INDEX.md`, `research/RESEARCH_STATE.md`, `research/visualizations/bigfive_geometry_overlay_data.csv`, `research/visualizations/bigfive_overlay_validation.md`, `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_full_feature_matrix.csv`, `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_bigfive_features.csv`, `visualizations/bigfive_profiles.json`, `visualizations/psychology_profiles.csv`, `visualizations/deep_analysis.py`, and Claude branch `myfork/claude/persona-inventory-topology-4qp10` feature-loop artifacts.
Generating script: Direct audit with a small local CSV/JSON diagnostic; output includes `big_five_pc2_diagnostics.json` and `.csv`.
Dependent analyses: Future Big Five overlay redesign, PC2 visual interpretation, trait-region overlay comparison, and Paper 1.5 evidential-independence caveats.
Current status: Complete provenance audit.
Notes/caveats: The audit classifies the current Big Five overlay as partially dependent on activation geometry because `visualizations/deep_analysis.py` uses activation-derived cluster labels as Big Five base scores before role-name heuristic adjustments. It found no dependency on the 240-trait vector/profile matrix. Recommendation: rebuild any evidence-bearing Big Five layer; retain the current overlay only if relabeled as a heuristic cluster-conditioned semantic summary.

## same-space activation-derived Big Five overlay outputs

Artifact: Same-space Big Five overlay built directly from released role and trait activation vectors.
Location: `research/outputs/same_space_big_five_overlay/`
Created by: Codex/GPT-5.5.
Model used: Script-author and analysis model GPT-5.5; no model APIs, pods, GPUs, or new activations were run.
Source inputs: released Qwen/Qwen3-32B, Llama-3.3-70B, and Gemma-2-27B role and trait vectors under `downloads/hf_vectors/{qwen-3-32b,llama-3.3-70b,gemma-2-27b}/`; trait vocabulary in `data/traits/trait_list.json`; cross-model role coordinates and clusters in `research/outputs/cross_model_cluster_topology/per_model_cluster_assignments.csv`; legacy heuristic overlay data in `research/visualizations/bigfive_geometry_overlay_data.csv` used only for descriptive continuity comparison; and prior provenance caveats in `research/outputs/big_five_provenance_audit/` and `research/outputs/trait_profile_provenance_audit/`.
Generating script: `research/outputs/same_space_big_five_overlay/run_same_space_big_five_overlay.py`.
Dependent analyses: Future evidence-bearing Big Five visualization layers, Paper 1.5 trait-overlay caveats, Qwen/Llama/Gemma same-space trait-vector inspection, and possible replacement or relabeling of the old heuristic Big Five explorer overlay.
Current status: Active same-space evidence layer.
Notes/caveats: Each Big Five direction is a predeclared positive-minus-negative facet composite over available released trait vectors, then applied by cosine projection to released role vectors. This is activation-derived trait-vector projection, not independent psychometric rating, human judgment, or behavioral validation. The old heuristic Big Five overlay is retained only as a descriptive comparison and should not be used as source evidence for this layer.

## pc2_muted_pc1_extremes outputs

Artifact: PC2 extremes inspection after muting PC1 to the central percentile band.
Location: `research/outputs/pc2_muted_pc1_extremes/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, or new activations were run.
Source inputs: `research/visualizations/geometry_viz_data.json`.
Generating script: `research/outputs/pc2_muted_pc1_extremes/run_pc2_muted_pc1_extremes.py`
Dependent analyses: PC2 interpretation language, future PC1-controlled matched-pair rater diagnostics, Paper 1.5 axis-interpretation caveats.
Current status: Descriptive coordinate-inspection diagnostic.
Notes/caveats: The selected central 45th-55th percentile PC1 band contains 27 roles with PC1 bounds -2.747954 to 6.917357. High PC2 roles are mostly situated/social/reactive; low PC2 roles are mostly abstract/integrative/systemic/procedural. The band is small and cluster-skewed, so this refines rather than finalizes PC2 interpretation.

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
Source inputs: `geometry_viz_data.json`, `bigfive_geometry_overlay_data.json`, `trait_region_overlay_data.json`, `research/outputs/qwen_pc2_trait_region_overlay/qwen_pc1_pc2_trait_region_cells.csv`, and `research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv`.
Generating script: Manual HTML/JS edits plus prior `build_geometry_viz.py` data generation and `research/visualizations/run_integrate_trait_regions_into_explorer.py` for the native trait-region overlay mode.
Dependent analyses: visual inspection of PCA/UMAP geometry, cluster coloring, Big Five overlays, selection/lasso review, and PC1 x PC2 local trait-enrichment inspection.
Current status: Established visualization tool with native trait-region overlay mode.
Notes/caveats: Visualization is self-contained and intentionally large. The trait-region overlay is exploratory support, not a statistical test. Trait labels are same-space Qwen activation-vector cosine enrichments with mixed provenance and should not be described as independent psychological ratings.

## persona geometry trait-region overlay integration

Artifact: Native PC1 x PC2 trait-region overlay mode inside the Persona Geometry Explorer.
Location: `research/visualizations/persona_geometry_explorer.html`, with companion data/report/script under `research/visualizations/trait_region_overlay_data.json`, `trait_region_overlay_integration_report.md`, and `run_integrate_trait_regions_into_explorer.py`.
Created by: Codex/GPT-5.5 Standard.
Model used: Script-author and integration model GPT-5.5 Standard.
Source inputs: canonical role geometry in `research/visualizations/geometry_viz_data.json`, prior 5 x 3 quantile cells in `research/outputs/qwen_pc2_trait_region_overlay/qwen_pc1_pc2_trait_region_cells.csv`, and joined Qwen role-by-trait profile matrix in `research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv`.
Generating script: `research/visualizations/run_integrate_trait_regions_into_explorer.py`.
Dependent analyses: PC2 visual inspection, PC1-band-relative trait-region review, Paper 1.5 exploratory visualization, future axis interpretation figures.
Current status: Active integrated visualization mode.
Notes/caveats: Quantile bands are the stable default because they control cell counts. Fixed explorer-grid regions are descriptive only and sparse cells are flagged. Color semantics are separated: point color indicates selected point overlay, label text indicates locally enriched traits, and label border/chip indicates dominant trait-region cluster when used.

## multimodel ordered trait-region viewer

Artifact: Multi-model ordered-axis trait-region viewer for Qwen, Llama, and Gemma.
Location: `research/outputs/multimodel_ordered_trait_region_viewer/`.
Created by: Codex/GPT-5.5.
Model used: Script-author and analysis model GPT-5.5.
Source inputs: released role and trait vectors under `downloads/hf_vectors/qwen-3-32b/`, `downloads/hf_vectors/llama-3.3-70b/`, and `downloads/hf_vectors/gemma-2-27b/`; Qwen reference geometry and clusters from `research/visualizations/geometry_viz_data.json`; prior Qwen overlay method and caveats from `research/outputs/qwen_pc2_trait_region_overlay/`; trait-profile provenance caveats from `research/outputs/trait_profile_provenance_audit/`.
Generating script: `research/outputs/multimodel_ordered_trait_region_viewer/run_multimodel_ordered_trait_region_viewer.py`.
Dependent analyses: cross-model PC-axis visual inspection, ordered-axis PC1/PC2 and PC2/PC1 comparison, PC2/PC3 exploratory trait-region review, future Paper 1.5 visualization selection.
Current status: Active exploratory visualization and data bundle.
Notes/caveats: The selected x-axis defines the conditioning baseline, so reversed views are distinct analyses. Qwen uses canonical coordinates from `geometry_viz_data.json`; Llama and Gemma coordinates are recomputed from layer-mean role vectors and sign-oriented to the Qwen reference. Trait labels are same-space activation-vector cosine enrichments, not independent psychological ratings or solved PC interpretations. Quantile views are stable defaults; fixed-grid views are descriptive and sparse cells are flagged.

## blinded axis rubric validation outputs

Artifact: Coordinate-blind no-label prompt rubric validation for PC1, PC2, and PC3 interpretations.
Location: `research/q2_stability/qwen/outputs/blinded_axis_rubric_validation/`
Created by: Codex/GPT-5.5.
Model used: Script-author and analysis model GPT-5.5; numeric scoring was deterministic local code, not model inference.
Source inputs: `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl` and `research/visualizations/geometry_viz_data.json`.
Generating script: `research/q2_stability/qwen/scripts/blinded_axis_rubric_validation.py`
Dependent analyses: PC1/PC2/PC3 interpretation confidence, future blinded rater study design, Paper 1.5 methodology caveats.
Current status: Provisional validation screen.
Notes/caveats: Uses all five no-label prompts for all 275 personas and excludes persona names/PCA coordinates during scoring. It is a lexical-semantic proxy, not a true independent human or LLM blinded-rating study. Target correlations were positive but modest: PC1 r=0.247, PC2 r=0.224, PC3 r=0.349; matched-pair validation was weak.

## blinded axis rater study outputs

Artifact: Reading-based blinded PCA-axis rater study over anonymized persona dossiers.
Location: `research/q2_stability/qwen/outputs/blinded_axis_rater_study/`
Created by: Codex/GPT-5.5.
Model used: Codex/GPT-5.5 as rater, analysis model, and script-author model.
Source inputs: `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`, `research/visualizations/geometry_viz_data.json`, and corpus inventory over local response/prompt sources.
Generating script: `research/q2_stability/qwen/scripts/blinded_axis_rater_study.py`
Dependent analyses: PC1/PC2/PC3 interpretation confidence, Paper 1.5 axis language, future independent-rater study design.
Current status: Provisional but stronger than the lexical-proxy screen.
Notes/caveats: Full 275-persona rollout-response corpus was not found locally; dossiers use all five no-label rewritten prompts per persona. Persona names, PCA coordinates, clusters, Big Five scores, residuals, and prior labels were hidden from the rater. This is Codex-as-rater rather than independent human or second-model annotation. Target correlations were PC1 r=0.558, PC2 r=0.373, PC3 r=0.690; matched-pair validation was PC1 75%, PC2 100%, PC3 95%.

## pc2 conditional validation outputs

Artifact: Conditional PC2 validation after approximate PC1 control.
Location: `research/q2_stability/qwen/outputs/pc2_conditional_validation/`
Created by: Codex/GPT-5.5 High Reasoning.
Model used: Analysis and script-author model GPT-5.5 High Reasoning; candidate scores reused from the prior Codex/GPT-5.5 blinded rater study.
Source inputs: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv` and `research/q2_stability/qwen/outputs/blinded_axis_rater_study/axis_rater_scores.csv`.
Generating script: One-time local analysis for the 2026-05-30 conditional PC2 validation session.
Dependent analyses: PC2 interpretation language, matched-pair follow-up design, Paper 1.5 axis-interpretation confidence.
Current status: Provisional but strongest current PC2 disentanglement result.
Notes/caveats: Uses 273 common personas and 10 PC1 percentile bands. The ratings are prompt-dossier based rather than full rollout-response based. Abstraction is the strongest residual PC2 predictor after PC1 band control (r=-0.618, R2=0.382); coherent action is weaker (r=+0.427, R2=0.182); uncertainty exposure fails (r=-0.026, R2=0.001).

## extraction equivalence audit outputs

Artifact: Source/artifact audit comparing original/local Assistant Axis extraction code, prior adaptive trickster/editor extraction, and the H100 percentile-edge extraction runner.
Location: `research/outputs/extraction_equivalence_audit/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, or new activations were run.
Source inputs: `pipeline/2_activations.py`, `assistant_axis/internals/activations.py`, `assistant_axis/internals/spans.py`, `assistant_axis/internals/conversation.py`, `assistant_axis/pca.py`, `research/q2_stability/qwen/scripts/phase1_inference_only_v4.py`, `research/q2_stability/qwen/scripts/phase1_inference_only_editor.py`, `research/q2_stability/qwen/outputs/paper1_5/`, `research/outputs/h100_percentile_edge_validation/`, and `research/outputs/h100_diagnostic_followups/`.
Generating script: `research/outputs/extraction_equivalence_audit/run_extraction_equivalence_audit.py`
Dependent analyses: H100 D01 diagnostic status, forecast-observed anomaly interpretation, decision whether to calibrate immediately or first run a hook-vs-hidden-states equivalence test.
Current status: Partial methodological resolution; D01 remains `in_progress`.
Notes/caveats: Projection, response-token mean pooling, model identity, and prior hook-based trickster replication are verified. The prior trickster score>=2 vector matched the downloaded trickster vector at cosine 0.957557, and H100 PCA reproduction max error was 1.207e-06. Activation-site equivalence remains unresolved because source/prior adaptive extraction uses forward hooks on `model.model.layers[48]`, while H100 validation used `out.hidden_states[48]`.

## public-source extraction equivalence audit outputs

Artifact: Public-source audit of whether H100 `outputs.hidden_states[48]` extraction is equivalent to the original Assistant Axis Qwen layer-48 hook convention.
Location: `research/outputs/public_source_extraction_equivalence/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, or new activations were run.
Source inputs: Official Assistant Axis source files under `pipeline/` and `assistant_axis/`, Hugging Face `lu-christina/assistant-axis-vectors` dataset metadata, Hugging Face `belmore/assistant-axis-vector-prompts` metadata, Qwen/Qwen3-32B config metadata, Transformers Qwen3 4.51.0 source semantics, prior trickster/editor adaptive extraction scripts, current H100 runner, and the earlier extraction-equivalence audit.
Generating script: `research/outputs/public_source_extraction_equivalence/run_public_source_extraction_equivalence_audit.py`
Dependent analyses: D01 diagnostic status, decision whether H100 PC2/PC3 anomalies can be interpreted behaviorally, and whether to rerun H100 extraction with a corrected boundary.
Current status: Public-source mismatch likely; D01 is open pending a tiny hook-vs-hidden-states confirmation test.
Notes/caveats: Official/prior extraction hooks `model.model.layers[48]` and captures decoder layer-48 post-MLP residual output. Public Transformers/Qwen3 semantics indicate `hidden_states[48]` is the input to decoder layer 48 / output after layer 47, while the layer-48 hook output likely corresponds to `hidden_states[49]`. PCA reproduction max error 1.207e-06 remains valid for projection-basis correctness only.

## role rollout artifact audit outputs

Artifact: Public/local audit of original Assistant Axis role-vector rollout inputs, generated-response availability, judge-score availability, retained-filter availability, and the remembered "64" count.
Location: `research/outputs/role_rollout_artifact_audit/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, activations, or response generation were run.
Source inputs: Official Assistant Axis paper/arXiv, official GitHub `data/roles/instructions/`, `data/extraction_questions.jsonl`, `pipeline/`, `assistant_axis/generation.py`, Hugging Face `lu-christina/assistant-axis-vectors`, Hugging Face `belmore/assistant-axis-vector-prompts`, local prompt artifact inventory, local extraction-equivalence audit, local trickster/editor adaptive extraction artifacts, `research/RESEARCH_STATE.md`, and `research/FINDINGS_LEDGER.md`.
Generating script: `research/outputs/role_rollout_artifact_audit/run_role_rollout_artifact_audit.py`
Dependent analyses: Revised instance-level prompt-to-centroid forecasting design, successful-rollout-only dataset feasibility, and correction of earlier "64-row cap" language.
Current status: Established public-data boundary: intended inputs are reconstructable; original generated responses, judge scores, and retained masks are not public.
Notes/caveats: The intended 1,200 combinations per role are reconstructable as 5 positive role instructions x 240 extraction questions. Exact token-level prompts depend on tokenizer/chat-template/runtime version. The remembered "64" is resolved as Qwen layer count in `[64,5120]` released vectors plus local adaptive-extraction sample/count usage, not as a public original retained-response count.

## within-role displacement design outputs

Artifact: Reusable design packet for a user-selected one-role within-role displacement study.
Location: `research/outputs/within_role_displacement_design/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activations, or response generation were run.
Source inputs: `data/roles/instructions/*.json`, `data/extraction_questions.jsonl`, `research/visualizations/geometry_viz_data.json`, `research/outputs/role_rollout_artifact_audit/`, and `research/outputs/prompt_artifact_inventory/`. Requested method-card files under `/mnt/data/` were not present.
Generating script: `research/outputs/within_role_displacement_design/run_within_role_displacement_design.py`
Dependent analyses: Target-role selection, manual/LLM-assisted instruction/question displacement scoring, selected-role 1,200-input reconstruction, and later corrected-hook within-role GPU displacement analysis after D01/T01 is resolved.
Current status: Established design artifact; target role remains user-selected.
Notes/caveats: The packet inventories 275 non-default roles with five positive instructions each and 240 shared questions. It defines centroid-relative displacement rubrics for PC1/PC2/PC3 and provides blank scoring templates. It does not score items, choose a target role, generate responses, extract activations, or overcome the public-data absence of original response-level judge scores and retained masks.

## positive PC2 pilot candidate selection outputs

Artifact: Positive-PC2 edge role shortlist for the first two-persona activation-cloud GPU pilot with playwright.
Location: `research/outputs/positive_pc2_pilot_candidate_selection/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activations, or response generation were run.
Source inputs: `research/visualizations/geometry_viz_data.json` and `data/roles/instructions/*.json`.
Generating script: `research/outputs/positive_pc2_pilot_candidate_selection/run_positive_pc2_candidate_selection.py`
Dependent analyses: User selection of the second persona for the first activation-cloud pilot after T01/D01 extraction-boundary verification.
Current status: Planning artifact awaiting user selection.
Notes/caveats: Preferred filter found 15 valid candidates using PC2 percentile >= 85 and PC1 percentile 40-75, so no fallback was needed. Primary shortlist is `amateur`, `influencer`, `newlywed`, `graduate`, and `patient`; alternates are `celebrity`, `divorcee`, `parent`, `retiree`, and `student`. This does not establish activation movement and should not be treated as empirical validation.

## a100 two-role activation cloud pilot outputs

Artifact: Staged GPU boundary verification and two-role response activation-cloud pilot for amateur and playwright.
Location: `research/outputs/a100_two_role_activation_cloud_pilot/`
Created by: Codex/GPT-5.5.
Model used: Qwen/Qwen3-32B for response generation and activation extraction; Codex/GPT-5.5 for script authoring, orchestration, analysis, and reporting.
Source inputs: `research/visualizations/geometry_viz_data.json`, `data/roles/instructions/amateur.json`, `data/roles/instructions/playwright.json`, `data/extraction_questions.jsonl`, and `downloads/hf_vectors/qwen-3-32b/role_vectors/*.pt`.
Generating script: `research/outputs/a100_two_role_activation_cloud_pilot/run_a100_two_role_activation_cloud_pilot.py`
Dependent analyses: D01/T01 extraction-boundary closeout, response-state uncertainty/T04 analysis, offline judge filtering for role-expression quality, and future region/distribution-level forecasting calibration.
Current status: Established pilot output; pod outputs were copied back and checksummed locally before termination.
Notes/caveats: RunPod pod `eu6ub11lshcyze` used an A100-SXM4-80GB at $1.49/hr. Boundary test showed `model.model.layers[48]` hook output matches `outputs.hidden_states[49]`, not `hidden_states[48]`. Stage 2 used direct hook extraction and generated 60 responses per role. Published centroids were near all-response centroids, but individual response clouds were broad; this supports distribution-level rather than exact single-response point-coordinate forecasting. Raw generated responses are preserved for later judge filtering; no judge API was called in this GPU task.

## a100 activation cloud posthoc analysis outputs

Artifact: Local posthoc analysis of amateur/playwright activation-cloud shape, bootstrap sample-size convergence, and GPT-4.1 judge-filter preparation.
Location: `research/outputs/a100_activation_cloud_posthoc_analysis/`
Created by: Codex/GPT-5.5.
Model used: Codex/GPT-5.5 for script authoring and local analysis; GPT-4.1 for role-expression judging at temperature 0 in the completed follow-up judge run.
Source inputs: `research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv`, `activation_cloud_summary_by_role.csv`, `activation_cloud_covariance_by_role.json`, `activation_cloud_distance_stats.json`, `judge_input_responses.jsonl`, and `boundary_test_report.md`.
Generating scripts: `research/outputs/a100_activation_cloud_posthoc_analysis/run_a100_activation_cloud_posthoc_analysis.py` and `research/outputs/a100_activation_cloud_posthoc_analysis/run_gpt41_judge_filter_resume.py`
Dependent analyses: Score==3 outlier inspection, rejected near-centroid response review, instruction/question-effect analysis, sample-size planning for future activation-cloud roles, and decision whether response-state forecasting should target role-conditioned distributions rather than exact single-response coordinates.
Current status: Cloud shape, bootstrap, GPT-4.1 scoring, and judge-filtered cloud analysis complete.
Notes/caveats: No GPU, pod, activation extraction, or response generation occurred in the posthoc analysis. The first judge attempt hit HTTP 429 quota and wrote a sanitized failure record, later removed after successful scoring; the completed judge run scored all 120 responses. The scripts load `OPENAI_API_KEY` from the environment or `~/.openai_api_key` without logging or committing secrets. Bootstrap estimates use unfiltered response clouds and may underestimate raw generations needed after judge filtering. Filtering reduced volume and mean response distance but moved centroids farther from the published role vectors, so the result is mixed rather than a simple sharpening toward the published centroid.

## a100 activation cloud visualization and judge compare outputs

Artifact: Standalone visualization package and judge-model comparison attempt for the amateur/playwright activation-cloud pilot.
Location: `research/outputs/a100_activation_cloud_visualization_and_judge_compare/`
Created by: Codex/GPT-5.5.
Model used: Codex/GPT-5.5 for script authoring, visualization, and local analysis; GPT-5.5 API availability was checked but no GPT-5.5 judge scoring was run because the required temperature-0 configuration was rejected by the API.
Source inputs: `research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv`, `research/outputs/a100_two_role_activation_cloud_pilot/judge_input_responses.jsonl`, `research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv`, `research/outputs/a100_activation_cloud_posthoc_analysis/judge_filtered_cloud_summary_by_role.csv`, `research/outputs/a100_activation_cloud_posthoc_analysis/judge_filtered_centroid_shifts.csv`, `research/outputs/a100_activation_cloud_posthoc_analysis/cloud_covariance_eigendecomp.json`, and `research/visualizations/geometry_viz_data.json`.
Generating script: `research/outputs/a100_activation_cloud_visualization_and_judge_compare/run_cloud_viz_judge_suite.py`
Dependent analyses: Interactive inspection of score==3 outliers, instruction/question effects, future viewer integration, and future judge-model sensitivity if a deterministic or explicitly default-temperature comparison protocol is approved.
Current status: Visualization package complete; GPT-5.5 comparison skipped under preregistered temperature-0 constraint.
Notes/caveats: The main geometry viewer was not modified. The standalone viewer uses Plotly from CDN and embeds a compact data bundle. GPT-5.5 appears in the local model list, but the chat-completions API rejected `temperature=0` for that model and only supports default temperature, so no apples-to-apples GPT-4.1-vs-GPT-5.5 judge comparison was produced.

## activation cloud suite tool scaffold

Artifact: Reusable no-GPU activation-cloud analysis scaffold for future persona-cloud pilots.
Location: `research/tools/activation_cloud_suite/`
Created by: Codex/GPT-5.5.
Model used: Codex/GPT-5.5 for tool scaffold and documentation.
Source inputs: Generalized from the A100 amateur/playwright pilot and posthoc analysis outputs.
Generating script: `research/outputs/a100_activation_cloud_visualization_and_judge_compare/run_cloud_viz_judge_suite.py`
Dependent analyses: Future persona activation-cloud pilots after GPU extraction, judge filtering, covariance/cloud-shape inspection, and viewer generation.
Current status: Scaffolded; the A100 worked-example script remains the reference implementation.
Notes/caveats: The current suite runner is a lightweight config loader/stub, not a fully factored library. Future pilots should either reuse the worked-example script or promote its functions into the tool package before relying on the suite as a stable interface.

## GPT-5.5 judge and outlier follow-up outputs

Artifact: GPT-5.5 default-temperature judge comparison and score==3/instruction/question follow-up analysis for the amateur/playwright activation clouds.
Location: `research/outputs/gpt55_judge_and_outlier_followup/`
Created by: Codex/GPT-5.5.
Model used: GPT-5.5 through the OpenAI API for role-expression judging at model-default temperature; Codex/GPT-5.5 for script authoring, analysis, and reporting.
Source inputs: `research/outputs/a100_two_role_activation_cloud_pilot/judge_input_responses.jsonl`, `research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv`, `research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv`, `research/outputs/a100_activation_cloud_posthoc_analysis/judge_filtered_cloud_summary_by_role.csv`, and `research/outputs/a100_activation_cloud_posthoc_analysis/judge_filtered_centroid_shifts.csv`.
Generating script: `research/outputs/gpt55_judge_and_outlier_followup/run_gpt55_judge_and_outlier_followup.py`
Dependent analyses: Judge-model sensitivity, score==3 outlier review, instruction/question selection for future GPU runs, and activation-cloud sample-size/protocol refinement.
Current status: Complete.
Notes/caveats: This is not a deterministic replication of GPT-4.1 because GPT-4.1 used temperature 0 while GPT-5.5 required model-default temperature. The comparison should be described as evaluator-model plus decoding-policy sensitivity. No GPU work, response generation, activation extraction, or pod work occurred. API credentials were loaded from the environment or `~/.openai_api_key` and were not logged or committed.

## prior adaptive recovery audit outputs

Artifact: Local recoverability audit for prior adaptive trickster/editor extraction artifacts under the corrected D01 boundary result.
Location: `research/outputs/prior_adaptive_recovery_audit/`
Created by: Codex/GPT-5.5.
Model used: Codex/GPT-5.5 for script authoring, local audit, and reporting; no model API calls, pods, GPU work, response generation, or activation extraction were run.
Source inputs: `research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl`, `research/q2_stability/qwen/outputs/paper1_5/trickster_phase2_scores_codex_gpt55.jsonl`, `research/q2_stability/qwen/outputs/paper1_5/activations_trickster/`, `research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase1_128.jsonl`, `research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase2_scores_codex_gpt55.jsonl`, `research/q2_stability/qwen/outputs/paper1_5/editor/activations_editor/`, `research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/editor_phase1_matched64_1024.jsonl`, `research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/editor_phase2_scores_1024_codex_gpt55.jsonl`, `research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/activations_editor_1024/`, `research/q2_stability/qwen/scripts/phase1_inference_only_v4.py`, `research/q2_stability/qwen/scripts/phase1_inference_only_editor.py`, `research/q2_stability/qwen/scripts/phase1_inference_editor_matched64_1024.py`, `downloads/hf_vectors/qwen-3-32b/role_vectors/`, `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv`, `data/roles/instructions/`, and `data/extraction_questions.jsonl`.
Generating script: `research/outputs/prior_adaptive_recovery_audit/run_prior_adaptive_recovery_audit.py`
Dependent analyses: Evaluator-model sensitivity for prior adaptive extraction, Paper 1.5 methodology caveats, local PCA/cloud comparison of saved hook-derived adaptive vectors, and decisions about whether GPU regeneration is necessary.
Current status: Complete.
Notes/caveats: The audit found three explicit prior adaptive runs and classified all three as `full_reproject_possible` because they preserve response text and 5120-d hook-derived activation shards. D01 does not invalidate these saved hook vectors; the corrected result says the hook matches `outputs.hidden_states[49]`, not `hidden_states[48]`. The prepared GPT-4.1 judge input JSONL contains 1,392 saved responses, but no OpenAI judge call was run because no explicit `run_gpt41_rejudge=true` configuration was present. Raw token-level hidden states cannot be recovered from mean-pooled shards without GPU reruns.

## recovered role cloud analysis outputs

Artifact: GPT-4.1 rejudging and activation-cloud comparison for recovered trickster/editor adaptive extraction runs.
Location: `research/outputs/recovered_role_cloud_analysis/`
Created by: Codex/GPT-5.5.
Model used: GPT-4.1 through the OpenAI API for role-expression judging at temperature 0; Codex/GPT-5.5 for script authoring, local analysis, and reporting.
Source inputs: `research/outputs/prior_adaptive_recovery_audit/prior_adaptive_gpt41_judge_inputs.jsonl`, `research/outputs/prior_adaptive_recovery_audit/prior_adaptive_corrected_coordinates.csv`, `research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv`, `research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv`, and `research/visualizations/geometry_viz_data.json`.
Generating script: `research/outputs/recovered_role_cloud_analysis/run_recovered_role_cloud_analysis.py`
Dependent analyses: Paper 1.5 evaluator-sensitivity language for adaptive extraction, editor/procedural-professional failure interpretation, future procedural-professional anchoring redesign, and comparison of adaptive extraction clouds to response-state activation clouds.
Current status: Complete.
Notes/caveats: The run scored 1,392 recovered responses with GPT-4.1 at temperature 0, using `~/.openai_api_key` without logging the key. Actual usage was 1,084,673 prompt tokens and 187,913 completion tokens, with estimated cost $3.6726. This is GPT-4.1, not `gpt-4.1-mini`; therefore it is a practical evaluator-sensitivity comparison, not strict Lu-method identity. Trickster retained 1200/1200 score>=2 and 1198/1200 score==3; editor remained low at score==3 in both 512-token and 1024-token runs.

## activation cloud layered viewer outputs

Artifact: Standalone layered visualization for activation-cloud comparisons across amateur, playwright, recovered trickster, and recovered editor runs.
Location: `research/outputs/activation_cloud_layered_viewer/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activation extraction, judge calls, or response generation were run.
Source inputs: `research/visualizations/geometry_viz_data.json`, `research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv`, `research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv`, `research/outputs/gpt55_judge_and_outlier_followup/gpt55_judge_scores.csv`, `research/outputs/prior_adaptive_recovery_audit/prior_adaptive_corrected_coordinates.csv`, `research/outputs/recovered_role_cloud_analysis/recovered_gpt41_scores.csv`, and prior standalone viewer artifacts under `research/outputs/a100_activation_cloud_visualization_and_judge_compare/`.
Generating script: `research/outputs/activation_cloud_layered_viewer/run_activation_cloud_layered_viewer.py`
Dependent analyses: Visual inspection of judge-filter sensitivity, comparison of published centroids to all-response and retained-response subclouds, editor/procedural-professional failure reassessment, and future activation-cloud pilot planning.
Current status: Complete standalone viewer; main persona geometry explorer was not modified.
Notes/caveats: The viewer contains 1,512 response points and five role/run views: `amateur`, `playwright`, `trickster_phase1_1200`, `editor_phase1_128`, and `editor_matched64_1024`. GPT-5.5 layers are available only for amateur/playwright. Editor GPT-4.1 score==3 centroids are sparse (`n=3` for `editor_phase1_128`, `n=2` for `editor_matched64_1024`) and should be treated as visual reference points rather than stable centroid estimates.

## cloud eigenvector angle analysis outputs

Artifact: Activation-cloud covariance/eigenvector orientation analysis across layered response clouds.
Location: `research/outputs/cloud_eigenvector_angle_analysis/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activation extraction, judge calls, or response generation were run.
Source inputs: `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json`, `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_centroids.csv`, `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_membership_counts.csv`, `research/visualizations/geometry_viz_data.json`, and the original cloud/judge artifacts already incorporated by the layered viewer.
Generating script: `research/outputs/cloud_eigenvector_angle_analysis/run_cloud_eigenvector_angle_analysis.py`
Dependent analyses: Future activation-cloud pilot role selection, negative-PC2 test design, Paper 1.5 response-cloud uncertainty language, and visual interpretation of role-expression filtering effects.
Current status: Complete local analysis.
Notes/caveats: The analysis treats eigenvector angles as sign-invariant line orientations. Assistant-axis direction is a proxy estimated by regressing stored role `axis_projections` on PC1/PC2, not by independently loading an assistant-axis vector in PCA space. The empirical high-PC1/high-PC2 upper-region direction is also a documented proxy. Sparse editor score==3 layers remain unstable (`n=3` and `n=2`), and the all-response boundary/orientation pattern is provisional because only five role/run views were analyzed.

## Paper 1.5 clean repo copy plan

Artifact: Copy plan for a future clean Paper 1.5 core repository.
Location: `research/outputs/paper15_clean_repo_copy_plan/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no files were copied, moved, deleted, or reorganized.
Source inputs: Current repo layout, `research/RESEARCH_STATE.md`, `research/RESEARCH_INDEX.md`, `research/PROVENANCE_REGISTRY.md`, `research/CLAIMS_REGISTER.md`, `research/visualizations/`, `research/outputs/`, `research/q2_stability/qwen/outputs/`, `research/assistant_axis_methodology/`, public role/trait prompt artifacts, and current untracked-file state.
Generating script: `research/outputs/paper15_clean_repo_copy_plan/run_clean_repo_copy_plan.py`
Dependent analyses: Future creation of `assistant-axis-paper15-core`, report/notebook consolidation, artifact provenance generation, and first-pass exclusion of H100/prompt-battery materials.
Current status: Established planning artifact awaiting user review.
Notes/caveats: The plan proposes 43 canonical include rows, 7 optional include rows, 3 draft-reference rows, and 4 unresolved/user-review rows, with estimated canonical copy size 10.01 MB. It explicitly excludes H100 validation outputs, H100 forecast-observed arrow visualizations, extraction-boundary diagnostics, prompt-battery generation, large generated response JSONLs, RunPod logs, dyad dynamics, emotion-vector work, and activation shards. No copy operation has occurred.

## pc2 cluster-conditioned extremes outputs

Artifact: Global, per-cluster, and muted-PC1-within-cluster PC2 extremes diagnostic for the stability/impressionability interpretation.
Location: `research/outputs/pc2_cluster_conditioned_extremes/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activations, or response generation were run.
Source inputs: `research/visualizations/geometry_viz_data.json`, `research/outputs/pc2_muted_pc1_extremes/`, `research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_candidate_scores.csv`, `research/outputs/trait_persona_prediction/`, `research/outputs/trait_space_interpretation/`, and `research/outputs/axis_forcing_function_notes/`.
Generating script: `research/outputs/pc2_cluster_conditioned_extremes/run_pc2_cluster_conditioned_extremes.py`
Dependent analyses: Paper 1.5 PC2 report wording, future blinded within-cluster matched-pair ratings, and diagnostic role examples for stability/formative-state versus impressionability/transition.
Current status: Provisional/partial support.
Notes/caveats: The analysis uses 275 persona/role PCA coordinates and cluster labels from the existing geometry visualization data. Expected-direction checks passed 7/8 globally and 5/8 by cluster median; abstraction was the strongest existing proxy after cluster demeaning (Pearson r=-0.484). `shapeshifter`, `chameleon`, and `elder` remain important caveats, so PC2 should not be stated as a pure plasticity/rootedness axis.

## cross-model PC2/PC3 diagnostic outputs

Artifact: Contained cross-model PC2/PC3 comparability diagnostic over released Qwen, Llama, and secondary Gemma role vectors.
Location: `research/outputs/cross_model_pc2_pc3_diagnostic/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activations, response generation, clean-repo copying, or visualization edits were run.
Source inputs: `research/visualizations/geometry_viz_data.json`, `downloads/hf_vectors/qwen-3-32b/role_vectors/*.pt`, `downloads/hf_vectors/llama-3.3-70b/role_vectors/*.pt`, `downloads/hf_vectors/gemma-2-27b/role_vectors/*.pt`, `research/outputs/pc2_muted_pc1_extremes/`, `research/outputs/pc2_cluster_conditioned_extremes/`, and `research/visualizations/persona_geometry_explorer.html` for feasibility inspection only.
Generating script: `research/outputs/cross_model_pc2_pc3_diagnostic/run_cross_model_pc2_pc3_diagnostic.py`
Dependent analyses: Paper 1.5 PC2 transfer language, future cross-model visualization decision, and PC3 comparability caveats.
Current status: Provisional/partial support for Qwen-Llama PC2 transfer in a shared PC1/PC2 plane; weak-to-moderate PC3 comparability.
Notes/caveats: The diagnostic uses layer-mean role vectors to match the current Qwen visualization builder. Qwen-Llama PC1/PC2 plane principal correlations are 0.977 and 0.905, while same-index PC2 Pearson r=0.606 and Qwen PC2 best matches Llama PC1 at r=0.692. Qwen-Llama same-index PC3 is weaker at Pearson r=0.440, so uncaveated 3D PC3 arrows are not recommended. Gemma was included because local vectors were present and showed strong same-index local artifact alignment with Qwen, but it remains secondary to the requested Qwen-Llama diagnostic.

## cross-model cluster topology outputs

Artifact: Bounded Qwen/Llama/Gemma cluster-topology comparison testing whether coarse persona regions are more stable than later same-index PCs.
Location: `research/outputs/cross_model_cluster_topology/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activations, response generation, clean-repo copying, or visualization edits were run.
Source inputs: `research/visualizations/geometry_viz_data.json`, `downloads/hf_vectors/qwen-3-32b/role_vectors/*.pt`, `downloads/hf_vectors/llama-3.3-70b/role_vectors/*.pt`, `downloads/hf_vectors/gemma-2-27b/role_vectors/*.pt`, `research/outputs/cross_model_pc2_pc3_diagnostic/`, `research/outputs/cluster_conditioned_axis_tests/`, `research/outputs/pc2_cluster_conditioned_extremes/`, and `research/visualizations/persona_geometry_explorer.html` for feasibility inspection only.
Generating script: `research/outputs/cross_model_cluster_topology/run_cross_model_cluster_topology.py`
Dependent analyses: Paper 1.5 cross-model topology language, cross-model visualization decision, and cautious distinction between stable broad regions and model-local PCA axes.
Current status: Provisional/partial support for broad topology preservation; hard clusters are not universal.
Notes/caveats: The diagnostic uses layer-mean role vectors to match the current Qwen visualization builder. Independent `k=7` k-means clustering in top-3-PC space gave Qwen-Llama ARI/NMI 0.364/0.458, Qwen-Gemma 0.637/0.656, and Llama-Gemma 0.355/0.454. Top-5-PC sensitivity improved Qwen-Llama to 0.537/0.548. Procedural/evaluator and mythic/symbolic regions are the clearest recurring regions; grounded/social, care/repair, adversarial/perturbative, and creative/symbolic regions split more. Visualization recommendation is model switching or cluster-overlap/alluvial views before any cross-model PC3 arrows.

## Paper 1.5 core analysis notebook skeleton

Artifact: First-pass local-runnable Jupyter notebook skeleton for the Paper 1.5 core analysis walkthrough.
Location: `research/notebooks/paper15_core_analysis_walkthrough.ipynb`
Supporting location: `research/outputs/paper15_notebook_core/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activation extraction, response generation, clean-repo copying, or visualization edits were run.
Source inputs: `research/outputs/paper15_clean_repo_copy_plan/`, `research/visualizations/geometry_viz_data.json`, `research/visualizations/persona_geometry_explorer.html`, `research/outputs/pc2_muted_pc1_extremes/`, `research/outputs/pc2_cluster_conditioned_extremes/`, `research/outputs/cross_model_pc2_pc3_diagnostic/`, `research/outputs/cross_model_cluster_topology/`, `research/outputs/pc3_validation/`, `research/outputs/trait_persona_prediction/`, `research/outputs/trait_space_interpretation/`, `research/outputs/prompt_to_geometry_forecasting/`, `research/outputs/prompt_artifact_inventory/`, and `research/outputs/role_rollout_artifact_audit/`.
Generating script: `research/outputs/paper15_notebook_core/run_build_paper15_notebook.py`
Dependent analyses: Future clean Paper 1.5 core repo, executable technical appendix, report-spine walkthrough, and user review of which canonical artifacts belong in the shareable package.
Current status: Established WIP notebook skeleton with successful headless Jupyter execution, shareability revision, and collapsed-code HTML export.
Notes/caveats: The notebook intentionally excludes H100 validation outputs, prompt-battery generation, extraction-boundary diagnostics, RunPod logs, activation shards, and H100 forecast-observed arrow visualizations. Initial plain-Python validation passed before Jupyter was installed. A repo-local `.venv-notebook` environment was then created, the authorized notebook stack was installed, deterministic notebook cell IDs were added as a mechanical metadata fix, and headless execution produced `research/notebooks/paper15_core_analysis_walkthrough.executed.ipynb` plus `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough.html` with 12/12 code cells executed, 0 errors, and 0 final execution-log warnings. The shareability revision added markdown clarifications for geometry metadata, cross-model PCA alignment, trait/persona reconstruction limits, the 1,200-rollout versus 64-vector-count distinction, optional forecasting status, and final summary caveats; it regenerated `research/outputs/paper15_notebook_core/paper15_core_analysis_walkthrough_report_collapsed_code.html` with 12 collapsed code toggles and outputs visible. PDF export was skipped because nbconvert `webpdf` requires Playwright, which was outside the authorized package list for the revision task.

## PC2 trait-stratified profile outputs

Artifact: PC1-stratified trait-profile analysis of Qwen persona PC2.
Location: `research/outputs/pc2_trait_stratified_profile/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activation extraction, response generation, or new judging were run.
Source inputs: `research/visualizations/geometry_viz_data.json`, `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`, `research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json`, `research/outputs/pc2_muted_pc1_extremes/`, and `research/outputs/pc2_cluster_conditioned_extremes/`.
Generating script: `research/outputs/pc2_trait_stratified_profile/run_pc2_trait_stratified_profile.py`
Dependent analyses: Paper 1.5 PC2 interpretation wording, future prompt-to-geometry rubric design, future blinded PC2 matched-pair checks, and clean notebook/report updates if this analysis is admitted into the core artifact set.
Current status: Complete local analysis with provisional interpretation update.
Notes/caveats: The analysis joins 275 roles/personas to 240 trait-cosine features and compares high versus low PC2 roles globally and inside PC1 strata. Replication is defined descriptively by same-sign Cohen's d at threshold across PC1 quintiles. Because PC1 and PC2 are PCA-orthogonal, direct PC2 residualization on PC1 is nearly unchanged; the primary PC1-confound protection is stratified enrichment plus per-trait PC1 covariate checks. Trait profiles are activation-space cosine features, not independent psychological ratings or causal labels.

## Trait-profile provenance audit

Artifact: Provenance audit for the 275-role x 240-trait Qwen profile matrix used in trait-profile and PC2 analyses.
Location: `research/outputs/trait_profile_provenance_audit/`
Created by: Codex/GPT-5.5.
Model used: Analysis and editing model GPT-5.5; no model APIs, pods, GPU work, activation extraction, response generation, new trait scoring, or judging were run.
Source inputs: `research/REPO_NAVIGATION.md`, `research/REPO_FILE_INDEX.csv`, `research/RAW_URL_INDEX.md`, `research/PROVENANCE_REGISTRY.md`, `research/RESEARCH_INDEX.md`, `research/RESEARCH_STATE.md`, `research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`, `research/outputs/trait_persona_prediction/run_trait_persona_prediction.py`, `research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json`, `research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv`, `research/outputs/pc2_trait_stratified_profile/run_pc2_trait_stratified_profile.py`, `research/outputs/qwen_pc2_trait_region_overlay/run_qwen_pc2_trait_region_overlay.py`, `data/traits/trait_list.json`, `data/traits/instructions/*.json`, `downloads/hf_vectors/qwen-3-32b/trait_vectors/*.pt`, `downloads/hf_vectors/qwen-3-32b/role_vectors/*.pt`, `research/outputs/prompt_artifact_inventory/prompt_artifact_inventory_report.md`, Hugging Face API metadata for `lu-christina/assistant-axis-vectors`, and Hugging Face API metadata for `belmore/assistant-axis-vector-prompts`.
Generating script: none; direct provenance audit with schema/count checks and source-code inspection.
Dependent analyses: Paper 1.5 trait-profile language, PC2 trait-stratified interpretation, Qwen PC1 x PC2 trait-region overlay caveats, and future claims about evidential independence of trait-enrichment visualizations.
Current status: Complete provenance audit.
Notes/caveats: Verdict is mixed. The 240 trait vocabulary, prompt artifacts, and Qwen trait vectors are inherited Assistant Axis / Lu et al. artifacts; the 275 x 240 CSV matrix is internally generated by mean-pooling released Qwen role/trait tensors, L2-normalizing them, and computing activation-space cosine similarities. Scores are not assigned from bare role names, role descriptions, system prompts, generated response text, human ratings, or an LLM trait questionnaire inside the matrix-generation script. The matrix has low evidential independence from Qwen role PCA geometry because both are derived from the same Qwen activation-vector artifact family.

## Qwen PC1 x PC2 trait-region overlay prototype

Artifact: First Qwen-only PC1 x PC2 trait-region overlay for inspecting local PC2 trait organization within PC1 bands.
Location: `research/outputs/qwen_pc2_trait_region_overlay/`
Created by: Codex/GPT-5.5.
Model used: Analysis, visualization, and script-author model GPT-5.5; no model APIs, pods, GPU work, activation extraction, response generation, or judging were run.
Source inputs: `research/REPO_NAVIGATION.md`, `research/REPO_FILE_INDEX.csv`, `research/RAW_URL_INDEX.md`, `research/geometry_tables/qwen_role_pc_rankings.csv`, `research/geometry_tables/qwen_trait_pc_rankings.csv`, `research/geometry_tables/cluster_membership_table.csv`, and the navigation-located trait profile matrix `research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv`.
Generating script: `research/outputs/qwen_pc2_trait_region_overlay/run_qwen_pc2_trait_region_overlay.py`
Dependent analyses: Paper 1.5 PC2 visual interpretation, future interactive persona-geometry overlays, and report figures explaining why PC1-band-relative trait labels are preferable to global trait labels for PC2 inspection.
Current status: Prototype visualization with descriptive support for PC1-band-relative interpretation.
Notes/caveats: The prototype uses five equal-count PC1 quantile bands and three equal-count PC2 tertiles within each PC1 band, producing 15 populated cells and no sparse cells under the n<8 threshold. Enrichment is descriptive over activation-space trait cosine features: `enrichment_z = (mean_trait_cell - mean_trait_pc1_band) / global_trait_std`. Mean top-3 overlap between PC1-band-relative and global labels was 0.18, so local labels materially change the visible interpretation. This does not solve PC2 or establish causal psychological labels.

## AGENTS continuity and maintenance instructions

Artifact: Updated repository-level agent instructions for GPT/Codex continuity and canonical registry maintenance.
Location: `AGENTS.md`
Created by: Codex/GPT-5.5.
Model used: Analysis and editing model GPT-5.5; no model APIs, pods, GPU work, activation extraction, response generation, or judging were run.
Source inputs: `AGENTS.md`, `research/REPO_NAVIGATION.md`, `research/REPO_FILE_INDEX.csv`, `research/RAW_URL_INDEX.md`, `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, `research/FINDINGS_LEDGER.md`, `research/CLAIMS_REGISTER.md`, and `research/PROVENANCE_REGISTRY.md`.
Generating script: none; direct Markdown/CSV maintenance edit.
Dependent analyses: Future Codex/GPT startup, handoff continuity, artifact provenance discipline, navigation-file maintenance, and final-report consistency.
Current status: Active repository instruction.
Notes/caveats: The update preserves existing instructions except where superseded by canonical registry, navigation, THREAD_START, artifact-status, and final-report requirements. `AGENTS.md` itself remains classified as `active` in `research/REPO_FILE_INDEX.csv`, while navigation files and startup files remain canonical.

## persona cloud geometry audit outputs

Artifact: Local activation-cloud size, anisotropy, orientation reliability, and matched-n sample-size sensitivity audit.
Location: `research/outputs/persona_cloud_geometry_audit/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activation extraction, response generation, or judging were run.
Source inputs: `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json`, `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_centroids.csv`, `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_membership_counts.csv`, `research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv`, `research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv`, `research/outputs/gpt55_judge_and_outlier_followup/gpt55_judge_scores.csv`, `research/outputs/prior_adaptive_recovery_audit/prior_adaptive_corrected_coordinates.csv`, `research/outputs/recovered_role_cloud_analysis/recovered_gpt41_scores.csv`, and `research/outputs/cloud_eigenvector_angle_analysis/cloud_orientation_metrics.csv`.
Generating script: `research/outputs/persona_cloud_geometry_audit/run_persona_cloud_geometry_audit.py`
Dependent analyses: Paper 2 local-manifold planning, future balanced activation-cloud sampling, Paper 1.5 caveat language around role vectors as centroids, and editor/procedural-professional failure interpretation.
Current status: Complete local analysis; supporting/future-work evidence, not a material claim-status update.
Notes/caveats: The audit uses already-projected Qwen PC1/PC2/PC3 response coordinates from existing local artifacts. Matched-n bootstrap comparisons are central because cloud sizes differ from n=60 to n=1200. Sparse editor score==3 clouds are marked unreliable for covariance/orientation. Trickster is less directionally constrained by anisotropy/orientation criteria, but not larger by matched-n RMS radius.

## occupation-population persona join outputs

Artifact: Exploratory join between occupational/professional persona roles and public U.S. occupation statistics.
Location: `research/outputs/occupation_population_persona_join/`
Created by: Codex/GPT-5.5.
Model used: Analysis and script-author model GPT-5.5; no model APIs, pods, GPU work, activation extraction, response generation, or judging were run.
Source inputs: `research/geometry_tables/qwen_role_pc_rankings.csv`, `research/geometry_tables/cluster_membership_table.csv`, `research/outputs/cross_model_cluster_topology/per_model_cluster_assignments.csv`, Bureau of Labor Statistics Occupational Employment and Wage Statistics (OEWS) May 2025 national cross-industry estimates via the BLS public API, OEWS tables page `https://www.bls.gov/oes/tables.htm`, and OEWS time-series documentation under `https://download.bls.gov/pub/time.series/oe/`.
Generating script: `research/outputs/occupation_population_persona_join/run_occupation_population_persona_join.py`
Dependent analyses: Exploratory future-work/appendix checks about whether real-world occupational prevalence, wage, or specialization proxies have any detectable relationship to persona geometry among defensibly matchable occupational roles.
Current status: Complete exploratory first pass; not part of Paper 1.5 core claims.
Notes/caveats: Role-to-SOC mappings are manual and conservative. Ambiguous mappings are preserved but excluded from quantitative correlations, and unmatched archetypal/mythic/symbolic roles are not forced. Direct scripted downloads from BLS bulk ZIP/text hosts returned HTTP 403 in this environment, and the unauthenticated BLS API hit a daily threshold during the run, so returned BLS coverage is partial: 50 included roles with employment count and 42 included roles with annual median wage. OEWS employment count is not training-corpus frequency and should not be interpreted as evidence that persona geometry reflects U.S. labor demographics.

## occupation-prevalence geometry overlay outputs

Artifact: Descriptive Qwen PC1 x PC2 visualization overlay for exact/close occupation-matched persona roles, with employment-scaled highlighted points.
Location: `research/outputs/occupation_prevalence_geometry_overlay/`
Created by: Codex/GPT-5.5.
Model used: Analysis, visualization, and script-author model GPT-5.5; no model APIs, pods, GPU work, activation extraction, response generation, new BLS/Census fetches, or judging were run.
Source inputs: `research/geometry_tables/qwen_role_pc_rankings.csv`, `research/outputs/occupation_population_persona_join/role_occupation_mapping.csv`, `research/outputs/occupation_population_persona_join/role_occupation_geometry_join.csv`, `research/outputs/occupation_population_persona_join/occupation_population_cluster_summary.csv`, `research/outputs/occupation_population_persona_join/occupation_population_correlations.csv`, and `research/outputs/occupation_population_persona_join/data_source_manifest.md`.
Generating script: `research/outputs/occupation_prevalence_geometry_overlay/run_occupation_prevalence_geometry_overlay.py`
Dependent analyses: Exploratory future-work visualization of where occupation-matched professional persona roles sit in Qwen persona geometry; possible appendix/future-work figure, not Paper 1.5 core evidence.
Current status: Complete descriptive visualization follow-up.
Notes/caveats: The primary overlay includes exact and close occupational matches only; broad matches are optional in the interactive HTML; ambiguous and unmatched roles are excluded from highlighted layers. Point size reflects log BLS OEWS May 2025 employment count where inherited values are available, and missing employment values are marked explicitly. The overlay supports visual inspection of regional concentration but does not claim persona geometry reflects U.S. labor demographics, training-corpus frequency, or occupational prevalence.
