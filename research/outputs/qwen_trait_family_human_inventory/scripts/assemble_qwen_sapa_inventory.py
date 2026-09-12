#!/usr/bin/env python3
"""Assemble the inspectable Qwen-family to SAPA measurement inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


BLIND_SEED = 20260919
STRONG = "STRONG_FAMILY_MATCH"
PARTIAL = "PARTIAL_FAMILY_MATCH"
FACET = "FACET_OR_SUBCOMPONENT"
ITEM = "ITEM_LEVEL_ONLY"
NONE = "NO_DEFENSIBLE_MATCH"


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


def family_id_map() -> dict[tuple[str, str], str]:
    families = [(f"PC{pc}", pole) for pc in range(1, 7) for pole in ("positive", "negative")]
    shuffled = families.copy()
    random.Random(BLIND_SEED).shuffle(shuffled)
    return {family: f"FAM-{index:02d}" for index, family in enumerate(shuffled, 1)}


def best_family_status(statuses: set[str]) -> str:
    if STRONG in statuses:
        return STRONG
    if PARTIAL in statuses:
        return PARTIAL
    if FACET in statuses or ITEM in statuses:
        return FACET
    return NONE


def build(repo: Path, output: Path, generated_at: str) -> None:
    summary_path = output / "qwen_trait_family_summaries.csv"
    packet_path = output / "qwen_trait_family_blinded_mapping_packet.csv"
    judgment_path = output / "qwen_trait_family_human_mapping_judgments.csv"
    correlation_path = output / "qwen_trait_pc_correlations_all.csv"
    membership_path = output / "qwen_trait_family_membership_primary.csv"
    numeric_manifest_path = output / "numeric_source_manifest.json"
    library_path = repo / "research/outputs/qwen_pc_human_construct_bridge/human_construct_library.csv"
    library_sources_path = repo / "research/outputs/qwen_pc_human_construct_bridge/human_construct_library_sources.md"
    item_path = repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"
    correction_path = repo / "research/outputs/qwen_pc_human_construct_bridge/sapa_flagged_item_quality_audit.csv"

    summaries = pd.read_csv(summary_path).fillna("")
    packet = pd.read_csv(packet_path).fillna("")
    judgments = pd.read_csv(judgment_path).fillna("")
    membership = pd.read_csv(membership_path).fillna("")
    library = pd.read_csv(library_path).fillna("")
    items = pd.read_csv(item_path).fillna("")
    id_map = family_id_map()

    summaries["family_id"] = [id_map[(row.pc, row.pole)] for row in summaries.itertuples(index=False)]
    expected_packet_members = packet.set_index("family_id")["family_members_ordered"].to_dict()
    for row in summaries.itertuples(index=False):
        if row.ordered_member_list != expected_packet_members[row.family_id]:
            raise ValueError(f"Blind mapping key mismatch for {row.family_id}")

    family_meta: dict[str, dict[str, object]] = {}
    for family_id, group in judgments.groupby("family_id", sort=True):
        candidate_group = group[group["human_construct_id"].astype(str).str.len() > 0]
        item_union = set()
        for value in candidate_group["item_ids"]:
            item_union.update(split_ids(value))
        family_meta[family_id] = {
            "candidate_count": int(len(candidate_group)),
            "unique_item_count": len(item_union),
            "best_status": best_family_status(set(group["match_status"])),
        }

    inventory = summaries.merge(judgments, on="family_id", validate="one_to_many", suffixes=("_qwen", "_human"))
    inventory["qwen_selected_traits_with_r_json"] = inventory["ordered_member_correlations_json"]
    inventory["human_candidate_construct_count_for_family"] = inventory["family_id"].map(lambda x: family_meta[x]["candidate_count"])
    inventory["human_unique_item_count_for_family"] = inventory["family_id"].map(lambda x: family_meta[x]["unique_item_count"])
    inventory["family_level_best_match_category"] = inventory["family_id"].map(lambda x: family_meta[x]["best_status"])
    inventory["qwen_evidence_status"] = "OBSERVED_SAME_SPACE_QWEN_TRAIT_PC_ASSOCIATION"
    inventory["family_description_status"] = "INTERPRETATION_FROM_NUMERICALLY_SELECTED_TRAITS"
    inventory["human_match_status_epistemic"] = "INTERPRETATION_OF_AVAILABLE_SAPA_MEASUREMENT"
    inventory["shared_latent_property_status"] = "HYPOTHESIS_NOT_TESTED"
    inventory["human_model_quantitative_correspondence"] = "UNKNOWN_NOT_TESTED"

    columns = [
        "pc", "pole", "family_id", "primary_member_count", "ordered_member_list",
        "qwen_selected_traits_with_r_json", "strongest_correlated_trait", "second_strongest_trait",
        "third_strongest_trait", "pearson_r_min", "pearson_r_max",
        "sensitivity_member_count_abs_r_0_40", "primary_member_count_abs_r_0_50",
        "sensitivity_member_count_abs_r_0_60", "family_description",
        "human_candidate_construct_count_for_family", "human_unique_item_count_for_family",
        "family_level_best_match_category", "human_construct_id", "human_construct_name", "framework",
        "domain", "level", "match_status", "match_rationale", "covered_qwen_family_members",
        "important_uncovered_qwen_family_members", "SAPA_scale_or_key", "item_ids", "item_count",
        "item_wording_json", "measurement_direction", "library_scoring_direction", "item_valid_n_min",
        "item_valid_n_median", "item_valid_n_max", "pairwise_standardized_alpha", "reliability_note",
        "overlap_with_other_proposed_human_constructs", "substantial_item_overlap", "source_provenance",
        "qwen_evidence_status", "family_description_status", "human_match_status_epistemic",
        "shared_latent_property_status", "human_model_quantitative_correspondence",
    ]
    inventory = inventory[columns].sort_values(["pc", "pole", "match_status", "human_construct_id"], kind="mergesort")
    inventory.to_csv(output / "qwen_pc_trait_family_human_inventory.csv", index=False, lineterminator="\n")

    unique_qwen_traits = set(membership["trait"])
    candidate_rows = judgments[judgments["human_construct_id"].astype(str).str.len() > 0]
    unique_constructs = set(candidate_rows["human_construct_id"])
    unique_items: set[str] = set()
    construct_families: dict[str, set[str]] = defaultdict(set)
    item_families: dict[str, set[str]] = defaultdict(set)
    for row in candidate_rows.itertuples(index=False):
        construct_families[row.human_construct_id].add(row.family_id)
        for item_id in split_ids(row.item_ids):
            unique_items.add(item_id)
            item_families[item_id].add(row.family_id)
    family_status_counts = Counter(meta["best_status"] for meta in family_meta.values())
    construct_reuse = {key: len(value) for key, value in construct_families.items()}
    item_reuse = {key: len(value) for key, value in item_families.items()}

    summary = {
        "generated_at_utc": generated_at,
        "qwen_role_count": 275,
        "qwen_pc_count": 6,
        "family_count_including_empty_poles": 12,
        "primary_membership_rows": int(len(membership)),
        "unique_qwen_traits_selected": len(unique_qwen_traits),
        "unique_human_construct_or_item_candidates": len(unique_constructs),
        "unique_sapa_questionnaire_items_represented": len(unique_items),
        "family_level_match_category_counts": dict(sorted(family_status_counts.items())),
        "human_constructs_used_in_multiple_families": sum(value > 1 for value in construct_reuse.values()),
        "maximum_family_reuse_per_human_construct": max(construct_reuse.values(), default=0),
        "sapa_items_used_in_multiple_families": sum(value > 1 for value in item_reuse.values()),
        "maximum_family_reuse_per_sapa_item": max(item_reuse.values(), default=0),
        "most_reused_human_constructs": [
            {"human_construct_id": key, "family_count": value, "families": sorted(construct_families[key])}
            for key, value in sorted(construct_reuse.items(), key=lambda pair: (-pair[1], pair[0])) if value > 1
        ],
        "families": {
            row.family_id: {
                "pc": row.pc,
                "pole": row.pole,
                "qwen_member_count": int(row.primary_member_count),
                "human_candidate_count": family_meta[row.family_id]["candidate_count"],
                "human_unique_item_count": family_meta[row.family_id]["unique_item_count"],
                "best_match_category": family_meta[row.family_id]["best_status"],
            }
            for row in summaries.itertuples(index=False)
        },
    }
    (output / "inventory_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )

    report = [
        "# Qwen PC trait-family → SAPA human-measurement inventory",
        "",
        "**Requested stopping point:** this report inventories SAPA measurements proposed to represent mechanically selected Qwen trait families. It does not score respondents, test correspondence, compare models, or select a next experiment.",
        "",
        "## Inventory overview",
        "",
        f"Across PC1-PC6, the frozen primary rule yields {len(membership)} PC-family memberships involving {len(unique_qwen_traits)} unique Qwen traits. The blind SAPA review identifies {len(unique_constructs)} unique construct/item candidates using {len(unique_items)} unique SAPA questionnaire items. Family-level best-match counts are " + ", ".join(f"{key}={value}" for key, value in sorted(family_status_counts.items())) + ".",
        "",
        "The exact/display wording for every item in every proposed counterpart is preserved in `qwen_pc_trait_family_human_inventory.csv`. To keep this report readable, each construct below shows its complete item-ID list and up to five wording examples; the CSV is exhaustive.",
        "",
        "| PC | Pole | Qwen traits | Strongest anchor | SAPA candidates | Unique SAPA items | Best available match |",
        "|---|---|---:|---|---:|---:|---|",
    ]
    summary_lookup = summaries.set_index(["pc", "pole"])
    for pc in [f"PC{i}" for i in range(1, 7)]:
        for pole in ("positive", "negative"):
            row = summary_lookup.loc[(pc, pole)]
            family_id = row.family_id
            report.append(f"| {pc} | {pole} | {int(row.primary_member_count)} | {row.strongest_correlated_trait or '—'} | {family_meta[family_id]['candidate_count']} | {family_meta[family_id]['unique_item_count']} | {family_meta[family_id]['best_status']} |")
    report.append("")

    for pc in [f"PC{i}" for i in range(1, 7)]:
        for pole in ("positive", "negative"):
            family = summary_lookup.loc[(pc, pole)]
            family_id = family.family_id
            report.extend([
                f"## {pc} {pole} — {family_id}",
                "",
                "### Qwen side",
                "",
                f"Observed selected-trait count: {int(family.primary_member_count)}. Strongest anchors: " + ", ".join(x for x in [family.strongest_correlated_trait, family.second_strongest_trait, family.third_strongest_trait] if x) + ("." if family.primary_member_count else "None."),
                "",
            ])
            evidence = json.loads(family.ordered_member_correlations_json) if family.ordered_member_correlations_json else []
            if evidence:
                report.append("Complete ordered family: " + "; ".join(f"{item['trait']} (r={item['pearson_r']:+.3f})" for item in evidence) + ".")
            else:
                report.append("Complete ordered family: empty under the frozen rule.")
            report.extend([
                "",
                "Interpretive description: " + family.family_description,
                "",
                f"Sensitivity sizes: |r| >= .40: {int(family.sensitivity_member_count_abs_r_0_40)}; primary |r| >= .50: {int(family.primary_member_count_abs_r_0_50)}; |r| >= .60: {int(family.sensitivity_member_count_abs_r_0_60)}.",
                "",
                "### Human side",
                "",
            ])
            family_judgments = judgments[judgments["family_id"] == family_id]
            for human in family_judgments.itertuples(index=False):
                if not human.human_construct_id:
                    report.extend([f"- **{human.match_status}:** {human.match_rationale}", ""])
                    continue
                wording = json.loads(human.item_wording_json)
                examples = "; ".join(f"{item['item_id']} — {item['display_wording']}" for item in wording[:5])
                if len(wording) > 5:
                    examples += f"; … ({len(wording) - 5} additional exact/display wordings in the CSV)"
                report.extend([
                    f"- **{human.human_construct_name}** — {human.framework}, {human.level}, `{human.match_status}`; {int(human.item_count)} item(s).",
                    f"  Match: {human.match_rationale}",
                    f"  Coverage: {human.covered_qwen_family_members or 'none'}.",
                    f"  Important mismatch: {human.important_uncovered_qwen_family_members}",
                    f"  Direction: {human.measurement_direction}",
                    f"  Item IDs: {human.item_ids or 'none'}.",
                    f"  Wording examples: {examples or 'none'}.",
                    f"  Source: {human.source_provenance}",
                    "",
                ])

    report.extend([
        "## Reuse and overlap",
        "",
        f"Observed availability: {sum(value > 1 for value in construct_reuse.values())} proposed human constructs recur across more than one family; the maximum is {max(construct_reuse.values(), default=0)} families for one construct. {sum(value > 1 for value in item_reuse.values())} SAPA items recur across more than one family; the maximum is {max(item_reuse.values(), default=0)} families for one item. Overlap fields and pairwise construct/item reuse are explicit in the machine-readable inventory.",
        "",
        "Most reused construct IDs: " + ("; ".join(f"{entry['human_construct_id']} ({entry['family_count']} families: {', '.join(entry['families'])})" for entry in summary["most_reused_human_constructs"]) or "none") + ".",
        "",
        "## Epistemic status",
        "",
        "Observed: Qwen trait-PC correlations, frozen threshold membership, and documented SAPA construct/item availability.",
        "",
        "Interpretation: the family descriptions and proposed SAPA counterparts summarize semantic and measurement coverage of the selected traits.",
        "",
        "Hypothesis: any claim that a proposed human construct and Qwen family reflect a shared latent property.",
        "",
        "Unknown: quantitative human/model correspondence, causal relationships, respondent-level mapping, and cross-model generalization.",
        "",
        "## Mandatory stop",
        "",
        "This inventory is the requested endpoint. No human respondent was scored or projected; no Llama, Gemma, or AA-7 result was used; no human/model correspondence test was run; and no next experiment was selected.",
    ])
    (output / "qwen_pc_trait_family_human_inventory_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    source_paths = [
        summary_path, packet_path, judgment_path, correlation_path, membership_path,
        numeric_manifest_path, library_path, library_sources_path, item_path, correction_path,
        repo / "research/outputs/qwen_pc_human_construct_bridge/verification_report.json",
    ]
    manifest = {
        "analysis": "Correlation-defined Qwen trait families to SAPA human-measurement inventory",
        "generated_at_utc": generated_at,
        "canonical_master_observed_at_start": "8f4e589df5d92217e56f76a978d51df07af5aa3a",
        "aa1_validated_source_commit": "313c5cff6e071d707d37b1318343cde4ed510725",
        "branch": "codex/aa1-qwen-trait-family-human-inventory",
        "source_hashes": {str(path.relative_to(repo)): sha256(path) for path in source_paths},
        "source_counts": {
            "qwen_roles": 275,
            "qwen_traits": 240,
            "qwen_pcs": 6,
            "SAPA_construct_library": int(len(library)),
            "SAPA_item_dictionary": int(len(items)),
        },
        "selection": json.loads(numeric_manifest_path.read_text(encoding="utf-8"))["thresholds"],
        "blind_mapping": {
            "family_id_seed": BLIND_SEED,
            "packet_frozen_commit": "70f7617",
            "judgments_frozen_commit": "9c5aad1",
            "candidate_universe": "all 126 documented constructs in human_construct_library.csv plus item-level fallback where no adequate scale exists",
            "prior_hypothesis_files_used": [],
        },
        "firewall": {
            "models_used": ["Qwen/Qwen3-32B"],
            "Llama_or_Gemma_analysis_used": False,
            "AA7_result_paths_used": [],
            "prior_AA1_hypothesis_files_used": [],
            "human_respondent_rows_loaded_or_scored": False,
            "human_model_projection_performed": False,
            "next_experiment_selected": False,
        },
        "privacy": "No respondent-level human records were read for this inventory or committed.",
        "compute": "CPU only; no GPU, RunPod, model inference, activation extraction, response generation, or external model API.",
    }
    (output / "source_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--generated-at", default="2026-09-12T20:30:00Z")
    args = parser.parse_args()
    build(args.repo_root.resolve(), args.output_dir.resolve(), args.generated_at)


if __name__ == "__main__":
    main()
