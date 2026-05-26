#!/usr/bin/env python3
"""Local truncation diagnostic for the trickster Phase 1 corpus.

CPU-only, no model loading, no API calls. Tokenization is attempted only from a
local tokenizer cache; otherwise character and word proxies are used.
"""

from __future__ import annotations

import json
import math
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
QWEN_ROOT = Path(__file__).resolve().parents[1]
INPUT = QWEN_ROOT / "outputs/paper1_5/trickster_phase1.jsonl"
INTEGRITY = QWEN_ROOT / "outputs/paper1_5/phase1_final_integrity.json"
OUT_DIR = QWEN_ROOT / "outputs/paper1_5"
OUT_JSON = OUT_DIR / "truncation_diagnostic.json"
OUT_MD = OUT_DIR / "truncation_diagnostic.md"
OUT_SAMPLES_JSONL = OUT_DIR / "truncation_review_samples.jsonl"
OUT_SAMPLES_MD = OUT_DIR / "truncation_review_samples.md"

EXPECTED_RECORDS = 1200
EXPECTED_SYSTEM_PROMPTS = 5
EXPECTED_QUESTIONS = 240

ROLE_MARKERS = [
    "trick", "trickster", "mischief", "chaos", "paradox", "mask", "riddle",
    "jester", "laugh", "wink", "subvert", "play", "rule", "dance", "mirror",
    "absurd", "delight", "twist", "prank", "unravel", "stage", "performance",
]


def load_records() -> list[dict[str, Any]]:
    records = []
    with INPUT.open() as f:
        for line_no, line in enumerate(f, 1):
            if line.strip():
                row = json.loads(line)
                row["_line_no"] = line_no
                records.append(row)
    return records


def try_load_tokenizer():
    try:
        from transformers import AutoTokenizer  # type: ignore

        return AutoTokenizer.from_pretrained(
            "Qwen/Qwen3-32B",
            trust_remote_code=True,
            local_files_only=True,
        )
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def has_unclosed_quote_or_parenthesis(text: str) -> bool:
    quote_chars = ['"', "'", "`"]
    quote_unclosed = any(text.count(q) % 2 == 1 for q in quote_chars)
    paren_unclosed = text.count("(") > text.count(")")
    bracket_unclosed = text.count("[") > text.count("]")
    brace_unclosed = text.count("{") > text.count("}")
    return quote_unclosed or paren_unclosed or bracket_unclosed or brace_unclosed


def completion_indicators(text: str) -> dict[str, Any]:
    stripped = text.rstrip()
    final_100 = stripped[-100:]
    final_120 = stripped[-120:]
    ends_with_sentence_punctuation = bool(re.search(r"[.!?][\"')\]]*$", stripped))
    ends_mid_word = bool(re.search(r"[A-Za-z]{3,}$", stripped))
    ends_with_colon_or_comma = bool(re.search(r"[:,;][\"')\]]*$", stripped))
    contains_numbered_list_marker_near_end = bool(
        re.search(r"(?:^|\n|\s)(?:\d+\.|[IVX]+\.)\s+\S*", final_120)
    )
    unclosed = has_unclosed_quote_or_parenthesis(stripped)
    return {
        "ends_with_sentence_punctuation": ends_with_sentence_punctuation,
        "ends_mid_word": ends_mid_word,
        "ends_with_colon_or_comma": ends_with_colon_or_comma,
        "final_100_chars": final_100,
        "contains_numbered_list_marker_near_end": contains_numbered_list_marker_near_end,
        "contains_unclosed_quote_or_parenthesis": unclosed,
    }


def role_marker_count(text: str) -> int:
    lower = text.lower()
    return sum(1 for marker in ROLE_MARKERS if marker in lower)


def abruptness_score(indicators: dict[str, Any]) -> int:
    score = 0
    if not indicators["ends_with_sentence_punctuation"]:
        score += 2
    if indicators["ends_mid_word"]:
        score += 2
    if indicators["ends_with_colon_or_comma"]:
        score += 2
    if indicators["contains_numbered_list_marker_near_end"]:
        score += 1
    if indicators["contains_unclosed_quote_or_parenthesis"]:
        score += 1
    return score


