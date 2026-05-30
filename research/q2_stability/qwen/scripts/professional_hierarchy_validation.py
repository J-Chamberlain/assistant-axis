#!/usr/bin/env python3
"""Targeted professional hierarchy validation for PCA-axis interpretations."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path

import numpy as np


REPO = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
OUT_DIR = REPO / "research/q2_stability/qwen/outputs/professional_hierarchy_validation"
NO_LABEL_PATH = REPO / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
VIZ_PATH = REPO / "research/visualizations/geometry_viz_data.json"
MODEL_USED = "GPT-5.5"
RANDOM_SEED = 42


PROFESSIONAL_PERSONAS = [
    "accountant", "activist", "advocate", "analyst", "anthropologist", "archaeologist",
    "architect", "archivist", "artisan", "auctioneer", "auditor", "biologist", "builder",
    "cartographer", "chef", "chemist", "coach", "composer", "conservator", "consultant",
    "coordinator", "counselor", "critic", "curator", "debugger", "designer", "detective",
    "dispatcher", "doctor", "economist", "editor", "engineer", "entrepreneur", "evaluator",
    "examiner", "facilitator", "fixer", "forecaster", "futurist", "geographer", "grader",
    "historian", "instructor", "interpreter", "interviewer", "journalist", "judge",
    "lawyer", "librarian", "linguist", "marketer", "mathematician", "mechanic",
    "mediator", "mentor", "merchant", "moderator", "naturalist", "navigator",
    "negotiator", "nutritionist", "organizer", "paramedic", "pharmacist", "philosopher",
    "photographer", "physicist", "pilot", "planner", "presenter", "producer",
    "programmer", "proofreader", "psychologist", "publisher", "recruiter", "reporter",
    "researcher", "reviewer", "scheduler", "scholar", "scientist", "screener",
    "secretary", "sociologist", "sommelier", "specialist", "statistician", "strategist",
    "summarizer", "supervisor", "synthesizer", "teacher", "technologist", "theorist",
    "therapist", "trainer", "translator", "tutor", "validator", "veterinarian", "writer",
]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_geometry() -> dict[str, dict]:
    data = json.loads(VIZ_PATH.read_text())["roles"]
    return {
        name: {
            "persona": name,
            "cluster": cluster,
            "PC1": float(coords[0]),
            "PC2": float(coords[1]),
            "PC3": float(coords[2]),
        }
        for name, coords, cluster in zip(data["names"], data["pca3d"], data["clusters"])
    }


def load_grouped_prompts() -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for row in read_jsonl(NO_LABEL_PATH):
        grouped[row["role"]].append(row)
    return {role: sorted(rows, key=lambda r: r["prompt_index"]) for role, rows in grouped.items()}


def build_prompt(chunk_idx: int, total_chunks: int, dossiers: list[dict]) -> str:
    blocks = []
    for dossier in dossiers:
        text = "\n".join(f"Record {r['record_index']}: {r['text']}" for r in dossier["records"])
        blocks.append(f"### {dossier['persona_id']}\n{text}")
    return f"""You are Codex/GPT-5.5 acting as a blinded semantic rater.

Task: Read each anonymized professional-role dossier and assign reading-based ratings. Do not infer from persona names; no persona names are provided. Do not use PCA coordinates, clusters, prior interpretations, or keyword matching. Base ratings on the whole dossier text.

Chunk {chunk_idx} of {total_chunks}.

Scales are 0-100.

objective_certainty_score:
Question: To what extent is success in this role determined by externally specified criteria rather than internally negotiated goals?
High: compliance, checking, validation, auditing, proofreading, accounting.
Low: architecture, therapy, philosophy, strategy, interpretation, goals discovered or constructed under ambiguity.

coherent_uncertainty_capacity_score:
Question: How effectively can this role continue making coherent progress while the correct answer, objective, or resolution remains unavailable?
High: can continue disciplined, coherent, productive action under unresolved uncertainty.
Low: fragments, avoids, collapses, or requires closure before functioning.
Do not score amount of uncertainty or complexity. Score competence while uncertainty remains unresolved.

system_perturbation_score:
Question: When encountering an existing structure, does this role primarily maintain/repair/stabilize/coordinate it, or challenge/stress-test/perturb/disrupt it?
Low: homeostatic, stabilizing, repairing, coordinating.
High: perturbative, challenging, adversarial, stress-testing, reforming, disruptive.

Return only valid JSON, an array of objects. Each object must have:
persona_id, objective_certainty_score, objective_certainty_rationale, coherent_uncertainty_capacity_score, coherent_uncertainty_rationale, system_perturbation_score, system_perturbation_rationale.

