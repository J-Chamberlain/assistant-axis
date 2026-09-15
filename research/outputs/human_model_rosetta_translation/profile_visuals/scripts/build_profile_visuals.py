"""Build descriptive 12/45-trait human-Qwen profile comparison visuals."""
from pathlib import Path
import json, hashlib, html
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/"research/outputs/human_model_rosetta_translation"
OUT=BASE/"profile_visuals"; FIG=OUT/"figures"
SRC=ROOT/"research/outputs/human_model_profile_correspondence"
ANCHORS=["adventurous","altruistic","forgiving","grandiose","impulsive","manipulative","optimistic","pessimistic","traditional","innovative","introspective","judgmental"]
KS=[4,5,6,7,8,10]

def metric(h,q):
    h=np.asarray(h,float); q=np.asarray(q,float); d=q-h
    return {"pearson_r":float(np.corrcoef(h,q)[0,1]),"spearman_rho":float(pd.Series(h).corr(pd.Series(q),method="spearman")),"cosine":float(np.dot(h,q)/(np.linalg.norm(h)*np.linalg.norm(q))),"rmse":float(np.sqrt(np.mean(d*d))),"mean_absolute_residual":float(np.mean(np.abs(d))),"mean_signed_residual":float(np.mean(d))}

def savefig(fig, name):
    fig.savefig(FIG/(name+".png"),dpi=170,bbox_inches="tight"); fig.savefig(FIG/(name+".svg"),bbox_inches="tight"); plt.close(fig)

def load():
    prof=pd.read_csv(BASE/"matched_cluster_profiles.csv")
    prof=prof[prof.model.eq("Qwen")].copy()
    traits=list(pd.read_csv(SRC/"model_family_trait_profiles_45.csv")["trait"].drop_duplicates())
    # Rosetta output contains each exact matched pair once per trait.
    wide=prof.pivot_table(index=["K","model_family_id","human_profile_id","cluster_size"],columns="trait",values="human_centroid")
    qwide=prof.pivot_table(index=["K","model_family_id","human_profile_id","cluster_size"],columns="trait",values="model_centroid")
    return prof, traits, wide, qwide

