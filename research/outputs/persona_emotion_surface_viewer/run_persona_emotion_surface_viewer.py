#!/usr/bin/env python3
"""Build an offline Qwen emotion-affinity landscape from existing CPU tensors."""

import argparse
import ast
import base64
import csv
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import time
from datetime import datetime, timezone

# The local Mac scientific runtime links two OpenMP libraries; use one thread.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import numpy as np
import plotly
from plotly.offline import get_plotlyjs
import scipy
from scipy.interpolate import RBFInterpolator
from scipy.spatial import Delaunay, cKDTree
from scipy.stats import rankdata, spearmanr
import torch

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
GEOMETRY = ROOT / "research/visualizations/geometry_viz_data.json"
VECTOR_DIR = ROOT / "downloads/hf_vectors/qwen-3-32b/role_vectors"
EMOTION_DIR = ROOT / "research/emotions/outputs"
DIRECTIONS = EMOTION_DIR / "emotion_readout_directions_qwen3_32b_full_layer48.pt"
EXTRACTOR = ROOT / "research/emotions/scripts/extract_qwen_full.py"
BOUNDARY = ROOT / "research/outputs/a100_two_role_activation_cloud_pilot/boundary_test_results.json"
EMOTIONS = [("Joy", "joyful"), ("Calm", "calm"), ("Sadness", "sad"),
            ("Fear", "afraid"), ("Anger", "angry"), ("Disgust", "disgusted")]
SMOOTHING = [("Detail", 0.003), ("Balanced", 0.03), ("Gentle", 0.3)]
ROLE_LAYER = 47
GRID_SIZE = 61


def read_json(path):
    return json.loads(path.read_text())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump_json(path, value, compact=False):
    path.write_text(json.dumps(value, allow_nan=False, indent=None if compact else 2,
                               separators=(",", ":") if compact else None) + "\n")


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def unit_rows(matrix):
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    if not np.isfinite(matrix).all() or np.any(norms < 1e-12):
        raise ValueError("Nonfinite or zero-norm source vector")
    return matrix / norms


def standardized(values):
    spread = values.std(axis=0, ddof=0)
    if np.any(spread < 1e-6):
        raise ValueError("An emotion channel has insufficient raw variation; do not fabricate a surface")
    return (values - values.mean(axis=0)) / spread


def verify_startup():
    manifest = (ROOT / "research/STARTUP_MANIFEST.md").read_text()
    result = {}
    for path in ["research/RESEARCH_STATE.md", "research/THREAD_START.md", "research/CLAIMS_REGISTER.md"]:
        section = manifest.split(f"### `{path}`")[1].split("\n### ")[0]
        expected = re.search(r"SHA256 content hash: `([^`]+)`", section).group(1)
        actual = sha256(ROOT / path)
        if actual != expected:
            raise ValueError(f"Startup manifest mismatch: {path}")
        result[path] = actual
    return result


def verify_boundary():
    source = EXTRACTOR.read_text()
    tree = ast.parse(source)
    target = next(n.value.value for n in tree.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "TARGET_LAYER" for t in n.targets))
    extraction = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                      and n.name == "get_last_token_activation")
    expression = ast.unparse(extraction)
    assert target == 48 and "out.hidden_states[layer][0, -1, :]" in expression
    assert ROLE_LAYER + 1 == target
    boundary = read_json(BOUNDARY)
    assert boundary["conclusion"] == "hook_matches_hidden_states_49"
    assert boundary["mean_coordinate_delta_l2_hook_vs_hidden_states_49"] < 1e-8
    hooks = (ROOT / "assistant_axis/internals/activations.py").read_text()
    assert "layer_list = list(range(len(self.probing_model.get_layers())))" in hooks
    assert "target_layer.register_forward_hook" in hooks
    assert "activations = torch.stack(activations)" in hooks
    return {
        "readout_hidden_state_index": target,
        "released_role_tensor_row": ROLE_LAYER,
        "role_row_semantics": "decoder block 47 output, corresponding to hidden_states[48]",
        "evidence": "source layer ordering and Qwen hidden-state semantics; prior empirical block-48 boundary test",
        "new_gpu_boundary_test": False,
        "remaining_transfer_assumption": "story last-token direction applied to response-mean role centroid",
        "display_geometry": "existing PCA of role tensors averaged across 64 layers; no PCA refit",
    }


