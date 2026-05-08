from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

from research_common import OUT_DIR, load_roles, normalize_name


ROLE_TRAIT_Z_PATH = OUT_DIR / "role_trait_similarity_zscored.csv"
FULL_RANKING_PATH = OUT_DIR / "full_ranking.csv"
CLUSTER_PROFILE_PATH = OUT_DIR / "cluster_trait_profiles.csv"

ANOMALIES = ["robot", "assistant", "poet", "angel", "saboteur"]


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, str]]:
    role_trait_z = pd.read_csv(ROLE_TRAIT_Z_PATH, index_col=0)
    ranking = pd.read_csv(FULL_RANKING_PATH)
    cluster_profiles = pd.read_csv(CLUSTER_PROFILE_PATH)

    roles = load_roles()
    role_mapping = {normalize_name(role): role for role in roles}

    required_ranking_cols = {"character", "cluster_label"}
    if not required_ranking_cols.issubset(ranking.columns):
        raise RuntimeError(f"{FULL_RANKING_PATH} is missing required columns: {required_ranking_cols - set(ranking.columns)}")

    ranking["role"] = ranking["character"].map(role_mapping)
    if ranking["role"].isna().any():
        missing = ranking.loc[ranking["role"].isna(), "character"].tolist()
        raise RuntimeError(f"Could not map these ranking rows back to raw role ids: {missing[:10]}")

    if role_trait_z.shape != (275, 240):
        raise RuntimeError(f"Expected role_trait_similarity_zscored.csv shape (275, 240), got {role_trait_z.shape}")

    return role_trait_z, ranking, cluster_profiles, role_mapping


def cosine_distance_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return cdist(np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64), metric="cosine")


def compute_centroids(role_trait_z: pd.DataFrame, ranking: pd.DataFrame) -> pd.DataFrame:
    cluster_by_role = ranking.set_index("role")["cluster_label"]
    ordered_roles = cluster_by_role.index.tolist()
    aligned = role_trait_z.loc[ordered_roles]
    centroids = aligned.groupby(cluster_by_role).mean()
    return centroids.sort_index()


def compute_cluster_distance_matrix(centroids: pd.DataFrame) -> pd.DataFrame:
    distances = cosine_distance_matrix(centroids.to_numpy(), centroids.to_numpy())
    return pd.DataFrame(distances, index=centroids.index, columns=centroids.index)


def summarize_cluster_pairs(distance_df: pd.DataFrame) -> tuple[list[tuple[str, str, float]], list[tuple[str, str, float]]]:
    rows = []
    labels = distance_df.index.tolist()
    for i, a in enumerate(labels):
        for j in range(i + 1, len(labels)):
            b = labels[j]
            rows.append((a, b, float(distance_df.loc[a, b])))
    rows.sort(key=lambda x: x[2])
    closest = rows[:3]
    most_distant = rows[-3:][::-1]
    return closest, most_distant


def compute_role_to_cluster_distances(role_trait_z: pd.DataFrame, centroids: pd.DataFrame) -> pd.DataFrame:
    distances = cosine_distance_matrix(role_trait_z.to_numpy(), centroids.to_numpy())
    return pd.DataFrame(distances, index=role_trait_z.index, columns=centroids.index)


def compute_boundary_roles(role_to_cluster_dist: pd.DataFrame, ranking: pd.DataFrame) -> pd.DataFrame:
    home_cluster = ranking.set_index("role")["cluster_label"]
    rows = []
    for role, home in home_cluster.items():
        foreign = role_to_cluster_dist.loc[role].drop(labels=[home]).sort_values()
        nearest_other_cluster = foreign.index[0]
        distance = float(foreign.iloc[0])
        rows.append(
            {
                "role": role,
                "home_cluster": home,
                "nearest_other_cluster": nearest_other_cluster,
                "distance_to_nearest_other_cluster": distance,
            }
        )
    boundary = pd.DataFrame(rows)
    boundary = boundary.sort_values(["home_cluster", "distance_to_nearest_other_cluster", "role"]).reset_index(drop=True)
    top_per_cluster = boundary.groupby("home_cluster", group_keys=False).head(10).reset_index(drop=True)
    return top_per_cluster


