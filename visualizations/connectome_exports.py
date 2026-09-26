from __future__ import annotations

from pathlib import Path as FilePath
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgba
from matplotlib.patches import FancyArrowPatch, PathPatch
from matplotlib.path import Path as MplPath


OUT_DIR = FilePath(__file__).resolve().parent / "connectome-exports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLUSTER_ORDER = [
    "editorial",
    "procedural_professional",
    "grounded_social",
    "other",
    "combative_iconoclast",
    "trickster_chaos",
    "mythic_spiritual",
]

COUNTS = {
    "procedural_professional": 127,
    "mythic_spiritual": 61,
    "grounded_social": 45,
    "other": 22,
    "combative_iconoclast": 8,
    "trickster_chaos": 7,
    "editorial": 5,
}

ACADEMIC_COLORS = {
    "editorial": "#2166AC",
    "procedural_professional": "#4393C3",
    "grounded_social": "#92C5DE",
    "mythic_spiritual": "#762A83",
    "combative_iconoclast": "#1B7837",
    "trickster_chaos": "#D6604D",
    "other": "#878787",
    "center": "#E8923A",
    "trait": "#AABBD4",
    "line": "#666666",
}

PARCHMENT_COLORS = {
    "editorial": "#4A6741",
    "procedural_professional": "#6B8F71",
    "grounded_social": "#9BB89E",
    "mythic_spiritual": "#7A5C82",
    "combative_iconoclast": "#4A6741",
    "trickster_chaos": "#A0522D",
    "other": "#A09070",
    "center": "#C87820",
    "trait": "#B4AC98",
    "line": "#5C3317",
    "background": "#F0E8D5",
}


def load_inputs(base: FilePath) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    full_ranking = pd.read_csv(base / "full_ranking.csv")
    role_trait = pd.read_csv(base / "role_trait_similarity_zscored.csv", index_col=0)
    cluster_profiles = pd.read_csv(base / "cluster_trait_profiles.csv")
    cluster_distance = pd.read_csv(base / "cluster_distance_matrix.csv").set_index("cluster_label")
    cluster_distance = cluster_distance.loc[CLUSTER_ORDER, CLUSTER_ORDER]
    return full_ranking, role_trait, cluster_profiles, cluster_distance


def node_sizes() -> dict[str, float]:
    min_count = min(COUNTS.values())
    max_count = max(COUNTS.values())
    min_size = 700.0
    max_size = 3600.0
    out = {}
    for cluster, count in COUNTS.items():
        scale = (count - min_count) / (max_count - min_count)
        out[cluster] = min_size + scale * (max_size - min_size)
    return out


def pretty_label(name: str) -> str:
    return name.replace("_", "\n")


def cluster_positions(radius: float = 0.82) -> dict[str, np.ndarray]:
    positions = {}
    for idx, cluster in enumerate(CLUSTER_ORDER):
        theta = np.pi / 2 - 2 * np.pi * idx / len(CLUSTER_ORDER)
        positions[cluster] = np.array([radius * np.cos(theta), radius * np.sin(theta)])
    return positions


def trait_positions(traits: list[str], radius: float = 0.45) -> dict[str, np.ndarray]:
    positions = {}
    for idx, trait in enumerate(traits):
        theta = np.pi / 2 - 2 * np.pi * idx / len(traits)
        positions[trait] = np.array([radius * np.cos(theta), radius * np.sin(theta)])
    return positions


def text_alignment(pos: np.ndarray) -> tuple[str, str]:
    x, y = pos
    ha = "center" if abs(x) < 0.08 else ("left" if x > 0 else "right")
    va = "bottom" if y > 0.15 else ("top" if y < -0.15 else "center")
    return ha, va


