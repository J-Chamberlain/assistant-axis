import torch
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from pathlib import Path
import json

DIRECTIONS_FILE = Path(
    "research/emotions/outputs/"
    "emotion_readout_directions_qwen3_32b_full_layer48.pt"
)
OUTPUT_DIR = Path("research/emotions/outputs")

# Load directions
print("Loading emotion readout directions...")
data = torch.load(DIRECTIONS_FILE, map_location="cpu")
emotions = list(data.keys())
vectors = np.stack([data[e].numpy() for e in emotions])
print(f"Loaded {len(emotions)} emotion directions, shape {vectors.shape}")

# Normalize (should already be unit norm, but ensure)
norms = np.linalg.norm(vectors, axis=1, keepdims=True)
vectors_norm = vectors / (norms + 1e-9)

# Elbow method: try k=4 through k=15, record inertia and silhouette
print("\nRunning elbow analysis (k=4 to k=15)...")
inertias = {}
silhouettes = {}
for k in range(4, 16):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(vectors_norm)
    inertias[k] = km.inertia_
    sil = silhouette_score(vectors_norm, labels)
    silhouettes[k] = sil
    print(f"  k={k}: inertia={km.inertia_:.1f}, silhouette={sil:.4f}")

# Select best k by silhouette score
best_k = max(silhouettes, key=silhouettes.get)
print(f"\nBest k by silhouette: {best_k} (score={silhouettes[best_k]:.4f})")

# Also note k=7 result explicitly for comparison with persona clusters
print(f"k=7 silhouette for reference: {silhouettes.get(7, 'not computed'):.4f}")

# Run final clustering at best_k
print(f"\nRunning final clustering at k={best_k}...")
km_final = KMeans(n_clusters=best_k, random_state=42, n_init=20)
labels = km_final.fit_predict(vectors_norm)
centroids = km_final.cluster_centers_

# For each cluster, find the emotion whose direction is
# closest to the cluster centroid (cosine similarity)
cluster_results = {}
for cluster_id in range(best_k):
    member_indices = np.where(labels == cluster_id)[0]
    member_emotions = [emotions[i] for i in member_indices]
    centroid = centroids[cluster_id]
    centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-9)

    # Cosine similarity of each member to centroid
    sims = []
    for idx in member_indices:
        sim = float(np.dot(vectors_norm[idx], centroid_norm))
        sims.append((emotions[idx], sim))
    sims.sort(key=lambda x: x[1], reverse=True)

    representative = sims[0][0]
    top5 = [e for e, s in sims[:5]]

    cluster_results[cluster_id] = {
        "representative": representative,
        "top5_nearest_centroid": top5,
        "all_members": member_emotions,
        "size": len(member_emotions),
        "centroid_similarity_of_rep": sims[0][1]
    }
    print(f"\nCluster {cluster_id} ({len(member_emotions)} emotions):")
    print(f"  Representative: {representative}")
    print(f"  Top 5 nearest centroid: {top5}")
    print(f"  All members: {sorted(member_emotions)}")

# Also run at k=7 for direct comparison with persona cluster count
print(f"\n--- k=7 clustering for persona cluster comparison ---")
km7 = KMeans(n_clusters=7, random_state=42, n_init=20)
labels7 = km7.fit_predict(vectors_norm)
centroids7 = km7.cluster_centers_
cluster_results_k7 = {}
for cluster_id in range(7):
    member_indices = np.where(labels7 == cluster_id)[0]
    member_emotions = [emotions[i] for i in member_indices]
    centroid = centroids7[cluster_id]
    centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-9)
    sims = []
    for idx in member_indices:
        sim = float(np.dot(vectors_norm[idx], centroid_norm))
        sims.append((emotions[idx], sim))
    sims.sort(key=lambda x: x[1], reverse=True)
    representative = sims[0][0]
    cluster_results_k7[cluster_id] = {
        "representative": representative,
        "top5_nearest_centroid": [e for e, s in sims[:5]],
        "all_members": member_emotions,
        "size": len(member_emotions)
    }
    print(f"  Cluster {cluster_id}: rep={representative}, "
          f"members={sorted(member_emotions)[:8]}...")

# Save results
output = {
    "best_k": best_k,
    "best_k_silhouette": silhouettes[best_k],
    "k7_silhouette": silhouettes[7],
    "elbow_analysis": {
        str(k): {"inertia": inertias[k], "silhouette": silhouettes[k]}
        for k in range(4, 16)
    },
    "clusters_best_k": cluster_results,
    "clusters_k7": cluster_results_k7,
    "recommended_emotion_set": [
        cluster_results[i]["representative"]
        for i in range(best_k)
    ],
    "recommended_emotion_set_k7": [
        cluster_results_k7[i]["representative"]
        for i in range(7)
    ]
}

out_path = OUTPUT_DIR / "emotion_cluster_results.json"
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nSaved cluster results to {out_path}")
print(f"\nRecommended emotion set (k={best_k}): "
      f"{output['recommended_emotion_set']}")
print(f"Recommended emotion set (k=7): "
      f"{output['recommended_emotion_set_k7']}")
print("Done.")
