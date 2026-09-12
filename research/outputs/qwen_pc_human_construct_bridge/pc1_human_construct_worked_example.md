# PC1 worked example: from a Qwen latent axis to a human-construct hierarchy

Status: discovery only; not cross-model validated  
Discovery model: Qwen/Qwen3-32B  
Rubric: `human_construct_match_rubric.md` version 1.0, frozen before candidate adjudication

## Conceptual answer

Yes. The earlier narrowing to 12 moderate-or-better *narrow model-trait proxies* excluded broad constructs that are useful at the level of a latent principal component. In particular, that filtering does **not** establish that Conscientiousness is a poor analogue for Qwen PC1.

The narrow proxy named `conscientious` was evaluated as a three-item candidate measurement that needed to remain distinct from neighboring retained model-trait proxies. It showed coherent human responses and source-scale convergence, but it correlated strongly with the proxy called `methodical` (`|r| = 0.750`) and was therefore labeled `REDUNDANT / BROAD` for the narrow-feature-matrix purpose. That is an appropriate penalty when the aim is differentiated narrow proxies. It is not an appropriate reason to discard the established 20- or 60-item Conscientiousness domain when the target is a broad PC.

## Observed Qwen PC1 signature

- PC1 explains 31.595% of variation among the 275 saved Qwen role vectors. Its bootstrap loading cosine is 0.994 median and 0.981 at q05, so it is a core, individually stable axis in the existing inventory.
- Its strongest positive trait affinities include `transparent` (r=0.987), `factual` (0.946), `analytical` (0.938), `methodical` (0.903), `data_driven` (0.875), `cautious` (0.841), and `calm` (0.830).
- Its strongest negative trait affinities include `narrative` (-0.980), `romantic` (-0.976), `poetic` (-0.976), `metaphorical` (-0.974), `dramatic` (-0.969), `enigmatic` (-0.969), `ethereal` (-0.961), and `artistic` (-0.942).
- The positive role pole begins with auditor, examiner, evaluator, supervisor, validator, statistician, screener, lawyer, researcher, planner, reviewer, and grader. The negative pole begins with leviathan, poet, wraith, caveman, revenant, bard, prophet, ghost, eldritch, vampire, pirate, and demon.
- The Qwen-only externally anchored strict Big Five directions correlate with PC1 as follows: Extraversion -0.817, Neuroticism -0.758, Conscientiousness +0.748, Openness -0.704, and Agreeableness +0.424.
- In prior focused activation evidence, accountability wording shifted PC1 positively relative to determination (mean +3.297; 95% interval 1.574 to 5.020) and arithmetic/checking (mean +9.551; 7.592 to 11.510). Those are model-side intervention results, not human evidence.

## Candidate comparison under the frozen rubric

| Candidate | Level | Polarity | Status | What it captures | Principal mismatch |
|---|---|---:|---|---|---|
| Conscientiousness | domain | positive | STRONG CANDIDATE | organized, persistent, standards-oriented, controlled goal pursuit | does not explain low-PC1 expressive/mythic possibility or the strong Extraversion/Openness opposition |
| Stability | metatrait | positive | STRONG CANDIDATE | joint high Conscientiousness/Agreeableness and low Neuroticism; maintained goal, affective, and social organization | does not specifically capture analytical/secular/transparent content |
| Plasticity | metatrait | negative | STRONG CANDIDATE | joint Extraversion/Openness, exploration, novelty, expression, and the possibility-expanding pole | mythic/nonhuman role instructions are not measurements of human exploratory behavior |
| Orderliness | aspect | positive | FACET / SUBCOMPONENT | structure, routine, rules, checking, and procedural constraint | too narrow for competence, achievement, and accountability |
| Industriousness | aspect | positive | FACET / SUBCOMPONENT | effort, persistence, efficiency, and task execution | does not cover order or the negative pole |
| Achievement Striving | facet | positive | FACET / SUBCOMPONENT | explicit standards and pursuit of excellence | institutional evaluator roles need not imply personal ambition |
| Self-Discipline | facet | positive | FACET / SUBCOMPONENT | initiation and persistence at controlled work | generic persistence is not external legibility |
| Dutifulness | facet | positive | FACET / SUBCOMPONENT | obligations, rules, and accountability | PC1 is not simply compliance or morality |
| Self-Efficacy | facet | positive | PLAUSIBLE PARTIAL CANDIDATE | expertise and competent task completion | confidence is not a leading trait signal |
| Emotional Stability | domain | positive | PLAUSIBLE PARTIAL CANDIDATE | calmness and the strong negative Neuroticism relation | misses analysis, standards, structure, and symbolic possibility |
| Assertiveness | aspect | negative | BROAD BUT NONSPECIFIC | one possible part of the negative Extraversion relation | high-PC1 supervisors, lawyers, and evaluators can be agentic |
| Need for Cognitive Closure | domain | positive | POOR MATCH | surface resemblance to certainty and order | high PC1 is secular/factual, whereas dogmatic/zealous content is negative; the scale is absent from SAPA |

All six evidence dimensions and counterevidence for these rows are preserved in `qwen_pc_human_construct_candidates.csv`.

## Interpretation

The best human hierarchy is not “PC1 equals Conscientiousness.” It is:

- broad contrast: **higher Stability and lower Plasticity**;
- strongest single established domain: **Conscientiousness**;
- relevant subordinate aspects/facets: **Orderliness, Industriousness, Achievement Striving, Self-Discipline, and Dutifulness**;
- Qwen-specific residual: **factual/transparent analytical practice under externally legible standards**, including the focused accountability effect.

This hierarchy handles broad-construct overlap as meaningful structure. Conscientiousness may overlap Orderliness and Industriousness because those are subordinate measures, not rival labels that must be made independent.

## Human measurement availability

All retained hierarchy members are available in the released SAPA item pool with official scoring keys. Pairwise-complete standardized alpha is 0.916 for the 20-item IPIP Conscientiousness key, 0.718 for the 20-item Stability key, 0.906 for the 20-item Plasticity key, 0.816 for Orderliness, 0.869 for Industriousness, 0.846 for Achievement Striving, 0.902 for Self-Discipline, and 0.814 for Dutifulness.

Planned missingness still prevents ordinary complete-key scoring: the median respondent sees three of the 20 Conscientiousness items, two of each metatrait's 20 items, and one or two items from each 10-item facet. No respondent sees all 20 Conscientiousness, Stability, or Plasticity items. This supports covariance/latent or partial-information scoring in later work, not complete-case scale scoring.

## Hypothesis and unknowns

Hypothesis: a broad high-Stability/low-Plasticity organization, with Conscientiousness and its facets prominent, may provide a human-psychological analogue for part of Qwen PC1.

Unknown: whether human scale variation corresponds to Qwen PC1, whether the same latent construct exists in the two systems, whether another model recovers the frozen pattern, and whether the Qwen-specific accountability/standards residual has any human psychometric analogue.

No human respondent was projected into Qwen geometry in producing this worked example.
