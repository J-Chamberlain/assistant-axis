#!/usr/bin/env python3
"""Build hashes and raw URLs for all committed analysis artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


BRANCH = "codex/aa1-qwen-trait-family-human-inventory"
REPO_SLUG = "J-Chamberlain/assistant-axis"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def description(name: str) -> str:
    descriptions = {
        "qwen_pc_trait_family_human_inventory.csv": "Main machine-readable Qwen family to SAPA construct/item inventory with exhaustive display wording.",
        "qwen_pc_trait_family_human_inventory_report.md": "Readable PC1-PC6 positive/negative family and human-measurement inventory report.",
        "qwen_trait_pc_correlations_all.csv": "All 1,440 Qwen PC-by-trait Pearson, Spearman, FDR, rank, and bootstrap records.",
        "qwen_trait_family_membership_primary.csv": "All memberships passing the frozen primary effect, FDR, and sign-stability rule.",
        "qwen_trait_family_threshold_sensitivity.csv": "Trait membership at frozen absolute-r thresholds 0.40, 0.50, and 0.60.",
        "qwen_trait_family_selection_spec.md": "Preregistered mechanical family selection and firewall specification.",
        "qwen_trait_family_summaries.csv": "Twelve PC-pole summaries with complete ordered members and sensitivity counts.",
        "qwen_trait_family_report.md": "Readable numeric Qwen family report before SAPA mapping.",
        "qwen_trait_family_blinded_mapping_packet.csv": "Frozen neutral-ID packet used for SAPA mapping without PC labels or prior interpretations.",
        "qwen_trait_family_blind_manifest.json": "Blind packet seed, exclusions, and source hashes.",
        "qwen_trait_family_human_mapping_judgments.csv": "Frozen neutral-family semantic judgments against the full SAPA construct library.",
        "inventory_summary.json": "Aggregate family match and construct/item reuse counts.",
        "source_manifest.json": "Source hashes, counts, audit commits, privacy boundary, and Qwen-only firewall.",
        "numeric_source_manifest.json": "Numerical selection source hashes, seeds, thresholds, and family counts.",
        "verification_report.json": "Deterministic numerical, blind-packet, inventory, privacy, and firewall verification.",
    }
    return descriptions.get(name, "Reproducible analysis source script.")


def build(repo: Path, output: Path) -> None:
    rows = []
    for path in sorted(output.rglob("*")):
        if not path.is_file() or path.name == "artifact_inventory.csv" or path.suffix == ".pyc" or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(repo).as_posix()
        rows.append({
            "path": relative,
            "status": "active",
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "branch_raw_url": f"https://raw.githubusercontent.com/{REPO_SLUG}/{BRANCH}/{relative}",
            "canonical_raw_url": f"https://raw.githubusercontent.com/{REPO_SLUG}/master/{relative}",
            "description": description(path.name),
        })
    with (output / "artifact_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "status", "sha256", "bytes", "branch_raw_url", "canonical_raw_url", "description"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} artifact records")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    build(args.repo_root.resolve(), args.output_dir.resolve())


if __name__ == "__main__":
    main()
