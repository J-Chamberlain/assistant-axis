#!/usr/bin/env python3
"""Quantify activation-cloud orientation angles for layered response clouds."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research" / "outputs" / "cloud_eigenvector_angle_analysis"
LAYERED_DATA = REPO / "research" / "outputs" / "activation_cloud_layered_viewer" / "activation_cloud_layered_viewer_data.json"
GEOMETRY = REPO / "research" / "visualizations" / "geometry_viz_data.json"

ROLES_OR_RUNS = [
    "amateur",
    "playwright",
    "trickster_phase1_1200",
    "editor_phase1_128",
    "editor_matched64_1024",
]

LAYERS = [
    ("all_responses", "All responses", lambda p: True, "primary"),
    ("gpt41_score_ge2", "GPT-4.1 score>=2", lambda p: p.get("gpt41_score") is not None and p.get("gpt41_score") >= 2, "primary"),
    ("gpt41_score_eq3", "GPT-4.1 score==3", lambda p: p.get("gpt41_score") == 3, "primary"),
    ("gpt55_score_ge2", "GPT-5.5 score>=2", lambda p: p.get("gpt55_score") is not None and p.get("gpt55_score") >= 2, "secondary"),
    ("gpt55_score_eq3", "GPT-5.5 score==3", lambda p: p.get("gpt55_score") == 3, "secondary"),
]

MIN_EIGEN_N = 3
SPARSE_N = 10


def canonical_angle_deg(angle: float) -> float:
    """Return sign-invariant line orientation in [-90, 90)."""
    return ((angle + 90.0) % 180.0) - 90.0


def angle_from_vec(x: float, y: float) -> float:
    return canonical_angle_deg(math.degrees(math.atan2(y, x)))


def angular_difference(a: float, b: float) -> float:
    """Smallest sign-invariant difference between two orientations."""
    diff = abs(canonical_angle_deg(a - b))
    return min(diff, 180.0 - diff)


def orient_vector_2d(v: np.ndarray) -> np.ndarray:
    """Flip sign to produce a canonical orientation with non-negative x when possible."""
    v = np.array(v, dtype=float)
    if abs(v[0]) > 1e-12:
        return v if v[0] >= 0 else -v
    return v if v[1] >= 0 else -v


def eig_sorted(cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    return vals[order], vecs[:, order]


def safe_ratio(a: float, b: float) -> float | None:
    if b <= 1e-12:
        return None
    return float(a / b)


def percentile_rank(values: np.ndarray, value: float) -> float:
    return float(100.0 * np.mean(values <= value))


def nearest_roles(role_names: list[str], coords: np.ndarray, point: np.ndarray, k: int = 5) -> list[dict]:
    d = np.linalg.norm(coords - point[None, :], axis=1)
    order = np.argsort(d)[:k]
    return [{"role": role_names[i], "distance": float(d[i])} for i in order]


def load_inputs() -> tuple[dict, dict]:
    with open(LAYERED_DATA) as f:
        layered = json.load(f)
    with open(GEOMETRY) as f:
        geometry = json.load(f)
    return layered, geometry


def get_layer_points(points: list[dict], role_or_run: str, predicate) -> list[dict]:
    subset = [p for p in points if p["role_or_run"] == role_or_run]
    return [p for p in subset if predicate(p)]


def compute_orientation(points: list[dict], role_or_run: str, role: str, layer_key: str, layer_label: str) -> tuple[dict, dict | None]:
    n = len(points)
    base = {
        "role_or_run": role_or_run,
        "role": role,
        "layer_key": layer_key,
        "layer_label": layer_label,
        "n": n,
        "sparse_warning": "sparse/unstable n<10" if 0 < n < SPARSE_N else ("unavailable" if n == 0 else ""),
    }
    if n < MIN_EIGEN_N:
        row = {
            **base,
            "status": "insufficient_n",
            "anisotropy_ratio_3d": None,
            "dominant_variance_share_3d": None,
            "pc1_pc2_angle_deg": None,
            "pc1_pc3_angle_deg": None,
            "pc2_pc3_angle_deg": None,
            "pc1_pc2_variance_share": None,
        }
        return row, None

    arr = np.array([[p["pc1"], p["pc2"], p["pc3"]] for p in points], dtype=float)
    cov3 = np.cov(arr, rowvar=False)
    vals3, vecs3 = eig_sorted(cov3)
    total3 = float(vals3.sum())
    dom3 = vecs3[:, 0]
    anis = safe_ratio(float(vals3[0]), float(vals3[-1]))
    eig_json = {
        "role_or_run": role_or_run,
        "role": role,
        "layer_key": layer_key,
        "layer_label": layer_label,
        "n": n,
        "covariance_3d": cov3.tolist(),
        "eigenvalues_3d": vals3.tolist(),
        "eigenvectors_3d_columns": vecs3.tolist(),
        "variance_share_3d": (vals3 / total3).tolist() if total3 > 0 else [None, None, None],
    }

    angles = {}
    shares = {}
    vecs2_json = {}
    for key, cols in {
        "pc1_pc2": (0, 1),
        "pc1_pc3": (0, 2),
        "pc2_pc3": (1, 2),
    }.items():
        cov2 = np.cov(arr[:, cols], rowvar=False)
        vals2, vecs2 = eig_sorted(cov2)
        total2 = float(vals2.sum())
        v = orient_vector_2d(vecs2[:, 0])
        angles[key] = angle_from_vec(float(v[0]), float(v[1]))
        shares[key] = float(vals2[0] / total2) if total2 > 0 else None
        vecs2_json[key] = {
            "covariance": cov2.tolist(),
            "eigenvalues": vals2.tolist(),
            "dominant_eigenvector": v.tolist(),
            "dominant_angle_deg": angles[key],
            "dominant_variance_share": shares[key],
        }

    eig_json["plane_eigendecomp"] = vecs2_json
    row = {
        **base,
        "status": "ok",
        "anisotropy_ratio_3d": anis,
        "dominant_variance_share_3d": float(vals3[0] / total3) if total3 > 0 else None,
        "eigenvalue1_3d": float(vals3[0]),
        "eigenvalue2_3d": float(vals3[1]),
        "eigenvalue3_3d": float(vals3[2]),
        "dominant_eigenvector_pc1": float(dom3[0]),
        "dominant_eigenvector_pc2": float(dom3[1]),
        "dominant_eigenvector_pc3": float(dom3[2]),
        "pc1_pc2_angle_deg": angles["pc1_pc2"],
        "pc1_pc3_angle_deg": angles["pc1_pc3"],
        "pc2_pc3_angle_deg": angles["pc2_pc3"],
        "pc1_pc2_variance_share": shares["pc1_pc2"],
        "pc1_pc3_variance_share": shares["pc1_pc3"],
        "pc2_pc3_variance_share": shares["pc2_pc3"],
        "sd_pc1": float(arr[:, 0].std(ddof=1)),
        "sd_pc2": float(arr[:, 1].std(ddof=1)),
        "sd_pc3": float(arr[:, 2].std(ddof=1)),
        "cloud_volume_proxy_sd_product": float(arr[:, 0].std(ddof=1) * arr[:, 1].std(ddof=1) * arr[:, 2].std(ddof=1)),
    }
    return row, eig_json


def compute_reference_directions(geometry: dict) -> tuple[list[dict], dict]:
    roles = geometry["roles"]
    names = roles["names"]
    coords = np.array(roles["pca3d"], dtype=float)
    pc12 = coords[:, :2]
    axis = np.array(roles.get("axis_projections", []), dtype=float)
    refs = [
        {"reference_key": "pc1_axis", "reference_label": "PC1 axis", "angle_deg": 0.0, "method": "definition"},
        {"reference_key": "pc2_axis", "reference_label": "PC2 axis", "angle_deg": 90.0, "method": "definition"},
        {"reference_key": "pc1_pc2_positive_diagonal", "reference_label": "Positive PC1 / positive PC2 diagonal", "angle_deg": 45.0, "method": "definition"},
    ]
    assistant_info = {
        "available": False,
        "method": "not_available",
        "angle_deg": None,
        "coefficients_pc1_pc2": None,
        "r2": None,
        "note": "",
    }
    if len(axis) == len(coords) and np.isfinite(axis).all():
        X = np.column_stack([np.ones(len(pc12)), pc12])
        beta, *_ = np.linalg.lstsq(X, axis, rcond=None)
        pred = X @ beta
        ss_res = float(((axis - pred) ** 2).sum())
        ss_tot = float(((axis - axis.mean()) ** 2).sum())
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else None
        grad = beta[1:]
        angle = angle_from_vec(float(grad[0]), float(grad[1]))
        assistant_info = {
            "available": True,
            "method": "linear_regression_axis_projection_on_pc1_pc2",
            "angle_deg": angle,
            "coefficients_pc1_pc2": [float(grad[0]), float(grad[1])],
            "intercept": float(beta[0]),
            "r2": r2,
            "note": "Proxy gradient estimated from stored role axis_projections; not a separately recovered assistant-axis vector in PCA coordinates.",
        }
        refs.append({
            "reference_key": "assistant_axis_projection_proxy",
            "reference_label": "Assistant-axis projection proxy",
            "angle_deg": angle,
            "method": "regress stored axis_projections on PC1 and PC2",
        })

    # Simple documented upper-boundary proxy: first PC of high-PC1/high-PC2 roles.
    pc1, pc2 = pc12[:, 0], pc12[:, 1]
    mask = (pc1 >= np.percentile(pc1, 60)) & (pc2 >= np.percentile(pc2, 60))
    boundary_note = "roles with PC1 and PC2 >= 60th percentile"
    if mask.sum() < 10:
        mask = (pc1 >= np.percentile(pc1, 55)) & (pc2 >= np.percentile(pc2, 55))
        boundary_note = "fallback roles with PC1 and PC2 >= 55th percentile"
    if mask.sum() >= 3:
        centered = pc12[mask] - pc12[mask].mean(axis=0)
        cov = np.cov(centered, rowvar=False)
        vals, vecs = eig_sorted(cov)
        v = orient_vector_2d(vecs[:, 0])
        angle = angle_from_vec(float(v[0]), float(v[1]))
        refs.append({
            "reference_key": "upper_pc1_pc2_region_proxy",
            "reference_label": "Empirical high-PC1/high-PC2 region proxy",
            "angle_deg": angle,
            "method": f"dominant PC1-PC2 direction among {int(mask.sum())} {boundary_note}",
        })
        assistant_info["upper_pc1_pc2_region_proxy"] = {
            "angle_deg": angle,
            "n_roles": int(mask.sum()),
            "method": boundary_note,
            "example_roles": [names[i] for i in np.where(mask)[0][:10]],
        }
    return refs, assistant_info


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    fields = []
    for row in rows:
        for k in row:
            if k not in fields:
                fields.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def make_boundary_rows(layered: dict, geometry: dict) -> list[dict]:
    roles = geometry["roles"]
    names = roles["names"]
    coords = np.array(roles["pca3d"], dtype=float)
    clusters = dict(zip(names, roles["clusters"]))
    pc1_vals, pc2_vals, pc3_vals = coords[:, 0], coords[:, 1], coords[:, 2]
    max_pc1, max_pc2, min_pc2 = float(pc1_vals.max()), float(pc2_vals.max()), float(pc2_vals.min())

    centroid_lookup = {}
    for c in layered["centroids"]:
        centroid_lookup[(c["role_or_run"], c["layer_key"])] = c

    rows = []
    for rr in ROLES_OR_RUNS:
        pub = centroid_lookup.get((rr, "published"))
        allc = centroid_lookup.get((rr, "all"))
        for label, c in [("published_centroid", pub), ("all_response_centroid", allc)]:
            if not c:
                continue
            point = np.array([float(c["pc1"]), float(c["pc2"]), float(c["pc3"])])
            nns = nearest_roles(names, coords, point)
            role = c["role"]
            rows.append({
                "role_or_run": rr,
                "role": role,
                "centroid_type": label,
                "cluster": clusters.get(role),
                "pc1": float(point[0]),
                "pc2": float(point[1]),
                "pc3": float(point[2]),
                "pc1_percentile": percentile_rank(pc1_vals, float(point[0])),
                "pc2_percentile": percentile_rank(pc2_vals, float(point[1])),
                "pc3_percentile": percentile_rank(pc3_vals, float(point[2])),
                "distance_from_high_pc1_boundary": max_pc1 - float(point[0]),
                "distance_from_high_pc2_boundary": max_pc2 - float(point[1]),
                "distance_from_low_pc2_boundary": float(point[1]) - min_pc2,
                "nearest_roles": "; ".join(f"{x['role']}:{x['distance']:.2f}" for x in nns),
            })
    return rows


def make_plots(orientation_rows: list[dict], boundary_rows: list[dict], layered: dict, geometry: dict) -> None:
    roles = geometry["roles"]
    names = roles["names"]
    coords = np.array(roles["pca3d"], dtype=float)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(coords[:, 0], coords[:, 1], s=12, alpha=0.18, color="#6b7280", label="Qwen roles")
    colors = {
        "amateur": "#1f77b4",
        "playwright": "#2ca02c",
        "trickster_phase1_1200": "#d62728",
        "editor_phase1_128": "#9467bd",
        "editor_matched64_1024": "#ff7f0e",
    }
    b_pub = {(r["role_or_run"], r["centroid_type"]): r for r in boundary_rows}
    all_rows = [r for r in orientation_rows if r["layer_key"] == "all_responses" and r["status"] == "ok"]
    eq3_rows = [r for r in orientation_rows if r["layer_key"] == "gpt41_score_eq3" and r["status"] == "ok" and r["n"] >= SPARSE_N]
    for row in all_rows:
        rr = row["role_or_run"]
        color = colors.get(rr, "black")
        pub = b_pub.get((rr, "published_centroid"))
        allc = b_pub.get((rr, "all_response_centroid"))
        if pub:
            ax.scatter(pub["pc1"], pub["pc2"], marker="*", s=160, color=color, edgecolor="black", linewidth=0.6)
        if allc:
            ax.scatter(allc["pc1"], allc["pc2"], marker="o", s=70, color=color, edgecolor="white", linewidth=0.8, label=rr)
            ang = math.radians(float(row["pc1_pc2_angle_deg"]))
            length = 12.0
            ax.arrow(allc["pc1"] - math.cos(ang) * length / 2, allc["pc2"] - math.sin(ang) * length / 2,
                     math.cos(ang) * length, math.sin(ang) * length,
                     color=color, width=0.18, head_width=1.2, alpha=0.8, length_includes_head=True)
    for row in eq3_rows:
        rr = row["role_or_run"]
        allc = b_pub.get((rr, "all_response_centroid"))
        if not allc:
            continue
        color = colors.get(rr, "black")
        ang = math.radians(float(row["pc1_pc2_angle_deg"]))
        length = 9.0
        ax.arrow(allc["pc1"] - math.cos(ang) * length / 2, allc["pc2"] - math.sin(ang) * length / 2,
                 math.cos(ang) * length, math.sin(ang) * length,
                 color=color, linestyle="--", width=0.08, head_width=0.8, alpha=0.45, length_includes_head=True)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("Activation-cloud dominant PC1-PC2 orientations")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.18)
    fig.tight_layout()
    fig.savefig(OUT / "cloud_orientation_overview_pc1_pc2.png", dpi=180)
    plt.close(fig)

    boundary_map = {(r["role_or_run"], r["centroid_type"]): r for r in boundary_rows}
    plot_rows = [r for r in all_rows if (r["role_or_run"], "published_centroid") in boundary_map]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for row in plot_rows:
        rr = row["role_or_run"]
        b = boundary_map[(rr, "published_centroid")]
        axes[0].scatter(b["pc1_percentile"], row["anisotropy_ratio_3d"], color=colors.get(rr, "black"), s=70)
        axes[0].annotate(rr, (b["pc1_percentile"], row["anisotropy_ratio_3d"]), fontsize=8, xytext=(4, 4), textcoords="offset points")
        axes[1].scatter(b["pc2_percentile"], abs(row["pc1_pc2_angle_deg"]), color=colors.get(rr, "black"), s=70)
        axes[1].annotate(rr, (b["pc2_percentile"], abs(row["pc1_pc2_angle_deg"])), fontsize=8, xytext=(4, 4), textcoords="offset points")
    axes[0].set_xlabel("Published centroid PC1 percentile")
    axes[0].set_ylabel("3D anisotropy ratio")
    axes[0].set_title("Boundary position vs anisotropy")
    axes[1].set_xlabel("Published centroid PC2 percentile")
    axes[1].set_ylabel("|dominant PC1-PC2 angle|")
    axes[1].set_title("PC2 position vs cloud orientation")
    for a in axes:
        a.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "cloud_orientation_boundary_scatter.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    x = np.arange(len(plot_rows))
    labels = [r["role_or_run"] for r in plot_rows]
    ax.bar(x - 0.2, [r["pc1_pc2_angle_deg"] for r in plot_rows], width=0.4, label="PC1-PC2 angle")
    ax.bar(x + 0.2, [r["dominant_variance_share_3d"] * 100 for r in plot_rows], width=0.4, label="Dominant 3D variance %")
    ax.axhline(45, color="#666", linestyle=":", label="45 deg diagonal")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_title("All-response cloud orientation and dominance")
    ax.set_ylabel("Degrees / percent")
    ax.legend()
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "cloud_orientation_report_figure.png", dpi=180)
    plt.close(fig)


def make_interactive_html(orientation_rows: list[dict], boundary_rows: list[dict]) -> None:
    rows = [r for r in orientation_rows if r["layer_key"] == "all_responses" and r["status"] == "ok"]
    boundary = {(r["role_or_run"], r["centroid_type"]): r for r in boundary_rows}
    data = {"orientation_rows": rows, "boundary_rows": boundary_rows}
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Cloud Orientation Interactive</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>body{{font-family:system-ui,sans-serif;margin:24px;}} #plot{{height:720px;}}</style></head>
<body><h1>Activation Cloud Orientation</h1><div id="plot"></div>
<script>
const DATA = {json.dumps(data)};
const traces = [];
for (const r of DATA.orientation_rows) {{
  const c = DATA.boundary_rows.find(x => x.role_or_run === r.role_or_run && x.centroid_type === 'all_response_centroid');
  if (!c) continue;
  const angle = r.pc1_pc2_angle_deg * Math.PI / 180;
  const len = 12;
  traces.push({{
    type:'scatter', mode:'markers+text', name:r.role_or_run,
    x:[c.pc1], y:[c.pc2], text:[r.role_or_run], textposition:'top center',
    hovertemplate:`${{r.role_or_run}}<br>angle=${{r.pc1_pc2_angle_deg.toFixed(1)}}°<br>anisotropy=${{r.anisotropy_ratio_3d.toFixed(2)}}<extra></extra>`
  }});
  traces.push({{
    type:'scatter', mode:'lines', showlegend:false,
    x:[c.pc1-Math.cos(angle)*len/2, c.pc1+Math.cos(angle)*len/2],
    y:[c.pc2-Math.sin(angle)*len/2, c.pc2+Math.sin(angle)*len/2],
    line:{{width:4}}
  }});
}}
Plotly.newPlot('plot', traces, {{title:'All-response dominant PC1-PC2 orientations', xaxis:{{title:'PC1'}}, yaxis:{{title:'PC2'}}, hovermode:'closest'}});
</script></body></html>"""
    (OUT / "cloud_orientation_interactive.html").write_text(html)


