import torch
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login, hf_hub_download
import os, json
from pathlib import Path

MODEL_ID = "Qwen/Qwen3-32B"
TARGET_LAYER = 48
OUTPUT_DIR = Path("research/emotions/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
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

# Use all available emotion labels in the corpus
all_emotions = sorted(ds["emotion"].unique().tolist())
print(f"All available emotions ({len(all_emotions)}): {all_emotions}")

# Opposite-valence pairs for cosine validation
# Use whatever pairs are available from the full list
CANDIDATE_PAIRS = [
    ("afraid", "calm"), ("happy", "sad"), ("angry", "content"),
    ("disgusted", "joyful"), ("anxious", "relaxed"),
    ("angry", "peaceful"), ("fearful", "confident"),
    ("sad", "happy"), ("depressed", "elated"),
    ("frustrated", "satisfied"), ("nervous", "calm"),
]
OPPOSITE_PAIRS = [(e1, e2) for e1, e2 in CANDIDATE_PAIRS
                  if e1 in all_emotions and e2 in all_emotions]
# Deduplicate
seen = set()
OPPOSITE_PAIRS_DEDUP = []
for p in OPPOSITE_PAIRS:
    key = frozenset(p)
    if key not in seen:
        seen.add(key)
        OPPOSITE_PAIRS_DEDUP.append(p)
OPPOSITE_PAIRS = OPPOSITE_PAIRS_DEDUP
print(f"Opposite-valence pairs for validation: {OPPOSITE_PAIRS}")

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
    train_acts = {}
    holdout_acts = {}
    for emotion in all_emotions:
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
            print(f"  {emotion}: insufficient ({len(train)}) -- skipped")
    return train_acts, holdout_acts

def compute_directions(train_acts):
    all_acts = np.vstack(list(train_acts.values()))
    mean = all_acts.mean(axis=0)
    centered = all_acts - mean
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    total_var = (S**2).sum()
    pc1_var = (S[0]**2 / total_var) * 100
    pc2_var = (S[1]**2 / total_var) * 100
    print(f"  PC1={pc1_var:.1f}%  PC2={pc2_var:.1f}%")
    pc1_dir = Vt[0]
    directions = {}
    for emotion, acts in train_acts.items():
        v = acts.mean(axis=0) - mean
        v_clean = v - (v @ pc1_dir) * pc1_dir
        v_norm = v_clean / (np.linalg.norm(v_clean) + 1e-9)
        directions[emotion] = v_norm
    return directions, mean, pc1_dir, pc1_var, pc2_var

def cosine_check(directions):
    results = {}
    for e1, e2 in OPPOSITE_PAIRS:
        if e1 not in directions or e2 not in directions:
            continue
        cos = float(np.dot(directions[e1], directions[e2]))
        results[f"{e1}/{e2}"] = cos
        print(f"  cosine {e1}/{e2}: {cos:.3f} (want negative)")
    anticorrelated = sum(1 for v in results.values() if v < 0)
    return results, anticorrelated

def discrimination_accuracy(directions, holdout_acts):
    emotion_list = list(directions.keys())
    vector_matrix = np.stack([directions[e] for e in emotion_list])
    correct = total = 0
    for true_emotion, acts in holdout_acts.items():
        if acts is None or true_emotion not in directions:
            continue
        for act in acts:
            act_norm = act / (np.linalg.norm(act) + 1e-9)
            sims = vector_matrix @ act_norm
            pred = emotion_list[np.argmax(sims)]
            if pred == true_emotion:
                correct += 1
            total += 1
    accuracy = correct / total if total > 0 else 0.0
    chance = 1.0 / len(emotion_list)
    print(f"  Discrimination accuracy: {accuracy:.3f} "
          f"(chance={chance:.3f}, n={total})")
    return accuracy, chance

# Run extraction at target layer
print(f"\n=== Full extraction at layer {TARGET_LAYER} ===")
train_acts, holdout_acts = extract_split(TARGET_LAYER)
directions, mean, pc1_dir, pc1_var, pc2_var = compute_directions(train_acts)
cosine_results, anticorrelated = cosine_check(directions)
accuracy, chance = discrimination_accuracy(directions, holdout_acts)

# Save everything unconditionally
suffix = f"qwen3_32b_full_layer{TARGET_LAYER}"
torch.save(
    {e: torch.tensor(v) for e, v in directions.items()},
    OUTPUT_DIR / f"emotion_readout_directions_{suffix}.pt"
)
np.save(OUTPUT_DIR / f"mean_activation_{suffix}.npy", mean)
np.save(OUTPUT_DIR / f"pc1_direction_{suffix}.npy", pc1_dir)

result = {
    "model": MODEL_ID,
    "layer": TARGET_LAYER,
    "n_emotions": len(directions),
    "emotion_labels": list(directions.keys()),
    "pc1_var": float(pc1_var),
    "pc2_var": float(pc2_var),
    "cosine_pairs": cosine_results,
    "anticorrelated_pairs": anticorrelated,
    "discrimination_accuracy": float(accuracy),
    "chance_level": float(chance),
    "readout_verdict": "USABLE" if accuracy > chance * 1.5 else "WEAK"
}
with open(OUTPUT_DIR / f"readout_verdict_{suffix}.txt", "w") as f:
    f.write(json.dumps(result, indent=2))

print(f"\n=== FINAL SUMMARY ===")
print(f"Emotions extracted: {len(directions)}")
print(f"PC1={pc1_var:.1f}%  anticorrelated={anticorrelated}/{len(OPPOSITE_PAIRS)}")
print(f"Discrimination accuracy: {accuracy:.3f} (chance={chance:.3f})")
print("Readout verdict: " + result["readout_verdict"])
print("Done. Stop here and report results.")
