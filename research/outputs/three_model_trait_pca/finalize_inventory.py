#!/usr/bin/env python3
"""Inventory AA-14 derived artifacts and extend canonical file navigation."""
import csv
import hashlib
import io
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BRANCH = "codex/three-model-trait-pca-persona-viewer"
BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/" + BRANCH + "/"
STAMP = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

files = sorted(p for p in HERE.iterdir() if p.is_file() and p.name != "artifact_inventory.csv")
inventory = []
for path in files:
    rel = path.relative_to(ROOT).as_posix()
    data = path.read_bytes()
    inventory.append({"path": rel, "status": "active", "size_bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest(), "raw_github_url": BASE + rel})
inventory_path = HERE / "artifact_inventory.csv"
with inventory_path.open("w", newline="") as stream:
    writer = csv.DictWriter(stream, inventory[0].keys(), lineterminator="\n")
    writer.writeheader(); writer.writerows(inventory)

index = ROOT / "research/REPO_FILE_INDEX.csv"
baseline = subprocess.check_output(["git", "show", "HEAD:research/REPO_FILE_INDEX.csv"], cwd=ROOT)
reader = csv.DictReader(io.StringIO(baseline.decode()))
fields = reader.fieldnames
rows = []
for path in sorted(HERE.iterdir()):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    category = "visualizations" if path.suffix in (".html", ".js") or path.name == "build_viewer.py" else "trait analyses"
    rows.append({"path": rel, "category": category, "status": "active",
                 "description": "AA-14 three-model trait PCA, projected-persona viewer, or verification artifact",
                 "raw_github_url": BASE + rel, "size_bytes": path.stat().st_size,
                 "extension": path.suffix, "updated_utc": STAMP})
buffer = io.StringIO()
writer = csv.DictWriter(buffer, fields, lineterminator="\n")
writer.writerows(rows)
index.write_bytes(baseline + buffer.getvalue().encode())
print(f"Indexed {len(inventory)+1} AA-14 files at {STAMP}")
