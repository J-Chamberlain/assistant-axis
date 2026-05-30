# Trait-Space Axis Interpretation

Model used for analysis scripting: GPT-5.5.

## Data Sources

- Trait vectors: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/qwen-3-32b/trait_vectors`
- Role vectors for comparison: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/downloads/hf_vectors/qwen-3-32b/role_vectors`
- Persona geometry data: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/visualizations/geometry_viz_data.json`
- Prior persona-trait cosine matrix: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv`
- Prior trait predictor coefficients: `/Users/alfred/Projects/Substack/mechonistic_interpretability/assistant-axis/research/outputs/trait_persona_prediction/pc_trait_predictor_coefficients.csv`

This analysis used raw activation vectors for trait PCA. Each Qwen/Qwen3-32B layer-48 trait tensor has shape `[64, 5120]`; each tensor was mean-pooled to one 5120-D vector before PCA and cosine comparisons. Role vectors were used only as comparison/reference.

## Observed Numerical Results

- Trait count: 240
- Persona count for comparison: 275
- Trait PC explained variance: PC1=0.353, PC2=0.168, PC3=0.134, cumulative=0.655.
- Absolute cosine alignment between trait and persona PCA directions: PC1=0.681, PC2=0.194, PC3=0.065.
- Correlation between trait PCA coordinates and prior persona-PC trait coefficients is strongest for: trait_pc2 vs persona PC3 coefficient, Pearson=0.074.

## Trait PC Rankings

### Trait PC1

Positive: serious (112.399), solemn (103.550), formal (96.817), calm (96.156), conscientious (94.651), serene (87.372), patient (87.032), methodical (86.005), dispassionate (83.523), meticulous (83.501)

Negative: flippant (-94.557), irreverent (-89.720), goofy (-85.208), sassy (-85.036), edgy (-77.482), witty (-76.366), flirty (-75.988), entertaining (-75.802), temperamental (-74.415), sardonic (-72.886)

Near zero examples: libertarian (0.614), paranoid (-0.948), pessimistic (1.158), fatalistic (1.303), socratic (-2.331), dogmatic (-2.384), dominant (2.704), eclectic (3.333), futuristic (3.518), confident (-3.623)

### Trait PC2

Positive: callous (75.501), detached (69.205), technical (61.411), dispassionate (60.161), esoteric (59.450), acerbic (55.420), cruel (55.419), hostile (51.483), savage (51.271), misanthropic (50.394)

Negative: nurturing (-74.492), accessible (-73.668), empathetic (-66.480), emotional (-66.479), benevolent (-66.264), naive (-63.379), supportive (-58.606), meditative (-55.580), chill (-54.838), optimistic (-54.097)

Near zero examples: progressive (-0.053), epicurean (-0.167), theatrical (0.234), relativist (-0.246), impulsive (0.593), independent (-0.652), avoidant (1.036), concise (-1.070), melodramatic (-1.117), goofy (-1.253)

### Trait PC3

Positive: grounded (73.476), practical (66.037), understated (58.241), accessible (57.036), efficient (53.710), concise (52.264), nonchalant (52.198), avoidant (51.909), casual (51.040), literal (49.011)

Negative: eloquent (-79.872), bombastic (-74.316), cryptic (-68.783), poetic (-62.054), theatrical (-62.026), dramatic (-59.611), philosophical (-59.108), melodramatic (-56.591), metaphorical (-55.811), esoteric (-54.544)

Near zero examples: ironic (0.096), skeptical (0.346), competitive (-0.688), structuralist (-0.959), absolutist (1.045), nurturing (-1.412), manic (1.683), individualistic (-1.822), arrogant (-1.989), deontological (2.067)

## Streamlined Axis Interpretations

**Trait PC1 interpretation:** The ranking separates formal, serious, calm, conscientious, patient, and methodical traits from flippant, irreverent, goofy, sassy, edgy, witty, entertaining, temperamental, and sardonic traits. A concise paper-ready label is **controlled seriousness / formal composure versus playful irreverence / expressive volatility**. It overlaps moderately with persona PC1 direction in raw activation space, so it should not be treated as a one-to-one copy of the assistant-axis/cone interpretation. It does, however, support the broader claim that trait geometry supplies a strong basis for reconstructing persona placement.

