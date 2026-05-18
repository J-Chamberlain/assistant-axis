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
