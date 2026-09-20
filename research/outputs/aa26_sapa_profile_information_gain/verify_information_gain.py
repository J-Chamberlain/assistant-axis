#!/usr/bin/env python3
"""Focused measurement, numerical estimator, artifact, and scope verification."""
import argparse,ast,sys,difflib
from sklearn.linear_model import Ridge
from aa26_common import *
from masked_ridge import Cache,r2_dimensions,residual_groups

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',required=True);a=ap.parse_args();checks={}
    def check(name,value):
        checks[name]=bool(value)
        assert checks[name],name
    d=Data(a.data_dir);f=json.loads((OUT/'repair/measurement_freeze.json').read_text());g=json.loads((OUT/'repair/target_validity_gate.json').read_text());s=json.loads((OUT/'information_gain_summary.json').read_text())
    check('freeze_bytes_match_prerun_hash',sha((OUT/'repair/measurement_freeze.json').read_bytes())==g['target_spec_sha256'])
    Y,N=d.score(f['targets']);mask=np.isfinite(Y);cohort=mask.sum(1)>=5
    check('target_mask_hash',sha(mask.tobytes())==g['target_observation_mask_sha256'])
    check('cohort_hash',sha(cohort.tobytes())==g['target_eligibility_sha256'])
    check('target_and_cohort_dimensions',Y.shape==(23679,74) and cohort.sum()==22349)
    check('no_one_item_target_scores',not (mask&(N<2)).any())
    check('no_target_imputation',np.array_equal(mask,N>=2))
    check('all_targets_have_minimum_two',all(x['minimum']==2 and len(x['items'])>=2 for x in f['targets']))
    for sp in f['targets']+f['candidates']:
        check('official_signs_'+sp['name'],np.array_equal(sp['signs'],d.key.loc[sp['items'],sp['official_key']].to_numpy()))
        x=d.raw[:,[d.ix[i] for i in sp['items']]];sg=np.array(sp['signs']);manual=np.where(sg[None,:]<0,7-x,x);nn=np.isfinite(manual).sum(1);v=np.nansum(manual,1)/np.maximum(nn,1);v[nn<2]=np.nan
        actual,_=d.score([sp]);check('independent_keyed_mean_'+sp['name'],np.allclose(actual[:,0],v,equal_nan=True,atol=1e-12,rtol=0))
    sets={k:set(i for sp in f[k] for i in sp['items']) for k in ['targets','candidates','bridge','bigfive']};hi=set(f['hifwb']['items'])
    check('target_disjoint',not sets['targets']&(sets['candidates']|sets['bridge']|sets['bigfive']|hi))
    check('candidate_disjoint',not sets['candidates']&(sets['bridge']|sets['bigfive']|hi))
    check('hifwb_predictors_disjoint',not hi&(sets['bridge']|sets['bigfive']))
    sec=pd.read_csv(OUT/'repair/bigfive_secondary_bridge.csv');check('bigfive_secondary_no_self_prediction',not set(';'.join(sec['items']).split(';'))&sets['bigfive'])
    cross_duplicates=[]
    for a in sorted(sets['candidates']):
        x=' '.join(str(d.dictionary.loc[a,'item_text']).lower().split())
        for b in sorted(set(d.ids)-sets['candidates']):
            y=' '.join(str(d.dictionary.loc[b,'item_text']).lower().split());similarity=difflib.SequenceMatcher(None,x,y).ratio()
            if similarity>=.90:cross_duplicates.append(dict(candidate_item=a,other_item=b,candidate_text=x,other_text=y,similarity=similarity))
    pd.DataFrame(cross_duplicates,columns=['candidate_item','other_item','candidate_text','other_text','similarity']).to_csv(OUT/'repair/candidate_vs_other_wording_audit.csv',index=False)
    check('no_near_duplicate_candidate_vs_other_wording',not cross_duplicates)
    # Numerical estimator test: missing labels, missing predictors, separate exact sklearn solves.
    rng=np.random.default_rng(19);X=rng.normal(size=(150,4));X[rng.random(X.shape)<.2]=np.nan;yy=np.nan_to_num(X)@rng.normal(size=(4,3))+rng.normal(size=(150,3));yy[rng.random(yy.shape)<.2]=np.nan
    class Fake:
        n=150
        def score(self,specs,fit,item_z=True):return X.copy(),np.isfinite(X).astype(int)
    tr=np.arange(100);va=np.arange(100,150);c=Cache(Fake(),[0,1,2,3],yy,tr,va);features=[0,2,3];cols=c.cols(features);p=c.predict(features,10.)
    for j in range(3):
        ok=np.isfinite(yy[tr,j]);m=Ridge(alpha=10,fit_intercept=True).fit(c.Xtr[ok][:,cols[1:]],(yy[tr[ok],j]-c.mu[j])/c.sd[j]);ref=m.predict(c.Xv[:,cols[1:]])*c.sd[j]+c.mu[j]
        check('masked_ridge_sklearn_'+str(j),np.allclose(p[:,j],ref,rtol=0,atol=1e-10))
    check('moment_sse_matches_direct_r2',abs(c.evaluate(features)[1]-np.mean(r2_dimensions(yy[va],p)[0]))<1e-10)
    original=c.coefficients(features,10.)[1].copy();X[va]=1000;yy[va]=-999;c2=Cache(Fake(),[0,1,2,3],yy,tr,va)
    check('validation_values_cannot_change_fit',np.allclose(original,c2.coefficients(features,10.)[1],rtol=0,atol=1e-12))
    folds=pd.read_csv(OUT/'split_manifest.csv');check('five_exhaustive_outer_test_counts',len(folds)==5 and folds.test_n.sum()==s['n'] and (folds.train_n+folds.test_n==s['n']).all())
    sel=pd.read_csv(OUT/'outer_fold_selection.csv');pairs=pd.read_csv(OUT/'outer_training_redundancy.csv')
    for row in sel[sel.path_type=='distinct'].itertuples():
        names=set(str(row.selected_families).split(';'));pp=pairs[(pairs.outer_fold==row.outer_fold)&pairs.redundant];check(f'distinct_fold_{row.outer_fold}_k{row.k}',not any(r.candidate_a in names and r.candidate_b in names for r in pp.itertuples()))
    curve=pd.read_csv(OUT/'minimal_set_curve.csv');check('k_zero_through_eight',curve.k.tolist()==list(range(9)))
    compare=pd.read_csv(OUT/'profile_reconstruction_comparison.csv').set_index('analysis');check('same_cohort_all_profile_comparisons',(compare.respondents==s['n']).all() and (compare.observed_target_cells==389072).all())
    check('curve_matches_profile_table',all(abs(r.profile_r2-compare.loc[f'distinct_k{r.k}','macro_r2'])<1e-12 for r in curve.itertuples()))
    best=curve.loc[curve.profile_r2.idxmax()];check('best_k_reproduced',best.k==s['best_k'])
    k95=int(curve.loc[curve.fraction_of_best_gain>=.95,'k'].min());check('relative_95percent_set',k95==s['k_capturing_95percent_gain'])
    ranks=pd.read_csv(OUT/'candidate_dimension_ranking.csv');check('nine_candidates_five_named_top',len(ranks)==9 and (ranks.rank_distinct_final<=5).sum()==5)
    stab=pd.read_csv(OUT/'selection_stability_runs.csv');check('twenty_split_stability_runs',stab.replicate.nunique()==20)
    dep=json.loads((OUT/'dependency_repair/refit_verification.json').read_text());check('only_affected_human_refits',set(dep['human_refits_completed'])=={'AA20','AA21_common','AA22','AA23','AA24'} and not dep['persona_projections_run'])
    changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines();check('original_AA16_to_AA25_unchanged',not any(p.startswith('research/outputs/aa'+str(j)+'_') for p in changed for j in range(16,26)))
    check('cpu_scope',all(s[k] is False for k in ['model_inference','runpod','paid_compute','raw_rows_exported']))
    required=['aa26_report.md','candidate_dimension_ranking.csv','selected_question_or_construct_set.csv','profile_reconstruction_comparison.csv','incremental_gain_by_candidate.csv','minimal_set_curve.csv','selection_stability.csv','phase_gate_audit.md']
    check('required_outputs',all((OUT/n).is_file() and (OUT/n).stat().st_size>20 for n in required))
    for p in OUT.glob('*.py'):ast.parse(p.read_text())
    check('scripts_parse',True)
    target_hash=sha(np.ascontiguousarray(np.where(mask,Y,0),dtype='<f8').tobytes());jsave(OUT/'repair/target_score_fingerprint.json',dict(score_sha256=target_hash,format='little-endian float64 row-major; missing replaced by zero; combine with observation-mask hash',observation_mask_sha256=sha(mask.tobytes()),rows=23679,dimensions=74,respondent_data_exported=False))
    jsave(OUT/'verification_report.json',dict(status='PASS',checks=checks,passed=len(checks),model_used='GPT-6 Astra',python=sys.version.split()[0],numpy=np.__version__,pandas=pd.__version__,numerical_score_tolerance=1e-10,scope='repaired measurement, affected human dependency refits, new nested CV; not restoration of withdrawn AA12/13 or persona transports',raw_rows_exported=False))
    print(json.dumps(dict(status='PASS',passed=len(checks))))
if __name__=='__main__':main()