def curved_patch(
    start: np.ndarray,
    end: np.ndarray,
    color: str,
    lw: float,
    alpha: float,
    inward: float = 0.55,
    offset: float = 0.0,
    zorder: int = 1,
) -> PathPatch:
    midpoint = (start + end) / 2
    norm = np.linalg.norm(midpoint)
    perp = np.array([-midpoint[1], midpoint[0]]) / (norm if norm else 1.0)
    ctrl1 = start * inward + perp * offset
    ctrl2 = end * inward + perp * offset
    path = MplPath(
        [tuple(start), tuple(ctrl1), tuple(ctrl2), tuple(end)],
        [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4],
    )
    return PathPatch(
        path,
        facecolor="none",
        edgecolor=to_rgba(color, alpha),
        lw=lw,
        capstyle="round",
        joinstyle="round",
        zorder=zorder,
    )


def scale_thickness(value: float, lo: float, hi: float, out_lo: float, out_hi: float, inverse: bool = False) -> float:
    if abs(hi - lo) < 1e-12:
        return (out_lo + out_hi) / 2
    if inverse:
        value = hi - (value - lo)
    scale = (value - lo) / (hi - lo)
    return out_lo + scale * (out_hi - out_lo)


def top_variance_traits(cluster_profiles: pd.DataFrame, top_n: int = 10) -> list[str]:
    pivot = cluster_profiles.pivot(index="trait", columns="cluster_label", values="mean_zscore")
    variances = pivot.var(axis=1).sort_values(ascending=False)
    return variances.head(top_n).index.tolist()


def cluster_trait_matrix(cluster_profiles: pd.DataFrame, traits: list[str]) -> pd.DataFrame:
    pivot = cluster_profiles.pivot(index="cluster_label", columns="trait", values="mean_zscore")
    return pivot.loc[CLUSTER_ORDER, traits]


def setup_axes(fig_size_inches: float, background: str) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(fig_size_inches, fig_size_inches), dpi=150)
    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.set_aspect("equal")
    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-1.12, 1.12)
    ax.axis("off")
    return fig, ax


def draw_pole_annotations(ax: plt.Axes, line_color: str, text_color: str) -> None:
    top_arc = FancyArrowPatch(
        (-0.18, 0.99), (0.18, 0.99),
        connectionstyle="arc3,rad=0.35",
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=1.0,
        color=to_rgba(line_color, 0.6),
        zorder=6,
    )
    bottom_arc = FancyArrowPatch(
        (0.18, -0.99), (-0.18, -0.99),
        connectionstyle="arc3,rad=0.35",
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=1.0,
        color=to_rgba(line_color, 0.6),
        zorder=6,
    )
    ax.add_patch(top_arc)
    ax.add_patch(bottom_arc)
    ax.text(0, 1.06, "assistant-aligned pole", ha="center", va="bottom", fontsize=9, color=text_color, family="DejaVu Sans")
    ax.text(0, -1.06, "role-play / anti-assistant pole", ha="center", va="top", fontsize=9, color=text_color, family="DejaVu Sans")


def draw_cluster_nodes(
    ax: plt.Axes,
    positions: dict[str, np.ndarray],
    palette: dict[str, str],
    label_color_mode: str = "node",
    highlight: str | None = None,
    highlight_variant: bool = False,
) -> dict[str, float]:
    sizes = node_sizes()
    label_pos_radius = 0.97
    for cluster in CLUSTER_ORDER:
        pos = positions[cluster]
        s = sizes[cluster]
        alpha = 1.0
        edgecolor = "white"
        linewidth = 1.5
        if highlight_variant:
            if cluster == highlight:
                s *= 1.4
                edgecolor = PARCHMENT_COLORS["line"]
                linewidth = 2.0
            else:
                alpha = 0.4
        ax.scatter(
            [pos[0]], [pos[1]],
            s=s,
            color=to_rgba(palette[cluster], alpha),
            edgecolors=edgecolor,
            linewidths=linewidth,
            zorder=8,
        )
        label_pos = pos / np.linalg.norm(pos) * label_pos_radius
        ha, va = text_alignment(label_pos)
        label_color = palette[cluster] if label_color_mode == "node" else palette["line"]
        if highlight_variant and cluster != highlight:
            label_color = to_rgba(label_color, 0.45)
        ax.text(
            label_pos[0], label_pos[1],
            pretty_label(cluster),
            ha=ha, va=va,
            fontsize=11,
            color=label_color,
            family="DejaVu Sans",
            zorder=9,
        )
    return sizes


