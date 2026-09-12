#!/usr/bin/env python3
"""Build full-library SAPA reconsideration and item-level audits for AA-8."""

from __future__ import annotations

import argparse
import csv
import io
import re
import subprocess
from pathlib import Path


SOURCE_COMMIT = "6497d28383aac33ea9f61b6ce2ac2ff195dccae4"
LIBRARY_PATH = "research/outputs/qwen_pc_human_construct_bridge/human_construct_library.csv"


def git_csv(repo: Path, commit: str, path: str) -> list[dict[str, str]]:
    text = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=repo, text=True)
    return list(csv.DictReader(io.StringIO(text)))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames, seen = [], set()
        for row in rows:
            for key in row:
                if key not in seen:
                    fieldnames.append(key)
                    seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def assessment(
    direction: str,
    positive: str,
    negative: str,
    concentrated: str,
    strict: str,
    roles: str,
    prior: str,
    focused: str,
    definition: str,
    items: str,
    contradictions: str,
    residual: str,
    match: str,
    disposition: str,
) -> dict[str, str]:
    return {
        "proposed_measurement_direction": direction,
        "positive_pole_marker_coverage": positive,
        "negative_pole_inverse_coherence": negative,
        "highly_concentrated_marker_coverage": concentrated,
        "strict_axis_specific_marker_coverage": strict,
        "role_persona_coherence": roles,
        "prior_model_side_interpretation_coherence": prior,
        "focused_activation_or_role_rating_coherence": focused,
        "human_construct_definition_fit": definition,
        "human_item_content_fit": items,
        "important_contradictions": contradictions,
        "model_specific_residual_content": residual,
        "overall_match": match,
        "previous_mapping_disposition": disposition,
    }


