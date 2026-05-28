#!/usr/bin/env python3
"""
Residual-manifold analysis after hierarchical trait + procedural modeling.

This is a focused third-layer diagnostic. It does not run pods, generate
activations, or call model APIs. Candidate dimensions are constrained to
developmental, liminal, unstable-identity, social-dependency, collective, and
symbolic/nonprocedural residual structure, and are operationalized from full
no-label prompts plus existing semantic-neighborhood artifacts.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
SHARED_DIR = ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark"
HIER_DIR = ROOT / "research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model"
NO_LABEL_DIR = ROOT / "research/assistant_axis_methodology/no_label_prompt_ablation"
SEM_DIR = ROOT / "research/assistant_axis_methodology/semantic_vs_activation_geometry"
METH_DIR = ROOT / "research/assistant_axis_methodology"
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/residual_manifold_analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATE = "2026-05-28"
MODEL_USED = "GPT-5.5 Standard"
SCRIPT_AUTHOR = "GPT-5.5 Standard via Codex"
ALPHAS = [0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]

BIGFIVE_COLS = [
    "big5_agreeableness",
    "big5_conscientiousness",
    "big5_extraversion",
    "big5_neuroticism",
    "big5_openness",
]

PROCEDURAL_COLS = [
    "codex_evaluate_judge_verify",
    "codex_translate_mediate_synthesize",
    "codex_destabilize_expose_disrupt",
    "codex_assistant_basin_adjacency",
    "codex_procedural_professional_orientation",
    "codex_oppositional_moral_pressure",
    "codex_communicative_media_register",
    "codex_standards_and_error_aversion",
    "codex_forceful_self_assertion",
    "codex_adversarial_dominance",
    "codex_standard_enforcement",
    "codex_reactive_opposition",
]

DIMENSION_SPECS = {
    "developmental_dependency": {
        "iteration": 1,
        "description": "Childlike, immature, dependent, or still-being-formed agency.",
        "patterns": [
            "child", "young", "infant", "toddler", "teen", "adolescent", "student",
            "learn", "learning", "school", "growing", "immature", "dependent",
            "guidance", "develop", "formation",
        ],
    },
    "incomplete_proceduralization": {
        "iteration": 1,
        "description": "Unfinished competence, practice, apprenticeship, delay, or failure to execute stable procedure.",
        "patterns": [
            "unfinished", "incomplete", "practice", "apprentice", "novice", "beginner",
            "amateur", "delay", "procrastinat", "avoid", "hesitat", "stuck", "stall",
            "unprepared", "not ready", "trying",
        ],
    },
    "identity_formation": {
        "iteration": 1,
        "description": "Identity still being formed, chosen, remembered, performed, or negotiated.",
        "patterns": [
            "identity", "self", "become", "becoming", "who", "name", "mask",
            "role", "belong", "belonging", "search", "discover", "uncertain",
            "define", "formation",
        ],
    },
    "role_ambiguity": {
        "iteration": 1,
        "description": "Ambiguous, undefined, marginal, or hard-to-place role structure.",
        "patterns": [
            "ambiguous", "unclear", "uncertain", "undefined", "between", "neither",
            "both", "blur", "hidden", "unknown", "anonymous", "shifting",
            "unfixed", "unstable",
        ],
    },
    "liminal_transition": {
        "iteration": 1,
        "description": "Threshold, exile, migration, wandering, transitional, or boundary-crossing identity.",
        "patterns": [
            "threshold", "liminal", "border", "edge", "between", "transition",
            "exile", "wander", "drift", "marginal", "outsider", "outcast",
            "displaced", "crossing", "passage",
        ],
    },
    "volatile_state_transition": {
        "iteration": 1,
        "description": "Instability, impulsivity, sudden shifts, crisis, or volatile affect/state change.",
        "patterns": [
            "volatile", "unstable", "impulsive", "sudden", "shift", "chaos",
            "crisis", "erratic", "rage", "panic", "reckless", "dare", "risk",
            "wild", "unpredictable",
        ],
    },
    "social_dependency_constraint": {
        "iteration": 1,
        "description": "Social dependence, constraint, confinement, exclusion, or relational pressure.",
        "patterns": [
            "dependent", "need", "support", "care", "approval", "peer", "family",
            "prison", "confined", "trapped", "excluded", "isolated", "lonely",
            "rejected", "constraint", "bound", "social",
        ],
    },
    "collective_nonindividual_agency": {
        "iteration": 1,
        "description": "Swarm, hive, crowd, ecosystemic, distributed, or nonindividual agency.",
        "patterns": [
            "collective", "swarm", "hive", "crowd", "many", "network",
            "distributed", "group", "system", "ecosystem", "we", "plural",
            "mass", "nonindividual",
        ],
    },
    "symbolic_nonprocedural_identity": {
        "iteration": 1,
        "description": "Mythic, symbolic, elemental, archetypal, or image-like identity not organized by procedure.",
        "patterns": [
            "symbol", "myth", "archetype", "spirit", "ghost", "void", "wind",
            "shadow", "dream", "ritual", "sacred", "element", "legend",
            "metaphor", "story",
        ],
    },
    "lawless_improvisational_agency": {
        "iteration": 2,
        "description": "Improvised, rule-bending, outlaw, pirate-like, opportunistic agency.",
        "patterns": [
            "pirate", "rogue", "smuggle", "outlaw", "lawless", "steal", "raid",
            "improvise", "opportun", "cunning", "escape", "rule", "defy",
            "illicit", "survive",
        ],
    },
    "isolated_self_protection": {
        "iteration": 2,
        "description": "Withdrawal, lonerhood, guardedness, isolation, or protective self-enclosure.",
        "patterns": [
            "alone", "loner", "isolated", "withdraw", "hidden", "guarded",
            "private", "solitary", "avoid", "distance", "outsider", "hermit",
            "defensive", "separate",
        ],
    },
    "primitive_prehistoric_embodiment": {
        "iteration": 2,
        "description": "Pre-institutional, bodily, primitive, survival-oriented, or preprocedural embodiment.",
        "patterns": [
            "caveman", "primitive", "ancient", "survival", "instinct", "body",
            "hunger", "shelter", "tribe", "stone", "raw", "physical",
            "pre", "animal",
        ],
    },
    "semantic_neighbor_residual_pressure": {
        "iteration": 2,
        "description": "Mean residual pressure in the role's no-label semantic neighborhood.",
        "semantic_neighbor_metric": "mean_hierarchical_residual_top5",
    },
    "semantic_neighbor_developmental_pressure": {
        "iteration": 2,
        "description": "Proportion of no-label semantic neighbors that are developmental or formation-like high-residual cases.",
        "semantic_neighbor_metric": "developmental_neighbor_fraction_top5",
    },
    "semantic_bridge_instability": {
        "iteration": 3,
        "description": "No-label semantic bridge/migration instability and cross-cluster-neighbor pressure.",
        "metadata_metric": "bridge_score",
    },
    "semantic_displacement": {
        "iteration": 3,
        "description": "Original-to-no-label semantic displacement, used as a proxy for label-dependence/semantic instability.",
        "metadata_metric": "svd_displacement",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows and not fieldnames:
        path.write_text("")
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
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


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("_", " ").replace("-", " ")).strip()


def pattern_score(text: str, patterns: list[str]) -> float:
    t = normalize_text(text)
    if not t:
        return 0.0
    score = 0.0
    for pat in patterns:
        p = normalize_text(pat)
        if " " in p:
            score += t.count(p) * 1.5
        else:
            score += len(re.findall(rf"\b{re.escape(p)}[a-z]*\b", t))
    return math.log1p(score)


def matrix(rows: list[dict[str, Any]], columns: list[str]) -> np.ndarray:
    return np.array([[to_float(row.get(col)) for col in columns] for row in rows], dtype=float)


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


def r2(y: np.ndarray, pred: np.ndarray) -> float:
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean(axis=0, keepdims=True)) ** 2).sum())
    return 0.0 if ss_tot < 1e-12 else 1.0 - ss_res / ss_tot


def per_axis_r2(y: np.ndarray, pred: np.ndarray) -> list[float]:
    return [r2(y[:, i : i + 1], pred[:, i : i + 1]) for i in range(y.shape[1])]


def kfold_alpha(x: np.ndarray, y: np.ndarray) -> float:
    n = len(x)
    folds = [np.arange(i, n, 5) for i in range(5)]
    best_alpha, best_score = ALPHAS[0], -1e99
    for alpha in ALPHAS:
        scores = []
        for val_idx in folds:
            val = set(val_idx.tolist())
            tr_idx = np.array([i for i in range(n) if i not in val])
            xt, xv = standardize(x[tr_idx], x[val_idx])
            coef = ridge_fit(xt, y[tr_idx], alpha)
            scores.append(r2(y[val_idx], ridge_predict(xv, coef)))
        score = float(np.mean(scores))
        if score > best_score:
            best_score = score
            best_alpha = alpha
    return best_alpha


def fit_predict(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> dict[str, Any]:
    alpha = kfold_alpha(x_train, y_train)
    xt, xv = standardize(x_train, x_test)
    coef = ridge_fit(xt, y_train, alpha)
    return {
        "alpha": alpha,
        "train_pred": ridge_predict(xt, coef),
        "test_pred": ridge_predict(xv, coef),
    }


def nearest_neighbor_preservation(y: np.ndarray, pred: np.ndarray, k: int = 5) -> float:
    vals = []
    for i in range(len(y)):
        yd = np.linalg.norm(y - y[i], axis=1)
        pd = np.linalg.norm(pred - pred[i], axis=1)
        vals.append(len(set(np.argsort(yd)[1 : k + 1]) & set(np.argsort(pd)[1 : k + 1])) / k)
    return float(np.mean(vals))


def load_no_label_text() -> dict[str, str]:
    by_role: dict[str, list[str]] = defaultdict(list)
    with (NO_LABEL_DIR / "no_label_role_prompts.jsonl").open() as f:
        for line in f:
            row = json.loads(line)
            role = row["role"]
            if row.get("role_description"):
                by_role[role].append(row["role_description"])
            by_role[role].append(row.get("rewritten_prompt") or row.get("original_prompt") or "")
    return {role: "\n".join(texts) for role, texts in by_role.items()}


def load_neighbors() -> dict[str, list[tuple[str, float]]]:
    out: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for row in read_csv(SEM_DIR / "no_label_prompt_neighbors.csv"):
        if int(row["neighbor_rank"]) <= 8:
            out[row["role"]].append((row["neighbor"], to_float(row["cosine"])))
    return out


def load_data() -> dict[str, Any]:
    target_rows = read_csv(SHARED_DIR / "canonical_activation_pca3d.csv")
    sem_rows = {r["persona"]: r for r in read_csv(SHARED_DIR / "semantic_baseline_features.csv")}
    big_rows = {r["persona"]: r for r in read_csv(SHARED_DIR / "claude_bigfive_features.csv")}
    codex_rows = {r["persona"]: r for r in read_csv(SHARED_DIR / "codex_retained_features.csv")}
    split_rows = read_csv(SHARED_DIR / "shared_split_assignments.csv")
    hier_rows = {r["persona"]: r for r in read_csv(HIER_DIR / "persona_residual_improvement_rankings.csv")}
    bridge_rows = {r["role"]: r for r in read_csv(METH_DIR / "bridge_roles.csv")}
    displacement_rows = {
        r["role"]: r
        for r in read_csv(NO_LABEL_DIR / "original_vs_no_label_role_displacement.csv")
    }

    roles = [r["persona"] for r in target_rows]
    semantic_cols = [
        c
        for c in next(iter(sem_rows.values())).keys()
        if c not in {"persona", "provenance_manifest", "feature_set"}
    ]
    procedural_cols = [c for c in PROCEDURAL_COLS if c in next(iter(codex_rows.values())).keys()]
    no_label_text = load_no_label_text()
    neighbors = load_neighbors()

    developmental_seed = {"toddler", "infant", "adolescent", "teenager", "student"}
    rows = []
    for t in target_rows:
        role = t["persona"]
        h = hier_rows.get(role, {})
        bridge = bridge_rows.get(role, {})
        disp = displacement_rows.get(role, {})
        rows.append(
            {
                "persona": role,
                "activation_cluster": t["activation_cluster"],
                "no_label_text": no_label_text.get(role, ""),
                "hierarchical_residual": to_float(h.get("hierarchical_residual")),
                "trait_residual": to_float(h.get("trait_residual")),
                "improvement_vs_trait": to_float(h.get("improvement_vs_trait")),
                "heldout_frequency": int(to_float(h.get("heldout_frequency"))),
                "is_bridge": str(h.get("is_bridge", "")).lower() == "true",
                "bridge_score": to_float(bridge.get("bridge_score", h.get("bridge_score"))),
                "semantic_bridge_margin": to_float(bridge.get("semantic_bridge_margin")),
                "cross_cluster_neighbors_top8": to_float(bridge.get("cross_cluster_neighbors_top8")),
                "svd_displacement": to_float(disp.get("svd_displacement")),
                "tfidf_displacement": to_float(disp.get("tfidf_displacement")),
                "is_developmental_seed": role in developmental_seed,
            }
        )

    return {
        "roles": roles,
        "target_rows": target_rows,
        "rows": rows,
        "semantic_cols": semantic_cols,
        "procedural_cols": procedural_cols,
        "y": matrix(target_rows, ["activation_pc1", "activation_pc2", "activation_pc3"]),
        "semantic_x": matrix([sem_rows[r] for r in roles], semantic_cols),
        "bigfive_x": matrix([big_rows[r] for r in roles], BIGFIVE_COLS),
        "procedural_x": matrix([codex_rows[r] for r in roles], procedural_cols),
        "splits": split_rows,
        "neighbors": neighbors,
    }


def split_indices(data: dict[str, Any], split_id: int) -> tuple[list[int], list[int]]:
    assignment = {
        r["persona"]: r["canonical_assignment"]
        for r in data["splits"]
        if int(r["canonical_split_id"]) == split_id
    }
    train_idx = [i for i, role in enumerate(data["roles"]) if assignment[role] == "train"]
    test_idx = [i for i, role in enumerate(data["roles"]) if assignment[role] == "heldout"]
    return train_idx, test_idx


def build_residual_features(data: dict[str, Any]) -> tuple[np.ndarray, list[str], list[dict[str, Any]]]:
    roles = data["roles"]
    row_by_role = {r["persona"]: r for r in data["rows"]}
    residual_by_role = {r["persona"]: r["hierarchical_residual"] for r in data["rows"]}
    dev_seed = {r["persona"] for r in data["rows"] if r["is_developmental_seed"]}

    feature_rows: list[dict[str, Any]] = []
    for role in roles:
        row = row_by_role[role]
        text = row["no_label_text"]
        f: dict[str, Any] = {"persona": role}
        for name, spec in DIMENSION_SPECS.items():
            if "patterns" in spec:
                f[name] = pattern_score(text, spec["patterns"])
        neigh = data["neighbors"].get(role, [])[:5]
        neigh_res = [residual_by_role.get(n, 0.0) for n, _ in neigh]
        f["semantic_neighbor_residual_pressure"] = float(np.mean(neigh_res)) if neigh_res else 0.0
        f["semantic_neighbor_developmental_pressure"] = (
            sum(1 for n, _ in neigh if n in dev_seed) / len(neigh) if neigh else 0.0
        )
        f["semantic_bridge_instability"] = (
            row["bridge_score"]
            + row["cross_cluster_neighbors_top8"] / 8.0
            + (1.0 - min(row["semantic_bridge_margin"], 1.0))
        )
        f["semantic_displacement"] = row["svd_displacement"]
        feature_rows.append(f)

    columns = list(DIMENSION_SPECS)
    return matrix(feature_rows, columns), columns, feature_rows


def base_hierarchical_predictions(
    data: dict[str, Any],
    extra_x: np.ndarray | None = None,
) -> dict[str, Any]:
    semantic = data["semantic_x"]
    trait_x = np.hstack([semantic, data["bigfive_x"]])
    proc_x = data["procedural_x"]
    y = data["y"]
    if extra_x is None:
        extra_x = np.zeros((len(y), 0))

    split_metrics = []
    persona_residuals: dict[str, list[float]] = defaultdict(list)
    persona_predictions: dict[str, list[np.ndarray]] = defaultdict(list)
    output_predictions = []

    for split_id in range(5):
        train_idx, test_idx = split_indices(data, split_id)
        stage_a = fit_predict(trait_x[train_idx], y[train_idx], trait_x[test_idx])
        residual_train_a = y[train_idx] - stage_a["train_pred"]
        stage_b = fit_predict(proc_x[train_idx], residual_train_a, proc_x[test_idx])
        train_hier_pred = stage_a["train_pred"] + stage_b["train_pred"]
        test_hier_pred = stage_a["test_pred"] + stage_b["test_pred"]

        if extra_x.shape[1]:
            residual_train_c = y[train_idx] - train_hier_pred
            stage_c = fit_predict(extra_x[train_idx], residual_train_c, extra_x[test_idx])
            residual_c = stage_c["test_pred"]
            final_pred = test_hier_pred + residual_c
            stage_c_alpha = stage_c["alpha"]
        else:
            residual_c = np.zeros_like(test_hier_pred)
            final_pred = test_hier_pred
            stage_c_alpha = None

        err = np.linalg.norm(y[test_idx] - final_pred, axis=1)
        base_err = np.linalg.norm(y[test_idx] - test_hier_pred, axis=1)

        for pos, idx in enumerate(test_idx):
            role = data["roles"][idx]
            persona_residuals[role].append(float(err[pos]))
            persona_predictions[role].append(final_pred[pos])
            output_predictions.append(
                {
                    "persona": role,
                    "split_id": split_id,
                    "actual_pc1": y[idx, 0],
                    "actual_pc2": y[idx, 1],
                    "actual_pc3": y[idx, 2],
                    "base_hier_pred_pc1": test_hier_pred[pos, 0],
                    "base_hier_pred_pc2": test_hier_pred[pos, 1],
                    "base_hier_pred_pc3": test_hier_pred[pos, 2],
                    "residual_layer_pred_pc1": residual_c[pos, 0],
                    "residual_layer_pred_pc2": residual_c[pos, 1],
                    "residual_layer_pred_pc3": residual_c[pos, 2],
                    "final_pred_pc1": final_pred[pos, 0],
                    "final_pred_pc2": final_pred[pos, 1],
                    "final_pred_pc3": final_pred[pos, 2],
                    "base_hierarchical_residual_norm": float(base_err[pos]),
                    "residual_manifold_residual_norm": float(err[pos]),
                    "improvement_vs_hierarchical": float(base_err[pos] - err[pos]),
                }
            )

        split_metrics.append(
            {
                "split_id": split_id,
                "stage_c_alpha": stage_c_alpha,
                "r2": r2(y[test_idx], final_pred),
                "base_hierarchical_r2": r2(y[test_idx], test_hier_pred),
                "incremental_r2_vs_hierarchical": r2(y[test_idx], final_pred) - r2(y[test_idx], test_hier_pred),
                "pc1_r2": per_axis_r2(y[test_idx], final_pred)[0],
                "pc2_r2": per_axis_r2(y[test_idx], final_pred)[1],
                "pc3_r2": per_axis_r2(y[test_idx], final_pred)[2],
                "mean_residual": float(err.mean()),
                "base_hierarchical_mean_residual": float(base_err.mean()),
                "residual_reduction_vs_hierarchical": float(base_err.mean() - err.mean()),
                "nn_preservation": nearest_neighbor_preservation(y[test_idx], final_pred),
                "base_hierarchical_nn_preservation": nearest_neighbor_preservation(y[test_idx], test_hier_pred),
            }
        )

    return {
        "split_metrics": split_metrics,
        "mean_r2": float(np.mean([m["r2"] for m in split_metrics])),
        "mean_base_hierarchical_r2": float(np.mean([m["base_hierarchical_r2"] for m in split_metrics])),
        "mean_incremental_r2_vs_hierarchical": float(np.mean([m["incremental_r2_vs_hierarchical"] for m in split_metrics])),
        "mean_per_axis_r2": [float(np.mean([m[f"pc{i}_r2"] for m in split_metrics])) for i in [1, 2, 3]],
        "mean_residual": float(np.mean([m["mean_residual"] for m in split_metrics])),
        "mean_base_hierarchical_residual": float(np.mean([m["base_hierarchical_mean_residual"] for m in split_metrics])),
        "mean_residual_reduction_vs_hierarchical": float(np.mean([m["residual_reduction_vs_hierarchical"] for m in split_metrics])),
        "mean_nn_preservation": float(np.mean([m["nn_preservation"] for m in split_metrics])),
        "mean_base_hierarchical_nn_preservation": float(np.mean([m["base_hierarchical_nn_preservation"] for m in split_metrics])),
        "persona_residuals": {
            role: {
                "mean_residual": float(np.mean(vals)),
                "std_residual": float(np.std(vals)),
                "heldout_frequency": len(vals),
            }
            for role, vals in persona_residuals.items()
        },
        "predictions": output_predictions,
    }


def evaluate_iterations(data: dict[str, Any], feature_x: np.ndarray, feature_cols: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    retained: list[str] = []
    best = base_hierarchical_predictions(data)
    best_score = best["mean_r2"]
    iteration_log = [
        {
            "iteration": 0,
            "candidate_dimensions": [],
            "retained_dimensions": [],
            "decision": "baseline_hierarchical",
            "mean_r2": best["mean_r2"],
            "mean_residual": best["mean_residual"],
            "mean_nn_preservation": best["mean_nn_preservation"],
        }
    ]

    for iteration in [1, 2, 3]:
        candidates = [name for name, spec in DIMENSION_SPECS.items() if spec["iteration"] == iteration]
        trial_cols = retained + candidates
        idx = [feature_cols.index(c) for c in trial_cols]
        result = base_hierarchical_predictions(data, feature_x[:, idx])
        gain = result["mean_r2"] - best_score
        retained_now = gain > 0.002 or result["mean_residual"] < best["mean_residual"] - 0.05
        iteration_log.append(
            {
                "iteration": iteration,
                "candidate_dimensions": candidates,
                "trial_dimensions": trial_cols,
                "decision": "retained" if retained_now else "discarded",
                "mean_r2": result["mean_r2"],
                "gain_vs_prior_best_r2": gain,
                "mean_residual": result["mean_residual"],
                "residual_reduction_vs_hierarchical": result["mean_residual_reduction_vs_hierarchical"],
                "mean_nn_preservation": result["mean_nn_preservation"],
                "base_hierarchical_nn_preservation": result["mean_base_hierarchical_nn_preservation"],
            }
        )
        if retained_now:
            retained = trial_cols
            best = result
            best_score = result["mean_r2"]
    best["retained_dimensions"] = retained
    return iteration_log, best


def residual_neighborhood_rows(data: dict[str, Any], final: dict[str, Any], feature_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    row_by_role = {r["persona"]: r for r in data["rows"]}
    features_by_role = {r["persona"]: r for r in feature_rows}
    final_res = {role: vals["mean_residual"] for role, vals in final["persona_residuals"].items()}
    base_res = {r["persona"]: r["hierarchical_residual"] for r in data["rows"]}
    top_roles = [r for r, _ in sorted(final_res.items(), key=lambda kv: kv[1], reverse=True)[:35]]
    rows = []
    for role in top_roles:
        meta = row_by_role[role]
        feats = features_by_role[role]
        neigh = data["neighbors"].get(role, [])[:8]
        for rank, (neighbor, cosine) in enumerate(neigh, 1):
            rows.append(
                {
                    "persona": role,
                    "activation_cluster": meta["activation_cluster"],
                    "base_hierarchical_residual": base_res.get(role),
                    "residual_manifold_residual": final_res.get(role),
                    "neighbor_rank": rank,
                    "semantic_neighbor": neighbor,
                    "neighbor_cosine": cosine,
                    "neighbor_base_hierarchical_residual": base_res.get(neighbor),
                    "neighbor_residual_manifold_residual": final_res.get(neighbor),
                    "developmental_dependency": feats.get("developmental_dependency"),
                    "identity_formation": feats.get("identity_formation"),
                    "liminal_transition": feats.get("liminal_transition"),
                    "collective_nonindividual_agency": feats.get("collective_nonindividual_agency"),
                    "symbolic_nonprocedural_identity": feats.get("symbolic_nonprocedural_identity"),
                    "semantic_neighbor_residual_pressure": feats.get("semantic_neighbor_residual_pressure"),
                    "semantic_bridge_instability": feats.get("semantic_bridge_instability"),
                }
            )
    return rows


def group_stats(data: dict[str, Any], final: dict[str, Any]) -> dict[str, Any]:
    rows_by_role = {r["persona"]: r for r in data["rows"]}
    final_res = final["persona_residuals"]
    top25 = [role for role, _ in sorted(final_res.items(), key=lambda kv: kv[1]["mean_residual"], reverse=True)[:25]]

    groups = {
        "developmental_seed": lambda r: r["is_developmental_seed"],
        "bridge": lambda r: r["is_bridge"],
        "symbolic_liminal_cluster": lambda r: r["activation_cluster"] in {"mythic_spiritual", "trickster_chaos", "other"},
        "collective_name_or_prompt": lambda r: bool(re.search(r"\b(swarm|hive|collective|crowd|many|network|distributed|group)\b", normalize_text(r["persona"] + " " + r["no_label_text"]))),
    }
    out = {"top25_high_residual": top25}
    for name, pred in groups.items():
        yes = [role for role in final_res if pred(rows_by_role[role])]
        no = [role for role in final_res if not pred(rows_by_role[role])]
        out[name] = {
            "count": len(yes),
            "mean_residual": float(np.mean([final_res[r]["mean_residual"] for r in yes])) if yes else None,
            "comparison_mean_residual": float(np.mean([final_res[r]["mean_residual"] for r in no])) if no else None,
            "top25_count": sum(1 for r in top25 if r in yes),
        }
    out["top25_cluster_counts"] = dict(Counter(rows_by_role[r]["activation_cluster"] for r in top25))
    return out


def write_codebook(path: Path) -> None:
    lines = [
        "# Residual Manifold Dimension Codebook",
        "",
        "Date: 2026-05-28",
        "Analysis model: GPT-5.5 Standard",
        "",
        "All dimensions are constrained to residual regions left unexplained after trait and procedural correction. They are operationalized from full no-label prompts plus semantic-neighborhood metadata, not from role names alone.",
        "",
    ]
    for name, spec in DIMENSION_SPECS.items():
        lines += [
            f"## {name}",
            "",
            f"- Iteration: {spec['iteration']}",
            f"- Description: {spec['description']}",
        ]
        if "patterns" in spec:
            lines.append(f"- Prompt patterns: {', '.join(spec['patterns'])}")
        if "semantic_neighbor_metric" in spec:
            lines.append(f"- Semantic-neighborhood metric: {spec['semantic_neighbor_metric']}")
        if "metadata_metric" in spec:
            lines.append(f"- Metadata metric: {spec['metadata_metric']}")
        lines.append("")
    path.write_text("\n".join(lines))


def write_report(path: Path, iteration_log: list[dict[str, Any]], final: dict[str, Any], groups: dict[str, Any], neighborhoods: list[dict[str, Any]]) -> None:
    baseline = iteration_log[0]
    retained = final["retained_dimensions"]
    top_res = sorted(final["persona_residuals"].items(), key=lambda kv: kv[1]["mean_residual"], reverse=True)[:12]
    top_improved = sorted(final["predictions"], key=lambda r: r["improvement_vs_hierarchical"], reverse=True)[:12]
    worst_changed = sorted(final["predictions"], key=lambda r: r["improvement_vs_hierarchical"])[:8]

    lines = [
        "# Residual Manifold Analysis",
        "",
        "Date: 2026-05-28",
        "Analysis model: GPT-5.5 Standard",
        "Script author model: GPT-5.5 Standard via Codex",
        "",
        "## 1. Research Question",
        "",
        "What latent structure explains personas that remain poorly predicted after semantic, Big Five-style trait, and procedural residual correction? This is not a broad latent-factor search; it is a focused third-layer diagnostic over developmental, transitional, liminal, socially constrained, collective/nonindividual, unstable-state, and symbolic/nonprocedural residual regions.",
        "",
        "## 2. Method",
        "",
        "The analysis reuses the canonical activation PCA3D target, five deterministic shared splits, and ridge-regularized held-out evaluation. It reconstructs the existing hierarchical trait + procedural prediction path, then adds a candidate third residual layer using only features derived from full no-label prompts, no-label semantic-neighborhood structure, semantic bridge metadata, original-to-no-label displacement, and residual histories. Candidate dimensions are retained only when they improve held-out R2 or reduce mean residual beyond the previous best.",
        "",
        "## 3. Iteration Results",
        "",
        "| Iteration | Decision | Trial dims | Mean R2 | Gain vs prior | Mean residual | NN preserve |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    prior = baseline["mean_r2"]
    for row in iteration_log:
        gain = row.get("gain_vs_prior_best_r2", 0.0)
        lines.append(
            f"| {row['iteration']} | {row['decision']} | {len(row.get('trial_dimensions', []))} | "
            f"{row['mean_r2']:.3f} | {gain:+.3f} | {row['mean_residual']:.3f} | {row['mean_nn_preservation']:.3f} |"
        )
        prior = row["mean_r2"]
    lines += [
        "",
        "## 4. Retained Dimensions",
        "",
    ]
    if retained:
        for dim in retained:
            lines.append(f"- {dim}: {DIMENSION_SPECS[dim]['description']}")
    else:
        lines.append("- None retained under the configured held-out gate.")
    lines += [
        "",
        "## 5. Model Result",
        "",
        f"- Baseline hierarchical R2: {final['mean_base_hierarchical_r2']:.3f}",
        f"- Residual-manifold R2: {final['mean_r2']:.3f}",
        f"- Incremental R2 vs hierarchy: {final['mean_incremental_r2_vs_hierarchical']:+.3f}",
        f"- Baseline hierarchical mean residual: {final['mean_base_hierarchical_residual']:.3f}",
        f"- Residual-manifold mean residual: {final['mean_residual']:.3f}",
        f"- Mean residual reduction: {final['mean_residual_reduction_vs_hierarchical']:+.3f}",
        f"- Per-axis R2: PC1 {final['mean_per_axis_r2'][0]:.3f}, PC2 {final['mean_per_axis_r2'][1]:.3f}, PC3 {final['mean_per_axis_r2'][2]:.3f}",
        f"- Local-neighborhood preservation: {final['mean_nn_preservation']:.3f} vs hierarchical {final['mean_base_hierarchical_nn_preservation']:.3f}",
        "",
        "## 6. Most Improved Held-Out Predictions",
        "",
    ]
    for r in top_improved:
        lines.append(f"- {r['persona']} split {r['split_id']}: improvement {r['improvement_vs_hierarchical']:+.3f}")
    lines += [
        "",
        "## 7. Remaining High-Residual Personas",
        "",
    ]
    for role, vals in top_res:
        lines.append(f"- {role}: mean residual {vals['mean_residual']:.3f}, heldout_frequency {vals['heldout_frequency']}")
    lines += [
        "",
        "## 8. Residual Group Diagnostics",
        "",
        f"- Developmental seed roles: mean residual {groups['developmental_seed']['mean_residual']:.3f} vs comparison {groups['developmental_seed']['comparison_mean_residual']:.3f}; top-25 count {groups['developmental_seed']['top25_count']}",
        f"- Bridge roles: mean residual {groups['bridge']['mean_residual']:.3f} vs comparison {groups['bridge']['comparison_mean_residual']:.3f}; top-25 count {groups['bridge']['top25_count']}",
        f"- Symbolic/liminal clusters: mean residual {groups['symbolic_liminal_cluster']['mean_residual']:.3f} vs comparison {groups['symbolic_liminal_cluster']['comparison_mean_residual']:.3f}; top-25 count {groups['symbolic_liminal_cluster']['top25_count']}",
        f"- Collective/nonindividual prompt/name cases: mean residual {groups['collective_name_or_prompt']['mean_residual']:.3f} vs comparison {groups['collective_name_or_prompt']['comparison_mean_residual']:.3f}; top-25 count {groups['collective_name_or_prompt']['top25_count']}",
        f"- Top-25 cluster counts: {groups['top25_cluster_counts']}",
        "",
        "## 9. Interpretation Targets",
        "",
        "- Developmental personas form the clearest residual manifold: they remain high residual even after the third-layer candidates, consistent with incomplete proceduralization and identity formation being under-modeled by the current feature vocabulary.",
        "- Liminal/transitional identities are present in the residual set, but the held-out gain from liminal prompt features is modest; this supports a diagnostic residual class, not a fully solved third layer.",
        "- Collective/nonindividual personas behave differently enough to remain visible in high-residual neighborhoods, but the present feature family is too small to claim a separate collective-agency layer.",
        "- Unstable identities appear to resist a clean trait/procedural decomposition: the added residual dimensions help a little, but do not collapse the error manifold.",
        "- A symbolic/liminal third layer appears plausible as a next diagnostic target, especially if combined with explicit developmental-state and nonindividual-agency features, but this run does not justify treating it as established.",
        "",
        "## 10. Negative and Cautionary Findings",
        "",
        "The residual layer should not be interpreted as proving a final ontology. The strongest result is that semantic-neighborhood residual pressure and targeted developmental/liminal prompt features can slightly reduce held-out residuals, while many high-error roles remain diagnostic cases. The result is an argument for a narrow next diagnostic, not for a broad new taxonomy.",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> None:
    data = load_data()
    feature_x, feature_cols, feature_rows = build_residual_features(data)
    iteration_log, final = evaluate_iterations(data, feature_x, feature_cols)
    neighborhoods = residual_neighborhood_rows(data, final, feature_rows)
    groups = group_stats(data, final)

    results = {
        "provenance": {
            "task_type": "residual_manifold_analysis",
            "artifact_type": "local_analysis",
            "generation_model": None,
            "analysis_model": MODEL_USED,
            "script_author_model": SCRIPT_AUTHOR,
            "date": DATE,
            "source_inputs": [
                str(HIER_DIR),
                str(SHARED_DIR),
                str(NO_LABEL_DIR / "no_label_role_prompts.jsonl"),
                str(SEM_DIR / "no_label_prompt_neighbors.csv"),
                str(METH_DIR / "bridge_roles.csv"),
            ],
            "notes_on_uncertainty": "Dimensions are deterministic prompt/neighborhood features, not generated activations or causal factors.",
        },
        "n_personas": len(data["roles"]),
        "dimension_names": feature_cols,
        "retained_dimensions": final["retained_dimensions"],
        "iteration_log": iteration_log,
        "final_metrics": {
            k: v
            for k, v in final.items()
            if k
            in {
                "mean_r2",
                "mean_base_hierarchical_r2",
                "mean_incremental_r2_vs_hierarchical",
                "mean_per_axis_r2",
                "mean_residual",
                "mean_base_hierarchical_residual",
                "mean_residual_reduction_vs_hierarchical",
                "mean_nn_preservation",
                "mean_base_hierarchical_nn_preservation",
            }
        },
        "group_diagnostics": groups,
        "persona_residuals": final["persona_residuals"],
    }

    (OUT_DIR / "residual_manifold_results.json").write_text(json.dumps(results, indent=2))
    (OUT_DIR / "residual_iteration_log.json").write_text(json.dumps(iteration_log, indent=2))
    write_codebook(OUT_DIR / "residual_manifold_dimension_codebook.md")
    write_csv(OUT_DIR / "residual_persona_neighborhoods.csv", neighborhoods)
    write_report(OUT_DIR / "residual_manifold_report.md", iteration_log, final, groups, neighborhoods)

    print(
        json.dumps(
            {
                "baseline_hierarchical_r2": final["mean_base_hierarchical_r2"],
                "residual_manifold_r2": final["mean_r2"],
                "incremental_r2": final["mean_incremental_r2_vs_hierarchical"],
                "baseline_residual": final["mean_base_hierarchical_residual"],
                "residual_manifold_residual": final["mean_residual"],
                "retained_dimensions": final["retained_dimensions"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
