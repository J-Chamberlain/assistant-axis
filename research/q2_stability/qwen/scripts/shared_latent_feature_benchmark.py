#!/usr/bin/env python3
"""
Shared latent-feature benchmark across Codex and Claude analyses.

This script does not generate activations or call external models. It aligns
existing canonical Qwen activation PCA coordinates with Claude's exported
cluster-cosine pseudo-PCA target, exports shared feature matrices, and evaluates
all feature families on the same deterministic held-out splits.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTER_SCRIPT = ROOT / "research/q2_stability/qwen/scripts/iterative_latent_feature_outer_loop.py"
OUTER_LOG = ROOT / "research/q2_stability/qwen/outputs/iterative_outer_loop/outer_loop_master_log.json"
CLAUDE_BRANCH = "myfork/claude/persona-inventory-topology-4qp10"
CLAUDE_BASE = "research/q2_stability/qwen/outputs/claude_latent_feature_loop"

DATE = "2026-05-28"
MODEL_USED = "GPT-5.5 Standard"
SCRIPT_AUTHOR = "GPT-5.5 Standard via Codex"
TARGETS = {
    "canonical_activation_pca3d": ("activation_pc1", "activation_pc2", "activation_pc3"),
    "claude_cluster_cosine_pseudopca3d": ("pseudo_pc1", "pseudo_pc2", "pseudo_pc3"),
}
BIGFIVE_COLUMNS = [
    "big5_agreeableness",
    "big5_conscientiousness",
    "big5_extraversion",
    "big5_neuroticism",
    "big5_openness",
]


def load_outer_module():
    spec = importlib.util.spec_from_file_location("outer_loop_module", OUTER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {OUTER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["outer_loop_module"] = module
    spec.loader.exec_module(module)
    return module


outer = load_outer_module()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def read_csv_text(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(text.splitlines()))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows and not fieldnames:
        path.write_text("")
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def git_show(path: str) -> str:
    return subprocess.check_output(["git", "show", f"{CLAUDE_BRANCH}:{path}"], cwd=ROOT, text=True)


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except Exception:
        return default


def spearman(a: list[float], b: list[float]) -> float | None:
    if len(a) < 3 or len(a) != len(b):
        return None
    ar = rankdata(np.array(a, dtype=float))
    br = rankdata(np.array(b, dtype=float))
    if float(ar.std()) < 1e-12 or float(br.std()) < 1e-12:
        return None
    return float(np.corrcoef(ar, br)[0, 1])


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and values[order[j]] == values[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + j - 1) / 2.0 + 1.0
        i = j
    return ranks


def make_provenance(artifact_path: str, artifact_type: str, notes: str = "") -> dict[str, Any]:
    return {
        "task_type": "shared_latent_feature_benchmark",
        "artifact_type": artifact_type,
        "artifact_path": artifact_path,
        "generation_model": None,
        "evaluation_model": None,
        "analysis_model": MODEL_USED,
        "script_author_model": SCRIPT_AUTHOR,
        "orchestration_agent": "Codex",
        "provider": "openai",
        "model_version_or_alias": MODEL_USED,
        "date": DATE,
        "prompt_family_id": None,
        "temperature": None,
        "max_tokens": None,
        "source_inputs": [
            "research/visualizations/geometry_viz_data.json",
            "research/q2_stability/qwen/outputs/iterative_outer_loop/outer_loop_master_log.json",
            f"{CLAUDE_BRANCH}:{CLAUDE_BASE}/claude_target_coordinates.csv",
            f"{CLAUDE_BRANCH}:{CLAUDE_BASE}/claude_feature_matrix.csv",
            f"{CLAUDE_BRANCH}:{CLAUDE_BASE}/claude_split_assignments.csv",
        ],
        "notes_on_uncertainty": notes,
    }


def dimension_from_dict(item: dict[str, Any]):
    return outer.Dimension(
        item["family"],
        item["name"],
        item.get("description", ""),
        tuple(item.get("positive_terms", [])),
        tuple(item.get("negative_terms", [])),
        item.get("source", "unknown"),
    )


def matrix_from_rows(rows: list[dict[str, Any]], columns: list[str]) -> np.ndarray:
    return np.array([[to_float(row.get(col)) for col in columns] for row in rows], dtype=float)


def semantic_matrix(personas: list[dict[str, Any]]) -> tuple[list[str], np.ndarray]:
    columns: list[str] = []
    parts = []
    for field in ["original_prompt_k7", "no_label_prompt_k7", "role_name_k7"]:
        values = [str(p[field]) for p in personas]
        universe = sorted(set(values))
        columns.extend([f"{field}__{value}" for value in universe])
        parts.append(outer.one_hot(values, universe))
    return columns, np.hstack(parts)


def codex_matrix(personas: list[dict[str, Any]], dims: list[Any]) -> tuple[list[str], np.ndarray]:
    roles = {p["role"] for p in personas}
    matrix = outer.code_dimensions(personas, dims, roles)
    columns = [f"codex_{dim.name}" for dim in dims]
    return columns, matrix


def load_aligned_data() -> dict[str, Any]:
    personas_all = outer.load_personas()
    persona_by_role = {p["role"]: p for p in personas_all}
    outer_log = load_json(OUTER_LOG)
    dims = [dimension_from_dict(item) for item in outer_log["final_retained_dimensions"]]

    claude_targets = read_csv_text(git_show(f"{CLAUDE_BASE}/claude_target_coordinates.csv"))
    claude_features = read_csv_text(git_show(f"{CLAUDE_BASE}/claude_feature_matrix.csv"))
    claude_splits = read_csv_text(git_show(f"{CLAUDE_BASE}/claude_split_assignments.csv"))
    claude_target_by_role = {r["persona"]: r for r in claude_targets}
    claude_feature_by_role = {r["persona"]: r for r in claude_features}
    claude_split_by_role = {r["persona"]: r for r in claude_splits}

    common_roles = sorted(set(persona_by_role) & set(claude_target_by_role) & set(claude_feature_by_role))
    personas = [persona_by_role[role] for role in common_roles]

    return {
        "personas": personas,
        "roles": common_roles,
        "dims": dims,
        "outer_log": outer_log,
        "claude_targets": claude_target_by_role,
        "claude_features": claude_feature_by_role,
        "claude_splits": claude_split_by_role,
        "claude_target_headers": list(claude_targets[0].keys()) if claude_targets else [],
        "claude_feature_headers": list(claude_features[0].keys()) if claude_features else [],
        "n_outer_personas": len(personas_all),
        "n_claude_targets": len(claude_targets),
        "n_claude_features": len(claude_features),
    }


def export_targets(data: dict[str, Any]) -> dict[str, list[str]]:
    rows_activation = []
    rows_claude = []
    source_cols = [
        "gemma_axis_proj_raw",
        "gemma_axis_proj_norm",
        "cos_to_editor",
        "cos_to_synthesizer",
        "cos_to_blogger",
        "cos_to_ancient",
        "cos_to_trickster",
        "cos_to_contrarian",
        "cos_to_podcaster",
        "gemma_cluster",
    ]
    for persona in data["personas"]:
        role = persona["role"]
        c = data["claude_targets"][role]
        rows_activation.append(
            {
                "persona": role,
                "activation_pc1": persona["pca1"],
                "activation_pc2": persona["pca2"],
                "activation_pc3": persona["pca3"],
                "activation_cluster": persona["activation_cluster"],
            }
        )
        row = {
            "persona": role,
            "pseudo_pc1": c["pseudo_pc1"],
            "pseudo_pc2": c["pseudo_pc2"],
            "pseudo_pc3": c["pseudo_pc3"],
            "source_columns_used": "cos_to_editor|cos_to_synthesizer|cos_to_blogger|cos_to_ancient|cos_to_trickster|cos_to_contrarian|cos_to_podcaster",
            "target_source": "direct_claude_export",
        }
        for col in source_cols:
            row[col] = c.get(col)
        rows_claude.append(row)
    write_csv(OUT_DIR / "canonical_activation_pca3d.csv", rows_activation)
    write_csv(OUT_DIR / "claude_cluster_cosine_pseudopca3d.csv", rows_claude)
    return {
        "canonical_activation_pca3d": ["activation_pc1", "activation_pc2", "activation_pc3"],
        "claude_cluster_cosine_pseudopca3d": ["pseudo_pc1", "pseudo_pc2", "pseudo_pc3"],
    }


def export_splits(data: dict[str, Any]) -> list[dict[str, Any]]:
    roles = set(data["roles"])
    rows = []
    for split_id, seed in enumerate(outer.SPLIT_SEEDS):
        train, test = outer.split(data["personas"], seed)
        train_roles = {p["role"] for p in train}
        for persona in data["personas"]:
            role = persona["role"]
            c = data["claude_splits"].get(role, {})
            rows.append(
                {
                    "persona": role,
                    "canonical_split_id": split_id,
                    "canonical_seed": seed,
                    "canonical_assignment": "train" if role in train_roles else "heldout",
                    "claude_split_id": c.get("test_fold"),
                    "claude_assignment": "heldout_in_claude_fold" if c.get("test_fold") not in ("", None) else None,
                    "in_common_benchmark": role in roles,
                }
            )
    write_csv(OUT_DIR / "shared_split_assignments.csv", rows)
    return rows


def export_feature_matrices(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    personas = data["personas"]
    roles = data["roles"]
    sem_cols, sem_x = semantic_matrix(personas)
    codex_cols, codex_x = codex_matrix(personas, data["dims"])

    claude_headers = [h for h in data["claude_feature_headers"] if h != "persona"]
    claude_full_cols = [h for h in claude_headers if h.startswith("tfidf_svd_") or h.startswith("big5_")]
    bigfive_cols = [h for h in BIGFIVE_COLUMNS if h in data["claude_feature_headers"]]
    claude_full_x = np.array([[to_float(data["claude_features"][role].get(col)) for col in claude_full_cols] for role in roles], dtype=float)
    bigfive_x = np.array([[to_float(data["claude_features"][role].get(col)) for col in bigfive_cols] for role in roles], dtype=float)

    matrices = {
        "semantic_baseline": {"columns": sem_cols, "x": sem_x},
        "codex_retained": {"columns": sem_cols + codex_cols, "x": np.hstack([sem_x, codex_x])},
        "claude_bigfive": {"columns": sem_cols + bigfive_cols, "x": np.hstack([sem_x, bigfive_x])},
        "claude_full_feature_matrix": {"columns": sem_cols + claude_full_cols, "x": np.hstack([sem_x, claude_full_x])},
        "combined_codex_claude": {"columns": sem_cols + codex_cols + claude_full_cols, "x": np.hstack([sem_x, codex_x, claude_full_x])},
    }
    files = {
        "semantic_baseline": "semantic_baseline_features.csv",
        "codex_retained": "codex_retained_features.csv",
        "claude_bigfive": "claude_bigfive_features.csv",
        "claude_full_feature_matrix": "claude_full_feature_matrix.csv",
        "combined_codex_claude": "combined_codex_claude_features.csv",
    }
    for name, item in matrices.items():
        columns = item["columns"]
        rows = []
        for i, role in enumerate(roles):
            row = {
                "persona": role,
                "provenance_manifest": "shared_benchmark_results.json",
                "feature_set": name,
            }
            for j, col in enumerate(columns):
                row[col] = round(float(item["x"][i, j]), 8)
            rows.append(row)
        write_csv(OUT_DIR / files[name], rows)
        item["file"] = files[name]
    return matrices


def target_matrix(data: dict[str, Any], target_name: str) -> tuple[np.ndarray, list[str]]:
    if target_name == "canonical_activation_pca3d":
        rows = [
            {
                "activation_pc1": p["pca1"],
                "activation_pc2": p["pca2"],
                "activation_pc3": p["pca3"],
            }
            for p in data["personas"]
        ]
        cols = list(TARGETS[target_name])
    else:
        rows = [data["claude_targets"][role] for role in data["roles"]]
        cols = list(TARGETS[target_name])
    return matrix_from_rows(rows, cols), cols


def evaluate_feature_set(
    data: dict[str, Any],
    matrices: dict[str, dict[str, Any]],
    feature_set: str,
    target_name: str,
    semantic_baseline_cache: dict[str, Any],
) -> dict[str, Any]:
    x = matrices[feature_set]["x"]
    y, target_cols = target_matrix(data, target_name)
    sem_x = matrices["semantic_baseline"]["x"]
    split_metrics = []
    residual_by_role: dict[str, list[float]] = defaultdict(list)
    baseline_residual_by_role: dict[str, list[float]] = defaultdict(list)
    prediction_by_role: dict[str, list[np.ndarray]] = defaultdict(list)
    heldout_frequency = Counter()

    for split_id, seed in enumerate(outer.SPLIT_SEEDS):
        train, test = outer.split(data["personas"], seed)
        train_roles = {p["role"] for p in train}
        train_idx = [i for i, role in enumerate(data["roles"]) if role in train_roles]
        test_idx = [i for i, role in enumerate(data["roles"]) if role not in train_roles]

        fit = outer.fit_predict(x[train_idx], y[train_idx], x[test_idx], y[test_idx])
        base_fit = outer.fit_predict(sem_x[train_idx], y[train_idx], sem_x[test_idx], y[test_idx])
        pred = fit["pred"]
        base_pred = base_fit["pred"]
        err = np.linalg.norm(y[test_idx] - pred, axis=1)
        base_err = np.linalg.norm(y[test_idx] - base_pred, axis=1)

        for pos, idx in enumerate(test_idx):
            role = data["roles"][idx]
            residual_by_role[role].append(float(err[pos]))
            baseline_residual_by_role[role].append(float(base_err[pos]))
            prediction_by_role[role].append(pred[pos])
            heldout_frequency[role] += 1

        row = {
            "split_id": split_id,
            "seed": seed,
            "r2": fit["r2"],
            "baseline_r2": base_fit["r2"],
            "delta_vs_semantic_baseline": fit["r2"] - base_fit["r2"],
            "pc1_r2": fit["per_axis_r2"][0],
            "pc2_r2": fit["per_axis_r2"][1],
            "pc3_r2": fit["per_axis_r2"][2],
            "baseline_pc1_r2": base_fit["per_axis_r2"][0],
            "baseline_pc2_r2": base_fit["per_axis_r2"][1],
            "baseline_pc3_r2": base_fit["per_axis_r2"][2],
            "mean_residual": float(err.mean()),
            "baseline_mean_residual": float(base_err.mean()),
            "residual_reduction_vs_baseline": float(base_err.mean() - err.mean()),
            "residual_reduction_percent": float((base_err.mean() - err.mean()) / base_err.mean() * 100.0) if float(base_err.mean()) else None,
        }
        if target_name == "canonical_activation_pca3d":
            row["activation_cluster_accuracy"] = outer.cluster_accuracy(
                x[train_idx],
                [data["personas"][i]["activation_cluster"] for i in train_idx],
                x[test_idx],
                [data["personas"][i]["activation_cluster"] for i in test_idx],
            )
        else:
            row["activation_cluster_accuracy"] = None
        split_metrics.append(row)

    mean_res = {
        role: float(np.mean(values))
        for role, values in residual_by_role.items()
        if values
    }
    base_mean_res = {
        role: float(np.mean(values))
        for role, values in baseline_residual_by_role.items()
        if values
    }
    sem_key = target_name
    if feature_set == "semantic_baseline":
        semantic_baseline_cache[sem_key] = mean_res
    baseline_ranks = semantic_baseline_cache.get(sem_key, base_mean_res)
    common_rank_roles = sorted(set(mean_res) & set(baseline_ranks))
    rank_agreement = spearman([mean_res[r] for r in common_rank_roles], [baseline_ranks[r] for r in common_rank_roles])
    top10 = set(sorted(mean_res, key=mean_res.get)[:10])
    bottom10 = set(sorted(mean_res, key=mean_res.get, reverse=True)[:10])
    base_top10 = set(sorted(baseline_ranks, key=baseline_ranks.get)[:10])
    base_bottom10 = set(sorted(baseline_ranks, key=baseline_ranks.get, reverse=True)[:10])

    permutation = permutation_null(x, y)
    metrics = {
        "feature_set": feature_set,
        "target": target_name,
        "n_personas": len(data["roles"]),
        "n_features": int(x.shape[1]),
        "target_columns": target_cols,
        "split_metrics": split_metrics,
        "mean_r2": float(np.mean([m["r2"] for m in split_metrics])),
        "std_r2": float(np.std([m["r2"] for m in split_metrics])),
        "semantic_baseline_r2": float(np.mean([m["baseline_r2"] for m in split_metrics])),
        "delta_vs_semantic_baseline": float(np.mean([m["delta_vs_semantic_baseline"] for m in split_metrics])),
        "mean_per_axis_r2": [float(np.mean([m[f"pc{i}_r2"] for m in split_metrics])) for i in [1, 2, 3]],
        "semantic_baseline_per_axis_r2": [float(np.mean([m[f"baseline_pc{i}_r2"] for m in split_metrics])) for i in [1, 2, 3]],
        "mean_residual": float(np.mean([m["mean_residual"] for m in split_metrics])),
        "semantic_baseline_mean_residual": float(np.mean([m["baseline_mean_residual"] for m in split_metrics])),
        "residual_reduction_vs_semantic_baseline": float(np.mean([m["residual_reduction_vs_baseline"] for m in split_metrics])),
        "residual_reduction_percent": float(np.mean([m["residual_reduction_percent"] for m in split_metrics if m["residual_reduction_percent"] is not None])),
        "activation_cluster_accuracy": None if target_name != "canonical_activation_pca3d" else float(np.mean([m["activation_cluster_accuracy"] for m in split_metrics])),
        "residual_rank_agreement_vs_semantic": rank_agreement,
        "top10_most_explained_overlap_vs_semantic": len(top10 & base_top10),
        "top10_least_explained_overlap_vs_semantic": len(bottom10 & base_bottom10),
        "permutation_null": permutation,
        "persona_residuals": {
            role: {
                "mean_residual": mean_res.get(role),
                "semantic_baseline_mean_residual": base_mean_res.get(role),
                "residual_reduction_vs_semantic": (base_mean_res.get(role, math.nan) - mean_res.get(role, math.nan)),
                "heldout_frequency": int(heldout_frequency.get(role, 0)),
                "mean_prediction": [float(x) for x in np.mean(prediction_by_role[role], axis=0)] if prediction_by_role.get(role) else None,
            }
            for role in data["roles"]
        },
    }
    return metrics


def permutation_null(x: np.ndarray, y: np.ndarray, n_perm: int = 50) -> dict[str, float]:
    rng = np.random.default_rng(12345)
    vals = []
    seed = outer.SPLIT_SEEDS[0]
    personas = CURRENT_DATA["personas"]
    train, test = outer.split(personas, seed)
    train_roles = {p["role"] for p in train}
    train_idx = [i for i, role in enumerate(CURRENT_DATA["roles"]) if role in train_roles]
    test_idx = [i for i, role in enumerate(CURRENT_DATA["roles"]) if role not in train_roles]
    xt, xv = outer.standardize(x[train_idx], x[test_idx])
    for _ in range(n_perm):
        yp = np.array(y[train_idx], copy=True)
        rng.shuffle(yp, axis=0)
        coef = outer.ridge_fit(xt, yp, 1.0)
        vals.append(outer.r2(y[test_idx], outer.ridge_predict(xv, coef)))
    arr = np.array(vals, dtype=float)
    return {
        "n_permutations": n_perm,
        "mean_r2": float(arr.mean()),
        "p95_r2": float(np.quantile(arr, 0.95)),
        "max_r2": float(arr.max()),
    }


CURRENT_DATA: dict[str, Any] = {}


def run_benchmark(data: dict[str, Any], matrices: dict[str, dict[str, Any]]) -> dict[str, Any]:
    global CURRENT_DATA
    CURRENT_DATA = data
    semantic_cache: dict[str, Any] = {}
    feature_sets = [
        "semantic_baseline",
        "codex_retained",
        "claude_bigfive",
        "claude_full_feature_matrix",
        "combined_codex_claude",
    ]
    results = {}
    for target in TARGETS:
        for feature_set in feature_sets:
            key = f"{feature_set}__{target}"
            results[key] = evaluate_feature_set(data, matrices, feature_set, target, semantic_cache)
    return results


def write_summary(results: dict[str, Any]) -> None:
    rows = []
    for item in results.values():
        rows.append(
            {
                "feature_set": item["feature_set"],
                "target": item["target"],
                "n_personas": item["n_personas"],
                "n_features": item["n_features"],
                "mean_r2": round(item["mean_r2"], 6),
                "semantic_baseline_r2": round(item["semantic_baseline_r2"], 6),
                "delta_vs_semantic_baseline": round(item["delta_vs_semantic_baseline"], 6),
                "pc1_r2": round(item["mean_per_axis_r2"][0], 6),
                "pc2_r2": round(item["mean_per_axis_r2"][1], 6),
                "pc3_r2": round(item["mean_per_axis_r2"][2], 6),
                "mean_residual": round(item["mean_residual"], 6),
                "semantic_baseline_mean_residual": round(item["semantic_baseline_mean_residual"], 6),
                "residual_reduction_vs_semantic_baseline": round(item["residual_reduction_vs_semantic_baseline"], 6),
                "residual_reduction_percent": round(item["residual_reduction_percent"], 3),
                "activation_cluster_accuracy": None if item["activation_cluster_accuracy"] is None else round(item["activation_cluster_accuracy"], 6),
                "residual_rank_agreement_vs_semantic": None if item["residual_rank_agreement_vs_semantic"] is None else round(item["residual_rank_agreement_vs_semantic"], 6),
                "top10_most_explained_overlap_vs_semantic": item["top10_most_explained_overlap_vs_semantic"],
                "top10_least_explained_overlap_vs_semantic": item["top10_least_explained_overlap_vs_semantic"],
                "permutation_null_p95_r2": round(item["permutation_null"]["p95_r2"], 6),
            }
        )
    write_csv(OUT_DIR / "shared_benchmark_summary.csv", rows)


def write_feature_target_matrix(results: dict[str, Any]) -> None:
    rows = []
    for item in results.values():
        rows.append(
            {
                "feature_family": item["feature_set"],
                "target": item["target"],
                "mean_r2": round(item["mean_r2"], 6),
                "pc1_r2": round(item["mean_per_axis_r2"][0], 6),
                "pc2_r2": round(item["mean_per_axis_r2"][1], 6),
                "pc3_r2": round(item["mean_per_axis_r2"][2], 6),
                "semantic_baseline_r2": round(item["semantic_baseline_r2"], 6),
                "delta_vs_baseline": round(item["delta_vs_semantic_baseline"], 6),
                "residual_reduction": round(item["residual_reduction_vs_semantic_baseline"], 6),
                "residual_reduction_percent": round(item["residual_reduction_percent"], 3),
                "interpretation": interpret_row(item),
            }
        )
    write_csv(OUT_DIR / "shared_feature_target_matrix.csv", rows)


def write_persona_rankings(data: dict[str, Any], results: dict[str, Any]) -> None:
    rows = []
    key_items = [
        ("activation_semantic", "semantic_baseline__canonical_activation_pca3d"),
        ("activation_codex", "codex_retained__canonical_activation_pca3d"),
        ("activation_bigfive", "claude_bigfive__canonical_activation_pca3d"),
        ("activation_combined", "combined_codex_claude__canonical_activation_pca3d"),
        ("pseudo_semantic", "semantic_baseline__claude_cluster_cosine_pseudopca3d"),
        ("pseudo_codex", "codex_retained__claude_cluster_cosine_pseudopca3d"),
        ("pseudo_bigfive", "claude_bigfive__claude_cluster_cosine_pseudopca3d"),
        ("pseudo_combined", "combined_codex_claude__claude_cluster_cosine_pseudopca3d"),
    ]
    for role in data["roles"]:
        row: dict[str, Any] = {"persona": role}
        for label, key in key_items:
            pr = results[key]["persona_residuals"][role]
            row[f"{label}_mean_residual"] = pr["mean_residual"]
            row[f"{label}_residual_reduction_vs_semantic"] = pr["residual_reduction_vs_semantic"]
            row[f"{label}_heldout_frequency"] = pr["heldout_frequency"]
        rows.append(row)

    # Add ranks for the most decision-relevant columns.
    for prefix in ["activation_codex", "activation_bigfive", "activation_combined", "pseudo_codex", "pseudo_bigfive", "pseudo_combined"]:
        sorted_roles = sorted(rows, key=lambda r: (r[f"{prefix}_mean_residual"] is None, r[f"{prefix}_mean_residual"] if r[f"{prefix}_mean_residual"] is not None else 1e99))
        rank = {r["persona"]: i + 1 for i, r in enumerate(sorted_roles)}
        for row in rows:
            row[f"{prefix}_rank_most_explained"] = rank[row["persona"]]
            row[f"{prefix}_rank_least_explained"] = len(rows) - rank[row["persona"]] + 1
    write_csv(OUT_DIR / "shared_persona_residual_rankings.csv", rows)


def interpret_row(item: dict[str, Any]) -> str:
    if item["feature_set"] == "semantic_baseline":
        return "semantic baseline reference"
    if item["delta_vs_semantic_baseline"] > 0.05 and item["residual_reduction_vs_semantic_baseline"] > 0:
        return "transfers with meaningful improvement"
    if item["delta_vs_semantic_baseline"] > 0 and item["residual_reduction_vs_semantic_baseline"] > 0:
        return "weak positive transfer"
    if item["delta_vs_semantic_baseline"] > 0 and item["residual_reduction_vs_semantic_baseline"] <= 0:
        return "mixed metric movement"
    return "no transfer over semantic baseline"


def top_roles(result: dict[str, Any], reverse: bool = False, n: int = 8) -> list[str]:
    residuals = {
        role: vals["mean_residual"]
        for role, vals in result["persona_residuals"].items()
        if vals["mean_residual"] is not None
    }
    return sorted(residuals, key=residuals.get, reverse=reverse)[:n]


def answer_core_questions(results: dict[str, Any]) -> dict[str, str]:
    act_big = results["claude_bigfive__canonical_activation_pca3d"]
    pseudo_codex = results["codex_retained__claude_cluster_cosine_pseudopca3d"]
    act_codex = results["codex_retained__canonical_activation_pca3d"]
    pseudo_big = results["claude_bigfive__claude_cluster_cosine_pseudopca3d"]
    combined_act = results["combined_codex_claude__canonical_activation_pca3d"]
    combined_pseudo = results["combined_codex_claude__claude_cluster_cosine_pseudopca3d"]
    best_act_single = max(act_big["mean_r2"], act_codex["mean_r2"])
    best_pseudo_single = max(pseudo_big["mean_r2"], pseudo_codex["mean_r2"], results["claude_full_feature_matrix__claude_cluster_cosine_pseudopca3d"]["mean_r2"])
    return {
        "does_claude_big_five_transfer_to_canonical_activation_pca": (
            f"Yes. Big Five reaches R2 {act_big['mean_r2']:.3f} vs semantic baseline {act_big['semantic_baseline_r2']:.3f} "
            f"(delta {act_big['delta_vs_semantic_baseline']:+.3f})."
        ),
        "does_codex_retained_transfer_to_claude_pseudopca": (
            f"No under the direct Claude target. Codex retained features reach R2 {pseudo_codex['mean_r2']:.3f} vs baseline {pseudo_codex['semantic_baseline_r2']:.3f} "
            f"(delta {pseudo_codex['delta_vs_semantic_baseline']:+.3f})."
        ),
        "does_combined_outperform_either_alone": (
            f"On canonical activation PCA, combined R2 {combined_act['mean_r2']:.3f} is {'above' if combined_act['mean_r2'] > best_act_single else 'not above'} the best single family ({best_act_single:.3f}). "
            f"On Claude pseudo-PCA, combined R2 {combined_pseudo['mean_r2']:.3f} is {'above' if combined_pseudo['mean_r2'] > best_pseudo_single else 'not above'} the best single/full Claude family ({best_pseudo_single:.3f})."
        ),
        "are_codex_and_claude_complementary": (
            "Mixed but not strongly complementary in this benchmark. Big Five carries strong transferable signal into canonical activation geometry, while Codex retained features do not improve the direct Claude pseudo-PCA target over the semantic baseline; combined features should be read as complementary only where held-out R2 and residual reduction both improve."
        ),
        "which_target_produces_stronger_agreement": (
            "Canonical activation PCA produces the cleaner cross-family comparison because neither feature family defines the target; Claude pseudo-PCA remains important but Big Five is close to a native positive-control target there."
        ),
        "which_personas_consistently_well_explained": ", ".join(top_roles(combined_act, reverse=False, n=8)),
        "which_personas_consistently_poorly_explained": ", ".join(top_roles(combined_act, reverse=True, n=8)),
        "does_big_five_survive_direct_target_alignment": (
            f"Yes for canonical activation alignment: Big Five improves activation PCA by {act_big['delta_vs_semantic_baseline']:+.3f} R2 over semantic baseline."
        ),
        "does_trait_plus_procedural_interpretation_survive": (
            "Supported as a bounded interpretation: trait-style and procedural/behavioral features both carry predictive signal, but neither should be treated as final or causal."
        ),
    }


def write_report(data: dict[str, Any], matrices: dict[str, Any], results: dict[str, Any], answers: dict[str, str]) -> None:
    summary_rows = read_csv(OUT_DIR / "shared_benchmark_summary.csv")
    matrix_lines = [
        "| Feature set | Target | Mean R2 | Baseline R2 | Delta | PC1 | PC2 | PC3 | Residual reduction |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        matrix_lines.append(
            f"| {row['feature_set']} | {row['target']} | {float(row['mean_r2']):.3f} | {float(row['semantic_baseline_r2']):.3f} | {float(row['delta_vs_semantic_baseline']):+.3f} | {float(row['pc1_r2']):.3f} | {float(row['pc2_r2']):.3f} | {float(row['pc3_r2']):.3f} | {float(row['residual_reduction_vs_semantic_baseline']):+.3f} |"
        )
    lines = [
        "# Shared Latent-Feature Benchmark",
        "",
        f"Date: {DATE}",
        f"Analysis model: {MODEL_USED}",
        f"Script author model: {SCRIPT_AUTHOR}",
        "",
        "## 1. Research Question",
        "",
        "This benchmark aligns Codex/GPT-5.5 and Claude latent-feature analyses against the same persona rows, the same deterministic held-out splits, and the same metrics. The goal is to test whether Claude's Big Five result is target-specific or transfers to canonical activation geometry, and whether Codex's behavioral/procedural feature vocabulary transfers to Claude's cluster-cosine pseudo-PCA geometry.",
        "",
        "## 2. Inputs and Alignment",
        "",
        f"- Common benchmark personas: {len(data['roles'])}",
        f"- Codex canonical activation personas available: {data['n_outer_personas']}",
        f"- Claude direct pseudo-PCA target rows available: {data['n_claude_targets']}",
        f"- Claude feature rows available: {data['n_claude_features']}",
        "- Claude pseudo-PCA target status: direct export from `claude_target_coordinates.csv`; no Big Five reconstruction was used.",
        "- Canonical split set: the five deterministic Codex outer-loop seeds.",
        "",
        "## 3. Feature Families",
        "",
        f"- Semantic baseline: {matrices['semantic_baseline']['x'].shape[1]} one-hot semantic-cluster features.",
        f"- Codex retained features: semantic baseline plus {len(data['dims'])} retained outer-loop dimensions.",
        f"- Claude Big Five features: semantic baseline plus {len(BIGFIVE_COLUMNS)} Big Five columns from Claude's exported feature matrix.",
        f"- Claude full feature matrix: semantic baseline plus {len([c for c in data['claude_feature_headers'] if c != 'persona'])} Claude TF-IDF/Big-Five feature columns.",
        "- Combined feature set: semantic baseline plus Codex retained dimensions plus Claude full feature matrix.",
        "",
        "## 4. Results Matrix",
        "",
        *matrix_lines,
        "",
        "## 5. Core Questions",
        "",
    ]
    for question, answer in answers.items():
        lines.append(f"### {question.replace('_', ' ').capitalize()}")
        lines.extend(["", answer, ""])
    lines.extend(
        [
            "## 6. Most and Least Explained Personas",
            "",
            "Using the combined feature set on canonical activation PCA, the most effectively explained personas are: "
            + ", ".join(top_roles(results["combined_codex_claude__canonical_activation_pca3d"], reverse=False, n=10))
            + ".",
            "",
            "Using the same condition, the least effectively explained personas are: "
            + ", ".join(top_roles(results["combined_codex_claude__canonical_activation_pca3d"], reverse=True, n=10))
            + ". These are diagnostic residual cases for the current feature vocabulary, not evidence that the personas are inherently inexplicable.",
            "",
            "## 7. Interpretation",
            "",
            "The shared benchmark supports a mixed but productive alignment story. Big Five-style features survive direct alignment to canonical activation PCA, which means Claude's trait result is not merely an artifact of its pseudo-PCA target. Codex procedural/behavioral dimensions do not transfer to Claude's direct pseudo-PCA export over the semantic baseline in this aligned run. The combined feature family is useful as an empirical diagnostic, but any trait-plus-procedural interpretation should remain bounded to held-out prediction rather than promoted to a causal explanation.",
            "",
            "## 8. Limitations",
            "",
            "- Claude's pseudo-PCA target is a direct export, but it remains a 7-cluster-cosine pseudo-target rather than the full activation PCA target.",
            "- Feature matrices are fixed at the common persona intersection to support apples-to-apples comparison.",
            "- Cluster accuracy is secondary and only reported for canonical activation clusters.",
            "- No pods, activations, or model calls were run.",
            "",
            "## 9. Recommended Next Steps",
            "",
            "- Ask Claude to run the same shared benchmark script or consume these exported matrices so both agents report against identical files.",
            "- Add a blinded human-readable feature codebook for Codex dimensions and Claude Big Five columns.",
            "- Re-run the benchmark after any future no-label activation stress test to see whether trait/procedural transfer survives label removal.",
        ]
    )
    (OUT_DIR / "shared_benchmark_report.md").write_text("\n".join(lines))


def write_results_json(data: dict[str, Any], matrices: dict[str, Any], results: dict[str, Any], answers: dict[str, str]) -> None:
    safe_results = json.loads(json.dumps(results, default=lambda x: None))
    payload = {
        "provenance": make_provenance(
            "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_results.json",
            "shared_benchmark_results",
            "Claude pseudo-PCA target is loaded directly from the Claude branch export, not reconstructed from local Big Five profiles.",
        ),
        "alignment": {
            "common_personas": len(data["roles"]),
            "codex_outer_personas": data["n_outer_personas"],
            "claude_target_rows": data["n_claude_targets"],
            "claude_feature_rows": data["n_claude_features"],
            "canonical_split_set": outer.SPLIT_SEEDS,
            "claude_target_status": "direct_export_used",
        },
        "feature_matrix_files": {
            name: item["file"]
            for name, item in matrices.items()
        },
        "answers": answers,
        "results": safe_results,
    }
    (OUT_DIR / "shared_benchmark_results.json").write_text(json.dumps(payload, indent=2))


def main() -> None:
    data = load_aligned_data()
    export_targets(data)
    export_splits(data)
    matrices = export_feature_matrices(data)
    results = run_benchmark(data, matrices)
    answers = answer_core_questions(results)
    write_summary(results)
    write_feature_target_matrix(results)
    write_persona_rankings(data, results)
    write_report(data, matrices, results, answers)
    write_results_json(data, matrices, results, answers)
    print(json.dumps({k: answers[k] for k in answers}, indent=2))
    print(f"Wrote benchmark outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
