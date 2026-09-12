# Axis-specific Qwen trait markers and purity-filtered SAPA inventory

Date: 2026-09-12  
Status: completed at the requested inventory stopping point  
Model: Qwen/Qwen3-32B only

## Executive comparison

The frozen axis-specificity rule retains **88 of 328 signed association-family memberships (26.8%)**. Because a marker must be dominated by one target axis, these are also 88 unique traits. PC1 retains 60 markers across its two poles, PC2 retains 13, PC3 retains 15, and PC4-PC6 retain none. The result is a substantial contraction of the original strong-correlation families, especially on PC2 and PC3; it does not erase the original association analysis or imply that removed cross-loading traits are invalid.

The retained human inventory contains **22 unique SAPA constructs/item candidates and 195 unique questionnaire items**. Three signed families have at least one strong SAPA family match, three have partial matches but no strong whole-family match, and six mechanically empty primary-marker families have no proposed counterpart. This is measurement availability and semantic interpretation only, not evidence of human/model equivalence.

## Frozen method

The authoritative inputs are the previously saved 1,440 Qwen trait-PC Pearson/Spearman associations. The original association family remains `|r| >= .50`, within-PC BH-FDR `q < .01`, and prior 2,000-bootstrap sign stability `>= .95`.

For every trait-target pair, specificity uses all six supported Qwen axes:

`axis purity = r_target² / sum(r_PC1² ... r_PC6²)`

The primary axis-specific marker rule, frozen before result inspection, additionally requires the target to be the trait's largest absolute PC1-PC6 correlation, 2,000-bootstrap probability of target dominance `>= .95`, and observed axis purity `>= .70`. PC1-PC3 remain the strict core; PC4-PC6 remain supported secondary/provisional axes. Sensitivity cells cross purity `.60/.70/.80` with bootstrap-dominance probability `.90/.95/.99`.

The PC scores are mutually uncorrelated to maximum absolute off-diagonal `4.86e-16`. Six-PC communality matches the multiple R² from regressing each standardized trait-role score on standardized PC1-PC6 to maximum absolute error `9.99e-16`, validating the purity denominator. Saved correlations reproduce from the role-level matrix to maximum absolute error below `3e-15`; that recomputation was verification, not a new association analysis.

## Signed-family results

| PC/pole | Original n | Pure n | Retained | Median purity: original → retained | Strongest / purest retained marker | SAPA counterpart summary |
|---|---:|---:|---:|---:|---|---|
| PC1 positive | 47 | 12 | 25.5% | .595 → .786 | transparent (`r=.987`, purity=.981) / transparent | Partial Intellect; Orderliness, Cautiousness, Sincerity facets; one secular item |
| PC1 negative | 123 | 48 | 39.0% | .626 → .819 | narrative (`r=-.980`, purity=.972) / narrative | Strong Openness aspect; partial Expressiveness; Imagination, Artistic Interests, Absorption, Excitement Seeking components |
| PC2 positive | 31 | 3 | 9.7% | .398 → .879 | experiential (`r=.942`, purity=.946) / experiential | Partial Inquisitiveness and Adventurousness; no whole-family scale for practical experiential inquiry |
| PC2 negative | 44 | 10 | 22.7% | .512 → .825 | introverted (`r=-.954`, purity=.937) / introverted | Partial low Extraversion, Intellect, and Traditionalism; compound rather than unitary match |
| PC3 positive | 42 | 7 | 16.7% | .439 → .836 | callous (`r=.936`, purity=.901) / callous | Strong low Agreeableness; partial Aggression; low Compassion/Trust and Social Potency components |
| PC3 negative | 31 | 8 | 25.8% | .510 → .802 | benevolent (`r=-.948`, purity=.926) / nurturing (purity=.938) | Strong Compassion and Agreeableness; Altruism and Cheerfulness components |
| PC4 positive | 2 | 0 | 0% | .324 → — | none | No primary pure-family counterpart |
| PC4 negative | 6 | 0 | 0% | .370 → — | none | No primary pure-family counterpart |
| PC5 positive | 1 | 0 | 0% | .419 → — | none | No primary pure-family counterpart |
| PC5 negative | 0 | 0 | — | — | none | No counterpart to an empty family |
| PC6 positive | 0 | 0 | — | — | none | No counterpart to an empty family |
| PC6 negative | 1 | 0 | 0% | .423 → — | none | No primary pure-family counterpart |

### PC1

