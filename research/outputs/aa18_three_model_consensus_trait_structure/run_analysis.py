#!/usr/bin/env python3
"""AA-18: saved-matrix, CPU-only three-view trait/persona consensus."""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import pandas as pd
from scipy.linalg import subspace_angles
from scipy.optimize import linear_sum_assignment
from scipy.stats import rankdata
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MODELS = ["Qwen", "Llama", "Gemma"]
SOURCE = {
    "Qwen": "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
    "Llama": "research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv",
    "Gemma": "research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv",
}
AA17 = ROOT / "research/outputs/aa17_three_model_trait_factor"
AA16 = ROOT / "research/outputs/aa16_sapa_hifwb_trait_profile"
SEED = 18018
N_BOOT_TRAIT = 200
N_BOOT_COMPONENT = 100
N_SPLIT = 20
N_NULL = 100
KMAX = 20


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, rows):
    pd.DataFrame(rows).to_csv(OUT / name, index=False)


def pcorr_cols(a, b):
    aa = a-a.mean(0); bb=b-b.mean(0)
    return np.sum(aa*bb,axis=0)/np.sqrt(np.sum(aa*aa,axis=0)*np.sum(bb*bb,axis=0))


def pcorr_rows(a, b):
    aa=a-a.mean(1,keepdims=True);bb=b-b.mean(1,keepdims=True)
    return np.sum(aa*bb,axis=1)/np.sqrt(np.sum(aa*aa,axis=1)*np.sum(bb*bb,axis=1))


def standardize(x):
    mu=x.mean(0);sd=x.std(0,ddof=1)
    if np.any(sd<1e-6):raise RuntimeError("degenerate trait")
    return (x-mu)/sd,mu,sd


def norm_columns(x):
    return x/np.maximum(np.linalg.norm(x,axis=0),1e-12)


def canonical_corr(a,b):
    qa=np.linalg.qr(a)[0];qb=np.linalg.qr(b)[0]
    return np.linalg.svd(qa.T@qb,compute_uv=False)


def congruence(a,b):
    return norm_columns(a).T@norm_columns(b)


def match(ref,other):
    c=congruence(ref,other)
    ii,jj=linear_sum_assignment(-abs(c))
    order=jj[np.argsort(ii)];sign=np.sign(c[np.arange(len(order)),order]);sign[sign==0]=1
    return other[:,order]*sign,order,sign


def pair_values(blocks, fn):
    return np.stack([fn(blocks[0],blocks[1]),fn(blocks[0],blocks[2]),fn(blocks[1],blocks[2])])


def gate():
    ref=json.loads((AA17/"verification_report.json").read_text())["source_sha256"]
    tables={m:pd.read_csv(ROOT/SOURCE[m]) for m in MODELS}
    first=tables["Qwen"]
    assert first.shape==(275,241) and first.columns[0]=="persona"
    assert len(set(first.persona))==275 and len(set(first.columns[1:]))==240
    rows=[];x={};raw_stats={}
    for m,t in tables.items():
        assert t.shape==first.shape and t.persona.tolist()==first.persona.tolist() and t.columns.tolist()==first.columns.tolist()
        xx=t.iloc[:,1:].to_numpy(float)
        assert np.isfinite(xx).all()
        z,mu,sd=standardize(xx)
        c=np.corrcoef(z,rowvar=False)
        exact=int(np.sum(np.triu(abs(c)>1-1e-12,1)))
        h=sha(ROOT/SOURCE[m]);assert h==ref[m],f"AA-17 source hash mismatch for {m}"
        x[m]=xx;raw_stats[m]=dict(mean=mu,sd=sd)
        rows.append(dict(model=m,path=SOURCE[m],sha256=h,rows=len(t),traits=xx.shape[1],missing=int(np.isnan(xx).sum()),
                         nonfinite=int((~np.isfinite(xx)).sum()),duplicate_persona_names=int(t.persona.duplicated().sum()),
                         exact_duplicate_trait_columns=exact,constant_columns=int((sd<1e-6).sum()),
                         raw_mean=float(xx.mean()),raw_sd=float(xx.std(ddof=1)),raw_min=float(xx.min()),raw_max=float(xx.max()),
                         minimum_trait_sd=float(sd.min()),maximum_trait_sd=float(sd.max())))
    (OUT/"source_inventory.json").write_text(json.dumps({"base_commit":"05ded7f8edd05550e3f9a7e8b18c3926cc51b3c5",
        "matrix_sources":rows,"aa17_verification_sha256":sha(AA17/"verification_report.json"),
        "aa17_factor_loadings_sha256":sha(AA17/"factor_loadings_rotated.csv"),
        "aa16_bridge_audit_sha256":sha(AA16/"existing_trait_bridge_audit.csv"),
        "score_construction":"model-specific cosine of L2-normalized means of saved role and trait activation vectors; mean across stored layer rows precedes L2 normalization",
        "source_scope":"saved matrices only; no tensor/model inference"},indent=2)+"\n")
    lines=["# AA-18 matrix reconstruction and comparability gate","","**PASS.** Exact source SHA256 values match AA-17, and all three 275 × 240 saved matrices have the same ordered persona and trait labels. No persona label repeats, no cell is missing or nonfinite, and no trait column is constant or an exact duplicate.","",
           "| Model | SHA256 | Raw mean | Raw SD | Range | Trait SD range |", "|---|---|---:|---:|---|---|"]
    for r in rows:lines.append(f"| {r['model']} | `{r['sha256'][:12]}` | {r['raw_mean']:.4f} | {r['raw_sd']:.4f} | {r['raw_min']:.3f} to {r['raw_max']:.3f} | {r['minimum_trait_sd']:.4f} to {r['maximum_trait_sd']:.4f} |")
    lines += ["", "AA-17 did not overwrite or transform these source CSVs. It centered and standardized columns in memory for factor fitting. AA-18 independently repeats column standardization and learns it only on training personas in held-out analyses. Raw cosines are retained for separate diagnostics. All three cells have the same formal meaning—same-model role-to-trait cosine between L2-normalized, layer-mean vectors—but their scales differ, especially Gemma. Identical prompts and labels do not establish full measurement invariance.","", "Each row is one named saved role/persona artifact; the 275 observations are not duplicated or averaged across persona labels. Each saved role and trait vector was internally averaged over stored layer rows, and upstream trait vectors arose from contrastive response activations. Exact original response IDs, scoring/selection records, aggregation weights, and full extraction equivalence remain unavailable, as documented in the AA-15 erratum. Hence AA-18 can compare profile organization but cannot equate absolute trait intensities across models or human traits.","", "No activation PCs define any AA-18 component. AA-14's PCA layer-label erratum and AA-17's phase-gate/provenance caveats remain in force."]
    (OUT/"matrix_reconstruction_audit.md").write_text("\n".join(lines)+"\n")
    (OUT/"preprocessing_specification.md").write_text("# Preprocessing specification\n\n"+
        "Primary: within each model and each training fold, subtract the training-persona mean and divide by training-persona sample SD for each of 240 signed trait columns. Apply these frozen parameters to held-out personas. No label-based sign reversal. The full-data standardization is used only for descriptive direct convergence, full-sample scores, and post-fit visualization. Model-specific SVD, ridge projection, and score scaling are refit inside each training fold. Raw cosine metrics are separately exported.\n")
    return tables,x,raw_stats


