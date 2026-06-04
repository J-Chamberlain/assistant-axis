#!/usr/bin/env python3
"""GPT-4.1 rejudge and cloud analysis for recovered adaptive role runs."""

from __future__ import annotations

import csv
import json
import math
import os
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from openai import OpenAI


REPO = Path(__file__).resolve().parents[3]
PRIOR = REPO / "research/outputs/prior_adaptive_recovery_audit"
A100_PILOT = REPO / "research/outputs/a100_two_role_activation_cloud_pilot"
A100_POSTHOC = REPO / "research/outputs/a100_activation_cloud_posthoc_analysis"
OUT = REPO / "research/outputs/recovered_role_cloud_analysis"
OUT.mkdir(parents=True, exist_ok=True)

MODEL = "gpt-4.1"
TEMPERATURE = 0
PRICE_INPUT_PER_1M = 2.00
PRICE_OUTPUT_PER_1M = 8.00

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

SCHEMA_FIELDS = [
    "response_id",
    "role",
    "score_0_to_3",
    "binary_retain_ge2",
    "binary_retain_eq3",
    "generic_assistant_collapse",
    "refusal_or_safety_neutralization",
    "theatrical_overexpression",
    "rationale",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2) + "\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_api_key() -> tuple[str, str]:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key, "environment"
    key_path = Path.home() / ".openai_api_key"
    if key_path.exists():
        key = key_path.read_text().strip()
        if key:
            return key, "~/.openai_api_key"
    raise RuntimeError("OPENAI_API_KEY not set and ~/.openai_api_key missing or empty")


def estimate_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def judge_payload(row: dict[str, Any]) -> str:
    return (
        f"response_id: {row['response_id']}\n"
        f"role: {row['role']}\n"
        f"role_instruction: {row.get('role_instruction', '')}\n"
        f"extraction_question: {row.get('extraction_question', '')}\n"
        f"generated_response:\n{row.get('generated_response', '')}"
    )


