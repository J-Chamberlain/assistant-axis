#!/usr/bin/env python3
"""Inventory the externally anchored Big Five bundle with branch and future-master URLs."""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REPOSITORY = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis"
BRANCH = "codex/aa2-big-five-audit"


def main() -> None:
    rows = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.name == "artifact_inventory.csv":
            continue
        relative = path.relative_to(ROOT).as_posix()
        rows.append(
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "status": "active",
                "branch_raw_url": f"{REPOSITORY}/{BRANCH}/{relative}",
                "future_master_raw_url": f"{REPOSITORY}/master/{relative}",
            }
        )
    with (HERE / "artifact_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
