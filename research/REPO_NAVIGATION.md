# Repository Navigation

Updated UTC: 2026-09-12
Last commit when updated: ebe36e0367fc36ddb8fe32a5842d4ef5d30ae04a (AA-8 repository integration)

This is the canonical navigation layer for the Assistant Axis repository. Use it before broad searches when locating reports, geometry tables, notebooks, visualizations, cloud-analysis outputs, adaptive extraction outputs, trait analyses, or archived/deprecated artifacts.

## Start Here

- `research/RESEARCH_STATE.md`: canonical project state and current status.
- `research/RESEARCH_INDEX.md`: compact topic and artifact index.
- `research/PROVENANCE_REGISTRY.md`: artifact lineage and dependency registry.
- `research/CLAIMS_REGISTER.md`: current claims and evidentiary status.
- `research/FINDINGS_LEDGER.md`: compact findings and negative-results ledger.
- `research/RAW_URL_INDEX.md`: frequently referenced artifacts with raw GitHub URLs.
- `research/REPO_FILE_INDEX.csv`: machine-readable file inventory.

## Canonical Geometry Tables

- `research/geometry_tables/qwen_role_pc_rankings.csv`: Qwen role PCA coordinates, clusters, ranks, percentiles, and assistant-axis projection.
- `research/geometry_tables/qwen_trait_pc_rankings.csv`: Qwen trait PCA coordinates, ranks, percentiles, and assistant-axis projection.
- `research/geometry_tables/cluster_membership_table.csv`: role-to-cluster membership with PCA coordinates, ranks, percentiles, cluster margin, and assistant-axis projection.
- Source: `research/visualizations/geometry_viz_data.json`.

## Inventory Categories

- active analyses: 3965
- adaptive extraction outputs: 81
- archived/deprecated outputs: 5
- canonical report artifacts: 12
- cloud-analysis outputs: 159
- geometry tables: 30
- notebooks: 7
- trait analyses: 453
- visualizations: 242


## Status Counts

- active: 4896
- archive: 11
- canonical: 23
- deprecated: 24


## Navigation Map

### Canonical Report Artifacts

Use `research/RESEARCH_STATE.md`, `research/RESEARCH_INDEX.md`, `research/PROVENANCE_REGISTRY.md`, `research/CLAIMS_REGISTER.md`, `research/FINDINGS_LEDGER.md`, `research/THREAD_START.md`, and `research/STARTUP_MANIFEST.md` for startup and report continuity. Use `research/paper15_content_ledger.md` as the canonical factual source ledger before drafting Paper 1.5 prose.

### Active Analyses

Human-supported trait convergence and aligned subspaces: `research/outputs/human_supported_trait_convergence/human_supported_trait_convergence_report.md` is the AA-7 entry point. The exact 12 AA-1-supported labels and all decisions were frozen before outcomes. Use `comparator_summary.csv` for the matched compact prediction result, `procrustes_alignment_cv.csv` and `procrustes_alignment_null.csv` for held-out alignment evidence, `aligned_human_supported_trait_directions.csv` and `aligned_big_five_directions.csv` for recurrence, and `verification_report.json` plus `artifact_inventory.csv` for reproduction/provenance. The primary compact-efficiency result is weak/absent; the separate activation-derived aligned-direction recurrence is strong. No human respondent or occupational centroid was projected.

Externally anchored Big Five audit: `research/outputs/externally_anchored_big_five/externally_anchored_big_five_report.md` is the AA-2 entry point for the frozen geometry-blind IPIP/SAPA constructions and their Qwen/Llama/Gemma activation-space tests. Use `agreeableness_pc3_focal_test.json` for the strict Qwen focal result, the mapping CSVs and freeze manifest for construct provenance, and `big_five_viewer_integration_report.md` for canonical ridge/surface compatibility. Negative Qwen PC3 has a strong Agreeableness component; it is not equivalent to Agreeableness, and the model-local axis number does not transfer universally.

