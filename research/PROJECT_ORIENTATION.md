# Project Orientation

This file is the first compact orientation layer for new GPT, Claude, and Codex sessions after `research/RESEARCH_STATE.md`. It is not a replacement for the canonical state file. It is a map of what matters now, where the evidence lives, and what a new agent should read before acting.

## Project Purpose

This repo supports a mechanistic interpretability research program centered on persona geometry in language models. The core question is whether models contain stable representational directions or basins corresponding to assistant-like behavior, role archetypes, motivational structures, and local persona-manifold structure. The work builds from Lu et al. (2026), "The Assistant Axis," and extends it into Paper 1.5 layered geometry interpretation, Paper 2 local centroid perturbation, and later work on confidence, archetype selection, dyadic dynamics, and rumination.

## Current Paper Sequence

Paper 1 is complete and establishes the Gemma 2 27B seven-cluster persona taxonomy and careful-evaluator assistant-axis finding.

Paper 1.5 is active. It is now framed as **Interpreting Persona Activation Geometry**. Its main claim is that persona activation geometry decomposes into layered semantic, dispositional, procedural, lexical/register, and residual structures after methodological stress testing. Adaptive extraction remains part of the due-diligence and tooling story, not the paper's headline contribution.

Paper 2 is now framed around local centroid perturbation and local persona-manifold mapping. The next compute-intensive program should map neighborhoods around selected anchors such as Trickster, Actor, Therapist, and Spy, testing whether local directions transfer across anchors. Earlier dyad contagion, attractor-collapse, conversational drift, and rumination plans are archived as future dynamics work rather than deleted.

Paper 3, Paper 3.5, and Paper 4 are pre-analysis. Paper 3 concerns a geometric confidence vector. Paper 3.5 concerns archetype self-selection. Paper 4 concerns computational rumination and depends on the earlier Paper 1.5/Paper 2 sequence.

## Current Canonical State Files

Read these before making research claims or generating Codex cards:

- `research/RESEARCH_STATE.md`: canonical current state, discoveries, next steps, pod status, and last session updates.
- `research/PROJECT_ORIENTATION.md`: this compact orientation file.
- `research/FINDINGS_LEDGER.md`: compact index of confirmed findings, negative findings, provisional interpretations, deviations, blockers, and next tests.
- `research/NEW_SESSION_STARTUP.md`: exact startup sequence for future agents.
- `research/paper1_5_outline.md`: current Paper 1.5 outline and methodology.
- `research/paper1_5_executive_summary.md`: concise current Paper 1.5 scope and contribution.
- `research/paper1_5_adaptive_extraction_notes.md`: operational adaptive-extraction workflow note.
- `research/paper2_local_centroid_perturbation_brief.md`: current Paper 2 scope and grant-relevant local-manifold plan.
- `research/assistant_axis_methodology/`: canonical Lu et al. methodology extraction package.
- `research/workflow/`: pod lifecycle, run registry, status artifact specs, execution tiers, and run checklists.
- `sticky_notes/README.md`: index of sticky notes and pre-analysis hypotheses.

## Current Validated Findings

The careful-evaluator finding is confirmed in Paper 1. In Gemma 2 27B, the assistant axis is dominated by evaluative roles such as proofreader, screener, grader, and editor, with conscientiousness strongly aligned and psychopathy strongly anti-aligned.

The base-model basin finding is confirmed. A careful-evaluator basin appears in Gemma 2 27B base model behavior, so the geometry is not only a post-training artifact.

Qwen/Qwen3-32B trickster adaptive extraction is validated operationally. Phase 1 produced 1200 preserved rollouts and 1200 activation shards. Codex GPT-5.5 Standard scoring reached 64 score>=2 responses and 33 score==3 responses in 64 scored records. The score>=2 vector matched the Lu trickster reference mean at cosine 0.957557, and adaptive stopping passed at n=16 for score>=2 and score==3 subsets.

The workflow lessons from the overnight trickster run are validated operationally. Detached pod execution, JSONL response records, activation-shard preservation, local integrity checks, explicit status artifacts, and API or `runpodctl` termination are now canonical workflow requirements.

