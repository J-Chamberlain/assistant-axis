#!/usr/bin/env python3
# Verify stored projections against their source rows.
import json,csv,hashlib,collections,os,platform
from pathlib import Path
os.chdir("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
paths=["../persona-human-geometry/AGENTS.md","../persona-human-geometry/RESEARCH_STATE.md","../persona-human-geometry/PROVENANCE.md","../persona-human-geometry/research/outputs/aa15_hifwb_trait_pc/aa14_extraction_provenance_erratum.md","../persona-human-geometry/research/outputs/aa27_ipip_neo_profile_plausibility/aa27_report.md","../persona-human-geometry/research/outputs/aa27_ipip_neo_profile_plausibility/facet_bridge_coverage.csv","../persona-human-geometry/research/outputs/aa27_ipip_neo_profile_plausibility/ipip_facet_scoring_specification.csv","../persona-human-geometry/research/outputs/aa27_ipip_neo_profile_plausibility/model_trait_ipip_facet_crosswalk.csv"]
sources=[{"path":p,"bytes":Path(p).stat().st_size,"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in paths]
v=json.load(open("research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json"));points=v["points"]
source=list(csv.DictReader(open("research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv")))+list(csv.DictReader(open("research/outputs/prior_adaptive_recovery_audit/prior_adaptive_corrected_coordinates.csv")))
lookup={d["response_id"]:d for d in source}
maxdiff=max(abs(float(p[k])-float(lookup[p["response_id"]][k])) for p in points for k in ("pc1","pc2","pc3"))
out={"sources":sources,"python":platform.python_version(),"platform":platform.platform(),"viewer_n":len(points),"viewer_unique_ids":len({p["response_id"] for p in points}),"source_unique_ids":len(lookup),"viewer_source_max_coordinate_error":maxdiff,"viewer_run_counts":dict(collections.Counter(p["role_or_run"] for p in points))}
print(json.dumps(out))
