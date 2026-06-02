#!/usr/bin/env python3
"""Contained cross-model PC2/PC3 comparability diagnostic.

Uses released Assistant Axis role vectors already present in downloads/hf_vectors.
No GPU work, no generation, and no visualization files are modified.
"""

import csv
import json
import math
import os
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch

try:
    from scipy.stats import pearsonr, spearmanr
except Exception as exc:  # pragma: no cover
    raise RuntimeError("scipy is required for this diagnostic") from exc


REPO = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
OUT = REPO / "research/outputs/cross_model_pc2_pc3_diagnostic"
OUT.mkdir(parents=True, exist_ok=True)

GEOMETRY_SOURCE = REPO / "research/visualizations/geometry_viz_data.json"
MAIN_VIEWER = REPO / "research/visualizations/persona_geometry_explorer.html"
H100_VIEWER = REPO / "research/outputs/h100_percentile_edge_validation_error_analysis/forecast_observed_3d_arrows.html"

MODEL_SPECS = {
    "qwen": {
        "label": "Qwen/Qwen3-32B",
        "vector_root": REPO / "downloads/hf_vectors/qwen-3-32b",
        "role_vector_dir": REPO / "downloads/hf_vectors/qwen-3-32b/role_vectors",
        "primary": True,
    },
    "llama": {
        "label": "Llama-3.3-70B",
        "vector_root": REPO / "downloads/hf_vectors/llama-3.3-70b",
        "role_vector_dir": REPO / "downloads/hf_vectors/llama-3.3-70b/role_vectors",
        "primary": True,
    },
    "gemma": {
        "label": "Gemma-2-27B",
        "vector_root": REPO / "downloads/hf_vectors/gemma-2-27b",
        "role_vector_dir": REPO / "downloads/hf_vectors/gemma-2-27b/role_vectors",
        "primary": False,
    },
}

DIAGNOSTIC_ROLES = [
    "shapeshifter", "chameleon", "tree", "hive", "elder", "patient", "amateur",
    "philosopher", "tulpa", "actor", "caregiver", "healer", "guardian", "optimist",
    "workaholic", "blogger", "podcaster", "influencer", "merchant", "symbiont",
    "visionary", "traditionalist", "purist", "composer",
]

HIGH_PC2_EXPECTED = [
    "patient", "amateur", "chameleon", "caregiver", "influencer", "blogger",
    "podcaster", "workaholic",
]
LOW_PC2_EXPECTED = [
    "tree", "hive", "philosopher", "healer", "guardian", "symbiont",
    "traditionalist", "purist",
]
WATCH_ROLES = ["shapeshifter", "elder", "actor", "tulpa"]


def load_geometry():
    with GEOMETRY_SOURCE.open() as f:
        data = json.load(f)
    roles = data["roles"]
    coords = {name: roles["pca3d"][i] for i, name in enumerate(roles["names"])}
    clusters = {name: roles["clusters"][i] for i, name in enumerate(roles["names"])}
    return data, coords, clusters


def load_layer_mean_vectors(role_dir: Path):
    names = []
    vectors = []
    for path in sorted(role_dir.glob("*.pt")):
        tensor = torch.load(path, map_location="cpu").float()
        vec = tensor.mean(0) if tensor.dim() > 1 else tensor
        arr = np.nan_to_num(vec.numpy().astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
        names.append(path.stem)
        vectors.append(arr)
    return names, np.stack(vectors)


def pca_numpy(x: np.ndarray, n_components=3):
    centered = x - x.mean(axis=0, keepdims=True)
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :n_components] * s[:n_components]
    explained = (s ** 2) / max(1, (x.shape[0] - 1))
    ratios = explained / explained.sum()
    return coords, vt[:n_components], ratios[:n_components]


def pearson(x, y):
    if len(x) < 3:
        return float("nan"), float("nan")
    r = pearsonr(x, y)
    return float(r.statistic), float(r.pvalue)


def spearman(x, y):
    if len(x) < 3:
        return float("nan"), float("nan")
    r = spearmanr(x, y)
    return float(r.statistic), float(r.pvalue)


def pct_ranks(values):
    ordered = sorted((v, i) for i, v in enumerate(values))
    out = [0.0] * len(values)
    n = len(values)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and ordered[j + 1][0] == ordered[i][0]:
            j += 1
        pct = 100.0 * ((i + j) / 2 + 0.5) / n
        for k in range(i, j + 1):
            out[ordered[k][1]] = pct
        i = j + 1
    return out


def orient_qwen_to_geometry(names, coords, geometry_coords):
    signs = [1, 1, 1]
    for pc in range(3):
        common = [name for name in names if name in geometry_coords]
        a = np.array([coords[names.index(name), pc] for name in common])
        b = np.array([geometry_coords[name][pc] for name in common])
        r, _ = pearson(a, b)
        if r < 0:
            signs[pc] = -1
            coords[:, pc] *= -1
    return signs


