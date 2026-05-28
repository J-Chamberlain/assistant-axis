#!/usr/bin/env python3
"""Normalize parsed Stage-1 role lists without semantic over-merging."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARSED_DIR = ROOT / "parsed_outputs"
OUTPUT_PATH = ROOT / "analysis" / "normalized_role_lists.json"
REQUIRED_PROVENANCE_FIELDS = [
    "task_type",
    "artifact_type",
    "artifact_path",
    "generation_model",
    "evaluation_model",
    "analysis_model",
    "script_author_model",
    "orchestration_agent",
    "provider",
    "model_version_or_alias",
    "date",
    "prompt_family_id",
    "temperature",
    "max_tokens",
    "source_inputs",
    "notes_on_uncertainty",
]


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_role_label(label: str) -> str:
    label = label.strip().lower()
    label = re.sub(r"[\u2010-\u2015-]+", "_", label)
    label = re.sub(r"[^a-z0-9_ /]+", "", label)
    label = label.replace("/", "_")
    label = re.sub(r"\s+", "_", label)
    label = re.sub(r"_+", "_", label)
    return label.strip("_")


def load_roles(path: Path) -> tuple[dict[str, Any], list[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    provenance = payload.get("model_provenance")
    if not isinstance(provenance, dict):
        raise ValueError(f"{path} missing required model_provenance object")
    missing = [field for field in REQUIRED_PROVENANCE_FIELDS if field not in provenance]
    if missing:
        raise ValueError(f"{path} model_provenance missing fields: {', '.join(missing)}")
    if not provenance.get("generation_model"):
        raise ValueError(f"{path} model_provenance.generation_model is required for role inventories")
    roles = payload.get("normalized_role_list") or payload.get("parsed_role_list") or []
    normalized = []
    seen = set()
    for role in roles:
        norm = normalize_role_label(str(role))
        if norm and norm not in seen:
            normalized.append(norm)
            seen.add(norm)
    return payload, normalized


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=PARSED_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    inventories = []
    errors = []
    global_counts: Counter[str] = Counter()
    by_role: dict[str, list[str]] = defaultdict(list)
    for path in sorted(args.input_dir.glob("*.json")):
        try:
            payload, roles = load_roles(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        provenance = payload["model_provenance"]
        inventory_id = f"{provenance['provider']}::{provenance['generation_model']}::{provenance['prompt_family_id']}"
        inventories.append(
            {
                "inventory_id": inventory_id,
                "source_path": str(path),
                "provider": provenance["provider"],
                "model": provenance["generation_model"],
                "prompt_family_id": provenance["prompt_family_id"],
                "model_provenance": provenance,
                "n_roles": len(roles),
                "normalized_role_list": roles,
            }
        )
        global_counts.update(roles)
        for role in roles:
            by_role[role].append(inventory_id)
    if errors:
        raise SystemExit("Invalid inventory provenance:\n" + "\n".join(f"- {error}" for error in errors))

    output = {
        "created_at": utc_timestamp(),
        "input_dir": str(args.input_dir),
        "n_inventories": len(inventories),
        "n_unique_roles": len(global_counts),
        "inventories": inventories,
        "role_counts": dict(sorted(global_counts.items(), key=lambda item: (-item[1], item[0]))),
        "role_sources": {role: sources for role, sources in sorted(by_role.items())},
        "normalization_policy": "Lowercase, punctuation cleanup, whitespace/hyphen to underscore, duplicate removal within inventory; no semantic merging.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} with {len(inventories)} inventories and {len(global_counts)} unique roles")


if __name__ == "__main__":
    main()