The positive family contracts from a broad 47-trait regulation/analysis cluster to 12 explicit empirical-analytic markers: transparent, factual, analytical, methodical, secular, data-driven, rationalist, educational, quantitative, utilitarian, cautious, and problem-solving. Conscientious, stoic, meticulous, serious, and perfectionist are strong PC1 associations but are more strongly associated with PC2 or otherwise cross-loading; the filtered human inventory therefore shifts away from broad Conscientiousness and toward partial Intellect plus method/order/caution facets. No SAPA scale jointly measures factual, transparent, secular, data-driven communication.

The negative family remains the largest pure family, but contracts from 123 to 48 markers. Its core is narrative, romantic, poetic, metaphorical, dramatic, enigmatic, ethereal, rhetorical, artistic, mystical, theatrical, spontaneous, intuitive, spiritual, creative, and related expressive/imaginative markers. The strong SAPA match is the Openness aspect, supplemented by Expressiveness, Imagination, Artistic Interests, Absorption, and Excitement Seeking; much of the antagonistic and generic affective tail is removed as diffuse or non-target-dominant.

Important strong but non-pure examples include calm/reserved/dispassionate on the positive pole (target-dominant but diffuse across PC2/PC3) and condescending/ironic/passive-aggressive plus cruel/acerbic on the negative pole (diffuse or more dominated by PC3).

### PC2

The positive pole contracts from 31 traits to experiential, practical, and inquisitive. The result has high median purity (.879), but available human scales split it: Inquisitiveness measures inquiry and Adventurousness measures direct experience; neither directly measures pragmatic application as a whole. Sociability, neuroticism, adaptability, and impulsivity-associated traits in the original family mostly cross-load on PC1 or PC3.

The negative pole retains introverted, ritualistic, pensive, theoretical, abstract, reverent, conceptual, principled, solemn, and erudite. It is semantically compound. Low Extraversion covers inwardness, Intellect covers theoretical/abstract thought, and Traditionalism covers only ritual/reverence/principle. Formal, big-picture, perfectionist, technical, and strategic are important strong associations but fail the primary specificity layer.

### PC3

The positive pole contracts to callous, cynical, pessimistic, vindictive, blunt, dominant, and skeptical. This yields a cleaner human-side antagonism inventory: low Agreeableness is the strong whole-family candidate, while Aggression, low Compassion, low Trust, and Social Potency cover distinct components. Confrontational, competitive, cruel, paranoid, rebellious, and manipulative remain important strong associations but are diffuse or more dominated by PC1.

The negative pole retains benevolent, nurturing, supportive, deferential, optimistic, altruistic, chill, and inspirational. Compassion and broad Agreeableness are strong available matches; Altruism and Cheerfulness capture narrower portions. Agreeable itself fails the pure-marker rule because of PC1 cross-loading, yet the full filtered family still has a strong construct-level Agreeableness match. This illustrates why trait-marker specificity and human construct matching are distinct judgments.

### PC4-PC6

No PC4-PC6 signed family has a primary marker under the frozen `.70/.95` rule. This means **no primary pure markers**, not no meaningful structure.

- PC4 positive: understated is an exploratory target-dominant trait with `|r| >= .30`, but purity is below the primary threshold; avoidant is more dominated by PC1.
- PC4 negative: holistic, systems-thinker, generous, progressive, and interdisciplinary are exploratory target-dominant moderate-strength candidates; the original strong members remain diffuse or cross-load on PC6/PC3/PC1.
- PC5 positive: divergent is target-dominant but diffuse, with substantial PC6 structure.
- PC5 negative and PC6 positive: no original `.50` association-family members.
- PC6 negative: systems-thinker is more strongly associated with PC4, so it is non-target-dominant for PC6.

These exploratory lists are stored separately in the family-comparison table and are not mixed with the primary marker set or SAPA mapping.

## Cross-loading classification and sensitivity

Among the 328 original family memberships, 88 are `AXIS_SPECIFIC_STRONG`, 150 are `TARGET_DOMINANT_BUT_DIFFUSE`, and 90 are `NON_TARGET_DOMINANT`. No row falls into the residual bootstrap-only `STRONG_CROSS_LOADING` class: every original-family row with observed target dominance and purity at least .70 also clears the .95 bootstrap-dominance threshold. Cross-loading remains scientifically visible in the classification table rather than being deleted.

At a `.60` purity threshold with `.95` dominance probability, the signed PC1-PC3 counts are 23/69, 7/15, and 9/11. At `.80/.95`, they are 5/27, 2/7, and 5/5. PC4-PC6 remain at zero across the reported primary-family sensitivity cells.

## Strength × purity and Pareto view

