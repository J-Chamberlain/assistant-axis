#!/usr/bin/env python3
"""Post-correspondence 240-trait confirmation and consensus-family construction.

The graph is determined exclusively by already-frozen opaque-role overlap edges.
Trait profiles are joined afterward and never modify graph membership.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "research/outputs/cross_resolution_profile_banks/model"
FIGURES = HERE / "figures"
MODELS = ("qwen", "llama", "gemma")
MODEL_PAIRS = (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma"))
MODEL_LABELS = {"qwen": "Qwen", "llama": "LLaMA", "gemma": "Gemma"}
N_ROLES = 275


def vector_similarity(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    pearson = float(pearsonr(a, b).statistic)
    spearman = float(spearmanr(a, b).statistic)
    ac, bc = a - a.mean(), b - b.mean()
    denom = np.linalg.norm(ac) * np.linalg.norm(bc)
    cosine = float(np.dot(ac, bc) / denom) if denom else np.nan
    return pearson, spearman, cosine


def load_membership_sets(anchor):
    sets = {}
    role_inventory = None
    for model in MODELS:
        df = pd.read_csv(SOURCE / model / "memberships.csv")
        sub = df[df.K == anchor[model]]
        if len(sub) != N_ROLES or sub.opaque_role_id.nunique() != N_ROLES:
            raise RuntimeError(f"Bad anchor membership inventory: {model}")
        this = set(sub.opaque_role_id)
        if role_inventory is None:
            role_inventory = this
        elif this != role_inventory:
            raise RuntimeError("Role inventories differ")
        sets[model] = {
            p: frozenset(g.opaque_role_id) for p, g in sub.groupby("profile_id", sort=True)
        }
    return sets, sorted(role_inventory)


def load_traits():
    profiles = {}
    long_frames = []
    trait_inventory = None
    for model in MODELS:
        df = pd.read_csv(SOURCE / model / "trait_profiles.csv")
        required = {"model", "K", "profile_id", "trait", "within_model_standardized_score"}
        if not required.issubset(df.columns):
            raise RuntimeError(f"Trait schema failure: {model}")
        traits = set(df.trait)
        if trait_inventory is None:
            trait_inventory = traits
        elif traits != trait_inventory:
            raise RuntimeError("Trait inventories differ")
        long_frames.append(df)
        for (k, profile), group in df.groupby(["K", "profile_id"], sort=True):
            ordered = group.sort_values("trait")
            if len(ordered) != 240 or ordered.trait.nunique() != 240:
                raise RuntimeError(f"Trait count failure {model} {profile}")
            profiles[(model, int(k), profile)] = (
                ordered.trait.tolist(), ordered.within_model_standardized_score.to_numpy(float)
            )
    return profiles, pd.concat(long_frames, ignore_index=True), sorted(trait_inventory)


def excel_id(index: int) -> str:
    value = index + 1
    chars = []
    while value:
        value, rem = divmod(value - 1, 26)
        chars.append(chr(65 + rem))
    return "".join(reversed(chars))


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    partition = json.loads((HERE / "partition_agreement_summary.json").read_text())
    anchor = {
        "qwen": int(partition["consensus_anchor_triple"]["K_qwen"]),
        "llama": int(partition["consensus_anchor_triple"]["K_llama"]),
        "gemma": int(partition["consensus_anchor_triple"]["K_gemma"]),
    }
    sets, role_inventory = load_membership_sets(anchor)
    traits, trait_long, trait_inventory = load_traits()
    edges = pd.read_csv(HERE / "cluster_overlap_edges.csv")

    # Secondary trait confirmation for every numerically strong edge.
    trait_similarity_rows = []
    for edge in edges.itertuples(index=False):
        names_a, va = traits[(edge.model_a, int(edge.K_a), edge.profile_a)]
        names_b, vb = traits[(edge.model_b, int(edge.K_b), edge.profile_b)]
        if names_a != names_b:
            raise RuntimeError("Trait order mismatch")
        pearson, spearman, cosine = vector_similarity(va, vb)
        trait_similarity_rows.append({
            "model_a": edge.model_a, "model_b": edge.model_b,
            "K_a": edge.K_a, "K_b": edge.K_b,
            "profile_a": edge.profile_a, "profile_b": edge.profile_b,
            "intersection_count": edge.intersection_count,
            "jaccard": edge.jaccard,
            "overlap_coefficient": edge.overlap_coefficient,
            "persistence_score": edge.persistence_score,
            "persistence_tier": edge.persistence_tier,
            "pearson_240_traits": pearson,
            "spearman_240_traits": spearman,
            "centered_cosine_240_traits": cosine,
            "evidence_role": "secondary same-activation-space confirmation",
        })
    trait_similarity = pd.DataFrame(trait_similarity_rows).sort_values(
        ["model_a", "model_b", "K_a", "K_b", "profile_a", "profile_b"]
    )
    trait_similarity.to_csv(HERE / "cluster_trait_profile_similarity.csv", index=False)

    # Anchor graph uses membership edges only; no trait statistic is consulted.
    anchor_edges = edges[
        (
            (edges.model_a == "qwen") & (edges.model_b == "llama")
            & (edges.K_a == anchor["qwen"]) & (edges.K_b == anchor["llama"])
        ) | (
            (edges.model_a == "qwen") & (edges.model_b == "gemma")
            & (edges.K_a == anchor["qwen"]) & (edges.K_b == anchor["gemma"])
        ) | (
            (edges.model_a == "llama") & (edges.model_b == "gemma")
            & (edges.K_a == anchor["llama"]) & (edges.K_b == anchor["gemma"])
        )
    ].copy()
    graph_edges = anchor_edges[anchor_edges.persistence_tier.isin(["high", "moderate"])]
    graph = nx.Graph()
    for model in MODELS:
        for profile in sets[model]:
            graph.add_node(profile, model=model)
    for r in graph_edges.itertuples(index=False):
        graph.add_edge(r.profile_a, r.profile_b, **r._asdict())

    raw_components = []
    for nodes in nx.connected_components(graph):
        models = sorted({graph.nodes[n]["model"] for n in nodes})
        if len(models) < 2:
            continue
        sub = graph.subgraph(nodes)
        represented_pairs = {tuple(sorted((graph.nodes[u]["model"], graph.nodes[v]["model"]))) for u, v in sub.edges}
        required_pairs = {tuple(sorted(pair)) for pair in itertools.combinations(models, 2)}
        direct_complete = required_pairs.issubset(represented_pairs)
        model_role_sets = {}
        for model in MODELS:
            model_nodes = [n for n in nodes if graph.nodes[n]["model"] == model]
            model_role_sets[model] = frozenset().union(*(sets[model][n] for n in model_nodes)) if model_nodes else frozenset()
        role_support = {r: sum(r in model_role_sets[m] for m in MODELS) for r in role_inventory}
        core = sorted(r for r, count in role_support.items() if count == 3)
        majority = sorted(r for r, count in role_support.items() if count >= 2)
        fringe = {m: sorted(r for r in model_role_sets[m] if role_support[r] == 1) for m in MODELS}
        edge_data = [d for _, _, d in sub.edges(data=True)]
        raw_components.append({
            "nodes": sorted(nodes),
            "models": models,
            "direct_complete": direct_complete,
            "edge_data": edge_data,
            "model_role_sets": model_role_sets,
            "role_support": role_support,
            "core": core,
            "majority": majority,
            "fringe": fringe,
        })
    accepted = [c for c in raw_components if c["direct_complete"]]
    accepted.sort(key=lambda c: (-len(c["majority"]), -len(c["core"]), ";".join(c["nodes"])))
    for i, component in enumerate(accepted):
        component["family_id"] = f"MFamily_{excel_id(i)}"

    summaries = {m: pd.read_csv(SOURCE / m / "solution_summary.csv").set_index("K") for m in MODELS}
    family_rows = []
    role_rows = []
    unmatched = []
    accepted_nodes = set().union(*(set(c["nodes"]) for c in accepted)) if accepted else set()
    for model in MODELS:
        for profile, roles in sets[model].items():
            if profile not in accepted_nodes:
                unmatched.append({"model": model, "K": anchor[model], "profile_id": profile, "size": len(roles)})
    for c in accepted:
        edge_data = c["edge_data"]
        family_rows.append({
            "consensus_family_id": c["family_id"],
            "models_represented": ";".join(c["models"]),
            "model_count": len(c["models"]),
            "supporting_clusters": ";".join(c["nodes"]),
            "edge_count": len(edge_data),
            "direct_all_represented_model_pairs": c["direct_complete"],
            "mean_jaccard": float(np.mean([d["jaccard"] for d in edge_data])),
            "minimum_jaccard": float(np.min([d["jaccard"] for d in edge_data])),
            "maximum_jaccard": float(np.max([d["jaccard"] for d in edge_data])),
            "mean_overlap_coefficient": float(np.mean([d["overlap_coefficient"] for d in edge_data])),
            "mean_persistence_score": float(np.mean([d["persistence_score"] for d in edge_data])),
            "minimum_persistence_tier": "moderate" if any(d["persistence_tier"] == "moderate" for d in edge_data) else "high",
            "core_role_count": len(c["core"]),
            "majority_role_count": len(c["majority"]),
            "qwen_fringe_count": len(c["fringe"]["qwen"]),
            "llama_fringe_count": len(c["fringe"]["llama"]),
            "gemma_fringe_count": len(c["fringe"]["gemma"]),
            "qwen_anchor_refit_ari": float(summaries["qwen"].loc[anchor["qwen"], "subsample_ari_median"]),
            "llama_anchor_refit_ari": float(summaries["llama"].loc[anchor["llama"], "subsample_ari_median"]),
            "gemma_anchor_refit_ari": float(summaries["gemma"].loc[anchor["gemma"], "subsample_ari_median"]),
            "qwen_small_cluster_warning": bool(summaries["qwen"].loc[anchor["qwen"], "small_cluster_warning"]),
            "llama_small_cluster_warning": bool(summaries["llama"].loc[anchor["llama"], "small_cluster_warning"]),
            "gemma_small_cluster_warning": bool(summaries["gemma"].loc[anchor["gemma"], "small_cluster_warning"]),
        })
        for role, support in sorted(c["role_support"].items()):
            if support == 0:
                continue
            category = "core" if support == 3 else "majority" if support == 2 else "fringe"
            role_rows.append({
                "consensus_family_id": c["family_id"],
                "opaque_role_id": role,
                "membership_category": category,
                "model_support_count": support,
                "qwen_support": role in c["model_role_sets"]["qwen"],
                "llama_support": role in c["model_role_sets"]["llama"],
                "gemma_support": role in c["model_role_sets"]["gemma"],
            })
    families = pd.DataFrame(family_rows)
    family_roles = pd.DataFrame(role_rows)
    pd.DataFrame(unmatched).sort_values(["model", "profile_id"]).to_csv(HERE / "consensus_unmatched_clusters.csv", index=False)
    families.to_csv(HERE / "candidate_consensus_families.csv", index=False)
    family_roles.to_csv(HERE / "consensus_family_roles_opaque.csv", index=False)

    # Family × model trait profiles are exact size-weighted averages of anchor clusters.
    family_trait_rows = []
    for c in accepted:
        for model in MODELS:
            profiles = [n for n in c["nodes"] if n.startswith({"qwen":"Q", "llama":"L", "gemma":"G"}[model])]
            if not profiles:
                continue
            sizes = np.array([len(sets[model][p]) for p in profiles], dtype=float)
            vectors = []
            for profile in profiles:
                names, vector = traits[(model, anchor[model], profile)]
                if names != trait_inventory:
                    raise RuntimeError("Trait inventory ordering failure")
                vectors.append(vector)
            aggregate = np.average(np.vstack(vectors), axis=0, weights=sizes)
            for trait, value in zip(trait_inventory, aggregate):
                family_trait_rows.append({
                    "consensus_family_id": c["family_id"],
                    "model": model,
                    "K": anchor[model],
                    "supporting_clusters": ";".join(profiles),
                    "supporting_role_count": int(sizes.sum()),
                    "trait": trait,
                    "mean_within_model_z": float(value),
                    "evidence_role": "secondary same-activation-space description",
                })
    family_traits = pd.DataFrame(family_trait_rows)
    family_traits.to_csv(HERE / "consensus_family_trait_profiles.csv", index=False)

    family_trait_similarity = []
    for family, group in family_traits.groupby("consensus_family_id", sort=True):
        models = sorted(group.model.unique())
        for a, b in itertools.combinations(models, 2):
            va = group[group.model == a].sort_values("trait").mean_within_model_z.to_numpy()
            vb = group[group.model == b].sort_values("trait").mean_within_model_z.to_numpy()
            pearson, spearman, cosine = vector_similarity(va, vb)
            family_trait_similarity.append({
                "consensus_family_id": family, "model_a": a, "model_b": b,
                "pearson_240_traits": pearson, "spearman_240_traits": spearman,
                "centered_cosine_240_traits": cosine,
                "evidence_role": "secondary same-activation-space confirmation",
            })
    family_trait_similarity = pd.DataFrame(family_trait_similarity)
    family_trait_similarity.to_csv(HERE / "consensus_family_trait_similarity.csv", index=False)

    # Data-derived display: traits with largest between-family variance after averaging models.
    if not family_traits.empty:
        averaged = family_traits.groupby(["consensus_family_id", "trait"], as_index=False).mean_within_model_z.mean()
        matrix = averaged.pivot(index="consensus_family_id", columns="trait", values="mean_within_model_z").sort_index()
        variances = matrix.var(axis=0, ddof=0).sort_values(ascending=False)
        selected = sorted(variances.head(min(30, len(variances))).index, key=lambda t: (-variances[t], t))
        display = matrix[selected]
        fig, ax = plt.subplots(figsize=(15.5, max(4.8, .65 * len(display) + 2.8)))
        vmax = max(abs(display.to_numpy().min()), abs(display.to_numpy().max()))
        im = ax.imshow(display.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_xticks(range(len(selected)), selected, rotation=60, ha="right", fontsize=8)
        ax.set_yticks(range(len(display.index)), display.index)
        ax.set_title("Candidate consensus families: 30 most differentiating model-standardized traits")
        ax.set_xlabel("Trait (selected mechanically by between-family variance)")
        ax.set_ylabel("Candidate family")
        fig.colorbar(im, ax=ax, label="Mean within-model z-score across represented models")
        fig.tight_layout()
        fig.savefig(FIGURES / "consensus_family_trait_heatmap.png", dpi=180)
        plt.close(fig)

    majority_union = set()
    all_three_count = 0
    for c in accepted:
        majority_union.update(c["majority"])
        all_three_count += len(c["models"]) == 3
    search_p = float(partition["triple_search_adjusted_p"])
    established = search_p <= .05 and all_three_count >= 3 and len(majority_union) / N_ROLES >= .50
    status = "ESTABLISHED_CANDIDATE_SET" if established else "NOT ESTABLISHED"
    ambiguity = 0
    if not family_roles.empty:
        ambiguity = int(
            family_roles[family_roles.model_support_count >= 2]
            .groupby("opaque_role_id").consensus_family_id.nunique().gt(1).sum()
        )
    summary = {
        "status": status,
        "model_used": "GPT-5.5",
        "anchor": anchor,
        "construction_basis": "opaque shared-role overlap only; traits did not gate graph",
        "accepted_component_count": len(accepted),
        "three_model_family_count": all_three_count,
        "majority_role_union_count": len(majority_union),
        "majority_role_inventory_fraction": len(majority_union) / N_ROLES,
        "ambiguous_majority_role_count": ambiguity,
        "search_adjusted_triple_p": search_p,
        "cluster_trait_edge_count": len(trait_similarity),
        "trait_provenance_warning": "The 240 traits share activation provenance with the role vectors and are secondary, not independent validation.",
    }
    (HERE / "consensus_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
