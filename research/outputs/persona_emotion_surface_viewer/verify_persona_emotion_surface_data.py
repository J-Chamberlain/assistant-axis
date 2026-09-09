#!/usr/bin/env python3
"""Independent source, normalization, mask, and artifact-integrity checks."""
import csv
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from scipy.spatial import Delaunay, cKDTree
from scipy.stats import rankdata
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    data = json.loads((HERE / "persona_emotion_surface_data.json").read_text())
    manifest = json.loads((HERE / "persona_emotion_surface_manifest.json").read_text())
    geometry = json.loads((ROOT / "research/visualizations/geometry_viz_data.json").read_text())["roles"]
    names = [r["name"] for r in data["roles"]]
    coordinates = np.array([r["pcs"] for r in data["roles"]])
    assert names == geometry["names"] and len(set(names)) == 275
    np.testing.assert_array_equal(coordinates, geometry["pca3d"])
    with (HERE / "persona_emotion_scores.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len({(r["persona"], r["emotion"]) for r in rows}) == 1650
    lookup = {(r["persona"], r["emotion"]): r for r in rows}
    bank = torch.load(ROOT / "research/emotions/outputs/emotion_readout_directions_qwen3_32b_full_layer48.pt",
                      map_location="cpu", weights_only=True)
    for emotion in data["emotions"]:
        raw, z = np.array(emotion["raw"]), np.array(emotion["z"])
        np.testing.assert_allclose(z, (raw - raw.mean()) / raw.std(), atol=1e-12)
        np.testing.assert_allclose(emotion["percentile"], 100 * (rankdata(raw) - 0.5) / 275)
        direction = bank[emotion["key"]].double().numpy()
        for i, name in enumerate(names):
            row = lookup[name, emotion["key"]]
            assert float(row["raw_affinity"]) == raw[i] and float(row["z_score"]) == z[i]
            np.testing.assert_array_equal([float(row[f"pc{p}"]) for p in (1, 2, 3)], coordinates[i])
        # Independently re-read sources for a deterministic coverage sample.
        for i in range(0, 275, 25):
            vector = torch.load(ROOT / f"downloads/hf_vectors/qwen-3-32b/role_vectors/{names[i]}.pt",
                                map_location="cpu", weights_only=True)[47].double().numpy()
            expected = np.dot(vector, direction) / (np.linalg.norm(vector) * np.linalg.norm(direction))
            np.testing.assert_allclose(expected, raw[i], atol=1e-12)
    for view in data["views"].values():
        points = (coordinates[:, view["axes"]] - view["fit_center"]) / view["fit_common_scale"]
        xx, yy = np.meshgrid(view["x"], view["y"])
        grid = (np.c_[xx.ravel(), yy.ravel()] - view["fit_center"]) / view["fit_common_scale"]
        unique = np.unique(points, axis=0)
        expected = (Delaunay(unique).find_simplex(grid) >= 0) & (cKDTree(unique).query(grid, k=6)[0][:, -1] <= view["support_sixth_neighbor_radius"])
        for level in view["levels"]:
            for mesh in level["grids"]:
                np.testing.assert_array_equal([v is not None for r in mesh for v in r], expected)
                assert max(abs(v) for r in mesh for v in r if v is not None) < data["z_limit"]
    for item in manifest["sources"]:
        assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
    for item in manifest["outputs"]:
        assert hashlib.sha256((HERE / item["filename"]).read_bytes()).hexdigest() == item["sha256"], item["filename"]
    result = {"status": "passed", "personas": 275, "score_rows": 1650, "independent_source_cosines": 66,
              "checks": ["exact canonical coordinates", "unique persona/emotion rows", "CSV/bundle equality",
                         "population normalization and midrank percentiles", "independent layer-47 cosine sample",
                         "all 54 support masks", "no clipping", "all source and output hashes"]}
    (HERE / "persona_emotion_surface_data_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
