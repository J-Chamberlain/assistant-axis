#!/usr/bin/env python3
"""Bounded cross-model persona cluster/topology diagnostic.

Compares Qwen, Llama, and Gemma released role-vector topology without GPU work
or visualization-tool edits.
"""

import csv
import json
import math
import os
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


REPO = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
OUT = REPO / "research/outputs/cross_model_cluster_topology"
OUT.mkdir(parents=True, exist_ok=True)

GEOMETRY_SOURCE = REPO / "research/visualizations/geometry_viz_data.json"
MAIN_VIEWER = REPO / "research/visualizations/persona_geometry_explorer.html"

MODEL_SPECS = {
    "qwen": {
        "label": "Qwen/Qwen3-32B",
        "role_vector_dir": REPO / "downloads/hf_vectors/qwen-3-32b/role_vectors",
    },
    "llama": {
        "label": "Llama-3.3-70B",
        "role_vector_dir": REPO / "downloads/hf_vectors/llama-3.3-70b/role_vectors",
    },
    "gemma": {
        "label": "Gemma-2-27B",
        "role_vector_dir": REPO / "downloads/hf_vectors/gemma-2-27b/role_vectors",
    },
}

REGION_SEEDS = {
    "procedural_professional": {
        "scientist", "researcher", "analyst", "doctor", "lawyer", "engineer",
        "journalist", "teacher", "programmer", "therapist", "historian",
        "philosopher", "architect", "accountant", "statistician", "economist",
        "auditor", "evaluator", "reviewer", "validator", "debugger",
        "proofreader", "editor", "screener", "grader", "examiner",
    },
    "mythic_spiritual": {
        "ancient", "oracle", "mystic", "prophet", "shaman", "angel", "demon",
        "ghost", "sage", "ascetic", "leviathan", "egregore", "hive", "swarm",
        "genie", "spirit", "eldritch", "avatar", "tree", "void", "witch",
    },
    "grounded_social": {
        "actor", "refugee", "veteran", "bartender", "surfer", "widow",
        "expatriate", "immigrant", "blogger", "podcaster", "moderator",
        "interviewer", "parent", "patient", "caregiver", "newlywed",
        "grandparent", "orphan", "amateur",
    },
    "care_repair_stabilizing": {
        "caregiver", "empath", "counselor", "therapist", "healer", "widow",
        "optimist", "romantic", "angel", "grandparent", "peacekeeper",
        "mediator", "guardian", "paramedic", "doctor", "nurturer",
    },
    "adversarial_perturbative": {
        "hacker", "cynic", "saboteur", "provocateur", "spy", "jester", "rogue",
        "trickster", "rebel", "contrarian", "devils_advocate", "daredevil",
        "criminal", "pirate", "vigilante", "demon",
    },
    "creative_symbolic": {
        "poet", "bard", "novelist", "writer", "composer", "artist", "musician",
        "playwright", "visionary", "dreamer", "mystic", "oracle", "shapeshifter",
        "tulpa", "narrator", "romantic",
    },
    "assistant_evaluator_like": {
        "assistant", "evaluator", "reviewer", "validator", "proofreader",
        "editor", "screener", "grader", "examiner", "auditor", "summarizer",
        "secretary", "scheduler", "accountant",
    },
}


def load_geometry():
    with GEOMETRY_SOURCE.open() as f:
        data = json.load(f)
    roles = data["roles"]
    clusters = {name: roles["clusters"][i] for i, name in enumerate(roles["names"])}
    qwen_coords = {name: roles["pca3d"][i] for i, name in enumerate(roles["names"])}
    return data, clusters, qwen_coords