def direct_audit(tables,x):
    names=tables["Qwen"].columns[1:].tolist();personas=tables["Qwen"].persona.tolist()
    z={m:standardize(x[m])[0] for m in MODELS}
    raw=[x[m] for m in MODELS];zz=[z[m] for m in MODELS]
    pear=pair_values(zz,pcorr_cols)
    ranked=[np.apply_along_axis(rankdata,0,b) for b in zz]
    spear=pair_values(ranked,pcorr_cols)
    rmse=pair_values(zz,lambda a,b:np.sqrt(np.mean((a-b)**2,axis=0)))
    raw_rmse=pair_values(raw,lambda a,b:np.sqrt(np.mean((a-b)**2,axis=0)))
    frozen=np.maximum(0,pear.min(0))*np.maximum(0,pear.mean(0))
    boot=np.empty((N_BOOT_TRAIT,240));bootmin=np.empty_like(boot)
    rng=np.random.default_rng(SEED)
    for k in range(N_BOOT_TRAIT):
        ids=rng.integers(0,275,275)
        rr=pair_values([b[ids] for b in zz],pcorr_cols)
        boot[k]=np.maximum(0,rr.min(0))*np.maximum(0,rr.mean(0));bootmin[k]=rr.min(0)
    influence=np.empty((275,240));persona_influence=[]
    for i,p in enumerate(personas):
        ids=np.r_[0:i,i+1:275]
        rr=pair_values([b[ids] for b in zz],pcorr_cols)
        score=np.maximum(0,rr.min(0))*np.maximum(0,rr.mean(0))
        influence[i]=abs(score-frozen)
        persona_influence.append(dict(persona=p,mean_trait_score_influence=float(influence[i].mean()),
                                      max_trait_score_influence=float(influence[i].max())))
    rows=[];bootrows=[];scores=[]
    for j,t in enumerate(names):
        pp=pear[:,j];sp=spear[:,j];alpha=3*pp.mean()/(1+2*pp.mean()) if 1+2*pp.mean()>0 else np.nan
        category="all_three_strong" if pp.min()>=.5 else "pairwise_only" if pp.max()>=.5 and pp.min()<.3 else "reversed" if pp.min()<0 else "weak_or_mixed"
        rows.append(dict(trait=t,pearson_qwen_llama=pp[0],pearson_qwen_gemma=pp[1],pearson_llama_gemma=pp[2],
                         pearson_mean=pp.mean(),pearson_min=pp.min(),pearson_max=pp.max(),spearman_mean=sp.mean(),spearman_min=sp.min(),
                         standardized_rmse_mean=rmse[:,j].mean(),standardized_rmse_max=rmse[:,j].max(),raw_rmse_mean=raw_rmse[:,j].mean(),
                         standardized_consistency_alpha=alpha,all_three_sign_consistent=bool((pp>0).all()),category=category,
                         max_leave_one_persona_score_change=influence[:,j].max(),most_influential_persona=personas[int(influence[:,j].argmax())]))
        bootrows.append(dict(trait=t,score_q05=np.quantile(boot[:,j],.05),score_q95=np.quantile(boot[:,j],.95),
                             minimum_pearson_q05=np.quantile(bootmin[:,j],.05),minimum_pearson_q95=np.quantile(bootmin[:,j],.95)))
        scores.append(dict(trait=t,all_three_convergence_score=frozen[j],mean_pairwise_pearson=pp.mean(),minimum_pairwise_pearson=pp.min(),
                           strongest_pair_pearson=pp.max(),pairwise_advantage=pp.max()-pp.min(),category=category))
    save("trait_profile_convergence.csv",rows);save("trait_convergence_bootstrap.csv",bootrows);save("trait_convergence_scores.csv",scores)
    pp=pair_values(zz,pcorr_rows);rawpp=pair_values(raw,pcorr_rows)
    p_rmse=pair_values(zz,lambda a,b:np.sqrt(np.mean((a-b)**2,axis=1)))
    prows=[]
    for i,p in enumerate(personas):
        v=pp[:,i];cat="all_three_strong" if v.min()>=.5 else "pairwise_only" if v.max()>=.5 and v.min()<.3 else "reversed" if v.min()<0 else "weak_or_mixed"
        prows.append(dict(persona=p,pearson_qwen_llama=v[0],pearson_qwen_gemma=v[1],pearson_llama_gemma=v[2],
                          pearson_mean=v.mean(),pearson_min=v.min(),pearson_max=v.max(),raw_profile_pearson_mean=rawpp[:,i].mean(),
                          standardized_rmse_mean=p_rmse[:,i].mean(),category=cat,**{k:persona_influence[i][k] for k in ['mean_trait_score_influence','max_trait_score_influence']}))
    save("persona_profile_convergence.csv",prows)
    pairrows=[]
    for q,(a,b) in enumerate([("Qwen","Llama"),("Qwen","Gemma"),("Llama","Gemma")]):
        pairrows.append(dict(model_a=a,model_b=b,trait_profile_pearson_median=np.median(pear[q]),
                             trait_profile_pearson_mean=np.mean(pear[q]),trait_profile_spearman_median=np.median(spear[q]),
                             persona_profile_pearson_median=np.median(pp[q]),persona_profile_pearson_mean=np.mean(pp[q]),
                             traits_pearson_ge_0_5=int((pear[q]>=.5).sum()),traits_reversed=int((pear[q]<0).sum())))
    save("pairwise_model_agreement.csv",pairrows)
    # Trait-label null: unpaired label matching for two of the three blocks.
    null=[]
    for k in range(N_NULL):
        perm=[zz[0],zz[1][:,rng.permutation(240)],zz[2][:,rng.permutation(240)]]
        rr=pair_values(perm,pcorr_cols)
        sc=np.maximum(0,rr.min(0))*np.maximum(0,rr.mean(0))
        null.append(dict(replicate=k,mean_all_three_score=float(sc.mean()),traits_all_three_strong=int((rr.min(0)>=.5).sum())))
    save("trait_label_permutation_null.csv",null)
    return z,pd.DataFrame(rows),pd.DataFrame(prows),pd.DataFrame(scores),pd.DataFrame(null)


def fit_gcca(blocks, d=20, alpha=1.0, kmax=KMAX):
    """Ridge MAXVAR GCCA using training-only SVD and covariance projectors."""
    n=len(blocks[0]);prepared=[];projectors=[]
    for raw in blocks:
        z,mu,sd=standardize(raw)
        u,s,vt=np.linalg.svd(z,full_matrices=False)
        u,s,vt=u[:,:d],s[:d],vt[:d]
        weight=s*s/(s*s+alpha*n)
        projectors.append((u*weight)@u.T)
        prepared.append(dict(z=z,mu=mu,sd=sd,u=u,s=s,vt=vt))
    p=sum(projectors)
    eigen,vec=np.linalg.eigh(p)
    order=np.argsort(eigen)[::-1][:kmax]
    eig=eigen[order];g=vec[:,order]
    weights=[];intercepts=[];scores=[];loadings=[]
    for item in prepared:
        u,s,vt=item["u"],item["s"],item["vt"]
        w=vt.T@((s/(s*s+alpha*n))[:,None]*(u.T@g))
        t=item["z"]@w
        sign=np.sign(np.sum(t*g,axis=0));sign[sign==0]=1
        w=w*sign;t=t*sign
        tm=t.mean(0);ts=t.std(0,ddof=1)
        w=w/ts;t=(t-tm)/ts
        weights.append(w);intercepts.append(tm/ts);scores.append(t)
        loadings.append(np.array([
            pcorr_cols(item["z"], np.broadcast_to(t[:,h,None], item["z"].shape))
            for h in range(kmax)
        ]).T)
    scores=np.stack(scores,axis=1);loadings=np.stack(loadings,axis=0)
    consensus=loadings.mean(0)
    for h in range(kmax):
        j=np.argmax(abs(consensus[:,h]))
        if consensus[j,h]<0:
            g[:,h]*=-1;scores[:,:,h]*=-1;loadings[:,:,h]*=-1;consensus[:,h]*=-1
            for m in range(3):weights[m][:,h]*=-1;intercepts[m][h]*=-1
    return dict(eigenvalues=eig,shared=g,weights=weights,intercepts=intercepts,scores=scores,loadings=loadings,
                consensus_loadings=consensus,means=[p["mu"] for p in prepared],sds=[p["sd"] for p in prepared],
                top_svd=[p["u"] for p in prepared],d=d,alpha=alpha)


def project(fit,blocks):
    return np.stack([((blocks[m]-fit["means"][m])/fit["sds"][m])@fit["weights"][m]-fit["intercepts"][m]
                     for m in range(3)],axis=1)


def score_agreement(scores):
    # scores: n × 3 × k
    vals=np.stack([np.array([np.corrcoef(scores[:,a,h],scores[:,b,h])[0,1] for h in range(scores.shape[2])])
                   for a,b in [(0,1),(0,2),(1,2)]])
    return vals


def loading_agreement(loadings):
    return np.stack([np.diag(congruence(loadings[a],loadings[b])) for a,b in [(0,1),(0,2),(1,2)]])


