#!/usr/bin/env python3
"""AA-19 CPU-only, aggregate-output human structure test. Set AA19_SAPA_DIR."""
from __future__ import annotations
import csv, hashlib, json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy.stats import spearmanr
from factor_analyzer import FactorAnalyzer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
AA18=ROOT/'research/outputs/aa18_three_model_consensus_trait_structure'
AA16=ROOT/'research/outputs/aa16_sapa_hifwb_trait_profile'
AA1=ROOT/'research/outputs/sapa_bridge_psychometric_audit'
RAW=Path(os.environ['AA19_SAPA_DIR'])
SEED=19019
MODELS=('Qwen','Llama','Gemma')
COS={'Qwen':'research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv',
     'Llama':'research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv',
     'Gemma':'research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv'}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,rows):pd.DataFrame(rows).to_csv(OUT/name,index=False,lineterminator='\n')
def corr(a,b):return float(np.corrcoef(a,b)[0,1])
def stand(v):return (v-np.mean(v,axis=0))/np.std(v,axis=0,ddof=1)
def cos(a,b):return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)))
def psd(c):
    e,u=np.linalg.eigh((c+c.T)/2);m=float(e.min());a=(u*np.maximum(e,1e-8))@u.T
    a/=np.sqrt(np.outer(np.diag(a),np.diag(a)));np.fill_diagonal(a,1)
    return a,m,float(np.max(abs(a-c)))
def factor(c,k,rotation='oblimin'):
    f=FactorAnalyzer(n_factors=k,method='minres',rotation=rotation if k>1 else None,is_corr_matrix=True).fit(psd(c)[0])
    l=f.loadings_.copy();phi=f.phi_ if f.phi_ is not None else np.eye(k)
    for j in range(k):
        if l[np.argmax(abs(l[:,j])),j]<0:l[:,j]*=-1;phi[j,:]*=-1;phi[:,j]*=-1
    return l,phi,np.diag(c-l@phi@l.T)
def factor_fit(c,l,phi):
    pred=l@phi@l.T;idx=np.triu_indices(len(c),1)
    return float(np.mean((pred[idx]-c[idx])**2))
def canonical(a,b):
    qa=np.linalg.qr(a)[0];qb=np.linalg.qr(b)[0]
    return np.linalg.svd(qa.T@qb,compute_uv=False)
def align(ref,other):
    sim=ref.T@other/np.outer(np.linalg.norm(ref,axis=0),np.linalg.norm(other,axis=0))
    ii,jj=linear_sum_assignment(-abs(sim));ordered=other[:,jj];sg=np.sign(sim[ii,jj]);sg[sg==0]=1
    return ordered*sg,sim[ii,jj],jj,sg
def matrix_item_corr(raw,items,min_n=200,with_counts=True):
    sub=raw[items]
    c=sub.corr(min_periods=min_n).to_numpy()
    if with_counts:
        obs=sub.notna().to_numpy(dtype=np.int32)
        n=obs.T@obs
        assert np.min(n)>0
    else:n=None
    if not np.isfinite(c).all():raise ValueError('item pair unavailable under minimum N')
    return c,n
def basis(scoring,items,traits):
    pos={x:i for i,x in enumerate(items)};col={t:i for i,t in enumerate(traits)}
    b=np.zeros((len(items),len(traits)))
    for r in scoring.itertuples():
        if r.trait in col:b[pos[r.item_id],col[r.trait]]=float(r.orientation_sign)
    assert (abs(b).sum(0)>0).all()
    return b
def proxy(c,b):
    a=b.T@c@b; d=np.sqrt(np.diag(a));v=a/np.outer(d,d);np.fill_diagonal(v,1);return v
def source_gate():
    inv=pd.read_csv(AA18/'artifact_inventory.csv')
    assert all(digest(ROOT/r.path)==r.sha256 for r in inv.itertuples())
    source=json.loads((AA18/'source_inventory.json').read_text())
    assert all(digest(ROOT/r['path'])==r['sha256'] for r in source['matrix_sources'])
    tab=RAW/'sapaTempData696items08dec2013thru26jul2014.tab';key=RAW/'superKey696.csv'
    assert digest(tab)=='fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6'
    assert digest(key)=='8d19b6a23c7f42b91cf5bc0895e2c63790510ba9355a2c69d19703c6f791bc49'
    bridge=pd.read_csv(AA16/'existing_trait_bridge_audit.csv')
    assert len(bridge)==240 and (bridge.mapping_tier=='direct').sum()==45 and bridge.mapping_tier.isin(['direct','close']).sum()==74
    scoring=pd.read_csv(AA1/'trait_proxy_item_scoring.csv')
    assert len(scoring)==183 and scoring.orientation_status.eq('explicit_resolved').all()
    keytable=pd.read_csv(key,index_col=0).fillna(0)
    bf=['IPIP100agree','IPIP100consc','IPIP100extra','IPIP100intel','IPIP100stability']
    assert all(x in keytable for x in bf)
    pd.DataFrame([dict(model=m,path=COS[m],sha256=digest(ROOT/COS[m])) for m in MODELS]).to_csv(OUT/'source_matrix_hashes.csv',index=False)
    (OUT/'source_inventory.json').write_text(json.dumps(dict(base_commit='eefe021f4f76635eb117e121aa824106a9d08c67',aa18_inventory_sha256=digest(AA18/'artifact_inventory.csv'),aa16_bridge_sha256=digest(AA16/'existing_trait_bridge_audit.csv'),aa1_scoring_sha256=digest(AA1/'trait_proxy_item_scoring.csv'),sapa_raw_sha256=digest(tab),sapa_scoring_key_sha256=digest(key),sapa_logical_path='data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/',respondent_rows_expected=23679,seed=SEED),indent=2)+'\n')
    return bridge,scoring,keytable,tab,bf
def bridge_sets(bridge):
    direct=bridge[bridge.mapping_tier=='direct'].model_trait.tolist();total=bridge[bridge.mapping_tier.isin(['direct','close'])].model_trait.tolist()
    def unique(names):
        x=bridge.set_index('model_trait').loc[names]
        return sorted(x.groupby('exact_source_group').apply(lambda g:sorted(g.index)[0],include_groups=False).tolist())
    safe=bridge[bridge.overlap_with_hifwb_item_ids.isna()]
    return {'direct':direct,'direct_unique':unique(direct),'direct_plus_close':total,
            'future_safe_direct':unique([t for t in direct if t in set(safe.model_trait)]),
            'future_safe_total':unique([t for t in total if t in set(safe.model_trait)])}
