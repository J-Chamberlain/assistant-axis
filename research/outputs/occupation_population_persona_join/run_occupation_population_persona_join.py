#!/usr/bin/env python3
"""Exploratory U.S. occupation prevalence join for Assistant Axis roles.

This is deliberately conservative: roles without defensible modern U.S.
occupation mappings are left unmatched rather than forced into SOC categories.
"""

from __future__ import annotations

import csv
import json
import math
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "outputs" / "occupation_population_persona_join"
OUT.mkdir(parents=True, exist_ok=True)

BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BLS_TABLES_URL = "https://www.bls.gov/oes/tables.htm"
BLS_TIMESERIES_DOC_URL = "https://download.bls.gov/pub/time.series/oe/oe.txt"
BLS_DATATYPE_URL = "https://download.bls.gov/pub/time.series/oe/oe.datatype"
BLS_VINTAGE = "May 2025"
BLS_YEAR = "2025"


# role: SOC mapping. Match classes are exact, close, broad, ambiguous, no_match.
# Ambiguous entries intentionally do not receive SOC codes unless the chosen broad
# category is still useful as a sensitivity row.
OCCUPATION_MAP = {
    "accountant": ("13-2011", "Accountants and Auditors", "exact", "high", "Direct occupational title match; auditors share same SOC."),
    "activist": ("21-1099", "Community and Social Service Specialists, All Other", "broad", "low", "Advocacy work exists occupationally, but activist is not a specific SOC title."),
    "actor": ("27-2011", "Actors", "exact", "high", "Direct occupational title match."),
    "advocate": ("21-1099", "Community and Social Service Specialists, All Other", "broad", "low", "Advocate is a work role, but SOC mapping is broad and context-dependent."),
    "ambassador": ("11-3121", "Human Resources Managers", "ambiguous", "low", "Ambassador is often diplomatic/brand/social role; no clean OEWS SOC. Kept ambiguous without analysis use."),
    "analyst": ("13-1111", "Management Analysts", "broad", "medium", "Generic analyst maps best to management analysts, but many analyst SOCs exist."),
    "anthropologist": ("19-3091", "Anthropologists and Archeologists", "exact", "high", "Direct occupational family title."),
    "archaeologist": ("19-3091", "Anthropologists and Archeologists", "exact", "high", "Direct occupational family title."),
    "architect": ("17-1011", "Architects, Except Landscape and Naval", "exact", "high", "Direct occupational title match."),
    "archivist": ("25-4011", "Archivists", "exact", "high", "Direct occupational title match."),
    "artisan": ("51-9199", "Production Workers, All Other", "broad", "low", "Artisan is a broad craft role without clean SOC."),
    "assistant": ("43-6014", "Secretaries and Administrative Assistants, Except Legal, Medical, and Executive", "broad", "medium", "Assistant is generic; administrative assistant is the most defensible broad mapping."),
    "auctioneer": ("41-9099", "Sales and Related Workers, All Other", "broad", "low", "Auctioneers are not cleanly represented as a detailed SOC in OEWS."),
    "auditor": ("13-2011", "Accountants and Auditors", "exact", "high", "Direct occupational title in SOC title."),
    "bartender": ("35-3011", "Bartenders", "exact", "high", "Direct occupational title match."),
    "biologist": ("19-1029", "Biological Scientists, All Other", "close", "medium", "Generic biologist maps to biological scientists all other; specializations vary."),
    "blogger": ("27-3043", "Writers and Authors", "close", "medium", "Blogging is a writing occupation, but not separately measured by OEWS."),
    "builder": ("47-2061", "Construction Laborers", "broad", "low", "Builder is too broad; construction laborers are a rough family proxy."),
    "cartographer": ("17-1021", "Cartographers and Photogrammetrists", "exact", "high", "Direct occupational title match."),
    "caregiver": ("31-1120", "Home Health and Personal Care Aides", "close", "medium", "Caregiver maps reasonably to home health/personal care aides, but institutional settings vary."),
    "chef": ("35-1011", "Chefs and Head Cooks", "exact", "high", "Direct occupational title match."),
    "chemist": ("19-2031", "Chemists", "exact", "high", "Direct occupational title match."),
    "coach": ("27-2022", "Coaches and Scouts", "exact", "high", "Direct occupational title in SOC title."),
    "collector": ("43-3011", "Bill and Account Collectors", "ambiguous", "low", "Collector could mean debt collector, art collector, or gatherer; left ambiguous."),
    "comedian": ("27-2011", "Actors", "close", "medium", "Comedian is a performing role; OEWS does not provide a detailed comedian SOC."),
    "composer": ("27-2041", "Music Directors and Composers", "exact", "high", "Direct occupational title in SOC title."),
    "conservator": ("25-4012", "Curators", "close", "medium", "Museum/art conservator is not separate in OEWS; curators is closest public category."),
    "consultant": ("13-1111", "Management Analysts", "close", "medium", "Management analyst is the standard SOC proxy for business consultants."),
    "coordinator": ("13-1082", "Project Management Specialists", "broad", "medium", "Coordinator is generic; project management specialists are a defensible broad proxy."),
    "counselor": ("21-1019", "Counselors, All Other", "broad", "medium", "Counselor is broad; all-other counselor category avoids over-specification."),
    "critic": ("27-3023", "News Analysts, Reporters, and Journalists", "broad", "low", "Critic is a media/writing function, not a clean SOC."),
    "curator": ("25-4012", "Curators", "exact", "high", "Direct occupational title match."),
    "debugger": ("15-1251", "Computer Programmers", "close", "medium", "Debugging is a programming/software task, not a separate occupation."),
    "designer": ("27-1029", "Designers, All Other", "broad", "medium", "Generic designer maps to all-other designers."),
    "detective": ("33-3021", "Detectives and Criminal Investigators", "exact", "high", "Direct occupational title match."),
    "dispatcher": ("43-5032", "Dispatchers, Except Police, Fire, and Ambulance", "exact", "high", "Direct occupational title match for non-emergency dispatchers."),
    "doctor": ("29-1215", "Family Medicine Physicians", "broad", "low", "Doctor is broad; family medicine physician is a concrete but incomplete proxy."),
    "economist": ("19-3011", "Economists", "exact", "high", "Direct occupational title match."),
    "editor": ("27-3041", "Editors", "exact", "high", "Direct occupational title match."),
    "emissary": ("11-2032", "Public Relations Managers", "ambiguous", "low", "Emissary is symbolic/diplomatic; no clean modern SOC."),
    "engineer": ("17-2199", "Engineers, All Other", "broad", "medium", "Generic engineer maps to all-other engineers; many detailed engineer SOCs exist."),
    "entrepreneur": ("11-1021", "General and Operations Managers", "ambiguous", "low", "Entrepreneur is owner/founder status, not an OEWS occupation; ambiguous only."),
    "evaluator": ("13-2099", "Financial Specialists, All Other", "ambiguous", "low", "Evaluator is generic and not cleanly occupational."),
    "examiner": ("13-2099", "Financial Specialists, All Other", "ambiguous", "low", "Examiner is generic; many examiner categories exist."),
    "facilitator": ("13-1151", "Training and Development Specialists", "broad", "low", "Facilitator is a task role; training/development is a weak proxy."),
    "fixer": ("49-9099", "Installation, Maintenance, and Repair Workers, All Other", "ambiguous", "low", "Fixer is colloquial/archetypal; mapping is ambiguous."),
    "forecaster": ("19-2021", "Atmospheric and Space Scientists", "ambiguous", "low", "Forecaster could be weather, economic, strategic, or symbolic; ambiguous."),
    "futurist": ("13-2099", "Financial Specialists, All Other", "ambiguous", "low", "Futurist is not an OEWS occupation; ambiguous."),
    "geographer": ("19-3092", "Geographers", "exact", "high", "Direct occupational title match."),
    "grader": ("25-9044", "Teaching Assistants, Postsecondary", "ambiguous", "low", "Grader is a task, not a detailed occupation."),
    "guide": ("39-7010", "Tour and Travel Guides", "close", "medium", "Guide maps reasonably to tour/travel guides, though role can be symbolic."),
    "hacker": ("15-1212", "Information Security Analysts", "close", "medium", "Legal security work maps to information security analysts; hacker role remains culturally broader."),
    "historian": ("19-3093", "Historians", "exact", "high", "Direct occupational title match."),
    "influencer": ("27-3031", "Public Relations Specialists", "broad", "low", "Influencer is not separately measured; PR specialists are a weak public-facing proxy."),
    "instructor": ("25-3099", "Teachers and Instructors, All Other", "exact", "high", "Direct occupational title in SOC title."),
    "interpreter": ("27-3091", "Interpreters and Translators", "exact", "high", "Direct occupational title in SOC title."),
    "interviewer": ("43-4111", "Interviewers, Except Eligibility and Loan", "exact", "high", "Direct occupational title match."),
    "journalist": ("27-3023", "News Analysts, Reporters, and Journalists", "exact", "high", "Direct occupational title in SOC title."),
    "judge": ("23-1023", "Judges, Magistrate Judges, and Magistrates", "exact", "high", "Direct occupational title match."),
    "lawyer": ("23-1011", "Lawyers", "exact", "high", "Direct occupational title match."),
    "librarian": ("25-4022", "Librarians and Media Collections Specialists", "exact", "high", "Direct occupational title in SOC title."),
    "linguist": ("19-3099", "Social Scientists and Related Workers, All Other", "close", "medium", "Linguists are not a standalone OEWS detailed SOC; social scientists all other is closest."),
    "marketer": ("13-1161", "Market Research Analysts and Marketing Specialists", "close", "medium", "Marketer maps to marketing specialists/market research analysts."),
    "mathematician": ("15-2021", "Mathematicians", "exact", "high", "Direct occupational title match."),
    "mechanic": ("49-3023", "Automotive Service Technicians and Mechanics", "close", "medium", "Generic mechanic maps to automotive mechanics as a concrete common proxy."),
    "mediator": ("23-1022", "Arbitrators, Mediators, and Conciliators", "exact", "high", "Direct occupational title in SOC title."),
    "mentor": ("21-1093", "Social and Human Service Assistants", "ambiguous", "low", "Mentor is a social/training role, not a clean occupation."),
    "merchant": ("41-4012", "Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products", "broad", "low", "Merchant is broad/historical; wholesale sales representative is a weak proxy."),
    "moderator": ("43-4051", "Customer Service Representatives", "ambiguous", "low", "Moderator can mean online content moderation, meeting facilitation, or broadcast role."),
    "musician": ("27-2042", "Musicians and Singers", "exact", "high", "Direct occupational title match."),
    "naturalist": ("19-1031", "Conservation Scientists", "close", "medium", "Naturalist maps roughly to conservation science/ecology work."),
    "navigator": ("53-5021", "Captains, Mates, and Pilots of Water Vessels", "close", "medium", "Navigator is not separate; vessel navigation is a defensible occupational proxy."),
    "negotiator": ("13-1028", "Buyers and Purchasing Agents", "ambiguous", "low", "Negotiator is a task across occupations; purchasing agents are only a weak proxy."),
    "novelist": ("27-3043", "Writers and Authors", "exact", "high", "Novelist is a writer/author specialization."),
    "nutritionist": ("29-1031", "Dietitians and Nutritionists", "exact", "high", "Direct occupational title in SOC title."),
    "organizer": ("13-1082", "Project Management Specialists", "broad", "low", "Organizer is broad; project management is a rough proxy."),
    "paramedic": ("29-2042", "Emergency Medical Technicians and Paramedics", "exact", "high", "Direct occupational title in SOC title."),
    "pharmacist": ("29-1051", "Pharmacists", "exact", "high", "Direct occupational title match."),
    "photographer": ("27-4021", "Photographers", "exact", "high", "Direct occupational title match."),
    "physicist": ("19-2012", "Physicists", "exact", "high", "Direct occupational title match."),
    "pilot": ("53-2012", "Commercial Pilots", "close", "medium", "Pilot is broad; commercial pilots is a concrete OEWS category."),
    "planner": ("19-3051", "Urban and Regional Planners", "close", "medium", "Generic planner maps to urban/regional planners, but planning work is broader."),
    "playwright": ("27-3043", "Writers and Authors", "close", "medium", "Playwright is an author specialization."),
    "podcaster": ("27-3011", "Broadcast Announcers and Radio Disc Jockeys", "close", "medium", "Podcasting maps roughly to broadcast/on-air media work."),
    "poet": ("27-3043", "Writers and Authors", "close", "medium", "Poet is an author specialization."),
    "presenter": ("27-3011", "Broadcast Announcers and Radio Disc Jockeys", "close", "medium", "Presenter maps roughly to broadcast announcers."),
    "producer": ("27-2012", "Producers and Directors", "exact", "high", "Direct occupational title in SOC title."),
    "programmer": ("15-1251", "Computer Programmers", "exact", "high", "Direct occupational title match."),
    "proofreader": ("43-9081", "Proofreaders and Copy Markers", "exact", "high", "Direct occupational title match."),
    "psychologist": ("19-3039", "Psychologists, All Other", "broad", "medium", "Generic psychologist maps to all-other psychologists."),
    "publisher": ("11-2031", "Public Relations Managers", "ambiguous", "low", "Publisher can be executive/business owner/editorial function; no clean detailed OEWS match."),
    "recruiter": ("13-1071", "Human Resources Specialists", "close", "medium", "Recruiter maps to HR specialists."),
    "reporter": ("27-3023", "News Analysts, Reporters, and Journalists", "exact", "high", "Direct occupational title in SOC title."),
    "researcher": ("19-3099", "Social Scientists and Related Workers, All Other", "broad", "low", "Researcher is cross-occupational; broad social-science proxy used only cautiously."),
    "reviewer": ("13-2099", "Financial Specialists, All Other", "ambiguous", "low", "Reviewer is a task/function, not a clean occupation."),
    "scheduler": ("43-5061", "Production, Planning, and Expediting Clerks", "close", "medium", "Scheduling maps to planning/expediting clerks, but role is generic."),
    "scholar": ("25-1089", "Education Teachers, Postsecondary, All Other", "ambiguous", "low", "Scholar is status/role rather than occupation; postsecondary teacher all-other is weak."),
    "scientist": ("19-1099", "Life Scientists, All Other", "broad", "low", "Scientist is broad; no single detailed SOC."),
    "scout": ("27-2022", "Coaches and Scouts", "exact", "high", "Direct occupational title in SOC title."),
    "screener": ("33-9093", "Transportation Security Screeners", "close", "medium", "Screener is broad; transportation security screeners are concrete but incomplete."),
    "secretary": ("43-6014", "Secretaries and Administrative Assistants, Except Legal, Medical, and Executive", "exact", "high", "Direct occupational title in SOC title."),
    "sociologist": ("19-3041", "Sociologists", "exact", "high", "Direct occupational title match."),
    "soldier": ("55-3019", "Military Enlisted Tactical Operations and Air/Weapons Specialists and Crew Members, All Other", "close", "medium", "Soldier maps to military enlisted tactical roles; OEWS military coverage is limited/caveated."),
    "sommelier": ("35-1012", "First-Line Supervisors of Food Preparation and Serving Workers", "broad", "low", "Sommelier is not separate in OEWS; food service supervisory proxy is weak."),
    "specialist": ("13-1199", "Business Operations Specialists, All Other", "ambiguous", "low", "Specialist is generic."),
    "spy": ("33-1099", "First-Line Supervisors of Protective Service Workers, All Other", "ambiguous", "low", "Spy/intelligence role is not cleanly public-OEWS measurable."),
    "statistician": ("15-2041", "Statisticians", "exact", "high", "Direct occupational title match."),
    "strategist": ("13-1082", "Project Management Specialists", "ambiguous", "low", "Strategist is generic and not cleanly measured."),
    "summarizer": ("43-9081", "Proofreaders and Copy Markers", "ambiguous", "low", "Summarizer is a task/function, not an occupation."),
    "supervisor": ("43-1011", "First-Line Supervisors of Office and Administrative Support Workers", "broad", "low", "Supervisor is generic; office/admin supervisor is one proxy."),
    "surfer": ("39-3091", "Amusement and Recreation Attendants", "ambiguous", "low", "Surfer is usually hobby/identity; professional mapping is weak."),
    "teacher": ("25-3099", "Teachers and Instructors, All Other", "broad", "medium", "Teacher is broad; all-other teachers avoids choosing grade level."),
    "technologist": ("15-1299", "Computer Occupations, All Other", "broad", "low", "Technologist is generic."),
    "theorist": ("19-3099", "Social Scientists and Related Workers, All Other", "ambiguous", "low", "Theorist is a scholarly function, not an occupation."),
    "therapist": ("29-1129", "Therapists, All Other", "broad", "medium", "Therapist is broad; all-other therapist category avoids choosing discipline."),
    "trainer": ("13-1151", "Training and Development Specialists", "close", "medium", "Trainer maps to training/development specialists."),
    "translator": ("27-3091", "Interpreters and Translators", "exact", "high", "Direct occupational title in SOC title."),
    "tutor": ("25-3099", "Teachers and Instructors, All Other", "close", "medium", "Tutor maps to teachers/instructors all other."),
    "validator": ("13-2099", "Financial Specialists, All Other", "ambiguous", "low", "Validator is a task/function, not a clean occupation."),
    "veterinarian": ("29-1131", "Veterinarians", "exact", "high", "Direct occupational title match."),
    "veteran": ("55-3019", "Military Enlisted Tactical Operations and Air/Weapons Specialists and Crew Members, All Other", "ambiguous", "low", "Veteran is prior status, not occupation; military proxy retained as ambiguous only."),
    "virtuoso": ("27-2042", "Musicians and Singers", "ambiguous", "low", "Virtuoso is a skill/status label; musician proxy only if interpreted musically."),
    "writer": ("27-3043", "Writers and Authors", "exact", "high", "Direct occupational title match."),
}

