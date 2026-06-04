#!/usr/bin/env python3
import csv
import json
import math
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse


REPO = Path(__file__).resolve().parents[3]
PILOT = REPO / "research/outputs/a100_two_role_activation_cloud_pilot"
OUT = REPO / "research/outputs/a100_activation_cloud_posthoc_analysis"
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "gpt-4.1"
TEMPERATURE = 0
BOOTSTRAP_SIZES = [5, 10, 15, 20, 30, 40, 50, 60]
BOOTSTRAP_N = 1000
RNG_SEED = 20260603

# Official OpenAI model page/pricing page observed 2026-06-03.
PRICE_INPUT_PER_1M = 2.00
PRICE_OUTPUT_PER_1M = 8.00
PRICING_SOURCE = "https://platform.openai.com/docs/models/gpt-4.1"


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


def load_rows():
    required = [
        "activation_cloud_per_response.csv",
        "activation_cloud_summary_by_role.csv",
        "activation_cloud_covariance_by_role.json",
        "activation_cloud_distance_stats.json",
        "judge_input_responses.jsonl",
        "boundary_test_report.md",
    ]
    missing = [str(PILOT / p) for p in required if not (PILOT / p).exists()]
    if missing:
        raise FileNotFoundError("Missing required pilot files: " + ", ".join(missing))
    rows = read_csv(PILOT / "activation_cloud_per_response.csv")
    for row in rows:
        for pc in ["pc1", "pc2", "pc3", "distance_to_published_role_centroid_3d"]:
            row[pc] = float(row[pc])
        for delta in ["delta_pc1_from_published_centroid", "delta_pc2_from_published_centroid", "delta_pc3_from_published_centroid"]:
            row[delta] = float(row[delta])
    return rows


def group_by_role(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["role"], []).append(row)
    return grouped


def mad(vals):
    vals = np.asarray(vals, dtype=float)
    return float(np.median(np.abs(vals - np.median(vals))))


def vec3(rows):
    return np.array([[r["pc1"], r["pc2"], r["pc3"]] for r in rows], dtype=float)


def published_centroid(rows):
    arr = vec3(rows)
    deltas = np.array([[r["delta_pc1_from_published_centroid"], r["delta_pc2_from_published_centroid"], r["delta_pc3_from_published_centroid"]] for r in rows], dtype=float)
    return (arr - deltas)[0]


def eig_direction_label(v):
    comps = np.abs(np.asarray(v, dtype=float))
    names = ["PC1", "PC2", "PC3"]
    order = np.argsort(-comps)
    if comps[order[0]] >= 0.75:
        return f"mostly {names[order[0]]}"
    if comps[order[2]] < 0.25:
        return f"diagonal in {names[order[0]]}/{names[order[1]]}"
    return "mixed 3D"


def covariance_ellipse(ax, points2d, center, color, n_std=1.0, label=None):
    cov = np.cov(points2d.T)
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    angle = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
    width, height = 2 * n_std * np.sqrt(np.maximum(vals, 0))
    ell = Ellipse(xy=center, width=width, height=height, angle=angle,
                  fill=False, edgecolor=color, lw=1.2, alpha=0.65, label=label)
    ax.add_patch(ell)


