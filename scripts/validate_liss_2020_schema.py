#!/usr/bin/env python3
import sys
from liss_common import *
require_files(CP, SS)
try:
 import pandas as pd
except Exception as e:
 print(f"pandas required after data arrival: {e}", file=sys.stderr); raise SystemExit(2)
cp=pd.read_stata(CP, iterator=True).read(0); ss=pd.read_stata(SS, iterator=True).read(0)
required_cp=[f"cp20l{i:03d}" for i in range(20,70)]
required_ss=["ss20a001"]+[f"ss20a{i:03d}" for i in range(2,72)]
missing=[x for x in required_cp if x not in cp.columns]+[x for x in required_ss if x not in ss.columns]
if missing: print({"missing_columns":missing}); raise SystemExit(2)
print({"status":"schema_ok","cp_rows":len(cp),"ss_rows":len(ss)})
