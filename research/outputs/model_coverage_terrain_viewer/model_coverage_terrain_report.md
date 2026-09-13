# AA-12 follow-up 6 — Model-only persona-space coverage terrain

## Result in one paragraph

The viewer makes the sampled territory of the same 275 curated roles inspectable in the frozen native PC1–PC3 geometry of Qwen 3 32B, LLaMA 3.3 70B, and Gemma 2 27B. A full-covariance Scott Gaussian KDE supplies role-only sample-occupancy boundaries, while inverse density and standardized-PC 10-neighbor distances expose locally sparse sampled roles. The clearest recurring descriptive pattern is a dense professional/informational region associated with frozen MFamily_A and a sparse peripheral set containing developmental/literal and several disruptive or archaic roles. The overall density ordering is robust to the preregistered 0.75×–1.25× bandwidth range, although a few extreme-decile memberships change. These are properties of the selected role inventory and smoothing rule—not population probabilities, persona prevalence, dynamical stability, accessibility, or evidence about humans.

## Scope and frozen inputs

This is a model-only coverage instrument. No SAPA, NLSY97, human latent profile, human 45/12-trait profile, human/model similarity, or human-profile ID entered the analysis.

Native coordinates come from the frozen `research/outputs/extended_persona_pca/viewer_data.json`; its PC1–PC3 scores reproduce the full-PCA arrays at maximum absolute error below `1e-8` and the canonical Qwen geometry table within `2e-6`. Each model contains exactly 275 unique roles, and the role-label sets are identical.

Frozen family memberships come from `research/outputs/crossmodel_cluster_reconciliation/consensus_family_roles.csv`. A–D remain broad candidate consensus families. E remains the small, resolution-sensitive family: it contains three LLaMA roles, four Gemma roles, and no Qwen role at the anchor solutions. No clustering or family definition changed.

The optional Qwen-only trait landmarks come from `research/geometry_tables/qwen_trait_pc_rankings.csv`. They are rendered as landmarks and excluded from every occupancy, density, sparsity, neighborhood, and coverage calculation.

## Terrain method

- Primary space: native, canonically oriented PC1–PC3 for each model separately.
- Density: `scipy.stats.gaussian_kde`, full covariance, Scott factor `0.448254` for N=275 and d=3.
- Grid: 36 points per axis, spanning observed extrema plus one marginal kernel SD on both sides.
- Coverage thresholds: role-location KDE quantiles targeting 50%, 80%, and 95% of sampled roles.
- Achieved sample fractions in every model: 138/275 = 50.18%, 220/275 = 80.00%, and 261/275 = 94.91%.
- Primary sparsity: inverse-KDE ordering reported as a within-model percentile from 0 (densest) to 100 (sparsest).
- Diagnostic sparsity/neighbors: mean distance to the 10 nearest roles after standardizing each native PC axis by its model-specific SD.
- Two-dimensional views: separate bivariate Scott KDEs for PC1×PC2, PC1×PC3, and PC2×PC3.
- Family envelopes: convex sampled-role envelopes only for model-specific family N≥10. They are not density or probability regions. E is points only.

The complete preregistered specification is in `coverage_terrain_method.md`, frozen at commit `5c2814f7554d26cfce97cb83fd0cda34ffbf2333` before terrain generation.

## Model-local occupancy descriptions

### Qwen 3 32B

The densest sampled roles are `generalist`, `publisher`, `librarian`, `journalist`, and `organizer`. The sparsest are `procrastinator`, `toddler`, `infant`, `fool`, and `romantic`, followed closely by `caveman`.

MFamily_A occupies the densest broad lobe (median density percentile 81.57) at positive native PC1 and slightly negative PC2. B is centered far into negative PC1/PC2 and is less densely sampled (median 37.23). C and D are both positive-PC2 peripheral regions, separated most visibly by native PC3: C is negative and D positive. Their median density percentiles are 22.99 and 24.45. This is sampled family placement, not a claim that the families are natural or exhaustive.

### LLaMA 3.3 70B

The densest sampled roles are `editor`, `technologist`, `designer`, `librarian`, and `geographer`. The sparsest are `infant`, `caveman`, `toddler`, `fool`, and `robot`; `procrastinator` is also in the sparsest eight.

MFamily_A is again the dense broad lobe (median density percentile 79.93). B and D are more peripheral (20.80 and 23.18), while C is intermediate (39.96). Native axes are LLaMA's own axes, so these positions must not be numerically overlaid with Qwen or Gemma. E's three roles occupy an exceptionally sparse sampled location (median density percentile 0.36) and remain points only.

### Gemma 2 27B

The densest sampled roles are `publisher`, `geographer`, `librarian`, `designer`, and `sociologist`. The sparsest are `caveman`, `toddler`, `fool`, `infant`, and `procrastinator`.

