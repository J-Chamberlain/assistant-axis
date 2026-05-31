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

- Generated timestamp UTC: `2026-05-31T13:15:59Z`
- Current branch: `master`
- generation base commit: `80a6e31645ed6530e50d34c9673a5ec10942df7a`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `80a6e31645ed6530e50d34c9673a5ec10942df7a`
- generation base commit: `80a6e31645ed6530e50d34c9673a5ec10942df7a`
- Git blob hash: `1c766ca50785d57a1528ab2216d8a36024d38716`
- SHA256 content hash: `409ddf541a593ddf5d4d3b512637c7aa05da9cd890584db68b271179e092bd6a`
- Byte count: `102867`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-05-31`
  - Last commit: `80a6e31`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-05-31T13:15:59Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `7a0fd21098f74de403abd210dafaf4e8819d4164`
- generation base commit: `80a6e31645ed6530e50d34c9673a5ec10942df7a`
- Git blob hash: `97fc581c9ac4340cdf26531e5e74472cf86ca078`
- SHA256 content hash: `babb302215a2e9137cdf44e138be5e8739279e25062b8141375de377abfd51c5`
- Byte count: `6763`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-05-30`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-05-31T13:15:59Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `80a6e31645ed6530e50d34c9673a5ec10942df7a`
- generation base commit: `80a6e31645ed6530e50d34c9673a5ec10942df7a`
- Git blob hash: `ab81917e427f8391247b4d8bf8bbf8f16cebee01`
- SHA256 content hash: `71966d03ebf145c9b49f33c1b404eafb0c9bcfcbf294bcd45e5251e0b6f17a86`
- Byte count: `31420`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-05-31`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-05-31T13:15:59Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
