# Overnight Run Lessons Synthesized

Date: 2026-05-26

## What Worked

Detached pod execution worked. The Qwen trickster Phase 1 job continued after chat-side monitoring degraded, reached 1200/1200 records, and preserved matching activation shards. JSONL plus `.pt` shard output was recoverable and integrity-checkable. The inference and scoring split worked: generation artifacts could be preserved once and scored later by different judges. Codex-based scoring produced a usable pragmatic subset, and score-conditioned validation reproduced the Lu trickster geometry with cosine 0.957557 for the score>=2 vector.

## What Failed

Chat continuity failed as an operational state system. The pod kept working, but the monitoring thread lost durable awareness. Pod lifecycle state was ambiguous, especially around whether to continue, preserve, or terminate. Browser-based termination was too unstable to serve as the primary closeout path. There was no canonical run registry, no standard heartbeat, and no single place to see preservation, integrity, scoring, validation, and termination status.

## What Became Canonical

Long pod jobs must run detached and emit heartbeat artifacts. Outputs must be preservable while in progress. Local integrity validation gates scoring. Scoring files must be judge-specific and must not overwrite stricter planned judge paths. Vector validation must report the score file used, candidate subset, reference vector, cosine to reference, and adaptive stopping result. Run lifecycle must be tracked outside chat.

## What Changed Operationally

Future runs use `research/workflow/` as the workflow canon. A run registry records lifecycle state. Each run emits manifest, heartbeat, integrity, preservation, termination, scoring summary, and validation summary artifacts where applicable. Execution tasks are tiered so monitoring, engineering, and methodology work use different expectations and model settings.

## What Should Never Be Repeated

Do not rely on chat memory as the only run-state record. Do not terminate a pod before preservation and integrity checks unless the user explicitly requests emergency termination. Do not infer final completion from partial local snapshots. Do not treat a substitute judge as strict Lu-method replication. Do not leave pod ID, endpoint, and termination status undocumented.

## Default Behavior Going Forward

Every long run starts with a manifest and registry entry. Every long run writes a heartbeat. Every preservation step records what was copied and where. Every closeout requires integrity before scoring and termination after preservation. Every scoring and validation result records the judge, method caveat, thresholds, and paths. Every meaningful operational decision updates `RESEARCH_STATE.md` or the run registry before the session closes.
