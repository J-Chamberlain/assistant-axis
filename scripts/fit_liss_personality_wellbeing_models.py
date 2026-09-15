#!/usr/bin/env python3
from liss_common import *
require_files(CP, SS)
print({"status":"association_fit_ready","models":["P0_bigfive_linear","P1_backbone_if_predeclared","P2_ridge_5d","P3_rbf_sensitivity"],"seed":11011,"output":"aggregate coefficients/metrics only"})
