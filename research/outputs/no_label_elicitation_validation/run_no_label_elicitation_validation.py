#!/usr/bin/env python3
"""Run the no-label elicitation validation experiment for Qwen/Qwen3-32B.

The model-visible prompt for each sample is intentionally restricted to the
frozen packet's prompt_text field. Metadata is used only after generation for
analysis and is never serialized into the chat messages.
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


REPO_ROOT = Path(os.environ.get("ASSISTANT_AXIS_REPO", "/root/assistant-axis"))
OUT_DIR = REPO_ROOT / "research/outputs/no_label_elicitation_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_CSV = REPO_ROOT / "research/outputs/no_label_elicitation_prompt_packet_v1/no_label_elicitation_prompts_v1.csv"
PROMPT_JSON = REPO_ROOT / "research/outputs/no_label_elicitation_prompt_packet_v1/no_label_elicitation_prompts_v1.json"
PROMPT_REPORT = REPO_ROOT / "research/outputs/no_label_elicitation_prompt_packet_v1/no_label_elicitation_prompt_packet_report.md"
GEOMETRY_PATH = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
VECTOR_ROOT = REPO_ROOT / "downloads/hf_vectors"
VECTOR_FOLDER = "qwen-3-32b"
VECTOR_DIR = VECTOR_ROOT / VECTOR_FOLDER / "role_vectors"
CANONICAL_PCA_PATH = REPO_ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"

MODEL_ID = "Qwen/Qwen3-32B"
DATASET_ID = "lu-christina/assistant-axis-vectors"
LAYER = 48
REPEATS_PER_PROMPT = int(os.environ.get("REPEATS_PER_PROMPT", "10"))
MAX_NEW_TOKENS = int(os.environ.get("MAX_NEW_TOKENS", "300"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
TOP_P = float(os.environ.get("TOP_P", "0.9"))
DO_SAMPLE = os.environ.get("DO_SAMPLE", "1") not in {"0", "false", "False"}
BASE_SEED = int(os.environ.get("BASE_SEED", "20260609"))
SUCCESS_THRESHOLD = 0.70

EXPECTED_IDS = (
    [f"pc1_pos_{i:02d}" for i in range(1, 11)]
    + [f"pc1_neg_{i:02d}" for i in range(1, 11)]
    + [f"pc2_pos_{i:02d}" for i in range(1, 11)]
    + [f"pc2_neg_{i:02d}" for i in range(1, 11)]
    + [f"pc3_pos_{i:02d}" for i in range(1, 11)]
    + [f"pc3_neg_{i:02d}" for i in range(1, 11)]
)

RESPONSE_FIELDS = [
    "response_id",
    "prompt_id",
    "repeat_index",
    "pc",
    "polarity",
    "family",
    "target_axis",
    "predicted_sign",
    "seed",
    "model_id",
    "layer",
    "activation_source",
    "model_visible_user_prompt_sha256",
    "model_visible_message_count",
    "model_visible_roles",
    "prompt_token_count",
    "response_token_count",
    "generation_time_seconds",
    "activation_time_seconds",
    "generated_response",
    "pc1",
    "pc2",
    "pc3",
    "assistant_baseline_pc1",
    "assistant_baseline_pc2",
    "assistant_baseline_pc3",
    "delta_pc1",
    "delta_pc2",
    "delta_pc3",
    "target_axis_delta",
    "target_axis_success",
    "euclidean_delta_from_assistant",
    "nearest_role",
    "nearest_role_distance",
    "error_flag",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


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
        for row in rows:
            writer.writerow(row)


def append_csv(path: Path, row: dict[str, Any], fieldnames: list[str]) -> None:
    exists = path.exists()
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def target_axis(pc: str) -> str:
    return f"delta_{pc.lower()}"


def predicted_sign(polarity: str) -> int:
    return 1 if polarity == "positive" else -1


def validate_prompt_packet() -> list[dict[str, str]]:
    missing = [str(p) for p in [PROMPT_CSV, PROMPT_JSON, PROMPT_REPORT] if not p.exists()]
    if missing:
        raise RuntimeError(f"Frozen prompt packet incomplete; missing files: {missing}")
    rows = read_csv(PROMPT_CSV)
    json_rows = json.loads(PROMPT_JSON.read_text())
    if len(rows) != 60 or len(json_rows) != 60:
        raise RuntimeError(f"Frozen prompt packet must contain 60 prompts; csv={len(rows)} json={len(json_rows)}")
    ids = [r["prompt_id"] for r in rows]
    if ids != EXPECTED_IDS:
        raise RuntimeError("Frozen prompt packet IDs/order do not match expected canonical v1 IDs")
    required = {"prompt_id", "pc", "polarity", "family", "prompt_text", "family_reasoning", "source_note"}
    for row in rows:
        missing_cols = required - set(row)
        if missing_cols:
            raise RuntimeError(f"Missing required columns: {sorted(missing_cols)}")
        if not row["prompt_text"].strip():
            raise RuntimeError(f"Empty prompt_text for {row['prompt_id']}")
        if row["pc"] not in {"PC1", "PC2", "PC3"}:
            raise RuntimeError(f"Invalid PC for {row['prompt_id']}: {row['pc']}")
        if row["polarity"] not in {"positive", "negative"}:
            raise RuntimeError(f"Invalid polarity for {row['prompt_id']}: {row['polarity']}")
    write_csv(OUT_DIR / "prompt_catalog_used.csv", rows)
    return rows


def write_preflight_documents(prompt_rows: list[dict[str, str]]) -> None:
    manifest = {
        "experiment": "Paper 1.5 no-label elicitation validation",
        "status": "prepared",
        "created_utc": now_iso(),
        "model_id": MODEL_ID,
        "layer": LAYER,
        "activation_source": "direct forward hook on model.model.layers[48]",
        "target_geometry": "Qwen/Qwen3-32B persona PCA space",
        "baseline": "published assistant role-vector centroid projected into the same PCA basis",
        "frozen_prompt_packet": {
            "csv": str(PROMPT_CSV.relative_to(REPO_ROOT)),
            "json": str(PROMPT_JSON.relative_to(REPO_ROOT)),
            "report": str(PROMPT_REPORT.relative_to(REPO_ROOT)),
            "csv_sha256": sha256_file(PROMPT_CSV),
            "json_sha256": sha256_file(PROMPT_JSON),
            "report_sha256": sha256_file(PROMPT_REPORT),
            "prompt_count": len(prompt_rows),
        },
        "design": {
            "families": 6,
            "prompts_per_family": 10,
            "repeats_per_prompt": REPEATS_PER_PROMPT,
            "planned_response_count": len(prompt_rows) * REPEATS_PER_PROMPT,
            "success_unit": "prompt mean",
            "family_success_threshold": SUCCESS_THRESHOLD,
        },
        "generation_settings": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "do_sample": DO_SAMPLE,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "base_seed": BASE_SEED,
            "thinking_disabled": True,
        },
        "blinding": {
            "model_visible_fields": ["prompt_text"],
            "metadata_excluded": [
                "prompt_id",
                "pc",
                "polarity",
                "family",
                "family_reasoning",
                "source_note",
                "predictions",
                "success_criteria",
                "PCA/geometry/axis labels",
            ],
        },
    }
    write_json(OUT_DIR / "experiment_manifest.json", manifest)

    (OUT_DIR / "prompt_blinding_verification.md").write_text(
        "\n".join(
            [
                "# Prompt Blinding Verification",
                "",
                f"- Verified UTC: {now_iso()}",
                f"- Frozen prompt source: `{PROMPT_CSV.relative_to(REPO_ROOT)}`",
                "- The generation loop constructs exactly one chat message per sample: `{'role': 'user', 'content': prompt_text}`.",
                "- The model-visible user content is read only from the frozen packet's `prompt_text` column.",
                "- `prompt_id`, PC labels, polarity labels, family labels, reasoning paragraphs, source notes, predictions, success criteria, and analysis metadata are never inserted into `messages`.",
                "- No system prompt is added by this runner.",
                "- The Qwen chat template is applied with `add_generation_prompt=True` and `enable_thinking=False` when supported by Transformers.",
                "- Analysis metadata is joined back only after generation and activation projection.",
                "",
                "Status: pass, conditional on using this script without modification.",
                "",
            ]
        )
    )
    (OUT_DIR / "generation_independence_verification.md").write_text(
        "\n".join(
            [
                "# Generation Independence Verification",
                "",
                f"- Verified UTC: {now_iso()}",
                "- Each generation call creates a fresh `messages` list containing only the current sample's user prompt.",
                "- No previous user prompts are included.",
                "- No previous assistant responses are included.",
                "- The script does not pass `past_key_values` between generations.",
                "- The script generates samples sequentially; it does not concatenate examples into a batch.",
                "- The generation call may use KV cache internally for the current sample only (`use_cache=True`).",
                "- Activation extraction is a separate full forward pass over only the current generated sequence with `use_cache=False`.",
                "- Repeated samples of the same prompt receive distinct seeds and independent generation calls.",
                "- Different prompts receive distinct seeds and independent generation calls.",
                "",
                "Status: pass, conditional on using this script without modification.",
                "",
            ]
        )
    )


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
        r["persona"]: np.array(
            [float(r["activation_pc1"]), float(r["activation_pc2"]), float(r["activation_pc3"])],
            dtype=np.float64,
        )
        for r in canonical_rows
    }
    names = sorted(p.stem for p in VECTOR_DIR.glob("*.pt"))
    vectors = []
    for name in names:
        tensor = torch.load(VECTOR_DIR / f"{name}.pt", map_location="cpu").float()
        if tensor.ndim == 2:
            vec = tensor.mean(0)
        elif tensor.ndim == 1:
            vec = tensor
        else:
            raise RuntimeError(f"Unexpected role vector shape for {name}: {tuple(tensor.shape)}")
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
    if float(abs_err.max()) > 1e-5:
        raise RuntimeError(f"PCA reproduction error too high: {float(abs_err.max())}")
    assistant_idx = names.index("assistant")
    debug = {
        "basis_source": "reconstructed_from_canonical_qwen_role_vectors_with_sign_alignment",
        "vector_dir": str(VECTOR_DIR.relative_to(REPO_ROOT)),
        "canonical_pca_path": str(CANONICAL_PCA_PATH.relative_to(REPO_ROOT)),
        "n_roles_used": len(names),
        "role_vector_shape": list(x.shape),
        "sign_alignment": signs,
        "max_abs_coordinate_reproduction_error": float(abs_err.max()),
        "mean_abs_coordinate_reproduction_error": float(abs_err.mean()),
        "assistant_baseline_pc1": float(reconstructed[assistant_idx, 0]),
        "assistant_baseline_pc2": float(reconstructed[assistant_idx, 1]),
        "assistant_baseline_pc3": float(reconstructed[assistant_idx, 2]),
    }
    write_json(OUT_DIR / "projection_basis_debug.json", debug)
    return {
        "mean": mean,
        "components": components,
        "debug": debug,
        "role_names": names,
        "role_pca": reconstructed,
        "assistant_baseline": reconstructed[assistant_idx],
    }


def project(vec: np.ndarray, basis: dict[str, Any]) -> np.ndarray:
    return (vec.astype(np.float64) - basis["mean"]) @ basis["components"].T


def nearest_role(coords: np.ndarray, basis: dict[str, Any]) -> tuple[str, float]:
    distances = np.linalg.norm(basis["role_pca"] - coords[None, :], axis=1)
    idx = int(np.argmin(distances))
    return str(basis["role_names"][idx]), float(distances[idx])


def make_messages(prompt_text: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": prompt_text}]


def apply_template(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    try:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def tokenize_prompt(tokenizer: Any, prompt_text: str, device: Any) -> tuple[dict[str, Any], int, list[dict[str, str]]]:
    messages = make_messages(prompt_text)
    rendered = apply_template(tokenizer, messages)
    inputs = tokenizer(rendered, return_tensors="pt").to(device)
    return inputs, int(inputs["input_ids"].shape[1]), messages


def generate_tokens(tokenizer: Any, model: Any, prompt_text: str, seed: int) -> dict[str, Any]:
    import torch

    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    inputs, prompt_len, messages = tokenize_prompt(tokenizer, prompt_text, model.device)
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
    response_text = tokenizer.decode(response_tokens, skip_special_tokens=True).strip()
    return {
        "input_ids": generated,
        "prompt_len": prompt_len,
        "messages": messages,
        "response_text": response_text,
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


def run_generation(prompt_rows: list[dict[str, str]]) -> None:
    tokenizer, model = load_model_and_tokenizer()
    basis = load_role_vectors_and_basis()
    assistant = basis["assistant_baseline"]
    completed = existing_response_ids()
    total = len(prompt_rows) * REPEATS_PER_PROMPT
    started = time.time()
    for prompt_index, row in enumerate(prompt_rows):
        pc = row["pc"].lower()
        sign = predicted_sign(row["polarity"])
        axis_key = target_axis(row["pc"])
        for repeat_idx in range(REPEATS_PER_PROMPT):
            response_id = f"{row['prompt_id']}_r{repeat_idx:02d}"
            if response_id in completed:
                continue
            seed = BASE_SEED + prompt_index * 100 + repeat_idx
            result: dict[str, Any] = {
                "response_id": response_id,
                "prompt_id": row["prompt_id"],
                "repeat_index": repeat_idx,
                "pc": row["pc"],
                "polarity": row["polarity"],
                "family": row["family"],
                "target_axis": axis_key,
                "predicted_sign": sign,
                "seed": seed,
                "model_id": MODEL_ID,
                "layer": LAYER,
                "activation_source": "model.model.layers[48] direct forward hook",
                "model_visible_user_prompt_sha256": sha256_text(row["prompt_text"]),
                "model_visible_message_count": 1,
                "model_visible_roles": "user",
                "error_flag": "",
            }
            try:
                t0 = time.time()
                generated = generate_tokens(tokenizer, model, row["prompt_text"], seed)
                result["generation_time_seconds"] = round(time.time() - t0, 4)
                t1 = time.time()
                hook_tensor = full_forward_hook_capture(model, generated["input_ids"])
                vec = pooled_response_vector(hook_tensor, generated["prompt_len"])
                result["activation_time_seconds"] = round(time.time() - t1, 4)
                coords = project(vec, basis)
                deltas = coords - assistant
                nearest, nearest_dist = nearest_role(coords, basis)
                result.update(
                    {
                        "prompt_token_count": generated["prompt_len"],
                        "response_token_count": int(generated["input_ids"].shape[1] - generated["prompt_len"]),
                        "generated_response": generated["response_text"],
                        "pc1": float(coords[0]),
                        "pc2": float(coords[1]),
                        "pc3": float(coords[2]),
                        "assistant_baseline_pc1": float(assistant[0]),
                        "assistant_baseline_pc2": float(assistant[1]),
                        "assistant_baseline_pc3": float(assistant[2]),
                        "delta_pc1": float(deltas[0]),
                        "delta_pc2": float(deltas[1]),
                        "delta_pc3": float(deltas[2]),
                        "target_axis_delta": float(deltas[int(pc[-1]) - 1]),
                        "target_axis_success": bool(sign * deltas[int(pc[-1]) - 1] > 0),
                        "euclidean_delta_from_assistant": float(np.linalg.norm(deltas)),
                        "nearest_role": nearest,
                        "nearest_role_distance": nearest_dist,
                    }
                )
            except Exception as exc:
                result.update(
                    {
                        "prompt_token_count": "",
                        "response_token_count": "",
                        "generation_time_seconds": result.get("generation_time_seconds", ""),
                        "activation_time_seconds": "",
                        "generated_response": "",
                        "pc1": "",
                        "pc2": "",
                        "pc3": "",
                        "assistant_baseline_pc1": float(assistant[0]),
                        "assistant_baseline_pc2": float(assistant[1]),
                        "assistant_baseline_pc3": float(assistant[2]),
                        "delta_pc1": "",
                        "delta_pc2": "",
                        "delta_pc3": "",
                        "target_axis_delta": "",
                        "target_axis_success": "",
                        "euclidean_delta_from_assistant": "",
                        "nearest_role": "",
                        "nearest_role_distance": "",
                        "error_flag": repr(exc),
                    }
                )
            append_csv(OUT_DIR / "response_level_results.csv", result, RESPONSE_FIELDS)
            completed.add(response_id)
            heartbeat = {
                "updated_utc": now_iso(),
                "completed_responses": len(completed),
                "planned_responses": total,
                "elapsed_seconds": round(time.time() - started, 1),
                "last_response_id": response_id,
                "last_error_flag": result["error_flag"],
            }
            write_json(OUT_DIR / "run_heartbeat.json", heartbeat)
            print(f"{len(completed)}/{total} {response_id} target_delta={result.get('target_axis_delta')} err={result['error_flag']}", flush=True)


def ffloat(value: Any) -> float:
    if value == "" or value is None:
        return float("nan")
    return float(value)


def summarize_results(prompt_rows: list[dict[str, str]]) -> dict[str, Any]:
    response_path = OUT_DIR / "response_level_results.csv"
    if not response_path.exists():
        raise RuntimeError("Missing response_level_results.csv; generation did not run")
    rows = [r for r in read_csv(response_path) if not r.get("error_flag")]
    if len(rows) != len(prompt_rows) * REPEATS_PER_PROMPT:
        raise RuntimeError(f"Expected 600 successful rows, found {len(rows)}")
    by_prompt: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_prompt[row["prompt_id"]].append(row)

    prompt_means = []
    for meta in prompt_rows:
        rs = by_prompt[meta["prompt_id"]]
        sign = predicted_sign(meta["polarity"])
        pc_num = int(meta["pc"][-1])
        deltas = np.array([[ffloat(r["delta_pc1"]), ffloat(r["delta_pc2"]), ffloat(r["delta_pc3"])] for r in rs])
        coords = np.array([[ffloat(r["pc1"]), ffloat(r["pc2"]), ffloat(r["pc3"])] for r in rs])
        target_delta_mean = float(deltas[:, pc_num - 1].mean())
        abs_off_axis = [abs(float(deltas[:, i].mean())) for i in range(3) if i != pc_num - 1]
        prompt_means.append(
            {
                "prompt_id": meta["prompt_id"],
                "pc": meta["pc"],
                "polarity": meta["polarity"],
                "family": meta["family"],
                "n_responses": len(rs),
                "target_axis": f"delta_pc{pc_num}",
                "predicted_sign": sign,
                "mean_pc1": float(coords[:, 0].mean()),
                "mean_pc2": float(coords[:, 1].mean()),
                "mean_pc3": float(coords[:, 2].mean()),
                "mean_delta_pc1": float(deltas[:, 0].mean()),
                "mean_delta_pc2": float(deltas[:, 1].mean()),
                "mean_delta_pc3": float(deltas[:, 2].mean()),
                "std_delta_pc1": float(deltas[:, 0].std(ddof=1)),
                "std_delta_pc2": float(deltas[:, 1].std(ddof=1)),
                "std_delta_pc3": float(deltas[:, 2].std(ddof=1)),
                "target_axis_delta_mean": target_delta_mean,
                "target_axis_success": bool(sign * target_delta_mean > 0),
                "response_level_target_success_rate": float(np.mean(sign * deltas[:, pc_num - 1] > 0)),
                "mean_euclidean_delta": float(np.linalg.norm(deltas, axis=1).mean()),
                "max_abs_off_axis_mean_delta": float(max(abs_off_axis)),
                "off_axis_to_target_abs_ratio": float(max(abs_off_axis) / (abs(target_delta_mean) + 1e-12)),
            }
        )
    write_csv(OUT_DIR / "prompt_mean_results.csv", prompt_means)

    by_family: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in prompt_means:
        by_family[(row["pc"], row["polarity"], row["family"])].append(row)

    family_means = []
    success_rows = []
    for (pc, polarity, family), prs in sorted(by_family.items()):
        sign = predicted_sign(polarity)
        pc_num = int(pc[-1])
        prompt_success_count = sum(1 for r in prs if r["target_axis_success"])
        success_rate = prompt_success_count / len(prs)
        row = {
            "pc": pc,
            "polarity": polarity,
            "family": family,
            "target_axis": f"delta_pc{pc_num}",
            "predicted_sign": sign,
            "n_prompts": len(prs),
            "n_responses": sum(int(r["n_responses"]) for r in prs),
            "mean_delta_pc1": float(np.mean([r["mean_delta_pc1"] for r in prs])),
            "mean_delta_pc2": float(np.mean([r["mean_delta_pc2"] for r in prs])),
            "mean_delta_pc3": float(np.mean([r["mean_delta_pc3"] for r in prs])),
            "target_axis_mean_delta": float(np.mean([r["target_axis_delta_mean"] for r in prs])),
            "prompt_success_count": prompt_success_count,
            "prompt_success_rate": float(success_rate),
            "family_pass_70pct_threshold": bool(success_rate >= SUCCESS_THRESHOLD),
        }
        family_means.append(row)
        success_rows.append(
            {
                "family": family,
                "pc": pc,
                "polarity": polarity,
                "criterion": f"{pc} {polarity} prompt means move {'>' if sign > 0 else '<'} 0 on target axis",
                "minimum_success_rate": SUCCESS_THRESHOLD,
                "observed_success_rate": float(success_rate),
                "prompt_success_count": prompt_success_count,
                "n_prompts": len(prs),
                "pass": bool(success_rate >= SUCCESS_THRESHOLD),
            }
        )
    write_csv(OUT_DIR / "family_mean_results.csv", family_means)
    write_csv(OUT_DIR / "geometric_success_summary.csv", success_rows)

    off_axis_rows = []
    for row in prompt_means:
        pc_num = int(row["pc"][-1])
        target_abs = abs(row["target_axis_delta_mean"])
        for i in [1, 2, 3]:
            if i == pc_num:
                continue
            delta = row[f"mean_delta_pc{i}"]
            off_axis_rows.append(
                {
                    "prompt_id": row["prompt_id"],
                    "family": row["family"],
                    "target_pc": row["pc"],
                    "polarity": row["polarity"],
                    "off_axis": f"PC{i}",
                    "mean_off_axis_delta": delta,
                    "abs_mean_off_axis_delta": abs(delta),
                    "target_axis_delta_mean": row["target_axis_delta_mean"],
                    "off_axis_to_target_abs_ratio": abs(delta) / (target_abs + 1e-12),
                    "target_axis_success": row["target_axis_success"],
                }
            )
    off_axis_rows.sort(key=lambda r: r["abs_mean_off_axis_delta"], reverse=True)
    write_csv(OUT_DIR / "off_axis_effects.csv", off_axis_rows)

    outliers = []
    by_family_prompt = defaultdict(list)
    for row in prompt_means:
        by_family_prompt[row["family"]].append(row)
    for family, prs in by_family_prompt.items():
        strongest = max(prs, key=lambda r: predicted_sign(r["polarity"]) * r["target_axis_delta_mean"])
        weakest = min(prs, key=lambda r: predicted_sign(r["polarity"]) * r["target_axis_delta_mean"])
        outliers.append({"family": family, "case_type": "strongest_target_movement", **strongest})
        outliers.append({"family": family, "case_type": "weakest_target_movement", **weakest})
    for row in sorted(prompt_means, key=lambda r: r["max_abs_off_axis_mean_delta"], reverse=True)[:12]:
        outliers.append({"family": row["family"], "case_type": "largest_off_axis_movement", **row})
    write_csv(OUT_DIR / "outlier_prompt_analysis.csv", outliers)

    make_plots(prompt_means, family_means, success_rows)
    write_report(prompt_rows, family_means, success_rows, prompt_means, off_axis_rows, outliers)
    write_artifact_inventory()
    return {"families": family_means, "success": success_rows}


def make_plots(prompt_rows: list[dict[str, Any]], family_rows: list[dict[str, Any]], success_rows: list[dict[str, Any]]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [f"{r['pc']} {r['polarity']}" for r in family_rows]
    x = np.arange(len(labels))
    vals = np.array([[r["mean_delta_pc1"], r["mean_delta_pc2"], r["mean_delta_pc3"]] for r in family_rows])
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.25
    ax.bar(x - width, vals[:, 0], width, label="delta PC1")
    ax.bar(x, vals[:, 1], width, label="delta PC2")
    ax.bar(x + width, vals[:, 2], width, label="delta PC3")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Mean displacement from assistant baseline")
    ax.set_title("Family mean displacement")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "family_mean_displacement_plot.png", dpi=180)
    plt.close(fig)

    p_labels = [r["prompt_id"] for r in prompt_rows]
    target = [r["target_axis_delta_mean"] for r in prompt_rows]
    colors = ["#2ca02c" if r["target_axis_success"] else "#d62728" for r in prompt_rows]
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(np.arange(len(prompt_rows)), target, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(np.arange(len(prompt_rows)))
    ax.set_xticklabels(p_labels, rotation=90, fontsize=7)
    ax.set_ylabel("Prompt mean target-axis displacement")
    ax.set_title("Prompt mean target-axis displacement")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "prompt_mean_displacement_plot.png", dpi=180)
    plt.close(fig)

    for a, b in [(1, 2), (1, 3), (2, 3)]:
        fig, ax = plt.subplots(figsize=(7, 6))
        for family in sorted(set(r["family"] for r in prompt_rows)):
            subset = [r for r in prompt_rows if r["family"] == family]
            ax.scatter([r[f"mean_delta_pc{a}"] for r in subset], [r[f"mean_delta_pc{b}"] for r in subset], label=family, alpha=0.8)
        ax.axhline(0, color="black", linewidth=0.7)
        ax.axvline(0, color="black", linewidth=0.7)
        ax.set_xlabel(f"Mean delta PC{a}")
        ax.set_ylabel(f"Mean delta PC{b}")
        ax.set_title(f"Prompt mean displacement: PC{a} x PC{b}")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(OUT_DIR / f"pc{a}_pc{b}_scatter_overlay.png", dpi=180)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    rates = [r["observed_success_rate"] for r in success_rows]
    ax.bar(labels, rates, color=["#2ca02c" if r["pass"] else "#d62728" for r in success_rows])
    ax.axhline(SUCCESS_THRESHOLD, color="black", linestyle="--", label="70% threshold")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Prompt-level success rate")
    ax.set_title("Family success rates")
    ax.tick_params(axis="x", rotation=35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "family_success_rate_figure.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4))
    ratios = [r["off_axis_to_target_abs_ratio"] for r in prompt_rows]
    ax.bar(np.arange(len(prompt_rows)), ratios, color="#9467bd")
    ax.axhline(1.0, color="black", linewidth=0.8)
    ax.set_xticks(np.arange(len(prompt_rows)))
    ax.set_xticklabels(p_labels, rotation=90, fontsize=7)
    ax.set_ylabel("Largest off-axis / target-axis abs ratio")
    ax.set_title("Off-axis movement by prompt")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "off_axis_movement_figure.png", dpi=180)
    plt.close(fig)


def md_table(rows: list[dict[str, Any]], cols: list[str]) -> list[str]:
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in rows:
        vals = []
        for col in cols:
            val = row.get(col, "")
            if isinstance(val, float):
                vals.append(f"{val:.3f}")
            else:
                vals.append(str(val))
        out.append("| " + " | ".join(vals) + " |")
    return out


def write_report(
    prompt_rows: list[dict[str, str]],
    family_rows: list[dict[str, Any]],
    success_rows: list[dict[str, Any]],
    prompt_means: list[dict[str, Any]],
    off_axis_rows: list[dict[str, Any]],
    outliers: list[dict[str, Any]],
) -> None:
    pass_count = sum(1 for r in success_rows if r["pass"])
    overall = "supports" if pass_count == len(success_rows) else "does not fully support"
    lines = [
        "# No-Label Elicitation Validation Report",
        "",
        "## 1. Motivation",
        "This experiment tests whether role-free user prompts designed from the first three Qwen persona-space PC interpretations produce predictable response-activation displacement from the published assistant centroid.",
        "",
        "## 2. Frozen Prompt Source",
        f"- CSV: `{PROMPT_CSV.relative_to(REPO_ROOT)}`",
        f"- JSON: `{PROMPT_JSON.relative_to(REPO_ROOT)}`",
        f"- Report: `{PROMPT_REPORT.relative_to(REPO_ROOT)}`",
        f"- Prompt count used: {len(prompt_rows)}",
        "",
        "## 3. Experimental Design",
        f"Six prompt families, ten prompts per family, and {REPEATS_PER_PROMPT} independent generations per prompt produced {len(prompt_rows) * REPEATS_PER_PROMPT} planned responses. Prompt means are the unit of success.",
        "",
        "## 4. Prompt Blinding Verification",
        "The model saw only `prompt_text`. PC labels, polarity labels, family labels, reasoning, metadata, and predictions were never included in model-visible prompts. The runner used one user message per sample and no system prompt.",
        "",
        "## 5. Generation Independence Verification",
        "Each sample was generated as a fresh conversation. No prior user prompts or assistant responses were included, no `past_key_values` were passed between samples, repeated samples used independent generation calls with distinct seeds, and activation extraction used a separate no-cache full forward pass for the current sample only.",
        "",
        "## 6. Success Criteria",
        "For each family, at least 70% of prompt means must move in the predicted direction on the target PC. Off-axis movement is reported as interpretation evidence, not as failure.",
        "",
        "## 7. Aggregate Results",
        f"Observed: {pass_count}/{len(success_rows)} families passed the preregistered 70% prompt-mean threshold. Overall, the experiment {overall} the modest predictive validation claim under the stated criterion.",
        "",
        "## 8. Family-Level Results",
        *md_table(success_rows, ["family", "pc", "polarity", "prompt_success_count", "n_prompts", "observed_success_rate", "pass"]),
        "",
        "Family mean displacement:",
        *md_table(family_rows, ["family", "pc", "polarity", "mean_delta_pc1", "mean_delta_pc2", "mean_delta_pc3", "target_axis_mean_delta"]),
        "",
        "## 9. Prompt-Level Results",
        "Strongest target-axis prompt means by family are preserved in `outlier_prompt_analysis.csv`; all prompt means are in `prompt_mean_results.csv`.",
        "",
        "## 10. Off-Axis Findings",
        "Largest off-axis prompt effects are listed in `off_axis_effects.csv`. These include prompts that succeeded on target axis while moving strongly on another PC, and prompts whose failure may indicate a coherent alternative interpretation.",
        "",
        "Top off-axis rows:",
        *md_table(off_axis_rows[:10], ["prompt_id", "family", "target_pc", "off_axis", "mean_off_axis_delta", "target_axis_delta_mean", "off_axis_to_target_abs_ratio"]),
        "",
        "## 11. Outlier Analysis",
        "Outlier prompt rows include strongest target movers, weakest target movers, and largest off-axis movers. See `outlier_prompt_analysis.csv`.",
        "",
        "## 12. Interpretation",
        "- Observed: family pass/fail status is determined by prompt means, not response-level majorities.",
        "- Inferred: passed families provide evidence that ordinary no-label task demands can move Qwen response activations in predicted persona-space directions.",
        "- Speculative: failed families or strong off-axis shifts may indicate that the prompt wording recruits a different local response register than intended.",
        "- Unknown: the experiment does not isolate a single causal semantic feature and does not prove the PC interpretations.",
        "",
        "## 13. Limitations",
        "This validates response-state movement for this frozen packet and measurement convention only. It does not prove the PCs, solve the geometry, validate human psychology, or show effects isolated to one axis.",
        "",
        "## 14. Future Work",
        "Use the response-level variance and outlier prompts to refine future no-label elicitation packets, and compare with within-role activation-cloud work before treating single-response displacement as a stable persona address.",
        "",
    ]
    (OUT_DIR / "no_label_elicitation_validation_report.md").write_text("\n".join(lines))


def write_artifact_inventory() -> None:
    rows = []
    for path in sorted(OUT_DIR.iterdir()):
        if path.is_file():
            rows.append(
                {
                    "path": str(path.relative_to(REPO_ROOT)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "created_or_updated_utc": now_iso(),
                }
            )
    write_csv(OUT_DIR / "artifact_inventory.csv", rows)


def main() -> None:
    prompt_rows = validate_prompt_packet()
    write_preflight_documents(prompt_rows)
    mode = os.environ.get("NO_LABEL_VALIDATION_MODE", "run").lower()
    if mode == "preflight":
        write_artifact_inventory()
        return
    if mode in {"run", "generate"}:
        run_generation(prompt_rows)
    summarize_results(prompt_rows)


if __name__ == "__main__":
    main()
