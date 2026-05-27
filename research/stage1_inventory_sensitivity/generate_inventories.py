#!/usr/bin/env python3
"""Generate persona inventories across frontier models and prompt variants.

Stage 1 sensitivity analysis: how invariant is the large-scale semantic manifold
under reasonable generator and prompt variation?

Usage:
    python generate_inventories.py [--runs 3] [--models m1,m2] [--prompts p1,p2] [--dry-run]

Output: runs/runs.jsonl  (one JSON record per line; idempotent — skips completed cells)

Temperature note: all models run at temperature=1.0 (API-neutral default).
OpenAI reasoning models (o-series) ignore temperature; the value is passed but has no effect.
OpenAI runs also receive seed=42+run_index for reproducibility where supported.
Anthropic API does not support a seed parameter; within-model variance is unsuppressed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS_JSONL = HERE / "runs" / "runs.jsonl"
PROMPTS_FILE = HERE / "prompts.json"
MODELS_FILE = HERE / "models.json"


# ---------------------------------------------------------------------------
# API key resolution
# ---------------------------------------------------------------------------

def _load_key(env_var: str, fallback_file: str) -> str | None:
    key = os.environ.get(env_var)
    if key:
        return key.strip()
    path = Path(fallback_file).expanduser()
    if path.exists():
        return path.read_text().strip()
    return None


# ---------------------------------------------------------------------------
# Role list parser
# ---------------------------------------------------------------------------

def parse_roles(text: str) -> tuple[list[str], str]:
    """Parse free-text role output into a normalized list.

    Returns (roles, parse_method) where parse_method is a diagnostic tag.
    Normalization: lowercase, strip whitespace, deduplicate, drop blank or
    overly long tokens (>80 chars).
    """
    text = text.strip()

    # 1. JSON array
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            roles = _clean([str(r) for r in parsed])
            return roles, "json_array"
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. Numbered list: "1. Role" or "1) Role"
    numbered = re.findall(r"^\s*\d+[.)]\s+(.+)", text, re.MULTILINE)
    if len(numbered) >= 10:
        return _clean(numbered), "numbered_list"

    # 3. Bulleted list: "- Role" or "* Role" or "• Role"
    bulleted = re.findall(r"^\s*[-*•]\s+(.+)", text, re.MULTILINE)
    if len(bulleted) >= 10:
        return _clean(bulleted), "bulleted_list"

    # 4. Comma-separated single line
    if "," in text and text.count("\n") < 5:
        roles = _clean(text.split(","))
        if len(roles) >= 10:
            return roles, "comma_separated"

    # 5. Line-by-line fallback — strip list markers and cluster headers
    lines = text.split("\n")
    cleaned = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        # Drop cluster headers like "[PROFESSIONAL]" or "## Category"
        if re.match(r"^(\[.*\]|#{1,3}\s|[A-Z][A-Z\s/&]+:?\s*$)", ln):
            continue
        # Strip leading markers
        ln = re.sub(r"^[\d.)\-*•\s]+", "", ln).strip()
        if ln:
            cleaned.append(ln)
    return _clean(cleaned), "line_fallback"


def _clean(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        norm = item.strip().lower()
        # Drop trailing punctuation artifacts
        norm = re.sub(r"[;,.:]+$", "", norm).strip()
        if norm and len(norm) <= 80 and norm not in seen:
            seen.add(norm)
            out.append(norm)
    return out


# ---------------------------------------------------------------------------
# API callers
# ---------------------------------------------------------------------------

def _call_anthropic(model_id: str, prompt: str, params: dict, api_key: str) -> str:
    try:
        import anthropic
    except ImportError:
        sys.exit(
            "anthropic package not installed.\n"
            "Run: pip install anthropic\n"
            "Or: uv add anthropic"
        )
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model_id,
        max_tokens=params["max_tokens"],
        temperature=params["temperature"],
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def _call_openai(model_id: str, prompt: str, params: dict, api_key: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai package not installed. Run: pip install openai")
    client = OpenAI(api_key=api_key)
    kwargs: dict[str, Any] = dict(
        model=model_id,
        max_tokens=params["max_tokens"],
        messages=[{"role": "user", "content": prompt}],
    )
    # o-series models require temperature=1 (API enforces it); omit for safety
    if not model_id.startswith("o"):
        kwargs["temperature"] = params["temperature"]
    if "seed" in params:
        kwargs["seed"] = params["seed"]
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


def call_model(
    model_cfg: dict,
    prompt: str,
    params: dict,
    anthropic_key: str | None,
    openai_key: str | None,
) -> str:
    provider = model_cfg["provider"]
    model_id = model_cfg["model_id"]
    if provider == "anthropic":
        if not anthropic_key:
            raise RuntimeError(
                "No Anthropic API key found. Set ANTHROPIC_API_KEY or create ~/.anthropic_api_key"
            )
        return _call_anthropic(model_id, prompt, params, anthropic_key)
    if provider == "openai":
        if not openai_key:
            raise RuntimeError(
                "No OpenAI API key found. Set OPENAI_API_KEY or create ~/.openai_api_key"
            )
        return _call_openai(model_id, prompt, params, openai_key)
    raise ValueError(f"Unknown provider: {provider}")


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

def _load_completed_keys() -> set[tuple[str, str, int]]:
    done: set[tuple[str, str, int]] = set()
    if not RUNS_JSONL.exists():
        return done
    with open(RUNS_JSONL) as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get("status") == "ok":
                    done.add((rec["model_id"], rec["prompt_id"], rec["run_index"]))
            except (json.JSONDecodeError, KeyError):
                continue
    return done


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=int, default=3, help="Runs per (model × prompt) cell")
    parser.add_argument("--models", type=str, help="Comma-separated model_ids to include")
    parser.add_argument("--prompts", type=str, help="Comma-separated prompt_ids to include")
    parser.add_argument("--temperature", type=float, default=1.0, help="Sampling temperature (default 1.0)")
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--dry-run", action="store_true", help="Print plan without calling APIs")
    args = parser.parse_args()

    all_prompts: list[dict] = json.loads(PROMPTS_FILE.read_text())
    all_models: list[dict] = json.loads(MODELS_FILE.read_text())

    if args.prompts:
        pfilter = set(args.prompts.split(","))
        all_prompts = [p for p in all_prompts if p["prompt_id"] in pfilter]
    if args.models:
        mfilter = set(args.models.split(","))
        all_models = [m for m in all_models if m["model_id"] in mfilter]

    if not all_prompts:
        sys.exit("No prompts matched filter.")
    if not all_models:
        sys.exit("No models matched filter.")

    anthropic_key = _load_key("ANTHROPIC_API_KEY", "~/.anthropic_api_key")
    openai_key = _load_key("OPENAI_API_KEY", "~/.openai_api_key")

    base_params = {"temperature": args.temperature, "max_tokens": args.max_tokens}
    total = len(all_models) * len(all_prompts) * args.runs

    print(f"Plan: {len(all_models)} models × {len(all_prompts)} prompts × {args.runs} runs = {total} API calls")
    for m in all_models:
        key_status = "key OK" if (
            (m["provider"] == "anthropic" and anthropic_key) or
            (m["provider"] == "openai" and openai_key)
        ) else "NO KEY"
        print(f"  {m['provider']:10s}  {m['model_id']}  [{key_status}]")
    print("Prompts:")
    for p in all_prompts:
        print(f"  {p['prompt_id']}: {p['description']}")

    if args.dry_run:
        print("\n[DRY RUN] Exiting without API calls.")
        return

    RUNS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    completed_keys = _load_completed_keys()

    n_completed = 0
    n_skipped = 0
    n_failed = 0

    for model_cfg in all_models:
        for prompt_cfg in all_prompts:
            for run_idx in range(args.runs):
                mid = model_cfg["model_id"]
                pid = prompt_cfg["prompt_id"]
                cell_key = (mid, pid, run_idx)

                if cell_key in completed_keys:
                    print(f"  SKIP {mid} × {pid} run {run_idx}")
                    n_skipped += 1
                    continue

                print(f"  RUN  {mid} × {pid} run {run_idx} ... ", end="", flush=True)

                params = dict(base_params)
                if model_cfg["provider"] == "openai":
                    params["seed"] = 42 + run_idx

                raw_response: str | None = None
                error_msg: str | None = None
                t0 = time.time()

                for attempt in range(4):
                    try:
                        raw_response = call_model(model_cfg, prompt_cfg["text"], params, anthropic_key, openai_key)
                        break
                    except Exception as exc:
                        error_msg = str(exc)
                        if attempt < 3:
                            wait = 2 ** (attempt + 1)
                            print(f"retry({attempt + 1}, {wait}s) ", end="", flush=True)
                            time.sleep(wait)

                elapsed = time.time() - t0

                if raw_response is None:
                    print(f"FAILED ({elapsed:.1f}s): {error_msg}")
                    record: dict[str, Any] = {
                        "run_id": str(uuid.uuid4()),
                        "experiment_id": "persona_inventory_sensitivity_v1",
                        "model_id": mid,
                        "provider": model_cfg["provider"],
                        "prompt_id": pid,
                        "run_index": run_idx,
                        "generation_params": params,
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "status": "failed",
                        "error": error_msg,
                        "raw_response": None,
                        "roles_parsed": [],
                        "roles_count": 0,
                        "parse_method": None,
                    }
                    n_failed += 1
                else:
                    roles, parse_method = parse_roles(raw_response)
                    print(f"ok ({elapsed:.1f}s, {len(roles)} roles, {parse_method})")
                    record = {
                        "run_id": str(uuid.uuid4()),
                        "experiment_id": "persona_inventory_sensitivity_v1",
                        "model_id": mid,
                        "provider": model_cfg["provider"],
                        "prompt_id": pid,
                        "run_index": run_idx,
                        "generation_params": params,
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        "status": "ok",
                        "error": None,
                        "raw_response": raw_response,
                        "roles_parsed": roles,
                        "roles_count": len(roles),
                        "parse_method": parse_method,
                    }
                    n_completed += 1

                with open(RUNS_JSONL, "a") as f:
                    f.write(json.dumps(record) + "\n")

    print(f"\nDone: {n_completed} completed, {n_skipped} skipped, {n_failed} failed")
    print(f"Output: {RUNS_JSONL}")


if __name__ == "__main__":
    main()
