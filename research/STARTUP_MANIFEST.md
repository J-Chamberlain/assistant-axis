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

- Generated timestamp UTC: `2026-09-20T16:59:19Z`
- Current branch: `codex/aa27-ipip-neo-profile-plausibility`
- generation base commit: `26df4ebc7da8f9d163580745b92b17f84e6b8ae7`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `26df4ebc7da8f9d163580745b92b17f84e6b8ae7`
- generation base commit: `26df4ebc7da8f9d163580745b92b17f84e6b8ae7`
- Git blob hash: `6e70599f364a3a926d05c47f5e440f76451894e5`
- SHA256 content hash: `a4f3d07433f9ea336a76c25a4dcf17edb6983ddd347f2cd9d1c29ac6b4b628ea`
- Byte count: `219449`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-20`
  - Last commit: `26df4eb (before presentation-table update)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-20T16:59:19Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `26df4ebc7da8f9d163580745b92b17f84e6b8ae7`
- generation base commit: `26df4ebc7da8f9d163580745b92b17f84e6b8ae7`
- Git blob hash: `95a8bde5d484c94d586eb553676c19c45c446a0d`
- SHA256 content hash: `2c2acc89678b29fb90ae23e191a23c5bfc4dde6d2ac523123d7cf58602f274e2`
- Byte count: `54444`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-20`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-20T16:59:19Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `26df4ebc7da8f9d163580745b92b17f84e6b8ae7`
- generation base commit: `26df4ebc7da8f9d163580745b92b17f84e6b8ae7`
- Git blob hash: `1a13a4e69f7abf8a08ba0fafecdecc89eb194ccd`
- SHA256 content hash: `672230ea6d881ab72c4c485222a48151eb417ec3d48cc673fe49ccc328e45a5a`
- Byte count: `74538`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-09-20`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-20T16:59:19Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
