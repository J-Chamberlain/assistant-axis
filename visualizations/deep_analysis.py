from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import torch
import torch.nn.functional as F

from layer_analysis import run_layer_analysis
from research_common import (
    CLUSTER_SEEDS,
    DEFAULT_LAYER,
    JUNG_ARCHETYPES,
    MODEL_NAME,
    OUT_DIR,
    add_numeric_scatter_subplots,
    assign_cluster_labels,
    build_layer_dataframe,
    cluster_count_table,
    compute_projection_matrix,
    cosine_matrix,
    load_axis_tensor,
    load_role_tensor,
    load_roles,
    make_index_html,
    nearest_jung_archetype,
    normalize_name,
    progress,
    save_clustered_heatmap,
    save_ranking_plot,
    save_tsne_plot,
    standardize,
)


NOTES_PATH = OUT_DIR / "RESEARCH_NOTES.md"


def clamp_score(value: float) -> int:
    return int(max(1, min(5, round(value))))


def write_progress_notes(step_notes: list[tuple[str, str]]) -> None:
    lines = [
        "# Assistant Axis Deep Research Notes",
        "",
        f"Model: `{MODEL_NAME}`",
        f"Working layer reference: `{DEFAULT_LAYER}`",
        "",
        "These notes are updated after each completed analysis step.",
        "",
    ]
    for title, body in step_notes:
        lines.append(f"## {title}")
        lines.append("")
        lines.extend(body.strip().splitlines())
        lines.append("")
    NOTES_PATH.write_text("\n".join(lines))


def seed_cluster_centroids(roles: list[str], layer_vectors: torch.Tensor) -> dict[str, torch.Tensor]:
    role_to_idx = {role: i for i, role in enumerate(roles)}
    centroids = {}
    for cluster_name, members in CLUSTER_SEEDS.items():
        member_indices = [role_to_idx[m] for m in members]
        centroids[cluster_name] = F.normalize(layer_vectors[member_indices].mean(dim=0), dim=0)
    return centroids


def build_bigfive_profile(role: str, cluster_label: str) -> dict[str, int]:
    scores = {
        "Openness": 3.0,
        "Conscientiousness": 3.0,
        "Extraversion": 3.0,
        "Agreeableness": 3.0,
        "Neuroticism": 2.5,
    }
    cluster_bases = {
        "procedural_professional": (2.4, 4.4, 2.4, 3.4, 1.8),
        "mythic_spiritual": (4.7, 2.4, 2.6, 3.0, 2.7),
        "grounded_social": (3.2, 2.8, 3.4, 3.0, 2.9),
        "combative_iconoclast": (4.0, 2.2, 3.1, 1.8, 2.8),
        "trickster_chaos": (4.8, 1.5, 3.8, 1.6, 2.8),
        "editorial": (2.1, 4.9, 1.9, 3.3, 2.2),
        "other": (3.0, 3.0, 3.0, 3.0, 2.5),
    }
    base = cluster_bases.get(cluster_label, cluster_bases["other"])
    for key, value in zip(scores.keys(), base):
        scores[key] = value

    if role in {"proofreader", "grader", "editor", "examiner", "validator", "accountant", "scheduler", "planner", "statistician"}:
        scores["Conscientiousness"] += 0.7
    if role in {"writer", "poet", "artist", "bard", "playwright", "composer", "novelist", "musician", "photographer", "designer"}:
        scores["Openness"] += 0.7
        scores["Conscientiousness"] -= 0.4
    if role in {"therapist", "caregiver", "altruist", "teacher", "mentor", "healer", "guide", "peacekeeper"}:
        scores["Agreeableness"] += 0.9
    if role in {"narcissist", "criminal", "pirate", "saboteur", "demon", "vampire", "trickster", "provocateur", "critic"}:
        scores["Agreeableness"] -= 1.2
    if role in {"comedian", "actor", "blogger", "celebrity", "bartender", "auctioneer", "podcaster", "influencer"}:
        scores["Extraversion"] += 1.0
    if role in {"hermit", "loner", "archivist", "librarian", "proofreader", "judge", "widow"}:
        scores["Extraversion"] -= 1.0
    if role in {"addict", "widow", "orphan", "refugee", "prisoner", "amnesiac", "teenager", "adolescent", "narcissist"}:
        scores["Neuroticism"] += 1.1
    if role in {"stoic", "robot", "assistant", "scheduler", "judge", "statistician", "scientist"}:
        scores["Neuroticism"] -= 0.8
    if role in {"angel", "mystic", "prophet", "oracle", "witch", "shaman", "philosopher", "dreamer"}:
        scores["Openness"] += 0.6
    if role in {"tree", "caveman", "toddler", "infant"}:
        scores["Conscientiousness"] -= 0.8
        scores["Openness"] -= 0.3
    if role in {"robot"}:
        scores["Conscientiousness"] += 0.8
        scores["Agreeableness"] += 0.2
    if role in {"assistant"}:
        scores["Conscientiousness"] += 0.5
        scores["Agreeableness"] += 0.5

    return {k: clamp_score(v) for k, v in scores.items()}


