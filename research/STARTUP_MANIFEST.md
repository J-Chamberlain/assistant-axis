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

- Generated timestamp UTC: `2026-09-13T18:31:51Z`
- Current branch: `codex/aa12-human-model-profile-correspondence`
- generation base commit: `6fd89fb95ff794e82d505f0913fcbad118910e87`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `6fd89fb95ff794e82d505f0913fcbad118910e87`
- generation base commit: `6fd89fb95ff794e82d505f0913fcbad118910e87`
- Git blob hash: `5272327fcd5cd9e4d776a199d4771ebdc7cc0a15`
- SHA256 content hash: `37063bd9df43b6fdfd7711097e146e81d4c170144a809d93635723065398462e`
- Byte count: `196527`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-13`
  - Last commit: `035b7f6 (finalized exact aggregate human/model correspondence artifact lineage before canonical maintenance)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-13T18:31:51Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `6fd89fb95ff794e82d505f0913fcbad118910e87`
- generation base commit: `6fd89fb95ff794e82d505f0913fcbad118910e87`
- Git blob hash: `daad4b26690a47080a2f16bc7a40b53b0e9ff40b`
- SHA256 content hash: `84573c20665f504177efa888cdc5500f4e434018ef42c83c43fb589d2c6157e4`
- Byte count: `44209`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-13`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-13T18:31:51Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `6fd89fb95ff794e82d505f0913fcbad118910e87`
- generation base commit: `6fd89fb95ff794e82d505f0913fcbad118910e87`
- Git blob hash: `f32de2e3631655d524a959698c69b5d6e7c65fa6`
- SHA256 content hash: `b4dd75a7feff25dbb9bb4b034ac13de3e89e978cf1b3f611450ddaefc5aa4d6a`
- Byte count: `53260`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-13`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-13T18:31:51Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
