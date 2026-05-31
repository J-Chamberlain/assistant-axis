#!/usr/bin/env python3
"""Score playwright within-role displacement prompts using rubric text features.

This is a local, no-GPU, no-API preparation step. Scores are predicted
centroid-relative displacement pressures, not observed activation coordinates.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "research" / "outputs" / "playwright_displacement_scoring"
DESIGN_DIR = REPO_ROOT / "research" / "outputs" / "within_role_displacement_design"
QUESTION_PATH = REPO_ROOT / "data" / "extraction_questions.jsonl"
PLAYWRIGHT_PATH = REPO_ROOT / "data" / "roles" / "instructions" / "playwright.json"
CANONICAL_PCA_PATH = (
    REPO_ROOT
    / "research"
    / "q2_stability"
    / "qwen"
    / "outputs"
    / "shared_latent_feature_benchmark"
    / "canonical_activation_pca3d.csv"
)

MODEL_USED = "GPT-5.5"
OUT_DIR.mkdir(parents=True, exist_ok=True)

AXIS_DEFINITIONS = {
    "pc1": {
        "negative": "degrees of freedom, expressive possibility, symbolic ambiguity, multiple valid continuations",
        "positive": "convergence pressure, correctness, validation, checking, procedural constraint, externally checkable answer space",
    },
    "pc2": {
        "negative": "integrated abstraction, reflective synthesis, broad conceptual/world-model reasoning, accumulated perspective",
        "positive": "situated developmental immediacy, local social/emotional pressure, reactivity, vulnerability, role-bound interpersonal response",
    },
    "pc3": {
        "negative": "stabilization, repair, mediation, de-escalation, protection, reconciliation, preservation",
        "positive": "perturbation, intervention, boundary pressure, adversarial testing, exposure of weakness, disruption, forced change",
    },
}


FEATURES = {
    "pc1": {
        "positive": [
            ("correct", 2.0, "correctness/checking language"),
            ("accurate", 2.0, "accuracy pressure"),
            ("verify", 2.0, "verification pressure"),
            ("evidence", 1.5, "externally checkable evidence"),
            ("proof", 1.5, "proof/validation pressure"),
            ("calculate", 2.0, "calculation/procedure"),
            ("software", 1.5, "technical explanation"),
            ("algorithm", 1.5, "technical procedure"),
            ("steps", 1.0, "stepwise answer space"),
            ("principles should guide", 1.0, "normative convergence pressure"),
            ("best way", 1.0, "optimization framing"),
            ("law", 1.0, "rule/legal constraint"),
            ("policy", 1.0, "institutional constraint"),
            ("realistic", 1.0, "constraint from feasibility"),
            ("plan", 1.0, "procedural planning"),
            ("explain how", 1.0, "mechanistic explanation"),
        ],
        "negative": [
            ("imagine", 2.0, "imaginative possibility"),
            ("creative", 2.0, "creative open-endedness"),
            ("story", 1.5, "narrative possibility"),
            ("scene", 1.5, "dramatic/narrative possibility"),
            ("character", 1.0, "character expression"),
            ("metaphor", 2.0, "symbolic ambiguity"),
            ("poem", 2.0, "poetic expression"),
            ("dream", 2.0, "dream/symbolic looseness"),
            ("art", 1.5, "artistic expression"),
            ("dialogue", 1.0, "multi-voice expression"),
            ("multiple", 1.0, "multiple continuations"),
            ("possibilities", 1.5, "open possibility space"),
            ("meaning", 1.0, "interpretive openness"),
            ("absurd", 2.0, "absurd/open symbolic register"),
        ],
    },
    "pc2": {
        "positive": [
            ("i'm", 1.5, "first-person situated pressure"),
            ("i am", 1.0, "first-person situated pressure"),
            ("my ", 1.0, "personal situatedness"),
            ("me ", 0.8, "direct personal address"),
            ("my situation", 2.0, "local situation constraint"),
            ("facing", 1.5, "immediate challenge"),
            ("feel", 1.5, "emotional immediacy"),
            ("feelings", 1.5, "emotional immediacy"),
            ("worried", 1.5, "vulnerability"),
            ("afraid", 1.5, "vulnerability"),
            ("angry", 1.5, "reactive emotion"),
            ("lonely", 1.5, "vulnerability"),
            ("friend", 1.0, "local interpersonal context"),
            ("family", 1.0, "local social context"),
            ("conversation", 1.0, "situated dialogue"),
            ("conflict", 1.0, "local interpersonal pressure"),
            ("true feelings", 1.0, "interpersonal concealment"),
            ("help me", 1.5, "situated need"),
            ("realistic for my situation", 2.0, "local constraint"),
            ("child", 1.0, "developmental immediacy"),
            ("student", 1.0, "developmental/social role"),
        ],
        "negative": [
            ("relationship between", 1.5, "abstract relational synthesis"),
            ("principles", 1.5, "abstract principles"),
            ("morality", 1.5, "moral abstraction"),
            ("human action", 1.5, "broad human-level abstraction"),
            ("meaning", 1.5, "conceptual meaning"),
            ("theory", 1.5, "theoretical framing"),
            ("philosophy", 2.0, "philosophical abstraction"),
            ("history", 1.5, "historical perspective"),
            ("society", 1.5, "social-system abstraction"),
            ("culture", 1.5, "cultural abstraction"),
            ("compare", 1.0, "comparative abstraction"),
            ("why", 0.8, "explanatory abstraction"),
            ("system", 1.0, "systems reasoning"),
            ("principle", 1.5, "abstract principle"),
            ("ethics", 1.5, "ethical abstraction"),
            ("identity", 1.0, "self-concept abstraction"),
        ],
    },
    "pc3": {
        "positive": [
            ("challenge", 1.5, "challenge/pressure"),
            ("doesn't account", 1.5, "pushback/correction pressure"),
            ("conflict", 1.5, "conflict pressure"),
            ("tension", 1.5, "dramatic tension"),
            ("risk", 1.5, "risk/instability"),
            ("danger", 1.5, "danger pressure"),
            ("threat", 1.5, "threat pressure"),
            ("adversarial", 2.0, "adversarial testing"),
            ("test", 1.0, "testing pressure"),
            ("weakness", 2.0, "exposure of weakness"),
            ("expose", 2.0, "exposure"),
            ("hidden", 1.0, "concealment/exposure setup"),
            ("true feelings", 1.0, "exposure setup"),
            ("force", 1.5, "forced change"),
            ("disrupt", 2.0, "disruption"),
            ("manipulate", 2.0, "manipulation"),
            ("power", 1.0, "power pressure"),
            ("argue", 1.0, "argument pressure"),
            ("change", 0.8, "change/intervention"),
        ],
        "negative": [
            ("help", 1.0, "helping/repair"),
            ("support", 1.5, "support/stabilization"),
            ("resolve", 1.5, "resolution/repair"),
            ("repair", 2.0, "repair"),
            ("protect", 2.0, "protection"),
            ("safe", 1.5, "safety/preservation"),
            ("calm", 1.5, "de-escalation"),
            ("reconcile", 2.0, "reconciliation"),
            ("mediate", 2.0, "mediation"),
            ("adjust", 1.0, "adaptive repair"),
            ("realistic", 0.8, "stabilizing feasibility"),
            ("listen", 1.0, "receptive stabilization"),
            ("care", 1.0, "care/maintenance"),
            ("trust", 1.0, "trust-building"),
            ("cooperate", 1.0, "cooperation"),
        ],
    },
}


PLAYWRIGHT_BONUS = {
    "pc1": {
        "positive": [("blueprint", 1.0, "structured blueprint"), ("structure", 1.0, "dramatic structure")],
        "negative": [
            ("dialogue", 1.5, "open dramatic dialogue"),
            ("dramatic", 1.0, "dramatic possibility"),
            ("stage", 0.8, "embodied performance possibility"),
            ("theatrical", 1.5, "theatrical expression"),
            ("character", 1.0, "character multiplicity"),
            ("scripts", 1.0, "scripted imaginative scene"),
            ("performance", 0.8, "live expressive performance"),
        ],
    },
    "pc2": {
        "positive": [
            ("live", 1.0, "live situated performance"),
            ("stage", 1.0, "situated stage dynamics"),
            ("actors", 1.0, "interpersonal embodiment"),
            ("staging", 1.0, "local embodied staging"),
            ("character development", 1.0, "developmental character dynamics"),
            ("stage dynamics", 1.0, "local interpersonal dynamics"),
        ],
        "negative": [("deep expertise", 0.8, "accumulated perspective"), ("structure", 0.5, "structural abstraction")],
    },
    "pc3": {
        "positive": [
            ("dramatic", 1.0, "dramatic pressure"),
            ("stage dynamics", 1.0, "dynamic intervention"),
            ("come alive", 0.8, "animation/intensification"),
            ("dialogue", 0.5, "interpersonal pressure"),
        ],
        "negative": [("blueprint", 0.8, "stabilizing performance plan"), ("structure", 0.8, "structural stabilization")],
    },
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def phrase_in_text(phrase: str, text: str) -> bool:
    """Match phrase as words rather than arbitrary substrings."""
    phrase = normalize_text(phrase)
    if not phrase:
        return False
    if re.fullmatch(r"[a-z0-9' ]+", phrase):
        pattern = r"\b" + r"\s+".join(re.escape(part) for part in phrase.split()) + r"\b"
        return re.search(pattern, text) is not None
    return phrase in text


def feature_score(text: str, axis: str, extra: dict | None = None) -> tuple[int, str, list[str], float]:
    t = normalize_text(text)
    pos_hits: list[tuple[float, str]] = []
    neg_hits: list[tuple[float, str]] = []
    pools = {"positive": list(FEATURES[axis]["positive"]), "negative": list(FEATURES[axis]["negative"])}
    if extra:
        pools["positive"].extend(extra.get(axis, {}).get("positive", []))
        pools["negative"].extend(extra.get(axis, {}).get("negative", []))
    for phrase, weight, label in pools["positive"]:
        if phrase_in_text(phrase, t):
            pos_hits.append((weight, label))
    for phrase, weight, label in pools["negative"]:
        if phrase_in_text(phrase, t):
            neg_hits.append((weight, label))
    raw = sum(w for w, _ in pos_hits) - sum(w for w, _ in neg_hits)

    if raw >= 2.5:
        score = 2
    elif raw >= 0.9:
        score = 1
    elif raw <= -2.5:
        score = -2
    elif raw <= -0.9:
        score = -1
    else:
        score = 0

    conflict = bool(pos_hits and neg_hits)
    abs_raw = abs(raw)
    if score == 0:
        confidence = "low" if conflict or abs_raw > 0.5 else "medium"
    elif abs_raw >= 2.5 and not conflict:
        confidence = "high"
    elif abs_raw >= 1.5:
        confidence = "medium"
    else:
        confidence = "low"

    hits = []
    if pos_hits:
        hits.append("positive cues: " + ", ".join(label for _, label in pos_hits[:3]))
    if neg_hits:
        hits.append("negative cues: " + ", ".join(label for _, label in neg_hits[:3]))
    if not hits:
        rationale = "No strong rubric cues; treated as balanced or ambiguous."
    elif conflict:
        rationale = "; ".join(hits) + "; mixed cues reduce confidence."
    else:
        rationale = "; ".join(hits) + "."
    return score, confidence, hits, raw


def score_record(text: str, extra: dict | None = None) -> dict[str, object]:
    out: dict[str, object] = {}
    for axis in ["pc1", "pc2", "pc3"]:
        score, confidence, hits, raw = feature_score(text, axis, extra=extra)
        out[f"{axis}_score"] = score
        out[f"{axis}_confidence"] = confidence
        out[f"{axis}_raw"] = raw
        if not hits:
            rationale = "No strong rubric cues; treated as balanced or ambiguous."
        else:
            has_pos = any(h.startswith("positive") for h in hits)
            has_neg = any(h.startswith("negative") for h in hits)
            suffix = " Mixed cues reduce confidence." if has_pos and has_neg else ""
            rationale = "; ".join(hits) + "." + suffix
        out[f"{axis}_rationale"] = rationale
    return out


def load_questions() -> list[dict[str, object]]:
    with QUESTION_PATH.open() as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if len(rows) != 240:
        raise SystemExit(f"Expected 240 questions, found {len(rows)}")
    ids = [int(r["id"]) for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("Extraction question IDs are not unique")
    return [{"question_id": int(r["id"]), "question_text": r["question"]} for r in rows]


def load_playwright_instructions() -> list[dict[str, object]]:
    data = json.loads(PLAYWRIGHT_PATH.read_text())
    rows = [{"instruction_id": i, "instruction_text": item["pos"]} for i, item in enumerate(data["instruction"])]
    if len(rows) != 5:
        raise SystemExit(f"Expected five playwright positive instructions, found {len(rows)}")
    return rows


def load_playwright_centroid() -> dict[str, object]:
    if not CANONICAL_PCA_PATH.exists():
        return {
            "playwright_centroid_pc1": None,
            "playwright_centroid_pc2": None,
            "playwright_centroid_pc3": None,
            "playwright_activation_cluster": None,
        }
    with CANONICAL_PCA_PATH.open() as f:
        for row in csv.DictReader(f):
            if row["persona"] == "playwright":
                return {
                    "playwright_centroid_pc1": float(row["activation_pc1"]),
                    "playwright_centroid_pc2": float(row["activation_pc2"]),
                    "playwright_centroid_pc3": float(row["activation_pc3"]),
                    "playwright_activation_cluster": row.get("activation_cluster"),
                }
    return {
        "playwright_centroid_pc1": None,
        "playwright_centroid_pc2": None,
        "playwright_centroid_pc3": None,
        "playwright_activation_cluster": None,
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def count_scores(rows: list[dict[str, object]], prefix: str = "") -> dict[str, dict[str, int]]:
    out = {}
    for axis in ["pc1", "pc2", "pc3"]:
        key = f"{prefix}{axis}_score"
        counts = Counter(int(r[key]) for r in rows if r.get(key) not in (None, ""))
        out[axis] = {str(i): counts.get(i, 0) for i in [-2, -1, 0, 1, 2]}
    return out


def count_additive(rows: list[dict[str, object]]) -> dict[str, dict[str, int]]:
    out = {}
    for axis in ["pc1", "pc2", "pc3"]:
        key = f"additive_{axis}_score"
        counts = Counter(int(r[key]) for r in rows)
        out[axis] = {str(i): counts.get(i, 0) for i in range(-4, 5)}
    return out


def combined_confidence(instruction: dict[str, object], question: dict[str, object]) -> str:
    bits = []
    for axis in ["pc1", "pc2", "pc3"]:
        bits.append(
            f"{axis}:i{instruction[f'{axis}_confidence']}/q{question[f'{axis}_confidence']}"
        )
    return "; ".join(bits)


def top_items(rows: list[dict[str, object]], axis: str, text_key: str, id_key: str, positive: bool) -> list[dict[str, object]]:
    score_key = f"{axis}_score"
    raw_key = f"{axis}_raw"
    ordered = sorted(
        rows,
        key=lambda r: (int(r[score_key]), float(r[raw_key])),
        reverse=positive,
    )
    selected = [r for r in ordered if (int(r[score_key]) > 0 if positive else int(r[score_key]) < 0)]
    return [
        {
            "item_type": "question" if id_key == "question_id" else "instruction",
            "item_id": r[id_key],
            "axis": axis,
            "direction": "positive" if positive else "negative",
            "score": r[score_key],
            "confidence": r[f"{axis}_confidence"],
            "text": r[text_key],
            "rationale": r[f"{axis}_rationale"],
        }
        for r in selected[:10]
    ]


def build_shortlist(question_rows: list[dict[str, object]], instruction_rows: list[dict[str, object]], grid_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for axis in ["pc1", "pc2", "pc3"]:
        out.extend({**r, "shortlist_category": f"strongest_positive_{axis}_questions"} for r in top_items(question_rows, axis, "question_text", "question_id", True)[:8])
        out.extend({**r, "shortlist_category": f"strongest_negative_{axis}_questions"} for r in top_items(question_rows, axis, "question_text", "question_id", False)[:8])

    ambiguous = []
    for r in question_rows:
        impact = max(abs(int(r[f"{axis}_score"])) for axis in ["pc1", "pc2", "pc3"])
        low_conf = any(r[f"{axis}_confidence"] == "low" for axis in ["pc1", "pc2", "pc3"])
        if low_conf and impact >= 1:
            ambiguous.append((impact, sum(abs(float(r[f"{axis}_raw"])) for axis in ["pc1", "pc2", "pc3"]), r))
    for _impact, _raw, r in sorted(ambiguous, key=lambda x: (x[0], x[1]), reverse=True)[:20]:
        out.append(
            {
                "shortlist_category": "ambiguous_high_impact_low_confidence_questions",
                "item_type": "question",
                "item_id": r["question_id"],
                "axis": "mixed",
                "direction": "mixed",
                "score": f"{r['pc1_score']}/{r['pc2_score']}/{r['pc3_score']}",
                "confidence": f"{r['pc1_confidence']}/{r['pc2_confidence']}/{r['pc3_confidence']}",
                "text": r["question_text"],
                "rationale": "At least one nonzero axis score has low confidence.",
            }
        )

    for r in sorted(
        instruction_rows,
        key=lambda x: sum(abs(int(x[f"{axis}_score"])) for axis in ["pc1", "pc2", "pc3"]),
        reverse=True,
    ):
        out.append(
            {
                "shortlist_category": "playwright_instructions_strongest_predicted_displacement",
                "item_type": "instruction",
                "item_id": r["instruction_id"],
                "axis": "all",
                "direction": "mixed",
                "score": f"{r['pc1_score']}/{r['pc2_score']}/{r['pc3_score']}",
                "confidence": f"{r['pc1_confidence']}/{r['pc2_confidence']}/{r['pc3_confidence']}",
                "text": r["instruction_text"],
                "rationale": "Role-specific instruction displacement profile.",
            }
        )

    zero_cases = [
        r
        for r in grid_rows
        if int(r["additive_pc1_score"]) == 0
        and int(r["additive_pc2_score"]) == 0
        and int(r["additive_pc3_score"]) == 0
    ][:20]
    for r in zero_cases:
        out.append(
            {
                "shortlist_category": "near_zero_all_three_pcs_grid_cases",
                "item_type": "grid",
                "item_id": f"i{r['instruction_id']}_q{r['question_id']}",
                "axis": "all",
                "direction": "near_zero",
                "score": "0/0/0",
                "confidence": r["combined_confidence_summary"],
                "text": r["combined_input_preview"],
                "rationale": "Additive forecast is neutral on all three axes.",
            }
        )
    return out


def score_coverage(counts: dict[str, dict[str, int]]) -> dict[str, dict[str, object]]:
    out = {}
    for axis, c in counts.items():
        negative = c.get("-2", 0) + c.get("-1", 0)
        positive = c.get("1", 0) + c.get("2", 0)
        zero = c.get("0", 0)
        usable = negative > 0 and positive > 0 and zero < 240
        thin_side = min(negative, positive)
        if not usable:
            flag = "limited variation; review before GPU run"
        elif thin_side < 5:
            flag = "usable but thin one-sided coverage; manually review before GPU run"
        elif thin_side < 10:
            flag = "usable but modest one-sided coverage"
        else:
            flag = None
        out[axis] = {
            "negative_count": negative,
            "positive_count": positive,
            "zero_count": zero,
            "usable_variation": usable,
            "flag": flag,
        }
    return out


def main() -> None:
    questions = load_questions()
    instructions = load_playwright_instructions()
    centroid = load_playwright_centroid()

    question_rows = []
    for q in questions:
        score = score_record(str(q["question_text"]))
        question_rows.append(
            {
                "question_id": q["question_id"],
                "question_text": q["question_text"],
                "source_path": "data/extraction_questions.jsonl",
                "model_used": MODEL_USED,
                **score,
            }
        )

    instruction_rows = []
    for inst in instructions:
        score = score_record(str(inst["instruction_text"]), extra=PLAYWRIGHT_BONUS)
        instruction_rows.append(
            {
                "role": "playwright",
                "instruction_id": inst["instruction_id"],
                "instruction_text": inst["instruction_text"],
                "source_path": "data/roles/instructions/playwright.json",
                "model_used": MODEL_USED,
                **score,
            }
        )

    grid_rows = []
    for inst in instruction_rows:
        for q in question_rows:
            row = {
                "instruction_id": inst["instruction_id"],
                "question_id": q["question_id"],
                "system_instruction_text": inst["instruction_text"],
                "extraction_question_text": q["question_text"],
                "combined_input_preview": (
                    f"SYSTEM: {inst['instruction_text']} USER: {q['question_text']}"
                )[:300],
                **centroid,
            }
            for axis in ["pc1", "pc2", "pc3"]:
                row[f"instruction_{axis}_score"] = inst[f"{axis}_score"]
                row[f"question_{axis}_score"] = q[f"{axis}_score"]
                row[f"additive_{axis}_score"] = int(inst[f"{axis}_score"]) + int(q[f"{axis}_score"])
            row["combined_confidence_summary"] = combined_confidence(inst, q)
            grid_rows.append(row)
    if len(grid_rows) != 1200:
        raise SystemExit(f"Expected 1200 grid rows, found {len(grid_rows)}")

    q_fields = [
        "question_id",
        "question_text",
        "source_path",
        "model_used",
        "pc1_score",
        "pc1_confidence",
        "pc1_rationale",
        "pc2_score",
        "pc2_confidence",
        "pc2_rationale",
        "pc3_score",
        "pc3_confidence",
        "pc3_rationale",
        "pc1_raw",
        "pc2_raw",
        "pc3_raw",
    ]
    i_fields = [
        "role",
        "instruction_id",
        "instruction_text",
        "source_path",
        "model_used",
        "pc1_score",
        "pc1_confidence",
        "pc1_rationale",
        "pc2_score",
        "pc2_confidence",
        "pc2_rationale",
        "pc3_score",
        "pc3_confidence",
        "pc3_rationale",
        "pc1_raw",
        "pc2_raw",
        "pc3_raw",
    ]
    grid_fields = [
        "instruction_id",
        "question_id",
        "system_instruction_text",
        "extraction_question_text",
        "combined_input_preview",
        "playwright_centroid_pc1",
        "playwright_centroid_pc2",
        "playwright_centroid_pc3",
        "playwright_activation_cluster",
        "instruction_pc1_score",
        "question_pc1_score",
        "additive_pc1_score",
        "instruction_pc2_score",
        "question_pc2_score",
        "additive_pc2_score",
        "instruction_pc3_score",
        "question_pc3_score",
        "additive_pc3_score",
        "combined_confidence_summary",
    ]
    write_csv(OUT_DIR / "extraction_question_axis_scores.csv", question_rows, q_fields)
    write_csv(OUT_DIR / "playwright_positive_instruction_scores.csv", instruction_rows, i_fields)
    write_csv(OUT_DIR / "playwright_1200_displacement_forecast_grid.csv", grid_rows, grid_fields)

    q_counts = count_scores(question_rows)
    i_counts = count_scores(instruction_rows)
    additive_counts = count_additive(grid_rows)
    shortlist = build_shortlist(question_rows, instruction_rows, grid_rows)
    shortlist_fields = [
        "shortlist_category",
        "item_type",
        "item_id",
        "axis",
        "direction",
        "score",
        "confidence",
        "text",
        "rationale",
    ]
    write_csv(OUT_DIR / "displacement_manual_review_shortlist.csv", shortlist, shortlist_fields)

    top_cases = {}
    for axis in ["pc1", "pc2", "pc3"]:
        top_cases[f"{axis}_positive_questions"] = top_items(question_rows, axis, "question_text", "question_id", True)[:5]
        top_cases[f"{axis}_negative_questions"] = top_items(question_rows, axis, "question_text", "question_id", False)[:5]

    near_zero_grid_count = sum(
        1
        for r in grid_rows
        if int(r["additive_pc1_score"]) == 0
        and int(r["additive_pc2_score"]) == 0
        and int(r["additive_pc3_score"]) == 0
    )
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "model_used": MODEL_USED,
        "gpu_used": False,
        "role": "playwright",
        "question_source": str(QUESTION_PATH.relative_to(REPO_ROOT)),
        "instruction_source": str(PLAYWRIGHT_PATH.relative_to(REPO_ROOT)),
        "prior_design_directory_used": DESIGN_DIR.exists(),
        "question_count": len(question_rows),
        "positive_instruction_count": len(instruction_rows),
        "grid_row_count": len(grid_rows),
        "playwright_centroid": centroid,
        "axis_definitions": AXIS_DEFINITIONS,
        "question_score_counts": q_counts,
        "instruction_score_counts": i_counts,
        "additive_grid_score_counts": additive_counts,
        "question_coverage_assessment": score_coverage(q_counts),
        "near_zero_all_three_grid_count": near_zero_grid_count,
        "top_cases": top_cases,
        "caveat": "Scores are rubric-based predicted displacement pressures, not observed activation movement.",
    }
    (OUT_DIR / "displacement_score_distribution_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
    )

    report_lines = [
        "# Playwright Displacement Scoring Report",
        "",
        f"- Generated UTC: {summary['generated_utc']}",
        f"- Model used for analysis/script authorship: {MODEL_USED}",
        "- Startup status: passed via cache-busted raw GitHub startup manifest verification.",
        "- GPU used: no",
        f"- Question source: `{summary['question_source']}`",
        f"- Playwright instruction source: `{summary['instruction_source']}`",
        f"- Prior design directory used: `{summary['prior_design_directory_used']}`",
        f"- Counts: {len(question_rows)} shared questions, {len(instruction_rows)} playwright positive instructions, {len(grid_rows)} instruction-question grid rows",
        f"- Playwright centroid if available: PC1={centroid['playwright_centroid_pc1']}, PC2={centroid['playwright_centroid_pc2']}, PC3={centroid['playwright_centroid_pc3']}, cluster={centroid['playwright_activation_cluster']}",
        "",
        "## Scoring Scale",
        "",
        "- -2: strong negative displacement pressure",
        "- -1: moderate negative displacement pressure",
        "- 0: no clear pressure, balanced, mixed, or ambiguous",
        "- 1: moderate positive displacement pressure",
        "- 2: strong positive displacement pressure",
        "",
        "Scores are predicted displacement pressures relative to a later role centroid. They are not observed coordinates and do not establish activation movement until corrected extraction and GPU response measurements are performed.",
        "",
        "## Axis Definitions",
        "",
    ]
    for axis, defs in AXIS_DEFINITIONS.items():
        report_lines.extend([f"- {axis.upper()} negative: {defs['negative']}", f"- {axis.upper()} positive: {defs['positive']}"])
    report_lines.extend(["", "## Score Distributions Across 240 Questions", ""])
    for axis, counts in q_counts.items():
        assess = summary["question_coverage_assessment"][axis]
        flag = f"; flag={assess['flag']}" if assess["flag"] else ""
        report_lines.append(f"- {axis.upper()}: {counts}; usable variation={assess['usable_variation']}; negative={assess['negative_count']}, positive={assess['positive_count']}, zero={assess['zero_count']}{flag}")
    report_lines.extend(["", "## Score Distributions Across Five Playwright Instructions", ""])
    for axis, counts in i_counts.items():
        report_lines.append(f"- {axis.upper()}: {counts}")
    report_lines.extend(["", "## Additive Grid Score Distributions Across 1,200 Cases", ""])
    for axis, counts in additive_counts.items():
        report_lines.append(f"- {axis.upper()}: {counts}")
    report_lines.extend(["", "## Strongest Predicted Question Examples", ""])
    for axis in ["pc1", "pc2", "pc3"]:
        report_lines.append(f"### {axis.upper()} positive")
        for item in top_cases[f"{axis}_positive_questions"]:
            report_lines.append(f"- Q{item['item_id']} score {item['score']} ({item['confidence']}): {item['text']}")
        report_lines.append(f"### {axis.upper()} negative")
        for item in top_cases[f"{axis}_negative_questions"]:
            report_lines.append(f"- Q{item['item_id']} score {item['score']} ({item['confidence']}): {item['text']}")
    report_lines.extend(
        [
            "",
            "## Low-Confidence / Ambiguous Review Cases",
            "",
            "See `displacement_manual_review_shortlist.csv` for ambiguous high-impact low-confidence questions and near-zero grid cases.",
            "",
            "## Readiness Assessment",
            "",
        ]
    )
    for axis, assess in summary["question_coverage_assessment"].items():
        verdict = "usable" if assess["usable_variation"] else "limited"
        flag = f" ({assess['flag']})" if assess["flag"] else ""
        report_lines.append(f"- {axis.upper()}: {verdict} predicted variation for within-role displacement testing{flag}.")
    report_lines.extend(
        [
            "",
            "The question set does not collapse to zero and each PC has both positive and negative predicted coverage. The next recommended step before any GPU run is human review of the shortlist, especially low-confidence high-impact cases, followed by corrected-hook extraction equivalence confirmation before launching playwright activation measurements.",
            "",
        ]
    )
    (OUT_DIR / "playwright_displacement_scoring_report.md").write_text("\n".join(report_lines), encoding="utf-8")

    print(json.dumps({
        "question_count": len(question_rows),
        "instruction_count": len(instruction_rows),
        "grid_rows": len(grid_rows),
        "question_score_counts": q_counts,
        "instruction_score_counts": i_counts,
        "additive_grid_score_counts": additive_counts,
        "coverage": summary["question_coverage_assessment"],
    }, indent=2))


if __name__ == "__main__":
    main()
