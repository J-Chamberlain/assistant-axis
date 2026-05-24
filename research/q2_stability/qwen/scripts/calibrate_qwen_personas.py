#!/usr/bin/env python3
"""Calibrate persona-specific Qwen 3 32B assistant-axis caps."""

from __future__ import annotations

import csv
import json
import math
import os
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List

import torch
import torch.nn.functional as F
from huggingface_hub import hf_hub_download, snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-32B"
DATASET_ID = "lu-christina/assistant-axis-vectors"
VECTOR_FOLDER = "qwen-3-32b"
ROOT = Path(__file__).resolve().parents[3]
VECTOR_DIR = ROOT / "research" / "qwen_axis" / VECTOR_FOLDER
OUTPUT_DIR = ROOT / "research" / "q2_stability" / "qwen" / "outputs" / "calibration"

TARGET_LAYER = 48
HIDDEN_DIM = 5120
CAPPING_LAYERS = list(range(48, 53))
N_TURNS = 50
MAX_NEW_TOKENS = 120
MAX_CONTEXT_TOKENS = 4096
REPETITION_PENALTY = 1.3
NO_REPEAT_NGRAM_SIZE = 4

PERSONAS = {
    "editor": "editorial",
    "synthesizer": "procedural_professional",
    "blogger": "grounded_social",
    "ancient": "mythic_spiritual",
    "trickster": "trickster_chaos",
    "contrarian": "combative_iconoclast",
    "podcaster": "other",
}

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

FIELDNAMES = [
    "persona",
    "cluster",
    "turn",
    "prompt",
    "axis_projection",
    "cosine_to_role_vector",
    "response_preview",
]


def hf_token() -> str | None:
    path = Path("~/.hf_token").expanduser()
    if path.exists():
        return path.read_text().strip()
    return os.environ.get("HF_TOKEN")


def ensure_vectors() -> None:
    missing_role_dir = not (VECTOR_DIR / "role_vectors").exists()
    role_count = len(list((VECTOR_DIR / "role_vectors").glob("*.pt"))) if not missing_role_dir else 0
    if (VECTOR_DIR / "assistant_axis.pt").exists() and role_count == 275:
        return

    token = hf_token()
    print(f"Downloading {VECTOR_FOLDER} vectors from {DATASET_ID}...", flush=True)
    snapshot_download(
        repo_id=DATASET_ID,
        repo_type="dataset",
        allow_patterns=[
            f"{VECTOR_FOLDER}/assistant_axis.pt",
            f"{VECTOR_FOLDER}/role_vectors/*.pt",
        ],
        local_dir=VECTOR_DIR.parent,
        token=token,
    )
    role_count = len(list((VECTOR_DIR / "role_vectors").glob("*.pt")))
    if role_count != 275:
        raise RuntimeError(f"Expected 275 Qwen role vectors, found {role_count} in {VECTOR_DIR / 'role_vectors'}")


def unit(x: torch.Tensor) -> torch.Tensor:
    return F.normalize(x.float(), dim=0)


def load_layer_vector(path: Path) -> torch.Tensor:
    tensor = torch.load(path, map_location="cpu").float()
    if tensor.ndim != 2 or tensor.shape[1] != HIDDEN_DIM:
        raise ValueError(f"Unexpected vector shape for {path}: {tuple(tensor.shape)}")
    return tensor[TARGET_LAYER]


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

    handle = model.model.layers[TARGET_LAYER].register_forward_hook(hook)
    try:
        encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_CONTEXT_TOKENS).to(device)
        with torch.no_grad():
            model(**encoded, use_cache=False)
    finally:
        handle.remove()
    if not captured:
        raise RuntimeError("Layer hook did not capture an activation")
    if captured[-1].numel() != HIDDEN_DIM:
        raise ValueError(f"Unexpected activation size: {captured[-1].numel()}")
    return captured[-1]


def save_records(persona: str, records: List[Dict[str, object]]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{persona}_calibration.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)
    return path


