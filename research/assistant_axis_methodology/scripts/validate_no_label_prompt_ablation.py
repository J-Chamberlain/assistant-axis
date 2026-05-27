#!/usr/bin/env python3
"""Validate the no-label prompt-ablation dataset."""

from __future__ import annotations

import json
import math
import re
import string
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROLE_LIST_PATH = ROOT / "data/roles/role_list.json"
INPUT_JSONL = (
    ROOT
    / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl"
)
OUT_JSON = (
    ROOT
    / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_prompt_ablation_validation.json"
)
OUT_MD = (
    ROOT
    / "research/assistant_axis_methodology/no_label_prompt_ablation/no_label_prompt_ablation_validation.md"
)


def normalize_text(text: str) -> str:
    text = text.lower().replace("_", " ").replace("-", " ")
    text = text.translate(str.maketrans({ch: " " for ch in string.punctuation}))
    return re.sub(r"\s+", " ", text).strip()


def role_variants(role: str) -> list[str]:
    base = normalize_text(role)
    variants = {base, base.replace(" ", "-"), base.replace(" ", "_")}
    if base.endswith("y") and len(base) > 1:
        variants.add(base[:-1] + "ies")
    elif base.endswith(("s", "x", "ch", "sh")):
        variants.add(base + "es")
    else:
        variants.add(base + "s")
    return sorted(v for v in variants if v)


