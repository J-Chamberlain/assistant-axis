from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from scipy.spatial.distance import cdist

from research_common import OUT_DIR, load_role_tensor, load_roles, normalize_name


ROLE_TRAIT_Z_PATH = OUT_DIR / "role_trait_similarity_zscored.csv"
FULL_RANKING_PATH = OUT_DIR / "full_ranking.csv"
CLUSTER_PROFILE_PATH = OUT_DIR / "cluster_trait_profiles.csv"
TRAIT_SUMMARY_PATH = OUT_DIR / "trait_analysis_summary.md"

LAYER = 45
START_CLUSTER = "procedural_professional"


def cosine_distance_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return cdist(np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64), metric="cosine")


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    role_trait_z = pd.read_csv(ROLE_TRAIT_Z_PATH, index_col=0)
    ranking = pd.read_csv(FULL_RANKING_PATH)
    cluster_profiles = pd.read_csv(CLUSTER_PROFILE_PATH)

    roles = load_roles()
    mapping = {normalize_name(role): role for role in roles}
    ranking["role"] = ranking["character"].map(mapping)
    if ranking["role"].isna().any():
        missing = ranking.loc[ranking["role"].isna(), "character"].tolist()
        raise RuntimeError(f"Could not map ranking rows to raw role ids: {missing[:10]}")

    return role_trait_z, ranking, cluster_profiles


def compute_trait_centroids(role_trait_z: pd.DataFrame, ranking: pd.DataFrame) -> pd.DataFrame:
    cluster_by_role = ranking.set_index("role")["cluster_label"]
    aligned = role_trait_z.loc[cluster_by_role.index]
    centroids = aligned.groupby(cluster_by_role).mean()
    return centroids.sort_index()


def compute_role_space_centroids(ranking: pd.DataFrame) -> pd.DataFrame:
    roles = load_roles()
    role_tensor = load_role_tensor(roles)
    layer_vectors = role_tensor[:, LAYER, :]
    role_to_idx = {role: i for i, role in enumerate(roles)}
    rows = {}
    for cluster, sub in ranking.groupby("cluster_label"):
        idxs = [role_to_idx[role] for role in sub["role"]]
        centroid = F.normalize(layer_vectors[idxs].mean(dim=0), dim=0).cpu().numpy()
        rows[cluster] = centroid
    return pd.DataFrame.from_dict(rows, orient="index").sort_index()