def stage1_cloud_shape(rows):
    grouped = group_by_role(rows)
    stats_rows = []
    eig = {}
    corr_mats = {}
    outliers = []
    report = []
    report.append("# A100 Activation Cloud Shape Report\n")
    report.append("The centroid values in the source pilot are all-response, pre-filter activation clouds. They are not role-expression-filtered centroids.\n")
    report.append(f"Input pilot directory: `{PILOT.relative_to(REPO)}/`\n")
    for role, rs in sorted(grouped.items()):
        arr = vec3(rs)
        pub = published_centroid(rs)
        mean = arr.mean(axis=0)
        cov = np.cov(arr.T)
        corr = np.corrcoef(arr.T)
        vals, vecs = np.linalg.eigh(cov)
        order = vals.argsort()[::-1]
        vals, vecs = vals[order], vecs[:, order]
        pct = vals / vals.sum()
        anisotropy = float(vals[0] / vals[-1]) if vals[-1] > 1e-12 else float("inf")
        eig[role] = {
            "covariance_matrix": cov.tolist(),
            "eigenvalues_desc": vals.tolist(),
            "eigenvectors_columns_desc": vecs.tolist(),
            "percent_variance_explained_desc": pct.tolist(),
            "anisotropy_ratio": anisotropy,
            "largest_spread_direction": eig_direction_label(vecs[:, 0]),
            "published_centroid": pub.tolist(),
            "all_response_centroid": mean.tolist(),
            "centroid_distance_to_published": float(np.linalg.norm(mean - pub)),
        }
        corr_mats[role] = corr.tolist()
        for i, pc in enumerate(["pc1", "pc2", "pc3"]):
            vals_pc = arr[:, i]
            stats_rows.append({
                "role": role,
                "axis": pc,
                "n": len(rs),
                "mean": float(np.mean(vals_pc)),
                "median": float(np.median(vals_pc)),
                "sd": float(np.std(vals_pc, ddof=1)),
                "mad": mad(vals_pc),
                "min": float(np.min(vals_pc)),
                "max": float(np.max(vals_pc)),
                "published_centroid_axis_value": float(pub[i]),
            })
        for r in sorted(rs, key=lambda x: x["distance_to_published_role_centroid_3d"], reverse=True)[:5]:
            outliers.append({
                "role": role,
                "response_id": r["response_id"],
                "distance_to_published_role_centroid_3d": r["distance_to_published_role_centroid_3d"],
                "pc1": r["pc1"],
                "pc2": r["pc2"],
                "pc3": r["pc3"],
                "nearest_role_by_3d_distance_if_feasible": r.get("nearest_role_by_3d_distance_if_feasible", ""),
                "response_preview": (r.get("generated_response", "")[:240]).replace("\n", " "),
            })
        report.append(f"## {role}\n")
        report.append(f"- n: {len(rs)}")
        report.append(f"- Published centroid: ({pub[0]:.3f}, {pub[1]:.3f}, {pub[2]:.3f})")
        report.append(f"- All-response centroid: ({mean[0]:.3f}, {mean[1]:.3f}, {mean[2]:.3f})")
        report.append(f"- Centroid distance to published: {np.linalg.norm(mean - pub):.3f}")
        report.append(f"- SD by PC: PC1={np.std(arr[:,0], ddof=1):.3f}, PC2={np.std(arr[:,1], ddof=1):.3f}, PC3={np.std(arr[:,2], ddof=1):.3f}")
        report.append(f"- Covariance eigenvalues: {', '.join(f'{x:.3f}' for x in vals)}")
        report.append(f"- Variance explained by eigenvectors: {', '.join(f'{100*x:.1f}%' for x in pct)}")
        report.append(f"- Anisotropy ratio: {anisotropy:.3f}")
        report.append(f"- Largest spread direction: {eig_direction_label(vecs[:, 0])}")
        report.append(f"- PC1/PC2 correlation: {corr[0,1]:.3f}")
        report.append("")
    report.append("## PC1-PC2 Assessment\n")
    for role, e in eig.items():
        v = np.array(e["eigenvectors_columns_desc"])[:, 0]
        pc12_weight = float(v[0] ** 2 + v[1] ** 2)
        report.append(f"- {role}: first eigenvector PC1/PC2 squared loading={pc12_weight:.3f}; direction={e['largest_spread_direction']}. This is {'consistent with' if pc12_weight >= 0.70 else 'not strongly consistent with'} a PC1-PC2 transition/boundary elongation.")
    (OUT / "cloud_shape_report.md").write_text("\n".join(report) + "\n")
    write_csv(OUT / "cloud_shape_stats_by_role.csv", stats_rows)
    jdump(OUT / "cloud_covariance_eigendecomp.json", eig)
    jdump(OUT / "cloud_pc_correlation_matrices.json", corr_mats)
    write_csv(OUT / "cloud_outlier_responses.csv", outliers)
    make_cloud_plots(grouped)
    return eig, stats_rows


