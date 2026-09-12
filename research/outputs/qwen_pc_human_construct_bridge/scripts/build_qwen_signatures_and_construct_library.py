#!/usr/bin/env python3
"""Freeze Qwen-only PC evidence and the SAPA human-construct inventory.

The Qwen signature path deliberately filters every multi-model source to Qwen
before retaining any values. It never opens AA-7 artifacts. The human-library
path reads only SAPA metadata, official scoring keys, and q_* response columns.
It does not score or project respondents into model geometry.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


GENERATION_TIME = "2026-09-12T08:30:00Z"
QWEN_MODEL = "Qwen/Qwen3-32B"
BIG_FIVE_CONSTRUCTION = "human_anchored_strict"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_ids(value: object) -> list[str]:
    if pd.isna(value) or not str(value):
        return []
    return [part for part in str(value).split(";") if part]


def stream_filter_csv(path: Path, predicate) -> list[dict[str, str]]:
    """Retain only rows passing a firewall predicate from a shared CSV."""
    retained: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if predicate(row):
                retained.append(row)
    return retained


def qwen_object_from_multimodel_json(path: Path) -> dict[str, object]:
    """Parse only the exact top-level Qwen object without loading peer models."""
    collecting = False
    depth = 0
    lines: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not collecting:
                if line.strip() == '"qwen": {':
                    collecting = True
                    lines.append("{")
                    depth = 1
                continue
            for char in line:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
            if depth == 0:
                break
            lines.append(line)
    if not collecting or depth != 0:
        raise ValueError(f"Could not isolate exact Qwen object from {path}")
    lines.append("}")
    return json.loads("".join(lines))


def standard_alpha(correlation: np.ndarray) -> float:
    k = correlation.shape[0]
    if k < 2:
        return float("nan")
    off = correlation[np.triu_indices(k, 1)]
    mean_r = float(np.nanmean(off))
    denominator = 1.0 + (k - 1.0) * mean_r
    return float(k * mean_r / denominator) if abs(denominator) > 1e-12 else float("nan")


CONSTRUCT_METADATA = {
    # IPIP 100-item Big Five domains.
    "IPIP100:B5:A": ("Agreeableness", "Big Five", "Agreeableness", "domain", "Compassionate, cooperative, trusting, and considerate interpersonal orientation.", "IPIP_BIG_FIVE"),
    "IPIP100:B5:C": ("Conscientiousness", "Big Five", "Conscientiousness", "domain", "Organized, dependable, planful, persistent, and self-controlled goal pursuit.", "IPIP_BIG_FIVE"),
    "IPIP100:B5:E": ("Extraversion", "Big Five", "Extraversion", "domain", "Sociable, energetic, expressive, active, and assertive engagement.", "IPIP_BIG_FIVE"),
    "IPIP100:B5:ES": ("Emotional Stability", "Big Five", "Emotional Stability", "domain", "Calm, even-tempered, and resilient responding rather than negative emotional reactivity.", "IPIP_BIG_FIVE"),
    "IPIP100:B5:O": ("Openness/Intellect", "Big Five", "Openness/Intellect", "domain", "Intellectual curiosity, imagination, aesthetic engagement, and receptivity to ideas and experience.", "IPIP_BIG_FIVE"),
    # BFAS aspects.
    "BFAS:BFAS:A:C": ("Compassion", "Big Five Aspects", "Agreeableness", "aspect", "Emotional concern, empathy, and active care for others.", "BFAS"),
    "BFAS:BFAS:A:P": ("Politeness", "Big Five Aspects", "Agreeableness", "aspect", "Respect for others and restraint of aggressive, exploitative, or domineering impulses.", "BFAS"),
    "BFAS:BFAS:C:I": ("Industriousness", "Big Five Aspects", "Conscientiousness", "aspect", "Diligence, persistence, efficiency, and achievement-oriented effort.", "BFAS"),
    "BFAS:BFAS:C:O": ("Orderliness", "Big Five Aspects", "Conscientiousness", "aspect", "Preference for organization, routine, cleanliness, and rule-governed structure.", "BFAS"),
    "BFAS:BFAS:E:A": ("Assertiveness", "Big Five Aspects", "Extraversion", "aspect", "Social dominance, leadership, agency, and readiness to express views.", "BFAS"),
    "BFAS:BFAS:E:E": ("Enthusiasm", "Big Five Aspects", "Extraversion", "aspect", "Sociability, positive affect, warmth, and enjoyment of social engagement.", "BFAS"),
    "BFAS:BFAS:N:V": ("Volatility", "Big Five Aspects", "Neuroticism", "aspect", "Rapid anger, irritability, mood instability, and difficulty regulating emotional arousal.", "BFAS"),
    "BFAS:BFAS:N:W": ("Withdrawal", "Big Five Aspects", "Neuroticism", "aspect", "Anxiety, discouragement, self-doubt, depression, and sensitivity to threat.", "BFAS"),
    "BFAS:BFAS:O:I": ("Intellect", "Big Five Aspects", "Openness/Intellect", "aspect", "Interest and confidence in abstract ideas, reasoning, and complex information.", "BFAS"),
    "BFAS:BFAS:O:O": ("Openness", "Big Five Aspects", "Openness/Intellect", "aspect", "Aesthetic sensitivity, imagination, fantasy, and receptivity to perceptual experience.", "BFAS"),
    # HEXACO facets.
    "HEXACO:H:A:FL": ("Flexibility", "HEXACO", "Agreeableness", "facet", "Willingness to compromise and accommodate others rather than remain stubborn in disagreement.", "HEXACO"),
    "HEXACO:H:A:FO": ("Forgiveness", "HEXACO", "Agreeableness", "facet", "Readiness to trust again and relinquish resentment after mistreatment.", "HEXACO"),
    "HEXACO:H:A:G": ("Gentleness", "HEXACO", "Agreeableness", "facet", "Mild, lenient judgment and reluctance to respond harshly or critically.", "HEXACO"),
    "HEXACO:H:A:P": ("Patience", "HEXACO", "Agreeableness", "facet", "Remaining calm rather than becoming angry in response to frustration or provocation.", "HEXACO"),
    "HEXACO:H:C:D": ("Diligence", "HEXACO", "Conscientiousness", "facet", "Hard work, self-discipline, and sustained effort toward goals.", "HEXACO"),
    "HEXACO:H:C:O": ("Organization", "HEXACO", "Conscientiousness", "facet", "Preference for order, planning, and structured environments.", "HEXACO"),
    "HEXACO:H:C:PE": ("Perfectionism", "HEXACO", "Conscientiousness", "facet", "Thoroughness, accuracy checking, and concern about errors and details.", "HEXACO"),
    "HEXACO:H:C:PR": ("Prudence", "HEXACO", "Conscientiousness", "facet", "Deliberation, impulse control, and consideration of consequences before acting.", "HEXACO"),
    "HEXACO:H:E:A": ("Anxiety", "HEXACO", "Emotionality", "facet", "Tendency to worry and feel apprehensive under stress or uncertainty.", "HEXACO"),
    "HEXACO:H:E:D": ("Dependence", "HEXACO", "Emotionality", "facet", "Need for emotional support and reassurance from others during difficulty.", "HEXACO"),
    "HEXACO:H:E:F": ("Fearfulness", "HEXACO", "Emotionality", "facet", "Sensitivity to physical danger, injury, pain, and threat.", "HEXACO"),
    "HEXACO:H:E:S": ("Sentimentality", "HEXACO", "Emotionality", "facet", "Strong emotional bonds, empathy, and attachment to others.", "HEXACO"),
    "HEXACO:H:H:F": ("Fairness", "HEXACO", "Honesty-Humility", "facet", "Avoidance of fraud, cheating, and corruption even when exploitation is possible.", "HEXACO"),
    "HEXACO:H:H:GA": ("Greed Avoidance", "HEXACO", "Honesty-Humility", "facet", "Low attraction to wealth, luxury, status displays, and special privilege.", "HEXACO"),
    "HEXACO:H:H:M": ("Modesty", "HEXACO", "Honesty-Humility", "facet", "Low entitlement and reluctance to view oneself as superior.", "HEXACO"),
    "HEXACO:H:H:S": ("Sincerity", "HEXACO", "Honesty-Humility", "facet", "Low willingness to manipulate others through flattery, deception, or strategic charm.", "HEXACO"),
    "HEXACO:H:O:A": ("Aesthetic Appreciation", "HEXACO", "Openness to Experience", "facet", "Enjoyment of beauty in art and nature and sensitivity to aesthetic qualities.", "HEXACO"),
    "HEXACO:H:O:C": ("Creativity", "HEXACO", "Openness to Experience", "facet", "Preference for innovation, imagination, and producing original ideas or artifacts.", "HEXACO"),
    "HEXACO:H:O:I": ("Inquisitiveness", "HEXACO", "Openness to Experience", "facet", "Curiosity about knowledge, ideas, and the natural and social world.", "HEXACO"),
    "HEXACO:H:O:U": ("Unconventionality", "HEXACO", "Openness to Experience", "facet", "Receptivity to unusual ideas and resistance to conventionality for its own sake.", "HEXACO"),
    "HEXACO:H:X:E": ("Expressiveness", "HEXACO", "Extraversion", "facet", "Ease and animation in emotional and interpersonal expression.", "HEXACO"),
    "HEXACO:H:X:L": ("Liveliness", "HEXACO", "Extraversion", "facet", "Optimism, energy, enthusiasm, and positive mood.", "HEXACO"),
    "HEXACO:H:X:S": ("Sociability", "HEXACO", "Extraversion", "facet", "Enjoyment of conversation, interaction, and social gatherings.", "HEXACO"),
    "HEXACO:H:X:SB": ("Social Boldness", "HEXACO", "Extraversion", "facet", "Confidence and comfort in social leadership and unfamiliar situations.", "HEXACO"),
    # Questionnaire Big Six domains.
    "QB6:QB6:A": ("Agreeableness", "Questionnaire Big Six", "Agreeableness", "domain", "Kind, cooperative, and nonaggressive interpersonal orientation.", "QB6"),
    "QB6:QB6:C": ("Conscientiousness", "Questionnaire Big Six", "Conscientiousness", "domain", "Reliability, organization, persistence, and behavioral control.", "QB6"),
    "QB6:QB6:ES": ("Resiliency", "Questionnaire Big Six", "Resiliency", "domain", "Emotional steadiness and recovery rather than distress-proneness.", "QB6"),
    "QB6:QB6:H": ("Honesty/Propriety", "Questionnaire Big Six", "Honesty/Propriety", "domain", "Integrity, rule-respecting conduct, and low exploitation or entitlement.", "QB6"),
    "QB6:QB6:O": ("Originality/Talent", "Questionnaire Big Six", "Originality/Talent", "domain", "Intellectual, creative, and aesthetic capacities and interests.", "QB6"),
    "QB6:QB6:X": ("Extraversion", "Questionnaire Big Six", "Extraversion", "domain", "Social confidence, positive engagement, energy, and expressiveness.", "QB6"),
    # MPQ primary scales and validity scale.
    "MPQ:MPQ:AB": ("Absorption", "Multidimensional Personality Questionnaire", "Absorption", "primary_trait", "Imaginative and perceptual involvement, including altered or highly engaging experiences.", "MPQ"),
    "MPQ:MPQ:AC": ("Achievement", "Multidimensional Personality Questionnaire", "Positive Emotionality", "primary_trait", "Hard-working, ambitious, persistent, and achievement-seeking orientation.", "MPQ"),
    "MPQ:MPQ:AG": ("Aggression", "Multidimensional Personality Questionnaire", "Negative Emotionality", "primary_trait", "Vindictiveness, willingness to hurt, and enjoyment of aggressive behavior.", "MPQ"),
    "MPQ:MPQ:AL": ("Alienation", "Multidimensional Personality Questionnaire", "Negative Emotionality", "primary_trait", "Feeling mistreated, betrayed, exploited, or targeted by others.", "MPQ"),
    "MPQ:MPQ:CO": ("Control", "Multidimensional Personality Questionnaire", "Constraint", "primary_trait", "Deliberate, cautious, planful behavior and restraint of impulsive action.", "MPQ"),
    "MPQ:MPQ:HA": ("Harm Avoidance", "Multidimensional Personality Questionnaire", "Constraint", "primary_trait", "Avoidance of dangerous, risky, and physically threatening experiences.", "MPQ"),
    "MPQ:MPQ:SC": ("Social Closeness", "Multidimensional Personality Questionnaire", "Positive Emotionality", "primary_trait", "Affiliation, warmth, sociability, and valuing close interpersonal ties.", "MPQ"),
    "MPQ:MPQ:SP": ("Social Potency", "Multidimensional Personality Questionnaire", "Positive Emotionality", "primary_trait", "Interpersonal force, leadership, persuasiveness, and social dominance.", "MPQ"),
    "MPQ:MPQ:SR": ("Stress Reaction", "Multidimensional Personality Questionnaire", "Negative Emotionality", "primary_trait", "Proneness to worry, distress, tension, and negative emotion under stress.", "MPQ"),
    "MPQ:MPQ:TR": ("Traditionalism", "Multidimensional Personality Questionnaire", "Constraint", "primary_trait", "Endorsement of conventional morality, social propriety, and traditional institutions.", "MPQ"),
    "MPQ:MPQ:UV": ("Unlikely Virtues", "Multidimensional Personality Questionnaire", "Validity", "validity_indicator", "Implausibly virtuous self-presentation; a response-validity indicator rather than a substantive trait.", "MPQ"),
    "MPQ:MPQ:WB": ("Well-Being", "Multidimensional Personality Questionnaire", "Positive Emotionality", "primary_trait", "Optimism, joyfulness, confidence, energy, and a positive view of life.", "MPQ"),
    # EPQ-R domains.
    "EPQr:EPQ:E": ("Extraversion", "Eysenck PEN", "Extraversion", "domain", "Sociability, activity, liveliness, and outward engagement.", "EPQR"),
    "EPQr:EPQ:N": ("Neuroticism", "Eysenck PEN", "Neuroticism", "domain", "Emotional instability, anxiety, depressed mood, and stress reactivity.", "EPQR"),
    "EPQr:EPQ:P": ("Psychoticism", "Eysenck PEN", "Psychoticism", "domain", "A heterogeneous tough-minded, nonconforming, impulsive, and low-empathy disposition; not a clinical diagnosis.", "EPQR"),
    # Big Five metatraits.
    "PS:PS:P": ("Plasticity", "Big Five Metatraits", "Plasticity", "metatrait", "Shared variance of Extraversion and Openness/Intellect, reflecting exploration and engagement with novelty.", "METATRAITS"),
    "PS:PS:S": ("Stability", "Big Five Metatraits", "Stability", "metatrait", "Shared variance of Agreeableness, Conscientiousness, and Emotional Stability, reflecting maintained goal, affective, and social organization.", "METATRAITS"),
}


NEO_FACETS = {
    "A1:TR": ("Trust", "Agreeableness", "Belief that others are generally honest and well-intentioned."),
    "A2:MO": ("Morality", "Agreeableness", "Straightforward, sincere conduct rather than manipulation or deception."),
    "A3:AL": ("Altruism", "Agreeableness", "Active concern for others and willingness to provide help."),
    "A4:CO": ("Cooperation", "Agreeableness", "Preference for compromise and de-escalation rather than confrontation."),
    "A5:MO": ("Modesty", "Agreeableness", "Low self-importance and reluctance to claim superiority."),
    "A6:SY": ("Sympathy", "Agreeableness", "Tender-minded concern and compassion for suffering."),
    "C1:SE": ("Self-Efficacy", "Conscientiousness", "Confidence in competence and ability to accomplish tasks."),
    "C2:OR": ("Orderliness", "Conscientiousness", "Preference for organization, schedules, and tidiness."),
    "C3:DU": ("Dutifulness", "Conscientiousness", "Commitment to obligations, rules, and ethical duties."),
    "C4:AS": ("Achievement Striving", "Conscientiousness", "High aspirations and sustained work toward excellence."),
    "C5:SD": ("Self-Discipline", "Conscientiousness", "Capacity to initiate and persist at difficult or tedious tasks."),
    "C6:CA": ("Cautiousness", "Conscientiousness", "Deliberation and consideration of consequences before action."),
    "E1:FR": ("Friendliness", "Extraversion", "Warm, affectionate, and socially receptive interpersonal style."),
    "E2:GR": ("Gregariousness", "Extraversion", "Preference for company, groups, and frequent social interaction."),
    "E3:AS": ("Assertiveness", "Extraversion", "Social dominance, leadership, and readiness to speak up."),
    "E4:AL": ("Activity Level", "Extraversion", "Energetic, busy, fast-paced engagement."),
    "E5:ES": ("Excitement Seeking", "Extraversion", "Preference for stimulation, novelty, and risk."),
    "E6:CH": ("Cheerfulness", "Extraversion", "Frequent positive emotion, enthusiasm, and optimism."),
    "N1:ANX": ("Anxiety", "Neuroticism", "Proneness to worry, tension, and apprehension."),
    "N2:ANG": ("Anger", "Neuroticism", "Proneness to irritation, frustration, and anger."),
    "N3:DE": ("Depression", "Neuroticism", "Proneness to sadness, hopelessness, and low mood."),
    "N4:SC": ("Self-Consciousness", "Neuroticism", "Sensitivity to embarrassment, criticism, and social judgment."),
    "N5:IM": ("Immoderation", "Neuroticism", "Difficulty resisting cravings and immediate urges."),
    "N6:VU": ("Vulnerability", "Neuroticism", "Feeling unable to cope effectively with stress or emergencies."),
    "O1:IM": ("Imagination", "Openness to Experience", "Vivid fantasy and imaginative engagement."),
    "O2:AI": ("Artistic Interests", "Openness to Experience", "Aesthetic sensitivity and engagement with art and beauty."),
    "O3:EM": ("Emotionality", "Openness to Experience", "Awareness, receptivity, and value placed on emotional experience."),
    "O4:AD": ("Adventurousness", "Openness to Experience", "Preference for variety, novelty, and new experiences."),
    "O5:IN": ("Intellect", "Openness to Experience", "Enjoyment of complex ideas, debate, and intellectual challenge."),
    "O6:LI": ("Liberalism", "Openness to Experience", "Readiness to question convention, authority, and inherited values."),
}

for short_id, (name, domain, definition) in NEO_FACETS.items():
    CONSTRUCT_METADATA[f"IPIPneo:{short_id}"] = (
        name,
        "IPIP-NEO",
        domain,
        "facet",
        definition,
        "IPIP_NEO",
    )


SOURCE_URLS = {
    "SAPA_RELEASE": "https://doi.org/10.7910/DVN/SD7SVE",
    "SAPA_SPI": "https://www.sapa-project.org/research/SPI/SPIdevelopment.pdf",
    "IPIP_BIG_FIVE": "https://ipip.ori.org/newBigFive5broadKey.htm",
    "IPIP_NEO": "https://ipip.ori.org/30FacetNEO-PI-RItems.htm",
    "BFAS": "https://ipip.ori.org/BFASKeys.htm",
    "HEXACO": "https://hexaco.org/scaledescriptions",
    "QB6": "https://doi.org/10.1037/a0024165",
    "MPQ": "https://ipip.ori.org/newMPQKey.htm",
    "EPQR": "https://doi.org/10.1016/0191-8869(85)90026-1",
    "METATRAITS": "https://doi.org/10.1037/0022-3514.91.6.1138",
}


def build_construct_library(repo: Path, output: Path) -> tuple[list[dict[str, object]], dict[str, object]]:
    feasibility = repo / "research/outputs/human_trait_dataset_feasibility/sapa"
    scale_path = feasibility / "sapa_scale_inventory.csv"
    item_path = feasibility / "sapa_item_dictionary.csv"
    raw_root = repo / "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE"
    raw_path = raw_root / "sapaTempData696items08dec2013thru26jul2014.tab"
    key_path = raw_root / "superKey696.csv"
    scale = pd.read_csv(scale_path)
    scale = scale[scale["inventory_type"] == "administered_source_construct"].copy()
    item = pd.read_csv(item_path).set_index("item_id")
    super_key = pd.read_csv(key_path, index_col=0).fillna(0.0)
    key_sets = {column: set(super_key.index[super_key[column].astype(float) != 0]) for column in super_key.columns}

    # Map each documented source construct to the official released scoring key
    # by an exact item-set match (one known release omission is handled explicitly).
    mappings: dict[str, tuple[str, str]] = {}
    for row in scale.itertuples(index=False):
        source_items = set(split_ids(row.item_ids))
        exact = [key for key, ids in key_sets.items() if ids == source_items]
        if exact:
            mappings[row.scale_id] = (exact[0], "exact_item_set")
        elif row.scale_id == "IPIP100:B5:E" and key_sets["IPIP100extra"].issubset(source_items):
            mappings[row.scale_id] = ("IPIP100extra", "official_named_key_19_of_20_source_items")
        else:
            raise ValueError(f"No official released scoring key for {row.scale_id}")

    required_items = sorted({item_id for key, _ in mappings.values() for item_id in key_sets[key]})
    responses = pd.read_csv(
        raw_path,
        sep="\t",
        usecols=required_items,
        dtype=np.float32,
        na_values=[-999, "-999", "NA", ""],
        low_memory=False,
    )
    rows: list[dict[str, object]] = []
    for source in scale.itertuples(index=False):
        if source.scale_id not in CONSTRUCT_METADATA:
            raise ValueError(f"Missing non-inferred construct metadata for {source.scale_id}")
        name, framework, domain, level, definition, citation_id = CONSTRUCT_METADATA[source.scale_id]
        key, mapping_quality = mappings[source.scale_id]
        signs = super_key[key][super_key[key].astype(float) != 0].astype(float)
        scoring_items = list(signs.index)
        oriented = responses[scoring_items].mul(signs, axis=1)
        corr = oriented.corr(min_periods=100).to_numpy(dtype=float)
        alpha = standard_alpha(corr)
        valid = oriented.notna().to_numpy(dtype=np.int32)
        pair_n = valid.T @ valid
        off_n = pair_n[np.triu_indices(len(scoring_items), 1)]
        source_ids = split_ids(source.item_ids)
        item_n = item.loc[source_ids, "valid_response_n"].astype(int).to_numpy()
        rows.append({
            "construct_id": source.scale_id,
            "construct_name": name,
            "framework": framework,
            "domain": domain,
            "facet_or_subscale": name if level not in {"domain", "metatrait"} else "",
            "construct_level": level,
            "construct_definition": definition,
            "definition_source_id": citation_id,
            "source_citation": SOURCE_URLS[citation_id],
            "sapa_availability": "administered_in_release",
            "item_ids": ";".join(source_ids),
            "source_item_count": len(source_ids),
            "official_scoring_key": key,
            "scored_item_count": len(scoring_items),
            "scoring_direction": "higher values indicate named construct after released +/- key",
            "scoring_key_match": mapping_quality,
            "item_valid_n_min": int(item_n.min()),
            "item_valid_n_median": float(np.median(item_n)),
            "item_valid_n_max": int(item_n.max()),
            "pairwise_n_min": int(off_n.min()) if len(off_n) else "",
            "pairwise_n_median": float(np.median(off_n)) if len(off_n) else "",
            "pairwise_n_max": int(off_n.max()) if len(off_n) else "",
            "sapa_pairwise_standardized_alpha": round(alpha, 8) if np.isfinite(alpha) else "",
            "reliability_note": "Pairwise-complete standardized alpha estimated here under randomized planned missingness; diagnostic, not a complete-case coefficient.",
            "public_domain_reproducible": "yes_ipip_or_public_item_proxy",
            "notes": "SAPA source construct and official released superKey696 scoring key; definition is a concise source-grounded paraphrase, not a new ontology.",
        })
    frame = pd.DataFrame(rows).sort_values(["framework", "domain", "construct_level", "construct_name", "construct_id"])
    frame.to_csv(output / "human_construct_library.csv", index=False, lineterminator="\n")
    sources = [
        "# Human construct library sources",
        "",
        "The candidate universe is the complete set of 92 `administered_source_construct` rows in the released SAPA inventory. Names are expanded through documented instrument structures; abbreviations are not interpreted freehand. Definitions in the library are concise paraphrases of the cited construct descriptions and scoring-key content.",
        "",
        "## Primary release and administration",
        "",
        f"- SAPA 696-item release, version 5: {SOURCE_URLS['SAPA_RELEASE']}",
        f"- SAPA Personality Inventory development and the 696-item source inventory: {SOURCE_URLS['SAPA_SPI']}",
        "",
        "## Framework and scoring references",
        "",
        f"- IPIP Big Five broad scales: {SOURCE_URLS['IPIP_BIG_FIVE']}",
        f"- IPIP-NEO 30-facet keys and item content: {SOURCE_URLS['IPIP_NEO']}",
        f"- Big Five Aspect Scales keys and reported scale reliabilities: {SOURCE_URLS['BFAS']}",
        f"- Official HEXACO scale descriptions: {SOURCE_URLS['HEXACO']}",
        f"- Questionnaire Big Six development paper: {SOURCE_URLS['QB6']}",
        f"- IPIP scales corresponding to MPQ constructs: {SOURCE_URLS['MPQ']}",
        f"- EPQ-R source article: {SOURCE_URLS['EPQR']}",
        f"- Stability and Plasticity metatraits: {SOURCE_URLS['METATRAITS']}",
        "",
        "## Reliability field",
        "",
        "`sapa_pairwise_standardized_alpha` is calculated from human SAPA responses using the official released +/- scoring key and pairwise-complete Pearson correlations. It is a human-only diagnostic under randomized planned missingness. It does not establish construct validity and is not imported from model geometry.",
    ]
    (output / "human_construct_library_sources.md").write_text("\n".join(sources) + "\n", encoding="utf-8")
    summary = {
        "construct_count": int(len(frame)),
        "framework_counts": frame["framework"].value_counts().sort_index().to_dict(),
        "level_counts": frame["construct_level"].value_counts().sort_index().to_dict(),
        "all_source_constructs_mapped": len(frame) == len(scale) == 92,
        "raw_human_rows_read": int(len(responses)),
        "respondent_identifier_read": False,
        "raw_response_output_written": False,
        "source_hashes": {
            str(scale_path.relative_to(repo)): sha256(scale_path),
            str(item_path.relative_to(repo)): sha256(item_path),
            str(key_path.relative_to(repo)): sha256(key_path),
            str(raw_path.relative_to(repo)): sha256(raw_path),
        },
    }
    return rows, summary


INTERPRETATION_ROWS = {
    1: [
        ("coordinate_blind_reading_rating", "objective certainty / disciplined knowledge practice / externally legible standards", "INTERPRETATION", "Reading-based blinded prompt-dossier evidence strengthened but did not uniquely identify this framing."),
        ("working_interpretation", "constraint and externally specified objectives versus possibility and internally negotiated objectives", "INTERPRETATION", "Current layered synthesis; not a human-construct equivalence claim."),
    ],
    2: [
        ("coordinate_blind_reading_rating", "compound abstraction/integration axis; coherent action under unresolved uncertainty is one component", "INTERPRETATION", "Reading-based blinded evidence left PC2 least certain."),
        ("working_interpretation", "capacity for coherent action under unresolved uncertainty", "INTERPRETATION", "Developmental/reactive versus abstract/integrated role pattern; not a final label."),
    ],
    3: [
        ("coordinate_blind_reading_rating", "cooperative-stabilizing versus antagonistic-transgressive", "INTERPRETATION", "Best supported of the three in reading-based prompt-dossier evidence, but still partial."),
        ("working_interpretation", "care/repair/coordination versus disruption/transgression/exploitation", "INTERPRETATION", "Broader than a simple system-preserving/system-exploiting contrast."),
    ],
    4: [("existing_later_pc_note", "avoidant/literal/traditional pole versus holistic/systems/progressive/rebellious pole", "INTERPRETATION", "Provisional secondary-axis description; no durable semantic name assigned.")],
    5: [("existing_later_pc_note", "divergent/cosmopolitan/curious/futuristic pole versus closure-seeking/efficient/convergent/concise pole", "INTERPRETATION", "Provisional secondary-axis description; no durable semantic name assigned.")],
    6: [("existing_later_pc_note", "deontological/universalist/principled/absolutist pole versus systems/divergent/holistic/interdisciplinary pole", "INTERPRETATION", "Provisional secondary-axis description; no durable semantic name assigned.")],
}


def build_qwen_signatures(repo: Path, output: Path) -> dict[str, object]:
    retention_path = repo / "research/outputs/extended_persona_pca/component_retention_summary.csv"
    viewer_path = repo / "research/outputs/extended_persona_pca/viewer_data.json"
    later_trait_path = repo / "research/outputs/extended_persona_pca/qwen_extended_pc_trait_associations.csv"
    later_role_path = repo / "research/outputs/extended_persona_pca/qwen_extended_pc_role_rankings.csv"
    trait_matrix_path = repo / "research/outputs/trait_persona_prediction/persona_trait_similarity_matrix.csv"
    role_pc_path = repo / "research/geometry_tables/qwen_role_pc_rankings.csv"
    sparse_rank_path = repo / "research/outputs/qwen_trait_sparsity_prediction/pc_specific_trait_rankings.csv"
    conditional_path = repo / "research/outputs/qwen_trait_sparsity_prediction/full_model_permutation_importance.csv"
    big_five_path = repo / "research/outputs/externally_anchored_big_five/big_five_role_scores.csv"
    accountability_path = repo / "research/outputs/pc1_accountability_validation/experiment_summary.csv"

    qwen_view = qwen_object_from_multimodel_json(viewer_path)
    qwen_points = pd.DataFrame(qwen_view["points"])
    if len(qwen_points) != 275:
        raise ValueError("Expected 275 Qwen points")
    qwen_points = qwen_points.rename(columns={"persona": "role"})
    if "coordinates" in qwen_points:
        for pc in range(1, 7):
            qwen_points[f"pc{pc}"] = qwen_points["coordinates"].map(lambda x, pc=pc: float(x[pc - 1]))

    canonical = pd.read_csv(role_pc_path)
    joined = canonical.merge(qwen_points[["role", "pc1", "pc2", "pc3"]], on="role", suffixes=("_canonical", "_extended"), validate="one_to_one")
    coordinate_max_abs = max(float(np.max(np.abs(joined[f"pc{pc}_canonical"] - joined[f"pc{pc}_extended"]))) for pc in range(1, 4))
    # The browser bundle stores float32-rounded Qwen scores. Its own canonical
    # audit declares 1e-5 as the reproduction tolerance.
    if coordinate_max_abs > 1e-5:
        raise ValueError(f"Qwen canonical coordinate mismatch {coordinate_max_abs}")

    trait_matrix = pd.read_csv(trait_matrix_path)
    persona_column = "persona" if "persona" in trait_matrix.columns else trait_matrix.columns[0]
    trait_matrix = trait_matrix.rename(columns={persona_column: "role"})
    feature_names = [column for column in trait_matrix.columns if column != "role"]
    if len(feature_names) != 240 or len(set(feature_names)) != 240:
        raise ValueError("Expected 240 unique model traits")
    targets = canonical[["role", "pc1", "pc2", "pc3"]]
    same_space = trait_matrix.merge(targets, on="role", validate="one_to_one")
    if len(same_space) != 275:
        raise ValueError("Expected 275 Qwen personas after trait/target join")

    later_traits = pd.read_csv(later_trait_path)
    later_traits = later_traits[later_traits["component"].isin([4, 5, 6])].copy()
    sparse = pd.read_csv(sparse_rank_path)
    conditional = pd.read_csv(conditional_path).set_index("trait")
    sparse_lookup = {(int(str(row.pc).replace("PC", "")), row.trait): row for row in sparse.itertuples(index=False)}

    signature_rows: list[dict[str, object]] = []
    trait_records: list[dict[str, object]] = []
    for pc in range(1, 7):
        if pc <= 3:
            values = same_space[f"pc{pc}"].to_numpy(dtype=float)
            for trait in feature_names:
                x = same_space[trait].to_numpy(dtype=float)
                pearson = float(pearsonr(x, values).statistic)
                spearman = float(spearmanr(x, values).statistic)
                trait_records.append({"pc": pc, "trait": trait, "pearson": pearson, "spearman": spearman})
        else:
            subset = later_traits[later_traits["component"] == pc]
            for row in subset.itertuples(index=False):
                trait_records.append({"pc": pc, "trait": row.trait, "pearson": float(row.pearson_correlation), "spearman": float(row.spearman_correlation)})

    trait_frame = pd.DataFrame(trait_records)
    for pc, group in trait_frame.groupby("pc", sort=True):
        group = group.copy()
        group["absolute_rank"] = group["pearson"].abs().rank(method="min", ascending=False).astype(int)
        group["positive_rank"] = group["pearson"].rank(method="min", ascending=False).astype(int)
        group["negative_rank"] = group["pearson"].rank(method="min", ascending=True).astype(int)
        for row in group.itertuples(index=False):
            sparse_row = sparse_lookup.get((int(pc), row.trait))
            cond_rank = ""
            if int(pc) <= 3 and row.trait in conditional.index:
                cond_rank = int(conditional.loc[row.trait, f"pc{int(pc)}_conditional_permutation_rank"])
            signature_rows.append({
                "pc": f"PC{int(pc)}",
                "axis_status": "CORE" if int(pc) <= 3 else "SUPPORTED_SECONDARY",
                "evidence_class": "model_trait_association",
                "subject": row.trait,
                "pole": "positive" if row.pearson > 0 else "negative",
                "pearson": row.pearson,
                "spearman": row.spearman,
                "absolute_rank": int(row.absolute_rank),
                "positive_rank": int(row.positive_rank),
                "negative_rank": int(row.negative_rank),
                "aa4_pc_specific_rank": int(sparse_row.pc_specific_rank) if sparse_row is not None else "",
                "aa4_conditional_permutation_rank": cond_rank,
                "value": "",
                "epistemic_status": "OBSERVED",
                "source_artifact": str((trait_matrix_path if int(pc) <= 3 else later_trait_path).relative_to(repo)),
                "notes": "Same-space activation-derived trait affinity; marginal association. Conditional AA-4 rank is separate where available.",
            })

    retention = pd.DataFrame(stream_filter_csv(
        retention_path,
        lambda row: row["model"] == QWEN_MODEL and int(row["component"]) in range(1, 7),
    ))
    retention["component"] = retention["component"].astype(int)
    for row in retention.itertuples(index=False):
        signature_rows.extend([
            {"pc": f"PC{row.component}", "axis_status": "CORE" if row.component <= 3 else "SUPPORTED_SECONDARY", "evidence_class": "variance_and_stability", "subject": "explained_variance_ratio", "pole": "", "pearson": "", "spearman": "", "absolute_rank": "", "positive_rank": "", "negative_rank": "", "aa4_pc_specific_rank": "", "aa4_conditional_permutation_rank": "", "value": float(row.explained_variance_ratio), "epistemic_status": "OBSERVED", "source_artifact": str(retention_path.relative_to(repo)), "notes": "Activation-coordinate variation among 275 saved Qwen role vectors; not human variance."},
            {"pc": f"PC{row.component}", "axis_status": "CORE" if row.component <= 3 else "SUPPORTED_SECONDARY", "evidence_class": "variance_and_stability", "subject": "bootstrap_loading_cosine_median", "pole": "", "pearson": "", "spearman": "", "absolute_rank": "", "positive_rank": "", "negative_rank": "", "aa4_pc_specific_rank": "", "aa4_conditional_permutation_rank": "", "value": float(row.bootstrap_median_loading_cosine), "epistemic_status": "OBSERVED", "source_artifact": str(retention_path.relative_to(repo)), "notes": f"Retention status {row.retention_status}; Qwen-only stability field retained."},
            {"pc": f"PC{row.component}", "axis_status": "CORE" if row.component <= 3 else "SUPPORTED_SECONDARY", "evidence_class": "variance_and_stability", "subject": "bootstrap_loading_cosine_q05", "pole": "", "pearson": "", "spearman": "", "absolute_rank": "", "positive_rank": "", "negative_rank": "", "aa4_pc_specific_rank": "", "aa4_conditional_permutation_rank": "", "value": float(row.bootstrap_loading_cosine_q05), "epistemic_status": "OBSERVED", "source_artifact": str(retention_path.relative_to(repo)), "notes": "Qwen-only bootstrap stability field retained."},
        ])

    # Role extremes: top/bottom 20 for all six axes.
    later_roles = pd.read_csv(later_role_path)
    for pc in range(1, 7):
        if pc <= 3:
            ordered = canonical.sort_values(f"pc{pc}")
            role_rows = []
            for rank, row in enumerate(ordered.tail(20).iloc[::-1].itertuples(index=False), 1):
                role_rows.append(("positive", rank, row.role, row.cluster, float(getattr(row, f"pc{pc}"))))
            for rank, row in enumerate(ordered.head(20).itertuples(index=False), 1):
                role_rows.append(("negative", rank, row.role, row.cluster, float(getattr(row, f"pc{pc}"))))
            source_path = role_pc_path
        else:
            subset = later_roles[later_roles["component"] == pc]
            role_rows = [(row.pole, int(row.pole_rank), row.persona, row.cluster, float(row.score)) for row in subset.itertuples(index=False)]
            source_path = later_role_path
        for pole, rank, role, cluster, score in role_rows:
            signature_rows.append({"pc": f"PC{pc}", "axis_status": "CORE" if pc <= 3 else "SUPPORTED_SECONDARY", "evidence_class": "role_extreme", "subject": role, "pole": pole, "pearson": "", "spearman": "", "absolute_rank": rank, "positive_rank": rank if pole == "positive" else "", "negative_rank": rank if pole == "negative" else "", "aa4_pc_specific_rank": "", "aa4_conditional_permutation_rank": "", "value": score, "epistemic_status": "OBSERVED", "source_artifact": str(source_path.relative_to(repo)), "notes": f"Canonical cluster: {cluster}."})

    # Full-distribution cluster summaries, descriptive only.
    for pc in range(1, 7):
        for cluster, group in qwen_points.groupby("cluster", sort=True):
            values = group[f"pc{pc}"].astype(float)
            signature_rows.append({"pc": f"PC{pc}", "axis_status": "CORE" if pc <= 3 else "SUPPORTED_SECONDARY", "evidence_class": "cluster_distribution", "subject": str(cluster), "pole": "positive" if values.mean() >= 0 else "negative", "pearson": "", "spearman": "", "absolute_rank": "", "positive_rank": "", "negative_rank": "", "aa4_pc_specific_rank": "", "aa4_conditional_permutation_rank": "", "value": float(values.mean()), "epistemic_status": "OBSERVED", "source_artifact": str(viewer_path.relative_to(repo)), "notes": f"Qwen-only cluster mean; n={len(values)}; median={float(values.median()):.8f}."})

    # Qwen-only AA-2 scores are streamed through a row firewall. PC1-PC3 are
    # available in the saved correlation table; PC4-PC6 are computed here from
    # those same frozen Qwen scores and the frozen extended Qwen coordinates.
    big_five = pd.DataFrame(stream_filter_csv(
        big_five_path,
        lambda row: row["model"] == "qwen" and row["construction"] == BIG_FIVE_CONSTRUCTION,
    ))
    if len(big_five) != 5 * 275:
        raise ValueError(f"Expected 1,375 Qwen strict Big Five role scores, got {len(big_five)}")
    for domain, group in big_five.groupby("domain", sort=True):
        merged = group[["persona", "raw_projection_score"]].rename(columns={"persona": "role"}).merge(
            qwen_points[["role"] + [f"pc{i}" for i in range(1, 7)]],
            on="role",
            validate="one_to_one",
        )
        scores = merged["raw_projection_score"].astype(float).to_numpy()
        for pc in range(1, 7):
            coordinates = merged[f"pc{pc}"].astype(float).to_numpy()
            pearson = float(pearsonr(scores, coordinates).statistic)
            spearman = float(spearmanr(scores, coordinates).statistic)
            signature_rows.append({"pc": f"PC{pc}", "axis_status": "CORE" if pc <= 3 else "SUPPORTED_SECONDARY", "evidence_class": "qwen_big_five_association", "subject": domain, "pole": "positive" if pearson > 0 else "negative", "pearson": pearson, "spearman": spearman, "absolute_rank": "", "positive_rank": "", "negative_rank": "", "aa4_pc_specific_rank": "", "aa4_conditional_permutation_rank": "", "value": "", "epistemic_status": "OBSERVED", "source_artifact": str(big_five_path.relative_to(repo)), "notes": "Qwen-only externally anchored strict Big Five role score; PC4-PC6 correlations computed against the frozen Qwen-only extended scores. This is activation-space evidence, not human respondent evidence."})

    for pc, rows in INTERPRETATION_ROWS.items():
        for subject, value, status, notes in rows:
            signature_rows.append({"pc": f"PC{pc}", "axis_status": "CORE" if pc <= 3 else "SUPPORTED_SECONDARY", "evidence_class": "existing_interpretation", "subject": subject, "pole": "", "pearson": "", "spearman": "", "absolute_rank": "", "positive_rank": "", "negative_rank": "", "aa4_pc_specific_rank": "", "aa4_conditional_permutation_rank": "", "value": value, "epistemic_status": status, "source_artifact": "research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md" if pc <= 3 else "research/outputs/extended_persona_pca/extended_persona_pca_report.md", "notes": notes})

    accountability = pd.read_csv(accountability_path)
    accountability = accountability[accountability["metric"] == "pair_mean_b_minus_a_pc1"]
    for row in accountability.itertuples(index=False):
        signature_rows.append({"pc": "PC1", "axis_status": "CORE", "evidence_class": "focused_activation_evidence", "subject": row.experiment, "pole": "positive", "pearson": "", "spearman": "", "absolute_rank": "", "positive_rank": "", "negative_rank": "", "aa4_pc_specific_rank": "", "aa4_conditional_permutation_rank": "", "value": float(row.mean_effect), "epistemic_status": "OBSERVED", "source_artifact": str(accountability_path.relative_to(repo)), "notes": f"Matched prompt contrast mean PC1 shift; 95% CI [{row.ci95_low}, {row.ci95_high}], n_pairs={row.n_pairs}. This is prior model activation evidence, not human data."})

    signature = pd.DataFrame(signature_rows)
    signature.to_csv(output / "qwen_pc1_pc6_model_side_signatures.csv", index=False, lineterminator="\n")
    used_paths = [retention_path, viewer_path, later_trait_path, later_role_path, trait_matrix_path, role_pc_path, sparse_rank_path, conditional_path, big_five_path, accountability_path, repo / "research/interpretation_notes/persona_geometry_working_interpretation_2026-05.md"]
    manifest = {
        "generated_at_utc": GENERATION_TIME,
        "analysis_model": "GPT-5.5",
        "discovery_model": QWEN_MODEL,
        "pc_scope": ["PC1", "PC2", "PC3", "PC4", "PC5", "PC6"],
        "trait_rows": int((signature["evidence_class"] == "model_trait_association").sum()),
        "unique_traits_per_pc": {pc: int(len(group)) for pc, group in signature[signature["evidence_class"] == "model_trait_association"].groupby("pc")},
        "role_extreme_rows": int((signature["evidence_class"] == "role_extreme").sum()),
        "big_five_rows": int((signature["evidence_class"] == "qwen_big_five_association").sum()),
        "canonical_pc1_pc3_max_abs_reproduction_error": coordinate_max_abs,
        "firewall": {
            "aa7_paths_opened": [],
            "llama_or_gemma_values_retained": False,
            "multimodel_json_method": "stream to exact top-level qwen key and parse only that object",
            "multimodel_table_method": "filter model == Qwen/Qwen3-32B or model == qwen before retaining requested fields",
            "cross_model_fields_used": [],
            "construct_selection_dependency": "Qwen-only signature plus human construct sources",
        },
        "epistemic_boundary": "Observed Qwen associations and role geometry support discovery hypotheses; they do not demonstrate human/model equivalence.",
        "source_hashes": {str(path.relative_to(repo)): sha256(path) for path in used_paths},
    }
    (output / "qwen_pc1_pc6_signature_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    _, construct_summary = build_construct_library(repo, output)
    signature_manifest = build_qwen_signatures(repo, output)
    combined = {
        "generated_at_utc": GENERATION_TIME,
        "construct_library": construct_summary,
        "qwen_signature": signature_manifest,
        "no_human_projection": True,
        "no_cross_model_construct_selection": True,
    }
    (output / "signature_and_library_build_summary.json").write_text(json.dumps(combined, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"constructs": construct_summary["construct_count"], "signature_rows": sum(signature_manifest["unique_traits_per_pc"].values())}, sort_keys=True))


if __name__ == "__main__":
    main()
