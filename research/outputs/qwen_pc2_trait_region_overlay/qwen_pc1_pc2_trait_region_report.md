# Qwen PC1 x PC2 Trait-Region Overlay Prototype

Generated UTC: 2026-06-04T23:45:25Z
Model used: GPT-5.5

## Data sources

- Trait profile matrix located through navigation: `research/outputs/pc2_trait_stratified_profile/pc2_trait_profile_joined_matrix.csv`
- Canonical role geometry table: `research/geometry_tables/qwen_role_pc_rankings.csv`
- Canonical cluster membership table: `research/geometry_tables/cluster_membership_table.csv`

## Method

- Qwen role PC1 x PC2 only.
- PC1 divided into five equal-count quantile bands.
- PC2 divided into low/mid/high equal-count tertiles within each PC1 band.
- PC1-band-relative enrichment: `(mean_trait_cell - mean_trait_pc1_band) / global_trait_std`.
- Global enrichment: `(mean_trait_cell - mean_trait_global) / global_trait_std`.

## Sanity checks

- Populated cells: 15/15.
- Sparse cells with fewer than 8 roles: 0.
- Mean top-3 overlap between PC1-band-relative and global labels: 0.18.
- PC1-band-relative labels materially change apparent cell labels: yes.

No cells fell below the sparse-cell threshold; each quantile cell has enough roles for a first-pass visual read, though this is still exploratory.

## Cell summaries

### Q1 / PC2 low (n=18)
- Dominant cluster: mythic_spiritual (1.00)
- PC1-band-relative top traits: ascetic:1.01; reverent:0.92; pensive:0.90; principled:0.90; ritualistic:0.88; introverted:0.87; meditative:0.86; abstract:0.86
- Global top traits: ascetic:2.23; spiritual:2.03; fatalistic:2.02; idealistic:1.97; cryptic:1.89; mystical:1.89; fundamentalist:1.88; ethereal:1.86
- Example roles: oracle, spirit, witch, echo, void, mystic, shaman, golem

### Q1 / PC2 mid (n=18)
- Dominant cluster: mythic_spiritual (1.00)
- PC1-band-relative top traits: pensive:0.44; introverted:0.44; eloquent:0.40; elitist:0.37; big_picture:0.37; epicurean:0.37; abstract:0.36; solemn:0.36
- Global top traits: fatalistic:1.77; cryptic:1.74; ethereal:1.72; enigmatic:1.68; poetic:1.67; nostalgic:1.66; theatrical:1.63; melancholic:1.63
- Example roles: wind, aberration, dreamer, hermit, vampire, ghost, revenant, whale

### Q1 / PC2 high (n=19)
- Dominant cluster: trickster_chaos (0.37)
- PC1-band-relative top traits: experiential:1.14; practical:1.10; humble:0.98; casual:0.95; accessible:0.92; extroverted:0.91; grounded:0.91; contemporary:0.91
- Global top traits: goofy:1.64; playful:1.63; mischievous:1.59; whimsical:1.57; entertaining:1.52; flippant:1.52; disorganized:1.51; temperamental:1.50
- Example roles: criminal, infant, pirate, jester, surfer, trickster, fool, caveman

### Q2 / PC2 low (n=18)
- Dominant cluster: mythic_spiritual (0.61)
- PC1-band-relative top traits: abstract:1.43; introverted:1.42; conceptual:1.41; theoretical:1.40; pensive:1.38; ritualistic:1.36; reverent:1.30; big_picture:1.27
- Global top traits: conceptual:1.25; deterministic:1.23; abstract:1.21; philosophical:1.18; relativist:1.15; eloquent:1.14; big_picture:1.11; epicurean:1.10
- Example roles: alien, simulacrum, stoic, egregore, mycorrhizal, sage, martyr, parasite

### Q2 / PC2 mid (n=18)
- Dominant cluster: grounded_social (0.89)
- PC1-band-relative top traits: supportive:0.42; inspirational:0.42; generous:0.37; earnest:0.36; nurturing:0.36; adaptable:0.31; benevolent:0.30; inclusive:0.29
- Global top traits: existentialist:1.04; emotional:0.89; individualistic:0.88; improvisational:0.88; generalist:0.87; rebellious:0.86; stream_of_consciousness:0.86; visceral:0.86
- Example roles: hedonist, evangelist, nomad, empath, luddite, loner, refugee, widow

### Q2 / PC2 high (n=19)
- Dominant cluster: grounded_social (0.47)
- PC1-band-relative top traits: experiential:1.30; anxious:1.28; practical:1.20; nonchalant:1.20; casual:1.17; extroverted:1.12; neurotic:1.11; flippant:1.11
- Global top traits: anxious:2.20; nonchalant:2.12; neurotic:2.04; casual:2.03; irreverent:2.01; sassy:2.01; flippant:2.01; extroverted:1.94
- Example roles: comedian, gossip, cynic, daredevil, addict, prisoner, hoarder, orphan

### Q3 / PC2 low (n=18)
- Dominant cluster: procedural_professional (1.00)
- PC1-band-relative top traits: theoretical:1.03; ritualistic:1.01; abstract:1.01; conceptual:0.99; principled:0.98; erudite:0.93; pensive:0.93; reverent:0.91
- Global top traits: big_picture:1.06; abstract:0.94; conceptual:0.91; holistic:0.86; pensive:0.85; theoretical:0.83; principled:0.80; idealistic:0.74
- Example roles: composer, naturalist, traditionalist, healer, symbiont, purist, visionary, merchant