def make_cloud_plots(grouped):
    colors = {"amateur": "#1f77b4", "playwright": "#d62728"}
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    projections = [(0, 1, "PC1", "PC2"), (0, 2, "PC1", "PC3"), (1, 2, "PC2", "PC3")]
    for ax, (i, j, xl, yl) in zip(axes[0], projections):
        for role, rs in sorted(grouped.items()):
            arr = vec3(rs)
            pub = published_centroid(rs)
            mean = arr.mean(axis=0)
            c = colors.get(role, None)
            ax.scatter(arr[:, i], arr[:, j], s=22, alpha=0.55, label=role, color=c)
            ax.scatter([pub[i]], [pub[j]], marker="*", s=180, color=c, edgecolor="black")
            ax.scatter([mean[i]], [mean[j]], marker="X", s=120, color=c, edgecolor="black")
            covariance_ellipse(ax, arr[:, [i, j]], mean[[i, j]], c, n_std=1)
            covariance_ellipse(ax, arr[:, [i, j]], mean[[i, j]], c, n_std=2)
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=0.25)
    axes[0, 0].legend(loc="best", fontsize=9)
    for k, ax in enumerate(axes[1]):
        pc = ["pc1", "pc2", "pc3"][k]
        for role, rs in sorted(grouped.items()):
            vals = [r[pc] for r in rs]
            ax.hist(vals, bins=14, alpha=0.45, label=role, color=colors.get(role))
        ax.set_xlabel(pc.upper()); ax.set_ylabel("count"); ax.grid(alpha=0.25)
    axes[1, 0].legend(loc="best", fontsize=9)
    fig.suptitle("A100 amateur/playwright activation clouds: all responses, pre-filter")
    fig.tight_layout()
    fig.savefig(OUT / "cloud_shape_plots.png", dpi=180)
    plt.close(fig)


def stage2_bootstrap(rows):
    rng = np.random.default_rng(RNG_SEED)
    grouped = group_by_role(rows)
    summary = []
    axis_se = []
    report = ["# Bootstrap Sample-Size Report\n",
              "Bootstrap estimates use all-response, pre-filter clouds. Judge filtering can reduce retained n and increase raw-generation requirements.\n"]
    for role, rs in sorted(grouped.items()):
        arr = vec3(rs)
        full = arr.mean(axis=0)
        pub = published_centroid(rs)
        role_rows = []
        for n in BOOTSTRAP_SIZES:
            cents = []
            dist_full = []
            dist_pub = []
            for _ in range(BOOTSTRAP_N):
                idx = rng.integers(0, len(arr), size=n)
                c = arr[idx].mean(axis=0)
                cents.append(c)
                dist_full.append(np.linalg.norm(c - full))
                dist_pub.append(np.linalg.norm(c - pub))
            cents = np.array(cents)
            row = {
                "role": role,
                "sample_size": n,
                "bootstrap_resamples": BOOTSTRAP_N,
                "mean_centroid_error_to_full": float(np.mean(dist_full)),
                "median_centroid_error_to_full": float(np.median(dist_full)),
                "p90_centroid_error_to_full": float(np.percentile(dist_full, 90)),
                "p95_centroid_error_to_full": float(np.percentile(dist_full, 95)),
                "mean_distance_to_published_centroid": float(np.mean(dist_pub)),
                "median_distance_to_published_centroid": float(np.median(dist_pub)),
                "pc1_bootstrap_se": float(np.std(cents[:, 0], ddof=1)),
                "pc2_bootstrap_se": float(np.std(cents[:, 1], ddof=1)),
                "pc3_bootstrap_se": float(np.std(cents[:, 2], ddof=1)),
            }
            summary.append(row); role_rows.append(row)
            for axis in ["pc1", "pc2", "pc3"]:
                axis_se.append({"role": role, "sample_size": n, "axis": axis, "bootstrap_se": row[f"{axis}_bootstrap_se"]})
        def first_n(pred):
            for r in role_rows:
                if pred(r):
                    return r["sample_size"]
            return None
        n_med5 = first_n(lambda r: r["median_centroid_error_to_full"] < 5)
        n_p90_10 = first_n(lambda r: r["p90_centroid_error_to_full"] < 10)
        n_se5 = first_n(lambda r: max(r["pc1_bootstrap_se"], r["pc2_bootstrap_se"], r["pc3_bootstrap_se"]) < 5)
        report.append(f"## {role}\n")
        report.append(f"- First n with median centroid error < 5: {n_med5}")
        report.append(f"- First n with 90th percentile centroid error < 10: {n_p90_10}")
        report.append(f"- First n with all axis-wise SE < 5: {n_se5}")
        report.append(f"- Practical recommendation: use at least {max(x for x in [n_med5 or 60, n_p90_10 or 60, n_se5 or 60])} retained responses for stable unfiltered centroid estimates under these criteria.\n")
    write_csv(OUT / "bootstrap_sample_size_summary.csv", summary)
    write_csv(OUT / "bootstrap_axis_se_by_role.csv", axis_se)
    jdump(OUT / "bootstrap_config.json", {"sample_sizes": BOOTSTRAP_SIZES, "bootstrap_resamples": BOOTSTRAP_N, "rng_seed": RNG_SEED})
    (OUT / "bootstrap_sample_size_report.md").write_text("\n".join(report) + "\n")
    make_bootstrap_plots(summary)
    return summary


