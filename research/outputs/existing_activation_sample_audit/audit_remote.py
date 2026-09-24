#!/usr/bin/env python3
# Bounded metadata inspection only; no unpickling or tensor payload download.
import urllib.request,json,struct,pickletools,collections,hashlib
repos=["lu-christina/assistant-axis-vectors","belmore/assistant-axis-vector-prompts","EstherYang119/assistant-axis-outputs"]
out={"releases":[],"third_party":[]}
for repo in repos:
 d=json.load(urllib.request.urlopen("https://huggingface.co/api/datasets/"+repo+"?blobs=true"))
 out["releases"].append({"repo":repo,"revision":d["sha"],"files":d["siblings"]})
 if not repo.startswith("Esther"): continue
 base="https://huggingface.co/datasets/"+repo+"/resolve/"+d["sha"]+"/"
 for entry in d["siblings"]:
  path=entry["rfilename"]
  if "/activations/" not in path: continue
  req=urllib.request.Request(base+path,headers={"Range":"bytes=0-262143"})
  with urllib.request.urlopen(req,timeout=30) as r:
   b=r.read(262144); status=r.status; cr=r.headers.get("Content-Range")
  h=struct.unpack("<4s5H3I2H",b[:30]); n,e=h[-2:]; ops=list(pickletools.genops(b[30+n+e:]))
  strings=[a for o,a,p in ops if o.name in ("BINUNICODE","SHORT_BINUNICODE")]
  keys=[s for s in strings if s.startswith(("pos_p","neg_p"))]
  dims=collections.Counter()
  for i,(o,a,p) in enumerate(ops):
   if o.name=="BINPERSID":
    seq=ops[i+1:i+5]
    if len(seq)==4 and seq[-1][0].name=="TUPLE2": dims[str([seq[1][1],seq[2][1]])]+=1
  role=path.rsplit("/",1)[1][:-3]; run=path.split("/")[1]
  response_path=path.replace("/activations/","/responses/")[:-3]+".jsonl"
  with urllib.request.urlopen(base+response_path,timeout=30) as r: first=json.loads(r.readline(65536))
  score_path=path.replace("/activations/","/scores/")[:-3]+".json"
  scores={}
  if any(x["rfilename"]==score_path for x in d["siblings"]):
   scores=json.load(urllib.request.urlopen(base+score_path))
  out["third_party"].append({"path":path,"role":role,"run":run,"range_status":status,"content_range":cr,"header_bytes":len(b),"header_sha256":hashlib.sha256(b).hexdigest(),"pickle_stop_offset":ops[-1][2],"sample_count":len(keys),"unique_keys":len(set(keys)),"key_sha256":hashlib.sha256("\n".join(sorted(keys)).encode()).hexdigest(),"key_examples":keys[:2]+keys[-2:],"shapes":dict(dims),"storage_globals":[a for o,a,p in ops if o.name=="GLOBAL"],"prompt_indices":sorted({int(k.split("_p")[1].split("_q")[0]) for k in keys}),"question_indices":sorted({int(k.split("_q")[1]) for k in keys}),"response_path":response_path,"response_fields":list(first),"first_response_key":f'{first["label"]}_p{first["prompt_index"]}_q{first["question_index"]}',"first_prompt":first.get("system_prompt"),"first_question":first.get("question"),"score_path":score_path if scores else None,"score_count":len(scores),"score_counts":dict(collections.Counter(scores.values())),"scores_without_activations":len(set(scores)-set(keys)),"activations_without_scores":len(set(keys)-set(scores)),"bytes":entry["size"]})
print(json.dumps(out))
