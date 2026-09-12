#!/usr/bin/env python3
"""Build the independent-review agreement and flagged-item quality audit.

This script treats the user-supplied Claude CSV and the frozen Codex review as
immutable inputs. It does not load persona geometry, model coefficients, model
vectors, occupation data, or respondent-level human data.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score


REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "research/outputs/qwen_pc_human_construct_bridge"
CLAUDE_PATH = OUT / "sapa_category3_blinded_review_judgments.csv"
CODEX_PATH = (
    REPO
    / "research/outputs/human_trait_dataset_feasibility/sapa_review/"
    "sapa_category3_second_pass_review.csv"
)
PACKET_PATH = (
    REPO
    / "research/outputs/human_trait_dataset_feasibility/sapa_review/"
    "sapa_category3_blinded_review_packet.csv"
)
ITEM_DICTIONARY_PATH = (
    REPO
    / "research/outputs/human_trait_dataset_feasibility/sapa/"
    "sapa_item_dictionary.csv"
)
RAW_ITEM_INFO_PATH = (
    REPO
    / "data_external/human_validation/sapa/doi_10.7910_DVN_SD7SVE/"
    "ItemInfo696.csv"
)

DECISIONS = [
    "ACCEPT_DIRECT",
    "ACCEPT_CLOSE",
    "DOWNGRADE_BROAD",
    "REJECT",
    "AMBIGUOUS",
]
ORDINAL_DECISIONS = ["REJECT", "DOWNGRADE_BROAD", "ACCEPT_CLOSE", "ACCEPT_DIRECT"]
FLAGGED_ITEMS = [
    "q_251",
    "q_1483",
    "q_1671",
    "q_1758",
    "q_566",
    "q_463",
    "q_1742",
    "q_1624",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_ids(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(";") if part.strip()]


def proportion(a: pd.Series, b: pd.Series) -> float:
    return float((a == b).mean())


def build_agreement() -> None:
    claude = pd.read_csv(CLAUDE_PATH)
    codex = pd.read_csv(CODEX_PATH)
    packet = pd.read_csv(PACKET_PATH)

    required = {
        "review_id",
        "trait",
        "decision",
        "rationale",
        "evidence_item_ids",
        "evidence_scale_names",
        "single_or_multi_item",
        "reverse_direction_issue",
        "construct_boundary_note",
        "rubric_version",
        "review_date",
        "reviewer",
    }
    if not required.issubset(claude.columns):
        raise ValueError(f"Claude CSV lacks fields: {sorted(required - set(claude.columns))}")
    for name, frame in (("Claude", claude), ("Codex", codex), ("packet", packet)):
        if len(frame) != 78 or frame["review_id"].nunique() != 78:
            raise ValueError(f"{name} must contain exactly 78 unique review IDs")
    if set(claude["review_id"]) != set(codex["review_id"]) or set(claude["review_id"]) != set(
        packet["review_id"]
    ):
        raise ValueError("Review-ID sets differ")
    if not set(claude["decision"]).issubset(DECISIONS):
        raise ValueError("Unexpected Claude decision")
    if not set(codex["decision"]).issubset(DECISIONS):
        raise ValueError("Unexpected Codex decision")

    joined = codex.merge(
        claude,
        on=["review_id", "trait"],
        validate="one_to_one",
        suffixes=("_codex", "_claude"),
    )
    if len(joined) != 78:
        raise ValueError("Trait labels do not align one-to-one")

    exact = joined["decision_codex"] == joined["decision_claude"]
    retained_codex = joined["decision_codex"].isin(["ACCEPT_DIRECT", "ACCEPT_CLOSE"])
    retained_claude = joined["decision_claude"].isin(["ACCEPT_DIRECT", "ACCEPT_CLOSE"])
    direct_codex = joined["decision_codex"].eq("ACCEPT_DIRECT")
    direct_claude = joined["decision_claude"].eq("ACCEPT_DIRECT")

    confusion = pd.crosstab(
        pd.Categorical(joined["decision_codex"], categories=DECISIONS),
        pd.Categorical(joined["decision_claude"], categories=DECISIONS),
        dropna=False,
    )
    confusion.index.name = "codex_decision"
    confusion.columns.name = "claude_decision"
    confusion.reset_index().to_csv(OUT / "external_review_confusion_matrix.csv", index=False)

    disagreement_columns = [
        "review_id",
        "trait",
        "decision_codex",
        "decision_claude",
        "rationale_codex",
        "rationale_claude",
        "evidence_item_ids_codex",
        "evidence_item_ids_claude",
        "construct_boundary_note_codex",
        "construct_boundary_note_claude",
    ]
    joined.loc[~exact, disagreement_columns].to_csv(
        OUT / "external_review_disagreements.csv", index=False
    )

    consensus = joined[
        ["review_id", "trait", "decision_codex", "decision_claude"]
    ].copy()
    consensus["agreement"] = exact
    consensus["consensus_category"] = joined["decision_codex"].where(exact, "")
    consensus["consensus_status"] = "DISCORDANT"
    consensus.loc[exact & joined["decision_codex"].eq("ACCEPT_DIRECT"), "consensus_status"] = (
        "CONSENSUS_DIRECT"
    )
    consensus.loc[exact & joined["decision_codex"].eq("ACCEPT_CLOSE"), "consensus_status"] = (
        "CONSENSUS_CLOSE"
    )
    consensus.loc[
        exact & joined["decision_codex"].isin(["DOWNGRADE_BROAD", "REJECT", "AMBIGUOUS"]),
        "consensus_status",
    ] = "CONSENSUS_NONRETAIN"
    consensus["status_boundary"] = (
        "Descriptive two-AI semantic consensus; not expert psychometric validation"
    )
    consensus.to_csv(OUT / "sapa_semantic_consensus_v1.csv", index=False)

    ordinal_mask = ~joined["decision_codex"].eq("AMBIGUOUS") & ~joined[
        "decision_claude"
    ].eq("AMBIGUOUS")
    ordinal = joined.loc[ordinal_mask]
    summary = {
        "analysis": "Claude-versus-Codex blinded semantic-review agreement",
        "n": int(len(joined)),
        "claude_input_sha256": sha256(CLAUDE_PATH),
        "codex_input_sha256": sha256(CODEX_PATH),
        "frozen_packet_sha256": sha256(PACKET_PATH),
        "decision_order_for_tables": DECISIONS,
        "claude_decision_counts": {
            key: int((joined["decision_claude"] == key).sum()) for key in DECISIONS
        },
        "codex_decision_counts": {
            key: int((joined["decision_codex"] == key).sum()) for key in DECISIONS
        },
        "exact_five_category_agreement_n": int(exact.sum()),
        "exact_five_category_agreement": proportion(
            joined["decision_codex"], joined["decision_claude"]
        ),
        "cohens_kappa_unweighted_five_category": float(
            cohen_kappa_score(
                joined["decision_codex"], joined["decision_claude"], labels=DECISIONS
            )
        ),
        "weighted_kappa_primary_status": (
            "not_defensible_for_all_five_categories_because_AMBIGUOUS_is_not_ordinal"
        ),
        "weighted_kappa_ordinal_sensitivity": {
            "excluded_any_AMBIGUOUS_rows": int((~ordinal_mask).sum()),
            "n": int(len(ordinal)),
            "ordered_categories_low_to_high": ORDINAL_DECISIONS,
            "linear": float(
                cohen_kappa_score(
                    ordinal["decision_codex"],
                    ordinal["decision_claude"],
                    labels=ORDINAL_DECISIONS,
                    weights="linear",
                )
            ),
            "quadratic": float(
                cohen_kappa_score(
                    ordinal["decision_codex"],
                    ordinal["decision_claude"],
                    labels=ORDINAL_DECISIONS,
                    weights="quadratic",
                )
            ),
        },
        "binary_retained_status": {
            "definition": "ACCEPT_DIRECT or ACCEPT_CLOSE versus all other decisions",
            "agreement_n": int((retained_codex == retained_claude).sum()),
            "agreement": proportion(retained_codex, retained_claude),
            "cohens_kappa": float(cohen_kappa_score(retained_codex, retained_claude)),
        },
        "direct_status": {
            "definition": "ACCEPT_DIRECT versus all other decisions",
            "agreement_n": int((direct_codex == direct_claude).sum()),
            "agreement": proportion(direct_codex, direct_claude),
            "cohens_kappa": float(cohen_kappa_score(direct_codex, direct_claude)),
        },
        "disagreement_n": int((~exact).sum()),
        "consensus_status_counts": {
            key: int((consensus["consensus_status"] == key).sum())
            for key in [
                "CONSENSUS_DIRECT",
                "CONSENSUS_CLOSE",
                "CONSENSUS_NONRETAIN",
                "DISCORDANT",
            ]
        },
        "epistemic_status": (
            "Two AI semantic reviews, one genuinely separate and blinded as documented; "
            "not independent expert psychometric validation"
        ),
    }
    (OUT / "external_review_agreement_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )

    reviewer_metadata = {
        "reviewer": "Claude Opus 5",
        "provider": "Anthropic",
        "review_date": "2026-09-11",
        "review_file": str(CLAUDE_PATH.relative_to(REPO)),
        "review_file_sha256": sha256(CLAUDE_PATH),
        "review_rows": 78,
        "prior_substantive_project_knowledge": "none reported",
        "materials_located_by_reviewer": (
            "Only the three requested review files; no project-state or downstream-result files"
        ),
        "prohibited_information_reported_visible": False,
        "files_reported_not_inspected": [
            "RESEARCH_STATE",
            "claims",
            "geometry",
            "prior review decisions",
            "sparsity results",
            "occupations",
            "NLSY97 outcomes",
            "downstream analyses",
        ],
        "structural_conflict": (
            "Claude is an Anthropic-produced AI system; this is a potential structural conflict"
        ),
        "reviewer_reported_limitations": [
            "q_251 wording was elided",
            "q_1483 and q_1671 appeared bracketed or paraphrased",
            "No prose scale definitions accompanied SAPA scale metadata",
            "Direction metadata appeared inconsistent for q_1758, q_566, q_463, q_1742, and q_1624",
            "Several traits used identical or near-identical evidence sets",
            "The review is content adjudication, not psychometric validation",
        ],
        "current_workflow_model_used": "GPT-5.5",
        "current_workflow_external_model_api_used": False,
    }
    (OUT / "external_review_reviewer_metadata.json").write_text(
        json.dumps(reviewer_metadata, indent=2) + "\n", encoding="utf-8"
    )


def build_flagged_item_audit() -> None:
    dictionary = pd.read_csv(ITEM_DICTIONARY_PATH)
    item_info = pd.read_csv(RAW_ITEM_INFO_PATH, encoding="latin1").rename(
        columns={"Unnamed: 0": "item_id", "Item": "raw_release_wording"}
    )
    packet = pd.read_csv(PACKET_PATH)
    dictionary = dictionary.set_index("item_id", drop=False)
    item_info = item_info.set_index("item_id", drop=False)

    corrected_wording = {
        "q_251": "Am seldom bothered by the apparent suffering of strangers.",
        "q_1483": "Often forget to put things back in their proper place.",
        "q_1671": "Enjoy interactions less than others.",
    }
    wording_source = {
        "q_251": "https://ipip.ori.org/AlphabeticalItemList.htm",
        "q_1483": "https://ipip.ori.org/newBigFive5broadKey.htm",
        "q_1671": "https://www.sapa-project.org/research/SPI/SPIdevelopment.pdf",
    }
    verified_direction_by_item_trait = {
        "q_251": {"cruel": "same", "callous": "same"},
        "q_1483": {"disorganized": "same"},
        "q_1671": {"avoidant": "same"},
        "q_1758": {"naive": "reverse", "paranoid": "same"},
        "q_566": {"adaptable": "reverse"},
        "q_463": {"independent": "reverse", "gregarious": "same"},
        "q_1742": {
            "extroverted": "same",
            "reserved": "reverse",
            "gregarious": "same",
        },
        "q_1624": {"deferential": "same", "reverent": "same", "rebellious": "reverse"},
    }
    direction_adequate = {
        "q_251": True,
        "q_1483": True,
        "q_1671": True,
        "q_1758": False,
        "q_566": False,
        "q_463": False,
        "q_1742": False,
        "q_1624": False,
    }

    rows = []
    for item_id in FLAGGED_ITEMS:
        if item_id not in dictionary.index or item_id not in item_info.index:
            raise ValueError(f"Flagged item missing from sources: {item_id}")
        affected = packet[
            packet["evidence_item_ids"].fillna("").map(lambda x: item_id in split_ids(x))
        ]
        committed_direction = ";".join(
            f"{row.trait}:{row.item_scoring_direction_metadata}"
            for row in affected.itertuples(index=False)
        )
        verified_direction = ";".join(
            f"{trait}:{direction}"
            for trait, direction in verified_direction_by_item_trait[item_id].items()
        )
        raw_wording = str(item_info.loc[item_id, "raw_release_wording"])
        future_wording = corrected_wording.get(item_id, raw_wording)
        wording_exact = str(dictionary.loc[item_id, "item_text"]) == future_wording
        if item_id == "q_1671":
            action = (
                "Preserve the historical source-bracketed wording; future metadata may remove "
                "brackets only and must retain a source-qualified wording flag"
            )
        elif item_id in corrected_wording:
            action = (
                "Use the authoritative full wording in corrected derivative metadata; do not "
                "rewrite frozen historical review packets"
            )
        elif direction_adequate[item_id]:
            action = "No wording correction; retain trait-specific orientation in future analyses"
        else:
            action = (
                "Replace row-level same_direction shorthand with trait-specific item orientation "
                "in future derivative metadata; keep historical packets frozen"
            )
        rows.append(
            {
                "item_id": item_id,
                "committed_wording": dictionary.loc[item_id, "item_text"],
                "primary_source_wording": raw_wording,
                "corrected_future_wording": future_wording,
                "wording_exact": wording_exact,
                "committed_direction": committed_direction,
                "verified_direction": verified_direction,
                "direction_match": direction_adequate[item_id],
                "affected_traits": ";".join(affected["trait"].tolist()),
                "action_required": action,
                "source_file": str(RAW_ITEM_INFO_PATH.relative_to(REPO)),
                "source_hash": sha256(RAW_ITEM_INFO_PATH),
                "authoritative_wording_source": wording_source.get(item_id, "official SAPA V5 ItemInfo696.csv"),
            }
        )
    audit = pd.DataFrame(rows)
    audit.to_csv(OUT / "sapa_flagged_item_quality_audit.csv", index=False)

    log = f"""# SAPA metadata correction log

