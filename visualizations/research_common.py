from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import torch
import torch.nn.functional as F
from plotly.subplots import make_subplots
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler


MODEL_NAME = "gemma-2-27b"
DEFAULT_LAYER = 22
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DOWNLOAD_DIR = ROOT / "downloads" / "hf_vectors" / MODEL_NAME
ROLE_DIR = DOWNLOAD_DIR / "role_vectors"
OUT_DIR = ROOT / "visualizations"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLUSTER_SEEDS = {
    "procedural_professional": {
        "accountant", "activist", "advocate", "altruist", "ambassador", "analyst", "anarchist",
        "anthropologist", "archaeologist", "architect", "archivist", "assistant", "auditor",
        "biologist", "builder", "caregiver", "cartographer", "chemist", "coach", "collaborator",
        "collector", "conservator", "consultant", "coordinator", "cosmopolitan", "counselor",
        "critic", "curator", "cyborg", "debugger", "designer", "destroyer", "detective",
        "dispatcher", "doctor", "economist", "ecosystem", "egregore", "emissary", "empath",
        "engineer", "entrepreneur", "evaluator", "evangelist", "facilitator", "forecaster",
        "futurist", "generalist", "geographer", "guardian", "guide", "healer", "historian",
        "hive", "hybrid", "idealist", "instructor", "interpreter", "journalist", "judge",
        "lawyer", "librarian", "linguist", "marketer", "mathematician", "mediator", "mentor",
        "merchant", "minimalist", "naturalist", "navigator", "negotiator", "networker",
        "nutritionist", "observer", "optimist", "organizer", "pacifist", "paramedic",
        "peacekeeper", "perfectionist", "pharmacist", "physicist", "pilot", "planner",
        "polymath", "pragmatist", "prodigy", "producer", "programmer", "psychologist",
        "publisher", "realist", "recruiter", "reporter", "researcher", "reviewer",
        "revolutionary", "scheduler", "scholar", "scientist", "scout", "secretary", "skeptic",
        "sociologist", "specialist", "statistician", "strategist", "summarizer", "supervisor",
        "swarm", "symbiont", "synthesizer", "teacher", "technologist", "theorist", "therapist",
        "trainer", "translator", "tulpa", "tutor", "validator", "vegan", "veterinarian",
        "visionary", "witness", "writer",
    },
    "mythic_spiritual": {
        "aberration", "alien", "ancient", "angel", "artisan", "ascetic", "avatar", "bard",
        "bohemian", "chimera", "composer", "coral_reef", "demon", "dreamer", "echo", "elder",
        "eldritch", "familiar", "flaneur", "ghost", "golem", "guru", "hermit", "homunculus",
        "leviathan", "loner", "martyr", "musician", "mycorrhizal", "mystic", "narrator", "nomad",
        "novelist", "oracle", "parasite", "philosopher", "photographer", "pilgrim", "predator",
        "prophet", "purist", "revenant", "romantic", "sage", "shaman", "simulacrum", "spirit",
        "stoic", "traditionalist", "tree", "vampire", "virtuoso", "virus", "void", "wanderer",
        "warrior", "whale", "wind", "witch", "wraith", "zeitgeist",
    },
    "grounded_social": {
        "actor", "addict", "amateur", "auctioneer", "bartender", "blogger", "celebrity",
        "chameleon", "chef", "criminal", "daredevil", "divorcee", "exile", "expatriate", "fixer",
        "graduate", "grandparent", "hacker", "immigrant", "influencer", "mechanic", "newlywed",
        "orphan", "parent", "patient", "pirate", "playwright", "presenter", "prisoner",
        "provincial", "refugee", "retiree", "rogue", "saboteur", "shapeshifter", "smuggler",
        "soldier", "sommelier", "spy", "student", "surfer", "survivor", "veteran", "vigilante",
        "widow",
    },
    "combative_iconoclast": {
        "competitor", "contrarian", "cynic", "devils_advocate", "maverick", "provocateur",
        "rebel", "workaholic",
    },
    "trickster_chaos": {
        "absurdist", "dilettante", "genie", "hedonist", "improviser", "jester", "trickster",
    },
    "editorial": {
        "editor", "examiner", "grader", "proofreader", "screener",
    },
}