Extended persona PCA: `research/outputs/extended_persona_pca/extended_persona_pca_report.md` is the AA-3 entry point for the full rank-274 Qwen/Llama/Gemma spectra, dimensionality diagnostics, bootstrap stability, later-PC interpretation packet, cross-model shared-role score recurrence, and self-contained PC1-PC10 viewer. Use `component_retention_summary.csv` for status: Qwen PC1-PC3 are the strict core, PC4-PC6 supported secondary/provisional coordinates, PC8/PC10 exploratory, and PC7/PC9 plus later tested axes not privileged by the current stability criteria.

Qwen trait sparsity and basis coverage: `research/outputs/qwen_trait_sparsity_prediction/qwen_trait_sparsity_report.md` is the AA-4 entry point. Use `feature_budget_thresholds.csv`, `matched_basis_comparison.csv`, and `trait_span_pc_coverage.csv` to distinguish compact optimized real-trait efficiency from high-dimensional generic same-space reconstruction. The full 240-trait ceiling is substantially basis coverage and must not be described as independent psychological validation.

NLSY97 occupational personality stability: `research/outputs/nlsy97_occupation_personality_stability/nlsy97_occupation_personality_stability_report.md` is the AA-5 human-only entry point. Use `analysis_specification.md` for the frozen design, the narrow/broad stability tables and sample-size curves for centroid precision, and `persona_role_future_candidates.csv` for explicitly future candidate cells. Occupation is weak as a global personality grouping variable; stable broad parents can be semantically costly, no human/model projection was performed, and respondent-level files remain gitignored.

Multi-model trait-profile to persona-PC predictor: `research/outputs/multimodel_trait_profile_pc_predictor/multimodel_trait_profile_pc_predictor_report.md` is the entry point for the Llama-3.3-70B and Gemma-2-27B replication of the completed Qwen mapping. Use `cross_model_comparison.csv` for the canonical three-model metric table; each `llama/` and `gemma/` subdirectory contains the complete 275 x 240 cosine matrix, repeated nested comparison, raw/quantile LOPO, fixed Qwen-canonical role-family holdout, 100-permutation control, OOD reference, transparent Ridge/all-model bundles, endpoint-held-out synthetic interpolation, source manifest, and verification report. `deterministic_full_rerun_comparison.json` records byte-identical reproduction of all 20 deterministic CSVs. Each model uses its own established PCA geometry; cross-model sign orientation does not imply identical PC semantics. This is same-space saved-vector evidence, not behavioral, causal, psychometric, human-transfer, or model-sophistication evidence. No GPU, RunPod, new inference, activation extraction, or external model API was used.

Human trait-dataset feasibility: `research/outputs/human_trait_dataset_feasibility/human_trait_dataset_feasibility_report.md` is the entry point for the Phase-1 SAPA vocabulary and NLSY97 occupation/outcome audit. Use `sapa/sapa_model_trait_candidate_crosswalk.csv` for all 240 canonical trait judgments and exact item evidence, `sapa/sapa_trait_coverage_summary.json` for counts, `nlsy97/nlsy97_personality_occupation_cell_summary.json` for cohort totals, `nlsy97/nlsy97_persona_occupation_crosswalk.csv` for conservative prior-role translations and feasibility cells, `nlsy97/nlsy97_wave_overlap_summary.csv` for later-domain co-observation, and `artifact_inventory.csv` for hashes/raw URLs. Raw respondent files are gitignored under `data_external/human_validation/`. This establishes data feasibility only: no human-to-model projection, correspondence test, or human-personality claim was made.

SAPA bridge Phase-1b review: `research/outputs/human_trait_dataset_feasibility/sapa_review/` contains the fixed-seed coordinate-blind review packet for exactly the 78 original Category-3 candidates, the rubric committed before adjudication, all 78 second-pass decisions, the provisional bridge, item/scale reuse audits, retained-evidence missingness summary, verification, and an identical decision-free packet plus instructions for later external review. The review retained 45 direct primary-tier and 29 explicitly secondary close links, with 1 broad downgrade, 3 rejections, and 0 ambiguous rows. The 74 retained links use 129 items and 78 source scales, but no respondent observes all 129 retained items. The packet excludes original feasibility labels, geometry, predictors, personas, occupations, outcomes, and downstream performance. This same-workflow Codex review is not independent psychometric validation; genuinely independent review of the frozen external packet is the next gate.

