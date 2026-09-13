#!/usr/bin/env python3
"""Build the safe aggregate artifact inventory with git-introduction lineage."""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BRANCH = "codex/aa12-human-model-profile-correspondence"


def git_log(path: str, introducing: bool) -> str:
    args = ["git", "log"]
    if introducing:
        # The introducing commit is for this exact path. Do not follow rename
        # similarity into a different analysis directory.
        args += ["--diff-filter=A"]
    args += ["-1", "--format=%H", "--", path]
    return subprocess.check_output(args, cwd=REPO, text=True).strip()


def main() -> None:
    paths = sorted(
        p for p in HERE.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.name != "artifact_inventory.csv"
    )
    rows = []
    for path in paths:
        rel = path.relative_to(REPO).as_posix()
        data = path.read_bytes()
        intro = git_log(rel, True)
        latest = git_log(rel, False)
        if not intro:
            raise RuntimeError(f"Artifact has not yet been committed: {rel}")
        rows.append({
            "path": rel,
            "status": "active",
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "artifact_type": path.suffix.lstrip(".") or "none",
            "contains_respondent_level_human_data": False,
            "introducing_commit": intro,
            "latest_material_commit": latest,
            "branch_raw_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/{BRANCH}/{rel}",
            "canonical_raw_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/{rel}",
        })
    fields = list(rows[0])
    with (HERE / "artifact_inventory.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    print(f"wrote {len(rows)} artifact rows")


if __name__ == "__main__":
    main()
