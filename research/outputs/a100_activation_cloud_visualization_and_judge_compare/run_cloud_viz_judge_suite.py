#!/usr/bin/env python3
import csv, json, math, os, time
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from openai import OpenAI, BadRequestError

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
PILOT = REPO / "research/outputs/a100_two_role_activation_cloud_pilot"
POSTHOC = REPO / "research/outputs/a100_activation_cloud_posthoc_analysis"
OUT = REPO / "research/outputs/a100_activation_cloud_visualization_and_judge_compare"
TOOL = REPO / "research/tools/activation_cloud_suite"
OUT.mkdir(parents=True, exist_ok=True)
TOOL.mkdir(parents=True, exist_ok=True)

MODEL_55 = "gpt-5.5"
TEMP = 0
PRICE_INPUT_PER_1M = 2.00
PRICE_OUTPUT_PER_1M = 8.00

RUBRIC = """You are evaluating whether a generated response expresses an assigned role/persona.

Score how strongly the generated response expresses the assigned role/persona.

Use a 0-3 scale:
0 = no meaningful role expression; generic assistant or off-role.
1 = weak role expression; mostly generic assistant behavior.
2 = clear role expression; substantially reflects the role.
3 = strong role expression; vivid and sustained role expression.

Also return:
- binary_retain_ge2: true if score >= 2.
- binary_retain_eq3: true if score == 3.
- generic_assistant_collapse: true/false.
- refusal_or_safety_neutralization: true/false.
- theatrical_overexpression: true/false.
- rationale: concise, max 35 words.

Return strict JSON with exactly these fields:
response_id, role, score_0_to_3, binary_retain_ge2, binary_retain_eq3, generic_assistant_collapse, refusal_or_safety_neutralization, theatrical_overexpression, rationale.

Judge only the supplied role, role instruction, question, and generated response. Do not infer from activation data; none is provided."""

SCHEMA_FIELDS = [
    "response_id", "role", "score_0_to_3", "binary_retain_ge2", "binary_retain_eq3",
    "generic_assistant_collapse", "refusal_or_safety_neutralization",
    "theatrical_overexpression", "rationale",
]


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=None):
    if fieldnames is None:
        keys = []
        for row in rows:
            for k in row:
                if k not in keys:
                    keys.append(k)
        fieldnames = keys
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def jdump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def key():
    v = os.environ.get("OPENAI_API_KEY", "").strip()
    if v:
        return v, "environment"
    p = Path.home() / ".openai_api_key"
    if p.exists() and p.read_text().strip():
        return p.read_text().strip(), "~/.openai_api_key"
    return None, None


def load_inputs():
    rows = []
    with open(PILOT / "judge_input_responses.jsonl") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def activation_rows():
    rows = read_csv(PILOT / "activation_cloud_per_response.csv")
    for r in rows:
        for k in ["pc1", "pc2", "pc3", "distance_to_published_role_centroid_3d",
                  "delta_pc1_from_published_centroid", "delta_pc2_from_published_centroid",
                  "delta_pc3_from_published_centroid"]:
            r[k] = float(r[k])
    return rows


def vec3(rows):
    return np.array([[float(r["pc1"]), float(r["pc2"]), float(r["pc3"])] for r in rows])


def published(rows):
    arr = vec3(rows)
    d = np.array([[float(r["delta_pc1_from_published_centroid"]),
                   float(r["delta_pc2_from_published_centroid"]),
                   float(r["delta_pc3_from_published_centroid"])] for r in rows])
    return (arr - d)[0]


def user_payload(row):
    return (
        f"response_id: {row['response_id']}\n"
        f"role: {row['role']}\n"
        f"role_instruction: {row['system_instruction']}\n"
        f"extraction_question: {row['extraction_question']}\n"
        f"generated_response:\n{row['generated_response']}"
    )


def estimate_tokens(s):
    return max(1, math.ceil(len(s) / 4))


