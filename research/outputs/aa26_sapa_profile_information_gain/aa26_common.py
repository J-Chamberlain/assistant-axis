"""CPU-only frozen human input/scoring utilities; no model/persona operations."""
import os
for _k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
    os.environ.setdefault(_k,'1')
import hashlib,io,json,subprocess,warnings
from pathlib import Path
import numpy as np,pandas as pd

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
BASE='d4bd3ff9fa74472353f6db010cee07346c036be0'
AA13='045ac766949356ffb31705c69ba677824faf65b8'
SEED=20260919
BFKEYS=['IPIP100agree','IPIP100consc','IPIP100extra','IPIP100intel','IPIP100stability']
BFNAMES=['Agreeableness','Conscientiousness','Extraversion','Openness','Emotional_stability']
SOURCES={}
warnings.filterwarnings('ignore',message='Mean of empty slice')
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(p,ref=BASE):
    b=subprocess.check_output(['git','show',ref+':'+p],cwd=ROOT)
    SOURCES[(ref,p)]=dict(path=p,commit=ref,sha256=sha(b),bytes=len(b));return b
def read(p,ref=BASE):return pd.read_csv(io.BytesIO(blob('research/outputs/'+p,ref)))
def jsave(p,o):Path(p).write_text(json.dumps(o,indent=2,allow_nan=False)+'\n')
def save(p,rows):pd.DataFrame(rows).to_csv(p,index=False,lineterminator='\n')
def zfit(a,fit):
    mu=np.nanmean(a[fit],axis=0);sd=np.nanstd(a[fit],axis=0,ddof=1)
    sd=np.where(np.isfinite(sd)&(sd>1e-12),sd,1);mu=np.where(np.isfinite(mu),mu,0)
    return (a-mu)/sd,mu,sd
def mean_count(a,minimum=2):
    n=np.isfinite(a).sum(1);v=np.nansum(a,axis=1)/np.maximum(n,1);v[n<minimum]=np.nan;return v,n
def spec(name,ids,signs,minimum=2,**other):return dict(name=name,items=list(ids),signs=[int(x) for x in signs],minimum=minimum,**other)
def weighted(T,O,w,minmass=.15):
    den=O@abs(w);v=np.nansum(np.where(O,T*w,0),1)/np.maximum(den,1e-30)
    v[den<minmass*abs(w).sum()]=np.nan;return v

class Data:
    def __init__(self,directory):
        directory=Path(directory);rp=directory/'sapaTempData696items08dec2013thru26jul2014.tab';kp=directory/'superKey696.csv'
        assert sha(rp.read_bytes())=='fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6'
        assert sha(kp.read_bytes())=='8d19b6a23c7f42b91cf5bc0895e2c63790510ba9355a2c69d19703c6f791bc49'
        self.key=pd.read_csv(kp,index_col=0).fillna(0);self.ids=self.key.index.tolist();self.ix={v:i for i,v in enumerate(self.ids)}
        self.raw=pd.read_csv(rp,sep='\t',usecols=self.ids).loc[:,self.ids].to_numpy(float);assert self.raw.shape==(23679,696)
        self.n=len(self.raw);self.all=np.arange(self.n)
        assert np.isin(self.raw[np.isfinite(self.raw)],np.arange(1,7)).all()
        self.inventory=read('human_trait_dataset_feasibility/sapa/sapa_scale_inventory.csv')
        self.dictionary=read('human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv').set_index('item_id')
        b=read('aa19_human_consensus_factor_validation/bridge_mapping_audit.csv');self.bridge=b[b.aa19_primary_selected].sort_values('model_trait')
        self.bridge_specs=[]
        for r in self.bridge.itertuples():
            ids=r.sapa_item_ids.split(';');sg=dict(x.split(':') for x in r.orientation_signs.split(';'))
            self.bridge_specs.append(spec(r.model_trait,ids,[int(sg[i]) for i in ids],minimum=min(2,len(ids))))
        self.bf_specs=[self.key_spec(k,k) for k in BFKEYS]
        f=read('sapa_hifwb_reproducibility/wellbeing_item_freeze.csv');f=f[f.tier=='DIRECT']
        self.hifwb=spec('HiFWB',f.item_id.tolist(),[1 if s=='+' else -1 for s in f.orientation])
        self.bi=set(i for s in self.bridge_specs for i in s['items']);self.bfi=set(i for s in self.bf_specs for i in s['items']);self.hi=set(self.hifwb['items'])
        self.profile=read('broad_sapa_pca_wellbeing/predictor_inventory.csv',AA13)
        self.orig_target_items=set(';'.join(self.profile.source_items).split(';'))
    def key_spec(self,key,name,items=None,**kw):
        ids=self.key.index[self.key[key]!=0].tolist() if items is None else list(items)
        return spec(name,ids,self.key.loc[ids,key].to_numpy(),official_key=key,**kw)
    def key_for(self,items,sid):
        keys=[k for k in self.key if set(self.key.index[self.key[k]!=0])==set(items)]
        if keys:return keys[0]
        assert sid=='IPIP100:B5:E';return 'IPIP100extra'
    def score(self,specs,fit=None,item_z=False,minimum_override=None):
        vals=[];counts=[]
        for s in specs:
            x=self.raw[:,[self.ix[i] for i in s['items']]].copy();sg=np.array(s['signs']);x[:,sg<0]=7-x[:,sg<0]
            if item_z:x=zfit(x,self.all if fit is None else fit)[0]
            v,n=mean_count(x,s['minimum'] if minimum_override is None else minimum_override);vals.append(v);counts.append(n)
        return np.column_stack(vals),np.column_stack(counts)
    def fixed_weights(self):
        traits=[s['name'] for s in self.bridge_specs]
        l=read('aa19_human_consensus_factor_validation/human_factor_loadings.csv').pivot(index='trait',columns='human_factor',values='pattern_loading').loc[traits].to_numpy(float)
        q=np.linalg.qr(l)[0];c=read('aa18_three_model_consensus_trait_structure/consensus_trait_loadings.csv');w={}
        for j in [1,2,3]:
            v=c[c.component==f'C{j}'].set_index('trait').loc[traits].consensus_loading.to_numpy(float);w[f'C{j}']=q@(q.T@v)
            if j==3:w['C3_subspace']=w['C3'].copy();w['C3']=l[:,1]*np.sign(l[:,1]@v)
        for j in range(5):w[f'H{j+1}']=l[:,j]
        return w
    def human_scores(self,minimum,fit=None):
        T,c=self.score(self.bridge_specs,fit,item_z=True,minimum_override=minimum if minimum==1 else None)
        B,bn=self.score(self.bf_specs,fit,item_z=True);y,yn=self.score([self.hifwb],item_z=True)
        O=np.isfinite(T);W=self.fixed_weights();A=np.column_stack([weighted(T,O,W[n]) for n in ['C1','C2','C3','H1','H2','H3','H4','H5']])
        basic=np.isfinite(y[:,0])&np.isfinite(B).all(1)&(O.sum(1)>=8)
        common=basic.copy()
        for n in ['C1','C2','C3']:
            w=W[n];common&=(O[:,w>0].sum(1)>=2)&(O[:,w<0].sum(1)>=2)&((O@abs(w))/abs(w).sum()>=.15)
        common&=np.isfinite(A).all(1)
        return dict(T=T,O=O,B=B,y=y[:,0],A=A,W=W,basic=basic,common=common)

