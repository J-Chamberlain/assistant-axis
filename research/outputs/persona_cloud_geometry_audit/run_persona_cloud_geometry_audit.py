#!/usr/bin/env python3
"""Audit local persona activation-cloud geometry.

Inputs are existing projected PC coordinates. This script does not perform
model inference, activation extraction, API calls, or judging.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "outputs" / "persona_cloud_geometry_audit"
LAYERED_JSON = (
    ROOT
    / "research"
    / "outputs"
    / "activation_cloud_layered_viewer"
    / "activation_cloud_layered_viewer_data.json"
)

SOURCE_FILES = [
    ROOT / "research" / "outputs" / "activation_cloud_layered_viewer" / "activation_cloud_layered_viewer_data.json",
    ROOT / "research" / "outputs" / "activation_cloud_layered_viewer" / "activation_cloud_layered_centroids.csv",
    ROOT / "research" / "outputs" / "activation_cloud_layered_viewer" / "activation_cloud_layered_membership_counts.csv",
    ROOT / "research" / "outputs" / "a100_two_role_activation_cloud_pilot" / "activation_cloud_per_response.csv",
    ROOT / "research" / "outputs" / "a100_activation_cloud_posthoc_analysis" / "gpt41_judge_scores.csv",
    ROOT / "research" / "outputs" / "gpt55_judge_and_outlier_followup" / "gpt55_judge_scores.csv",
    ROOT / "research" / "outputs" / "prior_adaptive_recovery_audit" / "prior_adaptive_corrected_coordinates.csv",
    ROOT / "research" / "outputs" / "recovered_role_cloud_analysis" / "recovered_gpt41_scores.csv",
    ROOT / "research" / "outputs" / "cloud_eigenvector_angle_analysis" / "cloud_orientation_metrics.csv",
]

BOOTSTRAPS = 500
RNG = np.random.default_rng(20260604)
PC_COLS = ["pc1", "pc2", "pc3"]
CHI2_95_2D = 5.991464547107979
CHI2_95_3D = 7.814727903251179


def load_points() -> pd.DataFrame:
    data = json.loads(LAYERED_JSON.read_text())
    points = pd.DataFrame(data["points"])
    for col in PC_COLS:
        points[col] = pd.to_numeric(points[col], errors="coerce")
    return points.dropna(subset=PC_COLS).copy()


def condition_mask(points: pd.DataFrame, role_or_run: str, layer_key: str) -> pd.Series:
    base = points["role_or_run"].eq(role_or_run)
    if layer_key == "all":
        return base
    score_col = "gpt41_score" if layer_key.startswith("gpt41") else "gpt55_score"
    score = pd.to_numeric(points[score_col], errors="coerce")
    if layer_key.endswith("ge2"):
        return base & score.ge(2)
    if layer_key.endswith("eq3"):
        return base & score.eq(3)
    raise ValueError(layer_key)


def angle_from_vector(v: np.ndarray) -> float:
    angle = math.degrees(math.atan2(v[1], v[0]))
    return angle % 180.0


def axial_diff_deg(a: np.ndarray | float, b: float) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    return np.abs(((a - b + 90.0) % 180.0) - 90.0)


def covariance_metrics(coords: np.ndarray) -> dict:
    n = len(coords)
    centroid = coords.mean(axis=0)
    centered = coords - centroid
    distances = np.linalg.norm(centered, axis=1)
    out = {
        "n": int(n),
        "centroid_pc1": float(centroid[0]),
        "centroid_pc2": float(centroid[1]),
        "centroid_pc3": float(centroid[2]),
        "mean_distance_to_centroid": float(distances.mean()) if n else np.nan,
        "median_distance_to_centroid": float(np.median(distances)) if n else np.nan,
        "rms_radius": float(np.sqrt((distances**2).mean())) if n else np.nan,
    }
    if n < 2:
        return out
    cov2 = np.cov(centered[:, :2], rowvar=False)
    eig2, vec2 = np.linalg.eigh(cov2)
    order2 = np.argsort(eig2)[::-1]
    eig2 = eig2[order2]
    vec2 = vec2[:, order2]
    cov3 = np.cov(centered[:, :3], rowvar=False)
    eig3, vec3 = np.linalg.eigh(cov3)
    order3 = np.argsort(eig3)[::-1]
    eig3 = eig3[order3]
    vec3 = vec3[:, order3]
    out.update(
        {
            "cov2_lambda1": float(eig2[0]),
            "cov2_lambda2": float(eig2[1]) if len(eig2) > 1 else np.nan,
            "anisotropy_ratio_2d_l1_l2": float(eig2[0] / eig2[1]) if len(eig2) > 1 and eig2[1] > 0 else np.inf,
            "first_pc_explained_variance_2d": float(eig2[0] / eig2.sum()) if eig2.sum() > 0 else np.nan,
            "dominant_orientation_angle_pc1_pc2": float(angle_from_vector(vec2[:, 0])),
            "ellipse_area_95_pc1_pc2": float(math.pi * CHI2_95_2D * math.sqrt(max(eig2[0], 0) * max(eig2[1], 0))),
            "convex_hull_area_pc1_pc2": float(convex_hull_area(coords[:, :2])) if n >= 3 else np.nan,
            "cov3_lambda1": float(eig3[0]),
            "cov3_lambda2": float(eig3[1]) if len(eig3) > 1 else np.nan,
            "cov3_lambda3": float(eig3[2]) if len(eig3) > 2 else np.nan,
            "anisotropy_ratio_3d_l1_mean_rest": float(eig3[0] / np.mean(eig3[1:])) if len(eig3) > 2 and np.mean(eig3[1:]) > 0 else np.inf,
            "first_pc_explained_variance_3d": float(eig3[0] / eig3.sum()) if eig3.sum() > 0 else np.nan,
            "ellipsoid_volume_95_pc123": float((4.0 / 3.0) * math.pi * (CHI2_95_3D ** 1.5) * math.sqrt(max(np.prod(eig3), 0))),
        }
    )
    return out


def convex_hull_area(points: np.ndarray) -> float:
    pts = sorted(set(map(tuple, points)))
    if len(pts) < 3:
        return 0.0

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    area = 0.0
    for i, p in enumerate(hull):
        q = hull[(i + 1) % len(hull)]
        area += p[0] * q[1] - q[0] * p[1]
    return abs(area) / 2.0


def bootstrap_metrics(coords: np.ndarray, sample_n: int, b: int = BOOTSTRAPS) -> pd.DataFrame:
    if len(coords) < 3 or sample_n < 3:
        return pd.DataFrame()
    rows = []
    for i in range(b):
        sample = coords[RNG.choice(len(coords), size=sample_n, replace=True)]
        m = covariance_metrics(sample)
        m["bootstrap_i"] = i
        rows.append(m)
    return pd.DataFrame(rows)


def summarize_bootstrap(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    keys = [
        "mean_distance_to_centroid",
        "median_distance_to_centroid",
        "rms_radius",
        "anisotropy_ratio_2d_l1_l2",
        "anisotropy_ratio_3d_l1_mean_rest",
        "first_pc_explained_variance_2d",
        "first_pc_explained_variance_3d",
        "dominant_orientation_angle_pc1_pc2",
        "ellipse_area_95_pc1_pc2",
        "convex_hull_area_pc1_pc2",
        "ellipsoid_volume_95_pc123",
    ]
    out = {}
    for k in keys:
        if k not in df:
            continue
        vals = df[k].replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
        if len(vals) == 0:
            continue
        if k == "dominant_orientation_angle_pc1_pc2":
            med = axial_median(vals)
            diffs = axial_diff_deg(vals, med)
            out["orientation_angle_median"] = float(med)
            out["orientation_abs_deviation_median"] = float(np.median(diffs))
            out["orientation_abs_deviation_p95"] = float(np.percentile(diffs, 95))
            out["orientation_stability_width_p90"] = float(np.percentile(diffs, 95) * 2)
        else:
            out[f"{k}_median"] = float(np.median(vals))
            out[f"{k}_ci_low"] = float(np.percentile(vals, 2.5))
            out[f"{k}_ci_high"] = float(np.percentile(vals, 97.5))
    return out


def axial_median(vals: np.ndarray) -> float:
    grid = np.linspace(0, 180, 720, endpoint=False)
    losses = [np.median(axial_diff_deg(vals, g)) for g in grid]
    return float(grid[int(np.argmin(losses))])


def orientation_label(row: pd.Series) -> tuple[str, str]:
    n = int(row["n"])
    if n < 10:
        return "Unknown", "n<10; covariance/orientation too small"
    if row.get("anisotropy_ratio_2d_l1_l2", np.nan) < 1.5:
        return "Observed-no-preferred-direction", "near-isotropic 2D covariance"
    if row.get("first_pc_explained_variance_2d", np.nan) < 0.60:
        return "Observed-weak-orientation", "first PC explains <60% of 2D variance"
    if row.get("orientation_abs_deviation_p95", np.inf) > 35:
        return "Inferred-unstable-orientation", "bootstrap orientation spread is wide"
    return "Observed-meaningful-orientation", "anisotropy and bootstrap stability support a preferred direction"


def artifact_inventory(points: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for p in SOURCE_FILES:
        rows.append(
            {
                "source_path": str(p.relative_to(ROOT)),
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
                "role": "primary point source" if p == LAYERED_JSON else "supporting source",
                "notes": "",
            }
        )
    for role_run, g in points.groupby("role_or_run"):
        rows.append(
            {
                "source_path": str(LAYERED_JSON.relative_to(ROOT)),
                "exists": True,
                "size_bytes": LAYERED_JSON.stat().st_size,
                "role": f"point rows for {role_run}",
                "notes": f"{len(g)} all-response points; filters from gpt41_score/gpt55_score columns",
            }
        )
    return pd.DataFrame(rows)


def build_conditions(points: pd.DataFrame) -> dict[tuple[str, str], pd.DataFrame]:
    conditions = {}
    role_runs = sorted(points["role_or_run"].unique())
    layer_keys = ["all", "gpt41_ge2", "gpt41_eq3", "gpt55_ge2", "gpt55_eq3"]
    for role_run in role_runs:
        for layer in layer_keys:
            sub = points[condition_mask(points, role_run, layer)].copy()
            if len(sub):
                conditions[(role_run, layer)] = sub
    return conditions


def comparison_plan(metrics: pd.DataFrame) -> list[dict]:
    rows = []
    def add_set(name, predicate, min_allowed=10):
        sub = metrics[predicate(metrics)].copy()
        if sub.empty:
            return
        min_n = int(sub["n"].min())
        rows.append({"comparison_set": name, "keys": list(zip(sub["role_or_run"], sub["filter_condition"])), "matched_n": min_n, "usable": min_n >= min_allowed})

    add_set("all_response_clouds_only", lambda m: m["filter_condition"].eq("all"))
    add_set("gpt41_score_ge2_filtered_clouds", lambda m: m["filter_condition"].eq("gpt41_ge2"))
    add_set("gpt41_score_eq3_filtered_clouds", lambda m: m["filter_condition"].eq("gpt41_eq3"))
    add_set("gpt55_score_ge2_filtered_clouds_available", lambda m: m["filter_condition"].eq("gpt55_ge2"))
    add_set("gpt55_score_eq3_filtered_clouds_available", lambda m: m["filter_condition"].eq("gpt55_eq3"))
    for role_run in sorted(metrics["role_or_run"].unique()):
        add_set(f"{role_run}_all_vs_gpt41_ge2", lambda m, rr=role_run: m["role_or_run"].eq(rr) & m["filter_condition"].isin(["all", "gpt41_ge2"]))
        add_set(f"{role_run}_all_vs_gpt41_eq3", lambda m, rr=role_run: m["role_or_run"].eq(rr) & m["filter_condition"].isin(["all", "gpt41_eq3"]))
        add_set(f"{role_run}_all_vs_gpt55_ge2", lambda m, rr=role_run: m["role_or_run"].eq(rr) & m["filter_condition"].isin(["all", "gpt55_ge2"]))
        add_set(f"{role_run}_all_vs_gpt55_eq3", lambda m, rr=role_run: m["role_or_run"].eq(rr) & m["filter_condition"].isin(["all", "gpt55_eq3"]))
    add_set("editor_runs_all_response", lambda m: m["role_or_run"].isin(["editor_phase1_128", "editor_matched64_1024"]) & m["filter_condition"].eq("all"))
    add_set("editor_runs_gpt41_ge2", lambda m: m["role_or_run"].isin(["editor_phase1_128", "editor_matched64_1024"]) & m["filter_condition"].eq("gpt41_ge2"))
    return rows


def run_matched_bootstraps(conditions: dict, metrics: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    comp_rows = []
    raw_distributions = {}
    for plan in comparison_plan(metrics):
        keys = plan["keys"]
        matched_n = plan["matched_n"]
        if matched_n < 3:
            continue
        for role_run, layer in keys:
            coords = conditions[(role_run, layer)][PC_COLS].to_numpy(float)
            boot = bootstrap_metrics(coords, matched_n)
            if boot.empty:
                continue
            summary = summarize_bootstrap(boot)
            base = {
                "comparison_set": plan["comparison_set"],
                "role_or_run": role_run,
                "filter_condition": layer,
                "matched_n": matched_n,
                "usable_matched_n": bool(plan["usable"]),
                "original_n": int(len(coords)),
            }
            base.update(summary)
            comp_rows.append(base)
            raw_distributions[(plan["comparison_set"], role_run, layer)] = boot
    return pd.DataFrame(comp_rows), raw_distributions


def draw_cov_ellipse(ax, coords: np.ndarray, color: str, label: str) -> None:
    if len(coords) < 3:
        return
    centroid = coords[:, :2].mean(axis=0)
    cov = np.cov(coords[:, :2] - centroid, rowvar=False)
    eig, vec = np.linalg.eigh(cov)
    order = np.argsort(eig)[::-1]
    eig = eig[order]
    vec = vec[:, order]
    angle = math.degrees(math.atan2(vec[1, 0], vec[0, 0]))
    width = 2 * math.sqrt(CHI2_95_2D * max(eig[0], 0))
    height = 2 * math.sqrt(CHI2_95_2D * max(eig[1], 0))
    ell = Ellipse(centroid, width, height, angle=angle, fill=False, lw=2, color=color, alpha=0.9, label=label)
    ax.add_patch(ell)


def make_static_plot(points: pd.DataFrame, metrics: pd.DataFrame) -> None:
    colors = {
        "amateur": "#2563eb",
        "playwright": "#16a34a",
        "trickster_phase1_1200": "#dc2626",
        "editor_phase1_128": "#9333ea",
        "editor_matched64_1024": "#f97316",
    }
    fig, ax = plt.subplots(figsize=(12, 9))
    for role_run, g in points.groupby("role_or_run"):
        c = colors.get(role_run, "#6b7280")
        ax.scatter(g["pc1"], g["pc2"], s=14, alpha=0.18, color=c, label=f"{role_run} points")
        draw_cov_ellipse(ax, g[PC_COLS].to_numpy(float), c, f"{role_run} 95% ellipse")
        cent = g[["pc1", "pc2"]].mean()
        ax.scatter([cent["pc1"]], [cent["pc2"]], s=90, color=c, edgecolor="black", zorder=5)
        ax.text(cent["pc1"], cent["pc2"], role_run, fontsize=9, weight="bold")
    ax.axhline(0, color="black", lw=0.7, alpha=0.4)
    ax.axvline(0, color="black", lw=0.7, alpha=0.4)
    ax.set_xlabel("Qwen persona PC1")
    ax.set_ylabel("Qwen persona PC2")
    ax.set_title("Persona activation clouds: all-response PC1/PC2 with 95% covariance ellipses")
    ax.legend(loc="best", fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "cloud_geometry_pc12_static.png", dpi=180)
    plt.close(fig)


def make_bootstrap_plot(boot: pd.DataFrame) -> None:
    focus = boot[boot["comparison_set"].eq("all_response_clouds_only")].copy()
    if focus.empty:
        return
    metrics = [
        ("rms_radius_median", "Matched-n RMS radius"),
        ("anisotropy_ratio_2d_l1_l2_median", "Matched-n 2D anisotropy"),
        ("orientation_abs_deviation_p95", "Orientation p95 abs deviation"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (col, title) in zip(axes, metrics):
        sub = focus.sort_values("role_or_run")
        ax.bar(sub["role_or_run"], sub[col], color="#64748b")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=70)
    fig.tight_layout()
    fig.savefig(OUT / "cloud_geometry_bootstrap_diagnostics.png", dpi=180)
    plt.close(fig)


def make_distribution_plots(raw_distributions: dict, metrics: pd.DataFrame) -> None:
    all_items = [
        (key, df)
        for key, df in raw_distributions.items()
        if key[0] == "all_response_clouds_only" and not df.empty
    ]
    if all_items:
        labels = [key[1] for key, _ in all_items]
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        axes[0].boxplot([df["rms_radius"].dropna() for _, df in all_items], tick_labels=labels, showfliers=False)
        axes[0].set_title("All-response matched-n RMS radius bootstrap")
        axes[0].tick_params(axis="x", rotation=70)
        axes[0].set_ylabel("RMS radius")
        axes[1].boxplot([df["anisotropy_ratio_2d_l1_l2"].replace([np.inf, -np.inf], np.nan).dropna() for _, df in all_items], tick_labels=labels, showfliers=False)
        axes[1].set_title("All-response matched-n 2D anisotropy bootstrap")
        axes[1].tick_params(axis="x", rotation=70)
        axes[1].set_ylabel("lambda1 / lambda2")
        fig.tight_layout()
        fig.savefig(OUT / "cloud_geometry_matched_bootstrap_boxplots.png", dpi=180)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(11, 6))
        positions = []
        angle_data = []
        angle_labels = []
        metric_lookup = metrics.set_index(["role_or_run", "filter_condition"])
        for key, df in all_items:
            _, role_run, layer = key
            row = metric_lookup.loc[(role_run, layer)]
            if "meaningful" not in row["orientation_interpretation"]:
                continue
            med = axial_median(df["dominant_orientation_angle_pc1_pc2"].dropna().to_numpy(float))
            deviations = axial_diff_deg(df["dominant_orientation_angle_pc1_pc2"].dropna().to_numpy(float), med)
            angle_data.append(deviations)
            angle_labels.append(role_run)
            positions.append(len(positions) + 1)
        if angle_data:
            ax.boxplot(angle_data, tick_labels=angle_labels, showfliers=False)
            ax.set_title("Orientation stability for clouds with meaningful all-response orientation")
            ax.set_ylabel("Absolute axial angle deviation from bootstrap median (degrees)")
            ax.tick_params(axis="x", rotation=70)
            fig.tight_layout()
            fig.savefig(OUT / "cloud_geometry_orientation_stability.png", dpi=180)
        plt.close(fig)


def make_interactive(points: pd.DataFrame, metrics: pd.DataFrame) -> None:
    try:
        import plotly.graph_objects as go
    except Exception:
        return
    fig = go.Figure()
    for role_run, g in points.groupby("role_or_run"):
        hover = [
            f"role/run={r.role_or_run}<br>response={r.response_id}<br>PC1={r.pc1:.2f}<br>PC2={r.pc2:.2f}<br>PC3={r.pc3:.2f}<br>gpt41={r.gpt41_score}<br>gpt55={r.gpt55_score}"
            for r in g.itertuples()
        ]
        fig.add_trace(go.Scattergl(x=g["pc1"], y=g["pc2"], mode="markers", name=role_run, marker=dict(size=5, opacity=0.45), text=hover, hoverinfo="text"))
    fig.update_layout(title="Persona activation clouds in Qwen PC1/PC2", xaxis_title="PC1", yaxis_title="PC2", width=1100, height=800)
    fig.write_html(OUT / "cloud_geometry_pc12_interactive.html", include_plotlyjs="cdn")


def write_report(metrics: pd.DataFrame, boot: pd.DataFrame, inventory: pd.DataFrame) -> None:
    all_rows = metrics[metrics["filter_condition"].eq("all")].copy().sort_values("role_or_run")
    meaningful = metrics[["role_or_run", "filter_condition", "n", "orientation_interpretation", "orientation_reason", "rms_radius", "anisotropy_ratio_2d_l1_l2", "first_pc_explained_variance_2d", "dominant_orientation_angle_pc1_pc2"]].copy()
    all_boot = boot[boot["comparison_set"].eq("all_response_clouds_only")].copy()
    gpt41_boot = boot[boot["comparison_set"].eq("gpt41_score_ge2_filtered_clouds")].copy()
    editor_boot = boot[boot["comparison_set"].eq("editor_runs_all_response")].copy()

    def table(df, cols=None, n=None):
        d = df.copy()
        if cols:
            d = d[cols]
        if n:
            d = d.head(n)
        return df_to_md(d)

    trick = all_boot[all_boot["role_or_run"].eq("trickster_phase1_1200")]
    other = all_boot[~all_boot["role_or_run"].eq("trickster_phase1_1200")]
    if not trick.empty and not other.empty:
        trick_radius = float(trick["rms_radius_median"].iloc[0])
        median_other_radius = float(other["rms_radius_median"].median())
        trick_aniso = float(trick["anisotropy_ratio_2d_l1_l2_median"].iloc[0])
        median_other_aniso = float(other["anisotropy_ratio_2d_l1_l2_median"].median())
    else:
        trick_radius = median_other_radius = trick_aniso = median_other_aniso = np.nan

    report = f"""# Persona Cloud Geometry Audit

