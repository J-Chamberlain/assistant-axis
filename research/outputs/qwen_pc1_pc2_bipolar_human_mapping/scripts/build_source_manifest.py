#!/usr/bin/env python3
"""Build the AA-8 source manifest from exact commits and local canonical inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


STRICT_COMMIT = "6497d28383aac33ea9f61b6ce2ac2ff195dccae4"
BROAD_COMMIT = "db782414c6708f6fd2c46f3e5b08d0e61668b14d"
START_SHA = "8f4e589df5d92217e56f76a978d51df07af5aa3a"

COMMIT_SOURCES = [
    (STRICT_COMMIT, "research/outputs/qwen_trait_axis_specificity/qwen_axis_specific_marker_sets.csv", "strict .70-purity markers"),
    (STRICT_COMMIT, "research/outputs/qwen_trait_axis_specificity/qwen_trait_axis_specificity_metrics.csv", "strict specificity metrics"),
    (STRICT_COMMIT, "research/outputs/qwen_trait_axis_specificity/qwen_axis_specific_human_inventory.csv", "prior strict human inventory"),
    (STRICT_COMMIT, "research/outputs/qwen_pc_human_construct_bridge/human_construct_library.csv", "validated 126-construct library"),
    (BROAD_COMMIT, "research/outputs/qwen_pc_trait_specificity/qwen_trait_cross_pc_specificity_all.csv", "target-dominance and concentration metrics"),
    (BROAD_COMMIT, "research/outputs/qwen_pc_trait_specificity/qwen_pc_specificity_human_inventory.csv", "prior target-dominant human inventory"),
]

LOCAL_SOURCES = [
    ("research/outputs/role_geometry_instruction_inventory/qwen_role_geometry_with_positive_instructions.csv", "275 role coordinates, ranks, clusters, and instructions"),
    ("research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv", "696-item SAPA dictionary"),
    ("research/outputs/blind_pc_interpretation_rating_benchmark/blind_pc_interpretation_rating_report.md", "prior coordinate-blind interpretation evidence"),
    ("research/outputs/pc1_competing_theories_test/pc1_competing_theories_report.md", "PC1 competing-theories audit"),
    ("research/outputs/pc1_accountability_validation/accountability_validation_report.md", "focused PC1 activation evidence"),
    ("research/q2_stability/qwen/outputs/professional_hierarchy_validation/professional_hierarchy_report.md", "professional-role hierarchy"),
    ("research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_conditional_validation_report.md", "PC1-conditioned PC2 interpretation"),
    ("research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_extremes_report.md", "muted-PC1 PC2 role evidence"),
    ("research/outputs/cluster_conditioned_axis_tests/cluster_conditioned_axis_report.md", "cluster-conditioned PC1/PC2 evidence"),
    ("research/outputs/qwen_pc1_pc2_bipolar_human_mapping/pc2_coordinate_blind_role_ratings.csv", "AA-8 frozen coordinate-blind ratings"),
    ("research/outputs/qwen_pc1_pc2_bipolar_human_mapping/pc2_role_rating_freeze_manifest.json", "AA-8 rating freeze record"),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    sources = []
    for commit, path, role in COMMIT_SOURCES:
        data = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo)
        sources.append({"path": path, "source_commit": commit, "role": role, "bytes": len(data), "sha256": digest(data)})
    for path, role in LOCAL_SOURCES:
        file = repo / path
        data = file.read_bytes()
        sources.append({"path": path, "source_commit": START_SHA if "qwen_pc1_pc2" not in path else "AA8_BRANCH", "role": role, "bytes": len(data), "sha256": digest(data)})
    manifest = {
        "analysis": "AA-8 bipolar interpretation and SAPA measurement reconsideration for Qwen PC1 and PC2",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "model_under_study": "Qwen/Qwen3-32B",
        "model_used_for_interpretive_synthesis": "GPT-5.5",
        "canonical_starting_sha": START_SHA,
        "source_branches": {
            "strict_axis_specificity": {"branch": "codex/aa1-qwen-axis-specificity", "commit": STRICT_COMMIT},
            "target_dominance_specificity": {"branch": "codex/aa1-qwen-pc-trait-specificity", "commit": BROAD_COMMIT},
        },
        "coordinate_blind_rating_freeze_commit": "06b605d210b2a16d63682719af565781025dad31",
        "model_evidence_packet_freeze_commit": "61daa40",
        "specificity_evidence_hierarchy": {
            "pc_associated": 328,
            "pc_defining_target_dominant": 202,
            "strict_point70_purity": 88,
            "highly_concentrated": 70,
        },
        "sources": sources,
        "pc3_reference_only": {
            "formula": "mean(percentile(empathetic), percentile(agreeable), percentile(altruistic)) with equal weights",
            "correlations": {"PC1": -0.110061, "PC2": -0.011574, "PC3": -0.944857, "PC4": 0.049736, "PC5": 0.061208, "PC6": -0.038998},
            "specificity_margin": 0.834796,
            "pc1_pc6_concentration": 0.978101,
            "selection_or_mapping_reopened": False,
        },
        "firewall": {
            "specificity_rerun_or_retuned": False,
            "human_respondent_rows_loaded_or_scored": False,
            "human_projection_performed": False,
            "human_model_correspondence_test_run": False,
            "llama_or_gemma_scientific_data_used": False,
            "AA7_result_used_to_choose_interpretation": False,
            "NLSY_outcomes_used": False,
            "next_experiment_selected": False,
            "respondent_level_microdata_committed": False,
        },
        "compute": "CPU only; no GPU, RunPod, model-under-study inference, activation extraction, response generation, or external model API.",
    }
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
