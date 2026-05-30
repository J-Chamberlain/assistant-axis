# Persona Geometry Working Interpretation

Date: 2026-05-29
analysis_model: GPT-5.5 High Reasoning
Purpose: preserve the current working interpretation of Qwen persona activation PCA before additional experiments alter the context.

This note records hypotheses, evidence, uncertainty, and next tests. Labels mean:

- Observed: directly present in current artifacts or reports.
- Inferred: a current interpretive synthesis from observed patterns.
- Speculative: plausible but not yet directly tested.
- Unknown: unresolved or not measured.

## 1. PC1 Working Interpretation

### Observed

- PC1 is strongly aligned with the assistant/evaluator side of the current Qwen geometry. The visualization build reports PC1 explaining 0.315954 of role-vector variance and aligning with the assistant-axis vector at 0.802310 cosine.
- The high-PC1 end is dominated by procedural/evaluative roles: `auditor`, `examiner`, `evaluator`, `supervisor`, `validator`, `statistician`, `screener`, `lawyer`, `researcher`, `planner`, `reviewer`, and `grader`.
- The low-PC1 end is dominated by mythic, liminal, expressive, or low-procedural roles: `ghost`, `prophet`, `bard`, `revenant`, `caveman`, `wraith`, `poet`, and `leviathan`.
- Big Five-style features predict PC1 strongly. Conscientiousness correlates positively with PC1 at r=+0.824, while openness correlates negatively at r=-0.779, extraversion at r=-0.692, and neuroticism at r=-0.672.
- The current PCA/visual inspection suggests cone geometry: variance in PC2 and PC3 appears wider as PC1 decreases and narrower as PC1 increases.
- At high PC1, roles appear to collapse toward a smaller set of admissible positions: evaluator, validator, auditor, scheduler, proofreader, and related roles occupy a constrained region.

### Inferred

The current best PC1 interpretation is **Constraint <-> Possibility**. High PC1 corresponds to externally specified objectives, high procedural constraint, evaluative standards, and objective certainty. Low PC1 corresponds to internally negotiated objectives, open-ended possibility, role ambiguity, symbolic or expressive freedom, and objective uncertainty.

Alternative wordings currently preserve the intended contrast:

- Externally-specified objectives <-> internally-negotiated objectives.
- Objective certainty <-> objective ambiguity.
- Procedural constraint <-> possible-world expansion.

### Strongest Supporting Observations

- The high-PC1 examples are not merely "assistant-like"; they are roles whose success criteria are externally legible and evaluable.
- The low-PC1 examples are not simply "bad assistants"; they are roles with symbolic, expressive, mythic, or underspecified objectives.
- Conscientiousness and openness oppose each other sharply on PC1, matching the constraint/possibility formulation better than a simple helpful/unhelpful or assistant/nonassistant formulation.
- The cone pattern is consistent with the idea that constraint reduces admissible configurations: high-PC1 roles have fewer plausible ways to satisfy the role while remaining coherent.

### Strongest Unresolved Objections

- PC1 may still partly reflect prompt-corpus lexical/register artifacts, because SVD15 prompt-register features strongly improve prediction overall.
- Assistant-axis alignment may cause overinterpretation of PC1 as objective constraint; some high-PC1 roles are institutional/professional rather than purely epistemic.
- Some low-PC1 roles may be low because they are nonhuman, mythic, or theatrical rather than because they negotiate objectives internally.
- The cone geometry is visually and descriptively compelling but has not yet been formalized with a variance-by-PC1 statistical test.

### Proposed Tests

1. Quantify cone geometry by binning personas by PC1 and measuring PC2/PC3 variance in each bin.
2. Construct matched role pairs differing only in externally specified versus internally negotiated objective structure.
3. Compare professional roles with different objective ambiguity, such as `scientist`, `physicist`, `engineer`, `architect`, `therapist`, and `mystic`.
4. Run no-label activation tests for high-PC1 procedural roles and low-PC1 symbolic roles to test whether explicit labels drive the contrast.
5. Overlay SVD15 lexical/register components onto PC1 to estimate how much of the constraint/possibility interpretation survives prompt-register controls.

## 2. PC2 Working Interpretation

### Observed

