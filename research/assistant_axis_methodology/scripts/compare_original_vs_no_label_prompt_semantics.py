#!/usr/bin/env python3
"""Offline semantic comparison for original vs no-label role prompts.

Uses a local TF-IDF + SVD fallback because neither sentence-transformers nor
scikit-learn is required. No external APIs are called.
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
INPUT_JSONL = (
    ROOT
    / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
)
FULL_RANKING = ROOT / "visualizations/full_ranking.csv"
OUT_DIR = ROOT / "research/assistant_axis_methodology/no_label_prompt_ablation"
OUT_JSON = OUT_DIR / "original_vs_no_label_semantic_comparison.json"
OUT_MD = OUT_DIR / "original_vs_no_label_semantic_comparison.md"
OUT_DISPLACEMENT = OUT_DIR / "original_vs_no_label_role_displacement.csv"
OUT_NEIGHBORS = OUT_DIR / "original_vs_no_label_neighbors.csv"
OUT_CLUSTERS = OUT_DIR / "original_vs_no_label_cluster_assignments.csv"

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
    out = list(tokens)
    out += [tokens[i] + "_" + tokens[i + 1] for i in range(len(tokens) - 1)]
    return out


def build_tfidf(docs: list[str], max_features: int = 5000) -> tuple[np.ndarray, list[str]]:
    doc_terms = [ngrams(tokenize(doc)) for doc in docs]
    df = Counter()
    for terms in doc_terms:
        df.update(set(terms))
    vocab = [
        term
        for term, _ in sorted(
            df.items(), key=lambda kv: (-kv[1], kv[0])
        )
        if df[term] >= 2
    ][:max_features]
    idx = {term: i for i, term in enumerate(vocab)}
    mat = np.zeros((len(docs), len(vocab)), dtype=np.float64)
    n_docs = len(docs)
    idf = np.array([math.log((1 + n_docs) / (1 + df[t])) + 1 for t in vocab])
    for row, terms in enumerate(doc_terms):
        counts = Counter(t for t in terms if t in idx)
        if not counts:
            continue
        total = sum(counts.values())
        for term, count in counts.items():
            mat[row, idx[term]] = (count / total) * idf[idx[term]]
    return l2norm(mat), vocab


def l2norm(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def svd_reduce(mat: np.ndarray, n_components: int = 50) -> np.ndarray:
    if mat.shape[1] <= n_components:
        return mat
    u, s, _ = np.linalg.svd(mat, full_matrices=False)
    return l2norm(u[:, :n_components] * s[:n_components])


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def pairwise_cosine(mat: np.ndarray) -> np.ndarray:
    m = l2norm(mat)
    return m @ m.T


def nearest_neighbors(mat: np.ndarray, roles: list[str]) -> dict[str, str]:
    sim = pairwise_cosine(mat)
    out = {}
    for i, role in enumerate(roles):
        row = sim[i].copy()
        row[i] = -np.inf
        out[role] = roles[int(np.argmax(row))]
    return out


def upper_triangle_values(mat: np.ndarray) -> np.ndarray:
    idx = np.triu_indices_from(mat, k=1)
    return mat[idx]


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) == 0:
        return 0.0
    aa = a - a.mean()
    bb = b - b.mean()
    denom = np.linalg.norm(aa) * np.linalg.norm(bb)
    return float(np.dot(aa, bb) / denom) if denom else 0.0


def kmeans(mat: np.ndarray, k: int, max_iter: int = 100) -> list[int]:
    # Deterministic farthest-point initialization.
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
    return labels.tolist()


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


def load_activation_labels(roles: list[str]) -> dict[str, str]:
    if not FULL_RANKING.exists():
        return {}
    out = {}
    with FULL_RANKING.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            role = row.get("character") or row.get("persona") or row.get("role")
            label = row.get("cluster_label") or row.get("cluster")
            if role and label:
                out[role] = label
    return {role: out[role] for role in roles if role in out}


def main() -> None:
    records = [json.loads(line) for line in INPUT_JSONL.read_text().splitlines() if line]
    by_role = defaultdict(list)
    for rec in records:
        by_role[rec["role"]].append(rec)
    roles = sorted(by_role)
    original_docs = []
    rewritten_docs = []
    for role in roles:
        role_records = sorted(by_role[role], key=lambda r: r["prompt_index"])
        original_docs.append(" ".join(r["original_prompt"] for r in role_records))
        rewritten_docs.append(" ".join(r["rewritten_prompt"] for r in role_records))

    all_docs = original_docs + rewritten_docs
    tfidf, vocab = build_tfidf(all_docs)
    tfidf_svd = svd_reduce(tfidf, n_components=min(50, tfidf.shape[1], tfidf.shape[0] - 1))
    orig_tfidf = tfidf[: len(roles)]
    rew_tfidf = tfidf[len(roles) :]
    orig_svd = tfidf_svd[: len(roles)]
    rew_svd = tfidf_svd[len(roles) :]

    # Prompt-level similarities use prompt docs rather than role docs.
    prompt_docs = []
    prompt_pairs = []
    for rec in records:
        prompt_docs.append(rec["original_prompt"])
        prompt_docs.append(rec["rewritten_prompt"])
        prompt_pairs.append((rec["role"], rec["prompt_index"]))
    prompt_tfidf, _ = build_tfidf(prompt_docs, max_features=5000)
    prompt_sims = []
    for i, (role, prompt_index) in enumerate(prompt_pairs):
        prompt_sims.append(
            {
                "role": role,
                "prompt_index": prompt_index,
                "tfidf_cosine": cosine(prompt_tfidf[2 * i], prompt_tfidf[2 * i + 1]),
            }
        )

    role_sims = [
        {
            "role": role,
            "tfidf_cosine": cosine(orig_tfidf[i], rew_tfidf[i]),
            "svd_cosine": cosine(orig_svd[i], rew_svd[i]),
        }
        for i, role in enumerate(roles)
    ]
    displacement = [
        {
            "role": r["role"],
            "tfidf_cosine": r["tfidf_cosine"],
            "svd_cosine": r["svd_cosine"],
            "tfidf_displacement": 1 - r["tfidf_cosine"],
            "svd_displacement": 1 - r["svd_cosine"],
        }
        for r in role_sims
    ]
    most_changed = sorted(displacement, key=lambda r: -r["svd_displacement"])[:25]
    least_changed = sorted(displacement, key=lambda r: r["svd_displacement"])[:25]

    orig_nn = nearest_neighbors(orig_svd, roles)
    rew_nn = nearest_neighbors(rew_svd, roles)
    nn_rows = [
        {
            "role": role,
            "original_nearest_neighbor": orig_nn[role],
            "rewritten_nearest_neighbor": rew_nn[role],
            "nearest_neighbor_preserved": orig_nn[role] == rew_nn[role],
        }
        for role in roles
    ]
    nn_preservation = sum(r["nearest_neighbor_preserved"] for r in nn_rows) / len(nn_rows)

    orig_sim = pairwise_cosine(orig_svd)
    rew_sim = pairwise_cosine(rew_svd)
    distance_corr = pearson(
        1 - upper_triangle_values(orig_sim), 1 - upper_triangle_values(rew_sim)
    )

    cluster_results = {}
    cluster_assignments = {"role": roles}
    for k in [5, 7, 10]:
        lo = kmeans(orig_svd, k)
        lr = kmeans(rew_svd, k)
        cluster_results[str(k)] = {
            "ari_original_vs_no_label": adjusted_rand_index(lo, lr),
            "nmi_original_vs_no_label": normalized_mutual_info(lo, lr),
        }
        cluster_assignments[f"original_k{k}"] = lo
        cluster_assignments[f"no_label_k{k}"] = lr

    activation_labels = load_activation_labels(roles)
    activation_comparison = {}
    if activation_labels:
        labels = [activation_labels.get(role, "missing") for role in roles]
        for k in [5, 7, 10]:
            activation_comparison[str(k)] = {
                "ari_activation_vs_original_semantic": adjusted_rand_index(
                    labels, cluster_assignments[f"original_k{k}"]
                ),
                "nmi_activation_vs_original_semantic": normalized_mutual_info(
                    labels, cluster_assignments[f"original_k{k}"]
                ),
                "ari_activation_vs_no_label_semantic": adjusted_rand_index(
                    labels, cluster_assignments[f"no_label_k{k}"]
                ),
                "nmi_activation_vs_no_label_semantic": normalized_mutual_info(
                    labels, cluster_assignments[f"no_label_k{k}"]
                ),
            }

    comparison = {
        "date": "2026-05-27",
        "model_used": "GPT-5.5",
        "method": "offline_tfidf_svd_fallback",
        "embedding_methods": ["tfidf", "tfidf_svd"],
        "sentence_transformers_available": False,
        "sklearn_available": False,
        "input_jsonl": str(INPUT_JSONL.relative_to(ROOT)),
        "n_roles": len(roles),
        "n_prompts": len(records),
        "vocab_size": len(vocab),
        "prompt_similarity": summarize([r["tfidf_cosine"] for r in prompt_sims]),
        "role_similarity_tfidf": summarize([r["tfidf_cosine"] for r in role_sims]),
        "role_similarity_svd": summarize([r["svd_cosine"] for r in role_sims]),
        "nearest_neighbor_preservation_fraction": nn_preservation,
        "pairwise_distance_correlation_svd": distance_corr,
        "cluster_preservation": cluster_results,
        "activation_cluster_comparison": activation_comparison,
        "most_changed_roles": most_changed,
        "least_changed_roles": least_changed,
    }
    OUT_JSON.write_text(json.dumps(comparison, indent=2, ensure_ascii=False) + "\n")
    OUT_MD.write_text(render_markdown(comparison) + "\n")
    write_csvs(displacement, nn_rows, cluster_assignments)
    print(json.dumps(comparison, indent=2)[:4000])


def summarize(values: list[float]) -> dict:
    vals = sorted(float(x) for x in values)
    return {
        "min": vals[0],
        "p05": percentile(vals, 0.05),
        "p25": percentile(vals, 0.25),
        "median": percentile(vals, 0.5),
        "mean": sum(vals) / len(vals),
        "p75": percentile(vals, 0.75),
        "p95": percentile(vals, 0.95),
        "max": vals[-1],
    }


def percentile(vals: list[float], p: float) -> float:
    idx = p * (len(vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - idx) + vals[hi] * (idx - lo)


def write_csvs(displacement: list[dict], nn_rows: list[dict], clusters: dict) -> None:
    with OUT_DISPLACEMENT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(displacement[0]))
        writer.writeheader()
        writer.writerows(displacement)
    with OUT_NEIGHBORS.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(nn_rows[0]))
        writer.writeheader()
        writer.writerows(nn_rows)
    with OUT_CLUSTERS.open("w", newline="") as f:
        fieldnames = list(clusters)
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, role in enumerate(clusters["role"]):
            writer.writerow({key: clusters[key][i] for key in fieldnames})


def render_markdown(c: dict) -> str:
    lines = [
        "# Original vs No-Label Prompt Semantic Comparison",
        "",
        "## Method",
        "",
        "No local `sentence-transformers` or `scikit-learn` installation was available, so this analysis uses a local TF-IDF representation with unigrams and bigrams plus a NumPy SVD reduction. This is an offline prompt-space topology audit, not an activation-space test.",
        "",
        "## Headline Results",
        "",
        f"- Roles analyzed: {c['n_roles']}",
        f"- Prompts analyzed: {c['n_prompts']}",
        f"- Prompt-level TF-IDF original-vs-rewrite cosine median: {c['prompt_similarity']['median']:.3f}",
        f"- Role-level TF-IDF cosine median: {c['role_similarity_tfidf']['median']:.3f}",
        f"- Role-level TF-IDF+SVD cosine median: {c['role_similarity_svd']['median']:.3f}",
        f"- Nearest-neighbor preservation fraction: {c['nearest_neighbor_preservation_fraction']:.3f}",
        f"- Pairwise distance correlation, SVD role space: {c['pairwise_distance_correlation_svd']:.3f}",
        "",
        "## Cluster Preservation",
        "",
        "| k | ARI original vs no-label | NMI original vs no-label |",
        "|---:|---:|---:|",
    ]
    for k, vals in c["cluster_preservation"].items():
        lines.append(
            f"| {k} | {vals['ari_original_vs_no_label']:.3f} | {vals['nmi_original_vs_no_label']:.3f} |"
        )
    if c["activation_cluster_comparison"]:
        lines.extend(["", "## Comparison to Existing Activation-Space Labels", ""])
        lines.append(
            "Existing activation-space labels from `visualizations/full_ranking.csv` were available. These comparisons are exploratory because prompt-space clusters and activation-space clusters are not expected to be identical objects."
        )
        lines.append("")
        lines.append("| k | ARI activation vs original | ARI activation vs no-label | NMI activation vs original | NMI activation vs no-label |")
        lines.append("|---:|---:|---:|---:|---:|")
        for k, vals in c["activation_cluster_comparison"].items():
            lines.append(
                f"| {k} | {vals['ari_activation_vs_original_semantic']:.3f} | {vals['ari_activation_vs_no_label_semantic']:.3f} | {vals['nmi_activation_vs_original_semantic']:.3f} | {vals['nmi_activation_vs_no_label_semantic']:.3f} |"
            )
    lines.extend(["", "## Most Changed Roles", ""])
    lines.append("| Role | SVD displacement | SVD cosine | TF-IDF cosine |")
    lines.append("|---|---:|---:|---:|")
    for row in c["most_changed_roles"][:20]:
        lines.append(
            f"| `{row['role']}` | {row['svd_displacement']:.3f} | {row['svd_cosine']:.3f} | {row['tfidf_cosine']:.3f} |"
        )
    lines.extend(["", "## Least Changed Roles", ""])
    lines.append("| Role | SVD displacement | SVD cosine | TF-IDF cosine |")
    lines.append("|---|---:|---:|---:|")
    for row in c["least_changed_roles"][:20]:
        lines.append(
            f"| `{row['role']}` | {row['svd_displacement']:.3f} | {row['svd_cosine']:.3f} | {row['tfidf_cosine']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The no-label rewrite preserves a substantial amount of prompt-space semantic topology if role-level cosine and pairwise distance correlation remain high, but any loss of nearest-neighbor or cluster preservation indicates that explicit labels contribute materially to the original prompt-space organization. This analysis does not establish what will happen in activation space. It motivates a small no-label activation stress test only if the rewritten prompt space remains coherent enough to be a fair intervention.",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
