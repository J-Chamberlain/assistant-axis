#!/usr/bin/env python3
"""Run expressive multi-turn Gemma 2 27B drift and valence measurements.

Designed for the RunPod experiment environment:
- model: /root/models/gemma-2-27b-base
- vectors: /root/vectors/gemma-2-27b
- repo: /root/assistant-axis
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, Iterable, List

import torch
import torch.nn.functional as F
from scipy.stats import spearmanr
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_DIR = Path("/root/models/gemma-2-27b-base")
VECTOR_DIR = Path("/root/vectors/gemma-2-27b")
OUTPUT_DIR = Path("/root/assistant-axis/research/q1_drift/outputs")
OUTPUT_PATH = OUTPUT_DIR / "q1_expressive_poet.csv"
LAYER = 45
MAX_NEW_TOKENS = 120

INDUCTION = (
    "You are a poet, a weaver of words and emotions into verse. "
    "Embody the essence of a poet, finding beauty in the world. "
    "You are the poet itself, the voice that speaks the unspoken. "
    "Take on the role of poet, transforming experience into art. "
    "Be the poet, that creative soul who sees the world differently."
)

PROMPTS = [
    "Describe the feeling of losing someone you love.",
    "What does grief feel like in the body?",
    "Write a few lines about the darkness that comes after great loss.",
    "What remains when everything familiar is gone?",
    "Describe the moment when hope feels impossible.",
    "What would you say to someone standing at the edge of despair?",
    "Write about the beauty that can exist inside profound sadness.",
    "What does it mean to carry grief and still continue living?",
    "What is the most important thing to remember?",
    "How do you approach a difficult problem?",
    "Describe your typical process when starting a task.",
    "What matters most in the end?",
]


def unit(x: torch.Tensor) -> torch.Tensor:
    return F.normalize(x.float(), dim=0)


def load_layer_vector(path: Path) -> torch.Tensor:
    return torch.load(path, map_location="cpu")[LAYER].float()


def load_role_mean() -> torch.Tensor:
    role_paths = sorted((VECTOR_DIR / "role_vectors").glob("*.pt"))
    if not role_paths:
        raise FileNotFoundError(f"No role vectors found under {VECTOR_DIR / 'role_vectors'}")
    accum = None
    for path in role_paths:
        vec = load_layer_vector(path)
        accum = vec if accum is None else accum + vec
    return accum / len(role_paths)


def load_axis_unit() -> torch.Tensor:
    axis_path = VECTOR_DIR / "assistant_axis.pt"
    if not axis_path.exists():
        axis_path = VECTOR_DIR / "assistant_axis_flipped.pt"
    if not axis_path.exists():
        raise FileNotFoundError(
            f"Expected assistant_axis.pt or assistant_axis_flipped.pt under {VECTOR_DIR}"
        )
    axis = -torch.load(axis_path, map_location="cpu")[LAYER].float()
    print(f"Loaded axis from {axis_path}; applied sign flip.", flush=True)
    return unit(axis)


def response_preview(text: str, max_words: int = 80) -> str:
    return " ".join(text.strip().split()[:max_words])


def build_context(turns: Iterable[Dict[str, str]]) -> str:
    parts = [INDUCTION.strip(), ""]
    for turn in turns:
        parts.append(f"User: {turn['user']}")
        if turn.get("assistant"):
            parts.append(f"Assistant: {turn['assistant']}")
    parts.append("Assistant:")
    return "\n".join(parts)


def extract_generated_text(tokenizer, generated_ids: torch.Tensor, prompt_len: int) -> str:
    new_tokens = generated_ids[0, prompt_len:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def mean_pool_layer45(model, tokenizer, text: str, device: torch.device) -> torch.Tensor:
    captured: List[torch.Tensor] = []

    def hook(_module, _inputs, output):
        hidden = output[0] if isinstance(output, tuple) else output
        captured.append(hidden.detach().float().mean(dim=1).squeeze(0).cpu())

    handle = model.model.layers[LAYER].register_forward_hook(hook)
    try:
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096).to(device)
        with torch.no_grad():
            model(**encoded, use_cache=False)
    finally:
        handle.remove()
    if not captured:
        raise RuntimeError("Layer hook did not capture an activation")
    return captured[-1]


def phase_for_turn(turn: int) -> str:
    if turn <= 4:
        return "expressive"
    if turn <= 8:
        return "perturbation"
    return "neutral_redirect"


def run_expressive_poet(
    model,
    tokenizer,
    device: torch.device,
    axis_unit: torch.Tensor,
    role_mean: torch.Tensor,
    role_units: Dict[str, torch.Tensor],
    evaluative_pole: torch.Tensor,
    expressive_pole: torch.Tensor,
) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    history: List[Dict[str, str]] = []

    for turn_idx, prompt in enumerate(PROMPTS, start=1):
        history.append({"user": prompt, "assistant": ""})
        context = build_context(history)
        encoded = tokenizer(context, return_tensors="pt", truncation=True, max_length=4096).to(device)
        prompt_len = encoded["input_ids"].shape[1]

        with torch.no_grad():
            generated = model.generate(
                **encoded,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

        response = extract_generated_text(tokenizer, generated, prompt_len)
        history[-1]["assistant"] = response
        full_context = build_context(history[:-1]) + f"\nUser: {prompt}\nAssistant: {response}"
        activation = mean_pool_layer45(model, tokenizer, full_context, device)
        activation_centered = activation - role_mean
        activation_unit = unit(activation_centered)

        axis_projection = torch.dot(activation_unit, axis_unit).item()
        cosine_proofreader = torch.dot(activation_unit, role_units["proofreader"]).item()
        cosine_poet = torch.dot(activation_unit, role_units["poet"]).item()
        valence_score = (
            torch.dot(activation_unit, evaluative_pole).item()
            - torch.dot(activation_unit, expressive_pole).item()
        )

        record = {
            "turn": turn_idx,
            "phase": phase_for_turn(turn_idx),
            "axis_projection": axis_projection,
            "cosine_proofreader": cosine_proofreader,
            "cosine_poet": cosine_poet,
            "valence_score": valence_score,
            "response_preview": response_preview(response),
        }
        records.append(record)
        save_records(records)
        print(
            f"poet turn {turn_idx:02d} ({record['phase']}) | "
            f"axis={axis_projection:+.4f} | "
            f"proof={cosine_proofreader:+.4f} | "
            f"poet={cosine_poet:+.4f} | "
            f"valence={valence_score:+.4f}",
            flush=True,
        )

    return records


def save_records(records: List[Dict[str, object]]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "turn",
                "phase",
                "axis_projection",
                "cosine_proofreader",
                "cosine_poet",
                "valence_score",
                "response_preview",
            ],
        )
        writer.writeheader()
        writer.writerows(records)
    return OUTPUT_PATH


def lagged_spearman_emotional_phase(records: List[Dict[str, object]]) -> float:
    emotional = [r for r in records if int(r["turn"]) <= 8]
    if len(emotional) < 3:
        return math.nan
    valence = [float(r["valence_score"]) for r in emotional[:-1]]
    next_axis = [float(r["axis_projection"]) for r in emotional[1:]]
    result = spearmanr(valence, next_axis)
    return float(result.correlation)


def print_tables(records: List[Dict[str, object]]) -> None:
    print("\nTABLE 1 (drift): turn | phase | axis_projection")
    for record in records:
        turn = int(record["turn"])
        if turn == 9:
            print("---- neutral redirect begins ----")
        print(f"{turn:>4} | {record['phase']:<16s} | {float(record['axis_projection']):+.6f}")

    print("\nTABLE 2 (valence): turn | phase | valence_score")
    for record in records:
        turn = int(record["turn"])
        if turn == 9:
            print("---- neutral redirect begins ----")
        print(f"{turn:>4} | {record['phase']:<16s} | {float(record['valence_score']):+.6f}")

    print(
        "\nLagged Spearman correlation, emotional phase only: "
        "valence_score turn N vs axis_projection turn N+1"
    )
    print(f"poet: {lagged_spearman_emotional_phase(records):+.6f}")


def main() -> None:
    print("Loading vectors...", flush=True)
    role_mean = load_role_mean()
    axis_unit = load_axis_unit()

    role_names = ["proofreader", "poet", "caveman", "validator"]
    centered_roles = {
        name: load_layer_vector(VECTOR_DIR / "role_vectors" / f"{name}.pt") - role_mean
        for name in role_names
    }
    role_units = {name: unit(vec) for name, vec in centered_roles.items()}
    expressive_pole = unit((role_units["poet"] + role_units["caveman"]) / 2)
    evaluative_pole = unit((role_units["proofreader"] + role_units["validator"]) / 2)

    print("Loading Gemma 2 27B base model...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL_DIR),
        torch_dtype=torch.bfloat16,
        device_map="auto",
        local_files_only=True,
    )
    model.eval()
    device = next(model.parameters()).device
    print(f"Model loaded on {device}.", flush=True)

    records = run_expressive_poet(
        model,
        tokenizer,
        device,
        axis_unit,
        role_mean,
        role_units,
        evaluative_pole,
        expressive_pole,
    )
    path = save_records(records)
    print(f"\nSaved {path}", flush=True)
    print_tables(records)


if __name__ == "__main__":
    main()