def make_scores():
    geometry = read_json(GEOMETRY)["roles"]
    names = geometry["names"]
    assert len(names) == len(set(names)) == 275
    coords = np.asarray(geometry["pca3d"], dtype=np.float64)
    assert coords.shape == (275, 3) and np.isfinite(coords).all()
    bank = torch.load(DIRECTIONS, map_location="cpu", weights_only=True)
    assert len(bank) == 171
    directions = np.stack([bank[key].float().numpy().astype(np.float64) for _, key in EMOTIONS])
    assert directions.shape == (6, 5120)
    directions = unit_rows(directions)
    matrices = {"matched_row47": [], "adjacent_row48": [], "layer_mean": []}
    sources = []
    for name in names:
        path = VECTOR_DIR / f"{name}.pt"
        tensor = torch.load(path, map_location="cpu", weights_only=True).float().numpy().astype(np.float64)
        if tensor.shape != (64, 5120) or not np.isfinite(tensor).all():
            raise ValueError(f"Unexpected role tensor: {path}")
        matrices["matched_row47"].append(tensor[ROLE_LAYER])
        matrices["adjacent_row48"].append(tensor[48])
        matrices["layer_mean"].append(tensor.mean(0))
        sources.append({"path": str(path.relative_to(ROOT)), "sha256": sha256(path)})
    matrices = {k: np.stack(v) for k, v in matrices.items()}
    raw = unit_rows(matrices["matched_row47"]) @ directions.T
    z = standardized(raw)
    percentiles = np.stack([100 * (rankdata(raw[:, e], method="average") - 0.5) / len(names)
                            for e in range(6)], axis=1)
    mean = np.load(EMOTION_DIR / "mean_activation_qwen3_32b_full_layer48.npy", allow_pickle=False)
    nuisance = np.load(EMOTION_DIR / "pc1_direction_qwen3_32b_full_layer48.npy", allow_pickle=False)
    assert mean.shape == nuisance.shape == (5120,)
    nuisance = nuisance.astype(np.float64) / np.linalg.norm(nuisance)
    centered = matrices["matched_row47"] - mean
    cleaned = centered - np.outer(centered @ nuisance, nuisance)
    variants = {k: unit_rows(v) @ directions.T for k, v in matrices.items() if k != "matched_row47"}
    variants["story_mean_centered_pc_removed"] = unit_rows(cleaned) @ directions.T
    sensitivity = []
    emotions = []
    for e, (label, key) in enumerate(EMOTIONS):
        primary_top = set(np.argsort(raw[:, e])[-20:])
        for variant, values in variants.items():
            sensitivity.append({
                "emotion": key, "variant": variant,
                "spearman_vs_primary": float(spearmanr(raw[:, e], values[:, e]).statistic),
                "top20_overlap_fraction": len(primary_top & set(np.argsort(values[:, e])[-20:])) / 20,
                "status": "sensitivity only; not the displayed measurement",
            })
        emotions.append({"key": key, "label": label, "raw": raw[:, e].tolist(), "z": z[:, e].tolist(),
                         "percentile": percentiles[:, e].tolist(),
                         "raw_mean": float(raw[:, e].mean()), "raw_std": float(raw[:, e].std()),
                         "highest": [names[i] for i in np.argsort(z[:, e])[-5:][::-1]],
                         "lowest": [names[i] for i in np.argsort(z[:, e])[:5]]})
    rows = []
    for i, name in enumerate(names):
        for e, (_, key) in enumerate(EMOTIONS):
            rows.append({"persona": name, "emotion": key, "pc1": coords[i, 0], "pc2": coords[i, 1],
                         "pc3": coords[i, 2], "raw_affinity": raw[i, e], "z_score": z[i, e],
                         "percentile_midrank": percentiles[i, e], "role_layer_index": ROLE_LAYER,
                         "readout_hidden_state_index": 48, "reference_n": len(names)})
    assert np.allclose(z.mean(0), 0, atol=1e-10) and np.allclose(z.std(0), 1, atol=1e-10)
    return names, coords, emotions, z, rows, sensitivity, sources


