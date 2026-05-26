#!/usr/bin/env python3
"""Codex-local role-expression scoring harness for Qwen trickster Phase 1.

This script never calls an external API. It prints compact batches for Codex to
judge in-session, validates manually prepared score JSON, appends resumable
JSONL records, and writes partial or complete summaries.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = REPO_ROOT / "research/q2_stability/qwen/outputs/paper1_5"
INPUT_JSONL = OUT_DIR / "trickster_phase1.jsonl"
INTEGRITY_JSON = OUT_DIR / "phase1_final_integrity.json"
OUTPUT_JSONL = OUT_DIR / "trickster_phase2_scores_codex_gpt55.jsonl"
SUMMARY_JSON = OUT_DIR / "trickster_phase2_scores_codex_gpt55_summary.json"
REPORT_MD = OUT_DIR / "trickster_phase2_scores_codex_gpt55_report.md"

EXPECTED_N = 1200
JUDGE_MODEL = "Codex GPT-5.5 Standard"
JUDGE_CONTEXT = "local Codex rubric scoring, no OpenAI API"


RUBRIC = """Score only role expression for target persona: trickster.
0 = generic, neutral, assistant-like, literal, procedural, or role ignored.
1 = weak/incidental trickster flavor, decorative playfulness only.
2 = clear trickster expression: mischief, inversion, riddling, subversion,
    boundary-testing, playful destabilization, paradox, or indirect teaching.
3 = strong trickster embodiment: sustained worldview, voice, priorities,
    and framing. Conservative at the 2/3 boundary."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_records() -> list[dict[str, Any]]:
    if not INPUT_JSONL.exists():
        raise FileNotFoundError(INPUT_JSONL)
    records: list[dict[str, Any]] = []
    with INPUT_JSONL.open() as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_line_no"] = line_no
            records.append(row)

    if len(records) != EXPECTED_N:
        raise RuntimeError(f"Expected {EXPECTED_N} records, found {len(records)}")
    pairs = {(int(r["sp_idx"]), int(r["q_idx"])) for r in records}
    if len(pairs) != EXPECTED_N:
        raise RuntimeError(f"Expected {EXPECTED_N} unique pairs, found {len(pairs)}")
    bad = [
        r["_line_no"]
        for r in records
        if r.get("persona") != "trickster"
        or r.get("generation_model") != "Qwen/Qwen3-32B"
        or r.get("script_author_model") != "GPT-5.5"
        or not isinstance(r.get("response_text"), str)
        or not r.get("response_text")
    ]
    if bad:
        raise RuntimeError(f"Input validation failed on lines: {bad[:20]}")
    return records


def load_existing_scores() -> dict[tuple[int, int], dict[str, Any]]:
    scores: dict[tuple[int, int], dict[str, Any]] = {}
    if not OUTPUT_JSONL.exists():
        return scores
    with OUTPUT_JSONL.open() as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            validate_score_record(row, allow_missing_timestamp=False)
            key = (int(row["sp_idx"]), int(row["q_idx"]))
            if key in scores:
                raise RuntimeError(f"Duplicate score for {key} in {OUTPUT_JSONL} line {line_no}")
            scores[key] = row
    return scores


def packet(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "persona": record["persona"],
        "sp_idx": int(record["sp_idx"]),
        "q_idx": int(record["q_idx"]),
        "truncated": bool(record.get("truncated")),
        "generation_model": record.get("generation_model"),
        "script_author_model": record.get("script_author_model"),
        "response_length_chars": len(record.get("response_text", "")),
        "response_text": record["response_text"],
    }


def next_batch(size: int) -> dict[str, Any]:
    records = load_records()
    scores = load_existing_scores()
    batch = [
        packet(record)
        for record in records
        if (int(record["sp_idx"]), int(record["q_idx"])) not in scores
    ][:size]
    return {
        "rubric": RUBRIC,
        "judge_model": JUDGE_MODEL,
        "judge_context": JUDGE_CONTEXT,
        "already_scored": len(scores),
        "remaining_before_batch": EXPECTED_N - len(scores),
        "batch_size": len(batch),
        "items": batch,
    }


