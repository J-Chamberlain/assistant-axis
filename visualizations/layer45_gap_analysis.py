from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from research_common import (
    DEFAULT_LAYER,
    MODEL_NAME,
    OUT_DIR,
    build_layer_dataframe,
    load_axis_tensor,
    load_role_tensor,
    load_roles,
    progress,
    save_pca_plot,
    save_ranking_plot,
    save_tsne_plot,
    standardize,
)


TARGET_LAYER = 45


def build_comparison_dataframe(layer22_df: pd.DataFrame, layer45_df: pd.DataFrame) -> pd.DataFrame:
    rank22 = layer22_df.set_index("role")["rank"]
    rank45 = layer45_df.set_index("role")["rank"]
    proj22 = layer22_df.set_index("role")[f"axis_projection_layer{DEFAULT_LAYER}"]
    proj45 = layer45_df.set_index("role")[f"axis_projection_layer{TARGET_LAYER}"]
    z22 = (proj22 - proj22.mean()) / proj22.std()
    z45 = (proj45 - proj45.mean()) / proj45.std()
    labels = layer22_df.set_index("role")["character"]

    rows = []
    for role in rank22.index:
        delta = int(rank22[role] - rank45[role])
        if delta > 10:
            movement = "up"
        elif delta < -10:
            movement = "down"
        else:
            movement = "stable"
        rows.append(
            {
                "role": role,
                "character": labels[role],
                "rank22": int(rank22[role]),
                "rank45": int(rank45[role]),
                "proj22": float(proj22[role]),
                "proj45": float(proj45[role]),
                "zproj22": float(z22[role]),
                "zproj45": float(z45[role]),
                "rank_delta_22_minus_45": delta,
                "movement": movement,
            }
        )
    return pd.DataFrame(rows)


def subset_for_extremes(df: pd.DataFrame, rank_column: str) -> pd.DataFrame:
    top = df.nsmallest(40, rank_column)
    bottom = df.nlargest(40, rank_column)
    return pd.concat([top, bottom], ignore_index=True)


def build_side_by_side_chart(comparison_df: pd.DataFrame) -> None:
    layer22_subset = subset_for_extremes(comparison_df, "rank22").sort_values("rank22", ascending=False)
    layer45_subset = subset_for_extremes(comparison_df, "rank45").sort_values("rank45", ascending=False)
    color_map = {"up": "#1f77b4", "stable": "#7f7f7f", "down": "#d62728"}
    projection_min = float(min(comparison_df["zproj22"].min(), comparison_df["zproj45"].min()))
    projection_max = float(max(comparison_df["zproj22"].max(), comparison_df["zproj45"].max()))

    fig = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=False,
        subplot_titles=("Layer 22: Top/Bottom 40", "Layer 45: Top/Bottom 40"),
        horizontal_spacing=0.13,
    )

    for col_idx, subset, proj_col, raw_proj_col, rank_col in [
        (1, layer22_subset, "zproj22", "proj22", "rank22"),
        (2, layer45_subset, "zproj45", "proj45", "rank45"),
    ]:
        fig.add_trace(
            go.Bar(
                x=subset[proj_col],
                y=subset["character"],
                orientation="h",
                marker={"color": [color_map[m] for m in subset["movement"]]},
                customdata=subset[["rank22", "rank45", "rank_delta_22_minus_45", raw_proj_col]],
                hovertemplate=(
                    "Character: %{y}<br>"
                    "Standardized projection: %{x:.3f}<br>"
                    "Raw projection: %{customdata[3]:.3f}<br>"
                    "Layer 22 rank: %{customdata[0]}<br>"
                    "Layer 45 rank: %{customdata[1]}<br>"
                    "Rank delta (22-45): %{customdata[2]}<extra></extra>"
                ),
                showlegend=False,
            ),
            row=1,
            col=col_idx,
        )
        fig.update_yaxes(categoryorder="array", categoryarray=subset["character"].tolist(), row=1, col=col_idx)
        fig.update_xaxes(title_text="Standardized axis projection", range=[projection_min, projection_max], row=1, col=col_idx)

    fig.update_layout(
        title=f"Layer 22 vs Layer 45 Assistant-Axis Extremes ({MODEL_NAME})",
        height=2200,
        width=1800,
    )

    legend_traces = [
        go.Bar(name="Ranked Up >10", x=[None], y=[None], marker_color=color_map["up"]),
        go.Bar(name="Stable ±10", x=[None], y=[None], marker_color=color_map["stable"]),
        go.Bar(name="Ranked Down >10", x=[None], y=[None], marker_color=color_map["down"]),
    ]
    for trace in legend_traces:
        fig.add_trace(trace)
    fig.update_layout(barmode="overlay", legend={"orientation": "h", "y": 1.05})
    fig.write_html(OUT_DIR / "layer22_vs_layer45_comparison.html")


