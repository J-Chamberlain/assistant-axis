# Assistant Axis Methodology Artifact Inventory

Purpose: canonical inventory for local artifacts relevant to Lu et al. (2026), "The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models," arXiv 2601.10387, and this repo's Paper 1.5 replication work.

## Paper PDFs

| Path | Artifact type | Purpose | Canonical or derived | Source status |
|---|---|---|---|---|
| `/Users/alfred/Documents/ChatGPT_Project_References/mechanistic-interpretability/papers/anthropic-the-assistant-axis-situating-and-stabilizing-the-character-of-large-language-models-2026.pdf` | PDF | Lu et al. paper text | Canonical paper copy | External Lu et al. artifact |
| `/Users/alfred/Documents/ChatGPT_Project_References/mechanistic-interpretability/project-upload/anthropic-the-assistant-axis-situating-and-stabilizing-the-character-of-large-language-models-2026.pdf` | PDF | Lu et al. paper text | Canonical paper copy | External Lu et al. artifact |
| `/Users/alfred/Documents/ChatGPT_Project_References/mechanistic-interpretability/project-upload/missing-as-pdf/p04-assistant-axis.pdf` | PDF | Lu et al. paper text | Canonical paper copy | External Lu et al. artifact |

## Local Repositories and Code Roots

| Path | Artifact type | Purpose | Canonical or derived | Source status |
|---|---|---|---|---|
| `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis` | Git repo | Active assistant-axis research and replication repo | Working canonical repo for this project | Mixed: Lu et al. code/data plus local replication artifacts |
| `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/assistant_axis` | Python package | Generation, judging, activation extraction, PCA, steering helpers | Canonical local implementation | Lu et al. repo code |
| `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/pipeline` | Pipeline scripts | End-to-end Lu-style generation, activation extraction, judging, vectors, axis construction | Canonical local implementation | Lu et al. repo code |
| `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research` | Research outputs | Paper 1.5 and Q2 replication scripts, outputs, notes | Derived project artifacts | Local replication |

## Prompt and Question Artifacts

| Path | Artifact type | Purpose | Canonical or derived | Source status |
|---|---|---|---|---|
| `data/roles/role_list.json` | JSON | 275 role names and descriptions | Canonical role list | Lu et al. artifact |
| `data/roles/instructions/` | JSON directory | Five system prompts, role-specific questions, and judge prompt per role | Canonical prompt set | Lu et al. artifact |
| `data/roles/instructions/default.json` | JSON | Default Assistant baseline prompts | Canonical default prompt set | Lu et al. artifact |
| `data/extraction_questions.jsonl` | JSONL | 240 generic extraction questions | Canonical extraction question set | Lu et al. artifact |
| `data/traits/trait_list.json` | JSON | 240 trait names/descriptions | Canonical trait list | Lu et al. artifact |

## Vector and Geometry Artifacts

| Path | Artifact type | Purpose | Canonical or derived | Source status |
|---|---|---|---|---|
| `downloads/hf_vectors/gemma-2-27b/` | PT tensors | Gemma 2 27B role, trait, default, assistant-axis, and layer data | Canonical downloaded vectors | HuggingFace dataset `lu-christina/assistant-axis-vectors` |
| `downloads/hf_vectors/qwen-3-32b/` | PT tensors | Qwen 3 32B role, trait, default, assistant-axis, and capping config data | Canonical downloaded vectors | HuggingFace dataset `lu-christina/assistant-axis-vectors` |
| `downloads/hf_vectors/llama-3.3-70b/` | PT tensors | Llama 3.3 70B role, trait, default, assistant-axis, and capping config data | Canonical downloaded vectors | HuggingFace dataset `lu-christina/assistant-axis-vectors` |
| `visualizations/full_ranking.csv` | CSV | Gemma cluster/ranking table used by Paper 1 and later cluster analyses | Derived from local analyses | Local project artifact |
| `research/cluster_analysis/` | CSV/MD outputs | Cross-model cluster distance/directionality and other-cluster prompt compilation | Derived analyses | Local replication/extension |

## Pipeline and Methodology Scripts

