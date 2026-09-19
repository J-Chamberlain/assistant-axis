#!/usr/bin/env python3
"""Refit affected HUMAN portions only; immutable legacy functions, one masking patch.
No legacy main(), model matrices, persona projections, or viewer functions run.
"""
import argparse,ast,copy,textwrap,tempfile
from types import SimpleNamespace
from aa26_common import *
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score,mean_squared_error,mean_absolute_error
from scipy.stats import pearsonr,spearmanr
from factor_analyzer import FactorAnalyzer
import factor_analyzer.factor_analyzer as famodule
from sklearn.utils.validation import check_array as sklearn_check_array

# Existing factor_analyzer calls the pre-1.6 sklearn argument name. Semantic-only shim.
def check_array_compat(*args,**kw):
    if 'force_all_finite' in kw:kw['ensure_all_finite']=kw.pop('force_all_finite')
    return sklearn_check_array(*args,**kw)
famodule.check_array=check_array_compat

FOLDERS={20:'aa20_consensus_axes_hifwb',21:'aa21_bigfive_hifwb_persona_projection',22:'aa22_direct_trait_hifwb_bridge',23:'aa23_bigfive_residual_hifwb_bridge',24:'aa24_model_consensus_hifwb_projection'}

def load_functions(stage,tmp,rawdir):
    filename='run_bigfive_hifwb_projection.py' if stage==21 else 'run_analysis.py'
    src=blob('research/outputs/'+FOLDERS[stage]+'/'+filename).decode()
    tree=ast.parse(src);defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
    funcs=[]
    for n in defs:
        if n.name in ['trait_matrix','score_traits']:
            text=ast.get_source_segment(src,n)
            assert 'a[n==0]=np.nan' in text and ('observed.append(n>0)' in text or 'obs.append(n>0)' in text)
            text=text.replace('a[n==0]=np.nan','a[n<min(2,len(ids))]=np.nan').replace('observed.append(n>0)','observed.append(np.isfinite(a))').replace('obs.append(n>0)','obs.append(np.isfinite(a))')
            n=ast.parse(text).body[0]
        if n.name!='main':funcs.append(n)
    stageout=OUT/'dependency_repair'/f'AA{stage}';stageout.mkdir(exist_ok=True)
    env=dict(np=np,pd=pd,Path=Path,json=json,hashlib=__import__('hashlib'),os=os,pearsonr=pearsonr,spearmanr=spearmanr,Ridge=Ridge,r2_score=r2_score,mean_squared_error=mean_squared_error,mean_absolute_error=mean_absolute_error,FactorAnalyzer=FactorAnalyzer,ROOT=ROOT,OUT=stageout,RAW=Path(rawdir),SEED=20260915,AA18=tmp/'AA18',AA19=tmp/'AA19',AA20=tmp/'AA20',FREEZE=tmp/'wellbeing_item_freeze.csv',KEYS=BFKEYS,DOMAINS=['Agreeableness','Conscientiousness','Extraversion','Openness','Emotional_Stability'],HUMAN_NAMES=['agreeableness','conscientiousness','extraversion','openness','emotional_stability'],MODELS=['Intercept','BigFive','C1_C3','BigFive_plus_C1_C3','HumanFactors5','BigFive_plus_HumanFactors5'])
    exec(compile(ast.Module(body=funcs,type_ignores=[]),str(stageout/'legacy_function_copy'), 'exec'),env)
    return src,env,tree

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',required=True);args=ap.parse_args();d=Data(args.data_dir)
    tmp=Path(tempfile.mkdtemp(prefix='aa26_human_refit_inputs_'))
    for folder,name in [('AA18','consensus_trait_loadings.csv'),('AA19','human_factor_loadings.csv'),('AA19','bridge_mapping_audit.csv')]:
        (tmp/folder).mkdir(exist_ok=True);srcfolder='aa18_three_model_consensus_trait_structure' if folder=='AA18' else 'aa19_human_consensus_factor_validation'
        (tmp/folder/name).write_bytes(blob('research/outputs/'+srcfolder+'/'+name))
    (tmp/'wellbeing_item_freeze.csv').write_bytes(blob('research/outputs/sapa_hifwb_reproducibility/wellbeing_item_freeze.csv'))
    corrected=d.human_scores(2);summary=[]
    # AA-20: all original aggregate human primary/sensitivity blocks, with only proxy mask corrected.
    src,e,tree=load_functions(20,tmp,args.data_dir)
    raw=pd.DataFrame(d.raw,columns=d.ids);primary=d.bridge.copy();traits=primary.model_trait.tolist();key=d.key
    bridge=read('aa19_human_consensus_factor_validation/bridge_mapping_audit.csv');close=bridge[bridge.mapping_tier.isin(['direct','close'])&bridge.overlap_with_hifwb_item_ids.isna()].copy()
    close=close.loc[close.groupby('exact_source_group').model_trait.transform(lambda x:x==sorted(x)[0])].sort_values('model_trait')
    outcomes=pd.read_csv(tmp/'wellbeing_item_freeze.csv');outcomes=outcomes[outcomes.tier=='DIRECT'];outitems=outcomes.item_id.tolist()
    weights,_,_=e['fixed_weights'](traits);y,_,_=e['outcome_score'](raw,outitems)
    frame,cov,T,O,B,Bn=e['scores'](raw,primary,key,np.arange(d.n),weights)
    eligible=e['eligibility'](y,O,weights,Bn)&np.isfinite(frame[['C1','C2','C3','H1','H2','H3','H4','H5']]).all(axis=1)
    assert np.array_equal(eligible,corrected['common']) and np.allclose(T,corrected['T'],equal_nan=True,atol=1e-10)
    e.update(raw=raw,primary=primary,close=close,traits=traits,key=key,outcomes=outcomes,outitems=outitems,weights=weights,y=y,frame=frame,cov=cov,T=T,O=O,B=B,Bn=Bn,eligible=eligible)
    # Exact source block ends before any plot/report/main-side effects.
    start=src.index(' rel=[]',src.index('def main():'));end=src.index(' make_figures(',start)
    exec(compile(textwrap.dedent(src[start:end]),'AA20_aggregate_human_block','exec'),e)
    summary.append(dict(analysis='AA20',eligible_n=int(eligible.sum()),test_n=len(e['te']),delta_r2=float(e['obs']),ci_low=float(e['delta_ci'][0]),ci_high=float(e['delta_ci'][1]),decision=e['decision']))
    print('AA20 corrected aggregate refit complete',flush=True)
    # AA-22 and AA-23: execute their human-only AST main prefix, stop before any projection.
    for stage in [22,23]:
        src,env,tree=load_functions(stage,tmp,args.data_dir)
        mainnode=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');nodes=[]
        for n in mainnode.body:
            calls=[x for x in ast.walk(n) if isinstance(x,ast.Call)]
            if any(isinstance(x.func,ast.Name) and x.func.id=='project_residual_personas' for x in calls):break
            if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='proj' for t in n.targets):break
            nodes.append(n)
        assert all('project_residual_personas(' not in ast.unparse(n) for n in nodes)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),f'AA{stage}_human_prefix','exec'),env)
        result=env['fitres'];delta=float(result.iloc[-1].r2-result.iloc[0].r2)
        summary.append(dict(analysis=f'AA{stage}',eligible_n=int(env['eligible'].sum()),test_n=len(env['te']),delta_r2=delta,ci_low=float(env['lo']),ci_high=float(env['hi']),decision='increment interval excludes zero' if env['lo']>0 else 'increment not established'))
        print(f'AA{stage} corrected human refit complete',flush=True)
    # AA-24: same frozen axes, historical full-cohort item scaling, corrected masks.
    src,a,tree=load_functions(24,tmp,args.data_dir);x0=corrected;ids=np.random.default_rng(20260915).permutation(d.n);tr0,va0,te0=np.split(ids,[int(.6*d.n),int(.8*d.n)])
    tr,va,te=[ix[x0['common'][ix]] for ix in [tr0,va0,te0]];pred={};rows=[]
    for name,X in [('BigFive',x0['B']),('Consensus_C1_C3',x0['A'][:,:3]),('BigFive_plus_Consensus_C1_C3',np.column_stack([x0['B'],x0['A'][:,:3]]))]:
        p,alpha,m=a['fit_model'](X,x0['y'],tr,va,te);pred[name]=p;rows.append(dict(model=name,train_n=len(tr),validation_n=len(va),test_n=len(te),alpha=alpha,**a['metrics'](x0['y'][te],p)))
    save(a['OUT']/'human_model_comparison.csv',rows);lo,hi=a['bootstrap_delta'](x0['y'][te],pred['BigFive'],pred['BigFive_plus_Consensus_C1_C3']);delta=rows[-1]['r2']-rows[0]['r2']
    save(a['OUT']/'incremental_prediction_bootstrap.csv',[dict(observed_delta_r2=delta,ci_low=lo,ci_high=hi)])
    ws=[]
    for fitname,fit in [('full_corrected_common',np.flatnonzero(x0['common'])),('train_validation',np.r_[tr,va])]:
        X=zfit(x0['A'][:,:3],fit)[0];Y=zfit(x0['y'][:,None],fit)[0][:,0];m=Ridge(alpha=0).fit(X[fit],Y[fit]);ws.extend(dict(fit=fitname,axis=f'C{i+1}',weight=float(w)) for i,w in enumerate(m.coef_))
    save(a['OUT']/'human_axis_coefficients.csv',ws);summary.append(dict(analysis='AA24',eligible_n=int(x0['common'].sum()),test_n=len(te),delta_r2=delta,ci_low=lo,ci_high=hi,decision='increment interval excludes zero' if lo>0 else 'increment not established'))
    # AA-21 common sensitivity ONLY. Primary fit and saved persona scores are not run/read.
    src,e21,tree=load_functions(21,tmp,args.data_dir);fit=np.flatnonzero(x0['common']);X=zfit(x0['B'],fit)[0][fit];Y=zfit(x0['y'][:,None],fit)[0][fit,0]
    model,coefs,metrics=e21['fit_and_validate'](X,Y,forced_alpha=100)
    coefs.to_csv(e21['OUT']/'corrected_common_coefficients.csv',index=False);jsave(e21['OUT']/'corrected_common_metrics.json',metrics)
    summary.append(dict(analysis='AA21_common',eligible_n=len(fit),test_n=metrics['test_n'],delta_r2=None,ci_low=None,ci_high=None,decision='corrected common-sensitivity refit; primary unchanged',r2=metrics['test_r2']))
    save(OUT/'dependency_repair'/'corrected_analysis_summary.csv',summary)
    save(OUT/'dependency_repair'/'refit_source_inventory.csv',list(SOURCES.values()))
    jsave(OUT/'dependency_repair'/'refit_verification.json',dict(status='PASS',measurement_freeze_commit='51e5f52',legacy_base=BASE,only_patch='multi-item trait proxy minimum changes 1 to 2; genuine single item stays 1',human_refits_completed=['AA20','AA22','AA23','AA24','AA21_common'],unaffected_analyses_not_run=['AA16','AA17','AA18','AA19','AA21_primary','AA25'],legacy_human_function_code_used=True,legacy_main_not_called=True,aa20_all_original_aggregate_human_blocks_rerun=True,persona_projections_run=False,original_outputs_modified=False,respondent_rows_exported=False,whole_cohort_scaling_retained_for_repair_attribution=['AA22','AA23','AA24','AA21_common'],factor_analyzer_shim='rename force_all_finite to ensure_all_finite for existing sklearn API'))
    report=['# Affected human dependency refits','', 'All five flagged dependencies materially changed and were refit under the frozen two-item multi-item-proxy rule. These are corrected analyses, not verification of unchanged scores. Original artifacts remain historical.','', '| Analysis | Corrected eligible N | Test N | Delta R² | 95% paired interval | Decision |','|---|---:|---:|---:|---|---|']
    for r in summary:
        delta='' if r['delta_r2'] is None else f"{r['delta_r2']:+.4f}";ci='' if r['ci_low'] is None else f"[{r['ci_low']:+.4f}, {r['ci_high']:+.4f}]"
        report.append(f"| {r['analysis']} | {r['eligible_n']} | {r['test_n']} | {delta} | {ci} | {r['decision']} |")
    report += ['',f"AA-21 common sensitivity held-out R² is {metrics['test_r2']:.4f}; its primary coefficients, primary human performance, and persona constructions were not rerun.",'', 'AA-20 repeats the original aggregate association, bootstrap, indicator, repeated-split, factor-count/C3, bridge, and dominant-trait checks. AA-22/23 repeat the human fit and human full-sample weight portions. AA-24 repeats human predictions and human axis-weight sensitivity. No saved model matrices were loaded and no persona was rescored. Consequently, old persona transports and correlations dependent on changed human weights remain withdrawn/stale; this report does not claim those downstream products have been repaired. Original AA-12/13 withdrawals are also unchanged.','', 'The repair isolates eligibility: historical full-cohort item standardization remains in AA-22/23/24 and AA-21 common sensitivity, as in their source implementations. New AA-26 candidate evaluation uses training-only predictor preprocessing. Fixed-test bootstrap intervals condition on fitted predictions, not full refitting. The AA-20 factor_analyzer compatibility shim only renames an sklearn argument; it does not alter the estimator.','', 'This report is generated before candidate-effect interpretation. CPU-only; no RunPod/paid compute/GPU/model inference/viewer changes.']
    (OUT/'dependency_repair'/'dependency_refit_report.md').write_text('\n'.join(report)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
