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

- Generated timestamp UTC: `2026-09-11T23:39:45Z`
- Current branch: `codex/aa5-nlsy97-occupation-stability`
- generation base commit: `13fb08f1d75444820d0b374fef2e3e0292a4d1f1`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `5cecec530ad149a0ac0f884470e2c2d6898bde1a`
- generation base commit: `13fb08f1d75444820d0b374fef2e3e0292a4d1f1`
- Git blob hash: `3e69cba3b4172b8d6a9d0aedf117ce0927222e71`
- SHA256 content hash: `bb27e9fa1ebdaaa1505ae8b152632b4d0053a25b78ef99b8bca90c823da1a998`
- Byte count: `178564`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-11`
  - Last commit: `13fb08f (froze AA-5 NLSY97 occupation-centroid methods and tiers before outcome inspection; final analysis commit pending)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-11T23:39:45Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `cac5c0cefd94de83bdf9eac60d39f6517820d94d`
- generation base commit: `13fb08f1d75444820d0b374fef2e3e0292a4d1f1`
- Git blob hash: `072ee503d9ba6808c287668826ab36ce18fcfda2`
- SHA256 content hash: `e5115f4b9f2f6b6f47a26095784c2e55b3b1de605fc42190f245102c9c79e143`
- Byte count: `30875`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-11T23:39:45Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `0693aaf76e5073c37377024130dbc2d0e80424fd`
- generation base commit: `13fb08f1d75444820d0b374fef2e3e0292a4d1f1`
- Git blob hash: `4c50a36065107289371fdf9556ff4e01529b1443`
- SHA256 content hash: `e821e687c9d34069f7de9fb13a3ea6821614354ec8b980cfc2add51e65ec8d87`
- Byte count: `45298`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-11T23:39:45Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
