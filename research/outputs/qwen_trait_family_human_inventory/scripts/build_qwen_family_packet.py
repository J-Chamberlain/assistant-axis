#!/usr/bin/env python3
"""Describe numerically selected families and freeze a PC-blind packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

import pandas as pd


BLIND_SEED = 20260919
THRESHOLDS = (0.40, 0.50, 0.60)
DESCRIPTIONS = {
    ("PC1", "positive"): "An explicit, factual, analytical, methodical, and regulated response style, extending to caution, composure, problem solving, and formal structure.",
    ("PC1", "negative"): "An expressive, narrative, poetic, dramatic, symbolic, and imaginative response style, with affective intensity and a heterogeneous tail of spontaneity, nonconformity, and interpersonal performance.",
    ("PC2", "positive"): "An experiential, practical, informal, accessible, and socially engaged style that also includes adaptability, emotional reactivity, impulsivity, and low formality.",
    ("PC2", "negative"): "An inward, ritualized, contemplative, theoretical, abstract, principled, and formal style, with seriousness, meticulousness, and intellectual or spiritual reserve.",
    ("PC3", "positive"): "A hard-edged antagonistic family combining callousness, cynicism, pessimism, vindictiveness, blunt dominance, distrust, confrontation, and critical judgment.",
    ("PC3", "negative"): "A prosocial care-and-accommodation family combining benevolence, nurturance, support, forgiveness, optimism, altruism, tact, collaboration, and nonconfrontation.",
    ("PC4", "positive"): "A narrow two-trait family expressing avoidance together with understated, low-intensity presentation.",
    ("PC4", "negative"): "A heterogeneous small family combining holistic and systems-oriented thought with independence, critical evaluation, generosity, and progressive orientation.",
    ("PC5", "positive"): "A singleton family defined only by divergent idea generation and openness to multiple possible directions.",
    ("PC5", "negative"): "No Qwen trait met the frozen primary family rule for this pole.",
    ("PC6", "positive"): "No Qwen trait met the frozen primary family rule for this pole.",
    ("PC6", "negative"): "A singleton family defined only by systems-oriented, relational, and whole-system reasoning.",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def family_id_map() -> dict[tuple[str, str], str]:
    families = [(f"PC{pc}", pole) for pc in range(1, 7) for pole in ("positive", "negative")]
    rng = random.Random(BLIND_SEED)
    shuffled = families.copy()
    rng.shuffle(shuffled)
    return {family: f"FAM-{index:02d}" for index, family in enumerate(shuffled, 1)}


def build(output: Path) -> None:
    primary_path = output / "qwen_trait_family_membership_primary.csv"
    sensitivity_path = output / "qwen_trait_family_threshold_sensitivity.csv"
    spec_path = output / "qwen_trait_family_selection_spec.md"
    primary = pd.read_csv(primary_path)
    sensitivity = pd.read_csv(sensitivity_path)
    id_map = family_id_map()

    summary_rows: list[dict[str, object]] = []
    blind_rows: list[dict[str, object]] = []
    for pc in [f"PC{i}" for i in range(1, 7)]:
        for pole in ("positive", "negative"):
            group = primary[(primary["pc"] == pc) & (primary["pole"] == pole)].copy()
            group = group.sort_values("rank_within_positive_or_negative_pole", kind="mergesort")
            members = group["trait"].tolist()
            evidence = [
                {
                    "trait": row.trait,
                    "canonical_definition": row.canonical_definition,
                    "pearson_r": float(row.pearson_r),
                    "spearman_rho": float(row.spearman_rho),
                    "rank_within_pole": int(row.rank_within_positive_or_negative_pole),
                }
                for row in group.itertuples(index=False)
            ]
            sensitivity_counts = {}
            for threshold in THRESHOLDS:
                subset = sensitivity[
                    (sensitivity["pc"] == pc)
                    & (sensitivity["pole"] == pole)
                    & (sensitivity["abs_r_threshold"].round(8) == threshold)
                    & sensitivity["is_member"]
                ]
                sensitivity_counts[threshold] = int(len(subset))
            row = {
                "pc": pc,
                "pole": pole,
                "primary_member_count": len(group),
                "ordered_member_list": ";".join(members),
                "ordered_member_correlations_json": json.dumps(
                    [{"trait": item["trait"], "pearson_r": item["pearson_r"], "spearman_rho": item["spearman_rho"]} for item in evidence],
                    separators=(",", ":"),
                    ensure_ascii=False,
                ),
                "strongest_correlated_trait": members[0] if members else "",
                "second_strongest_trait": members[1] if len(members) > 1 else "",
                "third_strongest_trait": members[2] if len(members) > 2 else "",
                "pearson_r_min": float(group["pearson_r"].min()) if len(group) else "",
                "pearson_r_max": float(group["pearson_r"].max()) if len(group) else "",
                "sensitivity_member_count_abs_r_0_40": sensitivity_counts[0.40],
                "primary_member_count_abs_r_0_50": sensitivity_counts[0.50],
                "sensitivity_member_count_abs_r_0_60": sensitivity_counts[0.60],
                "family_description": DESCRIPTIONS[(pc, pole)],
                "description_status": "INTERPRETATION_FROM_NUMERICALLY_SELECTED_MEMBERS",
            }
            summary_rows.append(row)
            blind_rows.append({
                "family_id": id_map[(pc, pole)],
                "primary_member_count": len(group),
                "family_members_ordered": ";".join(members),
                "family_member_evidence_json": json.dumps(evidence, separators=(",", ":"), ensure_ascii=False),
                "strongest_correlated_trait": members[0] if members else "",
                "second_strongest_trait": members[1] if len(members) > 1 else "",
                "third_strongest_trait": members[2] if len(members) > 2 else "",
                "family_description": DESCRIPTIONS[(pc, pole)],
            })

    summaries = pd.DataFrame(summary_rows)
    blind = pd.DataFrame(blind_rows).sort_values("family_id", kind="mergesort")
    summaries.to_csv(output / "qwen_trait_family_summaries.csv", index=False, lineterminator="\n")
    blind.to_csv(output / "qwen_trait_family_blinded_mapping_packet.csv", index=False, lineterminator="\n")

    report = [
        "# Correlation-defined Qwen trait-family report",
        "",
        "The twelve PC-pole families below were selected mechanically before semantic description. The primary rule is |Pearson r| >= 0.50, BH-FDR q < 0.01 within each PC, and bootstrap sign stability >= 95% across 2,000 fixed-seed role resamples. Empty families remain empty.",
        "",
    ]
    for row in summaries.itertuples(index=False):
        report.extend([
            f"## {row.pc} {row.pole}",
            "",
            f"Observed: {row.primary_member_count} primary members; sensitivity counts are {row.sensitivity_member_count_abs_r_0_40} at |r| >= .40, {row.primary_member_count_abs_r_0_50} at |r| >= .50, and {row.sensitivity_member_count_abs_r_0_60} at |r| >= .60.",
            "",
        ])
        if row.primary_member_count:
            evidence = json.loads(row.ordered_member_correlations_json)
            report.append("Complete ordered member list: " + "; ".join(f"{item['trait']} (r={item['pearson_r']:+.3f}, rho={item['spearman_rho']:+.3f})" for item in evidence) + ".")
            report.append("")
            anchor_bits = [row.strongest_correlated_trait]
            if row.second_strongest_trait:
                anchor_bits.append(row.second_strongest_trait)
            if row.third_strongest_trait:
                anchor_bits.append(row.third_strongest_trait)
            report.append("Strongest anchors: " + ", ".join(anchor_bits) + f". Pearson range {row.pearson_r_min:+.3f} to {row.pearson_r_max:+.3f}.")
            report.append("")
        report.extend([
            "Interpretation: " + row.family_description,
            "",
        ])
    report.extend([
        "## Epistemic boundary",
        "",
        "Observed quantities are Qwen-only trait-PC correlations and threshold membership. The one-sentence family descriptions are interpretations of the selected Qwen traits. Any proposed relationship to a human construct is a hypothesis until tested; actual respondent-level human/model correspondence remains unknown.",
        "",
        "No human respondent was scored, no cross-model result was used, and no model inference or activation extraction was performed.",
    ])
    (output / "qwen_trait_family_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    blind_manifest = {
        "analysis": "PC-blind Qwen trait-family to SAPA mapping packet",
        "family_count": 12,
        "family_id_seed": BLIND_SEED,
        "family_id_assignment": "Python random.Random(seed).shuffle over PC1-positive, PC1-negative, ..., PC6-positive, PC6-negative; assignment key intentionally absent from reviewer-facing packet and manifest",
        "packet_sha256": sha256(output / "qwen_trait_family_blinded_mapping_packet.csv"),
        "source_hashes": {
            "qwen_trait_family_membership_primary.csv": sha256(primary_path),
            "qwen_trait_family_threshold_sensitivity.csv": sha256(sensitivity_path),
            "qwen_trait_family_selection_spec.md": sha256(spec_path),
        },
        "reviewer_visible_fields": list(blind.columns),
        "excluded_fields": [
            "PC number",
            "explicit pole label",
            "role or persona names and extremes",
            "prior PC interpretations",
            "AA-2 Big Five results",
            "AA-7 results",
            "prior AA-1 human-construct hypotheses and candidate labels",
            "Llama or Gemma results",
        ],
        "empty_families_preserved": int((summaries["primary_member_count"] == 0).sum()),
        "judgments_present": False,
        "epistemic_boundary": "Descriptions are interpretations of mechanically selected Qwen families; the packet contains no evidence of human/model equivalence.",
    }
    (output / "qwen_trait_family_blind_manifest.json").write_text(
        json.dumps(blind_manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "family_count": len(summaries),
        "blind_ids": blind["family_id"].tolist(),
        "empty_families": int((summaries["primary_member_count"] == 0).sum()),
    }, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    build(args.output_dir.resolve())


if __name__ == "__main__":
    main()