PC1 = {
    "NEO_C": assessment(
        "higher -> positive PC1",
        "Covers disciplined, careful, planful execution in the broad positive context.",
        "Lower scores partly fit spontaneity, impulsivity, and disorganization on negative PC1.",
        "Indirect coverage of methodical and cautious; does not cover factual, transparent, analytical, quantitative, or secular.",
        "Covers cautious and some methodical/procedural content; the negative strict pole is mostly symbolic-expression content outside Conscientiousness.",
        "Fits auditor/examiner/evaluator/validator roles and the professional hierarchy, but not the full negative expressive continuum.",
        "Consistent with the accountability/procedural evidence as one component, not the complete axis.",
        "Accountability effects support standards-governed execution; they do not establish broad Conscientiousness.",
        "Broad goal regulation is relevant but less specific than external standards plus disciplined knowledge practice.",
        "Items cover competence, order, duty, achievement, discipline, and deliberation; none measure empirical transparency as a unit.",
        "High Conscientiousness can coexist with poetic, imaginative, or symbolic cognition; low Conscientiousness does not imply those styles.",
        "Factuality, transparent communication, quantitative epistemics, and expressive-symbolic imagination remain outside the construct.",
        "PARTIAL_COMPONENT",
        "DOWNGRADE_AND_DECOMPOSE broad Conscientiousness; retain facets.",
    ),
    "BFAS:BFAS:C:O": assessment(
        "higher -> positive PC1", "Covers organization, routine, and rule-governed structure.", "Lower Orderliness weakly fits improvisation and spontaneity.", "Covers methodical/cautious only indirectly.", "Directly relevant to methodical; not to most strict positive or symbolic negative markers.", "Fits standards-bearing roles but is narrower than their knowledge/accountability content.", "External-standard evidence is compatible, while vocabulary tests showed orderliness weaker than accountability.", "Focused accountability effects exceed arithmetic/checking, limiting a pure orderliness account.", "Good facet fit for structure, not the whole axis.", "Items include schedules, order, routines, and rules being observed.", "Does not explain transparent/factual/analytical markers or narrative/poetic symbolism.", "Most epistemic and expressive content remains.", "PARTIAL_COMPONENT", "RETAIN as subordinate facet."),
    "IPIPneo:C3:DU": assessment(
        "higher -> positive PC1", "Directly covers obligations, rules, ethical duties, and accountable execution.", "Lower Dutifulness partly coheres with libertarian/subversive/improvisational context.", "Does not directly cover the core empirical markers but addresses the hypothesized standards mechanism.", "Rule/duty content complements methodical/cautious; does not cover the expressive-symbolic pole.", "Strong fit to auditor, examiner, judge, validator, soldier, and other standards-bearing roles.", "Among human constructs, this most directly represents the external-obligation part of the PC1 hypothesis.", "Compatible with accountability/scrutiny activation, though the intervention tested prompt wording rather than human Dutifulness.", "Strong definition fit for one proposed mechanism.", "Items explicitly cover breaking/following rules, duties, promises, taxes, and obligations.", "Ethical duty is narrower than empirical rigor; negative PC1 need not be undutiful.", "Knowledge practice, factuality, transparency, and expressive imagination remain.", "PLAUSIBLE_BIPOLAR_MATCH", "ADD as leading positive-pole facet; do not elevate to whole-axis identity."),
    "HEXACO:H:C:PE": assessment(
        "higher -> positive PC1", "Covers accuracy checking, detail, and avoiding errors.", "Lower Perfectionism partly fits improvisation and looseness.", "Indirectly covers methodical/cautious; not empirical transparency.", "Covers methodical/cautious and accuracy context, not the symbolic pole.", "Fits auditor, proofreader, validator, and checker roles.", "Supports correct-execution content, but previous specificity work showed `perfectionist` itself cross-loads.", "Accountability exceeded arithmetic/checking, so perfectionism cannot be the primary mechanism.", "Good narrow fit for error control.", "Items directly address mistakes, details, checking, and accuracy.", "Perfectionism also loads on negative PC2/formal abstraction and can be internally rather than externally motivated.", "External accountability, disciplined knowledge, and symbolic expression remain.", "PARTIAL_COMPONENT", "RETAIN as accuracy/correctness facet."),
    "IPIPneo:C6:CA": assessment(
        "higher -> positive PC1", "Covers deliberation and caution.", "Lower scores fit impulsive/spontaneous portions of negative PC1.", "Directly covers cautious, a highly concentrated positive marker.", "Covers cautious and some methodical content.", "Fits risk-managed professional roles but not necessarily epistemic transparency.", "Compatible with the positive pole but not central to prior accountability results.", "No focused evidence isolates deliberation as the driver.", "Good narrow fit.", "Items emphasize avoiding mistakes and considering consequences.", "Caution can inhibit transparent or decisive factual communication; expressive imagination is not simply incaution.", "Most analytic and symbolic content remains.", "PARTIAL_COMPONENT", "RETAIN as narrow marker-level analogue."),
    "IPIPneo:C5:SD": assessment(
        "higher -> positive PC1", "Covers persistence and disciplined task initiation.", "Lower scores fit some impulsive/disorganized background traits.", "Little direct coverage of the 11 highly concentrated positive markers.", "No strict marker is self-discipline by name.", "Fits work-focused roles but not uniquely the standards-bearing pole.", "Determination/persistence performed worse than accountability in the competing-theories audit.", "Focused accountability prompts exceeded determination prompts.", "Relevant but nonspecific.", "Items center task completion and persistence.", "Does not cover factuality or symbolic expressiveness and is explicitly weakened as a primary explanation.", "Axis-specific epistemic style remains.", "WEAK_OR_NONSPECIFIC", "DOWNGRADE from any broad Conscientiousness inference."),
    "BFAS:BFAS:C:I": assessment(
        "higher -> positive PC1", "Covers diligent, efficient achievement.", "Lower scores fit some disorganization but not the expressive-symbolic family.", "No direct highly concentrated marker coverage.", "No strict-marker match beyond weak methodical proximity.", "Professional roles may be industrious, but industriousness does not distinguish auditor from poet.", "Prior evidence favored external standards over determination.", "Accountability activation weakens effort-only explanations.", "Nonspecific goal-pursuit construct.", "Items cover work, persistence, task completion, and goals.", "Achievement effort is orthogonal to many epistemic/register contrasts.", "Transparency, empirical discipline, and symbolic imagination remain.", "WEAK_OR_NONSPECIFIC", "DOWNGRADE as primary; retain only background facet."),
    "IPIPneo:C4:AS": assessment(
        "higher -> positive PC1", "Covers excellence and standards for performance.", "Lower scores do not imply symbolic imagination.", "No direct concentrated-marker coverage.", "No strict marker is achievement striving.", "Some professional roles fit, but the full continuum does not.", "External criteria matter, but ambition did not emerge as the best model-side explanation.", "Focused activation did not test achievement.", "Narrow and nonspecific.", "Items concern ambition, excellence, and goals, with one high-standards item.", "Internal ambition differs from accountability to externally legible criteria.", "Empirical and expressive poles remain.", "WEAK_OR_NONSPECIFIC", "RETAIN only as peripheral standards facet."),
    "IPIPneo:C1:SE": assessment(
        "higher -> positive PC1", "Covers perceived competence.", "Low self-efficacy has little coherent relation to negative PC1 symbolism.", "No direct concentrated-marker coverage.", "No strict marker match.", "Expert roles may be high, but many negative-PC1 roles are also highly skilled.", "Blind intelligence/expertise predicts PC1, but self-efficacy is not expertise.", "No focused evidence.", "Definition mismatch for the axis.", "Items ask confidence and task competence.", "Confuses confidence with disciplined knowledge practice.", "Nearly all axis content remains.", "POOR_MATCH", "DO NOT PROMOTE."),
    "HEXACO:H:H:S": assessment(
        "higher -> positive PC1", "Covers nondeceptive, unmanipulative presentation and a narrow aspect of transparency.", "Lower Sincerity fits manipulative/sycophantic content on negative PC1 but not its artistic core.", "Transparent is highly concentrated, but human Sincerity is interpersonal nonmanipulation rather than epistemic transparency.", "Covers transparent only by partial semantic overlap.", "Some professional-legibility roles fit; negative expressive roles need not be insincere.", "Prior mapping correctly treated this as a facet, not a family-level match.", "Accountability evidence does not isolate honesty.", "Partial definition fit.", "Items focus flattery, manipulation, strategic charm, and deception.", "The construct misses factual accuracy and wrongly moralizes expressive-symbolic style if treated as bipolar axis.", "Empirical rigor and most negative-pole content remain.", "PARTIAL_COMPONENT", "RETAIN but narrow the rationale."),
    "QB6:QB6:H": assessment(
        "higher -> positive PC1", "Covers rule-respecting conduct and integrity.", "Lower scores weakly fit subversion/nonconformity.", "No direct empirical-marker coverage.", "No strict marker match except contextual rule adherence.", "Fits institutional-legibility roles.", "Relevant to rule compliance but blends honesty, propriety, exploitation, and entitlement.", "No focused construct-specific evidence.", "Broad semantic neighbor.", "Items include sticking to rules plus honesty/propriety content.", "Rule respect can be conventional rather than epistemically rigorous.", "Analytic and expressive content remains.", "PARTIAL_COMPONENT", "ADD as secondary rule-respect analogue."),
    "BFAS:BFAS:O:I": assessment(
        "higher -> positive PC1", "Covers analytical reasoning, complex information, and intellectual confidence.", "Its logical inverse does not cover poetic, symbolic, or imaginative negative PC1; those are often positively related to broader Openness/Intellect.", "Covers analytical, rationalist, quantitative, educational, and data-driven by proximity.", "Strongest coverage is analytical/quantitative; transparent/factual/procedural remain.", "Fits scientist, statistician, analyst, and researcher roles, but also negative-PC2 theorist/philosopher roles.", "Blind intelligence/expertise correlated strongly with PC1, supporting this component.", "Focused accountability evidence shows Intellect is not sufficient.", "Good fit for disciplined reasoning, poor fit for the whole bipolar axis.", "Items emphasize abstract ideas, difficult reading, vocabulary, and reasoning, not empirical procedure.", "Human Intellect is strongly abstract, while Qwen PC1 positive is not the negative-PC2 abstract/theoretical pole.", "External accountability and expressive symbolism remain.", "PARTIAL_COMPONENT", "RETAIN with explicit PC2 cross-interpretation caveat."),
    "BFAS:BFAS:O:O": assessment(
        "higher -> negative PC1", "Lower Openness partly fits literal, descriptive, materialist, and convergent positive context.", "Directly covers aesthetic, imaginative, fantasy, and perceptual negative PC1.", "Covers romantic, poetic, artistic, mystical, whimsical, intuitive, spiritual, and creative markers.", "Covers many strict negative markers and is the strongest prior family-level match.", "Fits bard, poet, dreamer, mystic, actor, and related negative-PC1 roles.", "Coheres strongly with the expressive-symbolic pole.", "No focused activation targeted Openness, but role evidence is consistent.", "Strong definition fit for the negative half; incomplete positive inverse.", "Items cover fantasy, beauty, poetry, reflection, and imagination.", "Low Openness is not equivalent to transparent factual analytical procedure.", "External standards and disciplined knowledge practice remain unmeasured.", "PLAUSIBLE_BIPOLAR_MATCH", "RETAIN as best negative-pole human analogue, not a complete axis label."),
    "IPIPneo:O1:IM": assessment(
        "higher -> negative PC1", "Low Imagination weakly fits literal/descriptive communication.", "Directly covers fantasy and imaginative engagement.", "Covers romantic, poetic, metaphorical, whimsical, creative, and narrative content.", "Covers a large strict negative subfamily.", "Strong role coherence on the expressive-symbolic side.", "Consistent with prior mapping.", "No focused activation.", "Good narrow facet fit.", "Items center fantasy, daydreaming, and vivid imagination.", "Does not cover rhetoric, charisma, nonconformity, or the positive procedural pole.", "Most positive-pole mechanism remains.", "PARTIAL_COMPONENT", "RETAIN."),
    "IPIPneo:O2:AI": assessment(
        "higher -> negative PC1", "Low Artistic Interests has little positive-pole explanatory power.", "Covers aesthetic and artistic engagement.", "Covers artistic/poetic/creative markers.", "Covers a narrow strict-negative subset.", "Fits artist/composer/poet roles.", "Consistent with prior mapping.", "No focused activation.", "Good narrow facet fit.", "Items cover art, poetry, beauty, dance, and aesthetics.", "No procedural or accountability inverse.", "Most axis content remains.", "PARTIAL_COMPONENT", "RETAIN."),
    "MPQ:MPQ:AB": assessment(
        "higher -> negative PC1", "Low Absorption weakly fits literal/detached positive context.", "Covers immersive imagination, fantasy, altered experience, and reflection.", "Covers ethereal, enigmatic, mystical, intuitive, spiritual, whimsical, and creative content.", "Covers a meaningful strict-negative subset.", "Fits mystic/dreamer/oracle regions more than performative roles.", "Consistent with prior mapping.", "No focused activation.", "Good component fit.", "Items cover fantasy, thought absorption, poetry, and beauty.", "Misses narrative performance, rhetoric, and institutional/procedural inverse.", "Most positive pole remains.", "PARTIAL_COMPONENT", "RETAIN."),
    "HEXACO:H:X:E": assessment(
        "higher -> negative PC1", "Low Expressiveness may fit reserved/detached positive context.", "Covers charismatic, theatrical, effusive, animated, and emotional expression.", "Covers charismatic and some dramatic/performative content.", "Covers a narrower strict-negative performance subset.", "Fits actor, bard, comedian, presenter, and performer roles.", "Consistent with prior partial mapping.", "No focused activation.", "Good expressive facet fit.", "Items emphasize emotional expression and public comfort.", "Does not cover poetic symbolism or factual procedure.", "Large residual on both poles.", "PARTIAL_COMPONENT", "RETAIN."),
    "MPQ:MPQ:CO": assessment(
        "higher -> positive PC1", "Covers deliberation, planning, restraint, and control.", "Lower Control fits impulsive/spontaneous portions of the negative context.", "Indirectly covers cautious/methodical only.", "Narrow strict-positive overlap.", "Fits constrained procedural roles.", "Relevant but less specific than duty/accountability and empirical reasoning.", "Accountability evidence limits a generic control interpretation.", "Moderate component fit.", "Items cover planning, caution, and impulse control.", "Does not cover the symbolic core or epistemic transparency.", "Substantial residual.", "PARTIAL_COMPONENT", "RETAIN as secondary restraint facet."),
    "MPQ:MPQ:TR": assessment(
        "higher -> positive PC1 only weakly", "Covers conventional institutions and propriety.", "Lower Traditionalism weakly fits libertarian/subversive content but not the broad symbolic family.", "No concentrated-marker match; secular points in the opposite direction from religiosity/tradition.", "Traditional itself is associated but cross-loading, not strict.", "Some institutional roles fit, but scientific/secular roles complicate it.", "Institutional legibility is not the same as conventional morality.", "No focused evidence.", "Weak and internally contradictory fit.", "Items concern religion, propriety, parents, and conventional morality.", "Positive PC1 includes secular; negative PC1 includes spiritual and nostalgic, creating content-specific rather than general traditionalism effects.", "Most axis content remains.", "WEAK_OR_NONSPECIFIC", "DOWNGRADE as PC1 explanation."),
}