## Current Negative and Provisional Findings

Gemma 2 27B emotion-vector extraction using the Sofroniew/Anthropic framing failed the PCA gate, though later cross-model emotion work suggests distributed emotion structure can still be usable.

Editor adaptive extraction did not replicate trickster's high-yield behavior. The first 128-record editor chunk produced only 10 score>=2 and 3 score==3 responses, below validation thresholds. The matched 1024-token sensitivity run sharply reduced truncation but did not improve role-expression yield, so token cap alone does not explain editor weakness.

The current interpretation is that assistant-adjacent personas may collapse toward generic assistant behavior under the current Lu-style extraction setup. That interpretation is plausible but not final. The next editor step should be revised anchoring design, not blind additional rollout generation.

Codex GPT-5.5 Standard scoring is a pragmatic substitute, not strict Lu-method judge replication. Strict Lu-method identity requires the `gpt-4.1-mini` scoring path and any paper-specific filtering choices to be restored and documented.

## Current Workflow Canon

Chat threads are planning interfaces, not operational source of truth. Runs need machine-readable status artifacts and local preserved outputs.

Pod jobs must run detached, preserve JSONL records and activation shards separately, write manifests and logs, pass local integrity before termination, and terminate through RunPod API or `runpodctl` when possible. Browser termination is fallback only.

Do not commit activation shards, secrets, duplicate model weights, or unrelated dirty files. Commit safe scripts, JSONL records, manifests, logs, integrity summaries, scoring summaries, validation summaries, and documentation.

## Current Empirical Frontier

The immediate Paper 1.5 methodology frontier is evaluator-model sensitivity, which remains unresolved. The immediate Paper 2 and grant frontier is local centroid perturbation around selected anchors. Revised editor anchoring remains useful, but Editor is not the preferred first local-manifold anchor because the first extraction test collapsed toward generic assistant behavior.

H100 local-manifold work is future/grant work, not a prerequisite for Paper 1.5. Paper 1.5 can proceed as a global geometry interpretation paper using the existing semantic, trait, procedural, lexical/register, and residual analyses.

## Methodology and Workflow Locations

Lu et al. methodology lives in:

- `research/assistant_axis_methodology/assistant_axis_pipeline_reconstruction.md`
- `research/assistant_axis_methodology/replication_differences_vs_lu.md`
- `research/assistant_axis_methodology/open_methodology_questions.md`
- `research/assistant_axis_methodology/prompts_and_questions/`

Adaptive extraction findings live in:

- `research/paper1_5_adaptive_extraction_notes.md`
- `research/paper1_5_outline.md`
- `research/q2_stability/qwen/outputs/paper1_5/`

Pod workflow rules live in:

- `research/workflow/`

Sticky notes live in:

- `sticky_notes/README.md`
- `sticky_notes/*.md`

## What Not to Rely On From Memory

Do not rely on chat memory for current empirical state, pod status, score counts, validation status, file paths, or methodology details. Fetch or read the repo files. Do not assume a pod is stopped unless `runpodctl` or the relevant provider API confirms it. Do not assume a score file exists from discussion alone. Do not assume Lu-method identity when a Codex judge or adaptive stopping path was used.

## Recommended Startup Sequence

1. Fetch or read `research/RESEARCH_STATE.md`.
2. Read `research/PROJECT_ORIENTATION.md`.
3. For methodology questions, read `research/assistant_axis_methodology/assistant_axis_pipeline_reconstruction.md` and `research/assistant_axis_methodology/replication_differences_vs_lu.md`.
4. For Paper 1.5 questions, read `research/paper1_5_outline.md`, `research/paper1_5_executive_summary.md`, and `research/paper1_5_adaptive_extraction_notes.md`.
5. For Paper 2 questions, read `research/paper2_local_centroid_perturbation_brief.md`; treat dyad/contagion files as archived prior framing unless the user explicitly asks about conversational dynamics.
6. For pod or execution questions, read `research/workflow/`.
7. Check `research/FINDINGS_LEDGER.md` for compact claim status.
8. Check `sticky_notes/README.md` if the task touches open hypotheses or write-up ideas.
