#!/usr/bin/env python3
"""Ingest provider-generated role inventories into a common normalized schema."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARSED_DIR = ROOT / "parsed_outputs"
OUTPUT_PATH = ROOT / "analysis" / "combined_role_inventories.json"


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


def load_inventory(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    roles = (
        payload.get("normalized_role_list")
        or payload.get("parsed_role_list")
        or payload.get("roles")
        or payload.get("role_list")
        or []
    )
    if isinstance(roles, str):
        roles = [line.strip() for line in roles.splitlines() if line.strip()]
    normalized = []
    seen = set()
    for role in roles:
        norm = normalize_role_label(str(role))
        if norm and norm not in seen:
            normalized.append(norm)
            seen.add(norm)
    provider = payload.get("provider") or payload.get("generation_settings", {}).get("provider") or "external"
    model = payload.get("model") or payload.get("generation_settings", {}).get("model") or "unknown"
    prompt_family_id = payload.get("prompt_family_id") or payload.get("generation_settings", {}).get("prompt_family_id") or path.stem
    return {
        "source_path": str(path),
        "provider": provider,
        "model": model,
        "prompt_family_id": prompt_family_id,
        "timestamp": payload.get("timestamp"),
        "n_roles": len(normalized),
        "normalized_role_list": normalized,
        "schema_note": "Common Stage-1 inventory schema; source may be OpenAI, Claude via GitHub sync, or manual.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=PARSED_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    inventories = []
    for path in sorted(args.input_dir.glob("*.json")):
        inventories.append(load_inventory(path))
    payload = {
        "created_at": utc_timestamp(),
        "input_dir": str(args.input_dir),
        "n_inventories": len(inventories),
        "inventories": inventories,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} with {len(inventories)} inventories")


if __name__ == "__main__":
    main()