PC2 = {
    "IPIP100:B5:E": assessment(
        "higher -> positive PC2", "Covers extroverted and gregarious target-dominant positive markers plus accessible/socially outward context.", "Lower Extraversion coheres directly with strict negative `introverted`.", "Positive high-concentration experiential/practical/inquisitive are not inherently extraverted; negative high-concentration introverted is directly covered.", "Directly covers introverted and contextual extroverted/gregarious, but not abstract/theoretical/ritual markers.", "The full role-rating social-outward correlation with PC2 is only r=.066, so role evidence is weak despite marker symmetry.", "Opposite-pole completion makes Extraversion more coherent than the earlier pole-local mapping implied.", "Coordinate-blind social/outward ratings do not recover much of PC2.", "Strong fit for one interpersonal subaxis, not the whole axis.", "Items mix talkativeness, sociability, energy, assertiveness, and expression.", "High-PC2 developmental/immediate roles are not uniformly social; low-PC2 roles can be socially engaged caregivers, healers, or mediators.", "Experiential practicality and abstract/ritual world-modeling remain.", "PARTIAL_COMPONENT", "RETAIN and upgrade to explicit bipolar component, not whole-axis match."),
    "IPIPneo:E4:AL": assessment(
        "higher -> positive PC2", "Covers energetic, busy, fast-paced engagement.", "Lower Activity Level only weakly resembles pensive/solemn inwardness.", "No direct coverage of experiential/practical/inquisitive beyond behavioral immediacy.", "No strict-marker identity.", "Could fit active positive-PC2 roles, but many top PC2 roles are developmental/social rather than physically active.", "A plausible behavioral expression, not a prior core mapping.", "The coordinate-blind physical rating has r=.145, while this scale measures energy rather than bodily skill.", "Good activity definition, weak axis breadth.", "Items describe being always on the go, reacting quickly, and a fast pace; they do not measure exercise or athleticism.", "Conflates tempo with embodiment and misses abstract/theoretical negative content.", "Physical/manual engagement and conceptual mediation remain.", "PARTIAL_COMPONENT", "ADD as semantic neighbor; do not relabel as physicality."),
    "IPIPneo:E2:GR": assessment(
        "higher -> positive PC2", "Directly covers gregarious positive context.", "Lower Gregariousness coheres with introverted negative PC2.", "No coverage of the strict/high-concentration experiential/practical/inquisitive trio beyond social context.", "Covers one broader target-dominant positive marker and part of introverted inverse.", "Role-level social-outward ratings correlate weakly with PC2.", "Useful opposite-pole completion.", "No focused evidence beyond the role diagnostic.", "Good narrow social fit.", "Items focus groups, company, crowds, and social contact.", "Does not explain abstraction, ritual, theory, or hands-on practicality.", "Most axis content remains.", "PARTIAL_COMPONENT", "ADD as narrow Extraversion facet."),
    "BFAS:BFAS:E:E": assessment(
        "higher -> positive PC2", "Covers social warmth and energetic engagement.", "Lower Enthusiasm weakly fits solemn/pensive content.", "No direct high-concentration marker coverage.", "Only indirect marker fit.", "Role-level social-outward evidence is weak.", "Not previously central.", "No focused support.", "Narrow behavioral neighbor.", "Items combine social warmth and positive affect.", "Confounds valence with outward engagement.", "Practical/abstract contrast remains.", "WEAK_OR_NONSPECIFIC", "ADD only as peripheral social-affective facet."),
    "BFAS:BFAS:E:A": assessment(
        "higher -> positive PC2 only weakly", "Covers outward agency but not the cooperative/accessible positive markers specifically.", "Low Assertiveness is not equivalent to introversion or abstract contemplation.", "No high-concentration coverage.", "No strict marker match.", "Competitor has positive PC2 but assertiveness/dominance also loads PC3; role evidence is not axis-specific.", "Not a primary prior mapping.", "No focused support.", "Weak fit.", "Items cover leadership and speaking up.", "Confounded with PC3 dominance and PC1 professional roles.", "Nearly all PC2 content remains.", "WEAK_OR_NONSPECIFIC", "DO NOT PROMOTE."),
    "IPIPneo:E5:ES": assessment(
        "higher -> positive PC2 only weakly", "Covers stimulation and direct novelty.", "Lower Excitement Seeking could fit solemn/inward context.", "Does not directly cover experiential/practical/inquisitive; Qwen risk-taking was more PC1-negative than PC2-specific.", "No strict PC2 marker match.", "Daredevil is physically coded but does not alone define the continuum.", "Previously mapped to PC1 negative, showing cross-axis semantic ambiguity.", "Physical role coding is modest and sparse.", "Narrow sensation/risk neighbor.", "Items cover thrills, danger, crowds, reckless action, and adventure.", "Risk seeking is not physical engagement or practical experience.", "Abstract/ritual structure remains.", "WEAK_OR_NONSPECIFIC", "DOWNGRADE as PC2 analogue."),
    "IPIPneo:O4:AD": assessment(
        "higher -> positive PC2", "Covers new and direct experience by semantic proximity.", "Lower Adventurousness weakly fits ritual/traditional regularity.", "Partial coverage of experiential; not practical or inquisitive.", "Experiential is covered indirectly; Qwen adventurous itself is not strict PC2 and is strongly PC1-negative.", "Surfer/daredevil/nomad-like roles provide mixed evidence.", "Retain previous positive-PC2 partial mapping with stronger cross-loading caveat.", "Physicality is only a modest independent signal.", "Good for novelty preference, not concrete application.", "Items cover variety, novelty, travel, new foods, and change rather than bodily action.", "Cross-loads conceptually with PC1 expressive/open possibility.", "Practicality, inward abstraction, and ritual remain.", "PARTIAL_COMPONENT", "RETAIN but DOWNGRADE as evidence for embodiment."),
    "HEXACO:H:O:I": assessment(
        "higher -> positive PC2 by literal marker, with caution", "Directly covers inquisitive, a highly concentrated positive marker.", "Its inverse does not fit theoretical/abstract negative PC2; human inquisitiveness often accompanies those traits.", "Direct marker-name coverage of inquisitive only.", "Directly covers one of three strict positive markers.", "Inquiry roles span practical and theoretical regions.", "Retain prior mapping but expose its bipolar contradiction.", "Coordinate-blind abstraction is negatively related to PC2, making knowledge curiosity ambiguous.", "Good lexical fit to one marker, poor whole-axis fit.", "Items emphasize knowledge, reading, science, history, and learning.", "Human Inquisitiveness may align the negative abstract pole as much as the positive experiential pole.", "Practical action and introversion/ritual remain.", "PARTIAL_COMPONENT", "RETAIN as marker-level analogue only."),
    "BFAS:BFAS:O:I": assessment(
        "higher -> negative PC2", "Lower Intellect partly fits concrete/immediate engagement but not inquisitiveness.", "Directly covers theoretical, abstract, conceptual, erudite, and pensive content.", "Covers theoretical/abstract/conceptual highly concentrated negative markers.", "Covers a substantial strict-negative subfamily.", "Fits philosopher, theorist, scholar, physicist, and integrated-world-model roles.", "Strongly coherent with prior blinded abstraction evidence and PC1-conditioned results.", "Coordinate-blind abstract/conceptual ratings correlate r=-.322 with PC2, the strongest new dimension.", "Best single established construct for the negative abstract pole.", "Items emphasize abstract ideas, complex information, reasoning, and intellectual challenge.", "Low Intellect does not positively define practical/experiential inquiry; positive inquisitive is contradictory.", "Embodiment, social outwardness, ritual/reverence, and practical application remain.", "PLAUSIBLE_BIPOLAR_MATCH", "RETAIN as leading but incomplete human analogue."),
    "IPIP100:B5:O": assessment(
        "mixed; do not assign a single direction", "Contains experiential novelty and curiosity that could fit positive PC2.", "Contains intellect, imagination, aesthetics, and ideas that could fit negative PC2.", "Its subfacets point toward both poles.", "The broad domain conflates opposing PC2 content.", "Role evidence likewise separates practical immediacy from abstract world-modeling within openness-like roles.", "Broad Openness/Intellect is less useful than decomposed facets.", "New role ratings favor decomposing abstraction from direct experience.", "Poor unitary fit despite relevant content.", "Items mix ideas, imagination, aesthetics, curiosity, and novelty.", "The construct spans both sides of the proposed bipolar axis.", "No unique directional score is defensible.", "POOR_MATCH", "REPLACE with separate Intellect and experiential/novelty components."),
    "MPQ:MPQ:TR": assessment(
        "higher -> negative PC2", "Low Traditionalism weakly fits informal/direct engagement.", "Covers ritualistic, reverent, principled, and formalized negative content.", "Covers ritualistic/reverent/principled by semantic proximity.", "Covers a meaningful strict-negative subset.", "Fits traditionalist, purist, ascetic, and standards-bearing roles, but not theorist/philosopher alone.", "Retain prior partial mapping.", "Ritual/formal role ratings correlate r=-.255 with PC2.", "Good for conventional/ritual mediation, not abstraction broadly.", "Items emphasize conventional morality, religion, propriety, and traditional institutions.", "Ritual/formal mediation also includes secular institutional procedure and contemplation, which this construct misses.", "Theoretical abstraction, introversion, and positive practical experience remain.", "PARTIAL_COMPONENT", "RETAIN as ritual/conventional facet."),
    "HEXACO:H:A:FL": assessment(
        "higher -> positive PC2 only as interpersonal flexibility", "Covers accommodating/adaptable context.", "Low Flexibility does not map cleanly to ritual/formal mediation.", "No high-concentration coverage.", "No strict marker match.", "Some accessible social roles fit, but the axis role evidence is broader.", "Previous target-dominant mapping was facet-level.", "Social role correlation is weak.", "Construct concerns compromise, not cognitive flexibility or spontaneity.", "Items focus stubbornness, compromise, and interpersonal disagreement.", "Cannot serve as opposite of ritual/formality.", "Nearly all PC2 content remains.", "WEAK_OR_NONSPECIFIC", "DOWNGRADE; preserve semantic distinction."),
    "SPI_15impulsivity": assessment(
        "higher -> positive PC2", "Covers immediate, unplanned action in broad positive context.", "Lower Impulsivity partly fits principled, solemn, formalized negative content.", "No direct high-concentration marker coverage.", "No strict marker match; Qwen impulsive is associated but cross-loading.", "Fits developmental/reactive top-PC2 roles better than physicality, but not practical competence.", "Useful contextual component from broader mapping.", "Earlier conditional work tied high PC2 partly to developmental/reactive action.", "Relevant behavioral component, not axis identity.", "Items cover acting without thought and weak restraint.", "Positive PC2 also includes practical and inquisitive, which are not impulsive.", "Experiential competence and abstract/ritual content remain.", "PARTIAL_COMPONENT", "RETAIN as secondary developmental-immediacy component."),
    "MPQ:MPQ:CO": assessment(
        "higher -> negative PC2 weakly", "Low Control could fit immediate/reactive action.", "Higher Control fits principled/formal/deliberative negative content.", "No direct high-concentration coverage.", "Indirect fit to principled/solemn only.", "Mixed role coherence because procedural control also tracks PC1.", "Potential cross-axis confound.", "PC1 control is necessary in role diagnostics.", "Broad constraint neighbor.", "Items cover planning, caution, and impulse control.", "Strong PC1 relevance prevents clean PC2 interpretation.", "Abstraction and embodiment remain.", "WEAK_OR_NONSPECIFIC", "DO NOT use as primary PC2 analogue."),
    "SPI_15seriousness": assessment(
        "higher -> negative PC2", "Low Seriousness weakly fits casual positive context.", "Covers solemn/serious/earnest negative context.", "No direct high-concentration coverage except solemn proximity.", "Covers solemn and contextual serious.", "Some role coherence, but seriousness also tracks PC1 and affective register.", "Previously not a leading mapping.", "No focused evidence.", "Narrow register component.", "Items mix deliberation, restraint, seriousness, and non-frivolity.", "Does not explain theoretical abstraction or experience.", "Most axis content remains.", "PARTIAL_COMPONENT", "ADD as narrow register facet."),
    "MPQ:MPQ:AB": assessment(
        "higher -> negative PC2 only weakly", "Low Absorption does not define practical engagement.", "Higher Absorption can fit contemplative/mystical mediated experience.", "No direct high-concentration match.", "Indirectly covers pensive/reverent only.", "Mystic-like roles are low PC2, but absorption also maps strongly to PC1 negative.", "Cross-axis ambiguity is substantial.", "No new direct support.", "Narrow contemplative neighbor.", "Items cover fantasy, reflection, and aesthetic immersion.", "More clearly a PC1-negative imaginative component than a clean PC2 construct.", "Most PC2 content remains.", "WEAK_OR_NONSPECIFIC", "DO NOT PROMOTE."),
    "MPQ:MPQ:HA": assessment(
        "lower harm avoidance -> positive PC2 only weakly", "Risk tolerance can accompany direct experience.", "Higher Harm Avoidance does not cover abstract/theoretical negative PC2.", "No high-concentration marker coverage.", "No strict marker match.", "Daredevil/surfer-like examples are insufficient and counterexamples are numerous.", "Not a prior core mapping.", "Physicality association is modest and independent of risk only incompletely.", "Poor physicality substitute.", "Items concern dangerous activities and risk avoidance.", "Risk appetite is distinct from bodily engagement and practical action.", "Nearly all axis content remains.", "POOR_MATCH", "DO NOT relabel as physicality."),
    "HEXACO:H:E:F": assessment(
        "lower fearfulness -> positive PC2 only weakly", "Low fear may permit physical action.", "High fear does not explain abstraction/ritual.", "No marker coverage.", "No strict marker match.", "Physical roles can be courageous, but infant/toddler are high PC2 without low fear being the axis.", "Not a prior mapping.", "New physical rating cannot validate fearlessness.", "Poor match.", "Items concern injury, danger, pain, and courage.", "Physical danger sensitivity is not athleticism or embodiment.", "Nearly all PC2 content remains.", "POOR_MATCH", "DO NOT relabel as physicality."),
    "PS:PS:P": assessment(
        "higher -> positive PC2 only ambiguously", "Combines extraverted engagement and novelty.", "Its Openness/Intellect component can point toward negative PC2 abstraction.", "No clean concentration coverage because components split across poles.", "No strict one-to-one match.", "Broad exploratory roles occupy both sides.", "Previous mapping treated Plasticity as partial.", "Role diagnostics favor decomposition.", "Metatrait too broad for this axis.", "Items mix social agency, novelty, and ideas.", "Contains opposing PC2 ingredients.", "Cannot distinguish experience from abstraction.", "POOR_MATCH", "REPLACE with decomposed facets."),
}


