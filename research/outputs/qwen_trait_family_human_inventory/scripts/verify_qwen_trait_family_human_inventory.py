#!/usr/bin/env python3
"""Deterministic verification for the Qwen-family/SAPA inventory."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd


SOURCE_COMMIT = "313c5cff6e071d707d37b1318343cde4ed510725"
NUMERIC_FREEZE_COMMIT = "9ce2809"
BLIND_PACKET_FREEZE_COMMIT = "70f7617"
JUDGMENT_FREEZE_COMMIT = "9c5aad1"
INVENTORY_FREEZE_COMMIT = "921df92"
EXPECTED_GENERATED_AT = "2026-09-12T21:30:00Z"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bh_reference(values: np.ndarray) -> np.ndarray:
    order = sorted(range(len(values)), key=lambda index: (values[index], index))
    adjusted_sorted = [0.0] * len(values)
    running = 1.0
    for position in range(len(values) - 1, -1, -1):
        index = order[position]
        candidate = values[index] * len(values) / (position + 1)
        running = min(running, candidate)
        adjusted_sorted[position] = min(1.0, running)
    result = np.empty(len(values), dtype=float)
    for position, index in enumerate(order):
        result[index] = adjusted_sorted[position]
    return result


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def verify(repo: Path, output: Path) -> dict[str, object]:
    checks: dict[str, bool] = {}
    associations = pd.read_csv(output / "qwen_trait_pc_correlations_all.csv")
    primary = pd.read_csv(output / "qwen_trait_family_membership_primary.csv")
    sensitivity = pd.read_csv(output / "qwen_trait_family_threshold_sensitivity.csv")
    summaries = pd.read_csv(output / "qwen_trait_family_summaries.csv").fillna("")
    packet = pd.read_csv(output / "qwen_trait_family_blinded_mapping_packet.csv").fillna("")
    judgments = pd.read_csv(output / "qwen_trait_family_human_mapping_judgments.csv").fillna("")
    inventory = pd.read_csv(output / "qwen_pc_trait_family_human_inventory.csv").fillna("")
    inventory_summary = json.loads((output / "inventory_summary.json").read_text(encoding="utf-8"))
    numeric_manifest = json.loads((output / "numeric_source_manifest.json").read_text(encoding="utf-8"))
    blind_manifest = json.loads((output / "qwen_trait_family_blind_manifest.json").read_text(encoding="utf-8"))
    source_manifest = json.loads((output / "source_manifest.json").read_text(encoding="utf-8"))
    library = pd.read_csv(repo / "research/outputs/qwen_pc_human_construct_bridge/human_construct_library.csv").fillna("")
    item_dictionary = pd.read_csv(repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv").fillna("")

    checks["exactly_240_traits_x_6_pcs"] = len(associations) == 1440 and associations["trait"].nunique() == 240 and associations["pc"].nunique() == 6
    checks["qwen_role_count_275"] = numeric_manifest["role_count"] == 275
    checks["all_association_statistics_finite"] = np.isfinite(associations[["pearson_r", "pearson_r_squared", "spearman_rho", "p_value", "BH_FDR_q", "bootstrap_sign_stability"]].to_numpy(float)).all()
    checks["pearson_r_squared_exact"] = np.allclose(associations["pearson_r_squared"], associations["pearson_r"] ** 2, atol=1e-15, rtol=1e-12)

    bh_ok = True
    for _, group in associations.groupby("pc"):
        reference = bh_reference(group["p_value"].to_numpy(float))
        bh_ok &= bool(np.allclose(reference, group["BH_FDR_q"].to_numpy(float), atol=1e-15, rtol=1e-12))
    checks["BH_FDR_correct_within_each_pc"] = bh_ok
    checks["bootstrap_fixed_2000_and_seeds"] = set(associations["bootstrap_resamples"]) == {2000} and set(associations["bootstrap_seed"]) == set(range(20260913, 20260919)) and numeric_manifest["bootstrap"]["master_seed"] == 20260912
    checks["bootstrap_all_finite"] = int(associations["bootstrap_nonfinite_count"].sum()) == 0
    checks["primary_members_all_pass_frozen_rule"] = bool((primary["pearson_r"].abs() >= 0.50).all() and (primary["BH_FDR_q"] < 0.01).all() and (primary["bootstrap_sign_stability"] >= 0.95).all())
    checks["positive_and_negative_poles_consistent"] = bool(((primary.loc[primary["pole"] == "positive", "pearson_r"] > 0).all()) and ((primary.loc[primary["pole"] == "negative", "pearson_r"] < 0).all()))

    primary_keys = set(zip(primary["pc"], primary["pole"], primary["trait"]))
    sensitivity_50 = sensitivity[(np.isclose(sensitivity["abs_r_threshold"], 0.50)) & sensitivity["is_member"]]
    checks["sensitivity_0_50_reproduces_primary"] = primary_keys == set(zip(sensitivity_50["pc"], sensitivity_50["pole"], sensitivity_50["trait"]))
    sensitivity_ok = True
    for row in sensitivity.itertuples(index=False):
        expected = abs(row.pearson_r) >= row.abs_r_threshold and row.BH_FDR_q < 0.01 and row.bootstrap_sign_stability >= 0.95
        sensitivity_ok &= bool(row.is_member == expected)
    checks["sensitivity_0_40_0_50_0_60_rules_reproduce"] = sensitivity_ok and set(np.round(sensitivity["abs_r_threshold"], 2)) == {0.40, 0.50, 0.60}
    checks["all_12_pc_pole_families_present"] = len(summaries) == 12 and set(zip(summaries["pc"], summaries["pole"])) == {(f"PC{i}", pole) for i in range(1, 7) for pole in ("positive", "negative")}

    canonical_definitions = pd.read_csv(repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_model_trait_candidate_crosswalk.csv")
    canonical_lookup = dict(zip(canonical_definitions["model_trait"], canonical_definitions["canonical_definition"], strict=True))
    checks["canonical_trait_definitions_exact"] = all(canonical_lookup[row.trait] == row.canonical_definition for row in associations.itertuples(index=False))
    checks["canonical_pc1_pc3_within_established_tolerance"] = numeric_manifest["canonical_pc1_pc3_max_abs_reproduction_error"] <= 1.3e-6

    packet_text = (output / "qwen_trait_family_blinded_mapping_packet.csv").read_text(encoding="utf-8")
    forbidden_columns = {"pc", "pole", "role", "persona", "cluster", "prior_interpretation", "big_five", "aa7"}
    checks["blind_packet_has_12_unique_neutral_ids"] = len(packet) == 12 and packet["family_id"].nunique() == 12 and set(packet["family_id"]) == {f"FAM-{i:02d}" for i in range(1, 13)}
    checks["blind_packet_excludes_pc_and_prohibited_fields"] = not (forbidden_columns & {column.lower() for column in packet.columns}) and re.search(r"\bPC[1-6]\b", packet_text) is None and not re.search(r"\b(?:Llama|Gemma|AA-7)\b", packet_text, flags=re.IGNORECASE)
    checks["blind_packet_hash_matches_frozen_manifest"] = sha256(output / "qwen_trait_family_blinded_mapping_packet.csv") == blind_manifest["packet_sha256"]
    checks["blind_packet_seed_and_order_reproduce"] = blind_manifest["family_id_seed"] == 20260919 and list(packet["family_id"]) == [f"FAM-{i:02d}" for i in range(1, 13)]

    valid_statuses = {"STRONG_FAMILY_MATCH", "PARTIAL_FAMILY_MATCH", "FACET_OR_SUBCOMPONENT", "ITEM_LEVEL_ONLY", "POOR_MATCH", "NO_DEFENSIBLE_MATCH"}
    checks["all_families_receive_valid_human_judgment"] = judgments["family_id"].nunique() == 12 and set(judgments["match_status"]).issubset(valid_statuses)
    checks["full_126_construct_library_is_candidate_universe"] = len(library) == 126 and library["construct_id"].nunique() == 126 and judgments["candidate_universe"].str.contains("126-construct").all()
    valid_constructs = set(library["construct_id"])
    referenced = set(judgments.loc[~judgments["human_construct_id"].str.startswith("ITEM:") & (judgments["human_construct_id"] != ""), "human_construct_id"])
    checks["judgments_reference_only_library_or_real_item"] = referenced.issubset(valid_constructs) and all(value.split(":", 1)[1] in set(item_dictionary["item_id"]) for value in judgments.loc[judgments["human_construct_id"].str.startswith("ITEM:"), "human_construct_id"])
    item_ids_ok = all(set(split for split in str(value).split(";") if split).issubset(set(item_dictionary["item_id"])) for value in judgments["item_ids"])
    wording_ok = all(len(json.loads(row.item_wording_json)) == int(row.item_count) for row in judgments.itertuples(index=False))
    checks["all_item_ids_and_wording_valid"] = item_ids_ok and wording_ok
    checks["inventory_has_all_families_and_judgments"] = len(inventory) == len(judgments) and inventory["family_id"].nunique() == 12 and set(zip(inventory["family_id"], inventory["human_construct_id"])) == set(zip(judgments["family_id"], judgments["human_construct_id"]))
    checks["inventory_summary_counts_reproduce"] = inventory_summary["primary_membership_rows"] == len(primary) and inventory_summary["unique_qwen_traits_selected"] == primary["trait"].nunique() and inventory_summary["unique_human_construct_or_item_candidates"] == judgments.loc[judgments["human_construct_id"] != "", "human_construct_id"].nunique()

    checks["qwen_only_firewall_recorded"] = source_manifest["firewall"]["models_used"] == ["Qwen/Qwen3-32B"] and source_manifest["firewall"]["Llama_or_Gemma_analysis_used"] is False and source_manifest["firewall"]["AA7_result_paths_used"] == []
    checks["prior_AA1_hypotheses_not_used"] = source_manifest["firewall"]["prior_AA1_hypothesis_files_used"] == [] and source_manifest["blind_mapping"]["prior_hypothesis_files_used"] == []
    checks["no_human_scoring_projection_or_next_experiment"] = source_manifest["firewall"]["human_respondent_rows_loaded_or_scored"] is False and source_manifest["firewall"]["human_model_projection_performed"] is False and source_manifest["firewall"]["next_experiment_selected"] is False

    tracked_human_raw = git(repo, "ls-files", "data_external/human_validation")
    forbidden_output_columns = {"respondent_id", "caseid", "subject_id", "nlsyid", "person_id"}
    output_columns = {column.lower() for path in output.glob("*.csv") for column in pd.read_csv(path, nrows=0).columns}
    checks["no_respondent_level_human_data_tracked_or_emitted"] = tracked_human_raw == "" and not (forbidden_output_columns & output_columns)

    historical_paths = [
        "research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_category3_blinded_review_packet.csv",
        "research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_category3_second_pass_review.csv",
        "research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_trait_bridge_provisional_v1.csv",
    ]
    historical_ok = True
    for relative in historical_paths:
        committed = subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{relative}"], cwd=repo)
        historical_ok &= hashlib.sha256(committed).hexdigest() == sha256(repo / relative)
    checks["historical_SAPA_packets_untouched"] = historical_ok

    source_verification = json.loads((repo / "research/outputs/qwen_pc_human_construct_bridge/verification_report.json").read_text(encoding="utf-8"))
    checks["validated_AA1_source_is_27_of_27"] = source_verification["passed"] is True and source_verification["check_count"] == 27 and all(source_verification["checks"].values())
    checks["freeze_commit_order_is_auditable"] = all(
        subprocess.run(["git", "merge-base", "--is-ancestor", earlier, later], cwd=repo).returncode == 0
        for earlier, later in [
            (NUMERIC_FREEZE_COMMIT, BLIND_PACKET_FREEZE_COMMIT),
            (BLIND_PACKET_FREEZE_COMMIT, JUDGMENT_FREEZE_COMMIT),
            (JUDGMENT_FREEZE_COMMIT, INVENTORY_FREEZE_COMMIT),
        ]
    )

    parse_ok = True
    for path in output.iterdir():
        if path.suffix == ".csv":
            try:
                pd.read_csv(path)
            except Exception:
                parse_ok = False
        elif path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                parse_ok = False
    checks["all_csv_json_outputs_parse"] = parse_ok

    deterministic_files = [
        "qwen_trait_pc_correlations_all.csv",
        "qwen_trait_family_membership_primary.csv",
        "qwen_trait_family_threshold_sensitivity.csv",
        "numeric_source_manifest.json",
        "qwen_trait_family_summaries.csv",
        "qwen_trait_family_report.md",
        "qwen_trait_family_blinded_mapping_packet.csv",
        "qwen_trait_family_blind_manifest.json",
        "qwen_trait_family_human_mapping_judgments.csv",
        "qwen_pc_trait_family_human_inventory.csv",
        "qwen_pc_trait_family_human_inventory_report.md",
        "inventory_summary.json",
    ]
    deterministic_ok = True
    outputs_root = repo / "research/outputs"
    with tempfile.TemporaryDirectory(prefix=".qwen_family_verify_", dir=outputs_root) as tmp_name:
        tmp = Path(tmp_name)
        shutil.copy2(output / "qwen_trait_family_selection_spec.md", tmp / "qwen_trait_family_selection_spec.md")
        scripts = output / "scripts"
        commands = [
            [sys.executable, str(scripts / "compute_qwen_trait_families.py"), "--repo-root", str(repo), "--output-dir", str(tmp)],
            [sys.executable, str(scripts / "build_qwen_family_packet.py"), "--output-dir", str(tmp)],
            [sys.executable, str(scripts / "build_blind_sapa_mapping.py"), "--repo-root", str(repo), "--output-dir", str(tmp)],
            [sys.executable, str(scripts / "assemble_qwen_sapa_inventory.py"), "--repo-root", str(repo), "--output-dir", str(tmp)],
        ]
        for command in commands:
            subprocess.run(command, cwd=repo, check=True, stdout=subprocess.DEVNULL)
        deterministic_ok = all((tmp / name).read_bytes() == (output / name).read_bytes() for name in deterministic_files)
    checks["deterministic_rerun_reproduces_primary_outputs"] = deterministic_ok

    inventory_path = output / "artifact_inventory.csv"
    inventory_failures = []
    if inventory_path.exists():
        with inventory_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                artifact = repo / row["path"]
                if not artifact.exists() or sha256(artifact) != row["sha256"] or artifact.stat().st_size != int(row["bytes"]):
                    inventory_failures.append(row["path"])
    checks["artifact_inventory_hashes_match"] = inventory_path.exists() and not inventory_failures

    failures = sorted(name for name, passed in checks.items() if not passed)
    return {
        "analysis": "Correlation-defined Qwen trait families to SAPA inventory verification",
        "generated_at_utc": EXPECTED_GENERATED_AT,
        "check_count": len(checks),
        "passed": not failures,
        "checks": {name: bool(value) for name, value in sorted(checks.items())},
        "failures": failures,
        "artifact_inventory_failures": inventory_failures,
        "counts": {
            "association_rows": len(associations),
            "primary_membership_rows": len(primary),
            "unique_primary_traits": int(primary["trait"].nunique()),
            "families": int(summaries["pc"].count()),
            "human_mapping_rows": len(judgments),
            "human_construct_or_item_candidates": inventory_summary["unique_human_construct_or_item_candidates"],
            "unique_SAPA_items": inventory_summary["unique_sapa_questionnaire_items_represented"],
        },
        "firewall": {
            "Qwen_only": True,
            "AA7_results_used": False,
            "prior_AA1_hypotheses_used": False,
            "human_respondents_scored": False,
            "human_model_projection": False,
        },
        "privacy": "No respondent-level human data are tracked or emitted.",
        "compute": "CPU only; no GPU, RunPod, model inference, activation extraction, response generation, or external model API.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = verify(args.repo_root.resolve(), args.output_dir.resolve())
    path = args.output_dir.resolve() / "verification_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "check_count": report["check_count"], "failures": report["failures"]}, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
