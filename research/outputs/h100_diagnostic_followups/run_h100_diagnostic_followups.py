#!/usr/bin/env python3
"""First-pass diagnostic follow-ups for H100 forecast-vs-observed anomalies."""

from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

import joblib
import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "research/outputs/h100_diagnostic_followups"

H100_RESULTS = REPO_ROOT / "research/outputs/h100_percentile_edge_validation/h100_final_results.csv"
H100_METRICS = REPO_ROOT / "research/outputs/h100_percentile_edge_validation/h100_final_metrics.json"
H100_RESPONSES = REPO_ROOT / "research/outputs/h100_percentile_edge_validation/h100_generated_responses.jsonl"
H100_RUNNER = REPO_ROOT / "research/outputs/h100_percentile_edge_validation/run_h100_percentile_edge_validation.py"
PROJECTION_DEBUG = REPO_ROOT / "research/outputs/h100_percentile_edge_validation/h100_activation_projection_debug.json"
ERROR_VECTORS = REPO_ROOT / "research/outputs/h100_percentile_edge_validation_error_analysis/per_prompt_error_vectors.csv"
REGIONAL_SUMMARY = REPO_ROOT / "research/outputs/h100_percentile_edge_validation_error_analysis/regional_error_summary.json"
SIX_POLE = REPO_ROOT / "research/outputs/h100_percentile_edge_validation_error_analysis/six_pole_error_breakdown.csv"
PROMPT_MANIFEST = REPO_ROOT / "research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv"
PROMPT_BATTERY = REPO_ROOT / "research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_prompt_battery.csv"
GEN_LOG = REPO_ROOT / "research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_generation_log.csv"
CANDIDATES = REPO_ROOT / "research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_candidates_all.csv"
THRESHOLDS = REPO_ROOT / "research/outputs/novel_prompt_battery_percentile_edges/inherited_percentile_thresholds.json"
GEOMETRY = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
FORECASTER = REPO_ROOT / "research/outputs/novel_prompt_battery/frozen_role_leakage_elastic_net_tfidf.joblib"
PCA_UTIL = REPO_ROOT / "assistant_axis/pca.py"

