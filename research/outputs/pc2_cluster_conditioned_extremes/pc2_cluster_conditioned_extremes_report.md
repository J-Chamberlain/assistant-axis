# Cluster-Conditioned PC2 Extremes Diagnostic

- Date: 2026-06-02T01:11:15Z
- model_used: GPT-5.5
- Geometry source: `research/visualizations/geometry_viz_data.json`
- No GPU work and no new LLM judge calls were run.

## Dataset

- Total roles/personas: 275
- Clusters analyzed: combative_iconoclast=15, editorial=13, grounded_social=54, mythic_spiritual=51, other=6, procedural_professional=126, trickster_chaos=10
- Clusters with at least 10 roles: combative_iconoclast, editorial, grounded_social, mythic_spiritual, procedural_professional, trickster_chaos
- Sparse cluster skipped for top/bottom requirement: other

### Global PC2 Top 10

| Rank | Persona | Cluster | PC1 | PC2 | PC3 | PC2 pct |
|---:|---|---|---:|---:|---:|---:|
| 1 | teenager | other | -13.392 | 78.114 | -6.474 | 99.8 |
| 2 | adolescent | other | -15.450 | 78.081 | -7.234 | 99.5 |
| 3 | toddler | other | -36.268 | 71.156 | -12.326 | 99.1 |
| 4 | procrastinator | other | -16.544 | 69.468 | 16.772 | 98.7 |
| 5 | gossip | trickster_chaos | -24.695 | 57.220 | 28.585 | 98.4 |
| 6 | comedian | trickster_chaos | -24.029 | 56.604 | 31.280 | 98.0 |
| 7 | fool | trickster_chaos | -37.407 | 47.921 | 7.515 | 97.6 |
| 8 | infant | other | -42.890 | 44.700 | -19.499 | 97.3 |
| 9 | daredevil | combative_iconoclast | -29.846 | 43.747 | 26.448 | 96.9 |
| 10 | cynic | combative_iconoclast | -21.407 | 40.712 | 36.281 | 96.5 |

### Global PC2 Bottom 10

| Rank | Persona | Cluster | PC1 | PC2 | PC3 | PC2 pct |
|---:|---|---|---:|---:|---:|---:|
| 1 | crystalline | mythic_spiritual | -10.335 | -44.008 | 8.553 | 0.2 |
| 2 | ascetic | mythic_spiritual | -40.440 | -40.351 | -4.579 | 0.5 |
| 3 | eldritch | mythic_spiritual | -52.717 | -39.481 | 15.742 | 0.9 |
| 4 | mystic | mythic_spiritual | -42.169 | -36.161 | -18.949 | 1.3 |
| 5 | avatar | mythic_spiritual | -38.015 | -35.417 | -12.982 | 1.6 |
| 6 | oracle | mythic_spiritual | -45.705 | -34.549 | -2.560 | 2.0 |
| 7 | leviathan | mythic_spiritual | -60.939 | -33.503 | 12.445 | 2.4 |
| 8 | echo | mythic_spiritual | -49.892 | -33.354 | 0.208 | 2.7 |
| 9 | spirit | mythic_spiritual | -45.036 | -33.237 | -18.034 | 3.1 |
| 10 | ancient | mythic_spiritual | -38.009 | -32.793 | 3.309 | 3.5 |

## Per-Cluster PC2 Extremes

### combative_iconoclast (n=15)

- High PC2: daredevil (43.7), cynic (40.7), influencer (40.0), competitor (27.9), gamer (25.0), rebel (23.9), provocateur (22.5), maverick (20.1), workaholic (19.4), hacker (14.3)
- Low PC2: revolutionary (-5.7), destroyer (-3.2), saboteur (-0.8), devils_advocate (7.7), contrarian (13.9), hacker (14.3), workaholic (19.4), maverick (20.1), provocateur (22.5), rebel (23.9)

### editorial (n=13)

