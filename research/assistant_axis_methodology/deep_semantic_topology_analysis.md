# Deep Semantic Topology Analysis

## 1. Research Question

This analysis asks what structure exists in the Lu et al. role corpus before target-model activations are considered. It treats the corpus as a constructed semantic manifold made from role names, role descriptions, original label-exposed system prompts, and no-label prompt rewrites. It does not run inference, generate activations, or claim that prompt-space structure causes activation-space structure.

## 2. Data and Methods

Inputs were `data/roles/role_list.json`, `data/roles/instructions/*.json`, `research/assistant_axis_methodology/no_label_prompt_ablation/no_label_role_prompts.jsonl`, and activation labels from `visualizations/full_ranking.csv` used only as a comparison reference. The local environment did not provide sentence-transformers, scikit-learn, or matplotlib, so the script used offline TF-IDF with unigrams and bigrams, NumPy SVD reduction, deterministic k-means, cosine nearest neighbors, density summaries, cluster-margin bridge scoring, and centroid-linkage hierarchical snapshots. The no-label prompt space is used as the primary controlled semantic manifold because prior audits showed it preserves continuous prompt topology while removing explicit role-title exposure.

## 3. Stable Semantic Structures

Continuous topology remains much more stable than hard cluster labels. The prior original-vs-no-label distance correlation is 0.956, while the k=7 hard-cluster ARI between original and no-label prompt spaces is only 0.183. In this deeper pass, the most compact no-label semantic clusters are narrow professional/evaluative, confrontational, and fantastical/social-play regions; the least compact regions are broad heterogeneous role basins.

The no-label k=7 semantic clusters are:

| Semantic cluster | n | Mean within cosine | Anchors | Main activation-label mix | Top terms |
|---:|---:|---:|---|---|---|
| 4 | 39 | 0.215 | `elder`, `expatriate`, `survivor`, `prisoner`, `refugee`, `orphan`, `nomad` | grounded_social:22, mythic_spiritual:11, other:4, trickster_chaos:1 | has, life, someone, through, understands, experience, someone_has, challenges |
| 5 | 43 | 0.213 | `recruiter`, `researcher`, `consultant`, `navigator`, `evaluator`, `pilot`, `debugger` | procedural_professional:36, editorial:5, grounded_social:2 | bring, specializes, extensive, bring_extensive, experience, someone, skilled, extensive_experience |
| 1 | 44 | 0.209 | `pharmacist`, `chef`, `mathematician`, `engineer`, `cartographer`, `naturalist`, `architect` | procedural_professional:34, grounded_social:6, mythic_spiritual:3, other:1 | bring, knowledge, specializes, expertise, someone, extensive, deep, bring_deep |
| 6 | 30 | 0.196 | `narrator`, `writer`, `podcaster`, `blogger`, `auctioneer`, `bard`, `journalist` | procedural_professional:14, mythic_spiritual:7, grounded_social:5, other:4 | through, bring, specializes, events, information, stories, skilled, excels |
| 3 | 40 | 0.176 | `dreamer`, `whale`, `eldritch`, `chimera`, `crystalline`, `egregore`, `demon` | mythic_spiritual:25, procedural_professional:7, other:5, trickster_chaos:2 | someone, through, whose, entity, embody, consciousness, embody_someone, reality |
| 0 | 36 | 0.174 | `purist`, `traditionalist`, `anarchist`, `pacifist`, `luddite`, `revolutionary`, `hoarder` | procedural_professional:18, mythic_spiritual:9, combative_iconoclast:4, other:3 | someone, all, cultural, between, systems, embody, embody_someone, bring |
| 2 | 43 | 0.133 | `guide`, `realist`, `optimist`, `narcissist`, `improviser`, `guru`, `caregiver` | procedural_professional:17, grounded_social:7, mythic_spiritual:6, other:5 | others, through, someone, people, use, thinking, bring, specializes |

## 4. Cluster Archetypes