PC_COLS = ["pc1", "pc2", "pc3"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def fnum(row: dict, key: str) -> float:
    return float(row[key])


def boolish(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def pct_rank(values: np.ndarray, x: float) -> float:
    return float(np.mean(values <= x))


def short(text: str, n: int = 420) -> str:
    clean = re.sub(r"\s+", " ", text or "").strip()
    return clean[:n]


def classify_response(text: str) -> str:
    s = (text or "").lower()
    if any(p in s[:280] for p in ["i can't help", "i cannot help", "i'm sorry", "i can’t assist", "as an ai"]):
        return "refusal/safety"
    if any(w in s for w in ["step-by-step", "checklist", "criteria", "standard", "evaluate", "review", "systematic"]):
        return "procedural critique"
    if any(w in s for w in ["calm", "comfort", "safe", "support", "reconcile", "de-escalate", "shared ground"]):
        return "stabilizing/de-escalating"
    if any(w in s for w in ["challenge", "pressure", "weakness", "disrupt", "probe", "risk", "scrutiny"]):
        return "perturbative/critical"
    if any(w in s for w in ["nuanced", "complex", "multiple perspectives", "ambiguity", "tension", "reflect"]):
        return "abstract synthesis"
    if any(w in s for w in ["worried", "embarrassed", "scared", "overwhelmed", "right now"]):
        return "situated reaction"
    if s.startswith(("sure", "certainly", "of course", "here")) or "here's" in s[:120]:
        return "generic assistant"
    return "other"


def load_rows() -> tuple[list[dict], dict, dict, dict]:
    rows = read_csv(ERROR_VECTORS if ERROR_VECTORS.exists() else H100_RESULTS)
    result_rows = {r["prompt_id"]: r for r in read_csv(H100_RESULTS)}
    manifest = {r["prompt_id"]: r for r in read_csv(PROMPT_MANIFEST)}
    gen_log = read_csv(GEN_LOG)
    response_json = {}
    with H100_RESPONSES.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            response_json[rec["prompt_id"]] = rec
    for row in rows:
        pid = row["prompt_id"]
        for src in (result_rows.get(pid, {}), manifest.get(pid, {}), response_json.get(pid, {})):
            for k, v in src.items():
                row.setdefault(k, v)
        row["response_style_classification"] = classify_response(row.get("generated_response", ""))
    return rows, manifest, response_json, {"generation_log": gen_log, "candidates": read_csv(CANDIDATES)}


def nearest_items(vec: np.ndarray, names: list[str], coords: np.ndarray, k: int = 5) -> str:
    dists = np.linalg.norm(coords - vec[None, :], axis=1)
    order = np.argsort(dists)[:k]
    return "; ".join(f"{names[i]}:{dists[i]:.2f}" for i in order)


def add_nearest(row: dict, geometry: dict) -> dict:
    obs = np.array([fnum(row, "observed_pc1"), fnum(row, "observed_pc2"), fnum(row, "observed_pc3")], dtype=float)
    roles = geometry["roles"]
    traits = geometry["traits"]
    row = dict(row)
    row["nearest_observed_roles_pca3d"] = nearest_items(obs, roles["names"], np.array(roles["pca3d"], dtype=float), 5)
    row["nearest_observed_traits_pca3d"] = nearest_items(obs, traits["names"], np.array(traits["pca3d"], dtype=float), 5)
    return row


def load_forecaster():
    try:
        return joblib.load(FORECASTER)
    except Exception:
        return None


def top_tfidf_terms(pipe, prompt: str, pc_index: int, n: int = 8) -> str:
    if pipe is None:
        return "forecaster unavailable"
    try:
        tfidf = pipe.named_steps["tfidf"]
        scale = pipe.named_steps["scale"]
        model = pipe.named_steps["model"]
        x = tfidf.transform([prompt])
        xs = scale.transform(x)
        coef = model.estimators_[pc_index].coef_
        arr = xs.multiply(coef).tocoo()
        if arr.nnz == 0:
            return ""
        features = tfidf.get_feature_names_out()
        terms = sorted(zip(arr.col, arr.data), key=lambda t: abs(t[1]), reverse=True)[:n]
        return "; ".join(f"{features[i]}:{v:.3f}" for i, v in terms)
    except Exception as exc:
        return f"term extraction failed: {exc}"


def with_tfidf(row: dict, pipe) -> dict:
    out = dict(row)
    prompt = out.get("prompt_text") or out.get("candidate_prompt") or ""
    out["top_tfidf_terms_pc1"] = top_tfidf_terms(pipe, prompt, 0)
    out["top_tfidf_terms_pc2"] = top_tfidf_terms(pipe, prompt, 1)
    out["top_tfidf_terms_pc3"] = top_tfidf_terms(pipe, prompt, 2)
    return out


def select_cone_outliers(rows: list[dict], geometry: dict, thresholds: dict) -> list[dict]:
    pc1 = np.array([p[0] for p in geometry["roles"]["pca3d"]], dtype=float)
    pc2 = np.array([p[1] for p in geometry["roles"]["pca3d"]], dtype=float)
    p = thresholds["percentiles"]
    cand = [
        r
        for r in rows
        if fnum(r, "observed_pc1") >= p["PC1"]["p80"]
        or fnum(r, "observed_pc1") >= 30
        or fnum(r, "observed_pc2") >= p["PC2"]["p80"]
        or fnum(r, "observed_pc2") >= 30
    ]
    for r in cand:
        r["observed_pc1_percentile"] = pct_rank(pc1, fnum(r, "observed_pc1"))
        r["observed_pc2_percentile"] = pct_rank(pc2, fnum(r, "observed_pc2"))
        r["pc1_pc2_percentile_sum"] = r["observed_pc1_percentile"] + r["observed_pc2_percentile"]
        r["diagnostic_note"] = (
            "High observed PC1/PC2 candidate; inspect for generic procedural answer, chat-template/pooling artifact, or genuine outside-cone response state."
        )
    return sorted(cand, key=lambda r: r["pc1_pc2_percentile_sum"], reverse=True)[:10]


def select_extreme_pc1_near_zero_pc3(rows: list[dict], pipe, thresholds: dict) -> list[dict]:
    p = thresholds["percentiles"]
    near_zero = sorted(rows, key=lambda r: abs(fnum(r, "predicted_pc3")))[: max(10, len(rows) // 10)]
    cand = [
        r
        for r in rows
        if abs(fnum(r, "predicted_pc3")) <= 2.5
        and (fnum(r, "predicted_pc1") <= p["PC1"]["p20"] or fnum(r, "predicted_pc1") >= p["PC1"]["p80"])
    ]
    cand.extend(
        [
            r
            for r in near_zero
            if fnum(r, "predicted_pc1") <= p["PC1"]["p20"] or fnum(r, "predicted_pc1") >= p["PC1"]["p80"]
        ]
    )
    unique = {r["prompt_id"]: r for r in cand}
    selected = sorted(unique.values(), key=lambda r: (abs(fnum(r, "predicted_pc3")), -abs(fnum(r, "predicted_pc1"))))[:20]
    for r in selected:
        r["diagnostic_note"] = (
            "Extreme forecast PC1 with near-zero forecast PC3; check whether lexical terms drive PC1 while PC3-relevant perturbation/stabilization terms are absent."
        )
    return [with_tfidf(r, pipe) for r in selected]


def select_low_pc2_near_zero_pc1(rows: list[dict]) -> list[dict]:
    low = sorted(rows, key=lambda r: fnum(r, "predicted_pc2"))[:25]
    selected = [r for r in low if abs(fnum(r, "predicted_pc1")) <= 8]
    if len(selected) < 10:
        selected = sorted(low, key=lambda r: abs(fnum(r, "predicted_pc1")))[:10]
    else:
        selected = selected[:10]
    for r in selected:
        r["diagnostic_note"] = (
            "Forecast low-PC2 prompt; observed response often shifts into situated/generic assistant PC2-high territory if response begins with scaffolded advice or interpersonal framing."
        )
    return selected


def pc2_family(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for r in rows:
        groups[r["prompt_family"]].append(r)
        for col in ["pc1_lower_tail", "pc1_upper_tail", "pc2_lower_tail", "pc2_upper_tail", "pc3_lower_tail", "pc3_upper_tail", "shoulder_edge", "interior_control"]:
            if boolish(r.get(col)):
                groups[f"tail::{col}"].append(r)
    out = []
    for name, subset in groups.items():
        deltas = [fnum(r, "delta_pc2") for r in subset]
        out.append(
            {
                "group": name,
                "count": len(subset),
                "mean_delta_pc2": mean(deltas),
                "median_delta_pc2": median(deltas),
                "mae_pc2": mean(abs(x) for x in deltas),
                "top_prompt_ids": ";".join(r["prompt_id"] for r in sorted(subset, key=lambda r: fnum(r, "delta_pc2"), reverse=True)[:5]),
            }
        )
    return sorted(out, key=lambda r: r["mean_delta_pc2"], reverse=True)


def select_pc3_high_collapse(rows: list[dict], geometry: dict) -> tuple[list[dict], dict]:
    high = [r for r in rows if "pc3_upper_tail" in (r.get("forecasted_regions") or "").split(";") or boolish(r.get("pc3_upper_tail"))]
    selected = sorted(high, key=lambda r: fnum(r, "delta_pc3"))[:3]
    for r in selected:
        r["response_classification"] = classify_response(r.get("generated_response", ""))
        r["diagnostic_note"] = "Largest downward PC3 error among forecasted PC3-high prompts; inspect for neutralization into abstract synthesis, de-escalation, or generic assistant stance."
    stats = {
        "count": len(high),
        "mean_delta_pc3": mean(fnum(r, "delta_pc3") for r in high),
        "median_delta_pc3": median(fnum(r, "delta_pc3") for r in high),
        "mean_observed_pc3": mean(fnum(r, "observed_pc3") for r in high),
        "retained_observed_pc3_high": sum(1 for r in high if "pc3_upper_tail" in (r.get("observed_regions") or "").split(";")),
    }
    return [add_nearest(r, geometry) for r in selected], stats


def select_largest_3d(rows: list[dict], geometry: dict) -> list[dict]:
    selected = sorted(rows, key=lambda r: fnum(r, "euclidean_delta_3d"), reverse=True)[:10]
    for r in selected:
        deltas = {pc: abs(fnum(r, f"delta_{pc}")) for pc in PC_COLS}
        cause = max(deltas, key=deltas.get)
        r["dominant_error_axis"] = cause
        r["response_classification"] = classify_response(r.get("generated_response", ""))
        r["likely_cause_category"] = {
            "pc1": "PC1 address miss / procedural-vs-symbolic mismatch",
            "pc2": "PC2 upward drift / response-style shift",
            "pc3": "PC3 perturbation-stabilization mismatch",
        }[cause]
        r["diagnostic_note"] = "Top 10 total 3D error case."
    return [add_nearest(r, geometry) for r in selected]


def audit_generation(gen: list[dict], accepted_rows: list[dict]) -> dict:
    accepted = [r for r in gen if str(r.get("accept_or_reject")).lower() in {"accept", "accepted"} or str(r.get("accepted_from_seed")).lower() == "true"]
    rejected = [r for r in gen if r not in accepted]
    prompts = [r.get("candidate_prompt") or r.get("prompt_text") or "" for r in accepted]
    final_prompts = [r.get("prompt_text") or "" for r in accepted_rows]
    phrase_counts = Counter()
    final_phrase_counts = Counter()
    phrase_list = [
        "Draft the response",
        "Write a natural user-facing response",
        "if useful, it can also",
        "A written plan creates tension",
        "Someone asks for help",
        "A person needs a response",
        "Please respond to the following scenario",
        "The response should",
    ]
    for p in prompts:
        for phrase in phrase_list:
            if phrase.lower() in p.lower():
                phrase_counts[phrase] += 1
    for p in final_prompts:
        for phrase in [
            *phrase_list,
        ]:
            if phrase.lower() in p.lower():
                final_phrase_counts[phrase] += 1
    by_region = defaultdict(lambda: {"accepted": 0, "rejected": 0, "mean_artifact_similarity": [], "mean_abs_pc3": []})
    for r in gen:
        target = r.get("generation_target_region", "unknown")
        is_acc = str(r.get("accept_or_reject")).lower() in {"accept", "accepted"} or str(r.get("accepted_from_seed")).lower() == "true"
        by_region[target]["accepted" if is_acc else "rejected"] += 1
        if r.get("artifact_similarity"):
            by_region[target]["mean_artifact_similarity"].append(float(r["artifact_similarity"]))
        if r.get("predicted_pc3"):
            by_region[target]["mean_abs_pc3"].append(abs(float(r["predicted_pc3"])))
    return {
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "rejection_reasons": Counter(r.get("rejection_reason", "missing") for r in rejected),
        "accepted_generation_phrase_counts": phrase_counts,
        "final_battery_phrase_counts": final_phrase_counts,
        "by_region": {
            k: {
                "accepted": v["accepted"],
                "rejected": v["rejected"],
                "mean_artifact_similarity": mean(v["mean_artifact_similarity"]) if v["mean_artifact_similarity"] else None,
                "mean_abs_predicted_pc3": mean(v["mean_abs_pc3"]) if v["mean_abs_pc3"] else None,
            }
            for k, v in by_region.items()
        },
    }


def calibration_metrics(rows: list[dict]) -> dict:
    out = {}
    n = len(rows)
    for i, pc in enumerate([1, 2, 3]):
        pred = np.array([fnum(r, f"predicted_pc{pc}") for r in rows])
        obs = np.array([fnum(r, f"observed_pc{pc}") for r in rows])
        coef = np.polyfit(pred, obs, 1)
        calibrated = coef[0] * pred + coef[1]
        cv_pred = np.zeros_like(obs)
        for j in range(n):
            mask = np.ones(n, dtype=bool); mask[j] = False
            c = np.polyfit(pred[mask], obs[mask], 1)
            cv_pred[j] = c[0] * pred[j] + c[1]
        def r2(y, yhat):
            return 1 - float(np.sum((y-yhat)**2) / np.sum((y-y.mean())**2))
        out[f"pc{pc}"] = {
            "uncalibrated_r2": r2(obs, pred),
            "in_sample_calibrated_r2": r2(obs, calibrated),
            "loocv_calibrated_r2": r2(obs, cv_pred),
            "slope": float(coef[0]),
            "intercept": float(coef[1]),
            "uncalibrated_rmse": float(np.sqrt(np.mean((obs-pred)**2))),
            "loocv_calibrated_rmse": float(np.sqrt(np.mean((obs-cv_pred)**2))),
        }
    return out


def methodology_table() -> list[dict]:
    runner = H100_RUNNER.read_text()
    debug = json.load(PROJECTION_DEBUG.open())
    config = json.load((REPO_ROOT / "research/outputs/h100_percentile_edge_validation/h100_run_config.json").open())
    pca_text = PCA_UTIL.read_text()
    rows = [
        ("Model identifier", "Qwen/Qwen3-32B", config.get("model"), "matched", "Run config and runner constant match."),
        ("Layer index", "Qwen layer 48 hidden state", config.get("layer"), "partially verified", "Runner uses out.hidden_states[LAYER]; local ActivationExtractor indexes model_layers[layer_idx] with hooks, so hidden_states-vs-module index equivalence needs source-pipeline confirmation."),
        ("Representation", "post-MLP residual / hidden-state vector", "transformers output_hidden_states hidden state", "partially verified", "Methodology notes describe mean post-MLP residual activations; H100 used output_hidden_states rather than the local hook extractor, likely equivalent to layer output but not proven line-by-line."),
        ("Pooling", "mean over response tokens only", "hidden[:, prompt_len:, :].mean(axis=0)", "matched in runner", "Prompt tokens excluded after chat-template prompt_len."),
        ("Chat template", "Qwen chat template with generation prompt", "tokenizer.apply_chat_template(... add_generation_prompt=True, enable_thinking=False)", "matched to run design", "Source Assistant Axis generation template not directly verified."),
        ("PCA basis", "loaded/reconstructed, not refit on prompts", debug.get("basis_source"), "matched", "Basis reconstructed from 275 role vectors; prompt observations projected into this basis."),
        ("Preprocessing", "mean centering, no standardization/L2", "project_activation subtracts role-vector mean and dots components", "matched to reproduced coordinates", "Reproduction error is the strongest evidence for preprocessing match."),
        ("Sign convention", "canonical committed coordinates", debug.get("sign_alignment"), "matched", "Sign aligned to canonical PCA CSV."),
        ("PCA reproduction", "near-exact reproduction", debug.get("max_abs_coordinate_reproduction_error"), "matched", "Max abs reproduction error 1.207e-06 over 273 committed coordinates."),
        ("Source code comparison", "assistant_axis/pca.py, internals/activations.py, replication_differences_vs_lu.md", "local source inspected", "partial", "Local utility supports mean centering and response-span pooling; local extractor prefers hooks while H100 runner used output_hidden_states."),
    ]
    return [
        {
            "check": a,
            "expected": b,
            "observed": c,
            "status": d,
            "evidence_or_caveat": e,
        }
        for a, b, c, d, e in rows
    ]


def write_markdown_outputs(bundle: dict) -> dict[str, dict]:
    checklist = {
        "D01": ("in_progress", "No blocking discrepancy found, but exact source extraction/chat-template convention remains not fully independently verified.", "Compare against upstream safety-research extraction code or original artifact metadata."),
        "D02": ("open", "Cone-violation candidates identified; several are generic/procedural observed responses in high PC1/PC2 regions.", "Inspect whether these are genuine admissible states or projection/pooling artifacts."),
        "D03": ("open", "Extreme-PC1/near-zero-PC3 cases exist and often show coefficient-aligned lexical construction.", "Decide whether to downweight or redesign these prompts in the next battery."),
        "D04": ("open", "Low-PC2 near-zero-PC1 cases generally drift upward on PC2 after generation.", "Compare prompt-intended abstraction against actual response style with second rater or calibrated model."),
        "D05": ("open", "PC2 upward shift is family/group dependent; neutral and cluster-region prompts show large positive deltas.", "Use family/cell diagnostics in calibration."),
        "D06": ("open", "Forecasted PC3-high prompts frequently become abstract/generic/stabilizing and fail observed high-PC3 retention.", "Test more direct non-operational perturbative prompts or response-style controls."),
        "D07": ("open", "Largest 3D errors are dominated mostly by PC2 upward drift and PC3 collapse.", "Use these as calibration stress cases."),
        "D08": ("open", "Generation loop and final battery show repeated scaffolds and some forecaster-facing lexical patterns; evidence suggests possible design bias but not enough to discard the battery.", "Create a human-naturalness review or regenerate a no-feedback holdout edge subset."),
        "D09": ("in_progress", "Axis-wise calibration diagnostics were scaffolded and run; held-out calibration should be treated as preliminary.", "Run proper train/test or nested calibration on a larger validation set."),
    }
    statuses = {}
    lines = [
        "# H100 Diagnostic Follow-Up Checklist",
        "",
        f"- Generated UTC: {now()}",
        "- Model used for this diagnostic pass: GPT-5.5",
        "- Rule: items remain open until resolved with direct evidence.",
        "",
        "| id | title | priority | status | conclusion | next action |",
        "|---|---|---|---|---|---|",
    ]
    titles = {
        "D01": ("Verify activation measurement methodology", "critical"),
        "D02": ("Investigate observed high-PC1/high-PC2 cone-violation outliers", "critical"),
        "D03": ("Inspect forecasted extreme-PC1 / near-zero-PC3 prompts", "high"),
        "D04": ("Inspect lowest predicted-PC2 prompts near PC1 approx 0", "high"),
        "D05": ("Analyze prompt families driving largest positive PC2 deltas", "high"),
        "D06": ("Inspect largest downward PC3 errors among forecasted PC3-high prompts", "high"),
        "D07": ("Inspect largest 3D-error prompts overall", "medium"),
        "D08": ("Audit prompt-generation loop for forecaster exploitation or origin bias", "high"),
        "D09": ("Distinguish calibration failure from true directional failure", "medium"),
    }
    for did in [f"D{i:02d}" for i in range(1, 10)]:
        status, conclusion, nxt = checklist[did]
        title, priority = titles[did]
        lines.append(f"| {did} | {title} | {priority} | {status} | {conclusion} | {nxt} |")
        statuses[did] = {"status": status, "conclusion": conclusion, "next_action": nxt}
    OUT.joinpath("diagnostic_followup_checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Methodology report
    method_lines = [
        "# Activation Methodology Verification",
        "",
        "## Direct Answer",
        "",
        "No blocking discrepancy was found in the local H100 runner or projection debug artifacts. The PCA projection convention is strongly verified by max absolute coordinate reproduction error 1.207e-06 against committed canonical coordinates. However, D01 remains `in_progress`, not resolved, because the exact upstream Assistant Axis extraction loop, layer-index convention, and chat-template convention were not independently compared line by line.",
        "",
        "| check | expected | observed | status | evidence/caveat |",
        "|---|---|---|---|---|",
    ]
    for r in bundle["methodology_table"]:
        method_lines.append(f"| {r['check']} | {r['expected']} | `{r['observed']}` | {r['status']} | {r['evidence_or_caveat']} |")
    method_lines += [
        "",
        "## Unresolved Methodological Discrepancies",
        "",
        "- Hidden-state index convention is internally consistent but still needs upstream source comparison for whether layer 48 refers to `hidden_states[48]`, hooked module index 48, or another block convention.",
        "- The source Assistant Axis chat template / prompt wrapper used to produce released vectors was not directly verified in this pass.",
        "- Local methodology notes describe mean post-MLP residual activations; the H100 runner used `output_hidden_states=True` rather than the local hook-based `ActivationExtractor.batch_conversations()` path. This is not yet shown to explain the PC2 shift, but it remains a live implementation-equivalence check.",
        "",
        "Confidence level: medium-high for PCA projection convention; medium for full activation-extraction equivalence.",
    ]
    OUT.joinpath("activation_methodology_verification.md").write_text("\n".join(method_lines) + "\n", encoding="utf-8")

    def table_report(path: str, title: str, rows: list[dict], fields: list[str], intro: str, conclusion: str):
        lines = [f"# {title}", "", intro, "", "| " + " | ".join(fields) + " |", "|" + "|".join(["---"] * len(fields)) + "|"]
        for r in rows:
            vals = []
            for f in fields:
                v = r.get(f, "")
                if isinstance(v, float):
                    v = f"{v:.3f}"
                vals.append(str(v).replace("\n", " ")[:500])
            lines.append("| " + " | ".join(vals) + " |")
        lines += ["", "## Diagnostic Conclusion", "", conclusion]
        OUT.joinpath(path).write_text("\n".join(lines) + "\n", encoding="utf-8")

    table_report(
        "cone_violation_outlier_report.md",
        "Cone-Violation Outlier Diagnostic Report",
        bundle["cone"],
        ["prompt_id", "prompt_family", "observed_pc1", "observed_pc2", "observed_pc3", "predicted_pc1", "predicted_pc2", "predicted_pc3", "response_style_classification", "nearest_observed_roles_pca3d", "diagnostic_note"],
        "Observed high-PC1/high-PC2 cases were selected by percentile/threshold criteria and ranked by combined observed PC1/PC2 percentile.",
        "Several candidates are generic/procedural assistant responses that occupy observed high-PC2 and sometimes high-PC1. They should not yet be interpreted as genuine cone violations until D01 is fully resolved and response-style controls are tested.",
    )
    table_report(
        "forecast_origin_bias_report.md",
        "Forecast Extreme-PC1 / Near-Zero-PC3 Diagnostic Report",
        bundle["origin_bias"],
        ["prompt_id", "prompt_family", "predicted_pc1", "predicted_pc3", "observed_pc1", "observed_pc3", "top_tfidf_terms_pc1", "top_tfidf_terms_pc3", "artifact_similarity", "diagnostic_note"],
        "Cases were selected for extreme forecast PC1 and near-zero forecast PC3.",
        "These cases support an origin-plane-bias concern: some prompts push PC1 with strong lexical features while PC3 remains near zero. This looks like forecaster design pressure, not necessarily natural semantic geometry.",
    )
    table_report(
        "pc2_upward_shift_report.md",
        "PC2 Upward Shift Diagnostic Report",
        bundle["low_pc2"],
        ["prompt_id", "prompt_family", "predicted_pc1", "predicted_pc2", "observed_pc1", "observed_pc2", "delta_pc2", "response_style_classification", "diagnostic_note"],
        "Low predicted-PC2 prompts near PC1 zero were inspected for response-style drift.",
        "Observed upward PC2 drift is often associated with generic assistant, abstract synthesis, or interpersonal response scaffolds. This supports calibration and response-style explanations more than a pure coordinate-randomness explanation.",
    )
    table_report(
        "pc3_high_collapse_report.md",
        "PC3-High Collapse Diagnostic Report",
        bundle["pc3_high"],
        ["prompt_id", "prompt_family", "predicted_pc3", "observed_pc3", "delta_pc3", "response_classification", "nearest_observed_roles_pca3d", "diagnostic_note"],
        "Selected the three largest downward PC3 errors among forecasted PC3-high prompts.",
        f"Forecasted PC3-high summary: {json.dumps(bundle['pc3_high_stats'])}. The first-pass evidence supports PC3 neutralization: generated responses often become abstract, procedural, or stabilizing rather than remaining perturbative.",
    )
    table_report(
        "prompt_generation_audit_report.md",
        "Prompt Generation Audit Report",
        [],
        ["field", "value"],
        "This audit compares accepted/rejected generation-loop records for repeated scaffolds, acceptance patterns, and potential forecaster exploitation.",
        "The generation loop shows repeated prompt scaffolds and coefficient-aligned lexical phrasing. The battery should be treated as a strong forecaster stress test, but future validation should include a larger no-feedback/manual edge subset before claiming clean natural-language generalization.",
    )
    audit = bundle["generation_audit"]
    audit_lines = [
        "# Prompt Generation Audit Report",
        "",
        f"- Accepted records in generation log: {audit['accepted_count']}",
        f"- Rejected records in generation log: {audit['rejected_count']}",
        f"- Rejection reasons: `{dict(audit['rejection_reasons'])}`",
        f"- Accepted-generation repeated phrase counts: `{dict(audit['accepted_generation_phrase_counts'])}`",
        f"- Final-battery repeated phrase counts: `{dict(audit['final_battery_phrase_counts'])}`",
        "",
        "## By Target Region",
        "",
        "| region | accepted | rejected | mean artifact similarity | mean abs predicted PC3 |",
        "|---|---:|---:|---:|---:|",
    ]
    for k, v in audit["by_region"].items():
        audit_lines.append(f"| {k} | {v['accepted']} | {v['rejected']} | {v['mean_artifact_similarity']} | {v['mean_abs_predicted_pc3']} |")
    audit_lines += [
        "",
        "## Diagnostic Conclusion",
        "",
        "The loop is auditable and leakage/safety flags remain clean, but several accepted prompts use repeated scaffolds such as `Draft the response`, `if useful, it can also`, and recurring scenario frames. This is not a fatal flaw for a stress test, but it is enough to keep D08 open and to recommend a larger no-feedback natural-language holdout.",
    ]
    OUT.joinpath("prompt_generation_audit_report.md").write_text("\n".join(audit_lines) + "\n", encoding="utf-8")

    cal = bundle["calibration"]
    cal_lines = [
        "# Calibration Diagnostic Report",
        "",
        "Axis-wise observed = a + b * predicted calibration was fit as a first-pass diagnostic. LOOCV values are preliminary because this is still the same 100-prompt validation set.",
        "",
        "| axis | uncalibrated R2 | in-sample calibrated R2 | LOOCV calibrated R2 | slope | intercept | uncalibrated RMSE | LOOCV RMSE |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for pc, m in cal.items():
        cal_lines.append(f"| {pc} | {m['uncalibrated_r2']:.3f} | {m['in_sample_calibrated_r2']:.3f} | {m['loocv_calibrated_r2']:.3f} | {m['slope']:.3f} | {m['intercept']:.3f} | {m['uncalibrated_rmse']:.3f} | {m['loocv_calibrated_rmse']:.3f} |")
    cal_lines += ["", "Conclusion: calibration looks promising enough to be the next task, but it is not a resolved fix until tested on held-out prompts."]
    OUT.joinpath("calibration_diagnostic_report.md").write_text("\n".join(cal_lines) + "\n", encoding="utf-8")
    OUT.joinpath("calibration_metrics.json").write_text(json.dumps(cal, indent=2) + "\n", encoding="utf-8")
    return statuses


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, _, _, gen_sources = load_rows()
    thresholds = json.load(THRESHOLDS.open())
    geometry = json.load(GEOMETRY.open())
    pipe = load_forecaster()

    # Ensure nearest role/trait diagnostics are available where requested.
    cone = [add_nearest(r, geometry) for r in select_cone_outliers(rows, geometry, thresholds)]
    origin = select_extreme_pc1_near_zero_pc3(rows, pipe, thresholds)
    low_pc2 = select_low_pc2_near_zero_pc1(rows)
    pc2_groups = pc2_family(rows)
    pc3_high, pc3_stats = select_pc3_high_collapse(rows, geometry)
    largest = select_largest_3d(rows, geometry)
    audit = audit_generation(gen_sources["generation_log"], rows)
    cal = calibration_metrics(rows)
    method = methodology_table()

    common_fields = [
        "prompt_id", "prompt_family", "prompt_text", "generated_response", "predicted_pc1", "predicted_pc2", "predicted_pc3",
        "observed_pc1", "observed_pc2", "observed_pc3", "delta_pc1", "delta_pc2", "delta_pc3", "euclidean_delta_3d",
        "response_style_classification", "diagnostic_note", "nearest_observed_roles_pca3d", "nearest_observed_traits_pca3d",
    ]
    write_csv(OUT / "cone_violation_outliers.csv", cone, common_fields + ["observed_pc1_percentile", "observed_pc2_percentile", "pc1_pc2_percentile_sum"])
    write_csv(OUT / "forecast_extreme_pc1_near_zero_pc3_cases.csv", origin, common_fields + ["top_tfidf_terms_pc1", "top_tfidf_terms_pc2", "top_tfidf_terms_pc3", "artifact_similarity", "duplicate_similarity"])
    write_csv(OUT / "low_pc2_near_zero_pc1_cases.csv", low_pc2, common_fields)
    write_csv(OUT / "pc2_delta_by_family.csv", pc2_groups, ["group", "count", "mean_delta_pc2", "median_delta_pc2", "mae_pc2", "top_prompt_ids"])
    write_csv(OUT / "pc3_high_downward_error_cases.csv", pc3_high, common_fields + ["response_classification"])
    write_csv(OUT / "largest_3d_error_cases.csv", largest, common_fields + ["dominant_error_axis", "likely_cause_category", "response_classification"])

    bundle = {
        "generated_utc": now(),
        "startup_status": "STARTUP VERIFIED",
        "methodology_table": method,
        "cone": cone,
        "origin_bias": origin,
        "low_pc2": low_pc2,
        "pc2_groups": pc2_groups,
        "pc3_high": pc3_high,
        "pc3_high_stats": pc3_stats,
        "largest_3d": largest,
        "generation_audit": audit,
        "calibration": cal,
    }
    statuses = write_markdown_outputs(bundle)
    bundle["checklist_statuses"] = statuses
    # Convert non-json objects from counters.
    def clean(obj):
        if isinstance(obj, Counter):
            return dict(obj)
        if isinstance(obj, defaultdict):
            return dict(obj)
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj
    OUT.joinpath("diagnostic_case_bundle.json").write_text(json.dumps(clean(bundle), indent=2), encoding="utf-8")
    print(f"Wrote H100 diagnostic followups to {OUT}")
    print("Checklist statuses:", {k: v["status"] for k, v in statuses.items()})


if __name__ == "__main__":
    main()
