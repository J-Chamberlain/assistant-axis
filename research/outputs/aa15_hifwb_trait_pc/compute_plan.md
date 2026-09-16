# AA-15 prospective extraction compute plan · 2026-09-16

Status: **not launched**. No HiFWB indicator responses or activations have been
extracted, and no cloud compute has been charged by this task.

## Required run

- Use on-demand, non-spot RunPod resources only after an authenticated account
  is available. Never print or commit credentials. Confirm current price in the
  console before launch and stop immediately if the selected configuration
  exceeds the authorized hourly cap.
- Qwen3-32B and Gemma-2-27B-it: one A100 80 GB each, BF16, no CPU/disk
  offload. Llama-3.3-70B-Instruct: two A100 80 GB GPUs, BF16 model-sharded,
  no CPU/disk offload. The latter is above the user's $2.50/hour confirmation
  threshold and **must not be launched without explicit confirmation**.
- The official [RunPod GPU pricing page](https://www.runpod.io/pricing) listed
  A100 80 GB on-demand at $1.59/GPU-hour when checked 2026-09-16. Thus the
  anticipated GPU rate is $1.59/hour for the one-GPU runs and $3.18/hour for
  Llama's two-GPU run, before any storage/network charges. Assuming 2–5 hours
  each for Qwen/Gemma and 3–8 hours for Llama, rough GPU cost is $15.90–$41.34;
  allow approximately $20–$60 total including setup and storage. Serial
  generation of 9,360 responses makes this uncertain; pilot throughput must
  revise the estimate before full runs. This is a planning estimate, not a
  measured runtime or a commitment to spend.
- First run `extract_hifwb_vectors.py --pilot` on each model; verify the model
  revision, Qwen thinking-disabled formatting, assistant-token pooling, layer
  count, BF16 placement, and one paired contrast. Only then run the complete
  13×3×5×8×2 response protocol. Terminate GPU resources promptly after
  verifying all 39 item/formulation bundles for that model.
- Write private `.npz` extraction bundles **outside the repository**; transfer
  these to a secure analysis machine or run the CPU projection job on the
  compute host with the released AA-14 vector bank. Export only compact CSVs,
  verification, report, and safe visualization JSON. Do not copy response text,
  model weights, or raw activation tensors into Git or public Site assets.

## Local constraints and alternatives

The development Mac has 16 GB RAM and roughly 0.4 GB free disk at this check;
it cannot hold the three BF16 models or safely stage the entire private
extraction bank. A remote run should use a sufficiently large temporary volume
and verify available space before loading weights. The projection script accepts
`--source-vector-root` so the released AA-14 vectors can be staged on that host
without changing the frozen PCA files. If authenticated RunPod access or the
Llama hourly-rate confirmation is unavailable, stop before paid inference and
leave AA-14's viewer publicly available unchanged. Never substitute a
quantized Llama model and call it method-matched to AA-14.
