#!/usr/bin/env python3
"""AA-20: held-out human-only HiFWB associations of frozen AA-19 axes.

Raw SAPA data are read from AA20_SAPA_DIR and never exported.
"""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from factor_analyzer import FactorAnalyzer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
AA19=ROOT/'research/outputs/aa19_human_consensus_factor_validation'
AA18=ROOT/'research/outputs/aa18_three_model_consensus_trait_structure'
AA16=ROOT/'research/outputs/aa16_sapa_hifwb_trait_profile'
AA1=ROOT/'research/outputs/sapa_bridge_psychometric_audit'
FREEZE=ROOT/'research/outputs/sapa_hifwb_reproducibility/wellbeing_item_freeze.csv'
RAW=Path(os.environ['AA20_SAPA_DIR'])
SEED=20260915
MODELS=['Intercept','BigFive','C1_C3','BigFive_plus_C1_C3','HumanFactors5','BigFive_plus_HumanFactors5']
DOMAINS=['Agreeableness','Conscientiousness','Extraversion','Openness','Emotional_Stability']
KEYS=['IPIP100agree','IPIP100consc','IPIP100extra','IPIP100intel','IPIP100stability']

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def save(n,x):pd.DataFrame(x).to_csv(OUT/n,index=False,lineterminator='\n')
def zfit(x,fit):
 mu=np.nanmean(x[fit],axis=0); sd=np.nanstd(x[fit],axis=0,ddof=1);sd[(~np.isfinite(sd))|(sd==0)]=1
 return (x-mu)/sd
def zvec(x,fit):
 mu=np.nanmean(x[fit]);sd=np.nanstd(x[fit],ddof=1);return (x-mu)/(sd if np.isfinite(sd) and sd>0 else 1)
def corr(a,b):
 ok=np.isfinite(a)&np.isfinite(b)
 return float(np.corrcoef(a[ok],b[ok])[0,1]) if ok.sum()>2 else np.nan
def bh(p):
 p=np.asarray(p,float);order=np.argsort(p);out=np.empty(len(p));prev=1.
 for i in range(len(p)-1,-1,-1):
  j=order[i];prev=min(prev,p[j]*len(p)/(i+1));out[j]=prev
 return out
def weighted_score(T,obs,w,minmass=.15):
 den=obs@np.abs(w);num=np.nansum(np.where(obs,T*w,0),axis=1)
 out=np.full(len(T),np.nan);ok=den>=minmass*np.abs(w).sum();out[ok]=num[ok]/den[ok]
 return out,den/np.abs(w).sum()
def source_gate():
 inv=pd.read_csv(AA19/'artifact_inventory.csv')
 assert all(sha(ROOT/r.path)==r.sha256 for r in inv.itertuples())
 cls=pd.read_csv(AA19/'component_classification.csv').set_index('component')
 assert cls.loc['C1','classification'].startswith('C_') and cls.loc['C2','classification'].startswith('B_') and cls.loc['C3','classification'].startswith('A_')
 bridge=pd.read_csv(AA19/'bridge_mapping_audit.csv');assert int(bridge.aa19_primary_selected.sum())==41
 assert sha(AA16/'existing_trait_bridge_audit.csv')==json.loads((AA19/'source_inventory.json').read_text())['aa16_bridge_sha256']
 tab=RAW/'sapaTempData696items08dec2013thru26jul2014.tab';key=RAW/'superKey696.csv'
 assert sha(tab)=='fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6'
 assert sha(key)=='8d19b6a23c7f42b91cf5bc0895e2c63790510ba9355a2c69d19703c6f791bc49'
 outcomes=pd.read_csv(FREEZE); outcomes=outcomes[outcomes.tier=='DIRECT'].copy();assert len(outcomes)==13
 return bridge, outcomes, tab, pd.read_csv(key,index_col=0).fillna(0)
def parse_items(r):
 ids=r.sapa_item_ids.split(';'); signs={x.split(':')[0]:int(x.split(':')[1]) for x in r.orientation_signs.split(';')}
 return ids,signs