- High PC2: student (23.4), interviewer (7.5), translator (5.1), nutritionist (2.0), proofreader (1.6), summarizer (-1.0), editor (-2.1), screener (-2.4), supervisor (-2.6), secretary (-3.4)
- Low PC2: grader (-6.2), pharmacist (-4.2), accountant (-4.0), secretary (-3.4), supervisor (-2.6), screener (-2.4), editor (-2.1), summarizer (-1.0), proofreader (1.6), nutritionist (2.0)

### grounded_social (n=54)

- High PC2: amateur (40.1), prisoner (38.8), addict (38.7), criminal (37.4), orphan (36.5), bartender (36.3), newlywed (36.0), narcissist (34.7), improviser (34.4), grandparent (34.4)
- Low PC2: artisan (-12.2), flaneur (-8.3), novelist (-8.1), shapeshifter (-7.2), romantic (-2.7), tulpa (-0.9), prey (1.3), bohemian (2.7), musician (2.9), empath (3.9)

### mythic_spiritual (n=51)

- High PC2: exile (-4.7), elder (-4.9), wanderer (-5.2), warrior (-6.9), narrator (-8.2), predator (-9.1), demon (-11.5), virus (-12.9), parasite (-13.2), poet (-14.7)
- Low PC2: crystalline (-44.0), ascetic (-40.4), eldritch (-39.5), mystic (-36.2), avatar (-35.4), oracle (-34.5), leviathan (-33.5), echo (-33.4), spirit (-33.2), ancient (-32.8)

### other (n=6)

Cluster has fewer than 10 roles; full ranking is in CSV.

### procedural_professional (n=126)

- High PC2: mechanic (22.1), entrepreneur (16.3), expatriate (14.2), pragmatist (13.1), presenter (13.1), counselor (13.0), therapist (12.4), coach (11.7), networker (11.7), realist (10.4)
- Low PC2: hive (-32.7), philosopher (-30.9), swarm (-30.7), purist (-29.7), traditionalist (-26.9), theorist (-24.5), scholar (-21.0), anthropologist (-20.2), archaeologist (-19.5), historian (-18.9)

### trickster_chaos (n=10)

- High PC2: gossip (57.2), comedian (56.6), fool (47.9), rogue (20.6), pirate (20.3), jester (20.0), trickster (19.7), caveman (15.5), absurdist (14.6), genie (1.5)
- Low PC2: genie (1.5), absurdist (14.6), caveman (15.5), trickster (19.7), jester (20.0), pirate (20.3), rogue (20.6), fool (47.9), comedian (56.6), gossip (57.2)


## Muted-PC1 Within-Cluster Results

Within each cluster, I selected the central 40th-60th percentile PC1 band when it yielded at least 12 roles, widened to 35th-65th if needed, and skipped clusters that remained too sparse.

| Cluster | Status | Band | Selected / Cluster |
|---|---|---|---:|
| combative_iconoclast | too_sparse | n/a | 5 / 15 |
| editorial | too_sparse | n/a | 3 / 13 |
| grounded_social | included | cluster_pc1_central_35_65 | 16 / 54 |
| mythic_spiritual | included | cluster_pc1_central_35_65 | 15 / 51 |
| other | too_sparse | n/a | 2 / 6 |
| procedural_professional | included | cluster_pc1_central_40_60 | 26 / 126 |
| trickster_chaos | too_sparse | n/a | 2 / 10 |

## Diagnostic Role Checks

The eight hand-coded expected-direction checks passed 7/8 against the global median and 5/8 against cluster medians.

| Role | Expected | Global side | Cluster side | PC2 | Cluster | Note |
|---|---|---|---|---:|---|---|
| shapeshifter | high | low | low | -7.226 | grounded_social | Strong counterexample to naive plasticity=high-PC2 within cluster. |
| chameleon | high | high | low | 15.880 | grounded_social | Global and cluster-conditioned signs diverge; cluster baseline matters. |
| tree | low | low | low | -28.499 | mythic_spiritual |  |
| hive | low | low | low | -32.681 | procedural_professional |  |
| elder | low | low | high | -4.930 | mythic_spiritual | Global and cluster-conditioned signs diverge; cluster baseline matters. |
| patient | high | high | high | 29.188 | grounded_social |  |
| amateur | high | high | high | 40.070 | grounded_social |  |
| philosopher | low | low | low | -30.944 | procedural_professional |  |