JUNG_ARCHETYPES = [
    "Innocent", "Orphan", "Hero", "Caregiver", "Explorer", "Rebel",
    "Lover", "Creator", "Jester", "Sage", "Magician", "Ruler",
]


def progress(message: str) -> None:
    print(message, flush=True)


def normalize_name(name: str) -> str:
    return name.replace("_", " ")


def load_roles() -> list[str]:
    roles = json.loads((DATA_DIR / "roles" / "role_list.json").read_text())
    return sorted(roles.keys())


def load_role_tensor(roles: list[str] | None = None) -> torch.Tensor:
    roles = roles or load_roles()
    progress(f"Loading {len(roles)} role tensors from {ROLE_DIR} ...")
    tensors = []
    for idx, role in enumerate(roles, 1):
        tensor = torch.load(ROLE_DIR / f"{role}.pt", map_location="cpu")
        if not torch.is_tensor(tensor):
            raise TypeError(f"Expected tensor for role {role}, got {type(tensor)}")
        tensors.append(tensor.float())
        if idx % 50 == 0 or idx == len(roles):
            progress(f"  loaded {idx}/{len(roles)} roles")
    return torch.stack(tensors)


def load_axis_tensor() -> torch.Tensor:
    axis = torch.load(DOWNLOAD_DIR / "assistant_axis.pt", map_location="cpu")
    if not torch.is_tensor(axis):
        raise TypeError(f"Expected tensor for assistant axis, got {type(axis)}")
    return axis.float()


def compute_projection_matrix(role_tensor: torch.Tensor, axis_tensor: torch.Tensor) -> torch.Tensor:
    axis_unit = F.normalize(axis_tensor, dim=1)
    return torch.einsum("rld,ld->rl", role_tensor, axis_unit)