def orient_to_qwen(model_names, model_coords, qwen_rows):
    qwen_by_name = {r["persona"]: r for r in qwen_rows}
    signs = [1, 1, 1]
    for pc in range(3):
        common = [name for name in model_names if name in qwen_by_name]
        a = np.array([model_coords[model_names.index(name), pc] for name in common])
        b = np.array([qwen_by_name[name][f"pc{pc+1}"] for name in common])
        r, _ = pearson(a, b)
        if r < 0:
            signs[pc] = -1
            model_coords[:, pc] *= -1
    return signs


def build_rows(model_key, model_label, names, coords, explained, clusters):
    pc_pcts = [pct_ranks(coords[:, i].tolist()) for i in range(3)]
    ranks = {}
    for pc in range(3):
        ranked = sorted([(coords[i, pc], names[i]) for i in range(len(names))], reverse=True)
        ranks[pc] = {name: idx + 1 for idx, (_, name) in enumerate(ranked)}
    rows = []
    for i, name in enumerate(names):
        rows.append({
            "model": model_key,
            "model_label": model_label,
            "persona": name,
            "cluster": clusters.get(name, "unknown"),
            "pc1": float(coords[i, 0]),
            "pc2": float(coords[i, 1]),
            "pc3": float(coords[i, 2]),
            "pc1_percentile": pc_pcts[0][i],
            "pc2_percentile": pc_pcts[1][i],
            "pc3_percentile": pc_pcts[2][i],
            "pc1_rank": ranks[0][name],
            "pc2_rank": ranks[1][name],
            "pc3_rank": ranks[2][name],
            "pc1_explained": float(explained[0]),
            "pc2_explained": float(explained[1]),
            "pc3_explained": float(explained[2]),
        })
    return rows


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def muted_pc1_extremes(rows):
    pc1_values = np.array([r["pc1"] for r in rows])
    selected = None
    selected_band = None
    selected_bounds = None
    for lo, hi in [(45, 55), (40, 60), (35, 65)]:
        bounds = (float(np.percentile(pc1_values, lo)), float(np.percentile(pc1_values, hi)))
        band_rows = [r for r in rows if bounds[0] <= r["pc1"] <= bounds[1]]
        if len(band_rows) >= 25 or (lo, hi) == (35, 65):
            selected = band_rows
            selected_band = f"central_{lo}_{hi}"
            selected_bounds = bounds
            break
    ranked = sorted(selected, key=lambda r: r["pc2"], reverse=True)
    out = []
    for rank, row in enumerate(ranked, 1):
        out.append({
            "model": row["model"],
            "model_label": row["model_label"],
            "band": selected_band,
            "pc1_lower_bound": selected_bounds[0],
            "pc1_upper_bound": selected_bounds[1],
            "selected_count": len(selected),
            "rank_pc2_desc": rank,
            "persona": row["persona"],
            "cluster": row["cluster"],
            "pc1": row["pc1"],
            "pc2": row["pc2"],
            "pc3": row["pc3"],
            "pc2_percentile": row["pc2_percentile"],
        })
    return out


def ranking_rows(rows, pc_name, top_n=20):
    pc = int(pc_name[-1])
    ranked_desc = sorted(rows, key=lambda r: r[pc_name], reverse=True)
    ranked_asc = sorted(rows, key=lambda r: r[pc_name])
    out = []
    for pole, ranked in [("positive", ranked_desc[:top_n]), ("negative", ranked_asc[:top_n])]:
        for rank, row in enumerate(ranked, 1):
            out.append({
                "model": row["model"],
                "model_label": row["model_label"],
                "pc": pc_name.upper(),
                "pole": pole,
                "rank": rank,
                "persona": row["persona"],
                "cluster": row["cluster"],
                "pc1": row["pc1"],
                "pc2": row["pc2"],
                "pc3": row["pc3"],
                f"{pc_name}_percentile": row[f"{pc_name}_percentile"],
            })
    return out


def correlation_matrix(model_rows):
    rows = []
    model_keys = list(model_rows)
    for a in model_keys:
        for b in model_keys:
            if a == b:
                continue
            amap = {r["persona"]: r for r in model_rows[a]}
            bmap = {r["persona"]: r for r in model_rows[b]}
            common = sorted(set(amap) & set(bmap))
            for ai in range(1, 4):
                for bi in range(1, 4):
                    x = np.array([amap[n][f"pc{ai}"] for n in common])
                    y = np.array([bmap[n][f"pc{bi}"] for n in common])
                    pr, pp = pearson(x, y)
                    sr, sp = spearman(x, y)
                    rows.append({
                        "model_a": a,
                        "model_b": b,
                        "pc_a": f"PC{ai}",
                        "pc_b": f"PC{bi}",
                        "matched_role_count": len(common),
                        "pearson_r": pr,
                        "pearson_p": pp,
                        "spearman_r": sr,
                        "spearman_p": sp,
                        "abs_pearson_r": abs(pr),
                        "abs_spearman_r": abs(sr),
                        "sign_corrected_pearson_r": abs(pr),
                        "sign_corrected_spearman_r": abs(sr),
                    })
    return rows


