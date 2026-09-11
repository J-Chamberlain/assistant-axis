#!/usr/bin/env python3
"""Deterministically verify the committed SAPA/NLSY97 feasibility artifacts.

The script reads respondent-level source files only from the gitignored
``data_external`` tree. It emits no respondent rows, identifiers, or sensitive
subgroup outcome tables.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


TIPI = [f"T316250{i}" for i in range(10)]
GOLDBERG = [f"S0920{i}00" for i in range(8)]
R12_OCC = [f"T{31869 + i:05d}00" for i in range(8)]
R6_OCC = [f"S{16030 + i:05d}00" for i in range(11)]
RAW_PREFIX = Path("data_external/human_validation")
OUTPUT_REL = Path("research/outputs/human_trait_dataset_feasibility")
RAW_BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def split_ids(value: object) -> list[str]:
    if pd.isna(value) or not str(value).strip():
        return []
    return [item for item in str(value).split(";") if item]


def valid(series: pd.Series, low: float, high: float) -> pd.Series:
    return series.between(low, high, inclusive="both")


def roster_value(data: pd.DataFrame, flag: str, variables: list[str]) -> pd.Series:
    result = np.full(len(data), np.nan)
    for loop, variable in enumerate(variables, 1):
        mask = data[flag].eq(loop)
        result[mask] = data.loc[mask, variable]
    return pd.Series(result, index=data.index)


def add_check(checks: dict[str, bool], name: str, condition: object) -> None:
    checks[name] = bool(condition)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--write-inventory", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = repo / OUTPUT_REL
    sapa = output / "sapa"
    nlsy = output / "nlsy97"
    checks: dict[str, bool] = {}

    traits = read_json(repo / "data/traits/trait_list.json")
    crosswalk = pd.read_csv(sapa / "sapa_model_trait_candidate_crosswalk.csv")
    items = pd.read_csv(sapa / "sapa_item_dictionary.csv")
    scales = pd.read_csv(sapa / "sapa_scale_inventory.csv")
    sapa_summary = read_json(sapa / "sapa_trait_coverage_summary.json")
    item_ids = set(items.item_id)
    scale_names = set(scales.scale_id) | set(scales.scale_name)

    add_check(checks, "canonical_model_traits_240_unique", len(traits) == len(set(traits)) == 240)
    add_check(checks, "crosswalk_exactly_matches_canonical_trait_order", crosswalk.model_trait.tolist() == list(traits))
    add_check(checks, "canonical_definitions_match", crosswalk.canonical_definition.tolist() == list(traits.values()))
    add_check(checks, "sapa_item_ids_696_unique", len(items) == items.item_id.nunique() == 696)
    add_check(checks, "sapa_scale_ids_or_names_valid", scales.scale_id.notna().all() and scales.scale_name.notna().all())
    add_check(checks, "sapa_coverage_categories_valid", set(crosswalk.coverage_category) <= {0, 1, 2, 3})
    referenced_items = {
        value
        for column in ["candidate_item_ids", "accepted_evidence_item_ids", "lexical_candidate_item_ids", "semantic_candidate_item_ids"]
        for cell in crosswalk[column]
        for value in split_ids(cell)
    }
    referenced_scales = {value for cell in crosswalk.candidate_scale_names for value in split_ids(cell)}
    add_check(checks, "sapa_crosswalk_item_references_valid", referenced_items <= item_ids)
    add_check(checks, "sapa_crosswalk_scale_references_valid", referenced_scales <= scale_names)
    coverage = crosswalk.coverage_category.value_counts().to_dict()
    add_check(checks, "sapa_coverage_counts_reproduce", (
        coverage.get(3, 0) == sapa_summary["category_3_direct_or_near_direct"]
        and coverage.get(2, 0) == sapa_summary["category_2_close_narrow"]
        and coverage.get(1, 0) == sapa_summary["category_1_broad_only"]
        and coverage.get(0, 0) == sapa_summary["category_0_no_defensible_coverage"]
    ))

    sapa_manifest = read_json(sapa / "sapa_source_manifest.json")
    add_check(checks, "sapa_source_hashes_match", all(
        Path(entry["local_path"]).exists() and sha256(Path(entry["local_path"])) == entry["sha256"]
        for entry in sapa_manifest["files"]
    ))
    sapa_raw = repo / RAW_PREFIX / "sapa/doi_10.7910_DVN_SD7SVE/sapaTempData696items08dec2013thru26jul2014.tab"
    sapa_header = pd.read_csv(sapa_raw, sep="\t", nrows=0).columns
    with sapa_raw.open(encoding="utf-8", errors="replace") as handle:
        respondent_rows = sum(1 for _ in handle) - 1
    add_check(checks, "sapa_raw_dimensions_reproduce", respondent_rows == 23679 and sum(c.startswith("q_") for c in sapa_header) == 696 and len(sapa_header) == 719)

    variable_manifest = pd.read_csv(nlsy / "nlsy97_variable_manifest.csv", dtype=str).fillna("")
    personality = pd.read_csv(nlsy / "nlsy97_personality_item_manifest.csv", dtype=str).fillna("")
    occupation = pd.read_csv(nlsy / "nlsy97_2002_census_occupation_codes.csv", dtype=str).fillna("")
    persona_crosswalk = pd.read_csv(nlsy / "nlsy97_persona_occupation_crosswalk.csv", dtype=str).fillna("")
    nlsy_summary = read_json(nlsy / "nlsy97_personality_occupation_cell_summary.json")
    add_check(checks, "nlsy_variable_ids_unique", variable_manifest.variable_id.nunique() == len(variable_manifest))
    add_check(checks, "nlsy_manifest_has_official_documentation", variable_manifest.official_documentation.str.len().gt(0).all() and variable_manifest.source_url.str.startswith("https://www.nlsinfo.org/").all())
    add_check(checks, "nlsy_personality_ids_unique", personality.variable_id.nunique() == len(personality))
    add_check(checks, "nlsy_tipi_and_goldberg_exact_counts", personality.variable_id.isin(TIPI).sum() == 10 and personality.variable_id.isin(GOLDBERG).sum() == 8)
    add_check(checks, "official_occupation_codes_510_unique", len(occupation) == occupation.census_2002_code.nunique() == 510)
    official_codes = set(occupation.census_2002_code)
    accepted_codes = {code for cell in persona_crosswalk.nlsy97_census_2002_codes for code in split_ids(cell)}
    add_check(checks, "occupation_crosswalk_codes_valid", accepted_codes <= official_codes)

    nlsy_raw = repo / RAW_PREFIX / "nlsy97/public_use_extract/human_trait_dataset_feasibility_final.csv"
    data = pd.read_csv(nlsy_raw)
    add_check(checks, "nlsy_raw_8984_unique", len(data) == data.R0000100.nunique() == 8984)
    tipi_complete = np.logical_and.reduce([valid(data[v], 1, 7) for v in TIPI])
    goldberg_complete = np.logical_and.reduce([valid(data[v], 1, 5) for v in GOLDBERG])
    r12_occ = roster_value(data, "T2009700", R12_OCC).map(lambda value: f"{int(value):04d}" if pd.notna(value) and value > 0 else "")
    r6_occ = roster_value(data, "S1549402", R6_OCC).map(lambda value: f"{int(value):04d}" if pd.notna(value) and value > 0 else "")
    r12_base = tipi_complete & r12_occ.isin(official_codes)
    r6_base = goldberg_complete & r6_occ.isin(official_codes)
    add_check(checks, "nlsy_primary_counts_reproduce", (
        int(tipi_complete.sum()) == nlsy_summary["round12_tipi_all_ten_complete_n"]
        and int(r12_base.sum()) == nlsy_summary["round12_tipi_plus_same_wave_occupation_n"]
        and int(goldberg_complete.sum()) == nlsy_summary["round6_goldberg_all_eight_complete_n"]
        and int(r6_base.sum()) == nlsy_summary["round6_goldberg_plus_same_wave_occupation_n"]
    ))
    overlap = pd.read_csv(nlsy / "nlsy97_wave_overlap_summary.csv")
    expected_overlap = {
        "Original NLSY97 cohort": len(data),
        "Round-12 TIPI all ten items complete": int(tipi_complete.sum()),
        "Round-12 TIPI + same-wave current/current-most-recent occupation": int(r12_base.sum()),
        "Round-6 Goldberg all eight items complete": int(goldberg_complete.sum()),
        "Round-6 Goldberg + same-wave current/current-most-recent occupation": int(r6_base.sum()),
        "Round-12 TIPI + same-wave occupation + later employment outcome": int((r12_base & data.Z9061900.between(0, 52)).sum()),
        "Round-12 TIPI + same-wave occupation + later education outcome": int((r12_base & data.T3606300.ge(0)).sum()),
        "Round-12 TIPI + same-wave occupation + later justice outcome": int((r12_base & data.T4501000.isin([0, 1])).sum()),
        "Round-12 TIPI + same-wave occupation + later health outcome": int((r12_base & data.T4562200.between(1, 5)).sum()),
        "Round-12 TIPI + same-wave occupation + later substance use outcome": int((r12_base & data.T4495500.ge(0)).sum()),
        "Round-12 TIPI + same-wave occupation + later family income outcome": int((r12_base & data.T3606500.ge(0)).sum()),
        "Round-12 TIPI + same-wave occupation + later marital status outcome": int((r12_base & data.T3611000.ge(0)).sum()),
    }
    actual_overlap = overlap.set_index("sample").respondent_n.astype(int).to_dict()
    add_check(checks, "nlsy_wave_overlap_counts_reproduce", actual_overlap == expected_overlap)

    nlsy_manifest = read_json(nlsy / "nlsy97_source_manifest.json")
    add_check(checks, "nlsy_source_hashes_match", all(
        Path(entry["local_path"]).exists() and sha256(Path(entry["local_path"])) == entry["sha256"]
        for entry in nlsy_manifest["files"]
    ))
    add_check(checks, "raw_human_data_gitignored", subprocess.run(
        ["git", "check-ignore", str(RAW_PREFIX / "sapa"), str(RAW_PREFIX / "nlsy97")],
        cwd=repo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0)

    # Execute both generators twice with a frozen timestamp and require every
    # emitted file to agree byte-for-byte. This checks the full candidate,
    # classification, counting, and manifest pipelines rather than only seeds.
    fixed_time = "2000-01-01T00:00:00Z"
    with tempfile.TemporaryDirectory(prefix="human-feasibility-determinism-") as tmp:
        temp = Path(tmp)
        reproducible = True
        commands = [
            [
                sys.executable, str(output / "scripts/audit_sapa_trait_coverage.py"),
                "--raw-dir", str((repo / RAW_PREFIX / "sapa/doi_10.7910_DVN_SD7SVE").resolve()),
                "--traits", str((repo / "data/traits/trait_list.json").resolve()),
                "--generated-at", fixed_time,
            ],
            [
                sys.executable, str(output / "scripts/audit_nlsy97_feasibility.py"),
                "--raw-dir", str((repo / RAW_PREFIX / "nlsy97/public_use_extract").resolve()),
                "--occupation-xls", str((repo / RAW_PREFIX / "nlsy97/occupation_crosswalks/2002-census-occupation-codes.xls").resolve()),
                "--prior-crosswalk", str((repo / "research/outputs/occupation_population_persona_join/role_occupation_mapping.csv").resolve()),
                "--generated-at", fixed_time,
            ],
        ]
        for number, base_command in enumerate(commands):
            destinations = [temp / f"job-{number}-a", temp / f"job-{number}-b"]
            for destination in destinations:
                subprocess.run(base_command + ["--output-dir", str(destination)], check=True, cwd=repo)
            left = {path.relative_to(destinations[0]): sha256(path) for path in destinations[0].rglob("*") if path.is_file()}
            right = {path.relative_to(destinations[1]): sha256(path) for path in destinations[1].rglob("*") if path.is_file()}
            reproducible &= left == right
        add_check(checks, "full_generators_byte_reproducible_with_fixed_timestamp", reproducible)

    csv_files = sorted(output.rglob("*.csv"))
    json_files = sorted(output.rglob("*.json"))
    try:
        for path in csv_files:
            with path.open(newline="", encoding="utf-8") as handle:
                list(csv.reader(handle))
        for path in json_files:
            read_json(path)
        parsable = True
    except (csv.Error, json.JSONDecodeError, UnicodeDecodeError):
        parsable = False
    add_check(checks, "all_csv_json_parse", parsable)
    forbidden_headers = {"RID", "PUBID", "R0000100", "respondent_id", "case_id"}
    committed_headers = {
        header
        for path in csv_files
        if path.name != "artifact_inventory.csv"
        for header in pd.read_csv(path, nrows=0).columns
    }
    add_check(checks, "no_respondent_identifier_columns_in_derived_csvs", not (forbidden_headers & committed_headers))
    add_check(checks, "no_respondent_level_csv_shape_in_output", max((sum(1 for _ in path.open(encoding="utf-8", errors="ignore")) - 1 for path in csv_files), default=0) < 1000)

    inventory_path = output / "artifact_inventory.csv"
    if inventory_path.exists() and not args.write_inventory:
        inventory = pd.read_csv(inventory_path, dtype=str).fillna("")
        inventory_ok = True
        for row in inventory.itertuples(index=False):
            path = repo / row.path
            inventory_ok &= path.exists() and str(path.stat().st_size) == row.bytes and sha256(path) == row.sha256
        add_check(checks, "artifact_inventory_hashes_match", inventory_ok)
    else:
        add_check(checks, "artifact_inventory_hashes_match", args.write_inventory)

    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "privacy": {
            "respondent_level_human_microdata_committed": False,
            "human_respondents_assigned_llm_persona": False,
            "human_to_model_pca_projection_performed": False,
            "sensitive_outcomes": "Only metadata and a whole-sample overlap count were emitted; no respondent or occupation-specific justice outcomes.",
        },
        "reproduction": {
            "canonical_trait_source": "data/traits/trait_list.json",
            "sapa_raw_source": str(sapa_raw.relative_to(repo)),
            "nlsy97_raw_source": str(nlsy_raw.relative_to(repo)),
            "raw_sources_gitignored": True,
        },
        "generated_at": generated,
    }
    report_path = output / "verification_report.json"
    if not args.check_only:
        report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if args.write_inventory:
        artifacts = sorted(
            path for path in output.rglob("*")
            if path.is_file()
            and path != inventory_path
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        )
        rows = []
        for path in artifacts:
            relative = path.relative_to(repo).as_posix()
            rows.append({
                "path": relative,
                "status": "active",
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "canonical_raw_url": RAW_BASE + relative,
                "artifact_type": path.suffix.lstrip(".") or "file",
                "contains_respondent_rows": False,
            })
        with inventory_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit(f"Verification failed: {failed}")


if __name__ == "__main__":
    main()