def main() -> None:
    roles = load_roles()
    role_tensor = load_role_tensor(roles)
    axis_tensor = load_axis_tensor()

    progress("Building layer 22 and layer 45 rankings ...")
    layer22_df = build_layer_dataframe(roles, role_tensor, axis_tensor, layer=DEFAULT_LAYER)
    layer45_df = build_layer_dataframe(roles, role_tensor, axis_tensor, layer=TARGET_LAYER)

    progress("Saving layer-45 PCA, rankings, and t-SNE visualizations ...")
    layer45_vectors = role_tensor[:, TARGET_LAYER, :].cpu().numpy()
    analysis_matrix = standardize(layer45_vectors)
    projection_col = f"axis_projection_layer{TARGET_LAYER}"

    save_pca_plot(
        layer45_df,
        analysis_matrix,
        projection_col,
        OUT_DIR / "pca_3d_layer45.html",
        f"Persona Space PCA (Layer {TARGET_LAYER}, {MODEL_NAME})",
    )
    save_ranking_plot(
        layer45_df,
        projection_col,
        OUT_DIR / "axis_ranking_layer45.html",
        f"Assistant Axis Ranking (Layer {TARGET_LAYER}, {MODEL_NAME})",
        OUT_DIR / "axis_ranking_layer45.png",
        png_extreme_count=40,
    )
    save_tsne_plot(
        layer45_df,
        analysis_matrix,
        projection_col,
        OUT_DIR / "tsne_2d_layer45.html",
        f"Persona Space t-SNE (Layer {TARGET_LAYER}, {MODEL_NAME})",
    )

    jung = json.loads((OUT_DIR / "jungian_mapping.json").read_text())
    layer45_jung_df = layer45_df.copy()
    layer45_jung_df["JungianArchetype"] = layer45_jung_df["role"].map(jung)
    save_tsne_plot(
        layer45_jung_df,
        analysis_matrix,
        "JungianArchetype",
        OUT_DIR / "tsne_jungian_layer45.html",
        f"Persona Space t-SNE by Jungian Archetype (Layer {TARGET_LAYER}, {MODEL_NAME})",
    )

    comparison_df = build_comparison_dataframe(layer22_df, layer45_df)
    build_side_by_side_chart(comparison_df)

    print("\nTOP 20 AT LAYER 45")
    print(layer45_df.head(20).to_string(index=False))
    print("\nBOTTOM 20 AT LAYER 45")
    print(layer45_df.tail(20).to_string(index=False))

    assistant22 = int(layer22_df.loc[layer22_df["role"] == "assistant", "rank"].iloc[0])
    assistant45 = int(layer45_df.loc[layer45_df["role"] == "assistant", "rank"].iloc[0])
    robot22 = int(layer22_df.loc[layer22_df["role"] == "robot", "rank"].iloc[0])
    robot45 = int(layer45_df.loc[layer45_df["role"] == "robot", "rank"].iloc[0])

    print("\nANOMALY CHECK")
    if assistant45 < assistant22:
        assistant_note = "gets stronger"
    elif assistant45 > assistant22:
        assistant_note = "partially resolves"
    else:
        assistant_note = "persists unchanged"

    if robot45 < robot22:
        robot_note = "gets stronger"
    elif robot45 > robot22:
        robot_note = "partially resolves"
    else:
        robot_note = "persists unchanged"

    print(f"assistant rank: layer22={assistant22}, layer45={assistant45} -> anomaly {assistant_note}")
    print(f"robot rank: layer22={robot22}, layer45={robot45} -> anomaly {robot_note}")

    moved = comparison_df.sort_values("rank_delta_22_minus_45", ascending=False)
    print("\nBIGGEST RISES FROM LAYER 22 TO LAYER 45")
    print(moved.head(15)[["character", "rank22", "rank45", "rank_delta_22_minus_45", "movement"]].to_string(index=False))
    print("\nBIGGEST DROPS FROM LAYER 22 TO LAYER 45")
    print(moved.tail(15)[["character", "rank22", "rank45", "rank_delta_22_minus_45", "movement"]].to_string(index=False))


if __name__ == "__main__":
    main()
