import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "/root/models/gemma-2-27b-it"
STORIES_PATH = "/root/emotion_stories/expression/stories.parquet"
NEUTRAL_PATH = "/root/emotion_stories/expression/neutral_stories.parquet"
OUTPUT_DIR = Path("research/emotions/outputs")
TARGET_LAYER = 21
BATCH_SIZE = 64
MAX_LENGTH = 512

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading model...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
model.config.use_cache = False
model.eval()
print("Model loaded", flush=True)

captured = []

def layer_hook(_module, _inputs, output):
    hidden = output[0] if isinstance(output, tuple) else output
    captured.append(hidden.detach())

handle = model.model.layers[TARGET_LAYER].register_forward_hook(layer_hook)

def batched_last_token_hidden(texts, batch_size=BATCH_SIZE):
    all_vecs = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        captured.clear()
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
        )
        inputs = {k: v.to("cuda:0") for k, v in inputs.items()}
        with torch.no_grad():
            model.model(**inputs, use_cache=False)
        if not captured:
            raise RuntimeError("Layer hook did not capture activations")
        hidden = captured[-1]
        last_indices = inputs["attention_mask"].sum(dim=1) - 1
        batch_indices = torch.arange(hidden.shape[0], device=hidden.device)
        vecs = hidden[batch_indices, last_indices.to(hidden.device), :].float().cpu()
        all_vecs.append(vecs)
    return torch.cat(all_vecs, dim=0)

print("Loading stories...", flush=True)
stories_df = pd.read_parquet(STORIES_PATH)
neutral_df = pd.read_parquet(NEUTRAL_PATH)
emotions = sorted(stories_df["emotion"].unique().tolist())
print(f"Found {len(emotions)} emotions, {len(stories_df)} stories total", flush=True)
print(f"Found {len(neutral_df)} neutral stories", flush=True)
print(f"Batch size: {BATCH_SIZE}", flush=True)

print("Extracting neutral story activations...", flush=True)
neutral_texts = neutral_df["story"].astype(str).tolist()
neutral_chunks = []
for start in range(0, len(neutral_texts), BATCH_SIZE * 10):
    chunk = neutral_texts[start:start + BATCH_SIZE * 10]
    neutral_chunks.append(batched_last_token_hidden(chunk))
    print(f"  Neutral: {min(start + len(chunk), len(neutral_texts))}/{len(neutral_texts)}", flush=True)
neutral_matrix = torch.cat(neutral_chunks, dim=0)

neutral_np = neutral_matrix.numpy()
neutral_centered = neutral_np - neutral_np.mean(axis=0)
U, S, Vt = np.linalg.svd(neutral_centered, full_matrices=False)
explained_var = (S ** 2) / (S ** 2).sum()
cumvar = np.cumsum(explained_var)
n_confound_pcs = int(np.searchsorted(cumvar, 0.50)) + 1
confound_directions = torch.tensor(Vt[:n_confound_pcs], dtype=torch.float32)
print(f"Removing {n_confound_pcs} confound PCs (explaining 50% variance)", flush=True)

def remove_confounds(vec, confound_dirs):
    v = vec.clone()
    for direction in confound_dirs:
        direction = direction / direction.norm()
        v = v - (v @ direction) * direction
    return v

print("Extracting emotion vectors...", flush=True)
emotion_vectors = {}
emotion_index = {}

for idx, emotion in enumerate(emotions):
    emotion_index[str(idx)] = emotion
    emotion_texts = stories_df.loc[stories_df["emotion"] == emotion, "story"].astype(str).tolist()
    hiddens = []
    for start in range(0, len(emotion_texts), BATCH_SIZE * 10):
        chunk = emotion_texts[start:start + BATCH_SIZE * 10]
        hiddens.append(batched_last_token_hidden(chunk))
    mean_hidden = torch.cat(hiddens, dim=0).mean(dim=0)
    mean_hidden_clean = remove_confounds(mean_hidden, confound_directions)
    mean_hidden_norm = mean_hidden_clean / mean_hidden_clean.norm()
    emotion_vectors[emotion] = mean_hidden_norm
    print(f"  Processed {idx + 1}/{len(emotions)} emotions: {emotion}", flush=True)

handle.remove()

emotion_tensor = torch.stack([emotion_vectors[e] for e in emotions])
torch.save(emotion_tensor, OUTPUT_DIR / "emotion_vectors_gemma2_27b_layer21.pt")
with open(OUTPUT_DIR / "emotion_index.json", "w") as f:
    json.dump(emotion_index, f, indent=2)

print(f"Saved emotion tensor: {emotion_tensor.shape}", flush=True)
print(f"Saved emotion index: {len(emotion_index)} emotions", flush=True)

print("\nVALIDATION", flush=True)
print("=" * 50, flush=True)
pca = PCA(n_components=10)
em_np = emotion_tensor.numpy()
pca.fit(em_np)
print(f"PC1 variance explained: {pca.explained_variance_ratio_[0] * 100:.1f}%", flush=True)
print(f"PC2 variance explained: {pca.explained_variance_ratio_[1] * 100:.1f}%", flush=True)
print("Expected ~40% and ~18% if replication successful", flush=True)

def cosim(a, b):
    return float((a @ b) / (a.norm() * b.norm()))

em_dict = {e: emotion_vectors[e] for e in emotions}
pairs_to_check = [
    ("afraid", "terrified", "should be high >0.7"),
    ("calm", "peaceful", "should be high >0.7"),
    ("afraid", "calm", "should be low or negative"),
    ("happy", "sad", "should be negative"),
    ("desperate", "hopeful", "should be negative"),
]

validation_lines = []
validation_lines.append("Emotion Vector Validation - Gemma 2 27B")
validation_lines.append("Date: 2026-05-19")
validation_lines.append("Methodology: Sofroniew et al. 2026 replication")
validation_lines.append("Stories: ryancodrai/emotion-probes")
validation_lines.append(f"Layer: {TARGET_LAYER}")
validation_lines.append(f"Batch size: {BATCH_SIZE}")
validation_lines.append(f"Confound PCs removed: {n_confound_pcs}")
validation_lines.append(f"PC1 variance: {pca.explained_variance_ratio_[0] * 100:.1f}%")
validation_lines.append(f"PC2 variance: {pca.explained_variance_ratio_[1] * 100:.1f}%")
validation_lines.append(f"Emotions extracted: {len(emotions)}")
validation_lines.append("")
validation_lines.append("Cosine similarity validation:")

print("\nCosine similarity validation:", flush=True)
for e1, e2, expected in pairs_to_check:
    if e1 in em_dict and e2 in em_dict:
        sim = cosim(em_dict[e1], em_dict[e2])
        line = f"  {e1} vs {e2}: {sim:.3f} ({expected})"
        print(line, flush=True)
        validation_lines.append(line)

for anchor in ["afraid", "calm"]:
    if anchor in em_dict:
        sims = {e: cosim(em_dict[anchor], em_dict[e]) for e in emotions if e != anchor}
        top5 = sorted(sims.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"\nTop 5 most similar to {anchor}:", flush=True)
        validation_lines.append("")
        validation_lines.append(f"Top 5 most similar to {anchor}:")
        for e, s in top5:
            line = f"  {e}: {s:.3f}"
            print(line, flush=True)
            validation_lines.append(line)

with open(OUTPUT_DIR / "emotion_vector_validation_layer21.txt", "w") as f:
    f.write("\n".join(validation_lines) + "\n")

print("\nExtraction complete.", flush=True)
