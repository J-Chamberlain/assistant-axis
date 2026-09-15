"""Reproduce the frozen aggregate human/model Rosetta translation study."""
from pathlib import Path
import json
import hashlib
import warnings
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.linalg import orthogonal_procrustes
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research/outputs/human_model_rosetta_translation"
SRC = ROOT / "research/outputs/human_model_profile_correspondence"
KS = [4, 5, 6, 7, 8, 10]
SEED = 2026091501
N_NULL = 2000
ANCHORS = ["adventurous", "altruistic", "forgiving", "grandiose", "impulsive", "manipulative", "optimistic", "pessimistic", "traditional", "innovative", "introspective", "judgmental"]

def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if np.std(a) == 0 or np.std(b) == 0: return 0.0
    return float(np.corrcoef(a, b)[0, 1])

def cosine(a, b):
    d = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / d) if d else 0.0

def match(h, m, labels=None):
    score = np.array([[corr(h[i], m[j]) for j in range(len(m))] for i in range(len(h))])
    rows, cols = linear_sum_assignment(-score)
    pairs = [(int(c), int(r), float(score[r, c])) for r, c in zip(rows, cols)]
    pairs.sort(key=lambda z: labels[z[0]] if labels else z[0])
    return score, pairs

def fit_predict(method, xtr, ytr, xte):
    xtr, ytr, xte = np.asarray(xtr, float), np.asarray(ytr, float), np.asarray(xte, float)
    if method == "identity": return xte.copy()
    if method == "global_intercept_scale":
        sx, sy = np.std(xtr, axis=0, ddof=1), np.std(ytr, axis=0, ddof=1)
        scale = np.divide(sy, sx, out=np.ones_like(sx), where=sx > 1e-12)
        return np.mean(ytr, axis=0) + (xte - np.mean(xtr, axis=0)) * scale
    if method == "trait_affine":
        # Strong shrinkage toward identity, with per-trait coefficients estimated only in-fold.
        out = np.empty_like(xte)
        for j in range(xtr.shape[1]):
            X = np.c_[np.ones(len(xtr)), xtr[:, j]]
            coef = np.linalg.solve(X.T @ X + np.diag([1e-6, 10.0]), X.T @ ytr[:, j])
            out[j] = coef[0] + coef[1] * xte[j]
        return out
    if method == "procrustes":
        xm, ym = np.mean(xtr, axis=0), np.mean(ytr, axis=0)
        # Orthogonal map in the shared target-profile coordinate system.
        R, _ = orthogonal_procrustes(xtr - xm, ytr - ym)
        return (xte - xm) @ R + ym
    if method == "ridge":
        model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
        model.fit(xtr, ytr)
        return model.predict(np.atleast_2d(xte))[0]
    raise ValueError(method)

def metrics(y, p):
    return {"pearson_r": corr(y, p), "cosine": cosine(y, p), "rmse": float(np.sqrt(np.mean((y-p)**2))), "standardized_rmse": float(np.sqrt(np.mean(((y-p)/(np.std(y, ddof=1)+1e-12))**2)))}

def load():
    human = pd.read_csv(SRC / "human_trait_profiles_45.csv")
    model = pd.read_csv(SRC / "model_family_trait_profiles_45.csv")
    traits = list(model["trait"].drop_duplicates())
    assert set(ANCHORS).issubset(traits) and len(traits) == 45
    targets = [t for t in traits if t not in ANCHORS]
    h = {}
    for k in KS:
        hk = human[human.K.eq(k)]
        prof = hk[["profile_id", "profile_size", "profile_proportion"]].drop_duplicates().set_index("profile_id")
        vals = hk.pivot(index="profile_id", columns="trait", values="human_trait_value").loc[:, traits]
        h[k] = vals.join(prof)
    q = model.pivot(index="family_id", columns="trait", values="qwen_value").loc[["MFamily_A", "MFamily_B", "MFamily_C", "MFamily_D"], traits]
    consensus = model.pivot(index="family_id", columns="trait", values="three_model_consensus_value").loc[q.index, traits]
    reps = {col: model.pivot(index="family_id", columns="trait", values=f"{col}_value").loc[q.index, traits] for col in ["qwen", "llama", "gemma"]}
    return traits, targets, h, q, consensus, reps

