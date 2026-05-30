# PC3 Perturbation-Stabilization Validation

model_used: GPT-5.5 High Reasoning

## Data Source

Exact data source path: `research/visualizations/geometry_viz_data.json`

PCA field: `roles.pca3d` with PC3 at index `2`.

Role definitions were extracted from `data/roles/instructions`. Scores used persona name plus extracted neutral role definition only; PC coordinates and clusters were joined only after scoring.

Number of personas scored: 275

Limitation: Scores are deterministic rubric scores from persona name plus extracted eval-prompt definition, not independent human or LLM judgments.

## Scoring Rubric

```text
Perturbation vs stabilization, 1-7:
1 = strongly stabilizing, nurturing, healing, mediating, preserving, protecting, supporting, or restoring systems.
2 = mostly stabilizing, with limited challenge or intervention.
3 = mildly stabilizing or support-oriented.
4 = neutral, mixed, or unclear.
5 = mildly perturbative: probes, challenges, tests, audits, diagnoses, disputes, or intervenes without clear destructive intent.
6 = strongly perturbative/interventionist: penetrates, stress-tests, exploits weaknesses, disrupts, investigates, debugs, argues, or forces change.
7 = extremely perturbative: chaotic, corrupting, predatory, destructive, sabotaging, or intentionally destabilizing.
```

## Global Correlations

Perturbation-stabilization vs PC3:

- Pearson: r=0.529, p=3.07e-21, 95% CI [0.435, 0.614]
- Spearman: r=0.511, p=9.92e-20, 95% CI [0.412, 0.603]
- Within-cluster pairwise ordering accuracy: 0.773 over 7824 usable pairs

## Within-Cluster Correlations

| cluster | n | Pearson | Spearman |
|---|---:|---|---|
| mythic_spiritual | 51 | r=0.639, p=4.62e-07, 95% CI [0.439, 0.788] | r=0.621, p=1.17e-06, 95% CI [0.426, 0.762] |
| grounded_social | 54 | r=0.243, p=0.0768, 95% CI [-0.130, 0.531] | r=0.138, p=0.32, 95% CI [-0.179, 0.433] |
| procedural_professional | 126 | r=0.663, p=2.93e-17, 95% CI [0.541, 0.758] | r=0.659, p=5.1e-17, 95% CI [0.523, 0.759] |

## Pairwise Ordering Accuracy For Target Clusters

| cluster | usable within-cluster pairs | accuracy |
|---|---:|---:|
| mythic_spiritual | 693 | 0.848 |
| grounded_social | 919 | 0.565 |
| procedural_professional | 6046 | 0.802 |

## Partial Correlation Controlling For Cluster

Pearson after residualizing score and PC3 against cluster dummies: r=0.491, p=4.54e-18, 95% CI [0.389, 0.583]

Spearman after residualizing score and PC3 against cluster dummies: r=0.440, p=1.85e-14, 95% CI [0.331, 0.542]

## Leave-One-Cluster-Out Validation

Training uses two of the target clusters and tests rank/order prediction in the held-out target cluster.

| held-out cluster | n train | n test | fitted slope | prediction Pearson | pairwise accuracy |
|---|---:|---:|---:|---|---:|
| mythic_spiritual | 180 | 51 | 5.083 | r=0.639, p=4.62e-07, 95% CI [0.439, 0.788] | 0.848 |
| grounded_social | 177 | 54 | 5.823 | r=0.243, p=0.0768, 95% CI [-0.130, 0.531] | 0.565 |
| procedural_professional | 105 | 126 | 6.750 | r=0.663, p=2.93e-17, 95% CI [0.541, 0.758] | 0.802 |

## Negative-Control Comparison

| rubric | Pearson vs PC3 | Spearman vs PC3 | within-cluster pairwise accuracy |
|---|---|---|---:|
| moral_badness | r=0.201, p=0.000826, 95% CI [0.047, 0.317] | r=0.147, p=0.0148, 95% CI [0.002, 0.275] | 0.665 |
| professionalism | r=0.103, p=0.0887, 95% CI [0.014, 0.186] | r=0.160, p=0.00795, 95% CI [0.053, 0.262] | 0.655 |
| weirdness_fantasticality | r=0.029, p=0.632, 95% CI [-0.085, 0.136] | r=0.022, p=0.714, 95% CI [-0.099, 0.140] | 0.563 |
| abstraction | r=0.129, p=0.0318, 95% CI [0.035, 0.221] | r=0.178, p=0.00302, 95% CI [0.064, 0.289] | 0.653 |

## Diagnostic Examples

### positive_but_prosocial

| persona | cluster | score | PC3 |
|---|---|---:|---:|
| auditor | procedural_professional | 7 | 13.609 |
| debugger | procedural_professional | 7 | 10.867 |
| skeptic | procedural_professional | 7 | 18.662 |
| statistician | procedural_professional | 7 | 15.733 |
| lawyer | procedural_professional | 7 | 14.466 |

### positive_and_antisocial

| persona | cluster | score | PC3 |
|---|---|---:|---:|
| demon | mythic_spiritual | 7 | 29.919 |
| parasite | mythic_spiritual | 7 | 23.002 |
| criminal | grounded_social | 6 | 26.992 |
| smuggler | grounded_social | 6 | 28.072 |

### negative_stabilizing

| persona | cluster | score | PC3 |
|---|---|---:|---:|
| counselor | procedural_professional | 1 | -36.167 |
| therapist | procedural_professional | 1 | -34.533 |
| healer | procedural_professional | 1 | -34.345 |
| caregiver | grounded_social | 1 | -43.371 |
| angel | mythic_spiritual | 1 | -30.585 |
| mediator | procedural_professional | 1 | -16.472 |

## Conclusion

Observed: the perturbation-stabilization score is positively associated with PC3 globally and remains positive after cluster control. The strongest evidence is the global correlation and within-cluster pairwise ordering result, especially where prosocial interventionist roles such as auditor and debugger score high without needing to be morally bad.

Observed: the result is mixed rather than decisive. Within-cluster correlations vary across the three target clusters, and the negative-control rubrics are not completely inert. Moral badness is the strongest negative control but remains much weaker than the target rubric, which means PC3 should not be described as a pure perturbation axis or as a pure moral-valence axis.

Inferred: PC3 shows suggestive but incomplete support for a perturbation-stabilization interpretation. The cleaner current wording is that positive PC3 emphasizes intervention, challenge, disruption, exploitation, testing, or adversarial pressure, while negative PC3 emphasizes care, repair, mediation, preservation, and stabilization. Cooperative-antagonistic remains a secondary or partial reading because many perturbative roles are socially antagonistic, but the diagnostic examples show perturbation can also be prosocial.

Recommended next test: replace this deterministic rubric with independent blinded human or second-model ratings over the same role definitions, then repeat the same cluster-control, pairwise-ordering, and negative-control tests.
