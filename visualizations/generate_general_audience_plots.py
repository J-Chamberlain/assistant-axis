from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle


BASE = Path(__file__).resolve().parent
OUT = BASE / "general-audience"
OUT.mkdir(exist_ok=True)

CLUSTER_ORDER = [
    "editorial",
    "procedural_professional",
    "grounded_social",
    "other",
    "combative_iconoclast",
    "trickster_chaos",
    "mythic_spiritual",
]

FRIENDLY = {
    "editorial": "Editorial\ncheckers",
    "procedural_professional": "Careful\nprofessionals",
    "grounded_social": "Grounded\nsocial roles",
    "other": "Unsettled\nmisc. roles",
    "combative_iconoclast": "Organized\nopposition",
    "trickster_chaos": "Playful\nchaos",
    "mythic_spiritual": "Mythic /\nspiritual",
}

SHORT = {
    "editorial": "Editorial",
    "procedural_professional": "Careful pros",
    "grounded_social": "Social",
    "other": "Unsettled",
    "combative_iconoclast": "Opposition",
    "trickster_chaos": "Chaos",
    "mythic_spiritual": "Mythic",
}

NODE_LABELS = {
    "editorial": "Editorial",
    "procedural_professional": "Careful\npros",
    "grounded_social": "Social",
    "other": "Mixed\nroles",
    "combative_iconoclast": "Oppose",
    "trickster_chaos": "Chaos",
    "mythic_spiritual": "Mythic",
}

PAPER_FAMILY_LABELS = {
    "editorial": "editorial",
    "procedural_professional": "procedural-professional",
    "grounded_social": "grounded-social",
    "other": "other",
    "combative_iconoclast": "combative-iconoclast",
    "trickster_chaos": "trickster-chaos",
    "mythic_spiritual": "mythic-spiritual",
}

MAP_LABEL_OFFSETS = {
    "procedural_professional": (0.0, 0.42, "center"),
    "editorial": (0.0, -0.28, "center"),
    "combative_iconoclast": (0.0, -0.26, "center"),
    "trickster_chaos": (0.0, -0.25, "center"),
    "other": (0.0, 0.27, "center"),
    "grounded_social": (0.0, 0.32, "center"),
    "mythic_spiritual": (0.0, 0.34, "center"),
}

COLORS = {
    "editorial": "#315F72",
    "procedural_professional": "#5C8F78",
    "grounded_social": "#9DBB8A",
    "other": "#B99B72",
    "combative_iconoclast": "#B35F49",
    "trickster_chaos": "#C9863E",
    "mythic_spiritual": "#7B638D",
}

BG = "#F6F1E7"
INK = "#2F2A24"
MUTED = "#6E665B"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ranking = pd.read_csv(BASE / "full_ranking.csv")
    distances = pd.read_csv(BASE / "cluster_distance_matrix.csv").set_index("cluster_label")
    distances = distances.loc[CLUSTER_ORDER, CLUSTER_ORDER]
    traits = pd.read_csv(BASE / "cluster_trait_profiles.csv")
    return ranking, distances, traits


