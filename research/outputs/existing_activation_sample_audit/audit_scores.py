#!/usr/bin/env python3
# Counts existing scores; never calls a judge.
import json,csv,collections,hashlib,os
from pathlib import Path
os.chdir("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
def rows(p):
 p=Path(p);return list(csv.DictReader(p.open())) if p.suffix==".csv" else [json.loads(x) for x in p.open()]
out={"score_sets":[]}
for p,scorefield,groupfield in [
("research/outputs/a100_activation_cloud_posthoc_analysis/gpt41_judge_scores.csv","score_0_to_3","role"),
("research/outputs/gpt55_judge_and_outlier_followup/gpt55_judge_scores.csv","score_0_to_3","role"),
("research/outputs/recovered_role_cloud_analysis/recovered_gpt41_scores.csv","score_0_to_3","source_run_id"),
("research/q2_stability/qwen/outputs/paper1_5/trickster_phase2_scores_codex_gpt55.jsonl","score","persona"),
("research/q2_stability/qwen/outputs/paper1_5/editor/editor_phase2_scores_codex_gpt55.jsonl","score","persona"),
("research/q2_stability/qwen/outputs/paper1_5/editor_token_cap_sensitivity/editor_phase2_scores_1024_codex_gpt55.jsonl","score","persona")]:
 ds=rows(p)
 for group in sorted({d[groupfield] for d in ds}):
  sub=[d for d in ds if d[groupfield]==group];vals=[int(d[scorefield]) for d in sub]
  ids=[d.get("response_id",(d.get("sp_idx"),d.get("q_idx"))) for d in sub]
  out["score_sets"].append({"path":p,"group":group,"n":len(sub),"unique_ids":len(set(ids)),"score_counts":dict(collections.Counter(vals)),"ge2":sum(x>=2 for x in vals),"eq3":sum(x==3 for x in vals),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest(),"bytes":Path(p).stat().st_size})
b=Path("research/q2_stability/qwen/outputs/paper1_5")
editor=rows(b/"editor/editor_phase1_128.jsonl"); cap=rows(b/"editor_token_cap_sensitivity/editor_phase1_matched64_1024.jsonl")
em={(d["sp_idx"],d["q_idx"]):d for d in editor}
out["editor_pairing"]={"matched_keys":sum((d["sp_idx"],d["q_idx"]) in em for d in cap),"identical_text":sum(d["response_text"]==em[(d["sp_idx"],d["q_idx"])]["response_text"] for d in cap)}
partial=rows(b/"trickster_replication_pilot.partial.jsonl");phase=rows(b/"trickster_phase1.jsonl");pm={(d["sp_idx"],d["q_idx"]):d for d in phase}
out["trickster_pairing"]={"matched_context_keys":sum((d["system_prompt_index"],d["question_id"]) in pm for d in partial),"identical_text":sum(d["response_text"]==pm[(d["system_prompt_index"],d["question_id"])]["response_text"] for d in partial)}
d=json.load(open("research/outputs/activation_cloud_layered_viewer/activation_cloud_layered_viewer_data.json"))
out["viewer_fields"]=list(d);print(json.dumps(out))