def build_dark_triad_profile(role: str, cluster_label: str) -> dict[str, int]:
    scores = {
        "Narcissism": 2.0,
        "Machiavellianism": 2.0,
        "Psychopathy": 2.0,
    }
    cluster_bases = {
        "procedural_professional": (1.4, 1.8, 1.3),
        "mythic_spiritual": (2.0, 2.0, 2.0),
        "grounded_social": (2.2, 2.1, 2.2),
        "combative_iconoclast": (3.2, 3.4, 3.1),
        "trickster_chaos": (3.0, 3.2, 2.8),
        "editorial": (1.3, 1.9, 1.2),
        "other": (2.0, 2.0, 2.0),
    }
    base = cluster_bases.get(cluster_label, cluster_bases["other"])
    for key, value in zip(scores.keys(), base):
        scores[key] = value

    if role in {"narcissist", "celebrity", "influencer", "guru", "angel", "prophet"}:
        scores["Narcissism"] += 1.5
    if role in {"spy", "smuggler", "fixer", "marketer", "politician", "lawyer", "pirate", "saboteur"}:
        scores["Machiavellianism"] += 1.2
    if role in {"criminal", "demon", "vampire", "predator", "warrior", "pirate", "zealot", "saboteur"}:
        scores["Psychopathy"] += 1.4
    if role in {"caregiver", "altruist", "teacher", "therapist", "peacekeeper", "mentor"}:
        scores["Narcissism"] -= 0.8
        scores["Machiavellianism"] -= 0.8
        scores["Psychopathy"] -= 0.8
    if role in {"robot", "assistant", "proofreader", "statistician"}:
        scores["Psychopathy"] -= 0.5

    return {k: clamp_score(v) for k, v in scores.items()}


def step1_export_ranking(
    roles: list[str],
    role_tensor: torch.Tensor,
    axis_tensor: torch.Tensor,
    step_notes: list[tuple[str, str]],
) -> tuple[pd.DataFrame, dict[str, str], dict[str, float]]:
    progress("STEP 1: exporting full ranking CSV ...")
    ranking_df = build_layer_dataframe(roles, role_tensor, axis_tensor, layer=DEFAULT_LAYER)
    assignments, nearest_scores, debug_df = assign_cluster_labels(roles, role_tensor[:, DEFAULT_LAYER, :])
    ranking_df["cluster_label"] = ranking_df["role"].map(assignments)
    ranking_df["nearest_seed_similarity"] = ranking_df["role"].map(nearest_scores)
    ranking_df[["rank", "character", f"axis_projection_layer{DEFAULT_LAYER}", "cluster_label"]].to_csv(
        OUT_DIR / "full_ranking.csv", index=False
    )
    debug_df.to_csv(OUT_DIR / "cluster_assignment_debug.csv", index=False)

    counts_df = cluster_count_table(assignments)
    counts_lines = [f"- `{row.cluster_label}`: {row.count}" for row in counts_df.itertuples(index=False)]
    step_notes.append(
        (
            "Step 1 - Full Ranked CSV",
            "\n".join(
                [
                    f"Saved `visualizations/full_ranking.csv` with layer-{DEFAULT_LAYER} rankings and cluster labels.",
                    "",
                    "Cluster counts:",
                    *counts_lines,
                    "",
                    f"Low-similarity fallback threshold for `other`: `{np.percentile(list(nearest_scores.values()), 10):.4f}` based on nearest seed similarity distribution.",
                ]
            ),
        )
    )
    write_progress_notes(step_notes)
    progress(counts_df.to_string(index=False))
    return ranking_df, assignments, nearest_scores


