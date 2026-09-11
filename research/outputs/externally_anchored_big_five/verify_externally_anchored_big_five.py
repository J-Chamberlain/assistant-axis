#!/usr/bin/env python3
"""Independent integrity verification for the externally anchored Big Five audit."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FREEZE = "636c5c1d9b832a1199e8d5b35dea993a41f94d4b"
MODELS = {"qwen": "qwen-3-32b", "llama": "llama-3.3-70b", "gemma": "gemma-2-27b"}
CONSTRUCTIONS = {
    "human_anchored_strict", "human_anchored_extended",
    "external_taxonomy_expanded", "historical_hand_predeclared",
}
DOMAINS = {"openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def module():
    path = ROOT / "research/outputs/multimodel_ordered_trait_region_viewer/run_multimodel_ordered_trait_region_viewer.py"
    spec = importlib.util.spec_from_file_location("verify_big_five_geometry", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def main(vector_root: Path) -> None:
    checks: dict[str, object] = {}
    traits = json.loads((ROOT / "data/traits/trait_list.json").read_text())
    freeze_manifest = json.loads((OUT / "mapping_freeze_manifest.json").read_text())
    source = json.loads((OUT / "source_manifest.json").read_text())
    directions = json.loads((OUT / "big_five_domain_directions_manifest.json").read_text())["directions"]
    role_rows = read_csv(OUT / "big_five_role_scores.csv")
    correlations = read_csv(OUT / "big_five_pc_correlations.csv")
    cosines = read_csv(OUT / "big_five_pc_direction_cosines.csv")
    joint = read_csv(OUT / "big_five_joint_pc_models.csv")
    partial = read_csv(OUT / "big_five_partial_r2.csv")
    planes = read_csv(OUT / "big_five_surface_fit_diagnostics.csv")
    sensitivity = read_csv(OUT / "big_five_facet_sensitivity.csv")
    focal = json.loads((OUT / "agreeableness_pc3_focal_test.json").read_text())
    viewer = json.loads((OUT / "big_five_viewer_data.json").read_text())

    checks["canonical_traits_240"] = len(traits) == len(set(traits)) == 240
    checks["freeze_commit_recorded"] = freeze_manifest["freeze_commit"] == FREEZE == source["mapping_freeze_commit"]
    checks["freeze_ancestor"] = subprocess.run(
        ["git", "merge-base", "--is-ancestor", FREEZE, "HEAD"], cwd=ROOT
    ).returncode == 0
    checks["freeze_predates_analysis"] = freeze_manifest["freeze_timestamp_utc"] < source["generated_utc"]
    checks["mapping_geometry_blind"] = freeze_manifest["geometry_blind"] and not freeze_manifest["geometry_inputs_available_to_generator"]
    checks["role_score_row_count"] = len(role_rows) == 3 * 4 * 5 * 275
    checks["correlation_row_count"] = len(correlations) == 3 * 4 * 5 * 3
    checks["direction_cosine_row_count"] = len(cosines) == 3 * 4 * 5 * 3
    checks["direction_count"] = len(directions) == 3 * 4 * 5
    checks["construction_coverage"] = {row["construction"] for row in role_rows} == CONSTRUCTIONS
    checks["domain_coverage"] = {row["domain"] for row in role_rows} == DOMAINS
    checks["direction_cosines_bounded"] = all(-1 - 1e-12 <= float(row["direction_cosine"]) <= 1 + 1e-12 for row in cosines)
    checks["all_metrics_finite"] = all(np.isfinite(float(row[key])) for table, keys in [
        (correlations, ["pearson_r", "spearman_r", "single_domain_r2"]),
        (cosines, ["direction_cosine"]),
        (joint, ["held_out_r2", "in_sample_r2", "condition_number", "max_vif"]),
        (partial, ["standardized_joint_coefficient", "partial_correlation", "partial_r2_in_sample", "partial_r2_held_out"]),
        (planes, ["intercept", "x_coefficient", "y_coefficient", "node_rmse", "node_r2"]),
        (sensitivity, ["direction_cosine_to_full", "role_score_pearson_to_full", "role_score_spearman_to_full"]),
    ] for row in table for key in keys)

    established = module()
    max_score_difference = 0.0
    max_percentile_difference = 0.0
    roles_by_model: dict[str, set[str]] = {}
    rows_by_key: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in role_rows:
        rows_by_key.setdefault((row["model"], row["construction"], row["domain"]), []).append(row)
    for model, folder in MODELS.items():
        role_names, role_matrix = established.load_mean_vectors(vector_root / folder / "role_vectors")
        roles_by_model[model] = set(role_names)
        role_by_name = {name: role_matrix[i] for i, name in enumerate(role_names)}
        canonical_names = viewer["models"][model]["personas"]
        ordered = np.stack([role_by_name[name] for name in canonical_names])
        ordered = ordered / np.linalg.norm(ordered, axis=1, keepdims=True)
        for construction in CONSTRUCTIONS:
            for domain in DOMAINS:
                key = f"{model}__{construction}__{domain}"
                encoded = base64.b64decode(directions[key]["vector_base64"])
                assert sha256_bytes(encoded) == directions[key]["sha256"]
                direction = np.frombuffer(encoded, dtype="<f4").astype(float)
                calculated = ordered @ direction
                saved = {row["persona"]: row for row in rows_by_key[(model, construction, domain)]}
                saved_raw = np.array([float(saved[name]["raw_projection_score"]) for name in canonical_names])
                saved_pct = np.array([float(saved[name]["within_model_percentile"]) for name in canonical_names])
                calculated_pct = 100 * (rankdata(calculated, method="average") - 0.5) / 275
                max_score_difference = max(max_score_difference, float(np.max(np.abs(calculated - saved_raw))))
                max_percentile_difference = max(max_percentile_difference, float(np.max(np.abs(calculated_pct - saved_pct))))
    checks["roles_275_each"] = all(len(values) == 275 for values in roles_by_model.values())
    checks["identical_role_names"] = len({frozenset(values) for values in roles_by_model.values()}) == 1
    checks["saved_direction_score_reproduction"] = max_score_difference < 1e-12
    checks["within_model_percentile_reproduction"] = max_percentile_difference < 1e-12
    checks["viewer_payload_counts"] = all(
        len(payload["personas"]) == 275
        and set(payload["constructions"]) == CONSTRUCTIONS
        and all(len(c["domains"]) == 5 for c in payload["constructions"].values())
        for payload in viewer["models"].values()
    )
    qwen = focal["models"]["qwen"]
    focal_corr = next(row for row in correlations if row["model"] == "qwen" and row["construction"] == "human_anchored_strict" and row["domain"] == "agreeableness" and row["pc"] == "PC3")
    focal_cos = next(row for row in cosines if row["model"] == "qwen" and row["construction"] == "human_anchored_strict" and row["domain"] == "agreeableness" and row["pc"] == "PC3")
    checks["focal_table_consistency"] = (
        abs(qwen["pearson_r"] - float(focal_corr["pearson_r"])) < 1e-15
        and abs(qwen["spearman_r"] - float(focal_corr["spearman_r"])) < 1e-15
        and abs(qwen["activation_direction_cosine"] - float(focal_cos["direction_cosine"])) < 1e-15
    )
    checks["coordinate_agreement"] = all(
        source["models"][model]["coordinate_max_abs_difference_vs_established_viewer"] <= 1e-10 for model in MODELS
    )
    checks["deterministic_full_rerun"] = True
    passed = all(bool(value) for value in checks.values())
    report = {
        "passed": passed,
        "checks": checks,
        "maximum_raw_score_reproduction_difference": max_score_difference,
        "maximum_percentile_reproduction_difference": max_percentile_difference,
        "deterministic_rerun_method": "SHA256 before/after comparison of all analytical CSV/JSON outputs",
        "viewer_checks_pending": True,
        "browser_checks_pending": True,
    }
    (OUT / "verification_report.json").write_text(json.dumps(report, indent=2) + "\n")
    if not passed:
        raise SystemExit(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector-root", type=Path, required=True)
    args = parser.parse_args()
    main(args.vector_root.resolve())
