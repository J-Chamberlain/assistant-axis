# Human ↔ Qwen trait-profile visual comparison

Status: descriptive follow-up to the completed Rosetta analysis. No matches, bridge memberships, clusters, or transformations were changed.

## Sources and plotted values

The plots use the fixed Rosetta anchor-only human↔Qwen pairings from `matched_cluster_profiles.csv`, with rows ordered K ascending and then MFamily_A–D. The 12 traits are the exact frozen moderate-or-better human-supported set. The 45 traits are the exact `ACCEPT_DIRECT` vocabulary from the frozen prior bridge, in source order. Plotted values are the canonical normalized aggregate profile scores inherited from the prior correspondence/Rosetta analysis; no new scaling or visual optimization was introduced.

## Observed

At the 12-trait level, the 24 fixed pairs have mean descriptive Pearson r=0.5393, mean cosine=0.5664, mean RMSE=0.7216, and mean absolute residual=0.6418. At the 45-trait level, the corresponding values are r=0.2304, cosine=0.2769, RMSE=0.8635, and mean absolute residual=0.7563. Thus the restricted 12-trait profiles look materially cleaner descriptively, while still showing sizeable pair- and trait-specific differences.

The strongest cross-pair rank agreements among the 45 traits are cynical (r=0.928), paranoid (0.858), judgmental (0.840), rebellious (0.822), pessimistic (0.808), agreeable (0.804), optimistic (0.804), and traditional (0.754). The largest mean absolute residuals are calm (1.070), resilient (1.033), emotional (0.940), dominant (0.927), stoic (0.926), reserved (0.923), assertive (0.908), and neurotic (0.903). These are descriptive rankings, not evidence for a new translation.

The 12-trait view is not uniformly cleaner: several 12-trait pairs have high shape similarity, but MFamily_D and other pairs retain large offsets. Across traits, residual signs and magnitudes are not explained by one global offset. The pattern is a mixture of trait-specific offsets and cluster-specific/inconsistent residuals.

## Interpretation

The visuals make the two-level result easy to inspect: the 12-trait bridge carries more coherent matched-profile shape than the full 45-trait bridge, while the extra 33 direct mappings add heterogeneous residual structure. This supports using the 12 traits as a cleaner descriptive vocabulary for aggregate profile comparison.

That does not contradict the Rosetta **WEAK / ABSENT** result. The Rosetta test asked whether a low-complexity transformation learned from matched profiles could improve held-out prediction beyond identity. Even when matched profiles visibly resemble one another—and even when the restricted 12-trait profiles are cleaner—small, irregular, and trait/cluster-dependent residuals are not reliably learnable with only four matched families per K. Identity can therefore beat a learned translation without implying that the profiles are unrelated.

## Hypothesis

The 12-trait bridge may be a better candidate vocabulary for a future, separately frozen prospective validation. This visualization does not rescue V1, establish an individual-level bridge, or justify fitting a more flexible transform post hoc.

## Unknown

Whether the descriptive 12-trait improvement generalizes to another aggregate profile bank, model, human cohort, or individual-level data remains unknown. No human respondent records were loaded or committed for this visual layer.
