# RunPod Pod Termination Runbook

Last updated: 2026-05-26

This note captures lessons from the Qwen trickster Phase 1 pod run, where the job completed successfully but termination was initially blocked because in-container shutdown commands did not stop the RunPod pod. Use this as the checklist for future long-running GPU jobs.

## What worked

- Final output preservation worked: copy JSONL, manifest, logs, script, and activation shards locally before termination.
- Integrity checks worked: verify JSONL line count, unique `(sp_idx, q_idx)` pairs, activation shard count, activation path consistency, think-artifact count, truncation count, full `response_text` presence, and tensor shape/dtype spot checks.
- Git protection worked: activation shard directories were ignored, and final committed artifacts excluded `.pt` activation tensors.
- SSH refusal is a useful confirmation signal after termination, but it is not sufficient by itself unless paired with RunPod API/dashboard confirmation.
- `runpodctl` worked once `RUNPOD_API_KEY` was provided from `~/.runpod_api_key`; `runpodctl pod list -o json` returning `[]` confirmed no pods were running.

## What did not work

- In-container shutdown is not durable termination. The following commands did not reliably terminate the pod:
  - `kill -TERM 1`
  - `kill -KILL 1`
  - killing `/start.sh` or its `sleep infinity` child
  - `poweroff -f`
- RunPod may restart the container after PID/process death, so SSH can briefly refuse and then become reachable again. Treat a single SSH refusal as provisional until repeated and/or API-confirmed.
- Computer Use was unavailable in this session: app listing and Chrome/Safari state inspection timed out. Dashboard termination through UI automation was therefore not reliable.
- Chrome automation was also unavailable: the browser bridge initialized, but reported no controllable browsers.
- `runpodctl` was installed but unusable until the API key existed. The prior config had no usable API key.

## Required termination sequence

1. Confirm the job is complete or intentionally stopped:

```bash
ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=8 \
  -p "$PORT" -i ~/.ssh/id_ed25519 root@"$POD_IP" \
  'ps aux | grep -E "phase1|run_dyad|python" | grep -v grep || true'
```

2. Copy all required outputs before termination:

```bash
scp -P "$PORT" -i ~/.ssh/id_ed25519 -r \
  root@"$POD_IP":/root/assistant-axis/research/q2_stability/qwen/outputs/paper1_5/ \
  /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/q2_stability/qwen/outputs/
```

3. Rerun local integrity checks before terminating. At minimum verify:

- JSONL line count equals expected rollout count.
- Unique `(sp_idx, q_idx)` count equals JSONL line count.
- Duplicate pair count is zero.
- `activation_saved=True` records match existing activation files.
- Activation shard count matches expected count.
- `think_artifact=True` count is reported.
- `truncated=True` count is reported.
- No `response_text` fields are empty.
- No literal `<think>` or `</think>` tags appear in response text.
- Sample or full activation tensors load and have expected shape/dtype.

4. Commit or otherwise preserve the final integrity report before termination:

```bash
git add research/RESEARCH_STATE.md
git add -f research/q2_stability/qwen/outputs/paper1_5/phase1_final_integrity.json
git add -u research/q2_stability/qwen/outputs/paper1_5
git diff --cached --name-only | grep '\.pt$' && echo "STOP: activation shards staged"
git commit -m "[paper1.5] final trickster phase1 outputs integrity"
git push myfork master
```

5. Terminate via RunPod API or dashboard, not from inside the container.

Preferred API path:

```bash
export RUNPOD_API_KEY="$(cat ~/.runpod_api_key)"
runpodctl pod list -o json
```

Identify the pod by ID, name, endpoint, or port. Then use the current `runpodctl pod` subcommand for termination/removal. Always check `runpodctl pod --help` because command names can change between CLI versions.

6. Confirm termination through two independent signals:

```bash
RUNPOD_API_KEY="$(cat ~/.runpod_api_key)" runpodctl pod list -o json
```

Expected result when no pods are running:

```json
[]
```

Then confirm SSH refusal:

```bash
ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=6 \
  -p "$PORT" -i ~/.ssh/id_ed25519 root@"$POD_IP" 'echo STILL_REACHABLE' \
  || echo SSH_REFUSED_OR_UNREACHABLE
```

## What is currently missing from the workflow

- A guaranteed RunPod API key bootstrap step in every pod card. Add this before the run starts:

```bash
ls -la ~/.runpod_api_key
export RUNPOD_API_KEY="$(cat ~/.runpod_api_key)"
runpodctl pod list -o json
```

- A saved pod identity file for each run. Every pod session should write a local file such as:

```text
research/q2_stability/qwen/outputs/paper1_5/pod_identity.json
```

with pod ID, pod name, IP, SSH port, GPU type, hourly rate, launch time, and expected termination policy.

- A standard finalization script. Future runs should have a single local command that:
  - Copies final pod outputs.
  - Runs integrity checks.
  - Writes final integrity JSON/Markdown.
  - Commits safe artifacts.
  - Confirms no `.pt` shards are staged.
  - Terminates the pod through RunPod API.
  - Verifies API list and SSH refusal.

- A dashboard fallback that does not depend on Computer Use. Computer Use and Chrome automation may be unavailable or timed out; the API path should be treated as the primary termination mechanism.

- A stronger on-pod completion sentinel. Long runs should write `DONE`, `FAILED`, and `FINAL_INTEGRITY_READY` sentinel files so termination decisions do not require reconstructing state from logs.

- A heartbeat/status JSON updated during the run with total records, activation shard count, last pair, ETA, GPU memory, truncation count, think-artifact count, and final completion marker.

## Recommended card language for future runs

Use this exact termination block in future pod cards:

```text
Before termination:
1. Copy final outputs from pod to Mac Mini.
2. Run final local integrity checks.
3. Commit/push safe artifacts only; do not commit activation .pt shards.
4. Confirm ~/.runpod_api_key exists.
5. Export RUNPOD_API_KEY and terminate the pod via runpodctl or RunPod API/dashboard.
6. Confirm runpodctl pod list no longer shows the pod.
7. Confirm SSH to the previous endpoint refuses connection.
8. Only then report "Pod terminated."

Do not treat in-container kill/poweroff commands as pod termination.
Do not treat one transient SSH refusal as sufficient confirmation.
```
