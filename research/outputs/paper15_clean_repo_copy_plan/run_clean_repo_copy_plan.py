#!/usr/bin/env python3
"""Create a copy plan for a clean Paper 1.5 core repository.

This script only writes planning artifacts. It does not copy, move, delete, or
reorganize any source-repo files.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


MODEL_USED = "GPT-5.5"
REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "research/outputs/paper15_clean_repo_copy_plan"
PREFERRED_REPO_NAME = "assistant-axis-paper15-core"
ALT_REPO_NAME = "persona-geometry-reanalysis"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dir_stats(path: Path) -> tuple[int, int, str]:
    files = sorted(p for p in path.rglob("*") if p.is_file())
    total = sum(p.stat().st_size for p in files)
    h = hashlib.sha256()
    for p in files:
        rel = p.relative_to(REPO_ROOT).as_posix()
        h.update(rel.encode())
        h.update(str(p.stat().st_size).encode())
        h.update(sha256_file(p).encode())
    return len(files), total, h.hexdigest()


def size_estimate(path_str: str) -> tuple[str, str]:
    path = REPO_ROOT / path_str
    if not path.exists():
        return "missing", ""
    if path.is_dir():
        n, total, digest = dir_stats(path)
        return f"{total} bytes across {n} files", digest
    return f"{path.stat().st_size} bytes", sha256_file(path)


def row(
    source: str,
    dest: str,
    artifact_type: str,
    section: str,
    reason: str,
    status: str,
    notebook: str,
    deps: str = "",
    notes: str = "",
) -> dict:
    size, digest = size_estimate(source)
    return {
        "source_path": source,
        "proposed_destination_path": dest,
        "artifact_type": artifact_type,
        "report_section": section,
        "reason_to_include": reason,
        "canonical_status": status,
        "required_for_notebook": notebook,
        "size_estimate": size,
        "hash_if_available": digest,
        "dependencies": deps,
        "notes_or_uncertainties": notes,
    }


def build_copy_plan() -> list[dict]:
    rows: list[dict] = []

    rows += [
        row("research/RESEARCH_STATE.md", "PROVENANCE/source_state/RESEARCH_STATE.md", "state_doc", "S05", "Preserve canonical state snapshot used when creating the copy plan.", "canonical_include", "no"),
        row("research/RESEARCH_INDEX.md", "PROVENANCE/source_state/RESEARCH_INDEX.md", "state_doc", "S05", "Compact navigation index for source artifacts and current interpretations.", "canonical_include", "no"),
        row("research/PROVENANCE_REGISTRY.md", "PROVENANCE/source_state/PROVENANCE_REGISTRY.md", "state_doc", "S01-S05", "Artifact lineage registry to preserve source-quarry provenance.", "canonical_include", "no"),
        row("research/THREAD_START.md", "PROVENANCE/source_state/THREAD_START.md", "state_doc", "S05", "Thread continuity brief useful for orienting future reviewers.", "optional_include", "no"),
        row("research/CLAIMS_REGISTER.md", "PROVENANCE/source_state/CLAIMS_REGISTER.md", "state_doc", "S05", "Claim status register; useful for separating findings from interpretations.", "optional_include", "no"),
        row("research/literature_reference.md", "report/references/literature_reference.md", "reference", "S01", "Citation/provenance metadata for Assistant Axis and related literature.", "canonical_include", "no", notes="Full local PDF was not found in this repo; use citation metadata or fetch externally if needed."),
        row("data/extraction_questions.jsonl", "data/public/extraction_questions.jsonl", "public_data", "S01", "Canonical 240 shared extraction questions used to reconstruct intended role inputs.", "canonical_include", "yes"),
        row("data/roles/instructions", "data/public/roles/instructions", "public_data_dir", "S01", "Canonical public role prompt artifacts: 275 non-default roles plus default.", "canonical_include", "yes"),
        row("data/traits/instructions", "data/public/traits/instructions", "public_data_dir", "S01", "Trait prompt artifacts useful for trait/persona comparison and source provenance.", "optional_include", "yes", notes="Include if trait-space notebook remains in first pass."),
        row("research/visualizations/geometry_viz_data.json", "data/processed/geometry_viz_data.json", "processed_data", "S01,S03", "Canonical compact geometry dataset for role PCA/UMAP, clusters, axis projections, and visualization.", "canonical_include", "yes"),
        row("research/visualizations/cluster_assignments_full.json", "data/processed/cluster_assignments_full.json", "processed_data", "S01,S03", "Full nearest-centroid cluster assignments for all 275 personas.", "canonical_include", "yes"),
        row("research/visualizations/bigfive_geometry_overlay_data.json", "data/processed/bigfive_geometry_overlay_data.json", "processed_data", "S03,S04", "Persona-aligned Big Five overlay data used by the main visualizer.", "canonical_include", "yes"),
        row("research/visualizations/bigfive_geometry_overlay_data.csv", "data/processed/bigfive_geometry_overlay_data.csv", "processed_data", "S03,S04", "Tabular Big Five overlay equivalent for notebooks.", "canonical_include", "yes"),
        row("research/visualizations/persona_geometry_explorer.html", "visualizations/persona_geometry_explorer.html", "visualization", "S01,S03", "Latest main self-contained Persona Geometry Explorer with PCA/UMAP, selection, clusters, and Big Five overlays.", "canonical_include", "no", deps="data embedded in HTML plus geometry/overlay files for reproducible rebuild"),
        row("research/visualizations/bigfive_overlay_validation.md", "visualizations/bigfive_overlay_validation.md", "validation_note", "S03,S04", "Documents Big Five overlay source, missing personas, and self-contained viewer checks.", "canonical_include", "no"),
        row("research/visualizations/scripts/build_geometry_viz.py", "scripts/build_geometry_viz.py", "script", "S01,S03", "Canonical rebuild script for the main geometry visualization.", "canonical_include", "yes"),
        row("research/visualizations/scripts/assign_clusters_by_centroid.py", "scripts/assign_clusters_by_centroid.py", "script", "S01", "Rebuild script for full nearest-centroid cluster assignments.", "canonical_include", "yes"),
        row("research/outputs/prompt_artifact_inventory", "outputs/tables/prompt_artifact_inventory", "output_dir", "S01", "Inventory proving role/trait prompt artifacts and vector-name alignment.", "canonical_include", "yes"),
        row("research/outputs/role_rollout_artifact_audit", "outputs/tables/role_rollout_artifact_audit", "output_dir", "S01,S02", "Audit showing intended 1,200 inputs per role are reconstructable while responses/scores/masks are not public.", "canonical_include", "yes"),
        row("research/assistant_axis_methodology/artifact_inventory.md", "report/methodology/artifact_inventory.md", "method_note", "S01", "Earlier methodology artifact inventory for public Assistant Axis reconstruction.", "canonical_include", "no"),
        row("research/assistant_axis_methodology/assistant_axis_pipeline_reconstruction.md", "report/methodology/assistant_axis_pipeline_reconstruction.md", "method_note", "S01,S02", "Pipeline reconstruction for public method explanation.", "canonical_include", "no"),
        row("research/assistant_axis_methodology/prompts_and_questions", "data/public/prompts_and_questions_cards", "method_cards_dir", "S01", "Human-readable canonical role list, system prompts, extraction questions, and judge prompt cards.", "canonical_include", "no"),
        row("research/assistant_axis_methodology/replication_differences_vs_lu.md", "report/methodology/replication_differences_vs_lu.md", "method_note", "S02", "Concise record of differences between public method, local reproduction, and unresolved metadata.", "canonical_include", "no"),
        row("research/assistant_axis_methodology/role_vector_structure_audit.md", "report/methodology/role_vector_structure_audit.md", "method_note", "S02", "Documents vector tensor interpretation and public vector structure.", "canonical_include", "no"),
        row("research/assistant_axis_methodology/no_label_prompt_ablation", "outputs/tables/no_label_prompt_ablation", "output_dir", "S02,S03", "No-label prompt ablation corpus and semantic comparison for methodology stress testing.", "canonical_include", "yes"),
        row("research/assistant_axis_methodology/semantic_vs_activation_geometry", "outputs/tables/semantic_vs_activation_geometry", "output_dir", "S02,S03", "Semantic-vs-activation comparison tables and report.", "canonical_include", "yes"),
        row("research/assistant_axis_methodology/semantic_topology_interpretation_note.md", "report/notes/semantic_topology_interpretation_note.md", "interpretation_note", "S02,S03", "Interpretive note for semantic topology versus activation geometry.", "canonical_include", "no"),
        row("research/q2_stability/qwen/outputs/paper1_5/trickster_sample_sufficiency_codex_gpt55.md", "outputs/tables/stress_tests/trickster_sample_sufficiency_codex_gpt55.md", "stress_test_report", "S02", "Canonical adaptive-extraction sample sufficiency result for trickster.", "canonical_include", "no"),
        row("research/q2_stability/qwen/outputs/paper1_5/trickster_vector_validation_codex_gpt55.md", "outputs/tables/stress_tests/trickster_vector_validation_codex_gpt55.md", "stress_test_report", "S02", "Vector validation showing trickster adaptive path matched released geometry.", "canonical_include", "no"),
        row("research/q2_stability/qwen/outputs/paper1_5/truncation_diagnostic.md", "outputs/tables/stress_tests/truncation_diagnostic.md", "stress_test_report", "S02", "Truncation/stability diagnostic used as methodological due diligence.", "canonical_include", "no"),
        row("research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase2_scores_codex_gpt55_report.md", "outputs/tables/stress_tests/editor_phase2_scores_codex_gpt55_report.md", "negative_stress_test_report", "S02", "Editor second-persona negative/weak result showing extraction reliability is role-dependent.", "canonical_include", "no"),
        row("research/q2_stability/qwen/outputs/shared_latent_feature_benchmark", "outputs/tables/shared_latent_feature_benchmark", "output_dir", "S04", "Canonical shared benchmark: semantic baseline, Codex procedural, Claude Big Five, feature matrices, splits, and residual rankings.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/scripts/shared_latent_feature_benchmark.py", "scripts/shared_latent_feature_benchmark.py", "script", "S04", "Rebuild script for shared benchmark if source features are present.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model", "outputs/tables/hierarchical_trait_procedural_model", "output_dir", "S04", "Hierarchical trait-to-procedural residual model outputs.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/scripts/hierarchical_trait_procedural_model.py", "scripts/hierarchical_trait_procedural_model.py", "script", "S04", "Rebuild script for hierarchical model.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/outputs/residual_manifold_analysis", "outputs/tables/residual_manifold_analysis", "output_dir", "S04", "Residual hand-feature layer explaining developmental/liminal/collective hard cases.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/scripts/residual_manifold_analysis.py", "scripts/residual_manifold_analysis.py", "script", "S04", "Rebuild script for residual manifold analysis.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/outputs/residual_svd_interpretation", "outputs/tables/residual_svd_interpretation", "output_dir", "S04", "SVD15 lexical/register interpretation and supporting tables.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/scripts/residual_svd_interpretation.py", "scripts/residual_svd_interpretation.py", "script", "S04", "Rebuild script for residual SVD interpretation.", "canonical_include", "yes"),
        row("research/outputs/pc3_validation", "outputs/tables/pc3_validation", "output_dir", "S03", "PC3 perturbation-stabilization validation with report, scores, stats, and plot.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/scripts/pc3_perturbation_validation.py", "scripts/pc3_perturbation_validation.py", "script", "S03", "Rebuild script for PC3 perturbation validation.", "canonical_include", "yes"),
        row("research/q2_stability/qwen/outputs/pc2_conditional_validation", "outputs/tables/pc2_conditional_validation", "output_dir", "S03", "Current strongest PC2 conditional interpretation after PC1 control.", "canonical_include", "yes", notes="No standalone script found in `research/q2_stability/qwen/scripts`; include outputs and mark script gap in report."),
        row("research/outputs/axis_forcing_function_notes", "report/notes/axis_forcing_function_notes", "interpretation_notes_dir", "S03,S05", "Current PC1/PC2 forcing-function interpretation and judge-rubric implications.", "canonical_include", "no"),
        row("research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md", "report/notes/persona_geometry_working_interpretation_2026-05.md", "interpretation_note", "S03", "Working PC1/PC2/PC3 interpretation note with epistemic labels and future tests.", "canonical_include", "no"),
        row("research/outputs/cluster_conditioned_axis_tests", "outputs/tables/cluster_conditioned_axis_tests", "output_dir", "S03", "Cluster-conditioned PC1/PC2 tests and pairwise ordering diagnostics.", "canonical_include", "yes"),
        row("research/outputs/trait_persona_prediction", "outputs/tables/trait_persona_prediction", "output_dir", "S03,S04", "Trait-vector similarity matrix and trait prediction of persona PCs.", "canonical_include", "yes"),
        row("research/outputs/trait_space_interpretation", "outputs/tables/trait_space_interpretation", "output_dir", "S03,S04", "Trait-only PCA and cone/axis comparison to persona space.", "optional_include", "yes"),
        row("research/q2_stability/qwen/outputs/blinded_axis_rater_study", "outputs/tables/blinded_axis_rater_study", "output_dir", "S03", "Reading-based Codex rater validation over no-label prompt dossiers.", "optional_include", "yes", notes="Useful but Codex-as-rater; include if report needs validation study detail."),
        row("research/q2_stability/qwen/outputs/professional_hierarchy_validation", "outputs/tables/professional_hierarchy_validation", "output_dir", "S03", "Targeted professional hierarchy validation for PC interpretations.", "optional_include", "yes"),
        row("research/outputs/prompt_to_geometry_forecasting", "outputs/tables/prompt_to_geometry_forecasting", "output_dir", "S04,S05", "Prompt-text-to-geometry forecasting results before H100; useful as transition/future-work material.", "optional_include", "yes", notes="Not part of H100 validation; include only if S04 covers forecasting as a lightweight extension."),
        row("research/paper1_5_outline.md", "report/drafts/paper1_5_outline.md", "draft", "S01-S05", "Current Paper 1.5 outline; copy as draft reference, not final text.", "draft_reference_only", "no"),
        row("research/paper1_5_executive_summary.md", "report/drafts/paper1_5_executive_summary.md", "draft", "S01-S05", "Concise executive framing; draft reference only.", "draft_reference_only", "no"),
        row("research/paper1_5_adaptive_extraction_notes.md", "report/drafts/paper1_5_adaptive_extraction_notes.md", "draft", "S02", "Adaptive extraction notes; draft reference only.", "draft_reference_only", "no"),
        row("research/visualizations/persona_pc_rankings.csv", "outputs/tables/persona_pc_rankings.csv", "table", "S03", "Useful PC1/PC2/PC3 ranking table if user wants rank walkthrough.", "unresolved_need_user_review", "yes", notes="Currently untracked in source worktree; do not treat as canonical until reviewed/committed."),
        row("research/visualizations/persona_pc_rankings.md", "outputs/tables/persona_pc_rankings.md", "table", "S03", "Human-readable PC ranking table if user wants rank walkthrough.", "unresolved_need_user_review", "no", notes="Currently untracked in source worktree; do not treat as canonical until reviewed/committed."),
        row("/mnt/data/METHOD CARD-Lu et al. role-vector extraction.txt", "report/methodology/METHOD_CARD_Lu_role_vector_extraction.txt", "method_card", "S01,S02", "Requested method card if available.", "unresolved_need_user_review", "no", notes="Not present at mounted path during inspection."),
        row("/mnt/data/METHOD CARD-Adaptive role-vector extraction attempt.txt", "report/methodology/METHOD_CARD_Adaptive_role_vector_extraction_attempt.txt", "method_card", "S02", "Requested adaptive method card if available.", "unresolved_need_user_review", "no", notes="Not present at mounted path during recent inspection."),
    ]
    return rows


def build_exclusions() -> list[dict]:
    excluded = [
        ("research/outputs/h100_percentile_edge_validation/", "H100 measured activation validation; deferred from first clean Paper 1.5 core pass."),
        ("research/outputs/h100_percentile_edge_validation_error_analysis/", "H100 forecast-vs-observed arrow visualizations and regional error analysis; explicitly excluded."),
        ("research/outputs/h100_diagnostic_followups/", "H100 anomaly diagnostics and extraction-boundary checklist; deferred."),
        ("research/outputs/extraction_equivalence_audit/", "H100/source extraction equivalence audit; important but outside first core repo."),
        ("research/outputs/public_source_extraction_equivalence/", "Public-source extraction boundary audit; deferred with H100 material."),
        ("research/outputs/novel_prompt_battery/", "Prompt-battery generation for H100 validation; excluded."),
        ("research/outputs/novel_prompt_battery_expansion/", "Adaptive prompt-battery expansion; excluded."),
        ("research/outputs/novel_prompt_battery_percentile_edges/", "Final H100 prompt battery; excluded."),
        ("research/outputs/training_forecast_error_geometry/", "Forecast-arrow visualization/control analysis tied to H100 diagnostic phase; excluded first pass."),
        ("research/q2_stability/qwen/outputs/dyad_v1/", "Archived Paper 2/dyad dynamics direction, not Paper 1.5 core."),
        ("research/q2_stability/qwen/outputs/dyad_v2/", "Archived Paper 2/dyad dynamics direction, not Paper 1.5 core."),
        ("research/q2_stability/qwen/outputs/dyad_v3/", "Archived Paper 2/dyad dynamics direction, not Paper 1.5 core."),
        ("research/emotions/", "Separate emotion-vector work; not Paper 1.5 core."),
        ("research/diagnostic/", "Early diagnostic logs/scripts; not canonical report material."),
        ("visualizations/", "Older exploratory visualization directory; use `research/visualizations/persona_geometry_explorer.html` instead."),
        ("research/q2_stability/qwen/outputs/paper1_5/activations_trickster/", "Large activation shards; do not copy into clean lightweight repo."),
        ("research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl", "Large generated rollout JSONL; summarize via reports instead."),
    ]
    return [{"source_path": p, "reason_excluded": r, "archive_note": "Leave in source repo for provenance; do not include in first clean repo pass."} for p, r in excluded]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def traceability_rows() -> list[dict]:
    return [
        {"claim_or_number": "275 roles", "value": "275 non-default roles", "source_file": "research/outputs/role_rollout_artifact_audit/role_rollout_artifact_audit_report.md", "report_section": "S01", "status": "verified", "notes": "Also visible in data/roles/instructions excluding default."},
        {"claim_or_number": "5 positive instructions per role", "value": "275/275 non-default roles have 5 positive instructions", "source_file": "research/outputs/role_rollout_artifact_audit/role_prompt_reconstruction_inventory.csv", "report_section": "S01", "status": "verified", "notes": "Directory aggregate planned for copy."},
        {"claim_or_number": "240 extraction questions", "value": "240", "source_file": "data/extraction_questions.jsonl", "report_section": "S01", "status": "verified", "notes": "One JSONL row per question."},
        {"claim_or_number": "1,200 intended inputs per role", "value": "5 x 240 = 1,200", "source_file": "research/outputs/role_rollout_artifact_audit/role_rollout_artifact_audit_report.md", "report_section": "S01", "status": "verified", "notes": "Message-schema reconstruction; exact token strings depend on template/runtime."},
        {"claim_or_number": "Semantic baseline", "value": "mean R2 0.389397", "source_file": "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv", "report_section": "S04", "status": "verified", "notes": "semantic_baseline row, canonical_activation_pca3d target."},
        {"claim_or_number": "Procedural/Codex retained features", "value": "mean R2 0.490090", "source_file": "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv", "report_section": "S04", "status": "verified", "notes": "codex_retained row."},
        {"claim_or_number": "Big Five-style features", "value": "mean R2 0.612979", "source_file": "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_summary.csv", "report_section": "S04", "status": "verified", "notes": "claude_bigfive row."},
        {"claim_or_number": "Hierarchical trait-procedural model", "value": "mean R2 0.621799", "source_file": "research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/hierarchical_model_summary.csv", "report_section": "S04", "status": "verified", "notes": "hierarchical row."},
        {"claim_or_number": "Residual manifold hand-feature layer", "value": "mean R2 0.632", "source_file": "research/q2_stability/qwen/outputs/residual_manifold_analysis/residual_manifold_report.md", "report_section": "S04", "status": "verified", "notes": "Report model result section."},
        {"claim_or_number": "SVD15 lexical/register model", "value": "mean R2 0.707", "source_file": "research/q2_stability/qwen/outputs/residual_svd_interpretation/residual_svd_interpretation_report.md", "report_section": "S04", "status": "verified", "notes": "Report says sem+BigFive baseline 0.613 to SVD15 0.707."},
        {"claim_or_number": "PC3 perturbation-stabilization validation", "value": "global Pearson r about 0.529; cluster-controlled Pearson r about 0.491; pairwise ordering about 0.773", "source_file": "research/outputs/pc3_validation/pc3_validation_report.md", "report_section": "S03", "status": "verified", "notes": "Stats JSON also included in same output dir."},
        {"claim_or_number": "PC2 conditional abstraction result", "value": "abstraction predicts residual PC2 at r=-0.618", "source_file": "research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md", "report_section": "S03", "status": "verified", "notes": "Current PC2 interpretation support."},
        {"claim_or_number": "Prompt-to-geometry held-out role performance", "value": "mean R2 about 0.621", "source_file": "research/outputs/prompt_to_geometry_forecasting/forecasting_dataset_summary.md", "report_section": "S04/S05", "status": "optional_verified", "notes": "Include only if forecasting extension remains in first clean repo pass."},
    ]


def report_spine_rows() -> list[dict]:
    return [
        {"section_id": "S01", "title": "Public result and data reconstruction", "supporting_artifacts": "data/extraction_questions.jsonl; data/roles/instructions/; geometry_viz_data.json; prompt_artifact_inventory; role_rollout_artifact_audit; methodology cards", "notebook": "01_public_data_and_geometry.ipynb", "notes": "Show what is public, reconstructable, and not public."},
        {"section_id": "S02", "title": "Method uncertainty and stress testing", "supporting_artifacts": "assistant_axis_methodology; no_label_prompt_ablation; semantic_vs_activation_geometry; selected trickster/editor reports", "notebook": "02_stress_tests_and_stability.ipynb", "notes": "Exclude H100 extraction-equivalence diagnostics in first pass."},
        {"section_id": "S03", "title": "Interpreting persona geometry", "supporting_artifacts": "geometry_viz_data; persona_geometry_explorer; pc3_validation; pc2_conditional_validation; trait_persona_prediction; cluster_conditioned_axis_tests; interpretation notes", "notebook": "03_axis_interpretation.ipynb", "notes": "Present endpoint evidence separately from forcing-function interpretation."},
        {"section_id": "S04", "title": "Prediction-improvement sequence", "supporting_artifacts": "shared_latent_feature_benchmark; hierarchical_trait_procedural_model; residual_manifold_analysis; residual_svd_interpretation; optionally prompt_to_geometry_forecasting", "notebook": "04_prediction_improvement_sequence.ipynb", "notes": "Trace every R2 number to committed CSV/report."},
        {"section_id": "S05", "title": "What remains unresolved", "supporting_artifacts": "REPORT_SPINE.md; archive_index.md; source state docs", "notebook": "none", "notes": "Mention H100, extraction-boundary, response-state variance, instance-level forecasting, and adaptive register selection as deferred."},
    ]


def write_tree(path: Path) -> None:
    path.write_text(
        """# Proposed Clean Repo Tree

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
""",
        encoding="utf-8",
    )


def write_visualization_inventory(path: Path) -> None:
    path.write_text(
        """# Visualization Tool Inventory

