# Repository Navigation

Updated UTC: 2026-06-04T16:56:24Z
Last commit when generated: 4ee315d

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

- active analyses: 3612
- adaptive extraction outputs: 81
- archived/deprecated outputs: 5
- canonical report artifacts: 10
- cloud-analysis outputs: 149
- geometry tables: 30
- notebooks: 7
- trait analyses: 302
- visualizations: 119

## Status Counts

- active: 4265
- archive: 11
- canonical: 18
- deprecated: 21

## Navigation Map

### Canonical Report Artifacts

Use `research/RESEARCH_STATE.md`, `research/RESEARCH_INDEX.md`, `research/PROVENANCE_REGISTRY.md`, `research/CLAIMS_REGISTER.md`, `research/FINDINGS_LEDGER.md`, `research/THREAD_START.md`, and `research/STARTUP_MANIFEST.md` for startup and report continuity.

### Active Analyses

Most active analyses live under `research/outputs/`, `research/assistant_axis_methodology/`, and `research/q2_stability/qwen/outputs/`. Prefer the directory-level report files first, then inspect CSV/JSON support files only as needed.

### Visualizations

Current interactive visualizations live under `research/visualizations/` and `visualizations/`. The main current geometry explorer is `research/visualizations/persona_geometry_explorer.html`; Paper 1 public-facing visualization assets remain under `visualizations/`.

### Geometry Tables

Canonical geometry tables now live under `research/geometry_tables/`. These are generated from `research/visualizations/geometry_viz_data.json` and should be treated as stable references for role/trait PC rankings and cluster membership.

### Notebooks

Current Paper 1.5 notebook artifacts live under `research/notebooks/` and `research/outputs/paper15_notebook_core/`. Use the executed notebook and collapsed-code HTML report for reader-facing workflows.

### Cloud-Analysis Outputs

H100/A100 validation, activation-cloud pilots, judge comparisons, extraction-boundary diagnostics, and cloud orientation analyses live under `research/outputs/h100_*`, `research/outputs/a100_*`, `research/outputs/*cloud*`, and related diagnostic directories.

### Adaptive Extraction Outputs

Adaptive extraction and recovered role-cloud artifacts live under `research/q2_stability/qwen/outputs/paper1_5/`, `research/outputs/prior_adaptive_recovery_audit/`, `research/outputs/recovered_role_cloud_analysis/`, and related activation-cloud directories.

### Trait Analyses

Trait-vector, Big Five, trait-space PCA, and trait-profile analyses are indexed in `research/outputs/trait_persona_prediction/`, `research/outputs/trait_space_interpretation/`, `research/outputs/pc2_trait_stratified_profile/`, and `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`.

### Archived or Deprecated Outputs

Archived material is marked `archive` in `research/REPO_FILE_INDEX.csv`. Deprecated material should be left in place unless a future cleanup task explicitly approves moving it.

## Maintenance Rule

Any future Codex task that creates, deletes, moves, or replaces a research artifact must update all three navigation files before committing:

- `research/REPO_NAVIGATION.md`
- `research/REPO_FILE_INDEX.csv`
- `research/RAW_URL_INDEX.md`

The task should record the update timestamp and commit. If the task also changes `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md`, regenerate `research/STARTUP_MANIFEST.md` with `python3 scripts/update_startup_manifest.py`.
