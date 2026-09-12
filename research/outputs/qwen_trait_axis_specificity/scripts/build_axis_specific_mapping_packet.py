#!/usr/bin/env python3
"""Build the frozen neutral-ID packet for primary axis-specific families."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


PACKET_SEED = 20260921
DESCRIPTIONS = {
    ("PC1", "positive"): "Explicit, factual, analytical, methodical, quantitative, and problem-solving communication, with caution and utilitarian/data-driven reasoning.",
    ("PC1", "negative"): "Expressive, narrative, poetic, symbolic, imaginative, and performative communication, extending into affective intensity, spontaneity, and nonconformity.",
    ("PC2", "positive"): "Experiential and practical inquiry: learning from direct experience while asking questions and applying ideas concretely.",
    ("PC2", "negative"): "Inward, abstract, theoretical, reflective, and erudite thought, combined with ritual, reverence, principle, and solemnity.",
    ("PC3", "positive"): "Callous, cynical, pessimistic, vindictive, blunt, dominant, and skeptical interpersonal stance.",
    ("PC3", "negative"): "Benevolent, nurturing, supportive, deferential, optimistic, altruistic, relaxed, and inspirational interpersonal care.",
    ("PC4", "positive"): "No trait passed the frozen primary axis-specific marker rule for this signed family.",
    ("PC4", "negative"): "No trait passed the frozen primary axis-specific marker rule for this signed family.",
    ("PC5", "positive"): "No trait passed the frozen primary axis-specific marker rule for this signed family.",
    ("PC5", "negative"): "No trait passed the frozen primary axis-specific marker rule for this signed family.",
    ("PC6", "positive"): "No trait passed the frozen primary axis-specific marker rule for this signed family.",
    ("PC6", "negative"): "No trait passed the frozen primary axis-specific marker rule for this signed family.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_key(path: Path, repo: Path) -> str:
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return f"temporary_output/{path.name}"


def main(repo: Path, output: Path) -> None:
    marker_path = output / "qwen_axis_specific_marker_sets.csv"
    metrics_path = output / "qwen_trait_axis_specificity_metrics.csv"
    library_path = repo / "research/outputs/qwen_pc_human_construct_bridge/human_construct_library.csv"
    marker = pd.read_csv(marker_path)
    metrics = pd.read_csv(metrics_path)
    library = pd.read_csv(library_path)
    if len(library) != 126 or library["construct_id"].duplicated().any():
        raise ValueError("Expected unchanged 126-row construct library")

    signed_families = [(f"PC{pc}", pole) for pc in range(1, 7) for pole in ["positive", "negative"]]
    rng = np.random.default_rng(PACKET_SEED)
    permutation = rng.permutation(len(signed_families))
    family_to_id = {
        signed_families[index]: f"PURE-FAM-{order + 1:02d}" for order, index in enumerate(permutation)
    }

    rows: list[dict[str, object]] = []
    manifest_rows: list[dict[str, object]] = []
    for pc, pole in signed_families:
        selected = marker[(marker["pc"] == pc) & (marker["pole"] == pole)].sort_values(
            ["target_abs_r", "trait"], ascending=[False, True], kind="mergesort"
        )
        purest = selected.sort_values(["axis_purity", "trait"], ascending=[False, True], kind="mergesort")
        evidence = [
            {
                "trait": row.trait,
                "canonical_definition": row.canonical_definition,
                "target_r": row.target_r,
                "axis_purity": row.axis_purity,
                "dominance_gap": row.dominance_gap,
            }
            for row in selected.itertuples(index=False)
        ]
        family_id = family_to_id[(pc, pole)]
        rows.append(
            {
                "family_id": family_id,
                "axis_specific_marker_count": len(selected),
                "axis_specific_marker_names": ";".join(selected["trait"]),
                "marker_evidence_json": json.dumps(evidence, separators=(",", ":")),
                "strongest_marker": selected.iloc[0]["trait"] if len(selected) else "",
                "purest_marker": purest.iloc[0]["trait"] if len(purest) else "",
                "marker_derived_family_description": DESCRIPTIONS[(pc, pole)],
                "candidate_universe": "all 126 documented constructs in human_construct_library.csv plus item-only fallback",
            }
        )
        manifest_rows.append(
            {
                "family_id": family_id,
                "pc": pc,
                "pole": pole,
                "axis_specific_marker_count": len(selected),
            }
        )
    packet = pd.DataFrame(rows).sort_values("family_id", kind="mergesort")
    prohibited = ["pc", "pole", "role", "persona", "aa2", "aa7", "big_five", "prior_human_match"]
    for column in packet.columns:
        lower = column.lower()
        if column != "candidate_universe" and any(token in lower for token in prohibited):
            raise ValueError(f"Prohibited reviewer-facing packet field: {column}")
    packet.to_csv(output / "qwen_axis_specific_human_mapping_packet.csv", index=False)
    manifest = {
        "analysis": "Neutral-ID SAPA mapping packet for primary Qwen axis-specific trait families",
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "packet_seed": PACKET_SEED,
        "packet_row_count": len(packet),
        "marker_row_count": len(marker),
        "candidate_construct_count": len(library),
        "source_hashes": {
            manifest_key(marker_path, repo): sha256(marker_path),
            manifest_key(metrics_path, repo): sha256(metrics_path),
            manifest_key(library_path, repo): sha256(library_path),
        },
        "reviewer_packet_excludes": [
            "PC number",
            "pole label",
            "role/persona evidence",
            "prior PC interpretations",
            "AA-2 results",
            "AA-7 results",
            "previous human match labels",
        ],
        "family_key_not_reviewer_facing": sorted(manifest_rows, key=lambda row: row["family_id"]),
        "prior_human_mapping_loaded": False,
        "AA7_results_loaded": False,
    }
    (output / "qwen_axis_specific_human_mapping_packet_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    main(args.repo_root.resolve(), args.output_dir.resolve())
