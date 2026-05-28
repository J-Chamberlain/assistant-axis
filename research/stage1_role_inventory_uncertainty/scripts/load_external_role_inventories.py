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


def load_inventory(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    provenance = payload.get("model_provenance")
    if not isinstance(provenance, dict):
        raise ValueError(f"{path} missing required model_provenance object")
    missing = [field for field in REQUIRED_PROVENANCE_FIELDS if field not in provenance]
    if missing:
        raise ValueError(f"{path} model_provenance missing fields: {', '.join(missing)}")
    if not provenance.get("generation_model"):
        raise ValueError(f"{path} model_provenance.generation_model is required for role inventories")
    if not provenance.get("provider"):
        raise ValueError(f"{path} model_provenance.provider is required")
    if not provenance.get("prompt_family_id"):
        raise ValueError(f"{path} model_provenance.prompt_family_id is required")
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
    return {
        "source_path": str(path),
        "provider": provenance["provider"],
        "model": provenance["generation_model"],
        "prompt_family_id": provenance["prompt_family_id"],
        "timestamp": payload.get("timestamp") or provenance.get("date"),
        "model_provenance": provenance,
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
    errors = []
    for path in sorted(args.input_dir.glob("*.json")):
        try:
            inventories.append(load_inventory(path))
        except ValueError as exc:
            errors.append(str(exc))
    if errors:
        raise SystemExit("Invalid inventory provenance:\n" + "\n".join(f"- {error}" for error in errors))
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