def build_anomaly_report(
    anomalies: list[str],
    role_to_cluster_dist: pd.DataFrame,
    ranking: pd.DataFrame,
    boundary_roles: pd.DataFrame,
    centroids: pd.DataFrame,
    cluster_sizes: pd.Series,
) -> tuple[dict[str, dict[str, object]], bool]:
    home_cluster = ranking.set_index("role")["cluster_label"].to_dict()
    boundary_lookup = set(boundary_roles["role"].tolist())
    reports: dict[str, dict[str, object]] = {}
    bad_assignment = False

    for role in anomalies:
        home = home_cluster[role]
        ranked = role_to_cluster_dist.loc[role].sort_values()
        foreign_ranked = ranked.drop(labels=[home])
        nearest_foreign = foreign_ranked.index[0]
        if nearest_foreign == home:
            bad_assignment = True
        reports[role] = {
            "home_cluster": home,
            "ranked_distances": [(cluster, float(val)) for cluster, val in foreign_ranked.items()],
            "nearest_foreign_cluster": nearest_foreign,
            "is_boundary_role": role in boundary_lookup,
            "nearest_foreign_distance": float(foreign_ranked.iloc[0]),
            "home_cluster_size": int(cluster_sizes[home]),
            "nearest_cluster_profile": centroids.loc[nearest_foreign].sort_values(ascending=False).head(5).index.tolist(),
        }
    return reports, bad_assignment


def save_topology_plot(
    distance_df: pd.DataFrame,
    cluster_sizes: pd.Series,
    boundary_roles: pd.DataFrame,
    anomaly_reports: dict[str, dict[str, object]],
) -> None:
    labels = distance_df.index.tolist()
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    radii = np.array([1.0, 1.02, 0.98, 1.04, 0.96, 1.01, 0.99])
    pos = {
        label: np.array([np.cos(theta) * r, np.sin(theta) * r])
        for label, theta, r in zip(labels, angles, radii)
    }

    pair_rows = []
    for i, a in enumerate(labels):
        for j in range(i + 1, n):
            b = labels[j]
            dist = float(distance_df.loc[a, b])
            pair_rows.append((a, b, dist))
    dists = np.array([row[2] for row in pair_rows])
    dmin, dmax = float(dists.min()), float(dists.max())

    def edge_width(dist: float) -> float:
        if dmax - dmin < 1e-9:
            return 2.0
        closeness = 1 - ((dist - dmin) / (dmax - dmin))
        return 0.8 + 4.2 * closeness

    def edge_alpha(dist: float) -> float:
        if dmax - dmin < 1e-9:
            return 0.45
        closeness = 1 - ((dist - dmin) / (dmax - dmin))
        return 0.18 + 0.45 * closeness

    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_aspect("equal")
    ax.axis("off")

    for a, b, dist in pair_rows:
        xy1 = pos[a]
        xy2 = pos[b]
        ax.plot(
            [xy1[0], xy2[0]],
            [xy1[1], xy2[1]],
            color="#8FA6BF",
            linewidth=edge_width(dist),
            alpha=edge_alpha(dist),
            zorder=1,
        )

    size_scale = 28
    cluster_colors = {
        "editorial": "#375E97",
        "procedural_professional": "#4A7C59",
        "grounded_social": "#8B6F47",
        "mythic_spiritual": "#9A4D7A",
        "trickster_chaos": "#C06C2B",
        "combative_iconoclast": "#B13E3E",
        "other": "#6B7280",
    }

    for label in labels:
        xy = pos[label]
        size = cluster_sizes[label] * size_scale
        ax.scatter([xy[0]], [xy[1]], s=size, color=cluster_colors.get(label, "#4B5563"), zorder=3, edgecolors="white", linewidths=1.5)
        ax.text(xy[0], xy[1], label, ha="center", va="center", fontsize=10, color="white", zorder=4, fontweight="bold")

    grouped = boundary_roles.groupby(["home_cluster", "nearest_other_cluster"])
    for (home, other), sub in grouped:
        xy1 = pos[home]
        xy2 = pos[other]
        midpoint = (xy1 + xy2) / 2
        direction = xy2 - xy1
        length = np.linalg.norm(direction)
        perp = np.array([-(direction[1]), direction[0]]) / (length if length else 1.0)
        count = len(sub)
        offsets = np.linspace(-0.14, 0.14, count)
        for offset, row in zip(offsets, sub.itertuples(index=False)):
            point = midpoint + perp * offset
            is_anomaly = row.role in anomaly_reports
            ax.scatter(
                [point[0]],
                [point[1]],
                s=80 if is_anomaly else 28,
                color=cluster_colors.get(home, "#4B5563"),
                alpha=0.9 if is_anomaly else 0.55,
                edgecolors="black" if is_anomaly else "white",
                linewidths=1.0 if is_anomaly else 0.4,
                zorder=5 if is_anomaly else 2,
            )
            if is_anomaly:
                ax.text(point[0], point[1] + 0.04, row.role, fontsize=9, ha="center", va="bottom", zorder=6)

    ax.set_title("Cluster Boundary Topology in Trait Space", fontsize=15, pad=18)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "cluster_topology.png", dpi=220, bbox_inches="tight")
    plt.close()