def has_label(role: str, text: str) -> bool:
    norm = normalize_text(text)
    return any(
        re.search(rf"\b{re.escape(normalize_text(v))}\b", norm)
        for v in role_variants(role)
    )


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalize_text(text))


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main() -> None:
    roles = json.loads(ROLE_LIST_PATH.read_text())
    records = [json.loads(line) for line in INPUT_JSONL.read_text().splitlines() if line]
    by_pair = {(r["role"], r["prompt_index"]): r for r in records}
    expected_pairs = [(role, i) for role in roles for i in range(5)]
    missing = [pair for pair in expected_pairs if pair not in by_pair]

    for rec in records:
        orig = rec["original_prompt"]
        rew = rec["rewritten_prompt"]
        ot = tokens(orig)
        rt = tokens(rew)
        rec["original_char_length"] = len(orig)
        rec["rewritten_char_length"] = len(rew)
        rec["char_length_ratio"] = len(rew) / len(orig) if orig else None
        rec["original_word_count"] = len(ot)
        rec["rewritten_word_count"] = len(rt)
        rec["word_count_ratio"] = len(rt) / len(ot) if ot else None
        rec["lexical_jaccard"] = jaccard(ot, rt)
        rec["exact_role_label_in_rewrite"] = bool(
            re.search(rf"\b{re.escape(rec['role'].lower())}\b", rew.lower())
        )
        rec["normalized_role_label_in_rewrite"] = has_label(rec["role"], rew)

    exact_remaining = [r for r in records if r["exact_role_label_in_rewrite"]]
    normalized_remaining = [r for r in records if r["normalized_role_label_in_rewrite"]]
    ratios = [r["char_length_ratio"] for r in records if r["char_length_ratio"] is not None]
    word_ratios = [r["word_count_ratio"] for r in records if r["word_count_ratio"] is not None]
    jaccards = [r["lexical_jaccard"] for r in records]
    overflattened = [
        r
        for r in records
        if (r["char_length_ratio"] is not None and r["char_length_ratio"] < 0.55)
        or r["lexical_jaccard"] < 0.35
    ]
    semantic_loss_candidates = [
        r
        for r in records
        if r["role"] in {"devils_advocate", "ancient", "eldritch", "leviathan", "hive"}
        or r["lexical_jaccard"] < 0.4
    ][:100]

    validation = {
        "date": "2026-05-27",
        "model_used": "GPT-5.5",
        "input_jsonl": str(INPUT_JSONL.relative_to(ROOT)),
        "total_expected_prompts": len(expected_pairs),
        "total_rewritten_prompts": len(records),
        "missing_rewrites": [
            {"role": role, "prompt_index": idx} for role, idx in missing
        ],
        "exact_role_label_exposure_in_rewrites": len(exact_remaining),
        "normalized_role_label_exposure_in_rewrites": len(normalized_remaining),
        "rewrite_status_counts": dict(Counter(r["rewrite_status"] for r in records)),
        "char_length_ratio": summarize(ratios),
        "word_count_ratio": summarize(word_ratios),
        "lexical_jaccard": summarize(jaccards),
        "possible_overflattened_count": len(overflattened),
        "possible_overflattened_examples": slim(overflattened[:25]),
        "semantic_loss_candidate_examples": slim(semantic_loss_candidates[:25]),
        "records_with_remaining_label": slim(normalized_remaining[:50]),
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n")
    OUT_MD.write_text(render_markdown(validation) + "\n")
    print(json.dumps(validation, indent=2)[:3000])


def summarize(values: list[float]) -> dict:
    if not values:
        return {}
    vals = sorted(values)
    return {
        "min": vals[0],
        "p05": percentile(vals, 0.05),
        "p25": percentile(vals, 0.25),
        "median": percentile(vals, 0.50),
        "mean": sum(vals) / len(vals),
        "p75": percentile(vals, 0.75),
        "p95": percentile(vals, 0.95),
        "max": vals[-1],
    }


def percentile(vals: list[float], p: float) -> float:
    if not vals:
        return math.nan
    idx = p * (len(vals) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - idx) + vals[hi] * (idx - lo)


def slim(records: list[dict]) -> list[dict]:
    return [
        {
            "role": r["role"],
            "prompt_index": r["prompt_index"],
            "original_prompt": r["original_prompt"],
            "rewritten_prompt": r["rewritten_prompt"],
            "char_length_ratio": r.get("char_length_ratio"),
            "lexical_jaccard": r.get("lexical_jaccard"),
            "rewrite_status": r.get("rewrite_status"),
        }
        for r in records
    ]


def render_markdown(v: dict) -> str:
    lines = [
        "# No-Label Prompt Ablation Validation",
        "",
        "## Summary",
        "",
        f"- Expected prompts: {v['total_expected_prompts']}",
        f"- Rewritten prompts: {v['total_rewritten_prompts']}",
        f"- Missing rewrites: {len(v['missing_rewrites'])}",
        f"- Exact role-label exposure remaining: {v['exact_role_label_exposure_in_rewrites']}",
        f"- Normalized role-label exposure remaining: {v['normalized_role_label_exposure_in_rewrites']}",
        f"- Rewrite status counts: {v['rewrite_status_counts']}",
        "",
        "## Length and Lexical Preservation",
        "",
        f"- Character length ratio median: {v['char_length_ratio'].get('median', 0):.3f}; mean: {v['char_length_ratio'].get('mean', 0):.3f}",
        f"- Word count ratio median: {v['word_count_ratio'].get('median', 0):.3f}; mean: {v['word_count_ratio'].get('mean', 0):.3f}",
        f"- Lexical Jaccard median: {v['lexical_jaccard'].get('median', 0):.3f}; mean: {v['lexical_jaccard'].get('mean', 0):.3f}",
        "",
        "## Possible Over-Flattening",
        "",
        f"Records flagged by low length ratio or low lexical overlap: {v['possible_overflattened_count']}. These are review targets, not automatic failures.",
        "",
        "## Remaining Label Exposure",
        "",
    ]
    if not v["records_with_remaining_label"]:
        lines.append("No rewritten prompts retain normalized target-role label exposure under the audit matcher.")
    else:
        for r in v["records_with_remaining_label"][:25]:
            lines.append(
                f"- `{r['role']}` prompt {r['prompt_index']}: {r['rewritten_prompt']}"
            )
    lines.extend(["", "## Review Examples", ""])
    for r in v["possible_overflattened_examples"][:20]:
        lines.append(
            f"- `{r['role']}` prompt {r['prompt_index']}: ratio={r['char_length_ratio']:.3f}, jaccard={r['lexical_jaccard']:.3f}"
        )
        lines.append(f"  - Original: {r['original_prompt']}")
        lines.append(f"  - Rewrite: {r['rewritten_prompt']}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
