#!/usr/bin/env python3
"""Materialize the frozen AA-12 SAPA K=4..10 numerical solution bank.

Only canonical item IDs are read from the dictionary. Respondent rows, masks,
split assignments, labels, and posteriors remain in memory and are never saved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import warnings
from pathlib import Path

for variable in (
    "VECLIB_MAXIMUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[variable] = "1"

# NumPy 2/Accelerate on this ARM host can emit stale floating-point status
# warnings from finite matrix products used inside sklearn. Every saved
# diagnostic is checked for finiteness below; suppress only these spurious
# status messages so a clean deterministic run is auditable.
warnings.filterwarnings("ignore", message=".*encountered in matmul", category=RuntimeWarning)

import numpy as np
import pandas as pd


K_VALUES = list(range(4, 11))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_write(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def assert_finite_numeric(frame: pd.DataFrame, label: str) -> None:
    numeric = frame.select_dtypes(include=[np.number])
    if not np.isfinite(numeric.to_numpy(dtype=np.float64)).all():
        raise RuntimeError(f"non-finite numeric value in {label}")


def profile_id(k: int, profile: str) -> str:
    return f"H{k:02d}_{profile.rsplit(' ', 1)[-1]}"


def eligibility_reason(row: pd.Series) -> str:
    if bool(row["eligible"]):
        return "eligible under original frozen AA-12 criteria"
    reasons = []
    if int(row["converged_starts"]) < 4:
        reasons.append(f"only {int(row['converged_starts'])}/6 converged monotone starts")
    if float(row["smallest_effective_class_proportion"]) < 0.02:
        reasons.append("smallest posterior-effective class proportion below 0.02")
    if float(row["smallest_map_class_proportion"]) < 0.02:
        reasons.append("smallest MAP class proportion below 0.02")
    if float(row["median_start_profile_distance"]) > 0.10:
        reasons.append("median aligned start distance above 0.10")
    return "; ".join(reasons) if reasons else "ineligible under original frozen AA-12 criteria"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--respondent-data", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--prior-output-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve() / "human"
    output.mkdir(parents=True, exist_ok=True)
    prior = args.prior_output_dir.resolve()

    sys.path.insert(0, str(prior))
    from latent_class_model import (  # noqa: PLC0415
        build_sparse_responses,
        expected_scores,
        posterior_and_loglik,
        profile_distance_matrix,
        profile_labels,
    )
    from run_sapa_numerical_analysis import (  # noqa: PLC0415
        administration_diagnostics,
        canonicalize,
        deterministic_split,
        fit_k,
        load_and_validate,
        profile_tables,
        refit_stability,
        response_style_diagnostics,
    )

    started = time.time()
    responses, mask, item_ids, integrity = load_and_validate(
        args.respondent_data.resolve(), args.dictionary.resolve()
    )
    answered = mask.sum(axis=1).astype(np.int32)
    splits = deterministic_split(answered)
    train_data = build_sparse_responses(responses[splits["discovery"]], observed_mask=mask[splits["discovery"]])
    validation_data = build_sparse_responses(
        responses[splits["validation"]], observed_mask=mask[splits["validation"]]
    )
    replication_data = build_sparse_responses(
        responses[splits["replication"]], observed_mask=mask[splits["replication"]]
    )
    all_data = build_sparse_responses(responses, observed_mask=mask)
    item_weights = mask[splits["discovery"]].sum(axis=0).astype(np.float64)

    fitted_metrics = []
    start_rows = []
    solutions = {}
    for k in K_VALUES:
        metric, starts, solution, _ = fit_k(
            k, train_data, validation_data, replication_data, item_weights
        )
        fitted_metrics.append(metric)
        start_rows.extend(starts)
        solutions[k] = solution
    fitted = pd.DataFrame(fitted_metrics).sort_values("k").reset_index(drop=True)
    original = pd.read_csv(prior / "model_selection_metrics.csv")
    frozen = original[original["k"].isin(K_VALUES)].sort_values("k").reset_index(drop=True)
    compare_columns = [
        "observed_data_log_likelihood",
        "best_seed",
        "converged_starts",
        "best_iterations",
        "bic",
        "icl",
        "median_start_profile_distance",
        "smallest_map_class_n",
        "validation_mean_log_likelihood_per_answer",
        "replication_mean_log_likelihood_per_answer",
        "eligible",
    ]
    comparisons = []
    for index, k in enumerate(K_VALUES):
        row = {"K": k}
        all_match = True
        for column in compare_columns:
            old = frozen.loc[index, column]
            new = fitted.loc[index, column]
            if isinstance(old, (bool, np.bool_)) or column == "eligible":
                match = bool(old) == bool(new)
            elif column in {"best_seed", "converged_starts", "best_iterations", "smallest_map_class_n"}:
                match = int(old) == int(new)
            else:
                match = bool(np.isclose(float(old), float(new), rtol=1e-11, atol=1e-7))
            row[f"{column}_matches"] = match
            all_match &= match
        row["all_frozen_metrics_match"] = all_match
        comparisons.append(row)
    if not all(row["all_frozen_metrics_match"] for row in comparisons):
        raise RuntimeError("rerun does not reproduce the frozen AA-12 K=4..10 metrics")

    probabilities, _, class_sizes, canonical = profile_tables(
        K_VALUES, solutions, train_data, item_ids
    )
    class_sizes["profile_id"] = [profile_id(int(k), profile) for k, profile in zip(class_sizes.k, class_sizes.profile)]
    class_lookup = class_sizes.set_index(["k", "profile"])
    probabilities["profile_id"] = [
        profile_id(int(k), profile) for k, profile in zip(probabilities.k, probabilities.profile)
    ]
    probabilities["domain"] = "human"
    probabilities["solution_status"] = probabilities["k"].map(
        frozen.set_index("k")["eligible"].map({True: "eligible", False: "DIAGNOSTIC / INELIGIBLE"})
    )
    probabilities["profile_size"] = [
        int(class_lookup.loc[(k, profile), "map_discovery_n"])
        for k, profile in zip(probabilities.k, probabilities.profile)
    ]
    probabilities["profile_proportion"] = [
        float(class_lookup.loc[(k, profile), "map_discovery_proportion"])
        for k, profile in zip(probabilities.k, probabilities.profile)
    ]
    probabilities["effective_discovery_n"] = [
        float(class_lookup.loc[(k, profile), "effective_discovery_n"])
        for k, profile in zip(probabilities.k, probabilities.profile)
    ]
    probabilities = probabilities.rename(
        columns={
            "k": "K",
            "probability_response_1": "p1",
            "probability_response_2": "p2",
            "probability_response_3": "p3",
            "probability_response_4": "p4",
            "probability_response_5": "p5",
            "probability_response_6": "p6",
        }
    )
    probability_columns = [
        "domain",
        "K",
        "solution_status",
        "profile_id",
        "profile_size",
        "profile_proportion",
        "effective_discovery_n",
        "item_id",
        "p1",
        "p2",
        "p3",
        "p4",
        "p5",
        "p6",
        "expected_response",
        "posterior_weighted_observed_support",
        "expected_response_standard_error",
    ]
    probabilities[probability_columns].to_csv(output / "human_cross_resolution_profiles.csv", index=False)

    stability, _ = refit_stability(
        K_VALUES,
        solutions,
        replication_data,
        mask[splits["replication"]].sum(axis=0).astype(np.float64),
    )
    stability["profile_id"] = [
        profile_id(int(k), profile) for k, profile in zip(stability.k, stability.profile)
    ]
    stability.to_csv(output / "human_split_refit_stability.csv", index=False)

    diagnostic_rows = []
    response_profile_rows = []
    mask_classifier_rows = []
    response_classifier_rows = []
    for k in K_VALUES:
        solution = canonical[k]
        posterior, _, _ = posterior_and_loglik(all_data, solution.pi, solution.theta)
        mask_classifier, _, _, missing_summary = administration_diagnostics(
            mask, answered, posterior, splits, item_ids
        )
        response_profiles, response_classifier, response_summary = response_style_diagnostics(
            responses, mask, posterior, solution, splits
        )
        mask_classifier["K"] = k
        response_classifier["K"] = k
        response_profiles["K"] = k
        response_profiles["profile_id"] = [profile_id(k, name) for name in response_profiles.profile]
        mask_classifier_rows.append(mask_classifier)
        response_classifier_rows.append(response_classifier)
        response_profile_rows.append(response_profiles)
        split_rows = stability[stability.k == k]
        diagnostic_rows.append(
            {
                "K": k,
                **missing_summary,
                **response_summary,
                "split_refit_mean_aligned_profile_distance": float(
                    split_rows.mean_aligned_profile_distance.iloc[0]
                ),
                "split_refit_stability_rating": split_rows.replication_stability_rating.iloc[0],
            }
        )

    diagnostics = pd.DataFrame(diagnostic_rows)
    assert_finite_numeric(diagnostics, "human diagnostic summary")
    diagnostics.to_csv(output / "human_diagnostic_summary.csv", index=False)
    mask_classifiers = pd.concat(mask_classifier_rows, ignore_index=True)
    response_classifiers = pd.concat(response_classifier_rows, ignore_index=True)
    response_profiles = pd.concat(response_profile_rows, ignore_index=True)
    assert_finite_numeric(mask_classifiers, "human missingness classifier metrics")
    assert_finite_numeric(response_classifiers, "human response-style classifier metrics")
    assert_finite_numeric(response_profiles, "human response-style profiles")
    mask_classifiers.to_csv(
        output / "human_missingness_classifier_metrics.csv", index=False
    )
    response_classifiers.to_csv(
        output / "human_response_style_classifier_metrics.csv", index=False
    )
    response_profiles.to_csv(
        output / "human_response_style_profiles.csv", index=False
    )

    continuity_rows = []
    for lower_k in range(4, 10):
        lower = canonical[lower_k]
        higher = canonical[lower_k + 1]
        cost = profile_distance_matrix(lower.theta, higher.theta, item_weights)
        lower_best = np.argmin(cost, axis=1)
        higher_best = np.argmin(cost, axis=0)
        lower_scores = expected_scores(lower.theta)
        higher_scores = expected_scores(higher.theta)
        for low in range(lower_k):
            for high in range(lower_k + 1):
                correlation = float(np.corrcoef(lower_scores[low], higher_scores[high])[0, 1])
                low_id = profile_id(lower_k, profile_labels(lower_k)[low])
                high_id = profile_id(lower_k + 1, profile_labels(lower_k + 1)[high])
                low_selects = int(lower_best[low]) == high
                high_selects = int(higher_best[high]) == low
                continuity_rows.append(
                    {
                        "lower_K": lower_k,
                        "higher_K": lower_k + 1,
                        "lower_profile_id": low_id,
                        "higher_profile_id": high_id,
                        "weighted_sqrt_js_distance": float(cost[low, high]),
                        "expected_score_profile_correlation": correlation,
                        "lower_profile_nearest_higher": low_selects,
                        "higher_profile_nearest_lower": high_selects,
                        "mutual_nearest": low_selects and high_selects,
                    }
                )
    pd.DataFrame(continuity_rows).to_csv(output / "human_adjacent_k_continuity.csv", index=False)

    summary = frozen.copy().rename(columns={"k": "K"})
    summary["fit_status"] = "available"
    summary["eligibility_reason"] = summary.apply(eligibility_reason, axis=1)
    summary["solution_status"] = summary["eligible"].map(
        {True: "eligible", False: "DIAGNOSTIC / INELIGIBLE"}
    )
    summary = summary.merge(diagnostics, on="K", how="left")
    summary_columns = [
        "K",
        "fit_status",
        "eligible",
        "solution_status",
        "eligibility_reason",
        "converged_starts",
        "observed_data_log_likelihood",
        "validation_mean_log_likelihood_per_answer",
        "replication_mean_log_likelihood_per_answer",
        "bic",
        "icl",
        "median_start_profile_distance",
        "split_refit_mean_aligned_profile_distance",
        "split_refit_stability_rating",
        "smallest_effective_class_proportion",
        "smallest_map_class_proportion",
        "local_optimum_warning",
        "strong_response_style_warning",
        "strong_missingness_warning",
        "item_centered_between_profile_variance_fraction",
        "replication_balanced_accuracy",
        "max_profile_observation_frequency_range",
    ]
    summary[summary_columns].to_csv(output / "human_cross_resolution_solution_summary.csv", index=False)
    class_sizes = class_sizes.rename(columns={"k": "K"})
    class_sizes[
        [
            "K",
            "profile_id",
            "prior_proportion",
            "effective_discovery_n",
            "map_discovery_n",
            "map_discovery_proportion",
        ]
    ].to_csv(output / "human_class_sizes.csv", index=False)
    pd.DataFrame(start_rows).to_csv(output / "human_start_robustness_metrics.csv", index=False)

    reproduction = {
        "status": "PASS",
        "source_numerical_freeze_commit": "f0e55723eacc16730d4d9184bcb8bb9868458fb0",
        "source_method_freeze_commit": "6b2e460f19efca5d4dbb47487461790651d34208",
        "metric_comparisons": comparisons,
        "respondent_integrity": integrity,
        "respondent_sha256": sha256(args.respondent_data.resolve()),
        "dictionary_sha256": sha256(args.dictionary.resolve()),
        "K_values": K_VALUES,
        "semantic_dictionary_columns_read": ["item_id"],
        "elapsed_seconds": time.time() - started,
        "privacy": {
            "respondent_level_outputs_written": False,
            "response_masks_written": False,
            "posteriors_written": False,
            "individual_imputations_written": False,
        },
    }
    json_write(output / "human_numerical_bank_manifest.json", reproduction)


if __name__ == "__main__":
    main()
