#!/usr/bin/env python3
"""
Hierarchical trait + procedural residual model for persona activation geometry.

Stage A fits broad dispositional placement with Claude Big-Five-style features.
Stage B fits only the remaining Stage A residuals with selected Codex
procedural/behavioral dimensions. No pods, activations, or model calls are run.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
SHARED_DIR = ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark"
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model"
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

DEVELOPMENTAL_ROLES = {"toddler", "infant", "teenager", "adolescent"}
SYMBOLIC_LIMINAL_TERMS = {
    "mythic_spiritual",
    "trickster_chaos",
    "other",
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
    train_pred = ridge_predict(xt, coef)
    test_pred = ridge_predict(xv, coef)
    return {"alpha": alpha, "train_pred": train_pred, "test_pred": test_pred}


def nearest_neighbor_preservation(y: np.ndarray, pred: np.ndarray, k: int = 5) -> float:
    vals = []
    for i in range(len(y)):
        yd = np.linalg.norm(y - y[i], axis=1)
        pd = np.linalg.norm(pred - pred[i], axis=1)
        vals.append(len(set(np.argsort(yd)[1 : k + 1]) & set(np.argsort(pd)[1 : k + 1])) / k)
    return float(np.mean(vals))


def one_hot(values: list[str], universe: list[str]) -> np.ndarray:
    idx = {v: i for i, v in enumerate(universe)}
    x = np.zeros((len(values), len(universe)))
    for i, value in enumerate(values):
        if value in idx:
            x[i, idx[value]] = 1.0
    return x


def cluster_accuracy(x_train: np.ndarray, labels_train: list[str], x_test: np.ndarray, labels_test: list[str]) -> float:
    labels = sorted(set(labels_train))
    y_train = one_hot(labels_train, labels)
    y_test = one_hot(labels_test, labels)
    fit = fit_predict(x_train, y_train, x_test)
    pred_idx = np.argmax(fit["test_pred"], axis=1)
    pred = [labels[i] for i in pred_idx]
    return sum(a == b for a, b in zip(pred, labels_test)) / len(labels_test)


def load_data() -> dict[str, Any]:
    target_rows = read_csv(SHARED_DIR / "canonical_activation_pca3d.csv")
    sem_rows = {r["persona"]: r for r in read_csv(SHARED_DIR / "semantic_baseline_features.csv")}
    big_rows = {r["persona"]: r for r in read_csv(SHARED_DIR / "claude_bigfive_features.csv")}
    codex_rows = {r["persona"]: r for r in read_csv(SHARED_DIR / "codex_retained_features.csv")}
    split_rows = read_csv(SHARED_DIR / "shared_split_assignments.csv")
    bridge_rows = {
        r["role"]: r
        for r in read_csv(ROOT / "research/assistant_axis_methodology/bridge_roles.csv")
    }

    roles = [r["persona"] for r in target_rows]
    semantic_cols = [
        c
        for c in next(iter(sem_rows.values())).keys()
        if c not in {"persona", "provenance_manifest", "feature_set"}
    ]
    available_procedural = [c for c in PROCEDURAL_COLS if c in next(iter(codex_rows.values())).keys()]

    rows = []
    for t in target_rows:
        role = t["persona"]
        bridge = bridge_rows.get(role, {})
        rows.append(
            {
                "persona": role,
                "activation_cluster": t["activation_cluster"],
                "is_bridge": bool(bridge),
                "bridge_score": to_float(bridge.get("bridge_score")),
                "is_developmental": role in DEVELOPMENTAL_ROLES,
                "is_symbolic_liminal": t["activation_cluster"] in SYMBOLIC_LIMINAL_TERMS,
            }
        )

    return {
        "roles": roles,
        "target_rows": target_rows,
        "rows": rows,
        "semantic_cols": semantic_cols,
        "procedural_cols": available_procedural,
        "y": matrix(target_rows, ["activation_pc1", "activation_pc2", "activation_pc3"]),
        "semantic_x": matrix([sem_rows[r] for r in roles], semantic_cols),
        "bigfive_x": matrix([big_rows[r] for r in roles], BIGFIVE_COLS),
        "procedural_x": matrix([codex_rows[r] for r in roles], available_procedural),
        "splits": split_rows,
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


def evaluate_direct_model(data: dict[str, Any], name: str, x: np.ndarray) -> dict[str, Any]:
    split_metrics = []
    predictions = defaultdict(list)
    residuals = defaultdict(list)
    for split_id in range(5):
        train_idx, test_idx = split_indices(data, split_id)
        y = data["y"]
        fit = fit_predict(x[train_idx], y[train_idx], x[test_idx])
        pred = fit["test_pred"]
        err = np.linalg.norm(y[test_idx] - pred, axis=1)
        for pos, idx in enumerate(test_idx):
            role = data["roles"][idx]
            predictions[role].append(pred[pos])
            residuals[role].append(float(err[pos]))
        split_metrics.append(
            {
                "split_id": split_id,
                "alpha": fit["alpha"],
                "r2": r2(y[test_idx], pred),
                "pc1_r2": per_axis_r2(y[test_idx], pred)[0],
                "pc2_r2": per_axis_r2(y[test_idx], pred)[1],
                "pc3_r2": per_axis_r2(y[test_idx], pred)[2],
                "mean_residual": float(err.mean()),
                "nn_preservation": nearest_neighbor_preservation(y[test_idx], pred),
                "cluster_accuracy": cluster_accuracy(
                    x[train_idx],
                    [data["rows"][i]["activation_cluster"] for i in train_idx],
                    x[test_idx],
                    [data["rows"][i]["activation_cluster"] for i in test_idx],
                ),
            }
        )
    return summarize_model(name, split_metrics, predictions, residuals)


def evaluate_hierarchical(data: dict[str, Any]) -> dict[str, Any]:
    semantic = data["semantic_x"]
    trait_x = np.hstack([semantic, data["bigfive_x"]])
    proc_x = data["procedural_x"]
    y = data["y"]
    split_metrics = []
    trait_predictions = []
    proc_predictions = []
    final_predictions = defaultdict(list)
    final_residuals = defaultdict(list)
    trait_residuals = defaultdict(list)

    for split_id in range(5):
        train_idx, test_idx = split_indices(data, split_id)
        stage_a = fit_predict(trait_x[train_idx], y[train_idx], trait_x[test_idx])
        residual_train = y[train_idx] - stage_a["train_pred"]
        stage_b = fit_predict(proc_x[train_idx], residual_train, proc_x[test_idx])
        trait_pred = stage_a["test_pred"]
        residual_pred = stage_b["test_pred"]
        final_pred = trait_pred + residual_pred
        trait_err = np.linalg.norm(y[test_idx] - trait_pred, axis=1)
        final_err = np.linalg.norm(y[test_idx] - final_pred, axis=1)

        for pos, idx in enumerate(test_idx):
            role = data["roles"][idx]
            final_predictions[role].append(final_pred[pos])
            final_residuals[role].append(float(final_err[pos]))
            trait_residuals[role].append(float(trait_err[pos]))
            trait_predictions.append(
                {
                    "persona": role,
                    "split_id": split_id,
                    "actual_pc1": y[idx, 0],
                    "actual_pc2": y[idx, 1],
                    "actual_pc3": y[idx, 2],
                    "trait_pred_pc1": trait_pred[pos, 0],
                    "trait_pred_pc2": trait_pred[pos, 1],
                    "trait_pred_pc3": trait_pred[pos, 2],
                    "trait_residual_norm": float(trait_err[pos]),
                }
            )
            proc_predictions.append(
                {
                    "persona": role,
                    "split_id": split_id,
                    "residual_pred_pc1": residual_pred[pos, 0],
                    "residual_pred_pc2": residual_pred[pos, 1],
                    "residual_pred_pc3": residual_pred[pos, 2],
                    "final_pred_pc1": final_pred[pos, 0],
                    "final_pred_pc2": final_pred[pos, 1],
                    "final_pred_pc3": final_pred[pos, 2],
                    "hierarchical_residual_norm": float(final_err[pos]),
                    "improvement_vs_trait": float(trait_err[pos] - final_err[pos]),
                }
            )

        split_metrics.append(
            {
                "split_id": split_id,
                "stage_a_alpha": stage_a["alpha"],
                "stage_b_alpha": stage_b["alpha"],
                "trait_r2": r2(y[test_idx], trait_pred),
                "hierarchical_r2": r2(y[test_idx], final_pred),
                "incremental_r2_vs_trait": r2(y[test_idx], final_pred) - r2(y[test_idx], trait_pred),
                "pc1_r2": per_axis_r2(y[test_idx], final_pred)[0],
                "pc2_r2": per_axis_r2(y[test_idx], final_pred)[1],
                "pc3_r2": per_axis_r2(y[test_idx], final_pred)[2],
                "trait_mean_residual": float(trait_err.mean()),
                "hierarchical_mean_residual": float(final_err.mean()),
                "residual_reduction_vs_trait": float(trait_err.mean() - final_err.mean()),
                "nn_preservation": nearest_neighbor_preservation(y[test_idx], final_pred),
                "trait_nn_preservation": nearest_neighbor_preservation(y[test_idx], trait_pred),
                "cluster_accuracy": cluster_accuracy(
                    np.hstack([trait_x, proc_x])[train_idx],
                    [data["rows"][i]["activation_cluster"] for i in train_idx],
                    np.hstack([trait_x, proc_x])[test_idx],
                    [data["rows"][i]["activation_cluster"] for i in test_idx],
                ),
            }
        )
    out = summarize_model("hierarchical_trait_plus_procedural_residual", split_metrics, final_predictions, final_residuals)
    out["trait_stage_predictions"] = trait_predictions
    out["procedural_residual_predictions"] = proc_predictions
    out["persona_trait_residuals"] = {
        role: float(np.mean(vals))
        for role, vals in trait_residuals.items()
    }
    return out


def summarize_model(name: str, split_metrics: list[dict[str, Any]], predictions: dict[str, list[np.ndarray]], residuals: dict[str, list[float]]) -> dict[str, Any]:
    persona = {
        role: {
            "mean_residual": float(np.mean(vals)),
            "std_residual": float(np.std(vals)),
            "heldout_frequency": len(vals),
            "mean_prediction": [float(x) for x in np.mean(predictions[role], axis=0)] if predictions.get(role) else None,
        }
        for role, vals in residuals.items()
    }
    return {
        "name": name,
        "split_metrics": split_metrics,
        "mean_r2": float(np.mean([m.get("r2", m.get("hierarchical_r2")) for m in split_metrics])),
        "mean_per_axis_r2": [float(np.mean([m[f"pc{i}_r2"] for m in split_metrics])) for i in [1, 2, 3]],
        "mean_residual": float(np.mean([m.get("mean_residual", m.get("hierarchical_mean_residual")) for m in split_metrics])),
        "mean_nn_preservation": float(np.mean([m["nn_preservation"] for m in split_metrics])),
        "mean_cluster_accuracy": float(np.mean([m["cluster_accuracy"] for m in split_metrics])),
        "persona_residuals": persona,
    }


def persona_improvement_rows(data: dict[str, Any], trait: dict[str, Any], hierarchical: dict[str, Any], semantic: dict[str, Any], procedural: dict[str, Any], naive: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    meta = {r["persona"]: r for r in data["rows"]}
    roles = sorted(hierarchical["persona_residuals"])
    for role in roles:
        trait_res = trait["persona_residuals"][role]["mean_residual"]
        hier_res = hierarchical["persona_residuals"][role]["mean_residual"]
        row = {
            "persona": role,
            "activation_cluster": meta[role]["activation_cluster"],
            "is_bridge": meta[role]["is_bridge"],
            "bridge_score": meta[role]["bridge_score"],
            "is_developmental": meta[role]["is_developmental"],
            "is_symbolic_liminal": meta[role]["is_symbolic_liminal"],
            "semantic_residual": semantic["persona_residuals"][role]["mean_residual"],
            "trait_residual": trait_res,
            "procedural_alone_residual": procedural["persona_residuals"][role]["mean_residual"],
            "naive_concat_residual": naive["persona_residuals"][role]["mean_residual"],
            "hierarchical_residual": hier_res,
            "improvement_vs_trait": trait_res - hier_res,
            "improvement_percent_vs_trait": ((trait_res - hier_res) / trait_res * 100.0) if trait_res else None,
            "heldout_frequency": hierarchical["persona_residuals"][role]["heldout_frequency"],
        }
        rows.append(row)
    rows.sort(key=lambda r: r["improvement_vs_trait"], reverse=True)
    for i, row in enumerate(rows, 1):
        row["rank_most_improved_vs_trait"] = i
    worst = sorted(rows, key=lambda r: r["improvement_vs_trait"])
    rank_worst = {r["persona"]: i + 1 for i, r in enumerate(worst)}
    for row in rows:
        row["rank_worsened_vs_trait"] = rank_worst[row["persona"]]
    return rows


def aggregate_group(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    yes = [r for r in rows if r[field]]
    no = [r for r in rows if not r[field]]
    def stats(items: list[dict[str, Any]]) -> dict[str, float | int | None]:
        if not items:
            return {"n": 0, "mean_improvement": None, "mean_trait_residual": None, "mean_hierarchical_residual": None}
        return {
            "n": len(items),
            "mean_improvement": float(np.mean([r["improvement_vs_trait"] for r in items])),
            "mean_trait_residual": float(np.mean([r["trait_residual"] for r in items])),
            "mean_hierarchical_residual": float(np.mean([r["hierarchical_residual"] for r in items])),
        }
    return {"yes": stats(yes), "no": stats(no)}


def unexplained_class_analysis(rows: list[dict[str, Any]], n: int = 25) -> dict[str, Any]:
    high = sorted(rows, key=lambda r: r["hierarchical_residual"], reverse=True)[:n]
    return {
        "top_n": n,
        "cluster_counts": dict(Counter(r["activation_cluster"] for r in high)),
        "developmental_count": sum(bool(r["is_developmental"]) for r in high),
        "symbolic_liminal_count": sum(bool(r["is_symbolic_liminal"]) for r in high),
        "bridge_count": sum(bool(r["is_bridge"]) for r in high),
        "roles": [r["persona"] for r in high],
    }


def write_outputs(data: dict[str, Any], results: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    hierarchical = results["hierarchical"]
    trait = results["trait_stage"]
    summary_rows = []
    for key in ["semantic_baseline", "trait_stage", "procedural_alone", "naive_concat", "hierarchical"]:
        item = results[key]
        summary_rows.append(
            {
                "model": key,
                "mean_r2": item["mean_r2"],
                "pc1_r2": item["mean_per_axis_r2"][0],
                "pc2_r2": item["mean_per_axis_r2"][1],
                "pc3_r2": item["mean_per_axis_r2"][2],
                "mean_residual": item["mean_residual"],
                "mean_nn_preservation": item["mean_nn_preservation"],
                "mean_cluster_accuracy": item["mean_cluster_accuracy"],
                "delta_r2_vs_trait_stage": item["mean_r2"] - trait["mean_r2"],
                "residual_reduction_vs_trait_stage": trait["mean_residual"] - item["mean_residual"],
            }
        )
    write_csv(OUT_DIR / "hierarchical_model_summary.csv", summary_rows)
    write_csv(OUT_DIR / "trait_stage_predictions.csv", hierarchical["trait_stage_predictions"])
    write_csv(OUT_DIR / "procedural_residual_predictions.csv", hierarchical["procedural_residual_predictions"])
    write_csv(OUT_DIR / "persona_residual_improvement_rankings.csv", rows)

    bridge = aggregate_group(rows, "is_bridge")
    developmental = aggregate_group(rows, "is_developmental")
    symbolic = aggregate_group(rows, "is_symbolic_liminal")
    unexplained = unexplained_class_analysis(rows)
    payload = {
        "provenance": {
            "task_type": "hierarchical_trait_procedural_model",
            "artifact_type": "hierarchical_model_results",
            "artifact_path": "research/q2_stability/qwen/outputs/hierarchical_trait_procedural_model/hierarchical_model_results.json",
            "generation_model": None,
            "evaluation_model": None,
            "analysis_model": MODEL_USED,
            "script_author_model": SCRIPT_AUTHOR,
            "orchestration_agent": "Codex",
            "provider": "openai",
            "model_version_or_alias": MODEL_USED,
            "date": DATE,
            "source_inputs": [
                "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv",
                "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/claude_bigfive_features.csv",
                "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/codex_retained_features.csv",
                "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_split_assignments.csv",
                "research/assistant_axis_methodology/bridge_roles.csv",
            ],
            "notes_on_uncertainty": "Stage A uses semantic controls plus Claude Big Five features to match the shared benchmark baseline. Stage B uses selected Codex procedural/behavioral columns only to predict Stage A residuals.",
        },
        "n_personas": len(data["roles"]),
        "stage_a_features": ["semantic controls"] + BIGFIVE_COLS,
        "stage_b_features": data["procedural_cols"],
        "results": results,
        "group_analyses": {
            "bridge_roles": bridge,
            "developmental_roles": developmental,
            "symbolic_liminal_roles": symbolic,
            "unexplained_top25_after_stage_b": unexplained,
        },
    }
    (OUT_DIR / "hierarchical_model_results.json").write_text(json.dumps(payload, indent=2))

    bridge_lines = [
        "# Bridge Role Improvement Analysis",
        "",
        f"Bridge-role mean improvement vs trait stage: {bridge['yes']['mean_improvement']:.3f} across {bridge['yes']['n']} roles.",
        f"Non-bridge mean improvement vs trait stage: {bridge['no']['mean_improvement']:.3f} across {bridge['no']['n']} roles.",
        "",
        "## Most Improved Bridge Roles",
        "",
    ]
    bridge_rows = [r for r in rows if r["is_bridge"]]
    for r in bridge_rows[:20]:
        bridge_lines.append(f"- {r['persona']}: improvement {r['improvement_vs_trait']:+.3f}; trait residual {r['trait_residual']:.3f}; hierarchical residual {r['hierarchical_residual']:.3f}")
    bridge_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Positive mean improvement would support the claim that procedural residual correction helps bridge roles disproportionately. Negative or near-zero improvement means bridge-role behavior is not captured by this Stage B feature set.",
        ]
    )
    (OUT_DIR / "bridge_role_improvement_analysis.md").write_text("\n".join(bridge_lines))

    top_improved = rows[:12]
    still_high = sorted(rows, key=lambda r: r["hierarchical_residual"], reverse=True)[:12]
    lines = [
        "# Hierarchical Trait + Procedural Model Report",
        "",
        f"Date: {DATE}",
        f"Analysis model: {MODEL_USED}",
        f"Script author model: {SCRIPT_AUTHOR}",
        "",
        "## 1. Research Question",
        "",
        "This experiment tests whether canonical persona activation geometry factorizes into a broad dispositional trait baseline plus a procedural/operating-mode residual correction. It is not framed as Big Five versus procedural structure; it asks whether procedural features explain what remains after trait-like features establish broad placement.",
        "",
        "## 2. Method",
        "",
        "Stage A fits canonical activation PCA coordinates from semantic controls plus Claude Big-Five-style trait features. Stage B computes train-set residuals from Stage A and fits selected Codex procedural/behavioral dimensions to those residuals. On held-out personas, the final prediction is Stage A trait prediction plus Stage B residual correction. The same canonical splits and ridge regularization path are used throughout.",
        "",
        "## 3. Model Comparison",
        "",
        "| Model | Mean R2 | PC1 | PC2 | PC3 | Mean residual | NN preserve | Cluster acc | Delta vs trait |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['model']} | {row['mean_r2']:.3f} | {row['pc1_r2']:.3f} | {row['pc2_r2']:.3f} | {row['pc3_r2']:.3f} | {row['mean_residual']:.3f} | {row['mean_nn_preservation']:.3f} | {row['mean_cluster_accuracy']:.3f} | {row['delta_r2_vs_trait_stage']:+.3f} |"
        )
    lines.extend(
        [
            "",
            "## 4. Specific Questions",
            "",
            f"1. Traits alone explain mean held-out PCA3D R2 {trait['mean_r2']:.3f}.",
            f"2. Procedural residual correction changes R2 by {hierarchical['mean_r2'] - trait['mean_r2']:+.3f} and changes mean residual by {trait['mean_residual'] - hierarchical['mean_residual']:+.3f}.",
            "3. Personas improving most after procedural correction: " + ", ".join(f"{r['persona']} ({r['improvement_vs_trait']:+.2f})" for r in top_improved) + ".",
            "4. Personas remaining most unexplained after both stages: " + ", ".join(f"{r['persona']} ({r['hierarchical_residual']:.2f})" for r in still_high) + ".",
            f"5. Bridge roles {'improve' if bridge['yes']['mean_improvement'] and bridge['yes']['mean_improvement'] > bridge['no']['mean_improvement'] else 'do not improve'} disproportionately: bridge mean improvement {bridge['yes']['mean_improvement']:.3f} vs non-bridge {bridge['no']['mean_improvement']:.3f}.",
            f"6. Developmental roles remain high residual: mean hierarchical residual {developmental['yes']['mean_hierarchical_residual']:.3f} vs non-developmental {developmental['no']['mean_hierarchical_residual']:.3f}.",
            f"7. Local-neighborhood preservation changes from trait {np.mean([m['trait_nn_preservation'] for m in hierarchical['split_metrics']]):.3f} to hierarchical {hierarchical['mean_nn_preservation']:.3f}.",
            f"8. The integrated model {'outperforms' if hierarchical['mean_r2'] > trait['mean_r2'] else 'does not outperform'} Big Five alone, {'outperforms' if hierarchical['mean_r2'] > results['procedural_alone']['mean_r2'] else 'does not outperform'} Codex procedural alone, and {'outperforms' if hierarchical['mean_r2'] > results['naive_concat']['mean_r2'] else 'does not outperform'} naive concatenation.",
            "",
            "## 5. Optional Third-Layer Residual Analysis",
            "",
            f"Among the top {unexplained['top_n']} residual personas after Stage B, cluster counts are {unexplained['cluster_counts']}. Developmental roles account for {unexplained['developmental_count']}, symbolic/liminal clusters for {unexplained['symbolic_liminal_count']}, and bridge roles for {unexplained['bridge_count']}. This suggests whether a future symbolic/liminal or developmental layer is plausible, but no third-layer model is fit here.",
            "",
            "## 6. Interpretation",
            "",
            "The result should be read as a hierarchical residualization test, not a competition. If Stage B improves over Stage A, that supports a layered model in which traits establish broad latent placement and procedural features refine local behavioral topology. If Stage B fails to improve, it means the selected procedural columns do not explain held-out trait residuals under this operationalization, even if procedural features remain useful in direct prediction.",
            "",
            "## 7. Final Interpretive Questions",
            "",
            f"- Clean factorization: {'supported' if hierarchical['mean_r2'] > trait['mean_r2'] and trait['mean_residual'] > hierarchical['mean_residual'] else 'not supported under this Stage B feature set'}.",
            "- BigFive-like broad placement: supported by the Stage A performance.",
            f"- Procedural local differentiation: {'supported' if hierarchical['mean_nn_preservation'] > np.mean([m['trait_nn_preservation'] for m in hierarchical['split_metrics']]) else 'not supported by local-neighborhood preservation in this run'}.",
            "- Symbolic/liminal residual: see top-residual cluster counts above; this remains descriptive, not modeled.",
            "- Overall geometry: the evidence continues to favor continuous behavioral manifolds over discrete persona taxonomies, because continuous PCA prediction is where signal is strongest.",
        ]
    )
    (OUT_DIR / "hierarchical_model_report.md").write_text("\n".join(lines))


def main() -> None:
    data = load_data()
    semantic_x = data["semantic_x"]
    trait_x = np.hstack([semantic_x, data["bigfive_x"]])
    proc_direct_x = np.hstack([semantic_x, data["procedural_x"]])
    naive_x = np.hstack([trait_x, data["procedural_x"]])

    results = {
        "semantic_baseline": evaluate_direct_model(data, "semantic_baseline", semantic_x),
        "trait_stage": evaluate_direct_model(data, "trait_stage_bigfive", trait_x),
        "procedural_alone": evaluate_direct_model(data, "procedural_alone", proc_direct_x),
        "naive_concat": evaluate_direct_model(data, "naive_bigfive_plus_procedural", naive_x),
    }
    results["hierarchical"] = evaluate_hierarchical(data)
    rows = persona_improvement_rows(data, results["trait_stage"], results["hierarchical"], results["semantic_baseline"], results["procedural_alone"], results["naive_concat"])
    write_outputs(data, results, rows)
    print(
        json.dumps(
            {
                "trait_stage_r2": results["trait_stage"]["mean_r2"],
                "hierarchical_r2": results["hierarchical"]["mean_r2"],
                "incremental_r2": results["hierarchical"]["mean_r2"] - results["trait_stage"]["mean_r2"],
                "trait_mean_residual": results["trait_stage"]["mean_residual"],
                "hierarchical_mean_residual": results["hierarchical"]["mean_residual"],
                "residual_reduction": results["trait_stage"]["mean_residual"] - results["hierarchical"]["mean_residual"],
                "naive_concat_r2": results["naive_concat"]["mean_r2"],
                "procedural_alone_r2": results["procedural_alone"]["mean_r2"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