Generated by `scripts/build_external_review_audit.py` from the frozen review packet, the committed item dictionary, and the official SAPA V5 `ItemInfo696.csv`.

## Historical-artifact policy

The frozen Codex packet, frozen external-review packet, and user-supplied Claude judgments remain unchanged. Corrections apply only to future derivative metadata.

## Wording findings

- `q_251`: the SAPA V5 source itself elides the sentence. The official IPIP item list supplies **“Am seldom bothered by the apparent suffering of strangers.”** Future derivatives use that complete wording and cite the IPIP list.
- `q_1483`: the SAPA V5 source uses a bracketed shortening. Official IPIP keys supply **“Often forget to put things back in their proper place.”** Future derivatives use the full item.
- `q_1671`: the SAPA V5 source and official SAPA SPI-development document both preserve the bracketed phrase **“[Enjoy interactions less than others].”** No longer wording was provenance-verified. Future derivatives may remove the source brackets for display but must label the wording source-qualified rather than independently recovered.

## Direction findings

The historical packet's row-level `same_direction` field was too coarse for evidence sets containing traits with opposite poles. Future derivative metadata uses item-by-trait orientations:

- `q_1758`: reverse for `naive`; same for `paranoid`.
- `q_566`: reverse for `adaptable`.
- `q_463`: reverse for `independent`; same for `gregarious`.
- `q_1742`: same for `extroverted` and `gregarious`; reverse for `reserved`.
- `q_1624`: same for `deferential` and `reverent`; reverse for `rebellious`.

These are semantic orientation corrections for future bridge construction. They do not alter official SAPA scale-key signs recorded in `superKey696.csv`.

## Sources

- SAPA V5: https://doi.org/10.7910/DVN/SD7SVE
- IPIP alphabetical item list: https://ipip.ori.org/AlphabeticalItemList.htm
- IPIP Big-Five factor markers: https://ipip.ori.org/newBigFive5broadKey.htm
- SAPA SPI development document: https://www.sapa-project.org/research/SPI/SPIdevelopment.pdf
"""
    (OUT / "sapa_metadata_correction_log.md").write_text(log, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_agreement()
    build_flagged_item_audit()
    print("Built external-review agreement and SAPA flagged-item quality audit.")


if __name__ == "__main__":
    main()
