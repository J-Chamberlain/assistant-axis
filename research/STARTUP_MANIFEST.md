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

- Generated timestamp UTC: `2026-09-10T00:32:33Z`
- Current branch: `master`
- generation base commit: `03d99df985b77b4836043c237e0276bb7f3311a0`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `03d99df985b77b4836043c237e0276bb7f3311a0`
- generation base commit: `03d99df985b77b4836043c237e0276bb7f3311a0`
- Git blob hash: `35988f4f56524594cbdfb5845e1aec3fab8faf02`
- SHA256 content hash: `4f8e30cb9a568cb58c917fa3be0599735c8e53d9625ec5eca5ed2205d66e2137`
- Byte count: `163902`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-09-09`
  - Last commit: `03d99df (base before grouped-trait 3D landscape and precise camera controls)`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-09-10T00:32:33Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `03d99df985b77b4836043c237e0276bb7f3311a0`
- generation base commit: `03d99df985b77b4836043c237e0276bb7f3311a0`
- Git blob hash: `2df2cabd41f57d59d5596a0f6cf546b9f3b67ea3`
- SHA256 content hash: `356539a76701984f437b1c2734295d2ee0f36e5e73960194643e293dfea9e94f`
- Byte count: `24647`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-09-09`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-09-10T00:32:33Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `96770accce38fa79d77435f1a8c94b6e286b395a`
- generation base commit: `03d99df985b77b4836043c237e0276bb7f3311a0`
- Git blob hash: `999673d640f24c34924fe8421b13c11245e4f23b`
- SHA256 content hash: `80840a6c9a2c22b6611f4f11d61a13f05b107375a5ca41fb1cb84b82017f4615`
- Byte count: `43979`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-10`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-09-10T00:32:33Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
