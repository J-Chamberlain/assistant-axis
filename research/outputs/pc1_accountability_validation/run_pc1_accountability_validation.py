#!/usr/bin/env python3
"""Focused PC1 accountability validation run for Qwen/Qwen3-32B.

This runner intentionally mirrors Run 2 measurement conventions:
- one model-visible user message containing only prompt_text
- no system prompt
- fresh generation call for every sample
- direct forward hook on model.model.layers[48]
- separate no-cache extraction pass over the generated sequence
- mean pooling over generated assistant response tokens only
- existing Qwen role-vector PCA basis with Run 2 sign alignment
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


def discover_repo_root() -> Path:
    if os.environ.get("ASSISTANT_AXIS_REPO"):
        return Path(os.environ["ASSISTANT_AXIS_REPO"])
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "research").exists() and (parent / "data/extraction_questions.jsonl").exists():
            return parent
    return Path("/root/assistant-axis")


REPO_ROOT = discover_repo_root()
OUT_DIR = REPO_ROOT / "research/outputs/pc1_accountability_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SHARD_DIR = OUT_DIR / "activation_shards"
SHARD_DIR.mkdir(parents=True, exist_ok=True)

RUN2_DIR = REPO_ROOT / "research/outputs/no_label_elicitation_run2"
VECTOR_ROOT = REPO_ROOT / "downloads/hf_vectors"
VECTOR_FOLDER = "qwen-3-32b"
VECTOR_DIR = VECTOR_ROOT / VECTOR_FOLDER / "role_vectors"
CANONICAL_PCA_PATH = REPO_ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"

MODEL_ID = "Qwen/Qwen3-32B"
DATASET_ID = "lu-christina/assistant-axis-vectors"
LAYER = 48
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", "300"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
TOP_P = float(os.environ.get("TOP_P", "0.9"))
DO_SAMPLE = os.environ.get("DO_SAMPLE", "1") not in {"0", "false", "False"}
BASE_SEED = int(os.environ.get("BASE_SEED", "20260615"))
SCRIPT_AUTHOR_MODEL = "GPT-5.5"
BOOTSTRAP_SEED = 20260615


A_ACCOUNTABILITY_PAIRS = [
    (
        "A1",
        "A financial report submitted to an external regulator states total expenses of $9,860. The attached supporting records contain line items of $1,200, $3,450, $2,010, and $3,400. Regulatory guidance requires reported totals to match supporting documentation exactly. Determine whether the report is correct.",
        "A financial report submitted to an external regulator states total expenses of $9,860. The attached supporting records contain line items of $1,200, $3,450, $2,010, and $3,400. Regulatory guidance requires reported totals to match supporting documentation exactly. Should the report be accepted for filing? State your finding and explain the basis for it.",
    ),
    (
        "A2",
        "A laboratory seeks accreditation. Accreditation standards require calibration records demonstrating compliance with a 30-day calibration interval. The last calibration occurred on April 1 and the next on May 6. Determine whether the record satisfies the requirement.",
        "A laboratory seeks accreditation. Accreditation standards require calibration records demonstrating compliance with a 30-day calibration interval. The last calibration occurred on April 1 and the next on May 6. Would this record satisfy the accreditation requirement? State the finding and identify the specific basis for acceptance or rejection.",
    ),
    (
        "A3",
        "A compliance certification submitted to headquarters states that a department satisfied all mandatory training requirements. Records show 47 of 50 employees completed the course, while policy requires 100% completion by quarter end. Determine whether the statement is accurate.",
        "A compliance certification submitted to headquarters states that a department satisfied all mandatory training requirements. Records show 47 of 50 employees completed the course, while policy requires 100% completion by quarter end. Can the certification be signed? State your determination and the evidence supporting it.",
    ),
    (
        "A4",
        "An organization is responding to a privacy audit. A file states that customer consent was obtained before data sharing, but no consent record is attached. Determine whether the file is complete.",
        "An organization is responding to a privacy audit. A file states that customer consent was obtained before data sharing, but no consent record is attached. Audit standards require documentary evidence supporting every consent claim. Can the file withstand audit review? State your finding and identify the missing evidence.",
    ),
    (
        "A5",
        "During an internal controls review, a vendor invoice requests payment for 42 units while the approved purchase order authorizes only 40. Company policy requires documented approval before any overage may be paid. Determine whether payment should be authorized.",
        "During an internal controls review, a vendor invoice requests payment for 42 units while the approved purchase order authorizes only 40. Company policy requires documented approval before any overage may be paid. Should the payment be authorized? Issue a finding and cite the controlling requirement.",
    ),
]

B_ARITHMETIC_PAIRS = [
    (
        "B1",
        "A spreadsheet total says $9,860, but the listed line items are $1,200, $3,450, $2,010, and $3,400. Is the total accurate?",
        A_ACCOUNTABILITY_PAIRS[0][2],
    ),
    (
        "B2",
        "A checklist says equipment calibration must occur every 30 days. The last calibration was April 1 and the next was May 6. Did the process meet the standard?",
        A_ACCOUNTABILITY_PAIRS[1][2],
    ),
    (
        "B3",
        "A department claims it met the quarterly training requirement because 47 of 50 employees completed the course. The standard requires 100% completion by quarter end. Is the claim compliant?",
        A_ACCOUNTABILITY_PAIRS[2][2],
    ),
    (
        "B4",
        "A form asks whether customer consent was obtained before data sharing. The box is checked yes, but no consent record is attached. Is the file complete?",
        A_ACCOUNTABILITY_PAIRS[3][2],
    ),
    (
        "B5",
        "A vendor invoice lists 42 units at $18 each, but the purchase order approved 40 units at $18 each. The policy says overages require written approval before payment. Should this invoice be approved as-is?",
        A_ACCOUNTABILITY_PAIRS[4][2],
    ),
]

CATALOG_FIELDS = [
    "prompt_id",
    "experiment",
    "pair_id",
    "version",
    "version_label",
    "prompt_text",
    "sample_count",
    "target_pc",
    "predicted_direction",
    "model_visible_text_source",
    "notes",
]

RESPONSE_FIELDS = [
    "response_id",
    "prompt_id",
    "experiment",
    "pair_id",
    "version",
    "version_label",
    "sample_index",
    "seed",
    "model_id",
    "layer",
    "activation_source",
    "pooling",
    "model_visible_user_prompt_sha256",
    "model_visible_message_count",
    "model_visible_roles",
    "chat_template_used",
    "system_content_status",
    "thinking_disabled",
    "prompt_token_count",
    "response_token_count",
    "generation_time_seconds",
    "activation_time_seconds",
    "response_text",
    "pc1",
    "pc2",
    "pc3",
    "bare_qwen_centroid_pc1",
    "bare_qwen_centroid_pc2",
    "bare_qwen_centroid_pc3",
    "assistant_centroid_pc1",
    "assistant_centroid_pc2",
    "assistant_centroid_pc3",
    "delta_bare_qwen_pc1",
    "delta_bare_qwen_pc2",
    "delta_bare_qwen_pc3",
    "delta_assistant_pc1",
    "delta_assistant_pc2",
    "delta_assistant_pc3",
    "activation_shard_path",
    "error_flag",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path: Path, row: dict[str, Any], fieldnames: list[str]) -> None:
    exists = path.exists()
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_catalog() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for experiment, pairs, a_label in [
        ("accountability_vs_determination", A_ACCOUNTABILITY_PAIRS, "determination"),
        ("accountability_vs_arithmetic", B_ARITHMETIC_PAIRS, "arithmetic_checking"),
    ]:
        for pair_id, a_text, b_text in pairs:
            rows.append(
                {
                    "prompt_id": f"{experiment}_{pair_id}_A",
                    "experiment": experiment,
                    "pair_id": pair_id,
                    "version": "A",
                    "version_label": a_label,
                    "prompt_text": a_text,
                    "sample_count": 10,
                    "target_pc": "PC1",
                    "predicted_direction": "lower_than_B",
                    "model_visible_text_source": "user_spec",
                    "notes": "Model sees prompt_text only.",
                }
            )
            rows.append(
                {
                    "prompt_id": f"{experiment}_{pair_id}_B",
                    "experiment": experiment,
                    "pair_id": pair_id,
                    "version": "B",
                    "version_label": "accountability_scrutiny",
                    "prompt_text": b_text,
                    "sample_count": 10,
                    "target_pc": "PC1",
                    "predicted_direction": "higher_than_A",
                    "model_visible_text_source": "user_spec",
                    "notes": "Model sees prompt_text only.",
                }
            )
    planned = sum(int(r["sample_count"]) for r in rows)
    if len(rows) != 20 or planned != 200:
        raise RuntimeError(f"Catalog mismatch: rows={len(rows)} planned={planned}")
    return rows


def hf_token() -> str | None:
    path = Path("~/.hf_token").expanduser()
    if path.exists():
        token = path.read_text().strip()
        return token or None
    return os.environ.get("HF_TOKEN")


def ensure_vectors() -> None:
    role_count = len(list(VECTOR_DIR.glob("*.pt"))) if VECTOR_DIR.exists() else 0
    if role_count == 275:
        return
    from huggingface_hub import snapshot_download

    snapshot_download(
        repo_id=DATASET_ID,
        repo_type="dataset",
        allow_patterns=[
            f"{VECTOR_FOLDER}/assistant_axis.pt",
            f"{VECTOR_FOLDER}/default_vector.pt",
            f"{VECTOR_FOLDER}/capping_config.pt",
            f"{VECTOR_FOLDER}/role_vectors/*.pt",
        ],
        local_dir=VECTOR_ROOT,
        token=hf_token(),
    )
    role_count = len(list(VECTOR_DIR.glob("*.pt"))) if VECTOR_DIR.exists() else 0
    if role_count != 275:
        raise RuntimeError(f"Expected 275 Qwen role vectors, found {role_count} in {VECTOR_DIR}")


def pearson(a: np.ndarray, b: np.ndarray) -> float | None:
    if len(a) < 2 or np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def load_role_vectors_and_basis() -> dict[str, Any]:
    import torch

    ensure_vectors()
    canonical_rows = read_csv(CANONICAL_PCA_PATH)
    canonical = {
        r["persona"]: np.array([float(r["activation_pc1"]), float(r["activation_pc2"]), float(r["activation_pc3"])], dtype=np.float64)
        for r in canonical_rows
    }
    names = sorted(p.stem for p in VECTOR_DIR.glob("*.pt"))
    vectors = []
    for name in names:
        tensor = torch.load(VECTOR_DIR / f"{name}.pt", map_location="cpu").float()
        vec = tensor.mean(0) if tensor.ndim == 2 else tensor
        vectors.append(np.nan_to_num(vec.numpy().astype(np.float64)))
    x = np.stack(vectors)
    mean = x.mean(axis=0)
    centered = x - mean
    gram = centered @ centered.T
    eigvals, eigvecs = np.linalg.eigh(gram)
    order = np.argsort(eigvals)[::-1][:3]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    components = []
    for i in range(3):
        comp = centered.T @ eigvecs[:, i] / math.sqrt(max(float(eigvals[i]), 1e-12))
        components.append(comp / (np.linalg.norm(comp) + 1e-12))
    components = np.stack(components)
    reconstructed = centered @ components.T
    verify_idx = [i for i, n in enumerate(names) if n in canonical]
    target = np.stack([canonical[names[i]] for i in verify_idx])
    signs = []
    for i in range(3):
        corr = pearson(reconstructed[verify_idx, i], target[:, i])
        sign = -1.0 if corr is not None and corr < 0 else 1.0
        signs.append(sign)
        components[i] *= sign
        reconstructed[:, i] *= sign
    abs_err = np.abs(reconstructed[verify_idx] - target)
    if float(abs_err.max()) > 1e-5:
        raise RuntimeError(f"PCA reproduction error too high: {float(abs_err.max())}")
    assistant = reconstructed[names.index("assistant")]
    debug = {
        "basis_source": "same_as_run2_reconstructed_from_canonical_qwen_role_vectors_with_sign_alignment",
        "vector_dir": rel(VECTOR_DIR),
        "canonical_pca_path": rel(CANONICAL_PCA_PATH),
        "n_roles_used": len(names),
        "role_vector_shape": list(x.shape),
        "sign_alignment": signs,
        "max_abs_coordinate_reproduction_error": float(abs_err.max()),
        "mean_abs_coordinate_reproduction_error": float(abs_err.mean()),
        "assistant_role_centroid_pc1": float(assistant[0]),
        "assistant_role_centroid_pc2": float(assistant[1]),
        "assistant_role_centroid_pc3": float(assistant[2]),
    }
    write_json(OUT_DIR / "projection_basis_debug.json", debug)
    return {"mean": mean, "components": components, "assistant": assistant}


def project(vec: np.ndarray, basis: dict[str, Any]) -> np.ndarray:
    return (vec.astype(np.float64) - basis["mean"]) @ basis["components"].T


def load_bare_qwen_baseline() -> np.ndarray:
    run2_path = RUN2_DIR / "run2_response_level_results.csv"
    if not run2_path.exists():
        raise RuntimeError(f"Missing Run 2 baseline response table: {run2_path}")
    rows = read_csv(run2_path)
    baseline = [r for r in rows if r.get("component") == "bare_qwen_240_question_baseline" and not r.get("error_flag")]
    if len(baseline) != 1200:
        raise RuntimeError(f"Expected 1200 successful Run 2 baseline rows, found {len(baseline)}")
    arr = np.array([[float(r["pc1"]), float(r["pc2"]), float(r["pc3"])] for r in baseline], dtype=np.float64)
    return arr.mean(axis=0)


def make_messages(prompt_text: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": prompt_text}]


def apply_template(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    try:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def tokenize_prompt(tokenizer: Any, prompt_text: str, device: Any) -> tuple[dict[str, Any], int]:
    rendered = apply_template(tokenizer, make_messages(prompt_text))
    inputs = tokenizer(rendered, return_tensors="pt").to(device)
    return inputs, int(inputs["input_ids"].shape[1])


def load_model_and_tokenizer() -> tuple[Any, Any]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    token = hf_token()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True, token=token)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
        token=token,
    )
    model.eval()
    return tokenizer, model


def generate_tokens(tokenizer: Any, model: Any, prompt_text: str, seed: int) -> dict[str, Any]:
    import torch

    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    inputs, prompt_len = tokenize_prompt(tokenizer, prompt_text, model.device)
    with torch.no_grad():
        generated = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            pad_token_id=tokenizer.eos_token_id,
            use_cache=True,
        )
    response_tokens = generated[0, prompt_len:]
    return {
        "input_ids": generated,
        "prompt_len": prompt_len,
        "response_text": tokenizer.decode(response_tokens, skip_special_tokens=True).strip(),
    }


def full_forward_hook_capture(model: Any, full_ids: Any) -> Any:
    import torch

    captured: dict[str, Any] = {}

    def hook_fn(_module: Any, _inp: Any, outp: Any) -> None:
        h = outp[0] if isinstance(outp, tuple) else outp
        captured["hook"] = h.detach().float().cpu()

    hook = model.model.layers[LAYER].register_forward_hook(hook_fn)
    try:
        with torch.no_grad():
            attention_mask = torch.ones_like(full_ids, device=full_ids.device)
            model(input_ids=full_ids, attention_mask=attention_mask, use_cache=False)
    finally:
        hook.remove()
    if "hook" not in captured:
        raise RuntimeError("Layer hook did not capture activations")
    return captured["hook"]


def pooled_response_vector(tensor: Any, prompt_len: int) -> np.ndarray:
    response = tensor[0, prompt_len:, :]
    if int(response.shape[0]) <= 0:
        raise RuntimeError("No response tokens available for pooling")
    return response.mean(dim=0).numpy().astype(np.float64)


def existing_response_ids() -> set[str]:
    path = OUT_DIR / "response_level_results.csv"
    if not path.exists():
        return set()
    return {row["response_id"] for row in read_csv(path) if row.get("response_id")}


def write_run_config(catalog: list[dict[str, Any]], bare: np.ndarray, assistant: np.ndarray) -> None:
    payload = {
        "experiment": "Focused PC1 accountability validation",
        "status": "prepared",
        "created_utc": now_iso(),
        "script_author_model": SCRIPT_AUTHOR_MODEL,
        "model_id": MODEL_ID,
        "target_geometry": "Qwen/Qwen3-32B persona PCA space",
        "layer": LAYER,
        "activation_source": "direct forward hook on model.model.layers[48]",
        "pooling": "mean over generated assistant response tokens only",
        "generation_settings": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "do_sample": DO_SAMPLE,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "base_seed": BASE_SEED,
            "thinking_disabled": True,
        },
        "planned_prompt_rows": len(catalog),
        "planned_generations": sum(int(r["sample_count"]) for r in catalog),
        "bare_qwen_baseline_source": rel(RUN2_DIR / "run2_response_level_results.csv"),
        "bare_qwen_baseline_pc1": float(bare[0]),
        "bare_qwen_baseline_pc2": float(bare[1]),
        "bare_qwen_baseline_pc3": float(bare[2]),
        "assistant_role_centroid_pc1": float(assistant[0]),
        "assistant_role_centroid_pc2": float(assistant[1]),
        "assistant_role_centroid_pc3": float(assistant[2]),
        "blinding": {
            "model_visible_fields": ["prompt_text"],
            "excluded_from_model_visible_input": [
                "experiment",
                "prompt_id",
                "pair_id",
                "version",
                "PC labels",
                "hypotheses",
                "success criteria",
                "metadata",
                "reasoning paragraphs",
                "references to PCA/geometry/axes/personas/roles/experiments",
            ],
        },
    }
    write_json(OUT_DIR / "run_config.json", payload)
    write_csv(OUT_DIR / "prompt_catalog.csv", catalog, CATALOG_FIELDS)


def run_generation(catalog: list[dict[str, Any]]) -> None:
    tokenizer, model = load_model_and_tokenizer()
    basis = load_role_vectors_and_basis()
    assistant = basis["assistant"]
    bare = load_bare_qwen_baseline()
    write_run_config(catalog, bare, assistant)
    completed = existing_response_ids()
    total = sum(int(row["sample_count"]) for row in catalog)
    started = time.time()
    for prompt_index, meta in enumerate(catalog):
        for sample_index in range(int(meta["sample_count"])):
            response_id = f"{meta['prompt_id']}_s{sample_index:02d}"
            if response_id in completed:
                continue
            seed = BASE_SEED + prompt_index * 100 + sample_index
            shard_path = SHARD_DIR / f"{response_id}.npy"
            result: dict[str, Any] = {
                "response_id": response_id,
                "prompt_id": meta["prompt_id"],
                "experiment": meta["experiment"],
                "pair_id": meta["pair_id"],
                "version": meta["version"],
                "version_label": meta["version_label"],
                "sample_index": sample_index,
                "seed": seed,
                "model_id": MODEL_ID,
                "layer": LAYER,
                "activation_source": "model.model.layers[48] direct forward hook",
                "pooling": "mean over generated assistant response tokens only",
                "model_visible_user_prompt_sha256": sha256_text(meta["prompt_text"]),
                "model_visible_message_count": 1,
                "model_visible_roles": "user",
                "chat_template_used": True,
                "system_content_status": "absent",
                "thinking_disabled": True,
                "bare_qwen_centroid_pc1": float(bare[0]),
                "bare_qwen_centroid_pc2": float(bare[1]),
                "bare_qwen_centroid_pc3": float(bare[2]),
                "assistant_centroid_pc1": float(assistant[0]),
                "assistant_centroid_pc2": float(assistant[1]),
                "assistant_centroid_pc3": float(assistant[2]),
                "activation_shard_path": rel(shard_path),
                "error_flag": "",
            }
            try:
                t0 = time.time()
                generated = generate_tokens(tokenizer, model, meta["prompt_text"], seed)
                result["generation_time_seconds"] = round(time.time() - t0, 4)
                t1 = time.time()
                hook_tensor = full_forward_hook_capture(model, generated["input_ids"])
                vec = pooled_response_vector(hook_tensor, generated["prompt_len"])
                np.save(shard_path, vec.astype(np.float32))
                coords = project(vec, basis)
                delta_bare = coords - bare
                delta_assistant = coords - assistant
                result.update(
                    {
                        "activation_time_seconds": round(time.time() - t1, 4),
                        "prompt_token_count": generated["prompt_len"],
                        "response_token_count": int(generated["input_ids"].shape[1] - generated["prompt_len"]),
                        "response_text": generated["response_text"],
                        "pc1": float(coords[0]),
                        "pc2": float(coords[1]),
                        "pc3": float(coords[2]),
                        "delta_bare_qwen_pc1": float(delta_bare[0]),
                        "delta_bare_qwen_pc2": float(delta_bare[1]),
                        "delta_bare_qwen_pc3": float(delta_bare[2]),
                        "delta_assistant_pc1": float(delta_assistant[0]),
                        "delta_assistant_pc2": float(delta_assistant[1]),
                        "delta_assistant_pc3": float(delta_assistant[2]),
                    }
                )
            except Exception as exc:
                result.update(
                    {
                        "generation_time_seconds": result.get("generation_time_seconds", ""),
                        "activation_time_seconds": "",
                        "prompt_token_count": "",
                        "response_token_count": "",
                        "response_text": "",
                        "pc1": "",
                        "pc2": "",
                        "pc3": "",
                        "delta_bare_qwen_pc1": "",
                        "delta_bare_qwen_pc2": "",
                        "delta_bare_qwen_pc3": "",
                        "delta_assistant_pc1": "",
                        "delta_assistant_pc2": "",
                        "delta_assistant_pc3": "",
                        "error_flag": repr(exc),
                    }
                )
            append_csv(OUT_DIR / "response_level_results.csv", result, RESPONSE_FIELDS)
            append_jsonl(OUT_DIR / "generation_log.jsonl", result)
            completed.add(response_id)
            heartbeat = {
                "updated_utc": now_iso(),
                "completed_responses": len(completed),
                "planned_responses": total,
                "last_response_id": response_id,
                "last_error_flag": result["error_flag"],
                "elapsed_seconds": round(time.time() - started, 1),
            }
            write_json(OUT_DIR / "heartbeat.json", heartbeat)
            print(f"{len(completed)}/{total} {response_id} err={result['error_flag']}", flush=True)


def ffloat(value: Any) -> float:
    if value in {"", None}:
        return float("nan")
    return float(value)


def ci95(values: list[float]) -> tuple[float, float]:
    arr = np.array(values, dtype=float)
    if len(arr) <= 1:
        return (float("nan"), float("nan"))
    mean = float(arr.mean())
    se = float(arr.std(ddof=1) / math.sqrt(len(arr)))
    return mean - 1.96 * se, mean + 1.96 * se


def bootstrap_diff_ci(a_vals: np.ndarray, b_vals: np.ndarray, seed: int = BOOTSTRAP_SEED, n: int = 5000) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n):
        a = rng.choice(a_vals, size=len(a_vals), replace=True)
        b = rng.choice(b_vals, size=len(b_vals), replace=True)
        diffs.append(float(b.mean() - a.mean()))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi)


def analyze(catalog: list[dict[str, Any]], allow_incomplete: bool = False) -> dict[str, Any]:
    path = OUT_DIR / "response_level_results.csv"
    if not path.exists():
        raise RuntimeError("Missing response_level_results.csv")
    rows = read_csv(path)
    successful = [r for r in rows if not r.get("error_flag")]
    planned = sum(int(r["sample_count"]) for r in catalog)
    if len(successful) != planned and not allow_incomplete:
        raise RuntimeError(f"Expected {planned} successful rows, found {len(successful)}")
    meta_by_id = {r["prompt_id"]: r for r in catalog}
    by_prompt: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in successful:
        by_prompt[r["prompt_id"]].append(r)

    prompt_means = []
    for prompt_id, rs in sorted(by_prompt.items()):
        meta = meta_by_id[prompt_id]
        coords = np.array([[ffloat(r["pc1"]), ffloat(r["pc2"]), ffloat(r["pc3"])] for r in rs])
        db = np.array([[ffloat(r["delta_bare_qwen_pc1"]), ffloat(r["delta_bare_qwen_pc2"]), ffloat(r["delta_bare_qwen_pc3"])] for r in rs])
        da = np.array([[ffloat(r["delta_assistant_pc1"]), ffloat(r["delta_assistant_pc2"]), ffloat(r["delta_assistant_pc3"])] for r in rs])
        prompt_means.append(
            {
                **{k: meta[k] for k in CATALOG_FIELDS},
                "n_successful": len(rs),
                "mean_pc1": float(coords[:, 0].mean()),
                "mean_pc2": float(coords[:, 1].mean()),
                "mean_pc3": float(coords[:, 2].mean()),
                "std_pc1": float(coords[:, 0].std(ddof=1)) if len(rs) > 1 else float("nan"),
                "std_pc2": float(coords[:, 1].std(ddof=1)) if len(rs) > 1 else float("nan"),
                "std_pc3": float(coords[:, 2].std(ddof=1)) if len(rs) > 1 else float("nan"),
                "mean_delta_bare_qwen_pc1": float(db[:, 0].mean()),
                "mean_delta_bare_qwen_pc2": float(db[:, 1].mean()),
                "mean_delta_bare_qwen_pc3": float(db[:, 2].mean()),
                "mean_delta_assistant_pc1": float(da[:, 0].mean()),
                "mean_delta_assistant_pc2": float(da[:, 1].mean()),
                "mean_delta_assistant_pc3": float(da[:, 2].mean()),
            }
        )
    write_csv(OUT_DIR / "prompt_means.csv", prompt_means)

    prompt_mean_by_id = {r["prompt_id"]: r for r in prompt_means}
    rows_by_prompt = {pid: rs for pid, rs in by_prompt.items()}
    pairwise = []
    for experiment in ["accountability_vs_determination", "accountability_vs_arithmetic"]:
        pair_ids = sorted({r["pair_id"] for r in catalog if r["experiment"] == experiment})
        for pair_id in pair_ids:
            a_id = f"{experiment}_{pair_id}_A"
            b_id = f"{experiment}_{pair_id}_B"
            a_mean = prompt_mean_by_id[a_id]
            b_mean = prompt_mean_by_id[b_id]
            a_rows = rows_by_prompt[a_id]
            b_rows = rows_by_prompt[b_id]
            out = {
                "experiment": experiment,
                "pair_id": pair_id,
                "a_prompt_id": a_id,
                "b_prompt_id": b_id,
                "a_version_label": a_mean["version_label"],
                "b_version_label": b_mean["version_label"],
                "n_a": len(a_rows),
                "n_b": len(b_rows),
            }
            for pc in [1, 2, 3]:
                a_vals = np.array([ffloat(r[f"pc{pc}"]) for r in a_rows])
                b_vals = np.array([ffloat(r[f"pc{pc}"]) for r in b_rows])
                diff = float(b_vals.mean() - a_vals.mean())
                lo, hi = bootstrap_diff_ci(a_vals, b_vals, seed=BOOTSTRAP_SEED + pc + len(pairwise) * 10)
                out[f"b_minus_a_pc{pc}"] = diff
                out[f"b_minus_a_pc{pc}_ci95_low"] = lo
                out[f"b_minus_a_pc{pc}_ci95_high"] = hi
            out["pass_pc1"] = out["b_minus_a_pc1"] > 0
            out["secondary_negative_pc2"] = out["b_minus_a_pc2"] < 0
            pairwise.append(out)
    write_csv(OUT_DIR / "pairwise_effects.csv", pairwise)

    summary = []
    for experiment in ["accountability_vs_determination", "accountability_vs_arithmetic"]:
        rs = [r for r in pairwise if r["experiment"] == experiment]
        for pc in [1, 2, 3]:
            vals = [float(r[f"b_minus_a_pc{pc}"]) for r in rs]
            lo, hi = ci95(vals)
            summary.append(
                {
                    "experiment": experiment,
                    "metric": f"pair_mean_b_minus_a_pc{pc}",
                    "n_pairs": len(vals),
                    "mean_effect": float(np.mean(vals)),
                    "ci95_low": lo,
                    "ci95_high": hi,
                    "positive_pair_count": sum(v > 0 for v in vals),
                    "negative_pair_count": sum(v < 0 for v in vals),
                }
            )
    write_csv(OUT_DIR / "experiment_summary.csv", summary)
    write_report(rows, successful, planned, prompt_means, pairwise, summary)
    write_inventory()
    return {"successful": len(successful), "planned": planned, "errors": len(rows) - len(successful)}


def write_report(
    response_rows: list[dict[str, str]],
    successful: list[dict[str, str]],
    planned: int,
    prompt_means: list[dict[str, Any]],
    pairwise: list[dict[str, Any]],
    summary: list[dict[str, Any]],
) -> None:
    err_count = len(response_rows) - len(successful)
    summary_lookup = {(r["experiment"], r["metric"]): r for r in summary}

    def fmt(x: Any) -> str:
        try:
            return f"{float(x):.3f}"
        except Exception:
            return ""

    lines = [
        "# PC1 Accountability Validation Report",
        "",
        f"model_used: {SCRIPT_AUTHOR_MODEL}",
        "",
        "## Startup Status",
        "",
        "Startup verification was performed before this run in the coordinating Codex session using the canonical raw startup files listed in `research/STARTUP_MANIFEST.md`.",
        "",
        "## Measurement Protocol",
        "",
        "- Model: Qwen/Qwen3-32B",
        "- Layer: 48",
        "- Activation source: direct forward hook on `model.model.layers[48]`",
        "- Pooling: mean over generated assistant response tokens only",
        "- PCA basis: same reconstructed Qwen persona PCA basis and sign alignment as Run 2",
        "- Conversation protocol: one fresh user message per sample, no system prompt, no prior history",
        "- Extraction pass: separate no-cache forward pass over the generated sequence",
        "- Model-visible text: prompt text only; prompt IDs, experiment labels, pair labels, PC labels, hypotheses, and metadata were not visible to Qwen",
        "",
        "## Run Integrity",
        "",
        f"- Planned generations: {planned}",
        f"- Successful generations: {len(successful)}",
        f"- Error count: {err_count}",
        "",
        "## Experiment A: Accountability vs Determination",
        "",
        "| pair | B-A PC1 | 95% CI | pass | B-A PC2 | secondary negative PC2 |",
        "|---|---:|---:|---|---:|---|",
    ]
    for r in [x for x in pairwise if x["experiment"] == "accountability_vs_determination"]:
        lines.append(
            f"| {r['pair_id']} | {fmt(r['b_minus_a_pc1'])} | [{fmt(r['b_minus_a_pc1_ci95_low'])}, {fmt(r['b_minus_a_pc1_ci95_high'])}] | {r['pass_pc1']} | {fmt(r['b_minus_a_pc2'])} | {r['secondary_negative_pc2']} |"
        )
    s = summary_lookup[("accountability_vs_determination", "pair_mean_b_minus_a_pc1")]
    s2 = summary_lookup[("accountability_vs_determination", "pair_mean_b_minus_a_pc2")]
    lines += [
        "",
        f"Mean B-A PC1 effect across pairs: {fmt(s['mean_effect'])} with 95% CI [{fmt(s['ci95_low'])}, {fmt(s['ci95_high'])}]. Positive pairs: {s['positive_pair_count']}/{s['n_pairs']}.",
        f"Mean B-A PC2 effect across pairs: {fmt(s2['mean_effect'])}; negative-PC2 pairs: {s2['negative_pair_count']}/{s2['n_pairs']}.",
        "",
        "## Experiment B: Accountability vs Arithmetic/Checking",
        "",
        "| pair | B-A PC1 | 95% CI | pass | B-A PC2 | secondary negative PC2 |",
        "|---|---:|---:|---|---:|---|",
    ]
    for r in [x for x in pairwise if x["experiment"] == "accountability_vs_arithmetic"]:
        lines.append(
            f"| {r['pair_id']} | {fmt(r['b_minus_a_pc1'])} | [{fmt(r['b_minus_a_pc1_ci95_low'])}, {fmt(r['b_minus_a_pc1_ci95_high'])}] | {r['pass_pc1']} | {fmt(r['b_minus_a_pc2'])} | {r['secondary_negative_pc2']} |"
        )
    s = summary_lookup[("accountability_vs_arithmetic", "pair_mean_b_minus_a_pc1")]
    s2 = summary_lookup[("accountability_vs_arithmetic", "pair_mean_b_minus_a_pc2")]
    lines += [
        "",
        f"Mean B-A PC1 effect across pairs: {fmt(s['mean_effect'])} with 95% CI [{fmt(s['ci95_low'])}, {fmt(s['ci95_high'])}]. Positive pairs: {s['positive_pair_count']}/{s['n_pairs']}.",
        f"Mean B-A PC2 effect across pairs: {fmt(s2['mean_effect'])}; negative-PC2 pairs: {s2['negative_pair_count']}/{s2['n_pairs']}.",
        "",
        "## Prompt Means",
        "",
        "See `prompt_means.csv` for per-version PC1/PC2/PC3 means and deltas relative to both the Run 2 bare-Qwen baseline and the released assistant-role centroid.",
        "",
        "## Interpretation Constraints",
        "",
        "This is a focused diagnostic, not Run 3. It tests whether accountability/scrutiny wording produces larger positive PC1 movement than determination or arithmetic/checking wording under matched scenarios. It does not by itself prove PC1 semantics, and it reuses the Run 2 baseline rather than regenerating it.",
        "",
    ]
    (OUT_DIR / "accountability_validation_report.md").write_text("\n".join(lines) + "\n")


def write_inventory() -> None:
    files = [
        "response_level_results.csv",
        "pairwise_effects.csv",
        "prompt_means.csv",
        "accountability_validation_report.md",
        "artifact_inventory.csv",
        "run_pc1_accountability_validation.py",
        "run_config.json",
        "prompt_catalog.csv",
        "experiment_summary.csv",
        "projection_basis_debug.json",
        "generation_log.jsonl",
        "heartbeat.json",
    ]
    rows = []
    for name in files:
        path = OUT_DIR / name
        if path.exists():
            rows.append(
                {
                    "path": rel(path),
                    "bytes": path.stat().st_size,
                    "status": "active",
                    "notes": "Focused PC1 accountability validation artifact",
                }
            )
    write_csv(OUT_DIR / "artifact_inventory.csv", rows)


def main() -> None:
    catalog = build_catalog()
    mode = os.environ.get("PC1_ACCOUNTABILITY_MODE", "run")
    if mode == "catalog":
        bare = load_bare_qwen_baseline()
        basis = load_role_vectors_and_basis()
        write_run_config(catalog, bare, basis["assistant"])
        write_inventory()
        return
    run_generation(catalog)
    analyze(catalog)


if __name__ == "__main__":
    main()
