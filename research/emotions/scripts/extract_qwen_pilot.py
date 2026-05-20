import torch
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login, hf_hub_download
import os, json
from pathlib import Path

MODEL_ID = "Qwen/Qwen3-32B"
LAYERS = [63, 48]
OUTPUT_DIR = Path("research/emotions/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PILOT_EMOTIONS = [
    "afraid", "calm", "happy", "sad", "angry", "content",
    "disgusted", "joyful", "scared", "serene", "furious", "melancholy"
]
OPPOSITE_PAIRS = [
    ("afraid", "calm"), ("happy", "sad"),
    ("angry", "content"), ("disgusted", "joyful")
]
STORIES_PER_EMOTION = 15

token = open(os.path.expanduser("~/.hf_token")).read().strip()
login(token=token)

print("Loading emotion-probes dataset from expression/stories.parquet...")
stories_file = hf_hub_download(
    repo_id="ryancodrai/emotion-probes",
    repo_type="dataset",
    filename="expression/stories.parquet",
    token=token,
)
ds = pd.read_parquet(stories_file)

# Verify pilot emotions are present in the corpus
available = set(ds["emotion"].unique())
print(f"Emotions in corpus: {sorted(available)}")
missing = [e for e in PILOT_EMOTIONS if e not in available]
if missing:
    print(f"WARNING: these pilot emotions not found in corpus: {missing}")
    print("Continuing with available emotions only.")
    PILOT_EMOTIONS = [e for e in PILOT_EMOTIONS if e in available]

print(f"\nLoading {MODEL_ID}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    output_hidden_states=True
)
model.eval()
print("Model loaded.")

def get_last_token_activation(text, layer):
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, max_length=512)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model(**inputs, output_hidden_states=True)
    return out.hidden_states[layer][0, -1, :].float().cpu().numpy()

def extract_activations(layer):
    print(f"\nExtracting activations at layer {layer}...")
    emotion_activations = {}
    for emotion in PILOT_EMOTIONS:
        stories = ds.loc[ds["emotion"] == emotion, "story"].head(STORIES_PER_EMOTION).tolist()
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
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    total_var = (S**2).sum()
    pc1_var = (S[0]**2 / total_var) * 100
    pc2_var = (S[1]**2 / total_var) * 100
    print(f"  PC1 variance: {pc1_var:.1f}% (gate requires >= 30%)")
    print(f"  PC2 variance: {pc2_var:.1f}%")
    return pc1_var, pc2_var, mean, Vt

def cosine_check(emotion_activations, mean, Vt):
    pc1_dir = Vt[0]
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
        cos = float(np.dot(v1, v2) /
                    (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9))
        results[f"{e1}/{e2}"] = cos
        print(f"  cosine {e1}/{e2}: {cos:.3f} (want negative)")
    return results

def compute_vectors(emotion_activations, mean, Vt):
    pc1_dir = Vt[0]
    vectors = {}
    for emotion, acts in emotion_activations.items():
        v = acts.mean(axis=0) - mean
        v_clean = v - (v @ pc1_dir) * pc1_dir
        v_norm = v_clean / (np.linalg.norm(v_clean) + 1e-9)
        vectors[emotion] = v_norm
    return vectors

def run_layer(layer):
    suffix = f"qwen3_32b_layer{layer}"
    emotion_activations = extract_activations(layer)
    pc1_var, pc2_var, mean, Vt = pca_gate(emotion_activations)
    cosine_results = cosine_check(emotion_activations, mean, Vt)
    gate_pass = pc1_var >= 30.0
    anticorrelated = sum(1 for v in cosine_results.values()
                         if v is not None and v < 0)
    verdict = "PASS" if (gate_pass and anticorrelated >= 2) else "LOW"
    print(f"\nVerdict layer {layer}: {verdict}")
    result = {
        "model": MODEL_ID, "layer": layer, "suffix": suffix,
        "pc1_var": float(pc1_var), "pc2_var": float(pc2_var),
        "cosine_pairs": {k: (None if v is None else float(v)) for k, v in cosine_results.items()},
        "anticorrelated_pairs": int(anticorrelated),
        "gate_pass": bool(gate_pass), "verdict": verdict,
        "n_emotions": int(len(emotion_activations))
    }
    with open(OUTPUT_DIR / f"reliability_verdict_{suffix}.txt", "w") as f:
        f.write(json.dumps(result, indent=2))
    if verdict == "PASS":
        vectors = compute_vectors(emotion_activations, mean, Vt)
        torch.save(
            {e: torch.tensor(v) for e, v in vectors.items()},
            OUTPUT_DIR / f"emotion_vectors_{suffix}.pt"
        )
        np.save(OUTPUT_DIR / f"mean_activation_{suffix}.npy", mean)
        print(f"Vectors saved for layer {layer}.")
    return result

# Run both layers always -- compare results
result_63 = run_layer(63)
print("\nLayer 63 complete. Proceeding to layer 48 regardless of result.")
result_48 = run_layer(48)

# Final summary
print("\n=== FINAL SUMMARY ===")
print(f"Layer 63: {result_63['verdict']} | "
      f"PC1={result_63['pc1_var']:.1f}% | "
      f"anticorrelated={result_63['anticorrelated_pairs']}")
print(f"Layer 48: {result_48['verdict']} | "
      f"PC1={result_48['pc1_var']:.1f}% | "
      f"anticorrelated={result_48['anticorrelated_pairs']}")

better = 63 if result_63['pc1_var'] >= result_48['pc1_var'] else 48
print(f"Stronger signal at: layer {better}")
print("Done.")
