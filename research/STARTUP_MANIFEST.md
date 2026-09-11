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

- Generated timestamp UTC: `2026-09-11T23:25:24Z`
- Current branch: `codex/aa3-extended-pca`
- generation base commit: `0fdb584c1bf7e03b0e3fcb35302d7d6f668800c1`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `5cecec530ad149a0ac0f884470e2c2d6898bde1a`
- generation base commit: `0fdb584c1bf7e03b0e3fcb35302d7d6f668800c1`
- Git blob hash: `c692b42125fa28de7c9ba70c92764c7f83058829`
- SHA256 content hash: `f4040abf83e1310bbbe4681b6ef1731a367a78e8833e25a081c50fc9c19c0693`
- Byte count: `178173`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-11`
  - Last commit: `0fdb584 (completed the full-rank Qwen/Llama/Gemma persona PCA dimensionality audit)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-11T23:25:24Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `cac5c0cefd94de83bdf9eac60d39f6517820d94d`
- generation base commit: `0fdb584c1bf7e03b0e3fcb35302d7d6f668800c1`
- Git blob hash: `ee05e72178ab99e9746c5c9b97ec2747aa0597de`
- SHA256 content hash: `2b52e42ce2428b983da14063e941b34f4be1bd829cf3801d4650afe8946b3270`
- Byte count: `31195`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-11T23:25:24Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `0693aaf76e5073c37377024130dbc2d0e80424fd`
- generation base commit: `0fdb584c1bf7e03b0e3fcb35302d7d6f668800c1`
- Git blob hash: `71c4caf5c373108f7c0354529d20de24937b732e`
- SHA256 content hash: `7c79e436d5389d7296e70e8f87522ba5ffa292ce670229c6276dbe2fb9555139`
- Byte count: `46366`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-11T23:25:24Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
