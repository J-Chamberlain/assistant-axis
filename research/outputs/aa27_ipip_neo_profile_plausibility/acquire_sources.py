#!/usr/bin/env python3
"""Acquire only documented first-party sources; no respondent parsing/export."""
import urllib.request,json,hashlib,datetime,shutil
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];RAW=ROOT/'data_external/aa27_ipip_neo';RAW.mkdir(parents=True,exist_ok=True)
records=[]
def get(url,path,expected=None):
    if not path.exists():
        with urllib.request.urlopen(url,timeout=60) as r,path.open('wb') as f:shutil.copyfileobj(r,f)
    b=path.read_bytes();h=hashlib.sha256(b).hexdigest()
    if expected:assert h==expected,(path,h)
    records.append(dict(url=url,path=str(path.relative_to(ROOT)),filename=path.name,bytes=len(b),sha256=h,osf_hash_matches=h==expected if expected else None,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),provider='first-party Johnson OSF' if 'osf.io' in url else 'official IPIP'))
    print(path.name,len(b),h,flush=True)
for meta,name in [('osf_wxvth_files.json','IPIP300.dat'),('osf_wxvth_files.json','DAT300.doc'),('osf_ycvdk_files.json','IPIP-NEO-ItemKey.xls'),('osf_ycvdk_files.json','IPIP-NEO-300 scoring tool_2.xlsx')]:
    row=next(x for x in json.loads((OUT/meta).read_text())['data'] if x['attributes']['name']==name)
    get(row['links']['download'],RAW/name,row['attributes']['extra']['hashes']['sha256'])
for name,url in [('official_facet_keys.html','https://ipip.ori.org/newNEOFacetsKey.htm'),('official_permission.html','https://ipip.ori.org/newPermission.htm'),('official_scoring.html','https://ipip.ori.org/newScoringInstructions.htm'),('osf_data_readme.md','https://api.osf.io/v2/wikis/hvndy/content/')]:get(url,RAW/name)
(OUT/'source_manifest.json').write_text(json.dumps(dict(model_used='GPT-6 Astra',thinking='High',repository='https://osf.io/tbmh5/',dataset_node='https://osf.io/wxvth/',key_node='https://osf.io/ycvdk/',sources=records,raw_data_gitignored=True,respondent_outputs_permitted=False),indent=2)+'\n')