## Canonical Include

Latest/main visualization tool: `research/visualizations/persona_geometry_explorer.html`.

Why this version is canonical:

- It is the active Persona Geometry Explorer under `research/visualizations/`, not the older top-level `visualizations/` exploratory pages.
- It uses embedded `VIZ_DATA` and no `fetch(` dependency.
- It supports PCA/UMAP, 2D/3D, axis swapping, fixed ranges, persistent selection, lasso/box selection, cluster colors, and Big Five-style overlays.
- Required rebuild/source data live beside it: `geometry_viz_data.json`, `cluster_assignments_full.json`, and `bigfive_geometry_overlay_data.json/.csv`.

## Explicit Exclusion

Do not include the H100 forecast-vs-observed arrow tools in the first clean repo pass:

- `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_3d_arrows.html`
- `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_2d_arrows_pc1_pc2.html`
- `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_2d_arrows_pc1_pc3.html`
- `research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_2d_arrows_pc2_pc3.html`

Those are useful later for the validation/calibration repo, but they would pull the first clean Paper 1.5 core repo toward H100 diagnostics rather than the report spine.
""",
        encoding="utf-8",
    )


def write_archive_index(path: Path, exclusions: list[dict]) -> None:
    lines = [
        "# Excluded Archive Index",
        "",
        "These materials remain in the source research repo and are intentionally excluded from the first clean Paper 1.5 core pass.",
        "",
    ]
    for item in exclusions:
        lines.append(f"- `{item['source_path']}`: {item['reason_excluded']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(path: Path, rows: list[dict], exclusions: list[dict]) -> None:
    canonical = [r for r in rows if r["canonical_status"] == "canonical_include"]
    optional = [r for r in rows if r["canonical_status"] == "optional_include"]
    unresolved = [r for r in rows if r["canonical_status"] == "unresolved_need_user_review"]
    total_size = 0
    for r in canonical:
        size = r["size_estimate"]
        if size != "missing":
            try:
                total_size += int(size.split()[0])
            except Exception:
                pass
    path.write_text(
        f"""# Clean Paper 1.5 Core Repo Copy Plan

