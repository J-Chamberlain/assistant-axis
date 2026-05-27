#!/usr/bin/env python3
"""Audit explicit role-label exposure in Lu et al. role system prompts.

This is a local, deterministic string-analysis audit. It does not use external
APIs and does not judge whether prompts successfully elicit behavior.
"""

from __future__ import annotations

import json
import re
import string
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[3]
INSTRUCTIONS_DIR = ROOT / "data/roles/instructions"
ROLE_LIST_PATH = ROOT / "data/roles/role_list.json"
CANONICAL_PROMPTS_MD = (
    ROOT
    / "research/assistant_axis_methodology/prompts_and_questions/canonical_system_prompts.md"
)
TRICKSTER_SCORE_SUMMARY = (
    ROOT
    / "research/q2_stability/qwen/outputs/paper1_5/trickster_phase2_scores_codex_gpt55_summary.json"
)
EDITOR_SCORE_SUMMARY = (
    ROOT
    / "research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase2_scores_codex_gpt55_summary.json"
)
OUT_JSON = (
    ROOT
    / "research/assistant_axis_methodology/role_prompt_label_exposure_audit.json"
)
OUT_MD = (
    ROOT
    / "research/assistant_axis_methodology/role_prompt_label_exposure_audit.md"
)

SPECIAL_ROLES = [
    "trickster",
    "editor",
    "assistant",
    "evaluator",
    "reviewer",
    "consultant",
    "oracle",
    "hive",
    "egregore",
    "mystic",
    "skeptic",
    "diplomat",
]

ASSISTANT_ADJACENT_ROLES = [
    "assistant",
    "evaluator",
    "reviewer",
    "consultant",
    "editor",
    "proofreader",
    "screener",
    "grader",
    "examiner",
    "moderator",
    "interviewer",
    "facilitator",
    "coordinator",
    "generalist",
    "interpreter",
    "synthesizer",
]

THEATRICAL_FANTASTICAL_ROLES = [
    "trickster",
    "jester",
    "fool",
    "oracle",
    "hive",
    "egregore",
    "mystic",
    "demon",
    "angel",
    "ghost",
    "genie",
    "eldritch",
    "leviathan",
    "golem",
    "chimera",
    "shaman",
    "prophet",
    "vampire",
    "werewolf",
    "alien",
    "avatar",
]


def normalize_text(text: str) -> str:
    text = text.lower().replace("_", " ").replace("-", " ")
    text = text.translate(str.maketrans({ch: " " for ch in string.punctuation}))
    return re.sub(r"\s+", " ", text).strip()


def role_variants(role: str) -> list[str]:
    base = normalize_text(role)
    variants = {base}
    if base.endswith("y") and len(base) > 1:
        variants.add(base[:-1] + "ies")
    if base.endswith(("s", "x", "ch", "sh")):
        variants.add(base + "es")
    else:
        variants.add(base + "s")
    variants.add(base.replace(" ", "-"))
    variants.add(base.replace(" ", "_"))
    return sorted(v for v in variants if v)


def exact_label_exposed(role: str, prompt: str) -> bool:
    return role.lower() in prompt.lower()


def normalized_label_exposed(role: str, prompt: str) -> bool:
    norm_prompt = normalize_text(prompt)
    for variant in role_variants(role):
        norm_variant = normalize_text(variant)
        if re.search(rf"\b{re.escape(norm_variant)}\b", norm_prompt):
            return True
    return False


def direct_identity_framing(role: str, prompt: str) -> bool:
    norm_prompt = normalize_text(prompt)
    variants = [normalize_text(v) for v in role_variants(role)]
    articles = r"(?:a|an|the)?"
    patterns = []
    for variant in variants:
        v = re.escape(variant)
        patterns.extend(
            [
                rf"\byou are {articles}\s*{v}\b",
                rf"\byou are now {articles}\s*{v}\b",
                rf"\bplease be {articles}\s*{v}\b",
                rf"\bact as {articles}\s*{v}\b",
                rf"\badopt the role of {articles}\s*{v}\b",
                rf"\btake on the role of {articles}\s*{v}\b",
                rf"\bas {articles}\s*{v}\b",
                rf"\brespond as {articles}\s*{v}\b",
                rf"\bembody {articles}\s*{v}\b",
            ]
        )
    return any(re.search(pattern, norm_prompt) for pattern in patterns)