def finish(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / f"{name}.png", dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def add_subtitle(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.06, 0.965, title, fontsize=19, weight="bold", color=INK, ha="left", va="top")
    fig.text(0.06, 0.925, subtitle, fontsize=10.5, color=MUTED, ha="left", va="top")


def plot_ranked_roles(ranking: pd.DataFrame) -> None:
    top = ranking.head(32).copy()
    assistant = ranking[ranking["character"] == "assistant"].head(1)
    if not assistant.empty and int(assistant.iloc[0]["rank"]) > len(top):
        top = pd.concat([top, assistant], ignore_index=True)
    top["label"] = top.apply(lambda r: f"{int(r['rank'])}. {r['character'].replace('_', ' ')}", axis=1)
    top["score"] = top["axis_projection_layer22"] - ranking["axis_projection_layer22"].min()
    top["is_assistant"] = top["character"].eq("assistant")

    fig, ax = plt.subplots(figsize=(9, 10), facecolor=BG)
    ax.set_facecolor(BG)
    y = np.arange(len(top))
    colors = [COLORS[c] for c in top["cluster_label"]]
    ax.barh(y, top["score"], color=colors, height=0.72)
    ax.set_yticks(y)
    ax.set_yticklabels(top["label"], fontsize=8.8, color=INK)
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_xlabel("")
    ax.spines[:].set_visible(False)
    ax.grid(axis="x", color="#D7CCBA", linewidth=0.7)

    for idx, row in top.iterrows():
        if row["is_assistant"]:
            ax.add_patch(
                Rectangle(
                    (0, idx - 0.46),
                    row["score"],
                    0.92,
                    fill=False,
                    edgecolor="#2F2A24",
                    linewidth=2.2,
                )
            )
            ax.text(row["score"] * 0.55, idx, "literal 'assistant'", ha="center", va="center", fontsize=8.5, color=INK, weight="bold")

    add_subtitle(
        fig,
        "The assistant axis mostly selects for careful evaluation",
        "The top roles are checkers, reviewers, analysts, and planners; the literal word 'assistant' appears lower.",
    )
    fig.subplots_adjust(top=0.86, left=0.24, right=0.96)
    finish(fig, "01_axis_top_roles")


def classical_mds(distances: pd.DataFrame) -> np.ndarray:
    d = distances.to_numpy(float)
    n = d.shape[0]
    j = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * j @ (d ** 2) @ j
    vals, vecs = np.linalg.eigh(b)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    coords = vecs[:, :2] * np.sqrt(np.maximum(vals[:2], 0))
    # Orient the map so careful professionals sit on the left and outer regions on the right.
    if coords[CLUSTER_ORDER.index("procedural_professional"), 0] > coords[CLUSTER_ORDER.index("trickster_chaos"), 0]:
        coords[:, 0] *= -1
    if coords[CLUSTER_ORDER.index("mythic_spiritual"), 1] < coords[CLUSTER_ORDER.index("grounded_social"), 1]:
        coords[:, 1] *= -1
    return coords


def plot_neighborhood_map(distances: pd.DataFrame, ranking: pd.DataFrame) -> None:
    _ = classical_mds(distances)
    coords_by_cluster = {
        "procedural_professional": (-1.6, 0.28),
        "editorial": (-1.45, -0.82),
        "combative_iconoclast": (0.35, -0.52),
        "trickster_chaos": (0.98, -0.16),
        "other": (1.48, 0.22),
        "grounded_social": (1.75, 0.78),
        "mythic_spiritual": (0.92, 1.05),
    }
    coords = np.array([coords_by_cluster[c] for c in CLUSTER_ORDER], dtype=float)
    counts = ranking.groupby("cluster_label").size().reindex(CLUSTER_ORDER)
    sizes = 600 + 2900 * (counts / counts.max())

    fig, ax = plt.subplots(figsize=(9, 7), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axhline(0, color="#D8CCB9", linewidth=1)
    ax.axvline(0, color="#D8CCB9", linewidth=1)

    for i, cluster in enumerate(CLUSTER_ORDER):
        x, y = coords[i]
        ax.scatter(x, y, s=sizes[cluster], color=COLORS[cluster], alpha=0.9, edgecolor="white", linewidth=2)
        dx, dy, ha = MAP_LABEL_OFFSETS[cluster]
        ax.text(x + dx, y + dy, PAPER_FAMILY_LABELS[cluster], ha=ha, va="center", fontsize=10.5, color=COLORS[cluster], weight="bold")
        ax.text(x, y, f"{counts[cluster]}", ha="center", va="center", fontsize=12, color="white", weight="bold")

    ax.text(-1.95, 1.15, "assistant-like basin", color=COLORS["procedural_professional"], fontsize=11, weight="bold")
    ax.text(0.85, -1.12, "outer persona web", color=COLORS["trickster_chaos"], fontsize=11, weight="bold")
    ax.set_xlim(-2.15, 2.15)
    ax.set_ylim(-1.25, 1.45)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[:].set_visible(False)
    add_subtitle(
        fig,
        "Persona space has neighborhoods",
        "Clusters close together have similar trait profiles; circle size shows how many roles are in each neighborhood.",
    )
    fig.subplots_adjust(top=0.86, left=0.04, right=0.98, bottom=0.04)
    finish(fig, "02_persona_neighborhood_map")


def plot_axis_neighbor_map(distances: pd.DataFrame, ranking: pd.DataFrame) -> None:
    cluster_stats = ranking.groupby("cluster_label").agg(
        axis_projection=("axis_projection_layer22", "mean"),
        count=("character", "size"),
    ).reindex(CLUSTER_ORDER)
    all_mean = float(ranking["axis_projection_layer22"].mean())
    all_std = float(ranking["axis_projection_layer22"].std())
    cluster_stats["axis_z"] = (cluster_stats["axis_projection"] - all_mean) / all_std

    nearest_dist = {}
    for cluster in CLUSTER_ORDER:
        row = distances.loc[cluster].drop(cluster)
        nearest_dist[cluster] = float(row.min())
    cluster_stats["nearest_distance"] = pd.Series(nearest_dist)
    sizes = 600 + 2900 * (cluster_stats["count"] / cluster_stats["count"].max())

    fig, ax = plt.subplots(figsize=(10.5, 7.0), facecolor=BG)
    ax.set_facecolor(BG)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#8D877E")
    ax.spines[["left", "bottom"]].set_linewidth(1.2)
    ax.grid(color="#D7CCBA", linewidth=0.8, alpha=0.8)

    for cluster in CLUSTER_ORDER:
        x = float(cluster_stats.loc[cluster, "axis_z"])
        y = float(cluster_stats.loc[cluster, "nearest_distance"])
        ax.scatter(x, y, s=float(sizes[cluster]), color=COLORS[cluster], alpha=0.9, edgecolor="white", linewidth=2.2, zorder=3)
        ax.text(x, y, f"{int(cluster_stats.loc[cluster, 'count'])}", ha="center", va="center", fontsize=12, color="white", weight="bold", zorder=4)

        if cluster == "procedural_professional":
            dx, dy, ha = 0.0, 0.073, "center"
        elif cluster == "mythic_spiritual":
            dx, dy, ha = 0.0, 0.065, "center"
        elif cluster == "editorial":
            dx, dy, ha = -0.03, 0.052, "right"
        elif cluster == "trickster_chaos":
            dx, dy, ha = 0.06, 0.048, "left"
        elif cluster == "grounded_social":
            dx, dy, ha = 0.0, 0.052, "center"
        elif cluster == "other":
            dx, dy, ha = 0.0, 0.044, "center"
        else:
            dx, dy, ha = 0.0, 0.054, "center"
        ax.text(x + dx, y + dy, PAPER_FAMILY_LABELS[cluster], ha=ha, va="center", fontsize=10.2, color=COLORS[cluster], weight="bold")

    xvals = cluster_stats["axis_z"].to_numpy(float)
    yvals = cluster_stats["nearest_distance"].to_numpy(float)
    ax.set_xlim(float(xvals.min()) - 0.28, float(xvals.max()) + 0.30)
    ax.set_ylim(max(0.0, float(yvals.min()) - 0.065), float(yvals.max()) + 0.09)

    ax.set_xlabel("")
    ax.set_ylabel("Distance to nearest neighboring family", fontsize=11, color=MUTED)
    ax.tick_params(colors=MUTED)

    y_arrow = -0.13
    ax.annotate(
        "",
        xy=(0.92, y_arrow),
        xytext=(0.08, y_arrow),
        xycoords=("axes fraction", "axes fraction"),
        textcoords=("axes fraction", "axes fraction"),
        arrowprops=dict(arrowstyle="<->", color="#8D877E", linewidth=1.4),
        annotation_clip=False,
    )
    ax.text(0.50, y_arrow - 0.025, "Assistant-axis position of family centroid", transform=ax.transAxes, ha="center", va="top", fontsize=10, color=MUTED)
    ax.text(0.08, y_arrow - 0.075, "role-playing", transform=ax.transAxes, ha="left", va="top", fontsize=10, color="#B35F49", weight="bold")
    ax.text(0.92, y_arrow - 0.075, "assistant-like", transform=ax.transAxes, ha="right", va="top", fontsize=10, color="#4F82D8", weight="bold")
    ax.text(0.01, 0.975, "more isolated", transform=ax.transAxes, ha="left", va="top", fontsize=9, color=MUTED)
    ax.text(0.01, 0.025, "more porous", transform=ax.transAxes, ha="left", va="bottom", fontsize=9, color=MUTED)

    fig.subplots_adjust(top=0.96, left=0.12, right=0.97, bottom=0.2)
    finish(fig, "02b_axis_neighbor_family_map")


def plot_distance_from_assistant(distances: pd.DataFrame) -> None:
    vals = distances.loc["procedural_professional"].drop("procedural_professional").sort_values()
    fig, ax = plt.subplots(figsize=(9, 5.4), facecolor=BG)
    ax.set_facecolor(BG)
    y = np.arange(len(vals))
    ax.barh(y, vals.values, color=[COLORS[c] for c in vals.index], height=0.65)
    ax.set_yticks(y)
    ax.set_yticklabels([SHORT[c] for c in vals.index], fontsize=10, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("Trait-space distance from careful professionals", color=MUTED)
    ax.spines[:].set_visible(False)
    ax.grid(axis="x", color="#D7CCBA", linewidth=0.8)
    for i, (cluster, value) in enumerate(vals.items()):
        label = "very close" if value < 0.2 else ("far" if value > 1.4 else "near")
        ax.text(value + 0.035, i, f"{value:.2f}  {label}", va="center", fontsize=9, color=INK)
    add_subtitle(
        fig,
        "The assistant-like region is isolated",
        "Editorial checking roles are nearby; social, mythic, oppositional, and chaotic regions are much farther away.",
    )
    fig.subplots_adjust(top=0.78, left=0.22, right=0.96, bottom=0.16)
    finish(fig, "03_distance_from_assistant_zone")


def plot_drift_path(distances: pd.DataFrame) -> None:
    path = [
        "procedural_professional",
        "editorial",
        "combative_iconoclast",
        "trickster_chaos",
        "other",
        "grounded_social",
    ]
    x = np.arange(len(path))
    y = np.zeros(len(path))

    fig, ax = plt.subplots(figsize=(11, 4.6), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-0.55, len(path) - 0.45)
    ax.set_ylim(-0.75, 0.92)
    ax.axis("off")

    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        d = float(distances.loc[a, b])
        color = "#A34F3B" if d > 1 else "#6E8F69"
        lw = 2.5 if d > 1 else 5.0
        arrow = FancyArrowPatch((x[i] + 0.32, y[i]), (x[i + 1] - 0.32, y[i + 1]), arrowstyle="-|>", mutation_scale=16, linewidth=lw, color=color, alpha=0.9)
        ax.add_patch(arrow)
        label = "big jump" if d > 1 else "easy step"
        ax.text((x[i] + x[i + 1]) / 2, 0.24, f"{d:.2f}\n{label}", ha="center", va="bottom", fontsize=9, color=INK)

    for i, cluster in enumerate(path):
        ax.scatter(x[i], y[i], s=2100, color=COLORS[cluster], edgecolor="white", linewidth=2.2, zorder=3)
        ax.text(x[i], y[i], NODE_LABELS[cluster], ha="center", va="center", fontsize=8.7, color="white", weight="bold", zorder=4, linespacing=0.92)

    ax.text(1.5, -0.5, "Leaving the assistant-like basin is the hard part.", ha="center", fontsize=10.5, color=INK, weight="bold")
    ax.text(4.0, -0.5, "After that, the outer regions are closely connected.", ha="center", fontsize=10.5, color=INK, weight="bold")
    add_subtitle(
        fig,
        "A simple picture of possible persona drift",
        "Distances come from cluster centroids: lower numbers mean a smaller movement in trait space.",
    )
    fig.subplots_adjust(top=0.78, left=0.03, right=0.99, bottom=0.05)
    finish(fig, "04_drift_path")


def plot_trait_cards(traits: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 4, figsize=(13, 7), facecolor=BG)
    axes = axes.ravel()
    for ax in axes:
        ax.set_facecolor(BG)
        ax.axis("off")

    for idx, cluster in enumerate(CLUSTER_ORDER):
        ax = axes[idx]
        top = traits[(traits["cluster_label"] == cluster) & (traits["direction"] == "top")].head(5)
        ax.add_patch(Rectangle((0.02, 0.05), 0.96, 0.86, facecolor="white", edgecolor="#D8CCB9", linewidth=1.2))
        ax.add_patch(Rectangle((0.02, 0.79), 0.96, 0.12, facecolor=COLORS[cluster], edgecolor=COLORS[cluster]))
        ax.text(0.5, 0.85, SHORT[cluster], ha="center", va="center", fontsize=12, color="white", weight="bold")
        for i, trait in enumerate(top["trait"].str.replace("_", " ")):
            ax.text(0.12, 0.68 - i * 0.115, f"{i + 1}. {trait}", ha="left", va="center", fontsize=10.5, color=INK)

    axes[-1].text(0.04, 0.72, "How to read this", fontsize=13, weight="bold", color=INK, ha="left")
    axes[-1].text(
        0.04,
        0.58,
        "Each card shows the traits\nmost unusually associated\nwith that persona cluster.",
        fontsize=11,
        color=MUTED,
        ha="left",
        va="top",
        linespacing=1.35,
    )
    add_subtitle(
        fig,
        "The clusters have distinct personalities",
        "This validates that the neighborhoods are meaningful, not just arbitrary chart colors.",
    )
    fig.subplots_adjust(top=0.83, left=0.04, right=0.98, bottom=0.04, hspace=0.22, wspace=0.1)
    finish(fig, "05_cluster_trait_cards")


def plot_distance_heatmap(distances: pd.DataFrame) -> None:
    labels = [SHORT[c] for c in CLUSTER_ORDER]
    data = distances.to_numpy(float)
    fig, ax = plt.subplots(figsize=(8.5, 7.6), facecolor=BG)
    ax.set_facecolor(BG)
    im = ax.imshow(data, cmap="YlGnBu_r", vmin=0, vmax=2.0)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=9, color=INK)
    ax.set_yticklabels(labels, fontsize=9, color=INK)
    ax.spines[:].set_visible(False)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if i == j:
                txt = "-"
            else:
                txt = f"{data[i, j]:.2f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8.5, color=INK)
    cbar = fig.colorbar(im, ax=ax, shrink=0.78, pad=0.025)
    cbar.set_label("distance: close -> far", color=MUTED)
    cbar.outline.set_visible(False)
    add_subtitle(
        fig,
        "Which persona regions are close together?",
        "A general-audience version of the connectome: low numbers mean nearby regions.",
    )
    fig.subplots_adjust(top=0.82, left=0.17, right=0.93, bottom=0.16)
    finish(fig, "06_simplified_distance_heatmap")


def write_index() -> None:
    images = [
        ("01_axis_top_roles.png", "What the assistant axis really selects for"),
        ("02_persona_neighborhood_map.png", "Persona neighborhoods"),
        ("02b_axis_neighbor_family_map.png", "Axis position by nearest-neighbor distance"),
        ("03_distance_from_assistant_zone.png", "Distance from assistant-like zone"),
        ("04_drift_path.png", "Possible drift path"),
        ("05_cluster_trait_cards.png", "Cluster personality cards"),
        ("06_simplified_distance_heatmap.png", "Simplified cluster distance heatmap"),
    ]
    body = "\n".join(
        f'<section><h2>{title}</h2><img src="{img}" alt="{title}"></section>' for img, title in images
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>General Audience Persona Figures</title>
  <style>
    body {{ margin: 0; background: {BG}; color: {INK}; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 32px 20px 64px; }}
    h1 {{ margin: 0 0 8px; font-size: 30px; }}
    p {{ color: {MUTED}; margin: 0 0 28px; }}
    section {{ margin: 34px 0; }}
    h2 {{ font-size: 18px; margin: 0 0 10px; }}
    img {{ width: 100%; height: auto; display: block; border: 1px solid #D8CCB9; background: white; }}
  </style>
</head>
<body>
<main>
  <h1>General Audience Persona Figures</h1>
  <p>Draft alternatives for explaining the same story as the persona connectome.</p>
  {body}
</main>
</body>
</html>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    ranking, distances, traits = load_data()
    plot_ranked_roles(ranking)
    plot_neighborhood_map(distances, ranking)
    plot_axis_neighbor_map(distances, ranking)
    plot_distance_from_assistant(distances)
    plot_drift_path(distances)
    plot_trait_cards(traits)
    plot_distance_heatmap(distances)
    write_index()
    print(f"Wrote general-audience figures to {OUT}")


if __name__ == "__main__":
    main()
