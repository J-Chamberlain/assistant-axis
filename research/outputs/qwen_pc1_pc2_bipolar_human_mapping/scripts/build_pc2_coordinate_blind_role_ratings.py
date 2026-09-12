#!/usr/bin/env python3
"""Build frozen coordinate-blind role ratings from names and instructions only."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_INPUT_COLUMNS = ["role"] + [f"positive_instruction_{i}" for i in range(1, 6)]
FORBIDDEN_OUTPUT_FRAGMENTS = (
    "pc", "rank", "percentile", "cluster", "correlation", "specificity", "purity"
)

# Phrase families are frozen before any geometry join. Frequencies are capped so
# repeated role-template wording cannot dominate a score.
DIMENSIONS = {
    "embodied_physical_engagement": {
        "patterns": {
            "bodily_action": r"\b(bodil(?:y|ies)|physical action|physical activity|physical participation|movement|move through|active physical)\b",
            "manual_skill": r"\b(hands[- ]on|with (?:your|their) hands|manual skill|handcrafted|craftsmanship|tools? and technique|repairing|fixing and maintaining)\b",
            "sensory_contact": r"\b(sensory|sensation|touch|taste|sound|smell|reading waves|in the water|ocean(?:'s)? rhythms)\b",
            "sport_thrill": r"\b(sport|athletic|physical training|adrenaline|stunts?|extreme adventure)\b",
            "combat": r"\b(combat|battle|fight|warfare|military warrior|weapons?|tactical)\b",
            "field_survival": r"\b(fieldwork|field activity|wild(?:erness)?|hunting|gathering|survival skills|shelter and fire|pathfinding|reconnaissance)\b",
            "physical_care": r"\b(emergency medical|life[- ]saving care|patient stabilization|clinical procedures|animal care|veterinary)\b",
            "material_making": r"\b(materials, tools|physical structures|cooking techniques|restaurant kitchens|culinary|craft(?:ed|ing)|construction)\b",
            "vehicle_operation": r"\b(navigating aircraft|flight operations|cockpit|driving|piloting|operating machinery)\b",
        },
        "cutoffs": (0.0, 1.2, 2.8, 5.0),
    },
    "practical_concrete_engagement": {
        "patterns": {
            "practical": r"\b(practical|pragmatic|real[- ]world|what actually works|proven methods)\b",
            "implementation": r"\b(implement(?:ation|ing|s|ed)?|actionable|turning .* into|apply|application|execution)\b",
            "operations": r"\b(operations?|operational|logistics|dispatch|workflow|production|maintenance)\b",
            "repair_build": r"\b(repair|fix(?:ing|es|ed)?|build(?:er|ing|s)?|construct(?:ion|ing|s)?|craft(?:ing|ed)?|make something)\b",
            "direct_problem_solving": r"\b(problem[- ]solving|solve problems|troubleshooting|diagnos(?:e|ing)|immediate practical solutions|direct methods)\b",
            "procedural_action": r"\b(procedures?|protocols?|step[- ]by[- ]step|action steps|care plans?|emergency response)\b",
            "observable_outcome": r"\b(measurable outcomes?|results?|deliverables?|patient stabilization|durable|functional|effective solutions?)\b",
            "decision_action": r"\b(decision[- ]making|taking action|responds? to|coordinates? .* care|negotiat(?:e|ion)|organizing)\b",
        },
        "cutoffs": (0.0, 1.5, 3.5, 6.0),
    },
    "social_outward_engagement": {
        "patterns": {
            "interpersonal": r"\b(interpersonal|relationships?|social interaction|connect with (?:people|others)|rapport)\b",
            "groups": r"\b(community|communities|teams?|groups?|audience|public|crowd|network)\b",
            "care_guidance": r"\b(helping people|helps? others|guides? others|supportive guidance|patient care|caregiver|counsel(?:or|ing))\b",
            "teaching": r"\b(students?|learners?|teach(?:er|ing)?|instruction|mentor(?:ing)?|coach(?:ing)?)\b",
            "persuasion": r"\b(persuad(?:e|ing)|influenc(?:e|ing)|advocacy|mobiliz(?:e|ing)|negotiat(?:e|ion)|diploma(?:cy|tic))\b",
            "coordination": r"\b(collaborat(?:e|ion|ive)|coordinat(?:e|ion)|facilitat(?:e|ion)|mediate|parties|stakeholders)\b",
            "performance_media": r"\b(perform(?:ance|er|ing)|entertain|broadcast|podcast|presenter|journalist|reporter|interview)\b",
            "conversation": r"\b(conversation|communicat(?:e|ion)|discussion|feedback|listening to others)\b",
        },
        "cutoffs": (0.0, 1.5, 3.5, 6.0),
    },
    "abstract_conceptual_engagement": {
        "patterns": {
            "theory": r"\b(theor(?:y|ies|etical|ist)|abstract models?|conceptual structures?|frameworks?)\b",
            "principles": r"\b(underlying principles?|fundamental laws?|first principles?|assumptions|foundations?)\b",
            "philosophy": r"\b(philosoph(?:y|ical|er)|existence|nature of knowledge|meaning of life|consciousness)\b",
            "symbolic": r"\b(symbols?|symbolic|metaphor|narrative|myth|archetyp|interpret(?:ation|ing)?)\b",
            "scholarship": r"\b(scholar(?:ship|ly)?|academic|historical analysis|research|systematic study|erudition)\b",
            "synthesis": r"\b(synthesi[sz]|integrat(?:e|ing) disparate|unified theor|hidden patterns|connections across)\b",
            "models_systems": r"\b(mathematical models?|worldview|systems thinking|complex systems?|concepts?|ideas?)\b",
            "reflection": r"\b(contemplat(?:e|es|ing|ion|ive)|reflect(?:s|ion|ing)?|meditat(?:e|es|ing|ion|ive)|introspection|profound thought)\b",
        },
        "cutoffs": (0.0, 1.5, 3.5, 6.0),
    },
    "ritual_formal_mediation": {
        "patterns": {
            "ritual_ceremony": r"\b(ritual|ceremon(?:y|ial)|sacred|religious rites?|liturgy|reverence)\b",
            "tradition": r"\b(traditional|tradition|ancient teachings|preserving traditional|customs?|heritage)\b",
            "rules_standards": r"\b(rules?|standards?|requirements?|regulations?|compliance|rubrics?)\b",
            "protocol_procedure": r"\b(protocols?|procedures?|formal process|methodical|systematic process|chain of command)\b",
            "institutional": r"\b(legal|court|audit|academic evaluation|peer review|professional ethics|official)\b",
            "contemplative": r"\b(contemplat(?:e|es|ing|ion|ive)|meditat(?:e|es|ing|ion|ive)|spiritual practices?|devoted|solemn|ascetic)\b",
            "symbolic_mediation": r"\b(symbols?|scripture|esoteric wisdom|metaphysical|divine|oracle|prophecy)\b",
            "discipline_duty": r"\b(discipline|duty|obligation|precision|accuracy|careful planning|loyalty to mission)\b",
        },
        "cutoffs": (0.0, 1.5, 3.5, 6.0),
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("_", " ")).strip()


def rate(text: str, spec: dict) -> tuple[int, list[str], float]:
    evidence = []
    raw = 0.0
    for label, pattern in spec["patterns"].items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            count = min(len(matches), 2)
            raw += 1.0 + 0.5 * (count - 1)
            evidence.append(label)
    # Role prompts vary modestly in length. Normalize to a 1,000-character basis.
    normalized = raw * 1000.0 / max(len(text), 500)
    c1, c2, c3, c4 = spec["cutoffs"]
    score = 1 + int(normalized > c1) + int(normalized >= c2) + int(normalized >= c3) + int(normalized >= c4)
    return min(score, 5), evidence, normalized


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--rubric", required=True, type=Path)
    parser.add_argument("--freeze-commit", default="")
    args = parser.parse_args()

    with args.input.open(newline="", encoding="utf-8") as fh:
        source_rows = list(csv.DictReader(fh))
    if len(source_rows) != 275:
        raise ValueError(f"Expected 275 roles, found {len(source_rows)}")
    if any(c not in source_rows[0] for c in ALLOWED_INPUT_COLUMNS):
        raise ValueError("Missing required role/instruction field")

    blind_rows = [{c: row[c] for c in ALLOWED_INPUT_COLUMNS} for row in source_rows]
    output_rows = []
    for row in blind_rows:
        instruction_text = " ".join(row[f"positive_instruction_{i}"] for i in range(1, 6))
        joined = normalize(row["role"] + " " + instruction_text)
        out = {
            "role": row["role"],
            "positive_instruction_1": row["positive_instruction_1"],
            "positive_instruction_2": row["positive_instruction_2"],
            "positive_instruction_3": row["positive_instruction_3"],
            "positive_instruction_4": row["positive_instruction_4"],
            "positive_instruction_5": row["positive_instruction_5"],
            "rating_method": "FROZEN_COORDINATE_BLIND_RUBRIC_CODING",
            "rater_model": "GPT-5.5",
        }
        for dim, spec in DIMENSIONS.items():
            score, evidence, normalized = rate(joined, spec)
            out[dim] = score
            out[f"{dim}_evidence"] = ";".join(evidence) if evidence else "none"
            out[f"{dim}_lexical_intensity"] = round(normalized, 6)
        output_rows.append(out)

    fieldnames = list(output_rows[0])
    for field in fieldnames:
        lowered = field.lower()
        if any(fragment in lowered for fragment in FORBIDDEN_OUTPUT_FRAGMENTS):
            raise ValueError(f"Forbidden geometry-related output field: {field}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    script_path = Path(__file__).resolve()
    manifest = {
        "analysis": "AA-8 PC2 coordinate-blind role-dimension rating freeze",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "role_count": len(output_rows),
        "model_used": "GPT-5.5",
        "rating_method": "deterministic coordinate-blind rubric coding over role name and five positive instructions",
        "allowed_source_fields": ALLOWED_INPUT_COLUMNS,
        "forbidden_information": [
            "PC coordinates", "PC ranks", "PC percentiles", "clusters", "prior PC interpretations",
            "trait correlations", "specificity outcomes",
        ],
        "geometry_join_performed": False,
        "freeze_commit": args.freeze_commit,
        "source_sha256": sha256(args.input),
        "rubric_sha256": sha256(args.rubric),
        "builder_sha256": sha256(script_path),
        "ratings_sha256": sha256(args.output),
        "ordinal_scale": [1, 2, 3, 4, 5],
        "dimension_names": list(DIMENSIONS),
    }
    with args.manifest.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")


if __name__ == "__main__":
    main()
