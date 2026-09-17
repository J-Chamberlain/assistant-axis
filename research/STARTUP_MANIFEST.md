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

- Generated timestamp UTC: `2026-09-17T15:25:22Z`
- Current branch: `codex/aa25-intervention-bigfive-transport`
- generation base commit: `ba868ec947de47ac2f92516364bd758c8081b604`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `ba868ec947de47ac2f92516364bd758c8081b604`
- generation base commit: `ba868ec947de47ac2f92516364bd758c8081b604`
- Git blob hash: `759078dfdc9e693e24dedd348413aaea2016113e`
- SHA256 content hash: `048b0f52ff4d779389fbc4b4b1cfc32e81faa0d7590571e888ca2cb02e186792`
- Byte count: `201765`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-17`
  - Last commit: `pending AA-23 remote commit (local analysis complete)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-17T15:25:22Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `e24e980b6713c59c7f0fed2556faca4072f84af3`
- generation base commit: `ba868ec947de47ac2f92516364bd758c8081b604`
- Git blob hash: `5cb52f1dcfbe13d38a965a32ec1ff5a095cd2268`
- SHA256 content hash: `9ac11761eec89d7c7117b70a0e67835da8597f69a5d762a1a8350aa3a9b248c9`
- Byte count: `45950`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-17T15:25:22Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `ba868ec947de47ac2f92516364bd758c8081b604`
- generation base commit: `ba868ec947de47ac2f92516364bd758c8081b604`
- Git blob hash: `1141975b7604d841d86afdbb36a8fc42ec3ab962`
- SHA256 content hash: `c5633443254199ecd290d072077ea9d76c2b3e54bdee48237c5bdf947f237b2a`
- Byte count: `66424`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-17T15:25:22Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
