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

- Generated timestamp UTC: `2026-09-12T00:35:31Z`
- Current branch: `codex/aa1-aa5-integration`
- generation base commit: `8a512401751799fac95324ce638d170a02d45e45`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `8a512401751799fac95324ce638d170a02d45e45`
- generation base commit: `8a512401751799fac95324ce638d170a02d45e45`
- Git blob hash: `b757686d0038668c64b8cd5bdd34ae9695bace2c`
- SHA256 content hash: `7d1cd156a0566279fae76d11ba0a845972ce79f98dce38a4da0bb9d7b3ba9db2`
- Byte count: `182509`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-11`
  - Last commit: `d918ca3 (integrated AA-1 through AA-5 claims, state, provenance, navigation, Paper 1.5, interpretation, runtime, and sticky-note layers)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-12T00:35:31Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `d918ca3a9c73d05a8f5bb21c77af20f516a90587`
- generation base commit: `8a512401751799fac95324ce638d170a02d45e45`
- Git blob hash: `a05fc2fecaabfc4f9cfbc49c4f010a1d4d912cf6`
- SHA256 content hash: `e6ee905f89c538ffbe4f67fe8ac39615c01d687b2f51efb47b439ba1824a4bb0`
- Byte count: `38072`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-12T00:35:31Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `c1f241bd94a0ac0fd6e5a21a08392eda553e25bf`
- generation base commit: `8a512401751799fac95324ce638d170a02d45e45`
- Git blob hash: `4b4fe49c1a69e57e2a6e70edee5b7d852c907893`
- SHA256 content hash: `6ad43720b0d802411f686dcfbe5146ef5f89c301b5697da2c63e52e2ecd5b5cc`
- Byte count: `48203`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-12T00:35:31Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
