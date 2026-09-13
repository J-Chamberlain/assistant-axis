#!/usr/bin/env python3
"""Frozen phase-3 cluster overlap, persistence, and tiny-cluster audit.

This program uses only opaque role IDs and previously frozen memberships. It does
not read role names, traits, human data, or SAPA artifacts.
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
from scipy.stats import hypergeom


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "research/outputs/cross_resolution_profile_banks/model"
FIGURES = HERE / "figures"
MODELS = ("qwen", "llama", "gemma")
MODEL_LABELS = {"qwen": "Qwen", "llama": "LLaMA", "gemma": "Gemma"}
MODEL_PAIRS = (("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma"))
KS = tuple(range(4, 11))
N_ROLES = 275
TINY_SIZE = 4


def bh_adjust(pvalues: np.ndarray) -> np.ndarray:
    pvalues = np.asarray(pvalues, dtype=float)
    order = np.argsort(pvalues, kind="mergesort")
    ranked = pvalues[order]
    adjusted = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    out = np.empty_like(adjusted)
    out[order] = np.minimum(adjusted, 1.0)
    return out


def is_strong(row) -> bool:
    regular = (
        row.intersection_count >= 3
        and (row.jaccard >= 0.30 - 1e-12 or row.overlap_coefficient >= 0.65 - 1e-12)
    )
    tiny = (
        min(row.size_a, row.size_b) <= TINY_SIZE
        and row.intersection_count >= 2
        and row.overlap_coefficient >= (2.0 / 3.0) - 1e-12
    )
    return bool(row.hypergeom_q <= 0.01 + 1e-15 and (regular or tiny))


def load_memberships():
    frames = {}
    sets = {}
    labels = {}
    common = None
    for model in MODELS:
        df = pd.read_csv(SOURCE / model / "memberships.csv")
        frames[model] = df
        this = set(df.opaque_role_id)
        if common is None:
            common = this
        elif this != common:
            raise RuntimeError("Role inventories differ")
        sets[model] = {}
        labels[model] = {}
        for k in KS:
            sub = df[df.K == k]
            if len(sub) != N_ROLES or sub.opaque_role_id.nunique() != N_ROLES:
                raise RuntimeError(f"Invalid membership inventory {model} K={k}")
            labels[model][k] = dict(zip(sub.opaque_role_id, sub.profile_id))
            sets[model][k] = {
                profile: frozenset(group.opaque_role_id)
                for profile, group in sub.groupby("profile_id", sort=True)
            }
    return frames, sets, labels


def overlap_record(a: str, b: str, ka: int, kb: int, pa: str, pb: str, sa: frozenset, sb: frozenset):
    inter = len(sa & sb)
    union = len(sa | sb)
    size_a, size_b = len(sa), len(sb)
    return {
        "model_a": a,
        "model_b": b,
        "K_a": ka,
        "K_b": kb,
        "profile_a": pa,
        "profile_b": pb,
        "size_a": size_a,
        "size_b": size_b,
        "intersection_count": inter,
        "union_count": union,
        "jaccard": inter / union,
        "overlap_coefficient": inter / min(size_a, size_b),
        "p_b_given_a": inter / size_a,
        "p_a_given_b": inter / size_b,
        "expected_overlap": size_a * size_b / N_ROLES,
        "enrichment_ratio": inter / (size_a * size_b / N_ROLES) if inter else 0.0,
        "hypergeom_p": float(hypergeom.sf(inter - 1, N_ROLES, size_a, size_b)),
    }


def nearest_profile(target: frozenset, candidates: dict[str, frozenset]) -> str:
    rows = []
    for profile, roles in candidates.items():
        inter = len(target & roles)
        rows.append((-(inter / len(target | roles)), -(inter / min(len(target), len(roles))), -inter, profile))
    rows.sort()
    return rows[0][3]


def plot_anchor_overlap(overlaps: pd.DataFrame, a: str, b: str, ka: int, kb: int):
    sub = overlaps[
        (overlaps.model_a == a) & (overlaps.model_b == b) & (overlaps.K_a == ka) & (overlaps.K_b == kb)
    ]
    matrix = sub.pivot(index="profile_a", columns="profile_b", values="jaccard")
    counts = sub.pivot(index="profile_a", columns="profile_b", values="intersection_count")
    matrix = matrix.sort_index().sort_index(axis=1)
    counts = counts.loc[matrix.index, matrix.columns]
    fig, ax = plt.subplots(figsize=(max(6.2, 0.75 * len(matrix.columns) + 2.7), max(5.2, 0.65 * len(matrix.index) + 2.3)))
    im = ax.imshow(matrix.to_numpy(), cmap="magma", vmin=0, vmax=max(0.7, matrix.to_numpy().max()), aspect="auto")
    ax.set_xticks(range(len(matrix.columns)), matrix.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    ax.set_xlabel(f"{MODEL_LABELS[b]} clusters")
    ax.set_ylabel(f"{MODEL_LABELS[a]} clusters")
    ax.set_title(f"Role-overlap Jaccard: {MODEL_LABELS[a]} K={ka} × {MODEL_LABELS[b]} K={kb}")
    for i in range(len(matrix.index)):
        for j in range(len(matrix.columns)):
            ax.text(j, i, f"{matrix.iloc[i,j]:.2f}\n(n={int(counts.iloc[i,j])})", ha="center", va="center", fontsize=7,
                    color="white" if matrix.iloc[i,j] > 0.30 else "black")
    fig.colorbar(im, ax=ax, label="Jaccard similarity")
    fig.tight_layout()
    fig.savefig(FIGURES / f"anchor_{a}_{b}_cluster_overlap.png", dpi=180)
    plt.close(fig)


def plot_anchor_graph(edges: pd.DataFrame, anchor: dict[str, int], sets):
    subparts = []
    for a, b in MODEL_PAIRS:
        ka, kb = anchor[a], anchor[b]
        subparts.append(edges[(edges.model_a == a) & (edges.model_b == b) & (edges.K_a == ka) & (edges.K_b == kb)])
    sub = pd.concat(subparts, ignore_index=True) if subparts else pd.DataFrame()
    graph = nx.Graph()
    positions = {}
    colors = {"qwen": "#4C78A8", "llama": "#F58518", "gemma": "#54A24B"}
    for x, model in enumerate(MODELS):
        profiles = sorted(sets[model][anchor[model]])
        for i, profile in enumerate(profiles):
            graph.add_node(profile, model=model)
            positions[profile] = (x, (i + 1) / (len(profiles) + 1))
    for r in sub.itertuples(index=False):
        graph.add_edge(r.profile_a, r.profile_b, weight=r.jaccard, tier=r.persistence_tier)
    fig, ax = plt.subplots(figsize=(10.5, 7.0))
    for model in MODELS:
        nodes = [n for n, d in graph.nodes(data=True) if d["model"] == model]
        nx.draw_networkx_nodes(graph, positions, nodelist=nodes, node_color=colors[model], node_size=1050, ax=ax)
    high = [(u, v) for u, v, d in graph.edges(data=True) if d["tier"] == "high"]
    moderate = [(u, v) for u, v, d in graph.edges(data=True) if d["tier"] == "moderate"]
    isolated = [(u, v) for u, v, d in graph.edges(data=True) if d["tier"] == "isolated"]
    for edgelist, style, alpha in [(high, "solid", .9), (moderate, "dashed", .75), (isolated, "dotted", .35)]:
        nx.draw_networkx_edges(
            graph, positions, edgelist=edgelist,
            width=[1.0 + 6.0 * graph.edges[e]["weight"] for e in edgelist],
            style=style, alpha=alpha, edge_color="#555555", ax=ax,
        )
    nx.draw_networkx_labels(graph, positions, font_size=8, font_color="white", ax=ax)
    for x, model in enumerate(MODELS):
        ax.text(x, 1.05, f"{MODEL_LABELS[model]} K={anchor[model]}", ha="center", va="bottom", fontsize=12, weight="bold")
    ax.set_title("Strong shared-role correspondences at the frozen consensus anchor\n(edge width = Jaccard; line style = resolution persistence)")
    ax.set_xlim(-0.35, 2.35); ax.set_ylim(-0.03, 1.13); ax.axis("off")
    fig.tight_layout()
    fig.savefig(FIGURES / "anchor_cluster_correspondence_graph.png", dpi=180)
    plt.close(fig)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    _, sets, _ = load_memberships()
    partition_summary = json.loads((HERE / "partition_agreement_summary.json").read_text())
    anchor = {
        "qwen": int(partition_summary["consensus_anchor_triple"]["K_qwen"]),
        "llama": int(partition_summary["consensus_anchor_triple"]["K_llama"]),
        "gemma": int(partition_summary["consensus_anchor_triple"]["K_gemma"]),
    }

    records = []
    for a, b in MODEL_PAIRS:
        for ka, kb in itertools.product(KS, KS):
            for pa, sa in sets[a][ka].items():
                for pb, sb in sets[b][kb].items():
                    records.append(overlap_record(a, b, ka, kb, pa, pb, sa, sb))
    overlaps = pd.DataFrame(records)
    overlaps["hypergeom_q"] = np.nan
    for _, idx in overlaps.groupby(["model_a", "model_b", "K_a", "K_b"], sort=False).groups.items():
        overlaps.loc[idx, "hypergeom_q"] = bh_adjust(overlaps.loc[idx, "hypergeom_p"].to_numpy())
    overlaps["strong_edge"] = [is_strong(r) for r in overlaps.itertuples(index=False)]
    overlaps = overlaps.sort_values(["model_a", "model_b", "K_a", "K_b", "profile_a", "profile_b"])
    overlaps.to_csv(HERE / "cluster_overlap_matrices.csv", index=False)

    lookup = {
        (r.model_a, r.model_b, int(r.K_a), int(r.K_b), r.profile_a, r.profile_b): r
        for r in overlaps.itertuples(index=False)
    }
    persistence_rows = []
    strong = overlaps[overlaps.strong_edge].copy()
    for edge in strong.itertuples(index=False):
        original_a = sets[edge.model_a][edge.K_a][edge.profile_a]
        original_b = sets[edge.model_b][edge.K_b][edge.profile_b]
        neighborhood = []
        for nka in [k for k in KS if abs(k - edge.K_a) <= 1]:
            traced_a = nearest_profile(original_a, sets[edge.model_a][nka])
            for nkb in [k for k in KS if abs(k - edge.K_b) <= 1]:
                traced_b = nearest_profile(original_b, sets[edge.model_b][nkb])
                found = lookup[(edge.model_a, edge.model_b, nka, nkb, traced_a, traced_b)]
                neighborhood.append((nka, nkb, traced_a, traced_b, bool(found.strong_edge)))
        support_count = sum(x[4] for x in neighborhood)
        score = support_count / len(neighborhood)
        if len(neighborhood) >= 4 and score >= .75 - 1e-12:
            tier = "high"
        elif len(neighborhood) >= 4 and score >= .50 - 1e-12:
            tier = "moderate"
        else:
            tier = "isolated"
        persistence_rows.append({
            "model_a": edge.model_a, "model_b": edge.model_b,
            "K_a": edge.K_a, "K_b": edge.K_b,
            "profile_a": edge.profile_a, "profile_b": edge.profile_b,
            "valid_neighborhood_cells": len(neighborhood),
            "supported_neighborhood_cells": support_count,
            "persistence_score": score,
            "persistence_tier": tier,
            "neighborhood_trace": ";".join(
                f"{ka},{kb},{pa},{pb},{int(ok)}" for ka, kb, pa, pb, ok in neighborhood
            ),
        })
    persistence = pd.DataFrame(persistence_rows).sort_values(
        ["model_a", "model_b", "K_a", "K_b", "profile_a", "profile_b"]
    )
    persistence.to_csv(HERE / "cross_resolution_persistence.csv", index=False)
    edges = strong.merge(
        persistence,
        on=["model_a", "model_b", "K_a", "K_b", "profile_a", "profile_b"],
        how="left",
    )
    edges.to_csv(HERE / "cluster_overlap_edges.csv", index=False)

    tiny_rows = []
    for model in MODELS:
        for k in KS:
            for profile, tiny_roles in sets[model][k].items():
                if len(tiny_roles) > TINY_SIZE:
                    continue
                parent = None
                for lower_k in [x for x in KS if x < k]:
                    for lower_profile, lower_roles in sets[model][lower_k].items():
                        inter = len(tiny_roles & lower_roles)
                        candidate = {
                            "lower_K": lower_k,
                            "profile": lower_profile,
                            "retained": inter / len(tiny_roles),
                            "jaccard": inter / len(tiny_roles | lower_roles),
                            "intersection": inter,
                        }
                        key = (-candidate["retained"], -candidate["jaccard"], -candidate["lower_K"], candidate["profile"])
                        if parent is None or key < parent[0]:
                            parent = (key, candidate)
                for target in [m for m in MODELS if m != model]:
                    per_k_best = []
                    for tk in KS:
                        candidates = []
                        for tp, target_roles in sets[target][tk].items():
                            inter = len(tiny_roles & target_roles)
                            candidates.append({
                                "target_K": tk,
                                "target_profile": tp,
                                "target_size": len(target_roles),
                                "intersection_count": inter,
                                "tiny_role_retention": inter / len(tiny_roles),
                                "jaccard": inter / len(tiny_roles | target_roles),
                                "overlap_coefficient": inter / min(len(tiny_roles), len(target_roles)),
                            })
                        candidates.sort(key=lambda x: (-x["tiny_role_retention"], -x["jaccard"], -x["intersection_count"], x["target_profile"]))
                        per_k_best.append(candidates[0])
                    per_k_best.sort(key=lambda x: (-x["tiny_role_retention"], -x["jaccard"], -x["intersection_count"], x["target_K"], x["target_profile"]))
                    best_signature = (per_k_best[0]["tiny_role_retention"], per_k_best[0]["jaccard"], per_k_best[0]["intersection_count"])
                    for candidate in sorted(per_k_best, key=lambda x: (x["target_K"], x["target_profile"])):
                        tiny_rows.append({
                            "model": model, "K": k, "profile_id": profile,
                            "size": len(tiny_roles),
                            "opaque_role_ids": ";".join(sorted(tiny_roles)),
                            "target_model": target,
                            **candidate,
                            "global_best_for_target_model": (
                                candidate["tiny_role_retention"], candidate["jaccard"], candidate["intersection_count"]
                            ) == best_signature,
                            "nearest_lower_K": parent[1]["lower_K"] if parent else None,
                            "nearest_lower_profile": parent[1]["profile"] if parent else None,
                            "parent_tiny_role_retention": parent[1]["retained"] if parent else None,
                            "parent_jaccard": parent[1]["jaccard"] if parent else None,
                        })
    tiny = pd.DataFrame(tiny_rows).sort_values(["model", "K", "profile_id", "target_model", "target_K"])
    tiny.to_csv(HERE / "tiny_cluster_audit_opaque.csv", index=False)

    for a, b in MODEL_PAIRS:
        plot_anchor_overlap(overlaps, a, b, anchor[a], anchor[b])
    plot_anchor_graph(edges, anchor, sets)

    # Numeric tiny-cluster overview: best recovery in each other model.
    best_tiny = tiny[tiny.global_best_for_target_model].copy()
    clusters = sorted(best_tiny.apply(lambda r: f"{r.profile_id}", axis=1).unique())
    targets = [f"{m}→{t}" for m in MODELS for t in MODELS if m != t]
    matrix = np.full((len(clusters), len(targets)), np.nan)
    for r in best_tiny.itertuples(index=False):
        matrix[clusters.index(r.profile_id), targets.index(f"{r.model}→{r.target_model}")] = r.tiny_role_retention
    fig, ax = plt.subplots(figsize=(10.5, max(5.0, .35 * len(clusters) + 2.5)))
    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(targets)), targets, rotation=45, ha="right")
    ax.set_yticks(range(len(clusters)), clusters)
    ax.set_title("Best cross-model retention of each <5-role cluster (opaque numerical audit)")
    for i in range(len(clusters)):
        for j in range(len(targets)):
            if np.isfinite(matrix[i,j]): ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax, label="Fraction of tiny-cluster roles retained")
    fig.tight_layout()
    fig.savefig(FIGURES / "tiny_cluster_membership_comparison.png", dpi=180)
    plt.close(fig)

    anchor_edges = edges[
        ((edges.model_a == "qwen") & (edges.model_b == "llama") & (edges.K_a == anchor["qwen"]) & (edges.K_b == anchor["llama"]))
        | ((edges.model_a == "qwen") & (edges.model_b == "gemma") & (edges.K_a == anchor["qwen"]) & (edges.K_b == anchor["gemma"]))
        | ((edges.model_a == "llama") & (edges.model_b == "gemma") & (edges.K_a == anchor["llama"]) & (edges.K_b == anchor["gemma"]))
    ]
    summary = {
        "status": "CLUSTER CORRESPONDENCE NUMERICALLY FROZEN; OPAQUE ROLE IDS ONLY",
        "role_count": N_ROLES,
        "all_cluster_pair_rows": int(len(overlaps)),
        "strong_edge_count": int(len(edges)),
        "persistence_tiers": {k: int(v) for k, v in persistence.persistence_tier.value_counts().to_dict().items()},
        "tiny_cluster_count": int(tiny[["model", "K", "profile_id"]].drop_duplicates().shape[0]),
        "anchor": anchor,
        "anchor_strong_edge_count": int(len(anchor_edges)),
        "anchor_persistence_tiers": {k: int(v) for k, v in anchor_edges.persistence_tier.value_counts().to_dict().items()},
        "boundary": "Role names, traits, human data, and SAPA artifacts were not loaded.",
    }
    (HERE / "cluster_correspondence_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