| Path | Artifact type | Purpose | Canonical or derived | Source status |
|---|---|---|---|---|
| `pipeline/1_generate.py` | Python script | Generate role/default rollouts from prompt x question combinations | Canonical for its workflow | Lu et al. repo code |
| `pipeline/2_activations.py` | Python script | Extract post-MLP residual activations and save per-role tensors | Canonical for its workflow | Lu et al. repo code |
| `pipeline/3_judge.py` | Python script | Score role expression using role-specific eval prompts | Canonical for its workflow | Lu et al. repo code |
| `pipeline/4_vectors.py` | Python script | Build role/default vectors from scored activations | Canonical for its workflow | Lu et al. repo code |
| `pipeline/5_axis.py` | Python script | Compute Assistant Axis from default and role vectors | Canonical for its workflow | Lu et al. repo code |
| `assistant_axis/generation.py` | Python script | Model loading and chat-template generation, including Qwen thinking disable path | Canonical for its workflow | Lu et al. repo code |
| `assistant_axis/judge.py` | Python script | OpenAI judge wrapper and score parser | Canonical for its workflow | Lu et al. repo code |
| `assistant_axis/internals/activations.py` | Python script | Forward-hook activation extraction on full transformer block outputs | Canonical for its workflow | Lu et al. repo code |
| `assistant_axis/internals/model.py` | Python script | Model wrapper and layer access conventions | Canonical for its workflow | Lu et al. repo code |
| `assistant_axis/models.py` | Python script | Model configs, target layers, capping config references | Canonical for its workflow | Lu et al. repo code |
| `assistant_axis/pca.py` | Python script | Mean scaling and PCA helpers for persona space | Canonical for its workflow | Lu et al. repo code |
| `assistant_axis/steering.py` | Python script | Activation steering and capping implementations | Canonical for its workflow | Lu et al. repo code |
| `research/q2_stability/qwen/scripts/phase1_inference_only_v4.py` | Python script | Local Qwen trickster Phase 1 rollout/activation preservation script | Canonical for its workflow | Local replication |
| `research/q2_stability/qwen/scripts/score_trickster_phase2_codex_gpt55.py` | Python script | Codex GPT-5.5 role-expression scoring harness for trickster | Canonical for its workflow | Local replication |
| `research/q2_stability/qwen/scripts/extract_validate_trickster_vector.py` | Python script | Score-conditioned trickster vector validation against Lu reference | Canonical for its workflow | Local replication |
| `research/q2_stability/qwen/scripts/analyze_trickster_sample_sufficiency.py` | Python script | Trickster sample-size and adaptive stopping analysis | Canonical for its workflow | Local replication |
| `research/q2_stability/qwen/scripts/score_editor_phase2_codex_gpt55.py` | Python script | Codex GPT-5.5 role-expression scoring harness for editor | Canonical for its workflow | Local replication |

## Notebooks and README/Method Docs

| Path | Artifact type | Purpose | Canonical or derived | Source status |
|---|---|---|---|---|
| `README.md` | Markdown | Repo overview, quickstart, Assistant Axis formula, HF vector references | Canonical implementation overview | Lu et al. repo code |
| `pipeline/README.md` | Markdown | Local five-stage pipeline documentation | Canonical pipeline guide | Lu et al. repo code |
| `research/paper1_5_outline.md` | Markdown | Paper 1.5 outline and adaptive extraction methodology | Derived project document | Local replication |
| `research/paper1_5_adaptive_extraction_notes.md` | Markdown | Operational notes from trickster adaptive extraction | Derived project document | Local replication |
| `research/workflow/` | Markdown/JSON templates | Run registry, pod lifecycle, status artifacts, checklists | Derived operational infrastructure | Local replication |
| `notebooks/pca.ipynb` | Notebook | Analysis or visualization notebook | Derived or exploratory | Local/Lu mixed |
| `notebooks/project_transcipt.ipynb` | Notebook | Analysis or visualization notebook | Derived or exploratory | Local/Lu mixed |
| `notebooks/steer.ipynb` | Notebook | Analysis or visualization notebook | Derived or exploratory | Local/Lu mixed |
| `notebooks/visualize_axis.ipynb` | Notebook | Analysis or visualization notebook | Derived or exploratory | Local/Lu mixed |
| `visualizations/research_paper_notebook.ipynb` | Notebook | Analysis or visualization notebook | Derived or exploratory | Local/Lu mixed |
| `visualizations/research_paper_notebook_clean.ipynb` | Notebook | Analysis or visualization notebook | Derived or exploratory | Local/Lu mixed |
