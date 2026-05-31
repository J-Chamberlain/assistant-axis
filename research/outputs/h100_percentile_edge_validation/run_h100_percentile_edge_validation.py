#!/usr/bin/env python3
"""Run percentile-edge prompt activation validation on Qwen/Qwen3-32B.

This runner is designed for RunPod execution. It uses existing project artifacts
only for the forecast side: the prompt manifest's frozen predicted PC addresses
and the canonical Qwen persona PCA geometry. The PCA projection basis is
reconstructed from the same committed Qwen role-vector source used to build the
visualizer, then sign-aligned and checked against the committed canonical
coordinates before any prompt validation proceeds.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


MODEL_ID = "Qwen/Qwen3-32B"
LAYER = 48
MAX_NEW_TOKENS = 256
DO_SAMPLE = False
TEMPERATURE = 0.0
TOP_P = 1.0
BATCH_SIZE = 10
EXPECTED_PROMPTS = 100

REPO_ROOT = Path(os.environ.get("ASSISTANT_AXIS_ROOT", "/root/assistant-axis"))
MANIFEST_PATH = REPO_ROOT / "research/outputs/novel_prompt_battery_percentile_edges/percentile_edge_h100_manifest.csv"
CANONICAL_PCA_PATH = REPO_ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"
VECTOR_DIR = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b/role_vectors"
OUT_DIR = REPO_ROOT / "research/outputs/h100_percentile_edge_validation"

RUN_CONFIG = OUT_DIR / "h100_run_config.json"
SMOKE_REPORT = OUT_DIR / "h100_smoke_test_report.md"
RUNTIME_ESTIMATE = OUT_DIR / "h100_runtime_estimate.json"
INCREMENTAL_CSV = OUT_DIR / "h100_incremental_results.csv"
CHECKPOINT_JSONL = OUT_DIR / "h100_checkpoint_metrics.jsonl"
CHECKPOINT_MD = OUT_DIR / "h100_checkpoint_summaries.md"
FINAL_CSV = OUT_DIR / "h100_final_results.csv"
FINAL_METRICS = OUT_DIR / "h100_final_metrics.json"
FINAL_REPORT = OUT_DIR / "h100_final_report.md"
RESPONSES_JSONL = OUT_DIR / "h100_generated_responses.jsonl"
PROJECTION_DEBUG = OUT_DIR / "h100_activation_projection_debug.json"
PLOTS_PATH = OUT_DIR / "h100_forecast_vs_observed_plots.png"
EARLY_STOP_REPORT = OUT_DIR / "h100_partial_early_stop_report.md"

RESULT_FIELDS = [
    "prompt_id",
    "prompt_text",
    "prompt_family",
    "predicted_pc1",
    "predicted_pc2",
    "predicted_pc3",
    "observed_pc1",
    "observed_pc2",
    "observed_pc3",
    "delta_pc1",
    "delta_pc2",
    "delta_pc3",
    "euclidean_delta_3d",
    "generated_response",
    "token_count",
    "generation_time_seconds",
    "activation_time_seconds",
    "total_prompt_time_seconds",
    "safety_empty_refusal_flag",
    "pc1_lower_tail",
    "pc1_upper_tail",
    "pc2_lower_tail",
    "pc2_upper_tail",
    "pc3_lower_tail",
    "pc3_upper_tail",
    "shoulder_edge",
    "interior_control",
]


def log(msg: str) -> None:
    print(msg, flush=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT),
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def to_float(x: Any) -> float:
    if x is None or x == "":
        return float("nan")
    return float(x)


def boolish(x: Any) -> bool:
    return str(x).strip().lower() in {"1", "true", "yes", "y"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rankdata(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    ranks = np.empty(len(x), dtype=float)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def pearson(a: np.ndarray, b: np.ndarray) -> float | None:
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 3:
        return None
    aa = a[mask] - a[mask].mean()
    bb = b[mask] - b[mask].mean()
    denom = np.linalg.norm(aa) * np.linalg.norm(bb)
    if denom <= 1e-12:
        return None
    return float(np.dot(aa, bb) / denom)


def spearman(a: np.ndarray, b: np.ndarray) -> float | None:
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 3:
        return None
    return pearson(rankdata(a[mask]), rankdata(b[mask]))


def rmse(a: np.ndarray, b: np.ndarray) -> float | None:
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() == 0:
        return None
    return float(np.sqrt(np.mean((a[mask] - b[mask]) ** 2)))


def mae(a: np.ndarray, b: np.ndarray) -> float | None:
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() == 0:
        return None
    return float(np.mean(np.abs(a[mask] - b[mask])))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float | None:
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    if mask.sum() < 2:
        return None
    ss_res = float(np.sum((y_true[mask] - y_pred[mask]) ** 2))
    ss_tot = float(np.sum((y_true[mask] - y_true[mask].mean()) ** 2))
    if ss_tot <= 1e-12:
        return None
    return 1.0 - ss_res / ss_tot


def slope_intercept(x: np.ndarray, y: np.ndarray) -> dict[str, float | None]:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 2 or np.var(x[mask]) <= 1e-12:
        return {"slope": None, "intercept": None}
    slope, intercept = np.polyfit(x[mask], y[mask], 1)
    return {"slope": float(slope), "intercept": float(intercept)}


def validate_manifest(rows: list[dict[str, str]]) -> None:
    if len(rows) != EXPECTED_PROMPTS:
        raise RuntimeError(f"Manifest row count {len(rows)} != expected {EXPECTED_PROMPTS}")
    ids = [r["prompt_id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise RuntimeError("Prompt IDs are not unique")
    for col in ["predicted_pc1", "predicted_pc2", "predicted_pc3"]:
        if col not in rows[0]:
            raise RuntimeError(f"Missing required manifest column: {col}")
        vals = np.array([to_float(r[col]) for r in rows], dtype=float)
        if not np.all(np.isfinite(vals)):
            raise RuntimeError(f"Non-finite forecast values in {col}")


def load_role_vectors_and_basis() -> dict[str, Any]:
    if not VECTOR_DIR.exists():
        raise RuntimeError(f"Missing Qwen role vector directory: {VECTOR_DIR}")
    canonical_rows = read_csv(CANONICAL_PCA_PATH)
    canonical = {
        r["persona"]: np.array(
            [to_float(r["activation_pc1"]), to_float(r["activation_pc2"]), to_float(r["activation_pc3"])],
            dtype=np.float64,
        )
        for r in canonical_rows
    }
    # The canonical visualizer PCA was fit over all available Qwen role vectors
    # (275), while the shared benchmark coordinate CSV contains the common
    # 273-persona subset. Fit the basis on the full role-vector source, then
    # verify coordinate reproduction on the committed subset.
    names = sorted([p.stem for p in VECTOR_DIR.glob("*.pt")])
    if len(names) < 275:
        raise RuntimeError(f"Too few Qwen role vectors found: {len(names)}")
    vectors = []
    for name in names:
        t = torch.load(VECTOR_DIR / f"{name}.pt", map_location="cpu").float()
        vec = t.mean(0) if t.dim() > 1 else t
        vectors.append(np.nan_to_num(vec.numpy().astype(np.float64)))
    x = np.stack(vectors)
    mean = x.mean(axis=0)
    centered = x - mean
    # Faster equivalent to PCA for n_roles << hidden_dim: eigendecompose the
    # role-role Gram matrix, then lift eigenvectors back into hidden space.
    gram = centered @ centered.T
    eigvals, eigvecs = np.linalg.eigh(gram)
    order = np.argsort(eigvals)[::-1][:3]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    components = []
    for i in range(3):
        scale = math.sqrt(max(float(eigvals[i]), 1e-12))
        comp = centered.T @ eigvecs[:, i] / scale
        comp = comp / (np.linalg.norm(comp) + 1e-12)
        components.append(comp)
    components = np.stack(components)
    reconstructed = centered @ components.T
    verify_idx = [i for i, n in enumerate(names) if n in canonical]
    verify_names = [names[i] for i in verify_idx]
    target = np.stack([canonical[n] for n in verify_names])
    signs = []
    for i in range(3):
        corr = pearson(reconstructed[verify_idx, i], target[:, i])
        sign = -1.0 if corr is not None and corr < 0 else 1.0
        signs.append(sign)
        components[i] *= sign
        reconstructed[:, i] *= sign
    abs_err = np.abs(reconstructed[verify_idx] - target)
    debug = {
        "basis_source": "reconstructed_from_canonical_qwen_role_vectors_with_sign_alignment",
        "basis_note": "No serialized PCA object was found in repo; this reconstructs the original basis from the same role-vector source and verifies exact coordinate reproduction before projection.",
        "vector_dir": str(VECTOR_DIR),
        "canonical_pca_path": str(CANONICAL_PCA_PATH),
        "n_roles_used": len(names),
        "n_roles_verified_against_committed_coordinates": len(verify_names),
        "role_vector_shape": list(x.shape),
        "sign_alignment": signs,
        "max_abs_coordinate_reproduction_error": float(abs_err.max()),
        "mean_abs_coordinate_reproduction_error": float(abs_err.mean()),
        "axis_max_abs_errors": {
            "pc1": float(abs_err[:, 0].max()),
            "pc2": float(abs_err[:, 1].max()),
            "pc3": float(abs_err[:, 2].max()),
        },
    }
    if debug["max_abs_coordinate_reproduction_error"] > 1e-5:
        raise RuntimeError(
            "Reconstructed PCA basis does not reproduce canonical coordinates; "
            f"max_abs_error={debug['max_abs_coordinate_reproduction_error']}"
        )
    PROJECTION_DEBUG.write_text(json.dumps(debug, indent=2))
    return {"mean": mean, "components": components, "debug": debug}


def project_activation(vec: np.ndarray, basis: dict[str, Any]) -> np.ndarray:
    return (vec.astype(np.float64) - basis["mean"]) @ basis["components"].T


def load_existing_results() -> list[dict[str, str]]:
    if not INCREMENTAL_CSV.exists():
        return []
    return read_csv(INCREMENTAL_CSV)


def is_refusal_or_empty(text: str) -> bool:
    s = text.strip().lower()
    if len(s) < 5:
        return True
    patterns = [
        "i can't help",
        "i cannot help",
        "i'm sorry",
        "i can’t assist",
        "i cannot assist",
        "as an ai",
    ]
    return any(p in s[:240] for p in patterns)


def make_prompt(tokenizer: Any, prompt_text: str) -> str:
    messages = [{"role": "user", "content": prompt_text}]
    try:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def generate_and_measure(
    tokenizer: Any,
    model: Any,
    prompt_text: str,
    basis: dict[str, Any],
) -> dict[str, Any]:
    prompt = make_prompt(tokenizer, prompt_text)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    prompt_len = int(inputs["input_ids"].shape[1])
    gen_start = time.time()
    with torch.no_grad():
        gen_out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=None if not DO_SAMPLE else TEMPERATURE,
            top_p=TOP_P,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )
    gen_time = time.time() - gen_start
    response_tokens = gen_out[0, prompt_len:]
    response_text = tokenizer.decode(response_tokens, skip_special_tokens=True).strip()
    act_start = time.time()
    with torch.no_grad():
        attn = torch.ones_like(gen_out, device=gen_out.device)
        out = model(
            input_ids=gen_out,
            attention_mask=attn,
            output_hidden_states=True,
            use_cache=False,
        )
        hidden = out.hidden_states[LAYER][0, prompt_len:, :].float().cpu().numpy()
    act_time = time.time() - act_start
    if hidden.shape[0] == 0:
        raise RuntimeError("No response-token hidden states captured")
    activation = hidden.mean(axis=0)
    coords = project_activation(activation, basis)
    return {
        "response_text": response_text,
        "token_count": int(response_tokens.shape[0]),
        "generation_time_seconds": gen_time,
        "activation_time_seconds": act_time,
        "observed": coords,
    }


def axis_arrays(rows: list[dict[str, Any]], pc: int) -> tuple[np.ndarray, np.ndarray]:
    pred = np.array([float(r[f"predicted_pc{pc}"]) for r in rows], dtype=float)
    obs = np.array([float(r[f"observed_pc{pc}"]) for r in rows], dtype=float)
    return pred, obs


def compute_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics: dict[str, Any] = {"completed_count": len(rows), "by_pc": {}, "families": {}, "tail_categories": {}}
    for pc in [1, 2, 3]:
        pred, obs = axis_arrays(rows, pc)
        si = slope_intercept(pred, obs)
        metrics["by_pc"][f"pc{pc}"] = {
            "pearson_r": pearson(pred, obs),
            "spearman_r": spearman(pred, obs),
            "rmse": rmse(pred, obs),
            "mae": mae(pred, obs),
            "r2": r2_score(obs, pred),
            "calibration_slope": si["slope"],
            "calibration_intercept": si["intercept"],
            "predicted_std": float(np.std(pred)) if len(pred) else None,
            "observed_std": float(np.std(obs)) if len(obs) else None,
        }
    euclidean = np.array([float(r["euclidean_delta_3d"]) for r in rows], dtype=float) if rows else np.array([])
    metrics["euclidean_delta_3d"] = {
        "mean": float(np.mean(euclidean)) if len(euclidean) else None,
        "median": float(np.median(euclidean)) if len(euclidean) else None,
        "max": float(np.max(euclidean)) if len(euclidean) else None,
    }
    for fam in sorted({r["prompt_family"] for r in rows}):
        subset = [r for r in rows if r["prompt_family"] == fam]
        metrics["families"][fam] = {
            "n": len(subset),
            "mae_pc1": mae(*axis_arrays(subset, 1)),
            "mae_pc2": mae(*axis_arrays(subset, 2)),
            "mae_pc3": mae(*axis_arrays(subset, 3)),
            "mean_euclidean_delta_3d": float(np.mean([float(r["euclidean_delta_3d"]) for r in subset])),
        }
    for col in [
        "pc1_lower_tail",
        "pc1_upper_tail",
        "pc2_lower_tail",
        "pc2_upper_tail",
        "pc3_lower_tail",
        "pc3_upper_tail",
        "shoulder_edge",
        "interior_control",
    ]:
        subset = [r for r in rows if boolish(r.get(col))]
        if subset:
            metrics["tail_categories"][col] = {
                "n": len(subset),
                "mae_pc1": mae(*axis_arrays(subset, 1)),
                "mae_pc2": mae(*axis_arrays(subset, 2)),
                "mae_pc3": mae(*axis_arrays(subset, 3)),
                "mean_euclidean_delta_3d": float(np.mean([float(r["euclidean_delta_3d"]) for r in subset])),
            }
    top_resid = sorted(rows, key=lambda r: float(r["euclidean_delta_3d"]), reverse=True)[:5]
    metrics["top_5_largest_residuals"] = [
        {
            "prompt_id": r["prompt_id"],
            "prompt_family": r["prompt_family"],
            "euclidean_delta_3d": float(r["euclidean_delta_3d"]),
            "delta_pc1": float(r["delta_pc1"]),
            "delta_pc2": float(r["delta_pc2"]),
            "delta_pc3": float(r["delta_pc3"]),
        }
        for r in top_resid
    ]
    return metrics


def write_checkpoint(rows: list[dict[str, Any]], start_time: float, rate_per_hour: float, phase: str) -> dict[str, Any]:
    elapsed = time.time() - start_time
    completed = len(rows)
    avg = elapsed / completed if completed else None
    remaining = max(EXPECTED_PROMPTS - completed, 0)
    est_remaining = remaining * avg if avg else None
    metrics = compute_metrics(rows)
    record = {
        "timestamp": now_iso(),
        "phase": phase,
        "completed_count": completed,
        "elapsed_time_seconds": elapsed,
        "average_seconds_per_prompt": avg,
        "estimated_remaining_time_seconds": est_remaining,
        "estimated_total_runtime_seconds": elapsed + (est_remaining or 0.0),
        "estimated_total_cost": ((elapsed + (est_remaining or 0.0)) / 3600.0) * rate_per_hour,
        "metrics": metrics,
    }
    append_jsonl(CHECKPOINT_JSONL, record)
    with CHECKPOINT_MD.open("a") as f:
        f.write(f"\n## Checkpoint: {completed} prompts ({phase})\n\n")
        f.write(f"- Timestamp UTC: {record['timestamp']}\n")
        f.write(f"- Elapsed: {elapsed/60:.2f} min\n")
        f.write(f"- Average seconds/prompt: {avg:.2f}\n" if avg else "- Average seconds/prompt: n/a\n")
        if est_remaining is not None:
            f.write(f"- Estimated remaining: {est_remaining/60:.2f} min\n")
            f.write(f"- Estimated total runtime: {record['estimated_total_runtime_seconds']/60:.2f} min\n")
            f.write(f"- Estimated total cost: ${record['estimated_total_cost']:.2f}\n")
        for pc in ["pc1", "pc2", "pc3"]:
            m = metrics["by_pc"][pc]
            f.write(
                f"- {pc}: Pearson={m['pearson_r']}, Spearman={m['spearman_r']}, "
                f"RMSE={m['rmse']}, MAE={m['mae']}\n"
            )
        f.write("- Top residuals: " + json.dumps(metrics["top_5_largest_residuals"]) + "\n")
    return record


def write_smoke_report(rows: list[dict[str, Any]], load_time: float, elapsed: float, rate_per_hour: float, basis_debug: dict[str, Any]) -> None:
    avg_total = elapsed / len(rows) if rows else None
    avg_gen = float(np.mean([float(r["generation_time_seconds"]) for r in rows])) if rows else None
    avg_act = float(np.mean([float(r["activation_time_seconds"]) for r in rows])) if rows else None
    est_total = (avg_total or 0.0) * EXPECTED_PROMPTS + load_time
    estimate = {
        "timestamp": now_iso(),
        "load_time_seconds": load_time,
        "smoke_elapsed_seconds_excluding_load": elapsed,
        "smoke_prompts": len(rows),
        "average_total_seconds_per_prompt": avg_total,
        "average_generation_seconds_per_prompt": avg_gen,
        "average_activation_projection_seconds_per_prompt": avg_act,
        "estimated_total_runtime_seconds_including_load": est_total,
        "rate_per_hour": rate_per_hour,
        "estimated_total_cost": est_total / 3600.0 * rate_per_hour,
    }
    RUNTIME_ESTIMATE.write_text(json.dumps(estimate, indent=2))
    metrics = compute_metrics(rows)
    SMOKE_REPORT.write_text(
        "# H100 Smoke Test Report\n\n"
        f"- Timestamp UTC: {now_iso()}\n"
        f"- Smoke prompts completed: {len(rows)}\n"
        f"- Model load time: {load_time:.2f}s\n"
        f"- Average generation time: {avg_gen:.2f}s\n"
        f"- Average activation/projection time: {avg_act:.2f}s\n"
        f"- Average total prompt time: {avg_total:.2f}s\n"
        f"- Estimated 100-prompt runtime including load: {est_total/60:.2f} min\n"
        f"- Estimated cost at ${rate_per_hour:.4f}/hr: ${estimate['estimated_total_cost']:.2f}\n"
        f"- PCA reproduction max abs error: {basis_debug['max_abs_coordinate_reproduction_error']:.3e}\n"
        f"- Smoke metrics: `{json.dumps(metrics['by_pc'])}`\n"
    )


def make_plots(rows: list[dict[str, Any]]) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        log(f"Plot generation skipped: {exc}")
        return
    if not rows:
        return
    fig, axes = plt.subplots(3, 3, figsize=(16, 14))
    for idx, pc in enumerate([1, 2, 3]):
        pred, obs = axis_arrays(rows, pc)
        axes[0, idx].scatter(pred, obs, alpha=0.75)
        axes[0, idx].set_title(f"Predicted vs observed PC{pc}")
        axes[0, idx].set_xlabel("predicted")
        axes[0, idx].set_ylabel("observed")
        lo = float(min(np.min(pred), np.min(obs)))
        hi = float(max(np.max(pred), np.max(obs)))
        axes[0, idx].plot([lo, hi], [lo, hi], "--", color="gray", linewidth=1)
        axes[1, idx].hist(obs - pred, bins=16)
        axes[1, idx].set_title(f"Residual histogram PC{pc}")
        axes[1, idx].set_xlabel("observed - predicted")
    for ax, pair in zip(axes[2], [(1, 2), (1, 3), (2, 3)]):
        p1, o1 = axis_arrays(rows, pair[0])
        p2, o2 = axis_arrays(rows, pair[1])
        ax.scatter(p1, p2, alpha=0.55, label="predicted")
        ax.scatter(o1, o2, alpha=0.55, label="observed")
        ax.set_title(f"PC{pair[0]}-PC{pair[1]} predicted/observed")
        ax.set_xlabel(f"PC{pair[0]}")
        ax.set_ylabel(f"PC{pair[1]}")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(PLOTS_PATH, dpi=180)
    plt.close(fig)


def write_final_report(rows: list[dict[str, Any]], rate_per_hour: float, start_time: float, early_stop: str | None = None) -> None:
    metrics = compute_metrics(rows)
    FINAL_METRICS.write_text(json.dumps(metrics, indent=2))
    make_plots(rows)
    elapsed = time.time() - start_time
    lines = [
        "# H100 Percentile-Edge Validation Final Report",
        "",
        f"- Timestamp UTC: {now_iso()}",
        f"- Completed prompts: {len(rows)}",
        f"- Early stop status: {early_stop or 'not triggered'}",
        f"- Elapsed runtime tracked by script: {elapsed/60:.2f} min",
        f"- Rate per hour: ${rate_per_hour:.4f}",
        f"- Script-estimated prompt-run cost: ${elapsed/3600*rate_per_hour:.2f}",
        f"- Model: {MODEL_ID}",
        f"- Layer: {LAYER}",
        f"- Representation: response-token residual activations, mean pooled over generated response tokens only",
        f"- Projection: reconstructed canonical Qwen persona PCA basis, sign-aligned and verified against committed coordinates",
        "",
        "## Forecast vs Observed Metrics",
        "",
    ]
    for pc in ["pc1", "pc2", "pc3"]:
        m = metrics["by_pc"][pc]
        lines.append(
            f"- {pc}: R2={m['r2']}, Pearson={m['pearson_r']}, Spearman={m['spearman_r']}, "
            f"RMSE={m['rmse']}, MAE={m['mae']}, slope={m['calibration_slope']}, intercept={m['calibration_intercept']}"
        )
    lines.extend(
        [
            "",
            "## Largest Current Residuals",
            "",
        ]
    )
    for r in metrics["top_5_largest_residuals"]:
        lines.append(f"- {r}")
    lines.extend(["", "## Metrics By Prompt Family", ""])
    for fam, m in metrics["families"].items():
        lines.append(f"- {fam}: {m}")
    lines.extend(["", "## Metrics By Percentile-Tail Category", ""])
    for cat, m in metrics["tail_categories"].items():
        lines.append(f"- {cat}: {m}")
    FINAL_REPORT.write_text("\n".join(lines) + "\n")


def maybe_early_stop(rows: list[dict[str, Any]], rate_per_hour: float, start_time: float) -> str | None:
    if len(rows) < 20:
        return None
    metrics = compute_metrics(rows)
    pearsons = [metrics["by_pc"][f"pc{i}"]["pearson_r"] for i in [1, 2, 3]]
    observed_stds = [metrics["by_pc"][f"pc{i}"]["observed_std"] for i in [1, 2, 3]]
    refusals = sum(1 for r in rows if boolish(r.get("safety_empty_refusal_flag")))
    if all(p is not None and p <= 0.0 for p in pearsons):
        return "all_three_pcs_have_nonpositive_pearson_after_20_prompts"
    if all(s is not None and s < 1e-6 for s in observed_stds):
        return "observed_coordinates_nearly_constant_after_20_prompts"
    if refusals / len(rows) > 0.5:
        return "generated_responses_empty_or_refusal_for_majority_after_20_prompts"
    elapsed = time.time() - start_time
    avg = elapsed / max(len(rows), 1)
    est_total_cost = (avg * EXPECTED_PROMPTS / 3600.0) * rate_per_hour
    if est_total_cost > 35.0:
        return f"estimated_total_cost_exceeds_budget_after_20_prompts: {est_total_cost:.2f}"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["smoke", "full"], required=True)
    parser.add_argument("--max-prompts", type=int, default=None)
    parser.add_argument("--rate-per-hour", type=float, required=True)
    parser.add_argument("--pod-id", default=os.environ.get("RUNPOD_POD_ID", "unknown"))
    parser.add_argument("--pod-name", default=os.environ.get("RUNPOD_POD_NAME", "unknown"))
    parser.add_argument("--auto-early-stop", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run_start = time.time()
    manifest_rows = read_csv(MANIFEST_PATH)
    validate_manifest(manifest_rows)
    basis = load_role_vectors_and_basis()

    config = {
        "timestamp": now_iso(),
        "repo_root": str(REPO_ROOT),
        "git_commit": git_commit(),
        "pod_id": args.pod_id,
        "pod_name": args.pod_name,
        "rate_per_hour": args.rate_per_hour,
        "model": MODEL_ID,
        "layer": LAYER,
        "manifest_path": str(MANIFEST_PATH),
        "manifest_sha256": sha256_file(MANIFEST_PATH),
        "canonical_pca_path": str(CANONICAL_PCA_PATH),
        "canonical_pca_sha256": sha256_file(CANONICAL_PCA_PATH),
        "decoding": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "do_sample": DO_SAMPLE,
            "enable_thinking": False,
        },
        "batch_size": BATCH_SIZE,
        "projection_debug": basis["debug"],
    }
    RUN_CONFIG.write_text(json.dumps(config, indent=2))

    token = os.environ.get("HF_TOKEN")
    load_start = time.time()
    log("Loading tokenizer/model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    load_time = time.time() - load_start
    log(f"Model loaded in {load_time:.1f}s")

    existing = load_existing_results() if args.phase == "full" else []
    done_ids = {r["prompt_id"] for r in existing}
    rows: list[dict[str, Any]] = [dict(r) for r in existing]
    limit = args.max_prompts if args.max_prompts is not None else EXPECTED_PROMPTS
    target_rows = [r for r in manifest_rows if r["prompt_id"] not in done_ids]
    target_rows = target_rows[: max(0, limit - len(rows))]

    phase_start_count = len(rows)
    for manifest_row in target_rows:
        prompt_start = time.time()
        pid = manifest_row["prompt_id"]
        log(f"Running {pid} ({len(rows)+1}/{EXPECTED_PROMPTS})")
        measured = generate_and_measure(tokenizer, model, manifest_row["prompt_text"], basis)
        observed = measured["observed"]
        pred = np.array(
            [
                to_float(manifest_row["predicted_pc1"]),
                to_float(manifest_row["predicted_pc2"]),
                to_float(manifest_row["predicted_pc3"]),
            ],
            dtype=float,
        )
        delta = observed - pred
        result: dict[str, Any] = {
            "prompt_id": pid,
            "prompt_text": manifest_row["prompt_text"],
            "prompt_family": manifest_row.get("prompt_family", ""),
            "predicted_pc1": float(pred[0]),
            "predicted_pc2": float(pred[1]),
            "predicted_pc3": float(pred[2]),
            "observed_pc1": float(observed[0]),
            "observed_pc2": float(observed[1]),
            "observed_pc3": float(observed[2]),
            "delta_pc1": float(delta[0]),
            "delta_pc2": float(delta[1]),
            "delta_pc3": float(delta[2]),
            "euclidean_delta_3d": float(np.linalg.norm(delta)),
            "generated_response": measured["response_text"],
            "token_count": measured["token_count"],
            "generation_time_seconds": round(measured["generation_time_seconds"], 3),
            "activation_time_seconds": round(measured["activation_time_seconds"], 3),
            "total_prompt_time_seconds": round(time.time() - prompt_start, 3),
            "safety_empty_refusal_flag": is_refusal_or_empty(measured["response_text"]),
        }
        for col in [
            "pc1_lower_tail",
            "pc1_upper_tail",
            "pc2_lower_tail",
            "pc2_upper_tail",
            "pc3_lower_tail",
            "pc3_upper_tail",
            "shoulder_edge",
            "interior_control",
        ]:
            result[col] = manifest_row.get(col, "")
        rows.append(result)
        write_csv(INCREMENTAL_CSV, rows, RESULT_FIELDS)
        append_jsonl(
            RESPONSES_JSONL,
            {
                "prompt_id": pid,
                "prompt_text": manifest_row["prompt_text"],
                "generated_response": measured["response_text"],
                "token_count": measured["token_count"],
                "timestamp": now_iso(),
            },
        )
        log(
            f"{pid}: obs=({observed[0]:.3f},{observed[1]:.3f},{observed[2]:.3f}) "
            f"delta_norm={result['euclidean_delta_3d']:.3f} "
            f"gen={result['generation_time_seconds']}s act={result['activation_time_seconds']}s"
        )
        completed = len(rows)
        if completed in {3, 10, 20} or (completed > 20 and completed % BATCH_SIZE == 0):
            write_checkpoint(rows, run_start, args.rate_per_hour, args.phase)
        if args.auto_early_stop and completed >= 20:
            reason = maybe_early_stop(rows, args.rate_per_hour, run_start)
            if reason:
                EARLY_STOP_REPORT.write_text(
                    "# H100 Partial Early Stop Report\n\n"
                    f"- Timestamp UTC: {now_iso()}\n"
                    f"- Completed prompts: {completed}\n"
                    f"- Reason: {reason}\n"
                    f"- Metrics: `{json.dumps(compute_metrics(rows)['by_pc'])}`\n"
                    f"- Outputs preserved under: `{OUT_DIR}`\n"
                )
                write_final_report(rows, args.rate_per_hour, run_start, early_stop=reason)
                write_csv(FINAL_CSV, rows, RESULT_FIELDS)
                log(f"EARLY_STOP: {reason}")
                return

    new_rows = len(rows) - phase_start_count
    if args.phase == "smoke":
        smoke_elapsed = time.time() - run_start - load_time
        write_smoke_report(rows, load_time, smoke_elapsed, args.rate_per_hour, basis["debug"])
    if len(rows) >= EXPECTED_PROMPTS or args.phase == "full":
        write_csv(FINAL_CSV, rows, RESULT_FIELDS)
        write_final_report(rows, args.rate_per_hour, run_start)
    log(f"Phase {args.phase} complete. new_rows={new_rows}, total_rows={len(rows)}")


if __name__ == "__main__":
    main()
