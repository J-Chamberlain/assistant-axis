#!/usr/bin/env python3
"""Build preregistered model-only validation and aggregate human projections."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.neighbors import KNeighborsRegressor


HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[2]
MODELS = ["qwen", "llama", "gemma"]
MODEL_LABEL = {"qwen": "Qwen 3 32B", "llama": "LLaMA 3.3 70B", "gemma": "Gemma 2 27B"}
TRAIT_COUNTS = [12, 45]
ELIGIBLE_K = {4, 5, 6, 7, 8, 10}
ALPHAS = np.power(10.0, np.arange(-6, 7))
KNN_K = [3, 5, 7, 10, 15, 25, 40]
KNN_WEIGHTS = ["uniform", "distance"]
OUTER_SEED = 120927
FINAL_SEED = 120928
BOOTSTRAP_SEEDS = {
    12: {"qwen": 121201, "llama": 121202, "gemma": 121203},
    45: {"qwen": 451201, "llama": 451202, "gemma": 451203},
}
N_BOOT = 500
METHOD_COMMIT = "5852980"
TERRAIN_FINAL = "103c13ea692ed7e1c9cb8309bfc8b150171e7b40"
TERRAIN_NUMERICAL = "9335ffaeac215cfdbb709b041c1fa1db0d8f754e"

HUMAN = {
    12: ROOT / "research/outputs/human_model_profile_correspondence/human_trait_profiles_12.csv",
    45: ROOT / "research/outputs/human_model_profile_correspondence/human_trait_profiles_45.csv",
}
ROLE_MATRIX = {
    "qwen": ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
    "llama": ROOT / "research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv",
    "gemma": ROOT / "research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv",
}
COORDS = ROOT / "research/outputs/model_coverage_terrain_viewer/role_coordinates.csv"
COVERAGE = ROOT / "research/outputs/model_coverage_terrain_viewer/coverage_region_summary.csv"
FAMILY = ROOT / "research/outputs/model_coverage_terrain_viewer/family_terrain_summary.csv"
ALIGNMENT_GIT_PATH = "research/outputs/human_supported_trait_convergence/procrustes_alignment_matrices.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, float_format="%.12g", lineterminator="\n")


def git_json(path: str) -> dict:
    payload = subprocess.run(
        ["git", "show", f"HEAD:{path}"], cwd=ROOT, check=True, capture_output=True
    ).stdout
    return json.loads(payload)


def ordered_traits(count: int) -> list[str]:
    frame = pd.read_csv(HUMAN[count])
    traits = frame.loc[frame.profile_id.eq(frame.profile_id.iloc[0]), "trait"].tolist()
    if len(traits) != count or len(set(traits)) != count:
        raise ValueError(f"invalid frozen {count}-trait order")
    if set(frame.trait) != set(traits):
        raise ValueError(f"trait mismatch in human {count} source")
    return traits


def shape_transform(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = values.mean(axis=1, keepdims=True)
    centered = values - mean
    norm = np.linalg.norm(centered, axis=1, keepdims=True)
    if not np.isfinite(norm).all() or np.any(norm <= 0):
        raise ValueError("zero or nonfinite centered trait-profile norm")
    return centered / norm, mean[:, 0], norm[:, 0]


def role_data(model: str, count: int) -> tuple[list[str], list[str], np.ndarray, np.ndarray, pd.DataFrame]:
    traits = ordered_traits(count)
    raw = pd.read_csv(ROLE_MATRIX[model])
    if len(raw) != 275 or raw.persona.duplicated().any():
        raise ValueError(f"invalid 275-role matrix for {model}")
    missing = sorted(set(traits) - set(raw.columns))
    if missing:
        raise ValueError(f"missing {model} traits: {missing}")
    raw = raw.sort_values("persona").reset_index(drop=True)
    x, means, norms = shape_transform(raw[traits].to_numpy(float))
    coords = pd.read_csv(COORDS)
    coords = coords[coords.model.eq(model)].sort_values("role").reset_index(drop=True)
    if raw.persona.tolist() != coords.role.tolist():
        raise ValueError(f"role/coordinate labels differ for {model}")
    y = coords[["native_pc1", "native_pc2", "native_pc3"]].to_numpy(float)
    long = pd.DataFrame(
        {
            "model": np.repeat(model, len(raw) * count),
            "model_label": np.repeat(MODEL_LABEL[model], len(raw) * count),
            "role": np.repeat(raw.persona.to_numpy(), count),
            "trait_set": np.repeat(count, len(raw) * count),
            "trait_order": np.tile(np.arange(1, count + 1), len(raw)),
            "trait": np.tile(traits, len(raw)),
            "raw_trait_value": raw[traits].to_numpy(float).ravel(),
            "row_trait_mean": np.repeat(means, count),
            "centered_l2_norm": np.repeat(norms, count),
            "shape_value": x.ravel(),
        }
    )
    return raw.persona.tolist(), traits, x, y, long


def normalized_rmse(y: np.ndarray, pred: np.ndarray, scale: np.ndarray | None = None) -> float:
    if scale is None:
        scale = y.std(axis=0, ddof=1)
    return float(np.sqrt(np.mean(np.square((y - pred) / scale))))


def choose_alpha(x: np.ndarray, y: np.ndarray, splits: list[tuple[np.ndarray, np.ndarray]]) -> float:
    scale = y.std(axis=0, ddof=1)
    scores = []
    for alpha in ALPHAS:
        pred = np.zeros_like(y)
        for train, test in splits:
            pred[test] = Ridge(alpha=float(alpha), fit_intercept=True).fit(x[train], y[train]).predict(x[test])
        scores.append(normalized_rmse(y, pred, scale))
    best = min(scores)
    tied = [float(a) for a, score in zip(ALPHAS, scores) if abs(score - best) <= 1e-12]
    return max(tied)


def choose_knn(x: np.ndarray, y: np.ndarray, splits: list[tuple[np.ndarray, np.ndarray]]) -> tuple[int, str]:
    scale = y.std(axis=0, ddof=1)
    scored = []
    for k in KNN_K:
        for weights in KNN_WEIGHTS:
            pred = np.zeros_like(y)
            for train, test in splits:
                estimator = KNeighborsRegressor(n_neighbors=k, weights=weights, metric="euclidean")
                pred[test] = estimator.fit(x[train], y[train]).predict(x[test])
            scored.append((normalized_rmse(y, pred, scale), k, weights))
    best = min(s[0] for s in scored)
    tied = [(k, w) for score, k, w in scored if abs(score - best) <= 1e-12]
    tied.sort(key=lambda item: (item[0], 0 if item[1] == "distance" else 1))
    return tied[0]


def model_validation(model: str, count: int) -> tuple[pd.DataFrame, pd.DataFrame, dict, pd.DataFrame]:
    roles, traits, x, y, long = role_data(model, count)
    outer = list(KFold(10, shuffle=True, random_state=OUTER_SEED).split(x))
    ridge_oof = np.zeros_like(y)
    knn_oof = np.zeros_like(y)
    baseline_oof = np.zeros_like(y)
    alpha_by_fold = []
    knn_by_fold = []
    fold_id = np.zeros(len(x), dtype=int)
    for fold, (train, test) in enumerate(outer, start=1):
        inner = list(KFold(5, shuffle=True, random_state=121000 + fold).split(x[train]))
        alpha = choose_alpha(x[train], y[train], inner)
        k, weights = choose_knn(x[train], y[train], inner)
        ridge_oof[test] = Ridge(alpha=alpha, fit_intercept=True).fit(x[train], y[train]).predict(x[test])
        knn_oof[test] = KNeighborsRegressor(k, weights=weights, metric="euclidean").fit(x[train], y[train]).predict(x[test])
        baseline_oof[test] = y[train].mean(axis=0)
        fold_id[test] = fold
        alpha_by_fold.append(alpha)
        knn_by_fold.append({"fold": fold, "k": k, "weights": weights})
    final_splits = list(KFold(10, shuffle=True, random_state=FINAL_SEED).split(x))
    final_alpha = choose_alpha(x, y, final_splits)
    final_k, final_weights = choose_knn(x, y, final_splits)
    scale = y.std(axis=0, ddof=1)
    nrmse = normalized_rmse(y, ridge_oof, scale)
    baseline_nrmse = normalized_rmse(y, baseline_oof, scale)
    r2s = [float(r2_score(y[:, j], ridge_oof[:, j])) for j in range(3)]
    gate = bool(nrmse <= 0.90 and np.mean(r2s) >= 0.20 and sum(r > 0 for r in r2s) >= 2 and nrmse < baseline_nrmse)
    residual = y - ridge_oof
    residual_cov = np.cov(residual, rowvar=False, ddof=1)
    rows = []
    for j, pc in enumerate(["PC1", "PC2", "PC3"]):
        rows.append(
            {
                "model": model,
                "model_label": MODEL_LABEL[model],
                "trait_set": count,
                "coordinate": pc,
                "outer_oof_r2": r2s[j],
                "outer_oof_rmse": math.sqrt(mean_squared_error(y[:, j], ridge_oof[:, j])),
                "target_sd": scale[j],
                "baseline_rmse": math.sqrt(mean_squared_error(y[:, j], baseline_oof[:, j])),
                "normalized_3d_rmse": nrmse,
                "baseline_normalized_3d_rmse": baseline_nrmse,
                "mean_coordinate_r2": float(np.mean(r2s)),
                "positive_coordinate_count": int(sum(r > 0 for r in r2s)),
                "final_alpha": final_alpha,
                "final_knn_k": final_k,
                "final_knn_weights": final_weights,
                "ridge_knn_oof_normalized_displacement_p95": float(
                    np.quantile(np.linalg.norm((ridge_oof - knn_oof) / scale, axis=1), 0.95)
                ),
                "usability_gate": "USABLE" if gate else "INSUFFICIENT MODEL-SIDE LOCALIZATION",
            }
        )
    oof = pd.DataFrame(
        {
            "model": model,
            "model_label": MODEL_LABEL[model],
            "trait_set": count,
            "role": roles,
            "outer_fold": fold_id,
            **{f"observed_pc{j+1}": y[:, j] for j in range(3)},
            **{f"ridge_oof_pc{j+1}": ridge_oof[:, j] for j in range(3)},
            **{f"knn_oof_pc{j+1}": knn_oof[:, j] for j in range(3)},
            **{f"baseline_oof_pc{j+1}": baseline_oof[:, j] for j in range(3)},
            "ridge_knn_normalized_displacement": np.linalg.norm((ridge_oof - knn_oof) / scale, axis=1),
        }
    )
    fit = Ridge(alpha=final_alpha, fit_intercept=True).fit(x, y)
    meta = {
        "model": model,
        "trait_set": count,
        "traits": traits,
        "outer_seed": OUTER_SEED,
        "final_seed": FINAL_SEED,
        "alpha_grid": ALPHAS.tolist(),
        "outer_selected_alphas": alpha_by_fold,
        "final_alpha": final_alpha,
        "knn_candidates": {"k": KNN_K, "weights": KNN_WEIGHTS},
        "outer_selected_knn": knn_by_fold,
        "final_knn": {"k": final_k, "weights": final_weights},
        "target_mean": y.mean(axis=0).tolist(),
        "target_sd": scale.tolist(),
        "ridge_intercept": fit.intercept_.tolist(),
        "ridge_coefficients": fit.coef_.tolist(),
        "residual_covariance": residual_cov.tolist(),
        "usability_gate": "USABLE" if gate else "INSUFFICIENT MODEL-SIDE LOCALIZATION",
        "human_rows_used_for_hyperparameter_selection": 0,
    }
    return pd.DataFrame(rows), oof, meta, long


def validation_stage() -> None:
    manifest = {
        "analysis_model": "GPT-5.5",
        "method_freeze_commit": METHOD_COMMIT,
        "terrain_final_commit": TERRAIN_FINAL,
        "terrain_numerical_commit": TERRAIN_NUMERICAL,
        "inputs": [],
        "models": {},
        "boundaries": {
            "model_only_hyperparameter_selection": True,
            "human_pc_coordinates_computed_in_validation_stage": False,
            "role_vectors_recomputed": False,
            "model_inference": False,
            "gpu": False,
        },
    }
    for path in [*HUMAN.values(), *ROLE_MATRIX.values(), COORDS, COVERAGE, FAMILY]:
        manifest["inputs"].append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    residual_rows = []
    for count in TRAIT_COUNTS:
        metrics, oof, metas, shape_rows = [], [], {}, []
        for model in MODELS:
            model_metrics, model_oof, meta, model_shape = model_validation(model, count)
            metrics.append(model_metrics); oof.append(model_oof); shape_rows.append(model_shape); metas[model] = meta
        write_csv(pd.concat(metrics, ignore_index=True), OUT / f"model_projection_cv_{count}.csv")
        write_csv(pd.concat(oof, ignore_index=True), OUT / f"model_projection_oof_predictions_{count}.csv")
        write_csv(pd.concat(shape_rows, ignore_index=True), OUT / f"model_role_shape{count}.csv")
        (OUT / f"projection_models_{count}.json").write_text(json.dumps(metas, indent=2) + "\n")
        manifest["models"][str(count)] = metas
        for model, meta in metas.items():
            for row_index, row in enumerate(meta["residual_covariance"], start=1):
                for column_index, value in enumerate(row, start=1):
                    residual_rows.append(
                        {
                            "model": model,
                            "trait_set": count,
                            "target_row": f"PC{row_index}",
                            "target_column": f"PC{column_index}",
                            "residual_covariance": value,
                        }
                    )
    write_csv(pd.DataFrame(residual_rows), OUT / "model_projection_residual_covariance.csv")
    (OUT / "projection_method_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for count in TRAIT_COUNTS:
        frame = pd.read_csv(OUT / f"model_projection_cv_{count}.csv")
        print(f"trait_set={count}")
        print(frame.drop_duplicates("model")[["model", "normalized_3d_rmse", "mean_coordinate_r2", "usability_gate"]].to_string(index=False))


def human_shape_data(count: int) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    source = pd.read_csv(HUMAN[count])
    traits = ordered_traits(count)
    meta_cols = ["K", "solution_status", "eligible_primary_k", "profile_id", "profile_size", "profile_proportion"]
    meta = source[meta_cols].drop_duplicates().sort_values(["K", "profile_id"]).reset_index(drop=True)
    pivot = source.pivot(index="profile_id", columns="trait", values="human_trait_value").loc[meta.profile_id, traits]
    x, means, norms = shape_transform(pivot.to_numpy(float))
    rows = []
    for i, profile in enumerate(meta.itertuples(index=False)):
        for j, trait in enumerate(traits):
            rows.append(
                {
                    "K": profile.K,
                    "solution_status": profile.solution_status,
                    "eligible_primary_k": profile.eligible_primary_k,
                    "profile_id": profile.profile_id,
                    "profile_size": profile.profile_size,
                    "profile_proportion": profile.profile_proportion,
                    "trait_set": count,
                    "trait_order": j + 1,
                    "trait": trait,
                    "raw_human_trait_value": pivot.iloc[i, j],
                    "row_trait_mean": means[i],
                    "centered_l2_norm": norms[i],
                    "shape_value": x[i, j],
                }
            )
    return meta, pd.DataFrame(rows), traits


def display_transform(model: str, values: np.ndarray, alignment: dict) -> np.ndarray:
    fits = alignment["fits"]
    qfit = fits["llama_to_qwen__pc1_pc3__variance_standardized"]
    if model == "qwen":
        return (values - np.asarray(qfit["target_mean"])) / np.asarray(qfit["target_scale"])
    fit = fits[f"{model}_to_qwen__pc1_pc3__variance_standardized"]
    return (
        (values - np.asarray(fit["source_mean"]))
        / np.asarray(fit["source_scale"])
        / np.asarray(fit["source_scale"])
    ) @ np.asarray(fit["rotation"])


def project_one(model: str, count: int, human_meta: pd.DataFrame, human_long: pd.DataFrame, alignment: dict) -> dict[str, pd.DataFrame]:
    roles, traits, x_role, y, _ = role_data(model, count)
    wide = human_long.pivot(index="profile_id", columns="trait", values="shape_value").loc[human_meta.profile_id, traits]
    x_human = wide.to_numpy(float)
    model_meta = json.loads((OUT / f"projection_models_{count}.json").read_text())[model]
    gate = model_meta["usability_gate"]
    scale = np.asarray(model_meta["target_sd"], float)
    ridge = Ridge(alpha=float(model_meta["final_alpha"]), fit_intercept=True).fit(x_role, y)
    pred = ridge.predict(x_human)
    knn_cfg = model_meta["final_knn"]
    knn = KNeighborsRegressor(int(knn_cfg["k"]), weights=knn_cfg["weights"], metric="euclidean").fit(x_role, y)
    knn_pred = knn.predict(x_human)
    neighbor_dist, neighbor_idx = knn.kneighbors(x_human, n_neighbors=int(knn_cfg["k"]), return_distance=True)
    similarities = 1.0 - np.square(neighbor_dist) / 2.0
    aligned = display_transform(model, pred, alignment)

    role_sim = x_role @ x_role.T
    np.fill_diagonal(role_sim, -np.inf)
    loo_support = role_sim.max(axis=1)
    human_role_sim = x_human @ x_role.T
    max_support = human_role_sim.max(axis=1)

    coords = pd.read_csv(COORDS)
    coords = coords[coords.model.eq(model)].sort_values("role").reset_index(drop=True)
    kde = gaussian_kde(y.T, bw_method="scott")
    point_density = kde(y.T)
    human_density = kde(pred.T)
    coverage = pd.read_csv(COVERAGE)
    thresholds = {int(r.target_sample_coverage_percent): float(r.density_threshold) for r in coverage[coverage.model.eq(model)].itertuples()}
    family = pd.read_csv(FAMILY)
    family = family[(family.model.eq(model)) & (~family.consensus_family_id.eq("Unassigned"))].copy()
    family_centers = family.set_index("consensus_family_id")[["native_centroid_pc1", "native_centroid_pc2", "native_centroid_pc3"]]

    oof = pd.read_csv(OUT / f"model_projection_oof_predictions_{count}.csv")
    disagreement_p95 = float(model_meta and oof[oof.model.eq(model)].ridge_knn_normalized_displacement.quantile(0.95))
    pc_dist = np.linalg.norm((pred[:, None, :] - y[None, :, :]) / scale, axis=2)
    nearest_pc_idx = np.argsort(pc_dist, axis=1)[:, :10]

    projection_rows, support_rows, coverage_rows, knn_rows, family_rows, ridge_knn_rows = [], [], [], [], [], []
    for i, h in enumerate(human_meta.itertuples(index=False)):
        eligible = int(h.K) in ELIGIBLE_K
        projection_status = "PRIMARY_ELIGIBLE" if eligible else "DIAGNOSTIC_INELIGIBLE_K9"
        if gate != "USABLE": projection_status = "INSUFFICIENT MODEL-SIDE LOCALIZATION"
        support_pct = 100.0 * float(np.mean(loo_support <= max_support[i]))
        displacement = float(np.linalg.norm((pred[i] - knn_pred[i]) / scale))
        density_sparsity_pct = 100.0 * float(np.mean(point_density >= human_density[i]))
        family_distance = np.linalg.norm((family_centers.to_numpy(float) - pred[i]) / scale, axis=1)
        nearest_family = str(family_centers.index[int(np.argmin(family_distance))])
        base = {
            "model": model, "model_label": MODEL_LABEL[model], "trait_set": count, "K": h.K,
            "profile_id": h.profile_id, "profile_size": h.profile_size, "profile_proportion": h.profile_proportion,
            "eligible_primary_k": eligible, "human_stability_tier": "moderate" if int(h.K) <= 6 else "low",
            "projection_status": projection_status, "model_usability_gate": gate,
        }
        projection_rows.append({**base, "ridge_pc1": pred[i,0], "ridge_pc2": pred[i,1], "ridge_pc3": pred[i,2],
            "display_aligned_x": aligned[i,0], "display_aligned_y": aligned[i,1], "display_aligned_z": aligned[i,2]})
        support_rows.append({**base, "maximum_role_shape_similarity": max_support[i],
            "mean_selected_neighbor_similarity": float(similarities[i].mean()), "shape_support_percentile": support_pct,
            "ridge_knn_pc_standardized_displacement": displacement, "ridge_knn_disagreement_p95": disagreement_p95,
            "low_shape_support_warning": support_pct < 5, "ridge_knn_disagreement_warning": displacement > disagreement_p95,
            "nearest_role_native_pc_distance": float(pc_dist[i, nearest_pc_idx[i,0]])})
        coverage_rows.append({**base, "ridge_kde_density": human_density[i], "terrain_sparsity_percentile": density_sparsity_pct,
            "inside_50_sample_coverage": human_density[i] >= thresholds[50], "inside_80_sample_coverage": human_density[i] >= thresholds[80],
            "inside_95_sample_coverage": human_density[i] >= thresholds[95], "beyond_95_warning": human_density[i] < thresholds[95]})
        ridge_knn_rows.append({**base, "ridge_pc1": pred[i,0], "ridge_pc2": pred[i,1], "ridge_pc3": pred[i,2],
            "knn_pc1": knn_pred[i,0], "knn_pc2": knn_pred[i,1], "knn_pc3": knn_pred[i,2],
            "pc_standardized_displacement": displacement, "disagreement_p95": disagreement_p95,
            "warning": displacement > disagreement_p95, "knn_k": int(knn_cfg["k"]), "knn_weights": knn_cfg["weights"]})
        for rank, idx in enumerate(neighbor_idx[i], 1):
            knn_rows.append({**base, "neighbor_type": "shape_support", "neighbor_rank": rank, "role": roles[idx],
                "trait_shape_similarity": human_role_sim[i,idx], "trait_shape_distance": neighbor_dist[i,rank-1],
                "native_pc_standardized_distance_from_ridge": pc_dist[i,idx]})
        for rank, idx in enumerate(nearest_pc_idx[i], 1):
            knn_rows.append({**base, "neighbor_type": "native_pc_nearest", "neighbor_rank": rank, "role": roles[idx],
                "trait_shape_similarity": human_role_sim[i,idx], "trait_shape_distance": math.sqrt(max(0,2-2*human_role_sim[i,idx])),
                "native_pc_standardized_distance_from_ridge": pc_dist[i,idx]})
        for family_id, d in zip(family_centers.index, family_distance):
            family_rows.append({**base, "family_id": family_id, "pc_standardized_distance": d,
                "nearest_family": family_id == nearest_family})

    rng = np.random.default_rng(BOOTSTRAP_SEEDS[count][model])
    boot_pred = np.empty((N_BOOT, len(human_meta), 3))
    for b in range(N_BOOT):
        sample = rng.integers(0, len(x_role), size=len(x_role))
        boot_pred[b] = Ridge(alpha=float(model_meta["final_alpha"]), fit_intercept=True).fit(x_role[sample], y[sample]).predict(x_human)
    boot_rows, summary_rows = [], []
    for i, h in enumerate(human_meta.itertuples(index=False)):
        base = {"model": model, "trait_set": count, "K": h.K, "profile_id": h.profile_id,
                "eligible_primary_k": int(h.K) in ELIGIBLE_K, "model_usability_gate": gate}
        for b in range(N_BOOT):
            boot_rows.append({**base, "bootstrap_draw": b + 1, "pc1": boot_pred[b,i,0], "pc2": boot_pred[b,i,1], "pc3": boot_pred[b,i,2]})
        cov = np.cov(boot_pred[:,i,:], rowvar=False, ddof=1)
        vals, vecs = np.linalg.eigh(cov); order = np.argsort(vals)[::-1]; vals=vals[order]; vecs=vecs[:,order]
        boot_density = kde(boot_pred[:,i,:].T)
        summary_rows.append({**base, "bootstrap_n": N_BOOT,
            "centroid_pc1": boot_pred[:,i,0].mean(), "centroid_pc2": boot_pred[:,i,1].mean(), "centroid_pc3": boot_pred[:,i,2].mean(),
            "sd_pc1": boot_pred[:,i,0].std(ddof=1), "sd_pc2": boot_pred[:,i,1].std(ddof=1), "sd_pc3": boot_pred[:,i,2].std(ddof=1),
            "cov_11": cov[0,0], "cov_12": cov[0,1], "cov_13": cov[0,2], "cov_22": cov[1,1], "cov_23": cov[1,2], "cov_33": cov[2,2],
            "eigenvalue_1": vals[0], "eigenvalue_2": vals[1], "eigenvalue_3": vals[2],
            **{f"eigenvector_{a+1}_{j+1}": vecs[j,a] for a in range(3) for j in range(3)},
            "fraction_inside_50_sample_coverage": float(np.mean(boot_density >= thresholds[50])),
            "fraction_inside_80_sample_coverage": float(np.mean(boot_density >= thresholds[80])),
            "fraction_inside_95_sample_coverage": float(np.mean(boot_density >= thresholds[95]))})
    return {"projection":pd.DataFrame(projection_rows), "support":pd.DataFrame(support_rows), "coverage":pd.DataFrame(coverage_rows),
            "neighbors":pd.DataFrame(knn_rows), "family":pd.DataFrame(family_rows), "ridge_knn":pd.DataFrame(ridge_knn_rows),
            "bootstrap":pd.DataFrame(boot_rows), "bootstrap_summary":pd.DataFrame(summary_rows)}


def projection_stage() -> None:
    alignment = git_json(ALIGNMENT_GIT_PATH)
    all_outputs = {key: [] for key in ["projection","support","coverage","neighbors","family","ridge_knn","bootstrap","bootstrap_summary"]}
    human_meta_by_count = {}
    for count in TRAIT_COUNTS:
        meta, human_long, _ = human_shape_data(count)
        human_meta_by_count[count] = meta
        write_csv(human_long, OUT / f"human_profiles_shared{count}.csv")
        for model in MODELS:
            result = project_one(model, count, meta, human_long, alignment)
            for key, frame in result.items(): all_outputs[key].append(frame)
        write_csv(pd.concat([x for x in all_outputs["projection"] if int(x.trait_set.iloc[0])==count],ignore_index=True), OUT/f"human_projection_{count}.csv")
    combined = {key: pd.concat(frames, ignore_index=True) for key, frames in all_outputs.items()}
    write_csv(combined["bootstrap"], OUT/"human_projection_bootstrap_draws.csv")
    write_csv(combined["bootstrap_summary"], OUT/"human_projection_bootstrap_summary.csv")
    write_csv(combined["support"], OUT/"human_projection_support_diagnostics.csv")
    write_csv(combined["coverage"], OUT/"human_projection_coverage_relation.csv")
    write_csv(combined["neighbors"], OUT/"human_projection_nearest_roles.csv")
    write_csv(combined["family"], OUT/"human_projection_family_relation.csv")
    write_csv(combined["ridge_knn"], OUT/"human_projection_ridge_vs_knn.csv")

    p12=combined["projection"][combined["projection"].trait_set.eq(12)].copy(); p45=combined["projection"][combined["projection"].trait_set.eq(45)].copy()
    keys=["model","K","profile_id"]
    sens=p12.merge(p45,on=keys,suffixes=("_12","_45"),validate="one_to_one")
    coords=pd.read_csv(COORDS); scales=coords.groupby("model")[["native_pc1","native_pc2","native_pc3"]].std(ddof=1)
    cov=combined["coverage"]
    fam=combined["family"][combined["family"].nearest_family].set_index(keys+["trait_set"])
    neigh=combined["neighbors"][combined["neighbors"].neighbor_type.eq("native_pc_nearest") & combined["neighbors"].neighbor_rank.eq(1)].set_index(keys+["trait_set"])
    rows=[]
    for r in sens.itertuples(index=False):
        scale=scales.loc[r.model].to_numpy(float); d=np.array([r.ridge_pc1_45-r.ridge_pc1_12,r.ridge_pc2_45-r.ridge_pc2_12,r.ridge_pc3_45-r.ridge_pc3_12])
        key=(r.model,r.K,r.profile_id)
        c12=cov[(cov.model.eq(r.model))&(cov.K.eq(r.K))&(cov.profile_id.eq(r.profile_id))&(cov.trait_set.eq(12))].iloc[0]
        c45=cov[(cov.model.eq(r.model))&(cov.K.eq(r.K))&(cov.profile_id.eq(r.profile_id))&(cov.trait_set.eq(45))].iloc[0]
        rows.append({"model":r.model,"K":r.K,"profile_id":r.profile_id,"eligible_primary_k":r.eligible_primary_k_12,
            "pc1_12":r.ridge_pc1_12,"pc2_12":r.ridge_pc2_12,"pc3_12":r.ridge_pc3_12,"pc1_45":r.ridge_pc1_45,"pc2_45":r.ridge_pc2_45,"pc3_45":r.ridge_pc3_45,
            "delta_pc1":d[0],"delta_pc2":d[1],"delta_pc3":d[2],"pc_standardized_displacement":np.linalg.norm(d/scale),
            "inside_50_12":c12.inside_50_sample_coverage,"inside_50_45":c45.inside_50_sample_coverage,
            "inside_80_12":c12.inside_80_sample_coverage,"inside_80_45":c45.inside_80_sample_coverage,
            "inside_95_12":c12.inside_95_sample_coverage,"inside_95_45":c45.inside_95_sample_coverage,
            "nearest_family_12":fam.loc[key+(12,)].family_id,"nearest_family_45":fam.loc[key+(45,)].family_id,
            "nearest_role_12":neigh.loc[key+(12,)].role,"nearest_role_45":neigh.loc[key+(45,)].role})
    comparison=pd.DataFrame(rows); write_csv(comparison,OUT/"human_projection_12_vs_45.csv")

    cross=[]
    for count in TRAIT_COUNTS:
        p=combined["projection"][combined["projection"].trait_set.eq(count)]
        for (k,profile),g in p.groupby(["K","profile_id"]):
            a=g.set_index("model")[["display_aligned_x","display_aligned_y","display_aligned_z"]]
            ds={}
            for m1,m2 in [("qwen","llama"),("qwen","gemma"),("llama","gemma")]: ds[f"{m1}_{m2}_distance"]=np.linalg.norm(a.loc[m1]-a.loc[m2])
            cross.append({"trait_set":count,"K":k,"profile_id":profile,"eligible_primary_k":int(k) in ELIGIBLE_K,**ds,"mean_pairwise_aligned_distance":np.mean(list(ds.values()))})
    write_csv(pd.DataFrame(cross),OUT/"human_crossmodel_projection_comparison.csv")

    support=combined["support"]; coverage=combined["coverage"]; boot=combined["bootstrap_summary"]
    cand=coverage[coverage.trait_set.eq(12)].merge(support[support.trait_set.eq(12)],on=["model","model_label","trait_set","K","profile_id","profile_size","profile_proportion","eligible_primary_k","human_stability_tier","projection_status","model_usability_gate"],validate="one_to_one")
    cand=cand.merge(comparison[["model","K","profile_id","pc_standardized_displacement"]],on=["model","K","profile_id"],validate="one_to_one")
    cand=cand.merge(boot[boot.trait_set.eq(12)][["model","K","profile_id","fraction_inside_95_sample_coverage"]],on=["model","K","profile_id"],validate="one_to_one")
    cand["candidate"]=(cand.model_usability_gate.eq("USABLE") & cand.eligible_primary_k.astype(bool) & ~cand.inside_95_sample_coverage.astype(bool))
    recurring=cand[cand.candidate].groupby(["K","profile_id"]).model.nunique()
    cand["cross_model_recurring_candidate"]=[bool(row.candidate and recurring.get((row.K,row.profile_id),0)>=2) for row in cand.itertuples()]
    write_csv(cand,OUT/"projected_coverage_extension_candidates.csv")
    write_csv(pd.DataFrame([{"status":"NOT_AVAILABLE","reason":"Frozen human split-refit table contains distances/proportions but no aligned aggregate trait vectors; no new human refit was authorized."}]),OUT/"human_profile_fit_sensitivity.csv")
    print("projection rows",len(combined["projection"]),"candidates",int(cand.candidate.sum()),"recurring",int(cand.cross_model_recurring_candidate.sum()))


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--stage",choices=["validation","projection","all"],required=True); args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if args.stage in {"validation","all"}: validation_stage()
    if args.stage in {"projection","all"}: projection_stage()


if __name__ == "__main__":
    main()
