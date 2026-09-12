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

- Generated timestamp UTC: `2026-09-12T12:19:54Z`
- Current branch: `codex/aa1-qwen-human-construct-bridge`
- generation base commit: `08bde9ad5db8417c764bcb356938ab7cf7ff97f6`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `8a512401751799fac95324ce638d170a02d45e45`
- generation base commit: `08bde9ad5db8417c764bcb356938ab7cf7ff97f6`
- Git blob hash: `97b4084b25207565ac54fb05729d40b04c1bad7b`
- SHA256 content hash: `f808a7938eb3c28a3d410bbc628877abf725d7b261643220af6d8e65bb928c32`
- Byte count: `184543`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-12`
  - Last commit: `08bde9a (Qwen-first human-construct bridge report before canonical state maintenance)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-12T12:19:54Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `d918ca3a9c73d05a8f5bb21c77af20f516a90587`
- generation base commit: `08bde9ad5db8417c764bcb356938ab7cf7ff97f6`
- Git blob hash: `1f03db99b445540d82982aa5a10225fbfb0e8897`
- SHA256 content hash: `34b9b4141c80326e4b36fc1fb3def9e07f7d454fd59b750820548708971d1374`
- Byte count: `39351`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-12`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-12T12:19:54Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `c1f241bd94a0ac0fd6e5a21a08392eda553e25bf`
- generation base commit: `08bde9ad5db8417c764bcb356938ab7cf7ff97f6`
- Git blob hash: `4b4fe49c1a69e57e2a6e70edee5b7d852c907893`
- SHA256 content hash: `6ad43720b0d802411f686dcfbe5146ef5f89c301b5697da2c63e52e2ecd5b5cc`
- Byte count: `48203`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-12T12:19:54Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