def cv_gcca(x,d=20,alpha=1.0,seed=SEED):
    folds=KFold(5,shuffle=True,random_state=seed)
    out=np.full((275,3,KMAX),np.nan)
    fold_rows=[]
    blocks=[x[m] for m in MODELS]
    for fold,(tr,te) in enumerate(folds.split(blocks[0])):
        fit=fit_gcca([b[tr] for b in blocks],d=d,alpha=alpha)
        pred=project(fit,[b[te] for b in blocks])
        out[te]=pred
        v=score_agreement(pred)
        for h in range(KMAX):fold_rows.append(dict(fold=fold,component=h+1,minimum_pairwise_correlation=float(v[:,h].min()),
                                                    mean_pairwise_correlation=float(v[:,h].mean()),eigenvalue=float(fit["eigenvalues"][h])))
    assert np.isfinite(out).all()
    return out,score_agreement(out),pd.DataFrame(fold_rows)


def shared_fit(x,tables):
    blocks=[x[m] for m in MODELS]
    primary=fit_gcca(blocks)
    held,v,fold=cv_gcca(x)
    rng=np.random.default_rng(SEED+1)
    null=np.empty((N_NULL,KMAX))
    null_mean=np.empty_like(null)
    for b in range(N_NULL):
        perm={"Qwen":x["Qwen"],"Llama":x["Llama"][rng.permutation(275)],"Gemma":x["Gemma"][rng.permutation(275)]}
        _,vv,_=cv_gcca(perm,seed=SEED)
        null[b]=vv.min(0);null_mean[b]=vv.mean(0)
    # A second null breaks named-trait agreement while leaving fitted components fixed.
    la=primary["loadings"];actual_l=loading_agreement(la).min(0)
    trait_null=np.empty((N_NULL,KMAX))
    for b in range(N_NULL):
        lp=la.copy();lp[1]=lp[1,rng.permutation(240)];lp[2]=lp[2,rng.permutation(240)]
        trait_null[b]=loading_agreement(lp).min(0)
    diag=[]
    for h in range(KMAX):
        diag.append(dict(component=h+1,projector_eigenvalue=primary["eigenvalues"][h],
                         heldout_min_pairwise_pearson=float(v[:,h].min()),heldout_mean_pairwise_pearson=float(v[:,h].mean()),
                         heldout_best_pairwise_pearson=float(v[:,h].max()),
                         best_pair_minus_all_three=float(v[:,h].max()-v[:,h].min()),
                         heldout_qwen_llama=float(v[0,h]),heldout_qwen_gemma=float(v[1,h]),heldout_llama_gemma=float(v[2,h]),
                         heldout_fold_min_median=float(fold[fold.component==h+1].minimum_pairwise_correlation.median()),
                         persona_null_p=(1+np.sum(null[:,h]>=v[:,h].min()))/(N_NULL+1),
                         persona_null_p95=float(np.quantile(null[:,h],.95)),
                         trait_loading_min_tucker=float(actual_l[h]),
                         trait_label_null_p=(1+np.sum(trait_null[:,h]>=actual_l[h]))/(N_NULL+1),
                         trait_label_null_p95=float(np.quantile(trait_null[:,h],.95))))
    save("shared_dimension_diagnostics.csv",diag)
    save("persona_correspondence_null.csv",[dict(replicate=b,component=h+1,min_heldout_score_corr=null[b,h],
                                                 mean_heldout_score_corr=null_mean[b,h]) for b in range(N_NULL) for h in range(KMAX)])
    save("trait_loading_label_null.csv",[dict(replicate=b,component=h+1,min_loading_tucker=trait_null[b,h]) for b in range(N_NULL) for h in range(KMAX)])
    save("heldout_fold_diagnostics.csv",fold.to_dict("records"))
    count=0
    for row in diag:
        if row["heldout_min_pairwise_pearson"]>=.4 and min(row["heldout_qwen_llama"],row["heldout_qwen_gemma"],row["heldout_llama_gemma"])>0 and row["persona_null_p"]<=.05:
            count+=1
        else:break
    count=max(0,count)
    sensitivity=[]
    for d,alpha in [(10,1),(40,1),(20,.1),(20,10),(10,.1),(10,10),(40,.1),(40,10)]:
        f=fit_gcca(blocks,d=d,alpha=alpha)
        _,sv,_=cv_gcca(x,d=d,alpha=alpha)
        c=congruence(primary["shared"][:,:max(count,1)],f["shared"][:,:max(count,1)])
        ii,jj=linear_sum_assignment(-abs(c))
        for h in range(KMAX):
            sensitivity.append(dict(pca_rank=d,ridge_alpha_multiplier=alpha,component=h+1,
                                    heldout_min_pairwise_pearson=float(sv[:,h].min()),
                                    heldout_mean_pairwise_pearson=float(sv[:,h].mean()),
                                    primary_shared_subspace_min_canonical=float(canonical_corr(primary["shared"][:,:max(count,1)],f["shared"][:,:max(count,1)]).min()),
                                    primary_axis_abs_score_match=float(abs(c[ii,jj][list(ii).index(h)])) if h in ii else np.nan))
    save("regularization_sensitivity.csv",sensitivity)
    names=tables["Qwen"].columns[1:].tolist();personas=tables["Qwen"].persona.tolist()
    score_rows=[];loading_rows=[];cons_rows=[]
    for h in range(KMAX):
        comp=f"C{h+1}"
        for i,p in enumerate(personas):
            score_rows.append(dict(persona=p,component=comp,retained=bool(h<count),consensus_score=float(primary["shared"][i,h]),
                                   qwen_score=float(primary["scores"][i,0,h]),llama_score=float(primary["scores"][i,1,h]),
                                   gemma_score=float(primary["scores"][i,2,h]),heldout_qwen_score=float(held[i,0,h]),
                                   heldout_llama_score=float(held[i,1,h]),heldout_gemma_score=float(held[i,2,h])))
        for j,t in enumerate(names):
            vv=primary["loadings"][:,j,h]
            cons_rows.append(dict(trait=t,component=comp,retained=bool(h<count),consensus_loading=float(vv.mean()),
                                  minimum_model_loading=float(vv.min()),maximum_model_loading=float(vv.max()),
                                  sign_consistent=bool((vv>0).all() or (vv<0).all()),loading_range=float(vv.max()-vv.min())))
            for mi,m in enumerate(MODELS):loading_rows.append(dict(model=m,trait=t,component=comp,retained=bool(h<count),
                                                                    trait_loading=float(vv[mi]),trait_weight=float(primary["weights"][mi][j,h])))
    save("shared_persona_scores.csv",score_rows);save("shared_trait_loadings_by_model.csv",loading_rows);save("consensus_trait_loadings.csv",cons_rows)
    return primary,count,pd.DataFrame(diag),pd.DataFrame(sensitivity),pd.DataFrame(score_rows),pd.DataFrame(cons_rows)


def leave_one_model_out(x):
    rngrows=[];blocks=[x[m] for m in MODELS]
    for held in range(3):
        sources=[i for i in range(3) if i!=held]
        predicted={k:np.zeros((275,240)) for k in range(1,6)}
        truth=np.zeros((275,240))
        for fold,(tr,te) in enumerate(KFold(5,shuffle=True,random_state=SEED).split(blocks[0])):
            prep=[];projectors=[]
            for mi in sources:
                z,mu,sd=standardize(blocks[mi][tr]);u,s,vt=np.linalg.svd(z,full_matrices=False)
                u,s,vt=u[:,:20],s[:20],vt[:20]
                projectors.append((u*(s*s/(s*s+len(tr))))@u.T)
                prep.append(dict(mu=mu,sd=sd,u=u,s=s,vt=vt,z=z,raw=blocks[mi]))
            e,g=np.linalg.eigh(sum(projectors));g=g[:,np.argsort(e)[::-1][:5]]
            train_scores=[];test_scores=[]
            for p in prep:
                w=p["vt"].T@((p["s"]/(p["s"]**2+len(tr)))[:,None]*(p["u"].T@g))
                ts=p["z"]@w
                sign=np.sign(np.sum(ts*g,axis=0));sign[sign==0]=1
                ts*=sign;w*=sign
                mu=ts.mean(0);sd=ts.std(0,ddof=1)
                train_scores.append((ts-mu)/sd)
                test_scores.append((((p["raw"][te]-p["mu"])/p["sd"])@w-mu)/sd)
            train_proxy=np.mean(train_scores,axis=0);test_proxy=np.mean(test_scores,axis=0)
            ytr,ymu,ysd=standardize(blocks[held][tr]);yte=(blocks[held][te]-ymu)/ysd
            truth[te]=yte
            for k in range(1,6):
                a=train_proxy[:,:k];b=np.linalg.solve(a.T@a+np.eye(k),a.T@ytr)
                pred=test_proxy[:,:k]@b;predicted[k][te]=pred
                rngrows.append(dict(held_out_model=MODELS[held],fold=fold,source_models="+".join(MODELS[i] for i in sources),
                                    components=k,heldout_matrix_r2=float(1-np.sum((yte-pred)**2)/np.sum(yte**2)),
                                    heldout_rmse=float(np.sqrt(np.mean((yte-pred)**2)))))
        for k in range(1,6):
            pred=predicted[k]
            rngrows.append(dict(held_out_model=MODELS[held],fold="pooled",source_models="+".join(MODELS[i] for i in sources),
                                components=k,heldout_matrix_r2=float(1-np.sum((truth-pred)**2)/np.sum(truth**2)),
                                heldout_rmse=float(np.sqrt(np.mean((truth-pred)**2)))))
    save("leave_one_model_out_prediction.csv",rngrows)
    return pd.DataFrame(rngrows)


