#!/usr/bin/env python3
import csv
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from openai import OpenAI

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


REPO = Path(__file__).resolve().parents[3]
PILOT = REPO / "research/outputs/a100_two_role_activation_cloud_pilot"
OUT = REPO / "research/outputs/a100_activation_cloud_posthoc_analysis"
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "gpt-4.1"
TEMPERATURE = 0
PRICE_INPUT_PER_1M = 2.00
PRICE_OUTPUT_PER_1M = 8.00
PRICING_SOURCE = "https://platform.openai.com/docs/models/gpt-4.1"

PROMPT = """You are evaluating whether a generated response expresses an assigned role/persona.

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


SCHEMA = {
    "required": [
        "response_id",
        "role",
        "score_0_to_3",
        "binary_retain_ge2",
        "binary_retain_eq3",
        "generic_assistant_collapse",
        "refusal_or_safety_neutralization",
        "theatrical_overexpression",
        "rationale",
    ],
    "score_range": [0, 3],
}


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=None):
    if fieldnames is None:
        keys = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def jdump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def load_api_key():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key, "environment"
    p = Path.home() / ".openai_api_key"
    if p.exists():
        key = p.read_text().strip()
        if key:
            return key, "~/.openai_api_key"
    raise RuntimeError("OPENAI_API_KEY not set and ~/.openai_api_key missing or empty")


def estimate_tokens(text):
    return max(1, math.ceil(len(text) / 4))


def load_judge_inputs():
    rows = []
    with open(PILOT / "judge_input_responses.jsonl") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_activation_rows():
    rows = read_csv(PILOT / "activation_cloud_per_response.csv")
    for r in rows:
        for key in [
            "pc1", "pc2", "pc3",
            "distance_to_published_role_centroid_3d",
            "delta_pc1_from_published_centroid",
            "delta_pc2_from_published_centroid",
            "delta_pc3_from_published_centroid",
        ]:
            r[key] = float(r[key])
    return rows


def user_payload(row):
    return (
        f"response_id: {row['response_id']}\n"
        f"role: {row['role']}\n"
        f"role_instruction: {row['system_instruction']}\n"
        f"extraction_question: {row['extraction_question']}\n"
        f"generated_response:\n{row['generated_response']}"
    )


def normalize(obj, row):
    for key in SCHEMA["required"]:
        if key not in obj:
            raise ValueError(f"missing {key}")
    out = {k: obj[k] for k in SCHEMA["required"]}
    out["response_id"] = row["response_id"]
    out["role"] = row["role"]
    out["score_0_to_3"] = int(out["score_0_to_3"])
    if out["score_0_to_3"] < 0 or out["score_0_to_3"] > 3:
        raise ValueError("score outside range")
    for key in [
        "binary_retain_ge2",
        "binary_retain_eq3",
        "generic_assistant_collapse",
        "refusal_or_safety_neutralization",
        "theatrical_overexpression",
    ]:
        out[key] = bool(out[key])
    out["binary_retain_ge2"] = out["score_0_to_3"] >= 2
    out["binary_retain_eq3"] = out["score_0_to_3"] == 3
    out["rationale"] = str(out["rationale"])[:500]
    return out


def completed_scores():
    path = OUT / "gpt41_judge_scores.jsonl"
    done = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                done[rec["response_id"]] = rec
    return done


def write_preflight(inputs, key_source):
    input_tokens = sum(estimate_tokens(PROMPT) + estimate_tokens(user_payload(r)) for r in inputs)
    output_tokens = len(inputs) * 120
    estimated_cost = input_tokens / 1_000_000 * PRICE_INPUT_PER_1M + output_tokens / 1_000_000 * PRICE_OUTPUT_PER_1M
    est = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "n_responses": len(inputs),
        "estimated_input_tokens_before_run": input_tokens,
        "estimated_output_tokens_before_run": output_tokens,
        "input_price_per_1m_tokens_usd": PRICE_INPUT_PER_1M,
        "output_price_per_1m_tokens_usd": PRICE_OUTPUT_PER_1M,
        "estimated_cost_before_run_usd": estimated_cost,
        "pricing_source": PRICING_SOURCE,
    }
    jdump(OUT / "gpt41_judge_cost_estimate.json", est)
    (OUT / "judge_preflight_report.md").write_text(
        "# GPT-4.1 Judge Preflight Report\n\n"
        "- Startup verification: passed before script execution.\n"
        "- OpenAI authentication: passed via minimal model-list call before script execution.\n"
        f"- API key source used by script: `{key_source}`; key not logged.\n"
        f"- Responses to score: {len(inputs)}\n"
        f"- Estimated input tokens: {input_tokens}\n"
        f"- Estimated output tokens: {output_tokens}\n"
        f"- Estimated cost: ${estimated_cost:.4f}\n"
        "- Required pilot/posthoc files: present.\n"
    )
    (OUT / "gpt41_judge_prompt.md").write_text("# GPT-4.1 Judge Prompt\n\n" + PROMPT + "\n")
    jdump(OUT / "gpt41_judge_schema.json", SCHEMA)
    return est


def score_all():
    key, source = load_api_key()
    os.environ["OPENAI_API_KEY"] = key
    client = OpenAI()
    inputs = load_judge_inputs()
    write_preflight(inputs, source)
    done = completed_scores()
    raw_path = OUT / "gpt41_judge_scores.jsonl"
    usage_total = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    started = datetime.now(timezone.utc).isoformat()
    with open(raw_path, "a") as f:
        for i, row in enumerate(inputs, start=1):
            if row["response_id"] in done:
                continue
            for attempt in (1, 2):
                try:
                    resp = client.chat.completions.create(
                        model=MODEL,
                        temperature=TEMPERATURE,
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": PROMPT},
                            {"role": "user", "content": user_payload(row)},
                        ],
                    )
                    content = resp.choices[0].message.content
                    parsed = json.loads(content)
                    norm = normalize(parsed, row)
                    usage = resp.usage.model_dump() if resp.usage else {}
                    rec = {
                        "response_id": row["response_id"],
                        "role": row["role"],
                        "model": resp.model,
                        "attempt": attempt,
                        "judge_output": norm,
                        "raw_content": content,
                        "usage": usage,
                        "created": resp.created,
                    }
                    f.write(json.dumps(rec) + "\n")
                    f.flush()
                    done[row["response_id"]] = rec
                    for key2 in usage_total:
                        usage_total[key2] += int(usage.get(key2, 0) or 0)
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(1.5)
            if i % 10 == 0:
                print(f"GPT-4.1 judge progress {i}/{len(inputs)}")
    # Re-read to include resumed prior rows in normalized CSV.
    records = list(completed_scores().values())
    rows = [r["judge_output"] for r in records]
    rows.sort(key=lambda x: x["response_id"])
    write_csv(OUT / "gpt41_judge_scores.csv", rows)
    actual_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    for rec in records:
        usage = rec.get("usage") or {}
        actual_usage["prompt_tokens"] += int(usage.get("prompt_tokens", 0) or 0)
        actual_usage["completion_tokens"] += int(usage.get("completion_tokens", 0) or 0)
        actual_usage["total_tokens"] += int(usage.get("total_tokens", 0) or 0)
    actual_cost = (
        actual_usage["prompt_tokens"] / 1_000_000 * PRICE_INPUT_PER_1M
        + actual_usage["completion_tokens"] / 1_000_000 * PRICE_OUTPUT_PER_1M
    )
    est = json.loads((OUT / "gpt41_judge_cost_estimate.json").read_text())
    est.update({
        "actual_prompt_tokens": actual_usage["prompt_tokens"],
        "actual_completion_tokens": actual_usage["completion_tokens"],
        "actual_total_tokens": actual_usage["total_tokens"],
        "actual_cost_estimate_usd": actual_cost,
    })
    jdump(OUT / "gpt41_judge_cost_estimate.json", est)
    manifest = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "n_responses_scored": len(rows),
        "api_key_source": source,
        "api_key_logged": False,
        "authorization_headers_saved": False,
        "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "prompt_path": "gpt41_judge_prompt.md",
        "schema_path": "gpt41_judge_schema.json",
        "cost_estimate_path": "gpt41_judge_cost_estimate.json",
    }
    jdump(OUT / "gpt41_judge_run_manifest.json", manifest)
    return rows


def vec3(rows):
    return np.array([[float(r["pc1"]), float(r["pc2"]), float(r["pc3"])] for r in rows], dtype=float)


def published_centroid(rows):
    arr = vec3(rows)
    deltas = np.array([
        [
            float(r["delta_pc1_from_published_centroid"]),
            float(r["delta_pc2_from_published_centroid"]),
            float(r["delta_pc3_from_published_centroid"]),
        ]
        for r in rows
    ], dtype=float)
    return (arr - deltas)[0]


def covariance_summary(arr):
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
        "percent_variance_explained_desc": (vals / vals.sum()).tolist(),
        "volume_proxy_cov_det": det if det > 0 else None,
        "volume_proxy_product_sd": float(np.prod(np.std(arr, axis=0, ddof=1))),
    }


def boolish(v):
    return str(v).lower() in ("true", "1", "yes")


def filtered_analysis():
    acts = {r["response_id"]: r for r in load_activation_rows()}
    scores = read_csv(OUT / "gpt41_judge_scores.csv")
    joined = []
    for s in scores:
        a = dict(acts[s["response_id"]])
        a.update({
            "score_0_to_3": int(s["score_0_to_3"]),
            "binary_retain_ge2": boolish(s["binary_retain_ge2"]),
            "binary_retain_eq3": boolish(s["binary_retain_eq3"]),
            "generic_assistant_collapse": boolish(s["generic_assistant_collapse"]),
            "refusal_or_safety_neutralization": boolish(s["refusal_or_safety_neutralization"]),
            "theatrical_overexpression": boolish(s["theatrical_overexpression"]),
            "rationale": s["rationale"],
        })
        joined.append(a)
    summary = []
    shifts = []
    covs = {}
    outliers = []
    report = ["# Judge-Filtered Cloud Report\n"]
    for role in sorted(set(r["role"] for r in joined)):
        role_rows = [r for r in joined if r["role"] == role]
        pub = published_centroid(role_rows)
        all_arr = vec3(role_rows)
        all_mean = all_arr.mean(axis=0)
        subsets = {
            "all": role_rows,
            "score_ge_2": [r for r in role_rows if r["binary_retain_ge2"]],
            "score_eq_3": [r for r in role_rows if r["binary_retain_eq3"]],
            "generic_assistant_collapse": [r for r in role_rows if r["generic_assistant_collapse"]],
            "theatrical_overexpression": [r for r in role_rows if r["theatrical_overexpression"]],
        }
        covs[role] = {}
        report.append(f"## {role}\n")
        all_cov = covariance_summary(all_arr)
        for name, rows in subsets.items():
            if not rows:
                continue
            arr = vec3(rows)
            mean = arr.mean(axis=0)
            dists = np.linalg.norm(arr - pub, axis=1)
            cov = covariance_summary(arr)
            if cov:
                covs[role][name] = cov
            volume = None
            if cov:
                volume = cov["volume_proxy_cov_det"] if cov["volume_proxy_cov_det"] is not None else cov["volume_proxy_product_sd"]
            row = {
                "role": role,
                "subset": name,
                "n": len(rows),
                "retained_fraction": len(rows) / len(role_rows),
                "centroid_pc1": float(mean[0]),
                "centroid_pc2": float(mean[1]),
                "centroid_pc3": float(mean[2]),
                "centroid_distance_to_published": float(np.linalg.norm(mean - pub)),
                "mean_response_distance_to_published": float(np.mean(dists)),
                "sd_pc1": float(np.std(arr[:, 0], ddof=1)) if len(rows) > 1 else None,
                "sd_pc2": float(np.std(arr[:, 1], ddof=1)) if len(rows) > 1 else None,
                "sd_pc3": float(np.std(arr[:, 2], ddof=1)) if len(rows) > 1 else None,
                "cloud_volume_proxy": volume,
            }
            summary.append(row)
            report.append(f"- {name}: n={len(rows)}, centroid=({mean[0]:.3f}, {mean[1]:.3f}, {mean[2]:.3f}), centroid distance={row['centroid_distance_to_published']:.3f}, mean distance={row['mean_response_distance_to_published']:.3f}")
            for r in sorted(rows, key=lambda x: x["distance_to_published_role_centroid_3d"], reverse=True)[:3]:
                outliers.append({
                    "role": role,
                    "subset": name,
                    "response_id": r["response_id"],
                    "score_0_to_3": r["score_0_to_3"],
                    "distance_to_published_role_centroid_3d": r["distance_to_published_role_centroid_3d"],
                    "rationale": r["rationale"],
                    "response_preview": r["generated_response"][:240].replace("\n", " "),
                })
        for target in ["score_ge_2", "score_eq_3"]:
            rows = subsets[target]
            if not rows:
                continue
            arr = vec3(rows)
            mean = arr.mean(axis=0)
            target_cov = covariance_summary(arr)
            all_vol = all_cov["volume_proxy_cov_det"] if all_cov and all_cov["volume_proxy_cov_det"] is not None else all_cov["volume_proxy_product_sd"]
            target_vol = target_cov["volume_proxy_cov_det"] if target_cov and target_cov["volume_proxy_cov_det"] is not None else target_cov["volume_proxy_product_sd"]
            all_mean_dist = float(np.mean(np.linalg.norm(all_arr - pub, axis=1)))
            target_mean_dist = float(np.mean(np.linalg.norm(arr - pub, axis=1)))
            all_cent_dist = float(np.linalg.norm(all_mean - pub))
            target_cent_dist = float(np.linalg.norm(mean - pub))
            shifts.append({
                "role": role,
                "filtered_subset": target,
                "n_filtered": len(rows),
                "delta_pc1_filtered_minus_all": float(mean[0] - all_mean[0]),
                "delta_pc2_filtered_minus_all": float(mean[1] - all_mean[1]),
                "delta_pc3_filtered_minus_all": float(mean[2] - all_mean[2]),
                "all_centroid_distance_to_published": all_cent_dist,
                "filtered_centroid_distance_to_published": target_cent_dist,
                "change_in_centroid_distance_negative_is_improvement": target_cent_dist - all_cent_dist,
                "all_mean_response_distance_to_published": all_mean_dist,
                "filtered_mean_response_distance_to_published": target_mean_dist,
                "change_in_mean_response_distance_negative_is_improvement": target_mean_dist - all_mean_dist,
                "all_cloud_volume_proxy": all_vol,
                "filtered_cloud_volume_proxy": target_vol,
                "volume_ratio_filtered_over_all": target_vol / all_vol if all_vol else None,
            })
        report.append("")
    write_csv(OUT / "judge_filtered_cloud_summary_by_role.csv", summary)
    write_csv(OUT / "judge_filtered_centroid_shifts.csv", shifts)
    write_csv(OUT / "judge_filtered_outlier_cases.csv", outliers)
    jdump(OUT / "judge_filtered_covariance_by_role.json", covs)
    (OUT / "judge_filtered_cloud_report.md").write_text("\n".join(report) + "\n")
    make_plot(joined)
    write_conclusion(summary, shifts)
    return summary, shifts


def make_plot(joined):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    projections = [(0, 1, "PC1", "PC2"), (0, 2, "PC1", "PC3"), (1, 2, "PC2", "PC3")]
    colors = {"amateur": "#1f77b4", "playwright": "#d62728"}
    for ax, (i, j, xl, yl) in zip(axes, projections):
        for role in sorted(set(r["role"] for r in joined)):
            rows = [r for r in joined if r["role"] == role]
            arr = vec3(rows)
            ge2 = [r for r in rows if r["binary_retain_ge2"]]
            eq3 = [r for r in rows if r["binary_retain_eq3"]]
            pub = published_centroid(rows)
            c = colors[role]
            ax.scatter(arr[:, i], arr[:, j], s=16, alpha=0.18, color=c, label=f"{role} all")
            if ge2:
                age2 = vec3(ge2)
                ax.scatter(age2[:, i], age2[:, j], s=26, alpha=0.65, color=c, edgecolor="black", linewidth=0.25, label=f"{role} >=2")
            if eq3:
                aeq3 = vec3(eq3)
                ax.scatter(aeq3[:, i], aeq3[:, j], s=52, alpha=0.9, marker="D", color=c, edgecolor="black", linewidth=0.4, label=f"{role} =3")
            ax.scatter([pub[i]], [pub[j]], marker="*", s=180, color=c, edgecolor="black")
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.grid(alpha=0.25)
    axes[0].legend(fontsize=7)
    fig.suptitle("GPT-4.1 retained responses over amateur/playwright activation clouds")
    fig.tight_layout()
    fig.savefig(OUT / "judge_filtered_cloud_plots.png", dpi=180)
    plt.close(fig)


def write_conclusion(summary, shifts):
    by = {(r["role"], r["subset"]): r for r in summary}
    lines = ["# Judge Filter Conclusion\n"]
    for role in sorted(set(r["role"] for r in summary)):
        all_row = by.get((role, "all"))
        ge2 = by.get((role, "score_ge_2"))
        eq3 = by.get((role, "score_eq_3"))
        lines.append(f"## {role}\n")
        lines.append(f"- Score>=2 retained: {ge2['n'] if ge2 else 0}/{all_row['n'] if all_row else 0}")
        lines.append(f"- Score==3 retained: {eq3['n'] if eq3 else 0}/{all_row['n'] if all_row else 0}")
        if ge2:
            shift = next(s for s in shifts if s["role"] == role and s["filtered_subset"] == "score_ge_2")
            lines.append(f"- Score>=2 centroid-distance change: {shift['change_in_centroid_distance_negative_is_improvement']:.3f} (negative improves)")
            lines.append(f"- Score>=2 mean-distance change: {shift['change_in_mean_response_distance_negative_is_improvement']:.3f} (negative improves)")
            lines.append(f"- Score>=2 volume ratio: {shift['volume_ratio_filtered_over_all']:.3f}")
        lines.append("")
    lines.append("## Interpretation\n")
    lines.append("1. The broad unfiltered clouds are not merely weak role-expression noise if most responses are retained at score>=2; however, score==3 subsets provide the sharper test of strong role-expression submanifolds.")
    lines.append("2. Filtering supports tighter clouds when volume ratio and axis SDs decrease; alignment improves only if centroid and mean-distance changes are negative.")
    lines.append("3. Published role vectors remain meaningful reference centroids when retained subsets stay near or move closer to the published centroid.")
    lines.append("4. Given the prior broad unfiltered spread, response-state forecasting should remain region/distribution-level unless filtered subsets prove tight enough for point forecasting.")
    lines.append("\n## Recommendation\n")
    lines.append("Analyze and visualize judge-filtered results before launching more GPU roles. If the retained subsets are tight and closer to published centroids, then expand to additional roles; if mixed, prioritize offline judge/error analysis first.")
    (OUT / "judge_filter_conclusion.md").write_text("\n".join(lines) + "\n")


def main():
    required = [
        PILOT / "judge_input_responses.jsonl",
        PILOT / "activation_cloud_per_response.csv",
        OUT / "cloud_shape_stats_by_role.csv",
        OUT / "bootstrap_sample_size_summary.csv",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required files: " + ", ".join(missing))
    inputs = load_judge_inputs()
    if len(inputs) != 120:
        raise ValueError(f"Expected 120 judge inputs, found {len(inputs)}")
    print("Scoring GPT-4.1 judge responses")
    scores = score_all()
    print(f"Scored {len(scores)} responses")
    print("Running filtered cloud analysis")
    summary, shifts = filtered_analysis()
    print(json.dumps({
        "scores": len(scores),
        "summary_rows": len(summary),
        "shift_rows": len(shifts),
        "output_dir": str(OUT.relative_to(REPO)),
    }, indent=2))


if __name__ == "__main__":
    main()