def build_layer_dataframe(
    roles: list[str],
    role_tensor: torch.Tensor,
    axis_tensor: torch.Tensor,
    layer: int = DEFAULT_LAYER,
) -> pd.DataFrame:
    projections = compute_projection_matrix(role_tensor, axis_tensor)[:, layer].cpu().numpy()
    norms = torch.linalg.norm(role_tensor[:, layer, :], dim=1).cpu().numpy()
    df = pd.DataFrame(
        {
            "role": roles,
            "character": [normalize_name(r) for r in roles],
            f"axis_projection_layer{layer}": projections,
            "norm": norms,
        }
    )
    df = df.sort_values(f"axis_projection_layer{layer}", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", np.arange(1, len(df) + 1))
    return df


def cosine_matrix(vectors: torch.Tensor) -> np.ndarray:
    progress(f"Computing cosine similarity for matrix with shape {tuple(vectors.shape)} ...")
    normalized = F.normalize(vectors, dim=1)
    cosine = torch.matmul(normalized, normalized.T).clamp(-1.0, 1.0)
    return cosine.cpu().numpy()


def assign_cluster_labels(
    roles: list[str],
    layer_vectors: torch.Tensor,
) -> tuple[dict[str, str], dict[str, float], pd.DataFrame]:
    role_to_idx = {role: i for i, role in enumerate(roles)}
    named_clusters = {k: set(v) for k, v in CLUSTER_SEEDS.items()}

    centroids = {}
    seed_scores = []
    for cluster_name, members in named_clusters.items():
        member_indices = [role_to_idx[m] for m in members if m in role_to_idx]
        cluster_vecs = layer_vectors[member_indices]
        centroid = F.normalize(cluster_vecs.mean(dim=0), dim=0)
        centroids[cluster_name] = centroid
        sims = F.cosine_similarity(cluster_vecs, centroid.unsqueeze(0), dim=1).cpu().numpy()
        seed_scores.extend(sims.tolist())

    threshold = float(np.percentile(seed_scores, 10))
    assignments: dict[str, str] = {}
    nearest_scores: dict[str, float] = {}
    rows = []

    for role in roles:
        if any(role in members for members in named_clusters.values()):
            cluster_name = next(name for name, members in named_clusters.items() if role in members)
            score = float(
                F.cosine_similarity(
                    layer_vectors[role_to_idx[role]].unsqueeze(0),
                    centroids[cluster_name].unsqueeze(0),
                    dim=1,
                ).item()
            )
        else:
            sims = {
                name: float(
                    F.cosine_similarity(
                        layer_vectors[role_to_idx[role]].unsqueeze(0),
                        centroid.unsqueeze(0),
                        dim=1,
                    ).item()
                )
                for name, centroid in centroids.items()
            }
            cluster_name, score = max(sims.items(), key=lambda item: item[1])
            if score < threshold:
                cluster_name = "other"
        assignments[role] = cluster_name
        nearest_scores[role] = score
        rows.append(
            {
                "role": role,
                "character": normalize_name(role),
                "cluster_label": cluster_name,
                "nearest_seed_similarity": score,
            }
        )

    debug_df = pd.DataFrame(rows).sort_values(["cluster_label", "nearest_seed_similarity"], ascending=[True, False])
    return assignments, nearest_scores, debug_df


def cluster_count_table(assignments: dict[str, str]) -> pd.DataFrame:
    counts = pd.Series(assignments).value_counts().rename_axis("cluster_label").reset_index(name="count")
    return counts.sort_values(["count", "cluster_label"], ascending=[False, True]).reset_index(drop=True)


def standardize(vectors: np.ndarray) -> np.ndarray:
    return StandardScaler().fit_transform(vectors.astype(np.float64))


def save_pca_plot(
    df: pd.DataFrame,
    analysis_matrix: np.ndarray,
    color_column: str,
    output_path: Path,
    title: str,
) -> None:
    pca = PCA(n_components=3, svd_solver="full")
    pcs = pca.fit_transform(analysis_matrix)
    plot_df = df.copy()
    plot_df["PC1"] = pcs[:, 0]
    plot_df["PC2"] = pcs[:, 1]
    plot_df["PC3"] = pcs[:, 2]
    fig = px.scatter_3d(
        plot_df,
        x="PC1",
        y="PC2",
        z="PC3",
        color=color_column,
        hover_name="character",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0.0 if pd.api.types.is_numeric_dtype(plot_df[color_column]) else None,
        title=title,
    )
    fig.update_traces(marker={"size": 5, "opacity": 0.85})
    fig.write_html(output_path)


def save_ranking_plot(
    df: pd.DataFrame,
    projection_column: str,
    output_html: Path,
    title: str,
    output_png: Path | None = None,
) -> None:
    plot_df = df.sort_values("rank", ascending=False).copy()
    fig = px.bar(
        plot_df,
        x=projection_column,
        y="character",
        orientation="h",
        color=projection_column,
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0.0,
        hover_data={"rank": True, projection_column: ":.4f", "character": False},
        title=title,
        height=6000,
        width=1400,
    )
    fig.update_layout(yaxis={"categoryorder": "array", "categoryarray": plot_df["character"].tolist()})
    fig.write_html(output_html)

    if output_png is not None:
        plt.figure(figsize=(14, 60))
        values = plot_df[projection_column]
        colors = plt.cm.RdBu_r((values - values.min()) / (values.max() - values.min() + 1e-12))
        plt.barh(plot_df["character"], values, color=colors)
        plt.xlabel("Projection onto Assistant Axis")
        plt.ylabel("Character")
        plt.title(title)
        plt.tight_layout()
        plt.savefig(output_png, dpi=200)
        plt.close()


def save_tsne_plot(
    df: pd.DataFrame,
    analysis_matrix: np.ndarray,
    color_column: str,
    output_path: Path,
    title: str,
) -> None:
    progress(f"Running t-SNE for {output_path.name} ...")
    tsne = TSNE(n_components=2, perplexity=30, random_state=42, init="random")
    embedding = tsne.fit_transform(analysis_matrix)
    plot_df = df.copy()
    plot_df["TSNE1"] = embedding[:, 0]
    plot_df["TSNE2"] = embedding[:, 1]
    fig = px.scatter(
        plot_df,
        x="TSNE1",
        y="TSNE2",
        color=color_column,
        hover_name="character",
        title=title,
        width=1300,
        height=900,
    )
    fig.update_traces(marker={"size": 9, "opacity": 0.9})
    fig.write_html(output_path)


def save_clustered_heatmap(
    roles: list[str],
    layer_vectors: torch.Tensor,
    output_path: Path,
    title: str,
) -> np.ndarray:
    cosine = cosine_matrix(layer_vectors)
    distance = 1.0 - cosine
    np.fill_diagonal(distance, 0.0)
    condensed = squareform(distance, checks=False)
    linkage_matrix = linkage(condensed, method="average")
    labels = [normalize_name(r) for r in roles]
    import seaborn as sns

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
    cluster.fig.suptitle(title, y=1.02)
    cluster.savefig(output_path, dpi=200)
    plt.close(cluster.fig)
    return cosine


def add_numeric_scatter_subplots(
    df: pd.DataFrame,
    score_columns: list[str],
    projection_column: str,
    title: str,
    output_path: Path,
) -> dict[str, float]:
    fig = make_subplots(rows=len(score_columns), cols=1, subplot_titles=score_columns, vertical_spacing=0.06)
    correlations = {}
    for idx, column in enumerate(score_columns, 1):
        x = df[column]
        y = df[projection_column]
        correlations[column] = float(np.corrcoef(x, y)[0, 1])
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers+text",
                text=df["character"],
                textposition="top center",
                marker={"size": 8, "opacity": 0.7},
                name=column,
                showlegend=False,
            ),
            row=idx,
            col=1,
        )
        fig.update_xaxes(title_text=column, row=idx, col=1)
        fig.update_yaxes(title_text=projection_column, row=idx, col=1)
    fig.update_layout(title=title, height=350 * len(score_columns), width=1400)
    fig.write_html(output_path)
    return correlations


