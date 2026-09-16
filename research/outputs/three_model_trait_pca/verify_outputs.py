#!/usr/bin/env python3
"""Independent artifact arithmetic, association, and frozen-centering checks."""
import csv
import io
import json
import os
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VECTORS = ROOT.parent / "assistant-axis" / "downloads" / "hf_vectors"
FOLDERS = {"qwen":"qwen-3-32b", "llama":"llama-3.3-70b", "gemma":"gemma-2-27b"}

def rows(name):
    return list(csv.DictReader((HERE/name).open()))

viz = json.loads((HERE/"viewer_data.json").read_text())
source = json.loads((HERE/"source_inventory.json").read_text())
spectrum = rows("full_spectra.csv")
traits = rows("trait_pc_scores.csv")
personas = rows("projected_personas.csv")
checks = {}
for model, folder in FOLDERS.items():
    m = viz["models"][model]
    ts = [r for r in traits if r["model"] == model]
    ps = [r for r in personas if r["model"] == model]
    ss = [r for r in spectrum if r["model"] == model]
    assert len(ts)==240 and len(ps)==275 and len(ss)==239
    assert [r["trait"] for r in ts]==[p["name"] for p in m["traits"]]
    assert [r["persona"] for r in ps]==[p["name"] for p in m["personas"]]
    assert source[model]["traits"]["count"]==240 and source[model]["personas"]["count"]==275
    ratio=np.array([float(r["explained_variance"]) for r in ss])
    cumulative=np.array([float(r["cumulative_variance"]) for r in ss])
    assert abs(ratio.sum()-1)<1e-12 and np.max(abs(np.cumsum(ratio)-cumulative))<1e-12
    assert np.max(abs(ratio[:20]-m["variance"]))<1e-12
    for row, point in zip(ts,m["traits"]):
        assert max(abs(float(row[f"trait_pc{i+1}"])-point["pcs"][i]) for i in range(20))<5.1e-6
    for row, point in zip(ps,m["personas"]):
        assert max(abs(float(row[f"trait_pc{i+1}"])-point["pcs"][i]) for i in range(20))<5.1e-6
        assert abs(float(row["captured_fraction_20"])-point["captured"])<5.1e-6
        assert abs(float(row["residual_norm_20"])-point["residual"])<5.1e-6
        a=float(row["projected_norm_squared_20"])
        b=float(row["residual_norm_20"])**2
        c=float(row["centered_norm_squared"])
        assert abs((a+b-c)/c)<1e-10
    # All 20^3 axis triples have finite coordinates for each of 515 points.
    coordinates=np.array([p["pcs"] for kind in ("personas","traits") for p in m[kind]])
    assert coordinates.shape==(515,20) and np.isfinite(coordinates).all()
    assert sum(bool(p["ood"]) for p in m["personas"])==sum(r["ood"]=="True" for r in ps)
    # Recompute every persona from raw saved tensors using the frozen trait mean and directions.
    frozen=np.load(HERE/f"{model}_trait_pca_directions.npz")
    directions=frozen["directions"].astype("float64")
    mean=frozen["mean"].astype("float64")
    assert np.max(abs(directions[:20]@directions[:20].T-np.eye(20)))<2e-6
    max_error=0
    for row in ps:
        path=VECTORS/folder/"role_vectors"/(row["persona"]+".pt")
        tensor=torch.load(io.BytesIO(path.read_bytes()),map_location="cpu",weights_only=True)
        vector=tensor.float().mean(0).numpy().astype("float64")
        coordinate=(vector-mean)@directions[:20].T
        target=np.array([float(row[f"trait_pc{i+1}"]) for i in range(20)])
        max_error=max(max_error,float(np.max(abs(coordinate-target))))
    assert max_error<.004, (model,max_error) # float32 direction/mean export precision
    checks[model]={"traits":240,"personas":275,"rank":239,"selector_axis_triples":8000,
                   "source_to_viewer_max_abs_error":max_error,"all_coordinates_finite":True,
                   "spectrum_sum":float(ratio.sum()),"cumulative_arithmetic_max_error":float(np.max(abs(np.cumsum(ratio)-cumulative)))}
repro=json.loads((HERE/"qwen_reproduction.json").read_text())
assert max(abs(np.array(repro["new"])-repro["prior"]))<1e-12
assert repro["score_max_abs_difference"]<1e-7
for name in ("viewer_data.json","trait_pc_persona_viewer.html","source_inventory.json"):
    data=(HERE/name).read_text()
    assert "/Users/" not in data and "BEGIN PRIVATE KEY" not in data
(HERE/"verification_artifact_checks.json").write_text(json.dumps(checks,indent=2)+"\n")
print(json.dumps(checks,indent=2))
