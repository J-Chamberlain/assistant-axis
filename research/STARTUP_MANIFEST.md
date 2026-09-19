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

- Generated timestamp UTC: `2026-09-19T23:23:54Z`
- Current branch: `codex/aa26-sapa-profile-information-gain`
- generation base commit: `bcec11d9db9b2e87554012bb3d2f5f2a8201df6f`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/RESEARCH_STATE.md`
- Latest commit touching file: `bcec11d9db9b2e87554012bb3d2f5f2a8201df6f`
- generation base commit: `bcec11d9db9b2e87554012bb3d2f5f2a8201df6f`
- Git blob hash: `b325d7ad38b89c0d49c212cc8eeb49d8b497bb7c`
- SHA256 content hash: `8ec27130e1a0cf75d84d52f359f0de69df36405ae95674c1b0003402e101b9af`
- Byte count: `206211`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-19`
  - Last commit: `pending AA-23 remote commit (local analysis complete)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-19T23:23:54Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/THREAD_START.md`
- Latest commit touching file: `bcec11d9db9b2e87554012bb3d2f5f2a8201df6f`
- generation base commit: `bcec11d9db9b2e87554012bb3d2f5f2a8201df6f`
- Git blob hash: `63726a7b134d7963f1aea0de3fe000564f23fed0`
- SHA256 content hash: `02adee3130d26dd9a5fee16383046b8f187d60c4d51f25d0092a44c6203d4f8d`
- Byte count: `48562`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-19`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-19T23:23:54Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `bcec11d9db9b2e87554012bb3d2f5f2a8201df6f`
- generation base commit: `bcec11d9db9b2e87554012bb3d2f5f2a8201df6f`
- Git blob hash: `441a182b709f39452f7a1f5eecb80e42a70f0d92`
- SHA256 content hash: `1ee5c79d93a18c66e06c2ec4a2ec164c0992acb2dd5b0941f2ff0e1b530a6beb`
- Byte count: `69193`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-19`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-19T23:23:54Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