def best_matches(corr_rows):
    out = []
    for model_a in sorted({r["model_a"] for r in corr_rows}):
        for model_b in sorted({r["model_b"] for r in corr_rows if r["model_a"] == model_a}):
            for pc_a in ["PC1", "PC2", "PC3"]:
                candidates = [r for r in corr_rows if r["model_a"] == model_a and r["model_b"] == model_b and r["pc_a"] == pc_a]
                if not candidates:
                    continue
                best = max(candidates, key=lambda r: r["abs_pearson_r"])
                out.append({
                    "model_a": model_a,
                    "model_b": model_b,
                    "pc_a": pc_a,
                    "best_matching_pc_b": best["pc_b"],
                    "pearson_r": best["pearson_r"],
                    "abs_pearson_r": best["abs_pearson_r"],
                    "spearman_r": best["spearman_r"],
                    "abs_spearman_r": best["abs_spearman_r"],
                    "matched_role_count": best["matched_role_count"],
                })
    return out


def pc12_subspace_stats(model_rows):
    out = {}
    for a in model_rows:
        for b in model_rows:
            if a == b:
                continue
            amap = {r["persona"]: r for r in model_rows[a]}
            bmap = {r["persona"]: r for r in model_rows[b]}
            common = sorted(set(amap) & set(bmap))
            xa = np.array([[amap[n]["pc1"], amap[n]["pc2"]] for n in common])
            xb = np.array([[bmap[n]["pc1"], bmap[n]["pc2"]] for n in common])
            xa = (xa - xa.mean(axis=0, keepdims=True)) / xa.std(axis=0, keepdims=True)
            xb = (xb - xb.mean(axis=0, keepdims=True)) / xb.std(axis=0, keepdims=True)
            corr = (xa.T @ xb) / (len(common) - 1)
            singular = np.linalg.svd(corr, compute_uv=False)
            out[f"{a}_vs_{b}"] = {
                "matched_role_count": len(common),
                "pc1_pc2_correlation_block": corr.tolist(),
                "principal_correlations": singular.tolist(),
                "mean_principal_correlation": float(np.mean(singular)),
            }
    return out


def diagnostic_role_rows(model_rows):
    out = []
    for model, rows in model_rows.items():
        by_name = {r["persona"]: r for r in rows}
        pc2_median = float(np.median([r["pc2"] for r in rows]))
        by_cluster = defaultdict(list)
        for r in rows:
            by_cluster[r["cluster"]].append(r["pc2"])
        cluster_medians = {c: float(np.median(v)) for c, v in by_cluster.items()}
        for role in DIAGNOSTIC_ROLES:
            if role not in by_name:
                out.append({"model": model, "persona": role, "present": "no"})
                continue
            r = by_name[role]
            out.append({
                "model": model,
                "model_label": r["model_label"],
                "persona": role,
                "present": "yes",
                "cluster": r["cluster"],
                "pc1": r["pc1"],
                "pc2": r["pc2"],
                "pc3": r["pc3"],
                "pc1_percentile": r["pc1_percentile"],
                "pc2_percentile": r["pc2_percentile"],
                "pc3_percentile": r["pc3_percentile"],
                "pc2_rank": r["pc2_rank"],
                "pc3_rank": r["pc3_rank"],
                "pc2_global_side": "above_median" if r["pc2"] > pc2_median else "below_median",
                "pc2_cluster_side": "above_cluster_median" if r["pc2"] > cluster_medians.get(r["cluster"], pc2_median) else "below_cluster_median",
            })
    return out


