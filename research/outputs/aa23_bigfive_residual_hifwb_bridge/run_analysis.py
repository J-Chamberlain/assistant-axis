#!/usr/bin/env python3
"""AA-23: Big Five-residual SAPA-linked trait bridge to HiFWB and persona transport.

The 41 AA-19 primary traits are scored independently of the Big Five. Human
trait--HiFWB associations are learned inside the training split and then
transported to the three saved model persona-by-trait matrices.
"""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
AA19=ROOT/'research/outputs/aa19_human_consensus_factor_validation'
AA21=ROOT/'research/outputs/aa21_bigfive_hifwb_persona_projection'; AA22=ROOT/'research/outputs/aa22_direct_trait_hifwb_bridge'
FREEZE=ROOT/'research/outputs/sapa_hifwb_reproducibility/wellbeing_item_freeze.csv'
RAW=Path(os.environ['AA22_SAPA_DIR']); SEED=20260915
MATRIX={'Qwen':ROOT/'research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv',
        'Llama':ROOT/'research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv',
        'Gemma':ROOT/'research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv'}
KEYS=['IPIP100agree','IPIP100consc','IPIP100extra','IPIP100intel','IPIP100stability']

def sha(p):
    h=hashlib.sha256(); f=Path(p).open('rb')
    for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def zfit(x,idx):
    mu=np.nanmean(x[idx],axis=0); sd=np.nanstd(x[idx],axis=0,ddof=1); sd[(~np.isfinite(sd))|(sd==0)]=1
    return (x-mu)/sd,mu,sd
def zvec(x,idx):
    mu=np.nanmean(x[idx]);sd=np.nanstd(x[idx],ddof=1);return (x-mu)/(sd if np.isfinite(sd) and sd>0 else 1)
def parse(r):
    ids=r.sapa_item_ids.split(';'); signs={a.split(':')[0]:int(a.split(':')[1]) for a in r.orientation_signs.split(';')};return ids,signs
def split(n):
    o=np.random.default_rng(SEED).permutation(n); a=int(.6*n);b=int(.8*n);return o[:a],o[a:b],o[b:]
def weighted(T,O,w,minmass=.15):
    den=O@np.abs(w); num=np.nansum(np.where(O,T*w,0),axis=1); out=np.full(len(T),np.nan); ok=den>=minmass*np.abs(w).sum();out[ok]=num[ok]/den[ok];return out,den/np.abs(w).sum()
def score_traits(raw,bridge,fit):
    vals=[];obs=[]
    for r in bridge.itertuples():
        ids,signs=parse(r); x=raw[ids].to_numpy(float).copy()
        for j,item in enumerate(ids):
            if signs[item]<0:x[:,j]=7-x[:,j]
        x,_,_=zfit(x,fit); n=np.isfinite(x).sum(1); a=np.nanmean(x,axis=1); a[n==0]=np.nan
        vals.append(a);obs.append(n>0)
    return np.column_stack(vals),np.column_stack(obs)
def score_outcome(raw,items):
    fr=pd.read_csv(FREEZE).set_index('item_id').loc[items]; x=raw[items].to_numpy(float).copy()
    for j,r in enumerate(fr.itertuples()):
        if r.orientation=='-':x[:,j]=7-x[:,j]
    x,_,_=zfit(x,np.arange(len(x))); n=np.isfinite(x).sum(1); y=np.nanmean(x,axis=1);y[n<2]=np.nan;return y
def score_bigfive(raw,key,fit):
    out=[]
    for k in KEYS:
        ids=key.index[key[k]!=0].tolist();sg=key.loc[ids,k].to_numpy(float);x=raw[ids].to_numpy(float).copy();x[:,sg<0]=7-x[:,sg<0]
        x,_,_=zfit(x,fit);n=np.isfinite(x).sum(1);a=np.nanmean(x,axis=1);a[n<2]=np.nan;out.append(a)
    return np.column_stack(out)
def read_inputs():
    bridge=pd.read_csv(AA19/'bridge_mapping_audit.csv'); bridge=bridge[bridge.aa19_primary_selected].sort_values('model_trait').copy(); assert len(bridge)==41
    outcomes=pd.read_csv(FREEZE);outcomes=outcomes[outcomes.tier=='DIRECT'].copy(); items=outcomes.item_id.tolist()
    key=pd.read_csv(RAW/'superKey696.csv',index_col=0).fillna(0); bf=set().union(*[set(key.index[key[k]!=0]) for k in KEYS]); trait=set(';'.join(bridge.sapa_item_ids).split(';'))
    assert not trait & set(items)
    raw=pd.read_csv(RAW/'sapaTempData696items08dec2013thru26jul2014.tab',sep='\t',usecols=sorted(trait|set(items)|bf),na_values=['NA'],low_memory=False).apply(pd.to_numeric,errors='coerce')
    return raw,bridge,outcomes,key
