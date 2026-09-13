#!/usr/bin/env python3
"""Build frozen aggregate human/model profiles in the direct SAPA-trait bridge.

This stage deliberately computes no human/model similarities.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

HUMAN_BANK = ROOT / "research/outputs/cross_resolution_profile_banks/human/human_cross_resolution_profiles.csv"
HUMAN_SUMMARY = ROOT / "research/outputs/cross_resolution_profile_banks/human/human_cross_resolution_solution_summary.csv"
BRIDGE = ROOT / "research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_trait_bridge_provisional_v1.csv"
SCORING = ROOT / "research/outputs/sapa_bridge_psychometric_audit/trait_proxy_item_scoring.csv"
SUPPORT = ROOT / "research/outputs/sapa_bridge_psychometric_audit/sapa_trait_bridge_psychometric_support_v1.csv"
ITEM_DICTIONARY = ROOT / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"
CONSENSUS_TRAITS = ROOT / "research/outputs/crossmodel_cluster_reconciliation/consensus_family_trait_profiles.csv"
MODEL_BANK = ROOT / "research/outputs/cross_resolution_profile_banks/model"
SOURCE_MANIFEST = ROOT / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_source_manifest.json"

RAW_SHA256 = "fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6"
ELIGIBLE_K = {4, 5, 6, 7, 8, 10}
CORE_TIERS = {"HIGH HUMAN-MEASUREMENT SUPPORT", "MODERATE SUPPORT"}
MODEL_ORDER = ["qwen", "llama", "gemma"]
PRIMARY_FAMILIES = ["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D"]
E_COMPONENTS = {"qwen": "Q07_G", "llama": "L09_I", "gemma": "G06_A"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_raw_sapa() -> Path:
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    entry = next(x for x in manifest["files"] if x["file_name"].endswith(".tab"))
    candidates = [Path(entry["local_path"])]
    workspace = ROOT.parent
    candidates.extend(
        workspace.glob(
            "assistant-axis*/data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/"
            "sapaTempData696items08dec2013thru26jul2014.tab"
        )
    )
    for candidate in candidates:
        if candidate.is_file() and sha256(candidate) == RAW_SHA256:
            return candidate
    raise FileNotFoundError("No local gitignored SAPA tab artifact matched the frozen SHA256")


def direct_metadata() -> tuple[pd.DataFrame, pd.DataFrame, list[str], list[str]]:
    bridge = pd.read_csv(BRIDGE)
    bridge = bridge.loc[bridge["review_decision"].eq("ACCEPT_DIRECT")].copy()
    scoring = pd.read_csv(SCORING)
    scoring = scoring.loc[scoring["review_decision"].eq("ACCEPT_DIRECT")].copy()
    support = pd.read_csv(SUPPORT)
    support = support.loc[support["semantic_review_decision"].eq("ACCEPT_DIRECT")].copy()

    if len(bridge) != 45 or bridge["trait"].nunique() != 45:
        raise ValueError("Frozen bridge does not contain exactly 45 unique ACCEPT_DIRECT traits")
    if len(scoring) != 119 or scoring["item_id"].nunique() != 96:
        raise ValueError("Frozen direct item scoring is not 119 rows / 96 unique items")
    if len(support) != 45 or support["trait"].nunique() != 45:
        raise ValueError("Human support table does not contain the same 45 direct traits")
    if set(bridge["trait"]) != set(scoring["trait"]) or set(bridge["trait"]) != set(support["trait"]):
        raise ValueError("Direct trait sets disagree across frozen bridge artifacts")
    if not set(scoring["orientation_sign"].astype(int)).issubset({-1, 1}):
        raise ValueError("Unexpected orientation sign")

    meta = bridge[["trait", "canonical_definition", "review_decision", "bridge_tier", "item_count"]].merge(
        support[
            [
                "trait",
                "human_measurement_support_tier",
                "structural_support_status",
                "supporting_item_count",
                "exact_or_inverse_item_set_alias",
                "max_shared_item_effect",
                "nearest_retained_proxy",
                "nearest_retained_proxy_absolute_r",
            ]
        ],
        on="trait",
        validate="one_to_one",
    )
    meta["single_item_flag"] = meta["supporting_item_count"].astype(int).eq(1)
    traits45 = sorted(meta["trait"].tolist())
    traits12 = sorted(meta.loc[meta["human_measurement_support_tier"].isin(CORE_TIERS), "trait"].tolist())
    if len(traits12) != 12:
        raise ValueError(f"Expected 12 frozen supported traits, found {len(traits12)}")
    return scoring, meta, traits45, traits12


def build_human_profiles(
    raw_path: Path, scoring: pd.DataFrame, meta: pd.DataFrame, traits45: list[str], traits12: list[str]
) -> dict:
    item_ids = sorted(scoring["item_id"].unique(), key=lambda x: int(x.split("_")[1]))
    raw = pd.read_csv(raw_path, sep="\t", usecols=item_ids, na_values=[""], low_memory=False)
    if len(raw) != 23679 or set(raw.columns) != set(item_ids):
        raise ValueError(f"Unexpected SAPA dimensions for mapped items: {raw.shape}")

    moments = []
    for item in item_ids:
        x = pd.to_numeric(raw[item], errors="coerce")
        invalid = x.dropna().loc[~x.dropna().isin([1, 2, 3, 4, 5, 6])]
        if len(invalid):
            raise ValueError(f"Invalid response codes in {item}: {sorted(invalid.unique())}")
        moments.append(
            {
                "item_id": item,
                "observed_n": int(x.notna().sum()),
                "missing_n": int(x.isna().sum()),
                "observed_fraction": float(x.notna().mean()),
                "empirical_mean_raw": float(x.mean()),
                "empirical_sd_raw_ddof1": float(x.std(ddof=1)),
            }
        )
    del raw
    moments = pd.DataFrame(moments)
    if moments["empirical_sd_raw_ddof1"].le(0).any() or moments.isna().any().any():
        raise ValueError("Invalid empirical item moments")
    moments = moments.sort_values("item_id", key=lambda s: s.str.split("_").str[1].astype(int))
    moments.to_csv(OUT / "human_item_normalization_moments.csv", index=False, float_format="%.12g")

    item_dict = pd.read_csv(ITEM_DICTIONARY)[["item_id", "item_text"]]
    scoring2 = scoring.merge(moments, on="item_id", validate="many_to_one").merge(
        item_dict, on="item_id", how="left", suffixes=("", "_dictionary"), validate="many_to_one"
    )
    if scoring2["item_text_dictionary"].isna().any() or not scoring2["item_text"].eq(scoring2["item_text_dictionary"]).all():
        raise ValueError("Frozen scoring wording differs from canonical item dictionary")

    bank = pd.read_csv(HUMAN_BANK)
    bank["K"] = bank["K"].astype(int)
    expected_profiles = sum(range(4, 11))
    if bank[["K", "profile_id", "item_id"]].duplicated().any():
        raise ValueError("Duplicate human profile-item keys")
    if bank[["K", "profile_id"]].drop_duplicates().shape[0] != expected_profiles:
        raise ValueError("Expected 49 frozen profiles over K=4..10")
    selected = bank.loc[bank["item_id"].isin(item_ids)].copy()
    expected_rows = expected_profiles * len(item_ids)
    if len(selected) != expected_rows:
        raise ValueError(f"Expected {expected_rows} profile-item rows, found {len(selected)}")

    values = selected.merge(
        scoring2[
            [
                "trait",
                "item_id",
                "item_text",
                "orientation_sign",
                "transformation",
                "final_orientation",
                "observed_n",
                "observed_fraction",
                "empirical_mean_raw",
                "empirical_sd_raw_ddof1",
            ]
        ],
        on="item_id",
        validate="many_to_many",
    )
    values["oriented_profile_expected"] = np.where(
        values["orientation_sign"].astype(int).eq(1), values["expected_response"], 7.0 - values["expected_response"]
    )
    values["oriented_empirical_mean"] = np.where(
        values["orientation_sign"].astype(int).eq(1), values["empirical_mean_raw"], 7.0 - values["empirical_mean_raw"]
    )
    values["oriented_item_z"] = (
        values["orientation_sign"].astype(int)
        * (values["expected_response"] - values["empirical_mean_raw"])
        / values["empirical_sd_raw_ddof1"]
    )
    values["eligible_primary_k"] = values["K"].isin(ELIGIBLE_K)
    value_cols = [
        "K",
        "solution_status",
        "eligible_primary_k",
        "profile_id",
        "profile_size",
        "profile_proportion",
        "trait",
        "item_id",
        "item_text",
        "orientation_sign",
        "transformation",
        "final_orientation",
        "expected_response",
        "empirical_mean_raw",
        "empirical_sd_raw_ddof1",
        "observed_n",
        "observed_fraction",
        "oriented_profile_expected",
        "oriented_empirical_mean",
        "oriented_item_z",
    ]
    values = values[value_cols].sort_values(["K", "profile_id", "trait", "item_id"])
    values.to_csv(OUT / "human_sapa_item_profile_values.csv", index=False, float_format="%.12g")

    human = (
        values.groupby(
            ["K", "solution_status", "eligible_primary_k", "profile_id", "profile_size", "profile_proportion", "trait"],
            as_index=False,
            sort=True,
        )
        .agg(human_trait_value=("oriented_item_z", "mean"), mapped_item_count=("item_id", "size"), unique_item_count=("item_id", "nunique"))
        .merge(meta, on="trait", validate="many_to_one")
    )
    if human[["K", "profile_id", "trait"]].duplicated().any() or human.shape[0] != expected_profiles * 45:
        raise ValueError("Human 45-trait profile dimensions are incorrect")
    human = human.sort_values(["K", "profile_id", "trait"])
    human.to_csv(OUT / "human_trait_profiles_45.csv", index=False, float_format="%.12g")
    human12 = human.loc[human["trait"].isin(traits12)].copy()
    if human12.shape[0] != expected_profiles * 12:
        raise ValueError("Human 12-trait profile dimensions are incorrect")
    human12.to_csv(OUT / "human_trait_profiles_12.csv", index=False, float_format="%.12g")

    return {
        "respondent_rows": 23679,
        "raw_sapa_sha256": sha256(raw_path),
        "mapped_unique_items": len(item_ids),
        "mapped_trait_item_rows": len(scoring),
        "human_profiles": expected_profiles,
        "human_profile_rows_45": len(human),
        "human_profile_rows_12": len(human12),
    }


def build_model_profiles(meta: pd.DataFrame, traits45: list[str], traits12: list[str]) -> dict:
    frozen = pd.read_csv(CONSENSUS_TRAITS)
    frozen = frozen.loc[frozen["consensus_family_id"].isin(PRIMARY_FAMILIES)].copy()
    if frozen[["consensus_family_id", "model", "trait"]].duplicated().any():
        raise ValueError("Duplicate frozen family/model/trait rows")
    if len(frozen) != 4 * 3 * 240:
        raise ValueError("Primary frozen family trait table is incomplete")

    parts = [frozen]
    for model, profile_id in E_COMPONENTS.items():
        source = pd.read_csv(MODEL_BANK / model / "trait_profiles.csv")
        e = source.loc[source["profile_id"].eq(profile_id), ["model", "K", "profile_id", "trait", "within_model_standardized_score"]].copy()
        if len(e) != 240 or e["trait"].nunique() != 240:
            raise ValueError(f"Incomplete frozen E component {profile_id}")
        e = e.rename(columns={"profile_id": "supporting_clusters", "within_model_standardized_score": "mean_within_model_z"})
        e["consensus_family_id"] = "MFamily_E"
        e["supporting_role_count"] = {"qwen": 3, "llama": 3, "gemma": 4}[model]
        e["evidence_role"] = "secondary frozen cross-resolution developmental recurrence"
        parts.append(e[frozen.columns])
    all_profiles = pd.concat(parts, ignore_index=True)

    direct = all_profiles.loc[all_profiles["trait"].isin(traits45)].copy()
    if direct.shape[0] != 5 * 3 * 45:
        raise ValueError(f"Expected 675 family/model/direct-trait rows, found {len(direct)}")
    pivot = direct.pivot(index=["consensus_family_id", "trait"], columns="model", values="mean_within_model_z").reset_index()
    if pivot[MODEL_ORDER].isna().any().any():
        raise ValueError("Missing model-specific family trait values")
    pivot["three_model_consensus_value"] = pivot[MODEL_ORDER].mean(axis=1)
    components = (
        direct.groupby(["consensus_family_id", "trait"], sort=True)["supporting_clusters"]
        .agg(lambda x: ";".join(f"{m}:{v}" for m, v in zip(MODEL_ORDER, x)))
        .reset_index(name="model_components")
    )
    # Reconstruct components deterministically because group row order need not be model order.
    comp_map = direct.pivot(index=["consensus_family_id", "trait"], columns="model", values="supporting_clusters").reset_index()
    comp_map["model_components"] = comp_map.apply(
        lambda r: ";".join(f"{m}:{r[m]}" for m in MODEL_ORDER), axis=1
    )
    out = pivot.merge(comp_map[["consensus_family_id", "trait", "model_components"]], on=["consensus_family_id", "trait"], validate="one_to_one")
    out = out.merge(meta, on="trait", validate="many_to_one")
    out = out.rename(columns={"consensus_family_id": "family_id", "qwen": "qwen_value", "llama": "llama_value", "gemma": "gemma_value"})
    out["analysis_role"] = np.where(out["family_id"].isin(PRIMARY_FAMILIES), "primary_A-D", "secondary_E")
    out = out.sort_values(["family_id", "trait"])
    out.to_csv(OUT / "model_family_trait_profiles_45.csv", index=False, float_format="%.12g")
    out12 = out.loc[out["trait"].isin(traits12)].copy()
    if len(out12) != 5 * 12:
        raise ValueError("Model 12-trait profile dimensions are incorrect")
    out12.to_csv(OUT / "model_family_trait_profiles_12.csv", index=False, float_format="%.12g")
    return {
        "model_families": 5,
        "primary_model_families": PRIMARY_FAMILIES,
        "secondary_model_families": ["MFamily_E"],
        "model_profile_rows_45": len(out),
        "model_profile_rows_12": len(out12),
        "mfamily_e_components": E_COMPONENTS,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    scoring, meta, traits45, traits12 = direct_metadata()
    raw_path = find_raw_sapa()
    human_summary = build_human_profiles(raw_path, scoring, meta, traits45, traits12)
    model_summary = build_model_profiles(meta, traits45, traits12)
    sources = [HUMAN_BANK, HUMAN_SUMMARY, BRIDGE, SCORING, SUPPORT, ITEM_DICTIONARY, CONSENSUS_TRAITS, SOURCE_MANIFEST]
    manifest = {
        "stage": "common_space_representations_only_no_correspondence",
        "date": "2026-09-13",
        "model_used": "GPT-5.5",
        "human_method_freeze": "6b2e460f19efca5d4dbb47487461790651d34208",
        "human_numerical_freeze": "f0e55723eacc16730d4d9184bcb8bb9868458fb0",
        "crossmodel_reconciliation_final": "c8383931fcaf4847b67fb178fd9ffd825f42e2f7",
        "direct_traits": traits45,
        "supported_traits_12": traits12,
        "eligible_primary_k": sorted(ELIGIBLE_K),
        "human_normalization": "observed-only item mean and ddof=1 SD; frozen sign; equal item weights",
        "model_normalization": "frozen within-model role-level trait z scores aggregated to frozen families; simple three-model mean",
        "human": human_summary,
        "model": model_summary,
        "source_hashes": {str(p.relative_to(ROOT)): sha256(p) for p in sources},
        "privacy": "aggregate outputs only; no respondent IDs, rows, masks, posteriors, scores, or imputations saved",
        "correspondence_calculated": False,
    }
    (OUT / "common_space_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"human": human_summary, "model": model_summary, "traits12": traits12}, indent=2))


if __name__ == "__main__":
    main()