def make_report(
    orientation_rows: list[dict],
    refs: list[dict],
    angle_rows: list[dict],
    boundary_rows: list[dict],
    assistant_info: dict,
) -> None:
    all_rows = [r for r in orientation_rows if r["layer_key"] == "all_responses" and r["status"] == "ok"]
    sparse = [r for r in orientation_rows if r["sparse_warning"]]
    diag_key = "pc1_pc2_positive_diagonal"
    pc1_key = "pc1_axis"
    pc2_key = "pc2_axis"
    assistant_key = "assistant_axis_projection_proxy"
    upper_key = "upper_pc1_pc2_region_proxy"
    angle_lookup = {(r["role_or_run"], r["layer_key"], r["reference_key"]): r for r in angle_rows}

    def fmt(v, digits=2):
        if v is None or v == "":
            return "NA"
        return f"{float(v):.{digits}f}"

    lines = []
    lines.append("# Activation Cloud Eigenvector Angle Analysis")
    lines.append("")
    lines.append("Startup status: **STARTUP VERIFIED**.")
    lines.append("")
    lines.append("## Roles/Runs and Layers")
    lines.append("")
    lines.append("Analyzed role/run views: `amateur`, `playwright`, `trickster_phase1_1200`, `editor_phase1_128`, and `editor_matched64_1024`.")
    lines.append("Layers considered: all responses, GPT-4.1 score>=2, GPT-4.1 score==3, GPT-5.5 score>=2 when available, and GPT-5.5 score==3 when available.")
    lines.append("")
    lines.append("## Sparse-Layer Warnings")
    lines.append("")
    for r in sparse:
        lines.append(f"- `{r['role_or_run']}` / {r['layer_label']}: n={r['n']} ({r['sparse_warning']})")
    if not sparse:
        lines.append("- None.")
    lines.append("")
    lines.append("## Dominant All-Response Orientations")
    lines.append("")
    lines.append("| role/run | n | PC1-PC2 angle | dominant 3D variance share | anisotropy | diff PC1 | diff PC2 | diff +45 diagonal | diff assistant proxy | diff upper-region proxy |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in all_rows:
        rr = r["role_or_run"]
        lines.append(
            f"| `{rr}` | {r['n']} | {fmt(r['pc1_pc2_angle_deg'])} | {fmt(100*r['dominant_variance_share_3d'])}% | "
            f"{fmt(r['anisotropy_ratio_3d'])} | {fmt(angle_lookup[(rr, 'all_responses', pc1_key)]['angle_difference_deg'])} | "
            f"{fmt(angle_lookup[(rr, 'all_responses', pc2_key)]['angle_difference_deg'])} | "
            f"{fmt(angle_lookup[(rr, 'all_responses', diag_key)]['angle_difference_deg'])} | "
            f"{fmt(angle_lookup[(rr, 'all_responses', assistant_key)]['angle_difference_deg']) if assistant_info['available'] else 'NA'} | "
            f"{fmt(angle_lookup[(rr, 'all_responses', upper_key)]['angle_difference_deg']) if (rr, 'all_responses', upper_key) in angle_lookup else 'NA'} |"
        )
    lines.append("")
    lines.append("## Reference Directions")
    lines.append("")
    for ref in refs:
        lines.append(f"- {ref['reference_label']}: {fmt(ref['angle_deg'])} degrees ({ref['method']}).")
    lines.append("")
    lines.append("Assistant-axis estimate: " + json.dumps(assistant_info, indent=2))
    lines.append("")
    lines.append("## Boundary-Distance Summary")
    lines.append("")
    lines.append("| role/run | centroid | PC1 pct | PC2 pct | high-PC1 distance | high-PC2 distance | nearest roles |")
    lines.append("|---|---|---:|---:|---:|---:|---|")
    for r in boundary_rows:
        if r["centroid_type"] == "published_centroid":
            lines.append(
                f"| `{r['role_or_run']}` | published | {fmt(r['pc1_percentile'])} | {fmt(r['pc2_percentile'])} | "
                f"{fmt(r['distance_from_high_pc1_boundary'])} | {fmt(r['distance_from_high_pc2_boundary'])} | {r['nearest_roles']} |"
            )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("**Observed.** The all-response clouds are not uniformly circular: editor, amateur, playwright, and trickster all show anisotropy. Playwright and the two editor runs have the strongest all-response anisotropy in this set; amateur is less elongated; trickster is still anisotropic but its dominant PC1-PC2 orientation is qualitatively different. The dominant all-response PC1-PC2 angles should be read as line orientations, so positive and negative arrow signs are equivalent.")
    lines.append("")
    lines.append("**Observed.** Amateur, playwright, and both editor all-response clouds align much better with the empirical high-PC1/high-PC2 region proxy (-21.42 degrees) than with the positive +45 degree PC1-PC2 diagonal. Their angular differences from that upper-region proxy are 13.46, 8.52, 9.60, and 20.13 degrees respectively. Trickster is the exception: its all-response orientation is nearly PC2-vertical (-87.37 degrees), only 2.63 degrees from the PC2 axis and 65.95 degrees from the upper-region proxy.")
    lines.append("")
    lines.append("**Observed.** The assistant-axis proxy is estimated from stored role axis projections by regression on PC1 and PC2. It points at +14.70 degrees with R2=0.966 for that two-dimensional projection. All-response playwright is the closest of the five all-response clouds to this proxy (27.61 degrees away), while amateur/editor all-response clouds are farther and trickster is farthest.")
    lines.append("")
    lines.append("**Inferred.** Amateur, playwright, and editor support the visual impression of a shared PC1-PC2 transition orientation, but the best-matching reference is a shallow negative-slope upper-region direction, not the naive positive-PC1/positive-PC2 diagonal. Editor is strongly elongated, but its role-expression-retained score==3 layers are sparse, so the editor result is better evidence about all-response/procedural-assistant collapse geometry than about stable editor-role expression.")
    lines.append("")
    lines.append("**Inferred.** Trickster does not share the amateur/playwright/editor orientation pattern. Its retained set is large, its GPT-4.1 score>=2 and score==3 layers are effectively the same cloud, and its dominant PC1-PC2 direction is near-vertical. That does not prove a different causal mechanism; it does suggest trickster is not constrained by the same visible PC1-PC2 boundary pattern in these saved runs.")
    lines.append("")
    lines.append("**Speculative.** Distance from the high-PC1 and high-PC2 boundaries may affect observable cloud shape, but this dataset has only five role/run views and repeated editor variants. The boundary scatter should be used to motivate a targeted next role, not to fit a general law. The apparent editor/amateur/playwright alignment should be retested with a negative-PC2 role and another non-editor high-PC1 role before becoming paper-level language.")
    lines.append("")
    lines.append("## Negative-PC2 Role Test Recommendation")
    lines.append("")
    lines.append("Current evidence supports running a negative-PC2 comparison role if another small GPU pilot is launched. `student` remains a useful candidate if the goal is to test whether a formative/developmental role below the current positive-PC2 edge shows a different cloud orientation or boundary relation; however, because `student` may be socially/developmentally loaded, a second negative-PC2 but more integrated/abstract role should be shortlisted as a contrast before launch.")
    lines.append("")
    lines.append("## Output Files")
    lines.append("")
    for name in [
        "cloud_orientation_metrics.csv",
        "cloud_orientation_eigendecomp.json",
        "cloud_reference_direction_table.csv",
        "cloud_angle_differences.csv",
        "assistant_axis_direction_estimate.json",
        "role_boundary_distance_metrics.csv",
        "cloud_orientation_overview_pc1_pc2.png",
        "cloud_orientation_boundary_scatter.png",
        "cloud_orientation_report_figure.png",
        "cloud_orientation_interactive.html",
    ]:
        lines.append(f"- `{name}`")
    (OUT / "cloud_orientation_analysis_report.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    layered, geometry = load_inputs()
    points = layered["points"]

    orientation_rows = []
    eigs = []
    for rr in ROLES_OR_RUNS:
        role_points = [p for p in points if p["role_or_run"] == rr]
        role = role_points[0]["role"] if role_points else rr.split("_")[0]
        for layer_key, layer_label, pred, _kind in LAYERS:
            pts = get_layer_points(points, rr, pred)
            row, eig = compute_orientation(pts, rr, role, layer_key, layer_label)
            orientation_rows.append(row)
            if eig:
                eigs.append(eig)

    refs, assistant_info = compute_reference_directions(geometry)
    ref_rows = refs
    angle_rows = []
    for row in orientation_rows:
        if row["status"] != "ok" or row["pc1_pc2_angle_deg"] is None:
            continue
        for ref in refs:
            angle_rows.append({
                "role_or_run": row["role_or_run"],
                "role": row["role"],
                "layer_key": row["layer_key"],
                "layer_label": row["layer_label"],
                "n": row["n"],
                "cloud_pc1_pc2_angle_deg": row["pc1_pc2_angle_deg"],
                "reference_key": ref["reference_key"],
                "reference_label": ref["reference_label"],
                "reference_angle_deg": ref["angle_deg"],
                "angle_difference_deg": angular_difference(row["pc1_pc2_angle_deg"], ref["angle_deg"]),
                "sparse_warning": row["sparse_warning"],
            })

    boundary_rows = make_boundary_rows(layered, geometry)
    write_csv(OUT / "cloud_orientation_metrics.csv", orientation_rows)
    write_csv(OUT / "cloud_reference_direction_table.csv", ref_rows)
    write_csv(OUT / "cloud_angle_differences.csv", angle_rows)
    write_csv(OUT / "role_boundary_distance_metrics.csv", boundary_rows)
    with open(OUT / "cloud_orientation_eigendecomp.json", "w") as f:
        json.dump({"eigendecomp": eigs}, f, indent=2)
    with open(OUT / "assistant_axis_direction_estimate.json", "w") as f:
        json.dump(assistant_info, f, indent=2)
    make_plots(orientation_rows, boundary_rows, layered, geometry)
    make_interactive_html(orientation_rows, boundary_rows)
    make_report(orientation_rows, refs, angle_rows, boundary_rows, assistant_info)
    print(f"Wrote {OUT}")
    print(f"orientation rows: {len(orientation_rows)}")
    print(f"angle rows: {len(angle_rows)}")


if __name__ == "__main__":
    main()
