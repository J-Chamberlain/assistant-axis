# Repository Navigation

Updated UTC: 2026-06-13T19:35:00Z
Last commit when generated: 8e2cac8

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

- active analyses: 3762
- adaptive extraction outputs: 81
- archived/deprecated outputs: 5
- canonical report artifacts: 12
- cloud-analysis outputs: 159
- geometry tables: 30
- notebooks: 7
- trait analyses: 340
- visualizations: 123


## Status Counts

- active: 4461
- archive: 11
- canonical: 23
- deprecated: 24


## Navigation Map

### Canonical Report Artifacts

Use `research/RESEARCH_STATE.md`, `research/RESEARCH_INDEX.md`, `research/PROVENANCE_REGISTRY.md`, `research/CLAIMS_REGISTER.md`, `research/FINDINGS_LEDGER.md`, `research/THREAD_START.md`, and `research/STARTUP_MANIFEST.md` for startup and report continuity. Use `research/paper15_content_ledger.md` as the canonical factual source ledger before drafting Paper 1.5 prose.

### Active Analyses

Paper 1.5 writing-phase entry point: `research/paper15_content_ledger.md`, with source inventory in `research/paper15_content_ledger_artifact_inventory.csv`. Use this ledger before drafting prose; it separates observed findings, interpretations, hypotheses, caveats, rejected explanations, claims inventory, open questions, and inclusion recommendations. As of 2026-06-16, the ledger includes methods-ready design/procedure details for the main PC validation and benchmark artifacts, so methods prose should start there rather than re-deriving sample sizes, rubrics, prompts, or regression procedures from individual reports.

Most active analyses live under `research/outputs/`, `research/assistant_axis_methodology/`, and `research/q2_stability/qwen/outputs/`. Prefer the directory-level report files first, then inspect CSV/JSON support files only as needed. The exploratory occupation-population persona join lives under `research/outputs/occupation_population_persona_join/` and is marked future-work/appendix material, not Paper 1.5 core evidence. Its descriptive geometry overlay lives under `research/outputs/occupation_prevalence_geometry_overlay/`. The active second-generation role-free probe packet for future PC1/PC2 directional pilot inspection lives under `research/outputs/role_free_directional_prompt_pilot_v2/`; it is prompt design only, with no activation run. The first packet under `research/outputs/role_free_directional_prompt_pilot/` is retained as the superseded comparison baseline. The true role-free directional steering packet lives under `research/outputs/role_free_directional_steering_prompts/`; it contains response-guidance instructions, not probe scenarios. The canonical v1 no-label elicitation prompt packet for Paper 1.5 manual review lives under `research/outputs/no_label_elicitation_prompt_packet_v1/`; it freezes 60 chat-developed prompts. The completed 600-response activation validation using that packet lives under `research/outputs/no_label_elicitation_validation/`. The diagnostic geometry follow-up for that validation lives under `research/outputs/no_label_elicitation_geometry_diagnostics/` and should be consulted before redesigning failed/off-axis no-label prompt families. The assistant-centroid provenance audit lives under `research/outputs/assistant_centroid_provenance_audit/`; it establishes that the current Paper 1.5 assistant baseline is the released role-conditioned `assistant` centroid, not bare Qwen, making the 240-question bare-Qwen/default baseline foundational for future no-label interpretation. The default Assistant baseline audit lives under `research/outputs/default_assistant_baseline_audit/`; it projects Lu et al.'s released Qwen `default_vector.pt` and shows it is distinct from both the assistant role centroid and Run 2 bare no-system centroid. The completed Run 2 no-label elicitation execution lives under `research/outputs/no_label_elicitation_run2/`; it contains the 1,690-response bare-Qwen/replacement/minimal-pair result tables, completed report, final heartbeat/status files, and local gitignored activation shards. Treat `run2_report.md`, `run2_execution_status.json`, and `run2_local_integrity_check.json` as the entry points. The Run 2 prompt-level diagnostic follow-up lives under `research/outputs/no_label_elicitation_run2_prompt_diagnostics/`; use it to inspect the PC1+ failed/strongest prompts, PC2- selected prompts, and five PC3 cost-to-others pair contrasts including the Run 1 `pc3_pos_05` A-side. The focused PC1 accountability validation lives under `research/outputs/pc1_accountability_validation/`; use it as the execution-time evidence that accountability/scrutiny wording drives stronger positive PC1 movement than determination or arithmetic/checking wording under matched scenarios. The role geometry/instruction inventory lives under `research/outputs/role_geometry_instruction_inventory/`; it joins Qwen role PC coordinates to the five positive role-conditioning prompts for Excel/manual inspection. The iterative semantic prediction methods archive lives under `research/outputs/iterative_semantic_prediction_methods/`; use it for the Paper 1.5 methods prose and benchmark table showing semantic baseline through SVD15 prompt-register performance. The PC1 competing-theories diagnostic lives under `research/outputs/pc1_competing_theories_test/`; use it to compare orderliness, determination, and external-standard-accountability vocabulary features. The completed blind PC interpretation rating benchmark lives under `research/outputs/blind_pc_interpretation_rating_benchmark/`; use it as the stronger coordinate-blind GPT-5.5 evidence for PC1 external-standard accountability, PC2 signed integration/coherence, and PC3 internal-objective-vs-care ratings over the shared 273-persona benchmark.