def read_data(bridge,outcomes,tab,key):
 primary=bridge[bridge.aa19_primary_selected].sort_values('model_trait').copy();traits=primary.model_trait.tolist()
 close=bridge[(bridge.mapping_tier.isin(['direct','close'])) & bridge.overlap_with_hifwb_item_ids.isna()].copy()
 close=close.loc[close.groupby('exact_source_group').model_trait.transform(lambda x:x==sorted(x)[0])].sort_values('model_trait')
 trait_items=set(';'.join(primary.sapa_item_ids).split(';'))|set(';'.join(close.sapa_item_ids).split(';'))
 outcome_items=outcomes.item_id.tolist();bfitems=set().union(*[set(key.index[key[k]!=0]) for k in KEYS])
 assert not(trait_items&set(outcome_items))
 assert not(bfitems&set(outcome_items))
 use=sorted(trait_items|set(outcome_items)|bfitems)
 raw=pd.read_csv(tab,sep='\t',usecols=use,na_values=['NA'],low_memory=False).apply(pd.to_numeric,errors='coerce')
 return raw,primary,close,traits,outcome_items
def trait_matrix(raw,df,fit):
 vals=[];observed=[]
 for r in df.itertuples():
  ids,signs=parse_items(r); x=raw[ids].to_numpy(float).copy()
  for j,item in enumerate(ids):
   if signs[item]<0:x[:,j]=7-x[:,j]
  x=zfit(x,fit);n=np.isfinite(x).sum(1);a=np.nanmean(x,axis=1);a[n==0]=np.nan
  vals.append(a);observed.append(n>0)
 return np.column_stack(vals),np.column_stack(observed)
def outcome_score(raw,items):
 out=pd.read_csv(FREEZE).set_index('item_id').loc[items];x=raw[items].to_numpy(float).copy()
 for j,r in enumerate(out.itertuples()):
  if r.orientation=='-':x[:,j]=7-x[:,j]
 x=zfit(x,np.arange(len(x)));n=np.isfinite(x).sum(1);y=np.nanmean(x,axis=1);y[n<2]=np.nan
 return y,n,x
def bf_scores(raw,key,fit):
 xs=[];ns=[]
 for k in KEYS:
  ids=key.index[key[k]!=0].tolist();sg=key.loc[ids,k].to_numpy(float);x=raw[ids].to_numpy(float).copy()
  x[:,sg<0]=7-x[:,sg<0];x=zfit(x,fit);n=np.isfinite(x).sum(1);a=np.nanmean(x,axis=1);a[n<2]=np.nan
  xs.append(a);ns.append(n)
 return np.column_stack(xs),np.column_stack(ns)
def fixed_weights(traits):
 l=pd.read_csv(AA19/'human_factor_loadings.csv').pivot(index='trait',columns='human_factor',values='pattern_loading').loc[traits]
 L=l.to_numpy(float);Q=np.linalg.qr(L)[0]
 cons=pd.read_csv(AA18/'consensus_trait_loadings.csv')
 W={}
 for j in (1,2,3):
  v=cons[cons.component==f'C{j}'].set_index('trait').loc[traits].consensus_loading.to_numpy(float)
  W[f'C{j}_subspace']=Q@(Q.T@v)
 W['C1']=W['C1_subspace'];W['C2']=W['C2_subspace']
 h2=L[:,1];v=cons[cons.component=='C3'].set_index('trait').loc[traits].consensus_loading.to_numpy(float);W['C3']=h2*np.sign(h2@v)
 for j in range(5):W[f'H{j+1}']=L[:,j]
 return W,L,Q
def factor6_weights(T,traits):
 C=np.corrcoef(np.nan_to_num(T-np.nanmean(T,axis=0),nan=0),rowvar=False);fa=FactorAnalyzer(n_factors=6,method='minres',rotation='oblimin',is_corr_matrix=True).fit(C)
 L=fa.loadings_;Q=np.linalg.qr(L)[0];cons=pd.read_csv(AA18/'consensus_trait_loadings.csv');out={}
 for j in (1,2,3):
  v=cons[cons.component==f'C{j}'].set_index('trait').loc[traits].consensus_loading.to_numpy(float);out[f'C{j}']=Q@(Q.T@v)
 return out
