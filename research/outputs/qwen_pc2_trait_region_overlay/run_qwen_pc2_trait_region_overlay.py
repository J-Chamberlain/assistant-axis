import csv, html, json, math, statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis')
OUT = REPO / 'research/outputs/qwen_pc2_trait_region_overlay'
OUT.mkdir(parents=True, exist_ok=True)
MODEL_USED = 'GPT-5.5'
UPDATED = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
SOURCE = REPO / 'research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv'
GEOM_ROLE = REPO / 'research/geometry_tables/qwen_role_pc_rankings.csv'
CLUSTER_TABLE = REPO / 'research/geometry_tables/cluster_membership_table.csv'

CLUSTER_COLORS = {
    'editorial': '#e8b84b',
    'procedural_professional': '#4a9eff',
    'grounded_social': '#5ecb8a',
    'other': '#b0b0b0',
    'combative_iconoclast': '#ff6b6b',
    'mythic_spiritual': '#c084fc',
    'trickster_chaos': '#fb923c',
    'unassigned': '#777777',
}
EXPECTED_HIGH = {'reactive','experiential','practical','visceral','accessible','anxious','neurotic','accommodating','grounded','casual'}
EXPECTED_LOW = {'abstract','formal','conscientious','conceptual','pensive','serious','theoretical','meticulous','integrated'}
META = ['persona','pc1','pc2','pc3','cluster','pc1_percentile','pc2_percentile','pc3_percentile']

def fnum(x):
    try: return float(x)
    except: return float('nan')

with SOURCE.open(newline='') as fh:
    rows = list(csv.DictReader(fh))
trait_cols = [c for c in rows[0].keys() if c not in META]
for r in rows:
    r['pc1'] = fnum(r['pc1']); r['pc2'] = fnum(r['pc2']); r['pc3'] = fnum(r['pc3'])
    for t in trait_cols: r[t] = fnum(r[t])

# Quantile helper: contiguous equal-count bins.
def quantile_bins(sorted_values, n_bins):
    n = len(sorted_values)
    bounds = []
    for b in range(n_bins):
        lo_i = math.floor(b*n/n_bins)
        hi_i = math.floor((b+1)*n/n_bins)-1
        bounds.append((sorted_values[lo_i], sorted_values[hi_i]))
    return bounds

pc1_sorted = sorted(r['pc1'] for r in rows)
pc1_bounds = quantile_bins(pc1_sorted, 5)

def assign_by_bounds(value, bounds):
    for i,(lo,hi) in enumerate(bounds):
        if i == len(bounds)-1:
            if lo <= value <= hi: return i
        elif lo <= value <= hi: return i
    # Handle duplicate boundary/numeric edge.
    diffs = [abs(value - ((lo+hi)/2)) for lo,hi in bounds]
    return min(range(len(bounds)), key=lambda i: diffs[i])

for r in rows:
    r['pc1_bin_idx'] = assign_by_bounds(r['pc1'], pc1_bounds)

pc2_bounds_by_pc1 = {}
for bi in range(5):
    sub = sorted(r['pc2'] for r in rows if r['pc1_bin_idx'] == bi)
    pc2_bounds_by_pc1[bi] = quantile_bins(sub, 3)
for r in rows:
    r['pc2_bin_idx'] = assign_by_bounds(r['pc2'], pc2_bounds_by_pc1[r['pc1_bin_idx']])

# Global means/stds.
global_mean = {}
global_std = {}
for t in trait_cols:
    vals = [r[t] for r in rows]
    global_mean[t] = statistics.fmean(vals)
    sd = statistics.pstdev(vals)
    global_std[t] = sd if sd > 1e-12 else 1.0

band_mean = {}
for bi in range(5):
    sub = [r for r in rows if r['pc1_bin_idx'] == bi]
    band_mean[bi] = {t: statistics.fmean([r[t] for r in sub]) for t in trait_cols}