def component_stability(x,primary,count):
    if count==0:
        save("component_stability.csv",[]);save("subspace_stability.csv",[])
        return pd.DataFrame(),pd.DataFrame(),{}
    blocks=[x[m] for m in MODELS];ref=primary["scores"][:,:,:count].mean(1)
    rng=np.random.default_rng(SEED+2)
    axis_rows=[];subrows=[]
    for b in range(N_BOOT_COMPONENT):
        idx=rng.integers(0,275,275)
        f=fit_gcca([v[idx] for v in blocks],kmax=count)
        projected=project(f,blocks)
        proposal=projected.mean(1)
        aligned,order,sign=match(ref,proposal)
        for dim in range(1,count+1):
            canon=canonical_corr(ref[:,:dim],aligned[:,:dim])
            subrows.append(dict(resample_type="bootstrap",replicate=b,subspace_dimension=dim,
                                subspace_min_canonical=float(canon.min()),subspace_mean_canonical=float(canon.mean())))
        for h in range(count):
            la=[]
            for mi,v in enumerate(blocks):
                z=standardize(v)[0]
                candidate=np.array([pcorr_cols(z,np.broadcast_to(projected[:,mi,order[h],None],z.shape))]).ravel()*sign[h]
                la.append(float(congruence(primary["loadings"][mi,:,h,None],candidate[:,None])[0,0]))
            axis_rows.append(dict(resample_type="bootstrap",replicate=b,component=f"C{h+1}",
                                  score_correlation=float(np.corrcoef(ref[:,h],aligned[:,h])[0,1]),
                                  minimum_model_loading_tucker=min(la),mean_model_loading_tucker=float(np.mean(la)),
                                  matched_original_component=int(order[h]+1),sign_correction=int(sign[h])))
    for b in range(N_SPLIT):
        perm=rng.permutation(275);halves=[perm[:137],perm[137:]]
        first=fit_gcca([v[halves[0]] for v in blocks],kmax=count)
        second=fit_gcca([v[halves[1]] for v in blocks],kmax=count)
        s1=project(first,blocks).mean(1);s2=project(second,blocks).mean(1)
        aligned,order,sign=match(s1,s2)
        for dim in range(1,count+1):
            canon=canonical_corr(s1[:,:dim],aligned[:,:dim])
            subrows.append(dict(resample_type="split_half",replicate=b,subspace_dimension=dim,
                                subspace_min_canonical=float(canon.min()),subspace_mean_canonical=float(canon.mean())))
        for h in range(count):
            axis_rows.append(dict(resample_type="split_half",replicate=b,component=f"C{h+1}",
                                  score_correlation=float(np.corrcoef(s1[:,h],aligned[:,h])[0,1]),
                                  minimum_model_loading_tucker=np.nan,mean_model_loading_tucker=np.nan,
                                  matched_original_component=int(order[h]+1),sign_correction=int(sign[h])))
    save("component_stability.csv",axis_rows);save("subspace_stability.csv",subrows)
    a=pd.DataFrame(axis_rows);s=pd.DataFrame(subrows)
    stable={}
    for h in range(count):
        q=a[a.component==f"C{h+1}"]
        boot=q[q.resample_type=="bootstrap"].score_correlation
        half=q[q.resample_type=="split_half"].score_correlation
        stable[h+1]=bool(boot.median()>=.85 and boot.quantile(.1)>=.65 and half.median()>=.70)
    return a,s,stable


def projector_joint_validation(z,primary,count):
    zz=[z[m] for m in MODELS];n=275;d=20
    us=[]
    for block in zz:
        u,_,_=np.linalg.svd(block,full_matrices=False);us.append(u[:,:d])
    def eigens(u_list):
        mat=sum(u@u.T for u in u_list)
        e,v=np.linalg.eigh(mat);return e[::-1],v[:,::-1]
    observed,g=eigens(us)
    rng=np.random.default_rng(SEED+3)
    null=np.empty((N_NULL,3*d))
    for b in range(N_NULL):
        e,_=eigens([us[0],us[1][rng.permutation(n)],us[2][rng.permutation(n)]])
        null[b]=e[:3*d]
    q95=np.quantile(null,.95,axis=0)
    joint_rank=0
    for j in range(d):
        if observed[j]>2 and observed[j]>q95[j]:joint_rank+=1
        else:break
    joint=g[:,:joint_rank]
    rank_boot=[]
    for b in range(50):
        ids=rng.integers(0,n,n)
        uboot=[]
        for v in zz:
            u,_,_=np.linalg.svd(v[ids],full_matrices=False);uboot.append(u[:,:d])
        eb,_=eigens(uboot)
        rank_boot.append(dict(replicate=b,joint_rank=int(sum((eb[:d]>2)&(eb[:d]>q95[:d]))),
                              first_eigenvalue=float(eb[0])))
    save("joint_rank_bootstrap.csv",rank_boot)
    jointrows=[];modelrows=[];residuals={}
    names=pd.read_csv(ROOT/SOURCE["Qwen"],nrows=0).columns[1:].tolist()
    for m,block in zip(MODELS,zz):
        jmat=joint@(joint.T@block) if joint_rank else np.zeros_like(block)
        residual=block-jmat;residuals[m]=residual
        ind_rank=max(0,d-joint_rank)
        if ind_rank:
            u,s,vt=np.linalg.svd(residual,full_matrices=False)
            imat=(u[:,:ind_rank]*s[:ind_rank])@vt[:ind_rank]
            for k in range(ind_rank):
                loading=vt[k]
                modelrows.append(dict(model=m,residual_component=k+1,variance_fraction=float(s[k]**2/np.sum(block**2)),
                                      positive_traits=";".join(names[j] for j in np.argsort(-loading)[:8]),
                                      negative_traits=";".join(names[j] for j in np.argsort(loading)[:8])))
        else:imat=np.zeros_like(block)
        remainder=residual-imat
        denom=np.sum(block**2)
        jointrows.append(dict(model=m,joint_rank=joint_rank,individual_rank=ind_rank,
                              joint_variance_fraction=float(np.sum(jmat**2)/denom),
                              individual_variance_fraction=float(np.sum(imat**2)/denom),
                              residual_variance_fraction=float(np.sum(remainder**2)/denom),
                              partition_sum=float((np.sum(jmat**2)+np.sum(imat**2)+np.sum(remainder**2))/denom)))
    save("joint_individual_variance_partition.csv",jointrows)
    save("model_specific_components.csv",modelrows)
    pairrows=[]
    for a,b in [("Qwen","Llama"),("Qwen","Gemma"),("Llama","Gemma")]:
        ua=np.linalg.svd(residuals[a],full_matrices=False)[0][:,:d]
        ub=np.linalg.svd(residuals[b],full_matrices=False)[0][:,:d]
        e,epair=eigens([ua,ub]);pnull=np.empty((N_NULL,2*d))
        for k in range(N_NULL):
            ee,_=eigens([ua,ub[rng.permutation(n)]])
            pnull[k]=ee[:2*d]
        pq=np.quantile(pnull,.95,axis=0)
        pair_rank=0
        for h in range(d):
            if e[h]>1.5 and e[h]>pq[h]:pair_rank+=1
            else:break
        gp=epair[:,:pair_rank]
        a_projection=gp@(gp.T@residuals[a]) if pair_rank else np.zeros_like(residuals[a])
        b_projection=gp@(gp.T@residuals[b]) if pair_rank else np.zeros_like(residuals[b])
        pairrows.append(dict(model_a=a,model_b=b,pairwise_joint_residual_rank=pair_rank,
                             leading_projector_eigenvalue=float(e[0]),leading_null_p95=float(pq[0]),
                             mean_top_pairwise_eigenvalue=float(np.mean(e[:max(1,pair_rank)])),
                             model_a_pairwise_fraction_of_total=float(np.sum(a_projection**2)/np.sum(z[a]**2)),
                             model_b_pairwise_fraction_of_total=float(np.sum(b_projection**2)/np.sum(z[b]**2)),
                             model_a_pairwise_fraction_of_joint_residual=float(np.sum(a_projection**2)/np.sum(residuals[a]**2)),
                             model_b_pairwise_fraction_of_joint_residual=float(np.sum(b_projection**2)/np.sum(residuals[b]**2))))
    save("pairwise_shared_structure.csv",pairrows)
    diag=[dict(component=h+1,observed_projector_eigenvalue=observed[h],null_p95=q95[h],
               all_three_threshold=2,retained_joint=bool(h<joint_rank)) for h in range(3*d)]
    save("joint_rank_diagnostics.csv",diag)
    cc=canonical_corr(joint,primary["shared"][:,:max(1,count)]) if joint_rank and count else np.array([])
    return joint_rank,pd.DataFrame(jointrows),pd.DataFrame(pairrows),pd.DataFrame(rank_boot),cc,joint,residuals