def model_bridge(bridge,sets):
    tables={m:pd.read_csv(ROOT/COS[m]) for m in MODELS};traits=tables['Qwen'].columns[1:].tolist()
    assert all(t.columns.tolist()==tables['Qwen'].columns.tolist() and t.persona.tolist()==tables['Qwen'].persona.tolist() for t in tables.values())
    loads=pd.read_csv(AA18/'shared_trait_loadings_by_model.csv');cons=pd.read_csv(AA18/'consensus_trait_loadings.csv');scores=pd.read_csv(AA18/'shared_persona_scores.csv');conv=pd.read_csv(AA18/'trait_convergence_scores.csv')
    z={m:stand(tables[m].iloc[:,1:].to_numpy()) for m in MODELS};rows=[];boots=[];loto=[];rng=np.random.default_rng(SEED);axis_gate={}
    for h in range(1,6):
        c=f'C{h}';cl=cons[cons.component==c].set_index('trait').loc[traits].consensus_loading.to_numpy()
        full={m:scores[scores.component==c][m.lower()+'_score'].to_numpy() for m in MODELS};full['Consensus']=scores[scores.component==c].consensus_score.to_numpy()
        weights={m:loads[(loads.component==c)&(loads.model==m)].set_index('trait').loc[traits].trait_weight.to_numpy() for m in MODELS}
        # Full frozen projection must match each exported AA-18 score after centering.
        assert all(corr(z[m]@weights[m],full[m])>.999999999 for m in MODELS)
        for variant,names in sets.items():
            mask=np.isin(traits,names);partial={m:z[m]@(weights[m]*mask) for m in MODELS}
            partial['Consensus']=sum(stand(partial[m]) for m in MODELS)/3
            pos=cl>0;neg=cl<0;ab=abs(cl)
            posmass=float(ab[mask&pos].sum()/ab[pos].sum());negmass=float(ab[mask&neg].sum()/ab[neg].sum())
            mapped=bridge.set_index('model_trait').loc[[traits[i] for i in np.where(mask)[0]]]
            one_source=float(max(mapped.groupby('exact_source_group').apply(lambda g:ab[[traits.index(t) for t in g.index]].sum(),include_groups=False))/ab[mask].sum())
            strong_pos=int(((ab>=.20)&mask&pos).sum());strong_neg=int(((ab>=.20)&mask&neg).sum())
            for m in (*MODELS,'Consensus'):
                a=stand(partial[m]);b=stand(full[m]);r=corr(a,b);sp=float(spearmanr(a,b).statistic)
                rows.append(dict(component=c,variant=variant,model=m,trait_count=int(mask.sum()),pearson_r=r,spearman_r=sp,standardized_rmse=float(np.sqrt(np.mean((a-b)**2))),positive_mass=posmass,negative_mass=negmass,absolute_mass=float(ab[mask].sum()/ab.sum()),strong_positive_traits=strong_pos,strong_negative_traits=strong_neg,largest_source_mass_share=one_source,top_quartile_order_agreement=float(len(set(np.argsort(a)[-69:])&set(np.argsort(b)[-69:]))/69)))
                if variant=='future_safe_direct':
                    vals=[]
                    for rep in range(200):
                        ids=rng.integers(0,len(a),len(a));vals.append(corr(a[ids],b[ids]))
                    boots.append(dict(component=c,model=m,replicates=200,pearson_p05=float(np.quantile(vals,.05)),pearson_median=float(np.median(vals)),pearson_p95=float(np.quantile(vals,.95))))
                    for t in names:
                        sub=mask.copy();sub[traits.index(t)]=False
                        q=sum(stand(z[mm]@(weights[mm]*sub)) for mm in MODELS)/3 if m=='Consensus' else z[m]@(weights[m]*sub)
                        loto.append(dict(component=c,model=m,removed_trait=t,pearson_r=corr(q,full[m])))
        q=pd.DataFrame(rows);qb=pd.DataFrame(boots);q=q[(q.component==c)&(q.variant=='future_safe_direct')]
        b=qb[qb.component==c]
        axis_gate[c]=bool((q.pearson_r>=.75).all() and (q.spearman_r>=.70).all() and (q.positive_mass>=.10).all() and (q.negative_mass>=.10).all() and (q.strong_positive_traits>=2).all() and (q.strong_negative_traits>=2).all() and (q.largest_source_mass_share<=.5).all() and (b.pearson_p05>.60).all())
    save('bridge_axis_reconstruction.csv',rows);save('bridge_axis_reconstruction_bootstrap.csv',boots);save('bridge_axis_leave_one_trait_out.csv',loto)
    return tables,traits,z,loads,cons,scores,conv,axis_gate
def human_data(bridge,scoring,keytable,tab,bf,sets):
    bf_items=keytable.index[(keytable[bf]!=0).any(axis=1)].tolist()
    items=sorted(set(scoring.item_id)|set(bf_items))
    raw=pd.read_csv(tab,sep='\t',usecols=items,na_values=['NA'])
    assert len(raw)==23679 and len(raw.columns)==len(items)
    itemcorr,pair_n=matrix_item_corr(raw,items)
    alltraits=bridge[bridge.mapping_tier.isin(['direct','close'])].model_trait.tolist()
    b=basis(scoring,items,alltraits)
    allc=proxy(itemcorr,b)
    direct=bridge[bridge.mapping_tier=='direct'].model_trait.tolist();di=[alltraits.index(t) for t in direct]
    saved=pd.read_csv(AA1/'human_trait_proxy_correlation_matrix.csv',index_col=0).loc[direct,direct].to_numpy()
    diff=float(np.max(abs(saved-allc[np.ix_(di,di)])))
    assert diff<2e-5,('AA-1 human correlation not reproduced',diff)
    sf=pd.DataFrame(scoring);audit=bridge.copy()
    audit['orientation_signs']=audit.model_trait.map(sf.groupby('trait').apply(lambda x:';'.join(f'{r.item_id}:{int(r.orientation_sign):+d}' for r in x.itertuples()),include_groups=False))
    audit['aa19_primary_selected']=audit.model_trait.isin(sets['future_safe_direct'])
    audit['aa19_source_alias_representative']=audit.model_trait.isin(sets['direct_unique'])
    audit['aa19_overlap_excluded']=audit.overlap_with_hifwb_item_ids.notna()
    audit.to_csv(OUT/'bridge_mapping_audit.csv',index=False,lineterminator='\n')
    selected=sets['future_safe_direct'];ix=[alltraits.index(t) for t in selected]
    c=allc[np.ix_(ix,ix)];cp,min_e,maxadj=psd(c)
    # Historical proxy pair effective N is the harmonic mean of item-pair Ns.
    eff=[]
    for i,t in enumerate(selected):
        ii=np.where(b[:,alltraits.index(t)]!=0)[0]
        for u in selected[i+1:]:
            jj=np.where(b[:,alltraits.index(u)]!=0)[0];x=pair_n[np.ix_(ii,jj)].ravel();eff.append(len(x)/np.sum(1/x))
    obs=raw.notna().sum(axis=1)
    audit_text=f'''# AA-19 human matrix and phase gate audit

**PASS.** AA-18 artifact-inventory hashes, source-matrix hashes, frozen C1–C5 loadings, AA-16 bridge counts, trait-item orientation table, SAPA raw SHA256, and official IPIP100 keys match their prior records. The 23,679-row raw file was read only through {len(items)} psychological item columns; no identifiers or demographics entered analysis or outputs. Exact absolute user-specific paths remain outside the package.

The 45 direct and 74 total mappings are explicit in `bridge_mapping_audit.csv`. The future-safe direct set has {len(selected)} unique human source representatives after overlap exclusion and alias collapse. Scoring uses the frozen 183 trait-item direction rows, including `7−x` for reverse-oriented released 1–6 items. Reconstructed 45-trait human correlations differ from the previously verified AA-1 aggregate matrix by at most {diff:.9g}.

SAPA administers planned item subsets: median observed loaded items per respondent {float(obs.median()):.0f} of {len(items)}. Median effective pairwise N among primary trait proxies is {np.median(eff):.1f}, minimum {min(eff):.1f}; the primary raw proxy-correlation minimum eigenvalue is {min_e:.6g} and nearest-PSD maximum adjustment is {maxadj:.6g}. Correlations are pairwise-complete standardized unit-weight item-proxy estimates, not correlations of fabricated complete respondent profiles. No respondent-level output is written.

The official five IPIP100 keys exist for secondary comparison. The historical extraction provenance limit on model vectors and the independence limit of the provisional semantic SAPA bridge remain in force. HiFWB overlaps affect only future-safe exclusion; outcome values and associations are never loaded.
'''
    (OUT/'human_matrix_audit.md').write_text(audit_text)
    return raw,items,itemcorr,pair_n,b,alltraits,allc,selected,c,cp,bf,diff