- Generated UTC: {utc_now()}
- model_used: {MODEL_USED}
- Recommended clean repo name: `{PREFERRED_REPO_NAME}`
- Alternative repo name: `{ALT_REPO_NAME}`
- No files were copied, moved, deleted, or reorganized.

## Purpose

Create a small, auditable Paper 1.5 core repo that supports a technical report and notebook walkthrough. The source repo remains the research quarry. The clean repo should take a reader from public Assistant Axis artifacts through method/stability stress tests, persona-geometry interpretation, and the prediction-improvement sequence without requiring them to navigate H100 validation material or exploratory prompt-battery work.

## Summary Counts

- Canonical include rows: {len(canonical)}
- Optional include rows: {len(optional)}
- Draft-reference rows: {sum(1 for r in rows if r['canonical_status'] == 'draft_reference_only')}
- Unresolved/user-review rows: {len(unresolved)}
- Explicit exclusion rows: {len(exclusions)}
- Estimated canonical copied size: {total_size / (1024 * 1024):.2f} MB, excluding git/object overhead and future notebooks.

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

{chr(10).join(f"- `{r['source_path']}`: {r['notes_or_uncertainties']}" for r in unresolved)}

## Explicit First-Pass Exclusions

H100 validation outputs, H100 error-analysis arrow visualizations, extraction-boundary diagnostics, prompt-battery generation outputs, RunPod logs, large response JSONLs, activation shards, dyad dynamics, and emotion-vector work are excluded from this first clean repo pass. They remain important source-quarry material, but they would obscure the core Paper 1.5 report spine.