## Startup And Scope

Startup was verified against `research/STARTUP_MANIFEST.md` by direct raw GitHub fetch before analysis. This audit uses existing Qwen PC-space response-cloud coordinates only; no GPU work, activation extraction, response generation, API calls, or judging were run.

Primary point source: `{LAYERED_JSON.relative_to(ROOT)}`.

## Concise Findings

- **Observed:** The five all-response clouds have different local geometry after matched-n control (`n=60`): trickster is not the largest-radius cloud, but it is the least anisotropic and least orientation-stable in PC1/PC2.
- **Observed:** Orientation angles are only interpretable when anisotropy and bootstrap stability support them. Amateur, playwright, and editor all-response clouds pass this threshold; trickster does not, despite its large sample size.
- **Inferred:** Trickster is less directionally constrained in the specific sense of weak PC1/PC2 anisotropy and unstable matched-n orientation. Its visual prominence is partly sample-size-driven (`n=1200`), not evidence of larger matched-n volume.
- **Observed:** GPT-4.1 filtering tightens editor clouds substantially, especially `editor_matched64_1024`, while trickster is unchanged because GPT-4.1 retained all or nearly all responses.
- **Unknown:** GPT-5.5 filtered comparisons exist only for amateur/playwright, so they cannot support cross-role conclusions.

