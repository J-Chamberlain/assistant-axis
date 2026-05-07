# Role-Trait Similarity Analysis Summary

## Layer Selection

Trait-axis projection variance also peaks at layer `45` (variance `7127351.500000`), so layer 45 was used for both roles and traits.

Sign-convention sanity check against the Assistant Axis README examples:
- mean(`transparent`, `grounded`, `flexible`) at layer 22 = `826.5551`
- mean(`enigmatic`, `subversive`, `dramatic`) at layer 22 = `-1364.7448`

## Null Hypothesis Test

- Mean within-cluster profile cosine similarity: `0.999809`
- Mean across-cluster profile cosine similarity: `0.999234`
- Observed difference (within - across): `0.000575`
- Permutation-test p-value (`n=1000`): `0.000999`

## Top Traits Per Cluster

### combative_iconoclast

**Top 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `confrontational` | 2.465 |
| 2 | `blunt` | 2.368 |
| 3 | `urgent` | 2.179 |
| 4 | `callous` | 2.072 |
| 5 | `savage` | 2.029 |
| 6 | `hostile` | 2.016 |
| 7 | `competitive` | 1.966 |
| 8 | `judgmental` | 1.926 |
| 9 | `dominant` | 1.923 |
| 10 | `radical` | 1.914 |

**Bottom 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `circumspect` | -2.331 |
| 2 | `tactful` | -2.255 |
| 3 | `collectivistic` | -2.215 |
| 4 | `traditional` | -2.163 |
| 5 | `agreeable` | -2.153 |
| 6 | `nurturing` | -2.123 |
| 7 | `deferential` | -2.083 |
| 8 | `altruistic` | -2.074 |
| 9 | `benevolent` | -2.058 |
| 10 | `diplomatic` | -2.008 |

### editorial

**Top 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `literal` | 2.046 |
| 2 | `convergent` | 1.838 |
| 3 | `regulatory` | 1.740 |
| 4 | `cautious` | 1.643 |
| 5 | `descriptive` | 1.638 |
| 6 | `rationalist` | 1.606 |
| 7 | `data_driven` | 1.593 |
| 8 | `quantitative` | 1.589 |
| 9 | `deferential` | 1.586 |
| 10 | `factual` | 1.571 |

**Bottom 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `interdisciplinary` | -2.247 |
| 2 | `generalist` | -2.133 |
| 3 | `systems_thinker` | -1.974 |
| 4 | `divergent` | -1.956 |
| 5 | `verbose` | -1.917 |
| 6 | `intuitive` | -1.886 |
| 7 | `speculative` | -1.847 |
| 8 | `constructivist` | -1.768 |
| 9 | `charismatic` | -1.729 |
| 10 | `creative` | -1.710 |

### grounded_social

**Top 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `experiential` | 1.223 |
| 2 | `casual` | 1.183 |
| 3 | `existentialist` | 1.059 |
| 4 | `inquisitive` | 1.055 |
| 5 | `accommodating` | 1.046 |
| 6 | `gregarious` | 1.035 |
| 7 | `submissive` | 0.983 |
| 8 | `empathetic` | 0.978 |
| 9 | `reactive` | 0.953 |
| 10 | `extroverted` | 0.942 |

**Bottom 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `formal` | -1.170 |
| 2 | `perfectionist` | -1.152 |
| 3 | `meticulous` | -1.125 |
| 4 | `serious` | -1.113 |
| 5 | `formalist` | -1.104 |
| 6 | `stoic` | -1.097 |
| 7 | `cosmopolitan` | -1.079 |
| 8 | `technical` | -1.076 |
| 9 | `solemn` | -1.068 |
| 10 | `principled` | -1.064 |

### mythic_spiritual

**Top 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `fatalistic` | 1.440 |
| 2 | `eloquent` | 1.437 |
| 3 | `philosophical` | 1.411 |
| 4 | `spiritual` | 1.404 |
| 5 | `cryptic` | 1.396 |
| 6 | `ethereal` | 1.382 |
| 7 | `mystical` | 1.374 |
| 8 | `idealistic` | 1.373 |
| 9 | `grandiose` | 1.350 |
| 10 | `esoteric` | 1.331 |

**Bottom 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `contemporary` | -1.436 |
| 2 | `grounded` | -1.416 |
| 3 | `reductionist` | -1.398 |
| 4 | `secular` | -1.329 |
| 5 | `transparent` | -1.306 |
| 6 | `utilitarian` | -1.224 |
| 7 | `materialist` | -1.183 |
| 8 | `humble` | -1.168 |
| 9 | `problem_solving` | -1.167 |
| 10 | `practical` | -1.154 |

