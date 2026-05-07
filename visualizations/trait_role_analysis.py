from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from scipy.spatial.distance import cdist, pdist, squareform

from research_common import (
    DEFAULT_LAYER,
    OUT_DIR,
    ROOT,
    compute_projection_matrix,
    load_axis_tensor,
    load_role_tensor,
    load_roles,
    normalize_name,
    progress,
)


TRAIT_DIR = ROOT / "downloads" / "hf_vectors" / "gemma-2-27b" / "trait_vectors"
ROLE_DIR = ROOT / "downloads" / "hf_vectors" / "gemma-2-27b" / "role_vectors"
TRAIT_LIST_PATH = ROOT / "data" / "traits" / "trait_list.json"
FULL_RANKING_PATH = OUT_DIR / "full_ranking.csv"

ROLE_PEAK_LAYER = 45
PERMUTATIONS = 1000
ANOMALY_ROLES = ["robot", "assistant", "poet", "angel", "saboteur"]
POSITIVE_TRAITS = ["transparent", "grounded", "flexible"]
NEGATIVE_TRAITS = ["enigmatic", "subversive", "dramatic"]


def load_trait_list() -> dict[str, str]:
    return json.loads(TRAIT_LIST_PATH.read_text())


def load_trait_tensor(traits: list[str]) -> torch.Tensor:
    tensors = []
    for idx, trait in enumerate(traits, 1):
        tensor = torch.load(TRAIT_DIR / f"{trait}.pt", map_location="cpu", weights_only=False)
        if isinstance(tensor, dict) and "vector" in tensor:
            tensor = tensor["vector"]
        if not torch.is_tensor(tensor):
            raise TypeError(f"Expected tensor for trait {trait}, got {type(tensor)}")
        tensors.append(tensor.float())
        if idx % 50 == 0 or idx == len(traits):
            progress(f"  loaded {idx}/{len(traits)} trait tensors")
    return torch.stack(tensors)


def validate_inputs() -> tuple[list[str], torch.Tensor, list[str], torch.Tensor, pd.DataFrame]:
    roles = load_roles()
    role_tensor = load_role_tensor(roles)
    traits = sorted(load_trait_list().keys())
    progress(f"Loading {len(traits)} trait tensors from {TRAIT_DIR} ...")
    trait_tensor = load_trait_tensor(traits)

    if tuple(role_tensor.shape[1:]) != tuple(trait_tensor.shape[1:]):
        raise RuntimeError(
            f"Role tensor shape tail {tuple(role_tensor.shape[1:])} does not match "
            f"trait tensor shape tail {tuple(trait_tensor.shape[1:])}"
        )

    ranking_df = pd.read_csv(FULL_RANKING_PATH)
    required_cols = {"character", "cluster_label"}
    if not required_cols.issubset(ranking_df.columns):
        raise RuntimeError(f"{FULL_RANKING_PATH} is missing required columns: {required_cols - set(ranking_df.columns)}")

    cluster_sizes = ranking_df["cluster_label"].value_counts()
    too_small = cluster_sizes[cluster_sizes < 5]
    if not too_small.empty:
        raise RuntimeError(
            "Cluster(s) below size 5 make permutation testing unreliable: "
            + ", ".join(f"{cluster}={count}" for cluster, count in too_small.items())
        )

    return roles, role_tensor, traits, trait_tensor, ranking_df