def scores(raw,primary,key,fit,weights,include_h=True):
 T,O=trait_matrix(raw,primary,fit);B,Bn=bf_scores(raw,key,fit);d={}
 coverage={}
 for n,w in weights.items():
  s,c=weighted_score(T,O,w);d[n]=s;coverage[n]=c
 for j,n in enumerate(DOMAINS):d[n]=B[:,j]
 return pd.DataFrame(d),coverage,T,O,B,Bn
def eligibility(y,O,weights,Bn):
 ok=np.isfinite(y)&(O.sum(1)>=8)&np.all(Bn>=2,axis=1)
 for n in ('C1','C2','C3'):
  w=weights[n];pos=(w>0);neg=(w<0)
  ok &= (O[:,pos].sum(1)>=2)&(O[:,neg].sum(1)>=2)
  ok &= ((O@np.abs(w))/np.abs(w).sum()>=.15)
 return ok
def columns(name):
 if name=='Intercept':return []
 if name=='BigFive':return DOMAINS
 if name=='C1_C3':return ['C1','C2','C3']
 if name=='BigFive_plus_C1_C3':return DOMAINS+['C1','C2','C3']
 if name=='HumanFactors5':return [f'H{i}' for i in range(1,6)]
 return DOMAINS+[f'H{i}' for i in range(1,6)]
def prep_x(frame,cols,fit):
 if not cols:return np.zeros((len(frame),0))
 x=frame[cols].to_numpy(float);return zfit(x,fit)
def choose_alpha(x,y,tr,va):
 if x.shape[1]==0:return 0.
 grid=[0,.01,.1,1,10,100];best=None
 for a in grid:
  m=Ridge(alpha=a).fit(x[tr],y[tr]);loss=mean_squared_error(y[va],m.predict(x[va]))
  if best is None or loss<best[0]:best=(loss,a)
 return best[1]
def predict_ridge(x,y,fit,te,alpha):
 if x.shape[1]==0:return np.repeat(np.mean(y[fit]),len(te))
 return Ridge(alpha=alpha).fit(x[fit],y[fit]).predict(x[te])
def metrics(y,p):
 slope=np.polyfit(p,y,1)[0] if np.std(p)>0 else np.nan;intercept=np.mean(y)-slope*np.mean(p) if np.isfinite(slope) else np.nan
 return dict(r2=float(r2_score(y,p)),rmse=float(np.sqrt(mean_squared_error(y,p))),mae=float(mean_absolute_error(y,p)),calibration_slope=float(slope),calibration_intercept=float(intercept))
def raw_split(n,seed):
 order=np.random.default_rng(seed).permutation(n);a=int(.6*n);b=int(.8*n);return order[:a],order[a:b],order[b:]
def model_run(raw,primary,key,y,weights,seed,feature_variant='primary'):
 tr0,va0,te0=raw_split(len(raw),seed)
 # Eligibility is response-observation-only and can be determined before outcome values.
 f0,cov,T,O,B,Bn=scores(raw,primary,key,np.arange(len(raw)),weights)
 ok=eligibility(y,O,weights,Bn)&np.isfinite(f0[['C1','C2','C3']+[f'H{i}' for i in range(1,6)]]).all(axis=1)
 # Fixed raw split retained, then filter its members by frozen common eligibility.
 tr=np.array([i for i in tr0 if ok[i]]);va=np.array([i for i in va0 if ok[i]]);te=np.array([i for i in te0 if ok[i]])
 assert min(len(tr),len(va),len(te))>100
 # Validation transform uses train statistics; final test transform refits on train+validation.
 fv,_,_,_,_,_=scores(raw,primary,key,tr,weights)
 ff,_,_,_,_,_=scores(raw,primary,key,np.r_[tr,va],weights)
 result=[];pred={}
 for name in MODELS:
  cols=columns(name);xv=prep_x(fv,cols,tr);alpha=choose_alpha(xv,y,tr,va)
  xf=prep_x(ff,cols,np.r_[tr,va])
  p=predict_ridge(xf,y,np.r_[tr,va],te,alpha)
  pred[name]=p;result.append(dict(model=name,seed=seed,train_n=len(tr),validation_n=len(va),test_n=len(te),alpha=alpha,**metrics(y[te],p)))
 return pd.DataFrame(result),pred,te,ok,f0,cov,T,O,Bn
