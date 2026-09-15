#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.neighbors import NearestNeighbors

ROOT=Path(__file__).resolve().parent; OUT=ROOT/'research/outputs/sapa_wellbeing_terrain_explorer'
DATA=Path('/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis-aa10/data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE'); TAB=DATA/'sapaTempData696items08dec2013thru26jul2014.tab'; KEY=DATA/'superKey696.csv'
SEED=20260915; BINS=24; MIN_N=10
DOMAINS={'Agreeableness':'IPIP100agree','Conscientiousness':'IPIP100consc','Extraversion':'IPIP100extra','Emotional Stability':'IPIP100stability','Openness':'IPIP100intel'}
items=pd.read_csv(KEY,encoding_errors='replace'); item_ids=items['Unnamed: 0'].astype(str).tolist()
def score(vals, signs):
 x=vals.astype(float).copy(); x[~np.isfinite(x)]=np.nan
 for j,s in enumerate(signs):
  if int(s)<0:x[:,j]=7-x[:,j]
 mu=np.nanmean(x,axis=0); sd=np.nanstd(x,axis=0,ddof=1); sd[(~np.isfinite(sd))|(sd==0)]=1
 return (x-mu)/sd
def main():
 frame=pd.read_csv(TAB,sep='\t',usecols=['RID',*item_ids],low_memory=False); vals=frame[item_ids].apply(pd.to_numeric,errors='coerce').to_numpy(float)
 assert len(frame)==23679
 domain={}; counts={}
 for name,col in DOMAINS.items():
  mark=items[col].astype(str).str.strip(); keep=mark.isin(['1','-1','+1','+','-']); ids=items.loc[keep,'Unnamed: 0'].astype(str).tolist(); signs=[1 if s in ('1','+1','+') else -1 for s in mark[keep]]; ix=[item_ids.index(i) for i in ids]; z=score(vals[:,ix],signs); counts[name]=np.isfinite(z).sum(1); domain[name]=np.nanmean(z,axis=1)
 terrain=np.column_stack([domain[n] for n in DOMAINS]); elig=np.all(np.column_stack([counts[n]>=2 for n in DOMAINS]),axis=1); terrain=(terrain-np.nanmean(terrain[elig],0))/np.nanstd(terrain[elig],0,ddof=1)
 wf=pd.read_csv(OUT.parent/'sapa_hifwb_reproducibility/wellbeing_item_freeze.csv'); direct=wf[wf.tier=='DIRECT']; d_ids=direct.item_id.tolist(); d_ix=[item_ids.index(i) for i in d_ids]; dz=score(vals[:,d_ix],[1 if str(s).strip().startswith('+') else -1 for s in direct.orientation]); dnames=direct.content.tolist()
 out={};
 for c in sorted(set(dnames)):
  a=dz[:,[i for i,n in enumerate(dnames) if n==c]]; out[c.lower().replace('-','_').replace(' ','_')]=np.nanmean(a,1)
 out['historical_13']=np.nanmean(dz,1); out['non_affect']=np.nanmean(dz[:,[n!='Affect' for n in dnames]],1)
 core=[c for c in ['Affect','Appraisal','Meaning-making','Self-concept','Interpersonal relationships'] if c.lower().replace('-','_').replace(' ','_') in out]
 out['content_balanced_ge2']=np.nanmean(np.column_stack([out[c.lower().replace('-','_').replace(' ','_')] for c in core]),1)
 # valid minimum content groups
 carr=np.column_stack([out[c.lower().replace('-','_').replace(' ','_')] for c in core]); out['content_balanced_ge2'][np.isfinite(carr).sum(1)<2]=np.nan; out['content_balanced_ge3']=out['content_balanced_ge2'].copy(); out['content_balanced_ge3'][np.isfinite(carr).sum(1)<3]=np.nan
 out['vitality']=score(vals[:,[item_ids.index('q_832')]], [1])[:,0]
 names=list(DOMAINS); rows=[]; coeff={}; edges={}
 for label,y in out.items():
  valid=elig&np.isfinite(y); yy=y[valid]; xx=terrain[valid]; mu=float(np.nanmean(yy)); ys=yy-mu
  alpha=GridSearchCV(Ridge(),{'alpha':[0.1,1,10,100]},cv=5,scoring='neg_mean_squared_error').fit(xx,ys).best_params_['alpha']; model=Ridge(alpha=alpha).fit(xx,ys); coeff[label]={'alpha':float(alpha),'intercept':float(model.intercept_+mu),'coef':model.coef_.tolist(),'N':int(valid.sum()),'mean':mu,'sd':float(np.nanstd(yy,ddof=1))}
  for ai in range(5):
   for bi in range(ai+1,5):
    ax,ay=names[ai],names[bi]; xv=terrain[valid,ai]; yv=terrain[valid,bi]; xe=np.linspace(np.nanpercentile(xv,1),np.nanpercentile(xv,99),BINS); ye=np.linspace(np.nanpercentile(yv,1),np.nanpercentile(yv,99),BINS); xb=np.clip(np.searchsorted(xe,xv),0,BINS-1); yb=np.clip(np.searchsorted(ye,yv),0,BINS-1)
    for i in range(BINS):
     for j in range(BINS):
      s=(xb==i)&(yb==j); n=int(s.sum());
      if n>=MIN_N: rows.append({'outcome':label,'x':ax,'y':ay,'ix':i,'iy':j,'x_value':float(xe[i]),'y_value':float(ye[j]),'N':n,'mean':float(np.mean(yy[s])),'sd':float(np.std(yy[s],ddof=1)) if n>1 else 0.0,'se':float(np.std(yy[s],ddof=1)/np.sqrt(n)) if n>1 else 0.0})
  
 # support kNN on full five-dimensional terrain
 nn=NearestNeighbors(n_neighbors=11).fit(terrain[elig]); dist=nn.kneighbors(terrain[elig])[0][:,1:].mean(1); pct=np.searchsorted(np.sort(dist),dist,side='right')/len(dist)*100
 support={'k':10,'N':int(elig.sum()),'distance_percentiles':{str(q):float(np.percentile(dist,q)) for q in [50,75,90,97.5,99]},'strong_max_percentile':75,'moderate_max_percentile':90,'sparse_max_percentile':97.5}
 bundle={'axes':names,'outcomes':{k:{'label':k.replace('_',' ').title(),'N':v['N'],'mean':v['mean'],'sd':v['sd']} for k,v in coeff.items()},'coefficients':coeff,'grid':rows,'support':support,'defaults':{'x':'Extraversion','y':'Emotional Stability','outcome':'content_balanced_ge2','mode':'empirical'},'source':{'dataset':'SAPA V5','respondents':23679,'terrain_N':int(elig.sum()),'tab_sha256':hashlib.sha256(TAB.read_bytes()).hexdigest()}}
 OUT.mkdir(parents=True,exist_ok=True); pd.DataFrame(rows).to_csv(OUT/'wellbeing_surface_aggregate.csv',index=False); (OUT/'wellbeing_surface_bundle.json').write_text(json.dumps(bundle))
 (OUT/'conditional_model_bundle.json').write_text(json.dumps({'axes':names,'coefficients':coeff,'model':'Ridge','alpha_grid':[0.1,1,10,100],'seed':SEED}))
 (OUT/'five_dimensional_support_summary.json').write_text(json.dumps(support,indent=2)); (OUT/'source_manifest.json').write_text(json.dumps(bundle['source'],indent=2))
 pd.DataFrame([{'outcome':k,**v} for k,v in coeff.items()]).to_csv(OUT/'conditional_model_metrics.csv',index=False)
 print(json.dumps({'terrain_N':int(elig.sum()),'grid_rows':len(rows),'outcomes':list(coeff)}))
if __name__=='__main__': main()
