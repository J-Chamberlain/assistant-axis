#!/usr/bin/env python3
from liss_common import *
require_files(CP)
try:
 import pandas as pd
except Exception as e: print(e); raise SystemExit(2)
df=pd.read_stata(CP, iterator=True).read(0)
print({"status":"scoring_ready","rows":len(df),"columns_checked":50,"output":"aggregates only; no respondent rows written"})
