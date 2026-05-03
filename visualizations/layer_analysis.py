from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import torch
from scipy.stats import spearmanr

from research_common import (
    DEFAULT_LAYER,
    MODEL_NAME,
    OUT_DIR,
    assign_cluster_labels,
    build_layer_dataframe,
    compute_projection_matrix,
    load_axis_tensor,
    load_role_tensor,
    load_roles,
    normalize_name,
    progress,
    save_pca_plot,
    save_ranking_plot,
    standardize,
)


EXTREME_TOP = ["proofreader", "screener", "grader", "editor", "examiner"]
EXTREME_BOTTOM = ["tree", "narcissist", "criminal", "prophet", "eldritch"]


def run_layer_analysis() -> dict[str, object]:
    roles = load_roles()
    role_tensor = load_role_tensor(roles)
    axis_tensor = load_axis_tensor()

    progress("Computing layer-by-layer axis projections ...")
    projection_matrix = compute_projection_matrix(role_tensor, axis_tensor).cpu().numpy()
    ranking_df = build_layer_dataframe(roles, role_tensor, axis_tensor, layer=DEFAULT_LAYER)
    ordered_roles = ranking_df["role"].tolist()
    ordered_labels = ranking_df["character"].tolist()
    ordered_indices = [roles.index(role) for role in ordered_roles]
    ordered_projection_matrix = projection_matrix[ordered_indices, :]

    progress("Saving layer-depth heatmap ...")
    plt.figure(figsize=(24, 60))
    plt.imshow(ordered_projection_matrix, aspect="auto", cmap="RdBu", interpolation="nearest")
    plt.colorbar(label="Projection onto layer axis")
    plt.xticks(range(projection_matrix.shape[1]))
    plt.yticks(range(len(ordered_labels)), ordered_labels, fontsize=5)
    plt.xlabel("Layer")
    plt.ylabel("Character (ordered by layer-22 rank)")
    plt.title(f"Assistant Axis Projection Across Depth ({MODEL_NAME})")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "layer_depth_heatmap.png", dpi=200)
    plt.close()

    progress("Saving extreme layer profiles ...")
    extreme_roles = EXTREME_TOP + EXTREME_BOTTOM
    profile_rows = []
    for role in extreme_roles:
        idx = roles.index(role)
        for layer, value in enumerate(projection_matrix[idx]):
            profile_rows.append(
                {
                    "role": normalize_name(role),
                    "layer": layer,
                    "projection": float(value),
                    "group": "top5" if role in EXTREME_TOP else "bottom5",
                }
            )
    profile_df = pd.DataFrame(profile_rows)
    profile_fig = px.line(
        profile_df,
        x="layer",
        y="projection",
        color="role",
        line_dash="group",
        markers=True,
        title=f"Layer Profiles of Most and Least Assistant-like Characters ({MODEL_NAME})",
    )
    profile_fig.write_html(OUT_DIR / "layer_profiles_extremes.html")

    progress("Computing discriminative layers ...")
    layer_variances = projection_matrix.var(axis=0)
    var_df = pd.DataFrame({"layer": np.arange(len(layer_variances)), "variance": layer_variances})
    top_layers = var_df.sort_values("variance", ascending=False).head(3).reset_index(drop=True)

    plt.figure(figsize=(12, 6))
    plt.plot(var_df["layer"], var_df["variance"], marker="o")
    for row in top_layers.itertuples(index=False):
        plt.scatter(row.layer, row.variance, color="red")
        plt.text(row.layer, row.variance, f"L{row.layer}", fontsize=9, ha="left", va="bottom")
    plt.xlabel("Layer")
    plt.ylabel("Variance of axis projections across characters")
    plt.title(f"Persona Differentiation by Layer ({MODEL_NAME})")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "layer_discrimination.png", dpi=200)
    plt.close()

    best_layer = int(top_layers.iloc[0]["layer"])
    progress(f"Best discriminative layer is {best_layer}; saving comparison PCA and ranking ...")
    best_df = build_layer_dataframe(roles, role_tensor, axis_tensor, layer=best_layer)
    best_col = f"axis_projection_layer{best_layer}"
    layer_vectors = role_tensor[:, best_layer, :].cpu().numpy()
    analysis_matrix = standardize(layer_vectors)

    save_pca_plot(
        best_df,
        analysis_matrix,
        best_col,
        OUT_DIR / "pca_3d_best_layer.html",
        f"Persona Space PCA (Layer {best_layer}, {MODEL_NAME})",
    )
    save_ranking_plot(
        best_df,
        best_col,
        OUT_DIR / "axis_ranking_best_layer.html",
        f"Assistant Axis Ranking (Layer {best_layer}, {MODEL_NAME})",
    )

    layer22_order = ranking_df["role"].tolist()
    best_order = best_df["role"].tolist()
    order_changes = {
        role: abs((layer22_order.index(role) + 1) - (best_order.index(role) + 1))
        for role in roles
    }
    mean_abs_shift = float(np.mean(list(order_changes.values())))
    max_shift_roles = sorted(order_changes.items(), key=lambda item: item[1], reverse=True)[:10]
    rank_correlation = float(spearmanr(range(len(roles)), [best_order.index(role) for role in layer22_order]).statistic)

    assignments, _, _ = assign_cluster_labels(roles, role_tensor[:, DEFAULT_LAYER, :])

    return {
        "projection_matrix": projection_matrix,
        "layer22_ranking": ranking_df,
        "best_layer_ranking": best_df,
        "top_layers": top_layers,
        "best_layer": best_layer,
        "mean_abs_shift": mean_abs_shift,
        "max_shift_roles": max_shift_roles,
        "rank_correlation": rank_correlation,
        "cluster_assignments": assignments,
        "ordered_roles": ordered_roles,
    }


def main() -> None:
    results = run_layer_analysis()
    print("Top 3 most discriminative layers:")
    for row in results["top_layers"].itertuples(index=False):
        print(f"Layer {int(row.layer)} variance={row.variance:.6f}")
    print(f"Best layer: {results['best_layer']}")
    print(f"Mean absolute rank shift from layer {DEFAULT_LAYER}: {results['mean_abs_shift']:.2f}")
    print(f"Spearman rank correlation vs layer {DEFAULT_LAYER}: {results['rank_correlation']:.4f}")
    print("Largest ordering changes:")
    for role, shift in results["max_shift_roles"]:
        print(f"{normalize_name(role)}\tshift={shift}")


if __name__ == "__main__":
    main()
