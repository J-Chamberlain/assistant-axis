#!/usr/bin/env python3
"""Post-freeze semantic browsing packets and aggregate visualizations."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

for variable in (
    "VECLIB_MAXIMUM_THREADS",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[variable] = "1"

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata


MODELS = {
    "qwen": {"label": "Qwen 3 32B", "directory": "qwen-3-32b"},
    "llama": {"label": "LLaMA 3.3 70B", "directory": "llama-3.3-70b"},
    "gemma": {"label": "Gemma 2 27B", "directory": "gemma-2-27b"},
}


def item_phrase(text: str, limit: int = 72) -> str:
    clean = " ".join(str(text).split())
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


def human_semantics(root: Path, dictionary_path: Path) -> tuple[pd.DataFrame, list[str]]:
    profiles = pd.read_csv(root / "human/human_cross_resolution_profiles.csv")
    sizes = pd.read_csv(root / "human/human_class_sizes.csv")
    dictionary = pd.read_csv(dictionary_path, usecols=["item_id", "item_text"])
    text_map = dictionary.set_index("item_id")["item_text"].to_dict()
    rows = []
    markdown = [
        "# Human cross-resolution semantic browsing packet",
        "",
        "Status: post-freeze description of numerical bank commit `d0c902b`; descriptions did not alter K, eligibility, probabilities, or membership.",
        "",
        "Scores are six-category expected responses. ‘Elevated’ and ‘depressed’ are relative to the class-proportion-weighted grand profile at the same K; ‘differentiating’ is relative to the mean of the other profiles. These are item-level descriptions, not named constructs or personality types.",
        "",
    ]
    for k in range(4, 11):
        subset = profiles[profiles.K == k].copy()
        pivot = subset.pivot(index="profile_id", columns="item_id", values="expected_response")
        proportions = sizes[sizes.K == k].set_index("profile_id")["prior_proportion"].reindex(pivot.index)
        grand = np.average(pivot.to_numpy(), axis=0, weights=proportions.to_numpy())
        markdown.extend([f"## K={k}", ""])
        for profile_position, profile in enumerate(pivot.index):
            values = pivot.loc[profile].to_numpy()
            others = pivot.drop(index=profile).mean(axis=0).to_numpy()
            criteria = {
                "highest_expected": np.argsort(-values, kind="stable")[:8],
                "lowest_expected": np.argsort(values, kind="stable")[:8],
                "most_elevated_vs_grand": np.argsort(-(values - grand), kind="stable")[:8],
                "most_depressed_vs_grand": np.argsort(values - grand, kind="stable")[:8],
                "most_differentiating_vs_other_profiles": np.argsort(
                    -np.abs(values - others), kind="stable"
                )[:10],
            }
            for selection, indices in criteria.items():
                reference = others if "other_profiles" in selection else grand
                for rank, item_index in enumerate(indices, start=1):
                    item_id = pivot.columns[item_index]
                    rows.append(
                        {
                            "K": k,
                            "profile_id": profile,
                            "selection": selection,
                            "rank": rank,
                            "item_id": item_id,
                            "item_text": text_map[item_id],
                            "expected_response": values[item_index],
                            "reference_expected_response": reference[item_index],
                            "difference": values[item_index] - reference[item_index],
                        }
                    )
            profile_size = sizes[(sizes.K == k) & (sizes.profile_id == profile)].iloc[0]
            elevated = [item_phrase(text_map[pivot.columns[i]]) for i in criteria["most_elevated_vs_grand"][:3]]
            depressed = [item_phrase(text_map[pivot.columns[i]]) for i in criteria["most_depressed_vs_grand"][:3]]
            differentiating = [
                item_phrase(text_map[pivot.columns[i]])
                for i in criteria["most_differentiating_vs_other_profiles"][:3]
            ]
            markdown.extend(
                [
                    f"### {profile}",
                    "",
                    f"Discovery MAP size: {int(profile_size.map_discovery_n):,} ({profile_size.map_discovery_proportion:.1%}); prior proportion {profile_size.prior_proportion:.3f}.",
                    "",
                    "Descriptively, its strongest relative elevations are “" + "”; “".join(elevated) + "”. Its strongest relative depressions are “" + "”; “".join(depressed) + "”. The largest same-K contrasts include “" + "”; “".join(differentiating) + "”.",
                    "",
                ]
            )
    semantic = pd.DataFrame(rows)
    semantic.to_csv(root / "human/human_semantic_items.csv", index=False)
    (root / "human/human_semantic_browsing.md").write_text("\n".join(markdown), encoding="utf-8")
    return profiles, [text_map[item] for item in dictionary.item_id]


def plot_human(root: Path, profiles: pd.DataFrame) -> None:
    figure_dir = root / "human/figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    matrix = profiles.pivot(index="profile_id", columns="item_id", values="expected_response")
    item_range = matrix.max(axis=0) - matrix.min(axis=0)
    global_items = sorted(item_range.index, key=lambda item: (-item_range[item], item))[:60]
    for k in range(4, 11):
        subset = matrix.loc[[index for index in matrix.index if index.startswith(f"H{k:02d}_")]]
        local_range = subset.max(axis=0) - subset.min(axis=0)
        local_items = sorted(local_range.index, key=lambda item: (-local_range[item], item))[:20]
        sizes = pd.read_csv(root / "human/human_class_sizes.csv")
        sizes = sizes[sizes.K == k].set_index("profile_id").reindex(subset.index)
        fig, axes = plt.subplots(3, 1, figsize=(15, 10), gridspec_kw={"height_ratios": [2.2, 1.0, 1.8]})
        image = axes[0].imshow(subset[global_items], aspect="auto", vmin=1, vmax=6, cmap="viridis")
        axes[0].set_yticks(range(len(subset)), subset.index)
        axes[0].set_xticks(range(len(global_items)), global_items, rotation=90, fontsize=6)
        axes[0].set_title(f"Human K={k}: fixed global top-60 differentiating items")
        fig.colorbar(image, ax=axes[0], label="Expected response")
        axes[1].bar(subset.index, sizes.map_discovery_n, color="#4c78a8")
        axes[1].set_ylabel("Discovery MAP n")
        axes[1].set_title("Profile sizes")
        local_image = axes[2].imshow(subset[local_items], aspect="auto", vmin=1, vmax=6, cmap="viridis")
        axes[2].set_yticks(range(len(subset)), subset.index)
        axes[2].set_xticks(range(len(local_items)), local_items, rotation=90, fontsize=7)
        axes[2].set_title("K-specific top-20 differentiating items")
        fig.colorbar(local_image, ax=axes[2], label="Expected response")
        fig.tight_layout()
        fig.savefig(figure_dir / f"human_k{k:02d}_overview.png", dpi=170)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(18, 13))
    image = ax.imshow(matrix[global_items], aspect="auto", vmin=1, vmax=6, cmap="viridis")
    ax.set_yticks(range(len(matrix)), matrix.index, fontsize=7)
    ax.set_xticks(range(len(global_items)), global_items, rotation=90, fontsize=6)
    ax.set_title("Human K=4–10 anonymous profiles on one fixed item ordering")
    ax.set_xlabel("Items selected by global response-derived range; no semantic selection")
    fig.colorbar(image, ax=ax, label="Expected response")
    fig.tight_layout()
    fig.savefig(figure_dir / "human_cross_k_overview.png", dpi=180)
    plt.close(fig)


def model_semantics(root: Path, vector_root: Path, trait_paths: dict[str, Path]) -> pd.DataFrame:
    all_traits = []
    for model, spec in MODELS.items():
        model_dir = root / "model" / model
        names = [path.stem for path in sorted((vector_root / spec["directory"] / "role_vectors").glob("*.pt"))]
        role_map = {f"R{index + 1:03d}": name for index, name in enumerate(names)}
        membership = pd.read_csv(model_dir / "memberships.csv")
        membership["role"] = membership.opaque_role_id.map(role_map)
        if membership.role.isna().any():
            raise RuntimeError(f"opaque role join failed for {model}")
        membership.to_csv(model_dir / "memberships_with_role_names.csv", index=False)

        traits = pd.read_csv(trait_paths[model])
        traits = traits.set_index("persona").reindex(names)
        if traits.isna().any().any() or list(traits.index) != names or traits.shape != (275, 240):
            raise RuntimeError(f"trait matrix integrity failure for {model}: {traits.shape}")
        values = traits.to_numpy(dtype=np.float64)
        global_mean = values.mean(axis=0)
        global_sd = values.std(axis=0)
        percentiles = np.column_stack(
            [100.0 * (rankdata(values[:, index], method="average") - 0.5) / len(values) for index in range(values.shape[1])]
        )
        trait_rows = []
        markdown = [
            f"# {spec['label']} cross-resolution role browsing",
            "",
            "Status: post-freeze description of numerical bank commit `d0c902b`; role names and trait labels did not alter membership, K, centroids, or stability metrics.",
            "",
            "Trait summaries are same-model activation-cosine descriptions of activation-derived role clusters. They are not population prevalence estimates or independent psychological measurements.",
            "",
        ]
        for k in range(4, 11):
            markdown.extend([f"## K={k}", ""])
            subset = membership[membership.K == k]
            for profile in sorted(subset.profile_id.unique()):
                members = subset[subset.profile_id == profile].sort_values("within_profile_centroid_rank")
                member_indices = [int(role_id[1:]) - 1 for role_id in members.opaque_role_id]
                cluster_values = values[member_indices]
                cluster_percentiles = percentiles[member_indices]
                means = cluster_values.mean(axis=0)
                medians = np.median(cluster_values, axis=0)
                zscores = (means - global_mean) / np.where(global_sd > 0, global_sd, 1.0)
                mean_percentiles = cluster_percentiles.mean(axis=0)
                for trait_index, trait in enumerate(traits.columns):
                    trait_rows.append(
                        {
                            "model": model,
                            "K": k,
                            "profile_id": profile,
                            "trait": trait,
                            "mean_trait_score": means[trait_index],
                            "median_trait_score": medians[trait_index],
                            "within_model_standardized_score": zscores[trait_index],
                            "within_model_mean_percentile": mean_percentiles[trait_index],
                        }
                    )
                high = np.argsort(-zscores, kind="stable")[:8]
                low = np.argsort(zscores, kind="stable")[:8]
                nearest = members.head(10).role.tolist()
                furthest = members.tail(5).sort_values("within_profile_centroid_rank", ascending=False).role.tolist()
                markdown.extend(
                    [
                        f"### {profile} — {len(members)} roles",
                        "",
                        "Brief description: the frozen activation-derived cluster is centered on roles such as " + ", ".join(nearest[:5]) + ". Its relatively elevated trait affinities are " + ", ".join(traits.columns[high[:5]]) + "; relatively depressed affinities are " + ", ".join(traits.columns[low[:5]]) + ".",
                        "",
                        "Nearest roles: " + ", ".join(nearest) + ".",
                        "",
                        "Furthest within-cluster roles: " + ", ".join(furthest) + ".",
                        "",
                        "Top elevated traits: " + ", ".join(f"{traits.columns[i]} ({zscores[i]:+.2f} SD)" for i in high) + ".",
                        "",
                        "Top depressed traits: " + ", ".join(f"{traits.columns[i]} ({zscores[i]:+.2f} SD)" for i in low) + ".",
                        "",
                        "All members: " + ", ".join(sorted(members.role.tolist())) + ".",
                        "",
                    ]
                )
        trait_frame = pd.DataFrame(trait_rows)
        trait_frame.to_csv(model_dir / "trait_profiles.csv", index=False)
        all_traits.append(trait_frame)
        (model_dir / "semantic_browsing.md").write_text("\n".join(markdown), encoding="utf-8")
        plot_model(root, model, membership, trait_frame)
    combined = pd.concat(all_traits, ignore_index=True)
    combined.to_csv(root / "model/model_cross_resolution_trait_profiles.csv", index=False)
    return combined


def plot_model(root: Path, model: str, membership: pd.DataFrame, traits: pd.DataFrame) -> None:
    model_dir = root / "model" / model
    summary = pd.read_csv(model_dir / "solution_summary.csv")
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    for k in range(4, 11):
        counts = membership[membership.K == k].groupby("profile_id").size()
        axes[0].plot([k] * len(counts), counts.values, "o", alpha=0.8)
    axes[0].plot(summary.K, summary.minimum_cluster_size, "k--", label="minimum")
    axes[0].plot(summary.K, summary.maximum_cluster_size, "k-", label="maximum")
    axes[0].set_ylabel("Roles per profile")
    axes[0].set_title(f"{MODELS[model]['label']}: cluster sizes across resolution")
    axes[0].legend()
    axes[1].plot(summary.K, summary.start_ari_median, "o-", label="start median ARI")
    axes[1].plot(summary.K, summary.subsample_ari_median, "s-", label="80% refit median ARI")
    axes[1].axhline(0.75, color="gray", linestyle="--", linewidth=1)
    axes[1].axhline(0.90, color="gray", linestyle=":", linewidth=1)
    axes[1].set_ylim(0, 1)
    axes[1].set_xlabel("K")
    axes[1].set_ylabel("ARI to retained solution")
    axes[1].set_title("Permutation-invariant stability")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(model_dir / "cluster_sizes_and_stability.png", dpi=180)
    plt.close(fig)

    pivot = traits.pivot(index="profile_id", columns="trait", values="within_model_standardized_score")
    trait_range = pivot.max(axis=0) - pivot.min(axis=0)
    selected = sorted(trait_range.index, key=lambda trait: (-trait_range[trait], trait))[:50]
    fig, ax = plt.subplots(figsize=(17, 13))
    image = ax.imshow(pivot[selected], aspect="auto", cmap="coolwarm", vmin=-1.8, vmax=1.8)
    ax.set_yticks(range(len(pivot)), pivot.index, fontsize=7)
    ax.set_xticks(range(len(selected)), selected, rotation=90, fontsize=6)
    ax.set_title(f"{MODELS[model]['label']} K=4–10 trait summaries (fixed data-derived ordering)")
    ax.set_xlabel("50 traits with largest across-bank standardized range")
    fig.colorbar(image, ax=ax, label="Within-model standardized cluster mean")
    fig.tight_layout()
    fig.savefig(model_dir / "trait_profile_heatmap.png", dpi=180)
    plt.close(fig)

    continuity = pd.read_csv(model_dir / "adjacent_k_continuity.csv")
    pair_metrics = continuity.groupby(["lower_K", "higher_K"], as_index=False)[
        ["adjacent_partition_ari", "adjacent_partition_nmi"]
    ].first()
    fig, axes = plt.subplots(2, 1, figsize=(13, 9))
    size_table = membership.groupby(["K", "profile_id"]).size().unstack(fill_value=0)
    axes[0].imshow(size_table.to_numpy().T, aspect="auto", cmap="Blues")
    axes[0].set_xticks(range(len(size_table.index)), size_table.index)
    axes[0].set_yticks(range(len(size_table.columns)), size_table.columns, fontsize=7)
    axes[0].set_title("K-specific membership sizes (profiles are anonymous; no lineage implied)")
    axes[1].plot(pair_metrics.lower_K, pair_metrics.adjacent_partition_ari, "o-", label="ARI")
    axes[1].plot(pair_metrics.lower_K, pair_metrics.adjacent_partition_nmi, "s-", label="NMI")
    axes[1].set_xticks(pair_metrics.lower_K, [f"{k}→{k+1}" for k in pair_metrics.lower_K])
    axes[1].set_ylim(0, 1)
    axes[1].set_ylabel("Partition continuity")
    axes[1].set_title("Adjacent-K role-membership continuity")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(model_dir / "partition_overview.png", dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dictionary", type=Path, required=True)
    parser.add_argument("--vector-root", type=Path, required=True)
    parser.add_argument("--qwen-traits", type=Path, required=True)
    parser.add_argument("--llama-traits", type=Path, required=True)
    parser.add_argument("--gemma-traits", type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    profiles, _ = human_semantics(root, args.dictionary.resolve())
    plot_human(root, profiles)
    model_semantics(
        root,
        args.vector_root.resolve(),
        {
            "qwen": args.qwen_traits.resolve(),
            "llama": args.llama_traits.resolve(),
            "gemma": args.gemma_traits.resolve(),
        },
    )


if __name__ == "__main__":
    main()