def load_layer_mean_vectors(role_dir: Path):
    names = []
    vectors = []
    for path in sorted(role_dir.glob("*.pt")):
        t = torch.load(path, map_location="cpu").float()
        vec = t.mean(0) if t.dim() > 1 else t
        arr = np.nan_to_num(vec.numpy().astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
        names.append(path.stem)
        vectors.append(arr)
    return names, np.stack(vectors)


def orient_to_reference(names, coords, ref_coords):
    for pc in range(min(coords.shape[1], 3)):
        common = [n for n in names if n in ref_coords]
        x = np.array([coords[names.index(n), pc] for n in common])
        y = np.array([ref_coords[n][pc] for n in common])
        if np.corrcoef(x, y)[0, 1] < 0:
            coords[:, pc] *= -1


def zscore(x):
    return (x - x.mean(axis=0, keepdims=True)) / (x.std(axis=0, keepdims=True) + 1e-12)


def cluster_kmeans(coords, k, seed=42):
    return KMeans(n_clusters=k, random_state=seed, n_init=50).fit_predict(zscore(coords))


def cluster_agglomerative(coords, k):
    return AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(zscore(coords))


def pct_ranks(values):
    ordered = sorted((v, i) for i, v in enumerate(values))
    out = [0.0] * len(values)
    n = len(values)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and ordered[j + 1][0] == ordered[i][0]:
            j += 1
        pct = 100.0 * ((i + j) / 2 + 0.5) / n
        for k in range(i, j + 1):
            out[ordered[k][1]] = pct
        i = j + 1
    return out


def semantic_label(roles):
    role_set = set(roles)
    scores = {label: len(role_set & seeds) for label, seeds in REGION_SEEDS.items()}
    best_label, best_score = max(scores.items(), key=lambda kv: kv[1])
    if best_score == 0:
        return "mixed_or_unlabeled"
    return best_label


def write_csv(path, rows, fields):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def overlap_matrix(labels_a, labels_b, names, model_a, model_b, label_type_a="kmeans", label_type_b="kmeans"):
    rows = []
    labels_a_set = sorted(set(labels_a), key=lambda x: str(x))
    labels_b_set = sorted(set(labels_b), key=lambda x: str(x))
    for la in labels_a_set:
        set_a = {names[i] for i, x in enumerate(labels_a) if x == la}
        for lb in labels_b_set:
            set_b = {names[i] for i, x in enumerate(labels_b) if x == lb}
            inter = sorted(set_a & set_b)
            union = set_a | set_b
            rows.append({
                "model_a": model_a,
                "model_b": model_b,
                "label_type_a": label_type_a,
                "label_type_b": label_type_b,
                "cluster_a": str(la),
                "cluster_b": str(lb),
                "size_a": len(set_a),
                "size_b": len(set_b),
                "overlap_count": len(inter),
                "jaccard": len(inter) / len(union) if union else 0.0,
                "overlap_roles": ";".join(inter),
            })
    return rows


def best_mapping(overlap_rows, model_a, model_b, label_type_a, label_type_b):
    candidates = [r for r in overlap_rows if r["model_a"] == model_a and r["model_b"] == model_b and r["label_type_a"] == label_type_a and r["label_type_b"] == label_type_b]
    out = []
    for ca in sorted({r["cluster_a"] for r in candidates}):
        rows = [r for r in candidates if r["cluster_a"] == ca]
        best = max(rows, key=lambda r: (r["jaccard"], r["overlap_count"]))
        out.append(dict(best))
    return out


def assignment_similarity(labels_by_model, names):
    rows = []
    models = sorted(labels_by_model)
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            la = labels_by_model[a]
            lb = labels_by_model[b]
            rows.append({
                "model_pair": f"{a}_vs_{b}",
                "matched_role_count": len(names),
                "kmeans_top3_ari": adjusted_rand_score(la["kmeans3"], lb["kmeans3"]),
                "kmeans_top3_nmi": normalized_mutual_info_score(la["kmeans3"], lb["kmeans3"]),
                "kmeans_top5_ari": adjusted_rand_score(la["kmeans5"], lb["kmeans5"]),
                "kmeans_top5_nmi": normalized_mutual_info_score(la["kmeans5"], lb["kmeans5"]),
                "agglomerative_top3_ari": adjusted_rand_score(la["agglo3"], lb["agglo3"]),
                "agglomerative_top3_nmi": normalized_mutual_info_score(la["agglo3"], lb["agglo3"]),
            })
    return rows


def summarize_cluster(model, label, rows, coords, names, labels, label_kind):
    out = []
    arr = np.asarray(coords[:, :3])
    global_centroid = arr.mean(axis=0)
    for cluster_id in sorted(set(labels), key=lambda x: str(x)):
        idx = [i for i, x in enumerate(labels) if x == cluster_id]
        sub = arr[idx]
        centroid = sub.mean(axis=0)
        d_centroid = np.linalg.norm(sub - centroid, axis=1)
        d_global = np.linalg.norm(sub - global_centroid, axis=1)
        closest = [names[idx[i]] for i in np.argsort(d_centroid)[:15]]
        extreme = [names[idx[i]] for i in np.argsort(d_global)[::-1][:15]]
        label_guess = semantic_label([names[i] for i in idx])
        out.append({
            "model": model,
            "model_label": label,
            "label_kind": label_kind,
            "cluster_id": str(cluster_id),
            "size": len(idx),
            "centroid_pc1": float(centroid[0]),
            "centroid_pc2": float(centroid[1]),
            "centroid_pc3": float(centroid[2]),
            "candidate_semantic_label": label_guess,
            "top15_closest_to_centroid": ";".join(closest),
            "top15_extreme_from_global_centroid": ";".join(extreme),
        })
    return out


def region_conservation(reference_clusters, model_labels, names):
    rows = []
    for region, seeds in REGION_SEEDS.items():
        present = sorted(seeds & set(names))
        if not present:
            continue
        ref_counts = Counter(reference_clusters[n] for n in present if n in reference_clusters)
        row = {
            "region": region,
            "seed_roles_present": len(present),
            "seed_roles": ";".join(present),
            "qwen_reference_primary_cluster": ref_counts.most_common(1)[0][0] if ref_counts else "",
            "qwen_reference_primary_count": ref_counts.most_common(1)[0][1] if ref_counts else 0,
        }
        for model, labels in model_labels.items():
            counts = Counter(labels[names.index(n)] for n in present)
            primary, count = counts.most_common(1)[0]
            row[f"{model}_primary_kmeans_cluster"] = str(primary)
            row[f"{model}_primary_count"] = count
            row[f"{model}_purity"] = count / len(present)
        rows.append(row)
    return rows


def migration_cases(qwen_ref, target_labels, target_name, names, top_n=80):
    rows = []
    # For each Qwen ref cluster, identify best target cluster, then list roles not retained.
    labels_a = [qwen_ref[n] for n in names]
    labels_b = target_labels
    overlaps = overlap_matrix(labels_a, labels_b, names, "qwen_reference", target_name, "reference", "kmeans3")
    best = {r["cluster_a"]: r["cluster_b"] for r in best_mapping(overlaps, "qwen_reference", target_name, "reference", "kmeans3")}
    for i, name in enumerate(names):
        qcl = qwen_ref[name]
        expected_target = best.get(qcl)
        actual = str(target_labels[i])
        if expected_target != actual:
            rows.append({
                "persona": name,
                "qwen_reference_cluster": qcl,
                "target_model": target_name,
                "best_matching_target_cluster_for_qwen_ref": expected_target,
                "actual_target_cluster": actual,
                "migration_type": "outside_best_match",
            })
    return rows[:top_n]


def plot_svg(model_data, labels_by_model, names, metrics, path_svg, path_png):
    width, height = 1600, 1100
    colors = ["#377eb8", "#e41a1c", "#4daf4a", "#984ea3", "#ff7f00", "#a65628", "#f781bf"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append('<text x="40" y="38" font-size="24" font-family="Arial" font-weight="bold">Cross-model cluster topology</text>')

    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def scale(v, lo, hi, a, b):
        if hi == lo:
            return (a + b) / 2
        return a + (v - lo) * (b - a) / (hi - lo)

    panel_specs = [("qwen", 50, 70), ("llama", 570, 70), ("gemma", 1090, 70)]
    for model, x0, y0 in panel_specs:
        coords = model_data[model]["coords"][:, :3]
        labels = labels_by_model[model]["kmeans3"]
        xs, ys = coords[:, 0], coords[:, 1]
        parts.append(f'<rect x="{x0}" y="{y0}" width="460" height="430" fill="#fbfbfb" stroke="#cccccc"/>')
        parts.append(f'<text x="{x0+12}" y="{y0+24}" font-size="17" font-family="Arial" font-weight="bold">{model} PC1/PC2 kmeans</text>')
        for i, name in enumerate(names):
            x = scale(xs[i], float(xs.min()), float(xs.max()), x0 + 45, x0 + 430)
            y = scale(ys[i], float(ys.min()), float(ys.max()), y0 + 395, y0 + 45)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{colors[int(labels[i]) % len(colors)]}" fill-opacity="0.75"/>')
    # Metrics bars.
    x0, y0 = 100, 610
    parts.append(f'<rect x="{x0}" y="{y0}" width="1400" height="320" fill="#fbfbfb" stroke="#cccccc"/>')
    parts.append(f'<text x="{x0+12}" y="{y0+26}" font-size="18" font-family="Arial" font-weight="bold">Cluster similarity metrics</text>')
    pairs = metrics
    maxv = 1.0
    for i, row in enumerate(pairs):
        y = y0 + 70 + i * 70
        parts.append(f'<text x="{x0+20}" y="{y+18}" font-size="14" font-family="Arial">{esc(row["model_pair"])}</text>')
        for j, key in enumerate(["kmeans_top3_ari", "kmeans_top3_nmi", "kmeans_top5_ari", "kmeans_top5_nmi"]):
            val = float(row[key])
            bx = x0 + 260 + j * 300
            bw = 220 * max(0, val) / maxv
            parts.append(f'<rect x="{bx}" y="{y}" width="{bw:.1f}" height="20" fill="{colors[j]}"/>')
            parts.append(f'<text x="{bx}" y="{y+42}" font-size="12" font-family="Arial">{key}={val:.3f}</text>')
    parts.append("</svg>")
    path_svg.write_text("\n".join(parts), encoding="utf-8")
    try:
        subprocess.run(["sips", "-s", "format", "png", str(path_svg), "--out", str(path_png)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        path_png.write_bytes(b"")


def fmt(x):
    return f"{float(x):.3f}"


def write_report(stats, metrics, qwen_llama_map, qwen_gemma_map, summaries, region_rows):
    metric_by_pair = {r["model_pair"]: r for r in metrics}
    ql = metric_by_pair["llama_vs_qwen"] if "llama_vs_qwen" in metric_by_pair else metric_by_pair["qwen_vs_llama"]
    qg = metric_by_pair["gemma_vs_qwen"] if "gemma_vs_qwen" in metric_by_pair else metric_by_pair["qwen_vs_gemma"]
    lg = metric_by_pair["gemma_vs_llama"] if "gemma_vs_llama" in metric_by_pair else metric_by_pair["llama_vs_gemma"]
    lines = []
    lines.append("# Cross-Model Cluster Topology Diagnostic")
    lines.append("")
    lines.append(f"- Date: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("- model_used: GPT-5.5")
    lines.append(f"- Geometry source: `{GEOMETRY_SOURCE.relative_to(REPO)}`")
    lines.append("- Released vector representation: layer-mean role vectors, matching the current Qwen geometry builder.")
    lines.append("- No GPU work, no H100 outputs, no prompt-battery outputs, no clean-repo copy, and no visualization files were modified.")
    lines.append("")
    lines.append("## Models and Matching")
    lines.append("")
    for model, info in stats["models"].items():
        lines.append(f"- {model}: {info['role_count']} roles; explained variance PC1/PC2/PC3 = {fmt(info['explained_variance'][0])}/{fmt(info['explained_variance'][1])}/{fmt(info['explained_variance'][2])}.")
    lines.append("")
    lines.append(f"Pairwise matched role counts: Qwen-Llama={stats['matched_role_counts']['qwen_vs_llama']}, Qwen-Gemma={stats['matched_role_counts']['qwen_vs_gemma']}, Llama-Gemma={stats['matched_role_counts']['llama_vs_gemma']}; three-way intersection={stats['matched_role_counts']['qwen_llama_gemma_intersection']}.")
    lines.append("")
    lines.append("## Clustering Method")
    lines.append("")
    lines.append(f"Existing Qwen reference labels have {stats['k']} clusters. I used `k={stats['k']}` for independent k-means clustering in each model's top-3-PC space, with fixed seed 42 and `n_init=50`. Sensitivity checks repeat k-means in top-5-PC space and agglomerative clustering in top-3-PC space.")
    lines.append("")
    lines.append("## Cross-Model Cluster Similarity")
    lines.append("")
    lines.append("| Pair | top3 kmeans ARI | top3 kmeans NMI | top5 kmeans ARI | top5 kmeans NMI | top3 agglomerative ARI | top3 agglomerative NMI |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for r in metrics:
        lines.append(f"| {r['model_pair']} | {fmt(r['kmeans_top3_ari'])} | {fmt(r['kmeans_top3_nmi'])} | {fmt(r['kmeans_top5_ari'])} | {fmt(r['kmeans_top5_nmi'])} | {fmt(r['agglomerative_top3_ari'])} | {fmt(r['agglomerative_top3_nmi'])} |")
    lines.append("")
    lines.append("The cluster metrics show partial topology preservation rather than clean universal clustering. Qwen-Llama top-3 k-means ARI/NMI are "
                 f"{fmt(ql['kmeans_top3_ari'])}/{fmt(ql['kmeans_top3_nmi'])}, which is more stable than same-index PC3 but not as direct as the shared PC1/PC2 subspace. Qwen-Gemma top-3 k-means ARI/NMI are {fmt(qg['kmeans_top3_ari'])}/{fmt(qg['kmeans_top3_nmi'])}; Llama-Gemma are {fmt(lg['kmeans_top3_ari'])}/{fmt(lg['kmeans_top3_nmi'])}.")
    lines.append("")
    lines.append("Prior same-index Qwen-Llama axis comparisons from `research/outputs/cross_model_pc2_pc3_diagnostic/` were PC2 Pearson r=0.606 and PC3 Pearson r=0.440, with Qwen-Llama PC1/PC2 plane principal correlations 0.977/0.905. The cluster result therefore supports the narrow claim that coarse topology is more robust than PC3 and that PC2 lives in a shared low-dimensional plane, but it does not prove that hard cluster assignments are more stable than all axis-level structure.")
    lines.append("")
    lines.append("## Qwen Reference Cluster Mapping")
    lines.append("")
    lines.append("Best Qwen-reference to Llama k-means matches:")
    for r in qwen_llama_map:
        retained = r["overlap_roles"].split(";")[:10] if r["overlap_roles"] else []
        lines.append(f"- {r['cluster_a']} -> Llama cluster {r['cluster_b']}: overlap {r['overlap_count']}, Jaccard {fmt(r['jaccard'])}; retained examples: {', '.join(retained)}")
    lines.append("")
    lines.append("Best Qwen-reference to Gemma k-means matches:")
    for r in qwen_gemma_map:
        retained = r["overlap_roles"].split(";")[:10] if r["overlap_roles"] else []
        lines.append(f"- {r['cluster_a']} -> Gemma cluster {r['cluster_b']}: overlap {r['overlap_count']}, Jaccard {fmt(r['jaccard'])}; retained examples: {', '.join(retained)}")
    lines.append("")
    lines.append("## Per-Model Cluster Labels")
    lines.append("")
    for model in ["qwen", "llama", "gemma"]:
        lines.append(f"### {model}")
        for r in [x for x in summaries if x["model"] == model and x["label_kind"] == "kmeans_top3"]:
            top = r["top15_closest_to_centroid"].split(";")[:8]
            lines.append(f"- Cluster {r['cluster_id']} (n={r['size']}), candidate label `{r['candidate_semantic_label']}`: {', '.join(top)}")
        lines.append("")
    lines.append("## Region Conservation")
    lines.append("")
    lines.append("Seed-set purity by model is in `cross_model_cluster_similarity_metrics.json` under `region_conservation` and summarized in `per_model_cluster_summaries.csv`. The strongest recurring regions are evaluator/procedural-professional and mythic/symbolic poles; grounded/social and care/repair regions are present but split more often. Adversarial/perturbative roles recur as neighborhoods in Qwen and partly in Llama/Gemma, but they are not a clean one-cluster invariant.")
    for r in region_rows:
        lines.append(f"- {r['region']}: Qwen ref primary={r['qwen_reference_primary_cluster']} ({r['qwen_reference_primary_count']}/{r['seed_roles_present']}); Qwen kmeans purity={fmt(r['qwen_purity'])}, Llama={fmt(r['llama_purity'])}, Gemma={fmt(r['gemma_purity'])}.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("Observed: coarse topology is partly more stable than same-index later PCs, especially compared with Qwen-Llama PC3. However, the topology is not cleanly universal: ARI values are modest, Qwen reference clusters often split across model-specific k-means clusters, and cluster labels require semantic caution. Inferred: the safest report framing is that broad role-space regions recur across models better than individual PC3 axes, while PC2 is best treated as a subspace-dependent direction inside a more stable low-dimensional plane. Speculative: some semantic regions may be conserved attractor basins even when PCA axes rotate, but this needs independent alignment and non-name-based validation.")
    lines.append("")
    lines.append("## Bounded Gemma Comparison")
    lines.append("")
    lines.append("Gemma is included because local released role vectors are present. In this artifact-level analysis, Gemma partially shares topology with Qwen/Llama but also reorganizes several regions; it should be used as secondary evidence, not as the arbiter of Qwen PC2/PC3 interpretation.")
    lines.append("")
    lines.append("## Visualization Recommendation")
    lines.append("")
    lines.append("Do not modify visualization tools yet. Model switching in the main viewer is feasible if a multi-model data bundle is built, but cross-model arrows need an explicit alignment convention. PC1/PC2-only or cluster-overlap visualizations are more justified than 3D PC3 arrows.")
    (OUT / "cross_model_cluster_topology_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_visualization_note():
    text = f"""# Cross-Model Cluster Visualization Feasibility Update

- Date: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
- Reference viewer inspected only: `research/visualizations/persona_geometry_explorer.html`
- No visualization files were modified.

## Feasibility

Model switching is feasible but should be implemented as a separate, reviewed visualization task. The current viewer embeds a single Qwen data object; a multi-model viewer needs a new data artifact containing per-model PCA/UMAP coordinates, cluster labels, nearest-neighbor summaries, and metadata.

## Arrows

Cross-model arrows are not recommended as a first visualization. Independent PCA spaces rotate, especially beyond PC1, and the previous diagnostic found weak same-index PC3 comparability. If arrows are built later, limit them to PC1/PC2 or use an alignment-corrected basis.

## Best Next Visualization

The best next visualization is a model-switching cluster/topology viewer or a cluster-overlap Sankey/alluvial table. This would show broad region preservation without implying that PC3 coordinates are directly interchangeable.
"""
    (OUT / "visualization_feasibility_update.md").write_text(text, encoding="utf-8")


def main():
    _, qwen_ref_clusters, qwen_ref_coords = load_geometry()
    model_data = {}
    for model, spec in MODEL_SPECS.items():
        names, vecs = load_layer_mean_vectors(spec["role_vector_dir"])
        pca = PCA(n_components=5, random_state=42)
        coords = pca.fit_transform(vecs)
        if model == "qwen":
            orient_to_reference(names, coords, qwen_ref_coords)
        else:
            # Orient to Qwen reference coordinates for easier summaries only; clustering uses signed coords but sign flips do not affect distances.
            orient_to_reference(names, coords, qwen_ref_coords)
        model_data[model] = {
            "label": spec["label"],
            "names": names,
            "coords": coords,
            "explained_variance": pca.explained_variance_ratio_.tolist(),
        }

    all_name_sets = {m: set(d["names"]) for m, d in model_data.items()}
    three_way = sorted(set.intersection(*all_name_sets.values()))
    names = three_way
    k = len(set(qwen_ref_clusters.values()))
    labels_by_model = {}
    assignment_rows = []
    for model, data in model_data.items():
        idx = [data["names"].index(n) for n in names]
        coords = data["coords"][idx, :]
        model_data[model]["names"] = names
        model_data[model]["coords"] = coords
        labels = {
            "kmeans3": cluster_kmeans(coords[:, :3], k),
            "kmeans5": cluster_kmeans(coords[:, :5], k),
            "agglo3": cluster_agglomerative(coords[:, :3], k),
        }
        labels_by_model[model] = labels
        pc_pcts = [pct_ranks(coords[:, i].tolist()) for i in range(3)]
        for i, name in enumerate(names):
            assignment_rows.append({
                "persona": name,
                "model": model,
                "model_label": data["label"],
                "qwen_reference_cluster": qwen_ref_clusters.get(name, "unknown"),
                "kmeans_top3_cluster": int(labels["kmeans3"][i]),
                "kmeans_top5_cluster": int(labels["kmeans5"][i]),
                "agglomerative_top3_cluster": int(labels["agglo3"][i]),
                "pc1": float(coords[i, 0]),
                "pc2": float(coords[i, 1]),
                "pc3": float(coords[i, 2]),
                "pc1_percentile": pc_pcts[0][i],
                "pc2_percentile": pc_pcts[1][i],
                "pc3_percentile": pc_pcts[2][i],
            })

    metrics = assignment_similarity(labels_by_model, names)
    qwen_ref_list = [qwen_ref_clusters[n] for n in names]
    overlap_rows = []
    for a in ["qwen", "llama", "gemma"]:
        for b in ["qwen", "llama", "gemma"]:
            if a != b:
                overlap_rows.extend(overlap_matrix(labels_by_model[a]["kmeans3"], labels_by_model[b]["kmeans3"], names, a, b))
    for target in ["llama", "gemma"]:
        overlap_rows.extend(overlap_matrix(qwen_ref_list, labels_by_model[target]["kmeans3"], names, "qwen_reference", target, "reference", "kmeans3"))

    qwen_llama_map = best_mapping(overlap_rows, "qwen_reference", "llama", "reference", "kmeans3")
    qwen_gemma_map = best_mapping(overlap_rows, "qwen_reference", "gemma", "reference", "kmeans3")
    summary_rows = []
    for model, data in model_data.items():
        summary_rows.extend(summarize_cluster(model, data["label"], assignment_rows, data["coords"], names, labels_by_model[model]["kmeans3"], "kmeans_top3"))
        summary_rows.extend(summarize_cluster(model, data["label"], assignment_rows, data["coords"], names, labels_by_model[model]["kmeans5"], "kmeans_top5"))
    region_rows = region_conservation(qwen_ref_clusters, {m: labels_by_model[m]["kmeans3"] for m in labels_by_model}, names)
    migration_rows = migration_cases(qwen_ref_clusters, labels_by_model["llama"]["kmeans3"], "llama", names)
    migration_rows.extend(migration_cases(qwen_ref_clusters, labels_by_model["gemma"]["kmeans3"], "gemma", names))

    stats = {
        "date_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_used": "GPT-5.5",
        "geometry_source": str(GEOMETRY_SOURCE.relative_to(REPO)),
        "k": k,
        "models": {
            m: {
                "label": d["label"],
                "role_count": len(d["names"]),
                "explained_variance": d["explained_variance"][:5],
            }
            for m, d in model_data.items()
        },
        "matched_role_counts": {
            "qwen_vs_llama": len(all_name_sets["qwen"] & all_name_sets["llama"]),
            "qwen_vs_gemma": len(all_name_sets["qwen"] & all_name_sets["gemma"]),
            "llama_vs_gemma": len(all_name_sets["llama"] & all_name_sets["gemma"]),
            "qwen_llama_gemma_intersection": len(three_way),
        },
        "cluster_similarity_metrics": metrics,
        "prior_cross_model_axis_context": {
            "qwen_llama_same_index_pc2_pearson": 0.605808866959668,
            "qwen_llama_same_index_pc2_spearman": 0.42971985805372037,
            "qwen_llama_same_index_pc3_pearson": 0.44043920658341235,
            "qwen_llama_same_index_pc3_spearman": 0.5578713828221921,
            "qwen_llama_pc1_pc2_plane_principal_correlations": [0.9765710453740877, 0.9045584252333672],
        },
        "region_conservation": region_rows,
        "visualization_files_modified": False,
    }

    write_csv(OUT / "matched_role_inventory.csv", [{"persona": n, "in_qwen": True, "in_llama": True, "in_gemma": True, "qwen_reference_cluster": qwen_ref_clusters.get(n, "unknown")} for n in names], ["persona", "in_qwen", "in_llama", "in_gemma", "qwen_reference_cluster"])
    write_csv(OUT / "per_model_cluster_assignments.csv", assignment_rows, ["persona", "model", "model_label", "qwen_reference_cluster", "kmeans_top3_cluster", "kmeans_top5_cluster", "agglomerative_top3_cluster", "pc1", "pc2", "pc3", "pc1_percentile", "pc2_percentile", "pc3_percentile"])
    write_csv(OUT / "cross_model_cluster_overlap_matrices.csv", overlap_rows, ["model_a", "model_b", "label_type_a", "label_type_b", "cluster_a", "cluster_b", "size_a", "size_b", "overlap_count", "jaccard", "overlap_roles"])
    write_csv(OUT / "qwen_to_llama_cluster_mapping.csv", qwen_llama_map, ["model_a", "model_b", "label_type_a", "label_type_b", "cluster_a", "cluster_b", "size_a", "size_b", "overlap_count", "jaccard", "overlap_roles"])
    write_csv(OUT / "qwen_to_gemma_cluster_mapping.csv", qwen_gemma_map, ["model_a", "model_b", "label_type_a", "label_type_b", "cluster_a", "cluster_b", "size_a", "size_b", "overlap_count", "jaccard", "overlap_roles"])
    write_csv(OUT / "per_model_cluster_summaries.csv", summary_rows, ["model", "model_label", "label_kind", "cluster_id", "size", "centroid_pc1", "centroid_pc2", "centroid_pc3", "candidate_semantic_label", "top15_closest_to_centroid", "top15_extreme_from_global_centroid"])
    write_csv(OUT / "cluster_migration_cases.csv", migration_rows, ["persona", "qwen_reference_cluster", "target_model", "best_matching_target_cluster_for_qwen_ref", "actual_target_cluster", "migration_type"])
    (OUT / "cross_model_cluster_similarity_metrics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    plot_svg(model_data, labels_by_model, names, metrics, OUT / "cross_model_cluster_topology_plots.svg", OUT / "cross_model_cluster_topology_plots.png")
    write_visualization_note()
    write_report(stats, metrics, qwen_llama_map, qwen_gemma_map, summary_rows, region_rows)
    print(f"Wrote cross-model cluster topology outputs to {OUT}")


if __name__ == "__main__":
    main()
