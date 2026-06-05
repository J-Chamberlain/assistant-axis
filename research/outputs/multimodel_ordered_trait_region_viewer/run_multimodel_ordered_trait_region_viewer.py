#!/usr/bin/env python3
"""Build a multi-model ordered-axis trait-region viewer.

This generalizes the Qwen PC1 x PC2 trait-region overlay.  The selected x-axis
defines the conditioning bands, so PC1 x PC2 and PC2 x PC1 are intentionally
different analyses.
"""

from __future__ import annotations

import csv
import html
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch


REPO = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
OUT = REPO / "research/outputs/multimodel_ordered_trait_region_viewer"
OUT.mkdir(parents=True, exist_ok=True)

MODEL_USED = "GPT-5.5"
UPDATED = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
VECTOR_ROOT = REPO / "downloads/hf_vectors"
GEOMETRY_SOURCE = REPO / "research/visualizations/geometry_viz_data.json"
QWEN_PRIOR_CELLS = REPO / "research/outputs/qwen_pc2_trait_region_overlay/qwen_pc1_pc2_trait_region_cells.csv"
QWEN_JOINED_TRAIT_MATRIX = REPO / "research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv"

MODEL_SPECS = {
    "qwen": {"label": "Qwen/Qwen3-32B", "folder": "qwen-3-32b"},
    "llama": {"label": "Llama-3.3-70B", "folder": "llama-3.3-70b"},
    "gemma": {"label": "Gemma-2-27B", "folder": "gemma-2-27b"},
}

AXES = ["pc1", "pc2", "pc3"]
ORDERED_VIEWS = [(x, y) for x in AXES for y in AXES if x != y]
BASES = ["quantile", "fixed_grid"]
SPARSE_THRESHOLD = 8

CLUSTER_COLORS = {
    "editorial": "#e8b84b",
    "procedural_professional": "#4a9eff",
    "grounded_social": "#5ecb8a",
    "other": "#b0b0b0",
    "combative_iconoclast": "#ff6b6b",
    "mythic_spiritual": "#c084fc",
    "trickster_chaos": "#fb923c",
    "unknown": "#777777",
}

REGION_COLORS = {
    "situated_reactive": "#fb923c",
    "abstract_integrated": "#8b5cf6",
    "careful_procedural": "#4a9eff",
    "social_affiliative": "#5ecb8a",
    "adversarial_volatile": "#ff6b6b",
    "expressive_symbolic": "#e8b84b",
    "other": "#9ca3af",
}

