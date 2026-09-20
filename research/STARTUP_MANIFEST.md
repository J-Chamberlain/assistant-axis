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

- Generated timestamp UTC: `2026-09-20T10:16:01Z`
- Current branch: `codex/aa27-ipip-neo-profile-plausibility`
- generation base commit: `91ad7519fe89b55921f58680a9a734e158320ca4`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa27-ipip-neo-profile-plausibility/research/RESEARCH_STATE.md`
- Latest commit touching file: `91ad7519fe89b55921f58680a9a734e158320ca4`
- generation base commit: `91ad7519fe89b55921f58680a9a734e158320ca4`
- Git blob hash: `843c1b53b8c0c8e18f5681b7c87b3b306d10730f`
- SHA256 content hash: `0e06c08d6352b52252d0202a7784d86b929c09ecaf60861c1b68ccedf19cac78`
- Byte count: `213024`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-19`
  - Last commit: `cf6ce5b (before AA-26 completion unit)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-20T10:16:01Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa27-ipip-neo-profile-plausibility/research/THREAD_START.md`
- Latest commit touching file: `91ad7519fe89b55921f58680a9a734e158320ca4`
- generation base commit: `91ad7519fe89b55921f58680a9a734e158320ca4`
- Git blob hash: `2c9d044be4076834a4f2903e638b773587ee494d`
- SHA256 content hash: `e1261a273c2dd94175869978bc1e9b5711ab77a73b90fccb19930f1576ed433d`
- Byte count: `51705`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-20`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-20T10:16:01Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa27-ipip-neo-profile-plausibility/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `91ad7519fe89b55921f58680a9a734e158320ca4`
- generation base commit: `91ad7519fe89b55921f58680a9a734e158320ca4`
- Git blob hash: `b8d3ca93df9b33b428fb386d756cb8ed144d0734`
- SHA256 content hash: `31cfbf778f1f151d6da62807e290c4b5d63e66ec7bc963ada2d38040148852e5`
- Byte count: `71799`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-20`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-20T10:16:01Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