Human-only SAPA bridge psychometric audit: `research/outputs/sapa_bridge_psychometric_audit/sapa_bridge_psychometric_audit_report.md` is the entry point for pairwise-complete human-response coherence, source-scale convergence, discriminant/reuse, Big Five, planned-missingness, and effective-dimensionality diagnostics on the frozen provisional bridge. Use `sapa_trait_bridge_psychometric_support_v1.csv` for the 74 trait-level outcomes, `human_trait_proxy_dimensionality_summary.json` for direct versus direct-plus-close summaries, the Pearson/Spearman matrix and pairwise-N files for group-level structure, `psychometric_support_rubric.md` for the pre-response freeze, and `artifact_inventory.csv` for hashes and branch/future-canonical URLs. The primary direct tier yields 9 high, 3 moderate, 30 redundant/broad, and 3 insufficient links; the matrix retains 6 parallel-analysis components and participation-ratio rank 12.44. This is human-data structural support only. No model geometry or respondent-to-model projection was used, and raw responses remain gitignored.

Trait-profile to persona-PC predictor: `research/outputs/trait_profile_pc_predictor/trait_profile_pc_predictor_report.md` is the entry point for the first-stage reusable mapping from all 240 Qwen activation-cosine trait features to canonical PC1/PC2/PC3. Use `validation_summary.json` for metrics and decisions, `ridge_predictor.json` for the transparent canonical V1 specification, `predict_trait_profile.py` for existing/external/percentile-modified profiles, `leave_one_persona_out_predictions.csv` for exact held-out persona lookups, `leave_one_cluster_out_summary.csv` for harder family shift, and `artifact_inventory.csv` for hashes/raw URLs. The analysis includes repeated nested Ridge/PLS/RBF-Kernel-Ridge/KNN comparison, fold-safe quantiles, 275-persona LOPO, all seven canonical cluster holdouts, 100 target permutations, OOD distance/reconstruction diagnostics, and 120 pair-endpoint-held-out synthetic activation mixes. It is same-space Qwen activation geometry; counterfactual outputs are predicted locations, not observed behavior or causal/human-personality claims. No inference, new activations, GPU, RunPod, or external model API was used.

Paper 1.5 writing-phase entry point: `research/paper15_content_ledger.md`, with source inventory in `research/paper15_content_ledger_artifact_inventory.csv`. Use this ledger before drafting prose; it separates observed findings, interpretations, hypotheses, caveats, rejected explanations, claims inventory, open questions, and inclusion recommendations. As of 2026-06-16, the ledger includes methods-ready design/procedure details for the main PC validation and benchmark artifacts, so methods prose should start there rather than re-deriving sample sizes, rubrics, prompts, or regression procedures from individual reports.