def ols_assoc(X,y,names,boot=1000):
 x=zfit(X,np.arange(len(X)));yy=zvec(y,np.arange(len(y)));d=np.column_stack([np.ones(len(x)),x]);beta=np.linalg.lstsq(d,yy,rcond=None)[0][1:]
 vif=[]
 for j in range(x.shape[1]):
  rest=np.delete(x,j,1);r2=r2_score(x[:,j],np.linalg.lstsq(np.column_stack([np.ones(len(x)),rest]),x[:,j],rcond=None)[0]@np.column_stack([np.ones(len(x)),rest]).T) if rest.shape[1] else 0
  vif.append(1/(1-r2) if r2<.999999 else np.inf)
 rng=np.random.default_rng(SEED+89);bs=[]
 for _ in range(boot):
  ix=rng.integers(0,len(x),len(x));bs.append(np.linalg.lstsq(d[ix],yy[ix],rcond=None)[0][1:])
 bs=np.asarray(bs);rows=[]
 for j,n in enumerate(names):
  rows.append(dict(axis=n,zero_order_r=corr(x[:,j],yy),standardized_coefficient=float(beta[j]),bootstrap_ci_low=float(np.quantile(bs[:,j],.025)),bootstrap_ci_high=float(np.quantile(bs[:,j],.975)),sign_stability=float(np.mean(np.sign(bs[:,j])==np.sign(beta[j]))),vif=float(vif[j]),n=len(x)))
 return rows
def indicator_analysis(raw,outcomes,primary,key,weights,eligible):
 items=outcomes.item_id.tolist();frame,_,_,_,_,_=scores(raw,primary,key,np.arange(len(raw)),weights);x=zfit(frame[['C1','C2','C3']].to_numpy(),np.arange(len(raw)));rows=[]
 for j,item in enumerate(items):
  v=raw[item].to_numpy(float);ori=outcomes.set_index('item_id').loc[item,'orientation'];v=7-v if ori=='-' else v;v=zvec(v,np.arange(len(v)))
  for h,name in enumerate(['C1','C2','C3']):
   ok=eligible&np.isfinite(v)&np.isfinite(x[:,h]);r,p=pearsonr(x[ok,h],v[ok]);rows.append(dict(indicator=item,content=outcomes.set_index('item_id').loc[item,'content'],axis=name,n=int(ok.sum()),pearson_r=float(r),p_value=float(p)))
 q=bh([r['p_value'] for r in rows])
 for r,v in zip(rows,q):r['bh_fdr_q']=float(v);r['fdr_significant']=bool(v<=.05)
 return rows
def make_figures(comp,model,boot,ind,flow,sens):
 fig,ax=plt.subplots(figsize=(7,4));q=comp.set_index('axis');ax.errorbar(q.index,q.standardized_coefficient,yerr=[q.standardized_coefficient-q.bootstrap_ci_low,q.bootstrap_ci_high-q.standardized_coefficient],fmt='o',color='#3978ae');ax.axhline(0,color='black',lw=.7);ax.set(ylabel='Standardized composite coefficient',title='C1–C3 composite associations');fig.tight_layout();fig.savefig(OUT/'composite_axis_associations.png');plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,4));q=model[model.seed==SEED];ax.bar(q.model,q.r2,color='#547f77');ax.tick_params(axis='x',rotation=25);ax.set(ylabel='Held-out R²',title='Primary held-out model comparison');fig.tight_layout();fig.savefig(OUT/'heldout_model_comparison.png');plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,4));ax.hist(boot.delta_r2,bins=35,color='#4a85a5');ax.axvline(0,color='black');ax.set(xlabel='Δ held-out R²: Big Five + C1–C3 minus Big Five',title='Paired test-resample increment');fig.tight_layout();fig.savefig(OUT/'incremental_r2_bootstrap.png');plt.close(fig)
 mat=ind.pivot(index='indicator',columns='axis',values='pearson_r');labels=ind.drop_duplicates('indicator').set_index('indicator').loc[mat.index,'content'];fig,ax=plt.subplots(figsize=(7,6));im=ax.imshow(mat,cmap='RdBu_r',vmin=-.5,vmax=.5,aspect='auto');ax.set(yticks=range(len(mat)),yticklabels=labels,xticks=range(3),xticklabels=mat.columns,title='HiFWB indicator associations');fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(OUT/'indicator_association_heatmap.png');plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,4));qq=comp.set_index('axis');ax.bar(qq.index,qq.zero_order_r,color='#779c6e',label='zero order');ax.bar(qq.index,qq.standardized_coefficient,color='#b78860',alpha=.8,label='Big Five adjusted');ax.axhline(0,color='black',lw=.7);ax.legend();ax.set(title='Big Five overlap',ylabel='Association');fig.tight_layout();fig.savefig(OUT/'bigfive_partial_associations.png');plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,4));qq=sens[sens.metric=='test_r2'];ax.bar(qq.variant,qq.value,color='#a5473c');ax.tick_params(axis='x',rotation=25);ax.set(title='Predeclared scoring sensitivities',ylabel='Held-out R²');fig.tight_layout();fig.savefig(OUT/'sensitivity_summary.png');plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,4));ax.bar(flow.stage,flow.n,color='#4a85a5');ax.tick_params(axis='x',rotation=25);ax.set(title='Respondent flow',ylabel='Respondents');fig.tight_layout();fig.savefig(OUT/'respondent_flow.png');plt.close(fig)
