# Live pod status check — 2026-05-26

Pod: `213.173.102.6:22707`

## Summary

- SSH succeeded: yes
- Process still running: yes, `python3 -u research/q2_stability/qwen/scripts/phase1_inference_only_v4.py` PID 5596
- Latest rollout count at check: 1180 JSONL lines out of 1200 expected
- Activation shard count at check: 1180 `.pt` files
- Output directory size at check: 39M
- Run classification: B. RUN STILL IN PROGRESS

## Latest log checkpoint

The latest visible checkpoint was `[new=1175 total=1175/1200] think_discards=0 truncated=710 rate=27.6s ETA=0.2hr GPU=65.5GB`. The direct file counts immediately after that checkpoint showed 1180 JSONL lines and 1180 activation shards.

## GPU state

`nvidia-smi` showed one active A100-SXM4-80GB process: PID 5596 using 64082 MiB, GPU utilization 88%, power 252W, temperature 43C. No OOM or GPU fault was visible.

## Disk state

Root overlay was 63G used / 88G available (42%). `/workspace` was 76% used on the network filesystem. `/dev/nvme2n1` was 55% used, and `/usr/bin/nvidia-smi` mount reported 3% use. No disk-pressure condition was visible.

## Interpretation

The run appeared healthy and near completion, not crashed. Because the one-time live check found 1180/1200 records rather than 1200/1200, final outputs were not copied in this card. The pod should remain alive until the user explicitly authorizes either a final copy/termination check or termination.
