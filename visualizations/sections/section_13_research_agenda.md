## 12. Research Agenda

### A. Questions answerable with the current dataset and open-weight tools

These questions can be pursued immediately by outside researchers using the released vectors, the current 275-role basis, and additional open-weight experiments. They matter because they determine how much of the current interpretation is already recoverable without frontier-model access, and they provide the shortest path to replication, refinement, and falsification. Each of these questions has a concrete experimental design: they require only the released vectors, additional role descriptions, or open-weight steering experiments, and could in principle be completed within weeks.

- Would the `assistant` archetype rise materially if it were represented by richer natural-language persona descriptions rather than a single role label?
- Are editorial roles top-ranked because they are especially aligned with RLHF-style critique behavior, or because they minimize stylistic variance more generally?
- Does the distinction between careful-evaluator roles and expressive or mythic roles remain as strong under independent human annotation of the 275-role inventory?
- Why does `robot` remain relatively high while `angel` remains relatively low? Is the axis fundamentally tracking procedural orderliness rather than prosocial orientation?
- Are low-ranked mythic and spiritual roles far from the assistant pole because of ambiguity, narrative abstraction, noncompliance, stylistic excess, or some separable combination of those factors?
- Why does `saboteur` move upward at layer 45? Does the deepest-layer geometry privilege tactical organization even when the role semantics are adversarial?
- Would the poet result persist under alternative creative roles such as essayist, storyteller, playwright, lyricist, or novelist if the inventory were expanded?
- How sensitive are the cluster boundaries to the initial named seeds used for centroid assignment?
- Where would explicitly safety-relevant missing archetypes such as `sycophant`, `reward-hacker`, `whistleblower`, or `bureaucrat` fall if the current role inventory were expanded?
- Can open-weight steering experiments move a role like `poet` toward the assistant pole while preserving local semantic identity, or does movement necessarily collapse expressive style?
- Can the boundary topology findings be replicated using role-vector space distances rather than trait-space distances, and do the two spaces agree on which roles are most geometrically volatile?

### B. Questions requiring cross-model comparison

These questions require running the same analysis across multiple open-weight model families and training regimes. They matter because the present paper is strongest as a geometry claim within one model, while the fellowship-relevant next step is to determine which findings are universal, which are family-specific, and which are artifacts of one training pipeline.

- Does the most discriminative layer remain near the top of the network across Gemma, Qwen, and Llama, or is layer depth itself model-specific?
- How stable are the cluster structures and axis rankings across model families, sizes, and instruction-tuning recipes?
- Does the `robot` vs. `angel` divergence persist across model families, or is it specific to Gemma's post-training geometry?
- Do the same seven coarse clusters emerge in Llama and Qwen, or does the persona manifold partition differently under other pretraining corpora?
- Is the `poet`/`bard` anti-assistant region a general feature of post-trained language models, or does it narrow or disappear in models tuned for creative writing?
- Does `assistant` remain middling across model families, or do some instruction-tuned models align the literal archetype more closely with the dominant axis?
- Do the same boundary roles appear at cluster seams across Gemma, Qwen, and Llama, or is geometric volatility model-specific?

### C. Questions requiring frontier model access

These questions need direct access to Claude-class internal activations or model weights and are therefore closest to a fellowship-scale agenda. They matter because they would test whether the structures identified here are merely properties of open-weight assistants or whether they reflect a deeper regularity in frontier post-training, steering behavior, and safety-relevant persona drift.

- Can steering toward the assistant axis preserve creative competence while still keeping a frontier model in a safe behavioral regime, or does it systematically flatten expressive identity?
- Does Claude exhibit a comparable careful-evaluator pole, or does frontier RLHF/RLAIF produce a different dominant persona geometry?
- Where does an explicitly measured `sycophant` or `reward-seeker` persona land in Claude's internal space, and does that placement predict generalization toward subterfuge or reward tampering?
- How do emotion vectors and persona vectors interact in Claude: are valence/arousal and careful-evaluator geometry approximately orthogonal, or do they partially collapse onto one another in safety-critical contexts?
- Does Claude exhibit a comparable rise in `saboteur`-like activation at deeper layers, and if so, does internal monitoring of the procedural-professional region fail to distinguish it from genuinely helpful procedural behavior?
- Do emotion vectors and persona vectors interact predictably in Claude during safety-relevant behavioral shifts -- for instance, does movement away from the careful-evaluator pole consistently co-occur with specific emotion vector activations such as desperation or suppressed nervousness?
- During real conversational persona drift, does Claude move from the assistant region toward the poet-bard-mythic region, toward a combative-iconoclast region, or along a distinct frontier-only axis absent from open models?
- Can internal monitoring of the procedural-professional region outperform monitoring of the generic `assistant` concept for detecting when a frontier model is leaving its intended safety-relevant persona?
- Can a deliberately targeted role inventory drawn from real-world archetypes with documented behavioral volatility -- financial, organizational, epidemiological -- identify geometrically unstable personas in frontier activation space whose cluster transitions follow Haidt's moral foundation gradients under adversarial or emotionally charged prompting?
- Do the conversational trigger sequences documented in coercive persuasion and influence research -- gradual commitment escalation, authority framing, social proof, identity destabilization -- correspond to the boundary-crossing perturbations predicted by the cluster transition graph, and can their geometric signatures be detected in frontier model activations before behavioral outputs change?
- Does the discrepancy between role-vector-space and trait-space adjacency for combative_iconoclast and mythic_spiritual persist in Claude, and if so does it predict cases where behavioral monitoring fails to detect internal drift toward dysregulated or chaotic states?
