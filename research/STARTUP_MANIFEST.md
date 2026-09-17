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

- Generated timestamp UTC: `2026-09-17T10:14:45Z`
- Current branch: `codex/aa18-three-model-consensus-trait-structure`
- generation base commit: `05ded7f8edd05550e3f9a7e8b18c3926cc51b3c5`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `68afc62fdea70bf0dc04e1f60fd423991cd2a921`
- generation base commit: `05ded7f8edd05550e3f9a7e8b18c3926cc51b3c5`
- Git blob hash: `9ae242b20003d53053b08ab2b6fe2d6b0c579c69`
- SHA256 content hash: `7ff0eba5eaa7c01a03a02c2dca1664b586e146118770006e7b2fab407b677063`
- Byte count: `194460`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-17`
  - Last commit: `05ded7f (AA-17 analytical base before AA-18)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-17T10:14:45Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `68afc62fdea70bf0dc04e1f60fd423991cd2a921`
- generation base commit: `05ded7f8edd05550e3f9a7e8b18c3926cc51b3c5`
- Git blob hash: `09adebd1bd1a2464016e950f384b06530e301dcb`
- SHA256 content hash: `9ccb8c3e2d7b0e7e06a21f826587ce4bd279196d6a70b47c150cd150627af5f8`
- Byte count: `43391`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-17T10:14:45Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `68afc62fdea70bf0dc04e1f60fd423991cd2a921`
- generation base commit: `05ded7f8edd05550e3f9a7e8b18c3926cc51b3c5`
- Git blob hash: `8432dd9643a5f31b30d99da1b5034bfa6de76eaf`
- SHA256 content hash: `6fe4627390050e1756948f96277ee388ea9a4c6f9ff21447cb8bcb78d2602efe`
- Byte count: `56130`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-17T10:14:45Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
