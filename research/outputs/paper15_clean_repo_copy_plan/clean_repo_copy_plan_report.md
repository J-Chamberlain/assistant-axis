# Clean Paper 1.5 Core Repo Copy Plan

- Generated UTC: 2026-06-01T23:16:45Z
- model_used: GPT-5.5
- Recommended clean repo name: `assistant-axis-paper15-core`
- Alternative repo name: `persona-geometry-reanalysis`
- No files were copied, moved, deleted, or reorganized.

## Purpose

Create a small, auditable Paper 1.5 core repo that supports a technical report and notebook walkthrough. The source repo remains the research quarry. The clean repo should take a reader from public Assistant Axis artifacts through method/stability stress tests, persona-geometry interpretation, and the prediction-improvement sequence without requiring them to navigate H100 validation material or exploratory prompt-battery work.

## Summary Counts

- Canonical include rows: 43
- Optional include rows: 7
- Draft-reference rows: 3
- Unresolved/user-review rows: 4
- Explicit exclusion rows: 17
- Estimated canonical copied size: 10.01 MB, excluding git/object overhead and future notebooks.

## Proposed Contents

Canonical contents include public role/trait prompt artifacts, extraction questions, compact geometry data, the latest Persona Geometry Explorer, prompt artifact and role-rollout audits, core methodology notes, no-label/semantic stress-test outputs, selected trickster/editor stress-test summaries, the shared feature benchmark, hierarchical/procedural residual models, residual manifold and SVD15 outputs, PC3 and PC2 interpretation outputs, cluster-conditioned tests, and trait/persona geometry outputs.

Optional contents include trait-space interpretation, reading-based blinded rater validation, professional hierarchy validation, and prompt-to-geometry forecasting. These are useful but may be too much for the first clean walkthrough depending on how tight the report should be.

## Latest Main Visualization

Use `research/visualizations/persona_geometry_explorer.html` as the canonical visualization. Exclude all H100 forecast-observed arrow visualizations in `research/outputs/h100_percentile_edge_validation_error_analysis/`.

## Numeric Claim Traceability

The core R2 sequence is traceable:

- Semantic baseline around R2 0.389: `shared_benchmark_summary.csv`.
- Codex retained procedural features around R2 0.490: `shared_benchmark_summary.csv`.
- Claude Big Five-style features around R2 0.613: `shared_benchmark_summary.csv`.
- Hierarchical trait/procedural model around R2 0.622: `hierarchical_model_summary.csv`.
- Residual manifold around R2 0.632: `residual_manifold_report.md`.
- SVD15 lexical/register model around R2 0.707: `residual_svd_interpretation_report.md`.

See `canonical_claims_traceability_table.csv` for full row-level traceability.

## Unresolved Files Needing User Review

- `research/visualizations/persona_pc_rankings.csv`: Currently untracked in source worktree; do not treat as canonical until reviewed/committed.
- `research/visualizations/persona_pc_rankings.md`: Currently untracked in source worktree; do not treat as canonical until reviewed/committed.
- `/mnt/data/METHOD CARD-Lu et al. role-vector extraction.txt`: Not present at mounted path during inspection.
- `/mnt/data/METHOD CARD-Adaptive role-vector extraction attempt.txt`: Not present at mounted path during recent inspection.

## Explicit First-Pass Exclusions

H100 validation outputs, H100 error-analysis arrow visualizations, extraction-boundary diagnostics, prompt-battery generation outputs, RunPod logs, large response JSONLs, activation shards, dyad dynamics, and emotion-vector work are excluded from this first clean repo pass. They remain important source-quarry material, but they would obscure the core Paper 1.5 report spine.

## Recommended Next Card

After reviewing this plan, run a separate copy-only card: create `../assistant-axis-paper15-core`, copy only rows marked `canonical_include` plus any user-approved optional/draft rows, generate `PROVENANCE.md` from `clean_repo_copy_plan.csv`, create stub notebooks from the notebook plan, and do not import H100/prompt-battery materials.