## Artifact Inventory

{table(inventory, ['source_path','exists','size_bytes','role','notes'])}

## All-Response Cloud Metrics

{table(all_rows, ['role_or_run','role','n','centroid_pc1','centroid_pc2','centroid_pc3','mean_distance_to_centroid','rms_radius','anisotropy_ratio_2d_l1_l2','anisotropy_ratio_3d_l1_mean_rest','first_pc_explained_variance_2d','dominant_orientation_angle_pc1_pc2','orientation_interpretation'])}

## Matched-n All-Response Bootstrap

Matched-n all-response comparison uses `n=60`, the minimum all-response cloud size.

{table(all_boot, ['role_or_run','filter_condition','matched_n','rms_radius_median','rms_radius_ci_low','rms_radius_ci_high','anisotropy_ratio_2d_l1_l2_median','anisotropy_ratio_2d_l1_l2_ci_low','anisotropy_ratio_2d_l1_l2_ci_high','orientation_angle_median','orientation_abs_deviation_p95'])}

Trickster matched-n RMS radius is {trick_radius:.3f}, compared with median non-trickster matched-n RMS radius {median_other_radius:.3f}. Trickster matched-n 2D anisotropy is {trick_aniso:.3f}, compared with median non-trickster anisotropy {median_other_aniso:.3f}. This means trickster is less directionally constrained by anisotropy/orientation criteria, not larger by matched-n radius.

