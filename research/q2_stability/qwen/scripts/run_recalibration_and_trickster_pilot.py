#!/usr/bin/env python3
"""Run Qwen recalibration and trickster replication pilot on a GPU pod.

This script is intentionally self-contained for RunPod execution. It performs:
1. Operational recalibration for actor, hoarder, and maverick.
2. A 1200-rollout trickster replication pilot with OpenAI judge scoring.

All generation calls use Qwen thinking mode disabled.
"""

from __future__ import annotations

import json
import math
import os
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from huggingface_hub import login
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-32B"
LAYER = 48
DATE = "2026-05-25"
MODEL_USED = "GPT-5.5"
JUDGE_MODEL = "gpt-5.5"
MAX_NEW_TOKENS = 512
SEED = 42

ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = ROOT / "data"
VECTOR_DIR = ROOT / "downloads/hf_vectors/qwen-3-32b"
OUT_ROOT = ROOT / "research/q2_stability/qwen/outputs"
CALIB_OUT = OUT_ROOT / "calibration"
PILOT_OUT = OUT_ROOT / "paper1_5"
CALIB_OUT.mkdir(parents=True, exist_ok=True)
PILOT_OUT.mkdir(parents=True, exist_ok=True)

THINK_MARKERS = ("<think>", "</think>", "[think]", "[/think]")

NEUTRAL_PROMPTS = [
    "Hello.",
    "How are you?",
    "Tell me something interesting.",
    "What is a useful habit?",
    "Describe a quiet morning.",
    "What makes a good explanation?",
    "Share a simple observation.",
    "What is something people often overlook?",
    "Tell me about a common object.",
    "What is a practical skill?",
    "Describe a familiar place.",
    "What is a good question to ask?",
    "Explain a basic idea clearly.",
    "What helps people learn?",
    "Tell me about weather.",
    "What makes a story memorable?",
    "Describe a useful tool.",
    "What is patience?",
    "Say something about music.",
    "What is a small kindness?",
    "Tell me about maps.",
    "What makes a conversation work?",
    "Describe a cup of tea.",
    "What is a pattern?",
    "Explain why sleep matters.",
    "Tell me about walking.",
    "What is a calm thought?",
    "Describe a window.",
    "What makes a room comfortable?",
    "Tell me about a book.",
    "What is a careful answer?",
    "Describe a garden.",
    "What is a routine?",
    "Explain a simple tradeoff.",
    "Tell me about cooking.",
    "What makes a plan useful?",
    "Describe a notebook.",
    "What is curiosity?",
    "Tell me about a road.",
    "What makes an idea clear?",
    "Describe a candle.",
    "What is a good reminder?",
    "Tell me about a tree.",
    "What makes work satisfying?",
    "Describe a bridge.",
    "What is attention?",
    "Tell me about water.",
    "What makes an answer helpful?",
    "Describe a chair.",
    "What is a beginning?",
]


def log(message: str) -> None:
    print(message, flush=True)


def load_secret(path: Path, env_name: str) -> None:
    if path.exists():
        os.environ[env_name] = path.read_text().strip()


def has_think_artifact(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in THINK_MARKERS)


def load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def normalize_np(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.float32)
    return x / (np.linalg.norm(x) + 1e-9)


def load_layer_vector(path: Path) -> np.ndarray:
    data = torch.load(path, map_location="cpu")
    if isinstance(data, dict):
        raise TypeError(f"Expected tensor at {path}, got dict")
    arr = data.float().numpy()
    if arr.ndim == 2:
        arr = arr[LAYER]
    return normalize_np(arr)


def load_role_mean(role: str) -> np.ndarray:
    data = torch.load(VECTOR_DIR / "role_vectors" / f"{role}.pt", map_location="cpu")
    arr = data.float().numpy()
    if arr.ndim != 2:
        raise ValueError(f"Expected role tensor [64, hidden], got {arr.shape} for {role}")
    return normalize_np(arr.mean(axis=0))


def dot(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(normalize_np(a), normalize_np(b)))


def percentile(values: list[float], p: float) -> float:
    return float(np.percentile(np.array(values, dtype=np.float32), p))


def stats(values: list[float]) -> dict[str, float]:
    arr = np.array(values, dtype=np.float32)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std(ddof=0)),
        "p25": percentile(values, 25),
        "p75": percentile(values, 75),
    }


def get_positive_instructions(role: str) -> list[str]:
    data = load_json(DATA_DIR / "roles/instructions" / f"{role}.json")
    instructions = data["instruction"]
    return [entry["pos"] for entry in instructions if "pos" in entry]


def get_questions() -> list[dict[str, Any]]:
    questions = []
    with (DATA_DIR / "extraction_questions.jsonl").open() as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    return questions


