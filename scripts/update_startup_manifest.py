#!/usr/bin/env python3
"""Regenerate the startup freshness manifest for canonical research state files."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "research" / "STARTUP_MANIFEST.md"

CANONICAL_FILES = [
    (
        "research/RESEARCH_STATE.md",
        "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md",
    ),
    (
        "research/THREAD_START.md",
        "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md",
    ),
    (
        "research/CLAIMS_REGISTER.md",
        "https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md",
    ),
]


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def file_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_manifest() -> str:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    branch = git("branch", "--show-current")
    head_commit = git("rev-parse", "HEAD")

    missing = [path for path, _ in CANONICAL_FILES if not (REPO_ROOT / path).is_file()]
    if missing:
        for path in missing:
            print(f"Missing canonical startup file: {path}", file=sys.stderr)
        raise SystemExit(1)

    lines = [
        "# Startup Manifest",
        "",
        "This manifest is the freshness contract for cross-thread assistant-axis startup.",
        "Fetch this file first, then fetch the canonical startup files by exact raw URL and verify content before claiming startup success.",
        "",
        "## Startup Verification Protocol",
        "",
        "1. Fetch `research/STARTUP_MANIFEST.md` first.",
        "2. Fetch each canonical startup file directly from the exact raw GitHub URL listed below.",
        "3. Use cache-busting query strings if the environment allows, for example `?t=<timestamp>`.",
        "4. Compute SHA256 and byte count for each fetched file.",
        "5. Compare observed SHA256, byte count, and visible internal metadata against this manifest.",
        "6. If any mismatch occurs, report `STARTUP STALE` and stop.",
        "7. Do not substitute search results, cached copies, memory, summaries, or inferred repo state.",
        "",
        "## Manifest Metadata",
        "",
        f"- Generated timestamp UTC: `{generated_at}`",
        f"- Current branch: `{branch}`",
        f"- HEAD commit at generation: `{head_commit}`",
        "- Manifest generator: `scripts/update_startup_manifest.py`",
        "",
        "## Canonical Startup Files",
        "",
    ]

    for path, raw_url in CANONICAL_FILES:
        data = (REPO_ROOT / path).read_bytes()
        latest_commit = git("log", "-n", "1", "--format=%H", "--", path)
        blob_hash = git("hash-object", path)
        lines.extend(
            [
                f"### `{path}`",
                "",
                f"- Path: `{path}`",
                f"- Raw GitHub URL: `{raw_url}`",
                f"- Latest commit touching file: `{latest_commit}`",
                f"- Git blob hash: `{blob_hash}`",
                f"- SHA256 content hash: `{file_sha256(data)}`",
                f"- Byte count: `{len(data)}`",
                f"- Generated timestamp UTC: `{generated_at}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Maintenance Rule",
            "",
            "Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:",
            "",
            "```bash",
            "python3 scripts/update_startup_manifest.py",
            "```",
            "",
            "Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    OUTPUT_PATH.write_text(build_manifest(), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
