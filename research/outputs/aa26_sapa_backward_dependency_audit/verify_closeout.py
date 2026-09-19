#!/usr/bin/env python3
"""Verify source receipts, dependency classifications, withdrawals and scope."""
import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
BASE='bcec11d9db9b2e87554012bb3d2f5f2a8201df6f'
def sha(b):return hashlib.sha256(b).hexdigest()
def rows(p):return list(csv.DictReader(p.open()))
checks={}
def check(k,v):
    checks[k]=bool(v)
    assert v,k
table=rows(OUT/'dependency_table.csv')
check('20_unique_result_groups',len(table)==len({r['result_id'] for r in table})==20)
check('aa16_through_aa25_covered',all(any(r['result_id'].startswith('AA'+str(i)) for r in table) for i in range(16,26)))
check('directly_affected_claims_withdrawn',all(r['claim_status']=='WITHDRAWN_PENDING_REPAIR' for r in table if r['classification']=='directly affected'))
check('exactly_four_withdrawals',sum(r['claim_status']=='WITHDRAWN_PENDING_REPAIR' for r in table)==4)
check('no_blank_dependency_actions',all(r['dependency_path'] and r['required_action'] and r['reason'] for r in table))
receipt=rows(OUT/'source_inventory.csv')
for r in receipt:
    b=subprocess.check_output(['git','show',r['commit']+':'+r['path']],cwd=ROOT)
    check('source_'+r['path'],sha(b)==r['sha256'] and len(b)==int(r['bytes']))
v=json.loads((OUT/'verification_report.json').read_text())
check('static_and_eligibility_checks_passed',v['checks_passed']==35 and all(v['checks'].values()))
check('no_analysis_reruns_or_target_repair',v['analyses_rerun']==v['models_fitted']==0 and v['broad_target_rebuilt'] is False)
for p in OUT.glob('*.csv'):
    with p.open() as f:
        rd=csv.reader(f);head=next(rd)
        check('csv_'+p.name,all(len(r)==len(head) for r in rd))
changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
allowed={'research/'+n for n in ['RESEARCH_STATE.md','THREAD_START.md','CLAIMS_REGISTER.md','FINDINGS_LEDGER.md','PROVENANCE_REGISTRY.md','RESEARCH_INDEX.md','REPO_NAVIGATION.md','REPO_FILE_INDEX.csv','RAW_URL_INDEX.md','STARTUP_MANIFEST.md']}
check('only_audit_and_canonical_records_modified',all(p in allowed or p.startswith(str(OUT.relative_to(ROOT))+'/') for p in changed))
check('previous_output_artifacts_untouched',not any(p.startswith('research/outputs/') and not p.startswith(str(OUT.relative_to(ROOT))+'/') for p in changed))
claim=(ROOT/'research/CLAIMS_REGISTER.md').read_text()
check('withdrawals_in_canonical_claims','WITHDRAWN PENDING REPAIR' in claim and 'AA-12 historical-13' in claim and 'AA-13 broad-score-dependent' in claim)
manifest=(ROOT/'research/STARTUP_MANIFEST.md').read_text()
for name in ['RESEARCH_STATE.md','THREAD_START.md','CLAIMS_REGISTER.md']:
    check('startup_'+name,sha((ROOT/'research'/name).read_bytes()) in manifest.split('### `research/'+name+'`')[1].split('### ')[0])
check('navigation_contains_audit',any(r['path']==str((OUT/'dependency_audit_report.md').relative_to(ROOT)) for r in rows(ROOT/'research/REPO_FILE_INDEX.csv')))
result=dict(status='PASS',checks=checks,check_count=len(checks),source_receipts=len(receipt),classified_results=20,directly_affected_withdrawn=4,potentially_affected=6,unaffected=10,original_outputs_unchanged=True)
(OUT/'closeout_verification.json').write_text(json.dumps(result,indent=2)+'\n')
with (OUT/'artifact_inventory.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','status','bytes','sha256'],lineterminator='\n');w.writeheader()
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!='artifact_inventory.csv':w.writerow(dict(path=str(p.relative_to(ROOT)),status='active',bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
