# PCA–trait dependency audit

## Observed construction

The canonical builder `research/visualizations/scripts/build_geometry_viz.py` loads saved Qwen role tensors and mean-pools every 2D tensor over its first dimension (`load_vectors`, lines 61–70). The verified role matrix has shape 275 × 5,120. The builder then executes `PCA(n_components=3).fit_transform(role_vecs)` on that role matrix (lines 200–205). Thus the PCA feature variables are the 5,120 activation coordinates, and the observations are the 275 roles/personas.

The builder also loads 240 trait tensors, but those traits are processed separately. They do not enter the role-PCA fit. The source-vector audit reproduced the canonical PCA coordinates from centered mean-pooled role vectors with maximum absolute error 1.207e-06 (tolerance 1.0e-05).

The existing 275 × 240 predictor matrix was independently reproduced by L2-normalizing the same mean-pooled role vectors and the 240 mean-pooled trait vectors, then multiplying role-unit vectors by trait-unit vectors transposed. Maximum absolute matrix error was 5.551e-16.

## Dependency conclusion

PCA and the trait bank are not circular in the strongest sense: the 240 named trait scores are not inputs to the PCA construction. They are nevertheless algebraically dependent. Every target coordinate is a centered linear projection of a role activation vector, while every predictor is a cosine projection of that same role vector onto a trait activation direction. With sufficiently stable role norms and enough directions, Ridge can reconstruct PCA directions through activation-space basis coverage even when the direction labels carry no special psychological meaning.

This audit therefore treats near-ceiling prediction as same-space reconstruction. Semantic trait-specific advantage must be established by outperforming matched generic direction banks; it cannot be inferred from the full 240-trait result alone.

## Verified counts

- Roles/personas: 275
- Mean-pooled role dimension: 5120
- Named trait directions: 240
- Named traits used to fit role PCA: no
- Same role activation vectors shared across predictors and targets: yes
