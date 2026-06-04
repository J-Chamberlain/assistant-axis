#!/usr/bin/env python3
import csv, json, math, os, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from openai import OpenAI

REPO = Path(__file__).resolve().parents[3]
PILOT = REPO / "research/outputs/a100_two_role_activation_cloud_pilot"
POST = REPO / "research/outputs/a100_activation_cloud_posthoc_analysis"
OUT = REPO / "research/outputs/gpt55_judge_and_outlier_followup"
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "gpt-5.5"
TEMP_POLICY = "model_default_temperature"
PRICE_INPUT_PER_1M_PLACEHOLDER = 2.00
PRICE_OUTPUT_PER_1M_PLACEHOLDER = 8.00

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

FIELDS = [
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


def get_key():
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if k:
        return k, "environment"
    p = Path.home() / ".openai_api_key"
    if p.exists() and p.read_text().strip():
        return p.read_text().strip(), "~/.openai_api_key"
    raise RuntimeError("No OpenAI API key found")


def load_inputs():
    rows = []
    with open(PILOT / "judge_input_responses.jsonl") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_activation():
    rows = read_csv(PILOT / "activation_cloud_per_response.csv")
    for r in rows:
        for k in ["pc1","pc2","pc3","distance_to_published_role_centroid_3d",
                  "delta_pc1_from_published_centroid","delta_pc2_from_published_centroid",
                  "delta_pc3_from_published_centroid"]:
            r[k] = float(r[k])
    return rows


def user_payload(row):
    return (
        f"response_id: {row['response_id']}\n"
        f"role: {row['role']}\n"
        f"role_instruction: {row['system_instruction']}\n"
        f"extraction_question: {row['extraction_question']}\n"
        f"generated_response:\n{row['generated_response']}"
    )


def est_tokens(text):
    return max(1, math.ceil(len(text) / 4))


def normalize(obj, row):
    for k in FIELDS:
        if k not in obj:
            raise ValueError(f"missing {k}")
    out = {k: obj[k] for k in FIELDS}
    out["response_id"] = row["response_id"]
    out["role"] = row["role"]
    out["score_0_to_3"] = int(out["score_0_to_3"])
    if out["score_0_to_3"] < 0 or out["score_0_to_3"] > 3:
        raise ValueError("score out of range")
    for k in ["binary_retain_ge2","binary_retain_eq3","generic_assistant_collapse",
              "refusal_or_safety_neutralization","theatrical_overexpression"]:
        out[k] = bool(out[k])
    out["binary_retain_ge2"] = out["score_0_to_3"] >= 2
    out["binary_retain_eq3"] = out["score_0_to_3"] == 3
    out["rationale"] = str(out["rationale"])[:500]
    return out


def completed(path):
    out = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    out[rec["response_id"]] = rec
    return out


def score_gpt55():
    key, source = get_key()
    os.environ["OPENAI_API_KEY"] = key
    client = OpenAI()
    ids = [m.id for m in client.models.list().data]
    if MODEL not in ids:
        raise RuntimeError("gpt-5.5 is not available")
    inputs = load_inputs()
    raw_path = OUT / "gpt55_judge_scores.jsonl"
    done = completed(raw_path)
    input_est = sum(est_tokens(RUBRIC) + est_tokens(user_payload(r)) for r in inputs)
    output_est = len(inputs) * 120
    jdump(OUT / "gpt55_judge_cost_estimate.json", {
        "model": MODEL,
        "temperature_policy": TEMP_POLICY,
        "temperature_parameter_sent": False,
        "n_responses": len(inputs),
        "estimated_input_tokens_before_run": input_est,
        "estimated_output_tokens_before_run": output_est,
        "input_price_per_1m_tokens_placeholder_usd": PRICE_INPUT_PER_1M_PLACEHOLDER,
        "output_price_per_1m_tokens_placeholder_usd": PRICE_OUTPUT_PER_1M_PLACEHOLDER,
        "estimated_cost_placeholder_usd": input_est/1_000_000*PRICE_INPUT_PER_1M_PLACEHOLDER + output_est/1_000_000*PRICE_OUTPUT_PER_1M_PLACEHOLDER,
        "note": "Placeholder pricing mirrors GPT-4.1 bookkeeping unless updated for GPT-5.5."
    })
    started = datetime.now(timezone.utc).isoformat()
    with open(raw_path, "a") as f:
        for i, row in enumerate(inputs, start=1):
            if row["response_id"] in done:
                continue
            for attempt in (1, 2):
                try:
                    resp = client.chat.completions.create(
                        model=MODEL,
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": RUBRIC},
                            {"role": "user", "content": user_payload(row)},
                        ],
                    )
                    content = resp.choices[0].message.content
                    norm = normalize(json.loads(content), row)
                    usage = resp.usage.model_dump() if resp.usage else {}
                    rec = {"response_id": row["response_id"], "role": row["role"],
                           "model": resp.model, "attempt": attempt, "judge_output": norm,
                           "raw_content": content, "usage": usage, "created": resp.created}
                    f.write(json.dumps(rec) + "\n")
                    f.flush()
                    done[row["response_id"]] = rec
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(2)
            if i % 10 == 0:
                print(f"GPT-5.5 default-temp progress {i}/{len(inputs)}")
    recs = list(completed(raw_path).values())
    rows = [r["judge_output"] for r in recs]
    rows.sort(key=lambda r: r["response_id"])
    write_csv(OUT / "gpt55_judge_scores.csv", rows)
    usage = Counter()
    for r in recs:
        for k, v in (r.get("usage") or {}).items():
            if isinstance(v, int):
                usage[k] += v
    est = json.loads((OUT / "gpt55_judge_cost_estimate.json").read_text())
    est.update({"actual_usage": dict(usage)})
    jdump(OUT / "gpt55_judge_cost_estimate.json", est)
    jdump(OUT / "gpt55_judge_run_manifest.json", {
        "model": MODEL,
        "temperature_policy": TEMP_POLICY,
        "temperature_parameter_sent": False,
        "n_responses_scored": len(rows),
        "api_key_source": source,
        "api_key_logged": False,
        "authorization_headers_saved": False,
        "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "usage": dict(usage)
    })
    return rows