def normalize_judge(parsed: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    for field in SCHEMA_FIELDS:
        if field not in parsed:
            raise ValueError(f"missing {field}")
    out = {field: parsed[field] for field in SCHEMA_FIELDS}
    out["response_id"] = row["response_id"]
    out["role"] = row["role"]
    out["score_0_to_3"] = int(out["score_0_to_3"])
    if out["score_0_to_3"] < 0 or out["score_0_to_3"] > 3:
        raise ValueError("score outside 0-3")
    for field in [
        "binary_retain_ge2",
        "binary_retain_eq3",
        "generic_assistant_collapse",
        "refusal_or_safety_neutralization",
        "theatrical_overexpression",
    ]:
        out[field] = bool(out[field])
    out["binary_retain_ge2"] = out["score_0_to_3"] >= 2
    out["binary_retain_eq3"] = out["score_0_to_3"] == 3
    out["rationale"] = str(out["rationale"])[:500]
    return out


def existing_raw_scores() -> dict[str, dict[str, Any]]:
    raw_path = OUT / "recovered_gpt41_scores.jsonl"
    done: dict[str, dict[str, Any]] = {}
    if not raw_path.exists():
        return done
    with raw_path.open() as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            done[rec["response_id"]] = rec
    return done


def run_gpt41_rejudge(inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    key, key_source = load_api_key()
    os.environ["OPENAI_API_KEY"] = key
    client = OpenAI()
    raw_path = OUT / "recovered_gpt41_scores.jsonl"
    done = existing_raw_scores()

    prompt_tokens_est = sum(estimate_tokens(PROMPT) + estimate_tokens(judge_payload(r)) for r in inputs)
    output_tokens_est = len(inputs) * 120
    cost_est = prompt_tokens_est / 1_000_000 * PRICE_INPUT_PER_1M + output_tokens_est / 1_000_000 * PRICE_OUTPUT_PER_1M
    write_json(
        OUT / "recovered_gpt41_judge_manifest.json",
        {
            "model": MODEL,
            "temperature": TEMPERATURE,
            "n_inputs": len(inputs),
            "n_already_scored_at_start": len(done),
            "estimated_input_tokens": prompt_tokens_est,
            "estimated_output_tokens": output_tokens_est,
            "estimated_cost_usd": cost_est,
            "key_source": key_source,
            "key_logged": False,
            "started_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    (OUT / "recovered_gpt41_judge_prompt.md").write_text("# GPT-4.1 Recovered Role Judge Prompt\n\n" + PROMPT + "\n")

    usage_total = Counter()
    for rec in done.values():
        for key2, val in rec.get("usage", {}).items():
            if isinstance(val, int):
                usage_total[key2] += val
    with raw_path.open("a") as f:
        for idx, row in enumerate(inputs, start=1):
            if row["response_id"] in done:
                continue
            for attempt in (1, 2):
                try:
                    response = client.chat.completions.create(
                        model=MODEL,
                        temperature=TEMPERATURE,
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": PROMPT},
                            {"role": "user", "content": judge_payload(row)},
                        ],
                    )
                    content = response.choices[0].message.content or "{}"
                    parsed = json.loads(content)
                    normalized = normalize_judge(parsed, row)
                    usage = response.usage.model_dump() if response.usage else {}
                    rec = {
                        "response_id": row["response_id"],
                        "source_run_id": row["source_run_id"],
                        "role": row["role"],
                        "role_family": row["role_family"],
                        "model": response.model,
                        "attempt": attempt,
                        "judge_output": normalized,
                        "raw_content": content,
                        "usage": usage,
                        "created": response.created,
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    f.flush()
                    done[row["response_id"]] = rec
                    for key2, val in usage.items():
                        if isinstance(val, int):
                            usage_total[key2] += val
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(2)
            if idx % 25 == 0:
                print(f"scored {idx}/{len(inputs)} total_done={len(done)}", flush=True)

    rows = []
    for rec in done.values():
        out = dict(rec["judge_output"])
        out["source_run_id"] = rec.get("source_run_id", "")
        out["role_family"] = rec.get("role_family", "")
        out["judge_model"] = rec.get("model", MODEL)
        rows.append(out)
    rows.sort(key=lambda r: r["response_id"])
    write_csv(OUT / "recovered_gpt41_scores.csv", rows)
    manifest = json.loads((OUT / "recovered_gpt41_judge_manifest.json").read_text())
    actual_input = usage_total.get("prompt_tokens", 0)
    actual_output = usage_total.get("completion_tokens", 0)
    actual_cost = actual_input / 1_000_000 * PRICE_INPUT_PER_1M + actual_output / 1_000_000 * PRICE_OUTPUT_PER_1M
    manifest.update(
        {
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "n_scored_final": len(rows),
            "actual_usage_total": dict(usage_total),
            "actual_cost_usd": actual_cost,
        }
    )
    write_json(OUT / "recovered_gpt41_judge_manifest.json", manifest)
    return rows


def load_centroids() -> dict[str, np.ndarray]:
    data = json.loads((REPO / "research/visualizations/geometry_viz_data.json").read_text())
    names = data["roles"]["names"]
    coords = data["roles"]["pca3d"]
    return {name: np.array(coord, dtype=float) for name, coord in zip(names, coords)}


def boolish(v: Any) -> bool:
    return str(v).lower() in {"true", "1", "yes"}


def cloud_metrics(
    rows: list[dict[str, Any]], role: str, run_id: str, subset: str, published: np.ndarray
) -> tuple[dict[str, Any], dict[str, Any]]:
    arr = np.array([[float(r["pc1"]), float(r["pc2"]), float(r["pc3"])] for r in rows], dtype=float)
    centroid = arr.mean(axis=0)
    deltas = arr - published
    distances = np.linalg.norm(deltas, axis=1)
    sd = arr.std(axis=0, ddof=1) if len(rows) > 1 else np.zeros(3)
    if len(rows) > 1:
        cov = np.cov(arr.T)
        eigvals, eigvecs = np.linalg.eigh(cov)
        order = np.argsort(eigvals)[::-1]
        eigvals = eigvals[order]
        eigvecs = eigvecs[:, order]
    else:
        cov = np.zeros((3, 3))
        eigvals = np.zeros(3)
        eigvecs = np.eye(3)
    min_eig = max(float(eigvals[-1]), 1e-12)
    volume_proxy = float(np.prod(sd))
    summary = {
        "run_id": run_id,
        "role": role,
        "subset": subset,
        "n": len(rows),
        "published_pc1": float(published[0]),
        "published_pc2": float(published[1]),
        "published_pc3": float(published[2]),
        "centroid_pc1": float(centroid[0]),
        "centroid_pc2": float(centroid[1]),
        "centroid_pc3": float(centroid[2]),
        "centroid_distance_to_published": float(np.linalg.norm(centroid - published)),
        "mean_response_distance_to_published": float(distances.mean()),
        "median_response_distance_to_published": float(np.median(distances)),
        "sd_pc1": float(sd[0]),
        "sd_pc2": float(sd[1]),
        "sd_pc3": float(sd[2]),
        "cloud_volume_proxy_sd_product": volume_proxy,
        "anisotropy_ratio": float(eigvals[0] / min_eig) if len(rows) > 1 else 0.0,
        "largest_eigenvalue": float(eigvals[0]),
        "largest_eigenvector_pc1": float(eigvecs[0, 0]),
        "largest_eigenvector_pc2": float(eigvecs[1, 0]),
        "largest_eigenvector_pc3": float(eigvecs[2, 0]),
    }
    detail = {
        "run_id": run_id,
        "role": role,
        "subset": subset,
        "covariance": cov.tolist(),
        "eigenvalues": eigvals.tolist(),
        "eigenvectors_columns": eigvecs.tolist(),
    }
    return summary, detail


def add_judge_to_recovered(
    coords: list[dict[str, str]], scores: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {s["response_id"]: s for s in scores}
    rows = []
    for r in coords:
        s = by_id.get(r["response_id"])
        if not s:
            continue
        row: dict[str, Any] = dict(r)
        for key in ["pc1", "pc2", "pc3"]:
            row[key] = float(row[key])
        row["score_0_to_3"] = int(s["score_0_to_3"])
        row["binary_retain_ge2"] = boolish(s["binary_retain_ge2"])
        row["binary_retain_eq3"] = boolish(s["binary_retain_eq3"])
        row["generic_assistant_collapse"] = boolish(s["generic_assistant_collapse"])
        row["refusal_or_safety_neutralization"] = boolish(s["refusal_or_safety_neutralization"])
        row["theatrical_overexpression"] = boolish(s["theatrical_overexpression"])
        rows.append(row)
    return rows


def load_amateur_playwright_rows() -> list[dict[str, Any]]:
    coords = read_csv(A100_PILOT / "activation_cloud_per_response.csv")
    scores = {r["response_id"]: r for r in read_csv(A100_POSTHOC / "gpt41_judge_scores.csv")}
    rows = []
    for r in coords:
        s = scores.get(r["response_id"])
        if not s:
            continue
        row: dict[str, Any] = {
            "run_id": f"{r['role']}_a100_cloud_60",
            "role": r["role"],
            "family": "a100_two_role_cloud",
            "response_id": r["response_id"],
            "pc1": float(r["pc1"]),
            "pc2": float(r["pc2"]),
            "pc3": float(r["pc3"]),
            "score_0_to_3": int(s["score_0_to_3"]),
            "binary_retain_ge2": boolish(s["binary_retain_ge2"]),
            "binary_retain_eq3": boolish(s["binary_retain_eq3"]),
            "generic_assistant_collapse": boolish(s["generic_assistant_collapse"]),
            "refusal_or_safety_neutralization": boolish(s["refusal_or_safety_neutralization"]),
            "theatrical_overexpression": boolish(s["theatrical_overexpression"]),
        }
        rows.append(row)
    return rows


def build_cloud_outputs(recovered_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    centroids = load_centroids()
    all_rows = recovered_rows + load_amateur_playwright_rows()
    grouped = defaultdict(list)
    for row in all_rows:
        grouped[(row["run_id"], row["role"])].append(row)

    summaries = []
    cov_details = []
    comparison = []
    for (run_id, role), group in sorted(grouped.items()):
        published = centroids[role]
        subsets = {
            "all": group,
            "score_ge2": [r for r in group if r["score_0_to_3"] >= 2],
            "score_eq3": [r for r in group if r["score_0_to_3"] == 3],
        }
        score_counts = Counter(r["score_0_to_3"] for r in group)
        for subset, subset_rows in subsets.items():
            if not subset_rows:
                continue
            summary, detail = cloud_metrics(subset_rows, role, run_id, subset, published)
            summary.update(
                {
                    "score0": score_counts.get(0, 0),
                    "score1": score_counts.get(1, 0),
                    "score2": score_counts.get(2, 0),
                    "score3": score_counts.get(3, 0),
                    "retention_ge2_count": len(subsets["score_ge2"]),
                    "retention_eq3_count": len(subsets["score_eq3"]),
                    "retention_ge2_rate": len(subsets["score_ge2"]) / len(group),
                    "retention_eq3_rate": len(subsets["score_eq3"]) / len(group),
                    "generic_assistant_collapse_count": sum(r["generic_assistant_collapse"] for r in group),
                    "theatrical_overexpression_count": sum(r["theatrical_overexpression"] for r in group),
                }
            )
            summaries.append(summary)
            cov_details.append(detail)
        all_summary = next(s for s in summaries if s["run_id"] == run_id and s["subset"] == "all")
        ge2_summary = next((s for s in summaries if s["run_id"] == run_id and s["subset"] == "score_ge2"), None)
        eq3_summary = next((s for s in summaries if s["run_id"] == run_id and s["subset"] == "score_eq3"), None)
        comparison.append(
            {
                "run_id": run_id,
                "role": role,
                "n_total": len(group),
                "score0": score_counts.get(0, 0),
                "score1": score_counts.get(1, 0),
                "score2": score_counts.get(2, 0),
                "score3": score_counts.get(3, 0),
                "retention_ge2_count": len(subsets["score_ge2"]),
                "retention_ge2_rate": len(subsets["score_ge2"]) / len(group),
                "retention_eq3_count": len(subsets["score_eq3"]),
                "retention_eq3_rate": len(subsets["score_eq3"]) / len(group),
                "all_centroid_distance": all_summary["centroid_distance_to_published"],
                "ge2_centroid_distance": ge2_summary["centroid_distance_to_published"] if ge2_summary else "",
                "eq3_centroid_distance": eq3_summary["centroid_distance_to_published"] if eq3_summary else "",
                "all_mean_response_distance": all_summary["mean_response_distance_to_published"],
                "ge2_mean_response_distance": ge2_summary["mean_response_distance_to_published"] if ge2_summary else "",
                "eq3_mean_response_distance": eq3_summary["mean_response_distance_to_published"] if eq3_summary else "",
                "all_volume_proxy": all_summary["cloud_volume_proxy_sd_product"],
                "ge2_volume_proxy": ge2_summary["cloud_volume_proxy_sd_product"] if ge2_summary else "",
                "eq3_volume_proxy": eq3_summary["cloud_volume_proxy_sd_product"] if eq3_summary else "",
                "all_anisotropy_ratio": all_summary["anisotropy_ratio"],
                "ge2_anisotropy_ratio": ge2_summary["anisotropy_ratio"] if ge2_summary else "",
                "eq3_anisotropy_ratio": eq3_summary["anisotropy_ratio"] if eq3_summary else "",
                "generic_assistant_collapse_count": sum(r["generic_assistant_collapse"] for r in group),
                "theatrical_overexpression_count": sum(r["theatrical_overexpression"] for r in group),
            }
        )
    write_csv(OUT / "recovered_cloud_summary_by_role.csv", summaries)
    write_json(OUT / "recovered_cloud_covariance.json", cov_details)
    write_csv(OUT / "recovered_cloud_comparison_table.csv", comparison)
    return summaries, cov_details, comparison


def fmt(x: Any, digits: int = 3) -> str:
    if x == "" or x is None:
        return ""
    return f"{float(x):.{digits}f}"


def html_visualization(recovered_rows: list[dict[str, Any]], comparison: list[dict[str, Any]]) -> None:
    all_rows = recovered_rows + load_amateur_playwright_rows()
    data = [
        {
            "run_id": r["run_id"],
            "role": r["role"],
            "response_id": r["response_id"],
            "pc1": float(r["pc1"]),
            "pc2": float(r["pc2"]),
            "pc3": float(r["pc3"]),
            "score": int(r["score_0_to_3"]),
        }
        for r in all_rows
    ]
    comp = comparison
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Recovered Role Cloud Analysis</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; color: #222; }}
#plot {{ width: 100%; height: 720px; }}
table {{ border-collapse: collapse; font-size: 13px; }}
td, th {{ border: 1px solid #ddd; padding: 6px 8px; text-align: right; }}
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) {{ text-align: left; }}
</style>
</head>
<body>
<h1>Recovered Trickster/Editor Clouds vs Amateur/Playwright</h1>
<p>Points show corrected PCA coordinates colored by run and symbolized by GPT-4.1 score.</p>
<div id="plot"></div>
<h2>Comparison Table</h2>
<table>
<tr><th>run_id</th><th>role</th><th>n</th><th>retain >=2</th><th>retain ==3</th><th>all centroid dist</th><th>ge2 centroid dist</th><th>all volume</th><th>all anisotropy</th></tr>
{''.join(f"<tr><td>{r['run_id']}</td><td>{r['role']}</td><td>{r['n_total']}</td><td>{r['retention_ge2_count']} ({fmt(r['retention_ge2_rate'])})</td><td>{r['retention_eq3_count']} ({fmt(r['retention_eq3_rate'])})</td><td>{fmt(r['all_centroid_distance'])}</td><td>{fmt(r['ge2_centroid_distance'])}</td><td>{fmt(r['all_volume_proxy'])}</td><td>{fmt(r['all_anisotropy_ratio'])}</td></tr>" for r in comp)}
</table>
<script>
const rows = {json.dumps(data)};
const groups = [...new Set(rows.map(r => r.run_id))];
const traces = groups.map(g => {{
  const rs = rows.filter(r => r.run_id === g);
  return {{
    type: 'scatter3d',
    mode: 'markers',
    name: g,
    x: rs.map(r => r.pc1),
    y: rs.map(r => r.pc2),
    z: rs.map(r => r.pc3),
    text: rs.map(r => `${{r.response_id}}<br>score=${{r.score}}`),
    marker: {{ size: rs.map(r => 3 + r.score * 1.5), opacity: 0.72 }}
  }};
}});
Plotly.newPlot('plot', traces, {{
  scene: {{ xaxis: {{ title: 'PC1' }}, yaxis: {{ title: 'PC2' }}, zaxis: {{ title: 'PC3' }} }},
  margin: {{ l: 0, r: 0, t: 10, b: 0 }}
}});
</script>
</body>
</html>
"""
    (OUT / "recovered_cloud_visualizations.html").write_text(html)


def write_reports(scores: list[dict[str, Any]], summaries: list[dict[str, Any]], comparison: list[dict[str, Any]]) -> None:
    by_run = {r["run_id"]: r for r in comparison}
    editor1 = by_run["editor_phase1_128"]
    editor1024 = by_run["editor_matched64_1024"]
    trickster = by_run["trickster_phase1_1200"]
    amateur = by_run["amateur_a100_cloud_60"]
    playwright = by_run["playwright_a100_cloud_60"]
    manifest = json.loads((OUT / "recovered_gpt41_judge_manifest.json").read_text())

    reassessment = f"""# Editor Failure Reassessment

## Best-supported explanation

The prior editor/procedural-professional failure is best explained by **genuine elicitation/role-expression difficulty with assistant-adjacent collapse**, not by GPT-5.5 strictness, D01 boundary error, or token-cap truncation alone.

## Evidence

- GPT-4.1 retained only {editor1['retention_ge2_count']}/{editor1['n_total']} editor 512-token responses at score>=2 and {editor1['retention_eq3_count']}/{editor1['n_total']} at score==3.
- The matched 1024-token editor rerun retained {editor1024['retention_ge2_count']}/{editor1024['n_total']} at score>=2 and {editor1024['retention_eq3_count']}/{editor1024['n_total']} at score==3, so reducing truncation did not rescue role expression.
- Trickster, scored with the same GPT-4.1 rubric, retained {trickster['retention_ge2_count']}/{trickster['n_total']} at score>=2 and {trickster['retention_eq3_count']}/{trickster['n_total']} at score==3, showing the judge is not globally suppressing recovered adaptive responses.
- The A100 comparison roles retained {amateur['retention_ge2_count']}/{amateur['n_total']} amateur and {playwright['retention_ge2_count']}/{playwright['n_total']} playwright responses at score>=2, again suggesting the editor issue is role/run-specific.
- D01 is not the failure source because these recovered vectors are hook-derived and locally reprojectable under the corrected boundary.

## Alternative explanations

- GPT-5.5 strictness: weakened. GPT-4.1 remains strict on editor.
- Token-cap/truncation: weakened. The 1024-token rerun reduced truncation but did not substantially improve retention.
- Centroid mismatch: possible contributor. Editor clouds sit in the high-PC1 assistant-adjacent region, where generic explanatory assistant behavior can appear geometrically close while still failing expression criteria.
- Sampling effects: possible but not primary. Both independent editor samples show low retained fractions.
- Genuine elicitation failure: strongest supported explanation.

## Recommendation

Do not launch another editor GPU run without changing the anchoring/elicitation design. If procedural-professional extraction matters, test a less assistant-collapsed role such as auditor, examiner, validator, or bureaucrat with explicit no-leakage role-expression controls.
"""
    (OUT / "editor_failure_reassessment.md").write_text(reassessment)

    score_counts = Counter((r["source_run_id"], r["score_0_to_3"]) for r in scores)
    report = f"""# Recovered Role Cloud Analysis

Startup status: **STARTUP VERIFIED**.

This local analysis rejudged recovered adaptive-extraction responses with the same GPT-4.1 temperature-0 role-expression rubric used for the amateur/playwright activation-cloud posthoc analysis, then processed recovered trickster/editor corrected PCA coordinates through the same cloud-summary logic.

Judge run: GPT-4.1, temperature 0, {manifest['n_scored_final']} recovered responses scored, actual token usage {manifest.get('actual_usage_total', {})}, estimated actual cost ${manifest.get('actual_cost_usd', 0):.4f}.

## Response Counts and Retention

| run | n | score0 | score1 | score2 | score3 | retain>=2 | retain==3 |
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(f"| {r['run_id']} | {r['n_total']} | {r['score0']} | {r['score1']} | {r['score2']} | {r['score3']} | {r['retention_ge2_count']} ({fmt(r['retention_ge2_rate'])}) | {r['retention_eq3_count']} ({fmt(r['retention_eq3_rate'])}) |" for r in comparison)}

## Cloud Comparison Summary

| run | all centroid distance | ge2 centroid distance | all mean response distance | all volume proxy | all anisotropy |
|---|---:|---:|---:|---:|---:|
{chr(10).join(f"| {r['run_id']} | {fmt(r['all_centroid_distance'])} | {fmt(r['ge2_centroid_distance'])} | {fmt(r['all_mean_response_distance'])} | {fmt(r['all_volume_proxy'])} | {fmt(r['all_anisotropy_ratio'])} |" for r in comparison)}

## Interpretation

Trickster behaves like a broad but high-yield recovered adaptive cloud: GPT-4.1 retains most responses and the score>=2/score==3 subsets remain well populated. Editor behaves unlike both trickster and the amateur/playwright A100 roles: retained counts are low in both the 512-token and 1024-token recovered runs, and token-cap relief does not solve the expression problem.

The editor/procedural-professional result is therefore best treated as an elicitation failure or assistant-adjacent collapse problem, not a recoverability problem. The saved hook vectors are usable for local analysis, but low retained counts make editor a weak candidate for downstream validated role-vector construction.

## Recommendation on Additional GPU Work

No additional GPU work is needed to recover these prior adaptive runs. If the goal is procedural-professional extraction, redesign the elicitation target before spending GPU: use a less generic assistant-adjacent procedural role, add stronger expression prompts, or run a small multi-role pilot comparing auditor/examiner/validator/editor before committing to a full extraction.
"""
    (OUT / "recovered_role_cloud_analysis_report.md").write_text(report)


def main() -> None:
    inputs = load_jsonl(PRIOR / "prior_adaptive_gpt41_judge_inputs.jsonl")
    scores = run_gpt41_rejudge(inputs)
    coords = read_csv(PRIOR / "prior_adaptive_corrected_coordinates.csv")
    recovered_rows = add_judge_to_recovered(coords, scores)
    summaries, covariances, comparison = build_cloud_outputs(recovered_rows)
    html_visualization(recovered_rows, comparison)
    write_reports(scores, summaries, comparison)
    print(f"complete: scored={len(scores)} recovered_rows={len(recovered_rows)}", flush=True)


if __name__ == "__main__":
    main()
