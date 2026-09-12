#!/usr/bin/env python3
"""Human-only NLSY97 occupational personality-centroid stability analysis.

The respondent-level public-use extract is read locally and is never written to
the output directory. Outputs contain aggregate cells with N >= 10 or aggregate
statistics that cannot identify respondents. No model vectors or geometry are
inputs to this program.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.stats import rankdata, spearmanr, t as student_t
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold


SEED = 20260911
BOOTSTRAP_REPS = 500
SPLIT_REPS = 500
SUBSAMPLE_REPS = 300
SUPPRESSION_N = 10
DOMAINS = ["openness", "conscientiousness", "extraversion", "agreeableness", "emotional_stability"]
DOMAIN_LABELS = {
    "openness": "Openness to Experience",
    "conscientiousness": "Conscientiousness",
    "extraversion": "Extraversion",
    "agreeableness": "Agreeableness",
    "emotional_stability": "Emotional Stability",
}
TIPI = [f"T316250{i}" for i in range(10)]
GOLDBERG = [f"S0920{i}00" for i in range(8)]
R12_OCC = [f"T{31869 + i:05d}00" for i in range(8)]
R6_OCC = [f"S{16030 + i:05d}00" for i in range(11)]
R12_CLASS = [f"T{24406 + i:05d}00" for i in range(8)]
R12_FREELANCE_CURRENT = [f"T{24002 + i:05d}00" for i in range(8)]
R12_FREELANCE_DLI = [f"T{23797 + i:05d}00" for i in range(4)]
STARTING_SHA = "7914d01f7d9c23060fe199815a90e547241d9682"
PREREG_SHA = "13fb08f1d75444820d0b374fef2e3e0292a4d1f1"

MAJOR_TITLES = {
    "11-0000": "Management Occupations",
    "13-0000": "Business and Financial Operations Occupations",
    "15-0000": "Computer and Mathematical Occupations",
    "17-0000": "Architecture and Engineering Occupations",
    "19-0000": "Life, Physical, and Social Science Occupations",
    "21-0000": "Community and Social Service Occupations",
    "23-0000": "Legal Occupations",
    "25-0000": "Education, Training, and Library Occupations",
    "27-0000": "Arts, Design, Entertainment, Sports, and Media Occupations",
    "29-0000": "Healthcare Practitioners and Technical Occupations",
    "31-0000": "Healthcare Support Occupations",
    "33-0000": "Protective Service Occupations",
    "35-0000": "Food Preparation and Serving Related Occupations",
    "37-0000": "Building and Grounds Cleaning and Maintenance Occupations",
    "39-0000": "Personal Care and Service Occupations",
    "41-0000": "Sales and Related Occupations",
    "43-0000": "Office and Administrative Support Occupations",
    "45-0000": "Farming, Fishing, and Forestry Occupations",
    "47-0000": "Construction and Extraction Occupations",
    "49-0000": "Installation, Maintenance, and Repair Occupations",
    "51-0000": "Production Occupations",
    "53-0000": "Transportation and Material Moving Occupations",
    "55-0000": "Military Specific Occupations",
}

MINOR_TITLES = {
    "11-1000": "Top Executives",
    "11-2000": "Advertising, Marketing, Promotions, Public Relations, and Sales Managers",
    "11-3000": "Operations Specialties Managers",
    "11-9000": "Other Management Occupations",
    "13-1000": "Business Operations Specialists",
    "13-2000": "Financial Specialists",
    "15-1000": "Computer Specialists",
    "15-2000": "Mathematical Science Occupations",
    "17-1000": "Architects, Surveyors, and Cartographers",
    "17-2000": "Engineers",
    "17-3000": "Drafters, Engineering, and Mapping Technicians",
    "19-1000": "Life Scientists",
    "19-2000": "Physical Scientists",
    "19-3000": "Social Scientists and Related Workers",
    "19-4000": "Life, Physical, and Social Science Technicians",
    "21-1000": "Counselors, Social Workers, and Other Community and Social Service Specialists",
    "21-2000": "Religious Workers",
    "23-1000": "Lawyers, Judges, and Related Workers",
    "23-2000": "Legal Support Workers",
    "25-1000": "Postsecondary Teachers",
    "25-2000": "Primary, Secondary, and Special Education School Teachers",
    "25-3000": "Other Teachers and Instructors",
    "25-4000": "Librarians, Curators, and Archivists",
    "25-9000": "Other Education, Training, and Library Occupations",
    "27-1000": "Art and Design Workers",
    "27-2000": "Entertainers and Performers, Sports and Related Workers",
    "27-3000": "Media and Communication Workers",
    "27-4000": "Media and Communication Equipment Workers",
    "29-1000": "Health Diagnosing and Treating Practitioners",
    "29-2000": "Health Technologists and Technicians",
    "29-9000": "Other Healthcare Practitioners and Technical Occupations",
    "31-1000": "Nursing, Psychiatric, and Home Health Aides",
    "31-2000": "Occupational and Physical Therapist Assistants and Aides",
    "31-9000": "Other Healthcare Support Occupations",
    "33-1000": "Supervisors, Protective Service Workers",
    "33-2000": "Fire Fighting and Prevention Workers",
    "33-3000": "Law Enforcement Workers",
    "33-9000": "Other Protective Service Workers",
    "35-1000": "Supervisors, Food Preparation and Serving Workers",
    "35-2000": "Cooks and Food Preparation Workers",
    "35-3000": "Food and Beverage Serving Workers",
    "35-9000": "Other Food Preparation and Serving Related Workers",
    "37-1000": "Supervisors, Building and Grounds Cleaning and Maintenance Workers",
    "37-2000": "Building Cleaning and Pest Control Workers",
    "37-3000": "Grounds Maintenance Workers",
    "39-1000": "Supervisors, Personal Care and Service Workers",
    "39-2000": "Animal Care and Service Workers",
    "39-3000": "Entertainment Attendants and Related Workers",
    "39-4000": "Funeral Service Workers",
    "39-5000": "Personal Appearance Workers",
    "39-6000": "Transportation, Tourism, and Lodging Attendants",
    "39-9000": "Other Personal Care and Service Workers",
    "41-1000": "Supervisors, Sales Workers",
    "41-2000": "Retail Sales Workers",
    "41-3000": "Sales Representatives, Services",
    "41-4000": "Sales Representatives, Wholesale and Manufacturing",
    "41-9000": "Other Sales and Related Workers",
    "43-1000": "Supervisors, Office and Administrative Support Workers",
    "43-2000": "Communications Equipment Operators",
    "43-3000": "Financial Clerks",
    "43-4000": "Information and Record Clerks",
    "43-5000": "Material Recording, Scheduling, Dispatching, and Distributing Workers",
    "43-6000": "Secretaries and Administrative Assistants",
    "43-9000": "Other Office and Administrative Support Workers",
    "45-1000": "Supervisors, Farming, Fishing, and Forestry Workers",
    "45-2000": "Agricultural Workers",
    "45-3000": "Fishing and Hunting Workers",
    "45-4000": "Forest, Conservation, and Logging Workers",
    "47-1000": "Supervisors, Construction and Extraction Workers",
    "47-2000": "Construction Trades Workers",
    "47-3000": "Helpers, Construction Trades",
    "47-4000": "Other Construction and Related Workers",
    "47-5000": "Extraction Workers",
    "49-1000": "Supervisors of Installation, Maintenance, and Repair Workers",
    "49-2000": "Electrical and Electronic Equipment Mechanics, Installers, and Repairers",
    "49-3000": "Vehicle and Mobile Equipment Mechanics, Installers, and Repairers",
    "49-9000": "Other Installation, Maintenance, and Repair Occupations",
    "51-1000": "Supervisors, Production Workers",
    "51-2000": "Assemblers and Fabricators",
    "51-3000": "Food Processing Workers",
    "51-4000": "Metal Workers and Plastic Workers",
    "51-5000": "Printing Workers",
    "51-6000": "Textile, Apparel, and Furnishings Workers",
    "51-7000": "Woodworkers",
    "51-8000": "Plant and System Operators",
    "51-9000": "Other Production Occupations",
    "53-1000": "Supervisors, Transportation and Material Moving Workers",
    "53-2000": "Air Transportation Workers",
    "53-3000": "Motor Vehicle Operators",
    "53-4000": "Rail Transportation Workers",
    "53-5000": "Water Transportation Workers",
    "53-6000": "Other Transportation Workers",
    "53-7000": "Material Moving Workers",
    "55-1000": "Military Officer Special and Tactical Operations Leaders/Managers",
    "55-2000": "First-Line Enlisted Military Supervisors/Managers",
    "55-3000": "Military Enlisted Tactical Operations and Air/Weapons Specialists and Crew Members",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def numeric(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def clean_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if not math.isfinite(float(value)):
            return ""
        return format(float(value), ".10g")
    return value


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(dict.fromkeys(key for row in rows for key in row)) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: clean_value(row.get(k, "")) for k in fieldnames})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, default=clean_value) + "\n",
        encoding="utf-8",
    )


def load_csv_columns(path: Path) -> tuple[list[str], dict[str, np.ndarray]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        columns: list[list[float]] = [[] for _ in header]
        for row in reader:
            if len(row) != len(header):
                raise ValueError(f"Malformed respondent row in {path}")
            for i, value in enumerate(row):
                columns[i].append(numeric(value))
    return header, {name: np.asarray(values, dtype=float) for name, values in zip(header, columns)}


def load_dict_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return [dict(row) for row in csv.DictReader(f)]


def roster_value(data: dict[str, np.ndarray], flag: str, variables: list[str]) -> np.ndarray:
    result = np.full(len(data[flag]), np.nan)
    for loop, variable in enumerate(variables, 1):
        mask = data[flag] == loop
        result[mask] = data[variable][mask]
    return result


def occupation_code(values: np.ndarray) -> np.ndarray:
    return np.asarray([f"{int(v):04d}" if math.isfinite(v) and v > 0 else "" for v in values], dtype=object)


def weighted_mean(x: np.ndarray, w: np.ndarray) -> float:
    valid = np.isfinite(x) & np.isfinite(w) & (w > 0)
    if not np.any(valid):
        return math.nan
    return float(np.sum(w[valid] * x[valid]) / np.sum(w[valid]))


def weighted_sd(x: np.ndarray, w: np.ndarray) -> float:
    valid = np.isfinite(x) & np.isfinite(w) & (w > 0)
    if not np.any(valid):
        return math.nan
    mu = weighted_mean(x[valid], w[valid])
    return float(np.sqrt(np.sum(w[valid] * (x[valid] - mu) ** 2) / np.sum(w[valid])))


def weighted_corr(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(w) & (w > 0)
    if np.sum(valid) < 2:
        return math.nan
    xv, yv, wv = x[valid], y[valid], w[valid]
    mx, my = weighted_mean(xv, wv), weighted_mean(yv, wv)
    cov = np.sum(wv * (xv - mx) * (yv - my)) / np.sum(wv)
    vx = np.sum(wv * (xv - mx) ** 2) / np.sum(wv)
    vy = np.sum(wv * (yv - my) ** 2) / np.sum(wv)
    return float(cov / np.sqrt(vx * vy)) if vx > 0 and vy > 0 else math.nan


def safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return math.nan
    xc, yc = x - np.mean(x), y - np.mean(y)
    denom = np.linalg.norm(xc) * np.linalg.norm(yc)
    return float(np.dot(xc, yc) / denom) if denom > 0 else math.nan


def cosine(x: np.ndarray, y: np.ndarray) -> float:
    denom = np.linalg.norm(x) * np.linalg.norm(y)
    return float(np.dot(x, y) / denom) if denom > 0 else math.nan


def kendall_tau_b(x: np.ndarray, y: np.ndarray) -> float:
    concordant = discordant = tie_x = tie_y = 0
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            dx, dy = np.sign(x[i] - x[j]), np.sign(y[i] - y[j])
            if dx == 0 and dy == 0:
                continue
            if dx == 0:
                tie_x += 1
            elif dy == 0:
                tie_y += 1
            elif dx == dy:
                concordant += 1
            else:
                discordant += 1
    denom = math.sqrt((concordant + discordant + tie_x) * (concordant + discordant + tie_y))
    return (concordant - discordant) / denom if denom else math.nan


def q(values: Iterable[float], p: float) -> float:
    a = np.asarray(list(values), dtype=float)
    a = a[np.isfinite(a)]
    return float(np.quantile(a, p)) if len(a) else math.nan


def group_title(level: str, code: str, occ_meta: dict[str, dict[str, str]]) -> str:
    if level == "narrow":
        return occ_meta[code]["occupation_title"]
    if level == "intermediate":
        return MINOR_TITLES.get(code, f"2000 SOC minor group {code}")
    return MAJOR_TITLES.get(code, f"2000 SOC major group {code}")


def build_occupation_metadata(occupation_rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], list[dict[str, Any]]]:
    meta: dict[str, dict[str, str]] = {}
    rows: list[dict[str, Any]] = []
    for row in occupation_rows:
        code = row["census_2002_code"].zfill(4)
        soc = row["soc_2000_code"].strip()
        minor = major = ""
        note = "official 2002 Census-to-2000-SOC mapping"
        found = re.findall(r"(\d{2})-([0-9X]{4})", soc)
        if found:
            minors = {f"{m}-{digits[0]}000" for m, digits in found}
            majors = {f"{m}-0000" for m, _ in found}
            if len(minors) == 1:
                minor = next(iter(minors))
            if len(majors) == 1:
                major = next(iter(majors))
        elif code == "9830":
            major = "55-0000"
            note = "military rank not specified; assigned only to official military major group"
        elif code == "9920":
            note = "not an occupation; excluded from all analytic occupation levels"
        meta[code] = {
            "occupation_title": row["occupation_title"],
            "soc_2000_code": soc,
            "intermediate_code": minor,
            "broad_code": major,
            "mapping_note": note,
        }
        rows.append({
            "census_2002_code": code,
            "occupation_title": row["occupation_title"],
            "soc_2000_source_code": soc,
            "intermediate_level": "2000_SOC_minor_group",
            "intermediate_code": minor,
            "intermediate_title": MINOR_TITLES.get(minor, f"2000 SOC minor group {minor}") if minor else "",
            "broad_level": "2000_SOC_major_group",
            "broad_code": major,
            "broad_title": MAJOR_TITLES.get(major, "") if major else "",
            "included_as_occupation": code != "9920",
            "mapping_note": note,
        })
    return meta, rows


def map_level(codes: np.ndarray, level: str, occ_meta: dict[str, dict[str, str]]) -> np.ndarray:
    mapped: list[str] = []
    for code in codes:
        if code not in occ_meta or code == "9920":
            mapped.append("")
        elif level == "narrow":
            mapped.append(code)
        elif level == "intermediate":
            mapped.append(occ_meta[code]["intermediate_code"])
        else:
            mapped.append(occ_meta[code]["broad_code"])
    return np.asarray(mapped, dtype=object)


def design_setup(strata: np.ndarray, psu: np.ndarray) -> tuple[np.ndarray, np.ndarray, int, dict[str, Any]]:
    unique_strata = np.asarray(sorted(set(int(x) for x in strata)), dtype=int)
    stratum_index = {value: i for i, value in enumerate(unique_strata)}
    h_index = np.asarray([stratum_index[int(x)] for x in strata], dtype=int)
    psu_int = psu.astype(int)
    counts = {int(h): sorted(set(int(p) for p in psu_int[strata == h])) for h in unique_strata}
    if any(v != [1, 2] for v in counts.values()):
        raise RuntimeError(f"Frozen two-PSU design condition failed: {counts}")
    key = h_index * 2 + (psu_int - 1)
    audit = {
        "strata": len(unique_strata),
        "psus": len(unique_strata) * 2,
        "design_degrees_of_freedom": len(unique_strata),
        "every_stratum_has_vpsu_1_and_2": True,
    }
    return h_index, key, len(unique_strata), audit


def design_se(y: np.ndarray, w: np.ndarray, cell_mask: np.ndarray, design_key: np.ndarray, n_strata: int) -> float:
    denom = np.sum(w[cell_mask])
    if denom <= 0:
        return math.nan
    mu = np.sum(w[cell_mask] * y[cell_mask]) / denom
    contribution = np.zeros(len(y), dtype=float)
    contribution[cell_mask] = w[cell_mask] * (y[cell_mask] - mu) / denom
    totals = np.bincount(design_key, weights=contribution, minlength=n_strata * 2).reshape(n_strata, 2)
    centered = totals - totals.mean(axis=1, keepdims=True)
    variance = np.sum(2.0 * centered**2)
    return float(np.sqrt(max(variance, 0.0)))


def summarize_metric(values: list[float], prefix: str) -> dict[str, float]:
    a = np.asarray(values, dtype=float)
    a = a[np.isfinite(a)]
    if not len(a):
        return {f"{prefix}_median": math.nan, f"{prefix}_p05": math.nan, f"{prefix}_p95": math.nan}
    return {
        f"{prefix}_median": float(np.median(a)),
        f"{prefix}_p05": float(np.quantile(a, 0.05)),
        f"{prefix}_p95": float(np.quantile(a, 0.95)),
    }


def corr_pair(x: list[float], y: list[float]) -> tuple[float, float]:
    a, b = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    valid = np.isfinite(a) & np.isfinite(b)
    if np.sum(valid) < 3:
        return math.nan, math.nan
    pearson = safe_corr(a[valid], b[valid])
    spearman = float(spearmanr(a[valid], b[valid]).statistic)
    return pearson, spearman


def random_intercept_mom(
    y: np.ndarray,
    group_ids: np.ndarray,
    frequency: np.ndarray | None = None,
) -> dict[str, float]:
    """One-way random-intercept method-of-moments estimate for unequal cells."""
    f = np.ones(len(y), dtype=float) if frequency is None else np.asarray(frequency, dtype=float)
    keep = np.isfinite(y) & np.isfinite(f) & (f > 0)
    yy, gg, ff = y[keep], group_ids[keep], f[keep]
    if not len(yy):
        return {k: math.nan for k in ["between", "within", "total", "icc", "effective_cell_n"]}
    group_n = np.bincount(gg, weights=ff)
    represented = group_n > 0
    groups = int(np.sum(represented))
    total_n = float(np.sum(ff))
    if groups < 2 or total_n <= groups:
        return {k: math.nan for k in ["between", "within", "total", "icc", "effective_cell_n"]}
    group_sum = np.bincount(gg, weights=ff * yy, minlength=len(group_n))
    group_mean = np.divide(group_sum, group_n, out=np.zeros_like(group_sum), where=represented)
    overall = float(np.sum(ff * yy) / total_n)
    ss_between = float(np.sum(group_n[represented] * (group_mean[represented] - overall) ** 2))
    ss_within = float(np.sum(ff * (yy - group_mean[gg]) ** 2))
    ms_between = ss_between / (groups - 1)
    ms_within = ss_within / (total_n - groups)
    effective_cell_n = (total_n - np.sum(group_n[represented] ** 2) / total_n) / (groups - 1)
    tau2 = max((ms_between - ms_within) / effective_cell_n, 0.0)
    total = tau2 + ms_within
    return {
        "between": tau2,
        "within": ms_within,
        "total": total,
        "icc": tau2 / total if total > 0 else math.nan,
        "effective_cell_n": float(effective_cell_n),
    }


def centered_bootstrap_interval(values: Iterable[float], point: float, lower: float | None = None, upper: float | None = None) -> tuple[float, float]:
    """Percentile interval from bootstrap deviations centered on their mean."""
    a = np.asarray(list(values), dtype=float)
    a = a[np.isfinite(a)]
    if not len(a):
        return math.nan, math.nan
    centered = point + math.sqrt(2.0) * (a - np.mean(a))
    lo, hi = q(centered, 0.025), q(centered, 0.975)
    if lower is not None:
        lo, hi = max(lower, lo), max(lower, hi)
    if upper is not None:
        lo, hi = min(upper, lo), min(upper, hi)
    return lo, hi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-csv", type=Path, required=True)
    parser.add_argument("--codebook", type=Path, required=True)
    parser.add_argument("--occupation-codes", type=Path, required=True)
    parser.add_argument("--persona-crosswalk", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--generated-at", default="2026-09-11T23:30:00Z")
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    header, data = load_csv_columns(args.raw_csv.resolve())
    required = set(TIPI + GOLDBERG + R12_OCC + R6_OCC + R12_CLASS + R12_FREELANCE_CURRENT + R12_FREELANCE_DLI + [
        "R0536300", "R0536402", "R1489700", "R1489800", "S1549402", "T2009700", "T2022500", "T3606300"
    ])
    missing = required - set(header)
    if missing:
        raise ValueError(f"Missing required variables: {sorted(missing)}")
    if len(next(iter(data.values()))) != 8984:
        raise ValueError("Expected 8,984 NLSY97 respondents")

    occupation_rows = load_dict_rows(args.occupation_codes.resolve())
    occ_meta, aggregation_rows = build_occupation_metadata(occupation_rows)
    write_csv(out / "occupation_aggregation_crosswalk.csv", aggregation_rows)
    valid_codes = set(occ_meta)

    r12_occ_raw = roster_value(data, "T2009700", R12_OCC)
    r6_occ_raw = roster_value(data, "S1549402", R6_OCC)
    r12_codes = occupation_code(r12_occ_raw)
    r6_codes = occupation_code(r6_occ_raw)
    r12_official_occ = np.asarray([c in valid_codes for c in r12_codes])
    r6_official_occ = np.asarray([c in valid_codes for c in r6_codes])
    r12_occupation = r12_official_occ & (r12_codes != "9920")
    r6_occupation = r6_official_occ & (r6_codes != "9920")

    tipi_items = np.column_stack([data[v] for v in TIPI])
    tipi_complete = np.all((tipi_items >= 1) & (tipi_items <= 7), axis=1)
    tipi_raw = np.column_stack([
        (tipi_items[:, 4] + (8 - tipi_items[:, 9])) / 2,
        (tipi_items[:, 2] + (8 - tipi_items[:, 7])) / 2,
        (tipi_items[:, 0] + (8 - tipi_items[:, 5])) / 2,
        ((8 - tipi_items[:, 1]) + tipi_items[:, 6]) / 2,
        ((8 - tipi_items[:, 3]) + tipi_items[:, 8]) / 2,
    ])
    goldberg_items = np.column_stack([data[v] for v in GOLDBERG])
    goldberg_complete = np.all((goldberg_items >= 1) & (goldberg_items <= 5), axis=1)
    goldberg_ac = np.column_stack([
        np.mean(np.column_stack([goldberg_items[:, 4], 6-goldberg_items[:, 5], 6-goldberg_items[:, 6], goldberg_items[:, 7]]), axis=1),
        np.mean(np.column_stack([6-goldberg_items[:, 0], goldberg_items[:, 1], 6-goldberg_items[:, 2], goldberg_items[:, 3]]), axis=1),
    ])

    weight_all = data["T2022500"] / 100.0
    design_valid = np.isfinite(data["R1489700"]) & np.isfinite(data["R1489800"]) & np.isin(data["R1489800"], [1, 2])
    primary_mask = tipi_complete & r12_occupation & (weight_all > 0) & design_valid
    primary_index = np.flatnonzero(primary_mask)
    w = weight_all[primary_mask]
    raw = tipi_raw[primary_mask]
    strata = data["R1489700"][primary_mask]
    psu = data["R1489800"][primary_mask]
    h_index, design_key, n_strata, design_audit = design_setup(strata, psu)
    global_mean = np.asarray([weighted_mean(raw[:, d], w) for d in range(5)])
    global_sd = np.asarray([weighted_sd(raw[:, d], w) for d in range(5)])
    if np.any(global_sd <= 0):
        raise RuntimeError("Invalid global TIPI standard deviation")
    z = (raw - global_mean) / global_sd

    r12_level_all = {level: map_level(r12_codes, level, occ_meta) for level in ["narrow", "intermediate", "broad"]}
    level_codes = {level: values[primary_mask] for level, values in r12_level_all.items()}
    r6_level_all = {level: map_level(r6_codes, level, occ_meta) for level in ["narrow", "intermediate", "broad"]}

    class_worker = roster_value(data, "T2009700", R12_CLASS)[primary_mask]
    freelance_current = roster_value(data, "T2009700", R12_FREELANCE_CURRENT)
    freelance_dli = roster_value(data, "T2009700", R12_FREELANCE_DLI)
    freelance_all = np.where(np.isin(freelance_current, [0, 1]), freelance_current, freelance_dli)[primary_mask]
    sex = data["R0536300"][primary_mask]
    age = 2008 - data["R0536402"][primary_mask]
    education = data["T3606300"][primary_mask]

    reliability = {}
    keyed_pairs = {
        "openness": (tipi_items[primary_mask, 4], 8-tipi_items[primary_mask, 9]),
        "conscientiousness": (tipi_items[primary_mask, 2], 8-tipi_items[primary_mask, 7]),
        "extraversion": (tipi_items[primary_mask, 0], 8-tipi_items[primary_mask, 5]),
        "agreeableness": (8-tipi_items[primary_mask, 1], tipi_items[primary_mask, 6]),
        "emotional_stability": (8-tipi_items[primary_mask, 3], tipi_items[primary_mask, 8]),
    }
    for domain, (a, b) in keyed_pairs.items():
        r = weighted_corr(a, b, w)
        reliability[domain] = {
            "weighted_inter_item_correlation": r,
            "spearman_brown_two_item_coefficient": 2*r/(1+r) if math.isfinite(r) and r > -1 else math.nan,
        }

    centroid_rows: list[dict[str, Any]] = []
    full_stats: dict[tuple[str, str], dict[str, Any]] = {}
    tcrit = float(student_t.ppf(0.975, design_audit["design_degrees_of_freedom"]))
    for level in ["narrow", "intermediate", "broad"]:
        codes = level_codes[level]
        for code in sorted(set(codes) - {""}):
            mask = codes == code
            n = int(np.sum(mask))
            if n < SUPPRESSION_N:
                continue
            centroid = np.asarray([weighted_mean(z[mask, d], w[mask]) for d in range(5)])
            unweighted_centroid = np.mean(z[mask], axis=0)
            heterogeneity = float(np.sqrt(np.sum(w[mask] * np.sum((z[mask] - centroid) ** 2, axis=1)) / np.sum(w[mask])))
            all_codes = r12_level_all[level]
            observed_mask = r12_occupation & (all_codes == code)
            complete_mask = observed_mask & tipi_complete
            narrow_children = sorted(set(r12_codes[observed_mask]))
            row: dict[str, Any] = {
                "occupation_level": level,
                "occupation_code": code,
                "occupation_title": group_title(level, code, occ_meta),
                "analytic_n": n,
                "occupation_observed_n": int(np.sum(observed_mask)),
                "tipi_complete_n": int(np.sum(complete_mask)),
                "tipi_complete_rate": float(np.sum(complete_mask) / np.sum(observed_mask)) if np.sum(observed_mask) else math.nan,
                "weighted_population_estimate": float(np.sum(w[mask])),
                "distinct_narrow_occupation_codes": len(narrow_children),
                "weighted_mean_age_approx_2008_minus_birth_year": weighted_mean(age[mask], w[mask]),
                "weighted_female_share": weighted_mean((sex[mask] == 2).astype(float), w[mask]),
                "round13_education_observed_n": int(np.sum(np.isfinite(education[mask]) & (((education[mask] >= 0) & (education[mask] <= 20)) | (education[mask] == 95)))),
                "weighted_education_lt_high_school_share": weighted_mean(((education[mask] >= 0) & (education[mask] <= 11)).astype(float), np.where(((education[mask] >= 0) & (education[mask] <= 20)), w[mask], 0)),
                "weighted_education_high_school_share": weighted_mean((education[mask] == 12).astype(float), np.where(((education[mask] >= 0) & (education[mask] <= 20)), w[mask], 0)),
                "weighted_education_some_college_share": weighted_mean(((education[mask] >= 13) & (education[mask] <= 15)).astype(float), np.where(((education[mask] >= 0) & (education[mask] <= 20)), w[mask], 0)),
                "weighted_education_bachelors_share": weighted_mean((education[mask] == 16).astype(float), np.where(((education[mask] >= 0) & (education[mask] <= 20)), w[mask], 0)),
                "weighted_education_postgraduate_share": weighted_mean(((education[mask] >= 17) & (education[mask] <= 20)).astype(float), np.where(((education[mask] >= 0) & (education[mask] <= 20)), w[mask], 0)),
                "weighted_education_ungraded_share": weighted_mean((education[mask] == 95).astype(float), np.where(((education[mask] >= 0) & (education[mask] <= 20)) | (education[mask] == 95), w[mask], 0)),
                "class_of_worker_observed_n": int(np.sum(np.isin(class_worker[mask], [1, 2, 3, 4, 5]))),
                "weighted_government_worker_share": weighted_mean((class_worker[mask] == 1).astype(float), np.where(np.isin(class_worker[mask], [1, 2, 3, 4, 5]), w[mask], 0)),
                "weighted_private_for_profit_share": weighted_mean((class_worker[mask] == 2).astype(float), np.where(np.isin(class_worker[mask], [1, 2, 3, 4, 5]), w[mask], 0)),
                "weighted_nonprofit_share": weighted_mean((class_worker[mask] == 3).astype(float), np.where(np.isin(class_worker[mask], [1, 2, 3, 4, 5]), w[mask], 0)),
                "weighted_unpaid_family_worker_share": weighted_mean((class_worker[mask] == 4).astype(float), np.where(np.isin(class_worker[mask], [1, 2, 3, 4, 5]), w[mask], 0)),
                "weighted_armed_forces_share": weighted_mean((class_worker[mask] == 5).astype(float), np.where(np.isin(class_worker[mask], [1, 2, 3, 4, 5]), w[mask], 0)),
                "freelance_contractor_observed_n": int(np.sum(np.isin(freelance_all[mask], [0, 1]))),
                "weighted_freelance_contractor_share": weighted_mean((freelance_all[mask] == 1).astype(float), np.where(np.isin(freelance_all[mask], [0, 1]), w[mask], 0)),
                "within_cell_5d_rms_heterogeneity": heterogeneity,
                "weight": "Round-12 cumulative-cases weight T2022500/100",
                "variance_design": "Taylor linearization with VSTRAT/VPSU",
            }
            domain_stats: dict[str, Any] = {}
            for d, domain in enumerate(DOMAINS):
                w_raw_mean = weighted_mean(raw[mask, d], w[mask])
                se_raw = design_se(raw[:, d], w, mask, design_key, n_strata)
                se_z = design_se(z[:, d], w, mask, design_key, n_strata)
                domain_stats[domain] = {
                    "weighted_raw_mean": w_raw_mean,
                    "unweighted_raw_mean": float(np.mean(raw[mask, d])),
                    "weighted_raw_sd": weighted_sd(raw[mask, d], w[mask]),
                    "weighted_z_mean": centroid[d],
                    "unweighted_z_mean": unweighted_centroid[d],
                    "design_se_raw": se_raw,
                    "design_ci95_raw_low": w_raw_mean - tcrit * se_raw,
                    "design_ci95_raw_high": w_raw_mean + tcrit * se_raw,
                    "design_se_z": se_z,
                    "design_ci95_z_low": centroid[d] - tcrit * se_z,
                    "design_ci95_z_high": centroid[d] + tcrit * se_z,
                }
                for key, value in domain_stats[domain].items():
                    row[f"{domain}_{key}"] = value
            centroid_rows.append(row)
            full_stats[(level, code)] = {
                "mask": mask,
                "n": n,
                "centroid": centroid,
                "unweighted_centroid": unweighted_centroid,
                "heterogeneity": heterogeneity,
                "weighted_population_estimate": float(np.sum(w[mask])),
                "domain_stats": domain_stats,
            }
    centroid_rows.sort(key=lambda x: ({"narrow": 0, "intermediate": 1, "broad": 2}[x["occupation_level"]], x["occupation_code"]))
    write_csv(out / "occupation_big_five_centroids.csv", centroid_rows)

    rng = np.random.default_rng(SEED)
    bootstrap_factor = np.empty((BOOTSTRAP_REPS, len(w)), dtype=np.float32)
    for h in range(n_strata):
        count_psu1 = rng.binomial(2, 0.5, size=BOOTSTRAP_REPS).astype(np.float32)
        bootstrap_factor[:, (h_index == h) & (psu == 1)] = count_psu1[:, None]
        bootstrap_factor[:, (h_index == h) & (psu == 2)] = (2 - count_psu1)[:, None]

    boot_centroids: dict[tuple[str, str], np.ndarray] = {}
    uncertainty_rows: list[dict[str, Any]] = []
    variance_rows: list[dict[str, Any]] = []
    for level in ["narrow", "intermediate", "broad"]:
        codes_all = level_codes[level]
        valid_level = codes_all != ""
        codes_sorted = sorted(set(codes_all[valid_level]))
        code_to_id = {code: i for i, code in enumerate(codes_sorted)}
        ids = np.asarray([code_to_id[c] for c in codes_all[valid_level]], dtype=int)
        ww, zz = w[valid_level], z[valid_level]
        bf = bootstrap_factor[:, valid_level]
        g = len(codes_sorted)
        denom_rep = np.zeros((BOOTSTRAP_REPS, g))
        num_rep = np.zeros((BOOTSTRAP_REPS, g, 5))
        variance_boot = {
            domain: {"between": [], "within": [], "icc": [], "anova_between": [], "anova_within": [], "anova_icc": []}
            for domain in DOMAINS
        }
        for r in range(BOOTSTRAP_REPS):
            rw = ww * bf[r]
            denom = np.bincount(ids, weights=rw, minlength=g)
            denom_rep[r] = denom
            for d in range(5):
                num_rep[r, :, d] = np.bincount(ids, weights=rw * zz[:, d], minlength=g)
            if level in {"narrow", "broad"}:
                total_w = np.sum(rw)
                for d, domain in enumerate(DOMAINS):
                    means = np.divide(num_rep[r, :, d], denom, out=np.zeros(g), where=denom > 0)
                    mu = np.sum(rw * zz[:, d]) / total_w
                    between = np.sum(denom * (means - mu) ** 2) / total_w
                    within = np.sum(rw * (zz[:, d] - means[ids]) ** 2) / total_w
                    variance_boot[domain]["between"].append(between)
                    variance_boot[domain]["within"].append(within)
                    variance_boot[domain]["icc"].append(between / (between + within))
                    anova = random_intercept_mom(zz[:, d], ids, bf[r])
                    variance_boot[domain]["anova_between"].append(anova["between"])
                    variance_boot[domain]["anova_within"].append(anova["within"])
                    variance_boot[domain]["anova_icc"].append(anova["icc"])
        for code in codes_sorted:
            key = (level, code)
            if key not in full_stats:
                continue
            j = code_to_id[code]
            valid_rep = denom_rep[:, j] > 0
            star = np.divide(num_rep[:, j, :], denom_rep[:, j, None], out=np.full((BOOTSTRAP_REPS, 5), np.nan), where=denom_rep[:, j, None] > 0)
            full = full_stats[key]["centroid"]
            adjusted = full + math.sqrt(2.0) * (star - full)
            boot_centroids[key] = adjusted
            valid_adjusted = adjusted[valid_rep & np.all(np.isfinite(adjusted), axis=1)]
            displacement = np.linalg.norm(valid_adjusted - full, axis=1)
            covariance = np.cov(valid_adjusted, rowvar=False, ddof=1) if len(valid_adjusted) > 1 else np.full((5, 5), np.nan)
            row = {
                "occupation_level": level,
                "occupation_code": code,
                "occupation_title": group_title(level, code, occ_meta),
                "analytic_n": full_stats[key]["n"],
                "bootstrap_requested_replicates": BOOTSTRAP_REPS,
                "bootstrap_valid_replicates": len(valid_adjusted),
                "bootstrap_mean_displacement": float(np.mean(displacement)) if len(displacement) else math.nan,
                "bootstrap_median_displacement": float(np.median(displacement)) if len(displacement) else math.nan,
                "bootstrap_p95_displacement": q(displacement, 0.95),
                "centroid_root_trace_covariance": float(np.sqrt(np.trace(covariance))) if np.all(np.isfinite(covariance)) else math.nan,
                "bootstrap_method": "stratified PSU-with-replacement; two PSUs drawn per VSTRAT; deviations rescaled sqrt(2)",
            }
            for d, domain in enumerate(DOMAINS):
                row[f"{domain}_bootstrap_mean"] = float(np.mean(valid_adjusted[:, d])) if len(valid_adjusted) else math.nan
                row[f"{domain}_bootstrap_ci95_low"] = q(valid_adjusted[:, d], 0.025) if len(valid_adjusted) else math.nan
                row[f"{domain}_bootstrap_ci95_high"] = q(valid_adjusted[:, d], 0.975) if len(valid_adjusted) else math.nan
            for i, left in enumerate(DOMAINS):
                for j2 in range(i, len(DOMAINS)):
                    right = DOMAINS[j2]
                    row[f"cov_{left}__{right}"] = covariance[i, j2]
            uncertainty_rows.append(row)

        if level in {"narrow", "broad"}:
            full_codes = codes_all[valid_level]
            full_ids = ids
            denom = np.bincount(full_ids, weights=ww, minlength=g)
            for d, domain in enumerate(DOMAINS):
                sums = np.bincount(full_ids, weights=ww * zz[:, d], minlength=g)
                means = sums / denom
                mu = weighted_mean(zz[:, d], ww)
                between = float(np.sum(denom * (means - mu) ** 2) / np.sum(ww))
                within = float(np.sum(ww * (zz[:, d] - means[full_ids]) ** 2) / np.sum(ww))
                full_values = {"between": between, "within": within, "icc": between / (between + within)}
                row = {
                    "occupation_level": level,
                    "domain": domain,
                    "estimator": "survey_weighted_descriptive_exact_decomposition",
                    "occupation_groups": g,
                    "respondent_n": len(ww),
                    "between_occupation_variance": between,
                    "within_occupation_variance": within,
                    "total_variance": between + within,
                    "icc": full_values["icc"],
                    "sampling_error_variance_removed": 0.0,
                    "interval_method": "centered stratified PSU bootstrap deviations; sqrt(2) rescaling",
                    "method_note": "Exact descriptive decomposition of observed finite-sample occupation means; includes occupation-mean estimation noise.",
                }
                for metric in ["between", "within", "icc"]:
                    lo, hi = centered_bootstrap_interval(
                        variance_boot[domain][metric], full_values[metric],
                        lower=0.0, upper=1.0 if metric == "icc" else None,
                    )
                    row[f"{metric}_bootstrap_ci95_low"] = lo
                    row[f"{metric}_bootstrap_ci95_high"] = hi
                variance_rows.append(row)

                sampling_noise = 0.0
                for group_code, group_weight in zip(codes_sorted, denom):
                    group_mask = codes_all == group_code
                    group_se = design_se(z[:, d], w, group_mask, design_key, n_strata)
                    if math.isfinite(group_se):
                        sampling_noise += group_weight * group_se**2
                sampling_noise /= np.sum(ww)
                corrected_between = max(between - sampling_noise, 0.0)
                corrected_total = corrected_between + within
                corrected_icc = corrected_between / corrected_total if corrected_total > 0 else math.nan
                corrected_boot_between = np.maximum(np.asarray(variance_boot[domain]["between"]) - sampling_noise, 0.0)
                corrected_boot_within = np.asarray(variance_boot[domain]["within"])
                corrected_boot_icc = corrected_boot_between / (corrected_boot_between + corrected_boot_within)
                corrected_row = {
                    "occupation_level": level,
                    "domain": domain,
                    "estimator": "survey_weighted_design_error_corrected_sensitivity",
                    "occupation_groups": g,
                    "respondent_n": len(ww),
                    "between_occupation_variance": corrected_between,
                    "within_occupation_variance": within,
                    "total_variance": corrected_total,
                    "icc": corrected_icc,
                    "sampling_error_variance_removed": sampling_noise,
                    "interval_method": "centered stratified PSU bootstrap deviations; sqrt(2) rescaling; point sampling-noise correction held fixed",
                    "method_note": "Method-of-moments sensitivity subtracting the population-share-weighted Taylor variance of occupation means; not used for feasibility tiers.",
                }
                for metric, vals, point in [
                    ("between", corrected_boot_between, corrected_between),
                    ("within", corrected_boot_within, within),
                    ("icc", corrected_boot_icc, corrected_icc),
                ]:
                    lo, hi = centered_bootstrap_interval(vals, point, lower=0.0, upper=1.0 if metric == "icc" else None)
                    corrected_row[f"{metric}_bootstrap_ci95_low"] = lo
                    corrected_row[f"{metric}_bootstrap_ci95_high"] = hi
                variance_rows.append(corrected_row)

                unweighted_means = np.bincount(full_ids, weights=zz[:, d], minlength=g) / np.bincount(full_ids, minlength=g)
                overall = float(np.mean(zz[:, d]))
                between_u = float(np.mean((unweighted_means[full_ids] - overall) ** 2))
                within_u = float(np.mean((zz[:, d] - unweighted_means[full_ids]) ** 2))
                variance_rows.append({
                    "occupation_level": level,
                    "domain": domain,
                    "estimator": "unweighted_sensitivity_exact_decomposition",
                    "occupation_groups": g,
                    "respondent_n": len(ww),
                    "between_occupation_variance": between_u,
                    "within_occupation_variance": within_u,
                    "total_variance": between_u + within_u,
                    "icc": between_u / (between_u + within_u),
                    "sampling_error_variance_removed": 0.0,
                    "interval_method": "not computed",
                    "method_note": "Unweighted exact descriptive sensitivity; includes occupation-mean estimation noise.",
                })
                anova = random_intercept_mom(zz[:, d], full_ids)
                anova_row = {
                    "occupation_level": level,
                    "domain": domain,
                    "estimator": "unweighted_random_intercept_anova_sensitivity",
                    "occupation_groups": g,
                    "respondent_n": len(ww),
                    "between_occupation_variance": anova["between"],
                    "within_occupation_variance": anova["within"],
                    "total_variance": anova["total"],
                    "icc": anova["icc"],
                    "effective_cell_n": anova["effective_cell_n"],
                    "sampling_error_variance_removed": between_u - anova["between"],
                    "interval_method": "centered stratified PSU bootstrap deviations; sqrt(2) rescaling",
                    "method_note": "One-way unequal-cell random-intercept ANOVA method-of-moments sensitivity; not used for feasibility tiers.",
                }
                for metric, vals, point in [
                    ("between", variance_boot[domain]["anova_between"], anova["between"]),
                    ("within", variance_boot[domain]["anova_within"], anova["within"]),
                    ("icc", variance_boot[domain]["anova_icc"], anova["icc"]),
                ]:
                    lo, hi = centered_bootstrap_interval(vals, point, lower=0.0, upper=1.0 if metric == "icc" else None)
                    anova_row[f"{metric}_bootstrap_ci95_low"] = lo
                    anova_row[f"{metric}_bootstrap_ci95_high"] = hi
                variance_rows.append(anova_row)
    uncertainty_rows.sort(key=lambda x: ({"narrow": 0, "intermediate": 1, "broad": 2}[x["occupation_level"]], x["occupation_code"]))
    write_csv(out / "occupation_centroid_uncertainty.csv", uncertainty_rows)
    write_csv(out / "occupation_personality_variance_decomposition.csv", variance_rows)

    split_rows: list[dict[str, Any]] = []
    split_map: dict[tuple[str, str], dict[str, Any]] = {}
    for level, code in sorted(full_stats, key=lambda x: ({"narrow": 0, "intermediate": 1, "broad": 2}[x[0]], x[1])):
        mask = full_stats[(level, code)]["mask"]
        local_z, local_w = z[mask], w[mask]
        metrics: dict[str, list[float]] = defaultdict(list)
        for split in range(SPLIT_REPS):
            order = np.random.default_rng(SEED + split).permutation(len(local_z))
            first, second = order[: len(order)//2], order[len(order)//2 :]
            c1 = np.asarray([weighted_mean(local_z[first, d], local_w[first]) for d in range(5)])
            c2 = np.asarray([weighted_mean(local_z[second, d], local_w[second]) for d in range(5)])
            metrics["euclidean_distance"].append(float(np.linalg.norm(c1-c2)))
            metrics["uncentered_cosine"].append(cosine(c1, c2))
            metrics["centered_cosine"].append(safe_corr(c1, c2))
            metrics["pearson_r"].append(safe_corr(c1, c2))
            metrics["kendall_tau_b"].append(kendall_tau_b(c1, c2))
        row = {
            "occupation_level": level,
            "occupation_code": code,
            "occupation_title": group_title(level, code, occ_meta),
            "analytic_n": len(local_z),
            "split_replicates": SPLIT_REPS,
            "split_seed_first": SEED,
            "split_seed_last": SEED + SPLIT_REPS - 1,
        }
        for metric, values in metrics.items():
            row.update(summarize_metric(values, metric))
        split_rows.append(row)
        split_map[(level, code)] = row
    write_csv(out / "occupation_centroid_split_half_stability.csv", split_rows)

    uncertainty_map = {(r["occupation_level"], r["occupation_code"]): r for r in uncertainty_rows}
    tier_rows: list[dict[str, Any]] = []
    tier_map: dict[tuple[str, str], str] = {}
    criteria_map: dict[tuple[str, str], list[str]] = {}
    for level in ["broad", "intermediate", "narrow"]:
        for key in sorted((k for k in full_stats if k[0] == level), key=lambda x: x[1]):
            _, code = key
            stat, boot, split = full_stats[key], uncertainty_map[key], split_map[key]
            ratio = boot["bootstrap_p95_displacement"] / stat["heterogeneity"] if stat["heterogeneity"] > 0 else math.inf
            strong_checks = {
                "N<100": stat["n"] >= 100,
                "valid_bootstrap<475": boot["bootstrap_valid_replicates"] >= 475,
                "bootstrap_mean>0.25": boot["bootstrap_mean_displacement"] <= 0.25,
                "bootstrap_p95>0.40": boot["bootstrap_p95_displacement"] <= 0.40,
                "split_median>0.45": split["euclidean_distance_median"] <= 0.45,
                "split_p95>0.80": split["euclidean_distance_p95"] <= 0.80,
                "uncertainty_heterogeneity_ratio>0.20": ratio <= 0.20,
            }
            moderate_checks = {
                "N<50": stat["n"] >= 50,
                "valid_bootstrap<450": boot["bootstrap_valid_replicates"] >= 450,
                "bootstrap_mean>0.40": boot["bootstrap_mean_displacement"] <= 0.40,
                "bootstrap_p95>0.60": boot["bootstrap_p95_displacement"] <= 0.60,
                "split_median>0.70": split["euclidean_distance_median"] <= 0.70,
                "split_p95>1.20": split["euclidean_distance_p95"] <= 1.20,
                "uncertainty_heterogeneity_ratio>0.30": ratio <= 0.30,
            }
            if all(strong_checks.values()):
                tier = "STRONG CENTROID"
                failed: list[str] = []
            elif all(moderate_checks.values()):
                tier = "MODERATE / EXPLORATORY"
                failed = [name for name, passed in strong_checks.items() if not passed]
            else:
                narrow_code = code if level == "narrow" else ""
                if level == "narrow":
                    broad = occ_meta[code]["broad_code"]
                elif level == "intermediate":
                    major_prefix = code[:2] if code else ""
                    broad = f"{major_prefix}-0000" if major_prefix else ""
                else:
                    broad = code
                if level != "broad" and tier_map.get(("broad", broad)) in {"STRONG CENTROID", "MODERATE / EXPLORATORY"}:
                    tier = "BROAD-FAMILY ONLY"
                else:
                    tier = "UNSTABLE / TOO SPARSE"
                failed = [name for name, passed in moderate_checks.items() if not passed]
            tier_map[key] = tier
            criteria_map[key] = failed
            if level == "narrow":
                broad_parent = occ_meta[code]["broad_code"]
                intermediate_parent = occ_meta[code]["intermediate_code"]
            elif level == "intermediate":
                broad_parent = f"{code[:2]}-0000"
                intermediate_parent = code
            else:
                broad_parent = code
                intermediate_parent = ""
            tier_rows.append({
                "occupation_level": level,
                "occupation_code": code,
                "occupation_title": group_title(level, code, occ_meta),
                "analytic_n": stat["n"],
                "weighted_population_estimate": stat["weighted_population_estimate"],
                "bootstrap_valid_replicates": boot["bootstrap_valid_replicates"],
                "bootstrap_mean_displacement": boot["bootstrap_mean_displacement"],
                "bootstrap_p95_displacement": boot["bootstrap_p95_displacement"],
                "split_half_median_euclidean_distance": split["euclidean_distance_median"],
                "split_half_p95_euclidean_distance": split["euclidean_distance_p95"],
                "within_cell_5d_rms_heterogeneity": stat["heterogeneity"],
                "bootstrap_p95_to_heterogeneity_ratio": ratio,
                "feasibility_tier": tier,
                "failed_applicable_thresholds": ";".join(failed),
                "intermediate_parent_code": intermediate_parent,
                "broad_parent_code": broad_parent,
                "criteria_source": "analysis_specification.md frozen at prereg commit",
            })
    tier_rows.sort(key=lambda x: ({"narrow": 0, "intermediate": 1, "broad": 2}[x["occupation_level"]], x["occupation_code"]))
    write_csv(out / "occupation_centroid_feasibility.csv", tier_rows)

    sample_rows: list[dict[str, Any]] = []
    level_index = {"narrow": 0, "intermediate": 1, "broad": 2}
    for level in ["narrow", "intermediate", "broad"]:
        for size in [10, 20, 30, 40, 50, 75, 100, 150, 200, 300, 500]:
            cell_summaries = []
            for key in sorted((k for k in full_stats if k[0] == level), key=lambda x: x[1]):
                code = key[1]
                stat = full_stats[key]
                if stat["n"] < max(2*size, size+20):
                    continue
                local_z, local_w = z[stat["mask"]], w[stat["mask"]]
                errors = []
                for repeat in range(SUBSAMPLE_REPS):
                    seed = SEED + 100000*level_index[level] + 1000*size + repeat
                    chosen = np.random.default_rng(seed).choice(stat["n"], size=size, replace=False)
                    sub = np.asarray([weighted_mean(local_z[chosen, d], local_w[chosen]) for d in range(5)])
                    errors.append(float(np.linalg.norm(sub - stat["centroid"])))
                row = {
                    "record_type": "occupation_cell",
                    "occupation_level": level,
                    "occupation_code": code,
                    "occupation_title": group_title(level, code, occ_meta),
                    "full_cell_n": stat["n"],
                    "subsample_n": size,
                    "subsample_replicates": SUBSAMPLE_REPS,
                    "eligible_occupation_cells": 1,
                    "centroid_error_mean": float(np.mean(errors)),
                    "centroid_error_median": float(np.median(errors)),
                    "centroid_error_p05": q(errors, 0.05),
                    "centroid_error_p95": q(errors, 0.95),
                    "reference": "full finite-sample cell centroid",
                }
                sample_rows.append(row)
                cell_summaries.append(row)
            if cell_summaries:
                sample_rows.append({
                    "record_type": "level_summary_equal_weight_per_occupation",
                    "occupation_level": level,
                    "occupation_code": "__LEVEL_SUMMARY__",
                    "occupation_title": f"{level.title()} level summary",
                    "full_cell_n": "",
                    "subsample_n": size,
                    "subsample_replicates": SUBSAMPLE_REPS,
                    "eligible_occupation_cells": len(cell_summaries),
                    "centroid_error_mean": float(np.mean([r["centroid_error_mean"] for r in cell_summaries])),
                    "centroid_error_median": float(np.median([r["centroid_error_median"] for r in cell_summaries])),
                    "centroid_error_p05": float(np.median([r["centroid_error_p05"] for r in cell_summaries])),
                    "centroid_error_p95": float(np.median([r["centroid_error_p95"] for r in cell_summaries])),
                    "reference": "equal-weight summary of cell-specific full-centroid errors",
                })
    sample_rows.sort(key=lambda x: (level_index[x["occupation_level"]], int(x["subsample_n"]), x["record_type"] != "occupation_cell", x["occupation_code"]))
    write_csv(out / "occupation_centroid_sample_size_curve.csv", sample_rows)

    shrinkage_rows: list[dict[str, Any]] = []
    for level in ["narrow", "intermediate", "broad"]:
        keys = sorted((k for k in full_stats if k[0] == level), key=lambda x: x[1])
        pop = np.asarray([full_stats[k]["weighted_population_estimate"] for k in keys])
        for domain in DOMAINS:
            means = np.asarray([full_stats[k]["domain_stats"][domain]["weighted_z_mean"] for k in keys])
            se2 = np.asarray([full_stats[k]["domain_stats"][domain]["design_se_z"] ** 2 for k in keys])
            between_observed = weighted_mean(means**2, pop)
            average_sampling = weighted_mean(se2, pop)
            tau2 = max(between_observed - average_sampling, 0.0)
            for k, mean, variance in zip(keys, means, se2):
                if tau2 > 0 and variance > 0:
                    reliability_weight = tau2 / (tau2 + variance)
                    posterior_se = math.sqrt(tau2 * variance / (tau2 + variance))
                elif tau2 > 0 and variance == 0:
                    reliability_weight, posterior_se = 1.0, 0.0
                else:
                    reliability_weight, posterior_se = 0.0, 0.0
                shrunken = reliability_weight * mean
                shrinkage_rows.append({
                    "occupation_level": level,
                    "occupation_code": k[1],
                    "occupation_title": group_title(level, k[1], occ_meta),
                    "domain": domain,
                    "analytic_n": full_stats[k]["n"],
                    "raw_weighted_z_mean": mean,
                    "design_se_z": math.sqrt(variance),
                    "estimated_between_cell_variance_tau2": tau2,
                    "posterior_reliability_weight_on_raw_mean": reliability_weight,
                    "shrunken_z_mean": shrunken,
                    "absolute_shrinkage": abs(shrunken-mean),
                    "posterior_se": posterior_se,
                    "analysis_role": "sensitivity only; does not alter N or feasibility tier",
                })
    write_csv(out / "occupation_centroid_shrinkage.csv", shrinkage_rows)

    tradeoff_rows: list[dict[str, Any]] = []
    for key in sorted((k for k in full_stats if k[0] == "narrow"), key=lambda x: x[1]):
        code = key[1]
        parents = {
            "narrow": key,
            "intermediate": ("intermediate", occ_meta[code]["intermediate_code"]) if occ_meta[code]["intermediate_code"] else None,
            "broad": ("broad", occ_meta[code]["broad_code"]) if occ_meta[code]["broad_code"] else None,
        }
        row: dict[str, Any] = {
            "narrow_occupation_code": code,
            "narrow_occupation_title": group_title("narrow", code, occ_meta),
            "intermediate_parent_code": occ_meta[code]["intermediate_code"],
            "broad_parent_code": occ_meta[code]["broad_code"],
        }
        narrow_n = full_stats[key]["n"]
        for level, parent in parents.items():
            if parent and parent in full_stats:
                stat, boot, split = full_stats[parent], uncertainty_map[parent], split_map[parent]
                row[f"{level}_n"] = stat["n"]
                row[f"{level}_sample_size_gain_vs_narrow"] = stat["n"] - narrow_n
                row[f"{level}_distinct_narrow_codes"] = next(r["distinct_narrow_occupation_codes"] for r in centroid_rows if r["occupation_level"] == level and r["occupation_code"] == parent[1])
                row[f"{level}_within_cell_5d_rms_heterogeneity"] = stat["heterogeneity"]
                row[f"{level}_bootstrap_p95_displacement"] = boot["bootstrap_p95_displacement"]
                row[f"{level}_split_median_distance"] = split["euclidean_distance_median"]
                row[f"{level}_feasibility_tier"] = tier_map[parent]
            else:
                for suffix in ["n", "sample_size_gain_vs_narrow", "distinct_narrow_codes", "within_cell_5d_rms_heterogeneity", "bootstrap_p95_displacement", "split_median_distance", "feasibility_tier"]:
                    row[f"{level}_{suffix}"] = ""
        row["semantic_cost_note"] = "Parent groups follow official SOC hierarchy and may contain substantively different narrow occupations."
        tradeoff_rows.append(row)
    write_csv(out / "occupation_granularity_tradeoff.csv", tradeoff_rows)

    r6_mask = goldberg_complete & r6_occupation
    r6_ac = goldberg_ac[r6_mask]
    r6_mean = np.mean(r6_ac, axis=0)
    r6_sd = np.std(r6_ac, axis=0, ddof=0)
    r6_z = (r6_ac - r6_mean) / r6_sd
    replication_rows: list[dict[str, Any]] = []
    for level in ["narrow", "intermediate", "broad"]:
        r6_groups = r6_level_all[level][r6_mask]
        r12_groups = level_codes[level]
        common = sorted((set(r6_groups) & set(r12_groups)) - {""})
        population_cells = []
        for code in common:
            m6, m12 = r6_groups == code, r12_groups == code
            if np.sum(m6) < 20 or np.sum(m12) < 20:
                continue
            cell = {
                "record_type": "cell",
                "analysis_type": "population_level_occupational_recurrence",
                "occupation_level": level,
                "occupation_code": code,
                "occupation_title": group_title(level, code, occ_meta),
                "round6_n": int(np.sum(m6)),
                "round12_n": int(np.sum(m12)),
                "stable_respondent_n": "",
                "round6_agreeableness_z_mean_unweighted": float(np.mean(r6_z[m6, 0])),
                "round12_agreeableness_z_mean_unweighted": float(np.mean(z[m12, DOMAINS.index("agreeableness")])),
                "round6_conscientiousness_z_mean_unweighted": float(np.mean(r6_z[m6, 1])),
                "round12_conscientiousness_z_mean_unweighted": float(np.mean(z[m12, DOMAINS.index("conscientiousness")])),
                "round6_agreeableness_z_mean_round12_weighted": "",
                "round12_agreeableness_z_mean_round12_weighted": "",
                "round6_conscientiousness_z_mean_round12_weighted": "",
                "round12_conscientiousness_z_mean_round12_weighted": "",
                "across_cell_pearson_r": "",
                "across_cell_spearman_r": "",
                "limitation": "Round-6 sample limited to younger cohort subset; different respondents and occupations may contribute at each wave; unweighted because Round-6 weight is absent from extract.",
            }
            replication_rows.append(cell)
            population_cells.append(cell)
        for domain in ["agreeableness", "conscientiousness"]:
            x = [c[f"round6_{domain}_z_mean_unweighted"] for c in population_cells]
            y = [c[f"round12_{domain}_z_mean_unweighted"] for c in population_cells]
            pearson, spearman = corr_pair(x, y)
            replication_rows.append({
                "record_type": "summary",
                "analysis_type": "population_level_occupational_recurrence",
                "occupation_level": level,
                "occupation_code": "__SUMMARY__",
                "occupation_title": f"{DOMAIN_LABELS[domain]} across-cell recurrence",
                "round6_n": "",
                "round12_n": "",
                "stable_respondent_n": "",
                "respondents_across_eligible_cells": int(sum(c["round6_n"] for c in population_cells)),
                "across_cell_pearson_r": pearson,
                "across_cell_spearman_r": spearman,
                "cells_in_correlation": len(population_cells),
                "domain": domain,
                "limitation": "Population-level recurrence; not individual personality change.",
            })

        both = goldberg_complete & r6_occupation & primary_mask
        stable6_groups = r6_level_all[level][both]
        stable12_groups = r12_level_all[level][both]
        both_idx = np.flatnonzero(both)
        r6_standardized_all = np.full((len(data["R0536300"]), 2), np.nan)
        r6_standardized_all[r6_mask] = r6_z
        stable_cells = []
        for code in sorted((set(stable6_groups) & set(stable12_groups)) - {""}):
            keep = (stable6_groups == code) & (stable12_groups == code)
            if np.sum(keep) < 20:
                continue
            rows_idx = both_idx[keep]
            local_w = weight_all[rows_idx]
            cell = {
                "record_type": "cell",
                "analysis_type": "stable_occupation_respondents",
                "occupation_level": level,
                "occupation_code": code,
                "occupation_title": group_title(level, code, occ_meta),
                "round6_n": int(np.sum(keep)),
                "round12_n": int(np.sum(keep)),
                "stable_respondent_n": int(np.sum(keep)),
                "round6_agreeableness_z_mean_unweighted": float(np.mean(r6_standardized_all[rows_idx, 0])),
                "round12_agreeableness_z_mean_unweighted": float(np.mean(((tipi_raw[rows_idx]-global_mean)/global_sd)[:, DOMAINS.index("agreeableness")])),
                "round6_conscientiousness_z_mean_unweighted": float(np.mean(r6_standardized_all[rows_idx, 1])),
                "round12_conscientiousness_z_mean_unweighted": float(np.mean(((tipi_raw[rows_idx]-global_mean)/global_sd)[:, DOMAINS.index("conscientiousness")])),
                "round6_agreeableness_z_mean_round12_weighted": weighted_mean(r6_standardized_all[rows_idx, 0], local_w),
                "round12_agreeableness_z_mean_round12_weighted": weighted_mean(((tipi_raw[rows_idx]-global_mean)/global_sd)[:, DOMAINS.index("agreeableness")], local_w),
                "round6_conscientiousness_z_mean_round12_weighted": weighted_mean(r6_standardized_all[rows_idx, 1], local_w),
                "round12_conscientiousness_z_mean_round12_weighted": weighted_mean(((tipi_raw[rows_idx]-global_mean)/global_sd)[:, DOMAINS.index("conscientiousness")], local_w),
                "across_cell_pearson_r": "",
                "across_cell_spearman_r": "",
                "limitation": "Same respondents and same occupational code/family, but differences can reflect measurement, age, period, or selection as well as personality.",
            }
            replication_rows.append(cell)
            stable_cells.append(cell)
        for domain in ["agreeableness", "conscientiousness"]:
            x = [c[f"round6_{domain}_z_mean_round12_weighted"] for c in stable_cells]
            y = [c[f"round12_{domain}_z_mean_round12_weighted"] for c in stable_cells]
            pearson, spearman = corr_pair(x, y)
            replication_rows.append({
                "record_type": "summary",
                "analysis_type": "stable_occupation_respondents",
                "occupation_level": level,
                "occupation_code": "__SUMMARY__",
                "occupation_title": f"{DOMAIN_LABELS[domain]} stable-respondent across-cell recurrence",
                "round6_n": int(sum(c["stable_respondent_n"] for c in stable_cells)),
                "round12_n": int(sum(c["stable_respondent_n"] for c in stable_cells)),
                "stable_respondent_n": int(sum(c["stable_respondent_n"] for c in stable_cells)),
                "respondents_across_eligible_cells": int(sum(c["stable_respondent_n"] for c in stable_cells)),
                "across_cell_pearson_r": pearson,
                "across_cell_spearman_r": spearman,
                "cells_in_correlation": len(stable_cells),
                "domain": domain,
                "limitation": "Round-12-weighted cell means; not a causal estimate or pure personality change.",
            })
    write_csv(out / "occupation_round6_round12_replication.csv", replication_rows)

    discrim_rows: list[dict[str, Any]] = []
    for level in ["narrow", "intermediate", "broad"]:
        groups = level_codes[level]
        counts = Counter(groups[groups != ""])
        eligible = sorted(code for code, count in counts.items() if count >= 50)
        if len(eligible) < 5:
            discrim_rows.append({
                "occupation_level": level,
                "eligible_class_minimum_n": 50,
                "eligible_classes": len(eligible),
                "respondent_n": int(np.sum(np.isin(groups, eligible))),
                "status": "not_run_fewer_than_five_classes",
            })
            continue
        keep = np.isin(groups, eligible)
        X, y = z[keep], groups[keep]
        scores = []
        for repeat in range(10):
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED+repeat)
            for train, test in cv.split(X, y):
                model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000, class_weight="balanced")
                model.fit(X[train], y[train])
                scores.append(float(balanced_accuracy_score(y[test], model.predict(X[test]))))
        discrim_rows.append({
            "occupation_level": level,
            "eligible_class_minimum_n": 50,
            "eligible_classes": len(eligible),
            "eligible_class_codes": ";".join(eligible),
            "respondent_n": len(y),
            "minimum_class_n": min(counts[c] for c in eligible),
            "maximum_class_n": max(counts[c] for c in eligible),
            "cv_repeats": 10,
            "folds_per_repeat": 5,
            "balanced_accuracy_mean": float(np.mean(scores)),
            "balanced_accuracy_sd": float(np.std(scores, ddof=1)),
            "balanced_accuracy_p05": q(scores, 0.05),
            "balanced_accuracy_p95": q(scores, 0.95),
            "uniform_multiclass_baseline": 1/len(eligible),
            "above_baseline_absolute": float(np.mean(scores)) - 1/len(eligible),
            "status": "completed_descriptive_control",
            "model": "fixed L2 multinomial logistic regression C=1; class-balanced fitting; no tuning",
        })
    write_csv(out / "occupation_personality_discriminability.csv", discrim_rows)

    persona_rows = load_dict_rows(args.persona_crosswalk.resolve())
    candidate_rows: list[dict[str, Any]] = []
    for role in persona_rows:
        if role.get("existing_include_in_analysis", "").lower() != "true":
            continue
        for narrow_code in filter(None, role.get("nlsy97_census_2002_codes", "").split(";")):
            narrow_code = narrow_code.zfill(4)
            if narrow_code not in occ_meta or narrow_code == "9920":
                continue
            hierarchy = [
                ("narrow", narrow_code),
                ("intermediate", occ_meta[narrow_code]["intermediate_code"]),
                ("broad", occ_meta[narrow_code]["broad_code"]),
            ]
            selected = next((k for k in hierarchy if k[1] and tier_map.get(k) in {"STRONG CENTROID", "MODERATE / EXPLORATORY"}), None)
            if not selected:
                continue
            source_stat = full_stats.get(("narrow", narrow_code))
            candidate_rows.append({
                "source_narrow_occupation_code": narrow_code,
                "source_narrow_occupation_title": occ_meta[narrow_code]["occupation_title"],
                "source_narrow_analytic_n": source_stat["n"] if source_stat else "<10_or_zero",
                "source_narrow_feasibility_tier": tier_map.get(("narrow", narrow_code), "SUPPRESSED_OR_EMPTY"),
                "future_comparison_level": selected[0],
                "future_comparison_occupation_code": selected[1],
                "future_comparison_occupation_title": group_title(selected[0], selected[1], occ_meta),
                "future_comparison_analytic_n": full_stats[selected]["n"],
                "human_stability_tier": tier_map[selected],
                "matching_model_role_name": role["persona"],
                "existing_match_quality": role.get("mapping_quality", ""),
                "existing_translation_quality": role.get("translation_quality", ""),
                "semantic_cost_flag": selected[0] != "narrow",
                "semantic_cost_note": "Official parent occupation contains other narrow occupations; future work must justify construct correspondence." if selected[0] != "narrow" else "No aggregation beyond the existing narrow mapping.",
                "boundary": "Candidate list only; no model data loaded and no human respondent labeled with a role name.",
            })
    candidate_rows.sort(key=lambda x: (x["future_comparison_level"], x["future_comparison_occupation_code"], x["matching_model_role_name"]))
    write_csv(out / "future_model_role_comparison_candidates.csv", candidate_rows)

    tier_counts: dict[str, dict[str, int]] = {}
    for level in ["narrow", "intermediate", "broad"]:
        tier_counts[level] = dict(Counter(r["feasibility_tier"] for r in tier_rows if r["occupation_level"] == level))
    cell_threshold_counts = {}
    suppression = {}
    for level in ["narrow", "intermediate", "broad"]:
        groups = level_codes[level]
        counts = Counter(groups[groups != ""])
        cell_threshold_counts[level] = {f"n_ge_{threshold}": sum(v >= threshold for v in counts.values()) for threshold in [10, 20, 50, 100]}
        suppression[level] = {
            "cells_n_lt_10": sum(v < 10 for v in counts.values()),
            "respondents_in_cells_n_lt_10": sum(v for v in counts.values() if v < 10),
        }

    cohort_summary = {
        "starting_sha": STARTING_SHA,
        "preregistered_specification_sha": PREREG_SHA,
        "original_cohort_n": len(data["R0536300"]),
        "round12_tipi_all_ten_complete_n": int(np.sum(tipi_complete)),
        "aa1_round12_tipi_plus_official_code_including_nonoccupation_9920_n": int(np.sum(tipi_complete & r12_official_occ)),
        "round12_tipi_plus_occupation_excluding_9920_n": int(np.sum(tipi_complete & r12_occupation)),
        "primary_analytic_n": len(primary_index),
        "primary_weighted_population_estimate": float(np.sum(w)),
        "round6_goldberg_all_eight_complete_n": int(np.sum(goldberg_complete)),
        "round6_goldberg_plus_occupation_excluding_9920_n": int(np.sum(r6_mask)),
        "round6_universe_limitation": "Items were administered only to respondents age 14 or younger at end of 1996.",
        "design": design_audit,
        "global_weighted_standardization": {
            domain: {"raw_mean": global_mean[i], "raw_population_sd": global_sd[i]} for i, domain in enumerate(DOMAINS)
        },
        "tipi_two_item_reliability": reliability,
        "tipi_item_availability": {
            variable: {
                "valid_1_to_7_n_full_extract": int(np.sum((data[variable] >= 1) & (data[variable] <= 7))),
                "valid_1_to_7_n_primary_analytic_cohort": int(np.sum((data[variable][primary_mask] >= 1) & (data[variable][primary_mask] <= 7))),
            }
            for variable in TIPI
        },
        "secondary_personality_inventory": {
            "round12_industriousness": "4 raw items (T3162600-T3162603); inventoried but not combined with TIPI",
            "round12_traditionalism": "4 raw items (T3162700-T3162703); inventoried but not combined with TIPI",
            "round16_17_grit": "8 Round-16 items plus a Round-17 repeat for Round-16 nonrespondents; inventoried but not combined with TIPI",
            "source": "research/outputs/human_trait_dataset_feasibility/nlsy97/nlsy97_personality_item_manifest.csv",
        },
        "cell_threshold_counts": cell_threshold_counts,
        "feasibility_tier_counts": tier_counts,
        "suppression": suppression,
        "generated_at": args.generated_at,
    }
    write_json(out / "analysis_cohort_summary.json", cohort_summary)

    aa1_dir = args.occupation_codes.resolve().parent
    aa1_input_names = [
        "nlsy97_personality_item_manifest.csv",
        "nlsy97_occupation_variable_manifest.csv",
        "nlsy97_2002_census_occupation_codes.csv",
        "nlsy97_personality_occupation_cell_counts.csv",
        "nlsy97_personality_occupation_cell_summary.json",
        "nlsy97_persona_occupation_crosswalk.csv",
        "nlsy97_wave_overlap_summary.csv",
        "nlsy97_source_manifest.json",
        "nlsy97_variable_manifest.csv",
    ]
    missing_aa1 = [name for name in aa1_input_names if not (aa1_dir / name).is_file()]
    if missing_aa1:
        raise FileNotFoundError(f"Missing canonical AA-1 artifacts: {missing_aa1}")
    source_manifest = {
        "study": "AA-5 NLSY97 occupational personality centroid stability",
        "scientific_scope": "human-only; future role names used only in post-tier candidate list",
        "starting_sha": STARTING_SHA,
        "preregistered_specification_sha": PREREG_SHA,
        "respondent_source": {
            "description": "Official NLS Investigator NLSY97 public-use extract; respondent rows remain gitignored",
            "logical_repo_path": "data_external/human_validation/nlsy97/public_use_extract/human_trait_dataset_feasibility_final.csv",
            "sha256": sha256(args.raw_csv.resolve()),
            "bytes": args.raw_csv.resolve().stat().st_size,
            "committed": False,
        },
        "official_codebook": {"sha256": sha256(args.codebook.resolve()), "bytes": args.codebook.resolve().stat().st_size, "committed": False},
        "committed_inputs": [
            {
                "path": f"research/outputs/human_trait_dataset_feasibility/nlsy97/{name}",
                "sha256": sha256(aa1_dir / name),
                "bytes": (aa1_dir / name).stat().st_size,
            }
            for name in aa1_input_names
        ],
        "official_sources": {
            "tipi_scoring": "https://gosling.psy.utexas.edu/scales-weve-developed/ten-item-personality-measure-tipi/",
            "tipi_primary_manuscript": "https://gosling.psy.utexas.edu/wp-content/uploads/2014/09/JRP-03-tipi.pdf",
            "nlsy97_weights_and_design": "https://www.bls.gov/nls/nlsy97/using-and-understanding-data/",
            "soc_2000_user_guide": "https://www.bls.gov/soc/2000/socguide.htm",
            "soc_2000_structure": "https://www.bls.gov/soc/socstructure_2000.pdf",
            "census_2002_occupation_codes": "https://www.census.gov/topics/employment/industry-occupation/guidance/code-lists.html",
        },
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
            "scikit_learn": __import__("sklearn").__version__,
        },
        "randomness": {"master_seed": SEED, "bootstrap_replicates": BOOTSTRAP_REPS, "split_replicates": SPLIT_REPS, "subsample_replicates": SUBSAMPLE_REPS},
        "prohibited_inputs_loaded": [],
        "model_geometry_used": False,
        "human_to_model_projection_performed": False,
        "gpu_used": False,
        "runpod_used": False,
        "model_inference_used": False,
        "activation_extraction_used": False,
        "external_model_api_used": False,
        "generated_at": args.generated_at,
    }
    write_json(out / "source_manifest.json", source_manifest)

    variance_descriptive = [r for r in variance_rows if r["estimator"] == "survey_weighted_descriptive_exact_decomposition"]
    variance_corrected = [r for r in variance_rows if r["estimator"] == "survey_weighted_design_error_corrected_sensitivity"]
    sample_summary = [r for r in sample_rows if r["record_type"].startswith("level_summary")]
    discrim_done = [r for r in discrim_rows if r.get("status") == "completed_descriptive_control"]
    recurrence_summary = [r for r in replication_rows if r["record_type"] == "summary"]
    stable_candidates = len(candidate_rows)
    candidate_roles = len({r["matching_model_role_name"] for r in candidate_rows})
    candidate_human_cells = len({(r["future_comparison_level"], r["future_comparison_occupation_code"]) for r in candidate_rows})
    direct_candidate_rows = sum(r["future_comparison_level"] == "narrow" for r in candidate_rows)
    aggregated_candidate_rows = stable_candidates - direct_candidate_rows
    narrow_stable = sum(tier_counts["narrow"].get(x, 0) for x in ["STRONG CENTROID", "MODERATE / EXPLORATORY"])
    broad_stable = sum(tier_counts["broad"].get(x, 0) for x in ["STRONG CENTROID", "MODERATE / EXPLORATORY"])

    def variance_sentence(level: str, rows: list[dict[str, Any]]) -> str:
        return ", ".join(
            f"{DOMAIN_LABELS[r['domain']]} {r['icc']:.3f}"
            for r in rows if r["occupation_level"] == level
        )

    requested_roles = [
        ("Secretary / administrative assistant", "5700", "secretary"),
        ("Accountant / auditor", "0800", "accountant"),
        ("Caregiver", "4610", "caregiver"),
        ("Counselor", "2000", "counselor"),
        ("Artisan proxy", "8960", "artisan"),
        ("Teacher / instructor", "2340", "teacher"),
        ("Lawyer", "2100", "lawyer"),
        ("Programmer", "1010", "programmer"),
        ("Engineer", "1530", "engineer"),
        ("Therapist", "3240", "therapist"),
        ("Psychologist", "1820", "psychologist"),
        ("Journalist", "2810", "journalist"),
        ("Actor", "2700", "actor"),
    ]
    requested_lines = []
    for label, code, role_name in requested_roles:
        source = full_stats.get(("narrow", code))
        source_text = f"N={source['n']}; {tier_map[('narrow', code)]}" if source else "N<10 or zero; suppressed/empty"
        candidate = next((r for r in candidate_rows if r["source_narrow_occupation_code"] == code and r["matching_model_role_name"] == role_name), None)
        if candidate and candidate["future_comparison_level"] == "narrow":
            parent_text = "Not needed"
            readout = "Direct narrow comparison is feasible at the stated tier."
        elif candidate:
            parent_text = f"{candidate['future_comparison_level']} {candidate['future_comparison_occupation_code']} ({candidate['future_comparison_occupation_title']}), N={candidate['future_comparison_analytic_n']}; {candidate['human_stability_tier']}"
            readout = "Precision improves only by changing the construct; semantic-cost flag applies."
        else:
            parent_text = "No stable reportable official parent"
            readout = "Not a current candidate."
        requested_lines.append(f"| {label} | {code} | {source_text} | {parent_text} | {readout} |")

    report_lines = [
        "# NLSY97 occupational personality centroid stability",
        "",
        "## Can NLSY97 produce stable human occupational personality centroids suitable for later model comparison?",
        "",
        f"Qualified yes. Among the 151 reportable narrow four-digit Census cells, {narrow_stable} pass the frozen empirical criteria ({tier_counts['narrow'].get('STRONG CENTROID', 0)} strong and {tier_counts['narrow'].get('MODERATE / EXPLORATORY', 0)} moderate). Among 22 reportable SOC major families, {broad_stable} pass ({tier_counts['broad'].get('STRONG CENTROID', 0)} strong and {tier_counts['broad'].get('MODERATE / EXPLORATORY', 0)} moderate). Aggregation makes means precise, but broad occupations explain only a small fraction of personality variance and mix substantively different jobs. The defensible conclusion is feasibility for selected aggregate human comparisons—not evidence that occupations are personality types.",
        "",
        "## Primary cohort and measurement",
        "",
        f"The official extract contains 8,984 respondents. {int(np.sum(tipi_complete)):,} have complete Round-12 TIPI data, and {int(np.sum(tipi_complete & r12_official_occ)):,} reproduce the AA-1 complete-TIPI plus official-code count. Excluding Census code 9920 because it represents no recent occupation, and requiring a positive Round-12 weight plus valid VSTRAT/VPSU, leaves {len(primary_index):,} respondents.",
        "",
        "TIPI domains use the [official Gosling scoring key](https://gosling.psy.utexas.edu/scales-weve-developed/ten-item-personality-measure-tipi/): Extraversion items 1 and reversed 6; Agreeableness reversed 2 and 7; Conscientiousness 3 and reversed 8; Emotional Stability reversed 4 and 9; Openness 5 and reversed 10. Each pair is averaged, then all five domains are standardized globally using Round-12 survey weights. The instrument is deliberately short; its two-item reliabilities and item availability are reported in `analysis_cohort_summary.json`. These are low-resolution domain summaries, not high-resolution personality profiles.",
        "",
        "Round-12 industriousness and traditionalism (four items each) and Round-16/17 grit (eight items) are inventoried but were not combined into an omnibus score. Round-6 Goldberg Agreeableness and Conscientiousness are kept as the separate replication layer. The official codebook—not the convenience labels in the original AA-1 item manifest—determines all eight bipolar directions; the corrected manifest is included in this branch.",
        "",
        "## Between-occupation signal and within-occupation heterogeneity",
        "",
    ]
    for level in ["narrow", "broad"]:
        report_lines.append(f"- {level.title()} observed finite-sample ICCs: {variance_sentence(level, variance_descriptive)}.")
        report_lines.append(f"- {level.title()} sampling-error-corrected sensitivity ICCs: {variance_sentence(level, variance_corrected)}.")
    report_lines += [
        "",
        "The observed narrow decomposition assigns 8.2%-12.0% of variance to the 400 sampled occupation means, but this is inflated because many means are estimated from sparse cells. Subtracting the population-share-weighted Taylor variance of those means reduces the narrow signal to 3.8%-7.8%. At the broad level, the corrected signal is only 0.8%-3.2%. Thus within-occupation heterogeneity dominates (roughly 92%-99%, depending on level, domain, and estimator). The separate unweighted random-intercept ANOVA sensitivity is also saved. None of these descriptive associations identifies selection, socialization, or a causal occupational effect.",
        "",
        "## Sample-size stability curve",
        "",
    ]
    for level in ["narrow", "intermediate", "broad"]:
        parts = []
        for n in [20, 50, 100]:
            row = next((r for r in sample_summary if r["occupation_level"] == level and r["subsample_n"] == n), None)
            if row:
                parts.append(f"N={n}: median expected error {row['centroid_error_median']:.3f} (median cell p95 {row['centroid_error_p95']:.3f}; {row['eligible_occupation_cells']} reference cells)")
        if parts:
            report_lines.append(f"- {level.title()}: " + "; ".join(parts) + ".")
    report_lines += [
        "",
        "The curve compares repeated subsample centroids with each full finite-sample cell centroid. N=20 leaves expected 5D error near 0.43-0.46 SD units and is not a confirmatory threshold. N=50 is a defensible lower bound only for moderate/exploratory cells that also pass vector-stability checks. N=100 is a sensible strong-centroid screen, not a guarantee. The narrow N=100 summary has only one eligible reference cell under the frozen `full N >= max(2n,n+20)` rule, so broad/intermediate curves provide the stronger empirical calibration at that size.",
        "",
        "## Frozen feasibility tiers",
        "",
    ]
    for level in ["narrow", "intermediate", "broad"]:
        counts = tier_counts[level]
        report_lines.append(f"- {level.title()}: " + ", ".join(f"{tier} = {counts.get(tier, 0)}" for tier in ["STRONG CENTROID", "MODERATE / EXPLORATORY", "BROAD-FAMILY ONLY", "UNSTABLE / TOO SPARSE"]) + ".")
    report_lines += [
        "",
        "Tier thresholds were committed before the trait outcomes were inspected. They jointly require N, design-respecting bootstrap precision, split-half distance, and uncertainty relative to within-cell heterogeneity. Shrinkage is reported only as a sensitivity analysis and cannot upgrade a tier.",
        "",
        "## Narrow versus broad occupation tradeoff",
        "",
        "Official SOC minor and major groups sharply increase sample size and generally reduce centroid uncertainty. They also increase the number of distinct four-digit Census occupations inside a cell and therefore the semantic distance from a specific role. `occupation_granularity_tradeoff.csv` exposes N gain, child-code count, heterogeneity, bootstrap error, split-half error, and tier at all three levels. A stable parent is a possible aggregate comparison only; it does not rescue the meaning of an unstable narrow job.",
        "",
        "| Requested comparison | Narrow code | Narrow result | Most specific stable official parent | Feasibility interpretation |",
        "|---|---:|---|---|---|",
        *requested_lines,
        "",
        "## Round-6/Round-12 recurrence",
        "",
        "The population-cell recurrence is mixed but more consistent for Conscientiousness:",
        "",
    ]
    for level in ["narrow", "intermediate", "broad"]:
        a = next(r for r in recurrence_summary if r["analysis_type"] == "population_level_occupational_recurrence" and r["occupation_level"] == level and r["domain"] == "agreeableness")
        c = next(r for r in recurrence_summary if r["analysis_type"] == "population_level_occupational_recurrence" and r["occupation_level"] == level and r["domain"] == "conscientiousness")
        report_lines.append(f"- {level.title()} population cells (k={a['cells_in_correlation']}): Agreeableness Pearson r={a['across_cell_pearson_r']:.3f}; Conscientiousness r={c['across_cell_pearson_r']:.3f}.")
    report_lines += ["", "Among respondents retained in the same official group at both waves:", ""]
    for level in ["narrow", "intermediate", "broad"]:
        a = next(r for r in recurrence_summary if r["analysis_type"] == "stable_occupation_respondents" and r["occupation_level"] == level and r["domain"] == "agreeableness")
        c = next(r for r in recurrence_summary if r["analysis_type"] == "stable_occupation_respondents" and r["occupation_level"] == level and r["domain"] == "conscientiousness")
        if a["cells_in_correlation"] < 3:
            report_lines.append(f"- {level.title()}: not estimable (fewer than three cells with at least 20 stable respondents).")
        else:
            report_lines.append(f"- {level.title()} stable cells (k={a['cells_in_correlation']}; {a['stable_respondent_n']} respondents across those cells): Agreeableness r={a['across_cell_pearson_r']:.3f}; Conscientiousness r={c['across_cell_pearson_r']:.3f}.")
    report_lines += [
        "",
        "The Round-6 items were administered only to respondents age 14 or younger at the end of 1996, and the canonical extract has no Round-6 survey weight. With few stable cells, especially at the intermediate level, correlations are volatile. The evidence supports modest Conscientiousness recurrence and no robust general recurrence claim for Agreeableness. These are occupational-pattern checks, not estimates of personality change.",
        "",
        "## Occupation discriminability",
        "",
    ]
    for row in discrim_done:
        report_lines.append(f"- {row['occupation_level'].title()}: balanced accuracy {row['balanced_accuracy_mean']:.3f} versus {row['uniform_multiclass_baseline']:.3f} baseline across {row['eligible_classes']} classes.")
    report_lines += [
        "",
        "Big Five profiles contain little occupation information: accuracy is only 0.009-0.034 above the balanced multiclass baseline. This is scientifically consistent with the small corrected ICCs and extensive distributional overlap, and should not be read as a useful individual occupation classifier.",
        "",
        "## Stable future role candidates",
        "",
        f"The post-tier crosswalk produces {stable_candidates} mapping rows covering {candidate_roles} model-role names and {candidate_human_cells} distinct stable human cells. Only {direct_candidate_rows} rows retain the mapped narrow occupation; {aggregated_candidate_rows} require an intermediate or broad parent and carry a semantic-cost flag. Secretary/administrative assistant is strong at the narrow level; accountant/auditor, caregiver, and the `production workers, all other` artisan proxy are moderate. Counselor, programmer, engineer, therapist, psychologist, journalist, teacher/instructor, and actor have only more aggregated stable options. Lawyer has no stable reportable parent in this sample. This is a candidate list for later preregistration, not a model comparison.",
        "",
        "## Expected-question audit",
        "",
        "1. Between-occupation variation exists, but the design-error-corrected signal is modest: 3.8%-7.8% at narrow and 0.8%-3.2% at broad levels.",
        "2. Within-occupation variance is the overwhelming majority in every domain.",
        "3. Five-dimensional centroids become reasonably stable around N=50 for exploratory use and around N=100 for a stronger screen, conditional on empirical stability.",
        "4. The earlier N>=20/50/100 cutoffs were sensible as sparse/exploratory/strong screens, but N=20 is too noisy and N alone is insufficient.",
        f"5. {narrow_stable} reportable narrow occupations are stable enough: {tier_counts['narrow'].get('STRONG CENTROID', 0)} strong and {tier_counts['narrow'].get('MODERATE / EXPLORATORY', 0)} moderate.",
        f"6. {broad_stable} broad families are stable enough: {tier_counts['broad'].get('STRONG CENTROID', 0)} strong and {tier_counts['broad'].get('MODERATE / EXPLORATORY', 0)} moderate.",
        "7. `future_model_role_comparison_candidates.csv` gives every current role correspondence and flags aggregation cost.",
        "8. Accountant, caregiver, secretary/administrative assistant, and the artisan proxy are plausible narrow future comparisons; counselor is plausible only as an explicitly broader community/social-service comparison.",
        "9. Lawyer, programmer, engineer, therapist, psychologist, journalist, and actor are too sparse at the narrow level; only some have stable broader substitutes.",
        "10. Broadening improves precision, often sharply, but can impose unacceptable semantic cost when the target is a specific job.",
        "11. Round-6/Round-12 recurrence is mixed; Conscientiousness recurs more consistently than Agreeableness, with major measurement and cell-count limitations.",
        "12. Occupation is adequate for selected preregistered aggregate comparisons, but the low ICCs and near-chance classification rule out treating it as a strong human personality grouping variable.",
        "",
        "## Observed",
        "",
        "Human occupational TIPI means, dispersion, design uncertainty, resampling stability, sample-size error, variance decomposition, cross-wave recurrence, and descriptive discriminability.",
        "",
        "## Interpretation",
        "",
        "Some official occupation groups are sufficiently reproducible to serve as human comparison distributions in a later, separately preregistered study. Stability means the group mean is estimated consistently; it does not mean the group is internally homogeneous, highly distinctive, or psychologically equivalent to a model role.",
        "",
        "## Unknowns and future hypothesis",
        "",
        "Whether any human occupational distribution corresponds to an LLM occupational-role prototype remains untested. A later study would need an independent construct bridge, frozen comparison metrics, multiplicity control, and explicit decisions about the semantic cost of occupation aggregation.",
        "",
        "No model geometry was used. No human-to-model projection was performed. No respondent-level NLSY97 data were committed. No GPU, RunPod, model inference, activation extraction, or external model API was used.",
    ]
    (out / "nlsy97_occupation_personality_stability_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