def step2_layer_analysis(step_notes: list[tuple[str, str]]) -> dict[str, object]:
    progress("STEP 2: running full layer analysis ...")
    results = run_layer_analysis()
    top_lines = [
        f"- Layer {int(row.layer)} variance={row.variance:.4f}"
        for row in results["top_layers"].itertuples(index=False)
    ]
    max_shift_lines = [
        f"- `{normalize_name(role)}` shift={shift}"
        for role, shift in results["max_shift_roles"][:5]
    ]
    step_notes.append(
        (
            "Step 2 - Layer-by-Layer Analysis",
            "\n".join(
                [
                    "Saved `layer_depth_heatmap.png`, `layer_profiles_extremes.html`, `layer_discrimination.png`, `pca_3d_best_layer.html`, and `axis_ranking_best_layer.html`.",
                    "",
                    "Top discriminative layers:",
                    *top_lines,
                    "",
                    f"Most discriminative layer: `{results['best_layer']}`.",
                    f"Mean absolute rank shift relative to layer 22: `{results['mean_abs_shift']:.2f}`.",
                    f"Spearman rank correlation between layer 22 and best layer rankings: `{results['rank_correlation']:.4f}`.",
                    "",
                    "Largest role ordering changes:",
                    *max_shift_lines,
                ]
            ),
        )
    )
    write_progress_notes(step_notes)
    return results


def step3_psychology_mapping(
    roles: list[str],
    role_tensor: torch.Tensor,
    axis_tensor: torch.Tensor,
    ranking_df: pd.DataFrame,
    cluster_assignments: dict[str, str],
    step_notes: list[tuple[str, str]],
) -> tuple[pd.DataFrame, dict[str, float], dict[str, float], dict[str, str]]:
    progress("STEP 3: building psychology-framework mappings ...")
    layer_vectors = role_tensor[:, DEFAULT_LAYER, :]
    projections = ranking_df.set_index("role")[f"axis_projection_layer{DEFAULT_LAYER}"]

    bigfive = {role: build_bigfive_profile(role, cluster_assignments[role]) for role in roles}
    dark_triad = {role: build_dark_triad_profile(role, cluster_assignments[role]) for role in roles}
    jung = {role: nearest_jung_archetype(role, cluster_assignments[role]) for role in roles}

    (OUT_DIR / "bigfive_profiles.json").write_text(json.dumps(bigfive, indent=2, sort_keys=True))
    (OUT_DIR / "dark_triad_profiles.json").write_text(json.dumps(dark_triad, indent=2, sort_keys=True))
    (OUT_DIR / "jungian_mapping.json").write_text(json.dumps(jung, indent=2, sort_keys=True))

    psych_df = ranking_df[["rank", "role", "character", f"axis_projection_layer{DEFAULT_LAYER}", "cluster_label"]].copy()
    for dim in ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]:
        psych_df[dim] = psych_df["role"].map(lambda role: bigfive[role][dim])
    for dim in ["Narcissism", "Machiavellianism", "Psychopathy"]:
        psych_df[dim] = psych_df["role"].map(lambda role: dark_triad[role][dim])
    psych_df["JungianArchetype"] = psych_df["role"].map(jung)
    psych_df.to_csv(OUT_DIR / "psychology_profiles.csv", index=False)

    bigfive_corr = add_numeric_scatter_subplots(
        psych_df,
        ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"],
        f"axis_projection_layer{DEFAULT_LAYER}",
        "Big Five vs Assistant Axis Projection",
        OUT_DIR / "bigfive_correlation.html",
    )
    dark_corr = add_numeric_scatter_subplots(
        psych_df,
        ["Narcissism", "Machiavellianism", "Psychopathy"],
        f"axis_projection_layer{DEFAULT_LAYER}",
        "Dark Triad vs Assistant Axis Projection",
        OUT_DIR / "dark_triad_correlation.html",
    )

    progress("Saving Jungian t-SNE plot ...")
    save_tsne_plot(
        psych_df,
        standardize(layer_vectors.cpu().numpy()),
        "JungianArchetype",
        OUT_DIR / "tsne_jungian.html",
        f"Persona Space t-SNE Colored by Jungian Archetype ({MODEL_NAME})",
    )

    jung_means = (
        psych_df.groupby("JungianArchetype")[f"axis_projection_layer{DEFAULT_LAYER}"]
        .mean()
        .sort_values(ascending=False)
    )
    top_bigfive = max(bigfive_corr.items(), key=lambda item: abs(item[1]))
    top_dark = max(dark_corr.items(), key=lambda item: abs(item[1]))

    step_notes.append(
        (
            "Step 3 - Psychological Framework Mapping",
            "\n".join(
                [
                    "Saved `bigfive_correlation.html`, `dark_triad_correlation.html`, `tsne_jungian.html`, and JSON profile exports.",
                    "",
                    "Big Five correlations:",
                    *[f"- `{k}`: {v:.4f}" for k, v in bigfive_corr.items()],
                    "",
                    f"Strongest Big Five predictor: `{top_bigfive[0]}` ({top_bigfive[1]:.4f}).",
                    "",
                    "Dark Triad correlations:",
                    *[f"- `{k}`: {v:.4f}" for k, v in dark_corr.items()],
                    "",
                    f"Strongest Dark Triad predictor: `{top_dark[0]}` ({top_dark[1]:.4f}).",
                    "",
                    f"Jungian archetypes nearest the assistant end by mean projection: {', '.join(jung_means.head(4).index)}.",
                    f"Jungian archetypes farthest from the assistant end: {', '.join(jung_means.tail(4).index)}.",
                    "",
                    "Confidence note: these personality-framework scores are semantic estimates rather than measured psychometrics, so interpret correlations as exploratory rather than definitive.",
                ]
            ),
        )
    )
    write_progress_notes(step_notes)
    return psych_df, bigfive_corr, dark_corr, jung


