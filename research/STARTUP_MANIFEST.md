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

- Generated timestamp UTC: `2026-06-12T00:37:44Z`
- Current branch: `master`
- generation base commit: `dc22f2c4b18c96223981fc3577f07d47716d0a51`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `dc22f2c4b18c96223981fc3577f07d47716d0a51`
- generation base commit: `dc22f2c4b18c96223981fc3577f07d47716d0a51`
- Git blob hash: `eb5b3af37871b5b85a59559347d0bbf70f08f6f8`
- SHA256 content hash: `94ef6e4f45801ca7eb846b6592d6e3ab391bbe6dad9239ebe1d6906bd77f88c9`
- Byte count: `148185`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-06-11`
  - Last commit: `dc22f2c`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-06-12T00:37:44Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `972490cac2ebed4addce1b0b1438bdefc286294e`
- generation base commit: `dc22f2c4b18c96223981fc3577f07d47716d0a51`
- Git blob hash: `70f1b336f961d104a7e7dcb5ce9258bd727997a1`
- SHA256 content hash: `f1c51bfed1750d58192a952f4f0316e4107dcd6e4fb21a3bd071db25381e5bdd`
- Byte count: `15364`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-06-11`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-06-12T00:37:44Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `9a48912bc9aa1ba45e4e79f702cdcaf6b1fcc118`
- generation base commit: `dc22f2c4b18c96223981fc3577f07d47716d0a51`
- Git blob hash: `e26316ca2149c97ae5a909a907871d53f0d08564`
- SHA256 content hash: `7f9d4ced8096e1ce6c1503d5a88ff92f1edbca53675580fbf744587c95165f90`
- Byte count: `40338`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-10`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-06-12T00:37:44Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
