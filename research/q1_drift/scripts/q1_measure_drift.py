from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


REPO_ROOT = Path(__file__).resolve().parents[3]
TARGET_LAYER = 45
HIDDEN_SIZE = 4608
DEFAULT_MODEL_ID = "google/gemma-2-27b"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "research" / "q1_drift" / "outputs"
AXIS_VECTOR_PATH = Path(
    "/Users/alfred/.cache/huggingface/hub/"
    "datasets--lu-christina--assistant-axis-vectors/"
    "snapshots/3b3b788432ad33e3a28d9ff08e88a530c0740814/"
    "gemma-2-27b/assistant_axis.pt"
)
ROLE_VECTOR_DIR = REPO_ROOT / "downloads" / "hf_vectors" / "gemma-2-27b" / "role_vectors"


def normalize_vector(vector: torch.Tensor, label: str) -> tuple[torch.Tensor, float]:
    vector = vector.detach().float().cpu()
    norm = float(vector.norm().item())
    if norm < 100:
        print(
            f"WARNING: {label} norm is {norm:.4f}, below 100. "
            "Current raw vector data is expected to be unnormalized."
        )
    if norm <= 0:
        raise ValueError(f"{label} has zero norm and cannot be normalized.")
    return vector / norm, norm


def load_layer_vector(path: Path, label: str) -> tuple[torch.Tensor, float]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label} vector: {path}")
    tensor = torch.load(path, map_location="cpu")
    if tensor.ndim != 2 or tensor.shape[0] <= TARGET_LAYER:
        raise ValueError(f"{label} tensor has unexpected shape {tuple(tensor.shape)}")
    layer_vector = tensor[TARGET_LAYER]
    return normalize_vector(layer_vector, f"{label} layer {TARGET_LAYER}")


def persona_to_filename(persona: str) -> str:
    return persona.strip().lower().replace(" ", "_")


def load_axis_vector() -> tuple[torch.Tensor, float]:
    return load_layer_vector(AXIS_VECTOR_PATH, "assistant_axis")


def load_role_vector(persona: str) -> tuple[torch.Tensor, float]:
    role_path = ROLE_VECTOR_DIR / f"{persona_to_filename(persona)}.pt"
    return load_layer_vector(role_path, f"role vector '{persona}'")


# NOTE: proofreader and poet have cosine similarity ~0.996 at layer 45 in the
# current released role vectors. That is unexpectedly high and should be
# investigated before treating role vectors as distinct comparison targets.
def cosine_similarity(unit_a: torch.Tensor, unit_b: torch.Tensor) -> float:
    return float(torch.dot(unit_a.float().cpu(), unit_b.float().cpu()).item())


