#!/usr/bin/env python3
"""Run the frozen, semantically blinded SAPA partial-response LCA analysis.

This script deliberately reads only ``item_id`` from the canonical dictionary.
It never writes respondent-level responses, masks, split assignments, labels, or
posteriors. All committed products are aggregate class/profile diagnostics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix, issparse
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score

from latent_class_model import (
    LCASolution,
    align_profiles,
    build_sparse_responses,
    canonical_profile_order,
    expected_scores,
    fit_multiple_starts,
    free_parameter_count,
    normalized_entropy,
    posterior_and_loglik,
    profile_labels,
    reorder_solution,
)


SPLIT_SEED = 2026091301
START_BASE = 2026091300
REPLICATION_START_BASE = 2026099900
INITIAL_K = list(range(2, 13))
MAX_K = 16
N_STARTS = 6
EXPECTED_ROWS = 23_679
EXPECTED_ITEMS = 696
EXPECTED_COLUMNS = 719
ALPHA = 0.5
FIT_KWARGS = {
    "alpha": ALPHA,
    "dirichlet_concentration": 0.35,
    "max_iter": 250,
    "min_iter": 25,
    "tolerance_per_observation": 1e-7,
    "consecutive_tolerance": 5,
    "monotonicity_relative_tolerance": 1e-8,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_write(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def class_label(index: int) -> str:
    return profile_labels(index + 1)[-1]


def load_and_validate(
    respondent_path: Path, dictionary_path: Path
) -> tuple[np.ndarray, np.ndarray, list[str], dict[str, object]]:
    # Semantic blinding: the only dictionary column ever loaded here is item_id.
    dictionary = pd.read_csv(dictionary_path, usecols=["item_id"], dtype={"item_id": "string"})
    item_ids = dictionary["item_id"].astype(str).tolist()
    if len(item_ids) != EXPECTED_ITEMS or len(set(item_ids)) != EXPECTED_ITEMS:
        raise RuntimeError(f"expected {EXPECTED_ITEMS} unique canonical item IDs, got {len(item_ids)}")
    if not all(item.startswith("q_") for item in item_ids):
        raise RuntimeError("canonical eligibility includes a non-q_ item")

    header = pd.read_csv(respondent_path, sep="\t", nrows=0).columns.tolist()
    if len(header) != EXPECTED_COLUMNS:
        raise RuntimeError(f"expected {EXPECTED_COLUMNS} respondent columns, got {len(header)}")
    missing_items = [item for item in item_ids if item not in header]
    q_columns = [column for column in header if column.startswith("q_")]
    if missing_items or len(q_columns) != EXPECTED_ITEMS or set(q_columns) != set(item_ids):
        raise RuntimeError(
            f"behavioral item mismatch: missing={missing_items[:5]}, q_columns={len(q_columns)}"
        )
    nonitems = [column for column in header if column not in item_ids]
    if "RID" not in nonitems or len(nonitems) != EXPECTED_COLUMNS - EXPECTED_ITEMS:
        raise RuntimeError("unexpected non-item column structure")

    frame = pd.read_csv(
        respondent_path,
        sep="\t",
        usecols=["RID", *item_ids],
        dtype={"RID": "string"},
        low_memory=False,
    )
    if len(frame) != EXPECTED_ROWS:
        raise RuntimeError(f"expected {EXPECTED_ROWS} respondents, got {len(frame)}")
    duplicate_rids = int(frame["RID"].duplicated().sum())
    missing_rids = int(frame["RID"].isna().sum())
    if duplicate_rids or missing_rids:
        raise RuntimeError(f"RID integrity failure: duplicates={duplicate_rids}, missing={missing_rids}")

    numeric = frame[item_ids].apply(pd.to_numeric, errors="raise")
    observed = numeric.notna().to_numpy(dtype=bool)
    observed_values = numeric.to_numpy(dtype=np.float64)[observed]
    unique_codes = sorted(np.unique(observed_values).tolist())
    if unique_codes != [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]:
        raise RuntimeError(f"unexpected observed response codes: {unique_codes}")
    if not np.all(observed_values == np.floor(observed_values)):
        raise RuntimeError("non-integer response detected")
    responses = numeric.fillna(0).to_numpy(dtype=np.int8)
    answered = observed.sum(axis=1).astype(np.int32)
    zero_rows = int(np.sum(answered == 0))
    frame = None
    numeric = None

    integrity = {
        "respondent_rows": int(len(responses)),
        "respondent_columns": int(len(header)),
        "canonical_behavioral_items": len(item_ids),
        "behavioral_items_present": len(q_columns),
        "nonbehavioral_columns_excluded": len(nonitems),
        "nonbehavioral_columns": nonitems,
        "duplicate_respondent_ids": duplicate_rids,
        "missing_respondent_ids": missing_rids,
        "observed_response_codes": [int(x) for x in unique_codes],
        "missing_representation": "empty TAB fields parsed as NaN, encoded as zero only before sparse observed-mask construction",
        "zero_answer_rows": zero_rows,
        "observed_cells": int(observed.sum()),
        "observed_fraction": float(observed.mean()),
        "median_items_answered": float(np.median(answered)),
        "min_items_answered": int(answered.min()),
        "max_items_answered": int(answered.max()),
        "respondent_sha256": sha256(respondent_path),
        "dictionary_sha256": sha256(dictionary_path),
    }
    return responses, observed, item_ids, integrity


def deterministic_split(answered: np.ndarray) -> dict[str, np.ndarray]:
    informative = np.flatnonzero(answered > 0)
    rng = np.random.default_rng(SPLIT_SEED)
    permutation = rng.permutation(informative)
    n = len(permutation)
    n_train = math.floor(0.60 * n)
    n_validation = math.floor(0.20 * n)
    return {
        "discovery": np.sort(permutation[:n_train]),
        "validation": np.sort(permutation[n_train : n_train + n_validation]),
        "replication": np.sort(permutation[n_train + n_validation :]),
        "zero_answer": np.flatnonzero(answered == 0),
    }


def valid_solutions(solutions: list[LCASolution]) -> list[LCASolution]:
    return [solution for solution in solutions if solution.converged and solution.monotone]


def start_stability(
    best: LCASolution, solutions: list[LCASolution], item_weights: np.ndarray
) -> tuple[list[dict[str, object]], float]:
    rows: list[dict[str, object]] = []
    distances: list[float] = []
    for solution in solutions:
        mean_distance = float("nan")
        per_class: list[float] = []
        if solution.converged and solution.monotone:
            _, matched, mean_distance = align_profiles(best.theta, solution.theta, item_weights)
            per_class = matched.tolist()
            distances.append(mean_distance)
        rows.append(
            {
                "k": solution.k,
                "seed": solution.seed,
                "converged": solution.converged,
                "monotone": solution.monotone,
                "iterations": solution.iterations,
                "log_likelihood": solution.log_likelihood,
                "mean_distance_to_best": mean_distance,
                "per_class_distances": json.dumps(per_class),
            }
        )
    return rows, float(np.median(distances)) if distances else float("nan")


def predictive_summary(
    data, solution: LCASolution
) -> tuple[np.ndarray, float, float, float]:
    _, row_ll, total_ll = posterior_and_loglik(data, solution.pi, solution.theta)
    per_answer = row_ll / data.answered
    return per_answer, float(per_answer.mean()), float(per_answer.std(ddof=1) / np.sqrt(len(per_answer))), total_ll


def fit_k(
    k: int,
    train_data,
    validation_data,
    replication_data,
    item_weights: np.ndarray,
) -> tuple[dict[str, object], list[dict[str, object]], LCASolution, dict[str, np.ndarray]]:
    seeds = [START_BASE + 100 * k + index for index in range(1, N_STARTS + 1)]
    started = time.time()
    solutions = fit_multiple_starts(train_data, k, seeds, **FIT_KWARGS)
    elapsed = time.time() - started
    valid = valid_solutions(solutions)
    if not valid:
        raise RuntimeError(f"K={k}: no converged monotone starts")
    best = valid[0]
    stability_rows, median_start_distance = start_stability(best, solutions, item_weights)
    entropy, normalized = normalized_entropy(best.responsibilities)
    effective_sizes = best.responsibilities.sum(axis=0)
    map_sizes = np.bincount(best.responsibilities.argmax(axis=1), minlength=k)
    params = free_parameter_count(k, train_data.n_items, train_data.n_categories)
    aic = 2 * params - 2 * best.log_likelihood
    bic = math.log(train_data.n_rows) * params - 2 * best.log_likelihood
    icl = bic + 2 * float(entropy.sum())
    val_pa, val_mean, val_se, val_ll = predictive_summary(validation_data, best)
    rep_pa, rep_mean, rep_se, rep_ll = predictive_summary(replication_data, best)
    ll_values = np.array([solution.log_likelihood for solution in valid])
    sorted_ll = np.sort(ll_values)[::-1]
    next_spread = float(sorted_ll[0] - sorted_ll[1]) if len(sorted_ll) > 1 else float("nan")
    min_eff_prop = float(effective_sizes.min() / train_data.n_rows)
    min_map_prop = float(map_sizes.min() / train_data.n_rows)
    eligible = bool(
        len(valid) >= 4
        and min_eff_prop >= 0.02
        and min_map_prop >= 0.02
        and median_start_distance <= 0.10
    )
    warning = bool(
        median_start_distance > 0.05
        or (np.isfinite(next_spread) and next_spread / train_data.n_observed > 0.001)
    )
    metric = {
        "k": k,
        "attempted_starts": len(solutions),
        "converged_starts": len(valid),
        "best_seed": best.seed,
        "best_iterations": best.iterations,
        "elapsed_seconds": elapsed,
        "observed_data_log_likelihood": best.log_likelihood,
        "parameters": params,
        "aic": aic,
        "bic": bic,
        "icl": icl,
        "posterior_entropy_sum": float(entropy.sum()),
        "classification_certainty": float(1 - normalized.mean()),
        "median_max_posterior": float(np.median(best.responsibilities.max(axis=1))),
        "smallest_effective_class_n": float(effective_sizes.min()),
        "smallest_effective_class_proportion": min_eff_prop,
        "smallest_map_class_n": int(map_sizes.min()),
        "smallest_map_class_proportion": min_map_prop,
        "best_converged_log_likelihood": float(ll_values.max()),
        "worst_converged_log_likelihood": float(ll_values.min()),
        "sd_converged_log_likelihood": float(ll_values.std(ddof=1)) if len(ll_values) > 1 else 0.0,
        "best_to_second_log_likelihood_spread": next_spread,
        "median_start_profile_distance": median_start_distance,
        "local_optimum_warning": warning,
        "eligible": eligible,
        "validation_log_likelihood": val_ll,
        "validation_mean_log_likelihood_per_answer": val_mean,
        "validation_se_log_likelihood_per_answer": val_se,
        "replication_log_likelihood": rep_ll,
        "replication_mean_log_likelihood_per_answer": rep_mean,
        "replication_se_log_likelihood_per_answer": rep_se,
    }
    arrays = {"validation_per_answer": val_pa, "replication_per_answer": rep_pa}
    print(json.dumps({"completed_k": k, **metric}, default=str), flush=True)
    return metric, stability_rows, best, arrays


def apply_selection_rules(
    metrics: pd.DataFrame, predictive_arrays: dict[int, dict[str, np.ndarray]]
) -> tuple[pd.DataFrame, list[int], int, dict[str, object]]:
    result = metrics.copy()
    eligible = result[result["eligible"]].copy()
    if eligible.empty:
        raise RuntimeError("no K is eligible under frozen rules")
    validation_best = int(
        eligible.sort_values(
            ["validation_mean_log_likelihood_per_answer", "k"], ascending=[False, True]
        ).iloc[0]["k"]
    )
    best_values = predictive_arrays[validation_best]["validation_per_answer"]
    one_se_flags = []
    paired_losses = []
    paired_ses = []
    for k in result["k"].astype(int):
        values = predictive_arrays[k]["validation_per_answer"]
        difference = best_values - values
        loss = float(difference.mean())
        se = float(difference.std(ddof=1) / np.sqrt(len(difference)))
        paired_losses.append(loss)
        paired_ses.append(se)
        one_se_flags.append(bool(result.loc[result["k"] == k, "eligible"].iloc[0] and loss <= se))
    result["paired_validation_loss_from_best"] = paired_losses
    result["paired_validation_loss_se"] = paired_ses
    result["predictive_one_se_support"] = one_se_flags
    bic_min = float(eligible["bic"].min())
    icl_min = float(eligible["icl"].min())
    result["delta_bic"] = result["bic"] - bic_min
    result["delta_icl"] = result["icl"] - icl_min
    result["information_criterion_support"] = (
        result["eligible"] & ((result["delta_bic"] <= 10) | (result["delta_icl"] <= 10))
    )
    result["frozen_candidate"] = (
        result["predictive_one_se_support"] & result["information_criterion_support"]
    )
    candidate = sorted(result.loc[result["frozen_candidate"], "k"].astype(int).tolist())
    conflict = False
    if candidate:
        preferred = min(candidate)
        reason = "smallest K in predictive one-SE and information-criterion intersection"
    else:
        conflict = True
        bic_best = int(eligible.sort_values(["bic", "k"]).iloc[0]["k"])
        icl_best = int(eligible.sort_values(["icl", "k"]).iloc[0]["k"])
        candidate = sorted(set([validation_best, bic_best, icl_best]))
        preferred = validation_best
        reason = (
            "no frozen-rule intersection; retained validation-best/BIC-best/ICL-best anchors; "
            "reference diagnostics use validation-best without claiming a unique winner"
        )
        result["frozen_candidate"] = result["k"].isin(candidate)
    summary = {
        "validation_best_k": validation_best,
        "bic_best_k": int(eligible.sort_values(["bic", "k"]).iloc[0]["k"]),
        "icl_best_k": int(eligible.sort_values(["icl", "k"]).iloc[0]["k"]),
        "candidate_k": candidate,
        "reference_k": preferred,
        "selection_conflict": conflict,
        "selection_reason": reason,
    }
    return result, candidate, preferred, summary


def extension_passes(
    metrics: list[dict[str, object]], predictive_arrays: dict[int, dict[str, np.ndarray]], k: int
) -> tuple[bool, dict[str, object]]:
    table = pd.DataFrame(metrics)
    current = table[table.k == k].iloc[0]
    prior = table[table.k == k - 1].iloc[0]
    eligible = bool(current.eligible)
    validation_best = bool(
        current.validation_mean_log_likelihood_per_answer
        >= table[table.eligible].validation_mean_log_likelihood_per_answer.max() - 1e-15
    )
    diff = (
        predictive_arrays[k]["validation_per_answer"]
        - predictive_arrays[k - 1]["validation_per_answer"]
    )
    improvement = float(diff.mean())
    se = float(diff.std(ddof=1) / np.sqrt(len(diff)))
    material = bool(improvement > 0.0005 and improvement > se)
    aic_improves = bool(current.aic < prior.aic)
    checks = {
        "boundary_k": k,
        "eligible": eligible,
        "validation_best": validation_best,
        "paired_improvement_per_answer": improvement,
        "paired_improvement_se": se,
        "material_improvement": material,
        "aic_improves": aic_improves,
    }
    return bool(eligible and validation_best and material and aic_improves), checks


def canonicalize(solution: LCASolution) -> LCASolution:
    return reorder_solution(solution, canonical_profile_order(solution.theta))


def profile_tables(
    candidate_k: list[int],
    solutions: dict[int, LCASolution],
    data,
    item_ids: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[int, LCASolution]]:
    probability_rows: list[dict[str, object]] = []
    expected_rows: list[dict[str, object]] = []
    size_rows: list[dict[str, object]] = []
    canonical: dict[int, LCASolution] = {}
    for k in candidate_k:
        solution = canonicalize(solutions[k])
        canonical[k] = solution
        labels = profile_labels(k)
        scores = expected_scores(solution.theta)
        counts_flat = np.asarray(data.design.T @ solution.responsibilities)
        counts = counts_flat.reshape(len(item_ids), 6, k).transpose(2, 0, 1)
        support = counts.sum(axis=2)
        category_grid = np.arange(1, 7, dtype=float)
        response_variance = np.sum(
            solution.theta * (category_grid[None, None, :] - scores[:, :, None]) ** 2,
            axis=2,
        )
        expected_se = np.sqrt(response_variance / np.maximum(support + 3.0, 1.0))
        for profile in range(k):
            map_n = int(np.sum(solution.responsibilities.argmax(axis=1) == profile))
            size_rows.append(
                {
                    "k": k,
                    "profile": labels[profile],
                    "prior_proportion": solution.pi[profile],
                    "effective_discovery_n": float(solution.responsibilities[:, profile].sum()),
                    "map_discovery_n": map_n,
                    "map_discovery_proportion": map_n / data.n_rows,
                }
            )
            row = {"k": k, "profile": labels[profile]}
            for item_index, item_id in enumerate(item_ids):
                theta = solution.theta[profile, item_index]
                probability_rows.append(
                    {
                        "k": k,
                        "profile": labels[profile],
                        "item_id": item_id,
                        **{f"probability_response_{category}": theta[category - 1] for category in range(1, 7)},
                        "expected_response": scores[profile, item_index],
                        "posterior_weighted_observed_support": support[profile, item_index],
                        "expected_response_standard_error": expected_se[profile, item_index],
                    }
                )
                row[item_id] = scores[profile, item_index]
            expected_rows.append(row)
    return (
        pd.DataFrame(probability_rows),
        pd.DataFrame(expected_rows),
        pd.DataFrame(size_rows),
        canonical,
    )


def refit_stability(
    candidate_k: list[int],
    discovery: dict[int, LCASolution],
    replication_data,
    item_weights: np.ndarray,
) -> tuple[pd.DataFrame, dict[int, LCASolution]]:
    rows: list[dict[str, object]] = []
    refits: dict[int, LCASolution] = {}
    for k in candidate_k:
        seeds = [REPLICATION_START_BASE + 100 * k + i for i in range(1, N_STARTS + 1)]
        started = time.time()
        solutions = fit_multiple_starts(replication_data, k, seeds, **FIT_KWARGS)
        valid = valid_solutions(solutions)
        if not valid:
            rows.append({"k": k, "status": "no converged replication refit"})
            continue
        refit = valid[0]
        reference = canonicalize(discovery[k])
        order, distances, mean_distance = align_profiles(reference.theta, refit.theta, item_weights)
        aligned = reorder_solution(refit, order)
        refits[k] = aligned
        rating = "high" if mean_distance <= 0.075 else "moderate" if mean_distance <= 0.125 else "low"
        for profile, distance in enumerate(distances):
            rows.append(
                {
                    "k": k,
                    "profile": profile_labels(k)[profile],
                    "status": "completed",
                    "replication_stability_rating": rating,
                    "aligned_profile_distance": distance,
                    "mean_aligned_profile_distance": mean_distance,
                    "discovery_prior_proportion": reference.pi[profile],
                    "replication_prior_proportion": aligned.pi[profile],
                    "replication_best_seed": aligned.seed,
                    "replication_converged_starts": len(valid),
                    "replication_refit_seconds": time.time() - started,
                }
            )
        print(json.dumps({"replication_refit_k": k, "distance": mean_distance, "rating": rating}), flush=True)
    return pd.DataFrame(rows), refits


def posterior_certainty_tables(
    all_data,
    solution: LCASolution,
    splits: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float], np.ndarray]:
    posterior, _, _ = posterior_and_loglik(all_data, solution.pi, solution.theta)
    max_post = posterior.max(axis=1)
    raw_entropy, norm_entropy = normalized_entropy(posterior)
    rows: list[dict[str, object]] = []
    for split_name, indices in splits.items():
        values = max_post[indices]
        ent = raw_entropy[indices]
        norm = norm_entropy[indices]
        rows.append(
            {
                "subset": split_name,
                "n": len(indices),
                "mean_max_posterior": float(values.mean()) if len(values) else float("nan"),
                "median_max_posterior": float(np.median(values)) if len(values) else float("nan"),
                "p10_max_posterior": float(np.quantile(values, 0.10)) if len(values) else float("nan"),
                "p25_max_posterior": float(np.quantile(values, 0.25)) if len(values) else float("nan"),
                "p75_max_posterior": float(np.quantile(values, 0.75)) if len(values) else float("nan"),
                "p90_max_posterior": float(np.quantile(values, 0.90)) if len(values) else float("nan"),
                "share_ge_0_50": float(np.mean(values >= 0.50)) if len(values) else float("nan"),
                "share_ge_0_70": float(np.mean(values >= 0.70)) if len(values) else float("nan"),
                "share_ge_0_80": float(np.mean(values >= 0.80)) if len(values) else float("nan"),
                "share_ge_0_90": float(np.mean(values >= 0.90)) if len(values) else float("nan"),
                "mean_posterior_entropy": float(ent.mean()) if len(values) else float("nan"),
                "mean_normalized_posterior_entropy": float(norm.mean()) if len(values) else float("nan"),
            }
        )
    informative = np.flatnonzero(all_data.answered > 0)
    rows.insert(
        0,
        {
            "subset": "all_respondents",
            "n": all_data.n_rows,
            "mean_max_posterior": float(max_post.mean()),
            "median_max_posterior": float(np.median(max_post)),
            "p10_max_posterior": float(np.quantile(max_post, 0.10)),
            "p25_max_posterior": float(np.quantile(max_post, 0.25)),
            "p75_max_posterior": float(np.quantile(max_post, 0.75)),
            "p90_max_posterior": float(np.quantile(max_post, 0.90)),
            "share_ge_0_50": float(np.mean(max_post >= 0.50)),
            "share_ge_0_70": float(np.mean(max_post >= 0.70)),
            "share_ge_0_80": float(np.mean(max_post >= 0.80)),
            "share_ge_0_90": float(np.mean(max_post >= 0.90)),
            "mean_posterior_entropy": float(raw_entropy.mean()),
            "mean_normalized_posterior_entropy": float(norm_entropy.mean()),
        },
    )

    answered = all_data.answered[informative]
    cert = max_post[informative]
    bins = pd.qcut(answered, q=10, duplicates="drop")
    bin_frame = pd.DataFrame({"answered": answered, "certainty": cert, "bin": bins})
    grouped = bin_frame.groupby("bin", observed=True)
    bin_rows = []
    for index, (_, group) in enumerate(grouped, start=1):
        bin_rows.append(
            {
                "answered_count_bin": index,
                "n": len(group),
                "min_items_answered": int(group.answered.min()),
                "max_items_answered": int(group.answered.max()),
                "mean_items_answered": float(group.answered.mean()),
                "median_items_answered": float(group.answered.median()),
                "mean_max_posterior": float(group.certainty.mean()),
                "median_max_posterior": float(group.certainty.median()),
                "share_ge_0_70": float(np.mean(group.certainty >= 0.70)),
                "share_ge_0_80": float(np.mean(group.certainty >= 0.80)),
                "share_ge_0_90": float(np.mean(group.certainty >= 0.90)),
            }
        )
    rho, p_value = spearmanr(answered, cert)
    slope, intercept = np.polyfit(np.log1p(answered), cert, 1)
    relationship = {
        "spearman_rho": float(rho),
        "spearman_p_value": float(p_value),
        "linear_slope_max_posterior_per_log1p_answered": float(slope),
        "linear_intercept": float(intercept),
    }
    return pd.DataFrame(rows), pd.DataFrame(bin_rows), relationship, posterior


def classifier_metrics(
    features,
    labels: np.ndarray,
    splits: dict[str, np.ndarray],
    k: int,
    diagnostic: str,
) -> list[dict[str, object]]:
    # Dense auxiliary summaries include item count (0--311) beside proportions
    # (0--1). Standardize from discovery rows to prevent scale-driven LBFGS
    # overflow. The sparse binary 696-item administration mask is left in its
    # natural 0/1 units.
    if issparse(features):
        model_features = features
        standardized = False
    else:
        model_features = np.asarray(features, dtype=np.float64).copy()
        train_values = model_features[splits["discovery"]]
        means = train_values.mean(axis=0)
        scales = train_values.std(axis=0)
        scales[scales == 0] = 1.0
        model_features = (model_features - means) / scales
        standardized = True
    model = LogisticRegression(
        C=1.0,
        solver="lbfgs",
        max_iter=1000,
        class_weight="balanced",
        random_state=0,
    )
    model.fit(model_features[splits["discovery"]], labels[splits["discovery"]])
    rows: list[dict[str, object]] = []
    for subset in ["validation", "replication"]:
        indices = splits[subset]
        predicted = model.predict(model_features[indices])
        truth = labels[indices]
        counts = np.bincount(truth, minlength=k)
        majority = float(counts.max() / counts.sum())
        accuracy = float(accuracy_score(truth, predicted))
        balanced = float(balanced_accuracy_score(truth, predicted))
        rows.append(
            {
                "diagnostic": diagnostic,
                "subset": subset,
                "n": len(indices),
                "accuracy": accuracy,
                "balanced_accuracy": balanced,
                "majority_accuracy_baseline": majority,
                "balanced_accuracy_chance": 1 / k,
                "adjusted_accuracy_above_majority": (accuracy - majority) / max(1 - majority, 1e-12),
                "converged": int(model.n_iter_.max()) < model.max_iter,
                "iterations": int(model.n_iter_.max()),
                "discovery_fitted_dense_standardization": standardized,
            }
        )
    return rows


def administration_diagnostics(
    mask: np.ndarray,
    answered: np.ndarray,
    posterior: np.ndarray,
    splits: dict[str, np.ndarray],
    item_ids: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    k = posterior.shape[1]
    labels = posterior.argmax(axis=1)
    sparse_mask = csr_matrix(mask.astype(np.float64))
    count_features = answered[:, None].astype(np.float64)
    classifier_rows = classifier_metrics(sparse_mask, labels, splits, k, "full_696_item_response_mask")
    classifier_rows += classifier_metrics(count_features, labels, splits, k, "answered_item_count_only")

    weighted_observed = np.asarray(sparse_mask.T @ posterior).T
    effective_n = posterior.sum(axis=0)
    frequency = weighted_observed / effective_n[:, None]
    frequency_rows = []
    for profile in range(k):
        for item_index, item_id in enumerate(item_ids):
            frequency_rows.append(
                {
                    "profile": profile_labels(k)[profile],
                    "item_id": item_id,
                    "posterior_weighted_observation_frequency": frequency[profile, item_index],
                }
            )
    range_by_item = frequency.max(axis=0) - frequency.min(axis=0)
    summary = {
        "max_profile_observation_frequency_range": float(range_by_item.max()),
        "median_profile_observation_frequency_range": float(np.median(range_by_item)),
        "mean_profile_observation_frequency_range": float(range_by_item.mean()),
    }
    rep_mask = next(
        row for row in classifier_rows if row["diagnostic"] == "full_696_item_response_mask" and row["subset"] == "replication"
    )
    summary["strong_missingness_warning"] = bool(
        rep_mask["balanced_accuracy"] > 1 / k + 0.15
        or rep_mask["adjusted_accuracy_above_majority"] > 0.25
    )
    count_rows = []
    for profile in range(k):
        weights = posterior[:, profile]
        count_rows.append(
            {
                "profile": profile_labels(k)[profile],
                "posterior_effective_n": float(weights.sum()),
                "posterior_weighted_mean_items_answered": float(np.average(answered, weights=weights)),
                "posterior_weighted_sd_items_answered": float(
                    np.sqrt(np.average((answered - np.average(answered, weights=weights)) ** 2, weights=weights))
                ),
            }
        )
    return pd.DataFrame(classifier_rows), pd.DataFrame(frequency_rows), pd.DataFrame(count_rows), summary


def respondent_style_features(responses: np.ndarray, mask: np.ndarray) -> np.ndarray:
    answered = mask.sum(axis=1).astype(float)
    safe = np.maximum(answered, 1.0)
    values = responses.astype(float)
    mean = values.sum(axis=1) / safe
    variance = ((values - mean[:, None]) ** 2 * mask).sum(axis=1) / safe
    frequencies = np.column_stack([np.sum(responses == category, axis=1) / safe for category in range(1, 7)])
    middle = frequencies[:, 2] + frequencies[:, 3]
    extreme = frequencies[:, 0] + frequencies[:, 5]
    high = frequencies[:, 4] + frequencies[:, 5]
    low = frequencies[:, 0] + frequencies[:, 1]
    return np.column_stack(
        [answered, mean, variance, frequencies[:, 0], frequencies[:, 5], middle, extreme, high, low, high - low]
    )


def response_style_diagnostics(
    responses: np.ndarray,
    mask: np.ndarray,
    posterior: np.ndarray,
    solution: LCASolution,
    splits: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    k = posterior.shape[1]
    labels = posterior.argmax(axis=1)
    features = respondent_style_features(responses, mask)
    classifier = pd.DataFrame(
        classifier_metrics(features, labels, splits, k, "raw_response_style_summaries")
    )
    rows = []
    safe_answered = np.maximum(mask.sum(axis=1), 1)
    respondent_metrics = {
        "mean_observed_response": responses.sum(axis=1) / safe_answered,
        "observed_response_variance": features[:, 2],
        "category_1_frequency": features[:, 3],
        "category_6_frequency": features[:, 4],
        "middle_category_3_4_frequency": features[:, 5],
        "extreme_category_1_6_frequency": features[:, 6],
        "high_category_5_6_frequency": features[:, 7],
        "low_category_1_2_frequency": features[:, 8],
        "high_minus_low_tendency": features[:, 9],
        "items_answered": features[:, 0],
    }
    for profile in range(k):
        weights = posterior[:, profile]
        row: dict[str, object] = {
            "profile": profile_labels(k)[profile],
            "posterior_effective_n": float(weights.sum()),
        }
        for name, values in respondent_metrics.items():
            row[name] = float(np.average(values, weights=weights))
        rows.append(row)

    scores = expected_scores(solution.theta)
    item_centered = scores - scores.mean(axis=0, keepdims=True)
    total_ss = float(np.sum(item_centered**2))
    double_centered = item_centered - item_centered.mean(axis=1, keepdims=True)
    fraction = float(np.sum(double_centered**2) / total_ss) if total_ss else float("nan")
    rep = classifier[classifier.subset == "replication"].iloc[0]
    summary = {
        "item_centered_between_profile_variance_fraction": fraction,
        "replication_balanced_accuracy": float(rep.balanced_accuracy),
        "replication_accuracy": float(rep.accuracy),
        "strong_response_style_warning": bool(
            rep.balanced_accuracy > 1 / k + 0.25 or fraction < 0.50
        ),
    }
    return pd.DataFrame(rows), classifier, summary


def make_figures(
    output: Path,
    metrics: pd.DataFrame,
    reference: LCASolution,
    item_ids: list[str],
    certainty_bins: pd.DataFrame,
    class_sizes: pd.DataFrame,
    missingness_classifier: pd.DataFrame,
) -> list[str]:
    generated: list[str] = []
    plt.style.use("seaborn-v0_8-whitegrid")
    ks = metrics.k.to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for criterion, color in [("aic", "#4C78A8"), ("bic", "#F58518"), ("icl", "#54A24B")]:
        delta = metrics[criterion] - metrics[criterion].min()
        axes[0].plot(ks, delta, marker="o", label=f"Δ{criterion.upper()}", color=color)
    axes[0].set_yscale("symlog", linthresh=10)
    axes[0].set_xlabel("Number of latent profiles (K)")
    axes[0].set_ylabel("Difference from criterion minimum (lower is better)")
    axes[0].legend()
    axes[1].errorbar(
        ks,
        metrics.validation_mean_log_likelihood_per_answer,
        yerr=metrics.validation_se_log_likelihood_per_answer,
        marker="o",
        label="Validation",
    )
    axes[1].plot(ks, metrics.replication_mean_log_likelihood_per_answer, marker="s", label="Locked replication")
    axes[1].set_xlabel("Number of latent profiles (K)")
    axes[1].set_ylabel("Mean observed-data log likelihood per answered item")
    axes[1].legend()
    fig.suptitle("SAPA categorical latent-profile model selection (item-ID blind)")
    fig.tight_layout()
    fig.savefig(output / "model_selection.png", dpi=180)
    plt.close(fig)
    generated.append("model_selection.png")

    scores = expected_scores(reference.theta)
    differentiation = scores.max(axis=0) - scores.min(axis=0)
    top = np.lexsort((np.arange(len(item_ids)), -differentiation))[:60]
    fig, ax = plt.subplots(figsize=(18, max(4, 0.7 * reference.k)))
    image = ax.imshow(scores[:, top], aspect="auto", cmap="RdBu_r", vmin=1, vmax=6)
    ax.set_yticks(np.arange(reference.k), profile_labels(reference.k))
    ax.set_xticks(np.arange(len(top)), [item_ids[index] for index in top], rotation=90, fontsize=6)
    ax.set_title("Anonymous profiles: 60 most differentiating item IDs")
    fig.colorbar(image, ax=ax, label="Expected response (1–6)")
    fig.tight_layout()
    fig.savefig(output / "profile_heatmap.png", dpi=180)
    plt.close(fig)
    generated.append("profile_heatmap.png")

    fig, ax = plt.subplots(figsize=(15, 6))
    for profile, label in enumerate(profile_labels(reference.k)):
        ax.plot(np.arange(len(item_ids)), scores[profile], linewidth=0.8, alpha=0.85, label=label)
    ax.set_xlabel("Canonical behavioral-item order")
    ax.set_ylabel("Expected response (1–6)")
    ax.set_ylim(1, 6)
    ax.set_title("Anonymous profile summary over all 696 items")
    ax.legend(ncol=min(reference.k, 6), fontsize=8)
    fig.tight_layout()
    fig.savefig(output / "profile_summary.png", dpi=180)
    plt.close(fig)
    generated.append("profile_summary.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(certainty_bins.mean_items_answered, certainty_bins.mean_max_posterior, marker="o", label="Mean max posterior")
    ax.plot(certainty_bins.mean_items_answered, certainty_bins.median_max_posterior, marker="s", label="Median max posterior")
    ax.set_xlabel("Mean items answered within deterministic count bin")
    ax.set_ylabel("Posterior assignment certainty")
    ax.set_ylim(0, 1.02)
    ax.legend()
    ax.set_title("Assignment certainty versus observed item count")
    fig.tight_layout()
    fig.savefig(output / "certainty_vs_items_answered.png", dpi=180)
    plt.close(fig)
    generated.append("certainty_vs_items_answered.png")

    subset = class_sizes[class_sizes.k == reference.k]
    x = np.arange(len(subset))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - 0.2, subset.effective_discovery_n, width=0.4, label="Posterior-effective")
    ax.bar(x + 0.2, subset.map_discovery_n, width=0.4, label="MAP assigned")
    ax.set_xticks(x, subset.profile)
    ax.set_ylabel("Discovery respondents")
    ax.set_title(f"Anonymous profile sizes for reference K={reference.k}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "class_sizes.png", dpi=180)
    plt.close(fig)
    generated.append("class_sizes.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    plot = missingness_classifier.copy()
    labels = [f"{row.diagnostic}\n{row.subset}" for _, row in plot.iterrows()]
    x = np.arange(len(plot))
    ax.bar(x, plot.balanced_accuracy, label="Balanced accuracy")
    ax.plot(x, plot.balanced_accuracy_chance, "k--", label="Chance")
    ax.set_xticks(x, labels, rotation=20, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Balanced accuracy")
    ax.set_title("Can administration masks predict frozen profile labels?")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "missingness_diagnostic.png", dpi=180)
    plt.close(fig)
    generated.append("missingness_diagnostic.png")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--respondent-data", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.time()

    synthetic = json.loads((output / "synthetic_validation_metrics.json").read_text(encoding="utf-8"))
    if synthetic.get("status") != "PASS":
        raise RuntimeError("synthetic validation gate has not passed")
    responses, mask, item_ids, integrity = load_and_validate(
        args.respondent_data.resolve(), args.dictionary.resolve()
    )
    answered = mask.sum(axis=1).astype(np.int32)
    splits = deterministic_split(answered)
    split_summary = {name: int(len(indices)) for name, indices in splits.items()}
    integrity["split_seed"] = SPLIT_SEED
    integrity["split_counts"] = split_summary
    json_write(output / "data_integrity_report.json", integrity)

    train_data = build_sparse_responses(responses[splits["discovery"]], observed_mask=mask[splits["discovery"]])
    validation_data = build_sparse_responses(responses[splits["validation"]], observed_mask=mask[splits["validation"]])
    replication_data = build_sparse_responses(responses[splits["replication"]], observed_mask=mask[splits["replication"]])
    all_data = build_sparse_responses(responses, observed_mask=mask)
    item_weights = mask[splits["discovery"]].sum(axis=0).astype(np.float64)

    metrics: list[dict[str, object]] = []
    start_rows: list[dict[str, object]] = []
    best_solutions: dict[int, LCASolution] = {}
    predictive_arrays: dict[int, dict[str, np.ndarray]] = {}
    extension_audit: list[dict[str, object]] = []
    for k in INITIAL_K:
        metric, rows, solution, arrays = fit_k(
            k, train_data, validation_data, replication_data, item_weights
        )
        metrics.append(metric)
        start_rows.extend(rows)
        best_solutions[k] = solution
        predictive_arrays[k] = arrays

    current = INITIAL_K[-1]
    while current < MAX_K:
        extend, audit = extension_passes(metrics, predictive_arrays, current)
        extension_audit.append(audit)
        if not extend:
            break
        current += 1
        metric, rows, solution, arrays = fit_k(
            current, train_data, validation_data, replication_data, item_weights
        )
        metrics.append(metric)
        start_rows.extend(rows)
        best_solutions[current] = solution
        predictive_arrays[current] = arrays

    metrics_df, candidate_k, reference_k, selection = apply_selection_rules(
        pd.DataFrame(metrics).sort_values("k"), predictive_arrays
    )
    metrics_df.to_csv(output / "model_selection_metrics.csv", index=False)
    pd.DataFrame(start_rows).to_csv(output / "start_robustness_metrics.csv", index=False)

    probabilities, expected, class_sizes, canonical_solutions = profile_tables(
        candidate_k, best_solutions, train_data, item_ids
    )
    probabilities.to_csv(output / "frozen_profile_item_probabilities.csv", index=False)
    expected.to_csv(output / "frozen_profile_expected_scores.csv", index=False)
    class_sizes.to_csv(output / "frozen_class_sizes.csv", index=False)
    reference = canonical_solutions[reference_k]

    stability, _ = refit_stability(
        candidate_k,
        best_solutions,
        replication_data,
        mask[splits["replication"]].sum(axis=0).astype(np.float64),
    )
    stability.to_csv(output / "profile_stability_metrics.csv", index=False)

    certainty, certainty_bins, certainty_relationship, posterior = posterior_certainty_tables(
        all_data, reference, splits
    )
    certainty.to_csv(output / "posterior_certainty_summary.csv", index=False)
    certainty_bins.to_csv(output / "certainty_by_items_answered.csv", index=False)

    mask_classifier, item_frequency, items_by_profile, missingness_summary = administration_diagnostics(
        mask, answered, posterior, splits, item_ids
    )
    mask_classifier.to_csv(output / "missingness_artifact_diagnostics.csv", index=False)
    item_frequency.to_csv(output / "missingness_item_frequency_by_profile.csv", index=False)
    items_by_profile.to_csv(output / "items_answered_by_profile.csv", index=False)

    response_style, response_classifier, response_summary = response_style_diagnostics(
        responses, mask, posterior, reference, splits
    )
    response_style.to_csv(output / "response_style_diagnostics.csv", index=False)
    response_classifier.to_csv(output / "response_style_classifier_metrics.csv", index=False)

    candidate_rows = metrics_df[metrics_df.k.isin(candidate_k)].copy()
    candidate_rows["reference_solution"] = candidate_rows.k == reference_k
    candidate_rows["selection_conflict"] = selection["selection_conflict"]
    candidate_rows["selection_reason"] = selection["selection_reason"]
    candidate_rows.to_csv(output / "candidate_solution_summary.csv", index=False)

    generated_figures = make_figures(
        output,
        metrics_df,
        reference,
        item_ids,
        certainty_bins,
        class_sizes,
        mask_classifier,
    )
    numerical_manifest = {
        "status": "FROZEN NUMERICAL OUTPUT; commit SHA recorded in downstream report",
        "semantic_blinding": "item_id column only; item_text was not read",
        "model_family": "six-category product-multinomial latent-class model",
        "fitted_k": metrics_df.k.astype(int).tolist(),
        "extension_audit": extension_audit,
        **selection,
        "certainty_relationship": certainty_relationship,
        "missingness_summary": missingness_summary,
        "response_style_summary": response_summary,
        "figures": generated_figures,
        "split_counts": split_summary,
        "elapsed_seconds": time.time() - started,
        "software": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "privacy": {
            "respondent_level_outputs_written": False,
            "individual_imputations_written": False,
        },
        "implementation_corrections_after_prefit_freeze": [
            {
                "scope": "auxiliary dense logistic diagnostics only",
                "change": "discovery-fitted column standardization before frozen L2/lbfgs regression",
                "reason": "unscaled item-count and proportion features caused LBFGS overflow warnings",
                "unchanged": "latent likelihood, K fits, profiles, selection rules, mask classifier, and semantic blinding",
            }
        ],
    }
    json_write(output / "numerical_freeze_manifest.json", numerical_manifest)
    print(json.dumps(numerical_manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
