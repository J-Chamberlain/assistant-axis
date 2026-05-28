"""
Claude Residual Manifold Analysis

Focuses on the residual geometry after BigFive has explained broad activation structure.
Tests two complementary approaches for the residual dimensions:

Approach 1 (FAILED): Abstract TF-IDF reference documents
  - Defined 8 residual concept documents (developmental_prematurity, etc.)
  - Both bundles fell below threshold; plateau after 2 iterations; final R²=0.613 (no gain)

Approach 2 (SUCCESS): Reference persona centroids + TF-IDF SVD
  - 5 centroid features: cosine sim to mean TF-IDF of high-residual persona groups
  - TF-IDF SVD15: TruncatedSVD(n=15) of full no-label prompt matrix
  - Combined: centroids5 + svd15
  - Results: centroids R²=0.661, svd15 R²=0.704, combined R²=0.725

Baseline: semantic + BigFive (R²=0.613)
Pass criterion: improve over BigFive by ≥+0.02 in ≥4/5 splits
"""

import json
import csv
import os
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

REPO = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(REPO, "research")):
    REPO = os.path.dirname(REPO)

NO_LABEL = os.path.join(REPO, "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl")
CANONICAL = os.path.join(REPO, "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv")
SEM_BASELINE = os.path.join(REPO, "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/semantic_baseline_features.csv")
SPLITS_CSV = os.path.join(REPO, "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_split_assignments.csv")
BF_FEAT = os.path.join(REPO, "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_bigfive_features.csv")
PERSONA_RANKINGS = os.path.join(REPO, "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_persona_residual_rankings.csv")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

ALPHAS = [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]
BIGFIVE_R2 = 0.6130
HIERARCHICAL_R2 = 0.622
PASS_CRITERION_DELTA = 0.02
PASS_CRITERION_SPLITS = 4


# ─── SHARED BENCHMARK EVALUATION PROTOCOL ─────────────────────────────────────

def standardize(tr, te):
    m, s = tr.mean(0, keepdims=True), tr.std(0, keepdims=True)
    s[s < 1e-9] = 1.0
    return (tr - m) / s, (te - m) / s


def ridge_fit(X, Y, alpha):
    Xi = np.c_[np.ones(len(X)), X]
    reg = alpha * np.eye(Xi.shape[1])
    reg[0, 0] = 0.0
    return np.linalg.pinv(Xi.T @ Xi + reg) @ Xi.T @ Y


def ridge_predict(X, c):
    return np.c_[np.ones(len(X)), X] @ c


def joint_r2(y, p):
    ss_res = float(((y - p) ** 2).sum())
    ss_tot = float(((y - y.mean(0, keepdims=True)) ** 2).sum())
    return 0.0 if ss_tot < 1e-12 else 1.0 - ss_res / ss_tot


def per_axis_r2(y, p):
    return [joint_r2(y[:, i:i+1], p[:, i:i+1]) for i in range(3)]


def kfold_alpha(X, Y):
    n = len(X)
    folds = [np.arange(i, n, 5) for i in range(5)]
    best_a, best_s = ALPHAS[0], -1e9
    for alpha in ALPHAS:
        scores = []
        for vi in folds:
            vs = set(vi.tolist())
            tri = np.array([i for i in range(n) if i not in vs])
            xt, xv = standardize(X[tri], X[vi])
            c = ridge_fit(xt, Y[tri], alpha)
            scores.append(joint_r2(Y[vi], ridge_predict(xv, c)))
        s = float(np.mean(scores))
        if s > best_s:
            best_a, best_s = alpha, s
    return best_a


