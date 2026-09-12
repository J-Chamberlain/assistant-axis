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

- Generated timestamp UTC: `2026-09-12T02:12:33Z`
- Current branch: `codex/aa7-human-trait-convergence`
- generation base commit: `68dc2f89b4c2a146825c52ddecf02e6394f3907e`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `8a512401751799fac95324ce638d170a02d45e45`
- generation base commit: `68dc2f89b4c2a146825c52ddecf02e6394f3907e`
- Git blob hash: `e83c4f1839275f5bac30626d39449e0e3de4babe`
- SHA256 content hash: `6aed934d3d810c15bd0d75df50b42b04913558cfab92876d971d3b1fc9eb57e7`
- Byte count: `184743`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-12`
  - Last commit: `68dc2f8 (inventoried the completed AA-7 analysis artifacts after the fully reproduced result commit 717caba)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-12T02:12:33Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `d918ca3a9c73d05a8f5bb21c77af20f516a90587`
- generation base commit: `68dc2f89b4c2a146825c52ddecf02e6394f3907e`
- Git blob hash: `55bb39ff29f4f4e02055e263b2c3212ca70aadf4`
- SHA256 content hash: `b2321bb87cb6ce6dea285f484ae5bbaa67b65f773e64d8e06f546fbc2c6a6a3f`
- Byte count: `38143`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-12`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-12T02:12:33Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `c1f241bd94a0ac0fd6e5a21a08392eda553e25bf`
- generation base commit: `68dc2f89b4c2a146825c52ddecf02e6394f3907e`
- Git blob hash: `e9e0d259388f671dc437e6ce0f3b8d5827900356`
- SHA256 content hash: `b38152956dee1bddbc1021075f87f968981787bfac2d082b98ce22718a0ad211`
- Byte count: `49968`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-12`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-12T02:12:33Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