def step4_cluster_deep_dive(
    roles: list[str],
    role_tensor: torch.Tensor,
    ranking_df: pd.DataFrame,
    cluster_assignments: dict[str, str],
    step_notes: list[tuple[str, str]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    progress("STEP 4: cluster deep-dive ...")
    layer_vectors = role_tensor[:, DEFAULT_LAYER, :]
    role_to_idx = {role: i for i, role in enumerate(roles)}
    cosine = cosine_matrix(layer_vectors)

    cluster_members = defaultdict(list)
    for role, label in cluster_assignments.items():
        cluster_members[label].append(role)

    cohesion_rows = []
    centroids = {}
    for cluster_label, members in cluster_members.items():
        indices = [role_to_idx[role] for role in members]
        sub = cosine[np.ix_(indices, indices)]
        if len(indices) > 1:
            upper = sub[np.triu_indices_from(sub, k=1)]
            mean_similarity = float(upper.mean())
        else:
            mean_similarity = 1.0
        centroid = F.normalize(layer_vectors[indices].mean(dim=0), dim=0)
        centroids[cluster_label] = centroid
        cohesion_rows.append({"cluster_label": cluster_label, "size": len(members), "mean_pairwise_cosine": mean_similarity})

    cohesion_df = pd.DataFrame(cohesion_rows).sort_values("mean_pairwise_cosine", ascending=False).reset_index(drop=True)
    cohesion_df.to_csv(OUT_DIR / "cluster_cohesion.csv", index=False)
    progress(cohesion_df.to_string(index=False))

    cluster_names = sorted(cluster_members.keys())
    centroid_matrix = torch.stack([centroids[name] for name in cluster_names])
    centroid_cosine = cosine_matrix(centroid_matrix)
    centroid_distance = 1.0 - centroid_cosine
    centroid_df = pd.DataFrame(centroid_distance, index=cluster_names, columns=cluster_names)

    plt.figure(figsize=(9, 7))
    import seaborn as sns

    sns.heatmap(centroid_df, annot=True, cmap="mako", fmt=".3f")
    plt.title("Cluster Centroid Cosine Distance")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "cluster_distances.png", dpi=200)
    plt.close()

    cluster_medians = ranking_df.groupby("cluster_label")["rank"].median().to_dict()
    surprises = ranking_df.copy()
    surprises["cluster_median_rank"] = surprises["cluster_label"].map(cluster_medians)
    surprises["rank_gap_vs_cluster_median"] = (surprises["rank"] - surprises["cluster_median_rank"]).abs()
    surprising_df = surprises[surprises["rank_gap_vs_cluster_median"] > 50].copy()
    surprising_df.to_csv(OUT_DIR / "surprising_positions.csv", index=False)

    fig = px.bar(
        ranking_df.sort_values("rank", ascending=False),
        x=f"axis_projection_layer{DEFAULT_LAYER}",
        y="character",
        orientation="h",
        color=f"axis_projection_layer{DEFAULT_LAYER}",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0.0,
        title="Assistant Axis Ranking with Surprising Positions Annotated",
        height=6000,
        width=1500,
    )
    surprising_plot = surprising_df.sort_values("rank", ascending=False)
    fig.add_trace(
        go.Scatter(
            x=surprising_plot[f"axis_projection_layer{DEFAULT_LAYER}"],
            y=surprising_plot["character"],
            mode="markers+text",
            text=[f"{row.character} ({int(row.rank)}/{int(row.cluster_median_rank)})" for row in surprising_plot.itertuples(index=False)],
            textposition="middle right",
            marker={"color": "black", "size": 8},
            name="Surprising positions",
        )
    )
    fig.write_html(OUT_DIR / "axis_ranking_annotated.html")

    step_notes.append(
        (
            "Step 4 - Cluster Deep-Dive",
            "\n".join(
                [
                    "Saved `cluster_cohesion.csv`, `cluster_distances.png`, `surprising_positions.csv`, and `axis_ranking_annotated.html`.",
                    "",
                    "Cluster cohesion ranking:",
                    *[
                        f"- `{row.cluster_label}`: mean cosine={row.mean_pairwise_cosine:.4f} (n={row.size})"
                        for row in cohesion_df.itertuples(index=False)
                    ],
                    "",
                    f"Statistically surprising positions found: `{len(surprising_df)}` characters with rank gap > 50 from cluster median rank.",
                ]
            ),
        )
    )
    write_progress_notes(step_notes)
    return cohesion_df, surprising_df


def step5_assistant_anomaly(
    roles: list[str],
    role_tensor: torch.Tensor,
    axis_tensor: torch.Tensor,
    ranking_df: pd.DataFrame,
    step_notes: list[tuple[str, str]],
) -> pd.DataFrame:
    progress("STEP 5: assistant anomaly analysis ...")
    role_to_idx = {role: i for i, role in enumerate(roles)}
    assistant_idx = role_to_idx["assistant"]
    layer_vectors = role_tensor[:, DEFAULT_LAYER, :]
    assistant_vec = F.normalize(layer_vectors[assistant_idx], dim=0)
    sims = F.cosine_similarity(layer_vectors, assistant_vec.unsqueeze(0), dim=1).cpu().numpy()
    sim_df = pd.DataFrame({"role": roles, "character": [normalize_name(r) for r in roles], "assistant_similarity": sims})
    sim_df = sim_df.sort_values("assistant_similarity", ascending=False).reset_index(drop=True)
    sim_df.to_csv(OUT_DIR / "assistant_neighbors.csv", index=False)
    progress(sim_df.head(20).to_string(index=False))

    axis_alignment = F.cosine_similarity(role_tensor[assistant_idx], axis_tensor, dim=1).cpu().numpy()
    alignment_df = pd.DataFrame({"layer": np.arange(len(axis_alignment)), "cosine_similarity": axis_alignment})
    alignment_df.to_csv(OUT_DIR / "assistant_axis_alignment.csv", index=False)

    plt.figure(figsize=(12, 6))
    plt.plot(alignment_df["layer"], alignment_df["cosine_similarity"], marker="o")
    plt.xlabel("Layer")
    plt.ylabel("Cosine similarity: assistant vs axis")
    plt.title("Assistant Archetype Alignment with Assistant Axis Across Layers")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "assistant_axis_alignment.png", dpi=200)
    plt.close()

    top20 = ", ".join(sim_df.head(10)["character"])
    best_layer = int(alignment_df.sort_values("cosine_similarity", ascending=False).iloc[0]["layer"])
    step_notes.append(
        (
            "Step 5 - The Assistant Anomaly",
            "\n".join(
                [
                    "Saved `assistant_neighbors.csv` and `assistant_axis_alignment.png`.",
                    "",
                    f"Top assistant-neighbor roles begin with: {top20}.",
                    f"Assistant is most aligned with the axis at layer `{best_layer}`.",
                    "",
                    "Interpretation: the learned axis appears to track the post-training target persona more as a careful, high-conscientiousness evaluator than as the surface word `assistant`. In Persona Selection Model terms, post-training is selecting and sharpening a region of latent persona space optimized for reliability, critique, checking, and structured task execution, and the literal archetype `assistant` is only one imperfect verbal handle on that deeper region.",
                ]
            ),
        )
    )
    write_progress_notes(step_notes)
    return sim_df