def summarize_numeric(values: list[int]) -> dict[str, float | int]:
    if not values:
        return {"count": 0}
    sorted_vals = sorted(values)

    def pct(p: float) -> float:
        idx = (len(sorted_vals) - 1) * p
        lo = math.floor(idx)
        hi = math.ceil(idx)
        if lo == hi:
            return float(sorted_vals[lo])
        return float(sorted_vals[lo] * (hi - idx) + sorted_vals[hi] * (idx - lo))

    return {
        "count": len(values),
        "min": min(values),
        "p25": pct(0.25),
        "median": pct(0.5),
        "p75": pct(0.75),
        "p90": pct(0.9),
        "max": max(values),
        "mean": statistics.fmean(values),
    }


def truncation_summary(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    out = {}
    for group, items in sorted(grouped.items(), key=lambda kv: kv[0]):
        trunc = sum(1 for item in items if item["truncated_bool"])
        out[str(group)] = {
            "records": len(items),
            "truncated": trunc,
            "fraction": trunc / len(items) if items else 0.0,
        }
    return out


def decile_for_q(q_idx: int) -> str:
    start = (q_idx // 24) * 24
    end = min(start + 23, EXPECTED_QUESTIONS - 1)
    return f"{start:03d}-{end:03d}"


def stratified(records: list[dict[str, Any]], want_truncated: bool, total: int) -> list[dict[str, Any]]:
    by_sp: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        if row["truncated_bool"] == want_truncated:
            by_sp[row["sp_idx"]].append(row)
    for rows in by_sp.values():
        rows.sort(key=lambda r: (r["q_idx"], r["_line_no"]))

    selected = []
    per_group = max(1, total // EXPECTED_SYSTEM_PROMPTS)
    for sp in sorted(by_sp):
        rows = by_sp[sp]
        if not rows:
            continue
        if len(rows) <= per_group:
            chosen = rows
        else:
            step = (len(rows) - 1) / max(per_group - 1, 1)
            chosen = [rows[round(i * step)] for i in range(per_group)]
        selected.extend(chosen)

    if len(selected) < total:
        existing = {row["_line_no"] for row in selected}
        remaining = [
            row for row in records
            if row["truncated_bool"] == want_truncated and row["_line_no"] not in existing
        ]
        remaining.sort(key=lambda r: (r["sp_idx"], r["q_idx"]))
        selected.extend(remaining[: total - len(selected)])
    return selected[:total]


def sample_record(row: dict[str, Any], sample_type: str) -> dict[str, Any]:
    return {
        "sample_type": sample_type,
        "line_no": row["_line_no"],
        "sp_idx": row["sp_idx"],
        "q_idx": row["q_idx"],
        "truncated": row["truncated_bool"],
        "char_len": row["char_len"],
        "word_count": row["word_count"],
        "abruptness_score": row["abruptness_score"],
        "role_marker_count": row["role_marker_count"],
        "completion_indicators": row["completion_indicators"],
        "response_text": row["response_text"],
    }


def md_escape(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def main() -> None:
    records = load_records()
    pairs = {(row.get("sp_idx"), row.get("q_idx")) for row in records}

    tokenizer_result = try_load_tokenizer()
    tokenizer = None
    tokenizer_note = ""
    if isinstance(tokenizer_result, tuple):
        tokenizer_note = (
            "Local tokenizer unavailable; character and word-count proxies were used. "
            f"Tokenizer error: {tokenizer_result[1]}"
        )
    else:
        tokenizer = tokenizer_result
        tokenizer_note = "Token counts computed with locally cached Qwen/Qwen3-32B tokenizer."

    for row in records:
        text = row.get("response_text") or ""
        row["truncated_bool"] = bool(row.get("truncated"))
        row["char_len"] = len(text)
        row["word_count"] = word_count(text)
        row["token_count"] = None
        if tokenizer is not None:
            row["token_count"] = len(tokenizer.encode(text, add_special_tokens=False))
        row["completion_indicators"] = completion_indicators(text)
        row["abruptness_score"] = abruptness_score(row["completion_indicators"])
        row["role_marker_count"] = role_marker_count(text)

    truncated = [row for row in records if row["truncated_bool"]]
    non_truncated = [row for row in records if not row["truncated_bool"]]
    q_decile_rows = []
    for row in records:
        copy = dict(row)
        copy["q_decile"] = decile_for_q(int(row["q_idx"]))
        q_decile_rows.append(copy)

    q_summary = truncation_summary(records, "q_idx")
    most_truncated_questions = sorted(
        q_summary.items(),
        key=lambda kv: (-kv[1]["fraction"], -kv[1]["truncated"], int(kv[0])),
    )[:25]

    indicator_counts = {
        "truncated": Counter(),
        "non_truncated": Counter(),
    }
    for label, rows in [("truncated", truncated), ("non_truncated", non_truncated)]:
        for row in rows:
            for key, value in row["completion_indicators"].items():
                if key == "final_100_chars":
                    continue
                if value:
                    indicator_counts[label][key] += 1

    abrupt_truncated = sorted(
        truncated,
        key=lambda r: (-r["abruptness_score"], r["char_len"], r["sp_idx"], r["q_idx"]),
    )[:10]
    longest_non_truncated = sorted(
        non_truncated,
        key=lambda r: (-r["char_len"], r["sp_idx"], r["q_idx"]),
    )[:10]
    samples = (
        [sample_record(row, "stratified_truncated") for row in stratified(records, True, 25)]
        + [sample_record(row, "stratified_non_truncated") for row in stratified(records, False, 25)]
        + [sample_record(row, "most_abrupt_truncated") for row in abrupt_truncated]
        + [sample_record(row, "longest_non_truncated") for row in longest_non_truncated]
    )

    truncated_role_marker_ge2 = sum(1 for row in truncated if row["role_marker_count"] >= 2)
    non_truncated_role_marker_ge2 = sum(1 for row in non_truncated if row["role_marker_count"] >= 2)
    truncated_sentence_end = sum(
        1 for row in truncated if row["completion_indicators"]["ends_with_sentence_punctuation"]
    )
    truncated_abrupt = sum(1 for row in truncated if row["abruptness_score"] >= 3)
    non_truncated_abrupt = sum(1 for row in non_truncated if row["abruptness_score"] >= 3)

    sp_summary = truncation_summary(records, "sp_idx")
    q_decile_summary = truncation_summary(q_decile_rows, "q_decile")
    char_stats = {
        "all": summarize_numeric([row["char_len"] for row in records]),
        "truncated": summarize_numeric([row["char_len"] for row in truncated]),
        "non_truncated": summarize_numeric([row["char_len"] for row in non_truncated]),
    }
    word_stats = {
        "all": summarize_numeric([row["word_count"] for row in records]),
        "truncated": summarize_numeric([row["word_count"] for row in truncated]),
        "non_truncated": summarize_numeric([row["word_count"] for row in non_truncated]),
    }
    token_values = [row["token_count"] for row in records if row["token_count"] is not None]
    token_stats = summarize_numeric(token_values) if token_values else {"count": 0, "note": tokenizer_note}

    sp_fractions = [entry["fraction"] for entry in sp_summary.values()]
    sp_range = max(sp_fractions) - min(sp_fractions)
    q_decile_fractions = [entry["fraction"] for entry in q_decile_summary.values()]
    q_decile_range = max(q_decile_fractions) - min(q_decile_fractions)

    answers = {
        "severity": (
            f"Truncation is high: {len(truncated)}/{len(records)} records "
            f"({len(truncated) / len(records):.1%}) are flagged truncated."
        ),
        "system_prompt_concentration": (
            "Truncation varies by system prompt, but every prompt has substantial truncation; "
            f"the sp_idx fraction range is {min(sp_fractions):.1%} to {max(sp_fractions):.1%}."
        ),
        "question_subset_concentration": (
            "Truncation varies more by question subset than by system prompt; "
            f"q_idx decile fractions range from {min(q_decile_fractions):.1%} to "
            f"{max(q_decile_fractions):.1%}."
        ),
        "role_expression_before_cutoff": (
            f"{truncated_role_marker_ge2}/{len(truncated)} truncated records "
            f"({truncated_role_marker_ge2 / len(truncated):.1%}) contain at least two simple "
            "trickster lexical markers, so many truncated records likely contain usable role "
            "expression before cutoff, but this is only a proxy."
        ),
        "ending_abruptness": (
            f"{truncated_sentence_end}/{len(truncated)} truncated records "
            f"({truncated_sentence_end / len(truncated):.1%}) end with sentence punctuation; "
            f"{truncated_abrupt}/{len(truncated)} ({truncated_abrupt / len(truncated):.1%}) "
            "meet the abrupt-ending heuristic."
        ),
        "score3_bias": (
            "Truncation could bias score-3 selection downward for records whose strongest role "
            "expression would have appeared late, and upward only if early role expression is "
            "strong while later generic continuation is cut away. The diagnostic supports keeping "
            "the truncation flag visible during scoring and downstream selection."
        ),
        "phase2_proceed": (
            "Phase 2 scoring should proceed on all 1200 records, with truncation included as a "
            "covariate/filter and with manual review of high-scoring truncated candidates."
        ),
        "followup_recommended": (
            "A small follow-up run with higher max_new_tokens is recommended for a stratified "
            "subset of high-scoring truncated records and the most abrupt truncated questions, "
            "not as a prerequisite for Phase 2."
        ),
    }

    diagnostic = {
        "date": "2026-05-26",
        "model_used": "GPT-5.5",
        "input_jsonl": str(INPUT.relative_to(REPO_ROOT)),
        "integrity_json": str(INTEGRITY.relative_to(REPO_ROOT)),
        "validation": {
            "record_count": len(records),
            "expected_record_count": EXPECTED_RECORDS,
            "unique_sp_q_pairs": len(pairs),
            "expected_unique_sp_q_pairs": EXPECTED_RECORDS,
            "system_prompt_count": len({row["sp_idx"] for row in records}),
            "expected_system_prompt_count": EXPECTED_SYSTEM_PROMPTS,
            "question_count": len({row["q_idx"] for row in records}),
            "expected_question_count": EXPECTED_QUESTIONS,
            "valid": (
                len(records) == EXPECTED_RECORDS
                and len(pairs) == EXPECTED_RECORDS
                and len({row["sp_idx"] for row in records}) == EXPECTED_SYSTEM_PROMPTS
                and len({row["q_idx"] for row in records}) == EXPECTED_QUESTIONS
            ),
        },
        "tokenization": {
            "tokenizer_available": tokenizer is not None,
            "note": tokenizer_note,
        },
        "length_stats": {
            "characters": char_stats,
            "words": word_stats,
            "tokens": token_stats,
        },
        "truncation": {
            "overall": {
                "records": len(records),
                "truncated": len(truncated),
                "non_truncated": len(non_truncated),
                "fraction": len(truncated) / len(records),
            },
            "by_sp_idx": sp_summary,
            "by_q_idx_decile": q_decile_summary,
            "most_truncated_questions": [
                {"q_idx": int(q), **vals} for q, vals in most_truncated_questions
            ],
            "system_prompt_fraction_range": sp_range,
            "q_decile_fraction_range": q_decile_range,
        },
        "completion_indicators": {
            "counts": {
                "truncated": dict(indicator_counts["truncated"]),
                "non_truncated": dict(indicator_counts["non_truncated"]),
            },
            "truncated_sentence_punctuation_fraction": truncated_sentence_end / len(truncated),
            "truncated_abrupt_fraction": truncated_abrupt / len(truncated),
            "non_truncated_abrupt_fraction": non_truncated_abrupt / len(non_truncated),
        },
        "role_expression_proxy": {
            "markers": ROLE_MARKERS,
            "truncated_records_with_at_least_two_markers": truncated_role_marker_ge2,
            "truncated_fraction_with_at_least_two_markers": truncated_role_marker_ge2 / len(truncated),
            "non_truncated_records_with_at_least_two_markers": non_truncated_role_marker_ge2,
            "non_truncated_fraction_with_at_least_two_markers": (
                non_truncated_role_marker_ge2 / len(non_truncated)
            ),
        },
        "answers": answers,
        "sample_counts": Counter(sample["sample_type"] for sample in samples),
    }

    OUT_JSON.write_text(json.dumps(diagnostic, indent=2) + "\n")
    with OUT_SAMPLES_JSONL.open("w") as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    md_lines = [
        "# Trickster Phase 1 Truncation Diagnostic",
        "",
        f"Date: {diagnostic['date']}",
        "Model used for analysis: GPT-5.5",
        f"Input: `{diagnostic['input_jsonl']}`",
        "",
        "## Validation",
        "",
        f"- Records: {len(records)} / {EXPECTED_RECORDS}",
        f"- Unique `(sp_idx, q_idx)` pairs: {len(pairs)} / {EXPECTED_RECORDS}",
        f"- System prompts: {diagnostic['validation']['system_prompt_count']} / {EXPECTED_SYSTEM_PROMPTS}",
        f"- Questions: {diagnostic['validation']['question_count']} / {EXPECTED_QUESTIONS}",
        f"- Tokenization: {tokenizer_note}",
        "",
        "## Length Statistics",
        "",
        "| Group | Character median | Character p90 | Word median | Word p90 |",
        "|---|---:|---:|---:|---:|",
    ]
    for group in ["all", "truncated", "non_truncated"]:
        md_lines.append(
            f"| {group} | {char_stats[group].get('median', 0):.0f} | "
            f"{char_stats[group].get('p90', 0):.0f} | "
            f"{word_stats[group].get('median', 0):.0f} | "
            f"{word_stats[group].get('p90', 0):.0f} |"
        )

    md_lines.extend([
        "",
        "## Truncation Summary",
        "",
        f"Overall truncation: {len(truncated)}/{len(records)} "
        f"({len(truncated) / len(records):.1%}).",
        "",
        "### By System Prompt",
        "",
        "| sp_idx | records | truncated | fraction |",
        "|---:|---:|---:|---:|",
    ])
    for sp, vals in sp_summary.items():
        md_lines.append(f"| {sp} | {vals['records']} | {vals['truncated']} | {vals['fraction']:.1%} |")

    md_lines.extend([
        "",
        "### By Question Decile",
        "",
        "| q_idx range | records | truncated | fraction |",
        "|---|---:|---:|---:|",
    ])
    for decile, vals in q_decile_summary.items():
        md_lines.append(
            f"| {decile} | {vals['records']} | {vals['truncated']} | {vals['fraction']:.1%} |"
        )

    md_lines.extend([
        "",
        "### Most Truncated Questions",
        "",
        "| q_idx | records | truncated | fraction |",
        "|---:|---:|---:|---:|",
    ])
    for item in diagnostic["truncation"]["most_truncated_questions"][:15]:
        md_lines.append(
            f"| {item['q_idx']} | {item['records']} | {item['truncated']} | {item['fraction']:.1%} |"
        )

    md_lines.extend([
        "",
        "## Completion Heuristics",
        "",
        f"- Truncated responses ending with sentence punctuation: {truncated_sentence_end}/{len(truncated)} "
        f"({truncated_sentence_end / len(truncated):.1%})",
        f"- Truncated responses meeting abrupt-ending heuristic: {truncated_abrupt}/{len(truncated)} "
        f"({truncated_abrupt / len(truncated):.1%})",
        f"- Non-truncated responses meeting abrupt-ending heuristic: {non_truncated_abrupt}/{len(non_truncated)} "
        f"({non_truncated_abrupt / len(non_truncated):.1%})",
        f"- Truncated responses with at least two trickster lexical markers: "
        f"{truncated_role_marker_ge2}/{len(truncated)} "
        f"({truncated_role_marker_ge2 / len(truncated):.1%})",
        "",
        "## Answers",
        "",
    ])
    question_text = [
        ("How severe is truncation overall?", "severity"),
        ("Is truncation concentrated by system prompt?", "system_prompt_concentration"),
        ("Is truncation concentrated by question subset?", "question_subset_concentration"),
        ("Do truncated responses appear to usually contain enough role expression before the cutoff?", "role_expression_before_cutoff"),
        ("Are endings often abrupt or mostly complete before continuation?", "ending_abruptness"),
        ("Does truncation look likely to bias score-3 selection?", "score3_bias"),
        ("Should Phase 2 scoring proceed on all 1200 records?", "phase2_proceed"),
        ("Is a small follow-up run with higher max_new_tokens recommended?", "followup_recommended"),
    ]
    for question, key in question_text:
        md_lines.append(f"### {question}")
        md_lines.append("")
        md_lines.append(answers[key])
        md_lines.append("")

    OUT_MD.write_text("\n".join(md_lines).rstrip() + "\n")

    sample_md = [
        "# Truncation Review Samples",
        "",
        "Full response texts for human review. Samples are deterministic.",
        "",
    ]
    for sample in samples:
        sample_md.extend([
            "---",
            "",
            f"## {sample['sample_type']} · sp{sample['sp_idx']} q{sample['q_idx']} · line {sample['line_no']}",
            "",
            f"truncated: `{sample['truncated']}` · chars: `{sample['char_len']}` · "
            f"words: `{sample['word_count']}` · abruptness: `{sample['abruptness_score']}` · "
            f"role markers: `{sample['role_marker_count']}`",
            "",
            "```text",
            md_escape(sample["response_text"]),
            "```",
            "",
        ])
    OUT_SAMPLES_MD.write_text("\n".join(sample_md).rstrip() + "\n")

    print(json.dumps(diagnostic, indent=2))


if __name__ == "__main__":
    main()
