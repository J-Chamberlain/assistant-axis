from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F


REPO_ROOT = Path(__file__).resolve().parents[3]
ROLE_VECTOR_DIR = REPO_ROOT / "downloads" / "hf_vectors" / "gemma-2-27b" / "role_vectors"
ASSIGNMENTS_PATH = REPO_ROOT / "visualizations" / "full_ranking.csv"
OUTPUT_PATH = REPO_ROOT / "research" / "q2_stability" / "gemma" / "outputs" / "calibration" / "centroid_representatives.txt"
LAYER = 45
EXPECTED_ROLE_SHAPE = (46, 4608)
EXPECTED_N_ROLES = 275
CLUSTERS = [
    "editorial",
    "procedural_professional",
    "grounded_social",
    "mythic_spiritual",
    "trickster_chaos",
    "combative_iconoclast",
    "other",
]


def require_path(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required path: {path}")


def role_to_filename(role: str) -> str:
    return role.strip().lower().replace(" ", "_")


def load_assignments() -> pd.DataFrame:
    require_path(ASSIGNMENTS_PATH)
    df = pd.read_csv(ASSIGNMENTS_PATH)

    role_col = "role" if "role" in df.columns else "character"
    cluster_col = "cluster" if "cluster" in df.columns else "cluster_label"
    required = {role_col, cluster_col, "rank"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {ASSIGNMENTS_PATH}: {sorted(missing)}")

    normalized = df.rename(
        columns={role_col: "role", cluster_col: "cluster", "rank": "axis_rank"}
    )[["role", "cluster", "axis_rank"]].copy()
    normalized["role"] = normalized["role"].astype(str)
    normalized["cluster"] = normalized["cluster"].astype(str)
    normalized["axis_rank"] = normalized["axis_rank"].astype(int)

    if len(normalized) != EXPECTED_N_ROLES:
        raise ValueError(f"Expected {EXPECTED_N_ROLES} roles, got {len(normalized)}")

    observed = set(normalized["cluster"])
    expected = set(CLUSTERS)
    if observed != expected:
        raise ValueError(
            f"Unexpected cluster labels. Missing={sorted(expected - observed)}, extra={sorted(observed - expected)}"
        )

    return normalized


def load_layer_vectors(roles: list[str]) -> torch.Tensor:
    require_path(ROLE_VECTOR_DIR)
    vectors = []
    for role in roles:
        path = ROLE_VECTOR_DIR / f"{role_to_filename(role)}.pt"
        require_path(path)
        tensor = torch.load(path, map_location="cpu").float()
        if tuple(tensor.shape) != EXPECTED_ROLE_SHAPE:
            raise ValueError(f"Unexpected tensor shape for {path}: {tuple(tensor.shape)}")
        vectors.append(tensor[LAYER])

    stacked = torch.stack(vectors, dim=0)
    if tuple(stacked.shape) != (EXPECTED_N_ROLES, EXPECTED_ROLE_SHAPE[1]):
        raise ValueError(f"Unexpected layer slice shape: {tuple(stacked.shape)}")
    return stacked


def cosine_to_centroid(member_vectors: torch.Tensor) -> torch.Tensor:
    centroid = member_vectors.mean(dim=0, keepdim=True)
    return F.cosine_similarity(member_vectors, centroid.expand_as(member_vectors), dim=1)


def format_table(rows: list[dict[str, object]]) -> str:
    headers = ["cluster", "representative", "cosine_to_centroid", "axis_rank", "n_members"]
    widths = {
        header: max(len(header), *(len(str(row[header])) for row in rows))
        for header in headers
    }
    lines = [
        " | ".join(header.ljust(widths[header]) for header in headers),
        " | ".join("-" * widths[header] for header in headers),
    ]
    for row in rows:
        lines.append(" | ".join(str(row[header]).ljust(widths[header]) for header in headers))
    return "\n".join(lines)


def main() -> None:
    assignments = load_assignments()
    layer_vectors = load_layer_vectors(assignments["role"].tolist())

    summary_rows: list[dict[str, object]] = []
    backup_sections: list[str] = []

    for cluster in CLUSTERS:
        cluster_df = assignments[assignments["cluster"] == cluster].copy()
        member_indices = cluster_df.index.to_list()
        similarities = cosine_to_centroid(layer_vectors[member_indices])
        cluster_df["cosine_to_centroid"] = similarities.tolist()
        cluster_df = cluster_df.sort_values(
            ["cosine_to_centroid", "axis_rank"],
            ascending=[False, True],
        )

        winner = cluster_df.iloc[0]
        summary_rows.append(
            {
                "cluster": cluster,
                "representative": winner["role"],
                "cosine_to_centroid": f"{winner['cosine_to_centroid']:.6f}",
                "axis_rank": int(winner["axis_rank"]),
                "n_members": len(cluster_df),
            }
        )

        backup_sections.append(f"{cluster} top 3:")
        for rank, (_, row) in enumerate(cluster_df.head(3).iterrows(), start=1):
            backup_sections.append(
                f"  {rank}. {row['role']} | cosine_to_centroid={row['cosine_to_centroid']:.6f} | "
                f"axis_rank={int(row['axis_rank'])}"
            )
        backup_sections.append("")

    report = "\n".join(
        [
            "Q2 centroid-nearest representatives",
            f"Layer: {LAYER}",
            f"Role tensor shape: ({EXPECTED_N_ROLES}, {EXPECTED_ROLE_SHAPE[0]}, {EXPECTED_ROLE_SHAPE[1]})",
            f"Layer slice shape: {tuple(layer_vectors.shape)}",
            "Axis rank source: visualizations/full_ranking.csv rank column",
            "",
            format_table(summary_rows),
            "",
            "Top 3 closest to centroid per cluster",
            "",
            "\n".join(backup_sections).rstrip(),
            "",
        ]
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report)
    print(report)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