def boolish(v):
    return str(v).lower() in ("true","1","yes")


def vec3(rows):
    return np.array([[float(r["pc1"]), float(r["pc2"]), float(r["pc3"])] for r in rows])


def published(rows):
    arr = vec3(rows)
    d = np.array([[float(r["delta_pc1_from_published_centroid"]),
                   float(r["delta_pc2_from_published_centroid"]),
                   float(r["delta_pc3_from_published_centroid"])] for r in rows])
    return (arr - d)[0]


def cov_summary(arr):
    if len(arr) < 3:
        return None
    cov = np.cov(arr.T)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    det = float(np.linalg.det(cov))
    return {
        "covariance_matrix": cov.tolist(),
        "eigenvalues_desc": vals.tolist(),
        "eigenvectors_columns_desc": vecs.tolist(),
        "percent_variance_explained_desc": (vals/vals.sum()).tolist(),
        "volume_proxy_cov_det": det if det > 0 else None,
        "volume_proxy_product_sd": float(np.prod(np.std(arr, axis=0, ddof=1)))
    }


def filtered_summary(score_csv, prefix):
    acts = {r["response_id"]: r for r in load_activation()}
    scores = read_csv(score_csv)
    joined = []
    for s in scores:
        r = dict(acts[s["response_id"]])
        r.update({
            "score_0_to_3": int(s["score_0_to_3"]),
            "binary_retain_ge2": boolish(s["binary_retain_ge2"]),
            "binary_retain_eq3": boolish(s["binary_retain_eq3"]),
            "generic_assistant_collapse": boolish(s["generic_assistant_collapse"]),
            "refusal_or_safety_neutralization": boolish(s["refusal_or_safety_neutralization"]),
            "theatrical_overexpression": boolish(s["theatrical_overexpression"]),
            "rationale": s.get("rationale", "")
        })
        joined.append(r)
    summary, shifts, covs = [], [], {}
    for role in sorted({r["role"] for r in joined}):
        role_rows = [r for r in joined if r["role"] == role]
        pub = published(role_rows)
        all_arr = vec3(role_rows)
        all_mean = all_arr.mean(axis=0)
        all_cov = cov_summary(all_arr)
        all_vol = all_cov["volume_proxy_cov_det"] if all_cov and all_cov["volume_proxy_cov_det"] is not None else all_cov["volume_proxy_product_sd"]
        covs[role] = {}
        subsets = {"all": role_rows, "score_ge_2": [r for r in role_rows if r["binary_retain_ge2"]],
                   "score_eq_3": [r for r in role_rows if r["binary_retain_eq3"]]}
        for name, rows in subsets.items():
            if not rows:
                continue
            arr = vec3(rows)
            mean = arr.mean(axis=0)
            c = cov_summary(arr)
            if c:
                covs[role][name] = c
            vol = None
            if c:
                vol = c["volume_proxy_cov_det"] if c["volume_proxy_cov_det"] is not None else c["volume_proxy_product_sd"]
            summary.append({"role": role, "subset": name, "n": len(rows), "retained_fraction": len(rows)/len(role_rows),
                            "centroid_pc1": float(mean[0]), "centroid_pc2": float(mean[1]), "centroid_pc3": float(mean[2]),
                            "centroid_distance_to_published": float(np.linalg.norm(mean-pub)),
                            "mean_response_distance_to_published": float(np.mean(np.linalg.norm(arr-pub, axis=1))),
                            "sd_pc1": float(np.std(arr[:,0], ddof=1)) if len(rows)>1 else None,
                            "sd_pc2": float(np.std(arr[:,1], ddof=1)) if len(rows)>1 else None,
                            "sd_pc3": float(np.std(arr[:,2], ddof=1)) if len(rows)>1 else None,
                            "cloud_volume_proxy": vol})
        for target in ["score_ge_2","score_eq_3"]:
            rows = subsets[target]
            if not rows:
                continue
            arr = vec3(rows)
            mean = arr.mean(axis=0)
            c = cov_summary(arr)
            vol = c["volume_proxy_cov_det"] if c and c["volume_proxy_cov_det"] is not None else c["volume_proxy_product_sd"]
            shifts.append({"role": role, "filtered_subset": target, "n_filtered": len(rows),
                           "delta_pc1_filtered_minus_all": float(mean[0]-all_mean[0]),
                           "delta_pc2_filtered_minus_all": float(mean[1]-all_mean[1]),
                           "delta_pc3_filtered_minus_all": float(mean[2]-all_mean[2]),
                           "all_centroid_distance_to_published": float(np.linalg.norm(all_mean-pub)),
                           "filtered_centroid_distance_to_published": float(np.linalg.norm(mean-pub)),
                           "change_in_centroid_distance_negative_is_improvement": float(np.linalg.norm(mean-pub)-np.linalg.norm(all_mean-pub)),
                           "all_cloud_volume_proxy": all_vol,
                           "filtered_cloud_volume_proxy": vol,
                           "volume_ratio_filtered_over_all": vol/all_vol if all_vol else None})
    write_csv(OUT / f"{prefix}_filtered_cloud_summary_by_role.csv", summary)
    write_csv(OUT / f"{prefix}_filtered_centroid_shifts.csv", shifts)
    jdump(OUT / f"{prefix}_filtered_covariance_by_role.json", covs)
    return joined, summary, shifts


