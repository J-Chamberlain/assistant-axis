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

- Generated timestamp UTC: `2026-09-19T23:47:56Z`
- Current branch: `codex/aa26-sapa-profile-information-gain`
- generation base commit: `51e5f52c052d3bfdd5e30ca95f5025c4423606c0`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/RESEARCH_STATE.md`
- Latest commit touching file: `51e5f52c052d3bfdd5e30ca95f5025c4423606c0`
- generation base commit: `51e5f52c052d3bfdd5e30ca95f5025c4423606c0`
- Git blob hash: `ba9ef004b35fa54e53d536ca6a476028da0d79ae`
- SHA256 content hash: `6dafcf9eb5049f0621d9aec684864577042c63865fa77768d6524182b435344c`
- Byte count: `207752`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-19`
  - Last commit: `pending AA-23 remote commit (local analysis complete)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-19T23:47:56Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/THREAD_START.md`
- Latest commit touching file: `51e5f52c052d3bfdd5e30ca95f5025c4423606c0`
- generation base commit: `51e5f52c052d3bfdd5e30ca95f5025c4423606c0`
- Git blob hash: `d64e2772c0c238c2b64db3fa3202c2f674403746`
- SHA256 content hash: `4656b91e636ecae334a8056d19ae7a4f9e74cf9c6555f1d11fd8665433312ef4`
- Byte count: `50202`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-19`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-19T23:47:56Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `51e5f52c052d3bfdd5e30ca95f5025c4423606c0`
- generation base commit: `51e5f52c052d3bfdd5e30ca95f5025c4423606c0`
- Git blob hash: `3f762d9b2723bacbe4d5ccbe36b45ebadccd0cef`
- SHA256 content hash: `df26fec12e26eb94cb70d150ae31418444f8c0c75baf71ed0b56d6aa07eac121`
- Byte count: `70833`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-19`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-19T23:47:56Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
