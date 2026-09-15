#!/usr/bin/env python3
from liss_common import *
require_files(CP, SS)
print({"status":"measurement_fit_ready","models":["general","correlated_contents","higher_order","bifactor_or_esem_if_identified"],"seed":11011,"output":"aggregate fit indices only"})
