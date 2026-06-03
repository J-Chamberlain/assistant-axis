#!/usr/bin/env python3
"""Select positive-PC2 edge role candidates for a two-persona activation-cloud pilot."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
GEOMETRY_PATH = ROOT / "research/visualizations/geometry_viz_data.json"
INSTRUCTION_DIR = ROOT / "data/roles/instructions"
OUT_DIR = ROOT / "research/outputs/positive_pc2_pilot_candidate_selection"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_ROLES = ["amateur", "influencer", "newlywed", "graduate", "patient"]
ALTERNATE_ROLES = ["celebrity", "divorcee", "parent", "retiree", "student"]
EXCLUDED_NOTES = {
    "competitor": "Operationally safe but adversarial/win-oriented; higher PC3 pressure could confound a first PC2-focused pilot.",
    "gamer": "Safe, but game-mechanics framing and high PC3 may make it less clean as the first positive-PC2 comparator.",
    "mechanic": "Safe, but procedural/troubleshooting instructions make it less representative of the target positive-PC2 hypothesis.",
    "optimist": "Safe, but affect-valence/positivity may confound PC2 with emotion-valence behavior.",
    "podcaster": "Safe, but too close to playwright on dialogue/media production to provide a clean contrast.",
}

RATIONALES = {
    "amateur": "Highest usable PC2 edge candidate; captures passion, incomplete expertise, and local curiosity without high-PC1 procedural constraint.",
    "influencer": "Strong social exposure and performance-pressure role; useful for testing socially situated positive-PC2 activation.",
    "newlywed": "Formative relational-transition role; directly targets identity blending, dependence, and situated adjustment.",
    "graduate": "Clean transition-from-structure role with explicit independence/responsibility tension and moderate PC1 headroom.",
    "patient": "Vulnerability and institutional dependence are direct positive-PC2 themes; useful but has a medical-content caveat.",
    "celebrity": "Public-scrutiny and image-management role; strong social exposure but less formative than influencer/newlywed/graduate.",
    "divorcee": "Identity-reconstruction and transition role; strong PC2 rationale but emotionally sensitive.",
    "parent": "Situated responsibility and family-pressure role; safe and interpretable, but more stabilizing than edge-positive.",
    "retiree": "Life-stage transition and reinvention role; safe, but less socially exposed than the primary candidates.",
    "student": "Formative learning role; safe and interpretable, but PC1 is relatively higher and academic framing may be more constrained.",
}

SAFETY_NOTES = {
    "amateur": "Safe; no operational-harm concern in positive instructions.",
    "influencer": "Safe for generic extraction prompts; note possible persuasion/brand-framing but no operational-harm instruction.",
    "newlywed": "Safe; relationship/life-adjustment content only.",
    "graduate": "Safe; transition and independence content only.",
    "patient": "Generally safe for generic extraction prompts; avoid prompting for medical advice in later pilot analysis.",
    "celebrity": "Safe; public-image and fame-pressure content only.",
    "divorcee": "Safe but emotionally sensitive; avoid treating relationship status as pathology.",
    "parent": "Safe; family responsibility content only.",
    "retiree": "Safe; life-stage transition content only.",
    "student": "Safe; learning/education content only.",
}

CONTRAST_NOTES = {
    "amateur": "Good contrast: passion and incomplete expertise versus playwright's trained craft and dramatic structure.",
    "influencer": "Good contrast: social exposure and audience pressure versus playwright's scripted/mediated performance design.",
    "newlywed": "Good contrast: lived relational transition versus playwright's authored relational simulation.",
    "graduate": "Good contrast: formative transition after institutional structure versus playwright's mature expressive production.",
    "patient": "Good contrast: vulnerable institutional role versus playwright's agentive expressive role.",
    "celebrity": "Moderate contrast: public performance pressure overlaps with playwright's performance domain.",
    "divorcee": "Good contrast: identity reconstruction versus playwright's constructed characters and staged identity.",
    "parent": "Moderate contrast: situated caregiving/stabilization versus playwright's expressive production.",
    "retiree": "Moderate contrast: life-stage reinvention versus playwright's creative construction.",
    "student": "Moderate contrast: learner/formative stance versus playwright's authorial expertise, but academic constraint may reduce variance.",
}


def percentile_rank(values: np.ndarray, value: float) -> float:
    return float(100.0 * (np.sum(values < value) + 0.5 * np.sum(values == value)) / len(values))


def load_instruction(role: str) -> tuple[Path, list[str], str]:
    path = INSTRUCTION_DIR / f"{role}.json"
    if not path.exists():
        return path, [], "missing"
    data = json.loads(path.read_text())
    instructions = [item.get("pos", "").strip() for item in data.get("instruction", [])]
    if len(instructions) != 5 or any(not x for x in instructions):
        return path, instructions, "malformed"
    return path, instructions, "ok"


def load_geometry() -> list[dict[str, object]]:
    data = json.loads(GEOMETRY_PATH.read_text())
    roles = data["roles"]
    names = roles["names"]
    pca = np.asarray(roles["pca3d"], dtype=float)
    clusters = roles["clusters"]
    pc1_vals, pc2_vals, pc3_vals = pca[:, 0], pca[:, 1], pca[:, 2]
    rows = []
    for idx, role in enumerate(names):
        pc1, pc2, pc3 = pca[idx]
        path, instructions, instruction_status = load_instruction(role)
        rows.append(
            {
                "role": role,
                "cluster": clusters[idx],
                "pc1": float(pc1),
                "pc2": float(pc2),
                "pc3": float(pc3),
                "pc1_percentile": percentile_rank(pc1_vals, float(pc1)),
                "pc2_percentile": percentile_rank(pc2_vals, float(pc2)),
                "pc3_percentile": percentile_rank(pc3_vals, float(pc3)),
                "instruction_path": str(path.relative_to(ROOT)),
                "instruction_status": instruction_status,
                "instructions": instructions,
            }
        )
    return rows


def row_for(role: str, rows: list[dict[str, object]]) -> dict[str, object]:
    by_role = {str(row["role"]): row for row in rows}
    if role not in by_role:
        raise KeyError(role)
    return by_role[role]


def format_candidate(
    role: str,
    rows: list[dict[str, object]],
    target_region_rank: int,
    list_type: str,
) -> dict[str, object]:
    row = row_for(role, rows)
    pc1_pct = float(row["pc1_percentile"])
    pc2_pct = float(row["pc2_percentile"])
    return {
        "list_type": list_type,
        "target_region_rank": target_region_rank,
        "role": role,
        "cluster": row["cluster"],
        "pc1": round(float(row["pc1"]), 6),
        "pc2": round(float(row["pc2"]), 6),
        "pc3": round(float(row["pc3"]), 6),
        "pc1_percentile": round(pc1_pct, 3),
        "pc2_percentile": round(pc2_pct, 3),
        "pc3_percentile": round(float(row["pc3_percentile"]), 3),
        "distance_from_pc1_upper_filter": round(75.0 - pc1_pct, 3),
        "distance_from_pc1_center_57_5": round(abs(pc1_pct - 57.5), 3),
        "instruction_path": row["instruction_path"],
        "instruction_status": row["instruction_status"],
        "behavioral_rationale": RATIONALES[role],
        "safety_suitability_note": SAFETY_NOTES[role],
        "playwright_contrast_note": CONTRAST_NOTES[role],
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, object]]) -> list[str]:
    lines = [
        "| Rank | Role | Cluster | PC1 | PC2 | PC3 | PC1 pct | PC2 pct | PC3 pct | Instructions |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['target_region_rank']} | {row['role']} | {row['cluster']} | "
            f"{row['pc1']:.6f} | {row['pc2']:.6f} | {row['pc3']:.6f} | "
            f"{row['pc1_percentile']:.3f} | {row['pc2_percentile']:.3f} | {row['pc3_percentile']:.3f} | "
            f"`{row['instruction_path']}` |"
        )
    return lines


def main() -> None:
    rows = load_geometry()
    preferred = [
        row
        for row in rows
        if float(row["pc2_percentile"]) >= 85.0
        and 40.0 <= float(row["pc1_percentile"]) <= 75.0
        and row["instruction_status"] == "ok"
    ]
    preferred_sorted = sorted(
        preferred,
        key=lambda row: (-float(row["pc2_percentile"]), abs(float(row["pc1_percentile"]) - 57.5), str(row["role"])),
    )
    preferred_rank = {str(row["role"]): idx for idx, row in enumerate(preferred_sorted, 1)}

    primary = [format_candidate(role, rows, preferred_rank[role], "primary") for role in PRIMARY_ROLES]
    alternates = [format_candidate(role, rows, preferred_rank[role], "alternate") for role in ALTERNATE_ROLES]
    write_csv(OUT_DIR / "positive_pc2_primary_candidates.csv", primary)
    write_csv(OUT_DIR / "positive_pc2_alternate_candidates.csv", alternates)

    playwright = row_for("playwright", rows)
    playwright_payload = {
        "role": "playwright",
        "cluster": playwright["cluster"],
        "pc1": float(playwright["pc1"]),
        "pc2": float(playwright["pc2"]),
        "pc3": float(playwright["pc3"]),
        "pc1_percentile": float(playwright["pc1_percentile"]),
        "pc2_percentile": float(playwright["pc2_percentile"]),
        "pc3_percentile": float(playwright["pc3_percentile"]),
        "instruction_path": playwright["instruction_path"],
        "instruction_status": playwright["instruction_status"],
        "positive_pc2_candidate_note": "Already selected comparison role; expressive high-degrees-of-freedom anchor, not the positive-PC2 edge candidate.",
    }
    (OUT_DIR / "playwright_comparison_coordinates.json").write_text(json.dumps(playwright_payload, indent=2) + "\n")

    excerpt_lines = [
        "# Positive-PC2 Candidate Instruction Excerpts",
        "",
        "All listed roles have exactly five positive instructions and passed the local instruction-file integrity check.",
    ]
    for group, group_rows in [("Primary Candidates", primary), ("Alternates", alternates), ("Comparison Role", [playwright_payload])]:
        excerpt_lines.extend(["", f"## {group}", ""])
        for candidate in group_rows:
            role = str(candidate["role"])
            source = row_for(role, rows)
            excerpt_lines.extend([f"### {role}", "", f"Path: `{source['instruction_path']}`", ""])
            for idx, instruction in enumerate(source["instructions"], 1):
                excerpt_lines.append(f"{idx}. {instruction}")
            excerpt_lines.append("")
    (OUT_DIR / "positive_pc2_candidate_instruction_excerpt.md").write_text("\n".join(excerpt_lines).rstrip() + "\n")

    excluded_preferred = []
    for row in preferred_sorted:
        role = str(row["role"])
        if role in PRIMARY_ROLES or role in ALTERNATE_ROLES:
            continue
        excluded_preferred.append(
            {
                "role": role,
                "pc1_percentile": round(float(row["pc1_percentile"]), 3),
                "pc2_percentile": round(float(row["pc2_percentile"]), 3),
                "reason": EXCLUDED_NOTES.get(role, "Not selected because the five primary and five alternate slots were stronger for the requested pilot."),
            }
        )

    report_lines = [
        "# Positive-PC2 Pilot Candidate Selection",
        "",
        "## Startup And Scope",
        "",
        "- Startup verification: passed against fetched raw startup files and `research/STARTUP_MANIFEST.md`.",
        "- No pod was started.",
        "- No model generation or activation extraction was run.",
        f"- Geometry source: `{GEOMETRY_PATH.relative_to(ROOT)}`",
        "- Instruction source: `data/roles/instructions/{role}.json`",
        "",
        "## Selection Thresholds",
        "",
        "- Preferred filter used: PC2 percentile >= 85 and PC1 percentile between 40 and 75.",
        "- Fallback thresholds needed: no.",
        f"- Preferred-filter candidates with valid instructions: {len(preferred_sorted)}.",
        "- Ranking prioritized high PC2, non-extreme PC1, safe positive instructions, interpretability for situated/formative positive-PC2 geometry, and contrast with playwright.",
        "",
        "## Playwright Comparison Row",
        "",
        "| Role | Cluster | PC1 | PC2 | PC3 | PC1 pct | PC2 pct | PC3 pct | Instructions |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
        f"| playwright | {playwright_payload['cluster']} | {playwright_payload['pc1']:.6f} | {playwright_payload['pc2']:.6f} | {playwright_payload['pc3']:.6f} | {playwright_payload['pc1_percentile']:.3f} | {playwright_payload['pc2_percentile']:.3f} | {playwright_payload['pc3_percentile']:.3f} | `{playwright_payload['instruction_path']}` |",
        "",
        "## Recommended Shortlist: Five Primary Candidates",
        "",
        *markdown_table(primary),
        "",
        "These are recommended as a shortlist only; the final second persona should be selected by the user before the GPU pilot.",
        "",
        "## Alternates",
        "",
        *markdown_table(alternates),
        "",
        "## Safety And Suitability Notes",
        "",
    ]
    for candidate in primary + alternates:
        report_lines.extend(
            [
                f"### {candidate['role']}",
                "",
                f"- Behavioral rationale: {candidate['behavioral_rationale']}",
                f"- Safety/suitability: {candidate['safety_suitability_note']}",
                f"- Contrast with playwright: {candidate['playwright_contrast_note']}",
                "",
            ]
        )
    report_lines.extend(
        [
            "## Preferred-Filter Roles Not Selected",
            "",
            "| Role | PC1 pct | PC2 pct | Reason |",
            "|---|---:|---:|---|",
        ]
    )
    for item in excluded_preferred:
        report_lines.append(f"| {item['role']} | {item['pc1_percentile']:.3f} | {item['pc2_percentile']:.3f} | {item['reason']} |")
    report_lines.extend(
        [
            "",
            "## Concerns About Role Instructions",
            "",
            "- No primary or alternate candidate had missing or malformed instruction artifacts.",
            "- `patient` is safe for generic extraction prompts but should not be used to solicit medical advice.",
            "- `influencer` and `celebrity` involve public persuasion/image management; monitor later generated text for social-manipulation framing, but the positive instructions themselves are not operationally harmful.",
            "- `divorcee` is emotionally sensitive; it is useful as a transition/identity candidate but should be framed carefully.",
            "",
            "## Next Step",
            "",
            "User selects one of the five primary candidates, or one alternate, as the positive-PC2 edge role for the first two-persona activation-cloud GPU pilot after extraction-boundary verification.",
            "",
        ]
    )
    (OUT_DIR / "positive_pc2_candidate_selection_report.md").write_text("\n".join(report_lines))

    print(
        json.dumps(
            {
                "preferred_filter_count": len(preferred_sorted),
                "fallback_needed": False,
                "primary": [row["role"] for row in primary],
                "alternates": [row["role"] for row in alternates],
                "playwright": playwright_payload,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
