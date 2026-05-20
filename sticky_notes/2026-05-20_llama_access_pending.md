# Llama 3.3 70B Access Confirmed and Pilot Run

Date: 2026-05-20
Status: Gated repo access was approved under account j-chamberlain.
The Llama pilot was run on RunPod using a single A100 SXM 80GB pod
with 300GB container disk.

Original intended bf16 loading did not fit cleanly on a single 80GB
GPU. The model offloaded too much to CPU and became impractically slow
before completing the first extraction step. The completed pilot
therefore used 8-bit loading with explicit FP32 CPU offload:
`load_mode = 8bit_with_fp32_cpu_offload`.

Pilot design:
  - Model: meta-llama/Llama-3.3-70B-Instruct
  - Emotions: 12-emotion pilot set using `scared` rather than `fearful`
  - Stories per emotion: 15
  - Layers: 79 and 40

Results:
  - Layer 79: LOW, PC1 = 7.52%, PC2 = 5.31%, 4/4 opposite-valence
    pairs anticorrelated
  - Layer 40: LOW, PC1 = 8.15%, PC2 = 5.53%, 4/4 opposite-valence
    pairs anticorrelated
  - Stronger signal: layer 40

Interpretation: Llama matches the Qwen pattern qualitatively: the PCA
gate fails because PC1 explains only about 8% of variance, but all
opposite-valence pairs remain anticorrelated. This suggests semantic
emotion opposition is present, while the Anthropic-style dominant PCA
structure does not replicate in this pilot setup.

Historical access check command:
  python -c "
from huggingface_hub import hf_hub_download
import os
hf_hub_download(
    repo_id='meta-llama/Llama-3.3-70B-Instruct',
    filename='config.json',
    token=open(os.path.expanduser('~/.hf_token')).read().strip()
)
print('Llama access confirmed')
"
