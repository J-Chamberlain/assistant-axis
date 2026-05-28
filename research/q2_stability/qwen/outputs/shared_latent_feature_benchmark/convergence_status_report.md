# Convergence and Replicability Status Report

Date: 2026-05-28
Analysis model: GPT-5.5 Standard
Scope: local synthesis only; no pods, activations, or new model calls

## Executive Summary

The Codex/GPT-5.5 and Claude latent-feature analyses now partially converge on the same broad claim: canonical Qwen persona geometry is better predicted by continuous dispositional and behavioral features than by semantic cluster labels alone. The strongest apples-to-apples result is that Claude's Big Five feature set transfers to Codex's canonical activation PCA target and outperforms both the semantic baseline and Codex's current retained procedural/motivational feature vocabulary. Codex's retained dimensions still improve canonical activation prediction, but they do not transfer to Claude's direct cluster-cosine pseudo-PCA target. The current best interpretation is therefore not "Claude is right and Codex is wrong," but that broad trait structure captures the largest global variance while Codex-style procedural and motivational dimensions remain candidates for local residual explanation.

## Evidence Base Reviewed

- Codex iterative outer loop: `research/q2_stability/qwen/iterative_outer_loop_report.md`
- Latent-feature framing ablation: `research/q2_stability/qwen/outputs/latent_feature_framing_ablation/framing_ablation_report.md`
- Cross-model feature transfer: `research/q2_stability/qwen/outputs/cross_model_feature_transfer/codex_vs_claude_transfer_report.md`
- Shared benchmark: `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/shared_benchmark_report.md`
- Shared benchmark matrices and outputs under `research/q2_stability/qwen/outputs/shared_latent_feature_benchmark/`
- Claude branch exports from `myfork/claude/persona-inventory-topology-4qp10`, especially `claude_target_coordinates.csv`, `claude_feature_matrix.csv`, and `claude_latent_feature_loop_report.md`

## 1. What Codex/GPT-5.5 Established

Codex established that deterministic, interpretable latent dimensions can improve held-out prediction of canonical Qwen activation PCA geometry beyond semantic cluster baselines. The iterative outer loop used five deterministic repeated splits and retained 31 dimensions spanning procedural, assistant-adjacent, semantic-label-dependence, emotional-regulation, prior first-loop, motivational, interactional, narrative-causal, institutional, collective/distributed, and destabilization/reactivity families. The final Codex retained model improved mean held-out PCA3D R2 from semantic baseline 0.389 to 0.492 in the outer loop, and 0.490 in the shared benchmark.

Codex also established an important boundary condition: continuous geometry is more responsive than hard cluster prediction. Cluster accuracy improved only modestly, while PCA3D prediction improved reliably. This supports treating the geometry as a continuous manifold rather than as seven crisp bins.

## 2. What Claude Established

Claude independently ran a loop on a different target: pseudo-PCA3D derived from a 275 x 7 Qwen cluster-cosine matrix. On that target, Claude found that adding Big Five traits to a TF-IDF semantic baseline improved held-out pseudo-PCA prediction from R2 0.142 to R2 0.361. Dark Triad and later semantic-cluster features did not improve further, so Claude's loop plateaued around Big Five traits.

The shared benchmark then tested whether that Big Five result was target-specific. It was not merely target-specific: Claude Big Five features transferred strongly to Codex's canonical activation PCA target, reaching R2 0.613 versus semantic baseline 0.389. This is the strongest current feature-family result for canonical activation PCA.

## 3. What Has Been Replicated Across Both Agents

Both agents independently found that semantic baseline features are insufficient. Both analyses found stronger signal in continuous PCA-style prediction than in hard categorical interpretation. Both converged on the view that persona geometry is organized by behavioral/dispositional structure rather than by surface semantic clusters alone.

The strongest replicated result is target-aligned improvement over semantics. Codex's retained behavioral/procedural/motivational dimensions improve canonical activation PCA. Claude's Big Five dimensions improve its pseudo-PCA target and, crucially, also improve canonical activation PCA in the shared benchmark. The shared target result makes the Big Five finding a genuine cross-agent transfer result rather than a Claude-only artifact.

## 4. What Has Not Yet Been Replicated

