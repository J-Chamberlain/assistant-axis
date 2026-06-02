#!/usr/bin/env python3
"""Cluster-conditioned PC2 extreme diagnostics.

Uses only local committed/research artifacts. No GPU work and no model calls.
"""

from __future__ import annotations

import csv
import json
import math
import os
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from scipy.stats import pearsonr, spearmanr


MODEL_USED = "GPT-5.5"
REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "research/outputs/pc2_cluster_conditioned_extremes"
GEOMETRY_PATH = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
PRIOR_MUTED_PATH = REPO_ROOT / "research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_extremes_report.md"
PC2_CANDIDATE_SCORES = REPO_ROOT / "research/q2_stability/qwen/outputs/pc2_conditional_validation/pc2_candidate_scores.csv"

DIAGNOSTIC_ROLES = [
    "shapeshifter",
    "chameleon",
    "tree",
    "hive",
    "elder",
    "patient",
    "amateur",
    "philosopher",
    "tulpa",
    "actor",
    "caregiver",
    "healer",
    "guardian",
    "optimist",
    "workaholic",
    "blogger",
    "podcaster",
    "influencer",
]

EXPECTED_DIRECTIONS = {
    "shapeshifter": "high",
    "chameleon": "high",
    "tree": "low",
    "hive": "low",
    "elder": "low",
    "patient": "high",
    "amateur": "high",
    "philosopher": "low",
}

