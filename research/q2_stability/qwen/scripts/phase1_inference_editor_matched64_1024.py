#!/usr/bin/env python3
"""Matched editor token-cap sensitivity run.

Regenerates the first 64 `(sp_idx, q_idx)` pairs from the editor 128-rollout
chunk with `max_new_tokens=1024`. This script performs generation and
activation capture only; it never calls a judge model or scoring API.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer


LAYER = 48
DEVICE = "cuda"
MODEL_ID = "Qwen/Qwen3-32B"
HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ROOT = Path(os.environ.get("ASSISTANT_AXIS_REPO", "/root/assistant-axis"))
EXTRACTION_Q_PATH = REPO_ROOT / "data/extraction_questions.jsonl"
INSTRUCTIONS_DIR = REPO_ROOT / "data/roles/instructions"
MATCHED_SOURCE_JSONL = (
    REPO_ROOT
    / "research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase1_128.jsonl"
)
OUTPUT_DIR = (
    REPO_ROOT
    / "research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity"
)
ACTIVATION_DIR = OUTPUT_DIR / "activations_editor_1024"
OUTPUT_JSONL = OUTPUT_DIR / "editor_phase1_matched64_1024.jsonl"
MANIFEST_PATH = OUTPUT_DIR / "editor_phase1_matched64_1024_manifest.json"
PERSONA = "editor"
MAX_NEW_TOKENS = 1024
N_PAIRS = 64
LOG_EVERY = 8

THINK_OPEN = chr(60) + "think" + chr(62)
THINK_CLOSE = chr(60) + "/think" + chr(62)


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:12]


def has_think_artifact(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return THINK_OPEN in lowered or THINK_CLOSE in lowered


def load_matched_pairs() -> list[tuple[int, int]]:
    if not MATCHED_SOURCE_JSONL.exists():
        raise FileNotFoundError(MATCHED_SOURCE_JSONL)
    pairs: list[tuple[int, int]] = []
    with MATCHED_SOURCE_JSONL.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            pairs.append((int(row["sp_idx"]), int(row["q_idx"])))
            if len(pairs) == N_PAIRS:
                break
    if len(pairs) != N_PAIRS:
        raise RuntimeError(f"Expected {N_PAIRS} matched pairs, found {len(pairs)}")
    if len(set(pairs)) != N_PAIRS:
        raise RuntimeError("Matched source contains duplicate pairs in first 64 records")
    return pairs


def load_completed() -> set[tuple[int, int]]:
    completed: set[tuple[int, int]] = set()
    if not OUTPUT_JSONL.exists():
        return completed
    with OUTPUT_JSONL.open() as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                completed.add((int(row["sp_idx"]), int(row["q_idx"])))
            except Exception:
                continue
    return completed


def write_manifest(system_prompts: list[str], questions: list[str], matched_pairs: list[tuple[int, int]]) -> None:
    if MANIFEST_PATH.exists():
        return
    manifest = {
        "persona": PERSONA,
        "generation_model": MODEL_ID,
        "script_author_model": "GPT-5.5",
        "layer": LAYER,
        "token_cap": MAX_NEW_TOKENS,
        "max_new_tokens": MAX_NEW_TOKENS,
        "matched_against": str(MATCHED_SOURCE_JSONL.relative_to(REPO_ROOT)),
        "n_pairs": N_PAIRS,
        "purpose": "token_cap_sensitivity",
        "n_system_prompts": len(system_prompts),
        "n_questions": len(questions),
        "matched_pairs": [{"sp_idx": sp_idx, "q_idx": q_idx} for sp_idx, q_idx in matched_pairs],
        "transformers_version": transformers.__version__,
        "torch_version": torch.__version__,
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
        "instructions_hash": file_hash(INSTRUCTIONS_DIR / f"{PERSONA}.json"),
        "questions_hash": file_hash(EXTRACTION_Q_PATH),
        "matched_source_hash": file_hash(MATCHED_SOURCE_JSONL),
        "git_commit": os.popen("git rev-parse --short HEAD").read().strip(),
        "script": "phase1_inference_editor_matched64_1024.py",
        "start_time": time.time(),
        "enable_thinking": False,
        "use_cache_for_measurement": False,
        "phase": "1_inference_only_token_cap_sensitivity_no_judge",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    print("Manifest written.", flush=True)


def build_prompt(tokenizer: AutoTokenizer, system_prompt: str, question: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )


def extract_rollout(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    system_prompt: str,
    question: str,
) -> tuple[torch.Tensor | None, str, bool, bool]:
    prompt_text = build_prompt(tokenizer, system_prompt, question)
    inputs = tokenizer(prompt_text, return_tensors="pt").to(DEVICE)
    prompt_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        try:
            out = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                enable_thinking=False,
            )
        except (TypeError, ValueError):
            out = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
            )

    response_tokens = out[0][prompt_len:]
    response_text = tokenizer.decode(response_tokens, skip_special_tokens=True)
    truncated = len(response_tokens) >= MAX_NEW_TOKENS
    think_artifact = has_think_artifact(response_text)
    if think_artifact:
        return None, response_text, truncated, True

    captured: dict[str, torch.Tensor] = {}

    def hook_fn(module, inp, outp):  # noqa: ANN001
        captured["h"] = (outp[0] if isinstance(outp, tuple) else outp).detach().float().cpu()

    hook = model.model.layers[LAYER].register_forward_hook(hook_fn)
    with torch.no_grad():
        model(input_ids=out, use_cache=False)
    hook.remove()

    h = captured["h"][0]
    response_h = h[prompt_len:]
    if response_h.shape[0] == 0:
        return None, response_text, truncated, False
    return response_h.mean(0), response_text, truncated, False


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVATION_DIR.mkdir(parents=True, exist_ok=True)

    matched_pairs = load_matched_pairs()
    completed = load_completed()
    print(f"Resuming: {len(completed)} matched rollouts already done", flush=True)

    with (INSTRUCTIONS_DIR / f"{PERSONA}.json").open() as f:
        instructions = json.load(f)
    system_prompts = [item["pos"] for item in instructions["instruction"]]

    with EXTRACTION_Q_PATH.open() as f:
        questions = [json.loads(line)["question"] for line in f if line.strip()]

    write_manifest(system_prompts, questions, matched_pairs)

    if len(completed.intersection(matched_pairs)) >= N_PAIRS:
        print(f"Target already complete: {N_PAIRS}/{N_PAIRS}", flush=True)
        return

    print("Loading model...", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=HF_TOKEN,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    print(f"Model loaded in {time.time() - t0:.1f}s", flush=True)

    run_start = time.time()
    new_done = 0
    think_discards = 0
    truncation_count = 0

    with OUTPUT_JSONL.open("a") as f_out:
        for sp_idx, q_idx in matched_pairs:
            if (sp_idx, q_idx) in completed:
                continue

            activation, response_text, truncated, think_artifact = extract_rollout(
                model,
                tokenizer,
                system_prompts[sp_idx],
                questions[q_idx],
            )

            if think_artifact:
                think_discards += 1
            if truncated:
                truncation_count += 1

            record = {
                "persona": PERSONA,
                "generation_model": MODEL_ID,
                "script_author_model": "GPT-5.5",
                "sp_idx": sp_idx,
                "q_idx": q_idx,
                "matched_source": "editor_phase1_128.jsonl",
                "max_new_tokens": MAX_NEW_TOKENS,
                "response_text": response_text or "",
                "truncated": bool(truncated),
                "think_artifact": bool(think_artifact),
                "activation_saved": False,
                "activation_path": None,
                "activation_relpath": None,
                "timestamp": time.time(),
            }

            if activation is not None:
                act_fname = f"sp{sp_idx}_q{q_idx}.pt"
                act_path = ACTIVATION_DIR / act_fname
                torch.save(activation, act_path)
                record["activation_saved"] = True
                record["activation_path"] = str(act_path)
                record["activation_relpath"] = (
                    f"editor_token_cap_sensitivity/activations_editor_1024/{act_fname}"
                )

            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            f_out.flush()
            os.fsync(f_out.fileno())
            new_done += 1

            total_done = len(completed.intersection(matched_pairs)) + new_done
            if new_done % LOG_EVERY == 0 or total_done == N_PAIRS:
                elapsed = time.time() - run_start
                rate = elapsed / max(new_done, 1)
                remaining = N_PAIRS - total_done
                eta_min = (remaining * rate) / 60
                gpu_mem = torch.cuda.memory_allocated() / 1e9
                print(
                    f"[new={new_done} total={total_done}/{N_PAIRS}] "
                    f"think_discards={think_discards} truncated={truncation_count} "
                    f"rate={rate:.1f}s ETA={eta_min:.1f}min GPU={gpu_mem:.1f}GB",
                    flush=True,
                )

            if total_done >= N_PAIRS:
                break

    print(
        f"Editor matched64 1024-token run complete. new={new_done} "
        f"total={len(load_completed().intersection(matched_pairs))}/{N_PAIRS} "
        f"think_discards={think_discards} truncated={truncation_count}",
        flush=True,
    )


if __name__ == "__main__":
    main()