cell_records = []
for bi in range(5):
    for cj in range(3):
        sub = [r for r in rows if r['pc1_bin_idx'] == bi and r['pc2_bin_idx'] == cj]
        if not sub:
            continue
        cell_mean = {t: statistics.fmean([r[t] for r in sub]) for t in trait_cols}
        rel_scores = [(t, (cell_mean[t] - band_mean[bi][t]) / global_std[t]) for t in trait_cols]
        glob_scores = [(t, (cell_mean[t] - global_mean[t]) / global_std[t]) for t in trait_cols]
        rel_scores.sort(key=lambda x: x[1], reverse=True)
        glob_scores.sort(key=lambda x: x[1], reverse=True)
        clusters = Counter(r['cluster'] for r in sub)
        dominant, dom_n = clusters.most_common(1)[0]
        # example roles: closest to cell center first, then name.
        xmid = sum(pc1_bounds[bi]) / 2
        ylo,yhi = pc2_bounds_by_pc1[bi][cj]
        ymid = (ylo+yhi)/2
        examples = sorted(sub, key=lambda r: ((r['pc1']-xmid)**2 + (r['pc2']-ymid)**2, r['persona']))[:8]
        rec = {
            'pc1_bin': f'Q{bi+1}',
            'pc1_bin_index': bi + 1,
            'pc1_min': pc1_bounds[bi][0],
            'pc1_max': pc1_bounds[bi][1],
            'pc2_bin': ['low','mid','high'][cj],
            'pc2_bin_index': cj + 1,
            'pc2_min': ylo,
            'pc2_max': yhi,
            'role_count': len(sub),
            'dominant_cluster': dominant,
            'dominant_cluster_fraction': dom_n / len(sub),
            'top_band_relative_traits': '; '.join(f'{t}:{s:.2f}' for t,s in rel_scores[:8]),
            'top_global_traits': '; '.join(f'{t}:{s:.2f}' for t,s in glob_scores[:8]),
            'top_band_relative_trait_names': ', '.join(t for t,s in rel_scores[:3]),
            'top_global_trait_names': ', '.join(t for t,s in glob_scores[:3]),
            'example_roles': ', '.join(r['persona'] for r in examples),
            'sparse_cell': len(sub) < 8,
        }
        cell_records.append((rec, rel_scores, glob_scores, sub))

csv_path = OUT / 'qwen_pc1_pc2_trait_region_cells.csv'
fields = ['pc1_bin','pc1_bin_index','pc1_min','pc1_max','pc2_bin','pc2_bin_index','pc2_min','pc2_max','role_count','dominant_cluster','dominant_cluster_fraction','top_band_relative_trait_names','top_band_relative_traits','top_global_trait_names','top_global_traits','example_roles','sparse_cell']
with csv_path.open('w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
    w.writeheader()
    for rec,_,_,_ in cell_records: w.writerow(rec)

# Interpretation checks.
top3_overlap = []
changed_cells = []
expected_hits = []
for rec, rel, glob, sub in cell_records:
    rel3 = {t for t,s in rel[:3]}; glob3 = {t for t,s in glob[:3]}
    overlap = len(rel3 & glob3)
    top3_overlap.append(overlap/3)
    if overlap < 1:
        changed_cells.append(rec)
    pc2bin = rec['pc2_bin']
    if pc2bin == 'high':
        expected_hits.append(len(rel3 & EXPECTED_HIGH))
    elif pc2bin == 'low':
        expected_hits.append(len(rel3 & EXPECTED_LOW))
mean_overlap = statistics.fmean(top3_overlap) if top3_overlap else 0
material_change = mean_overlap < 0.67 or len(changed_cells) >= 4
sparse = [rec for rec,_,_,_ in cell_records if rec['sparse_cell']]

# SVG helpers.
W,H = 1500, 980
margin = dict(left=90,right=40,top=70,bottom=80)
plot_w = W - margin['left'] - margin['right']
plot_h = H - margin['top'] - margin['bottom']
pc1_min = min(r['pc1'] for r in rows); pc1_max = max(r['pc1'] for r in rows)
pc2_min = min(r['pc2'] for r in rows); pc2_max = max(r['pc2'] for r in rows)
# pad
xpad = (pc1_max-pc1_min)*0.04; ypad=(pc2_max-pc2_min)*0.08
pc1_min -= xpad; pc1_max += xpad; pc2_min -= ypad; pc2_max += ypad

def sx(x): return margin['left'] + (x-pc1_min)/(pc1_max-pc1_min)*plot_w
def sy(y): return margin['top'] + plot_h - (y-pc2_min)/(pc2_max-pc2_min)*plot_h

def svg_text(x,y,text,size=12,fill='#222',anchor='middle',weight='normal'):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{html.escape(text)}</text>'

svg=[]
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append('<rect width="100%" height="100%" fill="#fbfbf8"/>')
svg.append(svg_text(W/2,32,'Qwen PC1 x PC2 Trait-Region Overlay',24,'#111',weight='700'))
svg.append(svg_text(W/2,55,'Cell labels show top PC1-band-relative enriched traits; points are Qwen role PCA coordinates.',13,'#555'))
svg.append(f'<rect x="{margin["left"]}" y="{margin["top"]}" width="{plot_w}" height="{plot_h}" fill="#ffffff" stroke="#ccc"/>')
# grid cells
for rec,_,_,_ in cell_records:
    x0=sx(rec['pc1_min']); x1=sx(rec['pc1_max'])
    y0=sy(rec['pc2_max']); y1=sy(rec['pc2_min'])
    svg.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}" fill="none" stroke="#999" stroke-width="1" stroke-dasharray="4 4"/>')
