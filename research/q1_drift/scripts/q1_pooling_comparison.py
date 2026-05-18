from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F


REPO_ROOT = Path(__file__).resolve().parents[3]
ROLE_VECTOR_DIR = REPO_ROOT / "downloads" / "hf_vectors" / "gemma-2-27b" / "role_vectors"
FULL_RANKING_PATH = REPO_ROOT / "visualizations" / "full_ranking.csv"
OUTPUT_DIR = REPO_ROOT / "research" / "q1_drift" / "outputs"
BY_LAYER_CSV = OUTPUT_DIR / "q1_pooling_centered_by_layer.csv"
DISTRIBUTION_TXT = OUTPUT_DIR / "q1_pooling_distribution_layer45.txt"
EXPECTED_ROLE_SHAPE = (46, 4608)
EXPECTED_STACKED_SHAPE = (275, 46, 4608)
TARGET_LAYER = 45


def require_path(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"MISSING PATH: {path}")


def role_to_filename(role: str) -> str:
    return role.strip().lower().replace(" ", "_")


def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(F.cosine_similarity(a.flatten(), b.flatten(), dim=0).item())


def percentile_le(values: torch.Tensor, value: float) -> float:
    """Percentile by share of values <= value. Low means less similar."""
    return float((values <= value).float().mean().item() * 100.0)


def load_roles() -> tuple[list[str], torch.Tensor]:
    require_path(FULL_RANKING_PATH)
    require_path(ROLE_VECTOR_DIR)

    roles = pd.read_csv(FULL_RANKING_PATH)["character"].astype(str).tolist()
    tensors: list[torch.Tensor] = []
    for role in roles:
        path = ROLE_VECTOR_DIR / f"{role_to_filename(role)}.pt"
        require_path(path)
        tensor = torch.load(path, map_location="cpu").float()
        if tuple(tensor.shape) != EXPECTED_ROLE_SHAPE:
            raise ValueError(f"Unexpected tensor shape for {path}: {tuple(tensor.shape)}")
        tensors.append(tensor)

    role_tensor = torch.stack(tensors, dim=0)
    if tuple(role_tensor.shape) != EXPECTED_STACKED_SHAPE:
        raise ValueError(
            f"Expected stacked role tensor shape {EXPECTED_STACKED_SHAPE}, got {tuple(role_tensor.shape)}"
        )
    return roles, role_tensor


def centered_matrix(role_tensor: torch.Tensor, layer: int) -> torch.Tensor:
    layer_matrix = role_tensor[:, layer, :]
    return layer_matrix - layer_matrix.mean(dim=0, keepdim=True)


def layer_sweep(roles: list[str], role_tensor: torch.Tensor) -> pd.DataFrame:
    proofreader_idx = roles.index("proofreader")
    poet_idx = roles.index("poet")
    rows = []

    for layer in range(role_tensor.shape[1]):
        raw = cosine(role_tensor[proofreader_idx, layer, :], role_tensor[poet_idx, layer, :])
        centered = centered_matrix(role_tensor, layer)
        centered_value = cosine(centered[proofreader_idx], centered[poet_idx])
        rows.append(
            {
                "layer": layer,
                "raw_cosine_proofreader_poet": raw,
                "centered_cosine_proofreader_poet": centered_value,
            }
        )

    df = pd.DataFrame(rows)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(BY_LAYER_CSV, index=False)
    return df


