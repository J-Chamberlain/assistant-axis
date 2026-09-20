#!/usr/bin/env python3
"""Aggregate-only source/density audit. No facet-distribution or plausibility fitting."""
from pathlib import Path
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np,pandas as pd,json,hashlib,collections
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];RAW=ROOT/'data_external/aa27_ipip_neo'
def digest(x):return hashlib.sha256(x).hexdigest()
def jsave(name,x):(OUT/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
b=(RAW/'IPIP300.dat').read_bytes();assert digest(b)=='1bbb7189f5f0f2883bb4493f956cf639178c5c8ee95319fd3881f6d9d2f189a3'
lines=b.splitlines();n=len(lines);assert n==307313;lengths=collections.Counter(map(len,lines));assert set(lengths)=={333},lengths
# Never retain CASE/date/time. Countries appear only as counts with small cells suppressed.
X=np.empty((n,300),dtype=np.uint8);age=np.empty(n,dtype=int);sex=np.empty(n,dtype=int);countries=[]
for i,line in enumerate(lines):
 X[i]=np.frombuffer(line[33:333],dtype=np.uint8)-48
 age[i]=int(line[7:9]) if line[7:9].strip() else -1
 sex[i]=int(line[6:7]) if line[6:7].strip() else -1
 countries.append(line[22:33].decode('ascii',errors='replace').strip().upper())
assert X.min()>=0 and X.max()<=5
spec=pd.read_csv(OUT/'ipip_facet_scoring_specification.csv');obs=X!=0;validfacet=np.column_stack([obs[:,g.item_number.to_numpy()-1].sum(1) for _,g in spec.groupby('facet_code',sort=True)])
complete=obs.all(1);near=(validfacet>=9).all(1);adult=(age>=18)&(age<=80);primary=complete&adult;sensitivity=near&adult
assert np.array_equal(complete,(validfacet==10).all(1))
miss=300-obs.sum(1);pd.DataFrame(dict(item_number=np.arange(1,301),observed_n=obs.sum(0),missing_n=(~obs).sum(0),missing_fraction=(~obs).mean(0))).to_csv(OUT/'item_missingness.csv',index=False)
v,c=np.unique(miss,return_counts=True);pd.DataFrame(dict(missing_item_count=v,respondents=c)).to_csv(OUT/'respondent_missingness_distribution.csv',index=False)
fac=[]
for j,(f,sp) in enumerate(spec.groupby('facet_code',sort=True)):fac.append(dict(facet_code=f,facet=sp.facet.iloc[0],items=len(sp),full_item_count_n=int((validfacet[:,j]==10).sum()),at_least_9_items_n=int((validfacet[:,j]>=9).sum())))
pd.DataFrame(fac).to_csv(OUT/'human_facet_eligibility.csv',index=False)
demo=[]
for cohort,mask in [('all_raw',np.ones(n,dtype=bool)),('complete_adults_18_80',primary)]:
 for code,num in collections.Counter(sex[mask]).items():demo.append(dict(cohort=cohort,variable='sex_code',category={1:'male',2:'female'}.get(int(code),'other_or_missing_code'),n=int(num)))
 for label,lo,hi in [('missing',-1,-1),('under18',0,17),('18_29',18,29),('30_44',30,44),('45_59',45,59),('60_80',60,80),('over80',81,99)]:demo.append(dict(cohort=cohort,variable='age_band',category=label,n=int((mask&(age>=lo)&(age<=hi)).sum())))
 cc=collections.Counter(x for x,ok in zip(countries,mask) if ok);supp=0
 for code,num in cc.items():
  if num>=100 and code:demo.append(dict(cohort=cohort,variable='country_reported_code',category=code,n=num))
  else:supp+=num
 demo.append(dict(cohort=cohort,variable='country_reported_code',category='OTHER_SMALL_CELLS_OR_BLANK',n=supp))
pd.DataFrame(demo).to_csv(OUT/'demographic_summary.csv',index=False)
sg=spec.sort_values('item_number').original_response_sign.to_numpy();rawcat=np.where(sg[None,:]<0,6-X,X);rawcat=np.where(obs,rawcat,0);rekey=np.where(sg[None,:]<0,6-rawcat,rawcat);rekey=np.where(obs,rekey,0)
assert np.array_equal(rekey,X)
# Independent streaming parser: exact all-300 completion and 9/10 masks, no vectorized grouping.
lookup={f:sp.item_number.to_list() for f,sp in spec.groupby('facet_code')};cnt_complete=cnt_adult=cnt_near=cnt_near_adult=0
for row in lines:
 item=row[33:333];full=b'0' not in item;a=int(row[7:9]) if row[7:9].strip() else -1;adult2=18<=a<=80
 close=all(sum(item[k-1]!=48 for k in inds)>=9 for inds in lookup.values())
 cnt_complete+=full;cnt_adult+=full and adult2;cnt_near+=close;cnt_near_adult+=close and adult2
assert (cnt_complete,cnt_adult,cnt_near,cnt_near_adult)==(int(complete.sum()),int(primary.sum()),int(near.sum()),int(sensitivity.sum()))
audit=dict(status='PASS_DENSE_REFERENCE',respondents=n,item_columns=300,record_bytes=333,response_codes=[0,1,2,3,4,5],missing_code=0,scale='1–5, already reverse-keyed in released file',overall_missing_fraction=float((~obs).mean()),complete_30facets_all_ages=int(complete.sum()),complete_30facets_adults_18_80=int(primary.sum()),near_complete_9_of10_all_30facets_all_ages=int(near.sum()),near_complete_9_of10_all_30facets_adults_18_80=int(sensitivity.sum()),primary_eligible_hash=digest(primary.tobytes()),sensitivity_eligible_hash=digest(sensitivity.tobytes()),missing_item_quantiles={str(q):float(np.quantile(miss,q)) for q in [0,.25,.5,.75,.9,.99,1]},at_least_5000_primary=int(primary.sum())>=5000,negative_item_keys=int((sg<0).sum()),reverse_roundtrip_all_cells=True,independent_eligibility_parser_matches=True,facet_scores_saved=False,profile_distributions_inspected=False,persona_profile_analysis_run=False,respondent_rows_exported=False)
assert audit['at_least_5000_primary'];jsave('density_audit.json',audit)
print(json.dumps(audit,indent=2))