def draw_center_node(ax: plt.Axes, palette: dict[str, str], median_size: float) -> None:
    ax.scatter([0], [0], s=median_size * 1.15, color=palette["center"], edgecolors="white", linewidths=1.8, zorder=10)


def save_figure(fig: plt.Figure, prefix: str, suffix: str) -> list[Path]:
    created = []
    if suffix == "academic":
        png = OUT_DIR / f"{prefix}-{suffix}.png"
        svg = OUT_DIR / f"{prefix}-{suffix}.svg"
        fig.savefig(png, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        fig.savefig(svg, bbox_inches="tight", facecolor=fig.get_facecolor())
        created.extend([png, svg])
    else:
        png = OUT_DIR / f"{prefix}-{suffix}.png"
        fig.savefig(png, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        created.append(png)
    plt.close(fig)
    return created


def render_persona_connectome(
    cluster_distance: pd.DataFrame,
    parchment: bool = False,
    highlight: str | None = None,
    small: bool = False,
) -> list[Path]:
    palette = PARCHMENT_COLORS if parchment else ACADEMIC_COLORS
    fig, ax = setup_axes(4 if small else 8, palette["background"] if parchment else "white")
    positions = cluster_positions()
    sizes = draw_cluster_nodes(
        ax,
        positions,
        palette,
        label_color_mode="line" if parchment else "node",
        highlight=highlight,
        highlight_variant=highlight is not None,
    )
    draw_center_node(ax, palette, float(np.median(list(sizes.values()))))

    off_diag = cluster_distance.to_numpy()[~np.eye(len(cluster_distance), dtype=bool)]
    dmin, dmax = float(off_diag.min()), float(off_diag.max())

    for i, src in enumerate(CLUSTER_ORDER):
        for j in range(i + 1, len(CLUSTER_ORDER)):
            dst = CLUSTER_ORDER[j]
            dist = float(cluster_distance.loc[src, dst])
            lw = scale_thickness(dist, dmin, dmax, 0.5, 4.0, inverse=True)
            alpha_src = 0.4
            alpha_dst = 0.4
            if highlight is not None:
                if src == highlight or dst == highlight:
                    alpha_src = alpha_dst = 0.8
                else:
                    alpha_src = alpha_dst = 0.2
            patch_a = curved_patch(positions[src], positions[dst], palette[src], lw, alpha_src, inward=0.64, offset=0.03, zorder=2)
            patch_b = curved_patch(positions[dst], positions[src], palette[dst], lw, alpha_dst, inward=0.64, offset=-0.03, zorder=2)
            ax.add_patch(patch_a)
            ax.add_patch(patch_b)

    count_vals = np.array([COUNTS[c] for c in CLUSTER_ORDER], dtype=float)
    cmin, cmax = float(count_vals.min()), float(count_vals.max())
    center_r = 0.17
    for cluster in CLUSTER_ORDER:
        pos = positions[cluster]
        start = pos / np.linalg.norm(pos) * center_r
        end = pos * 0.92
        lw = scale_thickness(COUNTS[cluster], cmin, cmax, 1.0, 4.5, inverse=False)
        alpha = 0.6 if highlight is None else (0.8 if cluster == highlight else 0.25)
        ax.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=to_rgba(palette["center"] if not parchment else palette["line"], alpha),
            linewidth=lw,
            zorder=1,
        )

    if not small:
        draw_pole_annotations(ax, palette["line"], palette["line"] if parchment else "#666666")

    if highlight is None:
        prefix = "persona-connectome"
        suffix = "parchment" if parchment else "academic"
    else:
        prefix = f"persona-connectome-highlight-{highlight.replace('_', '-')}"
        suffix = "parchment"
    return save_figure(fig, prefix, suffix)


def render_trait_connectome(
    cluster_profiles: pd.DataFrame,
    parchment: bool = False,
) -> tuple[list[Path], list[str], int]:
    palette = PARCHMENT_COLORS if parchment else ACADEMIC_COLORS
    fig, ax = setup_axes(8, palette["background"] if parchment else "white")
    positions = cluster_positions()
    sizes = draw_cluster_nodes(ax, positions, palette, label_color_mode="line" if parchment else "node")
    draw_center_node(ax, palette, float(np.median(list(sizes.values()))))

    traits = top_variance_traits(cluster_profiles, top_n=10)
    trait_pos = trait_positions(traits)
    cluster_trait = cluster_trait_matrix(cluster_profiles, traits)
    trait_size = float(np.median(list(sizes.values())) * 0.36)

    center_r = 0.17
    for trait in traits:
        pos = trait_pos[trait]
        start = pos / np.linalg.norm(pos) * center_r
        end = pos * 0.92
        ax.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=to_rgba(palette["center"] if not parchment else palette["line"], 0.4),
            linewidth=1.2,
            zorder=1,
        )
        ax.scatter([pos[0]], [pos[1]], s=trait_size, color=palette["trait"], edgecolors="white", linewidths=1.0, zorder=7)
        label_pos = pos / np.linalg.norm(pos) * 0.57
        ha, va = text_alignment(label_pos)
        ax.text(
            label_pos[0], label_pos[1],
            trait.replace("_", "\n"),
            ha=ha,
            va=va,
            fontsize=9,
            color=palette["line"] if parchment else "#666666",
            family="DejaVu Sans",
            zorder=8,
        )

    zmax = float(cluster_trait.max().max())
    connections = 0
    for cluster in CLUSTER_ORDER:
        for trait in traits:
            z = float(cluster_trait.loc[cluster, trait])
            if z <= 1.5:
                continue
            lw = scale_thickness(z, 1.5, zmax, 0.8, 3.8, inverse=False)
            patch = curved_patch(
                positions[cluster],
                trait_pos[trait],
                palette[cluster],
                lw,
                0.35,
                inward=0.68,
                offset=0.015,
                zorder=2,
            )
            ax.add_patch(patch)
            connections += 1

    prefix = "trait-connectome"
    suffix = "parchment" if parchment else "academic"
    return save_figure(fig, prefix, suffix), traits, connections