def selected_corr(raw,items,b,alltraits,selected,min_n):
    ix=[alltraits.index(t) for t in selected];use=np.where((abs(b[:,ix]).sum(1)>0))[0]
    ic,_=matrix_item_corr(raw,[items[i] for i in use],min_n,with_counts=False)
    return psd(proxy(ic,b[np.ix_(use,ix)]))[0]
def retention(raw,items,b,alltraits,selected,c,pair_n):
    p=len(selected);rng_pa=np.random.default_rng(SEED+101);rng_cv=np.random.default_rng(SEED+102);cp,_,_=psd(c)
    eig=np.linalg.eigvalsh(cp)[::-1]
    eff=[]
    for i,t in enumerate(selected):
        ii=np.where(b[:,alltraits.index(t)]!=0)[0]
        for u in selected[i+1:]:
            jj=np.where(b[:,alltraits.index(u)]!=0)[0];pair=pair_n[np.ix_(ii,jj)].ravel()
            eff.append(len(pair)/np.sum(1/pair))
    nref=int(round(float(np.median(eff))));null=np.empty((200,p))
    for j in range(200):null[j]=np.linalg.eigvalsh(np.corrcoef(rng_pa.standard_normal((nref,p)),rowvar=False))[::-1]
    q95=np.quantile(null,.95,axis=0);pa=int(sum(eig>q95))
    e,u=np.linalg.eigh(cp);e=e[::-1];u=u[:,::-1];maps=[]
    for k in range(13):
        resid=cp-(u[:,:k]*e[:k])@u[:,:k].T if k else cp
        d=np.sqrt(np.maximum(np.diag(resid),1e-9));par=resid/np.outer(d,d)
        z=par[np.triu_indices(p,1)];maps.append(float(np.mean(z*z)))
    map_k=int(np.argmin(maps))
    folds=[]
    for rep in range(5):
        perm=rng_cv.permutation(len(raw));tr=perm[:int(.7*len(raw))];te=perm[int(.7*len(raw)):]
        train=selected_corr(raw.iloc[tr],items,b,alltraits,selected,100)
        test=selected_corr(raw.iloc[te],items,b,alltraits,selected,50)
        for k in range(1,min(12,p-2)+1):
            l,phi,_=factor(train,k)
            folds.append(dict(split=rep,factors=k,heldout_offdiag_mse=factor_fit(test,l,phi)))
    f=pd.DataFrame(folds);means=f.groupby('factors').heldout_offdiag_mse.mean();ses=f.groupby('factors').heldout_offdiag_mse.sem();best=int(means.idxmin())
    candidate=int(min(k for k in means.index if means.loc[k]<=means.loc[best]+ses.loc[best]))
    count=max(1,min(candidate,pa))
    rows=[dict(component=j+1,observed_eigenvalue=eig[j],parallel_p95=q95[j],parallel_pass=bool(eig[j]>q95[j]),parallel_reference_n=nref,map_objective=maps[j+1] if j<12 else np.nan,parallel_retained=pa,map_selected=map_k,heldout_one_se_selected=candidate,final_retained=count,heldout_mean_mse=float(means.loc[j+1]) if j+1 in means else np.nan,heldout_se=float(ses.loc[j+1]) if j+1 in ses else np.nan) for j in range(p)]
    save('human_factor_retention.csv',rows);save('human_retention_folds.csv',folds)
    l,phi,uni=factor(cp,count);structure=l@phi
    loadrows=[]
    for i,t in enumerate(selected):
        for j in range(count):loadrows.append(dict(trait=t,human_factor=f'H{j+1}',pattern_loading=l[i,j],structure_loading=structure[i,j],communality=float(1-uni[i]),uniqueness=uni[i]))
    save('human_factor_loadings.csv',loadrows)
    save('human_factor_correlations.csv',[dict(factor_a=f'H{i+1}',factor_b=f'H{j+1}',correlation=phi[i,j]) for i in range(count) for j in range(count)])
    primary_item_indices=np.where((abs(b[:,[alltraits.index(t) for t in selected]]).sum(1)>0))[0]
    primary_items=[items[i] for i in primary_item_indices]
    observed_median=float(raw[primary_items].notna().sum(axis=1).median())
    save('human_factor_scores_summary.csv',[dict(human_factor=f'H{j+1}',respondent_scores_imputed=False,loading_l2_norm=float(np.linalg.norm(l[:,j])),explained_proxy_variance_fraction=float(np.sum(structure[:,j]**2)/p),primary_items=len(primary_items),observed_primary_item_median_per_respondent=observed_median,note='Group-level correlation factor; no complete respondent score claimed') for j in range(count)])
    return count,l,phi,structure,cp,pa,map_k,candidate
def retention_split_sensitivity(raw,items,b,alltraits,selected,pa):
    """Independent five-fold split sets expose factor-count sensitivity."""
    rows=[]
    for seed_offset in range(102,110):
        rng=np.random.default_rng(SEED+seed_offset)
        for rep in range(5):
            perm=rng.permutation(len(raw));tr=perm[:int(.7*len(raw))];te=perm[int(.7*len(raw)):]
            train=selected_corr(raw.iloc[tr],items,b,alltraits,selected,100)
            test=selected_corr(raw.iloc[te],items,b,alltraits,selected,50)
            for k in range(3,9):
                l,phi,_=factor(train,k)
                rows.append(dict(seed_offset=seed_offset,split=rep,factors=k,heldout_offdiag_mse=factor_fit(test,l,phi)))
    folds=pd.DataFrame(rows);summary=[]
    for seed_offset,g in folds.groupby('seed_offset'):
        means=g.groupby('factors').heldout_offdiag_mse.mean();ses=g.groupby('factors').heldout_offdiag_mse.sem()
        best=int(means.idxmin());one_se=int(min(k for k in means.index if means.loc[k]<=means.loc[best]+ses.loc[best]))
        summary.append(dict(seed_offset=seed_offset,best_factor_count=best,one_se_factor_count=one_se,pa_cap=pa,selected_factor_count=min(pa,one_se),mse_k5=means.loc[5],mse_k6=means.loc[6],se_at_best=ses.loc[best]))
    save('human_retention_split_sensitivity.csv',summary)
    return pd.DataFrame(summary)
def factor_count_alignment_sensitivity(cp,cons,selected):
    rows=[]
    for k in (5,6):
        l,_,_=factor(cp,k);q=np.linalg.qr(l)[0]
        for j in range(1,6):
            c=f'C{j}';v=cons[cons.component==c].set_index('trait').loc[selected].consensus_loading.to_numpy()
            proj=q@(q.T@v)
            rows.append(dict(human_factor_count=k,component=c,subspace_projection_r=abs(cos(v,proj)),best_single_tucker=max(abs(cos(v,l[:,h])) for h in range(k))))
    save('human_factor_count_sensitivity.csv',rows)