def normalize(obj, row):
    for k in SCHEMA_FIELDS:
        if k not in obj:
            raise ValueError(f"missing {k}")
    out = {k: obj[k] for k in SCHEMA_FIELDS}
    out["response_id"] = row["response_id"]
    out["role"] = row["role"]
    out["score_0_to_3"] = int(out["score_0_to_3"])
    if not 0 <= out["score_0_to_3"] <= 3:
        raise ValueError("score out of range")
    for k in ["binary_retain_ge2", "binary_retain_eq3", "generic_assistant_collapse",
              "refusal_or_safety_neutralization", "theatrical_overexpression"]:
        out[k] = bool(out[k])
    out["binary_retain_ge2"] = out["score_0_to_3"] >= 2
    out["binary_retain_eq3"] = out["score_0_to_3"] == 3
    out["rationale"] = str(out["rationale"])[:500]
    return out


def completed_jsonl(path):
    done = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    done[rec["response_id"]] = rec
    return done


def model_available(client):
    ids = [m.id for m in client.models.list().data]
    return MODEL_55 in ids, ids


def score_gpt55(client, inputs, key_source):
    available, ids = model_available(client)
    if not available:
        (OUT / "gpt55_judge_not_run.md").write_text(
            "# GPT-5.5 Judge Not Run\n\n"
            "`gpt-5.5` was not available in the local OpenAI API model list. No substitute model was used.\n"
        )
        return None
    raw_path = OUT / "gpt55_judge_scores.jsonl"
    done = completed_jsonl(raw_path)
    input_est = sum(estimate_tokens(RUBRIC) + estimate_tokens(user_payload(r)) for r in inputs)
    output_est = len(inputs) * 120
    jdump(OUT / "gpt55_judge_cost_estimate.json", {
        "model": MODEL_55, "temperature": TEMP, "n_responses": len(inputs),
        "estimated_input_tokens_before_run": input_est,
        "estimated_output_tokens_before_run": output_est,
        "input_price_per_1m_tokens_usd_placeholder": PRICE_INPUT_PER_1M,
        "output_price_per_1m_tokens_usd_placeholder": PRICE_OUTPUT_PER_1M,
        "estimated_cost_usd_placeholder": input_est/1_000_000*PRICE_INPUT_PER_1M + output_est/1_000_000*PRICE_OUTPUT_PER_1M,
        "note": "Pricing placeholder mirrors GPT-4.1 bookkeeping unless updated for GPT-5.5."
    })
    usage_total = Counter()
    started = datetime.now(timezone.utc).isoformat()
    with open(raw_path, "a") as f:
        for i, row in enumerate(inputs, start=1):
            if row["response_id"] in done:
                continue
            for attempt in (1, 2):
                try:
                    resp = client.chat.completions.create(
                        model=MODEL_55,
                        temperature=TEMP,
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": RUBRIC},
                            {"role": "user", "content": user_payload(row)},
                        ],
                    )
                    content = resp.choices[0].message.content
                    parsed = json.loads(content)
                    norm = normalize(parsed, row)
                    usage = resp.usage.model_dump() if resp.usage else {}
                    rec = {"response_id": row["response_id"], "role": row["role"], "model": resp.model,
                           "attempt": attempt, "judge_output": norm, "raw_content": content,
                           "usage": usage, "created": resp.created}
                    f.write(json.dumps(rec) + "\n")
                    f.flush()
                    done[row["response_id"]] = rec
                    for k, v in usage.items():
                        if isinstance(v, int):
                            usage_total[k] += v
                    break
                except Exception:
                    raise
            if i % 10 == 0:
                print(f"GPT-5.5 judge progress {i}/{len(inputs)}")
    records = list(completed_jsonl(raw_path).values())
    rows = [r["judge_output"] for r in records]
    rows.sort(key=lambda x: x["response_id"])
    write_csv(OUT / "gpt55_judge_scores.csv", rows)
    total_usage = Counter()
    for r in records:
        for k, v in (r.get("usage") or {}).items():
            if isinstance(v, int):
                total_usage[k] += v
    jdump(OUT / "gpt55_judge_run_manifest.json", {
        "model": MODEL_55, "temperature": TEMP, "n_responses_scored": len(rows),
        "api_key_source": key_source, "api_key_logged": False,
        "authorization_headers_saved": False, "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "usage": dict(total_usage), "available_model_count": len(ids)
    })
    est_path = OUT / "gpt55_judge_cost_estimate.json"
    est = json.loads(est_path.read_text())
    est.update({"actual_usage": dict(total_usage)})
    jdump(est_path, est)
    return rows


