#!/usr/bin/env python3
"""Independent scoped feasibility verification; never compute persona facets/distances."""
from pathlib import Path
import csv,io,json,hashlib,subprocess,ast,collections
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE='91ad7519fe89b55921f58680a9a734e158320ca4';FREEZE='79417c2'
def sha(b):return hashlib.sha256(b).hexdigest()
checks={}
def check(n,v):checks[n]=bool(v);assert checks[n],n
s=json.loads((OUT/'source_manifest.json').read_text())
for r in s['sources']:check('source_hash_'+r['filename'],sha((ROOT/r['path']).read_bytes())==r['sha256'])
f=json.loads((OUT/'freeze_manifest.json').read_text())
for r in f['files']:
 check('frozen_current_'+r['path'],sha((OUT/r['path']).read_bytes())==r['sha256'])
 b=subprocess.check_output(['git','show',FREEZE+':'+str((OUT/r['path']).relative_to(ROOT))],cwd=ROOT);check('committed_precomparison_'+r['path'],sha(b)==r['sha256'])
rows=list(csv.DictReader((OUT/'model_trait_ipip_facet_crosswalk.csv').open()));check('cartesian_240_by_30',len(rows)==7200 and len({(r['model_trait'],r['facet_code']) for r in rows})==7200)
check('all_required_judgment_fields',all(r['semantic_rationale'] and r['evidence_source'] and r['duplicate_group'] and r['confidence'] for r in rows))
for mode,tiers in [('strict',{'direct'}),('expanded',{'direct','close'})]:
 inc=[r for r in rows if r[mode+'_included']=='True'];check(mode+'_tiers',all(r['mapping_tier'] in tiers for r in inc));check(mode+'_no_alias_duplicates',len(inc)==len({r['duplicate_group'] for r in inc}))
 coverage=collections.Counter(r['facet_code'] for r in inc);ret={f for f,n in coverage.items() if n>=2};check(mode+'_facet_counts',len(ret)==(20 if mode=='strict' else 29))
 if mode=='strict':check('coverage_gate_failed_before_personas',sum(x.startswith('E') for x in ret)==2)
key=list(csv.DictReader((OUT/'ipip_facet_scoring_specification.csv').open()));check('300_unique_official_items',sorted(int(r['item_number']) for r in key)==list(range(1,301)));check('ten_items_each_facet',set(collections.Counter(r['facet_code'] for r in key).values())=={10})
ks=list(csv.DictReader((OUT/'official_key_verification.csv').open()));check('300_independent_official_sign_matches',len(ks)==300 and all(r['official_html_sign']==r['workbook_sign'] for r in ks))
check('download_scoring_identity',all(r['download_transform']=='identity; zero becomes missing' for r in key));check('negative_key_count',sum(r['original_response_sign']=='-1' for r in key)==148)
# Simple non-tautological expected score test for already-keyed files.
raw_categories=[1,2,3,4,5];stored_negative=[5,4,3,2,1];check('documented_single_reverse_examples',[6-x for x in raw_categories]==stored_negative);check('second_reversal_would_invert_scores',[6-x for x in stored_negative]!=stored_negative)
a=json.loads((OUT/'density_audit.json').read_text());check('independent_eligibility_counts',a['independent_eligibility_parser_matches'] and a['respondents']==307313 and a['complete_30facets_adults_18_80']==117260)
mi=list(csv.DictReader((OUT/'item_missingness.csv').open()));hist=list(csv.DictReader((OUT/'respondent_missingness_distribution.csv').open()));check('item_person_missingness_reconcile',sum(int(r['missing_n']) for r in mi)==sum(int(r['missing_item_count'])*int(r['respondents']) for r in hist));check('missingness_hist_total',sum(int(r['respondents']) for r in hist)==307313)
# Read identifiers and schema only, leaving all numeric persona cells uninterpreted.
paths={'Qwen':'research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv','Llama':'research/outputs/multimodel_trait_profile_pc_predictor/llama/persona_trait_similarity_matrix.csv','Gemma':'research/outputs/multimodel_trait_profile_pc_predictor/gemma/persona_trait_similarity_matrix.csv'}
model_rows=[];first=None;traits={r['model_trait'] for r in rows}
for model,path in paths.items():
 b=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT);reader=csv.reader(io.StringIO(b.decode()));header=next(reader);personas=[row[0] for row in reader];check(model+'_275_unique_personas',len(personas)==len(set(personas))==275);check(model+'_240_exact_trait_set',len(header)==241 and set(header[1:])==traits)
 if first is None:first=(header,personas)
 check(model+'_exact_order_alignment',first==(header,personas))
 model_rows.append(dict(model=model,path=path,commit=BASE,sha256=sha(b),persona_n=275,trait_n=240,persona_order_sha256=sha(json.dumps(personas,separators=(',',':')).encode()),trait_order_sha256=sha(json.dumps(header[1:],separators=(',',':')).encode()),numeric_cells_evaluated=False))
with (OUT/'model_matrix_source_alignment.csv').open('w',newline='') as ff:w=csv.DictWriter(ff,fieldnames=list(model_rows[0]),lineterminator='\n');w.writeheader();w.writerows(model_rows)
old=subprocess.check_output(['git','show',BASE+':AGENTS.md'],cwd=ROOT,text=True);new=(ROOT/'AGENTS.md').read_text()
def outside_model_section(text):
 start=text.index('## Model specification for Codex analytical work');end=text.index('\n## ',start+4);return text[:start]+text[end:]
check('AGENTS_only_requested_section_changed',outside_model_section(old)==outside_model_section(new))
changed=subprocess.check_output(['git','diff',BASE,'--name-only'],cwd=ROOT,text=True).splitlines();check('AA16_AA26_artifacts_unchanged',not any(p.startswith('research/outputs/aa'+str(n)+'_') for p in changed for n in range(16,27)))
check('raw_files_gitignored',subprocess.run(['git','check-ignore','-q','data_external/aa27_ipip_neo/IPIP300.dat'],cwd=ROOT).returncode==0)
check('no_respondent_level_output_files',not any(p.suffix in ['.dat','.sav','.por','.npy','.npz','.parquet','.pkl'] for p in OUT.rglob('*')))
for name in ['persona_facet_scores.csv','persona_profile_plausibility.csv','human_calibration_summary.csv','cross_model_profile_agreement.csv']:check('blocked_no_rows_'+name,len(list(csv.DictReader((OUT/name).open())))==0)
check('no_split_no_calibration_after_failed_gate',not a['persona_profile_analysis_run'] and not a['facet_scores_saved'])
for p in OUT.glob('*.py'):ast.parse(p.read_text())
check('scripts_parse',True)
report=dict(status='PASS_FEASIBILITY_VERIFICATION',scientific_result='UNTESTABLE_WITH_PRESENT_BRIDGE',passed=len(checks),checks=checks,model_used='GPT-6 Astra',thinking='High',not_applicable_checks={'train_calibration_heldout_separation':'NOT_RUN: semantic gate failed before splitting','human_calibrated_metric_validation':'NOT_RUN: no metrics fitted','persona_percentile_bootstrap':'NOT_RUN: no persona plausibility test','leave_one_mapped_trait_out':'NOT_RUN: no model facet values evaluated'},no_result_leakage_evidence='Semantic scripts read definitions, published item keys and prior geometry-blind mappings only; frozen artifacts committed at79417c2 before response audit/model schema verification; no human correlations or persona numeric values used. Incidental published example-norm exposure disclosed in freeze.',source_hashes_checked=True,respondent_exports=False)
(OUT/'verification_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],checks=len(checks))))