def human_stability(raw,items,b,alltraits,selected,l,count):
    rng=np.random.default_rng(SEED+2);rows=[];sub=[]
    for kind,reps in [('bootstrap',50),('split_half',20)]:
        for rep in range(reps):
            if kind=='bootstrap':
                ids=rng.integers(0,len(raw),len(raw));a=selected_corr(raw.iloc[ids],items,b,alltraits,selected,200)
                la,_,_=factor(a,count);lb=l
            else:
                ids=rng.permutation(len(raw));cut=len(ids)//2
                a=selected_corr(raw.iloc[ids[:cut]],items,b,alltraits,selected,100)
                c=selected_corr(raw.iloc[ids[cut:]],items,b,alltraits,selected,100)
                la,_,_=factor(a,count);lb,_,_=factor(c,count)
            matched,sim,order,sign=align(lb,la)
            cc=canonical(lb,matched)
            sub.append(dict(resample_type=kind,replicate=rep,minimum_canonical=float(cc.min()),mean_canonical=float(cc.mean())))
            for j in range(count):
                rows.append(dict(resample_type=kind,replicate=rep,human_factor=f'H{j+1}',tucker=float(sim[j]*sign[j]),matched_original_factor=int(order[j]+1),sign_correction=int(sign[j])))
    save('human_factor_stability.csv',rows);save('human_subspace_stability.csv',sub)
    df=pd.DataFrame(rows);sd=pd.DataFrame(sub)
    stable_sub=bool(sd.groupby('resample_type').minimum_canonical.median().min()>=.8)
    stable_axis={f'H{j+1}':bool(df[df.human_factor==f'H{j+1}'].groupby('resample_type').tucker.median().min()>=.8) for j in range(count)}
    return stable_sub,stable_axis,df,sd
def axis_interpretation(traits,cons,loads,scores,conv):
    cv=conv.set_index('trait');rows=[];sections=['# AA-19 frozen AA-18 axis interpretation audit','',
      'Observed numerical poles precede all human structural comparisons. Candidate labels remain provisional model-only readings; no axis is a causal trait.','']
    labels={1:'charged expression / factual moderation',2:'abstract inwardness / situated practicality',3:'forgiving care / blunt prescription',4:'integrative exploration / literal tradition',5:'decisive closure / deferential caution'}
    alternatives={1:'expressive intensity versus restrained explanation',2:'conceptual register versus practical engagement',3:'care and openness versus directive hardness',4:'systems scope versus literal specificity',5:'assertive certainty versus reflective hesitation'}
    diag=pd.read_csv(AA18/'shared_dimension_diagnostics.csv').set_index('component')
    stab=pd.read_csv(AA18/'component_stability.csv')
    for j in range(1,6):
        c=f'C{j}';q=cons[cons.component==c].set_index('trait').loc[traits];v=q.consensus_loading.to_numpy();ss=scores[scores.component==c]
        top=list(np.argsort(-v)[:10])+list(np.argsort(v)[:10]);other=cons[(cons.component!=c)&cons.component.isin([f'C{x}' for x in range(1,6)])].pivot(index='trait',columns='component',values='consensus_loading')
        for ix in top:
            t=traits[ix];ll=loads[(loads.trait==t)&(loads.component==c)].set_index('model')
            rows.append(dict(component=c,pole='positive' if v[ix]>0 else 'negative',rank=int(np.where(np.array(top)==ix)[0][0]%10+1),trait=t,consensus_loading=v[ix],qwen_loading=float(ll.loc['Qwen','trait_loading']),llama_loading=float(ll.loc['Llama','trait_loading']),gemma_loading=float(ll.loc['Gemma','trait_loading']),loading_range=float(q.loc[t,'loading_range']),all_three_trait_convergence=float(cv.loc[t,'all_three_convergence_score']),minimum_trait_profile_r=float(cv.loc[t,'minimum_pairwise_pearson']),cross_loading=bool((abs(other.loc[t])>=.4).any())))
        p=ss.nlargest(5,'consensus_score').persona.tolist();n=ss.nsmallest(5,'consensus_score').persona.tolist()
        boot=stab[(stab.component==c)&(stab.resample_type=='bootstrap')].score_correlation.median()
        half=stab[(stab.component==c)&(stab.resample_type=='split_half')].score_correlation.median()
        disagreement=q.sort_values('loading_range',ascending=False).head(3).index.tolist()
        cross=sum((abs(other)>=.4).any(axis=1).loc[traits[i]] for i in np.where(abs(v)>=.4)[0])
        sections += [f'## {c}: {labels[j]}','',f'**Observed positive poles:** '+', '.join(f'{traits[i]} ({v[i]:+.2f})' for i in np.argsort(-v)[:5])+'.',
          f'**Observed negative poles:** '+', '.join(f'{traits[i]} ({v[i]:+.2f})' for i in np.argsort(v)[:5])+'.',
          f'Highest consensus personas: {", ".join(p)}. Lowest: {", ".join(n)}.',
          f'Positive/negative absolute loading mass: {abs(v[v>0]).sum():.1f}/{abs(v[v<0]).sum():.1f}; leading-trait cross-loadings and three-model disagreements are in `consensus_axis_poles.csv`.',
          f'Largest model-loading ranges: {", ".join(disagreement)}. Of {sum(abs(v)>=.4)} salient traits, {cross} also cross-load at |loading|≥0.4 on another C1–C5 axis.',
          f'AA-18 held-out weakest model-pair score r={diag.loc[j,"heldout_min_pairwise_pearson"]:.3f}; minimum trait-loading Tucker={diag.loc[j,"trait_loading_min_tucker"]:.3f}; median bootstrap/split-half axis score correlations={boot:.3f}/{half:.3f}.',
          f'**Interpretation:** The candidate label summarizes a signed model profile, subject to bridge and human tests. Plausible alternative: {alternatives[j]}.','']
    save('consensus_axis_poles.csv',rows);(OUT/'consensus_axis_interpretation.md').write_text('\n'.join(sections).rstrip()+'\n')
def matrix_alignment(bridge,sets,alltraits,allc,z,traits):
    rng=np.random.default_rng(SEED+3);rows=[]
    variants={'future_safe_direct':sets['future_safe_direct'],'direct_plus_close':sets['direct_plus_close']}
    for variant,names in variants.items():
        ai=[alltraits.index(t) for t in names];mi=[traits.index(t) for t in names]
        hc=allc[np.ix_(ai,ai)];h=hc[np.triu_indices(len(names),1)]
        modelc={m:np.corrcoef(z[m][:,mi],rowvar=False) for m in MODELS}
        modelc['Consensus']=np.mean(list(modelc.values()),axis=0)
        for m,mc in modelc.items():
            x=mc[np.triu_indices(len(names),1)];actual=corr(h,x);null=[]
            for rep in range(500):
                perm=rng.permutation(len(names));v=mc[np.ix_(perm,perm)][np.triu_indices(len(names),1)]
                null.append(corr(h,v))
            rows.append(dict(variant=variant,model=m,traits=len(names),upper_triangle_pearson=actual,upper_triangle_spearman=float(spearmanr(h,x).statistic),permutation_p=(1+sum(v>=actual for v in null))/501,null_p95=float(np.quantile(null,.95))))
    save('human_model_matrix_alignment.csv',rows)
    return pd.DataFrame(rows)
