"""Integrity checks for the aggregate Rosetta study."""
from pathlib import Path
import json, hashlib
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"research/outputs/human_model_rosetta_translation"
required=["analysis_freeze.md","source_provenance.md","anchor_target_partition.csv","matched_cluster_profiles.csv","matched_cluster_profile_residuals.csv","matched_cluster_summary.csv","translation_cv_predictions.csv","translation_model_comparison.csv","translation_null_results.csv","translation_stability_summary.csv","model_replication_summary.csv","human_model_rosetta_translation_report.md","run_rosetta_translation.py"]
checks=[]
def ck(name, ok, detail=""): checks.append({"name":name,"status":"PASS" if ok else "FAIL","detail":detail})
for f in required: ck(f"required artifact: {f}",(OUT/f).is_file())
part=pd.read_csv(OUT/"anchor_target_partition.csv"); ck("12 anchors and 33 targets",int((part.role=="anchor").sum())==12 and int((part.role=="target").sum())==33)
cv=pd.read_csv(OUT/"translation_cv_predictions.csv"); ck("24 folds per method",set(cv.groupby("method").size())=={24})
null=pd.read_csv(OUT/"translation_null_results.csv"); ck("three complete null families",set(null.null)=={"cluster_pairing","trait_label","joint_structure"} and set(null.draws)=={2000} and set(null.status)=={"complete"})
ck("no tracked respondent/private outputs",not any("sapaTempData" in x or "heldout_predictions" in x for x in __import__("subprocess").check_output(["git","-C",str(ROOT),"ls-files"],text=True).splitlines()))
inventory=[]
for f in sorted(OUT.rglob("*")):
 if f.is_file(): inventory.append({"path":str(f.relative_to(ROOT)),"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"status":"canonical" if f.name in required or f.name in {"verification_report.json","artifact_inventory.csv"} else "active"})
pd.DataFrame(inventory).to_csv(OUT/"artifact_inventory.csv",index=False)
result={"status":"PASS" if all(c["status"]=="PASS" for c in checks) else "FAIL","checks_passed":sum(c["status"]=="PASS" for c in checks),"checks_total":len(checks),"checks":checks}
(OUT/"verification_report.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
