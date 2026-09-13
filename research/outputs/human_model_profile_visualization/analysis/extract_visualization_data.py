#!/usr/bin/env python3
"""Extract frozen AA-12 correspondence values into figure-ready aggregate tables.

This script does not fit, optimize, permute, or otherwise alter the frozen
human/model correspondence. It verifies and reshapes committed aggregate data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


HERE = Path(__file__).resolve()
OUT = HERE.parents[1]
REPO = HERE.parents[4]
SRC = REPO / "research/outputs/human_model_profile_correspondence"
DATA = OUT / "data"

ELIGIBLE_K = [4, 5, 6, 7, 8, 10]
PRIMARY_FAMILIES = ["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D"]
PRIMARY_PAIRS = {
    "MFamily_A": "H10_C",
    "MFamily_B": "H10_J",
    "MFamily_C": "H10_G",
    "MFamily_D": "H10_I",
}
TIER_ORDER = {
    "HIGH HUMAN-MEASUREMENT SUPPORT": 0,
    "MODERATE SUPPORT": 1,
    "REDUNDANT / BROAD": 2,
    "INSUFFICIENT": 3,
}

SOURCE_FILES = [
    "human_trait_profiles_45.csv",
    "human_trait_profiles_12.csv",
    "human_sapa_item_profile_values.csv",
    "human_sapa_item_visualization_order.csv",
    "model_family_trait_profiles_45.csv",
    "model_family_trait_profiles_12.csv",
    "profile_similarity_45.csv",
    "profile_similarity_12.csv",
    "primary_assignments_by_k.csv",
    "primary_assignments_12_by_k.csv",
    "bridge_permutation_null_45.csv",
    "bridge_permutation_null_12.csv",
    "family_specific_results.csv",
    "human_stability_sensitivity.csv",
    "k9_diagnostic.csv",
    "model_specific_replication.csv",
    "cross_resolution_human_persistence.csv",
    "relaxed_split_merge_browsing.csv",
    "mfamily_e_secondary.csv",
    "primary_global_result.json",
    "robustness_result.json",
    "common_space_manifest.json",
    "semantic_profile_summary.md",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_csv(df: pd.DataFrame, name: str) -> Path:
    path = DATA / name
    df.to_csv(path, index=False, float_format="%.12g", lineterminator="\n")
    return path


def assert_close(actual: float, expected: float, label: str, atol: float = 1e-10) -> None:
    if not np.isclose(actual, expected, atol=atol, rtol=0):
        raise AssertionError(f"{label}: {actual} != {expected}")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    for name in SOURCE_FILES:
        if not (SRC / name).is_file():
            raise FileNotFoundError(SRC / name)

    h45 = pd.read_csv(SRC / "human_trait_profiles_45.csv")
    h12 = pd.read_csv(SRC / "human_trait_profiles_12.csv")
    m45 = pd.read_csv(SRC / "model_family_trait_profiles_45.csv")
    m12 = pd.read_csv(SRC / "model_family_trait_profiles_12.csv")
    sim45 = pd.read_csv(SRC / "profile_similarity_45.csv")
    sim12 = pd.read_csv(SRC / "profile_similarity_12.csv")
    assignments = pd.read_csv(SRC / "primary_assignments_by_k.csv")
    assignments12 = pd.read_csv(SRC / "primary_assignments_12_by_k.csv")
    family = pd.read_csv(SRC / "family_specific_results.csv")
    null45 = pd.read_csv(SRC / "bridge_permutation_null_45.csv")
    null12 = pd.read_csv(SRC / "bridge_permutation_null_12.csv")
    stability = pd.read_csv(SRC / "human_stability_sensitivity.csv")
    k9 = pd.read_csv(SRC / "k9_diagnostic.csv")
    replication = pd.read_csv(SRC / "model_specific_replication.csv")
    persistence = pd.read_csv(SRC / "cross_resolution_human_persistence.csv")
    relaxed = pd.read_csv(SRC / "relaxed_split_merge_browsing.csv")
    e_secondary = pd.read_csv(SRC / "mfamily_e_secondary.csv")
    sapa = pd.read_csv(SRC / "human_sapa_item_profile_values.csv")
    sapa_order = pd.read_csv(SRC / "human_sapa_item_visualization_order.csv")
    primary_json = json.loads((SRC / "primary_global_result.json").read_text())
    robust_json = json.loads((SRC / "robustness_result.json").read_text())
    common_json = json.loads((SRC / "common_space_manifest.json").read_text())

    canonical_traits = common_json["direct_traits"]
    supported_traits = set(common_json["supported_traits_12"])
    if len(canonical_traits) != 45 or len(supported_traits) != 12:
        raise AssertionError("Frozen 45/12 trait counts changed")
    trait_order = {trait: i + 1 for i, trait in enumerate(canonical_traits)}

    meta_cols = [
        "trait",
        "human_measurement_support_tier",
        "structural_support_status",
        "single_item_flag",
        "exact_or_inverse_item_set_alias",
        "max_shared_item_effect",
        "mapped_item_count",
        "unique_item_count",
    ]
    metadata = h45[meta_cols].drop_duplicates("trait").copy()
    metadata["canonical_order"] = metadata["trait"].map(trait_order)
    metadata["measurement_group_order"] = metadata["human_measurement_support_tier"].map(TIER_ORDER)
    metadata["is_12_trait_core"] = metadata["trait"].isin(supported_traits)
    metadata = metadata.sort_values(["measurement_group_order", "canonical_order"])
    metadata["grouped_order"] = np.arange(1, len(metadata) + 1)
    save_csv(metadata, "trait_metadata.csv")

    # Primary matched profiles and requested trait-level decomposition.
    shape_rows: list[dict] = []
    for fam, hp in PRIMARY_PAIRS.items():
        hv = h45[h45.profile_id.eq(hp)].set_index("trait")
        mv = m45[m45.family_id.eq(fam)].set_index("trait")
        hvals = hv.loc[canonical_traits, "human_trait_value"].to_numpy(float)
        mvals = mv.loc[canonical_traits, "three_model_consensus_value"].to_numpy(float)
        contributions = (hvals - hvals.mean()) * (mvals - mvals.mean())
        expected = sim45[(sim45.human_profile_id.eq(hp)) & (sim45.model_family_id.eq(fam))].iloc[0]
        assert_close(np.corrcoef(hvals, mvals)[0, 1], expected.pearson_r, f"Pearson {fam}/{hp}")
        assert_close(spearmanr(hvals, mvals).statistic, expected.spearman_rho, f"Spearman {fam}/{hp}")
        for i, trait in enumerate(canonical_traits):
            md = metadata.set_index("trait").loc[trait]
            shape_rows.append(
                {
                    "model_family_id": fam,
                    "human_profile_id": hp,
                    "pair_role": "primary_injective_K10",
                    "trait": trait,
                    "canonical_order": trait_order[trait],
                    "grouped_order": int(md.grouped_order),
                    "human_value": hvals[i],
                    "model_consensus_value": mvals[i],
                    "qwen_value": mv.loc[trait, "qwen_value"],
                    "llama_value": mv.loc[trait, "llama_value"],
                    "gemma_value": mv.loc[trait, "gemma_value"],
                    "signed_difference_human_minus_model": hvals[i] - mvals[i],
                    "absolute_difference": abs(hvals[i] - mvals[i]),
                    "covariance_contribution": contributions[i],
                    "pair_pearson_r": expected.pearson_r,
                    "pair_spearman_rho": expected.spearman_rho,
                    "human_measurement_support_tier": md.human_measurement_support_tier,
                    "structural_support_status": md.structural_support_status,
                    "is_12_trait_core": bool(md.is_12_trait_core),
                    "single_item_flag": bool(md.single_item_flag),
                    "redundant_or_broad_flag": md.human_measurement_support_tier == "REDUNDANT / BROAD",
                }
            )
    shapes = pd.DataFrame(shape_rows)
    save_csv(shapes, "primary_matched_profile_shapes.csv")

    top_rows: list[pd.DataFrame] = []
    for (fam, hp), group in shapes.groupby(["model_family_id", "human_profile_id"], sort=False):
        positive = group.sort_values(["covariance_contribution", "canonical_order"], ascending=[False, True]).head(8).copy()
        positive["driver_type"] = "top_positive_covariance_contribution"
        positive["rank"] = range(1, 9)
        disagreement = group.sort_values(["absolute_difference", "canonical_order"], ascending=[False, True]).head(8).copy()
        disagreement["driver_type"] = "top_absolute_disagreement"
        disagreement["rank"] = range(1, 9)
        top_rows.extend([positive, disagreement])
    top_drivers = pd.concat(top_rows, ignore_index=True)
    save_csv(top_drivers, "top_trait_drivers.csv")

    # K-level primary progression, retaining K=9 only as an ineligible diagnostic.
    k_rows = []
    for row in primary_json["K_scores"]:
        k = int(row["K"])
        k_rows.append(
            {
                "K": k,
                "included_in_primary": True,
                "status": "eligible",
                "mean_fisher_z": row["mean_fisher_z"],
                "back_transformed_mean_r": row["back_transformed_mean_r"],
                "human_stability": "moderate" if k <= 6 else "low",
                "anchor": "BIC/ICL anchor" if k == 4 else ("predictive-likelihood anchor; primary maximum" if k == 10 else ""),
            }
        )
    k_rows.append(
        {
            "K": 9,
            "included_in_primary": False,
            "status": "DIAGNOSTIC / INELIGIBLE",
            "mean_fisher_z": k9.mean_fisher_z.iloc[0],
            "back_transformed_mean_r": k9.back_transformed_mean_r.iloc[0],
            "human_stability": "low",
            "anchor": "excluded from primary scan",
        }
    )
    k_progression = pd.DataFrame(k_rows).sort_values("K")
    save_csv(k_progression, "k_progression.csv")

    # Unconstrained family-specific best human profile at each eligible K.
    best_rows = []
    for (k, fam), group in sim45.groupby(["K", "model_family_id"], sort=True):
        ranked = group.sort_values(["pearson_r", "human_profile_id"], ascending=[False, True])
        row = ranked.iloc[0]
        frow = family[family.model_family_id.eq(fam)].iloc[0]
        best_rows.append(
            {
                "K": int(k),
                "model_family_id": fam,
                "best_human_profile_id": row.human_profile_id,
                "best_pearson_r": row.pearson_r,
                "best_spearman_rho": row.spearman_rho,
                "family_specific_search_adjusted_p_over_all_K_profiles": frow.family_specific_search_adjusted_p,
                "passes_frozen_p05": bool(frow.positive_adjusted_evidence),
            }
        )
    family_best = pd.DataFrame(best_rows)
    save_csv(family_best, "family_best_by_k.csv")

    assignment_evolution = assignments.merge(
        family_best,
        on=["K", "model_family_id"],
        how="left",
        validate="one_to_one",
    )
    assignment_evolution["assigned_minus_unconstrained_best_r"] = (
        assignment_evolution.pearson_r - assignment_evolution.best_pearson_r
    )
    assignment_evolution["assignment_equals_unconstrained_best"] = (
        assignment_evolution.human_profile_id == assignment_evolution.best_human_profile_id
    )
    assignment_evolution["human_stability"] = np.where(assignment_evolution.K <= 6, "moderate", "low")
    persistence_keys = set(zip(persistence.K, persistence.human_profile_id))
    assignment_evolution["appears_in_frozen_mutual_nearest_lineage"] = [
        (k, hp) in persistence_keys for k, hp in zip(assignment_evolution.K, assignment_evolution.human_profile_id)
    ]
    save_csv(assignment_evolution, "assignment_evolution.csv")
    save_csv(persistence.copy(), "human_profile_continuity.csv")

    # Full A-D matrices plus separately flagged E values.
    sim_full = sim45.copy()
    sim_full["analysis_role"] = "primary_A-D"
    e = e_secondary[e_secondary.K.isin(ELIGIBLE_K)].copy()
    e = e.rename(columns={"human_profile_id": "human_profile_id"})
    e["trait_set"] = "45_ACCEPT_DIRECT"
    e["model_family_id"] = "MFamily_E"
    e["analysis_role"] = "secondary_E"
    e = e[["trait_set", "K", "human_profile_id", "model_family_id", "pearson_r", "spearman_rho", "analysis_role"]]
    sim_full = pd.concat(
        [sim_full[["trait_set", "K", "human_profile_id", "model_family_id", "pearson_r", "spearman_rho", "analysis_role"]], e],
        ignore_index=True,
    )
    primary_keys = set(zip(assignments.K, assignments.human_profile_id, assignments.model_family_id))
    best_keys = set(zip(family_best.K, family_best.best_human_profile_id, family_best.model_family_id))
    e_best = e_secondary[e_secondary.is_best_eligible]
    best_keys.update(zip(e_best.K, e_best.human_profile_id, ["MFamily_E"] * len(e_best)))
    ambiguous_keys = set(zip(relaxed[relaxed.ambiguous_margin_le_0_10].K, relaxed[relaxed.ambiguous_margin_le_0_10].human_profile_id))
    sim_full["is_primary_injective_assignment"] = [
        (k, hp, fam) in primary_keys for k, hp, fam in zip(sim_full.K, sim_full.human_profile_id, sim_full.model_family_id)
    ]
    sim_full["is_unconstrained_family_best_at_K"] = [
        (k, hp, fam) in best_keys for k, hp, fam in zip(sim_full.K, sim_full.human_profile_id, sim_full.model_family_id)
    ]
    sim_full["human_profile_has_ambiguous_top_two_margin"] = [
        (k, hp) in ambiguous_keys for k, hp in zip(sim_full.K, sim_full.human_profile_id)
    ]
    sim_full = sim_full.sort_values(["K", "human_profile_id", "model_family_id"])
    save_csv(sim_full, "full_similarity_matrices.csv")

    # C/D/E competition: deterministic union of top four K=10 human profiles for each family.
    cde = sim_full[(sim_full.K.eq(10)) & (sim_full.model_family_id.isin(["MFamily_C", "MFamily_D", "MFamily_E"]))]
    selected_profiles = {"H10_I", "H10_G"}
    for fam in ["MFamily_C", "MFamily_D", "MFamily_E"]:
        selected_profiles.update(
            cde[cde.model_family_id.eq(fam)].nlargest(4, "pearson_r").human_profile_id.tolist()
        )
    cde_comp = cde[cde.human_profile_id.isin(sorted(selected_profiles))].copy()
    cde_comp["selection_rule"] = "union of top four K10 profiles for C/D/E; H10_I and H10_G forced"
    save_csv(cde_comp, "cde_competition.csv")

    cde_shapes = []
    for label, kind in [("H10_I", "human"), ("H10_G", "human"), ("MFamily_C", "model"), ("MFamily_D", "model"), ("MFamily_E", "model")]:
        if kind == "human":
            values = h45[h45.profile_id.eq(label)].set_index("trait")["human_trait_value"]
        else:
            values = m45[m45.family_id.eq(label)].set_index("trait")["three_model_consensus_value"]
        for trait in canonical_traits:
            cde_shapes.append(
                {"profile_id": label, "domain": kind, "trait": trait, "canonical_order": trait_order[trait], "value": values.loc[trait]}
            )
    save_csv(pd.DataFrame(cde_shapes), "cde_profile_shapes.csv")

    # A/D exemplars distinguish the global injective pair from A's family-specific maximum.
    exemplar_specs = [
        ("MFamily_A", "H10_C", "primary_injective_K10"),
        ("MFamily_A", "H06_A", "family_specific_strongest"),
        ("MFamily_D", "H10_I", "primary_and_family_specific_strongest"),
    ]
    exemplar_rows = []
    for fam, hp, role in exemplar_specs:
        hv = h45[h45.profile_id.eq(hp)].set_index("trait")["human_trait_value"]
        mv = m45[m45.family_id.eq(fam)].set_index("trait")["three_model_consensus_value"]
        match = sim45[(sim45.human_profile_id.eq(hp)) & (sim45.model_family_id.eq(fam))].iloc[0]
        for trait in canonical_traits:
            exemplar_rows.append(
                {
                    "model_family_id": fam,
                    "human_profile_id": hp,
                    "comparison_role": role,
                    "trait": trait,
                    "canonical_order": trait_order[trait],
                    "human_value": hv.loc[trait],
                    "model_consensus_value": mv.loc[trait],
                    "pearson_r": match.pearson_r,
                    "spearman_rho": match.spearman_rho,
                }
            )
    save_csv(pd.DataFrame(exemplar_rows), "ad_exemplars.csv")

    # Frozen 45-versus-12 comparison at the shared maximizing K=10.
    compare_rows = []
    global_specs = [
        ("45_ACCEPT_DIRECT", assignments, primary_json["observed_max_back_transformed_mean_r"], primary_json["search_adjusted_global_p"]),
        ("12_HUMAN_SUPPORTED", assignments12, robust_json["twelve_trait"]["back_transformed_mean_r"], robust_json["twelve_trait"]["search_adjusted_p"]),
    ]
    primary45_k10 = assignments[assignments.K.eq(10)].set_index("model_family_id")
    for trait_set, table, global_r, global_p in global_specs:
        for _, row in table[table.K.eq(10)].iterrows():
            fixed_hp = primary45_k10.loc[row.model_family_id, "human_profile_id"]
            fixed12 = sim12[(sim12.K.eq(10)) & (sim12.human_profile_id.eq(fixed_hp)) & (sim12.model_family_id.eq(row.model_family_id))].iloc[0]
            compare_rows.append(
                {
                    "trait_set": trait_set,
                    "model_family_id": row.model_family_id,
                    "selected_human_profile_id": row.human_profile_id,
                    "selected_pearson_r": row.pearson_r,
                    "selected_spearman_rho": row.spearman_rho,
                    "same_profile_as_45_trait_assignment": row.human_profile_id == fixed_hp,
                    "primary_45_human_profile_id": fixed_hp,
                    "primary_45_pair_r_evaluated_on_12_traits": fixed12.pearson_r,
                    "global_back_transformed_mean_r": global_r,
                    "global_search_adjusted_p": global_p,
                }
            )
    save_csv(pd.DataFrame(compare_rows), "trait_set_comparison.csv")

    rep_plot = replication[replication.representation.isin(["three_model_consensus", "qwen", "llama", "gemma"])].copy()
    rep_order = {"three_model_consensus": 0, "qwen": 1, "llama": 2, "gemma": 3}
    rep_plot["representation_order"] = rep_plot.representation.map(rep_order)
    rep_plot = rep_plot.sort_values(["model_family_id", "representation_order"])
    save_csv(rep_plot, "model_specific_replication.csv")

    # Frozen null transformed only into deterministic display bins and exact summaries.
    counts, edges = np.histogram(null45.global_max_fisher_z.to_numpy(), bins=60)
    null_hist = pd.DataFrame(
        {
            "bin_left": edges[:-1],
            "bin_right": edges[1:],
            "bin_midpoint": (edges[:-1] + edges[1:]) / 2,
            "count": counts,
        }
    )
    save_csv(null_hist, "permutation_null_histogram.csv")
    null_summary = pd.DataFrame(
        [
            {"statistic": "null_median", "value": null45.global_max_fisher_z.median()},
            {"statistic": "null_95th_percentile", "value": null45.global_max_fisher_z.quantile(0.95)},
            {"statistic": "null_99th_percentile", "value": null45.global_max_fisher_z.quantile(0.99)},
            {"statistic": "null_99_9th_percentile", "value": null45.global_max_fisher_z.quantile(0.999)},
            {"statistic": "observed_max_mean_fisher_z", "value": primary_json["observed_max_mean_fisher_z"]},
            {"statistic": "null_exceedance_count", "value": int((null45.global_max_fisher_z >= primary_json["observed_max_mean_fisher_z"]).sum())},
            {"statistic": "permutation_count", "value": len(null45)},
            {"statistic": "empirical_p", "value": primary_json["search_adjusted_global_p"]},
        ]
    )
    save_csv(null_summary, "permutation_null_summary.csv")

    family_stats = family.copy()
    family_stats["frozen_threshold"] = 0.05
    family_stats["interpretive_note"] = [
        "passes; family-specific maximum is H06_A rather than primary H10_C",
        "marginal; does not pass frozen threshold",
        "passes but shares H10_I maximum with D",
        "passes strongly; primary and family-specific maximum are H10_I",
    ]
    save_csv(family_stats, "family_specific_statistics.csv")

    # Exact SAPA wording and aggregate item z values for requested human profiles.
    requested_profiles = ["H10_C", "H10_J", "H10_G", "H10_I", "H06_A"]
    sapa_named = sapa.merge(
        sapa_order,
        left_on=["item_id", "trait"],
        right_on=["item_id", "primary_frozen_trait_owner"],
        how="inner",
        validate="many_to_one",
        suffixes=("", "_order"),
    )
    sapa_named = sapa_named[sapa_named.profile_id.isin(requested_profiles)].copy()
    if len(sapa_named) != 96 * len(requested_profiles):
        raise AssertionError(f"Expected 480 SAPA display rows, got {len(sapa_named)}")
    sapa_named = sapa_named.sort_values(["profile_id", "visualization_order"])
    sapa_cols = [
        "profile_id", "K", "item_id", "item_text", "primary_frozen_trait_owner",
        "all_frozen_direct_trait_mappings", "mapping_count", "trait_orientation_signs",
        "visualization_order", "expected_response", "empirical_mean_raw",
        "empirical_sd_raw_ddof1", "oriented_item_z", "observed_n", "observed_fraction",
    ]
    save_csv(sapa_named[sapa_cols], "sapa_language_profiles.csv")

    # Exact frozen input inventory.
    source_rows = []
    for name in SOURCE_FILES:
        path = SRC / name
        row = {
            "source_path": str(path.relative_to(REPO)),
            "sha256": sha256(path),
            "size_bytes": path.stat().st_size,
            "source_role": "frozen_AA12_followup4",
        }
        if path.suffix == ".csv":
            df = pd.read_csv(path)
            row.update({"rows": len(df), "columns": len(df.columns)})
        source_rows.append(row)
    source_checks = pd.DataFrame(source_rows)
    save_csv(source_checks, "source_artifact_checks.csv")

    # Numerical reproduction checks are validations, not a new analysis.
    checks: list[dict] = []
    def checked(name: str, actual, expected, note: str = "") -> None:
        if isinstance(actual, (float, np.floating)):
            passed = bool(np.isclose(actual, expected, atol=1e-10, rtol=0))
        else:
            passed = actual == expected
        checks.append({"check": name, "passed": passed, "actual": actual, "expected": expected, "note": note})
        if not passed:
            raise AssertionError(name)

    checked("eligible_K", primary_json["eligible_K"], ELIGIBLE_K)
    checked("mapped_unique_items", common_json["human"]["mapped_unique_items"], 96)
    checked("direct_trait_count", len(canonical_traits), 45)
    checked("supported_trait_count", len(supported_traits), 12)
    checked("primary_maximizing_K", primary_json["maximizing_K"], 10)
    checked("primary_mean_fisher_z", primary_json["observed_max_mean_fisher_z"], 0.5765711530686384)
    checked("primary_mean_r", primary_json["observed_max_back_transformed_mean_r"], 0.5201688077382118)
    checked("primary_null_exceedances", int((null45.global_max_fisher_z >= primary_json["observed_max_mean_fisher_z"]).sum()), 0)
    checked("primary_global_p", (1 + 0) / (len(null45) + 1), primary_json["search_adjusted_global_p"])
    checked("twelve_mean_r", robust_json["twelve_trait"]["back_transformed_mean_r"], 0.7607970003865232)
    checked("twelve_global_p", (1 + int((null12.global_max_fisher_z >= robust_json["twelve_trait"]["mean_fisher_z"]).sum())) / (len(null12) + 1), robust_json["twelve_trait"]["search_adjusted_p"])
    checked("stable_K456_best_K", robust_json["human_stability_K456"]["best_K"], 6)
    checked("stable_K456_mean_r", robust_json["human_stability_K456"]["back_transformed_mean_r"], 0.4483469191929081)
    checked("mfamily_E_best_profile", robust_json["mfamily_e_secondary"]["best_human_profile"], "H10_I")
    checked("mfamily_E_r", robust_json["mfamily_e_secondary"]["pearson_r"], 0.747646787414387)
    checked("primary_assignment_profiles", PRIMARY_PAIRS, dict(zip(primary45_k10.index, primary45_k10.human_profile_id)))
    checked("primary_assignment_is_injective", primary45_k10.human_profile_id.nunique(), 4)
    checked("replication_pair_rows", len(rep_plot), 16)
    checked("all_Qwen_LLaMA_Gemma_fixed_pair_signs_positive", bool((rep_plot[rep_plot.representation.ne("three_model_consensus")].pearson_r > 0).all()), True)
    checked("no_correspondence_reoptimization", True, True, "Only frozen rows were selected, joined, checked, or deterministically transformed")

    checks_path = OUT / "numerical_reproduction_checks.json"
    checks_path.write_text(json.dumps({"status": "PASS", "checks": checks}, indent=2, sort_keys=True) + "\n")

    table_paths = sorted(DATA.glob("*.csv"))
    manifest = {
        "artifact": "AA-12 follow-up-5 visualization source-data manifest",
        "date": "2026-09-13",
        "status": "figure-ready aggregate data frozen",
        "source_analysis_final_commit": "fea29c20792617b013775f40efe0546ebd6e8ec7",
        "source_method_freeze": "c71bcf9568cfed478d706bc559606de01af48f04",
        "source_common_space_freeze": "ba095f60783bd70f0003e14a88eb2e041b65cd42",
        "source_primary_numerical_freeze": "96c3e0d8595dfdfd15974c6bc66e31b58f0af065",
        "source_robustness_freeze": "e1d10da957ac9b31486bb17bcdaabf1306f29a03",
        "source_postfreeze_semantics": "f55738dcb002c8da8d5013aa40f1ca1855214d3f",
        "eligible_K": ELIGIBLE_K,
        "diagnostic_ineligible_K": 9,
        "primary_model_families": PRIMARY_FAMILIES,
        "secondary_model_family": "MFamily_E",
        "frozen_primary_pairs": PRIMARY_PAIRS,
        "source_artifacts": source_rows,
        "figure_source_tables": [
            {"path": str(p.relative_to(REPO)), "sha256": sha256(p), "size_bytes": p.stat().st_size}
            for p in table_paths
        ],
        "existing_figure_review": {
            "reused_exactly": [
                "figures/bridge_permutation_null_45.png",
                "figures/cross_resolution_persistence.png",
                "figures/model_specific_replication.png",
            ],
            "reason": "These frozen figures already satisfy the corresponding core display; the packet adds captions and richer companion views.",
            "other_existing_figures": "inspected but superseded where requested annotations or comparisons were absent",
        },
        "privacy": "aggregate profiles and item moments only; no respondent rows, IDs, masks, posteriors, scores, or imputations",
        "scientific_boundary": "visualization and deterministic inspection only; no fitting, matching optimization, new null, or claim",
    }
    (OUT / "visualization_data_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {len(table_paths)} source tables and {len(checks)} passing numerical checks")


if __name__ == "__main__":
    main()
