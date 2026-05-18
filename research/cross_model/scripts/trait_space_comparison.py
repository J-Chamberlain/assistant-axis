#!/usr/bin/env python3
"""Compare assistant-axis trait-space rankings across cached model vectors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[3]
VECTOR_ROOT = ROOT / "downloads" / "hf_vectors"
OUTPUT_DIR = ROOT / "research" / "cross_model" / "outputs"
ROLE_SPEARMAN_BASELINE = 0.670267


@dataclass(frozen=True)
class ModelConfig:
    key: str
    label: str
    folder: str
    layer: int | None
    raw_axis_sign: int = 1


MODEL_CONFIGS = [
    ModelConfig("gemma", "Gemma 2 27B", "gemma-2-27b", 45, -1),
    ModelConfig("qwen", "Qwen 3 32B", "qwen-3-32b", 63, 1),
    ModelConfig("llama", "Llama", "llama-3.3-70b", None, 1),
]


def load_vector_dir(vector_dir: Path, names: list[str]) -> torch.Tensor:
    tensors = []
    for name in names:
        path = vector_dir / f"{name}.pt"
        if not path.exists():
            raise FileNotFoundError(f"Missing vector for {name}: {path}")
        tensors.append(torch.load(path, map_location="cpu").float())
    return torch.stack(tensors, dim=0)


def load_axis(model_dir: Path) -> torch.Tensor:
    axis_path = model_dir / "assistant_axis.pt"
    if not axis_path.exists():
        raise FileNotFoundError(f"Missing assistant axis: {axis_path}")
    return torch.load(axis_path, map_location="cpu").float()


def unit_vector(x: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    return x / x.norm().clamp_min(eps)


def rank_map(df: pd.DataFrame, item_col: str = "trait") -> dict[str, int]:
    return dict(zip(df[item_col], df["rank"]))


def spearman_from_ranks(a: dict[str, int], b: dict[str, int], items: list[str]) -> float:
    n = len(items)
    d2 = sum((a[item] - b[item]) ** 2 for item in items)
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def available_model_dirs() -> dict[str, Path]:
    found = {}
    for config in MODEL_CONFIGS:
        model_dir = VECTOR_ROOT / config.folder
        if model_dir.exists() and (model_dir / "trait_vectors").exists() and (model_dir / "assistant_axis.pt").exists():
            found[config.key] = model_dir
    return found


def choose_layer(config: ModelConfig, model_dir: Path, axis: torch.Tensor, role_names: list[str]) -> int:
    if config.layer is not None:
        return config.layer
    role_dir = model_dir / "role_vectors"
    if not role_dir.exists() or not role_names:
        raise ValueError(f"No explicit layer for {config.label}, and role vectors are unavailable for layer detection.")
    role_tensor = load_vector_dir(role_dir, role_names)
    axis_oriented = axis * config.raw_axis_sign
    axis_unit = axis_oriented / axis_oriented.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    projections = torch.einsum("rld,ld->rl", role_tensor, axis_unit)
    return int(projections.var(dim=0, unbiased=False).argmax().item())


def orient_axis_with_role_anchors(
    axis: torch.Tensor,
    model_dir: Path,
    layer: int,
    role_names: list[str],
    config: ModelConfig,
) -> tuple[torch.Tensor, bool, float, float]:
    role_dir = model_dir / "role_vectors"
    if not role_dir.exists() or "proofreader" not in role_names or "poet" not in role_names:
        return axis * config.raw_axis_sign, False, float("nan"), float("nan")

    anchor_roles = ["proofreader", "poet"]
    role_tensor = load_vector_dir(role_dir, anchor_roles)
    centered_reference = load_vector_dir(role_dir, role_names)[:, layer, :].mean(dim=0, keepdim=True)
    centered_anchors = role_tensor[:, layer, :] - centered_reference

    oriented_axis = axis * config.raw_axis_sign
    axis_unit = unit_vector(oriented_axis[layer])
    scores = torch.mv(centered_anchors, axis_unit)
    proofreader_score = float(scores[0].item())
    poet_score = float(scores[1].item())
    flipped = proofreader_score < poet_score
    if flipped:
        oriented_axis = -oriented_axis
        proofreader_score = -proofreader_score
        poet_score = -poet_score
    return oriented_axis, flipped, proofreader_score, poet_score


def trait_ranking(
    trait_tensor: torch.Tensor,
    axis: torch.Tensor,
    layer: int,
    trait_names: list[str],
) -> pd.DataFrame:
    layer_traits = trait_tensor[:, layer, :]
    centered = layer_traits - layer_traits.mean(dim=0, keepdim=True)
    axis_unit = unit_vector(axis[layer])
    scores = torch.mv(centered, axis_unit).cpu().numpy()
    df = pd.DataFrame({"trait": trait_names, "score": scores})
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


def centered_axis_ranking(
    tensor: torch.Tensor,
    axis: torch.Tensor,
    layer: int,
    names: list[str],
    item_col: str,
) -> pd.DataFrame:
    layer_items = tensor[:, layer, :]
    centered = layer_items - layer_items.mean(dim=0, keepdim=True)
    axis_unit = unit_vector(axis[layer])
    scores = torch.mv(centered, axis_unit).cpu().numpy()
    df = pd.DataFrame({item_col: names, "score": scores})
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


def centered_layer_matrix(tensor: torch.Tensor, layer: int) -> torch.Tensor:
    layer_tensor = tensor[:, layer, :]
    return layer_tensor - layer_tensor.mean(dim=0, keepdim=True)


def role_trait_signature(
    model_dir: Path,
    layer: int,
    role: str,
    trait_names: list[str],
) -> pd.DataFrame:
    role_vec = torch.load(model_dir / "role_vectors" / f"{role}.pt", map_location="cpu").float()[layer]
    all_roles = sorted(p.stem for p in (model_dir / "role_vectors").glob("*.pt"))
    role_reference = load_vector_dir(model_dir / "role_vectors", all_roles)[:, layer, :].mean(dim=0)
    role_centered = unit_vector(role_vec - role_reference)

    trait_tensor = load_vector_dir(model_dir / "trait_vectors", trait_names)
    trait_centered = centered_layer_matrix(trait_tensor, layer)
    trait_unit = trait_centered / trait_centered.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    scores = torch.mv(trait_unit, role_centered).cpu().numpy()
    df = pd.DataFrame({"trait": trait_names, "score": scores})
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


def format_top_bottom(label: str, ranking: pd.DataFrame, n: int = 10) -> list[str]:
    lines = [label, "-" * len(label), "Top 10"]
    for _, row in ranking.head(n).iterrows():
        lines.append(f"{int(row['rank']):>3}. {row['trait']:<28} {row['score']:>12.6f}")
    lines.append("")
    lines.append("Bottom 10")
    for _, row in ranking.tail(n).iterrows():
        lines.append(f"{int(row['rank']):>3}. {row['trait']:<28} {row['score']:>12.6f}")
    return lines


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    found_dirs = available_model_dirs()
    if "gemma" not in found_dirs or "qwen" not in found_dirs:
        raise FileNotFoundError("Gemma and Qwen trait vectors are required for this comparison.")

    cache_lines = ["Trait vector cache inventory", "=" * 28]
    active_configs = []
    for config in MODEL_CONFIGS:
        model_dir = VECTOR_ROOT / config.folder
        trait_dir = model_dir / "trait_vectors"
        role_dir = model_dir / "role_vectors"
        trait_count = len(list(trait_dir.glob("*.pt"))) if trait_dir.exists() else 0
        role_count = len(list(role_dir.glob("*.pt"))) if role_dir.exists() else 0
        axis_exists = (model_dir / "assistant_axis.pt").exists()
        cache_lines.append(
            f"{config.label}: traits={trait_count}, roles={role_count}, "
            f"axis={axis_exists}, path={trait_dir if trait_dir.exists() else 'missing'}"
        )
        if config.key in found_dirs:
            active_configs.append(config)

    trait_sets = {
        config.key: {p.stem for p in (found_dirs[config.key] / "trait_vectors").glob("*.pt")}
        for config in active_configs
    }
    shared_traits = sorted(set.intersection(*trait_sets.values()))
    if len(shared_traits) != 240:
        print(f"WARNING: expected 240 shared traits, found {len(shared_traits)}")

    role_sets = {
        config.key: {p.stem for p in (found_dirs[config.key] / "role_vectors").glob("*.pt")}
        for config in active_configs
        if (found_dirs[config.key] / "role_vectors").exists()
    }
    shared_roles = sorted(set.intersection(*role_sets.values())) if role_sets else []

    rankings: dict[str, pd.DataFrame] = {}
    role_rankings: dict[str, pd.DataFrame] = {}
    axes: dict[str, torch.Tensor] = {}
    layers: dict[str, int] = {}
    orientation_lines = ["", "Axis orientation", "=" * 16]

    for config in active_configs:
        model_dir = found_dirs[config.key]
        axis = load_axis(model_dir)
        layer = choose_layer(config, model_dir, axis, shared_roles)
        role_names = sorted(p.stem for p in (model_dir / "role_vectors").glob("*.pt"))
        oriented_axis, flipped, proofreader_score, poet_score = orient_axis_with_role_anchors(
            axis, model_dir, layer, role_names, config
        )
        trait_tensor = load_vector_dir(model_dir / "trait_vectors", shared_traits)
        rankings[config.key] = trait_ranking(trait_tensor, oriented_axis, layer, shared_traits)
        if role_names:
            role_tensor = load_vector_dir(model_dir / "role_vectors", role_names)
            role_rankings[config.key] = centered_axis_ranking(
                role_tensor, oriented_axis, layer, role_names, "role"
            )
        axes[config.key] = oriented_axis
        layers[config.key] = layer
        orientation_lines.append(
            f"{config.label}: layer={layer}, raw_axis_sign={config.raw_axis_sign}, "
            f"centered_anchor_flip={flipped}, proofreader={proofreader_score:.6f}, poet={poet_score:.6f}"
        )

    rank_maps = {key: rank_map(df) for key, df in rankings.items()}
    pair_names = [("gemma", "qwen"), ("gemma", "llama"), ("qwen", "llama")]
    correlations: dict[tuple[str, str], float] = {}
    for left, right in pair_names:
        if left in rank_maps and right in rank_maps:
            correlations[(left, right)] = spearman_from_ranks(rank_maps[left], rank_maps[right], shared_traits)

    score_maps = {
        key: dict(zip(df["trait"], df["score"]))
        for key, df in rankings.items()
    }
    comparison_rows = []
    for trait in shared_traits:
        row = {"trait": trait}
        ranks_for_trait = []
        for config in active_configs:
            row[f"{config.key}_rank"] = rank_maps[config.key][trait]
            row[f"{config.key}_score"] = score_maps[config.key][trait]
            ranks_for_trait.append(rank_maps[config.key][trait])
        if "gemma" in rank_maps and "qwen" in rank_maps:
            row["gemma_qwen_abs_rank_shift"] = abs(rank_maps["gemma"][trait] - rank_maps["qwen"][trait])
        if "gemma" in rank_maps and "llama" in rank_maps:
            row["gemma_llama_abs_rank_shift"] = abs(rank_maps["gemma"][trait] - rank_maps["llama"][trait])
        if "qwen" in rank_maps and "llama" in rank_maps:
            row["qwen_llama_abs_rank_shift"] = abs(rank_maps["qwen"][trait] - rank_maps["llama"][trait])
        row["mean_rank"] = sum(ranks_for_trait) / len(ranks_for_trait)
        row["rank_range"] = max(ranks_for_trait) - min(ranks_for_trait)
        comparison_rows.append(row)
    comparison = pd.DataFrame(comparison_rows).sort_values(["mean_rank", "rank_range", "trait"])
    comparison.to_csv(OUTPUT_DIR / "trait_space_comparison.csv", index=False)

    summary_lines = []
    summary_lines.extend(cache_lines)
    summary_lines.extend(orientation_lines)
    summary_lines.extend(["", "Spearman rank correlations", "=" * 26])
    for left, right in pair_names:
        if (left, right) in correlations:
            summary_lines.append(f"{left} vs {right}: {correlations[(left, right)]:.6f}")
    if ("gemma", "qwen") in correlations:
        relation = "more" if correlations[("gemma", "qwen")] > ROLE_SPEARMAN_BASELINE else "less"
        summary_lines.append(
            f"Gemma/Qwen trait-space convergence is {relation} convergent than role-space "
            f"ranking convergence ({correlations[('gemma', 'qwen')]:.6f} vs {ROLE_SPEARMAN_BASELINE:.6f})."
        )
    summary_lines.append("")
    for config in active_configs:
        summary_lines.extend(format_top_bottom(f"{config.label} trait ranking", rankings[config.key]))
        summary_lines.append("")
    (OUTPUT_DIR / "trait_space_top10_bottom10.txt").write_text("\n".join(summary_lines).rstrip() + "\n")

    divergent_lines = []
    divergent_lines.extend(cache_lines)
    divergent_lines.extend(orientation_lines)
    divergent_lines.extend(["", "Largest Gemma vs Qwen trait rank shifts", "=" * 41])
    if "gemma" in rank_maps and "qwen" in rank_maps:
        shifts = sorted(
            (
                (
                    trait,
                    rank_maps["gemma"][trait],
                    rank_maps["qwen"][trait],
                    abs(rank_maps["gemma"][trait] - rank_maps["qwen"][trait]),
                )
                for trait in shared_traits
            ),
            key=lambda item: item[3],
            reverse=True,
        )
        for trait, g_rank, q_rank, shift in shifts[:20]:
            divergent_lines.append(f"- {trait}: Gemma rank {g_rank}, Qwen rank {q_rank}, shift {shift}")

    divergent_lines.extend(["", "Convergent top-role trait-signature cross-reference", "=" * 53])
    if role_rankings:
        top20_sets = {
            key: set(df.head(20)["role"])
            for key, df in role_rankings.items()
        }
        convergent_roles = sorted(set.intersection(*top20_sets.values()))
        model_keys_for_roles = [config.key for config in active_configs if config.key in role_rankings]
        divergent_lines.append(
            "Shared top-20 roles considered across "
            f"{', '.join(model_keys_for_roles)}: {', '.join(convergent_roles) if convergent_roles else 'none'}"
        )
        for role in convergent_roles:
            role_lines = [f"", f"Role: {role}"]
            signatures = {}
            for config in active_configs:
                if config.key in role_rankings and (found_dirs[config.key] / "role_vectors" / f"{role}.pt").exists():
                    signatures[config.key] = role_trait_signature(
                        found_dirs[config.key], layers[config.key], role, shared_traits
                    )
                    top_traits = ", ".join(signatures[config.key].head(5)["trait"].tolist())
                    role_lines.append(f"- {config.label} top traits: {top_traits}")
            if "gemma" in signatures and "qwen" in signatures:
                role_corr = spearman_from_ranks(rank_map(signatures["gemma"]), rank_map(signatures["qwen"]), shared_traits)
                shared_top10 = sorted(set(signatures["gemma"].head(10)["trait"]) & set(signatures["qwen"].head(10)["trait"]))
                role_lines.append(f"- Gemma/Qwen trait-signature Spearman: {role_corr:.6f}")
                role_lines.append(f"- Shared top-10 signature traits: {', '.join(shared_top10) if shared_top10 else 'none'}")
            if "gemma" in signatures and "llama" in signatures:
                role_corr = spearman_from_ranks(rank_map(signatures["gemma"]), rank_map(signatures["llama"]), shared_traits)
                role_lines.append(f"- Gemma/Llama trait-signature Spearman: {role_corr:.6f}")
            if "qwen" in signatures and "llama" in signatures:
                role_corr = spearman_from_ranks(rank_map(signatures["qwen"]), rank_map(signatures["llama"]), shared_traits)
                role_lines.append(f"- Qwen/Llama trait-signature Spearman: {role_corr:.6f}")
            divergent_lines.extend(role_lines)
    (OUTPUT_DIR / "trait_space_divergent_traits.txt").write_text("\n".join(divergent_lines).rstrip() + "\n")

    print("\n".join(summary_lines))


if __name__ == "__main__":
    main()
