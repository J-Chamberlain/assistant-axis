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

- Generated timestamp UTC: `2026-05-30T14:30:30Z`
- Current branch: `master`
- HEAD commit at generation: `29f968a4a6cd09543022d2805d787039ea4a50a1`
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `a927363601b41302d4baa6507a5a9486ed5c0c40`
- HEAD commit at manifest generation: `29f968a4a6cd09543022d2805d787039ea4a50a1`
- Git blob hash: `5bbcb43f6db5240e6d9e19a6c22547e4649e0827`
- SHA256 content hash: `1b79cb1a506152c20d66c71443f5b98913df12f05f08d77360833db337924985`
- Byte count: `74458`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-05-30`
  - Last commit: `3422356`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-05-30T14:30:30Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `14dd9933545599a4d1e884c1d8007a42d590a2ed`
- HEAD commit at manifest generation: `29f968a4a6cd09543022d2805d787039ea4a50a1`
- Git blob hash: `97fc581c9ac4340cdf26531e5e74472cf86ca078`
- SHA256 content hash: `babb302215a2e9137cdf44e138be5e8739279e25062b8141375de377abfd51c5`
- Byte count: `6763`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-05-30`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-05-30T14:30:30Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `14dd9933545599a4d1e884c1d8007a42d590a2ed`
- HEAD commit at manifest generation: `29f968a4a6cd09543022d2805d787039ea4a50a1`
- Git blob hash: `a6facb048d6cbca546f6a4ac85b0ae76e03cac52`
- SHA256 content hash: `dcdfe66d81059df4df73f09c6acb1684c6a8ac0837740fa3cfa8ef8708efcec1`
- Byte count: `12475`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-05-30`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-05-30T14:30:30Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
