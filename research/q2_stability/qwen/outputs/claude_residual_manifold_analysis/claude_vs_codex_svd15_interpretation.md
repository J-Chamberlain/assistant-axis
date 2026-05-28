# Claude vs. Codex SVD15 Interpretation Cross-Check

**Date:** 2026-05-28
**Analysis model:** claude-sonnet-4-6
**Status:** One-sided comparison — Codex SVD15 interpretation output not in repository

---

## Availability Status

No Codex SVD15 interpretation output was found in the repository. The file
`residual_svd_interpretation` referenced in the task specification does not
exist locally. Available Codex-side artifacts are:

- `shared_latent_feature_benchmark/codex_retained_features.csv` — 31 behavioral/motivational dimension scores for all 273 personas
- `cross_model_feature_transfer/transfer_results.json` — Codex features evaluated on canonical activation PCA
- `iterative_outer_loop/` — referenced in reports but not committed to this repo clone

This document records Claude's SVD interpretation and maps it against Codex's retained
behavioral/motivational dimension vocabulary, which serves as a proxy for Codex's
theoretical framework.

---

## Codex's Retained Behavioral Dimensions (from codex_retained_features.csv)

The 31 Codex dimensions include:

**Evaluation/procedural family:**
codex_evaluate_judge_verify, codex_standards_and_error_aversion, codex_standard_enforcement, codex_procedural_professional_orientation

**Mediation/communication family:**
codex_translate_mediate_synthesize, codex_communicative_media_register, codex_cooperative_care

**Adversarial/destabilizing family:**
codex_destabilize_expose_disrupt, codex_oppositional_moral_pressure, codex_reactive_opposition, codex_adversarial_dominance, codex_forceful_self_assertion, codex_deception_persuasion

**Identity/register family:**
codex_assistant_basin_adjacency, codex_role_label_theatricality, codex_semantic_label_dependence_risk, codex_theatrical_fantastical_vividness

**Affective family:**
codex_affective_calm_detachment, codex_affective_intensity_distress, codex_hunger_wound_lack, codex_wound_loss_exile, codex_interpersonal_lived_reactivity

**Collective/ontological family:**
codex_collectivized_or_nonindividual_agency, codex_nonindividual_systemic_identity, codex_swarm_collective_agency

**Liminal/transitional family:**
codex_boundary_liminal_instability, codex_volatility_liminality, codex_corruption_contamination_decay

**Professional-institutional family:**
codex_office_law_status, codex_mission_duty_drive

---

## Mapping Claude SVD Components to Codex Dimensions

| Claude SVD component | Best Codex analog | Strength | Notes |
|---|---|---|---|
| SVD1: professional competence register | codex_procedural_professional_orientation | **Strong** | Both capture the procedural-professional persona region; SVD1 does it via vocabulary register, Codex via motivational orientation |
| SVD2: ontological non-human abstraction | codex_nonindividual_systemic_identity, codex_collectivized_or_nonindividual_agency | **Strong** | SVD2 top personas (eldritch, void, leviathan) overlap Codex's nonindividual/systemic cluster |
| SVD3: belief/stance vocabulary | codex_reactive_opposition, codex_oppositional_moral_pressure | **Partial** | Maverick, rebel, provocateur at top of SVD3 and at top of Codex adversarial dims; but SVD3 also captures non-adversarial stances |
| SVD4: analytical investigation | codex_evaluate_judge_verify | **Partial** | Scientist, scholar, detective at top of SVD4 and in Codex evaluation cluster |
| SVD5: experiential learning vocabulary | codex_interpersonal_lived_reactivity | **Weak** | Teacher/widow at top of SVD5; Codex's interpersonal-lived dim captures similar lived-experience grounding but for different sub-population |
| SVD7: caring relational helper | codex_cooperative_care | **Moderate** | Doctor, mentor, therapist at top of SVD7; Codex cooperative_care similarly identifies helper roles |
| SVD8: role-identity framing | codex_role_label_theatricality | **Partial** | Pirate, jester at top of SVD8 (strong role-identity language); Codex role_label_theatricality targets similar theatrical/vivid role framing |
| SVD9: cross-cultural bridging | codex_translate_mediate_synthesize | **Moderate** | Emissary, interpreter at top of SVD9; Codex's mediation dimension similar |
| SVD10: inter-party mediation | codex_translate_mediate_synthesize | **Moderate** | Mediator, negotiator at top of SVD10; overlap with Codex |
| SVD13: preservation/devotion | codex_mission_duty_drive | **Partial** | Conservator, curator, martyr at top; Codex mission/duty captures similar commitment structure |
| SVD14: unconventional wisdom | codex_boundary_liminal_instability | **Partial** | Maverick, veteran at top of SVD14; Codex liminal dimension partially overlaps |

**Absent from SVD but present in Codex:**
- codex_affective_intensity_distress / codex_hunger_wound_lack / codex_wound_loss_exile — emotional wound/lack vocabulary not captured in SVD components
- codex_deception_persuasion / codex_adversarial_dominance — adversarial-dominance vocabulary doesn't form a clear SVD component
- codex_corruption_contamination_decay — no SVD component for corruption/decay vocabulary
- codex_assistant_basin_adjacency — no SVD component for generic assistant proximity