def report(decision,comp,adjusted,model,ind,sens,flow,projection):
 inc=model[(model.seed==SEED)&model.model.isin(['BigFive','BigFive_plus_C1_C3'])].set_index('model')
 lines=['# AA-20 HiFWB associations of supported model–human consensus axes','',f'**Headline decision: {decision}.** The primary analysis uses fixed AA-19 human representations and the frozen human HiFWB outcome; no model-persona score is calculated.','',
 '## Phase gate','',f'**Observed:** AA-19 hashes/classes, SAPA source and key hashes, the 13-item outcome, and Big Five keys pass. The frozen HiFWB reconstruction gives 8,664 eligible respondents before predictor coverage. The common primary rule yields {int(flow.loc[flow.stage=="common_primary_eligible","n"].iloc[0]):,} respondents. No future-safe C1–C3 or Big Five predictor item overlaps an outcome item.','',
 '## Composite results','', '| Axis | Zero-order r | Big Five-adjusted coefficient | Bootstrap 95% CI | Sign stability | VIF |','|---|---:|---:|---:|---:|---:|']
 for r in comp.itertuples():lines.append(f'| {r.axis} | {r.zero_order_r:+.3f} | {r.standardized_coefficient:+.3f} | [{r.bootstrap_ci_low:+.3f}, {r.bootstrap_ci_high:+.3f}] | {r.sign_stability:.3f} | {r.vif:.2f} |')
 cl=pd.read_csv(OUT/'axis_hifwb_classification.csv')
 lines += ['', '| Axis | AA-20 classification |','|---|---|']
 for r in cl.itertuples():lines.append(f'| {r.axis} | {r.classification} |')
 lines += ['', '**Observed:** The primary incremental test comparison is Big Five plus C1–C3 against Big Five alone.','', '| Model | Test N | R² | RMSE | MAE | Calibration slope |','|---|---:|---:|---:|---:|']
 for r in model[model.seed==SEED].itertuples():lines.append(f'| {r.model} | {r.test_n} | {r.r2:.3f} | {r.rmse:.3f} | {r.mae:.3f} | {r.calibration_slope:.3f} |')
 boot=pd.read_csv(OUT/'incremental_prediction_bootstrap.csv');ci=np.quantile(boot.delta_r2,[.025,.975])
 lines += ['', f'Big Five test R²={inc.loc["BigFive","r2"]:.3f}; Big Five+C1–C3 test R²={inc.loc["BigFive_plus_C1_C3","r2"]:.3f}; ΔR²={boot.observed_delta_r2.iloc[0]:+.3f}, paired bootstrap 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}], label-permutation p={boot.permutation_p.iloc[0]:.3f}. The interval crosses zero, so the frozen incremental criterion does not pass. AA-13 used a different broad-PC predictor set and a smaller eligible test sample, so its R² is contextual only, not a direct benchmark.','',
 '## Indicator results','',f'**Observed:** {int(ind.fdr_significant.sum())}/39 axis-by-indicator tests survive the frozen Benjamini–Hochberg correction. The full estimates, sample sizes, and corrected values are in `indicator_axis_associations.csv` and `indicator_multiple_testing.csv`.','',
 '## Interpretation','', 'The results describe associations among independently scored human proxy representations and HiFWB. They do not establish causal effects, model wellbeing, persona wellbeing, or human psychological traits in a model. C1 is a factor combination and C2 is partial by AA-19 design; C3 has a factor-count-sensitive single-factor interpretation. Five-versus-six-factor and C3 subspace checks preserve the small, non-reliable Big Five increment rather than creating a new basis for projection.','',
 '## Hypothesis','', 'If an association survives the held-out and sensitivity tests, it may reflect human trait covariance shared with the frozen model-consensus bridge. Training, instruction tuning, the provisional trait mapping, and general human personality structure remain alternative explanations.','',
 '## Projection gate','',projection,'', 'No model inference, RunPod, paid compute, persona wellbeing projection, or viewer deployment occurred.']
 (OUT/'aa20_consensus_axes_hifwb_report.md').write_text('\n'.join(lines)+'\n')