## Recommended Next Card

After reviewing this plan, run a separate copy-only card: create `../{PREFERRED_REPO_NAME}`, copy only rows marked `canonical_include` plus any user-approved optional/draft rows, generate `PROVENANCE.md` from `clean_repo_copy_plan.csv`, create stub notebooks from the notebook plan, and do not import H100/prompt-battery materials.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_copy_plan()
    exclusions = build_exclusions()
    write_csv(
        OUT_DIR / "clean_repo_copy_plan.csv",
        rows,
        [
            "source_path",
            "proposed_destination_path",
            "artifact_type",
            "report_section",
            "reason_to_include",
            "canonical_status",
            "required_for_notebook",
            "size_estimate",
            "hash_if_available",
            "dependencies",
            "notes_or_uncertainties",
        ],
    )
    write_csv(
        OUT_DIR / "canonical_claims_traceability_table.csv",
        traceability_rows(),
        ["claim_or_number", "value", "source_file", "report_section", "status", "notes"],
    )
    write_csv(
        OUT_DIR / "excluded_archive_index.csv",
        exclusions,
        ["source_path", "reason_excluded", "archive_note"],
    )
    write_csv(
        OUT_DIR / "report_spine_artifact_map.csv",
        report_spine_rows(),
        ["section_id", "title", "supporting_artifacts", "notebook", "notes"],
    )
    # Also write markdown versions requested by the task.
    (OUT_DIR / "report_spine_artifact_map.md").write_text(
        "# Report Spine Artifact Map\n\n"
        + "\n".join(
            f"## {r['section_id']} - {r['title']}\n\n- Notebook: `{r['notebook']}`\n- Supporting artifacts: {r['supporting_artifacts']}\n- Notes: {r['notes']}\n"
            for r in report_spine_rows()
        ),
        encoding="utf-8",
    )
    write_tree(OUT_DIR / "proposed_clean_repo_tree.md")
    write_visualization_inventory(OUT_DIR / "visualization_tool_inventory.md")
    write_archive_index(OUT_DIR / "excluded_archive_index.md", exclusions)
    write_report(OUT_DIR / "clean_repo_copy_plan_report.md", rows, exclusions)

    metadata = {
        "generated_utc": utc_now(),
        "model_used": MODEL_USED,
        "source_repo_head": os.popen("git rev-parse HEAD").read().strip(),
        "recommended_repo_name": PREFERRED_REPO_NAME,
        "files_copied": False,
        "canonical_include_count": sum(1 for r in rows if r["canonical_status"] == "canonical_include"),
        "optional_include_count": sum(1 for r in rows if r["canonical_status"] == "optional_include"),
        "unresolved_need_user_review_count": sum(1 for r in rows if r["canonical_status"] == "unresolved_need_user_review"),
        "exclusion_count": len(exclusions),
    }
    (OUT_DIR / "copy_plan_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote clean repo copy plan to {OUT_DIR}")


if __name__ == "__main__":
    main()