Most active analyses live under `research/outputs/`, `research/assistant_axis_methodology/`, and `research/q2_stability/qwen/outputs/`. Prefer the directory-level report files first, then inspect CSV/JSON support files only as needed. The exploratory occupation-population persona join lives under `research/outputs/occupation_population_persona_join/` and is marked future-work/appendix material, not Paper 1.5 core evidence. Its descriptive geometry overlay lives under `research/outputs/occupation_prevalence_geometry_overlay/`. The active second-generation role-free probe packet for future PC1/PC2 directional pilot inspection lives under `research/outputs/role_free_directional_prompt_pilot_v2/`; it is prompt design only, with no activation run. The first packet under `research/outputs/role_free_directional_prompt_pilot/` is retained as the superseded comparison baseline. The true role-free directional steering packet lives under `research/outputs/role_free_directional_steering_prompts/`; it contains response-guidance instructions, not probe scenarios. The canonical v1 no-label elicitation prompt packet for Paper 1.5 manual review lives under `research/outputs/no_label_elicitation_prompt_packet_v1/`; it freezes 60 chat-developed prompts. The completed 600-response activation validation using that packet lives under `research/outputs/no_label_elicitation_validation/`. The diagnostic geometry follow-up for that validation lives under `research/outputs/no_label_elicitation_geometry_diagnostics/` and should be consulted before redesigning failed/off-axis no-label prompt families. The assistant-centroid provenance audit lives under `research/outputs/assistant_centroid_provenance_audit/`; it establishes that the current Paper 1.5 assistant baseline is the released role-conditioned `assistant` centroid, not bare Qwen, making the 240-question bare-Qwen/default baseline foundational for future no-label interpretation. The default Assistant baseline audit lives under `research/outputs/default_assistant_baseline_audit/`; it projects Lu et al.'s released Qwen `default_vector.pt` and shows it is distinct from both the assistant role centroid and Run 2 bare no-system centroid. The completed Run 2 no-label elicitation execution lives under `research/outputs/no_label_elicitation_run2/`; it contains the 1,690-response bare-Qwen/replacement/minimal-pair result tables, completed report, final heartbeat/status files, and local gitignored activation shards. Treat `run2_report.md`, `run2_execution_status.json`, and `run2_local_integrity_check.json` as the entry points. The Run 2 prompt-level diagnostic follow-up lives under `research/outputs/no_label_elicitation_run2_prompt_diagnostics/`; use it to inspect the PC1+ failed/strongest prompts, PC2- selected prompts, and five PC3 cost-to-others pair contrasts including the Run 1 `pc3_pos_05` A-side. The focused PC1 accountability validation lives under `research/outputs/pc1_accountability_validation/`; use it as the execution-time evidence that accountability/scrutiny wording drives stronger positive PC1 movement than determination or arithmetic/checking wording under matched scenarios. The role geometry/instruction inventory lives under `research/outputs/role_geometry_instruction_inventory/`; it joins Qwen role PC coordinates to the five positive role-conditioning prompts for Excel/manual inspection. The iterative semantic prediction methods archive lives under `research/outputs/iterative_semantic_prediction_methods/`; use it for the Paper 1.5 methods prose and benchmark table showing semantic baseline through SVD15 prompt-register performance. The PC1 competing-theories diagnostic lives under `research/outputs/pc1_competing_theories_test/`; use it to compare orderliness, determination, and external-standard-accountability vocabulary features. The completed blind PC interpretation rating benchmark lives under `research/outputs/blind_pc_interpretation_rating_benchmark/`; use it as the stronger coordinate-blind GPT-5.5 evidence for PC1 external-standard accountability, PC2 signed integration/coherence, and PC3 internal-objective-vs-care ratings over the shared 273-persona benchmark.

### Visualizations

Multimodel grouped trait landscape: `research/outputs/persona_trait_surface_viewer/persona_trait_surface_viewer.html` switches without reload among Qwen, Llama, and Gemma and between the original Editorial groups and AA-2 strict Big Five domains. Editorial remains the default. Every model/profile has its own nodes, fabrics, masks, planes, diagnostics, hover data, and details; camera state and persona-name selection persist as designed, stale traces are removed on rapid switching, and Qwen Editorial numerical drift is exactly zero. Data/DOM tests and actual local Chrome 152/Plotly WebGL verification passed. Open the completed HTML, not `viewer_template.html`; use `big_five_viewer_integration_report.md` and the directory inventories for methods and hashes.

Multimodel PC-ranked trait profiles: `research/outputs/persona_trait_ridge_plots/persona_trait_ridges.html` keeps the unchanged 15-trait Editorial mode as default and adds Big Five mode with strict, extended, external-taxonomy-expanded, and historical constructions. It switches without reload among Qwen/Llama/Gemma; Qwen Editorial outputs are unchanged, model/profile/construction switching leaves no stale traces, and selection persists by persona name. Heights remain within-model scores/ranks rather than absolute cross-model psychological measurements.

