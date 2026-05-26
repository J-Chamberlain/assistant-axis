DRAFT ONLY. DO NOT EXECUTE FROM THIS FILE WITHOUT USER CONFIRMATION.

**CODEX CARD:**
```
You are working in the assistant-axis repo on the Mac Mini.

RECOMMENDED CODEX SETTINGS
Model: GPT-5.5 Standard
Reason: RunPod launch, detached execution, preservation, integrity, and repo-safe operational follow-through.

GOAL
Launch the Qwen/Qwen3-32B editor adaptive extraction test as the second-persona generalization run for Paper 1.5. Run only the first 128 editor rollouts, preserve outputs locally, run integrity, update run-status artifacts, and stop before scoring unless explicitly instructed. Do not terminate the pod without user confirmation.

STARTUP CHECK
Run:
pwd && git remote -v
git status --short
git branch --show-current
git log -8 --oneline

Confirm repo path:
/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis

READ BEFORE LAUNCH
Read:
research/RESEARCH_STATE.md
research/paper1_5_adaptive_extraction_notes.md
research/q2_stability/qwen/outputs/paper1_5/editor_adaptive_run_plan.md
research/q2_stability/qwen/outputs/paper1_5/editor_script_adaptation_notes.md
research/workflow/pod_lifecycle_protocol.md
research/workflow/run_registry_spec.md
research/workflow/run_status_artifact_spec.md
research/workflow/examples/pod_launch_checklist.md
research/workflow/examples/pod_monitoring_checklist.md
research/workflow/examples/pod_closeout_checklist.md

VERIFY INPUTS
Confirm:
data/roles/instructions/editor.json exists and contains five positive instruction prompts.
downloads/hf_vectors/qwen-3-32b/role_vectors/editor.pt exists and loads as shape [64, 5120].
data/extraction_questions.jsonl exists and contains 240 extraction questions.

RUNPOD LAUNCH
Launch one RunPod instance:
- Preferred GPU: A100 SXM 80GB at or near $1.49/hr
- Acceptable GPU: A100 PCIe 80GB
- H100 PCIe only if under $2.50/hr
- Never use spot instances
- Minimum VRAM: 80GB

Record pod_id, ssh endpoint, GPU type, start time, and expected completion in a local run registry entry under:
research/q2_stability/qwen/outputs/paper1_5/editor_run_registry.json

POD SCRIPT REQUIREMENTS
Create or adapt editor-specific pod scripts from the trickster workflow. The Phase 1 inference script must:
- Use persona `editor`
- Use Qwen/Qwen3-32B
- Use layer 48
- Disable thinking with `enable_thinking=False` where supported
- Generate deterministically
- Use `use_cache=False` in the measurement forward pass
- Save full response_text
- Save one activation `.pt` shard per rollout
- Save JSONL records to `editor_phase1.jsonl`
- Save activation shards under `activations_editor/`
- Save a manifest to `editor_phase1_manifest.json`
- Reject or flag think artifacts
- Resume safely if interrupted
- Stop after 128 newly preserved editor rollouts unless explicitly instructed otherwise

Do not run judge scoring on the pod. Do not call OpenAI or any external scoring API from the pod.

DETACHED EXECUTION
Run the editor Phase 1 script detached with nohup, tmux, or screen. Save pod-side logs in the output directory. Confirm the process continues after disconnect.

STATUS ARTIFACTS
Emit or update these artifacts during the run where practical:
- manifest.json or editor_phase1_manifest.json
- heartbeat.json
- integrity.json after local preservation
- preservation.json after local copy

At minimum, preserve enough state to reconstruct: latest rollout count, latest heartbeat time, current status, pod_id, ssh endpoint, GPU type, output paths, and known errors.

LOCAL PRESERVATION
After the 128-rollout chunk completes, copy outputs from the pod to:
research/q2_stability/qwen/outputs/paper1_5/

Expected local outputs:
- editor_phase1.jsonl
- editor_phase1_manifest.json
- activations_editor/*.pt
- editor pod log file
- editor preservation/status artifacts

Do not commit activation `.pt` shards.

INTEGRITY CHECK
Run a local integrity check before scoring or termination. Verify:
- 128 JSONL records unless the run was explicitly resumed to a different target
- unique `(sp_idx, q_idx)` pairs
- all records have non-empty `response_text`
- all `activation_saved=True` records point to existing local activation shards
- all sampled or all activation tensors load as shape [5120]
- no literal think tags are present
- no `think_artifact=True` records unless explicitly reported

Save integrity output as:
research/q2_stability/qwen/outputs/paper1_5/editor_phase1_integrity.json
research/q2_stability/qwen/outputs/paper1_5/editor_phase1_integrity.md

STOP POINT
Stop after preservation and integrity. Do not score unless the user explicitly asks you to continue. Do not terminate the pod without explicit user confirmation. Report pod status and whether it is safe to terminate.

COMMIT
Commit safe artifacts only. Do not commit activation shards. Use:
git add research/q2_stability/qwen/outputs/paper1_5/editor_phase1.jsonl
git add research/q2_stability/qwen/outputs/paper1_5/editor_phase1_manifest.json
git add research/q2_stability/qwen/outputs/paper1_5/editor_phase1_integrity.json
git add research/q2_stability/qwen/outputs/paper1_5/editor_phase1_integrity.md
git add research/q2_stability/qwen/outputs/paper1_5/editor_run_registry.json
git commit -m "[paper1.5] run editor adaptive extraction phase1 chunk"
git push origin master

RESEARCH_STATE UPDATE
Before committing, update research/RESEARCH_STATE.md Section 3 (Current State) with:
- What was completed this session
- Next step
- Last commit hash
If empirical findings were produced, append them to Section 2 with date and key statistic.

STICKY NOTES CHECK
Before committing, read sticky_notes/README.md.
If any work this session addresses or modifies a sticky note,
append a dated update to that note file.

REPORT BACK using this exact format:
[3-5 sentence plain-text summary, no bullets, no headers]

Results saved to: [raw GitHub URL if any large outputs exist]

STICKY NOTES:
- Updated: [filename] - [one line] (or "No changes")

Pushed [hash] to master: [description]

## WAITING FOR CONFIRMATION:
Editor 128-rollout chunk is preserved and integrity-checked. Confirm whether to score locally, run another chunk, or terminate the pod.
```
