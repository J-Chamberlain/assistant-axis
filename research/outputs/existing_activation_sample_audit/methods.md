# Methods, provenance and detailed findings

## Checkout and search boundary

Original local checkout: /Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis.
Startup branch master; HEAD 0693aaf76e5073c37377024130dbc2d0e80424fd.
myfork points to J-Chamberlain/assistant-axis; origin points to safety-research/assistant-axis.
Startup dirty paths are recorded verbatim in source_manifest.json and preserved.

Read AGENTS.md, sticky_notes/README.md, research/RESEARCH_STATE.md, THREAD_START.md, relevant canonical provenance/claim/finding entries and all eight requested audit directories. Consulted the successor at commit 621ef9b53adcc957385cfad19655c8c03a304661, including its startup rules, state, AA15 erratum, AA27 report and mapping. No successor files changed.

Searched tracked and ignored/untracked project data and outputs, local Hugging Face release cache, sibling project directories for gregarious artifacts, relevant external-path references and public manifests. Detailed limits are in search_log.json. No read-denied errors occurred in the enumerated local research/download/cache trees. Historical /root/assistant-axis paths refer to remote pod files: local equivalents were resolved where present; no remote connection or new pod was attempted. Terminated-pod/private storage is inaccessible, not “searched and absent.” Public release payloads deliberately not downloaded are “not fully inspected,” not inaccessible. The public web renderer failed on Esther's page, but direct Hugging Face APIs and bounded Range requests succeeded.

Disk writes initially failed with ENOSPC despite df reporting about 116 MiB available. A temporary increase allowed preservation and dedicated-branch creation. When writes failed again, only the specifically presented SciPy 1.18.1 pip cache entry and its HTTP metadata were removed (20,467,992 logical bytes). No research artifacts, installed packages, Git history or unrelated work were deleted. See disk_preservation.json. Filesystem write failure was not missing input data.

## Source revisions and safe inspection