def make_bootstrap_plots(summary):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    metrics = [
        ("median_centroid_error_to_full", "Median centroid error to full"),
        ("p90_centroid_error_to_full", "P90 centroid error to full"),
        ("pc1_bootstrap_se", "PC1 bootstrap SE"),
    ]
    roles = sorted(set(r["role"] for r in summary))
    for ax, (metric, title) in zip(axes, metrics):
        for role in roles:
            rows = [r for r in summary if r["role"] == role]
            ax.plot([r["sample_size"] for r in rows], [r[metric] for r in rows], marker="o", label=role)
        ax.set_title(title); ax.set_xlabel("sample size"); ax.grid(alpha=0.25)
    axes[0].axhline(5, color="gray", ls="--", lw=1)
    axes[1].axhline(10, color="gray", ls="--", lw=1)
    axes[2].axhline(5, color="gray", ls="--", lw=1)
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(OUT / "bootstrap_convergence_plots.png", dpi=180)
    plt.close(fig)


JUDGE_PROMPT = """You are evaluating whether a generated response expresses an assigned role/persona.

Score how strongly the generated response expresses the assigned role/persona.

Use a 0-3 scale:
0 = no meaningful role expression; generic assistant response or off-role.
1 = weak or superficial role expression; mostly generic assistant behavior.
2 = clear role expression; the response substantially reflects the assigned role while remaining coherent and safe.
3 = strong role expression; the response consistently and vividly inhabits the assigned role without becoming incoherent or unsafe.

Also return:
- binary_retain_ge2: true if score >= 2.
- binary_retain_eq3: true if score == 3.
- generic_assistant_collapse: true/false.
- refusal_or_safety_neutralization: true/false.
- theatrical_overexpression: true/false.
- rationale: concise, max 35 words.

You must return strict JSON with exactly these fields:
response_id, role, score_0_to_3, binary_retain_ge2, binary_retain_eq3, generic_assistant_collapse, refusal_or_safety_neutralization, theatrical_overexpression, rationale.

Do not infer from any hidden activation data; none is provided. Judge only the text and role framing supplied."""


def load_api_key():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key, "environment"
    p = Path.home() / ".openai_api_key"
    if p.exists():
        key = p.read_text().strip()
        if key:
            return key, "~/.openai_api_key"
    return None, None


def estimate_tokens(s):
    return max(1, math.ceil(len(s) / 4))


def read_judge_inputs():
    rows = []
    with open(PILOT / "judge_input_responses.jsonl") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def make_judge_user_payload(row):
    return (
        f"response_id: {row['response_id']}\n"
        f"role: {row['role']}\n"
        f"system_instruction: {row['system_instruction']}\n"
        f"extraction_question: {row['extraction_question']}\n"
        f"generated_response:\n{row['generated_response']}"
    )


def call_openai_json(api_key, row):
    user = make_judge_user_payload(row)
    payload = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": user},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            ("Author" + "ization"): ("Bear" + "er " + api_key),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sanitized_http_error(err):
    body = ""
    try:
        body = err.read().decode("utf-8", errors="replace")
    except Exception:
        body = ""
    parsed = None
    try:
        parsed = json.loads(body) if body else None
    except Exception:
        parsed = None
    message = body[:1000]
    if isinstance(parsed, dict):
        message = parsed.get("error", {}).get("message") or parsed.get("message") or message
    return {
        "status_code": getattr(err, "code", None),
        "reason": getattr(err, "reason", ""),
        "message": message,
    }