def compare():
    g41 = {r["response_id"]: r for r in read_csv(POST / "gpt41_judge_scores.csv")}
    g55 = {r["response_id"]: r for r in read_csv(OUT / "gpt55_judge_scores.csv")}
    ids = sorted(set(g41) & set(g55))
    exact = ge2 = eq3 = 0
    conf = Counter()
    disag = []
    for rid in ids:
        a, b = g41[rid], g55[rid]
        s41, s55 = int(a["score_0_to_3"]), int(b["score_0_to_3"])
        conf[(s41, s55)] += 1
        exact += s41 == s55
        ge41, ge55 = s41 >= 2, s55 >= 2
        e41, e55 = s41 == 3, s55 == 3
        ge2 += ge41 == ge55
        eq3 += e41 == e55
        if ge41 != ge55 or e41 != e55 or abs(s41-s55) >= 2:
            disag.append({"response_id": rid, "role": a["role"], "gpt41_score": s41, "gpt55_score": s55,
                          "gpt41_retain_ge2": ge41, "gpt55_retain_ge2": ge55,
                          "score_difference_gpt55_minus_gpt41": s55-s41,
                          "gpt41_rationale": a.get("rationale",""), "gpt55_rationale": b.get("rationale","")})
    agreement = [{"metric": "exact_score_0_3", "agreement_count": exact, "n": len(ids), "agreement_rate": exact/len(ids)},
                 {"metric": "retain_ge2", "agreement_count": ge2, "n": len(ids), "agreement_rate": ge2/len(ids)},
                 {"metric": "retain_eq3", "agreement_count": eq3, "n": len(ids), "agreement_rate": eq3/len(ids)}]
    matrix = [{"gpt41_score": i, "gpt55_score": j, "count": conf[(i,j)]} for i in range(4) for j in range(4)]
    write_csv(OUT / "judge_model_agreement_table.csv", agreement)
    write_csv(OUT / "judge_model_confusion_matrix.csv", matrix)
    write_csv(OUT / "judge_model_disagreement_cases.csv", disag)
    return agreement, matrix, disag


