#!/usr/bin/env python3
"""Post-freeze role-name joins and deterministic trait browsing tables."""

from __future__ import annotations

from pathlib import Path
import json

import pandas as pd


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "research/outputs/cross_resolution_profile_banks/model"
MODELS = ("qwen", "llama", "gemma")


def main() -> None:
    role_maps = {}
    membership_sets = {}
    for model in MODELS:
        named = pd.read_csv(SOURCE / model / "memberships_with_role_names.csv")
        role_maps[model] = dict(zip(named.opaque_role_id, named.role))
        membership_sets[model] = {
            (int(k), profile): frozenset(group.opaque_role_id)
            for (k, profile), group in named.groupby(["K", "profile_id"], sort=True)
        }
    if not (role_maps["qwen"] == role_maps["llama"] == role_maps["gemma"]):
        raise RuntimeError("Opaque-to-semantic role maps differ")
    names = role_maps["qwen"]

    roles = pd.read_csv(HERE / "consensus_family_roles_opaque.csv")
    roles.insert(2, "role", roles.opaque_role_id.map(names))
    if roles.role.isna().any():
        raise RuntimeError("Missing role name")
    roles.to_csv(HERE / "consensus_family_roles.csv", index=False)

    tiny = pd.read_csv(HERE / "tiny_cluster_audit_opaque.csv")
    source_names, overlap_names, extra_names = [], [], []
    for row in tiny.itertuples(index=False):
        source = set(str(row.opaque_role_ids).split(";"))
        target = set(membership_sets[row.target_model][(int(row.target_K), row.target_profile)])
        source_names.append(";".join(names[x] for x in sorted(source)))
        overlap_names.append(";".join(names[x] for x in sorted(source & target)))
        extra_names.append(";".join(names[x] for x in sorted(target - source)))
    tiny.insert(tiny.columns.get_loc("target_model"), "role_names", source_names)
    tiny["target_overlap_role_names"] = overlap_names
    tiny["target_extra_role_names"] = extra_names
    tiny.to_csv(HERE / "tiny_cluster_audit.csv", index=False)

    family_traits = pd.read_csv(HERE / "consensus_family_trait_profiles.csv")
    rows = []
    for family, group in family_traits.groupby("consensus_family_id", sort=True):
        matrix = group.pivot(index="model", columns="trait", values="mean_within_model_z")
        stats = pd.DataFrame({
            "trait": matrix.columns,
            "cross_model_mean_z": matrix.mean(axis=0).to_numpy(),
            "minimum_model_z": matrix.min(axis=0).to_numpy(),
            "maximum_model_z": matrix.max(axis=0).to_numpy(),
            "cross_model_sd": matrix.std(axis=0, ddof=0).to_numpy(),
            "models_represented": len(matrix.index),
        })
        selections = [
            ("elevated", stats.sort_values(["cross_model_mean_z", "trait"], ascending=[False, True]).head(10)),
            ("depressed", stats.sort_values(["cross_model_mean_z", "trait"], ascending=[True, True]).head(10)),
            ("disagreement", stats.sort_values(["cross_model_sd", "trait"], ascending=[False, True]).head(10)),
        ]
        for kind, selected in selections:
            for rank, record in enumerate(selected.itertuples(index=False), 1):
                rows.append({
                    "consensus_family_id": family,
                    "selection": kind,
                    "rank": rank,
                    **record._asdict(),
                })
    pd.DataFrame(rows).to_csv(HERE / "consensus_family_trait_summary.csv", index=False)

    partition = json.loads((HERE / "partition_agreement_summary.json").read_text())
    anchor = {
        "qwen": int(partition["consensus_anchor_triple"]["K_qwen"]),
        "llama": int(partition["consensus_anchor_triple"]["K_llama"]),
        "gemma": int(partition["consensus_anchor_triple"]["K_gemma"]),
    }
    edges = pd.read_csv(HERE / "cluster_overlap_edges.csv")
    parts = []
    for a, b in [("qwen", "llama"), ("qwen", "gemma"), ("llama", "gemma")]:
        sub = edges[
            (edges.model_a == a) & (edges.model_b == b)
            & (edges.K_a == anchor[a]) & (edges.K_b == anchor[b])
            & edges.persistence_tier.isin(["high", "moderate"])
        ].copy()
        degree_a = sub.groupby("profile_a").size().to_dict()
        degree_b = sub.groupby("profile_b").size().to_dict()
        sub["profile_a_persistent_degree"] = sub.profile_a.map(degree_a)
        sub["profile_b_persistent_degree"] = sub.profile_b.map(degree_b)
        sub["split_merge_pattern"] = [
            "many_to_many" if degree_a[pa] > 1 and degree_b[pb] > 1
            else "one_to_many" if degree_a[pa] > 1
            else "many_to_one" if degree_b[pb] > 1
            else "one_to_one"
            for pa, pb in zip(sub.profile_a, sub.profile_b)
        ]
        parts.append(sub)
    pd.concat(parts, ignore_index=True).to_csv(HERE / "anchor_split_merge_patterns.csv", index=False)

    print({
        "consensus_role_rows": len(roles),
        "tiny_audit_rows": len(tiny),
        "trait_summary_rows": len(rows),
        "split_merge_edge_rows": sum(len(x) for x in parts),
        "role_map_count": len(names),
    })


if __name__ == "__main__":
    main()