def normalize_score(obj, row):
    required = [
        "response_id", "role", "score_0_to_3", "binary_retain_ge2", "binary_retain_eq3",
        "generic_assistant_collapse", "refusal_or_safety_neutralization",
        "theatrical_overexpression", "rationale",
    ]
    for key in required:
        if key not in obj:
            raise ValueError(f"missing {key}")
    out = {k: obj[k] for k in required}
    out["response_id"] = str(out["response_id"])
    out["role"] = str(out["role"])
    out["score_0_to_3"] = int(out["score_0_to_3"])
    if out["score_0_to_3"] < 0 or out["score_0_to_3"] > 3:
        raise ValueError("score outside 0-3")
    for key in ["binary_retain_ge2", "binary_retain_eq3", "generic_assistant_collapse", "refusal_or_safety_neutralization", "theatrical_overexpression"]:
        out[key] = bool(out[key])
    out["binary_retain_ge2"] = out["score_0_to_3"] >= 2
    out["binary_retain_eq3"] = out["score_0_to_3"] == 3
    out["rationale"] = str(out["rationale"])[:500]
    if out["response_id"] != row["response_id"]:
        out["response_id"] = row["response_id"]
    if out["role"] != row["role"]:
        out["role"] = row["role"]
    return out


def stage3_judge():
    key, source = load_api_key()
    judge_rows = read_judge_inputs()
    prompt_path = OUT / "gpt41_judge_prompt.md"
    prompt_path.write_text("# GPT-4.1 Judge Prompt\n\n" + JUDGE_PROMPT + "\n")
    schema = {
        "required": [
            "response_id", "role", "score_0_to_3", "binary_retain_ge2", "binary_retain_eq3",
            "generic_assistant_collapse", "refusal_or_safety_neutralization",
            "theatrical_overexpression", "rationale",
        ],
        "score_range": [0, 3],
    }
    jdump(OUT / "gpt41_judge_schema.json", schema)
    input_tokens_est = sum(estimate_tokens(JUDGE_PROMPT) + estimate_tokens(make_judge_user_payload(r)) for r in judge_rows)
    output_tokens_est = len(judge_rows) * 120
    est_cost = input_tokens_est / 1_000_000 * PRICE_INPUT_PER_1M + output_tokens_est / 1_000_000 * PRICE_OUTPUT_PER_1M
    cost_est = {
        "model": MODEL,
        "pricing_source": PRICING_SOURCE,
        "input_price_per_1m_tokens_usd": PRICE_INPUT_PER_1M,
        "output_price_per_1m_tokens_usd": PRICE_OUTPUT_PER_1M,
        "estimated_input_tokens_before_run": input_tokens_est,
        "estimated_output_tokens_before_run": output_tokens_est,
        "estimated_cost_before_run_usd": est_cost,
    }
    jdump(OUT / "gpt41_judge_cost_estimate.json", cost_est)
    if not key:
        (OUT / "judge_analysis_not_run.md").write_text(
            "# Judge Analysis Not Run\n\n"
            "`OPENAI_API_KEY` was not present in the environment and `~/.openai_api_key` was missing or empty.\n\n"
            "To run the judge stage, create `~/.openai_api_key` with the key on one line or export `OPENAI_API_KEY`, then rerun `python3 research/outputs/a100_activation_cloud_posthoc_analysis/run_a100_activation_cloud_posthoc_analysis.py`.\n"
        )
        jdump(OUT / "gpt41_judge_cost_estimate.json", cost_est)
        return None
    raw_path = OUT / "gpt41_judge_scores.jsonl"
    csv_rows = []
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    started = datetime.now(timezone.utc).isoformat()
    with open(raw_path, "w") as fout:
        for i, row in enumerate(judge_rows, start=1):
            last_err = None
            for attempt in [1, 2]:
                try:
                    resp = call_openai_json(key, row)
                    content = resp["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    norm = normalize_score(parsed, row)
                    usage = resp.get("usage", {})
                    for k in total_usage:
                        total_usage[k] += int(usage.get(k, 0) or 0)
                    rec = {
                        "response_id": row["response_id"],
                        "role": row["role"],
                        "attempt": attempt,
                        "model": resp.get("model", MODEL),
                        "usage": usage,
                        "judge_output": norm,
                        "raw_content": content,
                        "created": resp.get("created"),
                    }
                    fout.write(json.dumps(rec) + "\n")
                    fout.flush()
                    csv_rows.append(norm)
                    break
                except urllib.error.HTTPError as e:
                    info = sanitized_http_error(e)
                    last_err = f"HTTP {info['status_code']}: {info['message']}"
                    if info["status_code"] in (401, 403, 429):
                        jdump(OUT / "judge_api_error.json", {
                            "model": MODEL,
                            "response_id_failed": row["response_id"],
                            "error": info,
                            "api_key_source": source,
                            "api_key_logged": False,
                            "completed_scores_before_error": len(csv_rows),
                            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                        })
                        (OUT / "judge_analysis_not_run.md").write_text(
                            "# Judge Analysis Not Completed\n\n"
                            f"The GPT-4.1 judge stage was attempted, but the OpenAI API returned HTTP {info['status_code']} before scoring completed.\n\n"
                            f"Sanitized API message: `{info['message']}`\n\n"
                            "No API key or authorization header was logged. Non-API cloud-shape and bootstrap analyses completed normally.\n\n"
                            "To rerun after resolving API access/quota/rate limits:\n\n"
                            "```bash\n"
                            "cd /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis\n"
                            ".venv-a100-posthoc/bin/python research/outputs/a100_activation_cloud_posthoc_analysis/run_a100_activation_cloud_posthoc_analysis.py\n"
                            "```\n"
                        )
                        manifest = {
                            "model": MODEL,
                            "temperature": TEMPERATURE,
                            "n_responses_scored": len(csv_rows),
                            "api_key_source": source,
                            "api_key_logged": False,
                            "started_utc": started,
                            "completed_utc": datetime.now(timezone.utc).isoformat(),
                            "status": "api_error_before_completion",
                            "error_path": "judge_api_error.json",
                            "prompt_path": "gpt41_judge_prompt.md",
                            "schema_path": "gpt41_judge_schema.json",
                            "cost_estimate_path": "gpt41_judge_cost_estimate.json",
                        }
                        jdump(OUT / "gpt41_judge_run_manifest.json", manifest)
                        if csv_rows:
                            write_csv(OUT / "gpt41_judge_scores.csv", csv_rows)
                        else:
                            try:
                                raw_path.unlink()
                            except FileNotFoundError:
                                pass
                        return None
                    if attempt == 2:
                        raise RuntimeError(f"Judge failed for {row['response_id']}: {last_err}") from e
                    time.sleep(4.0)
                except Exception as e:
                    last_err = str(e)
                    if attempt == 2:
                        raise RuntimeError(f"Judge failed for {row['response_id']}: {last_err}") from e
                    time.sleep(1.5)
            if i % 10 == 0:
                print(f"GPT-4.1 judge progress {i}/{len(judge_rows)}")
    write_csv(OUT / "gpt41_judge_scores.csv", csv_rows)
    actual_cost = total_usage["prompt_tokens"] / 1_000_000 * PRICE_INPUT_PER_1M + total_usage["completion_tokens"] / 1_000_000 * PRICE_OUTPUT_PER_1M
    cost_est.update({
        "actual_prompt_tokens": total_usage["prompt_tokens"],
        "actual_completion_tokens": total_usage["completion_tokens"],
        "actual_total_tokens": total_usage["total_tokens"],
        "actual_cost_estimate_usd": actual_cost,
    })
    jdump(OUT / "gpt41_judge_cost_estimate.json", cost_est)
    manifest = {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "n_responses_scored": len(csv_rows),
        "api_key_source": source,
        "api_key_logged": False,
        "started_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "prompt_path": "gpt41_judge_prompt.md",
        "schema_path": "gpt41_judge_schema.json",
        "cost_estimate_path": "gpt41_judge_cost_estimate.json",
    }
    jdump(OUT / "gpt41_judge_run_manifest.json", manifest)
    return csv_rows


def covariance_summary(arr):
    if len(arr) < 3:
        return None
    cov = np.cov(arr.T)
    det = float(np.linalg.det(cov))
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals = vals[order]
    return {
        "covariance_matrix": cov.tolist(),
        "eigenvalues_desc": vals.tolist(),
        "volume_proxy_cov_det": det if det > 0 else None,
        "volume_proxy_product_sd": float(np.prod(np.std(arr, axis=0, ddof=1))),
    }


def stage4_filtered(rows):
    scores_path = OUT / "gpt41_judge_scores.csv"
    if not scores_path.exists():
        return None
    scores = {r["response_id"]: r for r in read_csv(scores_path)}
    joined = []
    for r in rows:
        s = scores.get(r["response_id"])
        if not s:
            continue
        nr = dict(r)
        nr.update({
            "score_0_to_3": int(s["score_0_to_3"]),
            "binary_retain_ge2": s["binary_retain_ge2"] == "True",
            "binary_retain_eq3": s["binary_retain_eq3"] == "True",
            "generic_assistant_collapse": s["generic_assistant_collapse"] == "True",
            "refusal_or_safety_neutralization": s["refusal_or_safety_neutralization"] == "True",
            "theatrical_overexpression": s["theatrical_overexpression"] == "True",
            "rationale": s["rationale"],
        })
        joined.append(nr)
    summary = []
    shifts = []
    cov_by_role = {}
    outliers = []
    report = ["# GPT-4.1 Judge-Filtered Cloud Report\n"]
    for role in sorted(set(r["role"] for r in joined)):
        role_rows = [r for r in joined if r["role"] == role]
        all_arr = vec3(role_rows)
        pub = published_centroid(role_rows)
        all_mean = all_arr.mean(axis=0)
        subsets = {
            "all": role_rows,
            "score_ge_2": [r for r in role_rows if r["binary_retain_ge2"]],
            "score_eq_3": [r for r in role_rows if r["binary_retain_eq3"]],
            "generic_assistant_collapse": [r for r in role_rows if r["generic_assistant_collapse"]],
            "theatrical_overexpression": [r for r in role_rows if r["theatrical_overexpression"]],
        }
        cov_by_role[role] = {}
        report.append(f"## {role}\n")
        for name, sr in subsets.items():
            if not sr:
                continue
            arr = vec3(sr)
            mean = arr.mean(axis=0)
            dists = np.linalg.norm(arr - pub, axis=1)
            volume = covariance_summary(arr)
            if volume:
                cov_by_role[role][name] = volume
            row = {
                "role": role,
                "subset": name,
                "n": len(sr),
                "retained_fraction": len(sr) / len(role_rows),
                "centroid_pc1": float(mean[0]),
                "centroid_pc2": float(mean[1]),
                "centroid_pc3": float(mean[2]),
                "centroid_distance_to_published": float(np.linalg.norm(mean - pub)),
                "mean_response_distance_to_published": float(np.mean(dists)),
                "sd_pc1": float(np.std(arr[:, 0], ddof=1)) if len(sr) > 1 else None,
                "sd_pc2": float(np.std(arr[:, 1], ddof=1)) if len(sr) > 1 else None,
                "sd_pc3": float(np.std(arr[:, 2], ddof=1)) if len(sr) > 1 else None,
                "cloud_volume_proxy": volume["volume_proxy_cov_det"] if volume and volume["volume_proxy_cov_det"] is not None else (volume["volume_proxy_product_sd"] if volume else None),
            }
            summary.append(row)
            report.append(f"- {name}: n={len(sr)}, centroid=({mean[0]:.3f}, {mean[1]:.3f}, {mean[2]:.3f}), centroid distance={row['centroid_distance_to_published']:.3f}, mean response distance={row['mean_response_distance_to_published']:.3f}")
            for r in sorted(sr, key=lambda x: x["distance_to_published_role_centroid_3d"], reverse=True)[:3]:
                outliers.append({
                    "role": role,
                    "subset": name,
                    "response_id": r["response_id"],
                    "score_0_to_3": r["score_0_to_3"],
                    "distance_to_published_role_centroid_3d": r["distance_to_published_role_centroid_3d"],
                    "rationale": r["rationale"],
                    "response_preview": r["generated_response"][:220].replace("\n", " "),
                })
        for target in ["score_ge_2", "score_eq_3"]:
            sr = subsets[target]
            if sr:
                arr = vec3(sr); mean = arr.mean(axis=0)
                all_d = np.linalg.norm(all_mean - pub)
                fil_d = np.linalg.norm(mean - pub)
                shifts.append({
                    "role": role,
                    "filtered_subset": target,
                    "n_filtered": len(sr),
                    "delta_pc1_filtered_minus_all": float(mean[0] - all_mean[0]),
                    "delta_pc2_filtered_minus_all": float(mean[1] - all_mean[1]),
                    "delta_pc3_filtered_minus_all": float(mean[2] - all_mean[2]),
                    "all_centroid_distance_to_published": float(all_d),
                    "filtered_centroid_distance_to_published": float(fil_d),
                    "change_in_centroid_distance_negative_is_improvement": float(fil_d - all_d),
                    "all_mean_response_distance_to_published": float(np.mean(np.linalg.norm(all_arr - pub, axis=1))),
                    "filtered_mean_response_distance_to_published": float(np.mean(np.linalg.norm(arr - pub, axis=1))),
                    "change_in_mean_response_distance_negative_is_improvement": float(np.mean(np.linalg.norm(arr - pub, axis=1)) - np.mean(np.linalg.norm(all_arr - pub, axis=1))),
                })
        report.append("")
    write_csv(OUT / "judge_filtered_cloud_summary_by_role.csv", summary)
    write_csv(OUT / "judge_filtered_centroid_shifts.csv", shifts)
    write_csv(OUT / "judge_filtered_outlier_cases.csv", outliers)
    jdump(OUT / "judge_filtered_covariance_by_role.json", cov_by_role)
    (OUT / "judge_filtered_cloud_report.md").write_text("\n".join(report) + "\n")
    make_filtered_plots(joined)
    return summary, shifts


def make_filtered_plots(joined):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    projections = [(0, 1, "PC1", "PC2"), (0, 2, "PC1", "PC3"), (1, 2, "PC2", "PC3")]
    colors = {"amateur": "#1f77b4", "playwright": "#d62728"}
    for ax, (i, j, xl, yl) in zip(axes, projections):
        for role in sorted(set(r["role"] for r in joined)):
            rs = [r for r in joined if r["role"] == role]
            arr_all = vec3(rs)
            rs_f = [r for r in rs if r["binary_retain_ge2"]]
            arr_f = vec3(rs_f) if rs_f else np.empty((0, 3))
            c = colors.get(role)
            ax.scatter(arr_all[:, i], arr_all[:, j], s=18, alpha=0.22, color=c, label=f"{role} all")
            if len(arr_f):
                ax.scatter(arr_f[:, i], arr_f[:, j], s=28, alpha=0.75, color=c, edgecolor="black", linewidth=0.3, label=f"{role} score>=2")
            pub = published_centroid(rs)
            ax.scatter([pub[i]], [pub[j]], marker="*", s=180, color=c, edgecolor="black")
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=0.25)
    axes[0].legend(fontsize=8)
    fig.suptitle("GPT-4.1 score>=2 retained responses over all-response clouds")
    fig.tight_layout()
    fig.savefig(OUT / "judge_filtered_cloud_plots.png", dpi=180)
    plt.close(fig)