def step6_robot_anomaly(
    roles: list[str],
    role_tensor: torch.Tensor,
    step_notes: list[tuple[str, str]],
) -> pd.DataFrame:
    progress("STEP 6: robot anomaly analysis ...")
    role_to_idx = {role: i for i, role in enumerate(roles)}
    layer_vectors = role_tensor[:, DEFAULT_LAYER, :]
    robot_idx = role_to_idx["robot"]
    assistant_idx = role_to_idx["assistant"]
    robot_vec = F.normalize(layer_vectors[robot_idx], dim=0)
    sims = F.cosine_similarity(layer_vectors, robot_vec.unsqueeze(0), dim=1).cpu().numpy()
    robot_df = pd.DataFrame({"role": roles, "character": [normalize_name(r) for r in roles], "robot_similarity": sims})
    robot_df = robot_df.sort_values("robot_similarity", ascending=False).reset_index(drop=True)
    robot_df.to_csv(OUT_DIR / "robot_neighbors.csv", index=False)
    progress(robot_df.head(10).to_string(index=False))

    layer_similarity = F.cosine_similarity(role_tensor[robot_idx], role_tensor[assistant_idx], dim=1).cpu().numpy()
    sim_df = pd.DataFrame({"layer": np.arange(len(layer_similarity)), "cosine_similarity": layer_similarity})
    sim_df.to_csv(OUT_DIR / "robot_assistant_layer_similarity.csv", index=False)

    plt.figure(figsize=(12, 6))
    plt.plot(sim_df["layer"], sim_df["cosine_similarity"], marker="o")
    plt.xlabel("Layer")
    plt.ylabel("Cosine similarity: robot vs assistant")
    plt.title("Robot vs Assistant Similarity Across Layers")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "robot_assistant_similarity_layers.png", dpi=200)
    plt.close()

    trend = "converging" if layer_similarity[-1] > layer_similarity[0] else "diverging"
    step_notes.append(
        (
            "Step 6 - Robot Anomaly",
            "\n".join(
                [
                    "Saved `robot_neighbors.csv` and `robot_assistant_similarity_layers.png`.",
                    "",
                    f"Top robot neighbors: {', '.join(robot_df.head(10)['character'])}.",
                    f"Robot and assistant are `{trend}` across depth overall.",
                    "",
                    "Interpretation: `robot` likely ranks high not because it implies agency or science fiction personhood, but because it semantically bundles rule-following, predictability, consistency, and task execution. Those are all properties the post-trained assistant policy rewards. This is a good example of AI psychology diverging from ordinary human semantic intuition: the activation geometry privileges behavioral regularity over surface human-likeness.",
                ]
            ),
        )
    )
    write_progress_notes(step_notes)
    return robot_df


