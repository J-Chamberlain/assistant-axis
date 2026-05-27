#!/usr/bin/env python3
"""Create a no-label prompt-ablation dataset from canonical role prompts.

The rewrite is deterministic and local. It removes explicit target-role labels
with conservative rule-based transformations while preserving the surrounding
behavioral content as much as possible.
"""

from __future__ import annotations

import json
import re
import string
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INSTRUCTIONS_DIR = ROOT / "data/roles/instructions"
ROLE_LIST_PATH = ROOT / "data/roles/role_list.json"
LABEL_AUDIT_PATH = (
    ROOT / "research/assistant_axis_methodology/role_prompt_label_exposure_audit.json"
)
OUT_DIR = ROOT / "research/assistant_axis_methodology/no_label_prompt_ablation"
OUT_JSONL = OUT_DIR / "no_label_role_prompts.jsonl"
OUT_SAMPLES = OUT_DIR / "no_label_role_prompts_review_samples.md"
OUT_MANIFEST = OUT_DIR / "no_label_rewrite_manifest.json"


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
    return sorted((v for v in variants if v), key=len, reverse=True)


def has_label(role: str, text: str) -> bool:
    norm = normalize_text(text)
    for variant in role_variants(role):
        v = normalize_text(variant)
        if re.search(rf"\b{re.escape(v)}\b", norm):
            return True
    return False


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = re.sub(r"\bwho who\b", "who", text, flags=re.I)
    text = re.sub(r"\bthat that\b", "that", text, flags=re.I)
    text = re.sub(r"\bwith with\b", "with", text, flags=re.I)
    return text.strip()


