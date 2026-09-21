"""Exact finite PC displacement, two frozen readouts, and frozen AA18 changes."""
from pathlib import Path
import base64,hashlib,json
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.spatial.distance import cdist

HERE=Path(__file__).resolve().parent;OUT=HERE.parent
def unit(a):return a/np.linalg.norm(a)
def deg(a,b):return float(np.degrees(np.arccos(np.clip(unit(a)@unit(b),-1,1))))
def main():
    bundle=np.load(HERE/'qwen_mean_roles.npz');names=bundle['personas'].tolist();H=bundle['vectors'].astype(float);norm=np.linalg.norm(H,axis=1)
    m=pd.read_csv(OUT/'trait_persona_prediction/persona_trait_similarity_matrix.csv').set_index('persona').loc[names];X=m.to_numpy();mu=X.mean(0);sd=X.std(0,ddof=1)
    # Complete trait-PCA reconstruction supplies unit trait directions.
    a=np.load(OUT/'three_model_trait_pca/qwen_trait_pca_directions.npz');t=pd.read_csv(OUT/'three_model_trait_pca/trait_pc_scores_all.csv');t=t[t.model=='qwen'].set_index('trait').loc[m.columns]
    T=t[[f'trait_pc{i}' for i in range(1,240)]].to_numpy()@a['directions'].astype(float)+a['mean'].astype(float);T/=np.linalg.norm(T,axis=1,keepdims=True)
    expected=json.load(open(OUT/'extended_persona_pca/viewer_data.json'))['models']['qwen']['points'];Zref=pd.DataFrame({p['persona']:p['coordinates'] for p in expected}).T.loc[names].to_numpy()[:,:5]
    mean=H.mean(0);U,S,V=np.linalg.svd(H-mean,full_matrices=False);P=V[:5].T
    signs=np.sign(np.sum(((H-mean)@P)*Zref,axis=0));P*=signs;Z=(H-mean)@P
    checks={'pc_coordinate_max_error':float(np.max(abs(Z-Zref))),'trait_cosine_max_error':float(np.max(abs((H/norm[:,None])@T.T-X)))}
    nr=pd.read_csv(OUT/'qwen_trait_sparsity_prediction/role_norm_pc_audit.csv').set_index('persona').loc[names].role_vector_l2_norm.to_numpy();checks['role_norm_max_error']=float(np.max(abs(norm-nr)))
    assert checks['pc_coordinate_max_error']<.005 and checks['trait_cosine_max_error']<1e-6 and checks['role_norm_max_error']<.001,checks
    # Readout vectors and offsets exactly matching the saved score recipes.
    w=pd.read_csv(OUT/'aa26_sapa_profile_information_gain/dependency_repair/AA22/trait_weight_sensitivity.csv').set_index('trait').weight_full_sample
    av=np.zeros(240);idx=m.columns.get_indexer(w.index);av[idx]=w.to_numpy()/w.abs().sum()/sd[idx];bd=av@T;cd=-mu@av
    coef=pd.read_csv(OUT/'aa21_bigfive_hifwb_persona_projection/human_bigfive_hifwb_coefficients.csv');coef=coef[coef.human_fit=='full_overlap_primary'].set_index('domain').standardized_coefficient
    bm=json.load(open(OUT/'externally_anchored_big_five/big_five_domain_directions_manifest.json'))['directions'];bs=pd.read_csv(OUT/'externally_anchored_big_five/big_five_role_scores.csv');bf=np.zeros(H.shape[1]);cf=0.
    for dom,co in coef.items():
        key='neuroticism' if dom=='emotional_stability' else dom;sg=-1 if dom=='emotional_stability' else 1
        v=np.frombuffer(base64.b64decode(bm[f'qwen__external_taxonomy_expanded__{key}']['vector_base64']),dtype='<f4').astype(float)
        vals=bs[(bs.model=='qwen')&(bs.construction=='external_taxonomy_expanded')&(bs.domain==key)].set_index('persona').loc[names].raw_projection_score.to_numpy()
        bf+=co*sg*v/vals.std(ddof=1);cf-=co*sg*vals.mean()/vals.std(ddof=1)
    original=pd.read_csv(OUT/'wellbeing_mapping_comparison/persona_comparison.csv');original=original[original.model=='qwen'].set_index('persona').loc[names]
    cf+=float(np.mean(original.bigfive_score-((H/norm[:,None])@bf+cf)))
    B=np.stack([bf,bd]);C=np.array([cf,cd]);baseline=(H/norm[:,None])@B.T+C
    checks['bridge_baseline_max_error']=float(np.max(abs(baseline-original[['bigfive_score','direct_score']].to_numpy())));assert checks['bridge_baseline_max_error']<1e-6
    cw=pd.read_csv(OUT/'aa18_three_model_consensus_trait_structure/shared_trait_loadings_by_model.csv');cw=cw[(cw.model=='Qwen')&cw.component.isin(['C1','C2','C3','C4','C5'])].pivot(index='trait',columns='component',values='trait_weight').loc[m.columns].to_numpy()
    sc=pd.read_csv(OUT/'aa18_three_model_consensus_trait_structure/shared_persona_scores.csv');sc=sc[sc.component.isin(['C1','C2','C3','C4','C5'])].pivot(index='persona',columns='component',values='qwen_score').loc[names].to_numpy()
    calc=((X-mu)/sd)@cw;intercept=np.mean(calc-sc,axis=0);checks['consensus_baseline_max_error']=float(np.max(abs(calc-intercept-sc)));assert checks['consensus_baseline_max_error']<1e-9
    csd=sc.std(0,ddof=1)
    dist=cdist(Z,Z);np.fill_diagonal(dist,np.inf);fifth=np.partition(dist,4,axis=1)[:,4];scale=float(np.median(fifth));radii=np.array([.25,.5,1.])*scale
    rng=np.random.default_rng(20260921);rows=[];search=[];checkgrad=0.;checkend=0.;failed=0
    for k in [5,3]:
        pk=P[:,:k];positions=Z[:,:k];nk=cdist(positions,positions);np.fill_diagonal(nk,np.inf);support_cut=float(np.quantile(np.partition(nk,4,axis=1)[:,4],.95))
        sample=rng.normal(size=(512,k));sample/=np.linalg.norm(sample,axis=1,keepdims=True)
        for ri,radius in enumerate(radii):
            for i,name in enumerate(names):
                hp=H[i]@pk;hb=H[i]@B.T;bp=pk.T@B.T;n2=norm[i]**2
                def values(x):
                    delta=radius*np.asarray(x);nn=np.sqrt(n2+2*delta@hp+np.sum(delta*delta,axis=-1));return (hb+delta@bp)/np.expand_dims(nn,-1)+C
                def jac(x):
                    de=radius*x;nn=np.sqrt(n2+2*de@hp+de@de);num=hb+de@bp
                    return radius*(bp.T/nn-num[:,None]*(hp+de)[None,:]/nn**3)
                if i==0:
                    xx=unit(np.arange(1,k+1,dtype=float));eps=1e-5;fd=np.stack([(values(xx+np.eye(k)[j]*eps)-values(xx-np.eye(k)[j]*eps))/(2*eps) for j in range(k)],axis=1);checkgrad=max(checkgrad,float(np.max(abs(fd-jac(xx)))))
                sphere={'type':'eq','fun':lambda x:x@x-1,'jac':lambda x:2*x}
                seeds=np.vstack([sample,unit(jac(np.zeros(k))[0]),unit(jac(np.zeros(k))[1])]);sv=values(seeds)
                best=[];maxima=[]
                for obj in [0,1]:
                    starts=[]
                    for ind in np.argsort(sv[:,obj])[::-1]:
                        if all(deg(seeds[ind],x)>30 for x in starts):starts.append(seeds[ind])
                        if len(starts)==3:break
                    sols=[]
                    for x0 in starts:
                        res=minimize(lambda x:-values(x)[obj],x0,jac=lambda x:-jac(x)[obj],constraints=[sphere],method='SLSQP',options={'ftol':1e-11,'maxiter':100})
                        if res.success and abs(res.x@res.x-1)<1e-6:sols.append((values(res.x)[obj],unit(res.x),res))
                        else:failed+=1
                    if not sols:raise RuntimeError((name,k,ri,obj,'no converged optimum'))
                    sols.sort(key=lambda v:-v[0]);best.append(sols[0][1]);peaks=[]
                    for val,x,res in sols:
                        if all(deg(x,y)>15 for y in peaks):peaks.append(x)
                    maxima.append(len(peaks))
                    search.append(dict(persona=name,dimensions=k,radius=radius,bridge=['bigfive','direct'][obj],converged_starts=len(sols),detected_distinct_maxima=len(peaks),sample_best_gain=float(sv[:,obj].max()-baseline[i,obj]),optimized_gain=float(sols[0][0]-baseline[i,obj])))
                gain=np.array([values(best[j])[j]-baseline[i,j] for j in [0,1]])
                assert np.all(gain>1e-9),(name,gain)
                candidates=[('bigfive_optimum',best[0]),('direct_optimum',best[1])]
                start=unit(best[0]+best[1]);v0=min((values(start)-baseline[i])/gain)
                # Epigraph maximin of the fraction of each individually attainable gain.
                cons=[{'type':'eq','fun':lambda v:v[:-1]@v[:-1]-1,'jac':lambda v:np.r_[2*v[:-1],0.]},{'type':'ineq','fun':lambda v:(values(v[:-1])-baseline[i])/gain-v[-1],'jac':lambda v:np.column_stack([jac(v[:-1])/gain[:,None],-np.ones(2)])}]
                cr=[]
                for seed in [start,best[0],best[1]]:
                    vv=min((values(seed)-baseline[i])/gain)
                    rr=minimize(lambda v:-v[-1],np.r_[seed,vv],jac=lambda v:np.r_[np.zeros(k),-1.],constraints=cons,method='SLSQP',options={'ftol':1e-9,'maxiter':200})
                    if rr.success and abs(rr.x[:-1]@rr.x[:-1]-1)<1e-6 and min(cons[1]['fun'](rr.x))>-1e-6:
                        cr.append(rr)
                        if len(cr)==1 and seed is start:break
                assert cr,(name,'no verified compromise convergence')
                rr=max(cr,key=lambda a:min((values(unit(a.x[:-1]))-baseline[i])/gain))
                candidates.append(('compromise',unit(rr.x[:-1])))
                for obj in [0,1]:
                    chosen=[best[obj]]
                    for alt in [1,2]:
                        cap=np.cos(np.pi/4);mask=np.all(seeds@np.stack(chosen).T<=cap+1e-8,axis=1);ids=np.flatnonzero(mask);assert len(ids)
                        aa=[]
                        for ind in ids[np.argsort(sv[ids,obj])[-6:]]:
                            cons2=[sphere]+[{'type':'ineq','fun':lambda x,u=u:cap-x@u,'jac':lambda x,u=u:-u} for u in chosen]
                            rr=minimize(lambda x:-(values(x)[obj]-baseline[i,obj])/gain[obj],seeds[ind],jac=lambda x:-jac(x)[obj]/gain[obj],constraints=cons2,method='SLSQP',options={'ftol':1e-9,'maxiter':250})
                            if rr.success and abs(rr.x@rr.x-1)<1e-6 and np.max(np.stack(chosen)@unit(rr.x))<=cap+1e-6:
                                aa.append(unit(rr.x))
                                if len(aa)==2:break
                        assert aa,(name,'alternative failed');x=max(aa,key=lambda x:values(x)[obj]);chosen.append(x);candidates.append((['bigfive','direct'][obj]+f'_alternative_{alt}',x))
                for kind,x in candidates:
                    delta=radius*x;hnew=H[i]+pk@delta;newtraits=hnew@T.T/np.linalg.norm(hnew);newscore=values(x);exact=hnew@B.T/np.linalg.norm(hnew)+C;checkend=max(checkend,float(np.max(abs(exact-newscore))))
                    dc=((newtraits-X[i])/sd)@cw/csd
                    paths=positions[i]+np.linspace(.2,1,5)[:,None]*delta;nd=cdist(paths,positions);support=np.partition(nd,4,axis=1)[:,4]
                    row=dict(persona=name,dimensions=k,radius=radius,radius_fraction_of_median_fifth_neighbor=[.25,.5,1.][ri],candidate=kind,bigfive_start=baseline[i,0],direct_start=baseline[i,1],bigfive_end=newscore[0],direct_end=newscore[1],delta_bigfive=newscore[0]-baseline[i,0],delta_direct=newscore[1]-baseline[i,1],bigfive_gain_fraction=(newscore[0]-baseline[i,0])/gain[0],direct_gain_fraction=(newscore[1]-baseline[i,1])/gain[1],angle_to_bigfive_optimum=deg(x,best[0]),angle_to_direct_optimum=deg(x,best[1]),endpoint_fifth_neighbor_distance=support[-1],path_max_fifth_neighbor_distance=support.max(),support_threshold=support_cut,path_outside_reference_support=bool(support.max()>support_cut),sphere_norm_error=abs(np.linalg.norm(delta)-radius))
                    for j in range(5):row[f'delta_PC{j+1}']=delta[j] if j<k else 0.;row[f'unit_PC{j+1}']=x[j] if j<k else 0.;row[f'delta_C{j+1}_sd']=dc[j]
                    rows.append(row)
            pd.DataFrame(rows).to_csv(HERE/'partial_candidates.csv',index=False)
            pd.DataFrame(search).to_csv(HERE/'partial_search.csv',index=False)
            print('completed',k,'PCs radius',radius,flush=True)
    result=pd.DataFrame(rows)
    result['delta_bigfive_persona_sd']=result.delta_bigfive/baseline[:,0].std(ddof=1)
    result['delta_direct_persona_sd']=result.delta_direct/baseline[:,1].std(ddof=1)
    result.to_csv(HERE/'radius_candidates.csv',index=False);pd.DataFrame(search).to_csv(HERE/'peak_search_diagnostics.csv',index=False)
    checks.update(gradient_finite_difference_max_error=checkgrad,endpoint_full_vector_score_max_error=checkend,failed_individual_optimizer_starts=failed,candidate_rows=len(result),maximum_sphere_norm_error=float(result.sphere_norm_error.max()),median_fifth_neighbor_distance_5pc=scale,radii=radii.tolist(),model_identity='unknown',no_model_inference=True)
    assert checkgrad<1e-7 and checkend<1e-10 and len(result)==11550 and result.sphere_norm_error.max()<1e-8
    (HERE/'verification.json').write_text(json.dumps(checks,indent=2)+'\n')
    # Save the small, exact geometry/readout bundle so endpoint trait profiles remain retrievable.
    np.savez_compressed(HERE/'radius_geometry.npz',personas=names,traits=m.columns.to_numpy(dtype=str),pc_basis=P,pc_mean=mean,trait_mean=mu,trait_sd=sd,bridge_directions=B,bridge_offsets=C,consensus_weights=cw,consensus_sd=csd)
    for temp in ['partial_candidates.csv','partial_search.csv']:(HERE/temp).unlink(missing_ok=True)
    print(json.dumps(checks,indent=2),flush=True)
if __name__=='__main__':main()