def exposure_category(count: int) -> str:
    if count == 0:
        return "0/5 none"
    if count <= 2:
        return "1-2/5 partial"
    if count == 5:
        return "5/5 complete"
    return "3-5/5 high"


def load_score_summary(path: Path) -> dict | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    total = data.get("total_scored") or data.get("n_scored") or data.get("total")
    score_counts = data.get("score_counts", {})
    if not score_counts and "counts_by_score" in data:
        score_counts = data["counts_by_score"]
    if not score_counts and "score_distribution" in data:
        score_counts = {
            str(k): v.get("count", 0) if isinstance(v, dict) else v
            for k, v in data["score_distribution"].items()
        }
    ge2 = data.get("score_ge_2_count")
    eq3 = data.get("score_eq_3_count")
    if ge2 is None and isinstance(data.get("score_ge_2"), dict):
        ge2 = data["score_ge_2"].get("count")
    if eq3 is None and isinstance(data.get("score_eq_3"), dict):
        eq3 = data["score_eq_3"].get("count")
    if ge2 is None:
        ge2 = sum(int(v) for k, v in score_counts.items() if int(k) >= 2)
    if eq3 is None:
        eq3 = int(score_counts.get("3", score_counts.get(3, 0)))
    return {
        "path": str(path.relative_to(ROOT)),
        "total_scored": total,
        "score_ge_2": ge2,
        "score_eq_3": eq3,
        "score_ge_2_fraction": (ge2 / total) if total else None,
        "score_eq_3_fraction": (eq3 / total) if total else None,
    }


def summarize_group(rows: list[dict], role_names: list[str]) -> dict:
    selected = [r for r in rows if r["role"] in role_names]
    if not selected:
        return {"n_roles": 0}
    return {
        "n_roles": len(selected),
        "mean_exposed_prompts": mean(r["exposed_prompt_count"] for r in selected),
        "mean_exposure_fraction": mean(r["exposure_fraction"] for r in selected),
        "category_counts": dict(Counter(r["exposure_category"] for r in selected)),
        "roles": [r["role"] for r in selected],
    }


