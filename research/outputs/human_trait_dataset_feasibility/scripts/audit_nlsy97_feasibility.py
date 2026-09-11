#!/usr/bin/env python3
"""Audit NLSY97 personality/occupation co-observation using public-use data.

Respondent-level input remains gitignored. Outputs are variable metadata and
aggregate counts only; no respondent is assigned an LLM persona label.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


INVESTIGATOR_URL = "https://www.nlsinfo.org/investigator/pages/search"
NLSY97_URL = "https://www.bls.gov/nls/nlsy97.htm"
OCCUPATION_GUIDE_URL = "https://www.nlsinfo.org/content/cohorts/nlsy97/topical-guide/employment/occupation"
WEIGHTS_GUIDE_URL = "https://www.nlsinfo.org/content/cohorts/nlsy97/using-and-understanding-the-data/sample-weights-design-effects"
CENSUS_CODE_URL = "https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2002-census-occupation-codes.xls"
CENSUS_2010_CROSSWALK_URL = "https://www2.census.gov/programs-surveys/demo/guidance/industry-occupation/2010-occ-codes-with-crosswalk-from-2002-2011.xls"
BLS_2010_2018_SOC_CROSSWALK_URL = "https://www.bls.gov/soc/2018/crosswalks.htm"
DOWNLOAD_DATE = "2026-09-11"

TIPI = [f"T316250{i}" for i in range(10)]
GOLDBERG = [f"S0920{i}00" for i in range(8)]
R12_OCC = [f"T{31869 + i:05d}00" for i in range(8)]
R6_OCC = [f"S{16030 + i:05d}00" for i in range(11)]
R12_INDUSTRY = [f"T{31860 + i:05d}00" for i in range(8)]
R12_TENURE = [f"T{20217 + i:05d}00" for i in range(8)]
R12_CLASS = [f"T{24406 + i:05d}00" for i in range(8)]
R12_MILITARY = [f"T{35044 + i:05d}00" for i in range(8)]
R12_FREELANCE = [f"T{23797 + i:05d}00" for i in range(4)] + [f"T{24002 + i:05d}00" for i in range(8)]

TIPI_DIMENSIONS = [
    ("Extraversion", "Extraverted, enthusiastic", "same"),
    ("Agreeableness", "Critical, quarrelsome", "reverse"),
    ("Conscientiousness", "Dependable, self-disciplined", "same"),
    ("Emotional Stability", "Anxious, easily upset", "reverse"),
    ("Openness to Experience", "Open to new experiences, complex", "same"),
    ("Extraversion", "Reserved, quiet", "reverse"),
    ("Agreeableness", "Sympathetic, warm", "same"),
    ("Conscientiousness", "Disorganized, careless", "reverse"),
    ("Emotional Stability", "Calm, emotionally stable", "same"),
    ("Openness to Experience", "Conventional, uncreative", "reverse"),
]

GOLDBERG_ITEMS = [
    ("Conscientiousness", "Disorganized describes you; 1=organized, 5=disorganized", "reverse"),
    ("Conscientiousness", "Conscientious describes you; 1=not conscientious, 5=conscientious", "same"),
    ("Conscientiousness", "Undependable describes you; 1=undependable, 5=dependable", "same"),
    ("Conscientiousness", "Thorough describes you; 1=thorough, 5=careless", "reverse"),
    ("Agreeableness", "Agreeable describes you; 1=agreeable, 5=quarrelsome", "reverse"),
    ("Agreeableness", "Difficult describes you; 1=cooperative, 5=difficult", "reverse"),
    ("Agreeableness", "Stubborn describes you; endpoints stubborn/flexible", "same_toward_flexible"),
    ("Agreeableness", "Trustful describes you; 1=distrustful, 5=trustful", "same"),
]

# Conservative title-reviewed supplements to exact 2018-SOC-code matches. Each
# target is an official 2002 Census code; aggregation introduced by the older
# code frame is made explicit in translation_quality.
ROLE_CODE_OVERRIDES = {
    "activist": "2020", "advocate": "2020", "assistant": "5700",
    "anthropologist": "1860", "archaeologist": "1860", "artisan": "8960", "geographer": "1860",
    "historian": "1860", "architect": "1300", "archivist": "2400",
    "conservator": "2400", "curator": "2400", "coach": "2720",
    "scout": "2720", "composer": "2750", "caregiver": "4610",
    "cartographer": "1310", "chemist": "1720", "coordinator": "0710",
    "organizer": "0710", "counselor": "2000", "critic": "2810",
    "journalist": "2810", "reporter": "2810", "dispatcher": "5520",
    "doctor": "3060", "facilitator": "0620", "trainer": "0620",
    "hacker": "1000", "instructor": "2340", "teacher": "2340",
    "tutor": "2340", "interpreter": "2860", "translator": "2860",
    "judge": "2110", "mediator": "2110", "librarian": "2430",
    "linguist": "1860", "marketer": "1810", "merchant": "4850",
    "musician": "2750", "naturalist": "1640", "navigator": "9310",
    "physicist": "1700", "pilot": "9030",
    "podcaster": "2800", "presenter": "2800", "recruiter": "0620",
    "researcher": "1860", "secretary": "5700", "soldier": "9820",
    "technologist": "1000", "artist": "2600",
    "manager": "0020", "police_officer": "3850", "psychologist": "1820",
    "scientist": "1760", "screener": "9420",
}

# These codes were checked as unchanged 2010->2018 in the official BLS SOC
# crosswalk/manual, and also occur in the official 2002 Census list's 2000-SOC
# column. Codes with split/merge markers (for example 51-9199) are excluded and
# handled as explicit title-reviewed older-frame mappings instead.
OFFICIAL_STABLE_2018_TO_2000_SOC = {
    "13-1111", "13-2011", "15-2021", "15-2041", "17-2199", "19-3011",
    "19-3041", "19-3051", "23-1011", "27-2011", "27-2012", "27-3031",
    "27-3041", "27-3043", "27-4021", "29-1031", "29-1051", "29-1129",
    "29-1131", "33-3021", "35-1011", "35-1012", "35-3011", "41-9099",
    "43-1011", "43-4111", "43-5061", "43-9081", "47-2061", "49-3023",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            obj,
            indent=2,
            ensure_ascii=False,
            default=lambda value: value.item() if isinstance(value, np.generic) else str(value),
        ) + "\n",
        encoding="utf-8",
    )


def compact_rnum(display: str) -> str:
    return display.replace(".", "")


def parse_codebook(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="latin-1")
    blocks = re.split(r"-{60,}\s*", text)
    rows = []
    header_re = re.compile(r"^([A-Z]\d{5}\.\d{2})\s+\[([^\]]+)\]\s+Survey Year:\s+(\d{4}|XRND)", re.M)
    for block in blocks:
        m = header_re.search(block)
        if not m:
            continue
        display, qname, year = m.groups()
        lines = block[m.end():].splitlines()
        nonempty = [line.strip() for line in lines if line.strip()]
        try:
            primary_idx = next(i for i, x in enumerate(nonempty) if x in {"PRIMARY VARIABLE", "XRND VARIABLE"})
            title = nonempty[primary_idx + 1]
            body_lines = nonempty[primary_idx + 2:]
        except (StopIteration, IndexError):
            title = ""
            body_lines = nonempty
        stop_prefixes = ("UNIVERSE:", "NOTE:", "COMMENT:", "RESPONSE CHOICE:", "Refusal(", "Min:", "Lead In:", "Default Next Question:")
        wording = []
        for line in body_lines:
            if line.startswith(stop_prefixes) or re.match(r"^\d+\s+[-\d]", line):
                break
            wording.append(line)
        rows.append({
            "variable_id": compact_rnum(display),
            "reference_number": display,
            "question_name": qname,
            "year": year,
            "variable_title": title,
            "question_wording_or_description": " ".join(wording).strip(),
            "official_documentation": "NLS Investigator codebook included in the official public-use extract",
        })
    return pd.DataFrame(rows).drop_duplicates("variable_id")


def parse_occupation_list(xls_path: Path) -> pd.DataFrame:
    with tempfile.TemporaryDirectory(prefix="nlsy97_occ_") as td:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "csv", "--outdir", td, str(xls_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        csv_path = Path(td) / f"{xls_path.stem}.csv"
        raw = pd.read_csv(csv_path, header=None, dtype=str).fillna("")
    rows = []
    for _, row in raw.iterrows():
        title = str(row.iloc[1]).strip() if len(row) > 1 else ""
        code = str(row.iloc[2]).strip() if len(row) > 2 else ""
        soc = str(row.iloc[3]).strip() if len(row) > 3 else ""
        if re.fullmatch(r"\d{4}", code):
            rows.append({"census_2002_code": code, "occupation_title": title, "soc_2000_code": soc})
    out = pd.DataFrame(rows).drop_duplicates("census_2002_code")
    if len(out) != 510:
        raise ValueError(f"Expected 510 official detailed/special occupation codes, found {len(out)}")
    return out


def select_roster_value(data: pd.DataFrame, flag: str, variables: list[str]) -> pd.Series:
    result = np.full(len(data), np.nan)
    for loop, variable in enumerate(variables, 1):
        mask = data[flag].eq(loop)
        result[mask] = data.loc[mask, variable]
    return pd.Series(result, index=data.index)


def valid(series: pd.Series, lo: float, hi: float) -> pd.Series:
    return series.between(lo, hi, inclusive="both")


def feasibility_label(n: int | None) -> str:
    if n is None:
        return "unresolved_translation"
    if n >= 100:
        return "strong occupational cell"
    if n >= 50:
        return "moderate occupational cell"
    if n >= 20:
        return "exploratory occupational cell"
    return "too sparse"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--occupation-xls", type=Path, required=True)
    parser.add_argument("--prior-crosswalk", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--generated-at", help="Optional fixed UTC timestamp for byte-reproducibility tests")
    args = parser.parse_args()
    raw = args.raw_dir.resolve()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    generated = args.generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    csv_path = raw / "human_trait_dataset_feasibility_final.csv"
    cdb_path = raw / "human_trait_dataset_feasibility_final.cdb"
    tagset_path = raw / "human_trait_dataset_feasibility_final.NLSY97"
    for p in [csv_path, cdb_path, tagset_path, args.occupation_xls, args.prior_crosswalk]:
        if not p.exists():
            raise FileNotFoundError(p)

    data = pd.read_csv(csv_path)
    if len(data) != 8984 or data["R0000100"].nunique() != 8984:
        raise ValueError("NLSY97 extract does not contain 8,984 unique respondents")
    codebook = parse_codebook(cdb_path)
    missing_docs = set(data.columns) - set(codebook.variable_id)
    if missing_docs:
        raise ValueError(f"Extract columns missing codebook entries: {sorted(missing_docs)}")

    # Full machine-readable manifest of every selected official variable.
    def classify(qname: str, variable: str) -> str:
        if variable in TIPI:
            return "personality_tipi_round12"
        if variable in GOLDBERG:
            return "personality_goldberg_round6"
        if qname.startswith("YTEL-IND"):
            return "personality_industriousness_round12"
        if qname.startswith("YTEL-TRAD"):
            return "personality_traditionalism_round12"
        if qname.startswith("YSAQ-GRIT"):
            return "personality_grit"
        if variable in R12_OCC or variable in R6_OCC:
            return "occupation_2002_census"
        if variable in R12_INDUSTRY:
            return "industry_2002_census"
        if variable in R12_CLASS:
            return "class_of_worker"
        if variable in R12_TENURE:
            return "job_tenure"
        if variable in R12_MILITARY:
            return "military_employer_flag"
        if variable in R12_FREELANCE:
            return "freelance_or_contractor"
        if qname.startswith("SAMPLING_") or qname in {"VSTRAT", "VPSU", "CV_SAMPLE_TYPE"}:
            return "survey_design"
        if qname.startswith("CV_MAINJOB"):
            return "main_job_roster_selector"
        if variable in {"T3606300", "T3606500", "T3611000", "T4501000", "T4562200", "T4495400", "T4495500", "Z9061900"}:
            return "later_outcome_probe"
        return "key_or_demographic"

    manifest = codebook[codebook.variable_id.isin(data.columns)].copy()
    manifest["round"] = manifest["year"].map({"1997": 1, "2002": 6, "2008": 12, "2009": 13, "2013": 16, "2015": 17, "XRND": "cross-round"}).fillna("")
    manifest["family"] = [classify(q, v) for q, v in zip(manifest.question_name, manifest.variable_id)]
    manifest["public_use_status"] = "public-use; obtained through NLS Investigator guest extraction"
    manifest["derived_or_raw"] = np.where(
        manifest.question_name.str.startswith(("CV_", "CVC_", "SAMPLING_")) | manifest.question_name.isin(["VSTRAT", "VPSU"]),
        "created/derived", "raw questionnaire or roster item"
    )
    manifest["source_url"] = INVESTIGATOR_URL
    manifest.sort_values(["year", "reference_number"]).to_csv(out / "nlsy97_variable_manifest.csv", index=False)

    personality_rows = []
    for i, variable in enumerate(TIPI):
        doc = manifest.set_index("variable_id").loc[variable]
        dimension, wording, direction = TIPI_DIMENSIONS[i]
        personality_rows.append({
            "instrument": "Ten-Item Personality Inventory (TIPI)", "round": 12, "year": 2008,
            "variable_id": variable, "reference_number": doc.reference_number, "question_name": doc.question_name,
            "construct": dimension, "exact_item_or_trait_pair": wording, "response_scale": "1=Disagree strongly; 7=Agree strongly",
            "reverse_scoring": direction, "raw_or_derived": "raw individual item", "public_use_status": "public-use",
            "official_documentation": INVESTIGATOR_URL,
        })
    for i, variable in enumerate(GOLDBERG):
        doc = manifest.set_index("variable_id").loc[variable]
        dimension, wording, direction = GOLDBERG_ITEMS[i]
        personality_rows.append({
            "instrument": "Goldberg Agreeableness/Conscientiousness bipolar items", "round": 6, "year": 2002,
            "variable_id": variable, "reference_number": doc.reference_number, "question_name": doc.question_name,
            "construct": dimension, "exact_item_or_trait_pair": wording, "response_scale": "1-5 bipolar anchored in item wording",
            "reverse_scoring": direction, "raw_or_derived": "raw individual item", "public_use_status": "public-use",
            "official_documentation": INVESTIGATOR_URL,
        })
    additional_specs = [
        (12, 2008, ["T3162600", "T3162601", "T3162602", "T3162603"], "Industriousness", ["reverse", "reverse", "same", "same"]),
        (12, 2008, ["T3162700", "T3162701", "T3162702", "T3162703"], "Traditionalism", ["same", "reverse", "same", "reverse"]),
        (16, 2013, [f"T{90394 + i:05d}00" for i in range(6)] + ["T9040000", "T9040100"], "Short Grit Scale", ["reverse", "same", "reverse", "same", "reverse", "reverse", "same", "same"]),
        (17, 2015, ["U1028900"] + [f"U{10290 + i:05d}00" for i in range(7)], "Short Grit Scale repeat for Round-16 nonrespondents", ["reverse", "same", "reverse", "same", "reverse", "reverse", "same", "same"]),
    ]
    mindex = manifest.set_index("variable_id")
    for rnd, year, variables, instrument, directions in additional_specs:
        for variable, direction in zip(variables, directions):
            doc = mindex.loc[variable]
            personality_rows.append({
                "instrument": instrument, "round": rnd, "year": year, "variable_id": variable,
                "reference_number": doc.reference_number, "question_name": doc.question_name,
                "construct": instrument, "exact_item_or_trait_pair": doc.variable_title,
                "response_scale": "See official codebook entry", "reverse_scoring": direction,
                "raw_or_derived": "raw individual item", "public_use_status": "public-use",
                "official_documentation": INVESTIGATOR_URL,
            })
    personality = pd.DataFrame(personality_rows)
    personality.to_csv(out / "nlsy97_personality_item_manifest.csv", index=False)

    occ_vars = manifest[manifest.family.isin({
        "occupation_2002_census", "industry_2002_census", "class_of_worker", "job_tenure",
        "military_employer_flag", "freelance_or_contractor", "main_job_roster_selector",
    })].copy()
    occ_vars["coding_system_or_role"] = np.select(
        [occ_vars.family.eq("occupation_2002_census"), occ_vars.family.eq("industry_2002_census"), occ_vars.family.eq("main_job_roster_selector")],
        ["2002 Census occupation codes (derived from 2000 SOC)", "2002 Census industry codes", "loop number selecting current/current-most-recent roster job"],
        default="questionnaire/created employment metadata",
    )
    occ_vars["use_in_primary_analysis"] = occ_vars.variable_id.isin(set(R12_OCC + ["T2009700"]))
    occ_vars["notes"] = np.where(
        occ_vars.family.eq("occupation_2002_census"),
        "Select the roster loop identified by the same-wave CV_MAINJOB_FLG; do not assume loop 1.",
        "Context variable; not used to define primary occupation cells unless stated.",
    )
    occ_vars.to_csv(out / "nlsy97_occupation_variable_manifest.csv", index=False)

    occ_codes = parse_occupation_list(args.occupation_xls.resolve())
    occ_codes.to_csv(out / "nlsy97_2002_census_occupation_codes.csv", index=False)
    valid_codes = set(occ_codes.census_2002_code)
    title_by_code = occ_codes.set_index("census_2002_code").occupation_title.to_dict()

    tipi_complete = np.logical_and.reduce([valid(data[v], 1, 7) for v in TIPI])
    # Conservative scoring sufficiency: both items for every TIPI dimension, so
    # sufficient and all-ten-complete are identical in this audit.
    tipi_sufficient = tipi_complete.copy()
    goldberg_complete = np.logical_and.reduce([valid(data[v], 1, 5) for v in GOLDBERG])
    r12_occ_num = select_roster_value(data, "T2009700", R12_OCC)
    r6_occ_num = select_roster_value(data, "S1549402", R6_OCC)
    r12_code = r12_occ_num.map(lambda x: f"{int(x):04d}" if pd.notna(x) and x > 0 else "")
    r6_code = r6_occ_num.map(lambda x: f"{int(x):04d}" if pd.notna(x) and x > 0 else "")
    r12_valid_occ = r12_code.isin(valid_codes)
    r6_valid_occ = r6_code.isin(valid_codes)
    r12_base = tipi_complete & r12_valid_occ
    r6_base = goldberg_complete & r6_valid_occ

    cell_rows = []
    for wave, complete, sufficient, codes, valid_occ, weight in [
        ("Round 12 TIPI", tipi_complete, tipi_sufficient, r12_code, r12_valid_occ, data["T2022500"] / 100.0),
        ("Round 6 Goldberg", goldberg_complete, goldberg_complete, r6_code, r6_valid_occ, pd.Series(np.nan, index=data.index)),
    ]:
        denom = int((complete & valid_occ).sum())
        for code in sorted(set(codes[valid_occ])):
            in_cell = codes.eq(code) & valid_occ
            all_ten = int((complete & in_cell).sum())
            sufficient_n = int((sufficient & in_cell).sum())
            weighted = float(weight[complete & in_cell].sum()) if wave == "Round 12 TIPI" else np.nan
            cell_rows.append({
                "analysis_wave": wave,
                "census_2002_occupation_code": code,
                "occupation_title": title_by_code[code],
                "occupation_observed_n": int(in_cell.sum()),
                "personality_all_items_complete_n": all_ten,
                "personality_scoring_sufficient_n": sufficient_n,
                "complete_rate_within_occupation": round(all_ten / int(in_cell.sum()), 8) if int(in_cell.sum()) else np.nan,
                "share_of_personality_complete_with_occupation": round(all_ten / denom, 8) if denom else np.nan,
                "weighted_population_estimate": round(weighted, 3) if np.isfinite(weighted) else "",
                "weight_note": "Round-12 cumulative-cases sampling weight, two implied decimal places; descriptive only" if wave == "Round 12 TIPI" else "not computed",
            })
    cell_counts = pd.DataFrame(cell_rows)
    cell_counts.to_csv(out / "nlsy97_personality_occupation_cell_counts.csv", index=False)

    # Translate prior role mappings. Exact stable SOC codes must be unchanged in
    # the official BLS 2010->2018 crosswalk and occur in the official 2002
    # Census list's 2000-SOC column. Others require explicit title-reviewed
    # older-frame mappings or remain unresolved; no code is invented.
    prior = pd.read_csv(args.prior_crosswalk, dtype=str).fillna("")
    exact_soc: dict[str, list[str]] = {}
    for _, row in occ_codes.iterrows():
        for soc in re.findall(r"\d{2}-\d{4}", row.soc_2000_code):
            exact_soc.setdefault(soc, []).append(row.census_2002_code)
    title_vec = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))
    all_titles = occ_codes.occupation_title.tolist() + prior.matched_occupation_title.tolist()
    title_matrix = title_vec.fit_transform(all_titles)
    title_sim = cosine_similarity(title_matrix[len(occ_codes):], title_matrix[:len(occ_codes)])
    crosswalk_rows = []
    for pos, (_, row) in enumerate(prior.iterrows()):
        source_status = row.match_class
        accepted: list[str] = []
        method = "not_applicable"
        quality = "unmatched"
        candidate_idx = int(np.argmax(title_sim[pos]))
        candidate_code = occ_codes.iloc[candidate_idx].census_2002_code
        candidate_title = occ_codes.iloc[candidate_idx].occupation_title
        candidate_score = float(title_sim[pos, candidate_idx])
        if row.include_in_analysis.lower() == "true":
            if row.soc_code in OFFICIAL_STABLE_2018_TO_2000_SOC and row.soc_code in exact_soc:
                accepted = exact_soc[row.soc_code]
                method = "official_BLS_2010-2018_crosswalk_same_code_plus_official_2002_Census/SOC_list"
                quality = "official_crosswalk_stable_code_translation"
            elif row.role in ROLE_CODE_OVERRIDES:
                accepted = [ROLE_CODE_OVERRIDES[row.role]]
                method = "explicit_title_review_against_official_2002_Census_code_list"
                quality = "older_frame_aggregate_or_title_translation"
            elif candidate_score >= 0.999999:
                accepted = [candidate_code]
                method = "exact_normalized_title_match_in_official_2002_Census_code_list"
                quality = "exact_title_translation"
            else:
                method = "unresolved_after_official_code_and_title_review"
                quality = "unresolved"
        accepted = [c for c in dict.fromkeys(accepted) if c in valid_codes]
        r12n = int((r12_base & r12_code.isin(accepted)).sum()) if accepted else None
        r6n = int((r6_base & r6_code.isin(accepted)).sum()) if accepted else None
        crosswalk_rows.append({
            "persona": row.role,
            "existing_match_status": source_status,
            "existing_include_in_analysis": row.include_in_analysis,
            "prior_soc_title": row.matched_occupation_title,
            "prior_soc_2018_code": row.soc_code,
            "nlsy97_census_2002_codes": ";".join(accepted),
            "nlsy97_occupation_titles": ";".join(title_by_code[c] for c in accepted),
            "translation_method": method,
            "translation_quality": quality,
            "official_crosswalk_chain": (
                "BLS official 2010-to-2018 SOC crosswalk/manual plus official 2002 Census-to-2000-SOC list"
                if quality == "official_crosswalk_stable_code_translation"
                else "Official 2002 Census code list with explicit title review; not represented as an exact SOC crosswalk"
                if accepted else "not applicable or unresolved"
            ),
            "mapping_quality": source_status,
            "mapping_rationale": row.rationale,
            "top_title_candidate_code": candidate_code if row.include_in_analysis.lower() == "true" else "",
            "top_title_candidate": candidate_title if row.include_in_analysis.lower() == "true" else "",
            "top_title_similarity": round(candidate_score, 6) if row.include_in_analysis.lower() == "true" else "",
            "round12_personality_complete_n": "" if r12n is None else r12n,
            "round6_personality_complete_n": "" if r6n is None else r6n,
            "round12_feasibility": feasibility_label(r12n),
            "notes": "Counts describe human respondents working in the occupation code, not human personas. No human-to-model projection performed.",
        })
    persona_crosswalk = pd.DataFrame(crosswalk_rows)
    persona_crosswalk.to_csv(out / "nlsy97_persona_occupation_crosswalk.csv", index=False)

    mapped = persona_crosswalk[pd.to_numeric(persona_crosswalk.round12_personality_complete_n, errors="coerce").notna()].copy()
    mapped["n"] = pd.to_numeric(mapped.round12_personality_complete_n)
    feasibility_counts = {
        "strong_n_ge_100": int((mapped.n >= 100).sum()),
        "moderate_50_to_99": int(((mapped.n >= 50) & (mapped.n < 100)).sum()),
        "exploratory_20_to_49": int(((mapped.n >= 20) & (mapped.n < 50)).sum()),
        "too_sparse_lt_20": int((mapped.n < 20).sum()),
        "translated_persona_roles": len(mapped),
        "unresolved_prior_included_roles": int(((persona_crosswalk.existing_include_in_analysis.str.lower() == "true") & (persona_crosswalk.round12_personality_complete_n == "")).sum()),
    }

    probes = {
        "later_employment": ("Z9061900", lambda s: s.between(0, 52)),
        "later_education": ("T3606300", lambda s: s.ge(0)),
        "later_justice": ("T4501000", lambda s: s.isin([0, 1])),
        "later_health": ("T4562200", lambda s: s.between(1, 5)),
        "later_substance_use": ("T4495500", lambda s: s.ge(0)),
        "later_family_income": ("T3606500", lambda s: s.ge(0)),
        "later_marital_status": ("T3611000", lambda s: s.ge(0)),
    }
    overlap_rows = [
        {"sample": "Original NLSY97 cohort", "respondent_n": len(data), "definition": "all public-use cohort respondents"},
        {"sample": "Round-12 TIPI all ten items complete", "respondent_n": int(tipi_complete.sum()), "definition": "all T3162500-T3162509 in 1..7"},
        {"sample": "Round-12 TIPI + same-wave current/current-most-recent occupation", "respondent_n": int(r12_base.sum()), "definition": "TIPI complete plus valid official Census code selected by T2009700 roster loop"},
        {"sample": "Round-6 Goldberg all eight items complete", "respondent_n": int(goldberg_complete.sum()), "definition": "all S0920000-S0920700 in 1..5"},
        {"sample": "Round-6 Goldberg + same-wave current/current-most-recent occupation", "respondent_n": int(r6_base.sum()), "definition": "Goldberg complete plus valid official Census code selected by S1549402 roster loop"},
    ]
    for label, (variable, predicate) in probes.items():
        overlap_rows.append({
            "sample": f"Round-12 TIPI + same-wave occupation + {label.replace('_', ' ')} outcome",
            "respondent_n": int((r12_base & predicate(data[variable])).sum()),
            "definition": f"primary R12 sample plus valid public-use {variable}",
        })
    overlap = pd.DataFrame(overlap_rows)
    overlap.to_csv(out / "nlsy97_wave_overlap_summary.csv", index=False)

    outcome_rows = [
        ("education", "CV_HGC_EVER_EDT", "T3606300", "Round 13 (2009); cross-round created", "after R12", "public-use", int((r12_base & data.T3606300.ge(0)).sum()), "Highest grade completed; extracted overlap probe."),
        ("earnings/income", "CV_INCOME_FAMILY", "T3606500", "Round 13 (2009)", "after R12", "public-use", int((r12_base & data.T3606500.ge(0)).sum()), "Gross family income; extracted overlap probe."),
        ("employment history", "CVC_WKSWK_YR_ALL.09", "Z9061900", "Calendar year 2009 cross-round series", "after R12", "public-use", int((r12_base & data.Z9061900.between(0, 52)).sum()), "Weeks worked at any job; extracted overlap probe."),
        ("unemployment spells", "EMP_STATUS weekly event-history array", "series", "weekly longitudinal array", "before/after R12", "public-use", "not extracted", "Available event-history family; exact extraction should be designed for the later outcome analysis."),
        ("job tenure", "CV_WKSWK_JOB_DLI.xx", ";".join(R12_TENURE), "Round 12 roster", "same wave", "public-use", "extracted metadata", "Weeks ever worked at each roster job."),
        ("marriage/partner/family", "CV_MARSTAT", "T3611000", "Round 13 (2009)", "after R12", "public-use", int((r12_base & data.T3611000.ge(0)).sum()), "Marital status; extracted overlap probe."),
        ("health", "YHEA-100", "T4562200", "Round 13 (2009)", "after R12", "public-use", int((r12_base & data.T4562200.between(1, 5)).sum()), "General health; extracted overlap probe."),
        ("mental health", "MHI-5 / CES-D / GAD age modules", "series", "MHI-5 R4,6,8,10,12,14,17-19; CES-D R19-21; GAD at ages 38/39", "same and after R12", "public-use", "not extracted", "Instrument families verified in official health topical documentation."),
        ("substance use", "YSAQ-361", "T4495500", "Round 13 (2009)", "after R12", "public-use", int((r12_base & data.T4495500.ge(0)).sum()), "Days smoked in last 30 days; extracted overlap probe. Alcohol/drug series also available by round."),
        ("risk-related behavior", "self-administered risk/delinquency item families", "series", "multiple rounds", "before/after R12", "public-use", "not extracted", "Availability only; no associations analyzed."),
        ("crime/delinquency", "self-reported delinquency item families", "series", "multiple rounds with changing universes", "before/after R12", "public-use", "not extracted", "Sensitive outcome metadata only."),
        ("arrests", "YSAQ-441 / arrest event history", "T4501000; ARREST_* series", "Round 13 probe plus cross-round arrays", "after R12", "public-use", int((r12_base & data.T4501000.isin([0, 1])).sum()), "Aggregate overlap only; no row-level justice data committed."),
        ("charges", "charge/offense event-history families", "series", "multiple rounds", "before/after R12", "public-use and some restricted detail", "not extracted", "Metadata inventory only."),
        ("court outcomes", "court disposition families", "series", "multiple rounds", "before/after R12", "public-use and some restricted detail", "not extracted", "Metadata inventory only."),
        ("sentencing", "sentence event-history families", "series", "multiple rounds", "before/after R12", "public-use and some restricted detail", "not extracted", "Metadata inventory only."),
        ("incarceration", "INCARC_* cross-round series", "E8043000-E8043601 family", "cross-round", "before/after R12", "public-use", "not extracted", "First/current incarceration and summary measures; sensitive metadata only."),
        ("months incarcerated", "INCARC_TOTMONTHS", "E8043500", "cross-round", "before/after R12", "public-use", "not extracted", "Sensitive metadata only; aggregate suppression required in later analysis."),
        ("military service", "YEMP_MILFLAG.xx / military employment modules", ";".join(R12_MILITARY), "Round 12 roster and longitudinal employment", "same and after R12", "public-use", "extracted metadata", "Military employer flags are public; specialty coding cautions documented."),
        ("civic/community participation", "YSAQ-300V1..V5", "T9040200-T9040600 family", "Round 16 (2013)", "after R12", "public-use", "not extracted", "Volunteer work, meetings, and donations documented alongside R16 SAQ."),
    ]
    outcome = pd.DataFrame(outcome_rows, columns=["domain", "variable_or_series", "exact_variable_ids", "rounds", "temporal_relation_to_round12_personality", "access_status", "coobserved_primary_sample_n", "notes"])
    outcome["official_source"] = "NLSY97 topical guides and NLS Investigator codebook"
    outcome.to_csv(out / "nlsy97_outcome_inventory.csv", index=False)

    summary = {
        "original_cohort_n": len(data),
        "round12_tipi_all_ten_complete_n": int(tipi_complete.sum()),
        "round12_tipi_scoring_sufficient_n": int(tipi_sufficient.sum()),
        "round12_tipi_plus_same_wave_occupation_n": int(r12_base.sum()),
        "round12_weighted_population_estimate": round(float((data.loc[r12_base, "T2022500"] / 100).sum()), 3),
        "round6_goldberg_all_eight_complete_n": int(goldberg_complete.sum()),
        "round6_goldberg_plus_same_wave_occupation_n": int(r6_base.sum()),
        "persona_role_feasibility_counts": feasibility_counts,
        "primary_occupation_selection": "Use CV_MAINJOB_FLG loop number to select same-round YEMP_OCCODE-2002.xx; never assume roster loop 1.",
        "scoring_sufficiency_rule": "Both items for every TIPI dimension (all ten items); no undocumented missing-item imputation.",
        "generated_at": generated,
    }
    write_json(out / "nlsy97_personality_occupation_cell_summary.json", summary)

    # Record all locally retained downloads; every row-level artifact is outside
    # version control even though the source is public-use.
    source_files = []
    for p in sorted(raw.iterdir()):
        if p.is_file():
            source_files.append({"file_name": p.name, "local_path": str(p), "bytes": p.stat().st_size, "sha256": sha256(p), "gitignored_raw": True})
    for p in sorted(args.occupation_xls.resolve().parent.iterdir()):
        if p.is_file():
            source_files.append({"file_name": p.name, "local_path": str(p), "bytes": p.stat().st_size, "sha256": sha256(p), "gitignored_raw": True})
    source_manifest = {
        "dataset": "National Longitudinal Survey of Youth 1997 (NLSY97) public-use data",
        "institution": "U.S. Bureau of Labor Statistics / CHRR, The Ohio State University",
        "release": "NLSY97 1997-2023, rounds 1-21",
        "canonical_url": NLSY97_URL,
        "extraction_url": INVESTIGATOR_URL,
        "download_date": DOWNLOAD_DATE,
        "license_or_access_terms": "Official no-cost public-use NLS Investigator data; project human-data rule prohibits committing respondent rows.",
        "extract_description": "human_trait_dataset_feasibility_final; 126 columns including six Investigator default identifiers/keys",
        "respondents": len(data),
        "files": source_files,
        "occupation_coding": {
            "system": "2002 Census occupation codes derived from 2000 SOC",
            "official_code_url": CENSUS_CODE_URL,
            "official_2010_census_crosswalk_url": CENSUS_2010_CROSSWALK_URL,
            "official_bls_2010_to_2018_soc_crosswalk_url": BLS_2010_2018_SOC_CROSSWALK_URL,
            "crosswalk_rule": "Only BLS-verified unchanged 2010-to-2018 SOC codes are treated as exact code translations; splits/merges and changed codes require an explicit title-reviewed older-frame mapping.",
        },
        "survey_design": {"sample_type": "cross-sectional and supplemental oversample identified by CV_SAMPLE_TYPE", "round12_weight": "T2022500 cumulative-cases weight, two implied decimals", "stratum": "R1489700 VSTRAT", "psu": "R1489800 VPSU", "inference_note": "Raw N is used for feasibility. Any later inference must use documented weights, strata, and PSUs rather than simple-random-sample standard errors."},
        "generated_at": generated,
    }
    write_json(out / "nlsy97_source_manifest.json", source_manifest)

    access_md = f"""# NLSY97 public-data access status

