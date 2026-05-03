from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import torch
import torch.nn.functional as F
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler


MODEL_NAME = "gemma-2-27b"
TARGET_LAYER = 22
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOWNLOAD_DIR = ROOT / "downloads" / "hf_vectors" / MODEL_NAME
ROLE_DIR = DOWNLOAD_DIR / "role_vectors"
OUT_DIR = ROOT / "visualizations"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_roles() -> list[str]:
    roles = json.loads((DATA_DIR / "roles" / "role_list.json").read_text())
    return sorted(roles.keys())


def load_role_matrix(roles: list[str]) -> torch.Tensor:
    tensors = []
    for role in roles:
        tensor = torch.load(ROLE_DIR / f"{role}.pt", map_location="cpu")
        if not torch.is_tensor(tensor):
            raise TypeError(f"Expected tensor for role {role}, got {type(tensor)}")
        tensors.append(tensor[TARGET_LAYER].float())
    return torch.stack(tensors)


def normalize_name(name: str) -> str:
    return name.replace("_", " ")


def build_dataframe(
    roles: list[str],
    role_matrix: torch.Tensor,
    axis_layer: torch.Tensor,
) -> pd.DataFrame:
    axis_unit = F.normalize(axis_layer.float(), dim=0)
    projections = torch.matmul(role_matrix, axis_unit).numpy()
    norms = torch.linalg.norm(role_matrix, dim=1).numpy()
    return pd.DataFrame(
        {
            "role": roles,
            "label": [normalize_name(r) for r in roles],
            "assistant_projection": projections,
            "norm": norms,
        }
    )


def save_pca_plot(df: pd.DataFrame, analysis_matrix: np.ndarray) -> None:
    pca = PCA(n_components=3, svd_solver="full")
    pcs = pca.fit_transform(analysis_matrix)
    pca_df = df.copy()
    pca_df["PC1"] = pcs[:, 0]
    pca_df["PC2"] = pcs[:, 1]
    pca_df["PC3"] = pcs[:, 2]

    fig = px.scatter_3d(
        pca_df,
        x="PC1",
        y="PC2",
        z="PC3",
        color="assistant_projection",
        hover_name="label",
        hover_data={
            "assistant_projection": ":.4f",
            "norm": ":.2f",
            "PC1": ":.3f",
            "PC2": ":.3f",
            "PC3": ":.3f",
        },
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0.0,
        title=f"Persona Space PCA (Layer {TARGET_LAYER}, {MODEL_NAME})",
    )
    fig.update_traces(marker={"size": 5, "opacity": 0.85})
    fig.write_html(OUT_DIR / "pca_3d.html")


def save_axis_ranking(df: pd.DataFrame) -> pd.DataFrame:
    ranked = df.sort_values("assistant_projection", ascending=False).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)

    plot_df = ranked.iloc[::-1].copy()
    fig = px.bar(
        plot_df,
        x="assistant_projection",
        y="label",
        orientation="h",
        color="assistant_projection",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0.0,
        hover_data={"rank": True, "assistant_projection": ":.4f", "label": False},
        title=f"Assistant Axis Ranking (Layer {TARGET_LAYER}, {MODEL_NAME})",
        height=6000,
        width=1400,
    )
    fig.update_layout(yaxis={"categoryorder": "array", "categoryarray": plot_df["label"].tolist()})
    fig.write_html(OUT_DIR / "axis_ranking.html")

    plt.figure(figsize=(14, 60))
    colors = plt.cm.RdBu_r(
        (plot_df["assistant_projection"] - plot_df["assistant_projection"].min())
        / (plot_df["assistant_projection"].max() - plot_df["assistant_projection"].min())
    )
    plt.barh(plot_df["label"], plot_df["assistant_projection"], color=colors)
    plt.xlabel("Projection onto Assistant Axis")
    plt.ylabel("Role")
    plt.title(f"Assistant Axis Ranking (Layer {TARGET_LAYER}, {MODEL_NAME})")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "axis_ranking.png", dpi=200)
    plt.close()

    return ranked


def save_cosine_heatmap(roles: list[str], role_matrix: torch.Tensor) -> tuple[np.ndarray, np.ndarray]:
    normalized = F.normalize(role_matrix, dim=1)
    cosine = torch.matmul(normalized, normalized.T).clamp(-1.0, 1.0).cpu().numpy()

    distance = 1.0 - cosine
    np.fill_diagonal(distance, 0.0)
    condensed = squareform(distance, checks=False)
    linkage_matrix = linkage(condensed, method="average")

    labels = [normalize_name(r) for r in roles]
    cluster = sns.clustermap(
        pd.DataFrame(cosine, index=labels, columns=labels),
        row_linkage=linkage_matrix,
        col_linkage=linkage_matrix,
        cmap="vlag",
        center=0.0,
        figsize=(40, 40),
        xticklabels=True,
        yticklabels=True,
    )
    cluster.fig.suptitle(f"Clustered Cosine Similarity Heatmap (Layer {TARGET_LAYER}, {MODEL_NAME})", y=1.02)
    cluster.savefig(OUT_DIR / "cosine_heatmap.png", dpi=200)
    plt.close(cluster.fig)
    return cosine, linkage_matrix


