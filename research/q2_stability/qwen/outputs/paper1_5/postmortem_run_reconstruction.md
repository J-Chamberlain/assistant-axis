# Postmortem Run Reconstruction

Audit date: 2026-05-26

## research/q2_stability/qwen/outputs/calibration/calibration_run.log
- Size: 27623 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: YES
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/dyad_v1/dyad_run.log
- Size: 180355 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: YES
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/dyad_v2/dyad_v2_run.log
- Size: 42932 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: YES
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/dyad_v3/dyad_v3_run.log
- Size: 36915 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: YES
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/dyad_v4/dyad_v4_run.log
- Size: 114185 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: YES
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/dyad_v5/dyad_v5_run.log
- Size: 44977 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: YES
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/dyad_v6/dyad_v6_run.log
- Size: 2477 bytes
- Model load: log contains "Loading model".
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: no
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/dyad_v6/v6_stdout.log
- Size: 6309 bytes
- Model load: log contains "Loading model".
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: no
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/dyad_v6_forced_cap/dyad_v6_run.log
- Size: 3160 bytes
- Model load: log contains "Loading model".
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: no
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/paper1_5/phase1_v4.log
- Size: 6554 bytes
- Model load: log contains "Loading model".
- Model load time: 14.4s
- Latest checkpoint line: new=1125, total=1125/1200, think_discards=0, truncated=669, rate=27.5s, ETA=0.6hr, GPU=65.5GB
- Latest completed rollout count: 1125
- think_discards at latest checkpoint: 0
- truncation count at latest checkpoint: 669
- rate and ETA at latest checkpoint: 27.5s/rollout, 0.6hr
- GPU memory at latest checkpoint: 65.5GB
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: no
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/paper1_5/trickster_phase1.jsonl
- Size: 2797983 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: YES
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/paper1_5/trickster_phase1_manifest.json
- Size: 623 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: no
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/paper1_5/trickster_replication_pilot.partial.jsonl
- Size: 5775201 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: no
- Launch method evident: not evident from local log

## research/q2_stability/qwen/outputs/valence_matrix/run.log
- Size: 43168 bytes
- Model load time: not found
- Latest checkpoint line: not found
- Latest completed rollout count: not found
- Any Python traceback: no
- Any CUDA OOM: no
- Any SSH/tmux/nohup/pod/connection error: YES
- Launch method evident: not evident from local log

## Overall Reconstruction
- Local `phase1_v3.log` was not present before the reachability check; the active pod exposed `/root/phase1_v3.log` and was tailed over SSH.
- The live process at audit time was `python3 -u research/q2_stability/qwen/scripts/phase1_inference_only_v4.py`.
- The live log showed progress through at least total=1125/1200 at 27.5s/rollout, zero think discards, 669 truncations, and 65.5GB GPU memory.
- The run appears launched as a long-lived process; local logs do not prove nohup, but the process survived outside the current chat session.
