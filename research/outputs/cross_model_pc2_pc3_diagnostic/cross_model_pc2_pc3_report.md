# Cross-Model PC2/PC3 Diagnostic

- Date: 2026-06-02T10:16:43Z
- model_used: GPT-5.5
- Geometry source: `research/visualizations/geometry_viz_data.json`
- Released vector roots: `downloads/hf_vectors/qwen-3-32b`, `downloads/hf_vectors/llama-3.3-70b`, `downloads/hf_vectors/gemma-2-27b`
- Vector representation: layer-mean role vectors, matching the current Qwen geometry visualization builder.
- No GPU work, no generation, no H100 outputs, no prompt-battery outputs, and no visualization files were modified.

## Models Found

- qwen: 275 roles, explained variance PC1/PC2/PC3 = 0.316/0.162/0.087
- llama: 275 roles, explained variance PC1/PC2/PC3 = 0.172/0.142/0.065
- gemma: 275 roles, explained variance PC1/PC2/PC3 = 0.235/0.128/0.057

All three local released-vector model directories contain 275 role vectors. Qwen and Llama are the primary comparison; Gemma is included as secondary diagnostic context.

## Qwen-Llama Correlation Matrix

Matched role count: 275.

| Qwen PC | Llama PC1 Pearson | Llama PC2 Pearson | Llama PC3 Pearson |
|---|---:|---:|---:|
| PC1 | 0.676 | -0.676 | 0.151 |
| PC2 | 0.692 | 0.606 | -0.154 |
| PC3 | -0.031 | 0.160 | 0.440 |

Best matches:

- PC1 best matches Llama PC2 at abs Pearson r=0.676 (signed r=-0.676).
- PC2 best matches Llama PC1 at abs Pearson r=0.692 (signed r=0.692).
- PC3 best matches Llama PC3 at abs Pearson r=0.440 (signed r=0.440).

The Qwen-Llama PC1/PC2 plane is more comparable than the individual same-numbered axes: the PC1/PC2 principal correlations are 0.977 and 0.905. This means PC2 should be interpreted with an axis-rotation caveat: Qwen PC2 overlaps both Llama PC1 and Llama PC2, and Qwen PC1 also mixes into Llama PC1/PC2.

## PC2 Comparability

Qwen PC2 vs Llama PC2 has Pearson r=0.606 and Spearman r=0.430. Qwen PC2's strongest single-axis Llama match is Llama PC1 at Pearson r=0.692. This is partial but meaningful agreement in a shared PC1/PC2 plane rather than a clean one-to-one same-index transfer.

Qwen PC2 top roles: teenager (78.1), adolescent (78.1), toddler (71.2), procrastinator (69.5), gossip (57.2), comedian (56.6), fool (47.9), infant (44.7), daredevil (43.7), cynic (40.7)
Qwen PC2 bottom roles: crystalline (-44.0), ascetic (-40.4), eldritch (-39.5), mystic (-36.2), avatar (-35.4), oracle (-34.5), leviathan (-33.5), echo (-33.4), spirit (-33.2), ancient (-32.8)

Llama PC2 top roles: caveman (4.2), toddler (4.2), infant (4.0), fool (3.5), procrastinator (2.7), criminal (2.7), pirate (2.5), adolescent (2.5), teenager (2.4), prisoner (2.4)
Llama PC2 bottom roles: theorist (-1.3), strategist (-1.2), evaluator (-1.2), emissary (-1.2), reviewer (-1.1), examiner (-1.1), forecaster (-1.1), polymath (-1.1), sociologist (-1.1), researcher (-1.1)

Llama muted-PC1 PC2 top roles: caveman (4.2), pirate (2.5), vigilante (1.1), widow (0.7), hacker (0.3), survivor (0.2), devils_advocate (-0.2), merchant (-0.4), scout (-0.5), altruist (-0.5)
Llama muted-PC1 PC2 bottom roles: futurist (-1.1), interpreter (-1.0), generalist (-1.0), anthropologist (-1.0), observer (-1.0), ambassador (-0.9), geographer (-0.9), judge (-0.9), archivist (-0.8), conservator (-0.8)

Expected-direction checks:

- Qwen global: 16/16; Qwen cluster-relative: 13/16.
- Llama global: 13/16; Llama cluster-relative: 7/16.

Interpretation: Llama gives partial support to the Qwen PC2 story, not a decisive resolution. The broad high-PC2 pattern continues to include formative, exposed, performative, or locally pressured roles in several cases, but cluster effects, individual counterexamples, and PC1/PC2 axis mixing remain important. PC2 should remain provisional and should be phrased as a partly transferable situated-immediacy/formative-state versus integrated-stability axis within a shared low-dimensional plane, not as a settled model-general same-index construct.

## PC3 Comparability

Qwen PC3 vs Llama PC3 has Pearson r=0.440 and Spearman r=0.558. This is weak relative to PC1/PC2 and supports caution about treating same-index PC3 as directly comparable across models.

Qwen PC3 top roles: hacker (36.4), cynic (36.3), saboteur (34.8), provocateur (34.5), absurdist (33.4), spy (32.1), comedian (31.3), aberration (31.1), jester (31.0), rogue (30.2)
Qwen PC3 bottom roles: caregiver (-43.4), empath (-36.9), counselor (-36.2), therapist (-34.5), healer (-34.3), widow (-34.3), optimist (-31.3), romantic (-30.8), angel (-30.6), grandparent (-30.1)

Llama PC3 top roles: infant (4.3), caveman (3.1), toddler (3.1), robot (1.7), void (1.5), eldritch (1.4), crystalline (1.2), leviathan (1.1), fool (1.0), prey (1.0)
Llama PC3 bottom roles: bohemian (-1.6), romantic (-1.4), pilgrim (-1.3), widow (-1.3), orphan (-1.3), idealist (-1.3), survivor (-1.2), divorcee (-1.2), celebrity (-1.2), pacifist (-1.1)

Interpretation: PC3 does not yet look stable enough for same-index Qwen-to-Llama 3D arrow visualizations. Future visualization should either omit PC3, explicitly show PC3 as low-confidence, or use an alignment-corrected cross-model basis.

## Diagnostic Roles

Detailed diagnostic-role coordinates and ranks are in `cross_model_diagnostic_roles.csv`. The key Qwen counterexamples remain visible: `shapeshifter` is low on Qwen PC2, `chameleon` is globally high but cluster-sensitive, and `elder` changes interpretation depending on global versus cluster-relative baseline. Llama helps by showing which of these are Qwen-specific versus shared rank ambiguities, but it does not remove the caveat.

## Gemma

Gemma was included because local vectors are available, but it should remain secondary to the requested Qwen-Llama diagnostic. In this layer-mean released-vector PCA diagnostic, Gemma aligns surprisingly strongly with Qwen on same-index PCs: Qwen-Gemma PC1 r=0.953, PC2 r=0.922, and PC3 r=0.806. This should be treated as a local artifact-level result rather than a full behavioral generalization claim.

## Visualization Feasibility

The current main viewer embeds a single Qwen `VIZ_DATA` object in `research/visualizations/persona_geometry_explorer.html` and expects one dataset with PCA/UMAP arrays, clusters, nearest neighbors, and overlay data. Adding model switching would require a new multi-model data bundle and UI state for selected model. Cross-model arrows would require a separate view or an alignment convention because independent PCA coordinates are not in one shared coordinate frame by default.

Recommendation: no visualization changes yet. If a visualization is added later, start with a cross-model PC1/PC2 comparison or model-switching viewer; do not build same-index PC1/PC2/PC3 cross-model arrows until PC3 alignment is corrected or explicitly caveated.

## Output Files

- `cross_model_pc_correlation_matrix.csv`
- `cross_model_pc_best_matches.csv`
- `cross_model_diagnostic_roles.csv`
- `qwen_llama_pc2_expected_direction_checks.csv`
- `per_model_pc2_rankings.csv`
- `per_model_pc3_rankings.csv`
- `muted_pc1_pc2_extremes_by_model.csv`
- `cross_model_pc2_pc3_stats.json`
- `visualization_feasibility_note.md`
- `cross_model_pc2_pc3_plots.png`
- `run_cross_model_pc2_pc3_diagnostic.py`