`qwen_axis_specificity_strength_purity.png` and its SVG source show all 240 traits per PC, distinguish original strong-family cross-loaders from primary markers, and label the top associations and retained markers. The Pareto table contains the traits for which no alternative is both stronger and purer. These displays are diagnostics; neither strength nor purity alone establishes a human psychological construct.

## Existing editorial composites

The exact five documented three-trait visualization groups were read from `persona_trait_ridge_plots/run_persona_trait_ridges.py` and scored as unweighted means of their canonical raw Qwen trait affinities. This secondary check did not affect individual-marker selection.

| Composite | Constituents | Best PC | r | Purity | Max off-axis | Gap |
|---|---|---|---:|---:|---:|---:|
| Exploration | creative, abstract, curious | PC1 | -.756 | .590 | .368 (PC4) | .388 |
| Response | reactive, adaptable, practical | PC2 | .854 | .741 | .414 (PC1) | .441 |
| Scrutiny | skeptical, analytical, conscientious | PC1 | .827 | .692 | .460 (PC2) | .367 |
| Challenge | rebellious, competitive, manipulative | PC1 | -.797 | .639 | .480 (PC3) | .316 |
| Affiliation | empathetic, agreeable, altruistic | PC3 | **-.970** | **.966** | .127 (PC1) | **.843** |

Thus the visual impression is numerically supported: among the documented editorial composites, Affiliation is exceptionally PC3-specific within PC1-PC6. It is still an editorial same-space composite, not an independently measured human factor.

## Purity-filtered SAPA inventory

The neutral reviewer packet was frozen before human judgments and shows only neutral family IDs, marker names/definitions, target correlations, purity, dominance gaps, and marker-derived descriptions. It omits PC/pole labels, roles/personas, prior PC interpretations, AA-2/AA-7 results, and prior human match labels. Judgments use the unchanged full 126-construct human library plus a single item-only fallback.

There are 31 judgment rows: 4 strong, 8 partial, 12 facet/subcomponent, 1 item-only, and 6 no-match rows. The 25 nonempty proposals contain 22 unique human construct/item IDs and 195 unique SAPA items. Three constructs recur across two signed families (Agreeableness, Compassion, and Intellect); 44 items recur across signed families, with maximum family reuse of three. Reuse is exposed in the judgment table.

Relative to the prior broad-family inventory, the most material changes are:

- PC1 positive drops broad Conscientiousness/HEXACO organization-perfection-prudence candidates and adds narrower Orderliness, Cautiousness, Sincerity, and one secular item.
- PC1 negative retains Openness/Expressiveness/Absorption but replaces broad domain and creativity/unconventionality entries with explicit Imagination, Artistic Interests, and Excitement Seeking facets.
- PC2 positive shrinks from five candidates to two partial components.
- PC3 retains Agreeableness at construct level on both poles, while its facet inventory becomes more specifically Compassion/Trust/Social Potency/Aggression versus Compassion/Altruism/Cheerfulness.
- All prior PC4-PC6 candidates are withheld from the primary purity-filtered inventory because no primary marker survives.

Exact retained, dropped, newly selected, status-change, item-count, and description comparisons are in `prior_vs_axis_specific_human_inventory_comparison.csv`.

## Epistemic status

### Observed

- Saved Qwen trait-PC correlations, derived strength/specificity metrics, bootstrap dominance, threshold membership, cross-loading classes, and documented SAPA construct/item availability.
- The primary marker set is a strict subset of the prior association families.
- The Affiliation editorial composite has PC3 correlation `-.970` and six-PC purity `.966`.

### Interpretation

- Primary markers are especially clean indicators for interpreting one Qwen PC within the supported six-PC subspace.
- Requiring specificity makes several human inventories narrower and more component-focused, especially for PC1 positive, PC2, and PC3.
- PC1 negative and both PC3 poles retain coherent construct-level human candidates after filtering.

### Hypothesis

- Any proposal that a measured human construct and a Qwen PC express a shared latent property.

### Unknown

- Human/model equivalence, respondent-level quantitative correspondence, causal mechanisms, behavioral realization, and cross-model generalization.

## Provenance and stopping point

Source model-side data are the existing Qwen/Qwen3-32B 275-role by 240-trait activation-cosine matrix and saved Qwen PC1-PC6 role coordinates. Human-side metadata are the unchanged 126-construct library and 696-item SAPA dictionary. No respondent row was loaded, scored, imputed, or projected.

This report is the requested stopping point. It does not score humans, run IRT/FIML, project respondents, compare human distributions, compare Qwen with Llama or Gemma, use AA-7 alignment, test human/model correspondence, or select a next experiment.
