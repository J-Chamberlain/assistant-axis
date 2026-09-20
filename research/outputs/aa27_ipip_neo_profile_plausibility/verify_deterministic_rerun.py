#!/usr/bin/env python3
"""Regenerate aggregates and semantic artifacts, requiring byte-identical results."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil,time
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
PYSCI='/tmp/aa17venv/bin/python';PYBUNDLE='/Users/alfred/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
names=['density_audit.json','item_missingness.csv','respondent_missingness_distribution.csv','human_facet_eligibility.csv','demographic_summary.csv','ipip_facet_scoring_specification.csv','official_key_verification.csv','scoring_key_verification.json','model_trait_ipip_facet_crosswalk.csv','facet_bridge_coverage.csv','domain_bridge_coverage.csv','bridge_validity_gate.json','freeze_manifest.json','semantic_source_inventory.csv']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected={n:sha(OUT/n) for n in names};start=time.time()
with tempfile.TemporaryDirectory(prefix='aa27_repro_') as td:
 tmp=Path(td)
 for name in ['semantic_judgments.tsv','analysis_freeze.md']:shutil.copyfile(OUT/name,tmp/name)
 for script,py in [('extract_scoring_spec.py',PYBUNDLE),('build_crosswalk.py',PYSCI),('audit_dataset.py',PYSCI)]:
  text=(OUT/script).read_text();needle='OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]';assert needle in text;text=text.replace(needle,f'OUT=Path({str(tmp)!r});ROOT=Path({str(ROOT)!r})');p=tmp/script;p.write_text(text)
  r=subprocess.run([py,str(p)],cwd=ROOT,capture_output=True,text=True);assert r.returncode==0,(script,r.stderr[-2000:])
 actual={n:sha(tmp/n) for n in names};equal={n:actual[n]==expected[n] for n in names};assert all(equal.values()),equal
 result=dict(status='PASS',byte_identical_artifacts=equal,artifact_count=len(names),temporary_rerun_removed=True,respondent_profiles_saved=False,persona_values_evaluated=False,random_operations='None in executed feasibility pipeline; conditional unexecuted comparison seed20260920',seconds=round(time.time()-start,3))
(OUT/'deterministic_rerun_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='PASS',identical_artifacts=len(names))))
