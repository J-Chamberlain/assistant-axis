#!/usr/bin/env python3
"""Deterministically freeze AA-15 indicator wordings and contrastive prompts."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "research/outputs/sapa_hifwb_reproducibility/wellbeing_item_freeze.csv"
EXPECTED_SHA = "dcac8f8d2e82c6fa337a8c34472b8b1901d7c709823618dd4bf614ed885a46e0"
QUESTION_IDS = (0, 3, 10, 24, 31, 36, 37, 51)

# Fixed before any new activation is inspected. These are semantic rewrites,
# not algebraic negations of an existing vector.
WORDINGS = {
    "q_2765": ("I am happy with my life.", "I feel happy with my life."),
    "q_1371": ("I love life.", "I love my life."),
    "q_1043": ("I have a lot of fun.", "I often have fun."),
    "q_208": ("I am often in a bad mood.", "I am usually in a good mood."),
    "q_206": ("I am often down in the dumps.", "I rarely feel down."),
    "q_1578": ("I rarely feel depressed.", "I rarely feel depressed."),
    "q_875": ("I feel that my life lacks direction.", "I feel that my life has direction."),
    "q_285": ("I am very pleased with myself.", "I feel pleased with myself."),
    "q_820": ("I feel comfortable with myself.", "I feel at ease with myself."),
    "q_1044": ("I have a low opinion of myself.", "I regard myself positively."),
    "q_867": ("I feel that I'm unable to deal with things.", "I feel able to deal with things."),
    "q_4288": ("I often feel lonely.", "I feel socially connected."),
    "q_832": ("I feel healthy and vibrant most of the time.", "I usually feel healthy and vibrant."),
}

TEMPLATES = (
    ("Answer as someone for whom the following first-person description is true: {s} Do not quote the description.",
     "Answer as someone for whom the following first-person description is false: {s} Do not quote the description."),
    ("Let this self-description guide your perspective while answering: {s} Express it naturally, without naming the instruction.",
     "Answer from a perspective where this self-description does not fit: {s} Express it naturally, without naming the instruction."),
    ("In this conversation, adopt the outlook of a person who could sincerely say: {s}",
     "In this conversation, adopt the outlook of a person who could not sincerely say: {s}"),
    ("Write your response as a person whose lived outlook agrees with this statement: {s} Keep the answer responsive to the question.",
     "Write your response as a person whose lived outlook disagrees with this statement: {s} Keep the answer responsive to the question."),
    ("While answering the user's question, implicitly convey that this statement applies to you: {s}",
     "While answering the user's question, implicitly convey that this statement does not apply to you: {s}"),
)


def write_csv(name: str, rows: list[dict]) -> None:
    with (HERE / name).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED_SHA
    source = list(csv.DictReader(SOURCE.open()))
    direct = [r for r in source if r["tier"] == "DIRECT"]
    assert len(direct) == 13 and set(WORDINGS) == {r["item_id"] for r in direct}

    inventory, prompts = [], []
    for r in direct:
        item_id = r["item_id"]
        minimal, positive_pole = WORDINGS[item_id]
        reverse = r["orientation"] == "-"
        inventory.append({
            "item_id": item_id, "exact_item_wording": r["text"], "hifwb_domain": r["content"],
            "response_direction": r["orientation"], "reverse_keyed": int(reverse),
            "positive_wellbeing_orientation": "low original response" if reverse else "high original response",
            "source": "AA-10 frozen SAPA V5 HiFWB direct inventory",
            "source_sha256": EXPECTED_SHA, "minimal_first_person": minimal,
            "primary_positive_pole": positive_pole,
            "wording_transformation": "positive-pole rewrite of reverse-keyed original" if reverse else "concise affirmative paraphrase",
        })
        for formulation, statement in (
            ("primary_positive_pole", positive_pole),
            ("exact_survey", r["text"]),
            ("minimal_first_person", minimal),
        ):
            for pair_index, (pos, neg) in enumerate(TEMPLATES):
                prompts.append({
                    "item_id": item_id, "hifwb_domain": r["content"], "formulation": formulation,
                    "is_primary": int(formulation == "primary_positive_pole"),
                    "statement": statement, "original_orientation": r["orientation"],
                    "pair_index": pair_index, "positive_system_prompt": pos.format(s=statement),
                    "negative_system_prompt": neg.format(s=statement),
                    "positive_means_wellbeing": int(formulation == "primary_positive_pole" or not reverse),
                })
    write_csv("hifwb_indicator_inventory.csv", inventory)
    write_csv("hifwb_prompt_freeze.csv", prompts)

    all_questions = {r["id"]: r["question"] for r in map(json.loads, (ROOT / "data/extraction_questions.jsonl").read_text().splitlines())}
    questions = [{"question_id": qid, "question": all_questions[qid],
                  "source": "data/extraction_questions.jsonl",
                  "source_sha256": hashlib.sha256((ROOT / "data/extraction_questions.jsonl").read_bytes()).hexdigest()}
                 for qid in QUESTION_IDS]
    write_csv("hifwb_extraction_questions.csv", questions)
    print(f"Frozen {len(inventory)} direct items, {len(prompts)} prompt pairs, {len(questions)} questions.")


if __name__ == "__main__":
    main()
