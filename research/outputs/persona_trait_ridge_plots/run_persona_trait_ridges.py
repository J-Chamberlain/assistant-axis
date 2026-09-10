#!/usr/bin/env python3
"""Render saved same-space trait affinities as complete PC-ranked ridge profiles."""
import argparse
import csv
import hashlib
import html
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.stats import rankdata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEOMETRY = ROOT / 'research/visualizations/geometry_viz_data.json'
MATRIX = ROOT / 'research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv'
JOINED = ROOT / 'research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv'
DEFINITIONS = ROOT / 'data/traits/trait_list.json'
AUDIT = ROOT / 'research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md'
# Editorial coverage groups chosen from descriptions, not fitted to PC correlations.
GROUPS = [
    ('Exploration', '#b4a5d0', ['creative', 'abstract', 'curious']),
    ('Response', '#dbb77c', ['reactive', 'adaptable', 'practical']),
    ('Scrutiny', '#91b6d0', ['skeptical', 'analytical', 'conscientious']),
    ('Challenge', '#d99a87', ['rebellious', 'competitive', 'manipulative']),
    ('Affiliation', '#8bc5c0', ['empathetic', 'agreeable', 'altruistic']),
]
KEYS = [k for _, _, keys in GROUPS for k in keys]
X = np.linspace(14, 436, len(KEYS))
GRID = np.linspace(X[0], X[-1], 211)
BASE, AMP, ROW, WIDTH = 36, 30, 44, 450


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def save_csv(name, rows):
    with (HERE / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def load_data():
    g = json.loads(GEOMETRY.read_text())['roles']
    names, pcs = g['names'], np.asarray(g['pca3d'], dtype=float)
    source = list(csv.DictReader(MATRIX.open()))
    joined = {r['persona']: r for r in csv.DictReader(JOINED.open())}
    matrix = {r['persona']: r for r in source}
    definitions = json.loads(DEFINITIONS.read_text())
    assert len(names) == len(set(names)) == len(source) == len(matrix) == 275
    assert set(matrix) == set(names) == set(joined)
    assert len(source[0]) == 241 and set(source[0]) - {'persona'} == set(definitions)
    assert len(definitions) == 240 and set(KEYS) <= set(definitions)
    assert pcs.shape == (275, 3) and np.isfinite(pcs).all()
    raw = np.array([[float(matrix[n][k]) for k in KEYS] for n in names])
    # The downstream CSV round-trip changes final decimal digits (<1e-16).
    joined_max_difference = max(abs(float(matrix[n][k])-float(joined[n][k]))
                                for n in names for k in definitions)
    assert joined_max_difference < 1e-12, joined_max_difference
    assert np.isfinite(raw).all() and np.all(np.abs(raw) <= 1 + 1e-6)
    assert np.all(raw.std(0) > 1e-8)
    z = (raw - raw.mean(0)) / raw.std(0, ddof=0)
    pct = np.column_stack([100 * (rankdata(raw[:, e], method='average') - .5) / len(names)
                           for e in range(len(KEYS))])
    curves = np.stack([PchipInterpolator(X, row)(GRID) for row in pct])
    assert np.all(curves >= pct.min(1)[:, None] - 1e-9)
    assert np.all(curves <= pct.max(1)[:, None] + 1e-9)
    orders = [sorted(range(len(names)), key=lambda i: (-pcs[i, a], names[i])) for a in range(3)]
    return names, pcs, raw, z, pct, curves, orders, definitions, joined_max_difference


def ridge(i, names, raw, z, pct, curves):
    y = BASE - curves[i] * AMP / 100
    line = 'M' + ' L'.join(f'{x:.2f},{yy:.2f}' for x, yy in zip(GRID, y))
    area = f'M{GRID[0]},{BASE} L' + line[1:] + f' L{GRID[-1]},{BASE} Z'
    parts = [f'<path d="{area}" fill="#b6c1c8" fill-opacity=".20"/>',
             f'<path d="M14,{BASE}H436" stroke="#45474a" stroke-width=".5"/>']
    for e in [3, 6, 9, 12]:
        mid = (X[e-1] + X[e])/2
        parts.append(f'<path d="M{mid:.2f},3V36" stroke="#6b6e70" stroke-dasharray="2 3" stroke-width=".5"/>')
    parts.append(f'<path d="{line}" stroke="#d4dadd" stroke-width="1.05" fill="none"/>')
    for e, k in enumerate(KEYS):
        tip = f'{names[i]} | {k} | percentile {pct[i,e]:.2f}/100 | z {z[i,e]:+.3f} | cosine {raw[i,e]:+.6f}'
        parts.append(f'<circle cx="{X[e]:.3f}" cy="{BASE-pct[i,e]*AMP/100:.3f}" r="2" fill="{GROUPS[e//3][1]}"><title>{html.escape(tip)}</title></circle>')
    return ''.join(parts)


def svg_panel(names, pcs, raw, z, pct, curves, order, axis, limit=None):
    chosen = order if limit is None else order[:limit]
    height, width, gx, gw = 220 + ROW*len(chosen) + 60, 1000, 226, 720
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
             f'<title>Qwen trait profiles in descending PC{axis+1} order</title>',
             f'<rect width="{width}" height="{height}" fill="#111315"/>',
             '<g font-family="DejaVu Sans, sans-serif" fill="#e8e8e8">',
             f'<text x="24" y="34" font-size="24">PC{axis+1} / trait profiles</text>',
             f'<text x="24" y="59" font-size="12" fill="#aaa6a0">{len(chosen)} of 275 personas; highest first. Height = within-trait percentile (0-100).</text>']
    for e, k in enumerate(KEYS):
        xx = gx + X[e]/WIDTH*gw
        parts.append(f'<text transform="translate({xx:.3f},191) rotate(-56)" font-size="12">{k.capitalize()}</text>')
    for gi, (label, color, _) in enumerate(GROUPS):
        xx = gx + X[gi*3+1]/WIDTH*gw
        parts.append(f'<text x="{xx:.3f}" y="90" font-size="12" text-anchor="middle" fill="{color}">{label}</text>')
    for rank, i in enumerate(chosen, 1):
        yy = 205 + (rank-1)*ROW
        if rank % 2 == 0:
            parts.append(f'<rect y="{yy}" width="1000" height="44" fill="#1b1e20"/>')
        parts += [f'<text x="24" y="{yy+18}" font-size="13">{rank:03d}  {html.escape(names[i].replace("_", " "))}</text>',
                  f'<text x="24" y="{yy+33}" font-size="10" fill="#aaa6a0">PC{axis+1} {pcs[i,axis]:+.3f}</text>',
                  f'<g transform="translate({gx},{yy}) scale({gw/WIDTH},1)">{ridge(i,names,raw,z,pct,curves)}</g>']
    parts += [f'<text x="24" y="{height-30}" font-size="11" fill="#aaa6a0">15 of 240 mapped traits; descriptive groups, not a valence scale or measured continuum.</text>',
              f'<text x="24" y="{height-12}" font-size="11" fill="#aaa6a0">Same-space activation cosines, not independent psychological ratings. Curves are not probability densities.</text>',
              '</g></svg>']
    return ''.join(parts)


