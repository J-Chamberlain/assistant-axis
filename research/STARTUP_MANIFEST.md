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

- Generated timestamp UTC: `2026-06-04T00:39:19Z`
- Current branch: `master`
- generation base commit: `8507acc65b275c0db00d335aa9032f2a65675bc9`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `8507acc65b275c0db00d335aa9032f2a65675bc9`
- generation base commit: `8507acc65b275c0db00d335aa9032f2a65675bc9`
- Git blob hash: `ea9ffd322cbfa56a5ddafbfa9eac0040044f91d5`
- SHA256 content hash: `7b4b419da0eeb6f49321c68cdd22c7ddb52c7079064298071a3fdd20459bc9ab`
- Byte count: `126435`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-06-03`
  - Last commit: `265f03d`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-06-04T00:39:19Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `7a0fd21098f74de403abd210dafaf4e8819d4164`
- generation base commit: `8507acc65b275c0db00d335aa9032f2a65675bc9`
- Git blob hash: `97fc581c9ac4340cdf26531e5e74472cf86ca078`
- SHA256 content hash: `babb302215a2e9137cdf44e138be5e8739279e25062b8141375de377abfd51c5`
- Byte count: `6763`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-05-30`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-06-04T00:39:19Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `f328aef34478065341a51cdb270e77bb4132a1cf`
- generation base commit: `8507acc65b275c0db00d335aa9032f2a65675bc9`
- Git blob hash: `e35b7e8fc44d40435a6d8dd995b7376e35f67f77`
- SHA256 content hash: `9c263b90ae606cdc3da77fc89f1287382d8e0853e287b1691a7791103f4d3c1d`
- Byte count: `37892`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-05-31`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-06-04T00:39:19Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