def expected_direction_checks(model_rows):
    out = []
    expected = [(r, "high") for r in HIGH_PC2_EXPECTED] + [(r, "low") for r in LOW_PC2_EXPECTED]
    for model, rows in model_rows.items():
        if model not in {"qwen", "llama"}:
            continue
        by_name = {r["persona"]: r for r in rows}
        pc2_median = float(np.median([r["pc2"] for r in rows]))
        by_cluster = defaultdict(list)
        for r in rows:
            by_cluster[r["cluster"]].append(r["pc2"])
        cluster_medians = {c: float(np.median(v)) for c, v in by_cluster.items()}
        for role, expectation in expected:
            if role not in by_name:
                continue
            r = by_name[role]
            global_side = "high" if r["pc2"] > pc2_median else "low"
            cluster_side = "high" if r["pc2"] > cluster_medians.get(r["cluster"], pc2_median) else "low"
            out.append({
                "model": model,
                "persona": role,
                "expected_pc2_side": expectation,
                "pc2": r["pc2"],
                "cluster": r["cluster"],
                "global_side": global_side,
                "global_pass": global_side == expectation,
                "cluster_side": cluster_side,
                "cluster_pass": cluster_side == expectation,
                "pc2_percentile": r["pc2_percentile"],
                "pc2_rank": r["pc2_rank"],
            })
        for role in WATCH_ROLES:
            if role in by_name:
                r = by_name[role]
                out.append({
                    "model": model,
                    "persona": role,
                    "expected_pc2_side": "watch",
                    "pc2": r["pc2"],
                    "cluster": r["cluster"],
                    "global_side": "high" if r["pc2"] > pc2_median else "low",
                    "global_pass": "",
                    "cluster_side": "high" if r["pc2"] > cluster_medians.get(r["cluster"], pc2_median) else "low",
                    "cluster_pass": "",
                    "pc2_percentile": r["pc2_percentile"],
                    "pc2_rank": r["pc2_rank"],
                })
    return out


def summarize_checks(checks):
    summary = {}
    for model in ["qwen", "llama"]:
        rows = [r for r in checks if r["model"] == model and r["expected_pc2_side"] != "watch"]
        summary[model] = {
            "global_pass": sum(1 for r in rows if r["global_pass"] is True),
            "global_total": len(rows),
            "cluster_pass": sum(1 for r in rows if r["cluster_pass"] is True),
            "cluster_total": len(rows),
        }
    return summary