def main() -> None:
    role_descriptions = json.loads(ROLE_LIST_PATH.read_text())
    rows = []
    missing_instruction_files = []

    for role, description in role_descriptions.items():
        path = INSTRUCTIONS_DIR / f"{role}.json"
        if not path.exists():
            missing_instruction_files.append(role)
            continue
        data = json.loads(path.read_text())
        prompts = [item.get("pos", "") for item in data.get("instruction", [])]
        prompt_rows = []
        exposed_count = 0
        exact_count = 0
        direct_count = 0
        for idx, prompt in enumerate(prompts):
            exact = exact_label_exposed(role, prompt)
            normalized = normalized_label_exposed(role, prompt)
            direct = direct_identity_framing(role, prompt)
            exposed = exact or normalized
            exposed_count += int(exposed)
            exact_count += int(exact)
            direct_count += int(direct)
            prompt_rows.append(
                {
                    "prompt_index": idx,
                    "prompt_text": prompt,
                    "exact_role_label_appears": exact,
                    "normalized_role_label_or_variant_appears": normalized,
                    "direct_identity_framing": direct,
                    "mostly_behavioral_without_explicit_role_label": not exposed,
                }
            )
        rows.append(
            {
                "role": role,
                "role_file": str(path.relative_to(ROOT)),
                "role_description": description,
                "role_variants_checked": role_variants(role),
                "prompts": prompt_rows,
                "exact_exposed_prompt_count": exact_count,
                "exposed_prompt_count": exposed_count,
                "direct_identity_prompt_count": direct_count,
                "exposure_fraction": exposed_count / len(prompts) if prompts else 0.0,
                "exposure_category": exposure_category(exposed_count),
            }
        )

    total_roles = len(rows)
    total_prompts = sum(len(r["prompts"]) for r in rows)
    total_exposed_prompts = sum(r["exposed_prompt_count"] for r in rows)
    total_exact_prompts = sum(r["exact_exposed_prompt_count"] for r in rows)
    total_direct_identity_prompts = sum(r["direct_identity_prompt_count"] for r in rows)
    category_counts = Counter(r["exposure_category"] for r in rows)
    exposed_by_count = Counter(r["exposed_prompt_count"] for r in rows)
    most_exposed = sorted(
        rows, key=lambda r: (-r["exposed_prompt_count"], r["role"])
    )[:25]
    least_exposed = sorted(
        rows, key=lambda r: (r["exposed_prompt_count"], r["role"])
    )[:25]

    special = {}
    for role in SPECIAL_ROLES:
        match = next((r for r in rows if r["role"] == role), None)
        special[role] = match or {"missing": True}

    scoring = {
        "trickster": load_score_summary(TRICKSTER_SCORE_SUMMARY),
        "editor": load_score_summary(EDITOR_SCORE_SUMMARY),
    }

    audit = {
        "date": "2026-05-27",
        "research_question": "Do Lu et al. role system prompts explicitly expose persona labels, potentially introducing direct identity-label priming?",
        "source_paths": {
            "role_instruction_json_dir": str(INSTRUCTIONS_DIR.relative_to(ROOT)),
            "role_list": str(ROLE_LIST_PATH.relative_to(ROOT)),
            "canonical_system_prompts_export": str(
                CANONICAL_PROMPTS_MD.relative_to(ROOT)
            ),
            "trickster_score_summary": str(TRICKSTER_SCORE_SUMMARY.relative_to(ROOT))
            if TRICKSTER_SCORE_SUMMARY.exists()
            else None,
            "editor_score_summary": str(EDITOR_SCORE_SUMMARY.relative_to(ROOT))
            if EDITOR_SCORE_SUMMARY.exists()
            else None,
        },
        "method": {
            "matching": [
                "case-insensitive exact role-label substring",
                "normalized lowercase matching with underscores/hyphens replaced by spaces, punctuation stripped, and whitespace collapsed",
                "basic singular/plural and hyphen/underscore/space variants",
                "simple direct identity framing regexes such as 'you are a ROLE', 'act as a ROLE', and 'as a ROLE'",
            ],
            "excluded_files": ["data/roles/instructions/default.json"],
        },
        "summary": {
            "total_roles_analyzed": total_roles,
            "total_prompts_analyzed": total_prompts,
            "total_prompts_with_exact_label_exposure": total_exact_prompts,
            "total_prompts_with_normalized_or_variant_label_exposure": total_exposed_prompts,
            "total_prompts_with_direct_identity_framing": total_direct_identity_prompts,
            "percent_prompts_with_exact_label_exposure": round(
                100 * total_exact_prompts / total_prompts, 4
            )
            if total_prompts
            else None,
            "percent_prompts_with_normalized_or_variant_label_exposure": round(
                100 * total_exposed_prompts / total_prompts, 4
            )
            if total_prompts
            else None,
            "percent_prompts_with_direct_identity_framing": round(
                100 * total_direct_identity_prompts / total_prompts, 4
            )
            if total_prompts
            else None,
            "role_exposure_category_counts": dict(category_counts),
            "role_exposure_count_distribution": dict(sorted(exposed_by_count.items())),
            "missing_instruction_files": missing_instruction_files,
        },
        "assistant_adjacent_roles_exposure_pattern": summarize_group(
            rows, ASSISTANT_ADJACENT_ROLES
        ),
        "theatrical_fantastical_roles_exposure_pattern": summarize_group(
            rows, THEATRICAL_FANTASTICAL_ROLES
        ),
        "special_roles": special,
        "most_exposed_roles": [
            {
                "role": r["role"],
                "exposed_prompt_count": r["exposed_prompt_count"],
                "direct_identity_prompt_count": r["direct_identity_prompt_count"],
                "category": r["exposure_category"],
            }
            for r in most_exposed
        ],
        "least_exposed_roles": [
            {
                "role": r["role"],
                "exposed_prompt_count": r["exposed_prompt_count"],
                "direct_identity_prompt_count": r["direct_identity_prompt_count"],
                "category": r["exposure_category"],
            }
            for r in least_exposed
        ],
        "optional_scoring_comparison": scoring,
        "roles": rows,
    }

    OUT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n")
    OUT_MD.write_text(render_markdown(audit) + "\n")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(json.dumps(audit["summary"], indent=2))


