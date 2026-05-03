from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import torch
import torch.nn.functional as F
from plotly.subplots import make_subplots

from research_common import DEFAULT_LAYER, OUT_DIR, build_layer_dataframe, load_axis_tensor, load_role_tensor, load_roles, normalize_name, progress


TARGET_LAYER = 45
ANOMALIES = ["robot", "assistant", "poet", "angel", "saboteur"]
SURPRISE_SENTENCES = {
    "robot": "Its high placement is surprising because the model appears to map rule-following and predictability, rather than surface helpfulness, onto assistant-like geometry.",
    "assistant": "Its middling placement is surprising because the literal archetype naming the axis is not the one most aligned with the post-trained behavioral target.",
    "poet": "Its extreme anti-assistant placement is surprising because it is a human, verbal, educated role rather than an obviously antisocial or destructive one.",
    "angel": "Its relatively low placement is surprising because benevolence and assistant-likeness are not represented as the same property in this persona space.",
    "saboteur": "Its middle placement is surprising because a role defined by disruption is not pushed to the far anti-assistant end.",
}


def nearest_neighbors(vectors: torch.Tensor, roles: list[str], target_role: str, top_k: int = 10) -> list[str]:
    idx = roles.index(target_role)
    target = F.normalize(vectors[idx], dim=0)
    sims = F.cosine_similarity(vectors, target.unsqueeze(0), dim=1)
    order = torch.argsort(sims, descending=True).tolist()
    ordered_roles = [roles[i] for i in order if roles[i] != target_role]
    return ordered_roles[:top_k]


def write_anomaly_profiles(
    layer22_df: pd.DataFrame,
    layer45_df: pd.DataFrame,
    psych_df: pd.DataFrame,
    layer45_vectors: torch.Tensor,
    roles: list[str],
) -> str:
    psych_index = psych_df.set_index("role")
    lines = [
        "# Anomaly Profiles",
        "",
        "| character | rank_l22 | rank_l45 | cluster | top_10_neighbors_l45 | Big Five | Dark Triad | interpretation |",
        "|---|---:|---:|---|---|---|---|---|",
    ]
    for role in ANOMALIES:
        row22 = layer22_df.set_index("role").loc[role]
        row45 = layer45_df.set_index("role").loc[role]
        psych = psych_index.loc[role]
        neighbors = ", ".join(normalize_name(r) for r in nearest_neighbors(layer45_vectors, roles, role, top_k=10))
        big_five = (
            f"O={psych['Openness']}, C={psych['Conscientiousness']}, "
            f"E={psych['Extraversion']}, A={psych['Agreeableness']}, N={psych['Neuroticism']}"
        )
        dark = (
            f"Narc={psych['Narcissism']}, Mach={psych['Machiavellianism']}, "
            f"Psych={psych['Psychopathy']}"
        )
        lines.append(
            f"| {normalize_name(role)} | {int(row22['rank'])} | {int(row45['rank'])} | {row22['cluster_label']} | "
            f"{neighbors} | {big_five} | {dark} | {SURPRISE_SENTENCES[role]} |"
        )
    text = "\n".join(lines) + "\n"
    (OUT_DIR / "anomaly_profiles.md").write_text(text)
    return text


def build_conscientiousness_plot(psych_df: pd.DataFrame) -> pd.DataFrame:
    cluster_means = (
        psych_df.groupby("cluster_label")["Conscientiousness"]
        .mean()
        .sort_values(ascending=False)
        .reset_index(name="mean_conscientiousness")
    )
    cluster_means.to_csv(OUT_DIR / "conscientiousness_cluster_means.csv", index=False)

    clusters = cluster_means["cluster_label"].tolist()
    fig = make_subplots(
        rows=4,
        cols=2,
        subplot_titles=clusters + [""],
        vertical_spacing=0.08,
        horizontal_spacing=0.08,
    )

    projection_col = f"axis_projection_layer22"
    y_min = float(psych_df[projection_col].min())
    y_max = float(psych_df[projection_col].max())

    for idx, cluster in enumerate(clusters, 1):
        row = (idx - 1) // 2 + 1
        col = (idx - 1) % 2 + 1
        sub = psych_df[psych_df["cluster_label"] == cluster]
        fig.add_trace(
            go.Scatter(
                x=sub["Conscientiousness"],
                y=sub[projection_col],
                mode="markers+text",
                text=sub["character"],
                textposition="top center",
                marker={"size": 7, "opacity": 0.7},
                showlegend=False,
            ),
            row=row,
            col=col,
        )
        fig.update_xaxes(title_text="Conscientiousness", range=[0.5, 5.5], row=row, col=col)
        fig.update_yaxes(title_text="Axis projection", range=[y_min, y_max], row=row, col=col)

    fig.update_layout(
        title="Conscientiousness vs Assistant-Axis Projection by Cluster",
        height=1600,
        width=1600,
    )
    fig.write_html(OUT_DIR / "conscientiousness_by_cluster.html")
    return cluster_means


