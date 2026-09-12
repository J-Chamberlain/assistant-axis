#!/usr/bin/env python3
"""Freeze geometry-blind Big Five mappings from external taxonomy and SAPA review.

This stage must run before any PCA association code. It reads only canonical
trait definitions, the reviewed SAPA bridge, and predeclared IPIP taxonomy
metadata. It deliberately contains no geometry, coordinate, or score loader.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TRAITS_PATH = ROOT / "data/traits/trait_list.json"
BRIDGE_PATH = ROOT / (
    "research/outputs/human_trait_dataset_feasibility/sapa_review/"
    "sapa_trait_bridge_provisional_v1.csv"
)
FREEZE_TIMESTAMP = "2026-09-11T22:58:36Z"
DOMAINS = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# Facet names follow the public-domain IPIP-NEO keys. Definitions are concise
# project paraphrases, not reproduced proprietary NEO PI-R item content.
FACETS = [
    ("neuroticism", "N1", "Anxiety", "Tendency toward worry, fear, and tension."),
    ("neuroticism", "N2", "Anger", "Proneness to irritation, anger, and frustration."),
    ("neuroticism", "N3", "Depression", "Proneness to sadness, hopelessness, and low mood."),
    ("neuroticism", "N4", "Self-Consciousness", "Sensitivity to social evaluation and embarrassment."),
    ("neuroticism", "N5", "Immoderation", "Difficulty resisting urges and immediate gratification."),
    ("neuroticism", "N6", "Vulnerability", "Difficulty remaining composed and effective under stress."),
    ("extraversion", "E1", "Friendliness", "Warmth and ease in approaching other people."),
    ("extraversion", "E2", "Gregariousness", "Preference for company and social interaction."),
    ("extraversion", "E3", "Assertiveness", "Readiness to speak up, lead, and influence others."),
    ("extraversion", "E4", "Activity Level", "Energetic, busy, and fast-paced engagement."),
    ("extraversion", "E5", "Excitement-Seeking", "Preference for stimulation, risk, and excitement."),
    ("extraversion", "E6", "Cheerfulness", "Proneness to positive affect, fun, and enthusiasm."),
    ("openness", "O1", "Imagination", "Rich fantasy, imagery, and imaginative ideation."),
    ("openness", "O2", "Artistic Interests", "Appreciation of art, beauty, and aesthetic experience."),
    ("openness", "O3", "Emotionality", "Awareness of and receptivity to emotional experience."),
    ("openness", "O4", "Adventurousness", "Preference for novelty, variety, and new experience."),
    ("openness", "O5", "Intellect", "Enjoyment of ideas, complexity, inquiry, and abstract thought."),
    ("openness", "O6", "Liberalism", "Readiness to reconsider convention, authority, and established values."),
    ("agreeableness", "A1", "Trust", "Expectation that other people are honest and well intentioned."),
    ("agreeableness", "A2", "Morality", "Straightforward, sincere, and non-manipulative conduct."),
    ("agreeableness", "A3", "Altruism", "Active concern for and willingness to help others."),
    ("agreeableness", "A4", "Cooperation", "Preference for compromise and harmony over conflict."),
    ("agreeableness", "A5", "Modesty", "Low self-aggrandizement and absence of superiority claims."),
    ("agreeableness", "A6", "Sympathy", "Compassion and concern for others' suffering."),
    ("conscientiousness", "C1", "Self-Efficacy", "Confidence in one's ability to accomplish tasks."),
    ("conscientiousness", "C2", "Orderliness", "Preference for organization, planning, and structure."),
    ("conscientiousness", "C3", "Dutifulness", "Commitment to obligations, rules, and reliability."),
    ("conscientiousness", "C4", "Achievement-Striving", "Drive to attain demanding goals and high standards."),
    ("conscientiousness", "C5", "Self-Discipline", "Persistence and follow-through despite distraction."),
    ("conscientiousness", "C6", "Cautiousness", "Deliberation before acting and avoidance of rash choices."),
]
FACET_BY_CODE = {code: (domain, name, definition) for domain, code, name, definition in FACETS}


# Geometry-blind adjudication of reviewed SAPA links. ACCEPT_DIRECT rows enter A;
# ACCEPT_CLOSE rows enter B only. Several reviewed traits are intentionally left
# out because their response-style definition is not a defensible Big Five facet.
HUMAN_MAPPING = {
    "pessimistic": ("neuroticism", "N1", "positive", "Dark outlook and expecting the worst indicate anxiety-prone negative anticipation."),
    "empathetic": ("agreeableness", "A6", "positive", "Direct compassion and emotional understanding match Sympathy."),
    "anxious": ("neuroticism", "N1", "positive", "Worry and nervous anticipation directly match Anxiety."),
    "patient": ("agreeableness", "A4", "positive", "Patience supports non-hostile accommodation and Cooperation."),
    "artistic": ("openness", "O2", "positive", "Art appreciation and creative expression directly match Artistic Interests."),
    "creative": ("openness", "O1", "positive", "Original, imaginative ideation directly matches Imagination."),
    "resilient": ("neuroticism", "N6", "negative", "Rapid recovery and stability under pressure are the low-Vulnerability pole."),
    "forgiving": ("agreeableness", "A4", "positive", "Releasing grudges and pardoning errors support Cooperation."),
    "judgmental": ("agreeableness", "A4", "negative", "Harsh interpersonal judgment opposes cooperative accommodation."),
    "traditional": ("openness", "O6", "negative", "Attachment to convention is the low-Liberalism pole in the IPIP terminology."),
    "perfectionist": ("conscientiousness", "C4", "positive", "High standards and flawless completion match Achievement-Striving."),
    "conscientious": ("conscientiousness", "C5", "positive", "Responsibility, detail, and plan completion support Self-Discipline."),
    "adventurous": ("extraversion", "E5", "positive", "Seeking adventure and stimulation directly matches Excitement-Seeking."),
    "secular": ("openness", "O6", "positive", "Questioning conventional religious commitment maps to the IPIP Liberalism/value-openness facet."),
    "temperamental": ("neuroticism", "N3", "positive", "Mood instability is carried by the reviewed IPIP-NEO negative-affect evidence."),
    "serene": ("neuroticism", "N6", "negative", "Calm composure under pressure is the low-Vulnerability pole."),
    "stoic": ("neuroticism", "N6", "negative", "Emotional control under pressure is the low-Vulnerability pole."),
    "callous": ("agreeableness", "A6", "negative", "Indifference to feelings and suffering directly opposes Sympathy."),
    "altruistic": ("agreeableness", "A3", "positive", "Helping and charitable concern directly match Altruism."),
    "paranoid": ("agreeableness", "A1", "negative", "Suspicion and distrust directly oppose Trust."),
    "curious": ("openness", "O5", "positive", "Interest in learning and ideas supports Intellect."),
    "impulsive": ("conscientiousness", "C6", "negative", "Acting without considering consequences is the low-Cautiousness pole."),
    "neurotic": ("neuroticism", "N1", "positive", "Persistent anxiety and negative emotionality directly indicate Neuroticism."),
    "meticulous": ("conscientiousness", "C2", "positive", "Detail control and precision support Orderliness."),
    "introspective": ("openness", "O1", "positive", "Inner reflection and getting lost in thought support Imagination."),
    "innovative": ("openness", "O5", "positive", "New ideas and original approaches support Intellect."),
    "assertive": ("extraversion", "E3", "positive", "Taking charge and advocating positions directly match Assertiveness."),
    "agreeable": ("agreeableness", "A4", "positive", "Harmony and cooperation directly match Cooperation."),
    "manipulative": ("agreeableness", "A2", "negative", "Deception and exploitation directly oppose Morality."),
    "melancholic": ("neuroticism", "N3", "positive", "Persistent sadness and hopelessness directly match Depression."),
    "playful": ("extraversion", "E6", "positive", "Fun, joking, and lightheartedness directly match Cheerfulness."),
    "calm": ("neuroticism", "N6", "negative", "Composure under tension is the low-Vulnerability pole."),
    "extroverted": ("extraversion", "E2", "positive", "Starting conversations and seeking company directly match Gregariousness."),
    "bitter": ("agreeableness", "A4", "negative", "Grudges and revenge oppose Cooperation."),
    "emotional": ("openness", "O3", "positive", "Awareness and expression of feelings directly match Emotionality."),
    "dominant": ("extraversion", "E3", "positive", "Taking charge directly matches Assertiveness."),
    "reserved": ("extraversion", "E2", "negative", "Limited disclosure and social initiation indicate low Gregariousness."),
    "cynical": ("agreeableness", "A1", "negative", "Distrust of human motives directly opposes Trust."),
    "grandiose": ("agreeableness", "A5", "negative", "Inflated self-importance directly opposes Modesty."),
    "optimistic": ("extraversion", "E6", "positive", "Positive outlook and hope directly support Cheerfulness."),
    "vindictive": ("agreeableness", "A4", "negative", "Revenge and persistent grudges directly oppose Cooperation."),
    "gregarious": ("extraversion", "E2", "positive", "Seeking company and social interaction directly match Gregariousness."),
    # ACCEPT_CLOSE: sensitivity tier only.
    "risk_taking": ("extraversion", "E5", "positive", "Personal risk propensity is a close proxy for Excitement-Seeking."),
    "detached": ("openness", "O3", "negative", "Low emotional engagement is a close proxy for low Emotionality."),
    "intuitive": ("openness", "O5", "positive", "Holistic insight is a close proxy for idea-oriented Intellect."),
    "methodical": ("conscientiousness", "C2", "positive", "Planful stepwise work is a close proxy for Orderliness."),
    "mercurial": ("neuroticism", "N3", "positive", "Frequent mood shifts are a close negative-affect proxy."),
    "zealous": ("openness", "O3", "positive", "Passionate investment is a close proxy for Emotionality."),
    "cruel": ("agreeableness", "A6", "negative", "Indifference to suffering is a close low-Sympathy proxy."),
    "acerbic": ("agreeableness", "A4", "negative", "A sharp, harsh tongue is a close low-Cooperation proxy."),
    "naive": ("agreeableness", "A1", "positive", "Assuming good intentions is a close high-Trust proxy."),
    "goofy": ("extraversion", "E6", "positive", "Joking and playful foolishness are a close Cheerfulness proxy."),
    "adaptable": ("openness", "O4", "positive", "Ease with change is a close Adventurousness/novelty proxy."),
    "confident": ("conscientiousness", "C1", "positive", "Self-assurance is a close proxy for Self-Efficacy."),
    "bombastic": ("agreeableness", "A5", "negative", "Pompous self-display is a close low-Modesty proxy."),
    "avoidant": ("extraversion", "E1", "negative", "Withdrawal and approach difficulty are a close low-Friendliness proxy."),
    "disorganized": ("conscientiousness", "C2", "negative", "Mess and poor detail placement are a close low-Orderliness proxy."),
    "cautious": ("conscientiousness", "C6", "positive", "Risk avoidance and deliberation are a close Cautiousness proxy."),
    "nonchalant": ("neuroticism", "N1", "negative", "Relaxed unconcern is a close low-Anxiety proxy."),
    "passionate": ("openness", "O3", "positive", "Strong felt investment is a close Emotionality proxy."),
    "deferential": ("agreeableness", "A5", "positive", "Yielding status claims is a close Modesty proxy."),
    "competitive": ("agreeableness", "A4", "negative", "Prioritizing winning over cooperation is a close low-Cooperation proxy."),
    "hostile": ("agreeableness", "A4", "negative", "Aggressive antagonism is a close low-Cooperation proxy."),
    "proactive": ("conscientiousness", "C4", "positive", "Turning plans into action is a close Achievement-Striving proxy."),
    "submissive": ("extraversion", "E3", "negative", "Avoiding assertion is a close low-Assertiveness proxy."),
    "spontaneous": ("conscientiousness", "C6", "negative", "Spur-of-the-moment decisions are a close low-Cautiousness proxy."),
    "chill": ("neuroticism", "N1", "negative", "Relaxed affect is a close low-Anxiety proxy."),
}


def m(domain: str, facet: str, polarity: str, confidence: str, relation: str, rationale: str):
    return domain, facet, polarity, confidence, relation, rationale


# Full-inventory mapping frozen from labels/definitions and the IPIP facet
# definitions above. Omitted traits are intentionally unmapped.
EXPANDED_MAPPING = {
    # Openness / Intellect
    "innovative": m("openness", "O5", "positive", "high", "direct", "Explicit pursuit of new ideas and methods."),
    "adventurous": m("openness", "O4", "positive", "high", "direct", "Explicit pursuit of novel experiences."),
    "creative": m("openness", "O1", "positive", "high", "direct", "Explicit imaginative originality."),
    "philosophical": m("openness", "O5", "positive", "high", "direct", "Abstract engagement with ideas and meaning."),
    "curious": m("openness", "O5", "positive", "high", "direct", "Explicit intellectual curiosity."),
    "inquisitive": m("openness", "O5", "positive", "high", "direct", "Probing inquiry and desire to understand."),
    "artistic": m("openness", "O2", "positive", "high", "direct", "Explicit aesthetic and artistic interest."),
    "futuristic": m("openness", "O5", "positive", "medium", "proxy", "Future-oriented novelty is an idea-openness proxy."),
    "introspective": m("openness", "O1", "positive", "medium", "proxy", "Inner reflection supports imaginative mental life."),
    "eclectic": m("openness", "O4", "positive", "high", "direct", "Preference for varied sources and perspectives."),
    "irreverent": m("openness", "O6", "positive", "medium", "proxy", "Disregard for convention is a value-openness proxy."),
    "theoretical": m("openness", "O5", "positive", "high", "direct", "Explicit preference for theories and concepts."),
    "metaphorical": m("openness", "O1", "positive", "high", "direct", "Figurative and symbolic imagination."),
    "exploratory": m("openness", "O4", "positive", "high", "direct", "Explicit investigation of multiple options."),
    "speculative": m("openness", "O1", "positive", "medium", "proxy", "Conjectural possibility generation."),
    "progressive": m("openness", "O6", "positive", "medium", "proxy", "Advocacy of change over convention."),
    "interdisciplinary": m("openness", "O5", "positive", "high", "direct", "Connecting ideas across fields."),
    "holistic": m("openness", "O5", "positive", "medium", "proxy", "Integrative complex-systems thinking."),
    "contrarian": m("openness", "O6", "positive", "medium", "proxy", "Challenges established opinion."),
    "socratic": m("openness", "O5", "positive", "medium", "proxy", "Inquiry through questions."),
    "narrative": m("openness", "O1", "positive", "medium", "proxy", "Story construction draws on imagination."),
    "abstract": m("openness", "O5", "positive", "high", "direct", "Explicit abstract conceptual thought."),
    "open_ended": m("openness", "O4", "positive", "high", "direct", "Comfort with ambiguity and alternatives."),
    "improvisational": m("openness", "O4", "positive", "medium", "proxy", "Unscripted adaptation implies novelty preference."),
    "conceptual": m("openness", "O5", "positive", "high", "direct", "Explicit idea- and framework-oriented thought."),
    "divergent": m("openness", "O1", "positive", "high", "direct", "Generates many novel possibilities."),
    "constructivist": m("openness", "O6", "positive", "medium", "proxy", "Allows nontraditional contextual accounts of truth."),
    "paradoxical": m("openness", "O5", "positive", "medium", "proxy", "Tolerates conceptual contradiction and complexity."),
    "whimsical": m("openness", "O1", "positive", "high", "direct", "Fanciful imaginative play."),
    "poetic": m("openness", "O2", "positive", "high", "direct", "Explicit aesthetic language and imagery."),
    "pensive": m("openness", "O1", "positive", "medium", "proxy", "Deep reflective inner thought."),
    "iconoclastic": m("openness", "O6", "positive", "high", "direct", "Explicit attack on cherished convention."),
    "secular": m("openness", "O6", "positive", "medium", "proxy", "Nontraditional value orientation in the reviewed IPIP framing."),
    "pluralist": m("openness", "O6", "positive", "high", "direct", "Acceptance of multiple valid perspectives."),
    "romantic": m("openness", "O1", "positive", "high", "direct", "Prioritizes imagination and idealized experience."),
    "mystical": m("openness", "O1", "positive", "medium", "proxy", "Receptivity to ineffable imaginative experience."),
    "systems_thinker": m("openness", "O5", "positive", "high", "direct", "Complex interconnection and emergence reasoning."),
    "structuralist": m("openness", "O5", "positive", "high", "direct", "Abstract analysis of organizing patterns."),
    "deconstructionist": m("openness", "O5", "positive", "medium", "proxy", "Reconsiders assumptions and conceptual structures."),
    "critical": m("openness", "O6", "positive", "medium", "proxy", "Questions accepted narratives and power structures."),
    "rebellious": m("openness", "O6", "positive", "high", "direct", "Explicit challenge to authority and norms."),
    "big_picture": m("openness", "O5", "positive", "medium", "proxy", "Broad conceptual synthesis."),
    "emotional": m("openness", "O3", "positive", "high", "direct", "Explicit engagement with emotional experience."),
    "passionate": m("openness", "O3", "positive", "medium", "proxy", "Strong felt investment."),
    "zealous": m("openness", "O3", "positive", "medium", "proxy", "Fervent emotional investment."),
    "intuitive": m("openness", "O5", "positive", "medium", "proxy", "Holistic pattern recognition."),
    "adaptable": m("openness", "O4", "positive", "medium", "proxy", "Comfort with change and novelty."),
    "traditional": m("openness", "O6", "negative", "high", "direct", "Explicit preference for convention."),
    "practical": m("openness", "O5", "negative", "medium", "proxy", "Concrete application over theory is a low-Intellect proxy."),
    "literal": m("openness", "O1", "negative", "high", "direct", "Explicit focus on literal rather than imaginative meaning."),
    "closure_seeking": m("openness", "O4", "negative", "high", "direct", "Preference for closure over ambiguity."),
    "convergent": m("openness", "O1", "negative", "high", "direct", "Narrows possibilities rather than generating them."),
    "essentialist": m("openness", "O6", "negative", "medium", "proxy", "Fixed essences are a rigidity proxy."),
    "formalist": m("openness", "O4", "negative", "medium", "proxy", "Prioritizes fixed form over flexible content."),
    "dogmatic": m("openness", "O6", "negative", "high", "direct", "Rigid adherence despite alternatives."),
    "fundamentalist": m("openness", "O6", "negative", "high", "direct", "Explicit uncompromising adherence."),
    "ritualistic": m("openness", "O4", "negative", "medium", "proxy", "Preference for established procedure and ceremony."),
    "absolutist": m("openness", "O6", "negative", "medium", "proxy", "Rejects contextual alternatives."),
    "detached": m("openness", "O3", "negative", "medium", "proxy", "Emotional distance is a low-Emotionality proxy."),
    "grounded": m("openness", "O1", "negative", "medium", "proxy", "Concrete reality focus is a low-Imagination proxy."),
    "dispassionate": m("openness", "O3", "negative", "high", "direct", "Explicit emotional distance."),
    # Conscientiousness
    "efficient": m("conscientiousness", "C1", "positive", "medium", "proxy", "Effective task completion."),
    "serious": m("conscientiousness", "C3", "positive", "medium", "proxy", "Substantive, non-frivolous task stance."),
    "circumspect": m("conscientiousness", "C6", "positive", "high", "direct", "Careful deliberation before response."),
    "principled": m("conscientiousness", "C3", "positive", "high", "direct", "Consistent duty to rules and values."),
    "cautious": m("conscientiousness", "C6", "positive", "high", "direct", "Explicit risk deliberation."),
    "methodical": m("conscientiousness", "C2", "positive", "high", "direct", "Systematic plan and order."),
    "perfectionist": m("conscientiousness", "C4", "positive", "high", "direct", "Demanding standards and flawless achievement."),
    "decisive": m("conscientiousness", "C1", "positive", "medium", "proxy", "Confidence in producing task decisions."),
    "problem_solving": m("conscientiousness", "C1", "positive", "high", "direct", "Task competence and solution production."),
    "data_driven": m("conscientiousness", "C3", "positive", "medium", "proxy", "Evidence discipline and procedural reliability."),
    "conscientious": m("conscientiousness", "C3", "positive", "high", "direct", "Explicit responsibility and thoroughness."),
    "strategic": m("conscientiousness", "C4", "positive", "medium", "proxy", "Goal-directed planning."),
    "regulatory": m("conscientiousness", "C3", "positive", "high", "direct", "Rules, standards, and compliance."),
    "proactive": m("conscientiousness", "C4", "positive", "high", "direct", "Anticipatory goal pursuit."),
    "prescriptive": m("conscientiousness", "C3", "positive", "medium", "proxy", "Rule and guideline orientation."),
    "meticulous": m("conscientiousness", "C2", "positive", "high", "direct", "Precision and detail order."),
    "calculating": m("conscientiousness", "C4", "positive", "medium", "proxy", "Strategic planning toward outcomes."),
    "ascetic": m("conscientiousness", "C5", "positive", "medium", "proxy", "Explicit self-denial and discipline."),
    "pedantic": m("conscientiousness", "C2", "positive", "medium", "proxy", "Excessive detail and formal order."),
    "impatient": m("conscientiousness", "C5", "negative", "high", "direct", "Low persistence for detailed work."),
    "disorganized": m("conscientiousness", "C2", "negative", "high", "direct", "Explicit lack of order."),
    "spontaneous": m("conscientiousness", "C6", "negative", "high", "direct", "Unplanned immediate action."),
    "reactive": m("conscientiousness", "C4", "negative", "medium", "proxy", "Responds after events rather than pursuing plans."),
    "flippant": m("conscientiousness", "C3", "negative", "medium", "proxy", "Casual disregard for seriousness and duty."),
    "nonchalant": m("conscientiousness", "C3", "negative", "medium", "proxy", "Unconcern about outcomes."),
    "hedonistic": m("conscientiousness", "C5", "negative", "medium", "proxy", "Immediate gratification over discipline."),
    "impulsive": m("conscientiousness", "C6", "negative", "high", "direct", "Acts without deliberation."),
    "chaotic": m("conscientiousness", "C2", "negative", "medium", "proxy", "Explicit disorder and unpredictability."),
    "risk_taking": m("conscientiousness", "C6", "negative", "high", "direct", "Embraces risk rather than deliberative caution."),
    # Extraversion
    "dramatic": m("extraversion", "E6", "positive", "medium", "proxy", "Expressive high-intensity presentation."),
    "charismatic": m("extraversion", "E1", "positive", "high", "direct", "Warm social magnetism."),
    "verbose": m("extraversion", "E2", "positive", "medium", "proxy", "Talkativeness proxy."),
    "witty": m("extraversion", "E6", "positive", "high", "direct", "Humorous positive social expression."),
    "confident": m("extraversion", "E3", "positive", "high", "direct", "Social certainty and forcefulness."),
    "assertive": m("extraversion", "E3", "positive", "high", "direct", "Explicit advocacy and position-taking."),
    "entertaining": m("extraversion", "E6", "positive", "high", "direct", "Fun and engaging positive affect."),
    "inspirational": m("extraversion", "E6", "positive", "medium", "proxy", "Positive energizing expression."),
    "extroverted": m("extraversion", "E2", "positive", "high", "direct", "Explicit social engagement."),
    "dominant": m("extraversion", "E3", "positive", "high", "direct", "Taking charge."),
    "urgent": m("extraversion", "E4", "positive", "medium", "proxy", "Fast-paced action orientation."),
    "playful": m("extraversion", "E6", "positive", "high", "direct", "Fun and lightheartedness."),
    "animated": m("extraversion", "E4", "positive", "high", "direct", "Energetic dynamic expression."),
    "effusive": m("extraversion", "E4", "positive", "high", "direct", "Overflowing energetic expression."),
    "gregarious": m("extraversion", "E2", "positive", "high", "direct", "Explicit sociability."),
    "optimistic": m("extraversion", "E6", "positive", "high", "direct", "Positive affect and hope."),
    "goofy": m("extraversion", "E6", "positive", "medium", "proxy", "Playful joking."),
    "flirty": m("extraversion", "E1", "positive", "medium", "proxy", "Social approach and charm."),
    "sassy": m("extraversion", "E3", "positive", "medium", "proxy", "Bold social expression."),
    "mischievous": m("extraversion", "E5", "positive", "medium", "proxy", "Stimulation-seeking playful trouble."),
    "theatrical": m("extraversion", "E6", "positive", "medium", "proxy", "Performative expressive enthusiasm."),
    "introverted": m("extraversion", "E2", "negative", "high", "direct", "Explicit low social breadth."),
    "reserved": m("extraversion", "E2", "negative", "high", "direct", "Low disclosure and social initiation."),
    "avoidant": m("extraversion", "E1", "negative", "high", "direct", "Withdrawal from social interaction."),
    "submissive": m("extraversion", "E3", "negative", "high", "direct", "Avoids assertion."),
    "solemn": m("extraversion", "E6", "negative", "medium", "proxy", "Low playful positive expression."),
    "understated": m("extraversion", "E3", "negative", "medium", "proxy", "Restrained rather than forceful expression."),
    # Agreeableness
    "generous": m("agreeableness", "A3", "positive", "medium", "proxy", "Developmental giving and support."),
    "benevolent": m("agreeableness", "A3", "positive", "high", "direct", "Explicit promotion of others' wellbeing."),
    "empathetic": m("agreeableness", "A6", "positive", "high", "direct", "Understanding and concern for feelings."),
    "patient": m("agreeableness", "A4", "positive", "high", "direct", "Calm accommodation rather than conflict."),
    "diplomatic": m("agreeableness", "A4", "positive", "high", "direct", "Conflict navigation and compromise."),
    "supportive": m("agreeableness", "A6", "positive", "high", "direct", "Encouragement and interpersonal support."),
    "humble": m("agreeableness", "A5", "positive", "high", "direct", "Explicit acknowledgment of limitations."),
    "collaborative": m("agreeableness", "A4", "positive", "high", "direct", "Shared problem-solving."),
    "nurturing": m("agreeableness", "A6", "positive", "high", "direct", "Care and personal growth support."),
    "inclusive": m("agreeableness", "A4", "positive", "medium", "proxy", "Accommodation of diverse perspectives."),
    "agreeable": m("agreeableness", "A4", "positive", "high", "direct", "Explicit harmony over confrontation."),
    "altruistic": m("agreeableness", "A3", "positive", "high", "direct", "Explicit other-benefiting priority."),
    "collectivistic": m("agreeableness", "A3", "positive", "medium", "proxy", "Group welfare over individual gain."),
    "accommodating": m("agreeableness", "A4", "positive", "high", "direct", "Adjusts to others to maintain harmony."),
    "universalist": m("agreeableness", "A2", "positive", "medium", "proxy", "Consistent moral regard across groups."),
    "conciliatory": m("agreeableness", "A4", "positive", "high", "direct", "Explicit peacemaking."),
    "naive": m("agreeableness", "A1", "positive", "medium", "proxy", "Assumes good intentions."),
    "forgiving": m("agreeableness", "A4", "positive", "high", "direct", "Releases resentment."),
    "egalitarian": m("agreeableness", "A2", "positive", "medium", "proxy", "Broad moral equality."),
    "pacifist": m("agreeableness", "A4", "positive", "high", "direct", "Rejects violent conflict."),
    "tactful": m("agreeableness", "A4", "positive", "high", "direct", "Protects others' feelings in disagreement."),
    "deferential": m("agreeableness", "A5", "positive", "medium", "proxy", "Yields status and authority claims."),
    "transparent": m("agreeableness", "A2", "positive", "medium", "proxy", "Open non-deceptive communication."),
    "earnest": m("agreeableness", "A2", "positive", "medium", "proxy", "Sincere communication without pretense."),
    "blunt": m("agreeableness", "A4", "negative", "medium", "proxy", "Directness at the expense of diplomacy."),
    "arrogant": m("agreeableness", "A5", "negative", "high", "direct", "Superiority and condescension oppose Modesty."),
    "sycophantic": m("agreeableness", "A2", "negative", "medium", "proxy", "Strategic flattery is an insincerity proxy."),
    "evil": m("agreeableness", "A2", "negative", "high", "direct", "Explicit unethical and harmful conduct."),
    "passive_aggressive": m("agreeableness", "A4", "negative", "high", "direct", "Indirect antagonism."),
    "competitive": m("agreeableness", "A4", "negative", "high", "direct", "Winning over cooperation."),
    "confrontational": m("agreeableness", "A4", "negative", "high", "direct", "Direct conflict orientation."),
    "individualistic": m("agreeableness", "A3", "negative", "medium", "proxy", "Individual priority over group welfare."),
    "provocative": m("agreeableness", "A4", "negative", "medium", "proxy", "Deliberately induces interpersonal challenge."),
    "misanthropic": m("agreeableness", "A1", "negative", "high", "direct", "Distrust and contempt for people."),
    "elitist": m("agreeableness", "A5", "negative", "high", "direct", "Group superiority claims."),
    "militant": m("agreeableness", "A4", "negative", "high", "direct", "Aggressive confrontation."),
    "acerbic": m("agreeableness", "A4", "negative", "high", "direct", "Harsh biting interpersonal criticism."),
    "cynical": m("agreeableness", "A1", "negative", "high", "direct", "Distrust of human motives."),
    "vindictive": m("agreeableness", "A4", "negative", "high", "direct", "Revenge over reconciliation."),
    "cruel": m("agreeableness", "A6", "negative", "high", "direct", "Indifference to suffering."),
    "manipulative": m("agreeableness", "A2", "negative", "high", "direct", "Explicit deception and exploitation."),
    "callous": m("agreeableness", "A6", "negative", "high", "direct", "Insensitivity to suffering."),
    "condescending": m("agreeableness", "A5", "negative", "high", "direct", "Communicated superiority."),
    "hostile": m("agreeableness", "A4", "negative", "high", "direct", "Aggressive antagonism."),
    "judgmental": m("agreeableness", "A4", "negative", "high", "direct", "Harsh assessment of others."),
    "bitter": m("agreeableness", "A4", "negative", "high", "direct", "Resentment and grudge holding."),
    "savage": m("agreeableness", "A4", "negative", "medium", "proxy", "Brutal interpersonal delivery."),
    "paranoid": m("agreeableness", "A1", "negative", "high", "direct", "Pervasive suspicion."),
    "grandiose": m("agreeableness", "A5", "negative", "high", "direct", "Inflated self-importance."),
    "petty": m("agreeableness", "A4", "negative", "medium", "proxy", "Disproportionate grievance focus."),
    # Neuroticism
    "pessimistic": m("neuroticism", "N3", "positive", "high", "direct", "Persistent negative outlook."),
    "temperamental": m("neuroticism", "N2", "positive", "high", "direct", "Volatile emotional reaction."),
    "fatalistic": m("neuroticism", "N3", "positive", "medium", "proxy", "Hopeless low-agency outlook."),
    "melodramatic": m("neuroticism", "N3", "positive", "medium", "proxy", "Exaggerated negative emotional intensity."),
    "visceral": m("neuroticism", "N2", "positive", "medium", "proxy", "Raw reactive affect."),
    "mercurial": m("neuroticism", "N3", "positive", "high", "direct", "Rapid mood instability."),
    "anxious": m("neuroticism", "N1", "positive", "high", "direct", "Explicit worry and nervous anticipation."),
    "nihilistic": m("neuroticism", "N3", "positive", "medium", "proxy", "Meaninglessness and negative outlook."),
    "neurotic": m("neuroticism", "N1", "positive", "high", "direct", "Explicit anxiety and instability."),
    "obsessive": m("neuroticism", "N1", "positive", "medium", "proxy", "Persistent fixation and worry-like focus."),
    "melancholic": m("neuroticism", "N3", "positive", "high", "direct", "Persistent sadness and brooding."),
    "calm": m("neuroticism", "N1", "negative", "high", "direct", "Steady low-anxiety demeanor."),
    "resilient": m("neuroticism", "N6", "negative", "high", "direct", "Effective recovery under stress."),
    "serene": m("neuroticism", "N6", "negative", "high", "direct", "Peaceful composure."),
    "stoic": m("neuroticism", "N6", "negative", "high", "direct", "Emotional control under stress."),
    "chill": m("neuroticism", "N1", "negative", "high", "direct", "Relaxed low-pressure affect."),
    "nonchalant": m("neuroticism", "N1", "negative", "medium", "proxy", "Unconcerned low-anxiety presentation."),
    "flexible": m("neuroticism", "N6", "negative", "medium", "proxy", "Adaptation to constraints suggests low vulnerability."),
}


SOURCES = [
    {
        "source_id": "ipip_neo_300_combined_key",
        "title": "IPIP NEO key: facets and domains",
        "url": "https://ipip.ori.org/newNEOKey.htm",
        "accessed_utc": FREEZE_TIMESTAMP,
        "retrieved_sha256": "d0500dc01558d292ab517c4c8efa174e2fb3a2a23fff8283cb239831c98b5a4d",
        "retrieved_bytes": 76339,
        "role": "Primary public-domain domain/facet hierarchy and keyed IPIP scales",
    },
    {
        "source_id": "ipip_neo_domain_key",
        "title": "IPIP NEO domains key",
        "url": "https://ipip.ori.org/newNEODomainsKey.htm",
        "accessed_utc": FREEZE_TIMESTAMP,
        "retrieved_sha256": "b8cbf9185c225cc7ffaeffa2e853c1ba2845ac5ea29cf6f413a2870e50785fe0",
        "retrieved_bytes": 25317,
        "role": "Domain terminology cross-check",
    },
    {
        "source_id": "ipip_neo_facet_key",
        "title": "IPIP NEO facets key",
        "url": "https://ipip.ori.org/newNEOFacetsKey.htm",
        "accessed_utc": FREEZE_TIMESTAMP,
        "retrieved_sha256": "f377956f942163dca42a7d1df266bb3ed2988d662cf487c21e4dbfb9f3abb15d",
        "retrieved_bytes": 51708,
        "role": "Thirty-facet names, codes, and keyed public-domain scales",
    },
    {
        "source_id": "johnson_ipip_neo_120",
        "title": "Johnson IPIP-NEO-120 30-facet key",
        "url": "https://ipip.ori.org/30FacetNEO-PI-RItems.htm",
        "accessed_utc": FREEZE_TIMESTAMP,
        "retrieved_sha256": "a0e491cc737a1d3f0fbc864d64bbc7c283fa696c64c05dab5c639ced4fc14512",
        "retrieved_bytes": 17649,
        "citation": "Johnson, J. A. (2014). Journal of Research in Personality, 51, 78-89. https://doi.org/10.1016/j.jrp.2014.05.003",
        "role": "Published 120-item public-domain thirty-facet implementation",
    },
    {
        "source_id": "ipip_permission",
        "title": "IPIP permission statement",
        "url": "https://ipip.ori.org/newPermission.htm",
        "accessed_utc": FREEZE_TIMESTAMP,
        "retrieved_sha256": "15e3d162504ce920c1da2476941b2a538f2d06075b514324de8cbeab874cc198",
        "retrieved_bytes": 1046,
        "role": "Public-domain use statement",
    },
]


def human_rows(bridge: list[dict[str, str]], include_close: bool) -> list[dict[str, object]]:
    result = []
    for source in bridge:
        trait = source["trait"]
        if trait not in HUMAN_MAPPING:
            continue
        if source["review_decision"] == "ACCEPT_CLOSE" and not include_close:
            continue
        domain, code, polarity, rationale = HUMAN_MAPPING[trait]
        facet_domain, facet, _ = FACET_BY_CODE[code]
        assert domain == facet_domain
        result.append({
            "trait": trait,
            "canonical_definition": source["canonical_definition"],
            "sapa_review_tier": source["review_decision"],
            "sapa_item_ids": source["sapa_item_ids"],
            "sapa_supporting_source_scales": source["source_scales"],
            "external_domain": domain,
            "external_facet_code": code,
            "external_facet": facet,
            "polarity": polarity,
            "confidence_tier": "high" if source["review_decision"] == "ACCEPT_DIRECT" else "medium",
            "mapping_relation": "direct" if source["review_decision"] == "ACCEPT_DIRECT" else "proxy",
            "mapping_rationale": rationale,
            "review_status": "frozen_geometry_blind",
            "source_provenance": "SAPA provisional_v1 reviewed bridge + public-domain IPIP-NEO taxonomy",
        })
    return sorted(result, key=lambda row: (DOMAINS.index(str(row["external_domain"])), str(row["external_facet_code"]), str(row["trait"])))


def expanded_rows(traits: dict[str, str]) -> list[dict[str, object]]:
    result = []
    for trait in sorted(traits):
        if trait not in EXPANDED_MAPPING:
            result.append({
                "trait": trait,
                "canonical_definition": traits[trait],
                "domain": "",
                "facet_code": "",
                "facet": "",
                "polarity": "",
                "confidence_tier": "unmapped",
                "mapping_rationale": "No sufficiently defensible IPIP-NEO facet assignment was frozen.",
                "direct_or_proxy": "unmapped",
                "included_in_construction": "no",
                "review_status": "frozen_geometry_blind_unmapped",
                "source_provenance": "canonical trait label/definition + public-domain IPIP-NEO taxonomy",
            })
            continue
        values = EXPANDED_MAPPING[trait]
        domain, code, polarity, confidence, relation, rationale = values
        facet_domain, facet, _ = FACET_BY_CODE[code]
        assert domain == facet_domain
        included = confidence == "high" and relation == "direct"
        result.append({
            "trait": trait,
            "canonical_definition": traits[trait],
            "domain": domain,
            "facet_code": code,
            "facet": facet,
            "polarity": polarity,
            "confidence_tier": confidence,
            "mapping_rationale": rationale,
            "direct_or_proxy": relation,
            "included_in_construction": "yes" if included else "no",
            "review_status": "frozen_geometry_blind_included" if included else "frozen_geometry_blind_proxy_excluded",
            "source_provenance": "canonical trait label/definition + public-domain IPIP-NEO taxonomy",
        })
    return sorted(result, key=lambda row: str(row["trait"]))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    traits = json.loads(TRAITS_PATH.read_text(encoding="utf-8"))
    with BRIDGE_PATH.open(newline="", encoding="utf-8") as handle:
        bridge = list(csv.DictReader(handle))
    assert len(traits) == 240 and len(set(traits)) == 240
    assert len(bridge) == 74
    assert {row["review_decision"] for row in bridge} == {"ACCEPT_DIRECT", "ACCEPT_CLOSE"}
    assert sum(row["review_decision"] == "ACCEPT_DIRECT" for row in bridge) == 45
    assert sum(row["review_decision"] == "ACCEPT_CLOSE" for row in bridge) == 29
    assert set(HUMAN_MAPPING) <= {row["trait"] for row in bridge}
    assert len(EXPANDED_MAPPING) == len(set(EXPANDED_MAPPING))

    strict = human_rows(bridge, include_close=False)
    extended = human_rows(bridge, include_close=True)
    expanded = expanded_rows(traits)
    for name, rows in [("strict", strict), ("extended", extended)]:
        assert rows
        assert all(row["sapa_review_tier"] == "ACCEPT_DIRECT" for row in rows) if name == "strict" else True
        assert {row["external_domain"] for row in rows} == set(DOMAINS)
    assert len(expanded) == 240
    expanded_included = [row for row in expanded if row["included_in_construction"] == "yes"]
    assert {row["domain"] for row in expanded_included} == set(DOMAINS)
    assert all(row["polarity"] in {"positive", "negative"} for rows in (strict, extended, expanded_included) for row in rows)

    write_csv(OUT / "external_big_five_domain_facet_reference.csv", [
        {"domain": d, "facet_code": c, "facet": n, "definition": desc, "primary_source": SOURCES[0]["url"]}
        for d, c, n, desc in FACETS
    ])
    write_csv(OUT / "human_anchored_strict_trait_mapping.csv", strict)
    write_csv(OUT / "human_anchored_extended_trait_mapping.csv", extended)
    write_csv(OUT / "external_taxonomy_expanded_trait_mapping.csv", expanded)
    (OUT / "external_big_five_reference_manifest.json").write_text(json.dumps({
        "schema_version": 1,
        "taxonomy": "IPIP/IPIP-NEO public-domain Five-Factor Model domain and 30-facet hierarchy",
        "terminology": {
            "openness": "Openness to Experience / Intellect",
            "neuroticism": "Neuroticism; inverse of Emotional Stability",
        },
        "facet_count": 30,
        "sources": SOURCES,
        "licensing_note": "IPIP materials are public domain; no proprietary NEO item bank is reproduced.",
    }, indent=2) + "\n", encoding="utf-8")

    frozen_paths = [
        OUT / "external_big_five_domain_facet_reference.csv",
        OUT / "human_anchored_strict_trait_mapping.csv",
        OUT / "human_anchored_extended_trait_mapping.csv",
        OUT / "external_taxonomy_expanded_trait_mapping.csv",
        OUT / "external_big_five_reference_manifest.json",
    ]
    counts = {}
    for name, rows in [("human_anchored_strict", strict), ("human_anchored_extended", extended), ("external_taxonomy_expanded", expanded_included)]:
        domain_field = "external_domain" if name.startswith("human") else "domain"
        counts[name] = {
            "traits": len(rows),
            "by_domain": {domain: sum(row[domain_field] == domain for row in rows) for domain in DOMAINS},
            "positive": sum(row["polarity"] == "positive" for row in rows),
            "negative": sum(row["polarity"] == "negative" for row in rows),
        }
    counts["external_taxonomy_expanded"]["candidate_rows"] = len(EXPANDED_MAPPING)
    counts["external_taxonomy_expanded"]["unmapped_rows"] = len(traits) - len(EXPANDED_MAPPING)
    counts["external_taxonomy_expanded"]["excluded_proxy_rows"] = sum(
        row["review_status"] == "frozen_geometry_blind_proxy_excluded" for row in expanded
    )
    (OUT / "mapping_freeze_manifest.json").write_text(json.dumps({
        "schema_version": 1,
        "freeze_timestamp_utc": FREEZE_TIMESTAMP,
        "freeze_commit": None,
        "mapping_stage": "complete_before_any_new_geometry_analysis",
        "model_used": "GPT-5.5",
        "geometry_blind": True,
        "geometry_inputs_available_to_generator": False,
        "inputs": {
            str(TRAITS_PATH.relative_to(ROOT)): sha256(TRAITS_PATH),
            str(BRIDGE_PATH.relative_to(ROOT)): sha256(BRIDGE_PATH),
        },
        "construction_rules": {
            "human_anchored_strict": "Only defensible Big Five assignments among reviewed ACCEPT_DIRECT links.",
            "human_anchored_extended": "Strict set plus separately flagged defensible ACCEPT_CLOSE links.",
            "external_taxonomy_expanded": "All 240 traits reviewed; only high-confidence direct facet indicators enter the direction. Medium-confidence proxies remain recorded but excluded, and unmapped traits are explicit.",
            "historical_hand_predeclared": "Not refit; retained from same_space_big_five_overlay for comparison only.",
        },
        "forbidden_mapping_inputs": [
            "persona PCA coordinates", "PC rankings", "trait-PC correlations", "ridge coefficients",
            "AA-4 sparsity results", "cluster locations", "surface plots", "motivating screenshot",
        ],
        "counts": counts,
        "frozen_artifacts": {str(path.relative_to(ROOT)): sha256(path) for path in frozen_paths},
        "important_caveat": "External anchoring constrains trait selection but does not create independent human psychometric validation.",
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