def layer45_distribution_report(roles: list[str], role_tensor: torch.Tensor, by_layer: pd.DataFrame) -> str:
    proofreader_idx = roles.index("proofreader")
    poet_idx = roles.index("poet")
    centered = centered_matrix(role_tensor, TARGET_LAYER)
    proofreader = centered[proofreader_idx]

    values = torch.tensor([cosine(proofreader, centered[idx]) for idx in range(len(roles))])
    raw_poet = cosine(role_tensor[proofreader_idx, TARGET_LAYER, :], role_tensor[poet_idx, TARGET_LAYER, :])
    centered_poet = float(values[poet_idx].item())

    ranked_desc = sorted(
        (
            {
                "role": role,
                "centered_cosine": float(values[idx].item()),
                "percentile_le": percentile_le(values, float(values[idx].item())),
            }
            for idx, role in enumerate(roles)
        ),
        key=lambda row: row["centered_cosine"],
        reverse=True,
    )
    for rank, row in enumerate(ranked_desc, start=1):
        row["similarity_rank"] = rank

    poet_rank = next(row["similarity_rank"] for row in ranked_desc if row["role"] == "poet")
    poet_percentile = percentile_le(values, centered_poet)
    editorial_neighbors = [row for row in ranked_desc if row["role"] != "proofreader"][:10]

    most_negative_row = by_layer.loc[
        by_layer["centered_cosine_proofreader_poet"].idxmin()
    ]
    max_sep_layer = int(most_negative_row["layer"])
    max_sep_value = float(most_negative_row["centered_cosine_proofreader_poet"])
    layer45_value = float(
        by_layer.loc[
            by_layer["layer"] == TARGET_LAYER, "centered_cosine_proofreader_poet"
        ].iloc[0]
    )

    lines = [
        "Q1 pooling comparison: proofreader vs poet",
        "",
        "Input tensor:",
        f"- role_tensor_shape: {tuple(role_tensor.shape)}",
        f"- target_layer: {TARGET_LAYER}",
        "- note: vectors are pre-computed role representations; no model weights or fresh inference were used.",
        "",
        "Layer 45 proofreader vs poet:",
        f"- raw_cosine: {raw_poet:.6f}",
        f"- centered_cosine: {centered_poet:.6f}",
        f"- poet_similarity_rank: {poet_rank} of {len(roles)} (1 = most similar to proofreader)",
        f"- poet_percentile_le: {poet_percentile:.2f} (share of roles with centered cosine <= poet)",
        "",
        "Layer 45 proofreader-vs-all centered cosine distribution:",
        f"- min: {float(values.min().item()):.6f}",
        f"- max: {float(values.max().item()):.6f}",
        f"- mean: {float(values.mean().item()):.6f}",
        f"- std: {float(values.std(unbiased=False).item()):.6f}",
        "",
        "Top-10 editorial neighbors at layer 45 after centering (defined as nearest non-proofreader roles to proofreader):",
        "rank,role,centered_cosine,percentile_le",
    ]
    lines.extend(
        f"{row['similarity_rank']},{row['role']},{row['centered_cosine']:.6f},{row['percentile_le']:.2f}"
        for row in editorial_neighbors
    )
    lines.extend(
        [
            "",
            "Across-layer separation:",
            f"- most_negative_layer: {max_sep_layer}",
            f"- most_negative_centered_cosine: {max_sep_value:.6f}",
            f"- layer45_centered_cosine: {layer45_value:.6f}",
            f"- differs_from_layer45: {max_sep_layer != TARGET_LAYER}",
            "",
            "Interpretation:",
            "- The stored vectors already use the original authors' pooling method, so this closes the remaining Q1 ambiguity at the level of available pre-computed geometry rather than by re-running token-level inference.",
            "- Mean-centering remains the necessary operation for proofreader/poet separation; raw cosine is still saturated at layer 45.",
        ]
    )
    report = "\n".join(lines) + "\n"
    DISTRIBUTION_TXT.write_text(report)
    return report


def main() -> None:
    roles, role_tensor = load_roles()
    by_layer = layer_sweep(roles, role_tensor)
    report = layer45_distribution_report(roles, role_tensor, by_layer)
    print(f"Saved: {BY_LAYER_CSV}")
    print(f"Saved: {DISTRIBUTION_TXT}")
    print()
    print(report)


if __name__ == "__main__":
    main()