def nearest_jung_archetype(role: str, cluster_label: str) -> str:
    if role in {"caregiver", "healer", "therapist", "mentor", "teacher", "peacekeeper", "nurse"}:
        return "Caregiver"
    if role in {"orphan", "refugee", "widow", "prisoner", "patient"}:
        return "Orphan"
    if role in {"warrior", "soldier", "guardian", "advocate", "hero", "vigilante"}:
        return "Hero"
    if role in {"wanderer", "nomad", "navigator", "scout", "surfer", "flaneur", "pilgrim"}:
        return "Explorer"
    if role in {"rebel", "anarchist", "contrarian", "provocateur", "saboteur"}:
        return "Rebel"
    if role in {"romantic", "newlywed", "lover", "poet"}:
        return "Lover"
    if role in {"writer", "playwright", "composer", "artist", "designer", "architect", "creator", "bard"}:
        return "Creator"
    if role in {"jester", "comedian", "trickster", "absurdist", "fool"}:
        return "Jester"
    if role in {"sage", "philosopher", "scholar", "oracle", "librarian", "archivist", "researcher"}:
        return "Sage"
    if role in {"witch", "shaman", "prophet", "angel", "demon", "magician", "mystic"}:
        return "Magician"
    if role in {"judge", "ruler", "secretary", "supervisor", "moderator", "director"}:
        return "Ruler"
    if cluster_label == "procedural_professional":
        return "Sage"
    if cluster_label == "mythic_spiritual":
        return "Magician"
    if cluster_label == "grounded_social":
        return "Orphan"
    if cluster_label == "combative_iconoclast":
        return "Rebel"
    if cluster_label == "trickster_chaos":
        return "Jester"
    if cluster_label == "editorial":
        return "Ruler"
    return "Innocent"


def make_index_html(entries: Iterable[tuple[str, str]], output_path: Path) -> None:
    lines = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'><title>Assistant Axis Visualizations</title></head><body>",
        "<h1>Assistant Axis Deep Analysis</h1>",
        "<ul>",
    ]
    for filename, description in entries:
        lines.append(f"<li><a href='{filename}'>{filename}</a> - {description}</li>")
    lines.extend(["</ul>", "</body></html>"])
    output_path.write_text("\n".join(lines))
