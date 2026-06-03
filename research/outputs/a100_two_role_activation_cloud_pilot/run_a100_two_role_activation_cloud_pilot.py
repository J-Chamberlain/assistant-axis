#!/usr/bin/env python3
"""Run boundary verification and a two-role activation-cloud pilot for Qwen/Qwen3-32B."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


REPO_ROOT = Path(os.environ.get("ASSISTANT_AXIS_REPO", "/root/assistant-axis"))
OUT_DIR = REPO_ROOT / "research/outputs/a100_two_role_activation_cloud_pilot"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = "Qwen/Qwen3-32B"
LAYER = 48
ROLES = ["amateur", "playwright"]
TARGET_GENERATIONS_PER_ROLE = int(os.environ.get("TARGET_GENERATIONS_PER_ROLE", "60"))
MAX_GENERATIONS_PER_ROLE_WITHOUT_CONFIRMATION = 100
QUESTION_COUNT_PER_INSTRUCTION = TARGET_GENERATIONS_PER_ROLE // 5
SEED = 20260603
MAX_NEW_TOKENS = 300
TEMPERATURE = 0.7
TOP_P = 0.9
DO_SAMPLE = True

GEOMETRY_PATH = REPO_ROOT / "research/visualizations/geometry_viz_data.json"
INSTRUCTION_DIR = REPO_ROOT / "data/roles/instructions"
QUESTIONS_PATH = REPO_ROOT / "data/extraction_questions.jsonl"
VECTOR_DIR = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b/role_vectors"
CANONICAL_PCA_PATH = REPO_ROOT / "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        return
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row.keys():
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_role_instructions(role: str) -> list[str]:
    path = INSTRUCTION_DIR / f"{role}.json"
    data = json.loads(path.read_text())
    instructions = [item["pos"].strip() for item in data["instruction"]]
    if len(instructions) != 5 or any(not x for x in instructions):
        raise RuntimeError(f"{role} expected exactly five non-empty positive instructions")
    return instructions


def load_questions() -> list[dict[str, Any]]:
    rows = []
    with QUESTIONS_PATH.open() as f:
        for idx, line in enumerate(f):
            obj = json.loads(line)
            question = obj.get("question") or obj.get("text")
            if not question:
                raise RuntimeError(f"Missing question text at line {idx}")
            rows.append({"question_id": idx, "question": question.strip(), **obj})
    if len(rows) != 240:
        raise RuntimeError(f"Expected 240 extraction questions, found {len(rows)}")
    return rows


def load_geometry() -> dict[str, Any]:
    data = json.loads(GEOMETRY_PATH.read_text())
    roles = data["roles"]
    out = {}
    for idx, role in enumerate(roles["names"]):
        pc1, pc2, pc3 = roles["pca3d"][idx]
        out[role] = {
            "role": role,
            "cluster": roles["clusters"][idx],
            "pc1": float(pc1),
            "pc2": float(pc2),
            "pc3": float(pc3),
        }
    for role in ROLES:
        if role not in out:
            raise RuntimeError(f"{role} missing from geometry")
    return out


def pearson(a: np.ndarray, b: np.ndarray) -> float | None:
    if len(a) < 2 or np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def load_role_vectors_and_basis() -> dict[str, Any]:
    if not VECTOR_DIR.exists():
        raise RuntimeError(f"Missing vector directory: {VECTOR_DIR}")
    canonical_rows = read_csv(CANONICAL_PCA_PATH)
    canonical = {
        r["persona"]: np.array(
            [float(r["activation_pc1"]), float(r["activation_pc2"]), float(r["activation_pc3"])],
            dtype=np.float64,
        )
        for r in canonical_rows
    }
    names = sorted([p.stem for p in VECTOR_DIR.glob("*.pt")])
    vectors = []
    for name in names:
        t = torch.load(VECTOR_DIR / f"{name}.pt", map_location="cpu").float()
        vec = t.mean(0) if t.dim() > 1 else t
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
    debug = {
        "basis_source": "reconstructed_from_canonical_qwen_role_vectors_with_sign_alignment",
        "vector_dir": str(VECTOR_DIR),
        "canonical_pca_path": str(CANONICAL_PCA_PATH),
        "n_roles_used": len(names),
        "n_roles_verified_against_committed_coordinates": len(verify_names),
        "role_vector_shape": list(x.shape),
        "sign_alignment": signs,
        "max_abs_coordinate_reproduction_error": float(abs_err.max()),
        "mean_abs_coordinate_reproduction_error": float(abs_err.mean()),
    }
    if debug["max_abs_coordinate_reproduction_error"] > 1e-5:
        raise RuntimeError(f"PCA reproduction error too high: {debug}")
    return {"mean": mean, "components": components, "debug": debug, "role_names": names, "role_vectors": x, "role_pca": reconstructed}


def project(vec: np.ndarray, basis: dict[str, Any]) -> np.ndarray:
    return (vec.astype(np.float64) - basis["mean"]) @ basis["components"].T


def nearest_role(coords: np.ndarray, basis: dict[str, Any]) -> tuple[str, float]:
    role_pca = basis["role_pca"]
    distances = np.linalg.norm(role_pca - coords[None, :], axis=1)
    idx = int(np.argmin(distances))
    return str(basis["role_names"][idx]), float(distances[idx])


def make_messages(system_instruction: str, question: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": system_instruction}, {"role": "user", "content": question}]


def apply_template(tokenizer: Any, messages: list[dict[str, str]]) -> str:
    try:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
    except TypeError:
        return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


def response_refusal_flag(text: str) -> bool:
    s = text.strip().lower()
    if len(s) < 8:
        return True
    return any(p in s[:300] for p in ["i can't help", "i cannot help", "i'm sorry", "as an ai", "cannot assist"])


def tokenize_prompt(tokenizer: Any, messages: list[dict[str, str]], device: Any) -> tuple[dict[str, torch.Tensor], int, str]:
    prompt = apply_template(tokenizer, messages)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    return inputs, int(inputs["input_ids"].shape[1]), prompt


def generate_tokens(tokenizer: Any, model: Any, messages: list[dict[str, str]], seed: int) -> dict[str, Any]:
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    inputs, prompt_len, prompt = tokenize_prompt(tokenizer, messages, model.device)
    with torch.no_grad():
        try:
            gen_out = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=DO_SAMPLE,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                pad_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )
        except TypeError:
            gen_out = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=DO_SAMPLE,
                temperature=TEMPERATURE,
                top_p=TOP_P,
                pad_token_id=tokenizer.eos_token_id,
                use_cache=True,
            )
    response_tokens = gen_out[0, prompt_len:]
    text = tokenizer.decode(response_tokens, skip_special_tokens=True).strip()
    return {"input_ids": gen_out, "prompt_len": prompt_len, "prompt": prompt, "response_text": text}


def full_forward_capture(model: Any, full_ids: torch.Tensor) -> dict[str, torch.Tensor]:
    captured = {}

    def hook_fn(_module: Any, _inp: Any, outp: Any) -> None:
        h = outp[0] if isinstance(outp, tuple) else outp
        captured["hook"] = h.detach().float().cpu()

    hook = model.model.layers[LAYER].register_forward_hook(hook_fn)
    try:
        with torch.no_grad():
            attention_mask = torch.ones_like(full_ids, device=full_ids.device)
            out = model(
                input_ids=full_ids,
                attention_mask=attention_mask,
                output_hidden_states=True,
                use_cache=False,
            )
    finally:
        hook.remove()
    if "hook" not in captured:
        raise RuntimeError("Layer hook did not capture output")
    return {
        "hook": captured["hook"],
        "hidden_states_48": out.hidden_states[48].detach().float().cpu(),
        "hidden_states_49": out.hidden_states[49].detach().float().cpu(),
    }


def pooled(tensor: torch.Tensor, prompt_len: int) -> np.ndarray:
    response = tensor[0, prompt_len:, :]
    if int(response.shape[0]) <= 0:
        raise RuntimeError("No response tokens available for pooling")
    return response.mean(dim=0).numpy().astype(np.float64)


def compare_vectors(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-12
    return {
        "cosine": float(np.dot(a, b) / denom),
        "l2_norm_difference": float(np.linalg.norm(a - b)),
        "max_abs_difference": float(np.max(np.abs(a - b))),
    }


def run_boundary_test(tokenizer: Any, model: Any, basis: dict[str, Any], instructions: dict[str, list[str]], questions: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    details = []
    for role_idx, role in enumerate(["playwright", "amateur"]):
        messages = make_messages(instructions[role][0], questions[0]["question"])
        generated = generate_tokens(tokenizer, model, messages, seed=SEED + role_idx)
        captures = full_forward_capture(model, generated["input_ids"])
        hook_vec = pooled(captures["hook"], generated["prompt_len"])
        hs48_vec = pooled(captures["hidden_states_48"], generated["prompt_len"])
        hs49_vec = pooled(captures["hidden_states_49"], generated["prompt_len"])
        hook_coords = project(hook_vec, basis)
        hs48_coords = project(hs48_vec, basis)
        hs49_coords = project(hs49_vec, basis)
        for label, vec, coords in [("hidden_states_48", hs48_vec, hs48_coords), ("hidden_states_49", hs49_vec, hs49_coords)]:
            comp = compare_vectors(hook_vec, vec)
            delta = coords - hook_coords
            row = {
                "role": role,
                "question_id": questions[0]["question_id"],
                "comparison": f"hook_layer_48_vs_{label}",
                "cosine": comp["cosine"],
                "l2_norm_difference": comp["l2_norm_difference"],
                "max_abs_difference": comp["max_abs_difference"],
                "hook_pc1": float(hook_coords[0]),
                "hook_pc2": float(hook_coords[1]),
                "hook_pc3": float(hook_coords[2]),
                f"{label}_pc1": float(coords[0]),
                f"{label}_pc2": float(coords[1]),
                f"{label}_pc3": float(coords[2]),
                "delta_pc1": float(delta[0]),
                "delta_pc2": float(delta[1]),
                "delta_pc3": float(delta[2]),
                "coordinate_delta_l2": float(np.linalg.norm(delta)),
            }
            rows.append(row)
        details.append(
            {
                "role": role,
                "response_text": generated["response_text"],
                "prompt_token_count": generated["prompt_len"],
                "response_token_count": int(generated["input_ids"].shape[1] - generated["prompt_len"]),
            }
        )
    write_csv(OUT_DIR / "boundary_test_vectors_summary.csv", rows)
    hs48_mean_cos = float(np.mean([r["cosine"] for r in rows if "hidden_states_48" in r["comparison"]]))
    hs49_mean_cos = float(np.mean([r["cosine"] for r in rows if "hidden_states_49" in r["comparison"]]))
    hs48_mean_delta = float(np.mean([r["coordinate_delta_l2"] for r in rows if "hidden_states_48" in r["comparison"]]))
    hs49_mean_delta = float(np.mean([r["coordinate_delta_l2"] for r in rows if "hidden_states_49" in r["comparison"]]))
    if hs49_mean_cos > 0.999999 and hs49_mean_delta < 1e-4 and hs49_mean_cos > hs48_mean_cos:
        conclusion = "hook_matches_hidden_states_49"
        proceed = True
        source = "hook_layer_48"
    elif hs48_mean_cos > 0.999999 and hs48_mean_delta < 1e-4 and hs48_mean_cos > hs49_mean_cos:
        conclusion = "hook_matches_hidden_states_48"
        proceed = True
        source = "hook_layer_48"
    else:
        conclusion = "ambiguous_use_hook_directly"
        proceed = True
        source = "hook_layer_48"
    result = {
        "stage": "boundary_test",
        "completed_utc": now_iso(),
        "layer": LAYER,
        "comparisons": rows,
        "details": details,
        "mean_cosine_hook_vs_hidden_states_48": hs48_mean_cos,
        "mean_cosine_hook_vs_hidden_states_49": hs49_mean_cos,
        "mean_coordinate_delta_l2_hook_vs_hidden_states_48": hs48_mean_delta,
        "mean_coordinate_delta_l2_hook_vs_hidden_states_49": hs49_mean_delta,
        "conclusion": conclusion,
        "proceed_to_stage_2": proceed,
        "activation_source_for_stage_2": source,
    }
    write_json(OUT_DIR / "boundary_test_results.json", result)
    report = [
        "# Boundary Test Report",
        "",
        f"- Completed UTC: {result['completed_utc']}",
        f"- Layer hook tested: `model.model.layers[{LAYER}]`",
        f"- Conclusion: `{conclusion}`",
        f"- Stage 2 proceeded: `{proceed}`",
        f"- Mean cosine hook vs hidden_states[48]: {hs48_mean_cos:.12f}",
        f"- Mean cosine hook vs hidden_states[49]: {hs49_mean_cos:.12f}",
        f"- Mean coordinate delta L2 hook vs hidden_states[48]: {hs48_mean_delta:.12e}",
        f"- Mean coordinate delta L2 hook vs hidden_states[49]: {hs49_mean_delta:.12e}",
        "",
        "Stage 2 uses direct hook extraction from `model.model.layers[48]`, which is functional regardless of the hidden-state tuple indexing convention.",
        "",
    ]
    (OUT_DIR / "boundary_test_report.md").write_text("\n".join(report))
    return result


def selected_questions(questions: list[dict[str, Any]], per_instruction: int) -> list[dict[str, Any]]:
    if per_instruction > 20:
        raise RuntimeError("per-instruction question count exceeds no-confirmation bound")
    indices = np.linspace(0, len(questions) - 1, per_instruction, dtype=int)
    return [questions[int(i)] for i in indices]


def run_activation_cloud(tokenizer: Any, model: Any, basis: dict[str, Any], geometry: dict[str, Any], instructions: dict[str, list[str]], questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    q_subset = selected_questions(questions, QUESTION_COUNT_PER_INSTRUCTION)
    responses_path = OUT_DIR / "activation_cloud_responses.jsonl"
    judge_path = OUT_DIR / "judge_input_responses.jsonl"
    rows = []
    manifest_rows = []
    with responses_path.open("w") as f_resp, judge_path.open("w") as f_judge:
        for role in ROLES:
            published = np.array([geometry[role]["pc1"], geometry[role]["pc2"], geometry[role]["pc3"]], dtype=np.float64)
            for instruction_id, system_instruction in enumerate(instructions[role]):
                for q in q_subset:
                    response_id = f"{role}_i{instruction_id:02d}_q{int(q['question_id']):03d}"
                    seed = SEED + (0 if role == "amateur" else 10000) + instruction_id * 1000 + int(q["question_id"])
                    messages = make_messages(system_instruction, q["question"])
                    t0 = time.time()
                    error_flag = ""
                    try:
                        generated = generate_tokens(tokenizer, model, messages, seed=seed)
                        gen_seconds = time.time() - t0
                        t1 = time.time()
                        captures = full_forward_capture(model, generated["input_ids"])
                        hook_vec = pooled(captures["hook"], generated["prompt_len"])
                        act_seconds = time.time() - t1
                        coords = project(hook_vec, basis)
                        nearest, nearest_dist = nearest_role(coords, basis)
                        delta = coords - published
                        response_text = generated["response_text"]
                        row = {
                            "response_id": response_id,
                            "role": role,
                            "instruction_id": instruction_id,
                            "question_id": int(q["question_id"]),
                            "system_instruction": system_instruction,
                            "extraction_question": q["question"],
                            "full_prompt_messages": json.dumps(messages, ensure_ascii=False),
                            "generated_response": response_text,
                            "generation_seed": seed,
                            "generation_settings": json.dumps(
                                {
                                    "max_new_tokens": MAX_NEW_TOKENS,
                                    "temperature": TEMPERATURE,
                                    "top_p": TOP_P,
                                    "do_sample": DO_SAMPLE,
                                    "thinking_disabled": True,
                                }
                            ),
                            "prompt_token_count": generated["prompt_len"],
                            "response_token_count": int(generated["input_ids"].shape[1] - generated["prompt_len"]),
                            "generation_time_seconds": round(gen_seconds, 4),
                            "activation_time_seconds": round(act_seconds, 4),
                            "activation_source_used": "model.model.layers[48] forward hook",
                            "pc1": float(coords[0]),
                            "pc2": float(coords[1]),
                            "pc3": float(coords[2]),
                            "distance_to_published_role_centroid_3d": float(np.linalg.norm(delta)),
                            "delta_pc1_from_published_centroid": float(delta[0]),
                            "delta_pc2_from_published_centroid": float(delta[1]),
                            "delta_pc3_from_published_centroid": float(delta[2]),
                            "nearest_role_by_3d_distance_if_feasible": nearest,
                            "nearest_role_3d_distance": nearest_dist,
                            "safety_or_refusal_heuristic_flag": response_refusal_flag(response_text),
                            "error_flag": error_flag,
                        }
                    except Exception as exc:
                        row = {
                            "response_id": response_id,
                            "role": role,
                            "instruction_id": instruction_id,
                            "question_id": int(q["question_id"]),
                            "system_instruction": system_instruction,
                            "extraction_question": q["question"],
                            "full_prompt_messages": json.dumps(messages, ensure_ascii=False),
                            "generated_response": "",
                            "generation_seed": seed,
                            "generation_settings": json.dumps({"error": "before_complete"}),
                            "prompt_token_count": None,
                            "response_token_count": None,
                            "generation_time_seconds": None,
                            "activation_time_seconds": None,
                            "activation_source_used": "model.model.layers[48] forward hook",
                            "pc1": None,
                            "pc2": None,
                            "pc3": None,
                            "distance_to_published_role_centroid_3d": None,
                            "delta_pc1_from_published_centroid": None,
                            "delta_pc2_from_published_centroid": None,
                            "delta_pc3_from_published_centroid": None,
                            "nearest_role_by_3d_distance_if_feasible": None,
                            "nearest_role_3d_distance": None,
                            "safety_or_refusal_heuristic_flag": None,
                            "error_flag": repr(exc),
                        }
                    rows.append(row)
                    f_resp.write(json.dumps(row, ensure_ascii=False) + "\n")
                    f_resp.flush()
                    f_judge.write(
                        json.dumps(
                            {
                                "response_id": row["response_id"],
                                "role": row["role"],
                                "system_instruction": row["system_instruction"],
                                "extraction_question": row["extraction_question"],
                                "generated_response": row["generated_response"],
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                    f_judge.flush()
                    manifest_rows.append(
                        {
                            "response_id": response_id,
                            "role": role,
                            "instruction_id": instruction_id,
                            "question_id": int(q["question_id"]),
                            "status": "error" if row["error_flag"] else "ok",
                        }
                    )
                    print(f"{response_id} pc=({row['pc1']},{row['pc2']},{row['pc3']}) err={row['error_flag']}", flush=True)
    write_csv(OUT_DIR / "activation_cloud_per_response.csv", rows)
    write_csv(OUT_DIR / "activation_cloud_run_manifest.csv", manifest_rows)
    return rows


def analyze_cloud(rows: list[dict[str, Any]], geometry: dict[str, Any]) -> dict[str, Any]:
    ok_rows = [r for r in rows if not r["error_flag"]]
    summary_rows = []
    covariance = {}
    distance_stats = {}
    report = ["# Activation Cloud Analysis Report", ""]
    for role in ROLES:
        role_rows = [r for r in ok_rows if r["role"] == role]
        coords = np.array([[float(r["pc1"]), float(r["pc2"]), float(r["pc3"])] for r in role_rows], dtype=np.float64)
        published = np.array([geometry[role]["pc1"], geometry[role]["pc2"], geometry[role]["pc3"]], dtype=np.float64)
        centroid = coords.mean(axis=0)
        deltas = coords - published[None, :]
        distances = np.linalg.norm(deltas, axis=1)
        cov = np.cov(coords.T)
        eigvals, eigvecs = np.linalg.eigh(cov)
        order = np.argsort(eigvals)[::-1]
        eigvals = eigvals[order]
        eigvecs = eigvecs[:, order]
        covariance[role] = {
            "covariance_matrix_pc1_pc2_pc3": cov.tolist(),
            "principal_spread_eigenvalues": eigvals.tolist(),
            "principal_spread_eigenvectors_columns": eigvecs.tolist(),
            "one_sigma_axis_lengths": np.sqrt(np.maximum(eigvals, 0)).tolist(),
            "two_sigma_axis_lengths": (2 * np.sqrt(np.maximum(eigvals, 0))).tolist(),
        }
        distance_stats[role] = {
            "n": len(role_rows),
            "mean_distance_to_published_centroid": float(distances.mean()),
            "median_distance_to_published_centroid": float(np.median(distances)),
            "min_distance_to_published_centroid": float(distances.min()),
            "max_distance_to_published_centroid": float(distances.max()),
            "std_distance_to_published_centroid": float(distances.std()),
        }
        summary_rows.append(
            {
                "role": role,
                "n": len(role_rows),
                "published_pc1": float(published[0]),
                "published_pc2": float(published[1]),
                "published_pc3": float(published[2]),
                "response_centroid_pc1": float(centroid[0]),
                "response_centroid_pc2": float(centroid[1]),
                "response_centroid_pc3": float(centroid[2]),
                "centroid_distance_to_published_3d": float(np.linalg.norm(centroid - published)),
                "variance_pc1": float(np.var(coords[:, 0], ddof=1)),
                "variance_pc2": float(np.var(coords[:, 1], ddof=1)),
                "variance_pc3": float(np.var(coords[:, 2], ddof=1)),
                "mean_distance_to_published_centroid": distance_stats[role]["mean_distance_to_published_centroid"],
                "median_distance_to_published_centroid": distance_stats[role]["median_distance_to_published_centroid"],
                "max_distance_to_published_centroid": distance_stats[role]["max_distance_to_published_centroid"],
            }
        )
        report.extend(
            [
                f"## {role}",
                "",
                f"- Responses: {len(role_rows)}",
                f"- Published centroid: ({published[0]:.6f}, {published[1]:.6f}, {published[2]:.6f})",
                f"- All-response centroid: ({centroid[0]:.6f}, {centroid[1]:.6f}, {centroid[2]:.6f})",
                f"- Centroid distance to published centroid: {np.linalg.norm(centroid - published):.6f}",
                f"- Variance by PC: PC1={np.var(coords[:, 0], ddof=1):.6f}, PC2={np.var(coords[:, 1], ddof=1):.6f}, PC3={np.var(coords[:, 2], ddof=1):.6f}",
                f"- Mean / median / max response distance to published centroid: {distances.mean():.6f} / {np.median(distances):.6f} / {distances.max():.6f}",
                "",
            ]
        )
    write_csv(OUT_DIR / "activation_cloud_summary_by_role.csv", summary_rows)
    write_json(OUT_DIR / "activation_cloud_covariance_by_role.json", covariance)
    write_json(OUT_DIR / "activation_cloud_distance_stats.json", distance_stats)
    report.extend(
        [
            "## Interpretation",
            "",
            "Judge analysis was not run in this GPU task. Raw responses were preserved in `judge_input_responses.jsonl` for later offline filtering and evaluator comparison.",
            "Single-response precision should be assessed from the distance and covariance outputs rather than assumed from the published role centroids.",
            "",
        ]
    )
    (OUT_DIR / "activation_cloud_analysis_report.md").write_text("\n".join(report))
    make_plots(ok_rows, geometry)
    make_html(ok_rows, geometry)
    write_json(
        OUT_DIR / "cloud_visualization_manifest.json",
        {
            "plots_png": "activation_cloud_plots.png",
            "html_3d": "activation_cloud_3d.html",
            "roles": ROLES,
            "generated_utc": now_iso(),
        },
    )
    return {"summary_rows": summary_rows, "covariance": covariance, "distance_stats": distance_stats}


def make_plots(rows: list[dict[str, Any]], geometry: dict[str, Any]) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return
    colors = {"amateur": "#1f77b4", "playwright": "#d62728"}
    pairs = [("pc1", "pc2"), ("pc1", "pc3"), ("pc2", "pc3")]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, (x, y) in zip(axes, pairs):
        for role in ROLES:
            role_rows = [r for r in rows if r["role"] == role]
            xs = [float(r[x]) for r in role_rows]
            ys = [float(r[y]) for r in role_rows]
            ax.scatter(xs, ys, s=22, alpha=0.5, label=f"{role} responses", color=colors[role])
            cx, cy = np.mean(xs), np.mean(ys)
            ax.scatter([cx], [cy], s=120, marker="x", color=colors[role], label=f"{role} response centroid")
            ax.scatter([geometry[role][x]], [geometry[role][y]], s=120, marker="*", color=colors[role], edgecolors="black", label=f"{role} published")
        ax.set_xlabel(x.upper())
        ax.set_ylabel(y.upper())
        ax.axhline(0, color="black", linewidth=0.5, alpha=0.25)
        ax.axvline(0, color="black", linewidth=0.5, alpha=0.25)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4)
    fig.tight_layout(rect=[0, 0.12, 1, 1])
    fig.savefig(OUT_DIR / "activation_cloud_plots.png", dpi=160)
    plt.close(fig)


def make_html(rows: list[dict[str, Any]], geometry: dict[str, Any]) -> None:
    data = []
    for r in rows:
        data.append(
            {
                "role": r["role"],
                "response_id": r["response_id"],
                "pc1": r["pc1"],
                "pc2": r["pc2"],
                "pc3": r["pc3"],
                "distance": r["distance_to_published_role_centroid_3d"],
            }
        )
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Activation Cloud Pilot</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script></head>
<body><div id="plot" style="width:100%;height:95vh"></div>
<script>
const rows = {json.dumps(data)};
const geometry = {json.dumps({r: geometry[r] for r in ROLES})};
const roles = {json.dumps(ROLES)};
const colors = {{amateur: '#1f77b4', playwright: '#d62728'}};
const traces = [];
for (const role of roles) {{
  const pts = rows.filter(r => r.role === role);
  traces.push({{
    type: 'scatter3d', mode: 'markers', name: role + ' responses',
    x: pts.map(r => r.pc1), y: pts.map(r => r.pc2), z: pts.map(r => r.pc3),
    text: pts.map(r => `${{r.response_id}}<br>dist=${{Number(r.distance).toFixed(2)}}`),
    marker: {{size: 4, color: colors[role], opacity: 0.65}}
  }});
  traces.push({{
    type: 'scatter3d', mode: 'markers', name: role + ' published centroid',
    x: [geometry[role].pc1], y: [geometry[role].pc2], z: [geometry[role].pc3],
    marker: {{size: 9, color: colors[role], symbol: 'diamond'}}
  }});
}}
Plotly.newPlot('plot', traces, {{scene: {{xaxis: {{title: 'PC1'}}, yaxis: {{title: 'PC2'}}, zaxis: {{title: 'PC3'}}}}}});
</script></body></html>"""
    (OUT_DIR / "activation_cloud_3d.html").write_text(html)


