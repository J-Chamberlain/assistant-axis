#!/usr/bin/env python3
"""Build a layered activation-cloud viewer for A100 and recovered role runs."""

from __future__ import annotations

import csv
import html
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "research/outputs/activation_cloud_layered_viewer"
OUT.mkdir(parents=True, exist_ok=True)

GEOMETRY = REPO / "research/visualizations/geometry_viz_data.json"
A100_ROWS = REPO / "research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv"
A100_GPT41 = REPO / "research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv"
A100_GPT55 = REPO / "research/outputs/gpt55_judge_and_outlier_followup/gpt55_judge_scores.csv"
RECOVERED_COORDS = REPO / "research/outputs/prior_adaptive_recovery_audit/prior_adaptive_corrected_coordinates.csv"
RECOVERED_INPUTS = REPO / "research/outputs/prior_adaptive_recovery_audit/prior_adaptive_gpt41_judge_inputs.jsonl"
RECOVERED_GPT41 = REPO / "research/outputs/recovered_role_cloud_analysis/recovered_gpt41_scores.csv"
EXISTING_VIEWER = REPO / "research/outputs/a100_activation_cloud_visualization_and_judge_compare/activation_cloud_viewer.html"
EXISTING_VIEWER_DATA = REPO / "research/outputs/a100_activation_cloud_visualization_and_judge_compare/activation_cloud_viewer_data.json"

MIN_STABLE_CENTROID_N = 5
MIN_COV_N = 5


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def boolish(value: Any) -> bool:
    return str(value).lower() in {"true", "1", "yes"}


def safe_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def safe_float(value: Any) -> float:
    return float(value)


def response_excerpt(text: str, n: int = 260) -> str:
    text = " ".join((text or "").split())
    return text[: n - 1] + "…" if len(text) > n else text


def load_published_centroids() -> dict[str, dict[str, Any]]:
    data = json.loads(GEOMETRY.read_text())
    roles = data["roles"]
    out = {}
    for name, coords, cluster in zip(roles["names"], roles["pca3d"], roles["clusters"]):
        out[name] = {
            "pc1": float(coords[0]),
            "pc2": float(coords[1]),
            "pc3": float(coords[2]),
            "cluster": cluster,
        }
    return out


def distance(row: dict[str, Any], centroid: dict[str, Any]) -> float:
    return math.sqrt(
        (float(row["pc1"]) - centroid["pc1"]) ** 2
        + (float(row["pc2"]) - centroid["pc2"]) ** 2
        + (float(row["pc3"]) - centroid["pc3"]) ** 2
    )


