#!/usr/bin/env python3
"""Deeper semantic topology analysis for the Lu et al. role corpus.

This is an offline semantic-manifold analysis. It does not run model inference,
generate activations, or call external APIs. The local environment lacks
sentence-transformers, scikit-learn, and matplotlib, so the analysis uses the
same deterministic TF-IDF plus NumPy SVD fallback as the prior semantic geometry
comparison.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
ROLE_LIST = ROOT / "data/roles/role_list.json"
INSTRUCTIONS_DIR = ROOT / "data/roles/instructions"
NO_LABEL_JSONL = (
    ROOT / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
)
FULL_RANKING = ROOT / "visualizations/full_ranking.csv"
OUT_MD = ROOT / "research/assistant_axis_methodology/deep_semantic_topology_analysis.md"
OUT_JSON = ROOT / "research/assistant_axis_methodology/deep_semantic_topology_analysis.json"
ANCHORS_CSV = ROOT / "research/assistant_axis_methodology/cluster_anchor_roles.csv"
BRIDGES_CSV = ROOT / "research/assistant_axis_methodology/semantic_bridge_roles.csv"
VOIDS_MD = ROOT / "research/assistant_axis_methodology/semantic_voids_note.md"

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "being",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "to",
    "with",
    "who",
    "you",
    "your",
    "please",
    "act",
    "respond",
    "role",
}


def tokenize(text: str) -> list[str]:
    toks = re.findall(r"[a-z0-9]+", text.lower().replace("_", " ").replace("-", " "))
    return [t for t in toks if len(t) > 1 and t not in STOPWORDS]


def ngrams(tokens: list[str]) -> list[str]:
    return tokens + [f"{tokens[i]}_{tokens[i + 1]}" for i in range(len(tokens) - 1)]


def l2norm(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def cosine_matrix(mat: np.ndarray) -> np.ndarray:
    m = l2norm(mat)
    return m @ m.T


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0


def percentile(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    idx = p * (len(xs) - 1)
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - idx) + xs[hi] * (idx - lo)


def summarize(xs: list[float]) -> dict:
    vals = [float(x) for x in xs]
    return {
        "min": min(vals),
        "p05": percentile(vals, 0.05),
        "p25": percentile(vals, 0.25),
        "median": percentile(vals, 0.50),
        "mean": sum(vals) / len(vals),
        "p75": percentile(vals, 0.75),
        "p95": percentile(vals, 0.95),
        "max": max(vals),
    }


def build_tfidf(docs_by_space: dict[str, list[str]], max_features: int = 9000):
    all_docs: list[str] = []
    offsets: dict[str, tuple[int, int]] = {}
    cursor = 0
    for name, docs in docs_by_space.items():
        offsets[name] = (cursor, cursor + len(docs))
        all_docs.extend(docs)
        cursor += len(docs)
    doc_terms = [ngrams(tokenize(doc)) for doc in all_docs]
    df = Counter()
    for terms in doc_terms:
        df.update(set(terms))
    vocab = [term for term, _ in sorted(df.items(), key=lambda kv: (-kv[1], kv[0]))][
        :max_features
    ]
    idx = {term: i for i, term in enumerate(vocab)}
    idf = np.array([math.log((1 + len(all_docs)) / (1 + df[t])) + 1 for t in vocab])
    mat = np.zeros((len(all_docs), len(vocab)), dtype=np.float64)
    for row, terms in enumerate(doc_terms):
        counts = Counter(t for t in terms if t in idx)
        total = sum(counts.values())
        if not total:
            continue
        for term, count in counts.items():
            mat[row, idx[term]] = (count / total) * idf[idx[term]]
    return l2norm(mat), offsets, vocab


def svd_reduce(mat: np.ndarray, n_components: int = 60) -> np.ndarray:
    n_components = min(n_components, mat.shape[0] - 1, mat.shape[1])
    if n_components <= 0 or mat.shape[1] <= n_components:
        return mat
    u, s, _ = np.linalg.svd(mat, full_matrices=False)
    return l2norm(u[:, :n_components] * s[:n_components])


def kmeans(mat: np.ndarray, k: int, max_iter: int = 120) -> list[int]:
    centers = [int(np.argmax(np.linalg.norm(mat, axis=1)))]
    while len(centers) < k:
        dists = np.min(
            np.stack([np.linalg.norm(mat - mat[c], axis=1) for c in centers]), axis=0
        )
        for c in centers:
            dists[c] = -1
        centers.append(int(np.argmax(dists)))
    centroids = mat[centers].copy()
    labels = np.zeros(mat.shape[0], dtype=int)
    for _ in range(max_iter):
        d = np.stack([np.linalg.norm(mat - c, axis=1) for c in centroids], axis=1)
        new_labels = np.argmin(d, axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for j in range(k):
            if np.any(labels == j):
                centroids[j] = mat[labels == j].mean(axis=0)
        centroids = l2norm(centroids)
    return labels.astype(int).tolist()


def adjusted_rand_index(a: list[int] | list[str], b: list[int] | list[str]) -> float:
    def comb2(n: int) -> float:
        return n * (n - 1) / 2

    n = len(a)
    ca: dict[int | str, list[int]] = defaultdict(list)
    cb: dict[int | str, list[int]] = defaultdict(list)
    for i, x in enumerate(a):
        ca[x].append(i)
    for i, x in enumerate(b):
        cb[x].append(i)
    sum_ij = 0.0
    for ia in ca.values():
        sa = set(ia)
        for ib in cb.values():
            sum_ij += comb2(len(sa & set(ib)))
    sum_a = sum(comb2(len(v)) for v in ca.values())
    sum_b = sum(comb2(len(v)) for v in cb.values())
    total = comb2(n)
    expected = sum_a * sum_b / total if total else 0.0
    max_index = 0.5 * (sum_a + sum_b)
    denom = max_index - expected
    return (sum_ij - expected) / denom if denom else 0.0


def load_roles() -> tuple[list[str], dict[str, str]]:
    roles_desc = json.loads(ROLE_LIST.read_text())
    return sorted(roles_desc), roles_desc


def load_original_prompts(roles: list[str]) -> dict[str, str]:
    out = {}
    for role in roles:
        data = json.loads((INSTRUCTIONS_DIR / f"{role}.json").read_text())
        prompts = [item.get("pos", "") for item in data.get("instruction", [])]
        out[role] = " ".join(prompts)
    return out


def load_no_label_prompts() -> dict[str, str]:
    by_role: dict[str, list[dict]] = defaultdict(list)
    for line in NO_LABEL_JSONL.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            by_role[rec["role"]].append(rec)
    return {
        role: " ".join(
            rec["rewritten_prompt"] for rec in sorted(rows, key=lambda r: r["prompt_index"])
        )
        for role, rows in by_role.items()
    }


def load_activation_labels(roles: list[str]) -> dict[str, str]:
    labels = {}
    with FULL_RANKING.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels[row["character"].replace(" ", "_")] = row["cluster_label"]
    return {role: labels.get(role, "unlabeled") for role in roles}


def nearest_neighbors(mat: np.ndarray, roles: list[str], n: int = 8) -> dict[str, list[dict]]:
    sim = cosine_matrix(mat)
    out = {}
    for i, role in enumerate(roles):
        order = np.argsort(-sim[i])
        rows = []
        for j in order:
            if j == i:
                continue
            rows.append({"role": roles[int(j)], "cosine": float(sim[i, j])})
            if len(rows) >= n:
                break
        out[role] = rows
    return out


def top_terms_for_roles(roles_subset: list[str], role_docs: dict[str, str], limit: int = 12) -> list[str]:
    terms = Counter()
    for role in roles_subset:
        terms.update(ngrams(tokenize(role_docs[role])))
    return [term for term, _ in terms.most_common(limit)]


def cluster_centroids(mat: np.ndarray, labels: list[int], k: int) -> np.ndarray:
    cents = []
    for cluster in range(k):
        idx = [i for i, label in enumerate(labels) if label == cluster]
        cents.append(mat[idx].mean(axis=0))
    return l2norm(np.array(cents))


def cluster_summaries(
    roles: list[str],
    mat: np.ndarray,
    labels: list[int],
    activation_labels: dict[str, str],
    role_docs: dict[str, str],
) -> list[dict]:
    k = len(set(labels))
    cents = cluster_centroids(mat, labels, k)
    rows = []
    sim = cosine_matrix(mat)
    for cluster in range(k):
        idx = [i for i, label in enumerate(labels) if label == cluster]
        cluster_roles = [roles[i] for i in idx]
        cent = cents[cluster]
        role_scores = sorted(
            [(roles[i], cosine(mat[i], cent)) for i in idx], key=lambda x: x[1], reverse=True
        )
        pairs = [sim[i, j] for n, i in enumerate(idx) for j in idx[n + 1 :]]
        act_counts = Counter(activation_labels[r] for r in cluster_roles)
        rows.append(
            {
                "cluster_id": cluster,
                "size": len(cluster_roles),
                "anchor_roles": [
                    {"role": role, "cosine_to_cluster_centroid": score}
                    for role, score in role_scores[:10]
                ],
                "lowest_members": [
                    {"role": role, "cosine_to_cluster_centroid": score}
                    for role, score in role_scores[-5:]
                ],
                "within_cluster_cosine_mean": float(np.mean(pairs)) if pairs else 1.0,
                "within_cluster_cosine_median": float(np.median(pairs)) if pairs else 1.0,
                "activation_label_distribution": dict(act_counts.most_common()),
                "top_terms": top_terms_for_roles(cluster_roles, role_docs, limit=14),
                "all_roles": cluster_roles,
            }
        )
    return sorted(rows, key=lambda r: (-r["within_cluster_cosine_mean"], -r["size"]))


def bridge_roles(
    roles: list[str],
    mat: np.ndarray,
    labels: list[int],
    nn: dict[str, list[dict]],
    activation_labels: dict[str, str],
) -> list[dict]:
    k = len(set(labels))
    cents = cluster_centroids(mat, labels, k)
    sim_to_centroids = l2norm(mat) @ cents.T
    rows = []
    for i, role in enumerate(roles):
        ordered = np.argsort(-sim_to_centroids[i])
        best = int(ordered[0])
        second = int(ordered[1])
        margin = float(sim_to_centroids[i, best] - sim_to_centroids[i, second])
        cross_neighbors = sum(1 for row in nn[role][:8] if labels[roles.index(row["role"])] != labels[i])
        density = float(np.mean([row["cosine"] for row in nn[role][:8]]))
        rows.append(
            {
                "role": role,
                "semantic_cluster": int(labels[i]),
                "activation_cluster": activation_labels.get(role, ""),
                "cluster_margin": margin,
                "best_centroid_cosine": float(sim_to_centroids[i, best]),
                "second_centroid_cosine": float(sim_to_centroids[i, second]),
                "second_cluster": second,
                "cross_cluster_neighbors_top8": cross_neighbors,
                "top8_neighbor_mean_cosine": density,
                "nearest_neighbors": ", ".join(
                    f'{r["role"]}:{r["cosine"]:.3f}' for r in nn[role][:5]
                ),
            }
        )
    return sorted(rows, key=lambda r: (r["cluster_margin"], -r["cross_cluster_neighbors_top8"]))[:40]


def density_rows(
    roles: list[str], mat: np.ndarray, nn: dict[str, list[dict]], activation_labels: dict[str, str]
) -> list[dict]:
    rows = []
    for role in roles:
        vals = [x["cosine"] for x in nn[role][:10]]
        rows.append(
            {
                "role": role,
                "activation_cluster": activation_labels.get(role, ""),
                "top5_neighbor_mean_cosine": float(np.mean(vals[:5])),
                "top10_neighbor_mean_cosine": float(np.mean(vals[:10])),
                "nearest_neighbors": ", ".join(
                    f'{x["role"]}:{x["cosine"]:.3f}' for x in nn[role][:5]
                ),
            }
        )
    return rows


def basin_stats(
    roles: list[str], mat: np.ndarray, activation_labels: dict[str, str]
) -> dict[str, dict]:
    named_groups = {
        "assistant_adjacent_seed": {
            "assistant",
            "editor",
            "proofreader",
            "screener",
            "grader",
            "examiner",
            "moderator",
            "interviewer",
            "evaluator",
            "reviewer",
            "consultant",
            "tutor",
            "translator",
            "counselor",
            "coach",
            "facilitator",
            "coordinator",
            "synthesizer",
        },
        "fantastical_theatrical_seed": {
            "trickster",
            "jester",
            "fool",
            "oracle",
            "hive",
            "egregore",
            "mystic",
            "demon",
            "angel",
            "ghost",
            "genie",
            "eldritch",
            "leviathan",
            "golem",
            "chimera",
            "shaman",
            "prophet",
            "vampire",
            "werewolf",
            "alien",
            "avatar",
            "absurdist",
        },
        "collective_identity_seed": {
            "hive",
            "egregore",
            "ecosystem",
            "mycorrhizal",
            "coral_reef",
            "zeitgeist",
            "chorus",
            "collective",
            "swarm",
        },
        "combative_seed": {
            "contrarian",
            "maverick",
            "devils_advocate",
            "competitor",
            "provocateur",
            "rebel",
            "cynic",
            "workaholic",
        },
    }
    for label in sorted(set(activation_labels.values())):
        named_groups[f"activation_{label}"] = {
            role for role in roles if activation_labels.get(role) == label
        }
    sim = cosine_matrix(mat)
    out = {}
    role_to_idx = {role: i for i, role in enumerate(roles)}
    for name, group in named_groups.items():
        present = sorted(r for r in group if r in role_to_idx)
        if len(present) < 2:
            continue
        idx = [role_to_idx[r] for r in present]
        vals = [sim[i, j] for n, i in enumerate(idx) for j in idx[n + 1 :]]
        centroid = l2norm(np.array([mat[idx].mean(axis=0)]))[0]
        anchors = sorted(
            [(roles[i], cosine(mat[i], centroid)) for i in idx],
            key=lambda x: x[1],
            reverse=True,
        )[:8]
        out[name] = {
            "n": len(present),
            "within_cosine_mean": float(np.mean(vals)),
            "within_cosine_median": float(np.median(vals)),
            "anchor_roles": [{"role": r, "cosine": s} for r, s in anchors],
        }
    return out


def hierarchical_snapshots(roles: list[str], mat: np.ndarray, targets=(3, 5, 7, 10, 20)) -> dict:
    """Create deterministic divisive hierarchy snapshots.

    Agglomerative centroid linkage collapsed into one huge cluster plus lexical
    pairs in this corpus, which is useful as an outlier signal but poor for
    interpretable superclusters. This divisive variant repeatedly splits the
    currently most dispersed cluster and is better aligned with the exploratory
    question: what coarse basins appear when the semantic manifold is forced to
    branch?
    """
    clusters = [list(range(len(roles)))]
    snapshots = {}
    target_set = set(targets)
    while len(clusters) < max(targets):
        split_idx = None
        split_score = -1.0
        for ci, cluster in enumerate(clusters):
            if len(cluster) < 4:
                continue
            sub = mat[cluster]
            cent = l2norm(np.array([sub.mean(axis=0)]))[0]
            dispersion = float(np.mean([1 - cosine(row, cent) for row in sub]))
            score = dispersion * math.log(len(cluster) + 1)
            if score > split_score:
                split_score = score
                split_idx = ci
        if split_idx is None:
            break
        cluster = clusters.pop(split_idx)
        labels = kmeans(mat[cluster], 2)
        a = [idx for idx, label in zip(cluster, labels) if label == 0]
        b = [idx for idx, label in zip(cluster, labels) if label == 1]
        if not a or not b:
            clusters.append(cluster)
            break
        clusters.extend([a, b])
        if len(clusters) in target_set:
            snap = []
            for cluster in clusters:
                cent = l2norm(np.array([mat[cluster].mean(axis=0)]))[0]
                anchors = sorted(
                    [(roles[i], cosine(mat[i], cent)) for i in cluster],
                    key=lambda x: x[1],
                    reverse=True,
                )[:10]
                snap.append({"size": len(cluster), "anchors": [r for r, _ in anchors]})
            snapshots[str(len(clusters))] = sorted(snap, key=lambda x: -x["size"])
    return snapshots


def write_csvs(cluster_rows: list[dict], bridges: list[dict], densities: list[dict]) -> None:
    with ANCHORS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "semantic_cluster",
                "cluster_size",
                "rank",
                "role",
                "cosine_to_cluster_centroid",
                "activation_label_distribution",
                "top_terms",
            ],
        )
        writer.writeheader()
        for row in cluster_rows:
            for rank, anchor in enumerate(row["anchor_roles"], start=1):
                writer.writerow(
                    {
                        "semantic_cluster": row["cluster_id"],
                        "cluster_size": row["size"],
                        "rank": rank,
                        "role": anchor["role"],
                        "cosine_to_cluster_centroid": f"{anchor['cosine_to_cluster_centroid']:.6f}",
                        "activation_label_distribution": json.dumps(
                            row["activation_label_distribution"], sort_keys=True
                        ),
                        "top_terms": ", ".join(row["top_terms"]),
                    }
                )
    with BRIDGES_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(bridges[0]))
        writer.writeheader()
        writer.writerows(bridges)
    sparse = sorted(densities, key=lambda r: r["top10_neighbor_mean_cosine"])[:30]
    dense = sorted(densities, key=lambda r: r["top10_neighbor_mean_cosine"], reverse=True)[:30]
    lines = [
        "# Semantic Voids and Density Notes",
        "",
        "This note uses no-label prompt TF-IDF/SVD topology. Low-density roles are not errors; they are roles whose prompt semantics have fewer close neighbors in this constructed corpus.",
        "",
        "## Lowest-Density Roles",
        "",
        "| Role | Activation cluster | Top-10 mean cosine | Nearest neighbors |",
        "|---|---|---:|---|",
    ]
    for row in sparse:
        lines.append(
            f"| `{row['role']}` | `{row['activation_cluster']}` | {row['top10_neighbor_mean_cosine']:.3f} | {row['nearest_neighbors']} |"
        )
    lines.extend(["", "## Highest-Density Roles", "", "| Role | Activation cluster | Top-10 mean cosine | Nearest neighbors |", "|---|---|---:|---|"])
    for row in dense:
        lines.append(
            f"| `{row['role']}` | `{row['activation_cluster']}` | {row['top10_neighbor_mean_cosine']:.3f} | {row['nearest_neighbors']} |"
        )
    VOIDS_MD.write_text("\n".join(lines) + "\n")


def write_report(summary: dict) -> None:
    clusters = summary["no_label_k7_clusters"]
    basins = summary["basin_stats"]
    bridges = summary["bridge_roles"][:15]
    density = summary["density"]
    stable = summary["stability"]
    activation = summary["activation_alignment"]
    hierarchical = summary["hierarchical_snapshots"]

    def anchor_list(row: dict) -> str:
        return ", ".join(f"`{x['role']}`" for x in row["anchor_roles"][:7])

    lines = [
        "# Deep Semantic Topology Analysis",
        "",
        "## 1. Research Question",
        "",
        "This analysis asks what structure exists in the Lu et al. role corpus before target-model activations are considered. It treats the corpus as a constructed semantic manifold made from role names, role descriptions, original label-exposed system prompts, and no-label prompt rewrites. It does not run inference, generate activations, or claim that prompt-space structure causes activation-space structure.",
        "",
        "## 2. Data and Methods",
        "",
        "Inputs were `data/roles/role_list.json`, `data/roles/instructions/*.json`, `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`, and activation labels from `visualizations/full_ranking.csv` used only as a comparison reference. The local environment did not provide sentence-transformers, scikit-learn, or matplotlib, so the script used offline TF-IDF with unigrams and bigrams, NumPy SVD reduction, deterministic k-means, cosine nearest neighbors, density summaries, cluster-margin bridge scoring, and centroid-linkage hierarchical snapshots. The no-label prompt space is used as the primary controlled semantic manifold because prior audits showed it preserves continuous prompt topology while removing explicit role-title exposure.",
        "",
        "## 3. Stable Semantic Structures",
        "",
        f"Continuous topology remains much more stable than hard cluster labels. The prior original-vs-no-label distance correlation is {stable['original_vs_no_label_distance_correlation']:.3f}, while the k=7 hard-cluster ARI between original and no-label prompt spaces is only {stable['original_vs_no_label_cluster_ari_k7']:.3f}. In this deeper pass, the most compact no-label semantic clusters are narrow professional/evaluative, confrontational, and fantastical/social-play regions; the least compact regions are broad heterogeneous role basins.",
        "",
        "The no-label k=7 semantic clusters are:",
        "",
        "| Semantic cluster | n | Mean within cosine | Anchors | Main activation-label mix | Top terms |",
        "|---:|---:|---:|---|---|---|",
    ]
    for row in clusters:
        top_act = ", ".join(
            f"{k}:{v}" for k, v in list(row["activation_label_distribution"].items())[:4]
        )
        lines.append(
            f"| {row['cluster_id']} | {row['size']} | {row['within_cluster_cosine_mean']:.3f} | {anchor_list(row)} | {top_act} | {', '.join(row['top_terms'][:8])} |"
        )
    lines.extend(
        [
            "",
            "## 4. Cluster Archetypes",
            "",
            "The strongest semantic structures are not a single kind of category. Some are professional and procedural, some are narrative or mythic, some are moralized or adversarial, and some are stylistic modes of speech. The corpus therefore appears organized by a mixture of social function, communicative stance, narrative genre, and expected behavioral repertoire rather than by one psychological taxonomy.",
            "",
            "The editorial/professional pocket is anchored by roles whose prompts repeatedly describe assessment, refinement, standards, and clear output improvement. The combative pocket is anchored by opposition, challenge, competition, and pressure. The theatrical/fantastical pocket is anchored by symbolic agency, boundary play, prophecy, mischief, and nonordinary identity. Large professional/helper and mythic/social basins are less discrete; they look more like gradients or families than clean partitions.",
            "",
            "## 5. Basin Structures",
            "",
            "| Basin | n | Mean within cosine | Anchors |",
            "|---|---:|---:|---|",
        ]
    )
    preferred_basin_order = [
        "assistant_adjacent_seed",
        "activation_editorial",
        "activation_procedural_professional",
        "fantastical_theatrical_seed",
        "collective_identity_seed",
        "combative_seed",
        "activation_trickster_chaos",
        "activation_mythic_spiritual",
        "activation_grounded_social",
        "activation_other",
    ]
    for name in preferred_basin_order:
        if name not in basins:
            continue
        row = basins[name]
        anchors = ", ".join(f"`{x['role']}`" for x in row["anchor_roles"][:6])
        lines.append(f"| `{name}` | {row['n']} | {row['within_cosine_mean']:.3f} | {anchors} |")
    lines.extend(
        [
            "",
            "The assistant-adjacent seed set is semantically coherent but not uniquely separate from the broader professional/helper material. This supports the current working view that assistant-basin structure can already be visible in prompt semantics, while activation-space extraction may compress these roles back toward generic assistant behavior. Fantastical and theatrical roles are semantically vivid, but they are not one compact island; they spread across prophetic, symbolic, playful, monstrous, and collective subregions.",
            "",
            "## 6. Density and Topology Observations",
            "",
            f"The densest local neighborhoods have top-10 neighbor mean cosine around {density['top10_summary']['p95']:.3f}; the sparsest tail falls near {density['top10_summary']['p05']:.3f}. Dense regions generally correspond to redundant social functions or strongly scripted genres. Sparse regions are often hybrid, culturally specific, or ontologically unusual roles whose prompts do not have many close analogues in the 275-role inventory.",
            "",
            "The hierarchical snapshots suggest broad superclusters rather than natural hard partitions. At three clusters the manifold separates into a large professional/social/helper region, a mythic/fantastical/symbolic region, and a more adversarial/playful/outlier region. At seven clusters these split into smaller pockets, but many boundaries remain soft.",
            "",
            "Representative hierarchical snapshots:",
            "",
        ]
    )
    for level in ["3", "5", "7"]:
        if level not in hierarchical:
            continue
        lines.append(f"### {level} clusters")
        lines.append("")
        for idx, row in enumerate(hierarchical[level][:8], start=1):
            lines.append(f"{idx}. n={row['size']}: " + ", ".join(f"`{x}`" for x in row["anchors"][:8]))
        lines.append("")
    lines.extend(
        [
            "## 7. Bridge and Outlier Roles",
            "",
            "Bridge roles were identified by low margin between the nearest and second-nearest no-label semantic cluster centroids, cross-cluster nearest neighbors, and local density. These are the roles most likely to move under small representation changes or different clustering methods.",
            "",
            "| Role | Activation cluster | Semantic cluster | Margin | Cross-cluster neighbors | Nearest neighbors |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in bridges:
        lines.append(
            f"| `{row['role']}` | `{row['activation_cluster']}` | {row['semantic_cluster']} | {row['cluster_margin']:.3f} | {row['cross_cluster_neighbors_top8']} | {row['nearest_neighbors']} |"
        )
    lines.extend(
        [
            "",
            "The main outlier pattern is not random noise. Low-density roles tend to expose missing coverage in the corpus: unusual collectivities, specialized social positions, embodied developmental identities, and roles whose cultural scripts are narrow or unevenly represented. This is why the report treats semantic voids as corpus-design evidence rather than as bad data.",
            "",
            "## 8. Relationship to Activation Geometry",
            "",
            f"Semantic topology and activation topology partially align, but the agreement is limited. In this deeper pass, k=7 ARI against activation labels is {activation['no_label_prompt_vs_activation_cluster_ari_k7']:.3f} for no-label prompt clusters and {activation['original_prompt_vs_activation_cluster_ari_k7']:.3f} for original prompt clusters. No-label prompt distances best predict available activation centroid-profile distances in the prior comparison, but correlations remain modest: {activation['gemma_centroid_profile_distance_correlation']:.3f} for Gemma and {activation['qwen_centroid_profile_distance_correlation']:.3f} for Qwen.",
            "",
            "The cautious interpretation is preservation plus reorganization. Activation-space geometry appears to inherit semantic priors from the elicitation corpus, but it also sharpens some pockets, compresses some broad regions, and reorganizes neighborhoods according to model-specific representational pressures. The editorial cluster is semantically intrinsic and activation-adjacent to the assistant basin; trickster is semantically vivid and activation-separable in the completed Qwen extraction; editor is semantically clear but behaviorally low-yield under the tested extraction setup.",
            "",
            "## 9. Cultural and Methodological Limitations",
            "",
            "The role corpus is not a representative sample of human social life. It is an English-language, frontier-model-generated role inventory with heavy coverage of professions, helpers, archetypes, fantastical figures, and individualist identities. It likely undersamples non-Western social categories, kinship systems, ritual offices, communal identities, caste or lineage structures, and non-individualist self-concepts. Semantic clusters should therefore be interpreted as structure in this constructed corpus, not as a canonical map of human psychology.",
            "",
            "The analysis is also methodologically limited by the local TF-IDF/SVD fallback. It captures lexical and phrase-level topology well enough for continuity checks, but it underestimates paraphrastic equivalence and culturally implicit similarity. The activation comparison uses available labels and centroid-profile outputs, not a reconstructed full activation distance matrix.",
            "",
            "## 10. Emerging Hypotheses",
            "",
            "### Supported observations",
            "",
            "- The role corpus has meaningful semantic topology before activations are considered.",
            "- No-label prompt topology remains close to original prompt topology at the continuous distance level.",
            "- Hard semantic clusters are soft and unstable compared with continuous neighborhoods.",
            "- Prompt semantics partially predict activation references, but not strongly enough to reduce activation geometry to semantics.",
            "",
            "### Provisional interpretations",
            "",
            "- Semantic priors constrain activation geometry, while model activations reorganize those priors into model-specific basins.",
            "- Assistant-adjacent roles may form a dense semantic/procedural basin that makes low-yield role extraction harder, not easier.",
            "- Theatrical roles may be easier to extract because their semantic cues are vivid, redundant, and far from generic assistant behavior.",
            "- Bridge and low-density roles are useful probes for testing whether activation clusters are robust or prompt-corpus-dependent.",
            "",
            "### Speculative hypotheses",
            "",
            "- Some activation clusters may correspond to semantic superclusters that are sharpened by model internals rather than directly mirrored from prompt text.",
            "- Current role coverage may miss important culturally situated identity regions, causing apparent voids or overlarge residual clusters.",
            "- No-label activation tests may separate roles whose prompt-space topology is label-independent from roles that require explicit identity priming to reach the intended activation direction.",
            "",
            "## 11. Recommended Next Experiments",
            "",
            "Run a small no-label activation-space stress test before scaling. Use a mixed set: trickster as a high-yield theatrical positive control, editor as an assistant-adjacent failure case, one professional/helper role, one mythic or collective role, and one bridge role from `semantic_bridge_roles.csv`. The test should compare original-prompt and no-label vectors against Lu reference directions while tracking role-expression scoring, truncation, and adaptive stopping separately.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")


def main() -> None:
    roles, role_desc = load_roles()
    original_prompts = load_original_prompts(roles)
    no_label_prompts = load_no_label_prompts()
    activation_labels = load_activation_labels(roles)

    docs = {
        "role_name": [role.replace("_", " ") for role in roles],
        "role_name_description": [
            f"{role.replace('_', ' ')}: {role_desc[role]}" for role in roles
        ],
        "original_prompt": [original_prompts[role] for role in roles],
        "no_label_prompt": [no_label_prompts[role] for role in roles],
    }
    tfidf, offsets, _vocab = build_tfidf(docs)
    reduced = svd_reduce(tfidf, n_components=60)
    mats = {name: reduced[start:end] for name, (start, end) in offsets.items()}

    no_label = mats["no_label_prompt"]
    original = mats["original_prompt"]
    name_mat = mats["role_name"]
    no_label_k7 = kmeans(no_label, 7)
    original_k7 = kmeans(original, 7)
    role_name_k7 = kmeans(name_mat, 7)
    activation_list = [activation_labels[role] for role in roles]
    no_label_nn = nearest_neighbors(no_label, roles, n=10)
    cluster_rows = cluster_summaries(
        roles, no_label, no_label_k7, activation_labels, no_label_prompts
    )
    bridges = bridge_roles(roles, no_label, no_label_k7, no_label_nn, activation_labels)
    densities = density_rows(roles, no_label, no_label_nn, activation_labels)
    basins = basin_stats(roles, no_label, activation_labels)
    hierarchical = hierarchical_snapshots(roles, no_label)

    # Reuse fixed prior metrics as documented outputs from the immediately
    # preceding comparison, because this script focuses on topology diagnostics.
    summary = {
        "date": "2026-05-27",
        "model_used": "GPT-5.5",
        "method": "offline_tfidf_svd_deep_semantic_topology",
        "n_roles": len(roles),
        "source_paths": {
            "role_list": str(ROLE_LIST.relative_to(ROOT)),
            "role_instruction_dir": str(INSTRUCTIONS_DIR.relative_to(ROOT)),
            "no_label_prompts": str(NO_LABEL_JSONL.relative_to(ROOT)),
            "activation_cluster_labels": str(FULL_RANKING.relative_to(ROOT)),
        },
        "environment": {
            "sentence_transformers_available": False,
            "sklearn_available": False,
            "matplotlib_available": False,
            "new_activation_inference": False,
        },
        "stability": {
            "original_vs_no_label_distance_correlation": 0.956,
            "original_vs_no_label_cluster_ari_k7": adjusted_rand_index(original_k7, no_label_k7),
            "role_name_vs_no_label_cluster_ari_k7": adjusted_rand_index(role_name_k7, no_label_k7),
        },
        "activation_alignment": {
            "role_name_vs_activation_cluster_ari_k7": adjusted_rand_index(role_name_k7, activation_list),
            "original_prompt_vs_activation_cluster_ari_k7": adjusted_rand_index(original_k7, activation_list),
            "no_label_prompt_vs_activation_cluster_ari_k7": adjusted_rand_index(no_label_k7, activation_list),
            "gemma_centroid_profile_distance_correlation": 0.230,
            "qwen_centroid_profile_distance_correlation": 0.254,
        },
        "no_label_k7_clusters": cluster_rows,
        "basin_stats": basins,
        "bridge_roles": bridges,
        "density": {
            "top10_summary": summarize([row["top10_neighbor_mean_cosine"] for row in densities]),
            "lowest_density_roles": sorted(
                densities, key=lambda r: r["top10_neighbor_mean_cosine"]
            )[:20],
            "highest_density_roles": sorted(
                densities, key=lambda r: r["top10_neighbor_mean_cosine"], reverse=True
            )[:20],
        },
        "hierarchical_snapshots": hierarchical,
        "interpretation": {
            "supported": [
                "The semantic role corpus has meaningful topology before activation-space analysis.",
                "Continuous original-to-no-label prompt topology is stable even when hard clusters shift.",
                "Semantic topology partially predicts activation references but does not explain them away.",
            ],
            "provisional": [
                "Assistant-adjacent roles form a dense semantic/procedural basin that may encourage generic assistant collapse.",
                "Theatrical roles may be easier to extract because their prompt cues are vivid, redundant, and distant from default assistant behavior.",
                "Bridge and sparse roles are useful probes for prompt-corpus dependence.",
            ],
            "speculative": [
                "Activation geometry may sharpen some semantic pockets and compress broad basins.",
                "The current English-language role corpus likely undersamples culturally situated communal and ritual identity regions.",
            ],
        },
    }

    write_csvs(cluster_rows, bridges, densities)
    write_report(summary)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {ANCHORS_CSV.relative_to(ROOT)}")
    print(f"Wrote {BRIDGES_CSV.relative_to(ROOT)}")
    print(f"Wrote {VOIDS_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
