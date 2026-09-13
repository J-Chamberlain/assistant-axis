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

- Generated timestamp UTC: `2026-09-13T13:11:37Z`
- Current branch: `codex/aa11-human-model-correspondence-tracks`
- generation base commit: `bc1168c7232f92b2c4db27c76d221851ace3589e`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `bc1168c7232f92b2c4db27c76d221851ace3589e`
- generation base commit: `bc1168c7232f92b2c4db27c76d221851ace3589e`
- Git blob hash: `a26c70d186bdfcc98c6a4ae3a7fd9368a9fc49b0`
- SHA256 content hash: `6af428e46ab261242a40572a7d9e8cb5392bfffff7ff8996a2264b1bbc1e877f`
- Byte count: `186089`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-13`
  - Last commit: `1027606 (introduced the AA-11 human/model correspondence-track continuity note)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-13T13:11:37Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `1027606ea2cb4d4c4094a928f99b1d0554a5c270`
- generation base commit: `bc1168c7232f92b2c4db27c76d221851ace3589e`
- Git blob hash: `effd12f06b9e351ea7c10e36cf952ca2e6b47716`
- SHA256 content hash: `163aa9873e93b4e1b64a880f56847599609a858320e743b4276d1452d0589fc4`
- Byte count: `39243`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-13`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-13T13:11:37Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `b9b6008ac4cff37bfef98bd2103a9cb9edf3a3a6`
- generation base commit: `bc1168c7232f92b2c4db27c76d221851ace3589e`
- Git blob hash: `96a1b2c77469a7cb5ca1cb67cb053850f5304029`
- SHA256 content hash: `7f543f3a5a5f8fa308c9ddfbf2efa6068ea7a7e516c7a133a08e14b63b1c69d0`
- Byte count: `50422`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-12`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-13T13:11:37Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
