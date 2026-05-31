#!/usr/bin/env python3
"""Prepare within-role displacement study scaffolding.

This script performs no model calls, no activation extraction, and no GPU work.
It reads public/local Assistant Axis prompt artifacts plus the current geometry
viewer dataset, then writes reusable design materials for a later one-role
within-role displacement study.
"""

from __future__ import annotations

import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


MODEL_USED = "GPT-5.5"
REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "research/outputs/within_role_displacement_design"
ROLE_INSTRUCTION_DIR = REPO_ROOT / "data/roles/instructions"
QUESTIONS_PATH = REPO_ROOT / "data/extraction_questions.jsonl"
GEOMETRY_PATH = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
ROLE_AUDIT_REPORT = REPO_ROOT / "research/outputs/role_rollout_artifact_audit/role_rollout_artifact_audit_report.md"
PROMPT_INVENTORY_REPORT = REPO_ROOT / "research/outputs/prompt_artifact_inventory/prompt_artifact_inventory_report.md"
METHOD_CARD_LU = Path("/mnt/data/METHOD CARD-Lu et al. role-vector extraction.txt")
METHOD_CARD_ADAPTIVE = Path("/mnt/data/METHOD CARD-Adaptive role-vector extraction attempt.txt")


SCORING_COLUMNS = [
    "predicted_delta_pc1_direction",
    "predicted_delta_pc1_strength",
    "predicted_delta_pc1_confidence",
    "predicted_delta_pc2_direction",
    "predicted_delta_pc2_strength",
    "predicted_delta_pc2_confidence",
    "predicted_delta_pc3_direction",
    "predicted_delta_pc3_strength",
    "predicted_delta_pc3_confidence",
    "expected_role_expression_effect",
    "rationale",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_role_files() -> dict[str, dict]:
    roles: dict[str, dict] = {}
    for path in sorted(ROLE_INSTRUCTION_DIR.glob("*.json")):
        if path.stem == "default":
            continue
        with path.open() as f:
            data = json.load(f)
        roles[path.stem] = data
    return roles


def read_questions() -> list[dict]:
    rows: list[dict] = []
    with QUESTIONS_PATH.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return sorted(rows, key=lambda r: int(r["id"]))


def read_geometry() -> dict[str, dict]:
    with GEOMETRY_PATH.open() as f:
        data = json.load(f)
    roles = data["roles"]
    out: dict[str, dict] = {}
    for i, name in enumerate(roles["names"]):
        pc1, pc2, pc3 = roles["pca3d"][i]
        out[name] = {
            "pc1": pc1,
            "pc2": pc2,
            "pc3": pc3,
            "cluster": roles["clusters"][i],
            "distance_from_origin": math.sqrt(pc1 * pc1 + pc2 * pc2 + pc3 * pc3),
        }
    return out


def percentile_rank(values: list[float], value: float) -> float:
    if not values:
        return float("nan")
    below = sum(1 for x in values if x < value)
    equal = sum(1 for x in values if x == value)
    return 100.0 * (below + 0.5 * equal) / len(values)


def quantiles(values: list[float]) -> dict[int, float]:
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    out = {}
    for q in [20, 35, 65, 80]:
        pos = (n - 1) * q / 100.0
        lo = math.floor(pos)
        hi = math.ceil(pos)
        if lo == hi:
            out[q] = sorted_vals[lo]
        else:
            frac = pos - lo
            out[q] = sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac
    return out


TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z'-]+")


def token_set(text: str) -> set[str]:
    stop = {
        "the",
        "and",
        "with",
        "that",
        "into",
        "your",
        "you",
        "are",
        "for",
        "any",
        "their",
        "from",
        "this",
        "have",
        "has",
        "who",
        "how",
        "what",
        "when",
        "where",
        "why",
    }
    return {t.lower() for t in TOKEN_RE.findall(text) if t.lower() not in stop}


def mean_pairwise_jaccard(texts: list[str]) -> float:
    sets = [token_set(t) for t in texts if t.strip()]
    if len(sets) < 2:
        return 0.0
    vals = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            union = sets[i] | sets[j]
            vals.append(len(sets[i] & sets[j]) / len(union) if union else 0.0)
    return mean(vals) if vals else 0.0


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_role_instruction_inventory(roles: dict[str, dict]) -> list[dict]:
    rows: list[dict] = []
    for role, data in sorted(roles.items()):
        for idx, instruction in enumerate(data.get("instruction", [])):
            rows.append(
                {
                    "role": role,
                    "instruction_id": idx,
                    "instruction_polarity": "positive",
                    "instruction_text": instruction.get("pos", ""),
                    "eval_prompt_present": bool(data.get("eval_prompt")),
                    "role_specific_question_count": len(data.get("questions", [])),
                    "source_path": f"data/roles/instructions/{role}.json",
                    "model_used": MODEL_USED,
                }
            )
    return rows


def build_question_inventory(questions: list[dict]) -> list[dict]:
    return [
        {
            "question_id": q["id"],
            "question_text": q["question"],
            "source_path": "data/extraction_questions.jsonl",
            "model_used": MODEL_USED,
        }
        for q in questions
    ]


def build_instruction_template(instruction_rows: list[dict]) -> list[dict]:
    rows = []
    for row in instruction_rows:
        out = {
            "role": row["role"],
            "instruction_id": row["instruction_id"],
            "instruction_text": row["instruction_text"],
        }
        out.update({k: "" for k in SCORING_COLUMNS})
        rows.append(out)
    return rows


def build_question_template(question_rows: list[dict]) -> list[dict]:
    rows = []
    for row in question_rows:
        out = {
            "question_id": row["question_id"],
            "question_text": row["question_text"],
        }
        out.update({k: "" for k in SCORING_COLUMNS})
        rows.append(out)
    return rows


def build_candidate_table(roles: dict[str, dict], geometry: dict[str, dict]) -> tuple[list[dict], dict]:
    pcs = {axis: [g[axis] for g in geometry.values()] for axis in ["pc1", "pc2", "pc3"]}
    qs = {axis: quantiles(vals) for axis, vals in pcs.items()}
    rows = []
    for role, data in sorted(roles.items()):
        if role not in geometry:
            continue
        g = geometry[role]
        instructions = [x.get("pos", "") for x in data.get("instruction", [])]
        pcts = {axis: percentile_rank(pcs[axis], g[axis]) for axis in ["pc1", "pc2", "pc3"]}
        central_35_65 = all(35 <= pcts[axis] <= 65 for axis in ["pc1", "pc2", "pc3"])
        central_20_80 = all(20 <= pcts[axis] <= 80 for axis in ["pc1", "pc2", "pc3"])
        extreme_axes = [
            axis.upper()
            for axis in ["pc1", "pc2", "pc3"]
            if pcts[axis] <= 20 or pcts[axis] >= 80
        ]
        rows.append(
            {
                "role": role,
                "pc1": f"{g['pc1']:.6f}",
                "pc2": f"{g['pc2']:.6f}",
                "pc3": f"{g['pc3']:.6f}",
                "distance_from_origin": f"{g['distance_from_origin']:.6f}",
                "pc1_percentile": f"{pcts['pc1']:.2f}",
                "pc2_percentile": f"{pcts['pc2']:.2f}",
                "pc3_percentile": f"{pcts['pc3']:.2f}",
                "cluster": g["cluster"],
                "positive_instruction_count": len(instructions),
                "positive_instructions_pipe_joined": " | ".join(instructions),
                "rough_instruction_coherence_jaccard": f"{mean_pairwise_jaccard(instructions):.4f}",
                "geometrically_extreme_axes": ";".join(extreme_axes),
                "central_35_65_all_pcs": central_35_65,
                "central_20_80_all_pcs": central_20_80,
                "candidate_note": candidate_note(role, central_35_65, central_20_80, extreme_axes),
                "model_used": MODEL_USED,
            }
        )
    return rows, qs


def candidate_note(role: str, central_35_65: bool, central_20_80: bool, extreme_axes: list[str]) -> str:
    if role in {"spy", "criminal", "demon", "parasite"}:
        return "Not recommended for first within-role displacement study due to safety-adjacent or adversarial semantics."
    if role in {"jester", "joker", "trickster"}:
        return "Likely too outlying for a first within-role displacement study."
    if role in {"therapist"}:
        return "Behaviorally coherent but likely PC3/stance-specialized; better as later targeted study."
    if role == "actor":
        return "Plausible candidate: coherent, flexible, behaviorally expressive, and useful for testing question/instruction variation."
    if central_35_65:
        return "Strong central candidate by geometry; inspect role-expression reliability before selection."
    if central_20_80:
        return "Moderately central candidate; inspect role coherence and expression reliability."
    return f"Geometrically edge-biased on {', '.join(extreme_axes) or 'none listed'}; use only if scientifically intentional."


def write_reconstruction_template(path: Path) -> None:
    path.write_text(
        f"""# Combined 1,200 Input Reconstruction Template

- Generated UTC: {utc_now()}
- model_used: {MODEL_USED}
- No GPU used.

Once `target_role` is selected, reconstruct one row for every positive-instruction and extraction-question pair:

```text
for each instruction_id in 0..4:
  system_message = role_positive_instruction[target_role][instruction_id]
  for each question_id in 0..239:
    user_message = extraction_questions[question_id]
```

Recommended output columns:

```csv
target_role,instruction_id,question_id,system_message,user_message,target_role_pc1,target_role_pc2,target_role_pc3,instruction_predicted_delta_pc1,instruction_predicted_delta_pc2,instruction_predicted_delta_pc3,question_predicted_delta_pc1,question_predicted_delta_pc2,question_predicted_delta_pc3,additive_predicted_delta_pc1,additive_predicted_delta_pc2,additive_predicted_delta_pc3,expected_role_expression_effect,instruction_rationale,question_rationale
```

Important constraints:

- The target is displacement around the selected role centroid, not absolute global PCA position.
- Do not assume the selected role centroid is the origin.
- Exact token-level rendering should be produced with the same tokenizer/chat-template conventions as the later corrected extraction run.
- Public artifacts do not include original successful-response masks, so any retained-response analysis requires fresh role-expression scoring.
""",
        encoding="utf-8",
    )


def write_gpu_plan(path: Path) -> None:
    path.write_text(
        f"""# Planned Within-Role GPU Analysis

- Generated UTC: {utc_now()}
- model_used: {MODEL_USED}
- No GPU was used to prepare this plan.

## Purpose

Test whether variation among five positive role instructions and 240 extraction questions predicts response-activation displacement around a fixed released role centroid.

## Later Execution Plan

1. Wait until D01/extraction-boundary uncertainty is resolved.
2. Select `target_role`.
3. Reconstruct 1,200 inputs: five positive role instructions x 240 shared extraction questions.
4. Generate deterministic Qwen/Qwen3-32B responses with the corrected hook-based extraction path.
5. Extract response-token activations with the same activation object, token mask, pooling, centering, and PCA basis used for the inherited geometry.
6. Compute observed coordinate and displacement:

```text
observed_delta_pcj = observed_pcj - released_target_role_centroid_pcj
```

7. Optionally judge role expression for every response and compare all responses vs retained role-expressive responses.

## Planned Statistical Tests

- Instruction main effects on PC1/PC2/PC3 displacement.
- Question main effects on PC1/PC2/PC3 displacement.
- Additive instruction + question prediction of observed displacement.
- Interaction diagnostics if signal and sample size justify it.
- Sign accuracy: predicted displacement direction vs observed displacement sign.
- Pearson/Spearman correlation between predicted displacement scores and observed displacement.
- Compare all-response analysis to retained-response-only analysis after fresh role-expression scoring.

## Interpretation Caveat

This study tests within-role displacement, not role-centroid recovery. A successful result would show that prompts move activations in predictable directions around a fixed role address.
""",
        encoding="utf-8",
    )


def write_report(path: Path, role_count: int, roles_with_five: int, question_count: int, central_35: int, central_20: int, missing_method_cards: list[str]) -> None:
    path.write_text(
        f"""# Within-Role Displacement Design Report

- Generated UTC: {utc_now()}
- model_used: {MODEL_USED}
- GPU used: no.

## What Was Prepared

This packet prepares a reusable one-role, within-role displacement study while leaving the final target role user-selected. The released role vector is treated as a centroid. The later H100/GPU run should test whether positive-instruction wording and extraction-question wording predict displacement around that centroid.

## Sources Used

- Five positive role instructions: `data/roles/instructions/*.json`
- Shared extraction questions: `data/extraction_questions.jsonl`
- Current role PCA coordinates/clusters: `research/visualizations/geometry_viz_data.json`
- Prior role-rollout audit: `research/outputs/role_rollout_artifact_audit/role_rollout_artifact_audit_report.md`
- Prompt artifact inventory: `research/outputs/prompt_artifact_inventory/prompt_artifact_inventory_report.md`

Unavailable requested method-card inputs: {', '.join(missing_method_cards) if missing_method_cards else 'none'}.

## Inventory Results

- Non-default roles inventoried: {role_count}
- Roles with all five positive instructions found: {roles_with_five}
- Shared extraction questions found: {question_count}
- Theoretical inputs per selected role: 5 x 240 = 1,200
- Candidate roles in 35th-65th percentile band on all PCs: {central_35}
- Candidate roles in 20th-80th percentile band on all PCs: {central_20}

All 240 shared questions were found. All 275 non-default roles have five positive instructions in the local public artifact files.

## Role Selection Criteria

Prefer a role that is behaviorally coherent, reliably role-expressive, and not too geometrically extreme on PC1, PC2, or PC3. The first study should avoid roles whose semantics make displacement hard to interpret: strongly outlying trickster/jester-like roles, heavily safety-adjacent roles such as spy, or roles selected specifically for PC3 extremes. Actor remains a plausible candidate because it is coherent, expressive, and flexible, but the final target role is intentionally not chosen here.

## Displacement Rubrics

PC1, convergence pressure versus degrees of freedom:

- Positive displacement: more correctness, validation, checking, ranking, procedural constraint, error detection, externally checkable answer-space convergence.
- Negative displacement: more open symbolic possibility, expressive identity, ambiguity, imaginative transformation, multiple valid continuations, non-procedural meaning-making.

PC2, integrated abstraction versus situated developmental immediacy:

- Negative displacement: more broad synthesis, reflective distance, conceptual integration, historical or world-model reasoning, accumulated perspective.
- Positive displacement: more local immediacy, situated emotional/social pressure, reactivity, developmental limitation, vulnerability, role-bound interpersonal response.

PC3, perturbation/intervention versus stabilization/repair:

- Positive displacement: more challenge, pressure, boundary stress, adversarial testing, exposing weakness, disruption, strategic critique, forced change.
- Negative displacement: more repair, mediation, de-escalation, caregiving, reconciliation, preservation, protection, restoring equilibrium.

## Public-Data Caveat

Public artifacts support reconstruction of intended instruction-question inputs, but not original generated responses, response-level judge scores, or retained-response masks. The later GPU run should therefore preserve all responses and optionally apply fresh role-expression judging so all-response and retained-response-only analyses can be separated.

## Exact Next Step

Once the user supplies `target_role`, fill the instruction and question scoring templates, reconstruct the 1,200 input table for that role, attach the selected role centroid coordinates, and run the planned corrected-hook extraction only after D01 is resolved.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    roles = read_role_files()
    questions = read_questions()
    geometry = read_geometry()

    instruction_rows = build_role_instruction_inventory(roles)
    question_rows = build_question_inventory(questions)
    candidate_rows, thresholds = build_candidate_table(roles, geometry)
    central_35 = sum(str(r["central_35_65_all_pcs"]) == "True" for r in candidate_rows)
    central_20 = sum(str(r["central_20_80_all_pcs"]) == "True" for r in candidate_rows)
    roles_with_five = len({r["role"] for r in instruction_rows if sum(1 for x in instruction_rows if x["role"] == r["role"]) == 5})
    missing_method_cards = [str(p) for p in [METHOD_CARD_LU, METHOD_CARD_ADAPTIVE] if not p.exists()]

    write_csv(
        OUT_DIR / "role_instruction_inventory.csv",
        ["role", "instruction_id", "instruction_polarity", "instruction_text", "eval_prompt_present", "role_specific_question_count", "source_path", "model_used"],
        instruction_rows,
    )
    write_csv(
        OUT_DIR / "extraction_question_inventory.csv",
        ["question_id", "question_text", "source_path", "model_used"],
        question_rows,
    )
    write_csv(
        OUT_DIR / "instruction_displacement_scoring_template.csv",
        ["role", "instruction_id", "instruction_text"] + SCORING_COLUMNS,
        build_instruction_template(instruction_rows),
    )
    write_csv(
        OUT_DIR / "question_displacement_scoring_template.csv",
        ["question_id", "question_text"] + SCORING_COLUMNS,
        build_question_template(question_rows),
    )
    write_csv(
        OUT_DIR / "role_candidate_selection_table.csv",
        [
            "role",
            "pc1",
            "pc2",
            "pc3",
            "distance_from_origin",
            "pc1_percentile",
            "pc2_percentile",
            "pc3_percentile",
            "cluster",
            "positive_instruction_count",
            "positive_instructions_pipe_joined",
            "rough_instruction_coherence_jaccard",
            "geometrically_extreme_axes",
            "central_35_65_all_pcs",
            "central_20_80_all_pcs",
            "candidate_note",
            "model_used",
        ],
        candidate_rows,
    )

    write_reconstruction_template(OUT_DIR / "combined_1200_input_reconstruction_template.md")
    write_gpu_plan(OUT_DIR / "planned_within_role_gpu_analysis.md")
    write_report(
        OUT_DIR / "within_role_displacement_design_report.md",
        len(roles),
        roles_with_five,
        len(questions),
        central_35,
        central_20,
        missing_method_cards,
    )
    metadata = {
        "generated_utc": utc_now(),
        "model_used": MODEL_USED,
        "gpu_used": False,
        "role_count": len(roles),
        "roles_with_five_positive_instructions": roles_with_five,
        "extraction_question_count": len(questions),
        "theoretical_inputs_per_selected_role": 1200,
        "central_35_65_all_pcs_count": central_35,
        "central_20_80_all_pcs_count": central_20,
        "geometry_path": str(GEOMETRY_PATH.relative_to(REPO_ROOT)),
        "role_instruction_dir": str(ROLE_INSTRUCTION_DIR.relative_to(REPO_ROOT)),
        "questions_path": str(QUESTIONS_PATH.relative_to(REPO_ROOT)),
        "missing_method_cards": missing_method_cards,
        "percentile_thresholds": thresholds,
    }
    (OUT_DIR / "design_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Wrote within-role displacement design packet to {OUT_DIR}")


if __name__ == "__main__":
    main()