ANALYSIS_MATCH_CLASSES = {"exact", "close", "broad"}
STRICT_MATCH_CLASSES = {"exact", "close"}
DATATYPES = {
    "employment_count": "01",
    "annual_mean_wage": "04",
    "hourly_median_wage": "08",
    "annual_median_wage": "13",
}


def soc_to_occ_code(soc: str) -> str:
    return soc.replace("-", "")


def make_series_id(soc: str, datatype: str) -> str:
    # OE + seasonal U + National N + area 0000000 + cross-industry 000000
    # + six-digit occupation code + two-digit datatype.
    return "OE" + "U" + "N" + "0000000" + "000000" + soc_to_occ_code(soc) + datatype


def query_bls(series_ids: list[str], year: str = BLS_YEAR) -> dict[str, float | None]:
    values: dict[str, float | None] = {}
    for i in range(0, len(series_ids), 50):
        batch = series_ids[i : i + 50]
        payload = json.dumps({"seriesid": batch, "startyear": year, "endyear": year}).encode()
        req = urllib.request.Request(
            BLS_API_URL,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        for series in parsed.get("Results", {}).get("series", []):
            sid = series["seriesID"]
            data = series.get("data", [])
            if data:
                try:
                    values[sid] = float(data[0]["value"])
                except Exception:
                    values[sid] = None
            else:
                values[sid] = None
        time.sleep(0.25)
    return values


def corr_rows(df: pd.DataFrame, include_classes: set[str], scope: str) -> list[dict]:
    rows = []
    subset = df[df["match_class"].isin(include_classes) & df["employment_count"].notna()].copy()
    if len(subset) < 5:
        return rows
    for model in sorted(subset["model"].dropna().unique()):
        mdf = subset[subset["model"] == model].copy()
        if len(mdf) < 5:
            continue
        for predictor in ["log_employment_count", "annual_median_wage", "log_annual_median_wage"]:
            if predictor not in mdf or mdf[predictor].notna().sum() < 5:
                continue
            for target in ["pc1", "pc2", "pc3", "axis_projection"]:
                if target not in mdf or mdf[target].notna().sum() < 5:
                    continue
                pair = mdf[[predictor, target]].dropna()
                if len(pair) < 5:
                    continue
                rows.append(
                    {
                        "scope": scope,
                        "model": model,
                        "predictor": predictor,
                        "target": target,
                        "n": len(pair),
                        "pearson_r": pair[predictor].corr(pair[target], method="pearson"),
                        "spearman_r": pair[predictor].rank().corr(pair[target].rank(), method="pearson"),
                    }
                )
    return rows


def safe_log(x):
    try:
        return math.log(float(x)) if x and float(x) > 0 else np.nan
    except Exception:
        return np.nan


def markdown_table(df: pd.DataFrame, cols: list[str]) -> str:
    if df.empty:
        return ""
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df[cols].iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.3f}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    qwen = pd.read_csv(ROOT / "research" / "geometry_tables" / "qwen_role_pc_rankings.csv")
    clusters = pd.read_csv(ROOT / "research" / "geometry_tables" / "cluster_membership_table.csv")
    cross = pd.read_csv(ROOT / "research" / "outputs" / "cross_model_cluster_topology" / "per_model_cluster_assignments.csv")
    roles = sorted(qwen["role"].tolist())

    cached_by_soc: dict[str, dict[str, float]] = defaultdict(dict)
    existing_mapping_path = OUT / "role_occupation_mapping.csv"
    if existing_mapping_path.exists():
        existing = pd.read_csv(existing_mapping_path)
        for _, row in existing.dropna(subset=["soc_code"]).iterrows():
            soc = str(row["soc_code"])
            for metric in DATATYPES:
                val = row.get(metric)
                if pd.notna(val):
                    cached_by_soc[soc][metric] = float(val)

    series_map = {}
    unique_socs = sorted({v[0] for v in OCCUPATION_MAP.values() if v[2] in ANALYSIS_MATCH_CLASSES})
    for soc in unique_socs:
        for metric, dtype in DATATYPES.items():
            series_map[(soc, metric)] = make_series_id(soc, dtype)
    bls_values = query_bls(list(series_map.values()))
    value_by_soc = defaultdict(dict)
    for (soc, metric), sid in series_map.items():
        value_by_soc[soc][metric] = bls_values.get(sid)
        if value_by_soc[soc][metric] is None and metric in cached_by_soc.get(soc, {}):
            value_by_soc[soc][metric] = cached_by_soc[soc][metric]

    mapping_rows = []
    for role in roles:
        if role in OCCUPATION_MAP:
            soc, title, klass, conf, rationale = OCCUPATION_MAP[role]
            include = klass in ANALYSIS_MATCH_CLASSES
            vals = value_by_soc.get(soc, {}) if include else {}
            group = soc[:2] + "-0000" if soc else ""
            source_dataset = "BLS OEWS national cross-industry estimates" if include else ""
            mapping_rows.append(
                {
                    "role": role,
                    "match_class": klass,
                    "include_in_analysis": include,
                    "matched_occupation_title": title,
                    "soc_code": soc,
                    "soc_major_group": group,
                    "match_confidence": conf,
                    "rationale": rationale,
                    "source_dataset": source_dataset,
                    "data_vintage": BLS_VINTAGE if include else "",
                    "employment_count": vals.get("employment_count"),
                    "annual_median_wage": vals.get("annual_median_wage"),
                    "annual_mean_wage": vals.get("annual_mean_wage"),
                    "hourly_median_wage": vals.get("hourly_median_wage"),
                    "notes_on_ambiguity": "Excluded from correlation analysis because mapping is ambiguous." if klass == "ambiguous" else "",
                }
            )
        else:
            mapping_rows.append(
                {
                    "role": role,
                    "match_class": "no_match",
                    "include_in_analysis": False,
                    "matched_occupation_title": "",
                    "soc_code": "",
                    "soc_major_group": "",
                    "match_confidence": "",
                    "rationale": "No defensible modern U.S. occupational mapping assigned.",
                    "source_dataset": "",
                    "data_vintage": "",
                    "employment_count": np.nan,
                    "annual_median_wage": np.nan,
                    "annual_mean_wage": np.nan,
                    "hourly_median_wage": np.nan,
                    "notes_on_ambiguity": "",
                }
            )
    mapping = pd.DataFrame(mapping_rows)
    mapping["log_employment_count"] = mapping["employment_count"].apply(safe_log)
    mapping["log_annual_median_wage"] = mapping["annual_median_wage"].apply(safe_log)
    mapping.to_csv(OUT / "role_occupation_mapping.csv", index=False)

    joined = cross.merge(mapping, left_on="persona", right_on="role", how="left")
    # Use canonical Qwen assistant-axis projection and cluster labels where available.
    qwen_extra = qwen[["role", "axis_projection"]].rename(columns={"axis_projection": "qwen_axis_projection"})
    joined = joined.merge(qwen_extra, on="role", how="left")
    joined["axis_projection"] = np.where(joined["model"] == "qwen", joined["qwen_axis_projection"], np.nan)
    joined.to_csv(OUT / "role_occupation_geometry_join.csv", index=False)

    correlations = pd.DataFrame(
        corr_rows(joined, STRICT_MATCH_CLASSES, "exact_close")
        + corr_rows(joined, ANALYSIS_MATCH_CLASSES, "exact_close_broad")
    )
    correlations.to_csv(OUT / "occupation_population_correlations.csv", index=False)

    matched_qwen = joined[(joined["model"] == "qwen") & joined["match_class"].isin(ANALYSIS_MATCH_CLASSES)].copy()
    cluster_summary = (
        matched_qwen.groupby(["qwen_reference_cluster", "match_class"])
        .agg(
            n=("role", "count"),
            employment_count_median=("employment_count", "median"),
            employment_count_mean=("employment_count", "mean"),
            log_employment_count_median=("log_employment_count", "median"),
            annual_median_wage_median=("annual_median_wage", "median"),
            pc1_median=("pc1", "median"),
            pc2_median=("pc2", "median"),
            pc3_median=("pc3", "median"),
        )
        .reset_index()
    )
    cluster_summary.to_csv(OUT / "occupation_population_cluster_summary.csv", index=False)

    # Visualizations.
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    ax = axes[0, 0]
    sizes = 20 + 18 * (matched_qwen["log_employment_count"] - matched_qwen["log_employment_count"].min())
    sc = ax.scatter(matched_qwen["pc1"], matched_qwen["pc2"], s=sizes, c=matched_qwen["log_employment_count"], cmap="viridis", alpha=0.75)
    for _, row in matched_qwen.sort_values("employment_count", ascending=False).head(12).iterrows():
        ax.text(row["pc1"], row["pc2"], row["role"], fontsize=7)
    ax.set_title("Qwen PC1 x PC2, matched occupations sized by log employment")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    fig.colorbar(sc, ax=ax, label="log employment")

    for ax, pc in zip(axes.flatten()[1:], ["pc1", "pc2", "pc3"]):
        ax.scatter(matched_qwen["log_employment_count"], matched_qwen[pc], alpha=0.75)
        ax.set_xlabel("log employment count")
        ax.set_ylabel(pc.upper())
        ax.set_title(f"Qwen {pc.upper()} vs occupational prevalence")
    fig.tight_layout()
    fig.savefig(OUT / "occupation_population_geometry_plots.png", dpi=180)
    plt.close(fig)

    # Coverage plot.
    cov = mapping["match_class"].value_counts().reindex(["exact", "close", "broad", "ambiguous", "no_match"], fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4))
    cov.plot(kind="bar", ax=ax, color=["#2b8cbe", "#7bccc4", "#bae4bc", "#fdae6b", "#d9d9d9"])
    ax.set_title("Role-to-occupation mapping coverage")
    ax.set_ylabel("role count")
    fig.tight_layout()
    fig.savefig(OUT / "occupation_population_coverage.png", dpi=180)
    plt.close(fig)

    # Summary values.
    top_corrs = (
        correlations.assign(abs_pearson=lambda d: d["pearson_r"].abs())
        .sort_values("abs_pearson", ascending=False)
        .head(10)
        if not correlations.empty
        else pd.DataFrame()
    )
    coverage = mapping["match_class"].value_counts().to_dict()
    included = mapping[mapping["match_class"].isin(ANALYSIS_MATCH_CLASSES)]
    exact_close = mapping[mapping["match_class"].isin(STRICT_MATCH_CLASSES)]
    included_with_employment = int(included["employment_count"].notna().sum())
    included_with_wage = int(included["annual_median_wage"].notna().sum())

    source_manifest = f"""# Data Source Manifest

## Official Source

- Dataset: Bureau of Labor Statistics Occupational Employment and Wage Statistics (OEWS), national cross-industry estimates.
- Vintage/year used: {BLS_VINTAGE}; API query year `{BLS_YEAR}`.
- OEWS tables page: {BLS_TABLES_URL}
- OEWS time-series documentation: {BLS_TIMESERIES_DOC_URL}
- OEWS datatype definitions: {BLS_DATATYPE_URL}
- BLS public API endpoint: {BLS_API_URL}

## Field Definitions Used

- `employment_count`: OEWS datatype `01`, employment estimate. BLS documentation states employment estimates are rounded to the nearest ten and self-employed workers are not included.
- `annual_mean_wage`: OEWS datatype `04`.
- `hourly_median_wage`: OEWS datatype `08`.
- `annual_median_wage`: OEWS datatype `13`.
- Series construction: `OE` + seasonal `U` + area type `N` + area `0000000` + industry `000000` + six-digit SOC occupation code + datatype code.

## Local Download/Query Path

- Full BLS bulk downloads were not stored because direct scripted access to the BLS ZIP/text download hosts returned HTTP 403 in this environment.
- The helper script queries only the needed official BLS public API series and writes the normalized outputs in this directory.
- Role-to-SOC mappings are manual, conservative, and auditable in `role_occupation_mapping.csv`.

## Core Geometry Sources

- Qwen canonical role table: `research/geometry_tables/qwen_role_pc_rankings.csv`
- Cluster membership table: `research/geometry_tables/cluster_membership_table.csv`
- Multi-model coordinate table: `research/outputs/cross_model_cluster_topology/per_model_cluster_assignments.csv`
"""
    (OUT / "data_source_manifest.md").write_text(source_manifest)

    report = f"""# Occupation-Population Persona Join

## Summary

This exploratory audit joins Assistant Axis persona roles to public U.S. occupational employment statistics only when a defensible modern SOC mapping exists. It is not Paper 1.5 claim material unless independently replicated and sharpened.

## Sources

- Geometry: `research/geometry_tables/qwen_role_pc_rankings.csv`, `research/geometry_tables/cluster_membership_table.csv`, and `research/outputs/cross_model_cluster_topology/per_model_cluster_assignments.csv`.
- Occupation data: BLS OEWS national cross-industry estimates, {BLS_VINTAGE}, queried through the BLS public API.
- Documentation: `{BLS_TIMESERIES_DOC_URL}` and `{BLS_DATATYPE_URL}`.

## Coverage

- Total roles: {len(mapping)}
- Exact occupational matches: {coverage.get('exact', 0)}
- Close occupational matches: {coverage.get('close', 0)}
- Broad occupational-family matches: {coverage.get('broad', 0)}
- Ambiguous occupational mappings, excluded from quantitative analysis: {coverage.get('ambiguous', 0)}
- Unmatched / intentionally not forced: {coverage.get('no_match', 0)}
- Quantitative exact+close roles: {len(exact_close)}
- Quantitative exact+close+broad roles: {len(included)}
- Included roles with returned/cached BLS employment count: {included_with_employment}
- Included roles with returned/cached BLS annual median wage: {included_with_wage}

Note: direct scripted downloads from the BLS bulk ZIP/text hosts returned HTTP 403 in this environment, and the unauthenticated BLS API hit a daily threshold during the run. The script is rerun-safe and preserves previously fetched official BLS values, but the quantitative subset remains smaller than the mapping subset until a full API refresh or manual XLSX download is available.

## Main Observations

### Observed

- A minority of persona roles map cleanly to modern U.S. occupations. Mythic, symbolic, animal, collective, developmental, and archetypal roles remain explicitly unmatched.
- The matched subset is cluster-skewed toward procedural/professional, editorial, media/creative, and grounded service roles.
- Correlations between log employment count and persona PCs are exploratory and sensitive to whether broad mappings are included.

### Inferred

- Occupational prevalence does not provide a clean, strong explanation of persona geometry in this first pass. Where correlations appear, they should be treated as small-sample pattern hints over a filtered occupational subset.
- High-PC1 procedural roles include both common and specialized occupations; real-world prevalence is not equivalent to assistant-axis/procedural centrality.

### Speculative

- If future work uses occupation prevalence at all, it should separate occupational institutionalization, corpus salience, public-facing recognizability, and employment count. Employment count alone is a weak inverse proxy for niche/specialization.

### Unknown

- Whether training-corpus frequency, web-document frequency, or user-query frequency relate to persona geometry. OEWS employment counts do not measure any of those quantities.

## Strongest Correlations

The table below ranks the largest absolute Pearson correlations found in the sensitivity analyses. These are descriptive diagnostics, not claims.

"""
    if not top_corrs.empty:
        report += markdown_table(top_corrs, ["scope", "model", "predictor", "target", "n", "pearson_r", "spearman_r"])
    else:
        report += "No correlation table was produced because too few matched rows were available."

    report += f"""

## Sensitivity Notes

- Exact+close sensitivity uses only roles where the SOC mapping is direct or reasonably close.
- Broad sensitivity adds rough occupational-family proxies and should be read with lower confidence.
- Ambiguous mappings are preserved in `role_occupation_mapping.csv` but excluded from quantitative correlations.

## Cluster Summary

See `occupation_population_cluster_summary.csv` for matched-role employment and wage summaries by Qwen reference cluster. Small cluster counts make these summaries descriptive only.

## Interpretation Constraints

- Do not claim persona geometry reflects U.S. labor demographics.
- Do not treat OEWS employment count as training-corpus frequency.
- Do not force occupational mappings for archetypes.
- Wage is analyzed separately and is not treated as status.
- This tests only whether real-world professional prevalence has any detectable relationship to persona geometry among matchable occupational roles.

## Recommendation

This should remain exploratory follow-on work. It is probably future-work / appendix material, not Paper 1.5 core evidence. A stronger version would use occupational text/corpus frequency, O*NET descriptors, and a pre-registered mapping rubric rather than employment count alone.
"""
    (OUT / "occupation_population_join_report.md").write_text(report)

    print(
        json.dumps(
            {
                "roles_total": len(mapping),
                "coverage": coverage,
                "included_exact_close_broad": int(len(included)),
                "included_exact_close": int(len(exact_close)),
                "correlation_rows": int(len(correlations)),
                "output_dir": str(OUT.relative_to(ROOT)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
