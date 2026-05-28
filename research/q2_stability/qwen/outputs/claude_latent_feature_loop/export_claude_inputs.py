#!/usr/bin/env python3
"""Export Claude latent-feature loop inputs for Codex transfer comparison.

Deterministically reconstructs (from fixed random seeds) the exact feature
matrix, target coordinates, split assignments, predictions, and residuals
used in the Claude latent-feature loop, and writes them to clean CSV files.

Does NOT rerun the full loop — only reconstructs the inputs and outputs
needed for an apples-to-apples Codex comparison.

Provenance:
  analysis_model: claude-sonnet-4-6
  script_author_model: claude-sonnet-4-6
  date: 2026-05-28
  purpose: export for Codex transfer comparison
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.linear_model import Ridge
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[5]
OUT_DIR = Path(__file__).parent

PROVENANCE = {
    "analysis_model": "claude-sonnet-4-6",
    "script_author_model": "claude-sonnet-4-6",
    "orchestration_agent": "claude-code",
    "provider": "anthropic",
    "date": "2026-05-28",
    "random_seed": 42,
    "cv_strategy": "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)",
    "stratification": "gemma_activation_cluster_label",
    "target_description": (
        "Pseudo-PCA3D: PCA(n_components=3, random_state=42) on StandardScaler-normalized "
        "275x7 Qwen cluster-cosine matrix. NOT identical to full Qwen activation-space PCA."
    ),
    "best_feature_set": "F1: TF-IDF (SVD-50) + BigFive (5 dims) = 55 features total",
    "note": (
        "BigFive profiles were assigned by LLM during Paper 1, not human raters. "
        "They may reflect the assigning model's role stereotypes. "
        "The pseudo-PCA3D target uses Qwen cluster cosines as a proxy — "
        "it is not identical to Codex canonical activation PCA. "
        "Transfer testing against Codex's target is required before claims generalize."
    ),
}


# ---------------------------------------------------------------------------
# Data loading (identical to run_claude_latent_feature_loop.py)
# ---------------------------------------------------------------------------

def _norm(name: str) -> str:
    return name.replace(" ", "_").lower().strip()


def load_data() -> dict:
    gemma_rows = list(csv.DictReader(open(ROOT / "visualizations/full_ranking.csv")))
    roles = [_norm(r["character"]) for r in gemma_rows]
    n = len(roles)

    gemma_proj_raw = np.array([float(r["axis_projection_layer22"]) for r in gemma_rows])
    gemma_cluster = [r["cluster_label"] for r in gemma_rows]

    # Qwen cosines
    qdir_rows = list(csv.DictReader(open(
        ROOT / "research/cluster_analysis/qwen_cluster_directionality.csv"
    )))
    cosine_cols = [c for c in qdir_rows[0].keys() if c.startswith("cos_to_")]
    qdir_by_role = {}
    for r in qdir_rows:
        qdir_by_role[_norm(r["persona"])] = r
        qdir_by_role[_norm(r["persona"]).replace(" ", "_")] = r

    qwen_cosines = np.zeros((n, len(cosine_cols)))
    for i, role in enumerate(roles):
        row = qdir_by_role.get(role) or qdir_by_role.get(role.replace("_", " "))
        if row:
            for j, col in enumerate(cosine_cols):
                try:
                    qwen_cosines[i, j] = float(row[col])
                except (ValueError, KeyError):
                    pass

    # BigFive
    big5_data = json.load(open(ROOT / "visualizations/bigfive_profiles.json"))
    big5_dims = ["Agreeableness", "Conscientiousness", "Extraversion", "Neuroticism", "Openness"]
    big5_mat = np.zeros((n, 5))
    for i, role in enumerate(roles):
        if role in big5_data:
            for j, dim in enumerate(big5_dims):
                big5_mat[i, j] = big5_data[role].get(dim, 3)

    # DarkTriad
    dark3_data = json.load(open(ROOT / "visualizations/dark_triad_profiles.json"))
    dark3_dims = ["Machiavellianism", "Narcissism", "Psychopathy"]
    dark3_mat = np.zeros((n, 3))
    for i, role in enumerate(roles):
        if role in dark3_data:
            for j, dim in enumerate(dark3_dims):
                dark3_mat[i, j] = dark3_data[role].get(dim, 3)

    # Semantic cluster
    topo = json.load(open(
        ROOT / "research/assistant_axis_methodology/deep_semantic_topology_analysis.json"
    ))
    sem_cluster_by_role = {}
    for cluster_info in topo["no_label_k7_clusters"]:
        for r in cluster_info["all_roles"]:
            sem_cluster_by_role[_norm(r)] = cluster_info["cluster_id"]

    sem_cluster_ids = sorted(set(sem_cluster_by_role.values()))
    sem_cluster_labels = [sem_cluster_by_role.get(r, sem_cluster_ids[0]) for r in roles]

    # Anchor/bridge
    stable_anchors, sem_bridges, sem_anchors = set(), set(), set()
    for row in csv.DictReader(open(
            ROOT / "research/assistant_axis_methodology/stable_anchor_roles.csv")):
        stable_anchors.add(_norm(row["role"]))
    for row in csv.DictReader(open(
            ROOT / "research/assistant_axis_methodology/semantic_bridge_roles.csv")):
        sem_bridges.add(_norm(row["role"]))
    for row in csv.DictReader(open(
            ROOT / "research/assistant_axis_methodology/cluster_anchor_roles.csv")):
        sem_anchors.add(_norm(row["role"]))

    anchor_mat = np.zeros((n, 3))
    for i, role in enumerate(roles):
        anchor_mat[i] = [
            1.0 if role in stable_anchors else 0.0,
            1.0 if role in sem_bridges else 0.0,
            1.0 if role in sem_anchors else 0.0,
        ]

    # No-label prompts
    nl_by_role = {}
    with open(ROOT / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl") as f:
        for line in f:
            rec = json.loads(line.strip())
            r = _norm(rec["role"])
            if r not in nl_by_role:
                nl_by_role[r] = rec["rewritten_prompt"]
    nl_docs = [nl_by_role.get(role, role) for role in roles]

    return {
        "roles": roles, "n": n,
        "gemma_proj_raw": gemma_proj_raw,
        "gemma_cluster": gemma_cluster,
        "qwen_cosines": qwen_cosines,
        "cosine_cols": cosine_cols,
        "big5_mat": big5_mat, "big5_dims": big5_dims,
        "dark3_mat": dark3_mat, "dark3_dims": dark3_dims,
        "sem_cluster_labels": sem_cluster_labels,
        "anchor_mat": anchor_mat,
        "nl_docs": nl_docs,
    }


# ---------------------------------------------------------------------------
# Feature construction (identical seeds/params to run_claude_latent_feature_loop.py)
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "by",
    "for", "from", "in", "into", "is", "it", "its", "of", "on", "or",
    "that", "the", "their", "to", "was", "were", "who", "with", "you",
    "your", "has", "have", "this", "they", "we", "i", "me",
}


def build_tfidf(docs: list[str], n_components: int = 50) -> np.ndarray:
    def tokenize(text):
        toks = re.findall(r"[a-z]+", text.lower())
        return [t for t in toks if t not in STOPWORDS and len(t) > 2]

    token_lists = [tokenize(d) for d in docs]
    vocab: dict[str, int] = {}
    for tl in token_lists:
        for tok in tl:
            if tok not in vocab:
                vocab[tok] = len(vocab)

    n, v = len(docs), len(vocab)
    mat = np.zeros((n, v))
    for i, tl in enumerate(token_lists):
        tf = Counter(tl)
        total = sum(tf.values()) or 1
        for tok, cnt in tf.items():
            mat[i, vocab[tok]] = cnt / total

    df = (mat > 0).sum(axis=0)
    idf = np.log((n + 1) / (df + 1)) + 1
    mat = mat * idf
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1
    mat = mat / norms

    svd = TruncatedSVD(n_components=min(n_components, v - 1, n - 1), random_state=42)
    return svd.fit_transform(mat)


def build_pca3d(qwen_cosines: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(qwen_cosines)
    pca = PCA(n_components=3, random_state=42)
    coords = pca.fit_transform(scaled)
    return coords, pca.explained_variance_ratio_, pca.components_


# ---------------------------------------------------------------------------
# Reconstruct predictions and residuals for best model (TF-IDF + BigFive)
# ---------------------------------------------------------------------------

def reconstruct_cv(X: np.ndarray, y_pca: np.ndarray, y_gemma: np.ndarray,
                   cluster_labels: list[str]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns (pca3d_preds, gemma_preds, fold_assignments)."""
    cluster_ids = sorted(set(cluster_labels))
    strat = [cluster_ids.index(c) for c in cluster_labels]
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    pca3d_preds = np.zeros_like(y_pca)
    gemma_preds = np.zeros_like(y_gemma)
    fold_assignments = np.zeros(len(cluster_labels), dtype=int)

    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, strat)):
        sc = StandardScaler()
        X_tr = sc.fit_transform(X[train_idx])
        X_te = sc.transform(X[test_idx])
        Ridge(alpha=1.0).fit(X_tr, y_pca[train_idx]).predict(X_te)
        pca3d_preds[test_idx] = Ridge(alpha=1.0).fit(X_tr, y_pca[train_idx]).predict(X_te)
        gemma_preds[test_idx] = Ridge(alpha=1.0).fit(X_tr, y_gemma[train_idx]).predict(X_te)
        fold_assignments[test_idx] = fold_idx

    return pca3d_preds, gemma_preds, fold_assignments


