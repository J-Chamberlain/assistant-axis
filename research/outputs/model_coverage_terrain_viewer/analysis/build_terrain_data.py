#!/usr/bin/env python3
"""Build deterministic model-only persona occupancy terrain tables and viewer data."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.stats import gaussian_kde, spearmanr


HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[2]

COORDINATE_SOURCE = ROOT / "research/outputs/extended_persona_pca/viewer_data.json"
COORDINATE_MANIFEST = ROOT / "research/outputs/extended_persona_pca/source_manifest.json"
FAMILY_SOURCE = ROOT / "research/outputs/crossmodel_cluster_reconciliation/consensus_family_roles.csv"
FAMILY_SUMMARY_SOURCE = ROOT / "research/outputs/crossmodel_cluster_reconciliation/candidate_consensus_families.csv"
ROLE_ID_SOURCE = ROOT / "research/outputs/cross_resolution_profile_banks/model/qwen/memberships_with_role_names.csv"
TRAIT_SOURCE = ROOT / "research/geometry_tables/qwen_trait_pc_rankings.csv"
ALIGNMENT_GIT_PATH = "research/outputs/human_supported_trait_convergence/procrustes_alignment_matrices.json"

MODEL_ORDER = ["qwen", "llama", "gemma"]
MODEL_LABEL = {
    "qwen": "Qwen 3 32B",
    "llama": "LLaMA 3.3 70B",
    "gemma": "Gemma 2 27B",
}
SOURCE_MODEL_LABEL = {
    "qwen": "Qwen/Qwen3-32B",
    "llama": "Llama-3.3-70B",
    "gemma": "Gemma-2-27B",
}
FAMILY_COLORS = {
    "MFamily_A": "#2D7FF9",
    "MFamily_B": "#E45756",
    "MFamily_C": "#54A24B",
    "MFamily_D": "#B279A2",
    "MFamily_E": "#F2CF5B",
    "Unassigned": "#8A93A3",
}
TARGET_COVERAGES = [0.50, 0.80, 0.95]
BANDWIDTH_MULTIPLIERS = [0.75, 1.00, 1.25]
GRID_3D = 36
GRID_2D = 80
K_NEIGHBORS = 10
MIN_FAMILY_ENVELOPE_N = 10


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_object(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)


def stable_rank_percentile_desc(values: np.ndarray, labels: list[str]) -> np.ndarray:
    order = sorted(range(len(values)), key=lambda i: (-float(values[i]), labels[i]))
    out = np.empty(len(values), dtype=float)
    for zero_rank, index in enumerate(order):
        out[index] = 100.0 * zero_rank / (len(values) - 1)
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a or b else math.nan


def standardize_axes(coords: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = coords.mean(axis=0)
    scale = coords.std(axis=0, ddof=1)
    if np.any(scale <= 0):
        raise ValueError("nonpositive coordinate scale")
    return (coords - mean) / scale, mean, scale


def nearest_neighbors(coords: np.ndarray, roles: list[str]) -> tuple[list[dict], np.ndarray, dict[str, set[str]]]:
    z, _, _ = standardize_axes(coords)
    distances = np.linalg.norm(z[:, None, :] - z[None, :, :], axis=2)
    rows: list[dict] = []
    mean_distances = np.zeros(len(roles))
    neighbor_sets: dict[str, set[str]] = {}
    for i, role in enumerate(roles):
        candidates = [(float(distances[i, j]), roles[j], j) for j in range(len(roles)) if j != i]
        candidates.sort(key=lambda item: (item[0], item[1]))
        chosen = candidates[:K_NEIGHBORS]
        mean_distances[i] = np.mean([item[0] for item in chosen])
        neighbor_sets[role] = {item[1] for item in chosen}
        for rank, (distance, neighbor, _) in enumerate(chosen, start=1):
            rows.append(
                {
                    "role": role,
                    "neighbor_rank": rank,
                    "neighbor_role": neighbor,
                    "standardized_native_pc_distance": distance,
                }
            )
    return rows, mean_distances, neighbor_sets


def fit_kde(coords: np.ndarray, multiplier: float = 1.0) -> gaussian_kde:
    base = gaussian_kde(coords.T, bw_method="scott")
    return gaussian_kde(coords.T, bw_method=float(base.factor) * multiplier)


def grid_for_kde(coords: np.ndarray, kde: gaussian_kde, resolution: int) -> tuple[list[np.ndarray], np.ndarray]:
    kernel_sd = np.sqrt(np.diag(kde.covariance))
    axes = [
        np.linspace(coords[:, axis].min() - kernel_sd[axis], coords[:, axis].max() + kernel_sd[axis], resolution)
        for axis in range(coords.shape[1])
    ]
    mesh = np.meshgrid(*axes, indexing="ij")
    grid_points = np.vstack([item.ravel() for item in mesh])
    density = kde(grid_points).reshape([resolution] * coords.shape[1])
    return axes, density


def source_rows() -> tuple[pd.DataFrame, dict, dict, bytes]:
    coordinate_payload = json.loads(COORDINATE_SOURCE.read_text(encoding="utf-8"))
    family = pd.read_csv(FAMILY_SOURCE)
    role_ids = pd.read_csv(ROLE_ID_SOURCE)[["opaque_role_id", "role"]].drop_duplicates()
    if role_ids.role.duplicated().any() or role_ids.opaque_role_id.duplicated().any() or len(role_ids) != 275:
        raise ValueError("role ID mapping is not one-to-one over 275 roles")
    role_id_map = dict(zip(role_ids.role, role_ids.opaque_role_id))

    role_sets: dict[str, set[str]] = {}
    records: list[dict] = []
    for model in MODEL_ORDER:
        payload = coordinate_payload["models"][model]
        points = payload["points"]
        if payload["role_count"] != 275 or len(points) != 275:
            raise ValueError(f"{model} does not have exactly 275 roles")
        roles = [str(point["persona"]) for point in points]
        if len(set(roles)) != 275:
            raise ValueError(f"{model} role labels are duplicated")
        role_sets[model] = set(roles)
        for point in points:
            values = np.asarray(point["coordinates"][:3], dtype=float)
            if values.shape != (3,) or not np.isfinite(values).all():
                raise ValueError(f"invalid PC1-PC3 coordinate for {model}/{point['persona']}")
            records.append(
                {
                    "model": model,
                    "model_label": MODEL_LABEL[model],
                    "source_model_label": SOURCE_MODEL_LABEL[model],
                    "opaque_role_id": role_id_map[point["persona"]],
                    "role": point["persona"],
                    "legacy_qwen_cluster": point.get("cluster", ""),
                    "native_pc1": values[0],
                    "native_pc2": values[1],
                    "native_pc3": values[2],
                }
            )
    if any(role_sets[model] != role_sets["qwen"] for model in MODEL_ORDER):
        raise ValueError("role label sets differ across models")

    alignment_bytes = git_object(ALIGNMENT_GIT_PATH)
    alignment = json.loads(alignment_bytes)
    return pd.DataFrame(records), coordinate_payload, alignment, alignment_bytes


def add_display_alignment(coords: pd.DataFrame, alignment: dict) -> pd.DataFrame:
    fits = alignment["fits"]
    qwen_fit = fits["llama_to_qwen__pc1_pc3__variance_standardized"]
    target_mean = np.asarray(qwen_fit["target_mean"], dtype=float)
    target_scale = np.asarray(qwen_fit["target_scale"], dtype=float)
    result = coords.copy()
    aligned = np.zeros((len(result), 3))
    for model in MODEL_ORDER:
        mask = result.model.eq(model).to_numpy()
        native = result.loc[mask, ["native_pc1", "native_pc2", "native_pc3"]].to_numpy(float)
        if model == "qwen":
            transformed = (native - target_mean) / target_scale
        else:
            fit = fits[f"{model}_to_qwen__pc1_pc3__variance_standardized"]
            transformed = (
                (native - np.asarray(fit["source_mean"], dtype=float))
                / np.asarray(fit["source_scale"], dtype=float)
            ) @ np.asarray(fit["rotation"], dtype=float)
        aligned[mask] = transformed
    result[["display_aligned_x", "display_aligned_y", "display_aligned_z"]] = aligned
    return result


def build_family_table(coords: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    family = pd.read_csv(FAMILY_SOURCE)
    family_summary = pd.read_csv(FAMILY_SUMMARY_SOURCE)
    family_status = {
        row.consensus_family_id: (
            "secondary_small_resolution_sensitive" if row.consensus_family_id == "MFamily_E" else "broad_candidate_consensus"
        )
        for row in family_summary.itertuples()
    }
    rows: list[dict] = []
    for model in MODEL_ORDER:
        support_col = f"{model}_support"
        selected = family[family[support_col].astype(bool)].copy()
        if selected.role.duplicated().any():
            raise ValueError(f"{model} has roles supported by multiple frozen families")
        mapping = selected.set_index("role").to_dict("index")
        counts = selected.groupby("consensus_family_id").size().to_dict()
        for row in coords[coords.model.eq(model)].itertuples():
            info = mapping.get(row.role)
            family_id = info["consensus_family_id"] if info else "Unassigned"
            family_n = int(counts.get(family_id, 0))
            rows.append(
                {
                    "model": model,
                    "model_label": MODEL_LABEL[model],
                    "opaque_role_id": row.opaque_role_id,
                    "role": row.role,
                    "consensus_family_id": family_id,
                    "membership_category": info["membership_category"] if info else "unassigned",
                    "model_support_count": int(info["model_support_count"]) if info else 0,
                    "family_status": family_status.get(family_id, "not_in_frozen_consensus_family"),
                    "family_color": FAMILY_COLORS[family_id],
                    "model_specific_family_n": family_n,
                    "family_envelope_eligible": bool(family_id != "Unassigned" and family_n >= MIN_FAMILY_ENVELOPE_N),
                }
            )
    return pd.DataFrame(rows), family_summary


def main() -> None:
    coords, source_payload, alignment, alignment_bytes = source_rows()
    coords = add_display_alignment(coords, alignment)
    family, family_summary = build_family_table(coords)
    coords = coords.merge(
        family[["model", "role", "consensus_family_id", "membership_category"]],
        on=["model", "role"],
        how="left",
        validate="one_to_one",
    )

    density_rows: list[dict] = []
    sparsity_rows: list[dict] = []
    coverage_rows: list[dict] = []
    sensitivity_rows: list[dict] = []
    neighbor_rows: list[dict] = []
    family_summary_rows: list[dict] = []
    neighbor_sets_by_model: dict[str, dict[str, set[str]]] = {}
    viewer_models: dict[str, dict] = {}

    for model in MODEL_ORDER:
        model_frame = coords[coords.model.eq(model)].sort_values("role").reset_index(drop=True)
        roles = model_frame.role.tolist()
        xyz = model_frame[["native_pc1", "native_pc2", "native_pc3"]].to_numpy(float)
        primary = fit_kde(xyz, 1.0)
        point_density = primary(xyz.T)
        log_density = np.log(point_density)
        density_percentile = 100.0 - stable_rank_percentile_desc(point_density, roles)
        sparsity_percentile = stable_rank_percentile_desc(point_density, roles)
        neighbor_model_rows, knn_mean, neighbor_sets = nearest_neighbors(xyz, roles)
        neighbor_sets_by_model[model] = neighbor_sets
        knn_sparsity_percentile = stable_rank_percentile_desc(-knn_mean, roles)
        for row in neighbor_model_rows:
            row.update({"model": model, "model_label": MODEL_LABEL[model], "k": K_NEIGHBORS})
            neighbor_rows.append(row)

        axes3, grid_primary = grid_for_kde(xyz, primary, GRID_3D)
        thresholds: dict[str, float] = {}
        for target in TARGET_COVERAGES:
            threshold = float(np.quantile(point_density, 1.0 - target, method="linear"))
            achieved_count = int(np.sum(point_density >= threshold))
            achieved_fraction = achieved_count / len(point_density)
            key = str(int(target * 100))
            thresholds[key] = threshold
            coverage_rows.append(
                {
                    "model": model,
                    "model_label": MODEL_LABEL[model],
                    "target_sample_coverage_fraction": target,
                    "target_sample_coverage_percent": int(target * 100),
                    "density_threshold": threshold,
                    "achieved_role_count": achieved_count,
                    "achieved_sample_fraction": achieved_fraction,
                    "achieved_sample_percent": 100.0 * achieved_fraction,
                    "total_sampled_roles": len(point_density),
                    "kde_method": "scipy gaussian_kde full-covariance Scott",
                    "scott_factor": float(primary.factor),
                    "grid_resolution_per_axis": GRID_3D,
                    "grid_extent_pc1_min": axes3[0][0],
                    "grid_extent_pc1_max": axes3[0][-1],
                    "grid_extent_pc2_min": axes3[1][0],
                    "grid_extent_pc2_max": axes3[1][-1],
                    "grid_extent_pc3_min": axes3[2][0],
                    "grid_extent_pc3_max": axes3[2][-1],
                }
            )

        primary_rank = pd.Series(point_density).rank(method="average").to_numpy()
        n_decile = int(math.ceil(len(roles) * 0.10))
        dense_primary = set(np.argsort(-point_density)[:n_decile])
        sparse_primary = set(np.argsort(point_density)[:n_decile])
        primary_mesh = np.meshgrid(*axes3, indexing="ij")
        primary_grid_points = np.vstack([item.ravel() for item in primary_mesh])
        for multiplier in BANDWIDTH_MULTIPLIERS:
            kde = fit_kde(xyz, multiplier)
            densities = kde(xyz.T)
            rank = pd.Series(densities).rank(method="average").to_numpy()
            grid = kde(primary_grid_points).reshape([GRID_3D] * 3)
            dense = set(np.argsort(-densities)[:n_decile])
            sparse = set(np.argsort(densities)[:n_decile])
            rank_rho = float(spearmanr(primary_rank, rank).statistic)
            dense_j = jaccard({str(x) for x in dense_primary}, {str(x) for x in dense})
            sparse_j = jaccard({str(x) for x in sparse_primary}, {str(x) for x in sparse})
            grid_r = float(np.corrcoef(grid_primary.ravel(), grid.ravel())[0, 1])
            sensitivity_rows.append(
                {
                    "model": model,
                    "model_label": MODEL_LABEL[model],
                    "bandwidth_multiplier": multiplier,
                    "effective_kde_factor": float(kde.factor),
                    "role_density_rank_spearman_vs_primary": rank_rho,
                    "densest_decile_jaccard_vs_primary": dense_j,
                    "sparsest_decile_jaccard_vs_primary": sparse_j,
                    "grid_density_pearson_vs_primary": grid_r,
                    "density_ordering_robust_at_frozen_rule": bool(rank_rho >= 0.90),
                    "dense_extreme_robust_at_frozen_rule": bool(dense_j >= 0.70),
                    "sparse_extreme_robust_at_frozen_rule": bool(sparse_j >= 0.70),
                }
            )

        family_model = family[family.model.eq(model)].set_index("role")
        for i, row in model_frame.iterrows():
            density_rows.append(
                {
                    "model": model,
                    "model_label": MODEL_LABEL[model],
                    "opaque_role_id": row.opaque_role_id,
                    "role": row.role,
                    "native_pc1": row.native_pc1,
                    "native_pc2": row.native_pc2,
                    "native_pc3": row.native_pc3,
                    "kde_density": point_density[i],
                    "log_kde_density": log_density[i],
                    "within_model_density_percentile": density_percentile[i],
                    "density_rank_1_is_densest": int(round(sparsity_percentile[i] * (len(roles) - 1) / 100.0)) + 1,
                    "scott_factor": float(primary.factor),
                }
            )
            sparsity_rows.append(
                {
                    "model": model,
                    "model_label": MODEL_LABEL[model],
                    "opaque_role_id": row.opaque_role_id,
                    "role": row.role,
                    "inverse_kde_density": 1.0 / point_density[i],
                    "within_model_sparsity_percentile": sparsity_percentile[i],
                    "sparsity_rank_1_is_sparsest": int(round((100.0 - sparsity_percentile[i]) * (len(roles) - 1) / 100.0)) + 1,
                    "knn_k": K_NEIGHBORS,
                    "mean_knn_distance_standardized_native_pc": knn_mean[i],
                    "within_model_knn_sparsity_percentile": knn_sparsity_percentile[i],
                }
            )

        hull_payload: dict[str, dict] = {}
        merged = model_frame.merge(
            family_model[["family_envelope_eligible"]],
            left_on="role",
            right_index=True,
            validate="one_to_one",
        )
        for family_id in ["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D", "MFamily_E"]:
            part = merged[merged.consensus_family_id.eq(family_id)]
            part_xyz = part[["native_pc1", "native_pc2", "native_pc3"]].to_numpy(float)
            eligible = len(part) >= MIN_FAMILY_ENVELOPE_N and np.linalg.matrix_rank(part_xyz - part_xyz.mean(axis=0)) == 3
            if eligible:
                hull = ConvexHull(part_xyz)
                hull_payload[family_id] = {
                    "roles": part.role.tolist(),
                    "vertices": np.round(part_xyz, 8).tolist(),
                    "simplices": hull.simplices.tolist(),
                    "volume": float(hull.volume),
                    "label": "convex sampled-role envelope; not density",
                }
            for axis, name in enumerate(["pc1", "pc2", "pc3"]):
                pass
            family_summary_rows.append(
                {
                    "model": model,
                    "model_label": MODEL_LABEL[model],
                    "consensus_family_id": family_id,
                    "role_count": len(part),
                    "envelope_eligible": bool(eligible),
                    "median_density_percentile": float(np.median([density_percentile[roles.index(r)] for r in part.role])) if len(part) else math.nan,
                    "median_sparsity_percentile": float(np.median([sparsity_percentile[roles.index(r)] for r in part.role])) if len(part) else math.nan,
                    "native_centroid_pc1": float(part.native_pc1.mean()) if len(part) else math.nan,
                    "native_centroid_pc2": float(part.native_pc2.mean()) if len(part) else math.nan,
                    "native_centroid_pc3": float(part.native_pc3.mean()) if len(part) else math.nan,
                    "native_mean_radius_from_family_centroid": float(np.linalg.norm(part_xyz - part_xyz.mean(axis=0), axis=1).mean()) if len(part) else math.nan,
                }
            )

        grids2d: dict[str, dict] = {}
        for a, b, pair in [(0, 1, "pc1_pc2"), (0, 2, "pc1_pc3"), (1, 2, "pc2_pc3")]:
            two = xyz[:, [a, b]]
            kde2 = fit_kde(two, 1.0)
            axes2, density2 = grid_for_kde(two, kde2, GRID_2D)
            grids2d[pair] = {
                "x": np.round(axes2[0], 8).tolist(),
                "y": np.round(axes2[1], 8).tolist(),
                "z": np.round(density2.T, 12).tolist(),
                "factor": float(kde2.factor),
            }

        point_payload = []
        for i, row in model_frame.iterrows():
            fam = family_model.loc[row.role]
            point_payload.append(
                {
                    "id": row.opaque_role_id,
                    "role": row.role,
                    "native": [round(float(row.native_pc1), 8), round(float(row.native_pc2), 8), round(float(row.native_pc3), 8)],
                    "aligned": [round(float(row.display_aligned_x), 8), round(float(row.display_aligned_y), 8), round(float(row.display_aligned_z), 8)],
                    "density": float(point_density[i]),
                    "density_percentile": round(float(density_percentile[i]), 6),
                    "sparsity_percentile": round(float(sparsity_percentile[i]), 6),
                    "knn_distance": round(float(knn_mean[i]), 8),
                    "family": fam.consensus_family_id,
                    "membership": fam.membership_category,
                    "neighbors": [x["neighbor_role"] for x in neighbor_model_rows if x["role"] == row.role],
                }
            )
        viewer_models[model] = {
            "label": MODEL_LABEL[model],
            "points": point_payload,
            "kde": {
                "factor": float(primary.factor),
                "axes": [np.round(axis, 8).tolist() for axis in axes3],
                "density": np.round(grid_primary, 12).ravel(order="C").tolist(),
                "shape": [GRID_3D, GRID_3D, GRID_3D],
                "thresholds": thresholds,
                "max": float(grid_primary.max()),
            },
            "grids2d": grids2d,
            "family_hulls": hull_payload,
        }

    recurrence_rows: list[dict] = []
    for role in sorted(neighbor_sets_by_model["qwen"]):
        q, l, g = (neighbor_sets_by_model[model][role] for model in MODEL_ORDER)
        ql, qg, lg = jaccard(q, l), jaccard(q, g), jaccard(l, g)
        recurrence_rows.append(
            {
                "opaque_role_id": coords[coords.role.eq(role)].opaque_role_id.iloc[0],
                "role": role,
                "qwen_llama_neighbor_jaccard_k10": ql,
                "qwen_gemma_neighbor_jaccard_k10": qg,
                "llama_gemma_neighbor_jaccard_k10": lg,
                "mean_pairwise_neighbor_jaccard_k10": float(np.mean([ql, qg, lg])),
            }
        )

    trait = pd.read_csv(TRAIT_SOURCE)[["trait", "pc1", "pc2", "pc3"]].copy()
    trait.insert(0, "model_label", MODEL_LABEL["qwen"])
    trait.insert(0, "model", "qwen")
    trait["landmark_type"] = "trait-direction landmark; excluded from occupancy density"

    coordinate_columns = [
        "model", "model_label", "source_model_label", "opaque_role_id", "role", "legacy_qwen_cluster",
        "native_pc1", "native_pc2", "native_pc3", "display_aligned_x", "display_aligned_y", "display_aligned_z",
        "consensus_family_id", "membership_category",
    ]
    coords[coordinate_columns].to_csv(OUT / "role_coordinates.csv", index=False, float_format="%.12g")
    pd.DataFrame(density_rows).to_csv(OUT / "role_density_scores.csv", index=False, float_format="%.12g")
    pd.DataFrame(sparsity_rows).to_csv(OUT / "role_sparsity_scores.csv", index=False, float_format="%.12g")
    family.to_csv(OUT / "role_family_membership.csv", index=False)
    pd.DataFrame(coverage_rows).to_csv(OUT / "coverage_region_summary.csv", index=False, float_format="%.12g")
    pd.DataFrame(sensitivity_rows).to_csv(OUT / "density_bandwidth_sensitivity.csv", index=False, float_format="%.12g")
    pd.DataFrame(neighbor_rows).sort_values(["model", "role", "neighbor_rank"]).to_csv(
        OUT / "nearest_role_neighbors.csv", index=False, float_format="%.12g"
    )
    pd.DataFrame(recurrence_rows).to_csv(OUT / "cross_model_neighborhood_recurrence.csv", index=False, float_format="%.12g")
    trait.to_csv(OUT / "trait_landmarks.csv", index=False, float_format="%.12g")
    coords[["model", "model_label", "opaque_role_id", "role", "display_aligned_x", "display_aligned_y", "display_aligned_z"]].to_csv(
        OUT / "display_alignment_coordinates.csv", index=False, float_format="%.12g"
    )
    pd.DataFrame(family_summary_rows).to_csv(OUT / "family_terrain_summary.csv", index=False, float_format="%.12g")

    viewer_payload = {
        "metadata": {
            "title": "Model-only persona-space coverage terrain",
            "role_count_per_model": 275,
            "models": MODEL_ORDER,
            "occupancy_warning": "Coverage reflects the selected 275-role inventory. It is not a population probability distribution.",
            "native_space_warning": "Each native panel uses its model's own canonical PC1-PC3 coordinates.",
            "aligned_space_warning": "Display alignment uses the shared 275-role inventory. Axes are aligned display coordinates, not universally shared native PC meanings.",
            "density_method": "scipy gaussian_kde, full covariance, Scott factor",
            "coverage_levels_percent": [50, 80, 95],
            "grid_3d": GRID_3D,
            "grid_2d": GRID_2D,
            "family_colors": FAMILY_COLORS,
            "small_family_min_n": MIN_FAMILY_ENVELOPE_N,
            "neighbor_k": K_NEIGHBORS,
        },
        "models": viewer_models,
        "traits": {
            "qwen": trait.rename(columns={"pc1": "x", "pc2": "y", "pc3": "z"}).to_dict("records")
        },
        "neighborhood_recurrence": pd.DataFrame(recurrence_rows).to_dict("records"),
    }
    (OUT / "terrain_viewer_data.json").write_text(json.dumps(viewer_payload, separators=(",", ":")), encoding="utf-8")

    inputs = [COORDINATE_SOURCE, COORDINATE_MANIFEST, FAMILY_SOURCE, FAMILY_SUMMARY_SOURCE, ROLE_ID_SOURCE, TRAIT_SOURCE]
    manifest = {
        "analysis_model": "GPT-5.5",
        "generated_utc": subprocess.check_output(
            ["git", "show", "-s", "--format=%cI", "5c2814f7554d26cfce97cb83fd0cda34ffbf2333"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "method_freeze_commit": "5c2814f7554d26cfce97cb83fd0cda34ffbf2333",
        "scope": "model-only curated-role sample occupancy; no human input",
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for path in inputs
        ]
        + [{"path": ALIGNMENT_GIT_PATH, "sha256": sha256_bytes(alignment_bytes), "bytes": len(alignment_bytes), "access": "git object; model-only transform"}],
        "coordinate_verification": {
            "models": MODEL_ORDER,
            "roles_per_model": coords.groupby("model").size().to_dict(),
            "identical_role_sets": True,
            "finite_native_coordinates": bool(np.isfinite(coords[["native_pc1", "native_pc2", "native_pc3"]]).all().all()),
            "no_role_vector_recomputation": True,
        },
        "parameters": {
            "kde": "scipy gaussian_kde full covariance Scott",
            "bandwidth_multipliers": BANDWIDTH_MULTIPLIERS,
            "grid_3d": GRID_3D,
            "grid_2d": GRID_2D,
            "coverage_levels": TARGET_COVERAGES,
            "nearest_neighbor_k": K_NEIGHBORS,
            "minimum_family_envelope_n": MIN_FAMILY_ENVELOPE_N,
            "fallback_seed": 120926,
        },
        "boundaries": {
            "roles_only_define_occupancy": True,
            "trait_landmarks_excluded_from_density": True,
            "human_artifacts_loaded": False,
            "human_model_correspondence_loaded": False,
            "new_inference": False,
            "activation_extraction": False,
            "external_api": False,
            "gpu": False,
            "runpod": False,
        },
    }
    (OUT / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "rows": {"coordinates": len(coords), "families": len(family), "neighbors": len(neighbor_rows), "recurrence": len(recurrence_rows)},
        "coverage": pd.DataFrame(coverage_rows)[["model", "target_sample_coverage_percent", "achieved_sample_percent"]].to_dict("records"),
        "files": sorted(path.name for path in OUT.iterdir() if path.is_file()),
    }, indent=2))


if __name__ == "__main__":
    main()