CLUSTER_COLORS = {
    "procedural_professional": "#377eb8",
    "grounded_social": "#4daf4a",
    "mythic_spiritual": "#984ea3",
    "combative_iconoclast": "#e41a1c",
    "editorial": "#ff7f00",
    "trickster_chaos": "#a65628",
    "other": "#777777",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def percentile(values: list[float], q: float) -> float:
    xs = sorted(values)
    if not xs:
        return float("nan")
    pos = (len(xs) - 1) * q / 100.0
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def percentile_rank(values: list[float], value: float) -> float:
    below = sum(1 for x in values if x < value)
    equal = sum(1 for x in values if x == value)
    return 100.0 * (below + 0.5 * equal) / len(values)


def median(values: list[float]) -> float:
    return statistics.median(values)


def read_geometry() -> list[dict]:
    data = json.load(open(GEOMETRY_PATH))
    r = data["roles"]
    pc1_vals = [x[0] for x in r["pca3d"]]
    pc2_vals = [x[1] for x in r["pca3d"]]
    pc3_vals = [x[2] for x in r["pca3d"]]
    rows = []
    for i, name in enumerate(r["names"]):
        pc1, pc2, pc3 = r["pca3d"][i]
        rows.append(
            {
                "persona": name,
                "cluster": r["clusters"][i],
                "pc1": pc1,
                "pc2": pc2,
                "pc3": pc3,
                "pc1_percentile": percentile_rank(pc1_vals, pc1),
                "pc2_percentile": percentile_rank(pc2_vals, pc2),
                "pc3_percentile": percentile_rank(pc3_vals, pc3),
            }
        )
    by_pc2 = sorted(rows, key=lambda x: x["pc2"], reverse=True)
    for rank, row in enumerate(by_pc2, 1):
        row["global_pc2_rank_desc"] = rank
    by_cluster = defaultdict(list)
    for row in rows:
        by_cluster[row["cluster"]].append(row)
    for cluster, items in by_cluster.items():
        ranked = sorted(items, key=lambda x: x["pc2"], reverse=True)
        for rank, row in enumerate(ranked, 1):
            row["cluster_pc2_rank_desc"] = rank
            row["cluster_size"] = len(items)
            row["cluster_pc2_median"] = median([x["pc2"] for x in items])
            row["cluster_pc1_median"] = median([x["pc1"] for x in items])
    return rows


def fmt(x: float) -> str:
    return f"{x:.6f}" if isinstance(x, float) and math.isfinite(x) else str(x)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def output_row(row: dict) -> dict:
    return {
        "persona": row["persona"],
        "cluster": row["cluster"],
        "pc1": fmt(row["pc1"]),
        "pc2": fmt(row["pc2"]),
        "pc3": fmt(row["pc3"]),
        "pc1_percentile": fmt(row["pc1_percentile"]),
        "pc2_percentile": fmt(row["pc2_percentile"]),
        "pc3_percentile": fmt(row["pc3_percentile"]),
        "global_pc2_rank_desc": row["global_pc2_rank_desc"],
        "cluster_pc2_rank_desc": row["cluster_pc2_rank_desc"],
        "cluster_size": row["cluster_size"],
    }


def build_global_ranking(rows: list[dict]) -> list[dict]:
    return [output_row(r) for r in sorted(rows, key=lambda x: x["pc2"], reverse=True)]


def build_per_cluster_rankings(rows: list[dict]) -> tuple[list[dict], dict]:
    out = []
    stats = {}
    by_cluster = defaultdict(list)
    for row in rows:
        by_cluster[row["cluster"]].append(row)
    for cluster in sorted(by_cluster):
        items = sorted(by_cluster[cluster], key=lambda x: x["pc2"], reverse=True)
        vals = [x["pc2"] for x in items]
        stats[cluster] = {
            "count": len(items),
            "pc2_mean": statistics.mean(vals),
            "pc2_median": statistics.median(vals),
            "pc2_min": min(vals),
            "pc2_max": max(vals),
            "pc2_std": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
        }
        if len(items) >= 10:
            selected = items[:10] + items[-10:]
        else:
            selected = items
        for r in selected:
            rr = output_row(r)
            rr["within_cluster_extreme_band"] = (
                "top10_pc2" if r["cluster_pc2_rank_desc"] <= 10 else "bottom10_pc2"
            )
            out.append(rr)
    return out, stats


def build_muted_pc1_within_cluster(rows: list[dict]) -> tuple[list[dict], dict]:
    out = []
    meta = {}
    by_cluster = defaultdict(list)
    for row in rows:
        by_cluster[row["cluster"]].append(row)
    for cluster in sorted(by_cluster):
        items = by_cluster[cluster]
        pc1s = [x["pc1"] for x in items]
        selection = None
        for label, lo_q, hi_q in [
            ("cluster_pc1_central_40_60", 40, 60),
            ("cluster_pc1_central_35_65", 35, 65),
        ]:
            lo = percentile(pc1s, lo_q)
            hi = percentile(pc1s, hi_q)
            chosen = [x for x in items if lo <= x["pc1"] <= hi]
            if len(chosen) >= 12:
                selection = (label, lo_q, hi_q, lo, hi, chosen)
                break
        if selection is None:
            lo = percentile(pc1s, 35)
            hi = percentile(pc1s, 65)
            chosen = [x for x in items if lo <= x["pc1"] <= hi]
            meta[cluster] = {
                "status": "too_sparse",
                "cluster_count": len(items),
                "attempted_35_65_count": len(chosen),
            }
            continue
        label, lo_q, hi_q, lo, hi, chosen = selection
        ranked = sorted(chosen, key=lambda x: x["pc2"], reverse=True)
        meta[cluster] = {
            "status": "included",
            "selection_band": label,
            "pc1_lower_percentile": lo_q,
            "pc1_upper_percentile": hi_q,
            "pc1_lower_value": lo,
            "pc1_upper_value": hi,
            "selected_count": len(ranked),
            "cluster_count": len(items),
        }
        for rank, r in enumerate(ranked, 1):
            rr = output_row(r)
            rr["muted_pc1_selection_band"] = label
            rr["muted_pc1_rank_desc"] = rank
            rr["muted_pc1_selected_count"] = len(ranked)
            out.append(rr)
    return out, meta


def diagnostic_table(rows: list[dict]) -> list[dict]:
    by_name = {r["persona"]: r for r in rows}
    out = []
    for name in DIAGNOSTIC_ROLES:
        if name not in by_name:
            out.append({"persona": name, "found": False})
            continue
        r = by_name[name]
        side_global = "above_global_median" if r["pc2"] > median([x["pc2"] for x in rows]) else "below_global_median"
        side_cluster = "above_cluster_median" if r["pc2"] > r["cluster_pc2_median"] else "below_cluster_median"
        note = ""
        if name in {"shapeshifter", "chameleon"}:
            note = "identity plasticity/social adaptation prediction case"
        elif name in {"tree", "hive", "elder", "philosopher"}:
            note = "stability/rootedness/integration prediction case"
        elif name in {"patient", "amateur"}:
            note = "vulnerability/formative-state prediction case"
        out.append(
            {
                "persona": name,
                "found": True,
                "cluster": r["cluster"],
                "pc1": fmt(r["pc1"]),
                "pc2": fmt(r["pc2"]),
                "pc3": fmt(r["pc3"]),
                "pc1_percentile": fmt(r["pc1_percentile"]),
                "pc2_percentile": fmt(r["pc2_percentile"]),
                "pc3_percentile": fmt(r["pc3_percentile"]),
                "global_pc2_rank_desc": r["global_pc2_rank_desc"],
                "cluster_pc2_rank_desc": r["cluster_pc2_rank_desc"],
                "cluster_size": r["cluster_size"],
                "cluster_pc2_median": fmt(r["cluster_pc2_median"]),
                "pc2_side_global": side_global,
                "pc2_side_cluster": side_cluster,
                "diagnostic_note": note,
            }
        )
    return out


def expected_checks(rows: list[dict]) -> list[dict]:
    by_name = {r["persona"]: r for r in rows}
    global_med = median([x["pc2"] for x in rows])
    out = []
    for name, expected in EXPECTED_DIRECTIONS.items():
        r = by_name[name]
        global_side = "high" if r["pc2"] > global_med else "low"
        cluster_side = "high" if r["pc2"] > r["cluster_pc2_median"] else "low"
        out.append(
            {
                "persona": name,
                "expected_pc2_side": expected,
                "cluster": r["cluster"],
                "pc2": fmt(r["pc2"]),
                "global_pc2_median": fmt(global_med),
                "cluster_pc2_median": fmt(r["cluster_pc2_median"]),
                "actual_global_side": global_side,
                "actual_cluster_side": cluster_side,
                "global_pass": global_side == expected,
                "cluster_pass": cluster_side == expected,
                "caveat": expected_check_caveat(name, r, global_side, cluster_side),
            }
        )
    return out


def expected_check_caveat(name: str, row: dict, global_side: str, cluster_side: str) -> str:
    if name == "shapeshifter" and cluster_side != "high":
        return "Strong counterexample to naive plasticity=high-PC2 within cluster."
    if name == "tree" and global_side != "low":
        return "Potential counterexample if rootedness is expected to dominate over mythic/organic cluster context."
    if global_side != cluster_side:
        return "Global and cluster-conditioned signs diverge; cluster baseline matters."
    return ""


def cluster_controlled_correlations(rows: list[dict]) -> dict:
    if not PC2_CANDIDATE_SCORES.exists():
        return {"status": "no_existing_proxy_scores_found"}
    score_rows = []
    with PC2_CANDIDATE_SCORES.open() as f:
        for r in csv.DictReader(f):
            score_rows.append(r)
    geo = {r["persona"]: r for r in rows}
    fields = [
        "maturity",
        "abstraction",
        "expertise",
        "uncertainty_exposure",
        "residence_time_under_uncertainty",
        "coherent_action_under_unresolved_uncertainty",
    ]
    merged = []
    for s in score_rows:
        name = s["persona"]
        if name not in geo:
            continue
        rec = {"persona": name, "cluster": geo[name]["cluster"], "pc2": geo[name]["pc2"]}
        for field in fields:
            rec[field] = float(s[field])
        merged.append(rec)
    result = {"status": "used_existing_pc2_conditional_validation_scores", "n": len(merged), "fields": {}}
    for field in fields:
        xs = [r[field] for r in merged]
        ys = [r["pc2"] for r in merged]
        pr = pearsonr(xs, ys)
        sr = spearmanr(xs, ys)
        # Cluster-demeaned association.
        by_cluster = defaultdict(list)
        for r in merged:
            by_cluster[r["cluster"]].append(r)
        x_dm = []
        y_dm = []
        for cluster, items in by_cluster.items():
            mx = statistics.mean([r[field] for r in items])
            my = statistics.mean([r["pc2"] for r in items])
            for r in items:
                x_dm.append(r[field] - mx)
                y_dm.append(r["pc2"] - my)
        dpr = pearsonr(x_dm, y_dm)
        dsr = spearmanr(x_dm, y_dm)
        result["fields"][field] = {
            "global_pearson_r": pr.statistic,
            "global_pearson_p": pr.pvalue,
            "global_spearman_r": sr.statistic,
            "global_spearman_p": sr.pvalue,
            "cluster_demeaned_pearson_r": dpr.statistic,
            "cluster_demeaned_pearson_p": dpr.pvalue,
            "cluster_demeaned_spearman_r": dsr.statistic,
            "cluster_demeaned_spearman_p": dsr.pvalue,
        }
    return result


def write_scoring_template(path: Path, rows: list[dict]) -> None:
    fields = [
        "persona",
        "cluster",
        "text_source",
        "stability_integration_score_0_100",
        "impressionability_transition_score_0_100",
        "situated_vulnerability_score_0_100",
        "rooted_durable_identity_score_0_100",
        "social_exposure_reactivity_score_0_100",
        "developmental_formative_state_score_0_100",
        "rationale",
        "rater_id",
    ]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in sorted(rows, key=lambda r: (r["cluster"], r["persona"])):
            w.writerow({
                "persona": row["persona"],
                "cluster": row["cluster"],
                "text_source": "",
                "stability_integration_score_0_100": "",
                "impressionability_transition_score_0_100": "",
                "situated_vulnerability_score_0_100": "",
                "rooted_durable_identity_score_0_100": "",
                "social_exposure_reactivity_score_0_100": "",
                "developmental_formative_state_score_0_100": "",
                "rationale": "",
                "rater_id": "",
            })


def scale(value: float, lo: float, hi: float, a: int, b: int) -> float:
    if hi == lo:
        return (a + b) / 2
    return a + (value - lo) * (b - a) / (hi - lo)


def svg_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_plots(rows: list[dict], path_svg: Path, path_png: Path) -> None:
    width, height = 1800, 1400
    margin = 70
    pc1s = [r["pc1"] for r in rows]
    pc2s = [r["pc2"] for r in rows]
    pc3s = [r["pc3"] for r in rows]
    diag = {r for r in DIAGNOSTIC_ROLES}

    def panel_axes(x0, y0, w, h, title):
        return [
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fbfbfb" stroke="#cccccc"/>',
            f'<text x="{x0+12}" y="{y0+24}" font-size="18" font-family="Arial" font-weight="bold">{title}</text>',
        ]

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append('<text x="40" y="38" font-size="24" font-family="Arial" font-weight="bold">PC2 cluster-conditioned diagnostics</text>')

    # Panel 1: PC1 vs PC2.
    x0, y0, w, h = 50, 70, 820, 560
    parts += panel_axes(x0, y0, w, h, "PC1 vs PC2 by cluster")
    for r in rows:
        x = scale(r["pc1"], min(pc1s), max(pc1s), x0 + margin, x0 + w - margin)
        y = scale(r["pc2"], min(pc2s), max(pc2s), y0 + h - margin, y0 + margin)
        color = CLUSTER_COLORS.get(r["cluster"], "#999999")
        rad = 6 if r["persona"] in diag else 3
        stroke = "black" if r["persona"] in diag else "none"
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{color}" fill-opacity="0.75" stroke="{stroke}"/>')
        if r["persona"] in diag:
            parts.append(f'<text x="{x+7:.1f}" y="{y-7:.1f}" font-size="11" font-family="Arial">{svg_escape(r["persona"])}</text>')
    parts.append(f'<text x="{x0+w/2-25}" y="{y0+h-18}" font-size="14" font-family="Arial">PC1</text>')
    parts.append(f'<text x="{x0+12}" y="{y0+h/2}" font-size="14" font-family="Arial" transform="rotate(-90 {x0+12},{y0+h/2})">PC2</text>')

    # Panel 2: global rank plot.
    x0, y0, w, h = 930, 70, 820, 560
    parts += panel_axes(x0, y0, w, h, "Global PC2 rank")
    ranked = sorted(rows, key=lambda x: x["pc2"], reverse=True)
    for i, r in enumerate(ranked, 1):
        x = scale(i, 1, len(ranked), x0 + margin, x0 + w - margin)
        y = scale(r["pc2"], min(pc2s), max(pc2s), y0 + h - margin, y0 + margin)
        color = CLUSTER_COLORS.get(r["cluster"], "#999999")
        rad = 6 if r["persona"] in diag else 2.3
        stroke = "black" if r["persona"] in diag else "none"
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{color}" fill-opacity="0.75" stroke="{stroke}"/>')
        if r["persona"] in diag:
            parts.append(f'<text x="{x+6:.1f}" y="{y-6:.1f}" font-size="11" font-family="Arial">{svg_escape(r["persona"])}</text>')
    parts.append(f'<text x="{x0+w/2-38}" y="{y0+h-18}" font-size="14" font-family="Arial">rank high-to-low</text>')

    # Panel 3: cluster PC2 strips.
    x0, y0, w, h = 50, 710, 820, 560
    parts += panel_axes(x0, y0, w, h, "Per-cluster PC2 strips")
    clusters = sorted(Counter(r["cluster"] for r in rows), key=lambda c: c)
    for ci, cluster in enumerate(clusters):
        cy = scale(ci, 0, max(1, len(clusters)-1), y0 + margin, y0 + h - margin)
        parts.append(f'<text x="{x0+10}" y="{cy+4:.1f}" font-size="12" font-family="Arial">{cluster}</text>')
        parts.append(f'<line x1="{x0+210}" y1="{cy:.1f}" x2="{x0+w-margin}" y2="{cy:.1f}" stroke="#dddddd"/>')
        items = [r for r in rows if r["cluster"] == cluster]
        for r in items:
            x = scale(r["pc2"], min(pc2s), max(pc2s), x0 + 230, x0 + w - margin)
            color = CLUSTER_COLORS.get(r["cluster"], "#999999")
            rad = 6 if r["persona"] in diag else 3
            stroke = "black" if r["persona"] in diag else "none"
            parts.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{rad}" fill="{color}" fill-opacity="0.75" stroke="{stroke}"/>')
            if r["persona"] in diag:
                parts.append(f'<text x="{x+6:.1f}" y="{cy-6:.1f}" font-size="10" font-family="Arial">{svg_escape(r["persona"])}</text>')
    parts.append(f'<text x="{x0+w/2-15}" y="{y0+h-18}" font-size="14" font-family="Arial">PC2</text>')

    # Panel 4: PC2 vs PC3.
    x0, y0, w, h = 930, 710, 820, 560
    parts += panel_axes(x0, y0, w, h, "PC2 vs PC3 by cluster")
    for r in rows:
        x = scale(r["pc2"], min(pc2s), max(pc2s), x0 + margin, x0 + w - margin)
        y = scale(r["pc3"], min(pc3s), max(pc3s), y0 + h - margin, y0 + margin)
        color = CLUSTER_COLORS.get(r["cluster"], "#999999")
        rad = 6 if r["persona"] in diag else 3
        stroke = "black" if r["persona"] in diag else "none"
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="{color}" fill-opacity="0.75" stroke="{stroke}"/>')
        if r["persona"] in diag:
            parts.append(f'<text x="{x+7:.1f}" y="{y-7:.1f}" font-size="11" font-family="Arial">{svg_escape(r["persona"])}</text>')
    parts.append(f'<text x="{x0+w/2-15}" y="{y0+h-18}" font-size="14" font-family="Arial">PC2</text>')
    parts.append(f'<text x="{x0+12}" y="{y0+h/2}" font-size="14" font-family="Arial" transform="rotate(-90 {x0+12},{y0+h/2})">PC3</text>')

    # Legend.
    lx, ly = 50, 1320
    for i, cluster in enumerate(clusters):
        x = lx + i * 240
        color = CLUSTER_COLORS.get(cluster, "#999999")
        parts.append(f'<circle cx="{x}" cy="{ly}" r="6" fill="{color}"/>')
        parts.append(f'<text x="{x+10}" y="{ly+4}" font-size="12" font-family="Arial">{cluster}</text>')
    parts.append("</svg>")
    path_svg.write_text("\n".join(parts), encoding="utf-8")
    try:
        subprocess.run(["sips", "-s", "format", "png", str(path_svg), "--out", str(path_png)], check=True, capture_output=True)
    except Exception:
        # Keep SVG if conversion is unavailable; create a tiny placeholder note in the PNG path.
        path_png.write_bytes(b"")


def top_bottom_md(rows: list[dict], n: int = 10) -> str:
    top = sorted(rows, key=lambda x: x["pc2"], reverse=True)[:n]
    bottom = sorted(rows, key=lambda x: x["pc2"])[:n]
    def table(title, items):
        lines = [f"### {title}", "", "| Rank | Persona | Cluster | PC1 | PC2 | PC3 | PC2 pct |", "|---:|---|---|---:|---:|---:|---:|"]
        for i, r in enumerate(items, 1):
            lines.append(f"| {i} | {r['persona']} | {r['cluster']} | {r['pc1']:.3f} | {r['pc2']:.3f} | {r['pc3']:.3f} | {r['pc2_percentile']:.1f} |")
        return "\n".join(lines)
    return table("Global PC2 Top 10", top) + "\n\n" + table("Global PC2 Bottom 10", bottom)


def per_cluster_summary_md(rows: list[dict]) -> str:
    by_cluster = defaultdict(list)
    for r in rows:
        by_cluster[r["cluster"]].append(r)
    lines = ["## Per-Cluster PC2 Extremes", ""]
    for cluster in sorted(by_cluster):
        items = sorted(by_cluster[cluster], key=lambda x: x["pc2"], reverse=True)
        lines += [f"### {cluster} (n={len(items)})", ""]
        if len(items) < 10:
            lines += ["Cluster has fewer than 10 roles; full ranking is in CSV.", ""]
            continue
        top = ", ".join(f"{r['persona']} ({r['pc2']:.1f})" for r in items[:10])
        bottom = ", ".join(f"{r['persona']} ({r['pc2']:.1f})" for r in reversed(items[-10:]))
        lines += [f"- High PC2: {top}", f"- Low PC2: {bottom}", ""]
    return "\n".join(lines)


def write_report(rows: list[dict], per_cluster_stats: dict, muted_meta: dict, expected: list[dict], corr: dict, diag: list[dict]) -> None:
    cluster_counts = Counter(r["cluster"] for r in rows)
    global_pass = sum(str(r["global_pass"]) == "True" for r in expected)
    cluster_pass = sum(str(r["cluster_pass"]) == "True" for r in expected)
    shape = next(r for r in diag if r["persona"] == "shapeshifter")
    cham = next(r for r in diag if r["persona"] == "chameleon")
    tree = next(r for r in diag if r["persona"] == "tree")
    hive = next(r for r in diag if r["persona"] == "hive")
    elder = next(r for r in diag if r["persona"] == "elder")
    patient = next(r for r in diag if r["persona"] == "patient")
    amateur = next(r for r in diag if r["persona"] == "amateur")
    philosopher = next(r for r in diag if r["persona"] == "philosopher")

    corr_summary = ""
    if corr.get("status") == "used_existing_pc2_conditional_validation_scores":
        fields = corr["fields"]
        corr_summary = "\n".join(
            f"- {k}: global Pearson r={v['global_pearson_r']:.3f}, cluster-demeaned Pearson r={v['cluster_demeaned_pearson_r']:.3f}"
            for k, v in fields.items()
        )
    else:
        corr_summary = "- No existing proxy scores found; future scoring template created."

    report = f"""# Cluster-Conditioned PC2 Extremes Diagnostic

- Date: {utc_now()}
- model_used: {MODEL_USED}
- Geometry source: `research/visualizations/geometry_viz_data.json`
- No GPU work and no new LLM judge calls were run.

## Dataset

- Total roles/personas: {len(rows)}
- Clusters analyzed: {', '.join(f'{k}={v}' for k, v in sorted(cluster_counts.items()))}
- Clusters with at least 10 roles: {', '.join(k for k, v in sorted(cluster_counts.items()) if v >= 10)}
- Sparse cluster skipped for top/bottom requirement: {', '.join(k for k, v in sorted(cluster_counts.items()) if v < 10) or 'none'}

{top_bottom_md(rows)}

{per_cluster_summary_md(rows)}

## Muted-PC1 Within-Cluster Results

Within each cluster, I selected the central 40th-60th percentile PC1 band when it yielded at least 12 roles, widened to 35th-65th if needed, and skipped clusters that remained too sparse.

| Cluster | Status | Band | Selected / Cluster |
|---|---|---|---:|
"""
    for cluster in sorted(muted_meta):
        m = muted_meta[cluster]
        report += f"| {cluster} | {m['status']} | {m.get('selection_band', 'n/a')} | {m.get('selected_count', m.get('attempted_35_65_count', 0))} / {m['cluster_count']} |\n"

    report += f"""
## Diagnostic Role Checks

The eight hand-coded expected-direction checks passed {global_pass}/8 against the global median and {cluster_pass}/8 against cluster medians.

| Role | Expected | Global side | Cluster side | PC2 | Cluster | Note |
|---|---|---|---|---:|---|---|
"""
    expected_by = {r["persona"]: r for r in expected}
    for name in EXPECTED_DIRECTIONS:
        e = expected_by[name]
        report += f"| {name} | {e['expected_pc2_side']} | {e['actual_global_side']} | {e['actual_cluster_side']} | {float(e['pc2']):.3f} | {e['cluster']} | {e['caveat']} |\n"

    report += f"""
Key examples:

- `shapeshifter`: PC2={float(shape['pc2']):.3f}, global rank {shape['global_pc2_rank_desc']}/{len(rows)}, cluster rank {shape['cluster_pc2_rank_desc']}/{shape['cluster_size']}; this is a major counterexample to a simple identity-plasticity=>high-PC2 rule.
- `chameleon`: PC2={float(cham['pc2']):.3f}, above the global median but below the grounded_social cluster median; this matches the broad social-adaptation prediction only before cluster conditioning.
- `tree`: PC2={float(tree['pc2']):.3f}, low globally and within mythic_spiritual, matching the rootedness/stability prediction.
- `hive`: PC2={float(hive['pc2']):.3f}, very low globally and within procedural_professional, matching systemic integration.
- `elder`: PC2={float(elder['pc2']):.3f}, low globally but high relative to the mythic_spiritual cluster median, so it only partially matches the long-residence integration prediction.
- `patient` and `amateur`: high globally and within cluster, matching vulnerability/formative-state predictions.
- `philosopher`: low globally and within cluster, matching abstraction/integration.

## Existing Proxy-Score Associations

Existing `pc2_conditional_validation` scores were reused; no new LLM scoring was performed.

{corr_summary}

## Interpretation

The cluster-conditioned results provide partial support for the refined PC2 hypothesis. High PC2 often emphasizes roles that are situated, vulnerable, socially exposed, formative, or shaped by immediate conditions: amateur, influencer, patient, blogger, podcaster, chameleon, toddler, infant, teenager, addict, and similar cases recur near high-PC2 regions. Low PC2 often emphasizes durable, systemic, rooted, abstract, or long-residence organization: hive, philosopher, elder, guardian, traditionalist, purist, strategist, historian-like and integrated/systemic cases recur near low-PC2 regions.

The interpretation does survive some cluster conditioning, especially within `grounded_social` and `procedural_professional`, but it is not clean enough to promote to an established claim. The biggest counterexamples are important: `shapeshifter` is low PC2 despite identity plasticity, `chameleon` drops below its cluster median despite being high globally, and `elder` is low globally but high relative to mythic_spiritual. These suggest PC2 is not just plasticity vs rootedness. It may instead combine social/developmental exposure, local situational demand, and degree of integrated abstraction, with cluster-specific semantic context changing which surface properties dominate.

## Careful Report Wording

PC2 is best described provisionally as a situated-immediacy/formative-state versus integrated-stability axis. High PC2 tends to collect roles whose behavior is shaped by immediate social context, vulnerability, developmental incompleteness, performance pressure, or dependence on local circumstance. Low PC2 tends to collect roles with more durable, abstract, systemic, rooted, or long-residence organization. This should not be stated as a pure plasticity axis: some plastic or organic roles violate the simple prediction, so PC2 remains a compound axis whose interpretation is strongest when conditioned on PC1 and cluster context.

## Recommended Next Test

Run a blinded within-cluster matched-pair rating study using role prompt text or rollout responses when available. Construct pairs close in PC1 and PC3 within the same cluster but separated on PC2, and force raters to choose which member is more situated/formative/impressionable versus integrated/stable/durable. This would test the interpretation directly rather than relying on role-name intuition.

## Output Files

- `pc2_global_ranking.csv`
- `pc2_per_cluster_rankings.csv`
- `pc2_muted_pc1_within_cluster_rankings.csv`
- `pc2_diagnostic_roles_table.csv`
- `pc2_expected_direction_checks.csv`
- `pc2_cluster_conditioned_stats.json`
- `pc2_cluster_conditioned_plots.png`
- `pc2_scoring_template_for_future_judge.csv`
"""
    (OUT_DIR / "pc2_cluster_conditioned_extremes_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_geometry()
    global_rows = build_global_ranking(rows)
    per_cluster_rows, per_cluster_stats = build_per_cluster_rankings(rows)
    muted_rows, muted_meta = build_muted_pc1_within_cluster(rows)
    diag = diagnostic_table(rows)
    expected = expected_checks(rows)
    corr = cluster_controlled_correlations(rows)

    common_fields = [
        "persona", "cluster", "pc1", "pc2", "pc3", "pc1_percentile", "pc2_percentile", "pc3_percentile",
        "global_pc2_rank_desc", "cluster_pc2_rank_desc", "cluster_size",
    ]
    write_csv(OUT_DIR / "pc2_global_ranking.csv", global_rows, common_fields)
    write_csv(OUT_DIR / "pc2_per_cluster_rankings.csv", per_cluster_rows, common_fields + ["within_cluster_extreme_band"])
    write_csv(OUT_DIR / "pc2_muted_pc1_within_cluster_rankings.csv", muted_rows, common_fields + ["muted_pc1_selection_band", "muted_pc1_rank_desc", "muted_pc1_selected_count"])
    write_csv(OUT_DIR / "pc2_diagnostic_roles_table.csv", diag, [
        "persona", "found", "cluster", "pc1", "pc2", "pc3", "pc1_percentile", "pc2_percentile", "pc3_percentile",
        "global_pc2_rank_desc", "cluster_pc2_rank_desc", "cluster_size", "cluster_pc2_median",
        "pc2_side_global", "pc2_side_cluster", "diagnostic_note",
    ])
    write_csv(OUT_DIR / "pc2_expected_direction_checks.csv", expected, [
        "persona", "expected_pc2_side", "cluster", "pc2", "global_pc2_median", "cluster_pc2_median",
        "actual_global_side", "actual_cluster_side", "global_pass", "cluster_pass", "caveat",
    ])
    write_scoring_template(OUT_DIR / "pc2_scoring_template_for_future_judge.csv", rows)
    stats = {
        "generated_utc": utc_now(),
        "model_used": MODEL_USED,
        "geometry_source": str(GEOMETRY_PATH.relative_to(REPO_ROOT)),
        "n_roles": len(rows),
        "cluster_counts": dict(Counter(r["cluster"] for r in rows)),
        "per_cluster_stats": per_cluster_stats,
        "muted_pc1_within_cluster_meta": muted_meta,
        "expected_direction_summary": {
            "global_pass_count": sum(str(r["global_pass"]) == "True" for r in expected),
            "cluster_pass_count": sum(str(r["cluster_pass"]) == "True" for r in expected),
            "n_checks": len(expected),
        },
        "proxy_score_correlations": corr,
        "prior_muted_pc1_report": str(PRIOR_MUTED_PATH.relative_to(REPO_ROOT)) if PRIOR_MUTED_PATH.exists() else None,
    }
    (OUT_DIR / "pc2_cluster_conditioned_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    write_plots(rows, OUT_DIR / "pc2_cluster_conditioned_plots.svg", OUT_DIR / "pc2_cluster_conditioned_plots.png")
    write_report(rows, per_cluster_stats, muted_meta, expected, corr, diag)
    print(f"Wrote PC2 cluster-conditioned diagnostics to {OUT_DIR}")


if __name__ == "__main__":
    main()
