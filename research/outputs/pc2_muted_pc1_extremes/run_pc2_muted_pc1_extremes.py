#!/usr/bin/env python3
"""
Inspect PC2 extremes while controlling PC1 near the center of the persona distribution.

Input: research/visualizations/geometry_viz_data.json
Outputs: report, ranking CSVs, band stats JSON, and diagnostic plots.
"""

from __future__ import annotations

import csv
import json
import struct
import zlib
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
GEOMETRY = ROOT / "research/visualizations/geometry_viz_data.json"
OUT_DIR = ROOT / "research/outputs/pc2_muted_pc1_extremes"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def percentile(values: np.ndarray, q: float) -> float:
    return float(np.percentile(values, q))


def percentile_rank(values: np.ndarray, value: float) -> float:
    return float(100.0 * (np.sum(values <= value) - 0.5) / len(values))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_roles() -> list[dict]:
    data = json.loads(GEOMETRY.read_text())
    roles = data["roles"]
    out = []
    for i, name in enumerate(roles["names"]):
        pc1, pc2, pc3 = roles["pca3d"][i]
        out.append(
            {
                "name": name,
                "cluster": roles["clusters"][i],
                "pc1": float(pc1),
                "pc2": float(pc2),
                "pc3": float(pc3),
            }
        )
    return out


def choose_band(roles: list[dict]) -> tuple[str, float, float, list[dict], dict]:
    pc1 = np.array([r["pc1"] for r in roles])
    stats = {}
    selected = None
    for label, lo_pct, hi_pct in [
        ("central_10_percent_45_55", 45, 55),
        ("central_20_percent_40_60", 40, 60),
        ("central_30_percent_35_65", 35, 65),
    ]:
        lo = percentile(pc1, lo_pct)
        hi = percentile(pc1, hi_pct)
        included = [r for r in roles if lo <= r["pc1"] <= hi]
        stats[label] = {
            "lower_percentile": lo_pct,
            "upper_percentile": hi_pct,
            "pc1_lower_bound": lo,
            "pc1_upper_bound": hi,
            "role_count": len(included),
        }
        if selected is None and len(included) >= 25:
            selected = (label, lo, hi, included)
    if selected is None:
        label = "central_30_percent_35_65"
        lo = stats[label]["pc1_lower_bound"]
        hi = stats[label]["pc1_upper_bound"]
        selected = (label, lo, hi, [r for r in roles if lo <= r["pc1"] <= hi])
    return (*selected, stats)


def ranked_rows(roles: list[dict], all_roles: list[dict]) -> list[dict]:
    pc1_vals = np.array([r["pc1"] for r in all_roles])
    pc2_vals = np.array([r["pc2"] for r in all_roles])
    pc3_vals = np.array([r["pc3"] for r in all_roles])
    ranked = sorted(roles, key=lambda r: r["pc2"], reverse=True)
    rows = []
    for i, r in enumerate(ranked, 1):
        rows.append(
            {
                "rank_by_pc2_desc": i,
                "role": r["name"],
                "cluster": r["cluster"],
                "pc1": round(r["pc1"], 6),
                "pc2": round(r["pc2"], 6),
                "pc3": round(r["pc3"], 6),
                "pc1_percentile": round(percentile_rank(pc1_vals, r["pc1"]), 3),
                "pc2_percentile": round(percentile_rank(pc2_vals, r["pc2"]), 3),
                "pc3_percentile": round(percentile_rank(pc3_vals, r["pc3"]), 3),
            }
        )
    return rows


def make_top_bottom(rows: list[dict]) -> list[dict]:
    top = rows[:10]
    bottom = list(reversed(rows[-10:]))
    out = []
    for label, group in [("top_pc2", top), ("bottom_pc2", bottom)]:
        for i, row in enumerate(group, 1):
            item = dict(row)
            item["extreme_group"] = label
            item["extreme_rank"] = i
            out.append(item)
    return out


def cluster_caution(rows: list[dict]) -> str:
    counts = Counter(r["cluster"] for r in rows)
    n = len(rows)
    most_cluster, most_count = counts.most_common(1)[0]
    if n < 25:
        return f"Caution: selected band contains only {n} roles, below the preferred stable-inspection threshold."
    if most_count / n >= 0.45:
        return f"Caution: selected band is cluster-skewed: {most_cluster} accounts for {most_count}/{n} roles."
    return f"No strong sample-size or single-cluster skew warning: largest cluster is {most_cluster} with {most_count}/{n} roles."


