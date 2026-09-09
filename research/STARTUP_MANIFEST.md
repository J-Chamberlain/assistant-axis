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

- Generated timestamp UTC: `2026-09-09T13:54:25Z`
- Current branch: `master`
- generation base commit: `e7513f60697ee52d5ef3b6f1c3962756e54c22d5`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `e7513f60697ee52d5ef3b6f1c3962756e54c22d5`
- generation base commit: `e7513f60697ee52d5ef3b6f1c3962756e54c22d5`
- Git blob hash: `2e5115ec903d723e660f35620f1e0cf668598d7b`
- SHA256 content hash: `bad2ee511ff1de7830dede4b70ee6423549e43593acff82f1c40ba528ecc41e1`
- Byte count: `158619`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-09`
  - Last commit: `e7513f6 (base before emotion viewer implementation)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-09T13:54:25Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `e7513f60697ee52d5ef3b6f1c3962756e54c22d5`
- generation base commit: `e7513f60697ee52d5ef3b6f1c3962756e54c22d5`
- Git blob hash: `7371a4882370eba7c399ee11d6626163af15b96a`
- SHA256 content hash: `da83c5d549e4e9eaec1515cdf78e510c74005e1d43a7fe8f3a00ce1c5a61c07d`
- Byte count: `21847`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-09`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-09T13:54:25Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `96770accce38fa79d77435f1a8c94b6e286b395a`
- generation base commit: `e7513f60697ee52d5ef3b6f1c3962756e54c22d5`
- Git blob hash: `999673d640f24c34924fe8421b13c11245e4f23b`
- SHA256 content hash: `80840a6c9a2c22b6611f4f11d61a13f05b107375a5ca41fb1cb84b82017f4615`
- Byte count: `43979`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-10`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-09T13:54:25Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
