#!/usr/bin/env python3
"""Deterministically verify the Qwen axis-specificity analysis and inventory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd


SOURCE_COMMIT = "667acdd634bfb8c39d40432fe60f0c5ef3bbbeeb"
PRIOR_HASHES = {
    "qwen_trait_pc_correlations_all.csv": "6ccbb08452af12ddf050fc95e083a0e0c4e2e01423c417cf2e9919909fd79424",
    "qwen_trait_family_membership_primary.csv": "cb010ab242747544ee5ba957e64b1565c8207565a76a9523cb5b837331237b97",
    "qwen_trait_family_human_mapping_judgments.csv": "cb4ac6b1338ce209ab2a88d24fac67c29abb3e6322055a4475b6b6dbc52e1f3c",
    "qwen_pc_trait_family_human_inventory.csv": "49f5b7c5c6b8f74d56ba2a2a410c4b9ebf4e3b4bf2459f013422fba0dfc37896",
    "verification_report.json": "d191f930c2f6a9d592ea856c8d1f5f0b458b17dbc4bc8a8fc1bc271a6b5ac8b8",
}
PCS = [f"PC{i}" for i in range(1, 7)]
VALID_CLASSES = {
    "AXIS_SPECIFIC_STRONG",
    "STRONG_CROSS_LOADING",
    "TARGET_DOMINANT_BUT_DIFFUSE",
    "NON_TARGET_DOMINANT",
}
VALID_MATCHES = {
    "STRONG_FAMILY_MATCH",
    "PARTIAL_FAMILY_MATCH",
    "FACET_OR_SUBCOMPONENT",
    "ITEM_LEVEL_ONLY",
    "POOR_MATCH",
    "NO_DEFENSIBLE_MATCH",
}
DETERMINISTIC_OUTPUTS = [
    "qwen_trait_axis_specificity_metrics.csv",
    "qwen_trait_best_axis_summary.csv",
    "qwen_trait_axis_specificity_bootstrap.csv",
    "qwen_axis_specific_marker_sets.csv",
    "qwen_axis_specificity_threshold_sensitivity.csv",
    "qwen_trait_family_specificity_classification.csv",
    "qwen_axis_specific_family_comparison.csv",
    "qwen_axis_specificity_pareto_front.csv",
    "existing_trait_composite_axis_specificity.csv",
    "qwen_axis_specific_human_mapping_packet.csv",
    "qwen_axis_specific_human_mapping_judgments.csv",
    "qwen_axis_specific_human_inventory.csv",
    "prior_vs_axis_specific_human_inventory_comparison.csv",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(repo: Path, output: Path, rerun: bool) -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    prior_dir = repo / "research/outputs/qwen_trait_family_human_inventory"
    for name, expected in PRIOR_HASHES.items():
        actual = sha256(prior_dir / name)
        check(f"prior_hash_{name}", actual == expected, {"actual": actual, "expected": expected})

    merge_base = subprocess.check_output(
        ["git", "merge-base", SOURCE_COMMIT, "HEAD"], cwd=repo, text=True
    ).strip()
    check("source_commit_is_exact_branch_ancestor", merge_base == SOURCE_COMMIT, merge_base)

    corr = pd.read_csv(prior_dir / "qwen_trait_pc_correlations_all.csv")
    members = pd.read_csv(prior_dir / "qwen_trait_family_membership_primary.csv")
    metrics = pd.read_csv(output / "qwen_trait_axis_specificity_metrics.csv")
    best = pd.read_csv(output / "qwen_trait_best_axis_summary.csv")
    bootstrap = pd.read_csv(output / "qwen_trait_axis_specificity_bootstrap.csv")
    markers = pd.read_csv(output / "qwen_axis_specific_marker_sets.csv")
    sensitivity = pd.read_csv(output / "qwen_axis_specificity_threshold_sensitivity.csv")
    classification = pd.read_csv(output / "qwen_trait_family_specificity_classification.csv")
    comparison = pd.read_csv(output / "qwen_axis_specific_family_comparison.csv")
    pareto = pd.read_csv(output / "qwen_axis_specificity_pareto_front.csv")
    composites = pd.read_csv(output / "existing_trait_composite_axis_specificity.csv")
    packet = pd.read_csv(output / "qwen_axis_specific_human_mapping_packet.csv")
    packet_manifest = json.loads(
        (output / "qwen_axis_specific_human_mapping_packet_manifest.json").read_text(encoding="utf-8")
    )
    judgments = pd.read_csv(output / "qwen_axis_specific_human_mapping_judgments.csv").fillna("")
    inventory = pd.read_csv(output / "qwen_axis_specific_human_inventory.csv").fillna("")
    prior_comparison = pd.read_csv(output / "prior_vs_axis_specific_human_inventory_comparison.csv")
    source_manifest = json.loads((output / "source_manifest.json").read_text(encoding="utf-8"))
    library_path = repo / "research/outputs/qwen_pc_human_construct_bridge/human_construct_library.csv"
    item_path = repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"
    library = pd.read_csv(library_path)
    items = pd.read_csv(item_path)

    check("saved_association_rows_1440", len(corr) == 1440, len(corr))
    check("exactly_240_traits", corr["trait"].nunique() == 240, corr["trait"].nunique())
    check("exactly_6_pcs", set(corr["pc"]) == set(PCS), sorted(corr["pc"].unique()))
    check("specificity_rows_1440", len(metrics) == 1440, len(metrics))
    check("best_axis_rows_240", len(best) == 240 and best["trait"].is_unique, len(best))
    check("bootstrap_rows_1440", len(bootstrap) == 1440, len(bootstrap))
    check("bootstrap_resamples_2000", set(bootstrap["bootstrap_resamples"]) == {2000}, sorted(bootstrap["bootstrap_resamples"].unique()))
    check("bootstrap_seed_fixed", set(bootstrap["bootstrap_specificity_seed"]) == {20260920}, sorted(bootstrap["bootstrap_specificity_seed"].unique()))
    increments = bootstrap["bootstrap_probability_target_largest_abs"] * 2000
    check("bootstrap_probabilities_have_valid_counts", np.allclose(increments, np.round(increments)), float(np.max(np.abs(increments - np.round(increments)))))

    pivot = corr.pivot(index="trait", columns="pc", values="pearson_r").loc[:, PCS]
    expected_communality = np.square(pivot).sum(axis=1)
    joined_comm = metrics.drop_duplicates("trait").set_index("trait")["six_pc_communality"]
    comm_error = float(np.max(np.abs(joined_comm.loc[pivot.index] - expected_communality)))
    check("communality_formula_reproduces", comm_error < 1e-12, comm_error)
    expected_purity = np.square(metrics["target_r"]) / metrics["six_pc_communality"]
    purity_error = float(np.max(np.abs(expected_purity - metrics["axis_purity"])))
    check("axis_purity_formula_reproduces", purity_error < 1e-12, purity_error)
    dominance_error = float(
        np.max(
            np.abs(
                metrics["dominance_gap"]
                - (metrics["target_abs_r"] - metrics["max_off_axis_abs_r"])
            )
        )
    )
    check("dominance_gap_formula_reproduces", dominance_error < 1e-12, dominance_error)
    check(
        "pc1_pc6_mutually_uncorrelated",
        source_manifest["verification_metrics"]["pc_max_abs_off_diagonal_correlation"] < 1e-12,
        source_manifest["verification_metrics"]["pc_max_abs_off_diagonal_correlation"],
    )
    check(
        "communality_matches_multiple_r2",
        source_manifest["verification_metrics"]["communality_vs_multiple_r2_max_abs_error"] < 1e-12,
        source_manifest["verification_metrics"]["communality_vs_multiple_r2_max_abs_error"],
    )
    check(
        "canonical_pc_coordinates_reproduce_within_established_tolerance",
        source_manifest["verification_metrics"]["canonical_pc1_pc3_coordinate_max_abs_error"] < 2e-6,
        source_manifest["verification_metrics"]["canonical_pc1_pc3_coordinate_max_abs_error"],
    )
    check(
        "saved_correlations_reproduce_from_role_scores",
        source_manifest["verification_metrics"]["saved_vs_role_level_recomputed_correlation_max_abs_error"] < 1e-12,
        source_manifest["verification_metrics"]["saved_vs_role_level_recomputed_correlation_max_abs_error"],
    )

    member_keys = set(zip(members["pc"], members["trait"], strict=True))
    marker_keys = set(zip(markers["pc"], markers["trait"], strict=True))
    check("all_markers_are_prior_family_members", marker_keys <= member_keys, len(marker_keys - member_keys))
    marker_metric = metrics.merge(markers[["pc", "trait"]], on=["pc", "trait"], validate="one_to_one")
    check("markers_target_dominant", marker_metric["target_is_largest_abs_loading"].all(), int((~marker_metric["target_is_largest_abs_loading"]).sum()))
    check("markers_purity_at_least_070", (marker_metric["axis_purity"] >= 0.70).all(), float(marker_metric["axis_purity"].min()))
    check(
        "markers_bootstrap_dominance_at_least_095",
        (marker_metric["bootstrap_probability_target_largest_abs"] >= 0.95).all(),
        float(marker_metric["bootstrap_probability_target_largest_abs"].min()),
    )
    check("classification_covers_all_original_members", len(classification) == len(members) == 328, len(classification))
    check("classification_values_valid", set(classification["specificity_class"]) <= VALID_CLASSES, sorted(classification["specificity_class"].unique()))

    independent_sensitivity = []
    metric_members = metrics[metrics["prior_association_family_member"]]
    for row in sensitivity.itertuples(index=False):
        frame = metric_members[(metric_members["pc"] == row.pc) & (metric_members["pole"] == row.pole)]
        count = int(
            (
                frame["target_is_largest_abs_loading"]
                & (frame["axis_purity"] >= row.purity_threshold)
                & (
                    frame["bootstrap_probability_target_largest_abs"]
                    >= row.bootstrap_dominance_probability_threshold
                )
            ).sum()
        )
        independent_sensitivity.append(count)
    check(
        "threshold_sensitivity_reproduces",
        independent_sensitivity == sensitivity["axis_specific_marker_count"].astype(int).tolist(),
        {"rows": len(sensitivity), "purities": sorted(sensitivity["purity_threshold"].unique()), "probabilities": sorted(sensitivity["bootstrap_dominance_probability_threshold"].unique())},
    )
    check("primary_threshold_pair_frozen", source_manifest["primary_axis_specific_rule"]["axis_purity_at_least"] == 0.70 and source_manifest["primary_axis_specific_rule"]["bootstrap_dominance_probability_at_least"] == 0.95, source_manifest["primary_axis_specific_rule"])
    check("family_comparison_has_12_signed_rows", len(comparison) == 12, len(comparison))
    check("pareto_rows_unique", not pareto.duplicated(["pc", "trait"]).any(), len(pareto))
    check("documented_composites_present", set(composites["composite_name"]) == {"Exploration", "Response", "Scrutiny", "Challenge", "Affiliation"}, sorted(composites["composite_name"]))
    affiliation = composites[composites["composite_name"] == "Affiliation"].iloc[0]
    check("affiliation_is_pc3_specific", affiliation["best_pc"] == "PC3" and affiliation["axis_purity"] > 0.95 and abs(affiliation["best_signed_r"]) > 0.95, {"best_pc": affiliation["best_pc"], "r": affiliation["best_signed_r"], "purity": affiliation["axis_purity"]})

    check("mapping_packet_has_12_neutral_families", len(packet) == 12 and packet["family_id"].is_unique, len(packet))
    prohibited_columns = [column for column in packet.columns if any(token in column.lower() for token in ["pc", "pole", "role", "persona", "aa2", "aa7", "big_five", "prior_human_match"])]
    check("mapping_packet_excludes_prohibited_fields", not prohibited_columns, prohibited_columns)
    rng = np.random.default_rng(packet_manifest["packet_seed"])
    signed = [(f"PC{pc}", pole) for pc in range(1, 7) for pole in ["positive", "negative"]]
    permutation = rng.permutation(12)
    expected_map = {signed[index]: f"PURE-FAM-{order + 1:02d}" for order, index in enumerate(permutation)}
    actual_map = {(row["pc"], row["pole"]): row["family_id"] for row in packet_manifest["family_key_not_reviewer_facing"]}
    check("mapping_packet_order_seed_reproduces", actual_map == expected_map, packet_manifest["packet_seed"])
    check("human_library_exactly_126_unique_constructs", len(library) == 126 and library["construct_id"].is_unique, len(library))
    valid_constructs = set(library["construct_id"])
    valid_items = set(items["item_id"])
    judgment_constructs_valid = all((not value) or value in valid_constructs or value.startswith("ITEM:") for value in judgments["human_construct_id"])
    cited_items = set(";".join(judgments["item_ids"]).split(";")) - {""}
    check("mapping_construct_ids_valid", judgment_constructs_valid, sorted(set(judgments["human_construct_id"]) - valid_constructs - {""}))
    check("mapping_item_ids_valid", cited_items <= valid_items, sorted(cited_items - valid_items))
    check("mapping_statuses_valid", set(judgments["match_status"]) <= VALID_MATCHES, sorted(judgments["match_status"].unique()))
    empty_ids = set(packet.loc[packet["axis_specific_marker_count"] == 0, "family_id"])
    empty_judgments = judgments[judgments["family_id"].isin(empty_ids)]
    check("empty_marker_families_only_no_match", len(empty_judgments) == len(empty_ids) and set(empty_judgments["match_status"]) == {"NO_DEFENSIBLE_MATCH"}, {"empty_families": len(empty_ids), "rows": len(empty_judgments)})
    check("inventory_rows_match_judgments", len(inventory) == len(judgments), {"inventory": len(inventory), "judgments": len(judgments)})
    check("prior_comparison_has_12_signed_rows", len(prior_comparison) == 12, len(prior_comparison))
    check("human_library_byte_identical", sha256(library_path) == "7aadc382dfd3d18da6dce43be945cc6f5ae8dc8d124dfd9f0a8a8c8fc4864fd0", sha256(library_path))
    source_paths = list(source_manifest["source_hashes"])
    check("no_llama_gemma_source", not any("llama" in path.lower() or "gemma" in path.lower() for path in source_paths), source_paths)
    check("no_aa7_scientific_source", not any("human_supported_trait_convergence" in path for path in source_paths), source_paths)
    check("no_human_respondent_rows_loaded", source_manifest["firewall"]["human_respondent_rows_loaded"] is False, source_manifest["firewall"])

    tracked_output = subprocess.check_output(
        ["git", "ls-files", str(output.relative_to(repo))], cwd=repo, text=True
    ).splitlines()
    respondent_like = []
    for relative in tracked_output:
        path = repo / relative
        if path.suffix == ".csv":
            with path.open(newline="", encoding="utf-8") as handle:
                header = next(csv.reader(handle), [])
            if any(column.lower() in {"respondent_id", "participant_id", "case_id"} for column in header):
                respondent_like.append(relative)
    check("no_respondent_level_output_schema", not respondent_like, respondent_like)

    parse_failures = []
    for path in output.rglob("*.csv"):
        try:
            pd.read_csv(path)
        except Exception as exc:  # pragma: no cover - verification path
            parse_failures.append(f"{path.name}: {exc}")
    for path in output.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - verification path
            parse_failures.append(f"{path.name}: {exc}")
    check("all_csv_json_parse", not parse_failures, parse_failures)
    check("report_exists", (output / "qwen_axis_specific_family_report.md").is_file(), str(output / "qwen_axis_specific_family_report.md"))
    check("diagnostic_figures_exist", (output / "qwen_axis_specificity_strength_purity.png").is_file() and (output / "qwen_axis_specificity_strength_purity.svg").is_file(), "png+svg")

    if rerun:
        with tempfile.TemporaryDirectory(prefix="qwen-axis-specificity-") as temp_name:
            temp = Path(temp_name)
            python = Path(__import__("sys").executable)
            scripts = output / "scripts"
            subprocess.run([str(python), str(scripts / "compute_axis_specificity.py"), "--repo-root", str(repo), "--output-dir", str(temp)], check=True, stdout=subprocess.DEVNULL)
            subprocess.run([str(python), str(scripts / "build_axis_specific_mapping_packet.py"), "--repo-root", str(repo), "--output-dir", str(temp)], check=True)
            subprocess.run([str(python), str(scripts / "build_axis_specific_human_inventory.py"), "--repo-root", str(repo), "--output-dir", str(temp)], check=True, stdout=subprocess.DEVNULL)
            mismatches = [name for name in DETERMINISTIC_OUTPUTS if sha256(temp / name) != sha256(output / name)]
            check("deterministic_rerun_primary_outputs", not mismatches, mismatches)
    else:
        check("deterministic_rerun_primary_outputs", True, "skipped by explicit --no-rerun")

    inventory_path = output / "artifact_inventory.csv"
    if inventory_path.exists():
        artifact = pd.read_csv(inventory_path)
        bad = []
        for row in artifact.itertuples(index=False):
            path = repo / row.path
            if not path.exists() or sha256(path) != row.sha256:
                bad.append(row.path)
        check("artifact_inventory_hashes_match", not bad, bad)

    failures = [entry for entry in checks if not entry["passed"]]
    report = {
        "analysis": "Axis-specific Qwen trait markers and purity-filtered SAPA inventory",
        "verified_at_utc": "2026-09-12T19:05:00Z",
        "passed": not failures,
        "check_count": len(checks),
        "failure_count": len(failures),
        "failures": failures,
        "checks": checks,
        "boundary": {
            "model_geometry_used": "Qwen/Qwen3-32B only",
            "human_respondent_scored_or_projected": False,
            "llama_gemma_comparison": False,
            "AA7_alignment_used": False,
            "human_model_correspondence_test": False,
            "next_experiment_selected": False,
        },
    }
    def json_default(value: object) -> object:
        if isinstance(value, np.generic):
            return value.item()
        raise TypeError(f"Not JSON serializable: {type(value).__name__}")

    (output / "verification_report.json").write_text(
        json.dumps(report, indent=2, default=json_default) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"passed": report["passed"], "check_count": len(checks), "failures": failures},
            indent=2,
            default=json_default,
        )
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-rerun", action="store_true")
    args = parser.parse_args()
    main(args.repo_root.resolve(), args.output_dir.resolve(), not args.no_rerun)
