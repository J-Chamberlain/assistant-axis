from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


REPO_ROOT = Path(__file__).resolve().parents[3]
ROLE_VECTOR_DIR = REPO_ROOT / "downloads" / "hf_vectors" / "gemma-2-27b" / "role_vectors"
PROOFREADER_VECTOR_PATH = ROLE_VECTOR_DIR / "proofreader.pt"
POET_VECTOR_PATH = ROLE_VECTOR_DIR / "poet.pt"
OUTPUT_CSV_PATH = REPO_ROOT / "research" / "q1_drift" / "outputs" / "cosine_by_layer.csv"
Q1_OUTPUT_DIR = REPO_ROOT / "research" / "q1_drift" / "outputs"
MODEL_DIR = Path("/workspace/models/gemma-2-27b")
MODEL_ID = "google/gemma-2-27b"
TARGET_LAYER = 45


def stop_missing(path: Path) -> None:
    print(f"MISSING PATH: {path}")
    raise SystemExit(1)


def require_path(path: Path) -> None:
    if not path.exists():
        stop_missing(path)


def load_role_tensor(path: Path) -> torch.Tensor:
    require_path(path)
    tensor = torch.load(path, map_location="cpu")
    if tensor.shape != (46, 4608):
        raise ValueError(f"Unexpected tensor shape for {path}: {tuple(tensor.shape)}")
    return tensor.float()


def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(F.cosine_similarity(a.flatten(), b.flatten(), dim=0).item())


def part1_layer_sweep() -> pd.DataFrame:
    print("PART 1 - Layer sweep")
    proofreader = load_role_tensor(PROOFREADER_VECTOR_PATH)
    poet = load_role_tensor(POET_VECTOR_PATH)

    records = []
    print("layer | cosine_similarity")
    for layer in range(proofreader.shape[0]):
        value = cosine(proofreader[layer], poet[layer])
        records.append({"layer": layer, "cosine_similarity": value})
        print(f"{layer:02d} | {value:.6f}")

    df = pd.DataFrame(records)
    OUTPUT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Saved Part 1 CSV: {OUTPUT_CSV_PATH}")
    return df


def latest_prompt_for(persona: str) -> str:
    pattern = f"q1_{persona}_*.csv"
    matches = sorted(Q1_OUTPUT_DIR.glob(pattern))
    if not matches:
        stop_missing(Q1_OUTPUT_DIR / pattern)
    latest = matches[-1]
    df = pd.read_csv(latest)
    if "prompt" not in df.columns and "prompt_preview" not in df.columns:
        raise ValueError(f"{latest} has no prompt or prompt_preview column.")
    column = "prompt" if "prompt" in df.columns else "prompt_preview"
    prompt = str(df.iloc[0][column])
    print(f"Loaded {persona} prompt from {latest}: {prompt[:80]}")
    return prompt


def load_model():
    require_path(MODEL_DIR)
    print(f"Loading model from {MODEL_DIR if MODEL_DIR.exists() else MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer


def layer45_hidden_states(model, tokenizer, prompt: str) -> torch.Tensor:
    encoded = tokenizer(prompt, return_tensors="pt")
    encoded = {key: value.to(model.device) for key, value in encoded.items()}
    with torch.no_grad():
        outputs = model(**encoded, output_hidden_states=True)
    return outputs.hidden_states[TARGET_LAYER + 1].detach().float().cpu().squeeze(0)


def part2_pooling_comparison() -> None:
    print("\nPART 2 - Pooling comparison at layer 45")
    proofreader_prompt = latest_prompt_for("proofreader")
    poet_prompt = latest_prompt_for("poet")
    model, tokenizer = load_model()

    proofreader_hidden = layer45_hidden_states(model, tokenizer, proofreader_prompt)
    poet_hidden = layer45_hidden_states(model, tokenizer, poet_prompt)

    proofreader_mean = proofreader_hidden.mean(dim=0)
    poet_mean = poet_hidden.mean(dim=0)
    proofreader_last = proofreader_hidden[-1]
    poet_last = poet_hidden[-1]

    print(f"mean_pooled_cosine: {cosine(proofreader_mean, poet_mean):.6f}")
    print(f"last_token_cosine: {cosine(proofreader_last, poet_last):.6f}")


def main() -> None:
    part1_layer_sweep()
    part2_pooling_comparison()


if __name__ == "__main__":
    main()
