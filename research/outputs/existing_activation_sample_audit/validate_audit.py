#!/usr/bin/env python3
"""Validate this inventory and its evidence without running models or extraction."""
import ast
import collections
import csv
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

rows = list(csv.DictReader((OUT / "inventory.csv").open()))
manifest = json.loads((OUT / "source_manifest.json").read_text())
assert len(rows) == 3167, len(rows)
key_fields = ("provenance_group", "model_id", "entity_type", "entity_name",
              "run_id", "classification", "source")
keys = [tuple(r[k] for k in key_fields) for r in rows]
assert len(keys) == len(set(keys)), "Duplicate artifact inventory key"
roles = {p.stem for p in (ROOT / "data/roles/instructions").glob("*.json")} - {"default"}
traits = set(json.loads((ROOT / "data/traits/trait_list.json").read_text()))
assert len(roles) == 275 and len(traits) == 240
original = [r for r in rows if r["provenance_group"] == "original-study release"]
models = {r["model_id"] for r in original}
assert len(models) == 3 and len(original) == 3090
for model in models:
    for kind, names in (("persona", roles), ("trait", traits)):
        for classification in ("Aggregate vector only", "Missing or inaccessible"):
            subset = [r for r in original if r["model_id"] == model
                      and r["entity_type"] == kind and r["classification"] == classification]
            assert len(subset) == len(names)
            assert {r["entity_name"] for r in subset} == names
            if classification == "Aggregate vector only":
                assert all(r["sample_axis"] == "NONE: rows are layers" for r in subset)
release = next(r for r in manifest["public_releases"]
               if r["repo"] == "lu-christina/assistant-axis-vectors")
files = {f["rfilename"]: f for f in release["files"]}
for entry in manifest["aggregate_files"]:
    path = ROOT / entry["path"]
    assert path.is_file()
    assert path.stat().st_size == entry["bytes"]
    assert sha(path) == entry["sha256"]
    remote = files[entry["path"].removeprefix("downloads/hf_vectors/")]
    assert remote["lfs"]["sha256"] == entry["sha256"]
for entry in manifest["local_sources"]:
    path = ROOT / entry["path"]
    assert path.is_file(), path
    assert path.stat().st_size == entry["bytes"], path
    assert sha(path) == entry["sha256"], path
for row in rows:
    path = ROOT / row["source"]
    if not row["source"].startswith("https:") and path.is_file():
        assert int(row["bytes"]) == path.stat().st_size, row["source"]
remote = json.loads((OUT / "remote_metadata.json").read_text())
assert len(remote) == 23
assert len({r["role"] for r in remote if r["role"] != "default"}) == 20
assert sum(r["role"] == "default" for r in remote) == 3
for r in remote:
    assert r["range_status"] == 206 and r["header_bytes"] == 262144
    assert r["sample_count"] == r["unique_keys"] == 1200
    assert r["shapes"] == {"[64, 5120]": 1200}
    assert r["prompt_indices"] == list(range(5))
    assert r["question_indices"] == list(range(240))
    assert r["scores_without_activations"] == 0
for entry in json.loads((OUT / "unrelated_work_snapshot.json").read_text()).items():
    name, expected = entry
    assert sha(ROOT / name) == expected["sha256"], "Unrelated file changed: " + name
for script in OUT.glob("*.py"):
    ast.parse(script.read_text(), filename=str(script))
runs = json.loads((OUT / "run_metadata.json").read_text())
raw = [r for r in runs if "activation_dir" in r]
assert len(raw) == 3 and sum(r["n"] for r in raw) == 1392
for r in raw:
    assert not r["missing_shards"] and r["unique_ids"] == r["n"]
    assert len(list((ROOT / r["activation_dir"]).glob("*.pt"))) == r["n"]
print(json.dumps({
    "status": "PASS", "inventory_rows": len(rows), "duplicate_keys": 0,
    "original_aggregate_entries": 1545, "explicit_original_missing_sample_entries": 1545,
    "local_release_hashes_verified": 1545,
    "local_source_hashes_verified": len(manifest["local_sources"]),
    "third_party_personas": 20, "third_party_default_runs": 3,
    "unrelated_work_hashes_unchanged": True,
    "limitations": "Remote tensor payloads and complete response joins were deliberately not downloaded or validated."
}, indent=2))