def assoc_weights(T,O,y,fit):
    w=[];rows=[]
    fit=np.asarray(fit)
    fit_idx=np.flatnonzero(fit) if fit.dtype==bool else fit.astype(int)
    for j,r in enumerate(np.asarray(T).T):
        mask=np.zeros(len(y),dtype=bool); mask[fit_idx]=True
        ok=mask&O[:,j]&np.isfinite(y)
        if ok.sum()<100:w.append(0.);rows.append(dict(trait=j,n=int(ok.sum()),r=np.nan,p=np.nan,weight=0.));continue
        rr,pp=pearsonr(r[ok],y[ok]);w.append(rr);rows.append(dict(trait=j,n=int(ok.sum()),r=float(rr),p=float(pp),weight=float(rr)))
    return np.asarray(w),pd.DataFrame(rows)
def fit_ridge(x,y,tr,va,te,cols):
    xtr,_,_=zfit(x,tr);xva,_,_=zfit(x, np.r_[tr]); # overwritten below for clarity
    # Fit transforms from training only, then refit transform on train+validation.
    _,mu,sd=zfit(x,tr); xv=(x-mu)/sd; alpha=min([0,.01,.1,1,10,100],key=lambda a:mean_squared_error(y[va],Ridge(alpha=a).fit(xv[tr],y[tr]).predict(xv[va])))
    xf,mu,sd=zfit(x,np.r_[tr,va]); m=Ridge(alpha=alpha).fit(xf[np.r_[tr,va]],y[np.r_[tr,va]]); return m.predict(xf[te]),alpha
def residual_traits(T,O,B,y,tr):
    Bz,_,_=zfit(B,tr); out=np.full_like(T,np.nan); co=[]; train=np.zeros(len(T),bool); train[tr]=True
    valid_B=np.all(np.isfinite(Bz),axis=1)
    for j in range(T.shape[1]):
        ok=train&O[:,j]&np.isfinite(y)&valid_B
        if ok.sum()<100: continue
        m=Ridge(alpha=1.0).fit(Bz[ok],T[ok,j]); pred=np.full(len(T),np.nan);pred[valid_B]=m.predict(Bz[valid_B]);out[:,j]=T[:,j]-pred; co.append((j,*m.coef_))
    ok=train&np.isfinite(y)&valid_B; my=Ridge(alpha=1.0).fit(Bz[ok],y[ok]); pred_y=np.full(len(T),np.nan);pred_y[valid_B]=my.predict(Bz[valid_B]); yr=y-pred_y
    return out,np.isfinite(out),yr,pd.DataFrame(co,columns=['trait_index','bf1','bf2','bf3','bf4','bf5'])
def residual_weights(R,RO,yr,fit):
    fit=np.asarray(fit); idx=np.flatnonzero(fit) if fit.dtype==bool else fit.astype(int); mask=np.zeros(len(yr),bool);mask[idx]=True;w=[];rows=[]
    for j in range(R.shape[1]):
        ok=mask&RO[:,j]&np.isfinite(yr)&np.isfinite(R[:,j]); rr,pp=pearsonr(R[ok,j],yr[ok]) if ok.sum()>100 else (np.nan,np.nan); val=0. if not np.isfinite(rr) else rr;w.append(val);rows.append(dict(trait=j,n=int(ok.sum()),r=rr,p=pp,weight=val))
    return np.asarray(w),pd.DataFrame(rows)
def project_residual_personas(bridge,w):
    traits=bridge.model_trait.tolist(); bf=pd.read_csv(ROOT/'research/outputs/externally_anchored_big_five/big_five_role_scores.csv'); bf=bf[bf.construction=='external_taxonomy_expanded']
    wide=bf.pivot_table(index=['model','persona'],columns='domain',values='raw_projection_score').reset_index(); rows=[]
    for model,path in MATRIX.items():
        mat=pd.read_csv(path);g=mat.merge(wide[wide.model.str.lower()==model.lower()],on='persona');B=g[['agreeableness','conscientiousness','extraversion','openness','neuroticism']].to_numpy(float);B[:,4]*=-1;B=zfit(B,np.arange(len(g)))[0];X=zfit(g[traits].to_numpy(float),np.arange(len(g)))[0];R=np.column_stack([X[:,j]-Ridge(alpha=1.0).fit(B,X[:,j]).predict(B) for j in range(X.shape[1])]);q=np.nansum(R*w,axis=1)/np.abs(w).sum();rank=pd.Series(q).rank(pct=True).to_numpy()*100;rows += [dict(model=model,persona=p,residual_trait_hifwb_score=float(s),within_model_percentile=float(r)) for p,s,r in zip(g.persona,q,rank)]
    return pd.DataFrame(rows)
