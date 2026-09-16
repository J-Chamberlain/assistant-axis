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

- Generated timestamp UTC: `2026-09-16T15:54:22Z`
- Current branch: `codex/aa15-hifwb-trait-pc-projection`
- generation base commit: `7afe97af9e0ea590c75009c17d4fe4a0191d9a01`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `7d810dd45e78b03ed177f749331a738d464f60b6`
- generation base commit: `7afe97af9e0ea590c75009c17d4fe4a0191d9a01`
- Git blob hash: `a29b96b15fe1aac509eb0652a0ca06b27cba202a`
- SHA256 content hash: `3bc8dec0ff1a6d2f7d7ef4332d393638d1c39292b7e0cf70d0e7adc15474ea6f`
- Byte count: `189464`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-16`
  - Last commit: `663853e (AA-9 base before the AA-14 branch update)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-16T15:54:22Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `7d810dd45e78b03ed177f749331a738d464f60b6`
- generation base commit: `7afe97af9e0ea590c75009c17d4fe4a0191d9a01`
- Git blob hash: `f7194f7f78db1ef3db068b3910c5a7a9675c23bc`
- SHA256 content hash: `7a23a9c84d99c211ac13aeec1112cb769dddf4b140d1fda243aad14b4d3ff0e7`
- Byte count: `40734`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-16`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-16T15:54:22Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `ffe188ac1373e96bb44bdc9c99125acb424bbe4f`
- generation base commit: `7afe97af9e0ea590c75009c17d4fe4a0191d9a01`
- Git blob hash: `5a81d23f1ef8c701d0178f1fc6c4e0be2f7346ef`
- SHA256 content hash: `8790565d59a65a6e2244508e596c56cf861176339b8d68b51edc812348f6c9fe`
- Byte count: `52323`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-16`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-16T15:54:22Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
