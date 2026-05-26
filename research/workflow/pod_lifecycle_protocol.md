# Pod Lifecycle Protocol

Purpose: make pod runs recoverable, auditable, and terminable without relying on chat memory.

## 1. Launch Sequence

Before launch, write a planned run entry in the run registry. Include run ID, intended script, model, GPU requirement, expected outputs, expected duration, and termination owner. Confirm local repo state and commit the script that will run on the pod. Copy or clone the exact committed script onto the pod, then record script path and commit hash in `manifest.json`.

## 2. Detached Execution Requirements

Long pod jobs must run detached from chat and SSH session lifetime. Use `nohup`, `tmux`, `screen`, or a process manager. Redirect stdout and stderr to a durable log file. The process must write a heartbeat artifact at regular intervals and a final completion marker when done.

Minimum detached command pattern:

```bash
nohup python3 path/to/run_script.py > run.log 2>&1 &
echo $! > run.pid
```

## 3. Preservation Checkpoints

Runs that produce JSONL plus activation shards must be copyable while in progress. Every checkpoint should preserve the JSONL, manifest, heartbeat, log, source script, and current shard directory. Partial snapshots must be labeled partial and must not be promoted to final until the integrity check passes against the planned count.

## 4. Local Integrity Requirements

A local integrity check is required before scoring, validation, or pod termination. At minimum it checks record count, unique work-unit keys, duplicate keys, empty responses, think artifacts, activation-saved flags, shard count, missing shard paths, and tensor shape spot checks. The result is saved as `integrity.json` and, when useful, a short Markdown report.

## 5. Pod Monitoring Behavior

Chat monitoring is not a durable state system. Every monitoring task must read heartbeat and logs from the pod or local snapshot, then update the run registry or `RESEARCH_STATE.md`. If chat context degrades, the next agent should be able to recover from artifacts alone.

Monitoring should report only high-signal state: latest rollout count, shard count, truncation or discard counts, GPU memory, disk state, ETA, and whether the process is alive.

## 6. Pod Termination Rules

Never terminate a pod before final or intentionally partial preservation is complete. Never terminate based only on dashboard appearance if SSH evidence suggests the process is alive. Termination happens only after local preservation and integrity status are recorded, unless the user explicitly instructs emergency termination.

## 7. Preferred Termination Path

Use a RunPod API or CLI termination path when credentials are available. Record pod ID, command used, timestamp, and response. After termination, confirm the pod no longer appears as running.

Preferred order:

1. RunPod API or CLI termination by pod ID.
2. RunPod dashboard termination.
3. In-pod shutdown attempt only as a last resort, and only with user confirmation when preservation status is uncertain.

## 8. Browser/Dashboard Fallback

Browser termination is allowed when API or CLI access is unavailable, but it must be treated as a fallback. Capture or record what the dashboard shows before and after termination. If the dashboard is unstable or ambiguous, do not infer termination from a single visual state.

## 9. Required Post-Termination Artifacts

After termination, save `termination.json` with pod ID, endpoint, termination method, timestamp, confirmation evidence, and any unresolved uncertainty. Update the run registry to `terminated` only after confirmation.

## 10. Do Not Terminate Before Preservation

This is the hard rule. If the run has produced unique outputs that are not already local and integrity-checked, preservation comes first. Termination without preservation is allowed only for explicit user-directed emergency cost control, and the final report must state that data may have been lost.
