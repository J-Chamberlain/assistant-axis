#!/usr/bin/env python3
"""Inventory committed-safe AA-15 artifacts and extend the canonical file index."""
import csv
import hashlib
import io
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa15-hifwb-trait-pc-projection/"
STAMP = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
files = sorted(p for p in HERE.iterdir() if p.is_file() and p.name != "artifact_inventory.csv")
inventory = []
for path in files:
    rel = path.relative_to(ROOT).as_posix()
    data = path.read_bytes()
    inventory.append({"path": rel, "status": "active", "size_bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest(), "raw_github_url": BASE + rel})
with (HERE / "artifact_inventory.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, inventory[0].keys(), lineterminator="\n")
    writer.writeheader()
    writer.writerows(inventory)

index = ROOT / "research/REPO_FILE_INDEX.csv"
baseline = subprocess.check_output(["git", "show", "HEAD:research/REPO_FILE_INDEX.csv"], cwd=ROOT)
reader = csv.DictReader(io.StringIO(baseline.decode()))
fields = reader.fieldnames
known = {row["path"] for row in reader}
rows = []
for path in sorted(HERE.iterdir()):
    if not path.is_file():
        continue
    rel = path.relative_to(ROOT).as_posix()
    if rel in known:
        continue
    rows.append({"path": rel, "category": "trait analyses", "status": "active",
                 "description": "AA-15 provenance, frozen HiFWB prompt protocol, or derived analysis artifact",
                 "raw_github_url": BASE + rel, "size_bytes": path.stat().st_size,
                 "extension": path.suffix, "updated_utc": STAMP})
buffer = io.StringIO()
writer = csv.DictWriter(buffer, fields, lineterminator="\n")
writer.writerows(rows)
index.write_bytes(baseline + buffer.getvalue().encode())
print(f"Indexed {len(files)+1} AA-15 artifacts ({len(rows)} new canonical file-index rows).")
