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

- Generated timestamp UTC: `2026-05-31T14:36:03Z`
- Current branch: `master`
- generation base commit: `be8cc15e1f81365d2ff2ad8c2e947d041f7348d4`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `be8cc15e1f81365d2ff2ad8c2e947d041f7348d4`
- generation base commit: `be8cc15e1f81365d2ff2ad8c2e947d041f7348d4`
- Git blob hash: `e50f083d102199c502e10ac6286e4d667d5b4e31`
- SHA256 content hash: `1eed010715f54150a861cce4ad59183a49dc380b999322501d53184e98d2de9e`
- Byte count: `106890`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-05-31`
  - Last commit: `be8cc15`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-05-31T14:36:03Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `7a0fd21098f74de403abd210dafaf4e8819d4164`
- generation base commit: `be8cc15e1f81365d2ff2ad8c2e947d041f7348d4`
- Git blob hash: `97fc581c9ac4340cdf26531e5e74472cf86ca078`
- SHA256 content hash: `babb302215a2e9137cdf44e138be5e8739279e25062b8141375de377abfd51c5`
- Byte count: `6763`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-05-30`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-05-31T14:36:03Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `be8cc15e1f81365d2ff2ad8c2e947d041f7348d4`
- generation base commit: `be8cc15e1f81365d2ff2ad8c2e947d041f7348d4`
- Git blob hash: `9be885563631d2d478b08ed234f570f837d18219`
- SHA256 content hash: `45a1255c02eed45d3f9a37151eb9cdc640ab997bab73c95e7892859d5c2d03eb`
- Byte count: `31908`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-05-31`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-05-31T14:36:03Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