MFamily_A is again dense (median density percentile 79.74). B, C, and D become progressively more peripheral by their median density percentiles (40.51, 26.28, and 12.96). B is strongly negative on native PC1; C and D are positive on native PC2 and distinguished by native PC3. E's four roles lie at a very sparse sampled location (median density percentile 0.55) and remain points only.

## Recurring and model-specific coverage patterns

Five sparse roles recur in the bottom eight of all three model-local density rankings: `infant`, `toddler`, `caveman`, `fool`, and `procrastinator`. `publisher` and `librarian` recur among the densest roles in all three models. This recurrence is descriptive of a fixed curated vocabulary; it does not establish low/high population prevalence or representational accessibility.

Local neighborhood recurrence is real but modest rather than near-identical. With k=10 standardized-native-PC neighbors, mean pairwise Jaccard across the three model pairs is 0.221 and the median is 0.207. Qwen–Gemma is higher on average (0.279) than Qwen–LLaMA (0.193) or LLaMA–Gemma (0.192). `mystic` and `researcher` have the highest three-pair mean recurrence (0.545), followed by `validator` (0.508). These values show that some local topology recurs while much remains model-specific.

The viewer supports two careful comparison modes:

1. Linked native panels, which preserve each model's own coordinates and highlight the same selected role in all three.
2. A secondary display-aligned overlay using the already-frozen variance-standardized PC1–PC3 shared-role Procrustes transformations. It is visibly labeled non-native. Because it was fitted on the same 275 roles, it is a display aid rather than independent confirmation.

No algorithmic empty-voxel or gap candidates were declared. Low KDE fields can be explored neutrally in the viewer, but visible empty space is not labeled a basin, barrier, attractor, repellor, inaccessible state, or unstable state.

## Bandwidth sensitivity

Across 0.75× and 1.25× Scott bandwidths, density-rank Spearman correlation with the primary ordering is 0.983–0.989 for Qwen, 0.993–0.995 for LLaMA, and 0.992–0.995 for Gemma. Common-grid density-field correlations are 0.975–0.987.

The frozen ≥0.70 extreme-decile overlap rule passes both tails at both alternative bandwidths for Qwen. LLaMA's densest decile is just below the rule at 1.25× (Jaccard 0.697). Gemma's sparsest decile is just below it at 0.75× and its densest decile is just below it at 1.25× (both 0.697). Accordingly, the broad density terrain is smoothing-robust, while exact extreme-role membership should be inspected with the bandwidth panel rather than treated as fixed.

## Viewer guide

Open `model_coverage_terrain_viewer.html` locally. It is self-contained and embeds both Plotly and the frozen terrain payload.

Available modes:

- Persona points: the 275 raw sampled roles.
- Occupancy cloud: selectable 50/80/95% role-sample coverage surfaces.
- Sample density and sparsity: within-model percentile coloring.
- Consensus families: A–E coloring, core/majority/fringe hover metadata, and optional eligible family envelopes.
- Native 2D contours: PC1×PC2, PC1×PC3, and PC2×PC3.
- Linked native comparison: three separate model-local scenes.
- Display-aligned overlay: frozen shared-role display coordinates, explicitly non-native.
- Linked role inspection: exact role coordinates, density/sparsity ranks, family status, nearest roles, and cross-model neighborhood recurrence.
- Optional Qwen trait landmarks: searchable, limited to five displayed landmarks, and excluded from occupancy.

The central warning is deliberately persistent: **Coverage reflects the selected 275-role inventory. It is not a population probability distribution.**

## Verification

The browser suite passes 23 checks in Google Chrome 152, including real WebGL rendering via software SwiftShader, all model/view switches, 2D contours, three-scene native comparison, aligned-view labeling, family envelopes, shared-role selection, trait landmarks, layer toggles, and stale-trace exclusion. The numerical/scope suite passes 35 checks, including exact coordinate reproduction, family reproduction, coverage fractions, role-only density, Qwen-only trait isolation, small-family handling, self-contained HTML, rendered static files, no human/correspondence input, and a byte-identical deterministic rerun of all numerical source tables.

No GPU research compute was used; SwiftShader was used only to render the saved browser visualization during UI verification. No model inference, prompt generation, activation extraction, external model API, or RunPod work occurred.

## Epistemic status

**Observed:** saved role locations, frozen family membership, KDE values under the frozen estimator, within-model sparsity ranks, coverage thresholds, and local-neighborhood recurrence.

**Interpretation:** sampled occupancy terrain, recurring versus model-specific occupied regions, and candidate low-coverage areas for inspection.

**Hypothesis:** some sparse regions may later prove dynamically unstable or less behaviorally realizable.

**Unknown:** whether sparse regions reflect representational constraints or curated role selection; whether humans occupy sparse model territory; whether density relates to behavioral transitions; and whether any region admits a population-probability interpretation.

Human-data ingestion and projection methodology remain a separate future design question and were not begun here.