def preflight() -> tuple[dict[str, Any], dict[str, list[str]], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    geometry = load_geometry()
    instructions = {role: load_role_instructions(role) for role in ROLES}
    questions = load_questions()
    basis = load_role_vectors_and_basis()
    config = {
        "created_utc": now_iso(),
        "model": MODEL_ID,
        "layer": LAYER,
        "roles": ROLES,
        "target_generations_per_role": TARGET_GENERATIONS_PER_ROLE,
        "question_count_per_instruction": QUESTION_COUNT_PER_INSTRUCTION,
        "generation_settings": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "do_sample": DO_SAMPLE,
            "thinking_disabled": True,
        },
        "geometry_source": str(GEOMETRY_PATH),
        "questions_path": str(QUESTIONS_PATH),
        "vector_dir": str(VECTOR_DIR),
        "pca_basis_debug": basis["debug"],
    }
    write_json(OUT_DIR / "run_config.json", config)
    preflight_report = [
        "# Preflight Report",
        "",
        f"- Completed UTC: {config['created_utc']}",
        f"- Model: {MODEL_ID}",
        f"- Roles: {', '.join(ROLES)}",
        f"- Geometry source exists: {GEOMETRY_PATH.exists()}",
        f"- Amateur centroid: ({geometry['amateur']['pc1']:.6f}, {geometry['amateur']['pc2']:.6f}, {geometry['amateur']['pc3']:.6f})",
        f"- Playwright centroid: ({geometry['playwright']['pc1']:.6f}, {geometry['playwright']['pc2']:.6f}, {geometry['playwright']['pc3']:.6f})",
        f"- Five positive instructions available for each role: {all(len(v) == 5 for v in instructions.values())}",
        f"- Extraction questions available: {len(questions)}",
        f"- PCA reproduction max abs error: {basis['debug']['max_abs_coordinate_reproduction_error']:.12e}",
        "",
    ]
    (OUT_DIR / "preflight_report.md").write_text("\n".join(preflight_report))
    return geometry, instructions, questions, basis, config


