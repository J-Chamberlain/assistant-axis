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

- Generated timestamp UTC: `2026-09-17T08:52:18Z`
- Current branch: `codex/aa16-sapa-hifwb-trait-pc-crosswalk`
- generation base commit: `aa7733b9bb2d768c3ce707c6dfe0d244a53828be`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `aa7733b9bb2d768c3ce707c6dfe0d244a53828be`
- generation base commit: `aa7733b9bb2d768c3ce707c6dfe0d244a53828be`
- Git blob hash: `942898ec813ca203df12da9974fab93786a29083`
- SHA256 content hash: `8e6a7e7dbf75f21492cc0b914ab38a187363e2077f28aedaef12582ffa83544d`
- Byte count: `191346`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-17`
  - Last commit: `aa7733b (AA-16 Stage 1 freeze checkpoint before final result commit)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-17T08:52:18Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `aa7733b9bb2d768c3ce707c6dfe0d244a53828be`
- generation base commit: `aa7733b9bb2d768c3ce707c6dfe0d244a53828be`
- Git blob hash: `a0fbe74da8263e88789863d309a72ad3d2c2765c`
- SHA256 content hash: `4f2b2bc68f19910ee6a5e188213d8d921a193e4aa8b91e10eb69d62b14eef697`
- Byte count: `41689`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-17T08:52:18Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `ffe188ac1373e96bb44bdc9c99125acb424bbe4f`
- generation base commit: `aa7733b9bb2d768c3ce707c6dfe0d244a53828be`
- Git blob hash: `419aaab0cdb9aae79ca851318c28498a351f0357`
- SHA256 content hash: `94b2cae940ce4ecd7e7f61ca717291e9e947bba9e17514816d56aa26845d44f0`
- Byte count: `54149`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-17`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-17T08:52:18Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
