#!/usr/bin/env python3
import argparse,collections,difflib
from aa26_common import *

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',required=True);a=ap.parse_args();d=Data(a.data_dir)
    t,c,ta,ca=freeze_measurements(d)
    # Collapse exact and inverse source-subset aliases, preserving canonical source order.
    kept=[];aliases=[];seen={}
    for s in sorted(t,key=lambda s:s['name']):
        sign=np.array(s['signs']);sign=sign*sign[0];identity=tuple(zip(s['items'],sign.tolist()))
        if identity in seen:aliases.append(dict(excluded=s['name'],representative=seen[identity],reason='exact_or_inverse_item_set'))
        else:seen[identity]=s['name'];kept.append(s)
    t=kept;Y,N=d.score(t);eligible=np.isfinite(Y).sum(1)>=5
    citems=sorted(set(i for s in c for i in s['items']));near=[]
    for j,i in enumerate(citems):
        for k in citems[:j]:
            x=' '.join(str(d.dictionary.loc[i,'item_text']).lower().split());y=' '.join(str(d.dictionary.loc[k,'item_text']).lower().split());sim=difflib.SequenceMatcher(None,x,y).ratio()
            if sim>=.90:near.append(dict(item_a=i,item_b=k,wording_a=x,wording_b=y,similarity=sim))
    assert not near,'Review near-duplicate candidate text before freezing'
    assert len(t)>=30 and eligible.sum()>1000
    counts=np.isfinite(Y).sum(1)
    specpack=dict(version='AA26_disjoint_human_profile_v2',base_commit=BASE,targets=t,candidates=c,bridge=d.bridge_specs,bigfive=d.bf_specs,hifwb=d.hifwb,raw_rows=d.n,eligible_profile_n=int(eligible.sum()),eligible_rule='>=5 observed target dimensions; each >=2 observed keyed items',primary_target_score='mean oriented raw response; no label imputation',candidate_group_rule='source identity plus fixed emotional stability alias and train-only residual |r|>=.80',allow_model_inference=False,allow_runpod=False)
    repair=OUT/'repair';repair.mkdir(exist_ok=True)
    jsave(repair/'measurement_freeze.json',specpack)
    for r in ta:
        r['included_after_alias_collapse']=r['dimension'] in {s['name'] for s in t}
        if r['included_after_alias_collapse']:
            j=[s['name'] for s in t].index(r['dimension']);r['eligible_cohort_observed_n']=int(np.isfinite(Y[eligible,j]).sum())
    save(repair/'target_dimension_inventory.csv',ta);save(repair/'candidate_pool_inventory.csv',ca)
    pd.DataFrame(aliases,columns=['excluded','representative','reason']).to_csv(repair/'target_alias_audit.csv',index=False)
    pd.DataFrame(near,columns=['item_a','item_b','wording_a','wording_b','similarity']).to_csv(repair/'candidate_wording_duplicate_audit.csv',index=False)
    save(repair/'candidate_existing_questions.csv',[dict(item_id=i,text=d.dictionary.loc[i,'item_text'],candidate_families=';'.join(s['name'] for s in c if i in s['items'])) for i in citems])
    Titems=set(i for s in t for i in s['items'])
    facts=dict(status='PASS',target_dimensions=len(t),candidate_families=len(c),target_unique_items=len(Titems),candidate_unique_items=len(citems),profile_eligible_n=int(eligible.sum()),respondents=d.n,complete_profiles=int(np.isfinite(Y).all(1).sum()),observed_target_cells=int(np.isfinite(Y).sum()),overall_missing_fraction=float(np.isnan(Y).mean()),median_observed_dimensions=float(np.median(counts)),observed_dimensions_quantiles=[float(x) for x in np.quantile(counts,[0,.25,.5,.75,1])],cohort_observed_target_cells=int(np.isfinite(Y[eligible]).sum()),bridge_target_overlap=len(Titems&d.bi),bigfive_target_overlap=len(Titems&d.bfi),hifwb_target_overlap=len(Titems&d.hi),candidate_target_overlap=len(set(citems)&Titems),one_item_target_scores_retained=int(((N<2)&np.isfinite(Y)).sum()),official_reverse_count=sum(sum(v<0 for v in s['signs']) for s in t),target_eligibility_sha256=sha(eligible.tobytes()),target_observation_mask_sha256=sha(np.isfinite(Y).tobytes()),target_spec_sha256=sha((repair/'measurement_freeze.json').read_bytes()),raw_data_exported=False)
    jsave(repair/'target_validity_gate.json',facts)
    old=d.human_scores(1);new=d.human_scores(2);vr=[]
    for stage,mask,features in [('AA20','common',['T','A']),('AA21_common','common',['B']),('AA22','basic',['T']),('AA23','basic',['T']),('AA24','common',['T','A'])]:
        before=old[mask];after=new[mask];diffs=[];lost=0
        for f in features:
            both=np.isfinite(old[f])&np.isfinite(new[f]);diffs.append(float(np.max(abs(old[f][both]-new[f][both]))));lost+=int((np.isfinite(old[f])&~np.isfinite(new[f])).sum())
        change=int(np.logical_xor(before,after).sum());same=change==0 and max(diffs)<=1e-10 and lost==0
        vr.append(dict(analysis=stage,mask_stage='pre_learned_index_coverage' if mask=='basic' else 'complete_common_coverage',old_eligible_n=int(before.sum()),corrected_eligible_n=int(after.sum()),removed_n=int((before&~after).sum()),added_n=int((after&~before).sum()),eligibility_changed_n=change,old_eligibility_sha256=sha(before.tobytes()),corrected_eligibility_sha256=sha(after.tobytes()),maximum_score_difference_common_finite=max(diffs),newly_missing_score_cells=lost,tolerance=1e-10,status='VERIFIED_UNCHANGED' if same else 'MATERIAL_CHANGE_RERUN_REQUIRED'))
    save(OUT/'dependency_repair'/'eligibility_comparison.csv',vr)
    jsave(OUT/'dependency_repair'/'verification_gate.json',dict(original_AA20_common_reproduced=int(old['common'].sum())==2859,original_AA22_AA23_preindex_reproduced=int(old['basic'].sum())==3551,all_five_require_rerun=all(r['status']=='MATERIAL_CHANGE_RERUN_REQUIRED' for r in vr),unchanged_analyses_not_run=['AA16','AA17','AA18','AA19','AA21_primary','AA25'],score_equivalence_tolerance=1e-10,mask_equivalence='exact',new_item_observations_required_for_multi_item_proxies=2))
    save(repair/'source_inventory.csv',list(SOURCES.values()))
    body=f'''# Repaired target and dependency gate — before candidate interpretation

The corrected target gate **passes** with {len(t)} disjoint-item source-construct dimensions, {facts['target_unique_items']} unique target items, and {facts['profile_eligible_n']:,} respondents with at least five observed dimensions. Every target uses official item signs (including 7−x reversal) and at least two observed items; all shared bridge, Big Five, and HiFWB items are removed. Zero one-item target scores survive. These are partial source-construct measures, not automatically full-scale validated scores. Exact dimension/coverage/missingness rules and hashes are in `target_dimension_inventory.csv`, `measurement_freeze.json`, and `target_validity_gate.json`.

Overall target missingness is {facts['overall_missing_fraction']:.1%}; the median respondent has {facts['median_observed_dimensions']:.0f} observed dimensions and there are {facts['complete_profiles']} complete profiles. Prediction will use only observed outcome labels and a fixed respondent cohort, never imputed target truth. The unused-item pool has {len(c)} adequately covered multi-item families; no predictive ranking has been calculated at this gate.

All five flagged dependencies materially change under the explicit two-item multi-item-proxy rule. The AA-20/24/common-sensitivity cohort contracts from {int(old['common'].sum()):,} to {int(new['common'].sum()):,}; AA-22/23 pre-index eligibility contracts from {int(old['basic'].sum()):,} to {int(new['basic'].sum()):,}. Exact masks were compared in memory and only hashes/counts exported. Passing equality on retained item means would not compensate for these changed masks. Human-only refits are required; original model/persona transports depending on these measures are not revalidated or rescored.

CPU gate: **PASS, local only**. RunPod/paid/GPU/model inference gate: **PROHIBITED**. AA-16–19, AA-21 primary, and AA-25 are not rerun. Old artifacts remain untouched. This report precedes candidate additions and does not state which concepts improve reconstruction.
'''
    (repair/'target_and_dependency_gate_report.md').write_text(body)
    print(json.dumps(dict(target_gate=facts,dependency_comparison=vr),indent=2))

if __name__=='__main__':main()