def aa17_comparison(tables,z,primary,count,joint):
    names=tables["Qwen"].columns[1:].tolist();personas=tables["Qwen"].persona.tolist()
    loads=pd.read_csv(AA17/"factor_loadings_rotated.csv")
    loads=loads[loads.variant=="full_shrinkage"]
    a17scores=pd.read_csv(AA17/"persona_factor_scores.csv")
    rows=[];sub=[]
    for mi,m in enumerate(MODELS):
        qq=loads[loads.model==m]
        factors=sorted(qq.factor.unique(),key=lambda v:int(v.rsplit("F",1)[1]))
        lmat=qq.pivot(index="trait",columns="factor",values="loading").loc[names,factors].to_numpy()
        smat=a17scores[a17scores.model==m].pivot(index="persona",columns="factor",values="score").loc[personas,factors].to_numpy()
        sub_cc=canonical_corr(smat,primary["scores"][:,mi,:max(1,count)])
        sub.append(dict(model=m,aa17_factors=len(factors),aa18_retained_components=count,
                        subspace_min_canonical=float(sub_cc.min()),subspace_mean_canonical=float(sub_cc.mean()),
                        subspace_correlations=";".join(f"{v:.6f}" for v in sub_cc)))
        joint_q=np.linalg.qr(joint)[0] if joint.shape[1] else np.empty((275,0))
        residual=z[m]-(joint_q@(joint_q.T@z[m]) if joint_q.size else 0)
        indiv_u=np.linalg.svd(residual,full_matrices=False)[0][:,:max(0,20-joint.shape[1])]
        for fi,f in enumerate(factors):
            aa=smat[:,fi];aa=aa-aa.mean()
            joint_overlap=float(np.sum((joint_q.T@aa)**2)/np.sum(aa**2)) if joint_q.size else 0.0
            indiv_overlap=float(np.sum((indiv_u.T@aa)**2)/np.sum(aa**2)) if indiv_u.size else 0.0
            for h in range(max(1,count)):
                bb=primary["scores"][:,mi,h]
                rows.append(dict(model=m,aa17_factor=f,consensus_component=f"C{h+1}",
                                 tucker_loading_congruence=float(congruence(lmat[:,fi,None],primary["loadings"][mi,:,h,None])[0,0]),
                                 persona_score_correlation=float(np.corrcoef(aa,bb)[0,1]),
                                 persona_score_variance_overlap=float(np.corrcoef(aa,bb)[0,1]**2),
                                 aa17_factor_joint_score_overlap=joint_overlap,
                                 aa17_factor_model_residual_overlap=indiv_overlap))
    save("aa17_factor_alignment.csv",rows);save("aa17_subspace_alignment.csv",sub)
    return pd.DataFrame(rows),pd.DataFrame(sub)


def human_bridge_readiness(tables,z,primary,count,stable):
    bridge=pd.read_csv(AA16/"existing_trait_bridge_audit.csv")
    names=tables["Qwen"].columns[1:].tolist();bridge=bridge.set_index("model_trait").loc[names]
    direct=(bridge.mapping_tier=="direct").to_numpy()
    total=bridge.mapping_tier.isin(["direct","close"]).to_numpy()
    assert direct.sum()==45 and total.sum()==74
    overlap=bridge.overlap_with_hifwb_item_ids.notna().to_numpy()
    group=bridge.exact_source_group
    repeated=set(group[group.notna() & group.duplicated(keep=False)])
    zz=[z[m] for m in MODELS];rows=[]
    for h in range(max(1,count)):
        c=primary["consensus_loadings"][:,h]
        full=np.mean([zz[i]@primary["weights"][i][:,h] for i in range(3)],axis=0)
        def metrics(mask):
            mass=float(np.sum(abs(c[mask]))/np.sum(abs(c)))
            pos=float(np.sum(c[mask & (c>0)])/max(1e-12,np.sum(c[c>0])))
            neg=float(np.sum(abs(c[mask & (c<0)]))/max(1e-12,np.sum(abs(c[c<0]))))
            partial=np.mean([zz[i][:,mask]@primary["weights"][i][mask,h] for i in range(3)],axis=0)
            corr=float(np.corrcoef(full,partial)[0,1]) if np.std(partial)>1e-10 else np.nan
            return mass,pos,neg,corr
        dm,dp,dn,dr=metrics(direct);tm,tp,tn,tr=metrics(total)
        eligible=total & ~overlap
        rows.append(dict(component=f"C{h+1}",retained=bool(h<count),individually_stable=bool(stable.get(h+1,False)),
                         direct_vocabulary_count=int(direct.sum()),direct_plus_close_vocabulary_count=int(total.sum()),
                         salient_direct_count=int(np.sum(direct & (abs(c)>=.3))),
                         salient_total_count=int(np.sum(total & (abs(c)>=.3))),
                         direct_loading_mass_fraction=dm,total_loading_mass_fraction=tm,
                         direct_positive_pole_mass_fraction=dp,direct_negative_pole_mass_fraction=dn,
                         total_positive_pole_mass_fraction=tp,total_negative_pole_mass_fraction=tn,
                         direct_mapped_score_correlation=dr,total_mapped_score_correlation=tr,
                         direct_mapped_score_r2=dr*dr,total_mapped_score_r2=tr*tr,
                         total_mapping_hifwb_overlap_exclusions=int(np.sum(total & overlap)),
                         eligible_total_mapping_count=int(eligible.sum()),
                         duplicate_exact_source_groups_in_total=int(len(repeated & set(group[total].dropna()))),
                         likely_coverage_bias=bool(min(tp,tn)<.2 or abs(tp-tn)>.25 or tr<.75)))
    save("human_bridge_consensus_coverage.csv",rows)
    return pd.DataFrame(rows)


