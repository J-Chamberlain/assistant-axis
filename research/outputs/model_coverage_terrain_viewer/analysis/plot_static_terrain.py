#!/usr/bin/env python3
"""Render deterministic static companion figures from the frozen terrain tables."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.ndimage import binary_erosion


HERE = Path(__file__).resolve().parent
OUT = HERE.parent
FIGURES = OUT / "figures"
FIGURES.mkdir(exist_ok=True)

MODEL_ORDER = ["qwen", "llama", "gemma"]
MODEL_LABEL = {"qwen": "Qwen 3 32B", "llama": "LLaMA 3.3 70B", "gemma": "Gemma 2 27B"}
FAMILY_COLORS = {
    "MFamily_A": "#2D7FF9",
    "MFamily_B": "#E45756",
    "MFamily_C": "#54A24B",
    "MFamily_D": "#B279A2",
    "MFamily_E": "#F2CF5B",
    "Unassigned": "#8A93A3",
}
LEVEL_COLORS = {"50": "#1256A0", "80": "#4E9BD3", "95": "#A9D4EE"}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 12,
        "axes.labelsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


def save(fig: plt.Figure, stem: str, svg: bool = False) -> list[str]:
    outputs = []
    png = FIGURES / f"{stem}.png"
    fig.savefig(png, dpi=190, bbox_inches="tight")
    outputs.append(str(png.relative_to(OUT)))
    if svg:
        vector = FIGURES / f"{stem}.svg"
        fig.savefig(vector, bbox_inches="tight")
        outputs.append(str(vector.relative_to(OUT)))
    plt.close(fig)
    return outputs


def style_3d(ax, title: str) -> None:
    ax.set_title(title, pad=12)
    ax.set_xlabel("Native PC1")
    ax.set_ylabel("Native PC2")
    ax.set_zlabel("Native PC3")
    ax.view_init(elev=22, azim=-55)
    ax.grid(True, alpha=0.16)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_alpha(0.02)


def shell_points(model_payload: dict, level: str, max_points: int = 2400) -> np.ndarray:
    axes = [np.asarray(item, dtype=float) for item in model_payload["kde"]["axes"]]
    shape = tuple(model_payload["kde"]["shape"])
    density = np.asarray(model_payload["kde"]["density"], dtype=float).reshape(shape)
    mask = density >= float(model_payload["kde"]["thresholds"][level])
    boundary = mask & ~binary_erosion(mask)
    indices = np.argwhere(boundary)
    if len(indices) > max_points:
        step = int(np.ceil(len(indices) / max_points))
        indices = indices[::step]
    return np.column_stack([axes[axis][indices[:, axis]] for axis in range(3)])


def family_legend() -> list:
    return [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=color, markeredgecolor="white", label=family.replace("MFamily_", "Family "), markersize=6)
        for family, color in FAMILY_COLORS.items()
    ]


def add_family_hulls(ax, payload: dict) -> None:
    for family, hull in payload.get("family_hulls", {}).items():
        vertices = np.asarray(hull["vertices"], dtype=float)
        faces = vertices[np.asarray(hull["simplices"], dtype=int)]
        mesh = Poly3DCollection(faces, alpha=0.035, facecolor=FAMILY_COLORS[family], edgecolor=FAMILY_COLORS[family], linewidth=0.18)
        ax.add_collection3d(mesh)


def main() -> None:
    data = json.loads((OUT / "terrain_viewer_data.json").read_text(encoding="utf-8"))
    coords = pd.read_csv(OUT / "role_coordinates.csv")
    density = pd.read_csv(OUT / "role_density_scores.csv")
    sparsity = pd.read_csv(OUT / "role_sparsity_scores.csv")
    bandwidth = pd.read_csv(OUT / "density_bandwidth_sensitivity.csv")
    recurrence = pd.read_csv(OUT / "cross_model_neighborhood_recurrence.csv")

    inventory: list[dict] = []
    axis_pairs = [
        ("pc1_pc2", "native_pc1", "native_pc2", "Native PC1", "Native PC2"),
        ("pc1_pc3", "native_pc1", "native_pc3", "Native PC1", "Native PC3"),
        ("pc2_pc3", "native_pc2", "native_pc3", "Native PC2", "Native PC3"),
    ]

    for model in MODEL_ORDER:
        frame = coords[coords.model.eq(model)].sort_values("role").reset_index(drop=True)
        den = density[density.model.eq(model)].set_index("role").loc[frame.role]
        spa = sparsity[sparsity.model.eq(model)].set_index("role").loc[frame.role]
        payload = data["models"][model]
        x = frame[["native_pc1", "native_pc2", "native_pc3"]].to_numpy(float)

        fig = plt.figure(figsize=(7.2, 6.1))
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(x[:, 0], x[:, 1], x[:, 2], s=15, c="#315C78", alpha=0.72, edgecolor="white", linewidth=0.22)
        style_3d(ax, f"{MODEL_LABEL[model]} — 275 sampled roles")
        fig.text(0.5, 0.01, "Curated role points in the model's native PCA space; not population observations.", ha="center", color="#4A5568")
        files = save(fig, f"{model}_pc1_pc3_point_cloud")
        inventory.append({"figure_id": f"{model}_point_cloud", "files": ";".join(files), "description": "Native PC1-PC3 sampled-role point cloud", "source_data": "role_coordinates.csv"})

        fig = plt.figure(figsize=(7.2, 6.1))
        ax = fig.add_subplot(111, projection="3d")
        for level, alpha, size in [("95", 0.055, 2.0), ("80", 0.085, 2.4), ("50", 0.13, 2.8)]:
            shell = shell_points(payload, level)
            ax.scatter(shell[:, 0], shell[:, 1], shell[:, 2], s=size, c=LEVEL_COLORS[level], alpha=alpha, depthshade=False)
        ax.scatter(x[:, 0], x[:, 1], x[:, 2], s=10, c="#263848", alpha=0.62, edgecolor="none")
        style_3d(ax, f"{MODEL_LABEL[model]} — sampled occupancy cloud")
        ax.legend(
            handles=[Patch(facecolor=LEVEL_COLORS[level], alpha=0.5, label=f"~{level}% sampled-role region") for level in ["50", "80", "95"]],
            loc="upper left",
            frameon=False,
        )
        fig.text(0.5, 0.01, "Scott-KDE boundaries describe this selected inventory; they are not probability or confidence regions.", ha="center", color="#4A5568")
        files = save(fig, f"{model}_occupancy_cloud")
        inventory.append({"figure_id": f"{model}_occupancy_cloud", "files": ";".join(files), "description": "Native 50/80/95% sampled-role KDE boundaries", "source_data": "terrain_viewer_data.json;coverage_region_summary.csv"})

        for pair, xcol, ycol, xlabel, ylabel in axis_pairs:
            grid = payload["grids2d"][pair]
            gx, gy, gz = np.asarray(grid["x"]), np.asarray(grid["y"]), np.asarray(grid["z"])
            fig, ax = plt.subplots(figsize=(7.2, 5.7))
            levels = np.quantile(gz[gz > 0], [0.55, 0.70, 0.82, 0.91, 0.97])
            cf = ax.contourf(gx, gy, gz, levels=np.r_[0, levels, gz.max()], cmap="Blues", alpha=0.86)
            ax.contour(gx, gy, gz, levels=levels, colors="#244862", linewidths=0.55, alpha=0.7)
            ax.scatter(frame[xcol], frame[ycol], s=11, c="#1F3446", alpha=0.62, edgecolor="white", linewidth=0.18)
            ax.set_title(f"{MODEL_LABEL[model]} — {xlabel} × {ylabel} role-sample density")
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            cb = fig.colorbar(cf, ax=ax, pad=0.02)
            cb.set_label("Native-space KDE (model-specific units)")
            fig.text(0.5, 0.01, "Contours estimate coverage of the 275 sampled roles, not population density.", ha="center", color="#4A5568")
            files = save(fig, f"{model}_{pair}_density_contour", svg=True)
            inventory.append({"figure_id": f"{model}_{pair}_contour", "files": ";".join(files), "description": f"Native {xlabel} × {ylabel} role-only KDE contours", "source_data": "terrain_viewer_data.json;role_coordinates.csv"})

        fig = plt.figure(figsize=(7.2, 6.1))
        ax = fig.add_subplot(111, projection="3d")
        colors = [FAMILY_COLORS[value] for value in frame.consensus_family_id]
        ax.scatter(x[:, 0], x[:, 1], x[:, 2], s=18, c=colors, alpha=0.8, edgecolor="white", linewidth=0.25)
        add_family_hulls(ax, payload)
        style_3d(ax, f"{MODEL_LABEL[model]} — frozen consensus-family placement")
        ax.legend(handles=family_legend(), loc="upper left", frameon=False, ncol=2)
        fig.text(0.5, 0.01, "Translucent meshes are convex sample envelopes for families with N≥10; E is points only where present.", ha="center", color="#4A5568")
        files = save(fig, f"{model}_family_view")
        inventory.append({"figure_id": f"{model}_family_view", "files": ";".join(files), "description": "Frozen family placement and eligible convex sample envelopes", "source_data": "role_coordinates.csv;role_family_membership.csv;terrain_viewer_data.json"})

        fig = plt.figure(figsize=(7.2, 6.1))
        ax = fig.add_subplot(111, projection="3d")
        sc = ax.scatter(x[:, 0], x[:, 1], x[:, 2], s=18, c=spa.within_model_sparsity_percentile, cmap="magma", alpha=0.84, edgecolor="white", linewidth=0.2)
        style_3d(ax, f"{MODEL_LABEL[model]} — local sample sparsity")
        cb = fig.colorbar(sc, ax=ax, shrink=0.72, pad=0.09)
        cb.set_label("Within-model sparsity percentile")
        fig.text(0.5, 0.01, "Higher values mean sparser placement within this curated inventory; not instability or improbability.", ha="center", color="#4A5568")
        files = save(fig, f"{model}_sparsity_view")
        inventory.append({"figure_id": f"{model}_sparsity_view", "files": ";".join(files), "description": "Native point cloud colored by inverse-KDE sparsity rank", "source_data": "role_coordinates.csv;role_sparsity_scores.csv"})

    fig = plt.figure(figsize=(14.2, 4.5))
    for index, model in enumerate(MODEL_ORDER, start=1):
        ax = fig.add_subplot(1, 3, index, projection="3d")
        frame = coords[coords.model.eq(model)].sort_values("role")
        xyz = frame[["native_pc1", "native_pc2", "native_pc3"]].to_numpy(float)
        ax.scatter(xyz[:, 0], xyz[:, 1], xyz[:, 2], s=9, c=[FAMILY_COLORS[v] for v in frame.consensus_family_id], alpha=0.74, edgecolor="none")
        style_3d(ax, MODEL_LABEL[model])
    fig.legend(handles=family_legend(), loc="lower center", ncol=6, frameon=False)
    fig.suptitle("Frozen family placement across linked native model spaces", y=1.01, fontsize=14)
    fig.text(0.5, 0.01, "Panels are native and not on a shared coordinate scale; color links unchanged family identities.", ha="center", color="#4A5568")
    files = save(fig, "cross_model_family_comparison")
    inventory.append({"figure_id": "cross_model_family_comparison", "files": ";".join(files), "description": "Family-colored linked native-space comparison", "source_data": "role_coordinates.csv;role_family_membership.csv"})

    fig, axes = plt.subplots(1, 3, figsize=(14.2, 5.8), sharey=False)
    for ax, model in zip(axes, MODEL_ORDER):
        den = density[density.model.eq(model)]
        dense = den.nlargest(8, "kde_density").sort_values("within_model_density_percentile")
        sparse = den.nsmallest(8, "kde_density").sort_values("within_model_density_percentile")
        combined = pd.concat([sparse, dense])
        colors = ["#C44E52" if value < 10 else "#3274A1" for value in combined.within_model_density_percentile]
        ax.barh(combined.role, combined.within_model_density_percentile, color=colors, alpha=0.82)
        ax.axvline(50, color="#7A8491", linewidth=0.8)
        ax.set_title(MODEL_LABEL[model])
        ax.set_xlabel("Density percentile")
        ax.set_xlim(0, 100)
    axes[0].set_ylabel("Sampled role")
    fig.suptitle("Densest and sparsest sampled roles by model", y=1.01, fontsize=14)
    fig.text(0.5, -0.02, "Blue marks dense sample placement; red marks sparse sample placement. Percentiles are within model.", ha="center", color="#4A5568")
    files = save(fig, "cross_model_density_sparsity_summary", svg=True)
    inventory.append({"figure_id": "cross_model_density_sparsity_summary", "files": ";".join(files), "description": "Top and bottom role-sample density ranks across models", "source_data": "role_density_scores.csv"})

    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.2), sharey=True)
    metrics = [
        ("role_density_rank_spearman_vs_primary", "Density-rank Spearman"),
        ("densest_decile_jaccard_vs_primary", "Densest-decile Jaccard"),
        ("sparsest_decile_jaccard_vs_primary", "Sparsest-decile Jaccard"),
    ]
    for ax, (metric, label) in zip(axes, metrics):
        for model, color in zip(MODEL_ORDER, ["#2D7FF9", "#E45756", "#54A24B"]):
            part = bandwidth[bandwidth.model.eq(model)].sort_values("bandwidth_multiplier")
            ax.plot(part.bandwidth_multiplier, part[metric], marker="o", label=MODEL_LABEL[model], color=color)
        ax.axhline(0.90 if "spearman" in metric else 0.70, color="#6C7480", linestyle="--", linewidth=0.9, label="Frozen robustness rule" if ax is axes[0] else None)
        ax.set_title(label)
        ax.set_xlabel("Scott bandwidth multiplier")
        ax.set_xticks([0.75, 1.0, 1.25])
        ax.set_ylim(0.55 if "jaccard" in metric else 0.88, 1.02)
    axes[0].set_ylabel("Agreement with primary bandwidth")
    handles, labels = axes[0].get_legend_handles_labels()
    model_handles = [Line2D([0], [0], color=c, marker="o", label=MODEL_LABEL[m]) for m, c in zip(MODEL_ORDER, ["#2D7FF9", "#E45756", "#54A24B"])]
    fig.legend(handles=model_handles + [Line2D([0], [0], color="#6C7480", linestyle="--", label="Frozen threshold")], loc="lower center", ncol=4, frameon=False)
    fig.suptitle("Bandwidth sensitivity of sampled density and sparsity", y=1.02, fontsize=14)
    files = save(fig, "bandwidth_sensitivity", svg=True)
    inventory.append({"figure_id": "bandwidth_sensitivity", "files": ";".join(files), "description": "Frozen 0.75×/1×/1.25× Scott sensitivity", "source_data": "density_bandwidth_sensitivity.csv"})

    fig, ax = plt.subplots(figsize=(8.2, 5.3))
    ax.hist(recurrence.mean_pairwise_neighbor_jaccard_k10, bins=np.linspace(0, 0.6, 19), color="#3A769B", alpha=0.85, edgecolor="white")
    median = recurrence.mean_pairwise_neighbor_jaccard_k10.median()
    ax.axvline(median, color="#C44E52", linewidth=1.5, label=f"Median = {median:.3f}")
    ax.set_title("Cross-model recurrence of local 10-role neighborhoods")
    ax.set_xlabel("Mean pairwise Jaccard across three model pairs")
    ax.set_ylabel("Sampled roles")
    ax.legend(frameon=False)
    fig.text(0.5, 0.01, "Neighborhoods use model-local standardized native PC1-PC3 distances; this does not equate native axes.", ha="center", color="#4A5568")
    files = save(fig, "cross_model_neighborhood_recurrence", svg=True)
    inventory.append({"figure_id": "cross_model_neighborhood_recurrence", "files": ";".join(files), "description": "Distribution of shared-role local-topology recurrence", "source_data": "cross_model_neighborhood_recurrence.csv"})

    pd.DataFrame(inventory).to_csv(OUT / "figure_inventory.csv", index=False)
    print(json.dumps({"figure_records": len(inventory), "files": len(list(FIGURES.glob('*')))}, indent=2))


if __name__ == "__main__":
    main()
