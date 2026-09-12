#!/usr/bin/env python3
"""Compute frozen Qwen-only trait-PC associations and family membership.

This script reads no human respondent records and no AA-7, Llama, or Gemma
results. It joins the canonical 275-role Qwen trait-affinity matrix to the
Qwen-only object isolated from the extended-PC viewer data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


QWEN_MODEL = "Qwen/Qwen3-32B"
MASTER_SEED = 20260912
PC_SEEDS = {pc: MASTER_SEED + pc for pc in range(1, 7)}
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_BATCH_SIZE = 50
FDR_THRESHOLD = 0.01
SIGN_STABILITY_THRESHOLD = 0.95
EFFECT_THRESHOLDS = (0.40, 0.50, 0.60)
PRIMARY_THRESHOLD = 0.50


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def qwen_object_from_multimodel_json(path: Path) -> dict[str, object]:
    """Parse only the exact top-level Qwen object from shared viewer JSON."""
    collecting = False
    depth = 0
    lines: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not collecting:
                if line.strip() == '"qwen": {':
                    collecting = True
                    lines.append("{")
                    depth = 1
                continue
            for char in line:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
            if depth == 0:
                break
            lines.append(line)
    if not collecting or depth != 0:
        raise ValueError(f"Could not isolate exact Qwen object from {path}")
    lines.append("}")
    return json.loads("".join(lines))


def bh_adjust(p_values: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjustment with stable ordering."""
    values = np.asarray(p_values, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError("BH input must be a finite one-dimensional array")
    m = len(values)
    order = np.argsort(values, kind="mergesort")
    ranked = values[order] * m / np.arange(1, m + 1, dtype=float)
    adjusted_sorted = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty(m, dtype=float)
    adjusted[order] = np.clip(adjusted_sorted, 0.0, 1.0)
    return adjusted


def bootstrap_sign_stability(
    x: np.ndarray,
    y: np.ndarray,
    observed: np.ndarray,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Vectorized role-bootstrap correlation signs for one PC."""
    rng = np.random.default_rng(seed)
    same = np.zeros(x.shape[1], dtype=np.int64)
    positive = np.zeros(x.shape[1], dtype=np.int64)
    negative = np.zeros(x.shape[1], dtype=np.int64)
    valid = np.zeros(x.shape[1], dtype=np.int64)
    remaining = BOOTSTRAP_RESAMPLES
    while remaining:
        batch = min(BOOTSTRAP_BATCH_SIZE, remaining)
        indices = rng.integers(0, x.shape[0], size=(batch, x.shape[0]))
        xb = x[indices, :]
        yb = y[indices]
        xc = xb - xb.mean(axis=1, keepdims=True)
        yc = yb - yb.mean(axis=1, keepdims=True)
        numerator = np.einsum("bnp,bn->bp", xc, yc, optimize=True)
        denominator = np.sqrt(
            np.einsum("bnp,bnp->bp", xc, xc, optimize=True)
            * np.einsum("bn,bn->b", yc, yc, optimize=True)[:, None]
        )
        with np.errstate(divide="ignore", invalid="ignore"):
            corr = numerator / denominator
        finite = np.isfinite(corr)
        valid += finite.sum(axis=0)
        positive += ((corr > 0) & finite).sum(axis=0)
        negative += ((corr < 0) & finite).sum(axis=0)
        same += (((corr > 0) & (observed > 0)) | ((corr < 0) & (observed < 0))).sum(axis=0)
        remaining -= batch
    stability = np.divide(same, valid, out=np.zeros_like(observed, dtype=float), where=valid > 0)
    positive_fraction = np.divide(positive, valid, out=np.zeros_like(observed, dtype=float), where=valid > 0)
    negative_fraction = np.divide(negative, valid, out=np.zeros_like(observed, dtype=float), where=valid > 0)
    return stability, positive_fraction, negative_fraction, BOOTSTRAP_RESAMPLES - valid


def deterministic_ranks(traits: list[str], correlations: np.ndarray) -> tuple[dict[str, int], dict[str, int]]:
    abs_order = sorted(range(len(traits)), key=lambda i: (-abs(correlations[i]), traits[i]))
    absolute = {traits[i]: rank for rank, i in enumerate(abs_order, 1)}
    positive_indices = [i for i, value in enumerate(correlations) if value >= 0]
    negative_indices = [i for i, value in enumerate(correlations) if value < 0]
    positive_order = sorted(positive_indices, key=lambda i: (-correlations[i], traits[i]))
    negative_order = sorted(negative_indices, key=lambda i: (correlations[i], traits[i]))
    pole = {traits[i]: rank for rank, i in enumerate(positive_order, 1)}
    pole.update({traits[i]: rank for rank, i in enumerate(negative_order, 1)})
    return absolute, pole


def load_inputs(repo: Path) -> tuple[pd.DataFrame, list[str], dict[str, str], float, list[Path]]:
    trait_path = repo / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
    viewer_path = repo / "research/outputs/extended_persona_pca/viewer_data.json"
    canonical_path = repo / "research/visualizations/geometry_viz_data.json"
    definition_path = repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_model_trait_candidate_crosswalk.csv"

    traits = pd.read_csv(trait_path)
    if traits.shape != (275, 241):
        raise ValueError(f"Expected 275 x 241 trait matrix including persona, got {traits.shape}")
    if traits["persona"].duplicated().any():
        raise ValueError("Duplicate personas in trait matrix")
    feature_names = [column for column in traits.columns if column != "persona"]
    if len(feature_names) != 240 or len(set(feature_names)) != 240:
        raise ValueError("Expected exactly 240 unique trait features")
    if not np.isfinite(traits[feature_names].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite trait-affinity value")

    qwen = qwen_object_from_multimodel_json(viewer_path)
    if qwen.get("label") != QWEN_MODEL or int(qwen.get("role_count", -1)) != 275:
        raise ValueError("Unexpected Qwen viewer metadata")
    point_rows = []
    for point in qwen["points"]:
        coords = point["coordinates"]
        if len(coords) < 6:
            raise ValueError("Qwen point lacks PC1-PC6")
        point_rows.append({"persona": point["persona"], **{f"PC{i}": coords[i - 1] for i in range(1, 7)}})
    points = pd.DataFrame(point_rows)
    if len(points) != 275 or points["persona"].duplicated().any():
        raise ValueError("Expected 275 unique Qwen viewer personas")
    merged = traits.merge(points, on="persona", how="inner", validate="one_to_one")
    if len(merged) != 275 or set(merged["persona"]) != set(traits["persona"]):
        raise ValueError("Trait and Qwen coordinate persona names do not align one-to-one")
    merged = merged.sort_values("persona", kind="mergesort").reset_index(drop=True)

    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))["roles"]
    canonical_lookup = dict(zip(canonical["names"], canonical["pca3d"], strict=True))
    max_error = 0.0
    for row in merged.itertuples(index=False):
        saved = canonical_lookup[row.persona]
        for pc in range(1, 4):
            max_error = max(max_error, abs(float(getattr(row, f"PC{pc}")) - float(saved[pc - 1])))

    crosswalk = pd.read_csv(definition_path)
    if len(crosswalk) != 240 or crosswalk["model_trait"].duplicated().any():
        raise ValueError("Canonical definition table must contain 240 unique model traits")
    definitions = dict(zip(crosswalk["model_trait"], crosswalk["canonical_definition"], strict=True))
    if set(definitions) != set(feature_names):
        raise ValueError("Canonical definitions and trait features do not match exactly")
    return merged, feature_names, definitions, max_error, [trait_path, viewer_path, canonical_path, definition_path]


def compute(repo: Path, output: Path, generated_at: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    merged, traits, definitions, coordinate_error, source_paths = load_inputs(repo)
    x = merged[traits].to_numpy(dtype=float)
    all_rows: list[dict[str, object]] = []
    sensitivity_rows: list[dict[str, object]] = []

    for pc in range(1, 7):
        y = merged[f"PC{pc}"].to_numpy(dtype=float)
        pearson_values = np.empty(len(traits), dtype=float)
        p_values = np.empty(len(traits), dtype=float)
        spearman_values = np.empty(len(traits), dtype=float)
        for index, trait in enumerate(traits):
            pearson_result = pearsonr(x[:, index], y)
            spearman_result = spearmanr(x[:, index], y)
            pearson_values[index] = float(pearson_result.statistic)
            p_values[index] = float(pearson_result.pvalue)
            spearman_values[index] = float(spearman_result.statistic)
        q_values = bh_adjust(p_values)
        stability, positive_fraction, negative_fraction, nonfinite = bootstrap_sign_stability(
            x, y, pearson_values, PC_SEEDS[pc]
        )
        absolute_ranks, pole_ranks = deterministic_ranks(traits, pearson_values)
        for index, trait in enumerate(traits):
            pole = "positive" if pearson_values[index] >= 0 else "negative"
            row = {
                "pc": f"PC{pc}",
                "trait": trait,
                "canonical_definition": definitions[trait],
                "pole": pole,
                "pearson_r": pearson_values[index],
                "pearson_r_squared": pearson_values[index] ** 2,
                "spearman_rho": spearman_values[index],
                "p_value": p_values[index],
                "BH_FDR_q": q_values[index],
                "bootstrap_sign_stability": stability[index],
                "bootstrap_positive_fraction": positive_fraction[index],
                "bootstrap_negative_fraction": negative_fraction[index],
                "bootstrap_nonfinite_count": int(nonfinite[index]),
                "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                "bootstrap_seed": PC_SEEDS[pc],
                "rank_by_absolute_r": absolute_ranks[trait],
                "rank_within_positive_or_negative_pole": pole_ranks[trait],
            }
            all_rows.append(row)
            for threshold in EFFECT_THRESHOLDS:
                passes_effect = abs(pearson_values[index]) >= threshold
                passes_fdr = q_values[index] < FDR_THRESHOLD
                passes_stability = stability[index] >= SIGN_STABILITY_THRESHOLD
                sensitivity_rows.append({
                    "pc": f"PC{pc}",
                    "pole": pole,
                    "trait": trait,
                    "abs_r_threshold": threshold,
                    "pearson_r": pearson_values[index],
                    "BH_FDR_q": q_values[index],
                    "bootstrap_sign_stability": stability[index],
                    "passes_effect_size": bool(passes_effect),
                    "passes_fdr": bool(passes_fdr),
                    "passes_sign_stability": bool(passes_stability),
                    "is_member": bool(passes_effect and passes_fdr and passes_stability),
                })

    associations = pd.DataFrame(all_rows).sort_values(
        ["pc", "rank_by_absolute_r", "trait"], kind="mergesort"
    )
    primary = associations[
        (associations["pearson_r"].abs() >= PRIMARY_THRESHOLD)
        & (associations["BH_FDR_q"] < FDR_THRESHOLD)
        & (associations["bootstrap_sign_stability"] >= SIGN_STABILITY_THRESHOLD)
    ].copy()
    primary = primary.sort_values(
        ["pc", "pole", "rank_within_positive_or_negative_pole", "trait"], kind="mergesort"
    )
    sensitivity = pd.DataFrame(sensitivity_rows).sort_values(
        ["abs_r_threshold", "pc", "pole", "trait"], kind="mergesort"
    )

    associations.to_csv(output / "qwen_trait_pc_correlations_all.csv", index=False, lineterminator="\n")
    primary.to_csv(output / "qwen_trait_family_membership_primary.csv", index=False, lineterminator="\n")
    sensitivity.to_csv(output / "qwen_trait_family_threshold_sensitivity.csv", index=False, lineterminator="\n")

    counts = {}
    for pc in range(1, 7):
        counts[f"PC{pc}"] = {}
        for pole in ("positive", "negative"):
            counts[f"PC{pc}"][pole] = {
                f"abs_r_{threshold:.2f}": int(
                    sensitivity[
                        (sensitivity["pc"] == f"PC{pc}")
                        & (sensitivity["pole"] == pole)
                        & np.isclose(sensitivity["abs_r_threshold"], threshold)
                        & sensitivity["is_member"]
                    ].shape[0]
                )
                for threshold in EFFECT_THRESHOLDS
            }

    manifest = {
        "analysis": "Correlation-defined Qwen trait families",
        "generated_at_utc": generated_at,
        "discovery_model": QWEN_MODEL,
        "role_count": int(len(merged)),
        "trait_count": len(traits),
        "pc_count": 6,
        "association_row_count": int(len(associations)),
        "primary_member_count": int(len(primary)),
        "unique_primary_trait_count": int(primary["trait"].nunique()),
        "bootstrap": {
            "master_seed": MASTER_SEED,
            "pc_seeds": {f"PC{pc}": seed for pc, seed in PC_SEEDS.items()},
            "resamples": BOOTSTRAP_RESAMPLES,
            "batch_size": BOOTSTRAP_BATCH_SIZE,
        },
        "thresholds": {
            "primary_absolute_pearson_r": PRIMARY_THRESHOLD,
            "sensitivity_absolute_pearson_r": list(EFFECT_THRESHOLDS),
            "BH_FDR_q_strictly_below": FDR_THRESHOLD,
            "bootstrap_sign_stability_at_least": SIGN_STABILITY_THRESHOLD,
        },
        "family_counts": counts,
        "canonical_pc1_pc3_max_abs_reproduction_error": coordinate_error,
        "source_hashes": {str(path.relative_to(repo)): sha256(path) for path in source_paths},
        "firewall": {
            "models_used": [QWEN_MODEL],
            "aa7_paths_opened": [],
            "llama_or_gemma_values_loaded": False,
            "prior_hypothesis_files_opened": [],
            "family_selection_inputs": [
                "canonical Qwen role-by-trait activation-cosine matrix",
                "Qwen-only PC1-PC6 role coordinates",
                "canonical trait definitions",
            ],
        },
        "compute": "CPU only; no GPU, RunPod, model inference, activation extraction, response generation, or external model API.",
    }
    (output / "numeric_source_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "association_rows": len(associations),
        "primary_members": len(primary),
        "unique_primary_traits": int(primary["trait"].nunique()),
        "canonical_pc1_pc3_max_abs_error": coordinate_error,
        "family_counts": counts,
    }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--generated-at", default="2026-09-12T19:00:00Z")
    args = parser.parse_args()
    compute(args.repo_root.resolve(), args.output_dir.resolve(), args.generated_at)


if __name__ == "__main__":
    main()