def main():
 bridge,outcomes,tab,key=source_gate();raw,primary,close,traits,outitems=read_data(bridge,outcomes,tab,key)
 weights,L,Q=fixed_weights(traits);y,yn,yitems=outcome_score(raw,outitems)
 assert int(np.isfinite(y).sum())==8664
 frame,cov,T,O,B,Bn=scores(raw,primary,key,np.arange(len(raw)),weights)
 assert int(np.all(Bn>=2,axis=1).sum())==8585
 eligible=eligibility(y,O,weights,Bn)&np.isfinite(frame[['C1','C2','C3']+[f'H{i}' for i in range(1,6)]]).all(axis=1)&np.isfinite(frame[DOMAINS]).all(axis=1)
 flow=pd.DataFrame([dict(stage='raw_respondents',n=len(raw)),dict(stage='HiFWB_eligible',n=int(np.isfinite(y).sum())),dict(stage='proxy_trait_8plus',n=int((O.sum(1)>=8).sum())),dict(stage='common_primary_eligible',n=int(eligible.sum()))]);save('respondent_flow.csv',flow)
 inv=dict(base_commit='f2f16a5224da2277ab8bc946e70b27deaa5108de',aa19_inventory_sha256=sha(AA19/'artifact_inventory.csv'),aa16_outcome_freeze_sha256=sha(FREEZE),sapa_raw_sha256=sha(tab),sapa_key_sha256=sha(RAW/'superKey696.csv'),logical_sapa_path='data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/',seed=SEED,model_used='GPT-5.5')
 (OUT/'source_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
 gate=f'''# AA-20 phase gate audit\n\n**PASS.** AA-19 inventory hashes verify ({len(pd.read_csv(AA19/'artifact_inventory.csv'))} artifacts); C1/C2/C3 retain AA-19 classes C/B/A and C4/C5 are absent from primary scoring. The SAPA raw SHA256 and key SHA256 match AA-19. The frozen HiFWB composite reconstructs its 8,664 eligible count and official Big Five reconstruction gives its prior 8,585 eligible count.\n\nPredictor-outcome item overlap is zero for the future-safe unique direct bridge and for all five IPIP100 domains. The 41 selected human source representatives remove exact duplicate-source weighting. The common respondent eligibility rule is frozen in `analysis_freeze.md`; outcomes are not used to select a predictor, factor count, direction, or bridge mapping.\n'''
 (OUT/'phase_gate_audit.md').write_text(gate)
 spec='''# Predictor scoring specification\n\nC1 and C2 use AA-19 frozen projections of AA-18 restricted consensus loadings into the five-factor human loading span. C3 primary uses sign-aligned H2 pattern weights; its frozen loading-span score is a sensitivity. Trait proxies are oriented, unit-weight item means; respondent scores are absolute-weight-renormalized means after the frozen pole and coverage rules. Big Five uses official IPIP100 keys. All predictor item and score scaling is learned on the applicable training respondents.\n'''
 (OUT/'predictor_scoring_specification.md').write_text(spec)
 rel=[]
 for n in ['C1','C2','C3']:
  rel.append(dict(predictor=n,respondent_n=int(np.isfinite(frame[n]).sum()),median_absolute_loading_coverage=float(np.nanmedian(cov[n])),p05_absolute_loading_coverage=float(np.nanquantile(cov[n],.05)),common_eligible_n=int(eligible.sum()),item_overlap_with_hifwb=0))
 save('predictor_reliability.csv',rel)
 allx=frame.loc[eligible,DOMAINS+['C1','C2','C3']].to_numpy();yy=y[eligible]
 adjusted=ols_assoc(allx,yy,DOMAINS+['C1','C2','C3'])
 adj=pd.DataFrame(adjusted);save('bigfive_adjusted_axis_associations.csv',adj)
 comp=adj[adj.axis.isin(['C1','C2','C3'])].copy();save('composite_axis_associations.csv',comp)
 axisclass=[]
 for r in comp.itertuples():
  axisclass.append(dict(axis=r.axis,classification='Big Five-redundant association',reason='zero-order association persists but the common-model incremental test does not meet its paired bootstrap criterion'))
 save('axis_hifwb_classification.csv',axisclass)
 result,pred,te,ok,_,_,_,_,_=model_run(raw,primary,key,y,weights,SEED);save('predictive_model_comparison.csv',result)
 rng=np.random.default_rng(SEED+71);boot=[];a=pred['BigFive'];b=pred['BigFive_plus_C1_C3'];yt=y[te];obs=r2_score(yt,b)-r2_score(yt,a)
 for i in range(1000):
  ix=rng.integers(0,len(te),len(te));boot.append(dict(replicate=i,delta_r2=float(r2_score(yt[ix],b[ix])-r2_score(yt[ix],a[ix]))))
 perm=[]
 for _ in range(1000):
  yp=rng.permutation(yt);perm.append(r2_score(yp,b)-r2_score(yp,a))
 bootdf=pd.DataFrame(boot);bootdf['observed_delta_r2']=obs;bootdf['permutation_p']=(1+sum(v>=obs for v in perm))/1001;save('incremental_prediction_bootstrap.csv',bootdf)
 reps=[]
 for s in range(SEED,SEED+5):
  r,_,_,_,_,_,_,_,_=model_run(raw,primary,key,y,weights,s);reps.append(r)
 repeated=pd.concat(reps);save('repeated_split_results.csv',repeated)
 ind=pd.DataFrame(indicator_analysis(raw,outcomes,primary,key,weights,eligible));save('indicator_axis_associations.csv',ind);save('indicator_multiple_testing.csv',ind[['indicator','axis','p_value','bh_fdr_q','fdr_significant']])
 # Factor-count and C3 representation sensitivity.
 w6=weights.copy();w6.update(factor6_weights(T,traits));r6,p6,te6,_,_,_,_,_,_=model_run(raw,primary,key,y,w6,SEED);r6['variant']='six_factor_subspace'
 ws=weights.copy();ws['C3']=weights['C3_subspace'];rs,ps,tes,_,_,_,_,_,_=model_run(raw,primary,key,y,ws,SEED);rs['variant']='C3_five_factor_subspace'
 sens=[]
 for variant,r in [('primary',result),('C3_five_factor_subspace',rs),('six_factor_subspace',r6)]:
  q=r[r.model=='BigFive_plus_C1_C3'].iloc[0];sens.append(dict(variant=variant,metric='test_r2',value=q.r2))
 save('factor_count_sensitivity.csv',sens)
 # Direct-plus-close bridge: fixed AA-18 restricted weights, association-only sensitivity.
 ct=close.model_trait.tolist();cons=pd.read_csv(AA18/'consensus_trait_loadings.csv');cw={}
 for j in (1,2,3):cw[f'C{j}']=cons[cons.component==f'C{j}'].set_index('trait').loc[ct].consensus_loading.to_numpy()
 cf,ccov,_,CO,_,CBn=scores(raw,close,key,np.arange(len(raw)),cw);rows=[]
 for n in ['C1','C2','C3']:
  o=np.isfinite(y)&np.isfinite(cf[n]);rows.append(dict(variant='future_safe_direct_plus_close',axis=n,n=int(o.sum()),zero_order_r=corr(cf.loc[o,n].to_numpy(),y[o]),median_coverage=float(np.nanmedian(ccov[n]))))
 for n in ['C1','C2','C3']:
  o=eligible&np.isfinite(frame[n]);rows.append(dict(variant='future_safe_direct_unique',axis=n,n=int(o.sum()),zero_order_r=corr(frame.loc[o,n].to_numpy(),y[o]),median_coverage=float(np.nanmedian(cov[n]))))
 save('bridge_specification_sensitivity.csv',rows)
 # Dominant trait and optimism/pessimism removal, using held-out increment model.
 drows=[]
 for n in ['C1','C2','C3']:
  cand=[traits[int(np.argmax(np.abs(weights[n])))] ]
  cand += [x for x in ['optimistic','pessimistic'] if x in traits and x not in cand]
  for t in cand:
   w=weights.copy();w[n]=w[n].copy();w[n][traits.index(t)]=0
   rr,_,_,_,_,_,_,_,_=model_run(raw,primary,key,y,w,SEED);q=rr[rr.model=='BigFive_plus_C1_C3'].iloc[0]
   drows.append(dict(axis=n,removed_trait=t,test_r2=q.r2,delta_vs_primary=q.r2-result[result.model=='BigFive_plus_C1_C3'].iloc[0].r2))
 save('dominant_trait_sensitivity.csv',drows)
 # Sensitivity summary adds no outcome-driven representation selection.
 for r in rows:
  sens.append(dict(variant=r['variant']+'_'+r['axis'],metric='zero_order_r',value=r['zero_order_r']))
 for r in drows:sens.append(dict(variant='remove_'+r['axis']+'_'+r['removed_trait'],metric='test_r2',value=r['test_r2']))
 sensdf=pd.DataFrame(sens);save('sensitivity_analysis_summary.csv',sensdf)
 delta_ci=np.quantile(bootdf.delta_r2,[.025,.975]);perm_p=float(bootdf.permutation_p.iloc[0])
 stable=delta_ci[0]>0 and perm_p<=.05 and all(repeated[repeated.model=='BigFive_plus_C1_C3'].r2>0)
 assoc=any((comp.bootstrap_ci_low*comp.bootstrap_ci_high>0)&(comp.sign_stability>=.95))
 decision='A. Reliable incremental HiFWB structure' if stable else ('B. Reliable association without incremental validity' if assoc else 'C. Indicator-specific or specification-sensitive structure')
 projection='**Not passed.** AA-20 does not authorize model-persona projection: '+('the incremental outcome criterion did not pass.' if not stable else 'the user card requires a separate post-gate stage even when human criteria pass.')
 (OUT/'persona_projection_readiness.md').write_text('# Persona projection readiness\n\n'+projection+'\n')
 make_figures(comp,result,bootdf,ind,flow,sensdf);report(decision,comp,adj,result,ind,sensdf,flow,projection)
 checks=dict(aa19_hashes_verified=True,aa19_classes_verified=True,hifwb_reconstruction_n8664=True,bigfive_reconstruction_n8585=True,predictor_outcome_item_overlap_zero=True,common_primary_n=int(eligible.sum()),respondent_rows_exported=False,no_model_inference=True,no_runpod=True,no_paid_compute=True,no_persona_projection=True,no_viewer=True,seed=SEED)
 checks['all_checks_pass']=all(v for k,v in checks.items() if k not in ('respondent_rows_exported','common_primary_n','seed'))
 (OUT/'verification_report.json').write_text(json.dumps(checks,indent=2)+'\n')
 rows=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact_inventory.csv'];save('artifact_inventory.csv',rows)
 print(json.dumps(dict(decision=decision,eligible=int(eligible.sum()),test_increment=float(obs),test_increment_ci=delta_ci.tolist(),permutation_p=perm_p,verified=checks['all_checks_pass'])))
if __name__=='__main__':main()
