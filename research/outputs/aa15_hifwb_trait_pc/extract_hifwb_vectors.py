#!/usr/bin/env python3
"""Prospective AA-15 contrastive extraction; private output is never committed.

Run on an authorized GPU host with the repository and frozen prompt CSVs.
Uses the repository's response generation and assistant-token extraction helpers.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONFIGS = {
    "qwen": ("Qwen/Qwen3-32B", 64, 5120),
    "llama": ("meta-llama/Llama-3.3-70B-Instruct", 80, 8192),
    "gemma": ("google/gemma-2-27b-it", 46, 4608),
}
SEED = 150015
REFUSAL = re.compile(r"\b(?:cannot|can't|do not have|don't have|as an ai|language model)\b", re.I)


def load_extractor():
    source = ROOT / "pipeline/2_activations.py"
    spec = importlib.util.spec_from_file_location("aa15_source_extractor", source)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.extract_activations_batch


def run(model_key: str, output_dir: Path, pilot: bool) -> None:
    from assistant_axis.generation import format_conversation, generate_response
    from assistant_axis.internals import ProbingModel

    model_name, layers, dim = CONFIGS[model_key]
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)
    assert torch.cuda.is_available(), "GPU is required; do not silently use CPU for model inference"
    extract = load_extractor()
    prompt_bytes = (HERE / "hifwb_prompt_freeze.csv").read_bytes()
    question_bytes = (HERE / "hifwb_extraction_questions.csv").read_bytes()
    protocol_hash = hashlib.sha256(prompt_bytes + b"\0" + question_bytes).hexdigest()
    prompts = list(csv.DictReader(prompt_bytes.decode().splitlines()))
    questions = list(csv.DictReader(question_bytes.decode().splitlines()))
    assert len(prompts) == 195 and len(questions) == 8
    model = ProbingModel(model_name, dtype=torch.bfloat16)
    assert len(model.get_layers()) == layers and model.hidden_size == dim
    placement = getattr(model.model, "hf_device_map", {})
    assert not any(str(device).lower() in {"cpu", "disk"} for device in placement.values()), (
        "Model placement spilled to CPU/disk; stop and choose a sufficient non-spot GPU configuration"
    )
    import transformers
    destination = output_dir / model_key
    assert not destination.resolve().is_relative_to(ROOT.resolve()), (
        "Private activation outputs must be outside the repository"
    )
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {
        "protocol": "AA-15 prospective contrastive analogue v1",
        "model": model_name,
        "model_key": model_key,
        "seed": SEED,
        "prompt_question_protocol_sha256": protocol_hash,
        "prompt_csv_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "question_csv_sha256": hashlib.sha256(question_bytes).hexdigest(),
        "dtype": "bfloat16",
        "all_layers": layers,
        "hidden_size": dim,
        "question_count": len(questions),
        "prompt_pairs_per_item_formulation": 5,
        "generation": {"temperature": 0, "top_p": 1, "max_new_tokens": 192, "qwen_thinking": False},
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "model_hub_revision": getattr(model.model.config, "_commit_hash", None),
        "tokenizer_hub_revision": getattr(model.tokenizer, "_commit_hash", None),
        "device_map": {str(k): str(v) for k, v in placement.items()},
        "items": [],
    }
    grouped = {}
    for row in prompts:
        grouped.setdefault((row["item_id"], row["formulation"]), []).append(row)
    assert len(grouped) == 39 and all(len(rows) == 5 for rows in grouped.values())
    existing_manifest = destination / "extraction_manifest.json"
    if existing_manifest.exists():
        prior_manifest = json.loads(existing_manifest.read_text())
        assert prior_manifest["model"] == model_name
        assert prior_manifest["seed"] == SEED
        assert prior_manifest["prompt_question_protocol_sha256"] == protocol_hash, (
            "Frozen prompt/question protocol differs from existing private extraction"
        )

    for (item_id, formulation), rows in grouped.items():
        target = destination / f"{item_id}__{formulation}.npz"
        if target.exists() and not pilot:
            with np.load(target) as prior:
                assert prior["protocol_sha256"].item() == protocol_hash
                assert prior["model_hub_revision"].item() == str(manifest["model_hub_revision"])
                assert 38 <= prior["unit_pooled_differences"].shape[0] <= 40
                assert prior["all_layer_contrast"].shape == (layers, dim)
            manifest["items"].append({"item_id": item_id, "formulation": formulation,
                                       "status": "reused", "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
            continue
        unit_vectors, response_hashes, refusal_count, empty_count = [], [], 0, 0
        layer_sum = np.zeros((layers, dim), dtype=np.float64)
        started = time.monotonic()
        for row in rows:
            for question in questions:
                pair = []
                for polarity in ("positive", "negative"):
                    conversation = format_conversation(row[f"{polarity}_system_prompt"], question["question"], model.tokenizer)
                    response = generate_response(model.model, model.tokenizer, conversation,
                                                 max_new_tokens=192, do_sample=False)
                    response_hashes.append(hashlib.sha256(response.encode()).hexdigest())
                    refusal_count += bool(REFUSAL.search(response))
                    if not response.strip():
                        empty_count += 1
                        pair.append(None)
                        continue
                    full = conversation + [{"role": "assistant", "content": response}]
                    activation = extract(model, [full], list(range(layers)), batch_size=1,
                                         max_length=2048, enable_thinking=False)[0]
                    assert activation is not None and tuple(activation.shape) == (layers, dim)
                    pair.append(activation.float().numpy())
                if all(p is not None for p in pair):
                    contrast = pair[0] - pair[1]
                    layer_sum += contrast
                    unit_vectors.append(contrast.mean(axis=0))
                if pilot:
                    print(json.dumps({"model": model_key, "pilot_item": item_id,
                                      "formulation": formulation, "paired_units": len(unit_vectors),
                                      "seconds": time.monotonic() - started, "refusals": refusal_count}))
                    return
        assert len(unit_vectors) >= 38, f"{item_id}/{formulation}: >5% paired units failed"
        unit = np.asarray(unit_vectors, dtype=np.float32)
        layer_contrast = (layer_sum / len(unit_vectors)).astype(np.float32)
        vector = layer_contrast.mean(axis=0)
        assert np.max(abs(vector - unit.mean(axis=0))) < 0.01
        np.savez_compressed(target, unit_pooled_differences=unit, all_layer_contrast=layer_contrast,
                            pooled_vector=vector,
                            protocol_sha256=protocol_hash,
                            model_hub_revision=str(manifest["model_hub_revision"]),
                            response_sha256=np.asarray(response_hashes),
                            completed_paired_units=len(unit_vectors), refusal_count=refusal_count,
                            empty_count=empty_count)
        manifest["items"].append({"item_id": item_id, "formulation": formulation,
                                   "status": "extracted", "paired_units": len(unit_vectors),
                                   "refusals": refusal_count, "empties": empty_count,
                                   "seconds": time.monotonic() - started,
                                   "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        (destination / "extraction_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"{model_key} {item_id} {formulation}: {len(unit_vectors)} paired units in {time.monotonic()-started:.1f}s", flush=True)
    (destination / "extraction_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=CONFIGS, required=True)
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="Private local directory, outside Git and outside public site assets")
    parser.add_argument("--pilot", action="store_true", help="One paired unit only; do not write result data")
    args = parser.parse_args()
    run(args.model, args.output_dir, args.pilot)
