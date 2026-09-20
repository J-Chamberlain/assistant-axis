"""Small regularized multi-output systems with observed-target losses only.
Shared alpha; target-specific intercepts and missing-label masks. CPU/NumPy.
"""
from aa26_common import *
ALPHAS=np.array([1.,10.,100.,1000.])

class Cache:
    def __init__(self,d,specs,Y,tr,va):
        self.nf=len(specs);self.tr=np.asarray(tr);self.va=np.asarray(va);self.Y=Y
        X,_=d.score(specs,self.tr,item_z=True);X,_,_=zfit(X,self.tr)
        observed=np.isfinite(X);p=observed[self.tr].mean(0);ms=np.sqrt(p*(1-p));ms[ms<1e-8]=1
        X=np.column_stack([np.ones(d.n),np.nan_to_num(X,nan=0),(observed-p)/ms])
        self.Xtr=X[self.tr];self.Xv=X[self.va]
        self.mu=np.nanmean(Y[self.tr],0);self.sd=np.nanstd(Y[self.tr],0,ddof=1);self.sd=np.where(self.sd>1e-10,self.sd,1)
        Z=(Y-self.mu)/self.sd
        def moments(ids,design):
            gs=[];bs=[];cs=[];ss=[];ns=[]
            for j in range(Y.shape[1]):
                ok=np.isfinite(Z[ids,j]);x=design[ok];y=Z[ids[ok],j]
                gs.append(x.T@x);bs.append(x.T@y);cs.append(y@y);ss.append(float(((y-y.mean())**2).sum()) if len(y) else 0);ns.append(len(y))
            return np.array(gs),np.array(bs),np.array(cs),np.array(ss),np.array(ns)
        self.G,self.b,self.c,self.sst,self.n=moments(self.tr,self.Xtr)
        self.Gv,self.bv,self.cv,self.sstv,self.nv=moments(self.va,self.Xv)
        assert min(self.n)>=30 and min(self.nv)>=20,(min(self.n),min(self.nv))
        self.memo={}
    def cols(self,features):
        f=sorted(features);return np.array([0]+[1+i for i in f]+[1+self.nf+i for i in f],dtype=int)
    def coefficients(self,features,alpha):
        cols=self.cols(features);g=self.G[:,cols,:][:,:,cols].copy();diag=np.arange(len(cols));g[:,diag[1:],diag[1:]]+=alpha
        beta=np.linalg.solve(g,self.b[:,cols,None])[:,:,0]
        return cols,beta
    def evaluate(self,features):
        k=tuple(sorted(features))
        if k in self.memo:return self.memo[k]
        scores=[]
        cols=self.cols(features);gv=self.Gv[:,cols,:][:,:,cols];bv=self.bv[:,cols]
        for alpha in ALPHAS:
            _,beta=self.coefficients(features,alpha)
            sse=np.einsum('di,dij,dj->d',beta,gv,beta)-2*np.sum(beta*bv,1)+self.cv
            scores.append(float(np.mean(1-sse/self.sstv)))
        self.memo[k]=np.array(scores);return self.memo[k]
    def predict(self,features,alpha):
        cols,beta=self.coefficients(features,alpha);return (self.Xv[:,cols]@beta.T)*self.sd+self.mu

def choose(caches,features):
    v=np.mean([c.evaluate(features) for c in caches],0);j=int(np.argmax(v));return float(v[j]),float(ALPHAS[j])

def greedy(caches,base,candidate_indices,groups,distinct=True,kmax=8):
    selected=[];path=[];base_score,base_alpha=choose(caches,base)
    path.append(dict(k=0,selected=[],score=base_score,alpha=base_alpha,added=None,increment=0.))
    for k in range(1,kmax+1):
        options=[j for j in range(len(candidate_indices)) if j not in selected and (not distinct or all(groups[j]!=groups[u] for u in selected))]
        if not options:break
        possibilities=[]
        for j in options:
            s,a=choose(caches,base+[candidate_indices[u] for u in selected+[j]]);possibilities.append((s,-j,a,j))
        score,_,alpha,j=max(possibilities);gain=score-path[-1]['score'];selected.append(j)
        path.append(dict(k=k,selected=selected.copy(),score=score,alpha=alpha,added=j,increment=gain))
    return path

def residual_groups(d,specs,tr,nbase,nc,threshold=.8):
    from sklearn.linear_model import Ridge
    X,_=d.score(specs,tr,item_z=True);Z=zfit(X,tr)[0];base=np.nan_to_num(Z[:,:nbase],nan=0);res=np.full((len(tr),nc),np.nan)
    for j in range(nc):
        y=Z[:,nbase+j];ok=np.isfinite(y[tr]);m=Ridge(alpha=10).fit(base[tr[ok]],y[tr[ok]]);res[ok,j]=y[tr[ok]]-m.predict(base[tr[ok]])
    parent=list(range(nc));pairs=[]
    def find(i):
        while parent[i]!=i:i=parent[i]
        return i
    for j in range(nc):
        for k in range(j):
            obs=np.isfinite(res[:,j])&np.isfinite(res[:,k]);n=int(obs.sum());r=float(np.corrcoef(res[obs,j],res[obs,k])[0,1]) if n>=100 else None
            names={specs[nbase+j]['name'],specs[nbase+k]['name']}
            semantic=names=={'QB6:QB6:ES','EPQr:EPQ:N'}
            redundant=semantic or (r is not None and abs(r)>=threshold)
            if redundant:parent[find(j)]=find(k)
            ia=set(specs[nbase+j]['items']);ib=set(specs[nbase+k]['items'])
            pairs.append(dict(candidate_a=specs[nbase+j]['name'],candidate_b=specs[nbase+k]['name'],joint_observed_n=n,residual_r=r,shared_items=';'.join(sorted(ia&ib)),semantic_same_construct=semantic,redundant=redundant,threshold=threshold))
    groups=[find(j) for j in range(nc)];return groups,pairs

def r2_dimensions(y,p):
    obs=np.isfinite(y)&np.isfinite(p);n=obs.sum(0);yy=np.where(obs,y,0);mu=yy.sum(0)/np.maximum(n,1)
    sst=np.where(obs,(y-mu)**2,0).sum(0);sse=np.where(obs,(y-p)**2,0).sum(0)
    result=1-sse/np.maximum(sst,1e-30);result[(n<20)|(sst==0)]=np.nan;return result,n

def correlation_dimensions(y,p):
    out=[]
    for j in range(y.shape[1]):
        ok=np.isfinite(y[:,j])&np.isfinite(p[:,j]);out.append(float(np.corrcoef(y[ok,j],p[ok,j])[0,1]) if ok.sum()>20 else np.nan)
    return np.array(out)

def row_correlation(yz,pz):
    ok=np.isfinite(yz)&np.isfinite(pz);n=ok.sum(1);a=np.where(ok,yz,0);b=np.where(ok,pz,0)
    a=np.where(ok,a-a.sum(1)[:,None]/np.maximum(n[:,None],1),0);b=np.where(ok,b-b.sum(1)[:,None]/np.maximum(n[:,None],1),0)
    den=np.sqrt((a*a).sum(1)*(b*b).sum(1));r=np.divide((a*b).sum(1),den,out=np.full(len(a),np.nan),where=(den>0)&(n>=5));return r
