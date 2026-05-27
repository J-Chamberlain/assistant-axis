# Cluster Overlap Analysis

## Research Question

This overlap study compares Lu et al. activation-space clusters with original prompt semantic clusters and no-label prompt semantic clusters. It uses existing cluster assignments and prior semantic-analysis artifacts only. No embeddings, activations, pod inference, or rollout generation were run.

## Data Sources

- `research/assistant_axis_methodology/semantic_vs_activation_geometry/cluster_assignments_comparison.csv`
- `research/assistant_axis_methodology/semantic_vs_activation_geometry/semantic_vs_activation_geometry_summary.json`
- `research/assistant_axis_methodology/deep_semantic_topology_analysis.json`
- `research/assistant_axis_methodology/semantic_bridge_roles.csv`

## Headline Results

- Roles analyzed: 275
- k=7 original-prompt ARI vs activation labels: 0.111
- k=7 no-label-prompt ARI vs activation labels: 0.130
- Stable anchors across activation, original semantic, and no-label semantic dominant regions: 73
- Bridge or migratory roles flagged by overlap criteria: 198

## Activation Cluster Overlaps at k=7

| Activation cluster | n | Dominant original semantic cluster | Original containment | Dominant no-label semantic cluster | No-label containment | Stable anchor examples |
|---|---:|---|---:|---|---:|---|
| `combative_iconoclast` | 8 | 3 | 0.625 | 2 | 0.875 | `contrarian`, `devils_advocate`, `maverick`, `provocateur`, `rebel` |
| `editorial` | 5 | 5 | 0.600 | 5 | 0.800 | `examiner`, `grader`, `screener` |
| `grounded_social` | 45 | 1 | 0.511 | 3 | 0.511 | `celebrity`, `criminal`, `daredevil`, `divorcee`, `exile`, `expatriate`, `graduate`, `grandparent` |
| `mythic_spiritual` | 61 | 4 | 0.426 | 0 | 0.475 | `aberration`, `alien`, `angel`, `chimera`, `demon`, `dreamer`, `eldritch`, `familiar` |
| `other` | 22 | 6 | 0.318 | 0 | 0.409 | `infant` |
| `procedural_professional` | 127 | 2 | 0.307 | 5 | 0.323 | `accountant`, `architect`, `archivist`, `biologist`, `builder`, `cartographer`, `chemist`, `collector` |
| `trickster_chaos` | 7 | 6 | 0.286 | 2 | 0.714 | `jester`, `trickster` |

Containment is asymmetric: it measures how much of an activation cluster falls inside the dominant semantic cluster. Low containment does not mean no relationship; it often means the activation cluster spans several semantic regions.

## Stable Basins

| Basin | Activation clusters | n | Stable anchors | Bridge roles | Interpretation |
|---|---|---:|---:|---:|---|
| `assistant_adjacent_procedural` | `editorial`, `procedural_professional` | 132 | 26 | 102 | A broad professional/helper basin. Editorial is semantically compact, but procedural-professional spreads across several semantic clusters, consistent with activation-space compression of many task-oriented roles. |
| `theatrical_fantastical` | `mythic_spiritual`, `trickster_chaos` | 68 | 20 | 47 | Semantic vividness survives label removal, but activation space separates playful/transgressive roles from broader mythic/fantastical roles more sharply than prompt taxonomy alone. |
| `collective_swarm` | `mythic_spiritual`, `procedural_professional` | 7 | 1 | 4 | Collective roles are compact in no-label prompt space, but activation labels distribute them across larger mythic/procedural regions, suggesting semantic coherence without a dedicated activation cluster in the available taxonomy. |
| `archetypal_social` | `grounded_social`, `mythic_spiritual`, `other` | 128 | 40 | 86 | Social, survival, mythic, and residual roles form overlapping gradients rather than crisp partitions. This is the main site of semantic-to-activation reorganization. |
| `destabilizing_liminal` | `combative_iconoclast`, `other`, `trickster_chaos` | 37 | 8 | 30 | Combative, playful, and residual roles contain many boundary cases. These are high-value probes for no-label activation tests because semantic ambiguity may be resolved or amplified in activations. |

## Stable Anchors