The strongest semantic structures are not a single kind of category. Some are professional and procedural, some are narrative or mythic, some are moralized or adversarial, and some are stylistic modes of speech. The corpus therefore appears organized by a mixture of social function, communicative stance, narrative genre, and expected behavioral repertoire rather than by one psychological taxonomy.

The editorial/professional pocket is anchored by roles whose prompts repeatedly describe assessment, refinement, standards, and clear output improvement. The combative pocket is anchored by opposition, challenge, competition, and pressure. The theatrical/fantastical pocket is anchored by symbolic agency, boundary play, prophecy, mischief, and nonordinary identity. Large professional/helper and mythic/social basins are less discrete; they look more like gradients or families than clean partitions.

## 5. Basin Structures

| Basin | n | Mean within cosine | Anchors |
|---|---:|---:|---|
| `assistant_adjacent_seed` | 18 | 0.172 | `reviewer`, `evaluator`, `grader`, `consultant`, `assistant`, `editor` |
| `activation_editorial` | 5 | 0.325 | `grader`, `screener`, `proofreader`, `examiner`, `editor` |
| `activation_procedural_professional` | 127 | 0.122 | `pharmacist`, `researcher`, `navigator`, `debugger`, `consultant`, `pilot` |
| `fantastical_theatrical_seed` | 21 | 0.153 | `demon`, `avatar`, `golem`, `jester`, `fool`, `eldritch` |
| `collective_identity_seed` | 7 | 0.379 | `swarm`, `hive`, `coral_reef`, `egregore`, `ecosystem`, `mycorrhizal` |
| `combative_seed` | 8 | 0.190 | `contrarian`, `maverick`, `rebel`, `devils_advocate`, `provocateur`, `competitor` |
| `activation_trickster_chaos` | 7 | 0.173 | `trickster`, `absurdist`, `jester`, `improviser`, `genie`, `dilettante` |
| `activation_mythic_spiritual` | 61 | 0.121 | `whale`, `spirit`, `golem`, `wanderer`, `demon`, `wind` |
| `activation_grounded_social` | 45 | 0.135 | `expatriate`, `prisoner`, `refugee`, `orphan`, `survivor`, `immigrant` |
| `activation_other` | 22 | 0.134 | `infant`, `toddler`, `hoarder`, `amnesiac`, `fool`, `zealot` |

The assistant-adjacent seed set is semantically coherent but not uniquely separate from the broader professional/helper material. This supports the current working view that assistant-basin structure can already be visible in prompt semantics, while activation-space extraction may compress these roles back toward generic assistant behavior. Fantastical and theatrical roles are semantically vivid, but they are not one compact island; they spread across prophetic, symbolic, playful, monstrous, and collective subregions.

## 6. Density and Topology Observations

The densest local neighborhoods have top-10 neighbor mean cosine around 0.576; the sparsest tail falls near 0.392. Dense regions generally correspond to redundant social functions or strongly scripted genres. Sparse regions are often hybrid, culturally specific, or ontologically unusual roles whose prompts do not have many close analogues in the 275-role inventory.

The hierarchical snapshots suggest broad superclusters rather than natural hard partitions. At three clusters the manifold separates into a large professional/social/helper region, a mythic/fantastical/symbolic region, and a more adversarial/playful/outlier region. At seven clusters these split into smaller pockets, but many boundaries remain soft.

Representative hierarchical snapshots:

### 3 clusters

1. n=129: `navigator`, `pharmacist`, `debugger`, `marketer`, `researcher`, `consultant`, `pilot`, `engineer`
2. n=83: `exile`, `prisoner`, `chimera`, `hoarder`, `addict`, `procrastinator`, `ecosystem`, `whale`
3. n=63: `guru`, `survivor`, `trickster`, `gamer`, `wanderer`, `hermit`, `narcissist`, `hedonist`

### 5 clusters