## GPT-4.1 Filtered Clouds

GPT-4.1 score>=2 comparison uses `n=36`, limited by `editor_matched64_1024`.

{table(gpt41_boot, ['role_or_run','filter_condition','matched_n','original_n','rms_radius_median','anisotropy_ratio_2d_l1_l2_median','orientation_angle_median','orientation_abs_deviation_p95'])}

Score==3 editor filtered clouds are too small (`n=2` and `n=3`) for reliable covariance or orientation estimates. They should be treated as sparse centroid references only.

## Editor Run Comparison

{table(editor_boot, ['role_or_run','filter_condition','matched_n','rms_radius_median','anisotropy_ratio_2d_l1_l2_median','orientation_angle_median','orientation_abs_deviation_p95'])}

The two editor runs have similar all-response radii under matched-n comparison. GPT-4.1 score>=2 filtering pulls both editor centroids toward the published editor vector and reduces spread, which is consistent with a role-expression filter selecting a narrower assistant-adjacent subcloud.

## Orientation Reliability

{table(meaningful.sort_values(['role_or_run','filter_condition']), ['role_or_run','filter_condition','n','orientation_interpretation','orientation_reason','anisotropy_ratio_2d_l1_l2','first_pc_explained_variance_2d','dominant_orientation_angle_pc1_pc2'])}

