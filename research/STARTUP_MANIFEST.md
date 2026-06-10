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

- Generated timestamp UTC: `2026-06-10T10:58:18Z`
- Current branch: `master`
- generation base commit: `9a48912bc9aa1ba45e4e79f702cdcaf6b1fcc118`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `9a48912bc9aa1ba45e4e79f702cdcaf6b1fcc118`
- generation base commit: `9a48912bc9aa1ba45e4e79f702cdcaf6b1fcc118`
- Git blob hash: `ecaf161e9163898d7dd6e385e0d29cedbbff1ccc`
- SHA256 content hash: `380a69a790b8bacdc2d39ffa0f79cc76acc99e814de3cd1a9c6d6a6499b8fd95`
- Byte count: `146220`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-06-10`
  - Last commit: `9a48912`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-06-10T10:58:18Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `9a48912bc9aa1ba45e4e79f702cdcaf6b1fcc118`
- generation base commit: `9a48912bc9aa1ba45e4e79f702cdcaf6b1fcc118`
- Git blob hash: `70fefd287640680064bdd08c2e366ae755cd278e`
- SHA256 content hash: `126b1e2b90d4a57deeeb95ebfe71ae4394be40ac7b92146fc59ee1f0a1d20fdf`
- Byte count: `14276`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-06-10`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-06-10T10:58:18Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `9a48912bc9aa1ba45e4e79f702cdcaf6b1fcc118`
- generation base commit: `9a48912bc9aa1ba45e4e79f702cdcaf6b1fcc118`
- Git blob hash: `e26316ca2149c97ae5a909a907871d53f0d08564`
- SHA256 content hash: `7f9d4ced8096e1ce6c1503d5a88ff92f1edbca53675580fbf744587c95165f90`
- Byte count: `40338`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-10`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-06-10T10:58:18Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