1. n=82: `navigator`, `pharmacist`, `pilot`, `merchant`, `marketer`, `chef`, `consultant`, `debugger`
2. n=63: `guru`, `survivor`, `trickster`, `gamer`, `wanderer`, `hermit`, `narcissist`, `hedonist`
3. n=54: `exile`, `procrastinator`, `addict`, `hoarder`, `prisoner`, `cosmopolitan`, `expatriate`, `ascetic`
4. n=47: `researcher`, `analyst`, `writer`, `summarizer`, `strategist`, `statistician`, `interviewer`, `journalist`
5. n=29: `eldritch`, `demon`, `golem`, `egregore`, `crystalline`, `chimera`, `dreamer`, `homunculus`

### 7 clusters

1. n=54: `exile`, `procrastinator`, `addict`, `hoarder`, `prisoner`, `cosmopolitan`, `expatriate`, `ascetic`
2. n=47: `researcher`, `analyst`, `writer`, `summarizer`, `strategist`, `statistician`, `interviewer`, `journalist`
3. n=47: `merchant`, `navigator`, `pharmacist`, `architect`, `marketer`, `entrepreneur`, `cartographer`, `chef`
4. n=37: `guru`, `martyr`, `trickster`, `narcissist`, `survivor`, `competitor`, `wanderer`, `visionary`
5. n=35: `consultant`, `assistant`, `generalist`, `polymath`, `reviewer`, `supervisor`, `evaluator`, `coordinator`
6. n=29: `eldritch`, `demon`, `golem`, `egregore`, `crystalline`, `chimera`, `dreamer`, `homunculus`
7. n=26: `grandparent`, `graduate`, `newlywed`, `hedonist`, `infant`, `toddler`, `elder`, `gamer`

## 7. Bridge and Outlier Roles

Bridge roles were identified by low margin between the nearest and second-nearest no-label semantic cluster centroids, cross-cluster nearest neighbors, and local density. These are the roles most likely to move under small representation changes or different clustering methods.

| Role | Activation cluster | Semantic cluster | Margin | Cross-cluster neighbors | Nearest neighbors |
|---|---|---:|---:|---:|---|
| `spy` | `grounded_social` | 2 | 0.001 | 7 | rogue:0.639, mycorrhizal:0.553, robot:0.455, interviewer:0.445, hacker:0.417 |
| `amnesiac` | `other` | 2 | 0.003 | 7 | orphan:0.558, workaholic:0.479, improviser:0.421, echo:0.409, hoarder:0.368 |
| `sage` | `mythic_spiritual` | 6 | 0.006 | 7 | guru:0.677, elder:0.605, pilgrim:0.540, hermit:0.521, absurdist:0.467 |
| `guardian` | `procedural_professional` | 3 | 0.008 | 5 | martyr:0.586, altruist:0.527, zealot:0.513, angel:0.472, narcissist:0.457 |
| `merchant` | `procedural_professional` | 5 | 0.013 | 4 | entrepreneur:0.778, smuggler:0.689, navigator:0.685, networker:0.669, marketer:0.667 |
| `emissary` | `procedural_professional` | 5 | 0.020 | 8 | mediator:0.763, interpreter:0.762, negotiator:0.745, translator:0.667, ambassador:0.656 |
| `technologist` | `procedural_professional` | 1 | 0.020 | 3 | evangelist:0.734, visionary:0.676, hacker:0.558, futurist:0.538, programmer:0.532 |
| `scout` | `procedural_professional` | 5 | 0.022 | 4 | recruiter:0.630, virtuoso:0.478, retiree:0.433, entrepreneur:0.428, screener:0.389 |
| `dilettante` | `trickster_chaos` | 2 | 0.023 | 6 | generalist:0.732, amateur:0.647, polymath:0.521, student:0.453, prodigy:0.439 |
| `addict` | `grounded_social` | 4 | 0.025 | 6 | prisoner:0.565, cosmopolitan:0.548, exile:0.532, stoic:0.520, provincial:0.516 |
| `mechanic` | `grounded_social` | 5 | 0.027 | 6 | engineer:0.796, debugger:0.698, mathematician:0.532, caveman:0.474, saboteur:0.459 |
| `surfer` | `grounded_social` | 3 | 0.027 | 6 | leviathan:0.628, pirate:0.547, whale:0.513, minimalist:0.442, ancient:0.433 |
| `alien` | `mythic_spiritual` | 3 | 0.028 | 6 | cyborg:0.729, demon:0.683, anthropologist:0.663, geographer:0.591, luddite:0.584 |
| `mystic` | `mythic_spiritual` | 1 | 0.031 | 6 | shaman:0.810, guru:0.698, pilgrim:0.616, healer:0.608, ascetic:0.541 |
| `toddler` | `other` | 4 | 0.033 | 7 | infant:0.645, caveman:0.484, poet:0.457, physicist:0.446, grandparent:0.434 |

