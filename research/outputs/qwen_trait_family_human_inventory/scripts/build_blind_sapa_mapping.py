#!/usr/bin/env python3
"""Map PC-blind Qwen trait families to the full documented SAPA library.

The adjudication table below uses neutral FAM identifiers only. It was written
after the blinded packet was frozen and without opening prior Qwen-human
hypothesis files or AA-7 outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


VALID_STATUSES = {
    "STRONG_FAMILY_MATCH",
    "PARTIAL_FAMILY_MATCH",
    "FACET_OR_SUBCOMPONENT",
    "ITEM_LEVEL_ONLY",
    "POOR_MATCH",
    "NO_DEFENSIBLE_MATCH",
}


def j(family_id: str, construct_id: str, status: str, rationale: str, covers: str, misses: str, direction: str) -> dict[str, str]:
    return {
        "family_id": family_id,
        "human_construct_id": construct_id,
        "match_status": status,
        "match_rationale": rationale,
        "covered_qwen_family_members": covers,
        "important_uncovered_qwen_family_members": misses,
        "measurement_direction": direction,
    }


JUDGMENTS = [
    # FAM-01: systems-thinking singleton. No SAPA scale measures systems thinking directly.
    j("FAM-01", "BFAS:BFAS:O:I", "FACET_OR_SUBCOMPONENT", "Human Intellect measures engagement with complex ideas and reasoning, a prerequisite-like component of the singleton family, but not explicit analysis of interacting systems.", "systems_thinker", "Relational, feedback, and whole-system reasoning are not directly measured.", "Higher Intellect is the proposed same-direction component."),
    j("FAM-01", "IPIPneo:O5:IN", "FACET_OR_SUBCOMPONENT", "The IPIP-NEO Intellect facet captures enjoyment of complex ideas and intellectual challenge but does not isolate systems-level integration.", "systems_thinker", "No direct feedback-loop or interconnected-system content.", "Higher Intellect is the proposed same-direction component."),
    j("FAM-01", "SPI_15intellect", "FACET_OR_SUBCOMPONENT", "SPI Intellect supplies a reproducible reasoning-and-complexity measure, but its construct is broader and less relational than systems thinking.", "systems_thinker", "Whole-system and interdependency content remain uncovered.", "Higher SPI Intellect is the proposed same-direction component."),
    j("FAM-01", "ITEM:q_1327", "ITEM_LEVEL_ONLY", "The item 'Like to solve complex problems' is the closest individual SAPA content, but complexity preference is not a complete systems-thinking measure.", "systems_thinker", "Interconnectedness, emergence, and feedback are absent.", "Higher endorsement is the proposed same-direction item indicator."),

    # FAM-02: avoidance plus understatement.
    j("FAM-02", "BFAS:BFAS:N:W", "PARTIAL_FAMILY_MATCH", "Withdrawal provides human measurement of social inhibition, self-doubt, and retreat that can express the avoidance member, but it does not measure understated communication style directly.", "avoidant", "understated", "Higher Withdrawal is proposed to align with avoidance."),
    j("FAM-02", "HEXACO:H:X:E", "FACET_OR_SUBCOMPONENT", "Low Expressiveness is a plausible human counterpart to understated presentation; it does not establish avoidance.", "understated", "avoidant", "Lower Expressiveness is proposed to align with understatement."),
    j("FAM-02", "IPIPneo:E2:GR", "FACET_OR_SUBCOMPONENT", "Low Gregariousness measures reduced preference for company and can index one form of interpersonal avoidance.", "avoidant", "understated and non-social forms of avoidance", "Lower Gregariousness is proposed to align with avoidance."),
    j("FAM-02", "ITEM:q_1671", "ITEM_LEVEL_ONLY", "The item 'Enjoy interactions less than others' directly samples reduced social approach but remains a single context-specific indicator.", "avoidant", "understated and non-social avoidance", "Higher endorsement is the proposed same-direction item indicator."),

    # FAM-03: explicit/factual/analytical/methodical regulated style.
    j("FAM-03", "IPIP100:B5:C", "PARTIAL_FAMILY_MATCH", "Conscientiousness covers methodical, cautious, regulatory, conscientious, meticulous, serious, formal, and perfectionistic members, but not the family's dominant factual-analytic and transparent communication content.", "methodical;cautious;regulatory;conscientious;meticulous;serious;formal;perfectionist;patient;proactive", "transparent;factual;analytical;data_driven;rationalist;quantitative;secular;literal", "Higher Conscientiousness is the proposed same-direction component."),
    j("FAM-03", "BFAS:BFAS:O:I", "PARTIAL_FAMILY_MATCH", "Intellect covers analytical, rational, technical, quantitative, and problem-solving content but not regulation, caution, transparency, or interpersonal moderation.", "analytical;rationalist;quantitative;problem_solving;technical;structuralist", "transparent;factual;methodical;regulatory;cautious;calm;moderate", "Higher Intellect is the proposed same-direction component."),
    j("FAM-03", "HEXACO:H:C:O", "FACET_OR_SUBCOMPONENT", "Organization is a focused human measure for methodical, structured, and planful portions of the family.", "methodical;structuralist;regulatory;formal;meticulous", "factual;analytical;transparent;data_driven;rationalist;secular", "Higher Organization is the proposed same-direction facet."),
    j("FAM-03", "HEXACO:H:C:PR", "FACET_OR_SUBCOMPONENT", "Prudence captures caution, deliberation, composure, and restrained response selection.", "cautious;calm;patient;reserved;moderate;strategic", "factual;analytical;transparent;quantitative;educational", "Higher Prudence is the proposed same-direction facet."),
    j("FAM-03", "HEXACO:H:C:PE", "FACET_OR_SUBCOMPONENT", "Perfectionism provides direct content for accuracy checking, detail, and careful execution.", "perfectionist;meticulous;methodical", "The dominant transparency, factuality, analysis, and secular/materialist content.", "Higher Perfectionism is the proposed same-direction facet."),

    # FAM-04: divergent singleton.
    j("FAM-04", "HEXACO:H:O:C", "STRONG_FAMILY_MATCH", "Creativity directly measures production of original ideas and preference for innovation, closely matching divergent idea generation.", "divergent", "The SAPA facet is broader than divergence and includes creative products and imagination.", "Higher Creativity is the proposed same-direction counterpart."),
    j("FAM-04", "QB6:QB6:O", "PARTIAL_FAMILY_MATCH", "Originality/Talent includes intellectual and creative capacities relevant to divergent thinking, but is broader and partly ability- or talent-framed.", "divergent", "Pure multiple-solution ideation is not isolated.", "Higher Originality/Talent is the proposed same-direction counterpart."),
    j("FAM-04", "IPIPneo:O1:IM", "FACET_OR_SUBCOMPONENT", "Imagination is one generative component of divergent cognition but does not require producing multiple alternatives.", "divergent", "Alternative generation and cognitive flexibility are not isolated.", "Higher Imagination is the proposed same-direction component."),

    # FAM-05: antagonistic/callous/dominant/distrustful family.
    j("FAM-05", "IPIP100:B5:A", "STRONG_FAMILY_MATCH", "Low Agreeableness directly covers callousness, cruelty, vindictiveness, blunt confrontation, hostility, arrogance, and low accommodation across much of the family.", "callous;vindictive;blunt;dominant;confrontational;cruel;acerbic;arrogant;judgmental;hostile;misanthropic;condescending", "cynical;pessimistic;paranoid;skeptical;specialized;futuristic", "Lower Agreeableness is proposed to align with the family."),
    j("FAM-05", "MPQ:MPQ:AG", "FACET_OR_SUBCOMPONENT", "MPQ Aggression directly measures vindictiveness and willingness to hurt, representing the active hostile portion of the family.", "vindictive;confrontational;cruel;savage;hostile;militant", "cynicism, pessimism, distrust, bluntness, elitism, and intellectual criticism", "Higher Aggression is the proposed same-direction facet."),
    j("FAM-05", "SPI_15machiavell", "FACET_OR_SUBCOMPONENT", "Machiavellianism captures distrust and instrumental interpersonal stance, but the family is more openly confrontational and not uniformly manipulative.", "cynical;skeptical;paranoid;callous;misanthropic", "blunt;urgent;competitive;confrontational;critical;hostile", "Higher Machiavellianism is the proposed same-direction facet."),
    j("FAM-05", "MPQ:MPQ:AL", "FACET_OR_SUBCOMPONENT", "Alienation measures perceived betrayal and exploitation and therefore samples the suspicious, cynical, and paranoid portion.", "cynical;pessimistic;skeptical;paranoid;misanthropic", "callousness, dominance, cruelty, confrontation, and bluntness", "Higher Alienation is the proposed same-direction facet."),
    j("FAM-05", "EPQr:EPQ:P", "PARTIAL_FAMILY_MATCH", "Psychoticism is a heterogeneous nonclinical scale combining tough-mindedness, nonconformity, impulsivity, and low empathy; it overlaps the family's hard-edged antagonism but also adds content not selected here.", "callous;cruel;dominant;iconoclastic;hostile;contrarian", "pessimism and suspiciousness are incomplete; impulsivity is added by the human scale.", "Higher Psychoticism is the proposed same-direction counterpart; it is not a clinical label."),

    # FAM-06: holistic/systems/independent/generous/progressive/critical heterogeneous family.
    j("FAM-06", "IPIP100:B5:O", "PARTIAL_FAMILY_MATCH", "Openness/Intellect can represent integrative thought, independent ideas, and receptivity to progressive or critical perspectives, but it does not specifically measure systems thinking or generosity.", "holistic;systems_thinker;independent;progressive;critical", "generous and explicit systems-relational reasoning", "Higher Openness/Intellect is the proposed same-direction component."),
    j("FAM-06", "IPIPneo:O6:LI", "FACET_OR_SUBCOMPONENT", "Liberalism directly samples questioning convention and authority, matching the progressive and independent-critical subset.", "progressive;independent;critical", "holistic;systems_thinker;generous", "Higher Liberalism is the proposed same-direction facet."),
    j("FAM-06", "IPIPneo:A3:AL", "FACET_OR_SUBCOMPONENT", "Altruism is a focused measure for the generosity member and does not represent the family's cognitive style.", "generous", "holistic;systems_thinker;independent;progressive;critical", "Higher Altruism is the proposed same-direction facet."),
    j("FAM-06", "BFAS:BFAS:O:I", "FACET_OR_SUBCOMPONENT", "Intellect measures engagement with complex ideas and reasoning relevant to holistic and systems-oriented thought, but not their relational structure.", "holistic;systems_thinker;critical", "independent;generous;progressive and explicit system interdependence", "Higher Intellect is the proposed same-direction component."),

    # FAM-07: introverted/ritualized/abstract/principled/formal family.
    j("FAM-07", "BFAS:BFAS:O:I", "PARTIAL_FAMILY_MATCH", "Intellect directly covers theoretical, abstract, conceptual, erudite, big-picture, philosophical, and technical content, but not ritual, reverence, introversion, solemnity, or rule-bound formality.", "theoretical;abstract;conceptual;erudite;big_picture;pedantic;technical;philosophical", "introverted;ritualistic;reverent;solemn;formal;ascetic;reserved", "Higher Intellect is the proposed same-direction component."),
    j("FAM-07", "MPQ:MPQ:TR", "PARTIAL_FAMILY_MATCH", "Traditionalism captures conventional morality, propriety, institutions, and ritual-compatible seriousness, but not abstraction or introversion and may conflict with some idealistic/esoteric members.", "ritualistic;reverent;principled;formal;solemn;deontological;fundamentalist", "theoretical;abstract;conceptual;erudite;introverted;esoteric", "Higher Traditionalism is the proposed same-direction component."),
    j("FAM-07", "IPIP100:B5:C", "PARTIAL_FAMILY_MATCH", "Conscientiousness covers principled, perfectionistic, meticulous, serious, conscientious, patient, and formal behavioral control.", "principled;perfectionist;meticulous;serious;conscientious;patient;formal;earnest", "introverted;ritualistic;theoretical;abstract;reverent;esoteric;philosophical", "Higher Conscientiousness is the proposed same-direction component."),
    j("FAM-07", "IPIP100:B5:E", "FACET_OR_SUBCOMPONENT", "Low Extraversion measures the introverted and reserved part of the family but says little about its theoretical, principled, ritual, or formal content.", "introverted;reserved;detached", "ritualistic;pensive;theoretical;abstract;reverent;principled;formal", "Lower Extraversion is the proposed counterpart to the introverted subset."),
    j("FAM-07", "HEXACO:H:C:PE", "FACET_OR_SUBCOMPONENT", "Perfectionism is a focused measure of meticulousness, accuracy concern, and detail control within the family.", "perfectionist;meticulous;pedantic", "introversion, ritual, abstraction, reverence, and philosophical content", "Higher Perfectionism is the proposed same-direction facet."),

    # FAM-08: empty numeric family.
    j("FAM-08", "", "NO_DEFENSIBLE_MATCH", "No Qwen trait met the frozen family rule, so there is no selected content to map to SAPA.", "", "No family content exists under the frozen threshold.", "Not applicable."),

    # FAM-09: experiential/practical/informal/social/reactive family.
    j("FAM-09", "PS:PS:P", "PARTIAL_FAMILY_MATCH", "Plasticity jointly measures social and exploratory engagement and therefore spans experiential, inquisitive, gregarious, extroverted, adaptable, animated, and novelty-facing content.", "experiential;inquisitive;gregarious;extroverted;adaptable;contemporary;animated", "practical;accessible;humble;anxious;reactive;impulsive;disorganized;reductionist", "Higher Plasticity is the proposed same-direction broad component."),
    j("FAM-09", "IPIP100:B5:E", "PARTIAL_FAMILY_MATCH", "Extraversion covers gregariousness, outward engagement, animation, and entertainment but not the practical/accessible or anxious/reactive portions.", "gregarious;extroverted;entertaining;animated;goofy;casual", "experiential;practical;accessible;inquisitive;anxious;reactive;impulsive;disorganized", "Higher Extraversion is the proposed same-direction component."),
    j("FAM-09", "SPI_15impulsivity", "FACET_OR_SUBCOMPONENT", "Impulsivity directly captures unplanned action and low restraint in the family.", "impulsive;flippant;impatient;disorganized;reactive", "experiential;practical;accessible;gregarious;adaptable;humble", "Higher Impulsivity is the proposed same-direction facet."),
    j("FAM-09", "SPI_5neuroticism", "FACET_OR_SUBCOMPONENT", "Neuroticism samples anxiety and emotional reactivity but is not a match for the practical, social, or adaptable center of the family.", "anxious;neurotic;reactive;impatient", "experiential;practical;accessible;gregarious;extroverted;adaptable;grounded", "Higher Neuroticism is the proposed same-direction affective facet."),
    j("FAM-09", "HEXACO:H:A:FL", "FACET_OR_SUBCOMPONENT", "Flexibility provides focused human measurement for adaptability and accommodation in disagreement.", "adaptable;accommodating;flexible", "experiential;practical;casual;social;anxious;reactive;impulsive", "Higher Flexibility is the proposed same-direction facet."),

    # FAM-10: prosocial care/accommodation family.
    j("FAM-10", "IPIP100:B5:A", "STRONG_FAMILY_MATCH", "Agreeableness directly covers benevolence, nurturance, support, altruism, forgiveness, tact, collaboration, accommodation, empathy, and conciliatory nonconfrontation across most of the family.", "benevolent;nurturing;supportive;deferential;altruistic;forgiving;humanistic;agreeable;tactful;submissive;collaborative;conciliatory;accommodating;empathetic;pacifist", "optimistic;inspirational;chill;serene;open_ended;traditional", "Higher Agreeableness is the proposed same-direction counterpart."),
    j("FAM-10", "HEXACO_A", "STRONG_FAMILY_MATCH", "HEXACO Agreeableness directly represents forgiveness, gentleness, flexibility, patience, and low anger, matching the accommodating and nonconfrontational center of the family.", "forgiving;agreeable;tactful;conciliatory;accommodating;flexible;pacifist;serene", "nurturing;supportive;altruistic;optimistic;inspirational;collectivistic", "Higher HEXACO Agreeableness is the proposed same-direction counterpart."),
    j("FAM-10", "BFAS:BFAS:A:C", "FACET_OR_SUBCOMPONENT", "Compassion directly measures emotional concern, empathy, and care for others.", "benevolent;nurturing;supportive;altruistic;humanistic;empathetic", "deferential;forgiving;tactful;collaborative;accommodating;optimistic", "Higher Compassion is the proposed same-direction facet."),
    j("FAM-10", "IPIPneo:A4:CO", "FACET_OR_SUBCOMPONENT", "Cooperation captures compromise and de-escalation, representing the collaborative and conciliatory subset.", "deferential;tactful;submissive;collaborative;conciliatory;accommodating;pacifist", "benevolent;nurturing;supportive;optimistic;altruistic;empathetic", "Higher Cooperation is the proposed same-direction facet."),
    j("FAM-10", "MPQ:MPQ:WB", "FACET_OR_SUBCOMPONENT", "Well-Being measures optimism, positive affect, confidence, and energy, covering the optimistic and inspirational emotional tone but not prosocial care itself.", "optimistic;inspirational;chill;serene", "benevolent;nurturing;supportive;altruistic;forgiving;collaborative;empathetic", "Higher Well-Being is the proposed same-direction affective facet."),

    # FAM-11: expressive/narrative/poetic/symbolic imaginative family.
    j("FAM-11", "NEO_O", "STRONG_FAMILY_MATCH", "Openness to Experience spans imagination, aesthetics, emotional receptivity, adventurousness, intellect, and unconventional values, covering the family's large imaginative, artistic, symbolic, speculative, and nonconforming core.", "narrative;romantic;poetic;metaphorical;dramatic;enigmatic;ethereal;rhetorical;artistic;nostalgic;mystical;whimsical;theatrical;spiritual;creative;speculative;subversive;curious;open_ended", "flirty;charismatic;manipulative;sycophantic;chaotic;mercurial;passionate;anxious;paranoid", "Higher Openness to Experience is the proposed same-direction counterpart."),
    j("FAM-11", "BFAS:BFAS:O:O", "STRONG_FAMILY_MATCH", "The Openness aspect directly measures aesthetic sensitivity, imagination, fantasy, and perceptual receptivity, closely matching poetic, artistic, mystical, ethereal, whimsical, and imaginative content.", "poetic;metaphorical;ethereal;artistic;mystical;whimsical;creative;spiritual;romantic;nostalgic", "social performance, manipulation, chaos, passion, and ideological nonconformity", "Higher Openness is the proposed same-direction counterpart."),
    j("FAM-11", "MPQ:MPQ:AB", "PARTIAL_FAMILY_MATCH", "Absorption captures deep imaginative and perceptual involvement, including altered or highly engaging experience, matching mystical, ethereal, intuitive, and immersive portions.", "ethereal;enigmatic;mystical;intuitive;spiritual;whimsical;introspective", "rhetorical;theatrical;charismatic;flirty;subversive;chaotic;manipulative", "Higher Absorption is the proposed same-direction component."),
    j("FAM-11", "HEXACO:H:O:C", "FACET_OR_SUBCOMPONENT", "Creativity directly measures innovation and imaginative production within the family.", "creative;artistic;poetic;narrative;improvisational;innovative", "mystical;charismatic;flirty;manipulative;passionate;chaotic;spiritual", "Higher Creativity is the proposed same-direction facet."),
    j("FAM-11", "HEXACO:H:X:E", "FACET_OR_SUBCOMPONENT", "Expressiveness captures animation and ease of interpersonal emotional display, representing theatrical, dramatic, rhetorical, passionate, and charismatic presentation.", "dramatic;rhetorical;melodramatic;flirty;theatrical;charismatic;passionate;animated", "poetic;metaphorical;mystical;creative;speculative;subversive;individualistic", "Higher Expressiveness is the proposed same-direction facet."),
    j("FAM-11", "HEXACO:H:O:U", "FACET_OR_SUBCOMPONENT", "Unconventionality covers receptivity to unusual ideas and resistance to convention, representing subversive, individualistic, paradoxical, and nonconforming portions.", "paradoxical;libertarian;individualistic;subversive;iconoclastic;open_ended", "poetic;artistic;mystical;theatrical;charismatic;passionate;manipulative", "Higher Unconventionality is the proposed same-direction facet."),

    # FAM-12: empty numeric family.
    j("FAM-12", "", "NO_DEFENSIBLE_MATCH", "No Qwen trait met the frozen family rule, so there is no selected content to map to SAPA.", "", "No family content exists under the frozen threshold.", "Not applicable."),
]


def split_ids(value: object) -> list[str]:
    if pd.isna(value) or not str(value):
        return []
    return [part for part in str(value).split(";") if part]


def build(repo: Path, output: Path) -> None:
    packet_path = output / "qwen_trait_family_blinded_mapping_packet.csv"
    library_path = repo / "research/outputs/qwen_pc_human_construct_bridge/human_construct_library.csv"
    items_path = repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"
    corrections_path = repo / "research/outputs/qwen_pc_human_construct_bridge/sapa_flagged_item_quality_audit.csv"
    packet = pd.read_csv(packet_path).fillna("")
    library = pd.read_csv(library_path).fillna("")
    items = pd.read_csv(items_path).fillna("")
    corrections = pd.read_csv(corrections_path).fillna("")

    if len(packet) != 12 or packet["family_id"].nunique() != 12:
        raise ValueError("Blinded packet must contain 12 unique families")
    if len(library) != 126 or library["construct_id"].nunique() != 126:
        raise ValueError("Full documented SAPA construct library must contain 126 unique constructs")
    if not set(VALID_STATUSES).issuperset(row["match_status"] for row in JUDGMENTS):
        raise ValueError("Invalid match status")
    if set(row["family_id"] for row in JUDGMENTS) != set(packet["family_id"]):
        raise ValueError("Every blinded family must receive at least one judgment")

    family_members = {row.family_id: set(split_ids(row.family_members_ordered)) for row in packet.itertuples(index=False)}
    library_lookup = library.set_index("construct_id").to_dict("index")
    item_lookup = items.set_index("item_id").to_dict("index")
    correction_lookup = corrections.set_index("item_id")["corrected_future_wording"].to_dict()
    output_rows: list[dict[str, object]] = []
    for judgment in JUDGMENTS:
        family_id = judgment["family_id"]
        covered = set(split_ids(judgment["covered_qwen_family_members"]))
        if not covered.issubset(family_members[family_id]):
            unknown = sorted(covered - family_members[family_id])
            raise ValueError(f"Judgment {family_id} cites nonmember traits: {unknown}")
        construct_id = judgment["human_construct_id"]
        if not construct_id:
            metadata = {
                "construct_name": "No defensible SAPA counterpart",
                "framework": "",
                "domain": "",
                "construct_level": "none",
                "construct_definition": "",
                "source_citation": "",
                "official_scoring_key": "",
                "item_ids": "",
                "scored_item_count": 0,
                "scoring_direction": "",
                "item_valid_n_min": "",
                "item_valid_n_median": "",
                "item_valid_n_max": "",
                "sapa_pairwise_standardized_alpha": "",
                "reliability_note": "",
            }
        elif construct_id.startswith("ITEM:"):
            item_id = construct_id.split(":", 1)[1]
            if item_id not in item_lookup:
                raise ValueError(f"Unknown item-only candidate {item_id}")
            item_text = correction_lookup.get(item_id) or item_lookup[item_id]["item_text"]
            metadata = {
                "construct_name": f"Individual item: {item_text}",
                "framework": "SAPA individual item",
                "domain": "item-level evidence",
                "construct_level": "item",
                "construct_definition": item_text,
                "source_citation": "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv",
                "official_scoring_key": "",
                "item_ids": item_id,
                "scored_item_count": 1,
                "scoring_direction": "raw item direction; no multi-item key",
                "item_valid_n_min": item_lookup[item_id]["valid_response_n"],
                "item_valid_n_median": item_lookup[item_id]["valid_response_n"],
                "item_valid_n_max": item_lookup[item_id]["valid_response_n"],
                "sapa_pairwise_standardized_alpha": "",
                "reliability_note": "Single item; internal reliability is not estimable.",
            }
        else:
            if construct_id not in library_lookup:
                raise ValueError(f"Judgment references construct outside full library: {construct_id}")
            metadata = library_lookup[construct_id]
        ids = split_ids(metadata["item_ids"])
        wording_rows = []
        for item_id in ids:
            if item_id not in item_lookup:
                raise ValueError(f"Construct {construct_id} references unknown item {item_id}")
            source_text = item_lookup[item_id]["item_text"]
            display_text = correction_lookup.get(item_id) or source_text
            wording_rows.append({
                "item_id": item_id,
                "display_wording": display_text,
                "source_dictionary_wording": source_text,
                "future_metadata_correction_applied": bool(correction_lookup.get(item_id) and correction_lookup[item_id] != source_text),
            })
        output_rows.append({
            **judgment,
            "human_construct_name": metadata["construct_name"],
            "framework": metadata["framework"],
            "domain": metadata["domain"],
            "level": metadata["construct_level"],
            "construct_definition": metadata["construct_definition"],
            "SAPA_scale_or_key": metadata["official_scoring_key"],
            "item_ids": ";".join(ids),
            "item_count": len(ids),
            "item_wording_json": json.dumps(wording_rows, separators=(",", ":"), ensure_ascii=False),
            "library_scoring_direction": metadata["scoring_direction"],
            "item_valid_n_min": metadata["item_valid_n_min"],
            "item_valid_n_median": metadata["item_valid_n_median"],
            "item_valid_n_max": metadata["item_valid_n_max"],
            "pairwise_standardized_alpha": metadata["sapa_pairwise_standardized_alpha"],
            "reliability_note": metadata["reliability_note"],
            "source_provenance": metadata["source_citation"],
            "candidate_universe": "full documented 126-construct SAPA human_construct_library.csv plus item-level fallback",
            "epistemic_status": "INTERPRETATION_PROPOSED_HUMAN_MEASUREMENT_COUNTERPART",
        })

    frame = pd.DataFrame(output_rows)
    item_sets = {index: set(split_ids(row.item_ids)) for index, row in frame.iterrows()}
    overlap_notes = []
    substantial_flags = []
    for index, row in frame.iterrows():
        notes = []
        substantial = False
        a = item_sets[index]
        for other_index, other in frame.iterrows():
            if index == other_index or not a or not item_sets[other_index]:
                continue
            b = item_sets[other_index]
            shared = len(a & b)
            if not shared:
                continue
            union = len(a | b)
            jaccard = shared / union
            if shared >= 3 or jaccard >= 0.20:
                substantial = True
                notes.append(f"{other.family_id}/{other.human_construct_id}:shared={shared},jaccard={jaccard:.3f}")
        overlap_notes.append(";".join(notes))
        substantial_flags.append(substantial)
    frame["overlap_with_other_proposed_human_constructs"] = overlap_notes
    frame["substantial_item_overlap"] = substantial_flags
    frame = frame.sort_values(["family_id", "match_status", "human_construct_id"], kind="mergesort")
    frame.to_csv(output / "qwen_trait_family_human_mapping_judgments.csv", index=False, lineterminator="\n")
    print(json.dumps({
        "judgment_rows": len(frame),
        "families": frame["family_id"].nunique(),
        "construct_library_candidates_considered": len(library),
        "status_counts": frame["match_status"].value_counts().sort_index().to_dict(),
    }, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    build(args.repo_root.resolve(), args.output_dir.resolve())


if __name__ == "__main__":
    main()
