# Findings Ledger

This is a compact index of project claims and their status. Use `research/RESEARCH_STATE.md` for full history and exact supporting paths.

## Confirmed Findings

### Careful Evaluator Finding

Gemma 2 27B's assistant axis is dominated by evaluative roles, especially proofreader, screener, grader, and editor. `assistant` ranks 45th out of 275 on the assistant axis, and the top pole correlates strongly with conscientiousness and negatively with psychopathy.

### Base Model Basin Finding

The careful-evaluator basin appears in Gemma 2 27B base model behavior, not only in instruction-tuned behavior. This supports the interpretation that the geometry reflects pretraining distribution structure as well as post-training.

### Qwen/Llama Convergence and Gemma Divergence

Qwen 3 32B and Llama 3.3 70B converge strongly on persona rankings, while Gemma diverges. This matters for any claim that transfers cluster representatives from Gemma into Qwen without Qwen-native validation.

### Trickster Adaptive Extraction Success

Qwen/Qwen3-32B trickster Phase 1 completed 1200 rollouts and 1200 activation shards with final integrity passed. Codex GPT-5.5 Standard adaptive scoring reached 64 score>=2 and 33 score==3 responses in 64 scored records. The score>=2 vector matched the Lu trickster reference mean at cosine 0.957557, and adaptive stopping passed at n=16 for both score>=2 and score==3 subsets.

### Pod Workflow Lessons

Detached execution, response JSONL preservation, separate activation shards, local integrity checks, explicit run artifacts, and RunPod API or `runpodctl` termination are now validated workflow requirements. Browser/dashboard termination is fallback only.

## Negative Findings

### Gemma Emotion PCA Gate Failure

Gemma 2 27B failed the Anthropic/Sofroniew emotion-vector PCA gate at tested layers. This is a negative result for dominant-PC emotion geometry in Gemma at this scale, though distributed emotion structure remains a separate possibility.

### Editor Adaptive Extraction Failure

The first Qwen editor adaptive extraction chunk did not meet validation thresholds. The 128-record 512-token run produced only 10 score>=2 and 3 score==3 responses, so vector validation and sample sufficiency were correctly not run.

### Token-Cap Sensitivity Result for Editor

The matched first-64 editor rerun at 1024 tokens reduced truncation from 50/64 to 5/64, but score>=2 and score==3 counts did not improve. Token cap alone does not explain editor's low role-expression yield.

### Forced Manual Cap Pilot Failure

The forced manual cap pilot froze geometry despite zero leakage, with post-T3 trickster cosine variance at 0.00e+00. It should not be treated as a valid stabilizing result.

## Provisional Interpretations

### Assistant-Adjacent Collapse

Editor weakness may reflect collapse toward generic assistant behavior for assistant-adjacent personas under the current Lu-style extraction setup. This is plausible but still provisional because only one editor chunk and one matched token-cap follow-up have been tested.

### Adaptive Extraction Generality

Adaptive extraction is operationally validated for trickster but not yet generally validated across persona types. It should be treated as a workflow candidate pending additional high-yield, mid-yield, and assistant-adjacent persona tests.

### Cluster Motivational Structure

Six of seven clusters have dialogue-derived motivational characterizations. These are useful for hypothesis generation and Paper 1.5 framing, but empirical verification remains pending.

## Methodological Deviations

### Codex GPT-5.5 Judge Substitution

The Lu et al. path uses `gpt-4.1-mini` as the role-expression judge. Current trickster and editor adaptive scoring used Codex GPT-5.5 Standard as a pragmatic substitute. This must be disclosed and should not be described as strict Lu-method replication.

### Adaptive Stopping

The project now uses an adaptive extraction protocol for operational efficiency. The provisional rule is 64 qualifying responses as a conservative target, with adaptive stopping permitted once convergence criteria pass at n>=16. This is a methodological extension beyond the fixed Lu-style rollout framing.

### Chunked Generation

Editor was tested with a 128-rollout chunk rather than a full 1200-rollout run. This was intentional for the second-persona generalization test and should not be conflated with exhaustive Lu-style extraction.

### Truncation as Covariate

High truncation is tracked explicitly rather than silently filtered. Trickster truncation did not materially destabilize geometry; editor token-cap results suggest truncation reduction does not necessarily improve role-expression yield.

## Current Blockers

The next editor experiment is blocked on revised anchoring methodology. More identical editor rollouts are unlikely to answer the failure mode cleanly.

Strict Lu-method replication remains blocked unless `gpt-4.1-mini` judge scoring is restored and run with documented filter choices.

Downloaded Lu vector metadata remains underspecified locally: the exact fully-roleplaying versus somewhat-roleplaying storage category and fixed 64-row selection procedure are not documented in local HF metadata.

## Next Empirical Tests

1. Design a revised editor anchoring methodology that can test assistant-adjacent role extraction without immediate collapse into generic assistant behavior.
2. Run at least one additional non-trickster persona adaptive extraction after the revised methodology is specified.
3. Restore or compare `gpt-4.1-mini` scoring if API access permits, to estimate judge sensitivity relative to Codex GPT-5.5 Standard.
4. Test whether cluster-synthesized background prompts improve low-yield persona anchoring without leaking role identity.
5. Continue Paper 1.5 validation before relying on adaptive extraction as a general persona-vector workflow.
