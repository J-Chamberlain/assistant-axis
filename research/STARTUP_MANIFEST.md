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

- Generated timestamp UTC: `2026-06-15T09:20:43Z`
- Current branch: `master`
- generation base commit: `b895dffc682c5eb7919125f74e93c22e4a5e611f`
- Note: The generation base commit is the repo HEAD observed before this manifest was committed. It may differ from the commit that contains the manifest.
- Manifest generator: `scripts/update_startup_manifest.py`

## Canonical Startup Files

### `research/RESEARCH_STATE.md`

- Path: `research/RESEARCH_STATE.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/RESEARCH_STATE.md`
- Latest commit touching file: `b895dffc682c5eb7919125f74e93c22e4a5e611f`
- generation base commit: `b895dffc682c5eb7919125f74e93c22e4a5e611f`
- Git blob hash: `295f7fba6909cdc45c297e84f329f848c9dbf2ed`
- SHA256 content hash: `d9dc6acf554c454278fe93b7efd0c6437e29b2713367d5ec2941b5ac36d31ae0`
- Byte count: `151799`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical project state`
  - Last updated: `2026-06-15`
  - Last commit: `b895dff`
  - Title/header or first non-empty line: `# RESEARCH_STATE.md`
- Generated timestamp UTC: `2026-06-15T09:20:43Z`

### `research/THREAD_START.md`

- Path: `research/THREAD_START.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/THREAD_START.md`
- Latest commit touching file: `b895dffc682c5eb7919125f74e93c22e4a5e611f`
- generation base commit: `b895dffc682c5eb7919125f74e93c22e4a5e611f`
- Git blob hash: `3b94b48b9d7a33de51045fc1fcecfee6f1e86f4f`
- SHA256 content hash: `17cb8f29d0c1ac32538a9754a6af04bbd4da41296da205ca03e4538248c1d1e8`
- Byte count: `17710`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `session continuity and immediate priorities`
  - Last updated: `2026-06-15`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Thread Start`
- Generated timestamp UTC: `2026-06-15T09:20:43Z`

### `research/CLAIMS_REGISTER.md`

- Path: `research/CLAIMS_REGISTER.md`
- Raw GitHub URL: `https://raw.githubusercontent.com/J-Chamberlain/assistant-axis/master/research/CLAIMS_REGISTER.md`
- Latest commit touching file: `8e2cac860c85a13ede7d25bf2df599630e9fe999`
- generation base commit: `b895dffc682c5eb7919125f74e93c22e4a5e611f`
- Git blob hash: `786991b801a443e2345f0cd571133c39b37e0cd3`
- SHA256 content hash: `636fee96e4cbc99fbf8d6b765f9bf5ed8b2cb0702411e8193d2b708f511c62b5`
- Byte count: `43075`
- Visible metadata:
  - Canonical startup file: `yes`
  - State role: `canonical claim status`
  - Last updated: `2026-06-10`
  - Last commit: `not present`
  - Title/header or first non-empty line: `# Claims Register`
- Generated timestamp UTC: `2026-06-15T09:20:43Z`

## Maintenance Rule

Whenever `research/RESEARCH_STATE.md`, `research/THREAD_START.md`, or `research/CLAIMS_REGISTER.md` changes, run:

```bash
python3 scripts/update_startup_manifest.py
```

Commit `research/STARTUP_MANIFEST.md` in the same change as the startup file update.
