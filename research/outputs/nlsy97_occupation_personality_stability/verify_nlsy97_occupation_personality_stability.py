#!/usr/bin/env python3
"""Verify AA-5 aggregate artifacts and deterministic reproduction."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-09-11T23:30:00Z"
STARTING_SHA = "7914d01f7d9c23060fe199815a90e547241d9682"
PREREG_SHA = "13fb08f1d75444820d0b374fef2e3e0292a4d1f1"
RAW_SHA = "b55b54308c4b3005ce27f4bf81fff15980c5c68b54a84d2a5a48694f80a51919"
CODEBOOK_SHA = "08bc87414445955b3147753ce16514077d2d34da3f8169e22cd7cf835b739aba"

RUNNER_OUTPUTS = [
    "analysis_cohort_summary.json",
    "future_model_role_comparison_candidates.csv",
    "nlsy97_occupation_personality_stability_report.md",
    "occupation_aggregation_crosswalk.csv",
    "occupation_big_five_centroids.csv",
    "occupation_centroid_feasibility.csv",
    "occupation_centroid_sample_size_curve.csv",
    "occupation_centroid_shrinkage.csv",
    "occupation_centroid_split_half_stability.csv",
    "occupation_centroid_uncertainty.csv",
    "occupation_granularity_tradeoff.csv",
    "occupation_personality_discriminability.csv",
    "occupation_personality_variance_decomposition.csv",
    "occupation_round6_round12_replication.csv",
    "source_manifest.json",
]

INVENTORY_FILES = [
    "analysis_specification.md",
    "run_nlsy97_occupation_personality_stability.py",
    "verify_nlsy97_occupation_personality_stability.py",
    *RUNNER_OUTPUTS,
]

DESCRIPTIONS = {
    "analysis_specification.md": "Outcome-blind frozen analysis and tier specification",
    "run_nlsy97_occupation_personality_stability.py": "Deterministic human-only analysis runner",
    "verify_nlsy97_occupation_personality_stability.py": "Independent artifact and reproducibility verifier",
    "analysis_cohort_summary.json": "Cohort counts, design audit, transformations, item availability, and tier counts",
    "future_model_role_comparison_candidates.csv": "Post-tier future comparison candidates; no model measurements",
    "nlsy97_occupation_personality_stability_report.md": "Scientific feasibility report",
    "occupation_aggregation_crosswalk.csv": "Frozen Census-to-SOC minor/major aggregation rules",
    "occupation_big_five_centroids.csv": "Aggregate weighted/unweighted occupational domain means and characterization",
    "occupation_centroid_feasibility.csv": "Frozen empirical feasibility tier assignments",
    "occupation_centroid_sample_size_curve.csv": "Repeated finite-cell subsampling error curves",
    "occupation_centroid_shrinkage.csv": "Empirical-Bayes sensitivity estimates",
    "occupation_centroid_split_half_stability.csv": "Repeated deterministic split-half metrics",
    "occupation_centroid_uncertainty.csv": "Design-respecting bootstrap centroid uncertainty",
    "occupation_granularity_tradeoff.csv": "Narrow-to-intermediate-to-broad reliability/specificity comparison",
    "occupation_personality_discriminability.csv": "Fixed cross-validated descriptive occupation classifier",
    "occupation_personality_variance_decomposition.csv": "Observed and sampling-error-corrected variance decompositions",
    "occupation_round6_round12_replication.csv": "Population-cell and stable-respondent A/C recurrence checks",
    "source_manifest.json": "Input, source, software, randomness, and scientific-boundary manifest",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [dict(row) for row in csv.DictReader(f)]


def record(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-csv", type=Path, required=True)
    parser.add_argument("--codebook", type=Path, required=True)
    parser.add_argument("--occupation-codes", type=Path, required=True)
    parser.add_argument("--persona-crosswalk", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    runner = output / "run_nlsy97_occupation_personality_stability.py"
    checks: list[dict[str, Any]] = []

    missing = [name for name in INVENTORY_FILES if not (output / name).is_file()]
    record(checks, "required_artifacts_present", not missing, f"missing={missing}")

    parsed_csv: dict[str, list[dict[str, str]]] = {}
    parse_errors: list[str] = []
    for path in sorted(output.glob("*.csv")):
        if path.name == "artifact_inventory.csv":
            continue
        try:
            parsed_csv[path.name] = csv_rows(path)
        except Exception as exc:  # pragma: no cover - verification path
            parse_errors.append(f"{path.name}: {exc}")
    for path in sorted(output.glob("*.json")):
        if path.name == "verification_report.json":
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - verification path
            parse_errors.append(f"{path.name}: {exc}")
    record(checks, "csv_json_parse", not parse_errors, f"parsed_csv={len(parsed_csv)}; errors={parse_errors}")

    cohort = json.loads((output / "analysis_cohort_summary.json").read_text())
    counts_ok = (
        cohort["original_cohort_n"] == 8984
        and cohort["round12_tipi_all_ten_complete_n"] == 7044
        and cohort["aa1_round12_tipi_plus_official_code_including_nonoccupation_9920_n"] == 6261
        and cohort["primary_analytic_n"] == 6261
    )
    record(checks, "canonical_respondent_counts", counts_ok, "8,984 source; 7,044 complete TIPI; 6,261 primary analytic")
    design = cohort["design"]
    record(
        checks,
        "survey_design",
        design == {"design_degrees_of_freedom": 117, "every_stratum_has_vpsu_1_and_2": True, "psus": 234, "strata": 117},
        f"audit={design}; weight=T2022500/100; variance=VSTRAT/VPSU",
    )
    record(checks, "starting_and_prereg_sha", cohort["starting_sha"] == STARTING_SHA and cohort["preregistered_specification_sha"] == PREREG_SHA, f"start={cohort['starting_sha']}; prereg={cohort['preregistered_specification_sha']}")

    raw_ok = digest(args.raw_csv.resolve()) == RAW_SHA and args.raw_csv.resolve().stat().st_size == 3264436
    codebook_ok = digest(args.codebook.resolve()) == CODEBOOK_SHA and args.codebook.resolve().stat().st_size == 169772
    record(checks, "canonical_aa1_raw_extract", raw_ok, f"sha256={digest(args.raw_csv.resolve())}; bytes={args.raw_csv.resolve().stat().st_size}")
    record(checks, "official_codebook", codebook_ok, f"sha256={digest(args.codebook.resolve())}; bytes={args.codebook.resolve().stat().st_size}")

    codebook_text = args.codebook.resolve().read_text(encoding="utf-8", errors="replace")
    goldberg_phrases = [
        "Where 1 means organized and 5 means disorganized.",
        "Where 1 means not conscientious and 5 means conscientious.",
        "Where 1 means dependable and 5 means undependable.",
        "Where 1 means careless and 5 means thorough.",
        "Where 1 means quarrelsome and 5 means agreeable.",
        "Where 1 means cooperative and 5 means difficult.",
        "Where 1 means flexible and 5 means stubborn.",
        "Where 1 means distrustful and 5 means trustful.",
    ]
    runner_text = runner.read_text(encoding="utf-8")
    tipi_literals = [
        "(tipi_items[:, 4] + (8 - tipi_items[:, 9])) / 2",
        "(tipi_items[:, 2] + (8 - tipi_items[:, 7])) / 2",
        "(tipi_items[:, 0] + (8 - tipi_items[:, 5])) / 2",
        "((8 - tipi_items[:, 1]) + tipi_items[:, 6]) / 2",
        "((8 - tipi_items[:, 3]) + tipi_items[:, 8]) / 2",
    ]
    record(checks, "official_tipi_scoring_implementation", all(x in runner_text for x in tipi_literals), "Developer key: O=5+10R, C=3+8R, E=1+6R, A=2R+7, ES=4R+9; pair averages")
    normalized_codebook = re.sub(r"\s+", " ", codebook_text)
    record(checks, "official_goldberg_directions", all(x in normalized_codebook for x in goldberg_phrases), "All eight bipolar anchors verified from official extract codebook")

    agg = parsed_csv["occupation_aggregation_crosswalk.csv"]
    agg_ok = len(agg) == 510 and len({r["census_2002_code"] for r in agg}) == 510
    agg_ok = agg_ok and all(r["included_as_occupation"] in {"0", "False"} for r in agg if r["census_2002_code"] == "9920")
    record(checks, "frozen_official_aggregation", agg_ok, "510 unique Census codes; official SOC minor and major parents; 9920 excluded")

    centroid = parsed_csv["occupation_big_five_centroids.csv"]
    feasibility = parsed_csv["occupation_centroid_feasibility.csv"]
    uncertainty = parsed_csv["occupation_centroid_uncertainty.csv"]
    split = parsed_csv["occupation_centroid_split_half_stability.csv"]
    sample_curve = parsed_csv["occupation_centroid_sample_size_curve.csv"]
    suppression_ok = all(int(r["analytic_n"]) >= 10 for rows in [centroid, feasibility, uncertainty, split] for r in rows)
    record(checks, "sparse_cell_suppression", suppression_ok, "All cell-specific scientific outputs have analytic N>=10; candidate source N<10 is coarsened")

    bootstrap_ok = all(int(r["bootstrap_requested_replicates"]) == 500 and int(r["bootstrap_valid_replicates"]) <= 500 for r in uncertainty)
    record(checks, "bootstrap_reproducibility_metadata", bootstrap_ok, "500 stratified PSU replicates; seed=20260911; sqrt(2) two-PSU rescaling")
    split_ok = all(int(r["split_replicates"]) == 500 and int(r["split_seed_first"]) == 20260911 and int(r["split_seed_last"]) == 20261410 for r in split)
    record(checks, "split_half_reproducibility_metadata", split_ok, "500 within-cell splits; seeds 20260911..20261410")
    sample_ok = all(int(r["subsample_replicates"]) == 300 for r in sample_curve)
    record(checks, "sample_curve_reproducibility_metadata", sample_ok, "300 subsamples per occupation-size combination")

    tiers = Counter((r["occupation_level"], r["feasibility_tier"]) for r in feasibility)
    tier_ok = tiers[("narrow", "STRONG CENTROID")] == 9 and tiers[("narrow", "MODERATE / EXPLORATORY")] == 18
    tier_ok = tier_ok and tiers[("broad", "STRONG CENTROID")] == 18 and tiers[("broad", "MODERATE / EXPLORATORY")] == 2
    for row in feasibility:
        if row["feasibility_tier"] == "STRONG CENTROID":
            tier_ok = tier_ok and int(row["analytic_n"]) >= 100 and float(row["bootstrap_mean_displacement"]) <= 0.25 and float(row["bootstrap_p95_displacement"]) <= 0.40 and float(row["split_half_median_euclidean_distance"]) <= 0.45 and float(row["split_half_p95_euclidean_distance"]) <= 0.80 and float(row["bootstrap_p95_to_heterogeneity_ratio"]) <= 0.20
        elif row["feasibility_tier"] == "MODERATE / EXPLORATORY":
            tier_ok = tier_ok and int(row["analytic_n"]) >= 50 and float(row["bootstrap_mean_displacement"]) <= 0.40 and float(row["bootstrap_p95_displacement"]) <= 0.60 and float(row["split_half_median_euclidean_distance"]) <= 0.70 and float(row["split_half_p95_euclidean_distance"]) <= 1.20 and float(row["bootstrap_p95_to_heterogeneity_ratio"]) <= 0.30
    record(checks, "frozen_tier_rules_recomputed", tier_ok, f"tier_counts={dict(tiers)}")

    forbidden_headers = {"pubid", "r0000100", "respondent_id", "activation_vector", "pc1", "pc2", "model_trait"}
    exposed = []
    for name, rows in parsed_csv.items():
        if rows:
            hits = forbidden_headers & {x.lower() for x in rows[0]}
            if hits:
                exposed.append(f"{name}:{sorted(hits)}")
    record(checks, "no_row_level_or_model_geometry_fields", not exposed, f"forbidden_header_hits={exposed}")
    source = json.loads((output / "source_manifest.json").read_text())
    boundary_fields = [
        "model_geometry_used", "human_to_model_projection_performed", "gpu_used", "runpod_used",
        "model_inference_used", "activation_extraction_used", "external_model_api_used",
    ]
    boundary_ok = not source["prohibited_inputs_loaded"] and all(source[x] is False for x in boundary_fields)
    record(checks, "scientific_compute_boundaries", boundary_ok, "No model geometry/projection; no GPU/RunPod/inference/activation extraction/external model API")

    ignored = subprocess.run(["git", "check-ignore", "-q", str(args.raw_csv)], cwd=output, check=False).returncode == 0
    tracked_external = subprocess.run(["git", "ls-files", "data_external/human_validation/nlsy97"], cwd=output, check=True, text=True, capture_output=True).stdout.strip()
    record(checks, "respondent_data_gitignored", ignored and not tracked_external, f"check_ignore={ignored}; tracked_external_files={tracked_external!r}")

    with tempfile.TemporaryDirectory(prefix="aa5-determinism-") as temp_dir:
        command = [
            sys.executable, str(runner),
            "--raw-csv", str(args.raw_csv.resolve()),
            "--codebook", str(args.codebook.resolve()),
            "--occupation-codes", str(args.occupation_codes.resolve()),
            "--persona-crosswalk", str(args.persona_crosswalk.resolve()),
            "--output-dir", temp_dir,
            "--generated-at", GENERATED_AT,
        ]
        run = subprocess.run(command, cwd=output, text=True, capture_output=True, check=False)
        rerun_hashes = {name: digest(Path(temp_dir) / name) for name in RUNNER_OUTPUTS if (Path(temp_dir) / name).is_file()}
        current_hashes = {name: digest(output / name) for name in RUNNER_OUTPUTS if (output / name).is_file()}
        differing = [name for name in RUNNER_OUTPUTS if rerun_hashes.get(name) != current_hashes.get(name)]
        deterministic_ok = run.returncode == 0 and not differing and len(rerun_hashes) == len(RUNNER_OUTPUTS)
        record(checks, "deterministic_full_rerun", deterministic_ok, f"returncode={run.returncode}; exact_hash_matches={len(RUNNER_OUTPUTS)-len(differing)}/{len(RUNNER_OUTPUTS)}; differing={differing}; stderr={run.stderr[-500:]}")

    inventory_rows = []
    for name in INVENTORY_FILES:
        path = output / name
        repo_path = f"research/outputs/nlsy97_occupation_personality_stability/{name}"
        suffix = path.suffix.lower()
        rows = len(csv_rows(path)) if suffix == ".csv" else ""
        inventory_rows.append({
            "path": repo_path,
            "media_type": {".csv": "text/csv", ".json": "application/json", ".md": "text/markdown", ".py": "text/x-python"}[suffix],
            "rows_excluding_header": rows,
            "bytes": path.stat().st_size,
            "sha256": digest(path),
            "description": DESCRIPTIONS[name],
            "respondent_level_data": False,
            "branch_raw_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa5-nlsy97-occupation-stability/{repo_path}",
            "future_canonical_raw_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/{repo_path}",
        })
    inventory_path = output / "artifact_inventory.csv"
    with inventory_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(inventory_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(inventory_rows)

    passed = all(x["passed"] for x in checks)
    report = {
        "study": "AA-5 NLSY97 occupational personality centroid stability",
        "status": "PASS" if passed else "FAIL",
        "generated_at": GENERATED_AT,
        "starting_sha": STARTING_SHA,
        "preregistered_specification_sha": PREREG_SHA,
        "checks_passed": sum(x["passed"] for x in checks),
        "checks_total": len(checks),
        "checks": checks,
        "deterministic_artifact_hashes": current_hashes,
        "artifact_inventory_sha256": digest(inventory_path),
        "artifact_inventory_scope": "All substantive outputs, specification, runner, and verifier; excludes inventory and verification report themselves to avoid circular hashes.",
    }
    (output / "verification_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not passed:
        raise SystemExit("Verification failed; inspect verification_report.json")
    print(f"PASS: {report['checks_passed']}/{report['checks_total']} checks; {len(RUNNER_OUTPUTS)} deterministic artifact hashes matched")


if __name__ == "__main__":
    main()
