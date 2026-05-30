# PC3 Hypothesis Evaluation

Date: 2026-05-29
Analysis model: GPT-5.5 High Reasoning

## 1. Research Question

Does PC3 primarily separate personas that preserve, repair, coordinate, or stabilize systems from personas that manipulate, exploit, challenge, invert, or destabilize systems? This report treats that interpretation as a falsifiable hypothesis rather than a conclusion.

## 2. Data and Method

Inputs are existing local artifacts only: canonical Qwen activation PCA3D coordinates, role descriptions, cluster assignments, Big Five overlay residuals, and hierarchical-model residuals. The blind rubric and competing hypotheses are deterministic lexical scores over persona descriptions only, not coordinates or role-vector activations.

## 3. PC3 Contrast Analysis

Pairs were formed by taking nearest neighbors in PC1/PC2 space, then ranking by PC3 separation. The strongest contrasts are:

| Pair | PC1 diff | PC2 diff | PC3 diff | Rubrics |
|---|---:|---:|---:|---|
| hacker ↔ caregiver | 3.91 | 0.32 | 79.73 | system-challenging ↔ system-preserving |
| contrarian ↔ caregiver | 4.93 | 0.68 | 69.45 | system-challenging ↔ system-preserving |
| widow ↔ provocateur | 4.89 | 6.11 | 68.82 | system-neutral ↔ system-challenging |
| widow ↔ absurdist | 5.70 | 1.86 | 67.73 | system-neutral ↔ system-challenging |
| optimist ↔ hacker | 2.80 | 7.91 | 67.63 | system-preserving ↔ system-challenging |
| workaholic ↔ caregiver | 1.22 | 4.74 | 67.35 | system-neutral ↔ system-preserving |
| grandparent ↔ cynic | 8.90 | 6.31 | 66.42 | system-neutral ↔ system-neutral |
| jester ↔ widow | 12.46 | 3.56 | 65.28 | system-neutral ↔ system-neutral |
| immigrant ↔ hacker | 2.20 | 0.45 | 65.14 | system-neutral ↔ system-challenging |
| refugee ↔ hacker | 10.77 | 1.85 | 64.92 | system-neutral ↔ system-challenging |
| widow ↔ rogue | 2.05 | 4.21 | 64.56 | system-neutral ↔ system-exploiting |
| empath ↔ fixer | 3.04 | 13.14 | 62.65 | system-neutral ↔ system-neutral |

Pattern readout: the pairwise contrasts often separate care/mediation/professional-support roles from outsider, transgressive, theatrical, or predatory roles, but the distinction is not pure. Some large contrasts are better described as social-care versus symbolic/disruptive register, or institutional/procedural role versus liminal/outlaw role.

## 4. Blind Rubric Test

- Ordinal rubric correlation with PC3: r=-0.318, Spearman=-0.298, R2=0.101
- Continuous preserve-minus-challenge/exploit score correlation with PC3: r=-0.312, Spearman=-0.306, R2=0.097
- Category counts: {'system-neutral': 228, 'system-challenging': 14, 'system-preserving': 30, 'system-exploiting': 1}
- Category mean PC3: {'system-neutral': 0.4408798527454942, 'system-challenging': 13.137480683251619, 'system-preserving': -10.843471837460179, 'system-exploiting': 30.23694749332942}

The blind rubric predicts PC3 only weakly if treated as a four-level categorical score. That is evidence against a strong version of the hypothesis. The continuous lexical score is more informative, but still not enough to claim PC3 is simply a system-preserving axis.

## 5. Alternative Hypothesis Search

| Rank | Hypothesis | Pearson r | Spearman r | R2 | Direction |
|---:|---|---:|---:|---:|---|
| 1 | nurturing_vs_competitive | -0.319 | -0.319 | 0.102 | negative_PC3 |
| 2 | system_preserving_vs_exploiting | -0.308 | -0.294 | 0.095 | negative_PC3 |
| 3 | altruistic_vs_self_interested | -0.170 | -0.183 | 0.029 | negative_PC3 |
| 4 | cooperative_vs_adversarial | -0.154 | -0.130 | 0.024 | negative_PC3 |
| 5 | transparent_vs_deceptive | 0.050 | 0.067 | 0.003 | positive_PC3 |
| 6 | institutional_vs_antiinstitutional | -0.049 | -0.039 | 0.002 | negative_PC3 |
| 7 | collective_vs_individualist | -0.009 | -0.036 | 0.000 | negative_PC3 |

The strongest lexical alternative is `nurturing_vs_competitive` (r=-0.319). The target system-preserving/exploiting hypothesis ranks 2 with r=-0.308.

## 6. UMAP / Cluster Validation

This quantitative check uses cluster labels rather than visual impressions from UMAP.

| Cluster | n | mean PC3 | std | min | max | frac > median | frac > q75 | d vs rest |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| combative_iconoclast | 14 | 25.78 | 9.41 | -2.21 | 36.36 | 0.93 | 0.93 | 1.86 |
| trickster_chaos | 10 | 23.03 | 10.40 | 0.40 | 33.41 | 1.00 | 0.80 | 1.58 |
| mythic_spiritual | 50 | -0.05 | 15.24 | -30.59 | 31.11 | 0.44 | 0.26 | -0.00 |
| procedural_professional | 126 | -0.60 | 11.70 | -36.17 | 32.14 | 0.56 | 0.19 | -0.07 |
| editorial | 13 | -3.14 | 6.52 | -17.44 | 7.35 | 0.38 | 0.00 | -0.21 |
| other | 6 | -4.09 | 11.73 | -19.50 | 16.77 | 0.33 | 0.17 | -0.26 |
| grounded_social | 54 | -8.50 | 17.35 | -43.37 | 28.07 | 0.26 | 0.17 | -0.69 |

