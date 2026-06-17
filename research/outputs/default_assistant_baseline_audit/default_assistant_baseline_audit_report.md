# Default Assistant Baseline Audit

model_used: GPT-5.5

Date: 2026-06-17

## Summary

This audit identifies and projects Lu et al.'s released Qwen default Assistant activation artifact into the canonical Paper 1.5 PCA basis, then compares it against the currently used assistant role centroid and the Run 2 bare no-system centroid.

**Direct answer:** the Lu et al. default Assistant activation artifact for Qwen is `downloads/hf_vectors/qwen-3-32b/default_vector.pt`. It is not `assistant_axis.pt`; `assistant_axis.pt` is an axis/difference vector, not a centroid/reference point. The Paper 1.5 bare no-system baseline is materially different from Lu's released default vector in the canonical PC space, so Paper 1.5 did not merely rediscover or duplicate Lu's default behavior reference.

## Section 1: Identify The Default Assistant Artifact

### Identified artifact

| Field | Value |
|---|---|
| Artifact | `downloads/hf_vectors/qwen-3-32b/default_vector.pt` |
| Tensor shape | `[64, 5120]` |
| Local projection convention | Mean across first tensor dimension, matching `research/visualizations/scripts/build_geometry_viz.py` and Run 2 projection-basis reconstruction |
| Status | Released/local Lu et al. default/no-role vector artifact |

### Evidence

- `downloads/hf_vectors/qwen-3-32b/default_vector.pt` exists next to `assistant_axis.pt` and `role_vectors/assistant.pt` in the released Qwen vector artifact directory.
- `data/roles/instructions/default.json` defines the default/no-role instruction set: empty instruction, `You are an AI assistant.`, `You are a large language model.`, `You are {model_name}.`, and `Respond as yourself.`
- `data/roles/instructions/assistant.json` separately defines explicit assistant role instructions, e.g. `You are an assistant dedicated to helping users with their various tasks and queries.`
- `pipeline/5_axis.py` states the formula `axis = mean(default_vectors) - mean(pos_3_vectors across roles)` and computes the axis from default vectors minus role vectors. Therefore `assistant_axis.pt` is a direction/difference vector, not the default activation point.
- The previous assistant-centroid provenance audit established that the Paper 1.5 assistant centroid is `downloads/hf_vectors/qwen-3-32b/role_vectors/assistant.pt`, not `default_vector.pt` and not `assistant_axis.pt`.

### Generation procedure provenance

Public/local evidence supports this lineage:

1. Default/no-role conditions are defined in `data/roles/instructions/default.json`.
2. Role-conditioned assistant conditions are defined separately in `data/roles/instructions/assistant.json`.
3. The released Hugging Face vector artifact stores the resulting Qwen default vector as `downloads/hf_vectors/qwen-3-32b/default_vector.pt`.
4. The Assistant Axis is derived downstream from default and role vectors, so `assistant_axis.pt` should not be interpreted as the default Assistant activation.

The public files do not expose original default rollout transcripts or response-level judge/filter records for this vector, so the audit identifies the artifact and source instruction family but does not reconstruct individual default-generation samples.

## Section 2: Projection Into Canonical Paper 1.5 PCA Basis

Projection used the same local basis reconstruction used by Run 2:

- Load 275 Qwen role vectors from `downloads/hf_vectors/qwen-3-32b/role_vectors/`.
- Reduce each `[64, 5120]` tensor to one vector by mean pooling the first tensor dimension.
- Reconstruct PCA over the 275 role vectors.
- Sign-align PCs to `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv`.
- Project `default_vector.pt` using the reconstructed mean and components.

Basis validation:

| Check | Value |
|---|---:|
| Roles used | 275 |
| Canonical rows used for validation | 273 |
| Max absolute coordinate reproduction error | 1.207e-06 |
| Mean absolute coordinate reproduction error | 1.074e-07 |
| Sign alignment | `[-1.0, 1.0, -1.0]` |

Projected Lu default Assistant activation:

| Reference | PC1 | PC2 | PC3 |
|---|---:|---:|---:|
| Lu default Assistant activation (`default_vector.pt`) | 27.130667 | 8.005075 | -6.630754 |

## Section 3: Compare Three Reference Points

