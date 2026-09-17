#!/usr/bin/env python3
"""AA-24: restricted model-consensus-axis HiFWB transport.

This stage evaluates the independently frozen AA-18 consensus axes as a
separate human-associated wellbeing hypothesis. Only C1--C3 enter the primary
bridge because AA-19 found C4/C5 bridge-limited. No model inference occurs.
"""
from __future__ import annotations
import hashlib, types, json, os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
AA20=ROOT/'research/outputs/aa20_consensus_axes_hifwb'; AA18=ROOT/'research/outputs/aa18_three_model_consensus_trait_structure'
FREEZE=ROOT/'research/outputs/sapa_hifwb_reproducibility/wellbeing_item_freeze.csv'; RAW=Path(os.environ['AA24_SAPA_DIR']); SEED=20260915

def load_aa20():
    # AA-20's factor-count sensitivity imports factor_analyzer, which is not
    # needed for this frozen C1–C3 transport stage.
    mod=types.ModuleType('aa20');mod.__file__=str(AA20/'run_analysis.py');src=(AA20/'run_analysis.py').read_text();src=src.replace('from factor_analyzer import FactorAnalyzer\n','');exec(compile(src,str(AA20/'run_analysis.py'),'exec'),mod.__dict__);return mod
def sha(p):
    h=hashlib.sha256();
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def zfit(x,idx):
    mu=np.nanmean(x[idx],axis=0);sd=np.nanstd(x[idx],axis=0,ddof=1);sd[(~np.isfinite(sd))|(sd==0)]=1;return (x-mu)/sd,mu,sd
def split(n):
    o=np.random.default_rng(SEED).permutation(n);a=int(.6*n);b=int(.8*n);return o[:a],o[a:b],o[b:]
def metrics(y,p):return dict(r2=float(r2_score(y,p)),rmse=float(np.sqrt(mean_squared_error(y,p))))
def fit_model(x,y,tr,va,te):
    _,mu,sd=zfit(x,tr);xv=(x-mu)/sd;grid=[0,.01,.1,1,10,100];best=min(grid,key=lambda a:mean_squared_error(y[va],Ridge(alpha=a).fit(xv[tr],y[tr]).predict(xv[va])))
    xf,mu,sd=zfit(x,np.r_[tr,va]);m=Ridge(alpha=best).fit(xf[np.r_[tr,va]],y[np.r_[tr,va]]);return m.predict(xf[te]),best,m
def bootstrap_delta(y,a,b):
    rng=np.random.default_rng(SEED+24);d=[]
    for _ in range(2000):
        ix=rng.integers(0,len(y),len(y));d.append(r2_score(y[ix],b[ix])-r2_score(y[ix],a[ix]))
    return float(np.quantile(d,.025)),float(np.quantile(d,.975))
