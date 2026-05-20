# Llama 3.3 70B Access Pending

Date: 2026-05-20
Status: Gated repo access request submitted to Meta via HuggingFace
under account j-chamberlain. Access not yet approved as of this session.

To verify when approved, run on Mac Mini:
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

Once confirmed, run the Llama pilot using the same 12-emotion x 15-story
design at layer 79 (outer) with layer 40 as fallback.
Reference: codex_emotion_extraction_full_sequence.html for full card.