def closeout_files(extra: dict[str, Any]) -> None:
    files = sorted([p for p in OUT_DIR.iterdir() if p.is_file()])
    with (OUT_DIR / "gpu_copy_manifest.sha256").open("w") as f:
        for path in files:
            if path.name == "gpu_copy_manifest.sha256":
                continue
            f.write(f"{sha256_file(path)}  {path.name}\n")
    write_json(OUT_DIR / "gpu_pod_closeout.json", extra)


def main() -> None:
    run_start = time.time()
    geometry, instructions, questions, basis, config = preflight()
    token = os.environ.get("HF_TOKEN")
    if not token and Path("/root/.hf_token").exists():
        token = Path("/root/.hf_token").read_text().strip()
    print("Loading tokenizer/model...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        token=token,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    boundary = run_boundary_test(tokenizer, model, basis, instructions, questions)
    stage2_proceeded = bool(boundary["proceed_to_stage_2"])
    rows: list[dict[str, Any]] = []
    analysis: dict[str, Any] = {}
    if stage2_proceeded:
        rows = run_activation_cloud(tokenizer, model, basis, geometry, instructions, questions)
        analysis = analyze_cloud(rows, geometry)
    runtime_seconds = time.time() - run_start
    cost_per_hr = float(os.environ.get("RUNPOD_COST_PER_HR", "1.49"))
    runtime_report = {
        "pod_id": os.environ.get("RUNPOD_POD_ID", "unknown"),
        "gpu_type": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none",
        "cost_per_hr": cost_per_hr,
        "runtime_seconds": runtime_seconds,
        "estimated_cost_usd": runtime_seconds / 3600.0 * cost_per_hr,
        "stage2_proceeded": stage2_proceeded,
        "responses_generated": len([r for r in rows if not r.get("error_flag")]),
        "completed_utc": now_iso(),
    }
    write_json(OUT_DIR / "gpu_runtime_cost_report.json", runtime_report)
    (OUT_DIR / "gpu_runtime_cost_report.md").write_text(
        "\n".join(
            [
                "# GPU Runtime Cost Report",
                "",
                f"- Pod ID: {runtime_report['pod_id']}",
                f"- GPU type: {runtime_report['gpu_type']}",
                f"- Hourly rate: ${cost_per_hr:.2f}/hr",
                f"- Runtime seconds: {runtime_seconds:.1f}",
                f"- Estimated cost: ${runtime_report['estimated_cost_usd']:.2f}",
                f"- Stage 2 proceeded: {stage2_proceeded}",
                f"- Responses generated: {runtime_report['responses_generated']}",
                "",
            ]
        )
    )
    closeout_files({"pod_id": runtime_report["pod_id"], "pre_termination_status": "outputs_written_on_pod", **runtime_report})
    print(json.dumps({"boundary": boundary["conclusion"], "runtime": runtime_report}, indent=2), flush=True)


if __name__ == "__main__":
    main()