**Trait PC2 interpretation:** The ranking separates callous, detached, technical, dispassionate, esoteric, acerbic, cruel, hostile, savage, and misanthropic traits from nurturing, accessible, empathetic, emotional, benevolent, naive, supportive, meditative, chill, and optimistic traits. A concise paper-ready label is **cold detachment / hard-edged abstraction versus warm accessibility / affiliative care**. The name-based abstraction/integration control correlates with trait PC2 at Pearson -0.089 / Spearman -0.088. This weakens any simple claim that trait PC2 independently recovers the current persona PC2 abstraction/integration interpretation; PC2 remains the least settled persona-axis interpretation.

**Trait PC3 interpretation:** The ranking separates grounded, practical, understated, accessible, efficient, concise, nonchalant, avoidant, casual, and literal traits from eloquent, bombastic, cryptic, poetic, theatrical, dramatic, philosophical, melodramatic, metaphorical, and esoteric traits. A concise paper-ready label is **plain practical groundedness versus ornate symbolic/theatrical expressivity**. The perturbation/stabilization control correlates with trait PC3 at Pearson -0.074 / Spearman -0.104, while moral valence correlates at Pearson 0.010 / Spearman -0.004. Trait PC3 therefore does not independently validate a clean perturbation-stabilization axis by itself, even though the prior persona-PC3 prediction subset favored perturbation/stabilization over moral valence.

## Comparison To Persona-Space Interpretations

- Persona PC1: careful evaluative/procedural certainty versus open symbolic possibility. Trait space shares only partial directional alignment with this axis, but the trait bank reconstructs persona PC1 almost perfectly through the persona-trait similarity profile.
- Persona PC2: abstraction/integration versus developmental/reactive immediacy. Trait PC2 does not cleanly resolve this interpretation; the observed trait ranking is more strongly about cold detachment versus affiliative warmth.
- Persona PC3: perturbative/interventionist versus stabilizing/nurturing. Trait PC3 is not reducible to this framing; direct trait PC3 is more lexical/register-like, contrasting plain grounded practicality with ornate symbolic/theatrical expressivity.

## Cone / Constraint Tests

The trait-space cone test bins traits by trait PC1 and measures secondary spread in PC2/PC3.

- Lowest-PC1 vs highest-PC1 radial spread ratio: 0.863
- Lowest-PC1 vs highest-PC1 convex hull area ratio: 0.9833534355526483
- Secondary variation expands as PC1 decreases: False

The trait-space result is therefore not consistent with the same simple cone/constraint pattern observed in persona space. See `trait_space_cone_tests.json` and `trait_space_cone_plots.png` for bin-level values.

## Diagnostic Trait Neighborhoods

Diagnostic persona neighborhoods were read from the prior persona-trait cosine matrix, not recomputed. The exported table includes nearest positive and negative trait profiles for assistant, evaluator, auditor, poet, bard, counselor, therapist, spy, demon, warrior, romantic, elder, and narrator.

## Interpretations

Trait-space analysis strengthens the layered interpretation in one specific sense: raw trait vectors occupy the same activation space and provide a highly predictive coordinate basis for persona PCA placement. It does not prove that the paper-ready persona axes are simply trait axes. Direct trait-only PCA partially reorganizes the structure, especially for PC2 and PC3.

## Hypotheses

- Trait vectors may act as a dense local basis for role/persona geometry rather than as independent psychological dimensions.
- Persona axes may emerge from interactions among trait-like, procedural, semantic, and lexical/register structure rather than any single source.
- PC2 likely needs a narrower validation design; trait-only PCA does not settle it.

## Unknowns / Limitations

- The rubric tests in this report are trait-name controls, not independent human or model annotation.
- PCA signs are conventional; interpretation uses rankings and absolute directional comparisons.
- Same-space near-ceiling reconstruction can reflect shared vector provenance and high-dimensional basis coverage.
- Trait PC axes are not guaranteed to align with persona PC axes because PCA was fit on a different point cloud.

## Recommended Next Experiment

Run a reduced, preregistered trait taxonomy test: choose a small non-overlapping set of perturbation/stabilization, moral-valence, abstraction/integration, and professionalism traits before looking at coefficients, then test which subsets predict held-out persona PC directions and within-cluster rankings.
