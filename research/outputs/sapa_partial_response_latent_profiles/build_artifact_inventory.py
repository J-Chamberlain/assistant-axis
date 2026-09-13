#!/usr/bin/env python3
"""Build the self-excluding aggregate artifact inventory for this analysis."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output_dir.resolve()
    inventory_path = output / "artifact_inventory.csv"
    rows = []
    for path in sorted(output.iterdir()):
        if not path.is_file() or path.name == inventory_path.name:
            continue
        relative = path.relative_to(repo).as_posix()
        introducing = git(
            repo, "log", "--diff-filter=A", "--format=%H", "--reverse", "--", relative
        ).splitlines()
        latest = git(repo, "log", "-1", "--format=%H", "--", relative)
        if not introducing or not latest:
            raise RuntimeError(f"artifact is not committed: {relative}")
        rows.append(
            {
                "path": relative,
                "status": "active",
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "canonical_raw_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/{relative}",
                "artifact_type": path.suffix.lstrip("."),
                "contains_respondent_rows": False,
                "introducing_commit": introducing[0],
                "latest_material_commit": latest,
            }
        )
    with inventory_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} aggregate artifacts to {inventory_path}")


if __name__ == "__main__":
    main()
