#!/usr/bin/env python3
"""Build pre-rendered PC-ranked emotion profiles using saved CPU vectors only."""
import argparse
import csv
import hashlib
import html
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.stats import rankdata
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEOMETRY = ROOT / "research/visualizations/geometry_viz_data.json"
BANK = ROOT / "research/emotions/outputs/emotion_readout_directions_qwen3_32b_full_layer48.pt"
VALENCE = ROOT / "research/emotions/outputs/qwen_valence_arousal.csv"
AXES = ROOT / "research/emotions/outputs/qwen_valence_arousal_axes.json"
OLD = ROOT / "research/outputs/persona_emotion_surface_viewer/persona_emotion_scores.csv"
LABELS = {"afraid": "Fear", "sad": "Sadness", "disgusted": "Disgust", "angry": "Anger",
          "lonely": "Loneliness", "calm": "Calm", "excited": "Excitement", "joyful": "Joy",
          "grateful": "Gratitude", "hopeful": "Hope"}
NEG = "#d99a87"
POS = "#8bc5c0"
TEXT = "#e8e8e8"
MUTED = "#aaa6a0"
X = np.linspace(14, 286, 10)
GRID = np.linspace(X[0], X[-1], 181)
BASE, AMPLITUDE, ROW = 36, 30, 44


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def save_csv(name, rows):
    with (HERE / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def norm(rows):
    norms = np.linalg.norm(rows, axis=1, keepdims=True)
    assert np.isfinite(rows).all() and np.all(norms > 1e-12)
    return rows / norms


def score():
    g = json.loads(GEOMETRY.read_text())["roles"]
    names, pcs = g["names"], np.asarray(g["pca3d"], dtype=float)
    assert len(names) == len(set(names)) == 275 and pcs.shape == (275, 3)
    bank = torch.load(BANK, map_location="cpu", weights_only=True)
    assert len(bank) == 171 and set(LABELS) <= set(bank)
    v = {r["emotion"]: r for r in csv.DictReader(VALENCE.open())}
    keys = sorted(LABELS, key=lambda k: float(v[k]["valence_raw"]))
    assert all(float(v[k]["valence_raw"]) < 0 for k in keys[:5])
    assert all(float(v[k]["valence_raw"]) > 0 for k in keys[5:])
    directions = norm(np.stack([bank[k].float().numpy().astype(float) for k in keys]))
    sources = [GEOMETRY, BANK, VALENCE, AXES, OLD,
               ROOT / "research/emotions/scripts/extract_qwen_full.py",
               ROOT / "research/emotions/scripts/compute_qwen_valence_arousal.py",
               ROOT / "research/outputs/a100_two_role_activation_cloud_pilot/boundary_test_results.json"]
    boundary = json.loads(sources[-1].read_text())
    assert boundary["conclusion"] == "hook_matches_hidden_states_49"
    role_rows = []
    for name in names:
        path = ROOT / f"downloads/hf_vectors/qwen-3-32b/role_vectors/{name}.pt"
        tensor = torch.load(path, map_location="cpu", weights_only=True)
        assert tuple(tensor.shape) == (64, 5120)
        role_rows.append(tensor[47].float().numpy().astype(float))
        sources.append(path)
    raw = norm(np.stack(role_rows)) @ directions.T
    assert np.isfinite(raw).all() and np.all(raw.std(0) > 1e-6)
    z = (raw - raw.mean(0)) / raw.std(0, ddof=0)
    pct = np.column_stack([100 * (rankdata(raw[:, e], method="average") - .5) / 275
                           for e in range(10)])
    orders = [sorted(range(275), key=lambda i: (-pcs[i, a], names[i])) for a in range(3)]
    ranks = [{i: rank + 1 for rank, i in enumerate(order)} for order in orders]
    lookup = {name: i for i, name in enumerate(names)}
    old_count, max_error = 0, 0.
    for r in csv.DictReader(OLD.open()):
        i, e = lookup[r["persona"]], keys.index(r["emotion"])
        max_error = max(max_error, abs(raw[i, e] - float(r["raw_affinity"])))
        assert np.allclose([raw[i, e], z[i, e], pct[i, e]],
                           [float(r[c]) for c in ["raw_affinity", "z_score", "percentile_midrank"]],
                           atol=1e-10, rtol=0)
        old_count += 1
    assert old_count == 1650
    # PCHIP joins categorical values without inventing overshooting peaks.
    curves = np.stack([PchipInterpolator(X, row)(GRID) for row in pct])
    assert np.all(curves >= pct.min(1)[:, None] - 1e-10)
    assert np.all(curves <= pct.max(1)[:, None] + 1e-10)
    assert np.allclose(z.mean(0), 0, atol=1e-10) and np.allclose(z.std(0), 1)
    return names, pcs, keys, v, raw, z, pct, orders, ranks, curves, sources, max_error


def path_strings(values):
    y = BASE - values * AMPLITUDE / 100
    line = "M" + " L".join(f"{x:.3f},{yy:.3f}" for x, yy in zip(GRID, y))
    return line, f"M{GRID[0]:.3f},{BASE} L" + line[1:] + f" L{GRID[-1]:.3f},{BASE} Z"


def row_svg(i, keys, pct, curves, name, raw, z, gradient):
    line, area = path_strings(curves[i])
    marks = []
    for e, k in enumerate(keys):
        tip = f"{name} | {LABELS[k]} | percentile {pct[i,e]:.2f}/100 | z {z[i,e]:+.3f} | cosine {raw[i,e]:+.6f}"
        marks.append(f'<circle cx="{X[e]:.3f}" cy="{BASE-pct[i,e]*AMPLITUDE/100:.3f}" r="1.7" '
                     f'fill="{NEG if e<5 else POS}"><title>{html.escape(tip)}</title></circle>')
    return (f'<path d="{area}" fill="url(#{gradient})" fill-opacity=".30"/>'
            f'<path d="M14,{BASE} H286" stroke="#343638" stroke-width=".5"/>'
            f'<path d="M150,3 V{BASE}" stroke="#646464" stroke-opacity=".6" stroke-width=".5"/>'
            f'<path d="{line}" fill="none" stroke="url(#{gradient})" stroke-width="1.1"/>' + ''.join(marks))


def gradient(identifier):
    return (f'<linearGradient id="{identifier}"><stop offset="0" stop-color="{NEG}"/>'
            f'<stop offset="45%" stop-color="{NEG}"/><stop offset="55%" stop-color="{POS}"/>'
            f'<stop offset="100%" stop-color="{POS}"/></linearGradient>')


def make_html(names, pcs, keys, pct, curves, raw, z, orders):
    panels = []
    for a, order in enumerate(orders):
        head = ''.join(f'<span style="left:{X[e]/3:.4f}%">{LABELS[k]}</span>' for e,k in enumerate(keys))
        rows = []
        for rank, i in enumerate(order, 1):
            marks = row_svg(i, keys, pct, curves, names[i], raw, z, f"gradient-{a}-{i}")
            rows.append(f'<div class="ridge-row" data-persona="{html.escape(names[i])}" data-rank="{rank}" '
                        f'data-pc="{pcs[i,a]:.15g}"><button type="button" class="name" data-name="{html.escape(names[i])}">'
                        f'<small>{rank:03d} <span>PC{a+1} {pcs[i,a]:+.2f}</span></small>'
                        f'{html.escape(names[i].replace("_", " "))}</button>'
                        f'<svg class="ridge" viewBox="0 0 300 44" preserveAspectRatio="none" role="img" '
                        f'aria-label="{html.escape(names[i])} emotion-affinity percentile profile">'
                        f'<defs>{gradient(f"gradient-{a}-{i}")}</defs>{marks}</svg></div>')
        panels.append(f'<section class="panel" id="pc{a+1}"><header><h2>PC{a+1}</h2>'
                      f'<p>Highest first <span>{pcs[order[0],a]:+.2f} to {pcs[order[-1],a]:+.2f}</span></p>'
                      f'<a href="persona_emotion_ridges_pc{a+1}.svg">Full SVG</a> / '
                      f'<a href="persona_emotion_ridges_pc{a+1}.png">Full PNG</a></header>'
                      f'<div class="rows" aria-label="All 275 personas in descending PC{a+1} order">'
                      f'<div class="chart-head"><div class="axis"><div>Rank / persona</div><div class="categories">{head}</div></div>'
                      f'<div class="polarity"><span></span><div><b>Negative</b><b>Positive</b></div></div>'
                      f'</div>{"".join(rows)}</div>'
                      '<div class="panel-foot">275 / 275 personas rendered; scroll this plot</div></section>')
    options = ''.join(f'<option value="{html.escape(n)}">{html.escape(n.replace("_", " "))}</option>' for n in sorted(names))
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Persona emotion ridges | Qwen</title><style>
:root {color-scheme:dark; --bg:#0d0d0d; --panel:#151515; --line:#303234; --text:#e8e8e8; --muted:#aaa6a0; --neg:#d99a87; --pos:#8bc5c0}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--text);font:13px/1.5 Menlo,Consolas,monospace}
.intro{padding:24px 26px 15px;border-bottom:1px solid var(--line)} .eyebrow{color:var(--pos);font-size:11px;letter-spacing:1.6px;text-transform:uppercase}
h1{font-weight:400;font-size:26px;letter-spacing:-.6px;margin:4px 0 8px} p{margin:4px 0;color:var(--muted)}
.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:12px 26px;border-bottom:1px solid var(--line)}
select,button{font:inherit} select{color:var(--text);background:var(--panel);border:1px solid #555;padding:7px;max-width:100%}
a{color:var(--pos);text-underline-offset:3px} .controls .scale{margin-left:auto;color:var(--muted);font-size:11px}
.plots{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;padding:20px 26px}
.panel{min-width:0;border:1px solid var(--line);background:var(--panel)} .panel header{padding:12px 12px 0}
h2{font-size:21px;font-weight:400;margin:0} .panel header p{font-size:11px;display:flex;justify-content:space-between;gap:8px}
.panel header a{font-size:11px}.axis,.ridge-row,.polarity{display:grid;grid-template-columns:122px minmax(0,1fr);padding:0 10px}
.axis{height:110px;padding-top:2px;align-items:end;color:var(--muted);font-size:11px;padding-bottom:5px}
.categories{height:96px;position:relative}.categories span{position:absolute;bottom:0;transform:rotate(-64deg);transform-origin:left bottom;white-space:nowrap;font-size:11px}
.polarity{font-size:10px;margin:0 0 7px}.polarity div{display:flex;justify-content:space-around}.polarity b{font-weight:400;color:var(--pos)}.polarity b:first-child{color:var(--neg)}
.rows{height:64vh;min-height:350px;overflow-y:scroll;scrollbar-gutter:stable;border-top:1px solid var(--line)}
.chart-head{position:sticky;top:0;z-index:2;background:var(--panel);border-bottom:1px solid var(--line)}
.ridge-row{min-height:44px;align-items:center;border-bottom:1px solid #242627}.ridge-row:nth-child(even){background:#17191a}
.ridge{width:100%;height:44px;overflow:visible}.name{background:none;color:var(--text);border:0;text-align:left;padding:2px 5px 2px 0;font-size:11px;line-height:1.25;cursor:pointer;overflow-wrap:anywhere}
.name small{display:block;font-size:9px;color:var(--muted);font-variant-numeric:tabular-nums;margin-bottom:2px}.name small span{margin-left:4px}
.ridge-row.selected{background:#233432;outline:1px solid var(--pos);outline-offset:-1px}.name:focus-visible{outline:2px solid var(--pos)}
.panel-foot{padding:7px 12px;font-size:10px;color:var(--muted);border-top:1px solid var(--line)}
.notes{padding:0 26px 24px;max-width:1120px}.notes summary{cursor:pointer}.notes p{font-size:12px;margin:10px 0}
#selection-status{color:var(--pos);font-size:11px}.scale-key{display:inline-block;vertical-align:middle;width:56px;height:27px}
@media(max-width:1100px){.plots{grid-template-columns:1fr}.axis,.ridge-row,.polarity{grid-template-columns:165px minmax(0,1fr)}.name{font-size:13px}.name small{font-size:10px}.categories span{font-size:12px;transform:rotate(-50deg)}.rows{height:65vh}}
@media(max-width:500px){.intro,.controls{padding:15px}.plots{padding:15px;gap:22px}.axis,.ridge-row,.polarity{grid-template-columns:115px minmax(0,1fr);padding-left:8px;padding-right:8px}.name{font-size:11px}.name small{font-size:9px}.categories span{font-size:10px;transform:rotate(-70deg)}.controls .scale{margin-left:0}.notes{padding:0 15px 20px}}
@media print{.plots{display:block}.panel{break-after:page}.rows{height:auto;overflow:visible}.controls{display:none}}
</style></head><body>
<div class="intro"><div class="eyebrow">Persona geometry / Qwen / 10 emotion directions</div>
<h1>Emotion profiles, ordered through PC space</h1>
<p>Each ridge is one persona. Each plot lists all 275 personas, from greatest to smallest component value.</p>
<p>Negative-valence categories on the left; positive on the right. Height is relative affinity, not emotion frequency.</p></div>
<div class="controls"><label for="find-persona">Locate the same persona in all three plots</label>
<select id="find-persona"><option value="">Choose a persona</option>''' + options + '''</select>
<span class="scale"><svg class="scale-key" viewBox="0 0 56 27" aria-hidden="true"><path d="M4,24V2M0,2H8M0,24H8" stroke="#aaa6a0"/><text x="12" y="9" fill="#aaa6a0" font-size="9">100</text><text x="12" y="25" fill="#aaa6a0" font-size="9">0</text></svg>Within-emotion percentile; same height scale throughout</span>
<div id="selection-status" role="status" aria-live="polite"></div></div>
<noscript><p class="notes">All three plots are fully rendered below. Only linked persona highlighting needs JavaScript.</p></noscript>
<main class="plots">''' + ''.join(panels) + '''</main>
<div class="notes"><details><summary>Scores, category order, and interpretation limits</summary>
<p>Ridge peaks use the persona's percentile within each emotion over a fixed 275-persona reference. Raw cosine affinities and z-scores are available by hovering the exact category dots and in the CSV. No per-persona peak scaling, area normalization, softmax, or probability estimation is applied. A low ridge is below-average affinity, not evidence that an emotion is absent.</p>
<p>Ten categories are equally spaced and ordered by their existing Qwen valence-axis projection. Spacing is categorical, not a calibrated valence interval. The central divider separates negative from positive category projections; it is not a measured neutral emotion. Smooth PCHIP connectors pass through the exact category scores without overshoot; they are not densities or measurements of intermediate emotional states.</p>
<p>All six original channels are retained, with loneliness, excitement, gratitude and hope added from the saved 171-direction bank. These are activation affinities, not probabilities, prevalence or subjective feelings. Per-emotion percentile scaling supports between-persona comparison of that emotion, not absolute intensity comparisons across different emotions.</p>
<p>Released Qwen role tensor row 47 matches the story probes' hidden_states[48] convention. The horizontal ranking uses the unchanged existing layer-averaged persona PCA. Story-last-token versus role-response-mean transfer remains unvalidated. No new activations, generations or model/API calls were used.</p>
<p><a href="persona_emotion_ridge_methodology.md">Methodology and provenance</a> / <a href="persona_emotion_ridge_scores.csv" download>Download all 2,750 scores</a> / <a href="../persona_emotion_surface_viewer/persona_emotion_surface_viewer.html">Return to the working 3D landscape</a></p>
</details></div><script>
(() => {
 const picker=document.getElementById('find-persona');
 const rows=Array.from(document.querySelectorAll('.ridge-row'));
 function select(name) {
   const matches=[];
   rows.forEach(row=>{const active=Boolean(name)&&row.dataset.persona===name;
     row.classList.toggle('selected',active);
     if(active){row.parentElement.scrollTop=row.offsetTop-row.parentElement.offsetTop-150;matches.push(row);}});
   picker.value=name;
   document.getElementById('selection-status').textContent=matches.length ?
     name.replaceAll('_',' ')+' | '+matches.map((row,i)=>'PC'+(i+1)+' rank '+row.dataset.rank+'/275').join(' | ') : '';
 }
 picker.addEventListener('change',()=>select(picker.value));
 document.querySelectorAll('[data-name]').forEach(button=>button.addEventListener('click',()=>select(button.dataset.name)));
})();
</script></body></html>'''


def svg_panel(names, pcs, keys, pct, curves, raw, z, order, axis, width=1000, limit=None):
    chosen = order if limit is None else order[:limit]
    height = 185 + ROW * len(chosen) + 55
    graph_x, graph_w = 240, width - 295
    defs = gradient(f"static-{axis}")
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
             f'<title>Qwen emotion ridges ordered by PC{axis+1}, highest first</title><defs>{defs}</defs>',
             f'<rect width="{width}" height="{height}" fill="#111315"/>',
             f'<g font-family="DejaVu Sans, sans-serif" fill="{TEXT}">',
             f'<text x="24" y="33" font-size="23">PC{axis+1} / emotion profiles</text>',
             f'<text x="24" y="58" font-size="12" fill="{MUTED}">{len(chosen)} of 275 personas; highest PC{axis+1} first. Height = percentile (0-100).</text>',
             f'<text x="{graph_x+graph_w*.22}" y="83" font-size="12" text-anchor="middle" fill="{NEG}">Negative valence</text>',
             f'<text x="{graph_x+graph_w*.78}" y="83" font-size="12" text-anchor="middle" fill="{POS}">Positive valence</text>']
    for e, k in enumerate(keys):
        xx = graph_x + X[e] / 300 * graph_w
        parts.append(f'<text transform="translate({xx:.3f},165) rotate(-48)" font-size="12">{LABELS[k]}</text>')
    for rank, i in enumerate(chosen, 1):
        yy = 178 + (rank-1)*ROW
        if rank % 2 == 0:
            parts.append(f'<rect x="0" y="{yy}" width="{width}" height="{ROW}" fill="#1b1e20"/>')
        parts.append(f'<text x="24" y="{yy+18}" font-size="13">{rank:03d}  {html.escape(names[i].replace("_"," "))}</text>')
        parts.append(f'<text x="24" y="{yy+33}" font-size="10" fill="{MUTED}">PC{axis+1} {pcs[i,axis]:+.3f}</text>')
        parts.append(f'<g transform="translate({graph_x},{yy}) scale({graph_w/300},1)">' +
                     row_svg(i, keys, pct, curves, names[i], raw, z, f"static-{axis}") + '</g>')
    parts += [f'<text x="24" y="{height-28}" font-size="11" fill="{MUTED}">Categorical order from saved valence projections; curves are score connectors, not probability densities.</text>',
              f'<text x="24" y="{height-11}" font-size="11" fill="{MUTED}">Saved Qwen activation affinities; story-to-role transfer unvalidated. No subjective-emotion claim.</text>', '</g></svg>']
    return ''.join(parts)


def main():
    names, pcs, keys, v, raw, z, pct, orders, ranks, curves, sources, max_error = score()
    now = datetime.now(timezone.utc).isoformat()
    base = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    rows = []
    for i, name in enumerate(names):
        for e, k in enumerate(keys):
            rows.append(dict(persona=name, emotion=k, label=LABELS[k], category_position=e+1,
                             category_valence_raw=float(v[k]['valence_raw']),
                             raw_affinity=float(raw[i,e]), z_score=float(z[i,e]),
                             ridge_height_percentile=float(pct[i,e]), pc1=float(pcs[i,0]),
                             pc2=float(pcs[i,1]), pc3=float(pcs[i,2]),
                             rank_pc1=ranks[0][i],rank_pc2=ranks[1][i],rank_pc3=ranks[2][i]))
    save_csv('persona_emotion_ridge_scores.csv',rows)
    save_csv('emotion_category_order.csv',[dict(position=e+1,emotion=k,label=LABELS[k],
                                              valence_raw=float(v[k]['valence_raw']),
                                              side='negative' if e<5 else 'positive',
                                              original_six=k in ['joyful','calm','sad','afraid','angry','disgusted'])
                                          for e,k in enumerate(keys)])
    save_json('persona_emotion_ridge_data.json',dict(
        categories=[dict(key=k,label=LABELS[k],valence_raw=float(v[k]['valence_raw'])) for k in keys],
        personas=names,coordinates=pcs.tolist(),raw_affinity=raw.tolist(),z_score=z.tolist(),
        height_percentile=pct.tolist(),orders=orders))
    (HERE/'persona_emotion_ridges.html').write_text(make_html(names,pcs,keys,pct,curves,raw,z,orders))
    for a in range(3):
        (HERE/f'persona_emotion_ridges_pc{a+1}.svg').write_text(svg_panel(names,pcs,keys,pct,curves,raw,z,orders[a],a))
    # An explicitly cropped overview; all rows remain in each full SVG and HTML panel.
    overview = ['<svg xmlns="http://www.w3.org/2000/svg" width="2100" height="1120" viewBox="0 0 2100 1120">',
                '<rect width="2100" height="1120" fill="#0d0d0d"/>']
    for a in range(3):
        overview.append(f'<g transform="translate({a*700},0)">'+svg_panel(names,pcs,keys,pct,curves,raw,z,orders[a],a,width=700,limit=20)+'</g>')
    overview.append('</svg>')
    (HERE/'persona_emotion_ridges_overview.svg').write_text(''.join(overview))
    manifest = dict(generated_utc=now,base_commit=base,activation_model='Qwen/Qwen3-32B',
                    author='Codex; exact runtime identifier not recorded',gpu_used=False,api_calls=0,
                    persona_count=275,emotion_count=10,saved_bank_count=171,score_rows=2750,
                    layer=dict(released_role_row=47,emotion_hidden_state_index=48),
                    height='100 * (average rank - 0.5) / 275, separately per emotion',
                    x_axis='equal-spaced categories sorted by existing valence_raw; not metric distances',
                    curve='shape-preserving PCHIP through percentile scores; no KDE or area normalization',
                    source_files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p)) for p in sources],
                    old_six_comparison=dict(rows=1650,max_absolute_raw_difference=max_error),
                    caveats=['affinity not probability or prevalence','between-emotion absolute intensity not calibrated',
                             'story-last-token versus response-mean transfer unvalidated','PC geometry layer-averaged unchanged'],
                    order_extremes={f'pc{a+1}':dict(highest=names[o[0]],lowest=names[o[-1]]) for a,o in enumerate(orders)})
    save_json('persona_emotion_ridge_manifest.json',manifest)
    checks=dict(status='pass',score_rows=len(rows),panels=3,rows_per_panel=275,
                same_original_six=True,max_absolute_raw_difference=max_error,
                finite_scores=True,normalization=True,strict_pc_descending_with_name_tiebreak=True,
                curve_no_overshoot=True,all_panels_prerendered=True,
                no_external_scripts=True,browser_validation='Not performed; static SVG render and source/data checks only')
    save_json('persona_emotion_ridge_checks.json',checks)
    print(json.dumps({**checks,'category_order':keys,'extremes':manifest['order_extremes']},indent=2))


def inventory():
    files = sorted(p for p in HERE.iterdir() if p.is_file() and p.name != 'artifact_inventory.csv')
    save_csv('artifact_inventory.csv', [dict(path=str(p.relative_to(ROOT)), size_bytes=p.stat().st_size,
        sha256=digest(p), raw_github_url='https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/'+str(p.relative_to(ROOT)))
        for p in files])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inventory-only', action='store_true', help='Refresh output checksums after static PNG rendering')
    args = parser.parse_args()
    if not args.inventory_only:
        main()
    inventory()
