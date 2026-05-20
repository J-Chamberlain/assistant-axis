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
    "disgusted", "joyful", "fearful", "serene", "furious", "melancholy"
]
OPPOSITE_PAIRS = [
    ("afraid", "calm"), ("happy", "sad"),
    ("angry", "content"), ("disgusted", "joyful")
]
# Use 12 stories for training vectors, 3 held out for discrimination test
STORIES_TRAIN = 12
STORIES_HOLDOUT = 3

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

available = set(ds["emotion"].unique())
print(f"Emotions in corpus: {sorted(available)}")
missing = [e for e in PILOT_EMOTIONS if e not in available]
if missing:
    print(f"WARNING: pilot emotions not in corpus: {missing}")
PILOT_EMOTIONS = [e for e in PILOT_EMOTIONS if e in available]
print(f"Running with {len(PILOT_EMOTIONS)} emotions: {PILOT_EMOTIONS}")

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

def extract_split(layer):
    """Extract train and holdout activations for all emotions."""
    train_acts = {}
    holdout_acts = {}
    for emotion in PILOT_EMOTIONS:
        stories = ds.loc[ds["emotion"] == emotion, "story"].tolist()
        train_stories = stories[:STORIES_TRAIN]
        holdout_stories = stories[STORIES_TRAIN:STORIES_TRAIN + STORIES_HOLDOUT]
        train = []
        for story in train_stories:
            try:
                train.append(get_last_token_activation(story, layer))
            except Exception as e:
                print(f"  skip train ({emotion}): {e}")
        holdout = []
        for story in holdout_stories:
            try:
                holdout.append(get_last_token_activation(story, layer))
            except Exception as e:
                print(f"  skip holdout ({emotion}): {e}")
        if len(train) >= 5:
            train_acts[emotion] = np.stack(train)
            holdout_acts[emotion] = np.stack(holdout) if holdout else None
            print(f"  {emotion}: {len(train)} train, {len(holdout)} holdout")
        else:
            print(f"  {emotion}: insufficient train ({len(train)}) -- skipped")
    return train_acts, holdout_acts

def compute_vectors(train_acts):
    """Compute mean-centered, PCA-confound-removed, unit-normalized vectors."""
    all_acts = np.vstack(list(train_acts.values()))
    mean = all_acts.mean(axis=0)
    centered = all_acts - mean
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    total_var = (S**2).sum()
    pc1_var = (S[0]**2 / total_var) * 100
    pc2_var = (S[1]**2 / total_var) * 100
    print(f"  PC1 variance: {pc1_var:.1f}%  PC2 variance: {pc2_var:.1f}%")
    pc1_dir = Vt[0]
    vectors = {}
    for emotion, acts in train_acts.items():
        v = acts.mean(axis=0) - mean
        v_clean = v - (v @ pc1_dir) * pc1_dir
        v_norm = v_clean / (np.linalg.norm(v_clean) + 1e-9)
        vectors[emotion] = v_norm
    return vectors, mean, pc1_dir, pc1_var, pc2_var

def cosine_check(vectors, mean, pc1_dir):
    """Check that opposite-valence pairs are anticorrelated."""
    results = {}
    for e1, e2 in OPPOSITE_PAIRS:
        if e1 not in vectors or e2 not in vectors:
            results[f"{e1}/{e2}"] = None
            continue
        cos = float(np.dot(vectors[e1], vectors[e2]))
        results[f"{e1}/{e2}"] = cos
        print(f"  cosine {e1}/{e2}: {cos:.3f} (want negative)")
    return results

def discrimination_accuracy(vectors, holdout_acts):
    """
    For each holdout story, project onto all emotion vectors.
    Correct if the highest-cosine emotion matches the true label.
    Chance level = 1 / n_emotions.
    """
    correct = 0
    total = 0
    emotion_list = list(vectors.keys())
    vector_matrix = np.stack([vectors[e] for e in emotion_list])
    for true_emotion, acts in holdout_acts.items():
        if acts is None or true_emotion not in vectors:
            continue
        for act in acts:
            act_norm = act / (np.linalg.norm(act) + 1e-9)
            sims = vector_matrix @ act_norm
            pred_emotion = emotion_list[np.argmax(sims)]
            if pred_emotion == true_emotion:
                correct += 1
            total += 1
    accuracy = correct / total if total > 0 else 0.0
    chance = 1.0 / len(emotion_list)
    print(f"  Discrimination accuracy: {accuracy:.3f} "
          f"(chance = {chance:.3f}, n={total})")
    return accuracy, chance, total

def run_layer(layer):
    suffix = f"qwen3_32b_readout_layer{layer}"
    print(f"\n=== Layer {layer} ===")

    train_acts, holdout_acts = extract_split(layer)
    vectors, mean, pc1_dir, pc1_var, pc2_var = compute_vectors(train_acts)
    cosine_results = cosine_check(vectors, mean, pc1_dir)
    accuracy, chance, n_holdout = discrimination_accuracy(vectors, holdout_acts)

    anticorrelated = sum(1 for v in cosine_results.values()
                         if v is not None and v < 0)
    above_chance = accuracy > (chance * 1.5)  # 50% above chance as threshold

    result = {
        "model": MODEL_ID, "layer": layer, "suffix": suffix,
        "pc1_var": pc1_var, "pc2_var": pc2_var,
        "cosine_pairs": cosine_results,
        "anticorrelated_pairs": anticorrelated,
        "discrimination_accuracy": accuracy,
        "chance_level": chance,
        "n_holdout_stories": n_holdout,
        "above_chance": above_chance,
        "readout_verdict": "USABLE" if above_chance else "WEAK",
        "n_emotions": len(train_acts)
    }

    # Save unconditionally regardless of PCA gate
    torch.save(
        {e: torch.tensor(v) for e, v in vectors.items()},
        OUTPUT_DIR / f"emotion_vectors_{suffix}.pt"
    )
    np.save(OUTPUT_DIR / f"mean_activation_{suffix}.npy", mean)
    np.save(OUTPUT_DIR / f"pc1_direction_{suffix}.npy", pc1_dir)
    with open(OUTPUT_DIR / f"readout_verdict_{suffix}.txt", "w") as f:
        f.write(json.dumps(result, indent=2))

    print(f"Readout verdict layer {layer}: {result['readout_verdict']} "
          f"(accuracy={accuracy:.3f}, chance={chance:.3f})")
    print(f"Vectors saved unconditionally.")
    return result

# Run both layers
result_63 = run_layer(63)
print("\nLayer 63 complete. Proceeding to layer 48.")
result_48 = run_layer(48)

# Final comparison
print("\n=== FINAL SUMMARY ===")
print(f"Layer 63: {result_63['readout_verdict']} | "
      f"PC1={result_63['pc1_var']:.1f}% | "
      f"accuracy={result_63['discrimination_accuracy']:.3f} | "
      f"anticorrelated={result_63['anticorrelated_pairs']}")
print(f"Layer 48: {result_48['readout_verdict']} | "
      f"PC1={result_48['pc1_var']:.1f}% | "
      f"accuracy={result_48['discrimination_accuracy']:.3f} | "
      f"anticorrelated={result_48['anticorrelated_pairs']}")

better = 63 if (result_63['discrimination_accuracy'] >=
                result_48['discrimination_accuracy']) else 48
print(f"Recommended readout layer: {better} "
      f"(higher discrimination accuracy)")
print("Done. Stop here and report results.")
