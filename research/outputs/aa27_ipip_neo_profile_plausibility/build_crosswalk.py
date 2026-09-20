#!/usr/bin/env python3
"""Semantic-only Cartesian crosswalk. No respondent values or model values read."""
from pathlib import Path
import csv,io,json,hashlib,subprocess,collections
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE='91ad7519fe89b55921f58680a9a734e158320ca4'
def readblob(path):
 b=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT);return b,list(csv.DictReader(io.StringIO(b.decode())))
source='research/outputs/externally_anchored_big_five/external_taxonomy_expanded_trait_mapping.csv';b,traits=readblob(source)
strict_source='research/outputs/externally_anchored_big_five/human_anchored_strict_trait_mapping.csv';b2,prior=readblob(strict_source);prior_by={r['trait']:r for r in prior}
assert len(traits)==240 and len({r['trait'] for r in traits})==240
items=list(csv.DictReader((OUT/'ipip_facet_scoring_specification.csv').open()));facets={r['facet_code']:(r['facet'],r['domain']) for r in items};assert len(facets)==30
judgments=list(csv.DictReader((OUT/'semantic_judgments.tsv').open(),delimiter='\t'));j={(r['trait'],r['facet']):r for r in judgments};assert len(j)==len(judgments)
assert set(r['trait'] for r in judgments)<={r['trait'] for r in traits}
rows=[]
for t in traits:
 for f in sorted(facets):
  r=j.get((t['trait'],f));tier='none';pol=0;group=t['trait'];rationale=f"The canonical definition describes {t['canonical_definition'].rstrip('.')} No explicit or close link to the {facets[f][0]} item family was identified."
  if t['facet_code']==f:
   tier='broad';pol={'positive':1,'negative':-1}.get(t['polarity'],0);rationale='Prior AA25 domain-level candidate retained as excluded broad evidence only; no direct/close item-content match accepted in this review. Prior rationale: '+t['mapping_rationale']
  if r:tier=r['tier'];pol=int(r['polarity']);group=r['alias_group'];rationale=r['rationale']
  rows.append(dict(model_trait=t['trait'],canonical_definition=t['canonical_definition'],facet_code=f,facet=facets[f][0],domain=facets[f][1],polarity=pol,mapping_tier=tier,semantic_rationale=rationale,evidence_source=f'{BASE}:{source}; official IPIP newNEOFacetsKey.htm#{facets[f][0]}; Johnson workbook Input',duplicate_group=f+':'+str(pol)+':'+group,confidence={'direct':'high','close':'moderate','broad':'low','none':'not_supported'}[tier],strict_included=False,expanded_included=False,prior_AA25_facet=t['facet_code'],prior_AA25_relation=t['direct_or_proxy'],prior_AA21_strict_facet=prior_by.get(t['trait'],{}).get('external_facet_code',''),model_used='GPT-6 Astra',thinking='High'))
# Same-pole near-alias removal: one deterministic representative per semantic group.
for mode,tiers in [('strict',{'direct'}),('expanded',{'direct','close'})]:
 by=collections.defaultdict(list)
 for r in rows:
  if r['mapping_tier'] in tiers:by[r['duplicate_group']].append(r)
 for group,rs in by.items():
  first=sorted(rs,key=lambda r:({'direct':0,'close':1}[r['mapping_tier']],r['model_trait']))[0];first[mode+'_included']=True
coverage=[]
for f,(name,domain) in sorted(facets.items()):
 ss=[r for r in rows if r['facet_code']==f];r=dict(facet_code=f,facet=name,domain=domain)
 for mode in ['strict','expanded']:
  tt=[x for x in ss if x[mode+'_included']];poles=set(x['polarity'] for x in tt)
  r[mode+'_traits']=';'.join(x['model_trait']+('+' if x['polarity']>0 else '-') for x in tt);r[mode+'_n']=len(tt);r[mode+'_retained']=len(tt)>=2;r[mode+'_one_sided']=len(poles)==1 if tt else None;r[mode+'_alias_removed_n']=sum(x['mapping_tier'] in ({'direct'} if mode=='strict' else {'direct','close'}) for x in ss)-len(tt)
 coverage.append(r)
for r in rows:
 c=next(x for x in coverage if x['facet_code']==r['facet_code']);r['strict_facet_retained']=c['strict_retained'];r['expanded_facet_retained']=c['expanded_retained'];r['strict_score_included']=r['strict_included'] and c['strict_retained'];r['expanded_score_included']=r['expanded_included'] and c['expanded_retained']
def save(p,data):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
save(OUT/'model_trait_ipip_facet_crosswalk.csv',rows);save(OUT/'facet_bridge_coverage.csv',coverage)
domain=[]
for d in ['Neuroticism','Extraversion','Openness','Agreeableness','Conscientiousness']:
 rr=[r for r in coverage if r['domain']==d];domain.append(dict(domain=d,strict_facets=sum(r['strict_retained'] for r in rr),expanded_facets=sum(r['expanded_retained'] for r in rr),required=3))
save(OUT/'domain_bridge_coverage.csv',domain)
strict_n=sum(r['strict_retained'] for r in coverage);expanded_n=sum(r['expanded_retained'] for r in coverage);passed=strict_n>=18 and all(r['strict_facets']>=3 for r in domain)
gate=dict(status='PASS' if passed else 'FAIL_UNTESTABLE_PRESENT_BRIDGE',strict_retained_facets=strict_n,expanded_retained_facets=expanded_n,required_total=18,required_per_domain=3,required_nonduplicate_traits_per_facet=2,domain_coverage=domain,expanded_cannot_rescue_primary=True,respondent_distribution_read=False,persona_value_read=False,crosswalk_rows=len(rows),traits=240,facets=30,judged_nondefault_pairs=len(judgments),model_used='GPT-6 Astra',thinking='High')
(OUT/'bridge_validity_gate.json').write_text(json.dumps(gate,indent=2)+'\n')
save(OUT/'semantic_source_inventory.csv',[dict(path=source,commit=BASE,sha256=hashlib.sha256(b).hexdigest(),role='canonical definitions and prior AA25 candidate taxonomy'),dict(path=strict_source,commit=BASE,sha256=hashlib.sha256(b2).hexdigest(),role='prior AA21 semantic facets only; no correlations or outcomes')])
freeze_files=['analysis_freeze.md','semantic_judgments.tsv','model_trait_ipip_facet_crosswalk.csv','facet_bridge_coverage.csv','domain_bridge_coverage.csv','ipip_facet_scoring_specification.csv','bridge_validity_gate.json']
(OUT/'freeze_manifest.json').write_text(json.dumps(dict(model_used='GPT-6 Astra',thinking='High',policy_commit='6d564c3',base_commit=BASE,before_profile_comparison=True,human_data_file_acquired_but_values_not_read=True,files=[dict(path=n,sha256=hashlib.sha256((OUT/n).read_bytes()).hexdigest(),bytes=(OUT/n).stat().st_size) for n in freeze_files]),indent=2)+'\n')
print(json.dumps(gate,indent=2))