def default_screen(axis: str, row: dict) -> dict:
    return {
        "proposed_measurement_direction": "not proposed",
        "positive_pole_marker_coverage": "No material coverage after full-library screen.",
        "negative_pole_inverse_coherence": "No material opposite-pole coherence after full-library screen.",
        "highly_concentrated_marker_coverage": "none identified",
        "strict_axis_specific_marker_coverage": "none identified",
        "role_persona_coherence": "Not a serious candidate for this axis.",
        "prior_model_side_interpretation_coherence": "Not used for interpretation selection.",
        "focused_activation_or_role_rating_coherence": "Not applicable.",
        "human_construct_definition_fit": f"The documented {row['construct_name']} definition does not capture the central bipolar evidence for {axis}.",
        "human_item_content_fit": "No item audit signal sufficient to elevate this construct.",
        "important_contradictions": "Outside the principal candidate set.",
        "model_specific_residual_content": "The central axis content remains unmeasured.",
        "overall_match": "WEAK_OR_NONSPECIFIC",
        "previous_mapping_disposition": "SCREENED_NOT_SELECTED",
    }


def construct_outputs(library: list[dict], axis: str, decisions: dict[str, dict]) -> tuple[list[dict], list[dict]]:
    reconsideration, serious = [], []
    for row in library:
        decision = decisions.get(row["construct_id"])
        out = {
            "axis": axis,
            "construct_id": row["construct_id"],
            "construct_name": row["construct_name"],
            "framework": row["framework"],
            "domain": row["domain"],
            "construct_level": row["construct_level"],
            "construct_definition": row["construct_definition"],
            "sapa_availability": row["sapa_availability"],
            "item_ids": row["item_ids"],
            "item_count": row["scored_item_count"],
            "reliability": row["sapa_pairwise_standardized_alpha"],
            "candidate_universe": "FULL_126_CONSTRUCT_LIBRARY",
            "serious_candidate": bool(decision),
        }
        out.update(decision or default_screen(axis, row))
        reconsideration.append(out)
        if decision:
            serious.append(out.copy())
    serious.append({
        "axis": axis,
        "construct_id": "NO_DIRECT_HUMAN_MEASURE",
        "construct_name": f"No single SAPA construct captures the whole {axis} axis",
        "framework": "AA-8 synthesis",
        "domain": "model-specific residual",
        "construct_level": "axis-level conclusion",
        "construct_definition": "The bipolar Qwen axis requires a hierarchy of partial human analogues and retains model-specific content.",
        "sapa_availability": "no",
        "item_ids": "",
        "item_count": 0,
        "reliability": "",
        "candidate_universe": "FULL_126_CONSTRUCT_LIBRARY",
        "serious_candidate": True,
        "proposed_measurement_direction": "not scoreable as one construct",
        "positive_pole_marker_coverage": "Requires several facets.",
        "negative_pole_inverse_coherence": "Requires several facets.",
        "highly_concentrated_marker_coverage": "No single library entry covers both poles.",
        "strict_axis_specific_marker_coverage": "No single library entry covers both poles.",
        "role_persona_coherence": "Compound interpretation fits role evidence better than a single human trait.",
        "prior_model_side_interpretation_coherence": "Consistent with the model-side evidence hierarchy.",
        "focused_activation_or_role_rating_coherence": "Consistent with bounded diagnostics.",
        "human_construct_definition_fit": "No direct construct definition exists.",
        "human_item_content_fit": "No single validated scale has the required content breadth.",
        "important_contradictions": "A compound is less parsimonious but avoids false equivalence.",
        "model_specific_residual_content": "Substantial and explicitly retained.",
        "overall_match": "NO_DIRECT_HUMAN_MEASURE",
        "previous_mapping_disposition": "FINAL_AXIS_LEVEL_CONCLUSION",
    })
    return reconsideration, serious