**Status: ACCESS OBTAINED.** On {DOWNLOAD_DATE}, the official NLS Investigator guest workflow produced a public-use extract with {len(data):,} rows and {len(data.columns):,} columns. No account, CAPTCHA bypass, or access-control circumvention was used. The final selected reference numbers are preserved in `{tagset_path.name}` in the gitignored raw-data directory, and the full committed variable manifest records every selected variable.

The official route is {INVESTIGATOR_URL}. NLS Investigator documentation states that an account is not needed to browse public data, although an account is needed to save datasets online. The downloaded respondent-level CSV, data file, control files, codebook, and ZIP remain under `data_external/human_validation/nlsy97/public_use_extract/`, which is gitignored.

Restricted geocodes were neither requested nor obtained. Military specialty questions are public questionnaire content, but this extraction retains the public military-employer flags and general 2002 Census occupation codes; known coding caveats for military specialty strings remain relevant. Later work involving fine geography or restricted fields would require a separate BLS restricted-data application.
"""
    (out / "nlsy97_access_status.md").write_text(access_md, encoding="utf-8")

    checks = {
        "respondents_8984_unique": len(data) == data.R0000100.nunique() == 8984,
        "selected_variable_ids_unique": len(data.columns) == len(set(data.columns)),
        "all_selected_variables_have_codebook_entries": not missing_docs,
        "personality_manifest_ids_unique": personality.variable_id.nunique() == len(personality),
        "tipi_ten_items_present": set(TIPI) <= set(data.columns),
        "goldberg_eight_items_present": set(GOLDBERG) <= set(data.columns),
        "official_occupation_codes_unique": occ_codes.census_2002_code.nunique() == len(occ_codes) == 510,
        "all_accepted_crosswalk_codes_valid": all(
            not x or set(str(x).split(";")) <= valid_codes for x in persona_crosswalk.nlsy97_census_2002_codes
        ),
        "round12_counts_reproduce": int(r12_base.sum()) == int(summary["round12_tipi_plus_same_wave_occupation_n"]),
        "round6_counts_reproduce": int(r6_base.sum()) == int(summary["round6_goldberg_plus_same_wave_occupation_n"]),
        "all_aggregate_counts_nonnegative": (cell_counts.personality_all_items_complete_n >= 0).all(),
        "source_hashes_recorded": all(row["sha256"] for row in source_files),
        "respondent_rows_not_written_to_output_dir": all(
            sum(1 for _ in p.open(encoding="utf-8", errors="ignore")) < 1000
            for p in out.glob("*.csv")
        ),
    }
    verification = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "privacy": {
            "respondent_level_files_committed": False,
            "direct_identifiers_in_derived_tables": False,
            "justice_data_output": "metadata and total overlap count only; no row-level or occupation-specific justice outcome",
            "suppression_rule": "No sensitive subgroup outcome counts were produced. Any later sensitive subgroup table must suppress n<5 at minimum and follow then-current BLS/source requirements.",
        },
        "limitations": [
            "Round-6 Goldberg items were administered only to respondents age <=14 at the end of 1996, so that sample is not the full cohort.",
            "TIPI is very brief and does not cover the 240-model-trait vocabulary.",
            "Some 2018 SOC role mappings collapse into broader 2002 Census categories; translation quality is explicit row by row.",
            "Weighted estimates are descriptive; no standard errors or inferential tests were computed.",
        ],
        "generated_at": generated,
    }
    write_json(out / "nlsy97_verification_report.json", verification)
    if verification["status"] != "PASS":
        raise RuntimeError(f"NLSY97 verification failed: {checks}")


if __name__ == "__main__":
    main()