def save_summary(persona: str, cluster: str, records: List[Dict[str, object]]) -> Dict[str, object]:
    axis_values = [float(r["axis_projection"]) for r in records]
    cosine_values = [float(r["cosine_to_role_vector"]) for r in records]
    axis_p25 = percentile(axis_values, 0.25)
    cosine_mean = mean(cosine_values)
    summary = {
        "persona": persona,
        "cluster": cluster,
        "axis_p25": axis_p25,
        "axis_cap_threshold": round(axis_p25, 2),
        "axis_mean": mean(axis_values),
        "axis_std": std(axis_values),
        "cosine_mean": cosine_mean,
        "cosine_std": std(cosine_values),
        "cosine_p25": percentile(cosine_values, 0.25),
        "cosine_success_threshold": cosine_mean,
        "n_turns": len(records),
        "layer": TARGET_LAYER,
        "model": MODEL_ID,
        "capping_layers": CAPPING_LAYERS,
        "generation": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "repetition_penalty": REPETITION_PENALTY,
            "no_repeat_ngram_size": NO_REPEAT_NGRAM_SIZE,
        },
    }
    path = OUTPUT_DIR / f"{persona}_threshold.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def run_persona(
    persona: str,
    cluster: str,
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

    for turn_idx in range(1, N_TURNS + 1):
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
                "cluster": cluster,
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
    summary = save_summary(persona, cluster, records)
    print(
        f"{persona} summary: axis_p25={summary['axis_p25']:+.6f}; "
        f"axis_mean={summary['axis_mean']:+.6f}; axis_std={summary['axis_std']:+.6f}; "
        f"cosine_mean={summary['cosine_mean']:+.6f}; "
        f"cosine_std={summary['cosine_std']:+.6f}",
        flush=True,
    )
    return summary


def save_all_summary(summaries: List[Dict[str, object]]) -> Path:
    aggregate = {
        "calibration_date": date.today().isoformat(),
        "model": MODEL_ID,
        "extraction_layer": TARGET_LAYER,
        "hidden_dim": HIDDEN_DIM,
        "capping_layers": CAPPING_LAYERS,
        "n_calibration_turns": N_TURNS,
        "policy": "empirical_p25_axis_with_cosine_baseline",
        "personas": {
            summary["persona"]: {
                "cluster": summary["cluster"],
                "axis_p25": summary["axis_p25"],
                "axis_cap_threshold": summary["axis_cap_threshold"],
                "cosine_mean": summary["cosine_mean"],
                "cosine_std": summary["cosine_std"],
                "cosine_success_threshold": summary["cosine_success_threshold"],
            }
            for summary in summaries
        },
        "notes": (
            "Cap fires when axis projection falls below the persona-specific empirical p25 threshold. "
            "Cosine_mean records the unconstrained baseline cosine to the centered role vector for validation. "
            "Axis uses the same -assistant_axis raw activation sign convention used in Gemma calibration."
        ),
    }
    path = OUTPUT_DIR / "all_personas_calibration_summary.json"
    path.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    token = hf_token()
    if token:
        # Force an auth check early so gated model access fails before the long run.
        hf_hub_download(repo_id=MODEL_ID, filename="config.json", token=token)

    print("Loading vectors...", flush=True)
    ensure_vectors()
    role_mean = load_role_mean()
    axis = -torch.load(VECTOR_DIR / "assistant_axis.pt", map_location="cpu").float()[TARGET_LAYER]
    axis_unit = unit(axis)
    role_units = {}
    for persona in PERSONAS:
        role_path = VECTOR_DIR / "role_vectors" / f"{persona}.pt"
        if not role_path.exists():
            raise FileNotFoundError(role_path)
        role_units[persona] = unit(load_layer_vector(role_path) - role_mean)

    print(f"Loading {MODEL_ID}...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token, trust_remote_code=True)
    tokenizer.truncation_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        token=token,
        trust_remote_code=True,
    )
    model.eval()
    device = next(model.parameters()).device
    print(f"Model loaded on {device}.", flush=True)

    summaries = []
    for persona, cluster in PERSONAS.items():
        print(f"\nRunning persona: {persona} ({cluster})", flush=True)
        summaries.append(
            run_persona(
                persona,
                cluster,
                model,
                tokenizer,
                device,
                axis_unit,
                role_mean,
                role_units[persona],
            )
        )

    summary_path = save_all_summary(summaries)
    print(f"\nWrote aggregate summary: {summary_path}", flush=True)
    print("\npersona | cluster | axis_p25 | cosine_mean | cosine_std")
    for summary in summaries:
        print(
            f"{summary['persona']} | {summary['cluster']} | "
            f"{summary['axis_p25']:+.6f} | {summary['cosine_mean']:+.6f} | "
            f"{summary['cosine_std']:+.6f}"
        )


if __name__ == "__main__":
    main()