PC1_ITEM_RE = re.compile(r"\b(rule|rules|duty|duties|obligation|standard|standards|correct|correctly|check|checking|accuracy|accurate|mistake|mistakes|procedure|procedures|authority|order|organized|plan|plans|careful|thorough|detail|discipline|responsib|dependab|perfection|schedule|routine|ethical|moral|follow)\b", re.I)


def pc1_item_audit(items: list[dict], item_to_constructs: dict[str, list[str]]) -> list[dict]:
    out = []
    for row in items:
        text = row["item_text"]
        if not PC1_ITEM_RE.search(text):
            continue
        low = text.lower()
        if "in order to impress" in low or "obstruct others' plans" in low:
            theme, status = "incidental wording", "NOT_RELEVANT_HOMONYM"
        elif re.search(r"\b(rule|rules|authority)\b", low):
            theme, status = "rules and authority", "ITEM_LEVEL_EVIDENCE_ONLY"
        elif re.search(r"\b(dut|obligation)", low):
            theme, status = "duties and obligations", "ITEM_LEVEL_EVIDENCE_ONLY"
        elif re.search(r"\b(mistake|accur|detail|check)", low):
            theme, status = "accuracy and error control", "ITEM_LEVEL_EVIDENCE_ONLY"
        elif re.search(r"\b(standard|correct)", low):
            theme, status = "standards and correctness", "ITEM_LEVEL_EVIDENCE_ONLY"
        elif re.search(r"\b(plan|order|schedule|routine)", low):
            theme, status = "planning and order", "SEMANTIC_NEIGHBOR"
        else:
            theme, status = "general responsibility or morality", "SEMANTIC_NEIGHBOR"
        out.append({
            "item_id": row["item_id"], "item_text": text, "audit_theme": theme,
            "evidence_status": status, "constructs_containing_item": ";".join(item_to_constructs.get(row["item_id"], [])),
            "source_scale_memberships": row["source_scale_memberships"], "valid_response_n": row["valid_response_n"],
            "interpretive_note": "Item-level content only; never treated as a validated standalone construct.",
        })
    return out