def make_html(names, pcs, raw, z, pct, curves, orders):
    panels = []
    head = ''.join(f'<span style="left:{X[e]/WIDTH*100:.4f}%">{k.capitalize()}</span>' for e,k in enumerate(KEYS))
    grouphead = ''.join(f'<span style="left:{X[gi*3+1]/WIDTH*100:.4f}%;color:{color}">{label}</span>'
                        for gi,(label,color,_) in enumerate(GROUPS))
    for a, order in enumerate(orders):
        rows = []
        for rank, i in enumerate(order, 1):
            rows.append(f'<div class="ridge-row" data-persona="{html.escape(names[i])}" data-rank="{rank}" data-pc="{pcs[i,a]:.15g}">'
                        f'<button class="name" type="button" data-name="{html.escape(names[i])}"><small>{rank:03d} / PC{a+1} {pcs[i,a]:+.2f}</small>{html.escape(names[i].replace("_", " "))}</button>'
                        f'<svg class="ridge" viewBox="0 0 450 44" preserveAspectRatio="none" role="img" aria-label="{html.escape(names[i])} trait-affinity percentile profile">'
                        f'{ridge(i,names,raw,z,pct,curves)}</svg></div>')
        panels.append(f'<section class="panel"><header><h2>PC{a+1}</h2><p>Highest first: {pcs[order[0],a]:+.2f} to {pcs[order[-1],a]:+.2f}</p>'
                      f'<a href="persona_trait_ridges_pc{a+1}.svg">Full SVG</a> / <a href="persona_trait_ridges_pc{a+1}.png">Full PNG</a></header>'
                      f'<div class="rows" aria-label="All 275 personas in descending PC{a+1} order"><div class="chart-head">'
                      f'<div class="axis"><span>Rank / persona</span><div class="categories">{head}</div></div>'
                      f'<div class="family-axis"><span></span><div class="families">{grouphead}</div></div></div>{"".join(rows)}</div>'
                      '<footer>275 / 275 personas; scroll this plot</footer></section>')
    options = ''.join(f'<option value="{html.escape(n)}">{html.escape(n.replace("_", " "))}</option>' for n in sorted(names))
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Persona trait ridges | Qwen</title><style>
:root{color-scheme:dark;--bg:#0d0d0d;--panel:#151515;--text:#e8e8e8;--muted:#aaa6a0;--line:#303234;--accent:#8bc5c0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:13px/1.5 Menlo,Consolas,monospace}
.intro{padding:24px 26px 15px;border-bottom:1px solid var(--line)}.eyebrow{color:var(--accent);font-size:11px;letter-spacing:1.6px;text-transform:uppercase}
h1{font-size:26px;font-weight:400;margin:4px 0 8px;letter-spacing:-.6px}p{color:var(--muted);margin:4px 0}a{color:var(--accent);text-underline-offset:3px}
.controls{padding:12px 26px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:12px;flex-wrap:wrap}
select,button{font:inherit}select{background:var(--panel);border:1px solid #555;color:var(--text);padding:7px;max-width:100%}.scale{margin-left:auto;font-size:11px;color:var(--muted)}
.plots{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;padding:20px 26px}.panel{min-width:0;background:var(--panel);border:1px solid var(--line)}
.panel header{padding:12px}h2{font-size:21px;font-weight:400;margin:0}.panel header p,.panel header a{font-size:11px}
.rows{height:68vh;min-height:390px;overflow:auto;scrollbar-gutter:stable;border-top:1px solid var(--line)}
.chart-head{position:sticky;top:0;z-index:2;background:var(--panel);border-bottom:1px solid var(--line)}
.axis,.family-axis,.ridge-row{display:grid;grid-template-columns:128px minmax(0,1fr);padding:0 10px;min-width:630px}
.axis{height:132px;align-items:end;color:var(--muted);font-size:11px;padding-bottom:6px}.categories{height:122px;position:relative}.categories span{position:absolute;bottom:0;transform:rotate(-64deg);transform-origin:left bottom;white-space:nowrap;font-size:11px}
.families{height:23px;position:relative}.families span{position:absolute;transform:translateX(-50%);font-size:10px;white-space:nowrap}
.ridge-row{height:44px;align-items:center;border-bottom:1px solid #242627}.ridge-row:nth-child(even){background:#17191a}.ridge{width:100%;height:44px;overflow:visible}
.name{color:var(--text);background:none;border:0;text-align:left;cursor:pointer;line-height:1.3;font-size:11px;padding:2px 5px 2px 0;overflow-wrap:anywhere}.name small{display:block;color:var(--muted);font-size:9px;margin-bottom:2px}
.ridge-row.selected{background:#233432;outline:1px solid var(--accent);outline-offset:-1px}.name:focus-visible{outline:2px solid var(--accent)}
footer{color:var(--muted);font-size:10px;padding:7px 12px}.notes{padding:0 26px 24px;max-width:1150px}.notes p{font-size:12px;margin:10px 0}.notes summary{cursor:pointer}#selection-status{color:var(--accent);font-size:11px}
@media(max-width:2050px){.plots{grid-template-columns:1fr}.rows{height:65vh}.axis,.family-axis,.ridge-row{grid-template-columns:190px minmax(0,1fr);min-width:690px}.categories span{font-size:12px;transform:rotate(-50deg)}.name{font-size:13px}.name small{font-size:10px}.families span{font-size:12px}}
@media(max-width:760px){.intro,.controls{padding:15px}.plots{padding:15px}.scale{margin-left:0}.notes{padding:0 15px 20px}.axis,.family-axis,.ridge-row{grid-template-columns:130px minmax(0,1fr);min-width:650px}.families span{font-size:10px}.categories span{font-size:11px;transform:rotate(-64deg)}.name{font-size:11px}.name small{font-size:9px}}
@media print{.plots{display:block}.rows{height:auto;overflow:visible}.panel{break-after:page}.controls{display:none}.chart-head{position:static}}
</style></head><body><div class="intro"><div class="eyebrow">Persona geometry / Qwen / 15 of 240 mapped traits</div>
<h1>Trait profiles, ordered through PC space</h1><p>All 275 personas, greatest to smallest PC1, PC2 or PC3. The same profile follows each persona across the three rankings.</p>
<p>Left to right: exploration, response, scrutiny, challenge, affiliation. These are descriptive groups, not a valence scale.</p></div>
<div class="controls"><label for="find-persona">Locate the same persona in all three plots</label><select id="find-persona"><option value="">Choose a persona</option>''' + options + '''</select>
<span class="scale">Height: 0-100 within-trait percentile / identical scale for every ridge</span><div id="selection-status" role="status" aria-live="polite"></div></div>
<noscript><p class="notes">All plots are already rendered. Only linked selection needs JavaScript.</p></noscript>
<main class="plots">''' + ''.join(panels) + '''</main>
<div class="notes"><p>Scroll each plot to see every persona; on narrow screens, scroll sideways to see all 15 trait labels. Hover a category dot for its raw cosine, z-score and percentile.</p>
<details><summary>Reading the profiles and their provenance</summary>
<p>Each height compares one persona with all 275 personas for that particular trait. A value of 80 is approximately the 80th percentile, not 80% trait intensity. Heights are not normalized within a persona and do not sum to 100. A lower height is lower relative activation affinity, not absence of the trait.</p>
<p>The 15 traits are an editorial coverage sample of 240 saved categories, selected from their descriptions before inspecting selected scores. Five colored groups provide navigation; they are not fitted clusters, valence signs, PCA directions, or validated psychological factors. Trait words remain neutral. Equally spaced categories and smooth non-overshooting connectors are visual aids, not a measured continuum or probability distribution.</p>
<p>Values are copied from the existing 275-by-240 Qwen role-to-trait cosine matrix used in earlier trait-region overlays. That matrix compares normalized means across the released 64-row activation tensors. This viewer does not rescore vectors or refit PCA. Mixed provenance: released trait definitions/vectors, internally computed cosines. Traits and PCA share source activation space, so this is not independent psychological validation.</p>
<p><a href="persona_trait_ridge_methodology.md">Methodology and complete trait definitions</a> / <a href="persona_trait_ridge_scores.csv" download>All 4,125 scores</a> / <a href="../persona_emotion_ridge_plots/persona_emotion_ridges.html">Emotion ridge plots</a></p>
</details></div><script>
(() => {
 const picker=document.getElementById('find-persona');
 const rows=Array.from(document.querySelectorAll('.ridge-row'));
 function select(name){
   const matches=[];
   rows.forEach(row=>{const active=Boolean(name)&&row.dataset.persona===name;
     row.classList.toggle('selected',active);
     if(active){row.parentElement.scrollTop=row.offsetTop-row.parentElement.offsetTop-170;matches.push(row);}});
   picker.value=name;
   document.getElementById('selection-status').textContent=matches.length ?
     name.replaceAll('_',' ')+' | '+matches.map((row,i)=>'PC'+(i+1)+' rank '+row.dataset.rank+'/275').join(' | ') : '';
 }
 picker.addEventListener('change',()=>select(picker.value));
 document.querySelectorAll('[data-name]').forEach(button=>button.addEventListener('click',()=>select(button.dataset.name)));
})();
</script></body></html>'''


def inventory():
    paths = sorted(p for p in HERE.iterdir() if p.is_file() and p.name != 'artifact_inventory.csv')
    save_csv('artifact_inventory.csv', [dict(path=str(p.relative_to(ROOT)),size_bytes=p.stat().st_size,
        sha256=sha(p),raw_github_url='https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/'+str(p.relative_to(ROOT))) for p in paths])


def main():
    names, pcs, raw, z, pct, curves, orders, definitions, joined_max_difference = load_data()
    ranks = [{i:r+1 for r,i in enumerate(order)} for order in orders]
    categories = [dict(position=e+1,trait=k,group=GROUPS[e//3][0],color=GROUPS[e//3][1],definition=definitions[k]) for e,k in enumerate(KEYS)]
    save_csv('trait_category_order.csv', categories)
    rows = [dict(persona=n,trait=k,group=GROUPS[e//3][0],category_position=e+1,
        raw_affinity=float(raw[i,e]),z_score=float(z[i,e]),ridge_height_percentile=float(pct[i,e]),
        pc1=float(pcs[i,0]),pc2=float(pcs[i,1]),pc3=float(pcs[i,2]),
        rank_pc1=ranks[0][i],rank_pc2=ranks[1][i],rank_pc3=ranks[2][i]) for i,n in enumerate(names) for e,k in enumerate(KEYS)]
    save_csv('persona_trait_ridge_scores.csv',rows)
    save_json('persona_trait_ridge_data.json',dict(categories=categories,personas=names,coordinates=pcs.tolist(),
        raw_affinity=raw.tolist(),z_score=z.tolist(),height_percentile=pct.tolist(),orders=orders))
    (HERE/'persona_trait_ridges.html').write_text(make_html(names,pcs,raw,z,pct,curves,orders))
    for a in range(3):
        (HERE/f'persona_trait_ridges_pc{a+1}.svg').write_text(svg_panel(names,pcs,raw,z,pct,curves,orders[a],a))
    overview = ['<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="940" viewBox="0 0 3000 940">']
    for a in range(3):
        overview.append(f'<g transform="translate({a*1000},0)">'+svg_panel(names,pcs,raw,z,pct,curves,orders[a],a,limit=15)+'</g>')
    (HERE/'persona_trait_ridges_overview.svg').write_text(''.join(overview)+'</svg>')
    sources=[GEOMETRY,MATRIX,JOINED,DEFINITIONS,AUDIT,ROOT/'research/outputs/trait_persona_prediction/run_trait_persona_prediction.py']
    manifest=dict(generated_utc=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        activation_model='Qwen/Qwen3-32B',author='Codex; exact runtime identifier not recorded',
        source_personas=275,source_traits=240,selected_traits=15,score_rows=len(rows),
        groups=categories,selection='Editorial coverage based on saved trait descriptions; not data-optimized or statistically representative',
        raw_scores='Copied exactly from saved role-by-trait cosine matrix; all 240 columns checked against PC2 joined copy',
        joined_matrix_max_absolute_difference=joined_max_difference,
        matrix_construction='Mean of 64 stored activation rows per role/trait, then L2 normalization and dot product; inherited without rescoring',
        normalization='100 * (average rank - 0.5) / 275 separately per trait; population z-scores also provided',
        ordering='Descending unchanged canonical PC value with name tie-break',
        x_axis='Equally spaced descriptive groups, not measured psychological/valence distance',
        curve='PCHIP score connectors; not density, no within-persona area/peak normalization',
        gpu_used=False,api_calls=0,activation_generation=False,pca_refit=False,
        source_files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sources])
    save_json('persona_trait_ridge_manifest.json',manifest)
    print(json.dumps(dict(personas=len(names),traits=len(KEYS),score_rows=len(rows),
        extremes=[dict(pc=a+1,highest=names[o[0]],lowest=names[o[-1]]) for a,o in enumerate(orders)]),indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--inventory-only',action='store_true')
    if not parser.parse_args().inventory_only:
        main()
    inventory()
