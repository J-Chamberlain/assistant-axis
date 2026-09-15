#!/usr/bin/env python3
from liss_common import *
require_files(CP, SS)
print({"status":"pipeline_ready","steps":["schema","source_hash","score_bigfive","score_hifwb","measurement_models","association_models"],"seed":11011,"no_model_inference":True})
