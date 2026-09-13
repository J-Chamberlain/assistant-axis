#!/usr/bin/env python3
"""Build the complete artifact inventory for the model coverage terrain viewer."""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[2]
BRANCH = "codex/aa12-model-coverage-terrain-viewer"
REPO = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis"


DESCRIPTIONS = {
    "model_coverage_terrain_viewer.html": "Self-contained interactive model-only persona occupancy terrain viewer",
    "model_coverage_terrain_report.md": "Reader-first methods, results, boundaries, and viewer guide",
    "coverage_terrain_method.md": "Pre-terrain frozen coverage and visualization methodology",
    "source_manifest.json": "Exact frozen model-side inputs, hashes, parameters, and compute boundaries",
    "role_coordinates.csv": "Native and frozen display-aligned PC1-PC3 coordinates for 275 roles per model",
    "role_density_scores.csv": "Role-only Scott-KDE density values and within-model density ranks",
    "role_sparsity_scores.csv": "Inverse-density and standardized-PC kNN sample-sparsity diagnostics",
    "role_family_membership.csv": "Exact frozen A-E model-specific role membership and core/majority/fringe status",
    "coverage_region_summary.csv": "KDE levels and achieved 50/80/95% sampled-role coverage fractions",
    "density_bandwidth_sensitivity.csv": "Frozen 0.75x/1x/1.25x Scott sensitivity diagnostics",
    "nearest_role_neighbors.csv": "Ten nearest sampled roles in standardized native PC1-PC3 per model",
    "cross_model_neighborhood_recurrence.csv": "Shared-role local-neighborhood Jaccard recurrence across models",
    "display_alignment_coordinates.csv": "Secondary frozen Procrustes display coordinates; not native shared axes",
    "trait_landmarks.csv": "Optional Qwen trait-direction landmarks excluded from occupancy density",
    "family_terrain_summary.csv": "Family role counts, density ranks, centroids, and envelope eligibility",
    "terrain_viewer_data.json": "Embedded deterministic grids, roles, hulls, and controls payload",
    "figure_inventory.csv": "Complete static figure catalog with source-table lineage",
    "browser_verification.json": "Chrome 152 WebGL and interaction verification results",
    "verification_report.json": "Numerical, source, scope, rendering, and reproducibility verification",
}


def description(relative: Path) -> str:
    if relative.name in DESCRIPTIONS:
        return DESCRIPTIONS[relative.name]
    if relative.parts[0] == "analysis":
        return "Deterministic analysis, rendering, or verification code"
    if relative.parts[0] == "figures":
        return "Static model coverage terrain companion figure"
    return "Model coverage terrain viewer artifact"


def introducing_commit(path: Path) -> str:
    relative = str(path.relative_to(ROOT))
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "--", relative],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip().splitlines()
    return result[-1] if result else "PENDING_THIS_CHECKPOINT"


def main() -> None:
    inventory = OUT / "artifact_inventory.csv"
    paths = sorted(
        path for path in OUT.rglob("*")
        if path.is_file() and path != inventory and "__pycache__" not in path.parts and path.name != "browser_console.log"
    )
    rows = []
    for path in paths:
        repo_relative = path.relative_to(ROOT)
        output_relative = path.relative_to(OUT)
        payload = path.read_bytes()
        rows.append(
            {
                "path": str(repo_relative),
                "status": "active",
                "category": "model coverage terrain viewer",
                "description": description(output_relative),
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "introducing_commit": introducing_commit(path),
                "canonical_raw_url": f"{REPO}/master/{repo_relative}",
                "branch_raw_url": f"{REPO}/{BRANCH}/{repo_relative}",
            }
        )
    own_relative = inventory.relative_to(ROOT)
    rows.append(
        {
            "path": str(own_relative),
            "status": "active",
            "category": "model coverage terrain viewer",
            "description": "Complete recursive artifact inventory with hashes, status, provenance, and raw URLs",
            "bytes": 0,
            "sha256": "SELF_REFERENTIAL_NOT_RECORDED",
            "introducing_commit": introducing_commit(inventory),
            "canonical_raw_url": f"{REPO}/master/{own_relative}",
            "branch_raw_url": f"{REPO}/{BRANCH}/{own_relative}",
        }
    )
    rows.sort(key=lambda row: row["path"])
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {inventory}")


if __name__ == "__main__":
    main()
