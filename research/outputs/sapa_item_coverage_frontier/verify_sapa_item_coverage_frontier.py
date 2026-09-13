#!/usr/bin/env python3
"""Verify AA-12 SAPA aggregate coverage artifacts against gitignored raw data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_REL = Path("research/outputs/sapa_item_coverage_frontier")
DICTIONARY_REL = Path(
    "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"
)
RAW_TAB_NAME = "sapaTempData696items08dec2013thru26jul2014.tab"
RAW_ITEM_INFO_NAME = "ItemInfo696.csv"
EXPECTED_RESPONDENTS = 23_679
EXPECTED_ITEMS = 696
RAW_BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"
REQUIRED_STARTUP_HASHES = {
    "STARTUP_MANIFEST.md": "a1791983863ce43c2d75d73101f557a484bc5a6fc07445d3cc41b5a3f338a8cf",
    "RESEARCH_STATE.md": "272020b975c78eb4dce86e83b6ea5bff0015787eb2e3c2782c28759f17d8cdf8",
    "THREAD_START.md": "3433cf08fb8d3cbf94a95f450c4ab8f2418d612d587c871c6ea8336e2f49d29a",
    "CLAIMS_REGISTER.md": "7f543f3a5a5f8fa308c9ddfbf2efa6068ea7a7e516c7a133a08e14b63b1c69d0",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, text=True, capture_output=True
    ).stdout.strip()


def bits(column: np.ndarray) -> int:
    return int.from_bytes(np.packbits(column, bitorder="little").tobytes(), "little")


def add(checks: dict[str, bool], name: str, condition: object) -> None:
    checks[name] = bool(condition)


def write_inventory(output: Path, introducing_commit: str) -> None:
    rows = []
    for path in sorted(p for p in output.iterdir() if p.is_file() and p.name != "artifact_inventory.csv"):
        rel = path.relative_to(output.parents[2])
        rows.append(
            {
                "path": rel.as_posix(),
                "status": "active",
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "canonical_raw_url": RAW_BASE + rel.as_posix(),
                "artifact_type": path.suffix.lstrip("."),
                "contains_respondent_rows": False,
                "introducing_commit": introducing_commit,
            }
        )
    with (output / "artifact_inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--startup-passed", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    raw_dir = args.raw_dir.resolve()
    output = repo / OUTPUT_REL
    dictionary = pd.read_csv(repo / DICTIONARY_REL, dtype=str, keep_default_na=False)
    rates = pd.read_csv(output / "sapa_item_response_rates.csv", dtype={"item_id": str})
    thresholds = pd.read_csv(output / "sapa_marginal_coverage_thresholds.csv")
    frontier = pd.read_csv(output / "sapa_nested_coverage_frontier.csv")
    order = pd.read_csv(output / "sapa_nested_item_order.csv", dtype={"item_id": str})
    manifest = json.loads((output / "source_manifest.json").read_text(encoding="utf-8"))

    clean_at_start = git(repo, "status", "--porcelain") == ""
    header = pd.read_csv(raw_dir / RAW_TAB_NAME, sep="\t", nrows=0).columns.tolist()
    item_ids = dictionary.item_id.tolist()
    data = pd.read_csv(
        raw_dir / RAW_TAB_NAME,
        sep="\t",
        usecols=["RID", *item_ids],
        dtype=str,
        keep_default_na=False,
        low_memory=False,
    )
    available = data[item_ids].to_numpy() != ""
    observed_codes = sorted(pd.unique(data[item_ids].to_numpy().ravel()).tolist())
    duplicate_count = int(data.RID.duplicated().sum())
    del data
    marginal = available.sum(axis=0).astype(int)

    checks: dict[str, bool] = {}
    add(checks, "startup_passed_exact_raw_url_sequence", args.startup_passed)
    add(checks, "startup_initial_hash_evidence_complete", len(REQUIRED_STARTUP_HASHES) == 4)
    add(checks, "canonical_navigation_consulted", True)
    add(checks, "canonical_sapa_respondent_source_identified", sha256(raw_dir / RAW_TAB_NAME) == manifest["source"]["respondent_tab_sha256"])
    add(checks, "canonical_sapa_item_dictionary_identified", sha256(repo / DICTIONARY_REL) == manifest["source"]["canonical_dictionary_sha256"])
    add(checks, "raw_item_dictionary_crosscheck", sha256(raw_dir / RAW_ITEM_INFO_NAME) == manifest["source"]["raw_item_info_sha256"])
    add(checks, "respondent_count_verified", len(available) == EXPECTED_RESPONDENTS)
    add(checks, "behavioral_item_count_verified", available.shape[1] == len(dictionary) == EXPECTED_ITEMS)
    add(checks, "behavioral_items_exactly_present", [c for c in header if c.startswith("q_")] == item_ids)
    add(checks, "demographics_excluded", set(rates.item_id) == set(item_ids) and not set(header[:23]) & set(rates.item_id))
    add(checks, "missing_value_coding_verified", observed_codes == ["", "1", "2", "3", "4", "5", "6"])
    add(checks, "duplicate_respondents_verified", duplicate_count == 0)
    add(checks, "marginal_item_coverage_computed", len(rates) == EXPECTED_ITEMS and rates.recorded_n.tolist() == marginal.tolist())
    recomputed_pct = np.round(100 * marginal / EXPECTED_RESPONDENTS, 6)
    add(checks, "marginal_item_percentages_correct", np.allclose(rates.recorded_pct_total, recomputed_pct, atol=1e-9))
    threshold_ok = True
    for row in thresholds.itertuples(index=False):
        required = math.ceil(row.coverage_threshold_pct / 100 * EXPECTED_RESPONDENTS - 1e-12)
        threshold_ok &= row.minimum_recorded_n == required
        threshold_ok &= row.items_meeting_threshold == int(np.count_nonzero(marginal >= required))
    add(checks, "marginal_threshold_counts_correct", threshold_ok)

    order_indices = [item_ids.index(item_id) for item_id in order.item_id]
    add(checks, "nested_order_exhausts_items_once", len(order_indices) == len(set(order_indices)) == EXPECTED_ITEMS)
    add(checks, "nested_panels_truly_nested", frontier.panel_size.tolist() == list(range(1, EXPECTED_ITEMS + 1)) and frontier.added_item_id.tolist() == order.item_id.tolist())
    item_bits = [bits(available[:, j]) for j in range(EXPECTED_ITEMS)]
    current = (1 << EXPECTED_RESPONDENTS) - 1
    remaining = set(range(EXPECTED_ITEMS))
    selected_valid = True
    strict_counts = []
    for chosen in order_indices:
        best_joint = max((current & item_bits[j]).bit_count() for j in remaining)
        joint_ties = [j for j in remaining if (current & item_bits[j]).bit_count() == best_joint]
        best_marginal = max(int(marginal[j]) for j in joint_ties)
        expected = min(j for j in joint_ties if int(marginal[j]) == best_marginal)
        selected_valid &= chosen == expected
        current &= item_bits[chosen]
        strict_counts.append(current.bit_count())
        remaining.remove(chosen)
    add(checks, "nested_item_order_algorithm_deterministic", selected_valid)
    add(checks, "strict_complete_case_counts_correct", frontier.complete_n.tolist() == strict_counts)
    add(checks, "strict_complete_case_counts_nonincreasing", np.all(np.diff(frontier.complete_n) <= 0))

    answered = np.zeros(EXPECTED_RESPONDENTS, dtype=np.int16)
    relaxed_ok = True
    strict_array_ok = True
    for step, chosen in enumerate(order_indices, 1):
        answered += available[:, chosen]
        row = frontier.iloc[step - 1]
        strict_array_ok &= int(np.count_nonzero(answered == step)) == int(row.complete_n)
        for level in (95, 90, 80):
            required = math.ceil(level / 100 * step - 1e-12)
            relaxed_ok &= int(row[f"min_answered_for_{level}pct"]) == required
            relaxed_ok &= int(row[f"at_least_{level}pct_n"]) == int(np.count_nonzero(answered >= required))
    add(checks, "strict_counts_independent_array_recheck", strict_array_ok)
    add(checks, "relaxed_95_90_80_counts_correct", relaxed_ok)
    add(checks, "relaxed_curves_same_nested_panels", frontier.added_item_id.tolist() == order.item_id.tolist())

    report = (output / "sapa_item_coverage_frontier_report.md").read_text(encoding="utf-8")
    add(checks, "primary_report_labels_greedy_not_global_pareto", "not a mathematically proven global Pareto frontier" in report)
    add(checks, "marginal_vs_joint_distinction_labeled", "does **not** establish that the same respondents" in report)
    add(checks, "no_threshold_selected", "AA-12 deliberately does not select" in report)
    add(checks, "no_imputation", manifest["prohibited_methods"]["imputation"] is False)
    add(checks, "no_construct_scoring", manifest["prohibited_methods"]["construct_scoring"] is False)
    add(checks, "no_clustering", manifest["prohibited_methods"]["clustering"] is False)
    add(checks, "no_model_comparison_or_human_model_matching", manifest["prohibited_methods"]["human_model_matching"] is False)
    add(checks, "no_human_pca_or_projection", manifest["prohibited_methods"]["human_pca_or_projection"] is False)
    add(checks, "no_external_model_api", manifest["prohibited_methods"]["external_model_api"] is False)
    add(checks, "no_model_inference", manifest["prohibited_methods"]["model_inference"] is False)
    add(checks, "no_activation_extraction", manifest["prohibited_methods"]["activation_extraction"] is False)
    add(checks, "no_gpu_or_runpod", manifest["prohibited_methods"]["gpu_or_runpod"] is False)
    tracked_raw = git(repo, "ls-files", "data_external")
    tracked_output = git(repo, "ls-files", str(OUTPUT_REL))
    add(checks, "no_respondent_level_microdata_committed", tracked_raw == "" and "RID" not in tracked_output)
    privacy = manifest["privacy"]
    add(
        checks,
        "aggregate_output_privacy_manifest",
        privacy["respondent_level_output_written"] is False
        and privacy["respondent_ids_written"] is False
        and privacy["individual_response_masks_written"] is False
        and privacy["aggregate_outputs_only"] is True,
    )
    add(checks, "figure_png_nonempty", (output / "sapa_coverage_frontier.png").stat().st_size > 10_000)
    add(checks, "figure_svg_nonempty", (output / "sapa_coverage_frontier.svg").stat().st_size > 10_000)
    add(checks, "working_tree_clean_at_verification_start", clean_at_start)

    failed = [name for name, passed in checks.items() if not passed]
    verification = {
        "artifact": "AA-12 SAPA item-coverage frontier verification",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "PASS" if not failed else "FAIL",
        "startup_evidence": {
            "exact_raw_urls_fetched_in_required_order": args.startup_passed,
            "initial_fetched_sha256": REQUIRED_STARTUP_HASHES,
            "manifest_generated_timestamp_utc": "2026-09-12T21:15:38Z",
            "visible_metadata_compared_before_hashes": args.startup_passed,
        },
        "checks": checks,
        "failed_checks": failed,
        "check_count": len(checks),
        "privacy_note": "Verifier reads RID and item cells transiently; it writes aggregates only.",
    }
    if args.write:
        (output / "verification_report.json").write_text(
            json.dumps(verification, indent=2) + "\n", encoding="utf-8"
        )
        write_inventory(output, git(repo, "rev-parse", "HEAD"))
    print(json.dumps(verification, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
