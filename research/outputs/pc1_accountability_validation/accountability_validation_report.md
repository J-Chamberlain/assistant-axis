# PC1 Accountability Validation Report

model_used: GPT-5.5

## Startup Status

Startup verification was performed before this run in the coordinating Codex session using the canonical raw startup files listed in `research/STARTUP_MANIFEST.md`.

## Measurement Protocol

- Model: Qwen/Qwen3-32B
- Layer: 48
- Activation source: direct forward hook on `model.model.layers[48]`
- Pooling: mean over generated assistant response tokens only
- PCA basis: same reconstructed Qwen persona PCA basis and sign alignment as Run 2
- Conversation protocol: one fresh user message per sample, no system prompt, no prior history
- Extraction pass: separate no-cache forward pass over the generated sequence
- Model-visible text: prompt text only; prompt IDs, experiment labels, pair labels, PC labels, hypotheses, and metadata were not visible to Qwen

## Run Integrity

- Planned generations: 200
- Successful generations: 200
- Error count: 0

## Experiment A: Accountability vs Determination

| pair | B-A PC1 | 95% CI | pass | B-A PC2 | secondary negative PC2 |
|---|---:|---:|---|---:|---|
| A1 | 3.663 | [1.743, 5.555] | True | -8.914 | True |
| A2 | 2.686 | [1.040, 5.005] | True | -7.865 | True |
| A3 | 6.526 | [4.605, 8.276] | True | -9.811 | True |
| A4 | 1.998 | [0.226, 3.581] | True | -8.929 | True |
| A5 | 1.611 | [0.077, 3.202] | True | -7.805 | True |

Mean B-A PC1 effect across pairs: 3.297 with 95% CI [1.574, 5.020]. Positive pairs: 5/5.
Mean B-A PC2 effect across pairs: -8.665; negative-PC2 pairs: 5/5.

## Experiment B: Accountability vs Arithmetic/Checking

| pair | B-A PC1 | 95% CI | pass | B-A PC2 | secondary negative PC2 |
|---|---:|---:|---|---:|---|
| B1 | 12.228 | [10.663, 13.721] | True | -19.398 | True |
| B2 | 6.822 | [5.239, 8.515] | True | -14.318 | True |
| B3 | 11.269 | [10.106, 12.399] | True | -13.363 | True |
| B4 | 8.003 | [6.276, 9.711] | True | -15.627 | True |
| B5 | 9.434 | [8.320, 10.605] | True | -17.543 | True |

Mean B-A PC1 effect across pairs: 9.551 with 95% CI [7.592, 11.510]. Positive pairs: 5/5.
Mean B-A PC2 effect across pairs: -16.050; negative-PC2 pairs: 5/5.

## Prompt Means

See `prompt_means.csv` for per-version PC1/PC2/PC3 means and deltas relative to both the Run 2 bare-Qwen baseline and the released assistant-role centroid.

## Interpretation Constraints

This is a focused diagnostic, not Run 3. It tests whether accountability/scrutiny wording produces larger positive PC1 movement than determination or arithmetic/checking wording under matched scenarios. It does not by itself prove PC1 semantics, and it reuses the Run 2 baseline rather than regenerating it.