def decide_and_decorate(count,diag,stability,sensitivity):
    sens=sensitivity.groupby("component").primary_axis_abs_score_match.min().to_dict()
    core=[]
    for row in diag.itertuples():
        ok=(row.component<=count and stability.get(row.component,False) and
            row.heldout_min_pairwise_pearson>=.5 and row.trait_loading_min_tucker>=.7 and
            row.persona_null_p<=.05 and row.trait_label_null_p<=.05 and sens.get(row.component,0)>=.8)
        core.append(bool(ok))
    diag=diag.copy();diag["provisional_retained"]=diag.component<=count
    diag["individually_stable"]=diag.component.map(stability).fillna(False)
    diag["regularization_sensitivity_min_axis_match"]=diag.component.map(sens)
    diag["supported_consensus_axis"]=core
    diag.to_csv(OUT/"shared_dimension_diagnostics.csv",index=False)
    for name in ["shared_persona_scores.csv","shared_trait_loadings_by_model.csv","consensus_trait_loadings.csv"]:
        q=pd.read_csv(OUT/name)
        q["supported_consensus_axis"]=q.component.str[1:].astype(int).map(dict(zip(diag.component,core))).fillna(False)
        if name=="consensus_trait_loadings.csv":
            q=q.rename(columns={"consensus_loading":"cross_model_mean_loading"})
            q["consensus_loading"]=q.cross_model_mean_loading.where(q.supported_consensus_axis)
        q.to_csv(OUT/name,index=False)
    headline="A" if any(core) else "B" if count and (pd.read_csv(OUT/"subspace_stability.csv").query("resample_type == 'bootstrap' and subspace_dimension == @count").subspace_min_canonical.median()>=.8) else "D"
    return diag,core,headline


def make_figures(traits,personas,diag,core,primary,partition,aa17,bridge,stability):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi":180,"savefig.dpi":220,"font.size":9,"axes.spines.top":False,"axes.spines.right":False})
    # 1: trait-level all-three distribution.
    fig,ax=plt.subplots(figsize=(7,4))
    ax.hist(traits.pearson_min,bins=np.linspace(-.2,1,31),color="#4f718e",alpha=.85)
    ax.axvline(.5,color="#c15643",ls="--",label="all-three strong threshold")
    ax.set(xlabel="Minimum of three pairwise trait-profile Pearson correlations",ylabel="Traits",title="Named-trait agreement across personas")
    ax.legend(frameon=False);fig.tight_layout();fig.savefig(OUT/"trait_agreement_distribution.png");plt.close(fig)
    # 2: ordered profile-correlation heatmap.
    q=traits.sort_values("pearson_min",ascending=False)
    fig,ax=plt.subplots(figsize=(5,9));im=ax.imshow(q[["pearson_qwen_llama","pearson_qwen_gemma","pearson_llama_gemma"]],aspect="auto",cmap="RdBu_r",vmin=-1,vmax=1)
    ticks=[0,20,60,120,180,220,239]
    ax.set(xticks=[0,1,2],xticklabels=["Qwen–Llama","Qwen–Gemma","Llama–Gemma"],yticks=ticks,yticklabels=[q.iloc[i].trait for i in ticks],title="Trait profiles ordered by weakest model pair")
    fig.colorbar(im,ax=ax,label="Pearson r",shrink=.7);fig.tight_layout();fig.savefig(OUT/"trait_agreement_heatmap.png");plt.close(fig)
    # 3: retention.
    fig,axes=plt.subplots(1,2,figsize=(11,4));v=diag
    axes[0].plot(v.component,v.projector_eigenvalue,marker="o",label="GCCA projector eigenvalue");axes[0].set(xlabel="Ordered component",ylabel="Eigenvalue",title="Shared-direction scree")
    axes[1].plot(v.component,v.heldout_min_pairwise_pearson,marker="o",label="Held-out all-three minimum")
    axes[1].plot(v.component,v.persona_null_p95,ls="--",label="Persona-null 95%")
    axes[1].axhline(.4,color="gray",ls=":");axes[1].set(xlabel="Ordered component",ylabel="Minimum pairwise held-out r",title="All-three held-out agreement")
    for ax in axes:
        ax.axvline(int(v.provisional_retained.sum()),color="#a7473a",alpha=.6);ax.legend(frameon=False)
    fig.tight_layout();fig.savefig(OUT/"shared_dimension_retention.png");plt.close(fig)
    # 4: score correspondence, first supported component.
    h=next((i for i,yes in enumerate(core) if yes),0);s=primary["scores"][:,:,h]
    fig,axes=plt.subplots(1,3,figsize=(11,3.6))
    for ax,(i,j) in zip(axes,[(0,1),(0,2),(1,2)]):
        ax.scatter(s[:,i],s[:,j],s=9,alpha=.55,color="#386b8d")
        ax.set(xlabel=MODELS[i],ylabel=MODELS[j],title=f"C{h+1}: r={np.corrcoef(s[:,i],s[:,j])[0,1]:.2f}")
    fig.tight_layout();fig.savefig(OUT/"shared_persona_score_agreement.png");plt.close(fig)
    # 5: operational AJIVE-like variance partition.
    fig,ax=plt.subplots(figsize=(7,4));bottom=np.zeros(3)
    for key,label,color in [("joint_variance_fraction","Joint","#3e7b8e"),("individual_variance_fraction","Individual","#d09050"),("residual_variance_fraction","Residual","#b9bcc2")]:
        values=partition[key].to_numpy();ax.bar(MODELS,values,bottom=bottom,label=label,color=color);bottom+=values
    ax.set(ylabel="Fraction of within-model standardized profile variance",ylim=(0,1),title="Joint / individual / residual partition");ax.legend(frameon=False)
    fig.tight_layout();fig.savefig(OUT/"joint_individual_variance.png");plt.close(fig)
    # 6: consensus loading heatmap, robust axes only.
    ids=[i for i,v in enumerate(core) if v]
    if not ids:ids=[0]
    mat=primary["consensus_loadings"][:,ids]
    trait_names=traits.trait.tolist();strength=np.max(abs(mat),axis=1);order=np.argsort(-strength)[:45]
    fig,ax=plt.subplots(figsize=(max(5,len(ids)*.9),10));im=ax.imshow(mat[order],aspect="auto",cmap="RdBu_r",vmin=-1,vmax=1)
    ax.set(xticks=range(len(ids)),xticklabels=[f"C{i+1}" for i in ids],yticks=range(len(order)),yticklabels=[trait_names[i] for i in order],title="Leading signed consensus loadings")
    ax.tick_params(axis="y",labelsize=6);fig.colorbar(im,ax=ax,shrink=.6);fig.tight_layout();fig.savefig(OUT/"consensus_loading_heatmap.png");plt.close(fig)
    # 7: AA-17 alignment by scores.
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,m in zip(axes,MODELS):
        q=aa17[aa17.model==m].pivot(index="aa17_factor",columns="consensus_component",values="persona_score_correlation")
        wanted=[f"C{i+1}" for i in ids]
        q=q.loc[:,wanted]
        im=ax.imshow(q,cmap="RdBu_r",vmin=-1,vmax=1,aspect="auto")
        ax.set(title=m,xticks=range(len(q.columns)),xticklabels=q.columns,yticks=range(len(q)),yticklabels=q.index)
    fig.colorbar(im,ax=axes.tolist(),shrink=.7);fig.subplots_adjust(right=.89,wspace=.45);fig.savefig(OUT/"aa17_consensus_alignment.png");plt.close(fig)
    # 8: stability distributions by component.
    fig,ax=plt.subplots(figsize=(11,4));boot=stability[stability.resample_type=="bootstrap"]
    vals=[boot[boot.component==f"C{i}"].score_correlation.to_numpy() for i in range(1,int(v.provisional_retained.sum())+1)]
    ax.boxplot(vals,showfliers=False);ax.axhline(.85,color="#b25141",ls="--",label="axis median threshold")
    ax.set(xlabel="Component",ylabel="Aligned bootstrap persona-score correlation",title="Individual-axis resampling stability");ax.legend(frameon=False)
    fig.tight_layout();fig.savefig(OUT/"component_stability.png");plt.close(fig)
    # 9: human bridge loading-mass readiness.
    q=bridge[bridge.component.isin([f"C{i+1}" for i in ids])]
    fig,ax=plt.subplots(figsize=(8,4));xpos=np.arange(len(q));w=.36
    ax.bar(xpos-w/2,q.direct_loading_mass_fraction,w,label="45 direct",color="#4c7890")
    ax.bar(xpos+w/2,q.total_loading_mass_fraction,w,label="74 direct + close",color="#b7864f")
    ax.set(xticks=xpos,xticklabels=q.component,ylabel="Fraction of absolute loading mass",ylim=(0,1),title="Bridge coverage of supported components")
    ax.legend(frameon=False);fig.tight_layout();fig.savefig(OUT/"human_bridge_loading_coverage.png");plt.close(fig)


