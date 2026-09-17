# AA-17 three-model exploratory trait factor analysis

## Decision

The 275 × 240 persona-by-trait matrix **passed** the phase gate. The factor solution is classified **C: partially shared factors with substantial model-specific structure**. Qwen has five individually stable axes under the frozen rule; Llama and Gemma have stable subspaces with some individually unresolved axes. One strong loading pattern recurs in all three models, while another recurs in Llama and Gemma. These are candidate latent common dimensions of same-space cosine profiles, not causal traits or human personality constructs.

## Retention and diagnostics

| Model | Parallel factors | MAP minimum | Eigenvalues > 1 (descriptive) | Bootstrap median minimum subspace correlation | Clean | Cross-loading | Weak communality |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen | 5 | 15 | 8 | 0.986 | 65 | 175 | 0 |
| Llama | 6 | 15 | 9 | 0.986 | 69 | 171 | 0 |
| Gemma | 6 | 15 | 9 | 0.975 | 58 | 182 | 0 |

Parallel analysis uses 100 independent within-column permutations (marginals preserved). MAP reaches its tested boundary at 15 factors in every model, so it gives no interior count. Heldout Gaussian likelihood also keeps improving through the candidate maximum; it does not corroborate a sharp five/six-factor optimum. The headline count is the predeclared parallel-analysis count and is a compact descriptive choice, not a unique true dimension. The ordinary correlation condition numbers range from ~2.6e9 to 4.5e10, making the shrinkage solution primary. Candidate fits, the ordinary input sensitivity, redundancy sensitivity, varimax sensitivity, and 3-fold heldout likelihood are recorded in `candidate_factor_fit.csv`. High cosine collinearity reflects shared activation geometry and limits claims of unique factors.

## Factor poles and stability

### Qwen

- **Observed Qwen_F1:** positive earnest (+1.02), patient (+0.97), resilient (+0.95), conscientious (+0.93), calm (+0.91); negative nonchalant (-1.00), anxious (-0.98), petty (-0.98), flippant (-0.98), wry (-0.98). Bootstrap median/q10 congruence 1.00/0.99; split-half median 0.99; individually stable. **Interpretation:** candidate label: steady accountability; positive pole reads as earnest patience and diligence, negative pole as flippant anxious antagonism. Plausible alternative: composed persistence. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Qwen_F2:** positive efficient (+0.85), concise (+0.79), optimistic (+0.71), egalitarian (+0.66), accessible (+0.62); negative verbose (-0.86), skeptical (-0.75), pedantic (-0.72), cautious (-0.70), specialized (-0.63). Bootstrap median/q10 congruence 0.99/0.98; split-half median 0.98; individually stable. **Interpretation:** candidate label: communication economy; positive pole reads as concise accessible efficiency, negative pole as verbose skeptical caution. Plausible alternative: streamlined versus qualified delivery. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Qwen_F3:** positive contemporary (+1.01), exploratory (+0.85), grounded (+0.84), utilitarian (+0.81), problem_solving (+0.80); negative deontological (-0.95), ascetic (-0.95), idealistic (-0.93), fundamentalist (-0.89), fatalistic (-0.87). Bootstrap median/q10 congruence 1.00/1.00; split-half median 0.99; individually stable. **Interpretation:** candidate label: pragmatic contemporaneity; positive pole reads as contemporary grounded pragmatism, negative pole as ascetic deontological idealism. Plausible alternative: grounded utility versus principled idealism. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Qwen_F4:** positive avoidant (+0.67), understated (+0.67), literal (+0.60), traditional (+0.50), reductionist (+0.42); negative systems_thinker (-1.02), holistic (-0.95), interdisciplinary (-0.84), generous (-0.84), curious (-0.77). Bootstrap median/q10 congruence 0.99/0.99; split-half median 0.97; individually stable. **Interpretation:** candidate label: narrow literalism; positive pole reads as literal understated withdrawal, negative pole as holistic systems curiosity. Plausible alternative: low versus high integrative reach. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Qwen_F5:** positive decisive (+1.05), closure_seeking (+0.99), dominant (+0.88), urgent (+0.71), confident (+0.68); negative open_ended (-0.77), humble (-0.73), pluralist (-0.72), circumspect (-0.67), deferential (-0.67). Bootstrap median/q10 congruence 0.99/0.98; split-half median 0.94; individually stable. **Interpretation:** candidate label: closure urgency; positive pole reads as decisive dominant closure, negative pole as humble open-ended circumspection. Plausible alternative: assertive finality versus exploratory restraint. **Hypothesis:** this reading may generalize to behavior, pending independent testing.

### Llama

