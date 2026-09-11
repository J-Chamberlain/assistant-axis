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

- Generated timestamp UTC: `2026-09-11T23:19:26Z`
- Current branch: `codex/qwen-trait-sparsity`
- generation base commit: `afb53d4951df421eacb36a72dc964be52a74484d`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `6654e2e5f8914790df65038417f46a7d61202c8a`
- generation base commit: `afb53d4951df421eacb36a72dc964be52a74484d`
- Git blob hash: `15d580a062b890c3f86197a2cd03be58cc07051a`
- SHA256 content hash: `f7260c2d3a46765af9b82181f23b2cb2ffcaafd8b1c96297b1dac2cac49594bf`
- Byte count: `176639`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-11`
  - Last commit: `afb53d4 (AA-4 analysis runner before result registration)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-11T23:19:26Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `6654e2e5f8914790df65038417f46a7d61202c8a`
- generation base commit: `afb53d4951df421eacb36a72dc964be52a74484d`
- Git blob hash: `157826573f4eebe9863a78fb62c79f4b4c421a02`
- SHA256 content hash: `f882176831bfe4d2c3a43569fb4e91a50b970feab0d837a4977fab451335cf58`
- Byte count: `31017`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-11T23:19:26Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `0693aaf76e5073c37377024130dbc2d0e80424fd`
- generation base commit: `afb53d4951df421eacb36a72dc964be52a74484d`
- Git blob hash: `8633b30347c7b1f076058d3e4524167b123313ed`
- SHA256 content hash: `e76cb93c2eb49812f37057031cbaa6097e768356d3afee3fe2b933bca254d006`
- Byte count: `46431`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-11T23:19:26Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