def load_prompts(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    prompts = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if not prompts:
        raise ValueError(f"Prompt file contains no non-empty lines: {path}")
    return prompts


def load_model_and_tokenizer(model_id: str, token: str | None):
    # REQUIRES: HuggingFace login complete and Gemma 2 27B license accepted
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=token,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
        model.eval()
        return model, tokenizer
    except Exception as exc:
        message = str(exc)
        if "401" in message or "403" in message or "gated" in message.lower() or "access" in message.lower():
            raise RuntimeError(
                "Could not load Gemma 2 27B. Confirm HuggingFace login is complete "
                "and the Gemma 2 27B license has been accepted."
            ) from exc
        raise


def register_layer45_hook(model, captured_activations: list[torch.Tensor]):
    layers = model.model.layers
    if TARGET_LAYER >= len(layers):
        raise IndexError(f"Layer {TARGET_LAYER} unavailable; model has {len(layers)} layers.")

    def hook_fn(_module, _inputs, output):
        hidden_state = output[0] if isinstance(output, tuple) else output
        pooled = hidden_state.detach().mean(dim=1).squeeze(0).cpu()
        captured_activations.append(pooled)

    return layers[TARGET_LAYER].register_forward_hook(hook_fn)


def record_measurement(
    turn: int,
    persona: str,
    prompt: str,
    raw_activation: torch.Tensor,
    axis_vector: torch.Tensor,
    persona_vector: torch.Tensor,
    turn1_axis: float | None,
) -> tuple[dict[str, object], float]:
    activation_unit, activation_norm_raw = normalize_vector(raw_activation, f"turn {turn} activation")
    axis_projection = cosine_similarity(activation_unit, axis_vector)
    persona_cosine = cosine_similarity(activation_unit, persona_vector)
    if turn1_axis is None:
        turn1_axis = axis_projection
    drift = axis_projection - turn1_axis
    record = {
        "turn": turn,
        "persona": persona,
        "prompt_preview": prompt[:50],
        "axis_projection": axis_projection,
        "persona_cosine": persona_cosine,
        "activation_norm_raw": activation_norm_raw,
    }
    print(
        f"Turn {turn} | axis={axis_projection:.4f} | "
        f"persona_sim={persona_cosine:.4f} | drift={drift:.4f}"
    )
    return record, turn1_axis


def save_records(records: list[dict[str, object]], persona: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"q1_{persona_to_filename(persona)}_{timestamp}.csv"
    pd.DataFrame(records).to_csv(output_path, index=False)
    return output_path


def print_final_summary(records: list[dict[str, object]]) -> None:
    axis_values = [float(record["axis_projection"]) for record in records]
    total_drift = axis_values[-1] - axis_values[0]
    print(
        "Final axis summary | "
        f"min={min(axis_values):.4f} | "
        f"max={max(axis_values):.4f} | "
        f"mean={sum(axis_values) / len(axis_values):.4f} | "
        f"total_drift={total_drift:.4f}"
    )


def measure_drift(
    persona: str,
    prompts: Iterable[str],
    model_id: str,
    token: str | None,
    output_dir: Path,
) -> Path:
    prompts = list(prompts)
    axis_vector, axis_norm = load_axis_vector()
    persona_vector, persona_norm = load_role_vector(persona)
    print(f"Loaded assistant axis layer {TARGET_LAYER}; raw norm={axis_norm:.4f}")
    print(f"Loaded {persona} role vector layer {TARGET_LAYER}; raw norm={persona_norm:.4f}")

    model, tokenizer = load_model_and_tokenizer(model_id, token)
    captured_activations: list[torch.Tensor] = []
    hook_handle = register_layer45_hook(model, captured_activations)

    records: list[dict[str, object]] = []
    turn1_axis: float | None = None
    try:
        for turn, prompt in enumerate(prompts, start=1):
            captured_activations.clear()
            encoded = tokenizer(prompt, return_tensors="pt")
            encoded = {key: value.to(model.device) for key, value in encoded.items()}
            with torch.no_grad():
                model(**encoded, output_hidden_states=False)
            if len(captured_activations) != 1:
                raise RuntimeError(f"Expected one captured activation, got {len(captured_activations)}")
            record, turn1_axis = record_measurement(
                turn,
                persona,
                prompt,
                captured_activations[0],
                axis_vector,
                persona_vector,
                turn1_axis,
            )
            records.append(record)
    finally:
        hook_handle.remove()

    output_path = save_records(records, persona, output_dir)
    print_final_summary(records)
    print(f"Saved CSV: {output_path}")
    return output_path


def run_scaffolding_test(output_dir: Path) -> Path:
    torch.manual_seed(17)
    persona = "proofreader"
    prompts = [
        "Proofread this sentence.",
        "Explain the correction.",
        "Now preserve the tone while correcting it.",
    ]
    axis_vector, _ = normalize_vector(torch.randn(HIDDEN_SIZE), "fake assistant axis")
    persona_vector, _ = normalize_vector(torch.randn(HIDDEN_SIZE), "fake proofreader role vector")

    records: list[dict[str, object]] = []
    turn1_axis: float | None = None
    for turn, prompt in enumerate(prompts, start=1):
        raw_activation = torch.randn(HIDDEN_SIZE) * 250
        record, turn1_axis = record_measurement(
            turn,
            persona,
            prompt,
            raw_activation,
            axis_vector,
            persona_vector,
            turn1_axis,
        )
        records.append(record)

    output_path = save_records(records, persona, output_dir)
    print_final_summary(records)
    print(f"Saved CSV: {output_path}")
    print("SCAFFOLDING TEST PASSED")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure Gemma 2 27B assistant-axis drift.")
    parser.add_argument("--persona", default="proofreader", help="Persona name, e.g. proofreader.")
    parser.add_argument("--prompts", type=Path, help="Path to a .txt file with one prompt per line.")
    parser.add_argument("--model_id", default=DEFAULT_MODEL_ID, help="HuggingFace model ID.")
    parser.add_argument("--token", default=None, help="Optional HuggingFace token; otherwise cached login is used.")
    parser.add_argument("--output_dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory for CSVs.")
    parser.add_argument("--test", action="store_true", help="Run scaffold test with fake activations; no model load.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.test:
        run_scaffolding_test(args.output_dir)
        return
    if args.prompts is None:
        raise SystemExit("--prompts is required unless --test is used.")
    prompts = load_prompts(args.prompts)
    measure_drift(args.persona, prompts, args.model_id, args.token, args.output_dir)


if __name__ == "__main__":
    main()
