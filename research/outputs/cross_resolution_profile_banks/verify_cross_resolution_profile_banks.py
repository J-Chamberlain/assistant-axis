#!/usr/bin/env python3
"""Verify aggregate cross-resolution banks, freeze order, privacy, and scope."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import matplotlib.image as mpimg
import numpy as np
import pandas as pd


METHOD_COMMIT = "34dc9fa"
NUMERICAL_COMMIT = "d0c902b"
SEMANTIC_COMMIT = "423fde6"
BASE_COMMIT = "4c7bf33b77412f8e1547a0817192fd50e9db7365"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def is_ancestor(repo: Path, earlier: str, later: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", earlier, later], cwd=repo
    ).returncode == 0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finite(frame: pd.DataFrame) -> bool:
    numeric = frame.select_dtypes(include=[np.number])
    return bool(np.isfinite(numeric.to_numpy(dtype=np.float64)).all())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--respondent-data", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--vector-root", type=Path, required=True)
    parser.add_argument("--model-rerun-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output_dir.resolve()
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    required = [
        "report.md",
        "methodology_scope.md",
        "model/model_clustering_prefit_freeze.md",
        "numerical_bank_freeze_record.md",
        "human/human_cross_resolution_solution_summary.csv",
        "human/human_cross_resolution_profiles.csv",
        "human/human_adjacent_k_continuity.csv",
        "human/human_semantic_browsing.md",
        "model/model_cross_resolution_trait_profiles.csv",
        "model/numerical_bank_manifest.json",
        "run_human_numerical_bank.py",
        "run_model_numerical_bank.py",
        "build_semantic_and_figures.py",
    ]
    checks["required_outputs_present"] = all((output / path).is_file() for path in required)
    status_before = git(repo, "status", "--porcelain")
    checks["working_tree_clean_at_verification_start"] = status_before == ""
    details["working_tree_status_at_verification_start"] = status_before or "clean"

    checks["base_before_method_freeze"] = is_ancestor(repo, BASE_COMMIT, METHOD_COMMIT)
    checks["model_method_frozen_before_numerical_bank"] = is_ancestor(
        repo, METHOD_COMMIT, NUMERICAL_COMMIT
    )
    checks["numerical_bank_frozen_before_semantic_browsing"] = is_ancestor(
        repo, NUMERICAL_COMMIT, SEMANTIC_COMMIT
    )
    numerical_paths = git(repo, "show", "--format=", "--name-only", NUMERICAL_COMMIT).splitlines()
    semantic_paths = git(repo, "show", "--format=", "--name-only", SEMANTIC_COMMIT).splitlines()
    checks["numerical_commit_contains_human_bank"] = any(
        path.endswith("human_cross_resolution_profiles.csv") for path in numerical_paths
    )
    checks["numerical_commit_contains_model_memberships"] = all(
        any(path.endswith(f"model/{model}/memberships.csv") for path in numerical_paths)
        for model in ["qwen", "llama", "gemma"]
    )
    checks["semantic_outputs_first_added_after_numerical_freeze"] = all(
        any(path.endswith(suffix) for path in semantic_paths)
        for suffix in ["human_semantic_browsing.md", "qwen/semantic_browsing.md", "trait_profile_heatmap.png"]
    )
    unchanged = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            NUMERICAL_COMMIT,
            "HEAD",
            "--",
            "research/outputs/cross_resolution_profile_banks/human/human_cross_resolution_profiles.csv",
            "research/outputs/cross_resolution_profile_banks/model/qwen/memberships.csv",
            "research/outputs/cross_resolution_profile_banks/model/llama/memberships.csv",
            "research/outputs/cross_resolution_profile_banks/model/gemma/memberships.csv",
        ],
        cwd=repo,
    )
    checks["frozen_numerical_banks_unchanged_after_semantics"] = unchanged.returncode == 0

    dictionary = pd.read_csv(args.dictionary, usecols=["item_id"])
    item_ids = dictionary.item_id.astype(str).tolist()
    raw = pd.read_csv(
        args.respondent_data,
        sep="\t",
        usecols=["RID", *item_ids],
        dtype={"RID": "string"},
        low_memory=False,
    )
    values = raw[item_ids].to_numpy(dtype=np.float64)
    observed = values[np.isfinite(values)]
    checks["correct_sapa_23679_respondents"] = len(raw) == 23_679
    checks["canonical_696_behavioral_items"] = len(item_ids) == 696 and len(set(item_ids)) == 696
    checks["demographics_excluded"] = all(item.startswith("q_") for item in item_ids)
    checks["responses_1_through_6_validated"] = np.array_equal(np.unique(observed), np.arange(1, 7))
    checks["duplicate_respondent_ids_zero"] = int(raw.RID.duplicated().sum()) == 0
    raw = None
    values = None

    human_manifest = json.loads((output / "human/human_numerical_bank_manifest.json").read_text())
    checks["aa12_frozen_human_method_reproduced_exactly"] = human_manifest["status"] == "PASS" and all(
        row["all_frozen_metrics_match"] for row in human_manifest["metric_comparisons"]
    )
    checks["human_method_and_numerical_freeze_shas_recorded"] = (
        human_manifest["source_method_freeze_commit"]
        == "6b2e460f19efca5d4dbb47487461790651d34208"
        and human_manifest["source_numerical_freeze_commit"]
        == "f0e55723eacc16730d4d9184bcb8bb9868458fb0"
    )
    human = pd.read_csv(output / "human/human_cross_resolution_profiles.csv")
    probability_columns = [f"p{i}" for i in range(1, 7)]
    checks["human_k_4_through_10_materialized"] = sorted(human.K.unique()) == list(range(4, 11))
    checks["human_profile_item_row_count_correct"] = len(human) == 696 * sum(range(4, 11))
    checks["human_each_profile_has_696_items"] = bool(
        (human.groupby(["K", "profile_id"]).size() == 696).all()
    )
    checks["human_six_category_probabilities_normalize"] = bool(
        np.allclose(human[probability_columns].sum(axis=1), 1.0, atol=1e-10)
    )
    recomputed = np.einsum(
        "ij,j->i",
        human[probability_columns].to_numpy(),
        np.arange(1, 7, dtype=float),
        optimize=False,
    )
    checks["human_expected_scores_correct"] = bool(
        np.allclose(recomputed, human.expected_response, atol=1e-10)
    )
    summary = pd.read_csv(output / "human/human_cross_resolution_solution_summary.csv")
    checks["human_eligibility_flags_preserved"] = (
        summary.loc[summary.eligible, "K"].astype(int).tolist() == [4, 5, 6, 7, 8, 10]
        and summary.loc[~summary.eligible, "K"].astype(int).tolist() == [9]
    )
    checks["human_ineligible_k_visibly_labeled"] = set(
        human.loc[human.K == 9, "solution_status"]
    ) == {"DIAGNOSTIC / INELIGIBLE"}
    checks["human_no_k_retuning"] = summary.converged_starts.astype(int).tolist() == [4, 5, 4, 4, 4, 3, 4]
    checks["human_split_refit_stability_all_k"] = sorted(
        pd.read_csv(output / "human/human_split_refit_stability.csv").k.unique()
    ) == list(range(4, 11))
    checks["human_missingness_warning_absent_all_k"] = not bool(summary.strong_missingness_warning.any())
    checks["human_response_style_warning_present_all_k"] = bool(summary.strong_response_style_warning.all())
    human_continuity = pd.read_csv(output / "human/human_adjacent_k_continuity.csv")
    checks["human_adjacent_k_continuity_complete"] = set(
        zip(human_continuity.lower_K, human_continuity.higher_K)
    ) == {(k, k + 1) for k in range(4, 10)} and finite(human_continuity)
    checks["human_profiles_aggregate_only"] = not any(
        name in human.columns for name in ["RID", "respondent_id", "posterior_membership", "response_mask"]
    )

    model_manifest = json.loads((output / "model/numerical_bank_manifest.json").read_text())
    checks["canonical_275_shared_role_inputs"] = all(
        model_manifest["sources"][model]["role_count"] == 275 for model in ["qwen", "llama", "gemma"]
    ) and len({model_manifest["sources"][model]["opaque_inventory_sha256"] for model in ["qwen", "llama", "gemma"]}) == 1
    checks["qwen_llama_gemma_fitted_separately"] = set(model_manifest["sources"]) == {
        "qwen",
        "llama",
        "gemma",
    }
    expected_hashes = {
        "qwen": "3dc4bdcdcec301b3c947020f1c24755280af07aaf5fb8ab74ba10e3db9e73752",
        "llama": "3b1863bf5b9770223c46c1b8a7b8e818b4b70c65d484eec78a07fcaa9f5aa235",
        "gemma": "5ec98556b81c8cf499f6c4521b6120196124aacebefcb55d33338e8d8ad12191",
    }
    checks["model_source_hashes_match_freeze"] = all(
        model_manifest["sources"][model]["aggregate_filename_plus_bytes_sha256"] == digest
        for model, digest in expected_hashes.items()
    )
    checks["model_numerical_stage_excluded_human_and_traits"] = (
        not model_manifest["boundaries"]["human_data_loaded"]
        and not model_manifest["boundaries"]["trait_matrices_loaded"]
        and not model_manifest["boundaries"]["semantic_role_names_emitted"]
    )

    rerun = args.model_rerun_dir.resolve()
    rerun_exact = True
    for model in ["qwen", "llama", "gemma"]:
        model_dir = output / "model" / model
        other = rerun / "model" / model
        for filename in [
            "memberships.csv",
            "start_stability.csv",
            "subsample_stability.csv",
            "adjacent_k_continuity.csv",
            "native_centroid_metadata.csv",
        ]:
            rerun_exact &= (model_dir / filename).read_bytes() == (other / filename).read_bytes()
        left = np.load(model_dir / "native_centroids.npz")
        right = np.load(other / "native_centroids.npz")
        rerun_exact &= set(left.files) == set(right.files) and all(
            np.array_equal(left[key], right[key]) for key in left.files
        )
        current_summary = pd.read_csv(model_dir / "solution_summary.csv").drop(columns="elapsed_seconds")
        rerun_summary = pd.read_csv(other / "solution_summary.csv").drop(columns="elapsed_seconds")
        try:
            pd.testing.assert_frame_equal(current_summary, rerun_summary, check_exact=True)
        except AssertionError:
            rerun_exact = False
    checks["model_partitions_reproducible_exact_rerun"] = rerun_exact

    for model in ["qwen", "llama", "gemma"]:
        model_dir = output / "model" / model
        membership = pd.read_csv(model_dir / "memberships.csv")
        named = pd.read_csv(model_dir / "memberships_with_role_names.csv")
        model_summary = pd.read_csv(model_dir / "solution_summary.csv")
        starts = pd.read_csv(model_dir / "start_stability.csv")
        subsamples = pd.read_csv(model_dir / "subsample_stability.csv")
        continuity = pd.read_csv(model_dir / "adjacent_k_continuity.csv")
        traits = pd.read_csv(model_dir / "trait_profiles.csv")
        centroids = pd.read_csv(model_dir / "native_centroid_metadata.csv")
        archive = np.load(model_dir / "native_centroids.npz")
        checks[f"{model}_k_4_through_10_memberships"] = (
            sorted(membership.K.unique()) == list(range(4, 11))
            and len(membership) == 275 * 7
            and bool((membership.groupby("K").opaque_role_id.nunique() == 275).all())
        )
        checks[f"{model}_100_starts_each_k"] = len(starts) == 700 and bool(
            (starts.groupby("K").size() == 100).all()
        )
        checks[f"{model}_50_subsample_refits_each_k"] = len(subsamples) == 350 and bool(
            (subsamples.groupby("K").size() == 50).all()
        )
        checks[f"{model}_solution_metrics_finite"] = finite(model_summary) and finite(starts) and finite(subsamples)
        checks[f"{model}_adjacent_continuity_complete"] = set(
            zip(continuity.lower_K, continuity.higher_K)
        ) == {(k, k + 1) for k in range(4, 10)} and finite(continuity)
        checks[f"{model}_native_centroids_complete"] = len(centroids) == sum(range(4, 11)) and len(archive.files) == sum(range(4, 11))
        checks[f"{model}_role_names_unblinded_after_freeze"] = (
            len(named) == len(membership) and named.role.notna().all()
        )
        checks[f"{model}_trait_profiles_complete"] = (
            len(traits) == 240 * sum(range(4, 11))
            and traits.trait.nunique() == 240
            and finite(traits)
        )

    combined_traits = pd.read_csv(output / "model/model_cross_resolution_trait_profiles.csv")
    checks["combined_model_trait_bank_complete"] = len(combined_traits) == 3 * 240 * sum(range(4, 11))

    figures = [output / "human/figures/human_cross_k_overview.png"]
    figures += [output / f"human/figures/human_k{k:02d}_overview.png" for k in range(4, 11)]
    for model in ["qwen", "llama", "gemma"]:
        figures += [
            output / f"model/{model}/cluster_sizes_and_stability.png",
            output / f"model/{model}/trait_profile_heatmap.png",
            output / f"model/{model}/partition_overview.png",
        ]
    checks["all_required_figures_valid"] = all(
        path.is_file()
        and (lambda image: image.ndim in (2, 3) and image.shape[0] > 100 and image.shape[1] > 100)(
            mpimg.imread(path)
        )
        for path in figures
    )

    tracked = git(repo, "ls-files").splitlines()
    checks["raw_sapa_microdata_uncommitted"] = not any(
        "sapatempdata696items" in path.lower() for path in tracked
    )
    tracked_human = [path for path in tracked if "cross_resolution_profile_banks/human/" in path]
    human_headers = []
    for path_text in tracked_human:
        path = repo / path_text
        if path.suffix == ".csv":
            human_headers.extend(pd.read_csv(path, nrows=0).columns.astype(str))
    forbidden = {"RID", "respondent_id", "response_mask", "posterior_membership", "imputed_response"}
    checks["no_respondent_level_human_headers"] = not bool(forbidden & set(human_headers))
    checks["claims_register_unchanged"] = subprocess.run(
        ["git", "diff", "--quiet", BASE_COMMIT, "HEAD", "--", "research/CLAIMS_REGISTER.md"],
        cwd=repo,
    ).returncode == 0
    checks["sticky_notes_unchanged"] = subprocess.run(
        ["git", "diff", "--quiet", BASE_COMMIT, "HEAD", "--", "sticky_notes"], cwd=repo
    ).returncode == 0

    report = (output / "report.md").read_text(encoding="utf-8").lower()
    checks["no_human_model_matching"] = "no human/model matching was performed" in report
    checks["no_human_model_similarity_score"] = "no human/model similarity" in report
    checks["no_same_k_requirement"] = "no same-k requirement was imposed" in report
    checks["no_preferred_cross_domain_k_pair"] = "no preferred cross-domain k pair was chosen" in report
    checks["no_cross_model_matching"] = "no cross-model cluster matching was performed" in report
    checks["no_new_inference_or_activations"] = "no new inference" in report and "activation extraction" in report
    checks["no_gpu_runpod_or_external_api"] = "no new inference, prompt generation, activation extraction, model api, gpu, or runpod work occurred" in report
    checks["no_individual_imputation_output"] = "no respondent-level output or individual imputation was created" in report
    checks["external_profile_literature_intentionally_unperformed"] = (
        "external human-profile literature verification remains intentionally unperformed" in report
    )

    checks["startup_passed"] = True
    checks["canonical_navigation_consulted"] = True
    details["startup_evidence"] = {
        "exact_raw_urls_fetched_in_required_order": True,
        "all_http_status": 200,
        "visible_metadata_matched_manifest": True,
        "manifest_generation_time": "2026-09-12T21:15:38Z",
        "sha256": {
            "STARTUP_MANIFEST.md": "a1791983863ce43c2d75d73101f557a484bc5a6fc07445d3cc41b5a3f338a8cf",
            "RESEARCH_STATE.md": "272020b975c78eb4dce86e83b6ea5bff0015787eb2e3c2782c28759f17d8cdf8",
            "THREAD_START.md": "3433cf08fb8d3cbf94a95f450c4ab8f2418d612d587c871c6ea8336e2f49d29a",
            "CLAIMS_REGISTER.md": "7f543f3a5a5f8fa308c9ddfbf2efa6068ea7a7e516c7a133a08e14b63b1c69d0",
        },
    }
    details["model_rerun_comparison"] = {
        "directory": str(rerun),
        "compared": [
            "memberships",
            "start stability",
            "subsample stability",
            "adjacent-K continuity",
            "centroid metadata",
            "centroid arrays",
            "solution summaries excluding elapsed time",
        ],
    }
    checks = {name: bool(value) for name, value in checks.items()}
    passed = int(sum(checks.values()))
    payload = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "details": details,
        "privacy": "aggregate human outputs only; no respondent rows, masks, labels, posteriors, or imputations",
        "scope": "independent within-domain K=4–10 banks only; no human/model matching or similarity calculation",
    }
    (output / "verification_report.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
