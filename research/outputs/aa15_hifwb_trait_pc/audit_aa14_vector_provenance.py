#!/usr/bin/env python3
"""Read-only audit of released layer matrices against frozen AA-14 inputs."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
AA14 = HERE.parent / "three_model_trait_pca"
ROOT = HERE.parents[2]
VECTORS = ROOT.parent / "assistant-axis" / "downloads" / "hf_vectors"
MODELS = {
    "qwen": ("qwen-3-32b", 48, 64, 5120),
    "llama": ("llama-3.3-70b", 40, 80, 8192),
    "gemma": ("gemma-2-27b", 22, 46, 4608),
}


def explained(x: np.ndarray) -> list[float]:
    z = x - x.mean(0)
    eigen = np.linalg.eigvalsh(z @ z.T)[::-1]
    eigen = np.maximum(eigen[: len(x) - 1], 0)
    return (eigen[:3] / eigen.sum()).tolist()


def main() -> None:
    result = {"aa14_commit": "4488ff8a828b9f690d64ab52814721c2bd7c47de", "models": {}}
    spectra = {}
    import csv
    with (AA14 / "full_spectra.csv").open() as stream:
        for row in csv.DictReader(stream):
            if int(row["pc"]) <= 3:
                spectra.setdefault(row["model"], []).append(float(row["explained_variance"]))
    for model, (folder, layer, n_layers, dim) in MODELS.items():
        files = sorted((VECTORS / folder / "trait_vectors").glob("*.pt"))
        pooled, selected, first = [], [], []
        dtypes, shapes, kinds = set(), set(), set()
        digest = hashlib.sha256()
        for path in files:
            data = path.read_bytes()
            digest.update(f"{path.name}\0{hashlib.sha256(data).hexdigest()}\n".encode())
            tensor = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
            kinds.add(type(tensor).__name__)
            dtypes.add(str(tensor.dtype))
            shapes.add(tuple(tensor.shape))
            assert tuple(tensor.shape) == (n_layers, dim)
            pooled.append(tensor.float().mean(0).numpy())
            selected.append(tensor[layer].float().numpy())
            first.append(tensor[0].float().numpy())
        pooled = np.array(pooled, dtype=np.float64)
        selected = np.array(selected, dtype=np.float64)
        first = np.array(first, dtype=np.float64)
        frozen = np.load(AA14 / f"{model}_trait_pca_directions.npz")
        mean = frozen["mean"].astype(np.float64)
        ratio_pooled, ratio_selected = explained(pooled), explained(selected)
        result["models"][model] = {
            "count": len(files), "tensor_kind": sorted(kinds), "dtypes": sorted(dtypes),
            "shapes": [list(s) for s in sorted(shapes)], "source_aggregate_sha256": digest.hexdigest(),
            "selected_layer_index": layer,
            "median_first_to_selected_layer_l2": float(np.median(np.linalg.norm(first - selected, axis=1))),
            "frozen_mean_max_abs_error_vs_all_layer_mean": float(np.max(abs(mean - pooled.mean(0)))),
            "frozen_mean_max_abs_error_vs_selected_layer": float(np.max(abs(mean - selected.mean(0)))),
            "aa14_pc1_to_pc3": spectra[model],
            "recomputed_all_layer_mean_pc1_to_pc3": ratio_pooled,
            "recomputed_selected_layer_pc1_to_pc3": ratio_selected,
            "aa14_vs_all_layer_mean_max_error": float(np.max(abs(np.array(spectra[model]) - ratio_pooled))),
            "aa14_vs_selected_layer_max_error": float(np.max(abs(np.array(spectra[model]) - ratio_selected))),
        }
    (HERE / "aa14_vector_layer_audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