PC-ranked emotion profiles: `research/outputs/persona_emotion_ridge_plots/persona_emotion_ridges.html` shows all 275 personas in three descending-PC rankings. Ten saved categories are ordered negative-to-positive, with ridge height encoding within-emotion percentile affinity. The directory includes 2,750 scores, full SVG/PNG exports, a top-20 overview and reproducible provenance/checks. All plots are pre-rendered; open the completed HTML, not a source template.

Emotion viewer startup follow-up: the user now reports the completed 3D viewer works; the shown nonworking page was the build template. The original clean-profile tests remain historical, and no new live-browser verification is claimed.

Qwen emotion surface viewer: `research/outputs/persona_emotion_surface_viewer/persona_emotion_surface_viewer.html` is the offline six-emotion slider/two-PC fabric landscape for all 275 personas. The directory contains the 1,650-row score table, data bundle, source manifest, methodology, implementation report, reproducible generator/UI sources, browser/data verification, and screenshots. The current UI adds a vivid fixed symmetric z-score palette, a fabric-only node toggle, synchronized yaw/pitch/roll/zoom dials, numeric entry, and Isometric/Top/Front/Side presets. The original plan is retained with a completion addendum. Values are normalized activation affinities, not emotion prevalence; layer/pooling caveats and smoothing gaps remain explicit. This companion does not overwrite the main explorer.

Current interactive visualizations live under `research/visualizations/` and `visualizations/`. The main current geometry explorer is `research/visualizations/persona_geometry_explorer.html`; it now includes native PC1 x PC2 trait-region overlay controls backed by `research/visualizations/trait_region_overlay_data.json`. Paper 1 public-facing visualization assets remain under `visualizations/`.

### Geometry Tables

Canonical geometry tables now live under `research/geometry_tables/`. These are generated from `research/visualizations/geometry_viz_data.json` and should be treated as stable references for role/trait PC rankings and cluster membership.

### Notebooks

Current Paper 1.5 notebook artifacts live under `research/notebooks/` and `research/outputs/paper15_notebook_core/`. Use the executed notebook and collapsed-code HTML report for reader-facing workflows.

### Cloud-Analysis Outputs

H100/A100 validation, activation-cloud pilots, judge comparisons, extraction-boundary diagnostics, cloud orientation analyses, and persona-cloud geometry audits live under `research/outputs/h100_*`, `research/outputs/a100_*`, `research/outputs/*cloud*`, `research/outputs/persona_cloud_geometry_audit/`, and related diagnostic directories.

### Adaptive Extraction Outputs

Adaptive extraction and recovered role-cloud artifacts live under `research/q2_stability/qwen/outputs/paper1_5/`, `research/outputs/prior_adaptive_recovery_audit/`, `research/outputs/recovered_role_cloud_analysis/`, and related activation-cloud directories.

### Trait Analyses

Trait-vector, Big Five, trait-space PCA, and trait-profile analyses are indexed in `research/outputs/trait_persona_prediction/`, `research/outputs/trait_space_interpretation/`, `research/outputs/pc2_trait_stratified_profile/`, `research/outputs/qwen_pc2_trait_region_overlay/`, `research/outputs/multimodel_ordered_trait_region_viewer/`, `research/outputs/multimodel_trait_profile_pc_predictor/`, `research/outputs/trait_profile_provenance_audit/`, `research/outputs/big_five_provenance_audit/`, `research/outputs/same_space_big_five_overlay/`, and `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`. For PC2 visualization work, start with `research/visualizations/persona_geometry_explorer.html` and its `Trait regions` controls for Qwen-only exploration, or `research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_viewer.html` for Qwen/Llama/Gemma ordered-axis comparisons. Then inspect `research/visualizations/trait_region_overlay_integration_report.md`, `research/outputs/qwen_pc2_trait_region_overlay/qwen_pc1_pc2_trait_region_report.md`, and `research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_report.md`. For the cross-model held-out predictive replication, use `research/outputs/multimodel_trait_profile_pc_predictor/multimodel_trait_profile_pc_predictor_report.md`. For provenance and evidential-independence caveats on the 275-role x 240-trait matrix, start with `research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md`. For provenance and independence caveats on the legacy Big Five explorer overlay, start with `research/outputs/big_five_provenance_audit/big_five_provenance_report.md`; that legacy overlay should be treated as heuristic cluster-conditioned semantic summary. For the current evidence-bearing same-space Big Five layer, use `research/outputs/same_space_big_five_overlay/same_space_big_five_report.md` and label it as activation-derived trait-vector projection, not independent psychometric rating.

