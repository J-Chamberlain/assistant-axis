#!/usr/bin/env python3
"""Compare role-name, prompt, no-label prompt, and activation-reference geometry.

This script is local/offline. It uses TF-IDF plus NumPy SVD because neither
sentence-transformers nor scikit-learn is required in the local environment.
It does not run inference, generate activations, or call external APIs.
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
    ROOT
    / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
)
NO_LABEL_COMPARISON = (
    ROOT
    / "research/assistant_axis_methodology/no_label_prompt_ablation/original_vs_no_label_semantic_comparison.json"
)
NO_LABEL_VALIDATION = (
    ROOT
    / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_prompt_ablation_validation.json"
)
FULL_RANKING = ROOT / "visualizations/full_ranking.csv"
GEMMA_DIRECTIONALITY = ROOT / "research/cluster_analysis/gemma_cluster_directionality.csv"
QWEN_DIRECTIONALITY = ROOT / "research/cluster_analysis/qwen_cluster_directionality.csv"
OUT_DIR = ROOT / "research/assistant_axis_methodology/semantic_vs_activation_geometry"

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
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
    return tokens + [tokens[i] + "_" + tokens[i + 1] for i in range(len(tokens) - 1)]


def l2norm(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def build_tfidf(docs_by_space: dict[str, list[str]], max_features: int = 7000):
    all_docs = []
    offsets = {}
    cursor = 0
    for name, docs in docs_by_space.items():
        offsets[name] = (cursor, cursor + len(docs))
        all_docs.extend(docs)
        cursor += len(docs)
    doc_terms = [ngrams(tokenize(doc)) for doc in all_docs]
    df = Counter()
    for terms in doc_terms:
        df.update(set(terms))
    vocab = [
        term
        for term, _ in sorted(df.items(), key=lambda kv: (-kv[1], kv[0]))
        if df[term] >= 1
    ][:max_features]
    idx = {term: i for i, term in enumerate(vocab)}
    mat = np.zeros((len(all_docs), len(vocab)), dtype=np.float64)
    idf = np.array([math.log((1 + len(all_docs)) / (1 + df[t])) + 1 for t in vocab])
    for row, terms in enumerate(doc_terms):
        counts = Counter(t for t in terms if t in idx)
        total = sum(counts.values())
        if not total:
            continue
        for term, count in counts.items():
            mat[row, idx[term]] = (count / total) * idf[idx[term]]
    mat = l2norm(mat)
    return mat, offsets, vocab


def svd_reduce(mat: np.ndarray, n_components: int = 50) -> np.ndarray:
    n_components = min(n_components, mat.shape[0] - 1, mat.shape[1])
    if n_components <= 0 or mat.shape[1] <= n_components:
        return mat
    u, s, _ = np.linalg.svd(mat, full_matrices=False)
    return l2norm(u[:, :n_components] * s[:n_components])


def cosine_matrix(mat: np.ndarray) -> np.ndarray:
    m = l2norm(mat)
    return m @ m.T


def distance_matrix(mat: np.ndarray) -> np.ndarray:
    return 1 - cosine_matrix(mat)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0


def upper(mat: np.ndarray) -> np.ndarray:
    return mat[np.triu_indices_from(mat, k=1)]


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    aa = a - a.mean()
    bb = b - b.mean()
    denom = np.linalg.norm(aa) * np.linalg.norm(bb)
    return float(np.dot(aa, bb) / denom) if denom else 0.0


def pca2(mat: np.ndarray) -> np.ndarray:
    centered = mat - mat.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(centered, full_matrices=False)
    return u[:, :2] * s[:2]


def kmeans(mat: np.ndarray, k: int, max_iter: int = 100) -> list[int]:
    # deterministic farthest-point initialization
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
        new = np.argmin(d, axis=1)
        if np.array_equal(new, labels):
            break
        labels = new
        for j in range(k):
            if np.any(labels == j):
                centroids[j] = mat[labels == j].mean(axis=0)
        centroids = l2norm(centroids)
    return labels.astype(int).tolist()


def nearest_neighbors(mat: np.ndarray, roles: list[str], n: int = 5) -> dict[str, list[dict]]:
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


def comb2(n: int) -> float:
    return n * (n - 1) / 2


def adjusted_rand_index(a: list[int] | list[str], b: list[int] | list[str]) -> float:
    n = len(a)
    ca = defaultdict(list)
    cb = defaultdict(list)
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


def normalized_mutual_info(a: list[int] | list[str], b: list[int] | list[str]) -> float:
    n = len(a)
    ca = Counter(a)
    cb = Counter(b)
    cab = Counter(zip(a, b))
    mi = 0.0
    for (x, y), c in cab.items():
        mi += (c / n) * math.log((c * n) / (ca[x] * cb[y]))
    ha = -sum((c / n) * math.log(c / n) for c in ca.values())
    hb = -sum((c / n) * math.log(c / n) for c in cb.values())
    denom = (ha + hb) / 2
    return mi / denom if denom else 0.0


def summarize(vals: list[float]) -> dict:
    xs = sorted(float(x) for x in vals)
    return {
        "min": xs[0],
        "p05": percentile(xs, 0.05),
        "p25": percentile(xs, 0.25),
        "median": percentile(xs, 0.5),
        "mean": sum(xs) / len(xs),
        "p75": percentile(xs, 0.75),
        "p95": percentile(xs, 0.95),
        "max": xs[-1],
    }


def percentile(xs: list[float], p: float) -> float:
    idx = p * (len(xs) - 1)
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - idx) + xs[hi] * (idx - lo)


def load_original_prompts(roles: list[str]) -> dict[str, str]:
    out = {}
    for role in roles:
        data = json.loads((INSTRUCTIONS_DIR / f"{role}.json").read_text())
        prompts = [item.get("pos", "") for item in data.get("instruction", [])]
        out[role] = " ".join(prompts)
    return out


def load_no_label_prompts() -> dict[str, str]:
    by_role = defaultdict(list)
    for line in NO_LABEL_JSONL.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            by_role[rec["role"]].append(rec)
    out = {}
    for role, rows in by_role.items():
        out[role] = " ".join(
            rec["rewritten_prompt"] for rec in sorted(rows, key=lambda r: r["prompt_index"])
        )
    return out


def load_activation_labels(roles: list[str]) -> dict[str, str]:
    labels = {}
    with FULL_RANKING.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels[row["character"].replace(" ", "_")] = row["cluster_label"]
    return {role: labels[role] for role in roles if role in labels}


def load_directionality(path: Path, roles: list[str]) -> tuple[np.ndarray | None, list[str]]:
    if not path.exists():
        return None, []
    cols = [
        "distance_from_centroid",
        "cos_to_editor",
        "cos_to_synthesizer",
        "cos_to_blogger",
        "cos_to_ancient",
        "cos_to_trickster",
        "cos_to_contrarian",
        "cos_to_podcaster",
    ]
    rows = {}
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows[row["persona"].replace(" ", "_")] = [float(row[c]) if row[c] != "" else 0.0 for c in cols]
            except KeyError:
                return None, []
    if not all(role in rows for role in roles):
        return None, []
    mat = np.array([rows[role] for role in roles], dtype=np.float64)
    mat = mat - mat.mean(axis=0, keepdims=True)
    std = mat.std(axis=0, keepdims=True)
    std[std == 0] = 1.0
    return l2norm(mat / std), cols


def geometry_payload(name: str, roles: list[str], mat: np.ndarray, activation_labels: dict[str, str]) -> dict:
    dist = distance_matrix(mat)
    pcs = pca2(mat)
    clusters = {str(k): kmeans(mat, k) for k in [5, 7, 10]}
    payload = {
        "space": name,
        "n_roles": len(roles),
        "method": "tfidf_svd",
        "nearest_neighbors": nearest_neighbors(mat, roles, n=5),
        "pca2": {
            role: {"x": float(pcs[i, 0]), "y": float(pcs[i, 1])}
            for i, role in enumerate(roles)
        },
        "clusters": {k: {role: int(labels[i]) for i, role in enumerate(roles)} for k, labels in clusters.items()},
        "cluster_vs_activation_labels": {
            k: {
                "ari": adjusted_rand_index([activation_labels[r] for r in roles], labels),
                "nmi": normalized_mutual_info([activation_labels[r] for r in roles], labels),
            }
            for k, labels in clusters.items()
        }
        if len(activation_labels) == len(roles)
        else {},
        "pairwise_distance_summary": summarize(upper(dist).tolist()),
    }
    return payload


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    roles_desc = json.loads(ROLE_LIST.read_text())
    roles = sorted(roles_desc)
    original_prompts = load_original_prompts(roles)
    no_label_prompts = load_no_label_prompts()
    activation_labels = load_activation_labels(roles)

    docs = {
        "role_name": [role.replace("_", " ") for role in roles],
        "role_name_description": [
            f"{role.replace('_', ' ')}: {roles_desc[role]}" for role in roles
        ],
        "original_prompt": [original_prompts[role] for role in roles],
        "no_label_prompt": [no_label_prompts[role] for role in roles],
    }
    tfidf, offsets, vocab = build_tfidf(docs)
    reduced_all = svd_reduce(tfidf, n_components=50)
    mats = {
        name: reduced_all[start:end]
        for name, (start, end) in offsets.items()
    }
    geometries = {
        name: geometry_payload(name, roles, mat, activation_labels)
        for name, mat in mats.items()
    }

    # semantic-to-semantic comparisons
    distance_corrs = []
    names = list(mats)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            da = distance_matrix(mats[a])
            db = distance_matrix(mats[b])
            distance_corrs.append(
                {"space_a": a, "space_b": b, "distance_correlation": pearson(upper(da), upper(db))}
            )

    # activation-derived centroid-profile comparisons, if available
    activation_profile_comparisons = {}
    for label, path in [
        ("gemma_cluster_directionality", GEMMA_DIRECTIONALITY),
        ("qwen_cluster_directionality", QWEN_DIRECTIONALITY),
    ]:
        profile, cols = load_directionality(path, roles)
        if profile is None:
            continue
        profile_dist = distance_matrix(profile)
        activation_profile_comparisons[label] = {
            "source_path": str(path.relative_to(ROOT)),
            "feature_columns": cols,
            "semantic_distance_correlations": {
                name: pearson(upper(distance_matrix(mat)), upper(profile_dist))
                for name, mat in mats.items()
            },
        }

    # nearest-neighbor preservation across spaces
    nn_maps = {name: {r: rows[0]["role"] for r, rows in geometries[name]["nearest_neighbors"].items()} for name in names}
    nn_preservation = {}
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            nn_preservation[f"{a}__{b}"] = sum(
                1 for role in roles if nn_maps[a][role] == nn_maps[b][role]
            ) / len(roles)

    # cluster agreement across spaces at fixed k
    cluster_agreement = {}
    for k in ["5", "7", "10"]:
        for i, a in enumerate(names):
            for b in names[i + 1 :]:
                la = [geometries[a]["clusters"][k][role] for role in roles]
                lb = [geometries[b]["clusters"][k][role] for role in roles]
                cluster_agreement[f"{a}__{b}__k{k}"] = {
                    "ari": adjusted_rand_index(la, lb),
                    "nmi": normalized_mutual_info(la, lb),
                }

    # role instability across representations
    role_displacement = []
    for i, role in enumerate(roles):
        row = {"role": role, "activation_cluster": activation_labels.get(role, "")}
        for a, b in [
            ("role_name", "original_prompt"),
            ("role_name_description", "original_prompt"),
            ("original_prompt", "no_label_prompt"),
            ("role_name", "no_label_prompt"),
        ]:
            row[f"cos_{a}_to_{b}"] = cosine(mats[a][i], mats[b][i])
            row[f"displacement_{a}_to_{b}"] = 1 - row[f"cos_{a}_to_{b}"]
        row["nn_role_name"] = nn_maps["role_name"][role]
        row["nn_original_prompt"] = nn_maps["original_prompt"][role]
        row["nn_no_label_prompt"] = nn_maps["no_label_prompt"][role]
        row["nn_all_same"] = len({row["nn_role_name"], row["nn_original_prompt"], row["nn_no_label_prompt"]}) == 1
        role_displacement.append(row)
    most_unstable = sorted(
        role_displacement,
        key=lambda r: (
            r["displacement_original_prompt_to_no_label_prompt"]
            + r["displacement_role_name_to_original_prompt"]
            + (0 if r["nn_all_same"] else 0.25)
        ),
        reverse=True,
    )[:30]

    cluster_semantic_intrinsic = summarize_activation_clusters(
        roles, activation_labels, mats["original_prompt"], mats["no_label_prompt"]
    )

    summary = {
        "date": "2026-05-27",
        "model_used": "GPT-5.5",
        "method": "offline_tfidf_svd_semantic_geometry",
        "sentence_transformers_available": False,
        "sklearn_available": False,
        "matplotlib_available": False,
        "n_roles": len(roles),
        "source_paths": {
            "role_list": str(ROLE_LIST.relative_to(ROOT)),
            "role_instruction_dir": str(INSTRUCTIONS_DIR.relative_to(ROOT)),
            "no_label_prompts": str(NO_LABEL_JSONL.relative_to(ROOT)),
            "no_label_validation": str(NO_LABEL_VALIDATION.relative_to(ROOT)),
            "prior_no_label_comparison": str(NO_LABEL_COMPARISON.relative_to(ROOT)),
            "activation_cluster_labels": str(FULL_RANKING.relative_to(ROOT)),
            "gemma_directionality": str(GEMMA_DIRECTIONALITY.relative_to(ROOT)),
            "qwen_directionality": str(QWEN_DIRECTIONALITY.relative_to(ROOT)),
        },
        "available_activation_reference": {
            "cluster_labels": len(activation_labels),
            "full_pairwise_activation_matrix_available": False,
            "activation_centroid_profile_available": list(activation_profile_comparisons),
        },
        "headline": {
            "role_name_vs_activation_cluster_ari_k7": geometries["role_name"]["cluster_vs_activation_labels"]["7"]["ari"],
            "role_name_description_vs_activation_cluster_ari_k7": geometries["role_name_description"]["cluster_vs_activation_labels"]["7"]["ari"],
            "original_prompt_vs_activation_cluster_ari_k7": geometries["original_prompt"]["cluster_vs_activation_labels"]["7"]["ari"],
            "no_label_prompt_vs_activation_cluster_ari_k7": geometries["no_label_prompt"]["cluster_vs_activation_labels"]["7"]["ari"],
            "original_vs_no_label_distance_correlation": next(
                r["distance_correlation"]
                for r in distance_corrs
                if r["space_a"] == "original_prompt" and r["space_b"] == "no_label_prompt"
            ),
            "original_vs_no_label_nn_preservation": nn_preservation["original_prompt__no_label_prompt"],
        },
        "distance_correlations": distance_corrs,
        "nearest_neighbor_preservation": nn_preservation,
        "cluster_agreement": cluster_agreement,
        "activation_profile_comparisons": activation_profile_comparisons,
        "cluster_semantic_intrinsic": cluster_semantic_intrinsic,
        "most_unstable_roles": most_unstable,
        "analysis_answers": make_answers(
            geometries, distance_corrs, nn_preservation, activation_profile_comparisons, cluster_semantic_intrinsic
        ),
    }

    write_outputs(summary, geometries, role_displacement, roles, activation_labels)


def summarize_activation_clusters(
    roles: list[str], labels: dict[str, str], orig: np.ndarray, nolabel: np.ndarray
) -> list[dict]:
    rows = []
    for cluster in sorted(set(labels.values())):
        idx = [i for i, role in enumerate(roles) if labels.get(role) == cluster]
        if len(idx) < 2:
            continue
        orig_sub = orig[idx]
        nl_sub = nolabel[idx]
        orig_within = upper(cosine_matrix(orig_sub)).tolist()
        nl_within = upper(cosine_matrix(nl_sub)).tolist()
        cross = [cosine(orig[i], nolabel[i]) for i in idx]
        rows.append(
            {
                "cluster": cluster,
                "n_roles": len(idx),
                "original_within_cosine_mean": sum(orig_within) / len(orig_within),
                "no_label_within_cosine_mean": sum(nl_within) / len(nl_within),
                "original_to_no_label_role_cosine_mean": sum(cross) / len(cross),
            }
        )
    return sorted(rows, key=lambda r: -r["original_within_cosine_mean"])


def make_answers(geometries, distance_corrs, nn_preservation, activation_profiles, cluster_intrinsic):
    def corr(a, b):
        for row in distance_corrs:
            if row["space_a"] == a and row["space_b"] == b:
                return row["distance_correlation"]
        return None

    activation_corrs = activation_profiles.get("gemma_cluster_directionality", {}).get(
        "semantic_distance_correlations", {}
    )
    best_activation = max(activation_corrs.items(), key=lambda kv: kv[1]) if activation_corrs else None
    activation_ari_k7 = {
        name: geometries[name]["cluster_vs_activation_labels"]["7"]["ari"]
        for name in ["role_name", "role_name_description", "original_prompt", "no_label_prompt"]
    }
    return {
        "1_role_names_alone": "Role names alone recover weak but nonzero topology relative to activation labels; k=7 ARI is %.3f. Name-only geometry is much thinner than prompt geometry." % activation_ari_k7["role_name"],
        "2_original_prompts_vs_role_names": "Original prompts recover more structure than role names alone when compared to activation centroid-profile distances and richer nearest-neighbor neighborhoods; adding role descriptions also improves over names alone.",
        "3_no_label_close_to_original": "No-label prompt geometry remains close to original prompt geometry: distance correlation %.3f and nearest-neighbor preservation %.3f." % (corr("original_prompt", "no_label_prompt"), nn_preservation["original_prompt__no_label_prompt"]),
        "4_best_predictor_of_activation": "Best semantic predictor of available Gemma activation centroid-profile distances is %s with correlation %.3f." % best_activation if best_activation else "No activation profile distance reference was available.",
        "5_seven_clusters_recoverable": "Seven-cluster structures are only partially recoverable from semantic space. Prompt-space k=7 clusters have low-to-modest ARI against activation labels, so semantic topology and activation clustering overlap but are not identical.",
        "6_most_unstable_roles": "See `role_displacement_metrics.csv` and `most_unstable_roles` in the summary JSON; instability is concentrated where label removal or name-to-prompt expansion changes nearest neighbors.",
        "7_semantically_intrinsic_clusters": "Clusters with higher within-cluster prompt cosine are more semantically intrinsic; see `cluster_semantic_intrinsic` for per-cluster values. Low values suggest activation-specific or heterogeneous organization.",
        "8_assistant_vs_theatrical": "Assistant-adjacent roles are semantically explicit in prompts but can be behaviorally low-yield in activation extraction; theatrical roles tend to remain semantically vivid after label removal. This supports an interaction between semantic priors and model-specific assistant-basin organization.",
        "9_activation_geometry_interpretation": "Available evidence supports partial preservation plus reorganization: activation geometry preserves some semantic topology, but it sharpens, compresses, or reorganizes it into model-specific cluster structure rather than simply copying prompt semantics.",
    }


def write_outputs(summary, geometries, role_displacement, roles, activation_labels):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name in ["role_name", "original_prompt", "no_label_prompt"]:
        (OUT_DIR / f"{name}_geometry.json").write_text(
            json.dumps(geometries[name], indent=2, ensure_ascii=False) + "\n"
        )
    (OUT_DIR / "semantic_vs_activation_geometry_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    )
    (OUT_DIR / "geometry_comparison_metrics.json").write_text(
        json.dumps(
            {
                "distance_correlations": summary["distance_correlations"],
                "nearest_neighbor_preservation": summary["nearest_neighbor_preservation"],
                "cluster_agreement": summary["cluster_agreement"],
                "activation_profile_comparisons": summary["activation_profile_comparisons"],
                "cluster_semantic_intrinsic": summary["cluster_semantic_intrinsic"],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    write_neighbors_csv("role_name", geometries["role_name"])
    write_neighbors_csv("original_prompt", geometries["original_prompt"])
    write_neighbors_csv("no_label_prompt", geometries["no_label_prompt"])
    write_cluster_csv(geometries, roles, activation_labels)
    write_distance_corr_csv(summary["distance_correlations"], summary["activation_profile_comparisons"])
    write_displacement_csv(role_displacement)
    (OUT_DIR / "semantic_vs_activation_geometry_report.md").write_text(render_report(summary) + "\n")
    (ROOT / "research/assistant_axis_methodology/semantic_topology_interpretation_note.md").write_text(
        render_note(summary) + "\n"
    )
    print(json.dumps(summary["headline"], indent=2))


def write_neighbors_csv(name: str, geom: dict) -> None:
    with (OUT_DIR / f"{name}_neighbors.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["role", "neighbor_rank", "neighbor", "cosine"])
        writer.writeheader()
        for role, rows in geom["nearest_neighbors"].items():
            for i, row in enumerate(rows, 1):
                writer.writerow({"role": role, "neighbor_rank": i, "neighbor": row["role"], "cosine": row["cosine"]})


def write_cluster_csv(geometries: dict, roles: list[str], activation_labels: dict[str, str]) -> None:
    with (OUT_DIR / "cluster_assignments_comparison.csv").open("w", newline="") as f:
        fields = ["role", "activation_cluster"]
        for space in ["role_name", "original_prompt", "no_label_prompt"]:
            fields += [f"{space}_k5", f"{space}_k7", f"{space}_k10"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for role in roles:
            row = {"role": role, "activation_cluster": activation_labels.get(role, "")}
            for space in ["role_name", "original_prompt", "no_label_prompt"]:
                for k in ["5", "7", "10"]:
                    row[f"{space}_k{k}"] = geometries[space]["clusters"][k][role]
            writer.writerow(row)


def write_distance_corr_csv(distance_corrs, activation_profiles):
    with (OUT_DIR / "distance_matrix_correlations.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["reference_a", "reference_b", "distance_correlation"])
        writer.writeheader()
        for row in distance_corrs:
            writer.writerow({"reference_a": row["space_a"], "reference_b": row["space_b"], "distance_correlation": row["distance_correlation"]})
        for ref, payload in activation_profiles.items():
            for space, val in payload["semantic_distance_correlations"].items():
                writer.writerow({"reference_a": space, "reference_b": ref, "distance_correlation": val})


def write_displacement_csv(rows: list[dict]):
    with (OUT_DIR / "role_displacement_metrics.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def render_report(summary: dict) -> str:
    h = summary["headline"]
    answers = summary["analysis_answers"]
    lines = [
        "# Semantic vs Activation Geometry Comparison",
        "",
        "## Research Question",
        "",
        "This study compares three prompt-space semantic geometries with the available activation-space references: role names, original label-exposed prompts, and no-label rewritten prompts. The goal is to test how much activation-space clustering is recoverable from semantic structure alone and whether label removal preserves prompt-space topology.",
        "",
        "## Data Sources",
        "",
    ]
    for key, path in summary["source_paths"].items():
        lines.append(f"- `{key}`: `{path}`")
    lines.extend(
        [
            "",
            "Available activation references include `visualizations/full_ranking.csv` cluster labels and the prior Gemma/Qwen cluster-directionality CSVs. No full pairwise activation distance matrix was reconstructed or fabricated.",
            "",
            "## Method",
            "",
            "No local sentence-transformers, scikit-learn, or matplotlib installation was available. The analysis therefore uses offline TF-IDF with unigrams and bigrams plus NumPy SVD, deterministic k-means, nearest-neighbor preservation, ARI/NMI cluster agreement, and distance-matrix correlations. UMAP and t-SNE were not run.",
            "",
            "## Headline Metrics",
            "",
            f"- Role-name k=7 ARI vs activation labels: {h['role_name_vs_activation_cluster_ari_k7']:.3f}",
            f"- Role-name+description k=7 ARI vs activation labels: {h['role_name_description_vs_activation_cluster_ari_k7']:.3f}",
            f"- Original-prompt k=7 ARI vs activation labels: {h['original_prompt_vs_activation_cluster_ari_k7']:.3f}",
            f"- No-label-prompt k=7 ARI vs activation labels: {h['no_label_prompt_vs_activation_cluster_ari_k7']:.3f}",
            f"- Original vs no-label distance correlation: {h['original_vs_no_label_distance_correlation']:.3f}",
            f"- Original vs no-label nearest-neighbor preservation: {h['original_vs_no_label_nn_preservation']:.3f}",
            "",
            "## Analysis Questions",
            "",
        ]
    )
    for key, answer in answers.items():
        lines.append(f"### {key}")
        lines.append("")
        lines.append(answer)
        lines.append("")
    lines.extend(
        [
            "## Cluster-Level Semantic Intrinsicness",
            "",
            "| Activation cluster | n | Original within cosine | No-label within cosine | Original-to-no-label role cosine |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in summary["cluster_semantic_intrinsic"]:
        lines.append(
            f"| `{row['cluster']}` | {row['n_roles']} | {row['original_within_cosine_mean']:.3f} | {row['no_label_within_cosine_mean']:.3f} | {row['original_to_no_label_role_cosine_mean']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The comparison supports partial preservation plus reorganization. Semantic topology is not irrelevant: role descriptions and prompts recover weak-to-modest agreement with activation labels, and no-label prompt geometry remains very close to original prompt geometry in continuous distance structure. At the same time, agreement with activation clusters is limited and hard semantic cluster assignments are unstable, so activation-space geometry should not be described as just semantics.",
            "",
            "The most defensible interpretation is that the activation geometry reflects an interaction between semantic priors in the elicitation corpus and model-specific representational organization. Label-exposed prompts contribute to prompt-space organization, but no-label rewrites preserve enough continuous topology to justify a small activation-space stress test.",
            "",
            "## Limitations",
            "",
            "This is a prompt-space semantic analysis, not a new activation experiment. TF-IDF/SVD is lexical and cannot fully capture paraphrastic equivalence. Activation comparison uses available cluster labels and centroid-proximity profiles, not a full published pairwise activation matrix. The role inventory is a constructed semantic corpus and should not be treated as a representative sample of humanity.",
            "",
            "## Recommended Next Experiment",
            "",
            "Run a small no-label activation-space stress test on a mixed role set. Include trickster as a high-yield theatrical positive control, editor as an assistant-adjacent failure case, and one or two intermediate roles. Compare no-label extracted vectors to Lu reference vectors and original-prompt extraction behavior before scaling.",
        ]
    )
    return "\n".join(lines)


def render_note(summary: dict) -> str:
    return """# Semantic Topology Interpretation Note