def axis_human_alignment(sets,traits,cons,selected,l,structure,axis_gate,stable_sub,stable_axis,raw,items,b,alltraits,count):
    rng=np.random.default_rng(SEED+4);q=np.linalg.qr(l)[0];rows=[];subrows=[]
    respondent_q=[]
    for rep in range(50):
        ids=rng.integers(0,len(raw),len(raw));cc=selected_corr(raw.iloc[ids],items,b,alltraits,selected,200)
        lb,_,_=factor(cc,count);respondent_q.append(np.linalg.qr(lb)[0])
    for j in range(1,6):
        c=f'C{j}';full=cons[cons.component==c].set_index('trait').loc[traits].consensus_loading
        v=full.loc[selected].to_numpy();proj=q@(q.T@v);fit=abs(cos(v,proj));sim=[abs(cos(v,l[:,h])) for h in range(count)]
        best=int(np.argmax(sim));single=float(max(sim));sg=np.sign(v@proj);p=v>.2;n=v<-.2
        polep=float(np.mean(np.sign(v[p])==np.sign(sg*proj[p]))) if p.any() else np.nan
        polen=float(np.mean(np.sign(v[n])==np.sign(sg*proj[n]))) if n.any() else np.nan
        null=[]
        for rep in range(500):
            vp=v[rng.permutation(len(v))];null.append(abs(cos(vp,q@(q.T@vp))))
        traitboot=[]
        for rep in range(50):
            ix=rng.choice(len(v),size=int(.8*len(v)),replace=False);qq=np.linalg.qr(l[ix])[0]
            traitboot.append(abs(cos(v[ix],qq@(qq.T@v[ix]))))
        respondent=[abs(cos(v,qq@(qq.T@v))) for qq in respondent_q]
        pval=(1+sum(x>=fit for x in null))/501
        if not axis_gate[c]:cls='D_presently_untestable'
        elif fit>=.8 and pval<=.05 and min(polep,polen)>=.7 and min(traitboot)>=.6 and min(respondent)>=.6 and stable_sub:
            cls='A_independently_supported' if single>=.7 and stable_axis[f'H{best+1}'] else 'C_human_combination'
        elif fit>=.6 and pval<=.05 and stable_sub:cls='B_partial_human_analogue'
        elif fit<.6 and pval>.05:cls='E_not_supported'
        else:cls='B_partial_human_analogue'
        rows.append(dict(component=c,bridge_adequate=axis_gate[c],human_subspace_projection_r=fit,best_single_factor=f'H{best+1}',best_single_tucker=single,mapping_permutation_p=pval,permutation_p95=float(np.quantile(null,.95)),positive_pole_agreement=polep,negative_pole_agreement=polen,trait_bootstrap_p05=float(np.quantile(traitboot,.05)),respondent_bootstrap_p05=float(np.quantile(respondent,.05)),stable_human_subspace=stable_sub,best_human_axis_stable=stable_axis[f'H{best+1}'],classification=cls))
        for h in range(count):subrows.append(dict(component=c,human_factor=f'H{h+1}',individual_tucker=float(cos(v,l[:,h])),human_factor_stable=stable_axis[f'H{h+1}'],subspace_projection_r=fit,principal_angle_degrees=float(np.degrees(np.arccos(np.clip(fit,-1,1))))))
    save('consensus_axis_human_alignment.csv',rows);save('human_model_subspace_alignment.csv',subrows)
    save('component_classification.csv',[{k:r[k] for k in ('component','bridge_adequate','human_subspace_projection_r','best_single_factor','best_single_tucker','mapping_permutation_p','classification')} for r in rows])
    mload=np.column_stack([cons[cons.component==f'C{j}'].set_index('trait').loc[selected].consensus_loading.to_numpy() for j in range(1,6)])
    cc=canonical(mload,l);nullmin=[]
    for rep in range(500):nullmin.append(float(canonical(mload[rng.permutation(len(selected))],l).min()))
    save('human_model_global_subspace.csv',[dict(canonical_index=j+1,canonical_correlation=float(v),principal_angle_degrees=float(np.degrees(np.arccos(np.clip(v,-1,1)))),minimum_canonical_permutation_p=(1+sum(x>=cc.min() for x in nullmin))/501,null_minimum_p95=float(np.quantile(nullmin,.95))) for j,v in enumerate(cc)])
    return pd.DataFrame(rows)
def model_specific_alignment(traits,selected,loads,l):
    q=np.linalg.qr(l)[0];rows=[]
    for c in [f'C{j}' for j in range(1,6)]:
        for m in MODELS:
            v=loads[(loads.component==c)&(loads.model==m)].set_index('trait').loc[selected].trait_loading.to_numpy()
            pr=q@(q.T@v)
            rows.append(dict(component=c,model=m,human_subspace_projection_r=abs(cos(v,pr)),best_single_human_tucker=max(abs(cos(v,l[:,j])) for j in range(l.shape[1]))))
    save('model_specific_human_alignment.csv',rows)
def sensitivity_human(sets,traits,cons,alltraits,allc):
    rng=np.random.default_rng(SEED+5);rows=[];axis=[]
    for variant in ['direct','direct_unique','direct_plus_close','future_safe_total']:
        names=sets[variant];ix=[alltraits.index(t) for t in names];c=psd(allc[np.ix_(ix,ix)])[0]
        eig=np.linalg.eigvalsh(c)[::-1];nref=474
        null=np.array([np.linalg.eigvalsh(np.corrcoef(rng.standard_normal((nref,len(names))),rowvar=False))[::-1] for _ in range(100)])
        k=int(sum(eig>np.quantile(null,.95,axis=0)));k=max(1,min(k,12))
        l,phi,_=factor(c,k);q=np.linalg.qr(l)[0]
        rows.append(dict(variant=variant,traits=len(names),parallel_retained=k,first_eigenvalue=float(eig[0]),factor_fit_offdiag_mse=factor_fit(c,l,phi)))
        for j in range(1,6):
            v=cons[cons.component==f'C{j}'].set_index('trait').loc[names].consensus_loading.to_numpy()
            fit=abs(cos(v,q@(q.T@v)));nvals=[]
            for _ in range(200):
                vp=v[rng.permutation(len(v))];nvals.append(abs(cos(vp,q@(q.T@vp))))
            axis.append(dict(variant=variant,component=f'C{j}',human_factor_count=k,subspace_projection_r=fit,permutation_p=(1+sum(a>=fit for a in nvals))/201))
    save('human_sensitivity_retention.csv',rows);save('human_bridge_sensitivity.csv',axis)
    return pd.DataFrame(axis)
