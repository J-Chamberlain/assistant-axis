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

- Generated timestamp UTC: `2026-06-06T23:36:20Z`
- Current branch: `master`
- generation base commit: `44d852ef2c44bb75b5fca5b438bb95702cac1781`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `44d852ef2c44bb75b5fca5b438bb95702cac1781`
- generation base commit: `44d852ef2c44bb75b5fca5b438bb95702cac1781`
- Git blob hash: `9fff0a364fd84887a0de6fac685f984fe7843be2`
- SHA256 content hash: `95e9588511632bb5f4a391cfe7368c33e15e4b9005325d715c632526cb27cb9e`
- Byte count: `144111`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-06-05`
  - Last commit: `069ef31`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-06-06T23:36:20Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `140b554ffdad5c9a709062d84e17c77e571d2ae2`
- generation base commit: `44d852ef2c44bb75b5fca5b438bb95702cac1781`
- Git blob hash: `fd1d8b1bfba3bf22b2dc883a2fffc6794165b8fc`
- SHA256 content hash: `1761572241c7ca58f85d94b35cac39baf6e625ab8e512f72875da3a20e712cb0`
- Byte count: `12058`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-06-05`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-06-06T23:36:20Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `069ef3107e971cb3f8674bcdf3a82a4a2a3ee681`
- generation base commit: `44d852ef2c44bb75b5fca5b438bb95702cac1781`
- Git blob hash: `c31511eb6452d30a232ba26a43516078295534b4`
- SHA256 content hash: `44f588d3d7e2a006d08aa5763354104d74ac2320e1589518d82d3083baf93804`
- Byte count: `38355`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-05`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-06-06T23:36:20Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
