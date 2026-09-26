from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F
from tqdm import tqdm


REPO_ROOT = Path(__file__).resolve().parents[3]
ROLE_VECTOR_DIR = REPO_ROOT / "downloads" / "hf_vectors" / "gemma-2-27b" / "role_vectors"
FULL_RANKING_PATH = REPO_ROOT / "visualizations" / "full_ranking.csv"
RAW_COSINE_PATH = REPO_ROOT / "research" / "q1_drift" / "outputs" / "cosine_by_layer.csv"
OUTPUT_PATH = REPO_ROOT / "research" / "q1_drift" / "outputs" / "centered_cosine_by_layer.csv"
EXPECTED_SHAPE = (46, 4608)
TARGET_LAYER = 45


def stop_missing(path: Path) -> None:
    print(f"MISSING PATH: {path}")
    raise SystemExit(1)


def require_path(path: Path) -> None:
    if not path.exists():
        stop_missing(path)


def role_to_filename(role: str) -> str:
    return role.strip().lower().replace(" ", "_")


def cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(F.cosine_similarity(a.flatten(), b.flatten(), dim=0).item())


def load_roles() -> tuple[list[str], torch.Tensor]:
    require_path(FULL_RANKING_PATH)
    require_path(ROLE_VECTOR_DIR)

    ranking = pd.read_csv(FULL_RANKING_PATH)
    roles = ranking["character"].astype(str).tolist()
    tensors = []

    for role in tqdm(roles, desc="Loading role vectors"):
        path = ROLE_VECTOR_DIR / f"{role_to_filename(role)}.pt"
        if not path.exists():
            stop_missing(path)
        tensor = torch.load(path, map_location="cpu")
        if tuple(tensor.shape) != EXPECTED_SHAPE:
            raise ValueError(f"Unexpected tensor shape for {path}: {tuple(tensor.shape)}")
        tensors.append(tensor.float())

    stacked = torch.stack(tensors, dim=0)
    if tuple(stacked.shape) != (275, 46, 4608):
        raise ValueError(f"Expected stacked role tensor shape (275, 46, 4608), got {tuple(stacked.shape)}")
    return roles, stacked


def load_raw_cosines() -> pd.DataFrame:
    require_path(RAW_COSINE_PATH)
    raw = pd.read_csv(RAW_COSINE_PATH)
    if set(raw.columns) != {"layer", "cosine_similarity"}:
        raise ValueError(f"Unexpected raw cosine columns in {RAW_COSINE_PATH}: {list(raw.columns)}")
    return raw.rename(columns={"cosine_similarity": "raw_cosine"})


def centered_layer_matrix(role_tensor: torch.Tensor, layer: int) -> torch.Tensor:
    layer_matrix = role_tensor[:, layer, :]
    return layer_matrix - layer_matrix.mean(dim=0, keepdim=True)


def layer_sweep(roles: list[str], role_tensor: torch.Tensor, raw_cosines: pd.DataFrame) -> pd.DataFrame:
    proofreader_idx = roles.index("proofreader")
    poet_idx = roles.index("poet")
    records = []

    print("layer | raw_cosine | centered_cosine")
    for layer in range(role_tensor.shape[1]):
        centered = centered_layer_matrix(role_tensor, layer)
        centered_cosine = cosine(centered[proofreader_idx], centered[poet_idx])
        raw_value = float(raw_cosines.loc[raw_cosines["layer"] == layer, "raw_cosine"].iloc[0])
        records.append(
            {
                "layer": layer,
                "raw_cosine": raw_value,
                "centered_cosine": centered_cosine,
            }
        )
        print(f"{layer:02d} | {raw_value:.6f} | {centered_cosine:.6f}")

    df = pd.DataFrame(records)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved centered cosine table: {OUTPUT_PATH}")
    return df


def layer45_rank_report(roles: list[str], role_tensor: torch.Tensor) -> None:
    proofreader_idx = roles.index("proofreader")
    poet_idx = roles.index("poet")
    centered = centered_layer_matrix(role_tensor, TARGET_LAYER)
    proofreader = centered[proofreader_idx]

    rows = []
    for idx, role in enumerate(roles):
        rows.append(
            {
                "rank": None,
                "role": role,
                "centered_cosine": cosine(proofreader, centered[idx]),
            }
        )

    sorted_rows = sorted(rows, key=lambda row: row["centered_cosine"], reverse=True)
    for rank, row in enumerate(sorted_rows, start=1):
        row["rank"] = rank

    poet_row = next(row for row in sorted_rows if row["role"] == "poet")
    print(f"\nLayer {TARGET_LAYER} proofreader vs all roles after centering")
    print(
        f"Poet rank: {poet_row['rank']} of {len(sorted_rows)} "
        f"(rank 1 = most similar), centered_cosine={poet_row['centered_cosine']:.6f}"
    )

    print("\nTop 10 most similar to proofreader after centering:")
    print("rank | role | centered_cosine")
    for row in sorted_rows[:10]:
        print(f"{row['rank']:03d} | {row['role']} | {row['centered_cosine']:.6f}")

    print("\nBottom 10 most similar to proofreader after centering:")
    print("rank | role | centered_cosine")
    for row in sorted_rows[-10:]:
        print(f"{row['rank']:03d} | {row['role']} | {row['centered_cosine']:.6f}")


def main() -> None:
    roles, role_tensor = load_roles()
    raw_cosines = load_raw_cosines()
    layer_sweep(roles, role_tensor, raw_cosines)
    layer45_rank_report(roles, role_tensor)


if __name__ == "__main__":
    main()
