#!/usr/bin/env python3
"""Read-only human-data gate; no fitting, respondent export, or source modification.

python3 research/outputs/aa26_sapa_profile_information_gain/run_feasibility_audit.py --data-dir PATH
Requires numpy. AA-13 source blobs are read by immutable git commit, not executed.
"""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
AA13 = '045ac766949356ffb31705c69ba677824faf65b8'
BASE = '56902f6'
PREFIX = 'research/outputs/broad_sapa_pca_wellbeing/'
RECEIPTS = []

def sha(b): return hashlib.sha256(b).hexdigest()
def source(path, ref=None):
    b = subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT) if ref else (ROOT/path).read_bytes()
    RECEIPTS.append(dict(path=path, git_ref=ref or BASE, sha256=sha(b), bytes=len(b)))
    return b
def table(b): return list(csv.DictReader(io.StringIO(b.decode())))
def save(name, rows, fields=None):
    with (OUT/name).open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
def writejson(name, obj): (OUT/name).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data-dir', type=Path, required=True); args=ap.parse_args()
    req={
      'sapaTempData696items08dec2013thru26jul2014.tab':'fb480e6bd4c5ba0832cdd105c2fac5dc47b144378e96ffb3a50f3e8d63868cb6',
      'superKey696.csv':'8d19b6a23c7f42b91cf5bc0895e2c63790510ba9355a2c69d19703c6f791bc49',
      'ItemInfo696.csv':'ce280ebf42cd77f3db1955a3027051a74d017ca61da02adf5dbbab11545b1732'}
    rawchecks=[]
    for name, expected in req.items():
        p=args.data_dir/name; actual=sha(p.read_bytes())
        rawchecks.append(dict(file=name, expected_sha256=expected, actual_sha256=actual, passed=actual==expected, bytes=p.stat().st_size))
    assert all(r['passed'] for r in rawchecks)
    feasibility='research/outputs/human_trait_dataset_feasibility/sapa/'
    audit='research/outputs/sapa_bridge_psychometric_audit/'
    cw=table(source(feasibility+'sapa_model_trait_candidate_crosswalk.csv'))
    inv=table(source(feasibility+'sapa_scale_inventory.csv'))
    support=table(source(audit+'sapa_trait_bridge_psychometric_support_v1.csv'))
    assoc=table(source(audit+'trait_proxy_scale_associations_long.csv'))
    bfassoc=table(source(audit+'retained_traits_vs_human_big_five.csv'))
    dictionary=table(source(feasibility+'sapa_item_dictionary.csv'))
    for p in [feasibility+'sapa_source_manifest.json',audit+'source_manifest.json']:
        source(p)
    profile=table(source(PREFIX+'predictor_inventory.csv',AA13))
    prior_missing=table(source(PREFIX+'missingness_summary.csv',AA13))
    first=source(PREFIX+'run_broad_sapa_pca.py',AA13).decode()
    follow=source(PREFIX+'run_followup_checks.py',AA13).decode()
    for p in ['source_manifest.json','analysis_freeze.md','external_data_dependency.md','frozen_score_reconstruction.json','verification_report.json','broad_sapa_pca_wellbeing_report.md']:
        source(PREFIX+p,AA13)
    bridge=table(source('research/outputs/aa19_human_consensus_factor_validation/bridge_mapping_audit.csv',BASE))
    source('research/outputs/aa19_human_consensus_factor_validation/human_matrix_audit.md',BASE)
    primary=[r for r in bridge if r['aa19_primary_selected']=='True']
    bridge_items=set(';'.join(r['sapa_item_ids'] for r in primary).split(';'))
    direct_items=set(';'.join(r['sapa_item_ids'] for r in support if r['semantic_review_decision']=='ACCEPT_DIRECT').split(';'))
    key=table((args.data_dir/'superKey696.csv').read_bytes())
    keycols=list(key[0])[1:]; keymap={r['']:r for r in key}
    bigkeys=['IPIP100agree','IPIP100consc','IPIP100extra','IPIP100intel','IPIP100stability']
    bfitems={i for i,r in keymap.items() if any(float(r[k] or 0)!=0 for k in bigkeys)}
    ids=[r['item_id'] for r in dictionary]; ix={x:i for i,x in enumerate(ids)}
    # Select only item columns; IDs and demographics are neither stored nor exported.
    with (args.data_dir/'sapaTempData696items08dec2013thru26jul2014.tab').open() as f:
        rd=csv.reader(f,delimiter='\t'); header=next(rd); cols=[header.index(i) for i in ids]
        raw=np.array([[float(row[j]) if row[j] not in ('NA','') else np.nan for j in cols] for row in rd])
    assert raw.shape==(23679,696)
    reverse={r['item_id']:set(r['reverse_keyed_in_derived_scales'].split(';')) for r in dictionary}
    sourceinv={r['scale_id'].replace(':','_'):r for r in inv if r['inventory_type']=='administered_source_construct'}
    target_items=set(); dim=[]; signexamples=[]; observed=[]; valid=[]
    for r in profile:
        items=r['source_items'].split(';'); target_items.update(items); s=sourceinv[r['predictor_id']]
        count=np.isfinite(raw[:,[ix[i] for i in items]]).sum(1)
        applied=[i for i in items if s['scale_id'] in reverse[i]]
        exact=[k for k in keycols if {i for i,v in keymap.items() if float(v[k] or 0)!=0}==set(items)]
        neg={k:[i for i in items if float(keymap[i][k] or 0)<0] for k in exact}
        for k, ii in neg.items():
            if ii: signexamples.append(dict(dimension=r['predictor_id'],exact_official_key=k,negative_item_ids=';'.join(ii),negative_count=len(ii),applied_reverse_count=len(applied)))
        dim.append(dict(dimension=r['predictor_id'],source_scale_id=s['scale_id'],instrument=s['instrument'],source_items=r['source_items'],item_count=len(items),respondent_total=len(raw),observed_at_least_one_n=int((count>=1).sum()),documented_at_least_two_n=int((count>=2).sum()),one_item_scores_retained_by_code=int((count==1).sum()),missing_fraction_two_item_rule=float((count<2).mean()),inventory_rule=r['scoring_rule'],manifest_rule='>=2 observed items',code_rule='mean if >=1 observed; >=2 only used for aggregate coverage',applied_reverse_count=len(applied),exact_official_keys=';'.join(exact),bridge41_overlap=len(set(items)&bridge_items),bridge45_overlap=len(set(items)&direct_items),bigfive_overlap=len(set(items)&bfitems),status='REJECTED_AS_FROZEN_TARGET'))
        observed.append(count>=1);valid.append(count>=2)
    allkeyitems={i for i,r in keymap.items() if any(float(r[k] or 0)!=0 for k in keycols)}
    assert len(profile)==79 and not any(d['applied_reverse_count'] for d in dim)
    assert 'if sid in rev.get(q,set())' in first and 'cols.append(sm)' in first
    assert 'cols.append(np.nanmean(a,1))' in follow
    assert all(int(p['respondent_n'])==d['documented_at_least_two_n'] for p,d in zip(profile,dim))
    assert all(int(p['respondent_n'])==d['documented_at_least_two_n'] for p,d in zip(prior_missing,dim))
    summary=dict(status='BLOCKED_INVALID_FROZEN_BROAD_TARGET',raw_data_available=True,raw_rows=len(raw),item_columns=raw.shape[1],aa13_dimensions=len(dim),aa13_target_item_union=len(target_items),aa13_reverse_key_identity_matches=0,dimensions_with_exact_official_key_requiring_reversals=len({r['dimension'] for r in signexamples}),retained_one_item_scale_cells=sum(r['one_item_scores_retained_by_code'] for r in dim),complete_profile_n_code=int(np.column_stack(observed).all(1).sum()),complete_profile_n_documented_rule=int(np.column_stack(valid).all(1).sum()),median_dimensions_observed_two_item_rule=float(np.median(np.column_stack(valid).sum(1))),bridge41_count=len(primary),bridge41_unique_items=len(bridge_items),bridge41_target_overlap=len(bridge_items&target_items),bridge45_unique_items=len(direct_items),bridge45_target_overlap=len(direct_items&target_items),bigfive_items=len(bfitems),bigfive_target_overlap=len(bfitems&target_items),official_key_count=len(keycols),official_key_target_union=len(allkeyitems),items_outside_all_official_keys=len(set(ids)-allkeyitems),aa13_items_outside_target=len(set(ids)-target_items),aa13_items_outside_target_bridge_and_bigfive=len(set(ids)-target_items-bridge_items-bfitems),required_artifact_rows=dict(crosswalk=len(cw),scale_inventory=len(inv),support=len(support),associations=len(assoc),bigfive_associations=len(bfassoc)),fit_performed=False)
    save('target_dimension_audit.csv',dim);save('reverse_scoring_evidence.csv',signexamples)
    save('baseline_predictor_audit.csv',[dict(bridge='AA19_future_safe_direct41',trait=r['model_trait'],item_ids=r['sapa_item_ids'],orientation_signs=r['orientation_signs'],target_overlap=';'.join(sorted(set(r['sapa_item_ids'].split(';'))&target_items))) for r in primary])
    save('source_artifact_inventory.csv',RECEIPTS);writejson('feasibility_summary.json',summary);writejson('raw_source_verification.json',rawchecks)
    for name,fields in {
      'candidate_dimension_ranking.csv':['rank','concept','delta_profile_r2','status'],
      'selected_question_or_construct_set.csv':['rank','concept','source_items','status'],
      'incremental_gain_by_candidate.csv':['concept','baseline','delta_profile_r2','delta_bigfive_r2','delta_hifwb_r2','status'],
      'selection_stability.csv':['concept','bootstrap_selection_frequency','split_selection_frequency','status']}.items():save(name,[],fields)
    save('profile_reconstruction_comparison.csv',[dict(baseline=b,profile_r2='',bigfive_r2='',hifwb_r2='',status='NOT_RUN_TARGET_GATE_FAILED') for b in ['current_bridge_only','big_five_only','current_bridge_plus_big_five','current_bridge_plus_big_five_plus_candidates']])
    save('minimal_set_curve.csv',[dict(k=k,profile_r2='',delta_profile_r2='',within_tolerance='',status='NOT_RUN_TARGET_GATE_FAILED') for k in range(1,9)])
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
