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
    global_counts: Counter[str] = Counter()
    by_role: dict[str, list[str]] = defaultdict(list)
    for path in sorted(args.input_dir.glob("*.json")):
        payload, roles = load_roles(path)
        inventory_id = f"{payload.get('provider', 'unknown')}::{payload.get('model', 'unknown')}::{payload.get('prompt_family_id', path.stem)}"
        inventories.append(
            {
                "inventory_id": inventory_id,
                "source_path": str(path),
                "provider": payload.get("provider", payload.get("generation_settings", {}).get("provider", "unknown")),
                "model": payload.get("model", payload.get("generation_settings", {}).get("model", "unknown")),
                "prompt_family_id": payload.get("prompt_family_id", path.stem),
                "n_roles": len(roles),
                "normalized_role_list": roles,
            }
        )
        global_counts.update(roles)
        for role in roles:
            by_role[role].append(inventory_id)

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