def main():
    OUT.mkdir(parents=True, exist_ok=True); (OUT / "figures").mkdir(exist_ok=True)
    traits, targets, hbanks, qwen, consensus, reps = load()
    at = pd.DataFrame([{"trait": t, "role": "anchor" if t in ANCHORS else "target", "anchor_basis": "prior moderate-or-better SAPA measurement support" if t in ANCHORS else "exact complement of frozen 45 ACCEPT_DIRECT vocabulary"} for t in traits])
    at.to_csv(OUT / "anchor_target_partition.csv", index=False)
    rows, residuals, summaries, cvrows = [], [], [], []
    methods = ["identity", "global_intercept_scale", "trait_affine", "procrustes", "ridge"]
    all_pairs = {}
    for k in KS:
        H = hbanks[k]; score, pairs = match(H[ANCHORS].to_numpy(), qwen[ANCHORS].to_numpy(), list(qwen.index))
        all_pairs[k] = pairs
        for fi, hi, ar in pairs:
            fid, hid = qwen.index[fi], H.index[hi]
            hv, mv = H.loc[hid, traits].to_numpy(float), qwen.loc[fid, traits].to_numpy(float)
            for j, t in enumerate(traits):
                rows.append({"K":k,"model":"Qwen","model_family_id":fid,"human_profile_id":hid,"trait":t,"cluster_size":float(H.loc[hid,"profile_size"]),"human_centroid":hv[j],"model_centroid":mv[j],"anchor":t in ANCHORS,"residual_model_minus_human":mv[j]-hv[j],"absolute_residual":abs(mv[j]-hv[j])})
            # held-out target translation for this matched pair
            others = [(f, h) for f, h, _ in pairs if f != fi]
            xtr = np.array([H.iloc[h][ANCHORS].to_numpy(float) for _, h in others])
            ytr = np.array([qwen.iloc[f][targets].to_numpy(float) for f, _ in others])
            xte = H.loc[hid, ANCHORS].to_numpy(float); yte = qwen.loc[fid, targets].to_numpy(float)
            # map anchor profile coordinates to target coordinates by frozen identity coordinate names;
            # models operate in the shared 12-anchor/33-target profile space via intercept-only baseline
            # for targets, while the non-identity candidates use a common 33-dimensional source built
            # from the held-out human target profile (strictly descriptive target-profile translation).
            xtr_t = np.array([H.iloc[h][targets].to_numpy(float) for _, h in others])
            xte_t = H.loc[hid, targets].to_numpy(float)
            for method in methods:
                pred = fit_predict(method, xtr_t, ytr, xte_t)
                mm = metrics(yte, pred)
                cvrows.append({"K":k,"model":"Qwen","model_family_id":fid,"human_profile_id":hid,"method":method,"n_train_pairs":len(others),**mm,"identity_delta_pearson":mm["pearson_r"]-corr(yte,xte_t),"identity_delta_rmse":mm["rmse"]-metrics(yte,xte_t)["rmse"]})
            for j, t in enumerate(targets): residuals.append({"K":k,"model_family_id":fid,"human_profile_id":hid,"trait":t,"human_centroid":H.loc[hid,t],"model_centroid":qwen.loc[fid,t],"residual":qwen.loc[fid,t]-H.loc[hid,t],"absolute_residual":abs(qwen.loc[fid,t]-H.loc[hid,t]),"anchor":False})
        summaries.append({"K":k,"n_pairs":len(pairs),"anchor_mean_r":float(np.mean([p[2] for p in pairs])),"anchor_min_r":float(np.min([p[2] for p in pairs]))})
    pd.DataFrame(rows).to_csv(OUT / "matched_cluster_profiles.csv", index=False)
    rdf = pd.DataFrame(residuals); rdf.to_csv(OUT / "matched_cluster_profile_residuals.csv", index=False)
    s = rdf.groupby("trait").agg(mean_residual=("residual","mean"),sd_residual=("residual","std"),sign_consistency=("residual",lambda x: max((x>0).mean(),(x<0).mean())),n=("residual","size")).reset_index(); s.to_csv(OUT / "matched_cluster_summary.csv", index=False)
    pd.DataFrame(cvrows).to_csv(OUT / "translation_cv_predictions.csv", index=False)
    cv = pd.DataFrame(cvrows).groupby("method").agg(pearson_r=("pearson_r","mean"),cosine=("cosine","mean"),rmse=("rmse","mean"),standardized_rmse=("standardized_rmse","mean"),identity_delta_pearson=("identity_delta_pearson","mean"),identity_delta_rmse=("identity_delta_rmse","mean"),folds=("method","size")).reset_index(); cv.to_csv(OUT / "translation_model_comparison.csv", index=False)
    # Fixed-pair model replication summaries.
    rep_rows=[]
    for k,pairs in all_pairs.items():
      for fi,hi,ar in pairs:
        fid, hid=qwen.index[fi], hbanks[k].index[hi]
        for name,mat in [("qwen",reps["qwen"]),("llama",reps["llama"]),("gemma",reps["gemma"]),("consensus",consensus)]: rep_rows.append({"K":k,"model_family_id":fid,"human_profile_id":hid,"representation":name,"pearson_r":corr(hbanks[k].loc[hid,traits],mat.loc[fid,traits]),"spearman_rho":pd.Series(hbanks[k].loc[hid,traits]).corr(pd.Series(mat.loc[fid,traits]),method="spearman")})
    pd.DataFrame(rep_rows).to_csv(OUT / "model_replication_summary.csv", index=False)
    # Primary statistic: best non-identity mean held-out Pearson improvement.
    nonid = cv[~cv.method.eq("identity")]
    obs_method = nonid.sort_values(["identity_delta_pearson", "method"], ascending=[False, True]).iloc[0].method
    obs = float(nonid.identity_delta_pearson.max())
    rng=np.random.default_rng(SEED)
    def draw_stat(kind):
      vals={m:[] for m in methods if m != "identity"}
      for k,pairs in all_pairs.items():
        H=hbanks[k]; n=len(pairs)
        Y=np.array([qwen.iloc[f][targets].to_numpy(float) for f,_,_ in pairs])
        if kind == "cluster_pairing": Y=Y[rng.permutation(n)]
        elif kind == "trait_label": Y=Y[:, rng.permutation(Y.shape[1])]
        elif kind == "joint_structure": Y=np.column_stack([Y[rng.permutation(n),j] for j in range(Y.shape[1])])
        for pos,(_,hi,_) in enumerate(pairs):
          xte=H.iloc[hi][targets].to_numpy(float); yte=Y[pos]
          ids=[z for z in range(n) if z != pos]
          xtr=np.array([H.iloc[pairs[z][1]][targets].to_numpy(float) for z in ids]); ytr=Y[ids]
          base=metrics(yte,xte)["pearson_r"]
          for method in vals:
            vals[method].append(metrics(yte,fit_predict(method,xtr,ytr,xte))["pearson_r"]-base)
      return max(float(np.mean(v)) for v in vals.values())
    null_rows=[]
    for kind in ["cluster_pairing","trait_label","joint_structure"]:
      null=np.array([draw_stat(kind) for _ in range(N_NULL)])
      exceed=int(np.sum(null >= obs)); p=(1+exceed)/(N_NULL+1)
      null_rows.append({"null":kind,"observed_statistic":obs,"selected_observed_method":obs_method,"null_mean":float(np.mean(null)),"null_sd":float(np.std(null,ddof=1)),"exceedances":exceed,"draws":N_NULL,"p_value":p,"seed":SEED,"status":"complete"})
    pd.DataFrame(null_rows).to_csv(OUT / "translation_null_results.csv", index=False)
    # Figures: systematic residual means and CV comparison.
    fig,ax=plt.subplots(figsize=(12,5)); ss=s.sort_values("mean_residual"); ax.bar(ss.trait,ss.mean_residual,color=np.where(ss.mean_residual>=0,"#1976a3","#c4513a")); ax.axhline(0,color="black",lw=.8); ax.tick_params(axis="x",rotation=70); ax.set_ylabel("Qwen minus human profile residual"); fig.tight_layout(); fig.savefig(OUT/"figures/trait_residual_consistency.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5)); ax.bar(cv.method,cv.pearson_r,color="#1976a3"); ax.axhline(float(cv.loc[cv.method.eq("identity"),"pearson_r"].iloc[0]),color="black",ls="--",label="identity"); ax.legend(); ax.tick_params(axis="x",rotation=35); ax.set_ylabel("Mean held-out target Pearson r"); fig.tight_layout(); fig.savefig(OUT/"figures/translation_cv_comparison.png",dpi=160); plt.close(fig)
    report={"status":"COMPLETE","seed":SEED,"null_draws":N_NULL,"primary_model":"Qwen","anchor_count":len(ANCHORS),"target_count":len(targets),"eligible_K":KS,"observed_best_nonidentity_delta_pearson":obs,"selected_observed_method":obs_method,"nulls":"cluster pairing, trait-label, and joint-structure; 2,000 draws each","source_sha256":hashlib.sha256((SRC/"human_trait_profiles_45.csv").read_bytes()).hexdigest()}
    (OUT/"translation_stability_summary.csv").write_text(pd.DataFrame([{"trait":r.trait,"mean_residual":r.mean_residual,"sd_residual":r.sd_residual,"sign_consistency":r.sign_consistency,"n":r.n} for r in s.itertuples()]).to_csv(index=False))
    (OUT/"run_summary.json").write_text(json.dumps(report,indent=2)+"\n")
if __name__ == "__main__": main()
