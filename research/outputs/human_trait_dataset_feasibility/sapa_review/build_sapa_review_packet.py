#!/usr/bin/env python3
"""Build the frozen coordinate-blind review packets for original SAPA Category-3 links."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path


SEED = 20260911
EXPECTED_SOURCE_CROSSWALK_SHA256 = "4000593255646b75e509a0e1e194dec52fd3770b58503b3df0d3388bd53d6d37"
FROZEN_GENERATED_AT = "2026-09-11T22:35:00Z"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    base = repo / "research/outputs/human_trait_dataset_feasibility"
    sapa = base / "sapa"
    out = base / "sapa_review"
    out.mkdir(parents=True, exist_ok=True)

    crosswalk_path = sapa / "sapa_model_trait_candidate_crosswalk.csv"
    item_path = sapa / "sapa_item_dictionary.csv"
    scale_path = sapa / "sapa_scale_inventory.csv"
    trait_path = repo / "data/traits/trait_list.json"
    rubric_path = out / "sapa_category3_review_rubric.md"

    assert sha256(crosswalk_path) == EXPECTED_SOURCE_CROSSWALK_SHA256, "Original feasibility crosswalk changed"
    crosswalk = read_csv(crosswalk_path)
    items = {row["item_id"]: row for row in read_csv(item_path)}
    scales = {row["scale_id"]: row for row in read_csv(scale_path)}
    canonical_traits = json.loads(trait_path.read_text(encoding="utf-8"))

    selected = [row for row in crosswalk if row["coverage_category"] == "3"]
    assert len(selected) == 78
    assert len({row["model_trait"] for row in selected}) == 78

    rng = random.Random(SEED)
    rng.shuffle(selected)
    csv_rows: list[dict[str, str]] = []
    json_rows: list[dict[str, object]] = []
    for index, source in enumerate(selected, 1):
        trait = source["model_trait"]
        assert canonical_traits[trait] == source["canonical_definition"]
        item_ids = [value for value in source["accepted_evidence_item_ids"].split(";") if value]
        assert item_ids and len(item_ids) == len(set(item_ids))
        evidence_items = []
        scale_ids: list[str] = []
        for item_id in item_ids:
            item = items[item_id]
            memberships = [value for value in item["source_scale_memberships"].split(";") if value]
            scale_ids.extend(memberships)
            evidence_items.append(
                {
                    "item_id": item_id,
                    "exact_wording": item["item_text"],
                    "response_anchors": item["response_anchors"],
                    "source_scale_memberships": memberships,
                    "derived_scoring_keys": [value for value in item["derived_scoring_keys"].split(";") if value],
                    "reverse_keyed_in_derived_scales": [
                        value for value in item["reverse_keyed_in_derived_scales"].split(";") if value
                    ],
                }
            )
        scale_ids = list(dict.fromkeys(scale_ids))
        scale_metadata = []
        for scale_id in scale_ids:
            assert scale_id in scales
            scale = scales[scale_id]
            scale_metadata.append(
                {
                    "scale_id": scale_id,
                    "instrument": scale["instrument"],
                    "scale_name": scale["scale_name"],
                    "item_count": int(scale["item_count"]),
                    "primary_definition": "not supplied in the release inventory; exact item wording governs review",
                }
            )
        review_id = f"SAPA-C3-{index:03d}"
        record = {
            "review_id": review_id,
            "trait": trait,
            "canonical_definition": source["canonical_definition"],
            "evidence_item_ids": ";".join(item_ids),
            "exact_sapa_item_wording": " | ".join(
                f'{item["item_id"]}: {item["exact_wording"]}' for item in evidence_items
            ),
            "evidence_scale_names": ";".join(scale_ids),
            "item_scoring_direction_metadata": source["wording_direction"],
            "single_or_multi_item": "single_item" if len(item_ids) == 1 else "multi_item",
            "response_anchors": " | ".join(
                f'{item["item_id"]}: {item["response_anchors"]}' for item in evidence_items
            ),
            "reverse_keying_metadata": " | ".join(
                f'{item["item_id"]}: {";".join(item["reverse_keyed_in_derived_scales"]) or "none documented"}'
                for item in evidence_items
            ),
            "sapa_scale_metadata": json.dumps(scale_metadata, ensure_ascii=False, separators=(",", ":")),
        }
        csv_rows.append(record)
        json_rows.append(
            {
                "review_id": review_id,
                "trait": trait,
                "canonical_definition": source["canonical_definition"],
                "evidence_items": evidence_items,
                "evidence_scales": scale_metadata,
                "item_scoring_direction_metadata": source["wording_direction"],
                "single_or_multi_item": record["single_or_multi_item"],
            }
        )

    fields = list(csv_rows[0])
    packet_csv = out / "sapa_category3_blinded_review_packet.csv"
    packet_json = out / "sapa_category3_blinded_review_packet.json"
    external_csv = out / "sapa_category3_external_review_packet.csv"
    write_csv(packet_csv, csv_rows, fields)
    write_csv(external_csv, csv_rows, fields)
    packet_json.write_text(
        json.dumps(
            {
                "packet_version": "1.0",
                "review_type": "coordinate-blind second-pass semantic review",
                "random_seed": SEED,
                "row_count": len(json_rows),
                "generated_at": FROZEN_GENERATED_AT,
                "rows": json_rows,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    forbidden_substrings = [
        "coverage_category",
        "coverage_label",
        "review_status",
        "top_semantic_score",
        "persona",
        "pc1",
        "pc2",
        "pc3",
        "coefficient",
        "occupation",
        "nlsy",
    ]
    packet_headers = set(csv_rows[0])
    assert not packet_headers.intersection(
        {"coverage_category", "coverage_label", "review_status", "top_semantic_score", "evidence_text"}
    )
    header_text = " ".join(packet_headers).lower()
    assert all(term not in header_text for term in forbidden_substrings)

    source_manifest = {
        "artifact": "SAPA Category-3 frozen blinded review packet",
        "packet_version": "1.0",
        "review_type": "coordinate-blind second-pass semantic review",
        "model_used_for_later_second_pass_review": "GPT-5.5",
        "random_seed": SEED,
        "selection_rule": "Exactly the 78 rows labeled coverage_category=3 in the immutable AA-1 feasibility crosswalk.",
        "reviewer_packet_excludes": [
            "original category and confidence fields",
            "persona identities and data",
            "PC coordinates and trait-PC correlations",
            "predictor coefficients and trait ranks",
            "trait sparsity results",
            "occupation and NLSY97 data",
            "all downstream correspondence results",
        ],
        "sources": {
            str(crosswalk_path.relative_to(repo)): sha256(crosswalk_path),
            str(item_path.relative_to(repo)): sha256(item_path),
            str(scale_path.relative_to(repo)): sha256(scale_path),
            str(trait_path.relative_to(repo)): sha256(trait_path),
            str(rubric_path.relative_to(repo)): sha256(rubric_path),
        },
        "frozen_outputs": {
            str(packet_csv.relative_to(repo)): sha256(packet_csv),
            str(packet_json.relative_to(repo)): sha256(packet_json),
            str(external_csv.relative_to(repo)): sha256(external_csv),
        },
        "original_category3_count": 78,
        "no_human_to_model_projection": True,
        "external_model_api_used": False,
        "new_model_inference_used": False,
        "generated_at": FROZEN_GENERATED_AT,
    }
    (out / "sapa_review_source_manifest.json").write_text(
        json.dumps(source_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(json.dumps({"status": "PASS", "row_count": 78, "seed": SEED, "packet_sha256": sha256(packet_csv)}, indent=2))


if __name__ == "__main__":
    main()