def normalize_points() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    published = load_published_centroids()
    gpt41 = {r["response_id"]: r for r in read_csv(A100_GPT41)}
    gpt55 = {r["response_id"]: r for r in read_csv(A100_GPT55)} if A100_GPT55.exists() else {}
    recovered_gpt41 = {r["response_id"]: r for r in read_csv(RECOVERED_GPT41)}
    recovered_inputs = {r["response_id"]: r for r in load_jsonl(RECOVERED_INPUTS)}

    points: list[dict[str, Any]] = []

    for row in read_csv(A100_ROWS):
        role = row["role"]
        centroid = published[role]
        s41 = gpt41.get(row["response_id"], {})
        s55 = gpt55.get(row["response_id"], {})
        point = {
            "role_or_run": role,
            "role": role,
            "source_run": f"{role}_a100_cloud_60",
            "response_id": row["response_id"],
            "pc1": safe_float(row["pc1"]),
            "pc2": safe_float(row["pc2"]),
            "pc3": safe_float(row["pc3"]),
            "published_centroid_pc1": centroid["pc1"],
            "published_centroid_pc2": centroid["pc2"],
            "published_centroid_pc3": centroid["pc3"],
            "published_cluster": centroid["cluster"],
            "gpt41_score": safe_int(s41.get("score_0_to_3")),
            "gpt55_score": safe_int(s55.get("score_0_to_3")),
            "instruction_id": row.get("instruction_id", ""),
            "question_id": row.get("question_id", ""),
            "response_text_excerpt": response_excerpt(row.get("generated_response", "")),
            "distance_to_published_centroid": safe_float(row["distance_to_published_role_centroid_3d"]),
        }
        points.append(point)

    for row in read_csv(RECOVERED_COORDS):
        role = row["role"]
        centroid = published[role]
        response_id = row["response_id"]
        s41 = recovered_gpt41.get(response_id, {})
        source = recovered_inputs.get(response_id, {})
        point = {
            "role_or_run": row["run_id"],
            "role": role,
            "source_run": row["run_id"],
            "response_id": response_id,
            "pc1": safe_float(row["pc1"]),
            "pc2": safe_float(row["pc2"]),
            "pc3": safe_float(row["pc3"]),
            "published_centroid_pc1": centroid["pc1"],
            "published_centroid_pc2": centroid["pc2"],
            "published_centroid_pc3": centroid["pc3"],
            "published_cluster": centroid["cluster"],
            "gpt41_score": safe_int(s41.get("score_0_to_3")),
            "gpt55_score": None,
            "instruction_id": row.get("sp_idx", ""),
            "question_id": row.get("q_idx", ""),
            "response_text_excerpt": response_excerpt(source.get("generated_response", "")),
            "distance_to_published_centroid": distance(row, centroid),
        }
        points.append(point)

    source_status = {
        "geometry": str(GEOMETRY.relative_to(REPO)),
        "amateur_playwright_rows": str(A100_ROWS.relative_to(REPO)),
        "amateur_playwright_gpt41": str(A100_GPT41.relative_to(REPO)),
        "amateur_playwright_gpt55": str(A100_GPT55.relative_to(REPO)) if A100_GPT55.exists() else None,
        "recovered_coordinates": str(RECOVERED_COORDS.relative_to(REPO)),
        "recovered_gpt41": str(RECOVERED_GPT41.relative_to(REPO)),
        "existing_viewer": str(EXISTING_VIEWER.relative_to(REPO)) if EXISTING_VIEWER.exists() else None,
        "existing_viewer_data": str(EXISTING_VIEWER_DATA.relative_to(REPO)) if EXISTING_VIEWER_DATA.exists() else None,
    }
    return points, source_status


def subset_points(points: list[dict[str, Any]], layer_key: str) -> list[dict[str, Any]]:
    if layer_key == "all":
        return points
    if layer_key == "gpt41_ge2":
        return [p for p in points if p.get("gpt41_score") is not None and p["gpt41_score"] >= 2]
    if layer_key == "gpt41_eq3":
        return [p for p in points if p.get("gpt41_score") == 3]
    if layer_key == "gpt55_ge2":
        return [p for p in points if p.get("gpt55_score") is not None and p["gpt55_score"] >= 2]
    if layer_key == "gpt55_eq3":
        return [p for p in points if p.get("gpt55_score") == 3]
    raise ValueError(layer_key)


LAYER_LABELS = {
    "all": "All responses",
    "gpt41_ge2": "GPT-4.1 score>=2",
    "gpt41_eq3": "GPT-4.1 score==3",
    "gpt55_ge2": "GPT-5.5 score>=2",
    "gpt55_eq3": "GPT-5.5 score==3",
}


