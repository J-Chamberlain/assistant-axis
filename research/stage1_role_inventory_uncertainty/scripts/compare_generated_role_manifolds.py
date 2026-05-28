#!/usr/bin/env python3
"""Compare generated Stage-1 role inventories using local/offline methods."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
NORMALIZED_PATH = ROOT / "analysis" / "normalized_role_lists.json"
SUMMARY_PATH = ROOT / "analysis" / "generated_role_manifold_comparison.json"
PAIRWISE_CSV_PATH = ROOT / "analysis" / "inventory_pairwise_overlap.csv"
REPORT_PATH = ROOT / "stage1_uncertainty_initial_findings.md"
SCRIPT_AUTHOR_MODEL = "GPT-5.5 Standard via Codex"

FAMILY_KEYWORDS = {
    "assistant_adjacent": ["assistant", "editor", "reviewer", "evaluator", "consultant", "advisor", "tutor", "coach", "analyst", "proofreader"],
    "emotional": ["anxious", "angry", "grieving", "joyful", "melancholic", "fearful", "hopeful", "resentful", "lonely", "empathetic"],
    "procedural": ["manager", "engineer", "planner", "operator", "technician", "accountant", "administrator", "coordinator", "strategist"],
    "mythic_symbolic": ["oracle", "mystic", "angel", "demon", "spirit", "god", "ghost", "dragon", "prophet", "sage"],
    "social_kinship": ["parent", "child", "sibling", "friend", "neighbor", "elder", "teacher", "student", "leader", "follower"],
    "liminal": ["exile", "refugee", "wanderer", "stranger", "outsider", "threshold", "ghost", "orphan", "survivor"],
    "collective": ["hive", "swarm", "collective", "crowd", "committee", "chorus", "mob", "network", "egregore"],
    "play_chaos": ["trickster", "jester", "fool", "comedian", "improviser", "absurdist", "rebel", "chaos"],
}


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_normalized(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing normalized role list file: {path}. Run normalize_role_lists.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def cosine_counter(a: Counter[str], b: Counter[str]) -> float:
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def family_counts(roles: list[str]) -> dict[str, int]:
    counts = {}
    for family, keywords in FAMILY_KEYWORDS.items():
        counts[family] = sum(1 for role in roles if any(keyword in role for keyword in keywords))
    return counts


def write_pairwise_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["inventory_a", "inventory_b", "provider_a", "provider_b", "model_a", "model_b", "jaccard", "overlap_count"],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Stage-1 Role Inventory Uncertainty: Initial Findings",
        "",
        "## Status",
        "",
        "This report is generated from locally available normalized inventory files. It is infrastructure-ready and should be regenerated after OpenAI and Claude-side inventories are synced into `parsed_outputs/`.",
        "",
        "## Current Inputs",
        "",
        f"- Inventories analyzed: {summary['n_inventories']}",
        f"- Unique normalized roles: {summary['n_unique_roles']}",
        "",
        "## Pairwise Overlap",
        "",
    ]
    if summary["pairwise_overlap"]:
        for row in summary["pairwise_overlap"][:10]:
            lines.append(f"- `{row['inventory_a']}` vs `{row['inventory_b']}`: Jaccard {row['jaccard']:.3f}, overlap {row['overlap_count']}")
    else:
        lines.append("- Pairwise overlap is not available until at least two inventories exist.")
    lines.extend(
        [
            "",
            "## Stable Semantic Regions",
            "",
            "Stable regions are operationalized as role-family keyword counts and high-frequency normalized labels across inventories. This is a first-pass local method, not a claim of psychological universality.",
            "",
            "## Generator-Specific Tendencies",
            "",
            "Generator-specific tendencies should be interpreted only after inventories from multiple models and prompt-family variants are available.",
            "",
            "## Implications",
            "",
            "This infrastructure tests whether Lu-style role inventories depend strongly on the generator model and generation prompt. Any recurring role families across providers would indicate stable semantic basins in the role-inventory generation process; provider-specific regions would indicate inventory-construction uncertainty that should be separated from activation-space findings.",
            "",
            "## Limitations",
            "",
            "No generated inventory should be treated as canonical. These outputs describe the role corpus construction process, not universal human psychology or model activation geometry.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=NORMALIZED_PATH)
    parser.add_argument("--summary", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--pairwise-csv", type=Path, default=PAIRWISE_CSV_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    normalized = load_normalized(args.input)
    inventories = normalized.get("inventories", [])
    pairwise = []
    for a, b in combinations(inventories, 2):
        roles_a = set(a.get("normalized_role_list", []))
        roles_b = set(b.get("normalized_role_list", []))
        pairwise.append(
            {
                "inventory_a": a["inventory_id"],
                "inventory_b": b["inventory_id"],
                "provider_a": a.get("provider", "unknown"),
                "provider_b": b.get("provider", "unknown"),
                "model_a": a.get("model", "unknown"),
                "model_b": b.get("model", "unknown"),
                "jaccard": jaccard(roles_a, roles_b),
                "overlap_count": len(roles_a & roles_b),
            }
        )

    role_counts = Counter(normalized.get("role_counts", {}))
    family_by_inventory = {
        inv["inventory_id"]: family_counts(inv.get("normalized_role_list", []))
        for inv in inventories
    }
    provider_counts: dict[str, int] = defaultdict(int)
    model_counts: dict[str, int] = defaultdict(int)
    for inv in inventories:
        provider_counts[inv.get("provider", "unknown")] += 1
        model_counts[inv.get("model", "unknown")] += 1

    summary = {
        "created_at": utc_timestamp(),
        "input_path": str(args.input),
        "model_provenance": {
            "task_type": "semantic_analysis",
            "artifact_type": "analysis_summary",
            "artifact_path": str(args.summary),
            "generation_model": None,
            "evaluation_model": None,
            "analysis_model": None,
            "script_author_model": SCRIPT_AUTHOR_MODEL,
            "orchestration_agent": "Codex",
            "provider": "none",
            "model_version_or_alias": "scripted_local_analysis",
            "date": utc_timestamp(),
            "prompt_family_id": None,
            "temperature": None,
            "max_tokens": None,
            "source_inputs": [str(args.input)],
            "notes_on_uncertainty": "Local scripted overlap analysis; no LLM analysis model is invoked by this script.",
        },
        "n_inventories": len(inventories),
        "n_unique_roles": len(role_counts),
        "provider_counts": dict(sorted(provider_counts.items())),
        "model_counts": dict(sorted(model_counts.items())),
        "top_recurrent_roles": role_counts.most_common(50),
        "family_counts_by_inventory": family_by_inventory,
        "pairwise_overlap": sorted(pairwise, key=lambda row: row["jaccard"], reverse=True),
        "analysis_note": "Local lexical overlap and role-family analysis; semantic embeddings can be added later if a local embedding dependency is available.",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_pairwise_csv(args.pairwise_csv, summary["pairwise_overlap"])
    write_report(args.report, summary)
    print(f"Wrote {args.summary}")
    print(f"Wrote {args.pairwise_csv}")
    print(f"Wrote {args.report}")


if __name__ == "__main__":
    main()
