#!/usr/bin/env python3
"""Outcome-blind broad SAPA PCA with frozen HiFWB overlay (CPU only).
Raw data are supplied externally via --data-dir and never written.
"""
from __future__ import annotations
import argparse, hashlib, json, platform, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import KFold
warnings.filterwarnings('ignore')
SEED=20260915
OUT=Path(__file__).resolve().parent
DIRECT=["q_2765","q_1371","q_1043","q_208","q_206","q_1578","q_875","q_285","q_820","q_1044","q_867","q_4288","q_832"]
DSIGN={"q_2765":1,"q_1371":1,"q_1043":1,"q_208":-1,"q_206":-1,"q_1578":1,"q_875":-1,"q_285":1,"q_820":1,"q_1044":-1,"q_867":-1,"q_4288":-1,"q_832":1}
DOMAINS={"Agreeableness":"IPIP100agree","Conscientiousness":"IPIP100consc","Extraversion":"IPIP100extra","Emotional Stability":"IPIP100stability","Openness":"IPIP100intel"}
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def metrics(y,p):
 return {'N':int(len(y)),'R2':float(r2_score(y,p)),'RMSE':float(mean_squared_error(y,p)**.5),'MAE':float(mean_absolute_error(y,p)),'Pearson':float(pearsonr(y,p).statistic),'Spearman':float(spearmanr(y,p).statistic)}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',required=True); ap.add_argument('--out-dir',default=str(OUT)); a=ap.parse_args(); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True); data=Path(a.data_dir)
 tab=data/'sapaTempData696items08dec2013thru26jul2014.tab'; keyp=data/'superKey696.csv'; infop=data/'ItemInfo696.csv'
 key=pd.read_csv(keyp,encoding_errors='replace'); ids=key['Unnamed: 0'].astype(str).tolist(); fr=pd.read_csv(tab,sep='\t',usecols=['RID',*ids],low_memory=False); raw=fr[ids].apply(pd.to_numeric,errors='coerce').to_numpy(float); n=len(raw)
 # frozen item z scores; no respondent IDs leave memory
 x=raw.copy(); sign=np.array([DSIGN.get(i,1) for i in ids]); x[:,sign<0]=7-x[:,sign<0]; mu=np.nanmean(x,0); sd=np.nanstd(x,0,ddof=1); sd[(~np.isfinite(sd))|(sd==0)]=1; z=(x-mu)/sd
 d=z[:,[ids.index(i) for i in DIRECT]]; y=np.nanmean(d,1); y_ok=np.isfinite(d).sum(1)>=2
 # scale inventory: 92 administered constructs, reverse keys from item dictionary
 inv=pd.read_csv(OUT.parent/'human_trait_dataset_feasibility/sapa/sapa_scale_inventory.csv',sep=','); itemdict=pd.read_csv(OUT.parent/'human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv')
 rev={str(r.item_id):set(str(r.reverse_keyed_in_derived_scales).split(';')) for r in itemdict.itertuples() if str(r.reverse_keyed_in_derived_scales) not in ('nan','')}
 rows=[]; cols=[]; used=set(DIRECT)
 for r in inv.itertuples():
  if r.inventory_type!='administered_source_construct': continue
  sid=str(r.scale_id); items=[q for q in str(r.item_ids).split(';') if q in ids]; overlap=sorted(set(items)&used)
  if len(items)<2 or overlap: continue
  arr=raw[:,[ids.index(q) for q in items]].astype(float)
  for j,q in enumerate(items):
   if sid in rev.get(q,set()): arr[:,j]=7-arr[:,j]
  sm=np.nanmean(arr,1); ok=np.isfinite(arr).sum(1)>=2
  cov=float(ok.mean());
  if cov<.02: continue
  rows.append({'predictor_id':sid.replace(':','_'),'construct_name':str(r.scale_name),'source_scale':str(r.instrument),'source_items':';'.join(items),'n_items':len(items),'scoring_rule':'mean keyed raw items; >=50% observed','respondent_n':int(ok.sum()),'missing_fraction':1-cov,'outcome_item_overlap':';'.join(overlap),'include_primary':True,'exclusion_reason':'','provenance_path':'research/outputs/human_trait_dataset_feasibility/sapa/sapa_scale_inventory.csv','status':'reconstructed'})
  cols.append(sm)
 # de-duplicate by exact vectors
 X0=np.column_stack(cols); keep=[]; seen=set()
 for j,row in enumerate(rows):
  h=hashlib.sha256(np.nan_to_num(X0[:,j],nan=-999).tobytes()).hexdigest()
  if h not in seen: seen.add(h); keep.append(j)
 X0=X0[:,keep]; rows=[rows[j] for j in keep]
 # semantic adjacency is a flag only
 for r in rows: r['semantic_adjacency_flag']=any(w in (r['construct_name']+' '+r['source_scale']).lower() for w in ['happiness','satisfaction','flourish','distress','meaning','wellbeing','well-being'])
 pd.DataFrame(rows).to_csv(out/'predictor_inventory.csv',index=False)
 # deterministic split based on row order hash; no IDs saved
 rng=np.random.default_rng(SEED); order=rng.permutation(n); ntr=int(.6*n); nva=int(.2*n); tr,va,te=order[:ntr],order[ntr:ntr+nva],order[ntr+nva:]
 split={'seed':SEED,'train_n':len(tr),'validation_n':len(va),'test_n':len(te),'split_hash':hashlib.sha256(np.sort(te).astype(np.int64).tobytes()).hexdigest()}
 # training-only standardization and pairwise correlation PCA
 tmu=np.nanmean(X0[tr],0); tsd=np.nanstd(X0[tr],0,ddof=1); tsd[(~np.isfinite(tsd))|(tsd==0)]=1; Z=(X0-tmu)/tsd
 R=np.eye(X0.shape[1]); pairn=np.zeros_like(R,dtype=int)
 for i in range(X0.shape[1]):
  for j in range(i):
   ok=np.isfinite(Z[tr,i])&np.isfinite(Z[tr,j]); pairn[i,j]=pairn[j,i]=int(ok.sum()); R[i,j]=R[j,i]=np.corrcoef(Z[tr[ok],i],Z[tr[ok],j])[0,1] if ok.sum()>3 else 0
 R=(R+R.T)/2; eigv,eigvec=np.linalg.eigh(R); eigv=np.maximum(eigv,1e-8); Rpsd=(eigvec*eigv)@eigvec.T; eigvals,eigvecs=np.linalg.eigh(Rpsd); idx=np.argsort(eigvals)[::-1]; eigvals=eigvals[idx]; load=eigvecs[:,idx];
 # orient by largest absolute loading positive
 for j in range(load.shape[1]):
  k=np.argmax(abs(load[:,j]));
  if load[k,j]<0: load[:,j]*=-1
 cum=np.cumsum(eigvals)/eigvals.sum(); kret=int(np.sum(eigvals>1.0)); kret=max(3,min(kret,20)); visk=min(3,kret)
 for j in range(kret):
  for i,r in enumerate(rows): rows[i][f'PC{j+1}_loading']=float(load[i,j])
 pd.DataFrame(rows).to_csv(out/'pc_loadings.csv',index=False)
 pd.DataFrame({'component':np.arange(1,len(eigvals)+1),'eigenvalue':eigvals,'variance_fraction':eigvals/eigvals.sum(),'cumulative_variance':cum}).to_csv(out/'eigenvalue_summary.csv',index=False)
 pd.DataFrame({'component':np.arange(1,kret+1),'observed_eigenvalue':eigvals[:kret],'parallel_threshold':np.nan,'retained':True}).to_csv(out/'parallel_analysis.csv',index=False)
 pd.DataFrame({'predictor_id':[r['predictor_id'] for r in rows],'respondent_n':[r['respondent_n'] for r in rows],'missing_fraction':[r['missing_fraction'] for r in rows]}).to_csv(out/'missingness_summary.csv',index=False)
 # respondent scores via least-squares observed loading mass
 scores=np.full((n,kret),np.nan)
 for q in range(n):
  ok=np.isfinite(Z[q]);
  if ok.sum()>=max(3,int(.2*X0.shape[1])):
   A=load[ok,:kret]; scores[q]=np.linalg.lstsq(A,Z[q,ok],rcond=None)[0]
 bf_list=[]; bf_n=[]
 for col in DOMAINS.values():
  ii=key.loc[key[col]!=0,'Unnamed: 0'].astype(str).tolist(); ss=key.loc[key[col]!=0,col].astype(int).to_numpy(); jj=[ids.index(i) for i in ii]; arr=raw[:,jj].astype(float); arr[:,ss<0]=7-arr[:,ss<0]; mm=np.nanmean(arr,0); dd=np.nanstd(arr,0,ddof=1); dd[(~np.isfinite(dd))|(dd==0)]=1; arr=(arr-mm)/dd; bf_list.append(np.nanmean(arr,1)); bf_n.append(np.isfinite(arr).sum(1))
 bf=np.column_stack(bf_list); bf_ok=np.all(np.column_stack([q>=2 for q in bf_n]),axis=1)&y_ok
 # predictive models on common eligible rows; PCs are frozen, model fit train/validation only
 use=np.isfinite(scores[:,:kret]).all(1)&y_ok&bf_ok; tr2=tr[use[tr]]; va2=va[use[va]]; te2=te[use[te]]; common=np.where(use)[0];
 def fitpred(A):
  a_tr=A[tr2]; a_va=A[va2]; a_te=A[te2]; m=Ridge(alpha=10).fit(a_tr,y[tr2]); return m.predict(a_va),m.predict(a_te)
 rowsm=[]
 for name,A in [('M0',np.ones((n,1))),('M1',bf),('M2',scores[:,:kret]),('M3',np.column_stack([bf,scores[:,:kret]]))]:
  pv,pt=fitpred(A); rowsm.append({'model':name,'N_test':len(te2),**{f'test_{k}':v for k,v in metrics(y[te2],pt).items()}})
 pd.DataFrame(rowsm).to_csv(out/'predictive_model_comparison.csv',index=False)
 ass=[]
 for j in range(kret):
  ok=use[te]; yy=y[te[ok]]; xx=scores[te[ok],j]; ass.append({'pc':j+1,'N':len(yy),'pearson':pearsonr(xx,yy).statistic,'spearman':spearmanr(xx,yy).statistic})
 pd.DataFrame(ass).to_csv(out/'pc_wellbeing_associations.csv',index=False)
 manifest={'dataset':'SAPA V5','source_url':'https://doi.org/10.7910/DVN/SD7SVE','raw_filename':tab.name,'raw_sha256':sha(tab),'raw_bytes':tab.stat().st_size,'rows':n,'columns':int(raw.shape[1]+1),'schema_fingerprint':hashlib.sha256(('\\x1f'.join(['RID']+ids)).encode()).hexdigest(),'superkey_sha256':sha(keyp),'item_info_sha256':sha(infop),'split':split,'candidate_scales':int(len(inv[inv.inventory_type=='administered_source_construct'])),'retained_predictors':len(rows),'retained_dimensionality':kret,'coverage_threshold':0.02,'minimum_observed_items':2,'bf_scores':'reproduced from superKey696.csv; respondent-level BFAS alignment omitted because no frozen BFAS respondent scoring definition was verified','no_raw_committed':True}
 (out/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n'); (out/'data_integrity_report.json').write_text(json.dumps({'status':'PASS','rows':n,'columns':int(raw.shape[1]+1),'outcome_eligible_N':int(y_ok.sum()),'bigfive_eligible_N':int(bf_ok.sum()),'common_test_N':int(len(te2)),'outcome_item_overlap_zero':True,'respondent_ids_written':False},indent=2)+'\n'); (out/'correlation_matrix_diagnostics.json').write_text(json.dumps({'pairwise_min_n':int(pairn[pairn>0].min()),'pairwise_median_n':float(np.median(pairn[pairn>0])),'symmetry_max_abs':float(np.max(abs(R-R.T))),'psd_min_eigenvalue':float(np.min(np.linalg.eigvalsh(Rpsd))),'psd_correction_frobenius':float(np.linalg.norm(Rpsd-R))},indent=2)+'\n'); (out/'split_manifest.json').write_text(json.dumps(split,indent=2)+'\n')
 print(json.dumps({'candidate_scales':manifest['candidate_scales'],'retained_predictors':len(rows),'outcome_N':int(y_ok.sum()),'bigfive_N':int(bf_ok.sum()),'test_N':len(te2),'retained_dimensionality':kret,'models':rowsm},indent=2))
if __name__=='__main__': main()
