#!/usr/bin/env python3
"""Replace stale AA-11 rows in the canonical machine-readable file index."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "research/REPO_FILE_INDEX.csv"
PACKAGE = ROOT / "research/outputs/liss_hifwb_prior_evidence"
BRANCH = "codex/aa11-liss-hifwb-repair-v2"
RAW = f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/{BRANCH}/"
SCRIPT_NAMES = [
    "repair_aa11_liss_package.py", "finalize_aa11_liss_repair.py", "update_aa11_navigation_index.py",
    "liss_common.py", "verify_liss_2020_sources.py", "validate_liss_2020_schema.py",
    "score_liss_bigfive.py", "score_liss_hifwb.py", "fit_liss_hifwb_measurement_models.py",
    "fit_liss_personality_wellbeing_models.py", "run_liss_2020_hifwb.py",
]

with INDEX.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    header = reader.fieldnames
    rows = [r for r in reader if "liss_hifwb_prior_evidence" not in r["path"] and r["path"] not in {f"scripts/{n}" for n in SCRIPT_NAMES} and r["path"] != "scripts/build_aa11_liss_package.py"]

paths = sorted(PACKAGE.glob("*")) + [ROOT / "scripts" / name for name in SCRIPT_NAMES]
for path in paths:
    if not path.is_file():
        continue
    relative = path.relative_to(ROOT).as_posix()
    status = "deprecated" if relative == "scripts/build_aa11_liss_package.py" else "active"
    rows.append({"path": relative, "category": "active analyses", "status": status,
                 "description": "AA-11 repaired human-only LISS/HiFWB pre-data artifact" if relative.startswith("research/") else "AA-11 repaired local pre-data execution/verification script",
                 "raw_github_url": RAW + relative, "size_bytes": str(path.stat().st_size),
                 "extension": path.suffix, "updated_utc": "2026-09-15T00:00:00Z"})

rows.sort(key=lambda row: row["path"])
with INDEX.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
print(f"indexed {len(paths)} repaired AA-11 paths; total rows {len(rows)}")