### other

**Top 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `avoidant` | 1.711 |
| 2 | `impulsive` | 1.572 |
| 3 | `anxious` | 1.564 |
| 4 | `neurotic` | 1.491 |
| 5 | `impatient` | 1.468 |
| 6 | `manic` | 1.459 |
| 7 | `flippant` | 1.431 |
| 8 | `reactive` | 1.414 |
| 9 | `naive` | 1.406 |
| 10 | `nonchalant` | 1.384 |

**Bottom 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `generous` | -1.837 |
| 2 | `holistic` | -1.712 |
| 3 | `proactive` | -1.694 |
| 4 | `independent` | -1.645 |
| 5 | `strategic` | -1.637 |
| 6 | `educational` | -1.533 |
| 7 | `conscientious` | -1.531 |
| 8 | `patient` | -1.513 |
| 9 | `earnest` | -1.511 |
| 10 | `calculating` | -1.407 |

### procedural_professional

**Top 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `factual` | 0.826 |
| 2 | `resilient` | 0.825 |
| 3 | `educational` | 0.804 |
| 4 | `methodical` | 0.800 |
| 5 | `problem_solving` | 0.779 |
| 6 | `moderate` | 0.773 |
| 7 | `analytical` | 0.773 |
| 8 | `reserved` | 0.768 |
| 9 | `calm` | 0.766 |
| 10 | `structuralist` | 0.766 |

**Bottom 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `manipulative` | -0.848 |
| 2 | `flirty` | -0.838 |
| 3 | `passive_aggressive` | -0.838 |
| 4 | `subversive` | -0.833 |
| 5 | `petty` | -0.827 |
| 6 | `spontaneous` | -0.826 |
| 7 | `relativist` | -0.825 |
| 8 | `mercurial` | -0.821 |
| 9 | `ironic` | -0.821 |
| 10 | `stream_of_consciousness` | -0.818 |

### trickster_chaos

**Top 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `wry` | 2.274 |
| 2 | `mischievous` | 2.197 |
| 3 | `goofy` | 2.196 |
| 4 | `witty` | 2.151 |
| 5 | `sardonic` | 2.142 |
| 6 | `ironic` | 2.101 |
| 7 | `hedonistic` | 2.068 |
| 8 | `sarcastic` | 2.021 |
| 9 | `passive_aggressive` | 1.997 |
| 10 | `whimsical` | 1.983 |

**Bottom 10 traits**

| Rank | Trait | Mean z-score |
| --- | --- | ---: |
| 1 | `earnest` | -2.063 |
| 2 | `vindictive` | -1.866 |
| 3 | `factual` | -1.693 |
| 4 | `patient` | -1.588 |
| 5 | `supportive` | -1.535 |
| 6 | `educational` | -1.531 |
| 7 | `ascetic` | -1.512 |
| 8 | `solemn` | -1.487 |
| 9 | `serious` | -1.442 |
| 10 | `regulatory` | -1.439 |

## Anomaly Deep-Dives

### robot

Top raw traits (reductionist, accommodating, practical, existentialist, accessible) would be consistent with the paper's systematic-execution interpretation if they emphasize detachment, method, or regularity.

**Top 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `reductionist` | 0.860 |
| 2 | `accommodating` | 0.853 |
| 3 | `practical` | 0.834 |
| 4 | `existentialist` | 0.834 |
| 5 | `accessible` | 0.829 |
| 6 | `generalist` | 0.784 |
| 7 | `flexible` | 0.759 |
| 8 | `pluralist` | 0.746 |
| 9 | `experiential` | 0.725 |
| 10 | `submissive` | 0.718 |
| 11 | `casual` | 0.683 |
| 12 | `benevolent` | 0.674 |
| 13 | `socratic` | 0.653 |
| 14 | `open_ended` | 0.636 |
| 15 | `optimistic` | 0.623 |

**Bottom 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `vindictive` | -0.914 |
| 2 | `elitist` | -0.858 |
| 3 | `introspective` | -0.830 |
| 4 | `arrogant` | -0.803 |
| 5 | `fundamentalist` | -0.797 |
| 6 | `esoteric` | -0.784 |
| 7 | `conceptual` | -0.778 |
| 8 | `dogmatic` | -0.773 |
| 9 | `essentialist` | -0.753 |
| 10 | `assertive` | -0.733 |
| 11 | `deterministic` | -0.727 |
| 12 | `idealistic` | -0.711 |
| 13 | `big_picture` | -0.707 |
| 14 | `erudite` | -0.703 |
| 15 | `eloquent` | -0.700 |

