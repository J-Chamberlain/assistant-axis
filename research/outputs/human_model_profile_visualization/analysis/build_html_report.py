#!/usr/bin/env python3
"""Build a self-contained reader-first HTML inspection report."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve()
OUT = HERE.parents[1]
REPO = HERE.parents[4]
DATA = OUT / "data"
FIG = OUT / "figures"
HTML = OUT / "human_model_profile_visualization.html"


def records(name: str) -> list[dict]:
    df = pd.read_csv(DATA / name)
    return json.loads(df.to_json(orient="records"))


def image_uri(path: Path) -> str:
    mime = "image/png" if path.suffix == ".png" else "image/svg+xml"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def main() -> None:
    image_paths = sorted(FIG.glob("*.png"))
    images = {p.stem: image_uri(p) for p in image_paths}
    data = {
        "shapes": records("primary_matched_profile_shapes.csv"),
        "drivers": records("top_trait_drivers.csv"),
        "traitMetadata": records("trait_metadata.csv"),
        "kProgression": records("k_progression.csv"),
        "familyBest": records("family_best_by_k.csv"),
        "assignmentEvolution": records("assignment_evolution.csv"),
        "traitSetComparison": records("trait_set_comparison.csv"),
        "replication": records("model_specific_replication.csv"),
        "familyStatistics": records("family_specific_statistics.csv"),
        "sapa": records("sapa_language_profiles.csv"),
    }
    template = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AA-12 Human ↔ Model Profile Correspondence — Inspection Packet</title>
<style>
:root{--ink:#172033;--muted:#5e687a;--paper:#f5f2eb;--card:#fff;--line:#d9dce3;--a:#1878b4;--b:#d99100;--c:#009c76;--d:#e06b00;--e:#7a5195;--human:#222b45;--accent:#c23b4a}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:#245a92}header{background:linear-gradient(125deg,#172033,#2d4267 62%,#315f61);color:white;padding:60px max(5vw,24px) 48px}.eyebrow{letter-spacing:.14em;text-transform:uppercase;font-size:.78rem;color:#cbd8ef;font-weight:700}h1{font-size:clamp(2.2rem,5vw,4.7rem);line-height:1.03;max-width:1100px;margin:.2em 0}.lede{max-width:900px;font-size:1.2rem;color:#e7ebf2}.badges{display:flex;gap:10px;flex-wrap:wrap;margin:25px 0}.badge{border:1px solid #7890ae;border-radius:999px;padding:7px 12px;background:#ffffff12;font-size:.85rem}.metrics{display:grid;grid-template-columns:repeat(4,minmax(145px,1fr));gap:12px;max-width:980px;margin-top:28px}.metric{background:#ffffff12;border:1px solid #ffffff24;border-radius:12px;padding:16px}.metric b{font-size:1.65rem;display:block}.metric span{font-size:.78rem;color:#dce4ef}nav{position:sticky;top:0;z-index:10;background:#fffefbf2;border-bottom:1px solid var(--line);padding:10px max(4vw,20px);backdrop-filter:blur(9px);overflow:auto;white-space:nowrap}nav a{margin-right:18px;text-decoration:none;font-size:.86rem;color:#3d4655}.wrap{max-width:1440px;margin:auto;padding:34px max(4vw,22px) 80px}section{scroll-margin-top:58px;margin:0 0 55px}h2{font-size:2rem;margin-bottom:.2em}h3{font-size:1.25rem;margin-top:1.7em}.section-intro{color:var(--muted);max-width:900px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:0 5px 20px #1720330b}.card img{width:100%;height:auto;display:block}.full{grid-column:1/-1}.callout{border-left:5px solid #4c759c;background:#edf3f6;padding:16px 18px;border-radius:6px;margin:18px 0}.warn{border-left-color:#bb6c20;background:#fff4e7}.family-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.family{border-top:5px solid var(--color);background:white;border-radius:10px;padding:14px;border-left:1px solid var(--line);border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.family b,.family span,.family small{display:block}.family b{font-size:1.05rem}.family small{color:var(--muted);margin-top:4px}label{font-weight:650;font-size:.88rem}.controls{display:flex;gap:16px;flex-wrap:wrap;align-items:end;margin:14px 0}select,input{font:inherit;border:1px solid #aeb5c1;border-radius:7px;background:white;padding:8px 10px}.chart-shell{overflow:auto;border:1px solid var(--line);border-radius:10px;background:#fff;padding:8px}#profileChart{min-width:1050px;width:100%;height:460px}.legend{display:flex;gap:18px;align-items:center;font-size:.86rem;color:var(--muted)}.swatch{display:inline-block;width:20px;height:3px;vertical-align:middle;margin-right:5px}.table-wrap{overflow:auto;max-height:580px;border:1px solid var(--line);border-radius:8px;background:white}table{border-collapse:collapse;width:100%;font-size:.84rem}th,td{padding:8px 10px;border-bottom:1px solid #eceef2;text-align:left;white-space:nowrap}th{position:sticky;top:0;background:#edf0f5;z-index:1}tr:hover td{background:#f7f8fa}.pill{display:inline-block;padding:2px 7px;border-radius:999px;background:#e8edf3;font-size:.75rem}.note{font-size:.82rem;color:var(--muted)}.heatmap-controls button{border:1px solid #9ca6b5;background:#fff;padding:7px 12px;border-radius:6px;margin:2px;cursor:pointer}.heatmap-controls button.active{background:#273d5c;color:white}.figure-caption{color:var(--muted);font-size:.84rem;margin:.7em 0 0}.boundary-list{columns:2;column-gap:36px}.boundary-list li{break-inside:avoid;margin-bottom:7px}.report-footer{border-top:1px solid var(--line);padding-top:22px;color:var(--muted);font-size:.84rem}.only-screen-reader{position:absolute;left:-9999px}@media(max-width:850px){.metrics,.family-row,.grid{grid-template-columns:1fr}.full{grid-column:auto}.boundary-list{columns:1}header{padding-top:35px}}
</style>
</head>
<body>
<header>
  <div class="eyebrow">AA-12 · Follow-up 5 · Frozen-result inspection packet</div>
  <h1>Human ↔ model profile correspondence, made inspectable</h1>
  <p class="lede">A reader-first view of the preregistered aggregate result. It shows what aligns trait by trait, what does not, how exact assignments change with human resolution, and why strong global structure is not the same thing as a stable four-type taxonomy.</p>
  <div class="badges"><span class="badge">Aggregate profiles only</span><span class="badge">45 frozen direct mappings</span><span class="badge">No re-optimization</span><span class="badge">No respondent projection</span></div>
  <div class="metrics">
    <div class="metric"><b>0.520</b><span>primary mean r at K=10</span></div>
    <div class="metric"><b>0.000050</b><span>full-search adjusted p</span></div>
    <div class="metric"><b>3 / 4</b><span>families pass adjusted max tests</span></div>
    <div class="metric"><b>96</b><span>distinct SAPA evidence items</span></div>
  </div>
</header>
<nav><a href="#overview">Overview</a><a href="#shapes">Matched shapes</a><a href="#drivers">Trait drivers</a><a href="#resolution">Resolution</a><a href="#matrices">Matrices</a><a href="#competition">C/D/E</a><a href="#sensitivity">45 vs 12</a><a href="#null">Null</a><a href="#sapa">SAPA language</a><a href="#boundaries">Boundaries</a></nav>
<main class="wrap">
<section id="overview">
  <h2>One-screen result summary</h2>
  <p class="section-intro">The frozen primary statistic is the maximum mean Fisher-z across injective A–D assignments and eligible human K. Its permutation null repeats that entire search. The result clears the preregistered strong aggregate tier, while several views below show why exact profile identities remain qualified.</p>
  <div class="family-row">
    <div class="family" style="--color:var(--a)"><b>MFamily_A ↔ H10_C</b><span>r=.519 · ρ=.473</span><small>Strongest family-specific pair is H06_A, r=.624.</small></div>
    <div class="family" style="--color:var(--b)"><b>MFamily_B ↔ H10_J</b><span>r=.394 · ρ=.501</span><small>Adjusted family-specific p=.0535: marginal.</small></div>
    <div class="family" style="--color:var(--c)"><b>MFamily_C ↔ H10_G</b><span>r=.319 · ρ=.283</span><small>Unconstrained C instead selects H10_I, which D also selects.</small></div>
    <div class="family" style="--color:var(--d)"><b>MFamily_D ↔ H10_I</b><span>r=.755 · ρ=.735</span><small>Strongest and most cross-model-consistent primary pair.</small></div>
  </div>
  <div class="callout"><b>What the evidence supports.</b> Independently frozen aggregate human and model profile shapes correspond through the pre-existing coordinate-blind trait bridge more strongly than expected after the complete assignment and K search.</div>
  <div class="callout warn"><b>What it does not support.</b> These are not four natural human types. Correlation is relative profile-shape similarity—not percent identity, percent of people, probability of equivalence, or population prevalence.</div>
</section>

<section id="shapes">
  <h2>Primary matched shapes</h2>
  <p class="section-intro">Choose a frozen family, trait ordering, and model representation. The three individual-model options retain the K=10 human counterpart fixed; they do not reassign profiles.</p>
  <div class="card">
    <div class="controls">
      <div><label for="familySelect">Family</label><br><select id="familySelect"><option>MFamily_A</option><option>MFamily_B</option><option>MFamily_C</option><option>MFamily_D</option></select></div>
      <div><label for="orderSelect">Trait order</label><br><select id="orderSelect"><option value="canonical_order">Canonical bridge order</option><option value="grouped_order">Frozen measurement-support grouping</option></select></div>
      <div><label for="modelSelect">Model profile</label><br><select id="modelSelect"><option value="model_consensus_value">Three-model consensus</option><option value="qwen_value">Qwen</option><option value="llama_value">LLaMA</option><option value="gemma_value">Gemma</option></select></div>
      <div id="profileStat" class="pill"></div>
    </div>
    <div class="legend"><span><i class="swatch" style="background:var(--human)"></i>human</span><span><i class="swatch" style="background:var(--accent)"></i>selected model representation</span><span>● trait belongs to 12-trait core</span></div>
    <div class="chart-shell"><svg id="profileChart" role="img" aria-label="Interactive human and model trait profile"></svg></div>
  </div>
  <div class="grid" style="margin-top:22px">
    <figure class="card"><img data-img="01_primary_matched_shapes_canonical" alt="Four primary matched profile shapes in canonical order"><figcaption class="figure-caption">Canonical bridge order; identical across A–D.</figcaption></figure>
    <figure class="card"><img data-img="01b_primary_matched_shapes_measurement_grouped" alt="Four primary matched shapes grouped by frozen measurement tier"><figcaption class="figure-caption">Grouped using pre-result measurement-support metadata—not observed agreement.</figcaption></figure>
  </div>
</section>

<section id="drivers">
  <h2>Trait-by-trait agreement and disagreement</h2>
  <p class="section-intro">Covariance contribution is the centered product requested for inspection. It decomposes profile similarity descriptively; no trait is given an individual inferential p-value.</p>
  <div class="grid">
    <figure class="card full"><img data-img="02_trait_decomposition_all_traits" alt="All-trait covariance contributions and signed differences"></figure>
    <figure class="card full"><img data-img="02b_top_trait_drivers" alt="Top contributors and disagreements by pair"></figure>
  </div>
  <div class="card">
    <div class="controls"><div><label for="driverFamily">Inspect family</label><br><select id="driverFamily"><option>MFamily_A</option><option>MFamily_B</option><option>MFamily_C</option><option>MFamily_D</option></select></div><div><label for="driverType">View</label><br><select id="driverType"><option value="top_positive_covariance_contribution">Top positive contributors</option><option value="top_absolute_disagreement">Largest disagreements</option></select></div></div>
    <div class="table-wrap"><table id="driverTable"><thead><tr><th>Rank</th><th>Trait</th><th>Human</th><th>Model</th><th>Contribution</th><th>Human−model</th><th>Human support</th><th>12 core</th><th>Single item</th><th>Redundant/broad</th></tr></thead><tbody></tbody></table></div>
  </div>
  <figure class="card"><img data-img="03_primary_pair_heatmap" alt="Compact paired 45-trait heatmap"><figcaption class="figure-caption">All four primary pairs on one common standardized color scale.</figcaption></figure>
</section>

<section id="resolution">
  <h2>What changes with human resolution?</h2>
  <p class="section-intro">The global score rises overall but is not monotone. K=10 maximizes the frozen search while carrying low split-refit stability; the moderate-stability K=4–6 subset still retains recognizable and significant structure.</p>
  <div class="grid">
    <figure class="card"><img data-img="04_k_progression" alt="Correspondence score by K"></figure>
    <figure class="card"><img data-img="05_family_best_across_k" alt="Best human profile similarity by family and K"></figure>
    <figure class="card"><img data-img="06_assignment_evolution_matrix" alt="Injective assignment evolution matrix"></figure>
    <figure class="card"><img data-img="07_human_profile_continuity_reused" alt="Frozen human profile continuity paths"></figure>
  </div>
</section>

<section id="matrices">
  <h2>Full human × model similarity matrices</h2>
  <p class="section-intro">The primary A–D columns and secondary E column are shown together, but separated visually. Markers distinguish the injective primary assignment from each family’s unconstrained maximum.</p>
  <div class="card">
    <div class="heatmap-controls" id="heatmapButtons"><button data-k="04">K4</button><button data-k="05">K5</button><button data-k="06">K6</button><button data-k="07">K7</button><button data-k="08">K8</button><button class="active" data-k="10">K10</button></div>
    <img id="heatmapImage" data-img="08_similarity_matrix_k10" alt="Selectable human by model family heatmap">
    <p class="figure-caption">● injective assignment · ▲ unconstrained best at this K · † frozen top-two ambiguity. E remains secondary.</p>
  </div>
</section>

<section id="competition">
  <h2>C, D, and E compete for the same human-profile region</h2>
  <div class="grid">
    <figure class="card full"><img data-img="09_cde_competition" alt="C D E competition heatmap and profile shapes"><figcaption class="figure-caption">Both mechanisms are visible: the model profiles share some bridge pattern, and H10_I is broadly aligned with several of them. The packet does not resolve that ambiguity by redefining families.</figcaption></figure>
    <figure class="card full"><img data-img="10_ad_exemplars" alt="A and D exemplar comparisons"><figcaption class="figure-caption">A illustrates why broad family evidence can peak outside the primary maximizing K; D illustrates the clearest fixed correspondence.</figcaption></figure>
    <figure class="card full"><img data-img="14_family_specific_statistics" alt="Family specific maxima and adjusted p values"></figure>
  </div>
</section>

<section id="sensitivity">
  <h2>45 traits versus the conservative 12-trait core</h2>
  <p class="section-intro">The separately permuted 12-trait pipeline is globally concordant, but only A keeps the same K=10 pair identity. This is the clearest visual distinction between a robust aggregate pattern and an unstable exact taxonomy.</p>
  <figure class="card"><img data-img="11_trait_set_comparison" alt="45 versus 12 trait assignment comparison"></figure>
  <div class="card">
    <div class="controls"><div><label for="traitSetSelect">Assignment representation</label><br><select id="traitSetSelect"><option value="45_ACCEPT_DIRECT">45 direct traits</option><option value="12_HUMAN_SUPPORTED">12 supported traits</option></select></div></div>
    <div class="table-wrap"><table id="traitSetTable"><thead><tr><th>Family</th><th>Selected human profile</th><th>r</th><th>ρ</th><th>Same as 45-trait pair?</th><th>Global mean r</th><th>Global adjusted p</th></tr></thead><tbody></tbody></table></div>
  </div>
  <h3>Fixed-pair model replication</h3>
  <figure class="card"><img data-img="12_model_specific_replication_reused" alt="Consensus Qwen LLaMA Gemma fixed pair correlations"><figcaption class="figure-caption">No model-specific reassignment. D is consistent; C is materially weaker in Qwen; all fixed-pair signs remain positive.</figcaption></figure>
</section>

<section id="null">
  <h2>The observed maximum is separated from the full-search null</h2>
  <figure class="card"><img data-img="13_primary_permutation_null" alt="Search-adjusted bridge permutation null"><figcaption class="figure-caption">This is not an ordinary pairwise-correlation p-value. Each of 20,000 draws repeated all profile correlations, injective assignment optimization, and the complete eligible-K search.</figcaption></figure>
  <div class="callout"><b>Frozen result:</b> 0 / 20,000 permuted maxima reached the observed Fisher-z of 0.576571; empirical p = 1 / 20,001 = 0.000050.</div>
</section>

<section id="sapa">
  <h2>Human profiles in SAPA’s own language</h2>
  <p class="section-intro">The static view includes all 96 unique items. Use the controls below to search the exact unshortened wording and inspect aggregate expected responses and observed-only standardized values.</p>
  <figure class="card"><img data-img="15_sapa_language_profiles" alt="All 96 SAPA items for selected human profiles"></figure>
  <div class="card">
    <div class="controls"><div><label for="sapaProfile">Human profile</label><br><select id="sapaProfile"><option>H10_C</option><option>H10_J</option><option>H10_G</option><option>H10_I</option><option>H06_A</option></select></div><div><label for="sapaSearch">Search exact wording or trait</label><br><input id="sapaSearch" size="34" placeholder="e.g. worry, adventure, forgiving"></div><div id="sapaCount" class="pill"></div></div>
    <div class="table-wrap"><table id="sapaTable"><thead><tr><th>Trait</th><th>Item ID</th><th>Exact SAPA wording</th><th>Expected response</th><th>Oriented z</th><th>Observed n</th></tr></thead><tbody></tbody></table></div>
  </div>
</section>

<section id="boundaries">
  <h2>Interpretation boundaries</h2>
  <ul class="boundary-list">
    <li>No new correspondence test or null</li><li>No human-profile refit</li><li>No model reclustering or family change</li><li>No K eligibility change</li><li>No bridge row, orientation, or normalization change</li><li>No ACCEPT_CLOSE traits</li><li>No respondent projection or individual output</li><li>No psychometric or prevalence equivalence</li><li>No PC-informed remapping</li><li>No new inference or activation extraction</li><li>No external model API</li><li>No GPU or RunPod</li>
  </ul>
  <p class="note">Observed visual patterns are decompositions of frozen evidence. They are not new tested claims. Semantic subtitles remain restrained descriptions created only after the numerical freeze.</p>
</section>
<footer class="report-footer">Built deterministically from AA-12 follow-up-4 aggregate artifacts. Self-contained: all data, JavaScript, CSS, and displayed images are embedded; no network request is required.</footer>
</main>
<script id="packetData" type="application/json">__DATA_JSON__</script>
<script id="packetImages" type="application/json">__IMAGE_JSON__</script>
<script>
const D=JSON.parse(document.getElementById('packetData').textContent), IM=JSON.parse(document.getElementById('packetImages').textContent);
document.querySelectorAll('[data-img]').forEach(el=>{el.src=IM[el.dataset.img]});
const familyColors={MFamily_A:'#1878b4',MFamily_B:'#d99100',MFamily_C:'#009c76',MFamily_D:'#e06b00',MFamily_E:'#7a5195'};
function pearson(a,b){const am=a.reduce((x,y)=>x+y,0)/a.length,bm=b.reduce((x,y)=>x+y,0)/b.length;let n=0,da=0,db=0;for(let i=0;i<a.length;i++){const x=a[i]-am,y=b[i]-bm;n+=x*y;da+=x*x;db+=y*y}return n/Math.sqrt(da*db)}
function renderProfile(){
  const fam=document.getElementById('familySelect').value, order=document.getElementById('orderSelect').value, modelKey=document.getElementById('modelSelect').value;
  const rows=D.shapes.filter(x=>x.model_family_id===fam).sort((a,b)=>a[order]-b[order]); const svg=document.getElementById('profileChart');
  const W=1200,H=450,L=62,R=24,T=25,B=150,iw=W-L-R,ih=H-T-B; const vals=rows.flatMap(x=>[x.human_value,x[modelKey]]); const pad=.18, ymin=Math.min(...vals)-pad,ymax=Math.max(...vals)+pad;
  const X=i=>L+i*iw/(rows.length-1),Y=v=>T+(ymax-v)*ih/(ymax-ymin); const path=key=>rows.map((r,i)=>(i?'L':'M')+X(i).toFixed(1)+','+Y(r[key]).toFixed(1)).join(' ');
  let s=`<rect width="${W}" height="${H}" fill="white"/><line x1="${L}" y1="${Y(0)}" x2="${W-R}" y2="${Y(0)}" stroke="#a9aeb8"/>`;
  for(let q=0;q<5;q++){const v=ymin+q*(ymax-ymin)/4,y=Y(v);s+=`<line x1="${L}" y1="${y}" x2="${W-R}" y2="${y}" stroke="#eceef2"/><text x="${L-8}" y="${y+4}" text-anchor="end" font-size="11" fill="#626b79">${v.toFixed(1)}</text>`}
  s+=`<path d="${path('human_value')}" fill="none" stroke="#222b45" stroke-width="3"/><path d="${path(modelKey)}" fill="none" stroke="${familyColors[fam]}" stroke-width="3"/>`;
  rows.forEach((r,i)=>{const x=X(i);s+=`<circle cx="${x}" cy="${Y(r.human_value)}" r="3.2" fill="#222b45"><title>${r.trait}: human ${r.human_value.toFixed(3)}</title></circle><rect x="${x-3}" y="${Y(r[modelKey])-3}" width="6" height="6" fill="${familyColors[fam]}"><title>${r.trait}: model ${r[modelKey].toFixed(3)}</title></rect><text transform="translate(${x},${H-B+12}) rotate(62)" text-anchor="start" font-size="10" fill="${r.is_12_trait_core?'#9b5a00':'#4e5664'}">${r.trait}${r.is_12_trait_core?' ●':''}</text>`});
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.innerHTML=s;
  const r=pearson(rows.map(x=>x.human_value),rows.map(x=>x[modelKey]));document.getElementById('profileStat').textContent=`${rows[0].human_profile_id} · ${modelKey==='model_consensus_value'?'frozen consensus r':'fixed-pair descriptive r'}=${r.toFixed(3)}`;
}
['familySelect','orderSelect','modelSelect'].forEach(id=>document.getElementById(id).addEventListener('change',renderProfile));renderProfile();
function renderDrivers(){const fam=document.getElementById('driverFamily').value,type=document.getElementById('driverType').value;const rows=D.drivers.filter(x=>x.model_family_id===fam&&x.driver_type===type).sort((a,b)=>a.rank-b.rank);document.querySelector('#driverTable tbody').innerHTML=rows.map(r=>`<tr><td>${r.rank}</td><td><b>${r.trait}</b></td><td>${r.human_value.toFixed(3)}</td><td>${r.model_consensus_value.toFixed(3)}</td><td>${r.covariance_contribution.toFixed(3)}</td><td>${r.signed_difference_human_minus_model.toFixed(3)}</td><td>${r.human_measurement_support_tier}</td><td>${r.is_12_trait_core?'yes':'no'}</td><td>${r.single_item_flag?'yes':'no'}</td><td>${r.redundant_or_broad_flag?'yes':'no'}</td></tr>`).join('')}
['driverFamily','driverType'].forEach(id=>document.getElementById(id).addEventListener('change',renderDrivers));renderDrivers();
document.querySelectorAll('#heatmapButtons button').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('#heatmapButtons button').forEach(x=>x.classList.remove('active'));btn.classList.add('active');document.getElementById('heatmapImage').src=IM['08_similarity_matrix_k'+btn.dataset.k]}));
function renderTraitSet(){const set=document.getElementById('traitSetSelect').value,rows=D.traitSetComparison.filter(x=>x.trait_set===set);document.querySelector('#traitSetTable tbody').innerHTML=rows.map(r=>`<tr><td>${r.model_family_id}</td><td><b>${r.selected_human_profile_id}</b></td><td>${r.selected_pearson_r.toFixed(3)}</td><td>${r.selected_spearman_rho.toFixed(3)}</td><td>${r.same_profile_as_45_trait_assignment?'yes':'no'}</td><td>${r.global_back_transformed_mean_r.toFixed(3)}</td><td>${r.global_search_adjusted_p.toFixed(6)}</td></tr>`).join('')}
document.getElementById('traitSetSelect').addEventListener('change',renderTraitSet);renderTraitSet();
function renderSapa(){const hp=document.getElementById('sapaProfile').value,q=document.getElementById('sapaSearch').value.toLowerCase().trim();const rows=D.sapa.filter(x=>x.profile_id===hp&&(!q||(x.item_text+' '+x.primary_frozen_trait_owner+' '+x.item_id).toLowerCase().includes(q))).sort((a,b)=>a.visualization_order-b.visualization_order);document.querySelector('#sapaTable tbody').innerHTML=rows.map(r=>`<tr><td>${r.primary_frozen_trait_owner}</td><td>${r.item_id}</td><td>${r.item_text}</td><td>${r.expected_response.toFixed(3)}</td><td>${r.oriented_item_z.toFixed(3)}</td><td>${r.observed_n}</td></tr>`).join('');document.getElementById('sapaCount').textContent=`${rows.length} of 96 items`}
document.getElementById('sapaProfile').addEventListener('change',renderSapa);document.getElementById('sapaSearch').addEventListener('input',renderSapa);renderSapa();
</script>
</body>
</html>'''
    rendered = template.replace("__DATA_JSON__", json.dumps(data, separators=(",", ":"), sort_keys=True).replace("</", "<\\/"))
    rendered = rendered.replace("__IMAGE_JSON__", json.dumps(images, separators=(",", ":"), sort_keys=True))
    HTML.write_text(rendered, encoding="utf-8")
    print(f"Wrote self-contained HTML: {HTML.relative_to(REPO)} ({HTML.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