def nullable_grid(values, mask):
    rounded = np.round(values, 6)
    return [[float(v) if valid else None for v, valid in zip(row, ok)] for row, ok in zip(rounded, mask)]


def make_meshes(coords, z):
    views, diagnostics = {}, []
    max_abs = float(np.max(np.abs(z)))
    for axes in itertools.combinations(range(3), 2):
        xy = coords[:, axes]
        center = xy.mean(0)
        # One common scale preserves relative PC distances in the surface fit.
        scale = float(np.sqrt(np.mean(np.var(xy, axis=0))))
        points = (xy - center) / scale
        unique, inverse = np.unique(points, axis=0, return_inverse=True)
        targets = np.stack([z[inverse == k].mean(0) for k in range(len(unique))])
        tree = cKDTree(unique)
        distances, _ = tree.query(unique, k=min(6, len(unique)))
        radius = float(np.quantile(distances[:, -1], 0.9))
        low, high = xy.min(0), xy.max(0)
        x = np.linspace(low[0], high[0], GRID_SIZE)
        y = np.linspace(low[1], high[1], GRID_SIZE)
        xx, yy = np.meshgrid(x, y)
        grid = (np.column_stack([xx.ravel(), yy.ravel()]) - center) / scale
        hull = Delaunay(unique)
        sixth, _ = tree.query(grid, k=min(6, len(unique)))
        supported = ((hull.find_simplex(grid) >= 0) & (sixth[:, -1] <= radius)).reshape(xx.shape)
        levels = []
        for label, smooth in SMOOTHING:
            fit = RBFInterpolator(unique, targets, kernel="thin_plate_spline", smoothing=smooth, degree=1)
            grid_values = fit(grid).reshape(GRID_SIZE, GRID_SIZE, 6)
            fitted = fit(points)
            assert np.isfinite(fitted).all() and np.isfinite(grid_values).all()
            max_abs = max(max_abs, float(np.max(np.abs(grid_values[supported]))))
            rmse = np.sqrt(np.mean((fitted - z) ** 2, axis=0))
            levels.append({"label": label, "smoothing": smooth,
                           "grids": [nullable_grid(grid_values[:, :, e], supported) for e in range(6)],
                           "fitted_nodes": [fitted[:, e].tolist() for e in range(6)], "fit_rmse": rmse.tolist()})
            for e, (_, key) in enumerate(EMOTIONS):
                diagnostics.append({"x_axis": axes[0] + 1, "y_axis": axes[1] + 1, "emotion": key,
                                    "smoothing_label": label, "smoothing": smooth, "in_sample_fit_rmse_z": float(rmse[e]),
                                    "max_abs_node_surface_gap_z": float(np.max(np.abs(fitted[:, e] - z[:, e]))),
                                    "supported_grid_fraction": float(supported.mean()),
                                    "coincident_projection_count": int(len(points) - len(unique))})
        views[f"{axes[0]}_{axes[1]}"] = {
            "axes": list(axes), "x": x.tolist(), "y": y.tolist(), "levels": levels,
            "fit_center": center.tolist(), "fit_common_scale": scale,
            "support_sixth_neighbor_radius": radius, "supported_grid_fraction": float(supported.mean()),
        }
    return views, diagnostics, float(np.ceil(max_abs * 2) / 2 + 0.5)


