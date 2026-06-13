# Run 2 No-Label Elicitation Validation Report

model_used: GPT-5.5

## 1. Motivation
Run 2 is designed to establish a bare-Qwen baseline over the 240 extraction questions and test revised no-label prompt manipulations against both the inherited assistant role centroid and the new bare-Qwen centroid.

## 2. Assistant Centroid Provenance Caveat
The current assistant centroid is the released role-conditioned `assistant` vector, not bare Qwen. Run 2 therefore treats the 240-question baseline as foundational rather than optional.

## 3. Bare-Qwen Baseline Design
The baseline uses all 240 canonical extraction questions with 5 samples each. No role prompt, persona prompt, assistant-role system prompt, experiment explanation, PC label, or metadata is included in model-visible input.

## 4. Full Run 2 Design
Catalog rows: 289. Planned generations: 1690. Component totals are recorded in `run2_experiment_manifest.json`.

## 5. Blinding Verification
Qwen-visible messages are one user message containing only `prompt_text`; for baseline rows this is only the extraction question. See `prompt_blinding_verification.md`.

## 6. Generation Independence Verification
Each sample is a fresh one-message conversation, no prior history or cross-sample KV cache is passed, and activation extraction is a separate no-cache forward pass. See `generation_independence_verification.md`.

## 7. Baseline Results
Execution did not start because this local environment has no configured RunPod API key and no local 80GB GPU. No baseline results are available yet.

## 8. PC1+ Replacement Results
Not run.

## 9. PC2- Replacement Results
Not run.

## 10. PC3 Minimal-Pair Results
Not run.

## 11. PC1 Minimal-Pair Results
Not run.

## 12. PC2 Minimal-Pair Results
Not run.

## 13. Off-Axis Findings
Not available until generation completes.

## 14. Interpretation
Observed: the Run 2 catalog and runner are archived, but generation is blocked before execution. Inferred: no evidential update should be made from Run 2 yet. Unknown: all Run 2 activation effects.

## 15. Limitations
This is a prepared-but-not-executed run package until `RUNPOD_API_KEY` is configured and an approved 80GB+ non-spot pod is launched.

## 16. Recommendation for Paper 1.5 Inclusion
Do not include Run 2 results in Paper 1.5 until the full 1690-generation run completes and integrity checks pass.