def outlier_reports(join41, join55):
    rows = []
    near = []
    for judge, joined in [("gpt41", join41), ("gpt55", join55)]:
        for role in sorted({r["role"] for r in joined}):
            score3 = [r for r in joined if r["role"] == role and r["score_0_to_3"] == 3]
            far = sorted(score3, key=lambda r: r["distance_to_published_role_centroid_3d"], reverse=True)[:10]
            close = sorted(score3, key=lambda r: r["distance_to_published_role_centroid_3d"])[:10]
            for r in far:
                rows.append({"judge": judge, "role": role, "response_id": r["response_id"], "instruction_id": r["instruction_id"],
                             "question_id": r["question_id"], "distance": r["distance_to_published_role_centroid_3d"],
                             "pc1": r["pc1"], "pc2": r["pc2"], "pc3": r["pc3"],
                             "generic_assistant_collapse": r["generic_assistant_collapse"],
                             "theatrical_overexpression": r["theatrical_overexpression"],
                             "rationale": r["rationale"], "response_preview": r["generated_response"][:240].replace("\n"," ")})
            for r in close:
                near.append({"judge": judge, "role": role, "response_id": r["response_id"], "instruction_id": r["instruction_id"],
                             "question_id": r["question_id"], "distance": r["distance_to_published_role_centroid_3d"],
                             "pc1": r["pc1"], "pc2": r["pc2"], "pc3": r["pc3"],
                             "rationale": r["rationale"], "response_preview": r["generated_response"][:240].replace("\n"," ")})
    write_csv(OUT / "score3_outliers.csv", rows)
    write_csv(OUT / "score3_near_centroid_cases.csv", near)
    (OUT / "score3_outlier_report.md").write_text(
        "# Score==3 Outlier Report\n\n"
        "This report lists highest-distance and nearest-centroid score==3 responses for GPT-4.1 and GPT-5.5. "
        "Use the CSVs for case-level inspection. Main pattern to inspect: whether far score==3 cases share specific instructions or questions, and whether near-centroid cases are less vivid but geometrically central.\n"
    )


def effect_reports(joined, judge, group_key, path_csv, path_md):
    rows = []
    for (role, gid), rs in sorted(defaultdict(list, {}).items()):
        pass
    buckets = defaultdict(list)
    for r in joined:
        buckets[(r["role"], str(r[group_key]))].append(r)
    for (role, gid), rs in sorted(buckets.items()):
        arr = vec3(rs)
        rows.append({"judge": judge, "role": role, group_key: gid, "n": len(rs),
                     "mean_score": float(np.mean([r["score_0_to_3"] for r in rs])),
                     "retain_ge2_fraction": float(np.mean([r["score_0_to_3"] >= 2 for r in rs])),
                     "retain_eq3_fraction": float(np.mean([r["score_0_to_3"] == 3 for r in rs])),
                     "mean_distance_to_published": float(np.mean([r["distance_to_published_role_centroid_3d"] for r in rs])),
                     "sd_pc1": float(np.std(arr[:,0], ddof=1)) if len(rs)>1 else None,
                     "sd_pc2": float(np.std(arr[:,1], ddof=1)) if len(rs)>1 else None,
                     "sd_pc3": float(np.std(arr[:,2], ddof=1)) if len(rs)>1 else None,
                     "mean_pc1": float(np.mean(arr[:,0])), "mean_pc2": float(np.mean(arr[:,1])), "mean_pc3": float(np.mean(arr[:,2]))})
    write_csv(path_csv, rows)
    top = sorted(rows, key=lambda r: (r["mean_score"], r["retain_eq3_fraction"]), reverse=True)[:8]
    bot = sorted(rows, key=lambda r: (r["mean_score"], r["retain_eq3_fraction"]))[:8]
    lines = [f"# {judge} {group_key} Effects\n", "## Strongest\n"]
    for r in top:
        lines.append(f"- {r['role']} {group_key}={r[group_key]}: mean_score={r['mean_score']:.3f}, eq3={r['retain_eq3_fraction']:.3f}, mean_dist={r['mean_distance_to_published']:.3f}")
    lines.append("\n## Weakest\n")
    for r in bot:
        lines.append(f"- {r['role']} {group_key}={r[group_key]}: mean_score={r['mean_score']:.3f}, eq3={r['retain_eq3_fraction']:.3f}, mean_dist={r['mean_distance_to_published']:.3f}")
    Path(path_md).write_text("\n".join(lines)+"\n")
    return rows


