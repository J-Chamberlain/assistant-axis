#!/usr/bin/env python3
from liss_common import *
require_files(CP, SS)
try:
 import pandas as pd
except Exception as e: print(e); raise SystemExit(2)
print({"status":"scoring_ready","cp_rows":len(pd.read_stata(CP,iterator=True).read(0)),"ss_rows":len(pd.read_stata(SS,iterator=True).read(0)),"output":"aggregates only"})
