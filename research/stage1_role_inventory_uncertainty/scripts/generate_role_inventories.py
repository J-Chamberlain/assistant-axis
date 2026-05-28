#!/usr/bin/env python3
"""Generate Stage-1 role inventories with OpenAI models only.

This script intentionally does not orchestrate Anthropic calls. External
inventories from Claude or other providers should be synced into the repo and
ingested with load_external_role_inventories.py.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "prompts"
RAW_DIR = ROOT / "raw_outputs"
PARSED_DIR = ROOT / "parsed_outputs"

DEFAULT_MODELS = ["gpt-5.5", "gpt-5.5-thinking", "gpt-4.1-mini"]
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_OUTPUT_TOKENS = 6000
SCRIPT_AUTHOR_MODEL = "GPT-5.5 Standard via Codex"
ORCHESTRATION_AGENT = "Codex"


@dataclass(frozen=True)
class GenerationRun:
    model: str
    prompt_family_id: str
    prompt_path: Path
    prompt_text: str


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_")


def load_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    key_path = Path.home() / ".openai_api_key"
    if not key_path.exists():
        raise SystemExit("Missing OpenAI API key. Create ~/.openai_api_key or set OPENAI_API_KEY.")
    return key_path.read_text(encoding="utf-8").strip()


def load_prompt_family() -> list[tuple[str, Path, str]]:
    prompts = []
    for path in sorted(PROMPT_DIR.glob("prompt_family_*.txt")):
        prompts.append((path.stem, path, path.read_text(encoding="utf-8").strip()))
    if not prompts:
        raise SystemExit(f"No prompt family files found under {PROMPT_DIR}")
    return prompts


def parse_roles(raw_response: str) -> list[str]:
    roles: list[str] = []
    seen: set[str] = set()
    for line in raw_response.splitlines():
        item = line.strip()
        if not item:
            continue
        item = re.sub(r"^\s*[-*]\s+", "", item)
        item = re.sub(r"^\s*\d+[\).:-]\s*", "", item)
        item = item.strip("`'\" ")
        if not item:
            continue
        normalized = normalize_role_label(item)
        if normalized and normalized not in seen:
            roles.append(item)
            seen.add(normalized)
    return roles


def normalize_role_label(label: str) -> str:
    label = label.strip().lower()
    label = re.sub(r"[\u2010-\u2015-]+", "_", label)
    label = re.sub(r"[^a-z0-9_ /]+", "", label)
    label = label.replace("/", "_")
    label = re.sub(r"\s+", "_", label)
    label = re.sub(r"_+", "_", label)
    return label.strip("_")


def openai_responses_call(api_key: str, model: str, prompt: str, temperature: float, max_output_tokens: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": "You generate controlled research datasets. Follow formatting constraints exactly.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_response_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    return "\n".join(chunks).strip()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def model_provenance(
    *,
    artifact_type: str,
    artifact_path: Path,
    model: str,
    prompt_family_id: str,
    prompt_path: Path,
    timestamp: str,
    temperature: float,
    max_output_tokens: int,
) -> dict[str, Any]:
    return {
        "task_type": "role_inventory_generation",
        "artifact_type": artifact_type,
        "artifact_path": str(artifact_path),
        "generation_model": model,
        "evaluation_model": None,
        "analysis_model": None,
        "script_author_model": SCRIPT_AUTHOR_MODEL,
        "orchestration_agent": ORCHESTRATION_AGENT,
        "provider": "openai",
        "model_version_or_alias": model,
        "date": timestamp,
        "prompt_family_id": prompt_family_id,
        "temperature": temperature,
        "max_tokens": max_output_tokens,
        "source_inputs": [str(prompt_path)],
        "notes_on_uncertainty": "OpenAI-side Stage-1 generation only; Anthropic inventories are generated separately and synced through GitHub.",
    }


def run_generation(run: GenerationRun, api_key: str, args: argparse.Namespace) -> None:
    stamp = utc_timestamp()
    output_id = f"{slugify(run.model)}__{run.prompt_family_id}"
    raw_path = RAW_DIR / f"{output_id}.json"
    parsed_path = PARSED_DIR / f"{output_id}.json"
    if raw_path.exists() and parsed_path.exists() and not args.overwrite:
        print(f"SKIP existing {output_id}")
        return

    settings = {
        "provider": "openai",
        "model": run.model,
        "temperature": args.temperature,
        "max_output_tokens": args.max_output_tokens,
        "prompt_family_id": run.prompt_family_id,
        "prompt_path": str(run.prompt_path),
        "script_author_model": SCRIPT_AUTHOR_MODEL,
        "orchestration_agent": ORCHESTRATION_AGENT,
    }
    raw_provenance = model_provenance(
        artifact_type="raw_generation",
        artifact_path=raw_path,
        model=run.model,
        prompt_family_id=run.prompt_family_id,
        prompt_path=run.prompt_path,
        timestamp=stamp,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
    )
    parsed_provenance = model_provenance(
        artifact_type="parsed_inventory",
        artifact_path=parsed_path,
        model=run.model,
        prompt_family_id=run.prompt_family_id,
        prompt_path=run.prompt_path,
        timestamp=stamp,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
    )
    print(f"CALL {run.model} {run.prompt_family_id}")
    try:
        response = openai_responses_call(api_key, run.model, run.prompt_text, args.temperature, args.max_output_tokens)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        error_payload = {
            "timestamp": stamp,
            "status": "error",
            "error_type": "HTTPError",
            "http_status": exc.code,
            "error_body": body,
            "generation_settings": settings,
            "model_provenance": raw_provenance,
            "prompt_text": run.prompt_text,
        }
        write_json(raw_path, error_payload)
        print(f"ERROR {output_id}: HTTP {exc.code}")
        return
    except Exception as exc:  # noqa: BLE001
        error_payload = {
            "timestamp": stamp,
            "status": "error",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "generation_settings": settings,
            "model_provenance": raw_provenance,
            "prompt_text": run.prompt_text,
        }
        write_json(raw_path, error_payload)
        print(f"ERROR {output_id}: {type(exc).__name__}")
        return

    raw_text = extract_response_text(response)
    parsed_roles = parse_roles(raw_text)
    normalized_roles = [normalize_role_label(role) for role in parsed_roles]
    raw_payload = {
        "timestamp": stamp,
        "status": "ok",
        "generation_settings": settings,
        "model_provenance": raw_provenance,
        "prompt_text": run.prompt_text,
        "raw_response": raw_text,
        "api_response": response,
    }
    parsed_payload = {
        "timestamp": stamp,
        "status": "ok",
        "provider": "openai",
        "model": run.model,
        "prompt_family_id": run.prompt_family_id,
        "generation_settings": settings,
        "model_provenance": parsed_provenance,
        "raw_output_path": str(raw_path),
        "parsed_role_list": parsed_roles,
        "normalized_role_list": normalized_roles,
        "n_roles": len(parsed_roles),
        "n_normalized_unique_roles": len(set(normalized_roles)),
    }
    write_json(raw_path, raw_payload)
    write_json(parsed_path, parsed_payload)
    print(f"WROTE {output_id}: {len(parsed_roles)} roles")
    if args.sleep_seconds:
        time.sleep(args.sleep_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="*", default=DEFAULT_MODELS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="List planned calls without using the API.")
    args = parser.parse_args()

    prompts = load_prompt_family()
    runs = [GenerationRun(model, prompt_id, path, text) for model in args.models for prompt_id, path, text in prompts]
    print(f"Planned OpenAI runs: {len(runs)}")
    for run in runs:
        print(f"- {run.model} {run.prompt_family_id}")
    if args.dry_run:
        return

    api_key = load_api_key()
    for run in runs:
        run_generation(run, api_key, args)


if __name__ == "__main__":
    main()