- **Observed Llama_F1:** positive optimistic (+0.97), forgiving (+0.90), collectivistic (+0.90), agreeable (+0.86), altruistic (+0.83); negative confrontational (-1.03), pessimistic (-0.94), cynical (-0.93), callous (-0.82), militant (-0.82). Bootstrap median/q10 congruence 1.00/0.97; split-half median 0.98; individually stable. **Interpretation:** candidate label: cooperative optimism; positive pole reads as optimistic cooperative care, negative pole as cynical confrontational harshness. Plausible alternative: warmth versus antagonism. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Llama_F2:** positive contemporary (+0.94), secular (+0.86), humble (+0.73), transparent (+0.70), grounded (+0.67); negative ascetic (-0.87), essentialist (-0.86), spiritual (-0.86), mystical (-0.85), ethereal (-0.84). Bootstrap median/q10 congruence 0.99/0.95; split-half median 0.99; individually stable. **Interpretation:** candidate label: secular groundedness; positive pole reads as contemporary secular groundedness, negative pole as spiritual mystical essentialism. Plausible alternative: contemporary versus transcendent framing. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Llama_F3:** positive empathetic (+0.92), emotional (+0.87), gregarious (+0.79), humanistic (+0.75), existentialist (+0.68); negative detached (-0.92), data_driven (-0.89), descriptive (-0.84), dispassionate (-0.83), rationalist (-0.79). Bootstrap median/q10 congruence 0.99/0.95; split-half median 0.97; individually stable. **Interpretation:** candidate label: empathic expression; positive pole reads as emotional empathic sociability, negative pole as detached analytical description. Plausible alternative: affective versus detached register. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Llama_F4:** positive traditional (+0.84), regulatory (+0.57), deferential (+0.49), understated (+0.40), convergent (+0.36); negative progressive (-0.83), adventurous (-0.82), innovative (-0.80), animated (-0.73), futuristic (-0.71). Bootstrap median/q10 congruence 0.96/0.55; split-half median 0.88; axis unresolved. **Interpretation:** no semantic label assigned to an unresolved individual axis. **Hypothesis:** the broader factor subspace may support a more stable reading.
- **Observed Llama_F5:** positive open_ended (+0.86), inquisitive (+0.62), deferential (+0.60), constructivist (+0.58), cautious (+0.58); negative closure_seeking (-0.96), decisive (-0.74), prescriptive (-0.66), convergent (-0.58), urgent (-0.55). Bootstrap median/q10 congruence 0.95/0.68; split-half median 0.79; axis unresolved. **Interpretation:** no semantic label assigned to an unresolved individual axis. **Hypothesis:** the broader factor subspace may support a more stable reading.
- **Observed Llama_F6:** positive verbose (+0.85), generous (+0.80), proactive (+0.75), principled (+0.74), big_picture (+0.74); negative avoidant (-0.87), concise (-0.87), efficient (-0.85), literal (-0.83), naive (-0.81). Bootstrap median/q10 congruence 0.99/0.82; split-half median 0.70; axis unresolved. **Interpretation:** no semantic label assigned to an unresolved individual axis. **Hypothesis:** the broader factor subspace may support a more stable reading.

### Gemma

- **Observed Gemma_F1:** positive vindictive (+0.75), concise (+0.61), earnest (+0.59), convergent (+0.57), solemn (+0.51); negative divergent (-0.89), verbose (-0.75), goofy (-0.67), mischievous (-0.64), witty (-0.63). Bootstrap median/q10 congruence 0.97/0.94; split-half median 0.87; individually stable. **Interpretation:** candidate label: convergent gravity; positive pole reads as concise solemn convergence, negative pole as divergent playful verbosity. Plausible alternative: compression versus playful expansion. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Gemma_F2:** positive accessible (+0.63), casual (+0.54), generalist (+0.54), practical (+0.54), efficient (+0.52); negative pedantic (-0.89), introspective (-0.76), specialized (-0.71), technical (-0.70), skeptical (-0.69). Bootstrap median/q10 congruence 0.98/0.87; split-half median 0.93; individually stable. **Interpretation:** candidate label: accessible practicality; positive pole reads as accessible practical generalism, negative pole as pedantic technical introspection. Plausible alternative: generalist versus specialized register. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Gemma_F3:** positive tactful (+0.88), collectivistic (+0.81), optimistic (+0.80), agreeable (+0.78), diplomatic (+0.77); negative blunt (-0.94), confrontational (-0.94), challenging (-0.86), urgent (-0.86), critical (-0.83). Bootstrap median/q10 congruence 0.99/0.95; split-half median 0.89; individually stable. **Interpretation:** candidate label: diplomatic cooperation; positive pole reads as tactful cooperative optimism, negative pole as blunt urgent confrontation. Plausible alternative: tact versus confrontation. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Gemma_F4:** positive literal (+0.86), avoidant (+0.72), understated (+0.54), concise (+0.51), materialist (+0.49); negative generous (-0.82), systems_thinker (-0.80), proactive (-0.80), holistic (-0.80), generalist (-0.78). Bootstrap median/q10 congruence 0.98/0.85; split-half median 0.81; individually stable. **Interpretation:** candidate label: literal restraint; positive pole reads as literal concise withdrawal, negative pole as proactive holistic generosity. Plausible alternative: narrow versus expansive response. **Hypothesis:** this reading may generalize to behavior, pending independent testing.
- **Observed Gemma_F5:** positive socratic (+0.98), open_ended (+0.82), inquisitive (+0.76), submissive (+0.74), introspective (+0.74); negative closure_seeking (-0.91), prescriptive (-0.84), dominant (-0.71), decisive (-0.68), principled (-0.58). Bootstrap median/q10 congruence 0.98/0.89; split-half median 0.77; axis unresolved. **Interpretation:** no semantic label assigned to an unresolved individual axis. **Hypothesis:** the broader factor subspace may support a more stable reading.
- **Observed Gemma_F6:** positive spiritual (+0.97), idealistic (+0.94), mystical (+0.94), meditative (+0.93), ethereal (+0.91); negative secular (-0.98), contemporary (-0.95), grounded (-0.90), utilitarian (-0.90), reductionist (-0.89). Bootstrap median/q10 congruence 1.00/0.99; split-half median 0.98; individually stable. **Interpretation:** candidate label: spiritual idealism; positive pole reads as spiritual idealist mysticism, negative pole as secular grounded utility. Plausible alternative: transcendent versus pragmatic framing. **Hypothesis:** this reading may generalize to behavior, pending independent testing.