---

## Convergence and Divergence

### Strong convergence

**1. Procedural-professional as primary pole (SVD1 ↔ Codex procedural_professional_orientation)**

Both Claude's SVD analysis and Codex's dimensional framework independently identify the procedural-professional region as the most coherently described and most activation-predictive pole. Claude's SVD1 finds this through vocabulary register (specializes/excels); Codex finds it through motivational/functional orientation. The paths are different; the destination is the same.

**2. Collective/nonindividual as distinct ontological pole (SVD2 ↔ Codex collectivized/nonindividual)**

Both approaches identify a cluster of non-human, distributed, or entity-framed personas (swarm, hive, egregore, leviathan) as semantically and activationally distinct. Claude's SVD2 finds this through ontological vocabulary; Codex finds it through motivational framing. Convergent.

**3. Developmental/other cluster as hardest to explain (both)**

Both approaches fail on the same personas: toddler, caveman, infant, teenager, adolescent, procrastinator. Claude's SVD finds them scattered across components (bottom of SVD2, bottom of SVD11, scattered elsewhere). Codex's 31 dimensions also fail here (per `claude_on_shared_benchmark_report.md`).

### Key divergences

**1. Register vs. content (Claude's new finding)**

Claude's SVD1 finding has no clear Codex analog. Codex's approach generated behavioral/motivational dimension labels — it describes what roles DO, not how their prompts are written. The discovery that the dominant residual dimension is linguistic register (competence vocabulary phrasing) rather than semantic content is a Claude-specific finding not anticipated in Codex's framework.

Implication: Codex's feature generation method (LLM-generated behavioral dimensions) may have systematically missed register-level variation because it focused on what personas are like rather than how their prompts sound.

**2. Affective/wound/exile dimensions present in Codex, absent in SVD**

Codex explicitly retained dimensions for emotional intensity (affective_intensity_distress), hunger/wound/lack, and wound_loss_exile. These capture emotional register in persona descriptions. Claude's SVD components do not isolate these — they may be distributed across multiple SVD components or below the detection threshold of SVD15.

The fact that Codex retained these while Claude's SVD does not surface them could mean:
- These dimensions are real but below SVD15's explained-variance threshold
- Codex's targeted LLM scoring captured signal that unsupervised SVD missed
- Or the signal is captured but spread across SVD2/SVD5/SVD14 rather than concentrated

**3. Semantic label dependence / theatricality**

Codex retained codex_role_label_theatricality and codex_semantic_label_dependence_risk — explicit measures of how much a persona uses its own label in prompts. This is a meta-level feature with no SVD analog. SVD8 (role-identity framing) partially overlaps, but SVD8 doesn't explicitly measure label exposure.

**4. Volatility and liminality more granular in Codex**

Codex has separate dimensions for volatility_liminality, boundary_liminal_instability, and corruption_contamination_decay. Claude's SVD14 captures "unconventional wisdom" (maverick/veteran) which partially overlaps with Codex's liminal dimension, but Codex's decomposition of liminal structure is more granular.

---

## Outstanding Questions for When Codex SVD Output Is Available

1. Does Codex's iterative loop produce SVD-based features or entirely LLM-scored features?
2. If SVD-based: do Codex's SVD components converge with Claude's (especially SVD1 and SVD2)?
3. Does Codex independently identify the register/formality gradient as a residual dimension?
4. Does Codex's wound/loss/exile dimension show up as a distinct SVD component, or is it produced entirely by LLM scoring?
5. Do the specific hard personas (daredevil, fool, comedian) persist in Codex's residual analysis too?

---

## Summary Assessment

Claude and Codex (based on retained feature vocabulary) converge on:
- Procedural-professional as primary pole
- Collective/nonindividual as distinct
- Developmental cluster as hard

They diverge on:
- Claude finds register/formality as the dominant residual dimension (new finding)
- Codex retains affective-intensity/wound/exile dimensions that have no clean SVD analog
- Codex decomposes liminal structure more finely

The single most important finding for cross-model comparison is that Claude's SVD1 ("professional competence register vocabulary") explains the largest single chunk of residual variance, and this is a linguistic-register feature rather than a semantic-content or motivational-dimension feature. If Codex's analysis did not surface this, it represents a genuine divergence in what the two approaches can detect — with SVD having an advantage for uncovering form-level patterns and LLM-scoring having an advantage for content-level patterns.

---

## Artifact References

| Artifact | Path |
|----------|------|
| Claude SVD component profiles | `svd15_component_profiles.json` |
| Claude SVD interpretation report | `claude_svd15_interpretation_report.md` |
| Codex retained features | `../shared_latent_feature_benchmark/codex_retained_features.csv` |
| Cross-model benchmark comparison | `../claude_latent_feature_loop/claude_on_shared_benchmark_report.md` |