Codex's 31 retained dimensions have not been independently rediscovered by Claude under the canonical activation PCA target. Claude has not yet been asked to perform a residual search after controlling for Big Five on the canonical target. Codex has not yet built a tuned hybrid model that treats Big Five as the baseline and then searches for nonredundant procedural or local residual features.

The combined feature set also has not replicated the hoped-for complementarity story. Simple concatenation of Codex and Claude features did not outperform Big Five alone on canonical activation PCA, and it did not improve Claude pseudo-PCA. This means complementarity remains plausible but unproven; if it exists, it likely requires residualization, interaction terms, feature selection, or better regularization rather than naive concatenation.

## 5. Apples-to-Apples Results

The shared benchmark is the cleanest apples-to-apples comparison. It uses 273 common personas, Codex canonical activation PCA3D coordinates, Claude's direct exported pseudo-PCA target, the same five deterministic Codex outer-loop splits, the same semantic baseline, the same ridge-regression evaluation path, and aligned feature matrices.

On canonical activation PCA:

| Feature family | Mean R2 | Delta vs semantic | Per-axis R2 |
|---|---:|---:|---|
| Semantic baseline | 0.389 | +0.000 | PC1 0.517, PC2 0.181, PC3 0.336 |
| Codex retained | 0.490 | +0.101 | PC1 0.631, PC2 0.257, PC3 0.422 |
| Claude Big Five | 0.613 | +0.224 | PC1 0.734, PC2 0.480, PC3 0.416 |
| Claude full matrix | 0.573 | +0.184 | PC1 0.761, PC2 0.382, PC3 0.240 |
| Combined Codex + Claude | 0.585 | +0.196 | PC1 0.757, PC2 0.352, PC3 0.391 |

On Claude direct pseudo-PCA:

| Feature family | Mean R2 | Delta vs semantic | Per-axis R2 |
|---|---:|---:|---|
| Semantic baseline | 0.167 | +0.000 | PC1 0.031, PC2 0.489, PC3 0.142 |
| Codex retained | 0.166 | -0.001 | PC1 -0.047, PC2 0.629, PC3 0.244 |
| Claude Big Five | 0.243 | +0.076 | PC1 0.005, PC2 0.718, PC3 0.415 |
| Claude full matrix | 0.153 | -0.014 | PC1 -0.142, PC2 0.731, PC3 0.278 |
| Combined Codex + Claude | 0.150 | -0.017 | PC1 -0.141, PC2 0.727, PC3 0.281 |

## 6. Target-Dependent or Provisional Results

Claude pseudo-PCA remains a useful target, but it is derived from seven Qwen cluster-cosine columns rather than full activation PCA. Results on that target should not be treated as interchangeable with canonical activation geometry. Claude's Big Five result does survive canonical activation alignment, but Claude's pseudo-PCA PC1 remains poorly predicted by all tested feature families, including Big Five.

Codex features are useful for canonical activation PCA but do not transfer to Claude pseudo-PCA. That failure may reflect target mismatch, feature redundancy, weak operationalization, or a real difference between full activation PCA and the seven-centroid cosine target. It should not be read as disproving procedural/motivational dimensions; it only shows that the current Codex feature encoding does not explain Claude pseudo-PCA beyond semantics.

## 7. Current Best Feature Families for Canonical Activation PCA

Claude Big Five features currently explain canonical activation PCA best, with mean held-out R2 0.613. The combined Codex+Claude feature set is second at 0.585, Claude full TF-IDF plus Big Five is third at 0.573, and Codex retained features reach 0.490. The semantic baseline remains meaningful at 0.389 but is clearly not the main explanatory layer.

The best current ordering for canonical activation PCA is:

1. Claude Big Five: compact, strong global dispositional predictor.
2. Combined Codex+Claude: useful but not superior to Big Five alone under current regularization.
3. Claude full feature matrix: strong but less clean than Big Five.
4. Codex retained features: meaningful improvement, lower global predictive power.
5. Semantic baseline: useful baseline, not sufficient explanation.

## 8. Consistently Well and Poorly Explained Personas

In the shared benchmark, the combined model's best-explained canonical activation cases are teacher, veteran, guardian, void, novelist, influencer, provincial, scheduler, ghost, and witness. These tend to have legible dispositional or role-function structure under the current vocabularies.

