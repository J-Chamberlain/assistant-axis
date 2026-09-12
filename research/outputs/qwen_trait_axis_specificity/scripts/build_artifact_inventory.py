#!/usr/bin/env python3
"""Build SHA256/URL inventory for safe Qwen axis-specificity artifacts."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd


BRANCH = "codex/aa1-qwen-axis-specificity"
INTRODUCING_COMMIT = "PENDING_FINAL_COMMIT"
STATUS = "active"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(repo: Path, output: Path, commit: str) -> None:
    rows = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == "artifact_inventory.csv" or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(repo).as_posix()
        suffix = path.suffix.lower()
        safe_text = suffix in {".csv", ".json", ".md", ".py", ".svg"}
        rows.append(
            {
                "path": relative,
                "artifact_status": STATUS,
                "artifact_role": "primary_report"
                if path.name == "qwen_axis_specific_family_report.md"
                else "verification"
                if path.name == "verification_report.json"
                else "reproducible_source"
                if suffix == ".py"
                else "diagnostic_figure"
                if suffix in {".png", ".svg"}
                else "derived_analysis",
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "introducing_commit": commit,
                "branch_raw_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/{BRANCH}/{relative}"
                if safe_text
                else "",
                "future_canonical_url": f"https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/{relative}"
                if safe_text
                else "",
                "redistribution_safe": "yes; aggregate/saved-model metadata only",
            }
        )
    pd.DataFrame(rows).to_csv(output / "artifact_inventory.csv", index=False)
    print(f"inventoried {len(rows)} artifacts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--commit", default=INTRODUCING_COMMIT)
    args = parser.parse_args()
    main(args.repo_root.resolve(), args.output_dir.resolve(), args.commit)