- [Original vector release](https://huggingface.co/datasets/lu-christina/assistant-axis-vectors/tree/3b3b788432ad33e3a28d9ff08e88a530c0740814): 3b3b788432ad33e3a28d9ff08e88a530c0740814. Manifest:275 roles+240 traits per model. All 1,545 local files match release LFS SHA256.
- [Prompt release](https://huggingface.co/datasets/belmore/assistant-axis-vector-prompts/tree/57424a9d6075a44196b935983ce1fa4e83191679): 57424a9d6075a44196b935983ce1fa4e83191679. The682,199-byte Parquet has516 rows:275 roles, default,240 traits. Its gregarious instructions, questions and rubric exactly match local JSON. SHA256 ae4531bc5e870606ee304198d086db23c7fd01fb31cc32f9dfa9c820bead6295.
- [Third-party outputs](https://huggingface.co/datasets/EstherYang119/assistant-axis-outputs/tree/d800bb147b7b4259b1ad8a6cf5e525ab5e70a607): d800bb147b7b4259b1ad8a6cf5e525ab5e70a607, latest commit2026-05-25, by EstherYang119. Ninety-six files; no README, extraction code, model revision or run configuration in the manifest.
- [Paper, v1 Appendix C.1](https://arxiv.org/html/2601.10387v1#A3.SS1) and locally pinned public pipeline code establish the intended method, not missing run-level lineage.

No downloaded Python code was executed. Local tensor archives were inspected with zipfile/pickletools (opcode parsing, not unpickling); spot loads used torch.load(map_location="cpu", weights_only=True). Remote activation files received262,144-byte prefix requests each (HTTP206); parsing completed through each pickle STOP without executing GLOBAL/REDUCE opcodes. No remote tensor storage payload was loaded. Header metadata is not a full-file checksum or a numerical integrity check. See remote_metadata.json and scripts.

## What each representation preserves

Released matrices: Qwen[64,5120], Llama[80,8192], Gemma[46,4608], all bfloat16. These are layer×feature aggregates, **not64/80/46 responses**. That interpretation follows models.py, hook/span code, release lineage and AA15, not shape alone.

The [AA15 erratum](../../../../persona-human-geometry/research/outputs/aa15_hifwb_trait_pc/aa14_extraction_provenance_erratum.md) establishes that successor AA14/15 geometry averages all saved layer rows. The original checkout's research/visualizations/scripts/build_geometry_viz.py:68 also averages rows before PCA. A single-layer response projected into that basis is a descriptive mixed-representation projection, not an observed all-layer-average response.

The corrected Qwen hook is model.model.layers[48] output, corresponding to hidden_states[49], as the saved A100 boundary test verifies (cosine1 and zero coordinate difference). hidden_states[48] is the preceding block 47 output. H100 percentile-edge outputs used this earlier boundary. Keep them separate. For a single-layer trait readout, pair block 48 response vectors with released row 48, conditional on the supported released layer-order convention. Do not silently substitute the successor's layer mean.

Public role pipeline2 stores one layer matrix per label/prompt/question key, mean-pooling assistant tokens. Pipeline4 averages score3 records (default minimum 50), while the paper describes fully/somewhat role categories and at least 10 in a category. The public code is not proof of the exact aggregate release's filter version. It is role-oriented and does not resolve trait-specific filtering/weighting. Repeated samples at the same key would collide in the public dictionary format unless identifiers were extended; never infer missing repeat counts from tensor size.

## Local role runs and scores

| Run | Responses | Preserved representation | Observed grouping | Existing score>=2 / score3 |
|---|---:|---|---|---|
| A100 amateur |60|PC1-PC3 + text; no full vector save in runner|5 instructions×12 questions|GPT-4.1:59/34; GPT-5.5:44/11|
| A100 playwright |60|PC1-PC3 + text; no full vector save in runner|5×12|GPT-4.1:54/49; GPT-5.5:54/40|
| trickster_phase1_1200 |1,200|1,200 float32[5120] shards + text + corrected PCs|5×240; greedy|GPT-4.1:1200/1198; GPT-5.5:64/33 among only 64 judged|
| editor_phase1_128 |128|128 float32[5120] shards + text + corrected PCs|1 instruction×128 questions; greedy|GPT-4.1:57/3; GPT-5.5:10/3|
| editor_matched64_1024 |64|64 float32[5120] shards + text + corrected PCs|1×64, matched contexts; greedy|GPT-4.1:36/2; GPT-5.5:5/1|
| earlier trickster inline pilot |104|normalized full-feature[5120] JSON arrays, rounded6 decimals + text|1×104; temperature0.7,top_p0.95|inline GPT-5.5 API:104/102|

The five main clouds total 1,512 run-qualified records. The additional 104-record pilot is separate, bringing the named-role total to 1,616 records; that is not 1,616 independent realizations. Its norms are0.999999063–1.000000764, consistent with the inspected normalization code, so raw radial variation cannot be reconstructed. Its historical score parser takes the first 0–3 digit and warrants caution. It shares104 context IDs with the later trickster run but zero exact response texts.

All 1,392 raw adaptive shards exist and have expected shape metadata. Their relative paths resolve from paper1_5, not each JSONL's immediate parent. Both editor runs share 64 prompt/question keys and 14 exactly identical response texts; retain run-qualified IDs and paired sensitivity comparisons, never count these as independent extra contexts. Truncation flags:733/1200 trickster,99/128 editor512,5/64 editor1024.

The layered viewer and prior/recovered analysis tables are derived copies, not new samples or neural layers. GPT-5.5 is absent from the viewer for editor/trickster but survives in the original score JSONLs; “unavailable in viewer” is not “unscored.” All score counts above were independently counted from existing artifacts, with unique IDs. These are role-expression scores, **not gregariousness scores**.

Covariance JSONs and companion n/means are sufficient for second moments in the saved 3D projection. They cannot recover full-feature covariance, tails, paired bootstraps, response-level scores or a lost cloud.

Additional Qwen extractions remain separate and do not increase275-persona/240-trait coverage:
- H100 percentile-edge validation:100 projected responses, hidden_states[48], user-only novel prompts.
- No-label Run1:600 projected responses, block 48 hook.
- No-label Run2:1,690 full float32[5120] .npy shards and linked rows, including1,200 bare-model baseline responses and490 condition responses.
- PC1 accountability validation:200 projected responses; all 200 referenced full shards are absent locally. The surviving CSV is usable; historical remote shards remain inaccessible/unverified.
Other emotion, steering and dialogue experiments have different constructs, token pooling or dependent multi-turn contexts; they are not recoveries of the original persona/trait elicitation distributions.

## Third-party recovery lead

Header inspection establishes 23 dictionaries, each with 1,200 unique pos_p0..4_q0..239 keys and 1,200 declared bfloat16[64,5120] tensors:27,600 run-qualified entries. These are dictionary-keyed samples with layer rows within each sample.

Creativity personas: composer, improviser, musician, novelist, playwright, poet, writer.
Reasoning: analyst, detective, devils_advocate, mathematician, philosopher, skeptic, theorist.
SWE: debugger, engineer, hacker, programmer, robot, technologist.
Each run also has default; default is not one of the 275 personas and its three copies are not presumed identical.

Every nondefault activation file has a score file. Nineteen have 1,200 score keys; debugger has 1,198, leaving 2 unscored activations. All score keys join to activation keys. First response records match the key schema and supply system/user/assistant messages. Full response files were not scanned, so exhaustive response↔activation linkage, duplicate texts, numerical tensor integrity and aggregate reconstruction remain unverified. Checkpoint response copies are excluded.

This is evidence of remote recoverable candidate clouds without model execution, but not of method equivalence or original-study lineage. Unknowns include exact model checkpoint, code version, hook order, pooling/truncation, generation settings, scorer identity and aggregation filter. Resolving them requires provenance documentation and bounded data validation; they cannot be filled in from a matching shape. The 23 activation payloads total about18.1GB, so none was downloaded for inventory completeness. No Llama, Gemma or trait activations occur in this manifest.

## Gregariousness trace and bridge boundary

Exact canonical definition: “Shows highly sociable, outgoing style that seeks interaction and company.” Source:data/traits/trait_list.json:163; key gregarious.

data/traits/instructions/gregarious.json preserves:
- Pair0: sociability and actively encouraging further interaction versus reserved/withdrawn, avoiding extended interaction.
- Pair1: enthusiasm, rapport and ongoing dialogue versus distance/solitude.
- Pair2: warmth and eager conversation across topics versus selective engagement and avoiding warmth.
- Pair3: companionship and thriving on connection versus solitude/minimal engagement.
- Pair4: outgoing group/community participation versus private/independent engagement.

All 40 indexed questions survive, ranging from office work, weekend evenings, new-city contacts and birthday celebrations to learning, shopping, conflict, customer service, group projects and small talk. Questions16,19,23,26 and 35 (zero-based) directly probe shopping, dinner parties, clubs, gatherings and community involvement respectively; shopping is a useful example of a weakly diagnostic context, not a new bridge indicator. Full wording and the zero-based source order remain in the unchanged JSON.

The rubric requests a0–100 trait-expression score or REFUSAL and explicitly mentions interaction, connection and others' company. It does not separately score company-seeking, warmth, energy, verbosity or friendliness. The prompts therefore have substantial conceptual overlap with seeking company, but also elicit rapport, warmth and conversation extension. Verbosity is a plausible consequence/confound, not an explicit length instruction; no empirical confound magnitude is claimed.

The paper describes 2,400 rollouts per polarity, response-token residual means, positive-minus-negative subtraction and a score-gap filter. Five preserved pairs×40 questions supply only 200 distinct contexts per polarity; the reported at-least-ten system-prompt-pair criterion is also not literal under five preserved pairs. Repeat structure, the selection unit and weighting remain unresolved. Do not invent12 repeats or reinterpret the unit as question pairs without evidence.

| Model | Instructions/questions/rubric | Aggregate gregarious tensor | Positive sample set | Negative sample set | Retained pairs/scores/weights | Reconstruct mean difference |
|---|---|---|---|---|---|---|
| Qwen | shared corpus survives |[64,5120] bf16|not found|not found|not found|no|
| Llama | shared corpus survives |[80,8192] bf16|not found|not found|not found|no|
| Gemma | shared corpus survives |[46,4608] bf16|not found|not found|not found|no|

The successor's AA27 ipip_facet_scoring_specification.csv maps E2 to ten existing items: company/group/party participation on the positive side, solitude/crowd avoidance/quiet on the negative side. See its model_trait_ipip_facet_crosswalk.csv and facet_bridge_coverage.csv: gregarious+ is the sole direct indicator; extroverted+ and introverted− are close, not newly admitted direct indicators. This audit adds none. Prompt warmth overlaps E1 content; expressive energy is not automatically E4 activity. Neither verbal similarity nor recovery of a response cloud satisfies AA27's requirement for two nonduplicate indicators per facet and three adequately measured Extraversion facets. AA27's failed gate and all AA26 corrections remain unchanged. No human values were computed or compared.

## Feasibility and resampling

| Question | What is possible now | Limit |
|---|---|---|
| Cloud width/orientation |3D clouds for4 Qwen personas; full-feature raw clouds for2; angular cloud for older trickster|3D says nothing about discarded axes; single-layer is not layer-average; normalized pilot loses radius|
| Uncertainty in estimated centroid |resample observed prompt/question groups and retained records|response spread is not SE; n-independent SE formulas ignore crossed contexts and filtering|
| Prompt/question sensitivity |preserved context keys, text, five-instruction trickster and pilot grids; paired editor caps|one-instruction editor/partial runs cannot estimate instruction-population variation|
| Filtering sensitivity |existing role judges and membership IDs, all vs>=2 vs=3|sparse editor score3 n=2–3;64 trickster GPT-5.5 scores are not a random sample of 1200|
| Persona gregariousness distributions |fixed row 48 trait readout on full-feature Qwen responses; cosine also on normalized partial|no saved gregariousness judge scores; no full readout from3D coordinates; no within-persona distribution from275 centroids|
| Positive/negative separation, trait direction stability |not possible for original gregariousness, or any original trait, with found samples|requires both polarities, context pairing, filter scores/membership and weighting|
| Third-party analyses |potential full-layer, response and score joins after payload/provenance validation|remote candidates currently excluded from method-compatible counts|

For the complete5×240 and5×12 grids, use a crossed prompt/question bootstrap (independent cluster resampling with product weights), preserving common question and instruction indices across compared filters. With so few instructions, report leave-one-instruction-out sensitivity alongside bootstrap intervals. For one-instruction runs condition inference on that instruction. In a recovered trait design, resample matched positive/negative context pairs together, preserve polarity balance, resample within-cell replicates only if they exist, and recompute the documented selection/aggregation rule rather than resampling layer rows.

Compare widths at matched numbers of contexts, show each run's full n, and report unfiltered plus fixed-threshold filtered results. Use common context support for paired editor comparisons; do not let14 identical texts create false independent replication. A filter changes the estimand; equalizing sample sizes does not undo selection bias or different instruction support. Sparse score3 editor subsets do not support stable covariance orientation. Report eigenvalue gaps and sign-invariant orientation intervals, and avoid directional claims for near-isotropic clouds.

Greedy trickster/editor variation across cells is context variation. The stochastic pilot has one sampled response per context, so stochastic and context variation cannot be separated within those cells. Repeated no-label runs can inform their own variance decomposition, not the 275 original personas. Do not generalize a handful of recovered clouds.

With a fixed trait vector g, resampling responses estimates uncertainty conditional on g. Uncertainty from estimating g requires resampling its positive/negative training samples and refitting g (ideally nested with held-out response scoring to address dependence). Those original training records are missing. Original released centroids and layer rows cannot substitute for them; n and covariance alone would support only assumption-dependent mean uncertainty, not recovery of the empirical cloud.

## Audit checks and handoff

validation_summary.json records coverage, exact vector hashes, unique run-qualified IDs, shard presence, tensor metadata, score counts and duplicate handling. Header parsing does not claim full numerical validation. A small safe torch check independently confirmed gregarious shapes/dtypes and a local response shard. inventory.csv contains source-specific rows; multiple artifact rows can refer to the same responses and must not be summed as independent samples.

The successor handoff is HANDOFF.md in this output directory. Preserve AA15's all-layer correction, AA26's superseded results and AA27's failed bridge gate. The audit authorizes no follow-on experiment. Stop here.
