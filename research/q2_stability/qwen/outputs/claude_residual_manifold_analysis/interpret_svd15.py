"""
SVD15 Residual Interpretation Script

Fits TruncatedSVD(n=15) on no-label prompt TF-IDF corpus (same hyperparameters
as run_residual_manifold_analysis.py), extracts vocabulary loadings per component,
maps personas to SVD scores, and correlates with canonical activation PCs.

Outputs used to write claude_svd15_interpretation_report.md.
"""

import json
import csv
import os
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import scipy.stats as stats

REPO = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(REPO, "research")):
    REPO = os.path.dirname(REPO)

NO_LABEL = os.path.join(REPO, "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl")
CANONICAL = os.path.join(REPO, "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv")
BF_FEAT = os.path.join(REPO, "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_bigfive_features.csv")
PERSONA_RANKINGS = os.path.join(REPO, "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_persona_residual_rankings.csv")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

N_TOP_TERMS = 15
N_TOP_PERSONAS = 12
N_COMPONENTS = 15


def norm(s):
    return s.replace(" ", "_").lower().strip()


def load_data():
    role_texts = defaultdict(list)
    with open(NO_LABEL) as f:
        for line in f:
            d = json.loads(line.strip())
            role_texts[norm(d["role"])].append(d["rewritten_prompt"])
    texts = {r: " ".join(v) for r, v in role_texts.items()}

    targets = {}
    clusters = {}
    with open(CANONICAL) as f:
        for row in csv.DictReader(f):
            targets[row["persona"]] = (
                float(row["activation_pc1"]),
                float(row["activation_pc2"]),
                float(row["activation_pc3"]),
            )
            clusters[row["persona"]] = row["activation_cluster"]

    bf_feats = {}
    with open(BF_FEAT) as f:
        reader = csv.DictReader(f)
        bf_cols = [c for c in reader.fieldnames if c.startswith("big5_")]
        for row in reader:
            bf_feats[row["persona"]] = {c: float(row[c]) for c in bf_cols}

    bigfive_resids = {}
    with open(PERSONA_RANKINGS) as f:
        for row in csv.DictReader(f):
            if row.get("activation_bigfive_mean_residual"):
                bigfive_resids[row["persona"]] = float(row["activation_bigfive_mean_residual"])

    return texts, targets, clusters, bf_feats, bigfive_resids