| Reference | PC1 | PC2 | PC3 | Source |
|---|---:|---:|---:|---|
| Assistant role centroid | 33.702803 | 3.441718 | -5.155534 | `downloads/hf_vectors/qwen-3-32b/role_vectors/assistant.pt` |
| Bare no-system centroid | 23.509937 | 14.040867 | -2.460112 | Mean of 1,200 Run 2 baseline activation shards |
| Lu default Assistant activation | 27.130667 | 8.005075 | -6.630754 | `downloads/hf_vectors/qwen-3-32b/default_vector.pt` |

Pairwise comparison:

| Pair | ΔPC1 | ΔPC2 | ΔPC3 | 3D distance | Full-vector cosine |
|---|---:|---:|---:|---:|---:|
| Assistant role -> bare no-system | -10.192866 | 10.599149 | 2.695422 | 14.949976 | 0.962533 |
| Assistant role -> Lu default | -6.572136 | 4.563357 | -1.475220 | 8.135937 | 0.999458 |
| Bare no-system -> Lu default | 3.620730 | -6.035792 | -4.170641 | 8.181364 | 0.962739 |

Nearest roles in canonical PC1/PC2/PC3 space:

| Reference | Nearest 5 roles |
|---|---|
| Assistant role centroid | assistant, instructor, trainer, recruiter, summarizer |
| Bare no-system centroid | paramedic, presenter, interviewer, translator, mentor |
| Lu default Assistant activation | paramedic, interviewer, mentor, tutor, teacher |

Full-vector cosine nearest roles are less discriminating because released role/default vectors are highly similar in the full 5120-dimensional space. In full-vector cosine, Lu `default_vector.pt` is extremely close to the assistant role vector (cosine 0.999458), while the Run 2 bare no-system centroid is much farther from both in full-vector terms (cosine about 0.963 to each). The PC projection is therefore the more relevant comparison for Paper 1.5 geometry interpretation.

## Section 4: Are Bare-Qwen And Lu Default The Same Object?

**Answer: Case B — the bare-Qwen baseline is materially different from Lu's default Assistant activation.**

Observed:

- The bare no-system centroid and Lu default vector differ by 8.181 PC units in canonical PC1/PC2/PC3 space.
- Their difference is structured, not numerical noise: Lu default is +3.621 PC1, -6.036 PC2, and -4.171 PC3 relative to the bare no-system centroid.
- Lu default is almost exactly halfway between assistant role and bare no-system in 3D distance: distance to assistant role is 8.136; distance to bare no-system is 8.181.
- Full-vector cosine does not collapse the distinction because the full-vector space is dominated by shared activation structure; in the geometry-relevant PCA subspace, the points are distinct.

Inferred:

- Run 2's bare no-system baseline is not a replication of `default_vector.pt`; it measures a stricter no-system/no-role condition over the 240 extraction questions with current direct-hook response extraction.
- Lu `default_vector.pt` likely reflects the released default/no-role instruction family, which includes several assistant/self-description default prompts, not only a bare one-message no-system condition.

Unknown:

- The public artifact does not include the exact generated responses underlying `default_vector.pt`, so the audit cannot decompose how much of the default vector comes from the empty instruction versus the assistant/LLM/self default instructions.

## Section 5: Paper Implication And Recommendation

Recommendation: **B. Keep both**, with clear labels.

Paper 1.5 should not replace the Run 2 bare-Qwen baseline discussion with Lu's default Assistant activation. It should report three distinct reference points when relevant:

1. `assistant` role centroid: role-conditioned assistant persona reference.
2. Lu `default_vector.pt`: inherited released default/no-role artifact from the Assistant Axis vector package.
3. Run 2 bare no-system centroid: stricter experiment-specific baseline over the 240 extraction-question instrument.

Recommended wording:

> The Run 2 bare no-system centroid is not the same object as Lu et al.'s released `default_vector.pt`. Projected into the same Qwen role-PCA basis, `default_vector.pt` lies between the assistant role centroid and the Run 2 bare no-system centroid. We therefore keep the bare no-system baseline as the experiment-specific reference for no-label elicitation while treating Lu's default vector as an inherited methodological reference point.

Explicit answer to the requested question:

**Paper 1.5 independently measured a stricter bare no-system baseline; it did not largely reproduce Lu et al.'s default behavior reference.** The Lu default vector remains useful as a comparison point, but it should not replace the bare-Qwen baseline.

## Files Produced

- `research/outputs/default_assistant_baseline_audit/default_assistant_baseline_audit_report.md`
- `research/outputs/default_assistant_baseline_audit/centroid_comparison_table.csv`
- `research/outputs/default_assistant_baseline_audit/default_vector_projection.csv`
- `research/outputs/default_assistant_baseline_audit/artifact_inventory.csv`