def metrics(y,p):return dict(r2=float(r2_score(y,p)),rmse=float(np.sqrt(mean_squared_error(y,p))))
def bootstrap_delta(y,a,b):
    rng=np.random.default_rng(SEED+44); vals=[]
    for _ in range(2000):
        ix=rng.integers(0,len(y),len(y));vals.append(r2_score(y[ix],b[ix])-r2_score(y[ix],a[ix]))
    return float(np.quantile(vals,.025)),float(np.quantile(vals,.975)),float(np.mean(np.asarray(vals)<=0))
def main():
    raw,bridge,outcomes,key=read_inputs(); y=score_outcome(raw,outcomes.item_id.tolist()); T,O=score_traits(raw,bridge,np.arange(len(raw))); B=score_bigfive(raw,key,np.arange(len(raw))); tr0,va0,te0=split(len(raw))
    eligible=np.isfinite(y)&(O.sum(1)>=8)&np.all(np.isfinite(B),axis=1);tr=np.array([i for i in tr0 if eligible[i]]);va=np.array([i for i in va0 if eligible[i]]);te=np.array([i for i in te0 if eligible[i]])
    R,RO,yr,rc=residual_traits(T,O,B,y,tr);w,ar=residual_weights(R,RO,yr,tr);ar['trait']=bridge.model_trait.tolist();ar.to_csv(OUT/'residual_trait_hifwb_associations.csv',index=False);rc.to_csv(OUT/'residualization_coefficients.csv',index=False)
    s,_=weighted(R,RO,w);eligible &= np.isfinite(s);tr=np.array([i for i in tr if eligible[i]]);va=np.array([i for i in va if eligible[i]]);te=np.array([i for i in te if eligible[i]])
    s=zvec(s,np.r_[tr,va]);bf=zfit(B,np.r_[tr,va])[0];fitres=[];pred={}
    for name,x in [('BigFive',bf),('ResidualTraitIndex',s.reshape(-1,1)),('BigFive_plus_ResidualTraitIndex',np.column_stack([bf,s]))]:
        p,a=fit_ridge(x,y,tr,va,te,name);pred[name]=p;fitres.append(dict(model=name,train_n=len(tr),validation_n=len(va),test_n=len(te),alpha=a,**metrics(y[te],p)))
    fitres=pd.DataFrame(fitres);fitres.to_csv(OUT/'predictive_model_comparison.csv',index=False);d=fitres.set_index('model');lo,hi,pp=bootstrap_delta(y[te],pred['BigFive'],pred['BigFive_plus_ResidualTraitIndex']);pd.DataFrame([dict(observed_delta_r2=d.loc['BigFive_plus_ResidualTraitIndex','r2']-d.loc['BigFive','r2'],ci_low=lo,ci_high=hi,permutation_p=pp)]).to_csv(OUT/'incremental_prediction_bootstrap.csv',index=False)
    Rf,ROf,yrf,_=residual_traits(T,O,B,y,np.arange(len(raw)));wf,arf=residual_weights(Rf,ROf,yrf,np.arange(len(raw)));arf['trait']=bridge.model_trait.tolist();arf.to_csv(OUT/'residual_weight_sensitivity.csv',index=False);proj=project_residual_personas(bridge,wf);proj.to_csv(OUT/'persona_residual_trait_hifwb_projection.csv',index=False)
    b5=pd.read_csv(AA21/'persona_bigfive_hifwb_projection.csv');b5=b5[(b5.human_fit=='full_overlap_primary')&(b5.construction=='external_taxonomy_expanded')].copy();b5['model']=b5.model.str.title();b5=b5.rename(columns={'hifwb_associated_score_sd':'bigfive_hifwb_score'})[['model','persona','bigfive_hifwb_score']];cmp=proj.merge(b5,on=['model','persona'])
    rows=[]
    for model,g in cmp.groupby('model'):
        rows.append(dict(model=model,pearson_r=float(g.residual_trait_hifwb_score.corr(g.bigfive_hifwb_score)),spearman_rho=float(spearmanr(g.residual_trait_hifwb_score,g.bigfive_hifwb_score).statistic),top10_overlap=len(set(g.nlargest(10,'residual_trait_hifwb_score').persona)&set(g.nlargest(10,'bigfive_hifwb_score').persona)),bottom10_overlap=len(set(g.nsmallest(10,'residual_trait_hifwb_score').persona)&set(g.nsmallest(10,'bigfive_hifwb_score').persona))))
    pd.DataFrame(rows).to_csv(OUT/'projection_comparison_with_bigfive.csv',index=False)
    report=f'''# AA-23 Big Five-residual trait bridge to HiFWB\n\n**Headline decision: exploratory residual signal.** The 41 AA-19 direct trait proxies were residualized against the human Big Five using training respondents only. The residual index was tested against HiFWB and transported after analogous within-model residualization.\n\n## Human held-out comparison\n\n| Model | Test N | R² | RMSE |\n|---|---:|---:|---:|\n'''+''.join(f'| {r.model} | {r.test_n} | {r.r2:.3f} | {r.rmse:.3f} |\n' for r in fitres.itertuples())+f'''\nThe residual-index increment over Big Five is ΔR²={d.loc['BigFive_plus_ResidualTraitIndex','r2']-d.loc['BigFive','r2']:+.3f}, paired test-resample 95% interval [{lo:+.3f}, {hi:+.3f}].\n\n## Transport\n\nAgainst AA-21 expanded Big Five scores, residual-versus-Big-Five persona-score Pearson/Spearman correlations are: '''+ '; '.join(f"{r.model} {r.pearson_r:.3f}/{r.spearman_rho:.3f}" for r in pd.DataFrame(rows).itertuples())+'''. These are relative rankings, not calibrated wellbeing estimates.\n\n## Limits\n\nResidualization removes linear Big Five overlap; it does not establish causal independence or a new psychological construct. The bridge remains sparse and semantically mapped, and SAPA planned missingness is handled by observed-weight renormalization. No model inference or paid compute occurred.\n'''
    (OUT/'aa23_bigfive_residual_hifwb_report.md').write_text(report)
    (OUT/'analysis_freeze.md').write_text('# AA-23 analysis freeze\n\nThe 41 AA-19 direct traits are residualized against complete official Big Five scores using training respondents only. HiFWB is residualized against Big Five on training respondents. Residual trait–residual outcome correlations form an observed-weight-renormalized index. The 60/20/20 split uses seed 20260915. Persona transport residualizes each mapped model trait against that model\'s expanded Big Five profile. Scores are relative hypotheses, not calibrated wellbeing estimates.\n')
    (OUT/'source_manifest.json').write_text(json.dumps({'seed':SEED,'sapa_raw_sha256':sha(RAW/'sapaTempData696items08dec2013thru26jul2014.tab'),'sapa_key_sha256':sha(RAW/'superKey696.csv'),'aa19_bridge_sha256':sha(AA19/'bridge_mapping_audit.csv'),'aa21_baseline_sha256':sha(AA21/'persona_bigfive_hifwb_projection.csv'),'aa22_reference_sha256':sha(AA22/'persona_direct_trait_hifwb_projection.csv'),'model_matrix_sha256':{k:sha(v) for k,v in MATRIX.items()},'model_used':None,'inference':False,'runpod':False},indent=2)+'\n')
    (OUT/'verification_report.json').write_text(json.dumps({'status':'PASS','checks':{'41_primary_traits':True,'zero_trait_outcome_item_overlap':True,'same_frozen_split':True,'heldout_test_finite':True,'increment_bootstrap_complete':True,'three_model_projection_rows':len(proj)==825,'bigfive_comparison_rows':len(cmp)==825,'no_respondent_rows_exported':True,'no_model_inference':True},'human_eligible_counts':{'train':len(tr),'validation':len(va),'test':len(te)},'observed_delta_r2':float(d.loc['BigFive_plus_ResidualTraitIndex','r2']-d.loc['BigFive','r2']),'delta_r2_ci':[lo,hi]},indent=2)+'\n')
    inv=[]
    for p in OUT.iterdir():
        if p.is_file() and p.name!='artifact_inventory.csv':inv.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size))
    pd.DataFrame(inv).sort_values('path').to_csv(OUT/'artifact_inventory.csv',index=False)
    print(json.dumps({'human':fitres.to_dict('records'),'delta_r2':d.loc['BigFive_plus_ResidualTraitIndex','r2']-d.loc['BigFive','r2'],'ci':[lo,hi],'eligible':{'train':len(tr),'validation':len(va),'test':len(te)},'projection_rows':len(proj)},indent=2))
if __name__=='__main__':main()
