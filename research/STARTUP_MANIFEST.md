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

- Generated timestamp UTC: `2026-09-17T14:41:53Z`
- Current branch: `codex/aa21-bigfive-hifwb-persona-projection`
- generation base commit: `8fef071939ae7ffe6096888fe6f207b6658b6145`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `8fef071939ae7ffe6096888fe6f207b6658b6145`
- generation base commit: `8fef071939ae7ffe6096888fe6f207b6658b6145`
- Git blob hash: `1725d9680960057614ce494161e97062d1b6f2e6`
- SHA256 content hash: `27e0361fef571ee50f7640376b8db5e9aefef7901bf6da1b76796707ec452cc6`
- Byte count: `201033`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-17`
  - Last commit: `pending AA-23 remote commit (local analysis complete)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-17T14:41:53Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- generation base commit: `8fef071939ae7ffe6096888fe6f207b6658b6145`
- Git blob hash: `5cb52f1dcfbe13d38a965a32ec1ff5a095cd2268`
- SHA256 content hash: `9ac11761eec89d7c7117b70a0e67835da8597f69a5d762a1a8350aa3a9b248c9`
- Byte count: `45950`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-17T14:41:53Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `8fef071939ae7ffe6096888fe6f207b6658b6145`
- generation base commit: `8fef071939ae7ffe6096888fe6f207b6658b6145`
- Git blob hash: `d0b28d96cdae741af1b287229b18381a70a0013c`
- SHA256 content hash: `4b10f26b0a51d28cb52d2d9b6649d50972182e4ea367decf737e9689c97af735`
- Byte count: `65096`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-17T14:41:53Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
