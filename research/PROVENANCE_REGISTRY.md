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
Source inputs: `geometry_viz_data.json`, `bigfive_geometry_overlay_data.json` embedded into HTML.
Generating script: Manual HTML/JS edits plus prior `build_geometry_viz.py` data generation.
Dependent analyses: visual inspection of PCA/UMAP geometry, cluster coloring, Big Five overlays, selection/lasso review.
Current status: Established visualization tool.
Notes/caveats: Visualization is self-contained and intentionally large. It is exploratory support, not a statistical test.

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
