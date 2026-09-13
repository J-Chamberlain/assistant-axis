#!/usr/bin/env python3
"""Build the standalone self-contained persona coverage terrain viewer."""

from __future__ import annotations

import json
from pathlib import Path

from plotly.offline import get_plotlyjs


HERE = Path(__file__).resolve().parent
OUT = HERE.parent


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Model-only persona-space coverage terrain viewer</title>
<script>__PLOTLY__</script>
<style>
:root{--ink:#152432;--muted:#5c6d7a;--line:#d9e2e8;--panel:#f5f8fa;--accent:#226ba7;--warning:#fff5d8;--shadow:0 12px 32px rgba(24,48,68,.10)}
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink);background:#fff;line-height:1.42}
header{padding:26px clamp(18px,4vw,52px) 18px;border-bottom:1px solid var(--line)}h1{font-size:clamp(25px,3vw,39px);font-weight:650;margin:0 0 7px;letter-spacing:-.025em}header p{margin:0;color:var(--muted);max-width:960px}
.warning{margin:16px clamp(18px,4vw,52px) 0;padding:12px 15px;background:var(--warning);border-left:4px solid #d59a00;font-weight:600}
.shell{display:grid;grid-template-columns:minmax(220px,290px) minmax(0,1fr);gap:18px;padding:18px clamp(18px,4vw,52px) 30px}.controls{background:var(--panel);padding:15px;border:1px solid var(--line);border-radius:10px;align-self:start}.group{padding:0 0 13px;margin:0 0 13px;border-bottom:1px solid var(--line)}.group:last-child{border:0;margin:0;padding:0}
label,.label{display:block;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.045em;color:var(--muted);margin:0 0 5px}select,input[type="search"]{width:100%;padding:8px 9px;border:1px solid #b9c6cf;border-radius:6px;background:white;color:var(--ink);font-size:14px;margin-bottom:8px}.checks{display:grid;grid-template-columns:1fr 1fr;gap:6px 8px}.checks label{display:flex;align-items:center;gap:6px;text-transform:none;letter-spacing:0;font-size:13px;font-weight:500;color:var(--ink);margin:0}.buttons{display:flex;flex-wrap:wrap;gap:7px}button{border:1px solid #a9bac6;background:#fff;color:var(--ink);border-radius:6px;padding:7px 10px;font-weight:600;cursor:pointer}button:hover{border-color:var(--accent);color:var(--accent)}button.primary{background:var(--accent);color:white;border-color:var(--accent)}
.main{min-width:0}.plot-wrap{border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow);overflow:hidden;background:white}.plot{width:100%;height:min(72vh,760px);min-height:560px}.status{padding:9px 13px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}.detail{margin-top:14px;display:grid;grid-template-columns:minmax(0,1fr) minmax(240px,360px);gap:14px}.detail section{border:1px solid var(--line);border-radius:10px;padding:14px}.detail h2{font-size:16px;margin:0 0 8px}.detail p{margin:5px 0;color:var(--muted)}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:6px 7px;border-bottom:1px solid #e7edf1}th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.04em}.note{font-size:12px;color:var(--muted)}.legend{display:flex;flex-wrap:wrap;gap:7px 12px;font-size:12px;margin-top:6px}.swatch{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:4px}.methods{padding:0 clamp(18px,4vw,52px) 38px;max-width:1200px}.methods h2{font-size:20px}.methods li{margin:5px 0;color:var(--muted)}code{font-size:12px}
@media(max-width:900px){.shell{grid-template-columns:1fr}.controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.group{border:0;margin:0;padding:0}.detail{grid-template-columns:1fr}.plot{height:620px}.warning{font-size:14px}}@media(max-width:560px){.controls{grid-template-columns:1fr}.plot{min-height:500px;height:62vh}header{padding-top:18px}}
</style>
</head>
<body>
<header>
  <h1>Persona-space coverage terrain</h1>
  <p>Explore where the same 275 curated roles occupy each model's frozen native PC1–PC3 geometry, how locally dense or sparse that sample is, and where reconciled model families sit.</p>
</header>
<div class="warning">Coverage reflects the selected 275-role inventory. It is not a population probability distribution.</div>
<div class="shell">
  <aside class="controls" aria-label="Terrain controls">
    <div class="group"><label for="model">Model</label><select id="model"><option value="qwen">Qwen 3 32B</option><option value="llama">LLaMA 3.3 70B</option><option value="gemma">Gemma 2 27B</option></select>
      <label for="view">View</label><select id="view"><option value="3d">Native PC1–PC3</option><option value="pc1_pc2">Native PC1 × PC2</option><option value="pc1_pc3">Native PC1 × PC3</option><option value="pc2_pc3">Native PC2 × PC3</option><option value="compare_native">Linked native comparison</option><option value="compare_aligned">Display-aligned shared-role overlay</option></select>
      <label for="mode">Color / terrain mode</label><select id="mode"><option value="occupancy">Occupancy cloud</option><option value="points">Persona points</option><option value="density">Sample density</option><option value="sparsity">Sample sparsity</option><option value="families">Consensus families</option></select></div>
    <div class="group"><span class="label">Layers</span><div class="checks">
      <label><input id="showPoints" type="checkbox" checked> Persona nodes</label><label><input id="showSurface" type="checkbox" checked> Density surface</label>
      <label><input id="showHulls" type="checkbox"> Family envelopes</label><label><input id="showTraits" type="checkbox"> Trait landmarks</label>
      <label><input class="coverage" value="50" type="checkbox"> 50% core</label><label><input class="coverage" value="80" type="checkbox" checked> 80% region</label><label><input class="coverage" value="95" type="checkbox"> 95% envelope</label>
    </div></div>
    <div class="group"><span class="label">Families</span><div class="checks" id="familyChecks"></div><div class="legend" id="familyLegend"></div></div>
    <div class="group"><label for="roleSearch">Select shared role</label><input id="roleSearch" type="search" list="roleList" placeholder="e.g. mystic"><datalist id="roleList"></datalist><div class="buttons"><button id="selectRole" class="primary">Select role</button><button id="clearRole">Clear</button></div></div>
    <div class="group"><label for="traitSearch">Qwen trait landmark</label><input id="traitSearch" type="search" list="traitList" placeholder="e.g. abstract"><datalist id="traitList"></datalist><div class="buttons"><button id="addTrait">Add</button><button id="clearTraits">Clear traits</button></div><p class="note">Landmarks are optional directions and never enter occupancy density.</p></div>
    <div class="group"><div class="buttons"><button id="resetCamera">Reset camera</button></div></div>
  </aside>
  <main class="main">
    <div class="plot-wrap"><div id="plot" class="plot" aria-label="Interactive model persona coverage terrain"></div><div id="status" class="status" aria-live="polite"></div></div>
    <div class="detail">
      <section><h2 id="detailTitle">Select a role</h2><div id="roleDetail"><p>Click a persona node or use role search. The same label will be highlighted across models in compare mode.</p></div></section>
      <section><h2>How to read this</h2><p id="readingNote"></p><p class="note">Sparse placement is not evidence of instability, implausibility, inaccessibility, or low prevalence. Family meshes are convex sampled-role envelopes, not density regions.</p></section>
    </div>
  </main>
</div>
<section class="methods"><h2>Frozen descriptive method</h2><ul><li>Primary occupancy: full-covariance Gaussian KDE with Scott bandwidth in each model's native PC1–PC3 coordinates.</li><li>Coverage boundaries contain approximately 50%, 80%, or 95% of the sampled role points by their role-location KDE level.</li><li>Sparsity: within-model inverse-KDE percentile; nearest roles use Euclidean distance after model-local PC standardization.</li><li>Display alignment reuses frozen variance-standardized shared-role Procrustes transforms. Its axes are not universal native PC meanings.</li><li>Family A–D are broad reconciled candidates; E remains small and resolution-sensitive. Envelopes require at least 10 roles.</li></ul></section>
<script>
const TERRAIN=__DATA__;
const PLOT=document.getElementById('plot');
const familyColors=TERRAIN.metadata.family_colors;
const familyOrder=['MFamily_A','MFamily_B','MFamily_C','MFamily_D','MFamily_E','Unassigned'];
const modelOrder=['qwen','llama','gemma'];
const modelSymbols={qwen:'circle',llama:'diamond',gemma:'square'};
const modelColors={qwen:'#2369a1',llama:'#d35d4f',gemma:'#4f9152'};
const state={model:'qwen',view:'3d',mode:'occupancy',selectedRole:null,selectedTraits:[],camera:null};

function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function familyLabel(f){return f==='Unassigned'?'Unassigned':f.replace('MFamily_','Family ');}
function selectedFamilies(){return new Set([...document.querySelectorAll('.familyToggle:checked')].map(x=>x.value));}
function coverageLevels(){return [...document.querySelectorAll('.coverage:checked')].map(x=>x.value);}
function modelPoints(model){return TERRAIN.models[model].points;}
function colorSpec(points){
  if(state.mode==='density') return {color:points.map(p=>p.density_percentile),colorscale:'Viridis',cmin:0,cmax:100,showscale:true,colorbar:{title:{text:'Sample density<br>percentile'},thickness:14}};
  if(state.mode==='sparsity') return {color:points.map(p=>p.sparsity_percentile),colorscale:'Inferno',cmin:0,cmax:100,showscale:true,colorbar:{title:{text:'Sample sparsity<br>percentile'},thickness:14}};
  return {color:'#315C78'};
}
function custom(points,model){return points.map(p=>[p.role,model,p.family,p.membership,p.density_percentile,p.sparsity_percentile,p.knn_distance]);}
function pointTrace(model,scene,coordinateKind='native'){
  let points=modelPoints(model).filter(p=>selectedFamilies().has(p.family));
  const xyz=points.map(p=>p[coordinateKind]); const marker=colorSpec(points);
  return {type:'scatter3d',mode:'markers',name:TERRAIN.models[model].label,x:xyz.map(v=>v[0]),y:xyz.map(v=>v[1]),z:xyz.map(v=>v[2]),scene,
    marker:{...marker,size:state.mode==='families'?5:4,opacity:.84,line:{color:'rgba(255,255,255,.65)',width:.35},symbol:modelSymbols[model]},customdata:custom(points,model),
    hovertemplate:'<b>%{customdata[0]}</b><br>'+TERRAIN.models[model].label+'<br>'+familyLabelText()+'%{customdata[2]} · %{customdata[3]}<br>density pct %{customdata[4]:.1f}<br>sparsity pct %{customdata[5]:.1f}<extra></extra>'};
}
function familyLabelText(){return 'family ';}
function familyPointTraces(model,scene,coordinateKind='native'){
  const traces=[];
  for(const family of familyOrder){
    if(!selectedFamilies().has(family)) continue;
    const points=modelPoints(model).filter(p=>p.family===family); if(!points.length) continue;
    const xyz=points.map(p=>p[coordinateKind]);
    traces.push({type:'scatter3d',mode:'markers',name:familyLabel(family),legendgroup:family,scene,x:xyz.map(v=>v[0]),y:xyz.map(v=>v[1]),z:xyz.map(v=>v[2]),
      marker:{size:5,color:familyColors[family],opacity:.86,line:{color:'rgba(255,255,255,.7)',width:.35},symbol:modelSymbols[model]},customdata:custom(points,model),
      hovertemplate:'<b>%{customdata[0]}</b><br>'+TERRAIN.models[model].label+'<br>'+familyLabel(family)+' · %{customdata[3]}<br>density pct %{customdata[4]:.1f}<br>sparsity pct %{customdata[5]:.1f}<extra></extra>'});
  }return traces;
}
function gridXYZ(model){
  const k=TERRAIN.models[model].kde, [a,b,c]=k.axes, x=[],y=[],z=[];
  for(let i=0;i<a.length;i++)for(let j=0;j<b.length;j++)for(let l=0;l<c.length;l++){x.push(a[i]);y.push(b[j]);z.push(c[l]);}
  return {x,y,z};
}
function surfaceTraces(model,scene){
  if(!document.getElementById('showSurface').checked || state.view!=='3d') return [];
  const k=TERRAIN.models[model].kde,g=gridXYZ(model), colors={'50':'#255f8f','80':'#65a9d3','95':'#b7d9eb'}, opacity={'50':.20,'80':.13,'95':.07};
  return coverageLevels().map(level=>({type:'isosurface',name:`~${level}% sampled-role region`,scene,x:g.x,y:g.y,z:g.z,value:k.density,isomin:k.thresholds[level],isomax:k.thresholds[level]*(1+1e-6),surface:{count:1,fill:.78,pattern:'all'},caps:{x:{show:false},y:{show:false},z:{show:false}},showscale:false,opacity:opacity[level],colorscale:[[0,colors[level]],[1,colors[level]]],hoverinfo:'skip'}));
}
function hullTraces(model,scene){
  if(!document.getElementById('showHulls').checked) return [];
  const traces=[];
  for(const [family,h] of Object.entries(TERRAIN.models[model].family_hulls)){
    if(!selectedFamilies().has(family))continue; const v=h.vertices,s=h.simplices;
    traces.push({type:'mesh3d',name:`${familyLabel(family)} sample envelope`,legendgroup:family,showlegend:false,scene,x:v.map(p=>p[0]),y:v.map(p=>p[1]),z:v.map(p=>p[2]),i:s.map(t=>t[0]),j:s.map(t=>t[1]),k:s.map(t=>t[2]),color:familyColors[family],opacity:.07,hovertemplate:`${familyLabel(family)} convex sample envelope<br>not density<extra></extra>`});
  }return traces;
}
function traitTrace3d(scene){
  if(!document.getElementById('showTraits').checked||state.model!=='qwen'||!state.selectedTraits.length)return [];
  const rows=TERRAIN.traits.qwen.filter(t=>state.selectedTraits.includes(t.trait));
  return [{type:'scatter3d',mode:'markers+text',name:'Trait landmarks',scene,x:rows.map(r=>r.x),y:rows.map(r=>r.y),z:rows.map(r=>r.z),text:rows.map(r=>r.trait),textposition:'top center',marker:{size:8,symbol:'diamond',color:'#111827',line:{color:'#fff',width:1}},customdata:rows.map(r=>r.trait),hovertemplate:'Trait-direction landmark: <b>%{customdata}</b><br>Excluded from occupancy density<extra></extra>'}];
}
function selectedTrace(model,scene,kind='native'){
  if(!state.selectedRole)return[];const p=modelPoints(model).find(x=>x.role===state.selectedRole);if(!p)return[];const v=p[kind];
  return [{type:'scatter3d',mode:'markers+text',name:'Selected role',showlegend:false,scene,x:[v[0]],y:[v[1]],z:[v[2]],text:[p.role],textposition:'top center',marker:{size:10,color:'#ffcf33',line:{color:'#111827',width:2},symbol:'circle-open'},hoverinfo:'skip'}];
}
function sceneDef(title,domain){return{domain,xaxis:{title:'PC1'},yaxis:{title:'PC2'},zaxis:{title:'PC3'},aspectmode:'data',camera:state.camera||{eye:{x:1.45,y:1.45,z:1.15}},bgcolor:'#fff',annotations:[],};}
function native3d(){
  const m=state.model,traces=[];
  traces.push(...surfaceTraces(m,'scene'));
  if(document.getElementById('showHulls').checked)traces.push(...hullTraces(m,'scene'));
  if(document.getElementById('showPoints').checked)traces.push(...(state.mode==='families'?familyPointTraces(m,'scene'): [pointTrace(m,'scene')]));
  traces.push(...traitTrace3d('scene'),...selectedTrace(m,'scene'));
  return {traces,layout:{scene:sceneDef(TERRAIN.models[m].label),title:{text:`${TERRAIN.models[m].label} · native PC1–PC3`,font:{size:17}},showlegend:state.mode==='families',legend:{orientation:'h',y:1.04,x:0},margin:{l:0,r:0,t:52,b:0}}};
}
function pointTrace2d(model,xcol,ycol){
  let points=modelPoints(model).filter(p=>selectedFamilies().has(p.family));const axes={pc1:0,pc2:1,pc3:2};
  if(state.mode==='families'){
    return familyOrder.filter(f=>selectedFamilies().has(f)).flatMap(f=>{const part=points.filter(p=>p.family===f);if(!part.length)return[];return[{type:'scattergl',mode:'markers',name:familyLabel(f),x:part.map(p=>p.native[axes[xcol]]),y:part.map(p=>p.native[axes[ycol]]),marker:{size:7,color:familyColors[f],opacity:.82,line:{color:'#fff',width:.3}},customdata:custom(part,model),hovertemplate:'<b>%{customdata[0]}</b><br>'+familyLabel(f)+' · %{customdata[3]}<br>density pct %{customdata[4]:.1f}<br>sparsity pct %{customdata[5]:.1f}<extra></extra>'}];});
  }
  const marker=colorSpec(points);return[{type:'scattergl',mode:'markers',name:'Sampled roles',x:points.map(p=>p.native[axes[xcol]]),y:points.map(p=>p.native[axes[ycol]]),marker:{...marker,size:7,opacity:.8,line:{color:'#fff',width:.3}},customdata:custom(points,model),hovertemplate:'<b>%{customdata[0]}</b><br>density pct %{customdata[4]:.1f}<br>sparsity pct %{customdata[5]:.1f}<extra></extra>'}];
}
function native2d(){
  const m=state.model,pair=state.view,parts=pair.split('_'),grid=TERRAIN.models[m].grids2d[pair],traces=[];
  if(document.getElementById('showSurface').checked)traces.push({type:'contour',name:'Role-only KDE contours',x:grid.x,y:grid.y,z:grid.z,colorscale:'Blues',opacity:.76,showscale:state.mode==='density',colorbar:{title:{text:'Native-space<br>role KDE'}},contours:{coloring:'heatmap',showlabels:false},hovertemplate:'Role-only KDE %{z:.3g}<extra></extra>'});
  if(document.getElementById('showPoints').checked)traces.push(...pointTrace2d(m,parts[0],parts[1]));
  if(state.selectedRole){const p=modelPoints(m).find(x=>x.role===state.selectedRole),idx={pc1:0,pc2:1,pc3:2};traces.push({type:'scatter',mode:'markers+text',showlegend:false,x:[p.native[idx[parts[0]]]],y:[p.native[idx[parts[1]]]],text:[p.role],textposition:'top center',marker:{size:13,color:'#ffcf33',line:{color:'#111827',width:2}},hoverinfo:'skip'});}
  if(document.getElementById('showTraits').checked&&m==='qwen'&&state.selectedTraits.length){const rows=TERRAIN.traits.qwen.filter(t=>state.selectedTraits.includes(t.trait)),idx={pc1:'x',pc2:'y',pc3:'z'};traces.push({type:'scatter',mode:'markers+text',name:'Trait landmarks',x:rows.map(r=>r[idx[parts[0]]]),y:rows.map(r=>r[idx[parts[1]]]),text:rows.map(r=>r.trait),textposition:'top center',marker:{size:11,symbol:'diamond',color:'#111827',line:{color:'#fff',width:1}},hovertemplate:'Trait-direction landmark: <b>%{text}</b><extra></extra>'});}
  return{traces,layout:{title:{text:`${TERRAIN.models[m].label} · native ${parts[0].toUpperCase()} × ${parts[1].toUpperCase()}`,font:{size:17}},xaxis:{title:`Native ${parts[0].toUpperCase()}`,zeroline:true},yaxis:{title:`Native ${parts[1].toUpperCase()}`,zeroline:true,scaleanchor:false},showlegend:state.mode==='families',legend:{orientation:'h',y:1.05},margin:{l:62,r:25,t:58,b:55},plot_bgcolor:'#fff'}};
}
function compareNative(){
  const traces=[];for(let i=0;i<modelOrder.length;i++){const m=modelOrder[i],scene=i===0?'scene':`scene${i+1}`;if(document.getElementById('showPoints').checked)traces.push(...(state.mode==='families'?familyPointTraces(m,scene):[pointTrace(m,scene)]));traces.push(...selectedTrace(m,scene));}
  return{traces,layout:{title:{text:'Linked native PC1–PC3 panels · same selected role',font:{size:17}},scene:sceneDef('Qwen',{x:[0,.32],y:[0,1]}),scene2:sceneDef('LLaMA',{x:[.34,.66],y:[0,1]}),scene3:sceneDef('Gemma',{x:[.68,1],y:[0,1]}),annotations:modelOrder.map((m,i)=>({text:TERRAIN.models[m].label,x:[.16,.5,.84][i],y:1.02,xref:'paper',yref:'paper',showarrow:false,font:{size:13}})),showlegend:state.mode==='families',legend:{orientation:'h',y:1.08},margin:{l:0,r:0,t:62,b:0}}};
}
function compareAligned(){
  const traces=[];for(const m of modelOrder){if(document.getElementById('showPoints').checked){let pts=modelPoints(m).filter(p=>selectedFamilies().has(p.family)),xyz=pts.map(p=>p.aligned);traces.push({type:'scatter3d',mode:'markers',name:TERRAIN.models[m].label,x:xyz.map(v=>v[0]),y:xyz.map(v=>v[1]),z:xyz.map(v=>v[2]),marker:{size:4,color:modelColors[m],symbol:modelSymbols[m],opacity:.57},customdata:custom(pts,m),hovertemplate:'<b>%{customdata[0]}</b><br>'+TERRAIN.models[m].label+'<br>aligned display coordinates<extra></extra>'});}traces.push(...selectedTrace(m,'scene','aligned'));}
  return{traces,layout:{title:{text:'Display-aligned shared-role overlay · non-native axes',font:{size:17}},scene:{xaxis:{title:'Aligned display 1'},yaxis:{title:'Aligned display 2'},zaxis:{title:'Aligned display 3'},aspectmode:'data',camera:state.camera||{eye:{x:1.45,y:1.45,z:1.15}}},showlegend:true,legend:{orientation:'h',y:1.04},margin:{l:0,r:0,t:55,b:0}}};
}
function render(){
  const config={responsive:true,displaylogo:false,scrollZoom:true,modeBarButtonsToRemove:['toImage','sendDataToCloud']};let built;
  if(state.view==='3d')built=native3d();else if(state.view==='compare_native')built=compareNative();else if(state.view==='compare_aligned')built=compareAligned();else built=native2d();
  built.layout.paper_bgcolor='#fff';built.layout.font={family:'Inter, system-ui, sans-serif',color:'#152432'};built.layout.uirevision='terrain';
  Plotly.react(PLOT,built.traces,built.layout,config).then(()=>{PLOT.removeAllListeners('plotly_click');PLOT.on('plotly_click',e=>{const datum=e.points&&e.points[0]&&e.points[0].customdata;if(Array.isArray(datum)&&modelOrder.includes(datum[1])){state.selectedRole=datum[0];document.getElementById('roleSearch').value=state.selectedRole;updateDetail();render();}});});
  updateText();
}
function updateText(){
  const aligned=state.view==='compare_aligned';const compare=state.view==='compare_native';const two=state.view.startsWith('pc');
  document.getElementById('readingNote').textContent=aligned?TERRAIN.metadata.aligned_space_warning:compare?'Panels remain in separate native spaces; linked selection compares the same role label without overlaying raw coordinates.':two?'Filled contours show a two-dimensional role-only KDE projection. Apparent gaps can change when a third coordinate is restored.':'Translucent boundaries are KDE levels selected by the sampled-role fraction they enclose. They are not confidence or probability regions.';
  const levels=coverageLevels().join('/');document.getElementById('status').textContent=`${TERRAIN.models[state.model].label} · ${state.view.replaceAll('_',' ')} · ${state.mode} · coverage ${levels||'off'} · role inventory N=275`;
}
function updateDetail(){
  const box=document.getElementById('roleDetail'),title=document.getElementById('detailTitle');if(!state.selectedRole){title.textContent='Select a role';box.innerHTML='<p>Click a persona node or use role search. The same label will be highlighted across models in compare mode.</p>';return;}
  title.textContent=state.selectedRole;const rows=modelOrder.map(m=>{const p=modelPoints(m).find(x=>x.role===state.selectedRole);return`<tr><td>${esc(TERRAIN.models[m].label)}</td><td>${p.native.map(v=>v.toFixed(2)).join(', ')}</td><td>${p.density_percentile.toFixed(1)}</td><td>${p.sparsity_percentile.toFixed(1)}</td><td>${esc(familyLabel(p.family))} · ${esc(p.membership)}</td></tr>`;}).join('');
  const rec=TERRAIN.neighborhood_recurrence.find(x=>x.role===state.selectedRole),current=modelPoints(state.model).find(x=>x.role===state.selectedRole);
  box.innerHTML=`<div style="overflow-x:auto"><table><thead><tr><th>Model</th><th>Native PC1,2,3</th><th>Density pct</th><th>Sparsity pct</th><th>Family</th></tr></thead><tbody>${rows}</tbody></table></div><p><b>${esc(TERRAIN.models[state.model].label)} nearest roles:</b> ${current.neighbors.slice(0,5).map(esc).join(', ')}</p><p><b>Mean cross-model 10-neighbor Jaccard:</b> ${rec.mean_pairwise_neighbor_jaccard_k10.toFixed(3)}</p>`;
}
function init(){
  const fam=document.getElementById('familyChecks'),legend=document.getElementById('familyLegend');
  familyOrder.forEach(f=>{fam.insertAdjacentHTML('beforeend',`<label><input class="familyToggle" value="${f}" type="checkbox" checked> ${familyLabel(f)}</label>`);legend.insertAdjacentHTML('beforeend',`<span><span class="swatch" style="background:${familyColors[f]}"></span>${familyLabel(f)}</span>`);});
  const roles=modelPoints('qwen').map(p=>p.role).sort();document.getElementById('roleList').innerHTML=roles.map(r=>`<option value="${esc(r)}">`).join('');
  const traits=TERRAIN.traits.qwen.map(t=>t.trait).sort();document.getElementById('traitList').innerHTML=traits.map(t=>`<option value="${esc(t)}">`).join('');
  for(const id of ['model','view','mode'])document.getElementById(id).addEventListener('change',e=>{state[id]=e.target.value;render();});
  for(const sel of ['#showPoints','#showSurface','#showHulls','#showTraits','.coverage','.familyToggle'])document.querySelectorAll(sel).forEach(x=>x.addEventListener('change',render));
  document.getElementById('selectRole').onclick=()=>{const v=document.getElementById('roleSearch').value.trim();if(roles.includes(v)){state.selectedRole=v;updateDetail();render();}};
  document.getElementById('roleSearch').addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('selectRole').click();});
  document.getElementById('clearRole').onclick=()=>{state.selectedRole=null;document.getElementById('roleSearch').value='';updateDetail();render();};
  document.getElementById('addTrait').onclick=()=>{const v=document.getElementById('traitSearch').value.trim();if(traits.includes(v)&&!state.selectedTraits.includes(v)){state.selectedTraits.push(v);state.selectedTraits=state.selectedTraits.slice(-5);document.getElementById('showTraits').checked=true;render();}};
  document.getElementById('clearTraits').onclick=()=>{state.selectedTraits=[];document.getElementById('traitSearch').value='';render();};
  document.getElementById('resetCamera').onclick=()=>{state.camera=null;Plotly.relayout(PLOT,{'scene.camera':{eye:{x:1.45,y:1.45,z:1.15}}});};
  PLOT.on?.('plotly_relayout',e=>{if(e['scene.camera'])state.camera=e['scene.camera'];});
  updateDetail();render();
}
init();
</script>
</body></html>"""


def main() -> None:
    data = json.loads((OUT / "terrain_viewer_data.json").read_text(encoding="utf-8"))
    html = HTML.replace("__PLOTLY__", get_plotlyjs()).replace(
        "__DATA__", json.dumps(data, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")
    )
    target = OUT / "model_coverage_terrain_viewer.html"
    target.write_text(html, encoding="utf-8")
    print(json.dumps({"path": str(target), "bytes": target.stat().st_size, "self_contained": True}, indent=2))


if __name__ == "__main__":
    main()