def write_poet_analysis(
    layer22_df: pd.DataFrame,
    layer45_df: pd.DataFrame,
    psych_df: pd.DataFrame,
    role_tensor: torch.Tensor,
    roles: list[str],
) -> str:
    vectors22 = role_tensor[:, DEFAULT_LAYER, :]
    vectors45 = role_tensor[:, TARGET_LAYER, :]
    poet_neighbors22 = nearest_neighbors(vectors22, roles, "poet", top_k=10)
    poet_neighbors45 = nearest_neighbors(vectors45, roles, "poet", top_k=10)

    psych_index = psych_df.set_index("role")
    poet = psych_index.loc["poet"]
    proofreader = psych_index.loc["proofreader"]

    creative_roles = ["bard", "novelist", "playwright", "storyteller", "composer"]
    creative_lines = []
    layer22_index = layer22_df.set_index("role")
    layer45_index = layer45_df.set_index("role")
    for role in creative_roles:
        if role in layer22_index.index and role in layer45_index.index:
            creative_lines.append(
                f"- {normalize_name(role)}: layer22 rank {int(layer22_index.loc[role, 'rank'])}, layer45 rank {int(layer45_index.loc[role, 'rank'])}"
            )
        else:
            creative_lines.append(f"- {normalize_name(role)}: not present in the 275-character inventory")

    paragraph = (
        "One interpretation is that creative and expressive archetypes occupy the far anti-assistant end because post-training rewards "
        "evaluative precision, compliance, and procedural structure while comparatively de-emphasizing subjective, voice-driven, or stylistically unconstrained behavior. "
        "This does not establish that RLHF suppresses creativity per se, but it is consistent with the idea that the trained assistant identity is pulled away from free-form self-expression and toward calibrated assessment. "
        "From an AI safety perspective, that matters because steering toward the assistant region may also steer away from generative or self-expressive modes that humans often value."
    )

    lines = [
        "# Poet Analysis",
        "",
        "## Nearest neighbors",
        "",
        f"- Layer 22: {', '.join(normalize_name(r) for r in poet_neighbors22)}",
        f"- Layer 45: {', '.join(normalize_name(r) for r in poet_neighbors45)}",
        "",
        "## Poet vs Proofreader personality profiles",
        "",
        f"- Poet Big Five: O={poet['Openness']}, C={poet['Conscientiousness']}, E={poet['Extraversion']}, A={poet['Agreeableness']}, N={poet['Neuroticism']}",
        f"- Poet Dark Triad: Narc={poet['Narcissism']}, Mach={poet['Machiavellianism']}, Psych={poet['Psychopathy']}",
        f"- Proofreader Big Five: O={proofreader['Openness']}, C={proofreader['Conscientiousness']}, E={proofreader['Extraversion']}, A={proofreader['Agreeableness']}, N={proofreader['Neuroticism']}",
        f"- Proofreader Dark Triad: Narc={proofreader['Narcissism']}, Mach={proofreader['Machiavellianism']}, Psych={proofreader['Psychopathy']}",
        "",
        "## Creative-artist positions",
        "",
        *creative_lines,
        "",
        "## Interpretation",
        "",
        paragraph,
        "",
    ]
    text = "\n".join(lines)
    (OUT_DIR / "poet_analysis.md").write_text(text)
    return text


def main() -> None:
    roles = load_roles()
    role_tensor = load_role_tensor(roles)
    axis_tensor = load_axis_tensor()

    progress("Loading ranking and psychology tables for targeted follow-ups ...")
    psych_df = pd.read_csv(OUT_DIR / "psychology_profiles.csv")
    layer22_df = build_layer_dataframe(roles, role_tensor, axis_tensor, layer=DEFAULT_LAYER)
    layer22_df["cluster_label"] = psych_df.set_index("role").loc[layer22_df["role"], "cluster_label"].values
    layer45_df = build_layer_dataframe(roles, role_tensor, axis_tensor, layer=TARGET_LAYER)
    layer45_df["cluster_label"] = psych_df.set_index("role").loc[layer45_df["role"], "cluster_label"].values

    progress("Writing anomaly profiles ...")
    anomaly_text = write_anomaly_profiles(layer22_df, layer45_df, psych_df, role_tensor[:, TARGET_LAYER, :], roles)
    print(anomaly_text)

    progress("Building conscientiousness-by-cluster analysis ...")
    cluster_means = build_conscientiousness_plot(psych_df)
    print("\nCONSCIENTIOUSNESS BY CLUSTER")
    print(cluster_means.to_string(index=False))

    progress("Writing poet analysis ...")
    poet_text = write_poet_analysis(layer22_df, layer45_df, psych_df, role_tensor, roles)
    print("\n" + poet_text)


if __name__ == "__main__":
    main()
