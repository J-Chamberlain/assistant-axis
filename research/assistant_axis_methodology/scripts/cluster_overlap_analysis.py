#!/usr/bin/env python3
"""Structured overlap analysis for activation and semantic prompt clusters.

This script uses already-generated artifacts. It does not recompute embeddings,
run model inference, generate activations, or call external APIs.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ASSIGNMENTS = (
    ROOT
    / "research/assistant_axis_methodology/semantic_vs_activation_geometry/cluster_assignments_comparison.csv"
)
DEEP_JSON = ROOT / "research/assistant_axis_methodology/deep_semantic_topology_analysis.json"
PRIOR_SUMMARY = (
    ROOT
    / "research/assistant_axis_methodology/semantic_vs_activation_geometry/semantic_vs_activation_geometry_summary.json"
)
BRIDGE_SOURCE = ROOT / "research/assistant_axis_methodology/semantic_bridge_roles.csv"
OUT_MD = ROOT / "research/assistant_axis_methodology/cluster_overlap_analysis.md"
OUT_NOTE = ROOT / "research/assistant_axis_methodology/cluster_overlap_interpretation_note.md"
OUT_JSON = ROOT / "research/assistant_axis_methodology/cluster_overlap_analysis.json"
OVERLAP_CSV = ROOT / "research/assistant_axis_methodology/activation_cluster_semantic_overlap.csv"
VENN_CSV = ROOT / "research/assistant_axis_methodology/semantic_vs_activation_venn_tables.csv"
ANCHORS_CSV = ROOT / "research/assistant_axis_methodology/stable_anchor_roles.csv"
BRIDGES_CSV = ROOT / "research/assistant_axis_methodology/bridge_roles.csv"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def containment(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a) if a else 0.0


def overlap_rows(rows: list[dict[str, str]], k: int) -> list[dict]:
    role_set_by_activation: dict[str, set[str]] = defaultdict(set)
    role_set_by_orig: dict[str, set[str]] = defaultdict(set)
    role_set_by_nolabel: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        role = row["role"]
        role_set_by_activation[row["activation_cluster"]].add(role)
        role_set_by_orig[row[f"original_prompt_k{k}"]].add(role)
        role_set_by_nolabel[row[f"no_label_prompt_k{k}"]].add(role)

    out = []
    for activation, act_roles in sorted(role_set_by_activation.items()):
        for semantic_type, semantic_sets in [
            ("original_prompt", role_set_by_orig),
            ("no_label_prompt", role_set_by_nolabel),
        ]:
            for sem_cluster, sem_roles in sorted(semantic_sets.items(), key=lambda kv: int(kv[0])):
                shared = act_roles & sem_roles
                if not shared:
                    continue
                out.append(
                    {
                        "k": k,
                        "activation_cluster": activation,
                        "semantic_type": semantic_type,
                        "semantic_cluster": sem_cluster,
                        "activation_n": len(act_roles),
                        "semantic_n": len(sem_roles),
                        "intersection_n": len(shared),
                        "jaccard": jaccard(act_roles, sem_roles),
                        "activation_containment": containment(act_roles, sem_roles),
                        "semantic_containment": containment(sem_roles, act_roles),
                        "shared_roles": sorted(shared),
                    }
                )
    return sorted(
        out,
        key=lambda r: (r["k"], r["activation_cluster"], r["semantic_type"], -r["intersection_n"]),
    )


def dominant_maps(overlaps: list[dict], k: int, semantic_type: str) -> dict[str, dict]:
    candidates = [
        r for r in overlaps if r["k"] == k and r["semantic_type"] == semantic_type
    ]
    by_activation: dict[str, list[dict]] = defaultdict(list)
    for row in candidates:
        by_activation[row["activation_cluster"]].append(row)
    out = {}
    for activation, rows in by_activation.items():
        out[activation] = sorted(
            rows,
            key=lambda r: (
                -r["activation_containment"],
                -r["intersection_n"],
                -r["jaccard"],
            ),
        )[0]
    return out


def stable_anchor_roles(rows: list[dict[str, str]], overlaps: list[dict]) -> list[dict]:
    orig_dom = dominant_maps(overlaps, 7, "original_prompt")
    nl_dom = dominant_maps(overlaps, 7, "no_label_prompt")
    out = []
    for row in rows:
        activation = row["activation_cluster"]
        orig = orig_dom[activation]["semantic_cluster"]
        nl = nl_dom[activation]["semantic_cluster"]
        stable = (
            row["original_prompt_k7"] == orig and row["no_label_prompt_k7"] == nl
        )
        if stable:
            out.append(
                {
                    "role": row["role"],
                    "activation_cluster": activation,
                    "dominant_original_cluster": orig,
                    "dominant_no_label_cluster": nl,
                    "original_prompt_k7": row["original_prompt_k7"],
                    "no_label_prompt_k7": row["no_label_prompt_k7"],
                }
            )
    return sorted(out, key=lambda r: (r["activation_cluster"], r["role"]))


def bridge_roles(rows: list[dict[str, str]], overlaps: list[dict]) -> list[dict]:
    orig_dom = dominant_maps(overlaps, 7, "original_prompt")
    nl_dom = dominant_maps(overlaps, 7, "no_label_prompt")
    bridge_source = {r["role"]: r for r in load_csv(BRIDGE_SOURCE)} if BRIDGE_SOURCE.exists() else {}
    out = []
    for row in rows:
        activation = row["activation_cluster"]
        orig_dominant = orig_dom[activation]["semantic_cluster"]
        nl_dominant = nl_dom[activation]["semantic_cluster"]
        orig_migrates = row["original_prompt_k7"] != orig_dominant
        nl_migrates = row["no_label_prompt_k7"] != nl_dominant
        label_changes = row["original_prompt_k7"] != row["no_label_prompt_k7"]
        bridge = bridge_source.get(row["role"], {})
        bridge_margin = float(bridge.get("cluster_margin", "999") or 999)
        cross_neighbors = int(float(bridge.get("cross_cluster_neighbors_top8", 0) or 0))
        score = (
            int(orig_migrates)
            + int(nl_migrates)
            + int(label_changes)
            + (1 if bridge_margin < 0.05 else 0)
            + (1 if cross_neighbors >= 5 else 0)
        )
        if score >= 2:
            out.append(
                {
                    "role": row["role"],
                    "activation_cluster": activation,
                    "original_prompt_k7": row["original_prompt_k7"],
                    "dominant_original_cluster_for_activation": orig_dominant,
                    "no_label_prompt_k7": row["no_label_prompt_k7"],
                    "dominant_no_label_cluster_for_activation": nl_dominant,
                    "original_migrates_from_activation_dominant": orig_migrates,
                    "no_label_migrates_from_activation_dominant": nl_migrates,
                    "original_to_no_label_cluster_changed": label_changes,
                    "semantic_bridge_margin": "" if bridge_margin == 999 else bridge_margin,
                    "cross_cluster_neighbors_top8": cross_neighbors,
                    "bridge_score": score,
                }
            )
    return sorted(out, key=lambda r: (-r["bridge_score"], r["activation_cluster"], r["role"]))


def triple_intersections(rows: list[dict[str, str]], k: int) -> list[dict]:
    out = []
    activations = sorted({r["activation_cluster"] for r in rows})
    original_clusters = sorted({r[f"original_prompt_k{k}"] for r in rows}, key=int)
    nolabel_clusters = sorted({r[f"no_label_prompt_k{k}"] for r in rows}, key=int)
    for activation in activations:
        act_roles = {r["role"] for r in rows if r["activation_cluster"] == activation}
        for orig in original_clusters:
            orig_roles = {r["role"] for r in rows if r[f"original_prompt_k{k}"] == orig}
            for nl in nolabel_clusters:
                nl_roles = {r["role"] for r in rows if r[f"no_label_prompt_k{k}"] == nl}
                shared = act_roles & orig_roles & nl_roles
                if len(shared) < 2:
                    continue
                out.append(
                    {
                        "k": k,
                        "activation_cluster": activation,
                        "original_prompt_cluster": orig,
                        "no_label_prompt_cluster": nl,
                        "intersection_n": len(shared),
                        "activation_containment": len(shared) / len(act_roles),
                        "roles": sorted(shared),
                    }
                )
    return sorted(out, key=lambda r: (-r["intersection_n"], r["activation_cluster"]))


def basin_analysis(rows: list[dict[str, str]], overlaps: list[dict], anchors: list[dict], bridges: list[dict]) -> dict:
    activation_to_roles = defaultdict(set)
    for row in rows:
        activation_to_roles[row["activation_cluster"]].add(row["role"])
    orig_dom = dominant_maps(overlaps, 7, "original_prompt")
    nl_dom = dominant_maps(overlaps, 7, "no_label_prompt")

    groups = {
        "assistant_adjacent_procedural": {"editorial", "procedural_professional"},
        "theatrical_fantastical": {"trickster_chaos", "mythic_spiritual"},
        "collective_swarm": {"mythic_spiritual", "procedural_professional"},
        "archetypal_social": {"grounded_social", "mythic_spiritual", "other"},
        "destabilizing_liminal": {"combative_iconoclast", "trickster_chaos", "other"},
    }
    collective_roles = {"hive", "swarm", "egregore", "ecosystem", "mycorrhizal", "coral_reef", "zeitgeist"}
    out = {}
    for name, activation_clusters in groups.items():
        roles_in_group = set().union(*(activation_to_roles[c] for c in activation_clusters if c in activation_to_roles))
        if name == "collective_swarm":
            roles_in_group = roles_in_group & collective_roles
        if not roles_in_group:
            continue
        anchor_roles = [a["role"] for a in anchors if a["role"] in roles_in_group]
        bridge_roles_in_group = [b["role"] for b in bridges if b["role"] in roles_in_group]
        sem_counts_orig = Counter(r["original_prompt_k7"] for r in rows if r["role"] in roles_in_group)
        sem_counts_nl = Counter(r["no_label_prompt_k7"] for r in rows if r["role"] in roles_in_group)
        dom_orig = sem_counts_orig.most_common(3)
        dom_nl = sem_counts_nl.most_common(3)
        out[name] = {
            "activation_clusters": sorted(activation_clusters),
            "n_roles": len(roles_in_group),
            "top_original_semantic_clusters": dom_orig,
            "top_no_label_semantic_clusters": dom_nl,
            "stable_anchor_count": len(anchor_roles),
            "stable_anchor_examples": sorted(anchor_roles)[:12],
            "bridge_count": len(bridge_roles_in_group),
            "bridge_examples": sorted(bridge_roles_in_group)[:12],
            "dominant_activation_cluster_maps": {
                c: {
                    "original": orig_dom[c]["semantic_cluster"] if c in orig_dom else None,
                    "no_label": nl_dom[c]["semantic_cluster"] if c in nl_dom else None,
                }
                for c in sorted(activation_clusters)
                if c in activation_to_roles
            },
        }
    return out


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            clean = {}
            for field in fields:
                val = row.get(field, "")
                if isinstance(val, list):
                    val = ", ".join(val)
                clean[field] = val
            writer.writerow(clean)


def make_report(summary: dict) -> str:
    lines = [
        "# Cluster Overlap Analysis",
        "",
        "## Research Question",
        "",
        "This overlap study compares Lu et al. activation-space clusters with original prompt semantic clusters and no-label prompt semantic clusters. It uses existing cluster assignments and prior semantic-analysis artifacts only. No embeddings, activations, pod inference, or rollout generation were run.",
        "",
        "## Data Sources",
        "",
        "- `research/assistant_axis_methodology/semantic_vs_activation_geometry/cluster_assignments_comparison.csv`",
        "- `research/assistant_axis_methodology/semantic_vs_activation_geometry/semantic_vs_activation_geometry_summary.json`",
        "- `research/assistant_axis_methodology/deep_semantic_topology_analysis.json`",
        "- `research/assistant_axis_methodology/semantic_bridge_roles.csv`",
        "",
        "## Headline Results",
        "",
        f"- Roles analyzed: {summary['n_roles']}",
        f"- k=7 original-prompt ARI vs activation labels: {summary['prior_metrics']['original_prompt_vs_activation_cluster_ari_k7']:.3f}",
        f"- k=7 no-label-prompt ARI vs activation labels: {summary['prior_metrics']['no_label_prompt_vs_activation_cluster_ari_k7']:.3f}",
        f"- Stable anchors across activation, original semantic, and no-label semantic dominant regions: {summary['stable_anchor_count']}",
        f"- Bridge or migratory roles flagged by overlap criteria: {summary['bridge_count']}",
        "",
        "## Activation Cluster Overlaps at k=7",
        "",
        "| Activation cluster | n | Dominant original semantic cluster | Original containment | Dominant no-label semantic cluster | No-label containment | Stable anchor examples |",
        "|---|---:|---|---:|---|---:|---|",
    ]
    for row in summary["activation_cluster_summary"]:
        anchors = ", ".join(f"`{r}`" for r in row["stable_anchor_examples"][:8])
        lines.append(
            f"| `{row['activation_cluster']}` | {row['activation_n']} | {row['dominant_original_cluster']} | {row['dominant_original_activation_containment']:.3f} | {row['dominant_no_label_cluster']} | {row['dominant_no_label_activation_containment']:.3f} | {anchors} |"
        )
    lines.extend(
        [
            "",
            "Containment is asymmetric: it measures how much of an activation cluster falls inside the dominant semantic cluster. Low containment does not mean no relationship; it often means the activation cluster spans several semantic regions.",
            "",
            "## Stable Basins",
            "",
            "| Basin | Activation clusters | n | Stable anchors | Bridge roles | Interpretation |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    interpretations = {
        "assistant_adjacent_procedural": "A broad professional/helper basin. Editorial is semantically compact, but procedural-professional spreads across several semantic clusters, consistent with activation-space compression of many task-oriented roles.",
        "theatrical_fantastical": "Semantic vividness survives label removal, but activation space separates playful/transgressive roles from broader mythic/fantastical roles more sharply than prompt taxonomy alone.",
        "collective_swarm": "Collective roles are compact in no-label prompt space, but activation labels distribute them across larger mythic/procedural regions, suggesting semantic coherence without a dedicated activation cluster in the available taxonomy.",
        "archetypal_social": "Social, survival, mythic, and residual roles form overlapping gradients rather than crisp partitions. This is the main site of semantic-to-activation reorganization.",
        "destabilizing_liminal": "Combative, playful, and residual roles contain many boundary cases. These are high-value probes for no-label activation tests because semantic ambiguity may be resolved or amplified in activations.",
    }
    for name, row in summary["basin_analysis"].items():
        lines.append(
            f"| `{name}` | {', '.join(f'`{x}`' for x in row['activation_clusters'])} | {row['n_roles']} | {row['stable_anchor_count']} | {row['bridge_count']} | {interpretations.get(name, '')} |"
        )
    lines.extend(
        [
            "",
            "## Stable Anchors",
            "",
            "Stable anchors are roles that sit inside the dominant original-prompt semantic cluster and the dominant no-label semantic cluster for their activation-space cluster. They are not guaranteed to be activation centroids, but they are robust overlap representatives.",
            "",
            "| Activation cluster | Anchor examples |",
            "|---|---|",
        ]
    )
    for cluster, roles in summary["stable_anchors_by_activation"].items():
        lines.append(f"| `{cluster}` | " + ", ".join(f"`{r}`" for r in roles[:15]) + " |")
    lines.extend(
        [
            "",
            "## Bridge and Migratory Roles",
            "",
            "Bridge roles either migrate between semantic and activation-dominant regions, change original-to-no-label semantic cluster, or have low semantic-cluster margin in the deep topology analysis.",
            "",
            "| Role | Activation cluster | Original k7 | No-label k7 | Bridge score | Notes |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in summary["top_bridge_roles"][:30]:
        notes = []
        if row["original_migrates_from_activation_dominant"]:
            notes.append("original outside activation-dominant semantic region")
        if row["no_label_migrates_from_activation_dominant"]:
            notes.append("no-label outside activation-dominant semantic region")
        if row["original_to_no_label_cluster_changed"]:
            notes.append("changes under label removal")
        if row["semantic_bridge_margin"] != "":
            notes.append(f"low margin {float(row['semantic_bridge_margin']):.3f}")
        lines.append(
            f"| `{row['role']}` | `{row['activation_cluster']}` | {row['original_prompt_k7']} | {row['no_label_prompt_k7']} | {row['bridge_score']} | {'; '.join(notes)} |"
        )
    lines.extend(
        [
            "",
            "## Focused Boundary-Role Checks",
            "",
            "The user-requested boundary roles are mixed rather than uniformly migratory. Some stay inside the activation-dominant semantic region, while others move across semantic partitions or sit near low-margin boundaries.",
            "",
            "| Role | Activation cluster | Original k7 | No-label k7 | Bridge score | Interpretation |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in summary["focused_roles"]:
        lines.append(
            f"| `{row['role']}` | `{row['activation_cluster']}` | {row['original_prompt_k7']} | {row['no_label_prompt_k7']} | {row['bridge_score']} | {row['interpretation']} |"
        )
    if summary["missing_focused_roles"]:
        lines.append("")
        lines.append(
            "Focused roles not present in the 275-role assignment table: "
            + ", ".join(f"`{role}`" for role in summary["missing_focused_roles"])
            + "."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The strongest overlap is local rather than global. Editorial roles form a compact semantic and activation grouping; combative and trickster-like roles retain recognizable semantic structure; and professional/helper roles occupy a large region that activation space compresses into a broad procedural-professional basin. The weaker overlaps occur in large heterogeneous clusters where prompt semantics split the roles by genre, life situation, or communicative form while activation labels group them by broader enacted behavioral stance.",
            "",
            "Activation-space clusters appear sharper in narrow basins and more compressed in broad basins. Editorial is the clearest case of a semantic structure that survives cleanly. Procedural-professional is the clearest case of compression: multiple semantic clusters of expertise, writing/media, evaluation, coordination, and technical problem solving map into one large activation cluster. Mythic-spiritual and grounded-social show reorganization rather than clean preservation, with survival, social-position, symbolic, and nonordinary roles crossing semantic boundaries.",
            "",
            "The overlap pattern supports the view that activation geometry is not reducible to lexical semantics. Prompt-space semantics provide priors and local neighborhoods, but activation labels reorganize those neighborhoods around procedural/behavioral coherence. This is a limited claim: the analysis does not prove causality, and it does not replace activation-space no-label stress tests.",
            "",
            "## Strongest Findings",
            "",
            "- Semantic and activation clusters overlap partially, with stable local anchors but low global hard-cluster agreement.",
            "- Editorial is the most stable activation-semantic overlap region.",
            "- Procedural-professional compresses several semantic regions into one broad activation basin.",
            "- Collective/swarm roles are semantically compact but do not form a dedicated activation cluster in the available labels.",
            "- Bridge roles provide a targeted set for no-label activation stress testing.",
            "",
            "## Speculative Findings",
            "",
            "- Activation geometry may encode enacted behavioral stance more strongly than prompt-space semantic taxonomy alone.",
            "- Theatrical roles may become more separable in activation space when their behavioral stance is distinct from generic assistant behavior.",
            "- Assistant-adjacent roles may compress into the default assistant/procedural basin even when their prompt semantics are explicit.",
            "",
            "## Recommended Next Experiment",
            "",
            "Run a small no-label activation-space stress test that samples stable anchors, bridge roles, sparse/outlier roles, assistant-adjacent roles, and theatrical roles. The purpose should be to test whether no-label prompts still recover Lu reference directions and whether bridge roles snap into activation basins or remain unstable.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = load_csv(ASSIGNMENTS)
    prior = json.loads(PRIOR_SUMMARY.read_text())
    deep = json.loads(DEEP_JSON.read_text())
    all_overlaps = []
    for k in (5, 7, 10):
        all_overlaps.extend(overlap_rows(rows, k))

    anchors = stable_anchor_roles(rows, all_overlaps)
    bridges = bridge_roles(rows, all_overlaps)
    triples = []
    for k in (5, 7, 10):
        triples.extend(triple_intersections(rows, k))
    basins = basin_analysis(rows, all_overlaps, anchors, bridges)
    bridge_by_role = {row["role"]: row for row in bridges}
    focused_names = [
        "diplomat",
        "skeptic",
        "philosopher",
        "strategist",
        "observer",
        "mediator",
        "negotiator",
        "editor",
        "reviewer",
        "consultant",
    ]
    focused_roles = []
    missing_focused_roles = []
    rows_by_role = {row["role"]: row for row in rows}
    for role in focused_names:
        if role not in rows_by_role:
            missing_focused_roles.append(role)
            continue
        row = rows_by_role[role]
        bridge = bridge_by_role.get(role)
        score = bridge["bridge_score"] if bridge else 0
        if not bridge:
            interp = "stable enough under overlap criteria; not flagged as a major bridge role"
        elif int(score) >= 4:
            interp = "strong migratory/boundary case under overlap criteria"
        else:
            interp = "moderate boundary case; semantic grouping differs from at least one activation-dominant region"
        focused_roles.append(
            {
                "role": role,
                "activation_cluster": row["activation_cluster"],
                "original_prompt_k7": row["original_prompt_k7"],
                "no_label_prompt_k7": row["no_label_prompt_k7"],
                "bridge_score": score,
                "interpretation": interp,
            }
        )

    orig_dom = dominant_maps(all_overlaps, 7, "original_prompt")
    nl_dom = dominant_maps(all_overlaps, 7, "no_label_prompt")
    activation_counts = Counter(r["activation_cluster"] for r in rows)
    anchors_by_activation = defaultdict(list)
    for row in anchors:
        anchors_by_activation[row["activation_cluster"]].append(row["role"])

    activation_summary = []
    for cluster in sorted(activation_counts):
        activation_summary.append(
            {
                "activation_cluster": cluster,
                "activation_n": activation_counts[cluster],
                "dominant_original_cluster": orig_dom[cluster]["semantic_cluster"],
                "dominant_original_intersection_n": orig_dom[cluster]["intersection_n"],
                "dominant_original_activation_containment": orig_dom[cluster][
                    "activation_containment"
                ],
                "dominant_no_label_cluster": nl_dom[cluster]["semantic_cluster"],
                "dominant_no_label_intersection_n": nl_dom[cluster]["intersection_n"],
                "dominant_no_label_activation_containment": nl_dom[cluster][
                    "activation_containment"
                ],
                "stable_anchor_examples": anchors_by_activation[cluster][:12],
            }
        )

    summary = {
        "date": "2026-05-27",
        "model_used": "GPT-5.5",
        "method": "cluster_overlap_from_existing_assignments",
        "n_roles": len(rows),
        "source_paths": {
            "cluster_assignments": str(ASSIGNMENTS.relative_to(ROOT)),
            "prior_semantic_summary": str(PRIOR_SUMMARY.relative_to(ROOT)),
            "deep_semantic_topology": str(DEEP_JSON.relative_to(ROOT)),
            "semantic_bridge_roles": str(BRIDGE_SOURCE.relative_to(ROOT)),
        },
        "prior_metrics": {
            "original_prompt_vs_activation_cluster_ari_k7": prior["headline"][
                "original_prompt_vs_activation_cluster_ari_k7"
            ],
            "no_label_prompt_vs_activation_cluster_ari_k7": prior["headline"][
                "no_label_prompt_vs_activation_cluster_ari_k7"
            ],
            "original_vs_no_label_distance_correlation": prior["headline"][
                "original_vs_no_label_distance_correlation"
            ],
        },
        "activation_cluster_summary": activation_summary,
        "overlap_rows": all_overlaps,
        "triple_intersections": triples,
        "stable_anchor_count": len(anchors),
        "stable_anchor_roles": anchors,
        "stable_anchors_by_activation": dict(anchors_by_activation),
        "bridge_count": len(bridges),
        "top_bridge_roles": bridges[:80],
        "basin_analysis": basins,
        "focused_roles": focused_roles,
        "missing_focused_roles": missing_focused_roles,
        "deep_topology_reference": {
            "bridge_roles_top10": [r["role"] for r in deep["bridge_roles"][:10]],
            "lowest_density_roles_top10": [
                r["role"] for r in deep["density"]["lowest_density_roles"][:10]
            ],
        },
    }

    write_csv(
        OVERLAP_CSV,
        all_overlaps,
        [
            "k",
            "activation_cluster",
            "semantic_type",
            "semantic_cluster",
            "activation_n",
            "semantic_n",
            "intersection_n",
            "jaccard",
            "activation_containment",
            "semantic_containment",
            "shared_roles",
        ],
    )
    write_csv(
        VENN_CSV,
        triples,
        [
            "k",
            "activation_cluster",
            "original_prompt_cluster",
            "no_label_prompt_cluster",
            "intersection_n",
            "activation_containment",
            "roles",
        ],
    )
    write_csv(
        ANCHORS_CSV,
        anchors,
        [
            "role",
            "activation_cluster",
            "dominant_original_cluster",
            "dominant_no_label_cluster",
            "original_prompt_k7",
            "no_label_prompt_k7",
        ],
    )
    write_csv(
        BRIDGES_CSV,
        bridges,
        [
            "role",
            "activation_cluster",
            "original_prompt_k7",
            "dominant_original_cluster_for_activation",
            "no_label_prompt_k7",
            "dominant_no_label_cluster_for_activation",
            "original_migrates_from_activation_dominant",
            "no_label_migrates_from_activation_dominant",
            "original_to_no_label_cluster_changed",
            "semantic_bridge_margin",
            "cross_cluster_neighbors_top8",
            "bridge_score",
        ],
    )

    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(make_report(summary))
    OUT_NOTE.write_text(
        "# Cluster Overlap Interpretation Note\n\n"
        "The overlap analysis finds structured partial agreement rather than cluster equality. "
        "Editorial roles are the cleanest activation-semantic overlap, while procedural-professional "
        "compresses several semantic regions into one broad activation basin. Mythic, social, residual, "
        "and theatrical roles reorganize more substantially: prompt semantics split them by genre, life "
        "situation, and symbolic content, while activation labels group them by broader enacted behavioral "
        "structure.\n\n"
        "This strengthens the current interpretation that activation geometry is not reducible to lexical "
        "or prompt-space semantics. Semantic priors define local neighborhoods and stable anchors, but "
        "activation space sharpens, compresses, and reorganizes those neighborhoods. The next test should "
        "sample stable anchors, bridge roles, sparse roles, assistant-adjacent roles, and theatrical roles "
        "in a small no-label activation-space stress test.\n"
    )

    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_NOTE.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OVERLAP_CSV.relative_to(ROOT)}")
    print(f"Wrote {VENN_CSV.relative_to(ROOT)}")
    print(f"Wrote {ANCHORS_CSV.relative_to(ROOT)}")
    print(f"Wrote {BRIDGES_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