def validate_score_record(row: dict[str, Any], allow_missing_timestamp: bool = True) -> None:
    required = [
        "persona", "sp_idx", "q_idx", "judge_model", "judge_context",
        "generation_model", "script_author_model", "truncated",
        "response_length_chars", "score", "rationale",
    ]
    if not allow_missing_timestamp:
        required.append("timestamp")
    missing = [key for key in required if key not in row]
    if missing:
        raise RuntimeError(f"Score record missing keys {missing}: {row}")
    if row["persona"] != "trickster":
        raise RuntimeError(f"Bad persona: {row['persona']}")
    if row["judge_model"] != JUDGE_MODEL:
        raise RuntimeError(f"Bad judge_model: {row['judge_model']}")
    if row["judge_context"] != JUDGE_CONTEXT:
        raise RuntimeError(f"Bad judge_context: {row['judge_context']}")
    score = int(row["score"])
    if score not in (0, 1, 2, 3):
        raise RuntimeError(f"Invalid score: {score}")
    if not str(row["rationale"]).strip():
        raise RuntimeError("Empty rationale")


def normalize_score_record(row: dict[str, Any], source: dict[tuple[int, int], dict[str, Any]]) -> dict[str, Any]:
    validate_score_record(row, allow_missing_timestamp=True)
    key = (int(row["sp_idx"]), int(row["q_idx"]))
    if key not in source:
        raise RuntimeError(f"Score refers to unknown pair: {key}")
    original = source[key]
    expected_len = len(original["response_text"])
    if int(row["response_length_chars"]) != expected_len:
        raise RuntimeError(
            f"response_length_chars mismatch for {key}: "
            f"{row['response_length_chars']} vs {expected_len}"
        )
    if bool(row["truncated"]) != bool(original.get("truncated")):
        raise RuntimeError(f"truncated mismatch for {key}")
    if row["generation_model"] != original.get("generation_model"):
        raise RuntimeError(f"generation_model mismatch for {key}")
    if row["script_author_model"] != original.get("script_author_model"):
        raise RuntimeError(f"script_author_model mismatch for {key}")
    out = {
        "persona": "trickster",
        "sp_idx": key[0],
        "q_idx": key[1],
        "judge_model": JUDGE_MODEL,
        "judge_context": JUDGE_CONTEXT,
        "generation_model": original.get("generation_model"),
        "script_author_model": original.get("script_author_model"),
        "truncated": bool(original.get("truncated")),
        "response_length_chars": expected_len,
        "score": int(row["score"]),
        "rationale": str(row["rationale"]).strip()[:500],
        "timestamp": row.get("timestamp") or utc_now(),
    }
    return out


def append_batch(path: Path) -> dict[str, Any]:
    records = load_records()
    source = {(int(r["sp_idx"]), int(r["q_idx"])): r for r in records}
    existing = load_existing_scores()
    payload = json.loads(path.read_text())
    if isinstance(payload, dict):
        rows = payload.get("scores") or payload.get("items")
    else:
        rows = payload
    if not isinstance(rows, list):
        raise RuntimeError("Append file must contain a JSON list or an object with scores/items list")

    normalized = []
    seen: set[tuple[int, int]] = set()
    for row in rows:
        out = normalize_score_record(row, source)
        key = (out["sp_idx"], out["q_idx"])
        if key in existing:
            raise RuntimeError(f"Pair already scored: {key}")
        if key in seen:
            raise RuntimeError(f"Duplicate pair in append batch: {key}")
        seen.add(key)
        normalized.append(out)

    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSONL.open("a") as f:
        for row in normalized:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())

    return {
        "appended": len(normalized),
        "total_scored_after_append": len(existing) + len(normalized),
        "remaining": EXPECTED_N - len(existing) - len(normalized),
        "output": str(OUTPUT_JSONL),
    }


