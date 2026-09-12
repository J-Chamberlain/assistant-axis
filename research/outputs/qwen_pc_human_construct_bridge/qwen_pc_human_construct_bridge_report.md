# Qwen-first human-construct bridge

Generated: 2026-09-12  
Analysis model: GPT-5.5  
Discovery model: Qwen/Qwen3-32B only  
Status: **DISCOVERY ONLY — NO CROSS-MODEL VALIDATION YET — NO HUMAN RESPONDENT PROJECTION**

## Executive answer

Yes. The previous reduction to 12 moderate-or-better narrow SAPA proxies excluded broad constructs that are potentially useful for interpreting Qwen's latent dimensions. That reduction answered whether literal model-trait labels formed distinct narrow human measurements. It did not answer whether established domains, aspects, facets, or metatraits describe a broad Qwen PC.

The clearest corrections are:

- **PC1:** Conscientiousness remains a strong single-domain candidate despite exclusion of the narrow `conscientious` proxy. The fuller hierarchy is higher Stability and lower Plasticity, with Conscientiousness, Orderliness, Industriousness, Achievement Striving, Self-Discipline, and Dutifulness representing distinct subcomponents. A Qwen-specific accountability/external-standards residual remains.
- **PC3:** Agreeableness remains a strong domain-level candidate, with Compassion and Politeness as facets and Honesty-Humility, Aggression, Altruism, and Machiavellianism describing additional components. Agreeableness does not exhaust transgression, deception, technical intervention, or outsider register.
- **PC2:** no clean single human domain was identified. Low Stability/Control/Conscientiousness, higher Neuroticism/Extraversion, and lower Intellect each capture parts of a compound reactive/social-immediacy versus abstract/integrated pattern.
- **PC4-PC6:** only partial or facet-level mappings are defensible. PC4 is partly lower Openness/Intellect and higher Traditionalism; PC5 is partly Openness/Plasticity and divergent exploration; PC6 is partly higher Need for Cognitive Closure and lower Openness/Intellect, but the dedicated closure scale is not in SAPA and the axis retains a model-specific cross-ideological principled-absolutist component.

The frozen hypothesis file contains 37 PC-construct rows representing 28 distinct constructs. Thirty-six rows (27 distinct constructs) are directly measurable with released SAPA keys; one PC6 candidate, Need for Cognitive Closure, requires another human dataset. No Qwen coordinate was applied to a human respondent.

## Study boundary and firewall

This is bridge construction, not equivalence testing. Inputs to construct selection were limited to:

- a frozen Qwen-only PC1-PC6 signature;
- Qwen-only trait, role, cluster, stability, compact-set/conditional, blinded-interpretation, focused-activation, and externally anchored Big Five evidence;
- authoritative human construct definitions and the acquired SAPA scale/item inventory;
- human-only SAPA reliability and administration summaries.

No AA-7 result was used. No Llama or Gemma association, aligned direction, component, recurrence classification, or performance result was used to generate, rank, or freeze human constructs. The shared extended browser JSON was streamed until the exact top-level `qwen` object and only that object was parsed; shared CSVs were row-filtered before retaining values. The output manifest records this firewall.

## Phase A — genuinely separate Claude semantic review

### Reviewer disclosure

The supplied file is preserved byte-for-byte as `sapa_category3_blinded_review_judgments.csv` (SHA256 `71902fbe78fd4dec9742af8ca25a1c27dd9429263f3319a85937b85fd3a9a86a`). The reviewer was Claude Opus 5, Anthropic, on 2026-09-11. Claude reported no prior substantive project knowledge; located only the three requested review files; and did not inspect project state, claims, geometry, prior decisions, sparsity, occupations, NLSY97 outcomes, or downstream analyses. Claude reported no prohibited downstream information visible. Claude is an Anthropic-produced AI system, which is recorded as a structural conflict. The review is content adjudication, not psychometric validation.

### Agreement

