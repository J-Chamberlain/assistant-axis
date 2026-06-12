# Assistant Centroid Provenance Audit

model_used: GPT-5.5

Date: 2026-06-11

## Section 1: Current Assistant Centroid Provenance

The assistant centroid currently used in Paper 1.5 no-label elicitation and geometry diagnostics is the inherited Qwen `assistant` role/persona coordinate:

| PC | coordinate |
|---|---:|
| PC1 | 33.7028027033 |
| PC2 | 3.441718015 |
| PC3 | -5.155533990 |

The current no-label validation runner sets this baseline by reconstructing canonical Qwen role coordinates from `downloads/hf_vectors/qwen-3-32b/role_vectors` and selecting `names.index("assistant")`. The same coordinate appears in `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv` and `research/visualizations/geometry_viz_data.json`.

**Direct answer:** the current assistant centroid is **not** a measurement of bare Qwen. It is a role-conditioned assistant persona coordinate from the released role-vector artifact family.

## Section 2: Source Artifact Lineage

The relevant lineage is:

1. Released/local Qwen role tensor: `downloads/hf_vectors/qwen-3-32b/role_vectors/assistant.pt`.
2. Canonical Qwen role coordinate table: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv`.
3. Visualization geometry: `research/visualizations/geometry_viz_data.json`.
4. No-label validation runner: `research/outputs/no_label_elicitation_validation/run_no_label_elicitation_validation.py`.
5. No-label projection debug record: `research/outputs/no_label_elicitation_validation/projection_basis_debug.json`.

The runner does not load `downloads/hf_vectors/qwen-3-32b/default_vector.pt` as the Paper 1.5 no-label baseline. It also does not use `downloads/hf_vectors/qwen-3-32b/assistant_axis.pt` as the centroid. Those are separate inherited artifacts.

The assistant role prompt artifact, `data/roles/instructions/assistant.json`, contains explicit assistant role instructions, including "You are an assistant dedicated to helping users with their various tasks and queries." By contrast, `data/roles/instructions/default.json` contains no-role/default conditions such as an empty instruction, "You are an AI assistant.", "You are a large language model.", "You are {model_name}.", and "Respond as yourself."

The local methodology reconstruction also preserves the same distinction: role vectors are produced from role-conditioned instructions, while default vectors come from default/no-role conditions; `pipeline/5_axis.py` computes the Assistant Axis as default mean minus role mean.

## Section 3: Role-Conditioned vs Bare-Model Assessment

The current assistant centroid should be interpreted as an **assistant persona representation**, not as unconditioned model behavior. It originated in the released role-vector artifact family and is reused as a coordinate anchor in the no-label validation and geometry diagnostics.

| Question | Answer |
|---|---|
| Did it come from Lu et al. released/local tensors? | Yes, through the Qwen role-vector tensor artifact family. |
| Is it a role-conditioned assistant vector? | Yes. |
| Is it a generated rollout from this project? | No. |
| Is it a local extraction run? | No. |
| Is it the released default vector? | No. |
| Is it the Assistant Axis vector? | No. |
| Is it bare/unconditioned Qwen? | No. |
| Is it reused across models? | The name exists for Qwen, Llama, and Gemma role vectors, but the current Paper 1.5 no-label baseline inspected here is the Qwen-specific assistant role coordinate. |

Transformations before use in the no-label runner:

- load released Qwen role-vector tensors;
- reduce each loaded role tensor to one vector when needed by averaging the first tensor dimension;
- reconstruct the PCA basis and coordinates from the role-vector matrix;
- sign-align reconstructed PCs to the canonical Qwen coordinate table;
- select the `assistant` role coordinate as the baseline;
- subtract that baseline from measured response coordinates to compute deltas.

The projection debug record reports max absolute canonical coordinate reproduction error of 1.207e-06, supporting coordinate-table reproduction. It does not prove that the assistant role coordinate is a bare-Qwen centroid.

## Section 4: Implications for Run 2

Observed:

- The no-label validation measured movement relative to the role-conditioned assistant centroid.
- The assistant centroid is high on Qwen PC1 relative to role centroids, which remains relevant to the PC1-positive failure.
- The current evidence does not show where bare Qwen sits under the 240 shared extraction questions.

Inferred:

- The PC1-positive failure should be described as a failure relative to a high-PC1 assistant role centroid, not as proof that bare Qwen cannot move further positive on PC1.
- The PC2-negative mixed result may partly depend on subtracting a role-conditioned assistant reference point.
- Future success criteria need two clearly separated baselines: the inherited assistant role centroid for continuity with existing geometry and a bare-Qwen/default extraction-question baseline for instrument-specific interpretation.

Speculative:

- The 240-question bare-Qwen baseline may reveal that the extraction-question instrument itself places unconditioned responses in a nonzero region of PC1/PC2/PC3 space.
- Per-question baseline subtraction may reduce apparent off-axis movement for some no-label prompt families.

Unknown:

- Whether the released `default_vector.pt` alone is sufficient for Run 2's exact planned no-system-prompt baseline.
- Whether a new bare-Qwen run will reproduce the released default-vector coordinate under the current extraction wrapper.

## Section 5: Recommendation

The 240-question bare-Qwen baseline should be treated as:

**B) foundational measurement required before interpreting future elicitation experiments.**

This recommendation is based on provenance, not convenience. The current baseline is role-conditioned. Therefore, Run 2 needs a bare-Qwen/default measurement over the extraction instrument before future no-label elicitation success or failure is interpreted as movement from the model's unconditioned response distribution.
