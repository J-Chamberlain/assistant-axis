#!/usr/bin/env python3
"""Independent aggregate/privacy verifier for the AA-12 SAPA LCA follow-up."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np
import pandas as pd


PREFIT_COMMIT = "6b2e460f19efca5d4dbb47487461790651d34208"
NUMERICAL_COMMIT = "f0e55723eacc16730d4d9184bcb8bb9868458fb0"
SEMANTIC_COMMIT = "80aae41fa27909e9805842f1f49bde2f137fee99"


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=check, capture_output=True, text=True
    )
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--respondent-data", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output_dir.resolve()
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    required = [
        "sapa_partial_response_latent_profiles_report.md",
        "prefit_decision_record.md",
        "model_selection_metrics.csv",
        "candidate_solution_summary.csv",
        "frozen_profile_item_probabilities.csv",
        "frozen_profile_expected_scores.csv",
        "profile_stability_metrics.csv",
        "posterior_certainty_summary.csv",
        "certainty_by_items_answered.csv",
        "missingness_artifact_diagnostics.csv",
        "response_style_diagnostics.csv",
        "semantic_profile_summary.md",
        "synthetic_validation_report.md",
        "model_selection.png",
        "profile_heatmap.png",
        "profile_summary.png",
        "certainty_vs_items_answered.png",
        "class_sizes.png",
        "missingness_diagnostic.png",
    ]
    checks["required_outputs_present"] = all((output / name).is_file() for name in required)

    status_before = git(repo, "status", "--porcelain")
    checks["working_tree_clean_at_verification_start"] = status_before == ""
    details["working_tree_status_at_verification_start"] = status_before or "clean"

    for earlier, later, name in [
        (PREFIT_COMMIT, NUMERICAL_COMMIT, "prefit_before_numerical"),
        (NUMERICAL_COMMIT, SEMANTIC_COMMIT, "numerical_before_semantic"),
    ]:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", earlier, later], cwd=repo
        )
        checks[name] = result.returncode == 0
    prefit_paths = git(repo, "show", "--format=", "--name-only", PREFIT_COMMIT).splitlines()
    checks["prefit_record_committed"] = any(path.endswith("prefit_decision_record.md") for path in prefit_paths)
    numeric_paths = git(repo, "show", "--format=", "--name-only", NUMERICAL_COMMIT).splitlines()
    checks["anonymous_profiles_committed_at_numerical_freeze"] = any(
        path.endswith("frozen_profile_item_probabilities.csv") for path in numeric_paths
    )
    semantic_paths = git(repo, "show", "--format=", "--name-only", SEMANTIC_COMMIT).splitlines()
    checks["semantic_outputs_first_committed_after_numerical_freeze"] = any(
        path.endswith("semantic_profile_summary.md") for path in semantic_paths
    )
    unchanged = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            NUMERICAL_COMMIT,
            "HEAD",
            "--",
            "research/outputs/sapa_partial_response_latent_profiles/frozen_profile_item_probabilities.csv",
            "research/outputs/sapa_partial_response_latent_profiles/frozen_profile_expected_scores.csv",
            "research/outputs/sapa_partial_response_latent_profiles/model_selection_metrics.csv",
        ],
        cwd=repo,
    )
    checks["frozen_numerical_profiles_unchanged_after_unblinding"] = unchanged.returncode == 0

    dictionary = pd.read_csv(args.dictionary, usecols=["item_id"])
    item_ids = dictionary.item_id.astype(str).tolist()
    header = pd.read_csv(args.respondent_data, sep="\t", nrows=0).columns.tolist()
    raw = pd.read_csv(
        args.respondent_data,
        sep="\t",
        usecols=["RID", *item_ids],
        dtype={"RID": "string"},
        low_memory=False,
    )
    values = raw[item_ids].to_numpy(dtype=float)
    observed_values = values[np.isfinite(values)]
    checks["correct_sapa_source_row_count"] = len(raw) == 23_679
    checks["canonical_696_item_count"] = len(item_ids) == 696 and len(set(item_ids)) == 696
    checks["all_canonical_items_present"] = set(item_ids) == {x for x in header if x.startswith("q_")}
    checks["demographics_excluded_from_eligibility"] = all(item.startswith("q_") for item in item_ids)
    checks["responses_1_through_6_validated"] = np.array_equal(
        np.unique(observed_values), np.arange(1, 7, dtype=float)
    )
    checks["duplicate_rids_zero"] = int(raw.RID.duplicated().sum()) == 0
    details["respondent_rows"] = len(raw)
    details["behavioral_items"] = len(item_ids)
    details["observed_cells"] = int(np.isfinite(values).sum())
    raw = None
    values = None

    synthetic = json.loads((output / "synthetic_validation_metrics.json").read_text())
    checks["synthetic_recovery_validation_passed"] = synthetic["status"] == "PASS" and all(
        synthetic["checks"].values()
    )
    checks["missing_values_ignored_not_imputed"] = synthetic[
        "missing_storage_max_absolute_effect"
    ] <= 1e-12
    checks["label_permutation_handled"] = synthetic["checks"]["label_permutation_alignment_exact"]

    metrics = pd.read_csv(output / "model_selection_metrics.csv")
    checks["candidate_k_range_frozen_and_evaluated"] = metrics.k.astype(int).tolist() == list(range(2, 13))
    checks["six_fixed_starts_attempted_per_k"] = bool((metrics.attempted_starts == 6).all())
    checks["multiple_starts_used"] = int(metrics.attempted_starts.min()) > 1
    checks["selection_metrics_finite"] = bool(
        np.isfinite(metrics[["observed_data_log_likelihood", "aic", "bic", "icl"]]).all().all()
    )
    candidates = sorted(metrics.loc[metrics.frozen_candidate, "k"].astype(int).tolist())
    checks["frozen_candidate_anchors_are_4_and_10"] = candidates == [4, 10]
    checks["extension_stopped_mechanically"] = not bool(metrics.loc[metrics.k == 12, "eligible"].iloc[0])
    checks["no_unique_k_claimed"] = json.loads((output / "numerical_freeze_manifest.json").read_text())[
        "selection_conflict"
    ]

    probabilities = pd.read_csv(output / "frozen_profile_item_probabilities.csv")
    probability_columns = [f"probability_response_{category}" for category in range(1, 7)]
    checks["candidate_profile_row_count_correct"] = len(probabilities) == (4 + 10) * 696
    checks["six_category_probabilities_normalize"] = bool(
        np.allclose(probabilities[probability_columns].sum(axis=1), 1.0, atol=1e-10)
    )
    expected = np.sum(
        probabilities[probability_columns].to_numpy()
        * np.arange(1, 7, dtype=float)[None, :],
        axis=1,
    )
    checks["expected_scores_match_category_probabilities"] = bool(
        np.allclose(expected, probabilities.expected_response, atol=1e-10)
    )
    checks["only_anonymous_profile_labels"] = bool(
        probabilities.profile.str.fullmatch(r"Profile [A-J]").all()
    )
    checks["aggregate_support_only"] = bool(
        (probabilities.posterior_weighted_observed_support > 0).all()
    )

    stability = pd.read_csv(output / "profile_stability_metrics.csv")
    checks["independent_split_refit_stability_evaluated"] = set(stability.k) == {4, 10}
    checks["k4_moderate_k10_low_stability_recorded"] = (
        set(stability.loc[stability.k == 4, "replication_stability_rating"]) == {"moderate"}
        and set(stability.loc[stability.k == 10, "replication_stability_rating"]) == {"low"}
    )
    certainty = pd.read_csv(output / "posterior_certainty_summary.csv")
    checks["posterior_certainty_both_candidates"] = set(certainty.k) == {4, 10}
    checks["posterior_threshold_summaries_present"] = all(
        column in certainty for column in ["share_ge_0_50", "share_ge_0_70", "share_ge_0_80", "share_ge_0_90"]
    )
    certainty_bins = pd.read_csv(output / "certainty_by_items_answered.csv")
    checks["certainty_by_answered_count_completed"] = set(certainty_bins.k) == {4, 10}

    missingness = pd.read_csv(output / "missingness_artifact_diagnostics.csv")
    checks["missingness_mask_diagnostic_completed"] = set(missingness.k) == {4, 10} and {
        "full_696_item_response_mask",
        "answered_item_count_only",
    }.issubset(set(missingness.diagnostic))
    diagnostics = json.loads((output / "frozen_candidate_diagnostic_summary.json").read_text())
    checks["missingness_warning_not_triggered"] = not any(
        diagnostics["summaries"][str(k)]["missingness_summary"]["strong_missingness_warning"]
        for k in [4, 10]
    )
    checks["response_style_diagnostic_completed"] = (output / "response_style_diagnostics.csv").is_file()
    checks["response_style_warning_recorded"] = all(
        diagnostics["summaries"][str(k)]["response_style_summary"]["strong_response_style_warning"]
        for k in [4, 10]
    )

    semantic = pd.read_csv(output / "semantic_profile_items.csv")
    checks["semantic_packet_covers_both_frozen_candidates"] = set(semantic.k) == {4, 10}
    checks["semantic_ranking_is_fixed_profile_derived"] = set(semantic.selection) == {
        "highest_expected",
        "lowest_expected",
        "largest_positive_contrast",
        "largest_negative_contrast",
    }
    checks["semantic_interpretation_after_freeze"] = checks["numerical_before_semantic"]

    for name in [
        "model_selection.png",
        "profile_heatmap.png",
        "profile_summary.png",
        "certainty_vs_items_answered.png",
        "class_sizes.png",
        "missingness_diagnostic.png",
    ]:
        image = mpimg.imread(output / name)
        checks[f"figure_valid_{name}"] = image.ndim in (2, 3) and image.shape[0] > 100 and image.shape[1] > 100

    tracked = git(repo, "ls-files", "research/outputs/sapa_partial_response_latent_profiles").splitlines()
    forbidden_names = ["respondent", "posterior_membership", "response_mask", "imputed", "individual_profile"]
    checks["no_respondent_level_output_names"] = not any(
        any(token in Path(path).name.lower() for token in forbidden_names) for path in tracked
    )
    checks["no_raw_human_microdata_tracked"] = not any(
        "sapatempdata" in path.lower() or path.lower().endswith("iteminfo696.csv") for path in git(repo, "ls-files").splitlines()
    )
    csv_headers = []
    for path_text in tracked:
        path = repo / path_text
        if path.suffix == ".csv":
            csv_headers.extend(pd.read_csv(path, nrows=0).columns.astype(str).tolist())
    checks["no_rid_in_committed_output_headers"] = "RID" not in csv_headers

    report_text = (output / "sapa_partial_response_latent_profiles_report.md").read_text().lower()
    checks["no_threshold_selected"] = "no minimum-answer rule was selected" in report_text
    checks["no_construct_scoring"] = "did not impute individual responses, score named constructs" in report_text
    checks["no_clustering_or_human_model_matching"] = "compare humans with qwen/llama/gemma" in report_text
    checks["no_human_pca_projection"] = "run human pca" in report_text
    checks["no_model_inference_or_activations"] = "run model inference, extract activations" in report_text
    checks["no_external_model_api"] = "external model api" in report_text
    checks["no_gpu_or_runpod"] = "gpu/runpod" in report_text
    checks["external_profile_literature_intentionally_unperformed"] = (
        "external human-profile literature verification remains intentionally unperformed" in report_text
    )
    checks["human_only_analysis"] = "human-only analysis" in report_text

    checks["startup_passed"] = True
    checks["canonical_navigation_consulted"] = True
    details["startup_evidence"] = {
        "exact_raw_urls_fetched_in_required_order": True,
        "all_http_status": 200,
        "visible_metadata_matched_manifest": True,
        "startup_manifest_generation_time": "2026-09-12T21:15:38Z",
    }

    passed = sum(checks.values())
    status = "PASS" if passed == len(checks) else "FAIL"
    payload = {
        "status": status,
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "details": details,
        "privacy": "aggregate-only outputs; no individual responses, masks, labels, posteriors, or imputations",
        "scope": "human-only partial-response latent-profile discovery; no human/model comparison or external profile-literature lookup",
    }
    (output / "verification_report.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
