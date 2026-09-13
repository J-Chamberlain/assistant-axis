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

- Generated timestamp UTC: `2026-09-13T19:15:40Z`
- Current branch: `codex/aa12-correspondence-visualization-packet`
- generation base commit: `07a6f166e539c93c867c5c204453b0cd32d6eddd`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `07a6f166e539c93c867c5c204453b0cd32d6eddd`
- generation base commit: `07a6f166e539c93c867c5c204453b0cd32d6eddd`
- Git blob hash: `d39fd321f20d6334af5bc5f0f24996ab072f8c57`
- SHA256 content hash: `43d174d1301ce2bff3cc845cd40d635ded0dafbc87e0336aa511958eef5b5f55`
- Byte count: `197849`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-13`
  - Last commit: `ba4c138 (inventoried the AA-12 aggregate correspondence visualization packet before canonical maintenance)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-13T19:15:40Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `07a6f166e539c93c867c5c204453b0cd32d6eddd`
- generation base commit: `07a6f166e539c93c867c5c204453b0cd32d6eddd`
- Git blob hash: `396752f0c434fd0e50d5f3046650079c450d790a`
- SHA256 content hash: `9f2cba506bdabb8a8c87d2fd415f6e9ec46c03dfff69e60dde7a14bf11bffd40`
- Byte count: `45105`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-13`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-13T19:15:40Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `6fd89fb95ff794e82d505f0913fcbad118910e87`
- generation base commit: `07a6f166e539c93c867c5c204453b0cd32d6eddd`
- Git blob hash: `f32de2e3631655d524a959698c69b5d6e7c65fa6`
- SHA256 content hash: `b4dd75a7feff25dbb9bb4b034ac13de3e89e978cf1b3f611450ddaefc5aa4d6a`
- Byte count: `53260`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-13`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-13T19:15:40Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
