# Startup Manifest

This manifest is the freshness contract for cross-thread assistant-axis startup.
Fetch this file first, then fetch the canonical startup files by exact raw URL and verify content before claiming startup success.

## Startup Verification Protocol

1. Fetch `research/STARTUP_MANIFEST.md` first.
2. Fetch each canonical startup file directly from the exact raw GitHub URL listed below.
3. Use cache-busting query strings if the environment allows, for example `?t=<timestamp>`.
4. Compare visible metadata first: title/header, `Last updated`, and `Last commit` when present.
5. Compute SHA256 and byte count only when the environment can do so reliably; these are secondary checks.
6. If visible metadata mismatches, report `STARTUP STALE` and stop unless this manifest explicitly marks the mismatch as expected.
7. Do not substitute search results, cached copies, memory, summaries, or inferred repo state.

## Text-First Verification Rule

Claude/GPT startup should compare visible metadata before hash metadata.
Required visible fields are `Canonical startup file`, `State role`, and `Last updated`; `Last commit` is compared only when present in the fetched file.
SHA256 and byte count remain useful for local or tool-enabled verification, but a startup is not fresh if visible file metadata disagrees with this manifest.

## Manifest Metadata

- Generated timestamp UTC: `2026-06-15T03:23:59Z`
- Current branch: `master`
- generation base commit: `cd8552a02526f40d38e4a837fa0ef69e7045670d`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `0f1fdc4e3e3279eea6cf9710009647c8f61c4575`
- generation base commit: `cd8552a02526f40d38e4a837fa0ef69e7045670d`
- Git blob hash: `a8e689a29ba7e80fb2042238bc41abf36c197091`
- SHA256 content hash: `294086ae9a0a40de0d6f3e5aafcd573522b53e82a1ea766f124e452f6950e4fc`
- Byte count: `150600`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-06-14`
  - Last commit: `cd8552a`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-06-15T03:23:59Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- generation base commit: `cd8552a02526f40d38e4a837fa0ef69e7045670d`
- Git blob hash: `6b4c5aad3871a460fbb550671bb08eb75fba09a6`
- SHA256 content hash: `f404fae9b64ed584842c255d5413f7b15dc81820edf1268f5da890f69d617398`
- Byte count: `16751`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-06-14`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-06-15T03:23:59Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- generation base commit: `cd8552a02526f40d38e4a837fa0ef69e7045670d`
- Git blob hash: `ffeb986ba8dbc77bfe56627648944231be066308`
- SHA256 content hash: `e6f8db845de30a4f2e9a1a56e5bc2d9b12334c9fbc5ddcf1d733b49fcaedfc80`
- Byte count: `41219`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-10`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-06-15T03:23:59Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
