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

- Generated timestamp UTC: `2026-09-11T22:41:13Z`
- Current branch: `codex/aa1-human-feasibility-integration`
- generation base commit: `4440ba0bda44517b63c8b4f05505b98651863ba9`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `9dd6fd39246fd8847d51d5ae61fee2604942caa7`
- generation base commit: `4440ba0bda44517b63c8b4f05505b98651863ba9`
- Git blob hash: `1afe26ff83abcbc2eb0f19c0e68fed078a73b1e9`
- SHA256 content hash: `de42a5fdcac142c82feb375fec9f84234a536608772769123e23478ffa55a15a`
- Byte count: `176510`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-11`
  - Last commit: `4440ba0 (Phase-1b blinded SAPA packet freeze checkpoint; final review artifacts pending this state update)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-11T22:41:13Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `9dd6fd39246fd8847d51d5ae61fee2604942caa7`
- generation base commit: `4440ba0bda44517b63c8b4f05505b98651863ba9`
- Git blob hash: `3f3fceba4bc55f578d5cff3f665f4280102f18d7`
- SHA256 content hash: `6b22eeb671de9a941544433073dfd7653f086ca95405ddd691a96a750ad15bf3`
- Byte count: `29996`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-11T22:41:13Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `0693aaf76e5073c37377024130dbc2d0e80424fd`
- generation base commit: `4440ba0bda44517b63c8b4f05505b98651863ba9`
- Git blob hash: `4c50a36065107289371fdf9556ff4e01529b1443`
- SHA256 content hash: `e821e687c9d34069f7de9fb13a3ea6821614354ec8b980cfc2add51e65ec8d87`
- Byte count: `45298`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-11T22:41:13Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
