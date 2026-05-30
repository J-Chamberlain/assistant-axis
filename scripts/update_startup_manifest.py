#!/usr/bin/env python3
"""Regenerate the startup freshness manifest for canonical research state files."""

from __future__ import annotations

import hashlib
import re
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


def first_non_empty_heading_or_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("#"):
            return line
    return lines[0] if lines else "not present"


def visible_metadata(text: str) -> dict[str, str]:
    canonical_startup_file = "not present"
    state_role = "not present"
    last_updated = "not present"
    last_commit = "not present"
    for line in text.splitlines():
        stripped = line.strip()
        canonical_match = re.match(r"^Canonical startup file:\s*(.+?)\s*$", stripped, flags=re.IGNORECASE)
        if canonical_match:
            canonical_startup_file = canonical_match.group(1)
        role_match = re.match(r"^State role:\s*(.+?)\s*$", stripped, flags=re.IGNORECASE)
        if role_match:
            state_role = role_match.group(1)
        updated_match = re.match(r"^(?:\*\*)?Last updated:(?:\*\*)?\s*(.+?)\s*$", stripped, flags=re.IGNORECASE)
        if updated_match:
            last_updated = updated_match.group(1)
        commit_match = re.match(r"^(?:\*\*)?Last commit:(?:\*\*)?\s*(.+?)\s*$", stripped, flags=re.IGNORECASE)
        if commit_match:
            last_commit = commit_match.group(1)
    return {
        "canonical_startup_file": canonical_startup_file,
        "state_role": state_role,
        "last_updated": last_updated,
        "last_commit": last_commit,
        "title_or_first_line": first_non_empty_heading_or_line(text),
    }


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
        "4. Compare visible metadata first: title/header, `Last updated`, and `Last commit` when present.",
        "5. Compute SHA256 and byte count only when the environment can do so reliably; these are secondary checks.",
        "6. If visible metadata mismatches, report `STARTUP STALE` and stop unless this manifest explicitly marks the mismatch as expected.",
        "7. Do not substitute search results, cached copies, memory, summaries, or inferred repo state.",
        "",
        "## Text-First Verification Rule",
        "",
        "Claude/GPT startup should compare visible metadata before hash metadata.",
        "Required visible fields are `Canonical startup file`, `State role`, and `Last updated`; `Last commit` is compared only when present in the fetched file.",
        "SHA256 and byte count remain useful for local or tool-enabled verification, but a startup is not fresh if visible file metadata disagrees with this manifest.",
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
        text = data.decode("utf-8")
        metadata = visible_metadata(text)
        latest_commit = git("log", "-n", "1", "--format=%H", "--", path)
        blob_hash = git("hash-object", path)
        lines.extend(
            [
                f"### `{path}`",
                "",
                f"- Path: `{path}`",
                f"- Raw GitHub URL: `{raw_url}`",
                f"- Latest commit touching file: `{latest_commit}`",
                f"- HEAD commit at manifest generation: `{head_commit}`",
                f"- Git blob hash: `{blob_hash}`",
                f"- SHA256 content hash: `{file_sha256(data)}`",
                f"- Byte count: `{len(data)}`",
                "- Visible metadata:",
                f"  - Canonical startup file: `{metadata['canonical_startup_file']}`",
                f"  - State role: `{metadata['state_role']}`",
                f"  - Last updated: `{metadata['last_updated']}`",
                f"  - Last commit: `{metadata['last_commit']}`",
                f"  - Title/header or first non-empty line: `{metadata['title_or_first_line']}`",
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
