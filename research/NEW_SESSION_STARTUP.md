# New Session Startup

Use this sequence for new GPT, Claude, and Codex sessions. Do not rely on chat memory for empirical state.

## Required Startup Sequence

1. Fetch or read `research/RESEARCH_STATE.md`.
2. Read `research/PROJECT_ORIENTATION.md`.
3. If the question is about Lu et al. methodology, read the `research/assistant_axis_methodology/` package, especially:
   - `research/assistant_axis_methodology/assistant_axis_pipeline_reconstruction.md`
   - `research/assistant_axis_methodology/replication_differences_vs_lu.md`
   - `research/assistant_axis_methodology/open_methodology_questions.md`
4. If the question is about workflow, pods, RunPod lifecycle, preservation, integrity, scoring, or closeout, read `research/workflow/`.
5. If the question is about Paper 1.5, read:
   - `research/paper1_5_outline.md`
   - `research/paper1_5_adaptive_extraction_notes.md`
   - `research/FINDINGS_LEDGER.md`
6. If the question touches open hypotheses, write-up reminders, or parked ideas, check `sticky_notes/README.md`.
7. Ask for Codex only when repo execution, file inspection, script writing, local validation, git commits, pod work, or browser/computer use is needed.

## Operating Rules

Do not assume the current state from a prior chat thread. Check files.

Do not assume a pod is stopped, idle, or preserved unless run artifacts and provider status confirm it.

Do not assume a score file or validation file exists because a plan mentioned it. Check the filesystem.

Do not describe Codex GPT-5.5 scoring as strict Lu-method replication. It is a pragmatic substitute unless `gpt-4.1-mini` scoring has actually been run.

Do not launch pod work without reading the workflow package and confirming preservation, integrity, termination, and git-safety requirements.

Do not generate new research claims from memory. Trace claims to `RESEARCH_STATE.md`, `FINDINGS_LEDGER.md`, a paper draft, or a local output artifact.