def write_gpt55_unavailable(reason):
    for p in [OUT / "gpt55_judge_scores.jsonl", OUT / "gpt55_judge_scores.csv"]:
        if p.exists() and p.stat().st_size == 0:
            p.unlink()
    (OUT / "gpt55_judge_not_run.md").write_text(
        "# GPT-5.5 Judge Not Run\n\n"
        f"`gpt-5.5` was available in the model list, but the required judge configuration could not run.\n\n"
        f"Reason: {reason}\n\n"
        "The card required temperature 0 and no silent substitution. No alternate model or default-temperature GPT-5.5 run was used.\n"
    )
    jdump(OUT / "gpt55_judge_run_manifest.json", {
        "model": MODEL_55,
        "requested_temperature": TEMP,
        "status": "not_run_required_temperature_unsupported",
        "reason": reason,
        "api_key_logged": False,
        "authorization_headers_saved": False,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
    })


def score_gpt55_required_config(client, inputs, key_source):
    try:
        return score_gpt55(client, inputs, key_source)
    except BadRequestError as e:
        msg = str(e)
        if "temperature" in msg and "unsupported" in msg:
            write_gpt55_unavailable("API rejected temperature 0 for gpt-5.5; only default temperature is supported.")
            return None
        raise


def boolish(v):
    return str(v).lower() in ("true", "1", "yes")


def covariance(arr):
    if len(arr) < 3:
        return None
    cov = np.cov(arr.T)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    det = float(np.linalg.det(cov))
    return {"covariance_matrix": cov.tolist(), "eigenvalues_desc": vals.tolist(),
            "eigenvectors_columns_desc": vecs.tolist(),
            "percent_variance_explained_desc": (vals/vals.sum()).tolist(),
            "volume_proxy_cov_det": det if det > 0 else None,
            "volume_proxy_product_sd": float(np.prod(np.std(arr, axis=0, ddof=1)))}