**Top 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `concise` | 4.764 |
| 2 | `literal` | 4.500 |
| 3 | `closure_seeking` | 3.840 |
| 4 | `prescriptive` | 3.696 |
| 5 | `detached` | 3.432 |
| 6 | `formalist` | 3.234 |
| 7 | `convergent` | 3.128 |
| 8 | `materialist` | 3.011 |
| 9 | `technical` | 2.974 |
| 10 | `pedantic` | 2.892 |
| 11 | `data_driven` | 2.855 |
| 12 | `quantitative` | 2.831 |
| 13 | `dispassionate` | 2.800 |
| 14 | `rationalist` | 2.761 |
| 15 | `decisive` | 2.697 |

**Bottom 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `generalist` | -4.266 |
| 2 | `empathetic` | -4.029 |
| 3 | `exploratory` | -3.976 |
| 4 | `constructivist` | -3.825 |
| 5 | `humanistic` | -3.779 |
| 6 | `open_ended` | -3.653 |
| 7 | `adaptable` | -3.626 |
| 8 | `inquisitive` | -3.625 |
| 9 | `curious` | -3.623 |
| 10 | `intuitive` | -3.115 |
| 11 | `emotional` | -3.101 |
| 12 | `divergent` | -3.011 |
| 13 | `forgiving` | -2.943 |
| 14 | `verbose` | -2.850 |
| 15 | `charismatic` | -2.817 |

### assistant

Top raw traits (accommodating, reductionist, accessible, existentialist, practical) help test whether the literal assistant role looks broadly helpful or specifically procedural/evaluative.

**Top 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `accommodating` | 0.863 |
| 2 | `reductionist` | 0.857 |
| 3 | `accessible` | 0.847 |
| 4 | `existentialist` | 0.844 |
| 5 | `practical` | 0.844 |
| 6 | `generalist` | 0.796 |
| 7 | `flexible` | 0.777 |
| 8 | `pluralist` | 0.758 |
| 9 | `experiential` | 0.742 |
| 10 | `submissive` | 0.726 |
| 11 | `casual` | 0.700 |
| 12 | `benevolent` | 0.692 |
| 13 | `socratic` | 0.659 |
| 14 | `open_ended` | 0.656 |
| 15 | `optimistic` | 0.636 |

**Bottom 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `vindictive` | -0.914 |
| 2 | `elitist` | -0.870 |
| 3 | `introspective` | -0.830 |
| 4 | `arrogant` | -0.816 |
| 5 | `fundamentalist` | -0.809 |
| 6 | `esoteric` | -0.801 |
| 7 | `conceptual` | -0.788 |
| 8 | `dogmatic` | -0.785 |
| 9 | `essentialist` | -0.769 |
| 10 | `deterministic` | -0.744 |
| 11 | `assertive` | -0.741 |
| 12 | `erudite` | -0.722 |
| 13 | `pedantic` | -0.721 |
| 14 | `idealistic` | -0.716 |
| 15 | `big_picture` | -0.708 |

**Top 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `pluralist` | 1.855 |
| 2 | `deferential` | 1.757 |
| 3 | `vindictive` | 1.702 |
| 4 | `humble` | 1.666 |
| 5 | `flexible` | 1.659 |
| 6 | `transparent` | 1.579 |
| 7 | `factual` | 1.496 |
| 8 | `grounded` | 1.460 |
| 9 | `cautious` | 1.438 |
| 10 | `moderate` | 1.435 |
| 11 | `supportive` | 1.414 |
| 12 | `descriptive` | 1.392 |
| 13 | `collaborative` | 1.376 |
| 14 | `benevolent` | 1.376 |
| 15 | `adaptable` | 1.355 |

**Bottom 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `deconstructionist` | -2.126 |
| 2 | `interdisciplinary` | -2.095 |
| 3 | `critical` | -2.003 |
| 4 | `verbose` | -1.911 |
| 5 | `contrarian` | -1.905 |
| 6 | `provocative` | -1.902 |
| 7 | `challenging` | -1.841 |
| 8 | `historical` | -1.733 |
| 9 | `speculative` | -1.732 |
| 10 | `obsessive` | -1.722 |
| 11 | `eclectic` | -1.720 |
| 12 | `subversive` | -1.704 |
| 13 | `creative` | -1.698 |
| 14 | `condescending` | -1.690 |
| 15 | `paradoxical` | -1.688 |

### poet