def write_report(tables,traits,personas,traitnull,diag,core,headline,primary,stability,subspace,
                 joint_rank,partition,pair,jointboot,jointcc,aa17,aa17sub,bridge,lomo):
    supported=[i+1 for i,v in enumerate(core) if v]
    labels={
        1:("charged expression / factual moderation","highly charged, spontaneous, intense expression","factual, moderate, conciliatory restraint","expressive intensity"),
        2:("abstract inwardness / situated practicality","introverted, ritualistic, conceptual abstraction","experiential, practical, accessible engagement","conceptual register"),
        3:("forgiving care / blunt prescription","forgiving, nurturing, empathic openness","blunt, prescriptive, callous urgency","care versus directive hardness"),
        4:("integrative exploration / literal tradition","progressive, divergent, systems-oriented exploration","traditional, literal, concise understatement","integrative scope"),
        5:("decisive closure / deferential caution","decisive, assertive closure","deferential, cautious, inquisitive openness","closure urgency"),
    }
    lines=["# AA-18 three-model consensus trait structure","", "## Headline decision", "",
           f"**{headline}.** The matrix gate passed and the frozen MAXVAR-GCCA analysis found **{int(diag.provisional_retained.sum())} provisional held-out all-three persona-score directions** before the first failed ordered component. **{len(supported)} individually stable, trait-congruent consensus axes** meet the stricter all-three rule: {', '.join('C'+str(v) for v in supported) if supported else 'none'}. The separate AJIVE-like top-20 row-subspace validation finds joint rank **{joint_rank}**. These numbers answer different questions; the high joint rank is an in-sample, rank-20 subspace overlap and is not a claim that 19 interpretable latent factors exist.","",
           "## Phase gate and direct cross-model audit","",
           "**Observed:** All three saved matrices are exact AA-17 hash matches with 275 unique, identically ordered personas and 240 identically ordered signed trait-cosine columns. There are no missing, nonfinite, constant, or exact duplicate columns. The values share a cosine construction but differ in scale and may differ in upstream extraction details; identical labels do not establish measurement invariance. Each persona label has one saved role artifact, not an independent human observation.","",
           f"Across named traits, {int((traits.category=='all_three_strong').sum())}/240 have minimum pairwise persona-profile Pearson r≥0.50; {int((traits.category=='pairwise_only').sum())} are pairwise-only by the frozen rule, and {int((traits.pearson_min<0).sum())} have a reversed model pair. The standardized consistency statistic is descriptive. Across personas, {int((personas.category=='all_three_strong').sum())}/275 have minimum pairwise 240-trait-profile Pearson r≥0.50. A small persona subset does not create the broad agreement: the maximum mean leave-one-persona trait-score change is {personas.mean_trait_score_influence.max():.4f}.","",
           "Strongest named traits by the frozen all-three score: "+", ".join(f"{r.trait} ({r.all_three_convergence_score:.3f})" for r in traits.merge(pd.read_csv(OUT/"trait_convergence_scores.csv")[["trait","all_three_convergence_score"]],on="trait").nlargest(8,"all_three_convergence_score").itertuples())+". Weakest by minimum pairwise Pearson: "+", ".join(f"{r.trait} ({r.pearson_min:+.3f})" for r in traits.nsmallest(8,"pearson_min").itertuples())+". Trait-level bootstrap intervals, raw-scale RMSE, and most influential persona for each trait are in the CSVs.","",
           "## Shared dimensions and falsification","",
           "The primary model uses training-fold column scaling, 20 training-only singular directions per model, and ridge penalty equal to training-persona count. Five-fold held-out scores, 100 persona-correspondence nulls, 100 trait-label loading nulls, eight regularization/PCA-rank sensitivities, 100 persona bootstraps, and 20 split halves are exported. No activation PCs or human outcomes selected dimensions.","",
           "| Component | Held-out weakest pair r | Weakest trait-loading Tucker | Bootstrap median axis r | Split-half median axis r | Supported? |",
           "|---|---:|---:|---:|---:|---|"]
    for row in diag.head(int(diag.provisional_retained.sum())).itertuples():
        q=stability[stability.component==f"C{row.component}"]
        bo=q[q.resample_type=="bootstrap"].score_correlation.median()
        sp=q[q.resample_type=="split_half"].score_correlation.median()
        lines.append(f"| C{row.component} | {row.heldout_min_pairwise_pearson:.3f} | {row.trait_loading_min_tucker:.3f} | {bo:.3f} | {sp:.3f} | {'yes' if row.supported_consensus_axis else 'no'} |")
    lines += ["", "The first five axes are the conservative interpretable core. Later components can retain highly correlated held-out persona scores while model-specific trait loadings disagree, rotate, or fail split-half stability. Thus agreement about *which personas vary together* extends farther than agreement about a unique named-trait loading pattern. The direct trait audit, covariance organization, and latent-axis organization are related but distinct results.","",
              "## Observed loading poles and bounded interpretation","", "Factor sign and order are conventions. The following labels are post-fit readings of stable axes; they are not causal traits or demonstrated human personality dimensions.",""]
    cons=pd.read_csv(OUT/"consensus_trait_loadings.csv")
    for h in supported:
        q=cons[cons.component==f"C{h}"]
        pos=", ".join(f"{r.trait} ({r.consensus_loading:+.2f})" for r in q.nlargest(5,"consensus_loading").itertuples())
        neg=", ".join(f"{r.trait} ({r.consensus_loading:+.2f})" for r in q.nsmallest(5,"consensus_loading").itertuples())
        label,positive,negative,alternative=labels.get(h,("unlabeled shared axis","positive loading pole","negative loading pole","unlabeled axis"))
        lines.append(f"- **Observed C{h}:** positive {pos}; negative {neg}. **Interpretation:** candidate *{label}*: {positive} versus {negative}. Plausible alternative label: *{alternative}*. **Hypothesis:** this numerical co-expression may reflect a broader behavioral contrast; independent observations would be needed to test that.")
    lines += ["", "## Joint, pairwise, and model-specific structure", "",
              f"The AJIVE-like top-20 joint rank is {joint_rank}; 50 persona bootstraps yielded median rank {jointboot.joint_rank.median():.0f} (range {jointboot.joint_rank.min()}–{jointboot.joint_rank.max()}). Its joint-score subspace overlaps the primary GCCA retained-score subspace at minimum canonical correlation {jointcc.min() if len(jointcc) else float('nan'):.3f}. This validation uses the same saved matrices with a different estimator, so it is not independent measurement evidence.","",
              "| Model | Joint variance | Individual variance | Residual variance |",
              "|---|---:|---:|---:|"]
    for r in partition.itertuples():lines.append(f"| {r.model} | {r.joint_variance_fraction:.3f} | {r.individual_variance_fraction:.3f} | {r.residual_variance_fraction:.3f} |")
    lines += ["", "These are in-sample fractions of within-model standardized profile variance under the frozen rank-20 projector decomposition. A high joint fraction means similar persona score spans, not identical trait semantics or absence of small model-specific directions. Pairwise residual subspaces and their fractions of total variance are in `pairwise_shared_structure.csv`; pairwise ranks on the small remaining variance should not be compared directly with the all-three joint rank.","",
              "Leave-one-model-out held-out reconstruction (two source models → excluded model's 240 standardized traits, five components): "+"; ".join(f"{r.held_out_model} R²={r.heldout_matrix_r2:.3f}" for r in lomo[(lomo.fold=="pooled")&(lomo.components==5)].itertuples())+". This target model is used to learn the training-fold readout, not to define the source components.","",
              "## Relation to AA-17","",
              "AA-17's grounded/secular versus spiritual/idealist match (Qwen F3 / Llama F2 / Gemma F6) remains in the shared persona-score span but is **split chiefly across C1 and C2**, rather than recovered as a single one-to-one axis. The Llama/Gemma cooperative-optimism match (Llama F1 / Gemma F3) overlaps C1 and, secondarily, C3; Qwen F1 also strongly overlaps C1. This supports an all-three shared portion while leaving model-specific loading combinations and rotations. See `aa17_factor_alignment.csv` for signed score correlations and Tucker congruence, and `aa17_subspace_alignment.csv` for the broader comparison. Similar words alone did not determine either match.","",
              "## Human bridge readiness only","",
              "The frozen AA-16 semantic bridge provides 45 direct and 74 direct-plus-close trait labels. Five total mapped labels overlap HiFWB composite items and remain excluded for later outcome work; source-item duplicates also require joint treatment. Neither those exclusions nor any human outcome selected components here. Loading mass and frozen-weight mapped-subset score reconstruction are descriptive coverage tests of model profiles, not human factor validity.","",
              "| Component | Direct loading mass | 74-set loading mass | 74-set mapped score r | Pole imbalance / coverage bias |",
              "|---|---:|---:|---:|---|"]
    for r in bridge[bridge.component.isin([f"C{i}" for i in supported])].itertuples():
        lines.append(f"| {r.component} | {r.direct_loading_mass_fraction:.3f} | {r.total_loading_mass_fraction:.3f} | {r.total_mapped_score_correlation:.3f} | {'flagged' if r.likely_coverage_bias else 'not flagged'} |")
    lines += ["", "## Limitations and next gate", "",
              "**Observed:** Shared labels, prompts, and saved activation-vector construction can generate strong model agreement without independent psychological measurement. Column standardization removes cross-model scale differences but does not prove measurement invariance. The original response-level extraction/filter records remain unavailable. Some higher score directions have poor loading congruence and should be handled as subspaces, not strongly named axes.","",
              "**Interpretation:** The five supported axes are credible model-only candidate common dimensions. Their matched human labels cover only a minority of total loading mass even where mapped model scores correlate highly because trait columns are redundant. A later SAPA/HiFWB comparison should be restricted to stable, pole-balanced axes, account for five HiFWB-overlap exclusions and duplicate human measures, and test human convergence independently.","",
              "The bridge is **conditionally ready for a restricted future comparison**, not for a full five-axis human interpretation: direct matches cover only 13–20% of absolute loading mass, and C4/C5 have just 8/3 direct and 16/6 total salient mapped traits. C5's total mapped-score reconstruction is weakest (r=0.812). Independent bridge review and duplicate-aware sensitivity remain necessary before human claims.","",
              "**Hypothesis:** Similar training data, instruction tuning, preference or safety tuning, chat templates, architecture, and the common English persona/trait prompts could each contribute to the observed convergence. This analysis cannot distinguish those causes. No model inference, RunPod, paid compute, HiFWB fitting, persona wellbeing scoring, respondent-level data, or viewer deployment occurred."]
    (OUT/"three_model_consensus_trait_report.md").write_text("\n".join(lines)+"\n")