Stable anchors are roles that sit inside the dominant original-prompt semantic cluster and the dominant no-label semantic cluster for their activation-space cluster. They are not guaranteed to be activation centroids, but they are robust overlap representatives.

| Activation cluster | Anchor examples |
|---|---|
| `combative_iconoclast` | `contrarian`, `devils_advocate`, `maverick`, `provocateur`, `rebel` |
| `editorial` | `examiner`, `grader`, `screener` |
| `grounded_social` | `celebrity`, `criminal`, `daredevil`, `divorcee`, `exile`, `expatriate`, `graduate`, `grandparent`, `immigrant`, `newlywed`, `orphan`, `parent`, `pirate`, `prisoner`, `refugee` |
| `mythic_spiritual` | `aberration`, `alien`, `angel`, `chimera`, `demon`, `dreamer`, `eldritch`, `familiar`, `golem`, `homunculus`, `leviathan`, `tree`, `virtuoso`, `void`, `whale` |
| `other` | `infant` |
| `procedural_professional` | `accountant`, `architect`, `archivist`, `biologist`, `builder`, `cartographer`, `chemist`, `collector`, `coordinator`, `designer`, `dispatcher`, `entrepreneur`, `lawyer`, `librarian`, `marketer` |
| `trickster_chaos` | `jester`, `trickster` |

## Bridge and Migratory Roles

Bridge roles either migrate between semantic and activation-dominant regions, change original-to-no-label semantic cluster, or have low semantic-cluster margin in the deep topology analysis.

| Role | Activation cluster | Original k7 | No-label k7 | Bridge score | Notes |
|---|---|---:|---:|---:|---|
| `proofreader` | `editorial` | 6 | 4 | 5 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.042 |
| `mechanic` | `grounded_social` | 5 | 1 | 5 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.027 |
| `spy` | `grounded_social` | 3 | 4 | 5 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.001 |
| `sage` | `mythic_spiritual` | 6 | 1 | 5 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.006 |
| `advocate` | `procedural_professional` | 5 | 4 | 5 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.035 |
| `interpreter` | `procedural_professional` | 0 | 1 | 5 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.043 |
| `peacekeeper` | `procedural_professional` | 0 | 2 | 5 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.047 |
| `dilettante` | `trickster_chaos` | 4 | 1 | 5 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.023 |
| `actor` | `grounded_social` | 0 | 3 | 4 | original outside activation-dominant semantic region; changes under label removal; low margin 0.039 |
| `addict` | `grounded_social` | 1 | 0 | 4 | no-label outside activation-dominant semantic region; changes under label removal; low margin 0.025 |
| `chameleon` | `grounded_social` | 0 | 0 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; low margin 0.039 |
| `ancient` | `mythic_spiritual` | 1 | 3 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.049 |
| `mystic` | `mythic_spiritual` | 4 | 6 | 4 | no-label outside activation-dominant semantic region; changes under label removal; low margin 0.031 |
| `amnesiac` | `other` | 1 | 0 | 4 | original outside activation-dominant semantic region; changes under label removal; low margin 0.003 |
| `moderator` | `other` | 0 | 4 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.069 |
| `toddler` | `other` | 6 | 2 | 4 | no-label outside activation-dominant semantic region; changes under label removal; low margin 0.033 |
| `archaeologist` | `procedural_professional` | 3 | 1 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.065 |
| `detective` | `procedural_professional` | 3 | 1 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.056 |
| `ecosystem` | `procedural_professional` | 0 | 0 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; low margin 0.048 |
| `emissary` | `procedural_professional` | 0 | 5 | 4 | original outside activation-dominant semantic region; changes under label removal; low margin 0.020 |
| `futurist` | `procedural_professional` | 3 | 1 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.054 |
| `guardian` | `procedural_professional` | 0 | 0 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; low margin 0.008 |
| `negotiator` | `procedural_professional` | 0 | 5 | 4 | original outside activation-dominant semantic region; changes under label removal; low margin 0.049 |
| `technologist` | `procedural_professional` | 3 | 2 | 4 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal; low margin 0.020 |
| `workaholic` | `combative_iconoclast` | 5 | 0 | 3 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal |
| `auctioneer` | `grounded_social` | 2 | 4 | 3 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal |
| `bartender` | `grounded_social` | 2 | 5 | 3 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal |
| `blogger` | `grounded_social` | 6 | 4 | 3 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal |
| `chef` | `grounded_social` | 2 | 5 | 3 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal |
| `fixer` | `grounded_social` | 3 | 2 | 3 | original outside activation-dominant semantic region; no-label outside activation-dominant semantic region; changes under label removal |