Claude assigned 48 `ACCEPT_DIRECT`, 22 `ACCEPT_CLOSE`, 2 `DOWNGRADE_BROAD`, 4 `REJECT`, and 2 `AMBIGUOUS`; Codex assigned 45, 29, 1, 3, and 0 respectively.

- exact five-category agreement: 69/78 = 0.8846;
- unweighted Cohen's kappa: 0.7855;
- retained versus nonretained agreement: 74/78 = 0.9487, kappa 0.6422;
- direct versus all other decisions: 73/78 = 0.9359, kappa 0.8671;
- ordinal sensitivity after excluding the two Claude-ambiguous rows: linear weighted kappa 0.8468 and quadratic weighted kappa 0.8837.

A five-category weighted kappa is not treated as primary because `AMBIGUOUS` is not an ordinal point between semantic-strength decisions. The descriptive consensus contains 44 `CONSENSUS_DIRECT`, 21 `CONSENSUS_CLOSE`, 4 `CONSENSUS_NONRETAIN`, and 9 discordant rows.

### All nine disagreements

| Review ID | Trait | Codex | Claude |
|---|---|---|---|
| SAPA-C3-001 | risk_taking | ACCEPT_CLOSE | ACCEPT_DIRECT |
| SAPA-C3-011 | mercurial | ACCEPT_CLOSE | ACCEPT_DIRECT |
| SAPA-C3-012 | zealous | ACCEPT_CLOSE | ACCEPT_DIRECT |
| SAPA-C3-038 | mischievous | ACCEPT_CLOSE | REJECT |
| SAPA-C3-041 | disorganized | ACCEPT_CLOSE | DOWNGRADE_BROAD |
| SAPA-C3-043 | cautious | ACCEPT_CLOSE | ACCEPT_DIRECT |
| SAPA-C3-048 | independent | ACCEPT_CLOSE | AMBIGUOUS |
| SAPA-C3-050 | nonchalant | ACCEPT_CLOSE | AMBIGUOUS |
| SAPA-C3-059 | melancholic | ACCEPT_DIRECT | ACCEPT_CLOSE |

The complete rationales, evidence item IDs, and construct-boundary notes from both reviews are preserved in `external_review_disagreements.csv`. Discordant rows were not adjudicated to increase coverage.

## Flagged SAPA item quality audit

Historical review packets and both sets of judgments remain unchanged. Corrections apply only to future derivative metadata.

