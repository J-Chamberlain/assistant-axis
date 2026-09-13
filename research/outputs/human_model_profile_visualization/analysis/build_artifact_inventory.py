#!/usr/bin/env python3
"""Inventory every peer artifact in the AA-12 visualization packet."""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve()
OUT = HERE.parents[1]
REPO = HERE.parents[4]
INVENTORY = OUT / "artifact_inventory.csv"
RAW_BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"


DESCRIPTIONS = {
    "human_model_profile_visualization.html": "Self-contained reader-first aggregate correspondence inspection report",
    "visualization_report.md": "Methods, figure guide, bounded visual decompositions, and interpretation limits",
    "visualization_data_manifest.json": "Frozen source hashes, checkpoints, source tables, and visualization scope",
    "numerical_reproduction_checks.json": "Twenty exact frozen-result reproduction checks",
    "figure_inventory.csv": "Static figure source, provenance, hash, format, and reuse inventory",
    "verification_report.json": "Independent 118-check deterministic and headless-browser verification",
    "startup_verification_record.json": "Required exact-master-URL startup and branch-base verification record",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def introducing_commit(rel: str) -> str:
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", rel],
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.splitlines()
    if not result:
        raise RuntimeError(f"No introducing commit for {rel}; commit peer artifacts before inventory")
    return result[-1]


def description(path: Path) -> str:
    if path.name in DESCRIPTIONS:
        return DESCRIPTIONS[path.name]
    rel = path.relative_to(OUT)
    if rel.parts[0] == "figures":
        return "Frozen-result static inspection figure: " + path.stem.replace("_", " ")
    if rel.parts[0] == "data":
        return "Deterministic aggregate figure-source table: " + path.stem.replace("_", " ")
    if rel.parts[0] == "analysis":
        return "Deterministic visualization packet script: " + path.name
    return path.name


def main() -> None:
    paths = sorted(p for p in OUT.rglob("*") if p.is_file() and p != INVENTORY)
    rows = []
    for path in paths:
        rel = str(path.relative_to(REPO))
        rows.append(
            {
                "path": rel,
                "status": "active",
                "category": "aggregate human/model correspondence visualization",
                "description": description(path),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
                "format": path.suffix.lstrip("."),
                "introducing_commit": introducing_commit(rel),
                "raw_github_url": RAW_BASE + rel,
                "privacy": "aggregate/non-respondent-level",
            }
        )
    with INVENTORY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Inventoried {len(rows)} peer artifacts (inventory self-excluded)")


if __name__ == "__main__":
    main()