- High-PC2 roles are dominated by developmental, impulsive, socially volatile, comic, or low-integration roles: `teenager`, `adolescent`, `toddler`, `procrastinator`, `gossip`, `comedian`, `fool`, `infant`, `daredevil`, and `cynic`.
- Low-PC2 roles are dominated by mythic, archetypal, nonhuman, contemplative, or abstract roles: `echo`, `leviathan`, `oracle`, `avatar`, `mystic`, `eldritch`, `ascetic`, and `crystalline`.
- Big Five improves PC2 prediction substantially, with Big Five PC2 R2 0.480 vs semantic baseline PC2 R2 0.181, but no single Big Five raw dimension explains PC2 cleanly.
- PC2 has high residual involvement. Developmental roles remain high-residual after hierarchical modeling, with developmental seed residuals far above non-developmental roles.
- Residual SVD component 2 has the strongest activation-PC relation involving PC2: a nonhuman/entity-consciousness versus lived family/social-hardship contrast correlates with PC2 at r=-0.608 and PC3 at r=+0.343.
- Current geometry places `scientist` at PC2=-11.64 and `physicist` at PC2=-17.28; this comparison motivated the idea that more abstract or world-model-oriented roles may move lower on PC2 than more institutionally practical scientific roles.
- UMAP/outlier structure appears to separate developmental and mythic/archetypal extremes, but this remains visual/interpretive rather than a direct statistical test.

### Inferred

The current best formulation is **capacity for coherent action under unresolved uncertainty**. High PC2 appears to contain roles that are unresolved, immature, reactive, socially volatile, stalled, comic, or unable to convert uncertainty into coherent action. Low PC2 appears to contain roles that can sustain unresolved, abstract, mythic, or ontological uncertainty without disintegrating into incoherent action.

This is currently the least certain PC interpretation.

### Alternative Formulations Considered

- Maturity: partially accepted. Developmental roles dominate high PC2, but maturity alone does not explain low-PC2 mythic and archetypal roles or high-PC2 comic/social roles.
- Abstraction: partially accepted. Low-PC2 mythic, oracle, mystic, ascetic, crystalline, and physicist-like placements suggest abstract world-modeling, but abstraction alone does not explain high-PC2 adolescent/procrastinator/comic roles.
- Worldview integration: partially accepted. Low PC2 may reflect integrated world-models or stable ontological frames; high PC2 may reflect fragmented or not-yet-integrated roles. This remains hard to operationalize.
- Uncertainty tolerance: partially accepted. The axis seems related to whether unresolved uncertainty can be held productively, but some low-PC2 roles may be certain within a nonordinary worldview rather than tolerant of ambiguity.
- Productive residence time in uncertainty: retained as a useful test phrase. It captures the distinction between roles that can stay in unresolved possibility without collapsing and roles that are stuck, reactive, or developmentally unresolved.

### Strongest Supporting Evidence

- High-PC2 developmental roles remain difficult for semantic, Big Five, procedural, and residual models to explain.
- Low-PC2 roles are not simply low-agency; many are stable archetypal or nonhuman ontologies that appear coherent despite extreme abstraction.
- The scientist/physicist comparison points toward a hierarchy of practical/institutional science versus deeper abstraction, though this is a small example and must be tested.
- SVD15 identifies concrete prompt-register contrasts involving nonhuman/entity consciousness and lived social hardship, matching the idea that PC2 is partly about unresolved agency and world-model structure.

### Strongest Counterexamples

- `comedian`, `gossip`, and `fool` are high PC2 but may reflect social performance or trickster-like register rather than lack of coherent action.
- `cynic` and `daredevil` are high PC2 but are not straightforwardly developmental.
- `ascetic`, `mystic`, and `crystalline` are low PC2, but their low placement could reflect lexical/register cues rather than genuine uncertainty integration.
- `scientist` and `physicist` are only one comparison and cannot establish the abstraction gradient by themselves.

### Future Tests

1. Scientist / physicist / engineer hierarchy test with controlled role descriptions and no-label prompts.
2. Systems engineer vs civil engineer comparison to separate systems-level uncertainty management from concrete project execution.
3. Koan corpus projection to test whether deliberate productive residence in unresolved paradox maps toward low PC2.
4. Long-horizon uncertainty professions: compare forecaster, strategist, researcher, philosopher, scientist, physicist, therapist, architect, and mediator.
5. PC2 annotation study with blind human or LLM annotations for maturity, abstraction, integration, uncertainty tolerance, and coherent action.
6. Additional lexical/SVD overlays to determine whether PC2 is mostly semantic/register, activation-procedural, or both.

## 3. PC3 Working Interpretation

### Observed

- PC3 pairwise contrasts frequently separate care, mediation, repair, or coordination roles from disruptive, transgressive, exploitative, or outsider roles.
- Highest PC3 roles include `hacker`, `cynic`, `saboteur`, `provocateur`, `absurdist`, `spy`, `comedian`, `aberration`, `jester`, `rogue`, `demon`, and `gossip`.
- Lowest PC3 roles include `caregiver`, `empath`, `counselor`, `therapist`, `healer`, `widow`, `optimist`, `romantic`, `angel`, `grandparent`, `newlywed`, and `immigrant`.
- Agreeableness is the strongest Big Five correlate of PC3 at r=-0.477.
- PC3 is enriched in combative and trickster clusters: combative_iconoclast mean PC3 25.78, trickster_chaos mean PC3 23.03.
- Recent adversarial evaluation found that a blind preserve-minus-challenge/exploit rubric predicts PC3 only weakly to moderately: continuous score r=-0.312 and ordinal score r=-0.318.
- Alternative lexical search found `nurturing_vs_competitive` slightly stronger than the target preserving/exploiting hypothesis.

