#!/usr/bin/env python3
"""Read-only extraction of Johnson workbook Input sheet, checked against official IPIP HTML."""
from pathlib import Path
import csv,json,re,hashlib
from html.parser import HTMLParser
import openpyxl
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];RAW=ROOT/'data_external/aa27_ipip_neo'
w=openpyxl.load_workbook(RAW/'IPIP-NEO-300 scoring tool_2.xlsx',read_only=True,data_only=False)
rows=[]
for row in w['Input'].iter_rows(min_row=2,max_row=301,values_only=True):
 i,sign,key,facet,text=row[:5];assert key==sign[1:];assert i==len(rows)+1
 rows.append(dict(item_number=i,facet_code=key,facet=facet,domain={'N':'Neuroticism','E':'Extraversion','O':'Openness','A':'Agreeableness','C':'Conscientiousness'}[key[0]],wording=text,original_response_sign=1 if sign[0]=='+' else -1,downloaded_data_already_keyed=True,download_transform='identity; zero becomes missing',raw_response_reverse_formula='6-x' if sign[0]=='-' else 'x',primary_minimum_observed=10,sensitivity_minimum_observed=9,source='https://osf.io/download/4w86n/',official_item_key_source='https://ipip.ori.org/newNEOFacetsKey.htm'))
assert len(rows)==300 and len(set(r['facet_code'] for r in rows))==30
class P(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.cur=[];self.cell='';self.intd=False;self.facet=None
 def handle_starttag(self,t,a):
  if t=='tr':self.cur=[]
  if t=='td':self.intd=True;self.cell=''
 def handle_data(self,d):
  m=re.search(r'([NEOAC][1-6]):',d)
  if m:self.facet=m.group(1)
  if self.intd:self.cell+=d
 def handle_endtag(self,t):
  if t=='td':self.cur.append(' '.join(self.cell.split()));self.intd=False
  if t=='tr' and self.cur:self.rows.append((self.facet,self.cur.copy()))
p=P();p.feed((RAW/'official_facet_keys.html').read_text(encoding='latin1'))
def norm(t):
 t=t.replace('no absolute right or wrong','no absolute right and wrong')
 if t in ['Interested in many things.','Willing to try anything once.']:t='Am '+t[0].lower()+t[1:]
 return re.sub(r'[^a-z0-9]','',t.lower())
off={};facet=None;sg=None
for ff,rr in p.rows:
 if ff!=facet:facet=ff;sg=None
 if not facet:continue
 if 'keyed' in rr[0]:sg=1 if '+' in rr[0] else -1
 if len(rr)>1 and rr[1] and sg is not None:off[(facet,norm(rr[1]))]=sg
checks=[]
for r in rows:checks.append(dict(item_number=r['item_number'],facet_code=r['facet_code'],official_html_sign=off.get((r['facet_code'],norm(r['wording']))),workbook_sign=r['original_response_sign']))
bad=[r for r in checks if r['official_html_sign']!=r['workbook_sign']]
print('official HTML extracted',len(off),'key discrepancies',bad[:5])
assert not bad
for filename,data in [('ipip_facet_scoring_specification.csv',rows),('official_key_verification.csv',checks)]:
 with (OUT/filename).open('w',newline='') as f:wr=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');wr.writeheader();wr.writerows(data)
(OUT/'scoring_key_verification.json').write_text(json.dumps(dict(status='PASS',items=300,facets=30,negative_keys=sum(r['original_response_sign']<0 for r in rows),official_html_item_sign_matches=300,documented_wording_variants=[58,78,202],reverse_twice_prohibited=True,downloaded_data_documentation='https://osf.io/download/2kfhe/',workbook_input_only=True),indent=2)+'\n')