Near-isotropic or sparse clouds are not assigned meaningful preferred directions. Sparse `score==3` editor layers remain `Unknown`.

## Answers To The Main Questions

1. Cloud artifacts exist for all five requested role/run families in `activation_cloud_layered_viewer_data.json`, with A100 source tables for amateur/playwright and recovered adaptive source tables for trickster/editor.
2. Sample sizes range from `n=2` for sparse editor score==3 filters to `n=1200` for trickster all/GPT-4.1 score>=2.
3. Centroid locations are reported in `cloud_geometry_metrics.csv`; they remain distinct from cloud shape.
4. Cloud size differs by role/run; matched-n controls do not support trickster as the largest-radius cloud.
5. Cloud anisotropy is strongest for playwright/editor-style clouds and weakest for trickster among all-response clouds.
6. Dominant orientations are meaningful only for anisotropic/stable clouds; sparse score==3 editor layers have no reliable orientation estimate.
7. Matched-n bootstrapping is central: all-response comparisons use `n=60`, GPT-4.1 score>=2 uses `n=36`, GPT-5.5 score>=2 uses available amateur/playwright only at `n=44`.
8. Trickster appears less directionally constrained by anisotropy/orientation stability, not by spread/volume. Its large visual footprint is partly a sample-size artifact.
9. Filtering often tightens or shifts clouds, especially editor; trickster is not affected by GPT-4.1 filtering because nearly all trickster responses pass.
10. Roles should be treated as local response-state distributions, not just points. Centroids summarize location, while radius, anisotropy, and filter sensitivity summarize local manifold shape.

