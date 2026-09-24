#!/usr/bin/env python3
# Read-only metadata audit. Prints JSON; does not run models or extraction.
import os,json,csv,hashlib,collections,zipfile,pickletools,subprocess
from pathlib import Path
root=Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
os.chdir(root)
def records(p):
 p=Path(p)
 return [json.loads(x) for x in p.open() if x.strip()] if p.suffix==".jsonl" else list(csv.DictReader(p.open()))
def digest(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
 return h.hexdigest()
def tensor_meta(p):
 with zipfile.ZipFile(p) as z:
  name=next(n for n in z.namelist() if n.endswith("data.pkl"))
  b=z.read(name)
 ops=list(pickletools.genops(b)); dims=[]; globals_=[]
 for i,(o,a,_) in enumerate(ops):
  if o.name=="GLOBAL": globals_.append(a)
  if o.name=="BINPERSID":
   seq=ops[i+1:i+5]
   if seq[-1][0].name=="TUPLE2": dims.append([seq[1][1],seq[2][1]])
   elif seq[2][0].name=="TUPLE1": dims.append([seq[1][1]])
 return {"shape":dims,"globals":globals_}
out={"base_commit":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),"branch":subprocess.check_output(["git","branch","--show-current"],text=True).strip(),"working_tree":subprocess.check_output(["git","status","--short"],text=True),"aggregates":[],"runs":[],"sources":[],"search":[]}
traits=json.loads(Path("data/traits/trait_list.json").read_text())
roles=sorted(p.stem for p in Path("data/roles/instructions").glob("*.json") if p.stem!="default")
out["roles"]=roles;out["traits"]=sorted(traits);out["gregarious_definition"]=traits["gregarious"]
for model in ["qwen-3-32b","llama-3.3-70b","gemma-2-27b"]:
 for kind,names in [("persona",roles),("trait",sorted(traits))]:
  for name in names:
   p=Path("downloads/hf_vectors")/model/("role_vectors" if kind=="persona" else "trait_vectors")/(name+".pt")
   d={"model":model,"kind":kind,"name":name,"path":str(p),"exists":p.exists()}
   if p.exists(): d.update(bytes=p.stat().st_size,sha256=digest(p),tensor=tensor_meta(p))
   out["aggregates"].append(d)
base=Path("research/q2_stability/qwen/outputs/paper1_5")
runs=[("trickster_phase1_1200","trickster",base/"trickster_phase1.jsonl"),("editor_phase1_128","editor",base/"editor/editor_phase1_128.jsonl"),("editor_matched64_1024","editor",base/"editor_token_cap_sensitivity/editor_phase1_matched64_1024.jsonl")]
for run,role,p in runs:
 ds=records(p); paths=[base/d["activation_relpath"] for d in ds]
 shapes=collections.Counter();totalbytes=0;missing=[]
 for ap in paths:
  if not ap.exists():missing.append(str(ap));continue
  tm=tensor_meta(ap); shapes[json.dumps(tm)]+=1;totalbytes+=ap.stat().st_size
 out["runs"].append({"run":run,"role":role,"path":str(p),"n":len(ds),"unique_ids":len({(d["sp_idx"],d["q_idx"]) for d in ds}),"unique_prompts":len({d["sp_idx"] for d in ds}),"unique_questions":len({d["q_idx"] for d in ds}),"activation_dir":str(paths[0].parent),"activation_bytes":totalbytes,"missing_shards":missing,"shapes":dict(shapes),"truncated":sum(bool(d.get("truncated")) for d in ds),"source_sha256":digest(p),"bytes":p.stat().st_size})
pilot=Path("research/outputs/a100_two_role_activation_cloud_pilot/activation_cloud_per_response.csv")
ds=records(pilot)
for role in sorted({d["role"] for d in ds}):
 sub=[d for d in ds if d["role"]==role]
 out["runs"].append({"run":"a100_two_role_pilot","role":role,"path":str(pilot),"n":len(sub),"unique_ids":len({d["response_id"] for d in sub}),"unique_prompts":len({d["instruction_id"] for d in sub}),"unique_questions":len({d["question_id"] for d in sub}),"errors":sum(bool(d["error_flag"]) for d in sub),"bytes":pilot.stat().st_size,"source_sha256":digest(pilot)})
p=base/"trickster_replication_pilot.partial.jsonl";ds=records(p)
out["runs"].append({"run":"trickster_inline_partial_104","role":"trickster","path":str(p),"n":len(ds),"unique_ids":len({(d["system_prompt_index"],d["question_id"]) for d in ds}),"unique_prompts":len({d["system_prompt_index"] for d in ds}),"unique_questions":len({d["question_id"] for d in ds}),"vector_lengths":dict(collections.Counter(len(d.get("activation_vector") or []) for d in ds)),"scores":dict(collections.Counter(d.get("score") for d in ds)),"norm_range":[min(sum(x*x for x in d["activation_vector"])**0.5 for d in ds),max(sum(x*x for x in d["activation_vector"])**0.5 for d in ds)],"bytes":p.stat().st_size,"source_sha256":digest(p)})
extras=[("h100_percentile_edge_validation","h100_final_results.csv"),("no_label_elicitation_validation","response_level_results.csv"),("no_label_elicitation_run2","run2_response_level_results.csv"),("pc1_accountability_validation","response_level_results.csv")]
for run,file in extras:
 p=Path("research/outputs")/run/file;ds=records(p)
 d={"run":run,"role":"noncanonical elicitation conditions","path":str(p),"n":len(ds),"fields":list(ds[0]),"bytes":p.stat().st_size,"source_sha256":digest(p)}
 if "response_id" in ds[0]:d["unique_ids"]=len({x["response_id"] for x in ds})
 if "activation_shard_path" in ds[0]:
  aps=[root/x["activation_shard_path"] if not x["activation_shard_path"].startswith("/") else root/x["activation_shard_path"].split("/assistant-axis/")[-1] for x in ds]
  d["shards_local"]=sum(x.exists() for x in aps); d["shard_example"]=str(aps[0]);d["shard_bytes"]=sum(x.stat().st_size for x in aps if x.exists())
 d["component_counts"]=dict(collections.Counter(x.get("component",x.get("family",x.get("experiment","all")) ) for x in ds))
 out["runs"].append(d)
for rel in ["research/outputs/persona_cloud_geometry_audit","research/outputs/activation_cloud_layered_viewer","research/outputs/recovered_role_cloud_analysis","research/outputs/prior_adaptive_recovery_audit","research/outputs/a100_two_role_activation_cloud_pilot","research/outputs/a100_activation_cloud_posthoc_analysis","research/outputs/extraction_equivalence_audit","research/outputs/public_source_extraction_equivalence","research/outputs/role_rollout_artifact_audit","data/traits/instructions/gregarious.json","data/traits/trait_list.json","data/extraction_questions.jsonl","pipeline","assistant_axis/internals/activations.py","assistant_axis/internals/spans.py","assistant_axis/models.py","research/visualizations/scripts/build_geometry_viz.py"]:
 p=Path(rel);ps=list(p.glob("*")) if p.is_dir() else [p]
 for q in ps:
  if q.is_file() and q.suffix in (".md",".json",".csv",".py",".jsonl"):
   out["sources"].append({"path":str(q),"bytes":q.stat().st_size,"sha256":digest(q)})
print(json.dumps(out))