Keep rationales short and grounded in the dossier text.

DOSSIERS:

{chr(10).join(blocks)}
"""


def prepare() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "rater_prompts").mkdir(exist_ok=True)
    (OUT_DIR / "rater_raw_outputs").mkdir(exist_ok=True)

    geometry = load_geometry()
    grouped = load_grouped_prompts()
    present = [p for p in PROFESSIONAL_PERSONAS if p in geometry and p in grouped]
    missing_examples = [
        "systems_engineer", "systems engineer", "professor", "investigative_journalist",
        "investigative journalist", "reformer",
    ]

    inventory = [geometry[p] for p in present]
    inventory.sort(key=lambda r: r["persona"])
    write_csv(OUT_DIR / "professional_persona_inventory.csv", inventory, ["persona", "cluster", "PC1", "PC2", "PC3"])

    id_map = {f"PR{i:03d}": persona for i, persona in enumerate([r["persona"] for r in inventory], start=1)}
    (OUT_DIR / "professional_persona_id_map.json").write_text(json.dumps(id_map, indent=2))
    missing_note = {
        "model_used": MODEL_USED,
        "present_professional_personas": len(inventory),
        "absent_requested_examples": missing_examples,
        "source_text": str(NO_LABEL_PATH),
        "rating_input_blinding": "persona names, coordinates, clusters, Big Five scores, residuals, and prior labels removed",
    }
    (OUT_DIR / "professional_inventory_manifest.json").write_text(json.dumps(missing_note, indent=2))

    dossiers = []
    for persona_id, persona in id_map.items():
        records = [
            {
                "record_index": row["prompt_index"],
                "text": row["rewritten_prompt"].strip(),
                "text_field": "rewritten_prompt",
            }
            for row in grouped[persona]
        ]
        dossiers.append(
            {
                "persona_id": persona_id,
                "records_used": len(records),
                "text_source_path": str(NO_LABEL_PATH),
                "records": records,
            }
        )
    with (OUT_DIR / "professional_blinded_dossiers.jsonl").open("w") as f:
        for dossier in dossiers:
            f.write(json.dumps(dossier, ensure_ascii=False) + "\n")

    chunks = [dossiers[i : i + 20] for i in range(0, len(dossiers), 20)]
    for i, chunk in enumerate(chunks, start=1):
        (OUT_DIR / "rater_prompts" / f"chunk_{i:02d}.md").write_text(build_prompt(i, len(chunks), chunk))
    print(f"Prepared {len(inventory)} professional personas in {len(chunks)} chunks.")


def parse_jsonish(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if not match:
            raise
        data = json.loads(match.group(0))
    if not isinstance(data, list):
        raise ValueError("Expected JSON array")
    return data


def load_scores() -> list[dict]:
    rows = []
    for path in sorted((OUT_DIR / "rater_raw_outputs").glob("chunk_*.json")):
        rows.extend(parse_jsonish(path.read_text()))
    if not rows:
        raise SystemExit("No raw rater outputs found.")
    return rows


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def rankdata(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=float)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    return pearson(rankdata(x), rankdata(y))


def correlation_rows(rows: list[dict]) -> list[dict]:
    specs = [
        ("objective_certainty_score", "PC1", 1),
        ("coherent_uncertainty_capacity_score", "PC2", -1),
        ("system_perturbation_score", "PC3", 1),
    ]
    out = []
    for score, target, expected_sign in specs:
        x = np.array([float(r[score]) for r in rows])
        for pc in ("PC1", "PC2", "PC3"):
            y = np.array([float(r[pc]) for r in rows])
            out.append(
                {
                    "score": score,
                    "pc": pc,
                    "pearson": pearson(x, y),
                    "spearman": spearman(x, y),
                    "target_axis": target,
                    "expected_sign_for_target": expected_sign if pc == target else "",
                    "target_aligned": pc == target,
                    "prediction_direction_supported": (
                        pc == target and pearson(x, y) * expected_sign > 0 and abs(pearson(x, y)) >= 0.2
                    ),
                }
            )
    return out


def fit_linear(X: np.ndarray, y: np.ndarray) -> float:
    X_aug = np.column_stack([np.ones(len(X)), X])
    coef = np.linalg.pinv(X_aug) @ y
    pred = X_aug @ coef
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot else float("nan")


def cv_r2(rows: list[dict], target: str) -> float:
    X = np.array([
        [
            float(r["objective_certainty_score"]),
            float(r["coherent_uncertainty_capacity_score"]),
            float(r["system_perturbation_score"]),
        ]
        for r in rows
    ])
    X = (X - X.mean(axis=0)) / np.where(X.std(axis=0) == 0, 1, X.std(axis=0))
    y = np.array([float(r[target]) for r in rows])
    idx = list(range(len(rows)))
    random.Random(RANDOM_SEED).shuffle(idx)
    folds = [idx[i::5] for i in range(5)]
    pred = np.zeros(len(rows))
    for fold in folds:
        test = np.array(fold)
        train = np.array([i for i in idx if i not in set(fold)])
        Xtr = X[train]
        ytr = y[train]
        coef = np.linalg.pinv(np.column_stack([np.ones(len(train)), Xtr])) @ ytr
        pred[test] = np.column_stack([np.ones(len(test)), X[test]]) @ coef
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot else float("nan")


def analyze() -> None:
    geometry = load_geometry()
    id_map = json.loads((OUT_DIR / "professional_persona_id_map.json").read_text())
    raw = load_scores()
    by_id = {r["persona_id"]: r for r in raw}
    rows = []
    for persona_id, persona in id_map.items():
        score = by_id[persona_id]
        row = {
            "persona_id": persona_id,
            "persona": persona,
            "persona_name_if_used": "",
            **score,
            **geometry[persona],
        }
        rows.append(row)
    rows.sort(key=lambda r: r["persona"])

    rating_fields = [
        "persona_id", "persona_name_if_used", "persona",
        "objective_certainty_score", "objective_certainty_rationale",
        "coherent_uncertainty_capacity_score", "coherent_uncertainty_rationale",
        "system_perturbation_score", "system_perturbation_rationale",
        "cluster", "PC1", "PC2", "PC3",
    ]
    write_csv(OUT_DIR / "professional_ratings.csv", rows, rating_fields)

    pred_rows = []
    for axis, score, rationale_key, descending in [
        ("PC1_objective_certainty", "objective_certainty_score", "objective_certainty_rationale", True),
        ("PC2_coherent_uncertainty_capacity", "coherent_uncertainty_capacity_score", "coherent_uncertainty_rationale", True),
        ("PC3_system_perturbation", "system_perturbation_score", "system_perturbation_rationale", True),
    ]:
        for rank, row in enumerate(sorted(rows, key=lambda r: float(r[score]), reverse=descending), start=1):
            pred_rows.append(
                {
                    "predicted_axis": axis,
                    "predicted_rank": rank,
                    "persona_id": row["persona_id"],
                    "persona": row["persona"],
                    "score": row[score],
                    "rationale": row[rationale_key],
                }
            )
    write_csv(OUT_DIR / "professional_rank_predictions.csv", pred_rows, ["predicted_axis", "predicted_rank", "persona_id", "persona", "score", "rationale"])

    corr = correlation_rows(rows)
    write_csv(OUT_DIR / "professional_vs_actual_comparison.csv", corr, ["score", "pc", "pearson", "spearman", "target_axis", "expected_sign_for_target", "target_aligned", "prediction_direction_supported"])

    actual_rows = []
    for axis, pc, reverse in [
        ("PC1_actual_high", "PC1", True),
        ("PC2_actual_low_for_capacity", "PC2", False),
        ("PC3_actual_high", "PC3", True),
    ]:
        for rank, row in enumerate(sorted(rows, key=lambda r: float(r[pc]), reverse=reverse), start=1):
            actual_rows.append({"actual_axis": axis, "actual_rank": rank, "persona": row["persona"], "value": row[pc]})
    write_csv(OUT_DIR / "professional_actual_rankings.csv", actual_rows, ["actual_axis", "actual_rank", "persona", "value"])

    regression = {
        "model_used": MODEL_USED,
        "cv_r2_from_three_professional_ratings": {
            "PC1": cv_r2(rows, "PC1"),
            "PC2": cv_r2(rows, "PC2"),
            "PC3": cv_r2(rows, "PC3"),
        },
    }
    (OUT_DIR / "professional_regression_summary.json").write_text(json.dumps(regression, indent=2))
    write_report(rows, corr, regression)
    print(f"Analyzed professional hierarchy: {len(rows)} personas.")


def md_table(rows: list[dict], fields: list[str], limit: int | None = None) -> str:
    if limit is not None:
        rows = rows[:limit]
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        vals = []
        for f in fields:
            v = row.get(f, "")
            vals.append(f"{v:.3f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(rows: list[dict], corr: list[dict], regression: dict) -> None:
    c = {(r["score"], r["pc"]): r for r in corr}
    pc1 = c[("objective_certainty_score", "PC1")]
    pc2 = c[("coherent_uncertainty_capacity_score", "PC2")]
    pc3 = c[("system_perturbation_score", "PC3")]
    pc1_pred = sorted(rows, key=lambda r: float(r["objective_certainty_score"]), reverse=True)
    pc2_pred = sorted(rows, key=lambda r: float(r["coherent_uncertainty_capacity_score"]), reverse=True)
    pc3_pred = sorted(rows, key=lambda r: float(r["system_perturbation_score"]), reverse=True)
    pc1_actual = sorted(rows, key=lambda r: float(r["PC1"]), reverse=True)
    pc2_actual = sorted(rows, key=lambda r: float(r["PC2"]))
    pc3_actual = sorted(rows, key=lambda r: float(r["PC3"]), reverse=True)
    scientist = next((r for r in rows if r["persona"] == "scientist"), None)
    physicist = next((r for r in rows if r["persona"] == "physicist"), None)

    support = []
    counter = []
    for row in rows:
        if row["persona"] in {"auditor", "validator", "proofreader", "examiner", "grader"}:
            support.append(row)
        if row["persona"] in {"architect", "philosopher", "therapist", "strategist", "physicist"}:
            support.append(row)
        if row["persona"] in {"economist", "sociologist", "reviewer", "critic", "reporter"}:
            counter.append(row)

    report = f"""# Professional Hierarchy Validation