def compute_centroids(points: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    role_runs = sorted({p["role_or_run"] for p in points})
    centroids: list[dict[str, Any]] = []
    counts: list[dict[str, Any]] = []
    ellipses: dict[str, Any] = {}

    for role_run in role_runs:
        run_points = [p for p in points if p["role_or_run"] == role_run]
        role = run_points[0]["role"]
        published = {
            "pc1": run_points[0]["published_centroid_pc1"],
            "pc2": run_points[0]["published_centroid_pc2"],
            "pc3": run_points[0]["published_centroid_pc3"],
        }
        centroids.append(
            {
                "role_or_run": role_run,
                "role": role,
                "layer_key": "published",
                "layer_label": "Published centroid",
                "n": "",
                "pc1": published["pc1"],
                "pc2": published["pc2"],
                "pc3": published["pc3"],
                "distance_to_published_centroid": 0.0,
                "sparse_warning": "",
                "centroid_type": "published",
            }
        )
        for layer_key, label in LAYER_LABELS.items():
            pts = subset_points(run_points, layer_key)
            if not pts:
                counts.append(
                    {
                        "role_or_run": role_run,
                        "role": role,
                        "layer_key": layer_key,
                        "layer_label": label,
                        "point_count": 0,
                        "centroid_available": False,
                        "sparse_warning": "layer unavailable",
                    }
                )
                continue
            arr = np.array([[p["pc1"], p["pc2"], p["pc3"]] for p in pts], dtype=float)
            mean = arr.mean(axis=0)
            dist = float(np.linalg.norm(mean - np.array([published["pc1"], published["pc2"], published["pc3"]])))
            sparse = "" if len(pts) >= MIN_STABLE_CENTROID_N else f"sparse centroid n={len(pts)}"
            counts.append(
                {
                    "role_or_run": role_run,
                    "role": role,
                    "layer_key": layer_key,
                    "layer_label": label,
                    "point_count": len(pts),
                    "centroid_available": True,
                    "sparse_warning": sparse,
                }
            )
            centroids.append(
                {
                    "role_or_run": role_run,
                    "role": role,
                    "layer_key": layer_key,
                    "layer_label": f"{label} centroid",
                    "n": len(pts),
                    "pc1": float(mean[0]),
                    "pc2": float(mean[1]),
                    "pc3": float(mean[2]),
                    "distance_to_published_centroid": dist,
                    "sparse_warning": sparse,
                    "centroid_type": "computed",
                }
            )
            if layer_key in {"all", "gpt41_eq3", "gpt55_eq3"} and len(pts) >= MIN_COV_N:
                ellipses[f"{role_run}:{layer_key}"] = {
                    "role_or_run": role_run,
                    "role": role,
                    "layer_key": layer_key,
                    "layer_label": label,
                    "n": len(pts),
                    "points": {
                        "pc1_pc2": covariance_ellipse(arr[:, [0, 1]]),
                        "pc1_pc3": covariance_ellipse(arr[:, [0, 2]]),
                        "pc2_pc3": covariance_ellipse(arr[:, [1, 2]]),
                    },
                }
    return centroids, counts, ellipses


def covariance_ellipse(arr2: np.ndarray, n_std: float = 2.0, steps: int = 96) -> list[list[float]]:
    mean = arr2.mean(axis=0)
    cov = np.cov(arr2.T)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]
    theta = np.linspace(0, 2 * np.pi, steps)
    circle = np.stack([np.cos(theta), np.sin(theta)])
    scale = np.diag(np.sqrt(np.maximum(vals, 0)) * n_std)
    pts = (vecs @ scale @ circle).T + mean
    return [[float(x), float(y)] for x, y in pts]


def write_data(points: list[dict[str, Any]], centroids: list[dict[str, Any]], counts: list[dict[str, Any]], ellipses: dict[str, Any], sources: dict[str, Any]) -> None:
    data = {
        "metadata": {
            "startup_status": "STARTUP VERIFIED",
            "main_geometry_viewer_modified": False,
            "min_stable_centroid_n": MIN_STABLE_CENTROID_N,
            "min_covariance_n": MIN_COV_N,
            "sources": sources,
        },
        "role_runs": sorted({p["role_or_run"] for p in points}),
        "points": points,
        "centroids": centroids,
        "membership_counts": counts,
        "ellipses": ellipses,
    }
    (OUT / "activation_cloud_layered_viewer_data.json").write_text(json.dumps(data, indent=2))
    write_csv(OUT / "activation_cloud_layered_centroids.csv", centroids)
    write_csv(OUT / "activation_cloud_layered_membership_counts.csv", counts)