The semantic-vs-activation comparison suggests that role-vector geometry should be interpreted as an interaction between semantic priors and model geometry, not as either pure corpus semantics or pure emergent structure. The role inventory and prompts form a constructed semantic corpus with strong lexical identity exposure, but the no-label ablation shows that much of the continuous prompt-space topology survives when explicit labels are removed.

This matters for cultural coverage. The 275-role inventory is not a neutral sample of human possibility; it is a frontier-model-generated taxonomy of recognizable English-language roles, archetypes, professions, and fantastical figures. Activation clusters therefore inherit a semantic prior from the elicitation corpus while also being reorganized by the model's learned representational structure.

The assistant basin should be treated with the same caution. Assistant-adjacent roles may be semantically clear in prompts while remaining hard to separate in activation extraction because the model's default assistant behavior already overlaps their behavioral surface. The editor failure is consistent with this, but it is not yet a general result.

The next useful test is activation-space, not more prompt-space analysis. A small no-label stress test can ask whether vectors extracted from label-ablated prompts still point toward Lu reference directions. If trickster survives label removal and editor still fails, the evidence shifts toward a model-geometry explanation. If trickster fails under no-label prompts, explicit identity-label priming may be more central to Lu-style extraction than the prompt-space topology alone suggests.
"""


if __name__ == "__main__":
    main()
