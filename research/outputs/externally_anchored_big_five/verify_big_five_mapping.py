#!/usr/bin/env python3
"""Verify the frozen geometry-blind Big Five mapping artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SAPA = ROOT / "research/outputs/human_trait_dataset_feasibility"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    traits = json.loads((ROOT / "data/traits/trait_list.json").read_text(encoding="utf-8"))
    with (SAPA / "sapa_review/sapa_trait_bridge_provisional_v1.csv").open(newline="", encoding="utf-8") as handle:
        bridge_rows = list(csv.DictReader(handle))
    with (SAPA / "sapa/sapa_item_dictionary.csv").open(newline="", encoding="utf-8") as handle:
        item_ids = {row["item_id"] for row in csv.DictReader(handle)}
    with (SAPA / "sapa/sapa_scale_inventory.csv").open(newline="", encoding="utf-8") as handle:
        scale_ids = {row["scale_id"] for row in csv.DictReader(handle)}
    bridge_by_trait = {row["trait"]: row for row in bridge_rows}
    strict = rows("human_anchored_strict_trait_mapping.csv")
    extended = rows("human_anchored_extended_trait_mapping.csv")
    expanded = rows("external_taxonomy_expanded_trait_mapping.csv")
    facets = rows("external_big_five_domain_facet_reference.csv")
    manifest = json.loads((OUT / "mapping_freeze_manifest.json").read_text(encoding="utf-8"))

    checks: dict[str, object] = {}
    checks["canonical_trait_count"] = len(traits) == 240 == len(set(traits))
    checks["reviewed_bridge_counts"] = (
        len(bridge_rows) == 74
        and sum(row["review_decision"] == "ACCEPT_DIRECT" for row in bridge_rows) == 45
        and sum(row["review_decision"] == "ACCEPT_CLOSE" for row in bridge_rows) == 29
    )
    checks["strict_direct_only"] = len(strict) == 42 and all(row["sapa_review_tier"] == "ACCEPT_DIRECT" for row in strict)
    checks["extended_tier_separation"] = (
        len(extended) == 67
        and {row["trait"] for row in strict} <= {row["trait"] for row in extended}
        and {row["sapa_review_tier"] for row in extended} == {"ACCEPT_DIRECT", "ACCEPT_CLOSE"}
    )
    checks["expanded_all_240_reviewed"] = len(expanded) == 240 and {row["trait"] for row in expanded} == set(traits)
    checks["expanded_strict_inclusion"] = (
        sum(row["included_in_construction"] == "yes" for row in expanded) == 109
        and all(
            row["confidence_tier"] == "high" and row["direct_or_proxy"] == "direct"
            for row in expanded if row["included_in_construction"] == "yes"
        )
    )
    checks["canonical_definitions_exact"] = all(
        traits[row["trait"]] == row["canonical_definition"] for row in strict + extended + expanded
    )
    checks["all_human_traits_in_reviewed_bridge"] = all(
        row["trait"] in bridge_by_trait and bridge_by_trait[row["trait"]]["review_decision"] == row["sapa_review_tier"]
        for row in strict + extended
    )
    checks["all_sapa_items_exist"] = all(
        set(filter(None, row["sapa_item_ids"].split(";"))) <= item_ids for row in strict + extended
    )
    checks["all_sapa_scales_exist"] = all(
        set(filter(None, row["sapa_supporting_source_scales"].split(";"))) <= scale_ids for row in strict + extended
    )
    checks["valid_polarities"] = all(
        row["polarity"] in {"positive", "negative"}
        for row in strict + extended + [r for r in expanded if r["included_in_construction"] == "yes"]
    )
    checks["thirty_external_facets"] = len(facets) == 30 and len({row["facet_code"] for row in facets}) == 30
    forbidden = ("pc", "coordinate", "ridge", "cluster", "surface")
    checks["no_geometry_columns"] = all(
        not any(token in column.lower() for token in forbidden)
        for table in (strict, extended, expanded)
        for column in table[0]
    )
    checks["geometry_blind_manifest"] = (
        manifest["geometry_blind"] is True
        and manifest["geometry_inputs_available_to_generator"] is False
        and manifest["mapping_stage"] == "complete_before_any_new_geometry_analysis"
    )
    checks["frozen_hashes_match"] = all(
        sha256(ROOT / path) == expected for path, expected in manifest["frozen_artifacts"].items()
    )
    passed = all(bool(value) for value in checks.values())
    report = {
        "passed": passed,
        "checks": checks,
        "counts": manifest["counts"],
        "mapping_hashes": manifest["frozen_artifacts"],
        "note": "This verifier reads no persona geometry or model score data.",
    }
    (OUT / "mapping_verification_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