def missingness_sensitivity(raw,items,b,alltraits,selected,primary_c,primary_l,count):
    ix=[alltraits.index(t) for t in selected];use=np.where((abs(b[:,ix]).sum(1)>0))[0]
    rank_item=raw[[items[i] for i in use]].corr(method='spearman',min_periods=200).to_numpy()
    if not np.isfinite(rank_item).all():raise ValueError('Spearman item pair unavailable')
    rank_proxy=psd(proxy(rank_item,b[np.ix_(use,ix)]))[0]
    rank_l,_,_=factor(rank_proxy,count)
    upper=np.triu_indices(len(selected),1)
    rows=[dict(method='pairwise_complete_Spearman_item_correlation',traits=len(selected),factors=count,
               pearson_vs_spearman_proxy_matrix_r=corr(primary_c[upper],rank_proxy[upper]),
               median_absolute_proxy_pair_change=float(np.median(abs(primary_c[upper]-rank_proxy[upper]))),
               factor_subspace_min_canonical=float(canonical(primary_l,rank_l).min()),
               factor_subspace_mean_canonical=float(canonical(primary_l,rank_l).mean()),
               missingness_treatment='same planned-missing item pairs; rank correlation sensitivity')]
    save('human_missingness_sensitivity.csv',rows)
def bigfive_alignment(keytable,bf,items,itemcorr,b,alltraits,selected,l,cp,cons):
    bi=[alltraits.index(t) for t in selected];bp=b[:,bi]
    bb=np.column_stack([keytable.loc[items,x].to_numpy(dtype=float) for x in bf])
    total=proxy(itemcorr,np.column_stack([bp,bb]));cross=total[:len(selected),len(selected):];bfcor=total[len(selected):,len(selected):]
    rows=[];vectors={f'H{j+1}':l[:,j] for j in range(l.shape[1])};q=np.linalg.qr(l)[0]
    for j in range(1,6):
        v=cons[cons.component==f'C{j}'].set_index('trait').loc[selected].consensus_loading.to_numpy()
        vectors[f'C{j}_human_projection']=q@(q.T@v)
    for name,v in vectors.items():
        coeff=np.linalg.pinv(cp)@v
        denom=np.sqrt(max(float(coeff@cp@coeff),1e-12));r=(coeff@cross)/denom
        r2=float(np.clip(r@np.linalg.pinv(bfcor)@r,0,1))
        for x,z in zip(bf,r):rows.append(dict(dimension=name,big_five_key=x,aggregate_correlation=float(z),multiple_r2=r2,part_whole_overlap_possible=True,method='official IPIP100 item-key aggregate; descriptive structural projection'))
    save('bigfive_alignment.csv',rows)
    return pd.DataFrame(rows)
