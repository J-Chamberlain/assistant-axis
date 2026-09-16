#!/usr/bin/env python3
"""Reconstruct frozen SAPA HiFWB and Big Five scores from an external matrix.

Raw respondent data stay outside git.  The path is supplied with --data-dir.
"""
from __future__ import annotations
import argparse, hashlib, json, platform
from pathlib import Path
import numpy as np, pandas as pd

DIRECT=["q_2765","q_1371","q_1043","q_208","q_206","q_1578","q_875","q_285","q_820","q_1044","q_867","q_4288","q_832"]
DIRECT_SIGN={"q_2765":1,"q_1371":1,"q_1043":1,"q_208":-1,"q_206":-1,"q_1578":1,"q_875":-1,"q_285":1,"q_820":1,"q_1044":-1,"q_867":-1,"q_4288":-1,"q_832":1}
DOMAINS={"Agreeableness":"IPIP100agree","Conscientiousness":"IPIP100consc","Extraversion":"IPIP100extra","Emotional Stability":"IPIP100stability","Openness":"IPIP100intel"}

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',required=True); ap.add_argument('--out-dir',default=str(Path(__file__).parent)); a=ap.parse_args()
 data=Path(a.data_dir); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
 tab=data/'sapaTempData696items08dec2013thru26jul2014.tab'; keyp=data/'superKey696.csv'; info=data/'ItemInfo696.csv'
 key=pd.read_csv(keyp,encoding_errors='replace'); ids=key['Unnamed: 0'].astype(str).tolist()
 frame=pd.read_csv(tab,sep='\t',usecols=['RID',*ids],low_memory=False); vals=frame[ids].apply(pd.to_numeric,errors='coerce').to_numpy(float)
 # item keyed z scores, using training-independent frozen source cohort parameters
 signs=np.array([DIRECT_SIGN.get(i,1) for i in ids]); x=vals.copy(); x[:,signs<0]=7-x[:,signs<0]
 mu=np.nanmean(x,axis=0); sd=np.nanstd(x,axis=0,ddof=1); sd[(~np.isfinite(sd))|(sd==0)]=1; z=(x-mu)/sd
 d=z[:,[ids.index(i) for i in DIRECT]]; wellbeing=np.nanmean(d,axis=1); eligible=np.isfinite(d).sum(1)>=2
 bf={}; bf_n={}
 for name,col in DOMAINS.items():
  ii=key.loc[key[col]!=0,'Unnamed: 0'].astype(str).tolist(); ss=key.loc[key[col]!=0,col].astype(int).to_numpy(); jj=[ids.index(i) for i in ii]; zz=vals[:,jj].astype(float); zz[:,ss<0]=7-zz[:,ss<0]; m=np.nanmean(zz,axis=0); s=np.nanstd(zz,axis=0,ddof=1); s[(~np.isfinite(s))|(s==0)]=1; zz=(zz-m)/s; bf[name]=np.nanmean(zz,axis=1); bf_n[name]=np.isfinite(zz).sum(1)
 bfmat=np.column_stack([bf[n] for n in DOMAINS]); bfok=np.all(np.column_stack([bf_n[n]>=2 for n in DOMAINS]),axis=1)
 summary={'dataset':'SAPA V5','rows':int(len(frame)),'columns':int(vals.shape[1]+1),'observed_cells':int(np.isfinite(vals).sum()),'respondent_sha256':sha(tab),'respondent_bytes':tab.stat().st_size,'superkey_sha256':sha(keyp),'item_info_sha256':sha(info),'frozen_outcome_eligible_N':int(eligible.sum()),'frozen_bigfive_eligible_N':int(bfok.sum()),'outcome_mean':float(np.nanmean(wellbeing[eligible])),'outcome_sd':float(np.nanstd(wellbeing[eligible],ddof=1)),'bigfive_summary':{n:{'N':int(bfok.sum()),'mean':float(np.nanmean(bf[n][bfok])),'sd':float(np.nanstd(bf[n][bfok],ddof=1))} for n in DOMAINS},'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__}
 (out/'frozen_score_reconstruction.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