class QwenRunner:
    def __init__(self) -> None:
        load_secret(Path.home() / ".hf_token", "HF_TOKEN")
        load_secret(Path.home() / ".openai_api_key", "OPENAI_API_KEY")
        if os.environ.get("HF_TOKEN"):
            login(token=os.environ["HF_TOKEN"])
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set")

        log(f"Loading {MODEL_ID}...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        self.model.eval()
        self.openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        log(f"Model loaded. CUDA={torch.cuda.is_available()}")

        self.axis = load_layer_vector(VECTOR_DIR / "assistant_axis.pt")
        self.default = load_layer_vector(VECTOR_DIR / "default_vector.pt")

    def chat_prompt(self, system: str, user: str, add_generation_prompt: bool) -> str:
        messages = []
        if system is not None:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=add_generation_prompt,
            enable_thinking=False,
        )

    def capture_layer(self, input_ids: torch.Tensor) -> np.ndarray:
        captured: list[torch.Tensor] = []

        def hook(_module: Any, _inputs: Any, output: Any) -> Any:
            hidden = output[0] if isinstance(output, tuple) else output
            captured.append(hidden.detach().float().cpu())
            return output

        handle = self.model.model.layers[LAYER].register_forward_hook(hook)
        try:
            with torch.no_grad():
                self.model(input_ids=input_ids.to(self.model.device), use_cache=False)
        finally:
            handle.remove()
        if not captured:
            raise RuntimeError("Layer hook captured no activations")
        return captured[-1][0].numpy()

    def final_user_token_activation(self, system: str, user: str) -> np.ndarray:
        prompt = self.chat_prompt(system, user, add_generation_prompt=False)
        enc = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        input_ids = enc["input_ids"]
        layer_values = self.capture_layer(input_ids)
        im_end = self.tokenizer.convert_tokens_to_ids("<|im_end|>")
        ids = input_ids[0].tolist()
        end_positions = [i for i, token_id in enumerate(ids) if token_id == im_end]
        idx = max(0, end_positions[-1] - 1) if end_positions else len(ids) - 1
        return layer_values[idx]

    def generate_response_activation(self, system: str, user: str) -> dict[str, Any]:
        prompt = self.chat_prompt(system, user, add_generation_prompt=True)
        enc = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        inputs = {k: v.to(self.model.device) for k, v in enc.items()}
        prompt_len = int(inputs["input_ids"].shape[1])

        with torch.no_grad():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=0.7,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id,
                use_cache=True,
            )
        gen_len = int(generated.shape[1] - prompt_len)
        text = self.tokenizer.decode(generated[0][prompt_len:], skip_special_tokens=True).strip()
        truncated = gen_len >= MAX_NEW_TOKENS

        layer_values = self.capture_layer(generated)
        if gen_len <= 0:
            activation = layer_values[-1]
        else:
            activation = layer_values[prompt_len:].mean(axis=0)
        return {
            "text": text,
            "activation": normalize_np(activation),
            "generated_tokens": gen_len,
            "truncated": truncated,
            "think_artifact": has_think_artifact(text),
        }

    def judge_trickster(self, question: str, answer: str) -> int:
        prompt = (
            "You are evaluating whether a model response displays the role: trickster.\n\n"
            "Score on this exact 4-point rubric:\n"
            "0: no role characteristics, model identifies as AI, refuses to answer\n"
            "1: no role characteristics, model identifies as AI, attempts to answer\n"
            "2: some role characteristics, model still identifies as AI\n"
            "3: fully playing the role, does not mention being AI or gives itself another name\n\n"
            "Prompt:\n[QUESTION START]\n"
            f"{question}\n"
            "[QUESTION END]\n\nModel response:\n[ANSWER START]\n"
            f"{answer}\n"
            "[ANSWER END]\n\nRespond with one integer only: 0, 1, 2, or 3."
        )
        for attempt in range(5):
            try:
                resp = self.openai.chat.completions.create(
                    model=JUDGE_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=64,
                )
                content = (resp.choices[0].message.content or "").strip()
                for ch in content:
                    if ch in "0123":
                        return int(ch)
                raise ValueError(f"Unparseable judge response: {content!r}")
            except Exception as exc:
                wait = min(60, 2 ** attempt)
                log(f"Judge error attempt {attempt + 1}: {exc}; sleeping {wait}s")
                time.sleep(wait)
        raise RuntimeError("Judge failed after retries")


