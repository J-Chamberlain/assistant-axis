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

- Generated timestamp UTC: `2026-09-19T23:06:47Z`
- Current branch: `codex/aa26-sapa-profile-information-gain`
- generation base commit: `56902f6e918d1838f1c28d841bf58a459fd80a16`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/RESEARCH_STATE.md`
- Latest commit touching file: `56902f6e918d1838f1c28d841bf58a459fd80a16`
- generation base commit: `56902f6e918d1838f1c28d841bf58a459fd80a16`
- Git blob hash: `8df73d8dd6b3884838351b9e8dc6a6185db81a99`
- SHA256 content hash: `bde7bc10cf7501017ddf6caa5e14d2aecbe7fe79b96ba9a2ed33fa406abfb711`
- Byte count: `204058`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-19`
  - Last commit: `pending AA-23 remote commit (local analysis complete)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-19T23:06:47Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/THREAD_START.md`
- Latest commit touching file: `56902f6e918d1838f1c28d841bf58a459fd80a16`
- generation base commit: `56902f6e918d1838f1c28d841bf58a459fd80a16`
- Git blob hash: `415a41aae2b462b3f760231cde357dc35a55076d`
- SHA256 content hash: `86f34320d09ce5bf018e8cd059ecbf5a2d0bb72764864cdc2747a7e05a54404a`
- Byte count: `47178`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-19`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-19T23:06:47Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/codex/aa26-sapa-profile-information-gain/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `2944dcb365fa79940b189a3854d262ffa735fccf`
- generation base commit: `56902f6e918d1838f1c28d841bf58a459fd80a16`
- Git blob hash: `54be35240a38f5d48afb394783d75c3c308b4e71`
- SHA256 content hash: `2f09d3f2c7984fd487851ee2913c4926819c52391e3c68caee8f5084cf9cc599`
- Byte count: `67241`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-19`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-19T23:06:47Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
