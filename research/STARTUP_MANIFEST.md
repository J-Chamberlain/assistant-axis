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

- Generated timestamp UTC: `2026-09-15T10:05:31Z`
- Current branch: `codex/human-model-rosetta-translation-v1`
- generation base commit: `c6e3409b0f56bda821aaec0f43ca860bc1661223`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `4e150a756f3b027b0d8bf51cf8f6533334853b58`
- generation base commit: `c6e3409b0f56bda821aaec0f43ca860bc1661223`
- Git blob hash: `4b358339ed8e33c05e6cee914487688a0037241a`
- SHA256 content hash: `0e9437a5fd45ff6424a1328b0e1be4e1b3f75e8f30f5d7e48dd715c140daa462`
- Byte count: `173102`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-11`
  - Last commit: `ba1affb (base before Llama/Gemma trait-profile predictor result registration)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-15T10:05:31Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `4e150a756f3b027b0d8bf51cf8f6533334853b58`
- generation base commit: `c6e3409b0f56bda821aaec0f43ca860bc1661223`
- Git blob hash: `e6da9a9c6e62b84bfd5e15e458391404538ffba4`
- SHA256 content hash: `199b6f502eb2c1206cdd1aa67030dd5247ed60af5dffbdb947ace91ec6302604`
- Byte count: `29694`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-15T10:05:31Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `4e150a756f3b027b0d8bf51cf8f6533334853b58`
- generation base commit: `c6e3409b0f56bda821aaec0f43ca860bc1661223`
- Git blob hash: `ba5229da8be2fa9fd4b663748ca40e803c6824d8`
- SHA256 content hash: `3d909119dd12d2ce48a8e0b5ee3dad34c9cbb28f2ebacce949e8e0c8024c4677`
- Byte count: `46321`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-15T10:05:31Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
