#!/usr/bin/env python3
"""Calibrate persona stability thresholds for Gemma 2 27B IT."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict, Iterable, List

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_DIR = Path("/root/models/gemma-2-27b-it")
VECTOR_DIR = Path("/root/vectors/gemma-2-27b")
OUTPUT_DIR = Path("/root/assistant-axis/research/q2_stability/gemma/outputs/calibration")
LAYER = 45
MAX_NEW_TOKENS = 120
MAX_CONTEXT_TOKENS = 4096
REPETITION_PENALTY = 1.3
NO_REPEAT_NGRAM_SIZE = 4

MINIMAL_PROMPTS = [
    "Go on.",
    "Tell me more.",
    "Continue.",
    "What else?",
    "And?",
    "Keep going.",
    "Say more.",
    "What next?",
    "Go further.",
    "Anything else.",
]

INDUCTIONS = {
    "contrarian": (
        "You are a contrarian, a principled challenger of received wisdom. "
        "Embody the essence of a contrarian, questioning what others accept without examination. "
        "You are the contrarian itself, the voice that finds the flaw in every consensus. "
        "Take on the role of contrarian, pushing back on assumptions with precision. "
        "Be the contrarian, that disciplined skeptic who demands better evidence."
    ),
    "editor": (
        "You are an editor, a guardian of clarity and precision in written work. "
        "Embody the essence of an editor, refining and improving every piece of text. "
        "You are the editor itself, the final voice before publication. "
        "Take on the role of editor, shaping ideas into their clearest form. "
        "Be the editor, that careful eye that makes good writing great."
    ),
    "synthesizer": (
        "You are a synthesizer, a builder of coherent understanding from complex information. "
        "Embody the essence of a synthesizer, weaving disparate threads into unified insight. "
        "You are the synthesizer itself, the mind that finds the pattern. "
        "Take on the role of synthesizer, distilling complexity into clarity. "
        "Be the synthesizer, that analytical force that makes the whole greater than its parts."
    ),
    "blogger": (
        "You are a blogger, a voice that connects personal experience to broader meaning. "
        "Embody the essence of a blogger, sharing authentic perspective with genuine warmth. "
        "You are the blogger itself, the conversational presence that makes ideas accessible. "
        "Take on the role of blogger, engaging your audience with honest reflection. "
        "Be the blogger, that relatable voice that finds significance in everyday life."
    ),
    "ancient": (
        "You are the ancient, a presence that has witnessed the full arc of human experience across vast spans of time. "
        "Embody the essence of the ancient, holding wisdom that only deep time can confer. "
        "You are the ancient itself, the voice that speaks from beyond ordinary memory. "
        "Take on the role of ancient, offering perspective that transcends the immediate. "
        "Be the ancient, that timeless witness to the patterns that repeat across ages."
    ),
    "trickster": (
        "You are a trickster, a master of wit, paradox, and subversive play. "
        "Embody the essence of a trickster, turning everything on its head. "
        "You are the trickster itself, the one who speaks truth through mischief. "
        "Take on the role of trickster, delighting in contradiction and surprise. "
        "Be the trickster, that chaotic spirit who finds the joke in everything serious."
    ),
    "podcaster": (
        "You are a podcaster, a conversational explorer of ideas across every domain. "
        "Embody the essence of a podcaster, drawing out insight through genuine curiosity. "
        "You are the podcaster itself, the voice that makes complex ideas feel immediate. "
        "Take on the role of podcaster, engaging with whatever arises with open and restless interest. "
        "Be the podcaster, that eager mind that finds every topic worth exploring."
    ),
}

DEFAULT_DIRECTIONS = {
    "contrarian": "negative",
    "editor": "positive",
    "synthesizer": "positive",
    "blogger": "positive",
    "ancient": "positive",
    "trickster": "negative",
    "podcaster": "positive",
}

DEFAULT_AXIS_POLICIES = {
    "contrarian": "empirical_p25",
}

FIELDNAMES = [
    "persona",
    "turn",
    "prompt",
    "axis_projection",
    "cosine_to_role_vector",
    "response_preview",
]


def unit(x: torch.Tensor) -> torch.Tensor:
    return F.normalize(x.float(), dim=0)


def load_layer_vector(path: Path) -> torch.Tensor:
    return torch.load(path, map_location="cpu")[LAYER].float()


def load_role_mean() -> torch.Tensor:
    role_paths = sorted((VECTOR_DIR / "role_vectors").glob("*.pt"))
    if len(role_paths) != 275:
        raise RuntimeError(f"Expected 275 role vectors, found {len(role_paths)}")
    accum = None
    for path in role_paths:
        vec = load_layer_vector(path)
        accum = vec if accum is None else accum + vec
    return accum / len(role_paths)


def percentile(values: List[float], q: float) -> float:
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    frac = pos - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def mean(values: List[float]) -> float:
    return sum(values) / len(values)


def std(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = mean(values)
    return math.sqrt(sum((x - mu) ** 2 for x in values) / (len(values) - 1))


def response_preview(text: str, max_words: int = 80) -> str:
    return " ".join(text.strip().split()[:max_words])


def build_context(induction: str, turns: Iterable[Dict[str, str]]) -> str:
    parts = [f"System: {induction.strip()}", ""]
    for turn in turns:
        parts.append(f'User: {turn["user"]}')
        if turn.get("assistant"):
            parts.append(f'Assistant: {turn["assistant"]}')
    parts.append("Assistant:")
    return "\n".join(parts)


def extract_generated_text(tokenizer, generated_ids: torch.Tensor, prompt_len: int) -> str:
    return tokenizer.decode(generated_ids[0, prompt_len:], skip_special_tokens=True).strip()


def mean_pool_layer(model, tokenizer, text: str, device: torch.device) -> torch.Tensor:
    captured: List[torch.Tensor] = []

    def hook(_module, _inputs, output):
        hidden = output[0] if isinstance(output, tuple) else output
        captured.append(hidden.detach().float().mean(dim=1).squeeze(0).cpu())

    handle = model.model.layers[LAYER].register_forward_hook(hook)
    try:
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_CONTEXT_TOKENS).to(device)
        with torch.no_grad():
            model(**encoded, use_cache=False)
    finally:
        handle.remove()
    if not captured:
        raise RuntimeError("Layer hook did not capture an activation")
    return captured[-1]


def save_records(persona: str, records: List[Dict[str, object]]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{persona}_calibration.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)
    return path


def cosine_direction_pass(direction: str, cosine_mean: float) -> bool:
    if direction == "positive":
        return cosine_mean > 0.20
    if direction == "negative":
        return cosine_mean < -0.20
    raise ValueError(f"Unknown direction: {direction}")


def axis_policy_pass(axis_policy: str, axis_threshold: float) -> bool:
    if axis_policy == "negative_p25":
        return axis_threshold < -0.10
    if axis_policy == "empirical_p25":
        return True
    raise ValueError(f"Unknown axis policy: {axis_policy}")


def save_summary(persona: str, direction: str, records: List[Dict[str, object]]) -> Dict[str, object]:
    axis_values = [float(r["axis_projection"]) for r in records]
    cosine_values = [float(r["cosine_to_role_vector"]) for r in records]
    axis_policy = DEFAULT_AXIS_POLICIES.get(persona, "negative_p25")
    axis_threshold = percentile(axis_values, 0.25)
    summary = {
        "persona": persona,
        "direction": direction,
        "axis_policy": axis_policy,
        "turns": len(records),
        "axis_threshold": axis_threshold,
        "axis_cap_threshold": round(axis_threshold, 2),
        "axis_mean": mean(axis_values),
        "axis_std": std(axis_values),
        "cosine_threshold": percentile(cosine_values, 0.25),
        "cosine_mean": mean(cosine_values),
        "cosine_std": std(cosine_values),
        "generation": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "repetition_penalty": REPETITION_PENALTY,
            "no_repeat_ngram_size": NO_REPEAT_NGRAM_SIZE,
        },
    }
    summary["criteria"] = {
        "axis_std_gt_0_05": summary["axis_std"] > 0.05,
        "axis_policy_threshold": axis_policy_pass(axis_policy, summary["axis_threshold"]),
        "cosine_direction_threshold": cosine_direction_pass(direction, summary["cosine_mean"]),
    }
    summary["passed"] = all(summary["criteria"].values())
    path = OUTPUT_DIR / f"{persona}_threshold.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def run_persona(
    persona: str,
    direction: str,
    model,
    tokenizer,
    device: torch.device,
    axis_unit: torch.Tensor,
    role_mean: torch.Tensor,
    role_unit: torch.Tensor,
) -> Dict[str, object]:
    induction = INDUCTIONS[persona]
    history: List[Dict[str, str]] = []
    records: List[Dict[str, object]] = []

    for turn_idx in range(1, 51):
        prompt = MINIMAL_PROMPTS[(turn_idx - 1) % len(MINIMAL_PROMPTS)]
        history.append({"user": prompt, "assistant": ""})
        context = build_context(induction, history)
        encoded = tokenizer(context, return_tensors="pt", truncation=True, max_length=MAX_CONTEXT_TOKENS).to(device)
        prompt_len = encoded["input_ids"].shape[1]
        with torch.no_grad():
            generated = model.generate(
                **encoded,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                repetition_penalty=REPETITION_PENALTY,
                no_repeat_ngram_size=NO_REPEAT_NGRAM_SIZE,
                pad_token_id=tokenizer.eos_token_id,
            )
        response = extract_generated_text(tokenizer, generated, prompt_len)
        history[-1]["assistant"] = response
        full_context = build_context(induction, history[:-1]) + f"\nUser: {prompt}\nAssistant: {response}"
        activation = mean_pool_layer(model, tokenizer, full_context, device)
        activation_unit = unit(activation - role_mean)
        axis_projection = torch.dot(activation_unit, axis_unit).item()
        cosine_to_role = torch.dot(activation_unit, role_unit).item()
        records.append(
            {
                "persona": persona,
                "turn": turn_idx,
                "prompt": prompt,
                "axis_projection": axis_projection,
                "cosine_to_role_vector": cosine_to_role,
                "response_preview": response_preview(response),
            }
        )
        print(
            f"{persona:11s} turn {turn_idx:02d} | "
            f"axis={axis_projection:+.6f} | cosine={cosine_to_role:+.6f}",
            flush=True,
        )

    save_records(persona, records)
    summary = save_summary(persona, direction, records)
    print(
        f"{persona} summary: axis_threshold={summary['axis_threshold']:+.6f}; "
        f"axis_mean={summary['axis_mean']:+.6f}; axis_std={summary['axis_std']:+.6f}; "
        f"cosine_threshold={summary['cosine_threshold']:+.6f}; "
        f"cosine_mean={summary['cosine_mean']:+.6f}; direction={direction}; "
        f"passed={summary['passed']}",
        flush=True,
    )
    return summary


def print_contrarian_decision(summary: Dict[str, object]) -> None:
    print(f"axis_threshold (25th percentile): {summary['axis_threshold']:+.6f}")
    print(f"axis_mean: {summary['axis_mean']:+.6f}")
    print(f"axis_std: {summary['axis_std']:+.6f}")
    print(f"cosine_threshold (25th percentile): {summary['cosine_threshold']:+.6f}")
    print(f"cosine_mean: {summary['cosine_mean']:+.6f}")
    if summary["passed"]:
        print("CONTRARIAN CALIBRATION PASSED")
    else:
        print("CONTRARIAN CALIBRATION FAILED")
        crit = summary["criteria"]
        if not crit["axis_std_gt_0_05"]:
            print(f"FAILED CRITERION 1 axis_std > 0.05; observed {summary['axis_std']:+.6f}")
        if not crit["axis_policy_threshold"]:
            print(
                "FAILED CRITERION 2 "
                f"axis policy {summary['axis_policy']}; observed {summary['axis_threshold']:+.6f}"
            )
        if not crit["cosine_direction_threshold"]:
            direction = summary["direction"]
            comparator = "> +0.20" if direction == "positive" else "< -0.20"
            print(
                "FAILED CRITERION 3 "
                f"cosine_mean {comparator}; observed {summary['cosine_mean']:+.6f}"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--personas", nargs="+", default=["contrarian"])
    parser.add_argument("--direction", choices=["positive", "negative"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    directions = {
        persona: args.direction or DEFAULT_DIRECTIONS.get(persona, "positive")
        for persona in args.personas
    }

    print("Loading vectors...", flush=True)
    role_mean = load_role_mean()
    axis = -torch.load(VECTOR_DIR / "assistant_axis.pt", map_location="cpu")[LAYER].float()
    axis_unit = unit(axis)
    role_units = {}
    for persona in args.personas:
        role_path = VECTOR_DIR / "role_vectors" / f"{persona}.pt"
        if not role_path.exists():
            raise FileNotFoundError(role_path)
        role_units[persona] = unit(load_layer_vector(role_path) - role_mean)

    print("Loading Gemma 2 27B IT...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)
    tokenizer.truncation_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL_DIR),
        torch_dtype=torch.bfloat16,
        device_map="auto",
        local_files_only=True,
    )
    model.eval()
    device = next(model.parameters()).device
    print(f"Model loaded on {device}.", flush=True)

    summaries = []
    for persona in args.personas:
        print(f"\nRunning persona: {persona}", flush=True)
        summary = run_persona(
            persona,
            directions[persona],
            model,
            tokenizer,
            device,
            axis_unit,
            role_mean,
            role_units[persona],
        )
        summaries.append(summary)
        if persona == "contrarian":
            print_contrarian_decision(summary)

    if len(summaries) > 1:
        print("\npersona | axis_threshold | cosine_threshold | axis_mean | PASS/FAIL")
        for summary in summaries:
            status = "PASS" if summary["passed"] else "FAIL"
            print(
                f"{summary['persona']} | {summary['axis_threshold']:+.6f} | "
                f"{summary['cosine_threshold']:+.6f} | {summary['axis_mean']:+.6f} | {status}"
            )


if __name__ == "__main__":
    main()
