#!/usr/bin/env python3
"""Build the AA-10 artifact inventory after the analysis commit exists."""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


BRANCH = "codex/aa10-crossmodel-pc-trait-specificity"
ANALYSIS_COMMIT = "d64f7efbd656765b2cd126b9c1f207c7c38b23cd"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    output = Path(__file__).resolve().parent
    repo = output.parents[2]
    actual = subprocess.run(
        ["git", "rev-parse", f"{ANALYSIS_COMMIT}^{{commit}}"], cwd=repo,
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if actual != ANALYSIS_COMMIT:
        raise ValueError("Analysis commit constant does not resolve exactly")
    rows = []
    for path in sorted(output.iterdir()):
        if not path.is_file() or path.name == "artifact_inventory.csv" or path.name.startswith("."):
            continue
        relative = path.relative_to(repo).as_posix()
        history = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H", "--reverse", "--", relative],
            cwd=repo, check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        introducing_commit = history[0] if history else ANALYSIS_COMMIT
        rows.append({
            "path": relative,
            "status": "active",
            "introducing_commit": introducing_commit,
            "size_bytes": path.stat().st_size,
            "sha256": digest(path),
            "branch_raw_github_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/{BRANCH}/{relative}",
            "future_canonical_master_raw_github_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/{relative}",
        })
    with (output / "artifact_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} inventory rows")


if __name__ == "__main__":
    main()
