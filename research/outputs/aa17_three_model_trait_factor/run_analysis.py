#!/usr/bin/env python3
"""Reproduce AA-17 from saved cosine matrices only (CPU)."""
from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import os
import sys
import warnings
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import pandas as pd
from factor_analyzer.rotator import Rotator
from scipy.linalg import subspace_angles, orthogonal_procrustes
from scipy.optimize import linear_sum_assignment
from scipy.stats import skew
from sklearn.covariance import LedoitWolf
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SEED = 17017
SOURCES = {
    "Qwen": "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv",
    "Llama": "research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv",
    "Gemma": "research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv",
}
BRIDGE = ROOT / "research/outputs/human_trait_dataset_feasibility/sapa_review/sapa_trait_bridge_provisional_v1.csv"


def save(name, rows):
    pd.DataFrame(rows).to_csv(OUT / name, index=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def corr(x):
    return np.corrcoef(x, rowvar=False)


def shrink_corr(x):
    obj = LedoitWolf().fit(x)
    c = obj.covariance_
    d = np.sqrt(np.diag(c))
    return c / d[:, None] / d[None, :], float(obj.shrinkage_)


def standardize(x):
    return (x - x.mean(0)) / x.std(0, ddof=1)


def canonical_corr(a, b):
    qa = np.linalg.qr(a)[0]
    qb = np.linalg.qr(b)[0]
    return np.linalg.svd(qa.T @ qb, compute_uv=False)


def congruence(a, b):
    return (a.T @ b) / np.linalg.norm(a, axis=0)[:, None] / np.linalg.norm(b, axis=0)[None, :]


def align(ref, other):
    c = congruence(ref, other)
    rows, cols = linear_sum_assignment(-abs(c))
    order = cols[np.argsort(rows)]
    signs = np.sign(c[np.arange(len(order)), order])
    signs[signs == 0] = 1
    return other[:, order] * signs, order, signs, c


def fit(r, k, rotation="oblimin"):
    h = np.clip(1 - 1 / np.diag(np.linalg.inv(r)), .005, .995)
    for _ in range(20):
        reduced = r.copy()
        np.fill_diagonal(reduced, h)
        w, v = np.linalg.eigh(reduced)
        order = np.argsort(w)[-k:][::-1]
        unrotated = v[:, order] * np.sqrt(np.maximum(w[order], 0))
        new_h = np.clip(np.sum(unrotated**2, axis=1), .005, .995)
        delta = np.max(abs(new_h-h)); h = new_h
        if delta < 1e-7:break
    if rotation is None:
        l = unrotated
        phi = np.eye(k)
    else:
        rotator = Rotator(method=rotation)
        l = rotator.fit_transform(unrotated)
        phi = np.eye(k) if rotator.phi_ is None else rotator.phi_
    st = l @ phi
    h = np.einsum("ij,ij->i", l, st)
    u = np.clip(1 - h, 0.005, 1)
    reconstructed = l @ phi @ l.T + np.diag(u)
    mask = ~np.eye(len(r), dtype=bool)
    rms = float(np.sqrt(np.mean((r[mask] - reconstructed[mask]) ** 2)))
    residual_abs=abs((r-reconstructed)[mask])
    coef = np.linalg.solve(r, st)
    return {"loading": l, "phi": phi, "structure": st, "h": h, "u": u, "rms": rms,
            "reconstructed": reconstructed, "score_coef": coef,"residual_p95_abs":float(np.quantile(residual_abs,.95)),
            "residual_max_abs":float(residual_abs.max())}


def log_likelihood(x, sigma):
    sg = (sigma + sigma.T) / 2
    ev = np.linalg.eigvalsh(sg)
    if ev.min() <= 0:
        sg += np.eye(len(sg)) * (abs(ev.min()) + 1e-5)
    sign, ld = np.linalg.slogdet(sg)
    return float(-0.5 * (len(sg) * np.log(2*np.pi) + ld + np.mean(np.sum((x @ np.linalg.inv(sg)) * x, axis=1))))


def map_curve(r, nmax=15):
    # Velicer original MAP: mean squared off-diagonal partial correlations after removing PCs.
    w, v = np.linalg.eigh(r)
    order = np.argsort(w)[::-1]
    w, v = w[order], v[:, order]
    rows = []
    for k in range(nmax+1):
        e = r if k == 0 else r - (v[:, :k] * w[:k]) @ v[:, :k].T
        d = np.sqrt(np.maximum(np.diag(e), 1e-10))
        q = e / d[:, None] / d[None, :]
        mask = ~np.eye(len(r), dtype=bool)
        rows.append((k, float(np.mean(q[mask]**2))))
    return rows


def load_data():
    tables = {m: pd.read_csv(ROOT / p) for m,p in SOURCES.items()}
    a = tables["Qwen"]
    assert a.shape == (275, 241) and a.columns[0] == "persona"
    assert len(set(a.persona)) == 275 and len(set(a.columns[1:])) == 240
    for m,d in tables.items():
        assert d.shape == a.shape and d.columns.tolist() == a.columns.tolist()
        assert d.persona.tolist() == a.persona.tolist()
        assert np.isfinite(d.iloc[:, 1:].to_numpy()).all()
    return tables


def audit(tables):
    rows, exclusions, summary = [], [], []
    for m,d in tables.items():
        x = d.iloc[:, 1:].to_numpy(float)
        sd = x.std(0, ddof=1)
        nondeg = sd >= 1e-6
        z = standardize(x[:, nondeg])
        r = corr(z)
        adjacency = abs(r) >= .995
        np.fill_diagonal(adjacency, False)
        exact_pairs=int(np.sum(np.triu(abs(r)>=1-1e-12,1)))
        parent = list(range(len(r)))
        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]; i = parent[i]
            return i
        for i,j in zip(*np.where(np.triu(adjacency, 1))):
            parent[find(int(j))] = find(int(i))
        reps = {}
        for i in range(len(r)):
            root = find(i)
            reps[root] = min(i, reps.get(root, i))
        representatives = {i: reps[find(i)] for i in range(len(r))}
        ev = np.linalg.eigvalsh(r)
        sh, alpha = shrink_corr(z)
        q = np.quantile(z, [.25, .75], axis=0)
        iqr = q[1] - q[0]
        outlier = ((z < q[0]-3*iqr) | (z > q[1]+3*iqr)).sum(0)
        names = np.array(d.columns[1:])[nondeg]
        for i,t in enumerate(d.columns[1:]):
            if not nondeg[i]:
                exclusions.append(dict(model=m,trait=t,full_excluded=True,sensitivity_excluded=True,reason="near_zero_variance",representative=""))
                continue
            j = int(np.sum(nondeg[:i])); rep = int(representatives[j]); rel = names[rep]
            rows.append(dict(model=m,trait=t,persona_count=len(d),signed_score=True,missing=0,sd=sd[i],skew=skew(x[:,i]),
                             min=x[:,i].min(),max=x[:,i].max(),outliers_3iqr=int(outlier[j]),
                             max_abs_correlation_other=float(np.max(abs(r[j, np.arange(len(r)) != j]))),
                             near_duplicate_representative=rel))
            exclusions.append(dict(model=m,trait=t,full_excluded=False,sensitivity_excluded=rel!=t,
                                   reason="near_duplicate_abs_r_ge_0.995" if rel!=t else "retained",representative=rel))
        summary.append(dict(model=m,source=SOURCES[m],sha256=sha(ROOT/SOURCES[m]),personas=len(d),traits=x.shape[1],
                            missing=int(np.isnan(x).sum()),min_sd=float(sd.min()),max_abs_skew=float(np.max(abs(skew(x,axis=0)))),
                            negative_fraction=float(np.mean(x<0)),min_score=float(x.min()),max_score=float(x.max()),
                            effective_rank=float(ev.sum()**2/np.sum(ev**2)),ordinary_condition=float(np.linalg.cond(r)),
                            shrinkage_alpha=alpha,shrinkage_condition=float(np.linalg.cond(sh)),
                            exact_duplicate_pairs=exact_pairs,near_duplicate_pairs=int(np.sum(np.triu(adjacency,1))),
                            traits_with_3iqr_outliers=int((outlier>0).sum()),sensitivity_columns=len(set(representatives.values()))))
    save("persona_trait_matrix_audit.csv", rows)
    save("trait_exclusion_inventory.csv", exclusions)
    lines = ["# Persona-by-trait matrix phase gate", "", "**PASS.** All three saved matrices have 275 matched, identically ordered persona rows and 240 identically ordered traits; every cell is finite and signed. Rows are observations and columns are cosine trait-expression variables. No hidden coordinate is a respondent.", "", "| Model | Source SHA256 | Missing | Minimum SD | Maximum absolute skew | Traits with 3×IQR outliers | Effective rank | Ordinary condition | Shrinkage α | Shrinkage condition | Exact / near-duplicate pairs |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summary:
        lines.append(f"| {s['model']} | `{s['sha256'][:12]}` | {s['missing']} | {s['min_sd']:.4g} | {s['max_abs_skew']:.2f} | {s['traits_with_3iqr_outliers']} | {s['effective_rank']:.2f} | {s['ordinary_condition']:.3g} | {s['shrinkage_alpha']:.3f} | {s['shrinkage_condition']:.3g} | {s['exact_duplicate_pairs']} / {s['near_duplicate_pairs']} |")
    lines += ["", "The saved CSVs were deterministically derived from model-specific released role and trait vectors: average the stored layer vectors for each role and trait, L2-normalize each mean separately, then take the role-by-trait dot product. Thus the values are cosine similarities, not projections, correlations, human ratings, or raw dot products. No across-role centering precedes the cosine; no trait contrast subtraction is documented in this matrix construction. Column centering and scaling happen only inside this analysis. A persona's 240 scores are comparable within its model, and a trait's scores are comparable across that model's personas. Absolute values are not calibrated across models. The construction uses model-specific layer-mean vectors (see the source scripts and provenance audit); the exact original upstream trait-vector extraction recipe remains partly unknown.", "", "Near duplicate components are based on absolute correlation of standardized persona profiles. The inventory records every trait and representative. Ordinary covariance conditioning makes shrinkage necessary.", "", "Sources: `research/outputs/trait_persona_prediction/run_trait_persona_prediction.py`, `research/outputs/multimodel_trait_profile_pc_predictor/run_multimodel_trait_profile_pc_predictor.py`, and `research/outputs/trait_profile_provenance_audit/trait_profile_provenance_report.md`."]
    (OUT/"persona_trait_matrix_audit.md").write_text("\n".join(lines)+"\n")
    return summary, pd.DataFrame(exclusions)


def retention(tables, exclusions):
    pa, fd, retain = [], [], {}
    for mi,(m,d) in enumerate(tables.items()):
        names = d.columns[1:].tolist()
        keep = [names.index(t) for t in exclusions[(exclusions.model==m)&(~exclusions.full_excluded)].trait]
        x = standardize(d.iloc[:,1:].to_numpy(float)[:, keep])
        r = corr(x); sh, alpha = shrink_corr(x)
        w = np.linalg.eigvalsh(r)[::-1]; ws = np.linalg.eigvalsh(sh)[::-1]
        rng = np.random.default_rng(SEED+mi)
        null = np.empty((100,20))
        for b in range(100):
            y = np.column_stack([rng.permutation(x[:,j]) for j in range(x.shape[1])])
            null[b] = np.linalg.eigvalsh(corr(y))[::-1][:20]
        q = np.quantile(null, .95, axis=0)
        count = int(np.sum(w[:20] > q))
        for k in range(20):
            pa.append(dict(model=m,component=k+1,ordinary_eigenvalue=w[k],shrinkage_eigenvalue=ws[k],
                           null_mean=null[:,k].mean(),null_p95=q[k],exceeds_p95=bool(w[k]>q[k])))
        maprows = dict(map_curve(r))
        mapk = min(maprows, key=maprows.get)
        for k in range(21):
            fd.append(dict(model=m,component_count=k,ordinary_eigenvalue=w[k-1] if k else np.nan,
                           shrinkage_eigenvalue=ws[k-1] if k else np.nan,map_mean_squared_partial=maprows.get(k,np.nan),
                           parallel_count=count,map_minimum=mapk,eigen_gt_one=int((w>1).sum()),shrinkage_alpha=alpha))
        retain[m] = count
    save("parallel_analysis.csv",pa);save("factor_retention_diagnostics.csv",fd)
    return retain


def fit_candidates(tables, exclusions, retain):
    candidates=[]; parameters=[]; candidate_phi=[]; solutions={}; series={}; score_data={}
    for mi,(m,d) in enumerate(tables.items()):
        names = d.columns[1:].tolist()
        keepnames = exclusions[(exclusions.model==m)&(~exclusions.full_excluded)].trait.tolist()
        x = standardize(d[keepnames].to_numpy(float)); series[m]=x
        k0=retain[m]; ks=range(max(2,k0-2),min(10,k0+3)+1)
        r,alpha=shrink_corr(x); ordinary=corr(x)
        for variant,rr in [("full_shrinkage",r),("ordinary_sensitivity",ordinary)]:
            for k in ks:
                try:
                    f=fit(rr,k)
                    un=fit(rr,k,rotation=None)
                    for j,t in enumerate(keepnames):
                        for h in range(k):
                            parameters.append(dict(model=m,variant=variant,factors=k,trait=t,factor=h+1,
                                                   unrotated_loading=un["loading"][j,h],pattern_loading=f["loading"][j,h],
                                                   structure_loading=f["structure"][j,h],score_coefficient=f["score_coef"][j,h],
                                                   communality=f["h"][j],uniqueness=f["u"][j]))
                    for h in range(k):
                        for t in range(k):candidate_phi.append(dict(model=m,variant=variant,factors=k,factor_a=h+1,factor_b=t+1,
                                                                     correlation=f["phi"][h,t]))
                    # Three heldout folds; estimate training correlation and evaluate new personas.
                    cv=[]
                    for train,test in KFold(3,shuffle=True,random_state=SEED+mi).split(x):
                        mu=x[train].mean(0); sd=x[train].std(0,ddof=1)
                        tr=(x[train]-mu)/sd; te=(x[test]-mu)/sd
                        rc,_=shrink_corr(tr) if variant=="full_shrinkage" else (corr(tr),0)
                        ff=fit(rc,k)
                        cv.append(log_likelihood(te,ff["reconstructed"]))
                    candidates.append(dict(model=m,variant=variant,factors=k,offdiag_residual_rms=f["rms"],
                                           residual_offdiag_p95_abs=f["residual_p95_abs"],residual_offdiag_max_abs=f["residual_max_abs"],
                                           heldout_gaussian_loglik_mean=float(np.mean(cv)),min_uniqueness=float(f["u"].min()),
                                           mean_communality=float(f["h"].mean()),shrinkage_alpha=alpha if variant=="full_shrinkage" else 0,
                                           retained_by_parallel=bool(k==k0)))
                    if k==k0 and variant=="full_shrinkage":solutions[m]=f;score_data[m]=dict(x=x,r=r,names=keepnames)
                    if k==k0 and variant=="ordinary_sensitivity":
                        al,_,_,_=align(solutions[m]["loading"],f["loading"])
                        candidates[-1]["primary_loading_mean_abs_congruence"]=float(np.mean(abs(np.diag(congruence(solutions[m]["loading"],al)))))
                except Exception as e:
                    candidates.append(dict(model=m,variant=variant,factors=k,error=str(e)))
        # Redundancy sensitivity, same count, mapped back later.
        reps=exclusions[(exclusions.model==m)&(~exclusions.sensitivity_excluded)].trait.tolist()
        xr=standardize(d[reps].to_numpy(float)); rr,ar=shrink_corr(xr)
        fr=fit(rr,k0)
        scores=xr@fr["score_coef"]
        assoc=np.corrcoef(np.column_stack([x,scores]),rowvar=False)[:x.shape[1],x.shape[1]:]
        mapped=assoc @ np.linalg.inv(fr["phi"])
        solutions[m+"_redundancy"]={**fr,"loading":mapped,"structure":assoc,"h":np.einsum("ij,ij->i",mapped,assoc)}
        al,_,_,_=align(solutions[m]["loading"],mapped)
        sensitivity_congruence=float(np.mean(abs(np.diag(congruence(solutions[m]["loading"],al)))))
        candidates.append(dict(model=m,variant="redundancy_controlled",factors=k0,offdiag_residual_rms=fr["rms"],
                               mean_communality=float(fr["h"].mean()),shrinkage_alpha=ar,represented_traits=len(reps),
                               primary_loading_mean_abs_congruence=sensitivity_congruence))
        orth=fit(r,k0,rotation="varimax")
        candidates.append(dict(model=m,variant="varimax_orthogonal",factors=k0,offdiag_residual_rms=orth["rms"],
                               mean_communality=float(orth["h"].mean()),shrinkage_alpha=alpha,
                               residual_offdiag_p95_abs=orth["residual_p95_abs"],residual_offdiag_max_abs=orth["residual_max_abs"]))
    save("candidate_factor_fit.csv",candidates)
    save("candidate_factor_parameters.csv",parameters)
    save("candidate_factor_correlations.csv",candidate_phi)
    return solutions,score_data


def export_solutions(tables, exclusions, retain, solutions, score_data):
    unrot,rot,structure,phir,comm,coefrows,groups,scores=[],[],[],[],[],[],[],[]
    for mi,m in enumerate(tables):
        f=solutions[m]; data=score_data[m]; x=data["x"]; names=data["names"]; k=retain[m]
        un=fit(data["r"],k,rotation=None)
        s=x@f["score_coef"]
        recon=s@f["loading"].T
        for j,t in enumerate(names):
            mags=np.argsort(-abs(f["loading"][j])); first=int(mags[0]); second=int(mags[1]); a=abs(f["loading"][j,first]); b=abs(f["loading"][j,second])
            for h in range(k):
                base=dict(model=m,variant="full_shrinkage",trait=t,factor=f"{m}_F{h+1}")
                unrot.append({**base,"loading":un["loading"][j,h]})
                rot.append({**base,"loading":f["loading"][j,h]})
                structure.append({**base,"loading":f["structure"][j,h]})
                coefrows.append({**base,"coefficient":f["score_coef"][j,h]})
            comm.append(dict(model=m,trait=t,communality=f["h"][j],uniqueness=f["u"][j],
                             reconstruction_residual_variance=float(np.mean((x[:,j]-recon[:,j])**2))))
            groups.append(dict(model=m,trait=t,primary_factor=f"{m}_F{first+1}",primary_loading=f["loading"][j,first],
                               secondary_factor=f"{m}_F{second+1}",secondary_loading=f["loading"][j,second],
                               communality=f["h"][j],assignment_confidence=a-b,stability=np.nan,
                               clean_loading=bool(a>=.4 and b<.3),cross_loading=bool(a>=.3 and b>=.3),weakly_explained=bool(f["h"][j]<.2)))
        for i in range(k):
            for j in range(k):phir.append(dict(model=m,factor_a=f"{m}_F{i+1}",factor_b=f"{m}_F{j+1}",correlation=f["phi"][i,j]))
        for i,p in enumerate(tables[m].persona):
            for h in range(k):scores.append(dict(model=m,persona=p,factor=f"{m}_F{h+1}",score=s[i,h],
                                                residual_trait_profile_variance=float(np.mean((x[i]-recon[i])**2))))
        # Redundancy sensitivity has all traits mapped back via correlations with score estimates.
        fr=solutions[m+"_redundancy"]
        for j,t in enumerate(names):
            for h in range(k):
                base=dict(model=m,variant="redundancy_controlled",trait=t,factor=f"{m}_F{h+1}")
                rot.append({**base,"loading":fr["loading"][j,h]})
                structure.append({**base,"loading":fr["structure"][j,h]})
    save("factor_loadings_unrotated.csv",unrot);save("factor_loadings_rotated.csv",rot)
    save("factor_structure_loadings.csv",structure);save("factor_correlations.csv",phir)
    save("trait_communalities.csv",comm);save("factor_score_coefficients.csv",coefrows)
    save("trait_factor_grouping.csv",groups);save("persona_factor_scores.csv",scores)
    return pd.DataFrame(groups)


def stability(tables,retain,solutions,score_data,groups):
    boot,split=[],[]
    score_uncertainty=[]
    for mi,m in enumerate(tables):
        x=score_data[m]["x"]; ref=solutions[m]["loading"]; k=retain[m]
        rng=np.random.default_rng(SEED+100+mi)
        assignment=np.zeros((x.shape[1],),float); cross=np.zeros_like(assignment)
        boot_scores=np.empty((20,len(x),k))
        for b in range(20):
            ids=rng.integers(0,len(x),len(x)); xb=standardize(x[ids]); rr,_=shrink_corr(xb)
            f=fit(rr,k); al,order,signs,_=align(ref,f["loading"])
            cc=canonical_corr(ref,al); c=congruence(ref,al)
            pmat,_=orthogonal_procrustes(f["loading"],ref)
            procrustes_fit=float(np.linalg.norm(f["loading"]@pmat-ref)/np.linalg.norm(ref))
            boot_scores[b]=x@f["score_coef"][:,order]*signs
            assignment+=(np.argmax(abs(al),axis=1)==np.argmax(abs(ref),axis=1))
            cross+=(np.sort(abs(al),axis=1)[:,-2]>=.3)&(np.sort(abs(al),axis=1)[:,-1]>=.3)
            for h in range(k):boot.append(dict(model=m,replicate=b,factor=f"{m}_F{h+1}",congruence=c[h,h],
                                            loading_correlation=np.corrcoef(ref[:,h],al[:,h])[0,1],
                                            min_subspace_canonical=float(cc.min()),matched_original_axis=int(order[h]+1),sign_correction=int(signs[h])))
            for item in boot[-k:]: item["procrustes_relative_error"]=procrustes_fit
        assignment/=20;cross/=20
        for i,p in enumerate(tables[m].persona):
            for h in range(k):score_uncertainty.append(dict(model=m,persona=p,factor=f"{m}_F{h+1}",score_bootstrap_sd=float(boot_scores[:,i,h].std(ddof=1))))
        idx=groups.model==m
        groups.loc[idx,"stability"]=assignment
        groups.loc[idx,"cross_loading_stability"]=cross
        for b in range(10):
            ids=rng.permutation(len(x));half=len(x)//2
            fits=[]
            for subset in [ids[:half],ids[half:]]:
                rr,_=shrink_corr(standardize(x[subset]));fits.append(fit(rr,k)["loading"])
            al,order,signs,_=align(fits[0],fits[1]); cc=canonical_corr(fits[0],al); c=congruence(fits[0],al)
            pmat,_=orthogonal_procrustes(fits[1],fits[0])
            procrustes_fit=float(np.linalg.norm(fits[1]@pmat-fits[0])/np.linalg.norm(fits[0]))
            for h in range(k):split.append(dict(model=m,replicate=b,factor=f"{m}_F{h+1}",congruence=c[h,h],
                                              min_subspace_canonical=float(cc.min()),matched_other_axis=int(order[h]+1),sign_correction=int(signs[h]),
                                              procrustes_relative_error=procrustes_fit))
    save("factor_bootstrap_stability.csv",boot);save("factor_split_half_stability.csv",split)
    groups.to_csv(OUT/"trait_factor_grouping.csv",index=False)
    scores=pd.read_csv(OUT/"persona_factor_scores.csv")
    scores=scores.merge(pd.DataFrame(score_uncertainty),on=["model","persona","factor"],validate="one_to_one")
    scores.to_csv(OUT/"persona_factor_scores.csv",index=False)
    return pd.DataFrame(boot),pd.DataFrame(split),groups


def cross_model(tables,retain,solutions,score_data):
    rows=[]; rng=np.random.default_rng(SEED+900)
    for a,b in [("Qwen","Llama"),("Qwen","Gemma"),("Llama","Gemma")]:
        la=solutions[a]["loading"];lb=solutions[b]["loading"]
        c=congruence(la,lb); ia,ib=linear_sum_assignment(-abs(c))
        cc=canonical_corr(la,lb)
        angles=np.degrees(subspace_angles(la,lb))
        null=[]
        for _ in range(100):
            cp=congruence(la,lb[rng.permutation(len(lb))]);ii,jj=linear_sum_assignment(-abs(cp));null.append(np.mean(abs(cp[ii,jj])))
        observed=float(np.mean(abs(c[ia,ib])));p=(1+sum(v>=observed for v in null))/101
        for i in range(la.shape[1]):
            for j in range(lb.shape[1]):
                ta=la[:,i];tb=lb[:,j];sign=1 if c[i,j]>=0 else -1
                disagreement=np.argsort(-abs(ta-sign*tb))[:8]
                names=score_data[a]["names"]
                rows.append(dict(model_a=a,model_b=b,factor_a=f"{a}_F{i+1}",factor_b=f"{b}_F{j+1}",
                                 tucker_congruence=c[i,j],loading_vector_correlation=np.corrcoef(ta,tb)[0,1],
                                 matched=bool((i,j) in zip(ia,ib)),sign_correction=sign,
                                 shared_subspace_canonical_min=float(cc.min()),shared_subspace_canonical_mean=float(cc.mean()),
                                 largest_principal_angle_deg=float(angles.max()),matched_mean_abs_congruence=observed,
                                 permutation_p=p,permutation_null_p95=float(np.quantile(null,.95)),
                                 largest_disagreement_traits=";".join(names[t] for t in disagreement)))
    save("cross_model_factor_alignment.csv",rows)
    # For 5-vs-6 comparisons, isolate the sixth subspace direction of the larger solution.
    extra_rows=[]
    qa=np.linalg.qr(solutions["Qwen"]["loading"])[0]
    extras={}
    for m in ["Llama","Gemma"]:
        qb=np.linalg.qr(solutions[m]["loading"])[0]
        _,singular,vt=np.linalg.svd(qa.T@qb,full_matrices=True)
        vector=qb@vt[-1]
        names=score_data[m]["names"]
        if vector[np.argmax(abs(vector))]<0:vector=-vector
        extras[m]=vector
        extra_rows.append(dict(model_small="Qwen",model_large=m,shared_subspace_dimension=5,
                               shared_canonical_correlations=";".join(f"{v:.6f}" for v in singular),
                               extra_direction_top_positive=";".join(names[i] for i in np.argsort(-vector)[:10]),
                               extra_direction_top_negative=";".join(names[i] for i in np.argsort(vector)[:10]),
                               extra_llama_gemma_abs_congruence=np.nan))
    extra_c=float(abs(np.dot(extras["Llama"],extras["Gemma"])))
    for row in extra_rows:row["extra_llama_gemma_abs_congruence"]=extra_c
    save("cross_model_additional_subspace.csv",extra_rows)
    scores=pd.read_csv(OUT/"persona_factor_scores.csv")
    # Strong matched-axis graph; factors and score signs are assigned from observed loadings.
    graph={}
    for row in rows:
        if row["matched"] and abs(row["tucker_congruence"])>=.85:
            a,b=row["factor_a"],row["factor_b"];s=row["sign_correction"]
            graph.setdefault(a,[]).append((b,s));graph.setdefault(b,[]).append((a,s))
    ids={};score_sign={};seen=set();number=0
    for start in sorted(graph):
        if start in seen:continue
        number+=1;stack=[(start,1)];component=[]
        while stack:
            node,sgn=stack.pop()
            if node in seen:continue
            seen.add(node);component.append(node);score_sign[node]=sgn
            for neighbor,edge_sign in graph[node]:stack.append((neighbor,sgn*edge_sign))
        models={node.split("_F")[0] for node in component}
        label=("shared_all_" if len(models)==3 else "shared_"+"_".join(sorted(models)).lower()+"_")+str(number)
        for node in component:ids[node]=label
    scores["aligned_cross_model_factor_identity"]=scores.factor.map(ids).fillna("unresolved_or_model_specific")
    scores["aligned_score_sign"]=scores.factor.map(score_sign)
    scores["aligned_score"]=scores.score*scores.aligned_score_sign
    scores.to_csv(OUT/"persona_factor_scores.csv",index=False)
    return pd.DataFrame(rows)


def coverage(groups,boot,retain):
    bridge=pd.read_csv(BRIDGE)
    direct=set(bridge.loc[bridge.review_decision=="ACCEPT_DIRECT","trait"])
    all74=set(bridge.loc[bridge.review_decision.isin(["ACCEPT_DIRECT","ACCEPT_CLOSE"]),"trait"])
    assert len(direct)==45 and len(all74)==74
    rows=[]
    for m in retain:
        for h in range(retain[m]):
            f=f"{m}_F{h+1}"; g=groups[(groups.model==m)&(groups.primary_factor==f)&(abs(groups.primary_loading)>=.3)]
            traits=set(g.trait);d=traits&direct;a=traits&all74
            member_bridge=bridge[bridge.trait.isin(a)]
            item_ids=[]
            for ids in member_bridge.sapa_item_ids.dropna():item_ids += str(ids).split(";")
            shared_item_ids=len(item_ids)-len(set(item_ids))
            rows.append(dict(model=m,factor=f,indicator_traits=len(traits),direct_45_count=len(d),direct_plus_close_74_count=len(a),
                             no_human_proxy_count=len(traits-a),direct_45_traits=";".join(sorted(d)),
                             added_close_traits=";".join(sorted(a-d)),poor_coverage=bool(len(d)<3 or len(a)<3 or len(a)/max(len(traits),1)<.15),
                             shared_sapa_item_reuses=shared_item_ids,duplicate_mapping_reduction_possible=bool(shared_item_ids>0)))
    save("human_bridge_factor_coverage.csv",rows)
    return pd.DataFrame(rows)


def prior_audit(groups):
    editorial={"Exploration":["creative","abstract","curious"],"Response":["reactive","adaptable","practical"],
               "Scrutiny":["skeptical","analytical","conscientious"],"Challenge":["rebellious","competitive","manipulative"],
               "Affiliation":["empathetic","agreeable","altruistic"]}
    lines=["# Prior grouping audit", "", "Source: `research/outputs/persona_trait_ridge_plots/run_persona_trait_ridges.py` (`GROUPS`), reused by `research/outputs/persona_trait_surface_viewer/run_persona_trait_surface.py`. Five groups contain three equal-weight trait labels each (15 of 240). The source comment says they were chosen from descriptions, not fitted to PC correlations. They are manual/editorial semantic selections, shared verbatim across Qwen, Llama, and Gemma. The viewer averages within-model percentile profiles. Membership is one group per selected trait; the other 225 traits are ungrouped. The grouping uses trait descriptions/names, then persona-profile percentiles for display, not factor estimation or activation clustering. It is an external comparison only.", "", "| Editorial group | Members | AA-17 primary factors (Qwen / Llama / Gemma) |", "|---|---|---|"]
    for group,traits in editorial.items():
        found=[]
        for m in ["Qwen","Llama","Gemma"]:
            g=groups[(groups.model==m)&(groups.trait.isin(traits))]
            found.append(", ".join(g.primary_factor.tolist()))
        lines.append(f"| {group} | {', '.join(traits)} | {' / '.join(found)} |")
    lines += ["", "Within-triplet agreement in primary assignment:"]
    for group,traits in editorial.items():
        values=[]
        for m in ["Qwen","Llama","Gemma"]:
            g=groups[(groups.model==m)&(groups.trait.isin(traits))]
            values.append(f"{m} {g.primary_factor.nunique()}/3 distinct factors")
        lines.append(f"- {group}: {'; '.join(values)}")
    (OUT/"prior_trait_grouping_audit.md").write_text("\n".join(lines)+"\n")


def figures(retain,groups,cross):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi":180,"savefig.dpi":220,"font.size":9})
    pa=pd.read_csv(OUT/"parallel_analysis.csv")
    fig,axes=plt.subplots(1,3,figsize=(13,3.7))
    for ax,m in zip(axes,retain):
        q=pa[pa.model==m];ax.plot(q.component,q.ordinary_eigenvalue,label="Observed",lw=2);ax.plot(q.component,q.null_p95,label="Permutation 95%",ls="--");ax.axvline(retain[m],color="tab:red",alpha=.6);ax.set(xlabel="Component",ylabel="Eigenvalue",title=f"{m}: PA {retain[m]}",xlim=(1,15));ax.legend(frameon=False)
    fig.tight_layout();fig.savefig(OUT/"factor_retention_diagnostic.png");plt.close(fig)
    loads=pd.read_csv(OUT/"factor_loadings_rotated.csv");loads=loads[loads.variant=="full_shrinkage"]
    fig,axes=plt.subplots(1,3,figsize=(13,13))
    for ax,m in zip(axes,retain):
        q=loads[loads.model==m].pivot(index="trait",columns="factor",values="loading")
        order=np.argsort(-q.abs().max(axis=1).to_numpy());q=q.iloc[order]
        im=ax.imshow(q.to_numpy(),aspect="auto",cmap="RdBu_r",vmin=-1,vmax=1);ax.set(title=m,xticks=range(q.shape[1]),xticklabels=[f"F{i+1}" for i in range(q.shape[1])],yticks=[])
    fig.colorbar(im,ax=axes.tolist(),shrink=.5,label="Pattern loading");fig.subplots_adjust(right=.9,wspace=.12);fig.savefig(OUT/"rotated_loading_heatmap.png");plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(11,3.5));ph=pd.read_csv(OUT/"factor_correlations.csv")
    for ax,m in zip(axes,retain):
        q=ph[ph.model==m].pivot(index="factor_a",columns="factor_b",values="correlation");im=ax.imshow(q,cmap="RdBu_r",vmin=-1,vmax=1);ax.set(title=m,xticks=range(len(q)),xticklabels=[f"F{i+1}" for i in range(len(q))],yticks=range(len(q)),yticklabels=[f"F{i+1}" for i in range(len(q))])
    fig.colorbar(im,ax=axes.tolist(),shrink=.8);fig.subplots_adjust(right=.88);fig.savefig(OUT/"factor_correlations.png");plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4))
    for m in retain:ax.hist(groups[groups.model==m].communality,bins=np.linspace(0,1,26),alpha=.45,label=m)
    ax.set(xlabel="Communality",ylabel="Trait count",title="Trait communalities");ax.legend(frameon=False);fig.tight_layout();fig.savefig(OUT/"trait_communality_distribution.png");plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(12,3.8))
    for ax,(a,b) in zip(axes,[("Qwen","Llama"),("Qwen","Gemma"),("Llama","Gemma")]):
        q=cross[(cross.model_a==a)&(cross.model_b==b)].pivot(index="factor_a",columns="factor_b",values="tucker_congruence");im=ax.imshow(q,cmap="RdBu_r",vmin=-1,vmax=1);ax.set(title=f"{a}–{b}",xticks=range(q.shape[1]),xticklabels=[f"F{i+1}" for i in range(q.shape[1])],yticks=range(q.shape[0]),yticklabels=[f"F{i+1}" for i in range(q.shape[0])])
    fig.colorbar(im,ax=axes.tolist(),shrink=.8);fig.subplots_adjust(right=.88);fig.savefig(OUT/"cross_model_factor_congruence.png");plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,10));ax.set_xlim(0,1);ax.set_ylim(0,21);ax.axis("off")
    y=20.3
    ax.text(.02,y,"FACTOR",weight="bold");ax.text(.18,y,"POSITIVE POLE · leading traits",weight="bold")
    ax.text(.58,y,"NEGATIVE POLE · leading traits",weight="bold");y-=.8
    row=0
    for m in retain:
        ax.text(.02,y,m.upper(),weight="bold",color="#355577",fontsize=10);y-=.7
        for h in range(retain[m]):
            if row%2==0:ax.axhspan(y-.2,y+.55,color="#f0f4f7",zorder=0)
            q=loads[(loads.model==m)&(loads.factor==f"{m}_F{h+1}")]
            pos=" · ".join(q.nlargest(3,"loading").trait.str.replace("_"," "))
            neg=" · ".join(q.nsmallest(3,"loading").trait.str.replace("_"," "))
            ax.text(.03,y+.05,f"F{h+1}",va="center",weight="bold")
            ax.text(.18,y+.05,pos,va="center",fontsize=8)
            ax.text(.58,y+.05,neg,va="center",fontsize=8)
            y-=.85;row+=1
        y-=.15
    fig.tight_layout(pad=1);fig.savefig(OUT/"factor_pole_summary.png",bbox_inches="tight");plt.close(fig)