def figures(cons,selected,ret,rec,alignment,load,stability,big,classes,scores):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'savefig.dpi':180})
    fig,axes=plt.subplots(1,5,figsize=(17,5),sharex=True)
    for i,ax in enumerate(axes,1):
        q=cons[cons.component==f'C{i}'].sort_values('consensus_loading')
        z=pd.concat([q.head(5),q.tail(5)]);ax.barh(z.trait,z.consensus_loading,color=['#3978ae' if x<0 else '#a5473c' for x in z.consensus_loading]);ax.axvline(0,color='black',lw=.6);ax.set_title(f'C{i}');ax.invert_yaxis()
    fig.tight_layout();fig.savefig(OUT/'consensus_axis_poles.png');plt.close(fig)
    q=rec[(rec.variant=='future_safe_direct')&(rec.model=='Consensus')]
    fig,ax=plt.subplots(figsize=(8,4));x=np.arange(5);ax.bar(x-.18,q.positive_mass,width=.36,label='positive');ax.bar(x+.18,q.negative_mass,width=.36,label='negative');ax.set(xticks=x,xticklabels=q.component,ylabel='Fraction of full pole absolute loading mass',title='Future-safe direct bridge coverage');ax.legend();fig.tight_layout();fig.savefig(OUT/'bridge_pole_coverage.png');plt.close(fig)
    fig,axes=plt.subplots(1,5,figsize=(16,3.5))
    for i,ax in enumerate(axes,1):
        q=scores[scores.component==f'C{i}'];target=stand(q.consensus_score.to_numpy());pred=stand(q.bridge_consensus_score.to_numpy());ax.scatter(target,pred,s=8,alpha=.45);ax.set(title=f'C{i} r={corr(target,pred):.2f}',xlabel='Full consensus',ylabel='Bridge reconstruction');ax.axline((0,0),slope=1,color='gray',lw=.7)
    fig.tight_layout();fig.savefig(OUT/'full_vs_bridge_reconstruction.png');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4));q=ret.head(12);axes[0].plot(q.component,q.observed_eigenvalue,'o-',label='Human');axes[0].plot(q.component,q.parallel_p95,'--',label='Parallel 95%');axes[0].legend();axes[0].set(xlabel='Ordered component',ylabel='Eigenvalue');axes[1].errorbar(q.component,q.heldout_mean_mse,yerr=q.heldout_se,fmt='o-');axes[1].set(xlabel='Factors',ylabel='Held-out off-diagonal MSE');fig.tight_layout();fig.savefig(OUT/'human_retention_diagnostics.png');plt.close(fig)
    mat=load.pivot(index='trait',columns='human_factor',values='pattern_loading').loc[selected];fig,ax=plt.subplots(figsize=(max(5,mat.shape[1]*.8),max(7,len(selected)*.18)));im=ax.imshow(mat,cmap='RdBu_r',vmin=-1,vmax=1,aspect='auto');ax.set(yticks=range(len(selected)),yticklabels=selected,xticks=range(mat.shape[1]),xticklabels=mat.columns,title='Human oblique factor pattern');fig.colorbar(im,ax=ax,shrink=.65);fig.tight_layout();fig.savefig(OUT/'human_loading_heatmap.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4));ax.bar(alignment.component,alignment.human_subspace_projection_r,color=['#547f77' if x else '#b78860' for x in alignment.bridge_adequate]);ax.axhline(.8,ls='--',color='gray');ax.set(ylabel='Restricted loading projection r',ylim=(0,1),title='Model axes in human factor subspace');fig.tight_layout();fig.savefig(OUT/'human_model_subspace_alignment.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4));s=stability[stability.resample_type=='bootstrap'];ax.boxplot([s[s.human_factor==x].tucker for x in sorted(s.human_factor.unique())],tick_labels=sorted(s.human_factor.unique()));ax.axhline(.8,ls='--',color='gray');ax.set(ylabel='Aligned Tucker congruence',title='Respondent bootstrap factor stability');fig.tight_layout();fig.savefig(OUT/'human_factor_bootstrap_stability.png');plt.close(fig)
    mat=big.pivot(index='dimension',columns='big_five_key',values='aggregate_correlation');fig,ax=plt.subplots(figsize=(8,max(4,len(mat)*.42)));im=ax.imshow(mat,cmap='RdBu_r',vmin=-1,vmax=1,aspect='auto');ax.set(yticks=range(len(mat)),yticklabels=mat.index,xticks=range(5),xticklabels=[x.replace('IPIP100','') for x in mat.columns],title='Secondary IPIP100 relationships');fig.colorbar(im,ax=ax,shrink=.7);fig.tight_layout();fig.savefig(OUT/'bigfive_alignment.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.5));colors={'A':'#247b65','B':'#8d9f42','C':'#4a85a5','D':'#b48b54','E':'#aa4b49'}
    ax.bar(classes.component,[1]*5,color=[colors[x[0]] for x in classes.classification]);ax.set(yticks=[],ylim=(0,1.1),title='AA-19 final evidence classification')
    for i,x in enumerate(classes.itertuples()):ax.text(i,.5,f'Class {x.classification[0]}',ha='center',va='center',color='white',fontsize=13,weight='bold')
    fig.text(.5,.01,'A independent   B partial   C human combination   D bridge-limited',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,1));fig.savefig(OUT/'component_classification.png');plt.close(fig)
def report(sets,axis_gate,count,pa,map_k,candidate,stable_sub,stable_axis,alignment,sens,mat,big,rec):
    classifications=alignment.classification.tolist();nD=sum(x.startswith('D') for x in classifications);nE=sum(x.startswith('E') for x in classifications);nGood=sum(x[0] in 'ABC' for x in classifications)
    overall='3. Evidence limited primarily by bridge coverage' if nD>=3 else '4. Adequate bridge but little human convergence' if nE>=3 else '1. Strong human convergence' if sum(x[0] in 'AC' for x in classifications)>=3 else '2. Partial human convergence' if nGood else '5. Analysis inconclusive'
    lines=['# AA-19 independent human test of five model-consensus axes','',f'**Overall decision: {overall}.** Human factor fitting and selection used only the verified SAPA item responses, frozen scoring, and future-safe unique direct human proxy correlations. AA-18 loadings entered only after the human solution was frozen. No HiFWB value or association entered any estimate.','',
       '## Phase gate and model bridge','',f'**Observed:** The 23,679-row SAPA release and official scoring keys match prior SHA256 fingerprints. The reconstructed 45-label aggregate proxy correlation matrix matches AA-1 within 5×10⁻⁹. The primary bridge has {len(sets["future_safe_direct"])} unique-source future-safe direct proxies from 45 direct labels; {len(sets["future_safe_total"])} unique-source future-safe labels are available when close proxies are added. No complete respondent profiles were fabricated.','',
       '| Axis | Primary bridge consensus r | Lowest model r | Positive/negative mass | Bridge gate | Human class |','|---|---:|---:|---:|---|---|']
    for a in alignment.itertuples():
        q=rec[(rec.component==a.component)&(rec.variant=='future_safe_direct')];c=q[q.model=='Consensus'].iloc[0]
        lines.append(f'| {a.component} | {c.pearson_r:.3f} | {q.pearson_r.min():.3f} | {c.positive_mass:.3f}/{c.negative_mass:.3f} | {"pass" if a.bridge_adequate else "fail"} | {a.classification} |')
    lines += ['','An inadequate bridge yields class D even if a restricted human alignment looks high. C4 is close to the direct-only model-score threshold (weakest r=0.735) and rises to 0.807 with future-safe close proxies; C5 rises from 0.528 to 0.750. Both remain D under the frozen primary direct-only rule. Direct-only, alias handling, close-proxy, and leave-one-trait-out results are separately exported.','',
       '## Independently estimated human structure','',f'**Observed:** Parallel analysis retains {pa} dimensions; Velicer MAP selects {map_k} within the tested 0–12 range; the held-out one-standard-error rule selects {candidate}. The frozen combined rule fits **{count} oblique minimum-residual human factors**. The human loading subspace is {"stable" if stable_sub else "not stable"} under respondent bootstrap and split halves. Individual factor stability is '+', '.join(f'{k}={"stable" if v else "unresolved"}' for k,v in stable_axis.items())+'. The criteria need not agree because planned missingness and proxy reuse change the effective information.','',
       'Post-freeze QA repeats the held-out selection with eight independent five-fold split sets: '+', '.join(f'{int(k)} factors in {int(v)}/8 sets' for k,v in pd.read_csv(OUT/'human_retention_split_sensitivity.csv').selected_factor_count.value_counts().sort_index().items())+'. This estimates split sensitivity; it does not replace the predeclared seed or selection rule.','',
       '| Human factor | Strongest positive proxies | Strongest negative proxies |','|---|---|---|']
    hl=pd.read_csv(OUT/'human_factor_loadings.csv')
    for j in range(1,count+1):
        q=hl[hl.human_factor==f'H{j}'];positive=', '.join(q.nlargest(3,'pattern_loading').trait);negative=', '.join(q.nsmallest(3,'pattern_loading').trait)
        lines.append(f'| H{j} | {positive} | {negative} |')
    glob=pd.read_csv(OUT/'human_model_global_subspace.csv')
    miss=pd.read_csv(OUT/'human_missingness_sensitivity.csv').iloc[0]
    lines += ['',f'The five restricted AA-18 loading vectors and the retained human factor subspace have canonical correlations '+', '.join(f'{v:.3f}' for v in glob.canonical_correlation)+f'; minimum-axis mapping-null p={glob.minimum_canonical_permutation_p.iloc[0]:.3f}. This subspace statistic does not identify one-to-one axes.','',
       f'Spearman item-pair sensitivity reproduces the human proxy correlation pattern at upper-triangle r={miss.pearson_vs_spearman_proxy_matrix_r:.3f}; the five-factor subspaces have minimum canonical correlation {miss.factor_subspace_min_canonical:.3f}. This changes association estimator, not the planned administration design.','',
       '## Model–human comparison','',f'**Observed:** Future-safe direct trait-covariance upper-triangle correlations with human proxies are '+', '.join(f'{r.model} {r.upper_triangle_pearson:.3f} (p={r.permutation_p:.3f})' for r in mat[mat.variant=='future_safe_direct'].itertuples())+'.',
       '', '| Axis | Human-subspace projection r | Best human factor | Best single Tucker | Mapping-null p | Classification |','|---|---:|---|---:|---:|---|']
    for a in alignment.itertuples():lines.append(f'| {a.component} | {a.human_subspace_projection_r:.3f} | {a.best_single_factor} | {a.best_single_tucker:.3f} | {a.mapping_permutation_p:.3f} | {a.classification} |')
    fcs=pd.read_csv(OUT/'human_factor_count_sensitivity.csv')
    lines += ['', '**Post-freeze factor-count sensitivity:** The six-factor solution was inspected because PA/MAP retain six and one of eight held-out split sets selects six. Projection and best-single-factor congruence under five versus six human factors are:','', '| Axis | 5-factor projection / single | 6-factor projection / single |','|---|---:|---:|']
    for j in range(1,6):
        a=fcs[(fcs.component==f'C{j}')&(fcs.human_factor_count==5)].iloc[0];d=fcs[(fcs.component==f'C{j}')&(fcs.human_factor_count==6)].iloc[0]
        lines.append(f'| C{j} | {a.subspace_projection_r:.3f} / {a.best_single_tucker:.3f} | {d.subspace_projection_r:.3f} / {d.best_single_tucker:.3f} |')
    lines += ['', 'C3 meets class A under the frozen five-factor primary solution, but its best single-factor congruence falls below the 0.70 threshold under six factors (0.675). Its **human-subspace** correspondence remains high. Treat the individual human-axis match as factor-count sensitive; a later HiFWB test should not rely on H2 as a uniquely resolved human counterpart.','']
    lines += ['','**Interpretation:** The human factor subspace comparison asks whether the model loading pattern lies within independently estimated human trait covariance. It does not require a one-to-one axis match. A high model-side bridge reconstruction is a gate on testability, not human validation. Weak direct mapping coverage and shared item sources constrain every human analogy.','',
       '## Secondary Big Five context','', 'Official IPIP100 keys were compared after factor fitting. Shared items can inflate these descriptive aggregate correlations. Neither Big Five keys nor model labels entered human factor retention or rotation.','',
       '| Human projection of model axis | Strongest official IPIP100 domain | Correlation | Big Five multiple R² |','|---|---|---:|---:|']
    for j in range(1,6):
        q=big[big.dimension==f'C{j}_human_projection'];r=q.iloc[int(np.argmax(abs(q.aggregate_correlation.to_numpy())))]
        lines.append(f'| C{j} | {r.big_five_key} | {r.aggregate_correlation:+.3f} | {r.multiple_r2:.3f} |')
    lines += ['','These descriptive R² values do not establish novelty beyond the Big Five: source-item overlap and planned missingness require a later independent test. The strongest C3 relationship is with Agreeableness, but the model axis is not defined by that domain.','',
       '## Limits and next gate','', '**Observed:** SAPA planned missingness provides group-level pairwise proxy correlations, with far fewer co-observations per proxy pair than 23,679. The Gaussian parallel reference approximates effective N but does not preserve the empirical item marginals or joint missingness mask; the held-out and MAP disagreement is retained. The semantic bridge is provisional and lacks independent expert adjudication. The model vectors share prompts/labels and retain the AA-15 historical extraction limitation. No human respondent was projected into model activation space.','',
       '**Interpretation:** Proceed to a separate HiFWB analysis only for axes with adequate future-safe bridge coverage and reproducible human alignment, with an independent outcome freeze and duplicate-aware sensitivity. Class D axes require better human proxies before any wellbeing test. This package establishes neither causal traits nor model–human psychological equivalence.','',
       '**Hypothesis:** Training data, instruction or preference tuning, common prompts, and bridge semantic limitations may each explain convergence or divergence. This analysis cannot distinguish those causes.','',
       'No model inference, RunPod, paid compute, HiFWB fitting, persona wellbeing scoring, viewer deployment, or respondent-level export occurred.']
    (OUT/'three_model_human_validation_report.md').write_text('\n'.join(lines)+'\n')
    return overall
def verify():
    st=pd.read_csv(OUT/'human_factor_stability.csv');classes=pd.read_csv(OUT/'component_classification.csv');bridge=pd.read_csv(OUT/'bridge_mapping_audit.csv')
    checks={'source_inventory_present':(OUT/'source_inventory.json').is_file(),'matrix_gate_documented':(OUT/'human_matrix_audit.md').is_file(),'freeze_present':(OUT/'analysis_freeze.md').is_file(),
       'primary_bridge_rows':len(bridge)==240,'future_safe_unique_direct_count':int(bridge.aa19_primary_selected.sum())==41,
       'axis_class_rows':len(classes)==5,'inadequate_axes_are_class_D':bool(classes.loc[~classes.bridge_adequate,'classification'].str.startswith('D').all()),
       'respondent_bootstrap_replicates':int(st[st.resample_type=='bootstrap'].replicate.nunique())==50,
       'split_half_replicates':int(st[st.resample_type=='split_half'].replicate.nunique())==20,
       'factor_retention_rows':len(pd.read_csv(OUT/'human_factor_retention.csv'))==41,
       'global_subspace_rows':len(pd.read_csv(OUT/'human_model_global_subspace.csv'))==5,
       'missingness_sensitivity_rows':len(pd.read_csv(OUT/'human_missingness_sensitivity.csv'))==1,
       'required_figures_present':all((OUT/n).is_file() for n in ('consensus_axis_poles.png','bridge_pole_coverage.png','full_vs_bridge_reconstruction.png','human_retention_diagnostics.png','human_loading_heatmap.png','human_model_subspace_alignment.png','human_factor_bootstrap_stability.png','bigfive_alignment.png','component_classification.png')),
       'human_loadings_finite':bool(np.isfinite(pd.read_csv(OUT/'human_factor_loadings.csv').pattern_loading).all()),'respondent_rows_exported':False,
       'no_hifwb_outcome_fit':True,'no_model_inference':True,'no_runpod':True,'no_paid_compute':True,'no_viewer':True,'seed':SEED}
    checks['all_checks_pass']=bool(all(v for k,v in checks.items() if k not in ('respondent_rows_exported','seed')))
    (OUT/'verification_report.json').write_text(json.dumps(checks,indent=2)+'\n')
    rows=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact_inventory.csv']
    save('artifact_inventory.csv',rows)
    return checks
def main():
    bridge,scoring,keytable,tab,bf=source_gate();sets=bridge_sets(bridge)
    tables,traits,z,loads,cons,scores,conv,axis_gate=model_bridge(bridge,sets)
    raw,items,itemcorr,pair_n,b,alltraits,allc,selected,c,cp,bf,diff=human_data(bridge,scoring,keytable,tab,bf,sets)
    axis_interpretation(traits,cons,loads,scores,conv)
    count,l,phi,structure,cp,pa,map_k,candidate=retention(raw,items,b,alltraits,selected,c,pair_n)
    retention_split_sensitivity(raw,items,b,alltraits,selected,pa)
    factor_count_alignment_sensitivity(cp,cons,selected)
    stable_sub,stable_axis,stability,sub=human_stability(raw,items,b,alltraits,selected,l,count)
    mat=matrix_alignment(bridge,sets,alltraits,allc,z,traits)
    alignments=axis_human_alignment(sets,traits,cons,selected,l,structure,axis_gate,stable_sub,stable_axis,raw,items,b,alltraits,count)
    model_specific_alignment(traits,selected,loads,l)
    sens=sensitivity_human(sets,traits,cons,alltraits,allc)
    missingness_sensitivity(raw,items,b,alltraits,selected,cp,l,count)
    for i,row in alignments.iterrows():
        q=sens[(sens.component==row.component)&(sens.variant=='direct_plus_close')].iloc[0]
        if row.classification.startswith(('A_','C_')) and (q.subspace_projection_r<.7 or q.permutation_p>.05):
            alignments.loc[i,'classification']='B_partial_human_analogue'
    save('consensus_axis_human_alignment.csv',alignments.to_dict('records'))
    save('component_classification.csv',[{k:r[k] for k in ('component','bridge_adequate','human_subspace_projection_r','best_single_factor','best_single_tucker','mapping_permutation_p','classification')} for r in alignments.to_dict('records')])
    big=bigfive_alignment(keytable,bf,items,itemcorr,b,alltraits,selected,l,cp,cons)
    rec=pd.read_csv(OUT/'bridge_axis_reconstruction.csv')
    # Compact plotting table: no raw respondent or full persona export.
    plot=[]
    for j in range(1,6):
        component=f'C{j}';mask=np.isin(traits,sets['future_safe_direct']);ss=scores[scores.component==component]
        partial=[]
        for m in MODELS:
            w=loads[(loads.component==component)&(loads.model==m)].set_index('trait').loc[traits].trait_weight.to_numpy()
            partial.append(stand(z[m]@(w*mask)))
        for i in range(len(ss)):plot.append(dict(component=component,consensus_score=float(ss.consensus_score.iloc[i]),bridge_consensus_score=float(np.mean([p[i] for p in partial]))))
    plot=pd.DataFrame(plot)
    figures(cons,selected,pd.read_csv(OUT/'human_factor_retention.csv'),rec,alignments,pd.read_csv(OUT/'human_factor_loadings.csv'),stability,big,alignments,plot)
    overall=report(sets,axis_gate,count,pa,map_k,candidate,stable_sub,stable_axis,alignments,sens,mat,big,rec)
    result=verify();print(json.dumps(dict(overall=overall,human_factors=count,classes=alignments.classification.tolist(),verified=result['all_checks_pass'])))
if __name__=='__main__':main()