## Interpretation

**Observed:** Role/run clouds differ in centroid, radius, anisotropy, and filter sensitivity.

**Inferred:** Editor failure is plausibly related to a narrow assistant-adjacent accepted-response subcloud: GPT-4.1 filtering reduces spread and shifts editor centroids toward the published editor role vector, but score==3 yield is too sparse for stable shape analysis.

**Speculative:** These local cloud-shape differences may explain why some personas are easier to elicit or stabilize than others, but the current set has only five role/run families and repeated editor variants.

**Unknown:** Whether the same cloud-shape signatures hold under a broader, balanced role sample.

## Paper Placement

This should be framed primarily as future Paper 2 / local-manifold evidence, with limited Paper 1.5 support for the claim that persona vectors are centroids of distributions rather than exhaustive descriptions of role behavior. It should not be treated as a core Paper 1.5 proof until more roles are sampled under matched extraction conditions.
"""
    (OUT / "persona_cloud_geometry_report.md").write_text(report)


def fmt_cell(value) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def df_to_md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    headers = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(fmt_cell(row[c]) for c in df.columns) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    points = load_points()
    inventory = artifact_inventory(points)
    inventory.to_csv(OUT / "cloud_geometry_artifact_inventory.csv", index=False)
    conditions = build_conditions(points)

    metric_rows = []
    for (role_run, layer), sub in sorted(conditions.items()):
        coords = sub[PC_COLS].to_numpy(float)
        m = covariance_metrics(coords)
        m.update(
            {
                "role_or_run": role_run,
                "role": sub["role"].iloc[0],
                "filter_condition": layer,
                "source_point_rows": len(sub),
            }
        )
        boot = bootstrap_metrics(coords, min(len(coords), max(3, len(coords))))
        summary = summarize_bootstrap(boot)
        m.update({k: v for k, v in summary.items() if k.startswith("orientation")})
        interp, reason = orientation_label(pd.Series(m))
        m["orientation_interpretation"] = interp
        m["orientation_reason"] = reason
        metric_rows.append(m)

    metrics = pd.DataFrame(metric_rows)
    metrics = metrics[
        [
            "role_or_run",
            "role",
            "filter_condition",
            "n",
            "centroid_pc1",
            "centroid_pc2",
            "centroid_pc3",
            "mean_distance_to_centroid",
            "median_distance_to_centroid",
            "rms_radius",
            "cov2_lambda1",
            "cov2_lambda2",
            "anisotropy_ratio_2d_l1_l2",
            "first_pc_explained_variance_2d",
            "dominant_orientation_angle_pc1_pc2",
            "orientation_angle_median",
            "orientation_abs_deviation_median",
            "orientation_abs_deviation_p95",
            "orientation_stability_width_p90",
            "ellipse_area_95_pc1_pc2",
            "convex_hull_area_pc1_pc2",
            "cov3_lambda1",
            "cov3_lambda2",
            "cov3_lambda3",
            "anisotropy_ratio_3d_l1_mean_rest",
            "first_pc_explained_variance_3d",
            "ellipsoid_volume_95_pc123",
            "orientation_interpretation",
            "orientation_reason",
            "source_point_rows",
        ]
    ]
    metrics.to_csv(OUT / "cloud_geometry_metrics.csv", index=False)

    boot_summary, boot_distributions = run_matched_bootstraps(conditions, metrics)
    boot_summary.to_csv(OUT / "cloud_geometry_bootstrap_summary.csv", index=False)

    make_static_plot(points, metrics)
    make_bootstrap_plot(boot_summary)
    make_distribution_plots(boot_distributions, metrics)
    make_interactive(points, metrics)
    write_report(metrics, boot_summary, inventory)

    print(
        json.dumps(
            {
                "output_dir": str(OUT.relative_to(ROOT)),
                "conditions": int(len(metrics)),
                "points": int(len(points)),
                "bootstrap_rows": int(len(boot_summary)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
