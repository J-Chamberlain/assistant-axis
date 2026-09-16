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

- Generated timestamp UTC: `2026-09-16T11:59:55Z`
- Current branch: `codex/aa13-broad-sapa-pca-wellbeing`
- generation base commit: `9d9408d65741609a2d2b6492de7b177f0c6b592b`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `9752edec6d2682b2768c64e86d4424a7e2ebf4d4`
- generation base commit: `9d9408d65741609a2d2b6492de7b177f0c6b592b`
- Git blob hash: `93aa64634624d547014eb487931cb9d55b2381df`
- SHA256 content hash: `afa026bedc6667025318ece8da95e92bd041346665df436521719ef982e029ac`
- Byte count: `186347`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-12`
  - Last commit: `b9b6008 (reconciled AA-7's negative compact-selection result, model-only aligned recurrence, exact controls, and canonical continuity)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-16T11:59:55Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `9752edec6d2682b2768c64e86d4424a7e2ebf4d4`
- generation base commit: `9d9408d65741609a2d2b6492de7b177f0c6b592b`
- Git blob hash: `ca2c7bca5b6e6ae245bbb8f5ab5ebcb5d634f5a7`
- SHA256 content hash: `b2167cd1742b3c0f071851fe7b10df4a25e3493dde145e6aff3ab5a30cbb5ac7`
- Byte count: `39336`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-12`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-16T11:59:55Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `b9b6008ac4cff37bfef98bd2103a9cb9edf3a3a6`
- generation base commit: `9d9408d65741609a2d2b6492de7b177f0c6b592b`
- Git blob hash: `96a1b2c77469a7cb5ca1cb67cb053850f5304029`
- SHA256 content hash: `7f543f3a5a5f8fa308c9ddfbf2efa6068ea7a7e516c7a133a08e14b63b1c69d0`
- Byte count: `50422`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-12`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-16T11:59:55Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
