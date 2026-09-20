#!/usr/bin/env python3
"""Nested held-out human profile reconstruction on frozen, disjoint measures."""
import argparse,time,gc
from sklearn.model_selection import KFold,train_test_split
from aa26_common import *
from masked_ridge import *

def display_concept(s):
    return 'Behavioral and emotional self-regulation' if s['name']=='PS:PS:S' else s['concept']

def paired_bootstrap(Y,predictions,reference,reps=1000):
    """Joint respondent bootstrap of OOF errors; predictions are held fixed."""
    obs=np.isfinite(Y);yy=np.nan_to_num(Y);n=len(Y)
    e0=np.where(obs,(Y-reference)**2,0)
    diff={name:e0-np.where(obs,(Y-p)**2,0) for name,p in predictions.items()}
    rng=np.random.default_rng(SEED+800);samples={k:[] for k in diff}
    for start in range(0,reps,25):
        size=min(25,reps-start);w=rng.multinomial(n,np.full(n,1/n),size=size).astype(float)
        counts=w@obs.astype(float);sy=w@yy;sy2=w@(yy*yy);sst=sy2-sy*sy/np.maximum(counts,1)
        for name,delta in diff.items():samples[name].extend(np.mean((w@delta)/sst,axis=1).tolist())
    return {name:dict(ci_low=float(np.quantile(v,.025)),ci_high=float(np.quantile(v,.975)),positive_fraction=float(np.mean(np.array(v)>0))) for name,v in samples.items()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',required=True);args=ap.parse_args();started=time.time()
    freeze=json.loads((OUT/'repair/measurement_freeze.json').read_text());d=Data(args.data_dir)
    specs=freeze['bridge']+freeze['bigfive']+freeze['candidates'];nb=46;nc=len(freeze['candidates']);candidate_indices=list(range(nb,nb+nc));base=list(range(nb))
    Y,_=d.score(freeze['targets']);cohort=np.flatnonzero(np.isfinite(Y).sum(1)>=5);Yc=Y[cohort];n=len(cohort);ny=Y.shape[1]
    assert len(cohort)==freeze['eligible_profile_n'] and sha((np.isfinite(Y).sum(1)>=5).tobytes())==json.loads((OUT/'repair/target_validity_gate.json').read_text())['target_eligibility_sha256']
    bf_y,_=d.score(freeze['bigfive'],item_z=True);h_y,_=d.score([freeze['hifwb']],item_z=True)
    secondary_bridge=[]
    for s in freeze['bridge']:
        ids=[i for i in s['items'] if i not in d.bfi]
        if len(ids)<2:continue
        signs=dict(zip(s['items'],s['signs']));secondary_bridge.append(spec(s['name'],ids,[signs[i] for i in ids]))
    assert not set(i for s in secondary_bridge for i in s['items'])&d.bfi
    bfspec=secondary_bridge+freeze['candidates'];bfbase=list(range(len(secondary_bridge)));bfcand=list(range(len(secondary_bridge),len(bfspec)))
    save(OUT/'repair/bigfive_secondary_bridge.csv',[dict(proxy=s['name'],items=';'.join(s['items']),minimum_observed=2) for s in secondary_bridge])
    P={};BF={};H={};mu=np.zeros((n,ny));sd=np.ones((n,ny));fold_rows=[];selection=[];redundancy=[];fold_metric=[];available={}
    def assign(dest,name,ix,p,width):
        if name not in dest:dest[name]=np.full((n,width),np.nan,dtype=np.float32)
        dest[name][ix]=p
    for fold,(ti,vi) in enumerate(KFold(5,shuffle=True,random_state=SEED).split(cohort),1):
        tr,te=cohort[ti],cohort[vi];begin=time.time();inner=[];bfinner=[];hinner=[]
        for it,iv in KFold(3,shuffle=True,random_state=SEED+fold).split(tr):
            inner.append(Cache(d,specs,Y,tr[it],tr[iv]))
            bfinner.append(Cache(d,bfspec,bf_y,tr[it],tr[iv]))
            hinner.append(Cache(d,specs,h_y,tr[it],tr[iv]))
        outer=Cache(d,specs,Y,tr,te);bfouter=Cache(d,bfspec,bf_y,tr,te);houter=Cache(d,specs,h_y,tr,te);mu[vi]=outer.mu;sd[vi]=outer.sd
        print(f'outer fold {fold}: caches ready ({time.time()-begin:.1f}s)',flush=True)
        groups,pairs=residual_groups(d,specs,tr,nb,nc,.8)
        redundancy.extend(dict(outer_fold=fold,**p) for p in pairs)
        for label,features in [('bridge_only',list(range(41))),('bigfive_only',list(range(41,46))),('bridge_plus_bigfive',base)]:
            score,alpha=choose(inner,features);prediction=outer.predict(features,alpha);assign(P,label,vi,prediction,ny)
            fold_metric.append(dict(fold=fold,analysis=label,macro_r2=float(np.mean(r2_dimensions(Y[te],prediction)[0])),alpha=alpha))
        paths={'distinct':greedy(inner,base,candidate_indices,groups),'unrestricted':greedy(inner,base,candidate_indices,groups,distinct=False)}
        for threshold in [.7,.9]:
            g,pp=residual_groups(d,specs,tr,nb,nc,threshold);paths[f'residual_{threshold:.2f}']=greedy(inner,base,candidate_indices,g)
        for label,path in paths.items():
            available.setdefault(label,[]).append(len(path)-1)
            for step in path:
                name=f'{label}_k{step["k"]}';features=base+[candidate_indices[j] for j in step['selected']];prediction=outer.predict(features,step['alpha']);assign(P,name,vi,prediction,ny)
                rr=r2_dimensions(Y[te],prediction)[0]
                fold_metric.append(dict(fold=fold,analysis=name,macro_r2=float(np.mean(rr)),alpha=step['alpha']))
                selection.append(dict(outer_fold=fold,path_type=label,k=step['k'],added_family='' if step['added'] is None else freeze['candidates'][step['added']]['name'],selected_families=';'.join(freeze['candidates'][j]['name'] for j in step['selected']),inner_macro_r2=step['score'],inner_increment=step['increment'],alpha=step['alpha'],outer_macro_r2=float(np.mean(rr)),distinct_group_count=len(set(groups))))
                if label=='distinct':
                    for caches,cache,bidx,cidx,store,w in [(bfinner,bfouter,bfbase,bfcand,BF,5),(hinner,houter,base,candidate_indices,H,1)]:
                        features=bidx+[cidx[j] for j in step['selected']];_,alpha=choose(caches,features);assign(store,f'k{step["k"]}',vi,cache.predict(features,alpha),w)
        for j,s in enumerate(freeze['candidates']):
            name=f'solo_{j}';features=base+[candidate_indices[j]];_,alpha=choose(inner,features);assign(P,name,vi,outer.predict(features,alpha),ny)
            for caches,cache,bidx,cidx,store,w in [(bfinner,bfouter,bfbase,bfcand,BF,5),(hinner,houter,base,candidate_indices,H,1)]:
                features=bidx+[cidx[j]];_,alpha=choose(caches,features);assign(store,name,vi,cache.predict(features,alpha),w)
        fold_rows.append(dict(fold=fold,train_n=len(tr),test_n=len(te),train_index_hash=sha(tr.tobytes()),test_index_hash=sha(te.tobytes()),distinct_max_k=len(paths['distinct'])-1,seconds=time.time()-begin))
        print(f'outer fold {fold} complete ({time.time()-begin:.1f}s), distinct max k={len(paths["distinct"])-1}',flush=True)
        del inner,bfinner,hinner,outer,bfouter,houter;gc.collect()
    # An admissible path size needs held-out predictions in all five folds.
    feasible=min(available['distinct']);baseline=P['bridge_plus_bigfive'];base_r=float(np.mean(r2_dimensions(Yc,baseline)[0]));results=[]
    yz=(Yc-mu)/sd
    for name,p in P.items():
        complete=bool(np.isfinite(p).all())
        if not complete:continue
        rr,counts=r2_dimensions(Yc,p);cc=correlation_dimensions(Yc,p);rowcorr=row_correlation(yz,(p-mu)/sd)
        results.append(dict(analysis=name,respondents=n,dimensions=ny,observed_target_cells=int(np.isfinite(Yc).sum()),macro_r2=float(np.mean(rr)),macro_dimension_r=float(np.nanmean(cc)),mean_within_person_profile_r=float(np.nanmean(rowcorr)),profile_r_valid_n=int(np.isfinite(rowcorr).sum()),delta_r2_vs_bridge_bigfive=float(np.mean(rr)-base_r)))
    metrics=pd.DataFrame(results).set_index('analysis')
    # Bootstrap all singleton candidates and admissible main curve points, holding OOF fits fixed.
    bootpred={name:P[name] for name in [*[f'distinct_k{k}' for k in range(1,feasible+1)],*[f'solo_{j}' for j in range(nc)]]}
    print('outer validation complete; paired respondent bootstrap begins',flush=True)
    ci=paired_bootstrap(Yc,bootpred,baseline)
    sec_metrics=[]
    for outcome,yy,store in [('BigFive',bf_y[cohort],BF),('HiFWB',h_y[cohort],H)]:
        base_sec=float(np.nanmean(r2_dimensions(yy,store['k0'])[0]))
        sec_ci=paired_bootstrap(yy,{name:p for name,p in store.items() if name!='k0' and np.isfinite(p).all()},store['k0'])
        for name,p in store.items():
            if not np.isfinite(p).all():continue
            rr,nn=r2_dimensions(yy,p);sec_metrics.append(dict(outcome=outcome,analysis=name,macro_r2=float(np.nanmean(rr)),delta_r2=float(np.nanmean(rr)-base_sec),delta_ci_low=sec_ci[name]['ci_low'] if name!='k0' else 0.,delta_ci_high=sec_ci[name]['ci_high'] if name!='k0' else 0.,observed_cells=int(np.isfinite(yy).sum()),observed_respondents=int(np.isfinite(yy).any(1).sum())))
    save(OUT/'secondary_outcome_comparison.csv',sec_metrics)
    # Full-cohort internal CV determines a transparent final ordering, NOT fixed-set external validation.
    full=[]
    for it,iv in KFold(3,shuffle=True,random_state=SEED+99).split(cohort):full.append(Cache(d,specs,Y,cohort[it],cohort[iv]))
    groups,fullpairs=residual_groups(d,specs,cohort,nb,nc,.8);finalpath=greedy(full,base,candidate_indices,groups);finalorder=finalpath[-1]['selected']
    save(OUT/'candidate_redundancy.csv',fullpairs);save(OUT/'outer_training_redundancy.csv',redundancy)
    # Additional split selection stability; these internal validation values are not claimed test performance.
    stab=[]
    for rep in range(20):
        train,val=train_test_split(cohort,test_size=.3,random_state=SEED+1000+rep);cache=Cache(d,specs,Y,train,val);g,_=residual_groups(d,specs,train,nb,nc,.8);path=greedy([cache],base,candidate_indices,g)
        for step in path[1:]:stab.append(dict(replicate=rep+1,k=step['k'],family=freeze['candidates'][step['added']]['name']))
        if (rep+1)%5==0:print(f'selection stability {rep+1}/20 complete',flush=True)
        del cache;gc.collect()
    save(OUT/'selection_stability_runs.csv',stab)
    outersteps=[r for r in selection if r['path_type']=='distinct' and r['k']>0]
    stability=[]
    for j,s in enumerate(freeze['candidates']):
        a=[r for r in outersteps if r['added_family']==s['name']];b=[r for r in stab if r['family']==s['name']]
        stability.append(dict(family=s['name'],outer_selected_top5_frequency=sum(r['k']<=5 for r in a)/5,outer_selected_first_frequency=sum(r['k']==1 for r in a)/5,outer_mean_rank=float(np.mean([r['k'] for r in a])) if a else np.nan,split_selected_top5_frequency=sum(r['k']<=5 for r in b)/20,split_selected_first_frequency=sum(r['k']==1 for r in b)/20,split_mean_rank=float(np.mean([r['k'] for r in b])) if b else np.nan,outer_folds=5,split_replicates=20))
    save(OUT/'selection_stability.csv',stability)
    solo=[];dim=[];rr0=r2_dimensions(Yc,baseline)[0]
    for j,s in enumerate(freeze['candidates']):
        name=f'solo_{j}';rr=r2_dimensions(Yc,P[name])[0];sec={r['outcome']:r for r in sec_metrics if r['analysis']==name}
        old=[freeze['candidates'][k]['name'] for k in finalorder[:finalorder.index(j)]] if j in finalorder else []
        related=[abs(r['residual_r']) for r in fullpairs if r['residual_r'] is not None and ((r['candidate_a']==s['name'] and r['candidate_b'] in old) or (r['candidate_b']==s['name'] and r['candidate_a'] in old))]
        o=d.score([s])[1][:,0]>=2
        solo.append(dict(family=s['name'],concept=display_concept(s),rank_distinct_final=finalorder.index(j)+1 if j in finalorder else np.nan,standalone_delta_profile_r2=float(np.mean(rr)-base_r),standalone_ci_low=ci[name]['ci_low'],standalone_ci_high=ci[name]['ci_high'],standalone_delta_macro_r=float(metrics.loc[name,'macro_dimension_r']-metrics.loc['bridge_plus_bigfive','macro_dimension_r']),dimensions_improved=int((rr>rr0).sum()),top_improved_dimensions=';'.join(freeze['targets'][i]['name'] for i in np.argsort(rr-rr0)[-5:][::-1]),bigfive_secondary_delta_r2=sec['BigFive']['delta_r2'],hifwb_secondary_delta_r2=sec['HiFWB']['delta_r2'],respondent_coverage_n=int(o.sum()),missing_fraction=float(1-o.mean()),item_count=len(s['items']),maximum_residual_r_with_preceding=max(related) if related else 0.,outer_top5_frequency=stability[j]['outer_selected_top5_frequency'],split_top5_frequency=stability[j]['split_selected_top5_frequency'],status='distinct_final_order' if j in finalorder else 'redundant_group_alternative'))
        for k,t in enumerate(freeze['targets']):dim.append(dict(family=s['name'],target=t['name'],baseline_r2=rr0[k],candidate_r2=rr[k],delta_r2=rr[k]-rr0[k]))
    save(OUT/'candidate_dimension_ranking.csv',sorted(solo,key=lambda r:r['rank_distinct_final'] if np.isfinite(r['rank_distinct_final']) else 999))
    save(OUT/'dimension_improvement_by_candidate.csv',dim)
    # Conditional increments are attributed only to folds where a family was selected.
    inc=[]
    for r in outersteps:
        prev=next(x for x in selection if x['outer_fold']==r['outer_fold'] and x['path_type']=='distinct' and x['k']==r['k']-1)
        inc.append(dict(family=r['added_family'],outer_fold=r['outer_fold'],k=r['k'],preceding_families=prev['selected_families'],inner_increment=r['inner_increment'],heldout_increment_r2=r['outer_macro_r2']-prev['outer_macro_r2'],heldout_macro_r2=r['outer_macro_r2']))
    save(OUT/'incremental_gain_by_candidate.csv',inc)
    bestk=max(range(1,feasible+1),key=lambda k:metrics.loc[f'distinct_k{k}','macro_r2']);best=float(metrics.loc[f'distinct_k{bestk}','macro_r2']);total=best-base_r
    tolerances=[]
    for tol in [.005,.01,.02]:
        k=0 if total<=0 else next(k for k in range(1,feasible+1) if metrics.loc[f'distinct_k{k}','macro_r2']>=best-tol)
        perf=base_r if k==0 else float(metrics.loc[f'distinct_k{k}','macro_r2']);tolerances.append(dict(tolerance_absolute_r2=tol,smallest_k=k,performance=perf,best_admissible_k=bestk,best_performance=best,fraction_of_best_improvement=(perf-base_r)/total if total>0 else 0,baseline_within_tolerance=base_r>=best-tol))
    minimum=next(r['smallest_k'] for r in tolerances if r['tolerance_absolute_r2']==.01)
    fraction95=0 if total<=0 else next(k for k in range(1,feasible+1) if (metrics.loc[f'distinct_k{k}','macro_r2']-base_r)>=.95*total)
    curve=[]
    for k in range(9):
        name=f'distinct_k{k}'
        if k>feasible:curve.append(dict(k=k,status='NOT_ADMISSIBLE_IN_ALL_OUTER_FOLDS'));continue
        perf=float(metrics.loc[name,'macro_r2']);interval=ci[name] if k else dict(ci_low=0,ci_high=0)
        curve.append(dict(k=k,status='NESTED_HELDOUT_ADAPTIVE_DISTINCT_PATH',profile_r2=perf,delta_profile_r2=perf-base_r,delta_ci_low=interval['ci_low'],delta_ci_high=interval['ci_high'],within_primary_tolerance=perf>=best-.01,fraction_of_best_gain=(perf-base_r)/total if total>0 else 0))
    save(OUT/'minimal_set_curve.csv',curve);save(OUT/'minimal_set_tolerance_sensitivity.csv',tolerances)
    selected=[]
    for rank,j in enumerate(finalorder,1):
        s=freeze['candidates'][j];selected.append(dict(rank=rank,concept=display_concept(s),family=s['name'],official_key=s['official_key'],source_items=';'.join(s['items']),signs=';'.join(f'{i}:{sg:+d}' for i,sg in zip(s['items'],s['signs'])),in_top_five=rank<=5,in_primary_minimal_set=rank<=minimum,in_95percent_gain_set=rank<=fraction95,measurement='existing multi-item subset; >=2 observed; no model-side evidence'))
    save(OUT/'selected_question_or_construct_set.csv',selected)
    save(OUT/'profile_reconstruction_comparison.csv',results)
    save(OUT/'outer_fold_metrics.csv',fold_metric);save(OUT/'outer_fold_selection.csv',selection);save(OUT/'split_manifest.csv',fold_rows)
    sensitivity=[r for r in results if r['analysis'].startswith(('unrestricted','residual_'))];save(OUT/'distinctness_sensitivity.csv',sensitivity)
    save(OUT/'analysis_source_inventory.csv',list(SOURCES.values()))
    summary=dict(status='COMPLETED',target_freeze_commit='51e5f52',dependency_refit_commit='cf6ce5b',n=n,dimensions=ny,candidate_families=nc,feasible_distinct_max_k=feasible,baseline_macro_r2=base_r,best_k=bestk,best_macro_r2=best,best_gain=total,primary_minimal_k=minimum,k_capturing_95percent_gain=fraction95,final_order=[display_concept(freeze['candidates'][j]) for j in finalorder],wall_seconds=time.time()-started,model_inference=False,runpod=False,paid_compute=False,raw_rows_exported=False,interpretation='OOF values validate adaptive selection paths, not independently fixed final full-data label sets')
    jsave(OUT/'information_gain_summary.json',summary)
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