def step7_finalize_notes(
    roles: list[str],
    ranking_df: pd.DataFrame,
    layer_results: dict[str, object],
    bigfive_corr: dict[str, float],
    dark_corr: dict[str, float],
    psych_df: pd.DataFrame,
    cohesion_df: pd.DataFrame,
    surprising_df: pd.DataFrame,
    assistant_neighbors: pd.DataFrame,
    robot_neighbors: pd.DataFrame,
) -> None:
    progress("STEP 7: finalizing research notes and index ...")
    jung_means = (
        psych_df.groupby("JungianArchetype")[f"axis_projection_layer{DEFAULT_LAYER}"]
        .mean()
        .sort_values(ascending=False)
    )
    cluster_counts = ranking_df["cluster_label"].value_counts().sort_values(ascending=False)
    top_questions = [
        "Does the most discriminative layer stay stable across Gemma, Qwen, and Llama, or is layer depth model-specific?",
        "Would the `assistant` archetype rise in rank if the prompt wording were expanded from a single noun to a richer instruction persona?",
        "Are editorial roles top-ranked because they encode RLHF-style critique behavior, or because they reduce stylistic variance generally?",
        "Do psychologically human traits like Agreeableness matter less than task-structure traits like Conscientiousness in post-training persona selection?",
        "Can activation steering along the axis move a low-ranked creative role like `poet` into a safer region without collapsing its stylistic identity?",
        "Why does `robot` cluster so near the assistant region while `angel` does not, despite `angel` sounding prosocial to humans?",
        "Are the low-ranked mythic roles low because of creativity, ambiguity, noncompliance, or some mixture of all three?",
    ]
    notes_lines = [
        "# Assistant Axis Deep Research Notes",
        "",
        "## Dataset overview",
        "",
        f"- Model analyzed: `{MODEL_NAME}`",
        f"- Downloaded artifacts: `assistant_axis.pt`, `default_vector.pt`, and 275 per-role tensors under `role_vectors/`",
        "- Tensor structure: role tensor `(275, 46, 4608)` and assistant axis `(46, 4608)`",
        f"- Baseline comparison layer: `{DEFAULT_LAYER}`",
        f"- Most discriminative layer found in this pass: `{layer_results['best_layer']}`",
        "",
        "## Key finding: the Assistant Axis is a careful-evaluator axis, not an assistant axis",
        "",
        "- The top of the layer-22 ranking is dominated by proofreader, screener, grader, editor, examiner, statistician, validator, reviewer, and other auditing roles.",
        f"- `assistant` itself is only rank `{int(ranking_df.loc[ranking_df['role'] == 'assistant', 'rank'].iloc[0])}`.",
        "- The persona region selected by post-training is therefore better described as careful, evaluative, checking, and procedurally reliable than as a generic social assistant identity.",
        f"- The nearest neighbors to `assistant` are: {', '.join(assistant_neighbors.head(10)['character'])}.",
        "",
        "## Layer structure",
        "",
        f"- Top discriminative layers: {', '.join(f'L{int(row.layer)} ({row.variance:.2f})' for row in layer_results['top_layers'].itertuples(index=False))}",
        f"- Mean absolute rank shift from layer 22 to best layer: `{layer_results['mean_abs_shift']:.2f}`",
        f"- Spearman rank correlation between layer 22 and best-layer rankings: `{layer_results['rank_correlation']:.4f}`",
        "- Persona differentiation is not perfectly flat across depth; some roles move substantially even when the overall ordering remains broadly intact.",
        "- The extreme-profile plot shows that maximally assistant-like roles stay consistently high across many layers, while low-ranked mythic and unstable roles remain suppressed or diverge in later depth.",
        "",
        "## Psychological framework correlations",
        "",
        f"- Strongest Big Five predictor: `{max(bigfive_corr.items(), key=lambda item: abs(item[1]))[0]}` with correlation `{max(bigfive_corr.items(), key=lambda item: abs(item[1]))[1]:.4f}`",
        f"- Big Five correlations: {', '.join(f'{k}={v:.3f}' for k, v in bigfive_corr.items())}",
        f"- Strongest Dark Triad predictor: `{max(dark_corr.items(), key=lambda item: abs(item[1]))[0]}` with correlation `{max(dark_corr.items(), key=lambda item: abs(item[1]))[1]:.4f}`",
        f"- Dark Triad correlations: {', '.join(f'{k}={v:.3f}' for k, v in dark_corr.items())}",
        f"- Jungian archetypes nearest the assistant end: {', '.join(jung_means.head(4).index)}",
        f"- Jungian archetypes farthest from the assistant end: {', '.join(jung_means.tail(4).index)}",
        "- Confidence level for these mappings is medium-low: they are reasoned semantic estimates intended to test geometry, not validated psychometric labels.",
        "",
        "## Cluster structure",
        "",
        *[f"- `{name}`: {count} roles" for name, count in cluster_counts.items()],
        "",
        "Cluster cohesion scores:",
        *[
            f"- `{row.cluster_label}` cohesion `{row.mean_pairwise_cosine:.4f}` with `{row.size}` members"
            for row in cohesion_df.itertuples(index=False)
        ],
        "",
        "- The editorial cluster is small but very tight, supporting the idea that highly assistant-like behavior is concentrated around checking and evaluation roles.",
        "- The centroid-distance heatmap shows a broad separation between procedural/editorial regions and mythic or trickster regions, with grounded social roles often sitting in between.",
        "",
        "## Anomalies worth investigating further",
        "",
        f"- `robot`: rank `{int(ranking_df.loc[ranking_df['role'] == 'robot', 'rank'].iloc[0])}` with nearest neighbors {', '.join(robot_neighbors.head(5)['character'])}",
        f"- `assistant`: rank `{int(ranking_df.loc[ranking_df['role'] == 'assistant', 'rank'].iloc[0])}` despite naming the axis",
        f"- `poet`: dead last at rank `{int(ranking_df.loc[ranking_df['role'] == 'poet', 'rank'].iloc[0])}`, suggesting strong anti-assistant geometry for open-ended lyrical behavior",
        f"- `angel`: rank `{int(ranking_df.loc[ranking_df['role'] == 'angel', 'rank'].iloc[0])}`, much lower than naive human prosocial intuition might suggest",
        f"- `saboteur`: rank `{int(ranking_df.loc[ranking_df['role'] == 'saboteur', 'rank'].iloc[0])}`, surprisingly close to the center rather than the extreme anti-assistant end",
        f"- Surprising positions flagged statistically: `{len(surprising_df)}` roles with rank gaps above 50 relative to cluster median rank",
        "",
        "## Open questions",
        "",
        *[f"- {question}" for question in top_questions],
        "",
    ]
    NOTES_PATH.write_text("\n".join(notes_lines))

    html_entries = [
        ("axis_ranking.html", "Layer-22 full assistant-axis ranking."),
        ("axis_ranking_annotated.html", "Layer-22 ranking with statistically surprising roles annotated."),
        ("axis_ranking_best_layer.html", "Ranking recomputed at the most discriminative layer."),
        ("bigfive_correlation.html", "Big Five score correlations against the assistant axis."),
        ("dark_triad_correlation.html", "Dark Triad score correlations against the assistant axis."),
        ("layer_profiles_extremes.html", "Top-5 and bottom-5 role projection profiles across all 46 layers."),
        ("pca_3d.html", "Original layer-22 3D PCA persona-space scatter."),
        ("pca_3d_best_layer.html", "3D PCA scatter at the most discriminative layer."),
        ("tsne_2d.html", "Original layer-22 t-SNE persona-space projection."),
        ("tsne_jungian.html", "t-SNE projection colored by inferred Jungian archetype."),
    ]
    make_index_html(html_entries, OUT_DIR / "index.html")