def build_role_mapping(roles: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for role in roles:
        key = normalize_name(role)
        if key in mapping:
            raise RuntimeError(f"Ambiguous normalized role name: {key}")
        mapping[key] = role
    return mapping


def compute_trait_layer_variance(
    trait_tensor: torch.Tensor,
    axis_tensor: torch.Tensor,
) -> tuple[pd.DataFrame, int]:
    trait_projection_matrix = compute_projection_matrix(trait_tensor, axis_tensor).cpu().numpy()
    layer_variances = trait_projection_matrix.var(axis=0)
    variance_df = pd.DataFrame({"layer": np.arange(trait_projection_matrix.shape[1]), "variance": layer_variances})
    peak_layer = int(variance_df.sort_values("variance", ascending=False).iloc[0]["layer"])
    return variance_df, peak_layer


def save_trait_layer_variance_plot(variance_df: pd.DataFrame, peak_layer: int) -> None:
    plt.figure(figsize=(12, 6))
    plt.plot(variance_df["layer"], variance_df["variance"], marker="o", color="#2166AC")
    plt.axvline(ROLE_PEAK_LAYER, color="#999999", linestyle="--", linewidth=1, label="Role peak layer (45)")
    plt.scatter([peak_layer], [variance_df.loc[variance_df["layer"] == peak_layer, "variance"].iloc[0]], color="#D6604D")
    plt.text(
        peak_layer,
        variance_df.loc[variance_df["layer"] == peak_layer, "variance"].iloc[0],
        f"trait peak L{peak_layer}",
        fontsize=9,
        ha="left",
        va="bottom",
    )
    plt.xlabel("Layer")
    plt.ylabel("Variance of trait-axis projections across 240 traits")
    plt.title("Trait Differentiation by Layer (Gemma 2 27B)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "trait_layer_discrimination.png", dpi=200)
    plt.close()


def sign_convention_check(traits: list[str], trait_tensor: torch.Tensor, axis_tensor: torch.Tensor) -> dict[str, float]:
    idx = {trait: i for i, trait in enumerate(traits)}
    projections = compute_projection_matrix(trait_tensor, axis_tensor).cpu().numpy()
    missing = [trait for trait in POSITIVE_TRAITS + NEGATIVE_TRAITS if trait not in idx]
    if missing:
        return {}
    positive_mean = float(np.mean([projections[idx[trait], DEFAULT_LAYER] for trait in POSITIVE_TRAITS]))
    negative_mean = float(np.mean([projections[idx[trait], DEFAULT_LAYER] for trait in NEGATIVE_TRAITS]))
    if positive_mean < negative_mean:
        raise RuntimeError(
            "Trait vectors appear to use the opposite sign convention from role vectors: "
            f"positive assistant-like trait mean ({positive_mean:.4f}) < negative trait mean ({negative_mean:.4f})"
        )
    return {"positive_mean": positive_mean, "negative_mean": negative_mean}


def cosine_similarity_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a64 = np.asarray(a, dtype=np.float64)
    b64 = np.asarray(b, dtype=np.float64)
    return 1.0 - cdist(a64, b64, metric="cosine")


def zscore_by_column(matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    means = matrix.mean(axis=0)
    stds = matrix.std(axis=0, ddof=0)
    near_zero = stds[stds < 1e-8]
    if not near_zero.empty:
        raise RuntimeError(
            "Trait(s) with near-zero variance across roles after similarity computation: "
            + ", ".join(near_zero.index.tolist())
        )
    zscored = (matrix - means) / stds
    return zscored, stds


def cluster_trait_profiles(
    role_trait_z: pd.DataFrame,
    ranking_df: pd.DataFrame,
    role_mapping: dict[str, str],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    ranking = ranking_df.copy()
    ranking["role"] = ranking["character"].map(role_mapping)
    if ranking["role"].isna().any():
        missing = ranking.loc[ranking["role"].isna(), "character"].tolist()
        raise RuntimeError(f"Could not map these characters back to raw role names: {missing[:10]}")

    role_to_cluster = ranking.set_index("role")["cluster_label"].to_dict()
    rows = []
    summary_tables: dict[str, pd.DataFrame] = {}

    for cluster_label, sub_roles in ranking.groupby("cluster_label")["role"]:
        cluster_matrix = role_trait_z.loc[sub_roles.tolist()]
        mean_profile = cluster_matrix.mean(axis=0).sort_values(ascending=False)
        top10 = mean_profile.head(10)
        bottom10 = mean_profile.tail(10).sort_values(ascending=True)
        summary_tables[cluster_label] = pd.concat(
            [
                pd.DataFrame({"trait": top10.index, "mean_zscore": top10.values, "direction": "top"}),
                pd.DataFrame({"trait": bottom10.index, "mean_zscore": bottom10.values, "direction": "bottom"}),
            ],
            ignore_index=True,
        )
        for rank, (trait, value) in enumerate(mean_profile.items(), 1):
            rows.append(
                {
                    "cluster_label": cluster_label,
                    "trait": trait,
                    "mean_zscore": float(value),
                    "rank_desc": rank,
                    "direction": "top" if rank <= 10 else ("bottom" if rank > len(mean_profile) - 10 else "middle"),
                    "cluster_size": int((ranking["cluster_label"] == cluster_label).sum()),
                }
            )

    cluster_profile_df = pd.DataFrame(rows).sort_values(["cluster_label", "rank_desc"]).reset_index(drop=True)
    return cluster_profile_df, summary_tables


def compute_profile_similarity(role_trait_raw: pd.DataFrame) -> np.ndarray:
    matrix = role_trait_raw.to_numpy(dtype=np.float64)
    distances = squareform(pdist(matrix, metric="cosine"))
    return 1.0 - distances


def within_across_difference(sim_matrix: np.ndarray, labels: np.ndarray) -> tuple[float, float, float]:
    iu = np.triu_indices_from(sim_matrix, k=1)
    pair_sims = sim_matrix[iu]
    same_mask = labels[iu[0]] == labels[iu[1]]
    within_mean = float(pair_sims[same_mask].mean())
    across_mean = float(pair_sims[~same_mask].mean())
    return within_mean, across_mean, within_mean - across_mean


def permutation_test(sim_matrix: np.ndarray, labels: np.ndarray, n_perm: int = PERMUTATIONS) -> tuple[float, float, float, np.ndarray]:
    within_mean, across_mean, observed = within_across_difference(sim_matrix, labels)
    rng = np.random.default_rng(0)
    perm_diffs = np.empty(n_perm, dtype=np.float64)
    for i in range(n_perm):
        shuffled = rng.permutation(labels)
        _, _, diff = within_across_difference(sim_matrix, shuffled)
        perm_diffs[i] = diff
    p_value = float((np.sum(perm_diffs >= observed) + 1) / (n_perm + 1))
    return within_mean, across_mean, p_value, perm_diffs


def save_permutation_plot(perm_diffs: np.ndarray, observed: float) -> None:
    plt.figure(figsize=(10, 6))
    plt.hist(perm_diffs, bins=40, color="#AABBD4", edgecolor="white")
    plt.axvline(observed, color="#D6604D", linewidth=2, label=f"Observed = {observed:.4f}")
    plt.xlabel("Within-cluster minus across-cluster mean profile cosine similarity")
    plt.ylabel("Count")
    plt.title("Permutation Test: Cluster Trait-Profile Coherence")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "permutation_test.png", dpi=200)
    plt.close()


def top_bottom_traits(raw_series: pd.Series, z_series: pd.Series, n: int = 15) -> dict[str, pd.DataFrame]:
    return {
        "raw_top": raw_series.sort_values(ascending=False).head(n).reset_index().rename(columns={"index": "trait", raw_series.name: "value"}),
        "raw_bottom": raw_series.sort_values(ascending=True).head(n).reset_index().rename(columns={"index": "trait", raw_series.name: "value"}),
        "z_top": z_series.sort_values(ascending=False).head(n).reset_index().rename(columns={"index": "trait", z_series.name: "value"}),
        "z_bottom": z_series.sort_values(ascending=True).head(n).reset_index().rename(columns={"index": "trait", z_series.name: "value"}),
    }


def anomaly_note(role: str, raw_top_traits: list[str]) -> str:
    joined = ", ".join(raw_top_traits[:5])
    notes = {
        "robot": f"Top raw traits ({joined}) would be consistent with the paper's systematic-execution interpretation if they emphasize detachment, method, or regularity.",
        "assistant": f"Top raw traits ({joined}) help test whether the literal assistant role looks broadly helpful or specifically procedural/evaluative.",
        "poet": f"Top raw traits ({joined}) should clarify whether the anti-assistant pole aligns with theatricality, expressiveness, and metaphor-rich style.",
        "angel": f"Top raw traits ({joined}) help distinguish practical benevolence from spiritual abstraction, which is central to the paper's interpretation.",
        "saboteur": f"Top raw traits ({joined}) are the key check for whether saboteur looks chaotic or tactically organized in trait space.",
    }
    return notes[role]


def write_summary(
    trait_peak_layer: int,
    trait_peak_variance: float,
    sign_check: dict[str, float],
    within_mean: float,
    across_mean: float,
    observed_diff: float,
    p_value: float,
    cluster_tables: dict[str, pd.DataFrame],
    anomaly_results: dict[str, dict[str, pd.DataFrame]],
) -> None:
    lines = [
        "# Role-Trait Similarity Analysis Summary",
        "",
        "## Layer Selection",
        "",
    ]
    if trait_peak_layer == ROLE_PEAK_LAYER:
        lines.append(
            f"Trait-axis projection variance also peaks at layer `{trait_peak_layer}` "
            f"(variance `{trait_peak_variance:.6f}`), so layer 45 was used for both roles and traits."
        )
    else:
        lines.append(
            f"Trait-axis projection variance peaks at layer `{trait_peak_layer}` "
            f"(variance `{trait_peak_variance:.6f}`), while roles previously peaked at layer `{ROLE_PEAK_LAYER}`. "
            "This discrepancy is itself a finding. The analysis therefore used layer 45 for roles and the trait-peak layer for traits."
        )
    lines.append("")
    if sign_check:
        lines.extend(
            [
                "Sign-convention sanity check against the Assistant Axis README examples:",
                f"- mean(`transparent`, `grounded`, `flexible`) at layer 22 = `{sign_check['positive_mean']:.4f}`",
                f"- mean(`enigmatic`, `subversive`, `dramatic`) at layer 22 = `{sign_check['negative_mean']:.4f}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Null Hypothesis Test",
            "",
            f"- Mean within-cluster profile cosine similarity: `{within_mean:.6f}`",
            f"- Mean across-cluster profile cosine similarity: `{across_mean:.6f}`",
            f"- Observed difference (within - across): `{observed_diff:.6f}`",
            f"- Permutation-test p-value (`n={PERMUTATIONS}`): `{p_value:.6f}`",
            "",
            "## Top Traits Per Cluster",
            "",
        ]
    )

    for cluster_label, table in cluster_tables.items():
        top = table[table["direction"] == "top"].copy()
        bottom = table[table["direction"] == "bottom"].copy()
        lines.append(f"### {cluster_label}")
        lines.append("")
        lines.append("**Top 10 traits**")
        lines.append("")
        lines.append("| Rank | Trait | Mean z-score |")
        lines.append("| --- | --- | ---: |")
        for idx, row in enumerate(top.itertuples(index=False), 1):
            lines.append(f"| {idx} | `{row.trait}` | {row.mean_zscore:.3f} |")
        lines.append("")
        lines.append("**Bottom 10 traits**")
        lines.append("")
        lines.append("| Rank | Trait | Mean z-score |")
        lines.append("| --- | --- | ---: |")
        for idx, row in enumerate(bottom.itertuples(index=False), 1):
            lines.append(f"| {idx} | `{row.trait}` | {row.mean_zscore:.3f} |")
        lines.append("")

    lines.extend(["## Anomaly Deep-Dives", ""])
    for role, tables in anomaly_results.items():
        lines.append(f"### {role}")
        lines.append("")
        lines.append(anomaly_note(role, tables["raw_top"]["trait"].tolist()))
        lines.append("")
        for key, title in [
            ("raw_top", "Top 15 traits by raw cosine similarity"),
            ("raw_bottom", "Bottom 15 traits by raw cosine similarity"),
            ("z_top", "Top 15 traits by z-scored similarity"),
            ("z_bottom", "Bottom 15 traits by z-scored similarity"),
        ]:
            lines.append(f"**{title}**")
            lines.append("")
            lines.append("| Rank | Trait | Value |")
            lines.append("| --- | --- | ---: |")
            for idx, row in enumerate(tables[key].itertuples(index=False), 1):
                lines.append(f"| {idx} | `{row.trait}` | {row.value:.3f} |")
            lines.append("")

    surprising = []
    if p_value < 0.05:
        surprising.append("Trait profiles are more cluster-coherent than expected under random cluster assignment.")
    if trait_peak_layer != ROLE_PEAK_LAYER:
        surprising.append("Trait differentiation peaks at a different layer than role differentiation.")
    if not surprising:
        surprising.append("No additional anomalies exceeded the pre-registered checks beyond the expected cluster structure.")

    lines.extend(["## Findings To Revisit", ""])
    for item in surprising:
        lines.append(f"- {item}")
    lines.append("")

    (OUT_DIR / "trait_analysis_summary.md").write_text("\n".join(lines))


def main() -> None:
    roles, role_tensor, traits, trait_tensor, ranking_df = validate_inputs()
    role_mapping = build_role_mapping(roles)
    axis_tensor = load_axis_tensor()

    sign_check = sign_convention_check(traits, trait_tensor, axis_tensor)

    progress("Computing trait layer-variance scan ...")
    trait_variance_df, trait_peak_layer = compute_trait_layer_variance(trait_tensor, axis_tensor)
    save_trait_layer_variance_plot(trait_variance_df, trait_peak_layer)

    role_layer = ROLE_PEAK_LAYER
    trait_layer = trait_peak_layer
    progress(f"Using role layer {role_layer} and trait layer {trait_layer} for role-trait similarity.")

    role_layer_matrix = role_tensor[:, role_layer, :].cpu().numpy()
    trait_layer_matrix = trait_tensor[:, trait_layer, :].cpu().numpy()
    similarity = cosine_similarity_matrix(role_layer_matrix, trait_layer_matrix)
    role_trait_raw = pd.DataFrame(similarity, index=roles, columns=traits)
    role_trait_raw.to_csv(OUT_DIR / "role_trait_similarity.csv")

    progress("Z-scoring trait similarities by trait column ...")
    role_trait_z, trait_stds = zscore_by_column(role_trait_raw)
    role_trait_z.to_csv(OUT_DIR / "role_trait_similarity_zscored.csv")

    progress("Computing cluster trait profiles ...")
    cluster_profile_df, cluster_tables = cluster_trait_profiles(role_trait_z, ranking_df, role_mapping)
    cluster_profile_df.to_csv(OUT_DIR / "cluster_trait_profiles.csv", index=False)

    progress("Running within-cluster vs across-cluster trait-profile permutation test ...")
    ranking_with_roles = ranking_df.copy()
    ranking_with_roles["role"] = ranking_with_roles["character"].map(role_mapping)
    ranking_with_roles = ranking_with_roles.set_index("role").loc[roles].reset_index()
    labels = ranking_with_roles["cluster_label"].to_numpy()
    profile_similarity_matrix = compute_profile_similarity(role_trait_raw)
    within_mean, across_mean, p_value, perm_diffs = permutation_test(profile_similarity_matrix, labels)
    observed_diff = within_mean - across_mean
    save_permutation_plot(perm_diffs, observed_diff)

    progress("Compiling anomaly deep-dives ...")
    anomaly_results: dict[str, dict[str, pd.DataFrame]] = {}
    for role in ANOMALY_ROLES:
        raw_series = role_trait_raw.loc[role].rename("raw_similarity")
        z_series = role_trait_z.loc[role].rename("z_similarity")
        anomaly_results[role] = top_bottom_traits(raw_series, z_series)

    write_summary(
        trait_peak_layer=trait_peak_layer,
        trait_peak_variance=float(trait_variance_df.loc[trait_variance_df["layer"] == trait_peak_layer, "variance"].iloc[0]),
        sign_check=sign_check,
        within_mean=within_mean,
        across_mean=across_mean,
        observed_diff=observed_diff,
        p_value=p_value,
        cluster_tables=cluster_tables,
        anomaly_results=anomaly_results,
    )

    print("Trait-role analysis complete.")
    print(f"Trait peak layer: {trait_peak_layer}")
    print(f"Observed within-across difference: {observed_diff:.6f}")
    print(f"Permutation p-value: {p_value:.6f}")
    print(f"Saved summary to {OUT_DIR / 'trait_analysis_summary.md'}")


if __name__ == "__main__":
    main()