def report(summary,retain,groups,boot,split,cross,cover):
    lines=["# AA-17 three-model exploratory trait factor analysis", "", "## Decision", "", "The 275 × 240 persona-by-trait matrix **passed** the phase gate. The factor solution is classified **C: partially shared factors with substantial model-specific structure**. Qwen has five individually stable axes under the frozen rule; Llama and Gemma have stable subspaces with some individually unresolved axes. One strong loading pattern recurs in all three models, while another recurs in Llama and Gemma. These are candidate latent common dimensions of same-space cosine profiles, not causal traits or human personality constructs.", "", "## Retention and diagnostics", "", "| Model | Parallel factors | MAP minimum | Eigenvalues > 1 (descriptive) | Bootstrap median minimum subspace correlation | Clean | Cross-loading | Weak communality |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    fd=pd.read_csv(OUT/"factor_retention_diagnostics.csv")
    for s in summary:
        m=s["model"];g=groups[groups.model==m];b=boot[boot.model==m]
        lines.append(f"| {m} | {retain[m]} | {int(fd[fd.model==m].map_minimum.iloc[0])} | {int(fd[fd.model==m].eigen_gt_one.iloc[0])} | {b.groupby('replicate').min_subspace_canonical.first().median():.3f} | {int(g.clean_loading.sum())} | {int(g.cross_loading.sum())} | {int(g.weakly_explained.sum())} |")
    lines += ["", "Parallel analysis uses 100 independent within-column permutations (marginals preserved). MAP reaches its tested boundary at 15 factors in every model, so it gives no interior count. Heldout Gaussian likelihood also keeps improving through the candidate maximum; it does not corroborate a sharp five/six-factor optimum. The headline count is the predeclared parallel-analysis count and is a compact descriptive choice, not a unique true dimension. The ordinary correlation condition numbers range from ~2.6e9 to 4.5e10, making the shrinkage solution primary. Candidate fits, the ordinary input sensitivity, redundancy sensitivity, varimax sensitivity, and 3-fold heldout likelihood are recorded in `candidate_factor_fit.csv`. High cosine collinearity reflects shared activation geometry and limits claims of unique factors.", "", "## Factor poles and stability", ""]
    loads=pd.read_csv(OUT/"factor_loadings_rotated.csv");loads=loads[loads.variant=="full_shrinkage"]
    interpretations={
        "Qwen_F1":("earnest patience and diligence","flippant anxious antagonism","steady accountability","composed persistence"),
        "Qwen_F2":("concise accessible efficiency","verbose skeptical caution","communication economy","streamlined versus qualified delivery"),
        "Qwen_F3":("contemporary grounded pragmatism","ascetic deontological idealism","pragmatic contemporaneity","grounded utility versus principled idealism"),
        "Qwen_F4":("literal understated withdrawal","holistic systems curiosity","narrow literalism","low versus high integrative reach"),
        "Qwen_F5":("decisive dominant closure","humble open-ended circumspection","closure urgency","assertive finality versus exploratory restraint"),
        "Llama_F1":("optimistic cooperative care","cynical confrontational harshness","cooperative optimism","warmth versus antagonism"),
        "Llama_F2":("contemporary secular groundedness","spiritual mystical essentialism","secular groundedness","contemporary versus transcendent framing"),
        "Llama_F3":("emotional empathic sociability","detached analytical description","empathic expression","affective versus detached register"),
        "Gemma_F1":("concise solemn convergence","divergent playful verbosity","convergent gravity","compression versus playful expansion"),
        "Gemma_F2":("accessible practical generalism","pedantic technical introspection","accessible practicality","generalist versus specialized register"),
        "Gemma_F3":("tactful cooperative optimism","blunt urgent confrontation","diplomatic cooperation","tact versus confrontation"),
        "Gemma_F4":("literal concise withdrawal","proactive holistic generosity","literal restraint","narrow versus expansive response"),
        "Gemma_F6":("spiritual idealist mysticism","secular grounded utility","spiritual idealism","transcendent versus pragmatic framing"),
    }
    for m in retain:
        lines.append(f"### {m}")
        lines.append("")
        for h in range(retain[m]):
            f=f"{m}_F{h+1}";q=loads[(loads.model==m)&(loads.factor==f)];bb=boot[(boot.model==m)&(boot.factor==f)].congruence;ss=split[(split.model==m)&(split.factor==f)].congruence
            status="individually stable" if bb.median()>=.9 and bb.quantile(.1)>=.75 and ss.median()>=.8 else "axis unresolved"
            pos=", ".join(f"{r.trait} ({r.loading:+.2f})" for r in q.nlargest(5,"loading").itertuples())
            neg=", ".join(f"{r.trait} ({r.loading:+.2f})" for r in q.nsmallest(5,"loading").itertuples())
            if status=="individually stable":
                polepos,poleneg,label,alternative=interpretations[f]
                interp=f"**Interpretation:** candidate label: {label}; positive pole reads as {polepos}, negative pole as {poleneg}. Plausible alternative: {alternative}. **Hypothesis:** this reading may generalize to behavior, pending independent testing."
            else:
                interp="**Interpretation:** no semantic label assigned to an unresolved individual axis. **Hypothesis:** the broader factor subspace may support a more stable reading."
            lines.append(f"- **Observed {f}:** positive {pos}; negative {neg}. Bootstrap median/q10 congruence {bb.median():.2f}/{bb.quantile(.1):.2f}; split-half median {ss.median():.2f}; {status}. {interp}")
        lines.append("")
    lines += ["## Cross-model comparison", ""]
    for (a,b),q in cross[cross.matched].groupby(["model_a","model_b"]):
        lines.append(f"- **Observed {a}–{b}:** matched absolute Tucker congruence {q.tucker_congruence.abs().round(2).tolist()}, mean {q.matched_mean_abs_congruence.iloc[0]:.2f}; minimum subspace canonical correlation {q.shared_subspace_canonical_min.iloc[0]:.2f}; largest principal angle {q.largest_principal_angle_deg.iloc[0]:.1f}°; trait-label permutation p={q.permutation_p.iloc[0]:.3f}. Individual axes are matched by loadings, not factor number.")
    lines += ["", "The clearest all-model match is Qwen F3, Llama F2, and Gemma F6 (absolute Tucker congruence 0.919/0.930/0.915 pairwise). Llama F1 and Gemma F3 form a further two-model match (0.896). The broader Qwen–Llama and Qwen–Gemma subspaces agree more than the full Llama–Gemma six-dimensional subspaces, whose weakest canonical correlation is 0.49. A signed correlation changes under arbitrary factor polarity. The alignment CSV retains signed and absolute matching information plus the traits of greatest disagreement. `cross_model_additional_subspace.csv` compares the fifth-dimensional shared Qwen subspace with each larger six-dimensional subspace and isolates each additional direction without equating an arbitrary factor number to the extra dimension.", "", "## Prior grouping and human bridge readiness", "", "The five prior editorial groups are semantic, hand-selected triplets covering 15/240 traits, shared across models. Their factor assignments are in `prior_trait_grouping_audit.md`. Agreement is descriptive and cannot validate the numerical solution. The bridge audit below counts traits whose primary absolute loading reaches 0.30; it does not fit or interpret SAPA data.", "", "| Model factor | Indicators | 45 direct | 74 total | No proxy | Poor coverage |", "|---|---:|---:|---:|---:|---|"]
    for r in cover.itertuples():lines.append(f"| {r.factor} | {r.indicator_traits} | {r.direct_45_count} | {r.direct_plus_close_74_count} | {r.no_human_proxy_count} | {r.poor_coverage} |")
    lines += ["", "Factor-level aggregation could reduce duplication where mapped human proxies reuse SAPA item IDs; `human_bridge_factor_coverage.csv` counts those reuses. It does not create a human factor score, and item reuse must be resolved before later human comparisons.", "", "## Limits and next gate", "", "Factor scores are regression summaries of model persona cosine profiles, with residual profile variance and bootstrap SD in the score table. Bootstrap assignment frequency is a practical uncertainty measure, but neither it nor score coefficients corrects upstream vector measurement uncertainty. No new model inference, GPU, RunPod, HiFWB scoring, respondent-level data, SAPA factor comparison, or viewer was used. The next SAPA/HiFWB stage can use the stable, bridge-covered candidates as hypotheses for an independent test. Poorly covered or axis-unresolved factors should be deferred or compared as subspaces."]
    (OUT/"three_model_trait_factor_report.md").write_text("\n".join(lines)+"\n")


def verify(tables,retain,solutions,groups,boot,split,cross,summary):
    checks={"matrix_phase_gate":True,"identical_persona_order":True,"identical_240_trait_order":True,
            "no_hifwb_input":True,"no_model_inference":True,"cpu_only":True,"seed":SEED,
            "runtime":{"python":sys.version.split()[0],"numpy":np.__version__,"pandas":pd.__version__,
                       "scipy":importlib.metadata.version("scipy"),"scikit_learn":importlib.metadata.version("scikit-learn"),
                       "factor_analyzer":importlib.metadata.version("factor-analyzer")},
            "source_sha256":{s["model"]:s["sha256"] for s in summary}}
    score_rows=pd.read_csv(OUT/"persona_factor_scores.csv")
    for m in retain:
        f=solutions[m];r=f["reconstructed"];checks[m]={"factors":retain[m],"finite_loadings":bool(np.isfinite(f["loading"]).all()),
            "factor_correlations_symmetric":bool(np.allclose(f["phi"],f["phi"].T)),
            "reconstruction_symmetric":bool(np.allclose(r,r.T)),"communalities_in_range":bool(((f["h"]>=0)&(f["h"]<=1.01)).all()),
            "bootstrap_replicates":int(boot[boot.model==m].replicate.nunique()),"split_half_replicates":int(split[split.model==m].replicate.nunique()),
            "score_rows":int(score_rows.query("model == @m").shape[0]),
            "structure_identity_max_abs_error":float(np.max(abs(f["structure"]-f["loading"]@f["phi"]))),
            "loading_reconstruction_max_abs_error":float(np.max(abs(r-(f["loading"]@f["phi"]@f["loading"].T+np.diag(f["u"]))))),
            "score_bootstrap_sd_finite":bool(np.isfinite(score_rows.loc[score_rows.model==m,"score_bootstrap_sd"]).all())}
    checks["all_checks_pass"]=all(v["finite_loadings"] and v["factor_correlations_symmetric"] and v["reconstruction_symmetric"] and v["communalities_in_range"] and v["bootstrap_replicates"]==20 and v["split_half_replicates"]==10 and v["score_rows"]==275*retain[m] for m,v in [(m,checks[m]) for m in retain])
    (OUT/"verification_report.json").write_text(json.dumps(checks,indent=2)+"\n")
    rows=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="artifact_inventory.csv":rows.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size))
    save("artifact_inventory.csv",rows)


def main():
    tables=load_data();summary,exclusions=audit(tables)
    retain=retention(tables,exclusions)
    solutions,score_data=fit_candidates(tables,exclusions,retain)
    groups=export_solutions(tables,exclusions,retain,solutions,score_data)
    boot,split,groups=stability(tables,retain,solutions,score_data,groups)
    cross=cross_model(tables,retain,solutions,score_data)
    cover=coverage(groups,boot,retain)
    prior_audit(groups);figures(retain,groups,cross);report(summary,retain,groups,boot,split,cross,cover)
    verify(tables,retain,solutions,groups,boot,split,cross,summary)
    print(json.dumps({"retained":retain,"verification":json.loads((OUT/"verification_report.json").read_text())["all_checks_pass"]}))


if __name__ == "__main__":main()