## Focused Boundary-Role Checks

The user-requested boundary roles are mixed rather than uniformly migratory. Some stay inside the activation-dominant semantic region, while others move across semantic partitions or sit near low-margin boundaries.

| Role | Activation cluster | Original k7 | No-label k7 | Bridge score | Interpretation |
|---|---|---:|---:|---:|---|
| `skeptic` | `procedural_professional` | 3 | 2 | 3 | moderate boundary case; semantic grouping differs from at least one activation-dominant region |
| `philosopher` | `mythic_spiritual` | 3 | 1 | 3 | moderate boundary case; semantic grouping differs from at least one activation-dominant region |
| `strategist` | `procedural_professional` | 2 | 1 | 2 | moderate boundary case; semantic grouping differs from at least one activation-dominant region |
| `observer` | `procedural_professional` | 3 | 4 | 3 | moderate boundary case; semantic grouping differs from at least one activation-dominant region |
| `mediator` | `procedural_professional` | 0 | 5 | 2 | moderate boundary case; semantic grouping differs from at least one activation-dominant region |
| `negotiator` | `procedural_professional` | 0 | 5 | 4 | strong migratory/boundary case under overlap criteria |
| `editor` | `editorial` | 6 | 5 | 2 | moderate boundary case; semantic grouping differs from at least one activation-dominant region |
| `reviewer` | `procedural_professional` | 5 | 5 | 0 | stable enough under overlap criteria; not flagged as a major bridge role |
| `consultant` | `procedural_professional` | 5 | 1 | 3 | moderate boundary case; semantic grouping differs from at least one activation-dominant region |

Focused roles not present in the 275-role assignment table: `diplomat`.

## Interpretation

The strongest overlap is local rather than global. Editorial roles form a compact semantic and activation grouping; combative and trickster-like roles retain recognizable semantic structure; and professional/helper roles occupy a large region that activation space compresses into a broad procedural-professional basin. The weaker overlaps occur in large heterogeneous clusters where prompt semantics split the roles by genre, life situation, or communicative form while activation labels group them by broader enacted behavioral stance.

Activation-space clusters appear sharper in narrow basins and more compressed in broad basins. Editorial is the clearest case of a semantic structure that survives cleanly. Procedural-professional is the clearest case of compression: multiple semantic clusters of expertise, writing/media, evaluation, coordination, and technical problem solving map into one large activation cluster. Mythic-spiritual and grounded-social show reorganization rather than clean preservation, with survival, social-position, symbolic, and nonordinary roles crossing semantic boundaries.

The overlap pattern supports the view that activation geometry is not reducible to lexical semantics. Prompt-space semantics provide priors and local neighborhoods, but activation labels reorganize those neighborhoods around procedural/behavioral coherence. This is a limited claim: the analysis does not prove causality, and it does not replace activation-space no-label stress tests.

## Strongest Findings

- Semantic and activation clusters overlap partially, with stable local anchors but low global hard-cluster agreement.
- Editorial is the most stable activation-semantic overlap region.
- Procedural-professional compresses several semantic regions into one broad activation basin.
- Collective/swarm roles are semantically compact but do not form a dedicated activation cluster in the available labels.
- Bridge roles provide a targeted set for no-label activation stress testing.

## Speculative Findings

- Activation geometry may encode enacted behavioral stance more strongly than prompt-space semantic taxonomy alone.
- Theatrical roles may become more separable in activation space when their behavioral stance is distinct from generic assistant behavior.
- Assistant-adjacent roles may compress into the default assistant/procedural basin even when their prompt semantics are explicit.

## Recommended Next Experiment

Run a small no-label activation-space stress test that samples stable anchors, bridge roles, sparse/outlier roles, assistant-adjacent roles, and theatrical roles. The purpose should be to test whether no-label prompts still recover Lu reference directions and whether bridge roles snap into activation basins or remain unstable.
