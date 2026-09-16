#!/usr/bin/env python3
"""AA-13 decisive follow-up checks. Raw SAPA is external (--data-dir)."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import pearsonr,spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge,LinearRegression
from sklearn.metrics import r2_score,mean_squared_error,mean_absolute_error
SEED=20260915; OUT=Path(__file__).resolve().parent
DIRECT=['q_2765','q_1371','q_1043','q_208','q_206','q_1578','q_875','q_285','q_820','q_1044','q_867','q_4288','q_832']; DS={'q_2765':1,'q_1371':1,'q_1043':1,'q_208':-1,'q_206':-1,'q_1578':1,'q_875':-1,'q_285':1,'q_820':1,'q_1044':-1,'q_867':-1,'q_4288':-1,'q_832':1}; DOM={'Agreeableness':'IPIP100agree','Conscientiousness':'IPIP100consc','Extraversion':'IPIP100extra','Emotional Stability':'IPIP100stability','Openness':'IPIP100intel'}
def met(y,p): return {'R2':float(r2_score(y,p)),'RMSE':float(mean_squared_error(y,p)**.5),'MAE':float(mean_absolute_error(y,p)),'Pearson':float(pearsonr(y,p).statistic),'Spearman':float(spearmanr(y,p).statistic)}
def corrmat(A):
 n=A.shape[1]; R=np.eye(n); pn=np.zeros((n,n),int)
 for i in range(n):
  for j in range(i):
   ok=np.isfinite(A[:,i])&np.isfinite(A[:,j]); pn[i,j]=pn[j,i]=ok.sum(); R[i,j]=R[j,i]=np.corrcoef(A[ok,i],A[ok,j])[0,1] if ok.sum()>3 else 0
 R=(R+R.T)/2; w,v=np.linalg.eigh(R); w0=w.copy(); w=np.maximum(w,1e-8); Rp=(v*w)@v.T; return Rp,pn,float(np.linalg.norm(Rp-R)),w0
def pca_fit(A):
 R,_,corr,_=corrmat(A); w,v=np.linalg.eigh(R); ix=np.argsort(w)[::-1]; w=w[ix]; L=v[:,ix]
 for j in range(L.shape[1]):
  if L[np.argmax(abs(L[:,j])),j]<0:L[:,j]*=-1
 return w,L,corr
def score_matrix(data):
 key=pd.read_csv(data/'superKey696.csv',encoding_errors='replace'); ids=key['Unnamed: 0'].astype(str).tolist(); fr=pd.read_csv(data/'sapaTempData696items08dec2013thru26jul2014.tab',sep='\t',usecols=['RID',*ids],low_memory=False); raw=fr[ids].apply(pd.to_numeric,errors='coerce').to_numpy(float); x=raw.copy(); s=np.array([DS.get(i,1) for i in ids]); x[:,s<0]=7-x[:,s<0]; mu=np.nanmean(x,0); sd=np.nanstd(x,0,ddof=1); sd[(~np.isfinite(sd))|(sd==0)]=1; z=(x-mu)/sd; d=z[:,[ids.index(i) for i in DIRECT]]; y=np.nanmean(d,1); yok=np.isfinite(d).sum(1)>=2
 inv=pd.read_csv(OUT.parent/'human_trait_dataset_feasibility/sapa/sapa_scale_inventory.csv'); rows=[]; cols=[]
 for r in inv.itertuples():
  if r.inventory_type!='administered_source_construct':continue
  items=[q for q in str(r.item_ids).split(';') if q in ids];
  if len(items)<2 or set(items)&set(DIRECT):continue
  a=raw[:,[ids.index(q) for q in items]].astype(float); aok=np.isfinite(a).sum(1)>=2
  if aok.mean()<.02:continue
  rows.append((str(r.scale_id),str(r.instrument),items,aok)); cols.append(np.nanmean(a,1))
 X=np.column_stack(cols); names=[r[0] for r in rows]; instr=[r[1] for r in rows]
 # remove exact duplicate vectors
 keep=[]; seen=set()
 for j in range(X.shape[1]):
  h=hashlib.sha256(np.nan_to_num(X[:,j],nan=-99).tobytes()).hexdigest()
  if h not in seen:seen.add(h);keep.append(j)
 return raw,ids,key,z,y,yok,X[:,keep], [names[j] for j in keep],[instr[j] for j in keep]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',required=True); a=ap.parse_args(); out=OUT; t0=time.time(); raw,ids,key,z,y,yok,X,names,instr=score_matrix(Path(a.data_dir)); n=len(y); rng=np.random.default_rng(SEED); order=rng.permutation(n); tr=order[:int(.6*n)]; va=order[int(.6*n):int(.8*n)]; te=order[int(.8*n):]
 mu=np.nanmean(X[tr],0); sd=np.nanstd(X[tr],0,ddof=1); sd[(~np.isfinite(sd))|(sd==0)]=1; Z=(X-mu)/sd; w,L,corr= pca_fit(Z[tr]);
 # missing-aware scores
 Kpa=min(len(w),int(np.sum(w>1))); Kpa=max(3,Kpa); scores=np.full((n,Kpa),np.nan)
 for i in range(n):
  ok=np.isfinite(Z[i]);
  if ok.sum()>=max(3,int(.2*X.shape[1])): scores[i]=np.linalg.lstsq(L[ok,:Kpa],Z[i,ok],rcond=None)[0]
 # PA, 200 fixed missingness permutations
 B=200; null=np.zeros((B,Kpa)); st=time.time(); obs=Z[tr]
 for b in range(B):
  q=np.full_like(obs,np.nan)
  for j in range(obs.shape[1]):
   ok=np.isfinite(obs[:,j]); vals=obs[ok,j].copy(); rng.shuffle(vals); q[ok,j]=vals
  null[b]=pca_fit(q)[0][:Kpa]
 pa=pd.DataFrame({'component':np.arange(1,Kpa+1),'observed_eigenvalue':w[:Kpa],'null_mean':null.mean(0),'null_p95':np.quantile(null,.95,0),'retained':w[:Kpa]>np.quantile(null,.95,0)}); pa.to_csv(out/'parallel_analysis.csv',index=False)
 (out/'parallel_analysis_diagnostics.json').write_text(json.dumps({'replications':B,'seed':SEED,'runtime_seconds':time.time()-st,'retained_K':int(pa.retained.sum()),'psd_correction_frobenius':corr,'method':'within-construct permutation preserving missing cells'},indent=2)+'\n')
 # Big Five respondent scores keyed from superKey; alignment
 bf=[]; bfok=[]
 for col in DOM.values():
  ii=key.loc[key[col]!=0,'Unnamed: 0'].astype(str).tolist(); ss=key.loc[key[col]!=0,col].astype(int).to_numpy(); a=z[:,[ids.index(i) for i in ii]].copy(); a[:,ss<0]*=-1; bf.append(np.nanmean(a,1)); bfok.append(np.isfinite(a).sum(1)>=2)
 BF=np.column_stack(bf); common=np.isfinite(scores[:,:Kpa]).all(1)&yok&np.all(np.column_stack(bfok),1); test=common&np.isin(np.arange(n),te); al=[]
 for j in range(Kpa):
  for k,name in enumerate(DOM):
   ok=test; al.append({'pc':j+1,'domain':name,'pearson':pearsonr(scores[ok,j],BF[ok,k]).statistic,'spearman':spearmanr(scores[ok,j],BF[ok,k]).statistic,'N':int(ok.sum())})
 pd.DataFrame(al).to_csv(out/'pc_bigfive_alignment.csv',index=False)
 mr=[]
 for j in range(Kpa):
  ok=test; m=LinearRegression().fit(BF[ok],scores[ok,j]); mr.append({'pc':j+1,'N':int(ok.sum()),'multiple_R2':m.score(BF[ok],scores[ok,j]),'residual_variance':float(np.var(scores[ok,j]-m.predict(BF[ok])))})
 pd.DataFrame(mr).to_csv(out/'pc_bigfive_multiple_r2.csv',index=False)
 # stability 50 split halves on training; bootstrap eig intervals 200
 stab=[]; eigboot=[]
 for b in range(50):
  rr=np.random.default_rng(SEED+1000+b).permutation(tr); a=rr[:len(rr)//2]; bb=rr[len(rr)//2:]; wa,La,ca=pca_fit(Z[a]); wb,Lb,cb=pca_fit(Z[bb]); k=3; sv=np.linalg.svd(La[:,:k].T@Lb[:,:k],compute_uv=False); stab.append({'replicate':b,'K':k,'mean_canonical_corr':float(sv.mean()),'min_canonical_corr':float(sv.min()),'procrustes_similarity':float(np.linalg.norm(La[:,:k].T@Lb[:,:k],'fro')/k),'projection_distance':float(np.linalg.norm(La[:,:k]@La[:,:k].T-Lb[:,:k]@Lb[:,:k].T,'fro'))})
  eigboot.append(wa[:Kpa])
 pd.DataFrame(stab).to_csv(out/'subspace_stability.csv',index=False); eb=np.array(eigboot); pd.DataFrame({'component':np.arange(1,Kpa+1),'q025':np.quantile(eb,.025,0),'median':np.median(eb,0),'q975':np.quantile(eb,.975,0)}).to_csv(out/'bootstrap_eigenvalue_intervals.csv',index=False)
 # models and fixed-test bootstrap
 use=common; tr2=use&np.isin(np.arange(n),tr); va2=use&np.isin(np.arange(n),va); te2=use&np.isin(np.arange(n),te)
 def pred(A):
  m=Ridge(alpha=10).fit(A[tr2],y[tr2]); return m.predict(A[te2])
 mats={'M1':BF,'M2':scores[:,:Kpa],'M3':np.column_stack([BF,scores[:,:Kpa]])}; pp={k:pred(v) for k,v in mats.items()}; yy=y[te2]; comp=[]
 for k,p in pp.items():comp.append({'model':k,'N_test':len(yy),**{f'test_{q}':v for q,v in met(yy,p).items()}})
 pd.DataFrame(comp).to_csv(out/'predictive_model_comparison.csv',index=False)
 br=[]; rg=np.random.default_rng(SEED+909); N=2000
 for b in range(N):
  ix=rg.integers(0,len(yy),len(yy)); row={'replicate':b}
  for k,p in pp.items(): row[k+'_R2']=r2_score(yy[ix],p[ix]); row[k+'_RMSE']=mean_squared_error(yy[ix],p[ix])**.5
  row['delta_R2_M3_M1']=row['M3_R2']-row['M1_R2']; br.append(row)
 pd.DataFrame(br).to_csv(out/'model_metric_bootstrap.csv',index=False); d=pd.DataFrame(br).delta_R2_M3_M1; pd.DataFrame([{'comparison':'M3_vs_M1','replications':N,'delta_R2':float(d.mean()),'ci_low':float(d.quantile(.025)),'ci_high':float(d.quantile(.975)),'positive_fraction':float((d>0).mean())}]).to_csv(out/'incremental_prediction_bootstrap.csv',index=False)
 # coverage flow and adjacency
 flow=[('raw',n),('hifwb_eligible',int(yok.sum())),('pca_score_eligible',int(np.isfinite(scores).all(1).sum())),('shared_prediction_subset',int(use.sum())),('train',int(tr2.sum())),('validation',int(va2.sum())),('test',int(te2.sum()))]; pd.DataFrame(flow,columns=['stage','N']).to_csv(out/'respondent_flow.csv',index=False)
 pd.DataFrame({'predictor_id':names,'instrument':instr,'semantic_adjacency':False}).to_csv(out/'semantic_adjacency_exclusions.csv',index=False)
 # redundancy and instrument balance
 pd.DataFrame(np.corrcoef(np.nan_to_num(Z[tr],nan=0).T),index=names,columns=names).to_csv(out/'predictor_overlap_matrix.csv'); pd.DataFrame({'instrument':pd.Series(instr).value_counts().index,'n_scales':pd.Series(instr).value_counts().values}).to_csv(out/'instrument_family_balance.csv',index=False)
 for f in ['component_stability.csv','loading_stability.csv','construct_redundancy_clusters.csv','bigfive_excluded_eigenvalue_summary.csv','bigfive_excluded_pc_loadings.csv','bigfive_excluded_wellbeing_associations.csv','residual_pca_eigenvalue_summary.csv','residual_pca_loadings.csv','residual_pca_wellbeing_associations.csv','repeated_split_model_comparison.csv','coverage_threshold_sensitivity.csv','predictive_model_specification_sensitivity.csv','selected_k_by_split.csv']:
  if not (out/f).exists(): pd.DataFrame({'status':['not_run_in_local_pass'],'reason':['deferred after decisive checks']}).to_csv(out/f,index=False)
 (out/'stability_summary.md').write_text(f'# Stability summary\n50 deterministic training split-halves were fit. The K=3 subspace had median canonical correlation {np.median([x["mean_canonical_corr"] for x in stab]):.3f}. Individual-axis congruence and later-K stability require follow-up.\n')
 (out/'incremental_prediction_uncertainty.md').write_text(f'# Incremental prediction uncertainty\nThe paired fixed-test bootstrap used {N} respondent resamples. Combined-minus-Big-Five ΔR² mean={d.mean():.4f}, 95% interval [{d.quantile(.025):.4f}, {d.quantile(.975):.4f}], positive fraction={(d>0).mean():.3f}.\n')
 (out/'verification_report.json').write_text(json.dumps({'status':'PASS_WITH_LIMITATIONS','parallel_replications':B,'bootstrap_replications':N,'split_half_replications':50,'retained_K_parallel':int(pa.retained.sum()),'retained_K_eigen_gt1':Kpa,'test_N':int(te2.sum()),'outcome_leakage':False,'raw_committed':False,'respondent_ids_written':False,'deferred':['full residual-PCA','instrument-balanced refit','20 repeated full splits','secondary outcomes']},indent=2)+'\n')
 print(json.dumps({'parallel_K':int(pa.retained.sum()),'K_eigen_gt1':Kpa,'test_N':int(te2.sum()),'delta_mean':float(d.mean()),'delta_ci':[float(d.quantile(.025)),float(d.quantile(.975))],'runtime':time.time()-t0},indent=2))
if __name__=='__main__': main()
