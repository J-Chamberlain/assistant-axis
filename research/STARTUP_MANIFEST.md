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
SHA256 and byte count remain useful for local or tool-enabled verification, but a startup is not fresh if visible file metadata disagrees with this manifest.

## Manifest Metadata

- Generated timestamp UTC: `2026-05-30T14:24:21Z`
- Current branch: `master`
- HEAD commit at generation: `91c45afd0c3a8ee224d7f15ec758eeedd4983be3`
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `a927363601b41302d4baa6507a5a9486ed5c0c40`
- HEAD commit at manifest generation: `91c45afd0c3a8ee224d7f15ec758eeedd4983be3`
- Git blob hash: `cb1aa6f5256639aed766cf94337c804fe96e5738`
- SHA256 content hash: `c1d4a13080dc74eccc6619bcf61348c2cc9bef081e5bf40a4ee1a156c3ffb4be`
- Byte count: `74314`
- Visible metadata:
  - Last updated: `2026-05-30`
  - Last commit: `3422356`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-05-30T14:24:21Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `14dd9933545599a4d1e884c1d8007a42d590a2ed`
- HEAD commit at manifest generation: `91c45afd0c3a8ee224d7f15ec758eeedd4983be3`
- Git blob hash: `d3d53146170ea13c0bec37a7ca5be46872f83aea`
- SHA256 content hash: `b4fe118499a51f971ca1a4567c8a7a1b0b1eeeeaa9b0a43a409b6fcf4f5a3968`
- Byte count: `6653`
- Visible metadata:
  - Last updated: `not present`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-05-30T14:24:21Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `14dd9933545599a4d1e884c1d8007a42d590a2ed`
- HEAD commit at manifest generation: `91c45afd0c3a8ee224d7f15ec758eeedd4983be3`
- Git blob hash: `1af81f63d2bfee02014067feeab04996b9f79f24`
- SHA256 content hash: `c6b8cda230c8e218f594ec6b83e491de6aab9dd3b387e66f7457169c9f66ea45`
- Byte count: `12386`
- Visible metadata:
  - Last updated: `not present`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-05-30T14:24:21Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
