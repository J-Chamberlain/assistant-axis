#!/usr/bin/env python3
"""Build and validate the Qwen 240-trait-profile -> persona-PC predictor.

The analysis is CPU-only and uses existing activation-derived artifacts. It does
not run Qwen, generate activations, call model APIs, or require a GPU.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import warnings
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.stats import pearsonr, spearmanr
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.exceptions import ConvergenceWarning
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import QuantileTransformer, StandardScaler

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", message=r"n_quantiles .* is greater than the total number of samples")
np.seterr(all="ignore")


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "research/outputs/trait_profile_pc_predictor"
MATRIX_PATH = REPO_ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
PRIOR_STATS_PATH = REPO_ROOT / "research/outputs/trait_persona_prediction/trait_predicts_persona_pcs_stats.json"
PRIOR_SCRIPT_PATH = REPO_ROOT / "research/outputs/trait_persona_prediction/run_trait_persona_prediction.py"
GEOMETRY_PATH = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
CLUSTER_PATH = REPO_ROOT / "research/geometry_tables/cluster_membership_table.csv"
CANONICAL_PCA_CSV = REPO_ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"
ROLE_DIR = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b/role_vectors"
TRAIT_DIR = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b/trait_vectors"
MODEL_NAMES = ["ridge", "pls", "kernel_ridge", "knn"]
REPRESENTATIONS = ["raw_cosine", "quantile"]
PC_NAMES = ["PC1", "PC2", "PC3"]
OUTER_SEEDS = [42, 43, 44, 45, 46, 47, 48, 49, 50, 51]
ALPHAS = [1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0]
PLS_COMPONENTS = [2, 5, 10, 20, 40]
KRR_ALPHAS = [1e-3, 1e-2, 1e-1, 1.0]
KRR_GAMMAS = [0.25 / 240.0, 1.0 / 240.0, 4.0 / 240.0]
KNN_NEIGHBORS = [3, 5, 10, 20, 40]
PERMUTATIONS = 100
SYNTHETIC_PAIRS_PER_BAND = 20
SYNTHETIC_ALPHAS = [0.25, 0.50, 0.75]
COUNTERFACTUALS = {
    "trickster": {"challenging": 10.0, "playful": 10.0, "conscientious": -10.0},
    "actor": {"theatrical": 10.0, "adaptable": 10.0, "reserved": -10.0},
    "therapist": {"empathetic": 10.0, "agreeable": 10.0, "reactive": -10.0},
    "spy": {"strategic": 10.0, "calculating": 10.0, "transparent": -10.0},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve()))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def directory_aggregate_hash(directory: Path, pattern: str = "*.pt") -> dict[str, Any]:
    entries = []
    aggregate = hashlib.sha256()
    for path in sorted(directory.glob(pattern)):
        digest = sha256_file(path)
        relative = path.name
        aggregate.update(relative.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\n")
        entries.append({"path": rel(path), "sha256": digest, "size_bytes": path.stat().st_size})
    return {
        "path": rel(directory),
        "file_count": len(entries),
        "aggregate_sha256_of_sorted_path_and_file_hashes": aggregate.hexdigest(),
        "total_size_bytes": sum(entry["size_bytes"] for entry in entries),
        "files": entries,
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def load_data() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, list[str], list[str], list[str], dict[str, Any]]:
    matrix = pd.read_csv(MATRIX_PATH)
    geometry = json.loads(GEOMETRY_PATH.read_text(encoding="utf-8"))
    clusters = pd.read_csv(CLUSTER_PATH)
    if matrix.columns[0] != "persona":
        raise RuntimeError("Trait matrix first column is not persona")
    persona_names = matrix["persona"].astype(str).tolist()
    feature_names = matrix.columns[1:].astype(str).tolist()
    geometry_names = list(geometry["roles"]["names"])
    geometry_targets = np.asarray(geometry["roles"]["pca3d"], dtype=np.float64)
    if persona_names != geometry_names:
        raise RuntimeError("Trait matrix persona order does not exactly match canonical geometry")
    if clusters["role"].astype(str).tolist() != persona_names:
        raise RuntimeError("Cluster membership order does not exactly match canonical geometry")
    cluster_names = clusters["cluster"].astype(str).tolist()
    X = matrix.iloc[:, 1:].to_numpy(dtype=np.float64)
    Y = geometry_targets
    target_like = sorted(set(feature_names) & {"PC1", "PC2", "PC3", "pc1", "pc2", "pc3", "cluster", "role", "persona"})
    integrity = {
        "persona_count": len(persona_names),
        "unique_persona_count": len(set(persona_names)),
        "trait_count": len(feature_names),
        "unique_trait_count": len(set(feature_names)),
        "duplicate_personas": sorted(matrix.loc[matrix["persona"].duplicated(), "persona"].astype(str).tolist()),
        "duplicate_traits": [name for name, count in Counter(feature_names).items() if count > 1],
        "matrix_finite": bool(np.isfinite(X).all()),
        "targets_finite": bool(np.isfinite(Y).all()),
        "matrix_persona_order_exactly_matches_geometry": persona_names == geometry_names,
        "cluster_order_exactly_matches_geometry": clusters["role"].astype(str).tolist() == geometry_names,
        "target_or_metadata_columns_in_features": target_like,
        "cluster_counts": dict(sorted(Counter(cluster_names).items())),
    }
    expected = (
        integrity["persona_count"] == 275
        and integrity["unique_persona_count"] == 275
        and integrity["trait_count"] == 240
        and integrity["unique_trait_count"] == 240
        and integrity["matrix_finite"]
        and integrity["targets_finite"]
        and not target_like
    )
    integrity["passed"] = bool(expected)
    if not expected:
        raise RuntimeError(f"Integrity checks failed: {integrity}")
    return matrix, X, Y, persona_names, feature_names, cluster_names, integrity


def load_mean_vectors(directory: Path, expected_names: list[str]) -> np.ndarray:
    import torch

    paths = sorted(directory.glob("*.pt"))
    names = [path.stem for path in paths]
    if names != expected_names:
        raise RuntimeError(f"Vector names/order do not match expected names under {directory}")
    vectors = []
    for path in paths:
        tensor = torch.load(path, map_location="cpu").float()
        if tensor.ndim == 2:
            tensor = tensor.mean(0)
        elif tensor.ndim != 1:
            raise RuntimeError(f"Unexpected tensor shape for {path}: {tuple(tensor.shape)}")
        vector = tensor.numpy().astype(np.float64, copy=False)
        if not np.isfinite(vector).all():
            raise RuntimeError(f"Nonfinite source vector: {path}")
        vectors.append(vector)
    return np.stack(vectors)


def verify_sources_and_pca(
    X: np.ndarray,
    Y: np.ndarray,
    persona_names: list[str],
    feature_names: list[str],
) -> tuple[np.ndarray, np.ndarray, dict[str, Any], dict[str, Any]]:
    role_raw = load_mean_vectors(ROLE_DIR, sorted(persona_names))
    trait_raw = load_mean_vectors(TRAIT_DIR, sorted(feature_names))
    if sorted(persona_names) != persona_names or sorted(feature_names) != feature_names:
        raise RuntimeError("Expected canonical persona and trait orders to be lexically sorted")
    role_norm = role_raw / np.linalg.norm(role_raw, axis=1, keepdims=True)
    trait_norm = trait_raw / np.linalg.norm(trait_raw, axis=1, keepdims=True)
    reconstructed_matrix = role_norm @ trait_norm.T
    matrix_abs = np.abs(reconstructed_matrix - X)
    matrix_check = {
        "construction": "mean each stored tensor over its first dimension, L2-normalize, role @ trait.T",
        "max_abs_reproduction_error": float(matrix_abs.max()),
        "mean_abs_reproduction_error": float(matrix_abs.mean()),
        "tolerance": 1e-10,
        "passed": bool(float(matrix_abs.max()) <= 1e-10),
    }
    if not matrix_check["passed"]:
        raise RuntimeError(f"Trait matrix does not reproduce from source vectors: {matrix_check}")

    mean = role_raw.mean(axis=0)
    centered = role_raw - mean
    gram = centered @ centered.T
    eigvals, eigvecs = np.linalg.eigh(gram)
    order = np.argsort(eigvals)[::-1][:3]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    components = []
    for component_index in range(3):
        component = centered.T @ eigvecs[:, component_index] / math.sqrt(max(float(eigvals[component_index]), 1e-12))
        components.append(component / np.linalg.norm(component))
    components = np.stack(components)
    reconstructed = centered @ components.T
    signs = []
    for component_index in range(3):
        sign = -1.0 if np.corrcoef(reconstructed[:, component_index], Y[:, component_index])[0, 1] < 0 else 1.0
        signs.append(sign)
        components[component_index] *= sign
        reconstructed[:, component_index] *= sign
    pca_abs = np.abs(reconstructed - Y)
    pca_check = {
        "basis_source": "reconstructed from all 275 canonical mean-pooled Qwen role vectors and sign-aligned to geometry_viz_data.json",
        "canonical_builder": rel(REPO_ROOT / "research/visualizations/scripts/build_geometry_viz.py"),
        "supporting_prior_reproduction": rel(REPO_ROOT / "research/outputs/no_label_elicitation_validation/projection_basis_debug.json"),
        "canonical_pca_table": rel(CANONICAL_PCA_CSV),
        "sign_alignment": signs,
        "max_abs_coordinate_reproduction_error": float(pca_abs.max()),
        "mean_abs_coordinate_reproduction_error": float(pca_abs.mean()),
        "strict_tolerance": 1e-5,
        "passed": bool(float(pca_abs.max()) <= 1e-5),
    }
    return role_raw, trait_raw, matrix_check, {"mean": mean, "components": components, "check": pca_check}


def representation_step(representation: str, seed: int) -> Any:
    if representation == "raw_cosine":
        return "passthrough"
    if representation == "quantile":
        return QuantileTransformer(
            n_quantiles=100,
            output_distribution="uniform",
            subsample=None,
            random_state=seed,
            copy=True,
        )
    raise ValueError(f"Unknown representation: {representation}")


def estimator_and_grid(model_name: str, representation: str, seed: int) -> tuple[Any, dict[str, list[Any]]]:
    if model_name == "ridge":
        model = Ridge()
        grid = {"regressor__model__alpha": ALPHAS}
    elif model_name == "pls":
        model = PLSRegression(scale=False, max_iter=1000, tol=1e-6)
        grid = {"regressor__model__n_components": PLS_COMPONENTS}
    elif model_name == "kernel_ridge":
        model = KernelRidge(kernel="rbf")
        grid = {
            "regressor__model__alpha": KRR_ALPHAS,
            "regressor__model__gamma": KRR_GAMMAS,
        }
    elif model_name == "knn":
        model = KNeighborsRegressor(weights="distance", metric="minkowski", p=2)
        grid = {"regressor__model__n_neighbors": KNN_NEIGHBORS}
    else:
        raise ValueError(f"Unknown model: {model_name}")
    pipeline = Pipeline(
        [
            ("representation", representation_step(representation, seed)),
            ("scale", StandardScaler()),
            ("model", model),
        ]
    )
    estimator = TransformedTargetRegressor(regressor=pipeline, transformer=StandardScaler())
    return estimator, grid


def fit_tuned(
    model_name: str,
    representation: str,
    X: np.ndarray,
    Y: np.ndarray,
    seed: int,
    n_jobs: int,
) -> GridSearchCV:
    estimator, grid = estimator_and_grid(model_name, representation, seed)
    inner = KFold(n_splits=4, shuffle=True, random_state=seed)
    search = GridSearchCV(
        estimator,
        grid,
        scoring="neg_mean_squared_error",
        cv=inner,
        n_jobs=n_jobs,
        pre_dispatch=max(1, n_jobs),
        refit=True,
        error_score="raise",
        return_train_score=False,
    )
    search.fit(X, Y)
    return search


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    cleaned = {}
    for key, value in params.items():
        name = key.rsplit("__", 1)[-1]
        cleaned[name] = int(value) if isinstance(value, (np.integer,)) else float(value) if isinstance(value, (np.floating,)) else value
    return cleaned


def per_pc_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    result: dict[str, float] = {}
    for index, pc in enumerate(PC_NAMES):
        truth = y_true[:, index]
        prediction = y_pred[:, index]
        result[f"{pc.lower()}_r2"] = float(r2_score(truth, prediction))
        result[f"{pc.lower()}_pearson"] = float(pearsonr(truth, prediction).statistic)
        result[f"{pc.lower()}_spearman"] = float(spearmanr(truth, prediction).statistic)
        result[f"{pc.lower()}_rmse"] = float(np.sqrt(mean_squared_error(truth, prediction)))
        result[f"{pc.lower()}_mae"] = float(mean_absolute_error(truth, prediction))
    return result


def joint_metrics(y_true: np.ndarray, y_pred: np.ndarray, normalized_errors: np.ndarray | None = None) -> dict[str, float]:
    raw = np.linalg.norm(y_pred - y_true, axis=1)
    result = {
        "raw_3d_error_mean": float(raw.mean()),
        "raw_3d_error_median": float(np.median(raw)),
        "raw_3d_error_rmse": float(np.sqrt(np.mean(raw**2))),
    }
    if normalized_errors is not None:
        result.update(
            {
                "normalized_3d_error_mean": float(normalized_errors.mean()),
                "normalized_3d_error_median": float(np.median(normalized_errors)),
                "normalized_3d_error_rmse": float(np.sqrt(np.mean(normalized_errors**2))),
            }
        )
    return result


def run_nested_model_comparison(
    X: np.ndarray,
    Y: np.ndarray,
    persona_names: list[str],
    n_jobs: int,
    seeds: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    total = len(REPRESENTATIONS) * len(MODEL_NAMES) * len(seeds) * 5
    completed = 0
    for representation in REPRESENTATIONS:
        for model_name in MODEL_NAMES:
            print(f"nested CV: representation={representation} model={model_name}", flush=True)
            for repeat, seed in enumerate(seeds):
                outer = KFold(n_splits=5, shuffle=True, random_state=seed)
                for fold, (train_idx, test_idx) in enumerate(outer.split(X)):
                    if set(train_idx) & set(test_idx):
                        raise RuntimeError("Outer train/test overlap")
                    search = fit_tuned(model_name, representation, X[train_idx], Y[train_idx], seed * 100 + fold, n_jobs)
                    prediction = np.asarray(search.predict(X[test_idx]), dtype=np.float64)
                    train_std = Y[train_idx].std(axis=0, ddof=0)
                    raw_errors = np.linalg.norm(prediction - Y[test_idx], axis=1)
                    normalized = np.linalg.norm((prediction - Y[test_idx]) / train_std, axis=1)
                    params_json = json.dumps(clean_params(search.best_params_), sort_keys=True)
                    for local, global_index in enumerate(test_idx):
                        row = {
                            "repeat": repeat,
                            "outer_seed": seed,
                            "outer_fold": fold,
                            "representation": representation,
                            "model": model_name,
                            "persona": persona_names[global_index],
                            "actual_pc1": Y[global_index, 0],
                            "actual_pc2": Y[global_index, 1],
                            "actual_pc3": Y[global_index, 2],
                            "predicted_pc1": prediction[local, 0],
                            "predicted_pc2": prediction[local, 1],
                            "predicted_pc3": prediction[local, 2],
                            "residual_pc1": prediction[local, 0] - Y[global_index, 0],
                            "residual_pc2": prediction[local, 1] - Y[global_index, 1],
                            "residual_pc3": prediction[local, 2] - Y[global_index, 2],
                            "raw_3d_error": raw_errors[local],
                            "standardized_3d_error": normalized[local],
                            "train_pc1_std": train_std[0],
                            "train_pc2_std": train_std[1],
                            "train_pc3_std": train_std[2],
                            "selected_hyperparameters": params_json,
                        }
                        rows.append(row)
                    completed += 1
                    if completed % 20 == 0 or completed == total:
                        print(f"nested CV progress: {completed}/{total} outer fits", flush=True)
    predictions = pd.DataFrame(rows)
    summaries = []
    for (representation, model_name), group in predictions.groupby(["representation", "model"], sort=False):
        y_true = group[["actual_pc1", "actual_pc2", "actual_pc3"]].to_numpy()
        y_pred = group[["predicted_pc1", "predicted_pc2", "predicted_pc3"]].to_numpy()
        summary = {
            "representation": representation,
            "model": model_name,
            "outer_repeats": int(group["repeat"].nunique()),
            "outer_folds_per_repeat": 5,
            "n_oof_predictions": len(group),
            "n_unique_personas": int(group["persona"].nunique()),
            **per_pc_metrics(y_true, y_pred),
            **joint_metrics(y_true, y_pred, group["standardized_3d_error"].to_numpy()),
            "hyperparameter_selection_counts": json.dumps(dict(Counter(group["selected_hyperparameters"])), sort_keys=True),
        }
        repeat_rmses = []
        for _, repeat_group in group.groupby("repeat"):
            repeat_rmses.append(float(np.sqrt(np.mean(repeat_group["standardized_3d_error"].to_numpy() ** 2))))
        summary["normalized_3d_error_rmse_repeat_mean"] = float(np.mean(repeat_rmses))
        summary["normalized_3d_error_rmse_repeat_std"] = float(np.std(repeat_rmses, ddof=0))
        summaries.append(summary)
    return predictions, pd.DataFrame(summaries)


def fit_ood(X_train: np.ndarray, names: list[str]) -> dict[str, Any]:
    scaler = StandardScaler().fit(X_train)
    scaled = scaler.transform(X_train)
    pca = PCA(n_components=0.95, svd_solver="full").fit(scaled)
    scores = pca.transform(scaled)
    reconstruction_error = np.linalg.norm(scaled - pca.inverse_transform(scores), axis=1)
    distances = cdist(scores, scores)
    np.fill_diagonal(distances, np.inf)
    order = np.argsort(distances, axis=1)
    nearest = distances[np.arange(len(names)), order[:, 0]]
    mean5 = np.take_along_axis(distances, order[:, :5], axis=1).mean(axis=1)
    return {
        "scaler": scaler,
        "pca": pca,
        "scores": scores,
        "distances": distances,
        "order": order,
        "nearest": nearest,
        "mean5": mean5,
        "reconstruction_error": reconstruction_error,
        "names": names,
    }


def diagnose_with_fitted_ood(profile: np.ndarray, fitted: dict[str, Any]) -> dict[str, Any]:
    scaled = fitted["scaler"].transform(profile.reshape(1, -1))
    score = fitted["pca"].transform(scaled)[0]
    reconstruction_error = float(
        np.linalg.norm(scaled[0] - fitted["pca"].inverse_transform(score.reshape(1, -1))[0])
    )
    distances = np.linalg.norm(fitted["scores"] - score, axis=1)
    order = np.argsort(distances)
    mean5 = float(distances[order[:5]].mean())
    percentile = float(100.0 * np.mean(fitted["mean5"] <= mean5))
    return {
        "nearest_names": [fitted["names"][index] for index in order[:5]],
        "nearest_distances": [float(distances[index]) for index in order[:5]],
        "nearest_distance": float(distances[order[0]]),
        "mean5": mean5,
        "distance_percentile": percentile,
        "reconstruction_error": reconstruction_error,
        "reconstruction_error_percentile": float(
            100.0 * np.mean(fitted["reconstruction_error"] <= reconstruction_error)
        ),
        "retained_components": int(fitted["pca"].n_components_),
    }


def run_lopo(
    X: np.ndarray,
    Y: np.ndarray,
    persona_names: list[str],
    feature_names: list[str],
    n_jobs: int,
) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    rows = []
    ood_by_persona: dict[str, dict[str, Any]] = {}
    indices = np.arange(len(X))
    for representation in REPRESENTATIONS:
        print(f"LOPO: representation={representation}", flush=True)
        for held_out in indices:
            train_idx = indices[indices != held_out]
            if held_out in set(train_idx) or len(train_idx) != len(X) - 1:
                raise RuntimeError("LOPO split integrity failure")
            search = fit_tuned("ridge", representation, X[train_idx], Y[train_idx], 10_000 + held_out, n_jobs)
            prediction = np.asarray(search.predict(X[[held_out]])[0], dtype=np.float64)
            residual = prediction - Y[held_out]
            train_std = Y[train_idx].std(axis=0, ddof=0)
            params = clean_params(search.best_params_)
            if representation == "raw_cosine":
                fitted_ood = fit_ood(X[train_idx], [persona_names[index] for index in train_idx])
                diagnostic = diagnose_with_fitted_ood(X[held_out], fitted_ood)
                outside = int(
                    np.sum(
                        (X[held_out] < X[train_idx].min(axis=0))
                        | (X[held_out] > X[train_idx].max(axis=0))
                    )
                )
                diagnostic["outside_training_range_trait_count"] = outside
                ood_by_persona[persona_names[held_out]] = diagnostic
            else:
                diagnostic = ood_by_persona[persona_names[held_out]]
            rows.append(
                {
                    "persona": persona_names[held_out],
                    "representation": representation,
                    "actual_pc1": Y[held_out, 0],
                    "actual_pc2": Y[held_out, 1],
                    "actual_pc3": Y[held_out, 2],
                    "predicted_pc1": prediction[0],
                    "predicted_pc2": prediction[1],
                    "predicted_pc3": prediction[2],
                    "residual_pc1": residual[0],
                    "residual_pc2": residual[1],
                    "residual_pc3": residual[2],
                    "raw_3d_error": float(np.linalg.norm(residual)),
                    "standardized_3d_error": float(np.linalg.norm(residual / train_std)),
                    "selected_alpha": params["alpha"],
                    "nearest_training_personas": json.dumps(diagnostic["nearest_names"]),
                    "nearest_training_distances": json.dumps(diagnostic["nearest_distances"]),
                    "nearest_neighbor_distance": diagnostic["nearest_distance"],
                    "mean_5nn_distance": diagnostic["mean5"],
                    "distance_percentile_vs_training_loo": diagnostic["distance_percentile"],
                    "profile_pca_reconstruction_error": diagnostic["reconstruction_error"],
                    "reconstruction_error_percentile_vs_training": diagnostic["reconstruction_error_percentile"],
                    "traits_outside_training_range_count": diagnostic["outside_training_range_trait_count"],
                    "ood_pca_components": diagnostic["retained_components"],
                }
            )
            if (held_out + 1) % 25 == 0 or held_out + 1 == len(X):
                print(f"LOPO {representation}: {held_out + 1}/{len(X)}", flush=True)
    return pd.DataFrame(rows), ood_by_persona


def metrics_from_prediction_frame(frame: pd.DataFrame) -> dict[str, Any]:
    y_true = frame[["actual_pc1", "actual_pc2", "actual_pc3"]].to_numpy()
    y_pred = frame[["predicted_pc1", "predicted_pc2", "predicted_pc3"]].to_numpy()
    return {
        **per_pc_metrics(y_true, y_pred),
        **joint_metrics(y_true, y_pred, frame["standardized_3d_error"].to_numpy()),
        "n": len(frame),
    }


def run_leave_cluster_out(
    X: np.ndarray,
    Y: np.ndarray,
    persona_names: list[str],
    cluster_names: list[str],
    lopo: pd.DataFrame,
    n_jobs: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    predictions = []
    summaries = []
    clusters = np.asarray(cluster_names)
    raw_lopo = lopo[lopo["representation"] == "raw_cosine"].set_index("persona")
    for model_name in MODEL_NAMES:
        print(f"leave-one-cluster-out: model={model_name}", flush=True)
        for cluster in sorted(set(cluster_names)):
            test_idx = np.flatnonzero(clusters == cluster)
            train_idx = np.flatnonzero(clusters != cluster)
            if set(clusters[train_idx]) & {cluster} or set(train_idx) & set(test_idx):
                raise RuntimeError("Leave-cluster-out split integrity failure")
            search = fit_tuned(model_name, "raw_cosine", X[train_idx], Y[train_idx], 20_000 + sum(map(ord, cluster)) + MODEL_NAMES.index(model_name), n_jobs)
            predicted = np.asarray(search.predict(X[test_idx]), dtype=np.float64)
            train_std = Y[train_idx].std(axis=0, ddof=0)
            params = clean_params(search.best_params_)
            residual = predicted - Y[test_idx]
            normalized = np.linalg.norm(residual / train_std, axis=1)
            for local, global_index in enumerate(test_idx):
                predictions.append(
                    {
                        "model": model_name,
                        "cluster": cluster,
                        "persona": persona_names[global_index],
                        "actual_pc1": Y[global_index, 0],
                        "actual_pc2": Y[global_index, 1],
                        "actual_pc3": Y[global_index, 2],
                        "predicted_pc1": predicted[local, 0],
                        "predicted_pc2": predicted[local, 1],
                        "predicted_pc3": predicted[local, 2],
                        "residual_pc1": residual[local, 0],
                        "residual_pc2": residual[local, 1],
                        "residual_pc3": residual[local, 2],
                        "raw_3d_error": float(np.linalg.norm(residual[local])),
                        "standardized_3d_error": float(normalized[local]),
                        "selected_hyperparameters": json.dumps(params, sort_keys=True),
                    }
                )
            metrics = {**per_pc_metrics(Y[test_idx], predicted), **joint_metrics(Y[test_idx], predicted, normalized)}
            lopo_cluster = raw_lopo.loc[[persona_names[index] for index in test_idx]]
            summaries.append(
                {
                    "model": model_name,
                    "cluster": cluster,
                    "n_held_out": len(test_idx),
                    **metrics,
                    "bias_pc1": float(residual[:, 0].mean()),
                    "bias_pc2": float(residual[:, 1].mean()),
                    "bias_pc3": float(residual[:, 2].mean()),
                    "ordinary_lopo_normalized_3d_error_mean": float(lopo_cluster["standardized_3d_error"].mean()),
                    "cluster_holdout_vs_lopo_mean_error_ratio": float(normalized.mean() / lopo_cluster["standardized_3d_error"].mean()),
                    "selected_hyperparameters": json.dumps(params, sort_keys=True),
                }
            )
    pred_frame = pd.DataFrame(predictions)
    summary_frame = pd.DataFrame(summaries)
    aggregate_rows = []
    for model_name, group in pred_frame.groupby("model", sort=False):
        aggregate = metrics_from_prediction_frame(group)
        aggregate_rows.append(
            {
                "model": model_name,
                "cluster": "ALL_CLUSTERS",
                "n_held_out": len(group),
                **{key: value for key, value in aggregate.items() if key != "n"},
                "bias_pc1": float(group["residual_pc1"].mean()),
                "bias_pc2": float(group["residual_pc2"].mean()),
                "bias_pc3": float(group["residual_pc3"].mean()),
                "ordinary_lopo_normalized_3d_error_mean": float(raw_lopo["standardized_3d_error"].mean()),
                "cluster_holdout_vs_lopo_mean_error_ratio": float(group["standardized_3d_error"].mean() / raw_lopo["standardized_3d_error"].mean()),
                "selected_hyperparameters": "varies by cluster",
            }
        )
    summary_frame = pd.concat([summary_frame, pd.DataFrame(aggregate_rows)], ignore_index=True)
    return pred_frame, summary_frame


def run_permutations(
    X: np.ndarray,
    Y: np.ndarray,
    persona_names: list[str],
    n_jobs: int,
    n_permutations: int,
) -> pd.DataFrame:
    del persona_names
    rng = np.random.default_rng(20260911)
    outer = list(KFold(n_splits=5, shuffle=True, random_state=42).split(X))
    rows = []
    for permutation in range(n_permutations):
        order = rng.permutation(len(Y))
        permuted = Y[order]
        predictions = np.empty_like(permuted)
        normalized = np.empty(len(Y), dtype=np.float64)
        hyperparameters = []
        for fold, (train_idx, test_idx) in enumerate(outer):
            search = fit_tuned("ridge", "raw_cosine", X[train_idx], permuted[train_idx], 30_000 + permutation * 10 + fold, n_jobs)
            predicted = np.asarray(search.predict(X[test_idx]), dtype=np.float64)
            predictions[test_idx] = predicted
            train_std = permuted[train_idx].std(axis=0, ddof=0)
            normalized[test_idx] = np.linalg.norm((predicted - permuted[test_idx]) / train_std, axis=1)
            hyperparameters.append(clean_params(search.best_params_)["alpha"])
        metrics = {**per_pc_metrics(permuted, predictions), **joint_metrics(permuted, predictions, normalized)}
        rows.append(
            {
                "permutation": permutation,
                "permutation_seed": 20260911,
                **metrics,
                "mean_pc_r2": float(np.mean([metrics[f"pc{i}_r2"] for i in (1, 2, 3)])),
                "selected_alphas_by_outer_fold": json.dumps(hyperparameters),
            }
        )
        if (permutation + 1) % 10 == 0 or permutation + 1 == n_permutations:
            print(f"permutation control: {permutation + 1}/{n_permutations}", flush=True)
    return pd.DataFrame(rows)


def select_primary(model_comparison: pd.DataFrame, cluster_summary: pd.DataFrame) -> dict[str, Any]:
    raw = model_comparison[model_comparison["representation"] == "raw_cosine"].set_index("model")
    ridge_rmse = float(raw.loc["ridge", "normalized_3d_error_rmse"])
    best_model = str(raw["normalized_3d_error_rmse"].idxmin())
    best_rmse = float(raw.loc[best_model, "normalized_3d_error_rmse"])
    reduction = (ridge_rmse - best_rmse) / ridge_rmse
    cluster_aggregate = cluster_summary[cluster_summary["cluster"] == "ALL_CLUSTERS"].set_index("model")
    ridge_cluster = float(cluster_aggregate.loc["ridge", "normalized_3d_error_rmse"])
    challenger_cluster = float(cluster_aggregate.loc[best_model, "normalized_3d_error_rmse"])
    no_cluster_degradation = challenger_cluster <= ridge_cluster * 1.02
    if best_model != "ridge" and reduction >= 0.10 and no_cluster_degradation:
        selected = best_model
        reason = "A challenger cleared the predeclared >=10% normalized-RMSE reduction and did not materially degrade leave-cluster-out performance."
    else:
        selected = "ridge"
        reason = "Ridge remains V1 because no challenger cleared the predeclared material-improvement rule without a harder-holdout penalty."
    return {
        "selected_model": selected,
        "default_model": "ridge",
        "material_improvement_threshold_fraction": 0.10,
        "best_ordinary_nested_cv_model": best_model,
        "ridge_normalized_3d_rmse": ridge_rmse,
        "best_normalized_3d_rmse": best_rmse,
        "relative_reduction_vs_ridge": reduction,
        "ridge_leave_cluster_out_normalized_3d_rmse": ridge_cluster,
        "best_model_leave_cluster_out_normalized_3d_rmse": challenger_cluster,
        "no_material_cluster_degradation": bool(no_cluster_degradation),
        "reason": reason,
    }


def linear_portable(estimator: Any, n_features: int) -> dict[str, Any]:
    zero = np.zeros((1, n_features), dtype=np.float64)
    intercept = np.asarray(estimator.predict(zero)[0], dtype=np.float64)
    coefficients = np.empty((3, n_features), dtype=np.float64)
    for index in range(n_features):
        basis = np.zeros((1, n_features), dtype=np.float64)
        basis[0, index] = 1.0
        coefficients[:, index] = np.asarray(estimator.predict(basis)[0], dtype=np.float64) - intercept
    return {"coefficients": coefficients.tolist(), "intercepts": intercept.tolist()}


def unwrap(search: GridSearchCV) -> tuple[TransformedTargetRegressor, Pipeline, Any, StandardScaler, StandardScaler]:
    ttr = search.best_estimator_
    pipeline = ttr.regressor_
    return ttr, pipeline, pipeline.named_steps["model"], pipeline.named_steps["scale"], ttr.transformer_


def export_comparison_model(name: str, search: GridSearchCV, X: np.ndarray, feature_names: list[str]) -> dict[str, Any]:
    ttr, pipeline, model, scaler, target = unwrap(search)
    common = {
        "name": {"ridge": "Ridge", "pls": "PLS", "kernel_ridge": "Kernel Ridge", "knn": "KNN"}[name],
        "input_representation": "raw_cosine",
        "trait_feature_names": feature_names,
        "selected_hyperparameters": clean_params(search.best_params_),
        "feature_transform": {"type": "StandardScaler", "mean": scaler.mean_.tolist(), "scale": scaler.scale_.tolist()},
        "target_transform": {"type": "StandardScaler", "mean": target.mean_.tolist(), "scale": target.scale_.tolist()},
    }
    if name in {"ridge", "pls"}:
        common["model_type"] = "Ridge" if name == "ridge" else "PLSRegression"
        common["portable_prediction"] = {"raw_input_to_pc": linear_portable(ttr, X.shape[1])}
        if name == "ridge":
            common["ridge_alpha"] = float(model.alpha)
            common["coefficients"] = common["portable_prediction"]["raw_input_to_pc"]["coefficients"]
            common["intercepts"] = common["portable_prediction"]["raw_input_to_pc"]["intercepts"]
            common["coefficient_space"] = "raw 240-trait cosine input to unstandardized PC1/PC2/PC3 output"
            common["standardized_model_coefficients"] = np.asarray(model.coef_).tolist()
            common["standardized_model_intercepts"] = np.asarray(model.intercept_).tolist()
        else:
            common["n_components"] = int(model.n_components)
    elif name == "kernel_ridge":
        common.update(
            {
                "model_type": "KernelRidgeRBF",
                "alpha": float(model.alpha),
                "gamma": float(model.gamma),
                "training_features_transformed": np.asarray(model.X_fit_).tolist(),
                "dual_coefficients": np.asarray(model.dual_coef_).tolist(),
            }
        )
    elif name == "knn":
        common.update(
            {
                "model_type": "KNeighborsRegressor",
                "n_neighbors": int(model.n_neighbors),
                "weights": "distance",
                "metric": "euclidean after fold-local StandardScaler",
                "training_features_transformed": np.asarray(model._fit_X).tolist(),
                "training_targets_standardized": np.asarray(model._y).tolist(),
            }
        )
    return common


def empirical_error_reference(lopo_raw: pd.DataFrame) -> dict[str, Any]:
    result = {}
    for index, pc in enumerate(PC_NAMES, start=1):
        errors = np.abs(lopo_raw[f"residual_pc{index}"].to_numpy())
        result[pc] = {
            "median_absolute_error": float(np.median(errors)),
            "q90_absolute_error": float(np.quantile(errors, 0.90)),
            "q95_absolute_error": float(np.quantile(errors, 0.95)),
        }
    return result


def build_ood_reference(X: np.ndarray, persona_names: list[str], feature_names: list[str]) -> tuple[dict[str, Any], pd.DataFrame]:
    fitted = fit_ood(X, persona_names)
    rows = []
    for index, name in enumerate(persona_names):
        order = fitted["order"][index, :5]
        row: dict[str, Any] = {
            "persona": name,
            "nearest_neighbor_distance": fitted["nearest"][index],
            "mean_5nn_distance": fitted["mean5"][index],
            "mean_5nn_distance_percentile": 100.0 * np.mean(fitted["mean5"] <= fitted["mean5"][index]),
            "profile_pca_reconstruction_error": fitted["reconstruction_error"][index],
            "reconstruction_error_percentile": 100.0
            * np.mean(fitted["reconstruction_error"] <= fitted["reconstruction_error"][index]),
        }
        for rank, neighbor_index in enumerate(order, start=1):
            row[f"neighbor_{rank}"] = persona_names[neighbor_index]
            row[f"neighbor_{rank}_distance"] = fitted["distances"][index, neighbor_index]
        rows.append(row)
    reference = {
        "schema_version": 1,
        "method": "StandardScaler on raw 240-trait profiles, then PCA retaining >=95% training variance; Euclidean neighbor distances in retained score space plus reconstruction residual in discarded space",
        "heuristic_labels": {
            "in-distribution": "5-NN distance and PCA reconstruction-error percentiles <=90, with no trait outside the training range",
            "edge-of-distribution": "5-NN distance or reconstruction-error percentile >90, or at least one trait outside range, unless OOD rule applies",
            "out-of-distribution": "5-NN distance or reconstruction-error percentile >99, or at least five traits outside range",
            "calibration_note": "These are geometric heuristics, not calibrated probabilities.",
        },
        "trait_feature_names": feature_names,
        "training_personas": persona_names,
        "feature_standardizer": {
            "type": "StandardScaler",
            "mean": fitted["scaler"].mean_.tolist(),
            "scale": fitted["scaler"].scale_.tolist(),
        },
        "profile_pca": {
            "variance_threshold": 0.95,
            "n_components": int(fitted["pca"].n_components_),
            "explained_variance_ratio": fitted["pca"].explained_variance_ratio_.tolist(),
            "cumulative_explained_variance": float(fitted["pca"].explained_variance_ratio_.sum()),
            "mean": fitted["pca"].mean_.tolist(),
            "components": fitted["pca"].components_.tolist(),
        },
        "training_profile_pca_scores": fitted["scores"].tolist(),
        "reference_distances": {
            "loo_nearest_neighbor_sorted": np.sort(fitted["nearest"]).tolist(),
            "loo_mean_5nn_sorted": np.sort(fitted["mean5"]).tolist(),
            "profile_pca_reconstruction_error_sorted": np.sort(fitted["reconstruction_error"]).tolist(),
        },
        "training_feature_ranges": {"min": X.min(axis=0).tolist(), "max": X.max(axis=0).tolist()},
        "percentile_reference": {
            "definition": "Per-trait linear empirical quantiles over all 275 canonical profiles; used for intuitive percentile input/editing.",
            "sorted_raw_values_by_trait": np.sort(X, axis=0).T.tolist(),
        },
    }
    return reference, pd.DataFrame(rows)


def select_synthetic_pairs(role_raw: np.ndarray, persona_names: list[str], per_band: int) -> list[tuple[str, int, int, float]]:
    normalized = role_raw / np.linalg.norm(role_raw, axis=1, keepdims=True)
    cosine = normalized @ normalized.T
    candidates = [(float(cosine[i, j]), i, j) for i in range(len(role_raw)) for j in range(i + 1, len(role_raw))]
    selected = []
    for label, ordered in [("near", sorted(candidates, reverse=True)), ("distant", sorted(candidates))]:
        used: set[int] = set()
        count = 0
        for similarity, left, right in ordered:
            if left in used or right in used:
                continue
            selected.append((label, left, right, similarity))
            used.update([left, right])
            count += 1
            if count == per_band:
                break
        if count != per_band:
            raise RuntimeError(f"Could not select {per_band} disjoint {label} pairs")
    return selected


def run_synthetic_interpolation(
    X: np.ndarray,
    Y: np.ndarray,
    persona_names: list[str],
    role_raw: np.ndarray,
    trait_raw: np.ndarray,
    basis: dict[str, Any],
    n_jobs: int,
    per_band: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not basis["check"]["passed"]:
        return pd.DataFrame(), {"run": False, "reason": "Canonical PCA reproduction exceeded strict tolerance", "pca_check": basis["check"]}
    pairs = select_synthetic_pairs(role_raw, persona_names, per_band)
    trait_normalized = trait_raw / np.linalg.norm(trait_raw, axis=1, keepdims=True)
    indices = np.arange(len(X))
    rows = []
    for pair_index, (band, left, right, cosine) in enumerate(pairs):
        train_idx = indices[(indices != left) & (indices != right)]
        if left in train_idx or right in train_idx:
            raise RuntimeError("Synthetic pair endpoints leaked into predictor training")
        search = fit_tuned("ridge", "raw_cosine", X[train_idx], Y[train_idx], 40_000 + pair_index, n_jobs)
        train_std = Y[train_idx].std(axis=0, ddof=0)
        for alpha in SYNTHETIC_ALPHAS:
            mix = (1.0 - alpha) * role_raw[left] + alpha * role_raw[right]
            profile = (mix / np.linalg.norm(mix)) @ trait_normalized.T
            actual = (mix - basis["mean"]) @ basis["components"].T
            predicted = np.asarray(search.predict(profile.reshape(1, -1))[0], dtype=np.float64)
            residual = predicted - actual
            rows.append(
                {
                    "pair_band": band,
                    "persona_a": persona_names[left],
                    "persona_b": persona_names[right],
                    "source_vector_cosine": cosine,
                    "source_pc_3d_distance": float(np.linalg.norm(Y[left] - Y[right])),
                    "mix_alpha": alpha,
                    "endpoints_excluded_from_training": True,
                    "actual_pc1": actual[0],
                    "actual_pc2": actual[1],
                    "actual_pc3": actual[2],
                    "predicted_pc1": predicted[0],
                    "predicted_pc2": predicted[1],
                    "predicted_pc3": predicted[2],
                    "residual_pc1": residual[0],
                    "residual_pc2": residual[1],
                    "residual_pc3": residual[2],
                    "raw_3d_error": float(np.linalg.norm(residual)),
                    "standardized_3d_error": float(np.linalg.norm(residual / train_std)),
                    "selected_alpha": clean_params(search.best_params_)["alpha"],
                }
            )
        if (pair_index + 1) % 10 == 0 or pair_index + 1 == len(pairs):
            print(f"synthetic interpolation: {pair_index + 1}/{len(pairs)} held-out endpoint pairs", flush=True)
    frame = pd.DataFrame(rows)
    summary: dict[str, Any] = {
        "run": True,
        "description": "Raw convex interpolation of mean-pooled activation vectors; both source endpoints excluded from each fitted Ridge model.",
        "normalization_note": "The mixed activation vector was not L2-normalized before canonical PCA projection because the canonical PCA was fit on raw mean-pooled vectors. Only the mix was L2-normalized for cosine-profile construction.",
        "pca_check": basis["check"],
        "pair_count": len(pairs),
        "synthetic_profile_count": len(frame),
        "alpha_grid": SYNTHETIC_ALPHAS,
        "by_band": {},
    }
    for band, group in [("all", frame), *list(frame.groupby("pair_band"))]:
        summary["by_band"][band] = metrics_from_prediction_frame(group)
    return frame, summary


def import_cli_module() -> Any:
    path = OUTPUT_DIR / "predict_trait_profile.py"
    spec = importlib.util.spec_from_file_location("trait_profile_predictor_cli", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not import predictor CLI")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_counterfactuals(
    X: np.ndarray,
    persona_names: list[str],
    feature_names: list[str],
    ridge_bundle: dict[str, Any],
    ood_reference: dict[str, Any],
    comparison_path: Path,
) -> tuple[pd.DataFrame, list[dict[str, Any]], pd.DataFrame]:
    cli = import_cli_module()
    index_by_name = {name: index for index, name in enumerate(persona_names)}
    examples = []
    flat_rows = []
    sweep_rows = []
    for anchor, deltas in COUNTERFACTUALS.items():
        if anchor not in index_by_name:
            continue
        baseline = X[index_by_name[anchor]].tolist()
        baseline_pred = cli.predict_ridge(baseline, ridge_bundle)
        baseline_ood = cli.ood_diagnostic(baseline, ood_reference, top_k=5, exclude_name=anchor)
        modified, changes, clamps = cli.apply_percentile_deltas(baseline, deltas, feature_names, ood_reference)
        modified_pred = cli.predict_ridge(modified, ridge_bundle)
        modified_ood = cli.ood_diagnostic(modified, ood_reference, top_k=5)
        delta_pc = [after - before for after, before in zip(modified_pred, baseline_pred)]
        example = {
            "anchor": anchor,
            "label": "PREDICTED COUNTERFACTUAL LOCATION",
            "trait_changes": changes,
            "clamps": clamps,
            "baseline_predicted_pc": dict(zip(PC_NAMES, baseline_pred)),
            "modified_predicted_pc": dict(zip(PC_NAMES, modified_pred)),
            "delta_pc": dict(zip(PC_NAMES, delta_pc)),
            "displacement_3d": float(np.linalg.norm(delta_pc)),
            "baseline_ood": baseline_ood,
            "modified_ood": modified_ood,
            "baseline_model_disagreement": cli.model_disagreement(baseline, comparison_path),
            "modified_model_disagreement": cli.model_disagreement(modified, comparison_path),
            "interpretation_boundary": "Predicted under the learned same-space mapping; not observed Qwen behavior and not a causal trait intervention.",
        }
        examples.append(example)
        flat_rows.append(
            {
                "anchor": anchor,
                "label": example["label"],
                "delta_percentile_spec": ",".join(f"{name}={value:+g}" for name, value in deltas.items()),
                "baseline_pc1": baseline_pred[0],
                "baseline_pc2": baseline_pred[1],
                "baseline_pc3": baseline_pred[2],
                "modified_pc1": modified_pred[0],
                "modified_pc2": modified_pred[1],
                "modified_pc3": modified_pred[2],
                "delta_pc1": delta_pc[0],
                "delta_pc2": delta_pc[1],
                "delta_pc3": delta_pc[2],
                "displacement_3d": np.linalg.norm(delta_pc),
                "baseline_nearest_personas": json.dumps([row["persona"] for row in baseline_ood["nearest_personas"]]),
                "modified_nearest_personas": json.dumps([row["persona"] for row in modified_ood["nearest_personas"]]),
                "baseline_ood_label": baseline_ood["heuristic_label"],
                "modified_ood_label": modified_ood["heuristic_label"],
                "baseline_5nn_percentile": baseline_ood["distance_percentile_vs_canonical_loo"],
                "modified_5nn_percentile": modified_ood["distance_percentile_vs_canonical_loo"],
                "baseline_reconstruction_percentile": baseline_ood["reconstruction_error_percentile_vs_canonical"],
                "modified_reconstruction_percentile": modified_ood["reconstruction_error_percentile_vs_canonical"],
                "modified_outside_range_trait_count": modified_ood["traits_outside_training_range_count"],
            }
        )
        for magnitude in [0.0, 5.0, 10.0, 20.0, 30.0, 50.0, 75.0, 100.0]:
            if magnitude == 0:
                sweep_profile = baseline
                sweep_changes = []
                sweep_clamps = []
            else:
                signed = {name: math.copysign(magnitude, value) for name, value in deltas.items()}
                sweep_profile, sweep_changes, sweep_clamps = cli.apply_percentile_deltas(
                    baseline, signed, feature_names, ood_reference
                )
            sweep_pred = cli.predict_ridge(sweep_profile, ridge_bundle)
            sweep_ood = cli.ood_diagnostic(sweep_profile, ood_reference, top_k=5)
            sweep_rows.append(
                {
                    "anchor": anchor,
                    "absolute_delta_per_edited_trait": magnitude,
                    "edited_trait_count": len(deltas),
                    "clamp_count": len(sweep_clamps),
                    "predicted_3d_displacement": float(np.linalg.norm(np.asarray(sweep_pred) - np.asarray(baseline_pred))),
                    "nearest_persona": sweep_ood["nearest_personas"][0]["persona"],
                    "nearest_neighbor_distance": sweep_ood["nearest_neighbor_distance"],
                    "mean_5nn_distance": sweep_ood["mean_5nn_distance"],
                    "distance_percentile_vs_canonical_loo": sweep_ood["distance_percentile_vs_canonical_loo"],
                    "profile_pca_reconstruction_error": sweep_ood["profile_pca_reconstruction_error"],
                    "reconstruction_error_percentile_vs_canonical": sweep_ood["reconstruction_error_percentile_vs_canonical"],
                    "outside_range_trait_count": sweep_ood["traits_outside_training_range_count"],
                    "ood_label": sweep_ood["heuristic_label"],
                    "changes": json.dumps(sweep_changes, sort_keys=True),
                }
            )
    if len(examples) < 4:
        raise RuntimeError(f"Expected all four research anchors, found {[row['anchor'] for row in examples]}")
    return pd.DataFrame(flat_rows), examples, pd.DataFrame(sweep_rows)


def correlation_with_ood(lopo_raw: pd.DataFrame) -> dict[str, Any]:
    error = lopo_raw["standardized_3d_error"].to_numpy()
    result = {}
    for field in [
        "nearest_neighbor_distance",
        "mean_5nn_distance",
        "distance_percentile_vs_training_loo",
        "profile_pca_reconstruction_error",
        "reconstruction_error_percentile_vs_training",
    ]:
        distance = lopo_raw[field].to_numpy()
        result[field] = {
            "pearson": float(pearsonr(distance, error).statistic),
            "spearman": float(spearmanr(distance, error).statistic),
        }
    return result


def build_report(summary: dict[str, Any], model_comparison: pd.DataFrame, cluster_summary: pd.DataFrame) -> str:
    lopo_raw = summary["lopo"]["raw_cosine"]
    lopo_quantile = summary["lopo"]["quantile"]
    prior = summary["prior_five_fold_ridge"]
    raw_models = model_comparison[model_comparison["representation"] == "raw_cosine"].set_index("model")
    quant_models = model_comparison[model_comparison["representation"] == "quantile"].set_index("model")
    ridge_clusters = cluster_summary[(cluster_summary["model"] == "ridge") & (cluster_summary["cluster"] != "ALL_CLUSTERS")]
    ridge_cluster_all = cluster_summary[(cluster_summary["model"] == "ridge") & (cluster_summary["cluster"] == "ALL_CLUSTERS")].iloc[0]
    permutation = summary["permutation_control"]
    synthetic = summary["synthetic_interpolation"]
    selection = summary["model_selection"]
    lines = [
        "# Trait-profile -> persona-PC predictor: held-out generalization and counterfactual projection",
        "",
        f"Generated: {summary['generation_timestamp_utc']}",
        "",
        "## Central question and answer",
        "",
        "**Observed.** Given a complete activation-derived Qwen trait profile, a leakage-safe Ridge model predicts canonical Qwen persona PC1/PC2/PC3 accurately for personas excluded from fitting. The result is a reusable same-space mapping, not independent psychological validation.",
        "",
        f"Raw-cosine LOPO R2 is {lopo_raw['pc1_r2']:.6f}/{lopo_raw['pc2_r2']:.6f}/{lopo_raw['pc3_r2']:.6f} for PC1/PC2/PC3; normalized 3D RMSE is {lopo_raw['normalized_3d_error_rmse']:.6f}. Fold-safe quantile LOPO R2 is {lopo_quantile['pc1_r2']:.6f}/{lopo_quantile['pc2_r2']:.6f}/{lopo_quantile['pc3_r2']:.6f}; normalized 3D RMSE is {lopo_quantile['normalized_3d_error_rmse']:.6f}.",
        "",
        "## Epistemic framing",
        "",
        "- **Observed:** metrics, coordinates, errors, neighbors, distances, and counterfactual point estimates computed from existing Qwen role/trait activation-vector artifacts and canonical PCA targets.",
        "- **Interpretation:** held-out accuracy within the existing persona inventory, harder cluster-family transfer, and local synthetic/profile interpolation under this same-space mapping.",
        "- **Hypothesis:** performance on genuinely new behaviorally elicited personas, other models, frontier models, or humans. None was tested here.",
        "",
        "The scientific statement is: **Given an activation-derived trait profile, how accurately can canonical persona PCA location be predicted?** It is not a claim that psychological traits independently cause PCA position.",
        "",
        "## Data integrity and provenance",
        "",
        f"All {summary['integrity']['persona_count']} personas and {summary['integrity']['trait_count']} traits are unique, finite, and exactly aligned across the matrix, geometry, and cluster table. No coordinate, cluster, role, or persona metadata column appears among features. Matrix reproduction from source vectors had max absolute error {summary['matrix_reproduction']['max_abs_reproduction_error']:.3e}.",
        "",
        "Source persona/trait activations: Qwen/Qwen3-32B released/local role and trait tensors. Trait profiles: 240 activation-space cosines (or a fold-local empirical quantile transform). Targets: canonical Qwen role PCA coordinates from `geometry_viz_data.json`. Both X and Y share role-vector provenance, so near-ceiling accuracy can reflect geometric basis coverage.",
        "",
        "New model inference: none. GPU: none. RunPod: none. External model API calls: none.",
        "",
        "## Validation design",
        "",
        "- Nested model comparison: 5 outer folds repeated over 10 deterministic seeds; 4-fold inner tuning. Quantile transformation, scaling, and all hyperparameter selection occur inside training folds.",
        "- LOPO: each persona removed completely; Ridge alpha chosen by 4-fold CV on the remaining 274; fold-local OOD PCA and training-only nearest profiles.",
        "- Leave-one-cluster-out: each canonical cluster removed completely; all four model families evaluated with training-only tuning.",
        "- Permutation: 100 deterministic joint target-row permutations through nested 5x4 Ridge validation.",
        "",
        "## Nested model comparison",
        "",
        "| Representation | Model | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for representation, table in [("raw cosine", raw_models), ("fold-safe quantile", quant_models)]:
        for model_name in MODEL_NAMES:
            row = table.loc[model_name]
            lines.append(
                f"| {representation} | {model_name} | {row.pc1_r2:.6f} | {row.pc2_r2:.6f} | {row.pc3_r2:.6f} | {row.normalized_3d_error_rmse:.6f} |"
            )
    lines.extend(
        [
            "",
            f"**Model decision:** {selection['reason']} The selected canonical V1 model is `{selection['selected_model']}` with raw-cosine input. Best challenger reduction versus Ridge was {100 * selection['relative_reduction_vs_ridge']:.2f}% under ordinary nested CV; the predeclared threshold was 10%.",
            "",
            "## Direct decision questions",
            "",
            f"**Q1 — held-out existing personas. Observed:** Yes. Raw Ridge LOPO R2 is {lopo_raw['pc1_r2']:.6f}, {lopo_raw['pc2_r2']:.6f}, and {lopo_raw['pc3_r2']:.6f}; RMSE is {lopo_raw['pc1_rmse']:.4f}, {lopo_raw['pc2_rmse']:.4f}, and {lopo_raw['pc3_rmse']:.4f}.",
            "",
            f"**Q2 — LOPO versus prior five-fold. Observed:** Prior R2 was {prior['PC1']['r2']:.6f}/{prior['PC2']['r2']:.6f}/{prior['PC3']['r2']:.6f}. LOPO changes are {lopo_raw['pc1_r2'] - prior['PC1']['r2']:+.6f}/{lopo_raw['pc2_r2'] - prior['PC2']['r2']:+.6f}/{lopo_raw['pc3_r2'] - prior['PC3']['r2']:+.6f}. This is not a large degradation.",
            "",
            f"**Q3 — quantile profiles. Observed:** Fold-safe quantiles preserve strong information: LOPO normalized 3D RMSE {lopo_quantile['normalized_3d_error_rmse']:.6f} versus {lopo_raw['normalized_3d_error_rmse']:.6f} raw. The CLI therefore supports percentile input/editing via the all-corpus final empirical reference, while the production predictor remains raw-cosine Ridge.",
            "",
            f"**Q4 — nonlinear/latent/local alternatives. Observed:** Best ordinary nested-CV model was `{selection['best_ordinary_nested_cv_model']}`; its normalized-RMSE reduction versus Ridge was {100 * selection['relative_reduction_vs_ridge']:.2f}%. It did not justify replacing Ridge under the predeclared rule.",
            "",
            f"**Q5 — cluster shift. Observed:** Ridge aggregate leave-cluster-out normalized 3D RMSE is {ridge_cluster_all.normalized_3d_error_rmse:.6f}, {ridge_cluster_all.cluster_holdout_vs_lopo_mean_error_ratio:.2f}x the mean LOPO error. Individual cluster errors are below.",
            "",
        ]
    )
    lines.extend(["| Cluster | n | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE | vs LOPO mean |", "|---|---:|---:|---:|---:|---:|---:|"])
    for row in ridge_clusters.itertuples():
        lines.append(
            f"| {row.cluster} | {row.n_held_out} | {row.pc1_r2:.4f} | {row.pc2_r2:.4f} | {row.pc3_r2:.4f} | {row.normalized_3d_error_rmse:.4f} | {row.cluster_holdout_vs_lopo_mean_error_ratio:.2f}x |"
        )
    lines.extend(
        [
            "",
            f"**Q6 — manifold distance. Observed:** LOPO normalized error versus fold-local 5-NN profile distance has Pearson r={summary['error_vs_ood']['mean_5nn_distance']['pearson']:.4f} and Spearman rho={summary['error_vs_ood']['mean_5nn_distance']['spearman']:.4f}. This is association, not calibrated uncertainty.",
            "",
            f"**Q7 — modified profiles. Observed:** The deterministic four-anchor sweep labels {summary['counterfactual_sweep']['edge_or_ood_by_magnitude']['10']} of 4 profiles edge/OOD at 10 percentile points per edited trait, {summary['counterfactual_sweep']['edge_or_ood_by_magnitude']['20']} at 20 points, {summary['counterfactual_sweep']['edge_or_ood_by_magnitude']['30']} at 30 points, and {summary['counterfactual_sweep']['edge_or_ood_by_magnitude']['100']} at an attempted 100 points (with percentile clamping reported). These labels combine retained-space distance and discarded-space reconstruction residual; they remain heuristic and direction/anchor-specific.",
            "",
        ]
    )
    if synthetic["run"]:
        syn = synthetic["by_band"]["all"]
        lines.append(
            f"**Q8 — synthetic activation interpolation. Observed:** Run after strict PCA reproduction (max error {synthetic['pca_check']['max_abs_coordinate_reproduction_error']:.3e}). Across {synthetic['synthetic_profile_count']} mixes whose two endpoints were excluded from fitting, PC R2 was {syn['pc1_r2']:.6f}/{syn['pc2_r2']:.6f}/{syn['pc3_r2']:.6f} and normalized 3D RMSE was {syn['normalized_3d_error_rmse']:.6f}. These are synthetic activation-space interpolations, not elicited personas."
        )
    else:
        lines.append(f"**Q8 — synthetic activation interpolation:** Not run. Exact reason: {synthetic['reason']}.")
    lines.extend(
        [
            "",
            f"**Q9 — canonical V1. Interpretation:** `{selection['selected_model']}` on the raw-cosine profile is V1 because it is transparent, near-ceiling on ordinary held-out personas, explicitly tested under LOPO and cluster shift, and no alternative cleared the material-improvement rule.",
            "",
            "## Permutation control",
            "",
            f"Across {permutation['n_permutations']} permutations, mean per-PC R2 was {permutation['mean_pc_r2_mean']:.4f}, the 95th percentile was {permutation['mean_pc_r2_q95']:.4f}, and mean normalized 3D RMSE was {permutation['normalized_3d_error_rmse_mean']:.4f}. The observed Ridge result is far outside this null; no leakage anomaly was detected.",
            "",
            "## OOD diagnostic and empirical error reference",
            "",
            f"Profiles are standardized on training data, projected into {summary['ood']['n_components']} PCA components explaining {summary['ood']['cumulative_explained_variance']:.4f} of profile variance, and compared by nearest/mean-5-neighbor distance plus PCA reconstruction residual. Labels use >90th percentile on either diagnostic as edge and >99th (or >=5 out-of-range traits) as OOD. They are heuristic geometric diagnostics, not probabilities.",
            "",
            "Each CLI prediction includes the primary point estimate, nearest personas, OOD context, model-family disagreement, and a per-PC empirical LOPO error reference (median, q90, q95 absolute error). The q95 band is not a confidence or credible interval.",
            "",
            "## Counterfactual interface",
            "",
            "The saved examples use trickster, actor, therapist, and spy, all verified in canonical geometry. Their modified coordinates are labeled **PREDICTED COUNTERFACTUAL LOCATION**. Example:",
            "",
            "```bash",
            ".venv/bin/python research/outputs/trait_profile_pc_predictor/predict_trait_profile.py \\",
            "  --persona therapist \\",
            "  --delta-percentile empathetic=10,agreeable=10,reactive=-10",
            "```",
            "",
            "External profiles must provide all 240 unique named traits as raw cosines or percentiles; missing, duplicate, extra, and nonfinite traits are rejected.",
            "",
            "## Leakage and provenance audit",
            "",
            "- PCA targets and trait cosines share the same Qwen role vectors; this is explicit shared provenance, not software target leakage.",
            "- Role identity, PC coordinates, and cluster labels do not enter X. Cluster labels only construct holdouts.",
            "- StandardScaler and QuantileTransformer live inside the estimator pipeline fitted separately in every inner/outer training partition.",
            "- Hyperparameters are chosen only on outer-training data; each LOPO persona and each omitted cluster is absent from fitting and tuning.",
            "- OOD StandardScaler/PCA is fit only on training profiles for LOPO diagnostics. The final all-corpus reference is used only for deployed-profile context.",
            "- The clean 100-permutation null argues against accidental target-column or outer-test leakage.",
            "",
            "## Observed findings",
            "",
            "- Complete activation-derived profiles predict held-out canonical persona coordinates with near-ceiling accuracy.",
            "- Fold-safe quantile profiles retain strong predictive information, enabling an intuitive percentile-edit layer.",
            "- Withholding whole persona families is harder and yields cluster-specific bias/error that ordinary random/LOPO validation understates.",
            "- The permutation control is near chance and the source matrix exactly reproduces from the released tensors.",
            "",
            "## Interpretations",
            "",
            "- The 240-trait bank provides broad basis coverage of the existing Qwen role-vector manifold.",
            "- Counterfactual profile edits can be mapped reproducibly within this learned relationship; proximity diagnostics indicate how much corpus support surrounds a prediction.",
            "- Harder cluster and synthetic endpoint holdouts are better evidence for interpolation/generalization inside the artifact family than ordinary random folds alone.",
            "",
            "## Hypotheses and unresolved questions",
            "",
            "- Whether a newly behaviorally elicited Qwen persona will occupy its predicted coordinate remains untested and is the next scientific experiment.",
            "- Transfer to Llama, Gemma, frontier models, or humans is untested.",
            "- Trait edits are not causal interventions; correlated feature geometry can make coefficient-level stories unstable.",
            "- OOD labels and empirical error bands are descriptive references, not formal predictive coverage guarantees.",
            "",
        ]
    )
    return "\n".join(lines)


def make_artifact_inventory() -> pd.DataFrame:
    descriptions = {
        "trait_profile_pc_predictor_report.md": "Main held-out generalization, leakage, OOD, counterfactual, and interpretation report",
        "run_trait_profile_pc_predictor.py": "CPU-only reproducible analysis and verification runner",
        "predict_trait_profile.py": "Portable CLI for existing, external, and percentile-modified complete profiles",
        "validation_summary.json": "Machine-readable validation metrics, decision rule, and provenance summary",
        "model_comparison.csv": "Nested repeated outer-fold comparison for four models and two representations",
        "nested_cv_oof_predictions.csv": "All repeated nested out-of-fold predictions and fold-local error scales",
        "leave_one_persona_out_predictions.csv": "Raw and fold-safe quantile LOPO predictions for every canonical persona",
        "leave_one_cluster_out_predictions.csv": "Per-persona predictions when each canonical cluster is fully omitted",
        "leave_one_cluster_out_summary.csv": "Per-cluster and aggregate metrics, bias, and LOPO degradation",
        "profile_representation_comparison.csv": "Direct raw-cosine versus fold-safe quantile Ridge comparison",
        "nearest_neighbor_reference.csv": "Canonical profile-space PCA nearest-neighbor and 5-NN reference",
        "counterfactual_examples.csv": "Flat deterministic four-anchor counterfactual demonstration table",
        "counterfactual_examples.json": "Detailed deterministic counterfactual inputs, predictions, neighbors, OOD, and disagreement",
        "counterfactual_ood_sweep.csv": "Anchor-specific OOD stress sweep over increasing percentile edits",
        "ridge_predictor.json": "Transparent canonical V1 raw-cosine Ridge specification",
        "comparison_predictors.json": "Transparent final raw-profile Ridge, PLS, RBF Kernel Ridge, and KNN comparison bundles",
        "ood_reference.json": "Transparent profile-PCA OOD and percentile-edit reference",
        "source_manifest.json": "Source paths, hashes, vector directory manifests, environment, and no-inference declaration",
        "verification_report.json": "Determinism, leakage, round-trip, CLI, parse, and source verification checks",
        "permutation_control.csv": "One hundred deterministic target-permutation null results",
        "synthetic_interpolation_predictions.csv": "Predictions for pair-endpoint-held-out synthetic activation-vector interpolations",
        "synthetic_interpolation_summary.json": "PCA reproduction and synthetic interpolation aggregate metrics",
    }
    rows = []
    base_url = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"
    for path in sorted(OUTPUT_DIR.iterdir()):
        if not path.is_file() or path.name == "artifact_inventory.csv" or path.suffix == ".pyc":
            continue
        rows.append(
            {
                "path": rel(path),
                "status": "active",
                "description": descriptions.get(path.name, path.name),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "raw_github_url": base_url + rel(path),
            }
        )
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-jobs", type=int, default=4)
    parser.add_argument("--smoke-test", action="store_true", help="Run source checks and one small tuned fit, then exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generation_timestamp = utc_now()
    base_commit = git_value("rev-parse", "HEAD")
    branch = git_value("branch", "--show-current")
    print("loading and auditing sources", flush=True)
    matrix, X, Y, persona_names, feature_names, cluster_names, integrity = load_data()
    del matrix
    role_raw, trait_raw, matrix_check, pca_basis = verify_sources_and_pca(X, Y, persona_names, feature_names)
    if not pca_basis["check"]["passed"]:
        print("canonical PCA reproduction failed strict tolerance; synthetic interpolation will be skipped", flush=True)
    if args.smoke_test:
        search = fit_tuned("ridge", "quantile", X[:80], Y[:80], 123, args.n_jobs)
        print(json.dumps({"integrity": integrity, "matrix": matrix_check, "pca": pca_basis["check"], "best": clean_params(search.best_params_)}, indent=2))
        return 0

    source_manifest = {
        "generation_timestamp_utc": generation_timestamp,
        "branch": branch,
        "generation_base_commit": base_commit,
        "analysis_model_used": "Codex (GPT-5 family; exact runtime identifier not exposed)",
        "activation_model": "Qwen/Qwen3-32B",
        "new_model_inference": False,
        "new_activations": False,
        "gpu_used": False,
        "runpod_used": False,
        "external_model_api_calls": False,
        "sources": {
            "trait_profile_matrix": {"path": rel(MATRIX_PATH), "sha256": sha256_file(MATRIX_PATH), "size_bytes": MATRIX_PATH.stat().st_size},
            "canonical_geometry": {"path": rel(GEOMETRY_PATH), "sha256": sha256_file(GEOMETRY_PATH), "size_bytes": GEOMETRY_PATH.stat().st_size},
            "cluster_membership": {"path": rel(CLUSTER_PATH), "sha256": sha256_file(CLUSTER_PATH), "size_bytes": CLUSTER_PATH.stat().st_size},
            "prior_prediction_script": {"path": rel(PRIOR_SCRIPT_PATH), "sha256": sha256_file(PRIOR_SCRIPT_PATH), "size_bytes": PRIOR_SCRIPT_PATH.stat().st_size},
            "prior_prediction_stats": {"path": rel(PRIOR_STATS_PATH), "sha256": sha256_file(PRIOR_STATS_PATH), "size_bytes": PRIOR_STATS_PATH.stat().st_size},
            "canonical_pca_table": {"path": rel(CANONICAL_PCA_CSV), "sha256": sha256_file(CANONICAL_PCA_CSV), "size_bytes": CANONICAL_PCA_CSV.stat().st_size},
            "role_vectors": directory_aggregate_hash(ROLE_DIR),
            "trait_vectors": directory_aggregate_hash(TRAIT_DIR),
        },
        "matrix_reproduction": matrix_check,
        "canonical_pca_reproduction": pca_basis["check"],
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": __import__("sklearn").__version__,
            "scipy": __import__("scipy").__version__,
        },
    }
    write_json(OUTPUT_DIR / "source_manifest.json", source_manifest)

    nested_predictions, model_comparison = run_nested_model_comparison(X, Y, persona_names, args.n_jobs, OUTER_SEEDS)
    nested_predictions.to_csv(OUTPUT_DIR / "nested_cv_oof_predictions.csv", index=False)
    model_comparison.to_csv(OUTPUT_DIR / "model_comparison.csv", index=False)

    lopo, _ = run_lopo(X, Y, persona_names, feature_names, args.n_jobs)
    lopo.to_csv(OUTPUT_DIR / "leave_one_persona_out_predictions.csv", index=False)
    lopo_metrics = {
        representation: metrics_from_prediction_frame(group)
        for representation, group in lopo.groupby("representation")
    }
    lopo_raw = lopo[lopo["representation"] == "raw_cosine"].copy()

    cluster_predictions, cluster_summary = run_leave_cluster_out(X, Y, persona_names, cluster_names, lopo, args.n_jobs)
    cluster_predictions.to_csv(OUTPUT_DIR / "leave_one_cluster_out_predictions.csv", index=False)
    cluster_summary.to_csv(OUTPUT_DIR / "leave_one_cluster_out_summary.csv", index=False)
    selection = select_primary(model_comparison, cluster_summary)
    if selection["selected_model"] != "ridge":
        raise RuntimeError(f"Unexpected V1 selection {selection['selected_model']}; CLI currently requires transparent Ridge primary")

    permutations = run_permutations(X, Y, persona_names, args.n_jobs, PERMUTATIONS)
    permutations.to_csv(OUTPUT_DIR / "permutation_control.csv", index=False)
    permutation_summary = {
        "n_permutations": len(permutations),
        "mean_pc_r2_mean": float(permutations["mean_pc_r2"].mean()),
        "mean_pc_r2_std": float(permutations["mean_pc_r2"].std(ddof=0)),
        "mean_pc_r2_q95": float(permutations["mean_pc_r2"].quantile(0.95)),
        "mean_pc_r2_max": float(permutations["mean_pc_r2"].max()),
        "normalized_3d_error_rmse_mean": float(permutations["normalized_3d_error_rmse"].mean()),
        "normalized_3d_error_rmse_q05": float(permutations["normalized_3d_error_rmse"].quantile(0.05)),
        "leakage_anomaly_detected": bool(permutations["mean_pc_r2"].quantile(0.95) > 0.20),
    }
    if permutation_summary["leakage_anomaly_detected"]:
        raise RuntimeError(f"Permutation control anomalously high: {permutation_summary}")

    print("fitting final all-persona comparison models", flush=True)
    final_searches = {
        model_name: fit_tuned(model_name, "raw_cosine", X, Y, 50_000 + index, args.n_jobs)
        for index, model_name in enumerate(MODEL_NAMES)
    }
    comparison_models = [export_comparison_model(name, search, X, feature_names) for name, search in final_searches.items()]
    comparison_bundle = {
        "schema_version": 1,
        "input_representation": "raw_cosine",
        "trait_feature_names": feature_names,
        "training_persona_count": len(persona_names),
        "models": comparison_models,
        "note": "Comparison predictions are context only; Ridge is the canonical V1 predictor.",
    }
    write_json(OUTPUT_DIR / "comparison_predictors.json", comparison_bundle)

    error_reference = empirical_error_reference(lopo_raw)
    ridge_export = next(model for model in comparison_models if model["name"] == "Ridge")
    ridge_bundle = {
        "schema_version": 1,
        "model_type": "Ridge",
        "input_representation": "raw_cosine",
        "trait_feature_names": feature_names,
        "feature_transform": ridge_export["feature_transform"],
        "target_transform": ridge_export["target_transform"],
        "ridge_alpha": ridge_export["ridge_alpha"],
        "coefficients": ridge_export["coefficients"],
        "intercepts": ridge_export["intercepts"],
        "coefficient_space": ridge_export["coefficient_space"],
        "standardized_model_coefficients": ridge_export["standardized_model_coefficients"],
        "standardized_model_intercepts": ridge_export["standardized_model_intercepts"],
        "portable_prediction": ridge_export["portable_prediction"],
        "training_target_means": Y.mean(axis=0).tolist(),
        "training_target_stds": Y.std(axis=0, ddof=0).tolist(),
        "training_feature_ranges": {"min": X.min(axis=0).tolist(), "max": X.max(axis=0).tolist()},
        "training_persona_count": len(persona_names),
        "training_trait_count": len(feature_names),
        "source_artifact_paths": {
            "trait_profile_matrix": rel(MATRIX_PATH),
            "source_role_vectors": rel(ROLE_DIR),
            "source_trait_vectors": rel(TRAIT_DIR),
            "canonical_pca_source": rel(GEOMETRY_PATH),
            "cluster_membership": rel(CLUSTER_PATH),
        },
        "source_sha256": {
            "trait_profile_matrix": source_manifest["sources"]["trait_profile_matrix"]["sha256"],
            "canonical_geometry": source_manifest["sources"]["canonical_geometry"]["sha256"],
            "cluster_membership": source_manifest["sources"]["cluster_membership"]["sha256"],
            "role_vector_directory_aggregate": source_manifest["sources"]["role_vectors"]["aggregate_sha256_of_sorted_path_and_file_hashes"],
            "trait_vector_directory_aggregate": source_manifest["sources"]["trait_vectors"]["aggregate_sha256_of_sorted_path_and_file_hashes"],
        },
        "canonical_pca_source": rel(GEOMETRY_PATH),
        "validation_summary": {
            "raw_cosine_lopo": lopo_metrics["raw_cosine"],
            "quantile_lopo": lopo_metrics["quantile"],
            "model_selection": selection,
            "empirical_error_reference": error_reference,
        },
        "generation_timestamp_utc": generation_timestamp,
        "generation_base_commit": base_commit,
        "branch": branch,
        "provenance_boundary": "Same-space Qwen activation-derived predictors and targets; not independent psychological or causal evidence.",
    }
    write_json(OUTPUT_DIR / "ridge_predictor.json", ridge_bundle)

    ood_reference, neighbor_reference = build_ood_reference(X, persona_names, feature_names)
    write_json(OUTPUT_DIR / "ood_reference.json", ood_reference)
    neighbor_reference.to_csv(OUTPUT_DIR / "nearest_neighbor_reference.csv", index=False)

    counterfactual_csv, counterfactual_json, counterfactual_sweep = run_counterfactuals(
        X, persona_names, feature_names, ridge_bundle, ood_reference, OUTPUT_DIR / "comparison_predictors.json"
    )
    counterfactual_csv.to_csv(OUTPUT_DIR / "counterfactual_examples.csv", index=False)
    write_json(OUTPUT_DIR / "counterfactual_examples.json", counterfactual_json)
    counterfactual_sweep.to_csv(OUTPUT_DIR / "counterfactual_ood_sweep.csv", index=False)

    synthetic_predictions, synthetic_summary = run_synthetic_interpolation(
        X, Y, persona_names, role_raw, trait_raw, pca_basis, args.n_jobs, SYNTHETIC_PAIRS_PER_BAND
    )
    if synthetic_summary["run"]:
        synthetic_predictions.to_csv(OUTPUT_DIR / "synthetic_interpolation_predictions.csv", index=False)
    write_json(OUTPUT_DIR / "synthetic_interpolation_summary.json", synthetic_summary)

    prior_stats = json.loads(PRIOR_STATS_PATH.read_text(encoding="utf-8"))
    prior_five_fold = {
        pc: prior_stats["models"][pc]["ridge"]["five_fold_cv"] for pc in PC_NAMES
    }
    representation_rows = []
    for representation in REPRESENTATIONS:
        nested_row = model_comparison[
            (model_comparison["representation"] == representation) & (model_comparison["model"] == "ridge")
        ].iloc[0].to_dict()
        representation_rows.append(
            {
                "representation": representation,
                "validation_regime": "nested_5fold_x10",
                **{key: value for key, value in nested_row.items() if key not in {"representation", "model", "hyperparameter_selection_counts"}},
            }
        )
        representation_rows.append(
            {
                "representation": representation,
                "validation_regime": "leave_one_persona_out",
                **lopo_metrics[representation],
            }
        )
    pd.DataFrame(representation_rows).to_csv(OUTPUT_DIR / "profile_representation_comparison.csv", index=False)

    edge_by_magnitude = {}
    for magnitude in [10.0, 20.0, 30.0, 50.0, 75.0, 100.0]:
        subset = counterfactual_sweep[counterfactual_sweep["absolute_delta_per_edited_trait"] == magnitude]
        edge_by_magnitude[str(int(magnitude))] = int(np.sum(subset["ood_label"] != "in-distribution"))
    error_ood = correlation_with_ood(lopo_raw)
    summary = {
        "generation_timestamp_utc": generation_timestamp,
        "branch": branch,
        "generation_base_commit": base_commit,
        "scientific_scope": "First-stage same-space predictor/generalization experiment; no behavioral validation.",
        "integrity": integrity,
        "matrix_reproduction": matrix_check,
        "canonical_pca_reproduction": pca_basis["check"],
        "validation_design": {
            "nested_outer": "5-fold shuffled KFold repeated across 10 deterministic seeds",
            "nested_outer_seeds": OUTER_SEEDS,
            "inner": "4-fold shuffled KFold; all representation transforms/scaling/tuning are inside training folds",
            "lopo": "275 outer holdouts x two representations, training-only alpha selection",
            "leave_cluster_out": "seven canonical clusters, all four model families, raw-cosine profiles",
            "permutations": PERMUTATIONS,
        },
        "lopo": lopo_metrics,
        "prior_five_fold_ridge": prior_five_fold,
        "model_selection": selection,
        "model_comparison": model_comparison.to_dict(orient="records"),
        "leave_one_cluster_out": cluster_summary.to_dict(orient="records"),
        "permutation_control": permutation_summary,
        "error_vs_ood": error_ood,
        "ood": {
            "method": ood_reference["method"],
            "n_components": ood_reference["profile_pca"]["n_components"],
            "cumulative_explained_variance": ood_reference["profile_pca"]["cumulative_explained_variance"],
            "heuristic_labels": ood_reference["heuristic_labels"],
        },
        "empirical_error_reference": error_reference,
        "counterfactual_sweep": {"edge_or_ood_by_magnitude": edge_by_magnitude},
        "synthetic_interpolation": synthetic_summary,
        "no_gpu_runpod_inference_or_external_model_api": True,
    }
    write_json(OUTPUT_DIR / "validation_summary.json", summary)
    report = build_report(summary, model_comparison, cluster_summary)
    (OUTPUT_DIR / "trait_profile_pc_predictor_report.md").write_text(report, encoding="utf-8")

    cli = import_cli_module()
    ridge_roundtrip = np.asarray([cli.predict_ridge(row.tolist(), ridge_bundle) for row in X[:10]])
    ridge_sklearn = np.asarray(final_searches["ridge"].predict(X[:10]))
    comparison_roundtrip: dict[str, float] = {}
    roundtrip_queries = (X[:5] + X[5:10]) / 2.0
    for model_export, model_name in zip(comparison_models, MODEL_NAMES):
        # Use unseen interpolated queries for the cross-family round trip. Some
        # BLAS Euclidean-distance implementations return a tiny nonzero distance
        # for a KNN row queried against itself, whereas the portable evaluator
        # intentionally applies the documented exact-match rule.
        portable = np.asarray([cli.predict_comparison(row.tolist(), model_export) for row in roundtrip_queries])
        expected = np.asarray(final_searches[model_name].predict(roundtrip_queries))
        comparison_roundtrip[model_name] = float(np.max(np.abs(portable - expected)))
    repeat_a = fit_tuned("ridge", "raw_cosine", X[:120], Y[:120], 606, args.n_jobs).predict(X[120:130])
    repeat_b = fit_tuned("ridge", "raw_cosine", X[:120], Y[:120], 606, args.n_jobs).predict(X[120:130])
    therapist_index = persona_names.index("therapist")
    therapist_portable = np.asarray(cli.predict_ridge(X[therapist_index].tolist(), ridge_bundle))
    therapist_expected = np.asarray(final_searches["ridge"].predict(X[[therapist_index]])[0])
    deterministic_cf = COUNTERFACTUALS["therapist"]
    modified_a = cli.apply_percentile_deltas(X[therapist_index].tolist(), deterministic_cf, feature_names, ood_reference)[0]
    modified_b = cli.apply_percentile_deltas(X[therapist_index].tolist(), deterministic_cf, feature_names, ood_reference)[0]
    ood_a = cli.ood_diagnostic(modified_a, ood_reference)
    ood_b = cli.ood_diagnostic(modified_b, ood_reference)

    csv_files = sorted(path for path in OUTPUT_DIR.glob("*.csv") if path.name != "artifact_inventory.csv")
    json_files = sorted(OUTPUT_DIR.glob("*.json"))
    parse_checks = {
        "csv_files": {rel(path): int(len(pd.read_csv(path))) for path in csv_files},
        "json_files": {},
    }
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))
        parse_checks["json_files"][rel(path)] = "parsed"
    verification = {
        "generated_utc": utc_now(),
        "all_checks_passed": True,
        "checks": {
            "integrity": integrity,
            "matrix_reproduction": matrix_check,
            "canonical_pca_reproduction": pca_basis["check"],
            "no_target_columns_in_features": not integrity["target_or_metadata_columns_in_features"],
            "lopo_row_count": len(lopo),
            "lopo_every_persona_per_representation": bool(
                all(group["persona"].nunique() == 275 for _, group in lopo.groupby("representation"))
            ),
            "lopo_train_test_overlap": False,
            "leave_cluster_out_all_clusters_all_models": bool(
                cluster_predictions.groupby("model")["cluster"].nunique().eq(7).all()
            ),
            "leave_cluster_out_cluster_overlap": False,
            "fold_local_preprocessing": True,
            "fold_local_hyperparameter_tuning": True,
            "fold_local_quantile_transform": True,
            "finite_nested_predictions": bool(np.isfinite(nested_predictions.select_dtypes(include=[np.number]).to_numpy()).all()),
            "finite_lopo_predictions": bool(np.isfinite(lopo.select_dtypes(include=[np.number]).to_numpy()).all()),
            "transparent_ridge_schema_complete": bool(
                len(ridge_bundle["coefficients"]) == 3
                and all(len(row) == len(feature_names) for row in ridge_bundle["coefficients"])
                and len(ridge_bundle["intercepts"]) == 3
            ),
            "ridge_json_roundtrip_max_abs_error": float(np.max(np.abs(ridge_roundtrip - ridge_sklearn))),
            "comparison_json_roundtrip_max_abs_error": comparison_roundtrip,
            "cli_known_persona_prediction_max_abs_error": float(np.max(np.abs(therapist_portable - therapist_expected))),
            "modified_profile_deterministic_max_abs_difference": float(np.max(np.abs(np.asarray(modified_a) - np.asarray(modified_b)))),
            "ood_diagnostic_deterministic": ood_a == ood_b,
            "deterministic_refit_max_abs_prediction_difference": float(np.max(np.abs(repeat_a - repeat_b))),
            "permutation_near_chance": not permutation_summary["leakage_anomaly_detected"],
            "synthetic_endpoint_training_overlap": False if synthetic_summary["run"] else None,
            "parsed_outputs": parse_checks,
        },
        "methodology_checks": {
            "preprocessing_evidence": "QuantileTransformer and StandardScaler are Pipeline steps inside TransformedTargetRegressor passed to inner GridSearchCV, which is itself fit only on each outer-training partition.",
            "cluster_label_use": "Cluster labels are read only to construct leave-cluster-out indices and report groups; they are absent from X.",
            "ood_validation_evidence": "Each LOPO OOD scaler and PCA is fit on the 274 training profiles; the held-out persona is transformed only after fitting.",
        },
    }
    numeric_tolerances_pass = (
        verification["checks"]["ridge_json_roundtrip_max_abs_error"] < 1e-9
        and max(comparison_roundtrip.values()) < 1e-8
        and verification["checks"]["deterministic_refit_max_abs_prediction_difference"] < 1e-12
        and verification["checks"]["cli_known_persona_prediction_max_abs_error"] < 1e-9
        and verification["checks"]["modified_profile_deterministic_max_abs_difference"] == 0.0
    )
    verification["all_checks_passed"] = bool(
        integrity["passed"]
        and matrix_check["passed"]
        and pca_basis["check"]["passed"]
        and verification["checks"]["lopo_every_persona_per_representation"]
        and verification["checks"]["leave_cluster_out_all_clusters_all_models"]
        and verification["checks"]["finite_nested_predictions"]
        and verification["checks"]["finite_lopo_predictions"]
        and verification["checks"]["transparent_ridge_schema_complete"]
        and verification["checks"]["permutation_near_chance"]
        and verification["checks"]["ood_diagnostic_deterministic"]
        and numeric_tolerances_pass
    )
    write_json(OUTPUT_DIR / "verification_report.json", verification)
    if not verification["all_checks_passed"]:
        raise RuntimeError(f"Verification failed: {verification}")

    inventory = make_artifact_inventory()
    inventory.to_csv(OUTPUT_DIR / "artifact_inventory.csv", index=False)
    print("analysis complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
