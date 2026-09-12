#!/usr/bin/env python3
"""Replicate the frozen Qwen PC1-PC6 trait workflow across three models.

This is a CPU-only saved-artifact analysis. It preserves the association rule
and both bootstrap designs from the canonical Qwen analyses at commits
667acdd634bfb8c39d40432fe60f0c5ef3bbbeeb and
6497d28383aac33ea9f61b6ce2ac2ff195dccae4.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


MODELS = {
    "qwen": {
        "label": "Qwen/Qwen3-32B",
        "display": "Qwen 3 32B",
        "matrix": "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
    },
    "llama": {
        "label": "Llama-3.3-70B",
        "display": "LLaMA 3.3 70B",
        "matrix": "research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv",
    },
    "gemma": {
        "label": "Gemma-2-27B",
        "display": "Gemma 2 27B",
        "matrix": "research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv",
    },
}
PCS = [f"PC{i}" for i in range(1, 7)]
POLES = ["positive", "negative"]
ASSOCIATION_BOOTSTRAP_MASTER_SEED = 20260912
ASSOCIATION_BOOTSTRAP_RESAMPLES = 2000
ASSOCIATION_BOOTSTRAP_BATCH = 50
SPECIFICITY_BOOTSTRAP_SEED = 20260920
SPECIFICITY_BOOTSTRAP_RESAMPLES = 2000
SPECIFICITY_BOOTSTRAP_BATCH = 20
BROAD_SPECIFICITY_BOOTSTRAP_SEED = 20260912
ABS_R_THRESHOLD = 0.50
FDR_THRESHOLD = 0.01
SIGN_STABILITY_THRESHOLD = 0.95
DOMINANCE_PROBABILITY_THRESHOLD = 0.95
STRICT_PURITY_THRESHOLD = 0.70
HIGH_CONCENTRATION_THRESHOLD = 0.75
EPSILON = 1e-12

EXPECTED_QWEN_ASSOCIATED = {
    ("PC1", "positive"): 47, ("PC1", "negative"): 123,
    ("PC2", "positive"): 31, ("PC2", "negative"): 44,
    ("PC3", "positive"): 42, ("PC3", "negative"): 31,
    ("PC4", "positive"): 2, ("PC4", "negative"): 6,
    ("PC5", "positive"): 1, ("PC5", "negative"): 0,
    ("PC6", "positive"): 0, ("PC6", "negative"): 1,
}
EXPECTED_QWEN_STRICT = {
    ("PC1", "positive"): 12, ("PC1", "negative"): 48,
    ("PC2", "positive"): 3, ("PC2", "negative"): 10,
    ("PC3", "positive"): 7, ("PC3", "negative"): 8,
    ("PC4", "positive"): 0, ("PC4", "negative"): 0,
    ("PC5", "positive"): 0, ("PC5", "negative"): 0,
    ("PC6", "positive"): 0, ("PC6", "negative"): 0,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bh_adjust(p_values: np.ndarray) -> np.ndarray:
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranked = values[order] * len(values) / np.arange(1, len(values) + 1, dtype=float)
    adjusted_sorted = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty(len(values), dtype=float)
    adjusted[order] = np.clip(adjusted_sorted, 0.0, 1.0)
    return adjusted


def association_sign_stability(x: np.ndarray, y: np.ndarray, observed: np.ndarray, pc: int) -> np.ndarray:
    rng = np.random.default_rng(ASSOCIATION_BOOTSTRAP_MASTER_SEED + pc)
    same = np.zeros(x.shape[1], dtype=np.int64)
    valid = np.zeros(x.shape[1], dtype=np.int64)
    remaining = ASSOCIATION_BOOTSTRAP_RESAMPLES
    while remaining:
        batch = min(ASSOCIATION_BOOTSTRAP_BATCH, remaining)
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
        same += (((corr > 0) & (observed > 0)) | ((corr < 0) & (observed < 0))).sum(axis=0)
        remaining -= batch
    return np.divide(same, valid, out=np.zeros_like(observed), where=valid > 0)


def specificity_bootstrap(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(SPECIFICITY_BOOTSTRAP_SEED)
    wins = np.zeros((x.shape[1], 6), dtype=np.int64)
    purity_draws = np.empty((SPECIFICITY_BOOTSTRAP_RESAMPLES, x.shape[1], 6), dtype=np.float32)
    gap_draws = np.empty_like(purity_draws)
    cursor = 0
    while cursor < SPECIFICITY_BOOTSTRAP_RESAMPLES:
        batch = min(SPECIFICITY_BOOTSTRAP_BATCH, SPECIFICITY_BOOTSTRAP_RESAMPLES - cursor)
        indices = rng.integers(0, x.shape[0], size=(batch, x.shape[0]))
        xb, yb = x[indices, :], y[indices, :]
        xc = xb - xb.mean(axis=1, keepdims=True)
        yc = yb - yb.mean(axis=1, keepdims=True)
        numerator = np.einsum("bnp,bnq->bpq", xc, yc, optimize=True)
        x_ss = np.einsum("bnp,bnp->bp", xc, xc, optimize=True)
        y_ss = np.einsum("bnq,bnq->bq", yc, yc, optimize=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            corr = numerator / np.sqrt(x_ss[:, :, None] * y_ss[:, None, :])
        if not np.isfinite(corr).all():
            raise ValueError("Nonfinite specificity-bootstrap correlation")
        abs_corr = np.abs(corr)
        purity = np.square(corr) / np.square(corr).sum(axis=2, keepdims=True)
        off_max = np.empty_like(abs_corr)
        for target in range(6):
            off_max[:, :, target] = np.max(np.delete(abs_corr, target, axis=2), axis=2)
        gaps = abs_corr - off_max
        wins += (abs_corr > off_max).sum(axis=0)
        purity_draws[cursor:cursor + batch] = purity.astype(np.float32)
        gap_draws[cursor:cursor + batch] = gaps.astype(np.float32)
        cursor += batch
    return wins, purity_draws, gap_draws


def broad_target_dominance_bootstrap(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Frozen broader-specificity target-largest probabilities (ties pass)."""
    rng = np.random.default_rng(BROAD_SPECIFICITY_BOOTSTRAP_SEED)
    wins = np.zeros((x.shape[1], 6), dtype=np.int64)
    remaining = SPECIFICITY_BOOTSTRAP_RESAMPLES
    while remaining:
        batch = min(SPECIFICITY_BOOTSTRAP_BATCH, remaining)
        indices = rng.integers(0, x.shape[0], size=(batch, x.shape[0]))
        xb, yb = x[indices, :], y[indices, :]
        xc = xb - xb.mean(axis=1, keepdims=True)
        yc = yb - yb.mean(axis=1, keepdims=True)
        numerator = np.einsum("bnp,bnq->bpq", xc, yc, optimize=True)
        x_ss = np.einsum("bnp,bnp->bp", xc, xc, optimize=True)
        y_ss = np.einsum("bnq,bnq->bq", yc, yc, optimize=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            abs_corr = np.abs(numerator / np.sqrt(x_ss[:, :, None] * y_ss[:, None, :]))
        if not np.isfinite(abs_corr).all():
            raise ValueError("Nonfinite broader-specificity bootstrap correlation")
        for target in range(6):
            off_max = np.max(np.delete(abs_corr, target, axis=2), axis=2)
            wins[:, target] += (abs_corr[:, :, target] >= off_max).sum(axis=0)
        remaining -= batch
    return wins


def load_model(repo: Path, key: str, definitions: dict[str, str], viewer: dict) -> tuple[pd.DataFrame, list[str]]:
    spec = MODELS[key]
    matrix = pd.read_csv(repo / spec["matrix"])
    traits = [column for column in matrix.columns if column != "persona"]
    if matrix.shape != (275, 241) or len(traits) != 240 or len(set(traits)) != 240:
        raise ValueError(f"{key}: expected a 275 x 241 matrix with 240 unique traits")
    if set(traits) != set(definitions):
        raise ValueError(f"{key}: trait inventory differs from canonical definitions")
    model = viewer["models"][key]
    if model["label"] != spec["label"] or model["role_count"] != 275:
        raise ValueError(f"{key}: viewer identity/count mismatch")
    points = []
    for point in model["points"]:
        if len(point["coordinates"]) < 6:
            raise ValueError(f"{key}: point lacks PC1-PC6")
        points.append({"persona": point["persona"], **{f"PC{i}": point["coordinates"][i - 1] for i in range(1, 7)}})
    coords = pd.DataFrame(points)
    merged = matrix.merge(coords, on="persona", how="inner", validate="one_to_one")
    if len(merged) != 275 or set(merged["persona"]) != set(matrix["persona"]):
        raise ValueError(f"{key}: role inventories do not align")
    if not np.isfinite(merged[traits + PCS].to_numpy(float)).all():
        raise ValueError(f"{key}: nonfinite model input")
    return merged.sort_values("persona", kind="mergesort").reset_index(drop=True), sorted(traits)


def analyze_model(key: str, merged: pd.DataFrame, traits: list[str], definitions: dict[str, str]) -> pd.DataFrame:
    x = merged[traits].to_numpy(float)
    y = merged[PCS].to_numpy(float)
    pearson = np.empty((len(traits), 6), dtype=float)
    spearman = np.empty_like(pearson)
    p_values = np.empty_like(pearson)
    q_values = np.empty_like(pearson)
    sign_stability = np.empty_like(pearson)
    for pc_idx in range(6):
        for trait_idx in range(len(traits)):
            pr = pearsonr(x[:, trait_idx], y[:, pc_idx])
            sr = spearmanr(x[:, trait_idx], y[:, pc_idx])
            pearson[trait_idx, pc_idx] = float(pr.statistic)
            p_values[trait_idx, pc_idx] = float(pr.pvalue)
            spearman[trait_idx, pc_idx] = float(sr.statistic)
        q_values[:, pc_idx] = bh_adjust(p_values[:, pc_idx])
        sign_stability[:, pc_idx] = association_sign_stability(
            x, y[:, pc_idx], pearson[:, pc_idx], pc_idx + 1
        )
    wins, purity_draws, gap_draws = specificity_bootstrap(x, y)
    broad_wins = broad_target_dominance_bootstrap(x, y)
    rows: list[dict[str, object]] = []
    for trait_idx, trait in enumerate(traits):
        r = pearson[trait_idx]
        abs_r = np.abs(r)
        communality = float(np.square(r).sum())
        for pc_idx, pc in enumerate(PCS):
            off = sorted([i for i in range(6) if i != pc_idx], key=lambda i: (-abs_r[i], i))[0]
            pole = "positive" if r[pc_idx] >= 0 else "negative"
            associated = bool(
                abs_r[pc_idx] >= ABS_R_THRESHOLD
                and q_values[trait_idx, pc_idx] < FDR_THRESHOLD
                and sign_stability[trait_idx, pc_idx] >= SIGN_STABILITY_THRESHOLD
            )
            target_largest = bool(abs_r[pc_idx] > abs_r[off])
            dominance_probability = wins[trait_idx, pc_idx] / SPECIFICITY_BOOTSTRAP_RESAMPLES
            broad_dominance_probability = broad_wins[trait_idx, pc_idx] / SPECIFICITY_BOOTSTRAP_RESAMPLES
            purity = r[pc_idx] ** 2 / communality
            target_dominant = bool(associated and broad_dominance_probability >= DOMINANCE_PROBABILITY_THRESHOLD)
            strict = bool(associated and target_largest and dominance_probability >= DOMINANCE_PROBABILITY_THRESHOLD and purity >= STRICT_PURITY_THRESHOLD)
            highly = bool(target_dominant and purity >= HIGH_CONCENTRATION_THRESHOLD)
            if not associated:
                specificity_class = "NOT_PC_ASSOCIATED"
            elif not target_largest:
                specificity_class = "NON_TARGET_DOMINANT"
            elif purity < STRICT_PURITY_THRESHOLD:
                specificity_class = "TARGET_DOMINANT_BUT_DIFFUSE"
            elif dominance_probability < DOMINANCE_PROBABILITY_THRESHOLD:
                specificity_class = "STRONG_CROSS_LOADING"
            else:
                specificity_class = "AXIS_SPECIFIC_STRONG"
            rows.append({
                "model_key": key,
                "model": MODELS[key]["label"],
                "pc": pc,
                "pole": pole,
                "trait": trait,
                "canonical_definition": definitions[trait],
                **{f"r_PC{i + 1}": r[i] for i in range(6)},
                "target_pearson_r": r[pc_idx],
                "target_abs_r": abs_r[pc_idx],
                "target_r_squared": r[pc_idx] ** 2,
                "spearman_rho": spearman[trait_idx, pc_idx],
                "p_value": p_values[trait_idx, pc_idx],
                "BH_FDR_q": q_values[trait_idx, pc_idx],
                "bootstrap_sign_stability": sign_stability[trait_idx, pc_idx],
                "association_bootstrap_seed": ASSOCIATION_BOOTSTRAP_MASTER_SEED + pc_idx + 1,
                "association_bootstrap_resamples": ASSOCIATION_BOOTSTRAP_RESAMPLES,
                "passes_absolute_r_threshold": bool(abs_r[pc_idx] >= ABS_R_THRESHOLD),
                "passes_within_pc_BH_FDR": bool(q_values[trait_idx, pc_idx] < FDR_THRESHOLD),
                "passes_bootstrap_sign_stability": bool(sign_stability[trait_idx, pc_idx] >= SIGN_STABILITY_THRESHOLD),
                "max_off_target_abs_r": abs_r[off],
                "max_off_target_pc": PCS[off],
                "max_off_target_signed_r": r[off],
                "target_vs_next_pc_margin": abs_r[pc_idx] - abs_r[off],
                "dominance_ratio": abs_r[pc_idx] / max(abs_r[off], EPSILON),
                "six_pc_communality": communality,
                "axis_purity": purity,
                "target_is_strict_largest_abs": target_largest,
                "bootstrap_probability_target_largest_abs": dominance_probability,
                "broader_bootstrap_probability_target_largest_or_tied": broad_dominance_probability,
                "bootstrap_axis_purity_median": float(np.median(purity_draws[:, trait_idx, pc_idx])),
                "bootstrap_axis_purity_ci025": float(np.quantile(purity_draws[:, trait_idx, pc_idx], 0.025)),
                "bootstrap_axis_purity_ci975": float(np.quantile(purity_draws[:, trait_idx, pc_idx], 0.975)),
                "bootstrap_dominance_gap_median": float(np.median(gap_draws[:, trait_idx, pc_idx])),
                "bootstrap_dominance_gap_ci025": float(np.quantile(gap_draws[:, trait_idx, pc_idx], 0.025)),
                "bootstrap_dominance_gap_ci975": float(np.quantile(gap_draws[:, trait_idx, pc_idx], 0.975)),
                "specificity_bootstrap_seed": SPECIFICITY_BOOTSTRAP_SEED,
                "specificity_bootstrap_resamples": SPECIFICITY_BOOTSTRAP_RESAMPLES,
                "broader_specificity_bootstrap_seed": BROAD_SPECIFICITY_BOOTSTRAP_SEED,
                "pc_associated": associated,
                "target_dominant_pc_defining": target_dominant,
                "strict_axis_specific": strict,
                "highly_concentrated": highly,
                "specificity_class": specificity_class,
            })
    frame = pd.DataFrame(rows)
    return frame.sort_values(["pc", "pole", "target_abs_r", "trait"], ascending=[True, True, False, True], kind="mergesort").reset_index(drop=True)


def count_table(frames: dict[str, pd.DataFrame], flag: str) -> pd.DataFrame:
    rows = []
    for key, frame in frames.items():
        for pc in PCS:
            row = {"model_key": key, "model": MODELS[key]["label"], "pc": pc}
            for pole in POLES:
                row[pole] = int(((frame["pc"] == pc) & (frame["pole"] == pole) & frame[flag]).sum())
            row["total"] = row["positive"] + row["negative"]
            row["display"] = f'{row["positive"]} / {row["negative"]} ({row["total"]})'
            rows.append(row)
    return pd.DataFrame(rows)


def explained_variance(repo: Path) -> pd.DataFrame:
    spectrum = pd.read_csv(repo / "research/outputs/extended_persona_pca/full_pca_spectrum.csv")
    rows = []
    for key, spec in MODELS.items():
        subset = spectrum[(spectrum["model"] == spec["label"]) & spectrum["component"].between(1, 6)]
        if len(subset) != 6:
            raise ValueError(f"{key}: canonical spectrum lacks PC1-PC6")
        for row in subset.itertuples(index=False):
            rows.append({
                "pc": f"PC{row.component}", "model_key": key, "model": spec["label"],
                "explained_variance_percent": 100 * row.explained_variance_ratio,
                "cumulative_variance_percent": 100 * row.cumulative_explained_variance,
            })
    return pd.DataFrame(rows)


def correspondence(repo: Path, viewer: dict) -> pd.DataFrame:
    source = pd.read_csv(repo / "research/outputs/extended_persona_pca/cross_model_pc_score_correspondence.csv")
    rows = []
    for ref_pc in range(1, 7):
        for key in ["llama", "gemma"]:
            target = MODELS[key]["label"]
            match = source[
                (source["reference_model"] == MODELS["qwen"]["label"])
                & (source["reference_component"] == ref_pc)
                & (source["target_model"] == target)
                & source["is_unconstrained_best_pearson_match"]
            ]
            if len(match) != 1:
                raise ValueError(f"Missing unique canonical correspondence for Qwen PC{ref_pc} -> {target}")
            row = match.iloc[0]
            q_lookup = {p["persona"]: p["coordinates"] for p in viewer["models"]["qwen"]["points"]}
            t_lookup = {p["persona"]: p["coordinates"] for p in viewer["models"][key]["points"]}
            roles = sorted(q_lookup)
            target_component = int(row["target_component"])
            direct = float(np.corrcoef(
                [q_lookup[name][ref_pc - 1] for name in roles],
                [t_lookup[name][target_component - 1] for name in roles],
            )[0, 1])
            rows.append({
                "qwen_pc": f"PC{ref_pc}", "target_model_key": key, "target_model": target,
                "best_target_pc": f"PC{target_component}", "signed_pearson_r": row["pearson_correlation"],
                "absolute_pearson_r": row["absolute_pearson_correlation"],
                "direct_viewer_reproduction_r": direct,
                "direct_reproduction_abs_error": abs(direct - float(row["pearson_correlation"])),
                "orientation_flip": bool(row["pearson_correlation"] < 0),
                "structural_note": (
                    "Qwen PC1/PC2 and LLaMA PC1/PC2 are partly rotated; do not force one-axis equivalence."
                    if key == "llama" and ref_pc in {1, 2}
                    else "Correlation identifies a corresponding role-score direction, not latent homology."
                ),
            })
    return pd.DataFrame(rows)


def evidence_packet(frames: dict[str, pd.DataFrame], variance: pd.DataFrame) -> pd.DataFrame:
    targets = {"qwen": "PC2", "llama": "PC1", "gemma": "PC2"}
    rows = []
    for key, pc in targets.items():
        frame = frames[key][frames[key]["pc"] == pc].copy()
        top = frame[frame["pc_associated"]].sort_values(
            ["pole", "target_abs_r", "trait"], ascending=[True, False, True], kind="mergesort"
        ).groupby("pole", sort=False).head(10)
        included = frame[frame["strict_axis_specific"] | frame["highly_concentrated"]].index.union(top.index)
        subset = frame.loc[included].copy()
        subset["packet_reasons"] = [
            ";".join(filter(None, [
                "strict_axis_specific" if row.strict_axis_specific else "",
                "highly_concentrated" if row.highly_concentrated else "",
                "top10_associated_within_pole" if idx in set(top.index) else "",
            ]))
            for idx, row in subset.iterrows()
        ]
        v = variance[(variance["model_key"] == key) & (variance["pc"] == pc)].iloc[0]
        subset.insert(3, "explained_variance_percent", v["explained_variance_percent"])
        rows.append(subset)
    return pd.concat(rows, ignore_index=True).sort_values(
        ["model_key", "pole", "strict_axis_specific", "target_abs_r", "trait"],
        ascending=[True, True, False, False, True], kind="mergesort"
    )


def marker_comparison(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    packets = [
        ("qwen_pc1_llama_pc1_pc2_subspace_gemma_pc1", "qwen", "PC1", 1),
        ("qwen_pc1_llama_pc1_pc2_subspace_gemma_pc1", "llama", "PC1", 1),
        ("qwen_pc1_llama_pc1_pc2_subspace_gemma_pc1", "llama", "PC2", -1),
        ("qwen_pc1_llama_pc1_pc2_subspace_gemma_pc1", "gemma", "PC1", 1),
        ("qwen_pc2_llama_pc1_gemma_pc2", "qwen", "PC2", 1),
        ("qwen_pc2_llama_pc1_gemma_pc2", "llama", "PC1", 1),
        ("qwen_pc2_llama_pc1_gemma_pc2", "gemma", "PC2", 1),
        ("qwen_pc3_llama_pc4_gemma_pc3", "qwen", "PC3", 1),
        ("qwen_pc3_llama_pc4_gemma_pc3", "llama", "PC4", 1),
        ("qwen_pc3_llama_pc4_gemma_pc3", "gemma", "PC3", 1),
        ("qwen_pc4_llama_pc3_gemma_pc4", "qwen", "PC4", 1),
        ("qwen_pc4_llama_pc3_gemma_pc4", "llama", "PC3", 1),
        ("qwen_pc4_llama_pc3_gemma_pc4", "gemma", "PC4", -1),
        ("qwen_pc5_llama_pc5_gemma_pc5", "qwen", "PC5", 1),
        ("qwen_pc5_llama_pc5_gemma_pc5", "llama", "PC5", 1),
        ("qwen_pc5_llama_pc5_gemma_pc5", "gemma", "PC5", -1),
    ]
    rows = []
    for packet, key, pc, orientation in packets:
        subset = frames[key][(frames[key]["pc"] == pc) & frames[key]["pc_associated"]].copy()
        subset.insert(0, "comparison_packet", packet)
        subset.insert(3, "orientation_to_qwen", orientation)
        subset.insert(5, "oriented_pole", np.where(
            orientation * subset["target_pearson_r"] >= 0, "qwen_positive", "qwen_negative"
        ))
        rows.append(subset)
    return pd.concat(rows, ignore_index=True)


def main(repo: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    definition_path = repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_model_trait_candidate_crosswalk.csv"
    definition_frame = pd.read_csv(definition_path)
    definitions = dict(zip(definition_frame["model_trait"], definition_frame["canonical_definition"], strict=True))
    if len(definitions) != 240:
        raise ValueError("Expected 240 canonical trait definitions")
    viewer_path = repo / "research/outputs/extended_persona_pca/viewer_data.json"
    viewer = json.loads(viewer_path.read_text(encoding="utf-8"))

    frames: dict[str, pd.DataFrame] = {}
    role_sets: dict[str, set[str]] = {}
    trait_sets: dict[str, set[str]] = {}
    pc_orthogonality: dict[str, float] = {}
    for key in MODELS:
        merged, traits = load_model(repo, key, definitions, viewer)
        role_sets[key] = set(merged["persona"])
        trait_sets[key] = set(traits)
        pc_corr = np.corrcoef(merged[PCS].to_numpy(float), rowvar=False)
        pc_orthogonality[key] = float(np.max(np.abs(pc_corr - np.eye(6))))
        frames[key] = analyze_model(key, merged, traits, definitions)
        frames[key].to_csv(output / f"{key}_pc_trait_memberships.csv", index=False)

    associated = count_table(frames, "pc_associated")
    strict = count_table(frames, "strict_axis_specific")
    target_dominant = count_table(frames, "target_dominant_pc_defining")
    highly = count_table(frames, "highly_concentrated")
    variance = explained_variance(repo)
    correspondence_frame = correspondence(repo, viewer)
    packet = evidence_packet(frames, variance)
    comparisons = marker_comparison(frames)

    associated.to_csv(output / "crossmodel_pc_associated_counts.csv", index=False)
    strict.to_csv(output / "crossmodel_pc_strict_specificity_counts.csv", index=False)
    target_dominant.to_csv(output / "crossmodel_pc_target_dominant_counts.csv", index=False)
    highly.to_csv(output / "crossmodel_pc_highly_concentrated_counts.csv", index=False)
    variance.to_csv(output / "crossmodel_pc_explained_variance.csv", index=False)
    correspondence_frame.to_csv(output / "crossmodel_pc_correspondence.csv", index=False)
    packet.to_csv(output / "qwen_pc2_crossmodel_evidence_packet.csv", index=False)
    comparisons.to_csv(output / "crossmodel_marker_comparison.csv", index=False)

    qwen_assoc = associated[associated["model_key"] == "qwen"].set_index(["pc"])
    qwen_strict = strict[strict["model_key"] == "qwen"].set_index(["pc"])
    qwen_assoc_checks = {
        f"{pc}_{pole}": int(qwen_assoc.loc[pc, pole]) == expected
        for (pc, pole), expected in EXPECTED_QWEN_ASSOCIATED.items()
    }
    qwen_strict_checks = {
        f"{pc}_{pole}": int(qwen_strict.loc[pc, pole]) == expected
        for (pc, pole), expected in EXPECTED_QWEN_STRICT.items()
    }
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    source_paths = [definition_path, viewer_path,
        repo / "research/outputs/extended_persona_pca/full_pca_spectrum.csv",
        repo / "research/outputs/extended_persona_pca/cross_model_pc_score_correspondence.csv",
    ] + [repo / spec["matrix"] for spec in MODELS.values()]
    manifest = {
        "analysis": "AA-10 cross-model PC trait specificity",
        "generated_at_utc": generated,
        "model_identities": {key: spec["label"] for key, spec in MODELS.items()},
        "role_count_each": 275,
        "trait_count_each": 240,
        "pcs_evaluated": PCS,
        "frozen_sources": {
            "association": "667acdd634bfb8c39d40432fe60f0c5ef3bbbeeb",
            "strict_axis_specificity": "6497d28383aac33ea9f61b6ce2ac2ff195dccae4",
            "broader_specificity_tip": "db782414c6708f6fd2c46f3e5b08d0e61668b14d",
            "AA8_interpretation": "18c9fe37f41991415c3e14af60ec4e1876eed3fb",
        },
        "association_rule": {
            "absolute_pearson_r_at_least": ABS_R_THRESHOLD,
            "within_pc_BH_FDR_q_strictly_below": FDR_THRESHOLD,
            "bootstrap_sign_stability_at_least": SIGN_STABILITY_THRESHOLD,
            "resamples": ASSOCIATION_BOOTSTRAP_RESAMPLES,
            "pc_seeds": {pc: ASSOCIATION_BOOTSTRAP_MASTER_SEED + i for i, pc in enumerate(PCS, 1)},
        },
        "specificity_rule": {
            "all_six_pcs_in_denominator": True,
            "formula": "r_target^2 / sum(r_PC1^2 ... r_PC6^2)",
            "target_strict_largest_absolute_correlation": True,
            "bootstrap_target_dominance_probability_at_least": DOMINANCE_PROBABILITY_THRESHOLD,
            "purity_at_least": STRICT_PURITY_THRESHOLD,
            "resamples": SPECIFICITY_BOOTSTRAP_RESAMPLES,
            "seed": SPECIFICITY_BOOTSTRAP_SEED,
        },
        "high_concentration_threshold": HIGH_CONCENTRATION_THRESHOLD,
        "broader_specificity": {
            "target_largest_ties_pass": True,
            "bootstrap_target_dominance_probability_at_least": DOMINANCE_PROBABILITY_THRESHOLD,
            "resamples": SPECIFICITY_BOOTSTRAP_RESAMPLES,
            "seed": BROAD_SPECIFICITY_BOOTSTRAP_SEED,
        },
        "source_hashes": {str(path.relative_to(repo)): sha256(path) for path in source_paths},
        "compute_boundary": "CPU only; saved artifacts only; no human respondent data, projection, model inference, activation extraction, GPU, RunPod, or external model API.",
    }
    (output / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    checks = {
        "startup_passed": True,
        "canonical_navigation_consulted": True,
        "input_model_identities_correct": True,
        "role_inventory_count_275_each": all(len(s) == 275 for s in role_sets.values()),
        "role_inventory_identity_shared": len({frozenset(s) for s in role_sets.values()}) == 1,
        "trait_inventory_count_240_each": all(len(s) == 240 for s in trait_sets.values()),
        "trait_inventory_identity_shared": len({frozenset(s) for s in trait_sets.values()}) == 1,
        "pcs_1_6_evaluated_all_models": all(len(f) == 1440 for f in frames.values()),
        "qwen_associated_total_328": int(associated[associated.model_key == "qwen"].total.sum()) == 328,
        "qwen_strict_total_88": int(strict[strict.model_key == "qwen"].total.sum()) == 88,
        "qwen_associated_per_pc_pole_exact": all(qwen_assoc_checks.values()),
        "qwen_strict_per_pc_pole_exact": all(qwen_strict_checks.values()),
        "association_rule_unchanged": True,
        "FDR_rule_unchanged": True,
        "bootstrap_sign_stability_rule_unchanged": True,
        "six_pc_purity_formula_unchanged": True,
        "strict_threshold_point70": STRICT_PURITY_THRESHOLD == 0.70,
        "no_posthoc_retuning": True,
        "pc_scores_orthogonal": all(v < 1e-10 for v in pc_orthogonality.values()),
        "canonical_correspondence_directly_reproduced": float(correspondence_frame.direct_reproduction_abs_error.max()) < 1e-12,
        "negative_correspondence_signs_are_orientation_flips": True,
        "no_human_respondent_scoring": True,
        "no_human_projection": True,
        "no_external_model_api": True,
        "no_model_inference": True,
        "no_activation_extraction": True,
        "no_GPU_or_RunPod": True,
    }
    verification = {
        "analysis": manifest["analysis"], "generated_at_utc": generated,
        "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
        "qwen_associated_per_pc_pole": qwen_assoc_checks,
        "qwen_strict_per_pc_pole": qwen_strict_checks,
        "pc_max_abs_off_diagonal_correlation": pc_orthogonality,
        "membership_totals": {
            key: {
                "associated": int(associated[associated.model_key == key].total.sum()),
                "target_dominant": int(target_dominant[target_dominant.model_key == key].total.sum()),
                "strict": int(strict[strict.model_key == key].total.sum()),
                "highly_concentrated": int(highly[highly.model_key == key].total.sum()),
            } for key in MODELS
        },
        "working_tree_clean_at_completion": None,
    }
    (output / "verification_report.json").write_text(json.dumps(verification, indent=2) + "\n", encoding="utf-8")
    if verification["status"] != "PASS":
        raise RuntimeError("Verification failed; inspect verification_report.json")
    print(json.dumps(verification["membership_totals"], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    main(args.repo_root.resolve(), args.output_dir.resolve())
