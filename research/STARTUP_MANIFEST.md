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

- Generated timestamp UTC: `2026-09-19T23:41:04Z`
- Current branch: `codex/aa26-sapa-profile-information-gain`
- generation base commit: `d4bd3ff9fa74472353f6db010cee07346c036be0`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/RESEARCH_STATE.md`
- Latest commit touching file: `d4bd3ff9fa74472353f6db010cee07346c036be0`
- generation base commit: `d4bd3ff9fa74472353f6db010cee07346c036be0`
- Git blob hash: `1ac99b74e0f92ffdffaf2a456a51ddedbd357f58`
- SHA256 content hash: `8c1f79e598f9679fe02003a69b526756a334ef35c0d5b11661f2b61a36eb38ae`
- Byte count: `207029`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-19`
  - Last commit: `pending AA-23 remote commit (local analysis complete)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-19T23:41:04Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/THREAD_START.md`
- Latest commit touching file: `d4bd3ff9fa74472353f6db010cee07346c036be0`
- generation base commit: `d4bd3ff9fa74472353f6db010cee07346c036be0`
- Git blob hash: `9534d932672ac62eca8e2d659d06ba1b7d2f865b`
- SHA256 content hash: `95da36eeb59fddb41adf80f801ba91bda8e0f5f4c2a39e159e510dab1f7a219e`
- Byte count: `49433`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-19`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-19T23:41:04Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `d4bd3ff9fa74472353f6db010cee07346c036be0`
- generation base commit: `d4bd3ff9fa74472353f6db010cee07346c036be0`
- Git blob hash: `5a311ff357706448b66f2a4a54e9eac401bc63d9`
- SHA256 content hash: `37825b75559943c19a99194c50ada2da87ca491605008c7726f4c7383efeef09`
- Byte count: `70064`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-19`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-19T23:41:04Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