def capitalize_start(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def rewrite_prompt(role: str, prompt: str) -> tuple[str, str]:
    rewritten = prompt.strip()
    notes: list[str] = []
    variants = [re.escape(normalize_text(v)) for v in role_variants(role)]

    # Apply broad normalized prefix transformations on a lowercase-normalized
    # copy, but preserve the original suffix text wherever possible by using
    # case-insensitive regexes against the original prompt.
    for raw_variant in role_variants(role):
        v = re.escape(raw_variant).replace("\\ ", r"[\s_-]+")
        article = r"(?:a|an|the)?"
        prefix_patterns = [
            (rf"^You are {article}\s*{v}\s+who\s+", "You "),
            (rf"^You are {article}\s*{v}\s+that\s+", "You "),
            (rf"^You are {article}\s*{v}\s+with\s+", "You bring "),
            (rf"^You are {article}\s*{v}\s+known for\s+", "You are known for "),
            (rf"^You are {article}\s*{v}\s+dedicated to\s+", "You are dedicated to "),
            (rf"^You are {article}\s*{v}\s+focused on\s+", "You focus on "),
            (rf"^You are {article}\s*{v}\s+skilled at\s+", "You are skilled at "),
            (rf"^You are {article}\s*{v}\s*,\s+", "You are "),
            (rf"^Please be {article}\s*{v}\s+who\s+", "You "),
            (rf"^Please be {article}\s*{v}\s+that\s+", "You "),
            (rf"^Please be {article}\s*{v}\s+with\s+", "Bring "),
            (rf"^Act as {article}\s*{v}\s+who\s+", "You "),
            (rf"^Act as {article}\s*{v}\s+that\s+", "You "),
            (rf"^Act as {article}\s*{v}\s+with\s+", "Bring "),
            (rf"^Act as {article}\s*{v}\s*,\s+", "Work from "),
            (rf"^Be {article}\s*{v}\s+who\s+", "You "),
            (rf"^Be {article}\s*{v}\s+that\s+", "You "),
            (rf"^Take on the role of {article}\s*{v}\s+who\s+", "Use "),
            (rf"^Take on the role of {article}\s*{v}\s+that\s+", "Use "),
            (rf"^Embody the role of {article}\s*{v}\s+who\s+", "Use "),
            (rf"^Embody {article}\s*{v}\s+who\s+", "Use "),
            (rf"^Please respond as {article}\s*{v}\s+entity\s*[-,]\s*", "Respond as a collective entity, "),
            (rf"^Please respond as {article}\s*{v}\s*[-,]\s*", "Respond from "),
        ]
        changed = True
        while changed:
            changed = False
            for pattern, replacement in prefix_patterns:
                new = re.sub(pattern, replacement, rewritten, count=1, flags=re.I)
                if new != rewritten:
                    rewritten = new
                    notes.append("prefix_identity_frame_removed")
                    changed = True

    # Remove remaining explicit target labels, preserving grammar with a neutral
    # reference only when the label appears as a noun phrase.
    for raw_variant in role_variants(role):
        v = re.escape(raw_variant).replace("\\ ", r"[\s_-]+")
        before = rewritten
        rewritten = re.sub(rf"\b(?:a|an|the)\s+{v}\b", "someone", rewritten, flags=re.I)
        rewritten = re.sub(rf"\b{v}\b", "", rewritten, flags=re.I)
        if rewritten != before:
            notes.append("residual_label_removed")

    rewritten = clean_text(rewritten)
    if rewritten.lower().startswith("you uses "):
        rewritten = "You use " + rewritten[9:]
    if rewritten.lower().startswith("use uses "):
        rewritten = "Use " + rewritten[9:]
    rewritten = capitalize_start(rewritten)

    if not rewritten:
        rewritten = prompt
        notes.append("rewrite_empty_reverted")

    status = "ok"
    if has_label(role, rewritten):
        status = "needs_review_label_remaining"
    elif len(rewritten.split()) < max(4, len(prompt.split()) * 0.35):
        status = "needs_review_possible_overflattening"
    return rewritten, "; ".join(dict.fromkeys(notes)) or "unchanged_no_label_detected"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    roles = json.loads(ROLE_LIST_PATH.read_text())
    label_audit = json.loads(LABEL_AUDIT_PATH.read_text())
    audit_by_role = {row["role"]: row for row in label_audit["roles"]}
    records = []

    with OUT_JSONL.open("w") as f:
        for role, description in roles.items():
            path = INSTRUCTIONS_DIR / f"{role}.json"
            data = json.loads(path.read_text())
            prompts = [item.get("pos", "") for item in data.get("instruction", [])]
            audit_role = audit_by_role.get(role, {})
            for idx, prompt in enumerate(prompts):
                rewritten, notes = rewrite_prompt(role, prompt)
                original_exposed = False
                if audit_role:
                    original_exposed = audit_role["prompts"][idx][
                        "normalized_role_label_or_variant_appears"
                    ]
                rewritten_exposed = has_label(role, rewritten)
                status = "ok" if not rewritten_exposed else "needs_review_label_remaining"
                if "needs_review_possible_overflattening" in notes:
                    status = "needs_review_possible_overflattening"
                rec = {
                    "role": role,
                    "role_description": description,
                    "prompt_index": idx,
                    "original_prompt": prompt,
                    "rewritten_prompt": rewritten,
                    "role_label": role,
                    "original_had_label_exposure": original_exposed,
                    "rewritten_has_label_exposure": rewritten_exposed,
                    "rewrite_status": status,
                    "notes": notes,
                    "script_author_model": "GPT-5.5",
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                records.append(rec)

    manifest = {
        "date": "2026-05-27",
        "model_used": "GPT-5.5",
        "method": "deterministic_minimal_label_ablation",
        "input_role_instruction_dir": str(INSTRUCTIONS_DIR.relative_to(ROOT)),
        "input_role_list": str(ROLE_LIST_PATH.relative_to(ROOT)),
        "input_label_exposure_audit": str(LABEL_AUDIT_PATH.relative_to(ROOT)),
        "output_jsonl": str(OUT_JSONL.relative_to(ROOT)),
        "n_roles": len(roles),
        "n_prompts": len(records),
        "rewrite_status_counts": count_by(records, "rewrite_status"),
        "rewritten_label_exposure_count": sum(r["rewritten_has_label_exposure"] for r in records),
        "notes": "Rule-based local rewrite removes explicit role labels and obvious normalized variants while preserving behavioral content as closely as possible. No external API calls were used.",
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    OUT_SAMPLES.write_text(render_samples(records) + "\n")
    print(json.dumps(manifest, indent=2))


def count_by(records: list[dict], key: str) -> dict:
    out: dict[str, int] = {}
    for rec in records:
        out[rec[key]] = out.get(rec[key], 0) + 1
    return dict(sorted(out.items()))


def render_samples(records: list[dict]) -> str:
    special_roles = [
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
    ]
    lines = [
        "# No-Label Role Prompt Rewrite Review Samples",
        "",
        "These samples are generated by `rewrite_role_prompts_no_label_codex_gpt55.py` for quick human inspection.",
        "",
    ]
    for role in special_roles:
        subset = [r for r in records if r["role"] == role]
        if not subset:
            continue
        lines.append(f"## {role}")
        lines.append("")
        for rec in subset:
            lines.append(f"### Prompt {rec['prompt_index']}")
            lines.append("")
            lines.append(f"Original: {rec['original_prompt']}")
            lines.append("")
            lines.append(f"Rewrite: {rec['rewritten_prompt']}")
            lines.append("")
            lines.append(
                f"Status: {rec['rewrite_status']}; rewritten label exposure: {rec['rewritten_has_label_exposure']}; notes: {rec['notes']}"
            )
            lines.append("")
    flagged = [r for r in records if r["rewrite_status"] != "ok"][:50]
    lines.append("## Flagged Records")
    lines.append("")
    if not flagged:
        lines.append("No flagged records.")
    for rec in flagged:
        lines.append(
            f"- `{rec['role']}` prompt {rec['prompt_index']}: {rec['rewrite_status']} | {rec['rewritten_prompt']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
