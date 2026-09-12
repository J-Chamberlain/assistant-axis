#!/usr/bin/env python3
"""Build hashes and branch/canonical raw URLs for specificity artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


BRANCH = "codex/aa1-qwen-pc-trait-specificity"
REPO_SLUG = "J-Chamberlain/assistant-axis"


DESCRIPTIONS = {
    "qwen_trait_cross_pc_specificity_all.csv": "All 1,440 Qwen trait-target rows with six signed correlations, observed specificity, and paired-bootstrap distributions.",
    "qwen_pc_trait_specificity_spec.md": "Pre-results frozen distinction, rules, seeds, tiers, Pareto universe, sensitivity grid, and composite policy.",
    "qwen_pc_defining_trait_sets.csv": "All 1,440 trait-target rows labeled for associated, PC-defining, concentration-tier, and all-trait Pareto status.",
    "qwen_pc_trait_specificity_pareto.csv": "All-trait strength-margin-concentration dominance classification within each PC and signed pole.",
    "qwen_pc_specificity_threshold_sensitivity.csv": "Twelve-family counts and trait lists over the complete 3x3 effect/dominance grid plus concentration sensitivity.",
    "qwen_pc_specificity_report.md": "Readable associated-versus-defining results, focal PC1/PC3 inspection, human coverage, reference composite, and epistemic boundaries.",
    "pc3_reference_composite_audit.md": "Canonical Affiliation visualization provenance, exact three-trait percentile formula, and PC1-PC6 benchmark.",
    "qwen_pc_specificity_composites.csv": "Secondary canonical-reference and simple top-three descriptive composite benchmarks.",
    "qwen_pc_specificity_human_inventory.csv": "Frozen 48-row SAPA judgments augmented with associated, PC-defining, concentrated, and Pareto coverage intersections.",
    "qwen_pc_specificity_human_summary.csv": "Twelve signed-family human-coverage and unmatched-specific-trait summaries.",
    "source_manifest.json": "Exact input hashes, AA-1/freeze commits, Qwen-only firewall, rules, seeds, and canonical PC3 provenance.",
    "verification_report.json": "Independent numerical, bootstrap, Pareto, deterministic-rerun, provenance, privacy, and firewall checks.",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
            "future_canonical_raw_url": f"https://raw.githubusercontent.com/{REPO_SLUG}/master/{relative}",
            "description": DESCRIPTIONS.get(path.name, "Reproducible Qwen PC specificity analysis script."),
        })
    target = output / "artifact_inventory.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
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
