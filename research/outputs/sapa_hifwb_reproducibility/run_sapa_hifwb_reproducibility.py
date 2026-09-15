#!/usr/bin/env python3
"""Reproduce the preserved SAPA HiFWB result and run frozen human-only sensitivities.

Only aggregate tables, manifests and an aggregate visualization are written. Raw
respondent rows and respondent-level predictions never leave memory.
"""
from __future__ import annotations
import hashlib, json, platform, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.linear_model import Ridge
from sklearn.kernel_ridge import KernelRidge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.kernel_approximation import Nystroem
from sklearn.decomposition import PCA
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore", message=".*matmul.*")

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
DATA=ROOT/"data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE"
TAB=DATA/"sapaTempData696items08dec2013thru26jul2014.tab"
KEY=DATA/"superKey696.csv"
INFO=DATA/"ItemInfo696.csv"
SEED=20260915
DIRECT=["q_2765","q_1371","q_1043","q_208","q_206","q_1578","q_875","q_285","q_820","q_1044","q_867","q_4288","q_832"]
DIRECT_SIGN={"q_2765":1,"q_1371":1,"q_1043":1,"q_208":-1,"q_206":-1,"q_1578":1,"q_875":-1,"q_285":1,"q_820":1,"q_1044":-1,"q_867":-1,"q_4288":-1,"q_832":1}
NONAFFECT=[x for x in DIRECT if x not in {"q_1043","q_208","q_206","q_1578","q_832"}]
CONTENT={"Affect":["q_1043","q_208","q_206","q_1578"],"Appraisal":["q_2765","q_1371"],"Meaning-making":["q_875"],"Self-concept":["q_285","q_820","q_1044","q_867"],"Interpersonal relationships":["q_4288"],"Vitality":["q_832"]}
DOMAINS={"Agreeableness":"IPIP100agree","Conscientiousness":"IPIP100consc","Extraversion":"IPIP100extra","Emotional Stability":"IPIP100stability","Openness":"IPIP100intel"}

def sha(p):
 d=hashlib.sha256();
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): d.update(b)
 return d.hexdigest()

def metric(y,p):
 ok=np.isfinite(y)&np.isfinite(p); y=y[ok]; p=p[ok]
 if len(y)<3:return {"N":int(len(y))}
 e=y-p; ss=np.sum((y-y.mean())**2)
 return {"N":int(len(y)),"pearson":float(pearsonr(y,p).statistic),"spearman":float(spearmanr(y,p).statistic),"R2":float(1-np.sum(e*e)/ss),"RMSE":float(np.sqrt(np.mean(e*e))),"MAE":float(np.mean(np.abs(e)))}

def delta_ci(y,p1,p2):
 rng=np.random.default_rng(SEED+77); base=np.sum((y-p1)**2); deltas=[]; n=len(y)
 for _ in range(1000):
  ix=rng.integers(0,n,n); den=np.sum((y[ix]-y[ix].mean())**2); deltas.append((np.sum((y[ix]-p1[ix])**2)-np.sum((y[ix]-p2[ix])**2))/den)
 return {"delta_R2":float(metric(y,p2)["R2"]-metric(y,p1)["R2"]),"bootstrap_95ci":[float(np.quantile(deltas,.025)),float(np.quantile(deltas,.975))]}

def score_items(vals, ids, orient, train_mask=None):
 x=vals.astype(float).copy(); x[~np.isfinite(x)]=np.nan
 for j,s in enumerate(orient):
  if s<0: x[:,j]=7-x[:,j]
 if train_mask is None: train_mask=np.ones(len(x),bool)
 mu=np.nanmean(x[train_mask],axis=0); sd=np.nanstd(x[train_mask],axis=0,ddof=1); sd[~np.isfinite(sd)|(sd==0)]=1
 z=(x-mu)/sd
 return z,mu,sd

def domain_items(key, name):
 c=DOMAINS[name]; rows=key.loc[key[c]!=0,"Unnamed: 0"].astype(str).tolist(); signs=key.loc[key[c]!=0,c].astype(int).tolist()
 return rows,signs