The main outlier pattern is not random noise. Low-density roles tend to expose missing coverage in the corpus: unusual collectivities, specialized social positions, embodied developmental identities, and roles whose cultural scripts are narrow or unevenly represented. This is why the report treats semantic voids as corpus-design evidence rather than as bad data.

## 8. Relationship to Activation Geometry

Semantic topology and activation topology partially align, but the agreement is limited. In this deeper pass, k=7 ARI against activation labels is 0.119 for no-label prompt clusters and 0.085 for original prompt clusters. No-label prompt distances best predict available activation centroid-profile distances in the prior comparison, but correlations remain modest: 0.230 for Gemma and 0.254 for Qwen.

The cautious interpretation is preservation plus reorganization. Activation-space geometry appears to inherit semantic priors from the elicitation corpus, but it also sharpens some pockets, compresses some broad regions, and reorganizes neighborhoods according to model-specific representational pressures. The editorial cluster is semantically intrinsic and activation-adjacent to the assistant basin; trickster is semantically vivid and activation-separable in the completed Qwen extraction; editor is semantically clear but behaviorally low-yield under the tested extraction setup.

## 9. Cultural and Methodological Limitations

The role corpus is not a representative sample of human social life. It is an English-language, frontier-model-generated role inventory with heavy coverage of professions, helpers, archetypes, fantastical figures, and individualist identities. It likely undersamples non-Western social categories, kinship systems, ritual offices, communal identities, caste or lineage structures, and non-individualist self-concepts. Semantic clusters should therefore be interpreted as structure in this constructed corpus, not as a canonical map of human psychology.

The analysis is also methodologically limited by the local TF-IDF/SVD fallback. It captures lexical and phrase-level topology well enough for continuity checks, but it underestimates paraphrastic equivalence and culturally implicit similarity. The activation comparison uses available labels and centroid-profile outputs, not a reconstructed full activation distance matrix.

## 10. Emerging Hypotheses

### Supported observations

- The role corpus has meaningful semantic topology before activations are considered.
- No-label prompt topology remains close to original prompt topology at the continuous distance level.
- Hard semantic clusters are soft and unstable compared with continuous neighborhoods.
- Prompt semantics partially predict activation references, but not strongly enough to reduce activation geometry to semantics.

### Provisional interpretations

- Semantic priors constrain activation geometry, while model activations reorganize those priors into model-specific basins.
- Assistant-adjacent roles may form a dense semantic/procedural basin that makes low-yield role extraction harder, not easier.
- Theatrical roles may be easier to extract because their semantic cues are vivid, redundant, and far from generic assistant behavior.
- Bridge and low-density roles are useful probes for testing whether activation clusters are robust or prompt-corpus-dependent.

### Speculative hypotheses

- Some activation clusters may correspond to semantic superclusters that are sharpened by model internals rather than directly mirrored from prompt text.
- Current role coverage may miss important culturally situated identity regions, causing apparent voids or overlarge residual clusters.
- No-label activation tests may separate roles whose prompt-space topology is label-independent from roles that require explicit identity priming to reach the intended activation direction.

## 11. Recommended Next Experiments

Run a small no-label activation-space stress test before scaling. Use a mixed set: trickster as a high-yield theatrical positive control, editor as an assistant-adjacent failure case, one professional/helper role, one mythic or collective role, and one bridge role from `semantic_bridge_roles.csv`. The test should compare original-prompt and no-label vectors against Lu reference directions while tracking role-expression scoring, truncation, and adaptive stopping separately.
