#!/usr/bin/env python3
"""Human-only psychometric audit of the provisional SAPA trait bridge.

This script deliberately reads only SAPA item/scoring metadata, the frozen
semantic bridge, and q_* response columns from the SAPA release. It does not
load persona, model-coordinate, activation, occupation, or predictor artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_score


SEED = 20260911
PARALLEL_DRAWS = 500
GENERATED_AT = "2026-09-11T23:10:00Z"
RUBRIC_FREEZE_COMMIT = "6bf36c0"

# Explicit trait-item reversals frozen from exact wording and the prior
# coordinate-blind review direction notes. All unlisted retained trait-item
# pairs use the released 1-6 direction unchanged.
REVERSE_BY_TRAIT = {
    "adaptable": {"q_566"},
    "artistic": {"q_610"},
    "assertive": {"q_2161"},
    "callous": {"q_4231"},
    "cautious": {"q_1781", "q_292"},
    "competitive": {"q_1910"},
    "cruel": {"q_4231"},
    "curious": {"q_2775"},
    "cynical": {"q_343"},
    "dominant": {"q_2161"},
    "emotional": {"q_1681"},
    "forgiving": {"q_915"},
    "goofy": {"q_1685"},
    "independent": {"q_463"},
    "intuitive": {"q_1676"},
    "manipulative": {"q_905"},
    "melancholic": {"q_1578"},
    "naive": {"q_1758"},
    "neurotic": {"q_1578"},
    "playful": {"q_1685"},
    "rebellious": {"q_1624"},
    "reserved": {"q_1742"},
    "secular": {"q_345"},
    "spiritual": {"q_660"},
    "submissive": {"q_1768"},
}

BIG_FIVE_KEYS = {
    "openness": ("IPIP100intel", 1.0),
    "conscientiousness": ("IPIP100consc", 1.0),
    "extraversion": ("IPIP100extra", 1.0),
    "agreeableness": ("IPIP100agree", 1.0),
    "neuroticism": ("IPIP100stability", -1.0),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_ids(value: object) -> list[str]:
    if pd.isna(value) or not str(value):
        return []
    return [part for part in str(value).split(";") if part]


def harmonic_mean(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values) & (values > 0)]
    if not len(values):
        return float("nan")
    return float(len(values) / np.sum(1.0 / values))


def fisher_se(r_value: float, n_value: float) -> float:
    if not np.isfinite(r_value) or not np.isfinite(n_value) or n_value <= 3:
        return float("nan")
    return float((1.0 - r_value**2) / math.sqrt(n_value - 3.0))


def standard_alpha(correlation: np.ndarray) -> float:
    k = correlation.shape[0]
    if k < 2:
        return float("nan")
    off = correlation[np.triu_indices(k, 1)]
    mean_r = float(np.nanmean(off))
    denominator = 1.0 + (k - 1.0) * mean_r
    return float(k * mean_r / denominator) if abs(denominator) > 1e-12 else float("nan")


def nearest_psd_correlation(matrix: np.ndarray) -> tuple[np.ndarray, float, float]:
    symmetric = (matrix + matrix.T) / 2.0
    raw_eigenvalues, raw_eigenvectors = np.linalg.eigh(symmetric)
    clipped = np.maximum(raw_eigenvalues, 1e-8)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        projected = (raw_eigenvectors * clipped) @ raw_eigenvectors.T
    if not np.isfinite(projected).all():
        raise FloatingPointError("Nonfinite nearest-PSD projection")
    scale = np.sqrt(np.maximum(np.diag(projected), 1e-12))
    projected = projected / np.outer(scale, scale)
    projected = np.clip((projected + projected.T) / 2.0, -1.0, 1.0)
    np.fill_diagonal(projected, 1.0)
    return projected, float(raw_eigenvalues.min()), float(np.max(np.abs(projected - symmetric)))


def effective_ranks(eigenvalues: np.ndarray) -> tuple[float, float]:
    values = np.maximum(np.asarray(eigenvalues, dtype=float), 0.0)
    if values.sum() <= 0:
        return float("nan"), float("nan")
    participation = float(values.sum() ** 2 / np.square(values).sum())
    probabilities = values / values.sum()
    probabilities = probabilities[probabilities > 0]
    entropy = float(np.exp(-np.sum(probabilities * np.log(probabilities))))
    return participation, entropy


def composite_correlation(
    correlation: pd.DataFrame,
    items_a: list[str],
    signs_a: dict[str, float],
    items_b: list[str],
    signs_b: dict[str, float],
    cross_n: pd.DataFrame | None = None,
    remove_shared: bool = False,
) -> tuple[float, float, int, int]:
    use_a = list(items_a)
    use_b = list(items_b)
    if remove_shared:
        shared = set(use_a) & set(use_b)
        use_a = [item for item in use_a if item not in shared]
        use_b = [item for item in use_b if item not in shared]
    if not use_a or not use_b:
        return float("nan"), float("nan"), len(use_a), len(use_b)
    sa = np.array([signs_a[item] for item in use_a], dtype=float)
    sb = np.array([signs_b[item] for item in use_b], dtype=float)
    r_aa = correlation.loc[use_a, use_a].to_numpy(dtype=float)
    r_bb = correlation.loc[use_b, use_b].to_numpy(dtype=float)
    r_ab = correlation.loc[use_a, use_b].to_numpy(dtype=float)
    # NumPy 2.2 linked to macOS Accelerate can emit spurious floating-point
    # matmul warnings even when every result is finite. Suppress only those
    # hardware-library warnings here and validate finiteness downstream.
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        numerator = float(sa @ r_ab @ sb)
        variance_a = float(sa @ r_aa @ sa)
        variance_b = float(sb @ r_bb @ sb)
    denominator = math.sqrt(max(variance_a * variance_b, 0.0))
    estimate = numerator / denominator if denominator > 1e-12 else float("nan")
    estimate = float(np.clip(estimate, -1.0, 1.0)) if np.isfinite(estimate) else estimate
    n_eff = float("nan")
    if cross_n is not None:
        n_eff = harmonic_mean(cross_n.loc[use_a, use_b].to_numpy(dtype=float).ravel())
    return estimate, n_eff, len(use_a), len(use_b)


def save_matrix(path: Path, labels: list[str], matrix: np.ndarray, digits: int = 8) -> None:
    frame = pd.DataFrame(matrix, index=labels, columns=labels)
    frame.index.name = "trait"
    frame.round(digits).to_csv(path, lineterminator="\n")


def build_source_scale_map(scale_inventory: pd.DataFrame, super_key: pd.DataFrame) -> dict[str, dict[str, object]]:
    source = scale_inventory[scale_inventory["inventory_type"] == "administered_source_construct"]
    key_sets = {
        key: set(super_key.index[super_key[key].fillna(0).astype(float) != 0])
        for key in super_key.columns
    }
    mapping: dict[str, dict[str, object]] = {}
    for row in source.itertuples(index=False):
        source_items = set(split_ids(row.item_ids))
        exact = [key for key, key_items in key_sets.items() if key_items == source_items]
        if exact:
            mapping[row.scale_id] = {
                "scoring_key": exact[0],
                "mapping_quality": "exact_item_set",
                "source_item_count": len(source_items),
                "key_item_count": len(key_sets[exact[0]]),
            }
        elif row.scale_id == "IPIP100:B5:E":
            key = "IPIP100extra"
            overlap = len(source_items & key_sets[key])
            mapping[row.scale_id] = {
                "scoring_key": key,
                "mapping_quality": f"official_named_key_{overlap}_of_{len(source_items)}_source_items",
                "source_item_count": len(source_items),
                "key_item_count": len(key_sets[key]),
            }
        else:
            raise ValueError(f"No official scoring-key map for {row.scale_id}")
    return mapping


def proxy_matrices(
    traits: list[str],
    proxy_items: dict[str, list[str]],
    proxy_signs: dict[str, dict[str, float]],
    correlation: pd.DataFrame,
    cross_n: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    p = len(traits)
    result = np.eye(p, dtype=float)
    effective_n = np.zeros((p, p), dtype=float)
    for left_index, left in enumerate(traits):
        _, diagonal_n, _, _ = composite_correlation(
            correlation,
            proxy_items[left],
            proxy_signs[left],
            proxy_items[left],
            proxy_signs[left],
            cross_n,
        )
        effective_n[left_index, left_index] = diagonal_n
        for right_index in range(left_index + 1, p):
            right = traits[right_index]
            estimate, n_eff, _, _ = composite_correlation(
                correlation,
                proxy_items[left],
                proxy_signs[left],
                proxy_items[right],
                proxy_signs[right],
                cross_n,
            )
            result[left_index, right_index] = result[right_index, left_index] = estimate
            effective_n[left_index, right_index] = effective_n[right_index, left_index] = n_eff
    return result, effective_n


def dimensionality_analysis(
    tier_name: str,
    traits: list[str],
    correlation: np.ndarray,
    effective_n: np.ndarray,
    rng: np.random.Generator,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object], np.ndarray]:
    psd, raw_minimum, max_adjustment = nearest_psd_correlation(correlation)
    raw_eigenvalues = np.linalg.eigvalsh((correlation + correlation.T) / 2.0)[::-1]
    eigenvalues = np.linalg.eigvalsh(psd)[::-1]
    participation, entropy = effective_ranks(eigenvalues)
    off_diagonal_n = effective_n[np.triu_indices(len(traits), 1)]
    median_n = int(round(float(np.nanmedian(off_diagonal_n))))
    null_eigenvalues = np.empty((PARALLEL_DRAWS, len(traits)), dtype=float)
    for draw in range(PARALLEL_DRAWS):
        sample = rng.standard_normal((median_n, len(traits)))
        null_eigenvalues[draw] = np.linalg.eigvalsh(np.corrcoef(sample, rowvar=False))[::-1]
    parallel_p95 = np.quantile(null_eigenvalues, 0.95, axis=0)
    parallel_count = int(np.sum(eigenvalues > parallel_p95))
    cumulative = np.cumsum(eigenvalues) / eigenvalues.sum()
    spectrum_rows = [
        {
            "analysis_tier": tier_name,
            "component": index + 1,
            "raw_eigenvalue": round(float(raw_eigenvalues[index]), 8),
            "psd_eigenvalue": round(float(eigenvalues[index]), 8),
            "variance_fraction": round(float(eigenvalues[index] / eigenvalues.sum()), 8),
            "cumulative_variance_fraction": round(float(cumulative[index]), 8),
            "parallel_analysis_p95": round(float(parallel_p95[index]), 8),
            "exceeds_parallel_p95": bool(eigenvalues[index] > parallel_p95[index]),
        }
        for index in range(len(traits))
    ]

    distance = np.sqrt(np.maximum(0.0, (1.0 - psd) / 2.0))
    np.fill_diagonal(distance, 0.0)
    hierarchy = linkage(squareform(distance, checks=False), method="average")
    best_score = -np.inf
    best_k = 2
    best_labels = None
    for k in range(2, min(12, len(traits) - 1) + 1):
        labels = fcluster(hierarchy, k, criterion="maxclust")
        if len(np.unique(labels)) < 2:
            continue
        score = float(silhouette_score(distance, labels, metric="precomputed"))
        if score > best_score + 1e-12:
            best_score, best_k, best_labels = score, k, labels
    assert best_labels is not None
    cluster_counts = Counter(int(value) for value in best_labels)
    cluster_rows = [
        {
            "analysis_tier": tier_name,
            "trait": trait,
            "cluster_id": int(label),
            "cluster_size": int(cluster_counts[int(label)]),
            "selected_cluster_count": int(best_k),
            "silhouette": round(best_score, 8),
        }
        for trait, label in zip(traits, best_labels)
    ]
    summary = {
        "trait_count": len(traits),
        "raw_minimum_eigenvalue": round(raw_minimum, 8),
        "psd_max_absolute_adjustment": round(max_adjustment, 8),
        "participation_ratio_effective_rank": round(participation, 6),
        "entropy_effective_rank": round(entropy, 6),
        "eigenvalues_above_one": int(np.sum(eigenvalues > 1.0)),
        "parallel_analysis_components": parallel_count,
        "parallel_analysis_draws": PARALLEL_DRAWS,
        "parallel_analysis_reference_n": median_n,
        "components_for_50pct_variance": int(np.searchsorted(cumulative, 0.5) + 1),
        "components_for_80pct_variance": int(np.searchsorted(cumulative, 0.8) + 1),
        "components_for_90pct_variance": int(np.searchsorted(cumulative, 0.9) + 1),
        "selected_cluster_count": int(best_k),
        "selected_cluster_silhouette": round(best_score, 8),
    }
    return spectrum_rows, cluster_rows, summary, psd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = (args.output_dir or Path(__file__).resolve().parent).resolve()
    output.mkdir(parents=True, exist_ok=True)

    feasibility = repo / "research/outputs/human_trait_dataset_feasibility"
    bridge_path = feasibility / "sapa_review/sapa_trait_bridge_provisional_v1.csv"
    review_path = feasibility / "sapa_review/sapa_category3_second_pass_review.csv"
    item_path = feasibility / "sapa/sapa_item_dictionary.csv"
    scale_path = feasibility / "sapa/sapa_scale_inventory.csv"
    sapa_manifest_path = feasibility / "sapa/sapa_source_manifest.json"
    review_manifest_path = feasibility / "sapa_review/sapa_review_source_manifest.json"
    rubric_path = output / "psychometric_support_rubric.md"
    raw_root = repo / "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE"
    raw_path = raw_root / "sapaTempData696items08dec2013thru26jul2014.tab"
    key_path = raw_root / "superKey696.csv"

    allowed_inputs = [
        bridge_path,
        review_path,
        item_path,
        scale_path,
        sapa_manifest_path,
        review_manifest_path,
        rubric_path,
        raw_path,
        key_path,
    ]
    for source in allowed_inputs:
        if not source.exists():
            raise FileNotFoundError(source)

    bridge = pd.read_csv(bridge_path).fillna("")
    review = pd.read_csv(review_path).fillna("")
    items = pd.read_csv(item_path).fillna("")
    scales = pd.read_csv(scale_path).fillna("")
    super_key = pd.read_csv(key_path, index_col=0).fillna(0)
    super_key.index = super_key.index.astype(str)
    super_key = super_key.apply(pd.to_numeric, errors="raise")

    assert Counter(bridge["review_decision"]) == {"ACCEPT_DIRECT": 45, "ACCEPT_CLOSE": 29}
    assert len(bridge) == 74 and bridge["trait"].is_unique
    assert len(set().union(*(set(split_ids(value)) for value in bridge["sapa_item_ids"]))) == 129
    assert set(REVERSE_BY_TRAIT) == set(bridge.loc[bridge["scoring_direction"] == "handled", "trait"])
    item_lookup = items.set_index("item_id")
    assert set(super_key.index) == set(items["item_id"])
    source_scale_map = build_source_scale_map(scales, super_key)
    intended_source_scales = sorted(set().union(*(set(split_ids(value)) for value in bridge["source_scales"])))
    assert len(intended_source_scales) == 78
    assert set(intended_source_scales) <= set(source_scale_map)

    proxy_items: dict[str, list[str]] = {}
    proxy_signs: dict[str, dict[str, float]] = {}
    scoring_rows: list[dict[str, object]] = []
    review_lookup = review.set_index("trait")
    for row in bridge.itertuples(index=False):
        trait_items = split_ids(row.sapa_item_ids)
        reversed_items = REVERSE_BY_TRAIT.get(row.trait, set())
        assert reversed_items <= set(trait_items)
        proxy_items[row.trait] = trait_items
        proxy_signs[row.trait] = {item: (-1.0 if item in reversed_items else 1.0) for item in trait_items}
        for item in trait_items:
            metadata = item_lookup.loc[item]
            sign = proxy_signs[row.trait][item]
            scoring_rows.append(
                {
                    "trait": row.trait,
                    "review_decision": row.review_decision,
                    "bridge_tier": row.bridge_tier,
                    "item_id": item,
                    "item_text": metadata["item_text"],
                    "original_item_polarity_relative_to_trait": "positive_indicator" if sign == 1 else "negative_indicator",
                    "orientation_sign": int(sign),
                    "transformation": "identity" if sign == 1 else "7-response",
                    "final_orientation": f"higher={row.trait}",
                    "released_response_scale": "1-6",
                    "official_derived_scoring_keys": metadata["derived_scoring_keys"],
                    "official_reverse_keyed_in_scales": metadata["reverse_keyed_in_derived_scales"],
                    "source_scale_memberships": metadata["source_scale_memberships"],
                    "second_pass_direction_note": review_lookup.loc[row.trait, "reverse_direction_issue"],
                    "orientation_status": "explicit_resolved",
                }
            )
    scoring = pd.DataFrame(scoring_rows)
    direct_traits = bridge.loc[bridge["review_decision"] == "ACCEPT_DIRECT", "trait"].tolist()
    all_traits = bridge["trait"].tolist()

    # Read psychological items only. Respondent ID and demographic columns never enter memory.
    all_item_ids = list(super_key.index)
    responses = pd.read_csv(raw_path, sep="\t", usecols=all_item_ids, na_values=["NA"])
    responses = responses.apply(pd.to_numeric, errors="coerce")
    assert responses.shape == (23679, 696)
    assert float(responses.min(skipna=True).min(skipna=True)) >= 1.0
    assert float(responses.max(skipna=True).max(skipna=True)) <= 6.0
    item_administration_n = responses.notna().sum(axis=0)
    scoring["item_administration_n"] = scoring["item_id"].map(item_administration_n).astype(int)
    scoring["item_observed_fraction"] = (
        scoring["item_administration_n"] / len(responses)
    ).round(8)
    scoring.to_csv(output / "trait_proxy_item_scoring.csv", index=False, lineterminator="\n")

    pearson = responses.corr(method="pearson", min_periods=200)
    retained_items = sorted(set(scoring["item_id"]))
    spearman_retained = responses[retained_items].corr(method="spearman", min_periods=200)
    assert np.isfinite(pearson.to_numpy()).all()
    assert np.isfinite(spearman_retained.to_numpy()).all()
    retained_observed = responses[retained_items].notna().to_numpy(dtype=np.float32)
    all_observed = responses[all_item_ids].notna().to_numpy(dtype=np.float32)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        retained_by_all_n = retained_observed.T @ all_observed
    assert np.isfinite(retained_by_all_n).all()
    assert float(retained_by_all_n.min()) >= 0.0
    assert float(retained_by_all_n.max()) <= len(responses)
    assert np.equal(retained_by_all_n, np.rint(retained_by_all_n)).all()
    cross_n = pd.DataFrame(retained_by_all_n, index=retained_items, columns=all_item_ids)
    retained_n = cross_n.loc[retained_items, retained_items]

    missingness_summary: dict[str, object] = {
        "respondents": len(responses),
        "design_interpretation": "SAPA randomized planned item administration; missingness is not treated as ordinary nonresponse.",
        "complete_case_analysis_used": False,
        "mean_imputation_used": False,
        "tiers": {},
    }
    for tier_name, tier_traits in [
        ("accept_direct", direct_traits),
        ("accept_direct_plus_close", all_traits),
    ]:
        tier_items = sorted(set().union(*(set(proxy_items[trait]) for trait in tier_traits)))
        per_respondent_items = responses[tier_items].notna().sum(axis=1)
        complete_proxy_count = np.zeros(len(responses), dtype=np.int16)
        partial_proxy_count = np.zeros(len(responses), dtype=np.int16)
        for trait in tier_traits:
            observed = responses[proxy_items[trait]].notna()
            complete_proxy_count += observed.all(axis=1).to_numpy(dtype=np.int16)
            partial_proxy_count += observed.any(axis=1).to_numpy(dtype=np.int16)
        tier_overlap = retained_n.loc[tier_items, tier_items].to_numpy(dtype=float)
        off_diagonal_overlap = tier_overlap[np.triu_indices(len(tier_items), 1)]
        missingness_summary["tiers"][tier_name] = {
            "trait_count": len(tier_traits),
            "distinct_item_count": len(tier_items),
            "item_administration_n_min": int(item_administration_n.loc[tier_items].min()),
            "item_administration_n_median": float(item_administration_n.loc[tier_items].median()),
            "item_administration_n_max": int(item_administration_n.loc[tier_items].max()),
            "retained_items_observed_per_respondent_p25": float(per_respondent_items.quantile(0.25)),
            "retained_items_observed_per_respondent_median": float(per_respondent_items.median()),
            "retained_items_observed_per_respondent_p75": float(per_respondent_items.quantile(0.75)),
            "retained_items_observed_per_respondent_max": int(per_respondent_items.max()),
            "respondents_observing_all_retained_items": int((per_respondent_items == len(tier_items)).sum()),
            "fully_observed_proxies_per_respondent_p25": float(np.quantile(complete_proxy_count, 0.25)),
            "fully_observed_proxies_per_respondent_median": float(np.median(complete_proxy_count)),
            "fully_observed_proxies_per_respondent_p75": float(np.quantile(complete_proxy_count, 0.75)),
            "fully_observed_proxies_per_respondent_max": int(complete_proxy_count.max()),
            "partially_observed_proxies_per_respondent_median": float(np.median(partial_proxy_count)),
            "item_pair_overlap_n_min": int(np.nanmin(off_diagonal_overlap)),
            "item_pair_overlap_n_median": float(np.nanmedian(off_diagonal_overlap)),
            "item_pair_overlap_n_max": int(np.nanmax(off_diagonal_overlap)),
        }
    (output / "sapa_bridge_planned_missingness_summary.json").write_text(
        json.dumps(missingness_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    item_pair_rows: list[dict[str, object]] = []
    for item_a, item_b in combinations(retained_items, 2):
        n_value = int(retained_n.loc[item_a, item_b])
        pearson_r = float(pearson.loc[item_a, item_b])
        spearman_r = float(spearman_retained.loc[item_a, item_b])
        item_pair_rows.append(
            {
                "item_a": item_a,
                "item_b": item_b,
                "pairwise_n": n_value,
                "pearson_r_raw_direction": round(pearson_r, 8),
                "pearson_se_fisher_approx": round(fisher_se(pearson_r, n_value), 8),
                "spearman_r_raw_direction": round(spearman_r, 8),
                "spearman_se_fisher_approx": round(fisher_se(spearman_r, n_value), 8),
            }
        )
    pd.DataFrame(item_pair_rows).to_csv(
        output / "retained_item_pair_correlations.csv", index=False, lineterminator="\n"
    )

    coherence_rows: list[dict[str, object]] = []
    coherence_pair_rows: list[dict[str, object]] = []
    for row in bridge.itertuples(index=False):
        trait_items = proxy_items[row.trait]
        signs = proxy_signs[row.trait]
        if len(trait_items) == 1:
            coherence_rows.append(
                {
                    "trait": row.trait,
                    "review_decision": row.review_decision,
                    "bridge_tier": row.bridge_tier,
                    "supporting_item_count": 1,
                    "item_pair_count": 0,
                    "pairwise_n_min": "",
                    "pairwise_n_median": "",
                    "pairwise_n_max": "",
                    "pearson_mean_interitem_r": "",
                    "pearson_median_interitem_r": "",
                    "pearson_min_interitem_r": "",
                    "pearson_max_interitem_r": "",
                    "pearson_standardized_alpha": "",
                    "spearman_mean_interitem_r": "",
                    "spearman_standardized_alpha": "",
                    "negative_pair_count": 0,
                    "coherence_status": "single_item_only",
                    "reliability_status": "not_estimable_internally",
                    "omega_status": "not_estimated_two_or_three_item_proxy_underidentified_or_saturated",
                }
            )
            continue
        pearson_values, spearman_values, n_values = [], [], []
        for item_a, item_b in combinations(trait_items, 2):
            sign_product = signs[item_a] * signs[item_b]
            pearson_r = float(pearson.loc[item_a, item_b] * sign_product)
            spearman_r = float(spearman_retained.loc[item_a, item_b] * sign_product)
            n_value = int(retained_n.loc[item_a, item_b])
            pearson_values.append(pearson_r)
            spearman_values.append(spearman_r)
            n_values.append(n_value)
            coherence_pair_rows.append(
                {
                    "trait": row.trait,
                    "review_decision": row.review_decision,
                    "item_a": item_a,
                    "item_b": item_b,
                    "orientation_sign_a": int(signs[item_a]),
                    "orientation_sign_b": int(signs[item_b]),
                    "pairwise_n": n_value,
                    "oriented_pearson_r": round(pearson_r, 8),
                    "pearson_se_fisher_approx": round(fisher_se(pearson_r, n_value), 8),
                    "oriented_spearman_r": round(spearman_r, 8),
                    "spearman_se_fisher_approx": round(fisher_se(spearman_r, n_value), 8),
                }
            )
        pearson_array = np.asarray(pearson_values)
        spearman_array = np.asarray(spearman_values)
        mean_r = float(pearson_array.mean())
        median_r = float(np.median(pearson_array))
        minimum_r = float(pearson_array.min())
        if mean_r < 0 or median_r < 0:
            coherence_status = "contradictory"
        elif mean_r >= 0.30 and minimum_r >= -0.10:
            coherence_status = "strong"
        elif mean_r >= 0.15 and minimum_r >= -0.10:
            coherence_status = "moderate"
        else:
            coherence_status = "weak"
        oriented_pearson = pearson.loc[trait_items, trait_items].to_numpy() * np.outer(
            [signs[item] for item in trait_items], [signs[item] for item in trait_items]
        )
        oriented_spearman = spearman_retained.loc[trait_items, trait_items].to_numpy() * np.outer(
            [signs[item] for item in trait_items], [signs[item] for item in trait_items]
        )
        coherence_rows.append(
            {
                "trait": row.trait,
                "review_decision": row.review_decision,
                "bridge_tier": row.bridge_tier,
                "supporting_item_count": len(trait_items),
                "item_pair_count": len(pearson_values),
                "pairwise_n_min": min(n_values),
                "pairwise_n_median": round(float(np.median(n_values)), 2),
                "pairwise_n_max": max(n_values),
                "pearson_mean_interitem_r": round(mean_r, 8),
                "pearson_median_interitem_r": round(median_r, 8),
                "pearson_min_interitem_r": round(minimum_r, 8),
                "pearson_max_interitem_r": round(float(pearson_array.max()), 8),
                "pearson_standardized_alpha": round(standard_alpha(oriented_pearson), 8),
                "spearman_mean_interitem_r": round(float(spearman_array.mean()), 8),
                "spearman_standardized_alpha": round(standard_alpha(oriented_spearman), 8),
                "negative_pair_count": int(np.sum(pearson_array < 0)),
                "coherence_status": coherence_status,
                "reliability_status": "pairwise_standardized_alpha_descriptive",
                "omega_status": "not_estimated_two_or_three_item_proxy_underidentified_or_saturated",
            }
        )
    coherence = pd.DataFrame(coherence_rows)
    coherence.to_csv(output / "trait_proxy_internal_coherence.csv", index=False, lineterminator="\n")
    pd.DataFrame(coherence_pair_rows).to_csv(
        output / "trait_proxy_internal_item_pairs.csv", index=False, lineterminator="\n"
    )

    # Human-only trait-proxy matrices: direct first, then direct+close sensitivity.
    matrix_results: dict[str, dict[str, object]] = {}
    for tier_name, tier_traits, pearson_name, spearman_name, n_name in [
        (
            "accept_direct",
            direct_traits,
            "human_trait_proxy_correlation_matrix.csv",
            "human_trait_proxy_spearman_correlation_matrix.csv",
            "human_trait_proxy_pairwise_n.csv",
        ),
        (
            "accept_direct_plus_close",
            all_traits,
            "human_trait_proxy_correlation_matrix_direct_plus_close.csv",
            "human_trait_proxy_spearman_correlation_matrix_direct_plus_close.csv",
            "human_trait_proxy_pairwise_n_direct_plus_close.csv",
        ),
    ]:
        pearson_matrix, n_matrix = proxy_matrices(tier_traits, proxy_items, proxy_signs, pearson, cross_n)
        spearman_matrix, _ = proxy_matrices(
            tier_traits, proxy_items, proxy_signs, spearman_retained, retained_n
        )
        save_matrix(output / pearson_name, tier_traits, pearson_matrix)
        save_matrix(output / spearman_name, tier_traits, spearman_matrix)
        save_matrix(output / n_name, tier_traits, np.rint(n_matrix).astype(int), digits=0)
        matrix_results[tier_name] = {
            "traits": tier_traits,
            "pearson": pearson_matrix,
            "spearman": spearman_matrix,
            "n": n_matrix,
        }
    rank_sensitivity: dict[str, dict[str, object]] = {}
    for tier_name, tier in matrix_results.items():
        upper = np.triu_indices(len(tier["traits"]), 1)
        primary = tier["pearson"][upper]
        sensitivity = tier["spearman"][upper]
        difference = np.abs(primary - sensitivity)
        rank_sensitivity[tier_name] = {
            "proxy_pair_count": len(primary),
            "pearson_spearman_vector_correlation": round(
                float(np.corrcoef(primary, sensitivity)[0, 1]), 8
            ),
            "median_absolute_pearson_spearman_difference": round(float(np.median(difference)), 8),
            "maximum_absolute_pearson_spearman_difference": round(float(np.max(difference)), 8),
            "sign_disagreement_count": int(np.sum(np.sign(primary) != np.sign(sensitivity))),
        }

    # Map every official source construct to the release scoring key, then
    # evaluate each proxy against every one of the 131 keyed scales.
    scale_key_items = {
        key: list(super_key.index[super_key[key] != 0]) for key in super_key.columns
    }
    scale_key_signs = {
        key: {item: float(super_key.loc[item, key]) for item in scale_key_items[key]}
        for key in super_key.columns
    }
    scale_rows: list[dict[str, object]] = []
    convergence_rows: list[dict[str, object]] = []
    associations_by_trait: dict[str, dict[str, float]] = defaultdict(dict)
    association_n_by_trait: dict[str, dict[str, float]] = defaultdict(dict)
    for bridge_row in bridge.itertuples(index=False):
        intended_ids = split_ids(bridge_row.source_scales)
        intended_key_to_sources: dict[str, list[str]] = defaultdict(list)
        for source_id in intended_ids:
            intended_key_to_sources[str(source_scale_map[source_id]["scoring_key"])].append(source_id)
        trait_scale_rows = []
        for scale_key in super_key.columns:
            estimate, n_eff, _, used_scale_count = composite_correlation(
                pearson,
                proxy_items[bridge_row.trait],
                proxy_signs[bridge_row.trait],
                scale_key_items[scale_key],
                scale_key_signs[scale_key],
                cross_n,
                remove_shared=True,
            )
            associations_by_trait[bridge_row.trait][scale_key] = estimate
            association_n_by_trait[bridge_row.trait][scale_key] = n_eff
            row = {
                "trait": bridge_row.trait,
                "review_decision": bridge_row.review_decision,
                "scale_scoring_key": scale_key,
                "is_intended_source_scale": scale_key in intended_key_to_sources,
                "intended_source_scale_ids": ";".join(intended_key_to_sources.get(scale_key, [])),
                "pearson_r_part_whole_corrected": round(estimate, 8) if np.isfinite(estimate) else "",
                "absolute_pearson_r": round(abs(estimate), 8) if np.isfinite(estimate) else "",
                "pairwise_effective_n": round(n_eff, 2) if np.isfinite(n_eff) else "",
                "proxy_item_count": len(proxy_items[bridge_row.trait]),
                "scale_item_count_before_exclusion": len(scale_key_items[scale_key]),
                "scale_item_count_after_exclusion": used_scale_count,
                "excluded_proxy_items": ";".join(
                    sorted(set(proxy_items[bridge_row.trait]) & set(scale_key_items[scale_key]))
                ),
            }
            scale_rows.append(row)
            trait_scale_rows.append(row)
        valid_rows = [row for row in trait_scale_rows if row["absolute_pearson_r"] != ""]
        ranked = sorted(valid_rows, key=lambda row: (-float(row["absolute_pearson_r"]), row["scale_scoring_key"]))
        rank_lookup = {row["scale_scoring_key"]: rank + 1 for rank, row in enumerate(ranked)}
        intended_rows = [row for row in valid_rows if row["is_intended_source_scale"]]
        alternative_rows = [row for row in valid_rows if not row["is_intended_source_scale"]]
        best_intended = max(intended_rows, key=lambda row: float(row["absolute_pearson_r"])) if intended_rows else None
        best_alternative = max(alternative_rows, key=lambda row: float(row["absolute_pearson_r"])) if alternative_rows else None
        item_associations = []
        for item in proxy_items[bridge_row.trait]:
            for intended_key in sorted(intended_key_to_sources):
                estimate, n_eff, _, _ = composite_correlation(
                    pearson,
                    [item],
                    {item: proxy_signs[bridge_row.trait][item]},
                    scale_key_items[intended_key],
                    scale_key_signs[intended_key],
                    cross_n,
                    remove_shared=True,
                )
                item_associations.append(
                    {
                        "item_id": item,
                        "intended_key": intended_key,
                        "r": round(estimate, 6) if np.isfinite(estimate) else None,
                        "n_eff": round(n_eff, 1) if np.isfinite(n_eff) else None,
                    }
                )
        if best_intended:
            intended_abs = float(best_intended["absolute_pearson_r"])
            intended_rank = rank_lookup[best_intended["scale_scoring_key"]]
            if intended_abs >= 0.30 and intended_rank <= math.ceil(0.25 * len(ranked)):
                convergence_status = "strong"
            elif intended_abs >= 0.20 and intended_rank <= math.ceil(0.50 * len(ranked)):
                convergence_status = "moderate"
            else:
                convergence_status = "weak"
        else:
            intended_abs, intended_rank, convergence_status = float("nan"), None, "insufficient"
        alternative_abs = float(best_alternative["absolute_pearson_r"]) if best_alternative else float("nan")
        convergence_rows.append(
            {
                "trait": bridge_row.trait,
                "review_decision": bridge_row.review_decision,
                "bridge_tier": bridge_row.bridge_tier,
                "intended_source_scale_ids": ";".join(intended_ids),
                "intended_scoring_keys": ";".join(sorted(intended_key_to_sources)),
                "intended_key_mapping_quality": ";".join(
                    f"{source_id}:{source_scale_map[source_id]['mapping_quality']}" for source_id in intended_ids
                ),
                "best_intended_source_scale_ids": best_intended["intended_source_scale_ids"] if best_intended else "",
                "best_intended_scoring_key": best_intended["scale_scoring_key"] if best_intended else "",
                "best_intended_pearson_r": best_intended["pearson_r_part_whole_corrected"] if best_intended else "",
                "best_intended_absolute_r": best_intended["absolute_pearson_r"] if best_intended else "",
                "best_intended_pairwise_effective_n": best_intended["pairwise_effective_n"] if best_intended else "",
                "best_intended_rank_of_131": intended_rank or "",
                "best_intended_rank_fraction": round(intended_rank / len(ranked), 8) if intended_rank else "",
                "strongest_alternative_scoring_key": best_alternative["scale_scoring_key"] if best_alternative else "",
                "strongest_alternative_pearson_r": best_alternative["pearson_r_part_whole_corrected"] if best_alternative else "",
                "strongest_alternative_absolute_r": best_alternative["absolute_pearson_r"] if best_alternative else "",
                "absolute_margin_over_strongest_alternative": round(intended_abs - alternative_abs, 8)
                if np.isfinite(intended_abs) and np.isfinite(alternative_abs)
                else "",
                "intended_scale_association_status": convergence_status,
                "item_to_intended_scale_associations": json.dumps(item_associations, separators=(",", ":")),
                "part_whole_correction": "all proxy evidence items excluded from each evaluated scale",
            }
        )
    scale_associations = pd.DataFrame(scale_rows)
    scale_associations.to_csv(
        output / "trait_proxy_scale_associations_long.csv", index=False, lineterminator="\n"
    )
    convergence = pd.DataFrame(convergence_rows)
    convergence.to_csv(output / "trait_proxy_source_scale_convergence.csv", index=False, lineterminator="\n")

    # Reuse sensitivity among all retained proxies.
    combined_traits = matrix_results["accept_direct_plus_close"]["traits"]
    combined_corr = matrix_results["accept_direct_plus_close"]["pearson"]
    combined_index = {trait: index for index, trait in enumerate(combined_traits)}
    reuse_rows: list[dict[str, object]] = []
    trait_max_reuse_delta: dict[str, float] = defaultdict(float)
    trait_exact_alias: dict[str, bool] = defaultdict(bool)
    trait_high_scale_redundancy: dict[str, bool] = defaultdict(bool)
    for left, right in combinations(combined_traits, 2):
        shared_items = sorted(set(proxy_items[left]) & set(proxy_items[right]))
        left_scales = set(split_ids(bridge.loc[bridge["trait"] == left, "source_scales"].iloc[0]))
        right_scales = set(split_ids(bridge.loc[bridge["trait"] == right, "source_scales"].iloc[0]))
        shared_scales = sorted(left_scales & right_scales)
        if not shared_items and not shared_scales:
            continue
        full_r = float(combined_corr[combined_index[left], combined_index[right]])
        adjusted_r, adjusted_n, left_remaining, right_remaining = composite_correlation(
            pearson,
            proxy_items[left],
            proxy_signs[left],
            proxy_items[right],
            proxy_signs[right],
            cross_n,
            remove_shared=True,
        )
        delta = abs(full_r) - abs(adjusted_r) if np.isfinite(adjusted_r) else float("nan")
        same_item_set = set(proxy_items[left]) == set(proxy_items[right])
        if same_item_set:
            left_vector = np.array([proxy_signs[left][item] for item in sorted(proxy_items[left])])
            right_vector = np.array([proxy_signs[right][item] for item in sorted(proxy_items[right])])
            if np.array_equal(left_vector, right_vector):
                alias_type = "exact_same_oriented_item_set"
            elif np.array_equal(left_vector, -right_vector):
                alias_type = "exact_inverse_oriented_item_set"
            else:
                alias_type = "same_item_set_mixed_orientation"
            trait_exact_alias[left] = trait_exact_alias[right] = True
            reuse_status = "exact_alias"
        elif np.isfinite(delta) and delta >= 0.20:
            reuse_status = "shared_item_sensitive"
        elif shared_scales and abs(full_r) >= 0.70:
            reuse_status = "same_scale_high_redundancy"
            trait_high_scale_redundancy[left] = trait_high_scale_redundancy[right] = True
            alias_type = "none"
        elif shared_scales and abs(full_r) >= 0.35:
            reuse_status = "neighboring_construct"
            alias_type = "none"
        else:
            reuse_status = "differentiated_despite_shared_scale_or_item"
            alias_type = "none"
        if np.isfinite(delta):
            trait_max_reuse_delta[left] = max(trait_max_reuse_delta[left], delta)
            trait_max_reuse_delta[right] = max(trait_max_reuse_delta[right], delta)
        reuse_rows.append(
            {
                "trait_a": left,
                "decision_a": bridge.loc[bridge["trait"] == left, "review_decision"].iloc[0],
                "trait_b": right,
                "decision_b": bridge.loc[bridge["trait"] == right, "review_decision"].iloc[0],
                "shared_item_count": len(shared_items),
                "shared_items": ";".join(shared_items),
                "shared_source_scale_count": len(shared_scales),
                "shared_source_scales": ";".join(shared_scales),
                "full_proxy_pearson_r": round(full_r, 8),
                "shared_items_removed_pearson_r": round(adjusted_r, 8) if np.isfinite(adjusted_r) else "",
                "absolute_r_reduction_after_shared_item_removal": round(delta, 8) if np.isfinite(delta) else "",
                "shared_items_removed_pairwise_effective_n": round(adjusted_n, 2)
                if np.isfinite(adjusted_n)
                else "",
                "remaining_items_trait_a": left_remaining,
                "remaining_items_trait_b": right_remaining,
                "alias_type": alias_type,
                "reuse_interpretation": reuse_status,
            }
        )
    reuse = pd.DataFrame(reuse_rows)
    reuse.to_csv(output / "bridge_reuse_sensitivity.csv", index=False, lineterminator="\n")

    # Human-side Big Five relationships using official IPIP100 scoring keys.
    big_five_rows: list[dict[str, object]] = []
    big_five_cross: dict[str, list[float]] = {}
    for bridge_row in bridge.itertuples(index=False):
        out: dict[str, object] = {
            "trait": bridge_row.trait,
            "review_decision": bridge_row.review_decision,
            "bridge_tier": bridge_row.bridge_tier,
        }
        cross_values = []
        for dimension, (scale_key, direction) in BIG_FIVE_KEYS.items():
            signs = {item: sign * direction for item, sign in scale_key_signs[scale_key].items()}
            estimate, n_eff, _, used_count = composite_correlation(
                pearson,
                proxy_items[bridge_row.trait],
                proxy_signs[bridge_row.trait],
                scale_key_items[scale_key],
                signs,
                cross_n,
                remove_shared=True,
            )
            cross_values.append(estimate)
            out[f"{dimension}_pearson_r"] = round(estimate, 8)
            out[f"{dimension}_pairwise_effective_n"] = round(n_eff, 2)
            out[f"{dimension}_scale_items_after_part_whole_exclusion"] = used_count
        absolute = np.abs(np.asarray(cross_values))
        out["strongest_big_five_dimension"] = list(BIG_FIVE_KEYS)[int(np.nanargmax(absolute))]
        out["strongest_big_five_absolute_r"] = round(float(np.nanmax(absolute)), 8)
        big_five_cross[bridge_row.trait] = cross_values
        big_five_rows.append(out)

    big_dimensions = list(BIG_FIVE_KEYS)
    big_matrix = np.eye(5)
    for left_index, left_dimension in enumerate(big_dimensions):
        left_key, left_direction = BIG_FIVE_KEYS[left_dimension]
        left_signs = {item: sign * left_direction for item, sign in scale_key_signs[left_key].items()}
        for right_index in range(left_index + 1, 5):
            right_dimension = big_dimensions[right_index]
            right_key, right_direction = BIG_FIVE_KEYS[right_dimension]
            right_signs = {
                item: sign * right_direction for item, sign in scale_key_signs[right_key].items()
            }
            estimate, _, _, _ = composite_correlation(
                pearson,
                scale_key_items[left_key],
                left_signs,
                scale_key_items[right_key],
                right_signs,
                None,
                remove_shared=True,
            )
            big_matrix[left_index, right_index] = big_matrix[right_index, left_index] = estimate
    big_psd, _, _ = nearest_psd_correlation(big_matrix)
    inverse_big = np.linalg.pinv(big_psd + np.eye(5) * 1e-8)
    for row in big_five_rows:
        vector = np.asarray(big_five_cross[row["trait"]], dtype=float)
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            r_squared = float(np.clip(vector @ inverse_big @ vector, 0.0, 1.0))
        if not np.isfinite(r_squared):
            raise FloatingPointError(f"Nonfinite Big Five multiple R-squared for {row['trait']}")
        row["big_five_multiple_r_squared"] = round(r_squared, 8)
        row["big_five_method"] = "part-whole-corrected proxy-to-IPIP100 correlations"
    big_five = pd.DataFrame(big_five_rows)
    big_five.to_csv(output / "retained_traits_vs_human_big_five.csv", index=False, lineterminator="\n")

    # Dimensionality, clustering, and Big Five residual summaries.
    rng = np.random.default_rng(SEED)
    spectrum_rows: list[dict[str, object]] = []
    cluster_rows: list[dict[str, object]] = []
    dimensionality_summary: dict[str, object] = {
        "method": {
            "correlation": "standardized unit-weight proxy composites from pairwise-complete item correlations",
            "psd_adjustment": "eigenvalue clipping plus diagonal renormalization",
            "parallel_analysis": f"{PARALLEL_DRAWS} Gaussian draws at median proxy-pair effective N",
            "parallel_analysis_seed": SEED,
            "clustering": "average linkage on sqrt((1-r)/2); k selected by silhouette",
        },
        "tiers": {},
        "spearman_sensitivity": rank_sensitivity,
        "planned_missingness": missingness_summary,
    }
    psd_matrices: dict[str, np.ndarray] = {}
    for tier_name in ["accept_direct", "accept_direct_plus_close"]:
        tier = matrix_results[tier_name]
        spectrum, clusters, summary, psd = dimensionality_analysis(
            tier_name, tier["traits"], tier["pearson"], tier["n"], rng
        )
        spectrum_rows.extend(spectrum)
        cluster_rows.extend(clusters)
        dimensionality_summary["tiers"][tier_name] = summary
        psd_matrices[tier_name] = psd

    # Residual human trait structure after linearly partialing the five IPIP100 domains.
    for tier_name in ["accept_direct", "accept_direct_plus_close"]:
        tier_traits = matrix_results[tier_name]["traits"]
        cross = np.array([big_five_cross[trait] for trait in tier_traits], dtype=float)
        with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
            residual_covariance = psd_matrices[tier_name] - cross @ inverse_big @ cross.T
        if not np.isfinite(residual_covariance).all():
            raise FloatingPointError(f"Nonfinite Big Five residual covariance for {tier_name}")
        diagonal = np.sqrt(np.maximum(np.diag(residual_covariance), 1e-8))
        residual_correlation = residual_covariance / np.outer(diagonal, diagonal)
        residual_correlation = np.clip((residual_correlation + residual_correlation.T) / 2.0, -1.0, 1.0)
        np.fill_diagonal(residual_correlation, 1.0)
        residual_psd, residual_min, residual_adjustment = nearest_psd_correlation(residual_correlation)
        residual_eigenvalues = np.linalg.eigvalsh(residual_psd)[::-1]
        residual_participation, residual_entropy = effective_ranks(residual_eigenvalues)
        tier_big_r2 = big_five.loc[big_five["trait"].isin(tier_traits), "big_five_multiple_r_squared"]
        dimensionality_summary["tiers"][tier_name]["big_five_multiple_r_squared_median"] = round(
            float(tier_big_r2.median()), 6
        )
        dimensionality_summary["tiers"][tier_name]["big_five_multiple_r_squared_p25"] = round(
            float(tier_big_r2.quantile(0.25)), 6
        )
        dimensionality_summary["tiers"][tier_name]["big_five_multiple_r_squared_p75"] = round(
            float(tier_big_r2.quantile(0.75)), 6
        )
        dimensionality_summary["tiers"][tier_name]["traits_big_five_r2_below_0_50"] = int(
            (tier_big_r2 < 0.50).sum()
        )
        dimensionality_summary["tiers"][tier_name]["big_five_residual_raw_minimum_eigenvalue"] = round(
            residual_min, 8
        )
        dimensionality_summary["tiers"][tier_name]["big_five_residual_psd_max_adjustment"] = round(
            residual_adjustment, 8
        )
        dimensionality_summary["tiers"][tier_name]["big_five_residual_participation_ratio"] = round(
            residual_participation, 6
        )
        dimensionality_summary["tiers"][tier_name]["big_five_residual_entropy_effective_rank"] = round(
            residual_entropy, 6
        )

    pd.DataFrame(spectrum_rows).to_csv(
        output / "human_trait_proxy_eigenspectrum.csv", index=False, lineterminator="\n"
    )
    pd.DataFrame(cluster_rows).to_csv(
        output / "human_trait_proxy_clusters.csv", index=False, lineterminator="\n"
    )

    # Discriminant status and final human-measurement tier.
    coherence_lookup = coherence.set_index("trait")
    convergence_lookup = convergence.set_index("trait")
    reuse_item_counts = Counter(item for trait in all_traits for item in proxy_items[trait])
    scale_counts = Counter(
        scale for value in bridge["source_scales"] for scale in split_ids(value)
    )
    discriminant_rows: list[dict[str, object]] = []
    support_rows: list[dict[str, object]] = []
    for bridge_row in bridge.itertuples(index=False):
        trait = bridge_row.trait
        position = combined_index[trait]
        neighbor_values = np.abs(combined_corr[position]).copy()
        neighbor_values[position] = -np.inf
        neighbor_position = int(np.argmax(neighbor_values))
        neighbor_trait = combined_traits[neighbor_position]
        nearest_r = float(combined_corr[position, neighbor_position])
        coh = coherence_lookup.loc[trait]
        conv = convergence_lookup.loc[trait]
        internal_min_n = float(pd.to_numeric(coh["pairwise_n_min"], errors="coerce"))
        convergence_n = float(
            pd.to_numeric(conv["best_intended_pairwise_effective_n"], errors="coerce")
        )
        finite_evidence_n = [
            value for value in [internal_min_n, convergence_n] if np.isfinite(value)
        ]
        evidence_n = min(finite_evidence_n) if finite_evidence_n else float("nan")
        exact_alias = bool(trait_exact_alias[trait])
        maximum_reuse_delta = float(trait_max_reuse_delta[trait])
        direction_ambiguous = False
        if (
            direction_ambiguous
            or conv["intended_scale_association_status"] == "insufficient"
            or not np.isfinite(evidence_n)
            or evidence_n < 200
        ):
            structural_status = "INSUFFICIENT EVIDENCE"
            structural_reason = "direction/source-scale/effective-N criterion failed"
        elif (
            coh["coherence_status"] == "contradictory"
            or abs(nearest_r) >= 0.90
            or maximum_reuse_delta >= 0.20
            or conv["intended_scale_association_status"] == "weak"
        ):
            structural_status = "WEAK / REDUNDANT"
            structural_reason = "coherence, convergence, near-duplicate, or reuse criterion failed"
        elif (
            conv["intended_scale_association_status"] == "strong"
            and coh["coherence_status"] in {"strong", "moderate", "single_item_only"}
            and abs(nearest_r) < 0.80
        ):
            structural_status = "STRONG STRUCTURAL SUPPORT"
            structural_reason = "strong convergence with adequate coherence/discriminant structure"
        elif (
            conv["intended_scale_association_status"] in {"strong", "moderate"}
            and coh["coherence_status"] != "contradictory"
            and abs(nearest_r) < 0.90
        ):
            structural_status = "MODERATE STRUCTURAL SUPPORT"
            structural_reason = "moderate-or-better convergence without contradiction"
        else:
            structural_status = "WEAK / REDUNDANT"
            structural_reason = "did not meet preregistered moderate structural rule"

        max_item_reuse = max(reuse_item_counts[item] for item in proxy_items[trait])
        max_scale_reuse = max(scale_counts[scale] for scale in split_ids(bridge_row.source_scales))
        discriminant_rows.append(
            {
                "trait": trait,
                "review_decision": bridge_row.review_decision,
                "supporting_item_count": len(proxy_items[trait]),
                "coherence_status": coh["coherence_status"],
                "pearson_mean_interitem_r": coh["pearson_mean_interitem_r"],
                "intended_scale_convergence_status": conv["intended_scale_association_status"],
                "best_intended_absolute_r": conv["best_intended_absolute_r"],
                "best_intended_rank_of_131": conv["best_intended_rank_of_131"],
                "strongest_alternative_scoring_key": conv["strongest_alternative_scoring_key"],
                "strongest_alternative_absolute_r": conv["strongest_alternative_absolute_r"],
                "nearest_retained_proxy": neighbor_trait,
                "nearest_retained_proxy_pearson_r": round(nearest_r, 8),
                "nearest_retained_proxy_absolute_r": round(abs(nearest_r), 8),
                "max_item_reuse_count": max_item_reuse,
                "max_source_scale_reuse_count": max_scale_reuse,
                "exact_or_inverse_item_set_alias": exact_alias,
                "same_scale_high_redundancy_flag": bool(trait_high_scale_redundancy[trait]),
                "max_absolute_r_reduction_after_shared_item_removal": round(maximum_reuse_delta, 8),
                "minimum_contributing_pairwise_effective_n": round(evidence_n, 2),
                "structural_support_status": structural_status,
                "structural_support_reason": structural_reason,
            }
        )

        alpha_value = float(pd.to_numeric(coh["pearson_standardized_alpha"], errors="coerce"))
        mean_interitem = float(pd.to_numeric(coh["pearson_mean_interitem_r"], errors="coerce"))
        intended_abs = float(pd.to_numeric(conv["best_intended_absolute_r"], errors="coerce"))
        unresolved_reuse = exact_alias or maximum_reuse_delta >= 0.20 or trait_high_scale_redundancy[trait]
        if structural_status == "INSUFFICIENT EVIDENCE" or coh["coherence_status"] == "contradictory":
            quality_tier = "INSUFFICIENT"
        elif structural_status == "WEAK / REDUNDANT" and unresolved_reuse:
            quality_tier = "REDUNDANT / BROAD"
        elif len(proxy_items[trait]) == 1:
            quality_tier = (
                "MODERATE SUPPORT"
                if structural_status == "STRONG STRUCTURAL SUPPORT"
                and conv["intended_scale_association_status"] == "strong"
                else "LIMITED / SINGLE-ITEM"
            )
        elif (
            bridge_row.review_decision == "ACCEPT_DIRECT"
            and structural_status == "STRONG STRUCTURAL SUPPORT"
            and mean_interitem >= 0.25
            and alpha_value >= 0.50
            and intended_abs >= 0.30
            and evidence_n >= 300
            and not unresolved_reuse
        ):
            quality_tier = "HIGH HUMAN-MEASUREMENT SUPPORT"
        elif structural_status in {"STRONG STRUCTURAL SUPPORT", "MODERATE STRUCTURAL SUPPORT"}:
            quality_tier = "MODERATE SUPPORT"
        elif unresolved_reuse:
            quality_tier = "REDUNDANT / BROAD"
        else:
            quality_tier = "LIMITED / SINGLE-ITEM"
        if bridge_row.review_decision == "ACCEPT_CLOSE" and quality_tier == "HIGH HUMAN-MEASUREMENT SUPPORT":
            quality_tier = "MODERATE SUPPORT"
        support_rows.append(
            {
                "trait": trait,
                "canonical_definition": bridge_row.canonical_definition,
                "semantic_review_decision": bridge_row.review_decision,
                "bridge_tier": bridge_row.bridge_tier,
                "human_measurement_support_tier": quality_tier,
                "structural_support_status": structural_status,
                "supporting_item_count": len(proxy_items[trait]),
                "sapa_item_ids": bridge_row.sapa_item_ids,
                "source_scales": bridge_row.source_scales,
                "coherence_status": coh["coherence_status"],
                "pearson_mean_interitem_r": coh["pearson_mean_interitem_r"],
                "pearson_standardized_alpha": coh["pearson_standardized_alpha"],
                "source_scale_convergence_status": conv["intended_scale_association_status"],
                "best_intended_absolute_r": conv["best_intended_absolute_r"],
                "best_intended_rank_of_131": conv["best_intended_rank_of_131"],
                "nearest_retained_proxy": neighbor_trait,
                "nearest_retained_proxy_absolute_r": round(abs(nearest_r), 8),
                "exact_or_inverse_item_set_alias": exact_alias,
                "max_shared_item_effect": round(maximum_reuse_delta, 8),
                "minimum_pairwise_effective_n": round(evidence_n, 2),
                "rubric_version": "1.0",
                "review_status": "human_data_structural_diagnostic_pending_independent_expert_review",
            }
        )
    discriminant = pd.DataFrame(discriminant_rows)
    support = pd.DataFrame(support_rows)
    discriminant.to_csv(output / "trait_proxy_discriminant_audit.csv", index=False, lineterminator="\n")
    support.to_csv(
        output / "sapa_trait_bridge_psychometric_support_v1.csv", index=False, lineterminator="\n"
    )

    # Append support/reuse summaries to the dimensionality JSON.
    dimensionality_summary["human_measurement_support_counts"] = {
        decision: dict(Counter(group["human_measurement_support_tier"]))
        for decision, group in support.groupby("semantic_review_decision")
    }
    dimensionality_summary["structural_support_counts"] = {
        decision: dict(Counter(group["structural_support_status"]))
        for decision, group in discriminant.groupby("review_decision")
    }
    dimensionality_summary["single_item_counts"] = {
        decision: int(((support["semantic_review_decision"] == decision) & (support["supporting_item_count"] == 1)).sum())
        for decision in ["ACCEPT_DIRECT", "ACCEPT_CLOSE"]
    }
    dimensionality_summary["reuse"] = {
        "evaluated_shared_evidence_pairs": len(reuse),
        "exact_or_inverse_item_set_alias_pairs": int((reuse["reuse_interpretation"] == "exact_alias").sum()),
        "shared_item_sensitive_pairs": int((reuse["reuse_interpretation"] == "shared_item_sensitive").sum()),
        "same_scale_high_redundancy_pairs": int((reuse["reuse_interpretation"] == "same_scale_high_redundancy").sum()),
        "neighboring_construct_pairs": int((reuse["reuse_interpretation"] == "neighboring_construct").sum()),
        "differentiated_pairs": int((reuse["reuse_interpretation"] == "differentiated_despite_shared_scale_or_item").sum()),
        "median_absolute_full_correlation": round(float(reuse["full_proxy_pearson_r"].abs().median()), 6),
        "median_absolute_correlation_after_shared_item_removal": round(
            float(pd.to_numeric(reuse["shared_items_removed_pearson_r"], errors="coerce").abs().median()), 6
        ),
    }
    direct_support = support[support["semantic_review_decision"] == "ACCEPT_DIRECT"]
    close_support = support[support["semantic_review_decision"] == "ACCEPT_CLOSE"]
    dimensionality_summary["key_counts"] = {
        "direct_total": 45,
        "close_total": 29,
        "direct_high_human_measurement_support": int(
            (direct_support["human_measurement_support_tier"] == "HIGH HUMAN-MEASUREMENT SUPPORT").sum()
        ),
        "direct_moderate_support": int(
            (direct_support["human_measurement_support_tier"] == "MODERATE SUPPORT").sum()
        ),
        "direct_limited_single_item": int(
            (direct_support["human_measurement_support_tier"] == "LIMITED / SINGLE-ITEM").sum()
        ),
        "direct_redundant_broad": int(
            (direct_support["human_measurement_support_tier"] == "REDUNDANT / BROAD").sum()
        ),
        "direct_insufficient": int(
            (direct_support["human_measurement_support_tier"] == "INSUFFICIENT").sum()
        ),
        "close_moderate_or_better": int(
            (close_support["human_measurement_support_tier"] == "MODERATE SUPPORT").sum()
        ),
    }
    dimensionality_summary["polychoric"] = {
        "run": False,
        "reason": "No reliable local polychoric implementation was installed; Pearson and Spearman were retained as preregistered primary/sensitivity analyses.",
        "source_document_context": "The SAPA SPI development document reports mean Pearson-minus-polychoric correlation difference 0.0033 and proceeds with Pearson.",
    }
    dimensionality_summary["generated_at"] = GENERATED_AT
    (output / "human_trait_proxy_dimensionality_summary.json").write_text(
        json.dumps(dimensionality_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    spectrum = pd.DataFrame(spectrum_rows)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    for axis, tier_name, title in zip(
        axes,
        ["accept_direct", "accept_direct_plus_close"],
        ["45 ACCEPT_DIRECT proxies", "74 DIRECT + CLOSE proxies"],
    ):
        subset = spectrum[spectrum["analysis_tier"] == tier_name]
        axis.plot(subset["component"], subset["psd_eigenvalue"], marker="o", ms=3, label="Observed")
        axis.plot(subset["component"], subset["parallel_analysis_p95"], linestyle="--", label="Parallel p95")
        axis.axhline(1.0, color="0.6", linewidth=0.8, linestyle=":")
        axis.set(title=title, xlabel="Component", ylabel="Eigenvalue")
        axis.set_xlim(1, len(subset))
        axis.grid(alpha=0.2)
    axes[0].legend(frameon=False)
    fig.suptitle("Human SAPA trait-proxy eigenspectra (no model geometry)")
    fig.savefig(output / "human_trait_proxy_scree.png", dpi=160)
    plt.close(fig)

    source_manifest = {
        "artifact": "Human-only SAPA psychometric structure audit of the provisional trait bridge",
        "analysis_model": "GPT-5.5",
        "generated_at": GENERATED_AT,
        "rubric_version": "1.0",
        "rubric_freeze_commit": RUBRIC_FREEZE_COMMIT,
        "rubric_post_freeze_change": "Four Markdown hard-break trailing spaces were removed; criteria text and thresholds are unchanged.",
        "random_seed": SEED,
        "parallel_analysis_draws": PARALLEL_DRAWS,
        "inputs_loaded": {
            str(path.relative_to(repo)): sha256(path) for path in allowed_inputs
        },
        "raw_data": {
            "logical_path": str(raw_path.relative_to(repo)),
            "resolved_path": str(raw_path.resolve()),
            "sha256": sha256(raw_path),
            "respondents": 23679,
            "psychological_item_columns_loaded": 696,
            "respondent_id_or_demographic_columns_loaded": 0,
            "gitignored": True,
        },
        "analysis_tiers": {"primary_accept_direct": 45, "secondary_accept_close": 29},
        "methods": {
            "pearson": "pairwise-complete item correlations; primary",
            "spearman": "pairwise-complete retained-item rank correlations; sensitivity",
            "polychoric": "not run; no reliable local implementation installed",
            "proxy_composites": "standardized unit-weight composites from pairwise item correlations",
            "source_scale_convergence": "official superKey696 signs with proxy evidence items excluded",
            "reliability": "mean inter-item correlation and standardized alpha; omega not estimated for 2-3 item proxies",
            "missing_data": "planned-missing pairwise information; no complete-case analysis and no mean imputation",
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
        },
        "forbidden_inputs_loaded": [],
        "model_geometry_used": False,
        "human_to_model_projection_performed": False,
        "respondent_level_outputs_written": False,
        "gpu_used": False,
        "runpod_used": False,
        "external_model_api_used": False,
        "new_model_inference_used": False,
        "command": "python run_sapa_bridge_psychometric_audit.py --repo-root .",
    }
    (output / "source_manifest.json").write_text(
        json.dumps(source_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(json.dumps(dimensionality_summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