def main() -> None:
    base = FilePath(__file__).resolve().parent
    _, _, cluster_profiles, cluster_distance = load_inputs(base)

    created: list[Path] = []
    unexpected: list[str] = []

    created.extend(render_persona_connectome(cluster_distance, parchment=False))
    created.extend(render_persona_connectome(cluster_distance, parchment=True))

    trait_academic, traits, n_conn_academic = render_trait_connectome(cluster_profiles, parchment=False)
    created.extend(trait_academic)
    trait_parchment, _, n_conn_parchment = render_trait_connectome(cluster_profiles, parchment=True)
    created.extend(trait_parchment)

    for cluster in CLUSTER_ORDER:
        created.extend(render_persona_connectome(cluster_distance, parchment=True, highlight=cluster, small=True))

    if n_conn_academic == 0 or n_conn_parchment == 0:
        unexpected.append("Trait connectome threshold z > 1.5 produced no visible connections.")
    if len(set(traits)) != 10:
        unexpected.append("Trait selection returned duplicate or missing traits.")

    print("Connectome export complete.")
    print("Selected top-variance traits:")
    for trait in traits:
        print(f"  - {trait}")
    print("\nFiles created:")
    for path in created:
        print(f"  - {path}")
    if unexpected:
        print("\nUnexpected data notes:")
        for note in unexpected:
            print(f"  - {note}")
    else:
        print("\nUnexpected data notes:\n  - none")
    if n_conn_academic == 0 or n_conn_parchment == 0:
        print("\nChord threshold note: no trait chords drawn at z > 1.5")
    else:
        print(f"\nChord threshold note: trait connectome drew {n_conn_academic} chords at z > 1.5")


if __name__ == "__main__":
    main()
