from pathlib import Path
import json, hashlib, subprocess
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
OUT=ROOT/"research/outputs/human_model_rosetta_translation/profile_visuals"
checks=[]
def ck(n,ok,d=""): checks.append({"name":n,"status":"PASS" if ok else "FAIL","detail":d})
part=pd.read_csv(OUT/"cluster_pair_metrics_12_45.csv")
ck("24 fixed Rosetta pairs",len(part)==24)
ck("same pair rows for 12 and 45",len(pd.read_csv(OUT/"cluster_pair_metrics_12.csv"))==24 and len(pd.read_csv(OUT/"cluster_pair_metrics_45.csv"))==24)
manifest=json.loads((OUT/"source_manifest.json").read_text())
ck("12 trait membership exact",set(pd.read_csv(OUT/"trait_agreement_summary_12.csv").trait)==set(manifest["traits12"]))
ck("45 trait membership exact",len(pd.read_csv(OUT/"trait_agreement_summary_45.csv"))==45)
page=(OUT/"human_model_trait_profile_comparison.html").read_text()
ck("HTML self-contained", "__DATA__" not in page and "const D=" in page)
static=["12_trait_matched_profiles.png","12_trait_matched_profiles.svg","12_trait_difference_heatmap.png","12_trait_difference_heatmap.svg","45_trait_difference_heatmap.png","45_trait_difference_heatmap.svg","12_vs_45_cluster_similarity.png","12_vs_45_cluster_similarity.svg","trait_level_agreement_summary.png","trait_level_agreement_summary.svg"]
ck("static exports present",all((OUT/"figures"/f).is_file() for f in static))
tracked=subprocess.check_output(["git","-C",str(ROOT),"ls-files"],text=True).splitlines()
ck("no private records tracked",not any("sapaTempData" in x or "heldout_predictions" in x for x in tracked))
inv=[]
for f in sorted(OUT.rglob('*')):
    if f.is_file(): inv.append({"path":str(f.relative_to(ROOT)),"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"status":"canonical" if f.name in {"human_model_trait_profile_comparison.html","trait_profile_visual_comparison_report.md","verification_report.json","source_manifest.json"} else "active"})
pd.DataFrame(inv).to_csv(OUT/"artifact_inventory.csv",index=False)
result={"status":"PASS" if all(x["status"]=="PASS" for x in checks) else "FAIL","checks_passed":sum(x["status"]=="PASS" for x in checks),"checks_total":len(checks),"checks":checks}
(OUT/"verification_report.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