#### AA-8 Qwen PC1/PC2 Bipolar Human Mapping

Use `research/outputs/qwen_pc1_pc2_bipolar_human_mapping/pc1_pc2_bipolar_human_mapping_report.md` as the entry point. All files are active; the two specificity sources are frozen and complementary.

- `analysis_specification.md`: frozen scope, hierarchy, rubrics, and firewalls.
- `pc1_bipolar_model_evidence_packet.csv`: PC1 trait, role, cluster, and prior-result packet.
- `pc2_bipolar_model_evidence_packet.csv`: PC2 trait, role, cluster, and prior-result packet.
- `model_evidence_packet_manifest.json`: packet source hashes and freeze provenance.
- `pc1_sapa_construct_reconsideration.csv`: full 126-construct PC1 screen.
- `pc1_rule_procedure_item_audit.csv`: 696-item-dictionary audit subset for rules/procedures/standards.
- `pc1_bipolar_human_mapping.csv`: bipolar PC1 candidate judgments.
- `pc2_coordinate_blind_role_rating_rubric.md`: frozen role-content rubric.
- `pc2_coordinate_blind_role_ratings.csv`: frozen ratings for all 275 roles, with no geometry fields.
- `pc2_role_rating_freeze_manifest.json`: rating hash and freeze commit.
- `pc2_role_dimension_pc_associations.csv`: post-freeze association and incremental diagnostics.
- `pc2_role_dimension_diagnostic_report.md`: embodiment, continuum, and counterexample audit.
- `pc2_sapa_construct_reconsideration.csv`: full 126-construct PC2/opposite-pole screen.
- `pc2_physicality_activity_item_audit.csv`: 696-item-dictionary physicality/activity audit subset.
- `pc2_bipolar_human_mapping.csv`: bipolar PC2 candidate judgments.
- `pc1_pc2_bipolar_interpretation_comparison.csv`: axis synthesis and competing interpretations.
- `pc1_pc2_bipolar_human_mapping_report.md`: primary scientific report.
- `source_manifest.json`: exact commit/path/hash provenance.
- `verification_report.json`: source, freeze, leakage, parse, and reproducibility checks.
- `artifact_inventory.csv`: hashes, introducing commits, and branch/future-canonical raw URLs.
- `scripts/build_pc2_coordinate_blind_role_ratings.py`: deterministic blind-rating builder.
- `scripts/build_model_evidence_and_role_diagnostics.py`: evidence/diagnostic builder.
- `scripts/build_human_reconsideration.py`: construct/item inventory builder.
- `scripts/build_source_manifest.py`: source-manifest builder.
- `scripts/verify_aa8.py`: independent verifier.
- `scripts/build_artifact_inventory.py`: artifact-inventory builder.

### Archived or Deprecated Outputs

Archived material is marked `archive` in `research/REPO_FILE_INDEX.csv`. Deprecated material should be left in place unless a future cleanup task explicitly approves moving it.

## Maintenance Rule

Any future Codex task that creates, deletes, moves, renames, replaces, supersedes, archives, deprecates, or materially revises a research artifact must update all three navigation files before committing:

- `research/REPO_NAVIGATION.md`
- `research/REPO_FILE_INDEX.csv`
- `research/RAW_URL_INDEX.md`

The task should record the update timestamp and commit, and assign each affected artifact one of these statuses: `canonical`, `active`, `archive`, or `deprecated`. If the task also changes `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md`, regenerate `research/STARTUP_MANIFEST.md` with `python3 scripts/update_startup_manifest.py`.