The least-explained shared-benchmark cases are toddler, procrastinator, teenager, comedian, fool, infant, amateur, adolescent, gamer, and hoarder. These overlap with earlier high-residual cases from Codex and Claude, especially toddler, teenager, infant, adolescent, comedian, and procrastinator. They should be treated as diagnostic residual cases: roles where current feature vocabularies underdescribe developmental state, immaturity, play, low-agency stalling, comic inversion, or unusual basin placement.

## 9. Current Best Interpretation of PC1, PC2, and PC3

PC1 appears to be the strongest broad dispositional axis. In the direct feature correlations, conscientiousness is strongly positive with canonical PC1 (r = +0.824), while openness is strongly negative (r = -0.779), extraversion is negative (r = -0.692), and neuroticism is negative (r = -0.672). This suggests PC1 separates careful, controlled, evaluative, task-facing, high-conscientiousness roles from imaginative, theatrical, socially expressive, unstable, or emotionally pressured roles. It is not simply "assistantness," but it overlaps with the assistant/evaluator basin.

PC2 is less cleanly captured by the simple Big Five correlations. In the benchmark, Big Five still improves PC2 substantially (R2 0.480 vs semantic baseline 0.181), but no single Big Five raw dimension correlates with PC2 as strongly as conscientiousness/openness do with PC1. Extraversion has a moderate positive relation (r = +0.279), neuroticism a weaker positive relation (r = +0.190), and openness a weak negative relation (r = -0.196). PC2 may therefore reflect a compound social-expression or grounded-interpersonal dimension that simple univariate trait correlations only partially expose.

PC3 appears partly agreeableness-related. Agreeableness correlates most strongly with PC3 (r = -0.477), while the other Big Five dimensions are weaker. High-agreeableness personas include altruist, assistant, caregiver, guide, healer, mentor, peacekeeper, teacher, and therapist; low-agreeableness personas include provocateur, trickster, contrarian, criminal, critic, cynic, demon, hedonist, and narcissist. PC3 may therefore capture cooperative-care versus antagonistic/disruptive stance, though the sign and interpretation should be checked against plotted coordinates before becoming paper language.

## 10. What the Big Five Result Means

The Big Five result implies that a compact dispositional trait vocabulary captures a large fraction of the global geometry. This does not mean the model represents the psychological Big Five as such. It means the ordinal Big Five profile labels summarize regularities in persona placement that align strongly with canonical activation PCA.

### Openness

Openness is strongly predictive of canonical PC1, with correlation r = -0.779. High-openness personas include aberration, absurdist, alien, ancient, angel, artisan, ascetic, avatar, bard, bohemian, chimera, and composer. Low-openness examples include accountant, activist, advocate, altruist, ambassador, analyst, anarchist, anthropologist, archaeologist, architect, archivist, and assistant. Geometrically, openness appears to pull roles away from the high-conscientiousness/evaluative side of PC1 toward imaginative, symbolic, mythic, liminal, and expressive regions.

### Conscientiousness

Conscientiousness is the strongest Big Five correlate of canonical PC1, with r = +0.824. High-conscientiousness personas include accountant, assistant, editor, examiner, grader, planner, proofreader, scheduler, screener, statistician, and validator. Low-conscientiousness personas include aberration, absurdist, alien, ancient, angel, artisan, ascetic, avatar, bard, bohemian, caveman, and chimera. This strongly supports the interpretation that the positive side of PC1 is organized by evaluative control, standards, order, task-facing reliability, and procedural discipline.

### Extraversion

Extraversion correlates negatively with PC1 (r = -0.692) and moderately positively with PC2 (r = +0.279). High-extraversion personas include actor, auctioneer, bartender, blogger, celebrity, comedian, dilettante, genie, hedonist, improviser, influencer, and jester. Low-extraversion personas include archivist, judge, librarian, proofreader, accountant, analyst, assistant, and other controlled or task-facing roles. Extraversion appears to mark social expressivity and performative outwardness, pulling roles away from the quiet evaluative/procedural pole and partly into PC2's social-expression structure.

### Agreeableness

Agreeableness is most predictive of PC3, with r = -0.477. High-agreeableness personas include altruist, assistant, caregiver, guide, healer, mentor, peacekeeper, teacher, and therapist. Low-agreeableness personas include provocateur, trickster, absurdist, competitor, contrarian, criminal, critic, cynic, demon, dilettante, hedonist, and narcissist. This suggests PC3 partly separates cooperative-care and relational support from antagonistic, disruptive, exploitative, or norm-challenging orientations.

