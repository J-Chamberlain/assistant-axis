#!/usr/bin/env python3
"""Score Qwen trickster Phase 1 responses with gpt-4.1-mini.

Resumable local OpenAI API judge pass. Does not read or modify activation shards.
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


INPUT_JSONL = Path("research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl")
INTEGRITY_JSON = Path("research/q2_stability/qwen/outputs/paper1_5/phase1_final_integrity.json")
OUTPUT_JSONL = Path(
    "research/q2_stability/qwen/outputs/paper1_5/trickster_phase2_scores_gpt41mini.jsonl"
)
SUMMARY_JSON = Path(
    "research/q2_stability/qwen/outputs/paper1_5/trickster_phase2_scores_summary.json"
)
REPORT_MD = Path(
    "research/q2_stability/qwen/outputs/paper1_5/trickster_phase2_scores_report.md"
)

JUDGE_MODEL = "gpt-4.1-mini"
MODEL_USED = "GPT-5.5"
EXPECTED_N = 1200
API_URL = "https://api.openai.com/v1/chat/completions"
MAX_RETRIES = 6
BASE_BACKOFF_SECONDS = 2.0
REQUEST_TIMEOUT_SECONDS = 60


SYSTEM_PROMPT = """You are scoring role expression for a mechanistic interpretability replication.

Score only how strongly the response expresses the trickster role. Do not score truth,
helpfulness, safety, literary quality, or whether the answer is truncated except when
truncation prevents enough evidence of role expression.

Rubric:
Score 0: No trickster expression. The response is generic, neutral, assistant-like, or refuses the role.
Score 1: Weak or incidental trickster flavor. Some playful language, but no sustained trickster perspective.
Score 2: Clear trickster expression. The response consistently reflects trickster-like framing, mischief, inversion, riddling, subversion, boundary-testing, or playful destabilization, while still responding to the question.
Score 3: Strong trickster embodiment. The response is deeply and consistently trickster-like in worldview, voice, priorities, and framing, not merely decorative. It should feel like the speaker is operating from a trickster identity.

Return strict JSON only:
{"score": 0|1|2|3, "rationale": "short reason, max 35 words"}"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_api_key() -> str:
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key
    key_path = Path.home() / ".openai_api_key"
    if key_path.exists():
        key = key_path.read_text().strip()
        if key:
            return key
    raise RuntimeError("OPENAI_API_KEY missing: set OPENAI_API_KEY or create ~/.openai_api_key")


def load_records() -> list[dict[str, Any]]:
    if not INPUT_JSONL.exists():
        raise FileNotFoundError(f"Missing input JSONL: {INPUT_JSONL}")
    records = []
    with INPUT_JSONL.open() as f:
        for line_no, line in enumerate(f, start=1):
            if line.strip():
                row = json.loads(line)
                row["_line_no"] = line_no
                records.append(row)
    if len(records) != EXPECTED_N:
        raise RuntimeError(f"Expected {EXPECTED_N} records, found {len(records)}")
    pairs = {(int(r["sp_idx"]), int(r["q_idx"])) for r in records}
    if len(pairs) != len(records):
        raise RuntimeError("Duplicate (sp_idx, q_idx) pairs found in input JSONL")
    bad = [
        r["_line_no"]
        for r in records
        if r.get("persona") != "trickster"
        or r.get("generation_model") != "Qwen/Qwen3-32B"
        or r.get("script_author_model") != "GPT-5.5"
        or not r.get("response_text")
    ]
    if bad:
        raise RuntimeError(f"Input validation failed on lines: {bad[:20]}")
    return records


def load_existing_scores() -> dict[tuple[int, int], dict[str, Any]]:
    scored: dict[tuple[int, int], dict[str, Any]] = {}
    if not OUTPUT_JSONL.exists():
        return scored
    with OUTPUT_JSONL.open() as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            key = (int(row["sp_idx"]), int(row["q_idx"]))
            score = int(row["score"])
            if score < 0 or score > 3:
                raise RuntimeError(f"Invalid score in existing JSONL line {line_no}: {score}")
            scored[key] = row
    return scored


def build_user_prompt(record: dict[str, Any]) -> str:
    trunc = bool(record.get("truncated"))
    return (
        "Persona being evaluated: trickster\n"
        f"Response truncated: {trunc}\n"
        f"sp_idx: {record['sp_idx']}\n"
        f"q_idx: {record['q_idx']}\n\n"
        "Response to score:\n"
        "<response>\n"
        f"{record['response_text']}\n"
        "</response>"
    )


