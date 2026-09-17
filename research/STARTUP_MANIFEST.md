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

- Generated timestamp UTC: `2026-09-17T11:20:35Z`
- Current branch: `codex/aa20-consensus-axes-hifwb`
- generation base commit: `f2f16a5224da2277ab8bc946e70b27deaa5108de`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `f2f16a5224da2277ab8bc946e70b27deaa5108de`
- generation base commit: `f2f16a5224da2277ab8bc946e70b27deaa5108de`
- Git blob hash: `dafe074cad5a9eae41740fa4a13372f495f93fa7`
- SHA256 content hash: `b23ee8ccbce79c8e72ba3fce2951c3a3ff85aa7f08e50797389a5dd115ce662e`
- Byte count: `197614`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-17`
  - Last commit: `f2f16a5 (AA-19 analytical base before AA-20)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-17T11:20:35Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `f2f16a5224da2277ab8bc946e70b27deaa5108de`
- generation base commit: `f2f16a5224da2277ab8bc946e70b27deaa5108de`
- Git blob hash: `84b6d89cb7cd09d549ce946f07f7435f8c950b34`
- SHA256 content hash: `58c82c167252fd3ca8d192c942215f423df8c770ee1aa1f53545dba801d02d0d`
- Byte count: `45192`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-17T11:20:35Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `f2f16a5224da2277ab8bc946e70b27deaa5108de`
- generation base commit: `f2f16a5224da2277ab8bc946e70b27deaa5108de`
- Git blob hash: `fdb51977147f3c297ffa880a87e68c09867c1ce7`
- SHA256 content hash: `89b41e4f9c3c08399656bde3e0b12188fd531a2f7d6492346bc2e9bc1cad8030`
- Byte count: `58656`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-17T11:20:35Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