def main() -> None:
    role_trait_z, ranking, cluster_profiles, _ = load_inputs()
    centroids = compute_centroids(role_trait_z, ranking)
    cluster_sizes = ranking["cluster_label"].value_counts().sort_index()

    distance_df = compute_cluster_distance_matrix(centroids)
    off_diag = distance_df.to_numpy()[~np.eye(len(distance_df), dtype=bool)]
    if float(off_diag.max() - off_diag.min()) < 1e-4:
        raise RuntimeError("Inter-cluster distances are nearly identical; trait space appears too compressed for meaningful boundary analysis.")

    closest, most_distant = summarize_cluster_pairs(distance_df)
    distance_df.to_csv(OUT_DIR / "cluster_distance_matrix.csv")

    role_to_cluster_dist = compute_role_to_cluster_distances(role_trait_z, centroids)
    role_to_cluster_dist.to_csv(OUT_DIR / "role_to_cluster_distances.csv")

    boundary_roles = compute_boundary_roles(role_to_cluster_dist, ranking)
    boundary_roles.to_csv(OUT_DIR / "boundary_roles.csv", index=False)

    anomaly_reports, bad_assignment = build_anomaly_report(
        ANOMALIES,
        role_to_cluster_dist,
        ranking,
        boundary_roles,
        centroids,
        cluster_sizes,
    )
    if bad_assignment:
        raise RuntimeError("At least one anomaly role mapped to its own home cluster as nearest foreign cluster; cluster assignment error suspected.")

    overall_top5 = boundary_roles.sort_values("distance_to_nearest_other_cluster").head(5).reset_index(drop=True)

    top_clusters = overall_top5["home_cluster"].value_counts()
    dominated = bool((top_clusters / len(overall_top5) > 0.6).any())

    save_topology_plot(distance_df, cluster_sizes, boundary_roles, anomaly_reports)

    print("Closest cluster pairs:")
    for a, b, dist in closest:
        print(f"  {a} <-> {b}: {dist:.6f}")
    print("Most distant cluster pairs:")
    for a, b, dist in most_distant:
        print(f"  {a} <-> {b}: {dist:.6f}")
    print("Top 5 boundary roles overall:")
    for row in overall_top5.itertuples(index=False):
        print(
            f"  {row.role} | home={row.home_cluster} | nearest_other={row.nearest_other_cluster} "
            f"| distance={row.distance_to_nearest_other_cluster:.6f}"
        )
    print("Anomaly boundary summary:")
    for role, report in anomaly_reports.items():
        nearest_cluster, nearest_dist = report["ranked_distances"][0]
        print(
            f"  {role}: home={report['home_cluster']} | nearest_foreign={nearest_cluster} "
            f"| distance={nearest_dist:.6f} | boundary_role={report['is_boundary_role']}"
        )

    if dominated:
        print("FLAG: The top-five boundary roles are dominated by a single cluster, suggesting uneven cluster geometry.")


if __name__ == "__main__":
    main()
