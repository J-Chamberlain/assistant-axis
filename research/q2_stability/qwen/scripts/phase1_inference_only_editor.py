#!/usr/bin/env python3
"""Qwen editor Phase 1 inference-only extraction, first adaptive chunk.

This pod script performs generation and hidden-state capture only. It never
calls a judge model or external scoring API.
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
OUTPUT_DIR = REPO_ROOT / "research/q2_stability/qwen/outputs/paper1_5/editor"
ACTIVATION_DIR = OUTPUT_DIR / "activations_editor"
OUTPUT_JSONL = OUTPUT_DIR / "editor_phase1_128.jsonl"
MANIFEST_PATH = OUTPUT_DIR / "editor_phase1_128_manifest.json"
PERSONA = "editor"
MAX_NEW_TOKENS = 512
MAX_ROLLOUTS = 128
LOG_EVERY = 16

THINK_OPEN = chr(60) + "think" + chr(62)
THINK_CLOSE = chr(60) + "/think" + chr(62)


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()[:12]


def has_think_artifact(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return THINK_OPEN in lowered or THINK_CLOSE in lowered


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


def write_manifest(system_prompts: list[str], questions: list[str]) -> None:
    if MANIFEST_PATH.exists():
        return
    manifest = {
        "persona": PERSONA,
        "generation_model": MODEL_ID,
        "script_author_model": "GPT-5.5",
        "layer": LAYER,
        "max_new_tokens": MAX_NEW_TOKENS,
        "max_rollouts": MAX_ROLLOUTS,
        "n_system_prompts": len(system_prompts),
        "n_questions": len(questions),
        "rollout_selection": "first 128 stable-order (sp_idx, q_idx) pairs",
        "transformers_version": transformers.__version__,
        "torch_version": torch.__version__,
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
        "instructions_hash": file_hash(INSTRUCTIONS_DIR / f"{PERSONA}.json"),
        "questions_hash": file_hash(EXTRACTION_Q_PATH),
        "git_commit": os.popen("git rev-parse --short HEAD").read().strip(),
        "script": "phase1_inference_only_editor.py",
        "start_time": time.time(),
        "enable_thinking": False,
        "use_cache_for_measurement": False,
        "phase": "1_inference_only_no_judge",
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

    activation = response_h.mean(0)
    return activation, response_text, truncated, False


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVATION_DIR.mkdir(parents=True, exist_ok=True)

    completed = load_completed()
    print(f"Resuming: {len(completed)} rollouts already done", flush=True)

    with (INSTRUCTIONS_DIR / f"{PERSONA}.json").open() as f:
        instructions = json.load(f)
    system_prompts = [item["pos"] for item in instructions["instruction"]]

    with EXTRACTION_Q_PATH.open() as f:
        questions = [json.loads(line)["question"] for line in f if line.strip()]

    target_pairs = [
        (sp_idx, q_idx)
        for sp_idx in range(len(system_prompts))
        for q_idx in range(len(questions))
    ][:MAX_ROLLOUTS]

    write_manifest(system_prompts, questions)

    if len(completed.intersection(target_pairs)) >= MAX_ROLLOUTS:
        print(f"Target already complete: {MAX_ROLLOUTS}/{MAX_ROLLOUTS}", flush=True)
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
        for sp_idx, q_idx in target_pairs:
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
                record["activation_relpath"] = f"editor/activations_editor/{act_fname}"

            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            f_out.flush()
            os.fsync(f_out.fileno())
            new_done += 1

            total_done = len(completed.intersection(target_pairs)) + new_done
            if new_done % LOG_EVERY == 0 or total_done == MAX_ROLLOUTS:
                elapsed = time.time() - run_start
                rate = elapsed / max(new_done, 1)
                remaining = MAX_ROLLOUTS - total_done
                eta_min = (remaining * rate) / 60
                gpu_mem = torch.cuda.memory_allocated() / 1e9
                print(
                    f"[new={new_done} total={total_done}/{MAX_ROLLOUTS}] "
                    f"think_discards={think_discards} truncated={truncation_count} "
                    f"rate={rate:.1f}s ETA={eta_min:.1f}min GPU={gpu_mem:.1f}GB",
                    flush=True,
                )

            if total_done >= MAX_ROLLOUTS:
                break

    print(
        f"Editor Phase 1 chunk complete. new={new_done} "
        f"total={len(load_completed().intersection(target_pairs))}/{MAX_ROLLOUTS} "
        f"think_discards={think_discards} truncated={truncation_count}",
        flush=True,
    )


if __name__ == "__main__":
    main()
