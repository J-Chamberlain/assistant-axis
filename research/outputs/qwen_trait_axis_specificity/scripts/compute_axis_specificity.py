#!/usr/bin/env python3
"""Compute Qwen PC1-PC6 axis-specificity from frozen trait correlations.

The saved 1,440 correlations are the authoritative inputs. Role-level saved
scores are loaded only to verify the communality identity and to perform the
new fixed-seed bootstrap. No human respondent data or other model is loaded.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SOURCE_COMMIT = "667acdd634bfb8c39d40432fe60f0c5ef3bbbeeb"
PRIOR_HASHES = {
    "qwen_trait_pc_correlations_all.csv": "6ccbb08452af12ddf050fc95e083a0e0c4e2e01423c417cf2e9919909fd79424",
    "qwen_trait_family_membership_primary.csv": "cb010ab242747544ee5ba957e64b1565c8207565a76a9523cb5b837331237b97",
    "qwen_trait_family_human_mapping_judgments.csv": "cb4ac6b1338ce209ab2a88d24fac67c29abb3e6322055a4475b6b6dbc52e1f3c",
    "qwen_pc_trait_family_human_inventory.csv": "49f5b7c5c6b8f74d56ba2a2a410c4b9ebf4e3b4bf2459f013422fba0dfc37896",
    "verification_report.json": "d191f930c2f6a9d592ea856c8d1f5f0b458b17dbc4bc8a8fc1bc271a6b5ac8b8",
}
PCS = [f"PC{i}" for i in range(1, 7)]
POLES = ["positive", "negative"]
EPSILON = 1e-12
BOOTSTRAP_SEED = 20260920
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_BATCH = 20
PRIMARY_PURITY = 0.70
PRIMARY_DOMINANCE_PROBABILITY = 0.95
PURITY_SENSITIVITY = (0.60, 0.70, 0.80)
DOMINANCE_SENSITIVITY = (0.90, 0.95, 0.99)

EDITORIAL_COMPOSITES = [
    ("Exploration", ["creative", "abstract", "curious"]),
    ("Response", ["reactive", "adaptable", "practical"]),
    ("Scrutiny", ["skeptical", "analytical", "conscientious"]),
    ("Challenge", ["rebellious", "competitive", "manipulative"]),
    ("Affiliation", ["empathetic", "agreeable", "altruistic"]),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_prior_module(repo: Path):
    path = repo / "research/outputs/qwen_trait_family_human_inventory/scripts/compute_qwen_trait_families.py"
    spec = importlib.util.spec_from_file_location("prior_qwen_families", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def deterministic_rank(frame: pd.DataFrame, column: str) -> pd.Series:
    ordered = frame.sort_values([column, "trait"], ascending=[False, True], kind="mergesort")
    ranks = pd.Series(np.arange(1, len(frame) + 1), index=ordered.index)
    return ranks.reindex(frame.index).astype(int)


def build_metrics(corr: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if len(corr) != 1440 or corr["trait"].nunique() != 240 or set(corr["pc"]) != set(PCS):
        raise ValueError("Expected 240 traits x 6 PCs in saved correlation table")
    pivot = corr.pivot(index="trait", columns="pc", values="pearson_r").loc[:, PCS]
    definitions = corr.drop_duplicates("trait").set_index("trait")["canonical_definition"]
    rows: list[dict[str, object]] = []
    best_rows: list[dict[str, object]] = []
    for trait, values in pivot.iterrows():
        r = values.to_numpy(dtype=float)
        abs_r = np.abs(r)
        communality = float(np.square(r).sum())
        best_idx = int(np.argmax(abs_r))
        sorted_indices = sorted(range(6), key=lambda i: (-abs_r[i], i))
        second_idx = sorted_indices[1]
        best_rows.append(
            {
                "trait": trait,
                "canonical_definition": definitions.loc[trait],
                "best_pc": PCS[best_idx],
                "best_signed_r": r[best_idx],
                "best_abs_r": abs_r[best_idx],
                "best_axis_purity": r[best_idx] ** 2 / communality,
                "six_pc_communality": communality,
                "second_best_pc": PCS[second_idx],
                "second_best_abs_r": abs_r[second_idx],
                "dominance_gap": abs_r[best_idx] - abs_r[second_idx],
            }
        )
        source_by_pc = corr[corr["trait"] == trait].set_index("pc")
        for target_idx, pc in enumerate(PCS):
            off_indices = [i for i in range(6) if i != target_idx]
            off_idx = sorted(off_indices, key=lambda i: (-abs_r[i], i))[0]
            source = source_by_pc.loc[pc]
            rows.append(
                {
                    "pc": pc,
                    "trait": trait,
                    "canonical_definition": definitions.loc[trait],
                    "pole": source["pole"],
                    "target_r": r[target_idx],
                    "target_abs_r": abs_r[target_idx],
                    "target_r_squared": r[target_idx] ** 2,
                    "max_off_axis_abs_r": abs_r[off_idx],
                    "second_best_pc": PCS[off_idx],
                    "second_best_abs_r": abs_r[off_idx],
                    "dominance_gap": abs_r[target_idx] - abs_r[off_idx],
                    "dominance_ratio": abs_r[target_idx] / max(abs_r[off_idx], EPSILON),
                    "six_pc_communality": communality,
                    "axis_purity": r[target_idx] ** 2 / communality,
                    "target_is_largest_abs_loading": bool(abs_r[target_idx] > abs_r[off_idx]),
                    "spearman_rho": source["spearman_rho"],
                    "p_value": source["p_value"],
                    "BH_FDR_q": source["BH_FDR_q"],
                    "prior_bootstrap_sign_stability": source["bootstrap_sign_stability"],
                    "prior_bootstrap_seed": int(source["bootstrap_seed"]),
                    "prior_association_family_member": False,
                }
            )
    metrics = pd.DataFrame(rows)
    for pc in PCS:
        mask = metrics["pc"] == pc
        subset = metrics.loc[mask].copy()
        metrics.loc[mask, "rank_target_strength"] = deterministic_rank(subset, "target_abs_r").to_numpy()
        metrics.loc[mask, "rank_axis_purity"] = deterministic_rank(subset, "axis_purity").to_numpy()
        metrics.loc[mask, "rank_dominance_gap"] = deterministic_rank(subset, "dominance_gap").to_numpy()
    metrics[["rank_target_strength", "rank_axis_purity", "rank_dominance_gap"]] = metrics[
        ["rank_target_strength", "rank_axis_purity", "rank_dominance_gap"]
    ].astype(int)
    best = pd.DataFrame(best_rows).sort_values("trait", kind="mergesort").reset_index(drop=True)
    return metrics.sort_values(["pc", "trait"], kind="mergesort").reset_index(drop=True), best, pivot


def bootstrap_specificity(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return target-win counts, purity draws, and dominance-gap draws."""
    n, p = x.shape
    if y.shape != (n, 6) or p != 240:
        raise ValueError("Unexpected role score dimensions")
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    wins = np.zeros((p, 6), dtype=np.int64)
    purity_draws = np.empty((BOOTSTRAP_RESAMPLES, p, 6), dtype=np.float32)
    gap_draws = np.empty((BOOTSTRAP_RESAMPLES, p, 6), dtype=np.float32)
    cursor = 0
    while cursor < BOOTSTRAP_RESAMPLES:
        batch = min(BOOTSTRAP_BATCH, BOOTSTRAP_RESAMPLES - cursor)
        indices = rng.integers(0, n, size=(batch, n))
        xb = x[indices, :]
        yb = y[indices, :]
        xc = xb - xb.mean(axis=1, keepdims=True)
        yc = yb - yb.mean(axis=1, keepdims=True)
        numerator = np.einsum("bnp,bnq->bpq", xc, yc, optimize=True)
        x_ss = np.einsum("bnp,bnp->bp", xc, xc, optimize=True)
        y_ss = np.einsum("bnq,bnq->bq", yc, yc, optimize=True)
        denominator = np.sqrt(x_ss[:, :, None] * y_ss[:, None, :])
        with np.errstate(divide="ignore", invalid="ignore"):
            correlations = numerator / denominator
        if not np.isfinite(correlations).all():
            raise ValueError("Nonfinite correlation in bootstrap")
        abs_corr = np.abs(correlations)
        communality = np.square(correlations).sum(axis=2, keepdims=True)
        purity = np.square(correlations) / communality
        off_max = np.empty_like(abs_corr)
        for target in range(6):
            off_max[:, :, target] = np.max(np.delete(abs_corr, target, axis=2), axis=2)
        gaps = abs_corr - off_max
        win_batch = abs_corr > off_max
        wins += win_batch.sum(axis=0)
        purity_draws[cursor : cursor + batch] = purity.astype(np.float32)
        gap_draws[cursor : cursor + batch] = gaps.astype(np.float32)
        cursor += batch
    return wins, purity_draws, gap_draws


