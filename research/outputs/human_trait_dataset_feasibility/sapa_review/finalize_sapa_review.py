#!/usr/bin/env python3
"""Finalize the provisional SAPA bridge and aggregate evidence audits."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


GENERATED_AT = "2026-09-11T22:40:00Z"
VALID_DECISIONS = {"ACCEPT_DIRECT", "ACCEPT_CLOSE", "DOWNGRADE_BROAD", "REJECT", "AMBIGUOUS"}
RETAINED_DECISIONS = {"ACCEPT_DIRECT", "ACCEPT_CLOSE"}
PACKET_FREEZE_COMMIT = "4440ba0bda44517b63c8b4f05505b98651863ba9"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def distribution(values: np.ndarray) -> dict[str, float | int]:
    return {
        "mean": round(float(values.mean()), 6),
        "median": round(float(np.median(values)), 6),
        "min": int(values.min()),
        "p05": round(float(np.percentile(values, 5)), 6),
        "p25": round(float(np.percentile(values, 25)), 6),
        "p75": round(float(np.percentile(values, 75)), 6),
        "p95": round(float(np.percentile(values, 95)), 6),
        "max": int(values.max()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    base = repo / "research/outputs/human_trait_dataset_feasibility"
    sapa = base / "sapa"
    out = base / "sapa_review"
    packet_path = out / "sapa_category3_blinded_review_packet.csv"
    review_path = out / "sapa_category3_second_pass_review.csv"
    item_path = sapa / "sapa_item_dictionary.csv"
    scale_path = sapa / "sapa_scale_inventory.csv"
    crosswalk_path = sapa / "sapa_model_trait_candidate_crosswalk.csv"
    raw_path = repo / "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/sapaTempData696items08dec2013thru26jul2014.tab"

    packet_rows = read_csv(packet_path)
    review_rows = read_csv(review_path)
    items = {row["item_id"]: row for row in read_csv(item_path)}
    scales = {row["scale_id"]: row for row in read_csv(scale_path)}
    packet = {row["review_id"]: row for row in packet_rows}
    reviews = {row["review_id"]: row for row in review_rows}
    assert len(packet_rows) == len(packet) == len(review_rows) == len(reviews) == 78
    assert list(packet) == [row["review_id"] for row in review_rows]
    assert set(row["decision"] for row in review_rows) <= VALID_DECISIONS
    for review_id, review in reviews.items():
        assert review["trait"] == packet[review_id]["trait"]
        ids = [value for value in review["evidence_item_ids"].split(";") if value]
        packet_ids = set(packet[review_id]["evidence_item_ids"].split(";"))
        assert ids and set(ids) <= packet_ids
        assert all(item_id in items for item_id in ids)
        scale_ids = [value for value in review["evidence_scale_names"].split(";") if value]
        assert all(scale_id in scales for scale_id in scale_ids)

    retained = [row for row in review_rows if row["decision"] in RETAINED_DECISIONS]
    item_to_traits: dict[str, list[tuple[str, str]]] = defaultdict(list)
    scale_to_traits: dict[str, list[tuple[str, str]]] = defaultdict(list)
    scale_to_items: dict[str, set[str]] = defaultdict(set)
    for review in retained:
        for item_id in review["evidence_item_ids"].split(";"):
            item_to_traits[item_id].append((review["trait"], review["decision"]))
        for scale_id in review["evidence_scale_names"].split(";"):
            scale_to_traits[scale_id].append((review["trait"], review["decision"]))
            scale_items = set(scales[scale_id]["item_ids"].split(";"))
            scale_to_items[scale_id].update(scale_items.intersection(item_to_traits))

    source_hashes = {
        "original_crosswalk": sha256(crosswalk_path),
        "item_dictionary": sha256(item_path),
        "scale_inventory": sha256(scale_path),
        "blinded_packet": sha256(packet_path),
        "frozen_rubric": sha256(out / "sapa_category3_review_rubric.md"),
        "second_pass_review": sha256(review_path),
    }
    source_hashes_text = json.dumps(source_hashes, sort_keys=True, separators=(",", ":"))

    bridge_rows: list[dict[str, object]] = []
    for review in retained:
        packet_row = packet[review["review_id"]]
        item_ids = review["evidence_item_ids"].split(";")
        missingness = [
            {
                "item_id": item_id,
                "valid_response_n": int(items[item_id]["valid_response_n"]),
                "missing_fraction": float(items[item_id]["missing_fraction"]),
            }
            for item_id in item_ids
        ]
        bridge_rows.append(
            {
                "trait": review["trait"],
                "canonical_definition": packet_row["canonical_definition"],
                "review_decision": review["decision"],
                "bridge_tier": "primary_direct" if review["decision"] == "ACCEPT_DIRECT" else "secondary_close",
                "sapa_item_ids": ";".join(item_ids),
                "sapa_exact_wording": " | ".join(f"{item_id}: {items[item_id]['item_text']}" for item_id in item_ids),
                "source_scales": review["evidence_scale_names"],
                "scoring_direction": review["reverse_direction_issue"],
                "item_count": len(item_ids),
                "planned_missingness_information": json.dumps(missingness, separators=(",", ":")),
                "source_hashes": source_hashes_text,
                "review_status": "provisional_v1_pending_independent_external_review",
            }
        )
    write_csv(out / "sapa_trait_bridge_provisional_v1.csv", bridge_rows, list(bridge_rows[0]))

    item_reuse_rows: list[dict[str, object]] = []
    for item_id, trait_decisions in item_to_traits.items():
        traits = [trait for trait, _ in trait_decisions]
        decision_counts = Counter(decision for _, decision in trait_decisions)
        item_reuse_rows.append(
            {
                "item_id": item_id,
                "item_text": items[item_id]["item_text"],
                "retained_model_trait_count": len(traits),
                "retained_traits": ";".join(sorted(traits)),
                "accept_direct_count": decision_counts["ACCEPT_DIRECT"],
                "accept_close_count": decision_counts["ACCEPT_CLOSE"],
                "source_scale_memberships": items[item_id]["source_scale_memberships"],
                "valid_response_n": int(items[item_id]["valid_response_n"]),
                "missing_fraction": items[item_id]["missing_fraction"],
            }
        )
    item_reuse_rows.sort(key=lambda row: (-int(row["retained_model_trait_count"]), str(row["item_id"])))
    write_csv(out / "sapa_bridge_item_reuse_audit.csv", item_reuse_rows, list(item_reuse_rows[0]))

    scale_reuse_rows: list[dict[str, object]] = []
    for scale_id, trait_decisions in scale_to_traits.items():
        unique_trait_decisions = list(dict.fromkeys(trait_decisions))
        traits = [trait for trait, _ in unique_trait_decisions]
        decision_counts = Counter(decision for _, decision in unique_trait_decisions)
        evidence_items = sorted(
            item_id
            for item_id in item_to_traits
            if scale_id in items[item_id]["source_scale_memberships"].split(";")
        )
        scale_reuse_rows.append(
            {
                "scale_id": scale_id,
                "instrument": scales[scale_id]["instrument"],
                "scale_name": scales[scale_id]["scale_name"],
                "retained_model_trait_count": len(traits),
                "retained_traits": ";".join(sorted(traits)),
                "accept_direct_count": decision_counts["ACCEPT_DIRECT"],
                "accept_close_count": decision_counts["ACCEPT_CLOSE"],
                "retained_evidence_item_count": len(evidence_items),
                "retained_evidence_item_ids": ";".join(evidence_items),
            }
        )
    scale_reuse_rows.sort(key=lambda row: (-int(row["retained_model_trait_count"]), str(row["scale_id"])))
    write_csv(out / "sapa_bridge_scale_reuse_audit.csv", scale_reuse_rows, list(scale_reuse_rows[0]))

    unique_item_ids = sorted(item_to_traits)
    raw = pd.read_csv(raw_path, sep="\t", usecols=unique_item_ids)
    valid = raw.ge(1) & raw.le(6)
    raw_valid_counts = valid.sum(axis=0).astype(int).to_dict()
    for item_id in unique_item_ids:
        assert raw_valid_counts[item_id] == int(items[item_id]["valid_response_n"])
    respondent_item_counts = valid.sum(axis=1).to_numpy(dtype=int)
    complete_all_n = int(valid.all(axis=1).sum())
    any_item_n = int(valid.any(axis=1).sum())
    matrix = valid.to_numpy(dtype=np.int32)
    overlap = matrix.T @ matrix
    off_diagonal = overlap[np.triu_indices_from(overlap, k=1)]

    trait_availability = []
    for review in retained:
        trait_items = review["evidence_item_ids"].split(";")
        trait_valid = valid[trait_items]
        trait_availability.append(
            {
                "trait": review["trait"],
                "review_decision": review["decision"],
                "item_count": len(trait_items),
                "all_retained_items_observed_n": int(trait_valid.all(axis=1).sum()),
                "at_least_one_retained_item_observed_n": int(trait_valid.any(axis=1).sum()),
            }
        )

    missingness = {
        "retained_trait_count": len(retained),
        "retained_unique_item_count": len(unique_item_ids),
        "respondent_count": len(valid),
        "per_item_valid_response_n": raw_valid_counts,
        "respondent_retained_items_observed": distribution(respondent_item_counts),
        "respondents_with_any_retained_item_n": any_item_n,
        "respondents_with_all_retained_items_n": complete_all_n,
        "respondents_with_all_retained_items_fraction": round(complete_all_n / len(valid), 8),
        "pairwise_retained_item_overlap_n": distribution(off_diagonal),
        "trait_level_availability": trait_availability,
        "planned_missingness_interpretation": (
            "SAPA administered random item subsets. The release has no cell-level planned-versus-ordinary "
            "nonresponse flag; empty retained-item cells are therefore predominantly but not perfectly "
            "identifiable as planned missingness."
        ),
        "complete_profile_feasibility": (
            "A respondent-level complete profile across all retained evidence is not a realistic default analysis unit."
        ),
        "later_method_options_not_adjudicated": [
            "item-response modeling",
            "source-scale scoring when design overlap is adequate",
            "latent-variable estimation",
            "pairwise or partial-information methods",
        ],
        "method_selection_status": "not selected in this task",
        "generated_at": GENERATED_AT,
    }
    (out / "sapa_provisional_bridge_missingness_summary.json").write_text(
        json.dumps(missingness, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    counts = Counter(row["decision"] for row in review_rows)
    summary = {
        "original_category3_count": 78,
        "review_counts": {decision: counts[decision] for decision in sorted(VALID_DECISIONS)},
        "retained_direct_count": counts["ACCEPT_DIRECT"],
        "retained_close_secondary_count": counts["ACCEPT_CLOSE"],
        "total_retained_count": len(retained),
        "direct_coverage_of_240": round(counts["ACCEPT_DIRECT"] / 240, 8),
        "direct_count_contraction_from_original_category3": 78 - counts["ACCEPT_DIRECT"],
        "direct_count_contraction_fraction": round((78 - counts["ACCEPT_DIRECT"]) / 78, 8),
        "distinct_sapa_items_retained": len(item_reuse_rows),
        "distinct_sapa_source_scales_retained": len(scale_reuse_rows),
        "highest_item_reuse_count": max(int(row["retained_model_trait_count"]) for row in item_reuse_rows),
        "highest_scale_reuse_count": max(int(row["retained_model_trait_count"]) for row in scale_reuse_rows),
        "most_reused_items": [row for row in item_reuse_rows if int(row["retained_model_trait_count"]) == int(item_reuse_rows[0]["retained_model_trait_count"])],
        "most_reused_scales": [row for row in scale_reuse_rows if int(row["retained_model_trait_count"]) == int(scale_reuse_rows[0]["retained_model_trait_count"])],
        "review_type": "blinded second-pass semantic review",
        "independence_status": "same-workflow Codex review; not independent psychometric validation",
        "provisional_status": "pending genuinely independent external review",
        "packet_freeze_commit": PACKET_FREEZE_COMMIT,
        "source_hashes": source_hashes,
        "generated_at": GENERATED_AT,
    }
    (out / "sapa_trait_bridge_provisional_v1_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    manifest_path = out / "sapa_review_source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["packet_freeze_commit"] = PACKET_FREEZE_COMMIT
    manifest["second_pass_review"] = {
        "reviewer": "Codex GPT-5.5",
        "independence_status": "same-workflow coordinate-blind second pass; not independent psychometric validation",
        "review_input": str(packet_path.relative_to(repo)),
        "rubric": str((out / "sapa_category3_review_rubric.md").relative_to(repo)),
        "decision_file": str(review_path.relative_to(repo)),
        "reviewed_row_count": 78,
        "forbidden_downstream_information_used": False,
        "human_to_model_projection_performed": False,
    }
    generated_paths = [
        review_path,
        out / "sapa_trait_bridge_provisional_v1.csv",
        out / "sapa_trait_bridge_provisional_v1_summary.json",
        out / "sapa_bridge_item_reuse_audit.csv",
        out / "sapa_bridge_scale_reuse_audit.csv",
        out / "sapa_provisional_bridge_missingness_summary.json",
    ]
    manifest["second_pass_sources"] = source_hashes
    manifest["second_pass_outputs"] = {
        str(path.relative_to(repo)): sha256(path) for path in generated_paths
    }
    manifest["second_pass_generated_at"] = GENERATED_AT
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
