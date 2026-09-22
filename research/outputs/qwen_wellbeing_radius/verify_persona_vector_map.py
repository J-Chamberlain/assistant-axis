#!/usr/bin/env python3
import csv,html,json,re
from pathlib import Path
p=Path(__file__).with_name('persona_vector_map.html'); text=p.read_text(); d=json.loads(html.unescape(re.search(r'<script id=data type=application/json>(.*?)</script>',text,re.S).group(1)))
assert d['schema']=='qwen-persona-vector-map-v1' and len(d['personas'])==275 and len(set(d['personas']))==275
assert len(d['coords'])==275 and all(len(x)==5 for x in d['coords'])
rows=d['candidates']; assert len(rows)==11550 and all(__import__('math').isfinite(x) for r in rows for k,x in r.items() if isinstance(x,float))
q=[r for r in rows if r['persona']=='romantic' and r['dimensions']==5 and r['radius_fraction_of_median_fifth_neighbor']==.5 and r['candidate']=='compromise'][0]
for k,v in {'delta_bigfive':.12325726627898526,'delta_direct':.16446656050061703,'delta_PC1':3.7428506931598124,'delta_PC2':-2.4230977981206516,'delta_PC3':-6.8155084299079975,'delta_C1_sd':-.2524369320419315,'delta_C3_sd':.33430350130843817}.items():assert abs(q[k]-v)<1e-12,(k,q[k])
print('PASS: 275 personas, 11,550 saved candidates, romantic medium-radius compromise match')