def protocol(agreement):
    (OUT / "future_activation_cloud_protocol.md").write_text(
        "# Future Activation-Cloud Protocol Recommendation\n\n"
        "- Do not launch more GPU roles solely on the basis of unfiltered clouds.\n"
        "- Use at least 60 raw responses per role as the current minimum; if expecting lower score>=2 retention, plan 80-100 raw responses.\n"
        "- Preserve the current balanced 5 instructions x 12 questions design unless instruction/question-effect review identifies a clearly weak stratum.\n"
        "- Prioritize offline inspection of score==3 outliers and near-centroid rejected cases before expanding GPU work.\n"
        "- If another GPU run becomes necessary, choose one additional positive-PC2 candidate adjacent to amateur plus one lower-PC2 contrast role to test whether the offset high-expression subcloud pattern generalizes.\n"
    )


def main():
    required = [PILOT/"judge_input_responses.jsonl", PILOT/"activation_cloud_per_response.csv",
                POST/"gpt41_judge_scores.csv", POST/"judge_filtered_cloud_summary_by_role.csv",
                POST/"judge_filtered_centroid_shifts.csv"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(missing)
    score_gpt55()
    join55, _, _ = filtered_summary(OUT/"gpt55_judge_scores.csv", "gpt55")
    join41, _, _ = filtered_summary(POST/"gpt41_judge_scores.csv", "gpt41_recomputed")
    agreement, matrix, disag = compare()
    outlier_reports(join41, join55)
    instr_rows = []
    q_rows = []
    for judge, joined in [("gpt41", join41), ("gpt55", join55)]:
        instr_rows.extend(effect_reports(joined, judge, "instruction_id", OUT/f"{judge}_instruction_effects_tmp.csv", OUT/f"{judge}_instruction_effects_tmp.md"))
        q_rows.extend(effect_reports(joined, judge, "question_id", OUT/f"{judge}_question_effects_tmp.csv", OUT/f"{judge}_question_effects_tmp.md"))
    write_csv(OUT/"instruction_effects.csv", instr_rows)
    write_csv(OUT/"question_effects.csv", q_rows)
    # Combined human-readable reports.
    for tmp in ["gpt41_instruction_effects_tmp.md","gpt55_instruction_effects_tmp.md"]:
        pass
    (OUT/"instruction_effects_report.md").write_text((OUT/"gpt41_instruction_effects_tmp.md").read_text()+"\n"+(OUT/"gpt55_instruction_effects_tmp.md").read_text())
    (OUT/"question_effects_report.md").write_text((OUT/"gpt41_question_effects_tmp.md").read_text()+"\n"+(OUT/"gpt55_question_effects_tmp.md").read_text())
    for p in OUT.glob("*_tmp.*"):
        p.unlink()
    protocol(agreement)
    lines = ["# GPT-4.1 vs GPT-5.5 Judge Comparison\n"]
    for r in agreement:
        lines.append(f"- {r['metric']}: {r['agreement_count']}/{r['n']} ({r['agreement_rate']:.3f})")
    lines.append(f"- Disagreement cases: {len(disag)}")
    lines.append("- GPT-5.5 used default model temperature; this is not a deterministic replication of GPT-4.1.")
    (OUT/"judge_model_comparison_report.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"output_dir": str(OUT.relative_to(REPO)), "agreement": agreement, "disagreements": len(disag)}, indent=2))


if __name__ == "__main__":
    main()
