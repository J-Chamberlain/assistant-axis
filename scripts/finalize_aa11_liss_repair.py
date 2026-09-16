#!/usr/bin/env python3
"""Validate and inventory the repaired AA-11 package without respondent data."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/outputs/liss_hifwb_prior_evidence"
BRANCH = "codex/aa11-liss-hifwb-repair-v2"
RAW = f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/{BRANCH}/"
REPAIR_COMMITS = "815a2a3;d86b332;ee315eb;c4bcce5"
SCRIPTS = [
    "scripts/repair_aa11_liss_package.py", "scripts/finalize_aa11_liss_repair.py",
    "scripts/liss_common.py", "scripts/verify_liss_2020_sources.py",
    "scripts/validate_liss_2020_schema.py", "scripts/score_liss_bigfive.py",
    "scripts/score_liss_hifwb.py", "scripts/fit_liss_hifwb_measurement_models.py",
    "scripts/fit_liss_personality_wellbeing_models.py", "scripts/run_liss_2020_hifwb.py",
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

for path in OUT.glob("*.csv"):
    with path.open(newline="", encoding="utf-8") as handle:
        list(csv.reader(handle))
for path in OUT.glob("*.json"):
    json.loads(path.read_text(encoding="utf-8"))

main_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in OUT.glob("*") if p.name != "aa12_followup_alignment_notes.md")
for forbidden in ("Independent profile-group correspondence", "PC-pole profile correspondence", "Trait-relationship structural correspondence"):
    if forbidden.lower() in main_text.lower():
        raise SystemExit(f"off-scope framing remains: {forbidden}")

paths = sorted([p.relative_to(ROOT).as_posix() for p in OUT.glob("*") if p.is_file()] + SCRIPTS)
inventory = OUT / "artifact_inventory.csv"
with inventory.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(["path", "status", "artifact_type", "bytes", "sha256", "introduced_commit", "repair_commits", "raw_url"])
    for relative in paths:
        path = ROOT / relative
        artifact_type = "human-only pre-data evidence/planning artifact" if relative.startswith("research/") else "local-only pre-data execution/verification script"
        introduced = "768528c" if relative not in {
            "research/outputs/liss_hifwb_prior_evidence/hifwb_characteristic_prior_evidence.csv",
            "research/outputs/liss_hifwb_prior_evidence/liss_hifwb_novelty_matrix.csv",
            "research/outputs/liss_hifwb_prior_evidence/liss_modifiable_variable_inventory.csv",
            "research/outputs/liss_hifwb_prior_evidence/liss_modifiable_pathway_program.md",
            "research/outputs/liss_hifwb_prior_evidence/liss_longitudinal_local_pathway_spec.md",
            "research/outputs/liss_hifwb_prior_evidence/public_dataset_pathway_matrix.csv",
            "research/outputs/liss_hifwb_prior_evidence/aa12_followup_alignment_notes.md",
            "scripts/repair_aa11_liss_package.py", "scripts/finalize_aa11_liss_repair.py"} else "AA-11 repair commits"
        writer.writerow([relative, "active", artifact_type, path.stat().st_size,
                         "SELF_REFERENTIAL" if path == inventory else digest(path), introduced, REPAIR_COMMITS, RAW + relative])
print(json.dumps({"status": "verified_and_inventoried", "artifacts": len(paths), "respondent_data_accessed": False}, indent=2))