Key examples:

- `shapeshifter`: PC2=-7.226, global rank 167/275, cluster rank 51/54; this is a major counterexample to a simple identity-plasticity=>high-PC2 rule.
- `chameleon`: PC2=15.880, above the global median but below the grounded_social cluster median; this matches the broad social-adaptation prediction only before cluster conditioning.
- `tree`: PC2=-28.499, low globally and within mythic_spiritual, matching the rootedness/stability prediction.
- `hive`: PC2=-32.681, very low globally and within procedural_professional, matching systemic integration.
- `elder`: PC2=-4.930, low globally but high relative to the mythic_spiritual cluster median, so it only partially matches the long-residence integration prediction.
- `patient` and `amateur`: high globally and within cluster, matching vulnerability/formative-state predictions.
- `philosopher`: low globally and within cluster, matching abstraction/integration.

## Existing Proxy-Score Associations

Existing `pc2_conditional_validation` scores were reused; no new LLM scoring was performed.

- maturity: global Pearson r=-0.376, cluster-demeaned Pearson r=-0.080
- abstraction: global Pearson r=-0.656, cluster-demeaned Pearson r=-0.484
- expertise: global Pearson r=-0.356, cluster-demeaned Pearson r=-0.252
- uncertainty_exposure: global Pearson r=-0.089, cluster-demeaned Pearson r=-0.014
- residence_time_under_uncertainty: global Pearson r=-0.400, cluster-demeaned Pearson r=-0.086
- coherent_action_under_unresolved_uncertainty: global Pearson r=0.371, cluster-demeaned Pearson r=0.083

## Interpretation

The cluster-conditioned results provide partial support for the refined PC2 hypothesis. High PC2 often emphasizes roles that are situated, vulnerable, socially exposed, formative, or shaped by immediate conditions: amateur, influencer, patient, blogger, podcaster, chameleon, toddler, infant, teenager, addict, and similar cases recur near high-PC2 regions. Low PC2 often emphasizes durable, systemic, rooted, abstract, or long-residence organization: hive, philosopher, elder, guardian, traditionalist, purist, strategist, historian-like and integrated/systemic cases recur near low-PC2 regions.

The interpretation does survive some cluster conditioning, especially within `grounded_social` and `procedural_professional`, but it is not clean enough to promote to an established claim. The biggest counterexamples are important: `shapeshifter` is low PC2 despite identity plasticity, `chameleon` drops below its cluster median despite being high globally, and `elder` is low globally but high relative to mythic_spiritual. These suggest PC2 is not just plasticity vs rootedness. It may instead combine social/developmental exposure, local situational demand, and degree of integrated abstraction, with cluster-specific semantic context changing which surface properties dominate.

## Careful Report Wording

PC2 is best described provisionally as a situated-immediacy/formative-state versus integrated-stability axis. High PC2 tends to collect roles whose behavior is shaped by immediate social context, vulnerability, developmental incompleteness, performance pressure, or dependence on local circumstance. Low PC2 tends to collect roles with more durable, abstract, systemic, rooted, or long-residence organization. This should not be stated as a pure plasticity axis: some plastic or organic roles violate the simple prediction, so PC2 remains a compound axis whose interpretation is strongest when conditioned on PC1 and cluster context.

## Recommended Next Test

Run a blinded within-cluster matched-pair rating study using role prompt text or rollout responses when available. Construct pairs close in PC1 and PC3 within the same cluster but separated on PC2, and force raters to choose which member is more situated/formative/impressionable versus integrated/stable/durable. This would test the interpretation directly rather than relying on role-name intuition.

## Output Files

- `pc2_global_ranking.csv`
- `pc2_per_cluster_rankings.csv`
- `pc2_muted_pc1_within_cluster_rankings.csv`
- `pc2_diagnostic_roles_table.csv`
- `pc2_expected_direction_checks.csv`
- `pc2_cluster_conditioned_stats.json`
- `pc2_cluster_conditioned_plots.png`
- `pc2_scoring_template_for_future_judge.csv`
