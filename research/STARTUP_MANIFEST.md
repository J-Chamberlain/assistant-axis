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

- Generated timestamp UTC: `2026-09-17T14:13:33Z`
- Current branch: `codex/aa21-bigfive-hifwb-persona-projection`
- generation base commit: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- generation base commit: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- Git blob hash: `6da3d94298e28f5bfa23cd2cb8a1481c39cb0f35`
- SHA256 content hash: `630e3b7cb082b20a888937ac9c51989137382c6940c710fbe3e708f4fd4a5e97`
- Byte count: `199377`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-17`
  - Last commit: `pending AA-22 remote commit (local analysis complete)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-17T14:13:33Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- generation base commit: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- Git blob hash: `5cb52f1dcfbe13d38a965a32ec1ff5a095cd2268`
- SHA256 content hash: `9ac11761eec89d7c7117b70a0e67835da8597f69a5d762a1a8350aa3a9b248c9`
- Byte count: `45950`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-17T14:13:33Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- generation base commit: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- Git blob hash: `9972493aedb21977b6abd1d81e286bdeb5ddef0a`
- SHA256 content hash: `5c9d04f15db2a48592f17a022112ad7c728d5261e3e1e402e8ea02daf64afd00`
- Byte count: `61780`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-17T14:13:33Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
