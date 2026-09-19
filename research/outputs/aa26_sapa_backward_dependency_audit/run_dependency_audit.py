#!/usr/bin/env python3
"""Focused source/eligibility audit. Never import or execute historical analyses.

Only static code, existing aggregate results, tiny synthetic scoring fixtures,
and optionally raw item availability are inspected. No fitting or target repair.
"""
import argparse, ast, csv, hashlib, io, json, subprocess, warnings
from pathlib import Path
from types import SimpleNamespace
import numpy as np

ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
BASE='bcec11d9db9b2e87554012bb3d2f5f2a8201df6f'
OLD='045ac766949356ffb31705c69ba677824faf65b8'
AA10='f4cc10bd3392c4432eccfa8244a3e58b5eef31a5'
sources=[]; checks={}
def sha(b):return hashlib.sha256(b).hexdigest()
def get(folder,name,ref=BASE):
    path='research/outputs/'+folder+'/'+name
    b=subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT)
    sources.append(dict(path=path,commit=ref,sha256=sha(b),bytes=len(b)))
    return b.decode()
def tab(s):return list(csv.DictReader(io.StringIO(s)))
def save(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def check(name,condition):
    checks[name]=bool(condition)
    if not condition:raise AssertionError(name)
def extract(src,name,env):
    node=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name==name)
    code=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),node],type_ignores=[])
    exec(compile(ast.fix_missing_locations(code),'synthetic_scoring_fixture','exec'),env)
    return env[name]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',type=Path,required=True);args=ap.parse_args()
    folders={16:'aa16_sapa_hifwb_trait_profile',17:'aa17_three_model_trait_factor',18:'aa18_three_model_consensus_trait_structure',19:'aa19_human_consensus_factor_validation',20:'aa20_consensus_axes_hifwb',21:'aa21_bigfive_hifwb_persona_projection',22:'aa22_direct_trait_hifwb_bridge',23:'aa23_bigfive_residual_hifwb_bridge',24:'aa24_model_consensus_hifwb_projection',25:'aa25_intervention_bigfive_transport'}
    scripts={i:get(f,'run_stage1.py' if i==16 else 'run_bigfive_hifwb_projection.py' if i==21 else 'run_analysis.py') for i,f in folders.items()}
    reports={16:'stage1_findings.md',17:'three_model_trait_factor_report.md',18:'three_model_consensus_trait_report.md',19:'three_model_human_validation_report.md',20:'aa20_consensus_axes_hifwb_report.md',21:'outcome1_bigfive_hifwb_report.md',22:'aa22_direct_trait_hifwb_report.md',23:'aa23_bigfive_residual_hifwb_report.md',24:'aa24_model_consensus_hifwb_report.md',25:'aa25_intervention_bigfive_transport_report.md'}
    for i,f in folders.items():
        get(f,reports[i]);get(f,'stage1_analysis_freeze.md' if i==16 else 'analysis_freeze.md') if i not in (21,25) else None
    get(folders[20],'predictor_scoring_specification.md')
    bridge=get('sapa_bridge_psychometric_audit','run_sapa_bridge_psychometric_audit.py')
    for f in ['psychometric_support_rubric.md','sapa_bridge_psychometric_audit_report.md']:get('sapa_bridge_psychometric_audit',f)
    first=get('broad_sapa_pca_wellbeing','run_broad_sapa_pca.py',OLD)
    follow=get('broad_sapa_pca_wellbeing','run_followup_checks.py',OLD)
    reconstruction=get('broad_sapa_pca_wellbeing','reconstruct_frozen_scores.py',OLD)
    for f in ['analysis_freeze.md','source_manifest.json','broad_sapa_pca_wellbeing_report.md','incremental_prediction_uncertainty.md','stability_summary.md','verification_report.json']:get('broad_sapa_pca_wellbeing',f,OLD)
    terrain=get('sapa_wellbeing_terrain_explorer','analysis/build_terrain.py',OLD)
    for f in ['methodology.md','sapa_wellbeing_terrain_explorer_report.md','source_manifest.json']:get('sapa_wellbeing_terrain_explorer',f,OLD)
    terrain_metrics=tab(get('sapa_wellbeing_terrain_explorer','conditional_model_metrics.csv',OLD))
    oldmetrics=tab(get('sapa_hifwb_reproducibility','robustness_metrics.csv',AA10))
    oldcode=get('sapa_hifwb_reproducibility','run_sapa_hifwb_reproducibility.py',AA10)
    for f in ['analysis_specification.md','historical_reconstruction_notes.md','sapa_hifwb_reproducibility_report.md','source_manifest.json']:get('sapa_hifwb_reproducibility',f,AA10)
    freeze=tab(get('sapa_hifwb_reproducibility','wellbeing_item_freeze.csv'))
    prior=json.loads(get('aa26_sapa_profile_information_gain','feasibility_summary.json'))
    check('prior_reverse_scoring_defect_preserved',prior['aa13_reverse_key_identity_matches']==0 and prior['dimensions_with_exact_official_key_requiring_reversals']==78)
    check('prior_missingness_defect_preserved',prior['retained_one_item_scale_cells']==636832)
    check('existing_q55_exception_mapping_found','elif row.scale_id == "IPIP100:B5:E"' in bridge and 'official_named_key_' in bridge)
    # Tiny fixtures exercise extracted functions only, never historical main().
    env={'np':np};f=extract(scripts[16],'score_mean',env)
    z={'a':np.array([1.,1.]),'b':np.array([np.nan,2.])};v,n=f(z,['a','b'],{'a'},2)
    check('aa16_two_item_mask_and_sign',np.isnan(v[0]) and v[1]==.5)
    class Frame:
        def __getitem__(self,ids):return self
        def to_numpy(self,*args):return np.array([[6.,np.nan],[6.,2.]])
    class Rows:
        def itertuples(self):return iter([SimpleNamespace(sapa_item_ids='a;b',orientation_signs='a:-1;b:1')])
    for i in [20,22,23]:
        env={'np':np,'zfit':(lambda x,fit:x) if i==20 else (lambda x,fit:(x,None,None))}
        extract(scripts[i],'parse_items' if i==20 else 'parse',env)
        f=extract(scripts[i],'trait_matrix' if i==20 else 'score_traits',env)
        v,obs=f(Frame(),Rows(),[0,1]);check(f'aa{i}_one_item_proxy_finite_and_oriented',v[0,0]==1 and obs[0,0] and v[1,0]==1.5)
        check(f'aa{i}_outcome_and_bigfive_two_item_masks','y[n<2]=np.nan' in scripts[i] and 'a[n<2]=np.nan' in scripts[i])
    check('aa21_primary_two_item_masks','y[yn < 2] = np.nan' in scripts[21] and 's[n < 2] = np.nan' in scripts[21])
    check('aa21_sensitivity_only_uses_proxy_coverage','common = bf_ok & (O.sum(1) >= 8)' in scripts[21] and 'Xfull[bf_ok], yfull[bf_ok], Xcommon[common]' in scripts[21])
    check('aa24_calls_aa20_scoring','a=load_aa20()' in scripts[24] and 'a.scores(' in scripts[24])
    check('aa25_uses_primary_not_common_weights','weights.human_fit == "full_overlap_primary"' in scripts[25])
    check('aa19_signed_covariance_not_respondent_means','b[pos[r.item_id],col[r.trait]]=float(r.orientation_sign)' in scripts[19] and 'a=b.T@c@b' in scripts[19])
    for i in range(16,26):check(f'aa{i}_no_broad_profile_import','broad_sapa_pca_wellbeing' not in scripts[i] and 'sapa_wellbeing_terrain_explorer' not in scripts[i])
    for i in [17,18]:check(f'aa{i}_no_raw_SAPA_input','sapaTempData' not in scripts[i] and 'superKey696' not in scripts[i])
    # Availability-only check: do not compute respondent scores or fit anything.
    rawpath=args.data_dir/'sapaTempData696items08dec2013thru26jul2014.tab';keypath=args.data_dir/'superKey696.csv'
    check('raw_hash',sha(rawpath.read_bytes())=='fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6')
    check('key_hash',sha(keypath.read_bytes())=='8d19b6a23c7f42b91cf5bc0895e2c63790510ba9355a2c69d19703c6f791bc49')
    key=tab(keypath.read_text());bigkeys=['IPIP100agree','IPIP100consc','IPIP100extra','IPIP100intel','IPIP100stability']
    groups=[[r[''] for r in key if float(r[k] or 0)!=0] for k in bigkeys]
    direct=[r['item_id'] for r in freeze if r['tier']=='DIRECT']
    nonaff12=[r['item_id'] for r in freeze if r['tier']=='DIRECT' and r['content']!='Affect']
    nonaff10=[i for i in nonaff12 if i!='q_832']
    counts=dict(raw_n=0,bigfive_ge2_n=0,historical13_ge1_n=0,historical13_ge2_n=0,aa12_nonaffect9_ge1_n=0,aa12_nonaffect9_ge2_n=0,aa10_nonaffect8_ge2_n=0)
    with rawpath.open() as f:
        rd=csv.reader(f,delimiter='\t');header=next(rd);indices=[[header.index(i) for i in g] for g in [*groups,direct,nonaff12,nonaff10]]
        for row in rd:
            counts['raw_n']+=1;n=[sum(row[j] not in ('NA','') for j in g) for g in indices]
            if min(n[:5])<2:continue
            counts['bigfive_ge2_n']+=1
            for name,test in [('historical13_ge1_n',n[5]>=1),('historical13_ge2_n',n[5]>=2),('aa12_nonaffect9_ge1_n',n[6]>=1),('aa12_nonaffect9_ge2_n',n[6]>=2),('aa10_nonaffect8_ge2_n',n[7]>=2)]:counts[name]+=int(test)
    published12={r['outcome']:r for r in terrain_metrics};published10={r['score']:r for r in oldmetrics}
    check('aa12_historical_uses_one_item_cohort',counts['historical13_ge1_n']==int(published12['historical_13']['N'])==6549)
    check('aa10_historical_two_item_cohort',counts['historical13_ge2_n']==int(published10['historical_13']['N'])==3972)
    check('aa12_nonaffect_one_item_cohort',counts['aa12_nonaffect9_ge1_n']==int(published12['non_affect']['N'])==5715)
    check('aa10_nonaffect_two_item_cohort',counts['aa10_nonaffect8_ge2_n']==int(published10['non_affect']['N'])==2548)
    check('content_balanced_saved_cohort_matches',published12['content_balanced_ge2']['N']==published10['content_balanced_ge2']['N']=='3257')
    check('terrain_bigfive_cohort',counts['bigfive_ge2_n']==8585)
    (OUT/'eligibility_verification.json').write_text(json.dumps(dict(counts=counts,extra_one_item_historical_rows=counts['historical13_ge1_n']-counts['historical13_ge2_n'],extra_one_item_nonaffect9_rows=counts['aa12_nonaffect9_ge1_n']-counts['aa12_nonaffect9_ge2_n'],nonaffect_membership_difference=['q_832'],raw_rows_exported=False,scoring_or_fitting_performed=False),indent=2)+'\n')
    # Exact source locations for review, with function line ranges where available.
    lines=[]
    for i,src in scripts.items():
        for n in ast.parse(src).body:
            if isinstance(n,ast.FunctionDef) and n.name in ['score_mean','association_rows','basis','proxy','human_data','bigfive_alignment','trait_matrix','outcome_score','bf_scores','eligibility','score_human_data','score_traits','score_outcome','score_bigfive','load_aa20','main']:
                lines.append(dict(stage='AA-'+str(i),function=n.name,first_line=n.lineno,last_line=n.end_lineno,source_path='research/outputs/'+folders[i]+'/'+('run_stage1.py' if i==16 else 'run_bigfive_hifwb_projection.py' if i==21 else 'run_analysis.py'),commit=BASE))
    save('scoring_function_locations.csv',lines)
    save('source_inventory.csv',list({(r['commit'],r['path']):r for r in sources}.values()))
    result=dict(status='PASS',model_used='GPT-6 Astra',audit_type='backward dependency; static source plus synthetic fixtures and item-availability counts',checks=checks,checks_passed=len(checks),analyses_rerun=0,models_fitted=0,broad_target_rebuilt=False,model_inference=False,respondent_rows_exported=False)
    (OUT/'verification_report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(checks=len(checks),counts=counts,analyses_rerun=0)))

if __name__=='__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning);main()