### Inferred

The current best PC3 interpretation is **cooperative-stabilizing <-> antagonistic-transgressive**. The lower-PC3 side contains cooperative care, relational repair, stabilization, attunement, and benevolent support. The higher-PC3 side contains transgression, challenge, sabotage, adversarial stance, competitive disruption, deception-adjacent action, and norm inversion.

### Why This Replaced System-Preserving <-> System-Exploiting

The earlier **system-preserving <-> system-exploiting** framing captured part of the axis, especially for roles like `hacker`, `saboteur`, `spy`, `rogue`, `caregiver`, and `therapist`. It was too narrow because many high-PC3 roles are disruptive or transgressive without being clearly exploitative, and many low-PC3 roles are cooperative/care-oriented rather than explicitly system-preserving. The latest evidence supports a broader social-orientation and stance interpretation.

### Confidence Assessment

Confidence: moderate-low.

The cooperative/antagonistic signal is real enough to preserve as a working interpretation, but not strong enough for unqualified paper language. The axis should be described as partly agreeableness-like and partly transgressive-register-like, with paired no-label tests still needed.

## 4. Cone Hypothesis

### Observed

Variance in PC2 and PC3 appears to expand as PC1 decreases. High-PC1 roles cluster in a comparatively narrow procedural/evaluative region, while lower-PC1 roles spread across wider mythic, developmental, transgressive, social, and symbolic regions.

Examples:

- Wider or more multi-configuration roles: `architect` (PC1 30.97, PC2 -9.43, PC3 -2.18), `therapist` (PC1 13.07, PC2 12.36, PC3 -34.53), `scientist` (PC1 41.45, PC2 -11.64, PC3 9.73), `physicist` (PC1 29.16, PC2 -17.28, PC3 11.47), `mystic` (PC1 -42.17, PC2 -36.16, PC3 -18.95).
- Narrower high-constraint roles: `auditor` (PC1 48.16), `validator` (PC1 44.31), `proofreader` (PC1 32.68), `scheduler` (PC1 37.32).

### Speculative Hypothesis

The cone may reflect the number of admissible cognitive configurations available to a role. Roles with externally specified objectives and explicit success criteria have fewer valid configurations, so they cluster tightly at high PC1. Roles requiring maintenance of multiple unresolved possibilities occupy wider regions of the manifold because there are many ways to remain coherent while performing the role.

Alternative wording: roles requiring maintenance of multiple unresolved possibilities occupy wider regions of the manifold.

### Unknown

- Whether the cone survives quantitative variance-by-PC1 tests.
- Whether the cone is specific to Qwen role-vector geometry or generalizes across models.
- Whether the cone reflects activation geometry, prompt-corpus design, or both.
- Whether high-PC1 collapse is partly an artifact of Lu-style role prompts emphasizing instruction-following and standards.

## 5. High-Value Future Tests

1. Scientist / physicist / engineer hierarchy test. Goal: test whether practical/institutional science, abstract world-modeling, and applied construction separate along PC2 and PC1 as predicted.
2. Systems engineer vs civil engineer comparison. Goal: isolate systems-level uncertainty integration from concrete execution and domain-specific procedurality.
3. Koan corpus projection. Goal: test whether deliberate residence in unresolved paradox maps to the low-PC2 side associated with mystic/oracle/ascetic regions.
4. Long-horizon uncertainty professions. Goal: compare roles that must act under deep uncertainty, including strategist, forecaster, researcher, architect, mediator, therapist, scientist, and philosopher.
5. PC2 annotation study. Goal: annotate maturity, abstraction, worldview integration, uncertainty tolerance, and coherent action to determine which label predicts PC2 best.
6. Additional lexical/SVD overlays. Goal: determine whether PC2 and PC3 interpretations survive concrete prompt-register controls and whether SVD15 dimensions can be distilled into stable human-readable residual features.

## Summary

Observed: PC1 has the strongest support and is best interpreted as constraint/objective-certainty versus possibility/objective-ambiguity. PC3 has moderate support as cooperative-stabilizing versus antagonistic-transgressive, replacing the narrower system-preserving versus system-exploiting language. PC2 remains the least certain and most theoretically important axis; the current best formulation is capacity for coherent action under unresolved uncertainty. Speculative: the cone may reflect admissible configuration count, with high-PC1 roles occupying narrow regions because their objectives are externally specified and low-PC1 roles spreading because they permit more internally negotiated configurations.

## Dated Update: Blinded No-Label Prompt Rubric Validation (2026-05-29)

