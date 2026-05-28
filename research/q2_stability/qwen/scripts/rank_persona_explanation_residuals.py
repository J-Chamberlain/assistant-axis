#!/usr/bin/env python3
"""
Rank persona-level explanation residuals for the iterative latent-feature loop.

This is local post-analysis only. It reconstructs the final retained feature
model from existing outer-loop artifacts and ranks personas by how well the
current feature vocabulary predicts activation PCA placement.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/iterative_outer_loop"
MASTER_LOG = OUT_DIR / "outer_loop_master_log.json"
CSV_OUT = OUT_DIR / "persona_explanation_rankings.csv"
JSON_OUT = OUT_DIR / "persona_explanation_rankings.json"
REPORT_OUT = OUT_DIR / "persona_explanation_rankings_report.md"
OUTER_SCRIPT = ROOT / "research/q2_stability/qwen/scripts/iterative_latent_feature_outer_loop.py"
MODEL_USED = "GPT-5.5 Standard"
DATE = "2026-05-28"


def load_outer_module():
    spec = importlib.util.spec_from_file_location("iterative_outer_loop_runtime", OUTER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {OUTER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["iterative_outer_loop_runtime"] = module
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def round_or_none(value: Any, ndigits: int = 6) -> float | None:
    if value is None:
        return None
    try:
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return round(float(value), ndigits)
    except Exception:
        return None


def residual(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    return np.linalg.norm(y - pred, axis=1)


def dimension_from_dict(outer: Any, item: dict[str, Any]):
    return outer.Dimension(
        item["family"],
        item["name"],
        item.get("description", ""),
        tuple(item.get("positive_terms", [])),
        tuple(item.get("negative_terms", [])),
        item.get("source", "outer-loop retained hypothesis"),
    )


def semantic_matrix_all(outer: Any, personas: list[dict[str, Any]]) -> np.ndarray:
    sem_all, _ = outer.semantic_features(personas, personas)
    return sem_all


def semantic_feature_width(outer: Any, personas: list[dict[str, Any]]) -> int:
    return semantic_matrix_all(outer, personas).shape[1]


def full_fit_predictions(outer: Any, personas: list[dict[str, Any]], dims: list[Any]) -> dict[str, Any]:
    all_roles = {p["role"] for p in personas}
    sem = semantic_matrix_all(outer, personas)
    coded = outer.code_dimensions(personas, dims, all_roles)
    x_final = np.hstack([sem, coded])
    y = np.array([[p["pca1"], p["pca2"], p["pca3"]] for p in personas], dtype=float)

    alpha_final = outer.kfold_alpha(x_final, y)
    xz, _ = outer.standardize(x_final, x_final)
    coef_final = outer.ridge_fit(xz, y, alpha_final)
    pred_final = outer.ridge_predict(xz, coef_final)

    alpha_sem = outer.kfold_alpha(sem, y)
    sz, _ = outer.standardize(sem, sem)
    coef_sem = outer.ridge_fit(sz, y, alpha_sem)
    pred_sem = outer.ridge_predict(sz, coef_sem)

    sem_width = sem.shape[1]
    dim_coef = coef_final[1 + sem_width :, :]
    x_mean = x_final.mean(axis=0, keepdims=True)
    x_std = x_final.std(axis=0, keepdims=True)
    x_std[x_std < 1e-9] = 1.0
    coded_z = ((x_final - x_mean) / x_std)[:, sem_width:]

    contribution_rows: list[list[str]] = []
    dim_names = [f"{d.family}/{d.name}" for d in dims]
    dim_strength = np.linalg.norm(dim_coef, axis=1)
    for i in range(len(personas)):
        scores = np.abs(coded_z[i]) * dim_strength
        active = [
            (dim_names[j], float(scores[j]), float(coded[i, j]))
            for j in np.argsort(-scores)[:6]
            if scores[j] > 1e-9 and coded[i, j] > 0
        ]
        contribution_rows.append([f"{name}={int(level)}" for name, _, level in active[:5]])

    return {
        "y": y,
        "pred_final": pred_final,
        "pred_semantic": pred_sem,
        "res_final": residual(y, pred_final),
        "res_semantic": residual(y, pred_sem),
        "contributions": contribution_rows,
        "alpha_final": alpha_final,
        "alpha_semantic": alpha_sem,
    }


def split_heldout_predictions(outer: Any, personas: list[dict[str, Any]], dims: list[Any]) -> dict[str, list[dict[str, Any]]]:
    by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for seed in outer.SPLIT_SEEDS:
        train, test = outer.split(personas, seed)
        train_roles = {p["role"] for p in train}
        ordered = train + test
        sem_train, sem_test = outer.semantic_features(train, test)
        coded = outer.code_dimensions(ordered, dims, train_roles)
        x_train = np.hstack([sem_train, coded[: len(train)]])
        x_test = np.hstack([sem_test, coded[len(train) :]])
        y_train = np.array([[p["pca1"], p["pca2"], p["pca3"]] for p in train], dtype=float)
        y_test = np.array([[p["pca1"], p["pca2"], p["pca3"]] for p in test], dtype=float)
        final_fit = outer.fit_predict(x_train, y_train, x_test, y_test)
        sem_fit = outer.fit_predict(sem_train, y_train, sem_test, y_test)
        final_res = residual(y_test, final_fit["pred"])
        sem_res = residual(y_test, sem_fit["pred"])
        for i, persona in enumerate(test):
            by_role[persona["role"]].append(
                {
                    "seed": seed,
                    "pred_final": final_fit["pred"][i].tolist(),
                    "pred_semantic": sem_fit["pred"][i].tolist(),
                    "final_residual": float(final_res[i]),
                    "semantic_residual": float(sem_res[i]),
                    "improvement": float(sem_res[i] - final_res[i]),
                }
            )
    return by_role


def anchor_bridge_status(persona: dict[str, Any]) -> str | None:
    if persona.get("stable_anchor"):
        return "stable_anchor"
    bridge_score = float(persona.get("bridge_score", 0.0))
    if bridge_score >= 4.0:
        return f"semantic_bridge_high_{bridge_score:.0f}"
    if bridge_score > 0.0:
        return f"semantic_bridge_{bridge_score:.0f}"
    return None


def build_rankings() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    outer = load_outer_module()
    master = json.loads(MASTER_LOG.read_text())
    personas = outer.load_personas()
    dims = [dimension_from_dict(outer, item) for item in master["final_retained_dimensions"]]
    full = full_fit_predictions(outer, personas, dims)
    heldout = split_heldout_predictions(outer, personas, dims)

    rows: list[dict[str, Any]] = []
    for i, persona in enumerate(personas):
        role = persona["role"]
        split_rows = heldout.get(role, [])
        if split_rows:
            mean_pred = np.array([r["pred_final"] for r in split_rows], dtype=float).mean(axis=0)
            mean_sem_pred = np.array([r["pred_semantic"] for r in split_rows], dtype=float).mean(axis=0)
            final_residual = float(np.mean([r["final_residual"] for r in split_rows]))
            semantic_residual = float(np.mean([r["semantic_residual"] for r in split_rows]))
            residual_std = float(np.std([r["final_residual"] for r in split_rows]))
            prediction_source = "mean_heldout_across_splits"
        else:
            mean_pred = full["pred_final"][i]
            mean_sem_pred = full["pred_semantic"][i]
            final_residual = float(full["res_final"][i])
            semantic_residual = float(full["res_semantic"][i])
            residual_std = None
            prediction_source = "apparent_full_model_no_heldout_split"

        improvement = semantic_residual - final_residual
        improvement_pct = None if semantic_residual <= 1e-12 else 100.0 * improvement / semantic_residual
        semantic_cluster = (
            f"original_prompt_k7={persona.get('original_prompt_k7')};"
            f"no_label_prompt_k7={persona.get('no_label_prompt_k7')};"
            f"role_name_k7={persona.get('role_name_k7')}"
        )
        rows.append(
            {
                "persona": role,
                "rank_most_explained": None,
                "rank_least_explained": None,
                "final_model_residual": round_or_none(final_residual),
                "semantic_baseline_residual": round_or_none(semantic_residual),
                "residual_improvement": round_or_none(improvement),
                "residual_improvement_percent": round_or_none(improvement_pct),
                "actual_pc1": round_or_none(persona["pca1"]),
                "actual_pc2": round_or_none(persona["pca2"]),
                "actual_pc3": round_or_none(persona["pca3"]),
                "predicted_pc1": round_or_none(mean_pred[0]),
                "predicted_pc2": round_or_none(mean_pred[1]),
                "predicted_pc3": round_or_none(mean_pred[2]),
                "semantic_baseline_predicted_pc1": round_or_none(mean_sem_pred[0]),
                "semantic_baseline_predicted_pc2": round_or_none(mean_sem_pred[1]),
                "semantic_baseline_predicted_pc3": round_or_none(mean_sem_pred[2]),
                "activation_cluster": persona.get("activation_cluster"),
                "semantic_cluster": semantic_cluster,
                "anchor_or_bridge_status": anchor_bridge_status(persona),
                "heldout_frequency": len(split_rows),
                "mean_residual_across_splits": round_or_none(np.mean([r["final_residual"] for r in split_rows]) if split_rows else None),
                "residual_std_across_splits": round_or_none(residual_std),
                "dimensions_features_most_associated_with_improved_prediction": "; ".join(full["contributions"][i]) if full["contributions"][i] else None,
                "prediction_source": prediction_source,
            }
        )

    by_most = sorted(rows, key=lambda r: (r["final_model_residual"] is None, r["final_model_residual"]))
    by_least = sorted(rows, key=lambda r: (r["final_model_residual"] is None, -(r["final_model_residual"] or -1)))
    for rank, row in enumerate(by_most, 1):
        row["rank_most_explained"] = rank
    for rank, row in enumerate(by_least, 1):
        row["rank_least_explained"] = rank
    rows.sort(key=lambda r: r["rank_most_explained"])

    metadata = {
        "model_used": MODEL_USED,
        "date": DATE,
        "n_personas": len(rows),
        "n_final_retained_dimensions": len(dims),
        "split_seeds": outer.SPLIT_SEEDS,
        "personas_with_heldout_predictions": sum(1 for r in rows if r["heldout_frequency"] > 0),
        "personas_without_heldout_predictions": sum(1 for r in rows if r["heldout_frequency"] == 0),
        "final_model_alpha_full_apparent": full["alpha_final"],
        "semantic_baseline_alpha_full_apparent": full["alpha_semantic"],
        "interpretation_note": (
            "final_model_residual uses mean held-out residual where the persona appeared in held-out splits; "
            "personas never held out use an apparent full-model residual and are marked in prediction_source."
        ),
        "metadata_gaps": [
            "No explicit all-persona final prediction artifact was stored by the original outer loop; this script reconstructs predictions from retained dimensions.",
            "Split-level held-out predictions were not stored by the original outer loop; this script recomputes them using the published deterministic split seeds.",
            "Anchor/bridge status is derived from stable_anchor_roles.csv and bridge_roles.csv rather than a dedicated outer-loop artifact.",
        ],
    }
    return rows, metadata


def table(rows: list[dict[str, Any]], cols: list[str], n: int = 12) -> list[str]:
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in rows[:n]:
        vals = []
        for col in cols:
            val = row.get(col)
            if isinstance(val, float):
                vals.append(f"{val:.3f}")
            else:
                vals.append("" if val is None else str(val))
        out.append("| " + " | ".join(vals) + " |")
    return out


def write_report(rows: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    most = sorted(rows, key=lambda r: r["rank_most_explained"])
    least = sorted(rows, key=lambda r: r["rank_least_explained"])
    improved = sorted(rows, key=lambda r: (r["residual_improvement"] is None, -(r["residual_improvement"] or -1)))
    worsened = sorted(rows, key=lambda r: (r["residual_improvement"] is None, r["residual_improvement"] if r["residual_improvement"] is not None else 1e9))
    recurrent = sorted(
        [r for r in rows if r["heldout_frequency"] and r["heldout_frequency"] >= 2],
        key=lambda r: (-(r["mean_residual_across_splits"] or 0), -r["heldout_frequency"]),
    )

    lines = [
        "# Persona Explanation Residual Rankings",
        "",
        f"Date: {DATE}",
        f"Model used: {MODEL_USED}",
        "",
        "## 1. Research Question",
        "",
        "Which personas are well explained by the current iterative latent-feature vocabulary, and which remain diagnostic residual cases relative to activation PCA geometry?",
        "",
        "## 2. Method",
        "",
        (
            "The script reconstructs the final retained outer-loop feature model from "
            "`outer_loop_master_log.json`, uses the original deterministic split code, "
            "and ranks all personas with PCA coordinates by residual norm in activation PCA3D space. "
            "For personas that appeared in one or more held-out splits, the primary residual is the mean "
            "held-out residual across those splits. For personas never held out by the five deterministic "
            "splits, the table uses an apparent full-model residual and marks `prediction_source` accordingly."
        ),
        "",
        f"Personas ranked: {metadata['n_personas']}. Personas with held-out prediction evidence: {metadata['personas_with_heldout_predictions']}. Personas without held-out split coverage: {metadata['personas_without_heldout_predictions']}. Retained dimensions: {metadata['n_final_retained_dimensions']}.",
        "",
        "Metadata gaps: " + " ".join(metadata["metadata_gaps"]),
        "",
        "## 3. Most Effectively Explained Personas",
        "",
        *table(most, ["persona", "final_model_residual", "semantic_baseline_residual", "residual_improvement", "activation_cluster", "prediction_source"], 15),
        "",
        "These are best described as well explained by the current feature vocabulary, not inherently simple or finally interpreted.",
        "",
        "## 4. Least Effectively Explained Personas",
        "",
        *table(least, ["persona", "final_model_residual", "semantic_baseline_residual", "residual_improvement", "activation_cluster", "heldout_frequency"], 15),
        "",
        "These are diagnostic residual cases: the current dimensions poorly explain their activation placement relative to other personas.",
        "",
        "## 5. Personas Most Improved Over Semantic Baseline",
        "",
        *table(improved, ["persona", "residual_improvement", "residual_improvement_percent", "final_model_residual", "semantic_baseline_residual", "activation_cluster"], 15),
        "",
        "Positive values mean the latent-feature model predicts activation placement better than the semantic baseline for that persona.",
        "",
        "## 6. Personas Worsened Relative to Semantic Baseline",
        "",
        *table(worsened, ["persona", "residual_improvement", "residual_improvement_percent", "final_model_residual", "semantic_baseline_residual", "activation_cluster"], 15),
        "",
        "Negative values mean the semantic baseline overpredicts or underpredicts activation placement less badly than the current feature vocabulary.",
        "",
        "## 7. Recurrent High-Residual Personas",
        "",
        *table(recurrent, ["persona", "mean_residual_across_splits", "residual_std_across_splits", "heldout_frequency", "activation_cluster", "anchor_or_bridge_status"], 15),
        "",
        "This section emphasizes personas with repeated held-out evidence rather than only apparent full-model residuals.",
        "",
        "## 8. Conceptual Interpretation",
        "",
        (
            "The ranking supports a bounded interpretation: some personas are well explained by the current "
            "feature vocabulary, especially where procedural, institutional, assistant-adjacent, or interactional "
            "signals map cleanly onto activation PCA placement. High-residual personas should be treated as "
            "diagnostic cases where current dimensions are incomplete, too coarse, or misweighted. The results "
            "do not prove final meanings of the dimensions and do not imply any persona is inherently inexplicable."
        ),
        "",
        "## 9. Recommended Diagnostic Follow-Ups",
        "",
        "- Add a sixth or leave-one-role-out split pass if every persona needs pure held-out coverage.",
        "- Inspect least-explained personas by activation cluster to determine whether residuals concentrate in developmental, mythic, social, or sparse-label regions.",
        "- Run a targeted paired-persona test for high-residual conceptual families, especially where semantic baseline and latent-feature predictions disagree.",
        "- Replace lexical feature coding with blind model-coded ordinal features and compare whether the same residual cases remain.",
        "- Track whether anchor or bridge roles are systematically overrepresented among high residuals.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    rows, metadata = build_rankings()
    write_csv(CSV_OUT, rows)
    JSON_OUT.write_text(json.dumps({"metadata": metadata, "rankings": rows}, indent=2))
    write_report(rows, metadata)
    print(f"Wrote {CSV_OUT}")
    print(f"Wrote {JSON_OUT}")
    print(f"Wrote {REPORT_OUT}")
    print(f"Rows: {len(rows)}")
    print("Most explained:", ", ".join(r["persona"] for r in sorted(rows, key=lambda x: x["rank_most_explained"])[:5]))
    print("Least explained:", ", ".join(r["persona"] for r in sorted(rows, key=lambda x: x["rank_least_explained"])[:5]))


if __name__ == "__main__":
    main()