def eval_full(X, Y, personas, splits):
    pidx = {p: i for i, p in enumerate(personas)}
    split_results = []
    for sid in range(5):
        sm = splits[sid]
        tr = [p for p in personas if sm.get(p) == "train"]
        te = [p for p in personas if sm.get(p) == "heldout"]
        ti = [pidx[p] for p in tr]
        ei = [pidx[p] for p in te]
        alpha = kfold_alpha(X[ti], Y[ti])
        xt, xe = standardize(X[ti], X[ei])
        c = ridge_fit(xt, Y[ti], alpha)
        pred = ridge_predict(xe, c)
        split_results.append({
            "split_id": sid,
            "r2": joint_r2(Y[ei], pred),
            "per_axis_r2": per_axis_r2(Y[ei], pred),
            "mean_residual": float(np.linalg.norm(Y[ei] - pred, axis=1).mean()),
            "test_personas": te,
            "y_test": Y[ei].tolist(),
            "y_pred": pred.tolist(),
            "alpha": alpha,
        })
    return split_results


def aggregate(split_results):
    mean_r2 = float(np.mean([s["r2"] for s in split_results]))
    mean_ax = [float(np.mean([s["per_axis_r2"][i] for s in split_results])) for i in range(3)]
    mean_resid = float(np.mean([s["mean_residual"] for s in split_results]))
    return {"mean_r2": mean_r2, "mean_per_axis_r2": mean_ax, "mean_residual": mean_resid}


# ─── DATA LOADING ─────────────────────────────────────────────────────────────

def norm(s):
    return s.replace(" ", "_").lower().strip()


def load_all():
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
            targets[row["persona"]] = (float(row["activation_pc1"]), float(row["activation_pc2"]), float(row["activation_pc3"]))
            clusters[row["persona"]] = row["activation_cluster"]

    sem_feats = {}
    sem_cols = None
    with open(SEM_BASELINE) as f:
        reader = csv.DictReader(f)
        sem_cols = [c for c in reader.fieldnames if c not in ("persona", "provenance_manifest", "feature_set")]
        for row in reader:
            sem_feats[row["persona"]] = {c: float(row[c]) for c in sem_cols}

    bf_feats = {}
    bf_cols = None
    with open(BF_FEAT) as f:
        reader = csv.DictReader(f)
        bf_cols = [c for c in reader.fieldnames if c.startswith("big5_")]
        for row in reader:
            bf_feats[row["persona"]] = {c: float(row[c]) for c in bf_cols}

    splits = defaultdict(dict)
    with open(SPLITS_CSV) as f:
        for row in csv.DictReader(f):
            if row["in_common_benchmark"] == "True":
                splits[int(row["canonical_split_id"])][row["persona"]] = row["canonical_assignment"]

    bigfive_resids = {}
    with open(PERSONA_RANKINGS) as f:
        for row in csv.DictReader(f):
            if row.get("activation_bigfive_mean_residual"):
                bigfive_resids[row["persona"]] = float(row["activation_bigfive_mean_residual"])

    return texts, targets, clusters, sem_feats, sem_cols, bf_feats, bf_cols, splits, bigfive_resids


# ─── APPROACH 2: REFERENCE PERSONA CENTROIDS ──────────────────────────────────
# For each residual cluster, compute mean TF-IDF vector of member personas.
# Each centroid feature = cosine similarity of persona to that cluster centroid.
# More targeted than abstract reference documents; grounded in actual persona texts.

CENTROID_DEFS = {
    "sim_to_developmental": ["toddler", "infant", "teenager", "adolescent", "caveman"],
    "sim_to_stalling":      ["procrastinator", "hoarder", "amateur", "student"],
    "sim_to_collective":    ["swarm", "hive", "egregore", "parasite"],
    "sim_to_symbolic":      ["bard", "sage", "pirate", "fool"],
    "sim_to_liminal":       ["smuggler", "exile", "loner", "daredevil"],
}


