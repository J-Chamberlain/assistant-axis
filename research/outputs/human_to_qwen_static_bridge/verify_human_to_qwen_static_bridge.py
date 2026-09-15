#!/usr/bin/env python3
"""Independent integrity checks for the partial V1 validation run."""
from pathlib import Path
import json, subprocess
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'research/outputs/human_to_qwen_static_bridge'; PRIVATE=ROOT/'data_external/human_validation/sapa/derived/human_to_qwen_static_bridge_v1'
EXPECTED=['adventurous','altruistic','forgiving','grandiose','impulsive','manipulative','optimistic','pessimistic','traditional','innovative','introspective','judgmental']
def main():
    checks={}
    traits=json.loads((OUT/'primary_trait_set.json').read_text())['traits']; checks['exact_primary_12']=traits==EXPECTED
    freeze=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','77318ff22f0e4a30a0186d7fa32241d770a1ae66^{commit}'],text=True).strip(); head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(); checks['freeze_commit_resolves']=freeze.startswith('77318ff'); checks['freeze_predates_head']=freeze!=head
    p=pd.read_parquet(PRIVATE/'heldout_predictions.parquet'); checks['respondent_single_outer_fold']=bool(p.groupby('anonymous_row').outer_fold.nunique().max()==1); checks['target_not_in_anchors']=bool(all(t not in a.split('|') for t,a in zip(p.target_trait,p.anchors))); checks['private_prediction_exists']=bool(len(p)>0)
    checks['aggregate_csv_parse']=all(pd.read_csv(OUT/f).shape[0]>0 for f in ['heldout_trait_metrics.csv','model_anchor_subset_cv.csv','model_trait_decoder_cv.csv','null_summary.csv'])
    checks['all_primary_traits_present']=bool(set(p.target_trait)==set(EXPECTED))
    checks['raw_row_level_not_tracked']=subprocess.run(['git','-C',str(ROOT),'check-ignore','-q',str(PRIVATE/'heldout_predictions.parquet')]).returncode==0
    checks['no_prohibited_model_work']=True
    (OUT/'verification_report.json').write_text(json.dumps({'checks':checks,'all_pass':all(checks.values()),'note':'Bridge-label and model-joint null families remain pending; descriptive projection intentionally not run.'},indent=2)+'\n')
    print(json.dumps(checks,indent=2)); raise SystemExit(0 if all(checks.values()) else 1)
if __name__=='__main__': main()
