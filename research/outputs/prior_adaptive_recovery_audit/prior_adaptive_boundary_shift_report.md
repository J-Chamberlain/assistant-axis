# Prior Adaptive Boundary Shift Report

## Conclusion

The prior adaptive Phase 1 activation shards for trickster and editor are
already hook-derived `model.model.layers[48]` response-token pooled vectors.
Under the corrected D01 boundary result, these correspond to the corrected
source (`hidden_states[49]` equivalent), not the mistaken `hidden_states[48]`
boundary.

## Local Reprojection

The audit reconstructed the canonical Qwen PCA basis from the committed
Qwen role vectors and aligned signs against
`canonical_activation_pca3d.csv`.

Basis reproduction debug:

```json
{
  "basis_source": "reconstructed_from_qwen_role_vectors_with_sign_alignment_to_canonical_activation_pca3d",
  "canonical_pca_path": "research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/canonical_activation_pca3d.csv",
  "vector_dir": "downloads/hf_vectors/qwen-3-32b/role_vectors",
  "n_roles_used": 275,
  "max_abs_coordinate_reproduction_error": 1.207032853223211e-06,
  "mean_abs_coordinate_reproduction_error": 1.0737016308133192e-07,
  "sign_alignment": [
    -1.0,
    1.0,
    -1.0
  ]
}
```

Corrected/local coordinates are written to
`prior_adaptive_corrected_coordinates.csv`, and cloud summaries are written to
`prior_adaptive_corrected_cloud_summary.csv`.

## What Would Still Require GPU

If a future question requires raw token-level hidden states or direct comparison
against `outputs.hidden_states[48]`/`[49]` for these exact prompts, that cannot be
recovered from the mean-pooled activation shards. It would require regenerating
or rerunning forward passes on GPU.
