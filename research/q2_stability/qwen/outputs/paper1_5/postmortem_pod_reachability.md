# Postmortem Pod Reachability

Audit date: 2026-05-26

## CLI checks

- `which runpodctl`: `/Users/alfred/.local/bin/runpodctl`
- `runpodctl get pod`: failed with `API key not found`.
- `runpodctl list pods`: unsupported command for installed CLI; also no authenticated pod listing was available.

## Local endpoint evidence

- Shell history contained older direct SSH endpoints including `216.81.245.98:15589` and `154.54.102.53:15352` plus RunPod proxy usernames.
- `~/.ssh/known_hosts` contained multiple RunPod direct TCP endpoints from recent sessions.
- Candidate probes were non-destructive: `hostname`, `ps aux | grep phase1`, and log tails only.

## Probe result

- Most historical endpoints refused SSH connections.
- Reachable endpoint found: `root@213.173.102.6 -p 22707`.
- Host responded with container hostname `2be6c38dc2d8`.
- Running process found: `python3 -u research/q2_stability/qwen/scripts/phase1_inference_only_v4.py`.
- The pod was not terminated.

## Live pod inspection

At first inspection, the pod reported:

```text
1119 /root/assistant-axis/research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl
1119 activation .pt files
38M /root/assistant-axis/research/q2_stability/qwen/outputs/paper1_5
```

A later inspection showed:

```text
1127 /root/assistant-axis/research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl
1127 activation .pt files
latest checkpoint: [new=1125 total=1125/1200] think_discards=0 truncated=669 rate=27.5s ETA=0.6hr GPU=65.5GB
```

## Preservation action

A local snapshot was copied from the live pod before any termination decision:

- `research/q2_stability/qwen/scripts/phase1_inference_only_v4.py`
- `research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl`
- `research/q2_stability/qwen/outputs/paper1_5/trickster_phase1_manifest.json`
- `research/q2_stability/qwen/outputs/paper1_5/activations_trickster/`

Local snapshot after tar copy contained 1126 JSONL records and 1126 activation shards. The pod continued running after the snapshot, so local snapshot may lag the live pod.

## Recommendation

RunPod dashboard verification is still recommended because `runpodctl` cannot authenticate locally. Do not terminate the live pod until final outputs are copied after completion or the user explicitly authorizes stopping it.