- `q_251`: the SAPA V5 file itself elides the item. The official IPIP item list supports “Am seldom bothered by the apparent suffering of strangers.” It is same-direction evidence for `cruel` and `callous`.
- `q_1483`: SAPA V5 contains `[Forget to put things back].`; the official IPIP key supplies “Often forget to put things back in their proper place.” It is same-direction for `disorganized`.
- `q_1671`: SAPA V5 and the official SAPA SPI document both preserve `[Enjoy interactions less than others].` No longer exact wording was provenance-verified. Future display may remove brackets only while retaining a source-qualified flag; direction is same for `avoidant`.
- `q_1758` (“Suspect hidden motives in others.”): reverse for `naive`, same for `paranoid`.
- `q_566` (“Dislike changes.”): reverse for `adaptable`.
- `q_463` (“Can't do without the company of others.”): reverse for `independent`, same for `gregarious`.
- `q_1742` (“Start conversations.”): same for `extroverted` and `gregarious`, reverse for `reserved`.
- `q_1624` (“Respect authority.”): same for `deferential` and `reverent`, reverse for `rebellious`.

The last five findings show that the historical row-level `same_direction` shorthand was too coarse when the same evidence item supported traits with opposite poles. Official SAPA scale-key signs are not changed.

## Human construct library

The library contains 126 nonduplicate documented constructs:

- all 92 administered source constructs;
- 23 SAPA Personality Inventory hierarchical keys;
- six HEXACO domain composites;
- five IPIP-NEO domain composites.

Framework coverage is Big Five (5), Big Five Aspects (10), Big Five Metatraits (2), Eysenck PEN (3), HEXACO (30), IPIP-NEO (35), MPQ (12), Questionnaire Big Six (6), and SAPA Personality Inventory (23). Duplicate short forms and duplicate derived copies of already represented scales were omitted. Definitions are source-grounded paraphrases; abbreviations were not expanded by guesswork.

Every library row records its hierarchy level, item IDs, official released scoring key, direction, sample availability, planned-overlap statistics, and human-only pairwise-complete standardized alpha. These alphas are reliability diagnostics under randomized planned missingness, not construct validation.

## Frozen Qwen model-side evidence

The signature contains all 240 trait associations for each of PC1-PC6 (1,440 rows), 20 role extremes per pole for each PC (240 rows), full-distribution cluster means, variance/stability, Qwen-only strict Big Five associations, AA-4 marginal/conditional evidence where available, existing blinded interpretations, and the PC1 focused accountability result. Canonical PC1-PC3 scores reproduce the extended Qwen browser bundle within `1.21e-6`, inside its `1e-5` tolerance.

| PC | Status | Variance | Bootstrap cosine median / q05 | Leading positive traits | Leading negative traits |
|---|---|---:|---:|---|---|
| PC1 | core | 31.595% | 0.994 / 0.981 | transparent, factual, analytical, methodical | narrative, romantic, poetic, metaphorical |
| PC2 | core | 16.163% | 0.984 / 0.957 | experiential, practical, casual, accessible | introverted, ritualistic, pensive, theoretical |
| PC3 | core | 8.690% | 0.979 / 0.938 | callous, cynical, pessimistic, vindictive | benevolent, nurturing, supportive, deferential |
| PC4 | supported secondary | 4.520% | 0.871 / 0.685 | avoidant, understated, literal, reductionist | holistic, systems thinker, independent, generous |
| PC5 | supported secondary | 3.615% | 0.830 / 0.575 | divergent, cosmopolitan, curious, introspective | closure seeking, efficient, convergent, concise |
| PC6 | supported secondary | 2.824% | 0.792 / 0.594 | deontological, universalist, fundamentalist, principled | systems thinker, divergent, holistic, interdisciplinary |

PC4-PC6 remain secondary/provisional because their bootstrap stability is materially below PC1-PC3. Human labels were not forced.

## PC-by-PC construct hypotheses

### PC1 — high Stability / low Plasticity with Conscientiousness prominent

**Model-side signature.** High PC1 is factual, analytical, methodical, cautious, calm, and populated by roles with externally legible standards. Low PC1 is poetic, narrative, metaphorical, dramatic, enigmatic, artistic, mythic, and expressive. Strict Qwen Big Five correlations are Extraversion -0.817, Neuroticism -0.758, Conscientiousness +0.748, Openness -0.704, and Agreeableness +0.424.

**Best candidates.** `STRONG CANDIDATE`: Conscientiousness (+), Stability (+), Plasticity (-). `FACET / SUBCOMPONENT`: Orderliness, Industriousness, Achievement Striving, Self-Discipline, and Dutifulness (+).

**Measurement.** All are directly available through released SAPA keys. Pairwise alpha ranges from 0.718 (Stability) to 0.916 (Conscientiousness); all facet estimates are at least 0.814.

**Mismatch and confidence.** Confidence is high *as a Qwen-only discovery description*, not as equivalence. No human construct covers transparent/secular factuality, external-standard accountability, and the full expressive/mythic negative pole simultaneously. `pc1_human_construct_worked_example.md` gives the complete candidate audit.

### PC2 — compound low regulation / high reactivity and social immediacy versus abstract integration

**Model-side signature.** High PC2 is experiential, practical, casual, accessible, gregarious, anxious, and associated with developmental, procrastinating, comic, and socially volatile roles. Low PC2 is introverted, ritualistic, pensive, theoretical, abstract, reverent, conceptual, principled, solemn, and archetypal. Strict directions are Conscientiousness -0.655, Neuroticism +0.534, Extraversion +0.534, Openness +0.295, Agreeableness -0.059.

**Best candidates.** No strong single construct. `PLAUSIBLE PARTIAL CANDIDATE`: lower Stability, lower MPQ Control, lower Conscientiousness, higher Neuroticism, and higher Extraversion. `FACET / SUBCOMPONENT`: lower Intellect and higher Volatility.

**Measurement.** All frozen components have SAPA keys with pairwise alpha 0.718-0.952. The 60-item Neuroticism domain is reliable at the covariance level but especially sparse within person.

**Mismatch and confidence.** Confidence is moderate-low. The human constructs capture regulation, affect, social immediacy, and abstraction separately; none captures the model-specific “coherent action under unresolved uncertainty” synthesis. A dedicated Intolerance of Uncertainty measure was considered but marked insufficient, not frozen.

### PC3 — low Agreeableness plus exploitative/aggressive residuals

**Model-side signature.** High PC3 is callous, cynical, pessimistic, vindictive, blunt, dominant, confrontational, competitive, and cruel, with disruptive/deceptive roles. Low PC3 is benevolent, nurturing, supportive, deferential, optimistic, altruistic, forgiving, and care-oriented. Strict Agreeableness correlates -0.882; other Big Five associations are much smaller.

**Best candidates.** `STRONG CANDIDATE`: Agreeableness (-). `PLAUSIBLE PARTIAL CANDIDATE`: Honesty-Humility (-). `FACET / SUBCOMPONENT`: Compassion (-), Politeness (-), Altruism (-), Aggression (+), and Machiavellianism (+).

**Measurement.** All are SAPA-available. Pairwise alpha is 0.910 for Agreeableness, 0.894 for the 40-item Honesty-Humility composite, and 0.757-0.876 for the facets.

**Mismatch and confidence.** Agreeableness remains the best established domain-level description, with high discovery confidence for the cooperative/antagonistic core. It captures only one major component of a broader transgressive stance; norm inversion, deception, technical intervention, and comic/outsider register remain partly model-specific.

### PC4 — lower Openness/Intellect and higher conventionality, provisionally

**Model-side signature.** High PC4 is avoidant, understated, literal, reductionist, traditional, and deferential; low PC4 is holistic, systems-oriented, independent, progressive, critical, big-picture, introspective, and interdisciplinary. Roles contrast infant/toddler/caveman/literal functions with revolutionary/anarchist/maverick/rebel/visionary roles. Strict Openness is -0.394; other Big Five relations are small.

**Best candidates.** `PLAUSIBLE PARTIAL CANDIDATE`: Openness/Intellect (-) and Traditionalism (+). `FACET / SUBCOMPONENT`: Intellect (-), Unconventionality (-), and IPIP-NEO Liberalism (-, meaning questioning convention/authority rather than partisan identity).

**Measurement.** All are SAPA-available and show pairwise alpha 0.781-0.892. Traditionalism and the Liberalism facet substantially reuse inverse item content (maximum selected-item Jaccard 0.667), so they are hierarchical/opposite-pole evidence rather than independent measurements.

**Mismatch and confidence.** Confidence is low-to-moderate because PC4 is a secondary axis and the developmental/avoidant role content is not explained by openness or conventionality. HEXACO interpersonal `Flexibility` was explicitly rejected as a label trap.

### PC5 — divergent exploratory openness versus convergent closure/action, provisionally

**Model-side signature.** High PC5 is divergent, cosmopolitan, curious, introspective, futuristic, inclusive, interdisciplinary, exploratory, and eclectic; low PC5 is closure-seeking, efficient, convergent, concise, anthropocentric, decisive, traditional, practical, and fundamentalist. Strict Openness is only +0.272; other Big Five relations are near zero.

**Best candidates.** `PLAUSIBLE PARTIAL CANDIDATE`: Openness/Intellect (+) and Plasticity (+). `FACET / SUBCOMPONENT`: Creativity, Inquisitiveness, Unconventionality, Absorption (+), and Traditionalism (-).

**Measurement.** All are SAPA-available with pairwise alpha 0.769-0.906.

**Mismatch and confidence.** Confidence is low-to-moderate. Developmental/comic positive roles and martial/criminal negative roles cannot be reduced to openness. The modest strict Big Five association and secondary-axis stability preclude a strong domain label.

### PC6 — principled/absolute closure versus systems exploration; no clean SAPA domain

**Model-side signature.** High PC6 is deontological, universalist, fundamentalist, principled, absolutist, convergent, literal, and dogmatic, with zealot, stoic, anarchist, revolutionary, martyr, judge, purist, traditionalist, pacifist, and cynic roles. Low PC6 is systems-oriented, divergent, holistic, interdisciplinary, futuristic, curious, exploratory, generous, adaptable, and populated by creative/leisure/craft roles. All strict Big Five correlations are small; Openness is the largest at -0.173.

**Best candidates.** `PLAUSIBLE PARTIAL CANDIDATE`: Need for Cognitive Closure (+) and Openness/Intellect (-). `FACET / SUBCOMPONENT`: Dutifulness (+). No strong candidate was assigned.

**Measurement.** Openness/Intellect and Dutifulness are in SAPA. The dedicated Need for Closure Scale is absent and requires another human dataset.

**Mismatch and confidence.** Confidence is low. Traditionalism was not frozen because anarchist and revolutionary roles share the positive pole; Unconventionality was rejected because political unconventionality and cognitive exploration split. The likely residual is content-invariant commitment to absolute principles versus pluralistic systems exploration, for which no clean SAPA construct was found.

## Human measurement feasibility after selection

The frozen set includes 27 distinct SAPA constructs spanning 331 unique items. Human-only pairwise standardized alpha ranges from 0.718 to 0.952. Pairwise covariance is therefore estimable, but ordinary respondent-level complete scoring is not:

- across the 36 SAPA-available frozen PC-construct rows, the median construct has one administered item per respondent (IQR 1-2; maximum median 7 for the 40-item Honesty-Humility composite);
- the median respondent sees three of the 20 IPIP Conscientiousness items, two Stability items, two Plasticity items, and one or two items from most 10-item facets;
- no respondent completes the 20-item PC1 domain/metatrait keys;
- only three distinct selected constructs have even one complete-key respondent, and no complete-case bridge profile exists;
- selected constructs can share substantial content where hierarchy legitimately overlaps; the largest observed selected-pair Jaccard is 0.667 for Traditionalism and Liberalism.

A later study should treat domain/aspect/facet overlap as a measurement hierarchy and use full-information factor/IRT modeling or another prevalidated partial-information method. Source-scale subset scoring may be suitable for descriptive scale means but does not solve individual-profile uncertainty. Complete-case analysis and mean imputation are not justified.

## Answers to the specified questions

1. **Why did Conscientiousness fail to appear in the 12-trait AA-1 set?** The narrow three-item `conscientious` proxy was penalized for redundancy with neighboring proxies—especially `methodical` at `|r|=0.750`—despite coherent items and source-scale convergence. The prior objective was differentiated narrow measurements.
2. **Does that imply Conscientiousness is a poor PC1 analogue?** No. The full Qwen PC1 signature and a reliable 20-item human domain make it a strong candidate for the high pole, though not a complete axis label.
3. **What hierarchy best characterizes PC1?** Higher Stability and lower Plasticity; Conscientiousness as the strongest single domain; Orderliness, Industriousness, Achievement Striving, Self-Discipline, and Dutifulness as subcomponents; external-standard accountability as a model-specific residual.
4. **Which broad constructs plausibly correspond to PC2?** Low Stability, Control, and Conscientiousness plus higher Neuroticism and Extraversion, with low Intellect representing the abstract low pole. This is a composite, not one clean domain.
5. **Does PC3 remain Agreeableness?** Agreeableness remains the strongest broad core, but it captures one component of a wider cooperative-stabilizing versus antagonistic-transgressive axis. Honesty-Humility, Aggression, and Machiavellianism capture residual parts.
6. **Are there defensible analogues for PC4-PC6?** Partial ones: lower Openness/Intellect and higher Traditionalism for PC4; Openness/Plasticity and divergent-exploratory facets for PC5; Need for Cognitive Closure, lower Openness/Intellect, and Dutifulness for PC6. None received a strong axis-level status.
7. **Which are directly measurable in SAPA?** Thirty-six of 37 frozen PC-construct rows, representing 27 distinct constructs. All PC1-PC5 candidates and PC6 Openness/Intellect and Dutifulness are available.
8. **Which require another dataset?** The frozen Need for Cognitive Closure candidate for PC6. A dedicated Intolerance of Uncertainty measure would also require another source if reconsidered for PC2.
9. **Is a domain-level bridge more coherent than the literal 240-trait bridge?** Interpretation: yes for PC1 and PC3, because it respects the hierarchy of broad axes and their facets instead of treating overlap as disqualifying. PC2 and PC4-PC6 remain compound or provisional, preventing false neatness.
10. **What remains model-specific?** PC1 external-standard accountability/transparent factual practice; PC2 abstraction and coherent action under unresolved uncertainty; PC3 transgressive/technical/outsider stance beyond Agreeableness; PC4 autonomous systemic revision; PC5 divergent exploration versus closure/action; and PC6 cross-ideological principled absolutism.

## Observed

- The supplied Claude file contains exactly 78 unique frozen review IDs and is preserved unchanged.
- Claude and Codex agree exactly on 69/78 five-category decisions; all nine disagreements and both rationales are saved.
- The flagged wording and trait-specific direction problems are provenance-audited; historical packets are unchanged.
- The construct library contains 126 documented human constructs and released keys; all have human-only administration and reliability diagnostics.
- The Qwen signature includes 240 traits per PC, 40 role extremes per PC, Qwen-only Big Five associations, stability, and permitted prior evidence.
- Four candidates met the frozen `STRONG CANDIDATE` rule: PC1 Conscientiousness, Stability, and negative-polarity Plasticity; PC3 negative-polarity Agreeableness.
- PC2 and PC4-PC6 have no strong single candidate under the frozen rubric.
- The final hypothesis set is frozen in `qwen_derived_human_construct_hypotheses_v1.csv` before the future validation plan was authored.

## Interpretation

- The 12-trait narrowing discarded broad constructs for a reason specific to narrow-proxy distinctness; reintroducing domain/aspect hierarchy is scientifically more appropriate for PC-level bridge construction.
- A defensible Qwen-only discovery bridge exists for PC1 and PC3. PC2 supports a composite hypothesis. PC4-PC6 support only provisional components.
- SAPA is adequate for estimating human covariance/latent structure for most selected constructs, but severe planned missingness makes naive individual complete-scale profiles unavailable.

## Hypotheses

- Qwen PC1 may share a broad organizational pattern with higher human Stability/Conscientiousness and lower Plasticity.
- Qwen PC3 may share a broad cooperative-versus-antagonistic pattern with human Agreeableness, supplemented by Honesty-Humility and aggression/exploitation facets.
- The component hypotheses for PC2 and PC4-PC6 may generalize to an independent role inventory or model, but their compound form and weaker axis stability make failure plausible.

## Unknown

- Whether any human latent score corresponds quantitatively to any Qwen PC.
- Whether the same latent constructs exist in human and model representations.
- Whether the hypotheses recur in another model family or a new Qwen role inventory.
- Whether behaviorally elicited responses realize the saved role-vector patterns.
- Whether independent human experts accept the construct hierarchy and disputed boundaries.
- Whether the PC6 closure candidate survives measurement with a dedicated human instrument.

## Next gate

The single most important immediate gate is independent human psychometric review of the frozen Qwen-PC → human-construct hypotheses, followed by a human-only measurement model that can handle SAPA's randomized planned missingness. Only after those gates and a preregistered held-out model test should respondent-to-model projection be considered.

No human respondent was assigned an LLM persona. No respondent-level human data were committed. No Llama/Gemma comparison was performed. No AA-7 alignment result was used. No GPU, RunPod, new model inference, activation extraction, response generation, or external model API was used.