def main():
    print("Loading data...")
    texts, targets, clusters, bf_feats, bigfive_resids = load_data()

    personas = sorted(targets.keys() & bf_feats.keys())
    print(f"Personas: {len(personas)}")

    corpus = [texts.get(p, "") for p in personas]

    # Fit TF-IDF — exact same params as run_residual_manifold_analysis.py
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        max_features=8000,
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    vocab = np.array(vectorizer.get_feature_names_out())
    print(f"Vocabulary size: {len(vocab)}")

    # Fit SVD
    svd = TruncatedSVD(n_components=N_COMPONENTS, random_state=42)
    svd_coords = svd.fit_transform(tfidf_matrix)  # shape: (n_personas, n_components)
    components = svd.components_  # shape: (n_components, vocab_size)
    ev = svd.explained_variance_ratio_
    print(f"SVD explained variance by component: {[f'{v:.4f}' for v in ev]}")
    print(f"Total SVD EV: {ev.sum():.4f}")

    # ── Per-component vocabulary analysis ──────────────────────────────────────
    component_profiles = []
    for ci in range(N_COMPONENTS):
        loadings = components[ci]
        top_pos_idx = np.argsort(loadings)[::-1][:N_TOP_TERMS]
        top_neg_idx = np.argsort(loadings)[:N_TOP_TERMS]
        top_pos = [(vocab[i], round(float(loadings[i]), 4)) for i in top_pos_idx]
        top_neg = [(vocab[i], round(float(loadings[i]), 4)) for i in top_neg_idx]

        # Top/bottom personas by SVD score
        scores = svd_coords[:, ci]
        top_persona_idx = np.argsort(scores)[::-1][:N_TOP_PERSONAS]
        bot_persona_idx = np.argsort(scores)[:N_TOP_PERSONAS]
        top_personas = [(personas[i], round(float(scores[i]), 4), clusters.get(personas[i], "?")) for i in top_persona_idx]
        bot_personas = [(personas[i], round(float(scores[i]), 4), clusters.get(personas[i], "?")) for i in bot_persona_idx]

        # Correlation with activation PCs
        Y = np.array([[targets[p][j] for j in range(3)] for p in personas])
        corrs = [stats.pearsonr(scores, Y[:, j]) for j in range(3)]
        corr_vals = [(round(float(r), 4), round(float(p), 4)) for r, p in corrs]

        # Cluster composition at top/bottom
        top_cluster_counts = defaultdict(int)
        for idx in np.argsort(scores)[::-1][:30]:
            top_cluster_counts[clusters.get(personas[idx], "?")] += 1
        bot_cluster_counts = defaultdict(int)
        for idx in np.argsort(scores)[:30]:
            bot_cluster_counts[clusters.get(personas[idx], "?")] += 1

        component_profiles.append({
            "component": ci,
            "explained_variance": round(float(ev[ci]), 5),
            "top_pos_terms": top_pos,
            "top_neg_terms": top_neg,
            "top_personas": top_personas,
            "bot_personas": bot_personas,
            "activation_pc_corrs": {
                "pc1": corr_vals[0],
                "pc2": corr_vals[1],
                "pc3": corr_vals[2],
            },
            "top30_cluster_dist": dict(top_cluster_counts),
            "bot30_cluster_dist": dict(bot_cluster_counts),
        })

        print(f"\n=== SVD{ci} (EV={ev[ci]:.4f}) ===")
        print(f"  Top terms: {[t for t, _ in top_pos[:8]]}")
        print(f"  Bot terms: {[t for t, _ in top_neg[:8]]}")
        print(f"  Top personas: {[(p, c) for p,_,c in top_personas[:6]]}")
        print(f"  Bot personas: {[(p, c) for p,_,c in bot_personas[:6]]}")
        print(f"  Corr w/ PC1={corr_vals[0][0]}, PC2={corr_vals[1][0]}, PC3={corr_vals[2][0]}")

    # ── Correlation with BigFive per component ─────────────────────────────────
    bf_cols = sorted([c for c in list(bf_feats[personas[0]].keys())])
    bf_matrix = np.array([[bf_feats[p][c] for c in bf_cols] for p in personas])

    print("\n=== BigFive correlations with SVD components ===")
    bf_corrs_all = []
    for ci in range(N_COMPONENTS):
        scores = svd_coords[:, ci]
        row = {}
        for j, col in enumerate(bf_cols):
            r, pval = stats.pearsonr(scores, bf_matrix[:, j])
            row[col] = round(float(r), 4)
        bf_corrs_all.append(row)
        top_corr = sorted(row.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        print(f"  SVD{ci}: {top_corr}")

    # ── BigFive residual correlation with SVD scores ───────────────────────────
    # For personas with high BigFive residual, which SVD components correlate?
    print("\n=== SVD component correlations with BigFive residual ===")
    resid_scores = np.array([bigfive_resids.get(p, np.nan) for p in personas])
    valid = ~np.isnan(resid_scores)
    svd_resid_corrs = []
    for ci in range(N_COMPONENTS):
        r, pval = stats.pearsonr(svd_coords[valid, ci], resid_scores[valid])
        svd_resid_corrs.append((ci, round(float(r), 4), round(float(pval), 5)))
    svd_resid_corrs_sorted = sorted(svd_resid_corrs, key=lambda x: abs(x[1]), reverse=True)
    for ci, r, pval in svd_resid_corrs_sorted[:8]:
        ev_c = round(float(ev[ci]), 5)
        print(f"  SVD{ci} (EV={ev_c}): r={r}, p={pval}")

    # ── Write outputs ──────────────────────────────────────────────────────────

    # 1. Component profiles JSON
    profiles_path = os.path.join(OUT_DIR, "svd15_component_profiles.json")
    with open(profiles_path, "w") as f:
        json.dump({
            "date": "2026-05-28",
            "n_components": N_COMPONENTS,
            "total_ev": round(float(ev.sum()), 4),
            "vocab_size": len(vocab),
            "n_personas": len(personas),
            "bigfive_residual_correlations": [
                {"component": ci, "r_with_bf_residual": r, "p": pval}
                for ci, r, pval in svd_resid_corrs
            ],
            "components": component_profiles,
        }, f, indent=2)
    print(f"\nWritten: {profiles_path}")

    # 2. Per-persona SVD scores CSV
    scores_path = os.path.join(OUT_DIR, "svd15_persona_scores.csv")
    with open(scores_path, "w", newline="") as f:
        fieldnames = ["persona", "activation_cluster", "bigfive_residual"] + [f"svd{ci}" for ci in range(N_COMPONENTS)]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, p in enumerate(personas):
            row = {
                "persona": p,
                "activation_cluster": clusters.get(p, "?"),
                "bigfive_residual": round(bigfive_resids.get(p, 0.0), 2),
            }
            for ci in range(N_COMPONENTS):
                row[f"svd{ci}"] = round(float(svd_coords[i, ci]), 5)
            writer.writerow(row)
    print(f"Written: {scores_path}")

    # 3. BigFive correlations CSV
    bf_corr_path = os.path.join(OUT_DIR, "svd15_bigfive_correlations.csv")
    with open(bf_corr_path, "w", newline="") as f:
        fieldnames = ["component"] + bf_cols
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ci, row in enumerate(bf_corrs_all):
            r = {"component": f"svd{ci}"}
            r.update(row)
            writer.writerow(r)
    print(f"Written: {bf_corr_path}")

    return component_profiles, personas, clusters, svd_coords, bf_corrs_all, svd_resid_corrs_sorted, vocab, components, ev


if __name__ == "__main__":
    (component_profiles, personas, clusters, svd_coords,
     bf_corrs_all, svd_resid_corrs_sorted, vocab, components, ev) = main()