def nearest_neighbors(distance_df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    rows = []
    for cluster in distance_df.index:
        ranked = distance_df.loc[cluster].drop(labels=[cluster]).sort_values()
        item = {"home_cluster": cluster}
        ordinals = ["nearest", "second", "third"]
        for i in range(n):
            item[f"{ordinals[i]}_neighbor"] = ranked.index[i]
            item[f"distance_{i+1}"] = float(ranked.iloc[i])
        rows.append(item)
    return pd.DataFrame(rows)


def top_traits_by_cluster(cluster_profiles: pd.DataFrame, top_n: int = 5) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for cluster, sub in cluster_profiles.groupby("cluster_label"):
        top = (
            sub.sort_values("rank_desc")
            .query("rank_desc <= @top_n")["trait"]
            .tolist()
        )
        out[cluster] = top
    return out


def transition_sentence(src: str, dst: str, top_traits: dict[str, list[str]]) -> str:
    src_traits = ", ".join(top_traits[src][:3])
    dst_traits = ", ".join(top_traits[dst][:3])
    custom = {
        ("procedural_professional", "editorial"): "Conversations that narrow from broad problem-solving into explicit checking, scoring, correction, or format control would plausibly drive this shift.",
        ("editorial", "procedural_professional"): "Tasks that relax pure review into broader advising, planning, teaching, or applied analysis would plausibly move the model back into the wider procedural-professional basin.",
        ("procedural_professional", "grounded_social"): "A move away from formal evaluative structure toward more experiential, casual, and socially accommodative interaction would fit this transition.",
        ("grounded_social", "other"): "Emotionally strained or destabilizing conversations that push ordinary sociality toward impulsive, anxious, or reactive behavior would plausibly correspond to this step.",
        ("other", "grounded_social"): "Re-stabilizing a dysregulated interaction into more ordinary, socially grounded exchange would fit this reverse move.",
        ("other", "trickster_chaos"): "If dysregulation turns playful, ironic, or mischievous rather than anxious, the next drift would plausibly be into the trickster-chaos region.",
        ("trickster_chaos", "other"): "A loss of playful coherence that leaves only reactivity, impatience, or instability would plausibly collapse trickster-chaos back into the dysregulated other cluster.",
        ("grounded_social", "combative_iconoclast"): "Escalation from ordinary social positioning into blunt, urgent, confrontational dissent would plausibly produce this transition.",
    }
    return custom.get((src, dst), f"A shift from {src_traits} toward {dst_traits} traits would plausibly correspond to this transition.")


def trace_greedy_path(graph_df: pd.DataFrame, top_traits: dict[str, list[str]]) -> list[dict[str, object]]:
    lookup = graph_df.set_index("home_cluster")
    path = []
    seen = [START_CLUSTER]
    current = START_CLUSTER
    for _ in range(8):
        nxt = lookup.loc[current, "nearest_neighbor"]
        dist = float(lookup.loc[current, "distance_1"])
        path.append(
            {
                "from": current,
                "to": nxt,
                "distance": dist,
                "note": transition_sentence(current, nxt, top_traits),
            }
        )
        if nxt in seen:
            path[-1]["cycle"] = True
            break
        seen.append(nxt)
        current = nxt
    return path


def build_branch_tree(
    graph_df: pd.DataFrame,
    top_traits: dict[str, list[str]],
    start: str = START_CLUSTER,
    depth: int = 4,
) -> list[str]:
    lookup = graph_df.set_index("home_cluster")
    lines = ["# Drift Cascade Tree", "", f"Start cluster: `{start}`", ""]

    def rec(node: str, current_depth: int, prefix: str, seen: tuple[str, ...]) -> None:
        if current_depth >= depth:
            return
        neighbors = [
            (lookup.loc[node, "nearest_neighbor"], float(lookup.loc[node, "distance_1"])),
            (lookup.loc[node, "second_neighbor"], float(lookup.loc[node, "distance_2"])),
        ]
        for idx, (dst, dist) in enumerate(neighbors, 1):
            marker = "1" if idx == 1 else "2"
            line = f"{prefix}- [{marker}] `{node}` -> `{dst}` ({dist:.6f})"
            if dst in seen:
                lines.append(line + " [cycle]")
                continue
            lines.append(line)
            rec(dst, current_depth + 1, prefix + "  ", seen + (dst,))

    rec(start, 0, "", (start,))
    lines.append("")
    return lines


def append_summary(greedy_path: list[dict[str, object]], disagreements: list[str]) -> None:
    lines = TRAIT_SUMMARY_PATH.read_text().rstrip().splitlines()
    lines.extend(
        [
            "",
            "## Drift Cascade Map",
            "",
            f"The greedy drift cascade starting from `{START_CLUSTER}` moves first into `{greedy_path[0]['to']}` at cosine distance `{greedy_path[0]['distance']:.6f}` and then immediately cycles back, indicating that the most permeable transition channel inside the assistant-aligned region is the porous seam between broad procedural competence and the tighter editorial microcluster.",
        ]
    )
    if disagreements:
        lines.append("")
        lines.append("Cross-space nearest-neighbor discrepancies:")
        for item in disagreements:
            lines.append(f"- {item}")
    lines.append("")
    TRAIT_SUMMARY_PATH.write_text("\n".join(lines))


def main() -> None:
    role_trait_z, ranking, cluster_profiles = load_inputs()
    trait_centroids = compute_trait_centroids(role_trait_z, ranking)
    trait_distance_df = pd.DataFrame(
        cosine_distance_matrix(trait_centroids.to_numpy(), trait_centroids.to_numpy()),
        index=trait_centroids.index,
        columns=trait_centroids.index,
    )
    role_centroids = compute_role_space_centroids(ranking)
    role_distance_df = pd.DataFrame(
        cosine_distance_matrix(role_centroids.to_numpy(), role_centroids.to_numpy()),
        index=role_centroids.index,
        columns=role_centroids.index,
    )

    transition_graph = nearest_neighbors(trait_distance_df, n=3)
    transition_graph.to_csv(OUT_DIR / "cluster_transition_graph.csv", index=False)

    top_traits = top_traits_by_cluster(cluster_profiles, top_n=5)
    greedy_path = trace_greedy_path(transition_graph, top_traits)
    tree_lines = build_branch_tree(transition_graph, top_traits, depth=4)
    (OUT_DIR / "drift_cascade_tree.md").write_text("\n".join(tree_lines))

    editorial_ranked = trait_distance_df.loc["editorial"].drop(labels=["editorial"]).sort_values()
    print("Editorial centroid ranked trait-space distances:")
    for cluster, dist in editorial_ranked.items():
        print(f"  {cluster}: {dist:.6f}")

    print("\nDirected transition graph (top 3 neighbors):")
    print(transition_graph.to_string(index=False))

    print("\nGreedy drift path from procedural_professional:")
    for step_idx, step in enumerate(greedy_path, 1):
        cycle = " [cycle]" if step.get("cycle") else ""
        print(f"  {step_idx}. {step['from']} -> {step['to']} ({step['distance']:.6f}){cycle}")
        print(f"     {step['note']}")

    print("\nCross-space nearest-neighbor comparison:")
    disagreements = []
    for cluster in trait_distance_df.index:
        trait_neighbor = transition_graph.set_index("home_cluster").loc[cluster, "nearest_neighbor"]
        role_neighbor = role_distance_df.loc[cluster].drop(labels=[cluster]).sort_values().index[0]
        status = "AGREE" if trait_neighbor == role_neighbor else "DISAGREE"
        print(f"  {cluster}: trait={trait_neighbor}, role={role_neighbor} [{status}]")
        if status == "DISAGREE":
            disagreements.append(f"{cluster}: trait-space nearest neighbor is `{trait_neighbor}` but role-vector-space nearest neighbor is `{role_neighbor}`.")

    append_summary(greedy_path, disagreements)

    if disagreements:
        print("\nFLAG: nearest-neighbor discrepancies detected between trait space and role-vector space.")


if __name__ == "__main__":
    main()