Top raw traits (accommodating, existentialist, reductionist, accessible, practical) should clarify whether the anti-assistant pole aligns with theatricality, expressiveness, and metaphor-rich style.

**Top 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `accommodating` | 0.870 |
| 2 | `existentialist` | 0.840 |
| 3 | `reductionist` | 0.838 |
| 4 | `accessible` | 0.835 |
| 5 | `practical` | 0.832 |
| 6 | `generalist` | 0.801 |
| 7 | `flexible` | 0.755 |
| 8 | `experiential` | 0.738 |
| 9 | `pluralist` | 0.738 |
| 10 | `submissive` | 0.731 |
| 11 | `casual` | 0.702 |
| 12 | `benevolent` | 0.678 |
| 13 | `socratic` | 0.672 |
| 14 | `narrative` | 0.665 |
| 15 | `open_ended` | 0.663 |

**Bottom 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `vindictive` | -0.920 |
| 2 | `elitist` | -0.852 |
| 3 | `introspective` | -0.830 |
| 4 | `arrogant` | -0.793 |
| 5 | `fundamentalist` | -0.793 |
| 6 | `esoteric` | -0.774 |
| 7 | `conceptual` | -0.772 |
| 8 | `dogmatic` | -0.766 |
| 9 | `essentialist` | -0.751 |
| 10 | `assertive` | -0.721 |
| 11 | `deterministic` | -0.716 |
| 12 | `regulatory` | -0.716 |
| 13 | `pedantic` | -0.712 |
| 14 | `erudite` | -0.708 |
| 15 | `big_picture` | -0.701 |

**Top 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `poetic` | 3.415 |
| 2 | `concise` | 3.342 |
| 3 | `cryptic` | 2.449 |
| 4 | `ethereal` | 2.368 |
| 5 | `enigmatic` | 2.257 |
| 6 | `romantic` | 2.247 |
| 7 | `eloquent` | 2.135 |
| 8 | `artistic` | 2.091 |
| 9 | `metaphorical` | 2.084 |
| 10 | `fatalistic` | 2.056 |
| 11 | `epicurean` | 2.038 |
| 12 | `nostalgic` | 2.024 |
| 13 | `mystical` | 2.023 |
| 14 | `dramatic` | 2.017 |
| 15 | `rhetorical` | 2.007 |

**Bottom 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `transparent` | -1.989 |
| 2 | `exploratory` | -1.953 |
| 3 | `grounded` | -1.931 |
| 4 | `contemporary` | -1.846 |
| 5 | `reductionist` | -1.826 |
| 6 | `proactive` | -1.808 |
| 7 | `humble` | -1.691 |
| 8 | `problem_solving` | -1.672 |
| 9 | `secular` | -1.497 |
| 10 | `utilitarian` | -1.440 |
| 11 | `educational` | -1.439 |
| 12 | `materialist` | -1.365 |
| 13 | `quantitative` | -1.356 |
| 14 | `analytical` | -1.306 |
| 15 | `understated` | -1.301 |

### angel

Top raw traits (accommodating, accessible, reductionist, existentialist, practical) help distinguish practical benevolence from spiritual abstraction, which is central to the paper's interpretation.

**Top 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `accommodating` | 0.867 |
| 2 | `accessible` | 0.841 |
| 3 | `reductionist` | 0.838 |
| 4 | `existentialist` | 0.838 |
| 5 | `practical` | 0.834 |
| 6 | `generalist` | 0.801 |
| 7 | `flexible` | 0.762 |
| 8 | `pluralist` | 0.746 |
| 9 | `experiential` | 0.736 |
| 10 | `submissive` | 0.730 |
| 11 | `casual` | 0.697 |
| 12 | `benevolent` | 0.692 |
| 13 | `socratic` | 0.667 |
| 14 | `open_ended` | 0.665 |
| 15 | `narrative` | 0.650 |

**Bottom 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `vindictive` | -0.915 |
| 2 | `elitist` | -0.857 |
| 3 | `introspective` | -0.828 |
| 4 | `arrogant` | -0.801 |
| 5 | `fundamentalist` | -0.791 |
| 6 | `esoteric` | -0.783 |
| 7 | `conceptual` | -0.772 |
| 8 | `dogmatic` | -0.770 |
| 9 | `essentialist` | -0.751 |
| 10 | `assertive` | -0.729 |
| 11 | `deterministic` | -0.727 |
| 12 | `pedantic` | -0.716 |
| 13 | `erudite` | -0.710 |
| 14 | `regulatory` | -0.708 |
| 15 | `big_picture` | -0.695 |