def methodology(manifest, sensitivity, diagnostics):
    lines = ["# Qwen Persona Emotion Surface Viewer: Methodology", "",
             f"Generated UTC: {manifest['generated_utc']}", "Author: Codex; exact runtime model identifier unavailable. Activation model: Qwen/Qwen3-32B.", "",
             "## What Was Built", "",
             "An offline HTML viewer with 275 exact persona nodes, six emotion-slider stops, all six ordered PC pairs, "
             "three surface smoothing levels, node tooltips and pinned selection, camera persistence, rotation, zoom, "
             "surface/connector toggles, and a zero-height reference. The UI also provides a vivid fixed symmetric "
             "z-score color scale, a fabric-only mode that hides nodes and reference guides, and synchronized "
             "yaw/pitch/roll/zoom dials with Isometric, Top, Front, and Side presets. No model inference, new "
             "activations, or judge calls were used; this update changes presentation controls only.", "",
             "## Sources and Layer Alignment", "",
             "The displayed PC coordinates are copied exactly from `research/visualizations/geometry_viz_data.json`. "
             "Its builder averages released role tensors across all 64 layers before PCA. No PCA is fitted by this tool.", "",
             "Emotion directions come from `research/emotions/outputs/emotion_readout_directions_qwen3_32b_full_layer48.pt`. "
             "The historical extractor uses the last token of supplied emotion stories at `hidden_states[48]`. "
             "The released role tensors stack decoder-block outputs in ascending layer order; row 47 is the matching intermediate "
             "boundary under the source-documented Qwen hidden-state convention. The prior A100 test independently established "
             "that block 48 matches `hidden_states[49]`. This tool therefore uses role row 47, not row 48. "
             "This mapping is based on inspected source conventions plus the existing boundary test; no new GPU equivalence test was run.", "",
             "The remaining transfer assumption is story-last-token emotion directions versus response-mean role centroids. "
             "Layer correspondence does not validate functional emotion measurement or eliminate pooling/domain differences.", "",
             "## Scores", "",
             "Primary affinity is cosine(role row 47, saved emotion direction). Role vectors are normalized without centering, "
             "matching the historical held-out nearest-direction readout's input normalization. Saved emotion directions already "
             "incorporate training-mean subtraction and removal of the leading story-activation PC. Unit normalization is repeated "
             "only to remove floating-point norm drift. There is no new probe fitting.", "",
             "For each emotion, z = (affinity - mean of all 275 affinities) / population standard deviation (ddof=0). "
             "Percentile = 100 * (average rank - 0.5) / 275. All six channels pass finite/nonzero-variation checks. "
             "Reference membership is fixed; selection and smoothing cannot change a node's score. CSV stores unrounded values. "
             "A negative z-score means below-average affinity, not an opposite emotion. Separate z-normalization does not "
             "make absolute emotion strengths comparable or convert affinity to prevalence/probability.", "",
             "## Surface", "",
             "Each PC plane is centered and divided by one common root-mean-axis-variance scale, preserving its relative PC metric. "
             "A degree-1 thin-plate-spline RBF fits all six z-score channels jointly with predeclared smoothing 0.003 (Detail), "
             "0.03 (Balanced, default), or 0.3 (Gentle). Parameters were not selected to maximize a scientific result. "
             "Coincident projected locations are averaged for the surface only; original nodes stay separate and unchanged. "
             "Reversed views transpose the same grid. A 61 x 61 grid is retained only inside the convex hull AND within "
             "the 90th percentile of role sixth-neighbor distances (including each role itself when estimating that radius). "
             "This masks large unsupported gaps. Missing grid cells are null, not zero; `connectgaps` is false.", "",
             "Surface heights are rounded to six decimals for the bundle; node scores and coordinates are not rounded. "
             "The faint weave follows the fitted surface without random height noise. Thin connectors link node heights to "
             "their fitted values when the gap exceeds 0.03 z. Density masking is not a confidence interval. "
             "The fixed symmetric Z/color range includes all nodes and all retained grid values across every view and smoothing. "
             "No outliers are clipped. X/Y ranges are padded by 4%; Z aspect is a labeled display choice because PC units and SD "
             "are unlike quantities. Missing third-PC information can make nearby points disagree; fitting cannot resolve that information loss.", "",
             "## Sensitivity", "",
             "The displayed method stays frozen. Alternatives below are diagnostics: adjacent row 48 is deliberately boundary-mismatched; "
             "layer mean follows the explorer pooling; story-centering/nuisance removal changes input preprocessing. "
             "These are not validated alternative emotion measurements.", "",
             "| Emotion | Variant | Spearman vs primary | Top-20 overlap |", "|---|---|---:|---:|"]
    for r in sensitivity:
        lines.append(f"| {r['emotion']} | {r['variant']} | {r['spearman_vs_primary']:.3f} | {r['top20_overlap_fraction']:.2f} |")
    lines += ["", "Surface fit errors are descriptive in-sample node/surface discrepancies, not predictive validation. "
              "See `persona_emotion_surface_fit_diagnostics.csv` for all 54 plane/emotion/smoothing combinations.", "",
              "## Reproduction and Verification", "", "From the repository root:", "", "```bash",
              "python3 -B research/outputs/persona_emotion_surface_viewer/run_persona_emotion_surface_viewer.py", "```", "",
              "The runner verifies local canonical startup hashes before scoring and uses CPU tensors only. "
              "Package versions and every input tensor hash are recorded in the manifest. Plotly is embedded with its MIT "
              "license header, as are all viewer data and styles: the HTML makes no network requests. "
              "Browser QA is recorded separately in `persona_emotion_surface_browser_checks.json` with preview images.", "",
              "## Interpretation Limits", "",
              "Observed: this tool calculates relative affinities of saved activation centroids to existing emotion directions. "
              "Inferred: those affinities may help locate emotion-associated representational structure across the displayed PC map. "
              "Unknown: transfer from story probes to role behavior, response-level prevalence, temporal variability, and subjective experience. "
              "A smooth landscape is a visualization of a fitted field, not evidence of an emotion manifold or a solved PC interpretation.", ""]
    return "\n".join(lines)