def summarize_bootstrap(
    traits: list[str], wins: np.ndarray, purity: np.ndarray, gaps: np.ndarray, corr: pd.DataFrame
) -> pd.DataFrame:
    prior = corr.set_index(["trait", "pc"])
    rows: list[dict[str, object]] = []
    for trait_idx, trait in enumerate(traits):
        for target_idx, pc in enumerate(PCS):
            pvals = purity[:, trait_idx, target_idx].astype(float)
            gvals = gaps[:, trait_idx, target_idx].astype(float)
            source = prior.loc[(trait, pc)]
            rows.append(
                {
                    "pc": pc,
                    "trait": trait,
                    "bootstrap_probability_target_largest_abs": wins[trait_idx, target_idx]
                    / BOOTSTRAP_RESAMPLES,
                    "bootstrap_axis_purity_median": np.median(pvals),
                    "bootstrap_axis_purity_ci025": np.quantile(pvals, 0.025),
                    "bootstrap_axis_purity_ci975": np.quantile(pvals, 0.975),
                    "bootstrap_dominance_gap_median": np.median(gvals),
                    "bootstrap_dominance_gap_ci025": np.quantile(gvals, 0.025),
                    "bootstrap_dominance_gap_ci975": np.quantile(gvals, 0.975),
                    "prior_bootstrap_sign_stability": source["bootstrap_sign_stability"],
                    "prior_bootstrap_seed": int(source["bootstrap_seed"]),
                    "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                    "bootstrap_specificity_seed": BOOTSTRAP_SEED,
                }
            )
    return pd.DataFrame(rows).sort_values(["pc", "trait"], kind="mergesort").reset_index(drop=True)


