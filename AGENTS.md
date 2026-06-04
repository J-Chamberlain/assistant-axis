# Agent Instructions — assistant-axis

## Repo
/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis

Always confirm you are in this directory at the start of every session:
  pwd
  git remote -v
Expected remote: https://github.com/J-Chamberlain/assistant-axis

## Push protocol
After every meaningful unit of work, commit and push to GitHub.
A meaningful unit is: a script written, a script run with results,
a file updated, or a finding documented.

Commit message format:
  [scope] brief description of what was done

Examples:
  [q1] add centered cosine diagnostic script
  [notes] document axis sign flip and mean-centering findings
  [q2] add steering hook scaffold

## Token limit handoff
If approaching context limit before a task is complete:
1. Commit and push everything in progress, even if incomplete
2. Write HANDOFF.md in the repo root with:
   - What was being worked on
   - What was completed
   - Exact next step to resume
   - Any open questions or blockers
3. Commit and push HANDOFF.md
4. Inform the user that a handoff note has been pushed

## Sticky notes protocol
At the start of every session, read sticky_notes/README.md.
This gives you the full inventory of open research questions,
write-up reminders, and flagged findings.

During a session, if any work addresses or modifies a sticky note:
- Append a dated update section to that specific note file
- Do not edit the original content — only append
- Format: ## Update YYYY-MM-DD followed by the update text

At the end of every session, report back to the user:
- Which sticky notes were updated (if any)
- A one-line summary of what changed in each

If a sticky note has been fully addressed by completed research:
- Append: ## Addressed YYYY-MM-DD — [commit hash or description]
- Update the STATUS field in sticky_notes/README.md to "addressed"

CANONICAL REGISTRY CHECK
Do not rely on research/findings_log.md as the primary project
record. It is legacy unless a task explicitly asks for it.

Use the canonical registries instead:
- research/FINDINGS_LEDGER.md for findings, negative results,
  interpretation updates, methodology constraints, and compact
  result summaries
- research/CLAIMS_REGISTER.md for claim-relevant evidence and
  changes to claim status or wording
- research/PROVENANCE_REGISTRY.md for artifact lineage, source
  inputs, generation scripts, model/API usage, dependent analyses,
  and caveats

If a task creates a new finding, interpretation, negative result,
methodology constraint, or claim-relevant evidence, update the
appropriate canonical registry before committing.

## RunPod specs
Account: josiah.chamberlain@gmail.com
HuggingFace account: j-chamberlain
HuggingFace token name: mini-research-2

GPU selection order:
1. A100 SXM 80GB on-demand (~$1.49/hr)
2. A100 PCIe 80GB on-demand
3. H100 PCIe 80GB (only if under $2.50/hr)
4. A100 SXM 80GB community cloud
5. 2x A40 48GB (last resort)

Never select: spot instances, GPU under 80GB VRAM,
any pod over $2.50/hr without explicit user confirmation.

Disk requirements:
- Gemma 2 27B: 200GB minimum container disk
- Qwen 3 32B: 150GB minimum container disk
- Both models sequentially: 300GB minimum

Always use /root, never /workspace (/workspace hangs on large downloads).

Always terminate pod when done. Never leave running without intent.
Always confirm termination with user before terminating.

## Session startup on RunPod
  tmux new -s main
  git clone https://github.com/J-Chamberlain/assistant-axis.git
  cd assistant-axis
  pip install transformers accelerate datasets huggingface_hub torch --quiet
  hf auth login   # paste mini-research-2 token when prompted

## Reporting format

The user supervises from an iPhone. All responses must be
phone-readable and copy-ready. Follow these rules on every task:

SUMMARY FIRST
End every task with a plain-text paragraph (3-5 sentences,
no bullet points, no markdown headers) summarizing what was
done and what the key outcome was. This is the first thing
the user reads. Keep it scannable on a small screen.

NEVER PASTE LARGE OUTPUTS INTO CHAT
If results include tables, CSVs, long file contents, or
terminal output longer than 10 lines: save to a file in
the repo, push it, and report the raw GitHub URL only.
Format: "Results saved to: [raw GitHub URL]"

CONFIRMATION REQUESTS
If you need the user to confirm something before proceeding,
end your message with exactly this format and nothing after it:

WAITING FOR CONFIRMATION:
[single specific question]

No additional text after the confirmation request.

RESEARCH_STATE UPDATE
Before committing, update research/RESEARCH_STATE.md Section 3 (Current State) with:
- What was completed this session (one sentence per task)
- Next step
- Last commit hash
If any new empirical findings were produced, append them to Section 2 with date and key statistic.

If the task significantly changes active objectives, top findings,
top open questions, current interpretations, current risks, or next
experiments, also update research/THREAD_START.md before committing.

REPO NAVIGATION UPDATE
If this task creates, deletes, moves, renames, replaces, supersedes,
archives, deprecates, or materially revises a research artifact,
update:
- research/REPO_NAVIGATION.md
- research/REPO_FILE_INDEX.csv
- research/RAW_URL_INDEX.md
Record the update timestamp and commit. Assign or update artifact
status using one of:
- canonical
- active
- archive
- deprecated

This navigation update requirement includes material revisions to
instructions, reports, notebooks, visualizations, scripts, data
tables, and registry/index files.

STICKY NOTES REPORT
At the very end of every response, after the summary,
report sticky notes changes in this exact format:

STICKY NOTES:
- Updated: [filename] — [one line description]
- Added: [filename] — [one line description]
- No changes (if nothing was updated)

COMMIT CONFIRMATIONS
When confirming a push, always include:
- Commit hash
- Branch
- One-line description of what changed
Format: "Pushed [hash] to master: [description]"

CODEX FINAL REPORT REQUIREMENTS
For every meaningful unit of work, the final report must include:
- commit hash
- branch
- files changed
- raw GitHub URLs for new or modified canonical artifacts
- registries updated
- navigation files updated
- one-sentence statement of impact on project state

## Model specification for Codex analytical work

When Codex is asked to perform analytical reasoning, synthesis,
qualitative evaluation, or any task involving its own language model
capabilities (as opposed to running bash commands or editing files),
the correct model is GPT-5.5.

All output files that record a model_used field must reflect the actual
model: GPT-5.5.

Cards generated by Claude that ask Codex to perform synthesis or
analysis should specify: "You are running as GPT-5.5. Record this
in any model_used field in output files."

This note was added 2026-05-24 after
cluster_background_prompts_v1.json was incorrectly tagged as GPT-4.5
due to a placeholder string in the generating card.

## Zero-Relay Workflow — Session Startup Check

At the start of every Codex session, before doing anything else:

1. Check if /tmp/codex_pending.txt exists and is non-empty.
2. If yes: read it, treat its contents as the task for this session, delete the file, and proceed with execution.
3. After completing the task, write a summary to research/runtime/CURRENT_RESULTS.md and clear research/runtime/PENDING_TASK.md (replace contents with the empty-state header comment only).
4. Push both files to master.
5. If /tmp/codex_pending.txt is absent or empty: proceed with the user's verbal instructions as normal.

This check is mandatory on every session start. It is the activation mechanism for the zero-relay workflow.