def freeze_measurements(d):
    inv=d.inventory[d.inventory.inventory_type=='administered_source_construct'];byid={r.scale_id.replace(':','_'):r for r in inv.itertuples()}
    targets=[];audit=[]
    for p in d.profile.itertuples():
        r=byid[p.predictor_id];key=d.key_for(r.item_ids.split(';'),r.scale_id);full=set(d.key.index[d.key[key]!=0]);ids=sorted(full-d.bi-d.bfi-d.hi)
        s=d.key_spec(key,r.scale_id,ids,source_items=sorted(full),instrument=r.instrument)
        v,n=d.score([s]) if ids else (np.full((d.n,1),np.nan),np.zeros((d.n,1)))
        count=int(np.isfinite(v).sum());keep=len(ids)>=2 and count>=.02*d.n
        audit.append(dict(dimension=r.scale_id,official_key=key,original_key_items=len(full),retained_items=len(ids),item_ids=';'.join(ids),signs=';'.join(f'{i}:{int(d.key.loc[i,key]):+d}' for i in ids),source_family=r.instrument,observed_ge2_n=count,coverage=count/d.n,missing_fraction=1-count/d.n,removed_bridge_bf_hifwb_items=';'.join(sorted(full-set(ids))),included=keep,reason='retained' if keep else 'insufficient_disjoint_items_or_coverage'))
        if keep:targets.append(s)
    target_items=set(i for s in targets for i in s['items'])
    allowed=set(d.ids)-target_items-d.bi-d.bfi-d.hi
    # Candidate families retain only their existing officially keyed items outside all targets/baselines/outcomes.
    candidates=[];ca=[]
    names={'BFAS:BFAS:N:W':'Discouragement and self-doubt','HEXACO:H:E:A':'Worry and intrusive anxious thoughts','HEXACO:H:X:L':'Energy and stamina','QB6:QB6:ES':'Broad emotional stability','MPQ:MPQ:WB':'Positive expectations and perceived good fortune','IPIPneo:E6:CH':'Cheerfulness and amusement','IPIPneo:N6:VU':'Coping under pressure','EPQr:EPQ:N':'Broad negative emotionality','PS:PS:S':'Stress reactivity'}
    for r in inv.itertuples():
        key=d.key_for(r.item_ids.split(';'),r.scale_id);full=set(d.key.index[d.key[key]!=0]);ids=sorted(full&allowed)
        if len(ids)<2:continue
        s=d.key_spec(key,r.scale_id,ids,concept=names.get(r.scale_id,r.scale_name),instrument=r.instrument)
        v,n=d.score([s]);count=int(np.isfinite(v).sum());keep=count>=.02*d.n
        ca.append(dict(family=r.scale_id,concept=s['concept'],official_key=key,items=';'.join(ids),signs=';'.join(f'{i}:{int(d.key.loc[i,key]):+d}' for i in ids),item_count=len(ids),original_key_item_count=len(full),observed_ge2_n=count,missing_fraction=1-count/d.n,included=keep,reason='retained' if keep else 'coverage_below_2_percent'))
        if keep:candidates.append(s)
    assert not target_items&(d.bi|d.bfi|d.hi)
    assert not set(i for s in candidates for i in s['items'])&(target_items|d.bi|d.bfi|d.hi)
    return targets,candidates,audit,ca
