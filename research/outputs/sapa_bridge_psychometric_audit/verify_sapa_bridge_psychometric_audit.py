#!/usr/bin/env python3
"""Verify the human-only SAPA bridge psychometric audit.

Respondent-level SAPA data are read only when ``--reproduce`` reruns the
aggregate analysis. This verifier never emits respondent rows or identifiers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT_REL = Path("research/outputs/sapa_bridge_psychometric_audit")
BRANCH = "codex/aa1-sapa-psychometric-audit"
GENERATED_AT = "2026-09-11T23:40:00Z"
PRIMARY_GENERATED = [
    "bridge_reuse_sensitivity.csv",
    "human_trait_proxy_clusters.csv",
    "human_trait_proxy_correlation_matrix.csv",
    "human_trait_proxy_correlation_matrix_direct_plus_close.csv",
    "human_trait_proxy_dimensionality_summary.json",
    "human_trait_proxy_eigenspectrum.csv",
    "human_trait_proxy_pairwise_n.csv",
    "human_trait_proxy_pairwise_n_direct_plus_close.csv",
    "human_trait_proxy_scree.png",
    "human_trait_proxy_spearman_correlation_matrix.csv",
    "human_trait_proxy_spearman_correlation_matrix_direct_plus_close.csv",
    "retained_item_pair_correlations.csv",
    "retained_traits_vs_human_big_five.csv",
    "sapa_bridge_planned_missingness_summary.json",
    "sapa_trait_bridge_psychometric_support_v1.csv",
    "source_manifest.json",
    "trait_proxy_discriminant_audit.csv",
    "trait_proxy_internal_coherence.csv",
    "trait_proxy_internal_item_pairs.csv",
    "trait_proxy_item_scoring.csv",
    "trait_proxy_scale_associations_long.csv",
    "trait_proxy_source_scale_convergence.csv",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def split_ids(value: object) -> list[str]:
    if pd.isna(value) or not str(value):
        return []
    return [part for part in str(value).split(";") if part]


def add(checks: dict[str, bool], name: str, value: object) -> None:
    checks[name] = bool(value)


def symmetric_correlation(frame: pd.DataFrame, size: int) -> bool:
    values = frame.to_numpy(dtype=float)
    return (
        frame.shape == (size, size)
        and list(frame.index) == list(frame.columns)
        and np.isfinite(values).all()
        and np.allclose(values, values.T, atol=1e-10)
        and np.allclose(np.diag(values), 1.0, atol=1e-10)
        and np.max(np.abs(values)) <= 1.0 + 1e-10
    )


def write_inventory(repo: Path, output: Path) -> pd.DataFrame:
    excluded = {"artifact_inventory.csv", "verification_report.json", "__pycache__"}
    rows = []
    for path in sorted(output.iterdir()):
        if not path.is_file() or path.name in excluded:
            continue
        relative = path.relative_to(repo).as_posix()
        rows.append(
            {
                "path": relative,
                "status": "active",
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "branch_raw_url": (
                    "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/"
                    f"refs/heads/{BRANCH}/{relative}"
                ),
                "future_canonical_raw_url": (
                    "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/" + relative
                ),
                "artifact_type": path.suffix.lstrip(".") or "text",
                "contains_respondent_rows": False,
            }
        )
    inventory = pd.DataFrame(rows)
    inventory.to_csv(output / "artifact_inventory.csv", index=False, lineterminator="\n")
    return inventory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--reproduce", action="store_true")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = repo / OUTPUT_REL
    checks: dict[str, bool] = {}

    bridge_path = repo / (
        "research/outputs/human_trait_dataset_feasibility/sapa_review/"
        "sapa_trait_bridge_provisional_v1.csv"
    )
    item_path = repo / (
        "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"
    )
    scale_path = repo / (
        "research/outputs/human_trait_dataset_feasibility/sapa/sapa_scale_inventory.csv"
    )
    raw_path = repo / (
        "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/"
        "sapaTempData696items08dec2013thru26jul2014.tab"
    )
    bridge = pd.read_csv(bridge_path).fillna("")
    items = pd.read_csv(item_path).fillna("")
    scales = pd.read_csv(scale_path).fillna("")

    decisions = Counter(bridge["review_decision"])
    add(checks, "bridge_45_direct_29_close", decisions == {"ACCEPT_DIRECT": 45, "ACCEPT_CLOSE": 29})
    add(checks, "bridge_74_unique_traits", len(bridge) == 74 and bridge["trait"].is_unique)
    referenced_items = set().union(*(set(split_ids(value)) for value in bridge["sapa_item_ids"]))
    referenced_scales = set().union(*(set(split_ids(value)) for value in bridge["source_scales"]))
    add(checks, "retained_items_129", len(referenced_items) == 129)
    add(checks, "retained_scales_78", len(referenced_scales) == 78)
    add(checks, "all_bridge_item_references_valid", referenced_items <= set(items["item_id"]))
    add(checks, "all_bridge_scale_references_valid", referenced_scales <= set(scales["scale_id"]))

    generated_before = {name: sha256(output / name) for name in PRIMARY_GENERATED}
    if args.reproduce:
        completed = subprocess.run(
            [
                sys.executable,
                str(output / "run_sapa_bridge_psychometric_audit.py"),
                "--repo-root",
                str(repo),
            ],
            cwd=repo,
            text=True,
            capture_output=True,
            check=False,
        )
        add(checks, "deterministic_rerun_exit_zero", completed.returncode == 0)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or completed.stdout)
        generated_after = {name: sha256(output / name) for name in PRIMARY_GENERATED}
        add(checks, "deterministic_primary_outputs_reproduce", generated_before == generated_after)
    else:
        add(checks, "deterministic_primary_outputs_reproduce", False)

    manifest = read_json(output / "source_manifest.json")
    add(
        checks,
        "all_input_hashes_match",
        all(sha256(repo / path) == digest for path, digest in manifest["inputs_loaded"].items()),
    )
    add(checks, "raw_hash_matches_release", sha256(raw_path) == manifest["raw_data"]["sha256"])
    add(checks, "raw_hash_expected", sha256(raw_path) == "fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6")
    add(checks, "respondent_id_columns_loaded_zero", manifest["raw_data"]["respondent_id_or_demographic_columns_loaded"] == 0)
    add(checks, "model_geometry_not_used", manifest["model_geometry_used"] is False)
    add(checks, "human_to_model_projection_not_performed", manifest["human_to_model_projection_performed"] is False)
    add(checks, "respondent_level_outputs_not_written", manifest["respondent_level_outputs_written"] is False)
    add(checks, "forbidden_inputs_loaded_empty", manifest["forbidden_inputs_loaded"] == [])

    direct_traits = bridge.loc[bridge["review_decision"] == "ACCEPT_DIRECT", "trait"].tolist()
    all_traits = bridge["trait"].tolist()
    direct_corr = pd.read_csv(output / "human_trait_proxy_correlation_matrix.csv", index_col=0)
    all_corr = pd.read_csv(
        output / "human_trait_proxy_correlation_matrix_direct_plus_close.csv", index_col=0
    )
    direct_spearman = pd.read_csv(
        output / "human_trait_proxy_spearman_correlation_matrix.csv", index_col=0
    )
    add(checks, "direct_matrix_order_and_finite", symmetric_correlation(direct_corr, 45) and list(direct_corr.index) == direct_traits)
    add(checks, "all_matrix_order_and_finite", symmetric_correlation(all_corr, 74) and list(all_corr.index) == all_traits)
    add(checks, "spearman_matrix_order_and_finite", symmetric_correlation(direct_spearman, 45) and list(direct_spearman.index) == direct_traits)

    direct_n = pd.read_csv(output / "human_trait_proxy_pairwise_n.csv", index_col=0)
    all_n = pd.read_csv(output / "human_trait_proxy_pairwise_n_direct_plus_close.csv", index_col=0)
    add(checks, "direct_pairwise_n_symmetric_positive", direct_n.shape == (45, 45) and np.allclose(direct_n, direct_n.T) and (direct_n.to_numpy() > 0).all())
    add(checks, "all_pairwise_n_symmetric_positive", all_n.shape == (74, 74) and np.allclose(all_n, all_n.T) and (all_n.to_numpy() > 0).all())

    item_pairs = pd.read_csv(output / "retained_item_pair_correlations.csv")
    add(checks, "all_129_item_pairs_present", len(item_pairs) == 129 * 128 // 2)
    add(checks, "item_pair_n_finite_and_plausible", item_pairs["pairwise_n"].between(200, 23679).all())
    add(checks, "item_pair_correlations_finite", np.isfinite(item_pairs[["pearson_r_raw_direction", "spearman_r_raw_direction"]].to_numpy()).all())

    scoring = pd.read_csv(output / "trait_proxy_item_scoring.csv")
    add(checks, "scoring_references_valid", set(scoring["item_id"]) == referenced_items and set(scoring["trait"]) == set(all_traits))
    add(checks, "scoring_transformations_explicit", set(scoring["transformation"]) <= {"identity", "7-response"} and set(scoring["orientation_status"]) == {"explicit_resolved"})
    add(checks, "score_directions_signed", set(scoring["orientation_sign"]) == {-1, 1})

    coherence = pd.read_csv(output / "trait_proxy_internal_coherence.csv")
    convergence = pd.read_csv(output / "trait_proxy_source_scale_convergence.csv")
    discriminant = pd.read_csv(output / "trait_proxy_discriminant_audit.csv")
    support = pd.read_csv(output / "sapa_trait_bridge_psychometric_support_v1.csv")
    add(checks, "coherence_74_unique_traits", len(coherence) == 74 and coherence["trait"].is_unique)
    add(checks, "convergence_74_unique_traits", len(convergence) == 74 and convergence["trait"].is_unique)
    add(checks, "discriminant_74_unique_traits", len(discriminant) == 74 and discriminant["trait"].is_unique)
    add(checks, "support_74_unique_traits", len(support) == 74 and support["trait"].is_unique)
    add(checks, "three_direct_single_item", len(coherence[(coherence["review_decision"] == "ACCEPT_DIRECT") & (coherence["supporting_item_count"] == 1)]) == 3)
    valid_support = {"HIGH HUMAN-MEASUREMENT SUPPORT", "MODERATE SUPPORT", "LIMITED / SINGLE-ITEM", "REDUNDANT / BROAD", "INSUFFICIENT"}
    add(checks, "support_tiers_valid", set(support["human_measurement_support_tier"]) <= valid_support)
    direct_support = support[support["semantic_review_decision"] == "ACCEPT_DIRECT"]
    add(checks, "direct_support_counts_9_3_30_3", Counter(direct_support["human_measurement_support_tier"]) == {"HIGH HUMAN-MEASUREMENT SUPPORT": 9, "MODERATE SUPPORT": 3, "REDUNDANT / BROAD": 30, "INSUFFICIENT": 3})

    dimensions = read_json(output / "human_trait_proxy_dimensionality_summary.json")
    add(checks, "parallel_analysis_seed_frozen", dimensions["method"]["parallel_analysis_seed"] == 20260911)
    add(checks, "direct_effective_rank_reproduces", abs(dimensions["tiers"]["accept_direct"]["participation_ratio_effective_rank"] - 12.441369) < 1e-6)
    add(checks, "direct_parallel_components_reproduce", dimensions["tiers"]["accept_direct"]["parallel_analysis_components"] == 6)

    # Parse every machine-readable output and reject respondent-like tables.
    direct_identifier_headers = {"respondent_id", "caseid", "email", "ip_address", "r0000100"}
    aggregate_files_safe = True
    for path in output.glob("*.csv"):
        frame = pd.read_csv(path)
        lower_headers = {str(column).lower() for column in frame.columns}
        if lower_headers & direct_identifier_headers or len(frame) == 23679:
            aggregate_files_safe = False
    for path in output.glob("*.json"):
        read_json(path)
    add(checks, "all_csv_json_parse_and_no_respondent_table", aggregate_files_safe)
    tracked_raw = subprocess.run(
        ["git", "ls-files", "data_external"], cwd=repo, text=True, capture_output=True, check=True
    ).stdout.strip()
    add(checks, "no_raw_human_data_tracked", tracked_raw == "")

    inventory = write_inventory(repo, output)
    add(checks, "artifact_inventory_paths_unique", inventory["path"].is_unique)
    add(
        checks,
        "artifact_inventory_hashes_match",
        all(sha256(repo / row.path) == row.sha256 for row in inventory.itertuples(index=False)),
    )

    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "status": "PASS" if not failed else "FAIL",
        "generated_at": GENERATED_AT,
        "checks": checks,
        "failed_checks": failed,
        "notes": [
            "Verification report and artifact_inventory.csv are excluded from the inventory to avoid self-referential hashes.",
            "The --reproduce mode reruns the aggregate analysis and requires the gitignored SAPA tab and scoring-key files.",
        ],
    }
    (output / "verification_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
