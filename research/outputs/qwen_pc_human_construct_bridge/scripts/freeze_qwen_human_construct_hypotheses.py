#!/usr/bin/env python3
"""Freeze Qwen-derived human-construct candidates and measurement feasibility.

This script consumes only the already frozen Qwen-only signature and the
human-only construct library. Candidate judgments are explicit constants; no
model performance optimization or respondent-to-model projection occurs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


GENERATED_AT = "2026-09-12T09:40:00Z"
VALIDATION_STATUS = "DISCOVERY_ONLY / NOT YET CROSS-MODEL VALIDATED"
ALLOWED_STATUSES = {
    "STRONG CANDIDATE",
    "PLAUSIBLE PARTIAL CANDIDATE",
    "FACET / SUBCOMPONENT",
    "BROAD BUT NONSPECIFIC",
    "POOR MATCH",
    "INSUFFICIENT EVIDENCE",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def c(
    pc: int,
    construct_id: str,
    construct: str,
    framework: str,
    level: str,
    polarity: str,
    status: str,
    trait: str,
    roles: str,
    blind: str,
    definition: str,
    measurement: str,
    activation: str,
    judgment: str,
    mismatches: str,
    freeze: bool,
    sapa_available: bool = True,
    external_source: str = "",
) -> dict[str, object]:
    return {
        "pc": f"PC{pc}",
        "axis_status_core_or_secondary": "CORE" if pc <= 3 else "SUPPORTED_SECONDARY",
        "construct_id": construct_id,
        "human_construct": construct,
        "framework": framework,
        "level_domain_aspect_facet": level,
        "polarity": polarity,
        "model_trait_profile_coverage": trait,
        "role_profile_coverage": roles,
        "blinded_interpretation_alignment": blind,
        "human_definition_item_fit": definition,
        "human_measurement_quality": measurement,
        "focused_activation_evidence": activation,
        "match_status": status,
        "overall_judgment": judgment,
        "sapa_available": sapa_available,
        "human_measurement_source": construct_id if sapa_available else external_source,
        "known_mismatches": mismatches,
        "freeze_in_hypothesis_set": freeze,
        "validation_status": VALIDATION_STATUS,
    }


CANDIDATES = [
    # PC1 deep worked-example candidates.
    c(1, "IPIP100:B5:C", "Conscientiousness", "Big Five", "domain", "positive", "STRONG CANDIDATE",
      "SUPPORTS — methodical, cautious, factual, analytical, and data-driven positive associations; narrative/poetic/open-ended traits occupy the negative pole.",
      "SUPPORTS — auditors, examiners, validators, statisticians, planners, reviewers, and graders are high; mythic and expressive roles are low.",
      "SUPPORTS — disciplined knowledge practice, procedural competence, and externally legible standards are central to the existing blinded interpretation.",
      "SUPPORTS — the domain covers organized, dependable, persistent, and controlled goal pursuit, with item content spanning order and task completion.",
      "SUPPORTS — 20-item released key; pairwise-complete SAPA alpha is high and overlap Ns are adequate for covariance estimation.",
      "SUPPORTS — accountability wording shifted PC1 positively relative to determination and arithmetic/checking in prior matched activation contrasts.",
      "Best single established human domain for the constrained/accountable pole, but not a complete name for PC1.",
      "Does not by itself explain the strong negative Extraversion/Openness pattern, poetic/mythic pole, transparency/secularity, or model-specific external-standard accountability.", True),
    c(1, "PS:PS:S", "Stability", "Big Five Metatraits", "metatrait", "positive", "STRONG CANDIDATE",
      "SUPPORTS — positive Conscientiousness/Agreeableness and negative Neuroticism jointly characterize the high pole.",
      "PARTIAL — constrained professional roles fit maintained goal and social organization, but mythic/expressive counterroles are only indirectly covered.",
      "SUPPORTS — externally legible objectives and coherent disciplined action align with maintained goal/affective organization.",
      "SUPPORTS — the established metatrait combines Agreeableness, Conscientiousness, and Emotional Stability rather than treating one narrow proxy as the axis.",
      "SUPPORTS — a 20-item released SAPA key is available; pairwise reliability is acceptable but weaker than the narrow domain keys.",
      "PARTIAL — accountability evidence fits goal maintenance but did not manipulate the full metatrait.",
      "Broad positive-pole metatrait; strongest when paired with low Plasticity rather than used alone.",
      "Does not capture the analytical/secular/transparent content specifically, and the Stability key is a compact operationalization.", True),
    c(1, "PS:PS:P", "Plasticity", "Big Five Metatraits", "metatrait", "negative", "STRONG CANDIDATE",
      "SUPPORTS — strong negative Openness and Extraversion associations plus poetic, metaphorical, narrative, artistic, and enigmatic negative traits.",
      "SUPPORTS — poet, bard, prophet, ghost, wraith, and other possibility-expanding roles occupy the negative pole.",
      "SUPPORTS — the constraint-versus-possibility interpretation directly predicts greater exploration and expressive latitude at low PC1.",
      "SUPPORTS — Plasticity is the established shared-variance construct for Extraversion and Openness/Intellect.",
      "SUPPORTS — a 20-item released SAPA key has high pairwise-complete reliability.",
      "UNAVAILABLE — the focused accountability experiment was not a Plasticity manipulation.",
      "Best broad descriptor of the negative/possibility pole; together with Stability it explains why a single Conscientiousness label is incomplete.",
      "Low-PC1 nonhuman and mythic roles need not express human exploratory behavior; the polarity is a discovery hypothesis, not identity.", True),
    c(1, "BFAS:BFAS:C:O", "Orderliness", "Big Five Aspects", "aspect", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — methodical, cautious, regulatory, and convergent associations fit structure and order.", "SUPPORTS — auditing, checking, scheduling, and evaluation roles fit organized rule-governed work.", "SUPPORTS — procedural constraint is part of the blinded interpretation.", "SUPPORTS — the aspect directly measures preference for organization, routines, and order.", "SUPPORTS — 10-item key with strong SAPA pairwise reliability.", "PARTIAL — accountability effects are compatible but not an Orderliness-specific intervention.", "Important Conscientiousness aspect, subordinate to the broader Stability/Plasticity contrast.", "Does not cover analytical competence, achievement, or the expressive negative pole.", True),
    c(1, "BFAS:BFAS:C:I", "Industriousness", "Big Five Aspects", "aspect", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — efficient, methodical, educational, and task-focused content is positive.", "SUPPORTS — professional evaluator and reviewer roles imply sustained task engagement.", "SUPPORTS — disciplined knowledge practice includes effortful execution.", "SUPPORTS — the aspect measures diligence, persistence, efficiency, and achievement effort.", "SUPPORTS — 10-item key with strong pairwise reliability, though some pairs have smaller planned overlap.", "PARTIAL — accountability can motivate effort but was not an industriousness manipulation.", "Effort/achievement facet of the high pole.", "Does not explain order, emotional stability, or the negative symbolic pole.", True),
    c(1, "IPIPneo:C4:AS", "Achievement Striving", "IPIP-NEO", "facet", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — goal-directed, evaluative, and standards-oriented content fits the positive pole.", "SUPPORTS — examiners, researchers, planners, and graders have explicit performance criteria.", "SUPPORTS — external standards are central to the current interpretation.", "SUPPORTS — the facet measures high aspirations and sustained pursuit of excellence.", "SUPPORTS — 10-item key with strong pairwise reliability.", "PARTIAL — accountability effects fit standards but not personal ambition specifically.", "Standards/achievement facet, not an axis-level label.", "Institutional evaluation can be high PC1 without personal ambition.", True),
    c(1, "IPIPneo:C5:SD", "Self-Discipline", "IPIP-NEO", "facet", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — methodical, efficient, cautious, and calm content is compatible with task persistence.", "SUPPORTS — high-pole roles require sustained controlled execution.", "SUPPORTS — disciplined knowledge practice directly fits.", "SUPPORTS — the facet measures initiation and persistence at difficult or tedious work.", "SUPPORTS — 10-item key with very strong pairwise reliability.", "PARTIAL — focused evidence varied accountability, not stable self-discipline.", "Self-regulation facet of the high pole.", "Does not distinguish procedural standards from generic persistence.", True),
    c(1, "IPIPneo:C3:DU", "Dutifulness", "IPIP-NEO", "facet", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — principled, regulatory, and careful content is compatible with obligation.", "SUPPORTS — auditors, validators, reviewers, and graders enact explicit duties and standards.", "SUPPORTS — externally legible objectives align with obligations.", "SUPPORTS — the facet measures commitment to obligations, rules, and ethical duties.", "SUPPORTS — 10-item released key with adequate pairwise reliability.", "SUPPORTS — accountability wording is directly compatible with obligation, though still not a trait intervention.", "Obligation/accountability facet of the high pole.", "PC1 is not simply morality or compliance; high roles also require analysis and expertise.", True),
    c(1, "IPIPneo:C1:SE", "Self-Efficacy", "IPIP-NEO", "facet", "positive", "PLAUSIBLE PARTIAL CANDIDATE",
      "PARTIAL — analytical and educational associations suggest competence, but confidence is not a leading trait signal.", "PARTIAL — high-pole professional roles imply expertise, though role competence was stipulated rather than measured.", "SUPPORTS — blinded ratings found intelligence/expertise strongly relevant to PC1.", "SUPPORTS — the facet measures confidence in competence and task accomplishment.", "SUPPORTS — 10-item released key with adequate reliability.", "UNAVAILABLE — accountability contrasts did not isolate self-efficacy.", "Plausible competence component, secondary to Conscientiousness and the metatrait contrast.", "Self-confidence may not track factual transparency or procedural constraint.", False),
    c(1, "IPIP100:B5:ES", "Emotional Stability", "Big Five", "domain", "positive", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — calm is positive and Qwen strict Neuroticism is strongly negative.", "PARTIAL — high-pole roles are controlled, but role ordering is not chiefly emotional.", "PARTIAL — coherent disciplined action is compatible with stability without defining the axis.", "SUPPORTS — the domain measures calm and resilient rather than reactive responding.", "SUPPORTS — 20-item key with strong pairwise reliability.", "UNAVAILABLE — no emotional-stability intervention was run.", "Real positive-pole component and contributor to Stability.", "Fails to cover structure, analytical standards, or low-pole symbolic possibility.", False),
    c(1, "BFAS:BFAS:E:A", "Assertiveness", "Big Five Aspects", "aspect", "negative", "BROAD BUT NONSPECIFIC",
      "PARTIAL — overall Extraversion is strongly negative, but dominance/assertiveness is not the main marginal pattern.", "CONTRADICTS — auditors, supervisors, lawyers, and evaluators can be agentic despite high PC1.", "PARTIAL — low expressive possibility is not equivalent to low assertiveness.", "SUPPORTS — item content directly measures social agency, but that is not the focal PC contrast.", "SUPPORTS — 10-item reliable measure is available.", "UNAVAILABLE — no assertiveness contrast.", "Extraversion contributes, but Assertiveness alone is nonspecific and has counterexamples.", "Conflates expressive/social engagement with dominance and leadership.", False),
    c(1, "external:NFC", "Need for Cognitive Closure", "Motivated Social Cognition", "domain", "positive", "POOR MATCH",
      "PARTIAL — certainty and closure language fits, but high PC1 is factual/analytical while dogmatic and zealous content is negative.", "CONTRADICTS — high roles apply external standards; low religious/mythic roles may themselves be certain or dogmatic.", "PARTIAL — objective certainty is one interpretation component, not a demonstrated dispositional closure need.", "SUPPORTS — the construct includes desire for predictability/order and discomfort with ambiguity.", "UNAVAILABLE — the Need for Closure Scale is not part of this SAPA release.", "UNAVAILABLE — accountability is not need for closure.", "A useful rejected alternative for PC1; label-level resemblance is outweighed by pole counterexamples.", "Closure need can be dogmatic, whereas high PC1 is secular/factual and low PC1 includes zealous/fundamental content.", False, False, "https://doi.org/10.1037/0022-3514.67.6.1049"),

    # PC2: no single clean human domain; preserve the compound components.
    c(2, "PS:PS:S", "Stability", "Big Five Metatraits", "metatrait", "negative", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — negative Conscientiousness and positive Neuroticism place the reactive high pole toward low Stability.", "PARTIAL — developmental/procrastinating roles fit low organization, but low-PC2 mythic/abstract roles are not simply stable humans.", "SUPPORTS — coherent action under uncertainty implies maintained goal and affective organization.", "SUPPORTS — Stability combines goal, social, and affective regulation.", "SUPPORTS — released 20-item key with acceptable reliability.", "UNAVAILABLE — no PC2-focused manipulation establishes the metatrait.", "Best broad regulatory component, but only one part of a compound PC2 pattern.", "Agreeableness is nearly unrelated; low-PC2 abstract/ritual roles are not fully explained.", True),
    c(2, "MPQ:MPQ:CO", "Control", "Multidimensional Personality Questionnaire", "primary_trait", "negative", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — practical/casual/reactive high content and principled/formal low content fit lower versus higher deliberative control.", "SUPPORTS — procrastinator, daredevil, adolescent, and fool are high; ascetic and solemn archetypal roles are low.", "PARTIAL — coherent action requires control but also abstraction and integration.", "SUPPORTS — Control measures deliberate, cautious, planful restraint of impulsive action.", "SUPPORTS — 10-item reliable released key.", "UNAVAILABLE — no direct PC2 Control intervention.", "Strong subcomponent of the high-reactive versus low-integrated contrast, not a complete axis label.", "Experiential/practical and abstract/theoretical differences exceed behavioral control.", True),
    c(2, "IPIP100:B5:C", "Conscientiousness", "Big Five", "domain", "negative", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — the strict Qwen domain association is strongly negative and high roles include procrastination/developmental immaturity.", "SUPPORTS — high-PC2 roles often lack structured execution; low roles are more formal and principled.", "PARTIAL — disciplined coherent action is relevant but does not capture abstraction.", "SUPPORTS — broad self-regulation and organized goal pursuit fit one component.", "SUPPORTS — 20-item high-reliability SAPA key.", "UNAVAILABLE — no Conscientiousness-focused PC2 intervention.", "Broad self-regulatory component; weaker as a total PC2 analogue than as part of a composite.", "High PC2 also contains accessible, inquisitive, adaptable, and social content; low PC2 contains nonhuman/mythic roles.", True),
    c(2, "NEO_N", "Neuroticism", "IPIP-NEO", "domain", "positive", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — anxious and reactive content and the positive Qwen Neuroticism association fit the high pole.", "PARTIAL — developmental and socially volatile roles fit, but comic/casual and abstract contrasts remain.", "PARTIAL — difficulty sustaining coherent action under uncertainty can involve negative affect without being reducible to it.", "SUPPORTS — domain covers anxiety, anger, depression, self-consciousness, immoderation, and vulnerability.", "SUPPORTS — 60-item released composite with high pairwise reliability but sparse within-person administration.", "UNAVAILABLE — no direct affective manipulation.", "Affective-reactivity component, not the axis as a whole.", "Low-PC2 mythic/abstract roles do not imply low human Neuroticism.", True),
    c(2, "IPIP100:B5:E", "Extraversion", "Big Five", "domain", "positive", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — gregarious, extroverted, accessible, and casual content and the positive strict association fit.", "SUPPORTS — gossip, comedian, influencer, teenager, and fool are socially immediate high roles.", "PARTIAL — social immediacy is one contributor to the high pole but not uncertainty integration.", "SUPPORTS — domain covers social energy and outward engagement.", "SUPPORTS — 19-item official key has strong reliability.", "UNAVAILABLE — no Extraversion manipulation.", "Social-immediacy component of high PC2.", "Daredevil/procrastinator and negative abstract/ritual roles require other constructs.", True),
    c(2, "BFAS:BFAS:O:I", "Intellect", "Big Five Aspects", "aspect", "negative", "FACET / SUBCOMPONENT",
      "SUPPORTS — theoretical, abstract, conceptual, erudite, pensive, and big-picture traits are negative.", "SUPPORTS — oracle, mystic, ancient, ascetic, and other abstract archetypes are low.", "SUPPORTS — prior interpretation explicitly treats abstraction/integration as a major PC2 component.", "SUPPORTS — Intellect measures engagement with abstract ideas and complex information.", "SUPPORTS — 10-item key with strong reliability.", "UNAVAILABLE — no direct Intellect intervention.", "Best measured facet for the abstract low pole.", "The negative pole also includes ritual, reverence, and nonhuman ontology; high inquisitive content complicates a pure Intellect axis.", True),
    c(2, "BFAS:BFAS:N:V", "Volatility", "Big Five Aspects", "aspect", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — anxious/reactive/socially volatile high content.", "SUPPORTS — adolescent, gossip, daredevil, cynic, and comic roles fit variable action or affect.", "PARTIAL — volatility can disrupt coherent action but does not explain abstraction.", "SUPPORTS — the aspect measures irritability and mood instability.", "SUPPORTS — 10-item key with high alpha though planned pair overlap is lower than some scales.", "UNAVAILABLE — no volatility intervention.", "Narrow affective component of the high pole.", "High PC2 contains practical/adaptable/humble content that is not volatile.", True),
    c(2, "PS:PS:P", "Plasticity", "Big Five Metatraits", "metatrait", "positive", "BROAD BUT NONSPECIFIC",
      "PARTIAL — Extraversion and Openness are positive, but theoretical/abstract/Intellect content is strongly negative.", "PARTIAL — socially exploratory high roles fit; low mythic/abstract roles complicate the mapping.", "PARTIAL — uncertainty residence can resemble exploration but coherent abstraction is on the opposite pole.", "SUPPORTS — Plasticity measures shared exploration/engagement variance.", "SUPPORTS — reliable 20-item key.", "UNAVAILABLE — no direct test.", "Broad covariance contributor, not a specific PC2 description.", "The Openness/Intellect hierarchy splits across PC2, making the metatrait internally inconsistent with the signature.", False),
    c(2, "external:IUS", "Intolerance of Uncertainty", "Clinical/Cognitive Individual Differences", "domain", "positive", "INSUFFICIENT EVIDENCE",
      "PARTIAL — anxiety at the high pole and the interpretation language suggest relevance.", "PARTIAL — developmental/reactive roles may struggle under uncertainty, but uncertainty exposure was not measured.", "SUPPORTS — it directly resembles one interpretation phrase.", "PARTIAL — the established construct is narrower and clinically inflected relative to the role axis.", "UNAVAILABLE — no dedicated scale is present in the acquired SAPA release.", "UNAVAILABLE — no direct manipulation.", "Important external-measure possibility, not frozen as a bridge hypothesis from present evidence.", "Risk of circularly reifying an interpretation label without sufficient trait/role evidence.", False, False, "Dedicated Intolerance of Uncertainty instrument required"),

    # PC3: strong Agreeableness core plus exploitative/aggressive residuals.
    c(3, "IPIP100:B5:A", "Agreeableness", "Big Five", "domain", "negative", "STRONG CANDIDATE",
      "SUPPORTS — benevolent, nurturing, supportive, altruistic, forgiving, and agreeable are negative; callous, cynical, vindictive, dominant, confrontational, competitive, and cruel are positive.", "SUPPORTS — caregivers, empaths, counselors, therapists, and healers are low; hackers, saboteurs, provocateurs, spies, rogues, and demons are high.", "SUPPORTS — cooperative-stabilizing versus antagonistic-transgressive is the best-supported current interpretation.", "SUPPORTS — the domain directly covers cooperative, compassionate, trusting, and considerate interpersonal orientation.", "SUPPORTS — 20-item high-reliability released key.", "UNAVAILABLE — no PC3 causal manipulation is treated as validation here.", "Primary established human domain for PC3, with sign reversed: high PC3 is low Agreeableness.", "Agreeableness does not fully capture norm transgression, deception, technical intervention, or outsider register.", True),
    c(3, "BFAS:BFAS:A:C", "Compassion", "Big Five Aspects", "aspect", "negative", "FACET / SUBCOMPONENT",
      "SUPPORTS — nurturing, benevolent, supportive, altruistic, and cruel/callous oppositions are central.", "SUPPORTS — caregiver, empath, counselor, therapist, healer versus antagonistic roles.", "SUPPORTS — care and repair anchor the cooperative pole.", "SUPPORTS — item content measures emotional concern and active care.", "SUPPORTS — 10-item key with high reliability.", "UNAVAILABLE — no direct manipulation.", "A major care facet of the low pole.", "Does not cover politeness, cooperation, manipulation, or broader transgression.", True),
    c(3, "BFAS:BFAS:A:P", "Politeness", "Big Five Aspects", "aspect", "negative", "FACET / SUBCOMPONENT",
      "SUPPORTS — deferential versus dominant, blunt, confrontational, and vindictive content.", "SUPPORTS — stabilizing professional/care roles oppose disruptive and exploitative roles.", "SUPPORTS — restraint of aggressive/dominating impulses fits the cooperative pole.", "SUPPORTS — the aspect measures respect and restraint of aggression/exploitation.", "SUPPORTS — 10-item key with acceptable reliability.", "UNAVAILABLE — no direct manipulation.", "Dominance/restraint facet of the PC3 social stance.", "Some high-PC3 roles are technically adversarial without being interpersonally impolite.", True),
    c(3, "HEXACO_H", "Honesty-Humility", "HEXACO", "domain", "negative", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — callous, cynical, manipulative-adjacent, competitive, and cruel content fits lower Honesty-Humility.", "SUPPORTS — spy, saboteur, rogue, hacker, and provocateur include deception/exploitation or norm violation.", "PARTIAL — the blinded interpretation includes exploitation but was broadened beyond it.", "SUPPORTS — domain measures sincerity, fairness, modesty, and low greed/exploitation.", "SUPPORTS — released 40-item domain composite with strong pairwise reliability but sparse within-person coverage.", "UNAVAILABLE — no direct Honesty-Humility manipulation.", "Exploitative/deceptive subdimension beyond Agreeableness.", "Provocation, skepticism, humor, or technical intervention can be high PC3 without greed or dishonesty.", True),
    c(3, "MPQ:MPQ:AG", "Aggression", "Multidimensional Personality Questionnaire", "primary_trait", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — vindictive, confrontational, cruel, dominant, and challenging content.", "SUPPORTS — saboteur, provocateur, demon, and rogue fit an aggressive/antagonistic component.", "SUPPORTS — antagonistic-transgressive framing includes aggression.", "SUPPORTS — MPQ Aggression measures vindictiveness and willingness to harm.", "SUPPORTS — 10-item reliable released key.", "UNAVAILABLE — no direct manipulation.", "Positive-pole aggression component.", "Hacker, cynic, comedian, and skeptic can be high without physical or interpersonal aggression.", True),
    c(3, "IPIPneo:A3:AL", "Altruism", "IPIP-NEO", "facet", "negative", "FACET / SUBCOMPONENT",
      "SUPPORTS — altruistic/supportive/nurturing versus callous/cruel opposition.", "SUPPORTS — caregiving and helping roles define the low pole.", "SUPPORTS — cooperative stabilization includes active aid.", "SUPPORTS — the facet measures active concern and willingness to help.", "SUPPORTS — 10-item released key with adequate reliability.", "UNAVAILABLE — no direct manipulation.", "Helping-behavior facet of the cooperative pole.", "Does not capture forgiveness, politeness, skepticism, or transgressive style.", True),
    c(3, "SPI_15machiavell", "Machiavellianism", "SAPA Personality Inventory", "narrow_trait", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — cynical, callous, dominant, competitive, and manipulative-adjacent content.", "SUPPORTS — spy, saboteur, rogue, and provocateur fit strategic manipulation or exploitation.", "PARTIAL — exploitation is a component but not the complete broader interpretation.", "SUPPORTS — the SPI scale targets strategic manipulation and distrust.", "SUPPORTS — released 8-item key with acceptable human-only reliability.", "UNAVAILABLE — no direct manipulation.", "Narrow exploitative facet of high PC3.", "Many high-PC3 roles are disruptive, comic, or skeptical rather than manipulative.", True),
    c(3, "NEO_N", "Neuroticism", "IPIP-NEO", "domain", "positive", "BROAD BUT NONSPECIFIC",
      "PARTIAL — pessimism and the positive strict association fit, but anger/vindictiveness dominates more than anxiety.", "PARTIAL — cynic and gossip fit; hacker/statistician-like counterexamples do not.", "PARTIAL — antagonism can covary with negative affect but is conceptually distinct.", "SUPPORTS — some facets cover anger and distress.", "SUPPORTS — reliable 60-item composite.", "UNAVAILABLE — no direct test.", "Secondary covariance, not a PC3 analogue.", "Conflates emotional distress with antagonistic stance and care withdrawal.", False),

    # PC4 supported secondary: conventional/literal dependence vs autonomous systemic revision.
    c(4, "IPIP100:B5:O", "Openness/Intellect", "Big Five", "domain", "negative", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — holistic, systems-thinking, big-picture, introspective, interdisciplinary, progressive, and critical traits are negative; literal, reductionist, and traditional traits are positive.", "SUPPORTS — visionary, revolutionary, maverick, rebel, and contrarian are negative; literal/developmental roles are positive.", "UNAVAILABLE — no mature coordinate-blind interpretation for this secondary axis.", "SUPPORTS — domain covers intellectual curiosity, imagination, and receptivity to ideas/experience.", "SUPPORTS — 20-item reliable key.", "UNAVAILABLE — no focused PC4 activation evidence.", "Best broad available descriptor, with high PC4 corresponding to lower Openness/Intellect.", "Avoidance/deference/naivety and infant/toddler/caveman roles are not fully explained; axis stability is secondary.", True),
    c(4, "MPQ:MPQ:TR", "Traditionalism", "Multidimensional Personality Questionnaire", "primary_trait", "positive", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — traditional, deferential, literal content is positive; progressive/deconstructionist content is negative.", "SUPPORTS — traditionalist/constrained roles tend positive relative to revolutionary/rebel/activist roles.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — construct measures conventional morality, institutions, and propriety.", "SUPPORTS — 10-item reliable released key.", "UNAVAILABLE — no focused evidence.", "Conventionality component of PC4.", "Infant, toddler, pirate, translator, and proofreader are not a coherent Traditionalism group; political content is not the whole axis.", True),
    c(4, "BFAS:BFAS:O:I", "Intellect", "Big Five Aspects", "aspect", "negative", "FACET / SUBCOMPONENT",
      "SUPPORTS — systems, big-picture, critical, interdisciplinary content is negative versus literal/reductionist positive.", "PARTIAL — visionary and systems-oriented roles fit, but developmental positives do not map cleanly.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — aspect measures engagement with abstract ideas and complex information.", "SUPPORTS — 10-item reliable key.", "UNAVAILABLE — no direct evidence.", "Cognitive-complexity facet of the negative pole.", "Avoidant/deferential and political-autonomy contrasts exceed Intellect.", True),
    c(4, "HEXACO:H:O:U", "Unconventionality", "HEXACO", "facet", "negative", "FACET / SUBCOMPONENT",
      "SUPPORTS — progressive, constructivist, deconstructionist content is negative while traditional is positive.", "SUPPORTS — revolutionary, anarchist, maverick, rebel, and provocateur are negative.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — facet measures receptivity to unusual ideas and resistance to convention.", "SUPPORTS — 10-item reliable key.", "UNAVAILABLE — no focused evidence.", "Convention-challenging facet of the negative pole.", "Does not cover systems cognition or avoidant/developmental positives.", True),
    c(4, "IPIPneo:O6:LI", "Liberalism", "IPIP-NEO", "facet", "negative", "FACET / SUBCOMPONENT",
      "SUPPORTS — progressive, critical, independent and deconstructionist traits are negative.", "SUPPORTS — revolutionary/rebel/activist/contrarian roles occupy the negative pole.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — the IPIP-NEO facet operationalizes questioning convention, authority, and inherited values; it is not a partisan label.", "SUPPORTS — 10-item key with adequate reliability.", "UNAVAILABLE — no focused evidence.", "Authority/convention-questioning facet.", "Political valence can overfit the role vocabulary and does not explain literal/reductionist or developmental content.", True),
    c(4, "HEXACO:H:A:FL", "Flexibility", "HEXACO", "facet", "negative", "POOR MATCH",
      "PARTIAL — adaptability and openness language superficially resembles the negative pole.", "CONTRADICTS — the role contrast is autonomy/system revision, not interpersonal compromise.", "UNAVAILABLE — no mature blinded interpretation.", "CONTRADICTS — HEXACO Flexibility concerns compromise in disagreement, not cognitive flexibility.", "SUPPORTS — reliable 10-item measure exists.", "UNAVAILABLE — no focused evidence.", "Rejected label trap: the authoritative item content does not match cognitive/systemic flexibility.", "Same word, different construct boundary.", False),

    # PC5 supported secondary: divergent exploratory cognition vs convergent closure/action.
    c(5, "IPIP100:B5:O", "Openness/Intellect", "Big Five", "domain", "positive", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — divergent, curious, introspective, futuristic, inclusive, interdisciplinary, exploratory, eclectic, and progressive traits are positive; closure-seeking, convergent, traditional, and practical traits are negative.", "PARTIAL — imaginative/comic/alien roles are positive and militarized/constrained roles negative, but developmental positives complicate the domain.", "UNAVAILABLE — no mature coordinate-blind interpretation for PC5.", "SUPPORTS — broad domain covers exploration, imagination, ideas, and aesthetic engagement.", "SUPPORTS — 20-item reliable key.", "UNAVAILABLE — no focused PC5 evidence.", "Best broad available descriptor of the exploratory/divergent pole.", "Strict Qwen Openness association is only modest; closure/efficiency and militarized role content are not exhausted by Openness.", True),
    c(5, "PS:PS:P", "Plasticity", "Big Five Metatraits", "metatrait", "positive", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — exploratory, curious, divergent, cosmopolitan, and future-oriented content fits novelty engagement.", "PARTIAL — comic and imaginative positives fit; infants/toddlers/procrastinators and military negatives add developmental/constraint content.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — metatrait measures exploration and engagement with novelty.", "SUPPORTS — 20-item high-reliability key.", "UNAVAILABLE — no focused evidence.", "Broad exploration metatrait, secondary to the more specific Openness/facet pattern.", "Extraversion association is weak, so the full metatrait is broader than PC5.", True),
    c(5, "HEXACO:H:O:C", "Creativity", "HEXACO", "facet", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — divergent, futuristic, eclectic, exploratory traits.", "SUPPORTS — designer, comic, absurdist, and imaginative/nonordinary roles fit better than military/convergent roles.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — facet measures innovation, imagination, and original production.", "SUPPORTS — 10-item reliable key.", "UNAVAILABLE — no focused evidence.", "Original-production facet of the positive pole.", "Does not capture cosmopolitanism, inclusion, or low closure by itself.", True),
    c(5, "HEXACO:H:O:I", "Inquisitiveness", "HEXACO", "facet", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — curious, exploratory, interdisciplinary, and futuristic content.", "PARTIAL — dilettante/linguist/nonordinary roles fit, but comic/developmental roles are mixed.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — facet measures curiosity about knowledge and the world.", "SUPPORTS — 10-item key with adequate reliability.", "UNAVAILABLE — no focused evidence.", "Curiosity facet of positive PC5.", "The Qwen model trait inquisitive is not among the very top PC5 associations and action/closure content remains.", True),
    c(5, "HEXACO:H:O:U", "Unconventionality", "HEXACO", "facet", "positive", "FACET / SUBCOMPONENT",
      "SUPPORTS — divergent, eclectic, progressive, exploratory content versus traditional/fundamentalist content.", "SUPPORTS — absurdist, fool, alien, simulacrum, and comedian are positive relative to conventional martial roles.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — facet measures receptivity to unusual ideas.", "SUPPORTS — reliable 10-item key.", "UNAVAILABLE — no focused evidence.", "Nonconformity facet of positive PC5.", "Infant/toddler/procrastinator positives are not unconventional beliefs.", True),
    c(5, "MPQ:MPQ:AB", "Absorption", "Multidimensional Personality Questionnaire", "primary_trait", "positive", "FACET / SUBCOMPONENT",
      "PARTIAL — introspective, divergent, and nonordinary content fits imaginative involvement.", "PARTIAL — alien, simulacrum, void, absurdist, and comic roles fit nonordinary engagement.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — Absorption measures immersive imaginative and perceptual involvement.", "SUPPORTS — 10-item reliable released key.", "UNAVAILABLE — no focused evidence.", "Experiential/imaginative subcomponent.", "Cosmopolitan/inclusive/futuristic content and closure/efficiency opposition are not absorption.", True),
    c(5, "MPQ:MPQ:TR", "Traditionalism", "Multidimensional Personality Questionnaire", "primary_trait", "negative", "FACET / SUBCOMPONENT",
      "SUPPORTS — traditional and fundamentalist traits are negative; progressive/cosmopolitan traits positive.", "PARTIAL — conventional martial/provincial roles are negative, though criminal/pirate counterexamples are not traditional.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — construct measures conventionality and traditional institutions.", "SUPPORTS — 10-item reliable key.", "UNAVAILABLE — no focused evidence.", "Conventionality component of the negative pole.", "Efficiency, decisiveness, and closure are not identical to Traditionalism.", True),
    c(5, "SPI_15impulsivity", "Impulsivity", "SAPA Personality Inventory", "narrow_trait", "positive", "BROAD BUT NONSPECIFIC",
      "PARTIAL — developmental and procrastinating roles suggest weak restraint, but the top trait pattern is cognitive divergence rather than impulsivity.", "PARTIAL — infant, toddler, fool, comedian, and procrastinator fit, but alien/linguist/simulacrum do not.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — scale directly measures unplanned immediate action.", "SUPPORTS — 8-item released key with human-only reliability.", "UNAVAILABLE — no focused evidence.", "Developmental covariance possibility, not a general PC5 analogue.", "Would collapse exploratory cognition into behavioral disinhibition.", False),

    # PC6 supported secondary: principled/absolute closure vs pluralistic systems exploration.
    c(6, "external:NFC", "Need for Cognitive Closure", "Motivated Social Cognition", "domain", "positive", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — deontological, universalist, fundamentalist, principled, absolutist, convergent, dogmatic, and literal positive traits oppose divergent/exploratory/systemic traits.", "SUPPORTS — zealot, stoic, martyr, judge, purist, traditionalist, and skeptic fit committed definite frameworks, although anarchist/revolutionary content spans ideologies.", "UNAVAILABLE — no mature coordinate-blind interpretation for PC6.", "SUPPORTS — the construct includes predictability/order, discomfort with ambiguity, and close-mindedness.", "UNAVAILABLE — no dedicated Need for Closure Scale is present in the acquired SAPA release; another dataset is required.", "UNAVAILABLE — no focused PC6 evidence.", "Best named external construct candidate for cognitive closure/absolute principle, but not currently measurable in SAPA and not a complete axis label.", "The PC6 pole includes principled commitment across opposed ideologies, not merely desire for quick answers; axis stability is secondary.", True, False, "https://doi.org/10.1037/0022-3514.67.6.1049"),
    c(6, "IPIP100:B5:O", "Openness/Intellect", "Big Five", "domain", "negative", "PLAUSIBLE PARTIAL CANDIDATE",
      "SUPPORTS — systems-thinking, divergent, holistic, interdisciplinary, futuristic, curious, and exploratory traits are negative; literal, fundamentalist, and dogmatic traits positive.", "PARTIAL — creative/aesthetic lifestyle roles are negative, but anarchist/revolutionary positive roles are not conventionally low Openness.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — domain covers intellectual exploration and receptivity to ideas.", "SUPPORTS — reliable 20-item key.", "UNAVAILABLE — no focused evidence.", "Available SAPA proxy for the exploratory negative pole, but only partial.", "Qwen strict association is weak and political/ethical commitment cuts across conventional openness content.", True),
    c(6, "MPQ:MPQ:TR", "Traditionalism", "Multidimensional Personality Questionnaire", "primary_trait", "positive", "BROAD BUT NONSPECIFIC",
      "PARTIAL — fundamentalist, deontological, literal, and dogmatic positive traits fit.", "CONTRADICTS — anarchist and revolutionary are among the positive role extremes alongside traditionalist.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — construct measures conventional moral/institutional commitment.", "SUPPORTS — reliable 10-item key.", "UNAVAILABLE — no focused evidence.", "Captures one conventional subset but not the content-invariant principled/absolute structure.", "Would mistake intensity/form of commitment for its political or traditional content.", False),
    c(6, "IPIPneo:C3:DU", "Dutifulness", "IPIP-NEO", "facet", "positive", "FACET / SUBCOMPONENT",
      "PARTIAL — deontological and principled content fits duty, but Conscientiousness as a whole is nearly unrelated.", "PARTIAL — judge, stoic, martyr, purist, and pacifist may embody obligation; anarchist and cynic complicate it.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — facet measures obligations, rules, and ethical duties.", "SUPPORTS — 10-item reliable key.", "UNAVAILABLE — no focused evidence.", "Moral-obligation facet of the positive pole.", "Cannot explain systems/divergent negative traits or cross-ideological extremity.", True),
    c(6, "HEXACO:H:O:U", "Unconventionality", "HEXACO", "facet", "negative", "POOR MATCH",
      "PARTIAL — exploratory/divergent negative traits fit lower closure.", "CONTRADICTS — anarchist and revolutionary are positive, while creative lifestyle roles are negative.", "UNAVAILABLE — no mature blinded interpretation.", "SUPPORTS — the facet measures unusual ideas and resistance to convention.", "SUPPORTS — reliable 10-item key.", "UNAVAILABLE — no focused evidence.", "Rejected as a total PC6 analogue because political unconventionality and cognitive exploration separate.", "Strong role-level counterexamples and weak Qwen strict Openness association.", False),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = args.output_dir.resolve()
    signature_path = output / "qwen_pc1_pc6_model_side_signatures.csv"
    library_path = output / "human_construct_library.csv"
    rubric_path = output / "human_construct_match_rubric.md"
    signature = pd.read_csv(signature_path)
    library = pd.read_csv(library_path)
    library_by_id = library.set_index("construct_id", drop=False)

    if len(signature[signature["evidence_class"] == "model_trait_association"]) != 6 * 240:
        raise ValueError("Frozen signature must contain 240 trait rows for each PC1-PC6")
    if not all(item["match_status"] in ALLOWED_STATUSES for item in CANDIDATES):
        raise ValueError("Candidate status outside frozen rubric")
    if {item["pc"] for item in CANDIDATES} != {f"PC{i}" for i in range(1, 7)}:
        raise ValueError("Every PC1-PC6 must be represented")
    for item in CANDIDATES:
        if item["sapa_available"] and item["construct_id"] not in library_by_id.index:
            raise ValueError(f"Unknown SAPA construct {item['construct_id']}")

    candidate = pd.DataFrame(CANDIDATES)
    candidate.to_csv(output / "qwen_pc_human_construct_candidates.csv", index=False, lineterminator="\n")

    frozen = candidate[candidate["freeze_in_hypothesis_set"]].copy()
    frozen["evidence_summary"] = frozen.apply(
        lambda row: f"Traits: {row.model_trait_profile_coverage} Roles: {row.role_profile_coverage} Blinded evidence: {row.blinded_interpretation_alignment}",
        axis=1,
    )
    frozen["model_side_dependencies"] = "qwen_pc1_pc6_model_side_signatures.csv; Qwen/Qwen3-32B only"
    frozen["measurement_quality"] = frozen["human_measurement_quality"]
    frozen = frozen[[
        "pc", "axis_status_core_or_secondary", "human_construct", "construct_id", "framework",
        "level_domain_aspect_facet", "polarity", "match_status", "evidence_summary",
        "model_side_dependencies", "human_measurement_source", "sapa_available",
        "measurement_quality", "known_mismatches", "validation_status",
    ]]
    frozen.to_csv(output / "qwen_derived_human_construct_hypotheses_v1.csv", index=False, lineterminator="\n")

    # Human-only scoring availability for frozen constructs. No identifiers are
    # read; only the union of q_* item columns is loaded.
    sapa_rows = frozen[frozen["sapa_available"]].copy()
    selected_ids = sorted(sapa_rows["construct_id"].unique())
    item_sets = {cid: str(library_by_id.loc[cid, "item_ids"]).split(";") for cid in selected_ids}
    raw_path = repo / "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/sapaTempData696items08dec2013thru26jul2014.tab"
    union_items = sorted({item for items in item_sets.values() for item in items})
    responses = pd.read_csv(raw_path, sep="\t", usecols=union_items, dtype=np.float32, na_values=[-999, "-999", "NA", ""], low_memory=False)
    feasibility_by_id: dict[str, dict[str, object]] = {}
    for cid in selected_ids:
        row = library_by_id.loc[cid]
        items = item_sets[cid]
        observed = responses[items].notna().sum(axis=1).to_numpy(dtype=int)
        other_ids = [other for other in selected_ids if other != cid]
        overlaps = []
        for other in other_ids:
            inter = set(items) & set(item_sets[other])
            union = set(items) | set(item_sets[other])
            overlaps.append((len(inter) / len(union), len(inter), other))
        overlaps.sort(reverse=True)
        best_overlap = overlaps[0] if overlaps else (0.0, 0, "")
        feasibility_by_id[cid] = {
            "construct_id": cid,
            "sapa_available": True,
            "source_item_count": int(row.source_item_count),
            "official_scoring_key": row.official_scoring_key,
            "sapa_pairwise_standardized_alpha": row.sapa_pairwise_standardized_alpha,
            "item_valid_n_min": int(row.item_valid_n_min),
            "item_valid_n_median": float(row.item_valid_n_median),
            "pairwise_n_median": float(row.pairwise_n_median),
            "respondent_n": int(len(observed)),
            "respondents_with_at_least_1_item": int((observed >= 1).sum()),
            "respondents_with_at_least_2_items": int((observed >= 2).sum()),
            "respondents_with_at_least_half_items": int((observed >= int(np.ceil(len(items) / 2))).sum()),
            "respondents_with_all_items": int((observed == len(items)).sum()),
            "observed_items_per_respondent_q25": float(np.quantile(observed, 0.25)),
            "observed_items_per_respondent_median": float(np.median(observed)),
            "observed_items_per_respondent_q75": float(np.quantile(observed, 0.75)),
            "maximum_item_overlap_jaccard_with_other_selected_construct": round(float(best_overlap[0]), 8),
            "maximum_shared_item_count_with_other_selected_construct": int(best_overlap[1]),
            "most_overlapping_selected_construct_id": best_overlap[2],
            "respondent_level_scoring_assessment": "Partial-information scoring is plausible; complete-key scoring is generally sparse. A later method must model randomized planned missingness and construct hierarchy.",
        }
    feasibility_rows = []
    for row in frozen.itertuples(index=False):
        if row.sapa_available:
            human = feasibility_by_id[row.construct_id]
        else:
            human = {
                "construct_id": row.construct_id, "sapa_available": False,
                "source_item_count": "", "official_scoring_key": "", "sapa_pairwise_standardized_alpha": "",
                "item_valid_n_min": "", "item_valid_n_median": "", "pairwise_n_median": "", "respondent_n": "",
                "respondents_with_at_least_1_item": "", "respondents_with_at_least_2_items": "",
                "respondents_with_at_least_half_items": "", "respondents_with_all_items": "",
                "observed_items_per_respondent_q25": "", "observed_items_per_respondent_median": "",
                "observed_items_per_respondent_q75": "", "maximum_item_overlap_jaccard_with_other_selected_construct": "",
                "maximum_shared_item_count_with_other_selected_construct": "", "most_overlapping_selected_construct_id": "",
                "respondent_level_scoring_assessment": "Not measured in the acquired SAPA release; an independent human instrument/dataset is required.",
            }
        feasibility_rows.append({"pc": row.pc, "human_construct": row.human_construct, "framework": row.framework, "level": row.level_domain_aspect_facet, "polarity": row.polarity, "match_status": row.match_status, **human})
    pd.DataFrame(feasibility_rows).to_csv(output / "selected_construct_human_measurement_feasibility.csv", index=False, lineterminator="\n")

    summary = {
        "generated_at_utc": GENERATED_AT,
        "rubric_sha256": sha256(rubric_path),
        "signature_sha256": sha256(signature_path),
        "construct_library_sha256": sha256(library_path),
        "candidate_count": len(candidate),
        "frozen_hypothesis_count": len(frozen),
        "status_counts_all_candidates": candidate["match_status"].value_counts().sort_index().to_dict(),
        "status_counts_frozen": frozen["match_status"].value_counts().sort_index().to_dict(),
        "frozen_by_pc": frozen.groupby("pc").size().to_dict(),
        "sapa_available_frozen_rows": int(frozen["sapa_available"].sum()),
        "external_measure_required_frozen_rows": int((~frozen["sapa_available"]).sum()),
        "human_response_columns_read": len(union_items),
        "human_respondent_identifier_read": False,
        "respondent_level_output_written": False,
        "cross_model_input": False,
        "aa7_input": False,
        "human_projection": False,
        "validation_status": VALIDATION_STATUS,
        "source_hashes": {str(path.relative_to(repo)): sha256(path) for path in [signature_path, library_path, rubric_path, raw_path]},
    }
    (output / "qwen_human_construct_freeze_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
