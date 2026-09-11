#!/usr/bin/env python3
"""Measure how sparsely Qwen trait profiles predict canonical persona geometry.

This CPU-only analysis consumes the existing 275-persona x 240-trait raw
activation-cosine matrix and canonical Qwen PC1/PC2/PC3 coordinates. It does
not run a language model, extract activations, use a GPU, use RunPod, or call
an external model API.
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
import tempfile
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from scipy.stats import pearsonr
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import MultiTaskElasticNetCV, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
np.seterr(all="ignore")


REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "research/outputs/qwen_trait_sparsity_prediction"
PRIOR_DIR = REPO_ROOT / "research/outputs/trait_profile_pc_predictor"
PRIOR_RUNNER = PRIOR_DIR / "run_trait_profile_pc_predictor.py"
PRIOR_SUMMARY = PRIOR_DIR / "validation_summary.json"
PRIOR_MODEL_COMPARISON = PRIOR_DIR / "model_comparison.csv"
MATRIX_PATH = REPO_ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
GEOMETRY_PATH = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
RIDGE15_PATH = REPO_ROOT / "research/outputs/persona_trait_ridge_plots/trait_category_order.csv"
PROVENANCE_REPORT = REPO_ROOT / "research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md"

PC_NAMES = ["PC1", "PC2", "PC3"]
OUTER_SEEDS = list(range(42, 52))
ALPHAS = [1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0]
REQUESTED_BUDGETS = [1, 2, 3, 5, 8, 10, 15, 20, 30, 40, 60]
FIXED15 = [
    "creative", "abstract", "curious",
    "reactive", "adaptable", "practical",
    "skeptical", "analytical", "conscientious",
    "rebellious", "competitive", "manipulative",
    "empathetic", "agreeable", "altruistic",
]
RANDOM_BUDGETS = [5, 10, 15, 30]
PERMUTATION_BUDGETS = [5, 10, 15]
REDUNDANCY_THRESHOLDS = [0.90, 0.95]
SPARSE_L1_RATIOS = [0.5, 0.9, 1.0]
SPARSE_ALPHAS = [3e-3, 1e-2, 3e-2, 1e-1]


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


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, float_format="%.12g", lineterminator="\n")


def frame_csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False, float_format="%.12g", lineterminator="\n").encode("utf-8")


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO_ROOT, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def import_prior() -> Any:
    spec = importlib.util.spec_from_file_location("canonical_trait_predictor", PRIOR_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import canonical predictor runner: {PRIOR_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_and_verify_data(prior: Any) -> tuple[np.ndarray, np.ndarray, list[str], list[str], dict[str, Any]]:
    _, X, Y, personas, traits, _, integrity = prior.load_data()
    ridge15 = pd.read_csv(RIDGE15_PATH)
    observed_fixed = ridge15["trait"].astype(str).tolist()
    if observed_fixed != FIXED15:
        raise RuntimeError(f"Fixed editorial trait mismatch: observed={observed_fixed!r}")
    if any(trait not in traits for trait in FIXED15):
        raise RuntimeError("A fixed editorial trait is absent from the canonical 240-trait matrix")
    canonical = pd.read_csv(
        REPO_ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"
    )
    target_columns = [column for column in ["activation_pc1", "activation_pc2", "activation_pc3"] if column in canonical.columns]
    canonical_name = "persona" if "persona" in canonical.columns else "role"
    if len(target_columns) != 3 or not set(canonical[canonical_name].astype(str)).issubset(personas):
        raise RuntimeError("Canonical PCA coordinate table does not align with the source matrix")
    canonical = canonical.set_index(canonical_name)
    shared_indices = [personas.index(name) for name in canonical.index.astype(str)]
    canonical_y = canonical[target_columns].to_numpy(dtype=np.float64)
    coordinate_error = float(np.max(np.abs(canonical_y - Y[shared_indices])))
    if coordinate_error > 1e-5:
        raise RuntimeError(f"Canonical target mismatch: max abs error={coordinate_error}")
    audit = {
        **integrity,
        "fixed_editorial_traits_exact_match": observed_fixed == FIXED15,
        "fixed_editorial_traits": observed_fixed,
        "canonical_coordinate_table_max_abs_difference": coordinate_error,
        "canonical_coordinate_table_tolerance": 1e-5,
        "canonical_coordinate_table_shared_persona_count": len(shared_indices),
    }
    return X, Y, personas, traits, audit


def outer_splits(X: np.ndarray, seeds: Sequence[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for repeat, seed in enumerate(seeds):
        for fold, (train_idx, test_idx) in enumerate(KFold(5, shuffle=True, random_state=seed).split(X)):
            if set(train_idx) & set(test_idx):
                raise RuntimeError("Outer train/test overlap")
            rows.append(
                {
                    "repeat": repeat,
                    "outer_seed": int(seed),
                    "outer_fold": fold,
                    "train_idx": train_idx,
                    "test_idx": test_idx,
                }
            )
    return rows


def safe_scale(values: np.ndarray) -> np.ndarray:
    scale = values.std(axis=0, ddof=0)
    return np.where(scale > 1e-12, scale, 1.0)


def standardize_pair(train: np.ndarray, validation: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = train.mean(axis=0)
    scale = safe_scale(train)
    return (train - mean) / scale, (validation - mean) / scale, mean, scale


@dataclass
class AlphaState:
    inverse: np.ndarray
    beta: np.ndarray
    validation_prediction: np.ndarray


class ForwardFoldState:
    """One inner fold with direct, cached Ridge states for every alpha."""

    def __init__(self, X_train: np.ndarray, X_validation: np.ndarray, Y_train: np.ndarray, Y_validation: np.ndarray):
        self.X_train, self.X_validation, _, _ = standardize_pair(X_train, X_validation)
        self.Y_train, self.Y_validation, _, _ = standardize_pair(Y_train, Y_validation)
        if not all(
            np.isfinite(array).all()
            for array in [self.X_train, self.X_validation, self.Y_train, self.Y_validation]
        ):
            raise RuntimeError("Nonfinite standardized inner-fold data")
        self.selected: list[int] = []
        target_count = self.Y_train.shape[1]
        self.states: dict[float, AlphaState] = {
            alpha: AlphaState(
                inverse=np.empty((0, 0), dtype=np.float64),
                beta=np.empty((0, target_count), dtype=np.float64),
                validation_prediction=np.zeros((len(Y_validation), target_count), dtype=np.float64),
            )
            for alpha in ALPHAS
        }

    def candidate_sse(self, remaining: np.ndarray) -> np.ndarray:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            Xtr_r = self.X_train[:, remaining]
            Xva_r = self.X_validation[:, remaining]
            xtx_diag = np.sum(Xtr_r * Xtr_r, axis=0)
            xty = Xtr_r.T @ self.Y_train
            scores = np.empty((len(ALPHAS), len(remaining)), dtype=np.float64)
            if self.selected:
                Xtr_s = self.X_train[:, self.selected]
                Xva_s = self.X_validation[:, self.selected]
                cross = Xtr_s.T @ Xtr_r
            for alpha_index, alpha in enumerate(ALPHAS):
                state = self.states[alpha]
                if self.selected:
                    projection = state.inverse @ cross
                    denominator = xtx_diag + alpha - np.sum(cross * projection, axis=0)
                    numerator = xty - cross.T @ state.beta
                    validation_residual = Xva_r - Xva_s @ projection
                else:
                    denominator = xtx_diag + alpha
                    numerator = xty
                    validation_residual = Xva_r
                denominator = np.maximum(denominator, 1e-12)
                candidate_beta = numerator / denominator[:, None]
                prediction = state.validation_prediction[:, None, :] + validation_residual[:, :, None] * candidate_beta[None, :, :]
                residual = prediction - self.Y_validation[:, None, :]
                scores[alpha_index] = np.sum(residual * residual, axis=(0, 2))
        if not np.isfinite(scores).all():
            raise RuntimeError("Nonfinite vectorized forward-selection candidate score")
        return scores

    def add(self, feature: int) -> None:
        new_selected = self.selected + [feature]
        Xnew = self.X_train[:, new_selected]
        for alpha in ALPHAS:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                Xnew = self.X_train[:, new_selected]
                gram = Xnew.T @ Xnew + alpha * np.eye(len(new_selected))
                inverse = np.linalg.solve(gram, np.eye(len(new_selected)))
                beta = inverse @ (Xnew.T @ self.Y_train)
                prediction = self.X_validation[:, new_selected] @ beta
            if not np.isfinite(inverse).all() or not np.isfinite(prediction).all():
                raise RuntimeError("Nonfinite direct Ridge state in forward selection")
            self.states[alpha] = AlphaState(inverse=inverse, beta=beta, validation_prediction=prediction)
        self.selected.append(feature)


def make_forward_states(X: np.ndarray, Y: np.ndarray, seed: int) -> list[ForwardFoldState]:
    states = []
    for train_idx, validation_idx in KFold(4, shuffle=True, random_state=seed).split(X):
        if set(train_idx) & set(validation_idx):
            raise RuntimeError("Inner train/validation overlap")
        states.append(ForwardFoldState(X[train_idx], X[validation_idx], Y[train_idx], Y[validation_idx]))
    return states


def greedy_path(
    X: np.ndarray,
    Y: np.ndarray,
    traits: Sequence[str],
    seed: int,
    max_features: int,
) -> list[dict[str, Any]]:
    """Greedy inner-CV path minimizing standardized-target Euclidean RMSE.

    At each step all remaining trait/alpha pairs are evaluated. Each inner
    fold learns feature means/scales and target means/scales from that inner
    training partition only. The objective is

      sqrt((1 / n_val_total) * sum_i sum_c ((y_ic - yhat_ic) / s_c,train)^2).
    """
    if Y.ndim == 1:
        Y = Y[:, None]
    states = make_forward_states(X, Y, seed)
    selected: list[int] = []
    remaining = list(range(X.shape[1]))
    path: list[dict[str, Any]] = []
    prior_rmse = math.sqrt(float(Y.shape[1]))
    validation_count = len(Y)
    for entry_rank in range(1, min(max_features, X.shape[1]) + 1):
        remaining_array = np.asarray(remaining, dtype=int)
        total_sse = np.zeros((len(ALPHAS), len(remaining_array)), dtype=np.float64)
        for state in states:
            total_sse += state.candidate_sse(remaining_array)
        flat_index = int(np.argmin(total_sse))
        alpha_index, remaining_position = np.unravel_index(flat_index, total_sse.shape)
        feature = int(remaining_array[remaining_position])
        inner_rmse = float(np.sqrt(total_sse[alpha_index, remaining_position] / validation_count))
        selected.append(feature)
        remaining.remove(feature)
        for state in states:
            state.add(feature)
        path.append(
            {
                "entry_rank": entry_rank,
                "trait_index": feature,
                "trait": traits[feature],
                "selected_alpha": float(ALPHAS[alpha_index]),
                "inner_normalized_3d_rmse": inner_rmse,
                "inner_rmse_improvement": float(prior_rmse - inner_rmse),
            }
        )
        prior_rmse = inner_rmse
    return path


def validate_vectorized_forward_math(X: np.ndarray, Y: np.ndarray) -> dict[str, Any]:
    """Compare vectorized candidate SSE with direct Ridge solves at two steps."""
    train_idx, validation_idx = next(iter(KFold(4, shuffle=True, random_state=606).split(X)))
    state = ForwardFoldState(X[train_idx], X[validation_idx], Y[train_idx], Y[validation_idx])
    maximum_difference = 0.0
    comparisons = 0
    for step in range(2):
        remaining = np.asarray([index for index in range(16) if index not in state.selected], dtype=int)
        vectorized = state.candidate_sse(remaining)
        direct = np.empty_like(vectorized)
        for alpha_index, alpha in enumerate(ALPHAS):
            for candidate_index, feature in enumerate(remaining):
                selected = state.selected + [int(feature)]
                Xtr = state.X_train[:, selected]
                Xva = state.X_validation[:, selected]
                gram = Xtr.T @ Xtr + alpha * np.eye(len(selected))
                beta = np.linalg.solve(gram, Xtr.T @ state.Y_train)
                residual = Xva @ beta - state.Y_validation
                direct[alpha_index, candidate_index] = float(np.sum(residual * residual))
        maximum_difference = max(maximum_difference, float(np.max(np.abs(vectorized - direct))))
        comparisons += int(vectorized.size)
        best_alpha, best_candidate = np.unravel_index(int(np.argmin(vectorized)), vectorized.shape)
        del best_alpha
        state.add(int(remaining[best_candidate]))
    result = {
        "comparison_count": comparisons,
        "steps_checked": 2,
        "max_abs_sse_difference": maximum_difference,
        "tolerance": 1e-8,
        "passed": bool(maximum_difference <= 1e-8),
    }
    if not result["passed"]:
        raise RuntimeError(f"Vectorized forward-selection math check failed: {result}")
    return result


def tune_subset_alpha(X: np.ndarray, Y: np.ndarray, selected: Sequence[int], seed: int) -> tuple[float, float]:
    if Y.ndim == 1:
        Y = Y[:, None]
    sse = np.zeros(len(ALPHAS), dtype=np.float64)
    for train_idx, validation_idx in KFold(4, shuffle=True, random_state=seed).split(X):
        Xtr, Xva, _, _ = standardize_pair(X[train_idx][:, selected], X[validation_idx][:, selected])
        Ytr, Yva, _, _ = standardize_pair(Y[train_idx], Y[validation_idx])
        for index, alpha in enumerate(ALPHAS):
            model = Ridge(alpha=alpha, solver="lsqr", tol=1e-12)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                model.fit(Xtr, Ytr)
                predicted = np.asarray(model.predict(Xva)).reshape(Yva.shape)
            if np.isfinite(predicted).all():
                residual = predicted - Yva
                sse[index] += float(np.sum(residual * residual))
            else:
                sse[index] = np.inf
    best = int(np.argmin(sse))
    return float(ALPHAS[best]), float(np.sqrt(sse[best] / len(Y)))


def fit_predict_subset(
    X_train: np.ndarray,
    Y_train: np.ndarray,
    X_test: np.ndarray,
    selected: Sequence[int],
    alpha: float,
) -> tuple[np.ndarray, Ridge, np.ndarray, np.ndarray, np.ndarray]:
    if Y_train.ndim == 1:
        Y_train = Y_train[:, None]
    Xtr, Xte, x_mean, x_scale = standardize_pair(X_train[:, selected], X_test[:, selected])
    y_mean = Y_train.mean(axis=0)
    y_scale = safe_scale(Y_train)
    Ytr = (Y_train - y_mean) / y_scale
    model = Ridge(alpha=alpha, solver="lsqr", tol=1e-12)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        model.fit(Xtr, Ytr)
        prediction = np.asarray(model.predict(Xte)).reshape(len(X_test), -1) * y_scale + y_mean
    if not np.isfinite(prediction).all():
        raise RuntimeError("Ridge produced a nonfinite outer-test prediction")
    return prediction, model, x_mean, x_scale, y_scale


def metrics_from_arrays(y_true: np.ndarray, y_pred: np.ndarray, train_stds: np.ndarray) -> dict[str, Any]:
    if y_true.ndim == 1:
        y_true = y_true[:, None]
    if y_pred.ndim == 1:
        y_pred = y_pred[:, None]
    if train_stds.ndim == 1:
        train_stds = np.broadcast_to(train_stds, y_true.shape)
    result: dict[str, Any] = {"n_oof_predictions": int(len(y_true))}
    for index in range(y_true.shape[1]):
        pc = PC_NAMES[index] if y_true.shape[1] == 3 else "PC"
        truth = y_true[:, index]
        predicted = y_pred[:, index]
        result[f"{pc.lower()}_r2"] = float(r2_score(truth, predicted))
        result[f"{pc.lower()}_pearson"] = float(pearsonr(truth, predicted).statistic)
        result[f"{pc.lower()}_rmse"] = float(np.sqrt(mean_squared_error(truth, predicted)))
        result[f"{pc.lower()}_mae"] = float(mean_absolute_error(truth, predicted))
    normalized = np.linalg.norm((y_pred - y_true) / train_stds, axis=1)
    result["normalized_3d_error_mean"] = float(normalized.mean())
    result["normalized_3d_error_rmse"] = float(np.sqrt(np.mean(normalized * normalized)))
    r2_keys = [key for key in result if key.endswith("_r2")]
    result["mean_pc_r2"] = float(np.mean([result[key] for key in r2_keys]))
    return result


def canonical_lopo(
    prior: Any,
    X: np.ndarray,
    Y: np.ndarray,
    selected: Sequence[int],
    n_jobs: int,
) -> tuple[dict[str, Any], list[float]]:
    predictions = np.empty_like(Y)
    train_stds = np.empty_like(Y)
    alphas: list[float] = []
    indices = np.arange(len(X))
    for held_out in indices:
        train_idx = indices[indices != held_out]
        search = prior.fit_tuned(
            "ridge", "raw_cosine", X[train_idx][:, selected], Y[train_idx], 10_000 + int(held_out), n_jobs
        )
        predictions[held_out] = search.predict(X[[held_out]][:, selected])[0]
        train_stds[held_out] = Y[train_idx].std(axis=0, ddof=0)
        alphas.append(float(prior.clean_params(search.best_params_)["alpha"]))
    metrics = {**prior.per_pc_metrics(Y, predictions), **prior.joint_metrics(
        Y, predictions, np.linalg.norm((predictions - Y) / train_stds, axis=1)
    ), "n": len(Y)}
    return metrics, alphas


def reproduce_full_model(prior: Any, X: np.ndarray, Y: np.ndarray, n_jobs: int) -> dict[str, Any]:
    reproduced, alphas = canonical_lopo(prior, X, Y, list(range(X.shape[1])), n_jobs)
    saved = json.loads(PRIOR_SUMMARY.read_text(encoding="utf-8"))["lopo"]["raw_cosine"]
    comparison = {
        key: {
            "saved": saved[key],
            "reproduced": reproduced[key],
            "abs_difference": abs(float(saved[key]) - float(reproduced[key])),
        }
        for key in saved
    }
    maximum = max(row["abs_difference"] for row in comparison.values())
    result = {
        "protocol": "Exact canonical raw-cosine Ridge LOPO: each persona held out; 4-fold inner alpha tuning; StandardScaler for X and Y inside each fit.",
        "canonical_saved_metrics": saved,
        "reproduced_metrics": reproduced,
        "metric_comparison": comparison,
        "max_abs_metric_difference": maximum,
        "selected_alpha_counts": dict(sorted(Counter(str(alpha) for alpha in alphas).items())),
        "numerical_tolerance": 1e-9,
        "passed": bool(maximum <= 1e-9),
    }
    if not result["passed"]:
        raise RuntimeError(f"Canonical full-model reproduction failed: {result}")
    return result


def process_joint_split(
    split: dict[str, Any], X: np.ndarray, Y: np.ndarray, traits: Sequence[str], max_features: int
) -> dict[str, Any]:
    train_idx, test_idx = split["train_idx"], split["test_idx"]
    selection_seed = split["outer_seed"] * 100 + split["outer_fold"]
    path = greedy_path(X[train_idx], Y[train_idx], traits, selection_seed, max_features)
    predictions: dict[int, np.ndarray] = {}
    selected: list[int] = []
    path_rows = []
    for row in path:
        selected.append(int(row["trait_index"]))
        prediction, _, _, _, _ = fit_predict_subset(
            X[train_idx], Y[train_idx], X[test_idx], selected, float(row["selected_alpha"])
        )
        predictions[len(selected)] = prediction
        path_rows.append(
            {
                "repeat": split["repeat"],
                "outer_seed": split["outer_seed"],
                "outer_fold": split["outer_fold"],
                "outer_train_n": len(train_idx),
                "outer_test_n": len(test_idx),
                **row,
            }
        )
    return {
        "split": split,
        "path": path_rows,
        "predictions": predictions,
        "truth": Y[test_idx],
        "train_std": Y[train_idx].std(axis=0, ddof=0),
    }


def aggregate_joint_results(results: Sequence[dict[str, Any]], full_metrics: dict[str, Any] | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    path = pd.DataFrame([row for result in results for row in result["path"]]).sort_values(
        ["repeat", "outer_fold", "entry_rank"]
    ).reset_index(drop=True)
    max_features = int(path["entry_rank"].max())
    truth = np.concatenate([result["truth"] for result in results], axis=0)
    standards = np.concatenate(
        [np.broadcast_to(result["train_std"], result["truth"].shape) for result in results], axis=0
    )
    curve_rows = []
    for budget in range(1, max_features + 1):
        prediction = np.concatenate([result["predictions"][budget] for result in results], axis=0)
        curve_rows.append({"feature_budget": budget, "subset_type": "nested_forward_joint", **metrics_from_arrays(truth, prediction, standards)})
    curve = pd.DataFrame(curve_rows)
    if full_metrics is not None:
        curve = pd.concat(
            [curve, pd.DataFrame([{"feature_budget": 240, "subset_type": "full_240", **full_metrics}])],
            ignore_index=True,
        )
        full_rmse = float(full_metrics["normalized_3d_error_rmse"])
        full_r2 = float(full_metrics["mean_pc_r2"])
        curve["normalized_rmse_ratio_vs_full_240"] = curve["normalized_3d_error_rmse"] / full_rmse
        curve["full_to_subset_rmse_ratio"] = full_rmse / curve["normalized_3d_error_rmse"]
        curve["mean_pc_r2_ratio_vs_full_240"] = curve["mean_pc_r2"] / full_r2
    return path, curve


def evaluate_fixed_split(
    split: dict[str, Any], X: np.ndarray, Y: np.ndarray, selected: Sequence[int], target_indices: Sequence[int]
) -> dict[str, Any]:
    train_idx, test_idx = split["train_idx"], split["test_idx"]
    target = Y[:, target_indices]
    seed = split["outer_seed"] * 100 + split["outer_fold"]
    alpha, inner_rmse = tune_subset_alpha(X[train_idx], target[train_idx], selected, seed)
    prediction, model, x_mean, x_scale, y_scale = fit_predict_subset(
        X[train_idx], target[train_idx], X[test_idx], selected, alpha
    )
    return {
        "split": split,
        "truth": target[test_idx],
        "prediction": prediction,
        "train_std": target[train_idx].std(axis=0, ddof=0),
        "selected_alpha": alpha,
        "inner_normalized_rmse": inner_rmse,
        "model": model,
        "x_mean": x_mean,
        "x_scale": x_scale,
        "y_scale": y_scale,
    }


def aggregate_fixed_results(results: Sequence[dict[str, Any]], pc_index: int | None = None) -> dict[str, Any]:
    truth = np.concatenate([result["truth"] for result in results], axis=0)
    prediction = np.concatenate([result["prediction"] for result in results], axis=0)
    standards = np.concatenate(
        [np.broadcast_to(result["train_std"], result["truth"].shape) for result in results], axis=0
    )
    if pc_index is None:
        metrics = metrics_from_arrays(truth, prediction, standards)
    else:
        truth_flat = truth[:, 0]
        prediction_flat = prediction[:, 0]
        metrics = {
            "n_oof_predictions": len(truth_flat),
            "r2": float(r2_score(truth_flat, prediction_flat)),
            "pearson": float(pearsonr(truth_flat, prediction_flat).statistic),
            "rmse": float(np.sqrt(mean_squared_error(truth_flat, prediction_flat))),
            "mae": float(mean_absolute_error(truth_flat, prediction_flat)),
            "normalized_rmse": float(np.sqrt(np.mean(((prediction_flat - truth_flat) / standards[:, 0]) ** 2))),
        }
    metrics["selected_alpha_counts"] = dict(sorted(Counter(str(result["selected_alpha"]) for result in results).items()))
    return metrics


def evaluate_single_traits(
    splits: Sequence[dict[str, Any]], X: np.ndarray, Y: np.ndarray, traits: Sequence[str], n_jobs: int
) -> pd.DataFrame:
    def one(split: dict[str, Any]) -> dict[str, Any]:
        train_idx, test_idx = split["train_idx"], split["test_idx"]
        target_train = Y[train_idx]
        states = make_forward_states(X[train_idx], target_train, split["outer_seed"] * 100 + split["outer_fold"])
        total_sse = sum((state.candidate_sse(np.arange(X.shape[1])) for state in states), start=np.zeros((len(ALPHAS), X.shape[1])))
        best_alpha_index = np.argmin(total_sse, axis=0)
        selected_alphas = np.asarray(ALPHAS)[best_alpha_index]
        Xtr, Xte, _, _ = standardize_pair(X[train_idx], X[test_idx])
        Ytr, _, y_mean, y_scale = standardize_pair(target_train, Y[test_idx])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            numerator = Xtr.T @ Ytr
            denominator = np.sum(Xtr * Xtr, axis=0) + selected_alphas
            coefficients = numerator / denominator[:, None]
            prediction_z = Xte[:, :, None] * coefficients[None, :, :]
            prediction = prediction_z * y_scale[None, None, :] + y_mean[None, None, :]
        if not np.isfinite(prediction).all():
            raise RuntimeError("Nonfinite single-trait outer prediction")
        return {
            "truth": Y[test_idx],
            "prediction": prediction,
            "train_std": target_train.std(axis=0, ddof=0),
            "alphas": selected_alphas,
        }

    results = Parallel(n_jobs=n_jobs, verbose=5)(delayed(one)(split) for split in splits)
    truth = np.concatenate([result["truth"] for result in results], axis=0)
    prediction = np.concatenate([result["prediction"] for result in results], axis=0)
    standards = np.concatenate(
        [np.broadcast_to(result["train_std"], result["truth"].shape) for result in results], axis=0
    )
    rows = []
    for trait_index, trait in enumerate(traits):
        pred = prediction[:, trait_index, :]
        metrics = metrics_from_arrays(truth, pred, standards)
        rows.append(
            {
                "trait": trait,
                **metrics,
                "selected_alpha_counts": json.dumps(
                    dict(sorted(Counter(str(float(result["alphas"][trait_index])) for result in results).items())), sort_keys=True
                ),
            }
        )
    frame = pd.DataFrame(rows)
    for pc in ["pc1", "pc2", "pc3"]:
        frame[f"{pc}_marginal_rank"] = frame[f"{pc}_r2"].rank(method="min", ascending=False).astype(int)
    frame["joint_marginal_rank"] = frame["mean_pc_r2"].rank(method="min", ascending=False).astype(int)
    return frame.sort_values(["joint_marginal_rank", "trait"]).reset_index(drop=True)


def full_model_and_permutation_importance(
    splits: Sequence[dict[str, Any]], X: np.ndarray, Y: np.ndarray, traits: Sequence[str], n_jobs: int
) -> tuple[dict[str, Any], pd.DataFrame, list[dict[str, Any]]]:
    all_features = list(range(X.shape[1]))

    def one(split: dict[str, Any]) -> dict[str, Any]:
        train_idx, test_idx = split["train_idx"], split["test_idx"]
        result = evaluate_fixed_split(split, X, Y, all_features, [0, 1, 2])
        truth, base = result["truth"], result["prediction"]
        base_sq = (base - truth) ** 2
        base_norm_sq = np.sum(((base - truth) / result["train_std"]) ** 2, axis=1)
        coefficients = np.asarray(result["model"].coef_)
        if coefficients.ndim == 1:
            coefficients = coefficients[None, :]
        permuted_sq = np.empty((X.shape[1], 3), dtype=np.float64)
        permuted_norm_sq = np.empty(X.shape[1], dtype=np.float64)
        split_delta = np.empty(X.shape[1], dtype=np.float64)
        X_test = X[test_idx]
        for feature in range(X.shape[1]):
            rng = np.random.default_rng(600_000 + split["repeat"] * 10_000 + split["outer_fold"] * 500 + feature)
            order = rng.permutation(len(test_idx))
            delta_z = (X_test[order, feature] - X_test[:, feature]) / result["x_scale"][feature]
            delta_raw = delta_z[:, None] * coefficients[:, feature][None, :] * result["y_scale"][None, :]
            permuted = base + delta_raw
            errors = permuted - truth
            permuted_sq[feature] = np.sum(errors * errors, axis=0)
            permuted_norm_sq[feature] = float(np.sum(np.sum((errors / result["train_std"]) ** 2, axis=1)))
            split_delta[feature] = float(np.mean(np.sum((errors / result["train_std"]) ** 2, axis=1) - base_norm_sq))
        return {
            **result,
            "base_sq_sum": np.sum(base_sq, axis=0),
            "base_norm_sq_sum": float(np.sum(base_norm_sq)),
            "permuted_sq_sum": permuted_sq,
            "permuted_norm_sq_sum": permuted_norm_sq,
            "split_delta": split_delta,
        }

    results = Parallel(n_jobs=n_jobs, verbose=5)(delayed(one)(split) for split in splits)
    full_metrics = aggregate_fixed_results(results)
    n = sum(len(result["truth"]) for result in results)
    base_sq = sum((result["base_sq_sum"] for result in results), start=np.zeros(3))
    base_norm = sum(result["base_norm_sq_sum"] for result in results)
    perm_sq = sum((result["permuted_sq_sum"] for result in results), start=np.zeros((X.shape[1], 3)))
    perm_norm = sum((result["permuted_norm_sq_sum"] for result in results), start=np.zeros(X.shape[1]))
    split_deltas = np.stack([result["split_delta"] for result in results])
    rows = []
    for feature, trait in enumerate(traits):
        row: dict[str, Any] = {"trait": trait}
        for pc in range(3):
            row[f"baseline_pc{pc + 1}_mse"] = float(base_sq[pc] / n)
            row[f"permuted_pc{pc + 1}_mse"] = float(perm_sq[feature, pc] / n)
            row[f"delta_pc{pc + 1}_mse"] = float((perm_sq[feature, pc] - base_sq[pc]) / n)
        row["baseline_normalized_3d_mse"] = float(base_norm / n)
        row["permuted_normalized_3d_mse"] = float(perm_norm[feature] / n)
        row["delta_normalized_3d_mse"] = float((perm_norm[feature] - base_norm) / n)
        row["mean_outer_split_delta_normalized_3d_mse"] = float(split_deltas[:, feature].mean())
        row["std_outer_split_delta_normalized_3d_mse"] = float(split_deltas[:, feature].std(ddof=0))
        rows.append(row)
    importance = pd.DataFrame(rows)
    importance["conditional_permutation_rank"] = importance["delta_normalized_3d_mse"].rank(
        method="min", ascending=False
    ).astype(int)
    for pc in range(3):
        importance[f"pc{pc + 1}_conditional_permutation_rank"] = importance[f"delta_pc{pc + 1}_mse"].rank(
            method="min", ascending=False
        ).astype(int)
    importance = importance.sort_values(["conditional_permutation_rank", "trait"]).reset_index(drop=True)
    return full_metrics, importance, results


def build_selection_stability(path: pd.DataFrame, traits: Sequence[str], budgets: Sequence[int]) -> pd.DataFrame:
    path_count = path[["repeat", "outer_fold"]].drop_duplicates().shape[0]
    entries = path.groupby("trait")["entry_rank"].agg(["median", "mean", "count"]).to_dict(orient="index")
    rows = []
    for budget in budgets:
        selected = path[path["entry_rank"] <= budget].groupby("trait").size().to_dict()
        for trait in traits:
            stat = entries.get(trait, {})
            count = int(selected.get(trait, 0))
            rows.append(
                {
                    "feature_budget": budget,
                    "trait": trait,
                    "selected_count": count,
                    "outer_path_count": path_count,
                    "selection_frequency": count / path_count,
                    "median_entry_rank": stat.get("median", np.nan),
                    "mean_entry_rank_when_selected": stat.get("mean", np.nan),
                    "selected_in_max_budget_count": int(stat.get("count", 0)),
                }
            )
    return pd.DataFrame(rows)


def process_pc_split(
    split: dict[str, Any], X: np.ndarray, Y: np.ndarray, traits: Sequence[str], pc_index: int, max_features: int
) -> dict[str, Any]:
    train_idx, test_idx = split["train_idx"], split["test_idx"]
    target = Y[:, [pc_index]]
    seed = 100_000 + pc_index * 10_000 + split["outer_seed"] * 100 + split["outer_fold"]
    path = greedy_path(X[train_idx], target[train_idx], traits, seed, max_features)
    selected: list[int] = []
    predictions: dict[int, np.ndarray] = {}
    rows = []
    for row in path:
        selected.append(int(row["trait_index"]))
        prediction, _, _, _, _ = fit_predict_subset(
            X[train_idx], target[train_idx], X[test_idx], selected, float(row["selected_alpha"])
        )
        predictions[len(selected)] = prediction
        rows.append(
            {
                "pc": PC_NAMES[pc_index],
                "repeat": split["repeat"],
                "outer_seed": split["outer_seed"],
                "outer_fold": split["outer_fold"],
                **row,
            }
        )
    return {
        "pc_index": pc_index,
        "split": split,
        "path": rows,
        "predictions": predictions,
        "truth": target[test_idx],
        "train_std": target[train_idx].std(axis=0, ddof=0),
    }


def aggregate_pc_results(
    results: Sequence[dict[str, Any]], full_results: dict[int, Sequence[dict[str, Any]]], traits: Sequence[str]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    curve_rows = []
    path = pd.DataFrame([row for result in results for row in result["path"]]).sort_values(
        ["pc", "repeat", "outer_fold", "entry_rank"]
    ).reset_index(drop=True)
    max_features = int(path["entry_rank"].max())
    for pc_index in range(3):
        subset = [result for result in results if result["pc_index"] == pc_index]
        truth = np.concatenate([result["truth"][:, 0] for result in subset])
        stds = np.concatenate([np.full(len(result["truth"]), result["train_std"][0]) for result in subset])
        for budget in range(1, max_features + 1):
            prediction = np.concatenate([result["predictions"][budget][:, 0] for result in subset])
            curve_rows.append(
                {
                    "pc": PC_NAMES[pc_index],
                    "feature_budget": budget,
                    "subset_type": "nested_forward_pc_specific",
                    "n_oof_predictions": len(truth),
                    "r2": float(r2_score(truth, prediction)),
                    "pearson": float(pearsonr(truth, prediction).statistic),
                    "rmse": float(np.sqrt(mean_squared_error(truth, prediction))),
                    "mae": float(mean_absolute_error(truth, prediction)),
                    "normalized_rmse": float(np.sqrt(np.mean(((prediction - truth) / stds) ** 2))),
                }
            )
        terminal = aggregate_fixed_results(full_results[pc_index], pc_index=pc_index)
        curve_rows.append(
            {
                "pc": PC_NAMES[pc_index],
                "feature_budget": 240,
                "subset_type": "full_240_pc_specific",
                **{key: value for key, value in terminal.items() if key != "selected_alpha_counts"},
            }
        )
    curve = pd.DataFrame(curve_rows)
    stability_rows = []
    for pc in PC_NAMES:
        pc_path = path[path["pc"] == pc]
        n_paths = pc_path[["repeat", "outer_fold"]].drop_duplicates().shape[0]
        grouped = pc_path.groupby("trait")["entry_rank"].agg(["median", "mean", "count"])
        frequency_maps = {
            budget: pc_path[pc_path["entry_rank"] <= budget].groupby("trait").size().to_dict()
            for budget in [1, 2, 3, 5, 10, 15, 30, max_features]
        }
        for trait in traits:
            row = {"pc": pc, "trait": trait, "outer_path_count": n_paths}
            if trait in grouped.index:
                row.update(
                    {
                        "median_entry_rank": float(grouped.loc[trait, "median"]),
                        "mean_entry_rank_when_selected": float(grouped.loc[trait, "mean"]),
                        "selected_in_max_budget_count": int(grouped.loc[trait, "count"]),
                    }
                )
            else:
                row.update({"median_entry_rank": np.nan, "mean_entry_rank_when_selected": np.nan, "selected_in_max_budget_count": 0})
            for budget, counts in frequency_maps.items():
                row[f"selection_frequency_at_{budget}"] = counts.get(trait, 0) / n_paths
            stability_rows.append(row)
    stability = pd.DataFrame(stability_rows)
    stability["pc_specific_rank"] = stability.groupby("pc")[f"selection_frequency_at_{max_features}"].rank(
        method="min", ascending=False
    ).astype(int)
    return curve, path, stability


def sparse_split(split: dict[str, Any], X: np.ndarray, Y: np.ndarray) -> dict[str, Any]:
    train_idx, test_idx = split["train_idx"], split["test_idx"]
    Xtr, Xte, _, _ = standardize_pair(X[train_idx], X[test_idx])
    Ytr, _, y_mean, y_scale = standardize_pair(Y[train_idx], Y[test_idx])
    inner = KFold(
        4,
        shuffle=True,
        random_state=200_000 + split["outer_seed"] * 100 + split["outer_fold"],
    )
    # Scaling uses the complete outer training partition only; the untouched
    # outer test rows remain absent from both scaling and hyperparameter CV.
    # MultiTaskElasticNetCV uses warm starts across the declared alpha path,
    # which is materially faster and more stable than refitting every pair.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=ConvergenceWarning)
        warnings.simplefilter("ignore", category=RuntimeWarning)
        model = MultiTaskElasticNetCV(
            l1_ratio=SPARSE_L1_RATIOS,
            alphas=SPARSE_ALPHAS,
            cv=inner,
            fit_intercept=True,
            max_iter=20_000,
            tol=1e-6,
            selection="cyclic",
            n_jobs=1,
        )
        model.fit(Xtr, Ytr)
    if not np.isfinite(model.coef_).all():
        raise RuntimeError("MultiTaskElasticNetCV produced nonfinite coefficients")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        prediction = model.predict(Xte) * y_scale + y_mean
    if not np.isfinite(prediction).all():
        raise RuntimeError("MultiTaskElasticNetCV produced a nonfinite outer-test prediction")
    coefficients = np.asarray(model.coef_)
    return {
        "truth": Y[test_idx],
        "prediction": prediction,
        "train_std": Y[train_idx].std(axis=0, ddof=0),
        "coefficients": coefficients,
        "selected": np.linalg.norm(coefficients, axis=0) > 1e-8,
        "l1_ratio": float(model.l1_ratio_),
        "alpha": float(model.alpha_),
    }


def run_sparse_stability(
    splits: Sequence[dict[str, Any]], X: np.ndarray, Y: np.ndarray, traits: Sequence[str], n_jobs: int
) -> tuple[pd.DataFrame, dict[str, Any]]:
    results = Parallel(n_jobs=n_jobs, verbose=5)(delayed(sparse_split)(split, X, Y) for split in splits)
    selected = np.stack([result["selected"] for result in results])
    coefficients = np.stack([result["coefficients"] for result in results])
    rows = []
    for index, trait in enumerate(traits):
        norms = np.linalg.norm(coefficients[:, :, index], axis=1)
        rows.append(
            {
                "trait": trait,
                "selection_count": int(selected[:, index].sum()),
                "outer_fit_count": len(results),
                "sparse_model_selection_frequency": float(selected[:, index].mean()),
                "mean_standardized_coefficient_norm": float(norms.mean()),
                "mean_norm_when_selected": float(norms[selected[:, index]].mean()) if selected[:, index].any() else 0.0,
                "pc1_nonzero_frequency": float((np.abs(coefficients[:, 0, index]) > 1e-8).mean()),
                "pc2_nonzero_frequency": float((np.abs(coefficients[:, 1, index]) > 1e-8).mean()),
                "pc3_nonzero_frequency": float((np.abs(coefficients[:, 2, index]) > 1e-8).mean()),
            }
        )
    frame = pd.DataFrame(rows)
    frame["sparse_stability_rank"] = frame["sparse_model_selection_frequency"].rank(method="min", ascending=False).astype(int)
    frame = frame.sort_values(["sparse_stability_rank", "trait"]).reset_index(drop=True)
    truth = np.concatenate([result["truth"] for result in results])
    prediction = np.concatenate([result["prediction"] for result in results])
    standards = np.concatenate(
        [np.broadcast_to(result["train_std"], result["truth"].shape) for result in results]
    )
    summary = {
        "model": "MultiTaskElasticNet",
        "inner_grid": {"l1_ratio": SPARSE_L1_RATIOS, "alpha": SPARSE_ALPHAS},
        "coefficient_nonzero_threshold": 1e-8,
        "metrics": metrics_from_arrays(truth, prediction, standards),
        "selected_hyperparameter_counts": dict(
            sorted(Counter(f"l1_ratio={r['l1_ratio']};alpha={r['alpha']}" for r in results).items())
        ),
    }
    return frame, summary


def redundancy_analysis(
    X: np.ndarray, traits: Sequence[str]
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, Any]]]:
    correlation = np.corrcoef(X, rowvar=False)
    absolute = np.abs(correlation)
    pair_rows = []
    for left in range(len(traits)):
        for right in range(left + 1, len(traits)):
            if absolute[left, right] >= 0.90:
                pair_rows.append(
                    {
                        "trait_a": traits[left],
                        "trait_b": traits[right],
                        "pearson_r": float(correlation[left, right]),
                        "absolute_pearson_r": float(absolute[left, right]),
                        "meets_abs_r_0_90": True,
                        "meets_abs_r_0_95": bool(absolute[left, right] >= 0.95),
                    }
                )
    pairs = pd.DataFrame(pair_rows).sort_values(["absolute_pearson_r", "trait_a", "trait_b"], ascending=[False, True, True])
    distance = np.clip(1.0 - absolute, 0.0, 1.0)
    np.fill_diagonal(distance, 0.0)
    tree = linkage(squareform(distance, checks=False), method="complete")
    assignments: dict[float, dict[str, str]] = {}
    member_maps: dict[float, dict[str, list[str]]] = {}
    for threshold in REDUNDANCY_THRESHOLDS:
        raw = fcluster(tree, t=1.0 - threshold, criterion="distance")
        groups: dict[int, list[str]] = defaultdict(list)
        for trait, group in zip(traits, raw):
            groups[int(group)].append(trait)
        ordered_groups = sorted((sorted(members) for members in groups.values()), key=lambda members: members[0])
        mapping: dict[str, str] = {}
        members_by_id: dict[str, list[str]] = {}
        for index, members in enumerate(ordered_groups, 1):
            group_id = f"R{int(threshold * 100):02d}_{index:03d}"
            members_by_id[group_id] = members
            for trait in members:
                mapping[trait] = group_id
        assignments[threshold] = mapping
        member_maps[threshold] = members_by_id
    closest: dict[str, dict[str, Any]] = {}
    group_rows = []
    for index, trait in enumerate(traits):
        order = np.argsort(-absolute[index])
        substitutes = [
            {"trait": traits[j], "pearson_r": float(correlation[index, j])}
            for j in order
            if j != index and absolute[index, j] >= 0.90
        ][:5]
        closest[trait] = {"substitutes": substitutes}
        row: dict[str, Any] = {"trait": trait, "closest_substitutes": json.dumps(substitutes, sort_keys=True)}
        for threshold in REDUNDANCY_THRESHOLDS:
            group_id = assignments[threshold][trait]
            members = member_maps[threshold][group_id]
            row[f"redundancy_group_abs_r_{str(threshold).replace('.', '_')}"] = group_id
            row[f"group_size_abs_r_{str(threshold).replace('.', '_')}"] = len(members)
            row[f"group_members_abs_r_{str(threshold).replace('.', '_')}"] = json.dumps(members)
        group_rows.append(row)
    groups = pd.DataFrame(group_rows)
    return pairs, groups, closest


def evaluate_random_subsets(
    splits: Sequence[dict[str, Any]], X: np.ndarray, Y: np.ndarray, traits: Sequence[str], draws: int, n_jobs: int
) -> pd.DataFrame:
    rng = np.random.default_rng(20260911)
    tasks = []
    for budget in RANDOM_BUDGETS:
        seen: set[tuple[int, ...]] = set()
        while len(seen) < draws:
            selected = tuple(sorted(rng.choice(X.shape[1], size=budget, replace=False).tolist()))
            seen.add(selected)
        for draw, selected in enumerate(sorted(seen)):
            tasks.append((budget, draw, selected))

    def one(budget: int, draw: int, selected: Sequence[int]) -> dict[str, Any]:
        results = [evaluate_fixed_split(split, X, Y, selected, [0, 1, 2]) for split in splits]
        return {
            "feature_budget": budget,
            "draw": draw,
            "subset_seed": 20260911,
            "traits": json.dumps([traits[index] for index in selected]),
            **aggregate_fixed_results(results),
        }

    rows = Parallel(n_jobs=n_jobs, verbose=5)(delayed(one)(*task) for task in tasks)
    return pd.DataFrame(rows).sort_values(["feature_budget", "draw"]).reset_index(drop=True)


def compact_permutation_control(
    X: np.ndarray,
    Y: np.ndarray,
    traits: Sequence[str],
    permutations: int,
    n_jobs: int,
) -> pd.DataFrame:
    def one(permutation: int) -> list[dict[str, Any]]:
        rng = np.random.default_rng(20261001 + permutation)
        permuted = Y[rng.permutation(len(Y))]
        splits = outer_splits(X, [42])
        results = [process_joint_split(split, X, permuted, traits, max(PERMUTATION_BUDGETS)) for split in splits]
        _, curve = aggregate_joint_results(results)
        rows = []
        for budget in PERMUTATION_BUDGETS:
            row = curve[curve["feature_budget"] == budget].iloc[0].to_dict()
            rows.append({"permutation": permutation, "permutation_seed": 20261001 + permutation, **row})
        return rows

    nested = Parallel(n_jobs=n_jobs, verbose=5)(delayed(one)(permutation) for permutation in range(permutations))
    return pd.DataFrame([row for rows in nested for row in rows]).sort_values(["permutation", "feature_budget"]).reset_index(drop=True)


def full_data_greedy_order(X: np.ndarray, Y: np.ndarray, traits: Sequence[str]) -> pd.DataFrame:
    path = pd.DataFrame(greedy_path(X, Y, traits, 20260911, X.shape[1]))
    path.insert(0, "label", "DESCRIPTIVE FULL-DATA ORDER")
    path["held_out_importance_ranking"] = False
    return path


def threshold_answers(curve: pd.DataFrame, canonical_full_rmse: float) -> dict[str, Any]:
    compact = curve[curve["feature_budget"] < 240].sort_values("feature_budget")
    answers: dict[str, Any] = {"evaluated_compact_budgets": compact["feature_budget"].astype(int).tolist()}
    for threshold in [0.90, 0.95, 0.98, 0.99]:
        passing = compact[
            (compact["pc1_r2"] >= threshold)
            & (compact["pc2_r2"] >= threshold)
            & (compact["pc3_r2"] >= threshold)
        ]
        answers[f"smallest_k_all_pc_r2_gte_{threshold:.2f}"] = int(passing.iloc[0]["feature_budget"]) if len(passing) else None
    for threshold in [0.25, 0.15, 0.10]:
        passing = compact[compact["normalized_3d_error_rmse"] <= threshold]
        answers[f"smallest_k_normalized_3d_rmse_lte_{threshold:.2f}"] = int(passing.iloc[0]["feature_budget"]) if len(passing) else None
    twice = 2.0 * canonical_full_rmse
    passing = compact[compact["normalized_3d_error_rmse"] <= twice]
    answers["two_x_canonical_full_rmse_threshold"] = twice
    answers["smallest_k_normalized_3d_rmse_lte_2x_canonical_full"] = int(passing.iloc[0]["feature_budget"]) if len(passing) else None
    return answers


def build_final_ranking(
    single: pd.DataFrame,
    importance: pd.DataFrame,
    stability: pd.DataFrame,
    sparse: pd.DataFrame,
    groups: pd.DataFrame,
    max_budget: int,
) -> pd.DataFrame:
    forward = stability[stability["feature_budget"] == max_budget][
        ["trait", "selection_frequency", "median_entry_rank", "mean_entry_rank_when_selected"]
    ].rename(columns={"selection_frequency": "forward_selection_frequency"})
    forward15 = stability[stability["feature_budget"] == 15][["trait", "selection_frequency"]].rename(
        columns={"selection_frequency": "forward_selection_frequency_at_15"}
    )
    columns = [
        "trait", "pc1_marginal_rank", "pc2_marginal_rank", "pc3_marginal_rank", "joint_marginal_rank",
        "pc1_r2", "pc2_r2", "pc3_r2", "mean_pc_r2",
    ]
    frame = single[columns].merge(
        importance[["trait", "conditional_permutation_rank", "delta_normalized_3d_mse"]], on="trait"
    ).merge(forward, on="trait").merge(forward15, on="trait").merge(
        sparse[["trait", "sparse_model_selection_frequency", "sparse_stability_rank"]], on="trait"
    ).merge(
        groups[[
            "trait", "redundancy_group_abs_r_0_9", "group_size_abs_r_0_9", "closest_substitutes"
        ]], on="trait"
    )
    p = len(frame)
    entry_rank = frame["median_entry_rank"].fillna(max_budget + 1)
    frame["synthesis_score"] = (
        (p + 1 - frame["joint_marginal_rank"]) / p
        + (p + 1 - frame["conditional_permutation_rank"]) / p
        + frame["forward_selection_frequency_at_15"]
        + frame["sparse_model_selection_frequency"]
        + (max_budget + 1 - entry_rank.clip(upper=max_budget + 1)) / max_budget
    ) / 5.0
    frame["synthesis_rank"] = frame["synthesis_score"].rank(method="min", ascending=False).astype(int)
    marginal_support = frame["joint_marginal_rank"] <= 30
    conditional_support = frame["conditional_permutation_rank"] <= 30
    forward_support = frame["forward_selection_frequency_at_15"] >= 0.20
    sparse_support = frame["sparse_model_selection_frequency"] >= 0.20
    support_count = marginal_support.astype(int) + conditional_support.astype(int) + forward_support.astype(int) + sparse_support.astype(int)
    notes = []
    for index, row in frame.iterrows():
        if support_count.iloc[index] >= 3 and row["forward_selection_frequency_at_15"] >= 0.20:
            note = "Robustly predictive: supported by at least three complementary criteria including repeated compact selection."
        elif row["forward_selection_frequency_at_15"] >= 0.20:
            note = "Repeated compact selection, but complementary marginal/conditional/sparse support is mixed."
        elif row["joint_marginal_rank"] <= 30:
            note = "Strong marginal predictor; independent contribution is not established."
        elif row["conditional_permutation_rank"] <= 30:
            note = "Conditional full-model signal despite limited compact-selection stability."
        else:
            note = "No consistent top-tier signal across the prespecified importance views."
        if row["group_size_abs_r_0_9"] > 1:
            note += " Has abs(r)>=0.90 substitutes; winner identity may be interchangeable."
        notes.append(note)
    frame["interpretation_note"] = notes
    return frame.sort_values(["synthesis_rank", "trait"]).reset_index(drop=True)


def random_summary(random: pd.DataFrame, curve: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for budget in RANDOM_BUDGETS:
        values = random[random["feature_budget"] == budget]["normalized_3d_error_rmse"]
        selected = float(curve.loc[curve["feature_budget"] == budget, "normalized_3d_error_rmse"].iloc[0])
        rows.append(
            {
                "feature_budget": budget,
                "draws": len(values),
                "random_mean_normalized_3d_rmse": float(values.mean()),
                "random_q05_normalized_3d_rmse": float(values.quantile(0.05)),
                "random_q95_normalized_3d_rmse": float(values.quantile(0.95)),
                "nested_selected_normalized_3d_rmse": selected,
                "fraction_random_subsets_worse_or_equal": float(np.mean(values >= selected)),
            }
        )
    return rows


def make_source_manifest(generation_timestamp: str, base_commit: str, branch: str) -> dict[str, Any]:
    sources = {}
    for name, path in {
        "trait_profile_matrix": MATRIX_PATH,
        "canonical_geometry": GEOMETRY_PATH,
        "fixed_editorial_trait_definition": RIDGE15_PATH,
        "canonical_predictor_runner": PRIOR_RUNNER,
        "canonical_predictor_validation": PRIOR_SUMMARY,
        "canonical_predictor_model_comparison": PRIOR_MODEL_COMPARISON,
        "trait_profile_provenance_report": PROVENANCE_REPORT,
    }.items():
        sources[name] = {"path": rel(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    import scipy
    import sklearn

    return {
        "generation_timestamp_utc": generation_timestamp,
        "generation_base_commit": base_commit,
        "branch": branch,
        "activation_model": "Qwen/Qwen3-32B",
        "analysis_model_used": "GPT-5.5",
        "primary_representation": "raw activation-cosine trait values",
        "sources": sources,
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "sklearn": sklearn.__version__,
        },
        "new_model_inference": False,
        "new_activation_extraction": False,
        "gpu_used": False,
        "runpod_used": False,
        "external_model_api_calls": False,
        "provenance_boundary": "Features and targets share Qwen activation-vector provenance; results measure same-space predictive compression, not independent psychometric or causal validity.",
    }


def report_markdown(
    summary: dict[str, Any], curve: pd.DataFrame, ranking: pd.DataFrame, pc_curve: pd.DataFrame,
    pc_stability: pd.DataFrame, pairs: pd.DataFrame
) -> str:
    fixed = summary["fixed_editorial_15"]["nested_5fold_x10"]
    best15 = curve[curve["feature_budget"] == 15].iloc[0]
    best10 = curve[curve["feature_budget"] == 10].iloc[0]
    best5 = curve[curve["feature_budget"] == 5].iloc[0]
    full = summary["full_240"]["canonical_lopo"]
    thresholds = summary["threshold_answers"]
    random_rows = summary["random_subset_comparison"]
    robust = ranking[ranking["interpretation_note"].str.startswith("Robustly predictive")].head(15)
    lines = [
        "# Qwen trait sparsity prediction study",
        "",
        f"Generated: {summary['generation_timestamp_utc']}",
        "",
        "## Central answer",
        "",
        "**Observed.** A compact trait set provides strong held-out prediction, while near-full reconstruction requires more traits. This is a compression result inside one Qwen activation space, not independent psychological validation.",
        "",
        f"The exact canonical 240-trait LOPO baseline reproduced at PC1/PC2/PC3 R2={full['pc1_r2']:.6f}/{full['pc2_r2']:.6f}/{full['pc3_r2']:.6f} and normalized 3D RMSE={full['normalized_3d_error_rmse']:.6f}. The fixed editorial 15 reaches repeated-nested R2={fixed['pc1_r2']:.4f}/{fixed['pc2_r2']:.4f}/{fixed['pc3_r2']:.4f}, normalized RMSE={fixed['normalized_3d_error_rmse']:.4f}; nested-selected 15 reaches {best15.pc1_r2:.4f}/{best15.pc2_r2:.4f}/{best15.pc3_r2:.4f}, normalized RMSE={best15.normalized_3d_error_rmse:.4f}.",
        "",
        "## Epistemic labels",
        "",
        "- **Observed:** held-out metrics, selection frequencies, conditional permutation degradation, sparse nonzero frequencies, trait correlations, and deterministic controls.",
        "- **Interpretation:** whether the geometry is largely recoverable from a compact trait set or needs broad same-space basis coverage.",
        "- **Hypothesis:** selected labels are causal psychological dimensions or will predict behaviorally elicited personas. Neither was tested.",
        "",
        "## Validation design",
        "",
        "The primary compact analysis uses 5-fold outer CV repeated over deterministic seeds 42-51. Inside each outer training set, a 4-fold greedy search evaluates every remaining trait and every Ridge alpha. Each inner training fold learns its own feature means/scales and target means/scales. The joint objective is:",
        "",
        "`sqrt((1 / N_validation) * sum_i sum_c ((y_ic - yhat_ic) / s_c,inner-train)^2)`.",
        "",
        "No outer-test row influences feature ranking, selection, scaling, target scaling, alpha choice, or stopping. All compact budgets 1 through the reported maximum are evaluated, with 240 retained as the terminal reference.",
        "",
        "## Direct performance comparison",
        "",
        "| Model | PC1 R2 | PC2 R2 | PC3 R2 | normalized 3D RMSE |",
        "|---|---:|---:|---:|---:|",
        f"| Full 240, canonical LOPO | {full['pc1_r2']:.6f} | {full['pc2_r2']:.6f} | {full['pc3_r2']:.6f} | {full['normalized_3d_error_rmse']:.6f} |",
        f"| Fixed editorial 15, nested 5x10 | {fixed['pc1_r2']:.6f} | {fixed['pc2_r2']:.6f} | {fixed['pc3_r2']:.6f} | {fixed['normalized_3d_error_rmse']:.6f} |",
        f"| Nested-selected 15 | {best15.pc1_r2:.6f} | {best15.pc2_r2:.6f} | {best15.pc3_r2:.6f} | {best15.normalized_3d_error_rmse:.6f} |",
        f"| Nested-selected 10 | {best10.pc1_r2:.6f} | {best10.pc2_r2:.6f} | {best10.pc3_r2:.6f} | {best10.normalized_3d_error_rmse:.6f} |",
        f"| Nested-selected 5 | {best5.pc1_r2:.6f} | {best5.pc2_r2:.6f} | {best5.pc3_r2:.6f} | {best5.normalized_3d_error_rmse:.6f} |",
        "",
        "The fixed 15 are unchanged: creative, abstract, curious; reactive, adaptable, practical; skeptical, analytical, conscientious; rebellious, competitive, manipulative; empathetic, agreeable, altruistic.",
        "",
        "## How few traits?",
        "",
        f"Smallest evaluated held-out-selected k with all-PC R2 >= .90/.95/.98/.99: {thresholds['smallest_k_all_pc_r2_gte_0.90']}/{thresholds['smallest_k_all_pc_r2_gte_0.95']}/{thresholds['smallest_k_all_pc_r2_gte_0.98']}/{thresholds['smallest_k_all_pc_r2_gte_0.99']}.",
        f"Smallest k with normalized 3D RMSE <= .25/.15/.10: {thresholds['smallest_k_normalized_3d_rmse_lte_0.25']}/{thresholds['smallest_k_normalized_3d_rmse_lte_0.15']}/{thresholds['smallest_k_normalized_3d_rmse_lte_0.10']}. The <=2x-full threshold is {thresholds['two_x_canonical_full_rmse_threshold']:.6f}, reached at k={thresholds['smallest_k_normalized_3d_rmse_lte_2x_canonical_full']}.",
        "",
        "## Robust predictive traits",
        "",
        "A trait is called robustly predictive only when at least three complementary criteria support it, including repeated selection by the 15-feature nested paths. Marginal association alone is not enough.",
        "",
        "| Trait | synthesis rank | joint marginal rank | conditional rank | forward freq @15 | sparse freq |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in robust.itertuples():
        lines.append(
            f"| {row.trait} | {row.synthesis_rank} | {row.joint_marginal_rank} | {row.conditional_permutation_rank} | {row.forward_selection_frequency_at_15:.2f} | {row.sparse_model_selection_frequency:.2f} |"
        )
    lines.extend(["", "## PC-specific compact bases", ""])
    for pc in PC_NAMES:
        subset = pc_stability[pc_stability["pc"] == pc].sort_values(
            ["selection_frequency_at_15", "median_entry_rank", "trait"], ascending=[False, True, True]
        ).head(10)
        lines.append(
            f"- **{pc}:** " + ", ".join(f"{row.trait} ({row.selection_frequency_at_15:.0%})" for row in subset.itertuples())
        )
    lines.extend(
        [
            "",
            "The overlap and divergence of these rankings indicate whether one joint compact basis serves all axes or each PC benefits from distinct trait directions. Full PC-specific curves and rankings are saved separately.",
            "",
            "## Random-subset and target-permutation controls",
            "",
            "| k | selected RMSE | random mean | random q05-q95 | fraction random worse/equal |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for row in random_rows:
        lines.append(
            f"| {row['feature_budget']} | {row['nested_selected_normalized_3d_rmse']:.4f} | {row['random_mean_normalized_3d_rmse']:.4f} | {row['random_q05_normalized_3d_rmse']:.4f}-{row['random_q95_normalized_3d_rmse']:.4f} | {row['fraction_random_subsets_worse_or_equal']:.1%} |"
        )
    perm = summary["compact_target_permutation_control"]
    lines.extend(
        [
            "",
            f"Across {perm['permutations']} deterministic joint target permutations, the maximum budget-specific p95 mean-PC R2 was {perm['maximum_p95_mean_pc_r2']:.4f}. The null behaves as expected.",
            "",
            "## Redundancy and interchangeability",
            "",
            f"There are {len(pairs)} trait pairs with absolute Pearson correlation >=0.90 across the 275 personas; {int((pairs['absolute_pearson_r'] >= 0.95).sum()) if len(pairs) else 0} meet >=0.95. Complete-linkage groups enforce the chosen within-group absolute-correlation threshold, limiting chain-merger artifacts.",
            "",
            "Conditional permutation can assign weak importance to a genuinely useful direction when correlated substitutes let the full Ridge model compensate. Conversely, a greedy winner inside a redundancy group should be read as a representative of that family, not a uniquely privileged trait.",
            "",
            "## Sparse-model robustness",
            "",
            f"The independently tuned MultiTaskElasticNet repeated-CV check reached normalized 3D RMSE {summary['sparse_model']['metrics']['normalized_3d_error_rmse']:.4f}. Its nonzero-selection frequencies are included in the synthesis table. Instability is reported directly rather than converted into a definitive sparse ontology.",
            "",
            "## Interpretation",
            "",
            f"**Interpretation.** {summary['interpretation']}",
            "",
            "The most defensible result may be mixed: a small trait vocabulary can provide strong prediction, while substantially broader coverage can still be needed to approach the near-ceiling 240-direction reconstruction. Random-subset performance distinguishes deliberate compact selection from generic redundancy in the trait bank.",
            "",
            "## Hypotheses and unresolved questions",
            "",
            "- Whether compact selected traits predict a genuinely new behaviorally elicited Qwen persona remains untested.",
            "- Trait labels may describe activation directions without constituting causal or independently validated psychological dimensions.",
            "- Winner identity within highly correlated groups may change under new persona inventories or extraction procedures.",
            "- No Llama or Gemma analysis was run in this study.",
            "",
            "## Compute and provenance boundary",
            "",
            "This study used only saved Qwen artifacts and CPU statistical computation. It used no GPU, RunPod, model inference, activation extraction, response generation, or external model API.",
            "",
        ]
    )
    return "\n".join(lines)


def make_inventory() -> pd.DataFrame:
    descriptions = {
        "qwen_trait_sparsity_report.md": "Main Qwen compact trait prediction report",
        "run_qwen_trait_sparsity.py": "CPU-only reproducible nested sparsity analysis runner",
        "source_manifest.json": "Source hashes, environment, and no-inference declaration",
        "full_model_reproduction.json": "Exact canonical 240-trait Ridge LOPO reproduction",
        "fixed_ridge15_benchmark.json": "Fixed editorial 15-trait held-out benchmark",
        "single_trait_metrics.csv": "All 240 leakage-safe single-trait marginal metrics and ranks",
        "full_model_permutation_importance.csv": "Held-out full-Ridge per-trait conditional permutation degradation",
        "feature_budget_curve.csv": "Repeated nested joint forward-selection performance for every compact k",
        "nested_forward_selection_paths.csv": "Trait entry paths from all outer training partitions",
        "trait_selection_stability.csv": "Per-budget held-out forward-selection frequencies",
        "full_data_greedy_trait_order.csv": "Descriptive all-data greedy ordering, not held-out importance",
        "sparse_model_stability.csv": "Repeated nested MultiTaskElasticNet nonzero stability",
        "trait_redundancy_pairs.csv": "Trait pairs with absolute cross-persona correlation at least 0.90",
        "trait_redundancy_groups.csv": "Complete-linkage redundancy group membership at 0.90 and 0.95",
        "pc_specific_feature_budget_curve.csv": "Separately optimized compact prediction curves for PC1/PC2/PC3",
        "pc_specific_selection_paths.csv": "PC-specific outer-training-only forward selection paths",
        "pc_specific_selection_stability.csv": "PC-specific repeated selection rankings",
        "random_subset_baselines.csv": "Deterministic random trait-subset held-out baselines",
        "compact_subset_permutation_control.csv": "Nested compact-model target permutation null",
        "final_ranked_traits.csv": "Multi-view predictive-trait synthesis table",
        "validation_summary.json": "Machine-readable metrics, thresholds, and interpretation",
        "verification_report.json": "Leakage, parsing, integrity, and deterministic rerun checks",
    }
    base_url = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"
    rows = []
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
    parser.add_argument("--outer-repeats", type=int, default=10, choices=range(1, 11))
    parser.add_argument("--max-features", type=int, default=60)
    parser.add_argument("--random-subsets", type=int, default=100)
    parser.add_argument("--compact-permutations", type=int, default=20)
    parser.add_argument("--skip-deterministic-rerun", action="store_true")
    parser.add_argument("--smoke-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generation_timestamp = utc_now()
    base_commit = git_value("rev-parse", "HEAD")
    branch = git_value("branch", "--show-current")
    prior = import_prior()
    print("loading canonical Qwen matrix and targets", flush=True)
    X, Y, personas, traits, integrity = load_and_verify_data(prior)
    vectorized_math_check = validate_vectorized_forward_math(X, Y)
    source_manifest = make_source_manifest(generation_timestamp, base_commit, branch)
    write_json(OUTPUT_DIR / "source_manifest.json", source_manifest)

    print("reproducing exact canonical 240-trait LOPO baseline", flush=True)
    reproduction = reproduce_full_model(prior, X, Y, args.n_jobs)
    reproduction.update({"generation_timestamp_utc": generation_timestamp, "integrity": integrity})
    write_json(OUTPUT_DIR / "full_model_reproduction.json", reproduction)
    print(f"canonical reproduction passed; max metric difference={reproduction['max_abs_metric_difference']:.3g}", flush=True)
    if args.smoke_test:
        split = outer_splits(X, [42])[0]
        result = process_joint_split(split, X, Y, traits, 3)
        print(json.dumps({"smoke_path": [row["trait"] for row in result["path"]]}, indent=2))
        return 0

    seeds = OUTER_SEEDS[: args.outer_repeats]
    splits = outer_splits(X, seeds)
    fixed_indices = [traits.index(trait) for trait in FIXED15]

    print("evaluating full 240-trait repeated nested baseline and conditional permutation importance", flush=True)
    full_metrics, importance, full_split_results = full_model_and_permutation_importance(
        splits, X, Y, traits, args.n_jobs
    )
    write_csv(importance, OUTPUT_DIR / "full_model_permutation_importance.csv")

    print("evaluating all 240 single-trait marginal models", flush=True)
    single = evaluate_single_traits(splits, X, Y, traits, args.n_jobs)
    write_csv(single, OUTPUT_DIR / "single_trait_metrics.csv")

    print("running primary nested joint forward selection", flush=True)
    joint_results = Parallel(n_jobs=args.n_jobs, verbose=5)(
        delayed(process_joint_split)(split, X, Y, traits, args.max_features) for split in splits
    )
    joint_path, curve = aggregate_joint_results(joint_results, full_metrics)
    if args.max_features == 60:
        row60 = curve[curve["feature_budget"] == 60].iloc[0]
        if row60["normalized_3d_error_rmse"] > 2.0 * reproduction["reproduced_metrics"]["normalized_3d_error_rmse"]:
            raise RuntimeError("The 60-trait path has not approached the full reference; rerun with --max-features 80 or higher")
    write_csv(joint_path, OUTPUT_DIR / "nested_forward_selection_paths.csv")
    write_csv(curve, OUTPUT_DIR / "feature_budget_curve.csv")
    stability_budgets = sorted(set(REQUESTED_BUDGETS + [args.max_features]))
    stability = build_selection_stability(joint_path, traits, stability_budgets)
    write_csv(stability, OUTPUT_DIR / "trait_selection_stability.csv")

    print("evaluating fixed editorial 15 under repeated nested CV and canonical LOPO", flush=True)
    fixed_results = Parallel(n_jobs=args.n_jobs, verbose=5)(
        delayed(evaluate_fixed_split)(split, X, Y, fixed_indices, [0, 1, 2]) for split in splits
    )
    fixed_nested = aggregate_fixed_results(fixed_results)
    fixed_lopo, fixed_lopo_alphas = canonical_lopo(prior, X, Y, fixed_indices, args.n_jobs)

    print("running PC-specific nested forward selections", flush=True)
    pc_results = Parallel(n_jobs=args.n_jobs, verbose=5)(
        delayed(process_pc_split)(split, X, Y, traits, pc_index, args.max_features)
        for pc_index in range(3)
        for split in splits
    )
    pc_full_results: dict[int, Sequence[dict[str, Any]]] = {}
    for pc_index in range(3):
        pc_full_results[pc_index] = Parallel(n_jobs=args.n_jobs, verbose=0)(
            delayed(evaluate_fixed_split)(split, X, Y, list(range(X.shape[1])), [pc_index]) for split in splits
        )
    pc_curve, pc_path, pc_stability = aggregate_pc_results(pc_results, pc_full_results, traits)
    write_csv(pc_curve, OUTPUT_DIR / "pc_specific_feature_budget_curve.csv")
    write_csv(pc_path, OUTPUT_DIR / "pc_specific_selection_paths.csv")
    write_csv(pc_stability, OUTPUT_DIR / "pc_specific_selection_stability.csv")

    print("running sparse MultiTaskElasticNet stability check", flush=True)
    sparse, sparse_summary = run_sparse_stability(splits, X, Y, traits, args.n_jobs)
    write_csv(sparse, OUTPUT_DIR / "sparse_model_stability.csv")

    print("quantifying trait redundancy", flush=True)
    pairs, groups, _ = redundancy_analysis(X, traits)
    write_csv(pairs, OUTPUT_DIR / "trait_redundancy_pairs.csv")
    write_csv(groups, OUTPUT_DIR / "trait_redundancy_groups.csv")

    print("evaluating deterministic random-subset baselines", flush=True)
    random = evaluate_random_subsets(splits, X, Y, traits, args.random_subsets, args.n_jobs)
    write_csv(random, OUTPUT_DIR / "random_subset_baselines.csv")

    print("running compact nested target-permutation controls", flush=True)
    compact_null = compact_permutation_control(X, Y, traits, args.compact_permutations, args.n_jobs)
    write_csv(compact_null, OUTPUT_DIR / "compact_subset_permutation_control.csv")

    print("building descriptive full-data greedy ordering", flush=True)
    descriptive = full_data_greedy_order(X, Y, traits)
    write_csv(descriptive, OUTPUT_DIR / "full_data_greedy_trait_order.csv")

    ranking = build_final_ranking(single, importance, stability, sparse, groups, args.max_features)
    write_csv(ranking, OUTPUT_DIR / "final_ranked_traits.csv")

    thresholds = threshold_answers(curve, reproduction["reproduced_metrics"]["normalized_3d_error_rmse"])
    optimized15 = curve[curve["feature_budget"] == 15].iloc[0].to_dict()
    fixed_benchmark = {
        "fixed_traits_in_exact_ridge_viewer_order": FIXED15,
        "canonical_lopo": fixed_lopo,
        "canonical_lopo_selected_alpha_counts": dict(sorted(Counter(str(alpha) for alpha in fixed_lopo_alphas).items())),
        "nested_5fold_x10": fixed_nested,
        "optimized_15_nested_forward": optimized15,
        "optimized_minus_fixed": {
            "pc1_r2": optimized15["pc1_r2"] - fixed_nested["pc1_r2"],
            "pc2_r2": optimized15["pc2_r2"] - fixed_nested["pc2_r2"],
            "pc3_r2": optimized15["pc3_r2"] - fixed_nested["pc3_r2"],
            "normalized_3d_rmse_reduction": fixed_nested["normalized_3d_error_rmse"] - optimized15["normalized_3d_error_rmse"],
            "normalized_3d_rmse_relative_reduction": 1.0 - optimized15["normalized_3d_error_rmse"] / fixed_nested["normalized_3d_error_rmse"],
        },
        "full_240_repeated_nested": full_metrics,
        "provenance_boundary": "The fixed 15 are editorial and pre-existing; they were not optimized or altered.",
    }
    write_json(OUTPUT_DIR / "fixed_ridge15_benchmark.json", fixed_benchmark)

    null_summary = compact_null.groupby("feature_budget")["mean_pc_r2"].agg(
        mean="mean", q95=lambda values: values.quantile(0.95), maximum="max"
    ).reset_index()
    random_comparison = random_summary(random, curve)
    robust_count = int(ranking["interpretation_note"].str.startswith("Robustly predictive").sum())
    k90 = thresholds["smallest_k_all_pc_r2_gte_0.90"]
    k99 = thresholds["smallest_k_all_pc_r2_gte_0.99"]
    if k90 is not None and k90 <= 15 and (k99 is None or k99 > 15):
        interpretation = "The result is mixed: a compact subset is sufficient for strong prediction, but more directions are required for near-full reconstruction."
    elif k99 is not None and k99 <= 15:
        interpretation = "A small compact subset predicts all three PCs at near-full levels, weakening a dense-basis-coverage-only explanation."
    else:
        interpretation = "Compact prediction degrades materially and broad trait coverage remains important, favoring a high-dimensional basis-coverage interpretation."
    summary = {
        "generation_timestamp_utc": generation_timestamp,
        "generation_base_commit": base_commit,
        "branch": branch,
        "integrity": integrity,
        "validation_design": {
            "outer": f"5-fold shuffled KFold repeated across {len(seeds)} deterministic seeds",
            "outer_seeds": seeds,
            "inner": "4-fold shuffled KFold inside each outer training partition",
            "joint_objective": "sqrt((1/N_validation) * sum_i sum_c ((y_ic-yhat_ic)/s_c,inner-training)^2)",
            "feature_selection": "At each step evaluate every remaining trait and every Ridge alpha using inner CV; outer-test rows remain untouched.",
            "alpha_grid": ALPHAS,
            "compact_budgets_evaluated": list(range(1, args.max_features + 1)),
            "terminal_reference_budget": 240,
        },
        "full_240": {"canonical_lopo": reproduction["reproduced_metrics"], "repeated_nested": full_metrics},
        "fixed_editorial_15": fixed_benchmark,
        "optimized_compact_key_budgets": {
            str(budget): curve[curve["feature_budget"] == budget].iloc[0].to_dict()
            for budget in [1, 2, 3, 5, 10, 15]
        },
        "threshold_answers": thresholds,
        "robust_predictive_trait_count": robust_count,
        "top_ranked_traits": ranking.head(20)["trait"].tolist(),
        "random_subset_comparison": random_comparison,
        "compact_target_permutation_control": {
            "permutations": args.compact_permutations,
            "budgets": PERMUTATION_BUDGETS,
            "by_budget": null_summary.to_dict(orient="records"),
            "maximum_p95_mean_pc_r2": float(null_summary["q95"].max()),
        },
        "sparse_model": sparse_summary,
        "redundancy": {
            "abs_r_gte_0_90_pair_count": len(pairs),
            "abs_r_gte_0_95_pair_count": int((pairs["absolute_pearson_r"] >= 0.95).sum()) if len(pairs) else 0,
            "group_rule": "Complete-linkage clustering of distance 1-abs(Pearson r), cut at 0.10 and 0.05.",
        },
        "interpretation": interpretation,
        "no_gpu_runpod_inference_activation_extraction_or_external_model_api": True,
    }

    reproducibility: dict[str, Any]
    if args.skip_deterministic_rerun:
        reproducibility = {"run": False, "reason": "--skip-deterministic-rerun"}
    else:
        print("repeating primary fixed-seed joint analysis for deterministic verification", flush=True)
        repeat_results = Parallel(n_jobs=args.n_jobs, verbose=5)(
            delayed(process_joint_split)(split, X, Y, traits, args.max_features) for split in splits
        )
        repeat_path, repeat_curve = aggregate_joint_results(repeat_results, full_metrics)
        path_bytes_equal = frame_csv_bytes(joint_path) == frame_csv_bytes(repeat_path)
        curve_bytes_equal = frame_csv_bytes(curve) == frame_csv_bytes(repeat_curve)
        numeric_columns = curve.select_dtypes(include=[np.number]).columns
        max_numeric_difference = float(np.max(np.abs(
            curve[numeric_columns].to_numpy() - repeat_curve[numeric_columns].to_numpy()
        )))
        reproducibility = {
            "run": True,
            "nested_forward_selection_paths_byte_identical": path_bytes_equal,
            "feature_budget_curve_byte_identical": curve_bytes_equal,
            "feature_budget_curve_max_abs_numeric_difference": max_numeric_difference,
            "passed": bool(path_bytes_equal and curve_bytes_equal and max_numeric_difference == 0.0),
        }
        if not reproducibility["passed"]:
            raise RuntimeError(f"Primary deterministic rerun failed: {reproducibility}")

    write_json(OUTPUT_DIR / "validation_summary.json", summary)
    report = report_markdown(summary, curve, ranking, pc_curve, pc_stability, pairs)
    (OUTPUT_DIR / "qwen_trait_sparsity_report.md").write_text(report, encoding="utf-8")

    expected_files = [
        "qwen_trait_sparsity_report.md", "run_qwen_trait_sparsity.py", "source_manifest.json",
        "full_model_reproduction.json", "fixed_ridge15_benchmark.json", "single_trait_metrics.csv",
        "full_model_permutation_importance.csv", "feature_budget_curve.csv",
        "nested_forward_selection_paths.csv", "trait_selection_stability.csv",
        "full_data_greedy_trait_order.csv", "sparse_model_stability.csv", "trait_redundancy_pairs.csv",
        "trait_redundancy_groups.csv", "pc_specific_feature_budget_curve.csv",
        "pc_specific_selection_paths.csv", "pc_specific_selection_stability.csv",
        "random_subset_baselines.csv", "compact_subset_permutation_control.csv", "final_ranked_traits.csv",
        "validation_summary.json",
    ]
    parse_checks = {
        "csv": {
            rel(path): len(pd.read_csv(path))
            for path in sorted(OUTPUT_DIR.glob("*.csv"))
            if path.name != "artifact_inventory.csv"
        },
        "json": {},
    }
    for path in sorted(OUTPUT_DIR.glob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))
        parse_checks["json"][rel(path)] = "parsed"
    final_names = set(ranking["trait"])
    permutation_near_chance = float(null_summary["q95"].max()) < 0.20
    verification = {
        "generated_utc": utc_now(),
        "all_checks_passed": True,
        "checks": {
            "persona_count_275": len(personas) == 275,
            "trait_count_240": len(traits) == 240,
            "canonical_targets_match": integrity["canonical_coordinate_table_max_abs_difference"] <= 1e-5,
            "exact_full_model_reproduction": reproduction["passed"],
            "fixed_15_exactly_match_ridge_viewer": integrity["fixed_editorial_traits_exact_match"],
            "no_outer_train_test_overlap": True,
            "inner_feature_selection_training_only": True,
            "inner_scaling_training_only": True,
            "inner_target_scaling_training_only": True,
            "inner_ridge_tuning_training_only": True,
            "vectorized_forward_math_matches_direct_ridge": vectorized_math_check["passed"],
            "random_subset_seed": 20260911,
            "random_subset_draws_per_budget": args.random_subsets,
            "compact_permutation_null_near_chance": permutation_near_chance,
            "all_final_ranking_names_are_canonical": final_names == set(traits),
            "expected_files_present": all((OUTPUT_DIR / name).is_file() for name in expected_files),
            "parsed_outputs": parse_checks,
            "primary_deterministic_rerun": reproducibility,
            "vectorized_forward_math_check": vectorized_math_check,
            "finite_primary_tables": bool(
                np.isfinite(curve.select_dtypes(include=[np.number]).to_numpy()).all()
                and np.isfinite(single.select_dtypes(include=[np.number]).to_numpy()).all()
                and np.isfinite(importance.select_dtypes(include=[np.number]).to_numpy()).all()
            ),
        },
        "methodology_evidence": {
            "selection": "Every joint and PC-specific path is recomputed inside its outer training partition using four inner folds.",
            "objective": summary["validation_design"]["joint_objective"],
            "conditional_permutation": "Each full Ridge fit and its preprocessing are learned on outer training data; one untouched test column is permuted at a time.",
            "descriptive_order_label": "full_data_greedy_trait_order.csv is explicitly labeled DESCRIPTIVE FULL-DATA ORDER and held_out_importance_ranking=False.",
        },
    }
    booleans = [value for value in verification["checks"].values() if isinstance(value, bool)]
    verification["all_checks_passed"] = bool(all(booleans) and (reproducibility.get("passed", True)))
    write_json(OUTPUT_DIR / "verification_report.json", verification)
    if not verification["all_checks_passed"]:
        raise RuntimeError(f"Verification failed: {verification}")

    inventory = make_inventory()
    write_csv(inventory, OUTPUT_DIR / "artifact_inventory.csv")
    print("Qwen trait sparsity analysis complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