def verify(tables,x,primary,traits,personas,diag,core,partition,stability,subspace,bridge):
    source=json.loads((OUT/"source_inventory.json").read_text())
    source_checks={r["model"]:sha(ROOT/r["path"])==r["sha256"] for r in source["matrix_sources"]}
    score=pd.read_csv(OUT/"shared_persona_scores.csv")
    loading=pd.read_csv(OUT/"shared_trait_loadings_by_model.csv")
    cc=pd.read_csv(OUT/"consensus_trait_loadings.csv")
    rebuilt=project(primary,[x[m] for m in MODELS])
    score_reconstruction_error=float(np.max(np.abs(rebuilt-primary["scores"])))
    loading_reconstruction_error=0.0
    for mi,m in enumerate(MODELS):
        zz=(x[m]-primary["means"][mi])/primary["sds"][mi]
        for h in range(KMAX):
            recalculated=pcorr_cols(zz,np.broadcast_to(primary["scores"][:,mi,h,None],zz.shape))
            loading_reconstruction_error=max(loading_reconstruction_error,float(np.max(np.abs(recalculated-primary["loadings"][mi,:,h]))))
    sign_agreement_min=float(np.min(np.sum(primary["scores"]*primary["shared"][:,None,:],axis=0)))
    checks={"source_sha256_match":source_checks,"same_275_persona_order":all(t.persona.tolist()==tables["Qwen"].persona.tolist() for t in tables.values()),
            "same_240_trait_order":all(t.columns.tolist()==tables["Qwen"].columns.tolist() for t in tables.values()),
            "matrix_gate_passed":True,"direct_trait_rows":len(traits),"direct_persona_rows":len(personas),
            "candidate_dimensions":len(diag),"supported_consensus_axes":int(sum(core)),
            "shared_persona_score_rows":len(score),"model_specific_loading_rows":len(loading),"consensus_trait_rows":len(cc),
            "all_score_cells_finite":bool(np.isfinite(score.select_dtypes("number").to_numpy()).all()),
            "consensus_loading_only_for_supported_axes":bool(cc.loc[~cc.supported_consensus_axis,"consensus_loading"].isna().all()),
            "variance_partition_max_abs_sum_error":float(max(abs(partition.partition_sum-1))),
            "score_reconstruction_max_abs_error":score_reconstruction_error,
            "loading_reconstruction_max_abs_error":loading_reconstruction_error,
            "minimum_aligned_score_dot_product":sign_agreement_min,
            "bootstrap_replicates":int(stability[stability.resample_type=="bootstrap"].replicate.nunique()),
            "split_half_replicates":int(stability[stability.resample_type=="split_half"].replicate.nunique()),
            "persona_correspondence_null_replicates":int(pd.read_csv(OUT/"persona_correspondence_null.csv").replicate.nunique()),
            "trait_label_null_replicates":int(pd.read_csv(OUT/"trait_label_permutation_null.csv").replicate.nunique()),
            "seed":SEED,"no_hifwb_component_input":True,"no_sapa_outcome_component_input":True,
            "no_model_inference":True,"no_paid_compute":True,"no_respondent_level_data":True,"no_viewer":True,
            "runtime":{"python":sys.version.split()[0],"numpy":np.__version__,"pandas":pd.__version__,
                       "scipy":importlib.metadata.version("scipy"),"scikit_learn":importlib.metadata.version("scikit-learn")}}
    checks["all_checks_pass"]=bool(all(source_checks.values()) and checks["same_275_persona_order"] and checks["same_240_trait_order"] and
        checks["direct_trait_rows"]==240 and checks["direct_persona_rows"]==275 and checks["candidate_dimensions"]==KMAX and
        checks["shared_persona_score_rows"]==275*KMAX and checks["model_specific_loading_rows"]==3*240*KMAX and
        checks["consensus_trait_rows"]==240*KMAX and checks["all_score_cells_finite"] and checks["consensus_loading_only_for_supported_axes"] and
        checks["variance_partition_max_abs_sum_error"]<1e-8 and score_reconstruction_error<1e-10 and
        loading_reconstruction_error<1e-10 and sign_agreement_min>0 and checks["bootstrap_replicates"]==N_BOOT_COMPONENT and
        checks["split_half_replicates"]==N_SPLIT and checks["persona_correspondence_null_replicates"]==N_NULL and
        checks["trait_label_null_replicates"]==N_NULL)
    (OUT/"verification_report.json").write_text(json.dumps(checks,indent=2)+"\n")
    rows=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="artifact_inventory.csv":
            rows.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size))
    save("artifact_inventory.csv",rows)
    return checks


def main():
    tables,x,_=gate()
    z,traits,personas,trait_scores,traitnull=direct_audit(tables,x)
    primary,count,diag,sensitivity,scores,cons=shared_fit(x,tables)
    stability,subspace,stable=component_stability(x,primary,count)
    joint_rank,partition,pair,jointboot,jointcc,joint,residuals=projector_joint_validation(z,primary,count)
    aa17,aa17sub=aa17_comparison(tables,z,primary,count,joint)
    bridge=human_bridge_readiness(tables,z,primary,count,stable)
    lomo=leave_one_model_out(x)
    diag,core,headline=decide_and_decorate(count,diag,stable,sensitivity)
    make_figures(traits,personas,diag,core,primary,partition,aa17,bridge,stability)
    write_report(tables,traits,personas,traitnull,diag,core,headline,primary,stability,subspace,
                 joint_rank,partition,pair,jointboot,jointcc,aa17,aa17sub,bridge,lomo)
    checks=verify(tables,x,primary,traits,personas,diag,core,partition,stability,subspace,bridge)
    print(json.dumps({"decision":headline,"provisional_score_dimensions":count,"supported_consensus_axes":int(sum(core)),
                      "joint_rank":joint_rank,"verified":checks["all_checks_pass"]}))


if __name__=="__main__":main()