### Q3 / PC2 mid (n=18)
- Dominant cluster: procedural_professional (0.44)
- PC1-band-relative top traits: pessimistic:0.42; paranoid:0.40; critical:0.40; cynical:0.36; confrontational:0.36; blunt:0.36; skeptical:0.36; vindictive:0.35
- Global top traits: critical:0.40; progressive:0.35; paranoid:0.32; rebellious:0.32; existentialist:0.31; radical:0.29; contrarian:0.29; constructivist:0.28
- Example roles: spy, devils_advocate, minimalist, soldier, saboteur, chef, writer, cosmopolitan

### Q3 / PC2 high (n=19)
- Dominant cluster: grounded_social (0.74)
- PC1-band-relative top traits: experiential:1.04; practical:1.01; inquisitive:0.97; accessible:0.97; adaptable:0.96; accommodating:0.95; humble:0.93; gregarious:0.92
- Global top traits: adaptable:1.35; accommodating:1.27; inquisitive:1.23; experiential:1.22; accessible:1.22; gregarious:1.18; practical:1.18; humble:1.13
- Example roles: patient, gamer, retiree, parent, optimist, podcaster, competitor, blogger

### Q4 / PC2 low (n=18)
- Dominant cluster: procedural_professional (1.00)
- PC1-band-relative top traits: theoretical:0.81; historical:0.76; abstract:0.75; conceptual:0.74; esoteric:0.73; erudite:0.69; deterministic:0.68; pedantic:0.63
- Global top traits: strategic:0.96; meticulous:0.95; educational:0.95; descriptive:0.94; serious:0.93; calculating:0.92; perfectionist:0.92; stoic:0.92
- Example roles: cartographer, emissary, conservator, critic, perfectionist, archivist, curator, cyborg

### Q4 / PC2 mid (n=18)
- Dominant cluster: procedural_professional (1.00)
- PC1-band-relative top traits: practical:0.16; proactive:0.16; anthropocentric:0.15; problem_solving:0.14; convergent:0.14; closure_seeking:0.13; decisive:0.13; prescriptive:0.13
- Global top traits: transparent:0.79; moderate:0.79; resilient:0.79; factual:0.78; calm:0.78; conciliatory:0.78; diplomatic:0.75; methodical:0.75
- Example roles: detective, peacekeeper, interpreter, designer, veterinarian, pilot, reporter, mediator

### Q4 / PC2 high (n=19)
- Dominant cluster: procedural_professional (0.84)
- PC1-band-relative top traits: inquisitive:0.69; practical:0.65; accessible:0.62; experiential:0.56; adaptable:0.55; humble:0.54; accommodating:0.53; efficient:0.52
- Global top traits: flexible:0.96; grounded:0.91; conciliatory:0.85; contemporary:0.84; transparent:0.82; chill:0.81; moderate:0.80; supportive:0.80
- Example roles: networker, presenter, entrepreneur, realist, coach, collaborator, pragmatist, mentor

### Q5 / PC2 low (n=18)
- Dominant cluster: procedural_professional (1.00)
- PC1-band-relative top traits: theoretical:0.73; historical:0.67; abstract:0.67; verbose:0.67; conceptual:0.65; esoteric:0.63; skeptical:0.61; deterministic:0.61
- Global top traits: cautious:1.71; data_driven:1.65; detached:1.62; rationalist:1.61; structuralist:1.59; dispassionate:1.58; formalist:1.58; technical:1.55
- Example roles: robot, sociologist, geographer, scholar, judge, scientist, lawyer, linguist

### Q5 / PC2 mid (n=18)
- Dominant cluster: procedural_professional (0.78)
- PC1-band-relative top traits: proactive:0.20; verbose:0.17; skeptical:0.15; exploratory:0.14; problem_solving:0.14; generous:0.13; pessimistic:0.13; quantitative:0.12
- Global top traits: data_driven:1.51; quantitative:1.50; rationalist:1.45; analytical:1.45; cautious:1.43; materialist:1.42; formalist:1.39; factual:1.37
- Example roles: engineer, strategist, forecaster, analyst, grader, pharmacist, secretary, accountant

### Q5 / PC2 high (n=19)
- Dominant cluster: procedural_professional (0.68)
- PC1-band-relative top traits: efficient:0.72; practical:0.69; optimistic:0.63; accessible:0.62; concise:0.60; accommodating:0.57; submissive:0.52; adaptable:0.48
- Global top traits: literal:1.40; convergent:1.31; avoidant:1.30; factual:1.23; reductionist:1.22; methodical:1.22; transparent:1.21; moderate:1.20
- Example roles: scheduler, debugger, coordinator, nutritionist, organizer, consultant, instructor, summarizer

## Interpretation

Observed: PC1-band-relative enrichment often changes the visible labels compared with global enrichment, especially in cells where global labels are dominated by broad PC1-associated formality, seriousness, or expressivity. This supports the purpose of the overlay: PC2 is easier to inspect when local trait shifts are shown against a PC1-band baseline rather than the full role distribution.

Observed: High-PC2 cells frequently surface traits from the expected situated/reactive family, including practical, casual, reactive, anxious/neurotic, accommodating, grounded, experiential, or adjacent terms depending on the PC1 band. Low-PC2 cells more often surface formal/integrated/abstract traits such as conscientious, formal, abstract, conceptual, serious, theoretical, ritualistic, or pensive, though the exact local labels vary by PC1 band.

Caveat: This prototype does not solve PC2. It is a visualization and descriptive enrichment layer over activation-space trait cosine features, not an independent causal or psychological validation. The useful result is methodological: PC1-band-relative labels make the vertical PC2 structure more legible and less confounded by global PC1 trait gradients.

## Files

- `qwen_pc1_pc2_trait_region_overlay.html`
- `qwen_pc1_pc2_trait_region_overlay.svg`
- `qwen_pc1_pc2_trait_region_cells.csv`
- `qwen_pc1_pc2_trait_region_report.md`