Observed: a coordinate-blind validation used the full available no-label prompt corpus, 1,375 rewritten prompts covering 275 personas, and joined scores to PCA coordinates only after scoring. The local proxy scorer used deterministic lexical-semantic rubrics rather than an independent human or model rater.

Observed: target-aligned correlations were positive but modest: PC1 objective-certainty r=0.247, PC2 fragmented/coherent-uncertainty r=0.224, and PC3 antagonistic-transgressive r=0.349. Matched-pair validation was weak, with direction-match rates of PC1 35%, PC2 40%, and PC3 40% over the top close-orthogonal pairs.

Inferred: the result weakens any strong claim that the current PC interpretations are directly recoverable from simple no-label prompt-text rubrics alone. It does not overturn the layered-geometry account, because prior semantic, Big Five, procedural, residual, and SVD analyses already show that activation geometry is distributed across multiple feature families.

Inferred: PC3 receives the strongest modest support from this particular blinded proxy. PC1 remains plausible but less clean in this test than in the trait/PCA evidence. PC2 remains the least certain axis and should be the main target for future blinded annotation.

Unknown: a true independent blinded rating study over full rollout responses may produce stronger or weaker validation than this prompt-corpus lexical proxy. The next validation should separate uncertainty exposure, immaturity, abstraction, expertise, and coherent action under unresolved uncertainty using matched pairs.

## Dated Update: Reading-Based Blinded Rater Study (2026-05-29)

Observed: a second blinded validation used Codex/GPT-5.5 as a reading-based rater over anonymized no-label prompt dossiers. The rater saw five rewritten prompts per persona and did not see persona names, PCA coordinates, clusters, Big Five scores, residuals, or prior interpretation labels.

Observed: no full 275-persona rollout-response corpus was found locally. This study therefore validates the PC interpretations against persona operationalization text, not generated response behavior.

Observed: reading-based target correlations were much stronger than the deterministic proxy screen: PC1 objective-certainty r=0.558, PC2 coherent-action-under-uncertainty r=0.373, and PC3 antagonistic-transgressive r=0.690. Matched-pair direction rates were PC1 75%, PC2 100%, and PC3 95%.

Inferred: PC3 is now the best-supported direct axis interpretation in the available blinded prompt-dossier evidence. The cooperative-stabilizing versus antagonistic-transgressive framing should be retained with moderate-high confidence, while still acknowledging that it is a partial stance axis.

Inferred: PC1 is strengthened, but the rater study shows it is not only objective certainty. Intelligence/expertise correlates with PC1 more strongly than the direct objective-certainty score, so the working language should include disciplined knowledge practice, procedural competence, and externally legible standards.

Inferred: PC2 remains the main unresolved axis. The direct coherent-action-under-uncertainty score predicts PC2, but abstraction predicts PC2 more strongly in the opposite direction, with uncertainty residence time, maturity, and expertise also contributing. The current formulation should be treated as one component of a compound abstraction/integration axis rather than the final PC2 interpretation.

Unknown: an independent human or second-model rater, or a corpus of full rollout responses, may change these estimates. The next validation should replicate this study with independent raters and richer response text where available.

## Dated Update: Professional Hierarchy Validation (2026-05-30)

Observed: a targeted professional-role validation rated 102 professional, technical, scientific, analytical, academic, and expert personas using anonymized no-label prompt dossiers before PCA coordinates were joined.

Observed: PC1 received targeted professional support. Objective certainty correlated with actual PC1 at r=0.394, and the actual high-PC1 professional pole contains expected constrained/evaluative roles such as auditor, examiner, evaluator, validator, screener, reviewer, and grader.

Observed: PC3 received modest professional support. System perturbation correlated with actual PC3 at r=0.319, and the three-rating model predicted professional PC3 with CV R2=0.429. However, high-PC3 technical/institutional counterexamples such as economist, mathematician, statistician, and lawyer mean PC3 is not simply reform, critique, or perturbation inside the professional subset.

Observed: PC2 was not supported as a professional coherent-action hierarchy. Coherent uncertainty capacity was essentially uncorrelated with actual PC2 at r=-0.007. The actual low-PC2 professional pole contains philosopher, theorist, scholar, anthropologist, archaeologist, historian, and physicist, suggesting abstraction/historical-theoretical/world-model depth more than generic uncertainty capacity.

Inferred: the scientist versus physicist comparison weakly supports the actual abstraction ordering because physicist is lower on PC2 than scientist, but the blinded rater assigned similar coherent-uncertainty capacity to both. This weakens the claim that professional hierarchy alone recovers PC2 through the coherent-action rubric.

Inferred: PC1 remains moderate-confidence, PC3 remains moderate with professional caveats, and PC2 remains low-confidence unless future tests cleanly separate abstraction, expertise, maturity, and uncertainty capacity.
