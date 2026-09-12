#!/usr/bin/env python3
"""Build the AA-8 artifact inventory with hashes, provenance, and raw URLs."""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path


OUT_REL = Path("research/outputs/qwen_pc1_pc2_bipolar_human_mapping")
BRANCH = "codex/aa8-pc1-pc2-bipolar-human-mapping"
BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis"


DESCRIPTIONS = {
    "analysis_specification.md": "Frozen AA-8 analysis scope, evidence hierarchy, interpretive rubrics, and firewalls.",
    "pc1_bipolar_model_evidence_packet.csv": "Frozen PC1 trait, role, cluster, and prior-result evidence packet.",
    "pc2_bipolar_model_evidence_packet.csv": "Frozen PC2 trait, role, cluster, and prior-result evidence packet.",
    "model_evidence_packet_manifest.json": "Source hashes and freeze provenance for the PC1/PC2 evidence packets.",
    "pc1_sapa_construct_reconsideration.csv": "Complete 126-construct PC1 SAPA reconsideration with serious-candidate classifications.",
    "pc1_rule_procedure_item_audit.csv": "Item-level SAPA audit for rules, standards, duties, accuracy, and procedure content.",
    "pc1_bipolar_human_mapping.csv": "Detailed bipolar PC1 human-candidate rubric judgments.",
    "pc2_coordinate_blind_role_rating_rubric.md": "Frozen coordinate-blind five-dimension role-rating rubric.",
    "pc2_coordinate_blind_role_ratings.csv": "Frozen coordinate-blind semantic ratings for all 275 Qwen roles.",
    "pc2_role_rating_freeze_manifest.json": "Hash and commit provenance for the role-rating freeze.",
    "pc2_role_dimension_pc_associations.csv": "Post-freeze PC associations and physicality incremental diagnostic.",
    "pc2_role_dimension_diagnostic_report.md": "PC2 role-rating, embodiment, role-extreme, and counterexample audit.",
    "pc2_sapa_construct_reconsideration.csv": "Complete 126-construct PC2 SAPA reconsideration with opposite-pole completion.",
    "pc2_physicality_activity_item_audit.csv": "Item-level audit of physicality, activity, embodiment, and semantic neighbors.",
    "pc2_bipolar_human_mapping.csv": "Detailed bipolar PC2 human-candidate rubric judgments.",
    "pc1_pc2_bipolar_interpretation_comparison.csv": "Observed/interpretive synthesis and competing explanations for PC1 and PC2.",
    "pc1_pc2_bipolar_human_mapping_report.md": "Primary AA-8 scientific report and revised human-measurement inventory.",
    "source_manifest.json": "Exact source commits, paths, hashes, and scope restrictions.",
    "verification_report.json": "Independent AA-8 source, freeze, leakage, parse, and reproduction checks.",
    "artifact_inventory.csv": "Complete AA-8 artifact hashes, introducing commits, and raw URLs.",
    "scripts/build_pc2_coordinate_blind_role_ratings.py": "Deterministic coordinate-blind role-rating builder.",
    "scripts/build_model_evidence_and_role_diagnostics.py": "Evidence-packet and post-freeze role-diagnostic builder.",
    "scripts/build_human_reconsideration.py": "Deterministic human-library reconsideration and item-audit builder.",
    "scripts/build_source_manifest.py": "Source-manifest builder.",
    "scripts/verify_aa8.py": "Independent AA-8 verification suite.",
    "scripts/build_artifact_inventory.py": "Artifact-inventory builder.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def introducing_commit(repo: Path, rel: Path) -> str:
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", rel.as_posix()],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip() or "PENDING_FINAL_COMMIT"


def main() -> None:
    repo = Path(__file__).resolve().parents[4]
    out = repo / OUT_REL
    target = out / "artifact_inventory.csv"
    paths = sorted(p for p in out.rglob("*") if p.is_file() and p != target)
    rows = []
    for path in paths:
        rel = path.relative_to(repo)
        local = path.relative_to(out).as_posix()
        rows.append(
            {
                "path": rel.as_posix(),
                "status": "active",
                "description": DESCRIPTIONS.get(local, f"AA-8 artifact: {local}"),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "introducing_commit": introducing_commit(repo, rel),
                "branch_raw_github_url": f"{BASE}/{BRANCH}/{rel.as_posix()}",
                "future_canonical_master_raw_github_url": f"{BASE}/master/{rel.as_posix()}",
            }
        )
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
