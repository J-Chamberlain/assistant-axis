import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from huggingface_hub import hf_hub_download, login
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct"
LAYERS = [79, 40]
LOAD_MODE = "8bit_with_fp32_cpu_offload"
OUTPUT_DIR = Path("research/emotions/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PILOT_EMOTIONS = [
    "afraid",
    "calm",
    "happy",
    "sad",
    "angry",
    "content",
    "disgusted",
    "joyful",
    "scared",
    "serene",
    "furious",
    "melancholy",
]
OPPOSITE_PAIRS = [
    ("afraid", "calm"),
    ("happy", "sad"),
    ("angry", "content"),
    ("disgusted", "joyful"),
]
STORIES_PER_EMOTION = 15


token = open(os.path.expanduser("~/.hf_token")).read().strip()
login(token=token)

print("Loading emotion-probes stories parquet...")
stories_file = hf_hub_download(
    repo_id="ryancodrai/emotion-probes",
    repo_type="dataset",
    filename="expression/stories.parquet",
    token=token,
)
ds = pd.read_parquet(stories_file)

available = set(ds["emotion"].unique())
print(f"Emotions in corpus: {sorted(available)}")
missing = [e for e in PILOT_EMOTIONS if e not in available]
if missing:
    print(f"WARNING: pilot emotions not in corpus: {missing}")
    PILOT_EMOTIONS = [e for e in PILOT_EMOTIONS if e in available]

print(f"\nLoading {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=token)
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_enable_fp32_cpu_offload=True,
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=quantization_config,
    device_map="auto",
    max_memory={0: "78GiB", "cpu": "180GiB"},
    output_hidden_states=True,
    token=token,
)
model.eval()
first_device = next(model.parameters()).device
print(f"Model loaded. First parameter device: {first_device}")


def get_last_token_activation(text, layer):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(first_device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True)
    return out.hidden_states[layer][0, -1, :].float().cpu().numpy()


def extract_activations(layer):
    print(f"\nExtracting activations at layer {layer}...")
    emotion_activations = {}
    for emotion in PILOT_EMOTIONS:
        stories = (
            ds.loc[ds["emotion"] == emotion, "story"]
            .head(STORIES_PER_EMOTION)
            .tolist()
        )
        acts = []
        for story in stories:
            try:
                acts.append(get_last_token_activation(story, layer))
            except Exception as e:
                print(f"  skip ({emotion}): {e}")
        if len(acts) >= 5:
            emotion_activations[emotion] = np.stack(acts)
            print(f"  {emotion}: {len(acts)} stories")
        else:
            print(f"  {emotion}: insufficient ({len(acts)}) -- skipped")
    return emotion_activations


def pca_gate(emotion_activations):
    all_acts = np.vstack(list(emotion_activations.values()))
    mean = all_acts.mean(axis=0)
    centered = all_acts - mean
    _, s, vt = np.linalg.svd(centered, full_matrices=False)
    total_var = (s**2).sum()
    pc1_var = float((s[0] ** 2 / total_var) * 100)
    pc2_var = float((s[1] ** 2 / total_var) * 100)
    print(f"  PC1 variance: {pc1_var:.1f}% (gate requires >= 30%)")
    print(f"  PC2 variance: {pc2_var:.1f}%")
    return pc1_var, pc2_var, mean, vt


def cosine_check(emotion_activations, mean, vt):
    pc1_dir = vt[0]
    results = {}
    for e1, e2 in OPPOSITE_PAIRS:
        if e1 not in emotion_activations or e2 not in emotion_activations:
            results[f"{e1}/{e2}"] = None
            print(f"  cosine {e1}/{e2}: skipped (emotion missing)")
            continue
        v1 = emotion_activations[e1].mean(axis=0) - mean
        v2 = emotion_activations[e2].mean(axis=0) - mean
        v1 = v1 - (v1 @ pc1_dir) * pc1_dir
        v2 = v2 - (v2 @ pc1_dir) * pc1_dir
        cos = float(
            np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
        )
        results[f"{e1}/{e2}"] = cos
        print(f"  cosine {e1}/{e2}: {cos:.3f} (want negative)")
    return results


def compute_vectors(emotion_activations, mean, vt):
    pc1_dir = vt[0]
    vectors = {}
    for emotion, acts in emotion_activations.items():
        v = acts.mean(axis=0) - mean
        v_clean = v - (v @ pc1_dir) * pc1_dir
        v_norm = v_clean / (np.linalg.norm(v_clean) + 1e-9)
        vectors[emotion] = v_norm
    return vectors


def run_layer(layer):
    suffix = f"llama33_70b_layer{layer}"
    emotion_activations = extract_activations(layer)
    pc1_var, pc2_var, mean, vt = pca_gate(emotion_activations)
    cosine_results = cosine_check(emotion_activations, mean, vt)
    gate_pass = bool(pc1_var >= 30.0)
    anticorrelated = int(
        sum(1 for v in cosine_results.values() if v is not None and v < 0)
    )
    verdict = "PASS" if (gate_pass and anticorrelated >= 2) else "LOW"
    print(f"\nVerdict layer {layer}: {verdict}")
    result = {
        "model": MODEL_ID,
        "layer": int(layer),
        "load_mode": LOAD_MODE,
        "suffix": suffix,
        "pc1_var": float(pc1_var),
        "pc2_var": float(pc2_var),
        "cosine_pairs": cosine_results,
        "anticorrelated_pairs": anticorrelated,
        "gate_pass": gate_pass,
        "verdict": verdict,
        "n_emotions": int(len(emotion_activations)),
    }
    with open(OUTPUT_DIR / f"reliability_verdict_{suffix}.txt", "w") as f:
        f.write(json.dumps(result, indent=2))
    if verdict == "PASS":
        vectors = compute_vectors(emotion_activations, mean, vt)
        torch.save(
            {e: torch.tensor(v) for e, v in vectors.items()},
            OUTPUT_DIR / f"emotion_vectors_{suffix}.pt",
        )
        np.save(OUTPUT_DIR / f"mean_activation_{suffix}.npy", mean)
        print(f"Vectors saved for layer {layer}.")
    return result


result_79 = run_layer(79)
print("\nLayer 79 complete. Proceeding to layer 40 regardless of result.")
result_40 = run_layer(40)

print("\n=== FINAL SUMMARY ===")
print(
    f"Layer 79: {result_79['verdict']} | "
    f"PC1={result_79['pc1_var']:.1f}% | "
    f"anticorrelated={result_79['anticorrelated_pairs']}"
)
print(
    f"Layer 40: {result_40['verdict']} | "
    f"PC1={result_40['pc1_var']:.1f}% | "
    f"anticorrelated={result_40['anticorrelated_pairs']}"
)
better = 79 if result_79["pc1_var"] >= result_40["pc1_var"] else 40
print(f"Stronger signal at: layer {better}")
print("Done. Stop here and report results.")
