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

- Generated timestamp UTC: `2026-09-17T08:43:37Z`
- Current branch: `codex/aa16-sapa-hifwb-trait-pc-crosswalk`
- generation base commit: `9a8e3c6fae4f320a4909d09dff1b88c6e84ae20b`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `e994f62d36364de74362b36a3277049d8e07d58f`
- generation base commit: `9a8e3c6fae4f320a4909d09dff1b88c6e84ae20b`
- Git blob hash: `161506de231d33c6e96ba94644ea0da321fe898a`
- SHA256 content hash: `2875342c0f2838f365e964aff47d610bb64a86d364120e85c0b221b4637a79e5`
- Byte count: `190163`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-16`
  - Last commit: `663853e (AA-9 base before the AA-14 branch update)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-17T08:43:37Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `e994f62d36364de74362b36a3277049d8e07d58f`
- generation base commit: `9a8e3c6fae4f320a4909d09dff1b88c6e84ae20b`
- Git blob hash: `d65b2ae6cf96a12ed1a5e5abfa11223618dd6da9`
- SHA256 content hash: `5b1949597ddd191b28917f5817c9c6d0a869a18e6a88d0afde97a2d1de1efa7f`
- Byte count: `41409`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-17T08:43:37Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `ffe188ac1373e96bb44bdc9c99125acb424bbe4f`
- generation base commit: `9a8e3c6fae4f320a4909d09dff1b88c6e84ae20b`
- Git blob hash: `5a81d23f1ef8c701d0178f1fc6c4e0be2f7346ef`
- SHA256 content hash: `8790565d59a65a6e2244508e596c56cf861176339b8d68b51edc812348f6c9fe`
- Byte count: `52323`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-16`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-17T08:43:37Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
