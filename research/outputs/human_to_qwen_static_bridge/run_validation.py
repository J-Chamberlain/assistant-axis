#!/usr/bin/env python3
"""CPU-only blinded validation for Human-to-Qwen Static Bridge V1.

The SAPA path is intentionally explicit and outside Git. This runner writes
respondent-level predictions only below data_external/ and aggregate results
under the study output directory.
"""
from __future__ import annotations

import hashlib, json, math, os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm, pearsonr, spearmanr
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research/outputs/human_to_qwen_static_bridge"
PRIVATE = ROOT / "data_external/human_validation/sapa/derived/human_to_qwen_static_bridge_v1"
SAPA = Path(os.environ.get("SAPA_TAB", "/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis-aa1-qwen-human-construct-bridge/data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/sapaTempData696items08dec2013thru26jul2014.tab"))
TRAITS = ["adventurous", "altruistic", "forgiving", "grandiose", "impulsive", "manipulative", "optimistic", "pessimistic", "traditional", "innovative", "introspective", "judgmental"]
SEED = 20260914
ALPHAS = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def normal_scores(x):
    """Midrank inverse-normal scores for a complete model vector."""
    x = np.asarray(x, float); n = len(x)
    order = np.argsort(x, kind="mergesort"); ranks = np.empty(n, float); ranks[order] = np.arange(1, n + 1)
    # average tied ranks
    s = pd.Series(x); ranks = s.rank(method="average").to_numpy()
    return norm.ppf((ranks - 0.5) / n)

def apply_training_cdf(x, ref):
    x = np.asarray(x, float); ref = np.sort(np.asarray(ref, float))
    lo = np.searchsorted(ref, x, side="left"); hi = np.searchsorted(ref, x, side="right")
    ranks = (lo + hi + 1.0) / 2.0
    return norm.ppf(np.clip((ranks - 0.5) / len(ref), 1e-8, 1 - 1e-8))

def choose_model_ridge(X, Y):
    cv = KFold(5, shuffle=True, random_state=SEED)
    best, best_loss = None, np.inf
    for alpha in ALPHAS:
        losses=[]
        for tr, va in cv.split(X):
            pipe=make_pipeline(StandardScaler(), Ridge(alpha=alpha))
            pipe.fit(X[tr],Y[tr]); losses.append(np.mean((pipe.predict(X[va])-Y[va])**2))
        loss=float(np.mean(losses))
        if loss < best_loss: best_loss, best = loss, alpha
    pipe=make_pipeline(StandardScaler(), Ridge(alpha=best)); pipe.fit(X,Y)
    return pipe, float(best), float(best_loss)

def model_subset_cache(model, pcs):
    z={t:normal_scores(model[t].to_numpy()) for t in TRAITS}
    y=pcs[["activation_pc1","activation_pc2","activation_pc3"]].to_numpy(float)
    cache={}
    def get(anchors):
        key=tuple(anchors)
        if key not in cache:
            X=np.column_stack([z[t] for t in key]); pipe,a,loss=choose_model_ridge(X,y)
            pred=[]
            for tr,va in KFold(5,shuffle=True,random_state=SEED).split(X):
                q=make_pipeline(StandardScaler(),Ridge(alpha=a)); q.fit(X[tr],y[tr]); pred.append((va,q.predict(X[va])))
            oof=np.empty_like(y)
            for va,p in pred:oof[va]=p
            ss=np.sum((y-y.mean(0))**2,0); r2=1-np.sum((y-oof)**2,0)/ss
            rmse=float(np.sqrt(np.mean((y-oof)**2))/np.sqrt(np.mean((y-y.mean(0))**2)))
            cache[key]=(pipe, {"anchors":"|".join(key),"anchor_count":len(key),"alpha":a,"cv_loss":loss,"pc1_r2":float(r2[0]),"pc2_r2":float(r2[1]),"pc3_r2":float(r2[2]),"normalized_3d_rmse":rmse,"mean_euclidean_error":float(np.mean(np.linalg.norm(y-oof,axis=1)))})
        return cache[key]
    return z, get, cache