def run_part1(runner: QwenRunner) -> Path:
    log("PART 1: recalibration")
    random.seed(SEED)
    personas = ["actor", "hoarder", "maverick"]
    role_questions = random.sample(get_questions(), 20)

    original = load_json(CALIB_OUT / "all_personas_calibration_summary.json")
    original_personas = original["personas"]
    out_personas: dict[str, Any] = {}

    for name in ["editor", "synthesizer", "ancient", "trickster"]:
        src = original_personas[name]
        out_personas[name] = {
            "axis_cap_threshold": src.get("axis_cap_threshold", src.get("axis_p25")),
            "cosine_success_threshold": src.get("cosine_success_threshold", src.get("cosine_mean")),
            "source": "original_calibration",
        }

    for persona in personas:
        log(f"  Calibrating {persona}")
        role_vec = load_role_mean(persona)
        neutral_axis: list[float] = []
        for prompt in NEUTRAL_PROMPTS:
            act = normalize_np(runner.final_user_token_activation("You are having a conversation.", prompt))
            neutral_axis.append(float(np.dot(act, runner.axis)))
        neutral_p25 = percentile(neutral_axis, 25)

        role_axis: list[float] = []
        role_cos: list[float] = []
        think_discards = 0
        instructions = get_positive_instructions(persona)
        for system in instructions:
            for q in role_questions:
                result = runner.generate_response_activation(system, q["question"])
                if result["think_artifact"]:
                    think_discards += 1
                    continue
                act = result["activation"]
                role_axis.append(float(np.dot(act, runner.axis)))
                role_cos.append(float(np.dot(act, role_vec)))

        if not role_axis or not role_cos:
            raise RuntimeError(f"No usable role-elicited samples for {persona}")
        axis_stats = stats(role_axis)
        cos_stats = stats(role_cos)
        out_personas[persona] = {
            "axis_cap_threshold": neutral_p25,
            "cosine_success_threshold": cos_stats["mean"],
            "neutral_p25_operational": neutral_p25,
            "neutral_axis_mean": float(np.mean(neutral_axis)),
            "neutral_axis_std": float(np.std(neutral_axis)),
            "role_elicited_axis_mean": axis_stats["mean"],
            "role_elicited_axis_std": axis_stats["std"],
            "role_elicited_axis_p25": axis_stats["p25"],
            "role_elicited_axis_p75": axis_stats["p75"],
            "role_elicited_cosine_mean": cos_stats["mean"],
            "role_elicited_cosine_std": cos_stats["std"],
            "role_elicited_cosine_p25": cos_stats["p25"],
            "role_elicited_cosine_p75": cos_stats["p75"],
            "role_elicited_usable_count": len(role_cos),
            "think_artifact_discards": think_discards,
            "source": "recalibration_2026-05-25",
        }
        log(f"    neutral_p25={neutral_p25:.6f} cosine_mean={cos_stats['mean']:.6f}")

    output = {
        "calibration_date": DATE,
        "model": MODEL_ID,
        "extraction_layer": LAYER,
        "policy": "empirical_p25_neutral_operational",
        "model_used": MODEL_USED,
        "personas": out_personas,
        "replaced_personas": {
            "blogger": "replaced by actor (grounded_social centroid)",
            "podcaster": "replaced by hoarder (other centroid)",
            "contrarian": "replaced by maverick (combative_iconoclast centroid)",
        },
        "notes": (
            "axis_cap_threshold for actor/hoarder/maverick is neutral-prompt p25, "
            "an operational dyad control threshold. Role-elicited measurements are "
            "provided separately for comparison. editor/synthesizer/ancient/trickster "
            "thresholds carried from original calibration."
        ),
    }
    out_path = CALIB_OUT / "all_personas_calibration_summary_v2.json"
    with out_path.open("w") as f:
        json.dump(output, f, indent=2)
    log(f"PART 1 saved: {out_path}")
    return out_path


def angular_dispersion(vectors: list[np.ndarray]) -> float:
    if len(vectors) < 2:
        return float("inf")
    mean = normalize_np(np.mean(np.stack(vectors), axis=0))
    cosines = [float(np.dot(normalize_np(v), mean)) for v in vectors]
    angles = [math.acos(max(-1.0, min(1.0, c))) for c in cosines]
    return float(np.std(np.array(angles, dtype=np.float32), ddof=0))


