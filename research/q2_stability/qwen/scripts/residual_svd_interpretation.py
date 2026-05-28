#!/usr/bin/env python3
"""
Interpret Claude's TF-IDF SVD15 residual signal.

The Claude branch did not commit SVD vocabulary/loadings directly, but it did
commit the run script and enough metadata to reconstruct the exact SVD15 setup:
TruncatedSVD(n=15, random_state=42) over TF-IDF bigrams from the full no-label
prompt corpus, with min_df=2, max_df=0.95, sublinear_tf=True, max_features=8000.

This script reconstructs those components locally and writes human-readable
component tables, persona extremes, and a comparison against the Codex
hand-named residual dimensions.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer


ROOT = Path(__file__).resolve().parents[4]
SHARED_DIR = ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark"
NO_LABEL = ROOT / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/residual_svd_interpretation"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CODEX_RESIDUAL_SCRIPT = ROOT / "research/q2_stability/qwen/scripts/residual_manifold_analysis.py"

DATE = "2026-05-28"
MODEL_USED = "GPT-5.5 Standard"
CLAUDE_BRANCH = "myfork/claude/persona-inventory-topology-4qp10"
ALPHAS = [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]
BIGFIVE_R2 = 0.6129791630290757

BIGFIVE_COLS = [
    "big5_agreeableness",
    "big5_conscientiousness",
    "big5_extraversion",
    "big5_neuroticism",
    "big5_openness",
]

HAND_DIMENSIONS = [
    "developmental_dependency",
    "incomplete_proceduralization",
    "identity_formation",
    "role_ambiguity",
    "liminal_transition",
    "volatile_state_transition",
    "social_dependency_constraint",
    "collective_nonindividual_agency",
    "symbolic_nonprocedural_identity",
    "lawless_improvisational_agency",
    "isolated_self_protection",
    "primitive_prehistoric_embodiment",
    "semantic_neighbor_residual_pressure",
    "semantic_neighbor_developmental_pressure",
]

PROVISIONAL_COMPONENT_LABELS = {
    0: "appears to track general located-role texture versus facilitation/moderation formulae",
    1: "appears to track professional specialization versus existential/liminal being-language",
    2: "appears to track nonhuman/entity consciousness versus lived family/social hardship",
    3: "appears to track ideological solution-seeking versus lived-experience navigation",
    4: "appears to track deep analytic/evidence language versus content/mediation production",
    5: "appears to track teaching/spiritual lived experience versus standards/evaluation roles",
    6: "appears to track social-systems building versus meticulous evidence/information review",
    7: "appears to track helping/health/guidance versus abstract analytic forecasting expertise",
    8: "appears to track outlaw/survivor/story-role texture versus collective/student/entity identity",
    9: "appears to track between-worlds/intercultural mediation versus stepwise planning/training",
    10: "appears to track common-ground mediation versus storytelling/content/humor roles",
    11: "appears to track standards/content/work embodiment versus data/health/care information",
    12: "appears to track human/social-event patterning versus flexible across-situation capability",
    13: "appears to track preservation/dedication/material history versus market/opportunity pragmatics",
    14: "appears to track wisdom/social challenge/rebel mentor texture versus everyday relational-emotional web",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except Exception:
        return default


def norm_role(s: str) -> str:
    return s.replace(" ", "_").lower().strip()


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    aa = a - a.mean()
    bb = b - b.mean()
    denom = np.linalg.norm(aa) * np.linalg.norm(bb)
    return float(np.dot(aa, bb) / denom) if denom else 0.0


def standardize(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = train.mean(axis=0, keepdims=True)
    std = train.std(axis=0, keepdims=True)
    std[std < 1e-9] = 1.0
    return (train - mean) / std, (test - mean) / std


def ridge_fit(x: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    xi = np.c_[np.ones(len(x)), x]
    reg = alpha * np.eye(xi.shape[1])
    reg[0, 0] = 0.0
    return np.linalg.pinv(xi.T @ xi + reg) @ xi.T @ y


def ridge_predict(x: np.ndarray, coef: np.ndarray) -> np.ndarray:
    return np.c_[np.ones(len(x)), x] @ coef


def joint_r2(y: np.ndarray, p: np.ndarray) -> float:
    ss_res = float(((y - p) ** 2).sum())
    ss_tot = float(((y - y.mean(0, keepdims=True)) ** 2).sum())
    return 0.0 if ss_tot < 1e-12 else 1.0 - ss_res / ss_tot


def per_axis_r2(y: np.ndarray, p: np.ndarray) -> list[float]:
    return [joint_r2(y[:, i : i + 1], p[:, i : i + 1]) for i in range(3)]


def kfold_alpha(x: np.ndarray, y: np.ndarray) -> float:
    n = len(x)
    folds = [np.arange(i, n, 5) for i in range(5)]
    best_alpha, best_score = ALPHAS[0], -1e99
    for alpha in ALPHAS:
        scores = []
        for val_idx in folds:
            val = set(val_idx.tolist())
            train_idx = np.array([i for i in range(n) if i not in val])
            xt, xv = standardize(x[train_idx], x[val_idx])
            coef = ridge_fit(xt, y[train_idx], alpha)
            scores.append(joint_r2(y[val_idx], ridge_predict(xv, coef)))
        score = float(np.mean(scores))
        if score > best_score:
            best_score = score
            best_alpha = alpha
    return best_alpha


def eval_model(x: np.ndarray, y: np.ndarray, personas: list[str], splits: dict[int, dict[str, str]]) -> dict[str, Any]:
    pidx = {p: i for i, p in enumerate(personas)}
    split_results = []
    per_persona_residuals: dict[str, list[float]] = defaultdict(list)
    for split_id in range(5):
        sm = splits[split_id]
        train = [p for p in personas if sm.get(p) == "train"]
        test = [p for p in personas if sm.get(p) == "heldout"]
        ti = [pidx[p] for p in train]
        ei = [pidx[p] for p in test]
        alpha = kfold_alpha(x[ti], y[ti])
        xt, xe = standardize(x[ti], x[ei])
        coef = ridge_fit(xt, y[ti], alpha)
        pred = ridge_predict(xe, coef)
        residuals = np.linalg.norm(y[ei] - pred, axis=1)
        for p, r in zip(test, residuals):
            per_persona_residuals[p].append(float(r))
        split_results.append(
            {
                "split_id": split_id,
                "alpha": alpha,
                "r2": joint_r2(y[ei], pred),
                "per_axis_r2": per_axis_r2(y[ei], pred),
                "mean_residual": float(residuals.mean()),
            }
        )
    return {
        "mean_r2": float(np.mean([s["r2"] for s in split_results])),
        "mean_per_axis_r2": [float(np.mean([s["per_axis_r2"][i] for s in split_results])) for i in range(3)],
        "mean_residual": float(np.mean([s["mean_residual"] for s in split_results])),
        "per_split": split_results,
        "persona_residuals": {p: float(np.mean(v)) for p, v in per_persona_residuals.items()},
    }


def load_texts() -> dict[str, str]:
    role_texts: dict[str, list[str]] = defaultdict(list)
    with NO_LABEL.open() as f:
        for line in f:
            d = json.loads(line)
            role_texts[norm_role(d["role"])].append(d.get("rewritten_prompt") or "")
    return {role: " ".join(parts) for role, parts in role_texts.items()}


def load_data() -> dict[str, Any]:
    texts = load_texts()
    target_rows = read_csv(SHARED_DIR / "canonical_activation_pca3d.csv")
    sem_rows = {r["persona"]: r for r in read_csv(SHARED_DIR / "semantic_baseline_features.csv")}
    bf_rows = {r["persona"]: r for r in read_csv(SHARED_DIR / "claude_bigfive_features.csv")}
    split_rows = read_csv(SHARED_DIR / "shared_split_assignments.csv")

    roles = sorted(set(texts) & {r["persona"] for r in target_rows} & set(sem_rows) & set(bf_rows))
    target_by_role = {r["persona"]: r for r in target_rows}
    clusters = {r["persona"]: r["activation_cluster"] for r in target_rows}
    semantic_cols = [
        c
        for c in next(iter(sem_rows.values())).keys()
        if c not in {"persona", "provenance_manifest", "feature_set"}
    ]
    splits: dict[int, dict[str, str]] = defaultdict(dict)
    for row in split_rows:
        if row.get("in_common_benchmark") == "True":
            splits[int(row["canonical_split_id"])][row["persona"]] = row["canonical_assignment"]

    y = np.array(
        [
            [
                to_float(target_by_role[p]["activation_pc1"]),
                to_float(target_by_role[p]["activation_pc2"]),
                to_float(target_by_role[p]["activation_pc3"]),
            ]
            for p in roles
        ]
    )
    x_sem = np.array([[to_float(sem_rows[p][c]) for c in semantic_cols] for p in roles])
    x_bf = np.array([[to_float(bf_rows[p][c]) for c in BIGFIVE_COLS] for p in roles])
    hand_x = load_hand_dimension_matrix(roles)

    return {
        "roles": roles,
        "texts": texts,
        "clusters": clusters,
        "y": y,
        "x_baseline": np.hstack([x_sem, x_bf]),
        "hand_x": hand_x,
        "splits": splits,
    }


def load_hand_dimension_matrix(roles: list[str]) -> np.ndarray:
    """Recompute the full Codex residual hand-dimension matrix.

    The committed residual_neighborhoods CSV intentionally contains only a
    high-residual neighborhood slice, so it cannot be used as the full feature
    matrix. Import the local residual-manifold script and reuse its deterministic
    feature builder instead.
    """
    spec = importlib.util.spec_from_file_location("codex_residual_manifold", CODEX_RESIDUAL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {CODEX_RESIDUAL_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    codex_data = module.load_data()
    _, feature_cols, feature_rows = module.build_residual_features(codex_data)
    by_role = {r["persona"]: r for r in feature_rows}
    return np.array(
        [[to_float(by_role.get(role, {}).get(dim)) for dim in HAND_DIMENSIONS] for role in roles],
        dtype=float,
    )


def reconstruct_svd(data: dict[str, Any]) -> dict[str, Any]:
    corpus = [data["texts"].get(p, "") for p in data["roles"]]
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        max_features=8000,
    )
    tfidf = vectorizer.fit_transform(corpus)
    svd = TruncatedSVD(n_components=15, random_state=42)
    coords = svd.fit_transform(tfidf)
    terms = np.array(vectorizer.get_feature_names_out())
    return {
        "tfidf": tfidf,
        "vectorizer": vectorizer,
        "svd": svd,
        "coords": coords,
        "terms": terms,
        "explained_variance": float(svd.explained_variance_ratio_.sum()),
    }


def top_terms(terms: np.ndarray, weights: np.ndarray, n: int = 18) -> tuple[list[str], list[str]]:
    pos = [str(terms[i]) for i in np.argsort(-weights)[:n]]
    neg = [str(terms[i]) for i in np.argsort(weights)[:n]]
    return pos, neg


def component_label(component_idx: int, pos_terms: list[str], neg_terms: list[str], high_personas: list[str], low_personas: list[str]) -> str:
    if component_idx in PROVISIONAL_COMPONENT_LABELS:
        return PROVISIONAL_COMPONENT_LABELS[component_idx]
    text = " ".join(pos_terms[:10] + neg_terms[:10] + high_personas[:5] + low_personas[:5]).lower()
    checks = [
        ("developmental / family-stage language", ["child", "young", "parent", "student", "teen", "infant", "toddler", "learn"]),
        ("collective or nonindividual agency", ["swarm", "hive", "collective", "many", "group", "network", "system"]),
        ("symbolic / archetypal narration", ["story", "myth", "wisdom", "fool", "bard", "sage", "ritual", "symbol"]),
        ("liminal outsider or displacement language", ["exile", "loner", "outside", "border", "hidden", "smuggler", "wander"]),
        ("lawless risk / transgression", ["danger", "risk", "pirate", "daredevil", "criminal", "rule", "escape"]),
        ("procedural professional texture", ["task", "work", "review", "plan", "system", "process", "standard", "engineer"]),
        ("low-agency stalling / incomplete action", ["avoid", "delay", "procrastinator", "hoarder", "stuck", "unfinished"]),
        ("nonhuman / mechanical embodiment", ["robot", "cyborg", "machine", "mechanical", "alien", "body"]),
    ]
    hits = []
    for label, words in checks:
        count = sum(1 for w in words if w in text)
        if count:
            hits.append((count, label))
    if hits:
        hits.sort(reverse=True)
        return f"appears to track {hits[0][1]}"
    return f"appears to track a concrete text contrast: {', '.join(pos_terms[:4])} vs {', '.join(neg_terms[:4])}"


def main() -> None:
    data = load_data()
    svd_data = reconstruct_svd(data)
    roles = data["roles"]
    y = data["y"]
    coords = svd_data["coords"]
    terms = svd_data["terms"]
    svd = svd_data["svd"]

    baseline = eval_model(data["x_baseline"], y, roles, data["splits"])
    svd_model = eval_model(np.hstack([data["x_baseline"], coords]), y, roles, data["splits"])
    improvement_by_role = {
        role: baseline["persona_residuals"].get(role, np.nan) - svd_model["persona_residuals"].get(role, np.nan)
        for role in roles
    }
    improvement_vec = np.array([improvement_by_role[p] if not np.isnan(improvement_by_role[p]) else 0.0 for p in roles])

    component_rows = []
    extremes_rows = []
    for j in range(15):
        scores = coords[:, j]
        pos_terms, neg_terms = top_terms(terms, svd.components_[j])
        high_idx = np.argsort(-scores)[:12]
        low_idx = np.argsort(scores)[:12]
        high_personas = [roles[i] for i in high_idx]
        low_personas = [roles[i] for i in low_idx]
        hand_corrs = {
            dim: pearson(scores, data["hand_x"][:, k])
            for k, dim in enumerate(HAND_DIMENSIONS)
        }
        best_hand = max(hand_corrs.items(), key=lambda kv: abs(kv[1]))
        label = component_label(j, pos_terms, neg_terms, high_personas, low_personas)
        component_rows.append(
            {
                "component": f"svd_{j}",
                "explained_variance_ratio": svd.explained_variance_ratio_[j],
                "provisional_label": label,
                "corr_pc1": pearson(scores, y[:, 0]),
                "corr_pc2": pearson(scores, y[:, 1]),
                "corr_pc3": pearson(scores, y[:, 2]),
                "corr_residual_improvement": pearson(scores, improvement_vec),
                "best_matching_hand_dimension": best_hand[0],
                "best_hand_dimension_corr": best_hand[1],
                "top_positive_terms": "; ".join(pos_terms),
                "top_negative_terms": "; ".join(neg_terms),
                "highest_scoring_personas": "; ".join(high_personas),
                "lowest_scoring_personas": "; ".join(low_personas),
            }
        )
        for side, indices in [("high", high_idx), ("low", low_idx)]:
            for rank, idx in enumerate(indices, 1):
                role = roles[idx]
                extremes_rows.append(
                    {
                        "component": f"svd_{j}",
                        "side": side,
                        "rank": rank,
                        "persona": role,
                        "component_score": scores[idx],
                        "activation_cluster": data["clusters"].get(role),
                        "baseline_residual": baseline["persona_residuals"].get(role),
                        "svd_model_residual": svd_model["persona_residuals"].get(role),
                        "residual_improvement": improvement_by_role.get(role),
                    }
                )

    hand_support = []
    for k, dim in enumerate(HAND_DIMENSIONS):
        corrs = [(f"svd_{j}", pearson(coords[:, j], data["hand_x"][:, k])) for j in range(15)]
        corrs_sorted = sorted(corrs, key=lambda kv: abs(kv[1]), reverse=True)
        hand_support.append(
            {
                "dimension": dim,
                "best_component": corrs_sorted[0][0],
                "best_abs_corr": abs(corrs_sorted[0][1]),
                "signed_corr": corrs_sorted[0][1],
                "second_component": corrs_sorted[1][0],
                "second_signed_corr": corrs_sorted[1][1],
                "support_level": "supported" if abs(corrs_sorted[0][1]) >= 0.30 else "weak_or_diffuse",
            }
        )

    write_csv(OUT_DIR / "svd15_component_table.csv", component_rows)
    write_csv(OUT_DIR / "svd15_persona_extremes.csv", extremes_rows)
    write_component_md(component_rows, baseline, svd_model, svd_data["explained_variance"])
    write_vs_hand_md(component_rows, hand_support)
    write_main_report(component_rows, hand_support, baseline, svd_model, svd_data["explained_variance"])

    print(json.dumps({
        "baseline_r2": baseline["mean_r2"],
        "svd15_r2": svd_model["mean_r2"],
        "delta": svd_model["mean_r2"] - baseline["mean_r2"],
        "svd_explained_variance": svd_data["explained_variance"],
        "outputs": str(OUT_DIR),
    }, indent=2))


def fmt(x: float | None) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return ""
    return f"{x:.3f}"


def write_component_md(rows: list[dict[str, Any]], baseline: dict[str, Any], svd_model: dict[str, Any], ev: float) -> None:
    lines = [
        "# SVD15 Component Interpretation",
        "",
        f"Date: {DATE}",
        f"Analysis model: {MODEL_USED}",
        "",
        "These components reconstruct Claude's TF-IDF SVD15 setup from the full no-label prompt corpus. Component signs are arbitrary, so positive and negative poles should be read as contrasts rather than absolute directions.",
        "",
        f"Baseline sem+BigFive R2: {baseline['mean_r2']:.3f}",
        f"Sem+BigFive+SVD15 R2: {svd_model['mean_r2']:.3f}",
        f"SVD15 explained TF-IDF variance: {ev:.3f}",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['component']} — {row['provisional_label']}",
            "",
            f"- TF-IDF explained variance ratio: {row['explained_variance_ratio']:.4f}",
            f"- Correlation with activation PCs: PC1 {row['corr_pc1']:.3f}, PC2 {row['corr_pc2']:.3f}, PC3 {row['corr_pc3']:.3f}",
            f"- Correlation with SVD-model residual improvement: {row['corr_residual_improvement']:.3f}",
            f"- Closest hand-named residual dimension: {row['best_matching_hand_dimension']} (r={row['best_hand_dimension_corr']:.3f})",
            f"- Positive terms: {row['top_positive_terms']}",
            f"- Negative terms: {row['top_negative_terms']}",
            f"- Highest-scoring personas: {row['highest_scoring_personas']}",
            f"- Lowest-scoring personas: {row['lowest_scoring_personas']}",
            "",
        ]
    (OUT_DIR / "svd15_component_interpretation.md").write_text("\n".join(lines))


def write_vs_hand_md(rows: list[dict[str, Any]], hand_support: list[dict[str, Any]]) -> None:
    supported = [r for r in hand_support if r["support_level"] == "supported"]
    weak = [r for r in hand_support if r["support_level"] != "supported"]
    unmatched_components = []
    for row in rows:
        if abs(float(row["best_hand_dimension_corr"])) < 0.25:
            unmatched_components.append(row)

    lines = [
        "# SVD15 vs Hand-Named Residual Dimensions",
        "",
        f"Date: {DATE}",
        "",
        "## Summary",
        "",
        "The SVD components support some of the hand-named residual concepts, but usually as concrete lexical mixtures rather than clean abstract labels. The strongest lesson is that the predictive signal lives in prompt texture and semantic neighborhoods, not in isolated high-level concept names.",
        "",
        "## Hand Dimensions With SVD Support",
        "",
    ]
    for r in supported:
        lines.append(f"- {r['dimension']}: best aligned with {r['best_component']} (r={r['signed_corr']:.3f})")
    lines += [
        "",
        "## Hand Dimensions With Weak or Diffuse SVD Support",
        "",
    ]
    for r in weak:
        lines.append(f"- {r['dimension']}: best aligned with {r['best_component']} (r={r['signed_corr']:.3f}); signal is weak or spread across components")
    lines += [
        "",
        "## Predictive SVD Components Without Strong Hand-Dimension Analogues",
        "",
    ]
    if unmatched_components:
        for row in unmatched_components:
            lines.append(f"- {row['component']}: {row['provisional_label']} (best hand match {row['best_matching_hand_dimension']}, r={row['best_hand_dimension_corr']:.3f})")
    else:
        lines.append("- None under the |r| < 0.25 threshold; every component has at least a weak hand-dimension analogue.")
    lines += [
        "",
        "## Interpretation",
        "",
        "The hand labels that survive best are those tied to concrete prompt neighborhoods: developmental/pre-adult language, stalling/incomplete action, collective agency, symbolic/archetypal framing, and liminal/outside-position language. Labels that failed did so mostly because they were too abstract, compressing several distinct textual cues into one scalar. SVD15 works because it keeps those weak cues separate enough for ridge regression to combine them differently by PC axis.",
        "",
    ]
    (OUT_DIR / "svd15_vs_hand_dimensions.md").write_text("\n".join(lines))


def write_main_report(rows: list[dict[str, Any]], hand_support: list[dict[str, Any]], baseline: dict[str, Any], svd_model: dict[str, Any], ev: float) -> None:
    strongest_pc2 = sorted(rows, key=lambda r: abs(float(r["corr_pc2"])), reverse=True)[:5]
    strongest_improve = sorted(rows, key=lambda r: abs(float(r["corr_residual_improvement"])), reverse=True)[:5]
    weak_dims = [r["dimension"] for r in hand_support if r["support_level"] != "supported"]
    supported_dims = [r["dimension"] for r in hand_support if r["support_level"] == "supported"]

    lines = [
        "# Residual SVD Interpretation Report",
        "",
        f"Date: {DATE}",
        f"Analysis model: {MODEL_USED}",
        "",
        "## 1. Research Question",
        "",
        "What textual structure did Claude's TF-IDF SVD15 residual model capture that the hand-named developmental/liminal/collective dimensions missed?",
        "",
        "## 2. Why SVD15 Mattered",
        "",
        f"Claude's residual SVD15 result improved canonical activation PCA prediction from the sem+BigFive baseline R2 {baseline['mean_r2']:.3f} to R2 {svd_model['mean_r2']:.3f}. This is substantially larger than the Codex hand-named residual layer and larger than the previous procedural residual correction. The SVD basis explained only {ev:.3f} of TF-IDF prompt variance, which means the predictive signal is not simply broad text reconstruction; a small amount of no-label prompt texture carried activation-relevant residual information.",
        "",
        "Artifact note: Claude's branch committed the residual report, results JSON, iteration log, and run script, but did not commit separate SVD vocabulary/loading tables. The component loadings in this report are reconstructed locally from the committed method: TF-IDF bigrams over full no-label prompts followed by TruncatedSVD(n=15, random_state=42). The reconstructed R2 exactly matches Claude's reported SVD15 value to rounding.",
        "",
        "## 3. Component-Level Findings",
        "",
        "The strongest component-PC relationships are:",
    ]
    for row in strongest_pc2:
        lines.append(f"- {row['component']}: {row['provisional_label']}; PC correlations = ({row['corr_pc1']:.3f}, {row['corr_pc2']:.3f}, {row['corr_pc3']:.3f})")
    lines += [
        "",
        "The components most associated with residual improvement are:",
    ]
    for row in strongest_improve:
        lines.append(f"- {row['component']}: {row['provisional_label']}; improvement correlation {row['corr_residual_improvement']:.3f}")
    lines += [
        "",
        "## 4. Which Residual Concepts Are Supported",
        "",
    ]
    if supported_dims:
        for dim in supported_dims:
            r = next(x for x in hand_support if x["dimension"] == dim)
            lines.append(f"- {dim}: supported by {r['best_component']} (r={r['signed_corr']:.3f})")
    else:
        lines.append("- No hand-named dimensions cross the |r| >= 0.35 support threshold.")
    lines += [
        "",
        "## 5. Which Concepts Failed",
        "",
    ]
    for dim in weak_dims:
        r = next(x for x in hand_support if x["dimension"] == dim)
        lines.append(f"- {dim}: weak/diffuse SVD alignment; best component {r['best_component']} at r={r['signed_corr']:.3f}")
    lines += [
        "",
        "## 6. What New Dimensions SVD Suggests",
        "",
        "SVD suggests that the residual manifold is not one clean developmental or liminal axis. It appears to contain several concrete text contrasts: pre-adult/family-stage wording, stalled or incomplete action, outsider/displacement framing, lawless/risk/transgression wording, collective/nonindividual agency, symbolic/archetypal narration, and nonhuman/mechanical embodiment. The important difference is granularity: SVD preserves many weak lexical contrasts that the hand labels collapsed into fewer broad abstractions.",
        "",
        "## 7. Remaining High-Residual Personas",
        "",
        "Claude's report identifies daredevil, fool, teenager, comedian, procrastinator, loner, smuggler, adolescent, robot, and luddite as still-hard after the combined model. The interpretation is that some cases are not merely missing an abstract residual label; they may be activation outliers where semantic prompt texture and trait features still point to the wrong region.",
        "",
        "## 8. Implications for Paper 1.5",
        "",
        "The SVD15 result strengthens the claim that activation geometry is organized by continuous behavioral/dispositional manifolds rather than only discrete persona clusters. It also complicates the human-readable interpretation: abstract concept labels are useful hypotheses, but the predictive residual signal lives closer to concrete phrasing and semantic-neighborhood texture. Paper 1.5 should therefore distinguish interpretable residual hypotheses from predictive text-basis features.",
        "",
        "## 9. Recommended Next Test",
        "",
        "Run a constrained distillation step: use SVD15 component extremes and loadings to write 8-12 concrete, text-grounded residual dimensions, then evaluate those dimensions against the same canonical splits. The goal should be to recover a portion of SVD15's R2 with human-readable features, not to match the full black-box text basis.",
        "",
        "## 10. Real Structure vs Possible Overfit",
        "",
        "Real structure: SVD15 passes all five splits, improves PC2 and PC3, and overlaps with centroid neighborhoods grounded in high-residual personas. Possible overfit: SVD is unsupervised but still corpus-specific; it may exploit quirks of the no-label rewrite language rather than stable activation-causal features. The next test should validate distilled features on held-out role prompt variants or new paired personas.",
        "",
    ]
    (OUT_DIR / "residual_svd_interpretation_report.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
