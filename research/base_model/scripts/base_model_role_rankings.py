#!/usr/bin/env python3
"""Generate Gemma 2 27B base-model role vectors and rank them on the assistant axis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_DIR = Path("/root/models/gemma-2-27b-base")
AXIS_PATH = Path("/root/vectors/gemma-2-27b/assistant_axis.pt")
FULL_RANKING_PATH = Path("visualizations/full_ranking.csv")
OUTPUT_DIR = Path("research/base_model/outputs")
OFFLOAD_DIR = Path("/root/model_offload/gemma-2-27b-base")
LAYER = 45


def induction_prompts(role: str) -> list[str]:
    return [
        f"You are {role}, embodying the core essence of this role.",
        f"Embody the essence of {role}, its defining qualities.",
        f"You are {role} itself, in its purest form.",
        f"Take on the role of {role}, fully and completely.",
        f"Be {role}, as it is most essentially understood.",
    ]


def load_axis() -> torch.Tensor:
    axis = torch.load(AXIS_PATH, map_location="cpu")[LAYER].float()
    return -axis


def mean_pool(hidden: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.to(hidden.device, dtype=hidden.dtype).unsqueeze(-1)
    return (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)


def main() -> None:
    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Missing model directory: {MODEL_DIR}")
    if not AXIS_PATH.exists():
        raise FileNotFoundError(f"Missing assistant axis: {AXIS_PATH}")
    if not FULL_RANKING_PATH.exists():
        raise FileNotFoundError(f"Missing instruction ranking: {FULL_RANKING_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ranking_df = pd.read_csv(FULL_RANKING_PATH)
    role_col = "character" if "character" in ranking_df.columns else "role"
    roles = ranking_df[role_col].astype(str).tolist()
    instruct_rank = dict(zip(ranking_df[role_col].astype(str), ranking_df["rank"].astype(int)))

    axis = load_axis()

    print(f"Loading base model from {MODEL_DIR}")
    OFFLOAD_DIR.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_DIR,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        max_memory={0: "70GiB", "cpu": "120GiB"},
        offload_folder=str(OFFLOAD_DIR),
        offload_state_dict=True,
        local_files_only=True,
    )
    model.eval()

    captured: list[torch.Tensor] = []
    current_attention_mask: torch.Tensor | None = None

    def hook(_module, _inputs, output):
        hidden = output[0] if isinstance(output, tuple) else output
        if current_attention_mask is None:
            raise RuntimeError("attention mask was not set before forward pass")
        captured.append(mean_pool(hidden.float(), current_attention_mask).detach().cpu())

    handle = model.model.layers[LAYER].register_forward_hook(hook)
    role_vectors = []

    try:
        with torch.no_grad():
            for idx, role in enumerate(roles, start=1):
                prompt_vectors = []
                for prompt in induction_prompts(role):
                    inputs = tokenizer(
                        prompt,
                        return_tensors="pt",
                        truncation=True,
                        max_length=256,
                    )
                    device = next(model.parameters()).device
                    inputs = {k: v.to(device) for k, v in inputs.items()}
                    current_attention_mask = inputs["attention_mask"]
                    captured.clear()
                    _ = model(**inputs, use_cache=False)
                    if not captured:
                        raise RuntimeError(f"No layer-{LAYER} activation captured for {role}")
                    prompt_vectors.append(captured[-1].squeeze(0))
                role_vector = torch.stack(prompt_vectors).mean(dim=0)
                role_vectors.append(role_vector)
                print(f"[{idx:03d}/{len(roles)}] {role}")
    finally:
        handle.remove()

    role_matrix = torch.stack(role_vectors).float()
    centered = role_matrix - role_matrix.mean(dim=0, keepdim=True)
    projection_scores = centered @ axis

    base_df = pd.DataFrame({"role": roles, "projection_score": projection_scores.numpy()})
    base_df = base_df.sort_values("projection_score", ascending=False).reset_index(drop=True)
    base_df.insert(0, "rank", range(1, len(base_df) + 1))
    base_df.to_csv(OUTPUT_DIR / "base_model_full_ranking.csv", index=False)

    base_rank = dict(zip(base_df["role"], base_df["rank"]))
    comparison = pd.DataFrame(
        {
            "role": roles,
            "base_rank": [base_rank[r] for r in roles],
            "instruct_rank": [instruct_rank[r] for r in roles],
        }
    )
    comparison["rank_shift"] = comparison["base_rank"] - comparison["instruct_rank"]
    comparison["abs_rank_shift"] = comparison["rank_shift"].abs()
    comparison = comparison.sort_values(["abs_rank_shift", "role"], ascending=[False, True])
    comparison.to_csv(OUTPUT_DIR / "base_vs_instruct_comparison.csv", index=False)

    spearman = pd.Series(base_rank).corr(pd.Series(instruct_rank), method="spearman")
    top20 = base_df.head(20)
    bottom20 = base_df.tail(20).sort_values("rank")
    instruct_top20 = set(ranking_df.sort_values("rank").head(20)[role_col].astype(str))
    base_top20 = set(top20["role"])
    base_unique_top20 = sorted(base_top20 - instruct_top20)

    def rank_for(role: str) -> int | None:
        return int(base_rank[role]) if role in base_rank else None

    proxy_roles = [r for r in ["zealot", "purist", "narcissist"] if r in base_rank]

    summary = f"""Gemma 2 27B Base vs Instruction-Tuned Role Ranking
======================================================

Layer: {LAYER}
Model: google/gemma-2-27b base, loaded from {MODEL_DIR}
Axis: instruction-tuned assistant axis from {AXIS_PATH}, sign flipped
Role induction: 5 prompts per role, averaged after layer-{LAYER} mean pooling

Key ranks:
  assistant base rank: {rank_for("assistant")}
  assistant instruction-tuned rank: {instruct_rank.get("assistant")}
  proofreader base rank: {rank_for("proofreader")}
  proofreader instruction-tuned rank: {instruct_rank.get("proofreader")}
  poet base rank: {rank_for("poet")}
  poet instruction-tuned rank: {instruct_rank.get("poet")}

Spearman correlation base vs instruction-tuned rankings: {spearman:.6f}

Top 20 base-model roles:
{top20.to_string(index=False)}

Bottom 20 base-model roles:
{bottom20.to_string(index=False)}

Top 20 largest absolute rank shifts:
{comparison.head(20)[["role", "base_rank", "instruct_rank", "rank_shift"]].to_string(index=False)}

Roles unique to the base-model top 20 relative to instruction-tuned top 20:
{", ".join(base_unique_top20) if base_unique_top20 else "None"}

Dogmatic/elitist/nihilistic proxy check:
The 275-role inventory does not include literal elitist, dogmatist, or nihilist roles.
Available proxy roles are reported here:
{pd.DataFrame({"role": proxy_roles, "base_rank": [base_rank[r] for r in proxy_roles], "instruct_rank": [instruct_rank[r] for r in proxy_roles]}).to_string(index=False) if proxy_roles else "No proxy roles found."}
"""

    (OUTPUT_DIR / "base_vs_instruct_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