Combative-iconoclast mean PC3 is 25.78, with 0.93 above the global upper quartile. Trickster-chaos mean PC3 is 23.03, with 0.80 above the global upper quartile. Both clusters overlap the rest of the distribution, so enrichment should not be mistaken for a hard separation.

## 7. Residual Analysis

| Metric | corr PC3 | corr abs(PC3) | high-PC3 mean | low-PC3 mean | high-low | d |
|---|---:|---:|---:|---:|---:|---:|
| bigfive_residual | 0.065 | 0.079 | 20.15 | 18.35 | 1.80 | 0.13 |
| hierarchical_residual | 0.080 | 0.117 | 21.81 | 19.76 | 2.04 | 0.14 |
| agreeableness | -0.477 | -0.190 | 2.71 | 3.09 | -0.38 | -0.90 |
| conscientiousness | -0.080 | -0.228 | 3.01 | 3.09 | -0.07 | -0.08 |
| openness | 0.082 | 0.149 | 3.32 | 3.14 | 0.17 | 0.14 |
| extraversion | 0.136 | 0.264 | 2.77 | 2.61 | 0.16 | 0.27 |
| neuroticism | -0.017 | 0.275 | 2.55 | 2.64 | -0.09 | -0.14 |

Agreeableness correlation with PC3 is -0.477; Big Five residual correlation with PC3 is 0.065; hierarchical residual correlation with PC3 is 0.080. This suggests PC3 is partly captured by Big Five-style structure, especially agreeableness, but not exhausted by it.

## 8. PC3 Extremes

Highest PC3 personas:
- hacker (combative_iconoclast): PC3=36.36; A digital infiltrator who breaks into systems to expose secrets or cause disruption
- cynic (combative_iconoclast): PC3=36.28; A distrustful person who expects the worst of human nature and motives
- saboteur (combative_iconoclast): PC3=34.77; A covert operative who deliberately damages systems from within
- provocateur (combative_iconoclast): PC3=34.50; An agitator who deliberately challenges social norms through shocking or controversial actions
- absurdist (trickster_chaos): PC3=33.41; A philosophical jester who embraces life's meaninglessness with humor and creative rebellion
- spy (procedural_professional): PC3=32.14; A covert intelligence gatherer who operates in secrecy to obtain sensitive information
- comedian (trickster_chaos): PC3=31.28; A humor architect who builds laughter from observation and timing
- aberration (mythic_spiritual): PC3=31.11; A thing that should not be, violating natural order
- jester (trickster_chaos): PC3=30.96; A comedic truth-teller who uses humor to critique power
- rogue (trickster_chaos): PC3=30.24; A cunning outsider who operates beyond conventional rules using stealth and deception
- demon (mythic_spiritual): PC3=29.92; A chaotic entity from infernal realms testing mortal nature
- gossip (trickster_chaos): PC3=28.58; A social information broker who trades in rumors and personal details

Lowest PC3 personas:
- caregiver (grounded_social): PC3=-43.37; A nurturing person dedicated to supporting others' wellbeing
- empath (grounded_social): PC3=-36.85; Someone highly attuned to others' emotions and experiences
- counselor (procedural_professional): PC3=-36.17; A supportive listener who provides guidance on personal matters.
- therapist (procedural_professional): PC3=-34.53; A mental health professional who helps process emotions and thoughts.
- healer (procedural_professional): PC3=-34.35; Someone dedicated to restoring physical, mental, or spiritual wellness
- widow (grounded_social): PC3=-34.32; A person rebuilding after losing their life partner to death
- optimist (grounded_social): PC3=-31.27; Someone who maintains hope and sees the positive potential in situations
- romantic (grounded_social): PC3=-30.82; An idealist who believes in love, beauty, and emotional connection
- angel (mythic_spiritual): PC3=-30.59; A celestial guardian embodying pure benevolence and divine will
- grandparent (grounded_social): PC3=-30.14; An elder watching their legacy continue through new generations
- newlywed (grounded_social): PC3=-29.97; Someone learning to merge individual identity with partnership
- immigrant (grounded_social): PC3=-28.78; Someone adapting to life in a new country while preserving their heritage

## 9. Final Evaluation

1. Strongest current interpretation: PC3 is best described as a social-orientation / cooperative-care / system-stabilization versus antagonistic-disruptive / transgressive-register axis, with agreeableness-like structure as a major component. The original preserving-vs-exploiting hypothesis captures part of this, but is too narrow.
2. Supporting evidence: PC3 correlates with agreeableness; high-PC3 clusters include trickster/combative enrichment; pairwise PC1/PC2-neighbor contrasts often separate care, mediation, repair, and coordination from transgressive, disruptive, exploitative, or outsider roles; the system-preserving lexical hypothesis is competitive among alternatives.
3. Evidence against: blind rubric scores over descriptions predict PC3 weakly; clusters overlap heavily; several high-PC3 and low-PC3 cases are better explained by symbolic register, institutional/procedural texture, or social-care orientation than by preserving/exploiting alone.
4. Confidence level: moderate-low. The axis has a real cooperative/antagonistic signal, but the exact system-preserving versus exploiting formulation is not yet strong enough for paper-level language without qualification.
5. Efficient falsification experiment: construct paired personas matched on PC1/PC2-relevant traits and semantic domain but differing only in preserve/repair versus exploit/destabilize stance, preregister PC3 direction, extract no-label vectors, and test whether PC3 moves consistently while PC1/PC2 stay approximately fixed.