def mark_membership(
    metrics: pd.DataFrame, bootstrap: pd.DataFrame, prior_members: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    member_keys = set(zip(prior_members["pc"], prior_members["trait"], strict=True))
    metrics = metrics.copy()
    metrics["prior_association_family_member"] = [
        (pc, trait) in member_keys for pc, trait in zip(metrics["pc"], metrics["trait"], strict=True)
    ]
    combined = metrics.merge(
        bootstrap[
            [
                "pc",
                "trait",
                "bootstrap_probability_target_largest_abs",
                "bootstrap_axis_purity_median",
                "bootstrap_axis_purity_ci025",
                "bootstrap_axis_purity_ci975",
                "bootstrap_dominance_gap_median",
                "bootstrap_dominance_gap_ci025",
                "bootstrap_dominance_gap_ci975",
            ]
        ],
        on=["pc", "trait"],
        validate="one_to_one",
    )
    primary = (
        combined["prior_association_family_member"]
        & combined["target_is_largest_abs_loading"]
        & (combined["bootstrap_probability_target_largest_abs"] >= PRIMARY_DOMINANCE_PROBABILITY)
        & (combined["axis_purity"] >= PRIMARY_PURITY)
    )
    combined["primary_axis_specific_marker"] = primary
    marker_columns = [
        "pc",
        "pole",
        "trait",
        "canonical_definition",
        "target_r",
        "target_abs_r",
        "spearman_rho",
        "axis_purity",
        "dominance_gap",
        "dominance_ratio",
        "max_off_axis_abs_r",
        "second_best_pc",
        "bootstrap_probability_target_largest_abs",
        "bootstrap_axis_purity_median",
        "bootstrap_axis_purity_ci025",
        "bootstrap_axis_purity_ci975",
        "prior_bootstrap_sign_stability",
        "rank_target_strength",
        "rank_axis_purity",
        "rank_dominance_gap",
    ]
    markers = combined.loc[primary, marker_columns].sort_values(
        ["pc", "pole", "target_abs_r", "trait"], ascending=[True, True, False, True], kind="mergesort"
    )

    sensitivity_rows: list[dict[str, object]] = []
    for pc in PCS:
        for pole in POLES:
            family = combined[
                (combined["pc"] == pc)
                & (combined["pole"] == pole)
                & combined["prior_association_family_member"]
            ]
            for purity_threshold in PURITY_SENSITIVITY:
                for probability_threshold in DOMINANCE_SENSITIVITY:
                    selected = family[
                        family["target_is_largest_abs_loading"]
                        & (family["axis_purity"] >= purity_threshold)
                        & (family["bootstrap_probability_target_largest_abs"] >= probability_threshold)
                    ].sort_values(["target_abs_r", "trait"], ascending=[False, True], kind="mergesort")
                    sensitivity_rows.append(
                        {
                            "pc": pc,
                            "pole": pole,
                            "purity_threshold": purity_threshold,
                            "bootstrap_dominance_probability_threshold": probability_threshold,
                            "is_primary_threshold_pair": purity_threshold == PRIMARY_PURITY
                            and probability_threshold == PRIMARY_DOMINANCE_PROBABILITY,
                            "original_family_size": len(family),
                            "axis_specific_marker_count": len(selected),
                            "traits": ";".join(selected["trait"]),
                        }
                    )
    sensitivity = pd.DataFrame(sensitivity_rows)

    classification_rows: list[dict[str, object]] = []
    original = combined[combined["prior_association_family_member"]].copy()
    for row in original.itertuples(index=False):
        failures = []
        if not row.target_is_largest_abs_loading:
            category = "NON_TARGET_DOMINANT"
            failures.append(f"{row.second_best_pc} has larger |r| ({row.max_off_axis_abs_r:.6f})")
        elif row.axis_purity < PRIMARY_PURITY:
            category = "TARGET_DOMINANT_BUT_DIFFUSE"
            failures.append(f"axis purity {row.axis_purity:.6f} < {PRIMARY_PURITY:.2f}")
        elif row.bootstrap_probability_target_largest_abs < PRIMARY_DOMINANCE_PROBABILITY:
            category = "STRONG_CROSS_LOADING"
            failures.append(
                "bootstrap P(target largest) "
                f"{row.bootstrap_probability_target_largest_abs:.6f} < {PRIMARY_DOMINANCE_PROBABILITY:.2f}"
            )
        else:
            category = "AXIS_SPECIFIC_STRONG"
            failures.append("passes all frozen axis-specificity criteria")
        classification_rows.append(
            {
                "pc": row.pc,
                "pole": row.pole,
                "trait": row.trait,
                "target_r": row.target_r,
                "target_abs_r": row.target_abs_r,
                "axis_purity": row.axis_purity,
                "dominance_gap": row.dominance_gap,
                "max_off_axis_abs_r": row.max_off_axis_abs_r,
                "second_best_pc": row.second_best_pc,
                "bootstrap_probability_target_largest_abs": row.bootstrap_probability_target_largest_abs,
                "specificity_class": category,
                "classification_reason": "; ".join(failures),
            }
        )
    classification = pd.DataFrame(classification_rows).sort_values(
        ["pc", "pole", "target_abs_r", "trait"], ascending=[True, True, False, True], kind="mergesort"
    )
    return combined, markers.reset_index(drop=True), sensitivity, classification.reset_index(drop=True)


def family_comparison(
    combined: pd.DataFrame, markers: pd.DataFrame, sensitivity: pd.DataFrame, classification: pd.DataFrame
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for pc in PCS:
        for pole in POLES:
            family = combined[
                (combined["pc"] == pc)
                & (combined["pole"] == pole)
                & combined["prior_association_family_member"]
            ].sort_values(["target_abs_r", "trait"], ascending=[False, True], kind="mergesort")
            selected = markers[(markers["pc"] == pc) & (markers["pole"] == pole)]
            classes = classification[(classification["pc"] == pc) & (classification["pole"] == pole)]
            all_pole = combined[(combined["pc"] == pc) & (combined["pole"] == pole)].sort_values(
                ["axis_purity", "target_abs_r", "trait"], ascending=[False, False, True], kind="mergesort"
            )
            strongest = selected.sort_values(
                ["target_abs_r", "trait"], ascending=[False, True], kind="mergesort"
            )
            purest = selected.sort_values(["axis_purity", "trait"], ascending=[False, True], kind="mergesort")
            exploratory = combined[
                (combined["pc"] == pc)
                & (combined["pole"] == pole)
                & combined["target_is_largest_abs_loading"]
                & (combined["target_abs_r"] >= 0.30)
            ].sort_values(["axis_purity", "target_abs_r", "trait"], ascending=[False, False, True], kind="mergesort")
            if pc not in {"PC4", "PC5", "PC6"}:
                exploratory = exploratory.iloc[0:0]
            sens = sensitivity[(sensitivity["pc"] == pc) & (sensitivity["pole"] == pole)]
            count_map = {
                (float(r.purity_threshold), float(r.bootstrap_dominance_probability_threshold)): int(
                    r.axis_specific_marker_count
                )
                for r in sens.itertuples(index=False)
            }
            rows.append(
                {
                    "pc": pc,
                    "axis_status": "strict_core" if pc in {"PC1", "PC2", "PC3"} else "supported_secondary_provisional",
                    "pole": pole,
                    "original_association_family_size": len(family),
                    "axis_specific_marker_count": len(selected),
                    "retention_percentage": 100.0 * len(selected) / len(family) if len(family) else math.nan,
                    "retained_traits": ";".join(selected["trait"]),
                    "removed_non_target_dominant": ";".join(
                        classes.loc[classes["specificity_class"] == "NON_TARGET_DOMINANT", "trait"]
                    ),
                    "removed_diffuse": ";".join(
                        classes.loc[classes["specificity_class"] == "TARGET_DOMINANT_BUT_DIFFUSE", "trait"]
                    ),
                    "removed_bootstrap_cross_loading": ";".join(
                        classes.loc[classes["specificity_class"] == "STRONG_CROSS_LOADING", "trait"]
                    ),
                    "strongest_axis_specific_marker": strongest.iloc[0]["trait"] if len(strongest) else "",
                    "strongest_axis_specific_marker_abs_r": strongest.iloc[0]["target_abs_r"]
                    if len(strongest)
                    else math.nan,
                    "purest_strong_marker": purest.iloc[0]["trait"] if len(purest) else "",
                    "purest_strong_marker_axis_purity": purest.iloc[0]["axis_purity"] if len(purest) else math.nan,
                    "highest_purity_marker_regardless_of_strength": all_pole.iloc[0]["trait"] if len(all_pole) else "",
                    "highest_purity_regardless_of_strength": all_pole.iloc[0]["axis_purity"] if len(all_pole) else math.nan,
                    "original_family_median_target_abs_r": family["target_abs_r"].median()
                    if len(family)
                    else math.nan,
                    "original_family_median_axis_purity": family["axis_purity"].median()
                    if len(family)
                    else math.nan,
                    "original_family_median_dominance_gap": family["dominance_gap"].median()
                    if len(family)
                    else math.nan,
                    "primary_marker_median_target_abs_r": selected["target_abs_r"].median()
                    if len(selected)
                    else math.nan,
                    "primary_marker_median_axis_purity": selected["axis_purity"].median()
                    if len(selected)
                    else math.nan,
                    "primary_marker_median_dominance_gap": selected["dominance_gap"].median()
                    if len(selected)
                    else math.nan,
                    "sensitivity_count_purity60_probability95": count_map[(0.60, 0.95)],
                    "sensitivity_count_purity70_probability90": count_map[(0.70, 0.90)],
                    "sensitivity_count_primary_purity70_probability95": count_map[(0.70, 0.95)],
                    "sensitivity_count_purity70_probability99": count_map[(0.70, 0.99)],
                    "sensitivity_count_purity80_probability95": count_map[(0.80, 0.95)],
                    "exploratory_top10_target_dominant_abs_r_ge_0_30": ";".join(exploratory.head(10)["trait"]),
                }
            )
    return pd.DataFrame(rows)


def pareto_front(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pc in PCS:
        frame = metrics[metrics["pc"] == pc].copy()
        values = frame[["target_abs_r", "axis_purity"]].to_numpy(float)
        keep = np.ones(len(frame), dtype=bool)
        for i in range(len(frame)):
            dominates = (
                (values[:, 0] >= values[i, 0])
                & (values[:, 1] >= values[i, 1])
                & ((values[:, 0] > values[i, 0]) | (values[:, 1] > values[i, 1]))
            )
            if dominates.any():
                keep[i] = False
        front = frame.loc[keep].sort_values(
            ["target_abs_r", "axis_purity", "trait"], ascending=[False, False, True], kind="mergesort"
        )
        for order, row in enumerate(front.itertuples(index=False), 1):
            rows.append(
                {
                    "pc": pc,
                    "pareto_order_by_strength": order,
                    "trait": row.trait,
                    "pole": row.pole,
                    "target_r": row.target_r,
                    "target_abs_r": row.target_abs_r,
                    "axis_purity": row.axis_purity,
                    "dominance_gap": row.dominance_gap,
                    "prior_association_family_member": row.prior_association_family_member,
                    "primary_axis_specific_marker": row.primary_axis_specific_marker,
                }
            )
    return pd.DataFrame(rows)


def composite_metrics(merged: pd.DataFrame, traits: list[str]) -> pd.DataFrame:
    pc_values = merged[PCS].to_numpy(float)
    rows: list[dict[str, object]] = []
    for name, constituents in EDITORIAL_COMPOSITES:
        scores = merged[constituents].mean(axis=1).to_numpy(float)
        correlations = np.array([np.corrcoef(scores, pc_values[:, i])[0, 1] for i in range(6)])
        abs_r = np.abs(correlations)
        best = int(np.argmax(abs_r))
        off = sorted([i for i in range(6) if i != best], key=lambda i: (-abs_r[i], i))[0]
        communality = float(np.square(correlations).sum())
        row: dict[str, object] = {
            "composite_name": name,
            "constituent_traits": ";".join(constituents),
            "construction": "unweighted mean of three canonical raw activation-cosine trait scores",
        }
        row.update({f"r_pc{i + 1}": correlations[i] for i in range(6)})
        row.update(
            {
                "best_pc": PCS[best],
                "best_signed_r": correlations[best],
                "best_abs_r": abs_r[best],
                "axis_purity": correlations[best] ** 2 / communality,
                "six_pc_communality": communality,
                "max_off_axis_abs_r": abs_r[off],
                "second_best_pc": PCS[off],
                "dominance_gap": abs_r[best] - abs_r[off],
                "documented_config_source": "research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py",
                "affects_individual_marker_selection": False,
            }
        )
        rows.append(row)
    if not set(sum((members for _, members in EDITORIAL_COMPOSITES), [])) <= set(traits):
        raise ValueError("Documented composite constituent missing from Qwen trait matrix")
    return pd.DataFrame(rows)


def plot_strength_purity(metrics: pd.DataFrame, output: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.2), sharex=True, sharey=True)
    for axis, pc in zip(axes.flat, PCS, strict=True):
        frame = metrics[metrics["pc"] == pc]
        ordinary = frame[~frame["prior_association_family_member"]]
        family = frame[frame["prior_association_family_member"] & ~frame["primary_axis_specific_marker"]]
        markers = frame[frame["primary_axis_specific_marker"]]
        axis.scatter(ordinary["target_abs_r"], ordinary["axis_purity"], s=9, c="#aeb8c4", alpha=0.35)
        axis.scatter(family["target_abs_r"], family["axis_purity"], s=18, c="#d18b5b", alpha=0.75, label="strong cross/diffuse")
        axis.scatter(markers["target_abs_r"], markers["axis_purity"], s=27, c="#087e8b", alpha=0.95, label="primary marker")
        top = frame.sort_values(["target_abs_r", "trait"], ascending=[False, True]).head(3)
        labels = pd.concat([markers, top]).drop_duplicates("trait")
        for row in labels.itertuples(index=False):
            axis.annotate(row.trait, (row.target_abs_r, row.axis_purity), fontsize=6, xytext=(2, 2), textcoords="offset points")
        axis.axvline(0.50, color="#555555", linewidth=0.7, linestyle="--")
        axis.axhline(0.70, color="#555555", linewidth=0.7, linestyle="--")
        axis.set_title(pc + (" — strict core" if pc in {"PC1", "PC2", "PC3"} else " — secondary"))
        axis.grid(alpha=0.15)
    axes[1, 0].set_xlabel("|target Pearson r|")
    axes[1, 1].set_xlabel("|target Pearson r|")
    axes[1, 2].set_xlabel("|target Pearson r|")
    axes[0, 0].set_ylabel("axis purity")
    axes[1, 0].set_ylabel("axis purity")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, frameon=False)
    fig.suptitle("Qwen trait association strength versus PC1-PC6 axis purity", fontsize=13)
    fig.text(0.5, 0.01, "Saved correlations; markers use frozen .70 purity / .95 bootstrap-dominance rule", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    fig.savefig(output / "qwen_axis_specificity_strength_purity.png", dpi=180)
    fig.savefig(output / "qwen_axis_specificity_strength_purity.svg")
    plt.close(fig)


def main(repo: Path, output: Path) -> None:
    prior_dir = repo / "research/outputs/qwen_trait_family_human_inventory"
    for name, expected in PRIOR_HASHES.items():
        actual = sha256(prior_dir / name)
        if actual != expected:
            raise ValueError(f"Prior hash mismatch for {name}: {actual} != {expected}")
    corr = pd.read_csv(prior_dir / "qwen_trait_pc_correlations_all.csv")
    prior_members = pd.read_csv(prior_dir / "qwen_trait_family_membership_primary.csv")
    metrics, best, pivot = build_metrics(corr)

    prior_module = load_prior_module(repo)
    merged, traits, _, coordinate_error, role_source_paths = prior_module.load_inputs(repo)
    if list(pivot.index) != sorted(traits):
        pivot = pivot.reindex(traits)
    x = merged[traits].to_numpy(float)
    y = merged[PCS].to_numpy(float)
    recomputed = np.corrcoef(x, y, rowvar=False)[: len(traits), len(traits) :]
    saved = pivot.reindex(traits).to_numpy(float)
    correlation_verification_max_abs_error = float(np.max(np.abs(recomputed - saved)))
    pc_corr = np.corrcoef(y, rowvar=False)
    pc_max_off_diagonal = float(np.max(np.abs(pc_corr - np.eye(6))))

    xz = (x - x.mean(axis=0)) / x.std(axis=0, ddof=0)
    yz = (y - y.mean(axis=0)) / y.std(axis=0, ddof=0)
    coefficients, _, _, _ = np.linalg.lstsq(yz, xz, rcond=None)
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        fitted = yz @ coefficients
    if not np.isfinite(fitted).all():
        raise ValueError("Nonfinite fitted value in communality/multiple-R2 verification")
    r2 = 1.0 - np.square(xz - fitted).sum(axis=0) / np.square(xz).sum(axis=0)
    communality = np.square(saved).sum(axis=1)
    communality_r2_max_abs_error = float(np.max(np.abs(communality - r2)))
    if pc_max_off_diagonal > 1e-10 or communality_r2_max_abs_error > 1e-10:
        raise ValueError(
            f"Orthogonality/communality verification failed: pc={pc_max_off_diagonal}, r2={communality_r2_max_abs_error}"
        )

    wins, purity_draws, gap_draws = bootstrap_specificity(x, y)
    bootstrap = summarize_bootstrap(traits, wins, purity_draws, gap_draws, corr)
    combined, markers, sensitivity, classification = mark_membership(metrics, bootstrap, prior_members)
    comparisons = family_comparison(combined, markers, sensitivity, classification)
    pareto = pareto_front(combined)
    composites = composite_metrics(merged, traits)

    output.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output / "qwen_trait_axis_specificity_metrics.csv", index=False)
    best.to_csv(output / "qwen_trait_best_axis_summary.csv", index=False)
    bootstrap.to_csv(output / "qwen_trait_axis_specificity_bootstrap.csv", index=False)
    markers.to_csv(output / "qwen_axis_specific_marker_sets.csv", index=False)
    sensitivity.to_csv(output / "qwen_axis_specificity_threshold_sensitivity.csv", index=False)
    classification.to_csv(output / "qwen_trait_family_specificity_classification.csv", index=False)
    comparisons.to_csv(output / "qwen_axis_specific_family_comparison.csv", index=False)
    pareto.to_csv(output / "qwen_axis_specificity_pareto_front.csv", index=False)
    composites.to_csv(output / "existing_trait_composite_axis_specificity.csv", index=False)
    plot_strength_purity(combined, output)

    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    source_hashes = {
        str((prior_dir / name).relative_to(repo)): sha256(prior_dir / name) for name in PRIOR_HASHES
    }
    for path in role_source_paths:
        source_hashes[str(path.relative_to(repo))] = sha256(path)
    composite_config = repo / "research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py"
    source_hashes[str(composite_config.relative_to(repo))] = sha256(composite_config)
    manifest = {
        "analysis": "Axis-specific Qwen trait markers and purity-filtered SAPA inventory",
        "source_commit": SOURCE_COMMIT,
        "selection_spec_frozen_commit": "1fe7fae",
        "generated_at_utc": generated,
        "model": "Qwen/Qwen3-32B",
        "role_count": 275,
        "trait_count": 240,
        "pc_count": 6,
        "supported_subspace": {
            "strict_core": ["PC1", "PC2", "PC3"],
            "supported_secondary_provisional": ["PC4", "PC5", "PC6"],
        },
        "saved_correlations_reused_not_recomputed_as_analysis": True,
        "bootstrap": {
            "resamples": BOOTSTRAP_RESAMPLES,
            "seed": BOOTSTRAP_SEED,
            "sampling_unit": "Qwen role",
            "same_indices_across_all_traits_and_pcs_per_resample": True,
        },
        "primary_axis_specific_rule": {
            "prior_family_member": True,
            "target_strict_largest_abs_correlation": True,
            "bootstrap_dominance_probability_at_least": PRIMARY_DOMINANCE_PROBABILITY,
            "axis_purity_at_least": PRIMARY_PURITY,
        },
        "sensitivity": {
            "purity_thresholds": list(PURITY_SENSITIVITY),
            "bootstrap_dominance_probability_thresholds": list(DOMINANCE_SENSITIVITY),
        },
        "verification_metrics": {
            "canonical_pc1_pc3_coordinate_max_abs_error": coordinate_error,
            "saved_vs_role_level_recomputed_correlation_max_abs_error": correlation_verification_max_abs_error,
            "pc1_pc6_correlation_matrix": pc_corr.tolist(),
            "pc_max_abs_off_diagonal_correlation": pc_max_off_diagonal,
            "communality_vs_multiple_r2_max_abs_error": communality_r2_max_abs_error,
        },
        "documented_composites": {
            "source": str(composite_config.relative_to(repo)),
            "construction": "unweighted mean of each documented three-trait editorial group",
            "names": [name for name, _ in EDITORIAL_COMPOSITES],
            "affects_individual_marker_selection": False,
        },
        "firewall": {
            "other_models_loaded": [],
            "AA7_scientific_results_loaded": [],
            "human_respondent_rows_loaded": False,
            "human_respondent_scores_computed": False,
            "human_model_correspondence_tested": False,
            "next_experiment_selected": False,
        },
        "compute": "CPU only; no GPU, RunPod, model inference, activation extraction, response generation, or external model API.",
        "source_hashes": dict(sorted(source_hashes.items())),
    }
    (output / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "markers": len(markers),
                "families": comparisons[
                    ["pc", "pole", "original_association_family_size", "axis_specific_marker_count"]
                ].to_dict(orient="records"),
                "pc_max_off_diagonal": pc_max_off_diagonal,
                "communality_r2_max_error": communality_r2_max_abs_error,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    main(args.repo_root.resolve(), args.output_dir.resolve())