# ---------------------------------------------------------------------------
# Main export
# ---------------------------------------------------------------------------

def main() -> None:
    print("Loading data...")
    data = load_data()
    roles = data["roles"]
    n = data["n"]

    print("Building TF-IDF features...")
    tfidf = build_tfidf(data["nl_docs"], n_components=50)

    print("Building pseudo-PCA3D targets...")
    y_pca, ev_ratios, pca_components = build_pca3d(data["qwen_cosines"])

    # Normalize Gemma projection
    g_raw = data["gemma_proj_raw"]
    y_gemma = 2 * (g_raw - g_raw.min()) / (g_raw.max() - g_raw.min()) - 1

    # Best feature set: TF-IDF + BigFive
    X_best = np.hstack([tfidf, data["big5_mat"]])
    print(f"Best feature matrix shape: {X_best.shape}")

    print("Reconstructing CV splits and predictions...")
    pca3d_preds, gemma_preds, fold_ids = reconstruct_cv(
        X_best, y_pca, y_gemma, data["gemma_cluster"]
    )

    pca3d_residuals = np.linalg.norm(y_pca - pca3d_preds, axis=1)
    gemma_residuals = np.abs(y_gemma - gemma_preds)

    # -----------------------------------------------------------------------
    # 1. claude_feature_matrix.csv
    # Columns: persona, tfidf_svd_00..49, big5_agreeableness, ..., big5_openness
    # -----------------------------------------------------------------------
    print("Writing claude_feature_matrix.csv...")
    tfidf_cols = [f"tfidf_svd_{i:02d}" for i in range(tfidf.shape[1])]
    big5_cols = [f"big5_{d.lower()}" for d in data["big5_dims"]]
    feature_cols = tfidf_cols + big5_cols

    with open(OUT_DIR / "claude_feature_matrix.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["persona"] + feature_cols)
        for i, role in enumerate(roles):
            row = [role] + list(X_best[i])
            writer.writerow(row)

    # -----------------------------------------------------------------------
    # 2. claude_target_coordinates.csv
    # Columns: persona, pc1, pc2, pc3, gemma_axis_proj_raw, gemma_axis_proj_norm,
    #          qwen_cos_to_editor, ..., qwen_cos_to_podcaster, gemma_cluster
    # -----------------------------------------------------------------------
    print("Writing claude_target_coordinates.csv...")
    cosine_cols = data["cosine_cols"]
    with open(OUT_DIR / "claude_target_coordinates.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "persona", "pseudo_pc1", "pseudo_pc2", "pseudo_pc3",
            "gemma_axis_proj_raw", "gemma_axis_proj_norm",
        ] + cosine_cols + ["gemma_cluster"])
        for i, role in enumerate(roles):
            row = (
                [role, round(y_pca[i, 0], 6), round(y_pca[i, 1], 6), round(y_pca[i, 2], 6),
                 round(float(g_raw[i]), 4), round(float(y_gemma[i]), 6)]
                + [round(float(data["qwen_cosines"][i, j]), 6) for j in range(len(cosine_cols))]
                + [data["gemma_cluster"][i]]
            )
            writer.writerow(row)

    # -----------------------------------------------------------------------
    # 3. claude_split_assignments.csv
    # Columns: persona, fold_id (0-4), split (train/test per fold)
    # -----------------------------------------------------------------------
    print("Writing claude_split_assignments.csv...")
    with open(OUT_DIR / "claude_split_assignments.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "persona", "test_fold", "gemma_cluster",
            "predicted_pc1", "predicted_pc2", "predicted_pc3",
            "predicted_gemma_norm",
            "actual_pc1", "actual_pc2", "actual_pc3",
            "actual_gemma_norm",
            "residual_pca3d", "residual_gemma",
        ])
        for i, role in enumerate(roles):
            writer.writerow([
                role,
                int(fold_ids[i]),
                data["gemma_cluster"][i],
                round(float(pca3d_preds[i, 0]), 6),
                round(float(pca3d_preds[i, 1]), 6),
                round(float(pca3d_preds[i, 2]), 6),
                round(float(gemma_preds[i]), 6),
                round(float(y_pca[i, 0]), 6),
                round(float(y_pca[i, 1]), 6),
                round(float(y_pca[i, 2]), 6),
                round(float(y_gemma[i]), 6),
                round(float(pca3d_residuals[i]), 6),
                round(float(gemma_residuals[i]), 6),
            ])

    # -----------------------------------------------------------------------
    # 4. claude_pca_loadings.csv — PCA component vectors for Codex to reuse
    # -----------------------------------------------------------------------
    print("Writing claude_pca_loadings.csv...")
    with open(OUT_DIR / "claude_pca_loadings.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["component"] + cosine_cols + ["explained_variance_ratio"])
        for k in range(3):
            writer.writerow(
                [f"PC{k+1}"]
                + [round(float(v), 8) for v in pca_components[k]]
                + [round(float(ev_ratios[k]), 6)]
            )

    # -----------------------------------------------------------------------
    # 5. Summary stats for the manifest
    # -----------------------------------------------------------------------
    ss_res = ((y_pca - pca3d_preds) ** 2).sum(axis=0)
    ss_tot = ((y_pca - y_pca.mean(axis=0)) ** 2).sum(axis=0)
    r2_per_axis = (1 - ss_res / ss_tot).tolist()
    r2_pca3d = float(np.mean(r2_per_axis))
    ss_g = float(1 - ((y_gemma - gemma_preds)**2).sum() / ((y_gemma - y_gemma.mean())**2).sum())

    print(f"\nReconstructed metrics:")
    print(f"  PCA3D R²: {r2_pca3d:.4f}  (PC1={r2_per_axis[0]:.4f}, PC2={r2_per_axis[1]:.4f}, PC3={r2_per_axis[2]:.4f})")
    print(f"  Gemma R²: {ss_g:.4f}")

    # -----------------------------------------------------------------------
    # Write claude_dimension_codebook.md
    # -----------------------------------------------------------------------
    print("Writing claude_dimension_codebook.md...")
    codebook = """# Claude Feature Dimension Codebook

## Provenance
- analysis_model: claude-sonnet-4-6
- script_author_model: claude-sonnet-4-6
- date: 2026-05-28

## Best Feature Set Used in Claude Loop
F1: TF-IDF (SVD-50 components) + BigFive (5 ordinal dims) = 55 total features

---

## Block 1: TF-IDF Semantic Features (tfidf_svd_00 … tfidf_svd_49)

Source: no-label rewritten prompts (first prompt per role, from
  research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl)

Method: TF-IDF (unigrams, custom stopwords) → SVD(n_components=50, random_state=42)
  → L2-normalized token frequencies × IDF weights → truncated SVD
Interpretability: None. SVD components are not interpretable on their own.
Role in loop: Semantic baseline (Round 0). Captures prompt vocabulary variation.

---

## Block 2: BigFive Psychological Traits (big5_agreeableness … big5_openness)

Source: visualizations/bigfive_profiles.json
  275 roles × 5 dimensions, ordinal scale 1–5

Dimensions:
  big5_agreeableness    — Agreeableness (1=low, 5=high)
  big5_conscientiousness — Conscientiousness (1=low, 5=high)
  big5_extraversion     — Extraversion (1=low, 5=high)
  big5_neuroticism      — Neuroticism (1=low, 5=high)
  big5_openness         — Openness (1=low, 5=high)

IMPORTANT PROVENANCE NOTE:
  These scores were assigned by an LLM (likely Claude or GPT-4) during the
  original Paper 1 analysis, not by human raters or empirical measurement.
  They encode the assigning model's implicit stereotypes about role personality.
  Strong BigFive predictability may reflect model-prior alignment rather than
  genuine psychological structure in the activation geometry.

Role in loop: Added in Round 1. Produced the largest single improvement (+0.219 PCA3D R²).

---

## Block 3: DarkTriad Traits (NOT in best model; tested in Round 2)

Source: visualizations/dark_triad_profiles.json
  Same provenance caveat as BigFive.

Dimensions:
  dark3_machiavellianism — Machiavellianism (1–5)
  dark3_narcissism       — Narcissism (1–5)
  dark3_psychopathy      — Psychopathy (1–5)

Round 2 result: PCA3D R²=0.353, Δ-0.009. NOT retained.

---

## Block 4: Semantic Cluster One-Hot (NOT in best model; tested in Round 3)

Source: deep_semantic_topology_analysis.json → no_label_k7_clusters
  7 clusters from no-label prompt TF-IDF/SVD + k-means (deterministic).

Round 3 result: PCA3D R²=0.339, Δ-0.014. NOT retained.

---

## Blocks 5–6: Anchor/Bridge + Claude Hypotheses + Cross-Model Rank
Not tested (plateau triggered before these rounds).

---

## Target Variables

### Pseudo-PCA3D (primary target)
Source: research/cluster_analysis/qwen_cluster_directionality.csv
  275 × 7 cosine distances to named Qwen cluster centroids:
  cos_to_editor, cos_to_synthesizer, cos_to_blogger, cos_to_ancient,
  cos_to_trickster, cos_to_contrarian, cos_to_podcaster

Method: StandardScaler → PCA(n_components=3, random_state=42)
  PC1: 59.3% EV | PC2: 25.9% | PC3: 10.3% | Total: 95.5%

CRITICAL NOTE FOR CODEX TRANSFER:
  This is NOT Codex canonical activation PCA. Codex's target is presumably
  PCA on the full Qwen role-vector activation tensors. This proxy uses only
  7 named cluster centroids. PC1 of this proxy may differ in meaning and
  orientation from PC1 of the full Qwen activation space.
  Transfer testing required before conclusions generalize.

### Gemma Axis (secondary target)
Source: visualizations/full_ranking.csv → axis_projection_layer22
  Normalized to [-1, 1]: y = 2*(x - min)/(max - min) - 1

---

## CV Protocol
  StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
  Stratification: Gemma activation cluster label (7 classes)
  Regression: Ridge(alpha=1.0) with StandardScaler per fold
  Metric: mean held-out R² across PC1, PC2, PC3
"""
    (OUT_DIR / "claude_dimension_codebook.md").write_text(codebook)

    # -----------------------------------------------------------------------
    # Write claude_feature_export_manifest.md
    # -----------------------------------------------------------------------
    print("Writing claude_feature_export_manifest.md...")
    manifest = f"""# Claude Latent Feature Loop — Export Manifest

**Date:** 2026-05-28
**Purpose:** Enable Codex/GPT-5.5 apples-to-apples transfer comparison
**analysis_model:** claude-sonnet-4-6
**Branch:** claude/persona-inventory-topology-4qp10

---

## Files in This Directory

### Analysis scripts
| File | Description |
|---|---|
| run_claude_latent_feature_loop.py | Full iterative loop (re-run to reproduce) |
| export_claude_inputs.py | This script — exports clean CSVs for Codex |

### Result artifacts
| File | Rows | Cols | Description |
|---|---|---|---|
| claude_feature_matrix.csv | 275 | 56 | persona + 50 TF-IDF + 5 BigFive (best model input) |
| claude_target_coordinates.csv | 275 | 14 | persona + pseudo-PC1/2/3 + Gemma proj + 7 cosines + cluster |
| claude_split_assignments.csv | 275 | 13 | persona + fold ID + predictions + actuals + residuals |
| claude_pca_loadings.csv | 3 | 9 | PCA component vectors (to project new data onto same space) |
| claude_dimension_codebook.md | — | — | Full feature definitions with provenance |
| claude_persona_explanation_rankings.csv | 275 | — | Persona ranked by final residual (from loop) |
| claude_persona_explanation_rankings.json | 275 | — | Same with provenance metadata |
| claude_latent_feature_loop_report.md | — | — | Narrative loop report |
| claude_latent_feature_loop_master_log.json | — | — | Machine-readable loop summary |
| claude_vs_codex_latent_feature_comparison.md | — | — | Comparison template (Codex column blank) |

---

## Key Results (for Codex context)

| Metric | Value |
|---|---|
| Null PCA3D R² (permutation, n=200) | -0.322 mean, -0.221 p95 |
| Semantic baseline (TF-IDF only) | 0.142 |
| Best model (TF-IDF + BigFive) | **0.361** |
| Improvement over baseline | +0.219 |
| PC1 held-out R² | -0.089 (UNPREDICTED) |
| PC2 held-out R² | 0.732 |
| PC3 held-out R² | 0.440 |
| Gemma axis held-out R² | 0.695 |
| Loop plateau | Round 3 (DarkTriad and semantic cluster add no signal) |
| Retained feature sets | TF-IDF (50 SVD dims) + BigFive (5 dims) |

---

## Target Compatibility Warning

Claude used **pseudo-PCA3D** derived from the 275×7 Qwen cluster-cosine matrix.
This is NOT identical to Codex's canonical activation PCA target (if Codex used
full Qwen role-vector tensors). Differences to expect:

1. **PC orientation** may differ. The pseudo-PCA is over 7 named centroid directions;
   the full activation PCA is over thousands of dimensions.
2. **PC1 meaning** may differ. Claude's PC1 (59% EV, unpredicted) may or may not
   correspond to Codex's PC1.
3. **Variance explained** may differ. Claude's target has 95.5% EV in 3 PCs because
   the input is already low-dimensional.

For a fair comparison, Codex should either:
  (a) Also predict Claude's pseudo-PCA3D targets (files provided here), OR
  (b) Provide its PCA target coordinates so Claude's features can be tested on them.

The `claude_target_coordinates.csv` contains all 7 raw Qwen cosines per persona,
which Codex can use to re-derive the pseudo-PCA3D independently and confirm matching.
The `claude_pca_loadings.csv` contains the PCA component vectors for exact replication.

---

## What Codex Needs for Transfer Comparison

- [x] Feature matrix: claude_feature_matrix.csv (BigFive columns clearly labeled)
- [x] Target coordinates: claude_target_coordinates.csv (pseudo-PCA3D + raw cosines)
- [x] Split assignments: claude_split_assignments.csv (same folds for matched comparison)
- [x] PCA loadings: claude_pca_loadings.csv (project onto same pseudo-PCA space)
- [x] Feature definitions: claude_dimension_codebook.md
- [ ] Codex target coordinates: NEEDED FROM CODEX (full activation PCA, if different)
- [ ] Codex feature matrix: NEEDED FROM CODEX (for Claude-side transfer test)

---

## Raw GitHub URLs (branch: claude/persona-inventory-topology-4qp10)

BASE = https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/claude/persona-inventory-topology-4qp10/research/q2_stability/qwen/outputs/claude_latent_feature_loop/

Files:
  claude_feature_matrix.csv
  claude_target_coordinates.csv
  claude_split_assignments.csv
  claude_pca_loadings.csv
  claude_dimension_codebook.md
  claude_feature_export_manifest.md
  claude_vs_codex_latent_feature_comparison.md
  claude_latent_feature_loop_report.md
  claude_latent_feature_loop_master_log.json
  claude_persona_explanation_rankings.csv
"""
    (OUT_DIR / "claude_feature_export_manifest.md").write_text(manifest)

    print(f"\nAll files written to: {OUT_DIR}")
    print("\nFiles created:")
    for f in sorted(OUT_DIR.iterdir()):
        print(f"  {f.name:55s} {f.stat().st_size:8d} bytes")


if __name__ == "__main__":
    main()
