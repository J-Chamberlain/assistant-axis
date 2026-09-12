#!/usr/bin/env python3
"""Run AA-7 from frozen, existing model-vector artifacts only.

The analysis is CPU-only. It performs no model inference, activation extraction,
response generation, external API call, human-respondent projection, or
human-occupation projection.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import io
import json
import math
import os
import subprocess
import sys
import warnings
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
import torch
from joblib import Parallel, delayed
from scipy.linalg import orthogonal_procrustes
from scipy.spatial.distance import pdist
from scipy.stats import kruskal, mannwhitneyu, pearsonr, rankdata, spearmanr
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore", category=RuntimeWarning)
np.seterr(all="ignore")
plt.rcParams["svg.hashsalt"] = "aa7-human-supported-trait-convergence"


REPO = Path(__file__).resolve().parents[3]
DEFAULT_OUT = Path(__file__).resolve().parent
CANONICAL_STARTING_SHA = "c5c2628ad54483253ad97b95c3e1febad29f9435"
FREEZE_COMMIT = "51c54a5862419d0e296da1fa9ac323e4ecfa3d95"
PREREGISTRATION_COMMIT = "cabd80732647bf7666c6d6cb469f485e222f87b7"
GENERATION_TIMESTAMP = "2026-09-12T01:14:04Z"
ALPHAS = np.asarray([1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0])
DOMAINS = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
MODEL_ORDER = ["qwen", "llama", "gemma"]
MODEL_SPECS = {
    "qwen": {"label": "Qwen/Qwen3-32B", "folder": "qwen-3-32b", "dimension": 5120},
    "llama": {"label": "Llama-3.3-70B", "folder": "llama-3.3-70b", "dimension": 8192},
    "gemma": {"label": "Gemma-2-27B", "folder": "gemma-2-27b", "dimension": 4608},
}
MATRIX_PATHS = {
    "qwen": REPO / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
    "llama": REPO / "research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv",
    "gemma": REPO / "research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv",
}
AA1_SUPPORT = REPO / "research/outputs/sapa_bridge_psychometric_audit/sapa_trait_bridge_psychometric_support_v1.csv"
AA2_SCORES = REPO / "research/outputs/externally_anchored_big_five/big_five_role_scores.csv"
AA2_DIRECTIONS = REPO / "research/outputs/externally_anchored_big_five/big_five_domain_directions_manifest.json"
AA3_VIEWER = REPO / "research/outputs/extended_persona_pca/viewer_data.json"
CLUSTERS = REPO / "research/geometry_tables/cluster_membership_table.csv"
FREEZE_PATH = DEFAULT_OUT / "human_supported_trait_set_freeze.json"
PREREG_PATH = DEFAULT_OUT / "analysis_preregistration.json"
PC_NAMES = [f"PC{i}" for i in range(1, 7)]
SUPPORT_CODES = {
    "INSUFFICIENT": 0,
    "REDUNDANT / BROAD": 1,
    "MODERATE SUPPORT": 2,
    "HIGH HUMAN-MEASUREMENT SUPPORT": 3,
}


@dataclass
class ModelData:
    key: str
    label: str
    personas: list[str]
    traits: list[str]
    trait_scores: np.ndarray
    pc_scores: np.ndarray
    big_five: np.ndarray
    clusters: np.ndarray
    role_raw: np.ndarray
    role_unit: np.ndarray
    pca_components: np.ndarray
    human_trait_loading_cosines: dict[str, np.ndarray]
    vector_audit: dict[str, Any]


@dataclass
class EvalResult:
    summary: dict[str, Any]
    per_pc: list[dict[str, Any]]
    truth: np.ndarray
    prediction: np.ndarray
    train_stds: np.ndarray
    fold_ids: np.ndarray
    selected_alphas: list[float]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.12g", lineterminator="\n")


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def safe_corr(x: np.ndarray, y: np.ndarray, method: str = "pearson") -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3 or np.std(x) <= 1e-14 or np.std(y) <= 1e-14:
        return 0.0
    value = pearsonr(x, y).statistic if method == "pearson" else spearmanr(x, y).statistic
    return float(value) if math.isfinite(float(value)) else 0.0


def unit(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype=np.float64)
    norm = float(np.linalg.norm(vector))
    return vector / norm if norm > 1e-15 else np.zeros_like(vector)


def import_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_mean_tensor(path: Path) -> np.ndarray:
    tensor = torch.load(io.BytesIO(path.read_bytes()), map_location="cpu", weights_only=True).float()
    if tensor.ndim > 1:
        tensor = tensor.mean(0)
    array = tensor.numpy().astype(np.float64)
    if not np.isfinite(array).all() or np.linalg.norm(array) <= 0:
        raise ValueError(f"Invalid saved vector: {path}")
    return array


def load_sources() -> tuple[dict[str, ModelData], pd.DataFrame, list[str], list[str], Path, dict[str, Any]]:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    frozen_traits = [row["trait"] for row in freeze["traits"]]
    expected = [
        "adventurous", "altruistic", "forgiving", "grandiose", "impulsive", "manipulative",
        "optimistic", "pessimistic", "traditional", "innovative", "introspective", "judgmental",
    ]
    if frozen_traits != expected:
        raise ValueError(f"Frozen trait order changed: {frozen_traits}")
    support = pd.read_csv(AA1_SUPPORT)
    direct = support[support["bridge_tier"].eq("primary_direct")].copy()
    if len(direct) != 45:
        raise ValueError(f"Expected 45 AA-1 direct traits, found {len(direct)}")
    aa1_frozen = direct[
        direct["human_measurement_support_tier"].isin(
            ["HIGH HUMAN-MEASUREMENT SUPPORT", "MODERATE SUPPORT"]
        )
    ]
    if set(aa1_frozen["trait"]) != set(frozen_traits) or len(aa1_frozen) != 12:
        raise ValueError("AA-1 support artifact does not reproduce the frozen 12")
    counts = aa1_frozen["human_measurement_support_tier"].value_counts().to_dict()
    if counts != {"HIGH HUMAN-MEASUREMENT SUPPORT": 9, "MODERATE SUPPORT": 3}:
        raise ValueError(f"AA-1 support-level mismatch: {counts}")

    matrix_frames = {key: pd.read_csv(path) for key, path in MATRIX_PATHS.items()}
    personas = matrix_frames["qwen"]["persona"].astype(str).tolist()
    traits = matrix_frames["qwen"].columns[1:].astype(str).tolist()
    if len(personas) != 275 or len(traits) != 240:
        raise ValueError("Canonical Qwen matrix is not 275 x 240")
    for key, frame in matrix_frames.items():
        if frame.shape != (275, 241):
            raise ValueError(f"{key} matrix shape {frame.shape}")
        if frame["persona"].astype(str).tolist() != personas or frame.columns[1:].astype(str).tolist() != traits:
            raise ValueError(f"{key} shared role/trait labels differ")
        if not np.isfinite(frame.iloc[:, 1:].to_numpy(dtype=float)).all():
            raise ValueError(f"{key} trait matrix is nonfinite")
    if not set(frozen_traits).issubset(traits) or not set(direct["trait"]).issubset(traits):
        raise ValueError("Frozen/direct traits are absent from the canonical matrices")

    viewer = json.loads(AA3_VIEWER.read_text(encoding="utf-8"))
    cluster_table = pd.read_csv(CLUSTERS).set_index("role")
    clusters = np.asarray([cluster_table.loc[name, "cluster"] for name in personas], dtype=object)
    bf = pd.read_csv(AA2_SCORES)
    bf = bf[bf["construction"].eq("human_anchored_strict")].copy()
    if len(bf) != 3 * 5 * 275:
        raise ValueError(f"Unexpected strict Big Five row count: {len(bf)}")

    aa3 = import_module(
        REPO / "research/outputs/extended_persona_pca/run_extended_persona_pca.py", "aa7_aa3_runner"
    )
    vector_root = aa3.resolve_vector_root(None)
    pca_results, _ = aa3.build_pca_results(vector_root)
    models: dict[str, ModelData] = {}
    source_checks: dict[str, Any] = {}
    for key in MODEL_ORDER:
        label = MODEL_SPECS[key]["label"]
        points = {row["persona"]: row for row in viewer["models"][key]["points"]}
        y = np.asarray([points[name]["coordinates"][:6] for name in personas], dtype=np.float64)
        result = pca_results[key]
        if result.names != personas:
            raise ValueError(f"{key} AA-3 role order mismatch")
        score_error = float(np.max(np.abs(result.scores[:, :6] - y)))
        if score_error > 1e-9:
            raise ValueError(f"{key} AA-3 PC1-PC6 mismatch: {score_error}")
        model_bf = bf[bf["model"].eq(key)].pivot(index="persona", columns="domain", values="raw_projection_score")
        model_bf = model_bf.reindex(index=personas, columns=DOMAINS)
        if model_bf.isna().any().any():
            raise ValueError(f"{key} strict Big Five scores incomplete")
        role_raw = result.vectors.astype(np.float64, copy=False)
        role_unit = role_raw / np.linalg.norm(role_raw, axis=1, keepdims=True)
        trait_cosines: dict[str, np.ndarray] = {}
        reproduction: dict[str, float] = {}
        trait_dir = vector_root / MODEL_SPECS[key]["folder"] / "trait_vectors"
        if len(list(trait_dir.glob("*.pt"))) != 240:
            raise ValueError(f"{key} saved trait-vector count is not 240")
        x = matrix_frames[key].iloc[:, 1:].to_numpy(dtype=np.float64)
        for trait in frozen_traits:
            raw = load_mean_tensor(trait_dir / f"{trait}.pt")
            direction = unit(raw)
            trait_cosines[trait] = result.components[:6] @ direction
            col = traits.index(trait)
            reproduction[trait] = float(np.max(np.abs(role_unit @ direction - x[:, col])))
        max_reproduction = max(reproduction.values())
        if max_reproduction > 1e-10:
            raise ValueError(f"{key} raw-cosine reproduction failed: {max_reproduction}")
        models[key] = ModelData(
            key=key,
            label=label,
            personas=personas,
            traits=traits,
            trait_scores=x,
            pc_scores=y,
            big_five=model_bf.to_numpy(dtype=np.float64),
            clusters=clusters,
            role_raw=role_raw,
            role_unit=role_unit,
            pca_components=result.components[:6].copy(),
            human_trait_loading_cosines=trait_cosines,
            vector_audit=result.source_audit,
        )
        source_checks[key] = {
            "aa3_pc1_pc6_max_abs_error": score_error,
            "frozen_trait_cosine_matrix_max_abs_error": max_reproduction,
            "role_vector_audit": result.source_audit,
            "role_count": len(personas),
            "trait_count": len(traits),
            "hidden_dimension": MODEL_SPECS[key]["dimension"],
        }
    return models, support, frozen_traits, direct["trait"].astype(str).tolist(), vector_root, source_checks


def safe_scale(values: np.ndarray) -> np.ndarray:
    scale = np.asarray(values, dtype=np.float64).std(axis=0, ddof=0)
    return np.where(scale > 1e-12, scale, 1.0)


def ridge_state(
    x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, alpha: float
) -> tuple[np.ndarray, dict[str, np.ndarray | float]]:
    x_mean = x_train.mean(axis=0)
    x_scale = safe_scale(x_train)
    y_mean = y_train.mean(axis=0)
    y_scale = safe_scale(y_train)
    xtr = (x_train - x_mean) / x_scale
    xte = (x_test - x_mean) / x_scale
    ytr = (y_train - y_mean) / y_scale
    u, singular, vt = np.linalg.svd(xtr, full_matrices=False)
    factor = singular / (singular * singular + float(alpha))
    beta = (vt.T * factor) @ (u.T @ ytr)
    prediction = (xte @ beta) * y_scale + y_mean
    return prediction, {
        "x_mean": x_mean,
        "x_scale": x_scale,
        "y_mean": y_mean,
        "y_scale": y_scale,
        "beta_standardized": beta,
        "alpha": float(alpha),
    }


def predict_from_state(x: np.ndarray, state: dict[str, np.ndarray | float]) -> np.ndarray:
    xz = (x - np.asarray(state["x_mean"])) / np.asarray(state["x_scale"])
    return (xz @ np.asarray(state["beta_standardized"])) * np.asarray(state["y_scale"]) + np.asarray(state["y_mean"])


def inner_alpha_scores(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    sse = np.zeros(len(ALPHAS), dtype=np.float64)
    for train_idx, val_idx in KFold(4, shuffle=True, random_state=seed).split(x):
        for alpha_index, alpha in enumerate(ALPHAS):
            prediction, _ = ridge_state(x[train_idx], y[train_idx], x[val_idx], float(alpha))
            scale = safe_scale(y[train_idx])
            residual = (prediction - y[val_idx]) / scale
            sse[alpha_index] += float(np.sum(residual * residual))
    return sse


def tune_alpha(x: np.ndarray, y: np.ndarray, seed: int) -> float:
    return float(ALPHAS[int(np.argmin(inner_alpha_scores(x, y, seed)))])


def metric_result(
    truth: np.ndarray, prediction: np.ndarray, train_stds: np.ndarray, scope: str
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    d = truth.shape[1]
    per_pc: list[dict[str, Any]] = []
    standardized_residual = (prediction - truth) / train_stds
    for pc in range(d):
        residual = prediction[:, pc] - truth[:, pc]
        ss_res = float(np.sum(residual * residual))
        centered = truth[:, pc] - truth[:, pc].mean()
        ss_tot = float(np.sum(centered * centered))
        per_pc.append(
            {
                "pc": PC_NAMES[pc],
                "r2": 1.0 - ss_res / ss_tot,
                "rmse": float(np.sqrt(np.mean(residual * residual))),
                "normalized_rmse": float(np.sqrt(np.mean(standardized_residual[:, pc] ** 2))),
                "mae": float(np.mean(np.abs(residual))),
                "pearson": safe_corr(truth[:, pc], prediction[:, pc]),
                "spearman": safe_corr(truth[:, pc], prediction[:, pc], "spearman"),
            }
        )
    summary: dict[str, Any] = {
        "n_oof_predictions": int(len(truth)),
        "mean_pc_r2": float(np.mean([row["r2"] for row in per_pc])),
        "aggregate_normalized_geometric_error": float(
            np.sqrt(np.mean(np.sum(standardized_residual * standardized_residual, axis=1)))
        ),
        "mean_normalized_rmse_per_pc": float(np.mean([row["normalized_rmse"] for row in per_pc])),
    }
    summary["core_pc1_pc3_aggregate_nrmse"] = float(
        np.sqrt(np.mean(np.sum(standardized_residual[:, :3] ** 2, axis=1)))
    )
    if d == 6:
        summary["secondary_pc4_pc6_aggregate_nrmse"] = float(
            np.sqrt(np.mean(np.sum(standardized_residual[:, 3:6] ** 2, axis=1)))
        )
        summary["full_pc1_pc6_aggregate_nrmse"] = summary["aggregate_normalized_geometric_error"]
    else:
        summary["secondary_pc4_pc6_aggregate_nrmse"] = math.nan
        summary["full_pc1_pc6_aggregate_nrmse"] = math.nan
    summary["scope"] = scope
    return summary, per_pc


def kfold_splits(n: int, seed: int = 42) -> list[dict[str, Any]]:
    rows = []
    for fold, (train_idx, test_idx) in enumerate(KFold(5, shuffle=True, random_state=seed).split(np.arange(n))):
        rows.append(
            {
                "id": f"kfold_{seed}_{fold}",
                "train_idx": train_idx,
                "test_idx": test_idx,
                "inner_seed": seed * 100 + fold,
                "outer_training_role_only": True,
            }
        )
    return rows


def lopo_splits(n: int) -> list[dict[str, Any]]:
    all_idx = np.arange(n)
    return [
        {
            "id": f"lopo_{held_out}",
            "train_idx": all_idx[all_idx != held_out],
            "test_idx": np.asarray([held_out]),
            "inner_seed": 10_000 + held_out,
            "outer_training_role_only": True,
        }
        for held_out in range(n)
    ]


def family_splits(clusters: np.ndarray) -> list[dict[str, Any]]:
    rows = []
    for index, family in enumerate(sorted(set(clusters.tolist()))):
        test_idx = np.flatnonzero(clusters == family)
        train_idx = np.flatnonzero(clusters != family)
        rows.append(
            {
                "id": f"family_{family}",
                "family": family,
                "train_idx": train_idx,
                "test_idx": test_idx,
                "inner_seed": 20_000 + index,
                "outer_training_role_only": True,
            }
        )
    return rows


def evaluate_scopes(
    feature_source: np.ndarray | Callable[[int, dict[str, Any]], np.ndarray],
    y6: np.ndarray,
    splits: Sequence[dict[str, Any]],
) -> dict[str, EvalResult]:
    collected: dict[str, dict[str, Any]] = {
        "core": {"truth": [], "prediction": [], "std": [], "fold": [], "alpha": []},
        "extended": {"truth": [], "prediction": [], "std": [], "fold": [], "alpha": []},
    }
    for split_index, split in enumerate(splits):
        x = feature_source(split_index, split) if callable(feature_source) else feature_source
        train_idx = np.asarray(split["train_idx"])
        test_idx = np.asarray(split["test_idx"])
        for scope, d in [("core", 3), ("extended", 6)]:
            y = y6[:, :d]
            alpha = tune_alpha(x[train_idx], y[train_idx], int(split["inner_seed"]))
            prediction, _ = ridge_state(x[train_idx], y[train_idx], x[test_idx], alpha)
            collected[scope]["truth"].append(y[test_idx])
            collected[scope]["prediction"].append(prediction)
            collected[scope]["std"].append(np.broadcast_to(safe_scale(y[train_idx]), prediction.shape))
            collected[scope]["fold"].append(np.repeat(split["id"], len(test_idx)))
            collected[scope]["alpha"].append(alpha)
    results: dict[str, EvalResult] = {}
    for scope, data in collected.items():
        truth = np.concatenate(data["truth"], axis=0)
        prediction = np.concatenate(data["prediction"], axis=0)
        standards = np.concatenate(data["std"], axis=0)
        summary, per_pc = metric_result(truth, prediction, standards, scope)
        summary["selected_alpha_counts"] = json.dumps(
            dict(sorted(Counter(str(value) for value in data["alpha"]).items())), sort_keys=True
        )
        results[scope] = EvalResult(
            summary=summary,
            per_pc=per_pc,
            truth=truth,
            prediction=prediction,
            train_stds=standards,
            fold_ids=np.concatenate(data["fold"]),
            selected_alphas=list(data["alpha"]),
        )
    return results


def add_evaluation_records(
    summaries: list[dict[str, Any]],
    per_pc_rows: list[dict[str, Any]],
    model: ModelData,
    family: str,
    feature_count: int,
    protocol: str,
    results: dict[str, EvalResult],
) -> None:
    for scope, result in results.items():
        summaries.append(
            {
                "model": model.label,
                "model_key": model.key,
                "feature_family": family,
                "feature_count": feature_count,
                "protocol": protocol,
                **result.summary,
            }
        )
        for row in result.per_pc:
            per_pc_rows.append(
                {
                    "model": model.label,
                    "model_key": model.key,
                    "feature_family": family,
                    "feature_count": feature_count,
                    "protocol": protocol,
                    "scope": scope,
                    **row,
                }
            )


def summary_wide(result: EvalResult) -> dict[str, Any]:
    row = dict(result.summary)
    for pc_row in result.per_pc:
        pc = pc_row["pc"].lower()
        for metric in ["r2", "rmse", "normalized_rmse", "mae"]:
            row[f"{pc}_{metric}"] = pc_row[metric]
    return row


def optimized_nested(
    model: ModelData,
    aa4: Any,
    splits: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[tuple[str, int], EvalResult]]:
    paths: list[dict[str, Any]] = []
    aggregate: dict[tuple[str, int], dict[str, list[Any]]] = {}
    for scope, d in [("core", 3), ("extended", 6)]:
        for budget in [5, 12]:
            aggregate[(scope, budget)] = {"truth": [], "prediction": [], "std": [], "fold": [], "alpha": []}
        for split in splits:
            train_idx = np.asarray(split["train_idx"])
            test_idx = np.asarray(split["test_idx"])
            y = model.pc_scores[:, :d]
            path = aa4.greedy_path(
                model.trait_scores[train_idx], y[train_idx], model.traits, int(split["inner_seed"]), 12
            )
            selected: list[int] = []
            for step in path:
                selected.append(int(step["trait_index"]))
                paths.append(
                    {
                        "model": model.label,
                        "model_key": model.key,
                        "scope": scope,
                        "outer_fold": split["id"],
                        **step,
                    }
                )
                budget = int(step["entry_rank"])
                if budget not in [5, 12]:
                    continue
                prediction, _ = ridge_state(
                    model.trait_scores[train_idx][:, selected],
                    y[train_idx],
                    model.trait_scores[test_idx][:, selected],
                    float(step["selected_alpha"]),
                )
                target = aggregate[(scope, budget)]
                target["truth"].append(y[test_idx])
                target["prediction"].append(prediction)
                target["std"].append(np.broadcast_to(safe_scale(y[train_idx]), prediction.shape))
                target["fold"].append(np.repeat(split["id"], len(test_idx)))
                target["alpha"].append(float(step["selected_alpha"]))
    results: dict[tuple[str, int], EvalResult] = {}
    for key, data in aggregate.items():
        scope, _ = key
        truth = np.concatenate(data["truth"])
        prediction = np.concatenate(data["prediction"])
        standards = np.concatenate(data["std"])
        summary, per_pc = metric_result(truth, prediction, standards, scope)
        summary["selected_alpha_counts"] = json.dumps(
            dict(sorted(Counter(str(value) for value in data["alpha"]).items())), sort_keys=True
        )
        results[key] = EvalResult(
            summary, per_pc, truth, prediction, standards, np.concatenate(data["fold"]), list(data["alpha"])
        )
    return paths, results


def make_random_subsets(trait_count: int, budgets: Sequence[int], draws: int) -> dict[int, list[tuple[int, ...]]]:
    rng = np.random.default_rng(2026091201)
    output: dict[int, list[tuple[int, ...]]] = {}
    for budget in budgets:
        seen: set[tuple[int, ...]] = set()
        while len(seen) < draws:
            seen.add(tuple(sorted(rng.choice(trait_count, size=budget, replace=False).tolist())))
        output[budget] = sorted(seen)
    return output


def isotropic_sampler(role_unit: np.ndarray, ambient_dimension: int) -> Callable[[int, int], np.ndarray]:
    gram = role_unit @ role_unit.T
    eigenvalues, eigenvectors = np.linalg.eigh((gram + gram.T) / 2.0)
    keep = eigenvalues > max(float(eigenvalues.max()) * 1e-12, 1e-12)
    values = eigenvalues[keep]
    vectors = eigenvectors[:, keep]
    rank = len(values)
    residual_df = ambient_dimension - rank
    if residual_df <= 0:
        raise ValueError("Ambient dimension must exceed role-span rank")

    def sample(seed: int, budget: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        in_span = rng.standard_normal((rank, budget))
        residual_norm_sq = rng.chisquare(residual_df, size=budget)
        direction_norm = np.sqrt(np.sum(in_span * in_span, axis=0) + residual_norm_sq)
        return (vectors @ (np.sqrt(values)[:, None] * in_span)) / direction_norm[None, :]

    sample.rank = rank  # type: ignore[attr-defined]
    sample.residual_df = residual_df  # type: ignore[attr-defined]
    return sample


def persona_span_caches(model: ModelData, splits: Sequence[dict[str, Any]]) -> list[dict[str, np.ndarray]]:
    unit_raw_gram = model.role_unit @ model.role_raw.T
    raw_gram = model.role_raw @ model.role_raw.T
    caches = []
    for split in splits:
        train_idx = np.asarray(split["train_idx"])
        cross = unit_raw_gram[:, train_idx]
        projection = cross - cross.mean(axis=1, keepdims=True)
        train_gram = raw_gram[np.ix_(train_idx, train_idx)]
        centered_gram = (
            train_gram
            - train_gram.mean(axis=1, keepdims=True)
            - train_gram.mean(axis=0, keepdims=True)
            + train_gram.mean()
        )
        caches.append({"projection": projection, "centered_gram": centered_gram})
    return caches


def evaluate_controls(
    models: dict[str, ModelData],
    splits: Sequence[dict[str, Any]],
    draws: int,
    n_jobs: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    random_subsets = make_random_subsets(240, [5, 12], draws)
    all_random: list[dict[str, Any]] = []
    all_isotropic: list[dict[str, Any]] = []
    all_span: list[dict[str, Any]] = []
    sampler_audit: dict[str, Any] = {}
    for model_index, key in enumerate(MODEL_ORDER):
        model = models[key]
        print(f"controls: {model.label} random real", flush=True)

        def one_random(budget: int, bank: int, selected: tuple[int, ...]) -> list[dict[str, Any]]:
            results = evaluate_scopes(model.trait_scores[:, selected], model.pc_scores, splits)
            return [
                {
                    "model": model.label,
                    "model_key": key,
                    "feature_budget": budget,
                    "bank": bank,
                    "subset_seed": 2026091201,
                    "traits": json.dumps([model.traits[index] for index in selected]),
                    "scope": scope,
                    **summary_wide(result),
                }
                for scope, result in results.items()
            ]

        tasks = [
            (budget, bank, selected)
            for budget, subsets in random_subsets.items()
            for bank, selected in enumerate(subsets)
        ]
        nested = Parallel(n_jobs=n_jobs, prefer="threads")(
            delayed(one_random)(budget, bank, selected) for budget, bank, selected in tasks
        )
        all_random.extend(row for group in nested for row in group)

        print(f"controls: {model.label} isotropic", flush=True)
        sampler = isotropic_sampler(model.role_unit, MODEL_SPECS[key]["dimension"])
        sampler_audit[key] = {
            "ambient_dimension": MODEL_SPECS[key]["dimension"],
            "role_span_rank": int(sampler.rank),  # type: ignore[attr-defined]
            "orthogonal_residual_degrees_of_freedom": int(sampler.residual_df),  # type: ignore[attr-defined]
            "method": "Exact distributional Gram/eigendecomposition sampler for normalized ambient Gaussian directions",
            "used_pc_targets": False,
        }

        def one_isotropic(budget: int, bank: int) -> list[dict[str, Any]]:
            seed = 30_000_000 + model_index * 1_000_000 + bank * 100 + budget
            features = sampler(seed, budget)
            results = evaluate_scopes(features, model.pc_scores, splits)
            return [
                {
                    "model": model.label,
                    "model_key": key,
                    "feature_budget": budget,
                    "bank": bank,
                    "bank_seed": seed,
                    "direction_generation_used_pc_targets": False,
                    "scope": scope,
                    **summary_wide(result),
                }
                for scope, result in results.items()
            ]

        tasks2 = [(budget, bank) for budget in [5, 12] for bank in range(draws)]
        nested = Parallel(n_jobs=n_jobs, prefer="threads")(
            delayed(one_isotropic)(budget, bank) for budget, bank in tasks2
        )
        all_isotropic.extend(row for group in nested for row in group)

        print(f"controls: {model.label} fold-local persona span", flush=True)
        caches = persona_span_caches(model, splits)

        def one_span(budget: int, bank: int) -> list[dict[str, Any]]:
            fold_features: list[np.ndarray] = []
            seeds: list[int] = []
            for fold_index, split in enumerate(splits):
                seed = 50_000_000 + model_index * 1_000_000 + bank * 100 + fold_index + budget
                seeds.append(seed)
                rng = np.random.default_rng(seed)
                weights = rng.standard_normal((len(split["train_idx"]), budget))
                cache = caches[fold_index]
                norm_sq = np.sum(weights * (cache["centered_gram"] @ weights), axis=0)
                if np.any(norm_sq <= 1e-20):
                    raise ValueError("Degenerate persona-span random direction")
                fold_features.append((cache["projection"] @ weights) / np.sqrt(norm_sq)[None, :])

            def getter(index: int, _: dict[str, Any]) -> np.ndarray:
                return fold_features[index]

            results = evaluate_scopes(getter, model.pc_scores, splits)
            return [
                {
                    "model": model.label,
                    "model_key": key,
                    "feature_budget": budget,
                    "bank": bank,
                    "fold_seed_min": min(seeds),
                    "fold_seed_max": max(seeds),
                    "outer_training_role_only": True,
                    "direction_generation_used_pc_targets": False,
                    "scope": scope,
                    **summary_wide(result),
                }
                for scope, result in results.items()
            ]

        nested = Parallel(n_jobs=n_jobs, prefer="threads")(
            delayed(one_span)(budget, bank) for budget, bank in tasks2
        )
        all_span.extend(row for group in nested for row in group)
    return (
        pd.DataFrame(all_random),
        pd.DataFrame(all_span),
        pd.DataFrame(all_isotropic),
        sampler_audit,
    )


def trait_scores_table(models: dict[str, ModelData], frozen_traits: list[str]) -> pd.DataFrame:
    rows = []
    for model in models.values():
        for trait in frozen_traits:
            values = model.trait_scores[:, model.traits.index(trait)]
            z = (values - values.mean()) / safe_scale(values[None, :].T)[0]
            percentile = 100.0 * (rankdata(values, method="average") - 1.0) / (len(values) - 1.0)
            for persona, raw, zscore, pct in zip(model.personas, values, z, percentile, strict=True):
                rows.append(
                    {
                        "model": model.label,
                        "model_key": model.key,
                        "role": persona,
                        "trait": trait,
                        "raw_cosine": raw,
                        "within_model_z_score": zscore,
                        "within_model_percentile": pct,
                    }
                )
    return pd.DataFrame(rows)


def association_tables(
    models: dict[str, ModelData], support: pd.DataFrame, frozen_traits: list[str], direct_traits: list[str]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    association_rows = []
    redundancy_rows = []
    utility_rows = []
    support_lookup = support.set_index("trait")["human_measurement_support_tier"].to_dict()
    for model in models.values():
        frozen_indices = [model.traits.index(name) for name in frozen_traits]
        frozen_x = model.trait_scores[:, frozen_indices]
        for i, left in enumerate(frozen_traits):
            for j in range(i, len(frozen_traits)):
                right = frozen_traits[j]
                redundancy_rows.append(
                    {
                        "model": model.label,
                        "model_key": model.key,
                        "trait_1": left,
                        "trait_2": right,
                        "pearson": safe_corr(frozen_x[:, i], frozen_x[:, j]),
                        "spearman": safe_corr(frozen_x[:, i], frozen_x[:, j], "spearman"),
                    }
                )
        for family_name, trait_names in [("human_supported_12", frozen_traits), ("direct_semantic_45", direct_traits)]:
            for trait in trait_names:
                values = model.trait_scores[:, model.traits.index(trait)]
                correlations = []
                for pc in range(6):
                    pearson = safe_corr(values, model.pc_scores[:, pc])
                    spearman = safe_corr(values, model.pc_scores[:, pc], "spearman")
                    correlations.append(pearson)
                    if family_name == "human_supported_12":
                        association_rows.append(
                            {
                                "model": model.label,
                                "model_key": model.key,
                                "trait": trait,
                                "aa1_human_support_level": support_lookup[trait],
                                "pc": PC_NAMES[pc],
                                "pearson": pearson,
                                "spearman": spearman,
                                "single_feature_r2": pearson * pearson,
                                "direction_cosine_with_pc_loading": model.human_trait_loading_cosines[trait][pc],
                            }
                        )
                for scope, d in [("core", 3), ("extended", 6)]:
                    subset = np.asarray(correlations[:d])
                    utility_rows.append(
                        {
                            "record_type": "trait",
                            "model": model.label,
                            "model_key": model.key,
                            "scope": scope,
                            "trait_family": family_name,
                            "trait": trait,
                            "human_support_tier": support_lookup[trait],
                            "support_code": SUPPORT_CODES[support_lookup[trait]],
                            "mean_squared_pc_correlation": float(np.mean(subset * subset)),
                            "max_absolute_pc_correlation": float(np.max(np.abs(subset))),
                        }
                    )
    utility = pd.DataFrame(utility_rows)
    summary_rows = []
    for (model, key, scope, family), group in utility.groupby(["model", "model_key", "scope", "trait_family"]):
        rho = safe_corr(group["support_code"].to_numpy(), group["mean_squared_pc_correlation"].to_numpy(), "spearman")
        summary_rows.append(
            {
                "record_type": "ordinal_association",
                "model": model,
                "model_key": key,
                "scope": scope,
                "trait_family": family,
                "trait": "",
                "human_support_tier": "all",
                "support_code": math.nan,
                "mean_squared_pc_correlation": math.nan,
                "max_absolute_pc_correlation": math.nan,
                "support_utility_spearman": rho,
                "n_traits": len(group),
            }
        )
        groups = [g["mean_squared_pc_correlation"].to_numpy() for _, g in group.groupby("human_support_tier")]
        if len(groups) >= 2 and all(len(x) for x in groups):
            stat = kruskal(*groups)
            summary_rows[-1]["kruskal_h"] = float(stat.statistic)
            summary_rows[-1]["kruskal_p"] = float(stat.pvalue)
        if family == "human_supported_12":
            high = group[group["human_support_tier"].eq("HIGH HUMAN-MEASUREMENT SUPPORT")]["mean_squared_pc_correlation"]
            moderate = group[group["human_support_tier"].eq("MODERATE SUPPORT")]["mean_squared_pc_correlation"]
            stat = mannwhitneyu(high, moderate, alternative="two-sided")
            summary_rows[-1]["high_mean_utility"] = float(high.mean())
            summary_rows[-1]["moderate_mean_utility"] = float(moderate.mean())
            summary_rows[-1]["high_vs_moderate_mannwhitney_p"] = float(stat.pvalue)
    utility = pd.concat([utility, pd.DataFrame(summary_rows)], ignore_index=True, sort=False)
    return pd.DataFrame(association_rows), pd.DataFrame(redundancy_rows), utility


def contribution_table(
    models: dict[str, ModelData], frozen_traits: list[str], splits: Sequence[dict[str, Any]]
) -> pd.DataFrame:
    rows = []
    for model in models.values():
        indices = [model.traits.index(name) for name in frozen_traits]
        x = model.trait_scores[:, indices]
        for scope, d in [("core", 3), ("extended", 6)]:
            y = model.pc_scores[:, :d]
            baseline = evaluate_scopes(x, model.pc_scores, splits)[scope]
            leaveout: dict[str, tuple[float, float]] = {}
            for trait_index, trait in enumerate(frozen_traits):
                keep = [i for i in range(12) if i != trait_index]
                result = evaluate_scopes(x[:, keep], model.pc_scores, splits)[scope]
                leaveout[trait] = (
                    result.summary["aggregate_normalized_geometric_error"]
                    - baseline.summary["aggregate_normalized_geometric_error"],
                    baseline.summary["mean_pc_r2"] - result.summary["mean_pc_r2"],
                )
            perm_predictions: dict[str, list[np.ndarray]] = {trait: [] for trait in frozen_traits}
            truth_parts: list[np.ndarray] = []
            std_parts: list[np.ndarray] = []
            for fold_index, split in enumerate(splits):
                train_idx = np.asarray(split["train_idx"])
                test_idx = np.asarray(split["test_idx"])
                alpha = tune_alpha(x[train_idx], y[train_idx], int(split["inner_seed"]))
                _, state = ridge_state(x[train_idx], y[train_idx], x[test_idx], alpha)
                truth_parts.append(y[test_idx])
                std_parts.append(np.broadcast_to(safe_scale(y[train_idx]), (len(test_idx), d)))
                for trait_index, trait in enumerate(frozen_traits):
                    altered = x[test_idx].copy()
                    rng = np.random.default_rng(61_000_000 + MODEL_ORDER.index(model.key) * 100_000 + d * 1_000 + trait_index * 10 + fold_index)
                    altered[:, trait_index] = altered[rng.permutation(len(altered)), trait_index]
                    perm_predictions[trait].append(predict_from_state(altered, state))
            truth = np.concatenate(truth_parts)
            standards = np.concatenate(std_parts)
            permutation: dict[str, tuple[float, float]] = {}
            for trait, predictions in perm_predictions.items():
                summary, _ = metric_result(truth, np.concatenate(predictions), standards, scope)
                permutation[trait] = (
                    summary["aggregate_normalized_geometric_error"]
                    - baseline.summary["aggregate_normalized_geometric_error"],
                    baseline.summary["mean_pc_r2"] - summary["mean_pc_r2"],
                )
            alpha = tune_alpha(x, y, 62_000 + d)
            _, state = ridge_state(x, y, x, alpha)
            beta = np.asarray(state["beta_standardized"])
            for trait_index, trait in enumerate(frozen_traits):
                for pc in range(d):
                    rows.append(
                        {
                            "model": model.label,
                            "model_key": model.key,
                            "scope": scope,
                            "trait": trait,
                            "pc": PC_NAMES[pc],
                            "full_data_descriptive_alpha": alpha,
                            "standardized_ridge_coefficient": beta[trait_index, pc],
                            "leave_one_trait_out_delta_aggregate_nrmse": leaveout[trait][0],
                            "leave_one_trait_out_delta_mean_pc_r2": leaveout[trait][1],
                            "conditional_permutation_delta_aggregate_nrmse": permutation[trait][0],
                            "conditional_permutation_delta_mean_pc_r2": permutation[trait][1],
                        }
                    )
    return pd.DataFrame(rows)


def procrustes_fit(source: np.ndarray, target: np.ndarray, variant: str) -> dict[str, Any]:
    source_mean = source.mean(axis=0)
    target_mean = target.mean(axis=0)
    source_scale = safe_scale(source) if variant == "variance_standardized" else np.ones(source.shape[1])
    target_scale = safe_scale(target) if variant == "variance_standardized" else np.ones(target.shape[1])
    a = (source - source_mean) / source_scale
    b = (target - target_mean) / target_scale
    rotation, _ = orthogonal_procrustes(a, b)
    fitted = a @ rotation
    return {
        "rotation": rotation,
        "source_mean": source_mean,
        "target_mean": target_mean,
        "source_scale": source_scale,
        "target_scale": target_scale,
        "training_relative_frobenius_error": float(np.linalg.norm(fitted - b) / np.linalg.norm(b)),
        "training_coordinate_rmse": float(np.sqrt(np.mean((fitted - b) ** 2))),
        "determinant": float(np.linalg.det(rotation)),
        "orthogonality_max_abs_error": float(np.max(np.abs(rotation.T @ rotation - np.eye(source.shape[1])))),
    }


def procrustes_apply(source: np.ndarray, fit: dict[str, Any]) -> np.ndarray:
    return ((source - fit["source_mean"]) / fit["source_scale"]) @ fit["rotation"]


def procrustes_target(target: np.ndarray, fit: dict[str, Any]) -> np.ndarray:
    return (target - fit["target_mean"]) / fit["target_scale"]


def nearest_neighbor_jaccard(left: np.ndarray, right: np.ndarray, k: int = 10) -> float:
    def neighbors(values: np.ndarray) -> list[set[int]]:
        distance = np.linalg.norm(values[:, None, :] - values[None, :, :], axis=2)
        np.fill_diagonal(distance, np.inf)
        return [set(np.argsort(distance[row])[:k].tolist()) for row in range(len(values))]

    a = neighbors(left)
    b = neighbors(right)
    return float(np.mean([len(x & y) / len(x | y) for x, y in zip(a, b, strict=True)]))


def alignment_metrics(target: np.ndarray, prediction: np.ndarray) -> dict[str, Any]:
    d = target.shape[1]
    residual = prediction - target
    metrics: dict[str, Any] = {
        "coordinate_rmse": float(np.sqrt(np.mean(residual * residual))),
        "geometric_rmse": float(np.sqrt(np.mean(np.sum(residual * residual, axis=1)))),
        "mean_aligned_coordinate_correlation": float(
            np.mean([safe_corr(target[:, pc], prediction[:, pc]) for pc in range(d)])
        ),
        "distance_matrix_correlation": safe_corr(pdist(target), pdist(prediction)),
        "nearest_neighbor_jaccard_k10": nearest_neighbor_jaccard(target, prediction, 10),
    }
    for pc in range(d):
        metrics[f"pc{pc + 1}_heldout_correlation"] = safe_corr(target[:, pc], prediction[:, pc])
    for pc in range(d, 6):
        metrics[f"pc{pc + 1}_heldout_correlation"] = math.nan
    return metrics


def alignment_analyses(
    models: dict[str, ModelData], permutations: int
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pairs = [("llama", "qwen"), ("gemma", "qwen"), ("gemma", "llama")]
    variants = ["raw_pc_scores", "variance_standardized"]
    full_payload: dict[str, Any] = {
        "primary_reference": "qwen",
        "primary_variant": "raw_pc_scores",
        "fits": {},
    }
    cv_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    observed_seed7100: dict[tuple[str, str, int, str], dict[str, Any]] = {}
    for d in [3, 6]:
        for variant in variants:
            for source_key, target_key in pairs:
                pair_name = f"{source_key}_to_{target_key}"
                source = models[source_key].pc_scores[:, :d]
                target = models[target_key].pc_scores[:, :d]
                fit = procrustes_fit(source, target, variant)
                full_payload["fits"][f"{pair_name}__pc1_pc{d}__{variant}"] = {
                    "source_model": models[source_key].label,
                    "target_model": models[target_key].label,
                    "dimensions": d,
                    "variant": variant,
                    **{
                        key: value.tolist() if isinstance(value, np.ndarray) else value
                        for key, value in fit.items()
                    },
                }
                prediction = procrustes_apply(source, fit)
                target_transformed = procrustes_target(target, fit)
                for role, residual in zip(models[source_key].personas, prediction - target_transformed, strict=True):
                    residual_rows.append(
                        {
                            "pair": pair_name,
                            "dimensions": d,
                            "variant": variant,
                            "role": role,
                            "residual_norm": float(np.linalg.norm(residual)),
                            **{f"residual_pc{i + 1}": residual[i] for i in range(d)},
                        }
                    )
                for seed in range(7100, 7110):
                    pred_all = np.empty_like(source)
                    target_all = np.empty_like(target)
                    for fold, (train_idx, test_idx) in enumerate(KFold(5, shuffle=True, random_state=seed).split(source)):
                        fold_fit = procrustes_fit(source[train_idx], target[train_idx], variant)
                        pred_all[test_idx] = procrustes_apply(source[test_idx], fold_fit)
                        target_all[test_idx] = procrustes_target(target[test_idx], fold_fit)
                    metrics = alignment_metrics(target_all, pred_all)
                    row = {
                        "pair": pair_name,
                        "source_model": models[source_key].label,
                        "target_model": models[target_key].label,
                        "dimensions": d,
                        "variant": variant,
                        "protocol": "repeated_5fold",
                        "repeat_seed": seed,
                        "fit_roles_only": True,
                        **metrics,
                    }
                    cv_rows.append(row)
                    if seed == 7100:
                        observed_seed7100[(source_key, target_key, d, variant)] = metrics
                pred_all = np.empty_like(source)
                target_all = np.empty_like(target)
                for split in family_splits(models[source_key].clusters):
                    train_idx = np.asarray(split["train_idx"])
                    test_idx = np.asarray(split["test_idx"])
                    fold_fit = procrustes_fit(source[train_idx], target[train_idx], variant)
                    pred_all[test_idx] = procrustes_apply(source[test_idx], fold_fit)
                    target_all[test_idx] = procrustes_target(target[test_idx], fold_fit)
                cv_rows.append(
                    {
                        "pair": pair_name,
                        "source_model": models[source_key].label,
                        "target_model": models[target_key].label,
                        "dimensions": d,
                        "variant": variant,
                        "protocol": "qwen_canonical_role_family_holdout",
                        "repeat_seed": math.nan,
                        "fit_roles_only": True,
                        **alignment_metrics(target_all, pred_all),
                    }
                )

    null_rows: list[dict[str, Any]] = []
    for d in [3, 6]:
        for variant_index, variant in enumerate(variants):
            for pair_index, (source_key, target_key) in enumerate(pairs):
                pair_name = f"{source_key}_to_{target_key}"
                source = models[source_key].pc_scores[:, :d]
                target = models[target_key].pc_scores[:, :d]
                observed = observed_seed7100[(source_key, target_key, d, variant)]
                split_rows = list(KFold(5, shuffle=True, random_state=7100).split(source))
                for permutation in range(permutations):
                    seed = 9_200_000 + d * 100_000 + variant_index * 10_000 + pair_index * 2_000 + permutation
                    rng = np.random.default_rng(seed)
                    permuted_source = source[rng.permutation(len(source))]
                    pred_all = np.empty_like(source)
                    target_all = np.empty_like(target)
                    for train_idx, test_idx in split_rows:
                        fold_fit = procrustes_fit(permuted_source[train_idx], target[train_idx], variant)
                        pred_all[test_idx] = procrustes_apply(permuted_source[test_idx], fold_fit)
                        target_all[test_idx] = procrustes_target(target[test_idx], fold_fit)
                    metrics = alignment_metrics(target_all, pred_all)
                    null_rows.append(
                        {
                            "pair": pair_name,
                            "dimensions": d,
                            "variant": variant,
                            "permutation": permutation,
                            "permutation_seed": seed,
                            "role_labels_permuted_before_fit": True,
                            "fit_roles_only": True,
                            "observed_geometric_rmse": observed["geometric_rmse"],
                            "observed_mean_aligned_coordinate_correlation": observed["mean_aligned_coordinate_correlation"],
                            "observed_distance_matrix_correlation": observed["distance_matrix_correlation"],
                            **metrics,
                        }
                    )
    return full_payload, pd.DataFrame(cv_rows), pd.DataFrame(null_rows), pd.DataFrame(residual_rows)


def direction_projection(scores: np.ndarray, feature: np.ndarray) -> tuple[np.ndarray, float]:
    centered_scores = scores - scores.mean(axis=0)
    centered_feature = feature - feature.mean()
    coefficient, *_ = np.linalg.lstsq(centered_scores, centered_feature, rcond=None)
    prediction = centered_scores @ coefficient
    denominator = float(np.sum(centered_feature * centered_feature))
    r2 = 1.0 - float(np.sum((centered_feature - prediction) ** 2)) / denominator
    return unit(coefficient), r2


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.dot(unit(left), unit(right)))


def classify_recurrence(values: Sequence[float]) -> str:
    mean_value = float(np.mean(values))
    minimum = float(np.min(values))
    if mean_value >= 0.75 and minimum >= 0.60:
        return "HIGH CROSS-MODEL RECURRENCE"
    if mean_value >= 0.50 and minimum >= 0.25:
        return "MODERATE"
    return "WEAK / MODEL-SPECIFIC"


def aligned_directions(
    models: dict[str, ModelData],
    full_alignments: dict[str, Any],
    frozen_traits: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any], dict[int, dict[str, Any]]]:
    human_rows: list[dict[str, Any]] = []
    bigfive_rows: list[dict[str, Any]] = []
    consensus_rows: list[dict[str, Any]] = []
    all_by_dim: dict[int, dict[str, Any]] = {}
    for d in [3, 6]:
        rotations = {
            key: np.asarray(
                full_alignments["fits"][f"{key}_to_qwen__pc1_pc{d}__raw_pc_scores"]["rotation"],
                dtype=np.float64,
            )
            for key in ["llama", "gemma"]
        }
        family_payload: dict[str, dict[str, Any]] = {}
        for family, names, feature_getter in [
            (
                "human_supported_12",
                frozen_traits,
                lambda model, name: model.trait_scores[:, model.traits.index(name)],
            ),
            (
                "externally_anchored_big_five_5",
                DOMAINS,
                lambda model, name: model.big_five[:, DOMAINS.index(name)],
            ),
        ]:
            family_payload[family] = {}
            for name in names:
                local: dict[str, np.ndarray] = {}
                projection_r2: dict[str, float] = {}
                for key in MODEL_ORDER:
                    local[key], projection_r2[key] = direction_projection(
                        models[key].pc_scores[:, :d], feature_getter(models[key], name)
                    )
                aligned = {
                    "qwen": local["qwen"],
                    "llama": unit(rotations["llama"].T @ local["llama"]),
                    "gemma": unit(rotations["gemma"].T @ local["gemma"]),
                }
                pairwise = {
                    "qwen_llama": cosine(aligned["qwen"], aligned["llama"]),
                    "qwen_gemma": cosine(aligned["qwen"], aligned["gemma"]),
                    "llama_gemma": cosine(aligned["llama"], aligned["gemma"]),
                }
                consensus = unit(np.mean(np.stack(list(aligned.values())), axis=0))
                angles = [math.degrees(math.acos(float(np.clip(cosine(vector, consensus), -1, 1)))) for vector in aligned.values()]
                recurrence = classify_recurrence(list(pairwise.values()))
                row = {
                    "dimensions": d,
                    "trait" if family == "human_supported_12" else "domain": name,
                    "qwen_local_vector": json.dumps(local["qwen"].tolist()),
                    "llama_local_vector": json.dumps(local["llama"].tolist()),
                    "gemma_local_vector": json.dumps(local["gemma"].tolist()),
                    "qwen_aligned_vector": json.dumps(aligned["qwen"].tolist()),
                    "llama_aligned_vector": json.dumps(aligned["llama"].tolist()),
                    "gemma_aligned_vector": json.dumps(aligned["gemma"].tolist()),
                    "qwen_projection_r2": projection_r2["qwen"],
                    "llama_projection_r2": projection_r2["llama"],
                    "gemma_projection_r2": projection_r2["gemma"],
                    "qwen_llama_cosine": pairwise["qwen_llama"],
                    "qwen_gemma_cosine": pairwise["qwen_gemma"],
                    "llama_gemma_cosine": pairwise["llama_gemma"],
                    "qwen_llama_angular_disagreement_degrees": math.degrees(math.acos(float(np.clip(pairwise["qwen_llama"], -1, 1)))),
                    "qwen_gemma_angular_disagreement_degrees": math.degrees(math.acos(float(np.clip(pairwise["qwen_gemma"], -1, 1)))),
                    "llama_gemma_angular_disagreement_degrees": math.degrees(math.acos(float(np.clip(pairwise["llama_gemma"], -1, 1)))),
                    "qwen_llama_euclidean_disagreement": float(np.linalg.norm(aligned["qwen"] - aligned["llama"])),
                    "qwen_gemma_euclidean_disagreement": float(np.linalg.norm(aligned["qwen"] - aligned["gemma"])),
                    "llama_gemma_euclidean_disagreement": float(np.linalg.norm(aligned["llama"] - aligned["gemma"])),
                    "consensus_vector": json.dumps(consensus.tolist()),
                    "mean_pairwise_cosine": float(np.mean(list(pairwise.values()))),
                    "minimum_pairwise_cosine": float(np.min(list(pairwise.values()))),
                    "maximum_pairwise_cosine": float(np.max(list(pairwise.values()))),
                    "mean_angular_dispersion_degrees": float(np.mean(angles)),
                    "recurrence_classification": recurrence,
                }
                family_payload[family][name] = {"local": local, "aligned": aligned, "row": row}
                if family == "human_supported_12":
                    human_rows.append(row)
                else:
                    bigfive_rows.append(row)
                consensus_rows.append(
                    {
                        "feature_family": family,
                        "feature": name,
                        "dimensions": d,
                        "consensus_vector": row["consensus_vector"],
                        "mean_pairwise_cosine": row["mean_pairwise_cosine"],
                        "minimum_pairwise_cosine": row["minimum_pairwise_cosine"],
                        "maximum_pairwise_cosine": row["maximum_pairwise_cosine"],
                        "mean_angular_dispersion_degrees": row["mean_angular_dispersion_degrees"],
                        "recurrence_classification": recurrence,
                    }
                )
        all_by_dim[d] = family_payload
    agree = all_by_dim[6]["externally_anchored_big_five_5"]["agreeableness"]
    row = agree["row"]
    consensus = np.asarray(json.loads(row["consensus_vector"]))
    fractions = {
        key: cosine(vector, consensus) ** 2 for key, vector in agree["aligned"].items()
    }
    mean_pair = float(row["mean_pairwise_cosine"])
    min_pair = float(row["minimum_pairwise_cosine"])
    if mean_pair >= 0.70 and min_pair >= 0.50:
        decision = "RECONCILED"
    elif mean_pair >= 0.50:
        decision = "PARTIALLY RECONCILED"
    else:
        decision = "NOT RECONCILED"
    agree_payload = {
        "focal_domain": "agreeableness",
        "dimensions": 6,
        "decision_rule_source": "analysis_preregistration.json",
        "decision": decision,
        "qwen_local_vector": agree["local"]["qwen"].tolist(),
        "llama_local_vector": agree["local"]["llama"].tolist(),
        "gemma_local_vector": agree["local"]["gemma"].tolist(),
        "qwen_aligned_vector": agree["aligned"]["qwen"].tolist(),
        "llama_aligned_vector": agree["aligned"]["llama"].tolist(),
        "gemma_aligned_vector": agree["aligned"]["gemma"].tolist(),
        "aligned_pairwise_cosines": {
            "qwen_llama": row["qwen_llama_cosine"],
            "qwen_gemma": row["qwen_gemma_cosine"],
            "llama_gemma": row["llama_gemma_cosine"],
        },
        "consensus_direction": consensus.tolist(),
        "fraction_of_directional_energy_in_consensus_squared_cosine": fractions,
        "mean_pairwise_cosine": mean_pair,
        "minimum_pairwise_cosine": min_pair,
    }
    return (
        pd.DataFrame(human_rows),
        pd.DataFrame(bigfive_rows),
        pd.DataFrame(consensus_rows),
        agree_payload,
        all_by_dim,
    )


def control_comparisons(
    summaries: pd.DataFrame,
    random_real: pd.DataFrame,
    persona_span: pd.DataFrame,
    isotropic: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    comparator_rows: list[dict[str, Any]] = []
    budget_rows: list[dict[str, Any]] = []
    primary = summaries[summaries["protocol"].eq("fixed_5fold_seed42")]
    for model_key in MODEL_ORDER:
        for scope in ["core", "extended"]:
            current = primary[(primary["model_key"].eq(model_key)) & (primary["scope"].eq(scope))]
            human = current[current["feature_family"].eq("human_supported_12")].iloc[0]
            optimized12 = current[current["feature_family"].eq("geometry_optimized_real_traits_12")].iloc[0]
            controls = {
                "random_real_12": random_real[(random_real.model_key == model_key) & (random_real.scope == scope) & (random_real.feature_budget == 12)],
                "persona_span_12": persona_span[(persona_span.model_key == model_key) & (persona_span.scope == scope) & (persona_span.feature_budget == 12)],
                "isotropic_12": isotropic[(isotropic.model_key == model_key) & (isotropic.scope == scope) & (isotropic.feature_budget == 12)],
            }
            metric = "aggregate_normalized_geometric_error"
            inferential: dict[str, Any] = {}
            for name, frame in controls.items():
                values = frame[metric].to_numpy(dtype=float)
                inferential[f"{name}_median_error"] = float(np.median(values))
                inferential[f"{name}_empirical_percentile"] = float(100.0 * np.mean(values >= human[metric]))
                inferential[f"{name}_empirical_one_sided_p"] = float((1 + np.sum(values <= human[metric])) / (len(values) + 1))
                inferential[f"{name}_relative_improvement"] = float((np.median(values) - human[metric]) / np.median(values))
            for family in ["human_supported_12", "geometry_optimized_real_traits_12", "externally_anchored_big_five_5", "direct_semantic_45", "full_real_traits_240"]:
                row = current[current["feature_family"].eq(family)].iloc[0].to_dict()
                if family == "human_supported_12":
                    row.update(inferential)
                comparator_rows.append(row)
            for name, frame in controls.items():
                values = frame[metric].to_numpy(dtype=float)
                comparator_rows.append(
                    {
                        "model": human["model"],
                        "model_key": model_key,
                        "feature_family": name + "_median",
                        "feature_count": 12,
                        "protocol": "fixed_5fold_seed42_distribution",
                        "scope": scope,
                        metric: float(np.median(values)),
                        "null_q05": float(np.quantile(values, 0.05)),
                        "null_q95": float(np.quantile(values, 0.95)),
                    }
                )
            for budget in [5, 12]:
                for control_name, frame in [("random_real", random_real), ("persona_span", persona_span), ("isotropic", isotropic)]:
                    values = frame[
                        (frame.model_key == model_key) & (frame.scope == scope) & (frame.feature_budget == budget)
                    ][metric].to_numpy(dtype=float)
                    budget_rows.append(
                        {
                            "model": human["model"],
                            "model_key": model_key,
                            "scope": scope,
                            "feature_budget": budget,
                            "feature_family": control_name,
                            "estimate_type": "distribution",
                            "aggregate_normalized_geometric_error": float(np.median(values)),
                            "q05": float(np.quantile(values, 0.05)),
                            "q95": float(np.quantile(values, 0.95)),
                            "draws": len(values),
                        }
                    )
                actual_family = "externally_anchored_big_five_5" if budget == 5 else "human_supported_12"
                optimized_family = f"geometry_optimized_real_traits_{budget}"
                for family in [actual_family, optimized_family]:
                    actual = current[current.feature_family.eq(family)].iloc[0]
                    budget_rows.append(
                        {
                            "model": actual["model"],
                            "model_key": model_key,
                            "scope": scope,
                            "feature_budget": budget,
                            "feature_family": family,
                            "estimate_type": "point",
                            "aggregate_normalized_geometric_error": actual[metric],
                            "q05": math.nan,
                            "q95": math.nan,
                            "draws": 1,
                        }
                    )
    return pd.DataFrame(comparator_rows), pd.DataFrame(budget_rows)


def subspace_coverage(
    models: dict[str, ModelData],
    summaries: pd.DataFrame,
    optimized_paths: pd.DataFrame,
    frozen_traits: list[str],
    direct_traits: list[str],
) -> pd.DataFrame:
    rows = []
    primary = summaries[(summaries.protocol == "fixed_5fold_seed42") & (summaries.scope == "extended")]
    for model in models.values():
        families = {
            "externally_anchored_big_five_5": model.big_five,
            "human_supported_12": model.trait_scores[:, [model.traits.index(x) for x in frozen_traits]],
            "direct_semantic_45": model.trait_scores[:, [model.traits.index(x) for x in direct_traits]],
            "full_real_traits_240": model.trait_scores,
        }
        for name, features in families.items():
            standardized = (features - features.mean(axis=0)) / safe_scale(features)
            singular = np.linalg.svd(standardized, compute_uv=False)
            rank = int(np.sum(singular > singular[0] * 1e-10))
            condition = float(singular[0] / singular[rank - 1])
            correlation = np.corrcoef(standardized, rowvar=False)
            offdiag = np.abs(correlation[np.triu_indices(correlation.shape[0], 1)]) if correlation.shape[0] > 1 else np.asarray([])
            perf = primary[(primary.model_key == model.key) & (primary.feature_family == name)].iloc[0]
            rows.append(
                {
                    "model": model.label,
                    "model_key": model.key,
                    "feature_family": name,
                    "feature_count": features.shape[1],
                    "matrix_rank": rank,
                    "condition_number_nonzero_span": condition,
                    "mean_absolute_pairwise_correlation": float(offdiag.mean()) if len(offdiag) else 0.0,
                    "max_absolute_pairwise_correlation": float(offdiag.max()) if len(offdiag) else 0.0,
                    "heldout_mean_pc1_pc6_r2": perf["mean_pc_r2"],
                    "heldout_pc1_pc6_aggregate_nrmse": perf["aggregate_normalized_geometric_error"],
                    "coverage_protocol": "fixed 5-fold seed 42 with fold-local four-fold alpha tuning",
                }
            )
        opt_perf = primary[
            (primary.model_key == model.key) & (primary.feature_family == "geometry_optimized_real_traits_12")
        ].iloc[0]
        opt = optimized_paths[(optimized_paths.model_key == model.key) & (optimized_paths.scope == "extended")]
        fold_stats = []
        for _, group in opt.groupby("outer_fold"):
            selected_names = group.sort_values("entry_rank").head(12)["trait"].tolist()
            features = model.trait_scores[:, [model.traits.index(x) for x in selected_names]]
            standardized = (features - features.mean(axis=0)) / safe_scale(features)
            singular = np.linalg.svd(standardized, compute_uv=False)
            rank = int(np.sum(singular > singular[0] * 1e-10))
            corr = np.corrcoef(standardized, rowvar=False)
            offdiag = np.abs(corr[np.triu_indices(12, 1)])
            fold_stats.append((rank, singular[0] / singular[rank - 1], offdiag.mean(), offdiag.max()))
        rows.append(
            {
                "model": model.label,
                "model_key": model.key,
                "feature_family": "geometry_optimized_real_traits_12",
                "feature_count": 12,
                "matrix_rank": float(np.mean([x[0] for x in fold_stats])),
                "condition_number_nonzero_span": float(np.mean([x[1] for x in fold_stats])),
                "mean_absolute_pairwise_correlation": float(np.mean([x[2] for x in fold_stats])),
                "max_absolute_pairwise_correlation": float(np.mean([x[3] for x in fold_stats])),
                "heldout_mean_pc1_pc6_r2": opt_perf["mean_pc_r2"],
                "heldout_pc1_pc6_aggregate_nrmse": opt_perf["aggregate_normalized_geometric_error"],
                "coverage_protocol": "nested fold-local AA-4 forward selection at k=12",
            }
        )
    frame = pd.DataFrame(rows)
    for model_key in MODEL_ORDER:
        bf_error = frame[(frame.model_key == model_key) & (frame.feature_family == "externally_anchored_big_five_5")]["heldout_pc1_pc6_aggregate_nrmse"].iloc[0]
        hs_error = frame[(frame.model_key == model_key) & (frame.feature_family == "human_supported_12")]["heldout_pc1_pc6_aggregate_nrmse"].iloc[0]
        frame.loc[frame.model_key == model_key, "error_reduction_vs_big_five"] = bf_error - frame.loc[frame.model_key == model_key, "heldout_pc1_pc6_aggregate_nrmse"]
        frame.loc[frame.model_key == model_key, "error_reduction_vs_human_supported_12"] = hs_error - frame.loc[frame.model_key == model_key, "heldout_pc1_pc6_aggregate_nrmse"]
    return frame


def core_vs_extended(
    alignment_cv: pd.DataFrame,
    directions: dict[int, dict[str, Any]],
) -> pd.DataFrame:
    rows = []
    cv = alignment_cv[
        (alignment_cv.protocol == "repeated_5fold") & (alignment_cv.variant == "raw_pc_scores")
    ]
    for d in [3, 6]:
        subset = cv[cv.dimensions == d]
        rows.append(
            {
                "measure_family": "alignment_cv",
                "dimensions": d,
                "mean_coordinate_correlation": subset["mean_aligned_coordinate_correlation"].mean(),
                "mean_distance_matrix_correlation": subset["distance_matrix_correlation"].mean(),
                "mean_geometric_rmse": subset["geometric_rmse"].mean(),
                "mean_pairwise_direction_cosine": math.nan,
            }
        )
        for family in ["human_supported_12", "externally_anchored_big_five_5"]:
            values = [payload["row"]["mean_pairwise_cosine"] for payload in directions[d][family].values()]
            rows.append(
                {
                    "measure_family": family,
                    "dimensions": d,
                    "mean_coordinate_correlation": math.nan,
                    "mean_distance_matrix_correlation": math.nan,
                    "mean_geometric_rmse": math.nan,
                    "mean_pairwise_direction_cosine": float(np.mean(values)),
                }
            )
        agree = directions[d]["externally_anchored_big_five_5"]["agreeableness"]["row"]["mean_pairwise_cosine"]
        rows.append(
            {
                "measure_family": "agreeableness_focal",
                "dimensions": d,
                "mean_pairwise_direction_cosine": agree,
                "mean_coordinate_correlation": math.nan,
                "mean_distance_matrix_correlation": math.nan,
                "mean_geometric_rmse": math.nan,
            }
        )
    frame = pd.DataFrame(rows)
    for family in frame.measure_family.unique():
        core = frame[(frame.measure_family == family) & (frame.dimensions == 3)].iloc[0]
        extended = frame[(frame.measure_family == family) & (frame.dimensions == 6)].iloc[0]
        mask = frame.measure_family == family
        frame.loc[mask, "pc1_pc6_minus_pc1_pc3_direction_cosine"] = (
            extended["mean_pairwise_direction_cosine"] - core["mean_pairwise_direction_cosine"]
            if pd.notna(core["mean_pairwise_direction_cosine"])
            else math.nan
        )
        frame.loc[mask, "material_direction_improvement_ge_0_10"] = bool(
            pd.notna(core["mean_pairwise_direction_cosine"])
            and extended["mean_pairwise_direction_cosine"] - core["mean_pairwise_direction_cosine"] >= 0.10
        )
    return frame


def make_figures(
    out: Path,
    comparator: pd.DataFrame,
    per_pc: pd.DataFrame,
    associations: pd.DataFrame,
    human_dirs: pd.DataFrame,
    bigfive_dirs: pd.DataFrame,
    agree: dict[str, Any],
    coverage: pd.DataFrame,
    random_real: pd.DataFrame,
    persona_span: pd.DataFrame,
    isotropic: pd.DataFrame,
) -> None:
    colors = {"qwen": "#4C78A8", "llama": "#F58518", "gemma": "#54A24B"}

    def save(fig: Any, stem: str) -> None:
        fig.tight_layout()
        fig.savefig(out / f"{stem}.png", dpi=180, metadata={"Date": GENERATION_TIMESTAMP})
        fig.savefig(out / f"{stem}.svg", metadata={"Date": GENERATION_TIMESTAMP})
        plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=False)
    for axis, key in zip(axes, MODEL_ORDER, strict=True):
        values = [
            random_real[(random_real.model_key == key) & (random_real.scope == "extended") & (random_real.feature_budget == 12)]["aggregate_normalized_geometric_error"],
            persona_span[(persona_span.model_key == key) & (persona_span.scope == "extended") & (persona_span.feature_budget == 12)]["aggregate_normalized_geometric_error"],
            isotropic[(isotropic.model_key == key) & (isotropic.scope == "extended") & (isotropic.feature_budget == 12)]["aggregate_normalized_geometric_error"],
        ]
        axis.boxplot(values, labels=["random\nreal", "persona\nspan", "isotropic"], showfliers=False)
        current = comparator[(comparator.model_key == key) & (comparator.scope == "extended")]
        for family, marker, color, xpos in [
            ("human_supported_12", "*", "#B22222", 1.0),
            ("geometry_optimized_real_traits_12", "D", "#111111", 1.15),
        ]:
            row = current[current.feature_family == family].iloc[0]
            axis.scatter(xpos, row["aggregate_normalized_geometric_error"], marker=marker, s=90, color=color, zorder=5)
        axis.set_title(MODEL_SPECS[key]["label"])
        axis.set_ylabel("PC1–PC6 aggregate nRMSE")
    save(fig, "figure_a_k12_compact_budget_comparison")

    primary = per_pc[(per_pc.protocol == "fixed_5fold_seed42") & (per_pc.scope == "extended")]
    families = ["human_supported_12", "geometry_optimized_real_traits_12", "externally_anchored_big_five_5", "direct_semantic_45", "full_real_traits_240"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    for axis, key in zip(axes, MODEL_ORDER, strict=True):
        current = primary[(primary.model_key == key) & (primary.feature_family.isin(families))]
        pivot = current.pivot(index="feature_family", columns="pc", values="r2").reindex(families)
        im = axis.imshow(pivot, aspect="auto", vmin=0, vmax=1, cmap="viridis")
        axis.set_xticks(range(6), PC_NAMES)
        axis.set_yticks(range(len(families)), [x.replace("_", " ") for x in families])
        axis.set_title(MODEL_SPECS[key]["label"])
    fig.colorbar(im, ax=axes, label="Held-out R²", shrink=0.8)
    save(fig, "figure_b_pc_prediction_by_feature_family")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    frozen_order = json.loads(FREEZE_PATH.read_text())["traits"]
    frozen_order = [row["trait"] for row in frozen_order]
    for axis, key in zip(axes, MODEL_ORDER, strict=True):
        current = associations[associations.model_key == key].pivot(index="trait", columns="pc", values="pearson").reindex(frozen_order)
        im = axis.imshow(current, aspect="auto", vmin=-1, vmax=1, cmap="coolwarm")
        axis.set_xticks(range(6), PC_NAMES)
        axis.set_yticks(range(12), frozen_order)
        axis.set_title(MODEL_SPECS[key]["label"])
    fig.colorbar(im, ax=axes, label="Pearson r", shrink=0.8)
    save(fig, "figure_c_human_trait_pc_association_heatmap")

    for frame, stem, feature_column in [
        (human_dirs[human_dirs.dimensions == 6], "figure_d_aligned_human_trait_similarity", "trait"),
        (bigfive_dirs[bigfive_dirs.dimensions == 6], "figure_e_aligned_big_five_similarity", "domain"),
    ]:
        columns = ["qwen_llama_cosine", "qwen_gemma_cosine", "llama_gemma_cosine"]
        data = frame.set_index(feature_column)[columns]
        fig, axis = plt.subplots(figsize=(7, max(3, 0.35 * len(data))))
        im = axis.imshow(data, aspect="auto", vmin=-1, vmax=1, cmap="coolwarm")
        axis.set_xticks(range(3), ["Qwen–Llama", "Qwen–Gemma", "Llama–Gemma"])
        axis.set_yticks(range(len(data)), data.index.tolist())
        fig.colorbar(im, ax=axis, label="Aligned direction cosine")
        save(fig, stem)

    local = np.vstack([agree[f"{key}_local_vector"] for key in MODEL_ORDER])
    aligned = np.vstack([agree[f"{key}_aligned_vector"] for key in MODEL_ORDER])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    for axis, values, title in [(axes[0], local, "Local PC coefficients"), (axes[1], aligned, "Qwen-aligned coefficients")]:
        x = np.arange(6)
        for index, key in enumerate(MODEL_ORDER):
            axis.plot(x, values[index], marker="o", label=key, color=colors[key])
        axis.axhline(0, color="#999999", linewidth=0.8)
        axis.set_xticks(x, PC_NAMES)
        axis.set_title(title)
    axes[1].legend()
    save(fig, "figure_f_agreeableness_local_vs_aligned")

    fig, axis = plt.subplots(figsize=(10, 4))
    current = coverage[coverage.feature_family.isin(["externally_anchored_big_five_5", "human_supported_12"])]
    x = np.arange(3)
    width = 0.34
    for offset, family in [(-width / 2, "externally_anchored_big_five_5"), (width / 2, "human_supported_12")]:
        values = [current[(current.model_key == key) & (current.feature_family == family)]["heldout_pc1_pc6_aggregate_nrmse"].iloc[0] for key in MODEL_ORDER]
        axis.bar(x + offset, values, width, label=family.replace("_", " "))
    axis.set_xticks(x, [MODEL_SPECS[key]["label"] for key in MODEL_ORDER])
    axis.set_ylabel("PC1–PC6 aggregate nRMSE")
    axis.legend()
    save(fig, "figure_g_big_five_vs_human12_coverage")


def evidence_decisions(
    comparator: pd.DataFrame,
    alignment_null: pd.DataFrame,
    consensus: pd.DataFrame,
) -> dict[str, Any]:
    human = comparator[comparator.feature_family == "human_supported_12"].copy()
    random_pass = human["random_real_12_empirical_one_sided_p"] <= 0.05
    span_pass = human["persona_span_12_empirical_one_sided_p"] <= 0.05
    by_scope = {
        scope: {
            key: {
                "random_real_pass": bool(human[(human.model_key == key) & (human.scope == scope)]["random_real_12_empirical_one_sided_p"].iloc[0] <= 0.05),
                "persona_span_pass": bool(human[(human.model_key == key) & (human.scope == scope)]["persona_span_12_empirical_one_sided_p"].iloc[0] <= 0.05),
            }
            for key in MODEL_ORDER
        }
        for scope in ["core", "extended"]
    }
    strong = bool(random_pass.all() and span_pass.all())
    moderate = all(
        sum(by_scope[scope][key]["random_real_pass"] for key in MODEL_ORDER) >= 2
        for scope in ["core", "extended"]
    )
    strength = "STRONG CROSS-MODEL" if strong else ("MODERATE CROSS-MODEL" if moderate else "WEAK / ABSENT")
    null6 = alignment_null[(alignment_null.dimensions == 6) & (alignment_null.variant == "raw_pc_scores")]
    alignment_p: dict[str, float] = {}
    for pair in ["llama_to_qwen", "gemma_to_qwen"]:
        group = null6[null6.pair == pair]
        observed = float(group["observed_mean_aligned_coordinate_correlation"].iloc[0])
        alignment_p[pair] = float((1 + np.sum(group["mean_aligned_coordinate_correlation"] >= observed)) / (len(group) + 1))
    human_consensus = consensus[(consensus.feature_family == "human_supported_12") & (consensus.dimensions == 6)]
    recurring = int(human_consensus.recurrence_classification.isin(["MODERATE", "HIGH CROSS-MODEL RECURRENCE"]).sum())
    random_and_span_two_models_both = all(
        sum(
            by_scope[scope][key]["random_real_pass"] and by_scope[scope][key]["persona_span_pass"]
            for key in MODEL_ORDER
        ) >= 2
        for scope in ["core", "extended"]
    )
    no_remaining_reverse = all(
        human[column].ge(0).all()
        for column in ["random_real_12_relative_improvement"]
    )
    future_gate = bool(
        random_and_span_two_models_both
        and no_remaining_reverse
        and all(value <= 0.05 for value in alignment_p.values())
        and recurring >= 6
    )
    return {
        "evidence_strength": strength,
        "model_scope_control_passes": by_scope,
        "alignment_qwen_reference_empirical_p": alignment_p,
        "moderate_or_high_recurrent_human_traits_pc1_pc6": recurring,
        "later_human_respondent_projection_design_gate_passed": future_gate,
        "later_study_statement": "A later human-respondent projection design is justified for planning only." if future_gate else "AA-7 does not satisfy the preregistered gate for designing a human-respondent projection study.",
    }


def write_report(
    out: Path,
    comparator: pd.DataFrame,
    associations: pd.DataFrame,
    utility: pd.DataFrame,
    alignment_cv: pd.DataFrame,
    alignment_null: pd.DataFrame,
    human_dirs: pd.DataFrame,
    bigfive_dirs: pd.DataFrame,
    agree: dict[str, Any],
    core_extended: pd.DataFrame,
    coverage: pd.DataFrame,
    decisions: dict[str, Any],
) -> None:
    human = comparator[comparator.feature_family == "human_supported_12"]
    lines = [
        "# AA-7 — Human-supported trait convergence and cross-model aligned-subspace study",
        "",
        "## Primary convergence answer",
        "",
        f"Preregistered evidence classification: **{decisions['evidence_strength']}**.",
        "",
        "The table below is the primary fixed-split matched comparison. Aggregate nRMSE is fold-standardized Euclidean geometric error, so lower is better. Empirical p-values are one-sided against 500 target-independent matched banks.",
        "",
        "| Model | Scope | Human 12 mean R² | Human 12 nRMSE | random median | p vs random | persona-span median | p vs span | optimized 12 nRMSE |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key in MODEL_ORDER:
        for scope in ["core", "extended"]:
            row = human[(human.model_key == key) & (human.scope == scope)].iloc[0]
            opt = comparator[(comparator.model_key == key) & (comparator.scope == scope) & (comparator.feature_family == "geometry_optimized_real_traits_12")].iloc[0]
            lines.append(
                f"| {MODEL_SPECS[key]['label']} | {scope} | {row['mean_pc_r2']:.4f} | {row['aggregate_normalized_geometric_error']:.4f} | {row['random_real_12_median_error']:.4f} | {row['random_real_12_empirical_one_sided_p']:.4f} | {row['persona_span_12_median_error']:.4f} | {row['persona_span_12_empirical_one_sided_p']:.4f} | {opt['aggregate_normalized_geometric_error']:.4f} |"
            )
    lines.extend([
        "",
        "Absolute feature-family and per-PC results are in `comparator_summary.csv`, `local_pc_prediction_summary.csv`, and `local_pc_prediction_per_pc.csv`. Big Five uses five features and is not treated as an equal-budget comparison with the 12-trait families.",
        "",
        "## Individual traits and human-support level",
        "",
    ])
    for key in MODEL_ORDER:
        current = associations[associations.model_key == key].copy()
        current["abs_pearson"] = current["pearson"].abs()
        top = current.nlargest(3, "abs_pearson")
        text = ", ".join(f"{row.trait}–{row.pc} (r={row.pearson:.3f})" for row in top.itertuples())
        lines.append(f"- {MODEL_SPECS[key]['label']}: {text}.")
    lines.append("")
    for key in MODEL_ORDER:
        row = utility[(utility.record_type == "ordinal_association") & (utility.trait_family == "human_supported_12") & (utility.model_key == key) & (utility.scope == "extended")].iloc[0]
        lines.append(f"- {MODEL_SPECS[key]['label']} AA-1 support versus extended geometric utility: Spearman rho={row.support_utility_spearman:.3f}; high mean={row.high_mean_utility:.3f}, moderate mean={row.moderate_mean_utility:.3f}. N=12; descriptive only.")
    lines.extend([
        "",
        "## Phase 2 — held-out role-score subspace alignment",
        "",
        "Primary alignment uses centered raw model-local PC scores; variance-standardized alignment is a declared sensitivity. Values below average the ten repeated role-held-out folds for PC1–PC6.",
        "",
        "| Pair | coordinate r | distance r | geometric RMSE | permutation p (coordinate r) |",
        "|---|---:|---:|---:|---:|",
    ])
    cv6 = alignment_cv[(alignment_cv.dimensions == 6) & (alignment_cv.variant == "raw_pc_scores") & (alignment_cv.protocol == "repeated_5fold")]
    null6 = alignment_null[(alignment_null.dimensions == 6) & (alignment_null.variant == "raw_pc_scores")]
    for pair in ["llama_to_qwen", "gemma_to_qwen", "gemma_to_llama"]:
        cv = cv6[cv6.pair == pair]
        null = null6[null6.pair == pair]
        observed = cv[cv.repeat_seed == 7100]["mean_aligned_coordinate_correlation"].iloc[0]
        p = (1 + np.sum(null["mean_aligned_coordinate_correlation"] >= observed)) / (len(null) + 1)
        lines.append(f"| {pair} | {cv.mean_aligned_coordinate_correlation.mean():.3f} | {cv.distance_matrix_correlation.mean():.3f} | {cv.geometric_rmse.mean():.3f} | {p:.4f} |")
    h6 = human_dirs[human_dirs.dimensions == 6]
    b6 = bigfive_dirs[bigfive_dirs.dimensions == 6]
    lines.extend([
        "",
        f"Human-supported recurrence: {(h6.recurrence_classification == 'HIGH CROSS-MODEL RECURRENCE').sum()} high, {(h6.recurrence_classification == 'MODERATE').sum()} moderate, {(h6.recurrence_classification == 'WEAK / MODEL-SPECIFIC').sum()} weak/model-specific.",
        f"Big Five recurrence: {(b6.recurrence_classification == 'HIGH CROSS-MODEL RECURRENCE').sum()} high, {(b6.recurrence_classification == 'MODERATE').sum()} moderate, {(b6.recurrence_classification == 'WEAK / MODEL-SPECIFIC').sum()} weak/model-specific.",
        "",
        "## Focal Agreeableness result",
        "",
        f"Preregistered decision: **{agree['decision']}**. Aligned pairwise cosines are Qwen–Llama {agree['aligned_pairwise_cosines']['qwen_llama']:.3f}, Qwen–Gemma {agree['aligned_pairwise_cosines']['qwen_gemma']:.3f}, and Llama–Gemma {agree['aligned_pairwise_cosines']['llama_gemma']:.3f}. The full local and aligned six-dimensional vectors and squared-cosine consensus fractions are in `aligned_agreeableness_focal_test.json`.",
        "",
        "## Core versus secondary coordinates",
        "",
    ])
    for family in ["human_supported_12", "externally_anchored_big_five_5", "agreeableness_focal"]:
        row = core_extended[(core_extended.measure_family == family) & (core_extended.dimensions == 6)].iloc[0]
        lines.append(f"- {family}: mean aligned direction cosine change from PC1–PC3 to PC1–PC6 = {row.pc1_pc6_minus_pc1_pc3_direction_cosine:.3f}; preregistered material-improvement flag = {bool(row.material_direction_improvement_ge_0_10)}.")
    lines.extend([
        "",
        "## Big Five versus the frozen 12",
        "",
        "`feature_family_subspace_coverage.csv` reports held-out coverage, numerical rank, condition number, redundancy, and error reductions. The comparison distinguishes the five-feature Big Five budget from the 12-feature human-supported family and does not treat raw feature counts as equal.",
        "",
        "## Observed",
        "",
        "All numerical statements above are measurements on existing model role vectors, model trait directions, and model-local role-score coordinates. The random-real and generic controls are matched and target-independent; persona-span directions are constructed inside each outer training fold.",
        "",
        "## Interpretation",
        "",
        "AA-7 tests whether human psychometric evidence supplied a useful geometry-blind construct filter. Any advantage is representational/geometric convergence within model activation artifacts, not evidence that the constructs are realized as human psychology in a model.",
        "",
        "## Hypotheses",
        "",
        "Cross-model recurrence after rotation is consistent with shared organization over the 275 role labels. It does not identify a causal latent mechanism, and shared role prompts remain a possible common source of structure.",
        "",
        "## Unknown",
        "",
        "Independent expert review may further contract the AA-1 bridge. Behavioral realization, causal control, respondent-level transfer, and generalization beyond the three saved-vector releases remain unknown.",
        "",
        "## Later human-respondent study gate",
        "",
        decisions["later_study_statement"],
        "",
        "## Scientific boundary",
        "",
        "The 12-trait set was frozen from prior human-data evidence before AA-7 geometry analysis. No human respondent or human occupational centroid was projected into model geometry. No respondent-level human microdata were committed. No GPU, RunPod, model inference, activation extraction, response generation, external model API, or human outcome prediction was used.",
    ])
    (out / "human_supported_trait_convergence_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def source_manifest(
    vector_root: Path,
    source_checks: dict[str, Any],
    sampler_audit: dict[str, Any],
    draws: int,
    permutations: int,
) -> dict[str, Any]:
    source_paths = [
        FREEZE_PATH,
        PREREG_PATH,
        AA1_SUPPORT,
        AA2_SCORES,
        AA2_DIRECTIONS,
        AA3_VIEWER,
        CLUSTERS,
        REPO / "research/outputs/extended_persona_pca/source_manifest.json",
        REPO / "research/outputs/qwen_trait_sparsity_prediction/source_manifest.json",
        *MATRIX_PATHS.values(),
    ]
    return {
        "analysis": "AA-7 human-supported trait convergence and cross-model aligned-subspace study",
        "analysis_model": "GPT-5.5",
        "branch": "codex/aa7-human-trait-convergence",
        "canonical_starting_sha": CANONICAL_STARTING_SHA,
        "freeze_commit": FREEZE_COMMIT,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "generation_timestamp_utc": GENERATION_TIMESTAMP,
        "inputs": {
            str(path.relative_to(REPO)): {"sha256": sha256_file(path), "size_bytes": path.stat().st_size}
            for path in source_paths
        },
        "vector_root_actual": str(vector_root),
        "vector_source_checks": source_checks,
        "random_controls": {"draws_per_model_and_budget": draws, "alignment_permutations_per_pair_variant_dimension": permutations},
        "isotropic_sampler_audit": sampler_audit,
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
            "matplotlib": matplotlib.__version__,
            "torch": torch.__version__,
        },
        "compute": {
            "cpu_only": True,
            "gpu_used": False,
            "runpod_used": False,
            "new_model_inference": False,
            "activation_extraction": False,
            "response_generation": False,
            "external_model_api": False,
        },
        "human_data_boundary": {
            "human_respondents_projected": False,
            "occupational_centroids_projected": False,
            "human_outcomes_predicted": False,
            "respondent_level_human_microdata_loaded": False,
            "respondent_level_human_microdata_committed": False,
            "human_evidence_use": "AA-1 support labels freeze/select constructs only",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--control-draws", type=int, default=500)
    parser.add_argument("--alignment-permutations", type=int, default=1000)
    parser.add_argument("--n-jobs", type=int, default=4)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if args.control_draws < 500 or args.alignment_permutations < 1000:
        raise ValueError("Preregistered minima are 500 control banks and 1000 alignment permutations")

    print("loading and verifying canonical sources", flush=True)
    models, support, frozen_traits, direct_traits, vector_root, source_checks = load_sources()
    fixed_splits = kfold_splits(275, 42)
    summaries: list[dict[str, Any]] = []
    per_pc_rows: list[dict[str, Any]] = []
    optimized_path_rows: list[dict[str, Any]] = []
    aa4 = import_module(
        REPO / "research/outputs/qwen_trait_sparsity_prediction/run_qwen_trait_sparsity.py", "aa7_aa4_runner"
    )

    print("phase 1: fixed families, LOPO, and role-family holdout", flush=True)
    for model in models.values():
        families = {
            "human_supported_12": model.trait_scores[:, [model.traits.index(x) for x in frozen_traits]],
            "externally_anchored_big_five_5": model.big_five,
            "direct_semantic_45": model.trait_scores[:, [model.traits.index(x) for x in direct_traits]],
            "full_real_traits_240": model.trait_scores,
        }
        for family, features in families.items():
            results = evaluate_scopes(features, model.pc_scores, fixed_splits)
            add_evaluation_records(summaries, per_pc_rows, model, family, features.shape[1], "fixed_5fold_seed42", results)
        lopo = evaluate_scopes(families["human_supported_12"], model.pc_scores, lopo_splits(275))
        add_evaluation_records(summaries, per_pc_rows, model, "human_supported_12", 12, "leave_one_persona_out", lopo)
        for family, features in families.items():
            result = evaluate_scopes(features, model.pc_scores, family_splits(model.clusters))
            add_evaluation_records(
                summaries, per_pc_rows, model, family, features.shape[1], "qwen_canonical_role_family_holdout", result
            )
        paths, optimized = optimized_nested(model, aa4, fixed_splits)
        optimized_path_rows.extend(paths)
        for (scope, budget), result in optimized.items():
            add_evaluation_records(
                summaries,
                per_pc_rows,
                model,
                f"geometry_optimized_real_traits_{budget}",
                budget,
                "fixed_5fold_seed42",
                {scope: result},
            )

    summaries_frame = pd.DataFrame(summaries)
    per_pc_frame = pd.DataFrame(per_pc_rows)
    optimized_paths = pd.DataFrame(optimized_path_rows)
    write_csv(out / "local_pc_prediction_summary.csv", summaries_frame)
    write_csv(out / "local_pc_prediction_per_pc.csv", per_pc_frame)
    write_csv(
        out / "role_family_holdout_summary.csv",
        summaries_frame[summaries_frame.protocol == "qwen_canonical_role_family_holdout"].reset_index(drop=True),
    )
    write_csv(out / "geometry_optimized_k12_selections.csv", optimized_paths)

    print("phase 1: 500-bank matched controls", flush=True)
    random_real, persona_span, isotropic, sampler_audit = evaluate_controls(
        models, fixed_splits, args.control_draws, args.n_jobs
    )
    write_csv(out / "random_real_k12_distribution.csv", random_real)
    write_csv(out / "persona_span_k12_distribution.csv", persona_span)
    write_csv(out / "isotropic_k12_distribution.csv", isotropic)

    print("phase 1: associations and contribution diagnostics", flush=True)
    score_table = trait_scores_table(models, frozen_traits)
    associations, redundancy, utility = association_tables(models, support, frozen_traits, direct_traits)
    contributions = contribution_table(models, frozen_traits, fixed_splits)
    comparator, budget_context = control_comparisons(summaries_frame, random_real, persona_span, isotropic)
    coverage = subspace_coverage(models, summaries_frame, optimized_paths, frozen_traits, direct_traits)
    write_csv(out / "human_supported_trait_scores.csv", score_table)
    write_csv(out / "human_supported_trait_pc_associations.csv", associations)
    write_csv(out / "human_supported_trait_redundancy.csv", redundancy)
    write_csv(out / "human_supported_trait_contributions.csv", contributions)
    write_csv(out / "human_support_vs_geometric_utility.csv", utility)
    write_csv(out / "comparator_summary.csv", comparator)
    write_csv(out / "feature_budget_context.csv", budget_context)
    write_csv(out / "feature_family_subspace_coverage.csv", coverage)

    print("phase 2: cross-validated Procrustes alignment and null", flush=True)
    full_alignments, alignment_cv, alignment_null, alignment_residuals = alignment_analyses(
        models, args.alignment_permutations
    )
    write_json(out / "procrustes_alignment_matrices.json", full_alignments)
    write_csv(out / "procrustes_alignment_cv.csv", alignment_cv)
    write_csv(out / "procrustes_alignment_null.csv", alignment_null)
    write_csv(out / "procrustes_role_residuals.csv", alignment_residuals)

    print("phase 2: aligned human-supported and Big Five directions", flush=True)
    human_dirs, bigfive_dirs, consensus, agree, directions = aligned_directions(
        models, full_alignments, frozen_traits
    )
    core_extended = core_vs_extended(alignment_cv, directions)
    write_csv(out / "aligned_human_supported_trait_directions.csv", human_dirs)
    write_csv(out / "aligned_big_five_directions.csv", bigfive_dirs)
    write_json(out / "aligned_agreeableness_focal_test.json", agree)
    write_csv(out / "aligned_trait_consensus_summary.csv", consensus)
    write_csv(out / "core_vs_extended_alignment.csv", core_extended)

    decisions = evidence_decisions(comparator, alignment_null, consensus)
    write_json(out / "primary_decisions.json", decisions)
    make_figures(
        out, comparator, per_pc_frame, associations, human_dirs, bigfive_dirs, agree, coverage,
        random_real, persona_span, isotropic,
    )
    write_report(
        out, comparator, associations, utility, alignment_cv, alignment_null, human_dirs,
        bigfive_dirs, agree, core_extended, coverage, decisions,
    )
    write_json(
        out / "source_manifest.json",
        source_manifest(vector_root, source_checks, sampler_audit, args.control_draws, args.alignment_permutations),
    )
    print(json.dumps(decisions, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
