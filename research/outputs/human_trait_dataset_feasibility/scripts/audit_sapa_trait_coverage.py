#!/usr/bin/env python3
"""Audit the official SAPA 696-item release against the canonical 240 traits.

This is a feasibility crosswalk, not a psychometric bridge.  Candidate generation
is deterministic and local; the checked-in category assignments are explicit
Codex review judgments that remain open to independent revision.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RELEASE_DOI = "doi:10.7910/DVN/SD7SVE"
RELEASE_URL = "https://doi.org/10.7910/DVN/SD7SVE"
DOWNLOAD_DATE = "2026-09-11"

# Explicit feasibility judgments. Any trait not listed is category 0. Categories
# are deliberately conservative: category 3 requires narrow, face-valid content;
# category 2 permits a neighboring narrow construct; category 1 is broad-domain
# content only. These lists cover all non-zero judgments and are validated below.
CATEGORY_3 = {
    "pessimistic", "rebellious", "dramatic", "innovative", "detached",
    "adventurous", "temperamental", "calm", "disorganized", "creative",
    "cautious", "optimistic", "methodical", "intuitive", "empathetic",
    "curious", "patient", "emotional", "artistic", "confident", "independent",
    "adaptable", "spontaneous", "traditional", "competitive", "risk_taking",
    "introspective", "extroverted", "perfectionist", "assertive", "playful",
    "conscientious", "agreeable", "dominant", "altruistic", "proactive",
    "confrontational", "accommodating", "passionate", "meticulous", "reserved",
    "mercurial", "deferential", "calculating", "bombastic", "gregarious",
    "acerbic", "stoic", "zealous", "nonchalant", "reverent", "cynical",
    "naive", "anxious", "serene", "forgiving", "vindictive", "spiritual",
    "secular", "neurotic", "resilient", "impulsive", "submissive", "paranoid",
    "grandiose", "melancholic", "avoidant", "sarcastic", "cruel",
    "manipulative", "callous", "hostile", "judgmental", "bitter", "goofy",
    "mischievous", "theatrical", "chill",
}

CATEGORY_2 = {
    "arrogant", "impatient", "sycophantic", "benevolent",
    "charismatic", "introverted", "passive_aggressive", "efficient",
    "circumspect", "principled", "analytical", "skeptical", "formal", "casual",
    "philosophical", "witty", "diplomatic", "supportive", "inquisitive",
    "idealistic", "humble", "collaborative", "flexible", "nurturing",
    "closure_seeking", "strategic", "regulatory", "reactive", "ritualistic",
    "improvisational", "solemn", "transparent", "effusive", "visceral",
    "iconoclastic", "conciliatory", "hedonistic", "misanthropic", "fundamentalist",
    "radical", "epicurean", "obsessive", "manic", "pedantic", "subversive",
    "formalist", "chaotic", "critical", "dogmatic",
}

CATEGORY_1 = {
    "meditative", "serious", "generous", "circumspect", "concise", "practical",
    "technical", "futuristic", "big_picture", "humanistic", "quantitative",
    "qualitative", "eclectic", "challenging", "theoretical", "experiential",
    "exploratory", "educational", "entertaining", "inspirational", "speculative",
    "individualistic", "collectivistic", "conceptual", "universalist", "whimsical",
    "eloquent", "animated", "pensive", "earnest", "tactful", "accessible",
    "grounded", "ascetic", "egalitarian", "romantic", "rationalist", "pluralist",
    "moderate", "systems_thinker", "structuralist", "edgy",
}

# Resolve intentional list conflicts toward the more specific category.
CATEGORY_1 -= CATEGORY_2 | CATEGORY_3
CATEGORY_2 -= CATEGORY_3

# Reviewed evidence anchors are inserted ahead of algorithmic candidates. IDs are
# exact release item IDs; their full wording and scale memberships are copied to
# the output, never paraphrased into invented definitions.
EVIDENCE_IDS = {
    "pessimistic": ["q_1038", "q_808"],
    "arrogant": ["q_364", "q_716", "q_1042"],
    "impatient": ["q_1330", "q_988", "q_4274"],
    "rebellious": ["q_1609", "q_1624"],
    "dramatic": ["q_2951"],
    "innovative": ["q_1392", "q_2745", "q_516"],
    "detached": ["q_1196", "q_1681"],
    "adventurous": ["q_1662", "q_2011"],
    "temperamental": ["q_52", "q_497", "q_1099"],
    "calm": ["q_85", "q_1616"],
    "sycophantic": ["q_1448", "q_917", "q_1894"],
    "benevolent": ["q_1385", "q_1763", "q_1041"],
    "charismatic": ["q_1045", "q_1055", "q_1742"],
    "introverted": ["q_241", "q_312", "q_4259"],
    "passive_aggressive": ["q_1467", "q_1543", "q_1151"],
    "efficient": ["q_988", "q_519"],
    "disorganized": ["q_1254", "q_1483", "q_1511"],
    "creative": ["q_2754", "q_2745", "q_1441"],
    "cautious": ["q_1781", "q_292", "q_2020"],
    "circumspect": ["q_507", "q_1477", "q_1521"],
    "principled": ["q_1752", "q_1812", "q_1633"],
    "analytical": ["q_1327", "q_423", "q_778"],
    "optimistic": ["q_1350", "q_1457", "q_1835"],
    "methodical": ["q_619", "q_1321", "q_1422"],
    "intuitive": ["q_1676"],
    "skeptical": ["q_1477", "q_126", "q_594"],
    "empathetic": ["q_844", "q_1763", "q_1757"],
    "curious": ["q_2775", "q_128", "q_1303"],
    "patient": ["q_278"],
    "formal": ["q_1301", "q_1657"],
    "casual": ["q_248", "q_4261"],
    "philosophical": ["q_322", "q_194", "q_1587"],
    "witty": ["q_4265", "q_158", "q_40"],
    "diplomatic": ["q_507", "q_1151", "q_253"],
    "supportive": ["q_1385", "q_1763", "q_1668"],
    "inquisitive": ["q_2775", "q_128", "q_778"],
    "emotional": ["q_1681", "q_793", "q_219"],
    "artistic": ["q_348", "q_610", "q_1441"],
    "idealistic": ["q_379", "q_343"],
    "humble": ["q_364", "q_716"],
    "confident": ["q_258", "q_820", "q_1055"],
    "collaborative": ["q_1910", "q_4264"],
    "independent": ["q_4244", "q_463"],
    "adaptable": ["q_38", "q_566"],
    "spontaneous": ["q_4276", "q_1488"],
    "traditional": ["q_82", "q_1301", "q_4291"],
    "competitive": ["q_1910"],
    "risk_taking": ["q_1781", "q_292", "q_1780"],
    "introspective": ["q_1880", "q_1310"],
    "extroverted": ["q_1742", "q_1803", "q_4257"],
    "perfectionist": ["q_1694", "q_530", "q_1915"],
    "flexible": ["q_997", "q_38"],
    "assertive": ["q_2161", "q_1768", "q_1769"],
    "nurturing": ["q_1385", "q_1763", "q_851"],
    "playful": ["q_4265", "q_1685", "q_1043"],
    "conscientious": ["q_1507", "q_1422", "q_491"],
    "agreeable": ["q_6", "q_1763", "q_1910"],
    "closure_seeking": ["q_469", "q_1521"],
    "dominant": ["q_1768", "q_1769", "q_2161"],
    "strategic": ["q_1321", "q_1422"],
    "altruistic": ["q_1385", "q_4229", "q_1764"],
    "proactive": ["q_1883", "q_4257"],
    "regulatory": ["q_1657", "q_1752"],
    "reactive": ["q_1599", "q_1601"],
    "ritualistic": ["q_1301", "q_1867"],
    "improvisational": ["q_131", "q_4276"],
    "confrontational": ["q_1051", "q_630"],
    "accommodating": ["q_6", "q_145", "q_1910"],
    "solemn": ["q_1685", "q_1043"],
    "passionate": ["q_228"],
    "meticulous": ["q_1063", "q_1507", "q_1915"],
    "transparent": ["q_1812", "q_1436"],
    "effusive": ["q_1681", "q_1703"],
    "reserved": ["q_1196", "q_1635", "q_1742"],
    "mercurial": ["q_52", "q_497", "q_1099"],
    "deferential": ["q_1624", "q_917"],
    "calculating": ["q_1896", "q_1765", "q_905"],
    "visceral": ["q_793", "q_1589"],
    "bombastic": ["q_1555", "q_1871"],
    "gregarious": ["q_463", "q_1742", "q_1803"],
    "acerbic": ["q_1051"],
    "stoic": ["q_1185", "q_1588", "q_1616"],
    "zealous": ["q_228"],
    "nonchalant": ["q_248", "q_4261"],
    "iconoclastic": ["q_1609", "q_4244"],
    "reverent": ["q_1624", "q_4236"],
    "conciliatory": ["q_1910", "q_145"],
    "cynical": ["q_594", "q_343", "q_381"],
    "naive": ["q_377", "q_1854", "q_1758"],
    "anxious": ["q_1989", "q_4249", "q_4256"],
    "serene": ["q_85", "q_1616", "q_1588"],
    "hedonistic": ["q_1043", "q_1371"],
    "forgiving": ["q_145", "q_915", "q_1869"],
    "vindictive": ["q_630", "q_1150"],
    "spiritual": ["q_345", "q_660"],
    "misanthropic": ["q_381", "q_594", "q_343"],
    "secular": ["q_660", "q_345"],
    "fundamentalist": ["q_345", "q_369", "q_4236"],
    "radical": ["q_566", "q_1609"],
    "epicurean": ["q_1043", "q_1371"],
    "neurotic": ["q_1989", "q_1099", "q_1578"],
    "resilient": ["q_1606", "q_1616"],
    "obsessive": ["q_1507", "q_1915"],
    "impulsive": ["q_22", "q_35", "q_636"],
    "submissive": ["q_2161", "q_1768"],
    "paranoid": ["q_1758", "q_880", "q_594"],
    "grandiose": ["q_364", "q_1042", "q_1830"],
    "melancholic": ["q_1706", "q_1578", "q_811"],
    "manic": ["q_1099", "q_279", "q_1393"],
    "avoidant": ["q_312", "q_901", "q_1671"],
    "sarcastic": ["q_1051", "q_4265"],
    "pedantic": ["q_1507", "q_1915", "q_1657"],
    "subversive": ["q_1609", "q_4244"],
    "formalist": ["q_1301", "q_1657", "q_1752"],
    "chaotic": ["q_22", "q_1254", "q_636"],
    "critical": ["q_238", "q_239"],
    "cruel": ["q_251", "q_4251", "q_4231"],
    "manipulative": ["q_1896", "q_1765", "q_905"],
    "callous": ["q_146", "q_251", "q_4231"],
    "dogmatic": ["q_345", "q_369", "q_689"],
    "hostile": ["q_1051", "q_630", "q_1150"],
    "judgmental": ["q_239", "q_238"],
    "bitter": ["q_848", "q_1150", "q_630"],
    "goofy": ["q_4265", "q_1685"],
    "mischievous": ["q_4251", "q_4265"],
    "theatrical": ["q_2951", "q_1555"],
    "chill": ["q_248", "q_820", "q_819"],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def lexical_forms(text: str) -> set[str]:
    """Return exact tokens plus a small deterministic lemma-like normalization."""
    forms: set[str] = set()
    for token in re.findall(r"[a-z]+", text.lower().replace("_", " ")):
        forms.add(token)
        if token.endswith("ies") and len(token) > 4:
            forms.add(token[:-3] + "y")
        elif token.endswith("ing") and len(token) > 5:
            forms.add(token[:-3])
        elif token.endswith("ed") and len(token) > 4:
            forms.add(token[:-2])
        elif token.endswith("s") and not token.endswith("ss") and len(token) > 3:
            forms.add(token[:-1])
    return forms


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def scales_for_row(row: pd.Series, instrument_cols: list[str]) -> list[str]:
    out: list[str] = []
    for instrument in instrument_cols:
        value = str(row[instrument]).strip()
        if value and value.upper() != "NULL" and value.lower() != "nan":
            out.append(f"{instrument}:{value}")
    return out


def direction_for(trait: str, wordings: list[str]) -> str:
    joined = " ".join(wordings).lower()
    reverse_markers = ("not ", "don't ", "do not ", "seldom ", "rarely ", "difficult", "lack ")
    if trait in {"cautious", "competitive", "submissive", "secular", "forgiving", "serene", "humble"}:
        return "mixed_same_and_reverse"
    if any(marker in joined for marker in reverse_markers):
        return "mixed_or_reverse_wording_review_required"
    return "same_direction"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--traits", type=Path, required=True)
    parser.add_argument("--generated-at", help="Optional fixed UTC timestamp for byte-reproducibility tests")
    args = parser.parse_args()

    raw = args.raw_dir.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    generated = args.generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    item_path = raw / "ItemInfo696.csv"
    key_path = raw / "superKey696.csv"
    tab_path = raw / "sapaTempData696items08dec2013thru26jul2014.tab"
    metadata_path = raw / "dataverse_metadata.json"
    list_path = raw / "ItemLists.csv"
    demographic_path = raw / "demographic codes.txt"
    required = [item_path, key_path, tab_path, metadata_path, list_path, demographic_path]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing SAPA source files: {missing}")

    traits: dict[str, str] = json.loads(args.traits.read_text(encoding="utf-8"))
    if len(traits) != 240 or len(set(traits)) != 240:
        raise ValueError("Canonical trait source must contain 240 unique names")
    if (CATEGORY_3 & CATEGORY_2) or (CATEGORY_3 & CATEGORY_1) or (CATEGORY_2 & CATEGORY_1):
        raise ValueError("Coverage category sets overlap")
    unknown_reviewed = (CATEGORY_3 | CATEGORY_2 | CATEGORY_1) - set(traits)
    if unknown_reviewed:
        raise ValueError(f"Reviewed names absent from canonical traits: {sorted(unknown_reviewed)}")

    info = pd.read_csv(item_path, encoding="latin-1", dtype=str).rename(columns=lambda x: x.strip())
    info = info.rename(columns={info.columns[0]: "item_id", "Item": "item_text"})
    instrument_cols = [c for c in info.columns if c not in {"item_id", "item_text"}]
    if len(info) != 696 or info["item_id"].nunique() != 696:
        raise ValueError("SAPA item dictionary is not 696 unique items")
    item_by_id = info.set_index("item_id")

    keys = pd.read_csv(key_path, encoding="latin-1", dtype=str).rename(columns={"Unnamed: 0": "item_id"})
    if keys.columns[0] != "item_id":
        keys = keys.rename(columns={keys.columns[0]: "item_id"})
    if keys["item_id"].nunique() != 696:
        raise ValueError("SAPA super-key item IDs are not unique")
    scoring_cols = list(keys.columns[1:])
    keys_by_id = keys.set_index("item_id")

    # Read actual respondent data and distinguish item columns from release-level
    # demographics/derived occupation variables.
    data = pd.read_csv(tab_path, sep="\t", na_values=["NA"], low_memory=False)
    item_cols = [c for c in data.columns if c.startswith("q_")]
    demographic_cols = [c for c in data.columns if c not in item_cols]
    if len(data) != 23679 or len(item_cols) != 696 or len(data.columns) != 719:
        raise ValueError(f"Unexpected SAPA dimensions: {data.shape}, item columns={len(item_cols)}")
    if set(item_cols) != set(info["item_id"]):
        raise ValueError("Item IDs differ between response data and ItemInfo696.csv")

    item_rows = []
    for _, row in info.iterrows():
        iid = row["item_id"]
        memberships = scales_for_row(row, instrument_cols)
        scoring = []
        reverse_scoring = []
        for scale in scoring_cols:
            val = pd.to_numeric(keys_by_id.loc[iid, scale], errors="coerce")
            if pd.notna(val) and float(val) != 0:
                scoring.append(scale)
                if float(val) < 0:
                    reverse_scoring.append(scale)
        valid_n = int(data[iid].notna().sum())
        item_rows.append({
            "item_id": iid,
            "item_text": row["item_text"],
            "source_scale_memberships": ";".join(memberships),
            "source_scale_membership_count": len(memberships),
            "derived_scoring_keys": ";".join(scoring),
            "reverse_keyed_in_derived_scales": ";".join(reverse_scoring),
            "response_min": 1,
            "response_max": 6,
            "response_anchors": "1=Very Inaccurate;6=Very Accurate",
            "valid_response_n": valid_n,
            "missing_n": len(data) - valid_n,
            "missing_fraction": round(1 - valid_n / len(data), 8),
        })
    pd.DataFrame(item_rows).to_csv(out / "sapa_item_dictionary.csv", index=False)

    scale_rows = []
    for instrument in instrument_cols:
        vals = sorted({str(v).strip() for v in info[instrument] if str(v).strip().upper() not in {"NULL", "NAN", ""}})
        for value in vals:
            members = info.loc[info[instrument] == value, "item_id"].tolist()
            scale_rows.append({
                "inventory_type": "administered_source_construct",
                "instrument": instrument,
                "scale_id": f"{instrument}:{value}",
                "scale_name": value,
                "item_count": len(members),
                "item_ids": ";".join(members),
                "key_source": "ItemInfo696.csv",
            })
    for scale in scoring_cols:
        numeric = pd.to_numeric(keys[scale], errors="coerce").fillna(0)
        members = keys.loc[numeric != 0, "item_id"].tolist()
        scale_rows.append({
            "inventory_type": "derived_scoring_key",
            "instrument": "SAPA Personality Inventory / superKey696",
            "scale_id": scale,
            "scale_name": scale,
            "item_count": len(members),
            "item_ids": ";".join(members),
            "key_source": "superKey696.csv",
        })
    scales_df = pd.DataFrame(scale_rows)
    scales_df.to_csv(out / "sapa_scale_inventory.csv", index=False)
    source_construct_count = int((scales_df.inventory_type == "administered_source_construct").sum())
    if source_construct_count != 92:
        raise ValueError(f"Expected 92 administered constructs; found {source_construct_count}")

    # Stage 1 token/lemma-lite candidate score and stage 2 deterministic local
    # word + character TF-IDF. No external API or learned remote model is used.
    names = list(traits)
    trait_queries = [f"{name.replace('_', ' ')} {traits[name]}" for name in names]
    item_texts = info["item_text"].fillna("").tolist()
    word_vec = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    word_mat = word_vec.fit_transform(item_texts + trait_queries)
    word_sim = cosine_similarity(word_mat[len(item_texts):], word_mat[:len(item_texts)])
    char_vec = TfidfVectorizer(lowercase=True, analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)
    char_mat = char_vec.fit_transform(item_texts + trait_queries)
    char_sim = cosine_similarity(char_mat[len(item_texts):], char_mat[:len(item_texts)])
    combined = 0.65 * word_sim + 0.35 * char_sim

    item_token_sets = [lexical_forms(str(t)) for t in item_texts]
    crosswalk_rows = []
    for i, name in enumerate(names):
        category = 3 if name in CATEGORY_3 else 2 if name in CATEGORY_2 else 1 if name in CATEGORY_1 else 0
        trait_tokens = lexical_forms(name)
        lexical_idx = sorted(
            range(len(item_texts)),
            key=lambda j: (len(trait_tokens & item_token_sets[j]), combined[i, j]),
            reverse=True,
        )[:5]
        semantic_idx = np.argsort(-combined[i])[:8].tolist()
        reviewed_ids = [iid for iid in EVIDENCE_IDS.get(name, []) if iid in item_by_id.index]
        candidate_ids = []
        for iid in reviewed_ids + [str(info.iloc[j]["item_id"]) for j in semantic_idx]:
            if iid not in candidate_ids:
                candidate_ids.append(iid)
        candidate_ids = candidate_ids[:8]

        # Positive evidence is restricted to reviewed anchors. For broad-only
        # rows we retain candidates but do not pretend they measure the narrow
        # construct. For category 0, all candidates are explicitly rejected.
        evidence_ids = reviewed_ids if category >= 2 else []
        evidence_wordings = [str(item_by_id.loc[iid, "item_text"]) for iid in evidence_ids]
        evidence_scales = []
        for iid in evidence_ids:
            evidence_scales.extend(scales_for_row(item_by_id.loc[iid], instrument_cols))
        evidence_scales = list(dict.fromkeys(evidence_scales))
        if category == 3:
            evidence_text = " | ".join(f"{iid}: {item_by_id.loc[iid, 'item_text']}" for iid in evidence_ids)
            note = "Face-valid narrow item content; feasibility only, not validated construct equivalence."
        elif category == 2:
            evidence_text = " | ".join(f"{iid}: {item_by_id.loc[iid, 'item_text']}" for iid in evidence_ids)
            note = "Neighboring narrow content; semantic scope differs from the canonical model-trait definition."
        elif category == 1:
            evidence_text = "Only broad Big-Five/HEXACO-domain content is plausible; no narrow reviewed item anchor accepted."
            note = "Broad-domain coverage is not a usable one-to-one trait match."
        else:
            evidence_text = "Top lexical/TF-IDF candidates were retained for audit but rejected as construct evidence."
            note = "No defensible coverage found in this feasibility review."
        crosswalk_rows.append({
            "model_trait": name,
            "canonical_definition": traits[name],
            "coverage_category": category,
            "coverage_label": {3: "DIRECT / NEAR-DIRECT CONSTRUCT COVERAGE", 2: "CLOSE NARROW CONSTRUCT", 1: "BROAD-DOMAIN ONLY", 0: "NO DEFENSIBLE COVERAGE FOUND"}[category],
            "review_status": "codex_feasibility_reviewed",
            "evidence_text": evidence_text,
            "candidate_item_ids": ";".join(candidate_ids),
            "accepted_evidence_item_ids": ";".join(evidence_ids),
            "candidate_scale_names": ";".join(evidence_scales),
            "wording_direction": direction_for(name, evidence_wordings) if evidence_ids else "not_applicable_or_not_accepted",
            "lexical_candidate_item_ids": ";".join(str(info.iloc[j]["item_id"]) for j in lexical_idx),
            "semantic_candidate_item_ids": ";".join(str(info.iloc[j]["item_id"]) for j in semantic_idx[:5]),
            "top_semantic_score": round(float(combined[i, semantic_idx[0]]), 6),
            "ambiguity_flag": category in {1, 2},
            "notes": note,
        })
    crosswalk = pd.DataFrame(crosswalk_rows)
    crosswalk.to_csv(out / "sapa_model_trait_candidate_crosswalk.csv", index=False)

    counts = Counter(int(x) for x in crosswalk.coverage_category)
    family_rows = [
        {"summary_type": "coverage_category", "group": str(cat), "count": counts[cat]}
        for cat in [3, 2, 1, 0]
    ]
    family_rows += [
        {"summary_type": "threshold", "group": "category_ge_2", "count": counts[3] + counts[2]},
        {"summary_type": "threshold", "group": "all_traits", "count": len(crosswalk)},
    ]
    pd.DataFrame(family_rows).to_csv(out / "sapa_trait_coverage_summary.csv", index=False)

    answered_per_respondent = data[item_cols].notna().sum(axis=1)
    respondents_per_item = data[item_cols].notna().sum(axis=0)
    missingness = {
        "respondent_count": len(data),
        "psychological_item_count": len(item_cols),
        "total_column_count": len(data.columns),
        "demographic_or_derived_column_count": len(demographic_cols),
        "demographic_or_derived_columns": demographic_cols,
        "answered_items_per_respondent": {
            "mean": round(float(answered_per_respondent.mean()), 6),
            "median": round(float(answered_per_respondent.median()), 6),
            "min": int(answered_per_respondent.min()),
            "p05": round(float(answered_per_respondent.quantile(.05)), 6),
            "p25": round(float(answered_per_respondent.quantile(.25)), 6),
            "p75": round(float(answered_per_respondent.quantile(.75)), 6),
            "p95": round(float(answered_per_respondent.quantile(.95)), 6),
            "max": int(answered_per_respondent.max()),
            "mean_fraction_of_696": round(float(answered_per_respondent.mean() / 696), 8),
        },
        "respondents_per_item": {
            "mean": round(float(respondents_per_item.mean()), 6),
            "median": round(float(respondents_per_item.median()), 6),
            "min": int(respondents_per_item.min()),
            "p05": round(float(respondents_per_item.quantile(.05)), 6),
            "p95": round(float(respondents_per_item.quantile(.95)), 6),
            "max": int(respondents_per_item.max()),
        },
        "overall_item_cell_missing_fraction": round(float(data[item_cols].isna().to_numpy().mean()), 8),
        "planned_missingness_interpretation": "SAPA administered random subsets by design. Release files do not carry a separate cell-level planned/nonresponse indicator, so exact planned versus unplanned missingness cannot be separated. The dominant item-cell missingness mechanism is documented planned missingness; it must not be treated as ordinary item nonresponse.",
        "release_codebook_discrepancy": "demographic codes.txt says items follow the first 20 columns; the actual tab file has 23 non-item columns and 696 q_* item columns (719 total).",
    }
    write_json(out / "sapa_missingness_summary.json", missingness)

    coverage_summary = {
        "model_trait_count": len(crosswalk),
        "category_3_direct_or_near_direct": counts[3],
        "category_2_close_narrow": counts[2],
        "category_ge_2": counts[3] + counts[2],
        "category_1_broad_only": counts[1],
        "category_0_no_defensible_coverage": counts[0],
        "method": {
            "stage_1": "exact/token/deterministic lemma-like overlap candidate ranking",
            "stage_2": "repo-local word and character TF-IDF candidate generation",
            "stage_3": "Codex feasibility review against exact item text and canonical definitions",
            "external_model_api": False,
            "psychometric_validation": False,
        },
        "generated_at": generated,
    }
    write_json(out / "sapa_trait_coverage_summary.json", coverage_summary)

    source_files = []
    for p in sorted(raw.iterdir()):
        if p.is_file():
            source_files.append({
                "file_name": p.name,
                "local_path": str(p),
                "bytes": p.stat().st_size,
                "sha256": sha256(p),
                "gitignored_raw": True,
            })
    source_manifest = {
        "dataset": "Selected personality data from the SAPA-Project: 08Dec2013 to 26Jul2014",
        "institution": "Harvard Dataverse / SAPA Project",
        "release_version": "5.0",
        "persistent_identifier": RELEASE_DOI,
        "canonical_url": RELEASE_URL,
        "download_date": DOWNLOAD_DATE,
        "license": "CC0 1.0",
        "citation": "Condon, David M.; Revelle, William (2015), Selected personality data from the SAPA-Project: 08Dec2013 to 26Jul2014, Harvard Dataverse, V5",
        "actual_dimensions": {"respondents": len(data), "columns": len(data.columns), "psychological_items": len(item_cols), "administered_source_constructs": source_construct_count, "derived_scoring_keys": len(scoring_cols)},
        "response_scale": "1=Very Inaccurate through 6=Very Accurate",
        "missing_value_encoding": "NA in tab data",
        "redistribution": "Dataset release is CC0; raw respondent-level files are nevertheless kept gitignored under the project human-data handling rule.",
        "files": source_files,
        "generated_at": generated,
    }
    write_json(out / "sapa_source_manifest.json", source_manifest)

    verification = {
        "status": "PASS",
        "checks": {
            "respondents_23679": len(data) == 23679,
            "items_696": len(item_cols) == 696,
            "item_ids_unique": info.item_id.nunique() == 696,
            "item_ids_align_response_columns": set(item_cols) == set(info.item_id),
            "administered_source_constructs_92": source_construct_count == 92,
            "canonical_model_traits_240_unique": len(traits) == len(set(traits)) == 240,
            "crosswalk_240_rows": len(crosswalk) == 240,
            "coverage_values_valid": set(crosswalk.coverage_category).issubset({0, 1, 2, 3}),
            "accepted_item_references_valid": all(
                not value or set(value.split(";")) <= set(info.item_id)
                for value in crosswalk.accepted_evidence_item_ids
            ),
            "candidate_item_references_valid": all(
                not value or set(value.split(";")) <= set(info.item_id)
                for value in crosswalk.candidate_item_ids
            ),
            "source_hashes_recorded": all(x["sha256"] for x in source_files),
        },
        "discrepancies": [
            "Data-paper abstract reports 23,681 observations; actual V5 tab release and SAPA update paper contain/report 23,679.",
            "demographic codes.txt describes first 20 columns, while actual V5 tab has 23 non-item columns.",
            "The documented 92 scales are administered source constructs; superKey696.csv separately supplies 131 derived scoring keys.",
        ],
        "generated_at": generated,
    }
    if not all(verification["checks"].values()):
        verification["status"] = "FAIL"
    write_json(out / "sapa_verification_report.json", verification)
    if verification["status"] != "PASS":
        raise RuntimeError("SAPA verification failed")


if __name__ == "__main__":
    main()
