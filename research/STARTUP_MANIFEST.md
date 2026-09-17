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

- Generated timestamp UTC: `2026-09-17T09:26:56Z`
- Current branch: `codex/aa17-three-model-trait-factor-analysis`
- generation base commit: `547b07d5aee74611c7f2900f7095eb104b41c35e`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `547b07d5aee74611c7f2900f7095eb104b41c35e`
- generation base commit: `547b07d5aee74611c7f2900f7095eb104b41c35e`
- Git blob hash: `15d837249fff95b977f560ea8e155e3b3a3f8dc8`
- SHA256 content hash: `66219f2b639cc31143834a5b1823aea966bf205f3f672c7868254d4066cdc677`
- Byte count: `193493`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-17`
  - Last commit: `547b07d (AA-16 completed starting commit before AA-17)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-17T09:26:56Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `547b07d5aee74611c7f2900f7095eb104b41c35e`
- generation base commit: `547b07d5aee74611c7f2900f7095eb104b41c35e`
- Git blob hash: `8d34845cdd372f9473cfa980b526a1932d3b7c7d`
- SHA256 content hash: `a5533609e968b55f9ccbf999c369419819a5c7d35a6b1f46b3a81af8db8ef430`
- Byte count: `42469`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-17T09:26:56Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `547b07d5aee74611c7f2900f7095eb104b41c35e`
- generation base commit: `547b07d5aee74611c7f2900f7095eb104b41c35e`
- Git blob hash: `4f181919eac67de3d3aba2a2f3ede1c14d3ba226`
- SHA256 content hash: `d1a99131ffd4ae69df8051e4436665edc19d0b59e23a8bd765b256c37b32814e`
- Byte count: `55074`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-17T09:26:56Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
