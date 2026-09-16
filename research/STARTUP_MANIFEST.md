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

- Generated timestamp UTC: `2026-09-16T15:28:55Z`
- Current branch: `codex/aa15-hifwb-trait-pc-projection`
- generation base commit: `4488ff8a828b9f690d64ab52814721c2bd7c47de`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `4488ff8a828b9f690d64ab52814721c2bd7c47de`
- generation base commit: `4488ff8a828b9f690d64ab52814721c2bd7c47de`
- Git blob hash: `ae994d25e53198c503242cb984626508133394c1`
- SHA256 content hash: `cf770881290e2da030ae515f6232d58b245331090d8cd2d4f20dd5f82d2b51ad`
- Byte count: `188828`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-16`
  - Last commit: `663853e (AA-9 base before the AA-14 branch update)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-16T15:28:55Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `4488ff8a828b9f690d64ab52814721c2bd7c47de`
- generation base commit: `4488ff8a828b9f690d64ab52814721c2bd7c47de`
- Git blob hash: `a97cde8bc41a2c018ced8ea30e547339c680561c`
- SHA256 content hash: `efab2ffd8e7e507d4e0ba17446dec1d01db625af9ef17716b4643e2fbf95b21e`
- Byte count: `40082`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-16`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-16T15:28:55Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `4488ff8a828b9f690d64ab52814721c2bd7c47de`
- generation base commit: `4488ff8a828b9f690d64ab52814721c2bd7c47de`
- Git blob hash: `5a81d23f1ef8c701d0178f1fc6c4e0be2f7346ef`
- SHA256 content hash: `8790565d59a65a6e2244508e596c56cf861176339b8d68b51edc812348f6c9fe`
- Byte count: `52323`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-16`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-16T15:28:55Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
