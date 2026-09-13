#!/usr/bin/env python3
"""Build static inspection figures and the derivative self-contained terrain viewer."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[2]
TERRAIN_DIR = ROOT / "research/outputs/model_coverage_terrain_viewer"
BASE_HTML = TERRAIN_DIR / "model_coverage_terrain_viewer.html"
TERRAIN_JSON = TERRAIN_DIR / "terrain_viewer_data.json"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

MODELS = ["qwen", "llama", "gemma"]
MODEL_LABEL = {"qwen": "Qwen 3 32B", "llama": "LLaMA 3.3 70B", "gemma": "Gemma 2 27B"}
COLORS = {"qwen": "#2563a6", "llama": "#d45b4c", "gemma": "#4f9252"}


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def display_transform(model: str, values: np.ndarray, alignment: dict) -> np.ndarray:
    fits = alignment["fits"]
    qfit = fits["llama_to_qwen__pc1_pc3__variance_standardized"]
    if model == "qwen":
        return (values - np.asarray(qfit["target_mean"])) / np.asarray(qfit["target_scale"])
    fit = fits[f"{model}_to_qwen__pc1_pc3__variance_standardized"]
    return ((values - np.asarray(fit["source_mean"])) / np.asarray(fit["source_scale"]) / np.asarray(fit["source_scale"])) @ np.asarray(fit["rotation"])


def make_ellipsoid(row: pd.Series, center: np.ndarray) -> dict:
    vals = np.array([row[f"eigenvalue_{i}"] for i in range(1, 4)]).clip(0)
    vecs = np.array([[row[f"eigenvector_{a}_{j}"] for a in range(1, 4)] for j in range(1, 4)])
    u = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    v = np.linspace(0, np.pi, 9)
    sphere = np.array([[np.cos(a) * np.sin(b), np.sin(a) * np.sin(b), np.cos(b)] for b in v for a in u])
    points = center + sphere @ (vecs @ np.diag(2 * np.sqrt(vals))).T
    return {"x": points[:, 0].round(8).tolist(), "y": points[:, 1].round(8).tolist(), "z": points[:, 2].round(8).tolist(), "nu": len(u), "nv": len(v)}


def build_viewer_data() -> dict:
    terrain = json.loads(TERRAIN_JSON.read_text())
    projection = pd.concat([pd.read_csv(OUT / "human_projection_12.csv"), pd.read_csv(OUT / "human_projection_45.csv")])
    ridge_knn = pd.read_csv(OUT / "human_projection_ridge_vs_knn.csv")
    support = pd.read_csv(OUT / "human_projection_support_diagnostics.csv")
    coverage = pd.read_csv(OUT / "human_projection_coverage_relation.csv")
    family = pd.read_csv(OUT / "human_projection_family_relation.csv")
    nearest = pd.read_csv(OUT / "human_projection_nearest_roles.csv")
    boot = pd.read_csv(OUT / "human_projection_bootstrap_summary.csv")
    sens = pd.read_csv(OUT / "human_projection_12_vs_45.csv")
    alignment = json.loads(
        subprocess.run(
            ["git", "show", "HEAD:research/outputs/human_supported_trait_convergence/procrustes_alignment_matrices.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
    )
    keys = ["model", "trait_set", "K", "profile_id"]
    data = projection.merge(ridge_knn[keys + ["knn_pc1", "knn_pc2", "knn_pc3"]], on=keys, validate="one_to_one").reset_index(drop=True)
    data = data.merge(support[keys + ["maximum_role_shape_similarity", "shape_support_percentile", "ridge_knn_pc_standardized_displacement", "ridge_knn_disagreement_warning", "nearest_role_native_pc_distance"]], on=keys, validate="one_to_one")
    data = data.merge(coverage[keys + ["ridge_kde_density", "terrain_sparsity_percentile", "inside_50_sample_coverage", "inside_80_sample_coverage", "inside_95_sample_coverage"]], on=keys, validate="one_to_one")
    nearest_family = family[family.nearest_family][keys + ["family_id"]].rename(columns={"family_id": "nearest_family"})
    data = data.merge(nearest_family, on=keys, validate="one_to_one")
    nearest_role = nearest[(nearest.neighbor_type == "native_pc_nearest") & (nearest.neighbor_rank <= 5)]
    role_lists = nearest_role.groupby(keys).role.apply(list).rename("nearest_roles").reset_index()
    data = data.merge(role_lists, on=keys, validate="one_to_one")
    data = data.merge(boot[keys + [c for c in boot.columns if c.startswith("eigen") or c.startswith("sd_") or c.startswith("fraction_inside")]], on=keys, validate="one_to_one")
    disp = sens[["model", "K", "profile_id", "pc_standardized_displacement"]].rename(columns={"pc_standardized_displacement": "displacement_12_45"})
    data = data.merge(disp, on=["model", "K", "profile_id"], validate="many_to_one")

    # Add display-aligned kNN locations and role-only KDE diagnostics for kNN locations.
    for model in MODELS:
        idx = data.model.eq(model)
        knn_xyz = data.loc[idx, ["knn_pc1", "knn_pc2", "knn_pc3"]].to_numpy(float)
        aligned = display_transform(model, knn_xyz, alignment)
        data.loc[idx, ["knn_aligned_x", "knn_aligned_y", "knn_aligned_z"]] = aligned
        role_xyz = np.array([p["native"] for p in terrain["models"][model]["points"]])
        role_density = np.array([p["density"] for p in terrain["models"][model]["points"]])
        kde = gaussian_kde(role_xyz.T, bw_method="scott")
        den = kde(knn_xyz.T)
        data.loc[idx, "knn_kde_density"] = den
        data.loc[idx, "knn_sparsity_percentile"] = [100 * np.mean(role_density >= x) for x in den]
        for level in (50, 80, 95):
            threshold = float(terrain["models"][model]["kde"]["thresholds"][str(level)])
            data.loc[idx, f"knn_inside_{level}"] = den >= threshold

    ellipsoids = {}
    boot_index = boot.set_index(keys)
    for row in data.itertuples(index=False):
        key = (row.model, int(row.trait_set), int(row.K), row.profile_id)
        b = boot_index.loc[key]
        ellipsoids["|".join(map(str, key))] = make_ellipsoid(b, np.array([row.ridge_pc1, row.ridge_pc2, row.ridge_pc3]))

    payload = {
        "metadata": {
            "title": "Aggregate human profiles in model persona terrain",
            "method_freeze": "58529805ce25f0c1e6ab2716fad4eaa8bc4b80e0",
            "model_validation_freeze": "1fbf9500cca092f5949a06f497f5d502f1ebc5c3",
            "human_projection_freeze": "9b84bf339d52b710117aed07799d9b308d097141",
            "model_terrain_dependency": "103c13ea692ed7e1c9cb8309bfc8b150171e7b40",
            "warning": "All eligible primary Ridge projections are outside the model-role 95% sampled-coverage envelope and below the model-role leave-one-out shape-support distribution. Treat locations as extrapolations.",
        },
        "profiles": records(data),
        "ellipsoids": ellipsoids,
    }
    (OUT / "human_terrain_viewer_data.json").write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    return payload


HUMAN_CONTROLS = r'''
<div class="group" id="humanControls"><span class="label">Predicted aggregate human profiles</span>
  <div class="checks"><label><input id="showHumans" type="checkbox" checked> Human overlay</label><label><input id="showUncertainty" type="checkbox" checked> Projection envelope</label><label><input id="showDisplacement" type="checkbox"> 12↔45 line</label><label><input id="scaleHuman" type="checkbox"> SAPA sample-size scale</label></div>
  <label for="humanK">Human resolution K</label><select id="humanK"><option value="4">K=4</option><option value="5">K=5</option><option value="6" selected>K=6 · moderate stability</option><option value="7">K=7 · low stability</option><option value="8">K=8 · low stability</option><option value="10">K=10 · predictive/correspondence anchor, low stability</option><option value="9">K=9 · diagnostic/ineligible</option></select>
  <label for="traitSet">Shared traits</label><select id="traitSet"><option value="12" selected>12 · primary</option><option value="45">45 · sensitivity</option></select>
  <label for="projectionMode">Projection</label><select id="projectionMode"><option value="ridge" selected>Ridge · extrapolative primary</option><option value="knn">Support-constrained interpolation</option></select>
  <label for="humanProfile">Human profile</label><select id="humanProfile"><option value="all">All profiles at selected K</option></select>
</div>'''


OVERLAY_JS = r'''
<script id="human-overlay-data">const HUMAN=__HUMAN_DATA__;</script>
<script>
state.humanK='6';state.traitSet='12';state.projectionMode='ridge';state.humanProfile='all';
const humanColor='#e11d72';
function humanRows(model=state.model,trait=state.traitSet,k=state.humanK){return HUMAN.profiles.filter(p=>p.model===model&&String(p.trait_set)===String(trait)&&String(p.K)===String(k)&&(state.humanProfile==='all'||p.profile_id===state.humanProfile));}
function humanXYZ(p,mode=state.projectionMode,aligned=false){if(mode==='knn')return aligned?[p.knn_aligned_x,p.knn_aligned_y,p.knn_aligned_z]:[p.knn_pc1,p.knn_pc2,p.knn_pc3];return aligned?[p.display_aligned_x,p.display_aligned_y,p.display_aligned_z]:[p.ridge_pc1,p.ridge_pc2,p.ridge_pc3];}
function humanCustom(rows){return rows.map(p=>['human',p.profile_id,p.K,p.model,p.trait_set,p.shape_support_percentile,p.ridge_knn_pc_standardized_displacement,p.nearest_family,p.nearest_roles.join(', '),p.profile_size,p.inside_95_sample_coverage,p.knn_inside_95]);}
function humanSize(p){return document.getElementById('scaleHuman').checked?Math.max(8,7+5*Math.sqrt(p.profile_proportion)):10;}
function humanTrace3d(model,scene='scene',aligned=false){if(!document.getElementById('showHumans').checked)return[];const rows=humanRows(model);const xyz=rows.map(p=>humanXYZ(p,state.projectionMode,aligned));return[{type:'scatter3d',mode:'markers+text',name:'Predicted human profiles',scene,x:xyz.map(v=>v[0]),y:xyz.map(v=>v[1]),z:xyz.map(v=>v[2]),text:rows.map(p=>p.profile_id),textposition:'top center',marker:{size:rows.map(humanSize),symbol:'diamond',color:humanColor,opacity:.95,line:{color:'#fff',width:1.2}},customdata:humanCustom(rows),hovertemplate:'<b>%{customdata[1]}</b> · aggregate SAPA profile<br>K=%{customdata[2]} · '+state.projectionMode+' · '+state.traitSet+' traits<br>shape-support percentile %{customdata[5]:.1f}<br>Ridge↔kNN displacement %{customdata[6]:.2f}<br>nearest family %{customdata[7]}<br>nearest roles %{customdata[8]}<extra>Predicted, not observed</extra>'}];}
function humanUncertainty3d(model,scene='scene'){if(!document.getElementById('showHumans').checked||!document.getElementById('showUncertainty').checked||state.projectionMode!=='ridge')return[];const traces=[];for(const p of humanRows(model)){if(state.humanProfile==='all'&&humanRows(model).length>6)continue;const e=HUMAN.ellipsoids[[model,p.trait_set,p.K,p.profile_id].join('|')];if(!e)continue;const I=[],J=[],K=[];for(let v=0;v<e.nv-1;v++)for(let u=0;u<e.nu;u++){let a=v*e.nu+u,b=v*e.nu+(u+1)%e.nu,c=(v+1)*e.nu+u,d=(v+1)*e.nu+(u+1)%e.nu;I.push(a,b);J.push(b,d);K.push(c,c);}traces.push({type:'mesh3d',scene,name:p.profile_id+' model-fit bootstrap envelope',showlegend:false,x:e.x,y:e.y,z:e.z,i:I,j:J,k:K,color:humanColor,opacity:.09,hoverinfo:'skip'});}return traces;}
function displacement3d(model,scene='scene',aligned=false){if(!document.getElementById('showHumans').checked||!document.getElementById('showDisplacement').checked)return[];const rows=humanRows(model);const traces=[];for(const p of rows){const other=HUMAN.profiles.find(q=>q.model===model&&q.K===p.K&&q.profile_id===p.profile_id&&q.trait_set!==(Number(state.traitSet)));if(!other)continue;const a=humanXYZ(p,'ridge',aligned),b=humanXYZ(other,'ridge',aligned);traces.push({type:'scatter3d',mode:'lines',showlegend:false,scene,x:[a[0],b[0]],y:[a[1],b[1]],z:[a[2],b[2]],line:{color:'#8b5cf6',width:3,dash:'dot'},hovertemplate:p.profile_id+' 12↔45 sensitivity<extra></extra>'});}return traces;}
const _native3d=native3d;native3d=function(){const b=_native3d();b.traces.push(...displacement3d(state.model),...humanUncertainty3d(state.model),...humanTrace3d(state.model));return b;};
const _native2d=native2d;native2d=function(){const b=_native2d();if(!document.getElementById('showHumans').checked)return b;const parts=state.view.split('_'),idx={pc1:0,pc2:1,pc3:2},rows=humanRows(state.model),xyz=rows.map(p=>humanXYZ(p));b.traces.push({type:'scatter',mode:'markers+text',name:'Predicted human profiles',x:xyz.map(v=>v[idx[parts[0]]]),y:xyz.map(v=>v[idx[parts[1]]]),text:rows.map(p=>p.profile_id),textposition:'top center',marker:{size:rows.map(humanSize),symbol:'diamond',color:humanColor,line:{color:'#fff',width:1}},customdata:humanCustom(rows),hovertemplate:'<b>%{customdata[1]}</b><br>predicted aggregate human profile<extra></extra>'});return b;};
const _compareNative=compareNative;compareNative=function(){const b=_compareNative();modelOrder.forEach((m,i)=>{const scene=i===0?'scene':`scene${i+1}`;b.traces.push(...humanTrace3d(m,scene));});return b;};
const _compareAligned=compareAligned;compareAligned=function(){const b=_compareAligned();for(const m of modelOrder)b.traces.push(...humanTrace3d(m,'scene',true));return b;};
const _baseRender=render;render=function(){_baseRender();setTimeout(()=>{PLOT.removeAllListeners('plotly_click');PLOT.on('plotly_click',e=>{const d=e.points&&e.points[0]&&e.points[0].customdata;if(Array.isArray(d)&&d[0]==='human'){state.humanProfile=d[1];document.getElementById('humanProfile').value=d[1];updateHumanDetail(d[1],d[3],d[4]);render();}else if(Array.isArray(d)&&modelOrder.includes(d[1])){state.selectedRole=d[0];document.getElementById('roleSearch').value=state.selectedRole;updateDetail();render();}});},0);};
function updateProfileOptions(){const sel=document.getElementById('humanProfile'),rows=HUMAN.profiles.filter(p=>p.model==='qwen'&&String(p.trait_set)===state.traitSet&&String(p.K)===state.humanK);sel.innerHTML='<option value="all">All profiles at selected K</option>'+rows.map(p=>`<option value="${p.profile_id}">${p.profile_id} · SAPA N=${p.profile_size}</option>`).join('');if(!rows.some(p=>p.profile_id===state.humanProfile))state.humanProfile='all';sel.value=state.humanProfile;}
function updateHumanDetail(profile,model,trait){const p=HUMAN.profiles.find(x=>x.profile_id===profile&&x.model===model&&String(x.trait_set)===String(trait));if(!p)return;document.getElementById('detailTitle').textContent=profile+' · predicted aggregate profile';document.getElementById('roleDetail').innerHTML=`<p><b>${TERRAIN.models[model].label}</b> · K=${p.K} · ${trait} traits · ${state.projectionMode}</p><table><tr><th>Native predicted PC</th><td>${humanXYZ(p).map(x=>x.toFixed(3)).join(', ')}</td></tr><tr><th>Shape support percentile</th><td>${p.shape_support_percentile.toFixed(1)} (low-support warning)</td></tr><tr><th>Ridge↔kNN displacement</th><td>${p.ridge_knn_pc_standardized_displacement.toFixed(2)}</td></tr><tr><th>Inside model 95% sample region</th><td>${state.projectionMode==='ridge'?p.inside_95_sample_coverage:p.knn_inside_95}</td></tr><tr><th>Nearest family</th><td>${p.nearest_family}</td></tr><tr><th>Nearest roles</th><td>${p.nearest_roles.join(', ')}</td></tr><tr><th>SAPA profile sample</th><td>${p.profile_size} (${(100*p.profile_proportion).toFixed(1)}%)</td></tr></table><p class="note">This is a model-predicted aggregate location, not an observed or individual human coordinate.</p>`;}
document.querySelector('.controls .group:nth-child(2)').insertAdjacentHTML('afterend',`__HUMAN_CONTROLS__`);
document.getElementById('humanK').onchange=e=>{state.humanK=e.target.value;state.humanProfile='all';updateProfileOptions();render();};
document.getElementById('traitSet').onchange=e=>{state.traitSet=e.target.value;state.humanProfile='all';updateProfileOptions();render();};
document.getElementById('projectionMode').onchange=e=>{state.projectionMode=e.target.value;render();};
document.getElementById('humanProfile').onchange=e=>{state.humanProfile=e.target.value;render();};
for(const id of ['showHumans','showUncertainty','showDisplacement','scaleHuman'])document.getElementById(id).onchange=render;
document.querySelector('.warning').insertAdjacentHTML('afterend','<div class="warning" style="background:#fff0f6;border-left-color:#e11d72">Predicted aggregate human locations are extrapolations: all primary eligible points lie beyond the model-role 95% sampled-coverage envelope and have 0th-percentile model-role shape support. Use the kNN view as a support-constrained diagnostic.</div>');
document.querySelector('header h1').textContent='Aggregate human profiles in persona-space terrain';
document.querySelector('header p').textContent='Inspect model-predicted locations for frozen aggregate SAPA profiles against the unchanged 275-role model terrain. Human markers are predictions and never enter role occupancy density.';
document.querySelector('.methods ul').insertAdjacentHTML('beforeend','<li>Human features are centered and L2-normalized across 12 primary or 45 sensitivity traits; Ridge was selected using model roles only. Envelopes show model-fit bootstrap spread, not confidence regions for true human positions.</li><li>Build provenance: method 58529805 · validation 1fbf9500 · projection 9b84bf33 · terrain dependency 103c13ea.</li>');
updateProfileOptions();render();
</script>'''


def build_html(payload: dict) -> None:
    html = BASE_HTML.read_text()
    script = OVERLAY_JS.replace("__HUMAN_DATA__", json.dumps(payload, separators=(",", ":")).replace("</", "<\\/"))
    script = script.replace("__HUMAN_CONTROLS__", HUMAN_CONTROLS.replace("`", "\\`"))
    html = html.replace("</body>", script + "\n</body>")
    html = html.replace("<title>Model-only persona-space coverage terrain viewer</title>", "<title>Aggregate human profiles in model persona terrain</title>")
    html = html.replace("</style>", ".human-note{color:#e11d72;font-weight:650}</style>")
    (OUT / "human_profile_terrain_overlay.html").write_text(html)


def build_figures() -> None:
    coords = pd.read_csv(TERRAIN_DIR / "role_coordinates.csv")
    p12 = pd.read_csv(OUT / "human_projection_12.csv")
    p45 = pd.read_csv(OUT / "human_projection_45.csv")
    cov = pd.read_csv(OUT / "human_projection_coverage_relation.csv")
    sens = pd.read_csv(OUT / "human_projection_12_vs_45.csv")
    rk = pd.read_csv(OUT / "human_projection_ridge_vs_knn.csv")
    boot = pd.read_csv(OUT / "human_projection_bootstrap_summary.csv")
    source_rows = []
    for model in MODELS:
        role = coords[coords.model.eq(model)]
        for k in (6, 10):
            human = p12[(p12.model.eq(model)) & (p12.K.eq(k))]
            fig = plt.figure(figsize=(8, 6)); ax = fig.add_subplot(111, projection="3d")
            ax.scatter(role.native_pc1, role.native_pc2, role.native_pc3, s=8, alpha=.30, c="#55758c", label="275 sampled model roles")
            ax.scatter(human.ridge_pc1, human.ridge_pc2, human.ridge_pc3, s=42, marker="D", c="#e11d72", label="Predicted aggregate human profiles")
            for row in human.itertuples(): ax.text(row.ridge_pc1, row.ridge_pc2, row.ridge_pc3, row.profile_id, fontsize=7)
            ax.set(xlabel="Native PC1", ylabel="Native PC2", zlabel="Native PC3", title=f"{MODEL_LABEL[model]} · K={k} · 12-trait Ridge")
            ax.legend(loc="upper left", fontsize=8); fig.tight_layout()
            name=f"{model}_k{k}_shared12_overlay.png"; fig.savefig(FIG/name,dpi=180); plt.close(fig)
            source_rows.append({"figure":name,"model":model,"K":k,"trait_set":12,"source":"role_coordinates.csv + human_projection_12.csv"})
    fig, axes = plt.subplots(1,3,figsize=(12,4))
    for ax,model in zip(axes,MODELS):
        d=sens[(sens.model.eq(model)) & (sens.eligible_primary_k.astype(bool))]
        ax.hist(d.pc_standardized_displacement,bins=14,color=COLORS[model],alpha=.82);ax.set_title(MODEL_LABEL[model]);ax.set_xlabel("12↔45 displacement\n(native-PC SD units)");ax.set_ylabel("profiles")
    fig.tight_layout();fig.savefig(FIG/"shared12_vs_shared45_displacement.png",dpi=180);plt.close(fig)
    source_rows.append({"figure":"shared12_vs_shared45_displacement.png","model":"all","K":"eligible","trait_set":"12_vs_45","source":"human_projection_12_vs_45.csv"})
    fig, axes=plt.subplots(1,3,figsize=(12,4))
    for ax,model in zip(axes,MODELS):
        d=rk[(rk.model.eq(model))&(rk.trait_set.eq(12))&rk.eligible_primary_k.astype(bool)]
        ax.hist(d.pc_standardized_displacement,bins=14,color=COLORS[model],alpha=.82);ax.axvline(d.disagreement_p95.iloc[0],color="#111827",ls="--",label="model-role warning threshold");ax.set_title(MODEL_LABEL[model]);ax.set_xlabel("Ridge↔kNN displacement");ax.legend(fontsize=7)
    fig.tight_layout();fig.savefig(FIG/"ridge_vs_interpolation_diagnostic.png",dpi=180);plt.close(fig)
    source_rows.append({"figure":"ridge_vs_interpolation_diagnostic.png","model":"all","K":"eligible","trait_set":12,"source":"human_projection_ridge_vs_knn.csv"})
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,model in zip(axes,MODELS):
        d=cov[(cov.model.eq(model))&(cov.trait_set.eq(12))&cov.eligible_primary_k.astype(bool)]
        ax.hist(d.terrain_sparsity_percentile,bins=np.linspace(0,100,21),color=COLORS[model]);ax.set_xlim(0,100);ax.set_title(MODEL_LABEL[model]);ax.set_xlabel("Model-terrain sparsity percentile")
    fig.suptitle("Primary projected profiles lie beyond sampled-role coverage");fig.tight_layout();fig.savefig(FIG/"human_projection_terrain_sparsity.png",dpi=180);plt.close(fig)
    source_rows.append({"figure":"human_projection_terrain_sparsity.png","model":"all","K":"eligible","trait_set":12,"source":"human_projection_coverage_relation.csv"})
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,model in zip(axes,MODELS):
        d=boot[(boot.model.eq(model))&(boot.trait_set.eq(12))&boot.eligible_primary_k.astype(bool)]
        ax.hist(d.fraction_inside_95_sample_coverage,bins=np.linspace(0,1,21),color=COLORS[model]);ax.set_title(MODEL_LABEL[model]);ax.set_xlabel("Bootstrap fraction inside 95% role region")
    fig.tight_layout();fig.savefig(FIG/"bootstrap_coverage_envelope_stability.png",dpi=180);plt.close(fig)
    source_rows.append({"figure":"bootstrap_coverage_envelope_stability.png","model":"all","K":"eligible","trait_set":12,"source":"human_projection_bootstrap_summary.csv"})
    pd.DataFrame(source_rows).to_csv(OUT/"figure_source_data.csv",index=False)


def main() -> None:
    payload = build_viewer_data()
    build_html(payload)
    build_figures()
    print(json.dumps({"profiles": len(payload["profiles"]), "ellipsoids": len(payload["ellipsoids"]), "html_bytes": (OUT / "human_profile_terrain_overlay.html").stat().st_size}))


if __name__ == "__main__":
    main()
