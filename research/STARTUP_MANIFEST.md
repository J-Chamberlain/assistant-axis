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

- Generated timestamp UTC: `2026-09-12T17:02:28Z`
- Current branch: `codex/aa1-qwen-trait-family-human-inventory`
- generation base commit: `4d2bdb41134d8950e8d9f606ee68e8b646c73b6e`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `313c5cff6e071d707d37b1318343cde4ed510725`
- generation base commit: `4d2bdb41134d8950e8d9f606ee68e8b646c73b6e`
- Git blob hash: `80bc1b3b788eed0433bc1e134d930c049076d6fb`
- SHA256 content hash: `63fe62bdd6e5d54d747a45dcc2601ad636f3c6e7769a8dbf202b6221d52e51bd`
- Byte count: `188225`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-12`
  - Last commit: `4d2bdb4 (verified the frozen correlation-defined Qwen trait-family to SAPA measurement inventory before canonical-state reconciliation)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-12T17:02:28Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `313c5cff6e071d707d37b1318343cde4ed510725`
- generation base commit: `4d2bdb41134d8950e8d9f606ee68e8b646c73b6e`
- Git blob hash: `aa76eb9061064de74302982bd05bb4896d4c387c`
- SHA256 content hash: `b6f16e62d1adaafc7ee11f0ce0043372eb2c58a3dcd97757a21152e20f49a44a`
- Byte count: `40050`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-12`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-12T17:02:28Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `c1f241bd94a0ac0fd6e5a21a08392eda553e25bf`
- generation base commit: `4d2bdb41134d8950e8d9f606ee68e8b646c73b6e`
- Git blob hash: `96a1b2c77469a7cb5ca1cb67cb053850f5304029`
- SHA256 content hash: `7f543f3a5a5f8fa308c9ddfbf2efa6068ea7a7e516c7a133a08e14b63b1c69d0`
- Byte count: `50422`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-12`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-12T17:02:28Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
