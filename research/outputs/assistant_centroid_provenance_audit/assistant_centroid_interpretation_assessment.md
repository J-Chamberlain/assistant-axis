# Assistant Centroid Interpretation Assessment

model_used: GPT-5.5

## Direct Answers

**Is the assistant centroid currently used in Paper 1.5 a measurement of bare Qwen?**

No. The current assistant centroid is the released Qwen `assistant` role/persona vector projected into the canonical Qwen role PCA coordinates. It is not the released `default_vector.pt`, not the `assistant_axis.pt`, and not a local bare-Qwen measurement.

**Should the 240-question baseline be considered foundational or optional?**

Foundational for future no-label elicitation interpretation. The current baseline answers "movement relative to the assistant role centroid," not "movement relative to bare Qwen on the extraction-question instrument."

## Observed

- The no-label validation runner loads `downloads/hf_vectors/qwen-3-32b/role_vectors`, reconstructs canonical role coordinates, and sets `assistant_baseline` to `reconstructed[names.index("assistant")]`.
- The debug file records `assistant_baseline_pc1=33.70280270327191`, `assistant_baseline_pc2=3.4417180154398817`, and `assistant_baseline_pc3=-5.155534089069803`.
- The canonical Qwen coordinate table and visualization geometry contain the same assistant row: PC1=33.702802703308954, PC2=3.441718014945549, PC3=-5.155533989826894.
- `data/roles/instructions/assistant.json` contains explicit assistant role instructions. `data/roles/instructions/default.json`, `downloads/hf_vectors/qwen-3-32b/default_vector.pt`, and `downloads/hf_vectors/qwen-3-32b/assistant_axis.pt` are separate artifacts.
- The public/source-style pipeline distinguishes role vectors from default vectors and computes an Assistant Axis as default mean minus role mean.

## Inferred

- The no-label elicitation results should be described as directional movement relative to the inherited assistant role/persona centroid.
- The PC1-positive failure can still be consistent with assistant-role saturation, but it does not prove bare-Qwen saturation because bare-Qwen/default behavior was not the baseline.
- PC2-negative mixed results may depend on using a role-conditioned assistant centroid as the subtraction point. A bare-Qwen extraction-question baseline is needed to determine the instrument's native PC2 placement.
- Future success criteria should explicitly distinguish movement relative to the assistant role centroid from movement relative to a bare-Qwen/default extraction-question distribution.

## Speculative

- A bare-Qwen baseline may shift the apparent difficulty of positive-PC1 elicitation if bare Qwen starts below the assistant role centroid on PC1.
- Some no-label prompt families may look cleaner when evaluated against a per-question bare-Qwen baseline rather than a single assistant role centroid.
- A revised experiment may need two reference points: the published assistant role centroid for continuity with Paper 1.5 and the bare 240-question baseline for instrument-specific causal interpretation.

## Unknown

- The exact bare-Qwen distribution over the 240 shared extraction questions has not yet been measured in this project.
- The current audit does not establish whether `default_vector.pt` is an adequate substitute for a new bare-Qwen run under the exact planned Run 2 generation wrapper.
- The current audit does not resolve all original Lu et al. retained-response IDs or response-level judge-score filters for the released assistant role vector.