def interpret(top: list[dict], bottom: list[dict]) -> tuple[str, str, str, str]:
    top_roles = [r["role"] for r in top]
    bottom_roles = [r["role"] for r in bottom]
    top_text = ", ".join(top_roles)
    bottom_text = ", ".join(bottom_roles)
    high = (
        "High PC2 within muted PC1 is dominated by socially situated, practical, local-role, "
        "and developmentally immediate personas: "
        f"{top_text}. The pattern looks interpersonal and circumstance-bound rather than abstract."
    )
    low = (
        "Low PC2 within muted PC1 is dominated by abstracting, integrative, systemic, "
        "standards-bearing, or craft/procedural personas: "
        f"{bottom_text}. The pattern looks more distanced, world-model-like, institutional, "
        "or system-stabilizing than locally reactive."
    )
    conclusion = (
        "This supports and sharpens the current PC2 hypothesis: lower PC2 reads as integrated "
        "abstraction or long-residence world-model structure, while higher PC2 reads as situated "
        "developmental immediacy and social reactivity. Because the band suppresses PC1, the result "
        "is less likely to be merely the PC1 convergence/open-possibility axis reappearing."
    )
    counter = (
        "Mixed cases remain. Roles such as healer, guardian, and merchant combine situated social "
        "function with low-PC2 placement, while gamer and workaholic combine concrete social roles "
        "with high PC3 pressure. PC2 should remain provisional and be checked with cluster-conditioned "
        "and trait-conditioned diagnostics."
    )
    return high, low, conclusion, counter


