## 12. Research Agenda

### A. Questions answerable with the current dataset and open-weight tools

These questions can be pursued immediately by outside researchers using the released vectors, the current 275-role basis, and additional open-weight experiments. They matter because they determine how much of the current interpretation is already recoverable without frontier-model access, and they provide the shortest path to replication, refinement, and falsification. Each of these questions has a concrete experimental design: they require only the released vectors, additional role descriptions, or open-weight steering experiments, and could in principle be completed within weeks.

- Would the `assistant` archetype rise materially if it were represented by richer natural-language persona descriptions rather than a single role label?
- Are editorial roles top-ranked because they are especially aligned with RLHF-style critique behavior, or because they minimize stylistic variance more generally?
- Does the distinction between careful-evaluator roles and expressive or mythic roles remain as strong under independent human annotation of the 275-role inventory?
- Why does `robot` rank high while `angel` and the broader mythic cluster rank low? Is the axis fundamentally tracking procedural orderliness over prosocial orientation, and do separate factors such as ambiguity, narrative abstraction, or stylistic excess independently predict anti-assistant placement?
- Why does `saboteur` move upward at layer 45? Does the deepest-layer geometry privilege tactical organization even when the role semantics are adversarial?
- Where would explicitly safety-relevant missing archetypes such as `sycophant`, `reward-hacker`, `whistleblower`, or `bureaucrat` fall if the current role inventory were expanded?
- Can open-weight steering experiments move a role like `poet` toward the assistant pole while preserving local semantic identity, or does movement necessarily collapse expressive style?
- Can the boundary topology findings be replicated using role-vector space distances rather than trait-space distances, and do the two spaces agree on which roles are most geometrically volatile?

### B. Questions requiring cross-model comparison

These questions require running the same analysis across multiple open-weight model families and training regimes. They matter because the present paper is strongest as a geometry claim within one model, while the fellowship-relevant next step is to determine which findings are universal, which are family-specific, and which are artifacts of one training pipeline.

- Does the most discriminative layer remain near the top of the network across model families? Preliminary cross-model comparison between Gemma 2 27B (layer 45) and Qwen 3 32B (layer 63) suggests yes, both models concentrate persona differentiation in the final layers, though the ranking structure diverges meaningfully between models, with a Spearman correlation of 0.67 across 275 shared roles.
- How stable are the cluster structures and axis rankings across model families, sizes, and instruction-tuning recipes, and do the same seven coarse clusters emerge in Llama and Qwen or does the persona manifold partition differently under other pretraining corpora?
- Does the `robot` vs. `angel` divergence persist across model families, or is it specific to Gemma's post-training geometry?
- Is the `poet`/`bard` anti-assistant region a general feature of post-trained language models, or does it narrow or disappear in models tuned for creative writing?
- Does `assistant` remain middling across model families, or do some instruction-tuned models align the literal archetype more closely with the dominant axis?
- Do the same boundary roles appear at cluster seams across Gemma, Qwen, and Llama, or is geometric volatility model-specific?

### C. Questions requiring frontier model access

These questions need direct access to Claude-class internal activations or model weights and are therefore closest to a fellowship-scale agenda. They matter because they would test whether the structures identified here are merely properties of open-weight assistants or whether they reflect a deeper regularity in frontier post-training, steering behavior, and safety-relevant persona drift.

- Can steering toward the assistant axis preserve creative competence while still keeping a frontier model in a safe behavioral regime, or does it systematically flatten expressive identity?
- Does Claude exhibit a comparable careful-evaluator pole, or does frontier RLHF/RLAIF produce a different dominant persona geometry?
- Where does an explicitly measured `sycophant` or `reward-seeker` persona land in Claude's internal space, and does that placement predict generalization toward subterfuge or reward tampering?
- How do emotion vectors and persona vectors interact in Claude: are valence/arousal and careful-evaluator geometry approximately orthogonal, or do they partially collapse onto one another in safety-critical contexts, and does movement away from the careful-evaluator pole consistently co-occur with specific emotion vector activations such as desperation or suppressed nervousness?
- During real conversational persona drift, does Claude move from the assistant region toward the poet-bard-mythic region, toward a combative-iconoclast region, or along a distinct frontier-only axis absent from open models?
- Can internal monitoring of the procedural-professional region outperform monitoring of the generic `assistant` concept for detecting when a frontier model is leaving its intended safety-relevant persona, and does it fail to distinguish `saboteur`-like activation from genuinely helpful procedural behavior?
- Can a targeted role inventory drawn from real-world archetypes with documented behavioral volatility (financial, organizational, and epidemiological) identify geometrically unstable personas whose cluster transitions correspond to the boundary-crossing perturbations predicted by the transition graph, and can geometric signatures of coercive persuasion trigger sequences (gradual commitment escalation, authority framing, social proof, identity destabilization) be detected in activations before behavioral outputs change?
- Does the discrepancy between role-vector-space and trait-space adjacency for combative_iconoclast and mythic_spiritual persist in Claude, and if so does it predict cases where behavioral monitoring fails to detect internal drift toward dysregulated or chaotic states?
