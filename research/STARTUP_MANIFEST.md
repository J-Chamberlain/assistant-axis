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

- Generated timestamp UTC: `2026-06-05T14:21:23Z`
- Current branch: `master`
- generation base commit: `1b15407f4f9370f3917f60c8d8bdd1f3720cd5fe`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `1b15407f4f9370f3917f60c8d8bdd1f3720cd5fe`
- generation base commit: `1b15407f4f9370f3917f60c8d8bdd1f3720cd5fe`
- Git blob hash: `6ed3d9c66850fb71570922b21fc357845d689d04`
- SHA256 content hash: `fdf01de64edc50c2bc7d3a30c8d2a75618e1774fccea0b8a6768546e48ef3a80`
- Byte count: `140208`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-06-05`
  - Last commit: `1b15407`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-06-05T14:21:23Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `1b15407f4f9370f3917f60c8d8bdd1f3720cd5fe`
- generation base commit: `1b15407f4f9370f3917f60c8d8bdd1f3720cd5fe`
- Git blob hash: `9a4a574479433917027bc05313665b7bf231256e`
- SHA256 content hash: `b4e5c084d2b8f7ef231495ca73fd456da35e17c7c0083223913265a036e239b6`
- Byte count: `10994`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-06-05`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-06-05T14:21:23Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `f328aef34478065341a51cdb270e77bb4132a1cf`
- generation base commit: `1b15407f4f9370f3917f60c8d8bdd1f3720cd5fe`
- Git blob hash: `c31511eb6452d30a232ba26a43516078295534b4`
- SHA256 content hash: `44f588d3d7e2a006d08aa5763354104d74ac2320e1589518d82d3083baf93804`
- Byte count: `38355`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-05`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-06-05T14:21:23Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