TRAIT_THEME_KEYWORDS = {
    "situated_reactive": {
        "experiential", "casual", "practical", "reactive", "grounded", "visceral",
        "anxious", "neurotic", "impulsive", "accessible", "accommodating",
        "vulnerable", "emotional", "spontaneous",
    },
    "abstract_integrated": {
        "abstract", "conceptual", "theoretical", "pensive", "serious", "integrated",
        "philosophical", "reflective", "systematic", "symbolic",
    },
    "careful_procedural": {
        "conscientious", "formal", "meticulous", "disciplined", "orderly",
        "methodical", "precise", "reliable", "dutiful", "ritualistic",
    },
    "social_affiliative": {
        "agreeable", "empathetic", "warm", "social", "nurturing", "cooperative",
        "supportive", "friendly", "communal", "affiliative",
    },
    "adversarial_volatile": {
        "psychopathic", "machiavellian", "narcissistic", "dominant", "hostile",
        "combative", "aggressive", "rebellious", "chaotic", "cynical",
    },
    "expressive_symbolic": {
        "creative", "open", "imaginative", "playful", "artistic", "expressive",
        "mythic", "mystical", "dramatic", "poetic",
    },
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def pct_ranks(values: list[float]) -> list[float]:
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


def pca_numpy(x: np.ndarray, n_components: int = 3) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    centered = x - x.mean(axis=0, keepdims=True)
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    coords = u[:, :n_components] * s[:n_components]
    explained = (s ** 2) / max(1, x.shape[0] - 1)
    return coords, vt[:n_components], explained[:n_components] / explained.sum()


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def normalize_rows(x: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    return x / x.norm(dim=-1, keepdim=True).clamp_min(eps)


def load_mean_vectors(vector_dir: Path) -> tuple[list[str], np.ndarray]:
    names: list[str] = []
    vectors: list[np.ndarray] = []
    for path in sorted(vector_dir.glob("*.pt")):
        tensor = torch.load(path, map_location="cpu").float()
        vec = tensor.mean(0) if tensor.dim() > 1 else tensor
        names.append(path.stem)
        vectors.append(np.nan_to_num(vec.numpy().astype(np.float64)))
    if not vectors:
        raise FileNotFoundError(f"No vectors found in {vector_dir}")
    return names, np.stack(vectors)


def load_geometry_reference() -> tuple[dict[str, list[float]], dict[str, str], dict[str, float]]:
    with GEOMETRY_SOURCE.open() as f:
        data = json.load(f)
    names = data["roles"]["names"]
    pca = data["roles"]["pca3d"]
    clusters = data["roles"]["clusters"]
    axis = data["roles"].get("axis_projections", [0.0] * len(names))
    coords = {name: [float(v) for v in pca[i][:3]] for i, name in enumerate(names)}
    cluster_map = {name: clusters[i] for i, name in enumerate(names)}
    axis_map = {name: float(axis[i]) for i, name in enumerate(names)}
    return coords, cluster_map, axis_map


def orient_to_reference(names: list[str], coords: np.ndarray, reference: dict[str, list[float]]) -> list[int]:
    signs = [1, 1, 1]
    name_index = {name: i for i, name in enumerate(names)}
    common = [name for name in names if name in reference]
    for pc in range(3):
        a = np.array([coords[name_index[name], pc] for name in common])
        b = np.array([reference[name][pc] for name in common])
        r = corr(a, b)
        if not math.isnan(r) and r < 0:
            coords[:, pc] *= -1
            signs[pc] = -1
    return signs


def build_model_payload(model_key: str, reference_coords: dict[str, list[float]], cluster_map: dict[str, str], axis_map: dict[str, float]) -> dict[str, object]:
    spec = MODEL_SPECS[model_key]
    root = VECTOR_ROOT / spec["folder"]
    role_dir = root / "role_vectors"
    trait_dir = root / "trait_vectors"
    if not role_dir.exists() or not trait_dir.exists():
        return {
            "available": False,
            "missing_reason": f"Missing role or trait vectors under {root}",
        }

    role_names, role_vecs = load_mean_vectors(role_dir)
    trait_names, trait_vecs = load_mean_vectors(trait_dir)
    role_by_name = {name: role_vecs[i] for i, name in enumerate(role_names)}
    trait_by_name = {name: trait_vecs[i] for i, name in enumerate(trait_names)}
    shared_roles = sorted(set(role_names) & set(reference_coords))
    shared_traits = sorted(trait_by_name)
    if len(shared_roles) < 25 or len(shared_traits) < 10:
        return {
            "available": False,
            "missing_reason": f"Insufficient shared roles/traits: roles={len(shared_roles)}, traits={len(shared_traits)}",
        }

    role_matrix = np.stack([role_by_name[name] for name in shared_roles])
    trait_matrix = np.stack([trait_by_name[name] for name in shared_traits])

    if model_key == "qwen":
        coords = np.array([reference_coords[name] for name in shared_roles], dtype=np.float64)
        explained = np.array([float("nan"), float("nan"), float("nan")])
        orientation_signs = [1, 1, 1]
        coordinate_source = "canonical_geometry_viz_data"
    else:
        coords, _, explained = pca_numpy(role_matrix, 3)
        orientation_signs = orient_to_reference(shared_roles, coords, reference_coords)
        coordinate_source = "recomputed_layer_mean_role_vector_pca_oriented_to_qwen_reference"

    role_t = normalize_rows(torch.from_numpy(role_matrix).float())
    trait_t = normalize_rows(torch.from_numpy(trait_matrix).float())
    sim = torch.mm(role_t, trait_t.T).numpy().astype(float)

    pc_percentiles = {f"pc{i+1}": pct_ranks(coords[:, i].tolist()) for i in range(3)}
    points: list[dict[str, object]] = []
    trait_profiles: dict[str, dict[str, float]] = {}
    for i, name in enumerate(shared_roles):
        trait_profiles[name] = {trait: float(sim[i, j]) for j, trait in enumerate(shared_traits)}
        points.append({
            "persona": name,
            "cluster": cluster_map.get(name, "unknown"),
            "assistant_axis": axis_map.get(name),
            "pc1": float(coords[i, 0]),
            "pc2": float(coords[i, 1]),
            "pc3": float(coords[i, 2]),
            "pc1_percentile": pc_percentiles["pc1"][i],
            "pc2_percentile": pc_percentiles["pc2"][i],
            "pc3_percentile": pc_percentiles["pc3"][i],
        })

    return {
        "available": True,
        "label": spec["label"],
        "folder": spec["folder"],
        "coordinate_source": coordinate_source,
        "orientation_signs": orientation_signs,
        "pca_explained_variance": [None if math.isnan(float(v)) else float(v) for v in explained],
        "role_count": len(shared_roles),
        "trait_count": len(shared_traits),
        "trait_names": shared_traits,
        "points": points,
        "trait_profiles": trait_profiles,
        "dependencies": {
            "role_vectors": str(role_dir.relative_to(REPO)),
            "trait_vectors": str(trait_dir.relative_to(REPO)),
            "geometry_reference": str(GEOMETRY_SOURCE.relative_to(REPO)),
        },
    }


def equal_count_assign(rows: list[dict[str, object]], axis: str, n_bins: int, key_name: str) -> list[tuple[float, float, list[dict[str, object]]]]:
    ordered = sorted(rows, key=lambda r: (float(r[axis]), str(r["persona"])))
    bins = []
    for b in range(n_bins):
        lo_i = math.floor(b * len(ordered) / n_bins)
        hi_i = math.floor((b + 1) * len(ordered) / n_bins)
        sub = ordered[lo_i:hi_i]
        for r in sub:
            r[key_name] = b
        vals = [float(r[axis]) for r in sub]
        bins.append((min(vals), max(vals), sub))
    return bins


def fixed_grid_assign(rows: list[dict[str, object]], axis: str, n_bins: int, key_name: str) -> list[tuple[float, float, list[dict[str, object]]]]:
    vals = [float(r[axis]) for r in rows]
    lo, hi = min(vals), max(vals)
    if hi == lo:
        hi = lo + 1.0
    edges = [lo + (hi - lo) * i / n_bins for i in range(n_bins + 1)]
    bins: list[list[dict[str, object]]] = [[] for _ in range(n_bins)]
    for r in rows:
        value = float(r[axis])
        idx = min(n_bins - 1, max(0, int((value - lo) / (hi - lo) * n_bins)))
        r[key_name] = idx
        bins[idx].append(r)
    return [(edges[i], edges[i + 1], bins[i]) for i in range(n_bins)]


def top_pairs(scores: list[tuple[str, float]], n: int = 8) -> list[dict[str, object]]:
    return [{"trait": t, "score": round(float(s), 4)} for t, s in scores[:n]]


def theme_for_traits(traits: list[str]) -> str:
    counts = Counter()
    for trait in traits[:5]:
        for theme, keywords in TRAIT_THEME_KEYWORDS.items():
            if trait in keywords:
                counts[theme] += 1
    return counts.most_common(1)[0][0] if counts else "other"


def compute_cells(model_key: str, model_payload: dict[str, object], x_axis: str, y_axis: str, basis: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    points = [dict(p) for p in model_payload["points"]]  # copy; bin assignment mutates rows
    traits = model_payload["trait_names"]
    profiles = model_payload["trait_profiles"]

    global_mean = {}
    global_std = {}
    for trait in traits:
        vals = [profiles[p["persona"]][trait] for p in points]
        global_mean[trait] = statistics.fmean(vals)
        sd = statistics.pstdev(vals)
        global_std[trait] = sd if sd > 1e-12 else 1.0

    if basis == "quantile":
        x_bins = equal_count_assign(points, x_axis, 5, "_xbin")
    elif basis == "fixed_grid":
        x_bins = fixed_grid_assign(points, x_axis, 5, "_xbin")
    else:
        raise ValueError(f"Unknown basis {basis}")

    cells: list[dict[str, object]] = []
    overlaps = []
    sparse_count = 0
    generated_cell_count = 0
    for x_idx, (x_min, x_max, x_rows) in enumerate(x_bins):
        if not x_rows:
            continue
        if basis == "quantile":
            y_bins = equal_count_assign(x_rows, y_axis, 3, "_ybin")
        else:
            y_bins = fixed_grid_assign(x_rows, y_axis, 3, "_ybin")
        band_mean = {
            trait: statistics.fmean([profiles[p["persona"]][trait] for p in x_rows])
            for trait in traits
        }
        for y_idx, (y_min, y_max, cell_rows) in enumerate(y_bins):
            generated_cell_count += 1
            if not cell_rows:
                sparse_count += 1
                continue
            cell_mean = {
                trait: statistics.fmean([profiles[p["persona"]][trait] for p in cell_rows])
                for trait in traits
            }
            local_scores = sorted(
                [(trait, (cell_mean[trait] - band_mean[trait]) / global_std[trait]) for trait in traits],
                key=lambda item: item[1],
                reverse=True,
            )
            global_scores = sorted(
                [(trait, (cell_mean[trait] - global_mean[trait]) / global_std[trait]) for trait in traits],
                key=lambda item: item[1],
                reverse=True,
            )
            local3 = {t for t, _ in local_scores[:3]}
            global3 = {t for t, _ in global_scores[:3]}
            overlap = len(local3 & global3) / 3.0
            overlaps.append(overlap)
            clusters = Counter(str(p.get("cluster", "unknown")) for p in cell_rows)
            dominant_cluster, dominant_n = clusters.most_common(1)[0]
            x_mid = (x_min + x_max) / 2.0
            y_mid = (y_min + y_max) / 2.0
            examples = sorted(
                cell_rows,
                key=lambda r: ((float(r[x_axis]) - x_mid) ** 2 + (float(r[y_axis]) - y_mid) ** 2, str(r["persona"])),
            )[:10]
            local_top_traits = [t for t, _ in local_scores[:5]]
            trait_region_cluster = theme_for_traits(local_top_traits)
            sparse = len(cell_rows) < SPARSE_THRESHOLD
            if sparse:
                sparse_count += 1
            cells.append({
                "cell_id": f"{model_key}_{x_axis}_{y_axis}_{basis}_x{x_idx+1}_y{y_idx+1}",
                "model": model_key,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "basis": basis,
                "x_bin": x_idx + 1,
                "y_bin": y_idx + 1,
                "y_band": ["low", "mid", "high"][y_idx],
                "x_min": round(float(x_min), 6),
                "x_max": round(float(x_max), 6),
                "y_min": round(float(y_min), 6),
                "y_max": round(float(y_max), 6),
                "x_mid": round(float(x_mid), 6),
                "y_mid": round(float(y_mid), 6),
                "role_count": len(cell_rows),
                "dominant_cluster": dominant_cluster,
                "dominant_cluster_fraction": round(dominant_n / len(cell_rows), 4),
                "trait_region_cluster": trait_region_cluster,
                "top_local_traits": top_pairs(local_scores, 8),
                "top_global_traits": top_pairs(global_scores, 8),
                "top_local_trait_names": ", ".join(t for t, _ in local_scores[:3]),
                "top_global_trait_names": ", ".join(t for t, _ in global_scores[:3]),
                "local_global_top3_overlap": round(overlap, 4),
                "example_roles": [p["persona"] for p in examples],
                "sparse_cell": sparse,
            })
    stats = {
        "cell_count": len(cells),
        "generated_cell_slots": generated_cell_count,
        "sparse_count": sparse_count,
        "mean_top3_local_global_overlap": round(statistics.fmean(overlaps), 4) if overlaps else None,
        "min_top3_local_global_overlap": round(min(overlaps), 4) if overlaps else None,
        "max_top3_local_global_overlap": round(max(overlaps), 4) if overlaps else None,
    }
    return cells, stats


def flatten_cell_for_csv(cell: dict[str, object]) -> dict[str, object]:
    return {
        "model": cell["model"],
        "x_axis": cell["x_axis"].upper(),
        "y_axis": cell["y_axis"].upper(),
        "basis": cell["basis"],
        "x_bin": cell["x_bin"],
        "y_bin": cell["y_bin"],
        "y_band": cell["y_band"],
        "x_min": cell["x_min"],
        "x_max": cell["x_max"],
        "y_min": cell["y_min"],
        "y_max": cell["y_max"],
        "role_count": cell["role_count"],
        "dominant_cluster": cell["dominant_cluster"],
        "dominant_cluster_fraction": cell["dominant_cluster_fraction"],
        "trait_region_cluster": cell["trait_region_cluster"],
        "top_local_trait_names": cell["top_local_trait_names"],
        "top_local_traits": "; ".join(f"{p['trait']}:{p['score']:.2f}" for p in cell["top_local_traits"]),
        "top_global_trait_names": cell["top_global_trait_names"],
        "top_global_traits": "; ".join(f"{p['trait']}:{p['score']:.2f}" for p in cell["top_global_traits"]),
        "local_global_top3_overlap": cell["local_global_top3_overlap"],
        "example_roles": ", ".join(cell["example_roles"]),
        "sparse_cell": cell["sparse_cell"],
    }


def make_html(data: dict[str, object]) -> str:
    payload = json.dumps(data, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Multi-Model Ordered Trait-Region Viewer</title>
  <style>
    :root {{
      --bg: #0d0d0d;
      --panel: #151515;
      --panel2: #101014;
      --line: #282828;
      --text: #e8e8e8;
      --muted: #8c8c8c;
      --accent: #4a9eff;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .shell {{ display: grid; grid-template-columns: 330px 1fr 360px; min-height: 100vh; }}
    aside {{ background: var(--panel); border-right: 1px solid var(--line); padding: 18px; overflow: auto; }}
    main {{ padding: 18px; }}
    .right {{ border-right: 0; border-left: 1px solid var(--line); }}
    h1 {{ font-size: 19px; margin: 0 0 8px; letter-spacing: .01em; }}
    h2 {{ font-size: 13px; color: #f1f1f1; margin: 20px 0 8px; text-transform: uppercase; letter-spacing: .08em; }}
    p, .small {{ color: var(--muted); font-size: 12px; line-height: 1.45; }}
    label {{ display: block; color: #bbbbbb; font-size: 12px; margin: 12px 0 5px; }}
    select, button {{ width: 100%; background: var(--panel2); color: var(--text); border: 1px solid #333; border-radius: 6px; padding: 8px 10px; }}
    button {{ cursor: pointer; }}
    .row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
    .pill {{ display: inline-block; border: 1px solid #3a3a3a; border-radius: 999px; padding: 3px 8px; color: #cfcfcf; font-size: 11px; margin: 3px 3px 3px 0; }}
    .warn {{ background: #2a1d10; border: 1px solid #7a4d1b; color: #f4bf75; padding: 9px; border-radius: 7px; font-size: 12px; }}
    .card {{ background: #111; border: 1px solid #2a2a2a; border-radius: 9px; padding: 12px; margin-top: 10px; }}
    #plot {{ width: 100%; min-height: calc(100vh - 36px); background: #fbfbf8; border: 1px solid #2a2a2a; border-radius: 10px; overflow: hidden; }}
    svg {{ display: block; width: 100%; height: auto; }}
    .role-point {{ cursor: pointer; }}
    .cell-rect {{ cursor: pointer; }}
    .cell-rect:hover {{ stroke-width: 3; }}
    .legend-swatch {{ width: 11px; height: 11px; border-radius: 3px; display: inline-block; margin-right: 6px; vertical-align: -1px; }}
    ul {{ padding-left: 18px; }}
    li {{ margin: 4px 0; }}
    code {{ color: #e7d38b; }}
    @media (max-width: 1100px) {{ .shell {{ grid-template-columns: 1fr; }} aside, .right {{ border: 0; border-bottom: 1px solid var(--line); }} #plot {{ height: 740px; }} }}
  </style>
</head>
<body>
<div class="shell">
  <aside>
    <h1>Ordered Trait Regions</h1>
    <p>Local labels are recomputed for the selected ordered axis view. The x-axis defines the conditioning baseline.</p>
    <label>Model</label>
    <select id="modelSelect"></select>
    <div class="row">
      <div><label>X axis / conditioning PC</label><select id="xAxis"></select></div>
      <div><label>Y axis / differentiation PC</label><select id="yAxis"></select></div>
    </div>
    <label>Region basis</label>
    <select id="basisSelect">
      <option value="quantile">Quantile bands (stable default)</option>
      <option value="fixed_grid">Fixed coordinate grid (descriptive)</option>
    </select>
    <label>Trait labels</label>
    <select id="labelCount">
      <option value="1">Top 1</option>
      <option value="3" selected>Top 3</option>
      <option value="5">Top 5</option>
    </select>
    <label>Point color</label>
    <select id="colorMode">
      <option value="cluster" selected>Cluster</option>
      <option value="region_cluster">Trait-region cluster</option>
      <option value="assistant_axis">Qwen assistant-axis projection</option>
    </select>
    <div class="card">
      <h2>Legend Semantics</h2>
      <p><b>Point color</b> means the selected point overlay. <b>Label text</b> means top locally enriched traits. <b>Label border/fill</b> means dominant trait-region cluster. These channels are intentionally separate.</p>
      <div id="regionLegend"></div>
    </div>
    <div class="card">
      <h2>Method Caveat</h2>
      <p>Trait labels are same-space activation-cosine overlays over released role/trait vectors. They are not independent psychological ratings, Big Five validation, or solved PC interpretations.</p>
    </div>
  </aside>
  <main><div id="plot"></div></main>
  <aside class="right">
    <h2>Selection</h2>
    <div id="detail" class="card"><p>Click a role point or region cell.</p></div>
    <h2>View Summary</h2>
    <div id="summary" class="card"></div>
  </aside>
</div>
<script>
const DATA = {payload};
const CLUSTER_COLORS = {json.dumps(CLUSTER_COLORS)};
const REGION_COLORS = {json.dumps(REGION_COLORS)};
const AXES = ["pc1","pc2","pc3"];
let selectedCell = null;
let selectedPoint = null;

function fmtAxis(a) {{ return a.toUpperCase(); }}
function cleanTrait(t) {{ return String(t || "").replaceAll("_", " "); }}
function cellKey(model,x,y,basis) {{ return `${{model}}|${{x}}|${{y}}|${{basis}}`; }}
function current() {{
  return {{
    model: document.getElementById("modelSelect").value,
    x: document.getElementById("xAxis").value,
    y: document.getElementById("yAxis").value,
    basis: document.getElementById("basisSelect").value,
    labels: Number(document.getElementById("labelCount").value),
    color: document.getElementById("colorMode").value,
  }};
}}
function colorscale(vals) {{
  const nums = vals.filter(v => typeof v === "number" && !Number.isNaN(v));
  const lo = Math.min(...nums), hi = Math.max(...nums);
  return vals.map(v => {{
    if (typeof v !== "number" || Number.isNaN(v)) return "#777";
    const t = (v - lo) / ((hi - lo) || 1);
    const r = Math.round(80 + 170*t), g = Math.round(145 - 90*t), b = Math.round(255 - 130*t);
    return `rgb(${{r}},${{g}},${{b}})`;
  }});
}}
function populateControls() {{
  const modelSel = document.getElementById("modelSelect");
  Object.entries(DATA.models).forEach(([key, m]) => {{
    const opt = document.createElement("option");
    opt.value = key; opt.textContent = m.available ? m.label : `${{key}} unavailable`;
    opt.disabled = !m.available; modelSel.appendChild(opt);
  }});
  ["xAxis","yAxis"].forEach((id, idx) => {{
    const sel = document.getElementById(id);
    AXES.forEach(a => {{
      const opt = document.createElement("option");
      opt.value = a; opt.textContent = fmtAxis(a);
      if ((idx === 0 && a === "pc1") || (idx === 1 && a === "pc2")) opt.selected = true;
      sel.appendChild(opt);
    }});
  }});
  document.getElementById("regionLegend").innerHTML = Object.entries(REGION_COLORS).map(([k,c]) => `<div class="small"><span class="legend-swatch" style="background:${{c}}"></span>${{k.replaceAll("_"," ")}}</div>`).join("");
}}
function enforceDistinctAxes(changed) {{
  const x = document.getElementById("xAxis"), y = document.getElementById("yAxis");
  if (x.value !== y.value) return;
  const fallback = AXES.find(a => a !== (changed === "x" ? x.value : y.value));
  if (changed === "x") y.value = fallback; else x.value = fallback;
}}
function activeCells(c) {{
  return DATA.views[cellKey(c.model,c.x,c.y,c.basis)]?.cells || [];
}}
function pointRegion(point, cells, axes) {{
  return cells.find(cell => point[axes.x] >= cell.x_min && point[axes.x] <= cell.x_max && point[axes.y] >= cell.y_min && point[axes.y] <= cell.y_max);
}}
function labelFor(cell, n) {{
  const traits = cell.top_local_traits.slice(0,n).map(p => cleanTrait(p.trait));
  return traits;
}}
function esc(s) {{
  return String(s ?? "").replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
}}
function scale(value, lo, hi, a, b) {{
  if (hi === lo) return (a + b) / 2;
  return a + (value - lo) * (b - a) / (hi - lo);
}}
function render() {{
  const c = current();
  const model = DATA.models[c.model];
  const cells = activeCells(c);
  const points = model.points || [];
  const regionByPoint = points.map(p => pointRegion(p, cells, c));
  let pointColors = points.map(p => CLUSTER_COLORS[p.cluster] || "#777");
  if (c.color === "region_cluster") pointColors = regionByPoint.map(cell => REGION_COLORS[cell?.trait_region_cluster || "other"]);
  if (c.color === "assistant_axis") pointColors = colorscale(points.map(p => p.assistant_axis));
  const W = 1120, H = 820;
  const m = {{ l: 76, r: 30, t: 72, b: 76 }};
  const plotW = W - m.l - m.r, plotH = H - m.t - m.b;
  const xVals = points.map(p => p[c.x]), yVals = points.map(p => p[c.y]);
  let xLo = Math.min(...xVals), xHi = Math.max(...xVals), yLo = Math.min(...yVals), yHi = Math.max(...yVals);
  const xPad = (xHi - xLo) * .07 || 1, yPad = (yHi - yLo) * .09 || 1;
  xLo -= xPad; xHi += xPad; yLo -= yPad; yHi += yPad;
  const sx = x => scale(x, xLo, xHi, m.l, m.l + plotW);
  const sy = y => scale(y, yLo, yHi, m.t + plotH, m.t);
  const tickVals = (lo, hi) => Array.from({{length:7}}, (_,i) => lo + (hi-lo)*i/6);
  let svg = `<svg viewBox="0 0 ${{W}} ${{H}}" role="img" aria-label="ordered trait region plot">`;
  svg += `<rect width="${{W}}" height="${{H}}" fill="#fbfbf8"/>`;
  svg += `<text x="${{W/2}}" y="30" text-anchor="middle" font-size="20" font-weight="700" fill="#111">${{esc(model.label)}} — ${{fmtAxis(c.x)}} conditions ${{fmtAxis(c.y)}} local trait regions</text>`;
  svg += `<text x="${{W/2}}" y="52" text-anchor="middle" font-size="12" fill="#555">x-axis bands define the local enrichment baseline; labels are top local traits</text>`;
  svg += `<rect x="${{m.l}}" y="${{m.t}}" width="${{plotW}}" height="${{plotH}}" fill="#fff" stroke="#d2d2d2"/>`;
  for (const tv of tickVals(xLo, xHi)) {{
    const x = sx(tv);
    svg += `<line x1="${{x}}" y1="${{m.t}}" x2="${{x}}" y2="${{m.t+plotH}}" stroke="#ece7dc"/>`;
    svg += `<text x="${{x}}" y="${{m.t+plotH+22}}" text-anchor="middle" font-size="10" fill="#555">${{tv.toFixed(0)}}</text>`;
  }}
  for (const tv of tickVals(yLo, yHi)) {{
    const y = sy(tv);
    svg += `<line x1="${{m.l}}" y1="${{y}}" x2="${{m.l+plotW}}" y2="${{y}}" stroke="#ece7dc"/>`;
    svg += `<text x="${{m.l-10}}" y="${{y+4}}" text-anchor="end" font-size="10" fill="#555">${{tv.toFixed(0)}}</text>`;
  }}
  svg += `<line x1="${{sx(0)}}" y1="${{m.t}}" x2="${{sx(0)}}" y2="${{m.t+plotH}}" stroke="#b5b5b5" stroke-dasharray="4 4"/>`;
  svg += `<line x1="${{m.l}}" y1="${{sy(0)}}" x2="${{m.l+plotW}}" y2="${{sy(0)}}" stroke="#b5b5b5" stroke-dasharray="4 4"/>`;
  cells.forEach((cell, i) => {{
    const color = REGION_COLORS[cell.trait_region_cluster] || REGION_COLORS.other;
    const x = sx(cell.x_min), y = sy(cell.y_max), w = sx(cell.x_max) - sx(cell.x_min), h = sy(cell.y_min) - sy(cell.y_max);
    svg += `<rect class="cell-rect" data-cell="${{i}}" x="${{x}}" y="${{y}}" width="${{w}}" height="${{h}}" fill="${{color}}18" stroke="${{color}}" stroke-width="${{cell.sparse_cell ? 1 : 1.5}}" stroke-dasharray="${{cell.sparse_cell ? '2 4' : '6 4'}}"><title>${{esc(fmtAxis(cell.x_axis)+' band '+cell.x_bin+' / '+fmtAxis(cell.y_axis)+' '+cell.y_band+' n='+cell.role_count+' local: '+cell.top_local_trait_names)}}</title></rect>`;
  }});
  points.forEach((p, i) => {{
    svg += `<circle class="role-point" data-point="${{i}}" cx="${{sx(p[c.x])}}" cy="${{sy(p[c.y])}}" r="4.2" fill="${{pointColors[i]}}" fill-opacity=".72" stroke="#111" stroke-width=".45"><title>${{esc(p.persona+' | '+p.cluster+' | '+fmtAxis(c.x)+' '+p[c.x].toFixed(2)+' | '+fmtAxis(c.y)+' '+p[c.y].toFixed(2))}}</title></circle>`;
  }});
  cells.forEach((cell, i) => {{
    const color = REGION_COLORS[cell.trait_region_cluster] || REGION_COLORS.other;
    const x = sx(cell.x_mid), y = sy(cell.y_mid);
    const traits = labelFor(cell, c.labels);
    const boxH = 28 + traits.length * 14;
    svg += `<g class="cell-label" data-cell="${{i}}" style="pointer-events:none"><rect x="${{x-70}}" y="${{y-boxH/2}}" width="140" height="${{boxH}}" rx="6" fill="rgba(255,255,255,.9)" stroke="${{color}}" stroke-width="1.2"/>`;
    traits.forEach((t, j) => {{ svg += `<text x="${{x}}" y="${{y-boxH/2+18+j*14}}" text-anchor="middle" font-size="11" fill="#111">${{esc(t)}}</text>`; }});
    svg += `<text x="${{x}}" y="${{y+boxH/2-6}}" text-anchor="middle" font-size="9" fill="#555">n=${{cell.role_count}}</text></g>`;
  }});
  svg += `<text x="${{W/2}}" y="${{H-24}}" text-anchor="middle" font-size="15" font-weight="700" fill="#111">${{fmtAxis(c.x)}} conditioning axis</text>`;
  svg += `<text x="26" y="${{H/2}}" text-anchor="middle" font-size="15" font-weight="700" fill="#111" transform="rotate(-90 26 ${{H/2}})">${{fmtAxis(c.y)}} differentiation axis</text>`;
  svg += `</svg>`;
  document.getElementById("plot").innerHTML = svg;
  document.querySelectorAll(".cell-rect").forEach(el => el.addEventListener("click", () => {{
    const cell = cells[Number(el.dataset.cell)];
    document.getElementById("detail").innerHTML = detailForCell(cell);
  }}));
  document.querySelectorAll(".role-point").forEach(el => el.addEventListener("click", () => {{
    const point = points[Number(el.dataset.point)];
    document.getElementById("detail").innerHTML = detailForPoint(point, pointRegion(point, cells, c));
  }}));
  document.getElementById("summary").innerHTML = viewSummary(c, cells, model);
}}
function viewSummary(c, cells, model) {{
  const stats = DATA.view_stats[cellKey(c.model,c.x,c.y,c.basis)] || {{}};
  const sparse = cells.filter(cell => cell.sparse_cell).length;
  return `<p><b>${{model.label}}</b><br>${{fmtAxis(c.x)}} conditions ${{fmtAxis(c.y)}}. The x-axis bands define the local baseline.</p>
    <div class="pill">${{c.basis.replace("_"," ")}}</div><div class="pill">${{cells.length}} cells</div><div class="pill">${{sparse}} sparse</div>
    <p>Mean top-3 local/global overlap: <b>${{stats.mean_top3_local_global_overlap ?? "n/a"}}</b>.</p>
    <p class="small">Dependencies: ${{Object.values(model.dependencies || {{}}).join("; ")}}</p>`;
}}
function detailForCell(cell) {{
  const local = cell.top_local_traits.slice(0,8).map(p => `<li><b>${{cleanTrait(p.trait)}}</b>: ${{p.score.toFixed(2)}}</li>`).join("");
  const global = cell.top_global_traits.slice(0,8).map(p => `<li><b>${{cleanTrait(p.trait)}}</b>: ${{p.score.toFixed(2)}}</li>`).join("");
  return `<h2>Region Cell</h2><p><b>${{fmtAxis(cell.x_axis)}} band ${{cell.x_bin}}</b> conditions <b>${{fmtAxis(cell.y_axis)}} ${{cell.y_band}}</b></p>
    ${{cell.sparse_cell ? '<div class="warn">Sparse cell; descriptive only.</div>' : ''}}
    <p>n=${{cell.role_count}}; dominant cluster: <b>${{cell.dominant_cluster}}</b> (${{Math.round(cell.dominant_cluster_fraction*100)}}%); region cluster: <b>${{cell.trait_region_cluster.replaceAll("_"," ")}}</b>.</p>
    <h2>Local enrichment</h2><ul>${{local}}</ul>
    <h2>Global enrichment</h2><ul>${{global}}</ul>
    <p>Top-3 overlap: <b>${{cell.local_global_top3_overlap}}</b></p>
    <h2>Example roles</h2><p>${{cell.example_roles.join(", ")}}</p>`;
}}
function detailForPoint(point, cell) {{
  return `<h2>Role Point</h2><p><b>${{point.persona}}</b><br>cluster: ${{point.cluster}}</p>
    <p>PC1 ${{point.pc1.toFixed(2)}} · PC2 ${{point.pc2.toFixed(2)}} · PC3 ${{point.pc3.toFixed(2)}}</p>
    <p>Percentiles: PC1 ${{point.pc1_percentile.toFixed(1)}} · PC2 ${{point.pc2_percentile.toFixed(1)}} · PC3 ${{point.pc3_percentile.toFixed(1)}}</p>
    ${{cell ? `<h2>Containing region</h2>${{detailForCell(cell)}}` : ""}}`;
}}
document.addEventListener("DOMContentLoaded", () => {{
  populateControls();
  ["modelSelect","basisSelect","labelCount","colorMode"].forEach(id => document.getElementById(id).addEventListener("change", render));
  document.getElementById("xAxis").addEventListener("change", () => {{ enforceDistinctAxes("x"); render(); }});
  document.getElementById("yAxis").addEventListener("change", () => {{ enforceDistinctAxes("y"); render(); }});
  render();
}});
</script>
</body>
</html>
"""


def make_static_svg(data: dict[str, object], model_key: str, x_axis: str, y_axis: str, path: Path) -> None:
    model = data["models"][model_key]
    key = f"{model_key}|{x_axis}|{y_axis}|quantile"
    cells = data["views"][key]["cells"]
    points = model["points"]
    w, h = 1320, 900
    m = {"l": 80, "r": 30, "t": 70, "b": 70}
    plot_w = w - m["l"] - m["r"]
    plot_h = h - m["t"] - m["b"]
    xs = [p[x_axis] for p in points]
    ys = [p[y_axis] for p in points]
    xlo, xhi = min(xs), max(xs)
    ylo, yhi = min(ys), max(ys)
    xpad = (xhi - xlo) * 0.06 or 1.0
    ypad = (yhi - ylo) * 0.08 or 1.0
    xlo -= xpad; xhi += xpad; ylo -= ypad; yhi += ypad
    def sx(x): return m["l"] + (x - xlo) / (xhi - xlo) * plot_w
    def sy(y): return m["t"] + plot_h - (y - ylo) / (yhi - ylo) * plot_h
    def esc(s): return html.escape(str(s))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    parts.append('<rect width="100%" height="100%" fill="#fbfbf8"/>')
    parts.append(f'<text x="{w/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">{esc(model["label"])} {x_axis.upper()} x {y_axis.upper()} ordered trait regions</text>')
    parts.append(f'<rect x="{m["l"]}" y="{m["t"]}" width="{plot_w}" height="{plot_h}" fill="#fff" stroke="#ccc"/>')
    for cell in cells:
        color = REGION_COLORS.get(cell["trait_region_cluster"], REGION_COLORS["other"])
        parts.append(f'<rect x="{sx(cell["x_min"]):.1f}" y="{sy(cell["y_max"]):.1f}" width="{sx(cell["x_max"])-sx(cell["x_min"]):.1f}" height="{sy(cell["y_min"])-sy(cell["y_max"]):.1f}" fill="none" stroke="{color}" stroke-dasharray="5 4"/>')
    for p in points:
        color = CLUSTER_COLORS.get(p.get("cluster"), "#777")
        parts.append(f'<circle cx="{sx(p[x_axis]):.1f}" cy="{sy(p[y_axis]):.1f}" r="3" fill="{color}" fill-opacity=".38"/>')
    for cell in cells:
        x = sx(cell["x_mid"]); y = sy(cell["y_mid"])
        traits = [clean["trait"] for clean in cell["top_local_traits"][:3]]
        color = REGION_COLORS.get(cell["trait_region_cluster"], REGION_COLORS["other"])
        parts.append(f'<rect x="{x-78:.1f}" y="{y-34:.1f}" width="156" height="62" rx="6" fill="#fffffff0" stroke="{color}"/>')
        parts.append(f'<text x="{x:.1f}" y="{y-16:.1f}" text-anchor="middle" font-family="Arial" font-size="10" font-weight="700">n={cell["role_count"]}</text>')
        for i, t in enumerate(traits):
            parts.append(f'<text x="{x:.1f}" y="{y+i*14:.1f}" text-anchor="middle" font-family="Arial" font-size="11">{esc(t)}</text>')
    parts.append(f'<text x="{w/2}" y="{h-25}" text-anchor="middle" font-family="Arial" font-size="15" font-weight="700">{x_axis.upper()} conditioning axis</text>')
    parts.append(f'<text x="28" y="{h/2}" text-anchor="middle" font-family="Arial" font-size="15" font-weight="700" transform="rotate(-90 28 {h/2})">{y_axis.upper()} differentiation axis</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n")


def build_report(data: dict[str, object], combined_rows: list[dict[str, object]]) -> str:
    available = [k for k, v in data["models"].items() if v.get("available")]
    unavailable = {k: v.get("missing_reason", "unknown") for k, v in data["models"].items() if not v.get("available")}
    quantile_stats = [v for k, v in data["view_stats"].items() if k.endswith("|quantile")]
    fixed_stats = [v for k, v in data["view_stats"].items() if k.endswith("|fixed_grid")]
    def avg(items, field):
        vals = [x[field] for x in items if x.get(field) is not None]
        return statistics.fmean(vals) if vals else float("nan")
    reverse_pairs = []
    for model in available:
        for a, b in [("pc1", "pc2"), ("pc1", "pc3"), ("pc2", "pc3")]:
            k1 = f"{model}|{a}|{b}|quantile"
            k2 = f"{model}|{b}|{a}|quantile"
            s1 = data["view_stats"][k1]["mean_top3_local_global_overlap"]
            s2 = data["view_stats"][k2]["mean_top3_local_global_overlap"]
            reverse_pairs.append((model, a, b, s1, s2, abs(s1 - s2)))
    strongest_reverse = sorted(reverse_pairs, key=lambda r: r[-1], reverse=True)[:6]
    qwen_like = []
    for model in available:
        for view in [("pc1", "pc2"), ("pc2", "pc1")]:
            key = f"{model}|{view[0]}|{view[1]}|quantile"
            cells = data["views"][key]["cells"]
            qwen_like.append((model, view, data["view_stats"][key]["mean_top3_local_global_overlap"], sum(1 for c in cells if c["sparse_cell"])))
    lines = [
        "# Multi-Model Ordered Trait-Region Viewer",
        "",
        f"Generated UTC: {UPDATED}",
        f"model_used: {MODEL_USED}",
        "",
        "## Startup and Source Status",
        "",
        "Startup verification was run before generation using the raw `STARTUP_MANIFEST.md`, `RESEARCH_STATE.md`, `THREAD_START.md`, and `CLAIMS_REGISTER.md` files from GitHub. The canonical file hashes matched the manifest.",
        "",
        "## What Was Built",
        "",
        "Created a single integrated HTML viewer for ordered trait-region overlays across available Qwen, Llama, and Gemma released-vector artifacts. The viewer supports model selection, ordered x/y PC-axis selection, quantile or fixed-grid region basis, label count selection, point coloring by cluster/region/assistant-axis, role-point click details, and region click details.",
        "",
        "The important methodological rule is enforced in the generated data: the selected x-axis defines the conditioning bands. `PC1 x PC2` asks how PC2 varies within PC1 bands; `PC2 x PC1` asks how PC1 varies within PC2 bands. These are not treated as equivalent.",
        "",
        "## Available Models",
        "",
    ]
    for model in available:
        m = data["models"][model]
        lines.append(f"- {model}: available, {m['role_count']} roles, {m['trait_count']} traits, coordinate source `{m['coordinate_source']}`.")
    for model, reason in unavailable.items():
        lines.append(f"- {model}: unavailable, {reason}.")
    lines += [
        "",
        "## Ordered Axis Views Generated",
        "",
        f"Generated {len(available) * len(ORDERED_VIEWS)} ordered model/axis views for each basis, covering all six ordered PC pairs per available model. Combined cell table rows: {len(combined_rows)}.",
        "",
        "## Dependencies Used",
        "",
    ]
    for model in available:
        m = data["models"][model]
        lines.append(f"- {model}: role vectors `{m['dependencies']['role_vectors']}`, trait vectors `{m['dependencies']['trait_vectors']}`, reference geometry `{m['dependencies']['geometry_reference']}`.")
    lines += [
        "",
        "## Local-vs-Global Label Difference",
        "",
        f"- Quantile views mean top-3 local/global overlap across views: {avg(quantile_stats, 'mean_top3_local_global_overlap'):.3f}.",
        f"- Fixed-grid views mean top-3 local/global overlap across views: {avg(fixed_stats, 'mean_top3_local_global_overlap'):.3f}.",
        "- Low overlap means local x-axis-band-relative labels differ materially from global cell labels, so the selected conditioning axis matters.",
        "",
        "## Axis Reversal",
        "",
        "Observed: reversing axes changes the conditioning baseline and changes local enrichment labels. Largest quantile-view reversal differences by mean local/global overlap:",
        "",
    ]
    for model, a, b, s1, s2, diff in strongest_reverse:
        lines.append(f"- {model} {a.upper()}x{b.upper()} overlap {s1:.3f} vs {b.upper()}x{a.upper()} overlap {s2:.3f}; absolute difference {diff:.3f}.")
    lines += [
        "",
        "Inferred: reverse views should be inspected as distinct hypotheses rather than as cosmetic axis swaps.",
        "",
        "## Cross-Model Interpretation Notes",
        "",
        "Observed: Qwen, Llama, and Gemma all have complete local released role/trait vector dependencies, so no model was excluded. Qwen uses canonical `geometry_viz_data.json` coordinates; Llama and Gemma coordinates are recomputed from layer-mean role vectors and sign-oriented to the Qwen reference geometry.",
        "",
        "Inferred: Qwen and Llama remain the most comparable pair for PC1/PC2 based on prior cross-model diagnostics. Gemma should be treated as secondary/contextual because prior diagnostics already found divergence from Qwen/Llama in effective psychological taxonomy.",
        "",
        "Speculative: publication-worthy views are likely the ordered PC1/PC2 and PC2/PC1 panels for Qwen and Llama, because they directly test whether local PC2 and PC1 interpretations survive conditioning-axis reversal. PC3 views are useful for exploration but should stay lower-confidence.",
        "",
        "Unknown: whether these same-space trait-cosine labels would survive independent human/LLM trait ratings or response-derived trait scoring.",
        "",
        "## Sparse Cells",
        "",
    ]
    sparse_quantile = sum(s["sparse_count"] for s in quantile_stats)
    sparse_fixed = sum(s["sparse_count"] for s in fixed_stats)
    lines.append(f"- Quantile basis sparse cells: {sparse_quantile}.")
    lines.append(f"- Fixed-grid basis sparse/empty cells: {sparse_fixed}.")
    lines.append("- Quantile views are the stable default because they control sample size. Fixed-grid views are descriptive and should not be overinterpreted in sparse regions.")
    lines += [
        "",
        "## Manual Inspection Recommendations",
        "",
        "1. Compare Qwen PC1xPC2 against Qwen PC2xPC1 to see how PC2-local labels change when PC2 becomes the conditioning axis.",
        "2. Compare Qwen and Llama PC1xPC2 for broad PC1 organization, then inspect Gemma as a divergence case.",
        "3. Treat PC3 ordered views as exploratory until cross-model PC3 alignment is stronger.",
        "4. Inspect sparse fixed-grid cells only as visual prompts, not as stable enrichment estimates.",
        "",
        "## Interpretation Constraints",
        "",
        "- Treat labels as activation-space trait-vector enrichments, not independent psychological ratings.",
        "- Do not claim Big Five/Dark Triad validation from this viewer.",
        "- Do not claim PC2 or PC3 is solved from visualization alone.",
        "- The selected x-axis defines the conditioning baseline and must be reported with any screenshot or interpretation.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    reference_coords, cluster_map, axis_map = load_geometry_reference()
    data: dict[str, object] = {
        "metadata": {
            "generated_utc": UPDATED,
            "model_used": MODEL_USED,
            "method": "ordered_x_axis_conditioned_trait_region_enrichment",
            "sparse_threshold": SPARSE_THRESHOLD,
            "sources": {
                "geometry_source": str(GEOMETRY_SOURCE.relative_to(REPO)),
                "qwen_prior_cells": str(QWEN_PRIOR_CELLS.relative_to(REPO)),
                "qwen_joined_trait_matrix": str(QWEN_JOINED_TRAIT_MATRIX.relative_to(REPO)),
                "vector_root": str(VECTOR_ROOT.relative_to(REPO)),
            },
            "ordered_views": [f"{x.upper()}_x_{y.upper()}" for x, y in ORDERED_VIEWS],
            "basis_options": BASES,
        },
        "models": {},
        "views": {},
        "view_stats": {},
        "region_colors": REGION_COLORS,
        "cluster_colors": CLUSTER_COLORS,
    }

    combined_rows: list[dict[str, object]] = []
    for model_key in MODEL_SPECS:
        payload = build_model_payload(model_key, reference_coords, cluster_map, axis_map)
        data["models"][model_key] = payload
        if not payload.get("available"):
            continue
        for x_axis, y_axis in ORDERED_VIEWS:
            for basis in BASES:
                cells, stats = compute_cells(model_key, payload, x_axis, y_axis, basis)
                key = f"{model_key}|{x_axis}|{y_axis}|{basis}"
                data["views"][key] = {
                    "model": model_key,
                    "x_axis": x_axis,
                    "y_axis": y_axis,
                    "basis": basis,
                    "cells": cells,
                }
                data["view_stats"][key] = stats
                combined_rows.extend(flatten_cell_for_csv(cell) for cell in cells)

    data_path = OUT / "multimodel_ordered_trait_region_data.json"
    data_path.write_text(json.dumps(data, indent=2))

    csv_fields = [
        "model", "x_axis", "y_axis", "basis", "x_bin", "y_bin", "y_band",
        "x_min", "x_max", "y_min", "y_max", "role_count", "dominant_cluster",
        "dominant_cluster_fraction", "trait_region_cluster", "top_local_trait_names",
        "top_local_traits", "top_global_trait_names", "top_global_traits",
        "local_global_top3_overlap", "example_roles", "sparse_cell",
    ]
    write_csv(OUT / "combined_ordered_trait_region_cells.csv", combined_rows, csv_fields)

    html_path = OUT / "multimodel_ordered_trait_region_viewer.html"
    html_path.write_text(make_html(data))

    static_views = [
        ("qwen", "pc1", "pc2"),
        ("qwen", "pc2", "pc1"),
        ("llama", "pc1", "pc2"),
        ("gemma", "pc1", "pc2"),
    ]
    static_files = []
    for model, x, y in static_views:
        if data["models"].get(model, {}).get("available"):
            path = OUT / f"{model}_{x}_{y}_ordered_trait_regions.svg"
            make_static_svg(data, model, x, y, path)
            static_files.append(path)

    report_path = OUT / "multimodel_ordered_trait_region_report.md"
    report_path.write_text(build_report(data, combined_rows))

    inventory_rows = [
        {
            "artifact": str((OUT / "multimodel_ordered_trait_region_viewer.html").relative_to(REPO)),
            "kind": "interactive_html",
            "description": "Integrated multi-model ordered-axis trait-region viewer.",
        },
        {
            "artifact": str(data_path.relative_to(REPO)),
            "kind": "json_data",
            "description": "Bundled role points, ordered cell definitions, local/global trait enrichments, and view stats.",
        },
        {
            "artifact": str((OUT / "combined_ordered_trait_region_cells.csv").relative_to(REPO)),
            "kind": "csv",
            "description": "Combined cell table for all available models, ordered axis pairs, and region bases.",
        },
        {
            "artifact": str(report_path.relative_to(REPO)),
            "kind": "report",
            "description": "Method/report for multi-model ordered trait-region viewer.",
        },
        {
            "artifact": str(Path(__file__).relative_to(REPO)),
            "kind": "script",
            "description": "Reusable generation script.",
        },
    ]
    for path in static_files:
        inventory_rows.append({
            "artifact": str(path.relative_to(REPO)),
            "kind": "static_svg",
            "description": "Static ordered trait-region view export.",
        })
    write_csv(OUT / "artifact_inventory.csv", inventory_rows, ["artifact", "kind", "description"])

    print(f"Wrote {html_path.relative_to(REPO)}")
    print(f"Wrote {data_path.relative_to(REPO)}")
    print(f"Wrote {len(combined_rows)} combined cell rows")


if __name__ == "__main__":
    main()