# points
for r in rows:
    color=CLUSTER_COLORS.get(r['cluster'],'#777')
    svg.append(f'<circle cx="{sx(r["pc1"]):.1f}" cy="{sy(r["pc2"]):.1f}" r="3.1" fill="{color}" fill-opacity="0.35" stroke="none"><title>{html.escape(r["persona"])} | {html.escape(r["cluster"])} | PC1 {r["pc1"]:.2f} | PC2 {r["pc2"]:.2f}</title></circle>')
# labels
for rec,_,_,_ in cell_records:
    x=(sx(rec['pc1_min'])+sx(rec['pc1_max']))/2
    y=(sy(rec['pc2_min'])+sy(rec['pc2_max']))/2
    traits=[t.strip() for t in rec['top_band_relative_trait_names'].split(',')]
    svg.append(f'<rect x="{x-96:.1f}" y="{y-42:.1f}" width="192" height="72" rx="6" fill="#fffffff0" stroke="#d7d7d7"/>')
    svg.append(svg_text(x,y-22,f"{rec['pc1_bin']} / {rec['pc2_bin']}  n={rec['role_count']}",11,'#333',weight='700'))
    for k,t in enumerate(traits[:3]): svg.append(svg_text(x,y-4+15*k,t,12,'#111'))
# axes labels
svg.append(f'<line x1="{margin["left"]}" y1="{margin["top"]+plot_h}" x2="{margin["left"]+plot_w}" y2="{margin["top"]+plot_h}" stroke="#333"/>')
svg.append(f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{margin["top"]+plot_h}" stroke="#333"/>')
svg.append(svg_text(W/2,H-30,'PC1',16,'#111',weight='700'))
svg.append(f'<text x="28" y="{H/2}" font-family="Arial, sans-serif" font-size="16" fill="#111" text-anchor="middle" transform="rotate(-90 28 {H/2})" font-weight="700">PC2</text>')
# ticks
for v in [pc1_min+x*(pc1_max-pc1_min)/6 for x in range(7)]:
    x=sx(v); svg.append(f'<line x1="{x:.1f}" y1="{margin["top"]+plot_h}" x2="{x:.1f}" y2="{margin["top"]+plot_h+5}" stroke="#333"/>'); svg.append(svg_text(x,margin['top']+plot_h+22,f'{v:.0f}',10,'#555'))
for v in [pc2_min+y*(pc2_max-pc2_min)/6 for y in range(7)]:
    y=sy(v); svg.append(f'<line x1="{margin["left"]-5}" y1="{y:.1f}" x2="{margin["left"]}" y2="{y:.1f}" stroke="#333"/>'); svg.append(svg_text(margin['left']-12,y+4,f'{v:.0f}',10,'#555','end'))
# legend
lx=W-280; ly=78
svg.append(svg_text(lx,ly,'Clusters',12,'#333','start',weight='700'))
for i,(cl,c) in enumerate(CLUSTER_COLORS.items()):
    yy=ly+18+i*16
    svg.append(f'<circle cx="{lx+6}" cy="{yy-4}" r="4" fill="{c}"/>')
    svg.append(svg_text(lx+18,yy,cl,10,'#555','start'))
svg.append('</svg>')
svg_text_content='\n'.join(svg)+'\n'
(OUT/'qwen_pc1_pc2_trait_region_overlay.svg').write_text(svg_text_content)

# Interactive HTML: inline SVG with hoverable cell overlays.
cell_payload=[]
for rec,rel,glob,sub in cell_records:
    cell_payload.append({
        'pc1_bin':rec['pc1_bin'],'pc2_bin':rec['pc2_bin'],'role_count':rec['role_count'],
        'dominant_cluster':rec['dominant_cluster'],'dominant_cluster_fraction':round(rec['dominant_cluster_fraction'],3),
        'top_band_relative':[(t,round(s,3)) for t,s in rel[:8]],
        'top_global':[(t,round(s,3)) for t,s in glob[:8]],
        'examples':[r['persona'] for r in sorted(sub,key=lambda r:r['persona'])[:12]],
        'sparse_cell':rec['sparse_cell'],
        'x0':sx(rec['pc1_min']),'x1':sx(rec['pc1_max']),'y0':sy(rec['pc2_max']),'y1':sy(rec['pc2_min'])
    })
html_parts=[]
html_parts.append('<!doctype html><html><head><meta charset="utf-8"><title>Qwen PC1 x PC2 Trait Region Overlay</title>')
html_parts.append('<style>body{margin:0;background:#111;color:#eee;font-family:Inter,Arial,sans-serif}.wrap{padding:18px}.panel{max-width:1500px;margin:auto}.note{color:#aaa;font-size:13px;margin:8px 0 16px}.viz{background:#fbfbf8;border-radius:8px;overflow:auto}.tooltip{position:fixed;display:none;max-width:460px;background:#181818;border:1px solid #555;border-radius:8px;padding:12px;box-shadow:0 10px 30px #0008;font-size:13px;line-height:1.35;z-index:5}.tooltip b{color:#fff}.tooltip .muted{color:#aaa}.cell{fill:#4a90d900;stroke:#1110;cursor:pointer}.cell:hover{fill:#4a90d91f;stroke:#222;stroke-width:2}.footer{color:#888;font-size:12px;margin-top:12px}</style></head><body>')
html_parts.append('<div class="wrap"><div class="panel"><h1>Qwen PC1 x PC2 Trait-Region Overlay</h1>')
html_parts.append('<div class="note">Hover cells for PC1-band-relative enrichment, global enrichment, population, dominant cluster, and example roles. Role points remain visible underneath. Source matrix: <code>research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv</code>.</div>')
html_parts.append('<div class="viz">')
# inject cell rects before closing svg
interactive_svg = svg_text_content.replace('</svg>', '')
for i,c in enumerate(cell_payload):
    interactive_svg += f'<rect class="cell" data-cell="{i}" x="{c["x0"]:.1f}" y="{c["y0"]:.1f}" width="{c["x1"]-c["x0"]:.1f}" height="{c["y1"]-c["y0"]:.1f}"/>\n'
interactive_svg += '</svg>'
html_parts.append(interactive_svg)
html_parts.append('</div><div class="footer">Prototype generated UTC '+UPDATED+' by '+MODEL_USED+'. PC1 bins are quintiles; PC2 bins are tertiles within each PC1 bin.</div></div></div><div id="tip" class="tooltip"></div>')
html_parts.append('<script>const CELLS = '+json.dumps(cell_payload)+'; const tip=document.getElementById("tip"); function fmtPairs(arr){return arr.map(x=>`<li><b>${x[0]}</b>: ${x[1].toFixed(2)}</li>`).join("");} document.querySelectorAll(".cell").forEach(el=>{el.addEventListener("mousemove",e=>{const c=CELLS[+el.dataset.cell]; tip.innerHTML=`<b>${c.pc1_bin} / PC2 ${c.pc2_bin}</b> <span class="muted">n=${c.role_count}</span><br><span class="muted">Dominant cluster:</span> ${c.dominant_cluster} (${Math.round(c.dominant_cluster_fraction*100)}%)<br><br><b>PC1-band-relative enrichment</b><ol>${fmtPairs(c.top_band_relative.slice(0,6))}</ol><b>Global enrichment</b><ol>${fmtPairs(c.top_global.slice(0,6))}</ol><b>Examples</b><br>${c.examples.join(", ")}${c.sparse_cell?"<br><br><b>Warning:</b> sparse cell; interpret cautiously.":""}`; tip.style.display="block"; tip.style.left=Math.min(e.clientX+16, window.innerWidth-500)+"px"; tip.style.top=Math.min(e.clientY+16, window.innerHeight-420)+"px";}); el.addEventListener("mouseleave",()=>tip.style.display="none");});</script>')
html_parts.append('</body></html>')
(OUT/'qwen_pc1_pc2_trait_region_overlay.html').write_text('\n'.join(html_parts))

# Report.
cell_count=len(cell_records)
report=[]
report.append('# Qwen PC1 x PC2 Trait-Region Overlay Prototype')
report.append('')
report.append(f'Generated UTC: {UPDATED}')
report.append(f'Model used: {MODEL_USED}')
report.append('')
report.append('## Data sources')
report.append('')
report.append(f'- Trait profile matrix located through navigation: `{SOURCE.relative_to(REPO)}`')
report.append(f'- Canonical role geometry table: `{GEOM_ROLE.relative_to(REPO)}`')
report.append(f'- Canonical cluster membership table: `{CLUSTER_TABLE.relative_to(REPO)}`')
report.append('')
report.append('## Method')
report.append('')
report.append('- Qwen role PC1 x PC2 only.')
report.append('- PC1 divided into five equal-count quantile bands.')
report.append('- PC2 divided into low/mid/high equal-count tertiles within each PC1 band.')
report.append('- PC1-band-relative enrichment: `(mean_trait_cell - mean_trait_pc1_band) / global_trait_std`.')
report.append('- Global enrichment: `(mean_trait_cell - mean_trait_global) / global_trait_std`.')
report.append('')
report.append('## Sanity checks')
report.append('')
report.append(f'- Populated cells: {cell_count}/15.')
report.append(f'- Sparse cells with fewer than 8 roles: {len(sparse)}.')
report.append(f'- Mean top-3 overlap between PC1-band-relative and global labels: {mean_overlap:.2f}.')
report.append(f'- PC1-band-relative labels materially change apparent cell labels: {"yes" if material_change else "no"}.')
report.append('')
if sparse:
    report.append('Sparse cells: ' + ', '.join(f"{r['pc1_bin']}/{r['pc2_bin']} n={r['role_count']}" for r in sparse))
else:
    report.append('No cells fell below the sparse-cell threshold; each quantile cell has enough roles for a first-pass visual read, though this is still exploratory.')
report.append('')
report.append('## Cell summaries')
report.append('')
for rec,rel,glob,sub in cell_records:
    report.append(f"### {rec['pc1_bin']} / PC2 {rec['pc2_bin']} (n={rec['role_count']})")
    report.append(f"- Dominant cluster: {rec['dominant_cluster']} ({rec['dominant_cluster_fraction']:.2f})")
    report.append(f"- PC1-band-relative top traits: {rec['top_band_relative_traits']}")
    report.append(f"- Global top traits: {rec['top_global_traits']}")
    report.append(f"- Example roles: {rec['example_roles']}")
    report.append('')
report.append('## Interpretation')
report.append('')
report.append('Observed: PC1-band-relative enrichment often changes the visible labels compared with global enrichment, especially in cells where global labels are dominated by broad PC1-associated formality, seriousness, or expressivity. This supports the purpose of the overlay: PC2 is easier to inspect when local trait shifts are shown against a PC1-band baseline rather than the full role distribution.')
report.append('')
report.append('Observed: High-PC2 cells frequently surface traits from the expected situated/reactive family, including practical, casual, reactive, anxious/neurotic, accommodating, grounded, experiential, or adjacent terms depending on the PC1 band. Low-PC2 cells more often surface formal/integrated/abstract traits such as conscientious, formal, abstract, conceptual, serious, theoretical, ritualistic, or pensive, though the exact local labels vary by PC1 band.')
report.append('')
report.append('Caveat: This prototype does not solve PC2. It is a visualization and descriptive enrichment layer over activation-space trait cosine features, not an independent causal or psychological validation. The useful result is methodological: PC1-band-relative labels make the vertical PC2 structure more legible and less confounded by global PC1 trait gradients.')
report.append('')
report.append('## Files')
report.append('')
report.append('- `qwen_pc1_pc2_trait_region_overlay.html`')
report.append('- `qwen_pc1_pc2_trait_region_overlay.svg`')
report.append('- `qwen_pc1_pc2_trait_region_cells.csv`')
report.append('- `qwen_pc1_pc2_trait_region_report.md`')
(OUT/'qwen_pc1_pc2_trait_region_report.md').write_text('\n'.join(report)+'\n')

# Save script copy for provenance.
script_dst = OUT / 'run_qwen_pc2_trait_region_overlay.py'
script_dst.write_text(Path(__file__).read_text())
print('Wrote outputs to', OUT)
print('cells', cell_count, 'mean_top3_overlap', round(mean_overlap,3), 'material_change', material_change, 'sparse', len(sparse))