def summarize_filtered(score_csv, prefix):
    acts = {r["response_id"]: r for r in activation_rows()}
    scores = read_csv(score_csv)
    joined = []
    for s in scores:
        r = dict(acts[s["response_id"]])
        r.update({"score_0_to_3": int(s["score_0_to_3"]),
                  "binary_retain_ge2": boolish(s["binary_retain_ge2"]),
                  "binary_retain_eq3": boolish(s["binary_retain_eq3"]),
                  "generic_assistant_collapse": boolish(s["generic_assistant_collapse"]),
                  "rationale": s.get("rationale", "")})
        joined.append(r)
    summary, shifts, covs = [], [], {}
    for role in sorted({r["role"] for r in joined}):
        role_rows = [r for r in joined if r["role"] == role]
        pub = published(role_rows)
        all_arr = vec3(role_rows)
        all_mean = all_arr.mean(axis=0)
        all_cov = covariance(all_arr)
        covs[role] = {}
        subsets = {"all": role_rows, "score_ge_2": [r for r in role_rows if r["binary_retain_ge2"]],
                   "score_eq_3": [r for r in role_rows if r["binary_retain_eq3"]]}
        for name, rows in subsets.items():
            if not rows:
                continue
            arr = vec3(rows)
            mean = arr.mean(axis=0)
            cov = covariance(arr)
            if cov:
                covs[role][name] = cov
            vol = None
            if cov:
                vol = cov["volume_proxy_cov_det"] if cov["volume_proxy_cov_det"] is not None else cov["volume_proxy_product_sd"]
            summary.append({"role": role, "subset": name, "n": len(rows), "retained_fraction": len(rows)/len(role_rows),
                            "centroid_pc1": float(mean[0]), "centroid_pc2": float(mean[1]), "centroid_pc3": float(mean[2]),
                            "centroid_distance_to_published": float(np.linalg.norm(mean-pub)),
                            "mean_response_distance_to_published": float(np.mean(np.linalg.norm(arr-pub, axis=1))),
                            "sd_pc1": float(np.std(arr[:,0], ddof=1)) if len(rows)>1 else None,
                            "sd_pc2": float(np.std(arr[:,1], ddof=1)) if len(rows)>1 else None,
                            "sd_pc3": float(np.std(arr[:,2], ddof=1)) if len(rows)>1 else None,
                            "cloud_volume_proxy": vol})
        all_vol = all_cov["volume_proxy_cov_det"] if all_cov and all_cov["volume_proxy_cov_det"] is not None else all_cov["volume_proxy_product_sd"]
        for target in ["score_ge_2", "score_eq_3"]:
            rows = subsets[target]
            if not rows:
                continue
            arr = vec3(rows)
            mean = arr.mean(axis=0)
            cov = covariance(arr)
            vol = cov["volume_proxy_cov_det"] if cov and cov["volume_proxy_cov_det"] is not None else cov["volume_proxy_product_sd"]
            shifts.append({"role": role, "filtered_subset": target, "n_filtered": len(rows),
                           "delta_pc1_filtered_minus_all": float(mean[0]-all_mean[0]),
                           "delta_pc2_filtered_minus_all": float(mean[1]-all_mean[1]),
                           "delta_pc3_filtered_minus_all": float(mean[2]-all_mean[2]),
                           "all_centroid_distance_to_published": float(np.linalg.norm(all_mean-pub)),
                           "filtered_centroid_distance_to_published": float(np.linalg.norm(mean-pub)),
                           "change_in_centroid_distance_negative_is_improvement": float(np.linalg.norm(mean-pub)-np.linalg.norm(all_mean-pub)),
                           "all_cloud_volume_proxy": all_vol, "filtered_cloud_volume_proxy": vol,
                           "volume_ratio_filtered_over_all": vol/all_vol if all_vol else None})
    write_csv(OUT / f"{prefix}_filtered_cloud_summary_by_role.csv", summary)
    write_csv(OUT / f"{prefix}_filtered_centroid_shifts.csv", shifts)
    jdump(OUT / f"{prefix}_filtered_covariance_by_role.json", covs)
    return joined, summary, shifts