def render_html(data):
    payload = json.dumps(data, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c")
    html = (HERE / "viewer_template.html").read_text()
    library = get_plotlyjs()
    preview = HERE / "persona_emotion_surface_desktop.png"
    image = "data:image/png;base64," + base64.b64encode(preview.read_bytes()).decode() if preview.exists() else ""
    replacements = {"__PLOTLY_LIBRARY__": library, "__VIEWER_DATA__": payload,
                    "__VIEWER_JS__": (HERE / "viewer.js").read_text(),
                    "__CAMERA_JS__": (HERE / "camera_controls.js").read_text(),
                    "__BOOTSTRAP_JS__": (HERE / "viewer_bootstrap.js").read_text(), "__PREVIEW_IMAGE__": image}
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html, re.search(r"plotly.js v([^\s]+)", library).group(1)


def rebuild_ui(output):
    manifest_path = output / "persona_emotion_surface_manifest.json"
    manifest = read_json(manifest_path)
    data = read_json(output / "persona_emotion_surface_data.json")
    for item in manifest["outputs"]:
        if item["filename"] in {"persona_emotion_surface_data.json", "persona_emotion_scores.csv"}:
            assert sha256(output / item["filename"]) == item["sha256"]
    html, version = render_html(data)
    (output / "persona_emotion_surface_viewer.html").write_text(html)
    manifest["viewer_updated_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["viewer_base_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest["versions"]["plotly_js"] = version
    sources = {item["path"]: item for item in manifest["sources"]}
    for path in [Path(__file__), HERE / "viewer_template.html", HERE / "viewer.js", HERE / "camera_controls.js", HERE / "viewer_bootstrap.js",
                 HERE / "persona_emotion_surface_desktop.png"]:
        sources[str(path.relative_to(ROOT))] = {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
    manifest["sources"] = list(sources.values())
    for item in manifest["outputs"]:
        path = output / item["filename"]
        item.update(sha256=sha256(path), bytes=path.stat().st_size)
    manifest["verification"]["browser_check_status"] = "Original clean-profile checks are historical; startup guard patch needs user-profile confirmation."
    dump_json(manifest_path, manifest)
    print("Rebuilt UI only; the 1,650 scores and surface data are unchanged.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    parser.add_argument("--ui-only", action="store_true", help="Rebuild HTML from checked saved data without rescoring")
    args = parser.parse_args()
    start = time.perf_counter()
    torch.set_num_threads(1)
    startup = verify_startup()
    if args.ui_only:
        rebuild_ui(args.output_dir.resolve())
        return
    mapping = verify_boundary()
    print("Startup and source boundary mapping verified; loading CPU tensors.", flush=True)
    names, coords, emotions, z, rows, sensitivity, sources = make_scores()
    print("275 roles x 6 emotion channels scored. Building supported surfaces.", flush=True)
    views, diagnostics, z_limit = make_meshes(coords, z)
    timestamp = datetime.now(timezone.utc).isoformat()
    manifest = {
        "schema_version": 1, "generated_utc": timestamp, "model_used": None, "author": "Codex",
        "model_provenance_note": "Exact author runtime model identifier unavailable; source activation model is recorded separately.",
        "source_model": "Qwen/Qwen3-32B",
        "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "startup_status": "local canonical hashes verified; session remote verification recorded in implementation report",
        "startup_file_hashes_at_run": startup, "layer_mapping": mapping, "n_roles": 275,
        "n_emotions": 6, "n_score_rows": len(rows), "emotions": [{"label": a, "key": b} for a, b in EMOTIONS],
        "scoring": "raw uncentered layer-matched cosine; per-emotion population z-score over all 275 roles",
        "percentiles": "100 * (average_rank - 0.5) / 275", "grid_size": GRID_SIZE,
        "smoothing": [{"label": a, "value": b} for a, b in SMOOTHING], "fixed_z_range": [-z_limit, z_limit],
        "cpu_only": True, "model_api_calls": 0, "gpu_runs": 0,
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__, "torch": torch.__version__, "plotly_py": plotly.__version__},
        "sources": sources, "elapsed_seconds": None,
        "verification": {"unique_personas": True, "finite_sources": True, "normalization_pass": True,
                          "pc_coordinates_copied_without_refit": True, "surface_diagnostics_are_in_sample": True},
    }
    source_paths = [GEOMETRY, DIRECTIONS, EXTRACTOR, BOUNDARY, Path(__file__), HERE / "viewer_template.html", HERE / "viewer.js", HERE / "camera_controls.js", HERE / "viewer_bootstrap.js",
                    ROOT / "assistant_axis/internals/activations.py", ROOT / "research/visualizations/scripts/build_geometry_viz.py",
                    ROOT / "research/assistant_axis_methodology/role_vector_structure_audit.md",
                    ROOT / "research/outputs/public_source_extraction_equivalence/qwen_hidden_states_semantics_notes.md",
                    EMOTION_DIR / "mean_activation_qwen3_32b_full_layer48.npy",
                    EMOTION_DIR / "pc1_direction_qwen3_32b_full_layer48.npy"]
    if (HERE / "persona_emotion_surface_desktop.png").exists():
        source_paths.append(HERE / "persona_emotion_surface_desktop.png")
    manifest["sources"] += [{"path": str(p.relative_to(ROOT)), "sha256": sha256(p)} for p in source_paths]
    data = {"schema_version": 1, "generated_utc": timestamp, "source_model": "Qwen/Qwen3-32B",
            "roles": [{"name": n, "pcs": c.tolist()} for n, c in zip(names, coords)], "emotions": emotions,
            "views": views, "z_limit": z_limit, "layer_mapping": mapping, "sensitivity": sensitivity}
    html, manifest["versions"]["plotly_js"] = render_html(data)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    dump_json(output / "persona_emotion_surface_data.json", data, compact=True)
    write_csv(output / "persona_emotion_scores.csv", rows)
    write_csv(output / "persona_emotion_score_sensitivity.csv", sensitivity)
    write_csv(output / "persona_emotion_surface_fit_diagnostics.csv", diagnostics)
    (output / "persona_emotion_surface_viewer.html").write_text(html)
    (output / "persona_emotion_surface_methodology.md").write_text(methodology(manifest, sensitivity, diagnostics))
    manifest["elapsed_seconds"] = time.perf_counter() - start
    manifest["outputs"] = [{"filename": p.name, "sha256": sha256(p), "bytes": p.stat().st_size}
                           for p in sorted(output.iterdir()) if p.name in {
                               "persona_emotion_surface_data.json", "persona_emotion_scores.csv",
                               "persona_emotion_score_sensitivity.csv", "persona_emotion_surface_fit_diagnostics.csv",
                               "persona_emotion_surface_viewer.html", "persona_emotion_surface_methodology.md"}]
    dump_json(output / "persona_emotion_surface_manifest.json", manifest)
    print(f"Wrote viewer, 1,650 scores, surface meshes and methodology in {manifest['elapsed_seconds']:.1f}s.")
    print(f"Fixed height range: {-z_limit} to {z_limit}; offline HTML: {len(html.encode()) / 1e6:.2f} MB.")


if __name__ == "__main__":
    main()