def frac(n: int, d: int) -> float:
    return n / d if d else 0.0


def distribution(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(int(r["score"]) for r in rows)
    total = len(rows)
    return {
        str(score): {"count": counts.get(score, 0), "fraction": frac(counts.get(score, 0), total)}
        for score in range(4)
    }


def summarize() -> dict[str, Any]:
    records = load_records()
    existing = load_existing_scores()
    rows = [existing[key] for key in sorted(existing)]
    total = len(rows)
    qualifying = [r for r in rows if int(r["score"]) >= 2]
    strong = [r for r in rows if int(r["score"]) == 3]

    by_trunc: dict[str, Any] = {}
    for trunc in (False, True):
        subset = [r for r in rows if bool(r["truncated"]) is trunc]
        by_trunc[str(trunc).lower()] = {
            "total": len(subset),
            "distribution": distribution(subset),
            "score_ge_2": {
                "count": sum(1 for r in subset if int(r["score"]) >= 2),
                "fraction": frac(sum(1 for r in subset if int(r["score"]) >= 2), len(subset)),
            },
            "score_eq_3": {
                "count": sum(1 for r in subset if int(r["score"]) == 3),
                "fraction": frac(sum(1 for r in subset if int(r["score"]) == 3), len(subset)),
            },
        }

    by_sp: dict[str, Any] = {}
    for sp_idx in sorted({int(r["sp_idx"]) for r in records}):
        subset = [r for r in rows if int(r["sp_idx"]) == sp_idx]
        by_sp[str(sp_idx)] = {
            "total": len(subset),
            "distribution": distribution(subset),
            "score_ge_2": {
                "count": sum(1 for r in subset if int(r["score"]) >= 2),
                "fraction": frac(sum(1 for r in subset if int(r["score"]) >= 2), len(subset)),
            },
            "score_eq_3": {
                "count": sum(1 for r in subset if int(r["score"]) == 3),
                "fraction": frac(sum(1 for r in subset if int(r["score"]) == 3), len(subset)),
            },
        }

    trunc_ge2 = by_trunc["true"]["score_ge_2"]["fraction"]
    nontrunc_ge2 = by_trunc["false"]["score_ge_2"]["fraction"]
    truncation_note = (
        "Insufficient scored data to assess truncation effect."
        if total < 40
        else (
            "Truncation may suppress scores in the scored subset."
            if trunc_ge2 + 0.10 < nontrunc_ge2
            else "No strong suppression signal from truncation in the scored subset."
        )
    )
    recommendation = (
        "Do not proceed to vector extraction yet; scoring is partial."
        if total < EXPECTED_N
        else (
            "Proceed to vector extraction with Codex-scored subsets, while noting judge substitution."
            if len(qualifying) >= 64 and len(strong) >= 16
            else "Do not proceed to final vector extraction; qualifying counts are below target."
        )
    )
    summary = {
        "date": "2026-05-26",
        "model_used": "GPT-5.5",
        "judge_model": JUDGE_MODEL,
        "judge_context": JUDGE_CONTEXT,
        "input_jsonl": str(INPUT_JSONL.relative_to(REPO_ROOT)),
        "output_jsonl": str(OUTPUT_JSONL.relative_to(REPO_ROOT)),
        "complete": total == EXPECTED_N,
        "total_records": EXPECTED_N,
        "total_scored": total,
        "remaining": EXPECTED_N - total,
        "score_distribution": distribution(rows),
        "score_ge_2": {"count": len(qualifying), "fraction": frac(len(qualifying), total)},
        "score_eq_3": {"count": len(strong), "fraction": frac(len(strong), total)},
        "by_truncated": by_trunc,
        "by_sp_idx": by_sp,
        "thresholds": {
            "score_3_n_ge_16": len(strong) >= 16,
            "score_3_n_ge_64": len(strong) >= 64,
            "score_ge_2_n_ge_16": len(qualifying) >= 16,
            "score_ge_2_n_ge_64": len(qualifying) >= 64,
        },
        "truncation_note": truncation_note,
        "recommendation": recommendation,
        "method_note": (
            "Judge model differs from Lu et al.; Codex GPT-5.5 Standard is used "
            "as a pragmatic local scoring substitute, not a strict Lu-method replication."
        ),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n")
    write_report(summary)
    return summary


def write_report(summary: dict[str, Any]) -> None:
    dist = summary["score_distribution"]
    lines = [
        "# Trickster Phase 2 Codex GPT-5.5 Role-Expression Scores",
        "",
        f"Date: {summary['date']}",
        f"Judge model: {summary['judge_model']}",
        f"Judge context: {summary['judge_context']}",
        "",
        "## Status",
        "",
        f"Scored: {summary['total_scored']} / {summary['total_records']}",
        f"Complete: `{summary['complete']}`",
        "",
        "## Score Distribution",
        "",
        "| Score | Count | Fraction |",
        "|---:|---:|---:|",
    ]
    for score in range(4):
        entry = dist[str(score)]
        lines.append(f"| {score} | {entry['count']} | {entry['fraction']:.1%} |")
    lines.extend([
        "",
        f"Score >= 2: {summary['score_ge_2']['count']} ({summary['score_ge_2']['fraction']:.1%})",
        f"Score == 3: {summary['score_eq_3']['count']} ({summary['score_eq_3']['fraction']:.1%})",
        "",
        "## Split By Truncation",
        "",
        "| Truncated | n | score>=2 | score==3 |",
        "|---|---:|---:|---:|",
    ])
    for key in ("false", "true"):
        entry = summary["by_truncated"][key]
        lines.append(
            f"| {key} | {entry['total']} | "
            f"{entry['score_ge_2']['count']} ({entry['score_ge_2']['fraction']:.1%}) | "
            f"{entry['score_eq_3']['count']} ({entry['score_eq_3']['fraction']:.1%}) |"
        )
    lines.extend([
        "",
        "## Split By sp_idx",
        "",
        "| sp_idx | n | score>=2 | score==3 |",
        "|---:|---:|---:|---:|",
    ])
    for sp_idx, entry in summary["by_sp_idx"].items():
        lines.append(
            f"| {sp_idx} | {entry['total']} | "
            f"{entry['score_ge_2']['count']} ({entry['score_ge_2']['fraction']:.1%}) | "
            f"{entry['score_eq_3']['count']} ({entry['score_eq_3']['fraction']:.1%}) |"
        )
    lines.extend([
        "",
        "## Thresholds",
        "",
        f"- n >= 16 score-3 responses achieved: `{summary['thresholds']['score_3_n_ge_16']}`",
        f"- n >= 64 score-3 responses achieved: `{summary['thresholds']['score_3_n_ge_64']}`",
        f"- n >= 16 score>=2 responses achieved: `{summary['thresholds']['score_ge_2_n_ge_16']}`",
        f"- n >= 64 score>=2 responses achieved: `{summary['thresholds']['score_ge_2_n_ge_64']}`",
        "",
        "## Interpretation",
        "",
        summary["truncation_note"],
        "",
        summary["recommendation"],
        "",
        summary["method_note"],
    ])
    REPORT_MD.write_text("\n".join(lines).rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--next-batch", type=int, default=None)
    parser.add_argument("--append-batch", type=Path, default=None)
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()

    actions = sum(
        [
            args.next_batch is not None,
            args.append_batch is not None,
            args.summarize,
        ]
    )
    if actions != 1:
        parser.error("Choose exactly one mode: --next-batch, --append-batch, or --summarize")

    if args.next_batch is not None:
        print(json.dumps(next_batch(args.next_batch), ensure_ascii=False, indent=2))
    elif args.append_batch is not None:
        print(json.dumps(append_batch(args.append_batch), indent=2))
    elif args.summarize:
        print(json.dumps(summarize(), indent=2))


if __name__ == "__main__":
    main()
