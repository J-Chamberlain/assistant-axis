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

- Generated timestamp UTC: `2026-06-13T19:14:01Z`
- Current branch: `master`
- generation base commit: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- generation base commit: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- Git blob hash: `465c005e6801c3f6fb135bf614798cf32172ad08`
- SHA256 content hash: `f193d051813ce4b57bc95db10764eab1698fd4b1017e28a0d5f723914d337c6b`
- Byte count: `149544`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-06-13`
  - Last commit: `8e2cac8`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-06-13T19:14:01Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- generation base commit: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- Git blob hash: `b28f76a00d7bedca0cb9966a9ba943616e6c9bac`
- SHA256 content hash: `2b35946b39eabe00402c0ccc71b75ee133e46cf06002bd4a32a517b4f1e1d004`
- Byte count: `16218`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-06-13`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-06-13T19:14:01Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- generation base commit: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- Git blob hash: `ffeb986ba8dbc77bfe56627648944231be066308`
- SHA256 content hash: `e6f8db845de30a4f2e9a1a56e5bc2d9b12334c9fbc5ddcf1d733b49fcaedfc80`
- Byte count: `41219`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-10`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-06-13T19:14:01Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
