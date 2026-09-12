#!/usr/bin/env python3
"""Build the AA-7 artifact inventory after analysis artifacts are committed."""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BRANCH = "codex/aa7-human-trait-convergence"
PREFIX = "research/outputs/human_supported_trait_convergence"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def introducing_commit(relative: str) -> str:
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--follow", "--format=%H", "--", relative],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    commits = [line for line in result.stdout.splitlines() if line]
    return commits[-1] if commits else "PENDING"


def description(name: str) -> str:
    exact = {
        "human_supported_trait_convergence_report.md": "Main AA-7 scientific report",
        "human_supported_trait_set_freeze.json": "Pre-outcome freeze of the 12 AA-1-supported traits",
        "analysis_preregistration.json": "Pre-outcome AA-7 analysis and decision specification",
        "source_manifest.json": "Input hashes, software, source reproduction, and scientific boundaries",
        "verification_report.json": "Independent 82-check integrity, leakage, and byte-reproduction report",
        "primary_decisions.json": "Machine-readable preregistered evidence and later-study decisions",
        "run_human_supported_trait_convergence.py": "CPU-only reproducible AA-7 analysis runner",
        "verify_human_supported_trait_convergence.py": "Independent AA-7 verification and full reproduction runner",
        "build_artifact_inventory.py": "Reproducible artifact hash and provenance inventory builder",
        "procrustes_alignment_matrices.json": "Full-fit PC1-PC3/PC1-PC6 alignment transforms",
        "aligned_agreeableness_focal_test.json": "Preregistered focal Agreeableness reconciliation result",
    }
    if name in exact:
        return exact[name]
    if name.startswith("figure_"):
        return "Static scientific figure: " + name.removeprefix("figure_").rsplit(".", 1)[0].replace("_", " ")
    if "distribution" in name:
        return "Matched held-out control-bank distribution"
    if name.endswith(".csv"):
        return "AA-7 tabular analysis artifact: " + name.removesuffix(".csv").replace("_", " ")
    return "AA-7 reproducibility artifact"


def main() -> None:
    files = sorted(
        path for path in HERE.iterdir()
        if path.is_file() and path.name != "artifact_inventory.csv" and not path.name.startswith(".")
    )
    destination = HERE / "artifact_inventory.csv"
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "path", "status", "description", "size_bytes", "sha256", "introducing_commit",
            "branch_raw_github_url", "future_canonical_master_raw_github_url",
        ])
        writer.writeheader()
        for path in files:
            relative = f"{PREFIX}/{path.name}"
            writer.writerow({
                "path": relative,
                "status": "active",
                "description": description(path.name),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "introducing_commit": introducing_commit(relative),
                "branch_raw_github_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/{BRANCH}/{relative}",
                "future_canonical_master_raw_github_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/{relative}",
            })
    print(f"wrote {destination} with {len(files)} artifacts")


if __name__ == "__main__":
    main()