## Cross-model comparison

- **Observed Llama–Gemma:** matched absolute Tucker congruence [0.9, 0.91, 0.83, 0.52, 0.65, 0.79], mean 0.77; minimum subspace canonical correlation 0.49; largest principal angle 60.7°; trait-label permutation p=0.010. Individual axes are matched by loadings, not factor number.
- **Observed Qwen–Gemma:** matched absolute Tucker congruence [0.79, 0.77, 0.93, 0.79, 0.73], mean 0.80; minimum subspace canonical correlation 0.78; largest principal angle 39.0°; trait-label permutation p=0.010. Individual axes are matched by loadings, not factor number.
- **Observed Qwen–Llama:** matched absolute Tucker congruence [0.73, 0.75, 0.92, 0.79, 0.61], mean 0.76; minimum subspace canonical correlation 0.82; largest principal angle 35.1°; trait-label permutation p=0.010. Individual axes are matched by loadings, not factor number.

The clearest all-model match is Qwen F3, Llama F2, and Gemma F6 (absolute Tucker congruence 0.919/0.930/0.915 pairwise). Llama F1 and Gemma F3 form a further two-model match (0.896). The broader Qwen–Llama and Qwen–Gemma subspaces agree more than the full Llama–Gemma six-dimensional subspaces, whose weakest canonical correlation is 0.49. A signed correlation changes under arbitrary factor polarity. The alignment CSV retains signed and absolute matching information plus the traits of greatest disagreement. `cross_model_additional_subspace.csv` compares the fifth-dimensional shared Qwen subspace with each larger six-dimensional subspace and isolates each additional direction without equating an arbitrary factor number to the extra dimension.

## Prior grouping and human bridge readiness

The five prior editorial groups are semantic, hand-selected triplets covering 15/240 traits, shared across models. Their factor assignments are in `prior_trait_grouping_audit.md`. Agreement is descriptive and cannot validate the numerical solution. The bridge audit below counts traits whose primary absolute loading reaches 0.30; it does not fit or interpret SAPA data.

| Model factor | Indicators | 45 direct | 74 total | No proxy | Poor coverage |
|---|---:|---:|---:|---:|---|
| Qwen_F1 | 119 | 32 | 46 | 73 | False |
| Qwen_F2 | 21 | 2 | 5 | 16 | True |
| Qwen_F3 | 60 | 5 | 10 | 50 | False |
| Qwen_F4 | 17 | 2 | 4 | 13 | True |
| Qwen_F5 | 23 | 4 | 9 | 14 | False |
| Llama_F1 | 64 | 17 | 22 | 42 | False |
| Llama_F2 | 56 | 6 | 12 | 44 | False |
| Llama_F3 | 35 | 6 | 9 | 26 | False |
| Llama_F4 | 15 | 5 | 6 | 9 | False |
| Llama_F5 | 13 | 1 | 2 | 11 | True |
| Llama_F6 | 57 | 10 | 23 | 34 | False |
| Gemma_F1 | 32 | 7 | 12 | 20 | False |
| Gemma_F2 | 25 | 5 | 6 | 19 | False |
| Gemma_F3 | 58 | 17 | 24 | 34 | False |
| Gemma_F4 | 18 | 2 | 4 | 14 | True |
| Gemma_F5 | 17 | 4 | 6 | 11 | False |
| Gemma_F6 | 90 | 10 | 22 | 68 | False |

Factor-level aggregation could reduce duplication where mapped human proxies reuse SAPA item IDs; `human_bridge_factor_coverage.csv` counts those reuses. It does not create a human factor score, and item reuse must be resolved before later human comparisons.

## Limits and next gate

Every original trait retains its full loading pattern, 20-bootstrap aligned loading interval in `factor_loading_uncertainty.csv`, and primary/cross-loading assignment frequency. Factor scores are regression summaries of model persona cosine profiles, with residual profile variance and bootstrap SD in the score table. These resampling measures do not correct upstream vector measurement uncertainty. No new model inference, GPU, RunPod, HiFWB scoring, respondent-level data, SAPA factor comparison, or viewer was used. The next SAPA/HiFWB stage can use the stable, bridge-covered candidates as hypotheses for an independent test. Poorly covered or axis-unresolved factors should be deferred or compared as subspaces.