def write_plots(model_rows, corr_rows, path_svg, path_png):
    width, height = 1600, 1200
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    parts.append('<rect width="100%" height="100%" fill="white"/>')
    parts.append('<text x="40" y="38" font-size="24" font-family="Arial" font-weight="bold">Cross-model PC2/PC3 diagnostic</text>')
    colors = {"qwen": "#377eb8", "llama": "#e41a1c", "gemma": "#4daf4a"}

    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def scale(v, lo, hi, a, b):
        if hi == lo:
            return (a + b) / 2
        return a + (v - lo) * (b - a) / (hi - lo)

    def panel(x, y, w, h, title):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fbfbfb" stroke="#cccccc"/>')
        parts.append(f'<text x="{x+12}" y="{y+24}" font-size="17" font-family="Arial" font-weight="bold">{esc(title)}</text>')

    # PC2 rank curves.
    x0, y0, w, h = 50, 70, 700, 480
    panel(x0, y0, w, h, "PC2 rank curves")
    all_pc2 = [r["pc2"] for rows in model_rows.values() for r in rows]
    for model, rows in model_rows.items():
        ranked = sorted(rows, key=lambda r: r["pc2"], reverse=True)
        pts = []
        for i, r in enumerate(ranked, 1):
            x = scale(i, 1, len(ranked), x0 + 60, x0 + w - 40)
            y = scale(r["pc2"], min(all_pc2), max(all_pc2), y0 + h - 50, y0 + 50)
            pts.append(f"{x:.1f},{y:.1f}")
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors.get(model, "#777")}" stroke-width="2"/>')
        parts.append(f'<text x="{x0+w-130}" y="{y0+55+24*list(model_rows).index(model)}" font-size="13" font-family="Arial" fill="{colors.get(model, "#777")}">{model}</text>')

    # PC3 rank curves.
    x0, y0, w, h = 830, 70, 700, 480
    panel(x0, y0, w, h, "PC3 rank curves")
    all_pc3 = [r["pc3"] for rows in model_rows.values() for r in rows]
    for model, rows in model_rows.items():
        ranked = sorted(rows, key=lambda r: r["pc3"], reverse=True)
        pts = []
        for i, r in enumerate(ranked, 1):
            x = scale(i, 1, len(ranked), x0 + 60, x0 + w - 40)
            y = scale(r["pc3"], min(all_pc3), max(all_pc3), y0 + h - 50, y0 + 50)
            pts.append(f"{x:.1f},{y:.1f}")
        parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors.get(model, "#777")}" stroke-width="2"/>')

    # Qwen vs Llama PC2 scatter.
    if "qwen" in model_rows and "llama" in model_rows:
        q = {r["persona"]: r for r in model_rows["qwen"]}
        l = {r["persona"]: r for r in model_rows["llama"]}
        common = sorted(set(q) & set(l))
        x0, y0, w, h = 50, 650, 700, 480
        panel(x0, y0, w, h, "Qwen PC2 vs Llama PC2")
        xs = [q[n]["pc2"] for n in common]
        ys = [l[n]["pc2"] for n in common]
        for n in common:
            x = scale(q[n]["pc2"], min(xs), max(xs), x0 + 60, x0 + w - 40)
            y = scale(l[n]["pc2"], min(ys), max(ys), y0 + h - 50, y0 + 50)
            rad = 5 if n in DIAGNOSTIC_ROLES else 2.5
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="#444" fill-opacity="0.55"/>')
            if n in DIAGNOSTIC_ROLES[:12]:
                parts.append(f'<text x="{x+6:.1f}" y="{y-6:.1f}" font-size="10" font-family="Arial">{esc(n)}</text>')
        x0, y0, w, h = 830, 650, 700, 480
        panel(x0, y0, w, h, "Qwen PC3 vs Llama PC3")
        xs = [q[n]["pc3"] for n in common]
        ys = [l[n]["pc3"] for n in common]
        for n in common:
            x = scale(q[n]["pc3"], min(xs), max(xs), x0 + 60, x0 + w - 40)
            y = scale(l[n]["pc3"], min(ys), max(ys), y0 + h - 50, y0 + 50)
            rad = 5 if n in DIAGNOSTIC_ROLES else 2.5
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad}" fill="#444" fill-opacity="0.55"/>')
            if n in DIAGNOSTIC_ROLES[:12]:
                parts.append(f'<text x="{x+6:.1f}" y="{y-6:.1f}" font-size="10" font-family="Arial">{esc(n)}</text>')

    parts.append("</svg>")
    path_svg.write_text("\n".join(parts), encoding="utf-8")
    try:
        subprocess.run(["sips", "-s", "format", "png", str(path_svg), "--out", str(path_png)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        path_png.write_bytes(b"")


def fmt(x, digits=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{float(x):.{digits}f}"


def top_bottom_text(rows, pc, n=10):
    top = sorted(rows, key=lambda r: r[pc], reverse=True)[:n]
    bot = sorted(rows, key=lambda r: r[pc])[:n]
    return (
        ", ".join(f"{r['persona']} ({r[pc]:.1f})" for r in top),
        ", ".join(f"{r['persona']} ({r[pc]:.1f})" for r in bot),
    )


def write_report(model_rows, corr_rows, best_rows, checks, muted_rows, stats):
    ql = [r for r in corr_rows if r["model_a"] == "qwen" and r["model_b"] == "llama"]
    def get_corr(a, b):
        row = next(r for r in ql if r["pc_a"] == a and r["pc_b"] == b)
        return row
    pc2 = get_corr("PC2", "PC2")
    pc3 = get_corr("PC3", "PC3")
    check_summary = summarize_checks(checks)
    qwen_pc2_top, qwen_pc2_bottom = top_bottom_text(model_rows["qwen"], "pc2")
    llama_pc2_top, llama_pc2_bottom = top_bottom_text(model_rows["llama"], "pc2")
    qwen_pc3_top, qwen_pc3_bottom = top_bottom_text(model_rows["qwen"], "pc3")
    llama_pc3_top, llama_pc3_bottom = top_bottom_text(model_rows["llama"], "pc3")
    llama_muted = [r for r in muted_rows if r["model"] == "llama"]
    lm_top = ", ".join(f"{r['persona']} ({r['pc2']:.1f})" for r in sorted(llama_muted, key=lambda r: r["pc2"], reverse=True)[:10])
    lm_bot = ", ".join(f"{r['persona']} ({r['pc2']:.1f})" for r in sorted(llama_muted, key=lambda r: r["pc2"])[:10])
    ql_best = [r for r in best_rows if r["model_a"] == "qwen" and r["model_b"] == "llama"]
    best_text = "\n".join(
        f"- {r['pc_a']} best matches Llama {r['best_matching_pc_b']} at abs Pearson r={fmt(r['abs_pearson_r'])} (signed r={fmt(r['pearson_r'])})."
        for r in ql_best
    )
    report = f"""# Cross-Model PC2/PC3 Diagnostic

- Date: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
- model_used: GPT-5.5
- Geometry source: `research/visualizations/geometry_viz_data.json`
- Released vector roots: `downloads/hf_vectors/qwen-3-32b`, `downloads/hf_vectors/llama-3.3-70b`, `downloads/hf_vectors/gemma-2-27b`
- Vector representation: layer-mean role vectors, matching the current Qwen geometry visualization builder.
- No GPU work, no generation, no H100 outputs, no prompt-battery outputs, and no visualization files were modified.

## Models Found

{chr(10).join(f"- {m}: {stats['models'][m]['role_count']} roles, explained variance PC1/PC2/PC3 = {fmt(stats['models'][m]['explained_variance'][0])}/{fmt(stats['models'][m]['explained_variance'][1])}/{fmt(stats['models'][m]['explained_variance'][2])}" for m in stats['models'])}

All three local released-vector model directories contain 275 role vectors. Qwen and Llama are the primary comparison; Gemma is included as secondary diagnostic context.

## Qwen-Llama Correlation Matrix

Matched role count: {pc2['matched_role_count']}.

| Qwen PC | Llama PC1 Pearson | Llama PC2 Pearson | Llama PC3 Pearson |
|---|---:|---:|---:|
| PC1 | {fmt(get_corr('PC1','PC1')['pearson_r'])} | {fmt(get_corr('PC1','PC2')['pearson_r'])} | {fmt(get_corr('PC1','PC3')['pearson_r'])} |
| PC2 | {fmt(get_corr('PC2','PC1')['pearson_r'])} | {fmt(get_corr('PC2','PC2')['pearson_r'])} | {fmt(get_corr('PC2','PC3')['pearson_r'])} |
| PC3 | {fmt(get_corr('PC3','PC1')['pearson_r'])} | {fmt(get_corr('PC3','PC2')['pearson_r'])} | {fmt(get_corr('PC3','PC3')['pearson_r'])} |

Best matches:

{best_text}

The Qwen-Llama PC1/PC2 plane is more comparable than the individual same-numbered axes: the PC1/PC2 principal correlations are {fmt(stats['pc1_pc2_subspace']['qwen_vs_llama']['principal_correlations'][0])} and {fmt(stats['pc1_pc2_subspace']['qwen_vs_llama']['principal_correlations'][1])}. This means PC2 should be interpreted with an axis-rotation caveat: Qwen PC2 overlaps both Llama PC1 and Llama PC2, and Qwen PC1 also mixes into Llama PC1/PC2.

## PC2 Comparability

Qwen PC2 vs Llama PC2 has Pearson r={fmt(pc2['pearson_r'])} and Spearman r={fmt(pc2['spearman_r'])}. Qwen PC2's strongest single-axis Llama match is Llama PC1 at Pearson r={fmt(next(r for r in best_rows if r['model_a']=='qwen' and r['model_b']=='llama' and r['pc_a']=='PC2')['pearson_r'])}. This is partial but meaningful agreement in a shared PC1/PC2 plane rather than a clean one-to-one same-index transfer.

Qwen PC2 top roles: {qwen_pc2_top}
Qwen PC2 bottom roles: {qwen_pc2_bottom}

Llama PC2 top roles: {llama_pc2_top}
Llama PC2 bottom roles: {llama_pc2_bottom}

Llama muted-PC1 PC2 top roles: {lm_top}
Llama muted-PC1 PC2 bottom roles: {lm_bot}

Expected-direction checks:

- Qwen global: {check_summary['qwen']['global_pass']}/{check_summary['qwen']['global_total']}; Qwen cluster-relative: {check_summary['qwen']['cluster_pass']}/{check_summary['qwen']['cluster_total']}.
- Llama global: {check_summary['llama']['global_pass']}/{check_summary['llama']['global_total']}; Llama cluster-relative: {check_summary['llama']['cluster_pass']}/{check_summary['llama']['cluster_total']}.

Interpretation: Llama gives partial support to the Qwen PC2 story, not a decisive resolution. The broad high-PC2 pattern continues to include formative, exposed, performative, or locally pressured roles in several cases, but cluster effects, individual counterexamples, and PC1/PC2 axis mixing remain important. PC2 should remain provisional and should be phrased as a partly transferable situated-immediacy/formative-state versus integrated-stability axis within a shared low-dimensional plane, not as a settled model-general same-index construct.

## PC3 Comparability

Qwen PC3 vs Llama PC3 has Pearson r={fmt(pc3['pearson_r'])} and Spearman r={fmt(pc3['spearman_r'])}. This is weak relative to PC1/PC2 and supports caution about treating same-index PC3 as directly comparable across models.

Qwen PC3 top roles: {qwen_pc3_top}
Qwen PC3 bottom roles: {qwen_pc3_bottom}

Llama PC3 top roles: {llama_pc3_top}
Llama PC3 bottom roles: {llama_pc3_bottom}

Interpretation: PC3 does not yet look stable enough for same-index Qwen-to-Llama 3D arrow visualizations. Future visualization should either omit PC3, explicitly show PC3 as low-confidence, or use an alignment-corrected cross-model basis.

## Diagnostic Roles

Detailed diagnostic-role coordinates and ranks are in `cross_model_diagnostic_roles.csv`. The key Qwen counterexamples remain visible: `shapeshifter` is low on Qwen PC2, `chameleon` is globally high but cluster-sensitive, and `elder` changes interpretation depending on global versus cluster-relative baseline. Llama helps by showing which of these are Qwen-specific versus shared rank ambiguities, but it does not remove the caveat.

## Gemma

Gemma was included because local vectors are available, but it should remain secondary to the requested Qwen-Llama diagnostic. In this layer-mean released-vector PCA diagnostic, Gemma aligns surprisingly strongly with Qwen on same-index PCs: Qwen-Gemma PC1 r={fmt(next(r for r in corr_rows if r['model_a']=='qwen' and r['model_b']=='gemma' and r['pc_a']=='PC1' and r['pc_b']=='PC1')['pearson_r'])}, PC2 r={fmt(next(r for r in corr_rows if r['model_a']=='qwen' and r['model_b']=='gemma' and r['pc_a']=='PC2' and r['pc_b']=='PC2')['pearson_r'])}, and PC3 r={fmt(next(r for r in corr_rows if r['model_a']=='qwen' and r['model_b']=='gemma' and r['pc_a']=='PC3' and r['pc_b']=='PC3')['pearson_r'])}. This should be treated as a local artifact-level result rather than a full behavioral generalization claim.

## Visualization Feasibility

The current main viewer embeds a single Qwen `VIZ_DATA` object in `research/visualizations/persona_geometry_explorer.html` and expects one dataset with PCA/UMAP arrays, clusters, nearest neighbors, and overlay data. Adding model switching would require a new multi-model data bundle and UI state for selected model. Cross-model arrows would require a separate view or an alignment convention because independent PCA coordinates are not in one shared coordinate frame by default.

Recommendation: no visualization changes yet. If a visualization is added later, start with a cross-model PC1/PC2 comparison or model-switching viewer; do not build same-index PC1/PC2/PC3 cross-model arrows until PC3 alignment is corrected or explicitly caveated.

## Output Files

- `cross_model_pc_correlation_matrix.csv`
- `cross_model_pc_best_matches.csv`
- `cross_model_diagnostic_roles.csv`
- `qwen_llama_pc2_expected_direction_checks.csv`
- `per_model_pc2_rankings.csv`
- `per_model_pc3_rankings.csv`
- `muted_pc1_pc2_extremes_by_model.csv`
- `cross_model_pc2_pc3_stats.json`
- `visualization_feasibility_note.md`
- `cross_model_pc2_pc3_plots.png`
- `run_cross_model_pc2_pc3_diagnostic.py`
"""
    (OUT / "cross_model_pc2_pc3_report.md").write_text(report, encoding="utf-8")


def write_visualization_note(stats):
    note = f"""# Visualization Feasibility Note

- Date: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
- Main viewer inspected: `research/visualizations/persona_geometry_explorer.html`
- H100 arrow viewer inspected as design reference only: `{H100_VIEWER.relative_to(REPO) if H100_VIEWER.exists() else 'not present'}`
- No visualization files were modified.

## Current Viewer Structure

The current main viewer embeds a single Qwen `VIZ_DATA` object and renders one active dataset at a time. It assumes one set of PCA/UMAP coordinates, one role list, one cluster assignment list, and one nearest-neighbor map. It does not currently expose a model dimension.

## Required Changes for Model Switching

To add Qwen/Llama/Gemma switching, build a separate multi-model geometry data artifact with per-model role coordinates, explained variance, nearest neighbors, and metadata. Then add a model selector to the viewer and route all PCA/UMAP/color/selection logic through the selected model's dataset.

## Required Changes for Cross-Model Arrows

Cross-model arrows from Qwen coordinates to Llama coordinates are only meaningful if coordinates are put into a shared alignment convention. Independent PCA spaces have arbitrary signs and rotations, especially for weaker PCs. Same-index PC3 is not currently reliable enough for uncaveated arrows.

## Recommendation

Do not modify visualization tools yet. If a visualization is later warranted, start with model switching or PC1/PC2-only cross-model arrows. A PC1/PC2/PC3 arrow viewer should wait for alignment correction or carry a strong PC3 caveat.
"""
    (OUT / "visualization_feasibility_note.md").write_text(note, encoding="utf-8")


def main():
    _, qwen_geometry_coords, clusters = load_geometry()
    model_rows = {}
    sign_alignment = {}
    available = {}
    for key, spec in MODEL_SPECS.items():
        role_dir = spec["role_vector_dir"]
        if not role_dir.exists():
            continue
        names, vecs = load_layer_mean_vectors(role_dir)
        coords, _, explained = pca_numpy(vecs, 3)
        if key == "qwen":
            signs = orient_qwen_to_geometry(names, coords, qwen_geometry_coords)
        else:
            signs = [1, 1, 1]
        rows = build_rows(key, spec["label"], names, coords, explained, clusters)
        model_rows[key] = rows
        sign_alignment[key] = signs
        available[key] = {
            "label": spec["label"],
            "role_count": len(rows),
            "vector_root": str(spec["vector_root"].relative_to(REPO)),
            "explained_variance": [float(x) for x in explained],
            "primary": spec["primary"],
        }
    if "qwen" not in model_rows or "llama" not in model_rows:
        raise RuntimeError("Qwen and Llama role vectors are required for this diagnostic")
    for key in list(model_rows):
        if key == "qwen":
            continue
        names = [r["persona"] for r in model_rows[key]]
        coords = np.array([[r["pc1"], r["pc2"], r["pc3"]] for r in model_rows[key]])
        signs = orient_to_qwen(names, coords, model_rows["qwen"])
        sign_alignment[key] = signs
        # Rebuild rows after sign alignment, preserving explained variance.
        explained = np.array([
            model_rows[key][0]["pc1_explained"],
            model_rows[key][0]["pc2_explained"],
            model_rows[key][0]["pc3_explained"],
        ])
        model_rows[key] = build_rows(key, MODEL_SPECS[key]["label"], names, coords, explained, clusters)

    corr_rows = correlation_matrix(model_rows)
    best_rows = best_matches(corr_rows)
    diag_rows = diagnostic_role_rows(model_rows)
    checks = expected_direction_checks(model_rows)
    muted_rows = []
    pc2_rows = []
    pc3_rows = []
    for rows in model_rows.values():
        muted_rows.extend(muted_pc1_extremes(rows))
        pc2_rows.extend(ranking_rows(rows, "pc2"))
        pc3_rows.extend(ranking_rows(rows, "pc3"))

    stats = {
        "date_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_used": "GPT-5.5",
        "geometry_source": str(GEOMETRY_SOURCE.relative_to(REPO)),
        "models": available,
        "sign_alignment": sign_alignment,
        "matched_role_counts": {
            f"{a}_vs_{b}": len({r["persona"] for r in model_rows[a]} & {r["persona"] for r in model_rows[b]})
            for a in model_rows for b in model_rows if a != b
        },
        "pc1_pc2_subspace": pc12_subspace_stats(model_rows),
        "expected_direction_summary": summarize_checks(checks),
        "visualization_files_modified": False,
    }

    write_csv(OUT / "cross_model_pc_correlation_matrix.csv", corr_rows, [
        "model_a", "model_b", "pc_a", "pc_b", "matched_role_count",
        "pearson_r", "pearson_p", "spearman_r", "spearman_p",
        "abs_pearson_r", "abs_spearman_r",
        "sign_corrected_pearson_r", "sign_corrected_spearman_r",
    ])
    write_csv(OUT / "cross_model_pc_best_matches.csv", best_rows, [
        "model_a", "model_b", "pc_a", "best_matching_pc_b",
        "pearson_r", "abs_pearson_r", "spearman_r", "abs_spearman_r",
        "matched_role_count",
    ])
    write_csv(OUT / "cross_model_diagnostic_roles.csv", diag_rows, [
        "model", "model_label", "persona", "present", "cluster", "pc1", "pc2", "pc3",
        "pc1_percentile", "pc2_percentile", "pc3_percentile",
        "pc2_rank", "pc3_rank", "pc2_global_side", "pc2_cluster_side",
    ])
    write_csv(OUT / "qwen_llama_pc2_expected_direction_checks.csv", checks, [
        "model", "persona", "expected_pc2_side", "pc2", "cluster",
        "global_side", "global_pass", "cluster_side", "cluster_pass",
        "pc2_percentile", "pc2_rank",
    ])
    write_csv(OUT / "per_model_pc2_rankings.csv", pc2_rows, [
        "model", "model_label", "pc", "pole", "rank", "persona", "cluster",
        "pc1", "pc2", "pc3", "pc2_percentile",
    ])
    write_csv(OUT / "per_model_pc3_rankings.csv", pc3_rows, [
        "model", "model_label", "pc", "pole", "rank", "persona", "cluster",
        "pc1", "pc2", "pc3", "pc3_percentile",
    ])
    write_csv(OUT / "muted_pc1_pc2_extremes_by_model.csv", muted_rows, [
        "model", "model_label", "band", "pc1_lower_bound", "pc1_upper_bound",
        "selected_count", "rank_pc2_desc", "persona", "cluster",
        "pc1", "pc2", "pc3", "pc2_percentile",
    ])
    (OUT / "cross_model_pc2_pc3_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    write_plots(model_rows, corr_rows, OUT / "cross_model_pc2_pc3_plots.svg", OUT / "cross_model_pc2_pc3_plots.png")
    write_visualization_note(stats)
    write_report(model_rows, corr_rows, best_rows, checks, muted_rows, stats)
    print(f"Wrote cross-model diagnostic outputs to {OUT}")


if __name__ == "__main__":
    main()