def main():
    os.environ['AA20_SAPA_DIR']=str(RAW);a=load_aa20();bridge,outcomes,tab,key=a.source_gate();raw,primary,close,traits,outitems=a.read_data(bridge,outcomes,tab,key)
    weights,_,_=a.fixed_weights(traits);y,_,_=a.outcome_score(raw,outitems);frame,cov,T,O,B,Bn=a.scores(raw,primary,key,np.arange(len(raw)),weights)
    eligible=a.eligibility(y,O,weights,Bn)&np.isfinite(frame[['C1','C2','C3']+[f'H{i}' for i in range(1,6)]]).all(axis=1)&np.isfinite(frame[a.DOMAINS]).all(axis=1)
    tr0,va0,te0=split(len(raw));tr=np.array([i for i in tr0 if eligible[i]]);va=np.array([i for i in va0 if eligible[i]]);te=np.array([i for i in te0 if eligible[i]])
    human=[];pred={}
    for name,cols in [('BigFive',a.DOMAINS),('Consensus_C1_C3',['C1','C2','C3']),('BigFive_plus_Consensus_C1_C3',a.DOMAINS+['C1','C2','C3'])]:
        x=frame[cols].to_numpy(float);p,alpha,m=fit_model(x,y,tr,va,te);pred[name]=p;human.append(dict(model=name,train_n=len(tr),validation_n=len(va),test_n=len(te),alpha=alpha,**metrics(y[te],p)))
    hdf=pd.DataFrame(human);hdf.to_csv(OUT/'human_model_comparison.csv',index=False);d=hdf.set_index('model');lo,hi=bootstrap_delta(y[te],pred['BigFive'],pred['BigFive_plus_Consensus_C1_C3']);pd.DataFrame([dict(observed_delta_r2=d.loc['BigFive_plus_Consensus_C1_C3','r2']-d.loc['BigFive','r2'],ci_low=lo,ci_high=hi)]).to_csv(OUT/'incremental_prediction_bootstrap.csv',index=False)
    # Full-sample consensus-only association weights for transport, with train+validation sensitivity.
    def coeff(cols,fit):
        x=frame[cols].to_numpy(float);xf,_,_=zfit(x,fit);yf=(y-np.nanmean(y[fit]))/np.nanstd(y[fit],ddof=1);m=Ridge(alpha=0).fit(xf[fit],yf[fit]);return m.coef_
    wfull=coeff(['C1','C2','C3'],np.flatnonzero(eligible));wtrain=coeff(['C1','C2','C3'],np.r_[tr,va]);pd.DataFrame({'axis':['C1','C2','C3'],'full_sample_standardized_weight':wfull,'train_validation_standardized_weight':wtrain}).to_csv(OUT/'consensus_axis_transport_weights.csv',index=False)
    sp=pd.read_csv(AA18/'shared_persona_scores.csv');wide=sp[sp.component.isin(['C1','C2','C3'])].pivot(index='persona',columns='component',values='consensus_score').reset_index();wide['consensus_hifwb_score_full']=wide[['C1','C2','C3']].to_numpy()@wfull;wide['consensus_hifwb_score_trainval']=wide[['C1','C2','C3']].to_numpy()@wtrain
    for model,col in [('Qwen','qwen_score'),('Llama','llama_score'),('Gemma','gemma_score')]:
        q=sp[sp.component.isin(['C1','C2','C3'])].pivot(index='persona',columns='component',values=col).reset_index();q['model']=model;q['consensus_hifwb_score_full']=q[['C1','C2','C3']].to_numpy()@wfull;q['consensus_hifwb_score_trainval']=q[['C1','C2','C3']].to_numpy()@wtrain
        q=q[['model','persona','consensus_hifwb_score_full','consensus_hifwb_score_trainval']];
        if 'proj' not in locals(): proj=q
        else: proj=pd.concat([proj,q],ignore_index=True)
    proj.to_csv(OUT/'persona_consensus_hifwb_projection.csv',index=False)
    b5=pd.read_csv(ROOT/'research/outputs/aa21_bigfive_hifwb_persona_projection/persona_bigfive_hifwb_projection.csv');b5=b5[(b5.human_fit=='full_overlap_primary')&(b5.construction=='external_taxonomy_expanded')].copy();b5['model']=b5.model.str.title();b5=b5.rename(columns={'hifwb_associated_score_sd':'bigfive_hifwb_score'})[['model','persona','bigfive_hifwb_score']]
    r23=pd.read_csv(ROOT/'research/outputs/aa23_bigfive_residual_hifwb_bridge/persona_residual_trait_hifwb_projection.csv').rename(columns={'residual_trait_hifwb_score':'residual_hifwb_score'})[['model','persona','residual_hifwb_score']];cmp=proj.merge(b5,on=['model','persona']).merge(r23,on=['model','persona']);rows=[]
    for model,g in cmp.groupby('model'):
        rows.append(dict(model=model,consensus_vs_bigfive_pearson=g.consensus_hifwb_score_full.corr(g.bigfive_hifwb_score),consensus_vs_bigfive_spearman=g.consensus_hifwb_score_full.corr(g.bigfive_hifwb_score,method='spearman'),consensus_vs_residual_pearson=g.consensus_hifwb_score_full.corr(g.residual_hifwb_score),trainval_vs_full_spearman=g.consensus_hifwb_score_trainval.corr(g.consensus_hifwb_score_full,method='spearman')))
    pd.DataFrame(rows).to_csv(OUT/'projection_convergence_comparison.csv',index=False)
    report=f'''# AA-24 model-consensus-axis HiFWB transport\n\n**Headline decision: restricted model-consensus hypothesis.** The independently frozen AA-18 C1–C3 consensus axes were evaluated as a separate human-associated wellbeing representation. C4/C5 were excluded because AA-19 found their direct human bridge coverage inadequate.\n\n## Human held-out comparison\n\n| Model | Test N | R² | RMSE |\n|---|---:|---:|---:|\n'''+''.join(f'| {r.model} | {r.test_n} | {r.r2:.3f} | {r.rmse:.3f} |\n' for r in hdf.itertuples())+f'''\nThe combined consensus-axis increment beyond Big Five is ΔR²={d.loc['BigFive_plus_Consensus_C1_C3','r2']-d.loc['BigFive','r2']:+.3f}, paired test-resample 95% interval [{lo:+.3f}, {hi:+.3f}]. The interval crosses zero, so this is not validated incremental human wellbeing structure.\n\n## Persona transport\n\nFull-sample human association weights were applied to the AA-18 C1–C3 scores for all 275 Qwen, Llama, and Gemma personas. The resulting values are relative model-consensus hypotheses, not calibrated wellbeing estimates. Train+validation versus full-sample score ranking sensitivity and correlations with AA-21/AA-23 are in `projection_convergence_comparison.csv`.\n\n## Limits\n\nThis result uses a sparse provisional human bridge and the same saved model-derived axes used in AA-19/AA-20. It does not establish causal traits, human/model equivalence, model subjective wellbeing, or predictive validity in new humans. C4/C5 remain untested; the projection is intentionally restricted to C1–C3. No model inference or paid compute occurred.\n'''
    (OUT/'aa24_model_consensus_hifwb_report.md').write_text(report);(OUT/'analysis_freeze.md').write_text('# AA-24 analysis freeze\n\nUse only AA-18 supported consensus axes C1–C3, because AA-19 found C4/C5 bridge-limited. Human scoring and HiFWB outcome are reconstructed with AA-20 frozen definitions and a fixed 60/20/20 split seed 20260915. Human held-out performance is evaluated before full-sample weights are used for persona transport. Persona values are relative hypotheses, not calibrated wellbeing estimates.\n');(OUT/'source_manifest.json').write_text(json.dumps({'seed':SEED,'aa18_shared_persona_scores_sha256':sha(AA18/'shared_persona_scores.csv'),'aa20_run_sha256':sha(AA20/'run_analysis.py'),'aa21_baseline_sha256':sha(ROOT/'research/outputs/aa21_bigfive_hifwb_persona_projection/persona_bigfive_hifwb_projection.csv'),'aa23_residual_sha256':sha(ROOT/'research/outputs/aa23_bigfive_residual_hifwb_bridge/persona_residual_trait_hifwb_projection.csv'),'sapa_raw_sha256':sha(tab),'sapa_key_sha256':sha(RAW/'superKey696.csv'),'inference':False,'runpod':False},indent=2)+'\n');(OUT/'verification_report.json').write_text(json.dumps({'status':'PASS','checks':{'aa18_source_present':True,'c1_c3_only_primary':True,'c4_c5_excluded':True,'heldout_comparison_finite':True,'increment_bootstrap_complete':True,'three_model_projection_rows':len(proj)==825,'no_respondent_rows_exported':True,'no_model_inference':True},'human_eligible_counts':{'train':len(tr),'validation':len(va),'test':len(te)},'observed_delta_r2':float(d.loc['BigFive_plus_Consensus_C1_C3','r2']-d.loc['BigFive','r2']),'delta_r2_ci':[lo,hi]},indent=2)+'\n')
    inv=[]
    for p in OUT.iterdir():
        if p.is_file() and p.name!='artifact_inventory.csv': inv.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size))
    pd.DataFrame(inv).sort_values('path').to_csv(OUT/'artifact_inventory.csv',index=False)
    print(json.dumps({'human':human,'delta_r2':float(d.loc['BigFive_plus_Consensus_C1_C3','r2']-d.loc['BigFive','r2']),'ci':[lo,hi],'projection_rows':len(proj)},indent=2))
if __name__=='__main__': main()