def pct(n: float | int | None) -> str:
    if n is None:
        return "n/a"
    return f"{n:.1f}%"


def render_markdown(audit: dict) -> str:
    s = audit["summary"]
    lines = [
        "# Role Prompt Label-Exposure Audit",
        "",
        "## Research Question",
        "",
        audit["research_question"],
        "",
        "This audit tests whether Lu et al. role system prompts explicitly contain the persona title/name they are intended to elicit. The goal is methodological: identify how much direct identity-label priming exists in the prompt set before making claims about purely behavioral elicitation.",
        "",
        "## Data Source Paths",
        "",
    ]
    for key, value in audit["source_paths"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "Canonical machine-readable source used for the audit: `data/roles/instructions/*.json`, with role descriptions from `data/roles/role_list.json`. The markdown prompt export under `research/assistant_axis_methodology/prompts_and_questions/canonical_system_prompts.md` was treated as a readable derived copy, not the analysis source.",
            "",
            "## Method",
            "",
            "For each of the 275 canonical roles, the script inspected the five `instruction[].pos` system prompts. It checked case-insensitive exact label exposure, normalized label exposure after replacing underscores and hyphens with spaces, basic singular/plural and separator variants, and simple direct identity framing patterns such as `You are a [role]`, `Act as a [role]`, and `As a [role]`. `default.json` was excluded because it is the assistant baseline prompt file, not one of the 275 role personas.",
            "",
            "The audit is conservative string analysis. It does not use semantic matching, external APIs, or LLM scoring.",
            "",
            "## Overall Findings",
            "",
            f"- Total roles analyzed: {s['total_roles_analyzed']}",
            f"- Total prompts analyzed: {s['total_prompts_analyzed']}",
            f"- Prompts with exact role-label exposure: {s['total_prompts_with_exact_label_exposure']} ({pct(s['percent_prompts_with_exact_label_exposure'])})",
            f"- Prompts with normalized or variant label exposure: {s['total_prompts_with_normalized_or_variant_label_exposure']} ({pct(s['percent_prompts_with_normalized_or_variant_label_exposure'])})",
            f"- Prompts with direct identity framing: {s['total_prompts_with_direct_identity_framing']} ({pct(s['percent_prompts_with_direct_identity_framing'])})",
            "",
            "Role exposure category counts:",
            "",
        ]
    )
    for cat in ["0/5 none", "1-2/5 partial", "3-5/5 high", "5/5 complete"]:
        lines.append(f"- {cat}: {s['role_exposure_category_counts'].get(cat, 0)}")

    lines.extend(["", "## Special-Role Table", ""])
    lines.append(
        "| Role | Exposed prompts | Direct identity prompts | Category | Role-expression yield if available |"
    )
    lines.append("|---|---:|---:|---|---|")
    scoring = audit["optional_scoring_comparison"]
    for role in SPECIAL_ROLES:
        row = audit["special_roles"][role]
        if row.get("missing"):
            lines.append(f"| `{role}` | missing | missing | missing | n/a |")
            continue
        score_note = "n/a"
        if role in scoring and scoring[role]:
            sc = scoring[role]
            score_note = (
                f"{sc['score_ge_2']}/{sc['total_scored']} score>=2; "
                f"{sc['score_eq_3']}/{sc['total_scored']} score==3"
            )
        lines.append(
            f"| `{role}` | {row['exposed_prompt_count']}/5 | "
            f"{row['direct_identity_prompt_count']}/5 | {row['exposure_category']} | {score_note} |"
        )

    lines.extend(["", "## Prompt-Level Findings for Special Roles", ""])
    for role in SPECIAL_ROLES:
        row = audit["special_roles"][role]
        lines.append(f"### {role}")
        if row.get("missing"):
            lines.append("")
            lines.append("Role file missing.")
            lines.append("")
            continue
        lines.append("")
        lines.append(
            f"Exposure: {row['exposed_prompt_count']}/5; direct identity framing: {row['direct_identity_prompt_count']}/5; category: {row['exposure_category']}."
        )
        lines.append("")
        for prompt in row["prompts"]:
            flags = []
            if prompt["exact_role_label_appears"]:
                flags.append("exact")
            if prompt["normalized_role_label_or_variant_appears"]:
                flags.append("normalized")
            if prompt["direct_identity_framing"]:
                flags.append("direct-identity")
            if not flags:
                flags.append("no-label")
            lines.append(
                f"{prompt['prompt_index'] + 1}. [{', '.join(flags)}] {prompt['prompt_text']}"
            )
        lines.append("")

    lines.extend(["## Full Exposure Distribution", ""])
    lines.append("| Exposed prompt count | Number of roles |")
    lines.append("|---:|---:|")
    for count, n in s["role_exposure_count_distribution"].items():
        lines.append(f"| {count} | {n} |")

    lines.extend(["", "## Most Exposed Roles", ""])
    lines.append("| Role | Exposed prompts | Direct identity prompts | Category |")
    lines.append("|---|---:|---:|---|")
    for row in audit["most_exposed_roles"][:20]:
        lines.append(
            f"| `{row['role']}` | {row['exposed_prompt_count']}/5 | {row['direct_identity_prompt_count']}/5 | {row['category']} |"
        )

    lines.extend(["", "## Least Exposed Roles", ""])
    lines.append("| Role | Exposed prompts | Direct identity prompts | Category |")
    lines.append("|---|---:|---:|---|")
    for row in audit["least_exposed_roles"][:20]:
        lines.append(
            f"| `{row['role']}` | {row['exposed_prompt_count']}/5 | {row['direct_identity_prompt_count']}/5 | {row['category']} |"
        )

    adj = audit["assistant_adjacent_roles_exposure_pattern"]
    theater = audit["theatrical_fantastical_roles_exposure_pattern"]
    lines.extend(
        [
            "",
            "## Group Patterns",
            "",
            f"Assistant-adjacent role set: n={adj.get('n_roles', 0)}, mean exposed prompts={adj.get('mean_exposed_prompts', 0):.2f}/5, mean exposure fraction={adj.get('mean_exposure_fraction', 0):.3f}.",
            "",
            f"Theatrical/fantastical role set: n={theater.get('n_roles', 0)}, mean exposed prompts={theater.get('mean_exposed_prompts', 0):.2f}/5, mean exposure fraction={theater.get('mean_exposure_fraction', 0):.3f}.",
            "",
            "These group sets are heuristic label-based subsets, not cluster assignments.",
            "",
            "## Interpretation",
            "",
            "The Lu et al. role-prompt set contains extensive direct identity-label priming. In this audit, most prompts explicitly expose the target role label or a normalized variant, and most roles fall in the complete 5/5 exposure category. This means the extraction design should be described as role-label-plus-behavior elicitation, not purely behavioral elicitation.",
            "",
            "Exposure varies across roles, so label exposure is a possible source of uneven role-expression yield. The trickster and editor prompt sets both show complete label exposure, yet their local Qwen adaptive extraction yields diverge sharply. That two-role comparison is only a motivating observation, but it suggests label exposure alone cannot explain role-expression success or failure.",
            "",
            "This audit does not show that activation geometry is invalid or reducible to labels. It identifies a methodological variable that should be measured in later analyses, especially if comparing theatrical personas to assistant-adjacent personas.",
            "",
            "## Limitations",
            "",
            "The audit uses conservative string methods and does not detect semantic aliases unless they share the normalized role label or simple variants. It does not measure how strongly a prompt behaviorally describes a role, whether the role label is central or incidental, or how the generated model response uses the label. It also does not correlate label exposure with all 275 role-vector separability scores.",
            "",
            "## Recommended Next Audit",
            "",
            "Run a behavioral-specificity audit that removes the role label from each prompt and measures how much role-identifying content remains. A useful follow-up would compute lexical label exposure, behavioral cue density, and role-expression yield for each persona, then compare those against vector separability and assistant-axis position.",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
