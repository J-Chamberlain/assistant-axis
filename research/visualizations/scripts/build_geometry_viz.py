import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMBA_NUM_THREADS", "1")

import torch, json, numpy as np
from pathlib import Path
import umap
from sklearn.decomposition import PCA

REPO_ROOT = Path("/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis")
VECTOR_ROOT = REPO_ROOT / "downloads/hf_vectors/qwen-3-32b"
OUTPUT_DIR = REPO_ROOT / "research/visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEVEN_CLUSTER_MAP = {
    "editorial": ["editor", "proofreader", "screener", "grader", "examiner"],
    "procedural_professional": [
        "scientist", "researcher", "analyst", "doctor", "lawyer", "engineer",
        "journalist", "teacher", "programmer", "coach", "therapist", "historian",
        "philosopher", "architect", "accountant", "statistician", "economist",
        "translator", "critic", "auditor", "activist", "anarchist", "revolutionary",
        "consultant", "evaluator", "reviewer", "validator", "debugger", "synthesizer"
    ],
    "grounded_social": [
        "actor", "refugee", "veteran", "bartender", "surfer", "widow",
        "expatriate", "immigrant", "blogger", "podcaster", "moderator",
        "interviewer", "neighbor", "parent", "spouse", "athlete"
    ],
    "other": [
        "robot", "comedian", "narcissist", "procrastinator", "teenager",
        "adolescent", "infant", "toddler", "gamer", "gossip", "hoarder",
        "zealot", "fool", "poet", "amnesiac", "prey", "luddite",
        "caveman", "crystalline"
    ],
    "combative_iconoclast": [
        "maverick", "contrarian", "villain", "cynic", "provocateur",
        "skeptic", "workaholic", "competitor", "devil's_advocate"
    ],
    "mythic_spiritual": [
        "ancient", "oracle", "mystic", "prophet", "shaman", "angel",
        "demon", "ghost", "wizard", "sage", "monk", "ascetic",
        "leviathan", "egregore", "hive", "swarm", "genie", "deity"
    ],
    "trickster_chaos": [
        "trickster", "jester", "clown", "spy", "shapeshifter", "con_artist"
    ]
}

def get_cluster(name):
    for cluster, members in SEVEN_CLUSTER_MAP.items():
        if name.lower() in [m.lower() for m in members]:
            return cluster
    return "unassigned"