def save_tsne_plot(df: pd.DataFrame, analysis_matrix: np.ndarray) -> None:
    tsne = TSNE(n_components=2, perplexity=30, random_state=42, init="random")
    embedding = tsne.fit_transform(analysis_matrix)
    tsne_df = df.copy()
    tsne_df["TSNE1"] = embedding[:, 0]
    tsne_df["TSNE2"] = embedding[:, 1]

    fig = px.scatter(
        tsne_df,
        x="TSNE1",
        y="TSNE2",
        color="assistant_projection",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0.0,
        hover_name="label",
        hover_data={"assistant_projection": ":.4f", "norm": ":.2f"},
        title=f"Persona Space t-SNE (Layer {TARGET_LAYER}, {MODEL_NAME})",
        width=1300,
        height=900,
    )
    fig.update_traces(marker={"size": 9, "opacity": 0.9})
    fig.write_html(OUT_DIR / "tsne_2d.html")


def summarize_clusters(roles: list[str], linkage_matrix: np.ndarray) -> list[tuple[str, list[str]]]:
    cluster_ids = fcluster(linkage_matrix, t=24, criterion="maxclust")
    groups: dict[int, list[str]] = {}
    for role, cluster_id in zip(roles, cluster_ids):
        groups.setdefault(cluster_id, []).append(role)

    sorted_groups = [members for members in groups.values() if len(members) >= 2]
    sorted_groups.sort(key=lambda members: (-len(members), members[0]))
    summaries = []
    for members in sorted_groups[:10]:
        label = ", ".join(normalize_name(m) for m in members[:3])
        if len(members) > 3:
            label += ", ..."
        summaries.append((label, members))
    return summaries


def summarize_surprises(ranked: pd.DataFrame) -> list[str]:
    top15 = set(ranked.head(15)["role"])
    bottom15 = set(ranked.tail(15)["role"])
    notes = []

    high_candidates = ["angel", "therapist", "teacher", "lawyer", "judge", "archivist", "secretary", "ghost", "robot", "oracle"]
    low_candidates = ["assistant", "demon", "criminal", "pirate", "saboteur", "vampire", "trickster", "zealot", "fool", "addict"]

    for role in high_candidates:
        if role in top15:
            notes.append(f"{normalize_name(role)} ranks unusually high on the Assistant Axis.")
    for role in low_candidates:
        if role in bottom15:
            notes.append(f"{normalize_name(role)} ranks unusually low on the Assistant Axis.")

    if "assistant" not in top15:
        rank = int(ranked.index[ranked["role"] == "assistant"][0]) + 1
        notes.append(f"Assistant itself is not top-15; it lands at rank {rank}.")

    return notes[:8]


def print_summary(ranked: pd.DataFrame, cluster_summaries: list[tuple[str, list[str]]]) -> None:
    print("\nSUMMARY REPORT")
    print(f"Model: {MODEL_NAME}")
    print(f"Target layer: {TARGET_LAYER}")

    print("\n1. FULL RANKED LIST BY ASSISTANT AXIS PROJECTION")
    for row in ranked.itertuples(index=False):
        print(f"{row.rank:03d}. {row.label}\t{row.assistant_projection:.6f}")

    print("\nTop 20 most assistant-like")
    for row in ranked.head(20).itertuples(index=False):
        print(f"{row.rank:03d}. {row.label}\t{row.assistant_projection:.6f}")

    print("\nBottom 20 least assistant-like")
    for row in ranked.tail(20).itertuples(index=False):
        print(f"{row.rank:03d}. {row.label}\t{row.assistant_projection:.6f}")

    print("\n2. TOP CLUSTERS FROM THE COSINE HEATMAP")
    for i, (label, members) in enumerate(cluster_summaries, 1):
        member_labels = ", ".join(normalize_name(m) for m in members)
        print(f"Cluster {i}: {label}")
        print(f"Members: {member_labels}")

    print("\n3. SURPRISING POSITIONS")
    surprise_notes = summarize_surprises(ranked)
    if surprise_notes:
        for note in surprise_notes:
            print(f"- {note}")
    else:
        print("- No obvious surprises detected from simple rank heuristics.")


def main() -> None:
    roles = load_roles()
    role_matrix = load_role_matrix(roles)
    axis = torch.load(DOWNLOAD_DIR / "assistant_axis.pt", map_location="cpu")
    if not torch.is_tensor(axis):
        raise TypeError(f"Expected tensor for assistant axis, got {type(axis)}")
    axis_layer = axis[TARGET_LAYER].float()

    df = build_dataframe(roles, role_matrix, axis_layer)
    role_array = role_matrix.numpy().astype(np.float64)
    analysis_matrix = StandardScaler().fit_transform(role_array)

    save_pca_plot(df, analysis_matrix)
    ranked = save_axis_ranking(df)
    _, linkage_matrix = save_cosine_heatmap(roles, role_matrix)
    save_tsne_plot(df, analysis_matrix)

    cluster_summaries = summarize_clusters(roles, linkage_matrix)
    print_summary(ranked, cluster_summaries)

    print("\nSaved files:")
    for path in sorted(OUT_DIR.glob("*")):
        if path.is_file():
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