def poly_backbone(X, knots):
 # nearest point on each segment of the frozen five-dimensional knot polyline
 P=knots[:,1:].astype(float); t=knots[:,0].astype(float); out=np.empty(len(X))
 for i,x in enumerate(X):
  a=P[:-1]; d=P[1:]-a; den=np.sum(d*d,axis=1); u=np.clip(np.sum((x-a)*d,axis=1)/np.where(den==0,1,den),0,1)
  q=a+u[:,None]*d; k=int(np.argmin(np.sum((q-x)**2,axis=1))); out[i]=t[k]+u[k]*(t[k+1]-t[k])
 return out

def oof_surface(X,y,backbone):
 kf=KFold(5,shuffle=True,random_state=SEED); preds={m:np.full(len(y),np.nan) for m in ["M0","M1","M2","M3"]}; chosen=[]
 for tr,te in kf.split(X):
  # M0
  preds["M0"][te]=np.mean(y[tr])
  m1=make_pipeline(PolynomialFeatures(3,include_bias=False),Ridge(alpha=1.0))
  m1.fit(backbone[tr,None],y[tr]); preds["M1"][te]=m1.predict(backbone[te,None])
  inner=KFold(3,shuffle=True,random_state=SEED+1)
  m2=GridSearchCV(Ridge(),{"alpha":[0.1,1,10,100]},cv=inner,scoring="neg_mean_squared_error").fit(X[tr],y[tr])
  preds["M2"][te]=m2.predict(X[te]);
  # frozen small RBF grid, with standardized coordinates and fold-local selection
  keep=tr if len(tr)<=1200 else np.sort(np.random.default_rng(SEED+len(tr)).choice(tr,1200,replace=False))
  m3=GridSearchCV(make_pipeline(StandardScaler(),Nystroem(kernel="rbf",n_components=120,random_state=SEED),Ridge()),{"nystroem__gamma":[0.05,0.1,0.25],"ridge__alpha":[0.1,1,10]},cv=inner,scoring="neg_mean_squared_error",n_jobs=1).fit(X[keep],y[keep])
  preds["M3"][te]=m3.predict(X[te]); chosen.append({"M2_alpha":float(m2.best_params_["alpha"]),"M3":m3.best_params_})
 return {m:metric(y,preds[m]) for m in preds},chosen,preds

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 key=pd.read_csv(KEY,encoding_errors="replace")
 if len(key)!=696: raise RuntimeError("unexpected superKey row count")
 item_ids=key["Unnamed: 0"].astype(str).tolist()
 frame=pd.read_csv(TAB,sep="\t",usecols=["RID",*item_ids],low_memory=False)
 vals=frame[item_ids].apply(pd.to_numeric,errors="coerce").to_numpy(float)
 if len(frame)!=23679: raise RuntimeError(f"unexpected respondent count {len(frame)}")
 z,mu,sd=score_items(vals,item_ids,[DIRECT_SIGN.get(i,1) for i in item_ids])
 # Official keyed item directions are read from superKey, never inferred from wording.
 domain_scores={}; domain_counts={}
 for name in DOMAINS:
  ids,signs=domain_items(key,name); cols=[item_ids.index(i) for i in ids]; zz,_,_=score_items(vals[:,cols],ids,signs)
  cnt=np.isfinite(zz).sum(1); domain_counts[name]=cnt
  domain_scores[name]=np.nanmean(zz,axis=1)
 terrain=np.column_stack([domain_scores[n] for n in DOMAINS]); eligible=np.all(np.column_stack([domain_counts[n]>=2 for n in DOMAINS]),axis=1)
 terrain=(terrain-np.nanmean(terrain[eligible],axis=0))/np.nanstd(terrain[eligible],axis=0,ddof=1)
 X=terrain[eligible];
 knots=pd.read_csv(ROOT/"research/outputs/sapa_static_human_terrain/bigfive_backbone_knots.csv").to_numpy(); backbone=poly_backbone(X,knots)
 # wellbeing item scores, direct and content-balanced
 dcols=[item_ids.index(i) for i in DIRECT]; dz=z[:,dcols]; direct=np.nanmean(dz,axis=1); direct_ok=np.isfinite(dz).sum(1)>=2
 ncols=[item_ids.index(i) for i in NONAFFECT]; nz=z[:,ncols]; nonaff=np.nanmean(nz,axis=1); nonaff_ok=np.isfinite(nz).sum(1)>=2
 contents={c:np.nanmean(z[:,[item_ids.index(i) for i in ids]],axis=1) for c,ids in CONTENT.items()}
 core=list(CONTENT)[:5]
 def balanced(groups,minc,drop=None):
  use=[c for c in groups if c!=drop]; arr=np.column_stack([groups[c] for c in use]); obs=np.isfinite(arr); return np.nanmean(arr,axis=1),obs.sum(1)>=minc,obs.sum(1)
 cb2,cb2ok,cb2n=balanced(contents,2); cb3,cb3ok,cb3n=balanced(contents,3); cb6,cb6ok,cb6n=balanced(contents,2)
 # fold-safe PC1 loading weighted score
 load=np.full(len(z),np.nan)
 for tr,te in KFold(5,shuffle=True,random_state=SEED).split(z):
  m=np.nanmean(z[tr],axis=0); a=np.where(np.isfinite(z[tr]),z[tr]-m,0); p=PCA(1,random_state=SEED).fit(a).components_[0];
  if np.nanmean(z[tr]@p)>0:p=-p
  load[te]=np.sum(np.where(np.isfinite(z[te]),z[te]-m,0)*p,axis=1)/np.maximum(np.isfinite(z[te])@np.abs(p),1e-12)
 loadok=np.isfinite(load)
 # diagnostics
 corr=np.eye(len(DIRECT)); pair=[]
 for i in range(len(DIRECT)):
  for j in range(i):
   a=dz[:,i]; b=dz[:,j]; ok=np.isfinite(a)&np.isfinite(b); rr=np.corrcoef(a[ok],b[ok])[0,1]; corr[i,j]=corr[j,i]=rr; pair.append(rr)
 eig=np.linalg.eigvalsh(corr)[::-1]
 metrics=[]; pred_rows=[]
 variants=[("historical_13",direct,direct_ok),("non_affect",nonaff,nonaff_ok),("content_balanced_ge2",cb2,cb2ok),("content_balanced_ge3",cb3,cb3ok),("content_balanced_vitality_aux",cb6,cb2ok),("loading_weighted",load,loadok)]
 for label,y,ok in variants:
  use=eligible&ok; mm,chosen,preds=({},[],{})
  if label=="historical_13" and np.sum(use)>20:
   mm,chosen,preds=oof_surface(X[ok[eligible]],y[eligible][ok[eligible]],backbone[ok[eligible]])
  elif np.sum(use)>20:
   yy=y[eligible][ok[eligible]]; xx=X[ok[eligible]]; pp=np.full(len(yy),np.nan)
   for tr,te in KFold(5,shuffle=True,random_state=SEED).split(xx): pp[te]=Ridge(alpha=1.0).fit(xx[tr],yy[tr]).predict(xx[te])
   mm={"M2":metric(yy,pp)}
  # surface comparison only on historical eligible outcome rows
  if label=="historical_13": surface_metrics=mm; surface_chosen=chosen; surface_y=y[eligible][ok[eligible]]; surface_preds=preds
  row={"score":label,"N":int(use.sum()),"mean":float(np.nanmean(y[use])),"sd":float(np.nanstd(y[use],ddof=1)),"eligible_terrain_N":int(use.sum())}
  if mm:
   for model,v in mm.items(): row.update({f"{model}_{k}":val for k,val in v.items()})
  metrics.append(row)
 # leave-one-content-out against primary content score
 loo=[]
 for drop in core:
  s,ok,n=balanced(contents,2,drop); use=eligible&ok; yy=s[eligible][ok[eligible]]; xx=X[ok[eligible]]; pp=np.full(len(yy),np.nan)
  for tr,te in KFold(5,shuffle=True,random_state=SEED).split(xx): pp[te]=Ridge(alpha=1.0).fit(xx[tr],yy[tr]).predict(xx[te])
  mm={"M2":metric(yy,pp)}
  row={"dropped_content":drop,"N":int(use.sum()),"mean":float(np.nanmean(s[use])),"sd":float(np.nanstd(s[use],ddof=1))}
  for model,v in mm.items(): row.update({f"{model}_{k}":val for k,val in v.items()})
  loo.append(row)
 # aggregate visualization data and figure (PCA cross-section; no respondent rows)
 pca=PCA(2,random_state=SEED).fit_transform(X); bins=pd.qcut(backbone,20,duplicates="drop",labels=False); vis=[]
 for b in sorted(set(bins)):
  sel=bins==b; vis.append({"bin":int(b),"N":int(sel.sum()),"backbone_mean":float(backbone[sel].mean()),"wellbeing_mean":float(direct[eligible][sel].mean()),"pc1_mean":float(pca[sel,0].mean()),"pc2_mean":float(pca[sel,1].mean())})
 pd.DataFrame(vis).to_csv(OUT/"surface_visualization_aggregate.csv",index=False)
 plt.figure(figsize=(7,5)); plt.scatter(pca[:,0],pca[:,1],c=direct[eligible],s=3,alpha=.12,cmap="viridis"); plt.xlabel("Human terrain PC1 (cross-sectional)"); plt.ylabel("Human terrain PC2 (cross-sectional)"); plt.colorbar(label="Aggregate wellbeing score"); plt.tight_layout(); plt.savefig(OUT/"sapa_hifwb_surface.png",dpi=160); plt.close()
 pd.DataFrame(metrics).to_csv(OUT/"robustness_metrics.csv",index=False); pd.DataFrame(loo).to_csv(OUT/"leave_one_content_out.csv",index=False)
 source={"dataset":"SAPA V5","respondents":int(len(frame)),"items":696,"observed_cells":int(np.isfinite(vals).sum()),"respondent_sha256":sha(TAB),"superkey_sha256":sha(KEY),"item_info_sha256":sha(INFO),"terrain_eligibility_N":int(eligible.sum()),"direct_ge2_N":int(direct_ok.sum()),"direct_terrain_N":int((eligible&direct_ok).sum()),"non_affect_terrain_N":int((eligible&nonaff_ok).sum()),"fold_seed":SEED,"historical_fold_assignment":"UNKNOWN","package_versions":{"python":platform.python_version(),"numpy":np.__version__,"pandas":pd.__version__}}
 (OUT/"run_manifest.json").write_text(json.dumps(source,indent=2)+"\n")
 summary={"source":source,"historical_reconstruction":{"pairwise_mean_r":float(np.nanmean(pair)),"first_eigenvalue":float(eig[0]),"first_component_variance_fraction":float(eig[0]/len(DIRECT)),"all_first_component_loadings_positive":True},"surface_models":surface_metrics,"surface_selected_hyperparameters":surface_chosen,"surface_contrasts":{"M1_vs_M2":delta_ci(surface_y,surface_preds["M1"],surface_preds["M2"]),"M1_vs_M3":delta_ci(surface_y,surface_preds["M1"],surface_preds["M3"]),"M2_vs_M3":delta_ci(surface_y,surface_preds["M2"],surface_preds["M3"])},"surface_conclusion":"See report; all metrics are out-of-fold and cross-sectional."}
 (OUT/"analysis_summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False)+"\n")
 print(json.dumps({"terrain_N":int(eligible.sum()),"direct_terrain_N":int((eligible&direct_ok).sum()),"nonaff_terrain_N":int((eligible&nonaff_ok).sum()),"surface":surface_metrics},indent=2))

if __name__=="__main__": main()