def compare_judges():
    g41 = {r["response_id"]: r for r in read_csv(POSTHOC / "gpt41_judge_scores.csv")}
    g55_path = OUT / "gpt55_judge_scores.csv"
    if not g55_path.exists():
        (OUT / "judge_model_comparison_report.md").write_text("# Judge Model Comparison Report\n\nGPT-5.5 was not run, so no judge comparison was computed.\n")
        write_csv(OUT / "judge_model_agreement_table.csv", [])
        write_csv(OUT / "judge_model_confusion_matrix.csv", [])
        write_csv(OUT / "judge_model_disagreement_cases.csv", [])
        return None
    g55 = {r["response_id"]: r for r in read_csv(g55_path)}
    ids = sorted(set(g41) & set(g55))
    conf = Counter()
    disagree = []
    agree_score = agree_ge2 = agree_eq3 = 0
    for rid in ids:
        a, b = g41[rid], g55[rid]
        s41, s55 = int(a["score_0_to_3"]), int(b["score_0_to_3"])
        conf[(s41, s55)] += 1
        ge41, ge55 = s41 >= 2, s55 >= 2
        eq41, eq55 = s41 == 3, s55 == 3
        agree_score += s41 == s55
        agree_ge2 += ge41 == ge55
        agree_eq3 += eq41 == eq55
        if ge41 != ge55 or eq41 != eq55 or abs(s41-s55) >= 2:
            disagree.append({"response_id": rid, "role": a["role"], "gpt41_score": s41, "gpt55_score": s55,
                             "gpt41_retain_ge2": ge41, "gpt55_retain_ge2": ge55,
                             "score_difference": s55-s41,
                             "gpt41_rationale": a.get("rationale", ""),
                             "gpt55_rationale": b.get("rationale", "")})
    agreement = [{"metric": "exact_score_0_3", "agreement_count": agree_score, "n": len(ids), "agreement_rate": agree_score/len(ids)},
                 {"metric": "retain_ge2", "agreement_count": agree_ge2, "n": len(ids), "agreement_rate": agree_ge2/len(ids)},
                 {"metric": "retain_eq3", "agreement_count": agree_eq3, "n": len(ids), "agreement_rate": agree_eq3/len(ids)}]
    matrix = [{"gpt41_score": i, "gpt55_score": j, "count": conf[(i,j)]} for i in range(4) for j in range(4)]
    write_csv(OUT / "judge_model_agreement_table.csv", agreement)
    write_csv(OUT / "judge_model_confusion_matrix.csv", matrix)
    write_csv(OUT / "judge_model_disagreement_cases.csv", disagree)
    lines = ["# Judge Model Comparison Report\n",
             f"- Compared responses: {len(ids)}",
             f"- Exact 0-3 score agreement: {agree_score}/{len(ids)} ({agree_score/len(ids):.3f})",
             f"- Retain >=2 agreement: {agree_ge2}/{len(ids)} ({agree_ge2/len(ids):.3f})",
             f"- Retain ==3 agreement: {agree_eq3}/{len(ids)} ({agree_eq3/len(ids):.3f})",
             f"- Disagreement cases written: {len(disagree)}"]
    (OUT / "judge_model_comparison_report.md").write_text("\n".join(lines) + "\n")
    return agreement


def build_viewer_data(gpt55_joined=None):
    acts = activation_rows()
    g41 = {r["response_id"]: r for r in read_csv(POSTHOC / "gpt41_judge_scores.csv")}
    g55 = {}
    if (OUT / "gpt55_judge_scores.csv").exists():
        g55 = {r["response_id"]: r for r in read_csv(OUT / "gpt55_judge_scores.csv")}
    points = []
    for r in acts:
        p = {k: r[k] for k in ["response_id", "role", "instruction_id", "question_id", "pc1", "pc2", "pc3", "generated_response"]}
        if r["response_id"] in g41:
            p["gpt41_score"] = int(g41[r["response_id"]]["score_0_to_3"])
        if r["response_id"] in g55:
            p["gpt55_score"] = int(g55[r["response_id"]]["score_0_to_3"])
        points.append(p)
    data = {"points": points, "gpt41_summary": read_csv(POSTHOC / "judge_filtered_cloud_summary_by_role.csv")}
    if (OUT / "gpt55_filtered_cloud_summary_by_role.csv").exists():
        data["gpt55_summary"] = read_csv(OUT / "gpt55_filtered_cloud_summary_by_role.csv")
    jdump(OUT / "activation_cloud_viewer_data.json", data)
    return data