def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    prof,traits,human,qwen=load(); traits=[t for t in traits if t in human.columns]; targets=[t for t in traits if t not in ANCHORS]
    pairs=[]
    for ix in human.index:
        k,fid,hid,size=ix
        h=human.loc[ix,traits].to_numpy(float); q=qwen.loc[ix,traits].to_numpy(float)
        row={"K":k,"model_family_id":fid,"human_profile_id":hid,"human_support":size}
        for level,ts in [("12",ANCHORS),("45",traits)]:
            m=metric(human.loc[ix,ts],qwen.loc[ix,ts]); row.update({f"{level}_{k2}":v for k2,v in m.items()})
        pairs.append(row)
    pairdf=pd.DataFrame(pairs).sort_values(["K","model_family_id"]); pairdf.to_csv(OUT/"cluster_pair_metrics_12_45.csv",index=False)
    pairdf[["K","model_family_id","human_profile_id","human_support"]+[f"12_{x}" for x in ["pearson_r","spearman_rho","cosine","rmse","mean_absolute_residual"]]].to_csv(OUT/"cluster_pair_metrics_12.csv",index=False)
    pairdf[["K","model_family_id","human_profile_id","human_support"]+[f"45_{x}" for x in ["pearson_r","spearman_rho","cosine","rmse","mean_absolute_residual"]]].to_csv(OUT/"cluster_pair_metrics_45.csv",index=False)
    ag=[]
    for t in traits:
        h=human[t].to_numpy(float); q=qwen[t].to_numpy(float); d=q-h
        ag.append({"trait":t,"cross_pair_pearson_r":metric(h,q)["pearson_r"],"mean_signed_residual":np.mean(d),"mean_absolute_residual":np.mean(np.abs(d)),"residual_sd":np.std(d,ddof=1),"sign_consistency":max(np.mean(d>0),np.mean(d<0)),"bridge_level":"12" if t in ANCHORS else "45_only","support_tier":"moderate_or_high" if t in ANCHORS else "redundant_broad_or_insufficient"})
    ag=pd.DataFrame(ag); ag[ag.bridge_level.eq("12")].to_csv(OUT/"trait_agreement_summary_12.csv",index=False); ag.to_csv(OUT/"trait_agreement_summary_45.csv",index=False)
    # Fixed pair order: K ascending, model family A-D. Same everywhere.
    labels=[f"K{r.K} {r.model_family_id}\n{r.human_profile_id}" for r in pairdf.itertuples()]
    def mat(level, field):
        return np.array([[field.loc[ix,t] for t in (ANCHORS if level==12 else traits)] for ix in human.index])
    # 12 overlay grid.
    fig,axs=plt.subplots(6,4,figsize=(16,22),sharex=True,sharey=True); axs=axs.ravel(); x=np.arange(12)
    for ax,(ix,row) in zip(axs,human.iterrows()):
        ax.plot(x,row[ANCHORS],"o-",lw=1.6,label="Human",color="#555555"); ax.plot(x,qwen.loc[ix,ANCHORS],"o-",lw=1.6,label="Qwen",color="#087ea4"); m=metric(row[ANCHORS],qwen.loc[ix,ANCHORS]); ax.set_title(f"K{ix[0]} {ix[1]} ↔ {ix[2]}\nr={m['pearson_r']:.2f}, ρ={m['spearman_rho']:.2f}",fontsize=8); ax.set_ylim(-2.0,2.0); ax.axhline(0,color="#bbb",lw=.5); ax.grid(alpha=.2)
    for ax in axs[-4:]: ax.set_xticks(x,ANCHORS,rotation=65,ha="right",fontsize=7)
    axs[0].legend(fontsize=8); fig.suptitle("12-trait matched human/Qwen profile overlays — fixed Rosetta pairs",y=.995); savefig(fig,"12_trait_matched_profiles")
    # Heatmap triptychs.
    for level,ts in [(12,ANCHORS),(45,traits)]:
        H=mat(level,human); Q=mat(level,qwen); D=Q-H; n=len(ts); fig,axs=plt.subplots(3,1,figsize=(max(14,n*.34),13),sharex=True)
        lim=max(1.0,float(np.nanmax(np.abs(np.r_[H,Q]))));
        for ax,data,title in zip(axs,[H,Q,D],["Human centroid","Qwen centroid","Qwen − Human residual"]):
            norm=TwoSlopeNorm(vmin=-lim,vcenter=0,vmax=lim) if title.endswith("residual") else TwoSlopeNorm(vmin=-lim,vcenter=0,vmax=lim); im=ax.imshow(data,aspect="auto",cmap="coolwarm",norm=norm); ax.set_ylabel("matched pair"); ax.set_yticks(range(len(labels)),labels,fontsize=6); ax.set_title(title); fig.colorbar(im,ax=ax,orientation="vertical",fraction=.012,pad=.01)
        axs[-1].set_xticks(range(n),ts,rotation=75,ha="right",fontsize=7); fig.suptitle(f"{level}-trait matched profile heatmap triptych (same rows/scales)"); savefig(fig,f"{level}_trait_profile_heatmap_triptych")
    # Required standalone residual heatmaps.
    for level,ts in [(12,ANCHORS),(45,traits)]:
        H=mat(level,human); Q=mat(level,qwen); D=Q-H; lim=max(1.0,float(np.nanmax(np.abs(D)))); fig,ax=plt.subplots(figsize=(max(14,len(ts)*.34),6)); im=ax.imshow(D,aspect="auto",cmap="coolwarm",norm=TwoSlopeNorm(vmin=-lim,vcenter=0,vmax=lim)); ax.set_yticks(range(len(labels)),labels,fontsize=6); ax.set_xticks(range(len(ts)),ts,rotation=75,ha="right",fontsize=7); ax.set_title(f"{level}-trait Qwen − Human residual heatmap"); fig.colorbar(im,ax=ax); savefig(fig,f"{level}_trait_difference_heatmap")
    # 45 dumbbells, one panel per fixed pair.
    (FIG/"45_trait_pairs").mkdir(exist_ok=True)
    for ix,row in human.iterrows():
        fig,ax=plt.subplots(figsize=(10,13)); y=np.arange(len(traits)); hv=row[traits].to_numpy(float); qv=qwen.loc[ix,traits].to_numpy(float); ax.hlines(y,hv,qv,color=np.where(qv>=hv,"#c4513a","#1976a3"),lw=2); ax.scatter(hv,y,color="#555",s=18,label="Human",zorder=3); ax.scatter(qv,y,color="#087ea4",s=18,label="Qwen",zorder=3); ax.set_yticks(y,traits,fontsize=7); ax.invert_yaxis(); ax.set_xlim(-2,2); ax.axvline(0,color="#aaa",lw=.6); ax.set_title(f"45-trait profile: K{ix[0]} {ix[1]} ↔ {ix[2]}"); ax.set_xlabel("Canonical normalized profile score"); ax.legend(); fig.tight_layout(); fig.savefig(FIG/"45_trait_pairs"/f"K{ix[0]}_{ix[1]}_{ix[2]}.png",dpi=150); plt.close(fig)
    # 12 vs 45 summary.
    fig,ax=plt.subplots(figsize=(7,6)); colors=plt.cm.viridis((pairdf.K-pairdf.K.min())/(pairdf.K.max()-pairdf.K.min())); ax.scatter(pairdf["45_pearson_r"],pairdf["12_pearson_r"],c=colors,s=55); lo=min(pairdf["45_pearson_r"].min(),pairdf["12_pearson_r"].min()); hi=max(pairdf["45_pearson_r"].max(),pairdf["12_pearson_r"].max()); ax.plot([lo,hi],[lo,hi],"--",color="#888"); ax.set_xlabel("45-trait Pearson r"); ax.set_ylabel("12-trait Pearson r"); ax.set_title("Descriptive similarity: 12 versus 45 traits"); savefig(fig,"12_vs_45_cluster_similarity")
    # Trait-level agreement plot.
    fig,ax=plt.subplots(figsize=(11,7)); a=ag.bridge_level.eq("12"); ax.scatter(ag.loc[~a,"cross_pair_pearson_r"],ag.loc[~a,"mean_absolute_residual"],c="#aaa",label="45-only",s=45); ax.scatter(ag.loc[a,"cross_pair_pearson_r"],ag.loc[a,"mean_absolute_residual"],c="#d07b2d",label="12-trait anchor",s=55); 
    for r in ag.itertuples(): ax.annotate(r.trait,(r.cross_pair_pearson_r,r.mean_absolute_residual),fontsize=7,xytext=(3,3),textcoords="offset points")
    ax.set_xlabel("Human/Qwen cross-matched-pair Pearson r"); ax.set_ylabel("Mean absolute residual"); ax.legend(); ax.set_title("Trait-level descriptive agreement"); savefig(fig,"trait_level_agreement_summary")
    # self-contained HTML using SVG rendering from embedded data.
    data={"traits12":ANCHORS,"traits45":traits,"pairs":[]}
    for ix,row in human.iterrows(): data["pairs"].append({"key":f"K{ix[0]}|{ix[1]}|{ix[2]}","K":int(ix[0]),"family":ix[1],"human":ix[2],"human_size":float(ix[3]),"h12":row[ANCHORS].tolist(),"q12":qwen.loc[ix,ANCHORS].tolist(),"h45":row[traits].tolist(),"q45":qwen.loc[ix,traits].tolist()})
    js=json.dumps(data,separators=(",",":"))
    page='''<!doctype html><meta charset="utf-8"><title>Human–Qwen Trait Profile Comparison</title><style>body{font:14px system-ui;margin:24px;color:#222}select,button{font:14px;padding:6px;margin-right:8px}svg{border:1px solid #ddd;max-width:100%;height:auto}.muted{color:#666}.human{stroke:#555}.qwen{stroke:#087ea4}.res{stroke:#c4513a}</style><h1>Human ↔ Qwen trait-profile comparison</h1><p class="muted">Descriptive fixed-pair viewer. Matching is frozen from the Rosetta anchor-only analysis; values are inherited canonical normalized profile scores.</p><label>Bridge <select id="level"><option value="12">12 traits</option><option value="45">45 traits</option></select></label><label>Pair <select id="pair"></select></label><label>View <select id="view"><option>Overlay</option><option>Difference</option><option>Dumbbell</option></select></label><div id="summary"></div><div id="chart"></div><script>const D=__DATA__;const level=document.querySelector('#level'),pair=document.querySelector('#pair'),view=document.querySelector('#view');D.pairs.forEach((p,i)=>pair.add(new Option(p.key,i)));function esc(s){return s.replaceAll('&','&amp;').replaceAll('<','&lt;')}function render(){let p=D.pairs[pair.value||0],ts=level.value==='12'?D.traits12:D.traits45,h=level.value==='12'?p.h12:p.h45,q=level.value==='12'?p.q12:p.q45;let R=450,W=980, pad=95, step=(W-pad-25)/ts.length, sx=i=>pad+i*step, sy=v=>35+(2-v)*80;let r=(a,b)=>{let ma=a.reduce((x,y)=>x+y,0)/a.length,mb=b.reduce((x,y)=>x+y,0)/b.length,n=a.reduce((x,y,i)=>x+(y-ma)*(b[i]-mb),0),d=Math.sqrt(a.reduce((x,y)=>x+(y-ma)**2,0)*b.reduce((x,y)=>x+(y-mb)**2,0));return n/d};let rr=r(h,q),diff=q.map((v,i)=>v-h[i]);document.querySelector('#summary').innerHTML='<p><b>'+esc(p.key)+'</b> · support '+p.human_size.toFixed(0)+' · descriptive Pearson r='+rr.toFixed(3)+' · strongest absolute differences: '+diff.map((v,i)=>[Math.abs(v),ts[i],v]).sort((a,b)=>b[0]-a[0]).slice(0,5).map(x=>esc(x[1])+' ('+x[2].toFixed(2)+')').join(', ')+'</p>';let lines='';for(let i=0;i<ts.length;i++){let x=sx(i),lab=esc(ts[i]);if(view.value==='Difference'){lines+='<line class="res" x1="'+x+'" y1="215" x2="'+x+'" y2="'+(215-diff[i]*80)+'" stroke-width="5"/><circle cx="'+x+'" cy="'+(215-diff[i]*80)+'" r="4" fill="#c4513a"/>'}else if(view.value==='Dumbbell'){lines+='<line class="res" x1="'+x+'" y1="'+sy(h[i])+'" x2="'+x+'" y2="'+sy(q[i])+'" stroke-width="3"/><circle cx="'+x+'" cy="'+sy(h[i])+'" r="4" fill="#555"/><circle cx="'+x+'" cy="'+sy(q[i])+'" r="4" fill="#087ea4"/>'}else{lines+='<circle cx="'+x+'" cy="'+sy(h[i])+'" r="3" fill="#555"/><circle cx="'+x+'" cy="'+sy(q[i])+'" r="3" fill="#087ea4"/>'}}let hp=view.value==='Overlay'?'<polyline class="human" points="'+h.map((v,i)=>sx(i)+','+sy(v)).join(' ')+'" fill="none" stroke-width="2"/>':'';let qp=view.value==='Overlay'?'<polyline class="qwen" points="'+q.map((v,i)=>sx(i)+','+sy(v)).join(' ')+'" fill="none" stroke-width="2"/>':'';document.querySelector('#chart').innerHTML='<svg viewBox="0 0 '+W+' '+R+'"><line x1="'+pad+'" y1="195" x2="'+(W-20)+'" y2="195" stroke="#aaa"/><line x1="'+pad+'" y1="35" x2="'+pad+'" y2="355" stroke="#aaa"/>'+hp+qp+lines+ts.map((t,i)=>'<text x="'+sx(i)+'" y="380" transform="rotate(65 '+sx(i)+' 380)" font-size="10">'+esc(t)+'</text>').join('')+'<text x="12" y="45">+2</text><text x="12" y="205">0</text><text x="12" y="365">−2</text></svg>'}function refill(){let old=pair.value;pair.innerHTML='';D.pairs.forEach((p,i)=>pair.add(new Option(p.key,i)));let n=D.pairs.findIndex(p=>p.key===old);pair.value=n<0?'0':n}level.onchange=()=>{refill();render()};pair.onchange=render;view.onchange=render;render();</script>'''.replace('__DATA__',js)
    (OUT/"human_model_trait_profile_comparison.html").write_text(page)
    manifest={"status":"canonical","source":"matched_cluster_profiles.csv","normalization":"frozen prior aggregate standardized profile values","matching":"Rosetta anchor-only fixed pairs; no visual rematching","traits12":ANCHORS,"traits45":traits,"pair_order":"K ascending then MFamily_A-D","files":sorted(str(f.relative_to(OUT)) for f in OUT.rglob('*') if f.is_file())}
    (OUT/"source_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
if __name__=='__main__': main()