### Visualizations

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

Trait-vector, Big Five, trait-space PCA, and trait-profile analyses are indexed in `research/outputs/trait_persona_prediction/`, `research/outputs/trait_space_interpretation/`, `research/outputs/pc2_trait_stratified_profile/`, `research/outputs/qwen_pc2_trait_region_overlay/`, `research/outputs/multimodel_ordered_trait_region_viewer/`, `research/outputs/trait_profile_provenance_audit/`, `research/outputs/big_five_provenance_audit/`, `research/outputs/same_space_big_five_overlay/`, and `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`. For PC2 visualization work, start with `research/visualizations/persona_geometry_explorer.html` and its `Trait regions` controls for Qwen-only exploration, or `research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_viewer.html` for Qwen/Llama/Gemma ordered-axis comparisons. Then inspect `research/visualizations/trait_region_overlay_integration_report.md`, `research/outputs/qwen_pc2_trait_region_overlay/qwen_pc1_pc2_trait_region_report.md`, and `research/outputs/multimodel_ordered_trait_region_viewer/multimodel_ordered_trait_region_report.md`. For provenance and evidential-independence caveats on the 275-role x 240-trait matrix, start with `research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md`. For provenance and independence caveats on the legacy Big Five explorer overlay, start with `research/outputs/big_five_provenance_audit/big_five_provenance_report.md`; that legacy overlay should be treated as heuristic cluster-conditioned semantic summary. For the current evidence-bearing same-space Big Five layer, use `research/outputs/same_space_big_five_overlay/same_space_big_five_report.md` and label it as activation-derived trait-vector projection, not independent psychometric rating.

### Archived or Deprecated Outputs

Archived material is marked `archive` in `research/REPO_FILE_INDEX.csv`. Deprecated material should be left in place unless a future cleanup task explicitly approves moving it.

## Maintenance Rule

Any future Codex task that creates, deletes, moves, renames, replaces, supersedes, archives, deprecates, or materially revises a research artifact must update all three navigation files before committing:

- `research/REPO_NAVIGATION.md`
- `research/REPO_FILE_INDEX.csv`
- `research/RAW_URL_INDEX.md`

The task should record the update timestamp and commit, and assign each affected artifact one of these statuses: `canonical`, `active`, `archive`, or `deprecated`. If the task also changes `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md`, regenerate `research/STARTUP_MANIFEST.md` with `python3 scripts/update_startup_manifest.py`.
