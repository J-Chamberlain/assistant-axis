#!/usr/bin/env python3
import json
from liss_common import *
require_files(CP, SS)
print(json.dumps({"status":"files_present","files":{CP.name:{"bytes":CP.stat().st_size,"sha256":sha256(CP)},SS.name:{"bytes":SS.stat().st_size,"sha256":sha256(SS)}}},indent=2))