def main():
    OUT.mkdir(parents=True, exist_ok=True); PRIVATE.mkdir(parents=True, exist_ok=True)
    items=pd.read_csv(OUT/"human_trait_scoring_manifest.csv")
    raw_cols=sorted(set(items.item_id))
    human=pd.read_csv(SAPA,sep="\t",usecols=["RID"]+raw_cols)
    scores={}
    for t in TRAITS:
        sub=items[items.trait==t]
        vals=human[sub.item_id.tolist()].to_numpy(float)
        vals=np.where(vals==vals, np.where(sub.orientation_sign.to_numpy()[None,:]==1, vals, 7-vals), np.nan)
        scores[t]=np.nanmean(vals,axis=1)
    H=pd.DataFrame(scores); observed=H.notna(); counts=observed.sum(axis=1)
    eligible=counts>=7
    model=pd.read_csv(ROOT/"research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv")
    pcs=pd.read_csv(ROOT/"research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv")
    model=model.set_index("persona").loc[pcs.persona].reset_index()
    z, get_subset, subset_cache=model_subset_cache(model,pcs)
    decoder={}
    decoder_rows=[]
    for t in TRAITS:
        p,a,loss=choose_model_ridge(pcs[["activation_pc1","activation_pc2","activation_pc3"]].to_numpy(float),z[t])
        decoder[t]=p; decoder_rows.append({"target_trait":t,"alpha":a,"cv_loss":loss,"n_personas":len(model)})
    # Freeze respondent folds before constructing any prediction.
    idx=np.where(eligible)[0]; fold=np.full(len(human),-1,int)
    for k,(_,va) in enumerate(KFold(5,shuffle=True,random_state=SEED).split(idx)): fold[idx[va]]=k
    rows=[]
    for i in idx:
        obs=[t for t in TRAITS if pd.notna(H.loc[i,t])]
        for target in obs:
            anchors=[t for t in obs if t!=target]
            if len(anchors)<6: continue
            tr_idx=np.where((fold==fold[i])==False)[0]
            ref={t:H.loc[tr_idx,t].dropna().to_numpy(float) for t in TRAITS}
            if len(ref[target])<100 or any(len(ref[t])<100 for t in anchors): continue
            X=np.array([[apply_training_cdf([H.loc[i,t]],ref[t])[0] for t in anchors]])
            pipe,meta=get_subset(anchors); pred_pc=pipe.predict(X)[0]
            pred=float(decoder[target].predict(pred_pc.reshape(1,-1))[0])
            actual=float(apply_training_cdf([H.loc[i,target]],ref[target])[0])
            rows.append({"anonymous_row":int(i),"outer_fold":int(fold[i]),"target_trait":target,"anchors":"|".join(anchors),"anchor_count":len(anchors),"predicted_target_normal":pred,"actual_target_normal":actual,"model_normalized_3d_rmse":meta["normalized_3d_rmse"],"model_mean_euclidean_error":meta["mean_euclidean_error"]})
    pred=pd.DataFrame(rows)
    try: pred.to_parquet(PRIVATE/"heldout_predictions.parquet",index=False)
    except Exception: pred.to_csv(PRIVATE/"heldout_predictions.csv",index=False)
    metrics=[]
    for t,g in pred.groupby("target_trait"):
        r=pearsonr(g.predicted_target_normal,g.actual_target_normal).statistic
        rho=spearmanr(g.predicted_target_normal,g.actual_target_normal).statistic
        slope=np.polyfit(g.predicted_target_normal,g.actual_target_normal,1)[0] if len(g)>1 else np.nan
        metrics.append({"trait":t,"n":len(g),"respondents":g.anonymous_row.nunique(),"pearson_r":r,"spearman_rho":rho,"rmse":float(np.sqrt(np.mean((g.predicted_target_normal-g.actual_target_normal)**2))),"calibration_slope":slope})
    mdf=pd.DataFrame(metrics).sort_values("trait"); mdf.to_csv(OUT/"heldout_trait_metrics.csv",index=False)
    valid=pred[pred.target_trait.isin(mdf.loc[mdf.n>=100,"trait"])]
    rs=mdf.loc[mdf.n>=100,"pearson_r"].to_numpy(); macro=float(np.tanh(np.mean(np.arctanh(np.clip(rs,-.999999,.999999))))) if len(rs) else np.nan
    summary={"freeze_commit":"77318ff22f0e4a30a0186d7fa32241d770a1ae66","primary_anchor_threshold":6,"eligible_respondents":int(pred.anonymous_row.nunique()),"respondent_target_predictions":int(len(pred)),"per_trait_n_min":int(mdf.n.min()),"per_trait_n_max":int(mdf.n.max()),"macro_fisher_pearson":macro,"pooled_pearson":float(pearsonr(valid.predicted_target_normal,valid.actual_target_normal).statistic),"pooled_spearman":float(spearmanr(valid.predicted_target_normal,valid.actual_target_normal).statistic),"raw_sapa_sha256":sha256(SAPA),"raw_sapa_bytes":SAPA.stat().st_size,"status":"PENDING_NULLS_AND_BOOTSTRAP"}
    (OUT/"primary_validation_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    pd.DataFrame([get_subset(tuple(sorted(set(a.split('|'))))) [1] for a in sorted(set(pred.anchors))]).to_csv(OUT/"model_anchor_subset_cv.csv",index=False)
    pd.DataFrame(decoder_rows).to_csv(OUT/"model_trait_decoder_cv.csv",index=False)
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
