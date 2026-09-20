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

- Generated timestamp UTC: `2026-09-20T00:07:15Z`
- Current branch: `codex/aa26-sapa-profile-information-gain`
- generation base commit: `cf6ce5b3b52a670682caff2683075e960d32e497`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/RESEARCH_STATE.md`
- Latest commit touching file: `cf6ce5b3b52a670682caff2683075e960d32e497`
- generation base commit: `cf6ce5b3b52a670682caff2683075e960d32e497`
- Git blob hash: `6957453f2d33f6de6a468e87867183bb31df845a`
- SHA256 content hash: `0ecaf0c7e85747ea1b222190285559f2df27780da7f1504135c0a5e07414f88e`
- Byte count: `212526`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-19`
  - Last commit: `cf6ce5b (before AA-26 completion unit)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-20T00:07:15Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/THREAD_START.md`
- Latest commit touching file: `cf6ce5b3b52a670682caff2683075e960d32e497`
- generation base commit: `cf6ce5b3b52a670682caff2683075e960d32e497`
- Git blob hash: `793edb440aab07bc300a9ffc12f6e23b409cf702`
- SHA256 content hash: `19b0919c8fcd677cb119696a8b895aa9e2fd0c6be3961879347b2a0a0596d9bd`
- Byte count: `51168`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-20`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-20T00:07:15Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `cf6ce5b3b52a670682caff2683075e960d32e497`
- generation base commit: `cf6ce5b3b52a670682caff2683075e960d32e497`
- Git blob hash: `b8d3ca93df9b33b428fb386d756cb8ed144d0734`
- SHA256 content hash: `31cfbf778f1f151d6da62807e290c4b5d63e66ec7bc963ada2d38040148852e5`
- Byte count: `71799`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-20`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-20T00:07:15Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
