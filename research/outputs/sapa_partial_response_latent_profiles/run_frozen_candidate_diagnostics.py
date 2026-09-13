#!/usr/bin/env python3
"""Compute required aggregate diagnostics for every frozen candidate K.

The script reconstructs immutable class probabilities from committed aggregate
files. It cannot fit or modify a latent model and reads only item IDs from the
dictionary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from latent_class_model import LCASolution, build_sparse_responses, profile_labels
from run_sapa_numerical_analysis import (
    administration_diagnostics,
    deterministic_split,
    json_write,
    load_and_validate,
    posterior_certainty_tables,
    response_style_diagnostics,
)


def reconstruct_solution(
    k: int,
    probabilities: pd.DataFrame,
    sizes: pd.DataFrame,
    item_ids: list[str],
) -> LCASolution:
    selected = probabilities[probabilities.k == k]
    theta = np.empty((k, len(item_ids), 6), dtype=np.float64)
    for profile_index, profile in enumerate(profile_labels(k)):
        rows = selected[selected.profile == profile].set_index("item_id").loc[item_ids]
        theta[profile_index] = rows[
            [f"probability_response_{category}" for category in range(1, 7)]
        ].to_numpy(dtype=np.float64)
    class_rows = sizes[sizes.k == k].set_index("profile").loc[profile_labels(k)]
    pi = class_rows["prior_proportion"].to_numpy(dtype=np.float64)
    pi /= pi.sum()
    return LCASolution(
        k=k,
        seed=-1,
        pi=pi,
        theta=theta,
        log_likelihood=float("nan"),
        iterations=0,
        converged=True,
        monotone=True,
        history=np.array([], dtype=float),
        responsibilities=np.empty((0, k), dtype=float),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--respondent-data", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()

    responses, mask, item_ids, integrity = load_and_validate(
        args.respondent_data.resolve(), args.dictionary.resolve()
    )
    answered = mask.sum(axis=1).astype(np.int32)
    splits = deterministic_split(answered)
    all_data = build_sparse_responses(responses, observed_mask=mask)
    probabilities = pd.read_csv(output / "frozen_profile_item_probabilities.csv")
    sizes = pd.read_csv(output / "frozen_class_sizes.csv")
    candidate_k = sorted(probabilities.k.unique().astype(int).tolist())

    certainty_tables = []
    certainty_bin_tables = []
    missing_classifier_tables = []
    item_frequency_tables = []
    items_answered_tables = []
    response_style_tables = []
    response_classifier_tables = []
    summaries: dict[str, object] = {}
    for k in candidate_k:
        solution = reconstruct_solution(k, probabilities, sizes, item_ids)
        certainty, bins, relationship, posterior = posterior_certainty_tables(
            all_data, solution, splits
        )
        certainty.insert(0, "k", k)
        bins.insert(0, "k", k)
        certainty_tables.append(certainty)
        certainty_bin_tables.append(bins)

        mask_classifier, item_frequency, item_counts, missingness_summary = administration_diagnostics(
            mask, answered, posterior, splits, item_ids
        )
        for table in [mask_classifier, item_frequency, item_counts]:
            table.insert(0, "k", k)
        missing_classifier_tables.append(mask_classifier)
        item_frequency_tables.append(item_frequency)
        items_answered_tables.append(item_counts)

        response_style, response_classifier, response_summary = response_style_diagnostics(
            responses, mask, posterior, solution, splits
        )
        response_style.insert(0, "k", k)
        response_classifier.insert(0, "k", k)
        response_style_tables.append(response_style)
        response_classifier_tables.append(response_classifier)
        summaries[str(k)] = {
            "certainty_relationship": relationship,
            "missingness_summary": missingness_summary,
            "response_style_summary": response_summary,
        }

    certainty_all = pd.concat(certainty_tables, ignore_index=True)
    bins_all = pd.concat(certainty_bin_tables, ignore_index=True)
    mask_all = pd.concat(missing_classifier_tables, ignore_index=True)
    item_frequency_all = pd.concat(item_frequency_tables, ignore_index=True)
    items_answered_all = pd.concat(items_answered_tables, ignore_index=True)
    response_style_all = pd.concat(response_style_tables, ignore_index=True)
    response_classifier_all = pd.concat(response_classifier_tables, ignore_index=True)
    certainty_all.to_csv(output / "posterior_certainty_summary.csv", index=False)
    bins_all.to_csv(output / "certainty_by_items_answered.csv", index=False)
    mask_all.to_csv(output / "missingness_artifact_diagnostics.csv", index=False)
    item_frequency_all.to_csv(output / "missingness_item_frequency_by_profile.csv", index=False)
    items_answered_all.to_csv(output / "items_answered_by_profile.csv", index=False)
    response_style_all.to_csv(output / "response_style_diagnostics.csv", index=False)
    response_classifier_all.to_csv(output / "response_style_classifier_metrics.csv", index=False)

    manifest = {
        "status": "PASS",
        "stage": "post-numerical-freeze aggregate diagnostic completion",
        "candidate_k": candidate_k,
        "source": "committed frozen_profile_item_probabilities.csv and frozen_class_sizes.csv",
        "latent_model_refit": False,
        "selection_changed": False,
        "respondent_level_outputs_written": False,
        "summaries": summaries,
        "data_integrity_recheck": {
            "respondent_rows": integrity["respondent_rows"],
            "behavioral_items_present": integrity["behavioral_items_present"],
            "observed_response_codes": integrity["observed_response_codes"],
        },
    }
    json_write(output / "frozen_candidate_diagnostic_summary.json", manifest)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(9, 5))
    for k, group in bins_all.groupby("k"):
        ax.plot(
            group.mean_items_answered,
            group.mean_max_posterior,
            marker="o",
            label=f"K={k} mean max posterior",
        )
    ax.set_xlabel("Mean items answered within deterministic count bin")
    ax.set_ylabel("Posterior assignment certainty")
    ax.set_ylim(0, 1.02)
    ax.legend()
    ax.set_title("Assignment certainty for both frozen candidate anchors")
    fig.tight_layout()
    fig.savefig(output / "certainty_vs_items_answered.png", dpi=180)
    plt.close(fig)

    plot = mask_all[mask_all.diagnostic == "full_696_item_response_mask"].copy()
    fig, ax = plt.subplots(figsize=(9, 5))
    positions = np.arange(len(plot))
    ax.bar(
        positions,
        plot.balanced_accuracy,
        color=["#4C78A8" if int(k) == 4 else "#F58518" for k in plot.k],
    )
    ax.plot(positions, plot.balanced_accuracy_chance, "k--", label="Chance for each K")
    ax.set_xticks(
        positions,
        [f"K={row.k} {row.subset}" for _, row in plot.iterrows()],
        rotation=20,
        ha="right",
    )
    ax.set_ylim(0, 1)
    ax.set_ylabel("Balanced accuracy")
    ax.set_title("Administration-mask prediction for both frozen candidate anchors")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "missingness_diagnostic.png", dpi=180)
    plt.close(fig)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
