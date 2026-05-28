import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import torch, json, numpy as np
import torch.nn.functional as F
from pathlib import Path

REPO_ROOT = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
VECTOR_ROOT = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b"
ROLE_DIR = VECTOR_ROOT / "role_vectors"
OUTPUT_DIR = REPO_ROOT / "research/visualizations"

# Seven cluster centroid persona representatives
# These are the Qwen-native centroids from calibration
CENTROID_REPS = {
    "editorial": "editor",
    "procedural_professional": "synthesizer",
    "grounded_social": "actor",
    "other": "hoarder",
    "combative_iconoclast": "maverick",
    "mythic_spiritual": "ancient",
    "trickster_chaos": "trickster"
}

# Load centroid vectors
centroid_vecs = {}
for cluster, rep in CENTROID_REPS.items():
    path = ROLE_DIR / f"{rep}.pt"
    if path.exists():
        t = torch.load(path, map_location="cpu").float()
        vec = t.mean(0) if t.dim() > 1 else t
        centroid_vecs[cluster] = F.normalize(vec, dim=0).numpy()
        print(f"Loaded centroid: {cluster} ({rep})")
    else:
        print(f"WARNING: centroid not found for {cluster} ({rep})")

centroid_matrix = np.stack(list(centroid_vecs.values()))
cluster_names = list(centroid_vecs.keys())

# Assign all personas by nearest centroid
assignments = {}
all_files = sorted(ROLE_DIR.glob("*.pt"))
print(f"\nAssigning {len(all_files)} personas to clusters...")

for fpath in all_files:
    try:
        t = torch.load(fpath, map_location="cpu").float()
        vec = t.mean(0) if t.dim() > 1 else t
        vec_norm = F.normalize(vec, dim=0).numpy()
        cosines = centroid_matrix @ vec_norm
        best_idx = np.argmax(cosines)
        best_cluster = cluster_names[best_idx]
        best_score = float(cosines[best_idx])
        second_idx = np.argsort(cosines)[-2]
        second_cluster = cluster_names[second_idx]
        second_score = float(cosines[second_idx])
        assignments[fpath.stem] = {
            "cluster": best_cluster,
            "centroid_cosine": best_score,
            "second_cluster": second_cluster,
            "second_cosine": second_score,
            "margin": best_score - second_score
        }
    except Exception as e:
        print(f"  Skip {fpath.stem}: {e}")
        assignments[fpath.stem] = {"cluster": "unassigned", "centroid_cosine": 0.0}

# Save assignments
out_path = OUTPUT_DIR / "cluster_assignments_full.json"
with open(out_path, "w") as f:
    json.dump(assignments, f, indent=2)

# Report
from collections import Counter
counts = Counter(v["cluster"] for v in assignments.values())
print("\nCluster distribution:")
for cluster, count in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {cluster}: {count}")

# Report low-margin assignments (ambiguous cases)
ambiguous = [(name, v) for name, v in assignments.items() if v.get("margin", 1) < 0.02]
print(f"\nAmbiguous assignments (margin < 0.02): {len(ambiguous)}")
for name, v in sorted(ambiguous, key=lambda x: x[1].get("margin", 0)):
    print(f"  {name}: {v['cluster']} ({v['centroid_cosine']:.4f}) vs {v['second_cluster']} ({v['second_cosine']:.4f}), margin={v['margin']:.4f}")

print(f"\nSaved to {out_path}")
