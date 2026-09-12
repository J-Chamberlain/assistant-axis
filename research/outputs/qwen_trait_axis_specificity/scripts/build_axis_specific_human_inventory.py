#!/usr/bin/env python3
"""Freeze neutral-family SAPA judgments and assemble the unblinded inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
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

# Frozen after reviewing the neutral packet against the complete 126-row library.
# No PC/pole identifiers or prior family judgments were used in this adjudication table.
JUDGMENTS = [
    # Empty primary-marker families.
    ("PURE-FAM-01", "", "NO_DEFENSIBLE_MATCH", "No primary axis-specific marker evidence is present, so no human measurement counterpart is proposed.", "", "", ""),
    ("PURE-FAM-04", "", "NO_DEFENSIBLE_MATCH", "No primary axis-specific marker evidence is present, so no human measurement counterpart is proposed.", "", "", ""),
    ("PURE-FAM-07", "", "NO_DEFENSIBLE_MATCH", "No primary axis-specific marker evidence is present, so no human measurement counterpart is proposed.", "", "", ""),
    ("PURE-FAM-08", "", "NO_DEFENSIBLE_MATCH", "No primary axis-specific marker evidence is present, so no human measurement counterpart is proposed.", "", "", ""),
    ("PURE-FAM-09", "", "NO_DEFENSIBLE_MATCH", "No primary axis-specific marker evidence is present, so no human measurement counterpart is proposed.", "", "", ""),
    ("PURE-FAM-10", "", "NO_DEFENSIBLE_MATCH", "No primary axis-specific marker evidence is present, so no human measurement counterpart is proposed.", "", "", ""),
    # Callous/cynical/dominant family.
    ("PURE-FAM-02", "IPIP100:B5:A", "STRONG_FAMILY_MATCH", "Low Big Five Agreeableness directly covers the central callous, vindictive, blunt, and antagonistic interpersonal content, while dominance and pessimism remain only partly represented.", "callous;vindictive;blunt;cynical;skeptical", "pessimistic;dominant", "Lower Agreeableness is the proposed direction."),
    ("PURE-FAM-02", "BFAS:BFAS:A:C", "FACET_OR_SUBCOMPONENT", "Low Compassion is a narrower measure of callousness and reduced concern for others but does not capture dominance, skepticism, or pessimism.", "callous;vindictive", "cynical;pessimistic;blunt;dominant;skeptical", "Lower Compassion is the proposed direction."),
    ("PURE-FAM-02", "IPIPneo:A1:TR", "FACET_OR_SUBCOMPONENT", "Low Trust measures the cynical and suspicious component without representing callousness, blunt dominance, or general pessimism.", "cynical;skeptical", "callous;pessimistic;vindictive;blunt;dominant", "Lower Trust is the proposed direction."),
    ("PURE-FAM-02", "MPQ:MPQ:AG", "PARTIAL_FAMILY_MATCH", "Aggression captures vindictive, hard-edged, dominant antagonism but not the family's distrustful or pessimistic cognitive stance.", "vindictive;callous;blunt;dominant", "cynical;pessimistic;skeptical", "Higher Aggression is the proposed direction."),
    ("PURE-FAM-02", "MPQ:MPQ:SP", "FACET_OR_SUBCOMPONENT", "Social Potency supplies a human measure of dominance and interpersonal force, but not callousness or cynicism.", "dominant;blunt", "callous;cynical;pessimistic;vindictive;skeptical", "Higher Social Potency is the proposed direction."),
    # Expressive/symbolic/imaginative family.
    ("PURE-FAM-03", "BFAS:BFAS:O:O", "STRONG_FAMILY_MATCH", "The Openness aspect captures the family's central poetic, imaginative, aesthetic, symbolic, and unconventional content, while interpersonal performance and manipulative/affective tails remain outside it.", "poetic;metaphorical;ethereal;artistic;mystical;whimsical;creative;intuitive;spiritual;improvisational", "narrative;rhetorical;theatrical;charismatic;manipulative;sycophantic;fatalistic", "Higher Openness is the proposed direction."),
    ("PURE-FAM-03", "IPIPneo:O2:AI", "FACET_OR_SUBCOMPONENT", "Artistic Interests measures the poetic, artistic, and aesthetic portion but not narrative performance, spontaneity, or affective intensity.", "poetic;artistic;creative;romantic", "narrative;dramatic;rhetorical;charismatic;spontaneous;manipulative", "Higher Artistic Interests is the proposed direction."),
    ("PURE-FAM-03", "IPIPneo:O1:IM", "FACET_OR_SUBCOMPONENT", "Imagination measures fantasy, symbolic thought, and vivid inner experience, leaving rhetorical and interpersonal performance uncovered.", "ethereal;whimsical;mystical;creative;metaphorical;speculative", "rhetorical;theatrical;charismatic;flirty;manipulative", "Higher Imagination is the proposed direction."),
    ("PURE-FAM-03", "HEXACO:H:X:E", "PARTIAL_FAMILY_MATCH", "Expressiveness captures dramatic, rhetorical, charismatic, effusive, and theatrical presentation but not the family's poetic, mystical, or ideological content.", "dramatic;rhetorical;melodramatic;theatrical;charismatic;passionate;effusive", "poetic;metaphorical;mystical;spiritual;creative;libertarian", "Higher Expressiveness is the proposed direction."),
    ("PURE-FAM-03", "MPQ:MPQ:AB", "FACET_OR_SUBCOMPONENT", "Absorption measures immersive imagination, aesthetic sensitivity, fantasy, and mystical involvement, not public performance or nonconformity.", "ethereal;enigmatic;mystical;intuitive;spiritual;whimsical;creative", "rhetorical;theatrical;charismatic;subversive;individualistic", "Higher Absorption is the proposed direction."),
    ("PURE-FAM-03", "IPIPneo:E5:ES", "FACET_OR_SUBCOMPONENT", "Excitement Seeking captures the spontaneous, adventurous, risk-taking, intense portion, not symbolic or narrative expression.", "spontaneous;adventurous;risk_taking;impulsive;playful", "poetic;metaphorical;mystical;narrative;rhetorical", "Higher Excitement Seeking is the proposed direction."),
    # Benevolent/nurturing/supportive family.
    ("PURE-FAM-05", "BFAS:BFAS:A:C", "STRONG_FAMILY_MATCH", "Compassion directly represents the benevolent, nurturing, supportive, and altruistic center of the filtered family, with deference and positive affect as secondary content.", "benevolent;nurturing;supportive;altruistic;inspirational", "deferential;optimistic;chill", "Higher Compassion is the proposed direction."),
    ("PURE-FAM-05", "IPIP100:B5:A", "STRONG_FAMILY_MATCH", "Broad Agreeableness covers prosocial care, support, altruism, and deference, while optimism and relaxed positive affect are not specific to the domain.", "benevolent;nurturing;supportive;deferential;altruistic", "optimistic;chill;inspirational", "Higher Agreeableness is the proposed direction."),
    ("PURE-FAM-05", "IPIPneo:A3:AL", "FACET_OR_SUBCOMPONENT", "Altruism measures active concern and helping, a narrow central component of benevolent and supportive care.", "benevolent;nurturing;supportive;altruistic", "deferential;optimistic;chill;inspirational", "Higher Altruism is the proposed direction."),
    ("PURE-FAM-05", "IPIPneo:E6:CH", "FACET_OR_SUBCOMPONENT", "Cheerfulness measures the optimistic, relaxed positive-affect component without indexing nurturing or altruism.", "optimistic;chill;inspirational", "benevolent;nurturing;supportive;deferential;altruistic", "Higher Cheerfulness is the proposed direction."),
    # Inward/theoretical/ritual-principled family.
    ("PURE-FAM-06", "IPIP100:B5:E", "PARTIAL_FAMILY_MATCH", "Low Extraversion represents the introverted and inward pole, but does not measure abstract theory, ritual, reverence, or principle.", "introverted;pensive;solemn", "ritualistic;theoretical;abstract;reverent;conceptual;principled;erudite", "Lower Extraversion is the proposed direction."),
    ("PURE-FAM-06", "BFAS:BFAS:O:I", "PARTIAL_FAMILY_MATCH", "Intellect captures theoretical, abstract, conceptual, and erudite thought but not introversion, ritual, reverence, or solemnity.", "theoretical;abstract;conceptual;erudite;pensive", "introverted;ritualistic;reverent;principled;solemn", "Higher Intellect is the proposed direction."),
    ("PURE-FAM-06", "MPQ:MPQ:TR", "PARTIAL_FAMILY_MATCH", "Traditionalism measures conventional, principled, and religiously or socially conservative orientation, approximating ritual and reverence but not abstract thought.", "ritualistic;reverent;principled;solemn", "introverted;pensive;theoretical;abstract;conceptual;erudite", "Higher Traditionalism is the proposed direction."),
    # Experiential/practical/inquisitive family.
    ("PURE-FAM-11", "HEXACO:H:O:I", "PARTIAL_FAMILY_MATCH", "Inquisitiveness directly measures curiosity and active information seeking, but practical and experience-based application are not central to the scale.", "inquisitive;experiential", "practical", "Higher Inquisitiveness is the proposed direction."),
    ("PURE-FAM-11", "IPIPneo:O4:AD", "PARTIAL_FAMILY_MATCH", "Adventurousness captures willingness to seek varied direct experience but not practical reasoning or intellectual inquiry by itself.", "experiential;inquisitive", "practical", "Higher Adventurousness is the proposed direction."),
    # Explicit empirical/analytic family.
    ("PURE-FAM-12", "BFAS:BFAS:O:I", "PARTIAL_FAMILY_MATCH", "Intellect captures analytical, quantitative, educational, rational, and problem-solving capacity or engagement, but not transparent/factual communication, secularism, or utilitarianism.", "analytical;educational;quantitative;rationalist;problem_solving;data_driven", "transparent;factual;methodical;secular;utilitarian;cautious", "Higher Intellect is the proposed direction."),
    ("PURE-FAM-12", "IPIPneo:C6:CA", "FACET_OR_SUBCOMPONENT", "Cautiousness measures deliberation and prudence, covering the cautious and methodical edge but not the family's epistemic and communicative center.", "cautious;methodical", "transparent;factual;analytical;secular;data_driven;rationalist;educational;quantitative;utilitarian;problem_solving", "Higher Cautiousness is the proposed direction."),
    ("PURE-FAM-12", "BFAS:BFAS:C:O", "FACET_OR_SUBCOMPONENT", "Orderliness captures methodical structure and organization but not factuality, quantitative reasoning, or transparency.", "methodical", "transparent;factual;analytical;secular;data_driven;rationalist;educational;quantitative;utilitarian;cautious;problem_solving", "Higher Orderliness is the proposed direction."),
    ("PURE-FAM-12", "HEXACO:H:H:S", "FACET_OR_SUBCOMPONENT", "Sincerity is a limited human analogue for transparent and non-obscuring interpersonal presentation; it does not measure clarity, analysis, or empirical reasoning.", "transparent", "factual;analytical;methodical;secular;data_driven;rationalist;educational;quantitative;utilitarian;cautious;problem_solving", "Higher Sincerity is the proposed direction."),
    ("PURE-FAM-12", "ITEM:q_660", "ITEM_LEVEL_ONLY", "The exact item 'Don't consider myself religious' supplies a narrow indicator related to secular self-description, but no multi-item human construct in the library represents secular empirical communication as a whole.", "secular", "transparent;factual;analytical;methodical;data_driven;rationalist;educational;quantitative;utilitarian;cautious;problem_solving", "Higher endorsement is the proposed same-direction indicator for secular self-description."),
]

SEMANTIC_SHIFT = {
    ("PC1", "positive"): "Narrows from a broad regulated/stable family to explicit empirical-analytic communication and problem solving; broad Conscientiousness/Stability coverage is reduced.",
    ("PC1", "negative"): "Retains the expressive-symbolic and imaginative center while dropping much of the antagonistic and Big-Five-like cross-loading tail.",
    ("PC2", "positive"): "Contracts to experiential, practical inquiry; sociability, emotionality, and adaptability cross-loaders no longer define the counterpart set.",
    ("PC2", "negative"): "Retains abstract inward contemplation plus ritual/principle, with technical, antagonistic, and PC1-regulation cross-loaders removed.",
    ("PC3", "positive"): "Narrows to low-Agreeableness callous/cynical dominance and pessimism; generic rebellious/competitive PC1 cross-loaders are removed.",
    ("PC3", "negative"): "Narrows to prosocial care/support plus optimism; some generic Agreeableness and calmness indicators fail axis specificity despite remaining conceptually adjacent.",
    ("PC4", "positive"): "No primary marker survives; prior partial human mapping is not carried forward.",
    ("PC4", "negative"): "No primary marker survives; prior systems/holism-related partial mappings are not carried forward.",
    ("PC5", "positive"): "The prior divergent singleton is target-dominant but diffuse, so its human counterpart is not retained as a primary pure-family match.",
    ("PC5", "negative"): "Both prior and filtered families are empty.",
    ("PC6", "positive"): "Both prior and filtered families are empty.",
    ("PC6", "negative"): "The prior systems-thinking singleton is more strongly associated with PC4, so its human counterparts are not retained for PC6.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_key(path: Path, repo: Path) -> str:
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return f"temporary_output/{path.name}"


def item_wording(item_ids: str, items: pd.DataFrame) -> str:
    lookup = items.set_index("item_id")["item_text"].to_dict()
    ids = [item for item in str(item_ids).split(";") if item]
    missing = sorted(set(ids) - set(lookup))
    if missing:
        raise ValueError(f"Unknown SAPA items: {missing}")
    return json.dumps([{"item_id": item, "item_wording": lookup[item]} for item in ids], separators=(",", ":"))


def build_judgments(library: pd.DataFrame, items: pd.DataFrame, packet: pd.DataFrame) -> pd.DataFrame:
    lib = library.set_index("construct_id")
    rows: list[dict[str, object]] = []
    for family_id, construct_id, status, rationale, covered, uncovered, direction in JUDGMENTS:
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status {status}")
        if family_id not in set(packet["family_id"]):
            raise ValueError(f"Unknown neutral family {family_id}")
        if construct_id.startswith("ITEM:"):
            item_ids = construct_id.split(":", 1)[1]
            item_row = items.set_index("item_id").loc[item_ids]
            record = {
                "human_construct_name": f"Individual item: {item_row['item_text']}",
                "framework": "SAPA individual item",
                "domain": "item-level evidence",
                "level": "item",
                "construct_definition": item_row["item_text"],
                "SAPA_scale_or_key": "",
                "item_ids": item_ids,
                "item_count": 1,
                "library_scoring_direction": "raw item direction; no multi-item key",
                "item_valid_n_min": item_row["valid_response_n"],
                "item_valid_n_median": item_row["valid_response_n"],
                "item_valid_n_max": item_row["valid_response_n"],
                "pairwise_standardized_alpha": "",
                "reliability_note": "Single item; internal reliability is not estimable.",
                "source_provenance": "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv",
            }
        elif construct_id:
            if construct_id not in lib.index:
                raise ValueError(f"Unknown construct {construct_id}")
            source = lib.loc[construct_id]
            record = {
                "human_construct_name": source["construct_name"],
                "framework": source["framework"],
                "domain": source["domain"],
                "level": source["construct_level"],
                "construct_definition": source["construct_definition"],
                "SAPA_scale_or_key": source["official_scoring_key"],
                "item_ids": source["item_ids"],
                "item_count": int(source["source_item_count"]),
                "library_scoring_direction": source["scoring_direction"],
                "item_valid_n_min": source["item_valid_n_min"],
                "item_valid_n_median": source["item_valid_n_median"],
                "item_valid_n_max": source["item_valid_n_max"],
                "pairwise_standardized_alpha": source["sapa_pairwise_standardized_alpha"],
                "reliability_note": source["reliability_note"],
                "source_provenance": source["source_citation"],
            }
        else:
            record = {
                "human_construct_name": "No defensible SAPA counterpart",
                "framework": "",
                "domain": "",
                "level": "none",
                "construct_definition": "",
                "SAPA_scale_or_key": "",
                "item_ids": "",
                "item_count": 0,
                "library_scoring_direction": "",
                "item_valid_n_min": "",
                "item_valid_n_median": "",
                "item_valid_n_max": "",
                "pairwise_standardized_alpha": "",
                "reliability_note": "",
                "source_provenance": "",
            }
        rows.append(
            {
                "family_id": family_id,
                "human_construct_id": construct_id,
                "match_status": status,
                "match_rationale": rationale,
                "covered_axis_specific_markers": covered,
                "important_uncovered_axis_specific_markers": uncovered,
                "measurement_direction": direction,
                **record,
            }
        )
    frame = pd.DataFrame(rows).sort_values(["family_id", "match_status", "human_construct_id"], kind="mergesort")
    frame["item_wording_json"] = [item_wording(value, items) if value else "[]" for value in frame["item_ids"]]

    overlaps: list[str] = []
    overlap_flags: list[bool] = []
    item_sets = [set(str(value).split(";")) - {""} for value in frame["item_ids"]]
    for index, left in enumerate(item_sets):
        records = []
        for other_index, right in enumerate(item_sets):
            if index == other_index or not left or not right:
                continue
            shared = left & right
            if shared:
                union = left | right
                records.append(
                    f"{frame.iloc[other_index]['family_id']}/{frame.iloc[other_index]['human_construct_id']}:"
                    f"shared={len(shared)},jaccard={len(shared)/len(union):.3f}"
                )
        overlaps.append(";".join(records))
        overlap_flags.append(any(len(left & right) / len(left | right) >= 0.25 for j, right in enumerate(item_sets) if j != index and left and right))
    frame["overlap_with_other_proposed_human_constructs"] = overlaps
    frame["substantial_item_overlap"] = overlap_flags
    frame["candidate_universe"] = "full documented 126-construct SAPA human_construct_library.csv plus item-level fallback"
    frame["epistemic_status"] = "INTERPRETATION_OF_AVAILABLE_SAPA_MEASUREMENT; HUMAN_MODEL_EQUIVALENCE_NOT_TESTED"
    return frame


def main(repo: Path, output: Path) -> None:
    packet_path = output / "qwen_axis_specific_human_mapping_packet.csv"
    packet_manifest_path = output / "qwen_axis_specific_human_mapping_packet_manifest.json"
    library_path = repo / "research/outputs/qwen_pc_human_construct_bridge/human_construct_library.csv"
    item_path = repo / "research/outputs/human_trait_dataset_feasibility/sapa/sapa_item_dictionary.csv"
    marker_path = output / "qwen_axis_specific_marker_sets.csv"
    comparison_path = output / "qwen_axis_specific_family_comparison.csv"
    prior_inventory_path = repo / "research/outputs/qwen_trait_family_human_inventory/qwen_pc_trait_family_human_inventory.csv"

    packet = pd.read_csv(packet_path)
    packet_manifest = json.loads(packet_manifest_path.read_text(encoding="utf-8"))
    library = pd.read_csv(library_path).fillna("")
    items = pd.read_csv(item_path).fillna("")
    markers = pd.read_csv(marker_path).fillna("")
    family_summary = pd.read_csv(comparison_path).fillna("")
    prior = pd.read_csv(prior_inventory_path).fillna("")
    if len(packet) != 12 or len(library) != 126:
        raise ValueError("Packet/library row-count drift")

    judgments = build_judgments(library, items, packet)
    judgments.to_csv(output / "qwen_axis_specific_human_mapping_judgments.csv", index=False)

    hidden = pd.DataFrame(packet_manifest["family_key_not_reviewer_facing"])
    unblinded = judgments.merge(packet, on="family_id", validate="many_to_one").merge(
        hidden, on=["family_id", "axis_specific_marker_count"], validate="many_to_one"
    )
    family_fields = family_summary[
        [
            "pc",
            "pole",
            "axis_status",
            "original_association_family_size",
            "axis_specific_marker_count",
            "retention_percentage",
            "retained_traits",
        ]
    ]
    unblinded = unblinded.merge(
        family_fields,
        on=["pc", "pole", "axis_specific_marker_count"],
        validate="many_to_one",
    )
    unblinded["observed_marker_evidence"] = "OBSERVED_SAME_SPACE_QWEN_PC1_PC6_CORRELATION_AND_SPECIFICITY"
    unblinded["family_description_status"] = "INTERPRETATION_FROM_PRIMARY_AXIS_SPECIFIC_MARKERS"
    unblinded["human_mapping_status"] = "INTERPRETATION_OF_AVAILABLE_SAPA_MEASUREMENT"
    unblinded["shared_latent_property_status"] = "HYPOTHESIS_NOT_TESTED"
    unblinded["human_model_equivalence_status"] = "UNKNOWN_NOT_TESTED"
    leading = [
        "pc",
        "axis_status",
        "pole",
        "family_id",
        "original_association_family_size",
        "axis_specific_marker_count",
        "retention_percentage",
        "axis_specific_marker_names",
        "marker_evidence_json",
        "strongest_marker",
        "purest_marker",
        "marker_derived_family_description",
    ]
    remaining = [column for column in unblinded.columns if column not in leading]
    unblinded = unblinded[leading + remaining].sort_values(
        ["pc", "pole", "match_status", "human_construct_id"], kind="mergesort"
    )
    unblinded.to_csv(output / "qwen_axis_specific_human_inventory.csv", index=False)

    comparison_rows = []
    for pc in [f"PC{i}" for i in range(1, 7)]:
        for pole in ["positive", "negative"]:
            old = prior[(prior["pc"] == pc) & (prior["pole"] == pole)]
            new = unblinded[(unblinded["pc"] == pc) & (unblinded["pole"] == pole)]
            old_real = old[old["human_construct_id"] != ""]
            new_real = new[new["human_construct_id"] != ""]
            old_ids = set(old_real["human_construct_id"])
            new_ids = set(new_real["human_construct_id"])
            old_status = old_real.set_index("human_construct_id")["match_status"].to_dict()
            new_status = new_real.set_index("human_construct_id")["match_status"].to_dict()
            status_changes = [
                f"{construct}:{old_status[construct]}->{new_status[construct]}"
                for construct in sorted(old_ids & new_ids)
                if old_status[construct] != new_status[construct]
            ]
            old_items = set(";".join(old_real["item_ids"]).split(";")) - {""}
            new_items = set(";".join(new_real["item_ids"]).split(";")) - {""}
            family_row = family_summary[(family_summary["pc"] == pc) & (family_summary["pole"] == pole)].iloc[0]
            old_description = old.iloc[0]["family_description"] if len(old) else ""
            new_description = new.iloc[0]["marker_derived_family_description"] if len(new) else ""
            comparison_rows.append(
                {
                    "pc": pc,
                    "pole": pole,
                    "original_association_family_size": int(family_row["original_association_family_size"]),
                    "axis_specific_marker_count": int(family_row["axis_specific_marker_count"]),
                    "prior_candidate_construct_count": len(old_ids),
                    "axis_specific_candidate_construct_count": len(new_ids),
                    "constructs_retained": ";".join(sorted(old_ids & new_ids)),
                    "constructs_dropped": ";".join(sorted(old_ids - new_ids)),
                    "constructs_newly_selected": ";".join(sorted(new_ids - old_ids)),
                    "match_status_changes": ";".join(status_changes),
                    "prior_unique_item_count": len(old_items),
                    "axis_specific_unique_item_count": len(new_items),
                    "item_count_change": len(new_items) - len(old_items),
                    "prior_family_description": old_description,
                    "axis_specific_family_description": new_description,
                    "major_semantic_shift": SEMANTIC_SHIFT[(pc, pole)],
                }
            )
    comparison = pd.DataFrame(comparison_rows)
    comparison.to_csv(output / "prior_vs_axis_specific_human_inventory_comparison.csv", index=False)

    manifest_path = output / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["human_mapping"] = {
        "judgments_frozen_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mapping_spec_frozen_commit": "0545130",
        "neutral_packet_seed": packet_manifest["packet_seed"],
        "candidate_universe_count": len(library),
        "judgment_rows": len(judgments),
        "nonempty_marker_families": int((packet["axis_specific_marker_count"] > 0).sum()),
        "empty_marker_families": int((packet["axis_specific_marker_count"] == 0).sum()),
        "prior_mapping_used_during_adjudication": False,
        "prior_inventory_loaded_only_after_judgments_were_encoded": True,
    }
    for path in [packet_path, packet_manifest_path, library_path, item_path, prior_inventory_path]:
        manifest["source_hashes"][manifest_key(path, repo)] = sha256(path)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "judgment_rows": len(judgments),
                "status_counts": judgments["match_status"].value_counts().sort_index().to_dict(),
                "unique_constructs": judgments.loc[judgments["human_construct_id"] != "", "human_construct_id"].nunique(),
                "unique_items": len(set(";".join(judgments["item_ids"]).split(";")) - {""}),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    main(args.repo_root.resolve(), args.output_dir.resolve())