def load_vectors(vector_dir, label="role"):
    vectors, names, labels = [], [], []
    vdir = Path(vector_dir)
    if not vdir.exists():
        print(f"  {label} directory not found: {vdir}")
        return None, None, None
    files = sorted(vdir.glob("*.pt"))
    print(f"  Loading {len(files)} {label} vectors...")
    for fpath in files:
        try:
            t = torch.load(fpath, map_location="cpu").float()
            vec = t.mean(0) if t.dim() > 1 else t
            arr = np.nan_to_num(vec.numpy().astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
            vectors.append(arr)
            names.append(fpath.stem)
            labels.append(fpath.stem)
        except Exception as e:
            print(f"  Skip {fpath.stem}: {e}")
    if not vectors:
        return None, None, None
    return np.stack(vectors), names, labels

# Load role vectors
print("Loading role vectors...")
role_vecs, role_names, _ = load_vectors(VECTOR_ROOT / "role_vectors", "role")

# Load trait vectors
print("Loading trait vectors...")
trait_vecs, trait_names, _ = load_vectors(VECTOR_ROOT / "trait_vectors", "trait")

# Try emotion vectors
print("Loading emotion vectors...")
emotion_dirs = ["emotion_vectors", "emotions", "emotion"]
emotion_vecs, emotion_names = None, None
for ed in emotion_dirs:
    ev, en, _ = load_vectors(VECTOR_ROOT / ed, "emotion")
    if ev is not None:
        emotion_vecs, emotion_names = ev, en
        print(f"  Found emotion vectors at {ed}")
        break

# Also load assistant axis for projection coloring
axis_path = VECTOR_ROOT / "assistant_axis.pt"
axis_vec = None
if axis_path.exists():
    av = torch.load(axis_path, map_location="cpu").float()
    axis_vec = av.mean(0).numpy() if av.dim() > 1 else av.numpy()
    axis_vec = np.nan_to_num(axis_vec.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    axis_vec = axis_vec / np.linalg.norm(axis_vec)
    print("Loaded assistant axis vector")

def compute_umap(vecs, n_components=3, n_neighbors=15, min_dist=0.1):
    reducer = umap.UMAP(
        n_components=n_components, n_neighbors=n_neighbors,
        min_dist=min_dist, random_state=42, metric="cosine",
        n_jobs=1, low_memory=True
    )
    return reducer.fit_transform(vecs)

def compute_axis_projections(vecs, axis):
    if axis is None:
        return np.zeros(len(vecs))
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    normalized = vecs / (norms + 1e-8)
    normalized = np.nan_to_num(normalized, nan=0.0, posinf=0.0, neginf=0.0)
    return np.nan_to_num(normalized @ axis, nan=0.0, posinf=0.0, neginf=0.0)

def compute_nearest_neighbors(vecs, names, k=5):
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    normalized = vecs / (norms + 1e-8)
    normalized = np.nan_to_num(normalized, nan=0.0, posinf=0.0, neginf=0.0)
    sim_matrix = np.nan_to_num(normalized @ normalized.T, nan=0.0, posinf=0.0, neginf=0.0)
    nn_data = {}
    for i, name in enumerate(names):
        sims = sim_matrix[i]
        sorted_idx = np.argsort(sims)[::-1]
        neighbors = []
        for j in sorted_idx[1:k+1]:
            neighbors.append({"name": names[j], "cosine": float(sims[j])})
        nn_data[name] = neighbors
    return nn_data

def compute_pca(vecs, names, label):
    pca3 = PCA(n_components=3, random_state=42)
    pca3d = pca3.fit_transform(vecs)
    pca2 = PCA(n_components=2, random_state=42)
    pca2d = pca2.fit_transform(vecs)
    variance = {
        "pc1_explained": float(pca3.explained_variance_ratio_[0]),
        "pc2_explained": float(pca3.explained_variance_ratio_[1]),
        "pc3_explained": float(pca3.explained_variance_ratio_[2]),
        "pc1_cumulative": float(pca3.explained_variance_ratio_[0]),
        "pc1_pc2_cumulative": float(sum(pca3.explained_variance_ratio_[:2])),
        "pc1_pc2_pc3_cumulative": float(sum(pca3.explained_variance_ratio_[:3]))
    }
    extremes = {}
    for comp_idx in range(3):
        scores = pca3d[:, comp_idx]
        order = np.argsort(scores)
        extremes[f"pc{comp_idx + 1}"] = {
            "positive": [
                {"name": names[i], "score": float(scores[i])}
                for i in order[::-1][:10]
            ],
            "negative": [
                {"name": names[i], "score": float(scores[i])}
                for i in order[:10]
            ]
        }
    print(
        f"{label} PCA variance: "
        f"PC1={variance['pc1_explained']:.6f}, "
        f"PC2={variance['pc2_explained']:.6f}, "
        f"PC3={variance['pc3_explained']:.6f}"
    )
    for comp_idx in range(3):
        key = f"pc{comp_idx + 1}"
        pos = ", ".join(x["name"] for x in extremes[key]["positive"][:5])
        neg = ", ".join(x["name"] for x in extremes[key]["negative"][:5])
        print(f"  {label} PCA-{comp_idx + 1} positive: {pos}")
        print(f"  {label} PCA-{comp_idx + 1} negative: {neg}")
    return pca3d, pca2d, variance, extremes

all_datasets = {
    "metadata": {
        "model_used": "GPT-5.5",
        "source_model": "Qwen/Qwen3-32B",
        "vector_root": str(VECTOR_ROOT),
    }
}

# Process role vectors
if role_vecs is not None:
    print("Computing UMAP for role vectors (3D)...")
    role_umap3 = compute_umap(role_vecs, n_components=3)
    print("Computing UMAP for role vectors (2D)...")
    role_umap2 = compute_umap(role_vecs, n_components=2)

    # Load full cluster assignments
    assignments_path = OUTPUT_DIR / "cluster_assignments_full.json"
    with open(assignments_path) as f:
        full_assignments = json.load(f)

    # PCA projection (3D and 2D)
    print("Computing PCA for role vectors...")
    pca3 = PCA(n_components=3, random_state=42)
    role_pca3 = pca3.fit_transform(role_vecs)
    pca2 = PCA(n_components=2, random_state=42)
    role_pca2 = pca2.fit_transform(role_vecs)

    # Record explained variance
    pca_variance = {
        "pc1_explained": float(pca3.explained_variance_ratio_[0]),
        "pc2_explained": float(pca3.explained_variance_ratio_[1]),
        "pc3_explained": float(pca3.explained_variance_ratio_[2]),
        "pc1_cumulative": float(pca3.explained_variance_ratio_[0]),
        "pc1_pc2_cumulative": float(sum(pca3.explained_variance_ratio_[:2])),
        "pc1_pc2_pc3_cumulative": float(sum(pca3.explained_variance_ratio_[:3]))
    }
    print(f"PCA variance: PC1={pca_variance['pc1_explained']:.3f}, PC2={pca_variance['pc2_explained']:.3f}, PC3={pca_variance['pc3_explained']:.3f}")

    # Check alignment of PC1 with assistant axis
    if axis_vec is not None:
        pc1_direction = pca3.components_[0]
        pc1_direction = pc1_direction / np.linalg.norm(pc1_direction)
        pc1_axis_alignment = float(abs(pc1_direction @ axis_vec))
        print(f"PC1 alignment with assistant axis: {pc1_axis_alignment:.4f}")
        pca_variance["pc1_axis_alignment"] = pc1_axis_alignment

    role_axis_proj = compute_axis_projections(role_vecs, axis_vec)
    role_nn = compute_nearest_neighbors(role_vecs, role_names)
    all_datasets["roles"] = {
        "names": role_names,
        "umap3d": role_umap3.tolist(),
        "umap2d": role_umap2.tolist(),
        "pca3d": role_pca3.tolist(),
        "pca2d": role_pca2.tolist(),
        "pca_variance": pca_variance,
        "clusters": [full_assignments.get(n, {}).get("cluster", "unassigned") for n in role_names],
        "cluster_cosines": [full_assignments.get(n, {}).get("centroid_cosine", 0.0) for n in role_names],
        "cluster_margins": [full_assignments.get(n, {}).get("margin", 0.0) for n in role_names],
        "axis_projections": role_axis_proj.tolist(),
        "nearest_neighbors": role_nn
    }
    print(f"Role vectors processed: {len(role_names)} personas")

# Process trait vectors
if trait_vecs is not None:
    print("Computing UMAP for trait vectors...")
    trait_umap3 = compute_umap(trait_vecs, n_components=3)
    trait_umap2 = compute_umap(trait_vecs, n_components=2)
    print("Computing PCA for trait vectors...")
    trait_pca3, trait_pca2, trait_pca_variance, trait_pca_extremes = compute_pca(
        trait_vecs, trait_names, "Trait"
    )
    trait_axis_proj = compute_axis_projections(trait_vecs, axis_vec)
    trait_nn = compute_nearest_neighbors(trait_vecs, trait_names)
    all_datasets["traits"] = {
        "names": trait_names,
        "umap3d": trait_umap3.tolist(),
        "umap2d": trait_umap2.tolist(),
        "pca3d": trait_pca3.tolist(),
        "pca2d": trait_pca2.tolist(),
        "pca_variance": trait_pca_variance,
        "pca_extremes": trait_pca_extremes,
        "pca_source": "Layer-mean Qwen/Qwen3-32B Lu-style activation-space trait vectors from downloads/hf_vectors/qwen-3-32b/trait_vectors/*.pt; each [64,5120] tensor is averaged across layers to one 5120-D trait vector before PCA.",
        "axis_projections": trait_axis_proj.tolist(),
        "nearest_neighbors": trait_nn
    }
    print(f"Trait vectors processed: {len(trait_names)} traits")

# Process emotion vectors
if emotion_vecs is not None:
    print("Computing UMAP for emotion vectors...")
    emo_umap3 = compute_umap(emotion_vecs, n_components=3)
    emo_umap2 = compute_umap(emotion_vecs, n_components=2)
    emo_axis_proj = compute_axis_projections(emotion_vecs, axis_vec)
    emo_nn = compute_nearest_neighbors(emotion_vecs, emotion_names)
    all_datasets["emotions"] = {
        "names": emotion_names,
        "umap3d": emo_umap3.tolist(),
        "umap2d": emo_umap2.tolist(),
        "axis_projections": emo_axis_proj.tolist(),
        "nearest_neighbors": emo_nn
    }
    print(f"Emotion vectors processed: {len(emotion_names)} emotions")

# Save data
output_path = OUTPUT_DIR / "geometry_viz_data.json"
with open(output_path, "w") as f:
    json.dump(all_datasets, f)
print(f"Data saved to {output_path}")
print(f"Datasets available: {[k for k in all_datasets.keys() if k != 'metadata']}")

html_path = OUTPUT_DIR / "persona_geometry_explorer.html"
if html_path.exists():
    content = html_path.read_text()
    marker = "    const VIZ_DATA = "
    start = content.find(marker)
    if start != -1:
        value_start = start + len(marker)
        value_end = content.find(";\n", value_start)
        if value_end != -1:
            embedded = json.dumps(all_datasets, separators=(",", ":"))
            html_path.write_text(content[:value_start] + embedded + content[value_end:])
            print(f"Embedded updated data into {html_path}")