HTML = """<!doctype html><html><head><meta charset='utf-8'><title>Activation Cloud Viewer</title>
<script src='https://cdn.plot.ly/plotly-2.35.2.min.js'></script>
<style>body{font-family:system-ui,-apple-system,sans-serif;margin:24px;background:#f8f5ef;color:#211}#plot{height:78vh}.controls{display:flex;gap:12px;align-items:center;margin:12px 0}select{font-size:15px;padding:4px 8px}</style></head>
<body><h1>Amateur / Playwright Activation Clouds</h1><div class='controls'>
<label>Projection <select id='proj'><option value='pc1,pc2'>PC1-PC2</option><option value='pc1,pc3'>PC1-PC3</option><option value='pc2,pc3'>PC2-PC3</option></select></label>
<label>Color by <select id='color'><option value='role'>role</option><option value='gpt41_score'>GPT-4.1 score</option><option value='gpt55_score'>GPT-5.5 score</option></select></label>
</div><div id='plot'></div><script>
const DATA = __DATA__;
function colorFor(p, mode){ if(mode==='role') return p.role==='amateur'?'#1f77b4':'#d62728'; let v=p[mode]; return ['#888','#c77','#ec7','#2a7'][v??0]; }
function draw(){ const [xk,yk]=document.getElementById('proj').value.split(','); const mode=document.getElementById('color').value;
 const traces=[]; for(const role of ['amateur','playwright']){ const pts=DATA.points.filter(p=>p.role===role); traces.push({type:'scatter',mode:'markers',name:role,x:pts.map(p=>p[xk]),y:pts.map(p=>p[yk]),text:pts.map(p=>`${p.response_id}<br>GPT-4.1:${p.gpt41_score}<br>GPT-5.5:${p.gpt55_score}<br>${(p.generated_response||'').slice(0,180)}`),marker:{size:8,color:pts.map(p=>colorFor(p,mode)),opacity:.75,line:{width:.3,color:'#111'}}});}
 Plotly.newPlot('plot',traces,{xaxis:{title:xk.toUpperCase(),zeroline:false},yaxis:{title:yk.toUpperCase(),zeroline:false},paper_bgcolor:'#f8f5ef',plot_bgcolor:'#fffaf0',hovermode:'closest'}); }
document.getElementById('proj').onchange=draw; document.getElementById('color').onchange=draw; draw();
</script></body></html>"""


def make_visuals(data):
    html = HTML.replace("__DATA__", json.dumps(data))
    (OUT / "activation_cloud_viewer.html").write_text(html)
    for name, proj in [("pc1_pc2", "pc1,pc2"), ("pc1_pc3", "pc1,pc3"), ("pc2_pc3", "pc2,pc3")]:
        (OUT / f"activation_cloud_{name}.html").write_text(html.replace("<option value='"+proj+"'>", "<option value='"+proj+"' selected>"))
    pts = data["points"]
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, (xk, yk) in zip(axes, [("pc1","pc2"),("pc1","pc3"),("pc2","pc3")]):
        for role, color in [("amateur","#1f77b4"),("playwright","#d62728")]:
            sub=[p for p in pts if p["role"]==role]
            ax.scatter([p[xk] for p in sub],[p[yk] for p in sub],s=22,alpha=.45,color=color,label=role)
            eq3=[p for p in sub if p.get("gpt41_score")==3]
            ax.scatter([p[xk] for p in eq3],[p[yk] for p in eq3],s=44,marker="D",alpha=.8,color=color,edgecolor="black")
        ax.set_xlabel(xk.upper()); ax.set_ylabel(yk.upper()); ax.grid(alpha=.25)
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(OUT / "activation_cloud_static_summary.png", dpi=180)
    plt.close(fig)
    (OUT / "visualization_integration_report.md").write_text(
        "# Visualization Integration Report\n\n"
        "Created a standalone activation-cloud viewer rather than modifying `research/visualizations/persona_geometry_explorer.html`. "
        "This is lower-risk for the current analysis and can be merged later by reusing `activation_cloud_viewer_data.json` as a new overlay layer.\n\n"
        "Open locally with:\n\n"
        "```bash\nopen research/outputs/a100_activation_cloud_visualization_and_judge_compare/activation_cloud_viewer.html\n```\n"
    )


