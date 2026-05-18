#!/usr/bin/env python3
"""Compare centered assistant-axis role rankings for Gemma 2 27B and Qwen 3 32B."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[3]
VECTOR_ROOT = ROOT / "downloads" / "hf_vectors"
OUTPUT_DIR = ROOT / "research" / "cross_model" / "outputs"

MODELS = {
    "gemma": {
        "folder": "gemma-2-27b",
        "layer": 45,
    },
    "qwen": {
        "folder": "qwen-3-32b",
        "layer": None,
    },
}


def load_axis(model_dir: Path) -> torch.Tensor:
    axis_path = model_dir / "assistant_axis.pt"
    if not axis_path.exists():
        raise FileNotFoundError(f"Missing axis vector: {axis_path}")
    return torch.load(axis_path, map_location="cpu").float()


def load_role_tensor(model_dir: Path, role_names: list[str]) -> torch.Tensor:
    role_dir = model_dir / "role_vectors"
    if not role_dir.exists():
        raise FileNotFoundError(f"Missing role vector directory: {role_dir}")

    tensors = []
    for role in role_names:
        path = role_dir / f"{role}.pt"
        if not path.exists():
            raise FileNotFoundError(f"Missing role vector for {role}: {path}")
        tensors.append(torch.load(path, map_location="cpu").float())
    return torch.stack(tensors, dim=0)


def unit_rows(x: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    return x / x.norm(dim=-1, keepdim=True).clamp_min(eps)


def projection_by_layer(role_tensor: torch.Tensor, axis: torch.Tensor) -> torch.Tensor:
    axis_unit = unit_rows(axis)
    return torch.einsum("rld,ld->rl", role_tensor, axis_unit)


def centered_ranking(
    role_tensor: torch.Tensor,
    axis: torch.Tensor,
    layer: int,
    role_names: list[str],
) -> pd.DataFrame:
    layer_roles = role_tensor[:, layer, :]
    centered = layer_roles - layer_roles.mean(dim=0, keepdim=True)
    axis_unit = axis[layer] / axis[layer].norm().clamp_min(1e-12)
    scores = torch.mv(centered, axis_unit).cpu().numpy()
    df = pd.DataFrame({"role": role_names, "score": scores})
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


def orient_centered_axis(
    axis: torch.Tensor,
    role_tensor: torch.Tensor,
    layer: int,
    role_names: list[str],
    model_label: str,
) -> tuple[torch.Tensor, bool, float, float]:
    """Orient centered ranking so proofreader is assistant-aligned relative to poet.

    The raw activation projection sign convention and centered role-vector
    projection convention can differ because centering subtracts the shared
    role-vector component. For cross-model rank comparison, the score direction
    must be oriented so the known careful-evaluator anchor is above the known
    expressive anti-assistant anchor.
    """
    proofreader_idx = role_names.index("proofreader")
    poet_idx = role_names.index("poet")
    centered = role_tensor[:, layer, :] - role_tensor[:, layer, :].mean(dim=0, keepdim=True)
    axis_unit = axis[layer] / axis[layer].norm().clamp_min(1e-12)
    scores = torch.mv(centered, axis_unit)
    proofreader_score = float(scores[proofreader_idx].item())
    poet_score = float(scores[poet_idx].item())
    flipped_for_centered_ranking = proofreader_score < poet_score
    if flipped_for_centered_ranking:
        axis = -axis
        proofreader_score = -proofreader_score
        poet_score = -poet_score
    print(
        f"{model_label}: centered-rank orientation flip="
        f"{flipped_for_centered_ranking} "
        f"(proofreader={proofreader_score:.6f}, poet={poet_score:.6f})"
    )
    return axis, flipped_for_centered_ranking, proofreader_score, poet_score


def rank_map(ranking: pd.DataFrame) -> dict[str, int]:
    return dict(zip(ranking["role"], ranking["rank"]))


def spearman_from_ranks(a: dict[str, int], b: dict[str, int], roles: list[str]) -> float:
    n = len(roles)
    d2 = sum((a[role] - b[role]) ** 2 for role in roles)
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def format_ranking(rows: pd.DataFrame) -> str:
    lines = []
    for _, row in rows.iterrows():
        lines.append(f"{int(row['rank']):>3}. {row['role']:<24} {row['score']:>12.6f}")
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gemma_dir = VECTOR_ROOT / MODELS["gemma"]["folder"]
    qwen_dir = VECTOR_ROOT / MODELS["qwen"]["folder"]
    for path in [gemma_dir, qwen_dir]:
        if not path.exists():
            raise FileNotFoundError(f"Missing vector folder: {path}")

    gemma_roles = sorted(p.stem for p in (gemma_dir / "role_vectors").glob("*.pt"))
    qwen_roles = sorted(p.stem for p in (qwen_dir / "role_vectors").glob("*.pt"))
    shared_roles = sorted(set(gemma_roles) & set(qwen_roles))
    if len(shared_roles) != 275:
        print(f"WARNING: expected 275 shared roles, found {len(shared_roles)}")

    print(f"Loading {len(shared_roles)} shared roles")
    gemma_axis_original = load_axis(gemma_dir)
    # Established for raw activation projections: use -assistant_axis.pt.
    # Centered role-vector projections are re-oriented below against anchors.
    gemma_axis_raw_flipped = -gemma_axis_original
    gemma_tensor = load_role_tensor(gemma_dir, shared_roles)

    qwen_axis_original = load_axis(qwen_dir)
    qwen_tensor = load_role_tensor(qwen_dir, shared_roles)

    proofreader_idx = shared_roles.index("proofreader")
    poet_idx = shared_roles.index("poet")
    qwen_probe = projection_by_layer(qwen_tensor[[proofreader_idx, poet_idx]], qwen_axis_original)
    qwen_best_preflip = int(qwen_probe.var(dim=0).argmax().item())
    proofreader_probe = qwen_probe[0, qwen_best_preflip].item()
    poet_probe = qwen_probe[1, qwen_best_preflip].item()
    qwen_flip_needed = proofreader_probe < 0 and poet_probe < 0
    qwen_axis_raw_oriented = -qwen_axis_original if qwen_flip_needed else qwen_axis_original

    qwen_layer_projections = projection_by_layer(qwen_tensor, qwen_axis_raw_oriented)
    qwen_variances = qwen_layer_projections.var(dim=0, unbiased=False)
    qwen_layer = int(qwen_variances.argmax().item())

    gemma_layer = int(MODELS["gemma"]["layer"])
    gemma_axis, gemma_centered_flip, gemma_anchor_proof, gemma_anchor_poet = orient_centered_axis(
        gemma_axis_raw_flipped, gemma_tensor, gemma_layer, shared_roles, "Gemma"
    )
    qwen_axis, qwen_centered_flip, qwen_anchor_proof, qwen_anchor_poet = orient_centered_axis(
        qwen_axis_raw_oriented, qwen_tensor, qwen_layer, shared_roles, "Qwen"
    )
    gemma_ranking = centered_ranking(gemma_tensor, gemma_axis, gemma_layer, shared_roles)
    qwen_ranking = centered_ranking(qwen_tensor, qwen_axis, qwen_layer, shared_roles)

    comparison = pd.DataFrame(
        {
            "rank": range(1, len(shared_roles) + 1),
            "gemma_role": gemma_ranking["role"],
            "gemma_score": gemma_ranking["score"],
            "qwen_role": qwen_ranking["role"],
            "qwen_score": qwen_ranking["score"],
        }
    )
    comparison.to_csv(OUTPUT_DIR / "qwen_gemma_ranking_comparison.csv", index=False)

    gemma_rank_by_role = rank_map(gemma_ranking)
    qwen_rank_by_role = rank_map(qwen_ranking)
    spearman = spearman_from_ranks(gemma_rank_by_role, qwen_rank_by_role, shared_roles)

    gemma_top20 = set(gemma_ranking.head(20)["role"])
    qwen_top20 = set(qwen_ranking.head(20)["role"])
    gemma_only_top20 = sorted(gemma_top20 - qwen_top20, key=lambda r: gemma_rank_by_role[r])
    qwen_only_top20 = sorted(qwen_top20 - gemma_top20, key=lambda r: qwen_rank_by_role[r])

    summary = []
    summary.append("Qwen vs Gemma Assistant-Axis Ranking Comparison")
    summary.append("=" * 55)
    summary.append(f"Shared roles: {len(shared_roles)}")
    summary.append(f"Gemma layer: {gemma_layer}")
    summary.append("Gemma raw activation sign flip applied before centered-rank orientation: True")
    summary.append(f"Gemma centered-rank orientation flip applied: {gemma_centered_flip}")
    summary.append(f"Gemma centered anchor scores: proofreader={gemma_anchor_proof:.6f}, poet={gemma_anchor_poet:.6f}")
    summary.append(f"Qwen raw sign flip needed: {qwen_flip_needed}")
    summary.append(f"Qwen centered-rank orientation flip applied: {qwen_centered_flip}")
    summary.append(f"Qwen centered anchor scores: proofreader={qwen_anchor_proof:.6f}, poet={qwen_anchor_poet:.6f}")
    summary.append(f"Qwen probe layer for sign check: {qwen_best_preflip}")
    summary.append(f"Qwen proofreader projection before flip: {proofreader_probe:.6f}")
    summary.append(f"Qwen poet projection before flip: {poet_probe:.6f}")
    summary.append(f"Qwen most discriminative layer: {qwen_layer}")
    summary.append(f"Qwen max projection variance: {qwen_variances[qwen_layer].item():.6f}")
    summary.append(f"Spearman rank correlation: {spearman:.6f}")
    summary.append("")
    summary.append("Side-by-side top 20")
    summary.append("rank | gemma_role | gemma_score | qwen_role | qwen_score")
    summary.append("-" * 75)
    for i in range(20):
        g = gemma_ranking.iloc[i]
        q = qwen_ranking.iloc[i]
        summary.append(
            f"{i + 1:>4} | {g['role']:<24} | {g['score']:>12.6f} | "
            f"{q['role']:<24} | {q['score']:>12.6f}"
        )
    summary.append("")
    summary.append("Gemma bottom 20")
    summary.append(format_ranking(gemma_ranking.tail(20)))
    summary.append("")
    summary.append("Qwen bottom 20")
    summary.append(format_ranking(qwen_ranking.tail(20)))
    summary_text = "\n".join(summary)
    (OUTPUT_DIR / "qwen_gemma_top20_bottom20.txt").write_text(summary_text + "\n")

    divergent = []
    divergent.append("Structurally divergent top-20 roles")
    divergent.append("=" * 40)
    divergent.append("")
    divergent.append("In Gemma top 20 but not Qwen top 20:")
    for role in gemma_only_top20:
        divergent.append(
            f"- {role}: Gemma rank {gemma_rank_by_role[role]}, Qwen rank {qwen_rank_by_role[role]}"
        )
    divergent.append("")
    divergent.append("In Qwen top 20 but not Gemma top 20:")
    for role in qwen_only_top20:
        divergent.append(
            f"- {role}: Qwen rank {qwen_rank_by_role[role]}, Gemma rank {gemma_rank_by_role[role]}"
        )
    divergent.append("")
    divergent.append("Largest absolute rank shifts:")
    shifts = sorted(
        ((role, gemma_rank_by_role[role], qwen_rank_by_role[role], abs(gemma_rank_by_role[role] - qwen_rank_by_role[role])) for role in shared_roles),
        key=lambda item: item[3],
        reverse=True,
    )
    for role, gr, qr, shift in shifts[:25]:
        divergent.append(f"- {role}: Gemma rank {gr}, Qwen rank {qr}, shift {shift}")
    divergent_text = "\n".join(divergent)
    (OUTPUT_DIR / "qwen_gemma_divergent_roles.txt").write_text(divergent_text + "\n")

    print(summary_text)
    print("")
    print(divergent_text)


if __name__ == "__main__":
    main()