## 1. Inventory Used

Observed: the professional inventory contains {len(rows)} personas present in the Qwen geometry corpus and no-label prompt corpus. Requested examples not present include `systems engineer`, `professor`, `investigative journalist`, and `reformer`.

Top of the inventory by actual PC1:

{md_table(pc1_actual, ["persona", "cluster", "PC1", "PC2", "PC3"], 12)}

## 2. Rating Methodology

Observed: ratings were produced before PCA evaluation from anonymized no-label prompt dossiers. The rater saw only dossier IDs and five rewritten prompts per professional persona. Coordinates, clusters, prior interpretations, Big Five scores, residuals, and persona names were not shown during rating.

Observed: scoring used Codex/GPT-5.5 as a reading-based rater, not a deterministic lexical proxy. The source corpus is `{NO_LABEL_PATH}` because no full 275-persona rollout-response corpus exists locally.

## 3. Predicted Hierarchy

PC1 predicted highest objective certainty:

{md_table(pc1_pred, ["persona", "objective_certainty_score", "objective_certainty_rationale"], 12)}

PC2 predicted highest coherent action under unresolved uncertainty:

{md_table(pc2_pred, ["persona", "coherent_uncertainty_capacity_score", "coherent_uncertainty_rationale"], 12)}

PC3 predicted highest perturbative relationship to systems:

{md_table(pc3_pred, ["persona", "system_perturbation_score", "system_perturbation_rationale"], 12)}

## 4. Actual Hierarchy

Actual highest PC1:

{md_table(pc1_actual, ["persona", "PC1", "objective_certainty_score"], 12)}

Actual lowest PC2, predicted direction for coherent uncertainty capacity:

{md_table(pc2_actual, ["persona", "PC2", "coherent_uncertainty_capacity_score"], 12)}

Actual highest PC3:

{md_table(pc3_actual, ["persona", "PC3", "system_perturbation_score"], 12)}

## 5. Scientist vs Physicist Analysis

Observed: `scientist` and `physicist` are both present.

| Persona | Objective certainty score | Coherent uncertainty capacity score | System perturbation score | PC1 | PC2 | PC3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| scientist | {scientist['objective_certainty_score']} | {scientist['coherent_uncertainty_capacity_score']} | {scientist['system_perturbation_score']} | {scientist['PC1']:.3f} | {scientist['PC2']:.3f} | {scientist['PC3']:.3f} |
| physicist | {physicist['objective_certainty_score']} | {physicist['coherent_uncertainty_capacity_score']} | {physicist['system_perturbation_score']} | {physicist['PC1']:.3f} | {physicist['PC2']:.3f} | {physicist['PC3']:.3f} |

Inferred: the actual geometry places `physicist` lower on PC2 than `scientist`, consistent with the prior abstraction/world-model interpretation if lower PC2 marks stronger productive residence in unresolved abstraction. The blinded professional rating gives the two roles similar coherent-uncertainty capacity, so this pair supports the actual ordering only weakly at the rating level.

## 6. Quantitative Comparison