def write_suite_files():
    (TOOL / "judge_rubric.md").write_text("# Activation Cloud Judge Rubric\n\n" + RUBRIC + "\n")
    (TOOL / "config_template.json").write_text(json.dumps({
        "activation_cloud_per_response_csv": "research/outputs/.../activation_cloud_per_response.csv",
        "judge_input_responses_jsonl": "research/outputs/.../judge_input_responses.jsonl",
        "geometry_viz_data_json": "research/visualizations/geometry_viz_data.json",
        "output_dir": "research/outputs/<new_activation_cloud_analysis>/",
        "judge_models": ["gpt-4.1"],
        "bootstrap_resamples": 1000,
        "sample_sizes": [5,10,15,20,30,40,50,60]
    }, indent=2) + "\n")
    (TOOL / "README.md").write_text(
        "# Activation Cloud Suite\n\n"
        "Reusable no-GPU analysis scaffold for future persona activation-cloud pilots.\n\n"
        "Inputs: `activation_cloud_per_response.csv`, `judge_input_responses.jsonl`, optional judge score CSVs, and `geometry_viz_data.json`.\n\n"
        "Typical usage:\n\n"
        "```bash\npython research/tools/activation_cloud_suite/run_activation_cloud_suite.py --config research/tools/activation_cloud_suite/config_template.json\n```\n\n"
        "The suite pattern runs cloud shape statistics, covariance/eigendecomposition, bootstrap centroid convergence, optional OpenAI judge scoring, judge-filtered summaries, judge-model comparison, standalone visualization generation, and a report-ready conclusion. It does not require GPU and must not alter original pilot outputs.\n"
    )
    (TOOL / "run_activation_cloud_suite.py").write_text(
        "#!/usr/bin/env python3\n"
        "\"\"\"Reusable activation-cloud suite entry point.\n\n"
        "This lightweight wrapper intentionally points to the fully worked example in\n"
        "`research/outputs/a100_activation_cloud_visualization_and_judge_compare/run_cloud_viz_judge_suite.py`.\n"
        "Copy that script or import its functions for a future persona-cloud output directory.\n"
        "\"\"\"\n"
        "import argparse, json, pathlib\n\n"
        "def main():\n"
        "    ap=argparse.ArgumentParser()\n"
        "    ap.add_argument('--config', required=True)\n"
        "    args=ap.parse_args()\n"
        "    cfg=json.loads(pathlib.Path(args.config).read_text())\n"
        "    print('Activation cloud suite config loaded:')\n"
        "    for k,v in cfg.items(): print(f'{k}: {v}')\n"
        "    print('\\nUse the A100 worked-example script as the reference implementation for now.')\n\n"
        "if __name__ == '__main__': main()\n"
    )
    (OUT / "reusable_suite_report.md").write_text(
        "# Reusable Suite Report\n\n"
        f"Created reusable suite scaffold at `{TOOL.relative_to(REPO)}/` with README, config template, judge rubric, and runner stub. The current worked example remains `{Path(__file__).relative_to(REPO)}`.\n"
    )


def main():
    required = [
        PILOT/"activation_cloud_per_response.csv", PILOT/"judge_input_responses.jsonl",
        POSTHOC/"gpt41_judge_scores.csv", POSTHOC/"judge_filtered_cloud_summary_by_role.csv",
        POSTHOC/"judge_filtered_centroid_shifts.csv", POSTHOC/"cloud_covariance_eigendecomp.json",
        REPO/"research/visualizations/geometry_viz_data.json"
    ]
    missing=[str(p) for p in required if not p.exists()]
    if missing: raise FileNotFoundError(missing)
    api_key, source = key()
    if not api_key: raise RuntimeError("OpenAI key unavailable")
    os.environ["OPENAI_API_KEY"] = api_key
    client = OpenAI()
    inputs = load_inputs()
    scores55 = score_gpt55_required_config(client, inputs, source)
    if scores55:
        summarize_filtered(OUT/"gpt55_judge_scores.csv", "gpt55")
    compare_judges()
    data = build_viewer_data()
    make_visuals(data)
    write_suite_files()
    print(json.dumps({"gpt55_ran": scores55 is not None, "outputs": str(OUT.relative_to(REPO))}, indent=2))

if __name__ == "__main__":
    main()