def post_chat_completion(api_key: str, record: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "model": JUDGE_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(record)},
        ],
        "temperature": 0,
        "top_p": 1,
        "max_tokens": 120,
        "response_format": {"type": "json_object"},
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "assistant-axis-local-scorer/1.0",
        },
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                body = json.loads(response.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            score = int(parsed["score"])
            if score not in (0, 1, 2, 3):
                raise ValueError(f"Score out of range: {score}")
            rationale = str(parsed.get("rationale", "")).strip()
            return {"score": score, "rationale": rationale[:500]}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in (401, 403):
                raise RuntimeError(f"OpenAI authentication failed with HTTP {exc.code}") from exc
            if exc.code == 429 or 500 <= exc.code <= 599:
                if attempt == MAX_RETRIES:
                    raise RuntimeError(f"OpenAI API transient failure persisted: HTTP {exc.code} {body[:300]}") from exc
                sleep_with_backoff(attempt, exc.code)
                continue
            raise RuntimeError(f"OpenAI API request failed: HTTP {exc.code} {body[:500]}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"OpenAI API/parse failure persisted: {exc}") from exc
            sleep_with_backoff(attempt, type(exc).__name__)
    raise RuntimeError("Unreachable retry state")


def sleep_with_backoff(attempt: int, reason: Any) -> None:
    delay = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
    print(f"Retryable error ({reason}); retry {attempt}/{MAX_RETRIES}, sleeping {delay:.1f}s", flush=True)
    time.sleep(delay)


def make_output_record(record: dict[str, Any], judged: dict[str, Any]) -> dict[str, Any]:
    return {
        "persona": record["persona"],
        "sp_idx": int(record["sp_idx"]),
        "q_idx": int(record["q_idx"]),
        "judge_model": JUDGE_MODEL,
        "generation_model": record.get("generation_model"),
        "script_author_model": record.get("script_author_model"),
        "model_used": MODEL_USED,
        "truncated": bool(record.get("truncated")),
        "response_length_chars": len(record.get("response_text", "")),
        "score": int(judged["score"]),
        "rationale": judged["rationale"],
        "timestamp": utc_now(),
    }


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def fraction(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    score_counts = Counter(int(r["score"]) for r in rows)
    score_distribution = {
        str(score): {"count": score_counts.get(score, 0), "fraction": fraction(score_counts.get(score, 0), total)}
        for score in range(4)
    }
    qualifying = sum(1 for r in rows if int(r["score"]) >= 2)
    strong = sum(1 for r in rows if int(r["score"]) == 3)

    truncated_split: dict[str, Any] = {}
    for trunc_value in (False, True):
        subset = [r for r in rows if bool(r["truncated"]) is trunc_value]
        counts = Counter(int(r["score"]) for r in subset)
        truncated_split[str(trunc_value).lower()] = {
            "total": len(subset),
            "score_distribution": {
                str(score): {"count": counts.get(score, 0), "fraction": fraction(counts.get(score, 0), len(subset))}
                for score in range(4)
            },
            "mean_score": round(sum(int(r["score"]) for r in subset) / len(subset), 6) if subset else None,
        }

    by_sp_idx: dict[str, Any] = {}
    for sp_idx in sorted({int(r["sp_idx"]) for r in rows}):
        subset = [r for r in rows if int(r["sp_idx"]) == sp_idx]
        counts = Counter(int(r["score"]) for r in subset)
        by_sp_idx[str(sp_idx)] = {
            "total": len(subset),
            "score_distribution": {
                str(score): {"count": counts.get(score, 0), "fraction": fraction(counts.get(score, 0), len(subset))}
                for score in range(4)
            },
            "qualifying_score_ge_2": sum(1 for r in subset if int(r["score"]) >= 2),
            "score_3": sum(1 for r in subset if int(r["score"]) == 3),
            "mean_score": round(sum(int(r["score"]) for r in subset) / len(subset), 6) if subset else None,
        }

    non_trunc_mean = truncated_split["false"]["mean_score"]
    trunc_mean = truncated_split["true"]["mean_score"]
    if trunc_mean is None or non_trunc_mean is None:
        truncation_note = "Truncation comparison unavailable because one split is empty."
    elif trunc_mean < non_trunc_mean - 0.1:
        truncation_note = "Truncated responses score lower on average; truncation appears to suppress role-expression scores."
    elif trunc_mean > non_trunc_mean + 0.1:
        truncation_note = "Truncated responses score higher on average; truncation may inflate scores by selecting highly stylized long generations."
    else:
        truncation_note = "Truncated and non-truncated responses have similar mean scores; no strong truncation effect is visible."

    proceed = qualifying >= 16
    summary = {
        "model_used": MODEL_USED,
        "judge_model": JUDGE_MODEL,
        "input_jsonl": str(INPUT_JSONL),
        "output_jsonl": str(OUTPUT_JSONL),
        "integrity_json": str(INTEGRITY_JSON),
        "timestamp": utc_now(),
        "total_scored": total,
        "score_distribution": score_distribution,
        "qualifying_score_ge_2": {"count": qualifying, "fraction": fraction(qualifying, total)},
        "score_3": {"count": strong, "fraction": fraction(strong, total)},
        "truncated_split": truncated_split,
        "score_distribution_by_sp_idx": by_sp_idx,
        "achieved_n_ge_16_score_3": strong >= 16,
        "achieved_n_ge_16_score_ge_2": qualifying >= 16,
        "truncation_note": truncation_note,
        "recommendation": (
            "Proceed to vector extraction using score >= 2 responses; score-3-only extraction is also feasible."
            if strong >= 16
            else (
                "Proceed to vector extraction using score >= 2 responses; score-3-only extraction is not recommended."
                if proceed
                else "Do not proceed to vector extraction; fewer than 16 qualifying responses were found."
            )
        ),
    }
    return summary


def write_summary_and_report(rows: list[dict[str, Any]]) -> None:
    summary = summarize(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    REPORT_MD.write_text(make_report(summary))


def make_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Trickster Phase 2 gpt-4.1-mini Scoring Report",
        "",
        f"Generated: {summary['timestamp']}",
        f"Model used: {summary['model_used']}",
        f"Judge model: {summary['judge_model']}",
        f"Input: `{summary['input_jsonl']}`",
        f"Scores: `{summary['output_jsonl']}`",
        "",
        "## Summary",
        "",
        f"- Total scored: {summary['total_scored']}",
        f"- Qualifying score >= 2: {summary['qualifying_score_ge_2']['count']} ({summary['qualifying_score_ge_2']['fraction']:.3f})",
        f"- Score 3: {summary['score_3']['count']} ({summary['score_3']['fraction']:.3f})",
        f"- Achieved n >= 16 score 3: {summary['achieved_n_ge_16_score_3']}",
        f"- Achieved n >= 16 score >= 2: {summary['achieved_n_ge_16_score_ge_2']}",
        f"- Recommendation: {summary['recommendation']}",
        "",
        "## Score Distribution",
        "",
        "| Score | Count | Fraction |",
        "|---:|---:|---:|",
    ]
    for score in range(4):
        item = summary["score_distribution"][str(score)]
        lines.append(f"| {score} | {item['count']} | {item['fraction']:.3f} |")

    lines.extend(["", "## Truncated vs Non-Truncated", "", summary["truncation_note"], ""])
    for trunc_key in ("false", "true"):
        split = summary["truncated_split"][trunc_key]
        label = "Non-truncated" if trunc_key == "false" else "Truncated"
        lines.extend(
            [
                f"### {label}",
                "",
                f"- Total: {split['total']}",
                f"- Mean score: {split['mean_score']}",
                "",
                "| Score | Count | Fraction |",
                "|---:|---:|---:|",
            ]
        )
        for score in range(4):
            item = split["score_distribution"][str(score)]
            lines.append(f"| {score} | {item['count']} | {item['fraction']:.3f} |")
        lines.append("")

    lines.extend(
        [
            "## Score Distribution by sp_idx",
            "",
            "| sp_idx | Total | Mean | Score 0 | Score 1 | Score 2 | Score 3 | Score >= 2 |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for sp_idx, item in summary["score_distribution_by_sp_idx"].items():
        dist = item["score_distribution"]
        lines.append(
            f"| {sp_idx} | {item['total']} | {item['mean_score']} | "
            f"{dist['0']['count']} | {dist['1']['count']} | {dist['2']['count']} | "
            f"{dist['3']['count']} | {item['qualifying_score_ge_2']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    api_key = load_api_key()
    records = load_records()
    scored = load_existing_scores()
    print(f"Loaded {len(records)} records; existing scores: {len(scored)}", flush=True)

    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    newly_scored = 0
    start = time.time()
    for record in records:
        key = (int(record["sp_idx"]), int(record["q_idx"]))
        if key in scored:
            continue
        judged = post_chat_completion(api_key, record)
        out = make_output_record(record, judged)
        append_jsonl(OUTPUT_JSONL, out)
        scored[key] = out
        newly_scored += 1
        if newly_scored % 25 == 0:
            elapsed = time.time() - start
            print(
                f"Progress: {len(scored)}/{len(records)} total scored "
                f"({newly_scored} new, {elapsed/60:.1f} min elapsed)",
                flush=True,
            )

    rows = [scored[(int(r["sp_idx"]), int(r["q_idx"]))] for r in records if (int(r["sp_idx"]), int(r["q_idx"])) in scored]
    write_summary_and_report(rows)
    print(f"Done. Total scored: {len(rows)}", flush=True)
    print(f"Wrote {OUTPUT_JSONL}", flush=True)
    print(f"Wrote {SUMMARY_JSON}", flush=True)
    print(f"Wrote {REPORT_MD}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