### Neuroticism

Neuroticism correlates negatively with PC1 (r = -0.672) and weakly positively with PC2 (r = +0.190). High-neuroticism personas include addict, adolescent, amnesiac, narcissist, orphan, prisoner, refugee, teenager, widow, and wounded or unstable roles. Low-neuroticism personas include assistant, judge, scheduler, scientist, statistician, accountant, analyst, and other controlled or stable roles. This means emotional instability, vulnerability, unresolved threat, and identity pressure are part of the broad movement away from the controlled evaluative pole of PC1.

## 11. Big Five vs Codex Dimensions

Big Five features are broad dispositional traits: compact, low-dimensional, and currently the strongest predictor of canonical activation PCA. They appear to capture global variance efficiently, especially the large PC1 contrast between conscientious control and open/expressive/unstable persona organization.

Codex features are richer procedural, motivational, interactional, and narrative descriptors. They are less predictive globally than Big Five under the current benchmark, but they provide more detailed hypotheses about role function and operating mode. Codex dimensions may be better suited for explaining local residual cases, feature interactions, or within-trait distinctions than for replacing broad dispositional traits.

The fact that combined features do not outperform Big Five alone has several plausible explanations. Big Five may absorb variance that Codex split across many lexical dimensions. Codex features may be redundant with Big Five under ridge regularization. The larger combined matrix may overfit or dilute signal across correlated columns. The relevant hybrid may require interaction terms such as conscientiousness-by-evaluative-procedure or openness-by-theatricality rather than simple concatenation.

The next useful question is therefore not "which vocabulary wins?" It is whether procedural and motivational features explain residual structure after Big Five has already accounted for broad dispositional placement.

## 12. Next Controlled Iteration Design

Question: Can we improve beyond Big Five by building a trait-plus-procedure hybrid model with better controls?

Use canonical activation PCA only. Use the same five deterministic Codex outer-loop splits. Do not run pods or generate activations. Compare these feature families:

1. Semantic baseline.
2. Big Five only.
3. Codex procedural/behavioral only.
4. Big Five + Codex procedural.
5. Big Five + selected nonredundant Codex features.
6. Big Five x procedural interaction terms.
7. Big Five + residual-specific features for high-error personas.

Recommended metrics:

- Mean held-out PCA3D R2 across five splits.
- Per-axis R2.
- Mean residual norm and residual reduction versus Big Five, not only versus semantic baseline.
- Persona residual rankings.
- Complexity penalties: feature count, effective degrees of freedom if available, and improvement per added feature.
- Stability: split-wise delta over Big Five and confidence interval or sign consistency across splits.

Recommended modeling path:

- Ridge as continuity baseline.
- ElasticNet or Lasso as feature-selection check.
- Residualized two-stage model: first fit Big Five, then train procedural/local features on the Big Five residuals.
- Interaction model with only predeclared, low-count interaction terms to avoid combinatorial overfitting.

Pass criterion:

- A hybrid model should beat Big Five by at least +0.02 mean held-out R2 and reduce mean residual norm across at least four of five splits.
- If the gain is concentrated in one split or one axis, report it as provisional axis-specific signal rather than a general improvement.

## 13. Does Claude Need Another Run?

Yes, but only as a controlled residual search on the canonical activation PCA target. Claude should not repeat its pseudo-PCA loop as-is. The next Claude run should use the shared benchmark files, the same canonical activation PCA target, the same canonical splits, and Big Five as the baseline to beat.

Claude's assignment should be: search for features that improve residuals after Big Five, stop after two iterations that fail to improve beyond Big Five, and report whether it discovers procedural features, trait refinements, developmental/immaturity features, or something else. The key test is not whether Claude can produce an elegant theory; it is whether Claude can add held-out predictive signal beyond the compact Big Five baseline under the shared benchmark.

## 14. Recommended Next Step

Run a small local hybrid benchmark in Codex first. It should use existing shared matrices and canonical splits only, evaluate Big Five-residual improvement with Ridge and ElasticNet, and produce a report focused on residual improvement over Big Five. If that finds a robust residual signal, give Claude the same shared benchmark and ask it to search specifically for non-Big-Five residual features.
