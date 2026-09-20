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

- Generated timestamp UTC: `2026-09-20T10:27:35Z`
- Current branch: `codex/aa27-ipip-neo-profile-plausibility`
- generation base commit: `6d564c3b1972be787ee7f645591225f9c9219abe`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa27-ipip-neo-profile-plausibility/research/RESEARCH_STATE.md`
- Latest commit touching file: `6d564c3b1972be787ee7f645591225f9c9219abe`
- generation base commit: `6d564c3b1972be787ee7f645591225f9c9219abe`
- Git blob hash: `a0e45bdc0efe6eebebe0afa6d67e8e865d778d5a`
- SHA256 content hash: `c969cc38827bfa9b0a4527fc4ad3b17b1f2ba44dda3ce853f70ff82be9c92506`
- Byte count: `213660`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-19`
  - Last commit: `cf6ce5b (before AA-26 completion unit)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-20T10:27:35Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa27-ipip-neo-profile-plausibility/research/THREAD_START.md`
- Latest commit touching file: `6d564c3b1972be787ee7f645591225f9c9219abe`
- generation base commit: `6d564c3b1972be787ee7f645591225f9c9219abe`
- Git blob hash: `7793c9af0019cd208b27d97d296df69985afb4a9`
- SHA256 content hash: `549666a10c81be66bce6e8d86be3b360ed79844f68a523fbf6bfb284bb98f4c8`
- Byte count: `52391`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-20`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-20T10:27:35Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa27-ipip-neo-profile-plausibility/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `91ad7519fe89b55921f58680a9a734e158320ca4`
- generation base commit: `6d564c3b1972be787ee7f645591225f9c9219abe`
- Git blob hash: `e38ec24e9187d0e2ddb228701941dd77de679ea0`
- SHA256 content hash: `b0696ccc2d7f26b100d0ef6ca6e6d1b628092dc7ae4cf87b70da97155d43742a`
- Byte count: `72485`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-20`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-20T10:27:35Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
