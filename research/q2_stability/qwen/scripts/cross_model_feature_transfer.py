#!/usr/bin/env python3
"""
Cross-target / cross-feature transfer comparison for Paper 1.5.

Compares Codex-derived latent features and Claude/Big-Five-style features on:
1. canonical activation PCA target
2. Big-Five-derived pseudo-PCA target

No pods, model calls, or activation generation are used.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = ROOT / "research/q2_stability/qwen/outputs/cross_model_feature_transfer"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTER_SCRIPT = ROOT / "research/q2_stability/qwen/scripts/iterative_latent_feature_outer_loop.py"
MASTER_LOG = ROOT / "research/q2_stability/qwen/outputs/iterative_outer_loop/outer_loop_master_log.json"
BIGFIVE_PATH = ROOT / "visualizations/bigfive_profiles.json"

RESULTS_JSON = OUT_DIR / "transfer_results.json"
SUMMARY_MD = OUT_DIR / "transfer_summary.md"
MATRIX_CSV = OUT_DIR / "feature_target_matrix.csv"
REPORT_MD = OUT_DIR / "codex_vs_claude_transfer_report.md"

MODEL_USED = "GPT-5.5 Standard"
DATE = "2026-05-28"
BIG_FIVE_TRAITS = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]


def load_outer_module():
    spec = importlib.util.spec_from_file_location("iterative_outer_loop_runtime_transfer", OUTER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {OUTER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["iterative_outer_loop_runtime_transfer"] = module
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


def dimension_from_dict(outer: Any, item: dict[str, Any]):
    return outer.Dimension(
        item["family"],
        item["name"],
        item.get("description", ""),
        tuple(item.get("positive_terms", [])),
        tuple(item.get("negative_terms", [])),
        item.get("source", "outer-loop retained hypothesis"),
    )


def zscore(x: np.ndarray) -> np.ndarray:
    mean = x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True)
    std[std < 1e-9] = 1.0
    return (x - mean) / std


def pca3(x: np.ndarray) -> tuple[np.ndarray, list[float]]:
    xz = zscore(x)
    _, s, vt = np.linalg.svd(xz, full_matrices=False)
    coords = xz @ vt[:3].T
    variance = (s**2) / max(1, len(xz) - 1)
    explained = variance / variance.sum()
    return coords[:, :3], [float(v) for v in explained[:3]]


def residual(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    return np.linalg.norm(y - pred, axis=1)


def evaluate_matrix(
    outer: Any,
    personas: list[dict[str, Any]],
    feature_matrix: np.ndarray,
    target_matrix: np.ndarray,
    include_semantic_baseline: bool = True,
) -> dict[str, Any]:
    split_rows = []
    for seed in outer.SPLIT_SEEDS:
        train, test = outer.split(personas, seed)
        role_to_idx = {p["role"]: i for i, p in enumerate(personas)}
        train_idx = [role_to_idx[p["role"]] for p in train]
        test_idx = [role_to_idx[p["role"]] for p in test]

        sem_train, sem_test = outer.semantic_features(train, test)
        x_train_raw = feature_matrix[train_idx]
        x_test_raw = feature_matrix[test_idx]
        if include_semantic_baseline:
            x_train = np.hstack([sem_train, x_train_raw])
            x_test = np.hstack([sem_test, x_test_raw])
        else:
            x_train, x_test = x_train_raw, x_test_raw
        y_train = target_matrix[train_idx]
        y_test = target_matrix[test_idx]

        fit = outer.fit_predict(x_train, y_train, x_test, y_test)
        baseline = outer.fit_predict(sem_train, y_train, sem_test, y_test)
        model_res = residual(y_test, fit["pred"])
        baseline_res = residual(y_test, baseline["pred"])
        split_rows.append(
            {
                "seed": seed,
                "r2": float(fit["r2"]),
                "baseline_r2": float(baseline["r2"]),
                "delta_vs_baseline": float(fit["r2"] - baseline["r2"]),
                "axis1_r2": float(fit["per_axis_r2"][0]),
                "axis2_r2": float(fit["per_axis_r2"][1]),
                "axis3_r2": float(fit["per_axis_r2"][2]),
                "baseline_axis1_r2": float(baseline["per_axis_r2"][0]),
                "baseline_axis2_r2": float(baseline["per_axis_r2"][1]),
                "baseline_axis3_r2": float(baseline["per_axis_r2"][2]),
                "mean_residual": float(model_res.mean()),
                "baseline_mean_residual": float(baseline_res.mean()),
                "mean_residual_reduction": float(baseline_res.mean() - model_res.mean()),
            }
        )

    return {
        "mean_r2": float(np.mean([r["r2"] for r in split_rows])),
        "std_r2": float(np.std([r["r2"] for r in split_rows])),
        "mean_baseline_r2": float(np.mean([r["baseline_r2"] for r in split_rows])),
        "mean_delta_vs_baseline": float(np.mean([r["delta_vs_baseline"] for r in split_rows])),
        "mean_per_axis_r2": [float(np.mean([r[f"axis{i}_r2"] for r in split_rows])) for i in [1, 2, 3]],
        "mean_baseline_per_axis_r2": [float(np.mean([r[f"baseline_axis{i}_r2"] for r in split_rows])) for i in [1, 2, 3]],
        "mean_residual": float(np.mean([r["mean_residual"] for r in split_rows])),
        "mean_baseline_residual": float(np.mean([r["baseline_mean_residual"] for r in split_rows])),
        "mean_residual_reduction": float(np.mean([r["mean_residual_reduction"] for r in split_rows])),
        "split_metrics": split_rows,
    }


def rounded(x: Any, n: int = 6) -> Any:
    if isinstance(x, float):
        return round(x, n)
    if isinstance(x, list):
        return [rounded(v, n) for v in x]
    return x


def condition_row(feature_family: str, target: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "feature_family": feature_family,
        "target": target,
        "mean_r2": round(result["mean_r2"], 6),
        "std_r2": round(result["std_r2"], 6),
        "semantic_baseline_r2": round(result["mean_baseline_r2"], 6),
        "delta_vs_semantic_baseline": round(result["mean_delta_vs_baseline"], 6),
        "axis1_r2": round(result["mean_per_axis_r2"][0], 6),
        "axis2_r2": round(result["mean_per_axis_r2"][1], 6),
        "axis3_r2": round(result["mean_per_axis_r2"][2], 6),
        "baseline_axis1_r2": round(result["mean_baseline_per_axis_r2"][0], 6),
        "baseline_axis2_r2": round(result["mean_baseline_per_axis_r2"][1], 6),
        "baseline_axis3_r2": round(result["mean_baseline_per_axis_r2"][2], 6),
        "mean_residual": round(result["mean_residual"], 6),
        "semantic_baseline_mean_residual": round(result["mean_baseline_residual"], 6),
        "mean_residual_reduction": round(result["mean_residual_reduction"], 6),
    }


def markdown_table(rows: list[dict[str, Any]]) -> list[str]:
    cols = [
        "feature_family",
        "target",
        "mean_r2",
        "semantic_baseline_r2",
        "delta_vs_semantic_baseline",
        "axis1_r2",
        "axis2_r2",
        "axis3_r2",
    ]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return lines


def main() -> None:
    outer = load_outer_module()
    master = json.loads(MASTER_LOG.read_text())
    bigfive = json.loads(BIGFIVE_PATH.read_text())
    personas = [p for p in outer.load_personas() if p["role"] in bigfive]
    personas = sorted(personas, key=lambda p: p["role"])

    retained_dims = [dimension_from_dict(outer, item) for item in master["final_retained_dimensions"]]
    all_roles = {p["role"] for p in personas}
    codex_features = outer.code_dimensions(personas, retained_dims, all_roles)
    bigfive_features = np.array([[float(bigfive[p["role"]][trait]) for trait in BIG_FIVE_TRAITS] for p in personas], dtype=float)

    canonical_target = np.array([[p["pca1"], p["pca2"], p["pca3"]] for p in personas], dtype=float)
    pseudo_target, pseudo_variance = pca3(bigfive_features)

    comparisons = {
        "codex_features__canonical_activation_pca": evaluate_matrix(outer, personas, codex_features, canonical_target),
        "claude_big_five__canonical_activation_pca": evaluate_matrix(outer, personas, bigfive_features, canonical_target),
        "codex_features__claude_big_five_pseudo_pca": evaluate_matrix(outer, personas, codex_features, pseudo_target),
        "claude_big_five__claude_big_five_pseudo_pca": evaluate_matrix(outer, personas, bigfive_features, pseudo_target),
    }

    rows = [
        condition_row("codex_derived_outer_loop_features", "canonical_activation_pca3", comparisons["codex_features__canonical_activation_pca"]),
        condition_row("claude_big_five_features", "canonical_activation_pca3", comparisons["claude_big_five__canonical_activation_pca"]),
        condition_row("codex_derived_outer_loop_features", "claude_big_five_pseudo_pca3", comparisons["codex_features__claude_big_five_pseudo_pca"]),
        condition_row("claude_big_five_features", "claude_big_five_pseudo_pca3", comparisons["claude_big_five__claude_big_five_pseudo_pca"]),
    ]
    write_csv(MATRIX_CSV, rows)

    bf_canonical = comparisons["claude_big_five__canonical_activation_pca"]["mean_delta_vs_baseline"]
    codex_pseudo = comparisons["codex_features__claude_big_five_pseudo_pca"]["mean_delta_vs_baseline"]
    codex_canonical = comparisons["codex_features__canonical_activation_pca"]["mean_delta_vs_baseline"]
    bf_pseudo = comparisons["claude_big_five__claude_big_five_pseudo_pca"]["mean_delta_vs_baseline"]

    def robust_improves(result: dict[str, Any]) -> bool:
        return result["mean_delta_vs_baseline"] > 0.01 and result["mean_residual_reduction"] > 0.0

    bf_canonical_ok = robust_improves(comparisons["claude_big_five__canonical_activation_pca"])
    codex_pseudo_ok = robust_improves(comparisons["codex_features__claude_big_five_pseudo_pca"])
    if bf_canonical_ok and codex_pseudo_ok:
        conclusion = "mixed_transfer_with_bidirectional_signal"
    elif bf_canonical_ok and not codex_pseudo_ok:
        conclusion = "big_five_transfers_to_activation_but_codex_does_not_transfer_to_pseudo_pca"
    elif not bf_canonical_ok and codex_pseudo_ok:
        conclusion = "codex_transfers_to_pseudo_pca_but_big_five_is_target_specific"
    else:
        conclusion = "mostly_target_specific_or_semantic_baseline_dominated"

    payload = {
        "metadata": {
            "date": DATE,
            "model_used": MODEL_USED,
            "analysis_model": MODEL_USED,
            "script_author_model": MODEL_USED,
            "n_personas": len(personas),
            "split_seeds": outer.SPLIT_SEEDS,
            "train_n": outer.TRAIN_N,
            "codex_feature_source": str(MASTER_LOG.relative_to(ROOT)),
            "claude_big_five_feature_source": str(BIGFIVE_PATH.relative_to(ROOT)),
            "canonical_activation_target_source": "research/visualizations/geometry_viz_data.json via iterative outer-loop loader",
            "claude_pseudo_pca_target_source": "reconstructed PCA3 from visualizations/bigfive_profiles.json",
            "claude_pseudo_pca_explained_variance": pseudo_variance,
            "semantic_baseline": "original_prompt_k7 + no_label_prompt_k7 + role_name_k7 one-hot features",
            "caveats": [
                "No separately committed Claude pseudo-PCA coordinate artifact was found; pseudo-PCA is reconstructed from local Big Five profiles.",
                "The Big Five feature source has no explicit per-file model provenance in the JSON; this analysis treats it as the available Claude/Big-Five feature artifact requested by the task.",
                "Claude Big Five features and Claude pseudo-PCA target are mathematically coupled, so the Big-Five-on-pseudo-PCA result is a positive-control style condition rather than independent validation.",
            ],
        },
        "comparisons": {k: rounded(v) for k, v in comparisons.items()},
        "summary": {
            "big_five_improves_canonical_activation_pca": bf_canonical_ok,
            "big_five_delta_on_canonical_activation_pca": round(bf_canonical, 6),
            "big_five_residual_reduction_on_canonical_activation_pca": round(comparisons["claude_big_five__canonical_activation_pca"]["mean_residual_reduction"], 6),
            "codex_improves_claude_pseudo_pca": codex_pseudo_ok,
            "codex_delta_on_claude_pseudo_pca": round(codex_pseudo, 6),
            "codex_residual_reduction_on_claude_pseudo_pca": round(comparisons["codex_features__claude_big_five_pseudo_pca"]["mean_residual_reduction"], 6),
            "codex_delta_on_canonical_activation_pca": round(codex_canonical, 6),
            "big_five_delta_on_claude_pseudo_pca": round(bf_pseudo, 6),
            "conclusion": conclusion,
        },
    }
    RESULTS_JSON.write_text(json.dumps(payload, indent=2))

    lines = [
        "# Cross-Model Feature Transfer Summary",
        "",
        f"Date: {DATE}",
        f"Model used: {MODEL_USED}",
        "",
        "## Question",
        "",
        "Do Claude Big Five features transfer to canonical activation PCA geometry, and do Codex-derived behavioral/procedural features transfer to a Claude/Big-Five-derived pseudo-PCA geometry?",
        "",
        "## Matrix",
        "",
        *markdown_table(rows),
        "",
        "## Direct Answers",
        "",
        f"- Big Five improves canonical activation PCA prediction: {'yes' if bf_canonical_ok else 'no'} (delta vs semantic baseline {bf_canonical:+.3f}; residual reduction {comparisons['claude_big_five__canonical_activation_pca']['mean_residual_reduction']:+.3f}).",
        f"- Codex features improve Claude pseudo-PCA prediction: {'yes' if codex_pseudo_ok else 'no'} (delta vs semantic baseline {codex_pseudo:+.3f}; residual reduction {comparisons['codex_features__claude_big_five_pseudo_pca']['mean_residual_reduction']:+.3f}).",
        f"- Overall interpretation: {conclusion.replace('_', ' ')}.",
        "",
        "## Caveat",
        "",
        "No separately committed Claude pseudo-PCA coordinate artifact was found. This run reconstructs the pseudo-PCA target from `visualizations/bigfive_profiles.json`, so the Big-Five-on-pseudo-PCA condition is a positive-control style condition rather than an independent target.",
    ]
    SUMMARY_MD.write_text("\n".join(lines) + "\n")

    report = [
        "# Codex vs Claude Feature Transfer Report",
        "",
        f"Date: {DATE}",
        f"Model used: {MODEL_USED}",
        "",
        "## 1. Research Question",
        "",
        "This comparison asks whether feature vocabularies transfer across targets. Specifically, it tests whether Claude Big Five features improve prediction of canonical Qwen activation PCA geometry, and whether Codex-derived behavioral/procedural latent features improve prediction of the Big-Five-derived pseudo-PCA target.",
        "",
        "## 2. Method",
        "",
        "The analysis reuses the iterative outer-loop persona loader, five deterministic split seeds, train size, ridge regression selection, per-axis R2, and semantic baseline. The semantic baseline is the same available one-hot cluster feature set: original-prompt k=7, no-label-prompt k=7, and role-name k=7. Codex features are the final 31 retained iterative outer-loop dimensions. Claude Big Five features are the five role-level scores in `visualizations/bigfive_profiles.json`. The pseudo-PCA target is reconstructed by PCA over those five Big Five dimensions because no separate Claude pseudo-PCA coordinate artifact was found locally.",
        "",
        "## 3. Results",
        "",
        *markdown_table(rows),
        "",
        "## 4. Per-Axis Pattern",
        "",
    ]
    for row in rows:
        report.append(
            f"- {row['feature_family']} on {row['target']}: "
            f"axis1={row['axis1_r2']:.3f}, axis2={row['axis2_r2']:.3f}, axis3={row['axis3_r2']:.3f}; "
            f"baseline axes=({row['baseline_axis1_r2']:.3f}, {row['baseline_axis2_r2']:.3f}, {row['baseline_axis3_r2']:.3f})."
        )
    report.extend(
        [
            "",
            "## 5. Interpretation",
            "",
            (
                f"Codex-derived features improve canonical activation PCA prediction by {codex_canonical:+.3f} R2 over the semantic baseline. "
                f"Claude Big Five features change canonical activation PCA prediction by {bf_canonical:+.3f} R2 over the same baseline. "
                f"Codex-derived features change the Big-Five pseudo-PCA target by {codex_pseudo:+.3f} R2, while Big Five features change their own pseudo-PCA target by {bf_pseudo:+.3f} R2."
            ),
            "",
            "The result should be read as mixed transfer only if both off-diagonal conditions improve R2 and reduce residuals relative to the semantic baseline. If only one off-diagonal condition passes both checks, the evidence supports asymmetric transfer. If neither off-diagonal condition passes, the evidence supports target specificity or semantic-baseline dominance under this operationalization.",
            "",
            f"This run's categorical conclusion is: **{conclusion.replace('_', ' ')}**.",
            "",
            "## 6. Limitations",
            "",
            "- The local Big Five profile JSON does not carry explicit Claude provenance metadata, so the analysis labels it as the available Claude/Big-Five feature source requested by the task.",
            "- The pseudo-PCA target is reconstructed from Big Five scores, not loaded from a dedicated Claude pseudo-PCA artifact.",
            "- Big-Five-on-pseudo-PCA is therefore a positive-control condition and should not be interpreted as independent evidence of transfer.",
            "- The comparison uses the existing lexical/ordinal Codex feature compiler and should be repeated with blind model-coded features if this result becomes central.",
            "",
            "## 7. Recommended Follow-Ups",
            "",
            "- Locate or generate a separately committed Claude pseudo-PCA artifact if one exists outside this repo snapshot, then rerun the same script without target reconstruction.",
            "- Add feature-score correlation analysis between Codex retained dimensions and Big Five dimensions.",
            "- Repeat the transfer matrix with leave-one-role-out coverage if all-persona held-out evidence is needed.",
            "- Add a third feature family from another model to distinguish Claude-specificity from Big-Five-specificity.",
        ]
    )
    REPORT_MD.write_text("\n".join(report) + "\n")

    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {SUMMARY_MD}")
    print(f"Wrote {MATRIX_CSV}")
    print(f"Wrote {REPORT_MD}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