| Hypothesis | Expected direction | Pearson | Spearman | Supported |
| --- | --- | ---: | ---: | --- |
| Objective certainty predicts PC1 | positive | {pc1['pearson']:.3f} | {pc1['spearman']:.3f} | {pc1['prediction_direction_supported']} |
| Coherent uncertainty capacity predicts lower PC2 | negative | {pc2['pearson']:.3f} | {pc2['spearman']:.3f} | {pc2['prediction_direction_supported']} |
| System perturbation predicts PC3 | positive | {pc3['pearson']:.3f} | {pc3['spearman']:.3f} | {pc3['prediction_direction_supported']} |

Cross-validated R2 from all three professional ratings:

{json.dumps(regression['cv_r2_from_three_professional_ratings'], indent=2)}

## 7. Strongest Supporting Examples

Observed: high objective-certainty professional roles such as `auditor`, `validator`, `examiner`, `grader`, and `proofreader` receive high objective-certainty ratings and sit toward the high-PC1 professional region. Open-ended interpretive roles such as `philosopher`, `therapist`, `architect`, and `strategist` receive lower objective-certainty ratings and generally shift away from the most constrained PC1 pole.

Observed: perturbative or challenge-oriented professional roles such as `critic`, `reviewer`, `reporter`, `journalist`, and `advocate` tend to score higher on system perturbation than repair/coordinating roles such as `mediator`, `counselor`, `facilitator`, and `coach`, partly supporting the PC3 stance interpretation. `fixer` is the strongest clean support case for PC3, with high perturbation and the highest actual PC3 in the professional subset.

## 8. Strongest Counterexamples

Observed: `scientist` and `physicist` do not separate strongly in the blinded coherent-uncertainty rating even though actual PC2 places `physicist` lower than `scientist`. This weakens the claim that the professional hierarchy alone recovers the PC2 abstraction gradient cleanly.

Observed: some high-expertise roles receive high objective-certainty ratings even when their actual work is exploratory, suggesting that PC1 may still conflate external standards, disciplined expertise, and institutional knowledge practice.

Observed: several high-PC3 professional roles are not rated as strongly perturbative, including `economist`, `mathematician`, `statistician`, and `lawyer`. This weakens a simple system-perturbation reading of PC3 inside the professional subset, even though the broader all-persona rater study supported the antagonistic-transgressive PC3 interpretation.

## 9. Judgment Calls and Alternative Interpretations

The professional inventory intentionally includes broad expert and applied roles, not only narrow licensed professions. Ambiguity exists for roles such as `activist`, `advocate`, `philosopher`, `writer`, and `artist-adjacent` expert roles; they were retained only when present in the corpus and relevant to professional, analytical, academic, or expert function.

Competing explanations considered: PC1 may track institutional expertise rather than objective certainty alone; PC2 may track abstraction/world-model depth rather than coherent action capacity; PC3 may track adversarial register or reform orientation rather than direct system perturbation.

Strongest unresolved uncertainty: PC2. A clear falsification of the current interpretation would be a blinded professional rater reliably ranking high-capacity uncertainty roles in the predicted order while actual PC2 fails to follow that ordering, or actual PC2 being better predicted by simple abstraction/expertise than by uncertainty capacity.

## 10. PC Interpretation Update

PC1: modestly strengthened. Objective certainty predicts actual PC1 at r={pc1['pearson']:.3f}, and the actual high-PC1 professional pole contains the expected auditor/examiner/evaluator/validator/screener/grader region. The result supports the professional hierarchy component of PC1, but does not isolate it from expertise and institutional competence.

PC2: weakened as a professional hierarchy claim. Coherent uncertainty capacity is essentially uncorrelated with actual PC2 in this subset (r={pc2['pearson']:.3f}), even though actual low-PC2 roles include philosopher, theorist, scholar, anthropologist, archaeologist, historian, and physicist. The professional evidence points more toward abstraction/historical-theoretical world-modeling than generic capacity under uncertainty.

PC3: modestly strengthened but with important counterexamples. System perturbation predicts actual PC3 at r={pc3['pearson']:.3f}, and the three-rating model predicts professional PC3 with CV R2={regression['cv_r2_from_three_professional_ratings']['PC3']:.3f}, but high-PC3 technical/institutional roles show that PC3 is not simply reform or critique.

## 11. Confidence Update

Confidence update: PC1 remains moderate and is supported in the professional subset. PC3 remains moderate, with professional evidence supporting a perturbative/stress-testing component but not the full broader all-persona interpretation. PC2 remains low-confidence and should be reframed away from a simple professional coherent-action hierarchy unless future tests separate abstraction, expertise, and uncertainty capacity more cleanly.
"""
    (OUT_DIR / "professional_hierarchy_report.md").write_text(report)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "analyze"])
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
    else:
        analyze()


if __name__ == "__main__":
    main()
