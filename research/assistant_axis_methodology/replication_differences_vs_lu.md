# Replication Differences vs Lu et al.

This document is the canonical local answer to: where does our methodology differ from Lu et al.?

## Baseline Lu-Style Methodology

Lu et al. generate five system prompts per role and 240 extraction questions, yielding 1200 possible rollouts per role. They score role expression with `gpt-4.1-mini`, separate fully role-playing and somewhat role-playing responses, extract mean post-MLP residual activations over response tokens, and construct vectors from qualified responses. The Assistant Axis is the mean default Assistant vector minus the mean role vector.

## Local Replication and Extension Workflow

Our Paper 1.5 workflow preserves the Lu-style prompt/question grid and Qwen/Qwen3-32B activation convention, but changes execution and validation in several practical ways. Runs are chunked, detached, and preserved as JSONL response records plus individual `.pt` activation shards. Integrity checks validate record counts, unique `(sp_idx, q_idx)` pairs, tensor shapes, missing activations, empty responses, think artifacts, and truncation before scoring or termination.

## Judge Differences

The strict Lu judge is `gpt-4.1-mini`. During trickster validation, API quota blocked that path, so Codex GPT-5.5 Standard was used as a pragmatic local role-expression judge. Editor scoring also used Codex GPT-5.5 Standard. This is explicitly a methodological deviation and should not be described as strict Lu-method judge replication.

## Adaptive Stopping

Lu-style extraction begins from the fixed 5x240 rollout design and the downloaded HF artifacts expose a fixed 64-row tensor convention. Our validated trickster workflow uses adaptive stopping after score-conditioned vector convergence. Trickster reached 64 score>=2 responses and 33 score==3 responses in 64 scored records, with adaptive stopping passing at n=16 for both score>=2 and score==3 subsets. Until broader validation is complete, 64 qualifying responses remains the conservative target.

## Rollout Count Reduction

The trickster run generated all 1200 Phase 1 rollouts before scoring, but the operational lesson is that future high-yield personas may not need exhaustive generation if adaptive scoring and convergence checks pass. The editor run intentionally tested a reduced first chunk of 128 rollouts plus a matched token-cap sensitivity set rather than generating all 1200 upfront.

## Token Cap and Truncation Handling

The Lu-style local generation default is 512 max tokens. Trickster produced 733/1200 truncated responses at 512 tokens, but pre-scoring geometry and Codex-scored vector validation remained stable. Editor token-cap sensitivity regenerated the first 64 pairs at 1024 tokens. Truncation dropped from 50/64 to 5/64, but score>=2 and score==3 counts did not improve, indicating token cap alone did not explain editor's weak role-expression yield. Truncation is retained as an explicit covariate rather than silently discarded.

## Local Scoring and Human-Inspectable Artifacts

Our scoring harnesses write JSONL score records, summary JSON, and Markdown reports. They are designed for local Codex rubric scoring and do not require OpenAI API credentials. This improves continuity and auditability but differs from the automated `gpt-4.1-mini` judge path in `pipeline/3_judge.py`.

## Detached Pod Execution and Preservation

Lu et al. do not describe the operational pod lifecycle in the paper. Our workflow now requires detached/nohup execution, local preservation before termination, explicit integrity artifacts, and RunPod API or `runpodctl` termination as the preferred closeout path. Chat threads are not treated as the operational source of truth.

## Role Prompt Differences

Current replication uses the local Lu et al. role instruction files under `data/roles/instructions/`. No evidence was found locally for alternate prompt regeneration during Paper 1.5 trickster/editor extraction. However, the exact Claude Sonnet 4 meta-prompt that originally generated the role list, role instructions, and extraction questions is not present locally.

## Geometry Differences Observed

Trickster is high-yield and geometrically recoverable under the adaptive workflow: score>=2 vector cosine to the Lu Qwen trickster mean is 0.957557. Editor is low-yield under the first chunk: 10 score>=2 and 3 score==3 out of 128 at 512 tokens, with no improvement in matched 1024-token role-expression yield. This supports the hypothesis that assistant-adjacent personas may collapse toward generic assistant behavior under the current extraction setup.

## Claim Boundaries

It is valid to say that the local workflow provides an operationally validated adaptive extraction path for trickster and a failed/diagnostic second-persona test for editor. It is not valid to claim strict Lu-method replication unless `gpt-4.1-mini` judge scoring and any other paper-specific filter choices are restored and documented.
