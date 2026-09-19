#!/usr/bin/env python3
"""Verify the AA-26 feasibility result, not success of the blocked experiment."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE='56902f6'
checks={}
def sha(b):return hashlib.sha256(b).hexdigest()
def rows(p):return list(csv.DictReader(p.open()))
def check(name,condition):
    checks[name]=bool(condition)
    if not condition:raise AssertionError(name)

s=json.loads((OUT/'feasibility_summary.json').read_text())
check('raw_fingerprints_match',all(x['passed'] and x['expected_sha256']==x['actual_sha256'] for x in json.loads((OUT/'raw_source_verification.json').read_text())))
check('required_artifact_counts',s['required_artifact_rows']==dict(crosswalk=240,scale_inventory=223,support=74,associations=9694,bigfive_associations=74))
check('source_dimensions',s['raw_rows']==23679 and s['item_columns']==696)
for r in rows(OUT/'source_artifact_inventory.csv'):
    b=subprocess.check_output(['git','show',r['git_ref']+':'+r['path']],cwd=ROOT)
    check('source_'+r['path'],sha(b)==r['sha256'] and len(b)==int(r['bytes']))
d=rows(OUT/'target_dimension_audit.csv');e=rows(OUT/'reverse_scoring_evidence.csv')
check('unique_79_dimensions',len(d)==len({r['dimension'] for r in d})==79)
check('zero_reversals_applied',all(int(r['applied_reverse_count'])==0 for r in d))
check('78_dimensions_have_required_reversals',len({r['dimension'] for r in e})==78 and all(int(r['negative_count'])>0 for r in e))
check('extraversion_key_mismatch',[(r['dimension']) for r in d if not r['exact_official_keys']]==['IPIP100_B5_E'])
check('missingness_discrepancy',sum(int(r['one_item_scores_retained_by_code']) for r in d)==s['retained_one_item_scale_cells']==636832)
check('coverage_count_identities',all(int(r['observed_at_least_one_n'])==int(r['documented_at_least_two_n'])+int(r['one_item_scores_retained_by_code']) for r in d))
check('bridge_unchanged',len(rows(OUT/'baseline_predictor_audit.csv'))==41)
check('baseline_overlap',s['bridge41_target_overlap']==82 and s['bigfive_target_overlap']==99)
check('official_all_key_target_exhausts_items',s['official_key_count']==131 and s['official_key_target_union']==696)
check('scientific_gate_blocked_not_null_result',s['status']=='BLOCKED_INVALID_FROZEN_BROAD_TARGET' and s['fit_performed'] is False)
for name in ['candidate_dimension_ranking.csv','selected_question_or_construct_set.csv','incremental_gain_by_candidate.csv','selection_stability.csv']:
    check('unfitted_'+name,not rows(OUT/name))
curve=rows(OUT/'minimal_set_curve.csv')
check('curve_not_fabricated',len(curve)==8 and [int(r['k']) for r in curve]==list(range(1,9)) and all(r['profile_r2']==r['delta_profile_r2']=='' and r['status']=='NOT_RUN_TARGET_GATE_FAILED' for r in curve))
comparison=rows(OUT/'profile_reconstruction_comparison.csv')
check('four_baselines_unfitted',len(comparison)==4 and all(r['profile_r2']==r['bigfive_r2']==r['hifwb_r2']=='' for r in comparison))
changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
allowed={'research/'+n for n in ['RESEARCH_STATE.md','THREAD_START.md','CLAIMS_REGISTER.md','FINDINGS_LEDGER.md','PROVENANCE_REGISTRY.md','RESEARCH_INDEX.md','REPO_NAVIGATION.md','REPO_FILE_INDEX.csv','RAW_URL_INDEX.md','STARTUP_MANIFEST.md']}
check('existing_changes_limited_to_aa26_and_registries',all(p in allowed or p.startswith('research/outputs/aa26_sapa_profile_information_gain/') for p in changed))
check('aa16_through_aa25_untouched',not any(any(p.startswith('research/outputs/aa'+str(i)+'_') for i in range(16,26)) for p in changed))
index=rows(ROOT/'research/REPO_FILE_INDEX.csv')
check('navigation_csv_valid',bool(index) and all(set(r)=={'path','category','status','description','raw_github_url','size_bytes','extension','updated_utc'} for r in index))
check('navigation_aa26_present',any(r['path'].endswith('aa26_sapa_profile_information_gain/aa26_report.md') for r in index))
manifest=(ROOT/'research/STARTUP_MANIFEST.md').read_text()
for name in ['RESEARCH_STATE.md','THREAD_START.md','CLAIMS_REGISTER.md']:
    section=manifest.split('### `research/'+name+'`',1)[1].split('### ',1)[0]
    check('startup_hash_'+name,sha((ROOT/'research'/name).read_bytes()) in section)
for path in OUT.glob('*.csv'):
    with path.open() as f:
        rd=csv.reader(f);head=next(rd)
        check('csv_schema_'+path.name,all(len(r)==len(head) for r in rd))
check('no_raw_artifact_extensions',not any(p.suffix in {'.tab','.npz','.npy','.parquet','.pt'} for p in OUT.iterdir()))
result=dict(verification_status='PASS',analysis_status=s['status'],model_used='GPT-6 Astra',checks=checks,scope=dict(cpu_only=True,model_inference=False,runpod=False,paid_compute=False,viewer_changes=False,persona_scoring=False,new_model_prompts=False,respondent_rows_exported=False),limitations=['No candidate fitting, held-out metrics, selection stability, or minimal-set result because target gate failed.','Integrity checks validate feasibility evidence, not prior broad-profile trait validity.'])
(OUT/'verification_report.json').write_text(json.dumps(result,indent=2)+'\n')
paths=sorted(p for p in OUT.iterdir() if p.is_file() and p.name!='artifact_inventory.csv')
with (OUT/'artifact_inventory.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','status','bytes','sha256'],lineterminator='\n');w.writeheader()
    for p in paths:w.writerow(dict(path=str(p.relative_to(ROOT)),status='active',bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
print(json.dumps(dict(verification_status='PASS',analysis_status=s['status'],checks=len(checks),inventoried_artifacts=len(paths))))