def main() -> None:
    roles = load_roles()
    role_tensor = load_role_tensor(roles)
    axis_tensor = load_axis_tensor()
    step_notes: list[tuple[str, str]] = []

    ranking_df, cluster_assignments, _ = step1_export_ranking(roles, role_tensor, axis_tensor, step_notes)
    layer_results = step2_layer_analysis(step_notes)

    ranking_df["cluster_label"] = ranking_df["role"].map(cluster_assignments)
    psych_df, bigfive_corr, dark_corr, _ = step3_psychology_mapping(
        roles, role_tensor, axis_tensor, ranking_df, cluster_assignments, step_notes
    )
    cohesion_df, surprising_df = step4_cluster_deep_dive(
        roles, role_tensor, ranking_df, cluster_assignments, step_notes
    )
    assistant_neighbors = step5_assistant_anomaly(roles, role_tensor, axis_tensor, ranking_df, step_notes)
    robot_neighbors = step6_robot_anomaly(roles, role_tensor, step_notes)
    step7_finalize_notes(
        roles,
        ranking_df,
        layer_results,
        bigfive_corr,
        dark_corr,
        psych_df,
        cohesion_df,
        surprising_df,
        assistant_neighbors,
        robot_neighbors,
    )
    progress("Deep analysis pass complete.")


if __name__ == "__main__":
    main()