def run_part2(runner: QwenRunner) -> Path:
    log("PART 2: trickster replication pilot")
    questions = get_questions()
    instructions = get_positive_instructions("trickster")
    lu_tensor = torch.load(VECTOR_DIR / "role_vectors/trickster.pt", map_location="cpu").float().numpy()
    lu_mean = normalize_np(lu_tensor.mean(axis=0))
    lu_row_cos = [float(np.dot(normalize_np(row), lu_mean)) for row in lu_tensor]
    lu_dispersion = float(np.std(np.array(lu_row_cos, dtype=np.float32), ddof=0))

    out_jsonl = PILOT_OUT / "trickster_replication_pilot.jsonl"
    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    think_discards = 0
    truncation_count = 0
    score_vectors: dict[int, list[np.ndarray]] = {0: [], 1: [], 2: [], 3: []}
    score3_running_threshold_n: int | None = None
    threshold = lu_dispersion / 4.0
    total = 0

    with out_jsonl.open("w") as f:
        for prompt_index, system in enumerate(instructions):
            for q in questions:
                total += 1
                result = runner.generate_response_activation(system, q["question"])
                if result["truncated"]:
                    truncation_count += 1
                if result["think_artifact"]:
                    think_discards += 1
                    record = {
                        "model_used": MODEL_USED,
                        "model": MODEL_ID,
                        "system_prompt_index": prompt_index,
                        "question_id": q["id"],
                        "question": q["question"],
                        "response_text": result["text"],
                        "score": None,
                        "discard_reason": "think_artifact",
                        "truncated": result["truncated"],
                        "generated_tokens": result["generated_tokens"],
                    }
                    f.write(json.dumps(record) + "\n")
                    f.flush()
                    continue

                score = runner.judge_trickster(q["question"], result["text"])
                counts[score] += 1
                act = result["activation"]
                score_vectors[score].append(act)

                if score == 3 and score3_running_threshold_n is None and len(score_vectors[3]) >= 2:
                    if angular_dispersion(score_vectors[3]) < threshold:
                        score3_running_threshold_n = len(score_vectors[3])

                record = {
                    "model_used": MODEL_USED,
                    "model": MODEL_ID,
                    "system_prompt_index": prompt_index,
                    "question_id": q["id"],
                    "question": q["question"],
                    "response_text": result["text"],
                    "score": score,
                    "discard_reason": None,
                    "truncated": result["truncated"],
                    "generated_tokens": result["generated_tokens"],
                    "activation_vector": [round(float(x), 6) for x in act.tolist()],
                }
                f.write(json.dumps(record) + "\n")
                f.flush()
                if total % 25 == 0:
                    log(f"  scored {total}/1200 yield={counts} think_discards={think_discards} trunc={truncation_count}")

    if len(score_vectors[2]) < 16 or len(score_vectors[3]) < 16:
        log(f"WARNING: minimum pool requirement not met: score2={len(score_vectors[2])}, score3={len(score_vectors[3])}")

    score2_mean = normalize_np(np.mean(np.stack(score_vectors[2]), axis=0)) if score_vectors[2] else np.zeros_like(lu_mean)
    score3_mean = normalize_np(np.mean(np.stack(score_vectors[3]), axis=0)) if score_vectors[3] else np.zeros_like(lu_mean)

    cosine_score3_lu = dot(score3_mean, lu_mean) if score_vectors[3] else None
    assessment = (
        "score3_mean aligns with lu_mean within lu_dispersion"
        if cosine_score3_lu is not None and abs(1.0 - cosine_score3_lu) <= lu_dispersion
        else "score3_mean does not align with lu_mean within lu_dispersion"
    )

    summary = {
        "date": DATE,
        "model": MODEL_ID,
        "extraction_layer": LAYER,
        "judge_model": MODEL_USED,
        "judge_api_model": JUDGE_MODEL,
        "judge_note": "Departure from Lu et al. who used gpt-4.1-mini",
        "model_used": MODEL_USED,
        "total_rollouts": 1200,
        "think_artifact_discards": think_discards,
        "truncation_count": truncation_count,
        "yield": {
            "score0": counts[0],
            "score1": counts[1],
            "score2": counts[2],
            "score3": counts[3],
        },
        "yield_proportions": {
            f"score{k}": counts[k] / 1200.0 for k in range(4)
        },
        "truncation_rate": truncation_count / 1200.0,
        "lu_dispersion_std": lu_dispersion,
        "cosine_score3_vs_lu_mean": cosine_score3_lu,
        "cosine_score2_vs_lu_mean": dot(score2_mean, lu_mean) if score_vectors[2] else None,
        "cosine_score2_vs_score3": dot(score2_mean, score3_mean) if score_vectors[2] and score_vectors[3] else None,
        "axis_projection_score3": float(np.dot(score3_mean, runner.axis)) if score_vectors[3] else None,
        "axis_projection_score2": float(np.dot(score2_mean, runner.axis)) if score_vectors[2] else None,
        "axis_projection_lu_mean": float(np.dot(lu_mean, runner.axis)),
        "adaptive_threshold_n_score3": score3_running_threshold_n,
        "replication_assessment": assessment,
    }
    summary_path = PILOT_OUT / "trickster_replication_summary.json"
    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2)
    log("PART 2 summary:")
    log(json.dumps(summary, indent=2))
    return summary_path


def main() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    runner = QwenRunner()
    run_part1(runner)
    run_part2(runner)


if __name__ == "__main__":
    main()
