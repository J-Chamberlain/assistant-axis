#!/usr/bin/env python3
"""Create geometry diagnostics for the no-label elicitation validation run."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "research" / "outputs" / "no_label_elicitation_geometry_diagnostics"
VALIDATION_DIR = REPO_ROOT / "research" / "outputs" / "no_label_elicitation_validation"
PACKET_DIR = REPO_ROOT / "research" / "outputs" / "no_label_elicitation_prompt_packet_v1"
GEOMETRY_PATH = REPO_ROOT / "research" / "visualizations" / "geometry_viz_data.json"


FAMILY_LABELS = {
    "pc1_positive_answer_space_constraint": "PC1+",
    "pc1_negative_open_expression": "PC1-",
    "pc2_positive_situated_experience": "PC2+",
    "pc2_negative_integrated_abstraction": "PC2-",
    "pc3_positive_internal_drive_consequence_disregard": "PC3+",
    "pc3_negative_care_orientation": "PC3-",
}

FAMILY_COLORS = {
    "pc1_positive_answer_space_constraint": "#d62728",
    "pc1_negative_open_expression": "#1f77b4",
    "pc2_positive_situated_experience": "#ff7f0e",
    "pc2_negative_integrated_abstraction": "#17becf",
    "pc3_positive_internal_drive_consequence_disregard": "#9467bd",
    "pc3_negative_care_orientation": "#2ca02c",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_role_geometry() -> pd.DataFrame:
    data = json.loads(GEOMETRY_PATH.read_text())
    names = data["roles"]["names"]
    coords = np.asarray(data["roles"]["pca3d"], dtype=float)
    clusters = data["roles"].get("clusters", ["unknown"] * len(names))
    return pd.DataFrame(
        {
            "role": names,
            "pc1": coords[:, 0],
            "pc2": coords[:, 1],
            "pc3": coords[:, 2],
            "cluster": clusters,
        }
    )


def parse_bool(x: object) -> bool:
    return str(x).strip().lower() == "true"


def nearest_roles(point: np.ndarray, roles: pd.DataFrame, k: int = 5) -> list[dict[str, object]]:
    coords = roles[["pc1", "pc2", "pc3"]].to_numpy(dtype=float)
    distances = np.linalg.norm(coords - point.reshape(1, 3), axis=1)
    order = np.argsort(distances)[:k]
    out = []
    for idx in order:
        row = roles.iloc[int(idx)]
        out.append(
            {
                "role": row["role"],
                "cluster": row["cluster"],
                "distance_3d": float(distances[idx]),
                "pc1": float(row["pc1"]),
                "pc2": float(row["pc2"]),
                "pc3": float(row["pc3"]),
            }
        )
    return out


def nearest_roles_text(nearest: list[dict[str, object]]) -> str:
    return "; ".join(f"{r['role']} ({r['distance_3d']:.2f})" for r in nearest)


def df_to_markdown(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    """Render a small dataframe as a GitHub-style Markdown table without tabulate."""
    headers = list(df.columns)
    rows = []
    for _, row in df.iterrows():
        rendered = []
        for h in headers:
            value = row[h]
            if isinstance(value, float) and not math.isnan(value):
                rendered.append(format(value, floatfmt))
            else:
                rendered.append(str(value))
        rows.append(rendered)

    def clean(cell: str) -> str:
        return cell.replace("\n", " ").replace("|", "\\|")

    lines = [
        "| " + " | ".join(clean(h) for h in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(clean(cell) for cell in row) + " |")
    return "\n".join(lines)


def percentile(value: float, values: np.ndarray) -> float:
    return float((values <= value).mean() * 100.0)


def add_family_coordinates(families: pd.DataFrame, assistant: dict[str, float], roles: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in families.iterrows():
        pc1 = assistant["pc1"] + float(row["mean_delta_pc1"])
        pc2 = assistant["pc2"] + float(row["mean_delta_pc2"])
        pc3 = assistant["pc3"] + float(row["mean_delta_pc3"])
        point = np.array([pc1, pc2, pc3], dtype=float)
        nearest = nearest_roles(point, roles)
        out = row.to_dict()
        out.update(
            {
                "label": FAMILY_LABELS.get(row["family"], row["family"]),
                "mean_pc1": pc1,
                "mean_pc2": pc2,
                "mean_pc3": pc3,
                "distance_from_assistant_3d": float(
                    np.linalg.norm(
                        np.array(
                            [
                                float(row["mean_delta_pc1"]),
                                float(row["mean_delta_pc2"]),
                                float(row["mean_delta_pc3"]),
                            ]
                        )
                    )
                ),
                "nearest_5_roles": nearest_roles_text(nearest),
                "nearest_5_roles_json": json.dumps(nearest),
            }
        )
        rows.append(out)
    return pd.DataFrame(rows)


def add_prompt_context(prompts: pd.DataFrame, packet: pd.DataFrame, roles: pd.DataFrame) -> pd.DataFrame:
    merged = prompts.merge(
        packet[["prompt_id", "prompt_text", "family_reasoning"]],
        on="prompt_id",
        how="left",
    )
    nearest_texts = []
    nearest_jsons = []
    for _, row in merged.iterrows():
        point = np.array([row["mean_pc1"], row["mean_pc2"], row["mean_pc3"]], dtype=float)
        nearest = nearest_roles(point, roles)
        nearest_texts.append(nearest_roles_text(nearest))
        nearest_jsons.append(json.dumps(nearest))
    merged["nearest_5_roles"] = nearest_texts
    merged["nearest_5_roles_json"] = nearest_jsons
    return merged


def write_assistant_percentiles(assistant: dict[str, float], roles: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for axis in ["pc1", "pc2", "pc3"]:
        values = roles[axis].to_numpy(dtype=float)
        coord = assistant[axis]
        sorted_values = np.sort(values)
        rank_le = int((values <= coord).sum())
        rows.append(
            {
                "axis": axis.upper(),
                "assistant_coordinate": coord,
                "role_count": len(values),
                "rank_count_le_assistant": rank_le,
                "percentile_le_assistant": percentile(coord, values),
                "role_min": float(values.min()),
                "role_median": float(np.median(values)),
                "role_max": float(values.max()),
                "nearest_lower_role_pc": float(sorted_values[max(0, rank_le - 1)]),
                "nearest_upper_role_pc": float(sorted_values[min(len(sorted_values) - 1, rank_le)]),
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "assistant_centroid_role_percentile.csv", index=False)
    return df


def plot_overlay(
    roles: pd.DataFrame,
    family_coords: pd.DataFrame,
    prompt_coords: pd.DataFrame,
    assistant: dict[str, float],
    axes: tuple[str, str],
    output_base: str,
    png: bool = False,
) -> None:
    x, y = axes
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.scatter(roles[x], roles[y], s=22, color="#a8a8a8", alpha=0.32, linewidths=0, label="Qwen role centroids")
    for family, sub in prompt_coords.groupby("family"):
        ax.scatter(
            sub[f"mean_{x}"],
            sub[f"mean_{y}"],
            s=28,
            color=FAMILY_COLORS.get(family, "#333333"),
            alpha=0.25,
            linewidths=0,
        )
    ax.scatter(
        [assistant[x]],
        [assistant[y]],
        marker="*",
        s=280,
        color="#111111",
        edgecolor="white",
        linewidth=1.0,
        label="Assistant centroid",
        zorder=6,
    )
    for _, row in family_coords.iterrows():
        family = row["family"]
        fx = row[f"mean_{x}"]
        fy = row[f"mean_{y}"]
        ax.annotate(
            "",
            xy=(fx, fy),
            xytext=(assistant[x], assistant[y]),
            arrowprops=dict(arrowstyle="->", color=FAMILY_COLORS.get(family, "#333333"), alpha=0.75, lw=1.6),
            zorder=4,
        )
        ax.scatter(
            [fx],
            [fy],
            s=150,
            color=FAMILY_COLORS.get(family, "#333333"),
            edgecolor="white",
            linewidth=0.9,
            zorder=7,
            label=row["label"],
        )
        ax.text(
            fx,
            fy,
            f" {row['label']}",
            fontsize=11,
            weight="bold",
            color=FAMILY_COLORS.get(family, "#333333"),
            zorder=8,
        )
    ax.axhline(0, color="#dddddd", lw=0.8, zorder=0)
    ax.axvline(0, color="#dddddd", lw=0.8, zorder=0)
    ax.set_xlabel(x.upper())
    ax.set_ylabel(y.upper())
    ax.set_title(f"No-label family means vs Qwen role centroids ({x.upper()} x {y.upper()})")
    handles, labels = ax.get_legend_handles_labels()
    seen = set()
    unique = []
    for h, l in zip(handles, labels):
        if l not in seen:
            seen.add(l)
            unique.append((h, l))
    ax.legend([h for h, _ in unique], [l for _, l in unique], loc="best", frameon=True, fontsize=9)
    ax.grid(alpha=0.14)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{output_base}.svg")
    if png:
        fig.savefig(OUT_DIR / f"{output_base}.png", dpi=180)
    plt.close(fig)


def plot_pc1_percentile(
    roles: pd.DataFrame,
    family_coords: pd.DataFrame,
    assistant: dict[str, float],
    assistant_percentiles: pd.DataFrame,
) -> None:
    pc1_pct = assistant_percentiles.loc[assistant_percentiles["axis"] == "PC1", "percentile_le_assistant"].iloc[0]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    values = roles["pc1"].to_numpy(dtype=float)
    ax.hist(values, bins=32, color="#c8c8c8", edgecolor="#ffffff", alpha=0.9)
    ax.plot(values, np.zeros_like(values), "|", color="#777777", markersize=12, alpha=0.55)
    ax.axvline(
        assistant["pc1"],
        color="#111111",
        lw=2.7,
        label=f"Assistant centroid PC1={assistant['pc1']:.2f} ({pc1_pct:.1f} percentile)",
    )
    for _, row in family_coords.sort_values("mean_pc1").iterrows():
        family = row["family"]
        ax.axvline(
            row["mean_pc1"],
            color=FAMILY_COLORS.get(family, "#333333"),
            lw=1.8,
            alpha=0.9,
            label=f"{row['label']} mean PC1={row['mean_pc1']:.1f}",
        )
    ax.set_xlabel("PC1 coordinate")
    ax.set_ylabel("Role centroid count")
    ax.set_title("Assistant centroid PC1 position relative to Qwen role distribution")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0, fontsize=9)
    ax.grid(axis="y", alpha=0.15)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "assistant_centroid_pc1_position_diagnostic.svg")
    fig.savefig(OUT_DIR / "assistant_centroid_pc1_position_diagnostic.png", dpi=180)
    plt.close(fig)


def build_report(
    assistant: dict[str, float],
    assistant_pcts: pd.DataFrame,
    family_coords: pd.DataFrame,
    prompt_context: pd.DataFrame,
    success: pd.DataFrame,
    artifact_hashes: dict[str, str],
) -> None:
    pc1_pct = assistant_pcts.loc[assistant_pcts["axis"] == "PC1", "percentile_le_assistant"].iloc[0]
    pc2_pct = assistant_pcts.loc[assistant_pcts["axis"] == "PC2", "percentile_le_assistant"].iloc[0]
    pc3_pct = assistant_pcts.loc[assistant_pcts["axis"] == "PC3", "percentile_le_assistant"].iloc[0]
    pc1_pos = family_coords[family_coords["family"] == "pc1_positive_answer_space_constraint"].iloc[0]
    pc3_neg = family_coords[family_coords["family"] == "pc3_negative_care_orientation"].iloc[0]
    pc3_pos_05 = prompt_context[prompt_context["prompt_id"] == "pc3_pos_05"].iloc[0]

    family_table = family_coords[
        [
            "label",
            "family",
            "mean_pc1",
            "mean_pc2",
            "mean_pc3",
            "mean_delta_pc1",
            "mean_delta_pc2",
            "mean_delta_pc3",
            "prompt_success_rate",
            "family_pass_70pct_threshold",
            "nearest_5_roles",
        ]
    ].copy()

    success_table = success[["family", "pc", "polarity", "observed_success_rate", "prompt_success_count", "n_prompts", "pass"]]

    lines = [
        "# No-label elicitation geometry diagnostics",
        "",
        "## Purpose",
        "",
        "This diagnostic places the no-label elicitation family means, prompt means, the published assistant baseline, and Qwen role/persona centroids in the same PCA coordinate space. It uses existing validation outputs only; no prompts, generations, activations, or projections were rerun.",
        "",
        "## Sources",
        "",
        f"- Geometry source: `research/visualizations/geometry_viz_data.json` (`{artifact_hashes['geometry']}`)",
        "- Validation source: `research/outputs/no_label_elicitation_validation/`",
        "- Frozen prompt packet: `research/outputs/no_label_elicitation_prompt_packet_v1/no_label_elicitation_prompts_v1.csv`",
        "- Assistant baseline: `research/outputs/no_label_elicitation_validation/projection_basis_debug.json`",
        "",
        "## Observed",
        "",
        f"- Assistant centroid: PC1={assistant['pc1']:.3f}, PC2={assistant['pc2']:.3f}, PC3={assistant['pc3']:.3f}.",
        f"- Assistant percentile among Qwen role centroids: PC1={pc1_pct:.1f}, PC2={pc2_pct:.1f}, PC3={pc3_pct:.1f}.",
        f"- The PC1-positive family did not remain at the assistant centroid; it moved negative on PC1 by {float(pc1_pos['mean_delta_pc1']):.3f}, to mean PC1={float(pc1_pos['mean_pc1']):.3f}.",
        f"- The PC3-negative family moved negative on PC1 by {float(pc3_neg['mean_delta_pc1']):.3f} while also moving negative on PC3 by {float(pc3_neg['mean_delta_pc3']):.3f}.",
        f"- `pc3_pos_05` mean displacement was PC1={float(pc3_pos_05['mean_delta_pc1']):.3f}, PC2={float(pc3_pos_05['mean_delta_pc2']):.3f}, PC3={float(pc3_pos_05['mean_delta_pc3']):.3f}. Its largest movement was strongly negative PC1 with high positive PC2, not positive PC3.",
        "",
        "### Family success summary",
        "",
        df_to_markdown(success_table),
        "",
        "### Family mean coordinates and nearest-role context",
        "",
        df_to_markdown(family_table),
        "",
        "### `pc3_pos_05` nearest-role context",
        "",
        f"- Prompt text: {pc3_pos_05.get('prompt_text', '')}",
        f"- Mean coordinates: PC1={float(pc3_pos_05['mean_pc1']):.3f}, PC2={float(pc3_pos_05['mean_pc2']):.3f}, PC3={float(pc3_pos_05['mean_pc3']):.3f}.",
        f"- Nearest roles: {pc3_pos_05['nearest_5_roles']}.",
        "",
        "## Inferred",
        "",
        f"- The PC1-positive failure is consistent with a saturation/baseline problem because the assistant centroid is already at the {pc1_pct:.1f} percentile on PC1 relative to role centroids. However, saturation is not the whole story: the family moved decisively negative on PC1, suggesting that the prompts elicited ordinary explanatory/helpful response modes rather than further positive-PC1 convergence pressure.",
        "- PC3-negative prompts appear to couple care/repair with lower PC1, so their successful PC3 movement should not be interpreted as axis-isolated.",
        "- `pc3_pos_05` appears mis-specified for the intended PC3-positive pole: the wording foregrounds personal cost and perseverance, which plausibly evokes self-sacrifice/commitment rather than disregard of consequences to others.",
        "- Several successful families move toward recognizable role regions, but nearest-role context should be used descriptively rather than as a new classifier.",
        "",
        "## Speculative",
        "",
        "- A revised PC1-positive no-label packet may need prompts that place the assistant farther from generic helpful explanation and closer to external checking, scoring, or rule-bound finality while still avoiding explicit labels.",
        "- Future prompt design should separate self-cost, other-cost, care, and rule-bound constraint more explicitly, because these may combine PC1 and PC3 pressures in non-obvious ways.",
        "- These diagnostics are better treated as Paper 2 or appendix evidence unless connected to a preregistered follow-up packet.",
        "",
        "## Output files",
        "",
        "- `family_role_centroid_overlay_pc1_pc2.svg` and `.png`",
        "- `family_role_centroid_overlay_pc1_pc3.svg`",
        "- `family_role_centroid_overlay_pc2_pc3.svg`",
        "- `assistant_centroid_pc1_position_diagnostic.svg` and `.png`",
        "- `family_mean_coordinates.csv`",
        "- `prompt_mean_coordinates_with_roles_context.csv`",
        "- `assistant_centroid_role_percentile.csv`",
        "- `artifact_inventory.csv`",
    ]
    (OUT_DIR / "no_label_elicitation_geometry_diagnostics_report.md").write_text("\n".join(lines) + "\n")


def write_artifact_inventory(inputs: list[Path], outputs: list[Path]) -> None:
    rows = []
    for kind, paths in [("input", inputs), ("output", outputs)]:
        for path in paths:
            rows.append(
                {
                    "artifact_role": kind,
                    "path": str(path.relative_to(REPO_ROOT)),
                    "exists": path.exists(),
                    "size_bytes": path.stat().st_size if path.exists() else "",
                    "sha256": sha256(path) if path.exists() and path.is_file() else "",
                    "notes": "",
                }
            )
    with (OUT_DIR / "artifact_inventory.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    roles = load_role_geometry()
    families = pd.read_csv(VALIDATION_DIR / "family_mean_results.csv")
    prompts = pd.read_csv(VALIDATION_DIR / "prompt_mean_results.csv")
    success = pd.read_csv(VALIDATION_DIR / "geometric_success_summary.csv")
    packet = pd.read_csv(PACKET_DIR / "no_label_elicitation_prompts_v1.csv")
    debug = json.loads((VALIDATION_DIR / "projection_basis_debug.json").read_text())
    assistant = {
        "pc1": float(debug["assistant_baseline_pc1"]),
        "pc2": float(debug["assistant_baseline_pc2"]),
        "pc3": float(debug["assistant_baseline_pc3"]),
    }

    assistant_pcts = write_assistant_percentiles(assistant, roles)
    family_coords = add_family_coordinates(families, assistant, roles)
    prompt_context = add_prompt_context(prompts, packet, roles)

    family_coords.to_csv(OUT_DIR / "family_mean_coordinates.csv", index=False)
    prompt_context.to_csv(OUT_DIR / "prompt_mean_coordinates_with_roles_context.csv", index=False)

    plot_overlay(roles, family_coords, prompt_context, assistant, ("pc1", "pc2"), "family_role_centroid_overlay_pc1_pc2", png=True)
    plot_overlay(roles, family_coords, prompt_context, assistant, ("pc1", "pc3"), "family_role_centroid_overlay_pc1_pc3")
    plot_overlay(roles, family_coords, prompt_context, assistant, ("pc2", "pc3"), "family_role_centroid_overlay_pc2_pc3")
    plot_pc1_percentile(roles, family_coords, assistant, assistant_pcts)

    artifact_hashes = {"geometry": sha256(GEOMETRY_PATH)}
    build_report(assistant, assistant_pcts, family_coords, prompt_context, success, artifact_hashes)

    output_paths = [
        OUT_DIR / "no_label_elicitation_geometry_diagnostics_report.md",
        OUT_DIR / "family_role_centroid_overlay_pc1_pc2.svg",
        OUT_DIR / "family_role_centroid_overlay_pc1_pc2.png",
        OUT_DIR / "family_role_centroid_overlay_pc1_pc3.svg",
        OUT_DIR / "family_role_centroid_overlay_pc2_pc3.svg",
        OUT_DIR / "assistant_centroid_pc1_position_diagnostic.svg",
        OUT_DIR / "assistant_centroid_pc1_position_diagnostic.png",
        OUT_DIR / "family_mean_coordinates.csv",
        OUT_DIR / "prompt_mean_coordinates_with_roles_context.csv",
        OUT_DIR / "assistant_centroid_role_percentile.csv",
    ]
    input_paths = [
        GEOMETRY_PATH,
        VALIDATION_DIR / "family_mean_results.csv",
        VALIDATION_DIR / "prompt_mean_results.csv",
        VALIDATION_DIR / "geometric_success_summary.csv",
        VALIDATION_DIR / "projection_basis_debug.json",
        PACKET_DIR / "no_label_elicitation_prompts_v1.csv",
    ]
    write_artifact_inventory(input_paths, output_paths + [OUT_DIR / "run_no_label_elicitation_geometry_diagnostics.py"])
    print(f"Wrote diagnostics to {OUT_DIR.relative_to(REPO_ROOT)}")
    print(assistant_pcts.to_string(index=False))


if __name__ == "__main__":
    main()