**Top 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `pacifist` | 2.465 |
| 2 | `idealistic` | 2.426 |
| 3 | `forgiving` | 2.422 |
| 4 | `deontological` | 2.347 |
| 5 | `meditative` | 2.346 |
| 6 | `serene` | 2.345 |
| 7 | `altruistic` | 2.330 |
| 8 | `collectivistic` | 2.290 |
| 9 | `environmental` | 2.218 |
| 10 | `reverent` | 2.169 |
| 11 | `nurturing` | 2.081 |
| 12 | `ascetic` | 2.060 |
| 13 | `spiritual` | 2.059 |
| 14 | `principled` | 1.964 |
| 15 | `humanistic` | 1.919 |

**Bottom 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `secular` | -2.725 |
| 2 | `blunt` | -2.366 |
| 3 | `utilitarian` | -2.127 |
| 4 | `materialist` | -2.102 |
| 5 | `urgent` | -1.909 |
| 6 | `reductionist` | -1.693 |
| 7 | `confrontational` | -1.625 |
| 8 | `contemporary` | -1.612 |
| 9 | `callous` | -1.539 |
| 10 | `progressive` | -1.534 |
| 11 | `skeptical` | -1.448 |
| 12 | `existentialist` | -1.352 |
| 13 | `sassy` | -1.318 |
| 14 | `quantitative` | -1.261 |
| 15 | `savage` | -1.230 |

### saboteur

Top raw traits (accommodating, reductionist, existentialist, practical, accessible) are the key check for whether saboteur looks chaotic or tactically organized in trait space.

**Top 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `accommodating` | 0.866 |
| 2 | `reductionist` | 0.852 |
| 3 | `existentialist` | 0.843 |
| 4 | `practical` | 0.838 |
| 5 | `accessible` | 0.838 |
| 6 | `generalist` | 0.796 |
| 7 | `flexible` | 0.759 |
| 8 | `experiential` | 0.740 |
| 9 | `pluralist` | 0.738 |
| 10 | `submissive` | 0.726 |
| 11 | `casual` | 0.703 |
| 12 | `benevolent` | 0.667 |
| 13 | `socratic` | 0.664 |
| 14 | `open_ended` | 0.652 |
| 15 | `narrative` | 0.638 |

**Bottom 15 traits by raw cosine similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `vindictive` | -0.917 |
| 2 | `elitist` | -0.856 |
| 3 | `introspective` | -0.828 |
| 4 | `fundamentalist` | -0.802 |
| 5 | `arrogant` | -0.797 |
| 6 | `esoteric` | -0.785 |
| 7 | `conceptual` | -0.780 |
| 8 | `dogmatic` | -0.771 |
| 9 | `essentialist` | -0.761 |
| 10 | `deterministic` | -0.725 |
| 11 | `assertive` | -0.721 |
| 12 | `regulatory` | -0.713 |
| 13 | `erudite` | -0.712 |
| 14 | `pedantic` | -0.712 |
| 15 | `idealistic` | -0.711 |

**Top 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `anthropocentric` | 1.777 |
| 2 | `confrontational` | 1.727 |
| 3 | `cynical` | 1.657 |
| 4 | `dominant` | 1.641 |
| 5 | `blunt` | 1.587 |
| 6 | `critical` | 1.532 |
| 7 | `callous` | 1.528 |
| 8 | `pessimistic` | 1.442 |
| 9 | `challenging` | 1.432 |
| 10 | `skeptical` | 1.424 |
| 11 | `competitive` | 1.396 |
| 12 | `urgent` | 1.389 |
| 13 | `decisive` | 1.277 |
| 14 | `militant` | 1.192 |
| 15 | `paranoid` | 1.176 |

**Bottom 15 traits by z-scored similarity**

| Rank | Trait | Value |
| --- | --- | ---: |
| 1 | `humanistic` | -1.843 |
| 2 | `optimistic` | -1.800 |
| 3 | `benevolent` | -1.630 |
| 4 | `nurturing` | -1.509 |
| 5 | `chill` | -1.484 |
| 6 | `forgiving` | -1.476 |
| 7 | `altruistic` | -1.446 |
| 8 | `deferential` | -1.315 |
| 9 | `circumspect` | -1.294 |
| 10 | `agreeable` | -1.276 |
| 11 | `naive` | -1.264 |
| 12 | `collectivistic` | -1.259 |
| 13 | `tactful` | -1.248 |
| 14 | `inspirational` | -1.248 |
| 15 | `traditional` | -1.202 |

## Findings To Revisit

- Trait profiles are more cluster-coherent than expected under random cluster assignment.