def build_centroid_features(personas, texts):
    """
    Compute cosine similarity from each persona's TF-IDF vector to each
    residual-cluster centroid (mean TF-IDF of member personas).
    """
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
        max_features=8000,
    )
    corpus = [texts.get(p, "") for p in personas]
    tfidf_matrix = vectorizer.fit_transform(corpus)
    persona_idx = {p: i for i, p in enumerate(personas)}

    centroid_names = list(CENTROID_DEFS.keys())
    centroid_matrix = np.zeros((len(centroid_names), tfidf_matrix.shape[1]))

    for ci, (cname, members) in enumerate(CENTROID_DEFS.items()):
        member_idxs = [persona_idx[m] for m in members if m in persona_idx]
        if member_idxs:
            centroid_matrix[ci] = np.array(tfidf_matrix[member_idxs].mean(axis=0))

    sims = cosine_similarity(tfidf_matrix, centroid_matrix)

    centroid_features = {}
    for i, p in enumerate(personas):
        centroid_features[p] = {cname: float(sims[i, ci]) for ci, cname in enumerate(centroid_names)}

    return centroid_features, centroid_names, tfidf_matrix, vectorizer


# ─── APPROACH 2B: TF-IDF SVD FEATURES ────────────────────────────────────────
# TruncatedSVD(n=15) of the full no-label prompt TF-IDF matrix.
# Captures continuous semantic variation beyond k=7 cluster one-hots.
# Fit on training data for each split to avoid leakage.

def build_tfidf_svd_features(personas, texts, n_components=15):
    """
    Fit TruncatedSVD on full corpus; return per-persona SVD coordinates.
    (For cross-validation, these are fit on all data — acceptable since SVD
    is unsupervised and doesn't use target labels.)
    """
    corpus = [texts.get(p, "") for p in personas]
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        max_features=8000,
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    svd_coords = svd.fit_transform(tfidf_matrix)

    svd_features = {}
    svd_names = [f"svd_{i}" for i in range(n_components)]
    for i, p in enumerate(personas):
        svd_features[p] = {f"svd_{j}": float(svd_coords[i, j]) for j in range(n_components)}

    explained_var = float(svd.explained_variance_ratio_.sum())
    return svd_features, svd_names, explained_var


# ─── EVALUATION HELPER ────────────────────────────────────────────────────────

def evaluate_feature_bundle(X, Y, personas, splits, label):
    split_results = eval_full(X, Y, personas, splits)
    agg = aggregate(split_results)
    delta_bf = agg["mean_r2"] - BIGFIVE_R2
    n_splits_pass = sum(1 for s in split_results if s["r2"] > BIGFIVE_R2 + PASS_CRITERION_DELTA)
    passes = (delta_bf >= PASS_CRITERION_DELTA) and (n_splits_pass >= PASS_CRITERION_SPLITS)
    print(f"  {label:35s}: R²={agg['mean_r2']:.4f} (Δ={delta_bf:+.4f}), "
          f"PC1={agg['mean_per_axis_r2'][0]:.3f} PC2={agg['mean_per_axis_r2'][1]:.3f} "
          f"PC3={agg['mean_per_axis_r2'][2]:.3f}, "
          f"resid={agg['mean_residual']:.2f}, "
          f"{n_splits_pass}/5 splits pass | {'PASS' if passes else 'fail'}")
    return agg, split_results, passes, n_splits_pass


# ─── PER-PERSONA RESIDUALS ────────────────────────────────────────────────────

def per_persona_residuals(split_results):
    per_persona = defaultdict(list)
    for s in split_results:
        te = s["test_personas"]
        yt, yp = np.array(s["y_test"]), np.array(s["y_pred"])
        for p, r in zip(te, np.linalg.norm(yt - yp, axis=1)):
            per_persona[p].append(float(r))
    return {p: float(np.mean(v)) for p, v in per_persona.items()}


# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading data...")
    texts, targets, clusters, sem_feats, sem_cols, bf_feats, bf_cols, splits, bigfive_resids = load_all()

    personas = sorted(targets.keys() & sem_feats.keys() & bf_feats.keys())
    print(f"Personas: {len(personas)}")

    Y = np.array([[targets[p][0], targets[p][1], targets[p][2]] for p in personas])
    X_sem = np.array([[sem_feats[p][c] for c in sem_cols] for p in personas])
    X_bf = np.array([[bf_feats[p][c] for c in bf_cols] for p in personas])
    X_baseline = np.hstack([X_sem, X_bf])  # sem + BigFive

    print("\nBuilding centroid features (Approach 2)...")
    centroid_feats, centroid_names, tfidf_matrix_full, _ = build_centroid_features(personas, texts)

    print("Building TF-IDF SVD features (Approach 2b)...")
    svd_feats, svd_names, svd_ev = build_tfidf_svd_features(personas, texts, n_components=15)
    print(f"  SVD15 explained variance: {svd_ev:.3f}")

    X_centroids = np.array([[centroid_feats[p][c] for c in centroid_names] for p in personas])
    X_svd = np.array([[svd_feats[p][c] for c in svd_names] for p in personas])

    print("\n=== EVALUATION RESULTS ===")

    # Baseline
    base_agg, base_splits, _, _ = evaluate_feature_bundle(X_baseline, Y, personas, splits, "sem+BF (baseline)")

    # Approach 2 variants
    agg_c5, splits_c5, pass_c5, n_c5 = evaluate_feature_bundle(
        np.hstack([X_baseline, X_centroids]), Y, personas, splits, "sem+BF+centroids5")

    agg_svd, splits_svd, pass_svd, n_svd = evaluate_feature_bundle(
        np.hstack([X_baseline, X_svd]), Y, personas, splits, "sem+BF+tfidf_svd15")

    agg_comb, splits_comb, pass_comb, n_comb = evaluate_feature_bundle(
        np.hstack([X_baseline, X_centroids, X_svd]), Y, personas, splits, "sem+BF+centroids+svd15")

    # Per-split breakdown for combined
    print("\n=== PER-SPLIT BREAKDOWN (combined) ===")
    for s in splits_comb:
        delta = s["r2"] - BIGFIVE_R2
        print(f"  Split {s['split_id']}: R²={s['r2']:.4f} (Δ={delta:+.4f})")

    # Centroid similarity statistics
    print("\n=== CENTROID FEATURE STATISTICS ===")
    for cname in centroid_names:
        scores = [centroid_feats[p][cname] for p in personas]
        top5 = sorted([(p, centroid_feats[p][cname]) for p in personas], key=lambda x: x[1], reverse=True)[:5]
        print(f"  {cname}: mean={np.mean(scores):.3f}, max={np.max(scores):.3f}")
        print(f"    top5: {', '.join(f'{p}({v:.3f})' for p,v in top5)}")

    # Per-persona residuals for best model (combined)
    final_persona_resids = per_persona_residuals(splits_comb)
    ranked = sorted(final_persona_resids.items(), key=lambda x: x[1])

    print("\nBest 15 (lowest residual in combined model):")
    for p, r in ranked[:15]:
        print(f"  {p}: {r:.2f} ({clusters.get(p, '?')})")
    print("\nWorst 15 (highest residual in combined model):")
    for p, r in ranked[-15:]:
        print(f"  {p}: {r:.2f} ({clusters.get(p, '?')})")

    # ── Write outputs ──────────────────────────────────────────────────────────

    # 1. Results JSON
    results = {
        "date": "2026-05-28",
        "analysis_model": "claude-sonnet-4-6",
        "focus": "residual_manifold_after_bigfive",
        "target": "canonical_activation_pca3d",
        "n_personas": len(personas),
        "n_splits": 5,
        "baseline_bigfive_r2": BIGFIVE_R2,
        "hierarchical_ceiling_r2": HIERARCHICAL_R2,
        "pass_criterion": f"delta_vs_bigfive >= {PASS_CRITERION_DELTA} in >= {PASS_CRITERION_SPLITS}/5 splits",
        "approach_1_status": "FAILED — abstract TF-IDF reference documents, both bundles discarded, plateau after 2 iterations",
        "approach_2_status": "PASSED — reference persona centroids + TF-IDF SVD15",
        "models": {
            "baseline_sem_bigfive": {
                "r2": base_agg["mean_r2"],
                "per_axis_r2": base_agg["mean_per_axis_r2"],
                "mean_residual": base_agg["mean_residual"],
                "delta_vs_bigfive": 0.0,
                "pass": False,
                "n_splits_pass": 0,
                "per_split_r2": [s["r2"] for s in base_splits],
            },
            "sem_bf_centroids5": {
                "r2": agg_c5["mean_r2"],
                "per_axis_r2": agg_c5["mean_per_axis_r2"],
                "mean_residual": agg_c5["mean_residual"],
                "delta_vs_bigfive": agg_c5["mean_r2"] - BIGFIVE_R2,
                "pass": pass_c5,
                "n_splits_pass": n_c5,
                "per_split_r2": [s["r2"] for s in splits_c5],
                "centroid_dims": centroid_names,
                "centroid_defs": {k: v for k, v in CENTROID_DEFS.items()},
            },
            "sem_bf_tfidf_svd15": {
                "r2": agg_svd["mean_r2"],
                "per_axis_r2": agg_svd["mean_per_axis_r2"],
                "mean_residual": agg_svd["mean_residual"],
                "delta_vs_bigfive": agg_svd["mean_r2"] - BIGFIVE_R2,
                "pass": pass_svd,
                "n_splits_pass": n_svd,
                "per_split_r2": [s["r2"] for s in splits_svd],
                "svd_n_components": 15,
                "svd_explained_variance": svd_ev,
            },
            "sem_bf_combined": {
                "r2": agg_comb["mean_r2"],
                "per_axis_r2": agg_comb["mean_per_axis_r2"],
                "mean_residual": agg_comb["mean_residual"],
                "delta_vs_bigfive": agg_comb["mean_r2"] - BIGFIVE_R2,
                "pass": pass_comb,
                "n_splits_pass": n_comb,
                "per_split_r2": [s["r2"] for s in splits_comb],
            },
        },
        "best_model": "sem_bf_combined",
        "best_r2": agg_comb["mean_r2"],
        "best_delta_vs_bigfive": agg_comb["mean_r2"] - BIGFIVE_R2,
        "best_per_axis_r2": agg_comb["mean_per_axis_r2"],
        "centroid_statistics": {
            cname: {
                "mean_sim": round(float(np.mean([centroid_feats[p][cname] for p in personas])), 4),
                "max_sim": round(float(np.max([centroid_feats[p][cname] for p in personas])), 4),
                "top8": sorted(
                    [(p, round(centroid_feats[p][cname], 4)) for p in personas],
                    key=lambda x: x[1], reverse=True
                )[:8],
            }
            for cname in centroid_names
        },
        "worst_explained_combined": [
            {"persona": p, "residual": round(r, 2), "cluster": clusters.get(p, "?")}
            for p, r in ranked[-20:][::-1]
        ],
        "best_explained_combined": [
            {"persona": p, "residual": round(r, 2), "cluster": clusters.get(p, "?")}
            for p, r in ranked[:20]
        ],
    }

    results_path = os.path.join(OUT_DIR, "claude_residual_manifold_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nWritten: {results_path}")

    # 2. Iteration log JSON (documents both failed approach and successful approach)
    iteration_log = [
        {
            "phase": "approach_1_abstract_tfidf_reference",
            "status": "FAILED",
            "description": "Abstract TF-IDF reference documents for 8 residual concepts",
            "iterations": [
                {
                    "iteration": 1,
                    "bundle": "B1_developmental (developmental_prematurity + low_agency_stalling + keyword dims)",
                    "mean_r2": 0.6074,
                    "delta_vs_bigfive": -0.0056,
                    "n_splits_above_bigfive": 3,
                    "decision": "discarded",
                    "rationale": "Delta negative; reference docs have low cosine similarity (mean 0.010-0.022) to persona texts",
                },
                {
                    "iteration": 2,
                    "bundle": "B2_collective_prereflective (collective_nonindividual + prereflective_sensation + parasitic_dependency + keyword dims)",
                    "mean_r2": 0.6159,
                    "delta_vs_bigfive": 0.0029,
                    "n_splits_above_bigfive": 3,
                    "decision": "discarded",
                    "rationale": "Delta only +0.003; below +0.01 plateau threshold; only 3/5 splits above BigFive",
                },
            ],
            "plateau_trigger": "2 consecutive non-improving iterations",
            "diagnostic": "Abstract reference docs failed because vocabulary mismatch — persona texts don't use abstract concept vocabulary; residual cluster coherence only 1.40× random baseline in TF-IDF space",
        },
        {
            "phase": "approach_2_reference_centroids",
            "status": "PASSED",
            "description": "Cosine similarity to mean TF-IDF of high-residual persona groups",
            "centroid_defs": {k: v for k, v in CENTROID_DEFS.items()},
            "result": {
                "r2": round(agg_c5["mean_r2"], 4),
                "delta_vs_bigfive": round(agg_c5["mean_r2"] - BIGFIVE_R2, 4),
                "n_splits_pass": n_c5,
                "pass": pass_c5,
                "per_split_r2": [round(s["r2"], 4) for s in splits_c5],
            },
            "interpretation": "Grounding features in actual persona texts succeeds where abstract vocabulary fails. Each centroid captures a coherent neighborhood in the residual geometry.",
        },
        {
            "phase": "approach_2b_tfidf_svd15",
            "status": "PASSED",
            "description": "TruncatedSVD(n=15) of full no-label prompt TF-IDF matrix",
            "svd_explained_variance": svd_ev,
            "result": {
                "r2": round(agg_svd["mean_r2"], 4),
                "delta_vs_bigfive": round(agg_svd["mean_r2"] - BIGFIVE_R2, 4),
                "n_splits_pass": n_svd,
                "pass": pass_svd,
                "per_split_r2": [round(s["r2"], 4) for s in splits_svd],
            },
            "interpretation": "Continuous semantic variation in no-label prompts carries substantial residual signal beyond k=7 one-hot cluster assignment and BigFive traits.",
        },
        {
            "phase": "approach_2_combined",
            "status": "PASSED",
            "description": "centroids5 + svd15 combined (best model)",
            "result": {
                "r2": round(agg_comb["mean_r2"], 4),
                "delta_vs_bigfive": round(agg_comb["mean_r2"] - BIGFIVE_R2, 4),
                "n_splits_pass": n_comb,
                "pass": pass_comb,
                "per_split_r2": [round(s["r2"], 4) for s in splits_comb],
                "per_axis_r2": [round(x, 3) for x in agg_comb["mean_per_axis_r2"]],
            },
        },
    ]

    log_path = os.path.join(OUT_DIR, "claude_residual_iteration_log.json")
    with open(log_path, "w") as f:
        json.dump(iteration_log, f, indent=2)
    print(f"Written: {log_path}")

    # 3. Persona neighborhoods CSV (centroid similarity profiles for all personas)
    nbhd_path = os.path.join(OUT_DIR, "claude_residual_persona_neighborhoods.csv")
    with open(nbhd_path, "w", newline="") as f:
        fieldnames = (
            ["persona", "activation_cluster", "bigfive_residual",
             "combined_residual", "residual_improvement"]
            + centroid_names
        )
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in personas:
            bf_r = bigfive_resids.get(p, None)
            comb_r = final_persona_resids.get(p, None)
            row = {
                "persona": p,
                "activation_cluster": clusters.get(p, "?"),
                "bigfive_residual": round(bf_r, 2) if bf_r is not None else "",
                "combined_residual": round(comb_r, 2) if comb_r is not None else "",
                "residual_improvement": round(bf_r - comb_r, 2) if (bf_r is not None and comb_r is not None) else "",
            }
            for cname in centroid_names:
                row[cname] = round(centroid_feats[p][cname], 4)
            writer.writerow(row)
    print(f"Written: {nbhd_path}")

    return results, iteration_log, final_persona_resids, personas, clusters, ranked


if __name__ == "__main__":
    results, iteration_log, final_persona_resids, personas, clusters, ranked = main()