def build_html() -> None:
    data_text = (OUT / "activation_cloud_layered_viewer_data.json").read_text()
    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Layered Activation Cloud Viewer</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root {{ --bg:#f4efe5; --ink:#231f1a; --muted:#6f675f; --panel:#fffaf0; --line:#d6cab8; --accent:#315f72; }}
body {{ margin:0; font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--ink); }}
header {{ padding:20px 28px 10px; }}
h1 {{ margin:0 0 6px; font-size:28px; letter-spacing:-0.02em; }}
p {{ margin:0; color:var(--muted); }}
.wrap {{ display:grid; grid-template-columns:320px 1fr; gap:16px; padding:14px 24px 24px; }}
.panel {{ background:rgba(255,250,240,.92); border:1px solid var(--line); border-radius:14px; padding:14px; box-shadow:0 8px 24px rgba(60,40,20,.06); }}
label {{ display:block; font-size:13px; font-weight:650; margin:10px 0 4px; color:#3f372f; }}
select {{ width:100%; font-size:15px; padding:8px; border:1px solid var(--line); border-radius:8px; background:white; color:var(--ink); }}
.checks label {{ display:flex; align-items:center; gap:8px; font-weight:500; margin:7px 0; }}
input[type=checkbox] {{ transform:scale(1.05); }}
#plot {{ width:100%; height:76vh; min-height:620px; }}
#meta {{ margin-top:12px; font-size:13px; line-height:1.45; color:var(--muted); }}
.pill {{ display:inline-block; padding:2px 7px; margin:2px 3px 2px 0; background:#e8dfd0; border-radius:999px; color:#473f36; }}
@media (max-width: 900px) {{ .wrap {{ grid-template-columns:1fr; }} #plot {{ height:70vh; min-height:480px; }} }}
</style>
</head>
<body>
<header>
<h1>Layered Activation Cloud Viewer</h1>
<p>Published centroids, all-response clouds, GPT-4.1/GPT-5.5 judge-filtered subclouds, and data-derived centroids.</p>
</header>
<div class="wrap">
<aside class="panel">
<label for="roleRun">Role / run</label>
<select id="roleRun"></select>
<label for="projection">Projection</label>
<select id="projection">
  <option value="pc1,pc2">PC1-PC2</option>
  <option value="pc1,pc3">PC1-PC3</option>
  <option value="pc2,pc3">PC2-PC3</option>
  <option value="3d">3D</option>
</select>
<div class="checks" id="checks"></div>
<div id="meta"></div>
</aside>
<main class="panel"><div id="plot"></div></main>
</div>
<script>
const DATA = {data_text};
const layerDefs = [
  ['published_centroid','Published centroid'],
  ['all_cloud','All cloud'],
  ['all_centroid','All centroid'],
  ['gpt41_ge2_cloud','GPT-4.1 score>=2 cloud'],
  ['gpt41_ge2_centroid','GPT-4.1 score>=2 centroid'],
  ['gpt41_eq3_cloud','GPT-4.1 score==3 cloud'],
  ['gpt41_eq3_centroid','GPT-4.1 score==3 centroid'],
  ['gpt55_ge2_cloud','GPT-5.5 score>=2 cloud'],
  ['gpt55_ge2_centroid','GPT-5.5 score>=2 centroid'],
  ['gpt55_eq3_cloud','GPT-5.5 score==3 cloud'],
  ['gpt55_eq3_centroid','GPT-5.5 score==3 centroid'],
  ['ellipses','Covariance ellipses']
];
const colors = {{ all:'#9aa0a6', gpt41_ge2:'#3478a6', gpt41_eq3:'#0d4b6e', gpt55_ge2:'#d08436', gpt55_eq3:'#8f4d12', published:'#111', centroid:'#d62728' }};
const roleSel = document.getElementById('roleRun');
DATA.role_runs.forEach(r => {{ const o=document.createElement('option'); o.value=r; o.textContent=r; roleSel.appendChild(o); }});
const checks = document.getElementById('checks');
const defaults = new Set(['published_centroid','all_cloud','all_centroid','gpt41_ge2_cloud','gpt41_ge2_centroid','gpt41_eq3_centroid','ellipses']);
layerDefs.forEach(([key,label]) => {{
  const id='check_'+key;
  const lab=document.createElement('label');
  lab.innerHTML = `<input type="checkbox" id="${{id}}" ${{defaults.has(key)?'checked':''}}> ${{label}}`;
  checks.appendChild(lab);
}});
function on(key) {{ return document.getElementById('check_'+key).checked; }}
function axes() {{
  const p = document.getElementById('projection').value;
  if (p === '3d') return ['pc1','pc2','pc3'];
  return p.split(',');
}}
function layerPoints(points, layer) {{
  if (layer === 'all') return points;
  if (layer === 'gpt41_ge2') return points.filter(p => p.gpt41_score !== null && p.gpt41_score >= 2);
  if (layer === 'gpt41_eq3') return points.filter(p => p.gpt41_score === 3);
  if (layer === 'gpt55_ge2') return points.filter(p => p.gpt55_score !== null && p.gpt55_score >= 2);
  if (layer === 'gpt55_eq3') return points.filter(p => p.gpt55_score === 3);
  return [];
}}
function centroidTrace(c, proj, name, color, symbol) {{
  const text = `${{c.layer_label}}<br>n=${{c.n || 'published'}}<br>dist=${{Number(c.distance_to_published_centroid||0).toFixed(3)}}<br>${{c.sparse_warning||''}}`;
  if (proj === '3d') return {{ type:'scatter3d', mode:'markers', name, x:[c.pc1], y:[c.pc2], z:[c.pc3], text:[text], marker:{{ size:9, color, symbol }}, hovertemplate:'%{{text}}<extra></extra>' }};
  const [xk,yk]=axes();
  return {{ type:'scatter', mode:'markers', name, x:[c[xk]], y:[c[yk]], text:[text], marker:{{ size:14, color, symbol, line:{{ color:'#111', width:1 }} }}, hovertemplate:'%{{text}}<extra></extra>' }};
}}
function cloudTrace(points, layer, proj, name, color) {{
  const text = points.map(p => `${{p.role_or_run}}<br>${{p.response_id}}<br>GPT-4.1=${{p.gpt41_score ?? 'NA'}} GPT-5.5=${{p.gpt55_score ?? 'NA'}}<br>instruction=${{p.instruction_id}} question=${{p.question_id}}<br>dist=${{Number(p.distance_to_published_centroid).toFixed(3)}}<br>${{p.response_text_excerpt}}`);
  if (proj === '3d') return {{ type:'scatter3d', mode:'markers', name, x:points.map(p=>p.pc1), y:points.map(p=>p.pc2), z:points.map(p=>p.pc3), text, marker:{{ size:4, color, opacity:.55 }}, hovertemplate:'%{{text}}<extra></extra>' }};
  const [xk,yk]=axes();
  return {{ type:'scatter', mode:'markers', name, x:points.map(p=>p[xk]), y:points.map(p=>p[yk]), text, marker:{{ size:7, color, opacity:.5, line:{{ width:.2, color:'#222' }} }}, hovertemplate:'%{{text}}<extra></extra>' }};
}}
function draw() {{
  const role = roleSel.value;
  const proj = document.getElementById('projection').value;
  const pts = DATA.points.filter(p => p.role_or_run === role);
  const cents = DATA.centroids.filter(c => c.role_or_run === role);
  const traces = [];
  if (on('all_cloud')) traces.push(cloudTrace(layerPoints(pts,'all'), 'all', proj, 'all cloud', colors.all));
  if (on('gpt41_ge2_cloud')) traces.push(cloudTrace(layerPoints(pts,'gpt41_ge2'), 'gpt41_ge2', proj, 'GPT-4.1 >=2 cloud', colors.gpt41_ge2));
  if (on('gpt41_eq3_cloud')) traces.push(cloudTrace(layerPoints(pts,'gpt41_eq3'), 'gpt41_eq3', proj, 'GPT-4.1 ==3 cloud', colors.gpt41_eq3));
  if (on('gpt55_ge2_cloud')) traces.push(cloudTrace(layerPoints(pts,'gpt55_ge2'), 'gpt55_ge2', proj, 'GPT-5.5 >=2 cloud', colors.gpt55_ge2));
  if (on('gpt55_eq3_cloud')) traces.push(cloudTrace(layerPoints(pts,'gpt55_eq3'), 'gpt55_eq3', proj, 'GPT-5.5 ==3 cloud', colors.gpt55_eq3));
  const centroidMap = new Map(cents.map(c => [c.layer_key, c]));
  if (on('published_centroid') && centroidMap.has('published')) traces.push(centroidTrace(centroidMap.get('published'), proj, 'published centroid', colors.published, 'diamond'));
  if (on('all_centroid') && centroidMap.has('all')) traces.push(centroidTrace(centroidMap.get('all'), proj, 'all centroid', '#555', 'circle'));
  if (on('gpt41_ge2_centroid') && centroidMap.has('gpt41_ge2')) traces.push(centroidTrace(centroidMap.get('gpt41_ge2'), proj, 'GPT-4.1 >=2 centroid', colors.gpt41_ge2, 'square'));
  if (on('gpt41_eq3_centroid') && centroidMap.has('gpt41_eq3')) traces.push(centroidTrace(centroidMap.get('gpt41_eq3'), proj, 'GPT-4.1 ==3 centroid', colors.gpt41_eq3, 'star'));
  if (on('gpt55_ge2_centroid') && centroidMap.has('gpt55_ge2')) traces.push(centroidTrace(centroidMap.get('gpt55_ge2'), proj, 'GPT-5.5 >=2 centroid', colors.gpt55_ge2, 'square'));
  if (on('gpt55_eq3_centroid') && centroidMap.has('gpt55_eq3')) traces.push(centroidTrace(centroidMap.get('gpt55_eq3'), proj, 'GPT-5.5 ==3 centroid', colors.gpt55_eq3, 'star'));
  if (on('ellipses') && proj !== '3d') {{
    const ellipseKey = {{'pc1,pc2':'pc1_pc2','pc1,pc3':'pc1_pc3','pc2,pc3':'pc2_pc3'}}[document.getElementById('projection').value];
    for (const key in DATA.ellipses) {{
      const e = DATA.ellipses[key]; if (e.role_or_run !== role) continue;
      const pts2 = e.points[ellipseKey]; if (!pts2) continue;
      traces.push({{ type:'scatter', mode:'lines', name:`ellipse ${{e.layer_label}}`, x:pts2.map(p=>p[0]), y:pts2.map(p=>p[1]), line:{{ color:e.layer_key==='all'?'#666':(e.layer_key.includes('gpt55')?colors.gpt55_eq3:colors.gpt41_eq3), width:1.5, dash:e.layer_key==='all'?'dot':'solid' }}, hoverinfo:'skip' }});
    }}
  }}
  const layout = proj === '3d'
    ? {{ scene:{{ xaxis:{{title:'PC1'}}, yaxis:{{title:'PC2'}}, zaxis:{{title:'PC3'}} }}, margin:{{l:0,r:0,t:10,b:0}}, paper_bgcolor:'#fffaf0' }}
    : {{ xaxis:{{title:axes()[0].toUpperCase(), zeroline:false}}, yaxis:{{title:axes()[1].toUpperCase(), zeroline:false, scaleanchor:null}}, margin:{{l:60,r:20,t:20,b:55}}, paper_bgcolor:'#fffaf0', plot_bgcolor:'#fffdf7', hovermode:'closest' }};
  Plotly.newPlot('plot', traces, layout, {{responsive:true}});
  const counts = DATA.membership_counts.filter(c => c.role_or_run === role);
  document.getElementById('meta').innerHTML = counts.map(c => `<span class="pill">${{c.layer_label}}: ${{c.point_count}}${{c.sparse_warning?' · '+c.sparse_warning:''}}</span>`).join(' ');
}}
roleSel.onchange = draw;
document.getElementById('projection').onchange = draw;
layerDefs.forEach(([key]) => document.getElementById('check_'+key).onchange = draw);
draw();
</script>
</body>
</html>
"""
    (OUT / "activation_cloud_layered_viewer.html").write_text(html_text)


def plot_panel(ax: Any, points: list[dict[str, Any]], centroids: list[dict[str, Any]], role_runs: list[str], title: str) -> None:
    palette = {
        "amateur": "#2b6cb0",
        "playwright": "#c05621",
        "trickster_phase1_1200": "#7b2cbf",
        "editor_phase1_128": "#2f855a",
        "editor_matched64_1024": "#718096",
    }
    for role_run in role_runs:
        pts = [p for p in points if p["role_or_run"] == role_run]
        if not pts:
            continue
        ax.scatter([p["pc1"] for p in pts], [p["pc2"] for p in pts], s=14, alpha=0.35, label=f"{role_run} cloud", color=palette.get(role_run))
        for layer_key, marker, size in [("published", "D", 70), ("all", "o", 64), ("gpt41_ge2", "s", 60), ("gpt41_eq3", "*", 110)]:
            match = [c for c in centroids if c["role_or_run"] == role_run and c["layer_key"] == layer_key]
            if match:
                c = match[0]
                ax.scatter(c["pc1"], c["pc2"], marker=marker, s=size, edgecolor="black", linewidth=0.6, color=palette.get(role_run), label=f"{role_run} {layer_key}")
    ax.axhline(0, color="#ddd", lw=0.8)
    ax.axvline(0, color="#ddd", lw=0.8)
    ax.set_title(title)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend(fontsize=6, loc="best", ncol=1)


def static_summary(points: list[dict[str, Any]], centroids: list[dict[str, Any]]) -> None:
    fig = plt.figure(figsize=(16, 11))
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])
    plot_panel(ax1, points, centroids, ["amateur", "playwright"], "A100 response clouds: amateur / playwright")
    plot_panel(ax2, points, centroids, ["trickster_phase1_1200", "editor_phase1_128", "editor_matched64_1024"], "Recovered adaptive clouds: trickster / editor")
    centroid_rows = [c for c in centroids if c["centroid_type"] == "computed"]
    labels = [f"{c['role_or_run']}\\n{c['layer_key']}" for c in centroid_rows]
    vals = [c["distance_to_published_centroid"] for c in centroid_rows]
    colors = ["#3478a6" if "gpt41" in c["layer_key"] else "#d08436" if "gpt55" in c["layer_key"] else "#777" for c in centroid_rows]
    ax3.bar(range(len(vals)), vals, color=colors)
    ax3.set_ylabel("Centroid distance to published role vector")
    ax3.set_title("Centroid alignment across available layers")
    ax3.set_xticks(range(len(vals)))
    ax3.set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / "activation_cloud_layered_static_summary.png", dpi=180)
    plt.close(fig)


def write_report(points: list[dict[str, Any]], centroids: list[dict[str, Any]], counts: list[dict[str, Any]], sources: dict[str, Any]) -> None:
    role_runs = sorted({p["role_or_run"] for p in points})
    judge_models = []
    for role_run in role_runs:
        pts = [p for p in points if p["role_or_run"] == role_run]
        judge_models.append(
            {
                "role_or_run": role_run,
                "gpt41_available": any(p["gpt41_score"] is not None for p in pts),
                "gpt55_available": any(p["gpt55_score"] is not None for p in pts),
            }
        )
    sparse = [c for c in counts if c["sparse_warning"]]
    table_counts = "\n".join(
        f"| {c['role_or_run']} | {c['layer_label']} | {c['point_count']} | {c['sparse_warning']} |"
        for c in counts
    )
    table_judges = "\n".join(
        f"| {j['role_or_run']} | {j['gpt41_available']} | {j['gpt55_available']} |" for j in judge_models
    )
    source_lines = "\n".join(f"- `{v}`" for v in sources.values() if v)
    sparse_lines = "\n".join(f"- `{c['role_or_run']}` / {c['layer_label']}: {c['sparse_warning']}" for c in sparse) or "- None"
    report = f"""# Activation Cloud Layered Viewer Report

Startup status: **STARTUP VERIFIED**.

## Source Files Used

{source_lines}

## Available Roles/Runs

{', '.join(f'`{r}`' for r in role_runs)}

## Available Judge Models

| role/run | GPT-4.1 | GPT-5.5 |
|---|---:|---:|
{table_judges}

## Layer Counts

| role/run | layer | n | warning |
|---|---|---:|---|
{table_counts}

## Centroid Counts

Centroids are computed for each available non-empty layer. Published centroids are included separately for each role/run. Computed centroids with n < {MIN_STABLE_CENTROID_N} are shown but marked sparse.

## Sparse-Layer Warnings

{sparse_lines}

Sparse editor score==3 layers should be used as visual reference points only, not as stable centroid estimates.

## Viewer

Viewer path: `research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer.html`

Local open instructions:

```bash
open research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer.html
```

The viewer has role/run and projection selectors, toggleable layers for published centroids, all-response clouds, GPT-4.1 layers, GPT-5.5 layers when available, and covariance ellipses where n is sufficient.

## Main Geometry Viewer

The main persona geometry explorer was **not modified**. This task created a new standalone layered activation-cloud viewer.
"""
    (OUT / "activation_cloud_layered_viewer_report.md").write_text(report)


def main() -> None:
    points, sources = normalize_points()
    centroids, counts, ellipses = compute_centroids(points)
    write_data(points, centroids, counts, ellipses, sources)
    build_html()
    static_summary(points, centroids)
    write_report(points, centroids, counts, sources)
    print(f"wrote {len(points)} points, {len(centroids)} centroid rows, {len(counts)} count rows")


if __name__ == "__main__":
    main()
