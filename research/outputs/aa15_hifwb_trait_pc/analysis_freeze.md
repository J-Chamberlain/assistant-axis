# AA-15 analysis and extraction freeze · version 1 · 2026-09-16

Frozen before new HiFWB activations or their projections are inspected. This
is a **prospective analogue**, not an exact replication of the historical
trait-vector generation. Its boundary is documented in
`aa14_extraction_provenance_erratum.md`.

## Inputs and orientation

- Frozen 13 DIRECT HiFWB items: byte-identical
  `research/outputs/sapa_hifwb_reproducibility/wellbeing_item_freeze.csv`,
  SHA256 `dcac8f8d2e82c6fa337a8c34472b8b1901d7c709823618dd4bf614ed885a46e0`.
  Four CLOSE auxiliary rows are not projected.
- Exact wording and response-key direction are retained in
  `hifwb_indicator_inventory.csv`. Six negative-keyed items are represented
  verbatim in `exact_survey` and grammatically prefixed in
  `minimal_first_person`, but **never algebraically negated as vectors**.
  Each gets a separately written affirmative wellbeing pole.
- The headline formulation is `primary_positive_pole` for all 13 items, so
  positive-prompt minus negative-prompt consistently means eliciting the
  positive-wellbeing pole. `exact_survey` and `minimal_first_person` are
  sensitivity variants. Their positive-minus-negative vectors represent
  endorsement of the original item, including *negative wellbeing* for
  reverse-keyed items, and must not be pooled with primary vectors without
  explicit semantic orientation.
- `build_prompt_freeze.py` deterministically produces all 195 system prompt
  pairs (13 items × 3 formulations × 5 wording pairs), eight fixed user
  questions, and the wording audit. The fixed question IDs from
  `data/extraction_questions.jsonl` are 0, 3, 10, 24, 31, 36, 37, 51;
  their source SHA256 is
  `31650b9a55d6b827d29ec2ee89034c7efd454672779b3ad9d7c8c4e9ea14f69e`.
  These questions cover neutral and wellbeing-adjacent topics but are not
  the original trait-specific 40-question banks.

## Prospective representation protocol

- Model IDs: `Qwen/Qwen3-32B`, `meta-llama/Llama-3.3-70B-Instruct`,
  `google/gemma-2-27b-it`; Qwen thinking disabled.
- For every item × formulation × prompt pair × question, generate both a
  positive-elicited and a negative-elicited **model response**. This is
  5 × 8 × 2 = 80 responses per item/formulation, 3,120 per model and 9,360
  across three models. No model response text or raw activation tensor will
  be committed. Generation temperature 0, top_p 1, maximum 192 new tokens,
  and fixed seed 150015. The original trait release's generation settings
  and response selection are unavailable; these settings are new.
- Re-run the *complete conversation* through the model with decoder-block
  forward hooks, capturing post-MLP residual outputs at **every** block:
  64×5120 Qwen, 80×8192 Llama, 46×4608 Gemma. Mean over assistant response
  tokens only, not system or user tokens. Follow the repository's
  `ActivationExtractor` / `SpanMapper.map_spans` convention. Keep Qwen
  thinking disabled in the extraction chat template as well.
- Mean response-token activations across the 40 positive and 40 negative
  responses separately at each layer, then subtract negative from positive.
  Include nonempty refusals but flag/count them; missing/empty responses are
  excluded symmetrically by paired unit. If >5% of units fail or a polarity
  is missing for an item/formulation/model, withhold that coordinate from
  headline interpretation rather than silently filling it.
- Save a local uncommitted all-layer contrast tensor per item/formulation
  with source hashes and counts; export only compact derived coordinates and
  diagnostics. Average all saved layer rows for the AA-14-compatible feature
  vector. **Never** select Qwen layer 48 for this fit or projection.
- Subtract the model-specific **frozen AA-14 trait mean** and right-multiply
  by its unchanged trait-PC directions. Never refit PCA or concatenate raw
  activation coordinates across models. Retain all available 239 PCs and
  show default PC1/PC2/PC3. The centering/projection identity and residual
  norm are verified against the compact exported results.

## Prespecified checks and decision rules

- Report every coordinate, norm, first-20 captured fraction, residual,
  20D/full-rank trait distances, nearest/farthest traits, centroid and
  direction, and the same AA-14 fifth-neighbor OOD reference. Report the
  original-wording and minimal-wording sensitivity separately.
- Bootstrap 500 paired prompt×question units (seed 150015) for coordinate
  and centroid uncertainty. This quantifies prompt-set sensitivity, not
  independent extraction or model-run uncertainty. Compare formulation
  subspace and item-specific cosine/rank stability; flag low agreement.
- Compare median pairwise 20D indicator distance against 5,000 draws of 13
  distinct traits, with a vector-norm-matched bank as primary. If the item
  norm range has no adequate trait matches, report failure of matching and
  use the unconditioned null only as descriptive. Never claim a tight
  wellbeing cluster from an unmatched null alone.
- Permit a single centroid direction only if (i) norm-matched compactness
  one-sided p<0.05, (ii) at least 10/13 primary vectors have positive
  projection along the leave-one-out centroid direction, (iii) median
  raw cosine to same-pole variants among the seven directly keyed items is
  ≥0.8 and median raw cosine to original negative-pole variants among the
  six reverse-keyed items is ≤-0.8, and (iv) the bootstrap 5th-percentile
  centroid-direction cosine to the full fit is ≥0.8. The negative-pole
  comparison is a diagnostic expectation, not an algebraic reversal or a
  replacement of the saved vector. Otherwise report multiple/unresolved
  regions; a centroid may still be tabulated descriptively.
- Align 20D model-local trait-score spaces to Qwen using AA-14's shared 240
  trait labels and orthogonal Procrustes, fitted on traits only. Do not
  match PC numbers or use HiFWB to estimate transforms. Permute item labels
  5,000 times for cross-model item correspondence. Compare centroids,
  neighborhoods, and trait/persona rankings only after alignment.
- Human SAPA crosswalk uses the existing AA-10 internal HiFWB PC1 fraction
  0.522552 and AA-13 broad-human-PC associations (PC1 r=-0.00386; strongest
  observed PC4 r=0.274142). These are **human covariance** coordinates,
  distinct from the present model activation coordinates. No new respondent
  or matched-trait SAPA projection is allowed in AA-15.

No outcome conclusion or public viewer layer is valid until all three models
and all three prompt formulations have verified activation vectors. If GPU
access is unavailable, publish this freeze and provenance audit as partial
work, and preserve the AA-14 public viewer unchanged.
