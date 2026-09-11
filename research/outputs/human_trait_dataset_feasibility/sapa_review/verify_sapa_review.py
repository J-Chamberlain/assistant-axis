#!/usr/bin/env python3
"""Deterministically verify the integrated AA-1 audit and Phase-1b SAPA review."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import subprocess
from collections import Counter
from pathlib import Path


GENERATED_AT = "2026-09-11T22:41:00Z"
AA1_COMMIT = "bef5614894e39f6e5d175e24d223f521f8af126a"
CANONICAL_BASE = "6654e2e5f8914790df65038417f46a7d61202c8a"
PACKET_FREEZE_COMMIT = "4440ba0bda44517b63c8b4f05505b98651863ba9"
ORIGINAL_CROSSWALK_SHA256 = "4000593255646b75e509a0e1e194dec52fd3770b58503b3df0d3388bd53d6d37"
SEED = 20260911
VALID_DECISIONS = {"ACCEPT_DIRECT", "ACCEPT_CLOSE", "DOWNGRADE_BROAD", "REJECT", "AMBIGUOUS"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def git_bytes(repo: Path, spec: str) -> bytes:
    return subprocess.check_output(["git", "show", spec], cwd=repo)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    base = repo / "research/outputs/human_trait_dataset_feasibility"
    sapa = base / "sapa"
    out = base / "sapa_review"
    checks: dict[str, bool] = {}

    original_crosswalk = sapa / "sapa_model_trait_candidate_crosswalk.csv"
    checks["original_feasibility_crosswalk_sha_unchanged"] = sha256(original_crosswalk) == ORIGINAL_CROSSWALK_SHA256
    source_rows = read_csv(original_crosswalk)
    category3 = [row for row in source_rows if row["coverage_category"] == "3"]
    checks["source_has_exactly_78_category3"] = len(category3) == 78 and len({row["model_trait"] for row in category3}) == 78

    packet_path = out / "sapa_category3_blinded_review_packet.csv"
    packet_rows = read_csv(packet_path)
    packet_json = json.loads((out / "sapa_category3_blinded_review_packet.json").read_text(encoding="utf-8"))
    external_path = out / "sapa_category3_external_review_packet.csv"
    checks["packet_has_exactly_78_unique_rows"] = (
        len(packet_rows) == 78
        and len({row["review_id"] for row in packet_rows}) == 78
        and len({row["trait"] for row in packet_rows}) == 78
    )
    expected = category3.copy()
    random.Random(SEED).shuffle(expected)
    checks["packet_order_matches_frozen_seed"] = [row["trait"] for row in packet_rows] == [row["model_trait"] for row in expected]
    allowed_packet_fields = {
        "review_id",
        "trait",
        "canonical_definition",
        "evidence_item_ids",
        "exact_sapa_item_wording",
        "evidence_scale_names",
        "item_scoring_direction_metadata",
        "single_or_multi_item",
        "response_anchors",
        "reverse_keying_metadata",
        "sapa_scale_metadata",
    }
    forbidden_packet_fields = {
        "coverage_category",
        "coverage_label",
        "review_status",
        "evidence_text",
        "top_semantic_score",
        "persona",
        "pc1",
        "pc2",
        "pc3",
        "predictor",
        "coefficient",
        "occupation",
        "nlsy97",
    }
    headers = set(packet_rows[0])
    checks["packet_fields_are_blind_and_allowlisted"] = headers == allowed_packet_fields and not {
        header.lower() for header in headers
    }.intersection(forbidden_packet_fields)
    checks["packet_json_matches_csv_identity_and_order"] = (
        packet_json["random_seed"] == SEED
        and packet_json["row_count"] == 78
        and [row["review_id"] for row in packet_json["rows"]] == [row["review_id"] for row in packet_rows]
        and [row["trait"] for row in packet_json["rows"]] == [row["trait"] for row in packet_rows]
    )
    checks["external_packet_is_decision_free_and_identical"] = packet_path.read_bytes() == external_path.read_bytes()

    item_rows = read_csv(sapa / "sapa_item_dictionary.csv")
    scale_rows = read_csv(sapa / "sapa_scale_inventory.csv")
    item_ids = {row["item_id"] for row in item_rows}
    scale_ids = {row["scale_id"] for row in scale_rows}
    checks["packet_cites_only_existing_items"] = all(
        set(row["evidence_item_ids"].split(";")) <= item_ids for row in packet_rows
    )
    checks["packet_cites_only_existing_scales"] = all(
        set(row["evidence_scale_names"].split(";")) <= scale_ids for row in packet_rows
    )

    reviews = read_csv(out / "sapa_category3_second_pass_review.csv")
    packet_map = {row["review_id"]: row for row in packet_rows}
    checks["all_78_rows_receive_one_valid_decision"] = (
        len(reviews) == 78
        and len({row["review_id"] for row in reviews}) == 78
        and set(row["decision"] for row in reviews) <= VALID_DECISIONS
        and [row["review_id"] for row in reviews] == [row["review_id"] for row in packet_rows]
    )
    checks["review_trait_and_evidence_are_packet_bound"] = all(
        row["review_id"] in packet_map
        and row["trait"] == packet_map[row["review_id"]]["trait"]
        and set(row["evidence_item_ids"].split(";")) <= set(packet_map[row["review_id"]]["evidence_item_ids"].split(";"))
        and set(row["evidence_scale_names"].split(";")) <= scale_ids
        for row in reviews
    )
    counts = Counter(row["decision"] for row in reviews)
    checks["review_counts_reproduce"] = counts == Counter(
        {"ACCEPT_DIRECT": 45, "ACCEPT_CLOSE": 29, "DOWNGRADE_BROAD": 1, "REJECT": 3}
    )

    bridge = read_csv(out / "sapa_trait_bridge_provisional_v1.csv")
    checks["provisional_bridge_has_only_permitted_distinct_tiers"] = (
        len(bridge) == 74
        and set(row["review_decision"] for row in bridge) == {"ACCEPT_DIRECT", "ACCEPT_CLOSE"}
        and set(row["bridge_tier"] for row in bridge) == {"primary_direct", "secondary_close"}
        and len({row["trait"] for row in bridge}) == 74
    )
    summary = json.loads((out / "sapa_trait_bridge_provisional_v1_summary.json").read_text(encoding="utf-8"))
    item_reuse = read_csv(out / "sapa_bridge_item_reuse_audit.csv")
    scale_reuse = read_csv(out / "sapa_bridge_scale_reuse_audit.csv")
    checks["reuse_summaries_reproduce"] = (
        summary["distinct_sapa_items_retained"] == len(item_reuse) == 129
        and summary["distinct_sapa_source_scales_retained"] == len(scale_reuse) == 78
        and summary["highest_item_reuse_count"] == max(int(row["retained_model_trait_count"]) for row in item_reuse) == 4
        and summary["highest_scale_reuse_count"] == max(int(row["retained_model_trait_count"]) for row in scale_reuse) == 7
    )
    missing = json.loads((out / "sapa_provisional_bridge_missingness_summary.json").read_text(encoding="utf-8"))
    checks["missingness_aggregates_reproduce_expected_core"] = (
        missing["respondent_count"] == 23679
        and missing["retained_trait_count"] == 74
        and missing["retained_unique_item_count"] == 129
        and missing["respondent_retained_items_observed"]["median"] == 13.0
        and missing["respondents_with_all_retained_items_n"] == 0
    )

    manifest = json.loads((out / "sapa_review_source_manifest.json").read_text(encoding="utf-8"))
    checks["manifest_records_freeze_and_blind_review"] = (
        manifest["packet_freeze_commit"] == PACKET_FREEZE_COMMIT
        and manifest["random_seed"] == SEED
        and manifest["second_pass_review"]["review_input"].endswith("sapa_category3_blinded_review_packet.csv")
        and manifest["second_pass_review"]["forbidden_downstream_information_used"] is False
        and manifest["second_pass_review"]["human_to_model_projection_performed"] is False
    )
    manifest_hashes_ok = True
    for relative, expected_hash in manifest["sources"].items():
        manifest_hashes_ok &= sha256(repo / relative) == expected_hash
    for relative, expected_hash in manifest["frozen_outputs"].items():
        manifest_hashes_ok &= sha256(repo / relative) == expected_hash
    for relative, expected_hash in manifest["second_pass_outputs"].items():
        manifest_hashes_ok &= sha256(repo / relative) == expected_hash
    checks["manifest_source_and_output_hashes_match"] = manifest_hashes_ok

    freeze_ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", PACKET_FREEZE_COMMIT, "HEAD"], cwd=repo, check=False
    ).returncode == 0
    freeze_contains_packet = subprocess.run(
        ["git", "cat-file", "-e", f"{PACKET_FREEZE_COMMIT}:research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_category3_review_rubric.md"],
        cwd=repo,
        check=False,
    ).returncode == 0
    freeze_contains_review = subprocess.run(
        ["git", "cat-file", "-e", f"{PACKET_FREEZE_COMMIT}:research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_category3_second_pass_review.csv"],
        cwd=repo,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0
    checks["rubric_and_packet_commit_precede_adjudication"] = freeze_ancestor and freeze_contains_packet and not freeze_contains_review

    aa1_paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", AA1_COMMIT, "research/outputs/human_trait_dataset_feasibility"],
        cwd=repo,
        text=True,
    ).splitlines()
    expected_modified = {
        "research/outputs/human_trait_dataset_feasibility/artifact_inventory.csv",
        "research/outputs/human_trait_dataset_feasibility/human_trait_dataset_feasibility_report.md",
        "research/outputs/human_trait_dataset_feasibility/verification_report.json",
    }
    unchanged = []
    for relative in aa1_paths:
        if relative not in expected_modified:
            unchanged.append((repo / relative).read_bytes() == git_bytes(repo, f"{AA1_COMMIT}:{relative}"))
    original_report = git_bytes(repo, f"{AA1_COMMIT}:research/outputs/human_trait_dataset_feasibility/human_trait_dataset_feasibility_report.md")
    current_report = (base / "human_trait_dataset_feasibility_report.md").read_bytes()
    checks["aa1_original_artifacts_preserved_with_report_addendum"] = all(unchanged) and current_report.startswith(original_report)
    checks["aa2_aa3_artifact_trees_untouched"] = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            CANONICAL_BASE,
            "--",
            "research/outputs/multimodel_trait_profile_pc_predictor",
            "research/outputs/persona_trait_surface_viewer",
            "research/outputs/persona_trait_ridge_plots",
        ],
        cwd=repo,
        check=False,
    ).returncode == 0

    tracked_raw = subprocess.check_output(["git", "ls-files", "data_external"], cwd=repo, text=True).strip()
    checks["no_respondent_level_microdata_tracked"] = tracked_raw == ""
    phase_b_csvs = sorted(out.glob("*.csv"))
    direct_id_headers = {"RID", "PUBID", "R0000100", "respondent_id", "case_id"}
    checks["no_direct_identifier_headers_in_phase_b"] = all(
        not direct_id_headers.intersection(read_csv(path)[0] if read_csv(path) else {}) for path in phase_b_csvs
    )

    parsable = True
    try:
        for path in base.rglob("*.csv"):
            list(csv.reader(path.open(newline="", encoding="utf-8")))
        for path in base.rglob("*.json"):
            json.load(path.open(encoding="utf-8"))
    except (csv.Error, json.JSONDecodeError, UnicodeDecodeError):
        parsable = False
    checks["all_human_feasibility_csv_json_parse"] = parsable

    inventory_path = base / "artifact_inventory.csv"
    inventory = read_csv(inventory_path)
    checks["artifact_inventory_hashes_match"] = all(
        (repo / row["path"]).exists()
        and str((repo / row["path"]).stat().st_size) == row["bytes"]
        and sha256(repo / row["path"]) == row["sha256"]
        for row in inventory
    )
    inventory_paths = {row["path"] for row in inventory}
    expected_inventory_paths = {
        str(path.relative_to(repo))
        for path in base.rglob("*")
        if path.is_file() and path != inventory_path and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }
    checks["artifact_inventory_is_complete"] = inventory_paths == expected_inventory_paths

    startup_manifest = (repo / "research/STARTUP_MANIFEST.md").read_text(encoding="utf-8")
    startup_ok = True
    for name in ["RESEARCH_STATE.md", "THREAD_START.md", "CLAIMS_REGISTER.md"]:
        block_match = re.search(
            rf"### `research/{re.escape(name)}`(?P<block>.*?)(?=\n### `research/|\n## Maintenance Rule)",
            startup_manifest,
            flags=re.S,
        )
        if not block_match:
            startup_ok = False
            continue
        block = block_match.group("block")
        hash_match = re.search(r"SHA256 content hash: `([0-9a-f]{64})`", block)
        bytes_match = re.search(r"Byte count: `([0-9]+)`", block)
        path = repo / "research" / name
        startup_ok &= bool(hash_match and bytes_match)
        if hash_match and bytes_match:
            startup_ok &= hash_match.group(1) == sha256(path) and int(bytes_match.group(1)) == path.stat().st_size
    checks["startup_manifest_matches_startup_files"] = startup_ok

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "review_counts": {decision: counts[decision] for decision in sorted(VALID_DECISIONS)},
        "retained": {"traits": 74, "distinct_items": 129, "distinct_scales": 78},
        "privacy": {
            "respondent_level_human_microdata_committed": False,
            "human_respondents_assigned_llm_persona": False,
            "human_to_model_pca_projection_performed": False,
        },
        "review_independence": "Codex same-workflow blinded second pass; not independent psychometric validation",
        "generated_at": GENERATED_AT,
    }
    if not args.check_only:
        (out / "sapa_review_verification_report.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit("Verification failed: " + ", ".join(name for name, passed in checks.items() if not passed))


if __name__ == "__main__":
    main()