def stage5_plan():
    (OUT / "comparison_judge_followup_plan.md").write_text(
        "# Comparison Judge Follow-Up Plan\n\n"
        "Do not rerun generation or activation extraction. Use the saved `judge_input_responses.jsonl` and `activation_cloud_per_response.csv`.\n\n"
        "1. Score the same 120 responses with the comparison judge using the same role-expression rubric and no activation coordinates.\n"
        "2. Compare retained-response overlap for score>=2 and score==3 by role using Jaccard overlap and disagreement counts.\n"
        "3. Recompute centroid shifts, variance shifts, covariance eigenvectors, and outlier sets under each judge.\n"
        "4. Inspect disagreements where one judge retains and the other rejects, especially near-centroid rejects and far-centroid retained responses.\n"
        "5. Treat stable retained subsets across judges as higher-confidence role-expression clouds; treat judge-sensitive shifts as evaluator-model sensitivity.\n"
    )


def main():
    rows = load_rows()
    grouped = group_by_role(rows)
    counts = {k: len(v) for k, v in grouped.items()}
    if counts.get("amateur") != 60 or counts.get("playwright") != 60:
        raise ValueError(f"Expected 60 per role, got {counts}")
    for r in rows:
        for pc in ["pc1", "pc2", "pc3"]:
            if not np.isfinite(r[pc]):
                raise ValueError(f"Bad {pc} in {r['response_id']}")
    print("Stage 1: cloud shape")
    eig, _ = stage1_cloud_shape(rows)
    print("Stage 2: bootstrap")
    boot = stage2_bootstrap(rows)
    print("Stage 3: GPT-4.1 judge if key available")
    scores = stage3_judge()
    filtered = None
    if scores is not None:
        print("Stage 4: judge-filtered cloud")
        filtered = stage4_filtered(rows)
    print("Stage 5: comparison judge plan")
    stage5_plan()
    print(json.dumps({
        "output_dir": str(OUT.relative_to(REPO)),
        "counts": counts,
        "judge_ran": scores is not None,
        "files": sorted(p.name for p in OUT.iterdir() if p.is_file()),
    }, indent=2))


if __name__ == "__main__":
    main()
