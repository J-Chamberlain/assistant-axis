#!/usr/bin/env python3
"""Build self-contained Qwen/Llama/Gemma PC-ranked trait ridge profiles."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
from scipy.interpolate import PchipInterpolator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/outputs"))
from multimodel_trait_viewer_data import MODEL_ORDER, load_multimodel_traits  # noqa: E402

DEFINITIONS = ROOT / "data/traits/trait_list.json"
AUDIT = ROOT / "research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md"
ESTABLISHED_SCRIPT = ROOT / (
    "research/outputs/multimodel_ordered_trait_region_viewer/"
    "run_multimodel_ordered_trait_region_viewer.py"
)
ESTABLISHED_DATA = ROOT / (
    "research/outputs/multimodel_ordered_trait_region_viewer/"
    "multimodel_ordered_trait_region_data.json"
)
BIG_FIVE_DATA = ROOT / "research/outputs/externally_anchored_big_five/big_five_viewer_data.json"
QWEN_REFERENCE_COMMIT = "d68921b898ed179194223f449149d715298cdabe"

# Editorial coverage groups chosen from descriptions, not fitted to PC correlations.
GROUPS = [
    ("Exploration", "#b4a5d0", ["creative", "abstract", "curious"]),
    ("Response", "#dbb77c", ["reactive", "adaptable", "practical"]),
    ("Scrutiny", "#91b6d0", ["skeptical", "analytical", "conscientious"]),
    ("Challenge", "#d99a87", ["rebellious", "competitive", "manipulative"]),
    ("Affiliation", "#8bc5c0", ["empathetic", "agreeable", "altruistic"]),
]
KEYS = [key for _, _, keys in GROUPS for key in keys]
X = np.linspace(14, 436, len(KEYS))
GRID = np.linspace(X[0], X[-1], 211)
BASE, AMP, ROW, WIDTH = 36, 30, 44, 450
BIG_FIVE_COLORS = ["#8f7cc3", "#6ea58d", "#d09b62", "#83a9ca", "#c77989"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(name: str, data: object) -> None:
    (HERE / name).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def save_csv(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", newline="") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=list(rows[0]),
            lineterminator="\n" if name == "artifact_inventory.csv" else "\r\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def git_json(commit: str, path: str) -> dict[str, object]:
    content = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True)
    return json.loads(content)


def qwen_reproduction(model: dict[str, object], categories: list[dict[str, object]], commit: str) -> dict[str, float]:
    previous = git_json(
        commit, "research/outputs/persona_trait_ridge_plots/persona_trait_ridge_data.json"
    )
    if model["personas"] != previous["personas"]:
        raise ValueError("Qwen persona order drifted from the compatibility artifact")
    if categories != previous["categories"]:
        raise ValueError("Qwen displayed trait definitions drifted from the compatibility artifact")
    if model["orders"] != previous["orders"]:
        raise ValueError("Qwen PC order drifted from the compatibility artifact")
    result: dict[str, float] = {}
    for current_key, previous_key in [
        ("coordinates", "coordinates"),
        ("raw_affinity", "raw_affinity"),
        ("z_score", "z_score"),
        ("height_percentile", "height_percentile"),
    ]:
        current = np.asarray(model[current_key], dtype=np.float64)
        old = np.asarray(previous[previous_key], dtype=np.float64)
        result[f"max_abs_{current_key}_difference"] = float(np.max(np.abs(current - old)))
    if any(value != 0 for value in result.values()):
        raise ValueError(f"Qwen compatibility drift detected: {result}")
    return result


def curves(model: dict[str, object]) -> np.ndarray:
    percentiles = np.asarray(model["height_percentile"], dtype=np.float64)
    result = np.stack([PchipInterpolator(X, row)(GRID) for row in percentiles])
    if np.any(result < percentiles.min(1)[:, None] - 1e-9):
        raise ValueError("PCHIP curve undershot an exact trait node")
    if np.any(result > percentiles.max(1)[:, None] + 1e-9):
        raise ValueError("PCHIP curve overshot an exact trait node")
    return result


def ridge(index: int, model: dict[str, object], curve_values: np.ndarray) -> str:
    names = model["personas"]
    raw = np.asarray(model["raw_affinity"])
    z_score = np.asarray(model["z_score"])
    percentiles = np.asarray(model["height_percentile"])
    y = BASE - curve_values[index] * AMP / 100
    line = "M" + " L".join(f"{x:.2f},{yy:.2f}" for x, yy in zip(GRID, y))
    area = f"M{GRID[0]},{BASE} L" + line[1:] + f" L{GRID[-1]},{BASE} Z"
    parts = [
        f'<path d="{area}" fill="#b6c1c8" fill-opacity=".20"/>',
        f'<path d="M14,{BASE}H436" stroke="#45474a" stroke-width=".5"/>',
    ]
    for trait_index in [3, 6, 9, 12]:
        midpoint = (X[trait_index - 1] + X[trait_index]) / 2
        parts.append(
            f'<path d="M{midpoint:.2f},3V36" stroke="#6b6e70" '
            'stroke-dasharray="2 3" stroke-width=".5"/>'
        )
    parts.append(f'<path d="{line}" stroke="#d4dadd" stroke-width="1.05" fill="none"/>')
    for trait_index, key in enumerate(KEYS):
        tip = (
            f"{names[index]} | {key} | percentile {percentiles[index, trait_index]:.2f}/100 | "
            f"z {z_score[index, trait_index]:+.3f} | cosine {raw[index, trait_index]:+.6f}"
        )
        parts.append(
            f'<circle cx="{X[trait_index]:.3f}" '
            f'cy="{BASE-percentiles[index, trait_index]*AMP/100:.3f}" r="2" '
            f'fill="{GROUPS[trait_index//3][1]}"><title>{html.escape(tip)}</title></circle>'
        )
    return "".join(parts)


def svg_panel(
    model: dict[str, object], curve_values: np.ndarray, order: list[int], axis: int, limit: int | None = None
) -> str:
    names = model["personas"]
    coordinates = np.asarray(model["coordinates"])
    chosen = order if limit is None else order[:limit]
    height, width, gx, gw = 220 + ROW * len(chosen) + 60, 1000, 226, 720
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">',
        f'<title>{model["short_label"]} trait profiles in descending PC{axis+1} order</title>',
        f'<rect width="{width}" height="{height}" fill="#111315"/>',
        '<g font-family="DejaVu Sans, sans-serif" fill="#e8e8e8">',
        f'<text x="24" y="34" font-size="24">{model["short_label"]} PC{axis+1} / trait profiles</text>',
        f'<text x="24" y="59" font-size="12" fill="#aaa6a0">{len(chosen)} of 275 personas; '
        'highest first. Height = within-model, within-trait percentile (0-100).</text>',
    ]
    for trait_index, key in enumerate(KEYS):
        xx = gx + X[trait_index] / WIDTH * gw
        parts.append(
            f'<text transform="translate({xx:.3f},191) rotate(-56)" font-size="12">{key.capitalize()}</text>'
        )
    for group_index, (label, color, _) in enumerate(GROUPS):
        xx = gx + X[group_index * 3 + 1] / WIDTH * gw
        parts.append(
            f'<text x="{xx:.3f}" y="90" font-size="12" text-anchor="middle" fill="{color}">{label}</text>'
        )
    for rank, index in enumerate(chosen, 1):
        yy = 205 + (rank - 1) * ROW
        if rank % 2 == 0:
            parts.append(f'<rect y="{yy}" width="1000" height="44" fill="#1b1e20"/>')
        parts += [
            f'<text x="24" y="{yy+18}" font-size="13">{rank:03d}  '
            f'{html.escape(names[index].replace("_", " "))}</text>',
            f'<text x="24" y="{yy+33}" font-size="10" fill="#aaa6a0">'
            f'PC{axis+1} {coordinates[index, axis]:+.3f}</text>',
            f'<g transform="translate({gx},{yy}) scale({gw/WIDTH},1)">'
            f'{ridge(index, model, curve_values)}</g>',
        ]
    parts += [
        f'<text x="24" y="{height-30}" font-size="11" fill="#aaa6a0">15 of 240 mapped traits; '
        'editorial groups, not a valence scale or fitted factors.</text>',
        f'<text x="24" y="{height-12}" font-size="11" fill="#aaa6a0">Same-space activation '
        'cosines; percentiles are within-model ranks. Curves are not probability densities.</text>',
        "</g></svg>",
    ]
    return "".join(parts)


def model_panels(model_key: str, model: dict[str, object], curve_values: np.ndarray) -> str:
    coordinates = np.asarray(model["coordinates"])
    names = model["personas"]
    panels = []
    category_head = "".join(
        f'<span style="left:{X[index]/WIDTH*100:.4f}%">{key.capitalize()}</span>'
        for index, key in enumerate(KEYS)
    )
    group_head = "".join(
        f'<span style="left:{X[index*3+1]/WIDTH*100:.4f}%;color:{color}">{label}</span>'
        for index, (label, color, _) in enumerate(GROUPS)
    )
    for axis, order in enumerate(model["orders"]):
        rows = []
        for rank, index in enumerate(order, 1):
            rows.append(
                f'<div class="ridge-row" data-model="{model_key}" data-axis="{axis+1}" '
                f'data-profile-set="editorial" data-construction="" '
                f'data-persona="{html.escape(names[index])}" data-rank="{rank}" '
                f'data-pc="{coordinates[index, axis]:.15g}">'
                f'<button class="name" type="button" data-name="{html.escape(names[index])}">'
                f'<small>{rank:03d} / PC{axis+1} {coordinates[index, axis]:+.2f}</small>'
                f'{html.escape(names[index].replace("_", " "))}</button>'
                f'<svg class="ridge" viewBox="0 0 450 44" preserveAspectRatio="none" role="img" '
                f'aria-label="{html.escape(names[index])} {model["short_label"]} trait-affinity percentile profile">'
                f'{ridge(index, model, curve_values)}</svg></div>'
            )
        panels.append(
            f'<section class="panel"><header><h2>PC{axis+1}</h2>'
            f'<p>Highest first: {coordinates[order[0], axis]:+.2f} to {coordinates[order[-1], axis]:+.2f}</p>'
            f'<a href="persona_trait_ridges_{model_key}_pc{axis+1}.svg">Full SVG</a> / '
            f'<a href="persona_trait_ridges_{model_key}_pc{axis+1}.png">Full PNG</a></header>'
            f'<div class="rows" aria-label="All 275 {model["short_label"]} personas in descending PC{axis+1} order">'
            f'<div class="chart-head"><div class="axis"><span>Rank / persona</span>'
            f'<div class="categories">{category_head}</div></div><div class="family-axis"><span></span>'
            f'<div class="families">{group_head}</div></div></div>{"".join(rows)}</div>'
            '<footer>275 / 275 personas; scroll this plot</footer></section>'
        )
    hidden = "" if model_key == "qwen" else " hidden"
    return (
        f'<div class="model-view" data-model-view="{model_key}" data-profile-set="editorial" data-construction=""{hidden}>'
        f'{"".join(panels)}</div>'
    )


def big_five_ridge(index: int, raw: np.ndarray, percentiles: np.ndarray, labels: list[str]) -> str:
    x_values = np.linspace(20, 430, len(labels))
    grid = np.linspace(x_values[0], x_values[-1], 181)
    curve = PchipInterpolator(x_values, percentiles[index])(grid)
    y = BASE - curve * AMP / 100
    line = "M" + " L".join(f"{x:.2f},{yy:.2f}" for x, yy in zip(grid, y))
    area = f"M{grid[0]},{BASE} L" + line[1:] + f" L{grid[-1]},{BASE} Z"
    parts = [
        f'<path d="{area}" fill="#b6c1c8" fill-opacity=".20"/>',
        f'<path d="M20,{BASE}H430" stroke="#45474a" stroke-width=".5"/>',
        f'<path d="{line}" stroke="#d4dadd" stroke-width="1.05" fill="none"/>',
    ]
    for domain_index, label in enumerate(labels):
        tip = f"{label} | percentile {percentiles[index, domain_index]:.2f}/100 | raw projection {raw[index, domain_index]:+.6f}"
        parts.append(
            f'<circle cx="{x_values[domain_index]:.3f}" cy="{BASE-percentiles[index, domain_index]*AMP/100:.3f}" '
            f'r="2.4" fill="{BIG_FIVE_COLORS[domain_index]}"><title>{html.escape(tip)}</title></circle>'
        )
    return "".join(parts)


def big_five_model_panels(model_key: str, payload: dict[str, object], construction_key: str) -> str:
    model = payload["models"][model_key]
    construction = model["constructions"][construction_key]
    names = model["personas"]
    coordinates = np.asarray(model["coordinates"], dtype=float)
    domains = construction["domains"]
    labels = [domain["label"] for domain in domains]
    raw = np.asarray([domain["raw_score"] for domain in domains], dtype=float).T
    percentile = np.asarray([domain["height_percentile"] for domain in domains], dtype=float).T
    x_values = np.linspace(20, 430, len(labels))
    category_head = "".join(
        f'<span style="left:{x_values[index]/WIDTH*100:.4f}%;color:{BIG_FIVE_COLORS[index]}">{label}</span>'
        for index, label in enumerate(labels)
    )
    panels = []
    for axis, order in enumerate(model["orders"]):
        rows = []
        for rank, index in enumerate(order, 1):
            rows.append(
                f'<div class="ridge-row" data-model="{model_key}" data-axis="{axis+1}" data-profile-set="big_five" '
                f'data-construction="{construction_key}" data-persona="{html.escape(names[index])}" data-rank="{rank}" '
                f'data-pc="{coordinates[index, axis]:.15g}"><button class="name" type="button" data-name="{html.escape(names[index])}">'
                f'<small>{rank:03d} / PC{axis+1} {coordinates[index, axis]:+.2f}</small>{html.escape(names[index].replace("_", " "))}</button>'
                f'<svg class="ridge" viewBox="0 0 450 44" preserveAspectRatio="none" role="img" '
                f'aria-label="{html.escape(names[index])} {construction["label"]} Big Five percentile profile">'
                f'{big_five_ridge(index, raw, percentile, labels)}</svg></div>'
            )
        panels.append(
            f'<section class="panel"><header><h2>PC{axis+1}</h2><p>Highest first: '
            f'{coordinates[order[0],axis]:+.2f} to {coordinates[order[-1],axis]:+.2f}</p>'
            f'<p>{construction["label"]} activation-derived Big Five</p></header>'
            f'<div class="rows"><div class="chart-head"><div class="axis"><span>Rank / persona</span>'
            f'<div class="categories big-five-head">{category_head}</div></div></div>{"".join(rows)}</div>'
            '<footer>275 / 275 personas; raw composite projection retained in hover</footer></section>'
        )
    return (
        f'<div class="model-view" data-model-view="{model_key}" data-profile-set="big_five" '
        f'data-construction="{construction_key}" hidden>{"".join(panels)}</div>'
    )


def make_html(models: dict[str, dict[str, object]], model_curves: dict[str, np.ndarray], big_five: dict[str, object]) -> str:
    names = models["qwen"]["personas"]
    options = "".join(
        f'<option value="{html.escape(name)}">{html.escape(name.replace("_", " "))}</option>'
        for name in sorted(names)
    )
    model_options = "".join(
        f'<option value="{key}"{(" selected" if key == "qwen" else "")}>{models[key]["short_label"]}</option>'
        for key in MODEL_ORDER
    )
    editorial_views = "".join(model_panels(key, models[key], model_curves[key]) for key in MODEL_ORDER)
    views = editorial_views + '<div id="big-five-view" hidden></div>'
    construction_options = "".join(
        f'<option value="{key}">{big_five["construction_labels"][key]}</option>'
        for key in big_five["construction_order"]
    )
    big_five_json = json.dumps(big_five, separators=(",", ":")).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Persona trait ridges | Qwen, Llama, Gemma</title><style>
:root{{color-scheme:dark;--bg:#0d0d0d;--panel:#151515;--text:#e8e8e8;--muted:#aaa6a0;--line:#303234;--accent:#8bc5c0}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:13px/1.5 Menlo,Consolas,monospace}}
.intro{{padding:24px 26px 15px;border-bottom:1px solid var(--line)}}.eyebrow{{color:var(--accent);font-size:11px;letter-spacing:1.6px;text-transform:uppercase}}
h1{{font-size:26px;font-weight:400;margin:4px 0 8px;letter-spacing:-.6px}}p{{color:var(--muted);margin:4px 0}}a{{color:var(--accent);text-underline-offset:3px}}
.controls{{padding:12px 26px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
select,button{{font:inherit}}select,.controls button{{background:var(--panel);border:1px solid #555;color:var(--text);padding:7px;max-width:100%}}.scale{{margin-left:auto;font-size:11px;color:var(--muted)}}
.model-view{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;padding:20px 26px}}.model-view[hidden]{{display:none}}.panel{{min-width:0;background:var(--panel);border:1px solid var(--line)}}
.panel header{{padding:12px}}h2{{font-size:21px;font-weight:400;margin:0}}.panel header p,.panel header a{{font-size:11px}}
.rows{{height:68vh;min-height:390px;overflow:auto;scrollbar-gutter:stable;border-top:1px solid var(--line)}}
.chart-head{{position:sticky;top:0;z-index:2;background:var(--panel);border-bottom:1px solid var(--line)}}
.axis,.family-axis,.ridge-row{{display:grid;grid-template-columns:128px minmax(0,1fr);padding:0 10px;min-width:630px}}
.axis{{height:132px;align-items:end;color:var(--muted);font-size:11px;padding-bottom:6px}}.categories{{height:122px;position:relative}}.categories span{{position:absolute;bottom:0;transform:rotate(-64deg);transform-origin:left bottom;white-space:nowrap;font-size:11px}}
.families{{height:23px;position:relative}}.families span{{position:absolute;transform:translateX(-50%);font-size:10px;white-space:nowrap}}
.ridge-row{{height:44px;align-items:center;border-bottom:1px solid #242627}}.ridge-row:nth-child(even){{background:#17191a}}.ridge{{width:100%;height:44px;overflow:visible}}
.name{{color:var(--text);background:none;border:0;text-align:left;cursor:pointer;line-height:1.3;font-size:11px;padding:2px 5px 2px 0;overflow-wrap:anywhere}}.name small{{display:block;color:var(--muted);font-size:9px;margin-bottom:2px}}
.ridge-row.selected{{background:#233432;outline:1px solid var(--accent);outline-offset:-1px}}.name:focus-visible{{outline:2px solid var(--accent)}}
footer{{color:var(--muted);font-size:10px;padding:7px 12px}}.notes{{padding:0 26px 24px;max-width:1200px}}.notes p{{font-size:12px;margin:10px 0}}.notes summary{{cursor:pointer}}#selection-status{{color:var(--accent);font-size:11px}}#model-provenance{{font-size:11px;color:var(--accent)}}#big-five-details{{padding:10px 26px;border-bottom:1px solid var(--line);color:var(--muted);font-size:11px}}#big-five-details[hidden]{{display:none}}.big-five-head span{{transform:rotate(-42deg)}}
@media(max-width:2050px){{.model-view{{grid-template-columns:1fr}}.rows{{height:65vh}}.axis,.family-axis,.ridge-row{{grid-template-columns:190px minmax(0,1fr);min-width:690px}}.categories span{{font-size:12px;transform:rotate(-50deg)}}.name{{font-size:13px}}.name small{{font-size:10px}}.families span{{font-size:12px}}}}
@media(max-width:760px){{.intro,.controls{{padding:15px}}.model-view{{padding:15px}}.scale{{margin-left:0}}.notes{{padding:0 15px 20px}}.axis,.family-axis,.ridge-row{{grid-template-columns:130px minmax(0,1fr);min-width:650px}}.families span{{font-size:10px}}.categories span{{font-size:11px;transform:rotate(-64deg)}}.name{{font-size:11px}}.name small{{font-size:9px}}}}
@media print{{.model-view{{display:block}}.rows{{height:auto;overflow:visible}}.panel{{break-after:page}}.controls{{display:none}}.chart-head{{position:static}}}}
</style></head><body><div class="intro"><div class="eyebrow">Persona geometry / <span id="active-model-name">Qwen</span> / <span id="active-profile-name">15 editorial traits</span></div>
<h1>Trait profiles, ordered through PC space</h1><p>All 275 personas, greatest to smallest PC1, PC2 or PC3. The selected model supplies both its own coordinates and its own trait scores.</p>
<p id="profile-description">Left to right: exploration, response, scrutiny, challenge, affiliation. These are editorial reading groups, not fitted latent factors.</p><p id="model-provenance">Qwen uses canonical geometry_viz_data coordinates and exact saved Qwen trait cosines.</p></div>
<div class="controls"><label for="model-select">Model</label><select id="model-select">{model_options}</select>
<label for="profile-set-select">Profile set</label><select id="profile-set-select"><option value="editorial" selected>Editorial traits</option><option value="big_five">Big Five</option></select>
<label for="construction-select">Big Five construction</label><select id="construction-select" disabled>{construction_options}</select>
<label for="find-persona">Locate the same persona in all three plots</label><select id="find-persona"><option value="">Choose a persona</option>{options}</select>
<button id="reset-view" type="button">Reset</button><span class="scale">Height: 0-100 within-model, within-trait percentile</span><div id="selection-status" role="status" aria-live="polite"></div></div>
<div id="big-five-details" hidden></div>
<noscript><p class="notes">The default Qwen plots are already rendered. Model switching and linked selection need JavaScript.</p></noscript>
<main id="plots">{views}</main>
<div class="notes"><p>Scroll each plot to see every persona; on narrow screens, scroll sideways to see all 15 trait labels. Hover a category dot for its raw cosine, z-score and within-model percentile.</p>
<details><summary>Reading the profiles and their provenance</summary>
<p>Each height compares one persona with the selected model's 275 personas for that trait. A value of 80 is approximately the 80th percentile within that model, not 80% trait intensity. Equal percentiles in different models express equal rank concepts, not equal absolute cosines or identical psychological semantics.</p>
<p>The 15 traits are the unchanged editorial coverage sample of 240 released trait directions. Five colored groups provide navigation; they are not fitted clusters, valence signs, PCA directions, or validated psychological factors. Smooth non-overshooting connectors are visual aids, not a measured continuum or probability distribution.</p>
<p>Qwen retains the canonical saved 275-by-240 cosine matrix exactly. Llama and Gemma use their own released role and trait vectors. Qwen keeps canonical geometry coordinates; Llama and Gemma PCA coordinates are recomputed from their own layer-mean role vectors and sign-oriented to the corresponding Qwen PCs with the established project procedure.</p>
<p>Big Five mode uses frozen externally anchored activation directions and within-model role-score percentiles. External anchoring does not make these independent human psychometric ratings. Model selection does not establish identical psychological semantics across models.</p>
<p><a href="persona_trait_ridge_methodology.md">Methodology and complete trait definitions</a> / <a href="persona_trait_ridge_scores.csv" download>All 12,375 model/persona/trait scores</a> / <a href="../persona_trait_surface_viewer/persona_trait_surface_viewer.html">Grouped trait landscapes</a></p>
</details></div><script>
(() => {{
 const modelNames={{qwen:'Qwen',llama:'Llama',gemma:'Gemma'}};
 const provenance={{qwen:'Qwen uses canonical geometry_viz_data coordinates and exact saved Qwen trait cosines.',llama:'Llama uses PCA from its own layer-mean role vectors, sign-oriented to the Qwen reference; trait ranks are within Llama.',gemma:'Gemma uses PCA from its own layer-mean role vectors, sign-oriented to the Qwen reference; trait ranks are within Gemma.'}};
 const bigFiveData={big_five_json};
 const modelSelect=document.getElementById('model-select'),profileSelect=document.getElementById('profile-set-select'),constructionSelect=document.getElementById('construction-select'),picker=document.getElementById('find-persona');
 const views=Array.from(document.querySelectorAll('[data-model-view]')),bigFiveView=document.getElementById('big-five-view');
 let model='qwen',profileSet='editorial',construction='human_anchored_strict',selected='';
 function isActive(element){{const elementModel=element.dataset.model||element.dataset.modelView;return elementModel===model&&element.dataset.profileSet===profileSet&&(profileSet==='editorial'||element.dataset.construction===construction);}}
 function activeRows(){{return Array.from(document.querySelectorAll('.ridge-row')).filter(isActive);}}
 function escapeHtml(value){{return String(value).replace(/[&<>"']/g,char=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[char]));}}
 function renderBigFive(){{
   if(profileSet!=='big_five'){{bigFiveView.hidden=true;return;}}
   const payload=bigFiveData.models[model],item=payload.constructions[construction],names=payload.personas,coords=payload.coordinates;
   const colors={json.dumps(BIG_FIVE_COLORS)},xs=[20,122.5,225,327.5,430];
   const heading=item.domains.map((domain,index)=>'<span style="left:'+(xs[index]/450*100).toFixed(4)+'%;color:'+colors[index]+'">'+escapeHtml(domain.label)+'</span>').join('');
   bigFiveView.innerHTML=payload.orders.map((order,axis)=>{{
     const rows=order.map((personaIndex,position)=>{{
       const points=item.domains.map((domain,index)=>[xs[index],36-domain.height_percentile[personaIndex]*.3]);
       const line='M'+points.map(point=>point[0].toFixed(2)+','+point[1].toFixed(2)).join(' L');
       const circles=item.domains.map((domain,index)=>{{const pct=domain.height_percentile[personaIndex],raw=domain.raw_score[personaIndex];return '<circle cx="'+xs[index]+'" cy="'+(36-pct*.3).toFixed(3)+'" r="2.4" fill="'+colors[index]+'"><title>'+escapeHtml(domain.label)+' | percentile '+pct.toFixed(2)+'/100 | raw projection '+(raw>=0?'+':'')+raw.toFixed(6)+'</title></circle>';}}).join('');
       const name=names[personaIndex],rank=position+1,pc=coords[personaIndex][axis];
       return '<div class="ridge-row" data-model="'+model+'" data-axis="'+(axis+1)+'" data-profile-set="big_five" data-construction="'+construction+'" data-persona="'+escapeHtml(name)+'" data-rank="'+rank+'" data-pc="'+pc+'"><button class="name" type="button" data-name="'+escapeHtml(name)+'"><small>'+String(rank).padStart(3,'0')+' / PC'+(axis+1)+' '+(pc>=0?'+':'')+pc.toFixed(2)+'</small>'+escapeHtml(name.replaceAll('_',' '))+'</button><svg class="ridge" viewBox="0 0 450 44" preserveAspectRatio="none" role="img" aria-label="'+escapeHtml(name)+' '+escapeHtml(item.label)+' Big Five percentile profile"><path d="M20,36 L'+line.slice(1)+' L430,36 Z" fill="#b6c1c8" fill-opacity=".20"/><path d="M20,36H430" stroke="#45474a" stroke-width=".5"/><path d="'+line+'" stroke="#d4dadd" stroke-width="1.05" fill="none"/>'+circles+'</svg></div>';
     }}).join('');
     const first=coords[order[0]][axis],last=coords[order[order.length-1]][axis];
     return '<section class="panel"><header><h2>PC'+(axis+1)+'</h2><p>Highest first: '+(first>=0?'+':'')+first.toFixed(2)+' to '+(last>=0?'+':'')+last.toFixed(2)+'</p><p>'+escapeHtml(item.label)+' activation-derived Big Five</p></header><div class="rows"><div class="chart-head"><div class="axis"><span>Rank / persona</span><div class="categories big-five-head">'+heading+'</div></div></div>'+rows+'</div><footer>275 / 275 personas; raw composite projection retained in hover</footer></section>';
   }}).join('');
   bigFiveView.dataset.modelView=model;bigFiveView.dataset.profileSet='big_five';bigFiveView.dataset.construction=construction;bigFiveView.className='model-view';bigFiveView.hidden=false;
   bigFiveView.querySelectorAll('[data-name]').forEach(button=>button.addEventListener('click',()=>select(button.dataset.name)));
 }}
 function updateDetails(){{
   const detail=document.getElementById('big-five-details');detail.hidden=profileSet!=='big_five';if(detail.hidden)return;
   const groups=bigFiveData.models[model].constructions[construction].domains;
   detail.innerHTML='<b>'+constructionSelect.options[constructionSelect.selectedIndex].text+'</b> — '+groups.map(domain=>'<b>'+domain.label+'</b>: '+domain.composition.map(item=>(item.polarity==='negative'?'−':'+')+item.trait.replaceAll('_',' ')+(item.facet?' ['+item.facet+']':'')).join(', ')).join(' · ');
 }}
 function select(name,scroll=true){{
   selected=name;
   const matches=[];
   document.querySelectorAll('.ridge-row').forEach(row=>{{const active=Boolean(name)&&isActive(row)&&row.dataset.persona===name;
     row.classList.toggle('selected',active);
     if(active){{if(scroll)row.parentElement.scrollTop=row.offsetTop-row.parentElement.offsetTop-170;matches.push(row);}}}});
   picker.value=name;
   document.getElementById('selection-status').textContent=matches.length ?
     name.replaceAll('_',' ')+' | '+matches.map(row=>'PC'+row.dataset.axis+' rank '+row.dataset.rank+'/275').join(' | ') : '';
 }}
 function setModel(next){{
   if(!modelNames[next])return;
   model=next;modelSelect.value=next;
   views.forEach(view=>view.hidden=profileSet!=='editorial'||view.dataset.modelView!==model);
   renderBigFive();
   document.getElementById('active-model-name').textContent=modelNames[model];
   document.getElementById('model-provenance').textContent=provenance[model];
   updateDetails();select(selected,true);
 }}
 function setProfileSet(next){{if(!['editorial','big_five'].includes(next))return;profileSet=next;profileSelect.value=next;constructionSelect.disabled=next!=='big_five';document.getElementById('active-profile-name').textContent=next==='editorial'?'15 editorial traits':'externally anchored Big Five';document.getElementById('profile-description').textContent=next==='editorial'?'Left to right: exploration, response, scrutiny, challenge, affiliation. These are editorial reading groups, not fitted latent factors.':'Five frozen Big Five domain composites; heights are within-model role-score percentiles and raw projections remain in hover.';setModel(model);}}
 function setConstruction(next){{if(!{json.dumps(big_five["construction_order"])}.includes(next))return;construction=next;constructionSelect.value=next;setModel(model);}}
 modelSelect.addEventListener('change',()=>setModel(modelSelect.value));
 profileSelect.addEventListener('change',()=>setProfileSet(profileSelect.value));constructionSelect.addEventListener('change',()=>setConstruction(constructionSelect.value));
 picker.addEventListener('change',()=>select(picker.value));
 document.querySelectorAll('[data-name]').forEach(button=>button.addEventListener('click',()=>select(button.dataset.name)));
 document.getElementById('reset-view').addEventListener('click',()=>{{selected='';construction='human_anchored_strict';constructionSelect.value=construction;setProfileSet('editorial');setModel('qwen');select('');}});
 window.__traitRidgeViewer={{get model(){{return model;}},get profileSet(){{return profileSet;}},get construction(){{return construction;}},get selectedPersona(){{return selected;}},setModel,setProfileSet,setConstruction,select,reset(){{selected='';construction='human_anchored_strict';constructionSelect.value=construction;setProfileSet('editorial');setModel('qwen');select('');}},activeRows}};
 setProfileSet('editorial');setModel('qwen');
}})();
</script></body></html>'''


def inventory() -> None:
    paths = sorted(path for path in HERE.iterdir() if path.is_file() and path.name != "artifact_inventory.csv")
    save_csv(
        "artifact_inventory.csv",
        [
            {
                "path": str(path.relative_to(ROOT)),
                "size_bytes": path.stat().st_size,
                "sha256": sha(path),
                "raw_github_url": (
                    "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/"
                    + str(path.relative_to(ROOT))
                ),
            }
            for path in paths
        ],
    )


def main(vector_root: str | None, qwen_reference_commit: str) -> None:
    definitions = json.loads(DEFINITIONS.read_text())
    categories = [
        {
            "position": index + 1,
            "trait": key,
            "group": GROUPS[index // 3][0],
            "color": GROUPS[index // 3][1],
            "definition": definitions[key],
        }
        for index, key in enumerate(KEYS)
    ]
    save_csv("trait_category_order.csv", categories)
    models, loading_audit = load_multimodel_traits(ROOT, vector_root, KEYS)
    qwen_differences = qwen_reproduction(models["qwen"], categories, qwen_reference_commit)
    model_curves = {key: curves(model) for key, model in models.items()}

    rows: list[dict[str, object]] = []
    for model_key in MODEL_ORDER:
        model = models[model_key]
        coordinates = np.asarray(model["coordinates"])
        raw = np.asarray(model["raw_affinity"])
        z_score = np.asarray(model["z_score"])
        percentiles = np.asarray(model["height_percentile"])
        ranks = [{index: rank + 1 for rank, index in enumerate(order)} for order in model["orders"]]
        for persona_index, persona in enumerate(model["personas"]):
            for trait_index, key in enumerate(KEYS):
                rows.append(
                    {
                        "model": model_key,
                        "model_label": model["label"],
                        "persona": persona,
                        "trait": key,
                        "group": GROUPS[trait_index // 3][0],
                        "category_position": trait_index + 1,
                        "raw_affinity": float(raw[persona_index, trait_index]),
                        "z_score": float(z_score[persona_index, trait_index]),
                        "ridge_height_percentile": float(percentiles[persona_index, trait_index]),
                        "pc1": float(coordinates[persona_index, 0]),
                        "pc2": float(coordinates[persona_index, 1]),
                        "pc3": float(coordinates[persona_index, 2]),
                        "rank_pc1": ranks[0][persona_index],
                        "rank_pc2": ranks[1][persona_index],
                        "rank_pc3": ranks[2][persona_index],
                    }
                )
    save_csv("persona_trait_ridge_scores.csv", rows)
    data = {
        "schema_version": 2,
        "default_model": "qwen",
        "model_order": MODEL_ORDER,
        "categories": categories,
        "models": models,
        "methodology": {
            "scientific_label": "same-space activation-cosine trait profiles",
            "normalization": "within-model midrank percentiles across 275 personas, independently per trait",
            "groups": "editorial reading groups, not fitted latent factors",
            "cross_model_semantics": "model selection does not establish identical psychological semantics",
            "coordinate_orientation": loading_audit["coordinate_orientation"],
        },
        # Backward-compatible Qwen aliases for consumers of the original schema.
        "personas": models["qwen"]["personas"],
        "coordinates": models["qwen"]["coordinates"],
        "raw_affinity": models["qwen"]["raw_affinity"],
        "z_score": models["qwen"]["z_score"],
        "height_percentile": models["qwen"]["height_percentile"],
        "orders": models["qwen"]["orders"],
    }
    save_json("persona_trait_ridge_data.json", data)
    big_five = json.loads(BIG_FIVE_DATA.read_text())
    (HERE / "persona_trait_ridges.html").write_text(make_html(models, model_curves, big_five))

    for model_key in MODEL_ORDER:
        model = models[model_key]
        for axis in range(3):
            content = svg_panel(model, model_curves[model_key], model["orders"][axis], axis)
            (HERE / f"persona_trait_ridges_{model_key}_pc{axis+1}.svg").write_text(content)
            if model_key == "qwen":
                (HERE / f"persona_trait_ridges_pc{axis+1}.svg").write_text(content)
        overview = ['<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="940" viewBox="0 0 3000 940">']
        for axis in range(3):
            overview.append(
                f'<g transform="translate({axis*1000},0)">'
                + svg_panel(model, model_curves[model_key], model["orders"][axis], axis, limit=15)
                + "</g>"
            )
        overview_content = "".join(overview) + "</svg>"
        (HERE / f"persona_trait_ridges_{model_key}_overview.svg").write_text(overview_content)
        if model_key == "qwen":
            (HERE / "persona_trait_ridges_overview.svg").write_text(overview_content)

    source_paths = [
        ROOT / "research/visualizations/geometry_viz_data.json",
        ROOT / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
        DEFINITIONS,
        AUDIT,
        ESTABLISHED_SCRIPT,
        ESTABLISHED_DATA,
        ROOT / "research/outputs/multimodel_trait_viewer_data.py",
        HERE / "run_persona_trait_ridges.py",
        HERE / "verify_persona_trait_ridges.py",
        HERE / "render_ridge_images.cjs",
        HERE / "persona_trait_ridge_methodology.md",
        BIG_FIVE_DATA,
    ]
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "qwen_compatibility_reference_commit": qwen_reference_commit,
        "author": "Codex / GPT-5.5",
        "default_model": "qwen",
        "models": {
            key: {
                "label": models[key]["label"],
                "role_count": models[key]["source_role_count"],
                "trait_count": models[key]["source_trait_count"],
                "coordinate_source": models[key]["coordinate_source"],
                "orientation_signs": models[key]["orientation_signs"],
                "score_source": models[key]["score_source"],
                "vector_sources": models[key]["vector_sources"],
                "established_coordinate_max_abs_difference": models[key]["established_coordinate_max_abs_difference"],
            }
            for key in MODEL_ORDER
        },
        "source_personas_per_model": 275,
        "source_traits_per_model": 240,
        "selected_traits": 15,
        "score_rows": len(rows),
        "qwen_score_rows": 4125,
        "groups": categories,
        "selection": "Unchanged editorial coverage based on saved trait descriptions; not data-optimized",
        "profile_sets": ["editorial", "big_five"],
        "big_five_constructions": big_five["construction_order"],
        "big_five_default_construction": big_five["default_construction"],
        "big_five_score_source": str(BIG_FIVE_DATA.relative_to(ROOT)),
        "normalization": "100 * (average rank - 0.5) / 275 independently for each trait and model",
        "aggregation": "Ridge heights show individual trait percentiles; no group composite in this viewer",
        "ordering": "Descending selected-model PC coordinate with persona-name tie-break",
        "curve": "PCHIP score connectors; exact dots are data; curves are not densities",
        "coordinate_orientation": loading_audit["coordinate_orientation"],
        "cross_model_caveat": loading_audit["cross_model_normalization"],
        "qwen_reproduction_max_differences": qwen_differences,
        "qwen_vector_recompute_vs_canonical_matrix_max_abs_difference": models["qwen"][
            "qwen_vector_recompute_vs_canonical_matrix_max_abs_difference"
        ],
        "gpu_used": False,
        "runpod_used": False,
        "api_calls": 0,
        "activation_generation": False,
        "new_inference": False,
        "source_files": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in source_paths
        ],
        "local_loading_audit": loading_audit,
    }
    save_json("persona_trait_ridge_manifest.json", manifest)
    print(
        json.dumps(
            {
                "models": MODEL_ORDER,
                "personas_per_model": 275,
                "source_traits_per_model": 240,
                "displayed_traits": len(KEYS),
                "score_rows": len(rows),
                "qwen_reproduction_max_differences": qwen_differences,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vector-root")
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument("--qwen-reference-commit", default=os.environ.get("QWEN_VIEWER_REFERENCE_COMMIT", QWEN_REFERENCE_COMMIT))
    arguments = parser.parse_args()
    if not arguments.inventory_only:
        main(arguments.vector_root, arguments.qwen_reference_commit)
    inventory()