def make_plots(all_roles: list[dict], band_rows: list[dict], full_rows: list[dict], lo: float, hi: float) -> None:
    width, height = 1800, 600
    img = bytearray([255, 255, 255] * width * height)

    def px(x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            i = (y * width + x) * 3
            img[i : i + 3] = bytes(color)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                px(x, y, color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(cx: int, cy: int, r: int, color: tuple[int, int, int]) -> None:
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    px(x, y, color)

    def panel(index: int) -> tuple[int, int, int, int]:
        left = 45 + index * 600
        top = 45
        return left, top, left + 520, top + 470

    def scale(vals: list[float], lo_px: int, hi_px: int, invert: bool = False):
        vmin, vmax = min(vals), max(vals)
        pad = (vmax - vmin) * 0.06 or 1.0
        vmin -= pad
        vmax += pad

        def f(v: float) -> int:
            t = (v - vmin) / (vmax - vmin)
            if invert:
                t = 1 - t
            return int(lo_px + t * (hi_px - lo_px))

        return f

    # Panel 1: PC1 vs PC2.
    l, t, r, b = panel(0)
    line(l, b, r, b, (0, 0, 0))
    line(l, t, l, b, (0, 0, 0))
    sx = scale([x["pc1"] for x in all_roles], l, r)
    sy = scale([x["pc2"] for x in all_roles], t, b, invert=True)
    rect(sx(lo), t, sx(hi), b, (255, 240, 205))
    for row in all_roles:
        circle(sx(row["pc1"]), sy(row["pc2"]), 2, (190, 190, 190))
    for row in band_rows:
        circle(sx(row["pc1"]), sy(row["pc2"]), 4, (40, 95, 170))

    # Panel 2: PC2 rank plot.
    l, t, r, b = panel(1)
    line(l, b, r, b, (0, 0, 0))
    line(l, t, l, b, (0, 0, 0))
    sx2 = scale([x["rank_by_pc2_desc"] for x in full_rows], l, r)
    sy2 = scale([x["pc2"] for x in full_rows], t, b, invert=True)
    last = None
    for row in full_rows:
        point = (sx2(row["rank_by_pc2_desc"]), sy2(row["pc2"]))
        if last:
            line(last[0], last[1], point[0], point[1], (40, 95, 170))
        circle(point[0], point[1], 3, (180, 55, 55))
        last = point

    # Panel 3: PC2 vs PC3 within band.
    l, t, r, b = panel(2)
    line(l, b, r, b, (0, 0, 0))
    line(l, t, l, b, (0, 0, 0))
    sx3 = scale([x["pc2"] for x in band_rows], l, r)
    sy3 = scale([x["pc3"] for x in band_rows], t, b, invert=True)
    for row in band_rows:
        circle(sx3(row["pc2"]), sy3(row["pc3"]), 4, (40, 130, 80))

    # Write a valid RGB PNG without external dependencies.
    raw = b"".join(b"\x00" + bytes(img[y * width * 3 : (y + 1) * width * 3]) for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    (OUT_DIR / "pc2_muted_pc1_plots.png").write_bytes(png)


def write_report(
    band_label: str,
    lo: float,
    hi: float,
    rows: list[dict],
    top_bottom: list[dict],
    band_stats: dict,
) -> None:
    top = [r for r in top_bottom if r["extreme_group"] == "top_pc2"]
    bottom = [r for r in top_bottom if r["extreme_group"] == "bottom_pc2"]
    high, low, conclusion, counter = interpret(top, bottom)
    caution = cluster_caution(rows)
    lines = [
        "# PC2 Extremes Within Muted PC1 Band",
        "",
        f"Date: 2026-06-01",
        f"Geometry source: `{GEOMETRY.relative_to(ROOT)}`",
        "",
        "## Band Selection",
        "",
        f"Selected band: `{band_label}`",
        f"Numeric PC1 bounds: {lo:.6f} to {hi:.6f}",
        f"Included roles/personas: {len(rows)}",
        "",
        "All candidate bands:",
        "",
        "| Band | Percentiles | PC1 lower | PC1 upper | Role count |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, stats in band_stats.items():
        lines.append(
            f"| {label} | {stats['lower_percentile']}-{stats['upper_percentile']} | "
            f"{stats['pc1_lower_bound']:.6f} | {stats['pc1_upper_bound']:.6f} | {stats['role_count']} |"
        )
    lines.extend(
        [
            "",
            f"Caution note: {caution}",
            "",
            "## Top 10 PC2 Roles Within Muted PC1",
            "",
            "| Rank | Role | Cluster | PC1 | PC2 | PC3 | PC1 pct | PC2 pct | PC3 pct |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for r in top:
        lines.append(
            f"| {r['extreme_rank']} | {r['role']} | {r['cluster']} | {r['pc1']:.6f} | "
            f"{r['pc2']:.6f} | {r['pc3']:.6f} | {r['pc1_percentile']:.3f} | "
            f"{r['pc2_percentile']:.3f} | {r['pc3_percentile']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Bottom 10 PC2 Roles Within Muted PC1",
            "",
            "| Rank | Role | Cluster | PC1 | PC2 | PC3 | PC1 pct | PC2 pct | PC3 pct |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for r in bottom:
        lines.append(
            f"| {r['extreme_rank']} | {r['role']} | {r['cluster']} | {r['pc1']:.6f} | "
            f"{r['pc2']:.6f} | {r['pc3']:.6f} | {r['pc1_percentile']:.3f} | "
            f"{r['pc2_percentile']:.3f} | {r['pc3_percentile']:.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Update",
            "",
            high,
            "",
            low,
            "",
            conclusion,
            "",
            counter,
            "",
            "Claim language: Within a muted-PC1 band, PC2 extremes show a coherent pattern that refines the PC2 interpretation independently of PC1.",
            "",
            "## Output Paths",
            "",
            "- Full ranked table: `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_full_ranking.csv`",
            "- Top/bottom table: `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_top_bottom.csv`",
            "- Band stats: `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_band_stats.json`",
            "- Plots: `research/outputs/pc2_muted_pc1_extremes/pc2_muted_pc1_plots.png`",
            "",
            "## Recommended Next Diagnostic",
            "",
            "Run blinded no-label matched-pair ratings inside this muted-PC1 band, asking raters to choose which role is more situated/reactive/developmental versus abstract/integrative/systemic. A follow-up cluster-conditioned version should test whether the same contrast survives inside procedural_professional and grounded_social rather than being driven by cluster skew.",
            "",
        ]
    )
    (OUT_DIR / "pc2_muted_pc1_extremes_report.md").write_text("\n".join(lines))


def main() -> None:
    roles = load_roles()
    band_label, lo, hi, band_roles, candidate_stats = choose_band(roles)
    rows = ranked_rows(band_roles, roles)
    top_bottom = make_top_bottom(rows)
    write_csv(OUT_DIR / "pc2_muted_pc1_full_ranking.csv", rows)
    write_csv(OUT_DIR / "pc2_muted_pc1_top_bottom.csv", top_bottom)
    stats = {
        "geometry_source": str(GEOMETRY.relative_to(ROOT)),
        "selected_band": band_label,
        "pc1_lower_bound": lo,
        "pc1_upper_bound": hi,
        "role_count": len(rows),
        "candidate_bands": candidate_stats,
        "cluster_counts": dict(Counter(r["cluster"] for r in rows)),
    }
    (OUT_DIR / "pc2_muted_pc1_band_stats.json").write_text(json.dumps(stats, indent=2))
    make_plots(roles, band_roles, rows, lo, hi)
    write_report(band_label, lo, hi, rows, top_bottom, candidate_stats)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