PC2_CONSTRUCT_IDS = {
    "IPIP100:B5:E", "EPQr:EPQ:E", "HEXACO_X", "NEO_E", "QB6:QB6:X", "SPI_5extraversion",
    "IPIPneo:E4:AL", "IPIPneo:E2:GR", "BFAS:BFAS:E:E", "BFAS:BFAS:E:A", "IPIPneo:E1:FR",
    "IPIPneo:E5:ES", "IPIPneo:O4:AD", "HEXACO:H:O:I", "BFAS:BFAS:O:I", "IPIPneo:O5:IN",
    "MPQ:MPQ:HA", "HEXACO:H:E:F", "SPI_15impulsivity", "PS:PS:P",
}


def pc2_item_audit(items: list[dict], library: list[dict], item_to_constructs: dict[str, list[str]]) -> list[dict]:
    candidate_ids = set()
    for row in library:
        if row["construct_id"] in PC2_CONSTRUCT_IDS:
            candidate_ids.update(x for x in row["item_ids"].split(";") if x)
    physical_words = re.compile(r"\b(physical|exercise|athlet|sport|bodily|manual|dance|swim|run|walk|hike|work out)\b", re.I)
    item_map = {r["item_id"]: r for r in items}
    out = []
    for item_id in sorted(candidate_ids, key=lambda x: int(x.split("_")[1])):
        row = item_map[item_id]
        text = row["item_text"]
        constructs = item_to_constructs.get(item_id, [])
        joined = ";".join(constructs)
        if item_id == "q_53":
            status, theme = "PHYSICAL_DANGER_NEIGHBOR", "fear of physical danger"
        elif item_id == "q_608":
            status, theme = "AESTHETIC_SPECTATORSHIP_NOT_PHYSICALITY", "watching dance"
        elif item_id == "q_1761":
            status, theme = "METAPHOR_NOT_PHYSICALITY", "figurative swimming"
        elif physical_words.search(text):
            status, theme = "POTENTIAL_DIRECT_ITEM_LEVEL_EVIDENCE", "explicit bodily or physical wording"
        elif "Activity Level" in joined:
            status, theme = "ACTIVITY_ENERGY_NEIGHBOR", "energy, busyness, or tempo"
        elif any(x in joined for x in ["Excitement Seeking", "Adventurousness", "Harm Avoidance", "Fearfulness"]):
            status, theme = "RISK_ADVENTURE_NEIGHBOR", "risk, novelty, or danger"
        elif "Inquisitiveness" in joined or "Intellect" in joined:
            status, theme = "KNOWLEDGE_INQUIRY_NEIGHBOR", "learning or conceptual inquiry"
        else:
            status, theme = "SOCIAL_OUTWARD_NEIGHBOR", "social engagement, energy, or expression"
        out.append({
            "item_id": item_id, "item_text": text, "audit_theme": theme, "physicality_status": status,
            "constructs_containing_item": joined, "source_scale_memberships": row["source_scale_memberships"],
            "valid_response_n": row["valid_response_n"],
            "interpretive_note": "No direct athleticism/physical-activity construct is inferred from this item; single items remain item-level evidence only.",
        })
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--item-dictionary", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    repo, outdir = args.repo.resolve(), args.output_dir.resolve()
    item_path = args.item_dictionary.resolve()
    library = git_csv(repo, SOURCE_COMMIT, LIBRARY_PATH)
    with item_path.open(newline="", encoding="utf-8") as fh:
        items = list(csv.DictReader(fh))
    if len(library) != 126 or len(items) != 696:
        raise ValueError(f"Expected 126 constructs and 696 items, found {len(library)} and {len(items)}")
    item_to_constructs: dict[str, list[str]] = {}
    for row in library:
        for item in filter(None, row["item_ids"].split(";")):
            item_to_constructs.setdefault(item, []).append(f"{row['construct_id']}:{row['construct_name']}")

    pc1_all, pc1_serious = construct_outputs(library, "PC1", PC1)
    pc2_all, pc2_serious = construct_outputs(library, "PC2", PC2)
    write_csv(outdir / "pc1_sapa_construct_reconsideration.csv", pc1_all)
    write_csv(outdir / "pc2_sapa_construct_reconsideration.csv", pc2_all)
    write_csv(outdir / "pc1_bipolar_human_mapping.csv", pc1_serious)
    write_csv(outdir / "pc2_bipolar_human_mapping.csv", pc2_serious)
    write_csv(outdir / "pc1_rule_procedure_item_audit.csv", pc1_item_audit(items, item_to_constructs))
    write_csv(outdir / "pc2_physicality_activity_item_audit.csv", pc2_item_audit(items, library, item_to_constructs))


if __name__ == "__main__":
    main()
